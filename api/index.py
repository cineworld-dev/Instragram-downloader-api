from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
import yt_dlp
import json

app = FastAPI()

@app.get("/")
async def get_formats(url: str = Query(..., description="Instagram reel URL")):
    try:
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        content = {
            "status": "success",
            "title": info.get("title"),
            "formats": info.get("formats"),
        }

        pretty_content = json.dumps(content, indent=4, ensure_ascii=False)
        return JSONResponse(content=pretty_content, media_type="application/json")

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
