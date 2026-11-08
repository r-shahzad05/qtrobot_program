import sys
import rospy
from qt_robot_interface.srv import *

class QTrobotController:
    def say(self, text):
        rospy.Publisher('/qt_robot/speech/say')
        pass

    def show_emotion(self, emotion):
        try:
            await rospy.ServiceProxy('/qt_robot/emotion/show', emotion)
        except  Error:
            print("Invalid emotion: ", emotion)
            await rospy.ServiceProxy('/qt_robot/emotion/show', 'QT/neutral')
        
        pass

