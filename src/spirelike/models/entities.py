from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional
import uuid

from spirelike.models.selection import CardSelectionRequest


def new_id() -> str:
    return uuid.uuid4().hex


@dataclass
class CardModifierInstance:
    modifier_id: str
    modifier_type: str
    duration: str
    stacks: int = 1
    source: str | None = None
    state: dict[str, Any] = field(default_factory=dict)
    instance_id: str = field(default_factory=new_id)

    def clone(self) -> "CardModifierInstance":
        return CardModifierInstance(
            modifier_id=self.modifier_id,
            modifier_type=self.modifier_type,
            duration=self.duration,
            stacks=self.stacks,
            source=self.source,
            state=dict(self.state),
        )


@dataclass
class CardInstance:
    card_id: str
    upgraded: bool = False
    modifiers: list[CardModifierInstance] = field(default_factory=list)
    temporary: bool = False
    # 戦闘中の一時的なコスト変更、キーワード付与、Afflictionなどの保持先。
    state: dict[str, Any] = field(default_factory=dict)
    instance_id: str = field(default_factory=new_id)

    def clone_for_combat(self) -> "CardInstance":
        return CardInstance(
            card_id=self.card_id,
            upgraded=self.upgraded,
            modifiers=[
                modifier.clone()
                if isinstance(modifier, CardModifierInstance)
                else CardModifierInstance(
                    modifier_id=str(modifier),
                    modifier_type="enchantment",
                    duration="run",
                )
                for modifier in self.modifiers
            ],
            temporary=self.temporary,
            state=dict(self.state),
        )


@dataclass
class RelicInstance:
    relic_id: str
    state: dict[str, Any] = field(default_factory=dict)


@dataclass
class PotionInstance:
    potion_id: str
    instance_id: str = field(default_factory=new_id)


@dataclass
class AncientBlessingInstance:
    ancient_id: str
    choice_id: str
    state: dict[str, Any] = field(default_factory=dict)


@dataclass
class PowerInstance:
    power_id: str
    source_card_id: str | None = None
    owner: str = "player"
    stacks: int = 1
    upgraded: bool = False
    state: dict[str, Any] = field(default_factory=dict)
    instance_id: str = field(default_factory=new_id)


@dataclass
class PlayerState:
    character_id: str
    hp: int
    max_hp: int
    gold: int
    base_energy: int
    deck: list[CardInstance]
    relics: list[RelicInstance]
    statuses: dict[str, int] = field(default_factory=dict)
    block: int = 0
    potion_slots: int = 3
    potions: list[PotionInstance | None] = field(default_factory=list)

    def __post_init__(self) -> None:
        # セーブデータや古い生成処理から来ても、必ずスロット数とリスト長を揃える。
        if not self.potions:
            self.potions = [None for _ in range(self.potion_slots)]
        elif len(self.potions) < self.potion_slots:
            self.potions.extend([None for _ in range(self.potion_slots - len(self.potions))])
        elif len(self.potions) > self.potion_slots:
            self.potions = self.potions[: self.potion_slots]

    def is_alive(self) -> bool:
        return self.hp > 0

    def heal(self, amount: int) -> int:
        before = self.hp
        self.hp = min(self.max_hp, self.hp + max(0, amount))
        return self.hp - before

    def lose_hp(self, amount: int) -> int:
        actual = max(0, amount)
        self.hp = max(0, self.hp - actual)
        return actual

    def add_card(self, card_id: str, upgraded: bool = False) -> CardInstance:
        card = CardInstance(card_id=card_id, upgraded=upgraded)
        self.deck.append(card)
        return card

    def has_relic(self, relic_id: str) -> bool:
        return any(relic.relic_id == relic_id for relic in self.relics)

    def first_empty_potion_slot(self) -> int | None:
        for index, potion in enumerate(self.potions):
            if potion is None:
                return index
        return None


@dataclass
class EnemyInstance:
    enemy_id: str
    name: str
    hp: int
    max_hp: int
    block: int = 0
    statuses: dict[str, int] = field(default_factory=dict)
    next_move: Optional[str] = None
    last_move: Optional[str] = None
    move_index: int = 0
    instance_id: str = field(default_factory=new_id)

    def is_alive(self) -> bool:
        return self.hp > 0


@dataclass
class MapNode:
    id: str
    layer: int
    x: float
    y: float
    node_type: str
    connected_to: list[str] = field(default_factory=list)
    visited: bool = False
    available: bool = False
    encounter_id: Optional[str] = None
    event_id: Optional[str] = None


@dataclass
class MapState:
    act_id: str
    nodes: dict[str, MapNode]
    layers: int
    start_node_ids: list[str]
    current_node_id: Optional[str] = None

    def available_nodes(self) -> list[MapNode]:
        return [node for node in self.nodes.values() if node.available and not node.visited]

    def mark_visited(self, node_id: str) -> None:
        node = self.nodes[node_id]
        node.visited = True
        node.available = False
        self.current_node_id = node_id
        for next_id in node.connected_to:
            if next_id in self.nodes and not self.nodes[next_id].visited:
                self.nodes[next_id].available = True

    def boss_visited(self) -> bool:
        return any(node.node_type == "boss" and node.visited for node in self.nodes.values())


@dataclass
class RunState:
    seed: int
    character_id: str
    act: int
    floor: int
    player: PlayerState
    map_state: MapState
    flags: dict[str, Any] = field(default_factory=dict)
    messages: list[str] = field(default_factory=list)
    ancient_blessings: list[AncientBlessingInstance] = field(default_factory=list)
    pending_selection: CardSelectionRequest | None = None
    pending_effects: list[dict[str, Any]] = field(default_factory=list)

    def add_message(self, text: str) -> None:
        self.messages.append(text)
        self.messages = self.messages[-8:]


@dataclass
class CombatState:
    run_state: RunState
    enemies: list[EnemyInstance]
    draw_pile: list[CardInstance]
    hand: list[CardInstance]
    discard_pile: list[CardInstance]
    exhaust_pile: list[CardInstance]
    limbo: list[CardInstance]
    powers: list[PowerInstance]
    energy: int
    pending_selection: CardSelectionRequest | None = None
    turn_number: int = 0
    cards_played_this_turn: int = 0
    combat_end_fired: bool = False
    outcome: Optional[str] = None
    log: list[str] = field(default_factory=list)

    def alive_enemies(self) -> list[EnemyInstance]:
        return [enemy for enemy in self.enemies if enemy.is_alive()]

    def add_log(self, text: str) -> None:
        self.log.append(text)
        self.log = self.log[-10:]
