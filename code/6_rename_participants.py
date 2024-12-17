

import os
from tqdm import tqdm
import pandas as pd
import re
import glob
import json
from collections import defaultdict
from datetime import datetime
import shutil

source_data_dir = "/Volumes/CurrentDisk/APEX/apex_enf/source_data"
rawdata_dir = "/Volumes/CurrentDisk/APEX/apex_enf/rawdata"


rename_participants = True
rename_tsv = True
rename_summary_file = True

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

def replace_ids_in_string(input_string, mapping):
	for original, renamed in mapping.items():
		input_string = input_string.replace(original, renamed)
	return input_string


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
			increment_number =  match.group(1).zfill(2)
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

if rename_tsv:





	### rename participants.tsv

	participants = pd.read_csv(f"{rawdata_dir}/participants.tsv",sep = '\t')
	equivalence_table = pd.read_csv(f"{rawdata_dir}/equivalence_table_participants.csv")# columns : original, renamed 
	mapping_dict = dict(zip(equivalence_table['original'], equivalence_table['renamed']))

	participants['participant_id'] = participants['participant_id'].map(mapping_dict)
	## save tsv

	participants.to_csv(f"{rawdata_dir}/participants.tsv",sep = '\t',index =False)

	### rename all sub-*_ses-*_scans.tsv

	scans_tsv_list = glob.glob(f"{rawdata_dir}/sub-*/ses-*/*scans.tsv")
	#print(scans_tsv_list)

	for file in scans_tsv_list:
		scan_df = pd.read_csv(file,sep = '\t')
		print(scan_df["filename"])

		scan_df['filename'] = scan_df['filename'].apply(lambda x: replace_ids_in_string(x, mapping_dict))

		print(scan_df)

		scan_df.to_csv(file, sep='\t', index=False)

		new_file_name = replace_ids_in_string(file, mapping_dict)

		os.rename(file, new_file_name)

if rename_summary_file:


	conversion_table = pd.read_csv(f"{rawdata_dir}/check_conversion.csv")
	equivalence_table = pd.read_csv(f"{rawdata_dir}/equivalence_table_participants.csv")  # columns: original, renamed
	mapping_dict = dict(zip(equivalence_table['original'], equivalence_table['renamed']))

	# conversion_table.drop(columns=['participant_id_bids'], inplace=True)

	conversion_table['subject_id_bids'] = conversion_table['subject_id'].map(mapping_dict)

	columns = conversion_table.columns.tolist()
	participant_index = columns.index('subject_id')
	columns.insert(participant_index + 1, columns.pop(columns.index('subject_id_bids')))
	conversion_table = conversion_table[columns]

	conversion_table.to_csv(f"{rawdata_dir}/check_conversion.csv", index=False)

		### float to int (plus tard)

	# exclude_columns = {'subject_id', 'subject_id_bids', 'session_id'}
	# for column in conversion_table.columns:
	# 	if column not in exclude_columns:
	# 		conversion_table[column] = conversion_table[column].apply(lambda x: int(x) if pd.notna(x) else None)


	# print(conversion_table)

	# conversion_table.to_csv(f"{rawdata_dir}/check_conversion.csv",index = False)
















### add rename scans/participants.tsv


	#print(renamed_files)


## rename
## attention copie de rawdata, et l'ancien s'appelle rawdata_sourcename




