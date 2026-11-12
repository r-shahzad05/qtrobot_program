cmake_minimum_required(VERSION 3.8)
project(companion_bot)

find_package(ament_cmake REQUIRED)
find_package(rclpy REQUIRED)
find_package(std_msgs REQUIRED)
find_package(qtrobot_interfaces REQUIRED)

install(
  PROGRAMS
    scripts/companion_bot_node.py
    bot_functionality/camera_operations.py
  DESTINATION lib/${PROJECT_NAME}
)

install(
  DIRECTORY bot_functionality
  DESTINATION lib/python3.12/site-packages/${PROJECT_NAME}
)

install(
  DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
