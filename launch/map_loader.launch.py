import os
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():

    # ✅ Change these two values according to your setup
    map_file = '/home/rishi/eric_assig/src/l1-rishishendre/testbed_bringup/maps/testbed_world.yaml'
    
    map_server_node = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[{
            'use_sim_time': True,       # False if using real robot
            'yaml_filename': map_file
        }]
    )

    lifecycle_manager_node = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_map',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'autostart': True,
            'node_names': ['map_server']
        }]
    )

    return LaunchDescription([
        map_server_node,
        lifecycle_manager_node,
    ])