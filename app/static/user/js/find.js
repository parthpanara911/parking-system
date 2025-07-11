// Initialize the map centered on Ahmedabad
const map = L.map('map').setView([23.0225, 72.5714], 12);

// Add OpenStreetMap tile layer
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

// Store markers for later reference
const markers = {};
let currentLocationId = null;

// Function to determine availability status
function getAvailabilityStatus(available, total) {
    const percentage = (available / total) * 100;
    if (percentage > 50) return { class: 'high-availability', text: 'High Availability' };
    else if (percentage > 20) return { class: 'medium-availability', text: 'Medium Availability' };
    else return { class: 'low-availability', text: 'Low Availability' };
}

// Function to create popup content
function createPopupContent(location) {
    return `
        <div class="popup-content">
            <h5>${location.name}</h5>
            <p>${location.area}, ${location.city}</p>
            <p><i class="far fa-clock me-2"></i>${location.opening_time} - ${location.closing_time}</p>
            <p id="availability-${location.id}"><i class="fas fa-car me-2"></i>${location.available_slots} / ${location.total_slots} spots</p>
            <p><i class="fas fa-rupee-sign me-2"></i>${location.hourly_rate}/hour</p>
            <button class="btn btn-primary btn-sm popup-book-btn" onclick="showParkingDetails(${location.id})">View Details</button>
        </div>
    `;
}

// Function to create location card
function createLocationCard(location) {
    const availability = getAvailabilityStatus(location.available_slots, location.total_slots);

    return `
        <div class="col-md-6 col-lg-4 mb-4">
            <div class="card location-card h-100" data-id="${location.id}">
                <img src="${location.image_url}" class="parking-image" alt="${location.name}">
                <div class="card-body">
                    <h5 class="card-title">${location.name}</h5>
                    <p class="card-text text-muted">${location.area}, ${location.city}</p>
                    
                    <div class="d-flex justify-content-between mb-2">
                        <span class="parking-details"><i class="far fa-clock me-1"></i> ${location.opening_time} - ${location.closing_time}</span>
                        <span class="parking-details"><i class="fas fa-rupee-sign me-1"></i> ${location.hourly_rate}/hour</span>
                    </div>
                    
                    <div class="d-flex justify-content-between align-items-center">
                        <span class="parking-details" id="availability-${location.id}"><i class="fas fa-car me-1"></i> ${location.available_slots} / ${location.total_slots} spots</span>
                        <span class="badge availability-badge ${availability.class}" id="badge-${location.id}">${availability.text}</span>
                    </div>
                </div>
                <div class="card-footer bg-white">
                    <button class="btn btn-primary btn-sm w-100" onclick="showParkingDetails(${location.id})">
                        View Details
                    </button>
                </div>
            </div>
        </div>
    `;
}

// Function to create modal content
function createModalContent(location) {
    const availability = getAvailabilityStatus(location.available_slots, location.total_slots);

    return `
        <div class="text-center mb-3">
            <img src="${location.image_url}" class="img-fluid rounded mb-3" style="max-height: 200px;" alt="${location.name}">
            <h4>${location.name}</h4>
            <span class="badge ${availability.class}" id="badge-${location.id}">${availability.text}</span>
        </div>
        <div class="row mb-3">
            <div class="col-6">
                <p><strong><i class="fas fa-map-marker-alt me-2"></i>Address:</strong></p>
            </div>
            <div class="col-6">
                <p>${location.address}</p>
            </div>
        </div>
        <div class="row mb-3">
            <div class="col-6">
                <p><strong><i class="fas fa-car me-2"></i>Available Slots:</strong></p>
            </div>
            <div class="col-6">
                <p id="availability-${location.id}">${location.available_slots} / ${location.total_slots}</p>
            </div>
        </div>
        <div class="row mb-3">
            <div class="col-6">
                <p><strong><i class="far fa-clock me-2"></i>Timing:</strong></p>
            </div>
            <div class="col-6">
                <p>${location.opening_time} - ${location.closing_time}</p>
            </div>
        </div>
        <div class="row mb-3">
            <div class="col-6">
                <p><strong><i class="fas fa-rupee-sign me-2"></i>Hourly Rate:</strong></p>
            </div>
            <div class="col-6">
                <p>₹${location.hourly_rate}</p>
            </div>
        </div>
    `;
}

// Function to show parking details in modal
function showParkingDetails(locationId) {
    $.ajax({
        url: `/parking/api/locations/${locationId}`,
        method: 'GET',
        success: function (location) {
            $('#parkingModalContent').html(createModalContent(location));
            $('#bookParkingBtn').data('location-id', location.id);
            currentLocationId = location.id;
            $('#parkingDetailsModal').modal('show');
        },
        error: function (error) {
            console.error('Error fetching location details:', error);
        }
    });
}

function updateParkingAvailability() {
    fetch('/parking/api/locations')
        .then(response => response.json())
        .then(data => {
            data.forEach(location => {
                const counterElement = document.querySelector(`#availability-${location.id}`);
                if (counterElement) {
                    counterElement.textContent = `${location.available_slots} / ${location.total_slots} spots`;

                    // Optional: update badge color based on status
                    const badge = document.querySelector(`#badge-${location.id}`);
                    if (badge) {
                        const ratio = location.available_slots / location.total_slots;
                        badge.className = 'badge availability-badge ' + (
                            ratio >= 0.5 ? 'bg-success' :
                                ratio >= 0.25 ? 'bg-warning' :
                                    'bg-danger'
                        );
                    }
                }
            });
        })
        .catch(err => {
            console.error('Error fetching parking data:', err);
        });
}

// Refresh every 30 seconds
setInterval(updateParkingAvailability, 30000);

// Run immediately on page load too
updateParkingAvailability();

// Handle the book button click
$(document).on('click', '#bookParkingBtn', function () {
    if (currentLocationId) {
        // Redirect to the booking details page
        window.location.href = `/parking/booking_details/${currentLocationId}`;
    }
});

// Handle location card clicks
$(document).on('click', '.location-card', function (e) {
    if (!$(e.target).hasClass('btn')) {
        const locationId = $(this).data('id');
        showParkingDetails(locationId);
    }
});

// Fetch parking locations
$(document).ready(function () {
    $.ajax({
        url: '/parking/api/locations',
        method: 'GET',
        success: function (locations) {
            if (locations.length > 0) {
                // Clear loading indicator
                $('#locations-list').empty();

                // Add markers to map and create location cards
                locations.forEach(function (location) {
                    // Create marker
                    const marker = L.marker([location.latitude, location.longitude])
                        .addTo(map)
                        .bindPopup(createPopupContent(location));

                    markers[location.id] = marker;

                    // Create location card
                    $('#locations-list').append(createLocationCard(location));
                });
            } else {
                $('#locations-list').html('<div class="col-12 text-center py-4"><p>No parking locations found.</p></div>');
            }
        },
        error: function (error) {
            console.error('Error fetching locations:', error);
        }
    });
}); 