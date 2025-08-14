#!/usr/bin/env python3
"""
Minimal Flask server to diagnose the exact deployment issue.
"""

import logging
import sys
import os
from flask import Flask, jsonify
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

@app.route('/health')
def health():
    logger.info("🏥 Health check requested")
    return jsonify({"status": "healthy", "message": "Simple server working"})

@app.route('/test')
def test():
    logger.info("🧪 Test endpoint requested")
    return jsonify({"test": "success", "message": "Basic endpoint working"})

if __name__ == '__main__':
    logger.info("🚀 Starting MINIMAL Flask server for diagnosis...")
    
    try:
        # Very basic server configuration
        app.run(host='127.0.0.1', port=8004, debug=True)
    except Exception as e:
        logger.error(f"❌ Server failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
