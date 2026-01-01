import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(localStorage.getItem('token'));
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (token) {
            // Setup default header
            api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
            // Try to fetch user details
            fetchUser();
        } else {
            delete api.defaults.headers.common['Authorization'];
            setLoading(false);
        }
    }, [token]);

    const fetchUser = async () => {
        try {
            const response = await api.get('/auth/me');
            setUser(response.data);
        } catch (error) {
            console.error("Failed to fetch user", error);
            logout();
        } finally {
            setLoading(false);
        }
    };

    const login = async (email, password) => {
        const response = await api.post('/auth/login', { email, password });
        const { access_token, ...userData } = response.data;

        localStorage.setItem('token', access_token);
        setToken(access_token);
        // We'll let useEffect fetch the full user profile or just set it here if response has enough info
        // setUser(userData); 
    };

    const register = async (email, password, firstName, lastName) => {
        const response = await api.post('/auth/register', { email, password, firstName, lastName });
        const { access_token } = response.data;

        localStorage.setItem('token', access_token);
        setToken(access_token);
    };

    const logout = () => {
        localStorage.removeItem('token');
        setToken(null);
        setUser(null);
        delete api.defaults.headers.common['Authorization'];
    };

    return (
        <AuthContext.Provider value={{ user, token, login, register, logout, loading }}>
            {!loading && children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
