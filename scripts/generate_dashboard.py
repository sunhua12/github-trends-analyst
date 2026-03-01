import json
import os
from datetime import datetime
import argparse
import logging
from jinja2 import Template

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("DashboardGen")

def generate_html(multi_data, analysis_summary, template_path, output_path):
    logger.info(f"Generating dashboard to {output_path} using Jinja2...")
    
    with open(template_path, 'r', encoding='utf-8') as f:
        template_str = f.read()
    
    template = Template(template_str)
    
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
    parser = argparse.ArgumentParser(description="Professional Dashboard Generator")
    parser.add_argument("--input", required=True, help="Input combined JSON file")
    parser.add_argument("--analysis", help="AI summary text")
    parser.add_argument("--analysis_file", help="Path to file containing AI summary text")
    parser.add_argument("--template", required=True, help="HTML template path")
    parser.add_argument("--output", default="index.html", help="Output HTML path")
    
    args = parser.parse_args()
    
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 優先從檔案讀取分析內容，避免 Shell 編碼問題
        analysis_content = ""
        if args.analysis_file and os.path.exists(args.analysis_file):
            with open(args.analysis_file, 'r', encoding='utf-8') as f:
                analysis_content = f.read()
        else:
            analysis_content = args.analysis or "No analysis provided."
            
        generate_html(data, analysis_content, args.template, args.output)
    except Exception as e:
        logger.error(f"Failed to process data: {e}")
