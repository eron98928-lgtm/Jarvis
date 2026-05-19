from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
import uuid
import logging
from .security_config import security_settings
from .jarvis_defense import jarvis_defense
from .anti_recon import anti_recon

# Setup Audit Logger
audit_logger = logging.getLogger("audit")
audit_logger.setLevel(logging.INFO)
handler = logging.FileHandler(security_settings.AUDIT_LOG_PATH)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
audit_logger.addHandler(handler)

class SecurityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 1. Request ID Tracking
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # 2. Payload Size Limit
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > security_settings.MAX_CONTENT_LENGTH:
            raise HTTPException(status_code=413, detail="Payload too large")
            
        # 3. Audit Logging (Start)
        client_ip = request.client.host
        method = request.method
        url = str(request.url)
        
        start_time = time.time()
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # 4. Security Headers
            for header, value in security_settings.SECURITY_HEADERS.items():
                response.headers[header] = value
            
            response.headers["X-Request-ID"] = request_id
            
            # Audit Log (Success)
            audit_logger.info(
                f"ID:{request_id} | IP:{client_ip} | {method} {url} | Status:{response.status_code} | Time:{process_time:.4f}s"
            )
            
            return response
            
        except Exception as e:
            # Audit Log (Error)
            audit_logger.error(
                f"ID:{request_id} | IP:{client_ip} | {method} {url} | Error:{str(e)}"
            )
            raise e

class IPBlockingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if jarvis_defense.is_blocked(request.client.host):
            raise HTTPException(status_code=403, detail="Access denied")
        return await call_next(request)

class DefenseMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 1. Anti-Recon Check
        try:
            await anti_recon.check_request(request)
        except HTTPException as e:
            await anti_recon.add_timing_jitter()
            return Response(
                content=jarvis_defense.obfuscate_error(e),
                status_code=e.status_code
            )

        # 2. Global Error Obfuscation
        try:
            response = await call_next(request)
            # 3. Anti-Fingerprinting
            jarvis_defense.anti_fingerprinting_headers(response.headers)
            return response
        except Exception as e:
            await anti_recon.add_timing_jitter()
            return Response(
                content=jarvis_defense.obfuscate_error(e),
                status_code=500
            )
