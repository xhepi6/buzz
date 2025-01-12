from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

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