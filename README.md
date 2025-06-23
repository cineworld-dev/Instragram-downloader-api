# Instagram Reel Downloader API

A simple Python Flask API to download Instagram reels in HD 720p quality, deployed on Vercel.

## Features

- Download Instagram reels in HD 720p quality
- RESTful API with JSON responses
- Support for both GET and POST requests
- Error handling and validation
- Health check endpoint
- Fast and free hosting on Vercel

## API Endpoints

### 1. Home / Documentation
```
GET /
```
Returns API documentation and usage information.

### 2. Download Instagram Reel
```
POST /download
Content-Type: application/json

{
  "url": "https://www.instagram.com/reel/your-reel-id/"
}
```

OR

```
GET /download?url=https://www.instagram.com/reel/your-reel-id/
```

### 3. Health Check
```
GET /health
```

## Response Format

### Success Response
```json
{
  "success": true,
  "title": "Reel Title",
  "duration": 30,
  "uploader": "username",
  "view_count": 1000,
  "like_count": 50,
  "thumbnail": "https://thumbnail-url.jpg",
  "download_url": "https://direct-download-url.mp4",
  "quality": "720p",
  "filesize": 5242880,
  "ext": "mp4",
  "created_by": "https://t.me/zerocreations"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error message",
  "created_by": "https://t.me/zerocreations"
}
```

## Deployment on Vercel

### Prerequisites
- Vercel account
- Vercel CLI installed

### Steps

1. **Clone/Create the project**
   ```bash
   mkdir instagram-reel-api
   cd instagram-reel-api
   ```

2. **Add the files**
   - `main.py` (main application file)
   - `requirements.txt` (Python dependencies)
   - `vercel.json` (Vercel configuration)
   - `README.md` (this file)

3. **Install Vercel CLI**
   ```bash
   npm i -g vercel
   ```

4. **Login to Vercel**
   ```bash
   vercel login
   ```

5. **Deploy**
   ```bash
   vercel --prod
   ```

## Usage Examples

### Using cURL

**POST Request:**
```bash
curl -X POST https://your-vercel-app.vercel.app/download \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.instagram.com/reel/your-reel-id/"}'
```

**GET Request:**
```bash
curl "https://your-vercel-app.vercel.app/download?url=https://www.instagram.com/reel/your-reel-id/"
```

### Using JavaScript

```javascript
// POST Request
const response = await fetch('https://your-vercel-app.vercel.app/download', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    url: 'https://www.instagram.com/reel/your-reel-id/'
  })
});

const data = await response.json();
console.log(data);

// GET Request
const response = await fetch('https://your-vercel-app.vercel.app/download?url=https://www.instagram.com/reel/your-reel-id/');
const data = await response.json();
console.log(data);
```

### Using Python

```python
import requests

# POST Request
url = "https://your-vercel-app.vercel.app/download"
payload = {"url": "https://www.instagram.com/reel/your-reel-id/"}
response = requests.post(url, json=payload)
print(response.json())

# GET Request
url = "https://your-vercel-app.vercel.app/download"
params = {"url": "https://www.instagram.com/reel/your-reel-id/"}
response = requests.get(url, params=params)
print(response.json())
```

## Features

- ✅ HD 720p quality downloads
- ✅ Fast response times
- ✅ Error handling
- ✅ JSON API responses
- ✅ Both GET and POST support
- ✅ Free hosting on Vercel
- ✅ No rate limits (within Vercel's limits)

## Notes

- Only supports Instagram reel URLs
- Maximum quality is 720p HD
- Files are not stored on the server
- Direct download URLs are provided in the response

## Support

For support and updates, join: https://t.me/zerocreations

## License

This project is for educational purposes. Please respect Instagram's terms of service.
