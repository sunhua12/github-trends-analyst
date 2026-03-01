#!/bin/bash

# 1. 定義路徑
VENV_PATH="../.venv/bin/python"
FETCH_SCRIPT="scripts/fetch_trends.py"
AI_ANALYZER="scripts/ai_analyzer.py"
DASHBOARD_SCRIPT="scripts/generate_dashboard.py"

echo "🚀 Starting Modernized Multi-Topic GitHub Trends Update..."

# 2. 一次性異步抓取所有主題 (Async & Parallel)
echo "📡 Fetching all topics in parallel..."
$VENV_PATH $FETCH_SCRIPT --langs all python rust --since daily > combined_trends.json

# 3. AI 綜合分析
if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️ Warning: GEMINI_API_KEY is not set."
    AI_SUMMARY="Manual multi-topic update at $(date)"
else
    echo "🧠 Generating AI Tech Insights..."
    # 將分析結果存入暫存檔以避開 Shell 編碼問題
    $VENV_PATH $AI_ANALYZER --input combined_trends.json --topic "Overall, AI/Python, Rust" --output ai_summary.txt
    AI_SUMMARY=$(cat ai_summary.txt)
    rm ai_summary.txt
fi

# 4. 生成多區塊儀表板 (Jinja2)
echo "🎨 Generating Jinja2 Dashboard..."
$VENV_PATH $DASHBOARD_SCRIPT --input combined_trends.json --analysis "$AI_SUMMARY" --template assets/dashboard_template.html --output index.html

echo "✅ Success! Dashboard is ready."
