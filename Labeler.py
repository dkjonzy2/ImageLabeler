# -*- coding: utf-8 -*-
"""
Image Labeler

Developer: Danny Jones (djones51@mgh.harvard.edu)

"""

# Set Constants

DATA_DIR = "Images"

# The features to be graded. A button will be created for each item in the list
features = ["Sz","GPD","LPD","LRDA","GRDA","focal slowing",
            "gen slowing","burst sup./atten.","suppressed",
            "normal","other (e.g. artifact)"]

#%%


import subprocess
import sys

# This will install the needed python packages if they are not already installed the first time the user runs the script
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install('pillow')
install('tkmacosx')
#install('distutils.dir_util')


from Sorter import Sorter
import tkinter as tk
from tkinter import messagebox
from tkinter.ttk import Progressbar
import PIL
from PIL import Image, ImageTk
from os import path
from csv import DictReader
from sys import exit
from tkmacosx import Button
import platform
import os
import pandas as pd
import numpy as np


# =============================================================================
# images_dir = 'Images'
# dir_path = path.dirname(path.realpath(__file__))
# =============================================================================

#%%
images_path = path.abspath(path.join(path.dirname(__file__), DATA_DIR))
images = os.listdir(images_path)
output_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Labeler_" + DATA_DIR + '_Output.xlsx')

cur_index = 0
# Get data
if os.path.exists(output_file):
    print("Output file found, opening for edits...")
    output_data = pd.read_excel(output_file, index_col=None)
    #Get starting point
    for i,row in output_data.iterrows():
        cur_index = i
        if pd.isna(row["Labels"]):
            break
else:
    print("Output file not found, creating...")
    output_data = pd.DataFrame(images, columns = ["Images"])
    output_data["Labels"] = ""
    output_data.to_excel(output_file)

print("Starting at index %d" % cur_index)
#convert df to dict
img_labels = dict(zip(output_data.Images, output_data.Labels))


#%% Functions

def pressed(feature):
    img_labels[images[cur_index]] = feature
    reset_buttons()
    buttons[feature].configure(bg=btn_color["1"])
    window.update()

def save():
    output_data["Labels"] = img_labels.values()
    output_data.to_excel(output_file)
    
def submit():
    #TODO check if a label has been selected and give pop up if not
    print("Submiting label...")
    save()
    global cur_index
    cur_index += 1
    if cur_index >= len(output_data):
        finish()
    reset()
    
def previous():
    print("Going back...")
    save()
    print("Going back one image")
    global cur_index
    cur_index -= 1
    if cur_index < 0:
        cur_index == 0
    reset()
    
def reset_buttons():
    for f in features:
        buttons[f].configure(bg=btn_color["0"])

def reset():
    global img, running, cur_index
    img = images[cur_index]
    progress['value'] = cur_index/len(images)
    window.update_idletasks()
    
    #Load new image
    image = Image.open(path.join(DATA_DIR, img))

    # This seems to be the slow step
    #start_time = time.monotonic()
    image = image.resize((img_width, img_height), Image.BOX)
    #end_time = time.monotonic()
    #print(timedelta(seconds=end_time - start_time))
    photo = ImageTk.PhotoImage(image)
    img_container.configure(relief=tk.FLAT, image=photo)
    img_container.image = photo
    
    reset_buttons()
    if (not pd.isna(img_labels[img])) and (not img_labels[img] == ''):
        buttons[img_labels[img]].configure(bg=btn_color["1"])
    
def finish():
    list = window.grid_slaves()
    for l in list:
        l.destroy()
    window.quit()
    messagebox.showinfo('','Sorting complete, you may exit the program')
    window.destroy()
    exit()
         

#%% Initialize TK inter window

window = tk.Tk()
window.title("Picture Sort")
width, height = window.winfo_screenwidth(), window.winfo_screenheight()
print(width, height)

window.geometry('%dx%d+0+0' % (width,height))


# Formating dimensions
offset = 0
if (platform.system() != 'Windows'): offset = 200
width = width-offset # Needed on mac because of borders ?
button_width = int(1/12 * width)
img_width = int(width / 2 - button_width)
img_height =  img_width #int(5/6 * height)
print(button_width)

#Set button colos
btn_color = {
    '1': 'pale green',
    '0': 'white'
    }

### Add layout

frm_main = tk.Frame(window)
frm_main.grid(row=1, column=0)
 
img_container = tk.Label (frm_main, bd = 6) # Initialized w/o an image, this will be updated in the reset
img_container.grid(row=0, column=1, sticky=tk.W, rowspan=len(features)) 

### Add buttons on either side with all features

buttons = {}
i = 0
for f in features:
    buttons[f] = Button(frm_main, text=f, command = lambda x=f: pressed(x))
    buttons[f].grid(row=i, column=3, sticky=tk.EW, padx=2)
    i += 1

btn_container = tk.Label (window, bd = 6)
btn_container.grid(row=2, column=0) 

btn_submit = tk.Button(btn_container, text='Submit', command = submit, width=10, bg='green3')
btn_submit.grid(row=2, column=1, pady=10)

btn_prev = tk.Button(btn_container, text='Previous', command = previous, width=10, bg='green3')
btn_prev.grid(row=2, column=0, pady=10)

##Bind controls

window.bind('<Right>', submit)
window.bind('<Left>', previous)

### Add progress bar at the top
progress = Progressbar(window, orient = tk.HORIZONTAL, mode='determinate', length=img_width*2)
progress.grid(row=0, column=0, pady=10)
prog_lbl = tk.Label(window, text='Progress:')
prog_lbl.grid(row=0, column=0, sticky=tk.W)

### Add Window resize support
# TODO - very slow

#%%
### Initialize
WELCOME_TEXT = '''
Welcome to ImageSort

In this set there are %d images that need labeling. %d are already labeled
Your progress will be displayed at the top
For each image, select the feature that best describes it and press submit
Feel free to exit the program and relaunch it later, your progress is saved with every submit
''' % (len(images), cur_index+1)

reset()

#Check if already labeled
if cur_index == len(output_data) - 1:
    finish()

print(WELCOME_TEXT)
messagebox.showinfo('Welcome to ImageSort', WELCOME_TEXT, parent=window)
window.update()

### run the main loop

window.mainloop()

