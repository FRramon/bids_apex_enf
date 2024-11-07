import os
from tqdm import tqdm
import pandas as pd
import re
import glob
import json




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






subject_list = [s for s in os.listdir(source_data_dir) if "sub" in s]

for sub in subject_list:
	session_list = [s for s in os.listdir(os.path.join(source_data_dir,sub)) if "ses" in s]

	for ses in session_list:

		session_path = os.path.join(source_data_dir,sub,ses)

		df_bidcoiner_history["patient_path"] = df_bidcoiner_history["source"].apply(lambda x: '/'.join(x.split('/')[:6]))

		
		sub_df_patient = df_bidcoiner_history[df_bidcoiner_history["patient_path"] == session_path]


		print(sub_df_patient)









for file,datatype,targets in tqdm(zip(df_bidcoiner_history["source"],df_bidcoiner_history["datatype"],df_bidcoiner_history["targets"])):


	if not "stop" in file and not "dot" in file:


		file_split = file.split('/')

		subject_id = file_split[4]
		session_id = file_split[5]

		json_enrichment = read_par_T1(file)

		target_list = targets.split(',')

		for target_elements in target_list:


			target_json_file = os.path.join(rawdata_dir,subject_id,session_id,datatype,f"{target_elements[:-7]}.json")

			# with open(target_json_file, 'r') as file:
			# 	data = json.load(file)

			# if isinstance(data, list):
			# 	data.append(json_enrichment)
			# elif isinstance(data, dict):
			# 	data.update(json_enrichment)

			# # Step 3: Save the updated data back to the JSON file
			# with open(target_json_file, 'w') as file:
			# 	json.dump(data, file, indent=4)




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





