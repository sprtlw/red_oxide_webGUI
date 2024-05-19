# Use Ubuntu as the base image
FROM ubuntu:latest

# Create app directory
WORKDIR /config

# Install dependencies (lame, sox, flac, Python)
RUN apt-get update && \
    apt-get install -y mktorrent lame sox flac python3 python3-pip git vim

# Install Intermodal
RUN apt-get install -y curl && \
    curl --proto '=https' --tlsv1.2 -sSf https://imdl.io/install.sh | bash -s -- --to /usr/local/bin

# Install Red Oxide
RUN apt-get install -y wget && \
    latest_version=$(wget -qO- https://github.com/DevYukine/red_oxide/releases/latest | grep -o -E "v[0-9]+\.[0-9]+\.[0-9]+" | head -n 1) && \
    wget "https://github.com/DevYukine/red_oxide/releases/download/$latest_version/red_oxide-Linux-x86_64-gnu" -P /usr/local/bin && \
    mv "/usr/local/bin/red_oxide-Linux-x86_64-gnu" "/usr/local/bin/red_oxide" && \
    chmod +x "/usr/local/bin/red_oxide"

# Install OrpheusBetter-Crawler
RUN git clone https://github.com/ApexWeed/orpheusbetter-crawler.git && \
    cd orpheusbetter-crawler && \
    pip3 install -r requirements.txt && \
    python3 setup.py install && \
    cd .. && \
    rm -rf orpheusbetter-crawler

# Install streamrip
RUN pip3 install streamrip --upgrade

# Define entry point
CMD ["/bin/bash"]
