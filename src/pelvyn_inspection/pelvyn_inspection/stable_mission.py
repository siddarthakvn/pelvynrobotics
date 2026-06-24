#!/usr/bin/env python3
"""Stable kinematic AUV mission with sonar obstacle avoidance."""

import math

import rclpy
from rclpy.node import Node
from gazebo_msgs.msg import EntityState
from gazebo_msgs.srv import SetEntityState
from geometry_msgs.msg import PoseStamped, TransformStamped
from nav_msgs.msg import Odometry, Path
from sensor_msgs.msg import Imu, Range
from std_msgs.msg import String
from tf2_ros import TransformBroadcaster
from tf_transformations import quaternion_from_euler
from visualization_msgs.msg import Marker, MarkerArray

from pelvyn_inspection.mission_config import (
    WAYPOINTS,
    TARGET_DEPTH,
    WAYPOINT_TOLERANCE,
    SONAR_THRESHOLD,
    SONAR_CLEAR,
    OBSTACLES,
)


class StableMission(Node):
    LINEAR_SPEED = 0.35
    YAW_RATE = 0.70
    ROBOT_RADIUS = 0.55

    def __init__(self):
        super().__init__('stable_mission')
        self.x, self.y = -1.0, -1.0
        self.z = TARGET_DEPTH
        self.yaw = 0.0
        self.wp_index = 0
        self.sonar_range = 12.0
        self.avoid_timer = 0.0
        self.turn_dir = 1.0
        self.entity_name = 'UCAT'

        self.pub_state = self.create_publisher(EntityState, '/ucat/state', 10)
        self.pub_odom = self.create_publisher(Odometry, '/ucat/odom', 10)
        self.pub_imu = self.create_publisher(Imu, '/ucat/imu_data', 10)
        self.pub_path = self.create_publisher(Path, '/mission/path', 10)
        self.pub_status = self.create_publisher(String, '/mission/status', 10)
        self.pub_sonar = self.create_publisher(Range, '/sonar/forward', 10)
        self.pub_markers = self.create_publisher(MarkerArray, '/obstacle_markers', 10)
        self.tf_br = TransformBroadcaster(self)

        self.gz_client = self.create_client(SetEntityState, '/gazebo/set_entity_state')
        self.create_timer(0.1, self.control_loop)
        self.create_timer(2.0, self.publish_path)
        self.publish_path()
        self.get_logger().info('Stable mission running')

    def publish_path(self):
        path = Path()
        path.header.stamp = self.get_clock().now().to_msg()
        path.header.frame_id = 'world'
        for x, y, z in WAYPOINTS:
            ps = PoseStamped()
            ps.header = path.header
            ps.pose.position.x = x
            ps.pose.position.y = y
            ps.pose.position.z = z
            ps.pose.orientation.w = 1.0
            path.poses.append(ps)
        self.pub_path.publish(path)

    def raycast_sonar(self):
        min_range = 12.0
        # Three rays: center + slight left/right for wider detection
        for angle_offset in (0.0, 0.35, -0.35):
            bearing = self.yaw + angle_offset
            d = 0.1
            while d <= min_range:
                rx = self.x + d * math.cos(bearing)
                ry = self.y + d * math.sin(bearing)
                for ox, oy, radius in OBSTACLES:
                    if math.hypot(rx - ox, ry - oy) <= radius + self.ROBOT_RADIUS:
                        min_range = min(min_range, max(0.1, d))
                        break
                else:
                    d += 0.1
                    continue
                break
        return min_range

    def repel_from_obstacles(self):
        for ox, oy, radius in OBSTACLES:
            dx, dy = self.x - ox, self.y - oy
            dist = math.hypot(dx, dy)
            min_dist = radius + self.ROBOT_RADIUS
            if dist < min_dist and dist > 0.01:
                push = (min_dist - dist) / dist
                self.x += dx * push
                self.y += dy * push

    def push_gazebo(self, q):
        if not self.gz_client.service_is_ready():
            return
        for name in (self.entity_name, f'{self.entity_name}::base_link'):
            req = SetEntityState.Request()
            st = EntityState()
            st.name = name
            st.reference_frame = 'world'
            st.pose.position.x = self.x
            st.pose.position.y = self.y
            st.pose.position.z = self.z
            st.pose.orientation.x = q[0]
            st.pose.orientation.y = q[1]
            st.pose.orientation.z = q[2]
            st.pose.orientation.w = q[3]
            req.state = st
            self.gz_client.call_async(req)

    def publish_markers(self, stamp):
        markers = MarkerArray()
        for i, (ox, oy, radius) in enumerate(OBSTACLES):
            m = Marker()
            m.header.stamp = stamp
            m.header.frame_id = 'world'
            m.ns = 'obstacles'
            m.id = i
            m.type = Marker.CYLINDER
            m.action = Marker.ADD
            m.pose.position.x = ox
            m.pose.position.y = oy
            m.pose.position.z = TARGET_DEPTH
            m.scale.x = radius * 2
            m.scale.y = radius * 2
            m.scale.z = 2.0
            m.color.r = 1.0
            m.color.g = 0.2
            m.color.b = 0.1
            m.color.a = 0.35
            markers.markers.append(m)

        beam = Marker()
        beam.header.stamp = stamp
        beam.header.frame_id = 'world'
        beam.ns = 'sonar'
        beam.id = 99
        beam.type = Marker.LINE_STRIP
        beam.action = Marker.ADD
        beam.scale.x = 0.08
        beam.color.r = 0.1
        beam.color.g = 1.0
        beam.color.b = 0.2
        beam.color.a = 0.9
        from geometry_msgs.msg import Point
        p0 = Point(x=self.x, y=self.y, z=self.z)
        p1 = Point(
            x=self.x + self.sonar_range * math.cos(self.yaw),
            y=self.y + self.sonar_range * math.sin(self.yaw),
            z=self.z,
        )
        beam.points = [p0, p1]
        markers.markers.append(beam)
        self.pub_markers.publish(markers)

    def publish_all(self, mode: str, speed: float):
        stamp = self.get_clock().now().to_msg()
        q = quaternion_from_euler(0.0, 0.0, self.yaw)

        state = EntityState()
        state.pose.position.x = self.x
        state.pose.position.y = self.y
        state.pose.position.z = self.z
        state.pose.orientation.x = q[0]
        state.pose.orientation.y = q[1]
        state.pose.orientation.z = q[2]
        state.pose.orientation.w = q[3]
        self.pub_state.publish(state)

        odom = Odometry()
        odom.header.stamp = stamp
        odom.header.frame_id = 'world'
        odom.child_frame_id = 'base_link'
        odom.pose.pose = state.pose
        odom.twist.twist.linear.x = speed * math.cos(self.yaw)
        odom.twist.twist.linear.y = speed * math.sin(self.yaw)
        self.pub_odom.publish(odom)

        imu = Imu()
        imu.header.stamp = stamp
        imu.header.frame_id = 'imu_link'
        imu.orientation.x = q[0]
        imu.orientation.y = q[1]
        imu.orientation.z = q[2]
        imu.orientation.w = q[3]
        imu.linear_acceleration.x = speed * 0.15
        imu.angular_velocity.z = self.YAW_RATE * 0.1
        self.pub_imu.publish(imu)

        sonar = Range()
        sonar.header.stamp = stamp
        sonar.header.frame_id = 'world'
        sonar.radiation_type = Range.ULTRASOUND
        sonar.field_of_view = 0.5
        sonar.min_range = 0.1
        sonar.max_range = 12.0
        sonar.range = float(self.sonar_range)
        self.pub_sonar.publish(sonar)

        t = TransformStamped()
        t.header.stamp = stamp
        t.header.frame_id = 'world'
        t.child_frame_id = 'base_link'
        t.transform.translation.x = self.x
        t.transform.translation.y = self.y
        t.transform.translation.z = self.z
        t.transform.rotation.x = q[0]
        t.transform.rotation.y = q[1]
        t.transform.rotation.z = q[2]
        t.transform.rotation.w = q[3]
        self.tf_br.sendTransform(t)

        self.pub_status.publish(String(data=mode))
        self.publish_markers(stamp)
        self.push_gazebo(q)

    def control_loop(self):
        dt = 0.1
        self.z = TARGET_DEPTH
        self.sonar_range = self.raycast_sonar()
        speed = 0.0

        if self.sonar_range < SONAR_THRESHOLD:
            self.avoid_timer = 3.0
            self.turn_dir = 1.0 if self.wp_index % 2 == 0 else -1.0
            self.yaw += self.turn_dir * self.YAW_RATE * dt
            speed = 0.0
            mode = f'AVOID sonar={self.sonar_range:.2f}m | pos=({self.x:.1f},{self.y:.1f},{self.z:.1f})'
        elif self.avoid_timer > 0.0:
            if self.sonar_range > SONAR_CLEAR:
                self.avoid_timer -= dt
                self.x += self.LINEAR_SPEED * 0.4 * math.cos(self.yaw) * dt
                self.y += self.LINEAR_SPEED * 0.4 * math.sin(self.yaw) * dt
                speed = self.LINEAR_SPEED * 0.4
                mode = f'AVOID_RECOVER sonar={self.sonar_range:.2f}m | pos=({self.x:.1f},{self.y:.1f},{self.z:.1f})'
            else:
                self.yaw += self.turn_dir * self.YAW_RATE * dt
                speed = 0.0
                mode = f'AVOID_TURN sonar={self.sonar_range:.2f}m | pos=({self.x:.1f},{self.y:.1f},{self.z:.1f})'
        else:
            gx, gy, _ = WAYPOINTS[self.wp_index]
            dx, dy = gx - self.x, gy - self.y
            dist = math.hypot(dx, dy)
            if dist < WAYPOINT_TOLERANCE:
                self.wp_index = (self.wp_index + 1) % len(WAYPOINTS)
                self.get_logger().info(f'Waypoint {self.wp_index} reached')
                gx, gy, _ = WAYPOINTS[self.wp_index]
                dx, dy = gx - self.x, gy - self.y
                dist = math.hypot(dx, dy)

            desired = math.atan2(dy, dx)
            err = math.atan2(math.sin(desired - self.yaw), math.cos(desired - self.yaw))
            self.yaw += max(-self.YAW_RATE, min(self.YAW_RATE, 2.0 * err)) * dt
            scale = max(0.3, min(1.0, dist / 4.0))
            if self.sonar_range < SONAR_CLEAR:
                scale *= 0.4
            speed = self.LINEAR_SPEED * scale
            self.x += speed * math.cos(self.yaw) * dt
            self.y += speed * math.sin(self.yaw) * dt
            mode = (
                f'NAVIGATE wp={self.wp_index} dist={dist:.1f}m '
                f'sonar={self.sonar_range:.2f}m pos=({self.x:.1f},{self.y:.1f},{self.z:.1f})'
            )

        self.repel_from_obstacles()
        self.publish_all(mode, speed)


def main(args=None):
    rclpy.init(args=args)
    node = StableMission()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
