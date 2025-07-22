/**
 * Spotify Playlist Data Extractor - Frontend JavaScript
 * Handles form submission, API communication, and UI updates
 */

let extractedData = null;

document.addEventListener('DOMContentLoaded', function() {
    // Initialize event listeners
    initializeEventListeners();
    
    // Check application health
    checkApplicationHealth();
});

function initializeEventListeners() {
    // Form submission
    const extractForm = document.getElementById('extractForm');
    extractForm.addEventListener('submit', handleFormSubmission);
    
    // CSV export button
    const exportCsvBtn = document.getElementById('exportCsvBtn');
    exportCsvBtn.addEventListener('click', handleCsvExport);
}

function checkApplicationHealth() {
    fetch('/health')
        .then(response => response.json())
        .then(data => {
            console.log('Application health check:', data);
        })
        .catch(error => {
            console.warn('Health check failed:', error);
        });
}

async function handleFormSubmission(event) {
    event.preventDefault();
    
    const playlistUrl = document.getElementById('playlistUrl').value.trim();
    
    if (!playlistUrl) {
        showError('Please enter a Spotify playlist URL');
        return;
    }
    
    if (!isValidSpotifyUrl(playlistUrl)) {
        showError('Please enter a valid Spotify playlist URL');
        return;
    }
    
    // Show loading state
    showLoading();
    hideError();
    hideResults();
    
    try {
        const response = await fetch('/extract', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: playlistUrl })
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            extractedData = data;
            displayResults(data);
            showSuccess(`Successfully extracted data using ${data.method}`);
        } else {
            throw new Error(data.error || 'Failed to extract playlist data');
        }
        
    } catch (error) {
        console.error('Extraction error:', error);
        showError(error.message || 'An unexpected error occurred');
    } finally {
        hideLoading();
    }
}

function isValidSpotifyUrl(url) {
    const spotifyUrlPattern = /^https:\/\/open\.spotify\.com\/playlist\/[a-zA-Z0-9]+/;
    return spotifyUrlPattern.test(url);
}

function showLoading() {
    const loadingSection = document.getElementById('loadingSection');
    loadingSection.style.display = 'block';
    loadingSection.classList.add('fade-in-up');
    
    // Disable form
    const extractBtn = document.getElementById('extractBtn');
    extractBtn.disabled = true;
    extractBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Extracting...';
}

function hideLoading() {
    const loadingSection = document.getElementById('loadingSection');
    loadingSection.style.display = 'none';
    
    // Re-enable form
    const extractBtn = document.getElementById('extractBtn');
    extractBtn.disabled = false;
    extractBtn.innerHTML = '<i class="fas fa-download me-2"></i>Extract Playlist Data';
}

function showError(message) {
    const errorSection = document.getElementById('errorSection');
    const errorMessage = document.getElementById('errorMessage');
    
    errorMessage.textContent = message;
    errorSection.style.display = 'block';
    errorSection.classList.add('fade-in-up');
    
    // Scroll to error
    errorSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function hideError() {
    const errorSection = document.getElementById('errorSection');
    errorSection.style.display = 'none';
}

function showSuccess(message) {
    // Create a temporary success alert
    const successAlert = document.createElement('div');
    successAlert.className = 'alert alert-success fade-in-up mt-4';
    successAlert.innerHTML = `
        <h6 class="alert-heading">
            <i class="fas fa-check-circle me-2"></i>
            Extraction Successful
        </h6>
        <p class="mb-0">${message}</p>
    `;
    
    // Insert before results section
    const resultsSection = document.getElementById('resultsSection');
    resultsSection.parentNode.insertBefore(successAlert, resultsSection);
    
    // Remove after 5 seconds
    setTimeout(() => {
        successAlert.remove();
    }, 5000);
}

function displayResults(data) {
    displayPlaylistInfo(data.playlist);
    displayTracksTable(data.tracks);
    displayExtractionMethod(data.method);
    
    // Show audio features if available
    if (data.tracks.some(track => track.danceability !== 'N/A')) {
        displayAudioFeatures(data.tracks);
    }
    
    // Show results section
    const resultsSection = document.getElementById('resultsSection');
    resultsSection.style.display = 'block';
    resultsSection.classList.add('fade-in-up');
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function displayPlaylistInfo(playlist) {
    const playlistInfo = document.getElementById('playlistInfo');
    
    const infoItems = [
        { label: 'Playlist Name', value: playlist.name || 'Unknown' },
        { label: 'Description', value: playlist.description || 'No description available' },
        { label: 'Total Saves/Followers', value: formatNumber(playlist.followers || 0) },
        { label: 'Number of Songs', value: formatNumber(playlist.total_tracks || 0) },
        { label: 'Total Duration', value: playlist.total_duration || 'Unknown' },
        { label: 'Spotify URL', value: playlist.external_url ? `<a href="${playlist.external_url}" target="_blank" class="text-success">Open in Spotify</a>` : 'N/A' }
    ];
    
    playlistInfo.innerHTML = infoItems.map(item => `
        <div class="col-md-6 col-lg-4 mb-3">
            <div class="playlist-info-item">
                <div class="playlist-info-label">${item.label}</div>
                <div class="playlist-info-value">${item.value}</div>
            </div>
        </div>
    `).join('');
}

function displayTracksTable(tracks) {
    const tbody = document.querySelector('#tracksTable tbody');
    
    tbody.innerHTML = tracks.map((track, index) => `
        <tr>
            <td><strong>${index + 1}</strong></td>
            <td>
                <div class="fw-bold">${escapeHtml(track.track_name)}</div>
                ${track.explicit ? '<span class="track-explicit">🅴</span>' : ''}
            </td>
            <td>${escapeHtml(track.artists)}</td>
            <td>${escapeHtml(track.album_name)}</td>
            <td><code>${track.duration}</code></td>
            <td>${track.release_year || 'Unknown'}</td>
            <td>
                ${track.popularity ? `<span class="track-popularity">${track.popularity}</span>` : 'N/A'}
            </td>
            <td>
                ${track.explicit ? 
                    '<i class="fas fa-exclamation-triangle text-warning" title="Explicit Content"></i>' : 
                    '<i class="fas fa-check text-success" title="Clean"></i>'
                }
            </td>
        </tr>
    `).join('');
}

function displayExtractionMethod(method) {
    const methodBadge = document.getElementById('extractionMethodBadge');
    methodBadge.textContent = `Extracted via ${method}`;
    methodBadge.className = method === 'Spotify API' ? 'badge bg-success ms-2' : 'badge bg-warning ms-2';
}

function displayAudioFeatures(tracks) {
    const audioFeaturesCard = document.getElementById('audioFeaturesCard');
    const audioFeaturesContent = document.getElementById('audioFeaturesContent');
    
    // Calculate average audio features
    const features = ['danceability', 'energy', 'valence', 'acousticness', 'tempo'];
    const averages = {};
    
    features.forEach(feature => {
        const values = tracks
            .map(track => track[feature])
            .filter(value => value !== 'N/A' && value !== null && !isNaN(value));
        
        if (values.length > 0) {
            averages[feature] = values.reduce((sum, val) => sum + parseFloat(val), 0) / values.length;
        }
    });
    
    if (Object.keys(averages).length > 0) {
        audioFeaturesContent.innerHTML = Object.entries(averages).map(([feature, value]) => `
            <div class="col-md-2 col-sm-4 col-6">
                <div class="audio-feature-item">
                    <span class="audio-feature-value">${value.toFixed(2)}</span>
                    <span class="audio-feature-label">${feature}</span>
                </div>
            </div>
        `).join('');
        
        audioFeaturesCard.style.display = 'block';
    }
}

async function handleCsvExport() {
    if (!extractedData) {
        showError('No data available to export');
        return;
    }
    
    const exportBtn = document.getElementById('exportCsvBtn');
    const originalText = exportBtn.innerHTML;
    
    try {
        // Show loading state
        exportBtn.disabled = true;
        exportBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Exporting...';
        
        const response = await fetch('/export-csv', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                playlist: extractedData.playlist,
                tracks: extractedData.tracks
            })
        });
        
        if (response.ok) {
            // Download the CSV file
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `spotify_${extractedData.playlist.name.replace(/[^a-zA-Z0-9]/g, '_')}_tracks.csv`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            showSuccess('CSV file downloaded successfully!');
        } else {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to export CSV');
        }
        
    } catch (error) {
        console.error('Export error:', error);
        showError(error.message || 'Failed to export CSV file');
    } finally {
        // Restore button state
        exportBtn.disabled = false;
        exportBtn.innerHTML = originalText;
    }
}

function hideResults() {
    const resultsSection = document.getElementById('resultsSection');
    resultsSection.style.display = 'none';
}

function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Error handling for uncaught promise rejections
window.addEventListener('unhandledrejection', function(event) {
    console.error('Uncaught promise rejection:', event.reason);
    showError('An unexpected error occurred. Please try again.');
});
