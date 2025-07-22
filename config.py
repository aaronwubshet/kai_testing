# -*- coding: utf-8 -*-
"""
Configuration module for the Kinematic Dashboard
Contains global variables, constants, and configuration settings
"""

import os
import pandas as pd

# --- FILE PATHS AND FOLDERS ---
STO_FOLDER = "STOfiles"
ASSETS_FOLDER = "assets"
VIDEOS_FOLDER = os.path.join(ASSETS_FOLDER, "videos")
IMAGES_FOLDER = os.path.join(ASSETS_FOLDER, "images")

# --- DATA LOADING ---
# Gather all .sto files in the folder
sto_files = [f for f in os.listdir(STO_FOLDER) if f.endswith('.sto')]

# --- FILE NAME MAPPINGS ---
# File mappings are now handled dynamically through the hierarchical selector
# using the new naming convention: MMDDYYYY_athleteID_workoutname_attemptNumber_suffix.sto

# --- ATHLETE PROFILES ---
athlete_profiles = {
    'Gabby': {
        'name': 'Gabby Rizika',
        'photo': 'images/gabby.jpeg',
        'age': 22,
        'weight': '135 lbs',
        'height': '5\'6"',
        'sex': 'Female',
        'sport': 'Basketball',
        'position': 'Point Guard'
    },
    'Hannah': {
        'name': 'Hannah Steadman',
        'photo': 'images/hannah.jpeg',
        'age': 20,
        'weight': '125 lbs',
        'height': '5\'3"',
        'sex': 'Female',
        'sport': 'Basketball',
        'position': 'Shooting Guard'
    },
    'Aaron': {
        'name': 'Aaron Wubshet',
        'photo': 'images/aaron.jpeg',
        'age': 24,
        'weight': '2200 lbs',
        'height': '6\'2"',
        'sex': 'Male',
        'sport': 'Basketball',
        'position': 'Small Forward'
    }
}

# --- ATHLETE MAPPINGS ---
# New athlete ID mapping (extensible for future athletes)
athlete_id_mapping = {
    'Aaron': '1',
    'Gabby': '2',
    'Hannah': '3'
}

# Reverse mapping for filename parsing
id_to_athlete_mapping = {v: k for k, v in athlete_id_mapping.items()}

# Legacy athlete prefix mapping (for backward compatibility)
athlete_prefix_mapping = {
    'Gabby': 'G',
    'Hannah': 'H', 
    'Aaron': 'A'
}

# --- WORKOUT DISPLAY NAMES ---
# Extensible mapping for workout names to display names
workout_display_mapping = {
    'overheadsquat': 'Overhead Squat',
    'squat': 'Squat',
    'pushup': 'Push Up',
    'standingjump': 'Vertical Jump'
}

# Reverse mapping for filename construction
display_to_workout_mapping = {v: k for k, v in workout_display_mapping.items()}

# --- STYLING CONSTANTS ---
COLORS = {
    'primary': '#3498db',
    'secondary': '#2c3e50',
    'success': '#27ae60',
    'danger': '#e74c3c',
    'warning': '#f39c12',
    'info': '#17a2b8',
    'light': '#f8f9fa',
    'dark': '#343a40',
    'purple': '#8e44ad',
    'muted': '#7f8c8d'
}

# --- APP SETTINGS ---
APP_TITLE = "Dynamic Kinematic Plotter"

# --- DEPLOYMENT DETECTION ---
# Detect if running on cloud platform
IS_CLOUD_DEPLOYMENT = bool(os.environ.get("RENDER") or 
                          os.environ.get("HEROKU") or 
                          os.environ.get("VERCEL") or
                          os.environ.get("PORT"))  # Generic cloud platform indicator

# --- COMPONENT IDS ---
COMPONENT_IDS = {
    'athlete_profile': 'athlete-profile-container',
    'metrics_container': 'metrics-selection-container',
    'video_player': 'video-player',
    'kinematic_plot': 'kinematic-plot',
    'hierarchical_store': 'hierarchical-selection-store',
    'metrics_store': 'persistent-metrics-store'
}

# --- METRICS CONFIGURATION ---
# Direct mapping of body parts to metrics (from metrics.csv)
metric_groups = {
    'Pelvis': [
        'pelvic_tilt',
        'pelvic_list',
        'pelvic_rotation',
        'pelvic_tx',
        'pelvic_ty',
        'pelvic_tz'
    ],
    'Back': [
        'lumbar_extension',
        'lumbar_bending',
        'lumbar_rotation'
    ],
    'Neck': [
        'neck_flex',
        'neck_tilt',
        'neck_rot',
        'neck_tx1',
        'neck_ty1',
        'neck_tz1'
    ],
    'Chest': [
        'SternumRRotZ',
        'SternumRRotX',
        'SternumRRotY',
        'SternumRX',
        'SternumRY',
        'SternumRZ',
        'SternumLRotZ',
        'SternumLRotX',
        'SternumLRotY',
        'SternumLX',
        'SternumLY',
        'SternumLZ'
    ],
    'Shoulder': [
        'shoulder_add_r',
        'shoulder_flex_r',
        'shoulder_rot_r',
        'shoulder_add_l',
        'shoulder_flex_l',
        'shoulder_rot_l'
    ],
    'Elbow': [
        'elbow_flexion_r',
        'elbow_varus_valg_r',
        'elbow_flexion_l',
        'elbow_varus_valg_l'
    ],
    'Forearm': [
        'pro_sup_r',
        'pro_sup_l'
    ],
    'Wrist': [
        'wrist_dev_r',
        'wrist_flex_r',
        'wrist_dev_l',
        'wrist_flex_l'
    ],
    'Hip': [
        'hip_flexion_r',
        'hip_adduction_r',
        'hip_rotation_r',
        'hip_flexion_l',
        'hip_adduction_l',
        'hip_rotation_l'
    ],
    'Knee': [
        'knee_angle_r',
        'knee_rotation_r',
        'knee_adduction_r',
        'knee_tz_r',
        'knee_angle_l',
        'knee_rotation_l',
        'knee_adduction_l',
        'knee_tz_l'
    ],
    'Foot': [
        'ankle_angle_r',
        'subtalar_angle_r',
        'mtp_angle_r',
        'ankle_angle_l',
        'subtalar_angle_l',
        'mtp_angle_l'
    ]
}

# Create a flat list of all metrics
all_metrics = [metric for metrics in metric_groups.values() for metric in metrics]

# --- GLOBAL STATE ---
current_mode = {'debug': False}
selected_metrics_store = []
