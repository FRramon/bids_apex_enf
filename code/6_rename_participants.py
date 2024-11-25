

import os
from tqdm import tqdm
import pandas as pd
import re
import glob
import json
from collections import defaultdict
from datetime import datetime

source_data_dir = "/Volumes/My Passport/source_data"
rawdata_dir = "/Volumes/My Passport/rawdata_sourcename"

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
	"1" : "ca",
	"2" : "ci",
	"3" : "mt",
	"4" : "pc",
	"5" : "prema"
}

#sub-enfca001

subject_list = [s for s in os.listdir(rawdata_dir) if "sub" in s]

group_id = [s[4] for s in subject_list]


# Renaming subjects based on the rules
renamed_subjects = []
group_count = {key: 0 for key in dict_group.keys()}  # To keep track of numbering within each group

dict_name = {}

for subject in subject_list:
    # Extract the group number and group name
    group_number = subject.split('-')[1][0]  # Get the first digit after "sub-"
    group_name = dict_group.get(group_number, "unknown")
    
    # Get the incremented number from the remaining part of the subject ID (after the first 3 characters)
    group_count[group_number] += 1
    increment_number = str(group_count[group_number]).zfill(3)  # Ensure 3-digit format
    
    # Rename subject
    renamed_subject = f"sub-enf{group_name}{increment_number}"
    renamed_subjects.append(renamed_subject)

    dict_name[subject] = renamed_subject

# Display the renamed subjects
print(renamed_subjects)

for subject_sourcename in subject_list:

	files2rename = glob.glob(f"{rawdata_dir}/{subject_sourcename}/*/*/*")	
	print(len(files2rename))
	renamed_files = rename_file(files2rename,dict_name[subject_sourcename])
	print(len(renamed_files))

	#print(renamed_files)


## rename
## attention copie de rawdata, et l'ancien s'appelle rawdata_sourcename




