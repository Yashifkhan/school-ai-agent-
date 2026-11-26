
import json
from pathlib import Path
from functools import lru_cache


# Project root: server/
BASE_DIR = Path(__file__).resolve().parents[2]

# JSON database path
DATA_FILE = BASE_DIR / "data" / "school_saas_demo_seed.json"


@lru_cache(maxsize=1)
def load_school_data() -> dict:
    """
    Load school JSON data once and cache it.
    """

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"School data file not found: {DATA_FILE}"
        )

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    return data


def get_collection(collection_name: str) -> list[dict]:
    """
    Get records from a particular collection.
    """

    data = load_school_data()

    collection = data.get(collection_name)

    if collection is None:
        raise ValueError(
            f"Collection '{collection_name}' does not exist."
        )

    if not isinstance(collection, list):
        raise ValueError(
            f"Collection '{collection_name}' must be a list."
        )

    return collection


