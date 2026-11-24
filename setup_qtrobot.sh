#!/usr/bin/env bash
set -euo pipefail

workspace="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/ROS_file" && pwd)"

if [[ -z "${ROS_DISTRO:-}" ]]; then
    echo "ROS is not sourced. Source /opt/ros/<distribution>/setup.bash first." >&2
    exit 1
fi

if ! command -v catkin_make >/dev/null 2>&1; then
    echo "catkin_make is unavailable in the sourced ROS environment." >&2
    exit 1
fi

echo "Building companion_bot in ${workspace}"
cd "${workspace}"
catkin_make

echo
echo "Build complete. Source the workspace with:"
echo "  source ${workspace}/devel/setup.bash"
