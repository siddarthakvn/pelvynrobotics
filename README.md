# Pelvyn Robotics — Autonomous Underwater Inspection AUV

ROS 2 Humble project for the **Pelvyn Robotics internship technical assessment**:  
autonomous underwater inspection, waypoint navigation, sonar obstacle avoidance, and Gazebo simulation.

**Author:** Kvn Sai Siddartha  
**Repository:** https://github.com/siddarthakvn/pelvynrobotics

---

## What is included

| Path | Description |
|------|-------------|
| `src/pelvyn_inspection/` | ROS 2 package — mission, navigation, sensors, world, RViz |
| `docs/` | Technical report PDF, diagrams, screenshot assets |
| `patches/eeuvsim_gazebo.patch` | Local fixes applied to eeUVsim for Humble build |
| `run_demo.sh` | Build and launch full simulation demo |
| `monitor_sensors.sh` | Terminal sensor dashboard for recording |
| `stop_demo.sh` | Stop all Gazebo / ROS nodes |

---

## Quick start

### 1. Create workspace and clone repos

```bash
mkdir -p ~/auv_ws/src
cd ~/auv_ws/src

# This project
git clone https://github.com/siddarthakvn/pelvynrobotics.git
mv pelvynrobotics/* pelvynrobotics/.[!.]* ../ 2>/dev/null || true
# OR clone directly into ~/auv_ws:
# git clone https://github.com/siddarthakvn/pelvynrobotics.git ~/auv_ws

# Underwater simulator (required)
git clone https://github.com/Centre-for-Biorobotics/eeUVsim_Gazebo.git
cd eeUVsim_Gazebo && git apply ../../patches/eeuvsim_gazebo.patch && cd ..
```

**Simpler layout** — clone this repo as your workspace root:

```bash
git clone https://github.com/siddarthakvn/pelvynrobotics.git ~/auv_ws
cd ~/auv_ws/src
git clone https://github.com/Centre-for-Biorobotics/eeUVsim_Gazebo.git
cd ../..
cd eeUVsim_Gazebo && git apply ../patches/eeuvsim_gazebo.patch
```

### 2. Install dependencies (once)

```bash
cd ~/auv_ws
chmod +x install_deps.sh
./install_deps.sh
pip3 install --user xacro transformations
```

### 3. Build and run demo

```bash
cd ~/auv_ws
./run_demo.sh
```

Wait ~12 seconds. You should see Gazebo, RViz, camera view, and `NAVIGATE` in the terminal.

**Sensor dashboard** (second terminal):

```bash
./monitor_sensors.sh
```

---

## ROS 2 nodes

- `stable_mission` — waypoint navigation + sonar avoidance
- `sensor_monitor` — live terminal dashboard
- Gazebo plugins — IMU, camera, P3D odometry

## Key topics

- `/sonar/forward` — obstacle distance
- `/mission/status` — NAVIGATE / AVOID / AVOID_RECOVER
- `/ucat/odom` — robot position
- `/camera/image_raw` — inspection camera

---

## Technical report

PDF submission document:

`docs/Pelvyn_AUV_Technical_Report_Kvn_Sai_Siddartha.pdf`

Regenerate:

```bash
python3 docs/generate_report.py
```

---

## Platform

- Ubuntu 22.04
- ROS 2 Humble
- Gazebo 11 Classic
- eeUVsim UCAT AUV model
