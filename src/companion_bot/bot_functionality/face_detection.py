import rospy
from qt_nuitrack_app.msg import faces
import json
import cv2
import numpy as np


# https://docs.luxai.com/docs/modules/camera maybe use this for the faces?


# Faces message structure 
# qt_nuitrack_app/FaceInfo[] faces
#     int32 id
#     string gender
#     int32 age_years
#     string age_type
#     float64 emotion_neutral
#     float64 emotion_angry
#     float64 emotion_happy
#     float64 emotion_surprise
#     float64[] rectangle
#     float64[] left_eye
#     float64[] right_eye
#     float64[] angles

def detect_face():
    face_detect = rospy.Sunscriber('/qt_nuitrack_app/faces', Faces, face_callback)
    