# Kinematic Dashboard - Complete Documentation

A modern, modular web application for analyzing kinematic data with hierarchical navigation, athlete profiles, and comprehensive reporting capabilities.

## 🚀 Quick Start

```bash
# Clone and navigate to project
cd testing_os/

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

Visit `http://localhost:8050` to access the dashboard.

## 📁 Project Structure

```
testing_os/
├── app.py                  # Main application entry point
├── config.py              # Configuration and mappings
├── utils.py               # Utility functions and data processing
├── layout.py              # UI layout components
├── callbacks.py           # Dash callback functions
├── requirements.txt       # Python dependencies
├── STOfiles/              # Kinematic data files (.sto format)
│   ├── file_renamer.py    # Batch file renaming script
│   └── old/               # Original files (backup)
├── assets/                # Static assets
│   ├── images/            # Athlete photos and icons
│   └── videos/            # Movement videos
├── static_report/         # Report generation
│   └── report_generator.py # Professional report creation
└── reports/               # Generated analysis reports
```

## 🏗️ Architecture Overview

### New File Naming Convention

The app now uses a standardized naming convention for better organization and extensibility:

**Format**: `MMDDYYYY_athleteID_workoutname_attemptNumber_suffix.sto`

**Examples**:
- `07092025_1_overheadsquat_1_Kinematics_q.sto` (Aaron, Overhead Squat, Attempt 1)
- `07092025_2_squat_3_Kinematics_q.sto` (Gabby, Squat, Attempt 3)
- `07092025_3_pushup_2_Kinematics_q.sto` (Hannah, Push Up, Attempt 2)

### Extensible Mappings

#### Athlete ID Mapping
```python
athlete_id_mapping = {
    'Aaron': '1',
    'Gabby': '2', 
    'Hannah': '3'
    # Easy to add new athletes
}
```

#### Workout Display Mapping
```python
workout_display_mapping = {
    'overheadsquat': 'Overhead Squat',
    'squat': 'Squat',
    'pushup': 'Push Up',
    'standingjump': 'Vertical Jump'
    # Easy to add new workouts
}
```

## 🔧 Core Modules

### `app.py` - Main Application Entry Point
- Initializes the Dash app
- Sets up the main layout
- Registers all callbacks
- Contains run configuration

### `config.py` - Configuration and Constants
**Key Features**:
- **Extensible Athlete Mapping**: Easy addition of new athletes
- **Workout Display Names**: Configurable exercise mappings
- **Metrics Configuration**: Internalized metric groups (no CSV dependency)
- **Styling Constants**: Centralized color scheme and component IDs
- **Cloud Deployment Detection**: Automatic platform detection

**Key Contents**:
- `athlete_id_mapping` - Numeric athlete identifiers
- `workout_display_mapping` - Exercise name mappings
- `metric_groups` - Organized body part metrics
- `COLORS` - Application color scheme
- `COMPONENT_IDS` - Component identifier constants

### `utils.py` - Utility Functions and Helper Classes

#### `DataProcessor`
- Loads and manages .sto file data
- Provides DataFrame access
- Handles file reading and processing

#### `FileAnalyzer`
- **NEW**: Parses new filename convention
- Extracts athlete, exercise, and attempt information
- Supports both old and new filename formats

#### `HierarchicalSelector`
- **REFACTORED**: Uses new filename convention
- Manages 5-level dropdown hierarchy
- Constructs filenames dynamically
- Generates video file paths

#### `NotesManager`
- **ENHANCED**: Cloud-deployment ready
- Local file saving for development
- Download functionality for cloud platforms
- Timestamped analysis notes

### `layout.py` - UI Layout Components

#### `HierarchicalDropdownsLayout`
- **ONLY INTERFACE**: Legacy file selection removed
- 5-level selection: Athlete → Exercise → Attempt → Metric Group → Metrics
- Dynamic option loading
- Cascading dropdown updates

#### `AthleteProfileLayout`
- Dynamic athlete profile display
- Athlete photos and statistics
- Responsive design

#### `VideoAnalysisLayout`
- Dynamic video player
- Automatic video filename construction
- Synchronized with data selection

#### `NotesLayout`
- Analysis notes interface
- **DUAL SAVE OPTIONS**: Local and download
- Cloud deployment awareness

### `callbacks.py` - Callback Functions

#### `HierarchicalDropdownCallbacks` (Core)
- **ONLY SELECTION METHOD**: File selection removed
- 5-level dropdown cascade logic
- Dynamic option updates
- State management

#### `AthleteProfileCallbacks`
- Dynamic profile updates
- Photo and information display

#### `MetricsSelectionCallbacks`
- Metric selection and display
- Selected metrics management

#### `VideoPlayerCallbacks`
- **NEW**: Dynamic video loading
- Filename construction from selections

#### `PlotCallbacks`
- **ENHANCED**: Uses hierarchical selection
- Kinematic plot generation
- Multi-metric visualization

#### `NotesCallbacks`
- **CLOUD-READY**: Dual save functionality
- Local development support
- Download for cloud deployment

## 🌐 Cloud Deployment

### Platform Support
- ✅ **Render** (Recommended)
- ✅ **Heroku**
- ✅ **Vercel**
- ✅ **AWS**
- ✅ **Other cloud platforms**

### Automatic Cloud Detection
```python
# In config.py
IS_CLOUD_DEPLOYMENT = bool(os.environ.get("RENDER") or 
                          os.environ.get("HEROKU") or 
                          os.environ.get("VERCEL") or
                          os.environ.get("PORT"))
```

### Notes Saving Solutions

#### 🚨 Cloud Platform Limitations
- **Ephemeral File System**: Files disappear on restart
- **No Persistent Local Storage**: Container restarts lose data
- **Regular Restarts**: Every 24 hours, deployments, scaling

#### ✅ Solutions Implemented

**1. Download Functionality (Recommended for Cloud)**
- ✅ Works on all cloud platforms
- ✅ No server storage required
- ✅ Users get persistent files
- ✅ No data loss on restarts

```python
# Generate downloadable notes
content = notes_manager.generate_notes_content(takeaways, observations, recommendations)
download_url, filename = notes_manager.create_download_link(content)
```

**2. Local Save (For Development)**
- ✅ Works in local development
- ⚠️ Shows warning on cloud platforms
- 📝 Files disappear on cloud deployment

### Notes Content Format
```
Analysis Notes - 2025-07-09 14:30:25
============================================================

KEY TAKEAWAYS:
---------------
• Primary insights from movement analysis
• Critical findings and patterns
• Main conclusions and recommendations

OBSERVATIONS:
--------------------
• Detailed movement patterns
• Biomechanical findings
• Joint-specific observations

RECOMMENDED MOVEMENTS:
-------------------------
• Corrective exercise suggestions
• Training modifications
• Technical improvements
```

### Deployment Options

#### Option 1: Current Implementation (Recommended)
- ✅ **No additional setup required**
- ✅ **Works on all platforms**
- ✅ **No external dependencies**
- ✅ **Users download their notes**

#### Option 2: Database Storage (Advanced)
```python
# Add to requirements.txt
psycopg2-binary==2.9.7  # PostgreSQL
# or
pymongo==4.5.0         # MongoDB
```

#### Option 3: Cloud Storage (Professional)
```python
# AWS S3, Google Cloud Storage, etc.
import boto3
```

## 📋 Render Deployment Guide

### Current Setup (Works Immediately)
1. **Deploy current code** → Works out of the box
2. **Users click "Download Notes"** → Files saved to user's computer
3. **No server storage needed** → No additional configuration
4. **Automatic platform detection** → App adapts automatically

### Environment Variables
Render automatically sets:
- `RENDER=true` (detected by app)
- `PORT=10000` (detected by app)
- App automatically adapts behavior

### User Experience
1. User analyzes movement data
2. User fills out analysis forms
3. User clicks **"Download Notes"**
4. Browser downloads `analysis_notes_20250709_143025.txt`
5. User has permanent copy of analysis

## 📊 Report Generator

### Professional Movement Analysis Reports

The app includes a sophisticated report generator that creates professional HTML reports similar to industry standards like Kinotek.

#### Features
- **Professional HTML Output**: KAI Analytics branded reports
- **Circular Progress Charts**: Visual mobility scoring
- **Joint-Specific Analysis**: Detailed range of motion assessment
- **Movement Recommendations**: Biomechanical improvement suggestions
- **Responsive Design**: Works on all devices
- **Cloud-Friendly PDF Download**: Opens in new tab with PDF download button

#### Updated for New File Structure
- ✅ **New Filename Parsing**: Supports `MMDDYYYY_athleteID_workoutname_attemptNumber_suffix.sto`
- ✅ **Backward Compatible**: Still works with legacy filename formats
- ✅ **Smart Path Detection**: Automatically finds STOfiles from any directory
- ✅ **Athlete ID Mapping**: Maps numeric IDs (1=Aaron, 2=Gabby, 3=Hannah)
- ✅ **Workout Mapping**: Maps internal names to display names

#### Report Generation Process
1. User selects athlete data in the main dashboard
2. User clicks "Generate Movement Report"
3. System processes all available files for the athlete
4. Report automatically opens in a new tab with built-in PDF download button

#### Streamlined Cloud Deployment Workflow
The fully automated workflow works seamlessly for both local and cloud deployments:

1. **Generate & Open**: Click "Generate Movement Report" button
2. **Automatic Opening**: Report automatically opens in a new browser tab
3. **Save as PDF**: Use the "Download PDF" button in the top-right corner of the report

#### Technical Implementation
```python
# Report generator with automatic opening
from static_report.report_generator import KinematicReportGenerator

generator = KinematicReportGenerator("STOfiles")
generator.process_all_files()

# Creates downloadable HTML that automatically opens in new tab
download_url, filename = generator.create_downloadable_report_with_pdf_option(athlete_name)

# Client-side callback automatically opens the report
# Uses window.open() to open the data URL in a new tab
```

#### PDF Download Features
- **Fixed Position Button**: Always visible in top-right corner
- **Professional Styling**: Matches KAI Analytics branding
- **Print Optimization**: Automatically hides button when printing
- **Responsive Layout**: Works on all screen sizes
- **Cross-Browser Support**: Uses standard `window.print()` function

## 🔄 File Migration

### Batch File Renaming
The project includes a script to rename files to the new convention:

```bash
cd STOfiles/
python file_renamer.py
```

**Features**:
- Dry run mode for safety
- Automatic athlete mapping
- Date format conversion
- Backup creation

### Migration Results
- ✅ All .sto files renamed to new convention
- ✅ Original files backed up in `old/` directory
- ✅ App updated to use new naming
- ✅ Dynamic filename construction working

## 🚀 Key Features

### Modular Architecture Benefits
1. **Separation of Concerns**: Each module has specific responsibility
2. **Maintainability**: Easy to locate and modify functionality
3. **Scalability**: Easy to add features without affecting existing code
4. **Extensibility**: Simple athlete and workout additions
5. **Testing**: Each module can be tested independently

### Enhanced User Experience
- **Hierarchical Navigation**: Intuitive 5-level selection
- **Dynamic Content**: Athlete profiles and videos update automatically
- **Cloud-Ready**: Works seamlessly on all platforms
- **Professional Reports**: Downloadable analysis notes
- **Responsive Design**: Works on all device sizes

### Data Flow
1. **Configuration** loads extensible mappings
2. **Utils** process data with new filename convention
3. **Layout** creates hierarchical interface
4. **Callbacks** handle dynamic updates
5. **App** coordinates cloud-ready functionality

## 🛠️ Development

### Adding New Athletes
```python
# In config.py
athlete_id_mapping['NewAthlete'] = '4'
athlete_profiles['NewAthlete'] = {
    'name': 'New Athlete Name',
    'photo': 'images/newathlete.jpeg',
    # ... other profile data
}
```

### Adding New Workouts
```python
# In config.py
workout_display_mapping['newworkout'] = 'New Workout Display Name'
```

### Adding New Metrics
```python
# In config.py
metric_groups['New Body Part'] = [
    'new_metric_1',
    'new_metric_2',
    # ... additional metrics
]
```

### Development Guidelines
- **Component IDs**: Use `COMPONENT_IDS` for consistency
- **Colors**: Use `COLORS` constants for styling
- **Error Handling**: Use try-catch blocks and `PreventUpdate`
- **Documentation**: Add docstrings to all functions
- **File Naming**: Follow new convention for data files

## 🔮 Future Enhancements

### Phase 1: Current (Complete)
- ✅ Hierarchical dropdown interface
- ✅ New file naming convention
- ✅ Cloud deployment ready
- ✅ Download functionality

### Phase 2: Database Integration
- User accounts and authentication
- Persistent analysis history
- Shared analyses between users
- Advanced search and filtering

### Phase 3: Professional Features
- Real-time collaboration
- Advanced analytics dashboard
- Cloud storage integration
- API for third-party integrations

## 📊 Current Status

### Refactoring Complete
- ✅ **File naming convention updated**
- ✅ **All legacy file selection removed**
- ✅ **Hierarchical dropdown only interface**
- ✅ **Extensible athlete and workout mappings**
- ✅ **Cloud deployment ready**
- ✅ **Report generator updated and integrated**
- ✅ **App tested and working**

### Files Processed
- **36 .sto files** renamed to new convention
- **All athletes**: Aaron (ID: 1), Gabby (ID: 2), Hannah (ID: 3)
- **All workouts**: Overhead Squat, Squat, Push Up, Vertical Jump
- **All attempts**: 1, 2, 3 for each athlete/workout combination

## 🎯 Recommendations

### For Immediate Use
- ✅ **Deploy current implementation**
- ✅ **Use download functionality**
- ✅ **No additional setup required**
- ✅ **Perfect for cloud deployment**

### For Future Development
- Consider database integration for user accounts
- Add real-time collaboration features
- Implement advanced analytics
- Create mobile-responsive enhancements

## 🧪 Testing

### Functionality Verified
- ✅ **Hierarchical dropdowns working**
- ✅ **Dynamic athlete profiles**
- ✅ **Video player integration**
- ✅ **Plot generation**
- ✅ **Notes download**
- ✅ **Cloud deployment compatibility**

### Browser Compatibility
- ✅ **Chrome** (Recommended)
- ✅ **Firefox**
- ✅ **Safari**
- ✅ **Edge**

## 📞 Support

The application is ready for production deployment with:
- **Comprehensive documentation**
- **Modular, maintainable code**
- **Cloud-ready architecture**
- **Extensible configuration**
- **Professional user experience**

Your kinematic analysis dashboard is **ready to deploy**! 🚀
