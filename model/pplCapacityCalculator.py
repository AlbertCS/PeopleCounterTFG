from tooltip import Tooltip
import tkinter as tk
from tkinter import filedialog
from typing import Text
from PIL import Image
from PIL import ImageTk
from peopleCounter import pplCounter
from centroidtracker import CentroidTracker
from imutils.video import VideoStream
from imutils.video import FPS
import cv2
from tkinter import ttk
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
        self.btStart = ttk.Button(self.frmMain, text="Start", command=self.inicount)
        self.btStart['padding'] = (0,2)
        self.btStop = ttk.Button(self.frmMain, text="Stop")
        self.btStart.grid(column=0, row=0)
        self.btStop['padding'] = (0,2)
        self.btStop.grid(column=1, row=0)
        Tooltip(self.btStart, text='To start the analisis')
        Tooltip(self.btStop, text='To stop the analisis')

        # Where the video will be displayed
        self.lblVideo = ttk.Label(self.frmMain, text="Video", padding=(0,0,5,0))
        self.lblVideo.grid(column=0, row=1, columnspan=2, rowspan=6)


        # Entry values frame
        self.frmEntries = tk.Frame(self.frmMain, padx=2, pady=10)
        self.frmEntries.grid(column=2, row=1, rowspan=2, sticky=tk.N)


        # Frame for the radiobuttons
        self.varCamera = tk.StringVar()
        self.varCamera.set("0")
        self.frmInput = ttk.Frame(self.frmEntries)
        self.entCamera = ttk.Entry(self.frmInput, textvariable=self.varCamera)
        self.entCamera.config(state='disable')
        self.btFileDialog = ttk.Button(self.frmInput, text="Select a video to process", command=self.browseFiles)
        self.btFileDialog.config(state='disable')
        Tooltip(self.entCamera, text='Write the ip of the camera, or 0 if you want the webcam')
        Tooltip(self.btFileDialog, text='Select the recording to analize (should be an .mp4)')


        # Radiobutton for the selection of the input
        self.radiobtCamera = ttk.Radiobutton(self.frmInput, text="Camera.", value=0, command=lambda e1=self.entCamera, e2=self.btFileDialog: self.valcheck(e1, e2))
        self.radiobtInput = ttk.Radiobutton(self.frmInput, text="Input video.", value=1,  command=lambda e1=self.btFileDialog, e2=self.entCamera: self.valcheck(e1, e2))
        self.radiobtCamera.grid(column=0, row=0, sticky=tk.W, pady=2)
        Tooltip(self.radiobtCamera, text='Select one of the options to start the analisi (webcam as a default option)')
        self.entCamera.grid(column=0, row=1, sticky=tk.W, padx=(20,0))
        self.radiobtInput.grid(column=0, row=2, sticky=tk.W, pady=2)
        self.btFileDialog.grid(column=0, row=3, sticky=tk.W, padx=(20,0), pady=(0,5))
        self.frmInput.grid(column=0, row=0)

        
        self.varConfidence = tk.StringVar()
        self.varSkipFrames = tk.IntVar()
        self.varConfidence = "0.4"
        self.varSkipFrames = 30
        # Entry for the confidence value
        self.lblConfidence = ttk.Label(self.frmEntries, text="Confidence:")
        self.entConfidence = ttk.Entry(self.frmEntries, validate='key', validatecommand=(self.frmEntries.register(self.validateEntryFloat), '%P'), textvariable=self.varConfidence)
        Tooltip(self.entConfidence, text='The minimum distance where two points are consideret the same in time')
        self.lblConfidence.grid(column=0, row=1, sticky=tk.W, pady=2)
        self.entConfidence.grid(column=1, row=1, sticky=tk.W, pady=2)

        # Entry for the skipFrames value
        self.lblSkipFrames = ttk.Label(self.frmEntries, text="SkipFrames:")
        self.entSkipFrames = ttk.Entry(self.frmEntries, validate='key', validatecommand=(self.frmEntries.register(self.validateEntryInt), '%P'), textvariable=self.varSkipFrames)
        Tooltip(self.entSkipFrames, text='The frames to skip to minimize the calculation')
        self.lblSkipFrames.grid(column=0, row=2, sticky=tk.W, pady=2)
        self.entSkipFrames.grid(column=1, row=2, sticky=tk.W, pady=2)

        # Data space
        self.lblData= ttk.Label(self.frmEntries, text="Data:")
        self.frmData = tk.Frame(self.frmEntries,  background="white", highlightbackground="black", highlightthickness=1)
        Tooltip(self.frmData, text='Status: Current status of the program\nEnter: How many people had enter\nExit: How many people had exit\nTotal: Total balance of the people inside')

        self.lblStatus = ttk.Label(self.frmData, text="Status: 0 ppl", background="white")
        self.lblEnter = ttk.Label(self.frmData, text="Enter: 0 ppl", background="white")
        self.lblExit = ttk.Label(self.frmData, text="Exit: 0 ppl", background="white")
        self.lblTotal = ttk.Label(self.frmData, text="Total: 0 ppl", background="white")
        self.lblStatus.grid(column=0, row=0, sticky=tk.W)
        self.lblEnter.grid(column=0, row=1, sticky=tk.W)
        self.lblExit.grid(column=0, row=2, sticky=tk.W)
        self.lblTotal.grid(column=0, row=3, sticky=tk.W)

        self.frmData.grid(column=0, row=5, sticky=tk.W, padx=(10,0))
        self.lblData.grid(column=0, row=4, sticky=tk.W, pady=(8,0))

        # Fps label
        self.lblFPS = ttk.Label(self.frmMain, text="Fps:")
        self.lblFPS.grid(column=0, row=7, sticky=tk.S + tk.W)
        Tooltip(self.lblFPS, text='FPS of the analisis')
        # Fps label
        self.lblElapsedTime = ttk.Label(self.frmMain, text="Elapsed time:")
        self.lblElapsedTime.grid(column=1, row=7, sticky=tk.S + tk.W)
        Tooltip(self.lblElapsedTime, text='Duration of the analisis')


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

        cameraArg = self.varCamera.get()
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

        # load our serialized model from diskS
        net = cv2.dnn.readNetFromCaffe(prototxtArg, modelArg)

        # if a video path was not supplied, grab a reference to the ip camera
        if inputArg == "Select a video to process":
            print("[INFO] Starting the live stream.. in "+cameraArg)
            # http://192.168.1.45:8080/video
            if "http" in cameraArg:
                vs = VideoStream(cameraArg).start()
            else:
                vs = VideoStream(int(cameraArg)).start()
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
        status=""

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
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                im =Image.fromarray(rgb)
                img = ImageTk.PhotoImage(image=im)
                self.lblVideo.configure(image=img)
                #self.lblVideo.image = img
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

        self.vs.stop()
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