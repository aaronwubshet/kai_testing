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

# Define the mapping for file names to more readable names
mapping = {
    '0627G1squat_Kinematics_q.sto': 'Gabby squat 1',
    '0627G2squat_Kinematics_q.sto': 'Gabby squat 2',
    '0627H1squat_Kinematics_q.sto': 'Hannah squat 1',
    '0627A1sprint_Kinematics_q.sto': 'Aaron sprint 1',
    '0627H1sprint_Kinematics_q.sto': 'Hannah sprint 1',
    '0627G1sprint_Kinematics_q.sto': 'Gabby sprint 1'
}

# --- METRICS CONFIGURATION ---

# Read the metrics.csv file
metrics_df = pd.read_csv("metrics.csv")

# Build the metric_groups dictionary from the CSV
metric_groups = {}
for col in metrics_df.columns:
    # Drop NaN and empty strings, keep only valid metric names
    metrics = [m for m in metrics_df[col].dropna() if str(m).strip() != ""]
    metric_groups[col] = metrics

all_metrics = [metric for metrics in metric_groups.values() for metric in metrics]


# --- DASH APP ---

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H2("Dynamic Kinematic Plotter"),
    # Box around file selection
    html.Div([
        html.Label("Select Files:"),
        dcc.Checklist(
            id='file-checklist',
            options=[{'label': mapping[f], 'value': f} for f in sto_files],
            value=[],
            inline=True
        ),
    ], style={
        'margin-bottom': '20px',
        'margin-right': '40px',
        'minWidth': '250px',
        'alignItems': 'center',
        'border': '2px solid #888',
        'borderRadius': '8px',
        'padding': '16px',
        'background': '#fafbfc'
    }),
    # Box around metrics selection (both rows)
    html.Div([
        # First row: first 5 metric groups
        html.Div([
            *[
                html.Div([
                    html.Label(f"{group} Metrics:"),
                    dcc.Checklist(
                        id=f"{group.lower()}-metrics",
                        options=[{'label': m, 'value': m} for m in metric_groups[group]],
                        value=[] if metric_groups[group] else [],
                        inline=True
                    ),
                ], style={'margin-right': '40px', 'minWidth': '200px'})
                for group in list(metric_groups.keys())[:5]
            ]
        ], style={'display': 'flex', 'flex-direction': 'row', 'align-items': 'flex-start', 'margin-bottom': '20px'}),
        # Second row: next 6 metric groups
        html.Div([
            *[
                html.Div([
                    html.Label(f"{group} Metrics:"),
                    dcc.Checklist(
                        id=f"{group.lower()}-metrics",
                        options=[{'label': m, 'value': m} for m in metric_groups[group]],
                        value=[] if metric_groups[group] else [],
                        inline=True
                    ),
                ], style={'margin-right': '40px', 'minWidth': '200px'})
                for group in list(metric_groups.keys())[5:11]
            ]
        ], style={'display': 'flex', 'flex-direction': 'row', 'align-items': 'flex-start'}),
    ], style={
        'border': '2px solid #888',
        'borderRadius': '8px',
        'padding': '16px',
        'background': '#f5f7fa',
        'margin-bottom': '20px'
    }),
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
    # Uncomment the following lines to run on a server or cloud platform
    # port = int(os.environ.get("PORT", 8050))
    # app.run(debug=True, host="0.0.0.0", port=port)  # Run the app on all interfaces

    # local run
    app.run(debug=True)