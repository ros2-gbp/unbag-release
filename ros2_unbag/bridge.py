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

"""
GUI Bridge Module.

Provides a JSON-based bridge used by the C++ Qt GUI.
One-shot commands use a request/response JSON envelope on stdin/stdout.
Long-running exports use NDJSON progress events on stdout and are canceled by
terminating the bridge process, which triggers the SIGTERM/SIGINT handler
below to abort the active exporter. There is intentionally no separate
``cancel_export`` RPC.
"""

from __future__ import annotations

import json
import signal
import sys
from typing import Any

from ros2_unbag.backend import (
    inspect_bag,
    list_formats_for_topic_type,
    validate_export_config,
)
from ros2_unbag.core.exporter import Exporter
from ros2_unbag.core.utils.bag_utils import resolve_bag_path
from ros2_unbag.core.bag_reader import BagReader

_ACTIVE_EXPORTER: Exporter | None = None


def _read_request() -> dict[str, Any]:
    """
    Read and decode a JSON request object from standard input.

    Args:
        None

    Returns:
        dict[str, Any]: Parsed request payload, or an empty dict if stdin is
        empty.

    Raises:
        ValueError: If the payload is not a JSON object.
    """
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise ValueError("Bridge request payload must be a JSON object.")
    return payload


def _write_json(data: dict[str, Any]) -> None:
    """
    Write a single JSON line to standard output and flush immediately.

    Args:
        data: JSON-serializable object to write.

    Returns:
        None
    """
    sys.stdout.write(json.dumps(data) + "\n")
    sys.stdout.flush()


def _write_response(data: Any) -> int:
    """
    Write a successful bridge response envelope.

    Args:
        data: Response payload to wrap.

    Returns:
        int: Process exit code for success.
    """
    _write_json({"ok": True, "data": data})
    return 0


def _write_error(message: str, *, exit_code: int = 1) -> int:
    """
    Write an error bridge response envelope.

    Args:
        message: User-displayable error message.
        exit_code: Process exit code to return.

    Returns:
        int: Provided process exit code.
    """
    _write_json({"ok": False, "error": message})
    return exit_code


def _handle_terminate(_signum, _frame) -> None:
    """
    Abort the active export in response to process termination signals.

    Args:
        _signum: Signal number provided by the signal handler.
        _frame: Current stack frame provided by the signal handler.

    Returns:
        None
    """
    global _ACTIVE_EXPORTER
    if _ACTIVE_EXPORTER is not None:
        _ACTIVE_EXPORTER.abort_export()


def _command_inspect_bag() -> int:
    """
    Handle the ``inspect_bag`` bridge command.

    Args:
        None

    Returns:
        int: Process exit code.
    """
    payload = _read_request()
    return _write_response(
        inspect_bag(
            payload["bag_path"],
            base_dir=payload.get("base_dir"),
        )
    )


def _command_list_formats_for_topic_type() -> int:
    """
    Handle the ``list_formats_for_topic_type`` bridge command.

    Args:
        None

    Returns:
        int: Process exit code.
    """
    payload = _read_request()
    return _write_response(list_formats_for_topic_type(payload["topic_type"]))


def _command_validate_export_config() -> int:
    """
    Handle the ``validate_export_config`` bridge command.

    Args:
        None

    Returns:
        int: Process exit code.
    """
    payload = _read_request()
    config, global_config = validate_export_config(
        payload["bag_path"],
        payload.get("topic_configs", {}),
        payload.get("global_config", {}),
        selected_topics=payload.get("selected_topics", []),
        base_dir=payload.get("base_dir"),
    )
    return _write_response({"topic_configs": config, "global_config": global_config})


def _command_run_export() -> int:
    """
    Handle the ``run_export`` bridge command.

    Reads the export request, validates and normalizes the config, executes the
    export, and emits NDJSON progress/completion/error events on stdout.

    Args:
        None

    Returns:
        int: Process exit code.
    """
    global _ACTIVE_EXPORTER

    payload = _read_request()
    config, global_config = validate_export_config(
        payload["bag_path"],
        payload.get("topic_configs", {}),
        payload.get("global_config", {}),
        selected_topics=payload.get("selected_topics", []),
        base_dir=payload.get("base_dir"),
    )

    resolved_path, _ = resolve_bag_path(payload["bag_path"])
    bag_reader = BagReader(resolved_path)

    def progress(current: int, total: int) -> None:
        """
        Emit one progress event for the active export.

        Args:
            current: Completed work units.
            total: Total work units.

        Returns:
            None
        """
        percent = 0 if total <= 0 else int((current / total) * 100)
        _write_json(
            {
                "type": "progress",
                "current": current,
                "total": total,
                "percent": percent,
            }
        )

    signal.signal(signal.SIGTERM, _handle_terminate)
    signal.signal(signal.SIGINT, _handle_terminate)

    try:
        _ACTIVE_EXPORTER = Exporter(bag_reader, config, global_config, progress_callback=progress)
        _ACTIVE_EXPORTER.run()
        _write_json({"type": "completed"})
        return 0
    except Exception as exc:
        _write_json({"type": "error", "message": str(exc)})
        return 1
    finally:
        _ACTIVE_EXPORTER = None


_COMMANDS = {
    "inspect_bag": _command_inspect_bag,
    "list_formats_for_topic_type": _command_list_formats_for_topic_type,
    "validate_export_config": _command_validate_export_config,
    "run_export": _command_run_export,
}


def main(argv: list[str] | None = None) -> int:
    """
    Execute the requested bridge command.

    Args:
        argv: Optional command-line argument list.

    Returns:
        int: Process exit code.
    """
    argv = argv if argv is not None else sys.argv[1:]
    if not argv:
        return _write_error("No bridge command provided.")

    command = argv[0]
    handler = _COMMANDS.get(command)
    if handler is None:
        return _write_error(f"Unsupported bridge command '{command}'.")

    try:
        return handler()
    except Exception as exc:
        return _write_error(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
