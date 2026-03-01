import sys
import os
import pytest
import json
from unittest.mock import patch, MagicMock

# 加入 scripts 路徑
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))
from ai_analyzer import analyze_topic_chunk, analyze_global_summary

def test_analyze_topic_chunk_flow():
    mock_repos = [{"full_name": "user/repo", "description": "test"}]
    mock_model = MagicMock()
    mock_response = MagicMock()
    # 模擬 AI 回傳的結構化 JSON 字串
    mock_response.text = json.dumps({
        "topic_summary": "Summary content",
        "repo_insights": {
            "user/repo": {"insight": "Insight content", "sentiment": "Sentiment content"}
        }
    })
    mock_model.generate_content.return_value = mock_response
    
    result = analyze_topic_chunk(mock_model, "Python", mock_repos)
    
    assert result["topic_summary"] == "Summary content"
    assert "user/repo" in result["repo_insights"]
    assert result["repo_insights"]["user/repo"]["insight"] == "Insight content"

def test_analyze_global_summary_flow():
    mock_data = {"Python": []}
    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = json.dumps({
        "global_summary": "Global summary content"
    })
    mock_model.generate_content.return_value = mock_response
    
    result = analyze_global_summary(mock_model, mock_data)
    
    assert result["global_summary"] == "Global summary content"

def test_ai_analyzer_structure_compatibility():
    # 驗證必要函式是否存在於腳本中
    import ai_analyzer
    assert hasattr(ai_analyzer, 'analyze_topic_chunk')
    assert hasattr(ai_analyzer, 'analyze_global_summary')
    assert hasattr(ai_analyzer, 'get_model')
