# 保守・リリース・マージ用チェックリスト

## 1. マージ前チェック

```bash
python -m compileall -q src main.py
PYTHONPATH=src python tools/validate_content.py
```

そのPRで追加したsmoke testをすべて実行してください。

## 2. コンテンツ追加時チェック

- [ ] YAML idとファイル名が一致している
- [ ] imageが存在する
- [ ] 参照先カード/敵/レリック/ポーションが存在する
- [ ] ContentLoader warningが出ない
- [ ] Unlock対象ならUnlock Ruleがある
- [ ] Achievement対象ならAchievementがある
- [ ] Compendiumに表示される
- [ ] Reward poolに出る/出ないが意図通り
- [ ] smoke testを追加した

## 3. System追加時チェック

- [ ] 新規SystemがSceneに依存していない
- [ ] ContentRegistry依存に留めている
- [ ] RunState.flagsのdefaultを考慮した
- [ ] Save/Loadが必要ならserializer対応した
- [ ] CombatSnapshotが必要なら対応した
- [ ] smoke testを追加した

## 4. Scene追加時チェック

- [ ] GameAppにregisterした
- [ ] 戻るボタンがある
- [ ] payloadがJSON化可能
- [ ] autosave対象か確認した
- [ ] 画面サイズ1280x720で破綻しない
- [ ] Pygame event処理が既存Sceneと同じ形式

## 5. Save互換チェック

- [ ] 旧セーブで新フィールドがなくても落ちない
- [ ] default値が設定される
- [ ] RewardBundle / CombatSnapshot / Profileの変更点を確認した
- [ ] migrationが必要か判断した
- [ ] smoke_test_save_roundtrip系を実行した

## 6. Profile互換チェック

- [ ] ProfileState.ensure_defaults()に新フィールドを追加した
- [ ] serializerに追加した
- [ ] 旧profile.jsonで落ちない
- [ ] Unlock/Achievement/Notificationに影響しない

## 7. Balanceチェック

- [ ] 0コストカードが強すぎない
- [ ] 1コストAttackが基準から外れすぎない
- [ ] 防御カードが過剰でない
- [ ] レリックがスターターとして強すぎない
- [ ] ポーション生成が過剰でない
- [ ] Unlock条件が遠すぎない
- [ ] 高難度で理不尽にならない

## 8. リリース前チェック

- [ ] saves/が含まれていない
- [ ] __pycache__/が含まれていない
- [ ] .venv/が含まれていない
- [ ] 公式名・公式素材がない
- [ ] READMEが最新
- [ ] 主要smoke testが通る
- [ ] 起動確認済み
- [ ] 新規ラン開始確認済み
- [ ] セーブ/ロード確認済み
- [ ] 戦闘勝利/敗北確認済み
