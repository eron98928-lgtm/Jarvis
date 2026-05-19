import random
import asyncio
from fastapi import Request, HTTPException
from .jarvis_defense import jarvis_defense

class AntiRecon:
    def __init__(self):
        # List of common paths scanners look for
        self.honeypot_paths = [
            "/.env", "/.git", "/wp-admin", "/admin", "/phpmyadmin", 
            "/config", "/backup", "/v1/debug", "/api/v1/users"
        ]
        
    async def check_request(self, request: Request):
        path = request.url.path
        ip = request.client.host
        
        # 1. Honeypot Detection
        if path in self.honeypot_paths:
            jarvis_defense.log_intrusion_attempt(ip, f"Honeypot access: {path}")
            # Add a random delay to slow down the scanner
            await asyncio.sleep(random.uniform(2.0, 5.0))
            raise HTTPException(status_code=404, detail="Not Found")

        # 2. Suspicious Headers
        user_agent = request.headers.get("user-agent", "").lower()
        scanners = ["nmap", "nikto", "sqlmap", "burp", "dirbuster"]
        for scanner in scanners:
            if scanner in user_agent:
                jarvis_defense.log_intrusion_attempt(ip, f"Scanner detected: {user_agent}")
                raise HTTPException(status_code=403, detail="Forbidden")

    @staticmethod
    async def add_timing_jitter():
        """Add random delay to error responses to prevent timing attacks."""
        await asyncio.sleep(random.uniform(0.1, 0.5))

anti_recon = AntiRecon()
