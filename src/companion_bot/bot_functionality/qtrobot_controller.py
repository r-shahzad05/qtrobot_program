import rclpy
from qtrobot_interfaces.srv import (
    FaceEmotionList,
    FaceEmotionShow,
    GestureFileList,
    GestureFilePlay,
    TtsEngineSayText,
)


class QTrobotController:
    def __init__(self, node):
        self.node = node
        self.say_client = node.create_client(
            TtsEngineSayText,
            "/qtrobot/tts/engine/say/text",
        )
        self.emotion_client = node.create_client(
            FaceEmotionShow,
            "/qtrobot/face/emotion/show",
        )
        self.gesture_client = node.create_client(
            GestureFilePlay,
            "/qtrobot/gesture/file/play",
        )
        self.emotion_list_client = node.create_client(
            FaceEmotionList,
            "/qtrobot/face/emotion/list",
        )
        self.gesture_list_client = node.create_client(
            GestureFileList,
            "/qtrobot/gesture/file/list",
        )

    def _call(self, client, request):
        if not client.wait_for_service(timeout_sec=30.0):
            self.node.get_logger().error(
                f"Service unavailable: {client.srv_name}"
            )
            return None

        future = client.call_async(request)
        rclpy.spin_until_future_complete(self.node, future)

        if future.exception() is not None:
            self.node.get_logger().error(
                f"Service call failed: {future.exception()}"
            )
            return None

        return future.result()

    def say(self, text):
        request = TtsEngineSayText.Request(text=text)
        result = self._call(self.say_client, request)
        return result is not None and result.status and result.result

    def show_emotion(self, emotion, speed=0.0):
        request = FaceEmotionShow.Request(emotion=emotion, speed=speed)
        result = self._call(self.emotion_client, request)
        return result is not None and result.status and result.result

    def show_gesture(self, gesture, speed_factor=1.0):
        request = GestureFilePlay.Request(
            gesture=gesture,
            speed_factor=speed_factor,
        )
        result = self._call(self.gesture_client, request)
        return result is not None and result.status and result.result

    def list_emotions(self):
        result = self._call(
            self.emotion_list_client,
            FaceEmotionList.Request(),
        )
        return result.result if result is not None and result.status else []

    def list_gestures(self):
        result = self._call(
            self.gesture_list_client,
            GestureFileList.Request(),
        )
        return result.result if result is not None and result.status else []
