"""
3006ICT Group Project - Controller
 
Mission:
    Search the observation stations, identify the requested visual target,
    navigate safely, and stop at the correct target.
"""
 
import heapq
import json
import math
from pathlib import Path
 
import cv2
import numpy as np
from controller import Robot
 
from project_utils import CONFIG, ROOT, world_to_grid, grid_to_world
from target_recognition import identify_target
import os

save_dir = os.path.dirname(os.path.abspath(__file__))
 
 
# ------------------------------------------------------------------
# Webots setup
# ------------------------------------------------------------------
robot = Robot()
timestep = int(robot.getBasicTimeStep())
 
left_motor = robot.getDevice("left wheel motor")
right_motor = robot.getDevice("right wheel motor")
camera = robot.getDevice("camera")
ps = [robot.getDevice(f"ps{i}") for i in range(8)]
gps = robot.getDevice("gps")
imu = robot.getDevice("imu")

print("Current camera FOV: ", camera.getFov())
camera.setFov(0.8)
print("changed to camera FOV: ", camera.getFov())
 
left_motor.setPosition(float("inf"))
right_motor.setPosition(float("inf"))
left_motor.setVelocity(0.0)
right_motor.setVelocity(0.0)
 
camera.enable(timestep)
gps.enable(timestep)
imu.enable(timestep)
for sensor in ps:
    sensor.enable(timestep)
 
MAX_SPEED = 10
GRID = np.load(ROOT / "maps" / "occupancy_grid.npy")
MISSION = json.loads((ROOT / "config" / "assessment_mission.json").read_text())
target = MISSION["target"]
 
# ------------------------------------------------------------------
# Provided low-level helpers
# ------------------------------------------------------------------
def set_speed(left, right):
    left = np.clip(left, -MAX_SPEED, MAX_SPEED)
    right = np.clip(right, -MAX_SPEED, MAX_SPEED)
    left_motor.setVelocity(float(left))
    right_motor.setVelocity(float(right))
 
 
def get_pose():
    """Return provided ground-truth-like pose (x, y, yaw)."""
    x, y, _ = gps.getValues()
    yaw = imu.getRollPitchYaw()[2]
    return x, y, yaw
 
 
def camera_bgr():
    h, w = camera.getHeight(), camera.getWidth()
    image = np.frombuffer(camera.getImage(), np.uint8).reshape(h, w, 4)
    return cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
 
 
def proximity_values():
    return [sensor.getValue() for sensor in ps]
 
 
# ------------------------------------------------------------------
# Group implementation
# ------------------------------------------------------------------
def angle_diff(a, b):
    """Shortest signed difference a - b in (-pi, pi]."""
    d = (a - b + math.pi) % (2 * math.pi) - math.pi
    return d
 
 
def go_to(target_x, target_y, tol=0.02):
    """Drive to (target_x, target_y). Blocks until within tol."""
    print(f"go_to({target_x:.2f}, {target_y:.2f})")
    step_count = 0
    while robot.step(timestep) != -1:
        x, y, yaw = get_pose()
        dx, dy = target_x - x, target_y - y
        dist = math.hypot(dx, dy)
 
        if step_count % 30 == 0:
            print(f"  pose=({x:+.2f},{y:+.2f}) yaw={yaw:+.2f} dist={dist:.2f}")
        step_count += 1
 
        if dist < tol:
            set_speed(0.0, 0.0)
            print(f"  REACHED ({x:+.2f},{y:+.2f})")
            return True
 
        bearing = math.atan2(dy, dx)
        h_err = angle_diff(bearing, yaw)
 
        if abs(h_err) > 0.2:
            turn = 2.0 if h_err > 0 else -2.0
            set_speed(-turn, turn)
        else:
            fwd = 3.0
            corr = 2.0 * h_err
            set_speed(fwd - corr, fwd + corr)
    return False
 
 
def rotate_to(target_yaw, tol=0.02):
    """Rotate in place until yaw matches target_yaw."""
    print(f"rotate_to({target_yaw:+.2f})")
    while robot.step(timestep) != -1:
        _, _, yaw = get_pose()
        err = angle_diff(target_yaw, yaw)
        if abs(err) < tol:
            set_speed(0.0, 0.0)
            print(f"  yaw={yaw:+.2f}")
            return
        turn = 1.5 if err > 0 else -1.5
        set_speed(-turn, turn)
 
 
# ------------------------------------------------------------------
# Path planning (A* on inflated occupancy grid)
# ------------------------------------------------------------------
def inflate_grid(grid, radius=2):
    """Expand obstacles by `radius` cells for robot-body safety margin."""
    inflated = grid.copy()
    rows, cols = grid.shape
    for r, c in np.argwhere(grid == 1):
        for dr in range(-radius, radius + 1):
            for dc in range(-radius, radius + 1):
                rr, cc = r + dr, c + dc
                if 0 <= rr < rows and 0 <= cc < cols:
                    inflated[rr, cc] = 1
    return inflated
 
 
NEIGHBOURS = [(-1, 0), (1, 0), (0, -1), (0, 1),
              (-1, -1), (-1, 1), (1, -1), (1, 1)]
 
 
def astar(start, goal, grid):
    """A* on 8-connected grid. start/goal are (row, col). Returns path or None."""
    open_set = [(0.0, start)]
    came_from = {}
    g = {start: 0.0}
    while open_set:
        _, cur = heapq.heappop(open_set)
        if cur == goal:
            path = [cur]
            while cur in came_from:
                cur = came_from[cur]
                path.append(cur)
            return path[::-1]
        for dr, dc in NEIGHBOURS:
            nxt = (cur[0] + dr, cur[1] + dc)
            if not (0 <= nxt[0] < grid.shape[0] and 0 <= nxt[1] < grid.shape[1]):
                continue
            if grid[nxt] == 1:
                continue
            tentative = g[cur] + math.hypot(dr, dc)
            if tentative < g.get(nxt, float("inf")):
                came_from[nxt] = cur
                g[nxt] = tentative
                f = tentative + math.hypot(nxt[0] - goal[0], nxt[1] - goal[1])
                heapq.heappush(open_set, (f, nxt))
    return None
 
 
def los_clear(a, b, grid):
    """Bresenham line-of-sight: True if no obstacle between grid cells a and b."""
    r0, c0 = a
    r1, c1 = b
    dr, dc = abs(r1 - r0), abs(c1 - c0)
    sr = 1 if r0 < r1 else -1
    sc = 1 if c0 < c1 else -1
    err = dr - dc
    while True:
        if grid[r0, c0] == 1:
            return False
        if (r0, c0) == (r1, c1):
            return True
        e2 = 2 * err
        if e2 > -dc:
            err -= dc
            r0 += sr
        if e2 < dr:
            err += dr
            c0 += sc
 
 
def smooth_path(path, grid):
    """Keep only waypoints not reachable in a straight line from the previous."""
    if len(path) < 3:
        return path
    out = [path[0]]
    i = 0
    while i < len(path) - 1:
        j = len(path) - 1
        while j > i + 1 and not los_clear(path[i], path[j], grid):
            j -= 1
        out.append(path[j])
        i = j
    return out
 
 
def nav_to(goal_x, goal_y):
    """Plan a safe path from current pose to (goal_x, goal_y) and drive it.
    Tries radius=1 inflation first; falls back to radius=0 if no path."""
    x, y, _ = get_pose()
    start_rc = world_to_grid(x, y)
    goal_rc = world_to_grid(goal_x, goal_y)
 
    path = None
    used_radius = None
    for radius in (1, 0):
        grid = inflate_grid(GRID, radius=radius)
        grid[start_rc] = 0
        grid[goal_rc] = 0
        path = astar(start_rc, goal_rc, grid)
        if path is not None:
            used_radius = radius
            break
 
    if path is None:
        print(f"  NO PATH to ({goal_x:.2f},{goal_y:.2f})")
        return False
 
    waypoints = smooth_path(path, grid)
    print(f"  path: {len(path)} cells -> {len(waypoints)} waypoints (inflation={used_radius})")
    for wx, wy in [grid_to_world(r, c) for r, c in waypoints[1:-1]]:
        go_to(wx, wy, tol=0.15)
    go_to(goal_x, goal_y)
    return True
 
 
# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------
def main():
    print("Group-project controller started.")
    print("Mission:", MISSION)
    print("Camera:", camera.getWidth(), "x", camera.getHeight())
 
    for _ in range(5):
        robot.step(timestep)
 
    stations = CONFIG["stations"]
    found = False

    # loop through all stations
    for st in stations:
        print(f"\n--- Visiting {st['id']} ---")
        if not nav_to(*st["observe"]):
            print(f"  SKIPPED {st['id']}")
            continue

        print(f"Station {st['id']} reached")
        rotate_to(st["observe_yaw"])
        for _ in range(5):
            robot.step(timestep)

        img = camera_bgr()

        out_path = os.path.join(save_dir, f"{st['id']}_view.png")
        cv2.imwrite(str(out_path), img)
        print(f"Saved {out_path}")

#-----NEW ADDITION---------------------
        is_target, label, score = identify_target(img, target)
        print(f"Identification: label={label}, score={score}, is_target={is_target}")

        if is_target:
            print(f"TARGET FOUND at {st['id']} - stopping")
            found = True
            break #stop robot, skip remaining stations

    if not found:
        print("\n Target not found at any station")

    print("Mission Complete!")
    while robot.step(timestep) != -1:
        set_speed(0.0, 0.0)
#---------------------------------------
    # print("\nAll stations visited.")
    # while robot.step(timestep) != -1:
    #     set_speed(0.0, 0.0)

 
if __name__ == "__main__":
    main()