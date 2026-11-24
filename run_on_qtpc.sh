#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
gateway_dir="${QTROBOT_GATEWAY_DIR:-${HOME}/qtrobot-service-hub-gateway-ros}"
gateway_repo="${QTROBOT_GATEWAY_REPO:-https://github.com/luxai-qtrobot/qtrobot-service-hub-gateway-ros.git}"
ros2_workspace="${ROS2_WS:-${HOME}/ros2_ws}"
ros_setup="${ROS_SETUP:-/opt/ros/jazzy/setup.bash}"
venv="${project_root}/.venv"
python_bin="${PYTHON_BIN:-python3.12}"
robot_ip="${ROBOT_IP:-}"

usage() {
    cat <<EOF
Usage:
  $0 install
  ROBOT_IP=<robot-ip> $0 run

Optional environment variables:
  ROS_SETUP             ROS2 setup file (default: /opt/ros/jazzy/setup.bash)
  ROS2_WS               ROS2 workspace (default: ~/ros2_ws)
  QTROBOT_GATEWAY_DIR   Gateway checkout (default: ~/qtrobot-service-hub-gateway-ros)
  PYTHON_BIN            Python 3.12 executable (default: python3.12)
EOF
}

require_file() {
    if [[ ! -f "$1" ]]; then
        echo "Required file not found: $1" >&2
        exit 1
    fi
}

install_all() {
    require_file "${ros_setup}"

    if ! command -v "${python_bin}" >/dev/null 2>&1; then
        echo "Python 3.12 is required. Set PYTHON_BIN to its executable." >&2
        exit 1
    fi

    if [[ ! -d "${gateway_dir}" ]]; then
        if ! command -v git >/dev/null 2>&1; then
            echo "Git is required to download the QTrobot gateway." >&2
            exit 1
        fi
        git clone "${gateway_repo}" "${gateway_dir}"
    fi

    source "${ros_setup}"
    mkdir -p "${ros2_workspace}/src"

    if [[ ! -e "${ros2_workspace}/src/qtrobot_interfaces" ]]; then
        ln -s "${gateway_dir}/qtrobot_interfaces" \
            "${ros2_workspace}/src/qtrobot_interfaces"
    fi

    cd "${ros2_workspace}"
    colcon build --packages-select qtrobot_interfaces
    source "${ros2_workspace}/install/setup.bash"

    if [[ ! -d "${venv}" ]]; then
        "${python_bin}" -m venv --system-site-packages "${venv}"
    fi

    "${venv}/bin/python" -m pip install --upgrade pip
    "${venv}/bin/python" -m pip install \
        -r "${gateway_dir}/requirements.txt" \
        -r "${project_root}/requirements-face-detection.txt"

    cd "${project_root}/ROS_file"
    colcon build

    echo "Installation complete."
}

run_all() {
    require_file "${ros_setup}"

    if [[ -z "${robot_ip}" ]]; then
        echo "Set ROBOT_IP before running, for example:" >&2
        echo "  ROBOT_IP=192.168.1.50 $0 run" >&2
        exit 1
    fi

    source "${ros_setup}"
    require_file "${ros2_workspace}/install/setup.bash"
    source "${ros2_workspace}/install/setup.bash"
    require_file "${project_root}/ROS_file/install/setup.bash"
    source "${project_root}/ROS_file/install/setup.bash"
    source "${venv}/bin/activate"

    cd "${gateway_dir}"
    python -m gateway.qtrobot_ros2 \
        --ros-args \
        -p "robot_ip:=${robot_ip}" \
        -r __ns:=/qtrobot &
    gateway_pid=$!

    cleanup() {
        kill "${gateway_pid}" 2>/dev/null || true
    }
    trap cleanup EXIT INT TERM

    sleep 2
    ros2 run companion_bot companion_bot_node.py
}

case "${1:-}" in
    install)
        install_all
        ;;
    run)
        run_all
        ;;
    *)
        usage
        exit 2
        ;;
esac
