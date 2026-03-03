import sys
import os
import pytest
import json
from unittest.mock import patch, MagicMock

# 加入 scripts 路徑
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))
import ai_analyzer

def test_analyze_everything_flow():
    mock_data = {
        "Python": [{"full_name": "user/repo", "description": "test"}]
    }
    mock_client = MagicMock()
    mock_response = MagicMock()
    
    # 模擬 AI 回傳的結構化 JSON 字串
    mock_response.text = json.dumps({
        "global_summary": "Global content",
        "topic_summaries": {
            "Python": "Python summary"
        },
        "repo_insights": {
            "user/repo": {"insight": "Insight content", "sentiment": "Sentiment content"}
        }
    })
    
    # 模擬新版 SDK 的呼叫鏈: client.models.generate_content(...)
    mock_client.models.generate_content.return_value = mock_response
    
    result = ai_analyzer.analyze_everything(mock_client, "gemini-2.0-flash", mock_data)
    
    assert result["global_summary"] == "Global content"
    assert result["topic_summaries"]["Python"] == "Python summary"
    assert "user/repo" in result["repo_insights"]
    assert result["repo_insights"]["user/repo"]["insight"] == "Insight content"

def test_ai_analyzer_structure_compatibility():
    # 驗證必要函式是否存在於新腳本中
    assert hasattr(ai_analyzer, 'analyze_everything')
    # 舊的 chunk 分析應該已被移除
    assert not hasattr(ai_analyzer, 'analyze_topic_chunk')
