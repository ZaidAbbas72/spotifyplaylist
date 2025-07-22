"""
Spotify API Data Extractor
Handles playlist and track data extraction using the official Spotify Web API
"""

import os
import logging
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import time
from datetime import datetime

logger = logging.getLogger(__name__)

class SpotifyExtractor:
    def __init__(self):
        """Initialize Spotify API client"""
        self.client_id = os.getenv('SPOTIFY_CLIENT_ID', '')
        self.client_secret = os.getenv('SPOTIFY_CLIENT_SECRET', '')
        self.sp = None
        
        if self.client_id and self.client_secret:
            try:
                client_credentials_manager = SpotifyClientCredentials(
                    client_id=self.client_id,
                    client_secret=self.client_secret
                )
                self.sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
                logger.info("Spotify API client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Spotify API client: {e}")
                raise Exception(f"Spotify API authentication failed: {e}")
        else:
            raise Exception("Spotify API credentials not provided")

    def extract_playlist_data(self, playlist_id):
        """Extract playlist metadata and tracks data"""
        if not self.sp:
            raise Exception("Spotify API client not initialized")
        
        try:
            # Get playlist metadata
            playlist_info = self.sp.playlist(playlist_id)
            
            playlist_data = {
                'id': playlist_info['id'],
                'name': playlist_info['name'],
                'description': playlist_info.get('description', ''),
                'followers': playlist_info.get('followers', {}).get('total', 0),
                'total_tracks': playlist_info['tracks']['total'],
                'external_url': playlist_info['external_urls']['spotify']
            }
            
            logger.info(f"Extracted playlist metadata: {playlist_data['name']}")
            
            # Get all tracks from the playlist
            tracks_data = []
            results = self.sp.playlist_tracks(playlist_id, limit=50)
            
            while results:
                for item in results['items']:
                    if item['track'] and item['track']['id']:  # Skip null tracks
                        track_info = self._extract_track_info(item)
                        if track_info:
                            tracks_data.append(track_info)
                
                # Check if there are more tracks
                if results['next']:
                    results = self.sp.next(results)
                    time.sleep(0.1)  # Rate limiting
                else:
                    break
            
            logger.info(f"Extracted {len(tracks_data)} tracks from playlist")
            
            # Calculate total duration
            total_duration_ms = sum(track.get('duration_ms', 0) for track in tracks_data)
            playlist_data['total_duration'] = self._format_duration(total_duration_ms)
            
            return playlist_data, tracks_data
            
        except Exception as e:
            logger.error(f"Error extracting playlist data: {e}")
            raise Exception(f"Failed to extract playlist data: {e}")

    def _extract_track_info(self, item):
        """Extract detailed information for a single track"""
        try:
            track = item['track']
            
            if not track or not track.get('id'):
                return None
            
            # Basic track info
            track_info = {
                'id': track['id'],
                'name': track['name'],
                'artists': [artist['name'] for artist in track['artists']],
                'artist_ids': [artist['id'] for artist in track['artists']],
                'album_name': track['album']['name'],
                'album_id': track['album']['id'],
                'duration_ms': track['duration_ms'],
                'duration_formatted': self._format_duration(track['duration_ms']),
                'popularity': track.get('popularity', 0),
                'explicit': track.get('explicit', False),
                'preview_url': track.get('preview_url'),
                'external_url': track['external_urls']['spotify'],
                'added_at': item.get('added_at', ''),
                'release_date': track['album'].get('release_date', ''),
                'release_year': self._extract_year(track['album'].get('release_date', '')),
                'track_number': track.get('track_number', 0),
                'disc_number': track.get('disc_number', 1)
            }
            
            # Try to get audio features for additional metadata
            try:
                audio_features = self.sp.audio_features([track['id']])[0]
                if audio_features:
                    track_info.update({
                        'danceability': audio_features.get('danceability'),
                        'energy': audio_features.get('energy'),
                        'key': audio_features.get('key'),
                        'loudness': audio_features.get('loudness'),
                        'mode': audio_features.get('mode'),
                        'speechiness': audio_features.get('speechiness'),
                        'acousticness': audio_features.get('acousticness'),
                        'instrumentalness': audio_features.get('instrumentalness'),
                        'liveness': audio_features.get('liveness'),
                        'valence': audio_features.get('valence'),
                        'tempo': audio_features.get('tempo'),
                        'time_signature': audio_features.get('time_signature')
                    })
                time.sleep(0.05)  # Rate limiting for audio features
            except Exception as e:
                logger.warning(f"Could not get audio features for track {track['name']}: {e}")
            
            return track_info
            
        except Exception as e:
            logger.error(f"Error extracting track info: {e}")
            return None

    def _format_duration(self, duration_ms):
        """Convert duration from milliseconds to mm:ss format"""
        if not duration_ms:
            return "0:00"
        
        seconds = duration_ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}:{seconds:02d}"

    def _extract_year(self, release_date):
        """Extract year from release date"""
        if not release_date:
            return None
        
        try:
            if len(release_date) >= 4:
                return int(release_date[:4])
        except (ValueError, TypeError):
            pass
        
        return None

    def get_track_popularity(self, track_id):
        """Get additional track popularity/streams data"""
        try:
            track = self.sp.track(track_id)
            return track.get('popularity', 0)
        except Exception as e:
            logger.warning(f"Could not get popularity for track {track_id}: {e}")
            return 0
