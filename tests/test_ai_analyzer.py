import sys
import os
import pytest
from unittest.mock import patch, MagicMock

# 加入 scripts 路徑
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))
from ai_analyzer import analyze_trends

def test_ai_analyzer_prompt_and_flow():
    mock_json = '{"test": "data"}'
    
    # 注意：現在要 Mock google.genai.Client
    with patch('google.genai.Client') as mock_client_class:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Mock AI Analysis Result"
        
        # 模擬 client.models.generate_content 的回傳路徑
        mock_client.models.generate_content.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        with patch.dict('os.environ', {'GEMINI_API_KEY': 'fake_key'}):
            result = analyze_trends(mock_json, "Python")
            assert result == "Mock AI Analysis Result"
            
            # 驗證調用參數
            call_args = mock_client.models.generate_content.call_args
            assert "Python" in call_args.kwargs['contents']
            assert mock_json in call_args.kwargs['contents']

def test_ai_analyzer_no_key():
    with patch.dict('os.environ', {}, clear=True):
        result = analyze_trends('{}', "Any")
        assert "Error" in result
