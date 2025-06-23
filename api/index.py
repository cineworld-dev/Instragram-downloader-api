from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx
import re

app = FastAPI()

def is_valid_instagram_reel_url(url: str) -> bool:
    pattern = r'https?://(www\.)?instagram\.com/reel/[a-zA-Z0-9_-]+/?'
    return bool(re.match(pattern, url))

@app.get("/")
async def instagram_reel_downloader(request: Request):
    url = request.query_params.get("url")
    if not url or not is_valid_instagram_reel_url(url):
        return JSONResponse({
            "status": "error",
            "message": "❌ Invalid or missing Instagram Reel URL."
        })

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    try:
        async with httpx.AsyncClient(headers=headers, timeout=10) as client:
            response = await client.get(url)
            page_content = response.text

        # Extract video URL with regex
        video_url_match = re.search(r'"video_url":"([^"]+)"', page_content)
        thumbnail_match = re.search(r'"thumbnail_url":"([^"]+)"', page_content)
        caption_match = re.search(r'"title":"([^"]+)"', page_content)

        if not video_url_match:
            return JSONResponse({
                "status": "error",
                "message": "⚠️ Could not extract video URL. Make sure the reel is public."
            })

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
            "message": "❌ Failed to fetch reel video.",
            "error": str(e)
        })
