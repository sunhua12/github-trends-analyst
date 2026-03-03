import json
import os
import argparse
import sys
import logging
import warnings

# 嘗試導入新版 SDK
try:
    from google import genai
    from google.genai import types
except ImportError:
    print("Error: 'google-genai' package not found.")
    print("Please install it using: pip install -U google-genai")
    sys.exit(1)

warnings.filterwarnings("ignore")
os.environ["PYTHONIOENCODING"] = "utf-8"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AIAnalyzer")

def analyze_everything(client, model_id, full_data):
    """使用新版 SDK 進行單次全方位分析"""
    prompt = f"""
    你是一位極致專業的技術分析大師。請針對以下 GitHub 趨勢數據進行全方位的深度解讀：
    
    {json.dumps(full_data, ensure_ascii=False)}
    
    請以 JSON 格式回傳（繁體中文），包含以下結構：
    {{
      "global_summary": "### 🧠 全域技術策略觀察\\n\\n- **核心發展動能**: ...\\n- **跨領域技術共鳴**: ...\\n- **開源生態重心偏移**: ...\\n- **全球開發者情緒總結**: ...",
      "topic_summaries": {{
        "主題名稱": "### 🚀 主題名稱 本週趨勢深度掃描\\n\\n- **技術範式轉移**: ...\\n- **核心競爭力分析**: ...\\n- **開發者痛點緩解**: ...\\n- **生態整合動向**: ...\\n- **下週技術展望**: ..."
      }},
      "repo_insights": {{
        "Repo完整路徑": {{
          "insight": "- **核心痛點**: ...\\n- **技術亮點**: ...\\n- **適用場景**: ...",
          "sentiment": "- **熱度來源**: ...\\n- **社群焦點**: ...\\n- **未來展望**: ..."
        }}
      }}
    }}
    
    要求：
    1. 必須針對每個主題產生總結，並涵蓋提供的「每一個」Repo，嚴禁遺漏。
    2. 內容要極其詳實，具備專業洞察力，使用繁體中文。
    3. 每點之間確保有足夠的分行，以利視覺化呈現。
    """
    
    try:
        # 使用新版 SDK 的 generate_content
        response = client.models.generate_content(
            model=model_id,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        return json.loads(response.text)
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        # 如果是模型 ID 錯誤（例如 2.5 還沒開放），嘗試自動降級
        if "not found" in str(e).lower() and model_id != "gemini-2.0-flash":
            logger.warning(f"Model {model_id} not found, falling back to gemini-2.0-flash...")
            return analyze_everything(client, "gemini-2.0-flash", full_data)
            
        return {
            "global_summary": f"分析生成失敗: {e}",
            "topic_summaries": {},
            "repo_insights": {}
        }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--github", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    
    try:
        with open(args.github, 'r', encoding='utf-8') as f:
            full_data = json.load(f)
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            sys.exit("API Key not found in environment variables.")
            
        # 初始化新版 Client
        client = genai.Client(api_key=api_key)
        
        # 依照要求使用 Gemini 2.5 Flash (若環境不支援會自動降級至 2.0)
        target_model = "gemini-2.5-flash"
        
        logger.info(f"Generating comprehensive analysis in a single call with {target_model}...")
        final_result = analyze_everything(client, target_model, full_data)
        
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(final_result, f, ensure_ascii=False, indent=2)
            
        logger.info(f"Success: Analysis completely generated using new google-genai SDK.")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
