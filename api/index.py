from flask import Flask, request, jsonify
import requests
import re
import json
from urllib.parse import urlparse

app = Flask(__name__)

class InstagramDownloader:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
        }
    
    def extract_shortcode(self, url):
        """Extract shortcode from Instagram URL"""
        patterns = [
            r'/reel/([A-Za-z0-9_-]+)',
            r'/p/([A-Za-z0-9_-]+)',
            r'/tv/([A-Za-z0-9_-]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def get_media_info(self, shortcode):
        """Get media information using Instagram's GraphQL API"""
        try:
            # Instagram GraphQL endpoint
            graphql_url = "https://www.instagram.com/graphql/query/"
            
            # Query hash for media info (this may need to be updated periodically)
            query_hash = "9f8827793ef34641b2fb195d4d41151c"
            
            variables = {
                "shortcode": shortcode,
                "child_comment_count": 3,
                "fetch_comment_count": 40,
                "parent_comment_count": 24,
                "has_threaded_comments": True
            }
            
            params = {
                "query_hash": query_hash,
                "variables": json.dumps(variables)
            }
            
            response = requests.get(graphql_url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and 'shortcode_media' in data['data']:
                    return data['data']['shortcode_media']
            
            return None
            
        except Exception as e:
            print(f"GraphQL request failed: {str(e)}")
            return None
    
    def extract_from_page(self, url):
        """Fallback method to extract from page HTML"""
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            # Look for JSON data in script tags
            patterns = [
                r'window\._sharedData\s*=\s*({.+?});',
                r'window\.__additionalDataLoaded\(\'[^\']+\',\s*({.+?})\);',
                r'"graphql":\s*({.+?"shortcode_media".+?})'
            ]
            
            for pattern in patterns:
                matches = re.finditer(pattern, response.text, re.DOTALL)
                for match in matches:
                    try:
                        json_str = match.group(1)
                        data = json.loads(json_str)
                        
                        # Navigate through different JSON structures
                        media = self.find_media_in_json(data)
                        if media:
                            return media
                    except:
                        continue
            
            return None
            
        except Exception as e:
            print(f"Page extraction failed: {str(e)}")
            return None
    
    def find_media_in_json(self, data):
        """Recursively find media data in JSON"""
        if isinstance(data, dict):
            if 'is_video' in data and data.get('is_video'):
                return data
            elif 'shortcode_media' in data:
                return data['shortcode_media']
            elif 'entry_data' in data:
                entry_data = data['entry_data']
                if 'PostPage' in entry_data and entry_data['PostPage']:
                    return entry_data['PostPage'][0]['graphql']['shortcode_media']
            
            # Recursively search in nested objects
            for value in data.values():
                result = self.find_media_in_json(value)
                if result:
                    return result
        
        elif isinstance(data, list):
            for item in data:
                result = self.find_media_in_json(item)
                if result:
                    return result
        
        return None
    
    def get_best_quality_url(self, media_data):
        """Extract the best quality video URL"""
        video_url = media_data.get('video_url')
        
        # Try to get higher quality versions
        if 'video_versions' in media_data:
            versions = media_data['video_versions']
            # Sort by width to get highest quality
            versions.sort(key=lambda x: x.get('width', 0), reverse=True)
            if versions:
                video_url = versions[0]['url']
        
        return video_url

downloader = InstagramDownloader()

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "message": "Instagram Reel Downloader API v2.0",
        "status": "active",
        "endpoints": {
            "/": "GET - API information",
            "/download": "POST - Download Instagram reel/video",
            "/health": "GET - Health check"
        },
        "usage": {
            "method": "POST",
            "endpoint": "/download",
            "headers": {
                "Content-Type": "application/json"
            },
            "body": {
                "url": "https://www.instagram.com/reel/XXXXXXXXX/"
            }
        },
        "features": [
            "720p quality download",
            "Reel metadata extraction",
            "Thumbnail extraction",
            "Fast processing"
        ],
        "created_by": "ZeroCreations",
        "join": "https://t.me/zerocreations"
    })

@app.route('/download', methods=['POST'])
def download_reel():
    try:
        # Get request data
        if request.is_json:
            data = request.get_json()
        else:
            return jsonify({
                "error": "Content-Type must be application/json",
                "created_by": "ZeroCreations",
                "join": "https://t.me/zerocreations"
            }), 400
        
        if not data or 'url' not in data:
            return jsonify({
                "error": "URL parameter is required",
                "example": {
                    "url": "https://www.instagram.com/reel/XXXXXXXXX/"
                },
                "created_by": "ZeroCreations",
                "join": "https://t.me/zerocreations"
            }), 400
        
        url = data['url'].strip()
        
        # Validate Instagram URL
        if not any(domain in url.lower() for domain in ['instagram.com', 'instagr.am']):
            return jsonify({
                "error": "Invalid Instagram URL",
                "created_by": "ZeroCreations",
                "join": "https://t.me/zerocreations"
            }), 400
        
        # Extract shortcode
        shortcode = downloader.extract_shortcode(url)
        if not shortcode:
            return jsonify({
                "error": "Could not extract media ID from URL",
                "created_by": "ZeroCreations",
                "join": "https://t.me/zerocreations"
            }), 400
        
        # Try to get media info
        media_data = downloader.get_media_info(shortcode)
        
        # Fallback to page scraping
        if not media_data:
            media_data = downloader.extract_from_page(url)
        
        if not media_data:
            return jsonify({
                "error": "Could not extract media data. The post might be private or unavailable.",
                "created_by": "ZeroCreations",
                "join": "https://t.me/zerocreations"
            }), 404
        
        # Check if it's a video
        if not media_data.get('is_video', False):
            return jsonify({
                "error": "This post is not a video/reel",
                "created_by": "ZeroCreations",
                "join": "https://t.me/zerocreations"
            }), 400
        
        # Extract video information
        video_url = downloader.get_best_quality_url(media_data)
        
        if not video_url:
            return jsonify({
                "error": "Could not extract video download URL",
                "created_by": "ZeroCreations",
                "join": "https://t.me/zerocreations"
            }), 404
        
        # Extract additional metadata
        caption_edges = media_data.get('edge_media_to_caption', {}).get('edges', [])
        caption = caption_edges[0]['node']['text'] if caption_edges else ""
        
        owner = media_data.get('owner', {})
        username = owner.get('username', 'unknown')
        
        response_data = {
            "success": True,
            "data": {
                "download_url": video_url,
                "thumbnail_url": media_data.get('display_url', ''),
                "video_info": {
                    "duration": media_data.get('video_duration', 0),
                    "width": media_data.get('dimensions', {}).get('width', 0),
                    "height": media_data.get('dimensions', {}).get('height', 0),
                    "quality": "720p (best available)"
                },
                "metadata": {
                    "caption": caption,
                    "username": username,
                    "shortcode": shortcode,
                    "like_count": media_data.get('edge_media_preview_like', {}).get('count', 0),
                    "comment_count": media_data.get('edge_media_to_comment', {}).get('count', 0)
                }
            },
            "created_by": "ZeroCreations",
            "join": "https://t.me/zerocreations"
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({
            "error": f"Internal server error: {str(e)}",
            "created_by": "ZeroCreations",
            "join": "https://t.me/zerocreations"
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": "2025-06-23",
        "version": "2.0",
        "created_by": "ZeroCreations",
        "join": "https://t.me/zerocreations"
    })

# Vercel handler
def handler(environ, start_response):
    return app(environ, start_response)
