#!/bin/bash

echo "🚀 Iniciando Setup do JARVIS (Segurança Máxima)..."

# 1. Criar diretórios necessários
mkdir -p data/db
touch data/audit.log

# 2. Instalar dependências locais para o scan
echo "📦 Instalando dependências para o scan de segurança..."
pip install -r backend/requirements.txt

# 3. Rodar Scan de Segurança
./security_scan.sh

# 4. Inicializar Banco de Dados
echo "🗄️ Inicializando banco de dados..."
python3 backend/init_db.py

echo "✅ Setup concluído com sucesso!"
echo "Para rodar o projeto, use: docker-compose up --build"
