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



sourcedata_dir =  "/Volumes/CurrentDisk/APEX/apex_enf/source_data"
rawdata_dir = "/Volumes/CurrentDisk/APEX/apex_enf/rawdata"

bidscoiner_history = os.path.join(rawdata_dir,"code","bidscoin","bidscoiner.tsv")
df_bidscoiner_history = pd.read_csv(bidscoiner_history,sep = '\t')

task_list = ["stop","dot"]
csv_data = []

convert_dot_stop = True
correct_runs = True
### A la place aller chercher dans source_data. glob etc

if convert_dot_stop:

	for task in task_list:

		if task == "stop":
			task_bids = "sst"
		elif task == "dot":
			task_bids = "dot"


		files_df = df_bidscoiner_history[
	    df_bidscoiner_history['source'].str.contains(task) & 
	    df_bidscoiner_history['targets'].isna()
		]

		list_files2process = files_df["source"].to_list()

		list_files2process = glob.glob(f"{sourcedata_dir}/sub-*/ses-*/*{task}*.PAR")

		### ICI ajouter : il ne doit pas y avoir de file dot/stop dans rawdata --> glob glob doit etre vide


		print(list_files2process)

		for file in tqdm(list_files2process):

			file_split_length = len(sourcedata_dir.split("/"))
			split_index = file_split_length + 2

			subject_id = file.split("/")[file_split_length]
			session_id = file.split("/")[file_split_length + 1]
			source_path = "/".join(file.split("/")[:split_index]) + '/'

			# task_subses = df_bidscoiner_history[
	    	# 		df_bidscoiner_history['source'].str.contains(task) & 
	    	# 		df_bidscoiner_history['source'].str.contains(source_path) & 
	    	# 		df_bidscoiner_history['targets'].isna()
			# ]
			# list_files_task = task_subses["source"].to_list()

			list_files_task = glob.glob(f"{source_path}/*{task}*.PAR")
			print(list_files_task)

			existing_file = glob.glob(f"{rawdata_dir}/{subject_id}/{session_id}/*{task_bids}*.nii.gz")

			if len(existing_file) == 0:

				if len(list_files_task) == 1:

					#if len(list_files_task) == 1:


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


					#eng.dicm2nii("/Volumes/BackupDisk/APEX/apex_enf/source_data/sub-523GUYPA/ses-post/5-23GUYPA-DTI2-3-alt-topup-8-1.PAR","/Volumes/BackupDisk/APEX/apex_enf/source_data/sub-523GUYPA/ses-post",nargout = 0)

							# CONVERT MAT FILE TO JSON

					mat_file_path = os.path.join(output_dir,"dcmHeaders.mat")
					json_file_path = os.path.join(output_dir,f"{subject_id}_{session_id}_task-{task_bids}_bold.json")

					mat2json(mat_file_path,json_file_path)
					os.remove(mat_file_path)

							# RENAME NII.GZ FILE TO BIDS

					out_nii_file = glob.glob(f'{output_dir}/*{task}*.nii.gz')[0]
					out_nii_bids_file = os.path.join(output_dir,f"{subject_id}_{session_id}_task-{task_bids}_bold.nii.gz")
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
					json_file_path = os.path.join(output_dir,f"{subject_id}_{session_id}_task-{task_bids}_run-{run_id}_bold.json")


					mat2json(mat_file_path,json_file_path)
					os.remove(mat_file_path)

					## RENAME NII.GZ FILE TO BIDS

					out_nii_file = glob.glob(f'{output_dir}/*{task}*_1.nii.gz')[0]  ### ajouter run 
					out_nii_bids_file = os.path.join(output_dir,f"{subject_id}_{session_id}_task-{task_bids}_run-{run_id}_bold.nii.gz")

					os.rename(out_nii_file,out_nii_bids_file)
					csv_data.append([file, out_nii_bids_file])


	csv_output_path = os.path.join(rawdata_dir, "command_history_dot_stop.csv")
	df_csv_output = pd.DataFrame(csv_data, columns=['source_file', 'destination'])
	df_csv_output.to_csv(csv_output_path, index=False)



# files2delete = glob.glob(f"{rawdata_dir}/sub-*/ses-*/func/*dot*")
# print(files2delete)

# for files in files2delete:
# 	os.remove(files)


task_list = ["dot","sst"]


if correct_runs:
	subject_list = [s for s in os.listdir(rawdata_dir) if "sub" in s]

	#subject_list = ["sub-227JOUAN"]

	columns = ["subject_id", "session_id", "comment"]
	comments_df = pd.DataFrame(columns=columns)

	for task in task_list:

		for sub in subject_list:


			session_list = [s for s in os.listdir(os.path.join(rawdata_dir,sub)) if "ses" in s]

			#session_list = ["ses-pre"]

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

						index2keep = dim_list.index(max(dim_list))  ### Ici on prend l'index du run qui a le plus de temporal position


						print(index2keep)

						if index2keep == 0:
							index2delete = 1
						elif index2keep == 1:
							index2delete = 0

						comment = f"Two {task}, one file has {min(dim_list)} volumes, the other {max(dim_list)}. Keep larger"
								# Append a new row to the comments DataFrame
						comments_df = pd.concat(
							[
								comments_df, 
								pd.DataFrame(
									[[sub, ses, comment]], 
									columns=columns
								)
							], 
							ignore_index=True
						)


						filepath_root2keep = task_runs[index2keep][:-5]

						split_filepath = filepath_root2keep.split("_")


						newfilepath_root2keep = "_".join(split_filepath[:-2]) + "_" + split_filepath[-1]

						print(newfilepath_root2keep)

						os.rename(f'{filepath_root2keep}.json',f"{newfilepath_root2keep}.json")
						os.rename(f'{filepath_root2keep}.nii.gz',f"{newfilepath_root2keep}.nii.gz")

						os.remove(task_runs[index2delete])

						nii2delete = task_runs[index2delete][:-5] + ".nii.gz"

						os.remove(nii2delete)

	comments_df.to_csv("/Volumes/BackupDisk/APEX/apex_enf/comments/comments_task_fmri.csv", index=False)

						####### Ajouter au csv "keep {task} with n volumes, delete file with less (k) volumes"


					#newfilepath_nii = task_runs[index2keep][:-4] + ".nii.gz"



					#os.rename(task_runs,)

#### Changer les champs json dot/stop en accord avec les autre json (dwi, func...)





						
#### 511 Dans le cahier d'aquisition : STOP refait après DTI : DTIseries7 et stopseries9 donc on garde series 9					

















