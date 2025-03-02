import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import { ArtistProvider } from "./context/ArtistContext";

document.body.style.margin = "0";
document.body.style.padding = "0";
document.body.style.backgroundColor = "#121212"; // Dark theme example

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
    <React.StrictMode>
        <BrowserRouter>
            <ArtistProvider>
                <App />
            </ArtistProvider>
        </BrowserRouter>
    </React.StrictMode>
);
