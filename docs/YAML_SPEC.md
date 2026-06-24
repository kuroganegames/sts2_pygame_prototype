# YAML Spec 初期版

## 共通ルール

カード、敵、キャラクター、レリック、ポーション、エンシェント、イベントは、原則としてYAMLと画像を同名にします。

```text
example_card.yaml
example_card.png
```

YAML内の `id` もファイル名と一致させます。

```yaml
id: example_card
image: example_card.png
```

## Card

```yaml
schema_version: 1
id: strike
name: ストライク
image: strike.png
character: wanderer
type: attack
rarity: basic
cost: 1
target: enemy
description: 6ダメージを与える。
effects:
  - type: damage
    target: selected_enemy
    amount: 6
```

## Potion

```yaml
schema_version: 1
id: fire_potion
name: 火炎ポーション
image: fire_potion.png
rarity: common
usage: combat
target: enemy
description: 敵1体に20ダメージを与える。
effects:
  - type: damage
    target: selected_enemy
    amount: 20
```

`usage` は以下を想定します。

```text
combat : 戦闘中のみ
map    : 戦闘外のみ
any    : どちらでも使用可能
```

## Ancient

```yaml
schema_version: 1
id: old_smith
name: 古き鍛冶師
image: old_smith.png
act_pool: [1, 2, 3]
weight: 100
description: 灰まみれの鍛冶師が、まだ火の入った炉の前でうなずく。
choices:
  - id: battle_temper
    name: 戦火の焼入れ
    description: 各戦闘開始時、筋力を1得る。
    effects: []
    triggers:
      - event: combat_start
        effects:
          - type: apply_status
            target: self
            status: strength
            stacks: 1
```

`effects` は選択時に即時実行されます。`triggers` は `RunState.ancient_blessings` に保存され、戦闘中の `combat_start` や `turn_start` で発火します。

## Effect DSL 初期対応

```yaml
- type: damage
  target: selected_enemy
  amount: 6

- type: gain_block
  target: self
  amount: 5

- type: draw_cards
  amount: 2

- type: gain_energy
  amount: 1

- type: apply_status
  target: selected_enemy
  status: weak
  stacks: 2

- type: gain_potion
  potion: fire_potion

- type: gain_random_potion
  rarity_weights:
    common: 70
    uncommon: 25
    rare: 5

- type: upgrade_random_card
  filter:
    type: attack

- type: remove_random_card_from_deck
  filter:
    rarity: basic

- type: repeat
  times: 2
  effects:
    - type: damage
      target: selected_enemy
      amount: 4
```

## Map

`content/maps/act1.yaml` で、階層数、固定レイヤー、深度別ノード重み、接続数、エンカウントプールを管理します。

現時点の `MapGenerator` は以下に対応しています。

- `layers`
- `layout.min_nodes_per_layer`
- `layout.max_nodes_per_layer`
- `layout.start_nodes`
- `layout.boss_nodes`
- `edges.max_outgoing_per_node`
- `fixed_layers`
- `weights_by_depth`
- `encounter_pools`

`ancient` ノードタイプを重みに含めると、マップ上にもエンシェント選択ノードが出現します。
