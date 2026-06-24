#!/usr/bin/env python3
"""Autonomous waypoint navigation with sonar-based obstacle avoidance."""

import math

import rclpy
from rclpy.node import Node
from eeuv_sim_interfaces.msg import Flippers, Flipper
from gazebo_msgs.msg import EntityState
from nav_msgs.msg import Path
from geometry_msgs.msg import PoseStamped
from sensor_msgs.msg import Range
from std_msgs.msg import Bool, String
from tf_transformations import euler_from_quaternion

from pelvyn_inspection.mission_config import (
    WAYPOINTS,
    TARGET_DEPTH,
    WAYPOINT_TOLERANCE,
    SONAR_THRESHOLD,
)

# UCAT fin oscillation defaults (from eeUVsim RL / dynamics yaml)
FIN_FREQUENCY = 2.0
PHASE_OFFSETS = [0.0, 3.14159, 0.0, 3.14159]
MAX_DEPTH = -4.0  # emergency surface below this [m]


def make_flippers_ucat(amplitudes, zero_directions):
    msg = Flippers()
    for i in range(4):
        fin = Flipper()
        fin.motor_number = bytes([i])
        fin.frequency = FIN_FREQUENCY
        fin.zero_direction = float(zero_directions[i])
        fin.amplitude = float(amplitudes[i])
        fin.phase_offset = float(PHASE_OFFSETS[i])
        msg.flippers.append(fin)
    return msg


def forward_fins(heading_steer=0.0, depth_boost=0.0):
    """FR, BR, BL, FL — surgeMap [1,-1,-1,1] needs asymmetric drive."""
    steer = max(-0.6, min(0.6, heading_steer))
    depth = max(-0.8, min(0.8, depth_boost))
    amps = [0.82, 0.68, 0.68, 0.82]
    zds = [
        0.15 + steer + depth,
        -0.15 - steer + depth,
        -0.15 + steer + depth,
        0.15 - steer + depth,
    ]
    return make_flippers_ucat(amps, zds)


def surface_fins(strength=1.0):
    """Strong heave/pitch-up pattern to counter negative buoyancy."""
    s = max(0.4, min(1.0, strength))
    amp = 0.85 * s
    zd = 1.1 * s
    return make_flippers_ucat(
        [amp, amp, amp, amp],
        [zd, -zd, -zd, zd],
    )


def stop_fins():
    return make_flippers_ucat([0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0])


class MissionController(Node):
    def __init__(self):
        super().__init__('mission_controller')
        self.pose = None
        self.sonar_range = 12.0
        self.wp_index = 0
        self.avoid_timer = 0.0
        self.reset_sent = False

        self.pub_fins = self.create_publisher(Flippers, '/hw/flippers_cmd', 10)
        self.pub_reset = self.create_publisher(Bool, '/ucat/reset', 10)
        self.pub_path = self.create_publisher(Path, '/mission/path', 10)
        self.pub_status = self.create_publisher(String, '/mission/status', 10)

        self.create_subscription(EntityState, '/ucat/state', self.state_cb, 10)
        self.create_subscription(Range, '/sonar/forward', self.sonar_cb, 10)

        self.create_timer(0.1, self.control_loop)
        self.create_timer(2.0, self.publish_path)
        self.publish_path()
        self.get_logger().info('Mission controller active')

    def state_cb(self, msg: EntityState):
        self.pose = msg

    def sonar_cb(self, msg: Range):
        self.sonar_range = msg.range

    def publish_path(self):
        path = Path()
        path.header.stamp = self.get_clock().now().to_msg()
        path.header.frame_id = 'world'
        for x, y, z in WAYPOINTS:
            pose = PoseStamped()
            pose.header = path.header
            pose.pose.position.x = x
            pose.pose.position.y = y
            pose.pose.position.z = z
            pose.pose.orientation.w = 1.0
            path.poses.append(pose)
        self.pub_path.publish(path)

    def trigger_reset(self):
        if not self.reset_sent:
            self.pub_reset.publish(Bool(data=True))
            self.reset_sent = True
            self.get_logger().warn('Depth limit exceeded — resetting robot to dock')

    def control_loop(self):
        if self.pose is None:
            self.pub_fins.publish(forward_fins(0.0, 0.2))
            return

        x = self.pose.pose.position.x
        y = self.pose.pose.position.y
        z = self.pose.pose.position.z
        q = self.pose.pose.orientation
        _, _, yaw = euler_from_quaternion([q.x, q.y, q.z, q.w])

        status = String()

        # Emergency: too deep — reset once and surface hard
        if z < MAX_DEPTH:
            self.trigger_reset()
            self.pub_fins.publish(surface_fins(1.0))
            status.data = f'EMERGENCY_SURFACE z={z:.2f}'
            self.pub_status.publish(status)
            if z > TARGET_DEPTH - 1.0:
                self.reset_sent = False
            return

        # Depth correction: more negative Z = deeper underwater
        depth_err = z - TARGET_DEPTH
        if depth_err < -0.5:
            strength = min(1.0, 0.5 + abs(depth_err) * 0.4)
            self.pub_fins.publish(surface_fins(strength))
            status.data = f'DEPTH_CORRECT z={z:.2f} target={TARGET_DEPTH}'
            self.pub_status.publish(status)
            return

        depth_boost = max(-0.3, min(0.3, -depth_err * 0.5))

        if self.sonar_range < SONAR_THRESHOLD:
            self.avoid_timer = 2.5
            turn = 0.5 if (self.wp_index % 2 == 0) else -0.5
            fins = forward_fins(turn, depth_boost)
            status.data = f'AVOID sonar={self.sonar_range:.2f}m'
        elif self.avoid_timer > 0.0:
            self.avoid_timer -= 0.1
            fins = forward_fins(0.0, depth_boost)
            status.data = 'AVOID_RECOVER'
        else:
            gx, gy, _ = WAYPOINTS[self.wp_index]
            dx = gx - x
            dy = gy - y
            dist = math.hypot(dx, dy)

            if dist < WAYPOINT_TOLERANCE:
                self.wp_index = (self.wp_index + 1) % len(WAYPOINTS)
                self.get_logger().info(f'Waypoint {self.wp_index} reached')
                gx, gy, _ = WAYPOINTS[self.wp_index]
                dx = gx - x
                dy = gy - y
                dist = math.hypot(dx, dy)

            desired_heading = math.atan2(dy, dx)
            heading_error = math.atan2(
                math.sin(desired_heading - yaw),
                math.cos(desired_heading - yaw),
            )
            nav_steer = max(-0.6, min(0.6, 1.8 * heading_error))
            fins = forward_fins(nav_steer, depth_boost)
            status.data = (
                f'NAVIGATE wp={self.wp_index} dist={dist:.1f}m '
                f'z={z:.2f} sonar={self.sonar_range:.1f}m'
            )

        self.pub_fins.publish(fins)
        self.pub_status.publish(status)


def main(args=None):
    rclpy.init(args=args)
    node = MissionController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
