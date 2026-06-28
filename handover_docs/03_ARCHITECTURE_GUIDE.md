# アーキテクチャガイド

## 1. 全体構造

```text
src/spirelike/
  app/
  content/
  core/
  models/
  profile/
  save/
  scenes/
  systems/
  ui/
```

## 2. 主要レイヤー

### app

Pygameアプリ本体とSceneManagerを管理します。

主な責務:

- pygame初期化
- window管理
- event loop
- Scene登録
- autosave hook
- continue saved run

### content

YAMLコンテンツを読み込む層です。

主要クラス:

- `ContentLoader`
- `ContentRegistry`
- `ContentItem`

全システムは原則として `ContentRegistry` から定義を取得します。

### core

ラン生成、RNG、seed処理など、ラン開始時に必要な基盤です。

主要ファイル:

- `run_factory.py`
- `rng.py`
- `seed_utils.py`

### models

Dataclass群です。

代表:

- `RunState`
- `PlayerState`
- `CardInstance`
- `RelicInstance`
- `PotionInstance`
- `EnemyInstance`
- `CombatState`
- `MapState`
- `MapNode`

### systems

ゲームロジックの中心です。

代表:

- `CombatSystem`
- `RewardSystem`
- `PotionSystem`
- `PotionDropSystem`
- `CardRewardRaritySystem`
- `DifficultySystem`
- `MapGenerator`
- `ShopSystem`
- `UnlockSystem`
- `AchievementSystem`
- `NotificationSystem`
- `CardOperationSystem`
- `CardModifierSystem`
- `PowerSystem`
- `AncientSystem`
- `EffectExecutor`

### scenes

Pygameの画面単位です。

代表:

- `TitleScene`
- `SaveSlotScene`
- `RunSetupScene`
- `CharacterSelectScene`
- `MapScene`
- `CombatScene`
- `RewardScene`
- `ShopScene`
- `RestScene`
- `EventScene`
- `AncientScene`
- `ProfileScene`
- `CompendiumScene`
- `UnlockTreeScene`
- `RunResultScene`

### save

RunStateやCombatSnapshotの保存・復元を担当します。

主な責務:

- JSON serializer
- セーブスロット管理
- legacy migration
- combat snapshot
- validation

### profile

Profile永続データです。

主な責務:

- run history
- bestiary
- compendium
- timeline
- unlock
- achievement
- notification
- progression result

## 3. 状態管理の考え方

### RunState

1ランの進行状態を持ちます。

含まれるもの:

- seed
- character_id
- act
- floor
- player
- map_state
- ancient_blessings
- flags
- messages

`flags` は拡張用の軽量ストアです。  
例:

- run_config
- unlocked_content
- card_reward_rare_bonus
- potion_drop_chance
- double_boss_enabled
- shop_card_removes

### ProfileState

ランをまたぐ永続状態です。

含まれるもの:

- summary
- characters
- run_history
- bestiary
- compendium
- timeline
- unlocks
- achievements
- notifications

### CombatState

戦闘中の一時状態です。

含まれるもの:

- enemies
- draw_pile
- hand
- discard_pile
- exhaust_pile
- limbo
- powers
- energy
- turn_number
- pending_selection

## 4. RNG設計

`RunRng` によって、用途別の乱数を分けます。

例:

- map
- combat
- reward
- shop
- event

設計意図:

- seedによる再現性を確保
- 報酬乱数と戦闘乱数の混線を避ける
- smoke testで安定させる

## 5. Effect DSL

カード、敵、レリック、ポーション、エンシェント、イベントはEffect DSLを通じて処理されます。

代表的なeffect:

```yaml
- type: damage
  target: selected_enemy
  amount: 6

- type: gain_block
  target: self
  amount: 5

- type: draw_cards
  amount: 1

- type: apply_status
  target: selected_enemy
  status: poison
  stacks: 3

- type: add_card_to_hand
  card: reagent
  amount: 1

- type: gain_random_potion

- type: apply_card_modifier
  modifier: sharp
  selector:
    zones:
      - master_deck
    count: 1
    player_choice: true
```

## 6. 拡張方針

新しいシステムを追加するときは、以下の順で考えます。

1. YAMLで表現できるか
2. Effect DSLで表現できるか
3. 既存Systemのhookで実装できるか
4. 新しいSystemが必要か
5. Save/Load対象か
6. Profile対象か
7. smoke testをどう書くか

## 7. 循環依存を避ける方針

原則:

- SceneはSystemを呼んでよい。
- SystemはSceneを知らない。
- SystemはContentRegistryを参照してよい。
- RunStateはSystemを知らない。
- ProfileSystemはUnlockSystem/AchievementSystemを呼んでよい。
- UIはゲームロジックを直接変更しすぎない。

## 8. 典型的な処理フロー

### ラン開始

```text
RunSetupScene
  -> CharacterSelectScene
  -> create_run()
  -> DifficultySystem.apply_run_start_effects()
  -> RunModifierSystem.apply_run_start_modifiers()
  -> ProfileSystem.record_run_started()
  -> AncientScene
  -> MapScene
```

### 戦闘

```text
MapScene
  -> CombatScene
  -> CombatSystem
  -> ActionQueue
  -> EffectExecutor
  -> RewardScene
```

### ラン終了

```text
RunResultScene
  -> ProfileSystem.finalize_run()
  -> metrics反映
  -> Difficulty進行
  -> Timeline解放
  -> Achievement評価
  -> Unlock評価
  -> Notification生成
```

## 9. 実装時の注意

- `ContentLoader` に新規YAML種類を追加したらvalidationも追加する。
- `RunState.flags` に新規値を入れる場合、既存セーブ未設定時のdefaultを必ず考える。
- RewardBundleなどScene payloadに入るものはserializer対応が必要。
- 戦闘中に新規状態を追加する場合、CombatSnapshot対応を忘れない。
- 乱数を使う場合は、既存のRunRng namespaceを使う。
