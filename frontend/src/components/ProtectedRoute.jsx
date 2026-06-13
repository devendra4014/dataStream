/* eslint-disable react/prop-types */
import { Navigate } from 'react-router-dom';

const ProtectedRoute = ({ children }) => {
    // Check if our fake token exists in local storage
    const token = localStorage.getItem('access_token');

    if (!token) {
        // Redirect to the login page if there is no token
        return <Navigate to="/login" replace />;
    }

    return children;
};

export default ProtectedRoute;