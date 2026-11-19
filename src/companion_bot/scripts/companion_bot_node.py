#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from companion_bot.bot_functionality.qt_controller import QT_controller
from companion_bot.bot_functionality.llm_client import llm_client
from companion_bot.bot_functionality.microphone_operations import QT_mic_operations
from std_msgs.msg import String


class QT_companionbotnode(Node):
    def __init__(self):
        super().__init__("companion_bot")

        self.robot = QT_controller(self)
        self.llm = llm_client()

        self.latest_emotion = "neutral"

        self.emotion_sub = self.create_subscription(String, "/companion_bot/detected_emotion", self.emotion_callback,10)
        self.microphone = QT_mic_operations(self, self.generate_robot_response)

        self.robot.say_text("Hello World")

    def emotion_callback(self, message):
        self.latest_emotion = message.data

    def generate_robot_response (self, text):
        try:
            response, emotion, gesture = self.llm.generate_response(text, self.latest_emotion, "conversation_history.txt")

        except Exception as error:
            self.logger().error(f"LLM failed: {error}")
            return

        self.robot.say_text(response)
        self.robot.show_emotion(emotion)
        self.robot.show_gesture(gesture)

        



def main(args=None):
    rclpy.init(args=args)
    node = QT_companionbotnode()

    try:
        rclpy.spin(node)

    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()


