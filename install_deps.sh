#!/bin/bash
# Install remaining Python/ROS deps without heavy ros2_control stack
set -eo pipefail

echo "Installing packages (sudo password required)..."
sudo apt-get update
sudo apt-get install -y \
  ros-humble-xacro \
  ros-humble-tf-transformations \
  python3-xacro

echo "Installing Python packages for current user..."
pip3 install --user xacro transformations

echo ""
echo "Done. Build and launch:"
echo "  source /opt/ros/humble/setup.bash"
echo "  cd ~/auv_ws && colcon build --symlink-install"
echo "  source install/setup.bash"
echo "  ros2 launch eeuv_sim spawn_UCAT.launch.py"
