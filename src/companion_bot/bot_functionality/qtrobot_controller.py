import sys
import rospy
from qt_robot_interface.srv import speech_say, emotion_show, gesture_play

class QTrobotController:

    def say(self, text):
        rospy.wait_for_service("/qt_robot/speech/say")
        try:
            speech_service = rospy.ServiceProxy("/qt_robot/speech/say", speech_say ) #speechsay is part of qtrobot interface
            speech_service(text)
            rospy.loginfo("Speech done")
            return True

        except rospy.ServiceException as e:
            rospy.logerr("Service call failed, %s", e)
            return False


    def show_emotion(self, emotion):

        rospy.wait_for_service("/qt_robot/emotion/show")
        try:
            emotion_service = rospy.ServiceProxy("/qt_robot/emotion/show", emotion_show)
            emotion_service(emotion)
            rospy.loginfo("Emotion shown")
            return True

        except  rospy.ServiceException as e:
            rospy.logerr("Service call failed, %s", e)
            return False
        

    def show_gesture(self, gesture):
        rospy.wait_for_service("/qt_robot/gesture/play")

        try:
            gesture_service = rospy.ServiceProxy("/qt_robot/gesture/play", gesture_play)
            gesture_service(gesture, 0)
            rospy.loginfo("Gesture finished")
            return True

        except rospy.ServiceException as e:
            rospy.logerr("Service call failed, %s", e)
            return False

