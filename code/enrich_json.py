import os
from tqdm import tqdm
import pandas as pd
import re
import glob
import json

#########  BIDS CONVERSION

# After defining bidsmap.yaml in /rawdata/code/bidscoin/bidsmap.yaml
# from CLI in /My Passport :
# bidsmapper source_data rawdata


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



source_data_dir = "/Volumes/My Passport/source_data"
rawdata_dir = "/Volumes/My Passport/rawdata"

print(os.listdir(rawdata_dir))
bidscoiner_history = os.path.join(rawdata_dir,"code","bidscoin","bidscoiner.tsv")

df_bidcoiner_history = pd.read_csv(bidscoiner_history,sep = '\t')


print(df_bidcoiner_history.columns)


rename_target = True
if rename_target:
	df_list = []

	subject_list = [s for s in os.listdir(source_data_dir) if "sub" in s]

	for sub in subject_list:
		print(sub)
		session_list = [s for s in os.listdir(os.path.join(source_data_dir,sub)) if "ses" in s]

		for ses in session_list:

			session_path = os.path.join(source_data_dir,sub,ses)

			df_bidcoiner_history["patient_path"] = df_bidcoiner_history["source"].apply(lambda x: '/'.join(x.split('/')[:6]))


			sub_df_patient = df_bidcoiner_history[df_bidcoiner_history["patient_path"] == session_path]
			
			sub_df_patient = sub_df_patient.assign(targets_renamed=sub_df_patient["targets"])


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



	final_df.to_csv("/Volumes/My Passport/rawdata/sequences_info.csv")






sequences_info = pd.read_csv("/Volumes/My Passport/rawdata/sequences_info.csv")


for file,datatype,targets in tqdm(zip(sequences_info["source"],sequences_info["datatype"],sequences_info["targets_renamed"]),total = len(sequences_info)):


	if not "stop" in file and not "dot" in file:


		file_split = file.split('/')

		subject_id = file_split[4]
		session_id = file_split[5]

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




### DELETE  ####


# source_data_dir = "/Volumes/My Passport/rawdata"
# template_to_delete = ["sub-*/ses-*/anat/sub-*_ses-*_acq-T2GREph_rec-apex026_*_T2w*","sub-*/ses-*/anat/sub-*_ses-*_acq-T2GREph_rec-apex026_T2w*"]
# folder_to_delete = ["sub-*/ses-*/anat"]
# tsv = "sub-*/ses-*/sub-415BERMA_ses-pre_scans.tsv"


# tsv_list = glob.glob(os.path.join(source_data_dir,tsv))
# for tsv_file in tsv_list:
# 	df_tsv = pd.read_csv(tsv_file,sep = '\t')
# 	print(df_tsv)
# 	df_tsv = df_tsv[~df_tsv['filename'].str.contains("apex026", na=False)]
# 	df_tsv.to_csv(tsv_file)





# for template in folder_to_delete:
# 	files_to_delete = glob.glob(os.path.join(source_data_dir,template))
# 	print(files_to_delete)

	#for file in files_to_delete:

		# os.rmdir(os.path.join(source_data_dir,file))





