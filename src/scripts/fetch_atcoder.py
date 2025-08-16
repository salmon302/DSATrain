from __future__ import annotations

from pathlib import Path

from src.collectors.atcoder_fetcher import AtCoderFetcher


def main() -> None:
    data_dir = Path(__file__).resolve().parents[2] / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    AtCoderFetcher(data_dir).run()


if __name__ == "__main__":
    main() 