import { createContext, useReducer, useContext } from "react";

const ArtistContext = createContext();

const initialState = {
    artists: [],
    events: [],
    selectedArtist: null,
    searchParams: { artist: "", country: "US", city: "Boston" }, 
    noEvents: false,
};

function artistReducer(state, action) {
    switch (action.type) {
        case "SET_ARTISTS":
            return { ...state, artists: action.payload };
        case "SET_EVENTS":
            return { ...state, events: action.payload };
        case "SELECT_ARTIST":
            return { ...state, selectedArtist: action.payload };
        case "SET_NO_EVENTS":
            return { ...state, noEvents: action.payload };  
        case "SET_SEARCH_PARAMS":
            return { ...state, searchParams: action.payload };          
        default:
            return state;
    }
}

export function ArtistProvider({ children }) {
    const [state, dispatch] = useReducer(artistReducer, initialState);
    return <ArtistContext.Provider value={{ state, dispatch }}>{children}</ArtistContext.Provider>;
}

export function useArtistContext() {
    return useContext(ArtistContext);
}
