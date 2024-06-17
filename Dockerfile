# Use Alpine Linux as the base image
FROM alpine:latest

# Create app directory
WORKDIR /app

# Install dependencies (lame, sox, flac, Python, git)
RUN apk update && \
    apk add --no-cache lame sox flac python3 py3-pip git

# Install Intermodal
RUN apk add --no-cache curl && \
    curl --proto '=https' --tlsv1.2 -sSf https://imdl.io/install.sh | ash -s -- --to /usr/local/bin

# Install Red Oxide
RUN apk add --no-cache git && \
    git clone https://github.com/DevYukine/red_oxide.git /usr/local/bin/red_oxide && \
    chmod +x /usr/local/bin/red_oxide/red_oxide

# Clone the web GUI repository directly into /app
RUN git clone https://github.com/sprtlw/red_oxide_webGUI.git /app

# Convert the whole directory to LF line endings
RUN find /app -type f -exec dos2unix {} +

# Install the dependencies in the web GUI
RUN source /app/venv/bin/activate && \
    pip install -r /app/requirements.txt

# Cleanup unnecessary packages
RUN apk del curl git

EXPOSE 5000

# Define entry point
CMD ["/bin/ash", "-c", "source /app/venv/bin/activate && flask run --host=0.0.0.0"]
