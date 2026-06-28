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
