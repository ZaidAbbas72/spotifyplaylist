"""
Web Scraper for Spotify Playlist Data
Fallback method for extracting playlist and track data when API is unavailable
"""

import logging
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class WebScraper:
    def __init__(self):
        """Initialize web scraper with Chrome options"""
        self.driver = None
        self.setup_driver()

    def setup_driver(self):
        """Setup Chrome WebDriver with appropriate options"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            logger.info("Chrome WebDriver initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            raise Exception(f"WebDriver initialization failed: {e}")

    def scrape_playlist_data(self, playlist_url):
        """Scrape playlist data from Spotify web interface"""
        if not self.driver:
            raise Exception("WebDriver not initialized")
        
        try:
            logger.info(f"Navigating to playlist URL: {playlist_url}")
            self.driver.get(playlist_url)
            
            # Wait for page to load
            time.sleep(5)
            
            # Accept cookies if present
            try:
                cookie_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'Agree')]"))
                )
                cookie_button.click()
                time.sleep(2)
            except TimeoutException:
                logger.info("No cookie banner found or already accepted")
            
            # Extract playlist metadata
            playlist_data = self._extract_playlist_metadata()
            
            # Extract track data
            tracks_data = self._extract_tracks_data()
            
            logger.info(f"Successfully scraped playlist: {playlist_data.get('name', 'Unknown')}")
            logger.info(f"Extracted {len(tracks_data)} tracks")
            
            return playlist_data, tracks_data
            
        except Exception as e:
            logger.error(f"Error scraping playlist data: {e}")
            raise Exception(f"Web scraping failed: {e}")
        
        finally:
            if self.driver:
                self.driver.quit()

    def _extract_playlist_metadata(self):
        """Extract playlist metadata from the page"""
        try:
            playlist_data = {}
            
            # Wait for content to load
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "h1"))
            )
            
            # Get page source and parse with BeautifulSoup
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Extract playlist name
            try:
                name_element = soup.find('h1', attrs={'data-testid': 'entityTitle'})
                if not name_element:
                    name_element = soup.find('h1')
                playlist_data['name'] = name_element.get_text(strip=True) if name_element else 'Unknown Playlist'
            except:
                playlist_data['name'] = 'Unknown Playlist'
            
            # Extract description
            try:
                desc_element = soup.find('span', attrs={'data-testid': 'playlist-description'})
                playlist_data['description'] = desc_element.get_text(strip=True) if desc_element else ''
            except:
                playlist_data['description'] = ''
            
            # Extract followers/saves count
            try:
                followers_element = soup.find(text=re.compile(r'\d+.*saves?', re.IGNORECASE))
                if followers_element:
                    followers_text = followers_element.strip()
                    followers_match = re.search(r'([\d,]+)', followers_text)
                    if followers_match:
                        playlist_data['followers'] = int(followers_match.group(1).replace(',', ''))
                    else:
                        playlist_data['followers'] = 0
                else:
                    playlist_data['followers'] = 0
            except:
                playlist_data['followers'] = 0
            
            # Extract total tracks count
            try:
                tracks_element = soup.find(text=re.compile(r'\d+.*songs?', re.IGNORECASE))
                if tracks_element:
                    tracks_text = tracks_element.strip()
                    tracks_match = re.search(r'([\d,]+)', tracks_text)
                    if tracks_match:
                        playlist_data['total_tracks'] = int(tracks_match.group(1).replace(',', ''))
                    else:
                        playlist_data['total_tracks'] = 0
                else:
                    playlist_data['total_tracks'] = 0
            except:
                playlist_data['total_tracks'] = 0
            
            playlist_data['external_url'] = self.driver.current_url
            
            return playlist_data
            
        except Exception as e:
            logger.error(f"Error extracting playlist metadata: {e}")
            return {'name': 'Unknown Playlist', 'description': '', 'followers': 0, 'total_tracks': 0}

    def _extract_tracks_data(self):
        """Extract track data from the playlist"""
        try:
            tracks_data = []
            
            # Scroll to load more tracks
            self._scroll_to_load_tracks()
            
            # Get updated page source
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Find track rows
            track_rows = soup.find_all('div', attrs={'data-testid': 'tracklist-row'})
            
            if not track_rows:
                # Try alternative selector
                track_rows = soup.find_all('div', class_=re.compile(r'.*tracklist.*row.*', re.IGNORECASE))
            
            logger.info(f"Found {len(track_rows)} track rows")
            
            for i, row in enumerate(track_rows[:20]):  # Limit to top 20 tracks
                try:
                    track_info = self._extract_single_track(row, i + 1)
                    if track_info:
                        tracks_data.append(track_info)
                except Exception as e:
                    logger.warning(f"Error extracting track {i + 1}: {e}")
                    continue
            
            return tracks_data
            
        except Exception as e:
            logger.error(f"Error extracting tracks data: {e}")
            return []

    def _extract_single_track(self, track_row, track_number):
        """Extract data for a single track"""
        try:
            track_info = {'track_number': track_number}
            
            # Extract track name
            try:
                name_element = track_row.find('div', attrs={'data-testid': 'tracklist-row-title'})
                if not name_element:
                    name_element = track_row.find('a', href=re.compile(r'/track/'))
                track_info['name'] = name_element.get_text(strip=True) if name_element else f'Track {track_number}'
            except:
                track_info['name'] = f'Track {track_number}'
            
            # Extract artists
            try:
                artist_elements = track_row.find_all('a', href=re.compile(r'/artist/'))
                if artist_elements:
                    track_info['artists'] = [elem.get_text(strip=True) for elem in artist_elements]
                else:
                    track_info['artists'] = ['Unknown Artist']
            except:
                track_info['artists'] = ['Unknown Artist']
            
            # Extract album name
            try:
                album_element = track_row.find('a', href=re.compile(r'/album/'))
                track_info['album_name'] = album_element.get_text(strip=True) if album_element else 'Unknown Album'
            except:
                track_info['album_name'] = 'Unknown Album'
            
            # Extract duration
            try:
                duration_element = track_row.find(text=re.compile(r'\d+:\d+'))
                if duration_element:
                    duration_text = duration_element.strip()
                    track_info['duration_formatted'] = duration_text
                    track_info['duration_ms'] = self._duration_to_ms(duration_text)
                else:
                    track_info['duration_formatted'] = '0:00'
                    track_info['duration_ms'] = 0
            except:
                track_info['duration_formatted'] = '0:00'
                track_info['duration_ms'] = 0
            
            # Extract date added (if available)
            try:
                date_elements = track_row.find_all(text=re.compile(r'\d{1,2}/\d{1,2}/\d{4}|\d{4}-\d{2}-\d{2}'))
                if date_elements:
                    track_info['added_at'] = date_elements[0].strip()
                else:
                    track_info['added_at'] = ''
            except:
                track_info['added_at'] = ''
            
            # Set default values for missing data
            track_info.update({
                'release_year': None,
                'popularity': 0,
                'explicit': False,
                'streams': None  # Not available through scraping
            })
            
            return track_info
            
        except Exception as e:
            logger.error(f"Error extracting single track: {e}")
            return None

    def _scroll_to_load_tracks(self):
        """Scroll down to load more tracks"""
        try:
            # Scroll down multiple times to load tracks
            for i in range(5):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            
            # Scroll back to top
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            
        except Exception as e:
            logger.warning(f"Error during scrolling: {e}")

    def _duration_to_ms(self, duration_str):
        """Convert duration string (mm:ss) to milliseconds"""
        try:
            if ':' in duration_str:
                parts = duration_str.split(':')
                minutes = int(parts[0])
                seconds = int(parts[1])
                return (minutes * 60 + seconds) * 1000
            return 0
        except:
            return 0

    def __del__(self):
        """Cleanup WebDriver on object destruction"""
        if hasattr(self, 'driver') and self.driver:
            try:
                self.driver.quit()
            except:
                pass
