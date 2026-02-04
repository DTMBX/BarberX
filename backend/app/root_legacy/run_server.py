"""Simple runner to start Flask server"""

import os
import sys

# Change to the Evident directory
os.chdir(r"c:\web-dev\github-repos\Evident.info")
sys.path.insert(0, r"c:\web-dev\github-repos\Evident.info")

from .app import app

if __name__ == "__main__":
    print("Starting Flask server on http://127.0.0.1:5001")
    app.run(host="127.0.0.1", port=5001, debug=False, use_reloader=False, threaded=True)


