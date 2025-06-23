from flask import Flask, request, jsonify
import yt_dlp
import os
import tempfile
import json
from urllib.parse import urlparse

app = Flask(__name__)

def is_valid_instagram_url(url):
    """Check if the URL is a valid Instagram URL"""
    parsed = urlparse(url)
    return parsed.netloc in ['www.instagram.com', 'instagram.com'] and '/reel/' in parsed.path

def get_instagram_video_info(url):
    """Extract video information from Instagram reel"""
    try:
        ydl_opts = {
            'format': 'best[height<=720]',  # Get best quality up to 720p
            'noplaylist': True,
            'extract_flat': False,
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Find the best format that's 720p or lower
            best_format = None
            for fmt in info.get('formats', []):
                if fmt.get('height') and fmt.get('height') <= 720:
                    if not best_format or fmt.get('height', 0) > best_format.get('height', 0):
                        best_format = fmt
            
            if not best_format:
                # Fallback to any available format
                best_format = info.get('formats', [{}])[-1] if info.get('formats') else {}
            
            return {
                'success': True,
                'title': info.get('title', 'Instagram Reel'),
                'duration': info.get('duration'),
                'uploader': info.get('uploader', 'Unknown'),
                'view_count': info.get('view_count'),
                'like_count': info.get('like_count'),
                'thumbnail': info.get('thumbnail'),
                'download_url': best_format.get('url'),
                'quality': f"{best_format.get('height', 'Unknown')}p",
                'filesize': best_format.get('filesize'),
                'ext': best_format.get('ext', 'mp4'),
                'created_by': "https://t.me/zerocreations"
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'created_by': "https://t.me/zerocreations"
        }

@app.route('/', methods=['GET'])
def home():
    """API documentation endpoint"""
    return jsonify({
        'message': 'Instagram Reel Downloader API',
        'version': '1.0.0',
        'endpoints': {
            'GET /': 'API documentation',
            'POST /download': 'Download Instagram reel',
            'GET /download': 'Download Instagram reel (with url parameter)'
        },
        'usage': {
            'POST': {
                'url': '/download',
                'method': 'POST',
                'body': {'url': 'https://www.instagram.com/reel/...'}
            },
            'GET': {
                'url': '/download?url=https://www.instagram.com/reel/...',
                'method': 'GET'
            }
        },
        'supported_platforms': ['Instagram Reels'],
        'max_quality': '720p HD',
        'created_by': 'https://t.me/zerocreations'
    })

@app.route('/download', methods=['POST', 'GET'])
def download_reel():
    """Download Instagram reel endpoint"""
    try:
        # Get URL from request
        if request.method == 'POST':
            data = request.get_json()
            if not data or 'url' not in data:
                return jsonify({
                    'success': False,
                    'error': 'URL is required in request body',
                    'created_by': 'https://t.me/zerocreations'
                }), 400
            url = data['url']
        else:  # GET request
            url = request.args.get('url')
            if not url:
                return jsonify({
                    'success': False,
                    'error': 'URL parameter is required',
                    'created_by': 'https://t.me/zerocreations'
                }), 400
        
        # Validate Instagram URL
        if not is_valid_instagram_url(url):
            return jsonify({
                'success': False,
                'error': 'Please provide a valid Instagram reel URL',
                'created_by': 'https://t.me/zerocreations'
            }), 400
        
        # Get video information
        result = get_instagram_video_info(url)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'An unexpected error occurred: {str(e)}',
            'created_by': 'https://t.me/zerocreations'
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Instagram Reel Downloader API is running',
        'created_by': 'https://t.me/zerocreations'
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'created_by': 'https://t.me/zerocreations'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'created_by': 'https://t.me/zerocreations'
    }), 500

if __name__ == '__main__':
    app.run(debug=True)
