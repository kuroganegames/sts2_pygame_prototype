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
