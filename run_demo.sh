#!/bin/bash
# Pelvyn AUV demo — clean start every time
set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$SCRIPT_DIR/stop_demo.sh"

source /opt/ros/humble/setup.bash
cd "$SCRIPT_DIR"
colcon build --symlink-install --packages-select pelvyn_inspection
source install/setup.bash

python3 -c "import xacro" 2>/dev/null || pip3 install --user xacro
python3 -c "import tf_transformations" 2>/dev/null || pip3 install --user transformations

echo ""
echo "============================================"
echo "  Pelvyn AUV Demo — STABLE MODE"
echo "  Wait 12 seconds after Gazebo opens."
echo "  Terminal should show: NAVIGATE wp=..."
echo "  z must stay at -2.00 (NOT -2.90 or -16)"
echo "============================================"
echo ""

ros2 launch pelvyn_inspection full_demo.launch.py
