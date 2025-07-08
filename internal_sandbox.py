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
    '0627G1sprint_Kinematics_q.sto': 'Gabby sprint 1',
    '0627ShootAround_Kinematics_q.sto': 'Sample shoot around',
}

# Athlete profiles data
athlete_profiles = {
    'Gabby': {
        'name': 'Gabby Martinez',
        'photo': 'images/gabby.jpeg',
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

# Function to extract athlete name from filename
def get_athlete_from_filename(filename):
    if 'G1' in filename or 'G2' in filename:
        return 'Gabby'
    elif 'H1' in filename:
        return 'Hannah'
    elif 'A1' in filename:
        return 'Aaron'
    return None

# Function to extract exercise type from filename
def get_exercise_from_filename(filename):
    if 'squat' in filename.lower():
        return 'squat'
    elif 'sprint' in filename.lower():
        return 'sprint'
    elif 'shootaround' in filename.lower():
        return 'shootaround'
    return None

# Helper functions for hierarchical dropdown system
def get_athletes_from_files():
    """Get unique athletes from available files"""
    athletes = set()
    for fname in sto_files:
        athlete = get_athlete_from_filename(fname)
        if athlete:
            athletes.add(athlete)
    return sorted(list(athletes))

def get_exercises_for_athlete(athlete):
    """Get available exercises for a specific athlete"""
    exercises = set()
    for fname in sto_files:
        if get_athlete_from_filename(fname) == athlete:
            exercise = get_exercise_from_filename(fname)
            if exercise:
                exercises.add(exercise)
    return sorted(list(exercises))

def get_attempts_for_athlete_exercise(athlete, exercise):
    """Get available attempt numbers for a specific athlete and exercise"""
    attempts = set()
    for fname in sto_files:
        if (get_athlete_from_filename(fname) == athlete and 
            get_exercise_from_filename(fname) == exercise):
            # Extract attempt number from filename
            if 'G1' in fname or 'H1' in fname or 'A1' in fname:
                attempts.add(1)
            elif 'G2' in fname:
                attempts.add(2)
            # Add logic for more attempts if needed
    return sorted(list(attempts))

def construct_filename_from_hierarchy(athlete, exercise, attempt):
    """Construct filename from hierarchical selection"""
    if not all([athlete, exercise, attempt]):
        return None
    
    # Map athlete to file prefix
    athlete_prefix = {
        'Gabby': 'G',
        'Hannah': 'H', 
        'Aaron': 'A'
    }.get(athlete)
    
    if not athlete_prefix:
        return None
    
    # Construct filename based on pattern: 0627{athlete_prefix}{attempt}{exercise}_Kinematics_q.sto
    filename = f"0627{athlete_prefix}{attempt}{exercise}_Kinematics_q.sto"
    
    # Check if the constructed filename exists in our files
    if filename in sto_files:
        return filename
    
    return None

def get_files_for_athlete_exercise(athlete, exercise):
    """Get files matching athlete and exercise"""
    matching_files = []
    for fname in sto_files:
        if (get_athlete_from_filename(fname) == athlete and 
            get_exercise_from_filename(fname) == exercise):
            matching_files.append(fname)
    return matching_files

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

app = dash.Dash(__name__, suppress_callback_exceptions=True)

app.layout = html.Div([
    # Header with title and debug toggle
    html.Div([
        html.H2("Dynamic Kinematic Plotter", style={'margin': 0, 'flex': '1'}),
        # Debug mode toggle in top right
        html.Div([
            html.Label("Debug Mode:", style={'margin-right': '8px', 'font-weight': 'bold'}),
            dcc.Checklist(
                id='debug-toggle',
                options=[{'label': '', 'value': 'debug'}],
                value=[],
                inline=True,
                style={'margin-right': '5px'}
            ),
            html.Span("(Dropdowns)", style={'font-size': '12px', 'color': '#666'})
        ], style={
            'display': 'flex', 
            'align-items': 'center',
            'padding': '10px 15px',
            'background': '#e8f4f8',
            'border': '1px solid #3498db',
            'border-radius': '5px'
        })
    ], style={
        'display': 'flex', 
        'justify-content': 'space-between', 
        'align-items': 'center',
        'margin-bottom': '20px'
    }),
    
    # Top section with athlete profile and controls
    html.Div([
        # Left side: Athlete Profile
        html.Div([
            html.Div(id='athlete-profile-container', children=[
                html.Div([
                    html.Img(
                        src='/assets/placeholder-athlete.png',
                        style={
                            'width': '80px',
                            'height': '80px',
                            'border-radius': '50%',
                            'object-fit': 'cover',
                            'border': '3px solid #3498db',
                            'margin-bottom': '8px'
                        }
                    ),
                    html.H4("Select an athlete", style={'margin': '3px 0', 'color': '#2c3e50', 'font-size': '16px'}),
                    html.P("Choose files to view profile", style={'margin': '0', 'font-size': '14px', 'color': '#7f8c8d'})
                ], style={'text-align': 'center'})
            ])
        ], style={
            'flex': '0 0 250px',
            'margin-right': '20px',
            'border': '2px solid #3498db',
            'border-radius': '12px',
            'padding': '12px',
            'background': 'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)',
            'box-shadow': '0 4px 6px rgba(52, 152, 219, 0.1)',
            'min-height': '200px'
        }),
        
        # Right side: Controls
        html.Div([
            # File selection container (only shown in normal mode) - now appears first
            html.Div(id='file-selection-wrapper'),
            
            # Box around metrics selection (dynamic based on debug mode) - now appears second
            html.Div([
                html.Div(id='metrics-selection-container')
            ], id='metrics-container-box', style={
                'border': '2px solid #888',
                'borderRadius': '8px',
                'padding': '16px',
                'background': '#f5f7fa'
            })
        ], style={'flex': '1'})
    ], style={'display': 'flex', 'margin-bottom': '20px'}),
    
    # Graph and Notes side by side
    html.Div([
        # Left side: Graph
        html.Div([
            dcc.Graph(id='kinematic-plot')
        ], style={'flex': '2', 'margin-right': '20px'}),
        
        # Right side: Split Notes text boxes
        html.Div([
            # Key Takeaways section
            html.Div([
                html.Label("Key Takeaways:", style={'font-weight': 'bold', 'margin-bottom': '8px', 'color': '#8e44ad'}),
                dcc.Textarea(
                    id='key-takeaways-textarea',
                    placeholder="Summarize key takeaways...\n\n• Primary insights\n• Critical findings\n• Main conclusions\n• Important highlights",
                    style={
                        'width': '100%',
                        'height': '180px',
                        'padding': '12px',
                        'border': '2px solid #8e44ad',
                        'borderRadius': '8px',
                        'resize': 'vertical',
                        'font-family': 'Arial, sans-serif',
                        'font-size': '14px',
                        'line-height': '1.5'
                    },
                    value=""
                ),
            ], style={'margin-bottom': '15px'}),
            
            # Observations section
            html.Div([
                html.Label("Observations:", style={'font-weight': 'bold', 'margin-bottom': '8px', 'color': '#2c3e50'}),
                dcc.Textarea(
                    id='observations-textarea',
                    placeholder="Record your observations here...\n\n• Movement patterns\n• Key findings\n• Notable biomechanics\n• Data insights",
                    style={
                        'width': '100%',
                        'height': '180px',
                        'padding': '12px',
                        'border': '2px solid #3498db',
                        'borderRadius': '8px',
                        'resize': 'vertical',
                        'font-family': 'Arial, sans-serif',
                        'font-size': '14px',
                        'line-height': '1.5'
                    },
                    value=""
                ),
            ], style={'margin-bottom': '15px'}),
            
            # Recommended movements section
            html.Div([
                html.Label("Recommended Movements:", style={'font-weight': 'bold', 'margin-bottom': '8px', 'color': '#27ae60'}),
                dcc.Textarea(
                    id='recommendations-textarea',
                    placeholder="Document movement recommendations...\n\n• Corrective exercises\n• Training suggestions\n• Technical improvements\n• Follow-up actions",
                    style={
                        'width': '100%',
                        'height': '180px',
                        'padding': '12px',
                        'border': '2px solid #27ae60',
                        'borderRadius': '8px',
                        'resize': 'vertical',
                        'font-family': 'Arial, sans-serif',
                        'font-size': '14px',
                        'line-height': '1.5'
                    },
                    value=""
                ),
            ], style={'margin-bottom': '15px'}),
            
            # Save button
            html.Button(
                "Save Notes",
                id="save-notes-btn",
                n_clicks=0,
                style={
                    'background-color': '#007bff',
                    'color': 'white',
                    'border': 'none',
                    'padding': '10px 20px',
                    'border-radius': '5px',
                    'cursor': 'pointer',
                    'width': '100%',
                    'font-weight': 'bold'
                }
            ),
            html.Div(id="save-status", style={'margin-top': '10px'})
        ], style={
            'flex': '1',
            'border': '2px solid #888',
            'borderRadius': '8px',
            'padding': '16px',
            'padding-right': '32px',
            'background': '#f9f9f9',
            'min-width': '350px',
            'margin-right': '20px'
        })
    ], style={'display': 'flex', 'flex-direction': 'row'}),
    
    # Hidden component to store hierarchical selection (always present)
    dcc.Store(id='hierarchical-selection-store', data={'files': [], 'metrics': []}),
    dcc.Store(id='persistent-metrics-store', data=[])  # Store for metrics that persist across group changes
])
from dash.dependencies import ALL, State, MATCH
from dash.exceptions import PreventUpdate
import dash

# Store for tracking current mode and metrics across groups
current_mode = {'debug': False}
selected_metrics_store = []

# Callback to update athlete profile based on selected files
@app.callback(
    Output('athlete-profile-container', 'children'),
    [Input({'type': 'file-selector', 'mode': ALL}, 'value'),
     Input('hierarchical-selection-store', 'data'),
     Input('debug-toggle', 'value')],
    prevent_initial_call=False
)
def update_athlete_profile(file_values, hierarchical_data, debug_mode):
    """Update athlete profile based on selected files"""
    is_debug = 'debug' in (debug_mode or [])
    
    # Get selected files based on mode
    if is_debug:
        # Debug mode: use hierarchical selection
        selected_files = hierarchical_data.get('files', [])
    else:
        # Normal mode: use file selector
        selected_files = []
        if file_values:
            for val in file_values:
                if val:
                    selected_files = val
                    break
    
    if not selected_files:
        # Default profile when no files selected
        return html.Div([
            html.Img(
                src='/assets/placeholder-athlete.png',
                style={
                    'width': '80px',
                    'height': '80px',
                    'border-radius': '50%',
                    'object-fit': 'cover',
                    'border': '3px solid #3498db',
                    'margin-bottom': '8px'
                }
            ),
            html.H4("Select an athlete", style={'margin': '3px 0', 'color': '#2c3e50', 'font-size': '16px'}),
            html.P("Choose files to view profile", style={'margin': '0', 'font-size': '14px', 'color': '#7f8c8d'})
        ], style={'text-align': 'center'})
    
    # Get athlete from first selected file
    first_file = selected_files[0]
    athlete_key = get_athlete_from_filename(first_file)
    
    if athlete_key and athlete_key in athlete_profiles:
        profile = athlete_profiles[athlete_key]
        return html.Div([
            html.Img(
                src=f'/assets/{profile["photo"]}',
                style={
                    'width': '80px',
                    'height': '80px',
                    'border-radius': '50%',
                    'object-fit': 'cover',
                    'border': '3px solid #3498db',
                    'margin-bottom': '8px'
                }
            ),
            html.H4(profile['name'], style={'margin': '3px 0', 'color': '#2c3e50', 'font-size': '16px'}),
            html.Div([
                html.Div([
                    html.Strong("Age: ", style={'color': '#34495e'}),
                    html.Span(f"{profile['age']} years", style={'color': '#7f8c8d'})
                ], style={'margin': '2px 0', 'font-size': '14px'}),
                html.Div([
                    html.Strong("Height: ", style={'color': '#34495e'}),
                    html.Span(profile['height'], style={'color': '#7f8c8d'})
                ], style={'margin': '2px 0', 'font-size': '14px'}),
                html.Div([
                    html.Strong("Weight: ", style={'color': '#34495e'}),
                    html.Span(profile['weight'], style={'color': '#7f8c8d'})
                ], style={'margin': '2px 0', 'font-size': '14px'}),
                html.Div([
                    html.Strong("Sex: ", style={'color': '#34495e'}),
                    html.Span(profile['sex'], style={'color': '#7f8c8d'})
                ], style={'margin': '2px 0', 'font-size': '14px'}),
                html.Div([
                    html.Strong("Sport: ", style={'color': '#34495e'}),
                    html.Span(profile['sport'], style={'color': '#7f8c8d'})
                ], style={'margin': '2px 0', 'font-size': '14px'}),
                html.Div([
                    html.Strong("Position: ", style={'color': '#34495e'}),
                    html.Span(profile['position'], style={'color': '#7f8c8d'})
                ], style={'margin': '2px 0', 'font-size': '14px'})
            ])
        ], style={'text-align': 'center'})
    
    # Fallback for unknown athlete
    return html.Div([
        html.Img(
            src='/assets/placeholder-athlete.png',
            style={
                'width': '80px',
                'height': '80px',
                'border-radius': '50%',
                'object-fit': 'cover',
                'border': '3px solid #3498db',
                'margin-bottom': '8px'
            }
        ),
        html.H4("Unknown Athlete", style={'margin': '3px 0', 'color': '#2c3e50', 'font-size': '16px'}),
        html.P("Profile not available", style={'margin': '0', 'font-size': '14px', 'color': '#7f8c8d'})
    ], style={'text-align': 'center'})

# Callback to update file selection UI based on debug mode
@app.callback(
    Output('file-selection-wrapper', 'children'),
    Input('debug-toggle', 'value')
)
def update_file_selection_wrapper(debug_mode):
    """Show/hide file selection based on debug mode"""
    is_debug = 'debug' in (debug_mode or [])
    
    if is_debug:
        # Debug mode: hide file selection entirely
        return []
    else:
        # Normal mode: show file selection with margin for spacing
        return html.Div([
            html.Label("Select Files:"),
            html.Div(id='file-selection-container')
        ], style={
            'margin-bottom': '30px',  # Increased padding between file selection and metrics
            'border': '2px solid #888',
            'borderRadius': '8px',
            'padding': '16px',
            'background': '#fafbfc'
        })

@app.callback(
    Output('file-selection-container', 'children'),
    Input('debug-toggle', 'value')
)
def update_file_selection(debug_mode):
    is_debug = 'debug' in (debug_mode or [])
    current_mode['debug'] = is_debug
    
    if is_debug:
        # Debug mode: no file selection (handled by hierarchical dropdowns)
        return []
    else:
        # Normal mode: Checklist
        return dcc.Checklist(
            id={'type': 'file-selector', 'mode': 'checklist'},
            options=[{'label': mapping[f], 'value': f} for f in sto_files],
            value=[],
            inline=True,
            style={'margin-top': '10px'}
        )

# Callback to update metrics selection UI based on debug mode
@app.callback(
    [Output('metrics-selection-container', 'children'),
     Output('metrics-container-box', 'style')],
    Input('debug-toggle', 'value')
)
def update_metrics_selection(debug_mode):
    is_debug = 'debug' in (debug_mode or [])
    
    # Update container style based on debug mode
    if is_debug:
        container_style = {
            'border': 'none',  # Remove border since we're adding separate containers
            'borderRadius': '0px',
            'padding': '0px',
            'background': 'transparent',
            'width': '100%'
        }
    else:
        container_style = {
            'border': '2px solid #888',
            'borderRadius': '8px',
            'padding': '16px',
            'background': '#f5f7fa'
        }
    
    # Always create hierarchical dropdowns to avoid callback errors, but hide them when not in debug mode
    hierarchical_dropdowns = html.Div([
        html.Label("Hierarchical Selection:", style={'margin-bottom': '15px', 'font-weight': 'bold', 'font-size': '16px'}),
        
        # Layer 1: Athlete Selection
        html.Div([
            html.Label("1. Select Athlete:", style={'font-weight': 'bold', 'margin-bottom': '5px', 'color': '#2c3e50'}),
            dcc.Dropdown(
                id={'type': 'hierarchical-dropdown', 'layer': 'athlete'},
                options=[{'label': athlete, 'value': athlete} for athlete in get_athletes_from_files()],
                value=None,
                placeholder="Choose an athlete...",
                style={'margin-bottom': '15px'}
            )
        ], style={'margin-bottom': '15px'}),
        
        # Layer 2: Exercise Selection
        html.Div([
            html.Label("2. Select Exercise:", style={'font-weight': 'bold', 'margin-bottom': '5px', 'color': '#2c3e50'}),
            dcc.Dropdown(
                id={'type': 'hierarchical-dropdown', 'layer': 'exercise'},
                options=[],
                value=None,
                placeholder="First select an athlete...",
                disabled=True,
                style={'margin-bottom': '15px'}
            )
        ], style={'margin-bottom': '15px'}),
        
        # Layer 3: Attempt Number Selection
        html.Div([
            html.Label("3. Select Attempt Number:", style={'font-weight': 'bold', 'margin-bottom': '5px', 'color': '#2c3e50'}),
            dcc.Dropdown(
                id={'type': 'hierarchical-dropdown', 'layer': 'attempt'},
                options=[],
                value=None,
                placeholder="First select exercise...",
                disabled=True,
                style={'margin-bottom': '15px'}
            )
        ], style={'margin-bottom': '15px'}),
        
        # Layer 4: Metric Group Selection
        html.Div([
            html.Label("4. Select Metric Group:", style={'font-weight': 'bold', 'margin-bottom': '5px', 'color': '#2c3e50'}),
            dcc.Dropdown(
                id={'type': 'hierarchical-dropdown', 'layer': 'group'},
                options=[{'label': group, 'value': group} for group in metric_groups.keys() if metric_groups[group]],
                value=None,
                placeholder="First select attempt...",
                disabled=True,
                style={'margin-bottom': '15px'}
            )
        ], style={'margin-bottom': '15px'}),
        
        # Layer 5: Exact Metric Selection
        html.Div([
            html.Label("5. Select Metrics:", style={'font-weight': 'bold', 'margin-bottom': '5px', 'color': '#2c3e50'}),
            dcc.Dropdown(
                id={'type': 'hierarchical-dropdown', 'layer': 'metrics'},
                options=[],
                value=[],
                multi=True,
                placeholder="First select metric group...",
                disabled=True,
                style={'margin-bottom': '15px'}
            )
        ], style={'margin-bottom': '15px'})
    ], style={'width': '50%', 'margin-right': '15px'})
    
    # Always create selected metrics display to avoid callback errors, but hide when not in debug mode  
    selected_metrics_display = html.Div([
        html.Div([
            html.Label("Selected Metrics:", style={'font-weight': 'bold', 'margin-bottom': '10px', 'color': '#2c3e50', 'font-size': '16px', 'flex': '1'}),
            html.Button(
                "Clear All",
                id={'type': 'clear-all-btn', 'component': 'metrics'},
                style={
                    'background': '#e74c3c',
                    'color': 'white',
                    'border': 'none',
                    'border-radius': '4px',
                    'padding': '6px 12px',
                    'font-size': '12px',
                    'cursor': 'pointer',
                    'font-weight': 'bold'
                },
                title="Remove all selected metrics"
            )
        ], style={'display': 'flex', 'align-items': 'center', 'justify-content': 'space-between', 'margin-bottom': '10px'}),
        html.Div(id='selected-metrics-display', children=[
            html.P("No metrics selected yet", style={'color': '#7f8c8d', 'font-style': 'italic', 'margin': '10px 0'})
        ], style={
            'border': '2px dashed #3498db',
            'border-radius': '8px',
            'padding': '15px',
            'background': '#f8f9fa',
            'min-height': '150px',
            'max-height': '300px',
            'overflow-y': 'auto'
        })
    ], style={'width': '50%'})

    # Always create video analysis section to avoid callback errors, but hide when not in debug mode
    video_analysis_section = html.Div([
        html.Label("Video Analysis:", style={'font-weight': 'bold', 'margin-bottom': '15px', 'color': '#e74c3c', 'font-size': '18px'}),
        html.Div([
            html.Video(
                id='video-player',
                src='',  # Start with no source
                controls=True,
                autoPlay=True,
                loop=True,
                muted=True,  # Required for autoplay in many browsers
                style={
                    'width': '100%',
                    'height': '350px',
                    'border': '2px solid #e74c3c',
                    'borderRadius': '8px',
                    'object-fit': 'cover'
                }
            )
        ], style={'display': 'flex', 'flex-direction': 'column', 'align-items': 'center'})
    ])

    if is_debug:
        # Debug mode: Show hierarchical dropdowns and selected metrics display in one container, video analysis in separate container (side by side)
        hierarchical_metrics_container = html.Div([
            hierarchical_dropdowns,
            selected_metrics_display
        ], style={
            'display': 'flex', 
            'width': '48%',
            'border': '2px solid #888',
            'borderRadius': '8px',
            'padding': '16px',
            'background': '#f5f7fa',
            'margin-right': '20px'
        })
        
        video_analysis_container = html.Div([
            video_analysis_section
        ], style={
            'width': '48%',
            'border': '2px solid #e74c3c',
            'borderRadius': '8px',
            'padding': '16px',
            'background': '#fef7f7'
        })
        
        # Wrap both containers in a horizontal flex container
        content = html.Div([
            hierarchical_metrics_container,
            video_analysis_container
        ], style={'display': 'flex', 'width': '100%'})
    else:
        # Normal mode: Grouped checklists + hidden hierarchical dropdowns to avoid callback errors
        # First row: first 5 metric groups
        first_row = html.Div([
            *[
                html.Div([
                    html.Label(f"{group} Metrics:"),
                    dcc.Checklist(
                        id={'type': 'metrics-selector', 'mode': 'checklist', 'group': group.lower()},
                        options=[{'label': m, 'value': m} for m in metric_groups[group]],
                        value=[],
                        inline=True
                    ),
                ], style={'margin-right': '40px', 'minWidth': '200px'})
                for group in list(metric_groups.keys())[:5]
            ]
        ], style={'display': 'flex', 'flex-direction': 'row', 'align-items': 'flex-start', 'margin-bottom': '20px'})
        
        # Second row: next 6 metric groups
        second_row = html.Div([
            *[
                html.Div([
                    html.Label(f"{group} Metrics:"),
                    dcc.Checklist(
                        id={'type': 'metrics-selector', 'mode': 'checklist', 'group': group.lower()},
                        options=[{'label': m, 'value': m} for m in metric_groups[group]],
                        value=[],
                        inline=True
                    ),
                ], style={'margin-right': '40px', 'minWidth': '200px'})
                for group in list(metric_groups.keys())[5:11]
            ]
        ], style={'display': 'flex', 'flex-direction': 'row', 'align-items': 'flex-start'})
        
        # Include hidden hierarchical dropdowns to avoid callback errors
        hidden_hierarchical = html.Div([
            hierarchical_dropdowns,
            selected_metrics_display,
            video_analysis_section
        ], style={'display': 'none'})
        
        content = [first_row, second_row, hidden_hierarchical]
    
    return content, container_style

@app.callback(
    Output('persistent-metrics-store', 'data', allow_duplicate=True),
    [Input('debug-toggle', 'value'),
     Input({'type': 'remove-metric-btn', 'metric': ALL}, 'n_clicks')],
    [State('persistent-metrics-store', 'data')],
    prevent_initial_call=True
)
def update_persistent_metrics_from_display(debug_mode, remove_clicks, persistent_metrics):
    """Update persistent metrics when remove buttons are clicked"""
    is_debug = 'debug' in (debug_mode or [])
    
    if not is_debug:
        # Not in debug mode, don't update
        raise PreventUpdate
    
    # Initialize persistent metrics if None
    if persistent_metrics is None:
        persistent_metrics = []
    
    # Get the triggered context
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate
    
    trigger_id = ctx.triggered[0]['prop_id']
    
    # Handle remove button clicks
    if 'remove-metric-btn' in trigger_id and any(remove_clicks):
        # Extract the metric name from the triggered ID
        triggered_component = ctx.triggered[0]['prop_id']
        if '"metric":"' in triggered_component:
            metric_to_remove = triggered_component.split('"metric":"')[1].split('"')[0]
            # Remove the metric from persistent store
            persistent_metrics = [m for m in persistent_metrics if m != metric_to_remove]
            return persistent_metrics
    
    raise PreventUpdate

# Callback to update the selected metrics display - only when in debug mode
@app.callback(
    Output('selected-metrics-display', 'children'),
    [Input('persistent-metrics-store', 'data'),
     Input('debug-toggle', 'value')],
    prevent_initial_call=True
)
def update_selected_metrics_display_content(persistent_metrics, debug_mode):
    """Update the visual display of selected metrics"""
    is_debug = 'debug' in (debug_mode or [])
    
    if not is_debug:
        # Component doesn't exist when not in debug mode
        raise PreventUpdate
    
    # Initialize persistent metrics if None
    if not persistent_metrics:
        return [html.P("No metrics selected yet", style={'color': '#7f8c8d', 'font-style': 'italic', 'margin': '10px 0'})]
    
    # Create a list of selected metrics with styling and remove buttons
    metric_items = []
    for i, metric in enumerate(persistent_metrics):
        # Find which group this metric belongs to for better labeling
        metric_group = None
        for group_name, group_metrics in metric_groups.items():
            if metric in group_metrics:
                metric_group = group_name
                break
        
        metric_items.append(
            html.Div([
                html.Div([
                    html.Span(f"{i+1}. ", style={'font-weight': 'bold', 'color': '#3498db', 'margin-right': '5px'}),
                    html.Span(metric, style={'color': '#2c3e50', 'font-size': '14px', 'flex': '1'}),
                    html.Span(f"({metric_group})", style={'font-size': '12px', 'color': '#666', 'margin-left': '8px'}) if metric_group else None,
                ], style={'display': 'flex', 'align-items': 'center', 'flex': '1'}),
                html.Button(
                    "×",
                    id={'type': 'remove-metric-btn', 'metric': metric},
                    style={
                        'background': '#e74c3c',
                        'color': 'white',
                        'border': 'none',
                        'border-radius': '50%',
                        'width': '20px',
                        'height': '20px',
                        'font-size': '14px',
                        'cursor': 'pointer',
                        'display': 'flex',
                        'align-items': 'center',
                        'justify-content': 'center',
                        'margin-left': '8px'
                    },
                    title=f"Remove {metric}"
                )
            ], style={
                'padding': '8px 12px',
                'margin': '4px 0',
                'background': '#e8f4f8',
                'border': '1px solid #3498db',
                'border-radius': '4px',
                'transition': 'all 0.2s ease',
                'display': 'flex',
                'align-items': 'center',
                'justify-content': 'space-between'
            })
        )
    
    return metric_items

# Separate callback for handling metrics dropdown changes
@app.callback(
    Output('persistent-metrics-store', 'data', allow_duplicate=True),
    [Input({'type': 'hierarchical-dropdown', 'layer': 'metrics'}, 'value'),
     Input('debug-toggle', 'value')],
    [State('persistent-metrics-store', 'data')],
    prevent_initial_call=True
)
def update_persistent_metrics_from_dropdown(dropdown_metrics, debug_mode, persistent_metrics):
    """Update persistent metrics when dropdown selection changes"""
    is_debug = 'debug' in (debug_mode or [])
    
    # Only run when in debug mode (when components exist)
    if not is_debug:
        raise PreventUpdate
    
    # Initialize persistent metrics if None
    if persistent_metrics is None:
        persistent_metrics = []
    
    # Add new metrics from dropdown to persistent store
    if dropdown_metrics:
        for metric in dropdown_metrics:
            if metric not in persistent_metrics:
                persistent_metrics.append(metric)
    
    return persistent_metrics

# Callbacks for hierarchical dropdown system (debug mode only)
# Use a simpler approach with separate callbacks for each layer

# Clear All button callback - using pattern matching to avoid component existence issues
@app.callback(
    [Output({'type': 'hierarchical-dropdown', 'layer': 'metrics'}, 'value', allow_duplicate=True),
     Output('persistent-metrics-store', 'data', allow_duplicate=True)],
    [Input({'type': 'clear-all-btn', 'component': ALL}, 'n_clicks')],
    prevent_initial_call=True
)
def clear_all_metrics_pattern(n_clicks_list):
    """Clear all selected metrics when Clear All button is clicked"""
    if any(n_clicks_list) and any(click for click in n_clicks_list if click):
        return [], []
    raise PreventUpdate

@app.callback(
    [Output({'type': 'hierarchical-dropdown', 'layer': 'exercise'}, 'options'),
     Output({'type': 'hierarchical-dropdown', 'layer': 'exercise'}, 'disabled'),
     Output({'type': 'hierarchical-dropdown', 'layer': 'exercise'}, 'placeholder'),
     Output({'type': 'hierarchical-dropdown', 'layer': 'exercise'}, 'value'),
     # Reset lower levels when athlete changes
     Output({'type': 'hierarchical-dropdown', 'layer': 'attempt'}, 'value', allow_duplicate=True),
     Output({'type': 'hierarchical-dropdown', 'layer': 'group'}, 'value', allow_duplicate=True),
     Output({'type': 'hierarchical-dropdown', 'layer': 'metrics'}, 'value', allow_duplicate=True)],
    [Input({'type': 'hierarchical-dropdown', 'layer': 'athlete'}, 'value'),
     Input('debug-toggle', 'value')],
    prevent_initial_call=True
)
def update_exercise_dropdown(selected_athlete, debug_mode):
    """Update exercise dropdown based on selected athlete and reset all lower levels"""
    is_debug = 'debug' in (debug_mode or [])
    
    # Only run when in debug mode (when components exist)
    if not is_debug:
        raise PreventUpdate
    
    try:
        if not selected_athlete:
            return [], True, "First select an athlete...", None, None, None, []
        
        exercises = get_exercises_for_athlete(selected_athlete)
        options = [{'label': ex.title(), 'value': ex} for ex in exercises]
        
        # Reset all lower levels when athlete changes
        return options, False, "Choose an exercise...", None, None, None, []
    except Exception:
        raise PreventUpdate

@app.callback(
    [Output({'type': 'hierarchical-dropdown', 'layer': 'attempt'}, 'options'),
     Output({'type': 'hierarchical-dropdown', 'layer': 'attempt'}, 'disabled'),
     Output({'type': 'hierarchical-dropdown', 'layer': 'attempt'}, 'placeholder'),
     Output({'type': 'hierarchical-dropdown', 'layer': 'attempt'}, 'value'),
     # Reset lower levels when exercise changes
     Output({'type': 'hierarchical-dropdown', 'layer': 'group'}, 'value', allow_duplicate=True),
     Output({'type': 'hierarchical-dropdown', 'layer': 'metrics'}, 'value', allow_duplicate=True)],
    [Input({'type': 'hierarchical-dropdown', 'layer': 'athlete'}, 'value'),
     Input({'type': 'hierarchical-dropdown', 'layer': 'exercise'}, 'value'),
     Input('debug-toggle', 'value')],
    prevent_initial_call=True
)
def update_attempt_dropdown(selected_athlete, selected_exercise, debug_mode):
    """Update attempt dropdown based on selected athlete and exercise and reset lower levels"""
    is_debug = 'debug' in (debug_mode or [])
    
    # Only run when in debug mode (when components exist)
    if not is_debug:
        raise PreventUpdate
    
    try:
        if not selected_athlete or not selected_exercise:
            return [], True, "First select athlete and exercise...", None, None, []
        
        attempts = get_attempts_for_athlete_exercise(selected_athlete, selected_exercise)
        options = [{'label': f"Attempt {att}", 'value': att} for att in attempts]
        
        # Reset lower levels when exercise changes
        return options, False, "Choose an attempt...", None, None, []
    except Exception:
        raise PreventUpdate

@app.callback(
    [Output({'type': 'hierarchical-dropdown', 'layer': 'group'}, 'disabled'),
     Output({'type': 'hierarchical-dropdown', 'layer': 'group'}, 'placeholder'),
     Output({'type': 'hierarchical-dropdown', 'layer': 'group'}, 'value'),
     # Reset metrics when attempt changes
     Output({'type': 'hierarchical-dropdown', 'layer': 'metrics'}, 'value', allow_duplicate=True)],
    [Input({'type': 'hierarchical-dropdown', 'layer': 'attempt'}, 'value'),
     Input('debug-toggle', 'value')],
    prevent_initial_call=True
)
def update_group_dropdown(selected_attempt, debug_mode):
    """Update metric group dropdown based on selected attempt and reset metrics"""
    is_debug = 'debug' in (debug_mode or [])
    
    # Only run when in debug mode (when components exist)
    if not is_debug:
        raise PreventUpdate
    
    try:
        if not selected_attempt:
            return True, "First select attempt...", None, []
        
        # Reset metrics when attempt changes
        return False, "Choose a metric group...", None, []
    except Exception:
        raise PreventUpdate

@app.callback(
    [Output({'type': 'hierarchical-dropdown', 'layer': 'metrics'}, 'options'),
     Output({'type': 'hierarchical-dropdown', 'layer': 'metrics'}, 'disabled'),
     Output({'type': 'hierarchical-dropdown', 'layer': 'metrics'}, 'placeholder'),
     Output({'type': 'hierarchical-dropdown', 'layer': 'metrics'}, 'value')],
    [Input({'type': 'hierarchical-dropdown', 'layer': 'group'}, 'value'),
     Input('debug-toggle', 'value')],
    [State({'type': 'hierarchical-dropdown', 'layer': 'metrics'}, 'value')],
    prevent_initial_call=True
)
def update_metrics_dropdown(selected_group, debug_mode, current_metrics):
    """Update exact metrics dropdown based on selected metric group"""
    is_debug = 'debug' in (debug_mode or [])
    
    # Only run when in debug mode (when components exist)
    if not is_debug:
        raise PreventUpdate
    
    try:
        if not selected_group or selected_group not in metric_groups:
            # If no group selected, show currently selected metrics as disabled options
            if current_metrics:
                options = [{'label': f"{metric} (from previous group)", 'value': metric} for metric in current_metrics]
                return options, True, "First select metric group...", current_metrics
            return [], True, "First select metric group...", []
        
        # Get metrics from the current group
        current_group_metrics = metric_groups[selected_group]
        
        # Create options: current group metrics + any previously selected metrics not in current group
        options = []
        all_option_values = set()
        
        # Add current group metrics
        for metric in current_group_metrics:
            options.append({'label': metric, 'value': metric})
            all_option_values.add(metric)
        
        # Add previously selected metrics that aren't in the current group
        if current_metrics:
            for metric in current_metrics:
                if metric not in all_option_values:
                    # Find which group this metric belongs to
                    metric_group = None
                    for group_name, group_metrics in metric_groups.items():
                        if metric in group_metrics:
                            metric_group = group_name
                            break
                    
                    label = f"{metric} (from {metric_group})" if metric_group else f"{metric} (other group)"
                    options.append({'label': label, 'value': metric})
                    all_option_values.add(metric)
        
        # Reset the dropdown value to empty (visual reset) but preserve selected metrics in the panel
        # The preserved metrics will be maintained by the selected-metrics-display
        return options, False, "Choose specific metrics...", []
    except Exception:
        raise PreventUpdate

@app.callback(
    Output('hierarchical-selection-store', 'data', allow_duplicate=True),
    [Input({'type': 'hierarchical-dropdown', 'layer': 'athlete'}, 'value'),
     Input({'type': 'hierarchical-dropdown', 'layer': 'exercise'}, 'value'),
     Input({'type': 'hierarchical-dropdown', 'layer': 'attempt'}, 'value'),
     Input('persistent-metrics-store', 'data'),
     Input('debug-toggle', 'value')],
    prevent_initial_call=True
)
def update_hierarchical_store(selected_athlete, selected_exercise, selected_attempt, persistent_metrics, debug_mode):
    """Update the store with hierarchical selections using all 5 levels"""
    is_debug = 'debug' in (debug_mode or [])
    
    # Only run when in debug mode (when components exist)
    if not is_debug:
        raise PreventUpdate
    
    try:
        if not all([selected_athlete, selected_exercise, selected_attempt]):
            return {'files': [], 'metrics': []}
        
        # Construct the specific filename using athlete + exercise + attempt
        filename = construct_filename_from_hierarchy(selected_athlete, selected_exercise, selected_attempt)
        
        if filename:
            return {
                'files': [filename],
                'metrics': persistent_metrics if persistent_metrics else []
            }
        else:
            return {'files': [], 'metrics': []}
    except Exception:
        return {'files': [], 'metrics': []}

# Separate callback to handle store updates when not in debug mode
@app.callback(
    Output('hierarchical-selection-store', 'data', allow_duplicate=True),
    Input('debug-toggle', 'value'),
    prevent_initial_call=True
)
def reset_hierarchical_store_on_mode_change(debug_mode):
    """Reset store when switching modes"""
    is_debug = 'debug' in (debug_mode or [])
    if not is_debug:
        return {'files': [], 'metrics': []}
    raise PreventUpdate

# Single unified callback using pattern-matching
@app.callback(
    Output('kinematic-plot', 'figure'),
    [Input('debug-toggle', 'value'),
     Input({'type': 'file-selector', 'mode': ALL}, 'value'),
     Input({'type': 'metrics-selector', 'mode': 'checklist', 'group': ALL}, 'value'),
     Input('hierarchical-selection-store', 'data')],
    prevent_initial_call=False
)
def update_plot_unified(debug_mode, file_values, checklist_metrics_values, hierarchical_data):
    """Unified plot update callback using pattern-matching"""
    is_debug = 'debug' in (debug_mode or [])
    
    # Get selected files and metrics based on mode
    if is_debug:
        # Debug mode: use hierarchical selection
        selected_files = hierarchical_data.get('files', [])
        selected_metrics = hierarchical_data.get('metrics', [])
    else:
        # Normal mode: use existing checklist system
        selected_files = []
        if file_values:
            for val in file_values:
                if val:
                    selected_files = val
                    break
        
        selected_metrics = []
        if checklist_metrics_values:
            for group_metrics in checklist_metrics_values:
                if group_metrics:
                    selected_metrics.extend(group_metrics)
    
    # Create the plot
    fig = go.Figure()
    for fname in selected_files:
        if fname in dfs:
            df = dfs[fname]
            for metric in selected_metrics:
                if metric in df.columns:
                    fig.add_trace(go.Scatter(
                        x=df['time'],
                        y=df[metric],
                        mode='lines',
                        name=f"{metric} - {fname}"
                    ))
    
    # Add debug mode indicator to title
    title_suffix = " (Debug Mode - Hierarchical)" if is_debug else ""
    fig.update_layout(
        xaxis_title="Time (s)",
        yaxis_title="Value",
        title=f"Kinematic Curves{title_suffix}",
        legend_title="Metric - File"
    )
    return fig

# Callback for saving notes
@app.callback(
    Output('save-status', 'children'),
    Input('save-notes-btn', 'n_clicks'),
    Input('key-takeaways-textarea', 'value'),
    Input('observations-textarea', 'value'),
    Input('recommendations-textarea', 'value'),
    prevent_initial_call=True
)
def save_notes(n_clicks, key_takeaways_content, observations_content, recommendations_content):
    if n_clicks > 0 and (key_takeaways_content or observations_content or recommendations_content):
        try:
            # Save notes to a file with timestamp
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"analysis_notes_{timestamp}.txt"
            
            with open(filename, 'w') as f:
                f.write(f"Analysis Notes - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*60 + "\n\n")
                
                # Key Takeaways section
                f.write("KEY TAKEAWAYS:\n")
                f.write("-" * 15 + "\n")
                f.write(key_takeaways_content if key_takeaways_content else "(No key takeaways recorded)\n")
                f.write("\n\n")
                
                # Observations section
                f.write("OBSERVATIONS:\n")
                f.write("-" * 20 + "\n")
                f.write(observations_content if observations_content else "(No observations recorded)\n")
                f.write("\n\n")
                
                # Recommendations section
                f.write("RECOMMENDED MOVEMENTS:\n")
                f.write("-" * 25 + "\n")
                f.write(recommendations_content if recommendations_content else "(No recommendations recorded)\n")
            
            return html.Div([
                html.Span("✓ Notes saved to: ", style={'color': 'green'}),
                html.Code(filename, style={'background': '#f0f0f0', 'padding': '2px 4px'})
            ])
        except Exception as e:
            return html.Div(f"Error saving notes: {str(e)}", style={'color': 'red'})
    
    return ""

# --- VIDEO PLAYER CALLBACK ---
@app.callback(
    Output('video-player', 'src'),
    [Input({'type': 'hierarchical-dropdown', 'layer': 'athlete'}, 'value'),
     Input({'type': 'hierarchical-dropdown', 'layer': 'exercise'}, 'value'),
     Input({'type': 'hierarchical-dropdown', 'layer': 'attempt'}, 'value'),
     Input('debug-toggle', 'value')]
)
def update_video_source(selected_athlete, selected_exercise, selected_attempt, debug_mode):
    """Update video source based on hierarchical selections"""
    is_debug = 'debug' in (debug_mode or [])
    
    # Only run when in debug mode
    if not is_debug:
        return ''
    
    # Check if all three selections are made
    if not all([selected_athlete, selected_exercise, selected_attempt]):
        return ''  # Return empty source to show blank video player
    
    try:
        # Map athlete to file prefix
        athlete_prefix = {
            'Gabby': 'G',
            'Hannah': 'H', 
            'Aaron': 'A'
        }.get(selected_athlete)
        
        if not athlete_prefix:
            return ''
        
        # Construct video filename based on the exact pattern: 0627{athlete_prefix}{attempt}{exercise}.webm
        # Format: 0627G1squat.webm
        video_filename = f"0627{athlete_prefix}{selected_attempt}{selected_exercise}.webm"
        video_path = f"/assets/videos/{video_filename}"
        
        return video_path
        
    except Exception:
        return ''

if __name__ == "__main__":
    # Uncomment the following lines to run on a server or cloud platform
    # port = int(os.environ.get("PORT", 8050))
    # app.run(debug=True, host="0.0.0.0", port=port)  # Run the app on all interfaces

    # local run
    app.run(debug=True)