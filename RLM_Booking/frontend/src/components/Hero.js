import React from "react";
import Box from "@mui/material/Box";
import Grid from "@mui/material/Grid";
import Typography from "@mui/material/Typography";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Button from "@mui/material/Button";
import SHLogo from "../assets/images/SHLogo.png"; // Update path to your logo

function Hero() {
    return (
        <Box
            sx={{
                textAlign: "center",
                padding: 4,
                backgroundColor: "#f5f5f5",
            }}
        >
            <img
                src={SHLogo}
                alt="StarrHill Logo"
                style={{ width: "150px", marginBottom: "20px" }}
            />
            <Typography variant="h4" sx={{ marginBottom: 3 }}>
                All-in-one platform for events and artists
            </Typography>
            <Grid container spacing={3} justifyContent="center">
                <Grid item xs={12} sm={6} md={4}>
                    <Card sx={{ padding: 2 }}>
                        <CardContent>
                            <Typography variant="h5" gutterBottom>
                                Artist Recommendation
                            </Typography>
                            <Typography variant="body2">
                                Find your ideal artist using the trained model.
                            </Typography>
                            <Button
                                variant="contained"
                                color="error"
                                href="/artist_recommendation"
                                sx={{ marginTop: 2 }}
                            >
                                Get Started
                            </Button>
                        </CardContent>
                    </Card>
                </Grid>
                <Grid item xs={12} sm={6} md={4}>
                    <Card sx={{ padding: 2 }}>
                        <CardContent>
                            <Typography variant="h5" gutterBottom>
                                Manage Possible Events
                            </Typography>
                            <Typography variant="body2">
                                Find your favorite artists within the area at your preferred time.
                            </Typography>
                            <Button
                                variant="contained"
                                color="error"
                                href="/event_management"
                                sx={{ marginTop: 2 }}
                            >
                                Manage
                            </Button>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>
        </Box>
    );
}

export default Hero;
