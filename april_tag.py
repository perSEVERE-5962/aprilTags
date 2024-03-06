#!/usr/bin/env python3

from networktables import NetworkTables
import apriltag
import cv2
import sys

# All networktable paths:
# 	NetworkTables.getDefault().getTable("apriltags").getEntry("cameraworking")
# 	NetworkTables.getDefault().getTable("apriltags").getSubTable("speakertags").getSubTable("pos").getEntry("x/y/z")
# 	NetworkTables.getDefault().getTable("apriltags").getSubTable("speakertags").getEntry("command")

def main():
	# April tag init

	#focal_data = (1.14693147e+03, 1.13616617e+03, 3.86121647e+02, 2.43241211e+02) # 3264 x 2448 camera
	focal_data = (429.78652322, 463.26344368, 328.23222028, 171.63344415)
	tag_size = 6.5 * 0.0254 # 0.0254 is the inches to meters ratio

	# Network table init

	if len(sys.argv) != 2:
		print("Need to initialize with an IP")
		return

	NetworkTables.initialize(sys.argv[1])
	networktable_tags = NetworkTables.getDefault().getTable("apriltags")
	speaker_tags_subtable = networktable_tags.getSubTable("speakertags")

	# Camera init
	capture = cv2.VideoCapture(index=0)

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
	try:
		print("Initializing program loop")
		while True:
			exists, frame = capture.read()
			if exists:
				gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
				options = apriltag.DetectorOptions(families="tag36h11", refine_pose=True)
				detector = apriltag.Detector(options)
				results = detector.detect(gray)

				if len(results) > 0:
					for tag in results:
						tag_id = tag[1]
						if tag_id != 4 and tag_id != 7:
							continue

						pose, _, _ = detector.detection_pose(tag, focal_data, tag_size) # Can't ignore return values else the position variables will be wrong

						# Position
						pos_x = pose[0][3]
						pos_y = pose[1][3]
						pos_z = pose[2][3]

						pos_subtable = speaker_tags_subtable.getSubTable("pos")
						pos_subtable.getEntry("x").setNumber(pos_x)
						pos_subtable.getEntry("y").setNumber(pos_y)
						pos_subtable.getEntry("z").setNumber(pos_z)

						# Center of tag
						center_x = tag.center[0] - (gray.shape[1] / 2) #center[0] is x, shape[1] is also x
						TOLERANCE = 88
						if center_x < TOLERANCE and center_x > -TOLERANCE:
							speaker_tags_subtable.getEntry("command").setString("Center")
						elif center_x > TOLERANCE:
							speaker_tags_subtable.getEntry("command").setString("Right")
						else:
							speaker_tags_subtable.getEntry("command").setString("Left")
				else:
					speaker_tags_subtable.getEntry("command").setString("Not found")

				print(speaker_tags_subtable.getEntry("command").getString(""))
					
			else:
				break
	except KeyboardInterrupt:
		pass

	capture.release()

main()