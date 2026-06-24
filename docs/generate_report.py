#!/usr/bin/env python3
"""Generate Pelvyn AUV Technical Assessment PDF report."""

import subprocess
from datetime import date
from pathlib import Path

from PIL import Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image as RLImage,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

DOCS = Path(__file__).parent
DIAGRAMS = DOCS / 'diagrams'
IMAGES = DOCS / 'images'
OUTPUT = DOCS / 'Pelvyn_AUV_Technical_Report_Kvn_Sai_Siddartha.pdf'
AUTHOR = 'Kvn Sai Siddartha'


def build_diagrams():
    subprocess.run(['python3', str(DOCS / 'generate_diagrams.py')], check=True)


def scaled_image(path: Path, max_width: float, max_height: float = None):
    img = Image.open(path)
    w, h = img.size
    ratio = w / h
    width = min(max_width, w * 72 / 96)
    height = width / ratio
    if max_height and height > max_height:
        height = max_height
        width = height * ratio
    return RLImage(str(path), width=width, height=height)


def wrap_table(data, col_widths, header='#1A5276'):
    styles = getSampleStyleSheet()
    cs = ParagraphStyle('tc', parent=styles['Normal'], fontSize=8, leading=10)
    hs = ParagraphStyle('th', parent=cs, fontName='Helvetica-Bold', textColor=colors.white)
    rows = []
    for i, row in enumerate(data):
        st = hs if i == 0 else cs
        rows.append([Paragraph(str(c), st) for c in row])
    t = Table(rows, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(header)),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#CCCCCC')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9F9')]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
    ]))
    return t


def build_pdf():
    styles = getSampleStyleSheet()
    title = ParagraphStyle('T', parent=styles['Title'], fontSize=20, alignment=TA_CENTER, spaceAfter=12)
    sub = ParagraphStyle('S', parent=styles['Normal'], fontSize=11, alignment=TA_CENTER, spaceAfter=4)
    h1 = ParagraphStyle('H1', parent=styles['Heading1'], fontSize=13, spaceBefore=8, spaceAfter=5)
    h2 = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=10.5, spaceBefore=6, spaceAfter=3)
    body = ParagraphStyle('B', parent=styles['Normal'], fontSize=9.5, leading=13, alignment=TA_JUSTIFY, spaceAfter=4)
    cap = ParagraphStyle('C', parent=styles['Normal'], fontSize=7.5, alignment=TA_CENTER,
                         textColor=colors.HexColor('#555555'), spaceAfter=4, spaceBefore=1)
    bullet = ParagraphStyle('Bu', parent=body, leftIndent=12, spaceAfter=2, fontSize=9.5, leading=12)

    doc = SimpleDocTemplate(
        str(OUTPUT), pagesize=A4,
        leftMargin=1.8 * cm, rightMargin=1.8 * cm, topMargin=1.7 * cm, bottomMargin=1.7 * cm,
        title='Pelvyn AUV Technical Report', author=AUTHOR,
    )
    story = []
    pw = A4[0] - 3.6 * cm

    # Cover
    story.append(Spacer(1, 2.5 * cm))
    story.append(Paragraph('Pelvyn Robotics', sub))
    story.append(Paragraph('Technical Assessment Submission', sub))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(
        'Autonomous Underwater Inspection Robot<br/>'
        'System Architecture &amp; Navigation Framework', title))
    story.append(Spacer(1, 0.6 * cm))
    story.append(Paragraph(f'<b>Candidate:</b> {AUTHOR}', sub))
    story.append(Paragraph('<b>Date:</b> ' + date.today().strftime('%B %d, %Y'), sub))
    story.append(Paragraph('<b>Platform:</b> ROS 2 Humble | Gazebo 11 | eeUVsim UCAT AUV', sub))
    story.append(PageBreak())

    # 1 + 2
    story.append(Paragraph('1. Executive Summary', h1))
    story.append(Paragraph(
        'This report presents the software and embedded architecture for an autonomous underwater '
        'inspection robot (AUV) for submerged infrastructure inspection and mapping. The system '
        'integrates forward sonar, IMU, depth control, camera, and odometry within a ROS 2 framework '
        'with waypoint mission planning and reactive obstacle avoidance.', body))
    story.append(Paragraph(
        'A working simulation was built using eeUVsim Gazebo and a custom <i>pelvyn_inspection</i> '
        'ROS 2 package. The AUV navigates a rectangular path at 2 m depth, detects obstacles via '
        'simulated sonar, executes AVOID / AVOID_TURN / AVOID_RECOVER maneuvers, and streams sensor '
        'data to RViz and a terminal dashboard.', body))

    story.append(Paragraph('2. System Architecture', h1))
    story.append(Paragraph(
        'The design separates sensing, embedded control (STM32), onboard computation (Jetson + ROS 2), '
        'and ground-station monitoring. Figure 1 shows the full stack.', body))
    story.append(scaled_image(DIAGRAMS / 'fig1_system_architecture.png', pw, max_height=6.8 * cm))
    story.append(Paragraph('Figure 1: System architecture block diagram.', cap))
    story.append(Paragraph('2.1 Major Modules', h2))
    story.append(wrap_table([
        ['Module', 'Responsibility', 'Implementation'],
        ['Perception', 'Obstacle detection, visual inspection', 'Sonar raycast + Gazebo camera'],
        ['Localization', 'Position and orientation', 'P3D odometry + IMU + TF'],
        ['Planning', 'Mission path', 'Waypoints in mission_config.py'],
        ['Navigation', 'Path tracking, depth hold', 'stable_mission (10 Hz)'],
        ['Avoidance', 'Reactive obstacle response', 'Sonar threshold state machine'],
        ['Visualization', 'Operator display', 'RViz2 + sensor_monitor'],
    ], [2.2 * cm, 5.2 * cm, 7.8 * cm]))

    # 3 + 4
    story.append(Paragraph('3. Sensor Suite Selection', h1))
    story.append(Paragraph(
        'Sensors support GPS-denied localization, low-visibility obstacle detection, depth hold, '
        'orientation tracking, and visual inspection.', body))
    story.append(wrap_table([
        ['Sensor', 'Purpose', 'ROS Topic', 'Simulation / Hardware'],
        ['Forward Sonar', 'Obstacle detection', '/sonar/forward', 'Simulated raycast'],
        ['IMU', 'Orientation and motion', '/ucat/imu_data', 'Gazebo IMU plugin'],
        ['Camera', 'Visual inspection', '/camera/image_raw', 'Gazebo 640×480'],
        ['Odometry', 'Horizontal position (DVL equiv.)', '/ucat/odom', 'P3D + kinematic state'],
        ['Depth', 'Altitude hold', 'TARGET_DEPTH', 'Software lock at −2 m'],
    ], [2.4 * cm, 4.2 * cm, 3.4 * cm, 4.6 * cm], header='#117A65'))
    story.append(Paragraph(
        '<b>Production hardware:</b> Teledyne Pathfinder DVL, Bar30 depth sensor, VectorNav VN-100 IMU, '
        'multibeam sonar, and low-light HD camera.', body))

    story.append(Paragraph('4. ROS 2 Software Architecture', h1))
    story.append(Paragraph(
        'ROS 2 Humble runs the <i>pelvyn_inspection</i> package for mission control and monitoring. '
        'eeUVsim supplies the UCAT URDF and Gazebo plugins (IMU, camera, P3D).', body))
    story.append(scaled_image(DIAGRAMS / 'fig2_ros2_communication.png', pw, max_height=7.8 * cm))
    story.append(Paragraph('Figure 2: ROS 2 nodes and topics (table below diagram).', cap))
    story.append(Paragraph('4.1 Key Nodes', h2))
    for line in [
        '<b>stable_mission</b> — Waypoint navigation, sonar raycast, avoidance, TF, markers.',
        '<b>sensor_monitor</b> — Terminal dashboard (mission, sonar, IMU, camera) every 1 s.',
        '<b>robot_state_publisher</b> — URDF joint states for RViz.',
        '<b>Gazebo plugins</b> — IMU, camera, P3D odometry.',
    ]:
        story.append(Paragraph('• ' + line, bullet))
    story.append(Paragraph(
        'Launch: <i>full_demo.launch.py</i> loads inspection_world, spawns UCAT at (−1,−1,−2), '
        'starts stable_mission, rqt_image_view, and RViz2.', body))

    story.append(PageBreak())

    # 5 + 6 + 7
    story.append(Paragraph('5. Navigation Framework', h1))
    story.append(scaled_image(DIAGRAMS / 'fig3_mission_flowchart.png', pw * 0.92, max_height=10.0 * cm))
    story.append(Paragraph('Figure 3: Mission state machine and obstacle avoidance.', cap))
    story.append(Paragraph(
        'Five waypoints at z = −2.0 m: (−1,−1) → (5.5,−0.5) → (5.5,5.5) → (0,5.5) → (−1,−1). '
        'Sonar below 4 m triggers AVOID; above 6 m allows AVOID_RECOVER.', body))
    story.append(wrap_table([
        ['Parameter', 'Value', 'Description'],
        ['SONAR_THRESHOLD', '4.0 m', 'Enter AVOID'],
        ['SONAR_CLEAR', '6.0 m', 'Safe to recover'],
        ['ROBOT_RADIUS', '0.55 m', 'Collision envelope'],
        ['LINEAR_SPEED', '0.35 m/s', 'Cruise speed'],
        ['YAW_RATE', '0.70 rad/s', 'Turn rate'],
    ], [3.2 * cm, 2.2 * cm, 9.8 * cm], header='#884EA0'))

    story.append(Paragraph('6. Sensor Fusion Strategy', h1))
    story.append(scaled_image(DIAGRAMS / 'fig4_sensor_fusion.png', pw, max_height=4.6 * cm))
    story.append(Paragraph('Figure 4: Sensor fusion pipeline.', cap))
    story.append(Paragraph(
        'Simulation uses P3D odometry for pose, IMU for orientation, and sonar for obstacles. '
        'On hardware, an EKF would fuse DVL, IMU, and depth at 50–100 Hz.', body))

    story.append(Paragraph('7. Failure Handling &amp; Safety', h1))
    for line in [
        '<b>Sensor loss:</b> Reduce speed, hold heading, report degraded mode.',
        '<b>Depth excursion:</b> Depth locked at −2.0 m in stable_mission.',
        '<b>Collision:</b> Repulsive force when inside obstacle envelope.',
        '<b>Stuck:</b> AVOID timer and turn alternation; recover when sonar &gt; 6 m.',
        '<b>Comms loss:</b> Watchdog neutralises thrust and triggers ascent after 30 s.',
    ]:
        story.append(Paragraph('• ' + line, bullet))

    # 8 — screenshots + conclusion on same page block (no extra page break)
    story.append(Paragraph('8. Simulation Results', h1))
    story.append(Paragraph(
        'Gazebo 11 tests with four cylindrical obstacles and a dock station. Screenshots show '
        'navigation, avoidance, RViz sensor display, and the live terminal dashboard.', body))

    shots = [
        ('Screenshot_from_2026-06-24_10-13-00-26388b53-bc35-4d25-ad74-afd5429903bf.png',
         'Fig. 5: Gazebo inspection world.'),
        ('Screenshot_from_2026-06-24_10-13-15-4ed4580d-d1f0-4e44-a9c0-3be86356964a.png',
         'Fig. 6: AUV among obstacles.'),
        ('Screenshot_from_2026-06-24_10-14-30-ff700122-2a9c-4d1e-83aa-7524febc0539.png',
         'Fig. 7: RViz path, sonar, markers.'),
        ('Screenshot_from_2026-06-24_10-14-59-a7de1766-6c4e-4c61-a382-acf5ee8c7335.png',
         'Fig. 8: Terminal dashboard (AVOID_RECOVER).'),
    ]
    half = pw / 2 - 0.1 * cm
    for i in range(0, len(shots), 2):
        imgs, caps = [], []
        for j in range(2):
            if i + j < len(shots):
                fn, ct = shots[i + j]
                p = IMAGES / fn
                if p.exists():
                    imgs.append(scaled_image(p, half, max_height=5.0 * cm))
                    caps.append(Paragraph(ct, cap))
        if len(imgs) == 2:
            ti = Table([[imgs[0], imgs[1]]], colWidths=[half, half])
            ti.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 2),
                ('RIGHTPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ]))
            story.append(ti)
            tc = Table([[caps[0], caps[1]]], colWidths=[half, half])
            tc.setStyle(TableStyle([('BOTTOMPADDING', (0, 0), (-1, -1), 2)]))
            story.append(tc)

    story.append(Paragraph(
        'Observed states: <b>NAVIGATE</b>, <b>AVOID</b> (sonar &lt; 4 m), <b>AVOID_TURN</b>, and '
        '<b>AVOID_RECOVER</b> (sonar &gt; 6 m). Depth held at z = −2.00 m throughout a 6+ minute run.',
        body))
    story.append(Paragraph('9. Conclusion', h1))
    story.append(Paragraph(
        'The simulation validates the full inspection stack — sensor integration, waypoint navigation, '
        'and sonar-based avoidance — for submerged infrastructure tasks. The AUV completed multiple '
        'laps of the inspection path while holding depth and reacting to obstacles in real time.',
        body))

    story.append(Paragraph('10. Future Scope', h1))
    story.append(Paragraph(
        'The current work establishes a simulation baseline. The following extensions would move the '
        'system toward a deployable inspection platform:', body))
    for line in [
        '<b>Sensor fusion on hardware:</b> Integrate robot_localization EKF with DVL velocity, '
        'IMU angular rates, and Bar30 pressure depth for robust pose estimation at 50–100 Hz.',
        '<b>Real sonar interface:</b> Replace the simulated raycast with a Gazebo ray plugin or a '
        'driver for a multibeam sonar (e.g. Oculus M750d) for environment-agnostic obstacle detection.',
        '<b>SLAM and mapping:</b> Add Cartographer or RTAB-Map to build seafloor and structure maps '
        'during inspection missions for post-mission analysis.',
        '<b>High-fidelity dynamics:</b> Couple fin/thruster physics with model-predictive control '
        'instead of kinematic set_entity_state for realistic hydrodynamic behaviour.',
        '<b>Mission operations:</b> Support mission upload from shore, acoustic or tethered telemetry, '
        'and automated data offload after each dive.',
        '<b>Docking and recovery:</b> Extend the dock_station model with autonomous homing and '
        'precision docking for battery swap and data retrieval.',
    ]:
        story.append(Paragraph('• ' + line, bullet))

    story.append(Paragraph(
        '<b>Demo command:</b> <i>ros2 launch pelvyn_inspection full_demo.launch.py</i> &nbsp;|&nbsp; '
        '<b>Workspace:</b> ~/auv_ws/src/pelvyn_inspection',
        ParagraphStyle('code', parent=body, fontSize=8.5, fontName='Courier', spaceBefore=4)),
    )

    doc.build(story)
    print(f'PDF written to {OUTPUT}')


if __name__ == '__main__':
    build_diagrams()
    build_pdf()
