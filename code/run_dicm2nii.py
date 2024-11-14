import matlab.engine
import os
import glob
import scipy.io
import json
import numpy as np


###################   UTILS FUNCTIONS : .mat to .json  ###################

# flatten dictionary structure 
def flatten_dict(d):
    items = {}
    for k, v in d.items():
        if isinstance(v, dict):
            items.update(flatten_dict_no_prefix(v))
        elif isinstance(v, np.ndarray):
            if v.dtype == 'object':
                items[k] = [flatten_dict_no_prefix(item) if isinstance(item, dict) else mat_to_json_compatible(item) for item in v.flat]
            else:
                items[k] = v.tolist()
        elif hasattr(v, '_fieldnames'):
            struct_dict = {field: mat_to_json_compatible(getattr(v, field)) for field in v._fieldnames}
            items.update(flatten_dict_no_prefix(struct_dict))
        else:
            items[k] = v
    return items

# Convert complex data types to JSON-compatible formats
def mat_to_json_compatible(data):
    if isinstance(data, np.ndarray):
        return data.tolist()
    elif isinstance(data, (int, float, str, bool)):
        return data
    elif hasattr(data, '_fieldnames'):
        return {field: mat_to_json_compatible(getattr(data, field)) for field in data._fieldnames}
    else:
        return str(data)

def mat2json(mat_file_path,json_file_path):
    mat_data = scipy.io.loadmat(mat_file_path, struct_as_record=False, squeeze_me=True)
    json_data = flatten_dict({key: mat_to_json_compatible(value) for key, value in mat_data.items() if not key.startswith('__')})

    with open(json_file_path, 'w') as json_file:
        json.dump(json_data, json_file, indent=4)


#### Ca a ameliorer (chercher dans bids coiner tsv)
file_list = ["1-07MAPSA-dot-SENSE-4-1.PAR","1-07MAPSA-stop-SENSE-6-1.PAR"]
task_list =["dot","stop"]

# add boucle sur ça
subject_id = "107MAPSA"
session_id = "pre"


for i,file in enumerate(file_list):

	input_dir = os.path.join("/Users/francoisramon/Downloads/sub-107MAPSA_CD/ses-pre",file)
	output_dir = '/Users/francoisramon/Downloads/sub-107MAPSA_CD/rawdata/ses-pre/func'

	if not os.path.isdir(output_dir):
		os.makedirs(output_dir)


	## RUN DICM2NII

	eng = matlab.engine.start_matlab()
	eng.addpath('/Users/francoisramon/dicm2nii')  
	eng.dicm2nii(input_dir, output_dir, nargout=0)
	eng.quit()

	## CONVERT MAT FILE TO JSON

	mat_file_path = os.path.join(output_dir,"dcmHeaders.mat")
	json_file_path = os.path.join(output_dir,f"sub-{subject_id}_ses-{session_id}_task-{task_list[i]}_bold.json")

	mat2json(mat_file_path,json_file_path)
	os.remove(mat_file_path)

	## RENAME NII.GZ FILE TO BIDS

	out_nii_file = glob.glob(f'/Users/francoisramon/Downloads/sub-107MAPSA_CD/rawdata/ses-pre/func/*{task_list[i]}*.nii.gz')[0]
	out_nii_bids_file = os.path.join(output_dir,f"sub-{subject_id}_ses-{session_id}_task-{task_list[i]}_bold.nii.gz")
	os.rename(out_nii_file,out_nii_bids_file)










