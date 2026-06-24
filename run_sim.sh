#!/bin/bash
# Start eeUVsim UCAT underwater simulation (kill stale Gazebo first)
set -eo pipefail

killall -9 gzserver gzclient gazebo 2>/dev/null || true
sleep 1

source /opt/ros/humble/setup.bash
source ~/auv_ws/install/setup.bash

# Python deps used by eeUVsim (if apt packages not installed)
python3 -c "import xacro" 2>/dev/null || pip3 install --user xacro
python3 -c "import tf_transformations" 2>/dev/null || pip3 install --user transformations

echo "Launching UCAT underwater simulation..."
ros2 launch eeuv_sim spawn_UCAT.launch.py
