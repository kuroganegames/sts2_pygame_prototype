from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, Optional
import yaml


@dataclass
class ContentItem:
    id: str
    data: dict[str, Any]
    yaml_path: Path
    image_path: Optional[Path] = None


@dataclass
class ContentRegistry:
    root: Path
    cards: Dict[str, ContentItem] = field(default_factory=dict)
    relics: Dict[str, ContentItem] = field(default_factory=dict)
    characters: Dict[str, ContentItem] = field(default_factory=dict)
    enemies: Dict[str, ContentItem] = field(default_factory=dict)
    statuses: Dict[str, ContentItem] = field(default_factory=dict)
    maps: Dict[str, ContentItem] = field(default_factory=dict)
    events: Dict[str, ContentItem] = field(default_factory=dict)
    potions: Dict[str, ContentItem] = field(default_factory=dict)
    ancients: Dict[str, ContentItem] = field(default_factory=dict)
    card_modifiers: Dict[str, ContentItem] = field(default_factory=dict)
    timeline_fragments: Dict[str, ContentItem] = field(default_factory=dict)
    run_modifiers: Dict[str, ContentItem] = field(default_factory=dict)
    difficulty_levels: Dict[str, ContentItem] = field(default_factory=dict)
    unlock_rules: Dict[str, ContentItem] = field(default_factory=dict)
    achievements: Dict[str, ContentItem] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    def card(self, card_id: str) -> dict[str, Any]:
        return self.cards[card_id].data

    def relic(self, relic_id: str) -> dict[str, Any]:
        return self.relics[relic_id].data

    def character(self, character_id: str) -> dict[str, Any]:
        return self.characters[character_id].data

    def enemy(self, enemy_id: str) -> dict[str, Any]:
        return self.enemies[enemy_id].data

    def status(self, status_id: str) -> dict[str, Any]:
        return self.statuses[status_id].data

    def map(self, map_id: str) -> dict[str, Any]:
        return self.maps[map_id].data

    def event(self, event_id: str) -> dict[str, Any]:
        return self.events[event_id].data

    def potion(self, potion_id: str) -> dict[str, Any]:
        return self.potions[potion_id].data

    def ancient(self, ancient_id: str) -> dict[str, Any]:
        return self.ancients[ancient_id].data

    def card_modifier(self, modifier_id: str) -> dict[str, Any]:
        return self.card_modifiers[modifier_id].data

    def timeline_fragment(self, fragment_id: str) -> dict[str, Any]:
        return self.timeline_fragments[fragment_id].data

    def run_modifier(self, modifier_id: str) -> dict[str, Any]:
        return self.run_modifiers[modifier_id].data

    def difficulty_level(self, difficulty_id: str) -> dict[str, Any]:
        return self.difficulty_levels[difficulty_id].data

    def unlock_rule(self, unlock_id: str) -> dict[str, Any]:
        return self.unlock_rules[unlock_id].data

    def achievement(self, achievement_id: str) -> dict[str, Any]:
        return self.achievements[achievement_id].data

    def image_for(self, kind: str, item_id: str) -> Optional[Path]:
        table = getattr(self, kind)
        return table[item_id].image_path

    def card_display_name(self, card_id: str, upgraded: bool = False) -> str:
        card = self.card(card_id)
        if upgraded and card.get("upgrade", {}).get("name"):
            return str(card["upgrade"]["name"])
        return str(card.get("name", card_id))

    def card_description(self, card_id: str, upgraded: bool = False) -> str:
        card = self.card(card_id)
        if upgraded and card.get("upgrade", {}).get("description"):
            return str(card["upgrade"]["description"])
        return str(card.get("description", ""))

    def card_cost(self, card_id: str, upgraded: bool = False):
        card = self.card(card_id)
        if upgraded and "cost" in card.get("upgrade", {}):
            return card["upgrade"]["cost"]
        return card.get("cost", 0)

    def card_effects(self, card_id: str, upgraded: bool = False) -> list[dict[str, Any]]:
        card = self.card(card_id)
        if upgraded and "effects" in card.get("upgrade", {}):
            return card["upgrade"]["effects"] or []
        return card.get("effects", []) or []


class ContentLoader:
    IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")
    MODIFIER_TYPES = {"enchantment", "affliction"}
    MODIFIER_DURATIONS = {"combat", "run", "permanent"}
    MODIFIER_NUMERIC_EVENTS = {"calculate_card_cost", "calculate_card_damage", "calculate_card_block"}
    RUN_MODIFIER_TYPES = {"bonus", "challenge", "chaos", "utility"}
    RUN_MODIFIER_EFFECT_TYPES = {
        "gain_gold",
        "add_potion_slot",
        "add_card_to_deck",
        "gain_relic",
        "enemy_hp_multiplier",
        "map_weight_multiplier",
    }
    DIFFICULTY_EFFECT_TYPES = {
        "enemy_hp_multiplier",
        "enemy_damage_multiplier",
        "player_max_hp_delta",
    }
    UNLOCK_TARGET_TYPES = {
        "character",
        "card",
        "relic",
        "potion",
        "run_modifier",
        "ancient",
        "card_modifier",
    }
    CONDITION_TYPES = {
        "runs_started_at_least",
        "runs_completed_at_least",
        "victories_at_least",
        "character_victories_at_least",
        "character_difficulty_victory_at_least",
        "character_difficulty_unlocked_at_least",
        "any_character_difficulty_unlocked_at_least",
        "enemy_seen",
        "enemy_defeated",
        "enemy_defeated_count_at_least",
        "card_seen",
        "card_acquired_count_at_least",
        "card_played_count_at_least",
        "relic_acquired",
        "potion_used",
        "potion_used_count_at_least",
        "modifier_applied",
        "modifier_applied_count_at_least",
        "ancient_choice",
        "timeline_unlocked",
        "achievement_unlocked",
        "unlocked_count_at_least",
        "timeline_count_at_least",
        "compendium_seen_count_at_least",
    }
    TIMELINE_CONDITION_TYPES = CONDITION_TYPES

    def __init__(self, root: Path) -> None:
        self.root = root
        self.registry = ContentRegistry(root=root)

    def load(self) -> ContentRegistry:
        self._load_collection("characters", self.registry.characters, require_image=True)
        self._load_collection("cards", self.registry.cards, require_image=True, recursive=True)
        self._load_collection("enemies", self.registry.enemies, require_image=True, recursive=True)
        self._load_collection("relics", self.registry.relics, require_image=True, recursive=True)
        self._load_collection("statuses", self.registry.statuses, require_image=False)
        self._load_collection("maps", self.registry.maps, require_image=False)
        self._load_collection("events", self.registry.events, require_image=True, recursive=True)
        self._load_collection("potions", self.registry.potions, require_image=True, recursive=True)
        self._load_collection("ancients", self.registry.ancients, require_image=True, recursive=True)
        self._load_collection("card_modifiers", self.registry.card_modifiers, require_image=True, recursive=True)
        self._load_collection("timeline", self.registry.timeline_fragments, require_image=False, recursive=True)
        self._load_collection("run_modifiers", self.registry.run_modifiers, require_image=False, recursive=True)
        self._load_collection("difficulty_levels", self.registry.difficulty_levels, require_image=False, recursive=True)
        self._load_collection("unlocks", self.registry.unlock_rules, require_image=False, recursive=True)
        self._load_collection("achievements", self.registry.achievements, require_image=False, recursive=True)
        self._validate_references()
        return self.registry

    def _load_collection(
        self,
        folder_name: str,
        target: Dict[str, ContentItem],
        *,
        require_image: bool,
        recursive: bool = False,
    ) -> None:
        folder = self.root / folder_name
        if not folder.exists():
            self.registry.warnings.append(f"Missing content folder: {folder}")
            return

        pattern = "**/*.yaml" if recursive else "*.yaml"
        for path in sorted(folder.glob(pattern)):
            data = self._read_yaml(path)
            item_id = str(data.get("id", "")).strip()
            if not item_id:
                self.registry.warnings.append(f"Missing id in {path}")
                continue
            if item_id != path.stem:
                self.registry.warnings.append(
                    f"ID mismatch: {path} has id={item_id!r}, filename={path.stem!r}"
                )
            if item_id in target:
                self.registry.warnings.append(f"Duplicate id {item_id!r}: {path}")
                continue
            image_path = self._find_image(path, data)
            if require_image and image_path is None:
                self.registry.warnings.append(f"Missing image for {item_id}: {path}")
            target[item_id] = ContentItem(
                id=item_id, data=data, yaml_path=path, image_path=image_path
            )

    def _read_yaml(self, path: Path) -> dict[str, Any]:
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        if not isinstance(data, dict):
            raise ValueError(f"YAML root must be a mapping: {path}")
        return data

    def _find_image(self, yaml_path: Path, data: dict[str, Any]) -> Optional[Path]:
        image_name = data.get("image")
        candidates = []
        if image_name:
            candidates.append(yaml_path.parent / str(image_name))
        for ext in self.IMAGE_EXTENSIONS:
            candidates.append(yaml_path.with_suffix(ext))
        for candidate in candidates:
            if candidate.exists():
                return candidate
        return None

    def _validate_references(self) -> None:
        for char_id, item in self.registry.characters.items():
            for card_id in item.data.get("starting_deck", []) or []:
                if card_id not in self.registry.cards:
                    self.registry.warnings.append(
                        f"Character {char_id} references missing card: {card_id}"
                    )
            for relic_id in item.data.get("starting_relics", []) or []:
                if relic_id not in self.registry.relics:
                    self.registry.warnings.append(
                        f"Character {char_id} references missing relic: {relic_id}"
                    )

        for card_id, item in self.registry.cards.items():
            self._validate_effects(item.data.get("effects", []), f"card {card_id}")
            self._validate_effects(
                item.data.get("upgrade", {}).get("effects", []), f"card {card_id}+"
            )

        for enemy_id, item in self.registry.enemies.items():
            for move_id, move in (item.data.get("moves", {}) or {}).items():
                self._validate_effects(move.get("effects", []), f"enemy {enemy_id}.{move_id}")

        for potion_id, item in self.registry.potions.items():
            self._validate_effects(item.data.get("effects", []), f"potion {potion_id}")

        for ancient_id, item in self.registry.ancients.items():
            choices = item.data.get("choices", []) or []
            if not choices:
                self.registry.warnings.append(f"Ancient {ancient_id} has no choices")
            for choice in choices:
                choice_id = choice.get("id", "<missing>")
                self._validate_effects(choice.get("effects", []), f"ancient {ancient_id}.{choice_id}")
                for trigger in choice.get("triggers", []) or []:
                    self._validate_effects(
                        trigger.get("effects", []),
                        f"ancient {ancient_id}.{choice_id}.{trigger.get('event', '<event>')}",
                    )

        for modifier_id, item in self.registry.card_modifiers.items():
            self._validate_card_modifier(modifier_id, item.data)

        for fragment_id, item in self.registry.timeline_fragments.items():
            self._validate_timeline_fragment(fragment_id, item.data)

        for modifier_id, item in self.registry.run_modifiers.items():
            self._validate_run_modifier(modifier_id, item.data)

        self._validate_difficulty_levels()
        self._validate_unlock_rules()
        self._validate_achievements()

    def _validate_card_modifier(self, modifier_id: str, data: dict[str, Any]) -> None:
        modifier_type = data.get("type")
        if modifier_type not in self.MODIFIER_TYPES:
            self.registry.warnings.append(f"Card modifier {modifier_id} has invalid type: {modifier_type}")
        duration = data.get("duration", "run")
        if duration not in self.MODIFIER_DURATIONS:
            self.registry.warnings.append(f"Card modifier {modifier_id} has invalid duration: {duration}")
        for rule in data.get("modifiers", []) or []:
            event = rule.get("event")
            if event not in self.MODIFIER_NUMERIC_EVENTS:
                self.registry.warnings.append(f"Card modifier {modifier_id} has invalid numeric event: {event}")
        for trigger in data.get("triggers", []) or []:
            self._validate_effects(trigger.get("effects", []), f"card_modifier {modifier_id}.{trigger.get('event', '<event>')}")

    def _validate_run_modifier(self, modifier_id: str, data: dict[str, Any]) -> None:
        if not data.get("name"):
            self.registry.warnings.append(f"Run modifier {modifier_id} has no name")
        modifier_type = data.get("type", "utility")
        if modifier_type not in self.RUN_MODIFIER_TYPES:
            self.registry.warnings.append(f"Run modifier {modifier_id} has invalid type: {modifier_type}")
        effects = data.get("effects", []) or []
        if not isinstance(effects, list):
            self.registry.warnings.append(f"Run modifier {modifier_id} effects must be a list")
            return
        for effect in effects:
            effect_type = effect.get("type")
            if effect_type not in self.RUN_MODIFIER_EFFECT_TYPES:
                self.registry.warnings.append(f"Run modifier {modifier_id} has invalid effect: {effect_type}")
            if effect_type == "add_card_to_deck" and effect.get("card") not in self.registry.cards:
                self.registry.warnings.append(f"Run modifier {modifier_id} references missing card: {effect.get('card')}")
            if effect_type == "gain_relic" and effect.get("relic") not in self.registry.relics:
                self.registry.warnings.append(f"Run modifier {modifier_id} references missing relic: {effect.get('relic')}")

    def _validate_difficulty_levels(self) -> None:
        seen_levels: set[int] = set()
        for difficulty_id, item in self.registry.difficulty_levels.items():
            data = item.data
            if not data.get("name"):
                self.registry.warnings.append(f"Difficulty {difficulty_id} has no name")
            try:
                level = int(data.get("level"))
            except (TypeError, ValueError):
                self.registry.warnings.append(f"Difficulty {difficulty_id} has invalid level: {data.get('level')}")
                continue
            if level in seen_levels:
                self.registry.warnings.append(f"Duplicate difficulty level: {level}")
            seen_levels.add(level)
            effects = data.get("effects", []) or []
            if not isinstance(effects, list):
                self.registry.warnings.append(f"Difficulty {difficulty_id} effects must be a list")
                continue
            for effect in effects:
                if effect.get("type") not in self.DIFFICULTY_EFFECT_TYPES:
                    self.registry.warnings.append(f"Difficulty {difficulty_id} has invalid effect: {effect.get('type')}")
        if self.registry.difficulty_levels and 0 not in seen_levels:
            self.registry.warnings.append("Difficulty level 0 is missing")

    def _validate_unlock_rules(self) -> None:
        seen_targets: set[tuple[str, str]] = set()
        for unlock_id, item in self.registry.unlock_rules.items():
            data = item.data
            target_type = data.get("target_type")
            target_id = data.get("target_id")
            if target_type not in self.UNLOCK_TARGET_TYPES:
                self.registry.warnings.append(f"Unlock {unlock_id} has invalid target_type: {target_type}")
                continue
            if not target_id:
                self.registry.warnings.append(f"Unlock {unlock_id} has no target_id")
                continue
            target_key = (str(target_type), str(target_id))
            if target_key in seen_targets:
                self.registry.warnings.append(f"Duplicate unlock target: {target_type}.{target_id}")
            seen_targets.add(target_key)
            if not self._target_exists(str(target_type), str(target_id)):
                self.registry.warnings.append(f"Unlock {unlock_id} references missing target: {target_type}.{target_id}")
            self._validate_conditions(data.get("conditions", []) or [], f"unlock {unlock_id}")

    def _validate_achievements(self) -> None:
        for achievement_id, item in self.registry.achievements.items():
            data = item.data
            if not data.get("name"):
                self.registry.warnings.append(f"Achievement {achievement_id} has no name")
            if not isinstance(data.get("category", "general"), str):
                self.registry.warnings.append(f"Achievement {achievement_id} category must be a string")
            self._validate_conditions(data.get("conditions", []) or [], f"achievement {achievement_id}")

    def _target_exists(self, target_type: str, target_id: str) -> bool:
        tables = {
            "character": self.registry.characters,
            "card": self.registry.cards,
            "relic": self.registry.relics,
            "potion": self.registry.potions,
            "run_modifier": self.registry.run_modifiers,
            "ancient": self.registry.ancients,
            "card_modifier": self.registry.card_modifiers,
        }
        return target_id in tables.get(target_type, {})

    def _validate_timeline_fragment(self, fragment_id: str, data: dict[str, Any]) -> None:
        if not data.get("title"):
            self.registry.warnings.append(f"Timeline fragment {fragment_id} has no title")
        conditions = data.get("unlock_conditions", []) or []
        self._validate_conditions(conditions, f"timeline {fragment_id}")

    def _validate_conditions(self, conditions: Iterable[dict[str, Any]], where: str) -> None:
        if not isinstance(conditions, list):
            self.registry.warnings.append(f"{where} conditions must be a list")
            return
        for condition in conditions:
            condition_type = condition.get("type")
            if condition_type not in self.CONDITION_TYPES:
                self.registry.warnings.append(f"{where} has invalid condition: {condition_type}")
            if condition.get("enemy") and condition["enemy"] not in self.registry.enemies:
                self.registry.warnings.append(f"{where} references missing enemy: {condition['enemy']}")
            if condition.get("card") and condition["card"] not in self.registry.cards:
                self.registry.warnings.append(f"{where} references missing card: {condition['card']}")
            if condition.get("relic") and condition["relic"] not in self.registry.relics:
                self.registry.warnings.append(f"{where} references missing relic: {condition['relic']}")
            if condition.get("potion") and condition["potion"] not in self.registry.potions:
                self.registry.warnings.append(f"{where} references missing potion: {condition['potion']}")
            if condition.get("modifier") and condition["modifier"] not in self.registry.card_modifiers:
                self.registry.warnings.append(f"{where} references missing modifier: {condition['modifier']}")
            if condition.get("ancient") and condition["ancient"] not in self.registry.ancients:
                self.registry.warnings.append(f"{where} references missing ancient: {condition['ancient']}")
            if condition.get("fragment") and condition["fragment"] not in self.registry.timeline_fragments:
                self.registry.warnings.append(f"{where} references missing timeline fragment: {condition['fragment']}")
            if condition.get("character") and condition["character"] not in self.registry.characters:
                self.registry.warnings.append(f"{where} references missing character: {condition['character']}")
            if condition.get("achievement") and condition["achievement"] not in self.registry.achievements:
                self.registry.warnings.append(f"{where} references missing achievement: {condition['achievement']}")
            if condition.get("target_type") and condition["target_type"] not in self.UNLOCK_TARGET_TYPES:
                self.registry.warnings.append(f"{where} references invalid target_type: {condition['target_type']}")

    def _validate_effects(self, effects: Iterable[dict[str, Any]], where: str) -> None:
        for effect in effects or []:
            if not isinstance(effect, dict):
                self.registry.warnings.append(f"Invalid effect in {where}: {effect!r}")
                continue
            if effect.get("type") == "apply_status":
                status_id = effect.get("status")
                if status_id not in self.registry.statuses:
                    self.registry.warnings.append(
                        f"{where} references missing status: {status_id}"
                    )
            if effect.get("type") in {"add_card_to_draw_pile", "add_card_to_hand", "add_card_to_deck"}:
                card_id = effect.get("card")
                if card_id not in self.registry.cards:
                    self.registry.warnings.append(
                        f"{where} references missing card: {card_id}"
                    )
            if effect.get("type") == "gain_relic":
                relic_id = effect.get("relic")
                if relic_id not in self.registry.relics:
                    self.registry.warnings.append(
                        f"{where} references missing relic: {relic_id}"
                    )
            if effect.get("type") == "gain_potion":
                potion_id = effect.get("potion")
                if potion_id not in self.registry.potions:
                    self.registry.warnings.append(
                        f"{where} references missing potion: {potion_id}"
                    )
            if effect.get("type") in {"apply_card_modifier", "remove_card_modifier"}:
                modifier_id = effect.get("modifier")
                if modifier_id not in self.registry.card_modifiers:
                    self.registry.warnings.append(
                        f"{where} references missing card modifier: {modifier_id}"
                    )
            if effect.get("type") == "if":
                self._validate_effects(effect.get("then", []), where)
                self._validate_effects(effect.get("else", []), where)
            if effect.get("type") == "repeat":
                self._validate_effects(effect.get("effects", []), where)
