#4-15BERMA

import os
import pandas as pd
import shutil
from tqdm import tqdm
import glob
import re
from collections import Counter

from datetime import datetime

source_data_dir = "/Volumes/My Passport/source_data"
raw_patient_dir = "/Volumes/My Passport/raw_patient_structure3"
raw_source_dir = "/Volumes/My Passport/sub-enf"

exclude_patient_list = [s for s in os.listdir(source_data_dir)] + ["AWELLI1V1S011","AWELLI1V1S108","CHAUFFEMACHINE","FCOSPDS15","TESTSTOPAS3","TESTSTOPAS4"]
patient_list_orig = [s for s in os.listdir(raw_patient_dir) if s not in exclude_patient_list]
patient_list_rename  = ["sub-" + ''.join(s.split('-')) for s in patient_list_orig]

patient_to_process = [s for s in patient_list_rename if s not in exclude_patient_list]




print(patient_list_orig)
print(patient_list_rename)
print(patient_to_process)


copysource = False
correct_name = False

get_unique_sequences = False

if copysource:


	for patient_name in tqdm(patient_to_process):

		patient_name = "2-03VALMA"

		if not os.path.isdir(os.path.join(source_data_dir,patient_name)):
			os.makedirs(os.path.join(source_data_dir,patient_name),exist_ok = True)

		session_list = [s for s in os.listdir(os.path.join(raw_patient_dir,patient_name)) if "ses" in s]

		for ses in session_list:

			session_dir = os.path.join(source_data_dir,patient_name,ses)

			if not os.path.isdir(session_dir):
				os.makedirs(session_dir,exist_ok = True)

			df_seq = pd.read_csv(os.path.join(raw_patient_dir,patient_name,ses,f"sequences_{patient_name}_{ses}.csv"))

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


			for item in unique_items:

				file2rename = [f for f in total_filepath_list if os.path.basename(f) == item]

				for file in file2rename:

					shutil.copy(file,session_dir)


			for item in non_unique_items:

				file2rename = [f for f in total_filepath_list if os.path.basename(f) == item]

				for i,f in enumerate(file2rename):

					if os.path.basename(f).split(".")[-1] == "PAR" or os.path.basename(f).split(".")[-1] == "REC" :

						if not os.path.basename(f)[0] == ".":

							newfilename = os.path.basename(f).split(".")[0] + f"_run-{i+1}." + os.path.basename(f).split(".")[1]

						elif len(os.path.basename(f))>2:


							newfilename = os.path.basename(f).split(".")[1] + f"_run-{i+1}." + os.path.basename(f).split(".")[2]

						shutil.copy(f,os.path.join(os.path.dirname(f),newfilename))



if correct_name:

	patient_to_correct = [s for s in os.listdir(source_data_dir) if not "sub" in s]

	corrected_names = ["sub-" + ''.join(s.split('-')) for s in patient_to_correct]

	for i,patient in enumerate(patient_to_correct):

		newfilename = corrected_names[i]

		print(f" Rename {patient} to {newfilename}")

		os.rename(os.path.join(source_data_dir,patient),os.path.join(source_data_dir,newfilename))



if get_unique_sequences:

	# On a renommé DUCLO et APEX027 à la main

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

add_run_label = True

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


	patient_name = "sub-138BLIRO"
	session_id = "ses-pre"

	patient_list = [s for s in os.listdir(os.path.join(source_data_dir)) if "sub" in s]

	for sub in patient_list:
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



		# print(f"{os.path.basename(file)} : {time}")















