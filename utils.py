# -*- coding: utf-8 -*-
"""
Utility functions and helper classes for the Kinematic Dashboard
Contains data processing, file handling, and analysis utilities
"""

import os
import pandas as pd
from config import sto_files, STO_FOLDER, athlete_id_mapping, id_to_athlete_mapping, workout_display_mapping, display_to_workout_mapping, athlete_prefix_mapping


class DataProcessor:
    """Class for handling data processing operations"""
    
    def __init__(self):
        self.dfs = {}
        self.load_all_sto_files()
    
    def read_sto_file(self, path):
        """Read a single .sto file and return DataFrame"""
        with open(path) as f:
            for i, line in enumerate(f):
                if 'endheader' in line:
                    header_line = i
                    break
        df = pd.read_csv(path, sep='\t', header=header_line-1)
        return df
    
    def load_all_sto_files(self):
        """Load all .sto files into memory"""
        self.dfs = {
            fname: self.read_sto_file(os.path.join(STO_FOLDER, fname)) 
            for fname in sto_files
        }
    
    def get_dataframe(self, filename):
        """Get DataFrame for a specific file"""
        return self.dfs.get(filename)
    
    def get_all_dataframes(self):
        """Get all loaded DataFrames"""
        return self.dfs


class FileAnalyzer:
    """Class for analyzing file patterns and extracting metadata"""
    
    @staticmethod
    def get_athlete_from_filename(filename):
        """Extract athlete name from filename (new format: MMDDYYYY_athleteID_workoutname_attemptNumber_suffix.sto)"""
        import re
        # Pattern: MMDDYYYY_athleteID_workoutname_attemptNumber_suffix.sto
        match = re.match(r'\d{8}_(\d+)_[^_]+_\d+_', filename)
        if match:
            athlete_id = match.group(1)
            return id_to_athlete_mapping.get(athlete_id)
        return None
    
    @staticmethod
    def get_exercise_from_filename(filename):
        """Extract exercise type from filename (new format: MMDDYYYY_athleteID_workoutname_attemptNumber_suffix.sto)"""
        import re
        # Pattern: MMDDYYYY_athleteID_workoutname_attemptNumber_suffix.sto
        match = re.match(r'\d{8}_\d+_([^_]+)_\d+_', filename)
        if match:
            workout_name = match.group(1)
            return workout_display_mapping.get(workout_name)
        return None
    
    @staticmethod
    def get_attempt_from_filename(filename):
        """Extract attempt number from filename (new format: MMDDYYYY_athleteID_workoutname_attemptNumber_suffix.sto)"""
        import re
        # Pattern: MMDDYYYY_athleteID_workoutname_attemptNumber_suffix.sto
        match = re.match(r'\d{8}_\d+_[^_]+_(\d+)_', filename)
        if match:
            return int(match.group(1))
        return None


class HierarchicalSelector:
    """Class for managing hierarchical dropdown selections"""
    
    def __init__(self):
        self.file_analyzer = FileAnalyzer()
    
    def get_athletes_from_files(self):
        """Get unique athletes from available files"""
        athletes = set()
        for fname in sto_files:
            athlete = self.file_analyzer.get_athlete_from_filename(fname)
            if athlete:
                athletes.add(athlete)
        return sorted(list(athletes))
    
    def get_exercises_for_athlete(self, athlete):
        """Get available exercises for a specific athlete"""
        exercises = set()
        for fname in sto_files:
            if self.file_analyzer.get_athlete_from_filename(fname) == athlete:
                exercise = self.file_analyzer.get_exercise_from_filename(fname)
                if exercise:
                    exercises.add(exercise)
        return sorted(list(exercises))
    
    def get_attempts_for_athlete_exercise(self, athlete, exercise):
        """Get available attempt numbers for a specific athlete and exercise"""
        attempts = set()
        for fname in sto_files:
            if (self.file_analyzer.get_athlete_from_filename(fname) == athlete and 
                self.file_analyzer.get_exercise_from_filename(fname) == exercise):
                attempt = self.file_analyzer.get_attempt_from_filename(fname)
                if attempt:
                    attempts.add(attempt)
        return sorted(list(attempts))
    
    def construct_filename_from_hierarchy(self, athlete, exercise, attempt):
        """Construct filename from hierarchical selection (new format: MMDDYYYY_athleteID_workoutname_attemptNumber_suffix.sto)"""
        if not all([athlete, exercise, attempt]):
            return None
        
        athlete_id = athlete_id_mapping.get(athlete)
        if not athlete_id:
            return None
        
        # Map exercise display names to workout names
        workout_name = display_to_workout_mapping.get(exercise)
        if not workout_name:
            return None
        
        # Construct filename based on new pattern: MMDDYYYY_athleteID_workoutname_attemptNumber_Kinematics_q.sto
        # Using the current date format from the renamed files
        filename = f"07092025_{athlete_id}_{workout_name}_{attempt}_Kinematics_q.sto"
        
        # Check if the constructed filename exists in our files
        if filename in sto_files:
            return filename
        
        return None
    
    def construct_video_filename(self, athlete, exercise, attempt):
        """Construct video filename from hierarchical selection (new format: MMDDYYYY_athleteID_workoutname_attemptNumber.webm)"""
        if not all([athlete, exercise, attempt]):
            return None
        
        athlete_id = athlete_id_mapping.get(athlete)
        if not athlete_id:
            return None
        
        # Map exercise display names to workout names
        workout_name = display_to_workout_mapping.get(exercise)
        if not workout_name:
            return None
        
        # Construct video filename: MMDDYYYY_athleteID_workoutname_attemptNumber.webm
        video_filename = f"07092025_{athlete_id}_{workout_name}_{attempt}.webm"
        return video_filename
    
    def get_files_for_athlete_exercise(self, athlete, exercise):
        """Get files matching athlete and exercise"""
        matching_files = []
        for fname in sto_files:
            if (self.file_analyzer.get_athlete_from_filename(fname) == athlete and 
                self.file_analyzer.get_exercise_from_filename(fname) == exercise):
                matching_files.append(fname)
        return matching_files


class NotesManager:
    """Class for managing analysis notes and file operations"""
    
    @staticmethod
    def save_notes_to_file(key_takeaways, observations, recommendations):
        """Save analysis notes to a timestamped file - LOCAL VERSION"""
        import datetime
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analysis_notes_{timestamp}.txt"
        
        try:
            with open(filename, 'w') as f:
                f.write(f"Analysis Notes - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*60 + "\n\n")
                
                # Key Takeaways section
                f.write("KEY TAKEAWAYS:\n")
                f.write("-" * 15 + "\n")
                f.write(key_takeaways if key_takeaways else "(No key takeaways recorded)\n")
                f.write("\n\n")
                
                # Observations section
                f.write("OBSERVATIONS:\n")
                f.write("-" * 20 + "\n")
                f.write(observations if observations else "(No observations recorded)\n")
                f.write("\n\n")
                
                # Recommendations section
                f.write("RECOMMENDED MOVEMENTS:\n")
                f.write("-" * 25 + "\n")
                f.write(recommendations if recommendations else "(No recommendations recorded)\n")
            
            return filename, None
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def generate_notes_content(key_takeaways, observations, recommendations):
        """Generate notes content as string for download or database storage"""
        import datetime
        
        content = []
        content.append(f"Analysis Notes - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        content.append("="*60)
        content.append("")
        
        # Key Takeaways section
        content.append("KEY TAKEAWAYS:")
        content.append("-" * 15)
        content.append(key_takeaways if key_takeaways else "(No key takeaways recorded)")
        content.append("")
        content.append("")
        
        # Observations section
        content.append("OBSERVATIONS:")
        content.append("-" * 20)
        content.append(observations if observations else "(No observations recorded)")
        content.append("")
        content.append("")
        
        # Recommendations section
        content.append("RECOMMENDED MOVEMENTS:")
        content.append("-" * 25)
        content.append(recommendations if recommendations else "(No recommendations recorded)")
        
        return "\n".join(content)
    
    @staticmethod
    def create_download_link(content, filename=None):
        """Create a download link for notes content"""
        import base64
        import datetime
        
        if filename is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"analysis_notes_{timestamp}.txt"
        
        # Encode content for download
        b64_content = base64.b64encode(content.encode()).decode()
        download_url = f"data:text/plain;base64,{b64_content}"
        
        return download_url, filename


# Initialize global instances
data_processor = DataProcessor()
hierarchical_selector = HierarchicalSelector()
notes_manager = NotesManager()
