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
                "stars_since": "10 stars today"
            }
        ],
        "Rust": [
            {
                "full_name": "test/rust-repo",
                "url": "http://rust.com",
                "description": "Rust desc",
                "language": "Rust",
                "total_stars": "200",
                "stars_since": "20 stars today"
            }
        ]
    }
    
    # 模擬 HTML 模板
    mock_template = "<html>{{TIMESTAMP}} {{ANALYSIS_SUMMARY}} {{CONTENT_SECTIONS}}</html>"
    
    with patch("builtins.open", mock_open(read_data=mock_template)) as m:
        # 執行生成邏輯
        # 注意：我們不真的寫入檔案，只測試回傳值或行為
        output_path = "test_output.html"
        result = generate_html(mock_data, "AI Summary Test", "template.html", output_path)
        
        # 取得寫入的內容
        written_content = m().write.call_args[0][0]
        
        # 驗證關鍵內容是否存在
        assert "Python Trending" in written_content
        assert "Rust Trending" in written_content
        assert "test/python-repo" in written_content
        assert "test/rust-repo" in written_content
        assert "AI Summary Test" in written_content
