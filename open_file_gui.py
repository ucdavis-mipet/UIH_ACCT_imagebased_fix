#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  4 09:14:04 2020

@author: Jeff
"""
import tkinter as tk 
from tkinter import filedialog

def import_filepath_gui():
    pass

    root = tk.Tk()
    root.withdraw()

    filedirectory = filedialog.askdirectory()
    return filedirectory 

def import_filename_gui():
    pass

    root = tk.Tk()
    root.withdraw()

    filepath = filedialog.askopenfilename()
    return filepath 
