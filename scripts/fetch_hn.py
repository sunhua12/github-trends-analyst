import httpx
import asyncio
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("HNFetcher")

async def fetch_item(client, item_id):
    url = f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json"
    try:
        resp = await client.get(url, timeout=10.0)
        return resp.json()
    except:
        return None

async def fetch_hn_top_stories(limit=15):
    logger.info("Fetching Hacker News Top Stories...")
    async with httpx.AsyncClient() as client:
        # 獲取 Top Stories IDs
        resp = await client.get("https://hacker-news.firebaseio.com/v0/topstories.json")
        ids = resp.json()[:limit]
        
        tasks = [fetch_item(client, i) for i in ids]
        items = await asyncio.gather(*tasks)
        
        stories = []
        for item in items:
            if item and 'title' in item:
                stories.append({
                    "title": item.get('title'),
                    "url": item.get('url', f"https://news.ycombinator.com/item?id={item['id']}"),
                    "score": item.get('score'),
                    "comments": item.get('descendants', 0)
                })
        return stories

if __name__ == "__main__":
    data = asyncio.run(fetch_hn_top_stories())
    print(json.dumps(data, indent=2))
