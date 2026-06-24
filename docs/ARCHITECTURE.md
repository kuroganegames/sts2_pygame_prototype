# Architecture

このプロトタイプは、ロジック・描画・データ定義を分離しています。

```text
main.py
  -> GameApp
      -> ContentLoader
      -> SceneManager
          -> Title / CharacterSelect / Ancient / Map / Combat / Reward / Rest / Event / Shop / Result
```

## 重要な分離

- `content/`: YAMLと画像。カード、敵、レリック、キャラ、ポーション、エンシェント、マップ、イベントを定義します。
- `src/spirelike/models/`: Dataclass。ゲーム状態を保持します。
- `src/spirelike/systems/`: ルール処理。戦闘、効果実行、報酬、マップ生成、ショップ、ポーション、エンシェント。
- `src/spirelike/scenes/`: Pygame画面。入力と画面遷移を担当します。
- `src/spirelike/ui/`: ボタン、カード表示、ポーション表示、画像キャッシュ、テキスト描画。

## ポーション

`PotionInstance` は `PlayerState.potions` にスロット順で保存します。ポーションの効果はカードと同じEffect DSLで記述し、戦闘中は `PotionSystem.use_in_combat()` から `EffectExecutor` へ渡します。

```text
Potion YAML
  -> PotionInstance
  -> PotionSystem
  -> EffectExecutor / RunEffectExecutor
```

## エンシェント

エンシェントは、即時Effectと永続Triggerを持てる特殊イベントです。ラン開始時に `AncientScene` が表示され、選んだ祝福は `RunState.ancient_blessings` に保存されます。

```text
Ancient YAML
  -> AncientScene
  -> AncientSystem.apply_choice()
  -> RunState.ancient_blessings
  -> CombatSystem.fire_trigger_event()
```

## 今後の拡張ポイント

- `EffectExecutor`: 新しいカード / ポーション / 祝福効果タイプを追加します。
- `CombatSystem.fire_trigger_event`: レリック、エンシェント、Power、Enchantments、Afflictionsのトリガー統合先です。
- `CardInstance.modifiers`: カード1枚ごとのenchantment / affliction保持先です。
- `PotionSystem`: 戦闘外ポーションUIやスロット拡張処理を追加できます。
- `MapGenerator`: YAMLのconstraintsをより厳密に反映する拡張先です。
