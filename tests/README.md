# Companion bot tests

## Mocked smoke tests

Run these without QTPC hardware:

```bash
cd /path/to/companion_bot
python3 -m unittest discover -s tests -p "test_module_smoke.py" -v
```

## Individual QTPC hardware tests

After sourcing ROS and the companion-bot workspace, run one module at a time:

```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
source /path/to/companion_bot/ROS_file/install/setup.bash

python3 tests/qtpc_individual_tests.py --module tts
python3 tests/qtpc_individual_tests.py --module camera
python3 tests/qtpc_individual_tests.py --module microphone
python3 tests/qtpc_individual_tests.py --module llm
python3 tests/qtpc_individual_tests.py --module services
python3 tests/qtpc_individual_tests.py --module all
```

Set `VOSK_MODEL_PATH` if the Vosk model is stored outside this project.
LLM tests require `openAI_api_key` in the project environment or the module
`bot_functionality/.env` file.
