#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  8 14:18:21 2024

@author: francoisramon
"""

import nibabel as nib
from nibabel import parrec


def get_actual_dynamics(rec_file_path, slices_per_dynamic):
    # Set up the file maps for PAR and REC files
    par_file_path = rec_file_path.replace('.REC', '.PAR')  # Assume matching .PAR file
    parrec_img = parrec.load(par_file_path, permit_truncated=True)  # Load with truncation allowed
    
    # Now get the actual total number of slices in the REC file
    total_slices = parrec_img.shape[-1]
    
    # Calculate the actual dynamics count
    actual_dynamics = total_slices // slices_per_dynamic
    remainder = total_slices % slices_per_dynamic
    
    if remainder != 0:
        print(f"Warning: There are {remainder} extra slices, indicating a mismatch.")
    
    return actual_dynamics

# Example usage
rec_file_path = '/Volumes/My Passport/source_data/sub-107MAPSA/ses-pre/1-07MAPSA-dot-SENSE-4-1.REC'
slices_per_dynamic = 41  # replace with the correct slice count per dynamic

actual_dynamics = get_actual_dynamics(rec_file_path, slices_per_dynamic)
print("Actual number of dynamics:", actual_dynamics)