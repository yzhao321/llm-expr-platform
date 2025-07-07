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
# File: expr_simulation.py
# Description:
# Author:
#
# ----------------------------------------------------------------------------

import subprocess
import sys
import random
import datasets
from datasets import load_dataset


class ExprSimulation:
    """
    Running prompts from datasets through Ollama.
    """

    def __init__(self, model_name="deepseek-r1:1.5b", split="validation", size=0):
        self.model_name = model_name
        self.split = split
        self.size = size
        self.dataset = None

    def download_dataset(self):
        """
        Download the hellaswag dataset.
        """
        print(f"[INFO] Downloading hellaswag ({self.split} split)...")
        self.dataset = load_dataset("hellaswag", split=self.split)
        print(f"[INFO] Download complete. Total samples: {len(self.dataset)}")

    def generate_prompt(self, sample):
        """
        Given a single sample, format it as a prompt.
        """
        context = sample.get("ctx", "")
        endings = sample.get("endings", [])
        prompt = f"Context: {context}\nOptions:\n"
        for idx, ending in enumerate(endings):
            prompt += f"{idx + 1}. {ending}\n"
        return prompt

    def run_ollama(self, prompt_text, sample_id=None):
        """
        Call ollama with the given prompt text.
        """
        print("[INFO] Running ollama...")
        if sample_id is not None:
            print(f"[INFO] Sample ID: {sample_id}")

        try:
            result = subprocess.run(
                ["ollama", "run", self.model_name],
                input=prompt_text.encode(),
                capture_output=True,
                check=True
            )
            print("[OLLAMA OUTPUT]")
            print(result.stdout.decode())
        except subprocess.CalledProcessError as e:
            print("[ERROR] Ollama command failed:")
            print(e.stderr.decode())
            sys.exit(1)

    def run(self):
        """
        Orchestrate the full experiment over multiple samples.
        """
        self.download_dataset()

        num_samples = len(self.dataset)
        to_process = min(self.size, num_samples) if self.size > 0 else num_samples

        print(f"[INFO] Processing {to_process} samples...")

        for i in range(to_process):
            sample = self.dataset[i]
            prompt = self.generate_prompt(sample)
            print(f"[INFO] Prompt for sample {i}:")
            print(prompt)
            self.run_ollama(prompt, sample_id=i)


if __name__ == "__main__":
    sim = ExprSimulation(size=10)
    sim.run()
