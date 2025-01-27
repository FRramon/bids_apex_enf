import os
from tqdm import tqdm
import pandas as pd
import re
import glob
import json
from collections import defaultdict
from datetime import datetime
import subprocess
import shutil

########################################
# This script check bidscoiner conversion, and rename files after run1 run2 if one run2 is found, but no run1
# After that, it enriches every json file from the content of its associated PAR file
# Finally, duplicates dwi,dwi AP are deleted


def split_date_time(date_output):
	date, time = date_output.split(" / ")
	return date,time


def search_line(key,line):
	match = re.search(rf'{re.escape(key)}\s*:\s*(.+)', line)
	if match:
		value = match.group(1).strip()
		return value
	else:
		return None

def read_time(filepath):

	with open(filepath, 'r') as file:
			data_file = json.load(file)

			exam_date = data_file.get("Examination date/time", "Field not found")
			exam_date = data_file.get("AcquisitionDateTime", "Field not found")


	pattern = r"(\d{4}\.\d{2}\.\d{2}) / (\d{2}:\d{2}:\d{2})"
		# Find the match
	match = re.search(pattern, exam_date)

	if match:
			# Extract date and time parts
		date_part = match.group(1)
		time_part = match.group(2)
			# Combine and convert to datetime object
		datetime_obj = datetime.strptime(f"{date_part} {time_part}", "%Y.%m.%d %H:%M:%S")
		return datetime_obj
	else:
		print("No match found!")

def get_run_id(filepath):
	basename = os.path.basename(filepath)

	run_id = basename.split("_")[-2][-1]
	return run_id

def get_files_run(json_filepath,run_id):

	## /VOlumes... /anat/sub_ses_run-1_T2 json/nii

	ses_dir = os.path.dirname(json_filepath)
	files2rename = [f for f in os.listdir(ses_dir) if run_id in f]

	return files2rename

def get_files_run_sesdir(ses_dir,run_id):

	## /VOlumes... /anat/sub_ses_run-1_T2 json/nii

	files2rename = [f for f in os.listdir(ses_dir) if run_id in f]

	return files2rename

def rename_run(list_files,run_id):

	## /VOlumes... /anat/sub_ses_run-1_T2 json/nii

	newfiles = []

	for files in list_files:

		rg = r"run-\d+"

		for match in re.findall(rg, files):
			files_2 = files.replace(match, run_id)

		newfiles.append(files_2)

	return newfiles


def read_par_T1(filepath):


# .    Reconstruction nr                  :   1
# .    Scan Duration [sec]                :   564
# .    Max. number of cardiac phases      :   1
# .    Max. number of echoes              :   1
# .    Max. number of slices/locations    :   176
# .    Max. number of dynamics            :   1
# .    Max. number of mixes               :   1
# .    Patient position                   :   Head First Supine
# .    Preparation direction              :   Anterior-Posterior
# .    Technique                          :   T1TFE
# .    Scan resolution  (x, y)            :   256  256
# .    Scan mode                          :   3D
# .    Repetition time [ms]               :   7.200  
# .    FOV (ap,fh,rl) [mm]                :   240.000  256.000  176.000
# .    Water Fat shift [pixels]           :   1.802
# .    Angulation midslice(ap,fh,rl)[degr]:   1.079  1.076  10.246
# .    Off Centre midslice(ap,fh,rl) [mm] :   -7.541  18.843  3.856
# .    Flow compensation <0=no 1=yes> ?   :   0
# .    Presaturation     <0=no 1=yes> ?   :   0
# .    Phase encoding velocity [cm/sec]   :   0.000000  0.000000  0.000000
# .    MTC               <0=no 1=yes> ?   :   0
# .    SPIR              <0=no 1=yes> ?   :   0
# .    EPI factor        <0,1=no EPI>     :   1
# .    Dynamic scan      <0=no 1=yes> ?   :   0
# .    Diffusion         <0=no 1=yes> ?   :   0
# .    Diffusion echo time [ms]           :   0.0000
# .    Max. number of diffusion values    :   1
# .    Max. number of gradient orients    :   1
# .    Number of label types   <0=no ASL> :   0

	patient_name = None
	protocol_name = None
	date_match = None


	key_list = [
	"Patient name",
	"Protocol name",
	"Examination date/time",
	"Series Type",
	"Acquisition nr",
	"Reconstruction nr",
	"Scan Duration [sec]",
	"Max. number of cardiac phases",
	"Max. number of echoes",
	"Max. number of slices/locations",
	"Max. number of dynamics",
	"Max. number of mixes",
	"Patient position",
	"Preparation direction",
	"Technique",
	"Scan resolution  (x, y)",
	"Scan mode",
	"Repetition time [ms]",
	"FOV (ap,fh,rl) [mm]",
	"Water Fat shift [pixels]",
	"Angulation midslice(ap,fh,rl)[degr]",
	'Off Centre midslice(ap,fh,rl) [mm]',
	'Flow compensation <0=no 1=yes> ?',
	'Presaturation     <0=no 1=yes> ?',
	'Phase encoding velocity [cm/sec]',
	'MTC               <0=no 1=yes> ?',
	'SPIR              <0=no 1=yes> ?',
	'EPI factor        <0,1=no EPI>',
	'Dynamic scan      <0=no 1=yes> ?',
	'Diffusion         <0=no 1=yes> ?',
	'Diffusion echo time [ms]',
	'Max. number of diffusion values',
	'Max. number of gradient orients',
	'Number of label types   <0=no ASL>']


	## Create json

	json_file = {} 


	with open(filepath, 'r') as file:
		for line in file:

			for key in key_list:

				res = search_line(key,line)

				if res != None:

					json_file[key] = res



	return json_file

rename_target =False ## OK change 8 / 6 by lenght of dir + k OK ## attention rename ou non?
enrich_json = False # OK
correct_run_time = False # OK
correct_run_time_T2 = False #  OK 
change_run2acq = False
delete_date = True
change_field_json = True
comment_only_T1Rs = False
# correct_fmap_epi = False
generate_conversion_table = False
check_conversion = False

source_data_dir = "/Volumes/CurrentDisk/APEX/apex_enf/source_data"
rawdata_dir = "/Volumes/CurrentDisk/APEX/apex_enf/rawdata"
base_dir =  "/Volumes/CurrentDisk/APEX/apex_enf"


bidscoiner_history = os.path.join(rawdata_dir,"code","bidscoin","bidscoiner.tsv")
df_bidcoiner_history = pd.read_csv(bidscoiner_history,sep = '\t')

# print(df_bidcoiner_history)

if rename_target:
	df_list = []

	subject_list = [s for s in os.listdir(source_data_dir) if "sub" in s]

	for sub in tqdm(subject_list):
		print(sub)
		session_list = [s for s in os.listdir(os.path.join(source_data_dir,sub)) if "ses" in s]

		for ses in session_list:

			print(ses)

			session_path = os.path.join(source_data_dir,sub,ses)

			file_split_length = len(source_data_dir.split("/"))
			split_index = file_split_length + 2

			df_bidcoiner_history["patient_path"] = df_bidcoiner_history["source"].apply(lambda x: '/'.join(x.split('/')[:split_index]))

			print(df_bidcoiner_history["patient_path"].to_list())
			print(session_path)


			sub_df_patient = df_bidcoiner_history[df_bidcoiner_history["patient_path"] == session_path]
			
			sub_df_patient = sub_df_patient.assign(targets_renamed=sub_df_patient["targets"])

			print("sub_df_patient")

			print(sub_df_patient)


			##################### CHECK T1 REPETITION   ##########################

			t1w_and_run = sub_df_patient[sub_df_patient['targets'].str.contains("T1w", case=False, na=False) & 
			                             sub_df_patient['targets'].str.contains("run", case=False, na=False)]

			t1w_no_run = sub_df_patient[sub_df_patient['targets'].str.contains("T1w", case=False, na=False) & 
			                            ~sub_df_patient['targets'].str.contains("run", case=False, na=False)]

			if len(t1w_and_run['targets'].to_list()) != 0:

				if len(t1w_no_run['targets'].to_list()) != 0:
					print("have multiple T1w : rename first one to run_1")

					print(t1w_no_run["targets"])

					original_filenames = t1w_no_run["targets"].iloc[0].split(',')

					new_filename_list = []

					for files in original_filenames:
						file_split = files.split("_")

						new_filename = '_'.join(file_split[:2]) + "_run-1_" + '_'.join(file_split[2:])

						print(f"rename {files} to {new_filename}")

						new_filename_list.append(new_filename)


					sub_df_patient.loc[sub_df_patient["targets"] == t1w_no_run["targets"].iloc[0], "targets_renamed"] = str(new_filename_list)[1:-1]

			##################### CHECK T2 REPETITION   ##########################


			# Step 1: Find rows where 'targets' contains both "T2w" and "run"
			t2w_and_run = sub_df_patient[sub_df_patient['targets'].str.contains("T2w", case=False, na=False) & 
			                             sub_df_patient['targets'].str.contains("run", case=False, na=False)]

			# Step 2: Find rows where 'targets' contains "T2w" but does NOT contain "run"
			t2w_no_run = sub_df_patient[sub_df_patient['targets'].str.contains("T2w", case=False, na=False) & 
			                            ~sub_df_patient['targets'].str.contains("run", case=False, na=False)]

			# Display results
			if len(t2w_and_run['targets'].to_list()) != 0:
				if len(t2w_no_run['targets'].to_list()) != 0:

					print("have multiple T2w : rename first one to run_1")

					print(t2w_no_run["targets"])

					original_filenames = t2w_no_run["targets"].iloc[0].split(',')

					new_filename_list = []

					for files in original_filenames:
						file_split = files.split("_")

						new_filename = '_'.join(file_split[:2]) + "_run-1_" + '_'.join(file_split[2:])

						print(f"rename {files} to {new_filename}")

						new_filename_list.append(new_filename)

					sub_df_patient.loc[sub_df_patient["targets"] == t2w_no_run["targets"].iloc[0], "targets_renamed"] = str(new_filename_list)[1:-1]
					#sub_df_patient["targets_renamed"] = str(new_filename_list)[1:-1]

				else:
					print("have only one magnitude")


			##################### CHECK MAGNITUDE REPETITION   ##########################



			magnitude_and_run = sub_df_patient[sub_df_patient['targets'].str.contains("magnitude", case=False, na=False) & 
			                             sub_df_patient['targets'].str.contains("run", case=False, na=False)]

			magnitude_no_run = sub_df_patient[sub_df_patient['targets'].str.contains("magnitude", case=False, na=False) & 
			                            ~sub_df_patient['targets'].str.contains("run", case=False, na=False)]
			print(magnitude_no_run)
			# Display results
			if len(magnitude_and_run['targets'].to_list()) != 0:
				if len(magnitude_no_run['targets'].to_list()) != 0:

					print("have multiple magnitude : rename first one to run_1")

					print(magnitude_no_run["targets"])

					original_filenames = magnitude_no_run["targets"].iloc[0].split(',')

					new_filename_list = []

					for files in original_filenames:
						file_split = files.split("_")

						new_filename = '_'.join(file_split[:2]) + "_run-1_" + '_'.join(file_split[2:])

						print(f"rename {files} to {new_filename}")
						#os.rename(files,new_filename)

						new_filename_list.append(new_filename)


					sub_df_patient.loc[sub_df_patient["targets"] == magnitude_no_run["targets"].iloc[0], "targets_renamed"] = str(new_filename_list)[1:-1]

				else:
					print("have only one magnitude")


			##################### CHECK DWI REPETITION   ##########################


			dwi_and_run = sub_df_patient[sub_df_patient['targets'].str.contains("64dirs", case=False, na=False) & 
			                             sub_df_patient['targets'].str.contains("run", case=False, na=False)]

			dwi_no_run = sub_df_patient[sub_df_patient['targets'].str.contains("64dirs", case=False, na=False) & 
			                            ~sub_df_patient['targets'].str.contains("run", case=False, na=False)]

			# Display results
			if len(dwi_and_run['targets'].to_list()) != 0:
				if len(dwi_no_run['targets'].to_list()) != 0:

					print("have multiple dwi : rename first one to run_1")

					print(dwi_no_run["targets"])

					original_filenames = dwi_no_run["targets"].iloc[0].split(',')

					new_filename_list = []

					for files in original_filenames:
						file_split = files.split("_")

						new_filename = '_'.join(file_split[:-1]) + "_run-1_" + '_'.join([file_split[-1]])

						print(f"rename {files} to {new_filename}")

						new_filename_list.append(new_filename)


					sub_df_patient.loc[sub_df_patient["targets"] == dwi_no_run["targets"].iloc[0], "targets_renamed"] = str(new_filename_list)[1:-1]

				else:
					print("have only one dwi")


			##################### CHECK DWI AP REPETITION   ##########################


			dwiap_and_run = sub_df_patient[sub_df_patient['targets'].str.contains("6dirs", case=False, na=False) & 
			                             sub_df_patient['targets'].str.contains("run", case=False, na=False)]

			dwiap_no_run = sub_df_patient[sub_df_patient['targets'].str.contains("6dirs", case=False, na=False) & 
			                            ~sub_df_patient['targets'].str.contains("run", case=False, na=False)]

			# Display results
			if len(dwiap_and_run['targets'].to_list()) != 0:
				if len(dwiap_no_run['targets'].to_list()) != 0:

					print("have multiple dwi ap : rename first one to run_1")

					print(dwiap_no_run["targets"])

					original_filenames = dwiap_no_run["targets"].iloc[0].split(',')

					new_filename_list = []

					for files in original_filenames:
						file_split = files.split("_")

						new_filename = '_'.join(file_split[:-1]) + "_run-1_" + '_'.join([file_split[-1]])

						print(f"rename {files} to {new_filename}")

						new_filename_list.append(new_filename)


					sub_df_patient.loc[sub_df_patient["targets"] == dwiap_no_run["targets"].iloc[0], "targets_renamed"] = str(new_filename_list)[1:-1]

				else:
					print("have only one dwi ap")

			##################### CHECK FUNC REST REPETITION   ##########################


			rest_and_run = sub_df_patient[sub_df_patient['targets'].str.contains("task-rest", case=False, na=False) & 
			                             sub_df_patient['targets'].str.contains("run", case=False, na=False)]

			rest_no_run = sub_df_patient[sub_df_patient['targets'].str.contains("task-rest", case=False, na=False) & 
			                            ~sub_df_patient['targets'].str.contains("run", case=False, na=False)]

			# Display results
			if len(rest_and_run['targets'].to_list()) != 0:
				if len(rest_no_run['targets'].to_list()) != 0:

					print("have multiple dwi ap : rename first one to run_1")

					print(rest_no_run["targets"])

					original_filenames = rest_no_run["targets"].iloc[0].split(',')

					new_filename_list = []

					for files in original_filenames:
						file_split = files.split("_")

						new_filename = '_'.join(file_split[:2]) + "_run-1_" + '_'.join(file_split[2:])

						print(f"rename {files} to {new_filename}")

						new_filename_list.append(new_filename)


					sub_df_patient.loc[sub_df_patient["targets"] == rest_no_run["targets"].iloc[0], "targets_renamed"] = str(new_filename_list)[1:-1]

				else:
					print("have only one rest ap")


			df_list.append(sub_df_patient)



	final_df = pd.concat(df_list, axis=0, ignore_index=True)



	final_df.to_csv(os.path.join(rawdata_dir,"sequences_info.csv"))





if enrich_json:
	sequences_info = pd.read_csv(os.path.join(rawdata_dir,"sequences_info.csv"))

	for file,datatype,targets in tqdm(zip(sequences_info["source"],sequences_info["datatype"],sequences_info["targets_renamed"]),total = len(sequences_info)):


		if not "stop" in file and not "dot" in file:


			file_split = file.split('/')

			file_split_length = len(rawdata_dir.split("/"))

			subject_id = file_split[file_split_length ] ## here it depends on length of rawdata dir
			session_id = file_split[file_split_length + 1] ## here too

			json_enrichment = read_par_T1(file)

			if isinstance(targets, str):

				target_list = targets.split(',')

				for target_elements in target_list:

					cleaned_target = target_elements.replace("'", "").replace(" ", "")

					target_json_file = os.path.join(rawdata_dir,subject_id,session_id,datatype,f"{cleaned_target[:-7]}.json")

					with open(target_json_file, 'r') as file:
						data = json.load(file)

					if isinstance(data, list):
						data.append(json_enrichment)
					elif isinstance(data, dict):
						data.update(json_enrichment)

					# Step 3: Save the updated data back to the JSON file
					with open(target_json_file, 'w') as file:
						json.dump(data, file, indent=4)

## Corrige nom run1 run2 avec les dates

if correct_run_time:

	T2_tot = 0
	correct_T1 = 0
	correct_T2 = 0
	correct_dwi = 0
	correct_dwiAP = 0
	correct_rs = 0
	correct_b0 = 0

	df_list = []

	subject_list = [s for s in os.listdir(rawdata_dir) if "sub" in s]

	for sub in tqdm(subject_list):
		session_list = [s for s in os.listdir(os.path.join(rawdata_dir,sub)) if "ses" in s]

		for ses in session_list:


			session_path = os.path.join(rawdata_dir,sub,ses)

			T1w_runs = glob.glob(f"{session_path}/anat/*_run-*_T1w.nii.gz")
			T2w_runs = glob.glob(f"{session_path}/anat/*_run-*_T2w.nii.gz")

			have_T2 = glob.glob(f"{session_path}/anat/*_T2w.nii.gz")
			dwi_runs = glob.glob(f"{session_path}/dwi/*dir-PA_run-*_dwi.nii.gz")
			dwiAP_runs = glob.glob(f"{session_path}/fmap/*dir-AP_run-*_epi.nii.gz")
			

			rs_runs = glob.glob(f"{session_path}/func/*task-rest_run-*_bold.nii.gz")
			b0_runs = glob.glob(f"{session_path}/fmap/*run-*_magnitude1.nii.gz")

			if len(have_T2) != 0:
				T2_tot += 1

			if len(T1w_runs) != 0:
				correct_T1 +=1
				print("correct T1 run")

			if len(T2w_runs) != 0:
				correct_T2 +=1
				#print("correct T2 run")

			if len(dwi_runs) != 0:
				correct_dwi += 1 
				print(f"{sub} - {ses} : correct dwi")

			if len(dwiAP_runs) != 0:
				correct_dwiAP +=1
				print(f"{sub} - {ses} : correct dwi AP")

			if len(rs_runs) != 0:
				correct_rs += 1
				print(f"{sub} - {ses} : correct rs fmri")

			### BO PAS DE PB




			# if len(T2w_runs) != 0:
			# 	print(f" {sub} - {ses} : correct run")
			# if len(T1w_runs) == 0:
			# 	print("do not correct")



			if os.path.isdir(os.path.join(session_path,'fmap')):
				# if len(b0_runs) ==0:
				# 	print(f"{sub} - {ses} : no b0")
				if len(b0_runs) == 2:

					correct_b0 += 1

					print(f"{sub} - {ses} : correct b0")
					print(b0_runs)

					fmap_dir = os.path.join(session_path,'fmap')

					filename_run1_nii = [item for item in b0_runs if "run-1" in item][0]
					filename_run1_json = filename_run1_nii[:-7] + ".json"

					newfilename_run1 = f"{sub}_{ses}_magnitude1"

					print(f"rename {filename_run1_nii} - {newfilename_run1}.nii.gz ")

					os.rename(os.path.join(fmap_dir,filename_run1_nii),os.path.join(fmap_dir,f"{newfilename_run1}.nii.gz"))
					os.rename(os.path.join(fmap_dir,filename_run1_json),os.path.join(fmap_dir,f"{newfilename_run1}.json"))

					filename_run2_nii = [item for item in b0_runs if "run-2" in item][0]
					filename_run2_json = filename_run2_nii[:-7] + ".json"
					newfilename_run2 = f"{sub}_{ses}_phase1"

					print(f"rename {filename_run2_nii} - {newfilename_run2}.nii.gz ")

					os.rename(os.path.join(fmap_dir,filename_run2_nii),os.path.join(fmap_dir,f"{newfilename_run2}.nii.gz"))
					os.rename(os.path.join(fmap_dir,filename_run2_json),os.path.join(fmap_dir,f"{newfilename_run2}.json"))


					#### Hypothèse : run-1 = magnitude, run-2 = phase


	print(f"correct T1 : {correct_T1}")
	print(f"correct T2 : {correct_T2}")
	print(f"correct dwi : {correct_dwi}")
	print(f"correct dwiAP : {correct_dwiAP}")
	print(f"correct rs : {correct_rs}")
	print(f"correct B0 : {correct_b0}")
	print(f"total T2  : {T2_tot}")


# if correct_fmap_epi:

# 	epi_files = glob.glob(f"{source_data_dir}/sub-*/ses-*/*DTI2-3-alt-topup*.PAR")

# 	temp_dir = os.path.join(base_dir,"temp_epi")
# 	if not os.path.isdir(temp_dir):
# 		os.mkdir(temp_dir)


# 	# for file in tqdm(epi_files):

# 	# 	print(file)

# 	# 	command = f"dcm2niix -o {temp_dir} -f %n_%f_%p_%4s  {file} "
# 	# 	print(command)
# 	# 	subprocess.run(command, shell = True)


# 	bv_files = glob.glob(f"{temp_dir}/*.bv*")

# 	for file in bv_files:

# 		split_file = os.path.basename(file).split("_")


# 		patient_name = split_file[0]
# 		session_id = split_file[1]

# 		patient_id = "sub-" + patient_name.replace("-","")
# 		print(patient_id)

# 		if patient_id == "sub-4":
# 			patient_id = "sub-410WISLO"
# 			session_id = split_file[2]

# 		if patient_id == "sub-143HIUEMA":
# 			patient_id = "sub-143HUEMA"

# 		if patient_id == "sub-406MALAX":
# 			patient_id = "sub-406HALAX"


# 		## recupere extension

# 		extension = os.path.basename(file)[-4:]

# 		newfilename = f"{patient_id}_{session_id}_acq-6dirs_dir-AP_epi." + extension
# 		destination = os.path.join(rawdata_dir,patient_id,session_id,"fmap")

# 		if not os.path.isfile(os.path.join(destination,newfilename)):

# 			shutil.copy(file,os.path.join(destination,newfilename))






	### patient name --> Recorriger


# sub-106GUEMA - ses-post : correct dwi
## Fichier dédoublé/ Supprimer run-1

guema_dwi_dir = os.path.join(rawdata_dir,"sub-106GUEMA","ses-post","dwi")
guema_dwi_filename = "sub-106GUEMA_ses-post_acq-64dirs_dir-PA_run-2_dwi"
guema_dwi_filename2delete = "sub-106GUEMA_ses-post_acq-64dirs_dir-PA_run-1_dwi"
guema_dwi_new_filename = "sub-106GUEMA_ses-post_acq-64dirs_dir-PA_dwi"

if os.path.isfile(os.path.join(guema_dwi_dir,f"{guema_dwi_filename}.nii.gz")):


	os.rename(os.path.join(guema_dwi_dir,f"{guema_dwi_filename}.nii.gz"),os.path.join(guema_dwi_dir,f"{guema_dwi_new_filename}.nii.gz"))
	os.rename(os.path.join(guema_dwi_dir,f"{guema_dwi_filename}.json"),os.path.join(guema_dwi_dir,f"{guema_dwi_new_filename}.json"))
	os.rename(os.path.join(guema_dwi_dir,f"{guema_dwi_filename}.bvec"),os.path.join(guema_dwi_dir,f"{guema_dwi_new_filename}.bvec"))
	os.rename(os.path.join(guema_dwi_dir,f"{guema_dwi_filename}.bval"),os.path.join(guema_dwi_dir,f"{guema_dwi_new_filename}.bval"))

	os.remove(os.path.join(guema_dwi_dir,f"{guema_dwi_filename2delete}.nii.gz"))
	os.remove(os.path.join(guema_dwi_dir,f"{guema_dwi_filename2delete}.json"))
	os.remove(os.path.join(guema_dwi_dir,f"{guema_dwi_filename2delete}.bval"))
	os.remove(os.path.join(guema_dwi_dir,f"{guema_dwi_filename2delete}.bvec"))

# sub-209MORJU - ses-pre : correct dwi
## Fichier dédoublé/ Supprimer run-1

morju_dwi_dir = os.path.join(rawdata_dir,"sub-209MORJU","ses-pre","dwi")
morju_dwi_filename = "sub-209MORJU_ses-pre_acq-64dirs_dir-PA_run-2_dwi"
morju_dwi_filename2delete = "sub-209MORJU_ses-pre_acq-64dirs_dir-PA_run-1_dwi"
morju_dwi_new_filename = "sub-209MORJU_ses-pre_acq-64dirs_dir-PA_dwi"

if os.path.isfile(os.path.join(morju_dwi_dir,f"{morju_dwi_filename}.nii.gz")):


	os.rename(os.path.join(morju_dwi_dir,f"{morju_dwi_filename}.nii.gz"),os.path.join(morju_dwi_dir,f"{morju_dwi_new_filename}.nii.gz"))
	os.rename(os.path.join(morju_dwi_dir,f"{morju_dwi_filename}.json"),os.path.join(morju_dwi_dir,f"{morju_dwi_new_filename}.json"))
	os.rename(os.path.join(morju_dwi_dir,f"{morju_dwi_filename}.bvec"),os.path.join(morju_dwi_dir,f"{morju_dwi_new_filename}.bvec"))
	os.rename(os.path.join(morju_dwi_dir,f"{morju_dwi_filename}.bval"),os.path.join(morju_dwi_dir,f"{morju_dwi_new_filename}.bval"))

	os.remove(os.path.join(morju_dwi_dir,f"{morju_dwi_filename2delete}.nii.gz"))
	os.remove(os.path.join(morju_dwi_dir,f"{morju_dwi_filename2delete}.json"))
	os.remove(os.path.join(morju_dwi_dir,f"{morju_dwi_filename2delete}.bval"))
	os.remove(os.path.join(morju_dwi_dir,f"{morju_dwi_filename2delete}.bvec"))



# sub-423DOCLO - ses-post : correct dwi AP
# sub-504MEITO - ses-pre : correct dwi

meito_dwi_dir = os.path.join(rawdata_dir,"sub-504MEITO","ses-pre","dwi")
meito_dwi_filename = "sub-504MEITO_ses-pre_acq-64dirs_dir-PA_run-2_dwi"
meito_dwi_filename2delete = "sub-504MEITO_ses-pre_acq-64dirs_dir-PA_run-1_dwi"
meito_dwi_new_filename = "sub-504MEITO_ses-pre_acq-64dirs_dir-PA_dwi"

if os.path.isfile(os.path.join(meito_dwi_dir, f"{meito_dwi_filename}.nii.gz")):

    os.rename(os.path.join(meito_dwi_dir, f"{meito_dwi_filename}.nii.gz"), os.path.join(meito_dwi_dir, f"{meito_dwi_new_filename}.nii.gz"))
    os.rename(os.path.join(meito_dwi_dir, f"{meito_dwi_filename}.json"), os.path.join(meito_dwi_dir, f"{meito_dwi_new_filename}.json"))
    os.rename(os.path.join(meito_dwi_dir, f"{meito_dwi_filename}.bvec"), os.path.join(meito_dwi_dir, f"{meito_dwi_new_filename}.bvec"))
    os.rename(os.path.join(meito_dwi_dir, f"{meito_dwi_filename}.bval"), os.path.join(meito_dwi_dir, f"{meito_dwi_new_filename}.bval"))

    os.remove(os.path.join(meito_dwi_dir, f"{meito_dwi_filename2delete}.nii.gz"))
    os.remove(os.path.join(meito_dwi_dir, f"{meito_dwi_filename2delete}.json"))
    os.remove(os.path.join(meito_dwi_dir, f"{meito_dwi_filename2delete}.bval"))
    os.remove(os.path.join(meito_dwi_dir, f"{meito_dwi_filename2delete}.bvec"))


doclo_dwi_dir = os.path.join(rawdata_dir, "sub-423DOCLO", "ses-post", "dwi")
doclo_dwi_filename = "sub-423DOCLO_ses-post_acq-6dirs_dir-AP_run-2_dwi"
doclo_dwi_filename2delete = "sub-423DOCLO_ses-post_acq-6dirs_dir-AP_run-1_dwi"
doclo_dwi_new_filename = "sub-423DOCLO_ses-post_acq-6dirs_dir-AP_dwi"

if os.path.isfile(os.path.join(doclo_dwi_dir, f"{doclo_dwi_filename}.nii.gz")):

    os.rename(os.path.join(doclo_dwi_dir, f"{doclo_dwi_filename}.nii.gz"), os.path.join(doclo_dwi_dir, f"{doclo_dwi_new_filename}.nii.gz"))
    os.rename(os.path.join(doclo_dwi_dir, f"{doclo_dwi_filename}.json"), os.path.join(doclo_dwi_dir, f"{doclo_dwi_new_filename}.json"))
    os.rename(os.path.join(doclo_dwi_dir, f"{doclo_dwi_filename}.bvec"), os.path.join(doclo_dwi_dir, f"{doclo_dwi_new_filename}.bvec"))
    os.rename(os.path.join(doclo_dwi_dir, f"{doclo_dwi_filename}.bval"), os.path.join(doclo_dwi_dir, f"{doclo_dwi_new_filename}.bval"))

    os.remove(os.path.join(doclo_dwi_dir, f"{doclo_dwi_filename2delete}.nii.gz"))
    os.remove(os.path.join(doclo_dwi_dir, f"{doclo_dwi_filename2delete}.json"))
    os.remove(os.path.join(doclo_dwi_dir, f"{doclo_dwi_filename2delete}.bval"))
    os.remove(os.path.join(doclo_dwi_dir, f"{doclo_dwi_filename2delete}.bvec"))


#here

				
if correct_run_time_T2:

	T2_list_file = glob.glob(f"{rawdata_dir}/sub-*/ses-*/anat/*run*T2w*")

	print(T2_list_file)

	list_session_dir = list(set([os.path.dirname(s) for s in T2_list_file]))

	for session_dir in list_session_dir:

		print(session_dir)
		## ouvrir tous les run-*_T2w.json, extraire date. 

		## extraire deux dates (garde en memore à quel fichier appartient)

		## min des deux --> run1
		## max des deux --> run2

		T2_runs_files = glob.glob(f"{session_dir}/*run-*part-phase_T2w.json")

		print(T2_runs_files)


		time1 = read_time(T2_runs_files[0])
		time2 = read_time(T2_runs_files[1])
	
		time_list = [time1,time2]

		print(time_list)


		run_id1 = os.path.basename(T2_runs_files[0]).split("_")[-3]
		run_id2 = os.path.basename(T2_runs_files[1]).split("_")[-3]


		if time1 < time2: 


		# 	if (run_id1 != "run-1") and (run_id2 != "run-2"):


			print(f"rename {run_id1} run 1")
			print(f"rename {run_id2} run 2")

			files_runid1 = glob.glob(f"{session_dir}/*{run_id1}*")
			files_runid1_renamed3 = rename_run(files_runid1,"run-3")

			for i,file in enumerate(files_runid1):
				print(f"rename {os.path.join(session_dir,file)} -> {os.path.join(session_dir,files_runid1_renamed3[i])}")
				os.rename(os.path.join(session_dir,file),os.path.join(session_dir,files_runid1_renamed3[i]))

			files_runid2 = glob.glob(f"{session_dir}/*{run_id2}*")
			files_runid2_renamed = rename_run(files_runid2,"run-2")

			for i,file in enumerate(files_runid2):
				print(f"rename {os.path.join(session_dir,file)} -> {os.path.join(session_dir,files_runid2_renamed[i])}")

				os.rename(os.path.join(session_dir,file),os.path.join(session_dir,files_runid2_renamed[i]))
			
			files_runid3 = glob.glob(f"{session_dir}/*run-3*")
			files_runid3_renamed = rename_run(files_runid3,"run-1")

			for i,file in enumerate(files_runid3):
				print(f"rename {os.path.join(session_dir,file)} -> {os.path.join(session_dir,files_runid3_renamed[i])}")
				os.rename(os.path.join(session_dir,file),os.path.join(session_dir,files_runid3_renamed[i]))

		if time1 > time2: 

			if (run_id1 != "run-2") and (run_id2 != "run-1"):


				print(f"rename {run_id1} run-2")
				print(f"rename {run_id2} run-1")


				files_runid1 = glob.glob(f"{session_dir}/*{run_id1}*")
				files_runid1_renamed = rename_run(files_runid1,"run-3")

				for i,file in enumerate(files_runid1):
					os.rename(os.path.join(session_dir,file),os.path.join(session_dir,files_runid1_renamed[i]))

				files_runid2 = glob.glob(f"{session_dir}/*{run_id2}*")
				files_runid2_renamed = rename_run(files_runid2,"run-1")

				for i,file in enumerate(files_runid2):
	
					os.rename(os.path.join(session_dir,file),os.path.join(session_dir,files_runid2_renamed[i]))

				files_runid3 = glob.glob(f"{session_dir}/*run-3*")
				files_runid3_renamed = rename_run(files_runid3,"run-2")

				for i,file in enumerate(files_runid3):
					os.rename(os.path.join(session_dir,file),os.path.join(session_dir,files_runid3_renamed[i]))


######  RENAME RUN --> ACQ-T1RS/DIFU

if  change_run2acq:


	#### cas ou il y 2 T2

	T2_list_file = glob.glob(f"{rawdata_dir}/sub-*/ses-*/anat/*run*T2w*")

	list_session_dir = list(set([os.path.dirname(s) for s in T2_list_file]))

	print(list_session_dir)

	for session_dir in tqdm(list_session_dir):

		if len(glob.glob(f"{session_dir}/*run-1_part-phase_T2w.json")) != 0:
			T2_run1_path = glob.glob(f"{session_dir}/*run-1_part-phase_T2w.json")[0]
			time_T2_run1 = read_time(T2_run1_path)


		if len(glob.glob(f"{session_dir}/*run-2_part-phase_T2w.json")) != 0:
			T2_run2_path = glob.glob(f"{session_dir}/*run-2_part-phase_T2w.json")[0]
			time_T2_run2 = read_time(T2_run2_path)

		if len(glob.glob(f"{session_dir}/*T1w.json")) != 0:
			T1_path = glob.glob(f"{session_dir}/*T1w.json")[0]
			time_T1 = read_time(T1_path)


			if time_T1 == time_T2_run2:
				print("exception run2 = run - T1")

				print(session_dir)

				print(f" time run-1: {time_T2_run1} ")
				print(f" time run-2: {time_T2_run2} ")
				print(f" time T1: {time_T1} ")

### decommenter pour faire tourner

	T2_list_file = [file for file in T2_list_file if 'acq' not in file and 'run' in file]

	for file_path in T2_list_file:

		new_file_path = file_path.replace("run-1", "acq-T1Rs").replace("run-2", "acq-DiFu")
				   
		os.rename(file_path, new_file_path)
		print(f"Renamed: {file_path} -> {new_file_path}")


	T2_list_file = glob.glob(f"{rawdata_dir}/sub-*/ses-*/anat/*T2w*")
	T2_list_file = [file for file in T2_list_file if 'acq' not in file and 'run' not in file]

	list_session_dir = list(set([os.path.dirname(s) for s in T2_list_file]))

	print(list_session_dir)

	for session_dir in tqdm(list_session_dir):


		if len(glob.glob(f"{session_dir}/*part-phase_T2w.json")) != 0:
			T2_path = glob.glob(f"{session_dir}/*part-phase_T2w.json")[0]
			time_T2 = read_time(T2_path)


		if len(glob.glob(f"{session_dir}/*T1w.json")) != 0:
			T1_path = glob.glob(f"{session_dir}/*T1w.json")[0]
			time_T1 = read_time(T1_path)


			print("\n")
			print(f" time run-1: {time_T2} ")
			print(f" time T1: {time_T1} ")

			if time_T1 == time_T2:
				print("T2 time = T1 time")

				print(session_dir)
			else:
				print("T2 time != T1 time")

				### renommer T2 en T2-acq-DiFU

				print(session_dir)


	T2_list_file = glob.glob(f"{rawdata_dir}/sub-*/ses-*/anat/*T2w*")
	T2_list_file = [file for file in T2_list_file if 'acq' not in file and 'run' not in file]

	T2_acqT1RS = [file for file in T2_list_file if "207MAUSK" not in file and "postdiff" not in file]

	for filepath in T2_acqT1RS:

		filename = os.path.basename(filepath)
		anat_path = os.path.dirname(filepath)

		new_T2_filename = "_".join(filename.split("_")[:2]) + "_acq-T1Rs_" + "_".join(filename.split("_")[2:])


		os.rename(os.path.join(anat_path,filename),os.path.join(anat_path,new_T2_filename))

	T2_acqDiFu = list(set(T2_list_file) - set(T2_acqT1RS))

	for filepath in T2_acqDiFu:

		filename = os.path.basename(filepath)
		anat_path = os.path.dirname(filepath)

		new_T2_filename = "_".join(filename.split("_")[:2]) + "_acq-DiFu_" + "_".join(filename.split("_")[2:])

		print(new_T2_filename)


		os.rename(os.path.join(anat_path,filename), os.path.join(anat_path,new_T2_filename))



if comment_only_T1Rs:

	subject_list = [s for s in os.listdir(rawdata_dir) if "sub" in s]

	columns = ["subject_id", "session_id", "comment"]
	comments_df = pd.DataFrame(columns=columns)


	for sub in tqdm(subject_list):
		session_list = [s for s in os.listdir(os.path.join(rawdata_dir,sub)) if "ses" in s]

		for ses in session_list:

			files_in_dir = os.listdir(os.path.join(rawdata_dir,sub,ses,"anat"))

			# Filter files that match the specific acquisition patterns
			acq_DiFu_files = [f for f in files_in_dir if "acq-DiFu" in f]
			acq_T1Rs_files = [f for f in files_in_dir if "acq-T1Rs" in f]

			# Check if there is one type of file but not the other
			# if (acq_DiFu_files and not acq_T1Rs_files) or (acq_T1Rs_files and not acq_DiFu_files):
			# 	print(f"Subject: {sub}, Session: {ses} - Missing one acquisition type")

			
			if acq_DiFu_files and not acq_T1Rs_files:
				print(f"Subject: {sub}, Session: {ses} - Missing acq-T1Rs file")


			elif acq_T1Rs_files and not acq_DiFu_files:
				print(f"Subject: {sub}, Session: {ses} - Missing acq-DiFu file")

				comment = f"Missing acq-DiFu T2w file"
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


	comments_df.to_csv("/Volumes/BackupDisk/APEX/apex_enf/comments/comments_missing_acq_T2.csv", index=False)





def update_json_fields(json_data, field_mapping, delete_fields):
    if isinstance(json_data, dict):
        # Remove keys that are in the delete_fields list
        json_data = {k: v for k, v in json_data.items() if k not in delete_fields}
        
        # Replace keys as per field_mapping
        updated_json = {field_mapping.get(k, k): update_json_fields(v, field_mapping, delete_fields) for k, v in json_data.items()}


        return updated_json
    
    elif isinstance(json_data, list):
        return [update_json_fields(i, field_mapping, delete_fields) for i in json_data]
    
    else:
        return json_data


if change_field_json:

	dict_correct_field = {

	    "Examination date/time": "AcquisitionDateTime",
	    "Reconstruction nr": "ReconstructionNumber",
	    "Scan Duration [sec]": "ScanDuration" ,
	    "Max. number of cardiac phases": "NumberOfCardiacPhases",
	    "Max. number of echoes": "NumberOfEchoes" ,
	    "Max. number of slices/locations": "SliceLocation",
	    "Max. number of dynamics": "NumberOfTemporalPositions",
	    "Max. number of mixes": "NumberOfMixes",
	    "Preparation direction": "MRStackPreparationDirection",
	    "Technique": "SequenceName",
	    "Scan resolution  (x, y)": "ScanResolution",
	    "Scan mode": "MRAcquisitionType",
	    "FOV (ap,fh,rl) [mm]": "FOV",
	    "Water Fat shift [pixels]": "WaterFatShiftPixels",
	    "Angulation midslice(ap,fh,rl)[degr]": "WaterFatShift",
	    "Off Centre midslice(ap,fh,rl) [mm]": "OffCentreMidslice",
	    "Flow compensation <0=no 1=yes> ?": "FlowCompensation",
	    "Presaturation     <0=no 1=yes> ?": "Presaturation",
	    "Phase encoding velocity [cm/sec]": "PhaseEncodingVelocity",
	    "MTC               <0=no 1=yes> ?": "MTC",
	    "SPIR              <0=no 1=yes> ?": "SPIR",
	    "EPI factor        <0,1=no EPI>":  "EPIFactor",
	    "Dynamic scan      <0=no 1=yes> ?": "DynamicScan",
	    "Diffusion         <0=no 1=yes> ?": "Diffusion",
	    "Diffusion echo time [ms]": "DiffusionEchoTime",
	    "Max. number of diffusion values": "NumberOfDiffusionValues",
	    "Max. number of gradient orients": "NumberOfGradientOrients",
	    "Number of label types   <0=no ASL>": "LabelTypeASL"
	}


	list_delete_field = ["Patient name","Protocol name", "Acquisition nr", "Series Type","Patient position","Repetition time [ms]","PatientName","SeriesDescription","Filename","NiftiName"]

	json_file_list = glob.glob(f"{rawdata_dir}/sub-*/ses-*/*/*.json")

	for file_path in tqdm(json_file_list):
		# File path (same for input and output)
	#	file_path = "/Volumes/My Passport/rawdata/sub-101VALAL/ses-pre/func/sub-101VALAL_ses-pre_task-stop_bold.json"

		# Read the JSON file
		with open(file_path, 'r',encoding = "utf-8") as infile:
		    json_data = json.load(infile)

		# Update the JSON (both replacing keys and deleting unwanted fields)
		updated_json_data = update_json_fields(json_data, dict_correct_field, list_delete_field)

		if delete_date:

			if "AcquisitionDateTime" in updated_json_data:


				date_time = json_data["AcquisitionDateTime"] 

				if "/" in date_time:
					new_date_time = date_time.split("/")[1][1:]
				if ":" not in date_time:
					time_uncorrected = date_time[8:]
					new_date_time = time_uncorrected[:2] + ":" + time_uncorrected[2:4] + ":" + time_uncorrected[4:6]


				updated_json_data["AcquisitionDateTime"] = new_date_time

		# Save the updated JSON back to the same file
		with open(file_path, 'w') as outfile:
		    json.dump(updated_json_data, outfile, indent=4)


if generate_conversion_table:

	data_records = []

	patient_list = [s for s in os.listdir(os.path.join(source_data_dir)) if "sub" in s]

	for subject_id in tqdm(patient_list):
		session_list = [s for s in os.listdir(os.path.join(source_data_dir,subject_id)) if 'ses' in s]

		for session_id in session_list:

			files_path = os.path.join(source_data_dir,subject_id,session_id)
			print(files_path)
			source_par = glob.glob(f'{files_path}/*.PAR')
			print(source_par)

			if all("T1" not in s for s in source_par):
				have_T1_source = 0
				have_T1_raw = None
				conversion_error_T1 = None

			if all("T2" not in s for s in source_par):
				have_T2_source = 0
				have_T2_raw = None
				have_multiple_T2 = None
				conversion_error_T2 = None

			if all("rs-multi-echo" not in s for s in source_par):
				have_rs_source = 0
				have_rs_raw = None
				conversion_error_rs = None

			if all("dot" not in s for s in source_par):
				have_dot_source = 0
				have_dot_raw = None
				conversion_error_dot = None

			if all("stop" not in s for s in source_par):
				have_stop_source = 0
				have_stop_raw = None
				conversion_error_stop = None

			if all("DTI2-3" not in s for s in source_par):
				have_dwi_source = 0
				have_dwi_raw = None
				conversion_error_dwi = None

			if all("DTI2-3-alt-topup" not in s for s in source_par):
				have_dwiAP_source = 0
				have_dwiAP_raw = None
				conversion_error_dwiAP = None

			if all("B0MAP" not in s for s in source_par):
				have_b0_source = 0
				have_b0_raw = None
				conversion_error_b0 = None

			for file in source_par:
		
		## filtre avec 3DT1, T2; dot,stop,rs-multi-echo, DTI2-3-alt without toput, DTI2-3-alt-topup,B0MAP

				if "3DT1" in file:

					raw_file = os.path.join(rawdata_dir,subject_id,session_id,"anat",f"{subject_id}_{session_id}_T1w.nii.gz")

					if os.path.isfile(raw_file):
						have_T1_source = 1
						have_T1_raw = 1
						conversion_error_T1 = 0
					else:
						have_T1_source = 1
						have_T1_raw = 0
						conversion_error_T1 = 1

				if "T2" in file:

					raw_files = glob.glob(os.path.join(rawdata_dir,subject_id,session_id,"anat","*T2w*.nii.gz"))

					if len(raw_files) == 2:
						have_T2_source = 1
						have_T2_raw = 1
						have_multiple_T2 = 0
						conversion_error_T2 = 0
					elif len(raw_files) == 4:
						have_T2_source = 1
						have_T2_raw = 1
						have_multiple_T2 = 1	
						conversion_error_T2 = 0

					if len(raw_files) == 0:
						have_T2_source = 1
						have_T2_raw = 0
						have_multiple_T2 = 0
						conversion_error_T2 = 1

				if "dot" in file:

					raw_file = os.path.join(rawdata_dir,subject_id,session_id,"func",f"{subject_id}_{session_id}_task-dot_bold.nii.gz")

					if os.path.isfile(raw_file):
						have_dot_source = 1
						have_dot_raw = 1
						conversion_error_dot = 0
					else:
						have_dot_source = 1
						have_dot_raw = 0
						conversion_error_dot= 1

				if "stop" in file:

					raw_file = os.path.join(rawdata_dir,subject_id,session_id,"func",f"{subject_id}_{session_id}_task-sst_bold.nii.gz")

					if os.path.isfile(raw_file):
						have_stop_source = 1
						have_stop_raw = 1
						conversion_error_stop = 0
					else:
						have_stop_source = 1
						have_stop_raw = 0
						conversion_error_stop= 1


				if "rs-multi-echo" in file:

					raw_files = glob.glob(os.path.join(rawdata_dir,subject_id,session_id,"func",f"{subject_id}_{session_id}_task-rest*_bold.nii.gz"))

					if len(raw_files) == 3:

						have_rs_source = 1
						have_rs_raw = 1
						conversion_error_rs = 0
					else:
						have_rs_source = 1
						have_rs_raw = 0
						conversion_error_rs = 1


				if "DTI2-3" in file and not "topup" in file:

					raw_file = os.path.join(rawdata_dir,subject_id,session_id,"dwi",f"{subject_id}_{session_id}_acq-64dirs_dir-PA_dwi.nii.gz")

					if os.path.isfile(raw_file):
						have_dwi_source = 1
						have_dwi_raw = 1
						conversion_error_dwi = 0
					else:
						have_dwi_source = 1
						have_dwi_raw = 0
						conversion_error_dwi= 1

				if "DTI2-3-alt-topup" in file:

					raw_file = os.path.join(rawdata_dir,subject_id,session_id,"dwi",f"{subject_id}_{session_id}_acq-6dirs_dir-AP_dwi.nii.gz")

					if os.path.isfile(raw_file):
						have_dwiAP_source = 1
						have_dwiAP_raw = 1
						conversion_error_dwiAP = 0
					else:
						have_dwiAP_source = 1
						have_dwiAP_raw = 0
						conversion_error_dwiAP = 1

				

				if "B0MAP" in file:

					raw_files = glob.glob(os.path.join(rawdata_dir,subject_id,session_id,"fmap","*1.nii.gz"))

					if len(raw_files) == 2:
						have_b0_source = 1
						have_b0_raw = 1
						conversion_error_b0 = 0
					else:
						have_b0_source = 1
						have_b0_raw = 0
						conversion_error_b0 = 1

			record = {
				"subject_id": subject_id,
				"session_id": session_id,
				"have_T1_source": have_T1_source,
				"have_T1_raw": have_T1_raw,
				"conversion_error_T1": conversion_error_T1,
				"have_T2_source": have_T2_source,
				"have_T2_raw": have_T2_raw,
				"have_multiple_T2": have_multiple_T2,
				"conversion_error_T2": conversion_error_T2,
				"have_rs_source": have_rs_source,
				"have_rs_raw": have_rs_raw,
				"conversion_error_rs": conversion_error_rs,
				"have_dot_source": have_dot_source,
				"have_dot_raw": have_dot_raw,
				"conversion_error_dot": conversion_error_dot,
				"have_stop_source": have_stop_source,
				"have_stop_raw": have_stop_raw,
				"conversion_error_stop": conversion_error_stop,
				"have_dwi_source": have_dwi_source,
				"have_dwi_raw": have_dwi_raw,
				"conversion_error_dwi": conversion_error_dwi,
				"have_dwiAP_source": have_dwiAP_source,
				"have_dwiAP_raw": have_dwiAP_raw,
				"conversion_error_dwiAP": conversion_error_dwiAP,
				"have_b0_source": have_b0_source,
				"have_b0_raw": have_b0_raw,
				"conversion_error_b0": conversion_error_b0
			}

			data_records.append(record)

	df = pd.DataFrame(data_records)


	session_order = ["ses-pre", "ses-post", "ses-postdiff"]
	df["session_id"] = pd.Categorical(df["session_id"], categories=session_order, ordered=True)
	df_sorted = df.sort_values(by=["subject_id","session_id"])
	df_sorted.to_csv(f"{rawdata_dir}/check_conversion.csv")


if check_conversion:

	### On s'attend ici à retrouver VALMA resting state ici (error nb not divisible : erreur transfert) 

	conversion_table = pd.read_csv(f"{rawdata_dir}/check_conversion.csv")


	## load conversion table
	## check for each conversion_error
	fields = ["conversion_error_T1","conversion_error_T2","conversion_error_rs","conversion_error_dot","conversion_error_stop","conversion_error_dwi","conversion_error_dwiAP","conversion_error_b0"]

	for i,row in conversion_table.iterrows():

		subject_id = row["subject_id"]
		session_id = row["session_id"]

		for field in fields	:
			if row[field] == 1:
				field_suffix = field.split("_")[-1]

				print(f"Problem conversion : {field_suffix} - {subject_id} - {session_id}")









