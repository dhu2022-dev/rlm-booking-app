console.log("JavaScript file loaded successfully!");

document.addEventListener("DOMContentLoaded", function () {
    const availabilityForm = document.getElementById("availabilityForm");
    if (availabilityForm) {
        availabilityForm.addEventListener("submit", async function (event) {
            event.preventDefault();

            // Collect form input values
            const artist = document.getElementById("artistSearchInput").value.trim();
            const zipCode = document.getElementById("zipCodeInput").value.trim();
            const radius = document.getElementById("radiusInput").value.trim();
            const startDate = document.getElementById("startDateInput").value.trim();
            const endDate = document.getElementById("endDateInput").value.trim();

            // Debugging logs
            console.log("Artist:", artist);
            console.log("Zip Code:", zipCode);
            console.log("Radius:", radius);
            console.log("Start Date:", startDate);
            console.log("End Date:", endDate);

            // Build query string
            const queryParams = new URLSearchParams({
                artist: artist || "",
                zipCode: zipCode || "",
                radius: radius || "",
                startDate: startDate || "",
                endDate: endDate || "",
            });
            console.log("Query Params:", queryParams.toString());

            try {
                // Fetch availability results
                const response = await fetch(`/event_management/search-events/?${queryParams.toString()}`);
                if (!response.ok) {
                    console.error(`Error: ${response.status} - ${response.statusText}`);
                    throw new Error("Failed to fetch availability data.");
                }

                const events = await response.json();
                console.log("Fetched Events:", events);

                // Populate the results table
                populateAvailabilityTable(events);
            } catch (error) {
                console.error("Error fetching availability:", error);
            }
        });
    } else {
        console.error("Availability form not found in the DOM.");
    }
});

function populateAvailabilityTable(events) {
    const tableBody = document.getElementById("availabilityResultsTable");
    tableBody.innerHTML = "";

    if (events.length === 0) {
        const noResultsRow = document.createElement("tr");
        noResultsRow.innerHTML = `<td colspan="5" class="text-center">No events found.</td>`;
        tableBody.appendChild(noResultsRow);
    } else {
        events.forEach((event) => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${event.artist || "Unknown"}</td>
                <td>${event.name || "Unknown"}</td>
                <td>${event.venue || "Unknown"}</td>
                <td>${event.date || "Unknown"}</td>
                <td>${event.location || "Unknown"}</td>
            `;
            tableBody.appendChild(row);
        });
    }
}

function clearTable() {
    const tableBody = document.getElementById("availabilityResultsTable");
    tableBody.innerHTML = `<tr><td colspan="5" class="text-center">Start typing to search for events.</td></tr>`;
}

let debounceTimer;
function debounce(func, delay) {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(func, delay);
}
