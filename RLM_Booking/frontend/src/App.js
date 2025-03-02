import React from "react";
import { Routes, Route } from "react-router-dom";
import Layout from "./components/common/Layout";
import HomePage from "./pages/HomePage";
import ArtistRecommendation from "./pages/ArtistRecommendation";
import EventManagement from "./pages/EventManagement";
import { ArtistProvider } from "./context/ArtistContext"; 

function App() {
    return (
        <Layout className="m-0">
            <Routes>
                <Route path="/" element={<HomePage />} />
                <Route 
                    path="/artist_recommendation" 
                    element={
                        <ArtistProvider>
                            <ArtistRecommendation />
                        </ArtistProvider>
                    } 
                />
                <Route path="/event_management" element={<EventManagement />} />
            </Routes>
        </Layout>
    );
}

export default App;