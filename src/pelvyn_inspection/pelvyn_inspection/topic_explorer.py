#!/usr/bin/env python3
"""List active ROS 2 topics — run after eeUVsim launch to map the simulator."""

import rclpy
from rclpy.node import Node


class TopicExplorer(Node):
    def __init__(self):
        super().__init__('topic_explorer')
        self.get_logger().info('Pelvyn inspection — active topics:')
        for name, types in self.get_topic_names_and_types():
            self.get_logger().info(f'  {name}  [{", ".join(types)}]')


def main(args=None):
    rclpy.init(args=args)
    node = TopicExplorer()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
