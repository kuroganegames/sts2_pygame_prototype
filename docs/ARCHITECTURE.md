# Architecture

このプロトタイプは、ロジック・描画・データ定義を分離しています。

```text
main.py
  -> GameApp
      -> ContentLoader
      -> SceneManager
          -> Title / CharacterSelect / Map / Combat / Reward / Rest / Event / Shop / Result
```

## 重要な分離

- `content/`: YAMLと画像。カード、敵、レリック、キャラ、マップ、イベントを定義します。
- `src/spirelike/models/`: Dataclass。ゲーム状態を保持します。
- `src/spirelike/systems/`: ルール処理。戦闘、効果実行、報酬、マップ生成、ショップ。
- `src/spirelike/scenes/`: Pygame画面。入力と画面遷移を担当します。
- `src/spirelike/ui/`: ボタン、カード表示、画像キャッシュ、テキスト描画。

## 今後の拡張ポイント

- `EffectExecutor`: 新しいカード効果タイプを追加します。
- `CombatSystem.fire_relic_event`: レリック、Power、Enchantments、Afflictionsのトリガー統合先です。
- `CardInstance.modifiers`: カード1枚ごとのenchantment / affliction保持先です。
- `MapGenerator`: YAMLのconstraintsをより厳密に反映する拡張先です。
