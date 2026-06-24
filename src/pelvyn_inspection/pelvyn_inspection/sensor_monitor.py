#!/usr/bin/env python3
"""Print live sensor data to terminal for demo recording."""

import math

import rclpy
from rclpy.node import Node
from gazebo_msgs.msg import EntityState
from sensor_msgs.msg import Imu, Range, Image
from std_msgs.msg import String
from tf_transformations import euler_from_quaternion


class SensorMonitor(Node):
    def __init__(self):
        super().__init__('sensor_monitor')
        self.state = None
        self.imu = None
        self.sonar = None
        self.mission = 'WAITING'
        self.camera_count = 0

        self.create_subscription(EntityState, '/ucat/state', lambda m: setattr(self, 'state', m), 10)
        self.create_subscription(Imu, '/ucat/imu_data', lambda m: setattr(self, 'imu', m), 10)
        self.create_subscription(Range, '/sonar/forward', lambda m: setattr(self, 'sonar', m), 10)
        self.create_subscription(String, '/mission/status', self.mission_cb, 10)
        self.create_subscription(
            Image, '/camera/image_raw',
            lambda _: setattr(self, 'camera_count', self.camera_count + 1),
            10,
        )
        self.create_timer(1.0, self.print_status)
        self.get_logger().info('Sensor monitor started — printing every 1 second')

    def mission_cb(self, msg):
        self.mission = msg.data

    def print_status(self):
        if self.state is None:
            self.get_logger().warn('Waiting for sensors...')
            return

        p = self.state.pose.position
        q = self.state.pose.orientation
        roll, pitch, yaw = euler_from_quaternion([q.x, q.y, q.z, q.w])
        sonar = self.sonar.range if self.sonar else float('nan')

        if self.imu:
            imu_str = (
                f'accel=({self.imu.linear_acceleration.x:.2f}, '
                f'{self.imu.linear_acceleration.y:.2f}, '
                f'{self.imu.linear_acceleration.z:.2f}) '
                f'gyro_z={self.imu.angular_velocity.z:.3f}'
            )
        else:
            imu_str = 'no data'

        obstacle_alert = '*** OBSTACLE CLOSE ***' if sonar < 2.5 else 'path clear'

        line = (
            f'\n'
            f'========== AUV SENSOR DASHBOARD ==========\n'
            f'  MISSION   : {self.mission}\n'
            f'  POSITION  : x={p.x:.2f}  y={p.y:.2f}  z={p.z:.2f} m\n'
            f'  HEADING   : yaw={math.degrees(yaw):.1f} deg\n'
            f'  SONAR     : {sonar:.2f} m  [{obstacle_alert}]\n'
            f'  IMU       : {imu_str}\n'
            f'  CAMERA    : {self.camera_count} frames received\n'
            f'=========================================='
        )
        print(line, flush=True)


def main(args=None):
    rclpy.init(args=args)
    node = SensorMonitor()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
