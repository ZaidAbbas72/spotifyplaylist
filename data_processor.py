"""
Data Processor for Spotify Playlist Data
Handles data formatting, validation, and CSV export functionality
"""

import logging
import csv
import io
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class DataProcessor:
    def __init__(self):
        """Initialize data processor"""
        pass

    def process_tracks(self, tracks_data, playlist_data):
        """Process and standardize track data"""
        processed_tracks = []
        
        for track in tracks_data:
            try:
                processed_track = self._standardize_track(track)
                processed_tracks.append(processed_track)
            except Exception as e:
                logger.warning(f"Error processing track {track.get('name', 'Unknown')}: {e}")
                continue
        
        logger.info(f"Processed {len(processed_tracks)} tracks")
        return processed_tracks

    def _standardize_track(self, track):
        """Standardize a single track's data format"""
        return {
            'track_name': track.get('name', 'Unknown'),
            'artists': ', '.join(track.get('artists', ['Unknown Artist'])),
            'album_name': track.get('album_name', 'Unknown Album'),
            'duration': track.get('duration_formatted', '0:00'),
            'duration_ms': track.get('duration_ms', 0),
            'date_added': self._format_date(track.get('added_at', '')),
            'release_year': track.get('release_year', 'Unknown'),
            'popularity': track.get('popularity', 0),
            'explicit': track.get('explicit', False),
            'streams': track.get('streams', 'N/A'),
            'track_number': track.get('track_number', 0),
            # Audio features (if available)
            'danceability': track.get('danceability', 'N/A'),
            'energy': track.get('energy', 'N/A'),
            'valence': track.get('valence', 'N/A'),
            'tempo': track.get('tempo', 'N/A'),
            'acousticness': track.get('acousticness', 'N/A'),
            'instrumentalness': track.get('instrumentalness', 'N/A'),
            'liveness': track.get('liveness', 'N/A'),
            'speechiness': track.get('speechiness', 'N/A'),
            'loudness': track.get('loudness', 'N/A'),
            'key': track.get('key', 'N/A'),
            'mode': track.get('mode', 'N/A'),
            'time_signature': track.get('time_signature', 'N/A')
        }

    def _format_date(self, date_string):
        """Format date string to a consistent format"""
        if not date_string:
            return 'Unknown'
        
        try:
            # Try parsing ISO format (from API)
            if 'T' in date_string:
                dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
                return dt.strftime('%Y-%m-%d')
            
            # Try parsing other common formats
            for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y']:
                try:
                    dt = datetime.strptime(date_string, fmt)
                    return dt.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            
            return date_string
            
        except Exception as e:
            logger.warning(f"Error formatting date {date_string}: {e}")
            return date_string

    def create_csv(self, playlist_data, tracks_data):
        """Create CSV content from playlist and tracks data"""
        try:
            output = io.StringIO()
            
            # Write playlist metadata header
            output.write("PLAYLIST METADATA\n")
            output.write(f"Name,{playlist_data.get('name', 'Unknown Playlist')}\n")
            output.write(f"Description,\"{playlist_data.get('description', '')}\"\n")
            output.write(f"Total Saves/Followers,{playlist_data.get('followers', 0)}\n")
            output.write(f"Number of Songs,{playlist_data.get('total_tracks', len(tracks_data))}\n")
            output.write(f"Total Duration,{playlist_data.get('total_duration', 'Unknown')}\n")
            output.write(f"URL,{playlist_data.get('external_url', '')}\n")
            output.write(f"Extracted on,{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            output.write("\n")
            
            # Write tracks data
            output.write("TRACKS DATA\n")
            
            # Define CSV headers
            headers = [
                'Track Number',
                'Track Name',
                'Artist(s)',
                'Album Name',
                'Duration (mm:ss)',
                'Date Added',
                'Release Year',
                'Popularity',
                'Explicit',
                'Streams',
                'Danceability',
                'Energy',
                'Valence',
                'Tempo',
                'Acousticness',
                'Instrumentalness',
                'Liveness',
                'Speechiness',
                'Loudness',
                'Key',
                'Mode',
                'Time Signature'
            ]
            
            writer = csv.writer(output)
            writer.writerow(headers)
            
            # Write track data
            for i, track in enumerate(tracks_data, 1):
                row = [
                    i,
                    track.get('track_name', 'Unknown'),
                    track.get('artists', 'Unknown Artist'),
                    track.get('album_name', 'Unknown Album'),
                    track.get('duration', '0:00'),
                    track.get('date_added', 'Unknown'),
                    track.get('release_year', 'Unknown'),
                    track.get('popularity', 0),
                    'Yes' if track.get('explicit', False) else 'No',
                    track.get('streams', 'N/A'),
                    self._format_audio_feature(track.get('danceability')),
                    self._format_audio_feature(track.get('energy')),
                    self._format_audio_feature(track.get('valence')),
                    self._format_audio_feature(track.get('tempo')),
                    self._format_audio_feature(track.get('acousticness')),
                    self._format_audio_feature(track.get('instrumentalness')),
                    self._format_audio_feature(track.get('liveness')),
                    self._format_audio_feature(track.get('speechiness')),
                    self._format_audio_feature(track.get('loudness')),
                    self._format_audio_feature(track.get('key')),
                    self._format_audio_feature(track.get('mode')),
                    self._format_audio_feature(track.get('time_signature'))
                ]
                writer.writerow(row)
            
            csv_content = output.getvalue()
            output.close()
            
            logger.info("CSV content created successfully")
            return csv_content
            
        except Exception as e:
            logger.error(f"Error creating CSV: {e}")
            raise Exception(f"Failed to create CSV: {e}")

    def _format_audio_feature(self, value):
        """Format audio feature values for CSV"""
        if value is None or value == 'N/A':
            return 'N/A'
        
        if isinstance(value, (int, float)):
            return round(value, 3)
        
        return str(value)

    def calculate_total_duration(self, tracks_data):
        """Calculate total duration of all tracks"""
        total_ms = sum(track.get('duration_ms', 0) for track in tracks_data)
        
        total_seconds = total_ms // 1000
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"

    def validate_track_data(self, track):
        """Validate track data completeness"""
        required_fields = ['name', 'artists', 'album_name']
        
        for field in required_fields:
            if not track.get(field):
                logger.warning(f"Missing required field {field} in track data")
                return False
        
        return True

    def get_data_summary(self, playlist_data, tracks_data):
        """Get summary statistics of extracted data"""
        summary = {
            'playlist_name': playlist_data.get('name', 'Unknown'),
            'total_tracks_extracted': len(tracks_data),
            'total_duration': self.calculate_total_duration(tracks_data),
            'avg_popularity': sum(track.get('popularity', 0) for track in tracks_data) / len(tracks_data) if tracks_data else 0,
            'explicit_tracks': sum(1 for track in tracks_data if track.get('explicit', False)),
            'tracks_with_release_year': sum(1 for track in tracks_data if track.get('release_year')),
            'tracks_with_audio_features': sum(1 for track in tracks_data if track.get('danceability') is not None)
        }
        
        return summary
