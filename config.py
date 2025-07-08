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
# Define the mapping for file names to more readable names
file_mapping = {
    '0627G1squat_Kinematics_q.sto': 'Gabby squat 1',
    '0627G2squat_Kinematics_q.sto': 'Gabby squat 2',
    '0627H1squat_Kinematics_q.sto': 'Hannah squat 1',
    '0627A1sprint_Kinematics_q.sto': 'Aaron sprint 1',
    '0627H1sprint_Kinematics_q.sto': 'Hannah sprint 1',
    '0627G1sprint_Kinematics_q.sto': 'Gabby sprint 1',
    '0627ShootAround_Kinematics_q.sto': 'Sample shoot around',
}

# --- ATHLETE PROFILES ---
athlete_profiles = {
    'Gabby': {
        'name': 'Gabby Martinez',
        'photo': 'images/gaby.jpeg',
        'age': 22,
        'weight': '125 lbs',
        'height': '5\'6"',
        'sex': 'Female',
        'sport': 'Basketball',
        'position': 'Point Guard'
    },
    'Hannah': {
        'name': 'Hannah Johnson',
        'photo': 'images/hannah.jpeg',
        'age': 20,
        'weight': '135 lbs',
        'height': '5\'8"',
        'sex': 'Female',
        'sport': 'Basketball',
        'position': 'Shooting Guard'
    },
    'Aaron': {
        'name': 'Aaron Thompson',
        'photo': 'images/aaron.jpeg',
        'age': 24,
        'weight': '180 lbs',
        'height': '6\'2"',
        'sex': 'Male',
        'sport': 'Basketball',
        'position': 'Small Forward'
    }
}

# --- ATHLETE TO FILE PREFIX MAPPING ---
athlete_prefix_mapping = {
    'Gabby': 'G',
    'Hannah': 'H', 
    'Aaron': 'A'
}

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
DEBUG_MODE = True

# --- COMPONENT IDS ---
COMPONENT_IDS = {
    'debug_toggle': 'debug-toggle',
    'athlete_profile': 'athlete-profile-container',
    'file_selection': 'file-selection-container',
    'metrics_container': 'metrics-selection-container',
    'video_player': 'video-player',
    'kinematic_plot': 'kinematic-plot',
    'hierarchical_store': 'hierarchical-selection-store',
    'metrics_store': 'persistent-metrics-store'
}

# --- METRICS CONFIGURATION ---
try:
    metrics_df = pd.read_csv("metrics.csv")
    # Build the metric_groups dictionary from the CSV
    metric_groups = {}
    for col in metrics_df.columns:
        # Drop NaN and empty strings, keep only valid metric names
        metrics = [m for m in metrics_df[col].dropna() if str(m).strip() != ""]
        metric_groups[col] = metrics
    
    all_metrics = [metric for metrics in metric_groups.values() for metric in metrics]
except FileNotFoundError:
    print("Warning: metrics.csv not found. Using empty metrics configuration.")
    metric_groups = {}
    all_metrics = []

# --- GLOBAL STATE ---
current_mode = {'debug': False}
selected_metrics_store = []
