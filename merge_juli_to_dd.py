name: Merge JULI to DD

# 每天自动跑 + 手动触发
on:
  workflow_dispatch:
  schedule:
    - cron: "0 3 * * *"  # UTC 时间每天 3:00（北京时间 11:00）

permissions:
  contents: write  # 允许提交文件

jobs:
  merge:
    runs-on: ubuntu-latest

    steps:
      # 1️⃣ 拉取仓库
      - name: 拉取仓库
        uses: actions/checkout@v4
        with:
          persist-credentials: true

      # 2️⃣ 安装 Python
      - name: 安装 Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      # 3️⃣ 安装依赖
      - name: 安装依赖
        run: pip install -r requirements.txt

      # 4️⃣ 运行合并脚本
      - name: 运行合并脚本
        run: python merge_juli_to_dd.py

      # 5️⃣ 提交 DD.m3u
      - name: 提交 DD.m3u
        run: |
          git config user.name "github-actions"
          git config user.email "github-actions@github.com"

          # 拉取远程更新并变基
          git pull --rebase origin main

          # 添加 DD.m3u
          git add DD.m3u

          # 提交更改（如果有）
          git diff --cached --exit-code || git commit -m "Generate DD.m3u (JULI → HK)"

          # 推送到远程仓库
          git push origin main
