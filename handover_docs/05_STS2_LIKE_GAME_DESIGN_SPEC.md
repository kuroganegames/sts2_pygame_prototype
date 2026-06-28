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
