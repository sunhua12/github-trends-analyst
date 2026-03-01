from google import genai
import json
import os
import argparse
import sys
import logging

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AIAnalyzer")

def analyze_trends(json_data, topic):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEY not found!")
        return "Error: GEMINI_API_KEY not found."

    try:
        # 使用新版 SDK 介面
        client = genai.Client(api_key=api_key)
        
        prompt = f"""
        你是一位資深的技術趨勢觀察家。請分析以下關於「{topic}」的 JSON 趨勢數據：
        
        {json_data}
        
        請提供結構化的繁體中文分析，包含本週主旋律、核心亮點與開發者啟示。
        """
        
        logger.info(f"Sending data to Gemini for {topic} analysis...")
        
        # 嘗試使用標準模型名稱
        # 注意：在某些區域或 SDK 版本中，可能需要改為 gemini-1.5-flash-latest
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        error_str = str(e)
        # 移除錯誤訊息中可能存在的 API Key 蹤跡
        error_msg = error_str.replace(api_key, "***") if api_key else error_str
        logger.error(f"AI Analysis failed: {error_msg}")
        
        # 針對 404 進行特殊處理
        if "404" in error_msg:
            return f"AI Analysis failed (404): 找不到模型 ID。這通常是因為 SDK 與模型名稱不匹配。請嘗試在 scripts/ai_analyzer.py 中將 model 修改為 'gemini-1.5-flash-latest'。"
            
        return f"AI Analysis failed: {error_msg}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Trend Analyzer using New Gemini SDK")
    parser.add_argument("--input", required=True, help="Input JSON file")
    parser.add_argument("--topic", default="Multi-Topic", help="The topic being analyzed")
    
    args = parser.parse_args()
    
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            data = f.read()
        
        analysis_result = analyze_trends(data, args.topic)
        print(analysis_result)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
