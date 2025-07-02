
def gather_sto_files(folder_path):
    '''
    Gathers all .sto files from the specified folder path. Process them into a list of data frames with their names and attempt numbers
    read them into a list of DataFrames, 
    remove the header rows which ends after "endheader" 
    Args:
        folder_path (str): The path to the folder containing .sto files.
    Returns:
        list: A list of tuples, each containing a DataFrame, athlete name, and attempt number.

    '''
    import os
    import pandas as pd
    mapping = {
        '0627G1squat_Kinematics_q.sto': ('Gabby', 1),
        '0627G2squat_Kinematics_q.sto': ('Gabby', 2),
        '0627H1squat_Kinematics_q.sto': ('Hannah', 1),
        '0627G1squat_Kinematics_q2.sto': ('Gabby', 2),
        '0627G2squat_Kinematics_q2.sto': ('Gabby', 2),
        '0627A1sprint_Kinematics_q.sto': ('Aaron', 1),
    }
    dfs_with_names = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.sto'):
            file_path = os.path.join(folder_path, filename)
            # Find the line number where 'endheader' appears
            with open(file_path) as f:
                for i, line in enumerate(f):
                    if 'endheader' in line:
                        header_line = i
                        break

            # Read the file into a DataFrame
            df = pd.read_csv(file_path, sep='\t', header=header_line - 1)
            # Extract athlete name and attempt number from mapping
            athlete_name, attempt_number = mapping.get(filename, ('Unknown', 0))
            dfs_with_names.append((df, athlete_name, attempt_number))
    return dfs_with_names




if __name__ == "__main__":
    folder_path = 'STOfiles'
    dfs_with_names = gather_sto_files(folder_path)
    
    # #testing the output
    # for df, athlete_name, attempt_number in dfs_with_names:
    #     print(f"Athlete: {athlete_name}, Attempt: {attempt_number}")
    #     print(df.head())  # Display the first few rows of each DataFrame