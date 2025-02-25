import logging
import os
import pathlib
import platform
import shutil
import subprocess
import tempfile
import traceback

import pkg_resources
import requests
from tqdm import tqdm

SUPPORTED_DOCUMENT_TYPES = [
    ".csv",
    ".docx",
    ".doc",
    ".enex",
    ".eml",
    ".epub",
    ".html",
    ".md",
    ".msg",
    ".odt",
    ".pdf",
    ".pptx",
    ".ppt",
    ".txt",
    ".py",
    ".js",
    ".jsx",
    ".php",
    ".ts",
    ".tsx",
    ".html",
    ".htm",
    ".java",
    ".cpp",
]


def open_file(path):
    """
    Open file in default application
    """
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


def extract_frontend_dist(static_folder):
    """
    Extract folder frontend/dist from package pautobot
    and put it in the same static folder for serving
    """
    if os.path.exists(static_folder):
        logging.info(f"Refreshing {static_folder}...")
        shutil.rmtree(static_folder, ignore_errors=True)
    dist_folder = pkg_resources.resource_filename("pautobot", "frontend-dist")
    if os.path.exists(dist_folder):
        pathlib.Path(static_folder).parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(dist_folder, static_folder)
    if not os.path.exists(static_folder):
        logging.warning("frontend-dist not found in package pautobot")
        pathlib.Path(static_folder).mkdir(parents=True, exist_ok=True)
        with open(os.path.join(static_folder, "index.html"), "w") as f:
            f.write(
                "<b>frontend-dist</b> not found in package pautobot. Please run: <code>bash build_frontend.sh</code>"
            )
        return


def download_file(url, file_path):
    """
    Send a GET request to the URL
    """
    tmp_file = tempfile.NamedTemporaryFile(delete=False)
    pathlib.Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    response = requests.get(url, stream=True)

    # Check if the request was successful
    if response.status_code == 200:
        total_size = int(response.headers.get("content-length", 0))
        block_size = 8192  # Chunk size in bytes
        progress_bar = tqdm(total=total_size, unit="B", unit_scale=True)

        with open(tmp_file.name, "wb") as file:
            # Iterate over the response content in chunks
            for chunk in response.iter_content(chunk_size=block_size):
                file.write(chunk)
                progress_bar.update(len(chunk))

        progress_bar.close()
        shutil.move(tmp_file.name, file_path)
        logging.info("File downloaded successfully.")
    else:
        logging.info("Failed to download file.")


DEFAULT_MODEL_URLS = {
    "ggml-gpt4all-j": "https://gpt4all.io/models/ggml-gpt4all-j.bin",
    "ggml-gpt4all-j-v1.1-breezy": "https://gpt4all.io/models/ggml-gpt4all-j-v1.1-breezy.bin",
    "ggml-gpt4all-j-v1.2-jazzy": "https://gpt4all.io/models/ggml-gpt4all-j-v1.2-jazzy.bin",
    "ggml-gpt4all-j-v1.3-groovy": "https://gpt4all.io/models/ggml-gpt4all-j-v1.3-groovy.bin",
    "ggml-gpt4all-l13b-snoozy": "https://gpt4all.io/models/ggml-gpt4all-l13b-snoozy.bin",
    "ggml-mpt-7b-base": "https://gpt4all.io/models/ggml-mpt-7b-base.bin",
    "ggml-mpt-7b-instruct": "https://gpt4all.io/models/ggml-mpt-7b-instruct.bin",
    "ggml-nous-gpt4-vicuna-13b": "https://gpt4all.io/models/ggml-nous-gpt4-vicuna-13b.bin",
    "ggml-replit-code-v1-3b": "https://huggingface.co/nomic-ai/ggml-replit-code-v1-3b/resolve/main/ggml-replit-code-v1-3b.bin",
    "ggml-stable-vicuna-13B.q4_2": "https://gpt4all.io/models/ggml-stable-vicuna-13B.q4_2.bin",
    "ggml-v3-13b-hermes-q5_1": "https://huggingface.co/eachadea/ggml-nous-hermes-13b/resolve/main/ggml-v3-13b-hermes-q5_1.bin",
    "ggml-vicuna-13b-1.1-q4_2": "https://gpt4all.io/models/ggml-vicuna-13b-1.1-q4_2.bin",
    "ggml-vicuna-7b-1.1-q4_2": "https://gpt4all.io/models/ggml-vicuna-7b-1.1-q4_2.bin",
    "ggml-wizard-13b-uncensored": "https://gpt4all.io/models/ggml-wizard-13b-uncensored.bin",
    "ggml-wizardLM-7B.q4_2": "https://gpt4all.io/models/ggml-wizardLM-7B.q4_2.bin",
}


def download_model(model_type, model_path):
    """
    Download model if not exists
    TODO (vietanhdev):
        - Support more model types
        - Multiple download links
        - Check hash of the downloaded file
        - Original default model: ggml-gpt4all-j-v1.3-groovy
    """
    MODEL_URL = DEFAULT_MODEL_URLS["ggml-replit-code-v1-3b"]

    if not os.path.exists(model_path):
        logging.info("Downloading model...")
        try:
            download_file(MODEL_URL, model_path)
        except Exception as e:
            logging.info(f"Error while downloading model: {e}")
            traceback.print_exc()
            exit(1)
        logging.info("Model downloaded!")
