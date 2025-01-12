from fastapi import FastAPI
from api import game_router, auth_router, room_router
from core.config import settings
from core.mongodb import mongodb
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from pathlib import Path

app = FastAPI(title="Buzz API")

# Custom middleware for static files
class StaticFilesCORSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Handle preflight requests
        if request.method == "OPTIONS":
            headers = {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "*",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Max-Age": "86400",  # 24 hours
            }
            return Response(status_code=204, headers=headers)
            
        response = await call_next(request)
        if request.url.path.startswith("/static"):
            # Set CORS headers for static files
            response.headers.update({
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Expose-Headers": "Content-Length, Content-Range",
                "Cross-Origin-Resource-Policy": "cross-origin",
                "Cross-Origin-Opener-Policy": "same-origin",
                "Cache-Control": "public, max-age=3600"
            })
        return response

app.add_middleware(StaticFilesCORSMiddleware)

# General CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory
static_path = Path(__file__).parent / "static"
if not static_path.exists():
    static_path.mkdir(parents=True)

# Mount static files with headers
app.mount("/static", 
    StaticFiles(
        directory=str(static_path),
        check_dir=True,
        html=True,
    ), 
    name="static"
)

# Include routers
app.include_router(game_router, tags=["games"])
app.include_router(auth_router, tags=["auth"])
app.include_router(room_router, tags=["room"])

@app.on_event("startup")
async def startup_db_client():
    # Verify static directories exist
    static_path = Path(__file__).parent / "static"
    images_path = static_path / "images" / "spyfall_locations"
    images_path.mkdir(parents=True, exist_ok=True)
    print(f"📁 Static path exists: {static_path.exists()}")
    print(f"📁 Images path exists: {images_path.exists()}")
    print(f"📁 Images directory contents: {list(images_path.glob('*.webp'))}")
    await mongodb.connect_db()

@app.on_event("shutdown")
async def shutdown_db_client():
    await mongodb.close_db()
