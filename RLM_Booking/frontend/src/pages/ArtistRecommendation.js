import React, { useState } from "react";
import SearchForm from "../components/SearchForm";
import MapSection from "../components/MapSection";
import AddToCalendarModal from "../components/AddToCalendarModal";
import ToastNotifications, { showSuccess, showError } from "../components/ToastNotifications";

function ArtistRecommendation() {
    const [modalOpen, setModalOpen] = useState(false);

    return (
            <div style={{ backgroundColor: "#121212", color: "white", minHeight: "100vh", padding: "20px" }}>
                <SearchForm />
                <button
                    onClick={() => setModalOpen(true)}
                    style={{ margin: "20px", backgroundColor: "#d32f2f", color: "white", padding: "10px 20px", border: "none", cursor: "pointer" }}
                >
                    Open Add to Calendar Modal
                </button>
                <MapSection />
                <AddToCalendarModal open={modalOpen} handleClose={() => setModalOpen(false)} />
                <ToastNotifications />
            </div>
    );
}

export default ArtistRecommendation;
