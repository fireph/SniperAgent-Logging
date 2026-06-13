FROM python:3-alpine

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir fastmcp openai httpx pytimeparse tiktoken

COPY src/sniper/ sniper/

CMD ["python", "-m", "sniper.main"]
