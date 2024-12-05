import os
import pandas as pd
import shutil
from tqdm import tqdm
import glob
import re
from collections import Counter
import subprocess
from datetime import datetime

""" 3_copysource_data.py

- Processes patient data by managing directories, renaming IDs, and copying relevant files with unique labels.
- Analyzes unique and non-unique file sequences, handling conflicts with incremental run labeling.
- Extracts metadata from .PAR files, such as patient name, protocol, and examination date/time.
- Prepares data for BIDS conversion by executing BIDScoin and managing associated configuration files.
- Modular functionality includes copying, renaming, sequence extraction, and run labeling for reproducible workflows.
"""


code_dir = "/Users/francoisramon/Desktop/These/APEX/apex_enf/code"
base_dir =  "/Volumes/BackupDisk/APEX/apex_enf"
source_data_dir = "/Volumes/BackupDisk/APEX/apex_enf/source_data"
raw_patient_dir = "/Volumes/BackupDisk/APEX/apex_enf/raw_structure"
raw_source_dir = "/Volumes/BackupDisk/APEX/apex_enf/sub-enf"

if not os.path.isdir(source_data_dir):
	os.mkdir(source_data_dir)


exclude_patient_list = [s for s in os.listdir(source_data_dir)] + ["AWELLI1V1S011","AWELLI1V1S108","CHAUFFEMACHINE","FCOSPDS15","TESTSTOPAS3","TESTSTOPAS4"]
patient_list_orig = [s for s in os.listdir(raw_patient_dir) if s not in exclude_patient_list]
patient_list_rename  = ["sub-" + ''.join(s.split('-')) for s in patient_list_orig]

patient_to_process = [s for s in patient_list_orig if s not in exclude_patient_list]

print(patient_list_orig)

print(patient_list_orig)
print(patient_list_rename)
print(patient_to_process)

copysource = False
correct_name = False	
get_unique_sequences = False
add_run_label = True
run_bidscoin = True

#patient_to_process = ["2-04HEBTO"]

if copysource:

	print("===================================================")
	print("==========        COPY IN SOURCE DATA     =========")
	print("===================================================\n")
	print(patient_to_process)

	#patient_to_process = ["2-03VALMA"]

	for patient_name in tqdm(patient_to_process):


		

		print(patient_name)

		#patient_name = "2-03VALMA"
		#print(patient_name)

		if not os.path.isdir(os.path.join(source_data_dir,patient_name)):
			os.makedirs(os.path.join(source_data_dir,patient_name),exist_ok = True)

		session_list = [s for s in os.listdir(os.path.join(raw_patient_dir,patient_name)) if "ses" in s]

		#session_list = ["ses-postdiff"]

		for ses in session_list:

			if patient_name == "2-04HEBTO" and ses == "ses-postdiff": #### special case 
				print("special copy")

				session_dir = os.path.join(source_data_dir,patient_name,ses)

				if not os.path.isdir(session_dir):
					os.makedirs(session_dir,exist_ok = True)

					### 3DT1 : sub-enfci204_ses-postdiff_mri-1474291553-2-04HEBTO-3DT1-3-1	-- > 3DT1-3-1
					for file in glob.glob(os.path.join(raw_source_dir,"sub-enfci204_ses-postdiff_mri-1474291553-2-04HEBTO-3DT1-3-1/*")):
						shutil.copy(file,session_dir)

					### T2* : sub-enfci204_ses-postdiff_mri-1474291553-2-04HEBTO-T2GREph-SENSE-4-1	--> T2-4-1

					for file in  glob.glob(os.path.join(raw_source_dir,"sub-enfci204_ses-postdiff_mri-1474291553-2-04HEBTO-T2GREph-SENSE-4-1/*")):
						shutil.copy(file,session_dir)

					### rs : sub-enfci204_ses-postdiff_mri-1474291553-2-04HEBTO-rs-multi-echo-SENSE-5-1	--> rs-5-1

					for file in glob.glob(os.path.join(raw_source_dir,"sub-enfci204_ses-postdiff_mri-1474291553-2-04HEBTO-rs-multi-echo-SENSE-5-1/*")):
						shutil.copy(file,session_dir)

					### stop : sub-enfci204_ses-postdiff_mri-1473862350-DBIEX-6-1-stop-SENSE	-- stop-6-1
					
					for file in glob.glob(os.path.join(raw_source_dir,"sub-enfci204_ses-postdiff_mri-1473862350-DBIEX-6-1-stop-SENSE/*")):
						if os.path.basename(file)[-3:] == "PAR":
							newfilename = "2-04HEBTO-stop-SENSE-6-1.PAR"
							shutil.copy(file,os.path.join(session_dir,newfilename))

						if os.path.basename(file)[-3:] == "REC":
							newfilename = "2-04HEBTO-stop-SENSE-6-1.REC"
							shutil.copy(file,os.path.join(session_dir,newfilename))

						# shutil.copy(file,session_dir)

					### b0 : sub-enfci204_ses-postdiff_mri-1473862350-DBIEX-7-1-WIP-B0MAP	--> b0-7-1

					for file in glob.glob(os.path.join(raw_source_dir,"sub-enfci204_ses-postdiff_mri-1473862350-DBIEX-7-1-WIP-B0MAP/*")):
						if os.path.basename(file)[-3:] == "PAR":
							newfilename = "2-04HEBTO-WIP-B0MAP-7-1.PAR"
							shutil.copy(file,os.path.join(session_dir,newfilename))

						if os.path.basename(file)[-3:] == "REC":
							newfilename = "2-04HEBTO-WIP-B0MAP-7-1.REC"
							shutil.copy(file,os.path.join(session_dir,newfilename))

					### dwi : sub-enfci204_ses-postdiff_mri-1473862350-DBIEX-8-1-WIP-DTI2-3-SENSE	--> dwi 8-1

					for file in glob.glob(os.path.join(raw_source_dir,"sub-enfci204_ses-postdiff_mri-1473862350-DBIEX-8-1-WIP-DTI2-3-SENSE/*")):
						if os.path.basename(file)[-3:] == "PAR":
							newfilename = "2-04HEBTO-WIP-DTI2-3-SENSE-8-1.PAR"
							shutil.copy(file,os.path.join(session_dir,newfilename))

						if os.path.basename(file)[-3:] == "REC":
							newfilename = "2-04HEBTO-WIP-DTI2-3-SENSE-8-1.REC"
							shutil.copy(file,os.path.join(session_dir,newfilename))
					### T2* : sub-enfci204_ses-postdiff_mri-1473862350-DBIEX-3-1-T2GREph-SENSE	--> T2-9-1

					for file in glob.glob(os.path.join(raw_source_dir,"sub-enfci204_ses-postdiff_mri-1473862350-DBIEX-3-1-T2GREph-SENSE/*")):
						if os.path.basename(file)[-3:] == "PAR":
							newfilename = "2-04HEBTO-T2GREph-SENSE-9-1.PAR"
							shutil.copy(file,os.path.join(session_dir,newfilename))

						if os.path.basename(file)[-3:] == "REC":
							newfilename = "2-04HEBTO-T2GREph-SENSE-9-1.REC"
							shutil.copy(file,os.path.join(session_dir,newfilename))

				if os.path.isdir(os.path.join(source_data_dir,"sub-204HEBTO")):

					shutil.copytree(session_dir,os.path.join(source_data_dir,"sub-204HEBTO","ses-postdiff"))
					shutil.rmtree(os.path.dirname(session_dir))

				### copy dbiex-4-1 in dot dot-SENSE-4-1
				### copy dbiex-5-1 in rs (pb slice) rs-multi-echo-SENSE-5-1
				## copy dbiex-6-1 in stop stop-SENSE-6-1
				## copy dbiex-7-1 in b0 WIP-B0MAP-7-1
				## copy dbiex-81 in dwi WIP-DTI2-3-SENSE-8-1

			else:

				session_dir = os.path.join(source_data_dir,patient_name,ses)

				if not os.path.isdir(session_dir):
					os.makedirs(session_dir,exist_ok = True)

				df_seq = pd.read_csv(os.path.join(raw_patient_dir,patient_name,ses,f"sequences_{patient_name}_{ses}.csv"))

				# print(df_seq)

				folder_list = df_seq["folder_name"].to_list()

				total_file_list = []
				total_filepath_list = []

				for folder in folder_list:

					file_list = os.listdir(os.path.join(raw_source_dir,folder))


					for file in file_list:
						total_file_list.append(file)
						total_filepath_list.append(os.path.join(raw_source_dir,folder,file))

				element_counts = Counter(total_file_list)

				non_unique_items = [item for item, count in element_counts.items() if count > 1]
				unique_items = [item for item, count in element_counts.items() if count == 1]
				count_non_unique_items = [count for item, count in element_counts.items() if count > 1]
				print("non unique")
				print(non_unique_items)
				print("unique")
				print(unique_items)

				### check size of files, if equal, just copy the first file (duplicate)
				### else : print(not duplicate)



				for item in unique_items:

					file2rename = [f for f in total_filepath_list if os.path.basename(f) == item  and "DBIEX" not in f] # and "DBIEX not in f"

					for file in file2rename:

						shutil.copy(file,session_dir)

				for item in non_unique_items:
					file2rename = [f for f in total_filepath_list if os.path.basename(f) == item if ".REC" in f]

					# if len(file2rename) == 0:
					# 	print(file2rename)

					if len(file2rename) == 2:

						print(file2rename)

						sizefiles = [os.path.getsize(f) for f in file2rename]
					# #print(len(sizefiles))

					# if len(sizefiles) == 0:
					# 	print(file2rename)

						if sizefiles[0] == sizefiles[1]:
							print("same size")  #### tranfert 2 fois, on en prend un des 2

							shutil.copy(file2rename[0],session_dir)

						else:  ### erreur transfert, on copie le + "lourd"

							imax = sizefiles.index(max(sizefiles))
							shutil.copy(file2rename[imax],session_dir)

					file2rename = [f for f in total_filepath_list if os.path.basename(f) == item if ".PAR" in f]

					# if len(file2rename) == 0:
					# 	print(file2rename)

					if len(file2rename) == 2:

						print(file2rename)

						sizefiles = [os.path.getsize(f) for f in file2rename]
					# #print(len(sizefiles))

					# if len(sizefiles) == 0:
					# 	print(file2rename)

						if sizefiles[0] == sizefiles[1]:
							print("same size")  #### tranfert 2 fois, on en prend un des 2

							shutil.copy(file2rename[0],session_dir)

						else:  ### erreur transfert, on copie le + "lourd"

							imax = sizefiles.index(max(sizefiles))
							shutil.copy(file2rename[imax],session_dir)

				# print(sizefiles)


				## extract les REC
				# calcul taille des rec. Si egale print( duplicate)

				#Sinon print not duplicate




			# for item in non_unique_items:

			# 	file2rename = [f for f in total_filepath_list if os.path.basename(f) == item]

			# 	for i,f in enumerate(file2rename):

			# 		if os.path.basename(f).split(".")[-1] == "PAR" or os.path.basename(f).split(".")[-1] == "REC" :

			# 			if not os.path.basename(f)[0] == ".":

			# 				newfilename = os.path.basename(f).split(".")[0] + f"_run-{i+1}." + os.path.basename(f).split(".")[1]

			# 			elif len(os.path.basename(f))>2:


			# 				newfilename = os.path.basename(f).split(".")[1] + f"_run-{i+1}." + os.path.basename(f).split(".")[2]

			# 			shutil.copy(f,os.path.join(os.path.dirname(f),newfilename))

if correct_name:

	print("===================================================")
	print("==========        RENAME SUBJECT IDS      =========")
	print("===================================================\n")

	patient_to_correct = [s for s in os.listdir(source_data_dir) if not "sub" in s]

	corrected_names = ["sub-" + ''.join(s.split('-')) for s in patient_to_correct]

	for i,patient in enumerate(patient_to_correct):

		newfilename = corrected_names[i]

		print(f" Rename {patient} to {newfilename}")

		os.rename(os.path.join(source_data_dir,patient),os.path.join(source_data_dir,newfilename))

if get_unique_sequences:

	### This is used to define bidsmap.yaml

	# On a renommé DUCLO et APEX027 à la main ### Attention ++++

	subject_list = [s for s in os.listdir(source_data_dir) if "sub" in s]

	files = glob.glob(source_data_dir + "/sub-*/ses-*/*.PAR")

	filtered_files = ['-'.join(os.path.basename(f).split('-')[2:]) for f in files]
	unique_files = list(set(filtered_files))

	file_list = []

	for file in unique_files:

		split_under = file.split("-")

		if "run" in split_under[-2]:

			split_under[-3] = "*"

			newfilename = '-'.join(split_under)

		else:
			split_under[-2] = "*"

			newfilename = '-'.join(split_under)

		file_list.append(newfilename)


	print(list(set(file_list)))


def split_date_time(date_output):
	date, time = date_output.split(" / ")
	return date,time

def read_par(filepath):

	patient_name = None
	protocol_name = None
	date_match = None



	with open(filepath, 'r') as file:
		for line in file:
			patient_match = re.search(r'Patient name\s*:\s*(.+)', line)
			protocol_match = re.search(r'Protocol name\s*:\s*(.+)', line)
			date_match = re.search(r'Examination date/time\s*:\s*(.+)', line)

			if patient_match:
				patient_name = patient_match.group(1).strip()
			if protocol_match:
				protocol_name = protocol_match.group(1).strip()
			if date_match:
				date_name = date_match.group(1).strip()
				date,time = split_date_time(date_name)


	return time


if add_run_label:


	patient_list = [s for s in os.listdir(os.path.join(source_data_dir)) if "sub" in s]

	for sub in tqdm(patient_list):
		session_list = [s for s in os.listdir(os.path.join(source_data_dir,sub)) if 'ses' in s]

		for ses in session_list:



			files_path = os.path.join(source_data_dir,sub,ses)

			file_list =os.listdir(files_path)

			T2_template = ['*T2GREph-*-1.PAR','*T2GREph-SENSE-*-1.PAR']


			T2_list1 = glob.glob(os.path.join(files_path,T2_template[0]))
			T2_list2 = glob.glob(os.path.join(files_path,T2_template[1]))

			T2_list = T2_list1 + T2_list2

			series_order_list = []
			time_list = []

			if len(T2_list) >= 2:

				for file in T2_list:

					time = read_par(file)
					time_list.append(time)

					filename = os.path.basename(file)
					series_order = filename[:-4][-3]
					series_order_list.append(series_order)

				series_order_bool = (series_order_list[0] < series_order_list[1])

				time_format = "%H:%M:%S"
			    
				# Convert strings to datetime objects
				t0 = datetime.strptime(time_list[0], time_format)
				t1 = datetime.strptime(time_list[1], time_format)

				time_order_bool = (t0<t1)
				time_order_equal = t0 == t1

				if time_order_equal:
					print("time points are equal")

				else:

					right_order_runs = (series_order_bool == time_order_bool)

					if right_order_runs:
						print(sub)
						print(ses)



						print(f" Right order runs : {right_order_runs}")


if run_bidscoin:

	# create rawdata dir
	rawdata_dir = os.path.join(base_dir,"rawdata")
	if not os.path.isdir(rawdata_dir):
		os.mkdir(rawdata_dir)

	# create code section and place bidsmaps.yaml

	if not os.path.isdir(os.path.join(rawdata_dir,"code")):
		os.mkdir(os.path.join(rawdata_dir,"code"))

	if not os.path.isdir(os.path.join(rawdata_dir,"code","bidscoin")):
		os.mkdir(os.path.join(rawdata_dir,"code","bidscoin"))

	# copy bidsmap.yaml
	shutil.copy(os.path.join(code_dir,"bidsmap.yaml"),os.path.join(rawdata_dir,"code","bidscoin","bidsmap.yaml"))

	# execute bidscoiner
	command_bidscoin = f"bidscoiner {source_data_dir} {rawdata_dir}"
	print(command_bidscoin)
	subprocess.run(command_bidscoin,shell = True)






