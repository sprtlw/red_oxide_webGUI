# Use Ubuntu as the base image
FROM ubuntu:latest

# Create app directory
WORKDIR /app

# Install dependencies (lame, sox, flac, Python, git)
RUN apt-get update && \
    apt-get install -y lame sox flac python3 python3-pip python3-venv git wget dos2unix

# Install Intermodal
RUN apt-get install -y curl && \
    curl --proto '=https' --tlsv1.2 -sSf https://imdl.io/install.sh | bash -s -- --to /usr/local/bin

# Install Red Oxide
RUN latest_version=$(wget -qO- https://github.com/DevYukine/red_oxide/releases/latest | grep -o -E "v[0-9]+\.[0-9]+\.[0-9]+" | head -n 1) && \
    wget https://github.com/DevYukine/red_oxide/releases/download/${latest_version}/red_oxide-Linux-x86_64-gnu -P /usr/local/bin && \
    mv /usr/local/bin/red_oxide-Linux-x86_64-gnu /usr/local/bin/red_oxide && \
    chmod +x /usr/local/bin/red_oxide

# Clone the web GUI repository directly into /app
RUN git clone https://github.com/sprtlw/red_oxide_webGUI.git /app

# Convert the whole directory to LF line endings
RUN find /app -type f -exec dos2unix {} +

# Create a virtual environment and install the dependencies in the web GUI
RUN python3 -m venv /app/.venv && \
    /app/.venv/bin/pip install --upgrade pip && \
    /app/.venv/bin/pip install -r /app/requirements.txt

# Cleanup unnecessary packages
RUN apt-get remove -y curl git wget dos2unix

EXPOSE 5000

# Define entry point
CMD ["/bin/bash", "-c", "source /app/.venv/bin/activate && flask run --host=0.0.0.0"]