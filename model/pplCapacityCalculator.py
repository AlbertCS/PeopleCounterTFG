import tkinter as tk
from tkinter import Variable, filedialog
from typing import Text
from PIL import Image
from PIL import ImageTk
from peopleCounter import pplCounter
from centroidtracker import CentroidTracker
from imutils.video import VideoStream
from imutils.video import FPS
import config, cv2
import numpy as np
from PIL import Image
from PIL import ImageTk



class pplCApp:
    
    global vs


    def __init__(self, master):
        self.master = master
        
        # Main Frame, enables a margin
        self.frmMain = tk.Frame(self.master, padx=10, pady=10)


        # Control buttons
        self.btStart = tk.Button(self.frmMain, text="Start", command=self.inicount)
        self.btStop = tk.Button(self.frmMain, text="Stop")
        self.btStart.grid(column=0, row=0, pady=2)
        self.btStop.grid(column=1, row=0, pady=2)


        # Where the video will be displayed
        self.lblVideo = tk.Label(self.frmMain, text="Video", background="grey")
        self.lblVideo.grid(column=0, row=1, columnspan=2, rowspan=6)


        # Entry values frame
        self.frmEntries = tk.Frame(self.frmMain, padx=2, pady=10)
        self.frmEntries.grid(column=2, row=1, rowspan=2, sticky=tk.N)


        # Frame for the radiobuttons
        self.varCamera = tk.StringVar()
        self.varCamera.set("0")
        self.frmInput = tk.Frame(self.frmEntries)
        self.entCamera = tk.Entry(self.frmInput, textvariable=self.varCamera)
        self.btFileDialog = tk.Button(self.frmInput, text="Select a video to process", command=self.browseFiles)
        self.btFileDialog.config(state='disable')


        # Radiobutton for the selection of the input
        self.radiobtCamera = tk.Radiobutton(self.frmInput, text="Camera.", value=0, command=lambda e1=self.entCamera, e2=self.btFileDialog: self.valcheck(e1, e2))
        self.radiobtInput = tk.Radiobutton(self.frmInput, text="Input video.", value=1,  command=lambda e1=self.btFileDialog, e2=self.entCamera: self.valcheck(e1, e2))
        self.radiobtCamera.select()
        self.radiobtInput.deselect()
        self.radiobtCamera.grid(column=0, row=0, sticky=tk.W, pady=2)
        self.entCamera.grid(column=0, row=1, sticky=tk.W, padx=(20,0))
        self.radiobtInput.grid(column=0, row=2, sticky=tk.W, pady=2)
        self.btFileDialog.grid(column=0, row=3, sticky=tk.W, padx=(20,0), pady=(0,5))
        self.frmInput.grid(column=0, row=0)

        
        self.varConfidence = tk.StringVar()
        self.varSkipFrames = tk.IntVar()
        self.varConfidence = "0.4"
        self.varSkipFrames = 30
        # Entry for the confidence value
        self.lblConfidence = tk.Label(self.frmEntries, text="Confidence:")
        self.entConfidence = tk.Entry(self.frmEntries, validate='key', vcmd=(self.frmEntries.register(self.validateEntryFloat), '%P'), textvariable=self.varConfidence)
        self.lblConfidence.grid(column=0, row=1, sticky=tk.W, pady=2)
        self.entConfidence.grid(column=1, row=1, sticky=tk.W, pady=2)

        # Entry for the skipFrames value
        self.lblSkipFrames = tk.Label(self.frmEntries, text="SkipFrames:")
        self.entSkipFrames = tk.Entry(self.frmEntries, validate='key', vcmd=(self.frmEntries.register(self.validateEntryInt), '%P'), textvariable=self.varSkipFrames)
        self.lblSkipFrames.grid(column=0, row=2, sticky=tk.W, pady=2)
        self.entSkipFrames.grid(column=1, row=2, sticky=tk.W, pady=2)

        # Data space
        self.lblData= tk.Label(self.frmEntries, text="Data:")
        self.frmData = tk.Frame(self.frmEntries, background="white", highlightbackground="black", highlightthickness=1)
        
        self.lblStatus = tk.Label(self.frmData, text="Status: 0 ppl", background="white")
        self.lblEnter = tk.Label(self.frmData, text="Enter: 0 ppl", background="white")
        self.lblExit = tk.Label(self.frmData, text="Exit: 0 ppl", background="white")
        self.lblTotal = tk.Label(self.frmData, text="Total: 0 ppl", background="white")
        self.lblStatus.grid(column=0, row=0, sticky=tk.W)
        self.lblEnter.grid(column=0, row=1, sticky=tk.W)
        self.lblExit.grid(column=0, row=2, sticky=tk.W)
        self.lblTotal.grid(column=0, row=3, sticky=tk.W)

        self.frmData.grid(column=0, row=5, sticky=tk.W, padx=(10,0))
        self.lblData.grid(column=0, row=4, sticky=tk.W, pady=(8,0))

        # Fps label
        self.lblFPS = tk.Label(self.frmMain, text="Fps:")
        self.lblFPS.grid(column=0, row=7, sticky=tk.S + tk.W)
        # Fps label
        self.lblElapsedTime = tk.Label(self.frmMain, text="Elapsed time:")
        self.lblElapsedTime.grid(column=1, row=7, sticky=tk.S + tk.W)


        self.frmMain.pack(fill=tk.BOTH, expand=True)

    def browseFiles(self):
        filename = filedialog.askopenfilename(initialdir = "/",title = "Select a File",filetypes = (("Text files","*.mp4*"),("all files","*.*")))
        self.btFileDialog.configure(text=filename)
        
   
    def validateEntryFloat(self, ent):
        try:
            float(ent)
        except:
            return False
        return True

    def validateEntryInt(self, ent):
        try:
            int(ent)
        except:
            return False
        return True
    
    def valcheck(self, e1, e2): 
            e1.configure(state='normal')
            e2.configure(state='disable')
    
    def inicount(self):

        # Parameters definition
        prototxtArg = ".\extras\deploy.prototxt"
        modelArg = ".\extras\deploy.caffemodel"
        #.\example_01.mp4
        #inputArg = ".\example_01.mp4"
        #confidenceArg = 0.4
        #skipFramesArg = 30

        cameraArg = self.varCamera
        inputArg = self.btFileDialog['text']
        print(inputArg)
        confidenceArg = float(self.varConfidence)
        print(confidenceArg)
        skipFramesArg = self.varSkipFrames
        print(skipFramesArg)
        
        # initialize the list of class labels MobileNet SSD was trained to
        # detect
        CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
            "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
            "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
            "sofa", "train", "tvmonitor"]

        # load our serialized model from disk
        net = cv2.dnn.readNetFromCaffe(prototxtArg, modelArg)

        # if a video path was not supplied, grab a reference to the ip camera
        if inputArg == "Select a video to process":
            print("[INFO] Starting the live stream.. in "+cameraArg.get())
            vs = VideoStream(cameraArg.get()).start()
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
        empty=[]
        empty1=[]
        total=0

        # start the frames per second throughput estimator
        fps = FPS().start()

        pplC = pplCounter()

        # loop over frames from the video stream
        while True :
            # grab the next frame and handle if we are reading from either
            # VideoCapture or VideoStream
            frame = vs.read()
            frame = frame[1] if (inputArg != "Select a video to process") else frame

            # if we are viewing a video and we did not grab a frame then we
            # have reached the end of the video
            if inputArg is not None and frame is None:
                break
            
            frame, totalUp, totalDown, empty, empty1, total, trackers, status  = pplC.countPPl(
                frame, W, H, totalFrames, skipFramesArg, net, confidenceArg, CLASSES, ct, trackableObjects, totalUp, empty, totalDown, empty1, trackers, total)
            
            if np.shape(frame) != ():
                im =Image.fromarray(frame)
                img = ImageTk.PhotoImage(image=im)
                self.lblVideo.configure(image=img)
                self.lblVideo.image = img
                self.lblVideo.after(1)
                self.lblVideo.update()

            self.lblStatus.configure(text="Status: "+status)
            self.lblEnter.configure(text="Enter: {} ppl".format(totalDown))
            self.lblExit.configure(text="Exit: {} ppl".format(totalUp))
            self.lblTotal.configure(text="Total inside: {} ppl".format(total))

            # increment the total number of frames processed thus far and
            # then update the FPS counter
            totalFrames += 1
            fps.update()


        # stop the timer and display FPS information
        fps.stop()
        self.lblElapsedTime.configure(text="Elapsed time: {:.2f}".format(fps.elapsed()))
        self.lblFPS.configure(text="FPS: {:.2f}".format(fps.fps()))


        # # if we are not using a video file, stop the camera video stream
        #if not inputArg:
            #vs.stop()

    def stop(self):
        self.vs.stop()
        

def main():
    root = tk.Tk()
    root.title("People capacity counter")
    root.resizable(False, False)
    app = pplCApp(root)
    root.mainloop()

main()