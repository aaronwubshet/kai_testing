# Kinematic Dashboard

A modern web application for analyzing kinematic data with hierarchical navigation, athlete profiles, and comprehensive reporting capabilities.

## 🚀 Quick Start

```bash
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
├── assets/                # Static assets (images, videos, reports)
└── static_report/         # Professional report generation
```

## 🏗️ Key Features

### File Naming Convention
**Format**: `MMDDYYYY_athleteID_workoutname_attemptNumber_suffix.sto`

**Examples**:
- `07092025_1_overheadsquat_1_Kinematics_q.sto` (Aaron, Overhead Squat, Attempt 1)
- `07092025_2_squat_3_Kinematics_q.sto` (Gabby, Squat, Attempt 3)

### Hierarchical Navigation
5-level dropdown system:
1. **Athlete** → 2. **Exercise** → 3. **Attempt** → 4. **Metric Group** → 5. **Metrics**

### Extensible Configuration
- **Athlete Mapping**: Easy addition of new athletes in `config.py`
- **Exercise Mapping**: Configurable workout display names
- **Metric Groups**: Organized body part metrics
- **Color Scheme**: Centralized styling constants

## 📊 Report Generation

### Professional Movement Analysis Reports
- **HTML Output**: KAI Analytics branded reports
- **Visual Charts**: Circular progress and mobility scoring
- **Joint Analysis**: Detailed range of motion assessment
- **Movement Recommendations**: Biomechanical improvement suggestions
- **PDF Download**: Built-in PDF export via browser print

### Workflow
1. Select athlete from dropdown
2. Click "Generate Movement Report"
3. Report automatically opens in new tab
4. Use "Download PDF" button to save as PDF

### Browser Compatibility
- ✅ Chrome, Safari, Firefox, Edge
- ✅ Works on all cloud platforms (Render, Heroku, Vercel)

## 🌐 Cloud Deployment

### Automatic Platform Detection
```python
IS_CLOUD_DEPLOYMENT = bool(os.environ.get("RENDER") or 
                          os.environ.get("HEROKU") or 
                          os.environ.get("VERCEL"))
```

### Features
- **Assets-based Reports**: HTML files served from `/assets/` folder
- **Cross-browser Support**: Works in Safari, Chrome, and all modern browsers
- **Ephemeral-friendly**: No persistent file storage required
- **Download Functionality**: Cloud-ready notes and report downloads

## 🔧 Core Architecture

### Modular Design
- **`config.py`**: Centralized configuration and mappings
- **`utils.py`**: Data processing and helper functions
- **`layout.py`**: UI components and responsive design
- **`callbacks.py`**: Interactive functionality and state management

### Data Flow
1. **File Selection**: Hierarchical dropdown navigation
2. **Data Processing**: Automatic .sto file loading and analysis
3. **Visualization**: Dynamic plots and athlete profiles
4. **Report Generation**: Professional HTML reports with PDF export
5. **Notes System**: Cloud-friendly analysis notes with download

## 🚀 Development

### Local Development
```bash
python app.py  # Runs on http://localhost:8050
```

### Production Deployment
The app automatically detects cloud environments and configures accordingly:
- **Debug Mode**: Disabled in production
- **Host Configuration**: `0.0.0.0` for cloud deployment
- **Port Detection**: Uses environment `PORT` variable

### Adding New Features
- **Athletes**: Add to `athlete_id_mapping` in `config.py`
- **Exercises**: Add to `workout_display_mapping` in `config.py`
- **Metrics**: Add to `metric_groups` in `config.py`
- **Styling**: Modify `COLORS` constants in `config.py`

## 📋 Deployment

### Environment Variables
Cloud platforms automatically set:
- `RENDER=true` / `HEROKU=true` / `VERCEL=true` (detected by app)
- `PORT=10000` (detected by app)

### User Experience
1. Select athlete and exercise data via hierarchical dropdowns
2. View kinematic plots and athlete profiles
3. Generate professional reports with automatic new tab opening
4. Download analysis notes and PDF reports directly to device

## 🛠️ Technical Notes

### File Structure
- **Hierarchical Navigation**: 5-level dropdown system for intuitive data selection
- **Extensible Mappings**: Easy addition of athletes, exercises, and metrics
- **Cloud-Ready**: Assets-based report serving for cross-browser compatibility
- **Professional Output**: Branded HTML reports with PDF download capability

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
