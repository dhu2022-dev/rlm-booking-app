import React from "react";
import AppBar from "@mui/material/AppBar";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";
import Button from "@mui/material/Button";
import { Link } from "react-router-dom";

function Navbar() {
    return (
        <AppBar position="static" sx={{ backgroundColor: "#d32f2f" }}>
            <Toolbar>
                <Typography
                    variant="h6"
                    component="div"
                    sx={{ flexGrow: 1, fontWeight: "bold" }}
                >
                    StarrHill Booking
                </Typography>
                <Button color="inherit" component={Link} to="/">
                    Home
                </Button>
                <Button color="inherit" component={Link} to="/artist_recommendation">
                    Artist Recommendation
                </Button>
                <Button color="inherit" component={Link} to="/event_management">
                    Event Management
                </Button>
            </Toolbar>
        </AppBar>
    );
}

export default Navbar;
