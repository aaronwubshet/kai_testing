# -*- coding: utf-8 -*-
"""
Kinematic Analysis Report Generator
Generates professional static reports from STO files similar to Kinotek format
"""

import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for web applications
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import base64
from io import BytesIO
import json

class KinematicReportGenerator:
    """Main class for generating kinematic analysis reports"""
    
    def __init__(self, sto_folder="STOfiles"):
        # Handle relative path - if called from app.py, STOfiles is in current directory
        # If called directly from static_report/, it's in parent directory
        if not os.path.exists(sto_folder) and os.path.exists(f"../{sto_folder}"):
            self.sto_folder = f"../{sto_folder}"
        else:
            self.sto_folder = sto_folder
        self.data = {}
        self.analysis_results = {}
        
        # Define normal ranges for different movements (degrees)
        self.normal_ranges = {
            'squat': {
                'hip_flexion': {'min': 90, 'max': 130, 'optimal': 110},
                'knee_flexion': {'min': 90, 'max': 140, 'optimal': 115},
                'ankle_dorsiflexion': {'min': 15, 'max': 25, 'optimal': 20},
                'lumbar_flexion': {'min': 10, 'max': 30, 'optimal': 20}
            },
            'overheadsquat': {
                'shoulder_flexion': {'min': 160, 'max': 180, 'optimal': 170},
                'hip_flexion': {'min': 90, 'max': 130, 'optimal': 110},
                'knee_flexion': {'min': 90, 'max': 140, 'optimal': 115},
                'thoracic_extension': {'min': 20, 'max': 40, 'optimal': 30}
            },
            'pushup': {
                'shoulder_flexion': {'min': 90, 'max': 120, 'optimal': 105},
                'elbow_flexion': {'min': 80, 'max': 100, 'optimal': 90},
                'thoracic_extension': {'min': 10, 'max': 30, 'optimal': 20}
            },
            'standingjump': {
                'hip_flexion': {'min': 80, 'max': 120, 'optimal': 100},
                'knee_flexion': {'min': 80, 'max': 120, 'optimal': 100},
                'ankle_plantarflexion': {'min': 20, 'max': 40, 'optimal': 30}
            }
        }
    
    def read_sto_file(self, filepath):
        """Read and parse a single STO file"""
        try:
            with open(filepath, 'r') as f:
                lines = f.readlines()
                
            # Find the header end
            header_end = 0
            for i, line in enumerate(lines):
                if 'endheader' in line.lower():
                    header_end = i
                    break
            
            # Read the data
            df = pd.read_csv(filepath, sep='\t', header=header_end+1, skiprows=header_end+1)
            
            # Clean column names
            df.columns = df.columns.str.strip()
            
            return df
            
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            return None
    
    def extract_athlete_info(self, filename):
        """Extract athlete and exercise info from filename (new format: MMDDYYYY_athleteID_workoutname_attemptNumber_suffix.sto)"""
        import re
        
        # Try new format first: MMDDYYYY_athleteID_workoutname_attemptNumber_suffix.sto
        new_format_match = re.match(r'(\d{8})_(\d+)_([^_]+)_(\d+)_', filename)
        if new_format_match:
            date, athlete_id, workout_name, attempt = new_format_match.groups()
            
            # Map athlete IDs to names
            athlete_map = {'1': 'Aaron', '2': 'Gabby', '3': 'Hannah'}
            athlete = athlete_map.get(athlete_id, 'Unknown')
            
            # Map workout names to display names
            exercise_map = {
                'overheadsquat': 'Overhead Squat',
                'squat': 'Squat',
                'pushup': 'Push Up',
                'standingjump': 'Standing Jump'
            }
            exercise_name = exercise_map.get(workout_name.lower(), workout_name.title())
            
            return {
                'athlete': athlete,
                'exercise': exercise_name,
                'exercise_key': workout_name.lower(),
                'attempt': int(attempt),
                'date': date
            }
        
        # Fallback to old format for backward compatibility: YYYYMMDD + Athlete + Attempt + Exercise
        old_format_match = re.match(r'(\d{4})([AGH])(\d+)([a-zA-Z]+)', filename)
        if old_format_match:
            date, athlete_code, attempt, exercise = old_format_match.groups()
            
            athlete_map = {'A': 'Aaron', 'G': 'Gabby', 'H': 'Hannah'}
            athlete = athlete_map.get(athlete_code, 'Unknown')
            
            # Map exercise names
            exercise_map = {
                'squat': 'Squat',
                'overheadsquat': 'Overhead Squat',
                'pushup': 'Push Up',
                'standingjump': 'Standing Jump'
            }
            exercise_name = exercise_map.get(exercise.lower(), exercise.title())
            
            return {
                'athlete': athlete,
                'exercise': exercise_name,
                'exercise_key': exercise.lower(),
                'attempt': int(attempt),
                'date': date
            }
        
        return None
    
    def calculate_range_of_motion(self, df, joint_column):
        """Calculate range of motion for a joint"""
        if joint_column not in df.columns:
            return None
            
        values = df[joint_column].dropna()
        if len(values) == 0:
            return None
            
        return {
            'max': values.max(),
            'min': values.min(),
            'range': values.max() - values.min(),
            'mean': values.mean(),
            'std': values.std()
        }
    
    def analyze_movement_quality(self, df, exercise_key):
        """Analyze movement quality based on exercise type"""
        results = {
            'overall_score': 0,
            'joint_scores': {},
            'asymmetry': {},
            'recommendations': []
        }
        
        if exercise_key not in self.normal_ranges:
            return results
        
        expected_ranges = self.normal_ranges[exercise_key]
        joint_scores = []
        
        # Analyze each joint
        for joint, range_info in expected_ranges.items():
            # Look for matching columns (handle variations in naming)
            possible_columns = [col for col in df.columns if joint.replace('_', '').lower() in col.lower()]
            
            if possible_columns:
                col = possible_columns[0]  # Use first match
                rom = self.calculate_range_of_motion(df, col)
                
                if rom:
                    # Calculate score based on how close to optimal range
                    optimal = range_info['optimal']
                    actual = rom['max']  # Use max as primary metric
                    
                    # Score calculation (0-100)
                    if range_info['min'] <= actual <= range_info['max']:
                        # Within normal range
                        deviation = abs(actual - optimal)
                        max_deviation = max(optimal - range_info['min'], range_info['max'] - optimal)
                        score = max(70, 100 - (deviation / max_deviation) * 30)
                    else:
                        # Outside normal range
                        if actual < range_info['min']:
                            deviation = range_info['min'] - actual
                        else:
                            deviation = actual - range_info['max']
                        score = max(0, 70 - deviation * 2)
                    
                    joint_scores.append(score)
                    results['joint_scores'][joint] = {
                        'score': round(score),
                        'actual': round(actual, 1),
                        'optimal': optimal,
                        'range': range_info
                    }
        
        # Calculate overall score
        if joint_scores:
            results['overall_score'] = round(np.mean(joint_scores))
        
        # Generate recommendations based on scores
        results['recommendations'] = self.generate_recommendations(results['joint_scores'], exercise_key)
        
        return results
    
    def generate_recommendations(self, joint_scores, exercise_key):
        """Generate movement recommendations based on analysis"""
        recommendations = []
        
        for joint, data in joint_scores.items():
            score = data['score']
            actual = data['actual']
            optimal = data['optimal']
            
            if score < 70:  # Below good range
                if actual < optimal:
                    recommendations.append(f"Improve {joint.replace('_', ' ')} mobility - currently limited")
                else:
                    recommendations.append(f"Work on {joint.replace('_', ' ')} control - excessive range")
        
        if not recommendations:
            recommendations.append("Movement pattern shows good quality - maintain current form")
        
        return recommendations
    
    def create_circular_score_chart(self, score, size=(200, 200)):
        """Create a circular progress chart similar to Kinotek"""
        fig, ax = plt.subplots(figsize=(size[0]/100, size[1]/100), subplot_kw=dict(projection='polar'))
        fig.patch.set_facecolor((0, 0, 0, 0))  # Transparent background
        
        # Create the circular progress
        theta = np.linspace(0, 2 * np.pi * (score / 100), 100)
        r = np.ones_like(theta)
        
        # Color based on score
        if score >= 80:
            color = '#27ae60'  # Green
        elif score >= 60:
            color = '#f39c12'  # Orange
        else:
            color = '#e74c3c'  # Red
        
        ax.plot(theta, r, color=color, linewidth=20)
        ax.fill_between(theta, 0, r, alpha=0.3, color=color)
        
        # Style the chart
        ax.set_ylim(0, 1)
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)
        ax.set_rlabel_position(0)
        ax.grid(False)
        ax.set_yticklabels([])
        ax.set_xticklabels([])
        ax.spines['polar'].set_visible(False)
        
        # Add score text in center
        ax.text(0, 0, str(int(score)), fontsize=48, fontweight='bold', 
                ha='center', va='center', transform=ax.transData)
        
        plt.tight_layout()
        
        # Convert to base64 for HTML embedding
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight', 
                   facecolor=(0, 0, 0, 0), edgecolor='none')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        plt.close()
        
        graphic = base64.b64encode(image_png)
        graphic = graphic.decode('utf-8')
        
        return f"data:image/png;base64,{graphic}"
    
    def process_all_files(self):
        """Process all STO files in the folder"""
        if not os.path.exists(self.sto_folder):
            print(f"Folder {self.sto_folder} not found")
            return
        
        sto_files = [f for f in os.listdir(self.sto_folder) if f.endswith('.sto')]
        
        for filename in sto_files:
            filepath = os.path.join(self.sto_folder, filename)
            print(f"Processing {filename}...")
            
            # Extract file info
            file_info = self.extract_athlete_info(filename)
            if not file_info:
                continue
            
            # Read data
            df = self.read_sto_file(filepath)
            if df is None:
                continue
            
            # Analyze movement
            analysis = self.analyze_movement_quality(df, file_info['exercise_key'])
            
            # Store results
            key = f"{file_info['athlete']}_{file_info['exercise']}_{file_info['attempt']}"
            self.data[key] = {
                'info': file_info,
                'dataframe': df,
                'analysis': analysis,
                'filename': filename
            }
    
    def generate_html_report(self, athlete_name):
        """Generate HTML report for a specific athlete"""
        athlete_data = {k: v for k, v in self.data.items() if v['info']['athlete'] == athlete_name}
        
        if not athlete_data:
            print(f"No data found for athlete: {athlete_name}")
            return None
        
        # Calculate overall mobility score
        all_scores = [data['analysis']['overall_score'] for data in athlete_data.values()]
        overall_mobility = round(np.mean(all_scores)) if all_scores else 0
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Movement Analysis Report - {athlete_name}</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background-color: #f8f9fa;
                    color: #333;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                }}
                .header {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 30px;
                    border-bottom: 2px solid #e9ecef;
                    padding-bottom: 20px;
                }}
                .header h1 {{
                    margin: 0;
                    color: #2c3e50;
                    font-size: 28px;
                }}
                .header .logo {{
                    background: #3498db;
                    color: white;
                    padding: 10px 20px;
                    border-radius: 5px;
                    font-weight: bold;
                }}
                .profile-section {{
                    display: flex;
                    align-items: center;
                    margin-bottom: 30px;
                    gap: 30px;
                }}
                .profile-info {{
                    flex: 1;
                }}
                .profile-info h2 {{
                    margin: 0 0 10px 0;
                    color: #2c3e50;
                }}
                .profile-info p {{
                    margin: 5px 0;
                    color: #7f8c8d;
                }}
                .overall-score {{
                    text-align: center;
                }}
                .score-circle {{
                    margin: 10px auto;
                }}
                .score-description {{
                    margin-top: 10px;
                    font-size: 14px;
                    color: #7f8c8d;
                }}
                .exercise-section {{
                    margin: 30px 0;
                    padding: 20px;
                    background: #f8f9fa;
                    border-radius: 8px;
                    border-left: 5px solid #3498db;
                }}
                .exercise-header {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 20px;
                }}
                .exercise-title {{
                    font-size: 20px;
                    font-weight: bold;
                    color: #2c3e50;
                    margin: 0;
                }}
                .exercise-score {{
                    text-align: center;
                }}
                .metrics-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 15px;
                    margin: 20px 0;
                }}
                .metric-card {{
                    background: white;
                    padding: 15px;
                    border-radius: 8px;
                    border: 1px solid #e9ecef;
                }}
                .metric-name {{
                    font-weight: bold;
                    color: #2c3e50;
                    margin-bottom: 5px;
                }}
                .metric-value {{
                    font-size: 18px;
                    color: #3498db;
                    margin-bottom: 3px;
                }}
                .metric-range {{
                    font-size: 12px;
                    color: #7f8c8d;
                }}
                .recommendations {{
                    margin-top: 20px;
                    padding: 15px;
                    background: #e8f4f8;
                    border-radius: 8px;
                    border-left: 4px solid #3498db;
                }}
                .recommendations h4 {{
                    margin: 0 0 10px 0;
                    color: #2c3e50;
                }}
                .recommendations ul {{
                    margin: 0;
                    padding-left: 20px;
                }}
                .recommendations li {{
                    margin: 5px 0;
                    color: #34495e;
                }}
                .score-good {{ color: #27ae60; }}
                .score-medium {{ color: #f39c12; }}
                .score-poor {{ color: #e74c3c; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Movement Analysis Report</h1>
                    <div class="logo">KAI Analytics</div>
                </div>
                
                <div class="profile-section">
                    <div class="profile-info">
                        <h2>Name: {athlete_name}</h2>
                        <p>Report Date: {datetime.now().strftime('%m/%d/%y')}</p>
                        <p>Exercises Analyzed: {len(athlete_data)}</p>
                        <div class="score-description">
                            <p><strong>Mobility Score:</strong> Reflects your range of motion vs. optimal range. 
                            Scores are based on biomechanical research and peer-reviewed sources.</p>
                        </div>
                    </div>
                    <div class="overall-score">
                        <div class="score-circle">
                            <img src="{self.create_circular_score_chart(overall_mobility, (150, 150))}" alt="Overall Score" />
                        </div>
                        <div style="font-weight: bold; margin-top: 10px;">MOBILITY</div>
                    </div>
                </div>
        """
        
        # Add exercise sections
        for key, data in athlete_data.items():
            info = data['info']
            analysis = data['analysis']
            score = analysis['overall_score']
            
            score_class = "score-good" if score >= 80 else "score-medium" if score >= 60 else "score-poor"
            
            html_content += f"""
                <div class="exercise-section">
                    <div class="exercise-header">
                        <h3 class="exercise-title">{info['exercise'].upper()}</h3>
                        <div class="exercise-score">
                            <img src="{self.create_circular_score_chart(score, (100, 100))}" alt="{info['exercise']} Score" />
                        </div>
                    </div>
                    
                    <div class="metrics-grid">
            """
            
            # Add joint metrics
            for joint, joint_data in analysis['joint_scores'].items():
                score_class = "score-good" if joint_data['score'] >= 80 else "score-medium" if joint_data['score'] >= 60 else "score-poor"
                
                html_content += f"""
                    <div class="metric-card">
                        <div class="metric-name">{joint.replace('_', ' ').title()}</div>
                        <div class="metric-value {score_class}">{joint_data['actual']}°</div>
                        <div class="metric-range">Optimal: {joint_data['optimal']}° | Score: {joint_data['score']}</div>
                    </div>
                """
            
            html_content += """
                    </div>
                    
                    <div class="recommendations">
                        <h4>Recommendations</h4>
                        <ul>
            """
            
            for rec in analysis['recommendations']:
                html_content += f"<li>{rec}</li>"
            
            html_content += """
                        </ul>
                    </div>
                </div>
            """
        
        html_content += """
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def save_report(self, athlete_name, output_dir="reports"):
        """Save HTML report to file"""
        os.makedirs(output_dir, exist_ok=True)
        
        html_content = self.generate_html_report(athlete_name)
        if html_content:
            filename = f"{athlete_name}_movement_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"Report saved: {filepath}")
            return filepath
        return None
    
    def create_download_link(self, html_content, athlete_name):
        """Create a download link for HTML report content (for cloud deployment)"""
        if html_content:
            # Encode content for download
            import base64
            b64_content = base64.b64encode(html_content.encode('utf-8')).decode()
            
            # Create filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{athlete_name}_movement_report_{timestamp}.html"
            
            # Create download URL
            download_url = f"data:text/html;base64,{b64_content}"
            
            return download_url, filename
        return None, None
    
    def create_downloadable_report_with_pdf_option(self, athlete_name):
        """Generate HTML report with PDF download option for cloud deployment"""
        athlete_data = {k: v for k, v in self.data.items() if v['info']['athlete'] == athlete_name}
        
        if not athlete_data:
            print(f"No data found for athlete: {athlete_name}")
            return None, None
        
        # Generate the base HTML report
        html_content = self.generate_html_report(athlete_name)
        if not html_content:
            return None, None
        
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
        
        # Create download link
        return self.create_download_link(html_content, athlete_name)
