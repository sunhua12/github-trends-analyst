from google import genai
import json
import os
import argparse
import sys
import logging

# 強制設定 UTF-8 環境
os.environ["PYTHONIOENCODING"] = "utf-8"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AIAnalyzer")

def analyze_trends(json_data, topic):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "Error: GEMINI_API_KEY not found."

    try:
        client = genai.Client(api_key=api_key)
        
        prompt = f"""
        你是一位精通全球開源生態系統的資深技術分析師。請針對「{topic}」主題，深度分析以下 GitHub Trending 數據（JSON 格式）：
        
        {json_data}
        
        你的目標是產出一份詳細的「技術趨勢解讀報表」。請務必遵守以下規範：
        
        1. **語言與風格**：使用繁體中文、條列式呈現、語氣專業銳利。
        2. **內容結構要求**：
           - **【本週總論】**：概括核心發展方向。
           - **【重點專案深度解析】**：針對 3-5 個專案，說明專案目標與社群評價。
           - **【開發者行動指南】**：分析爆紅原因與建議學習方向。
        3. **長度要求**：字數建議在 500 字左右。
        """
        
        logger.info(f"Sending data to Gemini for intensive {topic} analysis...")
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        error_msg = str(e).replace(api_key, "***") if api_key else str(e)
        logger.error(f"AI Analysis failed: {error_msg}")
        return f"AI Analysis failed: {error_msg}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Professional AI Trend Analyzer")
    parser.add_argument("--input", required=True, help="Input JSON file")
    parser.add_argument("--topic", default="Multi-Topic", help="The topic being analyzed")
    parser.add_argument("--output", help="Output text file path")
    
    args = parser.parse_args()
    
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            data = f.read()
        
        analysis_result = analyze_trends(data, args.topic)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(analysis_result)
            logger.info(f"Analysis saved to {args.output}")
        else:
            # Fallback to stdout with explicit encoding
            sys.stdout.buffer.write(analysis_result.encode('utf-8'))
    except Exception as e:
        logger.error(f"Fatal error: {e}")
