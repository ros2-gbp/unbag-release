# MIT License

# Copyright (c) 2026 Institute for Automotive Engineering (ika), RWTH Aachen University

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os


_STORAGE_BY_EXTENSION = {
    ".db3": "sqlite3",
    ".mcap": "mcap",
}

_EXTENSION_BY_STORAGE = {v: k for k, v in _STORAGE_BY_EXTENSION.items()}


def resolve_bag_path(path: str) -> tuple[str, str]:
    """
    Resolve and validate a bag input path.

    Supports:
    - Single-file bags (.db3 / .mcap)
    - Bag folders (directory with metadata.yaml + segment files)

    Args:
        path: User-provided path.

    Returns:
        tuple[str, str]: (resolved_uri, storage_id)

    Raises:
        FileNotFoundError: If path does not exist.
        ValueError: If path is not a supported bag input.
    """
    if path is None or str(path).strip() == "":
        raise ValueError("Bag path is empty.")

    resolved = os.path.abspath(os.path.expanduser(str(path)))

    if not os.path.exists(resolved):
        raise FileNotFoundError(f"Bag path '{path}' not found.")

    if os.path.isfile(resolved):
        ext = os.path.splitext(resolved)[1].lower()
        storage_id = _STORAGE_BY_EXTENSION.get(ext)
        if storage_id is None:
            raise ValueError(f"Unsupported bag extension: {ext}")
        return resolved, storage_id

    if os.path.isdir(resolved):
        return _resolve_bag_folder(resolved)

    raise ValueError(f"Unsupported bag path type: '{resolved}'")


def _resolve_bag_folder(folder_path: str) -> tuple[str, str]:
    """
    Validate a bag directory and resolve its storage backend.

    Args:
        folder_path: Absolute path to a candidate bag directory.

    Returns:
        tuple[str, str]: (folder_path, storage_id)

    Raises:
        ValueError: If metadata is missing/invalid, storage is unsupported,
            or no segment file matches the declared storage.
    """
    metadata_path = os.path.join(folder_path, "metadata.yaml")
    if not os.path.isfile(metadata_path):
        raise ValueError(
            f"Invalid bag folder '{folder_path}': missing metadata.yaml."
        )

    storage_id = _read_storage_identifier(metadata_path)
    ext = _EXTENSION_BY_STORAGE.get(storage_id)
    if ext is None:
        supported = ", ".join(sorted(_EXTENSION_BY_STORAGE.keys()))
        raise ValueError(
            f"Unsupported storage identifier '{storage_id}' in metadata.yaml. "
            f"Supported: {supported}."
        )

    segment_files = [
        name for name in os.listdir(folder_path)
        if os.path.isfile(os.path.join(folder_path, name)) and name.lower().endswith(ext)
    ]
    if len(segment_files) < 1:
        raise ValueError(
            f"Invalid bag folder '{folder_path}': expected at least 1 '{ext}' bag file."
        )

    return folder_path, storage_id


def _read_storage_identifier(metadata_path: str) -> str:
    """
    Extract the storage identifier from a ROS 2 bag metadata file.

    Args:
        metadata_path: Path to metadata.yaml.

    Returns:
        str: Storage identifier value (e.g., ``sqlite3`` or ``mcap``).

    Raises:
        ValueError: If no ``storage_identifier`` entry is present.
    """
    with open(metadata_path, "r", encoding="utf-8") as metadata_file:
        for line in metadata_file:
            stripped = line.strip()
            if stripped.startswith("storage_identifier:"):
                return stripped.split(":", 1)[1].strip().strip("'\"")

    raise ValueError(
        f"Invalid bag metadata '{metadata_path}': missing storage_identifier."
    )
