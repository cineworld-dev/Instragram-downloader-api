from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx
import re

app = FastAPI()

def is_instagram_reel_url(url: str) -> bool:
    return bool(re.match(r'https?://(www\.)?instagram\.com/reel/[a-zA-Z0-9_-]+/?', url))

@app.get("/")
async def download_reel(request: Request):
    url = request.query_params.get("url")
    if not url or not is_instagram_reel_url(url):
        return JSONResponse({"status": "error", "message": "❌ Invalid or missing Instagram Reel URL"})

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }

        async with httpx.AsyncClient(headers=headers, timeout=10) as client:
            res = await client.get(url)
            text = res.text

        # Regex pattern to extract the reel video URL from page source
        video_url_match = re.search(r'"video_url":"([^"]+)"', text)
        thumbnail_match = re.search(r'"thumbnail_url":"([^"]+)"', text)
        caption_match = re.search(r'"title":"([^"]+)"', text)

        if not video_url_match:
            return JSONResponse({"status": "error", "message": "⚠️ Could not extract video URL. Make sure the reel is public."})

        video_url = video_url_match.group(1).replace("\\u0026", "&")
        thumbnail = thumbnail_match.group(1).replace("\\u0026", "&") if thumbnail_match else None
        caption = caption_match.group(1) if caption_match else "Instagram Reel"

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
            "message": "❌ Failed to fetch the reel video.",
            "error": str(e)
        })
