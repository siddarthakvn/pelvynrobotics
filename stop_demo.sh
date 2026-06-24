#!/bin/bash
# Stop ALL simulation and ROS nodes from previous runs
set +e
echo "Stopping simulation..."
killall -9 gzserver gzclient gazebo rviz2 rqt_image_view 2>/dev/null
pkill -9 -f "AUVMotion.py" 2>/dev/null
pkill -9 -f "moveFins.py" 2>/dev/null
pkill -9 -f "moveThruster.py" 2>/dev/null
pkill -9 -f "mission_controller" 2>/dev/null
pkill -9 -f "stable_mission" 2>/dev/null
pkill -9 -f "sensor_dashboard" 2>/dev/null
pkill -9 -f "odom_tf_broadcaster" 2>/dev/null
pkill -9 -f "sonar_simulator" 2>/dev/null
pkill -9 -f "spawn_UCAT.launch" 2>/dev/null
pkill -9 -f "full_demo.launch" 2>/dev/null
pkill -9 -f "robot_state_publisher" 2>/dev/null
sleep 2
echo "All stopped."
