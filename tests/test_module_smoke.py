import importlib
import os
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import MagicMock


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BOT_PATH = PROJECT_ROOT / "src" / "companion_bot" / "bot_functionality"
sys.path.insert(0, str(BOT_PATH))


def install_module(name, **attributes):
    module = types.ModuleType(name)
    for key, value in attributes.items():
        setattr(module, key, value)
    sys.modules[name] = module
    return module


def install_ros_stubs():
    rclpy = install_module("rclpy")
    rclpy.init = MagicMock()
    rclpy.shutdown = MagicMock()
    rclpy.spin = MagicMock()
    rclpy.spin_until_future_complete = MagicMock()

    rclpy_node = install_module("rclpy.node")

    class Node:
        def __init__(self, name=None):
            self.name = name

        def get_logger(self):
            logger = MagicMock()
            logger.info = MagicMock()
            logger.warning = MagicMock()
            logger.error = MagicMock()
            return logger

    rclpy_node.Node = Node
    rclpy.node = rclpy_node

    std_msgs = install_module("std_msgs")
    std_msgs_msg = install_module("std_msgs.msg")
    std_msgs_msg.String = type("String", (), {})
    std_msgs.msg = std_msgs_msg

    qtrobot_interfaces = install_module("qtrobot_interfaces")
    qtrobot_msg = install_module("qtrobot_interfaces.msg")
    qtrobot_srv = install_module("qtrobot_interfaces.srv")

    for name in ("ImageFrameRaw", "MicEventFrame", "AudioFrameRaw"):
        setattr(qtrobot_msg, name, type(name, (), {}))

    for name in (
        "FaceLook",
        "FaceEmotionShow",
        "GestureFilePlay",
        "TtsEngineSayText",
        "FaceEmotionList",
        "GestureFileList",
    ):
        request_type = type(
            "Request",
            (),
            {
                "__init__":
                lambda self, **kwargs: self.__dict__.update(kwargs)
            },
        )
        setattr(
            qtrobot_srv,
            name,
            type(name, (), {"Request": request_type}),
        )

    qtrobot_interfaces.msg = qtrobot_msg
    qtrobot_interfaces.srv = qtrobot_srv

    deepface = install_module("deepface")
    deepface.DeepFace = type(
        "DeepFace",
        (),
        {"analyze": staticmethod(MagicMock())},
    )

    vosk = install_module("vosk")
    vosk.Model = MagicMock
    vosk.KaldiRecognizer = MagicMock


class FakeFuture:
    def __init__(self):
        self.done = MagicMock(return_value=True)
        self.result = MagicMock(return_value=None)


class LLMClientTests(unittest.TestCase):
    def setUp(self):
        openai = install_module("openai")
        openai.OpenAI = MagicMock
        dotenv = install_module("dotenv")
        dotenv.load_dotenv = MagicMock()
        os.environ["openAI_api_key"] = "test-key"
        sys.modules.pop("llm_client", None)
        self.module = importlib.import_module("llm_client")

    def tearDown(self):
        os.environ.pop("openAI_api_key", None)

    def test_missing_api_key_raises(self):
        os.environ.pop("openAI_api_key", None)
        with self.assertRaises(ValueError):
            self.module.llm_client()

    def test_generate_response_parses_llm_format(self):
        client = self.module.llm_client()
        completion = types.SimpleNamespace(
            choices=[
                types.SimpleNamespace(
                    message=types.SimpleNamespace(
                        content="0,happy,wave,Hello there"
                    )
                )
            ]
        )
        client.client.chat.completions.create = MagicMock(
            return_value=completion
        )

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "bot_personality.txt").write_text("Friendly bot")
            (root / "important_memories.txt").write_text("")
            history = root / "history.txt"
            history.write_text("")
            old_cwd = os.getcwd()
            os.chdir(root)
            try:
                response = client.generate_response(
                    "Hello",
                    "neutral",
                    str(history),
                )
            finally:
                os.chdir(old_cwd)

        self.assertEqual(response, ("Hello there", "happy", "wave"))


class CameraTests(unittest.TestCase):
    def setUp(self):
        install_ros_stubs()
        sys.modules.pop("camera_operations", None)
        self.module = importlib.import_module("camera_operations")

    def test_rgb_frame_conversion(self):
        import numpy as np

        detector = object.__new__(self.module.FaceDetectorNode)
        message = types.SimpleNamespace(
            width=2,
            height=1,
            encoding="rgb8",
            data=bytes([255, 0, 0, 0, 255, 0]),
        )
        image = detector.convert_image(message)
        self.assertEqual(image.shape, (1, 2, 3))
        np.testing.assert_array_equal(
            image[0, 0],
            np.array([0, 0, 255], dtype=np.uint8),
        )

    def test_malformed_frame_is_rejected(self):
        detector = object.__new__(self.module.FaceDetectorNode)
        message = types.SimpleNamespace(
            width=2,
            height=2,
            encoding="rgb8",
            data=bytes([0, 0, 0]),
        )
        with self.assertRaises(ValueError):
            detector.convert_image(message)


class MicrophoneTests(unittest.TestCase):
    def setUp(self):
        install_ros_stubs()
        sys.modules.pop("microphone_operations", None)
        self.module = importlib.import_module("microphone_operations")

    def test_recording_starts_stops_and_buffers_audio(self):
        mic = object.__new__(self.module.QT_mic_operations)
        mic.recording = False
        mic.audio_buffer = []
        mic.node = types.SimpleNamespace(get_logger=MagicMock())
        mic.detect_audio_then_record(
            types.SimpleNamespace(activity=True)
        )
        mic.sample_rate = 16000
        mic.sample_width = 2
        mic.channels = 1
        mic.record_audio(
            types.SimpleNamespace(
                sample_rate=16000,
                sample_width=2,
                channels=1,
                data=b"\x01\x02",
            )
        )
        self.assertTrue(mic.recording)
        self.assertEqual(mic.audio_buffer, [b"\x01\x02"])

        mic.finish_recording = MagicMock()
        mic.detect_audio_then_record(
            types.SimpleNamespace(activity=False)
        )
        mic.finish_recording.assert_called_once()


class ControllerTests(unittest.TestCase):
    def setUp(self):
        install_ros_stubs()
        sys.modules.pop("qt_controller", None)
        sys.modules.pop("copilot_emotion_gesturelister_QT", None)
        self.controller_module = importlib.import_module("qt_controller")

    def make_client(self):
        return types.SimpleNamespace(
            wait_for_service=MagicMock(return_value=True),
            call_async=MagicMock(return_value=FakeFuture()),
        )

    def test_qt_controller_builds_service_requests(self):
        speech = self.make_client()
        emotion = self.make_client()
        gesture = self.make_client()
        node = types.SimpleNamespace(
            create_client=MagicMock(
                side_effect=[speech, emotion, gesture]
            )
        )
        sys.modules["rclpy"].spin_until_future_complete = MagicMock()

        controller = self.controller_module.QT_controller(node)
        result = controller.say_text("Hello")

        self.assertIsNone(result)
        speech.wait_for_service.assert_called_once()
        speech.call_async.assert_called_once()

    def test_robot_list_controller_handles_missing_service(self):
        module = importlib.import_module(
            "copilot_emotion_gesturelister_QT"
        )
        emotion_client = self.make_client()
        emotion_client.wait_for_service = MagicMock(return_value=False)
        emotion_client.srv_name = "/qtrobot/face/emotion/list"
        gesture_client = self.make_client()
        node = types.SimpleNamespace(
            create_client=MagicMock(
                side_effect=[emotion_client, gesture_client]
            ),
            get_logger=MagicMock(),
        )
        controller = module.QTrobotController(node)
        self.assertEqual(controller.list_emotions(), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
