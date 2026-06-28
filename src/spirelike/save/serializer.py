from __future__ import annotations

from typing import Any

from spirelike.models.entities import (
    AncientBlessingInstance,
    CardInstance,
    CardModifierInstance,
    MapNode,
    MapState,
    PlayerState,
    PotionInstance,
    RelicInstance,
    RunState,
)
from spirelike.systems.card_reward_rarity_system import (
    reward_choice_from_dict,
    reward_choice_to_dict,
)
from spirelike.systems.reward_system import RewardBundle


def card_modifier_to_dict(modifier: CardModifierInstance) -> dict[str, Any]:
    return {
        "instance_id": modifier.instance_id,
        "modifier_id": modifier.modifier_id,
        "modifier_type": modifier.modifier_type,
        "duration": modifier.duration,
        "stacks": modifier.stacks,
        "source": modifier.source,
        "state": dict(modifier.state),
    }


def card_modifier_from_dict(data: dict[str, Any] | str) -> CardModifierInstance:
    if isinstance(data, str):
        return CardModifierInstance(
            modifier_id=data,
            modifier_type="enchantment",
            duration="run",
        )
    modifier = CardModifierInstance(
        modifier_id=str(data["modifier_id"]),
        modifier_type=str(data.get("modifier_type", "enchantment")),
        duration=str(data.get("duration", "run")),
        stacks=int(data.get("stacks", 1)),
        source=data.get("source"),
        state=dict(data.get("state", {}) or {}),
    )
    modifier.instance_id = str(data.get("instance_id", modifier.instance_id))
    return modifier


def card_instance_to_dict(card: CardInstance) -> dict[str, Any]:
    return {
        "instance_id": card.instance_id,
        "card_id": card.card_id,
        "upgraded": card.upgraded,
        "temporary": card.temporary,
        "state": dict(card.state),
        "modifiers": [card_modifier_to_dict(modifier) for modifier in card.modifiers],
    }


def card_instance_from_dict(data: dict[str, Any]) -> CardInstance:
    card = CardInstance(
        card_id=str(data["card_id"]),
        upgraded=bool(data.get("upgraded", False)),
        temporary=bool(data.get("temporary", False)),
        state=dict(data.get("state", {}) or {}),
        modifiers=[card_modifier_from_dict(mod) for mod in data.get("modifiers", []) or []],
    )
    card.instance_id = str(data.get("instance_id", card.instance_id))
    return card


def relic_to_dict(relic: RelicInstance) -> dict[str, Any]:
    return {"relic_id": relic.relic_id, "state": dict(relic.state)}


def relic_from_dict(data: dict[str, Any]) -> RelicInstance:
    return RelicInstance(relic_id=str(data["relic_id"]), state=dict(data.get("state", {}) or {}))


def potion_to_dict(potion: PotionInstance | None) -> dict[str, Any] | None:
    if potion is None:
        return None
    return {"potion_id": potion.potion_id, "instance_id": potion.instance_id}


def potion_from_dict(data: dict[str, Any] | None) -> PotionInstance | None:
    if data is None:
        return None
    potion = PotionInstance(potion_id=str(data["potion_id"]))
    potion.instance_id = str(data.get("instance_id", potion.instance_id))
    return potion


def ancient_blessing_to_dict(blessing: AncientBlessingInstance) -> dict[str, Any]:
    return {
        "ancient_id": blessing.ancient_id,
        "choice_id": blessing.choice_id,
        "state": dict(blessing.state),
    }


def ancient_blessing_from_dict(data: dict[str, Any]) -> AncientBlessingInstance:
    return AncientBlessingInstance(
        ancient_id=str(data["ancient_id"]),
        choice_id=str(data["choice_id"]),
        state=dict(data.get("state", {}) or {}),
    )


def player_to_dict(player: PlayerState) -> dict[str, Any]:
    return {
        "character_id": player.character_id,
        "hp": player.hp,
        "max_hp": player.max_hp,
        "gold": player.gold,
        "base_energy": player.base_energy,
        "block": player.block,
        "statuses": dict(player.statuses),
        "potion_slots": player.potion_slots,
        "deck": [card_instance_to_dict(card) for card in player.deck],
        "relics": [relic_to_dict(relic) for relic in player.relics],
        "potions": [potion_to_dict(potion) for potion in player.potions],
    }


def player_from_dict(data: dict[str, Any], character_id: str | None = None) -> PlayerState:
    potion_slots = int(data.get("potion_slots", 3))
    return PlayerState(
        character_id=str(data.get("character_id", character_id or "wanderer")),
        hp=int(data.get("hp", data.get("max_hp", 1))),
        max_hp=int(data.get("max_hp", 1)),
        gold=int(data.get("gold", 0)),
        base_energy=int(data.get("base_energy", 3)),
        block=int(data.get("block", 0)),
        statuses={str(k): int(v) for k, v in (data.get("statuses", {}) or {}).items()},
        potion_slots=potion_slots,
        deck=[card_instance_from_dict(card) for card in data.get("deck", []) or []],
        relics=[relic_from_dict(relic) for relic in data.get("relics", []) or []],
        potions=[potion_from_dict(potion) for potion in data.get("potions", []) or []],
    )


def map_node_to_dict(node: MapNode) -> dict[str, Any]:
    return {
        "id": node.id,
        "layer": node.layer,
        "x": node.x,
        "y": node.y,
        "node_type": node.node_type,
        "connected_to": list(node.connected_to),
        "visited": node.visited,
        "available": node.available,
        "encounter_id": node.encounter_id,
        "event_id": node.event_id,
    }


def map_node_from_dict(data: dict[str, Any]) -> MapNode:
    return MapNode(
        id=str(data["id"]),
        layer=int(data["layer"]),
        x=float(data["x"]),
        y=float(data["y"]),
        node_type=str(data["node_type"]),
        connected_to=list(data.get("connected_to", []) or []),
        visited=bool(data.get("visited", False)),
        available=bool(data.get("available", False)),
        encounter_id=data.get("encounter_id"),
        event_id=data.get("event_id"),
    )


def map_state_to_dict(map_state: MapState) -> dict[str, Any]:
    return {
        "act_id": map_state.act_id,
        "layers": map_state.layers,
        "start_node_ids": list(map_state.start_node_ids),
        "current_node_id": map_state.current_node_id,
        "nodes": [map_node_to_dict(node) for node in map_state.nodes.values()],
    }


def map_state_from_dict(data: dict[str, Any]) -> MapState:
    nodes = {node_data["id"]: map_node_from_dict(node_data) for node_data in data.get("nodes", []) or []}
    return MapState(
        act_id=str(data["act_id"]),
        nodes=nodes,
        layers=int(data["layers"]),
        start_node_ids=list(data.get("start_node_ids", []) or []),
        current_node_id=data.get("current_node_id"),
    )


def run_state_to_dict(run_state: RunState) -> dict[str, Any]:
    return {
        "seed": run_state.seed,
        "character_id": run_state.character_id,
        "act": run_state.act,
        "floor": run_state.floor,
        "flags": dict(run_state.flags),
        "messages": list(run_state.messages),
        "player": player_to_dict(run_state.player),
        "ancient_blessings": [
            ancient_blessing_to_dict(blessing) for blessing in run_state.ancient_blessings
        ],
        "map_state": map_state_to_dict(run_state.map_state),
    }


def run_state_from_dict(data: dict[str, Any]) -> RunState:
    character_id = str(data["character_id"])
    run_state = RunState(
        seed=int(data["seed"]),
        character_id=character_id,
        act=int(data.get("act", 1)),
        floor=int(data.get("floor", 0)),
        player=player_from_dict(data["player"], character_id=character_id),
        map_state=map_state_from_dict(data["map_state"]),
        flags=dict(data.get("flags", {}) or {}),
        messages=list(data.get("messages", []) or []),
        ancient_blessings=[
            ancient_blessing_from_dict(blessing)
            for blessing in data.get("ancient_blessings", []) or []
        ],
    )
    run_state.pending_selection = None
    run_state.pending_effects = []
    return run_state


def reward_bundle_to_dict(reward: RewardBundle | None) -> dict[str, Any] | None:
    if reward is None:
        return None
    return {
        "title": reward.title,
        "gold": reward.gold,
        "card_choices": [reward_choice_to_dict(choice) for choice in reward.card_choices],
        "relic_id": reward.relic_id,
        "potion_id": reward.potion_id,
        "message": reward.message,
        "base_applied": bool(getattr(reward, "base_applied", False)),
        "potion_drop": dict(getattr(reward, "potion_drop", {}) or {}),
    }


def reward_bundle_from_dict(data: dict[str, Any] | None) -> RewardBundle | None:
    if data is None:
        return None
    return RewardBundle(
        title=str(data.get("title", "報酬")),
        gold=int(data.get("gold", 0)),
        card_choices=[reward_choice_from_dict(choice) for choice in data.get("card_choices", []) or []],
        relic_id=data.get("relic_id"),
        potion_id=data.get("potion_id"),
        message=str(data.get("message", "")),
        base_applied=bool(data.get("base_applied", False)),
        potion_drop=dict(data.get("potion_drop", {}) or {}),
    )
