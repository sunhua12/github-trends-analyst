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
        
        # 結構化 Prompt
        prompt = f"""
        你是一位精通全球開源生態系統的資深技術分析師。請針對「{topic}」主題，深度分析以下 GitHub Trending 數據（JSON 格式）：
        
        {json_data}
        
        你的目標是產出一份詳細的「技術趨勢解讀報表」。請務必遵守以下規範：
        
        1. **語言與風格**：
           - 使用**繁體中文**。
           - 採用**條列式 (Bullet points)** 呈現，確保層次分明、易於閱讀。
           - 語氣要專業、具備洞察力且銳利。

        2. **內容結構要求**：
           - **【本週總論】**：用一段話概括該領域當前的核心發展方向與技術脈動。
           - **【重點專案深度解析】**：針對數據中前 3-5 個最具代表性的專案，分別說明：
             - **專案目標**：它具體在解決什麼技術痛點？提供了什麼核心功能？
             - **社群評價與反響**：根據星數成長動能與描述，分析開發者社群對其評價（例如：是否為突破性創新、是否解決了長久以來的易用性問題、或是具備極高的實作參考價值）。
           - **【開發者行動指南】**：分析這些專案為何在此時爆紅，並建議開發者下週應關注或學習哪些特定技術。

        3. **長度要求**：內容需詳實且豐富，字數建議在 500 字左右。
        """
        
        logger.info(f"Sending data to Gemini for intensive {topic} analysis...")
        
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        error_str = str(e)
        error_msg = error_str.replace(api_key, "***") if api_key else error_str
        logger.error(f"AI Analysis failed: {error_msg}")
        return f"AI Analysis failed: {error_msg}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Professional AI Trend Analyzer")
    parser.add_argument("--input", required=True, help="Input JSON file")
    parser.add_argument("--topic", default="Multi-Topic", help="The topic being analyzed")
    
    args = parser.parse_args()
    
    try:
        # 強制使用 utf-8 讀取檔案
        with open(args.input, 'r', encoding='utf-8') as f:
            data = f.read()
        
        analysis_result = analyze_trends(data, args.topic)
        
        # 針對環境修正輸出編碼
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
            
        print(analysis_result)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
