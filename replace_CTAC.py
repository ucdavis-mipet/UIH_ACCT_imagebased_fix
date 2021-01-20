#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on  01/14/2021

@author: Jeff
"""

import numpy as np
import pydicom
import time
import os
import shutil
import matplotlib.pyplot as plt

# defined functions
from open_file_gui import import_filepath_gui
from process_CTAC import process_ACCT_fix

tic = time.time()
# select directory of raw data to edit
current_dir = os.getcwd() #current folder 

print ''        
print 'Locate image directory and select AACT image folder \n' 
filename_and_path_aact = import_filepath_gui() #open gui to select directory and files to edit
file_path_acct = os.path.dirname(filename_and_path_aact)
file_name_acct = os.path.basename(filename_and_path_aact)

print ''        
print 'Locate image directory and select PET image folder \n' 
filename_and_path_pet = import_filepath_gui() #open gui to select directory and files to edit
file_path_pet = os.path.dirname(filename_and_path_pet)
file_name_pet = os.path.basename(filename_and_path_pet)

"""
    COPY ACCT IMAGES TO MODIFY
"""

# define copy directory with extension '_fix'
copy_dir = file_path_acct+'/'+file_name_acct+'_fix'

if os.path.exists(copy_dir) == False:
    print ''       
    print 'Copying ACCT image folder -> ACCT_fix ' 
    
    os.mkdir(copy_dir)
    os.chdir(filename_and_path_aact) #chg directory 
    num_ims = len([name for name in os.listdir('.') if os.path.isfile(name)])
    for i in range (1,10):    
        image_name = '0000000' + str(i) + '.dcm'
        shutil.copyfile(filename_and_path_aact+'/'+image_name, copy_dir+'/'+image_name) #copy ACCT images to _fix folder     
        
    for i in range (10,100):    
        image_name = '000000' + str(i) + '.dcm'
        shutil.copyfile(filename_and_path_aact+'/'+image_name, copy_dir+'/'+image_name) #copy ACCT images to _fix folder   
        
    for i in range (100,num_ims+1):    
        image_name = '00000' + str(i) + '.dcm'
        shutil.copyfile(filename_and_path_aact+'/'+image_name, copy_dir+'/'+image_name) #copy ACCT images to _fix folder   
    print 'Done copying ACCT to fix'
else: 
    print 'Warning: ACCT has been edited previously! \n'


"""
    RUN PROCESS ACCT_fix
"""
CTAC_image_volume_update = process_ACCT_fix(copy_dir, filename_and_path_pet)


"""
    WRITE UPDATED AACT IMAGE DATA TO DCM FILE
"""
print 'START: writing new dcm files'
[x,y,z] = CTAC_image_volume_update.shape
slice_array_scaled = np.zeros([x,y])

for i in range (1,10):    
    image_name = '0000000' + str(i) + '.dcm'
    slice_i = pydicom.dcmread(image_name) #load pydicom object
    scale_factor = slice_i.RescaleSlope #get slice scale factor
    scale_intercept = slice_i.RescaleIntercept #get slice intercept
    
    slice_array_scaled = CTAC_image_volume_update[:,:,i-1] / scale_factor - scale_intercept #invert scale and subtract intercept 
    slice_array_scaled = slice_array_scaled.astype('int16')
    slice_i.PixelData = slice_array_scaled.tobytes() #write pixel data data to dcm
    slice_i.save_as(image_name) #save dcm file
    
for i in range (10,100):
    image_name = '000000' + str(i) + '.dcm'
    slice_i = pydicom.dcmread(image_name) #load pydicom object
    scale_factor = slice_i.RescaleSlope #get slice scale factor
    scale_intercept = slice_i.RescaleIntercept #get slice intercept
    
    slice_array_scaled = CTAC_image_volume_update[:,:,i-1] / scale_factor - scale_intercept #invert scale and subtract intercept 
    slice_array_scaled = slice_array_scaled.astype('int16')
    slice_i.PixelData = slice_array_scaled.tobytes() #write pixel data data to dcm
    slice_i.save_as(image_name) #save dcm file

for i in range (100,num_ims+1):
    image_name = '00000' + str(i) + '.dcm'
    slice_i = pydicom.dcmread(image_name) #load pydicom object
    scale_factor = slice_i.RescaleSlope #get slice scale factor
    scale_intercept = slice_i.RescaleIntercept #get slice intercept
    
    slice_array_scaled = CTAC_image_volume_update[:,:,i-1] / scale_factor - scale_intercept #invert scale and subtract intercept 
    slice_array_scaled = slice_array_scaled.astype('int16')
    slice_i.PixelData = slice_array_scaled.tobytes() #write pixel data data to dcm
    slice_i.save_as(image_name) #save dcm file
  

print 'DONE: writing new dcm files'





file_name_dcm = file_name.replace('nc', 'dcm')
filename_and_path_dcm = filename_and_path.replace('nc', 'dcm')
shutil.copy(filename_and_path_dcm, current_dir+'/repository_edits/'+file_name_dcm)  #copy dcm file



"""
    REPLACE NC FILES
"""
# select new nc file to replace current nc file
print 'Select new nc file to replace current nc file \n' 

os.chdir(current_dir+'/nc_files') # change path to nc directory
filename_and_path_newnc = import_filename_gui() #open gui to select directory and files to edit
nc_file_name = os.path.basename(filename_and_path_newnc)

file_name_nc = os.path.basename(filename_and_path_newnc)
print 'Changing nc to: '+file_name_nc

for i in range (1,9): #change nodes 1 - 8
    filename_and_path_i = filename_and_path.replace('.1.nc','.'+str(i)+'.nc')        
    #print filename_and_path_i
    shutil.copy(filename_and_path_newnc, filename_and_path_i)
    
print 'All .nc files replaced \n'
"""
    REPLACE DCM FILES
""" 
# check which nc file was selected and corresponding QF
if nc_file_name == 'v5.nc':  
    dose_cal_factor = 221127.015625
    print 'New dose cal factor = '+str(dose_cal_factor)
else: 
    print 'No QF selected!!' 

dcm_to_edit = pydicom.dcmread(filename_and_path_dcm) # get dcm data
test = dcm_to_edit[0x00067, 0x002C] # QF tag specified by recon team 
test.value = dose_cal_factor # change value 

for i in range (1,9): 
    dcm_to_edit.save_as(filename_and_path_dcm.replace('.1.dcm','.'+str(i)+'.dcm') )

print 'All .dcm files replaced \n'

# display loading time
toc = time.time()
load_time = toc - tic
print 'load time = '+ str(load_time)+'seconds elapsed'
