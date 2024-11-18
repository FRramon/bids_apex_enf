from tkinter import *
import subprocess
import os
import signal
import pandas as pd
import glob


source_dir = '/Volumes/My Passport'
rawdata_dir= os.path.join(source_dir,'rawdata')
rawdata_dir_mrview = rawdata_dir.replace(' ', '\\ ')

start = 0


###################################################
#################  DEFINE STEP    #################
###################################################

first_run = True  #### First run is TRUE if its the first time you're running the code (and click_step is False)
click_step = True #### Every other run, click_step must be True, and first run False

###################################################


def clickKeepRun1():
    global keep_run,delete_run,clicked
    keep_run = "1"
    delete_run = "2"
    clicked = True
    root.destroy()
    return keep_run,delete_run,clicked

def clickKeepRun2():
    global keep_run,delete_run,clicked
    keep_run = "2"
    delete_run = "1"
    clicked = True 
    root.destroy()
    return keep_run,delete_run,clicked


if first_run:

    T2_run_files = glob.glob(f"{rawdata_dir}/sub-*/ses-*/anat/*_run-*_T2w.nii.gz")
    subses_list_init = [s.split('/')[4:6] +[0,0,0] for s in T2_run_files]  ### Takes every subject id + session id + two zeros to initialize, for subject that have run-* T2w

    ### Define an empty dataframe

    columns = ['subject_id', 'session_id','clicked','T2_to_keep','T2_to_delete']
    df_init = pd.DataFrame(subses_list_init, columns=columns).drop_duplicates()
    df_init.to_csv(os.path.join(source_dir,"francois","check_T2w_apex_enf.csv"))

    print(df_init.head())


if click_step:

    df_click = pd.read_csv(os.path.join(source_dir,"francois","check_T2w_apex_enf.csv"))

    for index, row in df_click.iterrows():

        if row["clicked"] == 0:
            subject_id = row["subject_id"]
            session_id = row["session_id"]
            print(f"Checking {subject_id} - {session_id}")

            if os.path.isfile(f"{rawdata_dir}/{subject_id}/{session_id}/anat/{subject_id}_{session_id}_run-1_T2w.nii.gz") and os.path.isfile(f"{rawdata_dir}/{subject_id}/{session_id}/anat/{subject_id}_{session_id}_run-2_T2w.nii.gz"):

                ## Open chosen images (mricron, mango, mrview, fsleyes, matplotlib.pyplot.imshow or nilearn.plotting ...) ##
                command_view = f"mrview {rawdata_dir_mrview}/{subject_id}/{session_id}/anat/{subject_id}_{session_id}_run-1_T2w.nii.gz -overlay.load {rawdata_dir_mrview}/{subject_id}/{session_id}/anat/{subject_id}_{session_id}_run-2_T2w.nii.gz -overlay.opacity 0.6"# -overlay.colour 0,0,255 -overlay.intensity 0,15000"
                command_view1 = f"mrview {rawdata_dir_mrview}/{subject_id}/{session_id}/anat/{subject_id}_{session_id}_run-1_T2w.nii.gz -position 100,500 -sync.focus"# -overlay.load {rawdata_dir_mrview}/{subject_id}/{session_id}/anat/{subject_id}_{session_id}_run-2_T2w.nii.gz -overlay.opacity 0.6"# -overlay.colour 0,0,255 -overlay.intensity 0,15000"

                pro1 = subprocess.Popen(command_view1, stdout=subprocess.PIPE, 
                        shell=True, preexec_fn=os.setsid) 

                command_view2 = f"mrview {rawdata_dir_mrview}/{subject_id}/{session_id}/anat/{subject_id}_{session_id}_run-2_T2w.nii.gz -position 900,500 -sync.focus"# -overlay.colour 0,0,255 -overlay.intensity 0,15000"
                pro2 = subprocess.Popen(command_view2, stdout=subprocess.PIPE, 
                        shell=True, preexec_fn=os.setsid) 

                root = Tk()
                root.title("Which T2 to keep ? Left = run-1; Right = run-2")
                root.geometry("500x160")
                button1 = Button(root,text='Keep run 1', command=clickKeepRun1)
                button1.place(x=700, y=700)
                button1.pack()

                button2 = Button(root,text='Keep run 2', command=clickKeepRun2)
                button2.place(x=700, y=600)
                button2.pack()
                   
                root.mainloop()
                os.killpg(os.getpgid(pro1.pid), signal.SIGTERM)  
                os.killpg(os.getpgid(pro2.pid), signal.SIGTERM)  


                if clicked:
                    df_click.at[index, "clicked"] = 1
                    df_click.at[index, "T2_to_keep"] = keep_run
                    df_click.at[index, "T2_to_delete"] = delete_run

                    df_click.to_csv(os.path.join(source_dir, "francois", "check_T2w_apex_enf.csv"), index=False)





### ICI, une fois que le tableau est plein (ie clicked est 1 partout, renommer le 'T2_to_keep' en sub-*_ses-*_T2w.* et sub-*_ses-*_part-phase_T2w.*)
### Et supprimer les 

#### ICI ajouter code qui fait l'excel final : has T1, has T2, has fmap, has dwiPA, has dwi AP, has rs fmri, has dot, has stop

    #         if os.path.isfile(f"{ses_dir}/{ses}/anat/{sub_id}_{ses}_T1w.nii.gz"):
    #             has_anat = 1
    #         if os.path.isfile(f"{ses_dir}/{ses}/dwi/{sub_id}_{ses}_acq-6dirs_dir-AP_dwi.nii.gz"):
    #             has_dwiAP = 1
    #         if os.path.isfile(f"{ses_dir}/{ses}/dwi/{sub_id}_{ses}_acq-60dirs_dir-PA_dwi.nii.gz"):
    #             has_dwiPA = 1
    #         if os.path.isfile(f"{ses_dir}/{ses}/func/{sub_id}_{ses}_task-rest_bold.nii.gz"):
    #             has_rsfmri = 1


    #         row_iter = {'Group': g, 'subject_id': sub_id,'session_id': ses,'anat':has_anat,'dwiAP': has_dwiAP,'dwiPA':has_dwiPA,'rsfmri':has_rsfmri,'fmap' : has_fmap,'PE_direction':phase_encoding_dir}
    #         df = df._append(row_iter,ignore_index=True)


    # df.to_csv(f"/Volumes/My Passport/francois/check_T2w_apex_enf.csv")




            
