const BASE_URL = window.location.hostname === "localhost"
    ? "http://127.0.0.1:8000"
    : "https://api.starrhill-booking.com"; // Replace with your real production URL

export default BASE_URL;
