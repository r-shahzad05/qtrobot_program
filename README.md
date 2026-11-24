# Companion Bot

Starter ROS package for programming a LuxAI QTrobot. The package is laid out as
a catkin workspace so it can be built on the QTrobot computer or on the lab
Ubuntu VM.

## Requirements

- Ubuntu with the ROS distribution supported by the QTrobot image
- A QTrobot (or a ROS environment providing `qt_robot_interface`)
- Python 3 and `catkin_make`
- Network access to the robot when ROS is running on another computer

The QTrobot tutorials are the source of truth for the installed ROS version and
service interfaces:

- [Create a ROS Python project](https://docs.luxai.com/docs/tutorials/python/python_ros_project)
- [QTrobot interfaces using ROS services](https://docs.luxai.com/docs/tutorials/python/python_ros_services)

## First-time setup

From this directory, on the robot computer or Ubuntu VM:

```bash
./setup_qtrobot.sh
source /opt/ros/$ROS_DISTRO/setup.bash
source ROS_file/devel/setup.bash
```

`setup_qtrobot.sh` does not install or modify system packages. It checks that a
ROS environment is sourced and builds the workspace with `catkin_make`.

If ROS is installed but not sourced yet, source the matching setup file first,
for example:

```bash
source /opt/ros/noetic/setup.bash
```

## Run the starter node

Start the ROS master and QTrobot drivers using the normal QTrobot startup
procedure. Then, in a new terminal:

```bash
cd /path/to/companion_bot
source /opt/ros/$ROS_DISTRO/setup.bash
source ROS_file/devel/setup.bash
roslaunch companion_bot companion_bot.launch
```

The node waits for `/qt_robot/speech/say` and says the configured greeting.
Change it without editing Python:

```bash
roslaunch companion_bot companion_bot.launch \
  greeting:="Hello from the companion bot" \
  speak_on_start:=true
```

To start the node without speaking, useful while developing other behavior:

```bash
roslaunch companion_bot companion_bot.launch speak_on_start:=false
```

## Development loop

1. Edit `ROS_file/src/companion_bot/scripts/companion_bot_node.py`.
2. Rebuild after changing package metadata or launch files:
   `cd ROS_file && catkin_make`.
3. Source `ROS_file/devel/setup.bash` in each new terminal.
4. Run `roslaunch companion_bot companion_bot.launch`.

The node is intentionally small so speech, camera, emotion, and conversation
features can be added as separate ROS interfaces without hiding hardware errors.
