import os
import re
import pandas as pd

# This script processes a markdown file to:
# - Extract subject IDs and session IDs from `# sub-enf...` and `## ses-...` blocks.
# - Add the string "hello world" after each `## ses-...` block.
# - Store the extracted information (subject ID, session ID, and a fixed field `have_markdown_field = 1`) in a pandas DataFrame.
# - Save the extracted information into a CSV file.
# In the future, this script will take input for a subject ID, session ID, and comment, 
# and it will add the comment at the correct location in the markdown file.

####### First step is to have a column sub-enf*** named subject_id





def process_sub_enf_blocks(file_path, output_path, csv_path):
    # regex pattern to match `# sub-enf...` blocks and their content
    pattern = r"(# sub-enf[^\s]+\s+)(.*?)(?=# sub-|$)"
    
    # read the file
    with open(file_path, 'r') as file:
        content = file.read()
    
    subject_sessions = []  # list to store extracted subject and session IDs
    
    # process each `# sub-enf...` block
    def process_block(match):
        sub_line = match.group(1)  # `# sub-enf...` line
        nested_content = match.group(2)  # content between blocks

        # extract subject ID
        subject_id_match = re.search(r"# sub-enf([^\s]+)", sub_line)
        subject_id = subject_id_match.group(1) if subject_id_match else "Unknown"

        # add "hello world" after each `## ses-...`
        # updated_nested = re.sub(
        #     r"(## ses-[^\s]+)",
        #     lambda m: f"{m.group(0)}\nhello world",
        #     nested_content
        # )

        # extract session IDs
        session_ids = re.findall(r"## ses-([^\s]+)", nested_content)
        
        # add session info to the list
        for session_id in session_ids:
            subject_sessions.append({
                'subject_id': "sub-enf" + subject_id, 
                'session_id': "ses-" + session_id, 
                'have_markdown_field': 1
            })

        return f"{sub_line}{updated_nested}"

    # apply the transformation to the content
    updated_content = re.sub(pattern, process_block, content, flags=re.DOTALL)
    
    # write the updated content to a new file
    with open(output_path, 'w') as output_file:
        output_file.write(updated_content)
    
    # create pandas DataFrame from the session list
    df = pd.DataFrame(subject_sessions)

    # save DataFrame to CSV
    df.to_csv(csv_path, index=False)

    # print extracted subject and session IDs
    print("Extracted Subject and Session IDs:")
    print(df)

# def add_comments_to_md(file_path, comments_csv,equivalence_table_dir, output_path):
#     # read the CSV with comments to add
#     comments_df = pd.read_csv(comments_csv)

#     comments_df = comments_df.rename(columns={"subject_id": "original_id"})
#     comments_df['original_id'] = "sub-" + comments_df['original_id'].str.replace("-", "")

#     equivalence_table = pd.read_csv(equivalence_table_dir)

#     equivalence_table = equivalence_table.rename(columns={"original": "original_id", "renamed": "subject_id"})

#     comments_df = pd.merge(comments_df,equivalence_table,on = "original_id")

#     print(comments_df)

#     # read the markdown file
#     with open(file_path, 'r') as file:
#         content = file.read()

#     # for each row in the comments CSV, add the comment at the right place
#     for _, row in comments_df.iterrows():
#         subject_id = row['subject_id']
#         session_id = row['session_id']
#         comment = row['comment']

#         print(row["session_id"])


#         # regex to find the right session block
#         pattern = r"(## " + re.escape(session_id) + r"[^\n]*\n)"

#         # insert the comment after the session block
#         content = re.sub(pattern, lambda m: f"{m.group(0)}{comment}\n", content)

#         # update content with the new comment
#         #content = updated_content
    
#     # write the updated content back to the markdown file
#     with open(output_path, 'w') as output_file:
#         output_file.write(content)

def add_comments_to_md(file_path, comments_csvs, equivalence_table_dir, output_path):
    # Concatenate all comments CSVs into one DataFrame
    comments_list = [pd.read_csv(csv_path) for csv_path in comments_csvs]
    comments_df = pd.concat(comments_list, ignore_index=True)

    # Standardize subject IDs
    comments_df = comments_df.rename(columns={"subject_id": "original_id"})

    #comments_df['original_id'] = "sub-" + comments_df['original_id'].str.replace("-", "")
    pattern = r"^\d-\d{2}[A-Z]{5}$"  # Matches one digit, one "-", two digits, four uppercase letters

    def process_subject_id(subject_id):
        if re.match(pattern, subject_id):  # Use `re.match` to ensure the pattern matches the start of the string
            return "sub-" + subject_id.replace("-", "")  # Remove dashes if it matches
        return subject_id  # Return unchanged if it doesn't match

    # Apply the function to 'original_id'
    comments_df['original_id'] = comments_df['original_id'].apply(process_subject_id)

    print(comments_df)

    # Load the equivalence table and merge with comments
    equivalence_table = pd.read_csv(equivalence_table_dir)
    equivalence_table = equivalence_table.rename(columns={"original": "original_id", "renamed": "subject_id"})
    comments_df = pd.merge(comments_df, equivalence_table, on="original_id")
    print("Merged Comments DataFrame:")
    print(comments_df)

    # Read the markdown file
    with open(file_path, 'r') as file:
        content = file.read()

    # Regex pattern to match each `# sub-enf...` block and its content
    pattern = r"(# sub-enf[^\s]+\s+)(.*?)(?=# sub-|$)"
    
    # Function to process each block and insert comments
    def process_block(match):
        sub_line = match.group(1)  # `# sub-enf...` line
        nested_content = match.group(2)  # Content between blocks

        # Extract subject ID
        subject_id_match = re.search(r"# sub-enf([^\s]+)", sub_line)
        subject_id = subject_id_match.group(1) if subject_id_match else "Unknown"

        # Filter comments for this subject ID
        subject_comments = comments_df[comments_df['subject_id'] == "sub-enf" + subject_id]

        # If no comments for this subject, return block unchanged
        if subject_comments.empty:
            return f"{sub_line}{nested_content}"

        # Process session blocks within the subject block
        def process_session_block(session_match):
            session_line = session_match.group(0)  # `## ses-...` line
            session_id_match = re.search(r"## ses-([^\s]+)", session_line)
            session_id = session_id_match.group(1) if session_id_match else "Unknown"

            # Filter comments for this session
            session_comments = subject_comments[subject_comments['session_id'] == "ses-" + session_id]

            # Add comments if they exist for this session
            if not session_comments.empty:
                comments = "\n".join(session_comments['comment'])
                return f"{session_line}**Remarques FR BA**\n{comments}\n"
            return session_line

        # Update the nested content with comments for each session
        
        #updated_nested = re.sub(r"(## ses-[^\s]+\n)", process_session_block, nested_content)

        updated_nested = re.sub(
            r"(## ses-[^\s]+.*?)(?=(## ses-|# sub-enf-|$))", 
            process_session_block, 
            nested_content, 
            flags=re.DOTALL
        )

        return f"{sub_line}{updated_nested}"

    # Apply the block processing to the content
    updated_content = re.sub(pattern, process_block, content, flags=re.DOTALL)

    # Write the updated content back to the markdown file
    with open(output_path, 'w') as output_file:
        output_file.write(updated_content)


base_dir = "/Volumes/BackupDisk/APEX/apex_enf"
equivalence_table_dir = "/Volumes/CurrentDisk/APEX/apex_enf/rawdata/equivalence_table_participants.csv"
file_path = os.path.join(base_dir,'carnet_mri.md')  # input .md file path
output_path = os.path.join(base_dir,'carnet_mri2.md')  # output .md file path
csv_path = os.path.join(base_dir, 'subject_sessions.csv')  # output CSV file path
comments_duplicates_csv = os.path.join(base_dir,"comments", 'comments_duplicates_larger.csv')  # CSV file with comments
comments_names_csv = os.path.join(base_dir,"comments", 'comments_name_correction.csv')  # CSV file with comments
comments_T2_csv = os.path.join(base_dir,"comments", 'comments_missing_acq_T2.csv')  # CSV file with comments
comments_fmri_csv = os.path.join(base_dir,"comments", "comments_task_fmri.csv")  # CSV file with comments

#process_sub_enf_blocks(file_path, output_path, csv_path)
add_comments_to_md(output_path, [comments_duplicates_csv,comments_names_csv,comments_T2_csv,comments_fmri_csv],equivalence_table_dir, output_path)


