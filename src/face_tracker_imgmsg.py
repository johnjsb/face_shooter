#!/usr/bin/env python
# ========================================= #
# Original author : Dom Larkin
# converted from face_tracker2_node.py by Benjamin Abruzzo 2018-09-12
# ========================================= #

# Import required Python code.
import sys
import rospy
import cv2
from std_msgs.msg import String
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
from geometry_msgs.msg import Vector3
from os.path import expanduser
home = expanduser("~")
import time

class face_tracker():
    # Must have __init__(self) function for a class, similar to a C++ class constructor.
    def __init__(self):
        self.new_image = False
        self.rate = rospy.Rate(30) # 30hz sleep rate for ros
        self.bridge = CvBridge()

        # define ros publishers and subscribers
        self.image_topic = rospy.get_param('~subscribed_image_topic', '/ardrone/image_raw')
        # print('subscribing to: ' + self.image_topic)
        self.image_sub = rospy.Subscriber(self.image_topic,Image,self.image_callback)
        
        self.centroid_topic = rospy.get_param('~publishing_centroid_topic', '/face_centroid')
        # print('publishing on: ' + self.centroid_topic)
        self.pub_centroid = rospy.Publisher(self.centroid_topic, Vector3, queue_size=1)  

    def image_callback(self,data):
        # print('image_callback(self,data):')
        # call back to read image message and save it into the class
        try:
            # print('try:')
            self.cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
            self.new_image = True
        except CvBridgeError as e:
            print(e)

if __name__ == '__main__':
    # Initialize the node and name it.
    rospy.init_node('face_tracker')
    # Go to class functions that do all the heavy lifting. Do error checking.
    try:
        ft = face_tracker()
    except rospy.ROSInterruptException: pass

    # Load params if provided else use the defaults
    haar_file_face = rospy.get_param("~haar_face_file")
    display_original_image = rospy.get_param("display_original_image","0") #default is off
    display_tracking_image = rospy.get_param("display_tracking_image","1") #default is on

    # Create the classifier
    face_cascade=cv2.CascadeClassifier(haar_file_face)

    # Process the images when new ones arrive
    last_time = 0
    num_frames = 0
    rate = rospy.Rate(30) # 30hz
    while not rospy.is_shutdown():
        # print('while not rospy.is_shutdown():')
        if (ft.new_image):
            if (display_original_image): # Dispaly the image if param is set to true       
                cv2.imshow('original',ft.cv_image)              
            # convert new image to gray scale
            gray = cv2.cvtColor(ft.cv_image, cv2.COLOR_BGR2GRAY)
            # Use the classifier to find faces
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            center=Vector3()
            for index,(x,y,w,h) in enumerate(faces): # For each face publish the centroid
                #print("Frame is: %d by %d and x,y %d, %d" %(frame.shape[1],frame.shape[0],x,y))
                ft.cv_tracking = cv2.rectangle(ft.cv_image,(x,y),(x+w,y+h),(255,0,0),2) # Draw a frame around each face
                cv2.imshow('tracking',ft.cv_tracking)
                # publish center of face
                center.x=x+w/2
                center.y=y+h/2
                center.z=index+1 # unique id for multiple faces, zero indexed
            if center.z != 0: # then at least one face was found
                ft.pub_centroid.publish(center)

        cv2.waitKey(1) # Needed for showing image
        # wait for new image to arrive
        rate.sleep() 
    # when done
    cv2.destroyAllWindows()
