import React from "react";
import { Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Hero from "./components/Hero";
//import HomePage from "./pages/HomePage";
import ArtistRecommendation from "./pages/ArtistRecommendation";
import EventManagement from "./pages/EventManagement";

function App() {
    return (
        <Layout>
            <Routes>
                {/* Define routes for the app */}
                <Route path="/" element={<Hero />} />
                <Route path="/artist_recommendation" element={<ArtistRecommendation />} />
                <Route path="/event_management" element={<EventManagement />} />
            </Routes>
        </Layout>
    );
}

export default App;
