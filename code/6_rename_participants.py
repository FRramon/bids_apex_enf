

import os
from tqdm import tqdm
import pandas as pd
import re
import glob
import json
from collections import defaultdict
from datetime import datetime
import shutil

source_data_dir = "/Volumes/BackupDisk/APEX/apex_enf/source_data"
rawdata_dir = "/Volumes/BackupDisk/APEX/apex_enf/rawdata"

rename_participants = True

## sub-\d+[A-Z]+

def rename_file(list_files,subject_id):

	## /VOlumes... /anat/sub_ses_run-1_T2 json/nii

	newfiles = []

	for files in list_files:

		rg = r"sub-\d+[A-Z]+"

		for match in re.findall(rg, files):
			files_2 = files.replace(match, subject_id)

		newfiles.append(files_2)

	return newfiles


# 5 derniers supprimer
# premier element après sub : defini le groupe
# les deux element après : defini le numéro

dict_group = {
	"1" : "ca1",
	"2" : "ci2",
	"3" : "mt3",
	"4" : "pc4",
	"5" : "prema5"
}

if rename_participants:

	if not os.path.isdir(f'{rawdata_dir}_original_ids'):

		os.rename(rawdata_dir,f'{rawdata_dir}_original_ids')
		shutil.copytree(f'{rawdata_dir}_original_ids',rawdata_dir)

	## faire des copies au fur et à mesure dans rawdata (créer les dossier va être long (création recursive?))

	subject_list = [s for s in os.listdir(rawdata_dir) if "sub" in s]
	group_id = [s[4] for s in subject_list]

	# Renaming subjects based on the rules
	renamed_subjects = []
	group_count = {key: 0 for key in dict_group.keys()}  # table conversion

	dict_name = {}

	for subject in subject_list:
		# Extract the group number and group name
		group_number = subject.split('-')[1][0]  # Get the first digit after "sub-"
		group_name = dict_group.get(group_number, "unknown")

		# Rename subject
		match = re.search(r'\d(\d{2})', subject)
		if match:
			increment_number =  match.group(1).zfill(3)
		renamed_subject = f"sub-enf{group_name}{increment_number}"
		renamed_subjects.append(renamed_subject)

		dict_name[subject] = renamed_subject

		print(f"rename {rawdata_dir}/{subject} : {rawdata_dir}/{renamed_subject}")

		os.rename(f"{rawdata_dir}/{subject}",f"{rawdata_dir}/{renamed_subject}")

	# Display the renamed subjects

	print(renamed_subjects)
	print(list(dict_name.keys()))


	conversion_table = pd.DataFrame(list(dict_name.items()), columns=["original", "renamed"])

	conversion_table.to_csv(f"{rawdata_dir}/equivalence_table_participants.csv",index = False)

	for subject_sourcename in list(dict_name.keys()):

		files2rename = glob.glob(f"{rawdata_dir}/{dict_name[subject_sourcename]}/*/*/*")	
		print(len(files2rename))
		renamed_files = rename_file(files2rename,dict_name[subject_sourcename])
		print(len(renamed_files))

		for i,file in enumerate(files2rename):
			print(f"rename {file} : {renamed_files[i]}")
			os.rename(file,renamed_files[i])


### add rename scans/participants.tsv


	#print(renamed_files)


## rename
## attention copie de rawdata, et l'ancien s'appelle rawdata_sourcename




