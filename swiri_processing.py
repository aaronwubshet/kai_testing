


def read_in_files(file_paths):
    """
    Reads in a list of file paths and returns a DataFrame for each file.
    
    Parameters:
    file_paths (list): List of file paths to read.
    
    Returns:
    list: List of DataFrames.
    """
    import pandas as pd
    
    dataframes = []
    for path in file_paths:
        df = pd.read_csv(path, sep='\t', header=[3, 4])
        dataframes.append(df)
    
    return dataframes

def clip_and_clean(dataframes):
    """
    Clips and cleans the DataFrames by forward-filling marker names and removing unnecessary entries.
    
    Parameters:
    dataframes (list): List of DataFrames to process.
    
    Returns:
    list: List of cleaned DataFrames.
    """
    import pandas as pd
    
    cleaned_dfs = []
    for df in dataframes:
        # Forward-fill the marker names in the first level of the columns
        marker_names = df.columns.get_level_values(0)
        coords = df.columns.get_level_values(1)
        marker_names_filled = marker_names.to_series().replace('Unnamed.*', pd.NA, regex=True).ffill().values
        
        # Rebuild the MultiIndex with corrected marker names
        df.columns = pd.MultiIndex.from_arrays([marker_names_filled, coords])
        
        # Extract the marker names and trim out first two entries which are not markers
        marker_names = df.columns.get_level_values(0).unique()
        marker_names = marker_names[2:]  # Assuming first two are not markers
        
        cleaned_dfs.append(df)
    
    return cleaned_dfs

def extract_marker_indices(df):
    """
    Extracts and adjusts the markers for each the dataframe in the list for each marker name
    return a dictionary of where the keys are the marker names and the values are the indices adjusted for coordinate postfix.

    Example:
    {
        'shoulder_r': {'x': 'X4', 'y': 'Y4', 'z': 'Z4'},
        'elbow_r': {'x': 'X5', 'y': 'Y5', 'z': 'Z5'},
        ...
        }

    """
    marker_names = df.columns.get_level_values(0).unique()
    # trim out first two entries which are not markers
    marker_names = marker_names[2:]
    marker_indices = {}
    for marker in marker_names:
        index = marker_names.get_loc(marker) + 1  # Adjust for coordinate postfix
        marker_indices[marker] = {
            'x': f"X{index}",
            'y': f"Y{index}",
            'z': f"Z{index}"
        }
    return marker_indices
     
def extract_coordinates(df, marker):
    """
    Extracts the coordinates for a given marker from the DataFrame.
    
    Parameters:
    df (DataFrame): The DataFrame containing marker data.
    marker (str): The marker name to extract coordinates for.
    
    Returns:
    tuple: Coordinates (x, y, z) of the marker.
    """
    marker_indices = extract_marker_indices(df)
    x_idx = f"{marker_indices[marker]['x']}"
    y_idx = f"{marker_indices[marker]['y']}"
    z_idx = f"{marker_indices[marker]['z']}"
    
    return df[(marker, x_idx)].values, df[(marker, y_idx)].values, df[(marker, z_idx)].values

def calculate_angle(a, b, c):
    """
    Calculate the angle between three points a, b, c.
    
    Parameters:
    a (array-like): Coordinates of point a.
    b (array-like): Coordinates of point b.
    c (array-like): Coordinates of point c.
    
    Returns:
    float: Angle in degrees.
    """
    import numpy as np
    
    ba = a - b
    bc = c - b
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))  # Clip to avoid NaN due to floating point errors
    return np.degrees(angle)

def calculate_joint_angles(df, angle_types):
    """
    Calculate angles based on the specified angle type at each row in the DataFrame.
    
    Parameters:
    df (DataFrame): The DataFrame containing marker data.
    angle_types (list of strings): Type of angle to calculate ('shoulder', 'elbow', 'wrist', 'hip', 'knee_r', 'ankle').

    Returns:
    float: data frame with field for selected angle
    
    """
    import numpy as np
    
    # Define the markers for each angle type
    # The markers are tuples of (marker1, marker2, marker3) where the angle is calculated at marker2
    # e.g., for 'shoulder', the angle is calculated at 'shoulder_r' using 'hip_r' and 'elbow_r'
    # The order is important: the angle is calculated at the second marker in the tuple
    marker_map = {
        'shoulder': ('hip_r', 'shoulder_r', 'elbow_r'),
        'knee_l': ('hip_l', 'knee_l', 'ankle_l'),
        'elbow': ('shoulder_r', 'elbow_r', 'wrist_r'),
        'wrist': ('elbow_r', 'wrist_r', 'elbow_r'),
        'hip': ('shoulder_r', 'hip_r', 'knee_r'),
        'knee_r': ('hip_r', 'knee_r', 'ankle_r'),
        'ankle': ('knee_r', 'ankle_r', 'foot_r_6'),
        'foot': ('ankle_r', 'foot_r_6', 'toes_r_6')
    }

    for angle_type in angle_types:
        if angle_type not in marker_map:
            raise ValueError(f"Invalid angle type: {angle_type}")

        markers = marker_map[angle_type]
        X = extract_coordinates(df, markers[0])
        Y = extract_coordinates(df, markers[1])
        Z = extract_coordinates(df, markers[2])
        
        angles = []
        for x, y, z in zip(zip(*X), zip(*Y), zip(*Z)):
            angle = calculate_angle(np.array(x), np.array(y), np.array(z))
            angles.append(angle)
        
        df[f'{angle_type}_angle'] = angles
    return df

def plot_joint_angles(df, angle_types):
    """
    Plot the joint angles over time. all on one figure.
    
    Parameters:
    df (DataFrame): The DataFrame containing marker data with angles.
    angle_types (list of str): Types of angles to plot ['shoulder', 'elbow', 'wrist', 'hip', 'knee', 'ankle'].

    Returns:
    None
    """
    import matplotlib.pyplot as plt

    plt.figure(figsize=(12, 8))
    for angle_type in angle_types:
        if f'{angle_type}_angle' in df.columns:
            plt.plot(df.index, df[f'{angle_type}_angle'], label=f'{angle_type} angle')
        else:
            print(f"Warning: {angle_type} angle not found in DataFrame.")

    plt.xlabel('Time')
    plt.ylabel('Angle (degrees)')
    plt.title('Joint Angles Over Time')
    plt.legend()
    plt.grid()
    plt.show()

def full_pipeline(file_paths, angle_types=['shoulder', 'elbow', 'wrist', 'hip', 'knee_r', 'ankle','knee_l']):
    """
    Full processing pipeline: read files, clean data, calculate angles, and plot. Plots all angle types.

    Parameters:
    file_paths (list): List of file paths to read.
    angle_types (list of str): Types of angles to calculate and plot.

    Returns:
    None
    """
    dfs = read_in_files(file_paths)
    cleaned_dfs = clip_and_clean(dfs)

    for df in cleaned_dfs:
        df = calculate_joint_angles(df, angle_types)
        plot_joint_angles(df, angle_types)

def multiple_pipeline(file_paths, angle_types=['shoulder', 'elbow', 'wrist', 'hip', 'knee_r', 'ankle','knee_l']):
    """
    Process multiple files and plot angles from each file in a single figure.
    
    Parameters:
    file_paths (list): List of file paths to read.
    angle_types (list of str): Types of angles to calculate and plot.

    Returns:
    None
    """
    import matplotlib.pyplot as plt

    plt.figure(figsize=(12, 8))
    
    for path in file_paths:
        df = read_in_files([path])[0]  # Read the first DataFrame from the file
        df = clip_and_clean([df])[0]  # Clean the DataFrame
        df = calculate_joint_angles(df, angle_types)  # Calculate angles
        
        for angle_type in angle_types:
            if f'{angle_type}_angle' in df.columns:
                plt.plot(df.index, df[f'{angle_type}_angle'], label=f'{angle_type} angle - {path}')
            else:
                print(f"Warning: {angle_type} angle not found in DataFrame for {path}.")

    plt.xlabel('Time')
    plt.ylabel('Angle (degrees)')
    plt.title('Joint Angles Over Time for Multiple Files')
    plt.legend()
    plt.grid()
    plt.show()

if __name__ == "__main__":

    # Example usage
    file_paths = ['TRCfiles/0627G1squat.trc', 'TRCfiles/0627G2squat.trc', 'TRCfiles/0627H1squat.trc']
    multiple_pipeline(file_paths, angle_types=[ 'knee_r','knee_l'])