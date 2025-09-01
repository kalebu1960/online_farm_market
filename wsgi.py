"""
WSGI config for Online Farm Market.

This module contains the WSGI application used by the production server.
"""

from app import app

if __name__ == "__main__":
    # This block will only run if the script is executed directly
    # (not when imported as a module).
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
