# Kinematic Dashboard - Modular Architecture

This project has been refactored into a modular structure for better organization, maintainability, and scalability.

## Project Structure

```
testing_os/
├── app.py                  # Main application entry point
├── config.py              # Global configuration and constants
├── utils.py               # Utility functions and helper classes
├── layout.py              # UI layout components and structures
├── callbacks.py           # Dash callback functions
├── internal_sandbox.py    # Original monolithic file (kept for reference)
├── assets/                # Static assets (images, videos, CSS)
├── STOfiles/              # Data files (.sto format)
└── metrics.csv            # Metrics configuration
```

## Module Descriptions

### `app.py` - Main Application Entry Point
- Initializes the Dash app
- Sets up the main layout
- Registers all callbacks
- Contains run configuration

**Usage:**
```python
python app.py
```

### `config.py` - Configuration and Constants
- **Global Variables**: File paths, folder locations
- **Data Configuration**: File mappings, athlete profiles
- **Styling Constants**: Colors, component IDs
- **Metrics Configuration**: Loads and processes metrics from CSV
- **Application Settings**: Debug mode, app title, etc.

**Key Contents:**
- `STO_FOLDER`, `ASSETS_FOLDER`, `VIDEOS_FOLDER`
- `athlete_profiles` - Athlete information and photos
- `file_mapping` - Readable names for data files
- `metric_groups` - Organized metrics from CSV
- `COLORS` - Color scheme constants
- `COMPONENT_IDS` - Centralized component ID management

### `utils.py` - Utility Functions and Helper Classes
Contains specialized classes for different aspects of data processing:

#### `DataProcessor`
- Loads and manages .sto file data
- Provides access to DataFrames
- Handles file reading and processing

#### `FileAnalyzer`
- Extracts metadata from filenames
- Identifies athletes, exercises, attempts
- Static methods for pattern matching

#### `HierarchicalSelector`
- Manages hierarchical dropdown logic
- Constructs filenames from selections
- Generates video file paths
- Provides options for dropdowns

#### `NotesManager`
- Handles saving analysis notes
- Creates timestamped files
- Manages file I/O operations

### `layout.py` - UI Layout Components
Organized layout classes for different UI sections:

#### `HeaderLayout`
- Application title and debug toggle
- Top navigation bar

#### `AthleteProfileLayout`
- Athlete information display
- Profile photos and statistics

#### `HierarchicalDropdownsLayout`
- 5-level hierarchical selection system
- Athlete → Exercise → Attempt → Metric Group → Metrics

#### `SelectedMetricsLayout`
- Selected metrics display panel
- Remove buttons and clear all functionality

#### `VideoAnalysisLayout`
- Video player component
- Dynamic video loading

#### `FileSelectionLayout`
- Normal mode file selection
- Checklist for file selection

#### `MetricsSelectionLayout`
- Normal mode metrics selection
- Grouped metric checklists

#### `NotesLayout`
- Analysis notes text areas
- Key takeaways, observations, recommendations
- Save functionality

#### `MainLayout`
- Main application layout structure
- Combines all components

### `callbacks.py` - Callback Functions
Organized callback classes by functionality:

#### `AthleteProfileCallbacks`
- Updates athlete profile display
- Handles profile photo and information

#### `FileSelectionCallbacks`
- Manages file selection UI
- Switches between debug/normal mode

#### `MetricsSelectionCallbacks`
- Handles metrics selection and display
- Manages selected metrics panel
- Clear all and remove functionality

#### `HierarchicalDropdownCallbacks`
- 5-level dropdown cascade logic
- Updates options based on selections
- Resets lower levels when higher levels change

#### `DataStoreCallbacks`
- Manages persistent data stores
- Updates hierarchical selection store
- Handles metrics persistence

#### `VideoPlayerCallbacks`
- Dynamic video source updates
- Constructs video paths from selections

#### `PlotCallbacks`
- Generates kinematic plots
- Handles both debug and normal modes
- Creates Plotly figures

#### `NotesCallbacks`
- Saves analysis notes to files
- Handles file I/O and error reporting

## Key Features

### Modular Design Benefits
1. **Separation of Concerns**: Each module has a specific responsibility
2. **Maintainability**: Easy to locate and modify specific functionality
3. **Scalability**: Easy to add new features without affecting existing code
4. **Reusability**: Components can be reused across different parts of the app
5. **Testing**: Each module can be tested independently

### Component Organization
- **Layout Components**: Reusable UI building blocks
- **Utility Classes**: Encapsulated business logic
- **Callback Groups**: Organized by functionality
- **Configuration Management**: Centralized settings

### Data Flow
1. **Configuration** loads settings and data mappings
2. **Utils** process data and provide business logic
3. **Layout** creates UI components
4. **Callbacks** handle user interactions and updates
5. **App** coordinates everything together

## Usage

### Running the Application
```bash
# Navigate to the project directory
cd testing_os/

# Run the modular version
python app.py

# Or run the original version for comparison
python internal_sandbox.py
```

### Adding New Features

#### Adding a New Layout Component
1. Create a new class in `layout.py`
2. Add styling constants to `config.py` if needed
3. Import and use in `MainLayout`

#### Adding a New Callback
1. Create a new callback class in `callbacks.py`
2. Add the class to `register_all_callbacks()`
3. Define component IDs in `config.py` if needed

#### Adding New Configuration
1. Add constants to `config.py`
2. Update utility classes in `utils.py` if needed
3. Use throughout the application

### Development Guidelines
- **Component IDs**: Use `COMPONENT_IDS` from config for consistency
- **Colors**: Use `COLORS` constants for consistent styling
- **Error Handling**: Use try-catch blocks and `PreventUpdate`
- **Documentation**: Add docstrings to all functions and classes

## Migration from Original Code

The original `internal_sandbox.py` file has been preserved for reference. The modular version maintains all existing functionality while providing better organization:

- **No functionality lost**: All features from the original are preserved
- **Improved structure**: Code is organized by purpose
- **Better maintainability**: Easier to modify and extend
- **Enhanced readability**: Clear separation of concerns

## Future Enhancements

With this modular structure, future enhancements become much easier:

1. **New Analysis Tools**: Add to `utils.py`
2. **Additional Visualizations**: Add to `layout.py` and `callbacks.py`
3. **Database Integration**: Add new data processing classes
4. **Advanced UI Components**: Create new layout classes
5. **API Integration**: Add new utility classes for external data

The modular architecture provides a solid foundation for continued development and feature expansion.
