import pandas as pd

def process_files(file_paths):
    """
    Process a list of sto files, 
    read them into a list of DataFrames, 
    remove the header rows which ends after "endheader" 
    
    The DataFrames will contain the kinematic data, including angles.
    Returns a list of DataFrames, one for each file.
    """
    dfs = []  # List to store DataFrames
    for path in file_paths:
    # Find the line number where 'endheader' appears
        with open(path) as f:
            for i, line in enumerate(f):
                if 'endheader' in line:
                    header_line = i
                    break

        data = pd.read_csv(path, sep='\t',header=header_line -1)
        dfs.append((data, path))  # Store tuple of (DataFrame, file name)

    return dfs

def extract_list_of_metrics(df):
    """
    Extracts a list of metrics from the DataFrame.
    
    Parameters:
    df (DataFrame): The DataFrame containing kinematic data.
    
    Returns:
    list: A list of metric names (column names).
    """
    # Assuming the first column is 'time' and the rest are metrics
    return df.columns[1:].tolist()  # Exclude 'time' column

def static_plot(dfs_with_names, metrics=None):
    """
    Create a static plot of the kinematic curves from the DataFrames to compare across files.

    Inputs: dfs: List of DataFrames containing kinematic data.
            metrics: List of metric names to plot. If None, all metrics will be plotted.
    """
    import matplotlib.pyplot as plt

    for df, file_name in dfs_with_names:
        if metrics is None:
            metrics = extract_list_of_metrics(df)
        for metric in metrics:
            plt.plot(df['time'], df[metric], label=f"{metric} - {file_name}")
    plt.xlabel("Time (s)")
    plt.ylabel("Value")
    plt.title("Static Plot of Kinematic Curves")
    plt.legend()
    plt.show()

if __name__ == "__main__":
    dfs_with_names = process_files(['STOfiles/0627G1squat_Kinematics_q.sto',
                                    'STOfiles/0627G2squat_Kinematics_q.sto',])
    # static_plot(dfs_with_names, metrics=['knee_rotation_r', 'knee_rotation_l'])
    

