from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
import numpy as np
import gpiozero


camera = PiCamera()
image_width = 640
image_height = 480
camera.resolution = (image_width, image_height)
camera.framerate = 32
rawCapture = PiRGBArray(camera,size = (image_width, image_height))
center_image_x = image_width/2
center_image_y = image_height/2
minimum_area = 250
maximum_area = 100000

boat = gpiozero.Robot(left = (20,21), right = (23,24))
forward_speed= 1.0
turn_speed = 0.8

Val_Hue = 24

Col_low_Val = np.array([Val_Hue-10,100,100])
Col_Up_Val = np.array([Val_Hue+10,255,255])

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    image = frame.array
 
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
 
    color_mask = cv2.inRange(hsv, Col_low_Val, Col_Up_Val)
 
    countours, hierarchy = cv2.findContours(color_mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
 
    trash_area= 0
    trash_x = 0
    trash_y = 0
 
    for contour in countours:
        x, y, width, height = cv2.boundingRect(contour)
        found_area = width * height
        center_x = x + (width / 2)
        center_y = y + (height / 2)
        if trash_area < found_area:
            trash_area = found_area
            trash_x = center_x
            trash_y = center_y
    if trash_area > 0:
        trash_location = [trash_area, trash_x, trash_y]
    else:
        trash_location = None
 
    if trash_location:
        if (trash_location[0] > minimum_area) and (trash_location[0] < maximum_area):
            if trash_location[1] > (center_image_x + (image_width/3)):
                robot.right(turn_speed)
                print("Turning right")
            elif trash_location[1] < (center_image_x - (image_width/3)):
                robot.left(turn_speed)
                print("Turning left")
            else:
                robot.forward(forward_speed)
                print("Forward")
        elif (trash_location[0] < minimum_area):
            robot.left(turn_speed)
            print("Target isn't large enough, searching")
        else:
            robot.stop()
            print("Target large enough, stopping")
    else:
        robot.left(turn_speed)
        print("Target not found, searching")
 
    rawCapture.truncate(0)


