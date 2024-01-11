from tkinter import DISABLED, StringVar
from tkinter import ttk
import tkinter as tk
from tkinter import filedialog
import platform, os, subprocess
import tri_d

def create_window(version):
    window = tk.Tk()
    window.title("Trident: Tri-D Automation")
    if platform.system() != 'Darwin':
        window.iconphoto(False, tk.PhotoImage(file='icon.png'))
    
    window.resizable(False, False)  # This code helps to disable windows from resizing

    window_height = 250
    window_width = 600

    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x_cordinate = int((screen_width/2) - (window_width/2))
    y_cordinate = int((screen_height/2) - (window_height/2))

    window.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate)) 
    window.attributes('-topmost', True)
    if platform.system() == 'Darwin':
        tmpl = 'tell application "System Events" to set frontmost of every process whose unix id is {} to true'
        script = tmpl.format(os.getpid())
        subprocess.check_call(['/usr/bin/osascript', '-e', script])
    window.after_idle(window.attributes, '-topmost', False)
    


    frame = build_analysis_frame(window)
    frame.grid()

    

    



    window.mainloop()


def build_analysis_frame(window):
    
    frame = ttk.Frame(window)
    indir = StringVar(frame, os.getcwd())
    outdir = StringVar(frame, os.getcwd()) 
    percent = StringVar(frame, "90") 
      
    inlabel = ttk.Label(frame, text = "Input Folder: ")
    inentry = ttk.Entry(frame, textvariable=indir)
    inbtn = ttk.Button(frame, text='Browse', command=lambda: filedialog(indir))
    outlabel = ttk.Label(frame, text= "Output Folder: ")
    outentry = ttk.Entry(frame, textvariable=outdir)
    outbtn = ttk.Button(frame, text='Browse', command=lambda: filedialog(outdir))
    pcntlabel = ttk.Label(frame, text= "Top User Percentage: ")
    vcmd = (frame.register(validate), '%S')
    pcntentry = ttk.Entry(frame, textvariable=percent, validate="key", validatecommand=vcmd, width=2)
    pcntsign = ttk.Label(frame, text="%")
    runbtn = ttk.Button(frame, text="Run", command=lambda: tri_d.run_trid(indir.get(), outdir.get(), percent.get(), log, window))
    log = tk.Text(frame, height=6, width=50, state=DISABLED)

    inlabel.grid(column=0, row=0)
    inentry.grid(column=1, row=0, columnspan=3, sticky="ew")
    inentry.xview_moveto(1)
    inbtn.grid(column=4, row=0, sticky="e")
    outlabel.grid(column=0, row=1, columnspan=1)
    outentry.grid(column=1, row=1, columnspan=3, sticky="ew")
    outentry.xview_moveto(1)
    outbtn.grid(column=4, row=1, columnspan=1, sticky="e")
    pcntlabel.grid(column=0, row=2, columnspan=1)
    pcntentry.grid(column=1, row=2)
    pcntsign.grid(column=1, row=2, sticky="e")
    runbtn.grid(column = 0, row =3, rowspan=2, sticky="s")
    log.grid(column=1, row=3, columnspan=3, rowspan=2, sticky="ns")
    return frame

def validate(S):
    if S:
        try:
            float(S)
            return True
        except ValueError:
            return False
    else:
        return False

def filedialog(path):
    p = tk.filedialog.askdirectory()
    if not p:
        return
    path.set(p)
