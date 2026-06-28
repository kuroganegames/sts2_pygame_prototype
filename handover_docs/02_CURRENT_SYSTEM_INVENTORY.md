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
