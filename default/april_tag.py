#!/usr/bin/env python3

from networktables import NetworkTables
import dt_apriltags
import cv2
import sys
import numpy as np

# All networktable paths:
# 	NetworkTables.getDefault().getTable("apriltags").getEntry("cameraworking")
# 	NetworkTables.getDefault().getTable("apriltags").getSubTable("speakertags").getSubTable("pos").getEntry("x/y/z")
# 	NetworkTables.getDefault().getTable("apriltags").getSubTable("speakertags").getEntry("command")
#	NetworkTables.getDefault().getTable("apriltags").getSubTable("speakertags").getEntry("angletotag")

def main():
	# April tag init

	#focal_data = (1.14693147e+03, 1.13616617e+03, 3.86121647e+02, 2.43241211e+02) # 3264 x 2448 camera
	#focal_data = (429.78652322, 463.26344368, 328.23222028, 171.63344415)
	#focal_data = (699.3778103, 677.7161226393, 345.6059345, 207.12741326)
	#focal_data = (532, 502, 320, 240) # Brute forced, most accurate so far and most accurate at 4 yards
	focal_data = (429.9904094363701, 698.4435532175353, 430.2632673961912, 605.7394267757956)
	tag_size = 6.5 * 0.0254 # 0.0254 is the inches to meters ratio

	# Network table init

	if len(sys.argv) != 2:
		print("Need to initialize with an IP or as server")
		return

	if sys.argv[1] == "server":
		NetworkTables.initialize()
		print("Initialized as server")
	else:
		NetworkTables.initialize(sys.argv[1])
		print("Initialized as client")

	networktable_tags = NetworkTables.getDefault().getTable("apriltags")

	speaker_tags_subtable = networktable_tags.getSubTable("speakertags")
	center_x_entry = speaker_tags_subtable.getEntry("centerx")
	within_distance_entry = speaker_tags_subtable.getEntry("withindist")
	angle_to_tag_entry = speaker_tags_subtable.getEntry("angletotag")
	pos_subtable = speaker_tags_subtable.getSubTable("pos")

	# Camera init
	capture = cv2.VideoCapture(0)

	camera_working_entry = networktable_tags.getEntry("cameraworking")
	camera_working_entry.setBoolean(False)

	if not capture.isOpened():
		print("ERROR: Camera not open")
		capture.release()
		return
	else:
		print("Successfully opened camera")
		camera_working_entry.setBoolean(True)

	# Main program loop
	#try:
		print("Initializing program loop")
		#gotten_dist = 0
		#count = 0
		while True:
			exists, frame = capture.read()
			if exists:
				image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
				detector = dt_apriltags.Detector(families="tag36h11", quad_decimate=1.0)
				results = detector.detect(img=image, estimate_tag_pose=True, camera_params=focal_data, tag_size=tag_size)

				if len(results) > 0:
					for tag in results:
						tag_id = tag.tag_id
						if tag_id != 4 and tag_id != 7:
							continue

						pose = tag.pose_t

						# Position
						pos_x = pose[0]
						pos_y = pose[1]
						pos_z = pose[2]
						#gotten_dist += pos_z
						#count += 1
						#print(f"Running dist: {gotten_dist}, Count: {count}, Average: {gotten_dist/count}, X/Y/Z: {pos_x}, {pos_y}, {pos_z}")

						pos_subtable.getEntry("x").setNumber(pos_x)
						pos_subtable.getEntry("y").setNumber(pos_y)
						pos_subtable.getEntry("z").setNumber(pos_z)

						angle_to_tag_entry.setNumber(np.arctan2(pos_x, pos_z))
						within_distance_entry.setBoolean(((pos_z >= 3.4) and (pos_z <= 3.8)))
						print(f"Angle: {np.arctan2(pos_x, pos_z)}, Components: [{pos_x}, {pos_z}]")

						# Center of tag
						center_x = tag.center[0] - (image.shape[1] / 2) #center[0] is x, shape[1] is also x
						center_x_entry.setNumber(center_x)
						TOLERANCE = 88
						if center_x < TOLERANCE and center_x > -TOLERANCE:
							speaker_tags_subtable.getEntry("command").setString("Center")
						elif center_x > TOLERANCE:
							speaker_tags_subtable.getEntry("command").setString("Right")
						else:
							speaker_tags_subtable.getEntry("command").setString("Left")
				else:
					speaker_tags_subtable.getEntry("command").setString("Not found")
					within_distance_entry.setBoolean(False)

				#print(speaker_tags_subtable.getEntry("command").getString(""))
					
			else:
				break
	#except KeyboardInterrupt:
	#	pass

	capture.release()

main()