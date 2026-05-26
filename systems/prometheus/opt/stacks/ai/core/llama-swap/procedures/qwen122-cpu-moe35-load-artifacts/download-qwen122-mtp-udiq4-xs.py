from pathlib import Path

from huggingface_hub import hf_hub_download


REPO_ID = "unsloth/Qwen3.5-122B-A10B-MTP-GGUF"
TARGET_DIR = Path("/mnt/local/nvme/ai/models/unsloth/Qwen3.5-122B-A10B-MTP-GGUF/UD-IQ4_XS")
CACHE_DIR = Path("/mnt/local/nvme/ai/cache/huggingface/hub")
FILES = [
    "UD-IQ4_XS/Qwen3.5-122B-A10B-UD-IQ4_XS-00001-of-00003.gguf",
    "UD-IQ4_XS/Qwen3.5-122B-A10B-UD-IQ4_XS-00002-of-00003.gguf",
    "UD-IQ4_XS/Qwen3.5-122B-A10B-UD-IQ4_XS-00003-of-00003.gguf",
]


def main() -> None:
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    for filename in FILES:
        cache_path = Path(hf_hub_download(repo_id=REPO_ID, filename=filename, cache_dir=CACHE_DIR))
        link_path = TARGET_DIR / Path(filename).name
        if link_path.exists() or link_path.is_symlink():
            link_path.unlink()
        link_path.symlink_to(cache_path)
        print(f"{link_path} -> {cache_path}")


if __name__ == "__main__":
    main()
