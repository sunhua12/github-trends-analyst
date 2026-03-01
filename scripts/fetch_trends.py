import httpx
from bs4 import BeautifulSoup
import json
import argparse
import sys
import asyncio
import logging
import os
from typing import List, Optional, Dict
from pydantic import BaseModel, HttpUrl

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Fetcher")

class RepoModel(BaseModel):
    full_name: str
    url: HttpUrl
    description: str
    language: str
    total_stars: str
    stars_since: str
    status: str = "stable"  # "new", "up", "down", "stable"

async def fetch_trending_task(client: httpx.AsyncClient, lang_id: str, lang_name: str, since: str = 'daily') -> List[RepoModel]:
    url = "https://github.com/trending"
    if lang_id != "all":
        url += f"/{lang_id}"
    
    logger.info(f"Fetching {lang_name}...")
    try:
        response = await client.get(url, params={'since': since}, timeout=15.0)
        response.raise_for_status()
    except Exception as e:
        logger.error(f"Failed to fetch {lang_name}: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    repos = []
    for article in soup.find_all('article', class_='Box-row'):
        try:
            h2 = article.find('h2', class_='h3 lh-condensed')
            a = h2.find('a')
            full_name = a.get_text(strip=True).replace(' ', '')
            repo_url = f"https://github.com{a['href']}"
            p = article.find('p', class_=lambda x: x and 'color-fg-muted' in x and 'my-1' in x)
            description = p.get_text(strip=True) if p else "No description."
            lang_span = article.find('span', itemprop='programmingLanguage')
            language_val = lang_span.get_text(strip=True) if lang_span else "Unknown"
            stars_a = article.find('a', href=lambda x: x and '/stargazers' in x)
            total_stars = stars_a.get_text(strip=True) if stars_a else "0"
            since_span = article.find('span', class_='d-inline-block float-sm-right')
            stars_since = since_span.get_text(strip=True) if since_span else "0 stars"
            
            repos.append(RepoModel(
                full_name=full_name, url=repo_url, description=description,
                language=language_val, total_stars=total_stars, stars_since=stars_since
            ))
        except: continue
    return repos[:10]

def compare_with_history(current_data, last_data):
    for topic, repos in current_data.items():
        if topic not in last_data:
            for r in repos: r['status'] = 'new'
            continue
        
        last_repos = {r['full_name']: i for i, r in enumerate(last_data[topic])}
        for i, r in enumerate(repos):
            if r['full_name'] not in last_repos:
                r['status'] = 'new'
            else:
                last_idx = last_repos[r['full_name']]
                if i < last_idx: r['status'] = 'up'
                elif i > last_idx: r['status'] = 'down'
                else: r['status'] = 'stable'
    return current_data

async def main():
    # Load Config
    with open('config.json', 'r') as f: config = json.load(f)
    
    # Load History
    last_data = {}
    if os.path.exists('combined_trends.json'):
        try:
            with open('combined_trends.json', 'r') as f:
                content = f.read().strip()
                if content:
                    last_data = json.loads(content)
        except Exception as e:
            logger.warning(f"Could not load history from combined_trends.json: {e}. Starting fresh.")
    
    async with httpx.AsyncClient() as client:
        tasks = [fetch_trending_task(client, t['id'], t['name']) for t in config['topics']]
        results = await asyncio.gather(*tasks)
        
        current_data = {t['name']: [r.model_dump(mode='json') for r in res] 
                        for t, res in zip(config['topics'], results)}
        
        # Compare
        final_data = compare_with_history(current_data, last_data)
        
        # Save results (Save current to trends.json for display, combined to last for next run)
        with open('combined_trends.json', 'w') as f: json.dump(final_data, f, indent=2)
        print(json.dumps(final_data, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
