import uuid
import time
from urllib.parse import urlparse, urlunparse

from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from apscheduler.schedulers.background import BackgroundScheduler
import yt_dlp

from config import (
    DOWNLOAD_DIR,
    EXPIRY_HOURS,
    BASE_URL,
    PORT,
    QUALITY_PRESETS,
    DEFAULT_QUALITY,
)

app = FastAPI()
video_store: dict[str, dict] = {}


def sanitize_url(raw_url: str) -> str:
    """Strip query/fragment tracking params while keeping base video URL."""
    parsed = urlparse(raw_url)
    if parsed.scheme and parsed.netloc:
        cleaned = parsed._replace(query="", fragment="")
        return urlunparse(cleaned)
    # Fallback for partial URLs
    return raw_url.split("?")[0].split("#")[0]


def cleanup_expired():
    now = time.time()
    expired = [
        vid
        for vid, data in video_store.items()
        if now - data["created"] > EXPIRY_HOURS * 3600
    ]
    for vid in expired:
        path = video_store[vid]["path"]
        if path.exists():
            path.unlink()
        del video_store[vid]
    if expired:
        print(f"Cleaned up {len(expired)} expired videos")


scheduler = BackgroundScheduler()
scheduler.add_job(cleanup_expired, "interval", minutes=15)
scheduler.start()


@app.on_event("shutdown")
def shutdown():
    scheduler.shutdown()


def build_quality_options() -> str:
    return "\n".join(
        f'<option value="{key}" {"selected" if key == DEFAULT_QUALITY else ""}>{key}</option>'
        for key in QUALITY_PRESETS
    )


@app.get("/", response_class=HTMLResponse)
async def index():
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>TikTok Downloader</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }}
            
            .wrapper {{
                display: flex;
                align-items: flex-start;
                justify-content: center;
                min-height: 100vh;
                padding: 40px 0;
            }}
            
            .container {{
                background: white;
                max-width: 600px;
                width: 100%;
                padding: 40px;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            }}
            
            h1 {{
                color: #333;
                margin-bottom: 10px;
                font-size: 28px;
                text-align: center;
            }}
            
            .subtitle {{
                text-align: center;
                color: #666;
                margin-bottom: 30px;
                font-size: 14px;
            }}
            
            label {{
                display: block;
                font-weight: 600;
                color: #333;
                margin-bottom: 8px;
                font-size: 14px;
            }}
            
            input[type="text"], select {{
                width: 100%;
                padding: 12px 16px;
                margin-bottom: 20px;
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                font-size: 15px;
                transition: all 0.3s ease;
                background: #f8f9fa;
            }}
            
            input[type="text"]:focus, select:focus {{
                outline: none;
                border-color: #667eea;
                background: white;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }}
            
            button {{
                width: 100%;
                padding: 14px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
            }}
            
            button:hover {{
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
            }}
            
            button:active {{
                transform: translateY(0);
            }}
            
            button:disabled {{
                opacity: 0.6;
                cursor: not-allowed;
                transform: none;
            }}
            
            #result {{
                margin-top: 30px;
            }}
            
            .loading {{
                text-align: center;
                color: #667eea;
                font-weight: 600;
                padding: 20px;
            }}
            
            .error {{
                background: #fee;
                color: #c33;
                padding: 15px;
                border-radius: 10px;
                border-left: 4px solid #c33;
            }}
            
            .result {{
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                padding: 25px;
                border-radius: 15px;
                border: 2px solid #e0e0e0;
            }}
            
            .result-header {{
                display: flex;
                align-items: center;
                gap: 10px;
                margin-bottom: 15px;
            }}
            
            .success-icon {{
                width: 24px;
                height: 24px;
                background: #10b981;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: bold;
            }}
            
            .result-header p {{
                color: #333;
                font-weight: 600;
                margin: 0;
            }}
            
            .link-container {{
                background: white;
                padding: 15px;
                border-radius: 10px;
                margin: 15px 0;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            }}
            
            .link-wrapper {{
                display: flex;
                flex-direction: column;
                align-items: stretch;
                gap: 10px;
                margin-bottom: 12px;
            }}
            
            .link-label {{
                font-size: 12px;
                font-weight: 600;
                color: #666;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            
            .link-input {{
                display: none;
            }}
            
            .link-text {{
                display: block;
                color: #667eea;
                text-decoration: none;
                font-weight: 600;
                margin-top: 8px;
                word-break: break-all;
                text-align: center;
            }}

            .link-text:hover {{
                text-decoration: underline;
            }}

            .copy-btn {{
                padding: 10px 20px;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-size: 14px;
                font-weight: 600;
                white-space: nowrap;
                transition: all 0.2s ease;
                box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
                flex-shrink: 0;
            }}
            
            .copy-btn:hover {{
                background: #5568d3;
                transform: scale(1.05);
            }}
            
            .copy-btn:active {{
                transform: scale(0.95);
            }}
            
            .copy-btn.copied {{
                background: #10b981;
            }}
            
            video {{
                width: 100%;
                max-width: 100%;
                border-radius: 10px;
                margin-top: 15px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
            }}
            
            .expiry-note {{
                font-size: 12px;
                color: #666;
                margin-top: 10px;
                text-align: center;
            }}
            
            @media (max-width: 640px) {{
                .container {{
                    padding: 30px 20px;
                }}
                
                h1 {{
                    font-size: 24px;
                }}
                
                .link-wrapper {{
                    flex-direction: column;
                    align-items: stretch;
                }}
                
                .link-input {{
                    width: 100%;
                }}
                
                .copy-btn {{
                    width: 100%;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="wrapper">
            <div class="container">
                <h1>🎵 TikTok Downloader</h1>
                <p class="subtitle">Download TikTok videos quickly and easily</p>
                
                <form id="form">
                    <label>TikTok URL</label>
                    <input type="text" name="url" placeholder="https://www.tiktok.com/@username/video/..." required>
                    
                    <button type="submit" id="submitBtn">Download Video</button>
                </form>
                
                <div id="result"></div>
            </div>
        </div>
        
        <script>
            async function copyToClipboard(text, btn) {{
                try {{
                    await navigator.clipboard.writeText(text);
                    const originalText = btn.textContent;
                    btn.textContent = 'Copied!';
                    btn.classList.add('copied');
                    setTimeout(() => {{
                        btn.textContent = originalText;
                        btn.classList.remove('copied');
                    }}, 2000);
                }} catch (err) {{
                    console.error('Failed to copy:', err);
                    alert('Failed to copy to clipboard');
                }}
            }}
            
            document.getElementById('form').onsubmit = async (e) => {{
                e.preventDefault();
                const result = document.getElementById('result');
                const submitBtn = document.getElementById('submitBtn');
                
                submitBtn.disabled = true;
                result.innerHTML = '<div class="loading">⏳ Downloading your video...</div>';
                
                const formData = new FormData(e.target);
                
                try {{
                    const res = await fetch('/download', {{ method: 'POST', body: formData }});
                    const data = await res.json();
                    
                    if (data.error) {{
                        result.innerHTML = `<div class="error">❌ ${{data.error}}</div>`;
                    }} else {{
                        result.innerHTML = `
                            <div class="result">
                                <div class="result-header">
                                    <div class="success-icon">✓</div>
                                    <p>Download ready</p>
                                </div>

                                <div class="link-container">
                                    <div class="link-label">Download Link</div>
                                    <div class="link-wrapper">
                                        <input type="text" class="link-input" value="${{data.url}}" readonly>
                                        <button class="copy-btn" onclick="copyToClipboard('${{data.url}}', this)">
                                            📋 Copy
                                        </button>
                                    </div>
                                    <a href="${{data.url}}" target="_blank" class="link-text">Open in new tab</a>
                                </div>
                                
                                <video src="${{data.url}}" controls></video>
                                
                                <p class="expiry-note">⏰ Link expires in {EXPIRY_HOURS} hours</p>
                            </div>
                        `;
                    }}
                }} catch (err) {{
                    result.innerHTML = `<div class="error">❌ Network error: ${{err.message}}</div>`;
                }} finally {{
                    submitBtn.disabled = false;
                }}
            }};
        </script>
    </body>
    </html>
    """


@app.post("/download")
async def download(url: str = Form(...)):
    clean_url = sanitize_url(url.strip())
    video_id = str(uuid.uuid4())
    output_path = DOWNLOAD_DIR / f"{video_id}.mp4"

    ydl_opts = {
        "outtmpl": str(output_path),
        "quiet": True,
        "no_warnings": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([clean_url])
    except Exception as e:
        return {"error": f"Download failed: {str(e)}"}

    if not output_path.exists():
        return {"error": "Download failed - no file created"}

    video_store[video_id] = {"path": output_path, "created": time.time()}

    return {
        "url": f"{BASE_URL}/video/{video_id}",
        "expires_in_hours": EXPIRY_HOURS,
    }


@app.get("/video/{video_id}")
async def serve_video(video_id: str):
    if video_id not in video_store:
        raise HTTPException(404, "Video not found or expired")

    path = video_store[video_id]["path"]
    if not path.exists():
        del video_store[video_id]
        raise HTTPException(404, "Video not found")

    return FileResponse(path, media_type="video/mp4")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=PORT)