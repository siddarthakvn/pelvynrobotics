"""Shared mission parameters for simulation."""

TARGET_DEPTH = -2.0
WAYPOINT_TOLERANCE = 1.0
SONAR_THRESHOLD = 4.0
SONAR_CLEAR = 6.0

# Inspection path — skirts obstacle field (spawn at -1,-1 away from dock)
WAYPOINTS = [
    (-1.0, -1.0, -2.0),
    (5.5, -0.5, -2.0),
    (5.5, 5.5, -2.0),
    (0.0, 5.5, -2.0),
    (-1.0, -1.0, -2.0),
]

# Static cylindrical obstacles (x, y, radius) — must match inspection_world.world
OBSTACLES = [
    (3.0, 0.5, 0.7),
    (3.5, 3.0, 0.8),
    (5.5, 5.0, 0.9),
    (1.5, 4.0, 0.6),
    (7.0, -1.5, 0.5),  # dock_station (moved to corner)
]
