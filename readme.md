# Spotify Playlist Data Extractor

## Overview

A Flask web application that extracts comprehensive track and metadata from Spotify playlists. The application provides dual extraction methods - using the official Spotify Web API as the primary method and web scraping as a fallback when API credentials are unavailable. Users can export extracted data to CSV format for further analysis.

## User Preferences

Preferred communication style: Simple, everyday language.
Export preferences: User requested both CSV and Excel export functionality for comprehensive data analysis.

## System Architecture

### Frontend Architecture
- **Technology**: Vanilla JavaScript with Bootstrap 5 for styling
- **Structure**: Single-page application with dynamic content updates
- **UI Framework**: Bootstrap 5 with custom CSS styling mimicking Spotify's design language
- **Communication**: Asynchronous fetch API calls to backend endpoints

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Architecture Pattern**: Modular design with separate classes for different concerns
- **Error Handling**: Comprehensive logging and graceful error handling throughout
- **API Design**: RESTful endpoints with JSON responses

## Key Components

### Core Modules

1. **SpotifyExtractor** (`spotify_extractor.py`)
   - Handles official Spotify Web API integration
   - Requires SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET environment variables
   - Provides comprehensive track metadata including audio features
   - Primary extraction method when API credentials are available

2. **WebScraper** (`web_scraper.py`)
   - Selenium-based web scraping fallback
   - Uses Chrome WebDriver in headless mode
   - Scrapes Spotify web interface when API is unavailable
   - Implements retry logic and error handling

3. **DataProcessor** (`data_processor.py`)
   - Standardizes and validates track data from both extraction methods
   - Handles CSV export functionality
   - Formats data consistently regardless of source
   - Provides data cleaning and normalization

4. **Flask Application** (`main.py`)
   - Main web server handling HTTP requests
   - Route definitions for web interface and API endpoints
   - Orchestrates the extraction workflow
   - Manages temporary file creation for CSV exports

### Frontend Components

1. **User Interface** (`templates/index.html`)
   - Bootstrap-based responsive design
   - Form for playlist URL input
   - Results display area
   - CSV export functionality

2. **JavaScript Logic** (`static/script.js`)
   - Form submission handling
   - API communication
   - UI state management
   - Error display and user feedback

3. **Styling** (`static/style.css`)
   - Custom CSS with Spotify-inspired design
   - Responsive layout components
   - Interactive element styling

## Data Flow

1. **User Input**: User provides Spotify playlist URL through web interface
2. **URL Validation**: Frontend validates URL format before submission
3. **Extraction Routing**: Backend attempts Spotify API extraction first
4. **Fallback Logic**: If API fails, system falls back to web scraping
5. **Data Processing**: Raw data is standardized and formatted
6. **Response**: Processed data is returned to frontend for display
7. **Export**: Users can download processed data as CSV

## External Dependencies

### Python Packages
- **Flask**: Web framework for backend API
- **spotipy**: Official Spotify Web API client library
- **selenium**: Web scraping automation
- **beautifulsoup4**: HTML parsing for scraped content
- **python-dotenv**: Environment variable management (implied)

### Frontend Dependencies
- **Bootstrap 5**: CSS framework for responsive design
- **Font Awesome**: Icon library for UI elements

### System Dependencies
- **Chrome WebDriver**: Required for Selenium web scraping
- **Chrome Browser**: Headless browser for scraping operations

### External Services
- **Spotify Web API**: Primary data source requiring client credentials
- **Spotify Web Interface**: Fallback data source accessed via scraping

## Deployment Strategy

### Environment Configuration
- Requires SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET environment variables
- Chrome/Chromium browser installation required for web scraping
- ChromeDriver must be available in system PATH

### Deployment Considerations
- Application can run without Spotify API credentials (scraping mode)
- Headless Chrome configuration for server environments
- Static file serving through Flask for development
- Production deployment would benefit from reverse proxy setup
- Rate limiting considerations for both API and scraping methods

### Scalability Notes
- Current design is single-threaded and suitable for personal use
- Web scraping method has inherent rate limitations
- API method supports higher throughput but has rate limits
- Database integration could be added for caching and analytics

## Recent Changes (July 2025)

### UI/UX Improvements
- **Enhanced Playlist Information Display**: Redesigned playlist metadata cards with icons, gradients, and improved typography
- **Advanced Export Options**: Added Excel export functionality alongside CSV export
- **Responsive Design**: Improved mobile layout for export buttons and playlist information

### Excel Export Features
- **Multi-Sheet Workbook**: Separate sheets for playlist summary, track details, and audio features
- **Professional Formatting**: Color-coded headers, alternating row colors, auto-adjusted column widths
- **Comprehensive Data**: Includes all extracted metadata with proper formatting and styling
- **Statistics Summary**: Automatic calculation of playlist statistics and insights

### Technical Updates
- **openpyxl Integration**: Added Excel processing capability with advanced formatting
- **Improved Error Handling**: Better user feedback for extraction failures
- **API Optimization**: Simplified extraction flow focusing on Spotify API reliability
- **Enhanced Styling**: Modern gradient designs and improved visual hierarchy

The application prioritizes robustness by providing dual extraction methods, ensuring functionality even when API credentials are unavailable. The modular design allows for easy extension and maintenance while providing a user-friendly interface for playlist data extraction. Recent improvements focus on enhanced data presentation and comprehensive export capabilities.