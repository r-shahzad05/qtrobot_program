#!/usr/bin/env python3

import json
import time

import cv2
import numpy as np
import rclpy
from deepface import DeepFace
from qtrobot_interfaces.msg import ImageFrameRaw
from qtrobot_interfaces.srv import FaceLook
from rclpy.node import Node


class FaceDetectorNode(Node):
    def __init__(self):
        super().__init__("face_detector")

        self.declare_parameter("analysis_interval", 0.5)
        self.declare_parameter("gaze_duration", 0.2)
        self.declare_parameter("invert_gaze_x", False)

        self.analysis_interval = float(
            self.get_parameter("analysis_interval").value
        )
        self.gaze_duration = float(
            self.get_parameter("gaze_duration").value
        )
        self.invert_gaze_x = bool(
            self.get_parameter("invert_gaze_x").value
        )

        self.last_analysis_time = 0.0
        self.look_future = None
        self.detected_emotion = None

        self.look_client = self.create_client(
            FaceLook,
            "/qtrobot/face/look",
        )

        self.subscription = self.create_subscription(
            ImageFrameRaw,
            "/qtrobot/camera/color/image",
            self.image_callback,
            10,
        )

        self.get_logger().info("Face detector is ready")

    def image_callback(self, message):
        current_time = time.monotonic()

        if current_time - self.last_analysis_time < self.analysis_interval:
            return

        self.last_analysis_time = current_time

        try:
            image = self.convert_image(message)
            result = self.analyze_face(image)

        except (KeyError, ValueError) as error:
            self.get_logger().warning(
                f"Could not process camera frame: {error}"
            )
            return

        if result is None:
            return

        emotion, face_region = result
        self.detected_emotion = emotion

        self.get_logger().info(
            f"Detected emotion: {emotion}"
        )

        self.look_at_face(
            face_region,
            message.width,
            message.height,
        )

    def convert_image(self, message):
        width = int(message.width)
        height = int(message.height)
        encoding = message.encoding.lower()

        channels_by_encoding = {
            "rgb8": 3,
            "bgr8": 3,
            "rgba8": 4,
            "bgra8": 4,
            "mono8": 1,
        }

        if encoding not in channels_by_encoding:
            raise ValueError(
                f"Unsupported image encoding: {message.encoding}"
            )

        channels = channels_by_encoding[encoding]

        image_data = np.frombuffer(
            message.data,
            dtype=np.uint8,
        )

        expected_size = width * height * channels

        if image_data.size != expected_size:
            raise ValueError(
                f"Expected {expected_size} bytes, "
                f"received {image_data.size}"
            )

        if channels == 1:
            image = image_data.reshape((height, width))
            return cv2.cvtColor(
                image,
                cv2.COLOR_GRAY2BGR,
            )

        image = image_data.reshape(
            (height, width, channels)
        )

        if encoding == "rgb8":
            return cv2.cvtColor(
                image,
                cv2.COLOR_RGB2BGR,
            )

        if encoding == "rgba8":
            return cv2.cvtColor(
                image,
                cv2.COLOR_RGBA2BGR,
            )

        if encoding == "bgra8":
            return cv2.cvtColor(
                image,
                cv2.COLOR_BGRA2BGR,
            )

        return image

    def analyze_face(self, image):
        results = DeepFace.analyze(
            img_path=image,
            actions=["emotion"],
            detector_backend="opencv",
            enforce_detection=False,
            silent=True,
        )

        if not results:
            return None

        if isinstance(results, dict):
            results = [results]

        valid_results = [
            result
            for result in results
            if result.get("region")
            and result.get("dominant_emotion")
        ]

        if not valid_results:
            return None

        largest_face = max(
            valid_results,
            key=lambda result: (
                result["region"].get("w", 0)
                * result["region"].get("h", 0)
            ),
        )

        return (
            largest_face["dominant_emotion"],
            largest_face["region"],
        )

    def look_at_face(
        self,
        face_region,
        image_width,
        image_height,
    ):
        if image_width <= 0 or image_height <= 0:
            return

        face_center_x = (
            face_region["x"]
            + face_region["w"] / 2
        )

        face_center_y = (
            face_region["y"]
            + face_region["h"] / 2
        )

        gaze_x = face_center_x / image_width
        gaze_y = face_center_y / image_height

        gaze_x = min(max(gaze_x, 0.0), 1.0)
        gaze_y = min(max(gaze_y, 0.0), 1.0)

        if self.invert_gaze_x:
            gaze_x = 1.0 - gaze_x

        if (
            self.look_future is not None
            and not self.look_future.done()
        ):
            return

        if not self.look_client.wait_for_service(
            timeout_sec=0.0
        ):
            self.get_logger().warning(
                "QTrobot face look service is unavailable"
            )
            return

        request = FaceLook.Request(
            l_eye=json.dumps([gaze_x, gaze_y]),
            r_eye=json.dumps([gaze_x, gaze_y]),
            duration=self.gaze_duration,
        )

        self.look_future = self.look_client.call_async(request)

