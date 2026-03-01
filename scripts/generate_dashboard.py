import json
import os
from datetime import datetime
import argparse
import logging
from jinja2 import Template

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("DashboardGen")

def generate_html(multi_data, analysis_json_path, template_path, output_path):
    analysis_content = {"global_summary": "", "repo_insights": {}, "topic_summaries": {}}
    if os.path.exists(analysis_json_path):
        try:
            with open(analysis_json_path, 'r', encoding='utf-8') as f:
                analysis_content = json.load(f)
        except: pass

    # 數據預處理：確保 topic_summaries 的值是字串而不是列表
    topic_summaries = analysis_content.get("topic_summaries", {})
    cleaned_summaries = {}
    for topic, summary in topic_summaries.items():
        if isinstance(summary, list):
            cleaned_summaries[topic] = "\n".join(summary)
        else:
            cleaned_summaries[topic] = str(summary)

    # 數據整合至 repo
    repo_insights = analysis_content.get("repo_insights", {})
    for topic, repos in multi_data.items():
        for repo in repos:
            repo_id = repo['full_name']
            insight_data = repo_insights.get(repo_id, {})
            # 確保 AI 內容也是字串
            repo['ai_insight'] = insight_data.get("insight", "分析生成中...")
            repo['ai_sentiment'] = insight_data.get("sentiment", "待評價")

    with open(template_path, 'r', encoding='utf-8') as f:
        template_str = f.read()
    
    template = Template(template_str)
    context = {
        "TIMESTAMP": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "GLOBAL_ANALYSIS": analysis_content.get("global_summary", ""),
        "TOPIC_SUMMARIES": cleaned_summaries,
        "TOPICS_DATA": multi_data
    }
    
    try:
        html = template.render(context)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        logger.info("Cleaned dashboard successfully generated.")
    except Exception as e:
        logger.error(f"Render failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--github_input", required=True)
    parser.add_argument("--analysis_file", required=True)
    parser.add_argument("--template", required=True)
    parser.add_argument("--output", default="index.html")
    args = parser.parse_args()
    
    try:
        with open(args.github_input, 'r', encoding='utf-8') as f: github_data = json.load(f)
        generate_html(github_data, args.analysis_file, args.template, args.output)
    except Exception as e:
        logger.error(f"Error: {e}")
