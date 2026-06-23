# YAML Spec 初期版

## 共通ルール

カード、敵、キャラクター、レリック、イベントは、原則としてYAMLと画像を同名にします。

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
upgrade:
  name: ストライク+
  description: 9ダメージを与える。
  effects:
    - type: damage
      target: selected_enemy
      amount: 9
```

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

- type: repeat
  times: 2
  effects:
    - type: damage
      target: selected_enemy
      amount: 4

- type: if
  condition:
    type: target_has_status
    target: selected_enemy
    status: weak
    stacks_at_least: 1
  then:
    - type: draw_cards
      amount: 1
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

`constraints` はYAML上に用意済みですが、初期実装では一部未反映です。
