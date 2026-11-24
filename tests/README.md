# Companion bot module smoke tests

These tests mock ROS topics, robot services, the camera, the microphone, and the
OpenAI client. They test module behavior without contacting QTPC hardware or
making an API request.

Run from the ROS workspace:

```bash
cd /path/to/ROS_file
python3 -m unittest discover -s tests -p "test_*.py" -v
```
