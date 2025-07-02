import dash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
import pandas as pd
import os

# --- CONFIGURATION ---
STO_FOLDER = "STOfiles"
# Gather all .sto files in the folder
sto_files = [f for f in os.listdir(STO_FOLDER) if f.endswith('.sto')]

# Read all files and store DataFrames in a dict
def read_sto_file(path):
    with open(path) as f:
        for i, line in enumerate(f):
            if 'endheader' in line:
                header_line = i
                break
    df = pd.read_csv(path, sep='\t', header=header_line-1)
    return df

dfs = {fname: read_sto_file(os.path.join(STO_FOLDER, fname)) for fname in sto_files}

# Get all possible metrics (assuming all files have the same columns)
all_metrics = ['pelvic_tilt', 'pelvic_list', 'pelvic_rotation', 'pelvic_tx', 'pelvic_ty', 'pelvic_tz', 'lumbar_extension', 'lumbar_bending', 'lumbar_rotation', 'neck_flex', 'neck_tilt', 'neck_rot', 'neck_tx1', 'neck_ty1', 'neck_tz1', 'SternumRRotZ', 'SternumRRotX', 'SternumRRotY', 'SternumRX', 'SternumRY', 'SternumRZ', 'SternumLRotZ', 'SternumLRotX', 'SternumLRotY', 'SternumLX', 'SternumLY', 'SternumLZ', 'shoulder_add_r', 'shoulder_flex_r', 'shoulder_rot_r', 'elbow_flexion_r', 'elbow_varus_valg_r', 'pro_sup_r', 'wrist_dev_r', 'wrist_flex_r', 'shoulder_add_l', 'shoulder_flex_l', 'shoulder_rot_l', 'elbow_flexion_l', 'elbow_varus_valg_l', 'pro_sup_l', 'wrist_dev_l', 'wrist_flex_l', 'hip_flexion_r', 'hip_adduction_r', 'hip_rotation_r', 'knee_angle_r', 'knee_rotation_r', 'knee_adduction_r', 'knee_tz_r', 'ankle_angle_r', 'subtalar_angle_r', 'mtp_angle_r', 'hip_flexion_l', 'hip_adduction_l', 'hip_rotation_l', 'knee_angle_l', 'knee_rotation_l', 'knee_adduction_l', 'knee_tz_l', 'ankle_angle_l', 'subtalar_angle_l', 'mtp_angle_l']


import pandas as pd

# Read the metrics.csv file
metrics_df = pd.read_csv("metrics.csv")

# Build the metric_groups dictionary from the CSV
metric_groups = {}
for col in metrics_df.columns:
    # Drop NaN and empty strings, keep only valid metric names
    metrics = [m for m in metrics_df[col].dropna() if str(m).strip() != ""]
    metric_groups[col] = metrics


# --- DASH APP ---

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H2("Dynamic Kinematic Plotter"),
    html.Div(
        [
            html.Div([
                html.Label("Select Files:"),
                dcc.Checklist(
                    id='file-checklist',
                    options=[{'label': f, 'value': f} for f in sto_files],
                    value=[],
                    inline=True
                ),
            ], style={'margin-right': '40px', 'minWidth': '250px', 'alignItems': 'center'}),  # <-- wider minWidth
            # Dynamically create a checklist for each metric group
            *[
                html.Div([
                    html.Label(f"{group} Metrics:"),
                    dcc.Checklist(
                        id=f"{group.lower()}-metrics",
                        options=[{'label': m, 'value': m} for m in metrics],
                        value=[] if metrics else [],
                        inline=True  # <-- This keeps checkbox and label on the same line
                    ),
                ], style={'margin-right': '40px', 'minWidth': '200px'})  # <-- Add minWidth or width here
                for group, metrics in metric_groups.items()
            ]
        ],
        style={'display': 'flex', 'flex-direction': 'row', 'align-items': 'flex-start'}
    ),
    dcc.Graph(id='kinematic-plot')
])
from dash.dependencies import ALL

@app.callback(
    Output('kinematic-plot', 'figure'),
    [Input('file-checklist', 'value')] +
    [Input(f"{group.lower()}-metrics", 'value') for group in metric_groups.keys()]
)
def update_plot(selected_files, *selected_metrics_groups):
    # Flatten all selected metrics into a single list
    selected_metrics = []
    for group_metrics in selected_metrics_groups:
        if group_metrics:
            selected_metrics.extend(group_metrics)
    fig = go.Figure()
    for fname in selected_files:
        df = dfs[fname]
        for metric in selected_metrics:
            if metric in df.columns:
                fig.add_trace(go.Scatter(
                    x=df['time'],
                    y=df[metric],
                    mode='lines',
                    name=f"{metric} - {fname}"
                ))
    fig.update_layout(
        xaxis_title="Time (s)",
        yaxis_title="Value",
        title="Kinematic Curves",
        legend_title="Metric - File"
    )
    return fig
if __name__ == "__main__":
    app.run(debug=True)