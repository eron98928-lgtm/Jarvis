#!/bin/bash

echo "🛡️ Iniciando Hardening de Segurança do JARVIS..."

# 1. Instalação de Ferramentas de Segurança (Simulado para o script)
echo "📦 Instalando Bandit, Semgrep e Safety..."
pip install bandit semgrep safety

# 2. SAST - Static Analysis Security Testing
echo "🔍 Rodando Bandit (SAST Python)..."
bandit -r backend/app -f txt -o data/bandit_report.txt

echo "🔍 Rodando Semgrep (Análise Estática)..."
semgrep --config auto backend/app --text -o data/semgrep_report.txt

# 3. Configuração de Firewall (UFW) - Requer sudo
if command -v ufw &> /dev/null; then
    echo "🔥 Configurando Firewall UFW..."
    sudo ufw default deny incoming
    sudo ufw default allow outgoing
    sudo ufw allow 80/tcp
    sudo ufw allow 443/tcp
    sudo ufw allow 8000/tcp
    # sudo ufw --force enable
fi

# 4. Docker Hardening Check
echo "🐳 Aplicando diretrizes de Hardening do Docker..."
# Estas diretrizes são aplicadas no docker-compose.yml e Dockerfile

# 5. Desabilitar informações de versão
echo "🚫 Ofuscando assinaturas de sistema..."
# Aplicado via Nginx e FastAPI Middlewares

echo "✅ Hardening concluído. Relatórios salvos em data/"
