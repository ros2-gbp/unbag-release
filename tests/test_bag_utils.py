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

from pathlib import Path

import pytest

from ros2_unbag.core.utils.bag_utils import resolve_bag_path


def test_resolve_single_db3_file(tmp_path: Path):
    bag_file = tmp_path / "sample.db3"
    bag_file.touch()

    resolved, storage_id = resolve_bag_path(str(bag_file))

    assert resolved == str(bag_file.resolve())
    assert storage_id == "sqlite3"


def test_resolve_single_mcap_file(tmp_path: Path):
    bag_file = tmp_path / "sample.mcap"
    bag_file.touch()

    resolved, storage_id = resolve_bag_path(str(bag_file))

    assert resolved == str(bag_file.resolve())
    assert storage_id == "mcap"


def test_reject_unsupported_file_extension(tmp_path: Path):
    bag_file = tmp_path / "sample.txt"
    bag_file.touch()

    with pytest.raises(ValueError, match="Unsupported bag extension"):
        resolve_bag_path(str(bag_file))


def test_reject_missing_path(tmp_path: Path):
    with pytest.raises(FileNotFoundError, match="not found"):
        resolve_bag_path(str(tmp_path / "does_not_exist"))


def test_resolve_valid_sqlite_folder(tmp_path: Path):
    bag_dir = tmp_path / "split_sqlite"
    bag_dir.mkdir()
    (bag_dir / "metadata.yaml").write_text(
        "rosbag2_bagfile_information:\n"
        "  storage_identifier: sqlite3\n",
        encoding="utf-8",
    )
    (bag_dir / "bag_0.db3").touch()
    (bag_dir / "bag_1.db3").touch()

    resolved, storage_id = resolve_bag_path(str(bag_dir))

    assert resolved == str(bag_dir.resolve())
    assert storage_id == "sqlite3"


def test_resolve_valid_mcap_folder(tmp_path: Path):
    bag_dir = tmp_path / "split_mcap"
    bag_dir.mkdir()
    (bag_dir / "metadata.yaml").write_text(
        "rosbag2_bagfile_information:\n"
        "  storage_identifier: mcap\n",
        encoding="utf-8",
    )
    (bag_dir / "bag_0.mcap").touch()
    (bag_dir / "bag_1.mcap").touch()

    resolved, storage_id = resolve_bag_path(str(bag_dir))

    assert resolved == str(bag_dir.resolve())
    assert storage_id == "mcap"


def test_reject_folder_without_metadata(tmp_path: Path):
    bag_dir = tmp_path / "invalid_folder"
    bag_dir.mkdir()
    (bag_dir / "bag_0.db3").touch()
    (bag_dir / "bag_1.db3").touch()

    with pytest.raises(ValueError, match="missing metadata.yaml"):
        resolve_bag_path(str(bag_dir))


def test_resolve_non_split_folder_with_single_segment(tmp_path: Path):
    bag_dir = tmp_path / "single_segment"
    bag_dir.mkdir()
    (bag_dir / "metadata.yaml").write_text(
        "rosbag2_bagfile_information:\n"
        "  storage_identifier: sqlite3\n",
        encoding="utf-8",
    )
    (bag_dir / "bag_0.db3").touch()

    resolved, storage_id = resolve_bag_path(str(bag_dir))

    assert resolved == str(bag_dir.resolve())
    assert storage_id == "sqlite3"


def test_reject_unsupported_storage_identifier(tmp_path: Path):
    bag_dir = tmp_path / "unsupported_storage"
    bag_dir.mkdir()
    (bag_dir / "metadata.yaml").write_text(
        "rosbag2_bagfile_information:\n"
        "  storage_identifier: foo\n",
        encoding="utf-8",
    )
    (bag_dir / "bag_0.foo").touch()
    (bag_dir / "bag_1.foo").touch()

    with pytest.raises(ValueError, match="Unsupported storage identifier"):
        resolve_bag_path(str(bag_dir))
