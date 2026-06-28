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
