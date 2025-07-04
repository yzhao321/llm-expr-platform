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
 && rm -rf /var/lib/apt/lists/*

# Install Ollama using the official install script
RUN curl -fsSL https://ollama.com/install.sh | sh

# Create a non-root user
RUN useradd -ms /bin/bash $USER_NAME
USER $USER_NAME
WORKDIR /home/$USER_NAME

# Default command
CMD ["bash"]
