# Use Python 3.12 slim como base
FROM python:3.12-slim

# Define variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1

# Atualiza pacotes e instala dependências do sistema
RUN apt-get update && apt-get install -y \
    git \
    wget \
    unzip \
    chromium \
    chromium-driver \
    fonts-liberation \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Define diretório de trabalho
WORKDIR /app

# Copia os arquivos do projeto para dentro do container
COPY . .

# Instala dependências Python
RUN pip install -r requirements.txt

# Define o comando padrão (opcional)
CMD ["python3", "-m", "consulta.routers.exec_consulta"]
