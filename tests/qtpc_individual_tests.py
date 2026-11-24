#!/usr/bin/env python3

import argparse
import os
import sys
import time
from pathlib import Path

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BOT_PATH = PROJECT_ROOT / "src" / "companion_bot" / "bot_functionality"
sys.path.insert(0, str(BOT_PATH))

from copilot_emotion_gesturelister_QT import QTrobotController
from llm_client import llm_client
from microphone_operations import QT_mic_operations
from qt_controller import QT_controller


def ok(name, detail=""):
    print(f"[PASS] {name}" + (f": {detail}" if detail else ""), flush=True)


def fail(name, detail):
    print(f"[FAIL] {name}: {detail}", flush=True)


def test_tts():
    rclpy.init()
    node = Node("qtpc_tts_test")
    robot = QT_controller(node)

    try:
        result = robot.say_text("QTPC text to speech test")
        if result is None:
            fail("TTS", "speech service unavailable")
        else:
            ok("TTS", "speech service returned a result")
    except Exception as error:
        fail("TTS", error)
    finally:
        node.destroy_node()
        rclpy.shutdown()


def test_services():
    rclpy.init()
    node = Node("qtpc_service_test")
    controller = QTrobotController(node)

    try:
        emotions = controller.list_emotions()
        gestures = controller.list_gestures()
        ok("Emotion list", ", ".join(emotions) if emotions else "no emotions returned")
        ok("Gesture list", ", ".join(gestures) if gestures else "no gestures returned")

        robot = QT_controller(node)
        emotion = "neutral" if "neutral" in emotions else (emotions[0] if emotions else None)
        gesture = gestures[0] if gestures else None

        if emotion:
            emotion_result = robot.show_emotion(emotion)
            ok("Emotion command", emotion) if emotion_result is not None else fail("Emotion command", "service unavailable")
        if gesture:
            gesture_result = robot.show_gesture(gesture)
            ok("Gesture command", gesture) if gesture_result is not None else fail("Gesture command", "service unavailable")
    except Exception as error:
        fail("QT service test", error)
    finally:
        node.destroy_node()
        rclpy.shutdown()


def test_camera():
    rclpy.init()
    node = Node("qtpc_camera_test")
    received = []
    subscription = node.create_subscription(
        String,
        "/companion_bot/detected_emotion",
        lambda message: received.append(message.data),
        10,
    )

    print("Camera test running. Look at the robot camera for 15 seconds.", flush=True)
    end_time = time.monotonic() + 15.0
    while time.monotonic() < end_time:
        rclpy.spin_once(node, timeout_sec=0.5)

    subscription.destroy()
    if received:
        ok("Camera/emotion", f"received emotions: {', '.join(sorted(set(received)))}")
    else:
        fail("Camera/emotion", "no emotion message received; check the camera node and gateway")

    node.destroy_node()
    rclpy.shutdown()


def test_microphone():
    rclpy.init()
    node = Node("qtpc_microphone_test")
    transcriptions = []

    try:
        mic = QT_mic_operations(
            node,
            lambda text: transcriptions.append(text),
        )
        print("Microphone test running. Say a short sentence within 20 seconds.", flush=True)
        end_time = time.monotonic() + 20.0
        while time.monotonic() < end_time:
            rclpy.spin_once(node, timeout_sec=0.5)

        if transcriptions:
            ok("Microphone/speech recognition", transcriptions[-1])
        else:
            fail(
                "Microphone/speech recognition",
                "no transcription; speak, then check microphone topics and VOSK_MODEL_PATH",
            )
    except Exception as error:
        fail("Microphone/speech recognition", error)
    finally:
        node.destroy_node()
        rclpy.shutdown()


def test_llm():
    try:
        client = llm_client()
        history = BOT_PATH / "conversation_history.txt"
        result, emotion, gesture = client.generate_response(
            "This is a QTPC module test.",
            "neutral",
            str(history),
        )
        ok(
            "LLM",
            f"response={result!r}, emotion={emotion}, gesture={gesture}",
        )
    except Exception as error:
        fail("LLM", error)


MODULE_TESTS = {
    "tts": test_tts,
    "camera": test_camera,
    "microphone": test_microphone,
    "llm": test_llm,
    "services": test_services,
}


def main():
    parser = argparse.ArgumentParser(
        description="Run one companion-bot module at a time on QTPC."
    )
    parser.add_argument(
        "--module",
        choices=[*MODULE_TESTS, "all"],
        required=True,
    )
    args = parser.parse_args()

    if args.module == "all":
        for name, test in MODULE_TESTS.items():
            print(f"\n=== {name.upper()} ===", flush=True)
            test()
    else:
        MODULE_TESTS[args.module]()


if __name__ == "__main__":
    main()
