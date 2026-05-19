import random
import asyncio
from fastapi import Request, HTTPException
from .jarvis_defense import jarvis_defense

class AntiRecon:
    def __init__(self):
        # Lista de caminhos comuns que scanners procuram
        self.honeypot_paths = [
            "/.env", "/.git", "/wp-admin", "/admin", "/phpmyadmin", 
            "/config", "/backup", "/v1/debug"
        ]
        
    async def check_request(self, request: Request):
        path = request.url.path
        ip = request.client.host
        
        # Bypass para dispositivos já autenticados ou com token de confiança
        # Isso evita que o administrador seja banido por extensões de navegador
        is_trusted = request.cookies.get("jarvis_device_token") or request.headers.get("X-Jarvis-Device-Token")
        
        # 1. Detecção de Honeypot
        if path in self.honeypot_paths:
            if is_trusted:
                # Se for um dispositivo confiável, apenas retorna 404 sem banir
                raise HTTPException(status_code=404, detail="Not Found")
            
            # Se não for confiável, loga a tentativa e aplica delay/banimento
            jarvis_defense.log_intrusion_attempt(ip, f"Honeypot access: {path}")
            # Delay aleatório para atrasar o scanner
            await asyncio.sleep(random.uniform(2.0, 5.0))
            raise HTTPException(status_code=404, detail="Not Found")

        # 2. Headers Suspeitos (Scanners conhecidos)
        user_agent = request.headers.get("user-agent", "").lower()
        scanners = ["nmap", "nikto", "sqlmap", "burp", "dirbuster"]
        for scanner in scanners:
            if scanner in user_agent:
                if is_trusted:
                    # Administrador usando ferramentas de teste
                    return
                
                jarvis_defense.log_intrusion_attempt(ip, f"Scanner detected: {user_agent}")
                raise HTTPException(status_code=403, detail="Forbidden")

    @staticmethod
    async def add_timing_jitter():
        """Adiciona delay aleatório em respostas de erro para prevenir ataques de timing."""
        await asyncio.sleep(random.uniform(0.1, 0.5))

anti_recon = AntiRecon()
