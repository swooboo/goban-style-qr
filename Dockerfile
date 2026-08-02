FROM python:3.12-slim

WORKDIR /app

# Copy only the files needed to install dependencies first (layer caching)
COPY pyproject.toml ./
COPY src/ ./src/

# Install the package and its dependencies; this creates the goban-style-qr-web script
RUN pip install --no-cache-dir .

# Expose the default port (Railway overrides this via the PORT env var)
EXPOSE 8000

# Bind to 0.0.0.0 so Railway can reach the process; port is read from $PORT env var
CMD ["goban-style-qr-web", "--host", "0.0.0.0"]
