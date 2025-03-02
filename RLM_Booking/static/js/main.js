let map;
let userMarker;

// Initialize the map
function initializeMap() {
    if (!map) {  // Only initialize the map if it hasn't been initialized
        console.log('Initializing map...');
        map = L.map('map').setView([51.505, -0.09], 13);  // Default view

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);

        console.log('Map initialized.');
    } else {
        console.log('Map already initialized.');  // Prevent reinitializing
    }
}

// Update the map with events
function updateMap(events) {
    if (!map) {
        console.error('Map is not initialized.');
        return;
    }

    // Clear existing markers
    map.eachLayer(layer => {
        if (layer instanceof L.Marker) {
            map.removeLayer(layer);
        }
    });

    const markerPromises = [];
    const bounds = L.latLngBounds();  // Create a bounds object

    events.forEach(event => {
        const venueName = event._embedded.venues[0].name;
        markerPromises.push(
            getLatLon(venueName)
                .then(({ lat, lon }) => {
                    if (lat && lon) {
                        const marker = L.marker([lat, lon])
                            .addTo(map)
                            .bindPopup(`<b>${event.name}</b><br>${venueName}`);
                        
                        bounds.extend(marker.getLatLng());  // Extend bounds to include this marker
                    } else {
                        console.warn(`Skipping event due to missing location: ${event.name}`);
                    }
                })
                .catch(error => {
                    console.error(`Error fetching location for ${venueName}:`, error);
                })
        );
    });

    Promise.allSettled(markerPromises).then(() => {
        if (bounds.isValid()) {
            map.fitBounds(bounds);  // Adjust the map view to fit the bounds
        } else {
            console.warn('No valid coordinates found to fit bounds.');
        }
        console.log('Map updated with event locations.');
    });
}

async function getLatLon(venueName) {
    try {
        const apiUrl = `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(venueName)}&format=json`;
        console.log(`Fetching coordinates from: ${apiUrl}`);

        const response = await fetch(apiUrl);

        // Check if the request was successful
        if (!response.ok) {
            console.error(`HTTP Error: ${response.status} ${response.statusText}`);
            return { lat: null, lon: null };
        }

        const data = await response.json();

        console.log('Geocoding response:', data);

        if (data.length > 0) {
            const { lat, lon } = data[0];
            return { lat: parseFloat(lat), lon: parseFloat(lon) };
        } else {
            console.warn(`No coordinates found for ${venueName}`);
            return { lat: null, lon: null };
        }
    } catch (error) {
        console.error(`Error fetching coordinates: ${error.message}`);
        return { lat: null, lon: null };
    }
}


function updateUserLocation(lat, lon) {
    console.log('Updating map to user location:', lat, lon);
    if (userMarker) {
        map.removeLayer(userMarker);  // Remove previous marker if exists
    }

    map.setView([lat, lon], 13);  // Center and zoom in on the user location
    userMarker = L.marker([lat, lon]).addTo(map)
        .bindPopup('You are here')
        .openPopup();
}

document.addEventListener('DOMContentLoaded', function() {

    const scrollToMapButton = document.getElementById('scroll-to-map');
    scrollToMapButton.classList.add('d-none');
    // Handle artist search form submission
    document.getElementById('artist-search-form').addEventListener('submit', function(e) {
        e.preventDefault();

        const artistName = document.getElementById('artist-name').value;
        const country = document.getElementById('country').vadlue || 'US';
        const city = document.getElementById('city').value || '';

        console.log('Search form submitted');
        console.log('Artist Name:', artistName);
        console.log('Country:', country);
        console.log('City:', city);

        document.getElementById('results').innerHTML = '';
        initializeMap();

        // Fetch artist data from the backend
        fetch(`/artist_recommendation/search-artist?name=${encodeURIComponent(artistName)}`)
            .then(response => response.json())
            .then(data => {
                console.log('Artist data received:', data);

                let artists = [];
                // Handle the case where data is an object with an "artists" property
                if (data.artists && data.artists.items) {
                    artists = data.artists.items.slice(0, 5);
                } 
                // Handle the case where data is a direct array of artist objects
                else if (Array.isArray(data)) {
                    artists = data.slice(0, 5);
                } 
                // Handle unexpected formats
                else {
                    console.error("Unexpected data format:", data);
                }

                if (artists.length > 0) {
                    console.log(artists.length + " search results.");
                    // Proceed with using artists
                } else {
                    console.log("No artists found or data is not in the expected format.");
                }

                // Clear previous results and render each artist as a card
                let artistHtml = '';
                artists.forEach(artist => {
                    artistHtml += `
                        <div class="col-md-6">
                            <div class="card mb-3" style="background-color: #1a1a1a; color: #ffffff; border: none;">
                                <div class="row g-0">
                                    <div class="col-md-4">
                                        <img src="${artist.images[0] ? artist.images[0].url : 'https://via.placeholder.com/150'}" 
                                            class="img-fluid rounded-start" 
                                            alt="${artist.name}" 
                                            style="border-radius: 10px 0 0 10px;">
                                    </div>
                                    <div class="col-md-8">
                                        <div class="card-body">
                                            <h5 class="card-title" style="color: #ff0000;">${artist.name}</h5>
                                            <p class="card-text">Followers: ${artist.followers.total.toLocaleString()}</p>
                                            <p class="card-text"><small style="color: #b3b3b3;">Popularity: ${artist.popularity}</small></p>
                                            <a href="${artist.external_urls.spotify}" target="_blank" class="btn btn-danger">View on Spotify</a>
                                            <button class="btn btn-primary view-artist-details" 
                                                    data-artist='${JSON.stringify({
                                                        name: artist.name,
                                                        followers: artist.followers.total,
                                                        popularity: artist.popularity,
                                                        image: artist.images[0] ? artist.images[0].url : 'https://via.placeholder.com/150',
                                                        spotify: artist.external_urls.spotify,
                                                        genres: artist.genres || []  // Include genres
                                                    })}'>
                                                View Details
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                });

                document.getElementById('results').innerHTML = artistHtml;

                // Fetch event data for the first artist in the list (if needed)
                const firstArtistName = artists[0].name;
                return fetch(`/artist_recommendation/get-events?name=${encodeURIComponent(firstArtistName)}&country=${encodeURIComponent(country)}&city=${encodeURIComponent(city)}`);
            })
            .then(response => response.json())
            .then(eventData => {
                console.log('Event data received:', eventData);
                let eventHtml = '<h2 style="color: #ff0000;">Upcoming Events:</h2>';

                if (eventData.local_event_count > 0 && Array.isArray(eventData.local_events)) {
                    eventHtml += `<h3 style="color: #ff0000;">Local Events (${eventData.local_event_count}):</h3>`;
                    eventData.local_events.forEach(event => {
                        eventHtml += `
                            <div class="card mb-3" style="background-color: #1a1a1a; color: #ffffff; border: none;">
                                <div class="card-body">
                                    <h5 class="card-title" style="color: #ff0000;">${event.name}</h5>
                                    <p class="card-text">Date: ${event.dates.start.localDate}</p>
                                    <p class="card-text">Location: ${event._embedded.venues[0].name}, ${event._embedded.venues[0].city.name}</p>
                                    <button class="btn btn-primary add-to-calendar" 
                                            data-event='${JSON.stringify({
                                                name: event.name,
                                                date: event.dates.start.localDate,
                                                location: `${event._embedded.venues[0].name}, ${event._embedded.venues[0].city.name}`,
                                            })}'>
                                        Add to Calendar
                                    </button>
                                </div>
                            </div>
                        `;
                    });
                } else {
                    eventHtml += '<p style="color: #b3b3b3;">No local events found.</p>';
                }

                if (eventData.global_event_count > 0 && Array.isArray(eventData.global_events)) {
                    eventHtml += `<h3 style="color: #ff0000;">Global Events (${eventData.global_event_count}):</h3>`;
                    eventData.global_events.forEach(event => {
                        eventHtml += `
                            <div class="card mb-3" style="background-color: #1a1a1a; color: #ffffff; border: none;">
                                <div class="card-body">
                                    <h5 class="card-title" style="color: #ff0000;">${event.name}</h5>
                                    <p class="card-text">Date: ${event.dates.start.localDate}</p>
                                    <p class="card-text">Location: ${event._embedded.venues[0].name}, ${event._embedded.venues[0].city.name}</p>
                                    <p class="card-text"><strong>Predicted Ticket Sales: ${event.predicted_sales}</strong></p>
                                    <p class="card-text"><strong>Suggested Ticket Price: $${event.suggested_price}</strong></p>
                                    <a href="${event.url}" target="_blank" class="btn" style="background-color: #ff0000; color: #ffffff;">Get Tickets</a>
                                    <button class="btn btn-primary add-to-calendar" 
                                            data-event='${JSON.stringify({
                                                name: event.name,
                                                date: event.dates.start.localDate,
                                                location: `${event._embedded.venues[0].name}, ${event._embedded.venues[0].city.name}`,
                                            })}'>
                                        Add to Calendar
                                    </button>
                                </div>
                            </div>
                        `;
                    });
                } else {
                    eventHtml += '<p style="color: #b3b3b3;">No global events found.</p>';
                }

                scrollToMapButton.classList.remove('d-none');

                document.getElementById('results').innerHTML += eventHtml;
                updateMap(eventData.local_events.concat(eventData.global_events)); //UNCOMMENT FOR MAP FUNCTIONALITY
            })
            .catch(error => {
                console.error('Error:', error);
                document.getElementById('results').innerHTML = `<div class="alert alert-danger" role="alert">An error occurred. Please try again later.</div>`;
            });
    });

    // Handle location detection
    document.getElementById('detect-location').addEventListener('click', function() {
        console.log('Detect location button clicked.');
        if (navigator.geolocation) {
            console.log('Geolocation is supported.');
            navigator.geolocation.getCurrentPosition(position => {
                console.log('Geolocation position received:', position);
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;

                // Use reverse geocoding to get city and country from lat/lon
                fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}`)
                    .then(response => response.json())
                    .then(data => {
                        console.log('Geocoding data received:', data);
                        const city = data.address.city || '';
                        const country = data.address.country_code.toUpperCase() || 'US';

                        document.getElementById('city').value = city;
                        document.getElementById('country').value = country;

                        updateUserLocation(lat, lon); //Update map to user location
                    });
            }, error => {
                console.error('Geolocation error:', error);
                alert('Unable to retrieve your location. Please check your permissions and try again.');
            });
        } else {
            console.log('Geolocation is not supported.');
            alert('Geolocation is not supported by this browser.');
        }
    });

    // Initialize map when DOM elements load
    initializeMap();
});

document.addEventListener('DOMContentLoaded', function() {
    // Scroll to map when the button is clicked
    document.getElementById('scroll-to-map').addEventListener('click', function() {
        document.getElementById('map').scrollIntoView({ behavior: 'smooth' });
    });
});

document.addEventListener('DOMContentLoaded', function() {
    // Scroll to top when the "Scroll to Top" button is clicked
    document.getElementById('scroll-to-top').addEventListener('click', function() {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
});

// Add Event Handling:
const events = []; // Global state to store events

document.addEventListener('click', function (e) {
    if (e.target.classList.contains('add-to-calendar')) {
        const eventData = JSON.parse(e.target.getAttribute('data-event'));

        // Populate the modal form with event data
        document.getElementById('event-name').value = eventData.name;
        document.getElementById('event-location').value = eventData.location;
        document.getElementById('event-date').value = eventData.date;

        // Show the modal
        new bootstrap.Modal(document.getElementById('addToCalendarModal')).show();
    }
});

document.getElementById('add-event-form').addEventListener('submit', function (e) {
    e.preventDefault();

    const newEvent = {
        name: this.name.value,
        location: this.location.value,
        date: this.date.value,
    };

    // Send the event to the backend
    fetch('/event_management/api/save-event/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(newEvent),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to save event');
        }
        return response.json();
    })
    .then(data => {
        const toastSuccess = new bootstrap.Toast(document.getElementById('toast-success'));
        toastSuccess.show();

        bootstrap.Modal.getInstance(document.getElementById('addToCalendarModal')).hide();
    })
    .catch(error => {
        console.error('Error:', error);

        const toastError = new bootstrap.Toast(document.getElementById('toast-error'));
        toastError.show();
    });
});

document.addEventListener('click', function (e) {
    if (e.target.classList.contains('view-artist-details')) {
        const artistData = JSON.parse(e.target.getAttribute('data-artist'));

        // Populate modal with artist details
        document.getElementById('artist-modal-name').innerText = artistData.name;
        document.getElementById('artist-followers').innerText = artistData.followers.toLocaleString();
        document.getElementById('artist-popularity').innerText = artistData.popularity;
        document.getElementById('artist-image').src = artistData.image;
        document.getElementById('artist-spotify-link').href = artistData.spotify;
        document.getElementById('artist-genres').innerText = artistData.genres.length > 0
            ? artistData.genres.join(', ') 
            : 'No genres available'; 

        // Show the modal
        new bootstrap.Modal(document.getElementById('artistInfoModal')).show();
    }
});