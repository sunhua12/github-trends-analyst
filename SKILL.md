---
name: github-trends
description: Analyze GitHub trending repositories and generate a visual dashboard. Use this skill when the user wants to know what's hot on GitHub, analyze technology trends, or create a trending report.
---

# GitHub Trends Analyst

This skill enables Gemini CLI to fetch, analyze, and visualize GitHub trending repositories. It provides a complete workflow from data collection to insight generation and dashboard creation.

## Capabilities

1.  **Fetch Trending Repos**: Retrieve trending repositories by language and timeframe (daily, weekly, monthly).
2.  **Trend Analysis**: Use AI to identify emerging patterns, popular technologies (e.g., AI/LLM, Web3, DevTools), and shifts in the developer ecosystem.
3.  **Visual Dashboard**: Generate a clean, modern HTML dashboard to present the findings.

## Workflow

To perform a complete analysis, follow these steps:

### 1. Data Collection
Use the `fetch_trends.py` script to get raw data in JSON format.
```bash
python scripts/fetch_trends.py --lang [language] --since [daily|weekly|monthly] --format json > trends.json
```

### 2. AI Analysis
Read the `trends.json` file and analyze the content. Look for:
- Common themes among the top repos.
- Sudden spikes in specific frameworks or libraries.
- Innovative use cases for existing technologies.

### 3. Dashboard Generation
Generate the final HTML report using `generate_dashboard.py`.
```bash
python scripts/generate_dashboard.py --input trends.json --analysis "[AI_ANALYSIS_TEXT]" --template assets/dashboard_template.html --output github_dashboard.html
```

## Resources

### scripts/
- `fetch_trends.py`: Scrapes GitHub Trending page. Supports `--lang`, `--since`, and `--format`.
- `generate_dashboard.py`: Combines JSON data and AI analysis into an HTML dashboard.

### assets/
- `dashboard_template.html`: A modern Vanilla CSS template for the dashboard.

## Examples

### User: "Analyze Python trends for this week"
1. Run `fetch_trends.py --lang python --since weekly --format json`.
2. Analyze the results (e.g., identifying a lot of agentic AI frameworks).
3. Run `generate_dashboard.py` with the analysis.
4. Provide the link to the generated `github_dashboard.html` to the user.
