# 開発ワークフローとテスト

## 1. 基本セットアップ

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Windowsの場合:

```powershell
.venv\Scripts\activate
```

## 2. 基本確認コマンド

```bash
python -m compileall -q src main.py
PYTHONPATH=src python tools/validate_content.py
```

## 3. smoke test方針

このプロトタイプはpytestではなく、`tools/smoke_test_*.py` 形式の軽量テストを多数持つ方針です。

理由:

- GitHub PR本文にコマンドを列挙しやすい
- 個別システムの独立検証がしやすい
- Pygame UIを起動せずロジック確認できる
- YAMLコンテンツ読み込み確認に向く

## 4. 新規PRで必ずやること

1. 変更対象を小さく切る。
2. 新規Systemを追加したらsmoke testを追加する。
3. YAML schemaを増やしたらContentLoader validationを更新する。
4. Save/Load対象ならserializerを更新する。
5. READMEを必要最低限更新する。
6. PR本文に実装内容と確認コマンドを書く。
7. 既存セーブ互換の扱いを明記する。

## 5. 推奨PR粒度

良い例:

```text
PR15:
  PotionDropSystemだけ実装
  RewardSystem接続
  Save対応
  smoke test追加
```

悪い例:

```text
PotionDropSystem
+ Shop価格
+ Act2
+ 新キャラ
+ UI全面改修
```

1PRに複数の大きな関心事を混ぜないでください。

## 6. テストカテゴリ

### Content validation

```bash
PYTHONPATH=src python tools/validate_content.py
```

確認:

- YAML id
- 画像
- 参照先
- effect
- condition
- difficulty effect

### Logic smoke tests

例:

```bash
PYTHONPATH=src python tools/smoke_test_logic.py
PYTHONPATH=src python tools/smoke_test_actions.py
PYTHONPATH=src python tools/smoke_test_powers.py
```

### Save smoke tests

例:

```bash
PYTHONPATH=src python tools/smoke_test_save_roundtrip.py
PYTHONPATH=src python tools/smoke_test_combat_snapshot_roundtrip.py
PYTHONPATH=src python tools/smoke_test_save_slots.py
```

### Profile smoke tests

例:

```bash
PYTHONPATH=src python tools/smoke_test_profile_roundtrip.py
PYTHONPATH=src python tools/smoke_test_run_history.py
PYTHONPATH=src python tools/smoke_test_timeline_unlocks.py
```

### Reward smoke tests

例:

```bash
PYTHONPATH=src python tools/smoke_test_card_reward_rarity_odds.py
PYTHONPATH=src python tools/smoke_test_potion_drop_initial_odds.py
```

## 7. PR作成テンプレート

```markdown
## 概要

- 追加した機能
- 変更したシステム
- 追加したYAML
- 追加したテスト

## 仕様

実装仕様を箇条書き。

## 互換性

- 既存セーブへの影響
- 旧形式の読み込み
- migrationの有無

## 確認

```bash
python -m compileall -q src main.py
PYTHONPATH=src python tools/validate_content.py
...
```

## 補足

後続PRに回したもの。
```

## 8. セーブ互換の考え方

`RunState.flags` に新規値を追加する場合:

- 未設定時のdefaultを必ず持つ。
- serializer変更が不要ならflagsに入れる。
- Scene payloadに入るものはserializer対応する。
- 旧セーブで存在しないフィールドは空値またはdefaultで復元する。

## 9. UI変更時の注意

Pygame UIは自動テストしにくいので、UI変更では以下を意識します。

- ロジックはSystemへ寄せる。
- SceneはSystemの結果を描画するだけに近づける。
- ボタン押下時の状態変更を小さくする。
- payloadはJSON化できる形を保つ。
- 保存可能Sceneかどうか確認する。

## 10. コンテンツ追加時のテスト例

新カードを追加した場合:

```python
registry = ContentLoader(ROOT / "content").load()
assert not registry.warnings
assert "new_card" in registry.cards
```

新キャラを追加した場合:

```python
run = create_run(registry, "new_character", seed=123)
assert run.character_id == "new_character"
assert len(run.player.deck) > 0
```

Unlockを追加した場合:

```python
system = UnlockSystem(registry)
assert not system.is_unlocked(profile, "card", "new_card")
profile.summary["victories"] = 1
system.evaluate_unlocks(profile)
assert system.is_unlocked(profile, "card", "new_card")
```
