from __future__ import annotations

import random
from typing import Any

from spirelike.content.loader import ContentRegistry
from spirelike.models.entities import MapNode, MapState
from spirelike.systems.difficulty_system import DifficultySystem


class MapGenerator:
    def __init__(self, registry: ContentRegistry) -> None:
        self.registry = registry
        self.difficulty = DifficultySystem(registry)

    def generate(self, act_id: str, rng: random.Random, run_config: dict[str, Any] | None = None) -> MapState:
        act_def = self.registry.map(act_id)
        layers = int(act_def.get("layers", 15))
        layout = act_def.get("layout", {}) or {}
        min_nodes = int(layout.get("min_nodes_per_layer", 2))
        max_nodes = int(layout.get("max_nodes_per_layer", 5))
        start_nodes = int(layout.get("start_nodes", 3))
        boss_nodes = int(layout.get("boss_nodes", 1))

        layer_nodes: list[list[MapNode]] = []
        nodes: dict[str, MapNode] = {}
        for layer in range(1, layers + 1):
            if layer == 1:
                count = start_nodes
            elif layer == layers:
                count = boss_nodes
            else:
                count = rng.randint(min_nodes, max_nodes)

            current_layer: list[MapNode] = []
            for i in range(count):
                node_type = self._choose_node_type(act_def, layer, rng, run_config=run_config)
                node_id = f"L{layer:02d}N{i:02d}"
                x = (i + 1) / (count + 1)
                y = (layer - 1) / max(1, layers - 1)
                node = MapNode(
                    id=node_id,
                    layer=layer,
                    x=x,
                    y=y,
                    node_type=node_type,
                )
                current_layer.append(node)
                nodes[node_id] = node
            layer_nodes.append(current_layer)

        self._connect_layers(layer_nodes, rng, act_def)
        start_node_ids = [node.id for node in layer_nodes[0]]
        for node_id in start_node_ids:
            nodes[node_id].available = True
        return MapState(act_id=act_id, nodes=nodes, layers=layers, start_node_ids=start_node_ids)

    def _choose_node_type(
        self,
        act_def: dict[str, Any],
        layer: int,
        rng: random.Random,
        run_config: dict[str, Any] | None = None,
    ) -> str:
        fixed = act_def.get("fixed_layers", {}) or {}
        fixed_layer = fixed.get(layer) or fixed.get(str(layer))
        if fixed_layer:
            allowed = fixed_layer.get("allowed") or {}
            if allowed:
                return self._weighted_choice(self._apply_difficulty_weights(allowed, run_config), rng)

        for depth_def in (act_def.get("weights_by_depth", {}) or {}).values():
            if layer in depth_def.get("layers", []):
                weights = depth_def.get("weights", {})
                return self._weighted_choice(self._apply_difficulty_weights(weights, run_config), rng)
        return "monster"

    def _apply_difficulty_weights(
        self,
        weights: dict[str, int | float],
        run_config: dict[str, Any] | None,
    ) -> dict[str, float]:
        adjusted: dict[str, float] = {}
        for node_type, weight in weights.items():
            multiplier = self.difficulty.map_weight_multiplier_for_config(run_config, str(node_type))
            adjusted[str(node_type)] = float(weight) * multiplier
        return adjusted

    def _weighted_choice(self, weights: dict[str, int | float], rng: random.Random) -> str:
        positive = [(key, float(value)) for key, value in weights.items() if float(value) > 0]
        if not positive:
            return "monster"
        total = sum(value for _, value in positive)
        roll = rng.uniform(0, total)
        upto = 0.0
        for key, weight in positive:
            upto += weight
            if roll <= upto:
                return key
        return positive[-1][0]

    def _connect_layers(
        self, layer_nodes: list[list[MapNode]], rng: random.Random, act_def: dict[str, Any]
    ) -> None:
        edges = act_def.get("edges", {}) or {}
        max_out = int(edges.get("max_outgoing_per_node", 3))
        for index in range(len(layer_nodes) - 1):
            current = layer_nodes[index]
            nxt = layer_nodes[index + 1]
            incoming: dict[str, int] = {node.id: 0 for node in nxt}
            for node in current:
                max_choices = min(max_out, len(nxt))
                count = rng.randint(1, max_choices)
                candidates = sorted(nxt, key=lambda n: abs(n.x - node.x))[: max(2, max_choices)]
                selected = rng.sample(candidates, k=min(count, len(candidates)))
                node.connected_to = sorted({n.id for n in selected})
                for selected_node in selected:
                    incoming[selected_node.id] += 1

            for next_node in nxt:
                if incoming[next_node.id] == 0:
                    previous = min(current, key=lambda n: abs(n.x - next_node.x))
                    if next_node.id not in previous.connected_to:
                        previous.connected_to.append(next_node.id)
                        previous.connected_to.sort()

    def choose_encounter(self, act_id: str, node_type: str, rng: random.Random) -> list[str]:
        act_def = self.registry.map(act_id)
        pools = act_def.get("encounter_pools", {}) or {}
        pool = pools.get(node_type) or pools.get("monster") or []
        if not pool:
            return []
        selected = rng.choice(pool)
        if isinstance(selected, list):
            return list(selected)
        return [str(selected)]
