import os

source_data_dir = "/Volumes/My Passport/source_data_test_anonymize"

subject_list = [s for s in os.listdir(source_data_dir) if "sub" in s]

for sub in subject_list:
	session_list =  [s for s in os.listdir(os.path.join(source_data_dir,sub)) if "ses" in s]

	for ses in session_list:

		session_dir = os.path.join(source_data_dir,sub,ses)

		filelist = [file for file in os.listdir(session_dir) if "PAR" in file or "REC" in file]

		for file in filelist:
			# print(file)

			split_file = file.split("-")

			# if len(split_file[1]) == 2:
			# 	print("have to correct name")

				# old_name =  '-'.join(split_file)

				# corrected_name = split_file[0] + '-' + ''.join(split_file[1:3]) + '-' + '-'.join(split_file[3:])
				# print(old_name)
				# print(corrected_name)

				#os.rename(os.path.join(session_dir,old_name),os.path.join(session_dir,corrected_name))





			if file[0] != '.':

				print(file)



				newfilename = '-'.join(file.split("-")[2:])

				#os.rename(os.path.join(session_dir,file),os.path.join(session_dir,newfilename))

