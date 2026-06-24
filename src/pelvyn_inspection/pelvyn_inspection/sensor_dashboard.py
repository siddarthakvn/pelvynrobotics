#!/usr/bin/env python3
"""Print live sensor summary for debugging and report screenshots."""

import math

import rclpy
from rclpy.node import Node
from gazebo_msgs.msg import EntityState
from sensor_msgs.msg import Imu, Range, Image
from std_msgs.msg import String
from tf_transformations import euler_from_quaternion


class SensorDashboard(Node):
  def __init__(self):
    super().__init__('sensor_dashboard')
    self.state = None
    self.imu = None
    self.sonar = None
    self.camera_frames = 0
    self.mission_status = 'INIT'

    self.create_subscription(EntityState, '/ucat/state', self.state_cb, 10)
    self.create_subscription(Imu, '/ucat/imu_data', self.imu_cb, 10)
    self.create_subscription(Range, '/sonar/forward', self.sonar_cb, 10)
    self.create_subscription(Image, '/camera/image_raw', self.camera_cb, 10)
    self.create_subscription(String, '/mission/status', self.mission_cb, 10)
    self.create_timer(2.0, self.report)

  def state_cb(self, msg):
    self.state = msg

  def imu_cb(self, msg):
    self.imu = msg

  def sonar_cb(self, msg):
    self.sonar = msg

  def camera_cb(self, _msg):
    self.camera_frames += 1

  def mission_cb(self, msg):
    self.mission_status = msg.data

  def report(self):
    if self.state is None:
      self.get_logger().warn('Waiting for /ucat/state ...')
      return

    p = self.state.pose.position
    q = self.state.pose.orientation
    _, _, yaw = euler_from_quaternion([q.x, q.y, q.z, q.w])
    sonar = self.sonar.range if self.sonar else -1.0
    imu_rate = 0.0
    if self.imu:
      imu_rate = self.imu.angular_velocity.z

    self.get_logger().info(
      f'[{self.mission_status}] '
      f'pos=({p.x:.2f}, {p.y:.2f}, {p.z:.2f}) '
      f'yaw={math.degrees(yaw):.1f}° '
      f'sonar={sonar:.2f}m '
      f'imu_wz={imu_rate:.3f} '
      f'camera_frames={self.camera_frames}'
    )


def main(args=None):
  rclpy.init(args=args)
  node = SensorDashboard()
  rclpy.spin(node)
  node.destroy_node()
  rclpy.shutdown()


if __name__ == '__main__':
  main()
