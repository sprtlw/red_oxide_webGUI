# Use Alpine Linux as the base image
FROM alpine:latest

# Create app directory
WORKDIR /app

# Install dependencies (lame, sox, flac, Python)
RUN apk update && \
    apk add --no-cache lame sox flac python3 py3-pip && \
    python3 -m venv /app/venv && \
    source /app/venv/bin/activate && \
    pip install Flask

# Install Intermodal
RUN apk add --no-cache curl && \
    curl --proto '=https' --tlsv1.2 -sSf https://imdl.io/install.sh | ash -s -- --to /usr/local/bin

# Install Red Oxide
RUN apk add --no-cache wget && \
    latest_version=$(wget -qO- https://github.com/DevYukine/red_oxide/releases/latest | grep -o -E "v[0-9]+\.[0-9]+\.[0-9]+" | head -n 1) && \
    wget "https://github.com/DevYukine/red_oxide/releases/download/$latest_version/red_oxide-Linux-x86_64-gnu" -P /usr/local/bin && \
    mv "/usr/local/bin/red_oxide-Linux-x86_64-gnu" "/usr/local/bin/red_oxide" && \
    chmod +x "/usr/local/bin/red_oxide"

# Download app.py and index.html from pastebin
RUN wget -O app.py https://pastebin.com/raw/WV6uRrcW
RUN mkdir -p templates && \
    wget -O templates/index.html https://pastebin.com/raw/u7DKjetC
RUN dos2unix app.py
RUN dos2unix templates/index.html

# Cleanup unnecessary packages
RUN apk del curl wget

EXPOSE 5000

# Define entry point
CMD ["/bin/ash", "-c", "source /app/venv/bin/activate && flask run --host=0.0.0.0"]