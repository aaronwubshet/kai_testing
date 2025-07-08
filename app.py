# -*- coding: utf-8 -*-
"""
Main application file for the Kinematic Dashboard
Modular Dash application entry point
"""

import dash
from layout import MainLayout
from callbacks import register_all_callbacks

# Initialize Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Set layout
app.layout = MainLayout.create()

# Register all callbacks
register_all_callbacks(app)

if __name__ == "__main__":
    # For development
    # app.run(debug=True)
    
    # For production (uncomment when deploying)
    import os
    port = int(os.environ.get("PORT", 8050))
    app.run(debug=True, host="0.0.0.0", port=port)
