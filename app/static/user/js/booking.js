/* ========================
1. Booking Details Logic
======================== */

$(document).ready(function () {
    // Initialize datepicker
    $('#date').datepicker({
        format: 'yyyy-mm-dd',
        startDate: new Date(),
        autoclose: true,
        todayHighlight: true
    }).on('changeDate', function (e) {
        // Ensure date is formatted correctly
        const selectedDate = $(this).datepicker('getFormattedDate');
        $(this).val(selectedDate);
        updateBookingSummary();
    });

    // If no date is set, default to today
    if (!$('#date').val()) {
        $('#date').datepicker('setDate', new Date());
    }

    // Set default times if not already set
    if (!$('#start_time').val() || !$('#end_time').val()) {
        const now = new Date();
        const hours = now.getHours();
        const minutes = now.getMinutes();

        // Round to nearest 30 minutes
        const roundedMinutes = Math.ceil(minutes / 30) * 30;
        const startHour = hours + Math.floor(roundedMinutes / 60);
        const startMin = roundedMinutes % 60;

        // Format time as HH:MM
        const startTime = `${String(startHour).padStart(2, '0')}:${String(startMin).padStart(2, '0')}`;
        const endTime = `${String(startHour + 1).padStart(2, '0')}:${String(startMin).padStart(2, '0')}`;

        if (!$('#start_time').val()) {
            $('#start_time').val(startTime);
        }

        if (!$('#end_time').val()) {
            $('#end_time').val(endTime);
        }
    }

    // Update booking summary when inputs change
    function updateBookingSummary() {
        const date = $('#date').val();
        const startTime = $('#start_time').val();
        const endTime = $('#end_time').val();
        const vehicleNumber = $('#vehicle_number').val();

        if (date) {
            $('#summaryDate').text(date);
        }

        if (startTime && endTime) {
            $('#summaryTime').text(`${startTime} to ${endTime}`);

            // Calculate duration
            const start = new Date(`2000-01-01T${startTime}`);
            const end = new Date(`2000-01-01T${endTime}`);

            const hourlyRate = parseFloat(document.getElementById('summaryCost').dataset.hourlyRate);

            if (end > start) {
                const durationMs = end - start;
                const durationHours = durationMs / (1000 * 60 * 60);
                $('#summaryDuration').text(`${durationHours.toFixed(1)} hours`);

                // Calculate cost
                const cost = durationHours * hourlyRate;
                $('#summaryCost').text(`₹${cost.toFixed(2)}`);
            } else {
                $('#summaryDuration').text('-');
                $('#summaryCost').text('₹0.00');
            }
        }

        if (vehicleNumber) {
            $('#summaryVehicle').text(vehicleNumber);
        }
    }

    // Input validation
    function validateForm() {
        let isValid = true;

        // Validate date
        const selectedDate = new Date($('#date').val());
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        if (selectedDate < today) {
            $('#dateError').text('Date cannot be in the past').show();
            isValid = false;
        } else {
            $('#dateError').hide();
        }

        // Validate times
        const startTime = $('#start_time').val();
        const endTime = $('#end_time').val();

        if (!startTime) {
            $('#startTimeError').text('Start time is required').show();
            isValid = false;
        } else {
            $('#startTimeError').hide();
        }

        if (!endTime) {
            $('#endTimeError').text('End time is required').show();
            isValid = false;
        } else {
            $('#endTimeError').hide();
        }

        // Check if end time is after start time
        if (startTime && endTime) {
            const start = new Date(`2000-01-01T${startTime}`);
            const end = new Date(`2000-01-01T${endTime}`);

            if (end <= start) {
                $('#endTimeError').text('End time must be after start time').show();
                isValid = false;
            } else {
                $('#endTimeError').hide();
            }
        }

        return isValid;
    }

    // Set up event listeners
    $('#date, #start_time, #end_time, #vehicle_number').on('change', updateBookingSummary);

    // Form submission with enhanced validation
    $('#bookingForm').on('submit', function (e) {
        // Format vehicle number to uppercase to match pattern
        const vehicleInput = $('#vehicle_number');
        vehicleInput.val(vehicleInput.val().toUpperCase().trim());

        // Ensure date is in yyyy-mm-dd format
        const dateInput = $('#date');
        const dateVal = dateInput.val();

        // Check date format
        if (!/^\d{4}-\d{2}-\d{2}$/.test(dateVal)) {
            $('#dateError').text('Invalid date format. Use YYYY-MM-DD').show();
            e.preventDefault();
            return false;
        }

        // Verify all validation rules
        if (!validateForm()) {
            e.preventDefault();
            return false;
        }

        // Vehicle number state code validation
        if (!validateVehicleNumberJS()) {
            e.preventDefault();
            return false;
        }

        return true;
    });

    // Initialize summary
    updateBookingSummary();

    // Helper function for vehicle number formatting
    $('#vehicle_number').on('input', function () {
        const vehicleInput = document.getElementById('vehicle_number');
        const errorDiv = document.getElementById('vehicleError');
        const value = vehicleInput.value.trim().toUpperCase();
        const stateCode = value.substring(0, 2);

        if (value.length >= 2 && !validStateCodes.includes(stateCode)) {
            if (errorDiv) {
                errorDiv.textContent = "Vehicle number must start with a valid Indian state code, Please refer below Vehicle Number Format.";
                errorDiv.style.display = 'block';
            }
            vehicleInput.classList.add('is-invalid');
            vehicleInput.classList.remove('is-valid');
        } else if (value.length >= 2 && validStateCodes.includes(stateCode)) {
            if (errorDiv) {
                errorDiv.textContent = "";
                errorDiv.style.display = 'none';
            }
            vehicleInput.classList.remove('is-invalid');
            vehicleInput.classList.add('is-valid');
        } else if (value.length < 2) {
            if (errorDiv) {
                errorDiv.textContent = "";
                errorDiv.style.display = 'none';
            }
            vehicleInput.classList.remove('is-invalid');
            vehicleInput.classList.remove('is-valid');
        }
    });
});

const validStateCodes = [
    "AP", "AR", "AS", "BR", "CG", "GA", "GJ", "HR", "HP", "JH", "KA", "KL", "MP", "MH", "ML", "MN", "MZ", "NL", "OD", "PB", "RJ",
    "SK", "TN", "TS", "TR", "UP", "UK", "WB", "AN", "CH", "DD", "DN", "DL", "JK", "LA", "LD", "PY"
];

function validateVehicleNumberJS() {
    const vehicleInput = document.getElementById('vehicle_number');
    const errorDiv = document.getElementById('vehicleError');
    if (!vehicleInput) return true;
    const value = vehicleInput.value.trim().toUpperCase();
    const stateCode = value.substring(0, 2);
    if (!validStateCodes.includes(stateCode)) {
        if (errorDiv) {
            errorDiv.textContent = "Vehicle number must start with a valid Indian state code, Please refer Vehicle Number Format.";
            errorDiv.style.display = 'block';
        }
        vehicleInput.classList.add('is-invalid');
        vehicleInput.classList.remove('is-valid');
        return false;
    } else {
        if (errorDiv) {
            errorDiv.textContent = "";
            errorDiv.style.display = 'none';
        }
        vehicleInput.classList.remove('is-invalid');
        vehicleInput.classList.add('is-valid');
    }
    return true;
}


/* ========================
2. Booking Slot Logic 
======================== */

$(document).ready(function () {
    let selectedSlotId = null;
    let currentVehicleType = null;

    // Handle vehicle type selection
    $('.vehicle-type-btn').on('click', function () {
        const vehicleType = $(this).data('vehicle-type');

        // Reset selections
        $('.vehicle-type-btn').removeClass('active');
        $(this).addClass('active');
        $('#slotsGrid').empty();
        $('#selectedSlotDetails').hide();
        selectedSlotId = null;
        currentVehicleType = vehicleType;

        // Show slot selection area
        $('#slotSelectionArea').show();
        $('#continueBtn').prop('disabled', true);

        // Load slots for the selected vehicle type
        const locationId = parseInt($('#slotSelectionArea').data('location-id'), 10);
        loadSlots(locationId, vehicleType);
        // Update form field
        $('#vehicleType').val(vehicleType);
    });

    // Function to load slots
    function loadSlots(locationId, vehicleType) {
        $.ajax({
            url: `/parking/api/slots/${locationId}/${vehicleType}`,
            method: 'GET',
            success: function (slots) {
                if (slots.length > 0) {
                    $('#noSlotsMessage').hide();
                    $('#slotsGrid').empty();

                    // Create slot elements - only show available slots
                    slots.forEach(function (slot) {
                        // Only create elements for available slots
                        if (slot.is_available) {
                            const slotElement = $(`
                                <div class="slot available" data-slot-id="${slot.id}" data-slot-number="${slot.slot_number}" data-hourly-rate="${slot.hourly_rate}" data-vehicle-type="${slot.vehicle_type}">
                                    ${slot.slot_number}
                                </div>
                            `);
                            $('#slotsGrid').append(slotElement);
                        }
                    });

                    // Add click handler to available slots
                    $('.slot.available').on('click', function () {
                        // Remove selection from all slots
                        $('.slot').removeClass('selected');

                        // Add selection to clicked slot
                        $(this).addClass('selected');

                        // Get slot details
                        selectedSlotId = $(this).data('slot-id');
                        const slotNumber = $(this).data('slot-number');
                        const vehicleTypeName = $(this).data('vehicle-type') === 'two-wheeler' ? 'Two Wheeler' : 'Four Wheeler';
                        const hourlyRate = $(this).data('hourly-rate');

                        // Update slot details display
                        $('#slotNumber').text(slotNumber);
                        $('#slotVehicleType').text(vehicleTypeName);
                        $('#slotRate').text(`₹${hourlyRate}/hour`);
                        $('#selectedSlotDetails').show();

                        // Update form field
                        $('#slotId').val(selectedSlotId);

                        // Enable continue button
                        $('#continueBtn').prop('disabled', false);
                    });
                } else {
                    $('#slotsGrid').empty();
                    $('#noSlotsMessage').show();
                }
            },
            error: function (error) {
                console.error('Error loading slots:', error);
                $('#slotsGrid').html('<div class="alert alert-danger">Error loading slots. Please try again.</div>');
            }
        });
    }

    // Form validation
    $('#slotForm').on('submit', function (e) {
        if (!selectedSlotId || !currentVehicleType) {
            e.preventDefault();
            alert('Please select a parking slot');
            return false;
        }

        return true;
    });
});


/* ========================
Booking Confirmation Logic 
======================== */

$(document).ready(function () {
    // Handle payment method selection
    $('.payment-option').on('click', function () {
        const paymentMethod = $(this).data('payment-method');

        // Unselect all payment options
        $('.payment-option').removeClass('selected');
        $('input[name="payment_method"]').prop('checked', false);

        // Select clicked payment option
        $(this).addClass('selected');
        $(`#${paymentMethod}Option`).prop('checked', true);
    });

    // Form validation
    $('#paymentForm').on('submit', function (e) {
        const paymentMethod = $('input[name="payment_method"]:checked').val();

        if (!paymentMethod) {
            e.preventDefault();
            alert('Please select a payment method');
            return false;
        }

        // If RazorPay is selected, we would integrate their API here
        if (paymentMethod === 'razorpay') {
            // In further process, integrate with their JavaScript SDK
            alert('Test Mode: Razorpay integration is active in test mode. No real payment will be processed.');
        }

        return true;
    });
}); 