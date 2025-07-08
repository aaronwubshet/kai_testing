# -*- coding: utf-8 -*-
"""
Layout components for the Kinematic Dashboard
Contains all UI layout definitions and component structures
"""

from dash import dcc, html
from config import (
    APP_TITLE, athlete_profiles, file_mapping, sto_files, 
    metric_groups, COLORS, COMPONENT_IDS
)
from utils import hierarchical_selector


class HeaderLayout:
    """Header section with title and debug toggle"""
    
    @staticmethod
    def create():
        return html.Div([
            html.H2(APP_TITLE, style={'margin': 0, 'flex': '1'}),
            # Debug mode toggle in top right
            html.Div([
                html.Label("Debug Mode:", style={'margin-right': '8px', 'font-weight': 'bold'}),
                dcc.Checklist(
                    id=COMPONENT_IDS['debug_toggle'],
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
                'border': f'1px solid {COLORS["primary"]}',
                'border-radius': '5px'
            })
        ], style={
            'display': 'flex', 
            'justify-content': 'space-between', 
            'align-items': 'center',
            'margin-bottom': '20px'
        })


class AthleteProfileLayout:
    """Athlete profile display component"""
    
    @staticmethod
    def create_default():
        """Create default profile when no athlete is selected"""
        return html.Div([
            html.Img(
                src='/assets/placeholder-athlete.png',
                style={
                    'width': '80px',
                    'height': '80px',
                    'border-radius': '50%',
                    'object-fit': 'cover',
                    'border': f'3px solid {COLORS["primary"]}',
                    'margin-bottom': '8px'
                }
            ),
            html.H4("Select an athlete", style={'margin': '3px 0', 'color': COLORS['secondary'], 'font-size': '16px'}),
            html.P("Choose files to view profile", style={'margin': '0', 'font-size': '14px', 'color': COLORS['muted']})
        ], style={'text-align': 'center'})
    
    @staticmethod
    def create_container():
        """Create the athlete profile container"""
        return html.Div([
            html.Div(id=COMPONENT_IDS['athlete_profile'], children=[
                AthleteProfileLayout.create_default()
            ])
        ], style={
            'flex': '0 0 250px',
            'margin-right': '20px',
            'border': f'2px solid {COLORS["primary"]}',
            'border-radius': '12px',
            'padding': '12px',
            'background': 'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)',
            'box-shadow': f'0 4px 6px rgba(52, 152, 219, 0.1)',
            'min-height': '200px'
        })


class HierarchicalDropdownsLayout:
    """Hierarchical dropdown system for debug mode"""
    
    @staticmethod
    def create():
        return html.Div([
            html.Label("Hierarchical Selection:", style={'margin-bottom': '15px', 'font-weight': 'bold', 'font-size': '16px'}),
            
            # Layer 1: Athlete Selection
            html.Div([
                html.Label("1. Select Athlete:", style={'font-weight': 'bold', 'margin-bottom': '5px', 'color': COLORS['secondary']}),
                dcc.Dropdown(
                    id={'type': 'hierarchical-dropdown', 'layer': 'athlete'},
                    options=[{'label': athlete, 'value': athlete} for athlete in hierarchical_selector.get_athletes_from_files()],
                    value=None,
                    placeholder="Choose an athlete...",
                    style={'margin-bottom': '15px'}
                )
            ], style={'margin-bottom': '15px'}),
            
            # Layer 2: Exercise Selection
            html.Div([
                html.Label("2. Select Exercise:", style={'font-weight': 'bold', 'margin-bottom': '5px', 'color': COLORS['secondary']}),
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
                html.Label("3. Select Attempt Number:", style={'font-weight': 'bold', 'margin-bottom': '5px', 'color': COLORS['secondary']}),
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
                html.Label("4. Select Metric Group:", style={'font-weight': 'bold', 'margin-bottom': '5px', 'color': COLORS['secondary']}),
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
                html.Label("5. Select Metrics:", style={'font-weight': 'bold', 'margin-bottom': '5px', 'color': COLORS['secondary']}),
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


class SelectedMetricsLayout:
    """Selected metrics display component"""
    
    @staticmethod
    def create():
        return html.Div([
            html.Div([
                html.Label("Selected Metrics:", style={'font-weight': 'bold', 'margin-bottom': '10px', 'color': COLORS['secondary'], 'font-size': '16px', 'flex': '1'}),
                html.Button(
                    "Clear All",
                    id={'type': 'clear-all-btn', 'component': 'metrics'},
                    style={
                        'background': COLORS['danger'],
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
                html.P("No metrics selected yet", style={'color': COLORS['muted'], 'font-style': 'italic', 'margin': '10px 0'})
            ], style={
                'border': f'2px dashed {COLORS["primary"]}',
                'border-radius': '8px',
                'padding': '15px',
                'background': COLORS['light'],
                'min-height': '150px',
                'max-height': '300px',
                'overflow-y': 'auto'
            })
        ], style={'width': '50%'})


class VideoAnalysisLayout:
    """Video analysis component"""
    
    @staticmethod
    def create():
        return html.Div([
            html.Label("Video Analysis:", style={'font-weight': 'bold', 'margin-bottom': '15px', 'color': COLORS['danger'], 'font-size': '18px'}),
            html.Div([
                html.Video(
                    id=COMPONENT_IDS['video_player'],
                    src='',  # Start with no source
                    controls=True,
                    autoPlay=True,
                    loop=True,
                    muted=True,  # Required for autoplay in many browsers
                    style={
                        'width': '100%',
                        'height': '350px',
                        'border': f'2px solid {COLORS["danger"]}',
                        'borderRadius': '8px',
                        'object-fit': 'cover'
                    }
                )
            ], style={'display': 'flex', 'flex-direction': 'column', 'align-items': 'center'})
        ])


class FileSelectionLayout:
    """File selection component for normal mode"""
    
    @staticmethod
    def create_wrapper():
        return html.Div(id='file-selection-wrapper')
    
    @staticmethod
    def create_normal_mode():
        return html.Div([
            html.Label("Select Files:"),
            html.Div(id=COMPONENT_IDS['file_selection'])
        ], style={
            'margin-bottom': '30px',
            'border': '2px solid #888',
            'borderRadius': '8px',
            'padding': '16px',
            'background': '#fafbfc'
        })
    
    @staticmethod
    def create_checklist():
        return dcc.Checklist(
            id={'type': 'file-selector', 'mode': 'checklist'},
            options=[{'label': file_mapping[f], 'value': f} for f in sto_files],
            value=[],
            inline=True,
            style={'margin-top': '10px'}
        )


class MetricsSelectionLayout:
    """Metrics selection layout for normal mode"""
    
    @staticmethod
    def create_normal_mode():
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
        
        return [first_row, second_row]


class NotesLayout:
    """Notes and analysis section"""
    
    @staticmethod
    def create():
        return html.Div([
            # Key Takeaways section
            html.Div([
                html.Label("Key Takeaways:", style={'font-weight': 'bold', 'margin-bottom': '8px', 'color': COLORS['purple']}),
                dcc.Textarea(
                    id='key-takeaways-textarea',
                    placeholder="Summarize key takeaways...\n\n• Primary insights\n• Critical findings\n• Main conclusions\n• Important highlights",
                    style={
                        'width': '100%',
                        'height': '180px',
                        'padding': '12px',
                        'border': f'2px solid {COLORS["purple"]}',
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
                html.Label("Observations:", style={'font-weight': 'bold', 'margin-bottom': '8px', 'color': COLORS['secondary']}),
                dcc.Textarea(
                    id='observations-textarea',
                    placeholder="Record your observations here...\n\n• Movement patterns\n• Key findings\n• Notable biomechanics\n• Data insights",
                    style={
                        'width': '100%',
                        'height': '180px',
                        'padding': '12px',
                        'border': f'2px solid {COLORS["primary"]}',
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
                html.Label("Recommended Movements:", style={'font-weight': 'bold', 'margin-bottom': '8px', 'color': COLORS['success']}),
                dcc.Textarea(
                    id='recommendations-textarea',
                    placeholder="Document movement recommendations...\n\n• Corrective exercises\n• Training suggestions\n• Technical improvements\n• Follow-up actions",
                    style={
                        'width': '100%',
                        'height': '180px',
                        'padding': '12px',
                        'border': f'2px solid {COLORS["success"]}',
                        'borderRadius': '8px',
                        'resize': 'vertical',
                        'font-family': 'Arial, sans-serif',
                        'font-size': '14px',
                        'line-height': '1.5'
                    },
                    value=""
                ),
            ], style={'margin-bottom': '15px'}),
            
            # Save and Download buttons
            html.Div([
                html.Button(
                    "Save Notes (Local)",
                    id="save-notes-btn",
                    n_clicks=0,
                    style={
                        'background-color': '#007bff',
                        'color': 'white',
                        'border': 'none',
                        'padding': '10px 20px',
                        'border-radius': '5px',
                        'cursor': 'pointer',
                        'width': '48%',
                        'font-weight': 'bold',
                        'margin-right': '4%'
                    }
                ),
                html.A(
                    html.Button(
                        "Download Notes",
                        id="download-notes-btn",
                        n_clicks=0,
                        style={
                            'background-color': '#28a745',
                            'color': 'white',
                            'border': 'none',
                            'padding': '10px 20px',
                            'border-radius': '5px',
                            'cursor': 'pointer',
                            'width': '100%',
                            'font-weight': 'bold'
                        }
                    ),
                    id="download-link",
                    download="analysis_notes.txt",
                    href="",
                    target="_blank",
                    style={'width': '48%', 'display': 'inline-block'}
                )
            ], style={'display': 'flex', 'width': '100%', 'margin-bottom': '10px'}),
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


class MainLayout:
    """Main application layout"""
    
    @staticmethod
    def create():
        return html.Div([
            # Header
            HeaderLayout.create(),
            
            # Top section with athlete profile and controls
            html.Div([
                # Left side: Athlete Profile
                AthleteProfileLayout.create_container(),
                
                # Right side: Controls
                html.Div([
                    # File selection container (only shown in normal mode)
                    FileSelectionLayout.create_wrapper(),
                    
                    # Box around metrics selection (dynamic based on debug mode)
                    html.Div([
                        html.Div(id=COMPONENT_IDS['metrics_container'])
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
                    dcc.Graph(id=COMPONENT_IDS['kinematic_plot'])
                ], style={'flex': '2', 'margin-right': '20px'}),
                
                # Right side: Notes
                NotesLayout.create()
            ], style={'display': 'flex', 'flex-direction': 'row'}),
            
            # Hidden components to store data (always present)
            dcc.Store(id=COMPONENT_IDS['hierarchical_store'], data={'files': [], 'metrics': []}),
            dcc.Store(id=COMPONENT_IDS['metrics_store'], data=[])  # Store for metrics that persist across group changes
        ])
