import cv2
import cvzone.HandTrackingModule as handTracking
import math
class VideoCamera(object):
    def __init__(self):
        self.video=cv2.VideoCapture(-1)

    def __del__(self):
        self.video.release() 

    def get_frame(self):
        ret,frame=self.video.read()
        ret,jpeg=cv2.imencode('.jpg',frame)   
        return jpeg.tobytes()    
