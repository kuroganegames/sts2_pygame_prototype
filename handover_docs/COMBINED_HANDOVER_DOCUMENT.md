

<!-- 00_README_INDEX.md -->


# STS2 Pygame Prototype 引継ぎ・開発ドキュメント一式

作成日: 2026-06-28  
対象リポジトリ: `kuroganegames/sts2_pygame_prototype`  
前提: PR16 `Ascension Fidelity Pass` までGitHub上でマージ済み

このドキュメント群は、PygameベースのSlay the Spire 2風ローグライクデッキビルダー・プロトタイプの開発引継ぎ、今後の開発計画、派生ゲーム開発時の参考資料をまとめたものです。

## 推奨読書順

1. `01_HANDOVER_SUMMARY.md`  
   現在の開発状況、完了済み領域、未完了領域、次の判断ポイント。

2. `02_CURRENT_SYSTEM_INVENTORY.md`  
   現在実装済みのゲームシステム棚卸し。

3. `03_ARCHITECTURE_GUIDE.md`  
   ディレクトリ構造、主要クラス、状態管理、RNG、セーブ、Scene構成。

4. `04_CONTENT_AUTHORING_GUIDE.md`  
   YAMLコンテンツ追加ルール。カード、敵、レリック、ポーション、エンシェント、イベント、Unlockなど。

5. `05_STS2_LIKE_GAME_DESIGN_SPEC.md`  
   このプロトタイプを用いてSTS2風ゲームを作るためのゲームデザイン仕様書。

6. `06_DEVELOPMENT_WORKFLOW_AND_TESTS.md`  
   開発手順、テスト方針、smoke test、PR作成ルール。

7. `07_ROADMAP_AND_BACKLOG.md`  
   今後の優先度付きロードマップ。PR17以降の候補を含む。

8. `08_DERIVATIVE_GAME_SYSTEM_REFERENCE.md`  
   このプロトタイプから派生ゲームシステムを作るときの設計リファレンス。

9. `09_RISK_AND_IP_NOTES.md`  
   STS2風ゲームとして開発する際の権利・仕様忠実度・運用上の注意。

10. `10_MAINTENANCE_CHECKLIST.md`  
    今後の保守、リリース、テスト、マージ時のチェックリスト。

## 現在の大まかな結論

基本システムの構築は、プロトタイプとしてはほぼ完了しています。  
今後は「基盤開発」よりも、以下のフェーズへ移行するのが妥当です。

- 仕様忠実度向上
- コンテンツ拡張
- バランス調整
- UI/UX改善
- 自動テストとセーブ互換性の強化
- 独自ゲーム化に向けた名称・素材・世界観の差し替え

## 重要な前提

このプロトタイプは、公式のSlay the Spire 2を再現・複製するためのものではなく、同ジャンルのゲームシステムを独自に実装するための土台です。  
商用化や公開を視野に入れる場合は、公式名称、公式画像、公式テキスト、公式カード名、公式キャラクター名を避け、独自名称・独自アート・独自バランスへ置き換えてください。



<!-- 01_HANDOVER_SUMMARY.md -->


# 引継ぎサマリー

## 1. 現在の状態

このプロトタイプは、Pygameベースのローグライクデッキビルダーとして、開始からラン終了までの主要ループを持つ状態まで到達しています。

実装済みの大枠は以下です。

- タイトル画面
- セーブスロット
- Run Setup
- キャラクター選択
- マップ生成
- マップノード選択
- 戦闘
- 報酬
- ショップ
- 休憩所
- イベント
- エンシェント
- ポーション
- レリック
- カード修飾
- Power
- ActionQueue
- Profile
- Run History
- Bestiary
- Compendium
- Timeline
- Unlock
- Achievement
- Notification
- Unlock Tree
- Card Reward Rarity System
- Potion Drop Accumulator
- Difficulty / Ascension Fidelity Pass
- 追加キャラクター基盤

結論として、**基本的なシステム構築はほぼ完了**と見てよいです。

## 2. 現在のmain前提

この資料では、GitHub上でPR16までマージ済みとして扱います。

現在のmainには、少なくとも以下の要素が入っている前提です。

- PR1〜PR13の各基盤
- PR14: Card Reward Rarity System
- PR15: Potion Drop Accumulator
- PR16: Ascension Fidelity Pass

## 3. 開発フェーズの切り替え

ここまでの開発は「基盤を作る」フェーズでした。

次のフェーズは以下です。

```text
基盤開発
  ↓
仕様忠実度向上
  ↓
コンテンツ拡張
  ↓
バランス調整
  ↓
UI/UX改善
  ↓
独自ゲーム化 / プロダクト化
```

現在は「仕様忠実度向上」と「コンテンツ拡張」の境界にいます。

## 4. 今止めるならやるべきこと

一度開発を止める場合、以下を行うと安全です。

1. mainの最新状態で全smoke testを実行する。
2. saves/配下のテスト用セーブを削除またはgitignore対象にする。
3. 未マージPRや閉じたPRの状況を整理する。
4. READMEに「現在の到達点」と「未実装領域」を追記する。
5. content schemaの最低限の仕様を固定する。
6. 今後の追加コンテンツ作業は、YAML追加とsmoke test追加をセットにする。
7. 公式STS2由来の固有名詞・素材が混ざっていないか確認する。

## 5. すぐ再開するなら優先すべきテーマ

PR17以降の候補は以下です。

優先度A:

- PR17: Shop Fidelity Pass
- PR18: Map Event Room Odds
- PR19: Act2 / Act3 Skeleton
- PR20: Act別敵・イベント・ボスプール
- PR21: Potion reward UI改善

優先度B:

- Alchemistカードバランス調整
- 新イベント追加
- 新敵・新ボス追加
- Unlock Tree UI改善
- 通知UI改善

優先度C:

- アニメーション
- SE/BGM
- 専用アート
- 入力/操作性改善
- オプション画面

## 6. 引継ぎ時の注意

このプロトタイプは、公式のSlay the Spire 2を再現するものではなく、STS2風のゲームシステムを独自に実装するための土台です。  
公式の名称、画像、テキスト、数値をそのまま商品利用するのは避け、独自名称・独自バランス・独自素材に差し替える前提で扱ってください。

## 7. 現在の到達度評価

| 領域 | 状態 |
|---|---|
| 戦闘基盤 | ほぼ完了 |
| カード/レリック/ポーションYAML | ほぼ完了 |
| マップ基盤 | ほぼ完了 |
| イベント基盤 | 最小実装済み |
| ショップ | 基本実装済み、精密化余地あり |
| セーブ/ロード | かなり進んでいる |
| Profile/Unlock/Achievement | 実装済み |
| Difficulty/Ascension | PR16で0〜10相当まで拡張済み |
| Act2/Act3 | 未実装または簡易 |
| 大型ギミック | 未実装 |
| UI/UX | プロトタイプ段階 |
| アート/音 | 仮素材段階 |



<!-- 02_CURRENT_SYSTEM_INVENTORY.md -->


# 現在のシステム棚卸し

## 1. コンテンツ管理

YAML駆動のコンテンツ管理が実装されています。

主なコンテンツ種別:

- characters
- cards
- enemies
- relics
- potions
- ancients
- card_modifiers
- run_modifiers
- difficulty_levels
- unlocks
- achievements
- timeline
- statuses
- maps
- events

原則として、コンテンツIDとYAMLファイル名を一致させます。

例:

```text
content/cards/wanderer/strike.yaml
id: strike
```

画像は同名画像またはYAMLの `image` 指定で読み込まれます。

## 2. 戦闘

実装済み:

- CombatSystem
- CombatState
- ActionQueue
- DamageAction
- GainBlockAction
- DrawCardsAction
- ApplyStatusAction
- TriggerEventAction
- PowerSystem
- CardRules
- CardModifierSystem
- CardOperationSystem
- PotionSystem
- Ancient trigger
- Relic trigger
- Enemy AI
- Intent表示

カードキーワード相当:

- Exhaust
- Retain
- Ethereal
- Innate
- Unplayable
- Power
- Status
- Curse
- Temporary/generated card

未完または簡易:

- Orb
- Summon
- Replay
- Lethal
- Artifact
- Incorporeal
- detailed Affliction
- complex enemy mechanics

## 3. 報酬

実装済み:

- CombatReward
- TreasureReward
- Card reward
- Relic reward
- Potion reward
- Gold reward
- Card Reward Rarity System
- Rare bonus
- Act-based upgrade chance
- Potion Drop Accumulator
- Unlock filtering

注意:

- Card Reward Rarity Systemは、カード報酬をレアリティ先行抽選に寄せたもの。
- Potion Drop Accumulatorは、戦闘報酬ポーションの固定確率を廃止し、蓄積値方式に変更したもの。
- Shopのカードタイプ固定枠や価格仕様はまだ簡易。

## 4. マップ

実装済み:

- YAMLベースのマップ生成
- layer
- fixed_layers
- weights_by_depth
- encounter_pools
- ノード接続
- start node
- boss node
- Difficultyによるelite weight multiplier hook

未完:

- Act2 / Act3
- ?マスの詳細抽選
- Actごとのイベント蓄積確率
- ダブルボス実戦接続
- マップスクロール / 大規模マップUI

## 5. セーブ

実装済み:

- RunState serialize
- PlayerState serialize
- MapState serialize
- RewardBundle serialize
- RewardCardChoice互換
- Potion drop metadata保存
- CombatSnapshot serialize
- 複数セーブスロット
- legacy save migration
- safe scene payload
- 戦闘中セーブガード

注意:

- ActionQueue解決途中のセーブは制限されています。
- Card selection overlay中のセーブは制限されています。
- RewardBundleの互換は、旧 `list[str]` と新 `RewardCardChoice` に対応。

## 6. Profile / メタ進行

実装済み:

- profile.json
- summary
- character stats
- run_history
- bestiary
- compendium
- timeline
- unlocks
- achievements
- notifications

実装済みの長期進行:

- Character別Difficulty解放
- Content Unlock
- Achievement
- Notification
- Unlock Tree

未完:

- 年代記未読時の開始制限
- 実績報酬
- Unlock Treeのグラフ線・スクロール・詳細パネル

## 7. Difficulty / Ascension

PR16でDifficulty 0〜10のAscension相当構造が入りました。

現在の想定:

- D0: 標準
- D1: エリート出現率上昇
- D2: 初期HP80% / エンシェント回復量80%
- D3: 戦闘・宝箱ゴールド25%減
- D4: ポーションスロット-1
- D5: 初期呪い
- D6: カード削除費用増加
- D7: カード報酬枯渇hook
- D8: 敵HP増加
- D9: 敵攻撃増加
- D10: Act3 double boss flag

A10はflagのみで、Act3実戦接続は未実装です。

## 8. 追加キャラクター

実装済み:

- Wanderer
- Alchemist

Alchemistの特徴:

- 毒
- 試薬
- ポーション生成
- 専用スターターデッキ
- 専用スターターレリック
- Unlock条件付きキャラクター

注意:

- 画像は仮アセット参照。
- カードバランスは未調整。
- 専用イベントは未実装。



<!-- 03_ARCHITECTURE_GUIDE.md -->


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



<!-- 04_CONTENT_AUTHORING_GUIDE.md -->


# コンテンツ作成ガイド

## 1. 基本ルール

原則として、コンテンツIDとYAMLファイル名を一致させます。

```yaml
id: strike
```

```text
content/cards/wanderer/strike.yaml
```

画像は以下の順で解決されます。

1. YAMLの `image` 指定
2. 同名画像
3. 見つからなければwarning

例:

```yaml
image: strike.png
```

## 2. カード

配置例:

```text
content/cards/wanderer/strike.yaml
content/cards/alchemist/emergency_brew.yaml
content/cards/curses/ascender_blight.yaml
```

基本形:

```yaml
schema_version: 1
id: sample_attack
name: サンプル攻撃
image: strike.png
character: wanderer
type: attack
rarity: common
cost: 1
target: enemy
description: 6ダメージを与える。
effects:
  - type: damage
    target: selected_enemy
    amount: 6
upgrade:
  name: サンプル攻撃+
  description: 9ダメージを与える。
  effects:
    - type: damage
      target: selected_enemy
      amount: 9
```

### type

- attack
- skill
- power
- status
- curse

### rarity

- basic
- common
- uncommon
- rare
- special

### keywords

```yaml
keywords:
  - exhaust
  - retain
  - ethereal
  - innate
  - unplayable
```

## 3. 敵

配置例:

```text
content/enemies/act1/slime_small.yaml
```

基本形:

```yaml
schema_version: 1
id: slime_small
name: 小さなスライム
hp:
  min: 10
  max: 14
moves:
  attack:
    intent: attack
    damage: 5
    weight: 70
    effects:
      - type: damage
        target: player
        amount: 5
ai:
  type: weighted_random
```

## 4. レリック

配置例:

```text
content/relics/common/steady_gear.yaml
content/relics/starter/experimental_kit.yaml
```

基本形:

```yaml
schema_version: 1
id: steady_gear
name: 安定歯車
image: iron_leaf.png
rarity: common
unique: true
description: 戦闘開始時、ブロックを3得る。
triggers:
  - event: combat_start
    effects:
      - type: gain_block
        target: self
        amount: 3
```

## 5. ポーション

配置例:

```text
content/potions/common/fire_potion.yaml
```

基本形:

```yaml
schema_version: 1
id: swift_potion
name: 迅速のポーション
image: fire_potion.png
rarity: uncommon
usage: combat
target: none
description: カードを2枚引く。
effects:
  - type: draw_cards
    amount: 2
```

## 6. エンシェント

配置例:

```text
content/ancients/neo.yaml
```

基本形:

```yaml
schema_version: 1
id: sample_ancient
name: 古き存在
image: sample.png
weight: 100
act_pool:
  - 1
choices:
  - id: heal
    name: 回復
    description: HPを回復する。
    effects:
      - type: heal
        amount: 10
```

## 7. イベント

配置例:

```text
content/events/act1/sample_event.yaml
```

基本形:

```yaml
schema_version: 1
id: sample_event
name: サンプルイベント
image: sample.png
description: 道端に不思議な箱がある。
choices:
  - id: take_gold
    text: ゴールドを得る。
    effects:
      - type: gain_gold
        amount: 50
```

## 8. Run Modifier

配置例:

```text
content/run_modifiers/glass_path.yaml
```

基本形:

```yaml
schema_version: 1
id: glass_path
name: 硝子の道
type: challenge
description: 敵HPが20%増えるが、開始時にカードを得る。
profile_eligible: false
effects:
  - type: enemy_hp_multiplier
    multiplier: 1.2
  - type: add_card_to_deck
    card: focus_blade
```

## 9. Difficulty Level

配置例:

```text
content/difficulty_levels/difficulty_07.yaml
```

PR16後の例:

```yaml
schema_version: 1
id: difficulty_07
level: 7
name: 枯渇
description: レア及びアップグレード済みカードの出現率が下がる。
effects:
  - type: card_reward_depletion
    enabled: true
```

## 10. Unlock Rule

配置例:

```text
content/unlocks/unlock_alchemist.yaml
```

基本形:

```yaml
schema_version: 1
id: unlock_alchemist
target_type: character
target_id: alchemist
initially_unlocked: false
hidden_until_unlocked: false
name: 錬金術師
description: 実績「最初の踏破」達成後、錬金術師が使用可能になる。
category: character
tier: 2
order: 30
conditions:
  - type: achievement_unlocked
    achievement: first_victory
```

## 11. Achievement

配置例:

```text
content/achievements/alchemist_victory.yaml
```

基本形:

```yaml
schema_version: 1
id: alchemist_victory
name: 錬金術の証明
category: character
description: 錬金術師で勝利する。
locked_description: 錬金術師でランを勝利する。
hidden_until_unlocked: false
profile_eligible_required: true
conditions:
  - type: character_victories_at_least
    character: alchemist
    amount: 1
```

## 12. 条件式

主な条件:

```yaml
- type: victories_at_least
  amount: 1

- type: character_victories_at_least
  character: alchemist
  amount: 1

- type: enemy_defeated_count_at_least
  enemy: cultist
  amount: 3

- type: potion_used
  potion: fire_potion

- type: achievement_unlocked
  achievement: first_victory

- type: unlocked_count_at_least
  target_type: run_modifier
  amount: 2

- type: timeline_unlocked
  fragment: first_steps
```

## 13. 新規コンテンツ追加時のチェックリスト

1. YAMLファイル名とidが一致している。
2. 画像が存在する。
3. 参照先カード・レリック・敵・ポーションが存在する。
4. `PYTHONPATH=src python tools/validate_content.py` を通す。
5. smoke testを追加する。
6. READMEか該当docsを更新する。
7. Unlock対象ならUnlock Treeで表示を確認する。



<!-- 05_STS2_LIKE_GAME_DESIGN_SPEC.md -->


# STS2風ゲーム開発用ゲームデザイン仕様書

## 1. 目的

このプロトタイプを使って、Slay the Spire 2風のシングルプレイ・ローグライクデッキビルダーを独自コンテンツで開発するための仕様書です。

## 2. 開発方針

- 公式素材や公式テキストは使わない。
- 公式カード名や固有名詞は使わない。
- 参考にするのはゲームジャンル上の構造と抽象仕様。
- 実装はYAML駆動で拡張しやすくする。
- まずシングルプレイのみ対象とする。
- オンライン要素・マルチプレイは対象外。

## 3. コアループ

```text
タイトル
  ↓
Run Setup
  ↓
キャラクター選択
  ↓
ラン開始ボーナス / エンシェント
  ↓
マップ選択
  ↓
ノード解決
    - 戦闘
    - エリート
    - ボス
    - イベント
    - ショップ
    - 休憩
    - 宝箱
    - エンシェント
  ↓
報酬
  ↓
次ノード
  ↓
ボス撃破 / 敗北
  ↓
RunResult
  ↓
Profile更新
```

## 4. 戦闘設計

### 4.1 ターン構造

```text
戦闘開始
  ↓
combat_start trigger
  ↓
初期ドロー
  ↓
プレイヤーターン
  - カード使用
  - ポーション使用
  - エネルギー消費
  ↓
ターン終了
  - discard
  - ethereal処理
  - retain処理
  ↓
敵ターン
  - intent実行
  ↓
次ターン
```

### 4.2 カード種別

- Attack
- Skill
- Power
- Status
- Curse

### 4.3 基本ステータス

- HP
- Block
- Strength
- Weak
- Vulnerable
- Poison

今後追加候補:

- Dexterity
- Artifact
- Thorns
- Intangible
- Orb
- Focus
- Summon
- Doom
- Replay
- Lethal

## 5. 報酬設計

### 5.1 カード報酬

現在の仕様:

- レアリティ先行抽選
- 通常敵 / エリート / ボス / ショップで確率が異なる
- レア補正値あり
- Act別アップグレード確率あり
- Unlock済みカードのみ候補
- 使用キャラクターまたはneutralのみ候補

### 5.2 ポーション報酬

現在の仕様:

- 初期ドロップ蓄積値40%
- ドロップ成功で-10%
- 失敗で+10%
- エリート補正+12.5%
- Actまたぎで維持
- 満杯時は抽選しない

### 5.3 レリック報酬

現在は簡易weight抽選です。  
今後、レリック抽選袋やレアリティ固定抽選を追加する余地があります。

## 6. メタ進行

### 6.1 Profile

Profileはランをまたいで保持します。

- summary
- character stats
- run history
- bestiary
- compendium
- timeline
- unlocks
- achievements
- notifications

### 6.2 Unlock

Unlock Ruleによりコンテンツの解放状態を制御します。

対象:

- character
- card
- relic
- potion
- run_modifier
- ancient
- card_modifier

### 6.3 Achievement

Achievementは長期目標です。  
実績解除はNotificationとRunResultに表示されます。

### 6.4 Unlock Tree

Unlock Treeは、解放済み/未解放/hidden状態を一覧表示します。

## 7. Difficulty / Ascension

Difficultyはキャラクター別解放です。  
PR16以降は0〜10段階のAscension相当として扱います。

想定:

- D0: 標準
- D1: エリート増
- D2: 初期HP/エンシェント回復低下
- D3: ゴールド減
- D4: ポーションスロット減
- D5: 初期呪い
- D6: 削除費用増
- D7: 枯渇
- D8: 敵HP増
- D9: 敵攻撃増
- D10: ダブルボス

## 8. キャラクター設計

### 8.1 Wanderer

基本キャラクター。  
攻撃、防御、ドロー、シンプルな状態付与を持つ。

### 8.2 Alchemist

毒、試薬、ポーション生成寄り。  
Unlockにより解放される追加キャラクター。

設計軸:

- Poison
- Reagent
- Potion slot
- Generated card

## 9. 今後のコンテンツ設計指針

カード追加時は、以下を意識してください。

- そのキャラクターの軸に合うか
- 既存カードと役割が被りすぎないか
- upgradeで意味のある変化があるか
- 報酬プールに入れてよいか
- Unlock条件が必要か
- 生成カードならrarityをbasic/specialにして報酬から除外するか
- Smoke testで読み込み確認するか

## 10. 完成度を上げる優先領域

優先度A:

- Shop Fidelity
- ?マス抽選
- Act2 / Act3
- 敵・イベント・ボス追加

優先度B:

- キーワード拡張
- Orb/Summon
- レリック抽選精密化
- ポーション取得UI改善

優先度C:

- アニメーション
- サウンド
- アート
- 翻訳



<!-- 06_DEVELOPMENT_WORKFLOW_AND_TESTS.md -->


# 開発ワークフローとテスト

## 1. 基本セットアップ

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Windowsの場合:

```powershell
.venv\Scripts\activate
```

## 2. 基本確認コマンド

```bash
python -m compileall -q src main.py
PYTHONPATH=src python tools/validate_content.py
```

## 3. smoke test方針

このプロトタイプはpytestではなく、`tools/smoke_test_*.py` 形式の軽量テストを多数持つ方針です。

理由:

- GitHub PR本文にコマンドを列挙しやすい
- 個別システムの独立検証がしやすい
- Pygame UIを起動せずロジック確認できる
- YAMLコンテンツ読み込み確認に向く

## 4. 新規PRで必ずやること

1. 変更対象を小さく切る。
2. 新規Systemを追加したらsmoke testを追加する。
3. YAML schemaを増やしたらContentLoader validationを更新する。
4. Save/Load対象ならserializerを更新する。
5. READMEを必要最低限更新する。
6. PR本文に実装内容と確認コマンドを書く。
7. 既存セーブ互換の扱いを明記する。

## 5. 推奨PR粒度

良い例:

```text
PR15:
  PotionDropSystemだけ実装
  RewardSystem接続
  Save対応
  smoke test追加
```

悪い例:

```text
PotionDropSystem
+ Shop価格
+ Act2
+ 新キャラ
+ UI全面改修
```

1PRに複数の大きな関心事を混ぜないでください。

## 6. テストカテゴリ

### Content validation

```bash
PYTHONPATH=src python tools/validate_content.py
```

確認:

- YAML id
- 画像
- 参照先
- effect
- condition
- difficulty effect

### Logic smoke tests

例:

```bash
PYTHONPATH=src python tools/smoke_test_logic.py
PYTHONPATH=src python tools/smoke_test_actions.py
PYTHONPATH=src python tools/smoke_test_powers.py
```

### Save smoke tests

例:

```bash
PYTHONPATH=src python tools/smoke_test_save_roundtrip.py
PYTHONPATH=src python tools/smoke_test_combat_snapshot_roundtrip.py
PYTHONPATH=src python tools/smoke_test_save_slots.py
```

### Profile smoke tests

例:

```bash
PYTHONPATH=src python tools/smoke_test_profile_roundtrip.py
PYTHONPATH=src python tools/smoke_test_run_history.py
PYTHONPATH=src python tools/smoke_test_timeline_unlocks.py
```

### Reward smoke tests

例:

```bash
PYTHONPATH=src python tools/smoke_test_card_reward_rarity_odds.py
PYTHONPATH=src python tools/smoke_test_potion_drop_initial_odds.py
```

## 7. PR作成テンプレート

```markdown
## 概要

- 追加した機能
- 変更したシステム
- 追加したYAML
- 追加したテスト

## 仕様

実装仕様を箇条書き。

## 互換性

- 既存セーブへの影響
- 旧形式の読み込み
- migrationの有無

## 確認

```bash
python -m compileall -q src main.py
PYTHONPATH=src python tools/validate_content.py
...
```

## 補足

後続PRに回したもの。
```

## 8. セーブ互換の考え方

`RunState.flags` に新規値を追加する場合:

- 未設定時のdefaultを必ず持つ。
- serializer変更が不要ならflagsに入れる。
- Scene payloadに入るものはserializer対応する。
- 旧セーブで存在しないフィールドは空値またはdefaultで復元する。

## 9. UI変更時の注意

Pygame UIは自動テストしにくいので、UI変更では以下を意識します。

- ロジックはSystemへ寄せる。
- SceneはSystemの結果を描画するだけに近づける。
- ボタン押下時の状態変更を小さくする。
- payloadはJSON化できる形を保つ。
- 保存可能Sceneかどうか確認する。

## 10. コンテンツ追加時のテスト例

新カードを追加した場合:

```python
registry = ContentLoader(ROOT / "content").load()
assert not registry.warnings
assert "new_card" in registry.cards
```

新キャラを追加した場合:

```python
run = create_run(registry, "new_character", seed=123)
assert run.character_id == "new_character"
assert len(run.player.deck) > 0
```

Unlockを追加した場合:

```python
system = UnlockSystem(registry)
assert not system.is_unlocked(profile, "card", "new_card")
profile.summary["victories"] = 1
system.evaluate_unlocks(profile)
assert system.is_unlocked(profile, "card", "new_card")
```



<!-- 07_ROADMAP_AND_BACKLOG.md -->


# ロードマップとバックログ

## 現在のフェーズ

基盤開発はほぼ完了。  
今後は以下のフェーズです。

```text
1. 仕様忠実度向上
2. コンテンツ拡張
3. バランス調整
4. UI/UX改善
5. 派生ゲーム化
```

## 優先度A: 仕様忠実度向上

### PR17: Shop Fidelity Pass

候補内容:

- カード削除UI
- 削除費用表示
- D6削除費用hook接続
- ショップ価格帯
- 半額カード
- 上段カードタイプ固定
- 無色カード枠
- レリック価格
- ポーション価格

### PR18: Map Event Room Odds

候補内容:

- ?マス抽選
- 通常敵 / 宝箱 / ショップ / イベントの蓄積値
- Act開始時リセット
- MapGeneratorのnode_type抽選強化
- Debug出力

### PR19: Act2 / Act3 Skeleton

候補内容:

- content/maps/act2.yaml
- content/maps/act3.yaml
- Act遷移
- Act別敵プール
- Act別イベントプール
- Act別ボス
- A10 double boss接続

### PR20: Act Content Pack

候補内容:

- Act2敵
- Act2イベント
- Act2エリート
- Act2ボス
- Act3敵
- Act3ボス

## 優先度B: コンテンツ拡張

### Alchemist Balance Pass

- Alchemistカードの数値調整
- 新Power追加
- ポーション生成カードの調整
- 毒カードのバランス
- 専用Unlock追加

### Wanderer Card Pack 02

- Attack/Skill/Power追加
- deck archetype強化
- Retain/Exhaust/Power連携

### Enemy Pack 02

- Act1敵追加
- Elite追加
- Boss追加
- Afflictionを使う敵
- カード修飾を付与する敵

### Event Pack 02

- カード削除イベント
- レリック交換イベント
- ポーションイベント
- HP/MaxHP選択イベント
- Unlock条件付きイベント

## 優先度C: 大型メカニクス

### OrbSystem

必要なもの:

- Orb slot
- channel
- evoke
- passive
- focus
- card effects
- UI表示

### SummonSystem

必要なもの:

- friendly minion
- summon slot
- minion action
- enemy targeting
- death trigger

### Advanced Keywords

候補:

- Artifact
- Thorns
- Intangible
- Replay
- Lethal
- Doom
- Forge
- Vitality

## 優先度D: UI/UX

- カード詳細tooltip
- レリック詳細tooltip
- ポーション破棄/入れ替えUI
- Unlock Tree詳細パネル
- Map scroll
- Combat log改善
- Settings
- Key config
- Animation
- SE/BGM

## 優先度E: 開発基盤

- pytest移行または併用
- GitHub Actions
- content schema json化
- save migration versioning
- debug menu
- deterministic replay
- golden seed tests
- lint/type check

## 長期目標

### MVP完成条件

- 2キャラ以上
- Act1〜Act3
- 各Actに敵・エリート・ボス
- イベント30以上
- レリック50以上
- ポーション20以上
- カード各キャラ40以上
- Ascension 0〜10
- セーブ/ロード安定
- Unlock/achievement一通り動作

### 派生ゲーム化条件

- 公式STS2名・画像・テキストを完全排除
- 独自世界観
- 独自キャラ
- 独自カード名
- 独自アート
- 独自バランス
- ライセンス確認済み素材のみ



<!-- 08_DERIVATIVE_GAME_SYSTEM_REFERENCE.md -->


# 派生ゲームシステム開発リファレンス

## 1. このプロトタイプを派生ゲームに使うときの考え方

このプロトタイプは、Slay the Spire 2風のゲームを作るための「構造」を提供します。  
派生ゲームでは、以下を差し替えるのが基本です。

- 世界観
- キャラクター
- カード名
- レリック名
- ポーション名
- 敵
- イベント
- UIテーマ
- アート
- バランス

残してよいもの:

- YAML駆動構造
- RunState / CombatState構造
- ActionQueue
- Effect DSL
- RewardSystem
- Unlock/Achievement
- Save/Profile
- Scene構造

## 2. 派生ゲームで最初に決めるべきこと

### 2.1 コアテーマ

例:

```text
錬金術
機械都市
深海探索
夢世界
SF宇宙船
妖怪退治
```

### 2.2 キャラクター軸

各キャラに、3つ程度の主軸を与えます。

例:

```text
Alchemist:
  - Poison
  - Reagent
  - Potion

Engineer:
  - Orb
  - Turret
  - Overload

Hunter:
  - Bleed
  - Retain
  - Combo
```

### 2.3 リソース設計

デフォルトでは以下があります。

- HP
- Block
- Energy
- Cards
- Potions
- Gold

派生ゲームで追加するなら、まずEffect DSL化できるか検討します。

例:

- Heat
- Mana
- Ammo
- Sanity
- Faith
- Charge

## 3. カード設計テンプレート

カードを作るときは、以下を決めます。

```text
1. キャラクター
2. カード種別
3. レアリティ
4. コスト
5. ターゲット
6. 通常効果
7. アップグレード効果
8. キーワード
9. Unlock条件
10. 報酬プールに出すか
```

## 4. キャラクター設計テンプレート

```yaml
schema_version: 1
id: new_character
name: 新キャラクター
image: new_character.png
max_hp: 70
starting_hp: 70
starting_gold: 99
base_energy: 3
starting_potion_slots: 3
starting_deck:
  - new_strike
  - new_strike
  - new_defend
starting_relics:
  - new_starter_relic
description: キャラクター説明。
```

### チェック項目

- starting_deckのカードがすべて存在する。
- starting_relicsがすべて存在する。
- 画像が存在する。
- RewardSystemでそのキャラのカードが出る。
- 他キャラの報酬に混ざらない。
- Unlockが必要ならUnlock Ruleを追加する。

## 5. 新規大型メカニクス追加手順

例: OrbSystemを追加する場合

1. `models` にOrbInstanceを追加する。
2. `CombatState` にorbsを追加する。
3. `save/combat_serializer.py` を更新する。
4. `systems/orb_system.py` を作る。
5. Effect DSLに `channel_orb`, `evoke_orb` を追加する。
6. UIにOrb表示を追加する。
7. smoke testを書く。
8. サンプルカードを追加する。

## 6. 派生ゲーム向けに避けるべきこと

- 公式カード名をそのまま使う。
- 公式キャラクター名をそのまま使う。
- 公式説明文をそのまま使う。
- 公式画像やUI素材を使う。
- 数値・効果・名称を完全一致させたコンテンツ群を作る。
- Wikiの文章をそのままYAMLに転記する。

## 7. 独自性を出す方法

- カードの効果軸を変える。
- 状態異常を独自名称にする。
- レリックを世界観に合わせる。
- ポーションを消耗品以外の形にする。
- マップノードに独自ノードを追加する。
- エンシェント相当を別テーマにする。
- Unlock Treeをストーリー進行にする。

## 8. 新規派生ゲームの最小構成

最初のMVPとして必要な量:

```text
Characters:
  1〜2体

Cards:
  各キャラ 25〜40枚

Enemies:
  通常敵 8〜12体
  エリート 3体
  ボス 2体

Relics:
  25〜40個

Potions:
  8〜12個

Events:
  10〜15個

Acts:
  1 Actでも可
```

## 9. バランス調整の考え方

- 1コストAttackは6〜8ダメージ基準。
- 1コストSkillは5〜8ブロック基準。
- 0コストカードはExhaustや条件付きにする。
- 2コストカードは効果を大きくするが手札事故も考慮する。
- Powerは長期戦で強いので即効性を抑える。
- 毒やDoTは累積しすぎると壊れやすい。
- ポーション生成はスロット制限と組み合わせて調整する。
- レリックは戦闘開始時効果を控えめにする。

## 10. 派生ゲームでの推奨開発順

```text
1. 世界観とキャラ軸を決める
2. 1キャラ目のstarter deckを作る
3. 通常敵を作る
4. 戦闘が楽しいか確認
5. 報酬カードを増やす
6. レリックを増やす
7. イベントを増やす
8. ボスを作る
9. Unlock/Achievementを接続する
10. UI/アート/音を差し替える
```



<!-- 09_RISK_AND_IP_NOTES.md -->


# リスク・権利・運用上の注意

## 1. 重要な前提

このプロトタイプは、Slay the Spire 2風のローグライクデッキビルダーを独自に作るための技術検証です。  
公式ゲームの複製や代替を目的にしないでください。

## 2. 避けるべきもの

公開・配布・商用化する場合、以下は避けてください。

- 公式キャラクター名
- 公式カード名
- 公式レリック名
- 公式ポーション名
- 公式イベント名
- 公式説明文
- 公式画像
- 公式UI素材
- 公式ロゴ
- 公式音声・音楽
- Wikiの文章の丸写し
- 公式数値・効果を大量にそのままコピーしたコンテンツセット

## 3. 参考にしてよいもの

一般的なゲームシステムとして参考にしやすいもの:

- ローグライクデッキビルダーというジャンル構造
- ターン制カード戦闘
- レリック型パッシブ
- ポーション型消耗品
- マップノード選択
- 報酬選択
- 高難度段階
- Unlock/Achievement
- セーブ/ロード構造

ただし、具体的な名称・表現・アートは独自化してください。

## 4. プロトタイプ内の仮素材

現在のプロトタイプは既存の仮画像参照を行っている箇所があります。

例:

- wanderer.png
- strike.png
- old_charm.png

派生ゲーム化する場合、これらはすべて独自素材に差し替えるべきです。

## 5. Wiki参照時の注意

Wikiは仕様理解には便利ですが、以下に注意してください。

- 文章をそのままコピーしない。
- 固有名詞をそのまま使わない。
- 数値をそのまま使う場合も、ゲームバランス上の独自調整を加える。
- 実装メモやドキュメントでは、参考元として扱い、ゲーム内データには転記しない。

## 6. ライセンス管理

今後アートや音を追加する場合は、以下を記録してください。

```text
assets/
  LICENSES.md
  source_urls.md
  author.md
```

素材ごとに記録する情報:

- 作者
- ライセンス
- 利用条件
- 改変可否
- 商用利用可否
- 入手URL
- 取得日

## 7. 公開前チェックリスト

- 公式由来の名前が残っていない。
- 公式由来の画像が残っていない。
- READMEに「fan clone」など誤解を招く表現がない。
- 独自タイトルになっている。
- 独自世界観になっている。
- ライセンス不明素材がない。
- セーブデータに開発用パスが入っていない。
- Debug UIが残っていない。
- テスト用コンテンツが本番に混ざっていない。



<!-- 10_MAINTENANCE_CHECKLIST.md -->


# 保守・リリース・マージ用チェックリスト

## 1. マージ前チェック

```bash
python -m compileall -q src main.py
PYTHONPATH=src python tools/validate_content.py
```

そのPRで追加したsmoke testをすべて実行してください。

## 2. コンテンツ追加時チェック

- [ ] YAML idとファイル名が一致している
- [ ] imageが存在する
- [ ] 参照先カード/敵/レリック/ポーションが存在する
- [ ] ContentLoader warningが出ない
- [ ] Unlock対象ならUnlock Ruleがある
- [ ] Achievement対象ならAchievementがある
- [ ] Compendiumに表示される
- [ ] Reward poolに出る/出ないが意図通り
- [ ] smoke testを追加した

## 3. System追加時チェック

- [ ] 新規SystemがSceneに依存していない
- [ ] ContentRegistry依存に留めている
- [ ] RunState.flagsのdefaultを考慮した
- [ ] Save/Loadが必要ならserializer対応した
- [ ] CombatSnapshotが必要なら対応した
- [ ] smoke testを追加した

## 4. Scene追加時チェック

- [ ] GameAppにregisterした
- [ ] 戻るボタンがある
- [ ] payloadがJSON化可能
- [ ] autosave対象か確認した
- [ ] 画面サイズ1280x720で破綻しない
- [ ] Pygame event処理が既存Sceneと同じ形式

## 5. Save互換チェック

- [ ] 旧セーブで新フィールドがなくても落ちない
- [ ] default値が設定される
- [ ] RewardBundle / CombatSnapshot / Profileの変更点を確認した
- [ ] migrationが必要か判断した
- [ ] smoke_test_save_roundtrip系を実行した

## 6. Profile互換チェック

- [ ] ProfileState.ensure_defaults()に新フィールドを追加した
- [ ] serializerに追加した
- [ ] 旧profile.jsonで落ちない
- [ ] Unlock/Achievement/Notificationに影響しない

## 7. Balanceチェック

- [ ] 0コストカードが強すぎない
- [ ] 1コストAttackが基準から外れすぎない
- [ ] 防御カードが過剰でない
- [ ] レリックがスターターとして強すぎない
- [ ] ポーション生成が過剰でない
- [ ] Unlock条件が遠すぎない
- [ ] 高難度で理不尽にならない

## 8. リリース前チェック

- [ ] saves/が含まれていない
- [ ] __pycache__/が含まれていない
- [ ] .venv/が含まれていない
- [ ] 公式名・公式素材がない
- [ ] READMEが最新
- [ ] 主要smoke testが通る
- [ ] 起動確認済み
- [ ] 新規ラン開始確認済み
- [ ] セーブ/ロード確認済み
- [ ] 戦闘勝利/敗北確認済み
