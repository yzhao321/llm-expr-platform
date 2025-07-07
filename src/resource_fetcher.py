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
# File: resource_fetcher.py
# Description: Utility to download models from a JSON configuration.
# Author:
#
# ----------------------------------------------------------------------------

import json
import sys
import shutil
from pathlib import Path
from huggingface_hub import hf_hub_download

class ResourceFetcher:
    """
    ResourceFetcher automates downloading models
    defined in a JSON configuration file using huggingface_hub.
    """

    def __init__(self, config_path, output_dir):
        self.config_path = Path(config_path)
        self.output_dir = Path(output_dir)
        self.config = self._load_config()

    def _load_config(self):
        """
        Load JSON configuration.
        """
        if not self.config_path.is_file():
            print(f"[ERROR] Config file not found: {self.config_path}")
            sys.exit(1)
        with open(self.config_path) as f:
            return json.load(f)

    def _download_hf_file(self, repo_id, filename, target_path):
        """
        Use huggingface_hub to download with authentication.
        """
        print(f"[INFO] Downloading {repo_id}/{filename}")
        try:
            local_path = hf_hub_download(
                repo_id=repo_id,
                filename=filename
            )
            target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(local_path, target_path)
            print(f"[SUCCESS] Saved to {target_path}")
        except Exception as e:
            print(f"[ERROR] Failed to download {repo_id}/{filename}: {e}")

    def download_models(self):
        """
        Download all models listed under 'models' in the config.
        Skips any model that has already been downloaded.
        """
        items = self.config.get("models", [])
        if not items:
            print("[INFO] No models to download.")
            return

        print("\n=== Downloading Models ===")
        for item in items:
            name = item.get("name", "unnamed_model")
            repo_id = item.get("repo_id")
            filename = item.get("filename")

            if not repo_id or not filename:
                print(f"[WARNING] Skipping {name}: missing repo_id or filename")
                continue

            target_folder = self.output_dir / "models" / name
            target_folder.mkdir(parents=True, exist_ok=True)
            target_file_path = target_folder / filename

            if target_file_path.exists():
                print(f"[SKIP] {name} already exists at {target_file_path}")
                continue

            print(f"\n[MODEL] {name}")
            print(f"  Repo ID : {repo_id}")
            print(f"  File    : {filename}")

            self._download_hf_file(repo_id, filename, target_file_path)


if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    config_path = project_root / "json" / "download_config.json"
    output_path = project_root / "downloads"

    fetcher = ResourceFetcher(config_path, output_path)
    fetcher.download_models()
