import logging
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("A2A_Server")

# --- 2. DEFINE MIDDLEWARE (The Transport Inspector) ---
class TrafficLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log the incoming connection details
        client_host = request.client.host if request.client else "Unknown"
        logger.info(f"👉 INCOMING: {request.method} {request.url.path} | From: {client_host}")
        
        # Process the request (pass it to A2A logic)
        response = await call_next(request)
        
        # Log the response details
        process_time = (time.time() - start_time) * 1000
        logger.info(f"👈 OUTGOING: Status {response.status_code} | Took {process_time:.2f}ms")
        
        return response