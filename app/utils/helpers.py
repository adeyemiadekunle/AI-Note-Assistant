from typing import List


def chunk_text(text: str, size: int) -> List[str]:
    """Split text into chunks of a given size."""
    if size <= 0:
        raise ValueError("size must be greater than zero")
    return [text[index : index + size] for index in range(0, len(text), size)]
