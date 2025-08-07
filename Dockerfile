# FROM ghcr.io/astral-sh/uv:python3.11-alpine

# ENV PYTHONUNBUFFERED=1
# ENV PYTHONDONTWRITEBYTECODE=1
# ENV DATABASE_URL=${DATABASE_URL}
# ENV SECRET_KEY=${SECRET_KEY}

# WORKDIR /app

# RUN apk update

# # COPY requirements.txt .

# COPY pyproject.toml .
# COPY uv.lock .
# RUN uv sync --locked

# # RUN pip install --no-cache-dir -r requirements.txt

# COPY . .

# EXPOSE 8000

# COPY entrypoint.sh /entrypoint.sh
# RUN chmod +x /entrypoint.sh
# CMD ["/entrypoint.sh"]
