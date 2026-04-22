from launch import LaunchDescription
from launch_ros.actions import Node
import os
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():

    pkg_path = get_package_share_directory('ros2_imu_demo')
    urdf_path = os.path.join(pkg_path, 'urdf', 'imu.urdf')
    rviz_config_path = os.path.join(pkg_path, 'rviz', 'config.rviz')

    return LaunchDescription([

        Node(
            package='ros2_imu_demo',
            executable='imu_listener',
            name='imu_listener'
        ),

        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            arguments=[urdf_path]
        ),

        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', rviz_config_path],
            output='screen'
        ),
    ])