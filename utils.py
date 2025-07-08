# -*- coding: utf-8 -*-
"""
Utility functions and helper classes for the Kinematic Dashboard
Contains data processing, file handling, and analysis utilities
"""

import os
import pandas as pd
from config import sto_files, STO_FOLDER, athlete_prefix_mapping


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
        """Extract athlete name from filename"""
        if 'G1' in filename or 'G2' in filename:
            return 'Gabby'
        elif 'H1' in filename:
            return 'Hannah'
        elif 'A1' in filename:
            return 'Aaron'
        return None
    
    @staticmethod
    def get_exercise_from_filename(filename):
        """Extract exercise type from filename"""
        if 'squat' in filename.lower():
            return 'squat'
        elif 'sprint' in filename.lower():
            return 'sprint'
        elif 'shootaround' in filename.lower():
            return 'shootaround'
        return None
    
    @staticmethod
    def get_attempt_from_filename(filename):
        """Extract attempt number from filename"""
        if 'G1' in filename or 'H1' in filename or 'A1' in filename:
            return 1
        elif 'G2' in filename:
            return 2
        # Add more attempt logic as needed
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
        """Construct filename from hierarchical selection"""
        if not all([athlete, exercise, attempt]):
            return None
        
        athlete_prefix = athlete_prefix_mapping.get(athlete)
        if not athlete_prefix:
            return None
        
        # Construct filename based on pattern: 0627{athlete_prefix}{attempt}{exercise}_Kinematics_q.sto
        filename = f"0627{athlete_prefix}{attempt}{exercise}_Kinematics_q.sto"
        
        # Check if the constructed filename exists in our files
        if filename in sto_files:
            return filename
        
        return None
    
    def construct_video_filename(self, athlete, exercise, attempt):
        """Construct video filename from hierarchical selection"""
        if not all([athlete, exercise, attempt]):
            return None
        
        athlete_prefix = athlete_prefix_mapping.get(athlete)
        if not athlete_prefix:
            return None
        
        # Construct video filename: 0627{athlete_prefix}{attempt}{exercise}.webm
        video_filename = f"0627{athlete_prefix}{attempt}{exercise}.webm"
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
        """Save analysis notes to a timestamped file"""
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


# Initialize global instances
data_processor = DataProcessor()
hierarchical_selector = HierarchicalSelector()
notes_manager = NotesManager()
