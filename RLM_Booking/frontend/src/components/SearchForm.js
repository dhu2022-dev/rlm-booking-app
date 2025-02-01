import React from "react";
import { Box, TextField, Button, Grid } from "@mui/material";

function SearchForm() {
    return (
        <Box component="form" sx={{ mt: 3 }}>
            <Grid container spacing={2} justifyContent="center">
                <Grid item>
                    <TextField
                        label="Artist Name"
                        variant="outlined"
                        required
                        InputProps={{
                            style: { backgroundColor: "white", color: "black", borderRadius: "4px"},
                        }}
                        InputLabelProps={{
                            style: { color: "#ffcccc", fontWeight: "bold" }, 
                        }}
                    />
                </Grid>
                <Grid item>
                    <TextField
                        label="Country Code (e.g., US)"
                        variant="outlined"
                        defaultValue="US"
                        InputProps={{
                            style: { backgroundColor: "white", color: "black", borderRadius: "4px"},
                        }}
                        InputLabelProps={{
                            style: { color: "#ffcccc", fontWeight: "bold" }, 
                        }}
                    />
                </Grid>
                <Grid item>
                    <TextField
                        label="City"
                        variant="outlined"
                        defaultValue="Boston"
                        InputProps={{
                            style: { backgroundColor: "white", color: "black", borderRadius: "4px"},
                        }}
                        InputLabelProps={{
                            style: { color: "#ffcccc", fontWeight: "bold" }, 
                        }}
                    />
                </Grid>
                <Grid item>
                    <Button variant="contained" color="error">
                        Search
                    </Button>
                </Grid>
            </Grid>
        </Box>
    );
}

export default SearchForm;
