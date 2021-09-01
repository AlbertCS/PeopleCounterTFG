from imutils.video.fps import FPS
from imutils.video.videostream import VideoStream
from tooltip import Tooltip
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from peopleCounter import pplCounter
from centroidtracker import CentroidTracker
import cv2, datetime, csv
from tkinter import ttk
import numpy as np



class pplCApp:
    
    # Main function to create the gui
    def __init__(self, master):
        self.master = master
        
        # Main Frame, enables a margin
        self.frmMain = tk.Frame(self.master, padx=10, pady=10)

        # Control buttons
        self.btStart = ttk.Button(self.frmMain, text="Start", command=self.inicount)
        self.btStart['padding'] = (0,2)
        self.stopClicked = False
        self.btStop = ttk.Button(self.frmMain, text="Stop", command=self.stop)
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
        self.frmInput = tk.Frame(self.frmEntries)
        
        # Radiobutton for the selection of the input
        self.varCamera = tk.StringVar()
        self.varCamera.set("0")
        self.entCamera = ttk.Entry(self.frmInput, textvariable=self.varCamera)
        self.entCamera.config(state='disable')
        self.btFileDialog = ttk.Button(self.frmInput, text="Select a video to process", command=self.browseFiles)
        self.btFileDialog.config(state='disable')    
        self.radiobtCamera = ttk.Radiobutton(self.frmInput, text="Camera.", value=0, command=lambda e1=self.entCamera, e2=self.btFileDialog: self.valcheck(e1, e2))
        self.radiobtInput = ttk.Radiobutton(self.frmInput, text="Input video.", value=1,  command=lambda e1=self.btFileDialog, e2=self.entCamera: self.valcheck(e1, e2))
        Tooltip(self.radiobtCamera, text='Select one of the options to start the analisi (webcam as a default option)')
        Tooltip(self.entCamera, text='Write the ip of the camera, or 0 if you want the webcam')
        Tooltip(self.btFileDialog, text='Select the recording to analize (should be an .mp4)')
        self.radiobtCamera.grid(column=0, row=0, sticky=tk.W, pady=2)
        self.entCamera.grid(column=0, row=1, sticky=tk.W, padx=(20,0))
        self.radiobtInput.grid(column=0, row=2, sticky=tk.W, pady=2)
        self.btFileDialog.grid(column=0, row=3, sticky=tk.W, padx=(20,0), pady=(0,5))
        self.frmInput.grid(column=0, row=0)

        # Entry for the confidence value
        self.varConfidence = tk.StringVar()
        #self.varConfidence = "0.4"
        self.lblConfidence = ttk.Label(self.frmEntries, text="Confidence:")
        self.entConfidence = ttk.Entry(self.frmEntries, validate='key', validatecommand=(self.frmEntries.register(self.validateEntryFloat), '%P'), textvariable=self.varConfidence)
        self.entConfidence.insert(1, "0.4")
        Tooltip(self.entConfidence, text='To filter weak detections, minimum probability to consider a detection as a good one')
        self.lblConfidence.grid(column=0, row=1, sticky=tk.W, pady=2)
        self.entConfidence.grid(column=1, row=1, sticky=tk.W, pady=2)

        # Entry for the skipFrames value
        self.varSkipFrames = tk.IntVar()
        self.lblSkipFrames = ttk.Label(self.frmEntries, text="SkipFrames:")
        self.entSkipFrames = ttk.Entry(self.frmEntries, validate='key', validatecommand=(self.frmEntries.register(self.validateEntryInt), '%P'), textvariable=self.varSkipFrames)
        self.entSkipFrames.insert(0, "3")
        Tooltip(self.entSkipFrames, text='The frames to skip to minimize the calculation')
        self.lblSkipFrames.grid(column=0, row=2, sticky=tk.W, pady=2)
        self.entSkipFrames.grid(column=1, row=2, sticky=tk.W, pady=2)
        
        # Entry for the maxim capacity value
        self.lblMaximimCap = ttk.Label(self.frmEntries, text="Maximum Capacity:")
        self.varMaximum = tk.IntVar()
        self.entMaximimCap = ttk.Entry(self.frmEntries,validate='key', validatecommand=(self.frmEntries.register(self.validateEntryInt), '%P'), textvariable=self.varMaximum)
        self.entMaximimCap.insert(0, "1")
        Tooltip(self.entMaximimCap, text='The maxmum people allowed inside')
        self.lblMaximimCap.grid(column=0, row=3, sticky=tk.W, pady=2)
        self.entMaximimCap.grid(column=1, row=3, sticky=tk.W, pady=2)

        # Data space
        self.lblData= ttk.Label(self.frmEntries, text="Data:")
        self.frmData = tk.Frame(self.frmEntries,  background="white", highlightbackground="black", highlightthickness=1)
        Tooltip(self.frmData, text='Status: Current status of the program\nEnter: How many people had enter\nExit: How many people had exit\nTotal: Total balance of the people inside')
        self.lblStatus = ttk.Label(self.frmData, text="Status: ", background="white")
        self.lblEnter = ttk.Label(self.frmData, text="Enter: 0 ppl", background="white")
        self.lblExit = ttk.Label(self.frmData, text="Exit: 0 ppl", background="white")
        self.lblTotal = ttk.Label(self.frmData, text="Total: 0 ppl", background="white")
        self.lblStatus.grid(column=0, row=0, sticky=tk.W)
        self.lblEnter.grid(column=0, row=1, sticky=tk.W)
        self.lblExit.grid(column=0, row=2, sticky=tk.W)
        self.lblTotal.grid(column=0, row=3, sticky=tk.W)
        self.frmData.grid(column=0, row=5, sticky=tk.W, padx=(10,0))
        self.lblData.grid(column=0, row=4, sticky=tk.W, pady=(8,0))

        # Log checkbutton
        self.varcheckedLog = tk.IntVar()
        self.chckbtLog = ttk.Checkbutton(self.frmEntries, variable=self.varcheckedLog, text="Activate log")
        self.chckbtLog.grid(column=0, row=6, sticky=tk.W, pady=(5,0))

        # Fps label
        self.lblFPS = ttk.Label(self.frmMain, text="Fps:")
        self.lblFPS.grid(column=0, row=7, sticky=tk.S + tk.W)
        Tooltip(self.lblFPS, text='FPS of the analisis')
        # Fps label
        self.lblElapsedTime = ttk.Label(self.frmMain, text="Elapsed time:")
        self.lblElapsedTime.grid(column=1, row=7, sticky=tk.S + tk.W)
        Tooltip(self.lblElapsedTime, text='Duration of the analisis')

        self.frmMain.pack(fill=tk.BOTH, expand=True)

    # Function to select the video file
    def browseFiles(self):
        filename = filedialog.askopenfilename(initialdir = "/",title = "Select a File",filetypes = (("Text files","*.mp4*")))
        self.btFileDialog.configure(text=filename)
   
    # Function to only allow float in the entry
    def validateEntryFloat(self, ent):
        try:
            float(ent)
        except:
            return False
        return True

    # Function to only allow integer in the entry
    def validateEntryInt(self, ent):
        try:
            int(ent)
        except:
            return False
        return True
    
    # Func to check the radioButtons
    def valcheck(self, e1, e2): 
            e1.configure(state='normal')
            e2.configure(state='disable')
    
    # Main function with the initialitzations and calling the main function
    def inicount(self):

        # Parameters definition
        prototxtArg = ".\model\deploy.prototxt"
        modelArg = ".\model\deploy.caffemodel"
        maximum = self.varMaximum.get()
        cameraArg = self.varCamera.get()
        inputArg = self.btFileDialog['text']
        confidenceArg = float(self.varConfidence.get())
        skipFramesArg = self.varSkipFrames.get()
        self.stopClicked = False
        
        # Initialize the list of class labels of the MobileNet SSD 
        CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
            "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
            "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
            "sofa", "train", "tvmonitor"]

        # Load our model
        net = cv2.dnn.readNetFromCaffe(prototxtArg, modelArg)

        # If a video path was not supplied, grab the ip camera or the webcam
        if inputArg == "Select a video to process":
            print("[INFO] Starting the live stream.. in "+cameraArg)
            if "http" in cameraArg:
                self.vs = VideoStream(cameraArg).start()
            else:
                self.vs = VideoStream(int(cameraArg)).start()
        # Otherwise, grab a reference to the video file
        else:
            print("[INFO] Starting the video..")
            self.vs = cv2.VideoCapture(inputArg)
            
        # Instantiate the centroid tracker, then initialize a list to store
        # each correlation trackers, and a dictionary to map each object ID to TrackableObject
        ct = CentroidTracker(maxDisappeared=40, maxDistance=50)
        trackers = []
        trackableObjects = {}

        # Initialize the frame dimensions
        W = None
        H = None

        # Initialize all the necesari variables, the total number of frames processed, the total number of objects that have moved up and down
        # the total inside, and the status
        totalFrames = 0
        totalDown = 0
        totalUp = 0
        empty=[]
        empty1=[]
        total=0
        status=""

        # Start the frames per second throughput estimator
        fps = FPS().start()

        # Initialize the clas that is going to calculate the object
        pplC = pplCounter()

        # Loop over frames from the video stream
        while True :
            # Grab the next frame and handle if we are reading from either VideoCapture or VideoStream
            frame = self.vs.read()
            frame = frame[1] if (inputArg != "Select a video to process") else frame

            # If we are viewing a video and we did not grab a frame then we
            # have reached the end of the video
            if inputArg is not None and frame is None:
                break
            
            # Call the main function to calculate the objects that had moved donw or up
            frame, totalUp, totalDown, empty, empty1, total, trackers, status  = pplC.countPPl(
                frame, W, H, totalFrames, skipFramesArg, net, confidenceArg, CLASSES, ct, trackableObjects, totalUp, empty, totalDown, empty1, trackers, total, maximum)
            

            # If the people limit exceeds over threshold
            if total >= maximum:
                cv2.putText(frame, "ALERT: Limit of people exceeded", (10, frame.shape[0] - 80),
				cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255), 2)


            # Print the frame in the window
            if np.shape(frame) != ():
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                im =Image.fromarray(rgb)
                img = ImageTk.PhotoImage(image=im)
                self.lblVideo.configure(image=img)
                self.lblVideo.after(1)
                self.lblVideo.update()
            
            # Show the information of the calculation
            self.lblStatus.configure(text="Status: "+status)
            self.lblEnter.configure(text="Enter: {} ppl".format(totalDown))
            self.lblExit.configure(text="Exit: {} ppl".format(totalUp))
            self.lblTotal.configure(text="Total inside: {} ppl".format(total))

            # Increment the total number of frames processed
            totalFrames += 1
            fps.update()

            # If the stop button is pressed stop the process
            if self.stopClicked:
                break

        print("[INFO] Analisis stoped")
        # stop the timer and display FPS information
        fps.stop()
        self.lblElapsedTime.configure(text="Elapsed time: {:.2f}".format(fps.elapsed()))
        self.lblFPS.configure(text="FPS: {:.2f}".format(fps.fps()))

        # Initiate a simple log to save data
        if self.varcheckedLog:
            date = [datetime.datetime.now()]
            export_data = [24, totalDown, totalUp, total]
            with open('Log.csv', 'w', encoding='UTF8') as myfile:
                wr = csv.writer(myfile)
                wr.writerow(("End Time", "In", "Out", "Total Inside"))
                wr.writerow(export_data)


    # Function of the stop button
    def stop(self):
        self.stopClicked = True
        self.vs.stop()
        self.vs.stream.release()
        
# Main process
def main():
    root = tk.Tk()
    root.title("People capacity counter")
    root.resizable(False, False)
    app = pplCApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
