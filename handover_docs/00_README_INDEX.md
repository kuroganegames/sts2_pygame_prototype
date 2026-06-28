# STS2 Pygame Prototype 引継ぎ・開発ドキュメント一式

作成日: 2026-06-28  
対象リポジトリ: `kuroganegames/sts2_pygame_prototype`  
前提: PR16 `Ascension Fidelity Pass` までGitHub上でマージ済み

このドキュメント群は、PygameベースのSlay the Spire 2風ローグライクデッキビルダー・プロトタイプの開発引継ぎ、今後の開発計画、派生ゲーム開発時の参考資料をまとめたものです。

## 推奨読書順

1. `01_HANDOVER_SUMMARY.md`  
   現在の開発状況、完了済み領域、未完了領域、次の判断ポイント。

2. `02_CURRENT_SYSTEM_INVENTORY.md`  
   現在実装済みのゲームシステム棚卸し。

3. `03_ARCHITECTURE_GUIDE.md`  
   ディレクトリ構造、主要クラス、状態管理、RNG、セーブ、Scene構成。

4. `04_CONTENT_AUTHORING_GUIDE.md`  
   YAMLコンテンツ追加ルール。カード、敵、レリック、ポーション、エンシェント、イベント、Unlockなど。

5. `05_STS2_LIKE_GAME_DESIGN_SPEC.md`  
   このプロトタイプを用いてSTS2風ゲームを作るためのゲームデザイン仕様書。

6. `06_DEVELOPMENT_WORKFLOW_AND_TESTS.md`  
   開発手順、テスト方針、smoke test、PR作成ルール。

7. `07_ROADMAP_AND_BACKLOG.md`  
   今後の優先度付きロードマップ。PR17以降の候補を含む。

8. `08_DERIVATIVE_GAME_SYSTEM_REFERENCE.md`  
   このプロトタイプから派生ゲームシステムを作るときの設計リファレンス。

9. `09_RISK_AND_IP_NOTES.md`  
   STS2風ゲームとして開発する際の権利・仕様忠実度・運用上の注意。

10. `10_MAINTENANCE_CHECKLIST.md`  
    今後の保守、リリース、テスト、マージ時のチェックリスト。

## 現在の大まかな結論

基本システムの構築は、プロトタイプとしてはほぼ完了しています。  
今後は「基盤開発」よりも、以下のフェーズへ移行するのが妥当です。

- 仕様忠実度向上
- コンテンツ拡張
- バランス調整
- UI/UX改善
- 自動テストとセーブ互換性の強化
- 独自ゲーム化に向けた名称・素材・世界観の差し替え

## 重要な前提

このプロトタイプは、公式のSlay the Spire 2を再現・複製するためのものではなく、同ジャンルのゲームシステムを独自に実装するための土台です。  
商用化や公開を視野に入れる場合は、公式名称、公式画像、公式テキスト、公式カード名、公式キャラクター名を避け、独自名称・独自アート・独自バランスへ置き換えてください。
