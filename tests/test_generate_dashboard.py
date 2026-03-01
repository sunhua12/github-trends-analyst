import sys
import os
import pytest
import json
from unittest.mock import patch, mock_open

# 加入 scripts 路徑
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))
from generate_dashboard import generate_html

def test_generate_html_structure():
    # 模擬多主題數據
    mock_data = {
        "Python": [
            {
                "full_name": "test/python-repo",
                "url": "http://test.com",
                "description": "Python desc",
                "language": "Python",
                "total_stars": "100",
                "stars_since": "10 stars today",
                "status": "new"
            }
        ]
    }
    
    # 模擬結構化的 AI 分析 JSON 檔案內容
    mock_analysis_json = json.dumps({
        "global_summary": "AI Global Summary Test",
        "topic_summaries": {"Python": "Python Trend Detail"},
        "repo_insights": {
            "test/python-repo": {"insight": "Detailed Insight", "sentiment": "Great"}
        }
    })
    
    # 使用符合目前實作的 Jinja2 語法 Mock 模板
    mock_template = """
    <html>
        {{ TIMESTAMP }}
        {{ GLOBAL_ANALYSIS }}
        {% for topic, repos in TOPICS_DATA.items() %}
            <h1>{{ topic }} Trending</h1>
            <p>{{ TOPIC_SUMMARIES.get(topic) }}</p>
            {% for repo in repos %}
                <div>{{ repo.full_name }}: {{ repo.ai_insight }}</div>
            {% endfor %}
        {% endfor %}
    </html>
    """
    
    # 我們需要 Mock 兩個檔案讀取：1. 模板, 2. AI 分析 JSON
    # 使用 side_effect 來區分不同路徑的讀取
    def mock_file_open(path, *args, **kwargs):
        if "template.html" in path:
            return mock_open(read_data=mock_template).return_value
        if "analysis.json" in path:
            return mock_open(read_data=mock_analysis_json).return_value
        return mock_open().return_value

    with patch("builtins.open", side_effect=mock_file_open) as m:
        with patch("os.path.exists", return_value=True):
            output_path = "test_output.html"
            generate_html(mock_data, "analysis.json", "template.html", output_path)
            
            # 獲取最後一次寫入行為（即寫入 HTML 的動作）
            # 因為 side_effect 較複雜，我們直接找有寫入 HTML 內容的那次呼叫
            written_content = ""
            for call in m().write.call_args_list:
                if "<html>" in str(call):
                    written_content = call[0][0]
                    break
            
            # 如果上面沒抓到，嘗試更簡單的捕獲方式
            if not written_content:
                # 在 mock_open 的情境下，通常最後一次寫入就是目標
                written_content = m().write.call_args[0][0]

            # 驗證內容
            assert "Python Trending" in written_content
            assert "AI Global Summary Test" in written_content
            assert "Python Trend Detail" in written_content
            assert "test/python-repo" in written_content
