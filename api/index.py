from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx
import re
from bs4 import BeautifulSoup

app = FastAPI()

def is_instagram_url(url):
    return re.match(r'https?://(www\.)?instagram\.com/reel/[a-zA-Z0-9-_]+', url)

@app.get("/")
async def download_reel(request: Request):
    url = request.query_params.get("url")
    if not url or not is_instagram_url(url):
        return JSONResponse({
            "status": "error",
            "message": "❌ Invalid or missing Instagram Reel URL"
        })

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        async with httpx.AsyncClient(headers=headers, timeout=10) as client:
            res = await client.get(url)
            html = res.text

        soup = BeautifulSoup(html, "html.parser")
        video_tag = soup.find("meta", property="og:video")
        thumb_tag = soup.find("meta", property="og:image")
        title_tag = soup.find("meta", property="og:title")

        video_url = video_tag["content"] if video_tag else None
        thumbnail = thumb_tag["content"] if thumb_tag else None
        caption = title_tag["content"] if title_tag else "Instagram Reel"

        if not video_url:
            return JSONResponse({
                "status": "error",
                "message": "⚠️ Could not extract video. Make sure it's public."
            })

        return JSONResponse({
            "status": "success",
            "video_url": video_url,
            "thumbnail": thumbnail,
            "caption": caption,
            "message": "Made with ❤️ by Zero Creations - Join https://t.me/zerocreations"
        })

    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": "❌ Failed to fetch data.",
            "error": str(e)
        })
