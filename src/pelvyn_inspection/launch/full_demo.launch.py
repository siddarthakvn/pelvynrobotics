import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, TimerAction
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
import xacro


def generate_launch_description():
    eeuv_share = get_package_share_directory('eeuv_sim')
    pelvyn_share = get_package_share_directory('pelvyn_inspection')

    os.environ['GAZEBO_MODEL_PATH'] = os.path.join(eeuv_share, 'models')
    world_path = os.path.join(pelvyn_share, 'worlds', 'inspection_world.world')
    xacro_file = os.path.join(eeuv_share, 'urdf', 'UCAT', 'base.xacro.urdf')

    doc = xacro.parse(open(xacro_file))
    xacro.process_doc(doc)

    use_rviz = LaunchConfiguration('rviz')
    use_camera = LaunchConfiguration('camera')

    return LaunchDescription([
        DeclareLaunchArgument('rviz', default_value='true'),
        DeclareLaunchArgument('camera', default_value='true'),

        ExecuteProcess(
            cmd=[
                'gazebo', '--verbose',
                '-s', 'libgazebo_ros_factory.so',
                '-s', 'libgazebo_ros_init.so',
                '-s', 'libgazebo_ros_force_system.so',
                world_path,
            ],
            output='screen',
        ),

        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            output='screen',
            parameters=[{'robot_description': doc.toxml()}],
        ),

        TimerAction(period=6.0, actions=[
            Node(
                package='gazebo_ros',
                executable='spawn_entity.py',
                arguments=['-topic', 'robot_description', '-entity', 'UCAT',
                           '-x', '-1', '-y', '-1', '-z', '-2.0'],
                output='screen',
            ),
        ]),

        # ONLY stable_mission — no AUVMotion, no moveFins, no mission_controller
        TimerAction(period=10.0, actions=[
            Node(package='pelvyn_inspection', executable='stable_mission', output='screen'),
        ]),

        Node(
            package='rqt_image_view',
            executable='rqt_image_view',
            arguments=['/camera/image_raw'],
            condition=IfCondition(use_camera),
        ),

        TimerAction(period=12.0, actions=[
            Node(
                package='rviz2',
                executable='rviz2',
                arguments=['-d', os.path.join(pelvyn_share, 'rviz', 'mission.rviz')],
                condition=IfCondition(use_rviz),
            ),
        ]),
    ])
