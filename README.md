# Level 1: ROS2 Navigation Assignment - Rishi Rakesh Shendre

## My Approach

### Step 1 — Map Loading (`map_loader.launch.py`)

The first launch file sets up the map server to load the pre-built map of the test environment.

**What I did:**
- Called the `map_server` node from the `nav2_map_server` package, passing the path to `testbed_world.yaml` as a parameter.
- Added a `lifecycle_manager` node to activate the `map_server`, since Nav2 nodes are lifecycle-managed and won't publish without being explicitly activated.

```
map_server  ──►  lifecycle_manager (manages: [map_server])
```

**To run:**
```bash
ros2 launch testbed_navigation map_loader.launch.py
```

---

### Step 2 — Localization (`localization.launch.py`)

The second launch file sets up AMCL (Adaptive Monte Carlo Localization) for the robot to locate itself within the loaded map.

**What I did:**
- Created `config/amcl_params.yaml` with tuned AMCL parameters for the Testbed-T1.0.0.
- Called the `amcl` node in the launch file, pointing it to the parameter file.
- Added another `lifecycle_manager` to activate the `amcl` node.

```
amcl  ──►  lifecycle_manager (manages: [amcl])
```

**To run** (after map loader):
```bash
ros2 launch testbed_navigation localization.launch.py
```

Then set the initial pose in RViz using the **2D Pose Estimate** tool.

---

### Step 3 — Navigation (`navigation.launch.py`)

The third launch file brings up the full navigation stack with individual Nav2 plugins.

**What I did:**
- Configured `config/nav2_params.yaml` with parameters for:
  - `planner_server` — global path planning using `NavfnPlanner`
  - `controller_server` — local planning using `DWBLocalPlanner`
  - `bt_navigator` — behaviour tree based goal execution
  - `behavior_server` — recovery behaviours (spin, backup, wait)
- All nodes are activated by a single `lifecycle_manager`.

```
planner_server  ──┐
controller_server ──┤──►  lifecycle_manager
bt_navigator    ──┤
behavior_server ──┘
```

**To run** (after localization):
```bash
ros2 launch testbed_navigation navigation.launch.py
```

Then send a goal in RViz using the **2D Nav Goal** tool.

---

## Challenges Faced & How I Solved Them

### Challenge 1 — Map Not Visible in RViz After Map Loader

**Problem:** After running `map_loader.launch.py`, the map was not appearing in RViz. The map server was running but not publishing the transform between the `map` and `odom` frames.

**Root Cause:** The static transform between `map` → `odom` was missing since AMCL (which publishes this transform) was not yet running.

**Solution:** Published a temporary static transform manually to verify the map was loading correctly:
```bash
ros2 run tf2_ros static_transform_publisher 0 0 0 0 0 0 map odom
```
This confirmed the map server was working. Once AMCL was running in the localization step, it took over publishing this transform automatically.

---

### Challenge 2 — Planner Loop Missed Desired Rate

**Problem:** The terminal showed:
```
Planner loop missed its desired rate of 10.0000 Hz. Current loop rate is 1.2500 Hz
```
The controller was receiving goals before the planner had finished computing the path, causing immediate failure.

**Root Cause:** The `expected_planner_frequency` in `nav2_params.yaml` was set too high relative to what the system could achieve, and the controller frequency was mismatched.

**Solution:** Reduced `expected_planner_frequency` to a value the system could sustain, and ensured `controller_frequency` was lower than the planner frequency so the controller waits for a valid path before attempting to follow it.

---

### Challenge 3 — Robot Only Spinning in Place

**Problem:** The robot would receive a goal, spin in place, and then fail with `No valid trajectories out of 0!`

**Root Cause:** Several DWB local planner parameters were missing or incorrectly set:
- `decel_lim_x` and `decel_lim_theta` were not defined, causing undefined behavior in trajectory sampling.
- `min_speed_theta: 0.0` meant the planner could sample zero-rotation trajectories, resulting in degenerate paths.
- `RotateToGoal.slowing_factor` was too aggressive, causing the robot to slow to a stop before reaching the goal orientation.

**Solution:** Added the missing deceleration limits, set `min_speed_theta: 0.3` to force meaningful rotation sampling, and tuned `RotateToGoal.slowing_factor` to allow the robot to complete its rotation and move forward.

```yaml
decel_lim_x: -2.5
decel_lim_theta: -3.2
min_speed_theta: 0.3
RotateToGoal.slowing_factor: 5.0
```

---

## Steps to Run the Full Navigation Stack

Run each command in a **separate terminal**, in order:

**Terminal 1 — Launch Simulation:**
```bash
cd ~/assignment_ws
source install/setup.bash
ros2 launch testbed_bringup testbed_full_bringup.launch.py
```

**Terminal 2 — Load Map:**
```bash
source install/setup.bash
ros2 launch testbed_navigation map_loader.launch.py
```

**Terminal 3 — Start Localization:**
```bash
source install/setup.bash
ros2 launch testbed_navigation localization.launch.py
```
> Set the initial pose in RViz using **2D Pose Estimate**.

**Terminal 4 — Start Navigation:**
```bash
source install/setup.bash
ros2 launch testbed_navigation navigation.launch.py
```
> Send a goal in RViz using **2D Nav Goal**.

---

## Demo

[Watch Demo Video](https://drive.google.com/file/d/1KTF1V_9mh8EPJ1f3G7SobcM5nUyMGl_0/view?usp=sharing)

---
## Contact Info
- Name: Rishi Shendre
- Contact number: 8806140318
- Email Address: rishishendre1@gmail.com
