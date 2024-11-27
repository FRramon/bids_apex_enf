import os
import pandas as pd
from tqdm import tqdm
from collections import defaultdict
import re
import glob 
import datetime


""" 2_create_raw_structure.py

- Merges and processes DICOM and RECPAR CSV data to build a hierarchical raw data structure.
- Identifies and resolves naming inconsistencies while grouping sequences by corrected patient IDs.
- Organizes data into session-specific folders based on examination dates and generates associated metadata.
- Renames and standardizes session folders for longitudinal analysis (e.g., pre/post/post-diff sessions).
- Summarizes the data structure in a CSV report, tracking available sequences (T1, T2) and session types.
"""

checkdoubles = False
correctNames = True
getSequences_persubject = True
createSes = True
rename_session = True
createSes_seq = True
createSummary = True

docs_dir = "/Volumes/BackupDisk/APEX/apex_enf/docs"
raw_structure_dir = "/Volumes/BackupDisk/APEX/apex_enf/raw_structure"



df_recpar = pd.read_csv(os.path.join(docs_dir,"/scan_folders_recpar.csv"))
df  = df_recpar
df["concat_apex_id"] = df["subject_id"] + "_" + df["patient_name"]

### Create structure  ###


subject_ids = df["concat_apex_id"].to_list()
unique_subject_ids = list(set(subject_ids))


def filter_by_subject_id(df, subject_id):
    return df[df['concat_apex_id'] == subject_id]


if checkdoubles:

	unique_subject_ids = list(set(df["subject_id"].to_list()))
	unique_patient_names = list(set(df["patient_name"].to_list()))

	subject1_to_subject2 = defaultdict(set)
	subject2_to_subject1 = defaultdict(set)

	for folder_name in os.listdir(raw_structure_dir):
	    if "_" in folder_name:
	        subject_id1, subject_id2 = folder_name.split("_", 1)

	        
	        subject1_to_subject2[subject_id1].add(subject_id2)
	        subject2_to_subject1[subject_id2].add(subject_id1)

	subject1_issue = any(len(ids) > 1 for ids in subject1_to_subject2.values())
	subject2_issue = any(len(ids) > 1 for ids in subject2_to_subject1.values())

	subject1_issue = False
	print("Subject ID1 with multiple Subject ID2 associations:")
	for subject_id1, ids in subject1_to_subject2.items():
	    if len(ids) > 1:
	        subject1_issue = True
	        print(f"{subject_id1}: {', '.join(ids)}")

	if not subject1_issue:
	    print("None")

	subject2_issue = False
	print("\nSubject ID2 with multiple Subject ID1 associations:")
	for subject_id2, ids in subject2_to_subject1.items():
	    if len(ids) > 1:
	        subject2_issue = True
	        print(f"{subject_id2}: {', '.join(ids)}")

	if not subject2_issue:
	    print("None")

	if subject1_issue or subject2_issue:
	    print("\nThere are issues with the associations. Please see the details above.")
	else:
	    print("\nEach subject_id1 is associated with exactly one subject_id2, and vice versa.")


################################################

## Correction des mauvais noms  #####

## supprimer les espaces. mettre les lettres entre parenthese.remplacer les _ par des -, remplacer les . par des -

unique_patient_names = list(set(df["patient_name"].to_list()))
if correctNames: 
#if not os.path.isfile("/Volumes/My Passport/francois/names_corrected.csv"):

	unique_patient_names = [s for s in unique_patient_names if s not in ["1.06gcema","1-43HIUEMA","2-010CHAPA","apex027"]]
	processed_names = [name.replace(" ", "").replace("_", "-").replace(".","-").upper() for name in unique_patient_names]


	correct_names = {
	    "patient_name": unique_patient_names,
	    "processed_name": processed_names
	}


	manual_correction =  {
	    "patient_name": ["1.06gcema","1-43HIUEMA","2-010CHAPA","apex027"],
	    "processed_name": ["1-06GUEMA","1-43HUEMA","2-10CHAPA","2-09MORJU"]
	}


	df_correct_names = pd.DataFrame(correct_names)
	df_manual_correction = pd.DataFrame(manual_correction)

	df_correct_names = pd.concat([df_correct_names,df_manual_correction])
	df_correct_names.to_csv("/Volumes/BackupDisk/APEX/apex_enf/docs/names_corrected.csv")


#### Cette structure montre qu'il y a des mélanges de nom.
## ex 02-2-FERMA est associé à enfci202 et enfpc402

### Creation structure à partir des noms originaux
### prendrer que les par rec car apparemment les dicoms sont corrompus + sont surement juste des doublons


#raw_structure_dir = "/Volumes/My Passport/raw_patient_structure3"
def filter_by_patient_name(df, subject_id):
    return df[df['patient_name'] == subject_id]

#unique_patient_names = list(set(df["patient_name"].to_list()))

df_correct_names = pd.read_csv("/Volumes/BackupDisk/APEX/apex_enf/docs/names_corrected.csv")
unique_corrected_names = list(set(df_correct_names["processed_name"].to_list()))
print(len(unique_corrected_names))	
if getSequences_persubject:

	print("===================================================")
	print("==========     GET SEQUENCES / SUBJECT    =========")
	print("===================================================\n")

	for ids in tqdm(unique_corrected_names):



		associated_name = df_correct_names[df_correct_names['processed_name'] == ids]["patient_name"].to_list()
		print(associated_name)


		pattern = r"^\d-\d{2}[A-Za-z]{5}$"

		if re.match(pattern,ids):

			print("found")

			print(len(associated_name))

			# Unique name associated : classical case
			if len(associated_name) == 1:
				df_subject_id = filter_by_patient_name(df,associated_name[0])
				df_subject_id["associated_name"] = associated_name[0]
				df_subject_id["corrected_name"] = ids

				#print(df_subject_id.head)


			# There are multiple names (typos) : concatenate into one
			else:
				df_list = []

				for name in associated_name:
					df_associated = filter_by_patient_name(df,name)
					df_associated["associated_name"] = name
					df_associated["corrected_name"] = ids

					df_list.append(df_associated)

				df_subject_id = pd.concat(df_list)

		else:
			if len(associated_name) == 1:
				df_subject_id = filter_by_patient_name(df,associated_name[0])
				df_subject_id["associated_name"] = associated_name[0]
				df_subject_id["corrected_name"] = ids



		# print(df_subject_id.shape)
		df_filename = f"sequences_{ids}.csv"


		os.makedirs(os.path.join(raw_structure_dir,ids),exist_ok = True)
		df_filename = f"sequences_{ids}.csv"

		df_subject_id.to_csv(os.path.join(raw_structure_dir,ids,df_filename))

		df_seq = pd.read_csv(os.path.join(raw_structure_dir,ids,df_filename))
		df_recpar = df_seq[df_seq['file_format'] == "RECPAR"]

		df_recpar.to_csv(os.path.join(raw_structure_dir,ids,f"sequences_RECPARC_{ids}.csv"))




################################################

## Identification des sessions  #####

## Dates to date :  ordre croissant. Def de ses-pre, post, post-diff

unique_corrected_names = list(set(df_correct_names["processed_name"].to_list()))

if createSes:

	print("===================================================")
	print("==========     CREATE SESSIONS FOLDER     =========")
	print("===================================================\n")

	for ids in tqdm(unique_corrected_names):
		df_recpar = pd.read_csv(os.path.join(raw_structure_dir,ids,f"sequences_RECPARC_{ids}.csv"))
		df_recpar['date'] = pd.to_datetime(df_recpar['date'], format='%Y.%m.%d')

		unique_dates = df_recpar['date'].drop_duplicates().sort_values().reset_index(drop=True).to_list()

		#print(unique_dates)
		if len(unique_dates) <= 3:
			for i in range(len(unique_dates)):
				session_id = f"ses-0{i}"
				wrong_session_id = "ses-0{i}"

				# if os.path.isdir(os.path.join(raw_structure_dir,ids,wrong_session_id)):
				# 	print("found")
				# 	os.rename(os.path.join(raw_structure_dir,ids,wrong_session_id),os.path.join(raw_structure_dir,ids,session_id))

				os.makedirs(os.path.join(raw_structure_dir,ids,session_id),exist_ok = True)


				df_recpar_ses = df_recpar[df_recpar["date"]== unique_dates[i]]

				df_recpar_ses.to_csv(os.path.join(raw_structure_dir,ids,session_id,f"sequences_{ids}_ses-0{i}.csv"))


		#print(len(unique_dates))
		if len(unique_dates) >= 4:
			print(ids)

			session_id = "ses-00"

			os.makedirs(os.path.join(raw_structure_dir,ids,session_id),exist_ok = True)
			df_recpar_ses00 = df_recpar[df_recpar["date"]== unique_dates[0]]
			df_recpar_ses00.to_csv(os.path.join(raw_structure_dir,ids,session_id,f"sequences_{ids}_ses-00.csv"))

			session_id = "ses-01" ### LA session post a été faite en 2 fois pour ce participant (VALMA)

			os.makedirs(os.path.join(raw_structure_dir,ids,session_id),exist_ok = True)
			df_recpar_ses01_1 = df_recpar[df_recpar["date"]== unique_dates[1]]
			df_recpar_ses01_2 = df_recpar[df_recpar["date"]== unique_dates[2]]
			df_recpar_ses01 = pd.concat([df_recpar_ses01_1,df_recpar_ses01_2])
			df_recpar_ses01.to_csv(os.path.join(raw_structure_dir,ids,session_id,f"sequences_{ids}_ses-01.csv"))


			session_id = "ses-02"
			os.makedirs(os.path.join(raw_structure_dir,ids,session_id),exist_ok = True)
			df_recpar_ses02 = df_recpar[df_recpar["date"]== unique_dates[3]]
			df_recpar_ses02.to_csv(os.path.join(raw_structure_dir,ids,session_id,f"sequences_{ids}_ses-02.csv"))



################################################

## Renommage des sessions  #####


if rename_session:

	print("===================================================")
	print("==========         RENAME SESSIONS        =========")
	print("===================================================\n")

	for ids in tqdm(unique_corrected_names):

		list_date = []

		session_list = ["ses-00","ses-01","ses-02"]
		session_list = [s for s in os.listdir(os.path.join(raw_structure_dir,ids)) if 'ses' in s]


		for ses in session_list:

			if os.path.isdir(os.path.join(raw_structure_dir,ids,ses)):


				df_seq = pd.read_csv(os.path.join(raw_structure_dir,ids,ses,f"sequences_{ids}_{ses}.csv"))

				date_seq = df_seq["date"].to_list()[0]

				date_seq = datetime.datetime.strptime(date_seq,'%Y-%m-%d')


				list_date.append(date_seq)


		if len(list_date) == 2:

			difference = list_date[1] - list_date[0]

			days_diff = difference.days


			if days_diff >= 45:

				os.rename(os.path.join(raw_structure_dir,ids,"ses-00"),os.path.join(raw_structure_dir,ids,"ses-pre"))
				os.rename(os.path.join(raw_structure_dir,ids,"ses-01"),os.path.join(raw_structure_dir,ids,"ses-postdiff"))

			else:

				os.rename(os.path.join(raw_structure_dir,ids,"ses-00"),os.path.join(raw_structure_dir,ids,"ses-pre"))
				os.rename(os.path.join(raw_structure_dir,ids,"ses-01"),os.path.join(raw_structure_dir,ids,"ses-post"))

		elif len(list_date) == 3:

			os.rename(os.path.join(raw_structure_dir,ids,"ses-00"),os.path.join(raw_structure_dir,ids,"ses-pre"))
			os.rename(os.path.join(raw_structure_dir,ids,"ses-01"),os.path.join(raw_structure_dir,ids,"ses-post"))
			os.rename(os.path.join(raw_structure_dir,ids,"ses-02"),os.path.join(raw_structure_dir,ids,"ses-postdiff"))


		elif len(list_date) == 1:

			os.rename(os.path.join(raw_structure_dir,ids,"ses-00"),os.path.join(raw_structure_dir,ids,"ses-pre"))

		elif len(list_date) == 4:
			print(ids)



unique_corrected_names = list(set(df_correct_names["processed_name"].to_list()))
if createSes_seq:

	print("===================================================")
	print("==========        RENAME SEQUENCE CSV     =========")
	print("===================================================\n")


	for ids in tqdm(unique_corrected_names):
		df_recpar = pd.read_csv(os.path.join(raw_structure_dir,ids,f"sequences_RECPARC_{ids}.csv"))
		df_recpar['date'] = pd.to_datetime(df_recpar['date'], format='%Y.%m.%d')

		unique_dates = df_recpar['date'].drop_duplicates().sort_values().reset_index(drop=True).to_list()

		#print(unique_dates)

		session_list = [s for s in os.listdir(os.path.join(raw_structure_dir,ids)) if "ses" in s]

		for ses in session_list:

			csv_file = glob.glob(os.path.join(raw_structure_dir,ids,ses,f"sequences_{ids}_ses-*.csv"))


			df_seq = pd.read_csv(csv_file[0])
			df_seq["session_name"] = ses
			#df_seq = df_seq.drop("session_id", axis=1)

			df_seq.to_csv(csv_file[0])

			os.rename(csv_file[0],os.path.join(raw_structure_dir,ids,ses,f"sequences_{ids}_{ses}.csv"))





		# if len(unique_dates) <= 3:
		# 	for i in range(len(unique_dates)):
		# 		session_id = f"ses-0{i}"
		# 		wrong_session_id = "ses-0{i}"

		# 		if os.path.isdir(os.path.join(raw_structure_dir,ids,wrong_session_id)):
		# 			os.rename(os.path.join(raw_structure_dir,ids,wrong_session_id),os.path.join(raw_structure_dir,ids,session_id))

		# 		os.makedirs(os.path.join(raw_structure_dir,ids,session_id),exist_ok = True)


		# 		df_recpar_ses = df_recpar[df_recpar["date"]== unique_dates[i]]

		# 		df_recpar_ses.to_csv(os.path.join(raw_structure_dir,ids,session_id,f"sequences_{ids}_ses-0{i}.csv"))


	# #print(len(unique_dates))
	# ## Exclu mais à ajouter : 2-03VALMA ci203
	# if len(unique_dates) >= 4:
	# 	print(ids)


if createSummary:

	print("===================================================")
	print("==========   CREATE SESSION SUMMARY CSV   =========")
	print("===================================================\n")


	df_summary = pd.DataFrame(columns = ["patient_name","have_ses_pre","have_ses_post","have_ses_postdiff","have_T1_pre","have_T1_post","have_T1_postdiff","have_T2_pre","have_T2_post","have_T2_postdiff"])
	df_list = []
	for ids in tqdm(unique_corrected_names):

		ses0 = "ses-pre"
		ses1 = "ses-post"
		ses2 = "ses-postdiff"

		have_ses_pre = 0
		have_ses_post = 0
		have_ses_postdiff = 0

		have_T1_pre = 0
		have_T1_post = 0
		have_T1_postdiff = 0

		have_T2_pre = 0
		have_T2_post = 0
		have_T2_postdiff = 0


		if os.path.isdir(os.path.join(raw_structure_dir,ids,ses0)):

			have_ses_pre = 1

			df_seq = pd.read_csv(os.path.join(raw_structure_dir,ids,ses0,f"sequences_{ids}_ses-pre.csv"))

			seq_list = [s.lower() for s in df_seq["protocol"].to_list()] 


			for seq in seq_list:
				if '3dt1' in seq:
					have_T1_pre += 1
				elif 't2' in seq:
					have_T2_pre += 1

			

		if os.path.isdir(os.path.join(raw_structure_dir,ids,ses1)):

			have_ses_post = 1

			df_seq = pd.read_csv(os.path.join(raw_structure_dir,ids,ses1,f"sequences_{ids}_ses-post.csv"))

			seq_list = [s.lower() for s in df_seq["protocol"].to_list()] 

			if "3dt1" in seq_list:
				have_T1_post = 1
			if "t2" in seq_list:
				have_T2_post = 1

		if os.path.isdir(os.path.join(raw_structure_dir,ids,ses2)):

			have_ses_postdiff = 1

			df_seq = pd.read_csv(os.path.join(raw_structure_dir,ids,ses2,f"sequences_{ids}_ses-postdiff.csv"))

			seq_list = [s.lower() for s in df_seq["protocol"].to_list()] 


			if "3dt1" in seq_list:
				have_T1_postdiff = 1
			if "t2" in seq_list:
				have_T2_postdiff= 1

		df_line = pd.DataFrame([{
			"patient_name": ids,
			"have_ses_pre": have_ses_pre,
			"have_ses_post":have_ses_post,
			"have_ses_postdiff":have_ses_postdiff,
			"have_T1_pre":have_T1_pre,
			"have_T2_pre": have_T2_pre,
			"have_T1_post":have_T1_post,
			'have_T2_post':have_T2_post,
			"have_T1_postdiff":have_T1_postdiff,
			"have_T2_postdiff" : have_T2_postdiff


			}])

		df_list.append(df_line)


	df_summary = pd.concat(df_list)


	df_summary.to_csv("/Volumes/BackupDisk/APEX/apex_enf/docs/summary_mri.csv")




















