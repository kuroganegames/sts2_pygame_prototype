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
