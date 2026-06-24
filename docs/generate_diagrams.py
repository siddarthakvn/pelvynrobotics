#!/usr/bin/env python3
"""Architecture diagrams for Pelvyn AUV report — original layout, overlap fixes."""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Polygon

OUT = Path(__file__).parent / 'diagrams'
OUT.mkdir(exist_ok=True)


def box(ax, x, y, w, h, text, color='#E8F4FD', edge='#1A5276', fs=8):
    rect = FancyBboxPatch(
        (x, y), w, h, boxstyle='round,pad=0.02,rounding_size=0.08',
        linewidth=1.2, edgecolor=edge, facecolor=color,
    )
    ax.add_patch(rect)
    ax.text(x + w / 2, y + h / 2, text, ha='center', va='center', fontsize=fs, linespacing=1.3)


def arrow(ax, x1, y1, x2, y2):
    ax.add_patch(FancyArrowPatch(
        (x1, y1), (x2, y2), arrowstyle='->', mutation_scale=12,
        linewidth=1.1, color='#2C3E50',
    ))


def system_architecture():
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')
    ax.set_title(
        'Figure 1: System Architecture — Autonomous Underwater Inspection Robot',
        fontsize=11, fontweight='bold', pad=12,
    )

    box(ax, 0.3, 4.5, 2.0, 1.0, 'Sensors\nSonar | IMU | Camera\nDepth | DVL', '#D5F5E3')
    box(ax, 2.7, 4.5, 2.0, 1.0, 'Embedded Layer\nSTM32 / Motor Driver\nThruster Control', '#FCF3CF')
    box(ax, 5.1, 4.5, 2.0, 1.0, 'Onboard Computer\nNVIDIA Jetson\nROS 2 Humble', '#D6EAF8')
    box(ax, 7.5, 4.5, 2.0, 1.0, 'Ground Station\nMission Monitor\nData Logging', '#FADBD8')

    box(ax, 1.0, 2.5, 2.4, 1.0, 'Perception\nObstacle Detection\nVisual Inspection', '#E8DAEF')
    box(ax, 3.8, 2.5, 2.4, 1.0, 'Localization\nEKF Fusion\nOdometry + IMU', '#D1F2EB')
    box(ax, 6.6, 2.5, 2.4, 1.0, 'Planning\nWaypoint Mission\nPath Generation', '#FDEBD0')

    box(ax, 2.5, 0.6, 5.0, 1.0,
        'Navigation & Control\nDepth Hold | Obstacle Avoidance | Mission State Machine',
        '#AED6F1', fs=9)

    arrow(ax, 2.3, 5.0, 2.7, 5.0)
    arrow(ax, 4.7, 5.0, 5.1, 5.0)
    arrow(ax, 7.1, 5.0, 7.5, 5.0)
    arrow(ax, 6.1, 4.5, 5.0, 3.5)
    arrow(ax, 2.2, 4.5, 2.2, 3.5)
    arrow(ax, 2.2, 3.0, 4.0, 1.6)
    arrow(ax, 5.0, 3.0, 5.0, 1.6)
    arrow(ax, 7.8, 3.0, 6.0, 1.6)

    fig.tight_layout()
    fig.savefig(OUT / 'fig1_system_architecture.png', dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)


def ros2_communication():
    """Original two-row node layout; topics listed in table below (no overlap)."""
    fig, ax = plt.subplots(figsize=(10, 7.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7.2)
    ax.axis('off')
    ax.set_title(
        'Figure 2: ROS 2 Node & Topic Communication (Simulation)',
        fontsize=11, fontweight='bold', pad=12,
    )

    # Top row
    box(ax, 0.4, 5.5, 1.8, 1.0, 'Gazebo\nSimulator', '#D5F5E3')
    box(ax, 2.7, 5.5, 1.9, 1.0, 'stable_mission\n(Navigation)', '#D6EAF8')
    box(ax, 5.1, 5.5, 1.9, 1.0, 'sensor_monitor\n(Dashboard)', '#FADBD8')
    box(ax, 7.6, 5.5, 1.9, 1.0, 'RViz2\n(Visualization)', '#E8DAEF')

    # Bottom row
    box(ax, 0.4, 4.0, 1.8, 1.0, 'robot_state_\npublisher', '#FCF3CF')
    box(ax, 2.7, 4.0, 1.9, 1.0, 'Gazebo Plugins\nIMU | Camera | P3D', '#D1F2EB')
    box(ax, 5.1, 4.0, 1.9, 1.0, 'rqt_image_view\n(Camera Feed)', '#FDEBD0')

    # Arrows only — no text on arrows
    arrow(ax, 2.2, 6.0, 2.7, 6.0)
    arrow(ax, 4.6, 6.0, 5.1, 6.0)
    arrow(ax, 7.0, 6.0, 7.6, 6.0)
    arrow(ax, 1.3, 5.5, 1.3, 5.0)
    arrow(ax, 3.6, 5.5, 3.6, 5.0)
    arrow(ax, 6.0, 5.5, 6.0, 5.0)

    # Topic reference table (replaces overlapping inline labels)
    rows = [
        ['Topic', 'Message Type', 'Publisher', 'Purpose'],
        ['/sonar/forward', 'sensor_msgs/Range', 'stable_mission', 'Obstacle avoidance'],
        ['/mission/status', 'std_msgs/String', 'stable_mission', 'Mission state'],
        ['/mission/path', 'nav_msgs/Path', 'stable_mission', 'Planned path (RViz)'],
        ['/obstacle_markers', 'visualization_msgs/MarkerArray', 'stable_mission', 'Obstacle display'],
        ['/ucat/odom', 'nav_msgs/Odometry', 'stable_mission / P3D', 'Localization'],
        ['/ucat/imu_data', 'sensor_msgs/Imu', 'Gazebo IMU plugin', 'Orientation'],
        ['/camera/image_raw', 'sensor_msgs/Image', 'Gazebo camera', 'Visual inspection'],
    ]
    y0, rh = 0.15, 0.38
    cw = [2.15, 2.35, 2.15, 2.9]
    x0 = 0.35
    for ri, row in enumerate(rows):
        x = x0
        bg = '#1A5276' if ri == 0 else ('#F4F6F7' if ri % 2 == 0 else 'white')
        tc = 'white' if ri == 0 else '#2C3E50'
        for cell, w in zip(row, cw):
            rect = FancyBboxPatch(
                (x, y0), w, rh, boxstyle='square,pad=0',
                linewidth=0.5, edgecolor='#BDC3C7', facecolor=bg,
            )
            ax.add_patch(rect)
            ax.text(x + w / 2, y0 + rh / 2, cell, ha='center', va='center',
                    fontsize=6.5, color=tc, fontweight='bold' if ri == 0 else 'normal')
            x += w
        y0 += rh

    fig.tight_layout()
    fig.savefig(OUT / 'fig2_ros2_communication.png', dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)


def mission_flowchart():
    """Vertical flowchart — main column centre, avoidance branch left, no crossing lines."""
    fig, ax = plt.subplots(figsize=(8.5, 11))
    ax.set_xlim(0, 8.5)
    ax.set_ylim(0, 11)
    ax.axis('off')
    ax.set_title(
        'Figure 3: Mission State Machine & Obstacle Avoidance Flow',
        fontsize=11, fontweight='bold', pad=12,
    )

    cx = 5.5
    bw, bh = 3.0, 0.72

    def b(cx_, cy_, text, color, w=bw):
        box(ax, cx_ - w / 2, cy_ - bh / 2, w, bh, text, color, fs=7.5)

    def d(cx_, cy_, text):
        w, h = 2.6, 0.88
        pts = [(cx_, cy_ + h / 2), (cx_ + w / 2, cy_), (cx_, cy_ - h / 2), (cx_ - w / 2, cy_)]
        ax.add_patch(Polygon(pts, closed=True, facecolor='#FCF3CF', edgecolor='#7D6608', lw=1))
        ax.text(cx_, cy_, text, ha='center', va='center', fontsize=7.5)

    # Main column (right)
    b(cx, 10.0, 'START\nSpawn at (-1,-1), depth -2m', '#D5F5E3')
    arrow(ax, cx, 9.64, cx, 9.06)
    b(cx, 8.7, 'NAVIGATE\nFollow waypoint path', '#D6EAF8')
    arrow(ax, cx, 8.34, cx, 7.76)
    d(cx, 7.3, 'Sonar < 4.0 m?')

    arrow(ax, cx, 6.86, cx, 6.28)
    ax.text(cx + 0.25, 6.55, 'NO', fontsize=7, color='green', fontweight='bold')
    b(cx, 5.9, 'Continue navigation\ntoward waypoint', '#D6EAF8', w=3.2)
    arrow(ax, cx, 5.54, cx, 4.96)
    b(cx, 4.6, 'Waypoint reached?\nNext waypoint / loop', '#E8DAEF', w=3.2)
    arrow(ax, cx + 1.6, 4.6, cx + 1.6, 8.7)
    arrow(ax, cx + 1.6, 8.7, cx + bw / 2, 8.7)

    # Avoidance branch (left) — YES from first diamond
    lx = 2.0
    arrow(ax, cx - 1.3, 7.3, lx + 1.25, 7.3)
    ax.text(3.5, 7.45, 'YES', fontsize=7, color='red', fontweight='bold')
    b(lx, 7.3, 'AVOID\nStop forward, turn only', '#FADBD8', w=2.5)
    arrow(ax, lx + 1.25, 6.94, lx + 1.25, 6.36)
    d(lx + 1.25, 5.9, 'Sonar > 6.0 m?')

    arrow(ax, lx + 1.25, 5.46, lx + 1.25, 4.88)
    ax.text(lx + 1.55, 5.15, 'YES', fontsize=7, color='green', fontweight='bold')
    b(lx, 4.5, 'AVOID_RECOVER\nSlow forward', '#D1F2EB', w=2.5)
    arrow(ax, lx + 2.5, 4.5, cx - 1.6, 5.9)

    # AVOID_TURN — below second diamond, NO path
    tx = 2.0
    arrow(ax, lx + 1.25, 5.46, tx + 1.25, 4.0)
    ax.text(lx + 2.0, 4.85, 'NO', fontsize=7, color='red', fontweight='bold')
    b(tx, 3.6, 'AVOID_TURN\nKeep turning', '#FADBD8', w=2.5)
    # loop back to second diamond (left side, no crossing main column)
    ax.plot([tx, tx - 0.5, tx - 0.5, lx + 1.25 - 1.3],
            [3.96, 3.96, 5.9, 5.9], color='#2C3E50', lw=1.0)
    ax.annotate('', xy=(lx + 1.25 - 1.3, 5.9), xytext=(tx - 0.5, 5.9),
                arrowprops=dict(arrowstyle='->', color='#2C3E50', lw=1.0))

    fig.tight_layout()
    fig.savefig(OUT / 'fig3_mission_flowchart.png', dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)


def sensor_fusion():
    fig, ax = plt.subplots(figsize=(10, 5.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5.2)
    ax.axis('off')
    ax.set_title(
        'Figure 4: Sensor Fusion & Perception Pipeline',
        fontsize=11, fontweight='bold', pad=12,
    )

    box(ax, 0.3, 3.5, 1.7, 0.85, 'Forward Sonar\n(Range)', '#D5F5E3')
    box(ax, 0.3, 2.1, 1.7, 0.85, 'IMU\n(Orientation)', '#D5F5E3')
    box(ax, 0.3, 0.7, 1.7, 0.85, 'Camera\n(Visual)', '#D5F5E3')

    box(ax, 2.8, 2.1, 1.8, 1.0, 'Perception\nLayer', '#D6EAF8')
    box(ax, 5.2, 2.1, 2.0, 1.0, 'State Estimator\n(EKF / Odometry)', '#FCF3CF')

    box(ax, 7.8, 3.3, 1.6, 0.8, 'Obstacle\nMap', '#FADBD8')
    box(ax, 7.8, 1.0, 1.6, 0.8, 'Pose Estimate\n(x, y, z, yaw)', '#D1F2EB')
    box(ax, 9.0, 2.1, 0.85, 1.0, 'Mission\nController', '#AED6F1', fs=7)

    for sy in (3.9, 2.5, 1.1):
        arrow(ax, 2.0, sy, 2.8, 2.6)
    arrow(ax, 4.6, 2.6, 5.2, 2.6)
    arrow(ax, 6.2, 2.7, 7.8, 3.3)
    arrow(ax, 6.2, 2.3, 7.8, 1.4)
    arrow(ax, 8.6, 3.3, 8.55, 2.7)
    arrow(ax, 8.6, 1.4, 8.55, 2.1)

    fig.tight_layout()
    fig.savefig(OUT / 'fig4_sensor_fusion.png', dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)


if __name__ == '__main__':
    system_architecture()
    ros2_communication()
    mission_flowchart()
    sensor_fusion()
    print(f'Diagrams saved to {OUT}')
