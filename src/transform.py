#!/usr/bin/env python
import rospy
import rospkg
import sys
import thread, time
from visualization_msgs.msg import MarkerArray
from visualization_msgs.msg import Marker
import numpy as np
import argparse
import cv2

"""
# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required = True, help = "Path to the image")
args = vars(ap.parse_args())
"""
rospack = rospkg.RosPack()
fpath = rospack.get_path('exercise3')

yaml_file=rospy.get_param('yaml_file')
import yaml
stram = open(yaml_file, "r")
#print yaml.load(stram)
doc=yaml.load(stram)
resolution=doc["resolution"]
origin=doc["origin"]


# load the image, clone it for output, and then convert it to grayscale
map_file=rospy.get_param('map_file')
image = cv2.imread(map_file)
output = image.copy()
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
gray=cv2.flip(gray, flipCode=0)

# detect circles in the image
circles = cv2.HoughCircles(gray, cv2.cv.CV_HOUGH_GRADIENT, 1.2, 75)

# ensure at least some circles were found
if circles is not None:
	# convert the (x, y) coordinates and radius of the circles to integers
	circles = np.round(circles[0, :]).astype("int")

	# loop over the (x, y) coordinates and radius of the circles
	for (x, y, r) in circles:
		# draw the circle in the output image, then draw a rectangle
		# corresponding to the center of the circle
		if r*resolution>0.8 and resolution<1.5:
			cv2.circle(output, (x, y), r, (0, 255, 0), 4)
			cv2.rectangle(output, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)

	# show the output image
	#cv2.imshow("output", np.hstack([image, output]))
	#cv2.waitKey(0)
	position_list=[]
	for (x, y, r) in circles:
		if r*0.05>0.8 and r*0.05<2.1:
			position_list.append((x,y))
	#print position_list

else:
	print('No circles found')



############################################################
#Start publishing markers

topic = 'visualization_marker'
publisher = rospy.Publisher(topic, Marker, queue_size=1)

rospy.init_node('register')

markerArray = MarkerArray()

while not rospy.is_shutdown():
   marker = Marker()
   marker.header.frame_id = 'map'
   marker.header.stamp = rospy.Time.now()
   marker.type = marker.SPHERE
   marker.action = marker.ADD
   marker.ns = 'basic_shapes'
   marker.id = 0
   marker.scale.x = 0.3
   marker.scale.y = 0.3
   marker.scale.z = 0.3
   marker.color.r = 0.0
   marker.color.g = 1.0
   marker.color.b = 0.0
   marker.color.a = 1.0
   counter=0
   for poses in position_list:
	   marker.id=counter
	   marker.pose.orientation.w = 1.0
	   marker.pose.position.x = poses[0]*resolution+origin[0]
	   marker.pose.position.y = poses[1]*resolution+origin[1]
	   marker.pose.position.z = 0
	   markerArray.markers.append(marker)
	   counter=counter+1
           publisher.publish(marker)
