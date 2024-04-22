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

# Download Web GUI
RUN wget -O app.py https://raw.githubusercontent.com/sprtlw/red_oxide_webGUI/main/app.py
RUN mkdir -p templates && \
    wget -O templates/index.html https://raw.githubusercontent.com/sprtlw/red_oxide_webGUI/main/templates/index.html
RUN mkdir -p static && \
    mkdir -p static/css && \
    wget -O static/css/styles.css https://raw.githubusercontent.com/sprtlw/red_oxide_webGUI/main/static/css/styles.css

# Convert to LF line endings
RUN dos2unix app.py
RUN dos2unix templates/index.html
RUN dos2unix static/css/styles.css

# Cleanup unnecessary packages
RUN apk del curl wget

EXPOSE 5000

# Define entry point
CMD ["/bin/ash", "-c", "source /app/venv/bin/activate && flask run --host=0.0.0.0"]
