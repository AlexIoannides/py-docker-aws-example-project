"""
api.py
~~~~~~

This module defines the simple API for our example project and will
also start the service if executed.
"""

from flask import Flask, jsonify, make_response, request

app = Flask(__name__)


@app.route('/microservice', methods=['GET'])
def service_health_check():
    """Service health-check endpoint.

    Returns a simple message string to confirm that the service is
    operational.
    
    :return: A message.
    :rtype: str
    """
        
    message = 'The microservice is operational.'
    return make_response(jsonify({'health_check': message}))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)