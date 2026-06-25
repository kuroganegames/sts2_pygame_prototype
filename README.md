# STS2 Pygame Prototype

Pygameで作った、Slay the Spire 2風のシングルプレイ・ローグライクデッキビルダー初期実装です。

公式素材や公式カード名は含めていません。カード、敵、キャラクター、レリック、ポーション、エンシェント、カード修飾、イベント、マップ生成ルールをYAMLで管理するためのプロトタイプです。

## 起動方法

```bash
cd sts2_pygame_prototype
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
python main.py
```

## 現在できること

- タイトル画面
- キャラクター選択
- ラン開始時のエンシェント祝福選択
- YAMLからコンテンツ読み込み
- YAMLからマップランダム生成
- マップノード選択
- 通常戦闘 / エリート / ボス戦闘
- カード使用、ダメージ、ブロック、ドロー、状態付与
- ActionQueueによる戦闘効果解決
- Powerカード / Exhaust / Retain / Ethereal / Innate / Unplayable
- Enchantment / Affliction によるカード1枚単位の修飾
- 安全地点でのオートセーブ / タイトルからのラン再開
- ポーションの獲得、購入、戦闘中使用
- 敵Intentと簡易AI
- 戦闘報酬、カード追加、レリック獲得、ポーション獲得
- 休憩所で回復またはカード強化
- イベントYAMLの選択肢実行
- 簡易ショップ

## データ追加ルール

原則として、カード・敵・キャラ・レリック・ポーション・エンシェント・カード修飾・イベントは `id` と同じファイル名にします。

例：

```text
content/card_modifiers/enchantments/sharp.yaml
content/card_modifiers/enchantments/sharp.png
```

YAML内にも同じIDを書きます。

```yaml
id: sharp
image: sharp.png
```

## 主なフォルダ

```text
src/spirelike/
  app/        Pygameアプリ本体、SceneManager
  content/    YAMLローダー、ContentRegistry
  core/       RunState、CombatState、RNG、ラン生成
  models/     Dataclass群
  save/       JSONセーブ / ロード
  scenes/     画面
  systems/    戦闘、効果実行、報酬、マップ生成、ショップなど
  ui/         ボタン、カード表示、ポーション表示、テキスト描画

content/
  characters/
  cards/
  enemies/
  relics/
  potions/
  ancients/
  card_modifiers/
  statuses/
  maps/
  events/
```

## YAML効果DSLの例

```yaml
effects:
  - type: damage
    target: selected_enemy
    amount: 6
  - type: gain_block
    target: self
    amount: 5
  - type: apply_card_modifier
    modifier: sharp
    selector:
      zones:
        - master_deck
      count: 1
      player_choice: true
```

## 注意

初期プロトタイプなので、UI演出・音・戦闘中の保存/ロード・詳細なカード選択UIなどはまだ簡易実装です。
ただし、コード構造は今後の拡張を前提に分離しています。
