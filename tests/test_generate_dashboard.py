import sys
import os
import pytest
import json
from unittest.mock import patch, mock_open, MagicMock

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
    
    # 模擬 Jinja2 模板
    mock_template = """
    <html>
        {{ TIMESTAMP }} {{ GLOBAL_ANALYSIS }}
        {% for topic, repos in TOPICS_DATA.items() %}
            <h1>{{ topic }} Trending</h1>
            <p>{{ TOPIC_SUMMARIES.get(topic) }}</p>
            {% for repo in repos %}
                <div>{{ repo.full_name }}: {{ repo.ai_insight }}</div>
            {% endfor %}
        {% endfor %}
    </html>
    """
    
    # 建立一個可以用來記錄所有 open() 回傳物件的 list
    file_handle_mocks = []

    def mock_file_open(path, mode='r', *args, **kwargs):
        content = ""
        if "template.html" in path:
            content = mock_template
        elif "analysis.json" in path:
            content = mock_analysis_json
        
        # 建立一個新的 mock_open 物件
        m = mock_open(read_data=content).return_value
        # 記錄這個物件，以便稍後檢查寫入行為
        file_handle_mocks.append(m)
        return m

    with patch("builtins.open", side_effect=mock_file_open):
        with patch("os.path.exists", return_value=True):
            output_path = "test_output.html"
            generate_html(mock_data, "analysis.json", "template.html", output_path)
            
            # 在 generate_html 中，最後一個被開啟的檔案應該是 index.html (寫入模式)
            # 我們搜尋所有 handle 的 write 紀錄
            written_content = ""
            for handle in file_handle_mocks:
                for call in handle.write.call_args_list:
                    arg = call[0][0]
                    if "<html>" in arg:
                        written_content = arg
                        break
            
            # 驗證內容
            assert "Python Trending" in written_content
            assert "AI Global Summary Test" in written_content
            assert "Python Trend Detail" in written_content
            assert "test/python-repo" in written_content
