cmake_minimum_required(VERSION 3.8)
project(companion_bot)

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(rclpy REQUIRED)
find_package(std_msgs REQUIRED)
find_package(qtrobot_interfaces REQUIRED)

install(
  PROGRAMS
    scripts/companion_bot_node.py
    bot_functionality/camera_operations.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_get_python_install_dir(PYTHON_INSTALL_DIR)
install(
  DIRECTORY bot_functionality
  DESTINATION ${PYTHON_INSTALL_DIR}/${PROJECT_NAME}
)

install(
  DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
