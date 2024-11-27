import os
import pydicom

raw_structure_dir = '/Volumes/My Passport/raw_organized'
raw_source_dir = '/Volumes/My Passport/sub-enf'

## APEX 027 = enfci029


folder_name = "sub-enfci209_ses-postdiff_mri-1484133270-DICOM-3DT1"
filename = os.listdir(os.path.join(raw_source_dir,folder_name))[0]

filepath = os.path.join(raw_source_dir,folder_name,filename)

dicom_data = pydicom.dcmread(filepath)
print(dicom_data)