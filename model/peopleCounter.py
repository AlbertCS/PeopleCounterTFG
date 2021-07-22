#from mylib.centroidTracker import CentroidTracker
from trackableObject import TrackableObject
import numpy as np
import time, dlib, cv2, imutils
from idlelib.tooltip import *


t0 = time.time()

class pplCounter:

	# Init function
	def __init__(self):
		pass

	# Main function to calculate the object that moved down and up
	def countPPl (self, frame, W, H, totalFrames, skipFramesArg, net, confidenceArg, CLASSES, ct, trackableObjects, totalUp, empty, totalDown, empty1, trackers, total, maximum):

		# Resize the frame to have a maximum width of 500 pixels, and convert
		# the frame from BGR to RGB for dlib
		frame = imutils.resize(frame, width = 500)
		rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

		# If the frame dimensions are empty, set them
		if W is None or H is None:
			(H, W) = frame.shape[:2]

		# Initialize the current status along with our list of bounding
		# box rectangles returned by either (1) our object detector or
		# (2) the correlation trackers
		status = "Waiting"
		rects = []
		i=0

		# Reduce the frames calculation to reduce the computation time 
		if totalFrames % skipFramesArg == 0:
			# Set the status and initialize our new set of object trackers
			status = "Detecting"
			trackers = []

			# Convert the frame to a blob and pass the blob through the
			# network and obtain the detections
			blob = cv2.dnn.blobFromImage(frame, 0.007843, (W, H), 127.5)
			net.setInput(blob)
			detections = net.forward()

			# Loop over the detections
			for i in np.arange(0, detections.shape[2]):
				# Extract the confidence associated with the prediction
				confidence = detections[0, 0, i, 2]

				# Filter out weak detections by requiring a minimum confidence
				if confidence > confidenceArg:
					# Extract the index and the label, from the detections list
					idx = int(detections[0, 0, i, 1])

					# If the class label is not a person, ignore it
					if CLASSES[idx] != "person":
						continue

					# Compute the (x, y)-coordinates of the bounding box for the object
					box = detections[0, 0, i, 3:7] * np.array([W, H, W, H])
					(startX, startY, endX, endY) = box.astype("int")

					# Construct a rectangle object from the bounding
					# box coordinates and then start the correlation tracker
					tracker = dlib.correlation_tracker()
					rect = dlib.rectangle(startX, startY, endX, endY)
					tracker.start_track(rgb, rect)

					# Add the tracker to our list of trackers so we can
					# utilize it during skip frames
					trackers.append(tracker)

		# Otherwise, we should utilize our object *trackers* rather than
		# object *detectors* 
		else:
			# Loop over the trackers
			for tracker in trackers:
				# Set the status of our system to be 'tracking'
				status = "Tracking"

				# Update the tracker and grab the updated position
				tracker.update(rgb)
				pos = tracker.get_position()

				# Unpack the position object
				startX = int(pos.left())
				startY = int(pos.top())
				endX = int(pos.right())
				endY = int(pos.bottom())

				# Add the bounding box coordinates to the rectangles list
				rects.append((startX, startY, endX, endY))

		# Draw a horizontal line in the center of the frame -- once an
		# object crosses this line we will determine whether they were
		# moving 'up' or 'down'
		cv2.line(frame, (0, H // 2), (W, H // 2), (0, 0, 0), 3)
		cv2.putText(frame, "-Prediction border - Entrance-", (10, H - ((i * 20) + 200)),
			cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

		# Use the centroid tracker to associate the (1) old object
		# centroids with (2) the newly computed object centroids
		objects = ct.update(rects)

		# Loop over the tracked objects
		for (objectID, centroid) in objects.items():
			# Check to see if a trackable object exists for the current object ID
			to = trackableObjects.get(objectID, None)

			# If there is no existing trackable object, create one
			if to is None:
				to = TrackableObject(objectID, centroid)

			# Otherwise, there is a trackable object so we can utilize it
			# to determine direction
			else:
				# The difference between the y-coordinate of the *current*
				# centroid and the mean of *previous* centroids will tell
				# us in which direction the object is moving (negative for
				# 'up' and positive for 'down')
				y = [c[1] for c in to.centroids]
				direction = centroid[1] - np.mean(y)
				to.centroids.append(centroid)

				# Check to see if the object has been counted or not
				if not to.counted:
					# If the direction is negative (indicating the object
					# is moving up) AND the centroid is above the center
					# line, count the object
					if direction < 0 and centroid[1] < H // 2:
						totalUp += 1
						empty.append(totalUp)
						to.counted = True

					# If the direction is positive (indicating the object
					# is moving down) AND the centroid is below the
					# center line, count the object
					elif direction > 0 and centroid[1] > H // 2:
						totalDown += 1
						empty1.append(totalDown)
						
						# If the people limit exceeds over threshold
						if total >= maximum:
							cv2.putText(frame, "-ALERT: People limit exceeded-", (10, frame.shape[0] - 80),
								cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255), 2)

						to.counted = True
						
					# Compute the sum of total people inside
					total = len(empty1)-len(empty)


			# Store the trackable object in our dictionary
			trackableObjects[objectID] = to

			# Draw both the ID of the object and the centroid of the
			# object on the output frame
			text = "ID {}".format(objectID)
			cv2.putText(frame, text, (centroid[0] - 10, centroid[1] - 10),
				cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
			cv2.circle(frame, (centroid[0], centroid[1]), 4, (255, 255, 255), -1)

		
		return frame, totalUp, totalDown, empty, empty1, total, trackers, status

			
			

	

