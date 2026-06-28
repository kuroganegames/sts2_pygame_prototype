# STS2 Pygame Prototype

Pygameで作った、Slay the Spire 2風のシングルプレイ・ローグライクデッキビルダー初期実装です。

公式素材や公式カード名は含めていません。カード、敵、キャラクター、レリック、ポーション、エンシェント、カード修飾、Run Modifier、Difficulty、Unlock、Achievement、Timeline、イベント、マップ生成ルールをYAMLで管理するためのプロトタイプです。

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
- 保存スロット選択による新規ラン開始 / 続きから
- 新規ラン開始前のRun Setup
- 数値または文字列によるシード指定
- カスタムRun Modifier選択
- Unlock条件に応じたRun Modifier選択制御
- キャラクター選択時のDifficulty Level選択
- キャラクター別Difficulty進行 / 勝利時の次段階解放
- Unlock YAMLによるコンテンツ解放制御
- Unlock Tree画面での解放条件 / 進捗表示
- Achievement YAMLによる実績解除
- Difficulty / Timeline / Unlock / Achievementの通知保存
- RunResultでの新規解放表示
- 小規模Content Pack 01
  - 追加カード
  - 追加レリック
  - 追加ポーション
  - 追加Run Modifier
- Character Pack 01: 錬金術師
  - 新プレイアブルキャラクター
  - 専用スターターデッキ
  - 専用スターターレリック
  - 毒 / 試薬 / ポーション生成寄りの専用カード
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
- 複数セーブスロットによる並行ラン管理
- 戦闘中の安定状態での「保存して終了」/ CombatSnapshot再開
- profile.jsonによるラン履歴 / 敵図鑑 / コレクション / Timeline / Unlock / Achievement / 通知記録
- ポーションの獲得、購入、戦闘中使用
- 敵Intentと簡易AI
- 戦闘報酬、カード追加、レリック獲得、ポーション獲得
- 休憩所で回復またはカード強化
- イベントYAMLの選択肢実行
- 簡易ショップ

## セーブファイル

```text
saves/
  slots/
    slot_001.json
    slot_002.json
    slot_003.json
  profile.json
```

旧形式の `saves/save_001.json` がある場合は、初回のスロット一覧取得時に `saves/slots/slot_001.json` へ移行し、旧ファイルは `saves/save_001.migrated.bak` として残します。

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

Timeline断片は `content/timeline/*.yaml`、Run Modifierは `content/run_modifiers/*.yaml`、Difficulty Levelは `content/difficulty_levels/*.yaml`、Unlock Ruleは `content/unlocks/*.yaml`、Achievementは `content/achievements/*.yaml` で管理します。

## 主なフォルダ

```text
src/spirelike/
  app/        Pygameアプリ本体、SceneManager
  content/    YAMLローダー、ContentRegistry
  core/       RunState、CombatState、RNG、ラン生成
  models/     Dataclass群
  profile/    profile.json、ラン履歴、図鑑、Timeline、Unlock、Achievement、通知状態
  save/       JSONセーブ / ロード / 複数スロット / CombatSnapshot
  scenes/     画面
  systems/    戦闘、効果実行、報酬、マップ生成、ショップ、Unlock、Achievement、通知など
  ui/         ボタン、カード表示、ポーション表示、テキスト描画

content/
  characters/
  cards/
  enemies/
  relics/
  potions/
  ancients/
  card_modifiers/
  run_modifiers/
  difficulty_levels/
  unlocks/
  achievements/
  timeline/
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

ポーション生成系の効果も使用できます。

```yaml
effects:
  - type: gain_random_potion
  - type: gain_potion
    potion: fire_potion
```

## 注意

初期プロトタイプなので、UI演出・音・ActionQueue途中状態の保存・カード選択Overlay中の保存などはまだ簡易または未対応です。
ただし、コード構造は今後の拡張を前提に分離しています。
