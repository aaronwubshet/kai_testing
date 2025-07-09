#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File Renamer Script for KAI Dashboard
Renames .sto files from old format to new naming convention
Old: 0708A1overheadsquat_Kinematics_q.sto
New: 07092025_1_overheadsquat_1_Kinematics_q.sto
"""

import os
import re
from datetime import datetime

# Athlete mapping: old letter code -> new athlete ID
ATHLETE_MAPPING = {
    'A': '1',  # Aaron
    'G': '2',  # Gabby  
    'H': '3'   # Hannah
}

# Date mapping: old date -> new date (MMDDYYYY format)
# Assuming old "0708" means July 8th, converting to current year
OLD_DATE = "0708"  # July 8th
NEW_DATE = "07092025"  # July 9th, 2025 (current date)

def parse_old_filename(filename):
    """
    Parse old filename format: 0708A1overheadsquat_Kinematics_q.sto
    Returns: (date, athlete_code, attempt, workout, suffix)
    """
    # Remove .sto extension
    base_name = filename.replace('.sto', '')
    
    # Pattern: 4-digit date + athlete letter + attempt number + workout name + suffix
    pattern = r'^(\d{4})([AGH])(\d+)([a-zA-Z]+)(.*)$'
    match = re.match(pattern, base_name)
    
    if match:
        date, athlete_code, attempt, workout, suffix = match.groups()
        return date, athlete_code, attempt, workout, suffix
    
    return None

def create_new_filename(date, athlete_code, attempt, workout, suffix):
    """
    Create new filename format: MMDDYYYY_athleteID_workoutname_attemptNumber_suffix.sto
    """
    # Map athlete code to new ID
    athlete_id = ATHLETE_MAPPING.get(athlete_code)
    if not athlete_id:
        return None
    
    # Use new date format
    new_date = NEW_DATE
    
    # Create new filename
    new_name = f"{new_date}_{athlete_id}_{workout}_{attempt}{suffix}.sto"
    return new_name

def rename_files(directory=".", dry_run=True):
    """
    Rename all .sto files in the directory
    
    Args:
        directory: Directory containing .sto files
        dry_run: If True, only show what would be renamed without actually renaming
    """
    print(f"{'DRY RUN - ' if dry_run else ''}Renaming files in: {os.path.abspath(directory)}")
    print("=" * 60)
    
    sto_files = [f for f in os.listdir(directory) if f.endswith('.sto')]
    
    if not sto_files:
        print("No .sto files found in directory")
        return
    
    renamed_count = 0
    error_count = 0
    
    for filename in sto_files:
        print(f"\nProcessing: {filename}")
        
        # Parse old filename
        parsed = parse_old_filename(filename)
        if not parsed:
            print(f"  ❌ ERROR: Could not parse filename format")
            error_count += 1
            continue
        
        date, athlete_code, attempt, workout, suffix = parsed
        print(f"  📋 Parsed: date={date}, athlete={athlete_code}, attempt={attempt}, workout={workout}, suffix={suffix}")
        
        # Create new filename
        new_filename = create_new_filename(date, athlete_code, attempt, workout, suffix)
        if not new_filename:
            print(f"  ❌ ERROR: Could not create new filename")
            error_count += 1
            continue
        
        print(f"  ➡️  New name: {new_filename}")
        
        # Check if new filename already exists
        old_path = os.path.join(directory, filename)
        new_path = os.path.join(directory, new_filename)
        
        if os.path.exists(new_path):
            print(f"  ⚠️  WARNING: Target file already exists: {new_filename}")
            continue
        
        # Rename the file (if not dry run)
        if not dry_run:
            try:
                os.rename(old_path, new_path)
                print(f"  ✅ RENAMED: {filename} -> {new_filename}")
                renamed_count += 1
            except Exception as e:
                print(f"  ❌ ERROR renaming file: {e}")
                error_count += 1
        else:
            print(f"  🔍 WOULD RENAME: {filename} -> {new_filename}")
            renamed_count += 1
    
    print("\n" + "=" * 60)
    print(f"SUMMARY:")
    print(f"  Total files processed: {len(sto_files)}")
    print(f"  {'Would be renamed' if dry_run else 'Successfully renamed'}: {renamed_count}")
    print(f"  Errors: {error_count}")
    
    if dry_run:
        print(f"\n🔍 This was a DRY RUN - no files were actually renamed")
        print(f"   Run with dry_run=False to perform actual renaming")

def show_mapping_preview():
    """Show the athlete and naming convention mapping"""
    print("RENAMING CONVENTION:")
    print("=" * 40)
    print("Old Format: 0708A1overheadsquat_Kinematics_q.sto")
    print("New Format: 07092025_1_overheadsquat_1_Kinematics_q.sto")
    print()
    print("ATHLETE MAPPING:")
    print("  A (Aaron)  -> 1")
    print("  G (Gabby)  -> 2") 
    print("  H (Hannah) -> 3")
    print()
    print("DATE MAPPING:")
    print(f"  {OLD_DATE} -> {NEW_DATE}")
    print()

if __name__ == "__main__":
    import sys
    
    # Show mapping info
    show_mapping_preview()
    
    # Get directory (default to current directory)
    directory = "." if len(sys.argv) < 2 else sys.argv[1]
    
    # Run dry run first
    print("STEP 1: DRY RUN")
    print("=" * 40)
    rename_files(directory, dry_run=True)
    
    print("\n" * 2)
    
    # Ask user for confirmation
    response = input("Do you want to proceed with the actual renaming? (y/N): ").strip().lower()
    
    if response in ['y', 'yes']:
        print("\nSTEP 2: ACTUAL RENAMING")
        print("=" * 40)
        rename_files(directory, dry_run=False)
    else:
        print("\n❌ Renaming cancelled by user")
