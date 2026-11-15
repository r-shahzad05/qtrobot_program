import rclpy
from qtrobot_interfaces.srv import (
    FaceEmotionList,
    GestureFileList,
)


class QTrobotController:
    def __init__(self, node):
        self.node = node
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
