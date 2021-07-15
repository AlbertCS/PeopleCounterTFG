from tkinter import ttk
from tkinter import *


class AppWindow(ttk.Frame):

    def __init__(self, master=None):

  

        self.root = Tk()
        self.root.title("People counter")
        self.root.configure(background="grey80")
        #self.root.geometry("1000x700")

        s = ttk.Style()
        s.configure("TFrame", background="grey")
        s.configure("Frame1.TFrame", background="red")
        s.configure("Frame2.TFrame", background="blue")


        ## Menu left ##

        self.menu_left = ttk.Frame(self.root, style="TFrame")
        # Upper left --> videoProperties
        self.videoProperties = ttk.Frame(self.menu_left, width=150, style="Frame1.TFrame")
        # Middle left --> video
        self.video = ttk.Frame(self.menu_left, style="Frame2.TFrame")
        # Lower left --> status
        self.status = ttk.Frame(self.menu_left, style="Frame1.TFrame")
        
        self.test = ttk.Label(self.videoProperties, text="videoProperties")
        self.test.pack()
        self.test1 = ttk.Label(self.video, text="video")
        self.test1.pack()
        self.test2 = ttk.Label(self.status, text="status")
        self.test2.pack()

        self.videoProperties.pack(side="top", fill="both", expand=True)
        self.video.pack(side="top", fill="both", expand=True)
        self.status.pack(side="top", fill="both", expand=True)

        self.menu_left.pack(side="left", fill="both", expand=True)


        ## Menu Right ##
        self.menu_right = ttk.Frame(self.root, style="TFrame")
        # Upper left --> videoProperties
        self.none_up = ttk.Frame(self.menu_right, width=150, style="Frame1.TFrame")
        # Middle left --> video
        self.properties = ttk.Frame(self.menu_right, style="Frame2.TFrame")
        # Lower left --> status
        self.none_down = ttk.Frame(self.menu_right, style="Frame1.TFrame")
        
        self.test3 = ttk.Label(self.none_up, text="none")
        self.test3.pack()
        self.test4 = ttk.Label(self.properties, text="properties")
        self.test4.pack()
        self.test5 = ttk.Label(self.none_down, text="none")
        self.test5.pack()

        self.none_up.pack(side="top", fill="both", expand=True)
        self.properties.pack(side="top", fill="both", expand=True)
        self.none_down.pack(side="top", fill="both", expand=True)

        self.menu_right.pack(side="right", fill="both", expand=True)

        
        self.root.mainloop()

AppWindow()
        
        
        
        
    








