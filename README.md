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

---

## Clone Repository

```bash
cd ~
git clone https://github.com/kimsniper/ros2_imu_demo.git
cd ~/ros2_imu_demo
```

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

```
MPU6050 (ESP32 Micro-ROS)
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

Start agent before running ESP32:

```bash
docker run -it --rm --net=host microros/micro-ros-agent:humble udp4 --port 8888 -v6
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

## License

BSD 3-Clause License

Copyright (c) 2026 Mezael Docoy
