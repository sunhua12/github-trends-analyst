import json
import os
import argparse
import sys
import logging
import warnings

try:
    import google.generativeai as genai
    from google.generativeai import types
except ImportError:
    print("Error: 'google-generativeai' package not found.")
    print("Please install it using: pip install -U google-generativeai")
    sys.exit(1)

warnings.filterwarnings("ignore")
os.environ["PYTHONIOENCODING"] = "utf-8"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AIAnalyzer")

def get_model():
    # 依照要求強制使用 Gemini 2.5 Flash
    model_name = "models/gemini-2.5-flash"
    try:
        # 檢查模型是否可用
        return genai.GenerativeModel(model_name)
    except Exception as e:
        logger.warning(f"Could not initialize {model_name}: {e}. Falling back to 1.5-flash.")
        return genai.GenerativeModel("gemini-1.5-flash")

def analyze_everything(model, full_data):
    """將所有數據一次性發送給模型進行全方位分析"""
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
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        return json.loads(response.text)
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
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
            sys.exit("API Key not found.")
        genai.configure(api_key=api_key)
        model = get_model()
        
        logger.info("Generating comprehensive analysis in a single call with Gemini 2.5 Flash...")
        final_result = analyze_everything(model, full_data)
        
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(final_result, f, ensure_ascii=False, indent=2)
            
        logger.info(f"Success: Analysis completely generated.")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
