# AI

シンプルな俳句ジェネレーターです。`python -m src.haiku_generator` を実行すると、ランダムな俳句を生成します。`--count` や `--seed` オプションで出力数やシード値を指定できます。

## 実行例

```bash
python -m src.haiku_generator --count 2 --seed 5
```

## テスト

```bash
pytest
```
