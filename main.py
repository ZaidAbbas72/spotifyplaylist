"""
Spotify Playlist Data Extractor
A Flask web application for extracting comprehensive track and metadata from Spotify playlists
"""

import os
import logging
from flask import Flask, render_template, request, jsonify, send_file
from spotify_extractor import SpotifyExtractor
from web_scraper import WebScraper
from data_processor import DataProcessor
from excel_processor import ExcelProcessor
import tempfile
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def extract_playlist_id(url):
    """Extract playlist ID from Spotify URL"""
    try:
        if 'playlist/' in url:
            playlist_id = url.split('playlist/')[-1].split('?')[0]
            return playlist_id
        else:
            raise ValueError("Invalid Spotify playlist URL")
    except Exception as e:
        logger.error(f"Error extracting playlist ID: {e}")
        return None

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/extract', methods=['POST'])
def extract_playlist():
    """Extract playlist data from Spotify URL"""
    try:
        data = request.get_json()
        playlist_url = data.get('url', '').strip()
        
        if not playlist_url:
            return jsonify({'error': 'Please provide a Spotify playlist URL'}), 400
        
        # Extract playlist ID from URL
        playlist_id = extract_playlist_id(playlist_url)
        if not playlist_id:
            return jsonify({'error': 'Invalid Spotify playlist URL format'}), 400
        
        logger.info(f"Extracting data for playlist ID: {playlist_id}")
        
        # Try Spotify API first
        spotify_extractor = SpotifyExtractor()
        
        try:
            playlist_data, tracks_data = spotify_extractor.extract_playlist_data(playlist_id)
            
            if playlist_data and tracks_data:
                logger.info("Successfully extracted data using Spotify API")
                
                # Process and format the data
                processor = DataProcessor()
                processed_data = processor.process_tracks(tracks_data, playlist_data)
                
                return jsonify({
                    'success': True,
                    'method': 'Spotify API',
                    'playlist': playlist_data,
                    'tracks': processed_data[:20],  # Top 20 tracks
                    'total_tracks': len(processed_data)
                })
            
        except Exception as api_error:
            logger.error(f"Spotify API failed: {api_error}")
            return jsonify({
                'error': f'Spotify API extraction failed: {str(api_error)}. Please ensure the playlist is public and accessible, or try a different playlist URL.'
            }), 500
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

@app.route('/export-csv', methods=['POST'])
def export_csv():
    """Export extracted data to CSV"""
    try:
        data = request.get_json()
        playlist_data = data.get('playlist', {})
        tracks_data = data.get('tracks', [])
        
        if not tracks_data:
            return jsonify({'error': 'No tracks data to export'}), 400
        
        # Create CSV file
        processor = DataProcessor()
        csv_content = processor.create_csv(playlist_data, tracks_data)
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8')
        temp_file.write(csv_content)
        temp_file.close()
        
        playlist_name = playlist_data.get('name', 'playlist').replace(' ', '_')
        filename = f"spotify_{playlist_name}_tracks.csv"
        
        return send_file(
            temp_file.name,
            as_attachment=True,
            download_name=filename,
            mimetype='text/csv'
        )
        
    except Exception as e:
        logger.error(f"Error exporting CSV: {e}")
        return jsonify({'error': f'Failed to export CSV: {str(e)}'}), 500

@app.route('/export-excel', methods=['POST'])
def export_excel():
    """Export extracted data to Excel"""
    try:
        data = request.get_json()
        playlist_data = data.get('playlist', {})
        tracks_data = data.get('tracks', [])
        
        if not tracks_data:
            return jsonify({'error': 'No tracks data to export'}), 400
        
        # Create Excel file
        excel_processor = ExcelProcessor()
        excel_content = excel_processor.create_excel(playlist_data, tracks_data)
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        temp_file.write(excel_content)
        temp_file.close()
        
        playlist_name = playlist_data.get('name', 'playlist').replace(' ', '_')
        filename = f"spotify_{playlist_name}_tracks.xlsx"
        
        return send_file(
            temp_file.name,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        logger.error(f"Error exporting Excel: {e}")
        return jsonify({'error': f'Failed to export Excel: {str(e)}'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Spotify Playlist Extractor is running'})

if __name__ == '__main__':
    logger.info("Starting Spotify Playlist Data Extractor...")
    logger.info("Web interface will be available at http://localhost:5000")
    
    # Check for environment variables
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        logger.warning("Spotify API credentials not found in environment variables.")
        logger.warning("The application will only use web scraping fallback.")
        logger.warning("Please set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET for API access.")
    else:
        logger.info("Spotify API credentials found. API method will be used primarily.")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
