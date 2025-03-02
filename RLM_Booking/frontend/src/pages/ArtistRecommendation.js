import React from "react";
import { Grid, Box, Typography, Container } from "@mui/material";
import SearchForm from "../components/artist_recommendation/SearchForm";
import MapSection from "../components/artist_recommendation/MapSection";
import ArtistResults from "../components/artist_recommendation/ArtistResults";
import EventResults from "../components/event_management/EventResults";
import { useArtistContext } from "../context/ArtistContext";
import BASE_URL from "../config";

function ArtistRecommendation() {
    // Get state and dispatch from context
    const { state, dispatch } = useArtistContext();
    const { artists, events, selectedArtist, noEvents, searchParams } = state;

    // Fetch events when "View Events" is clicked
    const handleArtistSelect = async (artistName, artistPopularity) => {
        if (!artistName) {
            console.error("Artist name is missing.");
            return;
        }
    
        if (!searchParams) {
            console.error("searchParams is undefined.");
            return;
        }
    
        try {
            dispatch({ type: "SELECT_ARTIST", payload: artistName }); // Update selected artist
    
            const response = await fetch(
                `${BASE_URL}/api/artist-recommendation/get-events/?name=${encodeURIComponent(artistName)}&popularity=${artistPopularity}&country=${encodeURIComponent(searchParams?.country || "US")}&city=${encodeURIComponent(searchParams?.city || "")}`
            );
    
            const eventData = await response.json();
    
            if (!eventData || !Array.isArray(eventData.events)) {
                dispatch({ type: "SET_EVENTS", payload: [] });  // Clear events
                dispatch({ type: "SET_NO_EVENTS", payload: true }); // Set no events flag
                return;
            }
    
            dispatch({ type: "SET_EVENTS", payload: eventData.events });
            dispatch({ type: "SET_NO_EVENTS", payload: false });
        } catch (error) {
            console.error("Error fetching events:", error);
            dispatch({ type: "SET_NO_EVENTS", payload: true });
        }
    };       

    // Handle adding events to the calendar
    const handleAddToCalendar = async (event) => {
        try {
            const response = await fetch("/api/event_management/save-event", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(event),
            });

            if (!response.ok) {
                throw new Error("Failed to save event");
            }

            console.log("Event successfully saved:", event);
            alert("Event added to calendar!");
        } catch (error) {
            console.error("Error:", error);
            alert("Failed to add event to calendar.");
        }
    };

    return (
        <Box sx={{ backgroundColor: "#121212", color: "white", minHeight: "100vh", padding: "40px" }}>
            <Container maxWidth="lg">
                <Typography variant="h3" gutterBottom fontWeight="bold" textAlign="center">
                    Artist Recommendation
                </Typography>
                <Typography variant="h6" textAlign="center" sx={{ marginBottom: 3 }}>
                    Find the perfect artist for your next event.
                </Typography>
                
                <SearchForm />

                {/* Artist Results Grid (Above the Map) */}
                {artists.length > 0 && (
                    <Box sx={{ maxHeight: "300px", overflowY: "auto", mb: 4, backgroundColor: "#1f1f1f", borderRadius: "8px", padding: 2 }}>
                        <ArtistResults artists={artists} onArtistSelect={handleArtistSelect} />
                    </Box>
                )}

                {/* Map and Event Results Side by Side */}
                <Grid container spacing={4}>
                    <Grid item xs={12} md={events.length > 0 || noEvents ? 6 : 12}>
                        <MapSection />
                    </Grid>
                    {events.length > 0 ? (
                        <Grid item xs={12} md={6} mt={2}>
                            <Box sx={{ border: "2px solid red", borderRadius: "8px", padding: "16px", backgroundColor: "#1f1f1f" }}>
                                <EventResults events={events} onAddToCalendar={handleAddToCalendar} />
                            </Box>
                        </Grid>
                    ) : (
                        noEvents && (
                            <Grid item xs={12} md={6} mt={2}>
                                <Box sx={{ border: "2px solid red", borderRadius: "8px", padding: "16px", backgroundColor: "#1f1f1f", textAlign: "center" }}>
                                    <Typography variant="h6" color="white">
                                        No events found
                                    </Typography>
                                </Box>
                            </Grid>
                        )
                    )}
                </Grid>
            </Container>
        </Box>
    );
}

export default ArtistRecommendation;
