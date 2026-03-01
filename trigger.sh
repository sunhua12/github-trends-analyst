#!/bin/bash

# 1. 定義路徑
VENV_PATH="../.venv/bin/python"
FETCH_SCRIPT="scripts/fetch_trends.py"
AI_ANALYZER="scripts/ai_analyzer.py"
DASHBOARD_SCRIPT="scripts/generate_dashboard.py"

echo "🚀 Starting Robust GitHub Trends Update..."

# 2. 異步抓取數據
echo "📡 Step 1: Fetching trending data in parallel..."
$VENV_PATH $FETCH_SCRIPT --langs all python rust go typescript --since daily > combined_trends.json

# 3. AI 綜合分析
AI_FILE="ai_summary.txt"
if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️ Warning: GEMINI_API_KEY is not set."
    echo "Manual multi-topic update at $(date)" > $AI_FILE
else
    echo "🧠 Step 2: Generating AI Tech Insights (Writing to $AI_FILE)..."
    # 使用 --output 參數確保 Python 內部直接處理 UTF-8 寫入
    $VENV_PATH $AI_ANALYZER --input combined_trends.json --topic "Overall, AI, Rust, Go, TS" --output $AI_FILE
fi

# 4. 生成儀表板
echo "🎨 Step 3: Generating Jinja2 Dashboard..."
# 使用 --analysis_file 傳遞路徑，徹底避開 Shell 傳參的編碼崩潰
$VENV_PATH $DASHBOARD_SCRIPT --input combined_trends.json --analysis_file $AI_FILE --template assets/dashboard_template.html --output index.html

# 清理暫存檔 (可選)
# rm $AI_FILE

echo "✅ Success! All components processed via robust file-based pipelines."
