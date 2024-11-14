import matlab.engine
import os
import glob
import scipy.io
import json
import numpy as np
import pandas as pd
from tqdm import tqdm
import nibabel as nib

###################   UTILS FUNCTIONS : .mat to .json  ###################

# flatten dictionary structure 
def flatten_dict(d):
    items = {}
    for k, v in d.items():
        if isinstance(v, dict):
            items.update(flatten_dict(v))
        elif isinstance(v, np.ndarray):
            if v.dtype == 'object':
                items[k] = [flatten_dict(item) if isinstance(item, dict) else mat_to_json_compatible(item) for item in v.flat]
            else:
                items[k] = v.tolist()
        elif hasattr(v, '_fieldnames'):
            struct_dict = {field: mat_to_json_compatible(getattr(v, field)) for field in v._fieldnames}
            items.update(flatten_dict(struct_dict))
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



### LIre bidscoiner.tsv
### Si il y a une ligne dot.PAR mais pas de dot nifti



sourcedata_dir =  "/Volumes/My Passport/source_data"
rawdata_dir = "/Volumes/My Passport/rawdata"

bidscoiner_history = os.path.join(rawdata_dir,"code","bidscoin","bidscoiner.tsv")
df_bidscoiner_history = pd.read_csv(bidscoiner_history,sep = '\t')



task_list = ["dot","stop"]
csv_data = []

convert_dot_stop = False

if convert_dot_stop:

	for task in task_list:

		files_df = df_bidscoiner_history[
	    df_bidscoiner_history['source'].str.contains(task) & 
	    df_bidscoiner_history['targets'].isna()
		]

		list_files2process = files_df["source"].to_list()

		for file in tqdm(list_files2process):

			subject_id = file.split("/")[4]
			session_id = file.split("/")[5]
			source_path = "/".join(file.split("/")[:6]) + '/'

			task_subses = df_bidscoiner_history[
	    			df_bidscoiner_history['source'].str.contains(task) & 
	    			df_bidscoiner_history['source'].str.contains(source_path) & 
	    			df_bidscoiner_history['targets'].isna()
			]
			list_files_task = task_subses["source"].to_list()


			#if sourcedata_dir == "/Volumes/My Passport/source_data":
			if subject_id == "sub-218LELAM":

				if len(list_files_task) == 1:


					filename = os.path.basename(file)



					print(f"Convert {subject_id} - {session_id} : {filename}")


					input_dir = file
					output_dir = os.path.join(rawdata_dir,subject_id,session_id,"func")

					if not os.path.isdir(output_dir):
						os.makedirs(output_dir)

					# RUN DICM2NII

					eng = matlab.engine.start_matlab()
					eng.addpath('/Users/francoisramon/dicm2nii')  
					eng.dicm2nii(input_dir, output_dir, nargout=0)
					eng.quit()

						# CONVERT MAT FILE TO JSON

					mat_file_path = os.path.join(output_dir,"dcmHeaders.mat")
					json_file_path = os.path.join(output_dir,f"{subject_id}_{session_id}_task-{task}_bold.json")

					mat2json(mat_file_path,json_file_path)
					os.remove(mat_file_path)

						# RENAME NII.GZ FILE TO BIDS

					out_nii_file = glob.glob(f'{output_dir}/*{task}*.nii.gz')[0]
					out_nii_bids_file = os.path.join(output_dir,f"{subject_id}_{session_id}_task-{task}_bold.nii.gz")
					os.rename(out_nii_file,out_nii_bids_file)

					csv_data.append([file, out_nii_bids_file])

				elif len(list_files_task) == 2:



					file_position = list_files_task.index(file)

					print(file_position)

					run_id = file_position + 1

					print(f"convert {file} and name it run {run_id}")


					input_dir = file
					output_dir = os.path.join(rawdata_dir,subject_id,session_id,"func")

					if not os.path.isdir(output_dir):
						os.makedirs(output_dir)

					## RUN DICM2NII

					eng = matlab.engine.start_matlab()
					eng.addpath('/Users/francoisramon/dicm2nii')  
					eng.dicm2nii(input_dir, output_dir, nargout=0)
					eng.quit()

						## CONVERT MAT FILE TO JSON

					mat_file_path = os.path.join(output_dir,"dcmHeaders.mat")
					json_file_path = os.path.join(output_dir,f"{subject_id}_{session_id}_task-{task}_run-{run_id}_bold.json")


					mat2json(mat_file_path,json_file_path)
					os.remove(mat_file_path)

						## RENAME NII.GZ FILE TO BIDS

					out_nii_file = glob.glob(f'{output_dir}/*{task}*_1.nii.gz')[0]  ### ajouter run 
					out_nii_bids_file = os.path.join(output_dir,f"{subject_id}_{session_id}_task-{task}_run-{run_id}_bold.nii.gz")

					os.rename(out_nii_file,out_nii_bids_file)
					csv_data.append([file, out_nii_bids_file])


	csv_output_path = os.path.join(rawdata_dir, "command_history_dot_stop.csv")
	df_csv_output = pd.DataFrame(csv_data, columns=['source_file', 'destination'])
	df_csv_output.to_csv(csv_output_path, index=False)





files2delete = glob.glob(f"{rawdata_dir}/sub-*/ses-*/func/*_1.nii.gz")
print(files2delete)

for files in files2delete:
	os.remove(files)


subject_list = [s for s in os.listdir(rawdata_dir) if "sub" in s]

for task in task_list:

	for sub in subject_list:
		session_list = [s for s in os.listdir(os.path.join(rawdata_dir,sub)) if "ses" in s]

		for ses in session_list:

			source_path = sourcedata_dir + "/" + sub + "/"+ ses+ '/'

			task_subses = df_bidscoiner_history[
				df_bidscoiner_history['source'].str.contains(task) & 
				df_bidscoiner_history['source'].str.contains(source_path) & 
				df_bidscoiner_history['targets'].isna()
			]

			# if len(task_subses["targets"].to_list()) >1:
			# 	print(f"{sub} - {ses} : repeated {task}")

			session_path = os.path.join(rawdata_dir,sub,ses)

			if len(glob.glob(f"{session_path}/func/*{task}*.nii.gz")) != 0:

				task_runs = glob.glob(f"{session_path}/func/*{task}_run-*_bold.json")
				if len(task_runs) != 0:
					print(f" {sub} - {ses} - repeated func {task} ")

					dim_list = []

					for task_run in task_runs:
						with open(task_run,'r') as file:
							json_data= json.load(file)
							dim4 = json_data.get("NumberOfTemporalPositions")
							dim_list.append(dim4)

					print(dim_list)

						
#### 511 Dans le cahier d'aquisition : STOP refait après DTI : DTIseries7 et stopseries9 donc on garde series 9					

















