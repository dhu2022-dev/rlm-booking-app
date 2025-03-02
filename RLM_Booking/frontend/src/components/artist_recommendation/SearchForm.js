import React, { useState } from "react";
import { Box, TextField, Button, Grid } from "@mui/material";
import BASE_URL from "../../config";
import { useArtistContext } from "../../context/ArtistContext"; // Use the context hook

function SearchForm() {
    const { dispatch } = useArtistContext(); // Get dispatch from context
    const [formValues, setFormValues] = useState({
        artist: "",
        country: "US",
        city: "Boston",
    });

    const handleChange = (e) => {
        setFormValues({ ...formValues, [e.target.name]: e.target.value });
    };

    const handleSearch = async () => {
        try {
            if (!formValues.artist.trim()) {
                console.error("Artist name cannot be empty.");
                return;
            }

            // Dispatch action to update search params in context
            dispatch({ type: "SET_SEARCH_PARAMS", payload: formValues });

            // Fetch artists
            const response = await fetch(
                `${BASE_URL}/api/artist-recommendation/search-artist/?name=${encodeURIComponent(formValues.artist)}&country=${encodeURIComponent(formValues.country)}&city=${encodeURIComponent(formValues.city)}`
            );

            const artistData = await response.json();

            if (!Array.isArray(artistData) || artistData.length === 0) {
                console.warn("No artists found.");
                dispatch({ type: "SET_ARTISTS", payload: [] });
                return;
            }

            dispatch({ type: "SET_ARTISTS", payload: artistData });
        } catch (error) {
            console.error("Error fetching artists:", error);
        }
    };

    return (
        <Box component="form" sx={{ m: 5, textAlign: "center" }}>
            <Grid container spacing={2} justifyContent="center">
                <Grid item>
                    <TextField
                        name="artist"
                        label="Artist Name"
                        variant="outlined"
                        required
                        value={formValues.artist} 
                        onChange={handleChange}
                        InputProps={{ style: { backgroundColor: "white", color: "black", borderRadius: "4px" } }}
                        InputLabelProps={{
                            style: {
                                color: "#ffcccc",
                                fontWeight: "bold",
                                transform: "translate(0, -1.5rem)",
                                backgroundColor: "#121212", 
                                padding: "0 4px", 
                            },
                        }}
                    />
                </Grid>
                <Grid item>
                    <TextField
                        name="country"
                        label="Country Code (e.g., US)"
                        variant="outlined"
                        value={formValues.country}
                        onChange={handleChange}
                        InputProps={{ style: { backgroundColor: "white", color: "black", borderRadius: "4px" } }}
                        InputLabelProps={{
                            style: {
                                color: "#ffcccc",
                                fontWeight: "bold",
                                transform: "translate(0, -1.5rem)", 
                                backgroundColor: "#121212",
                                padding: "0 4px",
                            },
                        }}
                    />
                </Grid>
                <Grid item>
                    <TextField
                        name="city"
                        label="City"
                        variant="outlined"
                        value={formValues.city}
                        onChange={handleChange}
                        InputProps={{ style: { backgroundColor: "white", color: "black", borderRadius: "4px" } }}
                        InputLabelProps={{
                            style: {
                                color: "#ffcccc",
                                fontWeight: "bold",
                                transform: "translate(0, -1.5rem)",
                                backgroundColor: "#121212",
                                padding: "0 4px",
                            },
                        }}
                    />
                </Grid>
                <Grid item>
                    <Button variant="contained" color="error" onClick={handleSearch}>
                        Search
                    </Button>
                </Grid>
            </Grid>
        </Box>
    );
}

export default SearchForm;
