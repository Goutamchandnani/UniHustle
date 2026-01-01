import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const PrivateRoute = ({ children }) => {
    const { token, loading } = useAuth();

    if (loading) {
        return (
            <div className="flex h-screen items-center justify-center">
                <div className="text-slate-500">Loading...</div>
            </div>
        );
    }

    return token ? children : <Navigate to="/login" />;
};

export default PrivateRoute;
