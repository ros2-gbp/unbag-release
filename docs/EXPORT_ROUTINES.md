# Export Routines

Export routines define how messages are exported from ROS 2 bag files to desired output formats. The tool comes with a comprehensive set of predefined routines for **all** message types and formats.

Need support for a custom message type or format? No problem! You can easily create and install your own export routines.

## Table of Contents

- [Built-in Export Routines](#built-in-export-routines)
  - [Specialized Routines](#specialized-routines)
  - [Generic Routines](#generic-routines)
- [Custom Export Routines](#custom-export-routines)
  - [Creating Custom Routines](#creating-custom-routines)
  - [Installing Routines](#installing-routines)
  - [Uninstalling Routines](#uninstalling-routines)

## Built-in Export Routines

### Specialized Routines

These routines are optimized for specific message types and formats:

| Identifier(s)                  | Topic(s)                                                      | Description                                                                                                                     |
| ------------------------------ | ------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| **image/png**                  | `sensor_msgs/msg/Image`<br> `sensor_msgs/msg/CompressedImage` | Exports images via openCV to PNG.                                                                                               |  
| **image/jpeg**                 | `sensor_msgs/msg/Image`<br> `sensor_msgs/msg/CompressedImage` | Exports images via openCV to JPEG.                                                                                              |
| **video/mp4**                  | `sensor_msgs/msg/Image`<br> `sensor_msgs/msg/CompressedImage` | Exports image sequences via openCV to MP4.                                                                                      |
| **video/avi**                  | `sensor_msgs/msg/Image`<br> `sensor_msgs/msg/CompressedImage` | Exports image sequences via openCV to AVI.                                                                                      |
| **pointcloud/pkl**             | `sensor_msgs/msg/PointCloud2`                                 | Serializes the entire `PointCloud2` message object using Python’s `pickle`, producing a `.pkl` file.                            |
| **pointcloud/xyz**             | `sensor_msgs/msg/PointCloud2`                                 | Unpacks each point’s x, y, z floats from the binary buffer and writes one `x y z` line per point into a plain `.xyz` text file. |
| **pointcloud/pcd**             | `sensor_msgs/msg/PointCloud2`                                 | Constructs a PCD v0.7 file and writes binary point data* in PCD format to a `.pcd` file.                                        |
| **pointcloud/pcd_compressed**  | `sensor_msgs/msg/PointCloud2`                                 | Constructs a PCD v0.7 file and writes compressed binary point data* in PCD format to a `.pcd` file.                             |
| **pointcloud/pcd_ascii**       | `sensor_msgs/msg/PointCloud2`                                 | Constructs a PCD v0.7 file and writes ASCII point data* in PCD format to a `.pcd` file.                                         |

⚠️ **Note:** Point data in PCD files is written with all fields that are present in the `PointCloud2` message. Some programs do not support arbitrary fields in PCD files. If you need to export only specific fields, you can use the `remove_fields` processor to drop unwanted fields before exporting. See the [Processors documentation](PROCESSORS.md) for more information.

### Generic Routines

In addition to these specialized routines, there are also generic routines for exporting any message type to common formats. They share the same base identifier (e.g. `table/csv`) and can operate either in single-file or multi-file mode. When both modes are available, selecting the base identifier defaults to the multi-file variant.

| Identifier    | Topic(s)             | `@single_file` Description                                                      | `@multi_file` Description                                                         |
| ------------- | -------------------- | ------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| **table/csv** | *any message type*   | Flattens fields, writes header + one row per message into a single `.csv` file. | Flattens fields, writes header + one message per file into separate `.csv` files. |
| **text/json** | *any message type*   | All messages in one `.json` file as a map keyed by timestamp.                   | One `.json` file per message.                                                     |
| **text/yaml** | *any message type*   | One `.yaml` document containing all messages in a single `.yaml` file.          | One `.yaml` document per message.                                                 |

💡 **Pro Tip**: Use just the base identifier (e.g. `table/csv`) to pick the default behaviour. Append `@single_file` or `@multi_file` to force a specific mode when both are supported.

## Custom Export Routines

Your message type or output format is not supported by default? No problem! You can add your own export routines to handle custom message types or output formats.

### Creating Custom Routines

Routines are defined using the `@ExportRoutine` decorator:

```python
from pathlib import Path                                                          # import Path from pathlib for file path handling
from ros2_unbag.core.routines.base import ExportRoutine                           # import the base class
# you can also import other packages here - e.g., numpy, cv2, etc.

@ExportRoutine("sensor_msgs/msg/PointCloud2", ["pointcloud/xyz"], mode=ExportMode.MULTI_FILE)
def export_pointcloud_xyz(msg, path: Path, fmt: str, metadata: ExportMetadata):   # define the export routine function, the name of the function does not matter
    """
    Export PointCloud2 message as an XYZ text file by unpacking x, y, z floats from each point and writing lines.

    Args:
        msg: PointCloud2 message instance.
        path: Output file path (without extension).
        fmt: Export format string (default "pointcloud/xyz").
        metadata: Export metadata including message index and max index.

    Returns:
        None
    """
    with open(path + ".xyz", 'w') as f:                                            # define your custom logic to export the message
        for i in range(0, len(msg.data), msg.point_step):
            x, y, z = struct.unpack_from("fff", msg.data, offset=i)
            f.write(f"{x} {y} {z}\n")
```

#### Decorator Attributes

The `ExportRoutine` decorator accepts the following parameters:

- **`msg_types`**: The message types that this routine can handle. Can be a single type or a list of types. Note that the message type must be installed in the system (available in the ROS 2 environment).
- **`formats`**: The output formats that this routine supports. Can be a single format or a list of formats.
- **`mode`**: Specifies the export mode — `SINGLE_FILE` or `MULTI_FILE`. This determines whether the routine is designed for exporting data into a single file or multiple files. While this setting affects parallelization and naming conventions, you must implement the logic for single file exports yourself if you choose `SINGLE_FILE` mode (e.g., appending data to the same file during each function call).

💡 **Tip**: A template for creating custom export routines is available in the `templates` directory of the repository. You can copy it and modify it to suit your needs.

### Installing Routines

You can import your own routines permanently by calling:

```bash 
ros2 unbag --install-routine <path_to_your_routine_file>
```

Alternatively, use them only temporarily by specifying the `--use-routine` option when starting the program. This works in both the GUI and CLI versions:

```bash
ros2 unbag --use-routine <path_to_your_routine_file>
```

### Uninstalling Routines

If you installed a routine and no longer need it, you can delete it by calling:

```bash
ros2 unbag --uninstall-routine
```

You'll be prompted to pick which routine to uninstall.

⚠️ **Caution:** Never use or install new routines that you did not write yourself or that you do not trust. The code gets ingested and executed in the context of the *ros2 unbag* process, which means it can access all data and resources available to the process. This includes reading and writing files, accessing network resources, and more. Always review the code of any routine you use or install.
