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
    import os
    
    # Check if running in production
    port = int(os.environ.get("PORT", 8050))
    debug = not bool(os.environ.get("RENDER") or 
                    os.environ.get("HEROKU") or 
                    os.environ.get("VERCEL"))
    
    if debug:
        # For development
        app.run(debug=True, port=port)
    else:
        # For production
        app.run(debug=False, host="0.0.0.0", port=port)
