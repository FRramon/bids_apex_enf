import os
import pandas as pd
import glob


## tableau avec colonnes : sub | ses | T1 | T2run1 | T2run2 | dwiPA | dwiAP | b0 | rsfmri | dot | stop

{"subject_id","session_id"}

source_data_dir = "/Volumes/My Passport/source_data"
rawdata_dir = "/Volumes/My Passport/rawdata_sourcename"

subject_list = [s for s in os.listdir(rawdata_dir) if "sub" in s]


