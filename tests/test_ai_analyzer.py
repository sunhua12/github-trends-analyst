import sys
import os
import pytest
from unittest.mock import patch, MagicMock

# 加入 scripts 路徑
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))
from ai_analyzer import analyze_trends

def test_ai_analyzer_prompt_and_flow():
    mock_json = '{"test": "data"}'
    
    with patch('google.generativeai.GenerativeModel') as mock_model_class:
        # 模擬 API 回傳成功
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Mock AI Analysis Result"
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        # 模擬已設定 API KEY
        with patch.dict('os.environ', {'GEMINI_API_KEY': 'fake_key'}):
            result = analyze_trends(mock_json, "Python")
            assert result == "Mock AI Analysis Result"
            
            # 驗證 prompt 是否包含關鍵字
            args = mock_model.generate_content.call_args[0][0]
            assert "Python" in args
            assert mock_json in args

def test_ai_analyzer_no_key():
    # 測試沒有 API Key 時的回報
    with patch.dict('os.environ', {}, clear=True):
        result = analyze_trends('{}', "Any")
        assert "Error" in result
