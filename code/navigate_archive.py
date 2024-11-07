import os
from tqdm import tqdm
import pandas as pd
import re
import pydicom

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


# source_dir = "/Volumes/My Passport/sub-enf"

# list_source =os.listdir(source_dir)
# exclude_labels= ["DICOMDIR","DS_STORE","archive",'.']
# list_source = [ids for ids in list_source if not any(s in ids for s in exclude_labels)]


# sub_rdm = list_source[0]
# file_list = os.listdir(os.path.join(source_dir,sub_rdm))
# first_dcm = file_list[0]


# Load the DICOM file


# return {
# 	'patient_name': str(patient_name),
# 	'protocol_name': str(protocol_name),
# 	'study_date': str(study_date),
# 	'study_time': str(study_time)
# 	}
# parfile = [f for f in file_list if 'PAR' in f][0]

# read_par(os.path.join(source_dir,sub_rdm,parfile))

## read par file


###########################################################
###														###
###					TEST 1	Check archives				###
###														###
###########################################################

test1 = False
if test1 : 
	archive_dir = "/Volumes/My Passport/sub-enf/archives"
	list_archives =os.listdir(archive_dir)
	num_export = 0
	num_dicom = 0
	for folder in list_archives:
		if "1_CA" in folder:
			export = [s.lower() for s in os.listdir(os.path.join(archive_dir,folder))]
			if "export" in export:

				num_export +=1
				export_dir = os.path.join(archive_dir,folder,"Export")
				print(os.listdir(export_dir)[0].split("_")[:2])

			else:
				dicom_dir = os.path.join(archive_dir,folder,"Dicom")
				if len(os.listdir(dicom_dir)) != 0:
					num_dicom +=1

	print(f" num export : {num_export}")
	print(f" num dicom : {num_dicom}")

#### Conclusion : Que 40 archives PAR REC. ET 17 DICOM : MAis pas d'idée de ses pre/post, il doit manquer des données

###########################################################
###														###
###					TEST 2	Check sub-enf				###
###														###
###########################################################

test2 = False
if test2:
	source_dir = "/Volumes/My Passport/sub-enf"
	list_source =os.listdir(source_dir)

	num_seq = 0

	subject_list_all = []
	session_list_all = []
	exclude_labels= ["DICOMDIR","DS_STORE","archive",'.']

	list_source = [ids for ids in list_source if not any(s in ids for s in exclude_labels)]
	for ids in tqdm(list_source):


		nomenclature = len(ids.split("_"))
		if nomenclature != 3:
			print("not the same nomenclature")
		else:
			num_seq += 1

			split_name = ids.split("_")

			subject_id = split_name[0]
			session_id = split_name[1]

			subject_list_all.append(subject_id)
			session_list_all.append(session_id)

	subject_list = list(set(subject_list_all))
	nb_subjects = len(subject_list)

	session_list = list(set(session_list_all))
	nb_sessions= len(session_list)

	print(f"nb seq : {num_seq}")
	print(f"unique subjects : {nb_subjects}")
	print(f"unique sessions : {nb_sessions}")
	print(f"sessions : {session_list}")



###########################################################
###														###
###				TEST 3	Check PAR/REC DICOM				###
###														###
###########################################################

test3 = False
if test3:
	source_dir = "/Volumes/My Passport/sub-enf"
	source_raw_dir = "/Volumes/My Passport/raw_organized"
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

				print(filtered_list_files)
				print(ids)

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

			else:
				num_dicom +=1

				print(filtered_list_files)
				print(ids)

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

	df_scan_recpar.to_csv("/Volumes/My Passport/francois/scan_folders_recpar.csv")
	df_scan_dicom.to_csv("/Volumes/My Passport/francois/scan_folders_dicom.csv")
	df_fail.to_csv("/Volumes/My Passport/francois/scan_folders_fail.csv")

	print(num_dicom)
	print(num_recpar)

#877
#2575

#perc_recpar = (nb_recpar/len(list_source))*100

###########################################################
###														###
###				TEST 4	Create Structure				###
###														###
###########################################################

test4 = False
if test4: 

	source_dir = "/Volumes/My Passport/sub-enf"
	source_raw_dir = "/Volumes/My Passport/raw_organized"
	print(session_list)

	


	for subject_id in tqdm(subject_list):

		#os.makedirs(os.path.join(source_raw_dir,subject_id),exist_ok = True)

		list_source = os.listdir(source_dir)

		for ses in session_list:

			substring = f"{subject_id}_{ses}"
			print(substring)
			exists = any(substring in file for file in list_source)
			print(exists)

			#if exists:
				#os.makedirs(os.path.join(source_raw_dir,subject_id,ses),exist_ok = True)



###########################################################
###														###
###				TEST 5	First checks on csv				###
###														###
###########################################################


test5 = False
if test5:
	scan_folder = pd.read_csv("/Volumes/My Passport/francois/scan_folders_recpar.csv")

	results = {}
	grouped = scan_folder.groupby('subject_id')

	for subject_id, group in grouped:
	    patient_names = group['patient_name'].tolist()  # Get unique patient names
	    dates = group['date'].tolist()  # Get all dates
	    
	    # Store results
	    results[subject_id] = {
	        'patient_names': patient_names,
	        'dates': dates
	    }

	    print(results)




