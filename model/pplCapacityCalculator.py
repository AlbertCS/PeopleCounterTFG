from tkinter import ttk
from tkinter import *
from PIL import Image
from PIL import ImageTk
from peopleCounter import pplCounter
from centroidtracker import CentroidTracker
from imutils.video import VideoStream
from imutils.video import FPS
import config, time, cv2
from PIL import Image
from PIL import ImageTk


def inicount():
    
    global vs

    if vs  is not None:
        lblVideo.image = ""
        vs.release()
        vs = None

    # Parameters definition
    prototxtArg = ".\extras\deploy.prototxt"
    modelArg = ".\extras\deploy.caffemodel"
	#.\example_01.mp4
    inputArg = ""
    confidenceArg = 0.4
    skipFramesArg = 30
    
    # initialize the list of class labels MobileNet SSD was trained to
    # detect
    CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
        "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
        "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
        "sofa", "train", "tvmonitor"]

    # load our serialized model from disk
    net = cv2.dnn.readNetFromCaffe(prototxtArg, modelArg)

    # if a video path was not supplied, grab a reference to the ip camera
    if not inputArg:
        print("[INFO] Starting the live stream.. in "+config.url)
        vs = VideoStream(0).start()
        time.sleep(2.0)

    # otherwise, grab a reference to the video file
    else:
        print("[INFO] Starting the video..")
        vs = cv2.VideoCapture(inputArg)

    # instantiate our centroid tracker, then initialize a list to store
    # each of our dlib correlation trackers, followed by a dictionary to
    # map each unique object ID to a TrackableObject
    ct = CentroidTracker(maxDisappeared=40, maxDistance=50)
    trackers = []
    trackableObjects = {}

    # initialize the frame dimensions (we'll set them as soon as we read
	# the first frame from the video)
    W = None
    H = None

    # initialize the total number of frames processed thus far, along
    # with the total number of objects that have moved either up or down
    totalFrames = 0
    totalDown = 0
    totalUp = 0
    x = []
    empty=[]
    empty1=[]

    # start the frames per second throughput estimator
    fps = FPS().start()

    # loop over frames from the video stream
    while True :
        # grab the next frame and handle if we are reading from either
	    # VideoCapture or VideoStream
        frame = vs.read()
        frame = frame[1] if inputArg else frame

        # if we are viewing a video and we did not grab a frame then we
        # have reached the end of the video
        if inputArg is not None and frame is None:
            break

        frame, totalUp, totalDown, empty, empty1, total, trackers  = pplCounter.countPPl(
            frame, W, H, totalFrames, skipFramesArg, net, confidenceArg, CLASSES, ct, trackableObjects, totalUp, empty, totalDown, empty1, trackers, total)
        
        im =Image.fromarray(frame)
        img = ImageTk.PhotoImage(image=im)
        lblVideo.configure(image=img)
        lblVideo.image = img

        # increment the total number of frames processed thus far and
		# then update the FPS counter
        totalFrames += 1

        fps.update()

    # stop the timer and display FPS information
    fps.stop()
    print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
    print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))


    # # if we are not using a video file, stop the camera video stream
    if not inputArg:
        vs.stop()

    

def stopcount():
    vs.release()
    
    
    
vs = None
root = Tk()
root.title("People counter")
root.configure(background="#d5cbc9")
root.geometry("1000x700")

s = ttk.Style()
s.configure("TFrame", background="#d5cbc9")

## Menu ##

btStart = Button(root, text="Start", command=inicount)
btStart.grid(column=0, row=0)

btStop = Button(root, text="Stop", command=stopcount)
btStop.grid(column=1, row=0)

lblVideo = Label(root)
lblVideo.grid(column=0, row=1)



root.mainloop()






        
        
        
        
    








