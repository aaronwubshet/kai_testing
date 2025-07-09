# -*- coding: utf-8 -*-
"""
Callbacks for the Kinematic Dashboard
Contains all Dash callback functions organized by functionality
"""

from dash import Input, Output, State, html, callback_context
from dash.dependencies import ALL
from dash.exceptions import PreventUpdate
import dash
import plotly.graph_objs as go

from config import (
    athlete_profiles, file_mapping, metric_groups, COMPONENT_IDS, 
    current_mode, COLORS
)
from utils import (
    data_processor, hierarchical_selector, notes_manager, 
    FileAnalyzer
)
from layout import (
    AthleteProfileLayout, FileSelectionLayout, HierarchicalDropdownsLayout,
    SelectedMetricsLayout, VideoAnalysisLayout, MetricsSelectionLayout
)


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


class MetricsSelectionCallbacks:
    """Callbacks related to metrics selection and display"""
    
    @staticmethod
    def register_callbacks(app):
        @app.callback(
            [Output(COMPONENT_IDS['metrics_container'], 'children'),
             Output('metrics-container-box', 'style')],
            Input(COMPONENT_IDS['debug_toggle'], 'value')
        )
        def update_metrics_selection(debug_mode):
            is_debug = 'debug' in (debug_mode or [])
            
            # Update container style based on debug mode
            if is_debug:
                container_style = {
                    'border': 'none',
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
            
            # Always create hierarchical dropdowns to avoid callback errors
            hierarchical_dropdowns = HierarchicalDropdownsLayout.create()
            selected_metrics_display = SelectedMetricsLayout.create()
            video_analysis_section = VideoAnalysisLayout.create()
            
            if is_debug:
                # Debug mode: Show hierarchical dropdowns and selected metrics display in one container, video analysis in separate container
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
                    'border': f'2px solid {COLORS["danger"]}',
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
                normal_mode_content = MetricsSelectionLayout.create_normal_mode()
                
                # Include hidden hierarchical dropdowns to avoid callback errors
                hidden_hierarchical = html.Div([
                    hierarchical_dropdowns,
                    selected_metrics_display,
                    video_analysis_section
                ], style={'display': 'none'})
                
                content = normal_mode_content + [hidden_hierarchical]
            
            return content, container_style

        @app.callback(
            Output('selected-metrics-display', 'children'),
            [Input(COMPONENT_IDS['metrics_store'], 'data'),
             Input(COMPONENT_IDS['debug_toggle'], 'value')],
            prevent_initial_call=True
        )
        def update_selected_metrics_display_content(persistent_metrics, debug_mode):
            """Update the visual display of selected metrics"""
            is_debug = 'debug' in (debug_mode or [])
            
            if not is_debug:
                raise PreventUpdate
            
            if not persistent_metrics:
                return [html.P("No metrics selected yet", style={'color': COLORS['muted'], 'font-style': 'italic', 'margin': '10px 0'})]
            
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
                            html.Span(f"{i+1}. ", style={'font-weight': 'bold', 'color': COLORS['primary'], 'margin-right': '5px'}),
                            html.Span(metric, style={'color': COLORS['secondary'], 'font-size': '14px', 'flex': '1'}),
                            html.Span(f"({metric_group})", style={'font-size': '12px', 'color': '#666', 'margin-left': '8px'}) if metric_group else None,
                        ], style={'display': 'flex', 'align-items': 'center', 'flex': '1'}),
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
                        'border': f'1px solid {COLORS["primary"]}',
                        'border-radius': '4px',
                        'transition': 'all 0.2s ease',
                        'display': 'flex',
                        'align-items': 'center',
                        'justify-content': 'space-between'
                    })
                )
            
            return metric_items

        @app.callback(
            Output(COMPONENT_IDS['metrics_store'], 'data', allow_duplicate=True),
            [Input(COMPONENT_IDS['debug_toggle'], 'value'),
             Input({'type': 'remove-metric-btn', 'metric': ALL}, 'n_clicks')],
            [State(COMPONENT_IDS['metrics_store'], 'data')],
            prevent_initial_call=True
        )
        def update_persistent_metrics_from_display(debug_mode, remove_clicks, persistent_metrics):
            """Update persistent metrics when remove buttons are clicked"""
            is_debug = 'debug' in (debug_mode or [])
            
            if not is_debug:
                raise PreventUpdate
            
            if persistent_metrics is None:
                persistent_metrics = []
            
            ctx = callback_context
            if not ctx.triggered:
                raise PreventUpdate
            
            trigger_id = ctx.triggered[0]['prop_id']
            
            if 'remove-metric-btn' in trigger_id and any(remove_clicks):
                triggered_component = ctx.triggered[0]['prop_id']
                if '"metric":"' in triggered_component:
                    metric_to_remove = triggered_component.split('"metric":"')[1].split('"')[0]
                    persistent_metrics = [m for m in persistent_metrics if m != metric_to_remove]
                    return persistent_metrics
            
            raise PreventUpdate

        @app.callback(
            [Output({'type': 'hierarchical-dropdown', 'layer': 'metrics'}, 'value', allow_duplicate=True),
             Output(COMPONENT_IDS['metrics_store'], 'data', allow_duplicate=True)],
            [Input({'type': 'clear-all-btn', 'component': ALL}, 'n_clicks')],
            prevent_initial_call=True
        )
        def clear_all_metrics_pattern(n_clicks_list):
            """Clear all selected metrics when Clear All button is clicked"""
            if any(n_clicks_list) and any(click for click in n_clicks_list if click):
                return [], []
            raise PreventUpdate


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
            [Input({'type': 'hierarchical-dropdown', 'layer': 'athlete'}, 'value'),
             Input(COMPONENT_IDS['debug_toggle'], 'value')],
            prevent_initial_call=True
        )
        def update_exercise_dropdown(selected_athlete, debug_mode):
            """Update exercise dropdown based on selected athlete and reset all lower levels"""
            is_debug = 'debug' in (debug_mode or [])
            
            if not is_debug:
                raise PreventUpdate
            
            try:
                if not selected_athlete:
                    return [], True, "First select an athlete...", None, None, None, []
                
                exercises = hierarchical_selector.get_exercises_for_athlete(selected_athlete)
                options = [{'label': ex.title(), 'value': ex} for ex in exercises]
                
                return options, False, "Choose an exercise...", None, None, None, []
            except Exception:
                raise PreventUpdate

        @app.callback(
            [Output({'type': 'hierarchical-dropdown', 'layer': 'attempt'}, 'options'),
             Output({'type': 'hierarchical-dropdown', 'layer': 'attempt'}, 'disabled'),
             Output({'type': 'hierarchical-dropdown', 'layer': 'attempt'}, 'placeholder'),
             Output({'type': 'hierarchical-dropdown', 'layer': 'attempt'}, 'value'),
             Output({'type': 'hierarchical-dropdown', 'layer': 'group'}, 'value', allow_duplicate=True),
             Output({'type': 'hierarchical-dropdown', 'layer': 'metrics'}, 'value', allow_duplicate=True)],
            [Input({'type': 'hierarchical-dropdown', 'layer': 'athlete'}, 'value'),
             Input({'type': 'hierarchical-dropdown', 'layer': 'exercise'}, 'value'),
             Input(COMPONENT_IDS['debug_toggle'], 'value')],
            prevent_initial_call=True
        )
        def update_attempt_dropdown(selected_athlete, selected_exercise, debug_mode):
            """Update attempt dropdown based on selected athlete and exercise and reset lower levels"""
            is_debug = 'debug' in (debug_mode or [])
            
            if not is_debug:
                raise PreventUpdate
            
            try:
                if not selected_athlete or not selected_exercise:
                    return [], True, "First select athlete and exercise...", None, None, []
                
                attempts = hierarchical_selector.get_attempts_for_athlete_exercise(selected_athlete, selected_exercise)
                options = [{'label': f"Attempt {att}", 'value': att} for att in attempts]
                
                return options, False, "Choose an attempt...", None, None, []
            except Exception:
                raise PreventUpdate

        @app.callback(
            [Output({'type': 'hierarchical-dropdown', 'layer': 'group'}, 'disabled'),
             Output({'type': 'hierarchical-dropdown', 'layer': 'group'}, 'placeholder'),
             Output({'type': 'hierarchical-dropdown', 'layer': 'group'}, 'value'),
             Output({'type': 'hierarchical-dropdown', 'layer': 'metrics'}, 'value', allow_duplicate=True)],
            [Input({'type': 'hierarchical-dropdown', 'layer': 'attempt'}, 'value'),
             Input(COMPONENT_IDS['debug_toggle'], 'value')],
            prevent_initial_call=True
        )
        def update_group_dropdown(selected_attempt, debug_mode):
            """Update metric group dropdown based on selected attempt and reset metrics"""
            is_debug = 'debug' in (debug_mode or [])
            
            if not is_debug:
                raise PreventUpdate
            
            try:
                if not selected_attempt:
                    return True, "First select attempt...", None, []
                
                return False, "Choose a metric group...", None, []
            except Exception:
                raise PreventUpdate

        @app.callback(
            [Output({'type': 'hierarchical-dropdown', 'layer': 'metrics'}, 'options'),
             Output({'type': 'hierarchical-dropdown', 'layer': 'metrics'}, 'disabled'),
             Output({'type': 'hierarchical-dropdown', 'layer': 'metrics'}, 'placeholder'),
             Output({'type': 'hierarchical-dropdown', 'layer': 'metrics'}, 'value')],
            [Input({'type': 'hierarchical-dropdown', 'layer': 'group'}, 'value'),
             Input(COMPONENT_IDS['debug_toggle'], 'value')],
            [State({'type': 'hierarchical-dropdown', 'layer': 'metrics'}, 'value')],
            prevent_initial_call=True
        )
        def update_metrics_dropdown(selected_group, debug_mode, current_metrics):
            """Update exact metrics dropdown based on selected metric group"""
            is_debug = 'debug' in (debug_mode or [])
            
            if not is_debug:
                raise PreventUpdate
            
            try:
                if not selected_group or selected_group not in metric_groups:
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
                
                return options, False, "Choose specific metrics...", []
            except Exception:
                raise PreventUpdate


class DataStoreCallbacks:
    """Callbacks for managing data stores and persistent state"""
    
    @staticmethod
    def register_callbacks(app):
        @app.callback(
            Output(COMPONENT_IDS['metrics_store'], 'data', allow_duplicate=True),
            [Input({'type': 'hierarchical-dropdown', 'layer': 'metrics'}, 'value'),
             Input(COMPONENT_IDS['debug_toggle'], 'value')],
            [State(COMPONENT_IDS['metrics_store'], 'data')],
            prevent_initial_call=True
        )
        def update_persistent_metrics_from_dropdown(dropdown_metrics, debug_mode, persistent_metrics):
            """Update persistent metrics when dropdown selection changes"""
            is_debug = 'debug' in (debug_mode or [])
            
            if not is_debug:
                raise PreventUpdate
            
            if persistent_metrics is None:
                persistent_metrics = []
            
            if dropdown_metrics:
                for metric in dropdown_metrics:
                    if metric not in persistent_metrics:
                        persistent_metrics.append(metric)
            
            return persistent_metrics

        @app.callback(
            Output(COMPONENT_IDS['hierarchical_store'], 'data', allow_duplicate=True),
            [Input({'type': 'hierarchical-dropdown', 'layer': 'athlete'}, 'value'),
             Input({'type': 'hierarchical-dropdown', 'layer': 'exercise'}, 'value'),
             Input({'type': 'hierarchical-dropdown', 'layer': 'attempt'}, 'value'),
             Input(COMPONENT_IDS['metrics_store'], 'data'),
             Input(COMPONENT_IDS['debug_toggle'], 'value')],
            prevent_initial_call=True
        )
        def update_hierarchical_store(selected_athlete, selected_exercise, selected_attempt, persistent_metrics, debug_mode):
            """Update the store with hierarchical selections using all 5 levels"""
            is_debug = 'debug' in (debug_mode or [])
            
            if not is_debug:
                raise PreventUpdate
            
            try:
                if not all([selected_athlete, selected_exercise, selected_attempt]):
                    return {'files': [], 'metrics': []}
                
                filename = hierarchical_selector.construct_filename_from_hierarchy(selected_athlete, selected_exercise, selected_attempt)
                
                if filename:
                    return {
                        'files': [filename],
                        'metrics': persistent_metrics if persistent_metrics else []
                    }
                else:
                    return {'files': [], 'metrics': []}
            except Exception:
                return {'files': [], 'metrics': []}

        @app.callback(
            Output(COMPONENT_IDS['hierarchical_store'], 'data', allow_duplicate=True),
            Input(COMPONENT_IDS['debug_toggle'], 'value'),
            prevent_initial_call=True
        )
        def reset_hierarchical_store_on_mode_change(debug_mode):
            """Reset store when switching modes"""
            is_debug = 'debug' in (debug_mode or [])
            if not is_debug:
                return {'files': [], 'metrics': []}
            raise PreventUpdate


class VideoPlayerCallbacks:
    """Callbacks for video player functionality"""
    
    @staticmethod
    def register_callbacks(app):
        @app.callback(
            Output(COMPONENT_IDS['video_player'], 'src'),
            [Input({'type': 'hierarchical-dropdown', 'layer': 'athlete'}, 'value'),
             Input({'type': 'hierarchical-dropdown', 'layer': 'exercise'}, 'value'),
             Input({'type': 'hierarchical-dropdown', 'layer': 'attempt'}, 'value'),
             Input(COMPONENT_IDS['debug_toggle'], 'value')]
        )
        def update_video_source(selected_athlete, selected_exercise, selected_attempt, debug_mode):
            """Update video source based on hierarchical selections"""
            is_debug = 'debug' in (debug_mode or [])
            
            if not is_debug:
                return ''
            
            if not all([selected_athlete, selected_exercise, selected_attempt]):
                return ''
            
            try:
                video_filename = hierarchical_selector.construct_video_filename(selected_athlete, selected_exercise, selected_attempt)
                if video_filename:
                    return f"/assets/videos/{video_filename}"
                else:
                    return ''
            except Exception:
                return ''


class PlotCallbacks:
    """Callbacks for plot generation and updates"""
    
    @staticmethod
    def register_callbacks(app):
        @app.callback(
            Output(COMPONENT_IDS['kinematic_plot'], 'figure'),
            [Input(COMPONENT_IDS['debug_toggle'], 'value'),
             Input({'type': 'file-selector', 'mode': ALL}, 'value'),
             Input({'type': 'metrics-selector', 'mode': 'checklist', 'group': ALL}, 'value'),
             Input(COMPONENT_IDS['hierarchical_store'], 'data')],
            prevent_initial_call=False
        )
        def update_plot_unified(debug_mode, file_values, checklist_metrics_values, hierarchical_data):
            """Unified plot update callback using pattern-matching"""
            is_debug = 'debug' in (debug_mode or [])
            
            # Get selected files and metrics based on mode
            if is_debug:
                selected_files = hierarchical_data.get('files', [])
                selected_metrics = hierarchical_data.get('metrics', [])
            else:
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
                df = data_processor.get_dataframe(fname)
                if df is not None:
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
            """Save notes to local file (works for local development)"""
            if n_clicks > 0 and (key_takeaways_content or observations_content or recommendations_content):
                filename, error = notes_manager.save_notes_to_file(
                    key_takeaways_content, 
                    observations_content, 
                    recommendations_content
                )
                
                if filename:
                    return html.Div([
                        html.Span("✓ Notes saved locally to: ", style={'color': 'green'}),
                        html.Code(filename, style={'background': '#f0f0f0', 'padding': '2px 4px'}),
                        html.Br(),
                        html.Small("Note: On cloud platforms, use 'Download Notes' for persistent storage.", 
                                 style={'color': '#666', 'font-style': 'italic'})
                    ])
                else:
                    return html.Div([
                        html.Span(f"⚠ Error saving locally: {error}", style={'color': 'orange'}),
                        html.Br(),
                        html.Small("Try using 'Download Notes' instead for cloud deployment.", 
                                 style={'color': '#666', 'font-style': 'italic'})
                    ])
            
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
            """Prepare notes for download (works on cloud platforms)"""
            if n_clicks > 0 and (key_takeaways_content or observations_content or recommendations_content):
                # Generate the notes content
                content = notes_manager.generate_notes_content(
                    key_takeaways_content,
                    observations_content,
                    recommendations_content
                )
                
                # Create download link
                download_url, filename = notes_manager.create_download_link(content)
                
                return download_url, filename
            
            # Return empty values if no content or not clicked
            return "", "analysis_notes.txt"


class ReportGenerationCallbacks:
    """Callbacks for generating static reports"""
    
    @staticmethod
    def register_callbacks(app):
        @app.callback(
            Output('report-status', 'children'),
            [Input('generate-report-btn', 'n_clicks')],
            [State({'type': 'hierarchical-dropdown', 'layer': 'athlete'}, 'value'),
             State({'type': 'file-selector', 'mode': ALL}, 'value'),
             State(COMPONENT_IDS['debug_toggle'], 'value')],
            prevent_initial_call=True
        )
        def generate_report(n_clicks, selected_athlete_dropdown, file_values, debug_mode):
            """Generate static report for selected athlete"""
            if not n_clicks:
                raise PreventUpdate
                
            is_debug = 'debug' in (debug_mode or [])
            
            # Determine which athlete to generate report for
            if is_debug and selected_athlete_dropdown:
                athlete_name = selected_athlete_dropdown
            else:
                # In normal mode, determine from selected files
                if not file_values or not any(file_values):
                    return html.Div("Please select files first", style={'color': 'red'})
                
                # Get the athlete from the first selected file
                selected_files = [f for files in file_values for f in (files or [])]
                if selected_files:
                    file_analyzer = FileAnalyzer(selected_files[0])
                    athlete_name = file_analyzer.get_athlete_name()
                else:
                    return html.Div("Please select files first", style={'color': 'red'})
            
            if not athlete_name:
                return html.Div("No athlete selected", style={'color': 'red'})
            
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
                report_path = generator.save_report(athlete_name)
                
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
