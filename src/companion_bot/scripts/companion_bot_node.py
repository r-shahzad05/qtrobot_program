#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from companion_bot.bot_functionality.qtrobot_controller import QTrobotController


class QT_companionbotnode(Node):
    def __init__(self):
        super().__init__("companion_bot")

        self.robot = QTrobotController(self)

        self.robot.say("Hello I am a companion robot")
        self.robot.show_emotion("QT/happy")



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
