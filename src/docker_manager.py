#!/usr/bin/env python3
#
# Copyright (c) 2025 University of California, Santa Cruz. All rights reserved.
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# ----------------------------------------------------------------------------
#
# File: docker_manager.py
# Description: Utility to manage Docker containers for LLM frameworks.
# Author: Yinyuan Zhao
#
# ----------------------------------------------------------------------------

import json
import subprocess
import sys
from pathlib import Path


class DockerManager:
    """
    DockerManager is a utility class to automate building, running,
    and managing Docker containers for LLM framework environments.
    """

    def __init__(self, config_path):
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self):
        """
        Internal helper to load the JSON configuration file.
        """
        if not self.config_path.exists():
            print(f"[ERROR] Config file not found: {self.config_path}")
            sys.exit(1)
        with open(self.config_path) as f:
            return json.load(f)

    def _get_framework_dir(self):
        """
        Internal helper to verify and return the Docker build context directory.
        """
        image_name = self.config.get("IMAGE_NAME", "")
        docker_dir = Path(__file__).parent.parent / "dockerfiles" / image_name
        dockerfile_path = docker_dir / "Dockerfile"

        if not docker_dir.is_dir() or not dockerfile_path.is_file():
            print(f"[ERROR] Missing framework directory or Dockerfile: {docker_dir}")
            sys.exit(1)
        return docker_dir

    def build_image(self):
        """
        Build the Docker image using the configuration and framework Dockerfile.
        """
        image_name = self.config.get("IMAGE_NAME", "")
        user_name = self.config.get("USER_NAME")

        if not user_name:
            print("[ERROR] USER_NAME is required in config.json")
            sys.exit(1)

        docker_dir = self._get_framework_dir()
        image_name_tag = f"llm_infra_{image_name}"

        cmd = [
            "docker", "build",
            "-t", image_name_tag,
            "--build-arg", f"USER_NAME={user_name}",
            str(docker_dir)
        ]

        print(f"[INFO] Running build: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)

    def run_container(self):
        """
        Run the Docker container in detached mode to serve in the background.
        """
        user_name = self.config.get("USER_NAME")
        if not user_name:
            print("[ERROR] USER_NAME is required in config.json")
            sys.exit(1)

        image_name = self.config.get("IMAGE_NAME", "")
        image_name_tag = f"llm_infra_{image_name}"
        container_name = f"{image_name_tag}_{user_name}"

        ports = self.config.get("PORTS", [])
        gpus = self.config.get("GPUS", None)
        mounts = self.config.get("MOUNTS", [])
        command = self.config.get("COMMAND", ["bash"])

        cmd = ["docker", "run", "-dit", "--name", container_name, "-e", f"USER_NAME={user_name}"]
        if gpus:
            cmd.extend(["--gpus", gpus])
        for p in ports:
            cmd.extend(["-p", p])
        for m in mounts:
            host_dir = Path(m["host_dir"]).resolve()
            if not host_dir.is_dir():
                print(f"[ERROR] Host directory does not exist: {host_dir}")
                sys.exit(1)
            container_dir = m["container_dir"]
            mount_spec = f"type=bind,source={host_dir},target={container_dir}"
            cmd.extend(["--mount", mount_spec])

        cmd.append(image_name_tag)
        cmd.extend(command)

        print(f"[INFO] Running container: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)

    def exec_container(self, command=None):
        """
        Execute a command inside the running container as the configured user.
        """
        user_name = self.config.get("USER_NAME")
        if not user_name:
            print("[ERROR] USER_NAME is required in config.json")
            sys.exit(1)

        image_name = self.config.get("IMAGE_NAME", "")
        image_name_tag = f"llm_infra_{image_name}"
        container_name = f"{image_name_tag}_{user_name}"

        if command is None:
            command = ["bash"]

        cmd = ["docker", "exec", "-it", "-u", user_name, container_name]
        cmd.extend(command)

        print(f"[INFO] Exec into container: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)


def launch():
    config_path = Path(__file__).parent.parent / "json" / "docker_config.json"
    manager = DockerManager(config_path)

    if len(sys.argv) < 2:
        print("Usage: docker_manager.py [build|run|exec]")
        sys.exit(1)

    action = sys.argv[1].lower()

    if action == "build":
        manager.build_image()
    elif action == "run":
        manager.run_container()
    elif action == "exec":
        manager.exec_container()
    else:
        print(f"[ERROR] Unknown action: {action}")
        sys.exit(1)


if __name__ == "__main__":
    launch()
