import pandas as pd

# Skip the first 3 lines (metadata), use the next two as headers
df = pd.read_csv('0627G2squat.trc', sep='\t', header=[3, 4])

# Forward-fill the marker names in the first level of the columns
marker_names = df.columns.get_level_values(0)
coords = df.columns.get_level_values(1)
marker_names_filled = marker_names.to_series().replace('Unnamed.*', pd.NA, regex=True).ffill().values

# Rebuild the MultiIndex with corrected marker names
df.columns = pd.MultiIndex.from_arrays([marker_names_filled, coords])

# Extract the marker names
marker_names = df.columns.get_level_values(0).unique()
# trim out first two entries which are not markers
marker_names = marker_names[2:]


# Calculate the angle of the elbow joint using the coordinates of the shoulder, elbow, and wrist using 'shoulder_r', 'elbow_r', and 'wrist_r' from the DataFrame
import numpy as np
def calculate_angle(a, b, c):
    """Calculate the angle between three points a, b, c."""
    ba = a - b
    bc = c - b
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))  # Clip to avoid NaN due to floating point errors
    return np.degrees(angle)

# where in marker_names is shoulder_r and add 1 to get the x y z coordinate postfix
shoulder_index = marker_names.get_loc('shoulder_r') +1
# where in marker_names is elbow_r
elbow_index = marker_names.get_loc('elbow_r') +1
# where in marker_names is wrist_r
wrist_index = marker_names.get_loc('wrist_r') +1
# repeat for hip_r, knee_r, and ankle_r 
hip_index = marker_names.get_loc('hip_r') + 1
knee_index = marker_names.get_loc('knee_r') + 1
ankle_index = marker_names.get_loc('ankle_r') + 1

# foot angle repeat
foot_index = marker_names.get_loc('foot_r_6') + 1


#Convert the shoulder_index to the correct x and y coordinate modifier e.g., 'X4'
x_shoulder_idx = "X" + str(shoulder_index)
x_elbow_idx = "X" + str(elbow_index)
x_wrist_idx = "X" + str(wrist_index)
y_shoulder_idx = "Y" + str(shoulder_index)
y_elbow_idx = "Y" + str(elbow_index)
y_wrist_idx = "Y" + str(wrist_index)
z_wrist_idx = "Z" + str(wrist_index)
z_shoulder_idx = "Z" + str(shoulder_index)
z_elbow_idx = "Z" + str(elbow_index)

x_foot_idx = "X" + str(foot_index)
y_foot_idx = "Y" + str(foot_index)
z_foot_idx = "Z" + str(foot_index)


# repeat for hip, knee, and ankle
x_hip_idx = "X" + str(hip_index)
y_hip_idx = "Y" + str(hip_index)
z_hip_idx = "Z" + str(hip_index)
x_knee_idx = "X" + str(knee_index)
y_knee_idx = "Y" + str(knee_index)
z_knee_idx = "Z" + str(knee_index)
x_ankle_idx = "X" + str(ankle_index)
y_ankle_idx = "Y" + str(ankle_index)
z_ankle_idx = "Z" + str(ankle_index)

# Extract the coordinates for foot
foot = df[('foot_r_6', x_foot_idx)].values, df[('foot_r_6', y_foot_idx)].values, df[('foot_r_6', z_foot_idx)].values

# Extract the coordinates for shoulder, elbow, and wrist
# Using the modified indices to access the correct columns

shoulder = df[('shoulder_r', x_shoulder_idx)].values, df[('shoulder_r', y_shoulder_idx)].values,df[('shoulder_r', z_shoulder_idx)].values
elbow = df[('elbow_r', x_elbow_idx)].values, df[('elbow_r', y_elbow_idx)].values,df[('elbow_r', z_elbow_idx)].values
wrist = df[('wrist_r', x_wrist_idx)].values, df[('wrist_r', y_wrist_idx)].values, df[('wrist_r', z_wrist_idx)].values


# Repeat for hip, knee, and ankle
hip = df[('hip_r', x_hip_idx)].values, df[('hip_r', y_hip_idx)].values, df[('hip_r', z_hip_idx)].values
knee = df[('knee_r', x_knee_idx)].values, df[('knee_r', y_knee_idx)].values, df[('knee_r', z_knee_idx)].values
ankle = df[('ankle_r', x_ankle_idx)].values, df[('ankle_r', y_ankle_idx)].values, df[('ankle_r', z_ankle_idx)].values

# Calculate angles
angles = []
for s, e, w in zip(zip(*shoulder), zip(*elbow), zip(*wrist)):
    angle = calculate_angle(np.array(s), np.array(e), np.array(w))
    angles.append(angle)    
# Add angles to the DataFrame
df['elbow_angle'] = angles

# Add hip, knee, and ankle angles
knee_angles = []
for h, k, a in zip(zip(*hip), zip(*knee), zip(*ankle)):
    angle = calculate_angle(np.array(h), np.array(k), np.array(a))
    knee_angles.append(angle)
df['knee_angle'] = knee_angles

# Add foot angle
foot_angles = []
for f, k, a in zip(zip(*knee), zip(*ankle), zip(*foot)):
    angle = 180-calculate_angle(np.array(f), np.array(k), np.array(a))
    foot_angles.append(angle)
df['foot_angle'] = foot_angles

# create simple graph of elbow angle and knee angle
import matplotlib.pyplot as plt
plt.figure(figsize=(12, 6))
plt.plot(df.index, df['elbow_angle'], label='Elbow Angle', color='blue')
plt.plot(df.index, df['knee_angle'], label='Knee Angle', color='red')
plt.plot(df.index, df['foot_angle'], label='Ankle Angle', color='green')
plt.xlabel('Frame Index')
plt.ylabel('Angle (degrees)')
plt.title('Right Side: Elbow, Knee, and Ankle Angles Over Time')
plt.legend()
plt.grid()
plt.show()