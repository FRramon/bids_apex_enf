

source_data_dir = "/Volumes/My Passport/source_data"
rawdata_dir = "/Volumes/My Passport/rawdata"

print(os.listdir(rawdata_dir))
bidscoiner_history = os.path.join(rawdata_dir,"code","bidscoin","bidscoiner.tsv")

df_bidcoiner_history = pd.read_csv(bidscoiner_history,sep = '\t')


print(df_bidcoiner_history.columns)


rename_target = False
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
						#os.rename(files,new_filename)

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



