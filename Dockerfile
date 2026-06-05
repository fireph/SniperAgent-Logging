FROM python:3-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir fastmcp openai httpx

COPY src/sniper/ sniper/

CMD ["python", "-m", "sniper.main"]
