import rclpy
from qtrobot_interfaces.srv import FaceEmotionShow, GestureFilePlay,TtsEngineSayText

class QT_controller:
    def __init__(self, node):
        self.node = node

        self.speech_client = node.create_client(TtsEngineSayText,"/qtrobot/tts/engine/say/text")

        self.emotion_client = node.create_client(FaceEmotionShow, "/qtrobot/face/emotion/show")

        self.gesture_client = node.create_client(GestureFilePlay, "/qtrobot/gesture/file/play")

    def say_text(self, text):
        request = TtsEngineSayText.Request(text=text)

        # wait for client to be open
        if not self.speech_client.wait_for_service(timeout_sec=30.0):                
            print("Speech service unavailable")
            return None

        future = self.speech_client.call_async(request)

        rclpy.spin_until_future_complete(self.node, future)
        return future.result()


    def show_emotion(self, emotion):
        request = FaceEmotionShow.Request(emotion=emotion, speed=0.0)
        
    
        if not self.emotion_client.wait_for_service(timeout_sec=30.0):
            print("Emotion service unavailable")
            return None                    
                
        future = self.emotion_client.call_async(request)
        
        rclpy.spin_until_future_complete(self.node, future)
        
        return future.result()
    
    def show_gesture(self, gesture):
        request = GestureFilePlay.Request(gesture=gesture, speed_factor=1.0)

        if not self.gesture_client.wait_for_service(timeout_sec=30.0):                    
            print("Service unavailable")
            return None
        
        future = self.gesture_client.call_async(request)
        
        rclpy.spin_until_future_complete(self.node, future)
        
        return future.result()
