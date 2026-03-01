import sys
import os
import pytest
from unittest.mock import patch, MagicMock

# 將 scripts 路徑加入系統路徑以便匯入
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))
from fetch_trends import fetch_trending

def test_fetch_trending_parser():
    # 模擬 GitHub Trending 的 HTML 片段
    mock_html = """
    <article class="Box-row">
        <h2 class="h3 lh-condensed">
            <a href="/user/repo"> user / repo </a>
        </h2>
        <p class="color-fg-muted my-1">This is a test description.</p>
        <span itemprop="programmingLanguage">Python</span>
        <a href="/user/repo/stargazers">1,234</a>
        <span class="d-inline-block float-sm-right">100 stars today</span>
    </article>
    """
    
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = mock_html
        mock_get.return_value = mock_response
        
        results = fetch_trending(language='python')
        
        assert len(results) == 1
        assert results[0]['full_name'] == "user/repo"
        assert results[0]['description'] == "This is a test description."
        assert results[0]['language'] == "Python"
        assert "1,234" in results[0]['total_stars']
        assert "100 stars today" in results[0]['stars_since']

def test_fetch_trending_error_handling():
    with patch('requests.get') as mock_get:
        mock_get.side_effect = Exception("Connection Error")
        results = fetch_trending()
        assert results == []
