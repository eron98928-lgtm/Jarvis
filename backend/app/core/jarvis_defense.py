import os
import time
import logging
from datetime import datetime
from .security_config import security_settings

# Defensive Logger
defense_logger = logging.getLogger("defense")
defense_logger.setLevel(logging.WARNING)
handler = logging.FileHandler("/app/data/defense.log")
formatter = logging.Formatter('%(asctime)s - [DEFENSE] - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
defense_logger.addHandler(handler)

class JarvisDefense:
    def __init__(self):
        self.suspicious_ips = {}
        self.blocklist = set()
        self.threshold = 10 # Attempts before block
        
    def log_intrusion_attempt(self, ip: str, reason: str):
        defense_logger.warning(f"Intrusion attempt detected from IP: {ip} | Reason: {reason}")
        self.suspicious_ips[ip] = self.suspicious_ips.get(ip, 0) + 1
        if self.suspicious_ips[ip] >= self.threshold:
            self.block_ip(ip)

    def block_ip(self, ip: str):
        if ip not in self.blocklist:
            defense_logger.critical(f"IP BLOCKED PERMANENTLY: {ip}")
            self.blocklist.add(ip)
            # In a real scenario, this would update UFW or a Redis blocklist

    def is_blocked(self, ip: str) -> bool:
        return ip in self.blocklist

    @staticmethod
    def obfuscate_error(error: Exception) -> str:
        """Never reveal internal details in error messages."""
        # Log the real error internally
        defense_logger.error(f"Internal Error: {str(error)}")
        # Return generic message to user
        return "Ocorreu um erro interno no sistema. O incidente foi registrado."

    @staticmethod
    def anti_fingerprinting_headers(response_headers: dict):
        """Remove headers that reveal technology stack."""
        response_headers.pop("Server", None)
        response_headers.pop("X-Powered-By", None)
        response_headers["Server"] = "JARVIS-Core" # Fake server name

jarvis_defense = JarvisDefense()
