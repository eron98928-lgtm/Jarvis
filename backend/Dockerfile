# Stage 1: Builder (Compilação de dependências pesadas como librosa em ARM64)
FROM python:3.11-slim as builder

WORKDIR /app

# Instalação de compiladores necessários para pacotes científicos (librosa, numpy, scipy)
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    gfortran \
    libatlas-base-dev \
    libsndfile1-dev \
    libasound2-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Instalação em diretório de usuário para fácil cópia posterior
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Final (Imagem limpa e segura)
FROM python:3.11-slim

WORKDIR /app

# Dependências de runtime necessárias
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    libasound2 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Criação de usuário não-root para segurança
RUN groupadd -r jarvis && useradd -r -g jarvis -m jarvis

# Copia pacotes Python compilados do estágio builder
COPY --from=builder /root/.local /home/jarvis/.local

# Copia o código da aplicação
COPY . .

# Configuração de diretórios e permissões
RUN mkdir -p data/db && chown -R jarvis:jarvis /app

# Variáveis de ambiente
ENV PATH=/home/jarvis/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

USER jarvis

EXPOSE 8000

# Healthcheck para monitoramento do container
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
