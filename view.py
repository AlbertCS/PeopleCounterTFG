import tkinter as tk
from tkinter import Variable, filedialog




class pplCApp:
        
    def __init__(self, master):
        self.master = master
        
        # Main Frame, enables a margin
        self.frmMain = tk.Frame(self.master, padx=10, pady=10)


        # Control buttons
        self.btStart = tk.Button(self.frmMain, text="Start")
        self.btStop = tk.Button(self.frmMain, text="Stop")
        self.btStart.grid(column=0, row=0, pady=2)
        self.btStop.grid(column=1, row=0, pady=2)


        # Where the video will be displayed
        self.lblVideo = tk.Label(self.frmMain, text="Video", background="grey", width=75, height=30)
        self.lblVideo.grid(column=0, row=1, columnspan=2, rowspan=2)


        # Entry values frame
        self.frmEntries = tk.Frame(self.frmMain, padx=2, pady=10)
        self.frmEntries.grid(column=2, row=1, rowspan=2, sticky=tk.N)


        # Frame for the radiobuttons
        self.frmInput = tk.Frame(self.frmEntries)
        self.entCamera = tk.Entry(self.frmInput)
        self.btFileDialog = tk.Button(self.frmInput, text="Select a video to process", command=self.browseFiles)


        # Radiobutton for the selection of the input
        self.radiobtCamera = tk.Radiobutton(self.frmInput, text="Camera.", value=0, command=lambda e1=self.entCamera, e2=self.btFileDialog: self.valcheck(e1, e2))
        self.radiobtInput = tk.Radiobutton(self.frmInput, text="Input video.", value=1, command=lambda e1=self.btFileDialog, e2=self.entCamera: self.valcheck(e1, e2))
        self.radiobtCamera.grid(column=0, row=0, sticky=tk.W)
        self.entCamera.grid(column=0, row=1, sticky=tk.W, padx=20)
        self.radiobtInput.grid(column=0, row=2, sticky=tk.W)
        self.btFileDialog.grid(column=0, row=3, sticky=tk.W, padx=20)
        self.frmInput.grid(column=0, row=0)

        
        # Entry for the confidence value
        self.lblConfidence = tk.Label(self.frmEntries, text="Confidence :")
        self.entConfidence = tk.Entry(self.frmEntries, validate='key', vcmd=(self.frmEntries.register(self.validateEntryFloat), '%P'))
        self.entConfidence.insert(0, 0.4)
        self.lblConfidence.grid(column=0, row=1, sticky=tk.W)
        self.entConfidence.grid(column=1, row=1, sticky=tk.W)

        # Entry for the skipFrames value
        self.lblConfidence = tk.Label(self.frmEntries, text="SkipFrames :")
        self.entConfidence = tk.Entry(self.frmEntries, validate='key', vcmd=(self.frmEntries.register(self.validateEntryInt), '%P'))
        self.entConfidence.insert(0, 30)
        self.lblConfidence.grid(column=0, row=2, sticky=tk.W)
        self.entConfidence.grid(column=1, row=2, sticky=tk.W)



        self.frmMain.pack(fill=tk.BOTH,expand=True)

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


def main():
    root = tk.Tk()
    root.title("People capacity counter")
    app = pplCApp(root)
    root.mainloop()

main()