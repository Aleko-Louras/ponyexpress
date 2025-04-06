import {createContext, useContext, useState} from "react";
import PropTypes from "prop-types";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
    const [loggedIn, setLoggedIn] = useState(false);

    const login = () => {
        setLoggedIn(true);
    }
    const logout = async () => {
        await fetch("http://localhost:8000/auth/web/logout", {
            method: "POST",
            credentials: "include",
        });
        setLoggedIn(false);
    }

    return (<AuthContext.Provider value={{loggedIn, login, logout, setLoggedIn}}>
        {children}
    </AuthContext.Provider>);
}

export const useAuth = () => useContext(AuthContext)

AuthProvider.propTypes = {
    children: PropTypes.node,
};