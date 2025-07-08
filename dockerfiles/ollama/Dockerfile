FROM ubuntu:22.04

# Avoid interactive prompts during package installs
ENV DEBIAN_FRONTEND=noninteractive

# Accept USER_NAME as build argument and set as env
ARG USER_NAME
ENV USER_NAME=${USER_NAME}

# Add /usr/local/bin to PATH globally
ENV PATH="/usr/local/bin:${PATH}"

# Install dependencies for HTTPS, GPG, LSB detection, and curl
RUN apt-get update && apt-get install -y \
    ca-certificates \
    gnupg \
    lsb-release \
    curl \
    python3 \
    python3-pip \
 && rm -rf /var/lib/apt/lists/*

# Install some standard Python packages for llm simulation
RUN pip3 install --no-cache-dir \
    numpy \
    pandas \
    datasets

# Install Ollama using the official install script
RUN curl -fsSL https://ollama.com/install.sh | sh

# Create a non-root user
RUN useradd -ms /bin/bash $USER_NAME
USER $USER_NAME
WORKDIR /home/$USER_NAME

# Default command
CMD ["bash"]
