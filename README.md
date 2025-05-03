
# Webサイト自動 **E2E テスト生成・実行ツール v4**

v4 では **常駐 `workspace` コンテナ** を導入し、環境構築とテスト実行を分離しました。
`docker compose up -d workspace` でコンテナを立ち上げたまま、
YAML 生成・テスト生成・pytest 実行を `docker compose exec workspace ...` で
何度でも呼び出せます。

## クイックスタート
```bash
cp .env.sample .env && vi .env           # 0) 設定
docker compose build builder             # 1) ビルド
docker compose up -d workspace           #    起動

docker compose exec workspace python scripts/yaml_generator.py     # 2) YAML 生成
docker compose exec workspace python scripts/generate_tests.py     # 3) テスト生成
docker compose exec workspace bash scripts/run_tests.sh            # 4) テスト実行

docker compose down                      # 終了
```

### ワンショット実行
```bash
docker compose up --build runner
```
