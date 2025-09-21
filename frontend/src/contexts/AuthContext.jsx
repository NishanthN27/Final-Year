import React, { createContext, useState, useContext, useEffect } from 'react';
import { jwtDecode } from 'jwt-decode';

// 1. Create the context
const AuthContext = createContext(null);

// 2. Create the provider component
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check for a token in localStorage when the app loads
    try {
      const token = localStorage.getItem('accessToken');
      if (token) {
        const decodedUser = jwtDecode(token);
        // Optional: Check if the token is expired
        if (decodedUser.exp * 1000 > Date.now()) {
          setUser({
            id: decodedUser.user_id,
            role: decodedUser.role,
          });
        } else {
          // Token is expired, remove it
          localStorage.removeItem('accessToken');
          localStorage.removeItem('refreshToken');
        }
      }
    } catch (error) {
      console.error("Failed to decode token on initial load", error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Login function
  const login = (accessToken) => {
    try {
      const decodedUser = jwtDecode(accessToken);
      localStorage.setItem('accessToken', accessToken);
      setUser({
        id: decodedUser.user_id,
        role: decodedUser.role,
      });
    } catch (error) {
      console.error("Failed to decode token on login", error);
    }
  };

  // Logout function
  const logout = () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    setUser(null);
  };

  // 3. Provide state and functions to children
  return (
    <AuthContext.Provider value={{ user, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

// 4. Create a custom hook for easy access
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
