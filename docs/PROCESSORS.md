# Processors

Processors are used to modify messages before they are exported. They can be applied to specific topics and allow you to perform operations such as filtering, transforming, or enriching the data.

## Table of Contents

- [Built-in Processors](#built-in-processors)
- [Processor Chains](#processor-chains)
- [Custom Processors](#custom-processors)
  - [Creating Custom Processors](#creating-custom-processors)
  - [Installing Processors](#installing-processors)
  - [Uninstalling Processors](#uninstalling-processors)

## Built-in Processors

The following processors are available by default:

| Identifier(s)          | Topic(s)                                                            | Arguments                                                                                                   | Description                                                   |
| ---------------------- | ------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| **field_mapping**      | `sensor_msgs/msg/PointCloud2`                                       | `field_mapping` String in the form `old_field:new_field, ...`                                               | Remaps fields in a PointCloud2 message.                       |
| **remove_fields**      | `sensor_msgs/msg/PointCloud2`                                       | `fields_to_remove` List of field names to remove `field1, ...`                                              | Removes specified fields from PointCloud2.                    |
| **transform**          | `sensor_msgs/msg/PointCloud2`                                       | `translation_x`, `translation_y`, `translation_z`, `rotation_x`, `rotation_y`, `rotation_z`, `rotation_w`   | Applies translation and quaternion rotation to PointCloud2.   |
| **transform_from_yaml**| `sensor_msgs/msg/PointCloud2`                                       | `custom_frame_path` Path to a YAML file with custom frame data                                              | Transforms PointCloud2 to a custom frame.                     |
| **apply_color_map**    | `sensor_msgs/msg/Image` <br> `sensor_msgs/msg/CompressedImage`      | `color_map` Integer specifying cv2 colormap index*.                                                         | Applies a color map to an image.                              |

**Note**: The `color_map` argument is an integer that specifies the OpenCV colormap index. You can find a list of available colormaps in the [OpenCV documentation](https://docs.opencv.org/4.x/d3/d50/group__imgproc__colormap.html).

## Processor Chains

You can chain multiple processors on the same topic. Processors run in the order they are specified, allowing you to build complex processing pipelines.

### CLI Usage

In the CLI, repeat `-p/--processing` for each step:

```bash
ros2 unbag mybag -e /camera/image:image/png -p /camera/image:normalize -p /camera/image:apply_color_map:color_map=2
```

### Configuration File Format

Processors run in the order they are specified. The resulting configuration stores them as an ordered list:

```json
"processors": [
  {"name": "normalize", "args": {}},
  {"name": "apply_color_map", "args": {"color_map": "2"}}
]
```

### GUI Usage

In the GUI, use the **Add Processor** button inside each topic card to append steps, and the arrow buttons to reorder or the close button to remove them.

## Custom Processors

You can define your own processors to implement custom message transformations.

### Creating Custom Processors

Processors are defined using the `@Processor` decorator:

```python
# Import the processor decorator
from ros2_unbag.core.processors.base import Processor

# Define the processor class with the appropriate message types and give it a name
@Processor(["std_msgs/msg/String"], ["your_processor_name"]) 
def your_processor_name(msg, your_parameter: str = "default", your_parameter_2: str = "template"):
    """
    Short description of what the processor does.

    Args:
        msg: The ROS message you want to process.
        your_parameter: Describe the parameter. This will be shown in the UI.
        your_parameter_2: You can add more parameters as needed.

    Returns:
        The return always needs to match the incoming message type.
    """

    # Validate and convert parameter
    try:
        your_parameter = str(your_parameter)
        your_parameter_2 = str(your_parameter_2)
    except ValueError:
        raise ValueError(f"One of the parameters is not valid: {your_parameter}, {your_parameter_2}")

    # Decode ROS message if necessary
    string_msg = msg.data  # Assuming msg is a String message

    # --- Apply your processing here ---
    processed_msg = string_msg.replace(your_parameter, your_parameter_2)

    # Re-encode the image
    msg.data = processed_msg

    return msg
```

#### Decorator Attributes

The `Processor` decorator accepts the following parameters:

- **`msg_types`**: The message types that this processor can handle. Can be a single type or a list of types. Note that the message type must be installed in the system (available in the ROS 2 environment).
- **`name`**: The name of the processor, which is used to identify it in the system.

💡 **Tip**: A template for creating custom processors is available in the `templates` directory of the repository. You can copy it and modify it to suit your needs.

### Installing Processors

You can import your own processors permanently by calling:

```bash
ros2 unbag --install-processor <path_to_your_processor_file>
```

Alternatively, use them only temporarily by specifying the `--use-processor` option when starting the program. This works in both the GUI and CLI versions:

```bash
ros2 unbag --use-processor <path_to_your_processor_file>
```

### Uninstalling Processors

If you installed a processor and no longer need it, you can delete it by calling:

```bash
ros2 unbag --uninstall-processor
```

You'll be prompted to pick which processor to uninstall.

⚠️ **Caution:** Never use or install new processors that you did not write yourself or that you do not trust. The code gets ingested and executed in the context of the *ros2 unbag* process, which means it can access all data and resources available to the process. This includes reading and writing files, accessing network resources, and more. Always review the code of any processor you use or install.