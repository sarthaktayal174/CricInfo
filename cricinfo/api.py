from flask import Flask, jsonify
from main import CricketScraperApp

app = Flask(__name__)
cricket_app = CricketScraperApp()

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get the current status of the cricket scraper"""
    status = cricket_app.get_status()
    return jsonify({
        'status': 'success',
        'data': status,
        'timestamp': status.get('timestamp')
    })

@app.route('/api/matches', methods=['GET'])
def get_matches():
    """Get the list of matches"""
    matches = cricket_app.data_store.get_match_list()
    return jsonify({
        'status': 'success',
        'data': {
            'matches': matches,
            'count': len(matches)
        }
    })

@app.route('/api/matches/<match_id>', methods=['GET'])
def get_match_data(match_id):
    """Get data for a specific match"""
    match_data = cricket_app.data_store.get_match_data(match_id)
    return jsonify({
        'status': 'success',
        'data': match_data
    })

if __name__ == '__main__':
    # Start the cricket scraper in a separate thread
    import threading
    scraper_thread = threading.Thread(target=cricket_app.start)
    scraper_thread.daemon = True
    scraper_thread.start()
    
    # Start the API server
    app.run(host='0.0.0.0', port=5000)