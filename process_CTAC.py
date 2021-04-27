#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 14 08:07:08 2021

@author: Jeff
"""

import pydicom
import numpy as np
import os

def process_ACCT_fix(ACCT_im_dir):
    
    os.chdir(ACCT_im_dir) #chg directory 
    num_slices = len([name for name in os.listdir('.') if os.path.isfile(name)]) #get number of slices in directory
    print ('Loading '+str(num_slices)+' ACCT slices to numpy')
    
    #get image matrix size
    test = pydicom.dcmread('00000001.dcm')
    test_im = test.pixel_array
    matrix_size = int(np.sqrt(np.size(test_im)))
    
    [x_dim, y_dim] = test.PixelSpacing
    z_dim = test.SliceThickness
    trans_FOV = matrix_size * x_dim

    image_volume = np.zeros([matrix_size,matrix_size,num_slices]) #allocate np array for image  
    image_mask = np.ones([matrix_size,matrix_size,num_slices]) #allocate np array for mask  
    image_volume_update = np.zeros([matrix_size,matrix_size,num_slices]) #allocate np array for image
    #print ('START: loading ACCT pixel data')
    for i in range (1,10):
    
        image_name = '0000000' + str(i) + '.dcm'
        slice_i = pydicom.dcmread(image_name)
        scale_factor = slice_i.RescaleSlope
        scale_intercept = slice_i.RescaleIntercept
        slice_array = slice_i.pixel_array
        slice_array_scaled = slice_array * scale_factor + scale_intercept
        image_volume[:,:,i-1] = slice_array_scaled
    
    for i in range (10,100):
        image_name = '000000' + str(i) + '.dcm'
        slice_i = pydicom.dcmread(image_name)
        scale_factor = slice_i.RescaleSlope
        scale_intercept = slice_i.RescaleIntercept
        slice_array = slice_i.pixel_array
        slice_array_scaled = slice_array * scale_factor + scale_intercept
        image_volume[:,:,i-1] = slice_array_scaled

    for i in range (100,num_slices):
        image_name = '00000' + str(i) + '.dcm'
        slice_i = pydicom.dcmread(image_name)
        scale_factor = slice_i.RescaleSlope
        scale_intercept = slice_i.RescaleIntercept
        slice_array = slice_i.pixel_array
        slice_array_scaled = slice_array * scale_factor + scale_intercept
        image_volume[:,:,i-1] = slice_array_scaled
  

    print ('Applying HU changes')
    """
    APPLY CT-IMAGE HU CHANGES
    """
    restricted_FOV_size = 500 #beyond this fov (in mm) to mask and threshold
    HU_thresh = -700
    for z in range(0,num_slices):

        for y in range(0,matrix_size):

            for x in range(0,matrix_size):
                 
                 x_ = x*x_dim-matrix_size*x_dim/2
                 y_ = y*y_dim-matrix_size*y_dim/2
            
                 if(x_*x_ + y_*y_ >= np.power(restricted_FOV_size/2,2) and image_volume[x,y,z] <= HU_thresh):
                     image_mask[x,y,z] = 0
                     #print 'x'
                     
    image_volume_update = (image_volume+1000)*image_mask - 1000   
    print ('Return fixed image volume \n')
              
    return image_volume_update
