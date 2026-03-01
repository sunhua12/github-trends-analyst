import google.generativeai as genai
import json
import os
import argparse
import sys
import logging
import warnings
import time

warnings.filterwarnings("ignore")
os.environ["PYTHONIOENCODING"] = "utf-8"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AIAnalyzer")

def get_model():
    model_name = "models/gemini-flash-latest"
    try:
        available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        if "models/gemini-flash-latest" in available: return genai.GenerativeModel("models/gemini-flash-latest")
        if "models/gemini-2.0-flash" in available: return genai.GenerativeModel("models/gemini-2.0-flash")
    except: pass
    return genai.GenerativeModel("gemini-1.5-flash")

def analyze_topic_chunk(model, topic_name, repos):
    """針對單一主題及其專案進行深度分析"""
    prompt = f"""
    你是一位極致專業的技術分析大師。請針對 GitHub 的「{topic_name}」領域數據進行深度解讀：
    
    {json.dumps(repos, ensure_ascii=False)}
    
    請以 JSON 格式回傳（繁體中文）：
    {{
      "topic_summary": "### 🚀 {topic_name} 本週趨勢深度掃描\\n\\n- **技術範式轉移**: ...\\n- **核心競爭力分析**: ...\\n- **開發者痛點緩解**: ...\\n- **生態整合動向**: ...\\n- **下週技術展望**: ...",
      "repo_insights": {{
        "Repo完整路徑": {{
          "insight": "- **核心痛點**: ...\\n- **技術亮點**: ...\\n- **適用場景**: ...",
          "sentiment": "- **熱度來源**: ...\\n- **社群焦點**: ...\\n- **未來展望**: ..."
        }}
      }}
    }}
    
    要求：
    1. 必須涵蓋該主題下提供的「每一個」Repo，嚴禁遺漏。
    2. 內容要極其詳實，具備專業洞察力。
    """
    
    try:
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        return json.loads(response.text)
    except Exception as e:
        logger.error(f"Topic {topic_name} analysis failed: {e}")
        return {"topic_summary": f"該主題分析生成失敗: {e}", "repo_insights": {}}

def analyze_global_summary(model, all_data):
    """針對全域進行總結"""
    topics = list(all_data.keys())
    prompt = f"""
    請針對以下多個技術領域的數據產出一份「全域技術趨勢總結」：
    領域清單：{topics}
    
    數據內容參考：{json.dumps(all_data, ensure_ascii=False)[:3000]} (部分截斷)
    
    要求以 JSON 格式回傳：
    {{
      "global_summary": "### 🧠 全域技術策略觀察\\n\\n- **核心發展動能**: ...\\n- **跨領域技術共鳴**: ...\\n- **開源生態重心偏移**: ...\\n- **全球開發者情緒總結**: ..."
    }}
    使用繁體中文，內容要深入，每點之間確保有足夠的分行。
    """
    try:
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        return json.loads(response.text)
    except:
        return {"global_summary": "無法生成全域總結。"}

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
        
        final_result = {
            "global_summary": "",
            "topic_summaries": {},
            "repo_insights": {}
        }
        
        # 1. 產生全域總結
        logger.info("Step 1/2: Generating Global Summary...")
        global_res = analyze_global_summary(model, full_data)
        final_result["global_summary"] = global_res.get("global_summary", "")
        
        # 2. 逐一產生主題分析 (確保 100% 覆蓋)
        logger.info(f"Step 2/2: Generating Topic-specific analysis for {len(full_data)} topics...")
        for topic_name, repos in full_data.items():
            logger.info(f"Processing Topic: {topic_name}")
            topic_res = analyze_topic_chunk(model, topic_name, repos)
            
            final_result["topic_summaries"][topic_name] = topic_res.get("topic_summary", "")
            final_result["repo_insights"].update(topic_res.get("repo_insights", {}))
            
            # 稍微停頓避免 429 錯誤
            time.sleep(2)
            
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(final_result, f, ensure_ascii=False, indent=2)
            
        logger.info(f"Success: Analysis completely generated for all topics.")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
