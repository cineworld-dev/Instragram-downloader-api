import os
import shutil
import uuid
from fastapi import FastAPI, Query, HTTPException, Response
from fastapi.responses import FileResponse, JSONResponse
import yt_dlp

app = FastAPI()

DOWNLOAD_DIR = "./downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def extract_formats(url: str):
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
    formats = []
    for f in info.get("formats", []):
        if f.get("format_id") and f.get("url"):
            formats.append({
                "format_id": f["format_id"],
                "format_note": f.get("format_note", ""),
                "ext": f.get("ext", ""),
                "acodec": f.get("acodec"),
                "vcodec": f.get("vcodec"),
                "filesize": f.get("filesize") or f.get("filesize_approx"),
                "resolution": f.get("resolution") or f.get("height"),
                "url": f["url"],
            })
    return formats

@app.get("/formats")
async def get_formats(url: str = Query(..., description="Instagram reel URL")):
    try:
        formats = await run_blocking(extract_formats, url)
        if not formats:
            return JSONResponse({"status": "error", "message": "No formats found"})
        return {"status": "success", "formats": formats}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def download_video_file(url: str, format_id: str):
    unique_id = str(uuid.uuid4())
    outtmpl = os.path.join(DOWNLOAD_DIR, f"{unique_id}.%(ext)s")
    ydl_opts = {
        "format": format_id,
        "outtmpl": outtmpl,
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
    return filename

async def run_blocking(func, *args):
    import asyncio
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func, *args)

@app.get("/download")
async def download(
    url: str = Query(..., description="Instagram reel URL"),
    format_id: str = Query(..., description="Format ID to download"),
):
    try:
        filepath = await run_blocking(download_video_file, url, format_id)
        if not os.path.exists(filepath):
            raise HTTPException(status_code=500, detail="File not found after download")

        response = FileResponse(path=filepath, filename=os.path.basename(filepath), media_type="video/mp4")

        # Cleanup after response is sent
        async def cleanup():
            await asyncio.sleep(5)  # wait 5 seconds for the response to finish
            try:
                os.remove(filepath)
            except Exception:
                pass

        import asyncio
        asyncio.create_task(cleanup())

        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
