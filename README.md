# ros2_imu_demo (Micro-ROS IMU Listener)

This package is a ROS 2 listener and visualization bridge for IMU data published from a Micro-ROS ESP32 MPU6050 node.

It subscribes to `/imu/data` and broadcasts TF transforms for visualization in RViz or other ROS tools.

---

## Overview

This project demonstrates:

- ROS 2 IMU subscriber node (`sensor_msgs/msg/Imu`)
- TF2 transform broadcasting from IMU data
- Integration with Micro-ROS ESP32 IMU publisher
- Simple robot model visualization in RViz

This project depends on a companion Micro-ROS ESP32 repository that publishes MPU6050 IMU data to ROS 2.

Required publisher repository:

- https://github.com/kimsniper/micro_ros_mpu6050

---

## Clone Repositories

Clone this listener package:

```bash
cd ~
git clone https://github.com/kimsniper/ros2_imu_demo.git
cd ~/ros2_imu_demo
```

Clone the required Micro-ROS MPU6050 publisher repository:

```bash
cd ~
git clone https://github.com/kimsniper/micro_ros_mpu6050.git
```

---

## Required Dependency Repository

This project is only the ROS 2 listener and visualization component.

To receive IMU data, you must also use the Micro-ROS ESP32 MPU6050 publisher:

- https://github.com/kimsniper/micro_ros_mpu6050

The publisher repository:

- Reads MPU6050 sensor data on ESP32
- Computes orientation data
- Publishes `sensor_msgs/msg/Imu`
- Sends IMU messages to ROS 2 through Micro-ROS

Data published from that repository is consumed by this package through:

```text
/imu/data
```

Without the Micro-ROS MPU6050 publisher running, this listener will not receive any IMU data.

---

## Build Project

```bash
colcon build
```

---

## Source Workspace

```bash
source install/setup.bash
```

---

## Launch

```bash
ros2 launch ros2_imu_demo imu_demo.launch.py
```

---

## ROS 2 IMU Listener Node

### Functionality

The node:

- Subscribes to `/imu/data`
- Reads quaternion orientation
- Broadcasts TF transform between:
  - `world` → `imu_link`

---

### Core Node Code

```cpp
class ImuListener : public rclcpp::Node
{
public:
    ImuListener() : Node("imu_listener")
    {
        tf_broadcaster_ = std::make_shared<tf2_ros::TransformBroadcaster>(this);

        sub_ = this->create_subscription<sensor_msgs::msg::Imu>(
            "/imu/data",
            10,
            std::bind(&ImuListener::imuCallback, this, std::placeholders::_1)
        );
    }

private:
    void imuCallback(const sensor_msgs::msg::Imu::SharedPtr msg)
    {
        geometry_msgs::msg::TransformStamped t;

        t.header.stamp = msg->header.stamp;
        t.header.frame_id = "world";
        t.child_frame_id = "imu_link";

        t.transform.translation.x = 0.0;
        t.transform.translation.y = 0.0;
        t.transform.translation.z = 0.0;

        geometry_msgs::msg::Quaternion q = msg->orientation;

        // IMU orientation correction
        std::swap(q.x, q.y);
        q.x = -q.x;

        t.transform.rotation = q;

        tf_broadcaster_->sendTransform(t);
    }

    rclcpp::Subscription<sensor_msgs::msg::Imu>::SharedPtr sub_;
    std::shared_ptr<tf2_ros::TransformBroadcaster> tf_broadcaster_;
};
```

---

## URDF Model

This robot model represents the IMU frame in RViz.

```xml
<robot name="imu">

  <link name="world"/>

  <link name="imu_link">

    <visual>
      <origin xyz="0 0 0" rpy="0 0 -1.507"/>
      <geometry>
        <mesh filename="package://ros2_imu_demo/meshes/plane.stl" scale=".005 .005 .005"/>
      </geometry>
      <material name="blue">
        <color rgba="0.8 0.8 0.8 0.5"/>
      </material>
    </visual>

  </link>

  <joint name="world_to_imu" type="fixed">
    <parent link="world"/>
    <child link="imu_link"/>
    <origin xyz="0 0 0" rpy="0 0 0"/>
  </joint>

</robot>
```

---

## Data Flow

```text
MPU6050 Sensor
        ↓
ESP32 Micro-ROS Node
(micro_ros_mpu6050)
        ↓
Micro-ROS Agent
        ↓
/imu/data (ROS 2 topic)
        ↓
ros2_imu_demo listener node
        ↓
TF broadcaster (world → imu_link)
        ↓
RViz visualization
```

---

## Usage Notes

- Ensure Micro-ROS agent is running before ESP32 publishes data
- IMU quaternion may require axis correction depending on hardware mounting
- The node swaps and inverts quaternion axes for correct orientation alignment:

```cpp
std::swap(q.x, q.y);
q.x = -q.x;
```

---

## Micro-ROS Dependency Reminder

Before running this package:

1. Flash and run the ESP32 firmware from:

   https://github.com/kimsniper/micro_ros_mpu6050

2. Start the Micro-ROS Agent:

```bash
docker run -it --rm --net=host microros/micro-ros-agent:humble udp4 --port 8888 -v6
```

3. Verify IMU messages are being published:

```bash
ros2 topic echo /imu/data
```

4. Launch this package:

```bash
ros2 launch ros2_imu_demo imu_demo.launch.py
```

---

## Topics

### Subscribed

- `/imu/data` (`sensor_msgs/msg/Imu`)

### Published

- TF: `/tf` (world → imu_link)

---

## Visualization

Open RViz2:

```bash
rviz2
```

Add:

- TF
- RobotModel (optional)
- IMU display

---

### Working Demo Video
![Demo](./images/imu_demo.gif)


Imu Demo: https://www.linkedin.com/feed/update/urn:li:activity:7453299633088540672/

---

## License

BSD 3-Clause License

Copyright (c) 2026 Mezael Docoy
