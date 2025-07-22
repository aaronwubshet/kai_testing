# -*- coding: utf-8 -*-
"""
Simplified Callbacks for the Kinematic Dashboard
Hierarchical dropdown interface only
"""

import os
from dash import Input, Output, State, html, callback_context, dcc, clientside_callback, ClientsideFunction
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

        @app.callback(
            [Output(COMPONENT_IDS['metrics_store'], 'data', allow_duplicate=True),
             Output({'type': 'hierarchical-dropdown', 'layer': 'metrics'}, 'value', allow_duplicate=True)],
            [Input({'type': 'clear-all-btn', 'component': 'metrics'}, 'n_clicks')],
            prevent_initial_call=True
        )
        def clear_all_metrics(n_clicks):
            """Clear all selected metrics when Clear All button is clicked"""
            if n_clicks and n_clicks > 0:
                return [], []  # Clear both persistent store and dropdown
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
            [Output(COMPONENT_IDS['video_player'], 'src'),
             Output('video-status', 'children')],
            [Input({'type': 'hierarchical-dropdown', 'layer': 'athlete'}, 'value'),
             Input({'type': 'hierarchical-dropdown', 'layer': 'exercise'}, 'value'),
             Input({'type': 'hierarchical-dropdown', 'layer': 'attempt'}, 'value')]
        )
        def update_video_source(selected_athlete, selected_exercise, selected_attempt):
            """Update video source based on hierarchical selections"""
            print(f"DEBUG: Video callback triggered with athlete={selected_athlete}, exercise={selected_exercise}, attempt={selected_attempt}")
            
            if selected_athlete and selected_exercise and selected_attempt:
                video_filename = hierarchical_selector.construct_video_filename(
                    selected_athlete, selected_exercise, selected_attempt
                )
                print(f"DEBUG: Constructed video filename: {video_filename}")
                
                if video_filename:
                    video_path = f'/assets/videos/{video_filename}'
                    print(f"DEBUG: Returning video path: {video_path}")
                    
                    # Check if file actually exists
                    import os
                    full_path = os.path.join("assets", "videos", video_filename)
                    if os.path.exists(full_path):
                        return video_path, f"Playing: {video_filename}"
                    else:
                        return '', f"Video not found: {video_filename}"
                else:
                    print("DEBUG: No video filename constructed")
                    return '', "No video available for this selection"
            else:
                print("DEBUG: Missing required selections")
                return '', "Select an athlete, exercise, and attempt to view video"


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
            Output('report-url-store', 'data'),
            [Input('generate-report-btn', 'n_clicks')],
            [State({'type': 'hierarchical-dropdown', 'layer': 'athlete'}, 'value')],
            prevent_initial_call=True
        )
        def generate_report(n_clicks, selected_athlete):
            """Generate static report for selected athlete"""
            if not n_clicks:
                raise PreventUpdate
                
            if not selected_athlete:
                return html.Div("Please select an athlete first", style={'color': 'red'}), None
            
            try:
                # Import the report generator
                from static_report.report_generator import KinematicReportGenerator
                
                # Initialize generator
                generator = KinematicReportGenerator("STOfiles")
                
                # Process only files for the selected athlete (more efficient)
                if not os.path.exists(generator.sto_folder):
                    return html.Div("Data folder not found", style={'color': 'red'}), None
                
                sto_files = [f for f in os.listdir(generator.sto_folder) if f.endswith('.sto')]
                if not sto_files:
                    return html.Div("No data files found", style={'color': 'red'}), None
                
                # Process files for the specific athlete only
                athlete_files_processed = 0
                for filename in sto_files:
                    filepath = os.path.join(generator.sto_folder, filename)
                    file_info = generator.extract_athlete_info(filename)
                    
                    if file_info and file_info['athlete'] == selected_athlete:
                        df = generator.read_sto_file(filepath)
                        if df is not None:
                            analysis = generator.analyze_movement_quality(df, file_info['exercise_key'])
                            key = f"{file_info['athlete']}_{file_info['exercise']}_{file_info['attempt']}"
                            generator.data[key] = {
                                'info': file_info,
                                'dataframe': df,
                                'analysis': analysis,
                                'filename': filename
                            }
                            athlete_files_processed += 1
                
                if athlete_files_processed == 0:
                    return html.Div(f"No data found for {selected_athlete}", style={'color': 'red'}), None
                
                # Generate report and save to assets folder for serving
                html_content = generator.generate_html_report(selected_athlete)
                if html_content:
                    # Add PDF download button to the report
                    pdf_button_html = """
                    <div style="position: fixed; top: 20px; right: 20px; z-index: 1000;">
                        <button onclick="window.print()" style="
                            background-color: #007bff;
                            color: white;
                            border: none;
                            padding: 12px 24px;
                            border-radius: 5px;
                            cursor: pointer;
                            font-size: 14px;
                            font-weight: bold;
                            box-shadow: 0 2px 5px rgba(0,123,255,0.3);
                            transition: all 0.3s ease;
                        " onmouseover="this.style.backgroundColor='#0056b3'" 
                           onmouseout="this.style.backgroundColor='#007bff'">
                            📄 Download PDF
                        </button>
                    </div>
                    
                    <style>
                        @media print {
                            /* Hide the PDF button when printing */
                            div[style*="position: fixed"] {
                                display: none !important;
                            }
                            
                            /* Optimize print layout */
                            body {
                                font-size: 12px;
                                line-height: 1.4;
                                margin: 0;
                                padding: 20px;
                            }
                            
                            .chart-container {
                                page-break-inside: avoid;
                                margin-bottom: 20px;
                            }
                            
                            .section {
                                page-break-inside: avoid;
                                margin-bottom: 15px;
                            }
                            
                            h1, h2, h3 {
                                page-break-after: avoid;
                            }
                        }
                    </style>
                    """
                    
                    # Insert the PDF button right after the body tag
                    html_content = html_content.replace('<body>', f'<body>{pdf_button_html}')
                    
                    # Save to assets folder so it can be served
                    import datetime
                    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"{selected_athlete}_report_{timestamp}.html"
                    
                    # Create assets folder if it doesn't exist
                    assets_folder = "assets"
                    if not os.path.exists(assets_folder):
                        os.makedirs(assets_folder)
                    
                    filepath = os.path.join(assets_folder, filename)
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    
                    # Create the URL for the assets file
                    report_url = f"/assets/{filename}"
                    
                    return html.Div([
                        html.P("✓ Report generated successfully!", style={'color': 'green', 'margin': '5px 0'}),
                        html.P(f"Files processed: {athlete_files_processed}", style={'color': 'blue', 'margin': '5px 0'}),
                        html.P("Opening report in new tab...", style={'color': 'blue', 'margin': '5px 0', 'font-size': '12px'})
                    ]), report_url
                else:
                    return html.Div("Failed to generate report", style={'color': 'red'}), None
                    
            except Exception as e:
                return html.Div(f"Error: {str(e)}", style={'color': 'red'}), None
        
        # Client-side callback to automatically open report in new tab
        app.clientside_callback(
            """
            function(report_url) {
                if (report_url) {
                    // Small delay to ensure the status message is shown first
                    setTimeout(function() {
                        window.open(report_url, '_blank');
                    }, 500);
                }
                return '';
            }
            """,
            Output('dummy-output', 'children'),
            Input('report-url-store', 'data'),
            prevent_initial_call=True
        )


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
