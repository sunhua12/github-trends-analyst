import json
import os
from datetime import datetime
import argparse
import logging
from jinja2 import Template

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("DashboardGen")

def generate_html(multi_data, analysis_summary, template_path, output_path):
    logger.info(f"Generating dashboard to {output_path} using Jinja2...")
    
    with open(template_path, 'r', encoding='utf-8') as f:
        template_str = f.read()
    
    # 建立 Jinja2 模板對象
    template = Template(template_str)
    
    # 準備渲染數據
    context = {
        "TIMESTAMP": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "ANALYSIS_SUMMARY": analysis_summary,
        "TOPICS_DATA": multi_data
    }
    
    try:
        html = template.render(context)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        logger.info("Dashboard generation successful.")
    except Exception as e:
        logger.error(f"Template rendering failed: {e}")
        return None
    
    return output_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Professional Dashboard Generator using Jinja2")
    parser.add_argument("--input", required=True, help="Input combined JSON file")
    parser.add_argument("--analysis", default="AI analysis in progress...", help="AI summary")
    parser.add_argument("--template", required=True, help="HTML template path")
    parser.add_argument("--output", default="index.html", help="Output HTML path")
    
    args = parser.parse_args()
    
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        generate_html(data, args.analysis, args.template, args.output)
    except Exception as e:
        logger.error(f"Failed to process input data: {e}")
