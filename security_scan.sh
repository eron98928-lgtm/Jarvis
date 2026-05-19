#!/bin/bash

echo "========================================="
echo "   JARVIS SECURITY SCAN (pip-audit)      "
echo "========================================="

# Check if pip-audit is installed
if ! command -v pip-audit &> /dev/null
then
    echo "pip-audit não encontrado. Instalando..."
    pip install pip-audit
fi

echo "Verificando vulnerabilidades no backend/requirements.txt..."
pip-audit -r backend/requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Nenhuma vulnerabilidade conhecida encontrada."
else
    echo "❌ Vulnerabilidades encontradas! Verifique o relatório acima."
fi

echo "========================================="
