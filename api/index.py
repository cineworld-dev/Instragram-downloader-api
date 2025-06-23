from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from playwright.async_api import async_playwright
import re
import asyncio

app = FastAPI()

def is_instagram_url(url: str) -> bool:
    pattern = r'https?://(www\.)?instagram\.com/reel/[a-zA-Z0-9-_]+/?'
    return re.match(pattern, url) is not None

@app.get("/")
async def reel_downloader(request: Request):
    url = request.query_params.get("url")
    if not url or not is_instagram_url(url):
        return JSONResponse({
            "status": "error",
            "message": "❌ Invalid or missing Instagram Reel URL"
        })

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
            await page.goto(url, wait_until="networkidle")
            # Wait for video tag or <meta property="og:video"> to appear
            video_url = None

            # First try: get video src from <video> element on page
            video_handle = await page.query_selector("video")
            if video_handle:
                video_url = await video_handle.get_attribute("src")

            # Second fallback: try meta tag og:video
            if not video_url:
                video_url = await page.eval_on_selector('meta[property="og:video"]', 'el => el.content').catch(lambda e: None)

            # Get thumbnail from og:image meta tag
            thumbnail = await page.eval_on_selector('meta[property="og:image"]', 'el => el.content').catch(lambda e: None)
            # Get caption/title from og:title
            caption = await page.eval_on_selector('meta[property="og:title"]', 'el => el.content').catch(lambda e: None)

            await browser.close()

        if not video_url:
            return JSONResponse({
                "status": "error",
                "message": "⚠️ Could not extract video URL. Make sure the reel is public."
            })

        return JSONResponse({
            "status": "success",
            "video_url": video_url,
            "thumbnail": thumbnail,
            "caption": caption or "Instagram Reel",
            "message": "Made with ❤️ by Zero Creations - Join https://t.me/zerocreations"
        })

    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": "❌ Failed to fetch the reel video.",
            "error": str(e)
        })
