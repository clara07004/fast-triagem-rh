# Fast Triagem — imagem do app pro servidor (VPS SaveinCloud / Docker).
# Build e subida: docker compose up -d --build  (ver docs/DEPLOY_VPS_SAVEINCLOUD.md)
FROM python:3.11-slim

# Horário de Brasília no histórico de triagens (datetime.now no servidor).
RUN apt-get update \
    && apt-get install -y --no-install-recommends tzdata \
    && rm -rf /var/lib/apt/lists/*
ENV TZ=America/Sao_Paulo \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_PORT=8501

WORKDIR /app

# Dependências primeiro — mudar só o app.py não refaz o pip install.
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir .

COPY app.py ./
COPY assets ./assets
COPY .streamlit ./.streamlit

EXPOSE 8501

# Porta vem de STREAMLIT_SERVER_PORT — sobrescrevível no painel da SaveinCloud.
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
