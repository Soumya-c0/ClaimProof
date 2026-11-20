FROM node:20-slim AS web
WORKDIR /web
COPY claimproof/frontend/package*.json ./
RUN npm ci
COPY claimproof/frontend/ ./
RUN npm run build

FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*
RUN useradd -m -u 1000 user && mkdir -p /app && chown user:user /app
WORKDIR /app
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
COPY claimproof/backend/requirements.txt .
RUN grep -v -i paddleocr requirements.txt > req.txt && pip install --no-cache-dir -r req.txt
RUN python -m spacy download en_core_web_lg
COPY --chown=user:user claimproof/backend/ .
COPY --from=web --chown=user:user /web/dist ./static
USER user
ENV HOME=/home/user HF_HOME=/home/user/.cache
RUN python -c "from sentence_transformers import CrossEncoder; CrossEncoder('BAAI/bge-reranker-base')" && python -c "import chromadb; c=chromadb.Client(); c.create_collection('w').add(ids=['1'], documents=['hi'])"
EXPOSE 7860
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]