#!/usr/bin/env python3
"""Manual UCAT fin commands for testing eeUVsim."""

import rclpy
from rclpy.node import Node
from eeuv_sim_interfaces.msg import Flippers, Flipper


class FinTeleop(Node):
    """Publish fin oscillation commands to /hw/flippers_cmd."""

    FIN_NAMES = ['FR (front-right)', 'BR (back-right)', 'BL (back-left)', 'FL (front-left)']

    def __init__(self):
        super().__init__('fin_teleop')
        self.pub = self.create_publisher(Flippers, '/hw/flippers_cmd', 10)
        self.timer = self.create_timer(0.1, self.publish_cmd)
        self.mode = 'stop'
        self.get_logger().info(
            'Fin teleop ready. Keys: f=forward, s=stop, l=left, r=right, u=surface, d=dive, q=quit'
        )

    def make_flippers(self, amplitude=0.0, frequency=1.0, zero_direction=0.0):
        msg = Flippers()
        for i in range(4):
            fin = Flipper()
            fin.motor_number = bytes([i])
            fin.frequency = float(frequency)
            fin.zero_direction = float(zero_direction)
            fin.amplitude = float(amplitude)
            fin.phase_offset = 0.0
            msg.flippers.append(fin)
        return msg

    def publish_cmd(self):
        presets = {
            'stop': self.make_flippers(0.0, 0.0, 0.0),
            # Forward: all fins oscillate with small amplitude
            'forward': self.make_flippers(0.35, 1.2, 0.0),
            'left': self.make_flippers(0.30, 1.0, 0.5),
            'right': self.make_flippers(0.30, 1.0, -0.5),
            'surface': self.make_flippers(0.25, 0.8, 1.2),
            'dive': self.make_flippers(0.25, 0.8, -1.2),
        }
        self.pub.publish(presets.get(self.mode, presets['stop']))

    def set_mode(self, mode: str):
        self.mode = mode
        self.get_logger().info(f'Mode: {mode}')


def main():
    import sys
    import termios
    import tty
    import select

    rclpy.init()
    node = FinTeleop()

    old_settings = termios.tcgetattr(sys.stdin)
    try:
        tty.setcbreak(sys.stdin.fileno())
        while rclpy.ok():
            rclpy.spin_once(node, timeout_sec=0.05)
            if select.select([sys.stdin], [], [], 0)[0]:
                key = sys.stdin.read(1)
                if key == 'q':
                    break
                mapping = {
                    'f': 'forward',
                    's': 'stop',
                    'l': 'left',
                    'r': 'right',
                    'u': 'surface',
                    'd': 'dive',
                }
                if key in mapping:
                    node.set_mode(mapping[key])
    finally:
        node.set_mode('stop')
        rclpy.spin_once(node, timeout_sec=0.1)
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
