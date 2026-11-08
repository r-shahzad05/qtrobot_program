cmake_minimum_required(VERSION 3.0.2)
project(companion_bot)

find_package(catkin REQUIRED COMPONENTS
  rospy
  qt_robot_interface
)

catkin_package()

catkin_install_python(PROGRAMS
  scripts/companion_bot_node.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

install(DIRECTORY launch
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)
