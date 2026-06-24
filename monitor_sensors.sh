#!/bin/bash
# Run in a SECOND terminal while demo is running — for screen recording
set -eo pipefail
source /opt/ros/humble/setup.bash
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/install/setup.bash"
echo "Starting sensor dashboard (updates every 1 second)..."
ros2 run pelvyn_inspection sensor_monitor
