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
#import matplotlib.pyplot as plt

# defined functions
from open_file_gui import import_filepath_gui
from open_file_gui import import_filename_gui
from process_CTAC import process_ACCT_fix

tic = time.time()
"""
 select directory of CTAC to edit
"""
current_dir = os.getcwd() # location of UIH_ACCT_imagebased_fix-main

print ('')        
print ('Locate image directory and select the CTAC_ image folder \n')
ctac_filename_and_path = import_filepath_gui() #open gui to select directory and files to edit
ctac_path = os.path.dirname(ctac_filename_and_path)
ctac_name = os.path.basename(ctac_filename_and_path)
print('  Selected CTAC image dir: ' + ctac_filename_and_path)


"""
    ---- REPLACE NC FILES ------------------------------------------------
"""
print ('')        
print ('Locate the associated raw data folder and click the  *.1.nc file \n')
rawdata_filename_and_path = import_filename_gui() #open gui to select directory and files to edit

if rawdata_filename_and_path[len(rawdata_filename_and_path)-4:len(rawdata_filename_and_path)] != '1.nc': # check that 1.nc is selected
    print ('Warning, wrong file selected: ' + rawdata_filename_and_path)
    
rawdata_file_path = os.path.dirname(rawdata_filename_and_path)
rawdata_file_name = os.path.basename(rawdata_filename_and_path)


# define copy directory EXPLORER
#rawdata_file_name_ = rawdata_file_name.replace('nc','_')
copy_dir = ctac_path[0:len(ctac_path)-6]+'_CTAC_fix_repo'

if os.path.exists(copy_dir) == False:         
    os.mkdir(copy_dir)
else: 
    print ('This raw data has been edited previously... \n')
     
print ('  Copy from:  '+ctac_path+'\n')
print ('  Copy to:  '+copy_dir+'\n')

# copy all rawdata nc and dcm files to copy dir
rawdata_filename_and_path_dcm = rawdata_filename_and_path.replace('nc', 'dcm') #get dcm name
for i in range (1,9): 
    shutil.copy(rawdata_filename_and_path.replace('.1.nc','.'+str(i)+'.nc'), copy_dir) #copy nc file
    shutil.copy(rawdata_filename_and_path_dcm.replace('.1.dcm','.'+str(i)+'.dcm'), copy_dir) #copy dcm file


"""
    CHOOSE NEW NC FILE
"""
# select new nc file to replace current nc file
print ('Select new nc file to replace current nc file (choose nc version closest to scan date) \n')

os.chdir(current_dir + os.sep + 'nc_files') # change path to nc directory
#rawdata_filename_and_path_newnc = import_filename_gui() #open gui to select directory and files to edit
#print ('nc : '+rawdata_filename_and_path_newnc)
rawdata_filename_and_path_newnc = 'C:/Users/UIH/Desktop/UIH_ACCT_imagebased_fix-main/nc_files/v9_Jan16_2021.nc'

nc_rawdata_file_name = os.path.basename(rawdata_filename_and_path_newnc)

rawdata_file_name_nc = os.path.basename(rawdata_filename_and_path_newnc)
print ('Changing nc to: '+rawdata_file_name_nc)

for i in range (1,9): #change nodes 1 - 8
    rawdata_filename_and_path_i = rawdata_filename_and_path.replace('.1.nc','.'+str(i)+'.nc')        
    shutil.copy(rawdata_filename_and_path_newnc, rawdata_filename_and_path_i)
    
print ('All .nc files replaced \n')
"""
   ---- REPLACE DCM FILES -----------------------------------------
""" 
# check which nc file was selected and corresponding QF
if nc_rawdata_file_name == 'v5.nc':  
    dose_cal_factor = 221127.015625
    print ('New dose cal factor = '+str(dose_cal_factor))
elif nc_rawdata_file_name == 'v8_Oct30_2020.nc':
    dose_cal_factor = 239663.968/0.98 #from qf cal on 10/30/2020
    print ('New dose cal factor = '+str(dose_cal_factor))
elif nc_rawdata_file_name == 'v9_Jan16_2021.nc':
    dose_cal_factor = 245386.95 #from qf cal on 1/16/2021
    print ('New dose cal factor = '+str(dose_cal_factor))
else: 
    print ('No QF selected!!') 

dcm_to_edit = pydicom.dcmread(rawdata_filename_and_path_dcm) # get dcm data
test = dcm_to_edit[0x00067, 0x002C] # QF tag specified by recon team 
test.value = dose_cal_factor # change value 

for i in range (1,9): 
    dcm_to_edit.save_as(rawdata_filename_and_path_dcm.replace('.1.dcm','.'+str(i)+'.dcm') )

print ('All .dcm files replaced \n')


"""
    COPY CTAC IMAGES TO MODIFY
"""

# define copy directory with extension '_fix'
ctac_fix_dir = ctac_path+'/'+ctac_name+'_fix'

if os.path.exists(ctac_fix_dir) == False:
    print ('')       
    print ('Copying CTAC image folder -> CTAC_fix ')
    
    os.mkdir(ctac_fix_dir)
    os.chdir(ctac_filename_and_path) #chg directory 
    num_ims = len([name for name in os.listdir('.') if os.path.isfile(name)])
    for i in range (1,10):    
        image_name = '0000000' + str(i) + '.dcm'
        shutil.copyfile(ctac_filename_and_path+'/'+image_name, ctac_fix_dir+'/'+image_name) #copy ACCT images to _fix folder     
        
    for i in range (10,100):    
        image_name = '000000' + str(i) + '.dcm'
        shutil.copyfile(ctac_filename_and_path+'/'+image_name, ctac_fix_dir+'/'+image_name) #copy ACCT images to _fix folder   
        
    for i in range (100,num_ims+1):    
        image_name = '00000' + str(i) + '.dcm'
        shutil.copyfile(ctac_filename_and_path+'/'+image_name, ctac_fix_dir+'/'+image_name) #copy ACCT images to _fix folder   
    
    # copy the orginal CTAC DICOM image directory to repository edits 
    repo_ctac_dir = copy_dir+'/'+ctac_name
    shutil.copytree(ctac_filename_and_path, repo_ctac_dir)
    
else: 
    print ('Warning: The CTAC has been edited previously! Editing data already in: ' +str(ctac_filename_and_path)+' \n')


"""
  --------  RUN PROCESS ACCT_fix   ---------------------------------
"""

CTAC_image_volume_update = process_ACCT_fix(ctac_fix_dir)

"""
    WRITE UPDATED AACT IMAGE DATA TO DCM FILE
"""
print ('START: writing fixed CTAC DICOM files')
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
  

print ('DONE: writing fixed CTAC DICOM files \n')

shutil.rmtree(ctac_filename_and_path)

# display loading time
toc = time.time()
load_time = toc - tic
print ('load time = '+ str(load_time)+'seconds elapsed')
