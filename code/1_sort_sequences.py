import os
from tqdm import tqdm
import pandas as pd
import re
import pydicom
import time
""" 1_sort_sequences.py

- Reads metadata from PAR/REC and DICOM files, extracting patient name, protocol, date, and time.
- Differentiates between RECPAR and DICOM file formats, handling errors and missing data gracefully.
- Builds DataFrames to organize and save extracted metadata into CSV files (scan_folders_recpar.csv, scan_folders_dicom.csv).
- Identifies and logs failed attempts to parse metadata for later review in a failure log (scan_folders_fail.csv).
- Supports testing for sequence nomenclature consistency and preliminary structure validation for subject/session organization.
"""

###########################################################
###														###
###				Read PAR file/ extract field			###
###														###
###########################################################


def split_date_time(date_output):
	date, time = date_output.split(" / ")
	return date,time

def read_par(filepath):

	patient_name = None
	protocol_name = None
	date_match = None

	try:

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

		if not patient_name or not protocol_name or not date or not time:
			raise ValueError("Missing required information (patient name, protocol, date, or time)")

		patient_info = {
			"patient_name": patient_name,
			"protocol": protocol_name,
			"date": date,
			"time": time
		}

		return patient_info

	except (FileNotFoundError, IsADirectoryError):
		return None
	except ValueError:
		return None
	except Exception :
		return None


def read_dcm(filepath):

	try: 
		dicom_data = pydicom.dcmread(filepath)

		patient_name = dicom_data.PatientName if 'PatientName' in dicom_data else 'Unknown'
		protocol = dicom_data.ProtocolName if 'ProtocolName' in dicom_data else 'Unknown'
		date = dicom_data.StudyDate if 'StudyDate' in dicom_data else 'Unknown'
		time = dicom_data.StudyTime if 'StudyTime' in dicom_data else 'Unknown'

		patient_info = {
			"patient_name": patient_name,
			"protocol": protocol,
			"date": date,
			"time": time
		}

		return patient_info

	except (pydicom.errors.InvalidDicomError, FileNotFoundError, IsADirectoryError) as e: 
		return None


# options
sortsequences = True
delete_change = True

## Variable list
source_dir = "/Volumes/BackupDisk/APEX/apex_enf/sub-enf"
docs_dir = "/Volumes/CurrentDisk/APEX/apex_enf/docs"


###########################################################
###														###
###				TEST 3	Check PAR/REC DICOM				###
###														###
###########################################################

if delete_change: ### Because we renamed un-1/run)2 PAR/REC files to copy in source data...
	list_source =os.listdir(source_dir)

	exclude_labels= ["DICOMDIR","DS_STORE","archive",'.']
	num_dicom = 0
	num_recpar = 0
	list_source = [ids for ids in list_source if not any(s in ids for s in exclude_labels)]

	print(list_source)

	files2delete = []

	for ids in tqdm(list_source):
		seq_folder = os.path.join(source_dir,ids)

		if len(os.listdir(seq_folder)) == 0:
			print("has no data")
		else:
			list_files = os.listdir(seq_folder)

			#filtered_list_files = [s for s in list_files if not s.startswith('.') and not s.startswith("_")]

			for file in list_files:

				file_path = os.path.join(seq_folder,file)

				ti_m = os.path.getmtime(file_path) ## extract last modification time
				m_ti = time.ctime(ti_m)

				year = m_ti.split()[-1]  # Extract the year 

				if year == "2024":

					os.remove(file_path)


if sortsequences:


	print("===================================================\n")
	print("==========         READ PAR/REC INFOS     =========\n")
	print("===================================================\n")



	if not os.path.isdir(docs_dir):
		os.mkdir(docs_dir)

	list_source =os.listdir(source_dir)

	exclude_labels= ["DICOMDIR","DS_STORE","archive",'.']
	num_dicom = 0
	num_recpar = 0
	list_source = [ids for ids in list_source if not any(s in ids for s in exclude_labels)]

	df_scan_recpar = pd.DataFrame(columns=['subject_id','session_id','folder_name','patient_name','protocol','date','time'])
	df_scan_dicom = pd.DataFrame(columns=['subject_id','session_id','folder_name','patient_name','protocol','date','time'])
	df_fail = pd.DataFrame(columns=['subject_id','session_id','folder_name'])


	for ids in tqdm(list_source):

		seq_folder = os.path.join(source_dir,ids)

		if  len(os.listdir(seq_folder)) == 0:
			print("has no data")
		else:
			list_files = os.listdir(seq_folder)

			filtered_list_files = [s for s in list_files if not s.startswith('.')]

			split_name = ids.split("_")

			subject_id = split_name[0]
			session_id = split_name[1]



			if len(filtered_list_files) == 2:
				num_recpar += 1

				# print(filtered_list_files)
				# print(ids)

				parfile_list = [f for f in filtered_list_files if 'PAR' in f]

				if len(parfile_list) == 0:

					dict_fail_line = {
						"subject_id": subject_id,
	    				"session_id": session_id,
	    				"folder_name": ids
	    			}

					df_fail_line = pd.DataFrame([dict_fail_line])
					df_fail = pd.concat([df_fail,df_fail_line],ignore_index = True)

				else:

					parfile = parfile_list[0]
					dict_info = read_par(os.path.join(seq_folder,parfile))

					if dict_info is not None:
				

						dict_recpar_line = {
			    			"subject_id": subject_id,
			    			"session_id": session_id,
			    			"folder_name": ids,
			    			"patient_name": dict_info['patient_name'],
			    			"protocol": dict_info['protocol'],
			    			"date": dict_info['date'],
			    			"time": dict_info['time'],
			    			"file_format" : "RECPAR"
						}

						df_recpar_line = pd.DataFrame([dict_recpar_line])


						df_scan_recpar = pd.concat([df_scan_recpar,df_recpar_line],ignore_index = True)

					else:

						dict_fail_line = {
							"subject_id": subject_id,
		    				"session_id": session_id,
		    				"folder_name": ids
		    			}

						df_fail_line = pd.DataFrame([dict_fail_line])
						df_fail = pd.concat([df_fail,df_fail_line],ignore_index = True)

			# elif  ### que des par et rec dans list_files :
			# 	## ce sont de par rec 
			# 	## mais deux fichiers PAR au moins
			# 	parfile_list = [f for f in filtered_list_files if 'PAR' in f]


			# 	for parfile in par_file_list:

			# 		dict_info = read_par(os.path.join(seq_folder,parfile))

			# 		if dict_info is not None:
				

			# 			dict_recpar_line = {
			#     			"subject_id": subject_id,
			#     			"session_id": session_id,
			#     			"folder_name": ids,
			#     			"patient_name": dict_info['patient_name'],
			#     			"protocol": dict_info['protocol'],
			#     			"date": dict_info['date'],
			#     			"time": dict_info['time'],
			#     			"file_format" : "RECPAR"
			# 			}

			# 			df_recpar_line = pd.DataFrame([dict_recpar_line])


			# 			df_scan_recpar = pd.concat([df_scan_recpar,df_recpar_line],ignore_index = True)

			# 		else:

			# 			dict_fail_line = {
			# 				"subject_id": subject_id,
		    # 				"session_id": session_id,
		    # 				"folder_name": ids
		    # 			}

			# 			df_fail_line = pd.DataFrame([dict_fail_line])
			# 			df_fail = pd.concat([df_fail,df_fail_line],ignore_index = True)


			else:
				num_dicom +=1

				# print(filtered_list_files)
				# print(ids)

				first_dcm = filtered_list_files[0]

				dict_info = read_dcm(os.path.join(seq_folder,first_dcm))

				if dict_info is not None:

					dict_dcm_line = {
	    				"subject_id": subject_id,
	    				"session_id": session_id,
	    				"folder_name": ids,
	    				"patient_name": dict_info['patient_name'],
	    				"protocol": dict_info['protocol'],
	    				"date": dict_info['date'],
	    				"time": dict_info['time'],
	    				"file_format" : "DICOM"
					}

					df_dcm_line = pd.DataFrame([dict_dcm_line])
					df_scan_dicom = pd.concat([df_scan_dicom,df_dcm_line],ignore_index = True)

				else:

					dict_fail_line = {
						"subject_id": subject_id,
	    				"session_id": session_id,
	    				"folder_name": ids
	    			}

					df_fail_line = pd.DataFrame([dict_fail_line])
					df_fail = pd.concat([df_fail,df_fail_line],ignore_index = True)

	df_scan_recpar.to_csv(f"{docs_dir}/scan_folders_recpar.csv")
	df_scan_dicom.to_csv(f"{docs_dir}/scan_folders_dicom.csv")
	df_fail.to_csv(f"{docs_dir}/scan_folders_fail.csv")

	print(num_dicom)
	print(num_recpar)





