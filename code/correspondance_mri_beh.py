import os
import glob
import pandas as pd
from datetime import datetime, timedelta
import re
import json
from tqdm import tqdm

rawrawdata_dir= "/Volumes/CurrentDisk/APEX/apex_enf/rawdata_original_ids" ### IRM

subject_list_raw =[s for s in os.listdir(rawrawdata_dir) if "sub-" in s]

dict_group = {
	"1" : "ca1",
	"2" : "ci2",
	"3" : "mt3",
	"4" : "pc4",
	"5" : "prema5"
}
renamed_subjects = []
group_count = {key: 0 for key in dict_group.keys()}  # table conversion

dict_name = {}

for subject in subject_list_raw:
		# Extract the group number and group name
	group_number = subject.split('-')[1][0]  # Get the first digit after "sub-"
	group_name = dict_group.get(group_number, "unknown")

		# Rename subject
	match = re.search(r'\d(\d{2})', subject)
	if match:
		increment_number =  match.group(1).zfill(2)
	renamed_subject = f"sub-enf{group_name}{increment_number}"
	renamed_subjects.append(renamed_subject)

	dict_name[renamed_subject] = subject

print(dict_name)







rawdata_dir = "/Volumes/CurrentDisk/APEX/apex_enf/rawdata" ### IRM

rawdata_beh_dir = "/Volumes/BackupDisk/APEX/apex/apex_data/rawdata"


subject_list = [s for s in os.listdir(rawdata_dir) if "sub-enf" in s]
subject_list_beh = [s for s in os.listdir(rawdata_beh_dir) if "sub-enf" in s]

c = 0


unicity = True


# for sub in subject_list:
# 	session_list = [s for s in os.listdir(os.path.join(rawdata_dir,sub)) if "ses" in s]

# 	for ses in session_list:



# 		if not os.path.isdir(os.path.join(rawdata_beh_dir,sub,ses)):
# 			print(f"missing {sub}-{ses} in beh")


# 		else:

# 			tsv_filelist = glob.glob(os.path.join(rawdata_beh_dir,sub,ses,"beh","*.tsv"))
# 			tsv_file = max(tsv_filelist, key=os.path.getsize)


# 			df = pd.read_csv(tsv_file,sep= '\t')


# 			### chercher date IRM

# 			if df.shape[0] != 1:
# 				date_str = df["date"].iloc[0]
# 				date_beh = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")



# 				### chercher date IRM

# 				raw_subject_id = dict_name[sub]

# 				if len(glob.glob(os.path.join(rawrawdata_dir,raw_subject_id,ses,"anat","*_T1w.json"))) != 0:


# 					T1_file = glob.glob(os.path.join(rawrawdata_dir,raw_subject_id,ses,"anat","*_T1w.json"))[0]


# 					with open(T1_file, "r") as file:
# 						data = json.load(file)
# 					acquisition_datetime_str = data.get("AcquisitionDateTime", "")
# 					acquisition_datetime_str = acquisition_datetime_str.replace("/", "")
# 					acquisition_datetime = datetime.strptime(acquisition_datetime_str, "%Y.%m.%d %H:%M:%S")

# 					time_diff = acquisition_datetime - date_beh
					

# 					if abs(time_diff) > timedelta(days=10):
# 						print(f"time difference for {sub} - {ses} : {time_diff} ")


# 				else:
# 					print(f"{sub}-{ses} : no T1")



# 				## convertir le nom en raw
# 				## aller chercher dans rawdata_original_ids



# 			else:
# 				c +=1 


### check date unicity in beh

if unicity:
	for sub in tqdm(subject_list_beh):

		session_list = [s for s in os.listdir(os.path.join(rawdata_beh_dir,sub)) if "ses" in s and '.' not in s and not "training" in s]

		for ses in session_list:


			list_tsv = glob.glob(f"/Volumes/BackupDisk/APEX/apex/apex_data/rawdata/{sub}/{ses}/beh/*_beh.tsv")

			list_date = []

			for tsv_file in list_tsv:
				df = pd.read_csv(tsv_file,sep= '\t')


				### chercher date IRM

				if df.shape[0] > 1 and 'date' in df:
					date_str = df["date"].iloc[0][:10]
					date_beh = datetime.strptime(date_str, "%Y-%m-%d")

					list_date.append(date_beh)

			unique_dates = list(set(list_date))


			if len(unique_dates) != 1:
				print(f"{sub} - {ses} : multiple dates")
				print(unique_dates)








# for sub in subject_list_beh:
# 	session_list = [s for s in os.listdir(os.path.join(rawdata_beh_dir,sub)) if "ses" in s]

# 	for ses in session_list:



# 		if not os.path.isdir(os.path.join(rawdata_dir,sub,ses)):
# 			print(f"missing {sub}-{ses} in mri")
