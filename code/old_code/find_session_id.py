import os
import pandas as pd
from datetime import datetime

raw_structure_dir = "/Volumes/My Passport/raw_patient_structure"

df_correct_names = pd.read_csv("/Volumes/My Passport/francois/names_corrected.csv")
unique_corrected_names = list(set(df_correct_names["processed_name"].to_list()))

print(unique_corrected_names)

session_list = ["ses-00","ses-01","ses-02"]





