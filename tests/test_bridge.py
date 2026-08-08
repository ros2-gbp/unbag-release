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

import io
import json
import numpy as np
from pathlib import Path
import sys
import types

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def _install_ros_stubs():
    tf2_msgs = types.ModuleType("tf2_msgs")
    tf2_msgs_msg = types.ModuleType("tf2_msgs.msg")
    tf2_msgs_msg.TFMessage = type("TFMessage", (), {})
    tf2_msgs.msg = tf2_msgs_msg
    sys.modules.setdefault("tf2_msgs", tf2_msgs)
    sys.modules.setdefault("tf2_msgs.msg", tf2_msgs_msg)

    rclpy = types.ModuleType("rclpy")
    rclpy_serialization = types.ModuleType("rclpy.serialization")
    rclpy_serialization.deserialize_message = lambda data, msg_type: data
    rclpy.serialization = rclpy_serialization
    sys.modules.setdefault("rclpy", rclpy)
    sys.modules.setdefault("rclpy.serialization", rclpy_serialization)

    rosbag2_py = types.ModuleType("rosbag2_py")
    rosbag2_py.ConverterOptions = object
    rosbag2_py.SequentialReader = object
    rosbag2_py.StorageFilter = object
    rosbag2_py.StorageOptions = object
    sys.modules.setdefault("rosbag2_py", rosbag2_py)

    rosidl_runtime_py = types.ModuleType("rosidl_runtime_py")
    rosidl_runtime_py.message_to_ordereddict = lambda msg: {}
    rosidl_runtime_py.message_to_yaml = lambda msg: ""
    rosidl_runtime_py_utilities = types.ModuleType("rosidl_runtime_py.utilities")
    rosidl_runtime_py_utilities.get_message = lambda name: name
    rosidl_runtime_py.utilities = rosidl_runtime_py_utilities
    sys.modules.setdefault("rosidl_runtime_py", rosidl_runtime_py)
    sys.modules.setdefault("rosidl_runtime_py.utilities", rosidl_runtime_py_utilities)

    sensor_msgs = types.ModuleType("sensor_msgs")
    sensor_msgs_msg = types.ModuleType("sensor_msgs.msg")
    sensor_msgs_msg.CompressedImage = type("CompressedImage", (), {})
    sensor_msgs_msg.Image = type("Image", (), {})
    sensor_msgs_msg.PointCloud2 = type("PointCloud2", (), {})
    sensor_msgs_msg.PointField = type(
        "PointField",
        (),
        {
            "INT8": 1,
            "UINT8": 2,
            "INT16": 3,
            "UINT16": 4,
            "INT32": 5,
            "UINT32": 6,
            "FLOAT32": 7,
            "FLOAT64": 8,
        },
    )
    sensor_msgs.msg = sensor_msgs_msg
    sys.modules.setdefault("sensor_msgs", sensor_msgs)
    sys.modules.setdefault("sensor_msgs.msg", sensor_msgs_msg)

    cv2 = types.ModuleType("cv2")
    cv2.IMREAD_GRAYSCALE = 0
    cv2.IMREAD_UNCHANGED = 0
    cv2.NORM_MINMAX = 0
    cv2.COLOR_GRAY2BGR = 1
    cv2.COLOR_RGB2BGR = 2
    cv2.COLOR_BGRA2BGR = 3
    cv2.COLOR_RGBA2BGR = 4
    cv2.COLOR_YUV2BGR_YUY2 = 5
    cv2.COLOR_BAYER_RG2BGR = 6
    cv2.COLOR_BAYER_BG2BGR = 7
    cv2.COLOR_BAYER_GB2BGR = 8
    cv2.COLOR_BAYER_GR2BGR = 9
    cv2.imdecode = lambda *args, **kwargs: None
    cv2.normalize = lambda image, *_args, **_kwargs: image
    cv2.applyColorMap = lambda image, *_args, **_kwargs: image
    cv2.imencode = lambda *_args, **_kwargs: (True, types.SimpleNamespace(tobytes=lambda: b""))
    def _cvt_color(image, code, *_args, **_kwargs):
        if code == cv2.COLOR_RGB2BGR:
            return image[..., ::-1]
        if code == cv2.COLOR_BGRA2BGR:
            return image[..., :3]
        if code == cv2.COLOR_RGBA2BGR:
            return image[..., [2, 1, 0]]
        if code == cv2.COLOR_GRAY2BGR:
            return np.repeat(image[..., None], 3, axis=2)
        if code == cv2.COLOR_YUV2BGR_YUY2:
            return np.zeros((image.shape[0], image.shape[1], 3), dtype=image.dtype)
        if code in {
            cv2.COLOR_BAYER_RG2BGR,
            cv2.COLOR_BAYER_BG2BGR,
            cv2.COLOR_BAYER_GB2BGR,
            cv2.COLOR_BAYER_GR2BGR,
        }:
            return np.zeros((image.shape[0], image.shape[1], 3), dtype=image.dtype)
        return image
    cv2.cvtColor = _cvt_color
    cv2.imwrite = lambda *_args, **_kwargs: True
    cv2.VideoWriter_fourcc = lambda *args: 0
    cv2.VideoWriter = lambda *args, **kwargs: types.SimpleNamespace(
        isOpened=lambda: True,
        write=lambda frame: None,
        release=lambda: None,
    )
    sys.modules.setdefault("cv2", cv2)


_install_ros_stubs()

from ros2_unbag import bridge  # noqa: E402


def test_inspect_bag_command(monkeypatch):
    monkeypatch.setattr(
        bridge,
        "inspect_bag",
        lambda bag_path, base_dir=None: {
            "bag_path": bag_path,
            "base_dir": base_dir,
            "topics": [],
        },
    )
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps({"bag_path": "/tmp/demo", "base_dir": "/tmp/out"})))
    stdout = io.StringIO()
    monkeypatch.setattr(sys, "stdout", stdout)

    rc = bridge.main(["inspect_bag"])

    assert rc == 0
    payload = json.loads(stdout.getvalue())
    assert payload["ok"] is True
    assert payload["data"]["bag_path"] == "/tmp/demo"
    assert payload["data"]["base_dir"] == "/tmp/out"


def test_validate_export_config_command(monkeypatch):
    monkeypatch.setattr(
        bridge,
        "validate_export_config",
        lambda *args, **kwargs: (
            {"/topic": {"format": "csv", "path": "/tmp", "subfolder": "topic", "naming": "%name_%index"}},
            {"cpu_percentage": 50.0},
        ),
    )
    monkeypatch.setattr(
        sys,
        "stdin",
        io.StringIO(
            json.dumps(
                {
                    "bag_path": "/tmp/demo",
                    "topic_configs": {},
                    "global_config": {},
                    "selected_topics": ["/topic"],
                }
            )
        ),
    )
    stdout = io.StringIO()
    monkeypatch.setattr(sys, "stdout", stdout)

    rc = bridge.main(["validate_export_config"])

    assert rc == 0
    payload = json.loads(stdout.getvalue())
    assert payload["ok"] is True
    assert payload["data"]["global_config"]["cpu_percentage"] == 50.0
    assert payload["data"]["topic_configs"]["/topic"]["format"] == "csv"


def test_run_export_emits_progress_and_completed(monkeypatch):
    class FakeExporter:
        def __init__(self, bag_reader, config, global_config, progress_callback=None):
            self.progress_callback = progress_callback

        def run(self):
            self.progress_callback(1, 4)
            self.progress_callback(4, 4)

    class FakeBagReader:
        def __init__(self, bag_path):
            self.bag_path = bag_path

    monkeypatch.setattr(
        bridge,
        "validate_export_config",
        lambda *args, **kwargs: (
            {"/topic": {"format": "csv", "path": "/tmp", "subfolder": "topic", "naming": "%name_%index"}},
            {"cpu_percentage": 50.0},
        ),
    )
    monkeypatch.setattr(bridge, "resolve_bag_path", lambda path: (path, "sqlite3"))
    monkeypatch.setattr(bridge, "BagReader", FakeBagReader)
    monkeypatch.setattr(bridge, "Exporter", FakeExporter)
    monkeypatch.setattr(
        sys,
        "stdin",
        io.StringIO(
            json.dumps(
                {
                    "bag_path": "/tmp/demo",
                    "topic_configs": {},
                    "global_config": {},
                    "selected_topics": ["/topic"],
                }
            )
        ),
    )
    stdout = io.StringIO()
    monkeypatch.setattr(sys, "stdout", stdout)

    rc = bridge.main(["run_export"])

    assert rc == 0
    events = [json.loads(line) for line in stdout.getvalue().splitlines()]
    assert events[0]["type"] == "progress"
    assert events[-1]["type"] == "completed"


def test_cancel_export_is_not_supported(monkeypatch):
    stdout = io.StringIO()
    monkeypatch.setattr(sys, "stdout", stdout)

    rc = bridge.main(["cancel_export"])

    assert rc == 1
    payload = json.loads(stdout.getvalue())
    assert payload["ok"] is False
    assert "Unsupported bridge command" in payload["error"]
