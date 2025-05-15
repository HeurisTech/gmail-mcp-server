FROM python:3.12-slim

# Install required dependencies for downloading and unpacking uv
RUN apt-get update && apt-get install -y curl unzip && rm -rf /var/lib/apt/lists/*

# Install uv from GitHub releases (latest as of now is 0.1.18)
RUN curl -Ls https://astral.sh/uv/install.sh | sh

# Ensure uv is in PATH
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app
COPY . .

RUN uv sync

CMD ["uv", "run", "server.py"]