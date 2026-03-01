import sys
import os
import pytest
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
    
    # 使用包含 Jinja2 語法的 Mock 模板
    mock_template = """
    <html>
        {{TIMESTAMP}} {{ANALYSIS_SUMMARY}}
        {% for topic, repos in TOPICS_DATA.items() %}
            <h1>{{ topic }} Trending</h1>
            {% for repo in repos %}
                <div>{{ repo.full_name }}</div>
            {% endfor %}
        {% endfor %}
    </html>
    """
    
    with patch("builtins.open", mock_open(read_data=mock_template)) as m:
        output_path = "test_output.html"
        result = generate_html(mock_data, "AI Summary Test", "template.html", output_path)
        
        # 取得渲染後寫入的內容
        written_content = m().write.call_args[0][0]
        
        # 驗證 Jinja2 是否正確渲染了循環內容
        assert "Python Trending" in written_content
        assert "test/python-repo" in written_content
        assert "AI Summary Test" in written_content
