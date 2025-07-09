# -*- coding: utf-8 -*-
"""
Simplified Callbacks for the Kinematic Dashboard
Hierarchical dropdown interface only
"""

from dash import Input, Output, State, html, callback_context
from dash.exceptions import PreventUpdate
import dash
import plotly.graph_objs as go

from config import (
    athlete_profiles, metric_groups, COMPONENT_IDS, COLORS
)
from utils import (
    data_processor, hierarchical_selector, notes_manager, 
    FileAnalyzer
)
from layout import AthleteProfileLayout


class AthleteProfileCallbacks:
    """Callbacks related to athlete profile management"""
    
    @staticmethod
    def register_callbacks(app):
        @app.callback(
            Output(COMPONENT_IDS['athlete_profile'], 'children'),
            [Input({'type': 'hierarchical-dropdown', 'layer': 'athlete'}, 'value')],
            prevent_initial_call=False
        )
        def update_athlete_profile(selected_athlete):
            """Update athlete profile based on selected athlete dropdown"""
            if selected_athlete:
                return AthleteProfileCallbacks._create_athlete_profile(selected_athlete)
            else:
                return AthleteProfileLayout.create_default()

    @staticmethod
    def _create_athlete_profile(athlete_key):
        """Helper method to create athlete profile UI"""
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
                        'border': f'3px solid {COLORS["primary"]}',
                        'margin-bottom': '8px'
                    }
                ),
                html.H4(profile['name'], style={'margin': '3px 0', 'color': COLORS['secondary'], 'font-size': '16px'}),
                html.Div([
                    html.Div([
                        html.Strong("Age: ", style={'color': '#34495e'}),
                        html.Span(f"{profile['age']} years", style={'color': COLORS['muted']})
                    ], style={'margin': '2px 0', 'font-size': '14px'}),
                    html.Div([
                        html.Strong("Height: ", style={'color': '#34495e'}),
                        html.Span(profile['height'], style={'color': COLORS['muted']})
                    ], style={'margin': '2px 0', 'font-size': '14px'}),
                    html.Div([
                        html.Strong("Weight: ", style={'color': '#34495e'}),
                        html.Span(profile['weight'], style={'color': COLORS['muted']})
                    ], style={'margin': '2px 0', 'font-size': '14px'}),
                    html.Div([
                        html.Strong("Sex: ", style={'color': '#34495e'}),
                        html.Span(profile['sex'], style={'color': COLORS['muted']})
                    ], style={'margin': '2px 0', 'font-size': '14px'}),
                    html.Div([
                        html.Strong("Sport: ", style={'color': '#34495e'}),
                        html.Span(profile['sport'], style={'color': COLORS['muted']})
                    ], style={'margin': '2px 0', 'font-size': '14px'}),
                    html.Div([
                        html.Strong("Position: ", style={'color': '#34495e'}),
                        html.Span(profile['position'], style={'color': COLORS['muted']})
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
                    'border': f'3px solid {COLORS["primary"]}',
                    'margin-bottom': '8px'
                }
            ),
            html.H4("Unknown Athlete", style={'margin': '3px 0', 'color': COLORS['secondary'], 'font-size': '16px'}),
            html.P("Profile not available", style={'margin': '0', 'font-size': '14px', 'color': COLORS['muted']})
        ], style={'text-align': 'center'})


class HierarchicalDropdownCallbacks:
    """Callbacks for hierarchical dropdown system"""
    
    @staticmethod
    def register_callbacks(app):
        @app.callback(
            [Output({'type': 'hierarchical-dropdown', 'layer': 'exercise'}, 'options'),
             Output({'type': 'hierarchical-dropdown', 'layer': 'exercise'}, 'disabled'),
             Output({'type': 'hierarchical-dropdown', 'layer': 'exercise'}, 'placeholder'),
             Output({'type': 'hierarchical-dropdown', 'layer': 'exercise'}, 'value'),
             Output({'type': 'hierarchical-dropdown', 'layer': 'attempt'}, 'value', allow_duplicate=True),
             Output({'type': 'hierarchical-dropdown', 'layer': 'group'}, 'value', allow_duplicate=True),
             Output({'type': 'hierarchical-dropdown', 'layer': 'metrics'}, 'value', allow_duplicate=True)],
            [Input({'type': 'hierarchical-dropdown', 'layer': 'athlete'}, 'value')],
            prevent_initial_call=True
        )
        def update_exercise_dropdown(selected_athlete):
            """Update exercise dropdown based on selected athlete and reset all lower levels"""
            try:
                if selected_athlete:
                    exercises = hierarchical_selector.get_exercises_for_athlete(selected_athlete)
                    options = [{'label': exercise, 'value': exercise} for exercise in exercises]
                    return options, False, "Select an exercise...", None, None, None, []
                else:
                    return [], True, "First select an athlete...", None, None, None, []
            except Exception:
                return [], True, "Error loading exercises", None, None, None, []

        @app.callback(
            [Output({'type': 'hierarchical-dropdown', 'layer': 'attempt'}, 'options'),
             Output({'type': 'hierarchical-dropdown', 'layer': 'attempt'}, 'disabled'),
             Output({'type': 'hierarchical-dropdown', 'layer': 'attempt'}, 'placeholder'),
             Output({'type': 'hierarchical-dropdown', 'layer': 'attempt'}, 'value'),
             Output({'type': 'hierarchical-dropdown', 'layer': 'group'}, 'value', allow_duplicate=True),
             Output({'type': 'hierarchical-dropdown', 'layer': 'metrics'}, 'value', allow_duplicate=True)],
            [Input({'type': 'hierarchical-dropdown', 'layer': 'athlete'}, 'value'),
             Input({'type': 'hierarchical-dropdown', 'layer': 'exercise'}, 'value')],
            prevent_initial_call=True
        )
        def update_attempt_dropdown(selected_athlete, selected_exercise):
            """Update attempt dropdown based on selected athlete and exercise and reset lower levels"""
            try:
                if selected_athlete and selected_exercise:
                    attempts = hierarchical_selector.get_attempts_for_athlete_exercise(selected_athlete, selected_exercise)
                    options = [{'label': f"Attempt {attempt}", 'value': attempt} for attempt in attempts]
                    return options, False, "Select an attempt...", None, None, []
                else:
                    return [], True, "First select athlete and exercise...", None, None, []
            except Exception:
                return [], True, "Error loading attempts", None, None, []

        @app.callback(
            [Output({'type': 'hierarchical-dropdown', 'layer': 'group'}, 'disabled'),
             Output({'type': 'hierarchical-dropdown', 'layer': 'group'}, 'placeholder'),
             Output({'type': 'hierarchical-dropdown', 'layer': 'group'}, 'value'),
             Output({'type': 'hierarchical-dropdown', 'layer': 'metrics'}, 'value', allow_duplicate=True)],
            [Input({'type': 'hierarchical-dropdown', 'layer': 'attempt'}, 'value')],
            prevent_initial_call=True
        )
        def update_group_dropdown(selected_attempt):
            """Update metric group dropdown based on selected attempt and reset metrics"""
            try:
                if selected_attempt:
                    return False, "Select a metric group...", None, []
                else:
                    return True, "First select an attempt...", None, []
            except Exception:
                return True, "Error loading groups", None, []

        @app.callback(
            [Output({'type': 'hierarchical-dropdown', 'layer': 'metrics'}, 'options'),
             Output({'type': 'hierarchical-dropdown', 'layer': 'metrics'}, 'disabled'),
             Output({'type': 'hierarchical-dropdown', 'layer': 'metrics'}, 'placeholder'),
             Output({'type': 'hierarchical-dropdown', 'layer': 'metrics'}, 'value')],
            [Input({'type': 'hierarchical-dropdown', 'layer': 'group'}, 'value')],
            [State({'type': 'hierarchical-dropdown', 'layer': 'metrics'}, 'value')],
            prevent_initial_call=True
        )
        def update_metrics_dropdown(selected_group, current_metrics):
            """Update exact metrics dropdown based on selected metric group"""
            try:
                if selected_group and selected_group in metric_groups:
                    options = [{'label': m, 'value': m} for m in metric_groups[selected_group]]
                    return options, False, "Select metrics...", current_metrics or []
                else:
                    return [], True, "First select a metric group...", []
            except Exception:
                return [], True, "Error loading metrics", []


class MetricsSelectionCallbacks:
    """Callbacks related to metrics selection and display"""
    
    @staticmethod
    def register_callbacks(app):
        @app.callback(
            Output('selected-metrics-display', 'children'),
            [Input(COMPONENT_IDS['metrics_store'], 'data')],
            prevent_initial_call=True
        )
        def update_selected_metrics_display_content(persistent_metrics):
            """Update the visual display of selected metrics"""
            if not persistent_metrics:
                return [html.P("No metrics selected yet", style={'color': COLORS['muted'], 'font-style': 'italic', 'margin': '10px 0'})]
            
            # Create a list of selected metrics with styling and remove buttons
            metric_items = []
            for i, metric in enumerate(persistent_metrics):
                metric_items.append(
                    html.Div([
                        html.Span(metric, style={'flex': '1', 'margin-right': '10px', 'color': COLORS['secondary']}),
                        html.Button(
                            "×",
                            id={'type': 'remove-metric-btn', 'metric': metric},
                            style={
                                'background': COLORS['danger'],
                                'color': 'white',
                                'border': 'none',
                                'border-radius': '50%',
                                'width': '20px',
                                'height': '20px',
                                'font-size': '12px',
                                'cursor': 'pointer',
                                'display': 'flex',
                                'align-items': 'center',
                                'justify-content': 'center'
                            },
                            title=f"Remove {metric}"
                        )
                    ], style={
                        'display': 'flex',
                        'align-items': 'center',
                        'justify-content': 'space-between',
                        'padding': '8px 12px',
                        'margin': '3px 0',
                        'background': COLORS['light'],
                        'border': f'1px solid {COLORS["primary"]}',
                        'border-radius': '15px',
                        'font-size': '14px'
                    })
                )
            
            return metric_items

        @app.callback(
            Output(COMPONENT_IDS['metrics_store'], 'data', allow_duplicate=True),
            [Input({'type': 'hierarchical-dropdown', 'layer': 'metrics'}, 'value')],
            [State(COMPONENT_IDS['metrics_store'], 'data')],
            prevent_initial_call=True
        )
        def update_persistent_metrics_from_dropdown(dropdown_metrics, persistent_metrics):
            """Update persistent metrics when dropdown changes"""
            if dropdown_metrics is None:
                dropdown_metrics = []
            
            if persistent_metrics is None:
                persistent_metrics = []
                
            # Add new metrics from dropdown that aren't already in persistent
            updated_metrics = persistent_metrics.copy()
            for metric in dropdown_metrics:
                if metric not in updated_metrics:
                    updated_metrics.append(metric)
            
            return updated_metrics

        @app.callback(
            Output(COMPONENT_IDS['metrics_store'], 'data', allow_duplicate=True),
            [Input({'type': 'remove-metric-btn', 'metric': dash.dependencies.ALL}, 'n_clicks')],
            [State(COMPONENT_IDS['metrics_store'], 'data')],
            prevent_initial_call=True
        )
        def remove_metric_from_persistent(remove_clicks, persistent_metrics):
            """Remove metric when remove button is clicked"""
            if persistent_metrics is None:
                persistent_metrics = []
            
            ctx = callback_context
            if not ctx.triggered:
                raise PreventUpdate
            
            trigger_id = ctx.triggered[0]['prop_id']
            
            if 'remove-metric-btn' in trigger_id and any(remove_clicks):
                # Extract metric name from button ID
                clicked_button_id = eval(trigger_id.split('.')[0])
                metric_to_remove = clicked_button_id['metric']
                
                # Remove the metric from persistent list
                updated_metrics = [m for m in persistent_metrics if m != metric_to_remove]
                return updated_metrics
            
            raise PreventUpdate


class DataStoreCallbacks:
    """Callbacks for managing data stores and persistent state"""
    
    @staticmethod
    def register_callbacks(app):
        @app.callback(
            Output(COMPONENT_IDS['hierarchical_store'], 'data', allow_duplicate=True),
            [Input({'type': 'hierarchical-dropdown', 'layer': 'athlete'}, 'value'),
             Input({'type': 'hierarchical-dropdown', 'layer': 'exercise'}, 'value'),
             Input({'type': 'hierarchical-dropdown', 'layer': 'attempt'}, 'value'),
             Input(COMPONENT_IDS['metrics_store'], 'data')],
            prevent_initial_call=True
        )
        def update_hierarchical_store(selected_athlete, selected_exercise, selected_attempt, persistent_metrics):
            """Update hierarchical store with current selections"""
            files = []
            
            if selected_athlete and selected_exercise and selected_attempt:
                filename = hierarchical_selector.construct_filename_from_hierarchy(
                    selected_athlete, selected_exercise, selected_attempt
                )
                if filename:
                    files = [filename]
            
            return {
                'files': files,
                'metrics': persistent_metrics or []
            }


class VideoPlayerCallbacks:
    """Callbacks for video player functionality"""
    
    @staticmethod
    def register_callbacks(app):
        @app.callback(
            Output(COMPONENT_IDS['video_player'], 'src'),
            [Input({'type': 'hierarchical-dropdown', 'layer': 'athlete'}, 'value'),
             Input({'type': 'hierarchical-dropdown', 'layer': 'exercise'}, 'value'),
             Input({'type': 'hierarchical-dropdown', 'layer': 'attempt'}, 'value')]
        )
        def update_video_source(selected_athlete, selected_exercise, selected_attempt):
            """Update video source based on hierarchical selections"""
            if selected_athlete and selected_exercise and selected_attempt:
                video_filename = hierarchical_selector.construct_video_filename(
                    selected_athlete, selected_exercise, selected_attempt
                )
                if video_filename:
                    return f'/assets/videos/{video_filename}'
            
            return ''


class PlotCallbacks:
    """Callbacks for plot generation and updates"""
    
    @staticmethod
    def register_callbacks(app):
        @app.callback(
            Output(COMPONENT_IDS['kinematic_plot'], 'figure'),
            [Input(COMPONENT_IDS['hierarchical_store'], 'data')],
            prevent_initial_call=False
        )
        def update_plot(hierarchical_data):
            """Update plot based on hierarchical selections"""
            files = hierarchical_data.get('files', [])
            metrics = hierarchical_data.get('metrics', [])
            
            if not files or not metrics:
                # Return empty plot
                return {
                    'data': [],
                    'layout': {
                        'title': 'Select athlete, exercise, attempt, and metrics to view data',
                        'xaxis': {'title': 'Time'},
                        'yaxis': {'title': 'Value'},
                        'plot_bgcolor': 'white',
                        'paper_bgcolor': 'white'
                    }
                }
            
            # Generate plot data
            traces = []
            for filename in files:
                df = data_processor.get_dataframe(filename)
                if df is not None:
                    for metric in metrics:
                        if metric in df.columns:
                            traces.append({
                                'x': df.index,
                                'y': df[metric],
                                'type': 'scatter',
                                'mode': 'lines',
                                'name': f'{metric} ({filename})'
                            })
            
            return {
                'data': traces,
                'layout': {
                    'title': f'Kinematic Analysis - {len(files)} file(s), {len(metrics)} metric(s)',
                    'xaxis': {'title': 'Time'},
                    'yaxis': {'title': 'Value'},
                    'plot_bgcolor': 'white',
                    'paper_bgcolor': 'white',
                    'hovermode': 'closest'
                }
            }


class NotesCallbacks:
    """Callbacks for notes and analysis functionality"""
    
    @staticmethod
    def register_callbacks(app):
        @app.callback(
            Output('save-status', 'children'),
            Input('save-notes-btn', 'n_clicks'),
            Input('key-takeaways-textarea', 'value'),
            Input('observations-textarea', 'value'),
            Input('recommendations-textarea', 'value'),
            prevent_initial_call=True
        )
        def save_notes_local(n_clicks, key_takeaways_content, observations_content, recommendations_content):
            """Save notes locally"""
            if n_clicks:
                filename, error = notes_manager.save_notes_to_file(
                    key_takeaways_content, observations_content, recommendations_content
                )
                if filename:
                    return html.Div(f"✓ Notes saved to {filename}", style={'color': 'green', 'margin-top': '10px'})
                else:
                    return html.Div(f"✗ Error saving notes: {error}", style={'color': 'red', 'margin-top': '10px'})
            return ""

        @app.callback(
            [Output('download-link', 'href'),
             Output('download-link', 'download')],
            [Input('download-notes-btn', 'n_clicks'),
             Input('key-takeaways-textarea', 'value'),
             Input('observations-textarea', 'value'),
             Input('recommendations-textarea', 'value')],
            prevent_initial_call=True
        )
        def prepare_download(n_clicks, key_takeaways_content, observations_content, recommendations_content):
            """Prepare download link for notes"""
            if n_clicks:
                content = notes_manager.generate_notes_content(
                    key_takeaways_content, observations_content, recommendations_content
                )
                download_url, filename = notes_manager.create_download_link(content)
                return download_url, filename
            
            return "", "analysis_notes.txt"


class ReportGenerationCallbacks:
    """Callbacks for generating static reports"""
    
    @staticmethod
    def register_callbacks(app):
        @app.callback(
            Output('report-status', 'children'),
            [Input('generate-report-btn', 'n_clicks')],
            [State({'type': 'hierarchical-dropdown', 'layer': 'athlete'}, 'value')],
            prevent_initial_call=True
        )
        def generate_report(n_clicks, selected_athlete):
            """Generate static report for selected athlete"""
            if not n_clicks:
                raise PreventUpdate
                
            if not selected_athlete:
                return html.Div("Please select an athlete first", style={'color': 'red'})
            
            try:
                # Import and run the report generator
                import sys
                import os
                # Add the static_report directory to the path
                current_dir = os.path.dirname(os.path.abspath(__file__))
                sys.path.append(os.path.join(current_dir, 'static_report'))
                from report_generator import KinematicReportGenerator
                
                # Initialize and run generator
                generator = KinematicReportGenerator()
                generator.process_all_files()
                
                # Generate report for the selected athlete
                report_path = generator.save_report(selected_athlete)
                
                if report_path:
                    # Create a clickable link to the report
                    report_filename = os.path.basename(report_path)
                    return html.Div([
                        html.P("✓ Report generated successfully!", style={'color': 'green', 'margin': '5px 0'}),
                        html.A(
                            f"Open {report_filename}",
                            href=f"/static_report/reports/{report_filename}",
                            target="_blank",
                            style={'color': 'blue', 'text-decoration': 'underline'}
                        )
                    ])
                else:
                    return html.Div("Failed to generate report", style={'color': 'red'})
                    
            except Exception as e:
                return html.Div(f"Error: {str(e)}", style={'color': 'red'})


def register_all_callbacks(app):
    """Register all callbacks with the app"""
    AthleteProfileCallbacks.register_callbacks(app)
    MetricsSelectionCallbacks.register_callbacks(app)
    HierarchicalDropdownCallbacks.register_callbacks(app)
    DataStoreCallbacks.register_callbacks(app)
    VideoPlayerCallbacks.register_callbacks(app)
    PlotCallbacks.register_callbacks(app)
    NotesCallbacks.register_callbacks(app)
    ReportGenerationCallbacks.register_callbacks(app)
