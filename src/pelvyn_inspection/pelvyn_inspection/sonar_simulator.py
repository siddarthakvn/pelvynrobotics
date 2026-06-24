#!/usr/bin/env python3
"""Simulated forward-looking sonar from robot pose and known obstacles."""

import math

import rclpy
from rclpy.node import Node
from gazebo_msgs.msg import EntityState
from sensor_msgs.msg import Range
from tf_transformations import euler_from_quaternion

from pelvyn_inspection.mission_config import OBSTACLES


class SonarSimulator(Node):
    MAX_RANGE = 12.0
    FIELD_OF_VIEW = 0.35

    def __init__(self):
        super().__init__('sonar_simulator')
        self.pose = None
        self.create_subscription(EntityState, '/ucat/state', self.state_cb, 10)
        self.pub = self.create_publisher(Range, '/sonar/forward', 10)
        self.create_timer(0.1, self.publish_range)

    def state_cb(self, msg: EntityState):
        self.pose = msg

    def raycast(self, x, y, yaw):
        min_range = self.MAX_RANGE
        step = 0.15
        distance = step
        while distance <= self.MAX_RANGE:
            rx = x + distance * math.cos(yaw)
            ry = y + distance * math.sin(yaw)
            for ox, oy, radius in OBSTACLES:
                if math.hypot(rx - ox, ry - oy) <= radius + 0.25:
                    min_range = min(min_range, distance)
                    return min_range
            distance += step
        return min_range

    def publish_range(self):
        msg = Range()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'sonars'
        msg.radiation_type = Range.ULTRASOUND
        msg.field_of_view = self.FIELD_OF_VIEW
        msg.min_range = 0.1
        msg.max_range = self.MAX_RANGE

        if self.pose is None:
            msg.range = self.MAX_RANGE
        else:
            q = self.pose.pose.orientation
            _, _, yaw = euler_from_quaternion([q.x, q.y, q.z, q.w])
            msg.range = float(self.raycast(
                self.pose.pose.position.x,
                self.pose.pose.position.y,
                yaw,
            ))

        self.pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = SonarSimulator()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
