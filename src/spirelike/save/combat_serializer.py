from __future__ import annotations

import random
from typing import Any

from spirelike.models.entities import CombatState, EnemyInstance, PowerInstance, RunState
from spirelike.save.serializer import card_instance_from_dict, card_instance_to_dict

COMBAT_SNAPSHOT_SCHEMA_VERSION = 1


def random_state_to_json(value: Any) -> Any:
    if isinstance(value, tuple):
        return [random_state_to_json(item) for item in value]
    if isinstance(value, list):
        return [random_state_to_json(item) for item in value]
    return value


def random_state_from_json(value: Any) -> Any:
    if isinstance(value, list):
        return tuple(random_state_from_json(item) for item in value)
    return value


def enemy_to_dict(enemy: EnemyInstance) -> dict[str, Any]:
    return {
        "instance_id": enemy.instance_id,
        "enemy_id": enemy.enemy_id,
        "name": enemy.name,
        "hp": enemy.hp,
        "max_hp": enemy.max_hp,
        "block": enemy.block,
        "statuses": dict(enemy.statuses),
        "next_move": enemy.next_move,
        "last_move": enemy.last_move,
        "move_index": enemy.move_index,
    }


def enemy_from_dict(data: dict[str, Any]) -> EnemyInstance:
    enemy = EnemyInstance(
        enemy_id=str(data["enemy_id"]),
        name=str(data.get("name", data["enemy_id"])),
        hp=int(data.get("hp", 1)),
        max_hp=int(data.get("max_hp", data.get("hp", 1))),
        block=int(data.get("block", 0)),
        statuses={str(k): int(v) for k, v in (data.get("statuses", {}) or {}).items()},
        next_move=data.get("next_move"),
        last_move=data.get("last_move"),
        move_index=int(data.get("move_index", 0)),
    )
    enemy.instance_id = str(data.get("instance_id", enemy.instance_id))
    return enemy


def power_to_dict(power: PowerInstance) -> dict[str, Any]:
    return {
        "instance_id": power.instance_id,
        "power_id": power.power_id,
        "source_card_id": power.source_card_id,
        "owner": power.owner,
        "stacks": power.stacks,
        "upgraded": power.upgraded,
        "state": dict(power.state),
    }


def power_from_dict(data: dict[str, Any]) -> PowerInstance:
    power = PowerInstance(
        power_id=str(data["power_id"]),
        source_card_id=data.get("source_card_id"),
        owner=str(data.get("owner", "player")),
        stacks=int(data.get("stacks", 1)),
        upgraded=bool(data.get("upgraded", False)),
        state=dict(data.get("state", {}) or {}),
    )
    power.instance_id = str(data.get("instance_id", power.instance_id))
    return power


def combat_state_to_dict(state: CombatState) -> dict[str, Any]:
    return {
        "enemies": [enemy_to_dict(enemy) for enemy in state.enemies],
        "draw_pile": [card_instance_to_dict(card) for card in state.draw_pile],
        "hand": [card_instance_to_dict(card) for card in state.hand],
        "discard_pile": [card_instance_to_dict(card) for card in state.discard_pile],
        "exhaust_pile": [card_instance_to_dict(card) for card in state.exhaust_pile],
        "limbo": [card_instance_to_dict(card) for card in state.limbo],
        "powers": [power_to_dict(power) for power in state.powers],
        "energy": state.energy,
        "turn_number": state.turn_number,
        "cards_played_this_turn": state.cards_played_this_turn,
        "combat_end_fired": state.combat_end_fired,
        "outcome": state.outcome,
        "log": list(state.log),
    }


def combat_state_from_dict(data: dict[str, Any], run_state: RunState) -> CombatState:
    return CombatState(
        run_state=run_state,
        enemies=[enemy_from_dict(enemy) for enemy in data.get("enemies", []) or []],
        draw_pile=[card_instance_from_dict(card) for card in data.get("draw_pile", []) or []],
        hand=[card_instance_from_dict(card) for card in data.get("hand", []) or []],
        discard_pile=[card_instance_from_dict(card) for card in data.get("discard_pile", []) or []],
        exhaust_pile=[card_instance_from_dict(card) for card in data.get("exhaust_pile", []) or []],
        limbo=[card_instance_from_dict(card) for card in data.get("limbo", []) or []],
        powers=[power_from_dict(power) for power in data.get("powers", []) or []],
        energy=int(data.get("energy", run_state.player.base_energy)),
        turn_number=int(data.get("turn_number", 0)),
        cards_played_this_turn=int(data.get("cards_played_this_turn", 0)),
        combat_end_fired=bool(data.get("combat_end_fired", False)),
        outcome=data.get("outcome"),
        log=list(data.get("log", []) or []),
    )


def combat_snapshot_to_dict(combat) -> dict[str, Any]:
    return {
        "schema_version": COMBAT_SNAPSHOT_SCHEMA_VERSION,
        "enemy_ids": [enemy.enemy_id for enemy in combat.state.enemies],
        "rng_state": random_state_to_json(combat.rng.getstate()),
        "state": combat_state_to_dict(combat.state),
    }


def combat_snapshot_from_dict(data: dict[str, Any], run_state: RunState) -> tuple[CombatState, random.Random]:
    if int(data.get("schema_version", 0)) != COMBAT_SNAPSHOT_SCHEMA_VERSION:
        raise ValueError(f"Unsupported combat snapshot schema: {data.get('schema_version')}")
    state = combat_state_from_dict(data["state"], run_state)
    rng = random.Random()
    rng_state = data.get("rng_state")
    if rng_state is not None:
        rng.setstate(random_state_from_json(rng_state))
    return state, rng
