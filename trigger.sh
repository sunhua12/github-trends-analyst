#!/bin/bash

# 1. 定義路徑
VENV_PATH="../.venv/bin/python"
FETCH_GITHUB="scripts/fetch_trends.py"
AI_ANALYZER="scripts/ai_analyzer.py"
DASHBOARD_SCRIPT="scripts/generate_dashboard.py"

echo "🚀 Starting Intensive GitHub Tech Pulse Update..."

# 2. 抓取 GitHub 數據
echo "📡 Step 1: Fetching GitHub Trends in parallel..."
$VENV_PATH $FETCH_GITHUB --langs all python rust go typescript --since daily > combined_trends.json

# 3. AI 深度分析
AI_FILE="ai_summary.txt"
if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️ Warning: GEMINI_API_KEY is not set."
    echo '{"global_summary": "Manual update", "topic_summaries": {}, "repo_insights": {}}' > $AI_FILE
else
    echo "🧠 Step 2: Generating AI Intensive Tech Insights..."
    # 這裡的 ai_analyzer.py 已經優化為只分析 GitHub 數據
    $VENV_PATH $AI_ANALYZER --github combined_trends.json --output $AI_FILE
fi

# 4. 生成儀表板
echo "🎨 Step 3: Generating Integrated Dashboard..."
# 移除 --hn_input，因為 generate_dashboard.py 現在只專注於 GitHub 整合
$VENV_PATH $DASHBOARD_SCRIPT --github_input combined_trends.json --analysis_file $AI_FILE --template assets/dashboard_template.html --output index.html

echo "✅ Success! Your GitHub Tech Pulse is ready."
