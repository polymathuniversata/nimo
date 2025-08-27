import React, { createContext, useContext, useState } from "react";

// Create context
const UserContext = createContext();

export const UserProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const savedUser = localStorage.getItem('nimo_user');
    return savedUser ? JSON.parse(savedUser) : null;
  });
  const [loading, setLoading] = useState(false);

  // Dummy users database
  const dummyUsers = [
    { 
      name: "John Doe", 
      email: "john@example.com", 
      password: "123456",
      location: "San Francisco, CA",
      bio: "Full-stack developer passionate about blockchain and social impact",
      skills: ["React", "Node.js", "Solidity", "UI/UX Design"]
    },
    { 
      name: "Jane Smith", 
      email: "jane@example.com", 
      password: "abcdef",
      location: "New York, NY",
      bio: "Community organizer and environmental advocate",
      skills: ["Community Management", "Environmental Advocacy", "Content Creation"]
    },
  ];

  const login = async (email, password) => {
    setLoading(true);
    await new Promise((res) => setTimeout(res, 500)); // simulate network delay

    const foundUser = dummyUsers.find(
      (u) => u.email === email && u.password === password
    );

    setLoading(false);
    if (foundUser) {
      setUser(foundUser);
      localStorage.setItem('nimo_user', JSON.stringify(foundUser));
      return { success: true };
    } else {
      alert("Invalid email or password!");
      return { success: false };
    }
  };

  const register = async (name, email, password) => {
    setLoading(true);
    await new Promise((res) => setTimeout(res, 500)); // simulate network delay

    if (dummyUsers.some((u) => u.email === email)) {
      setLoading(false);
      alert("Email already exists!");
      return { success: false };
    }

    const newUser = { name, email, password, location: '', bio: '', skills: [] };
    dummyUsers.push(newUser);
    setUser(newUser);
    localStorage.setItem('nimo_user', JSON.stringify(newUser));
    setLoading(false);
    return { success: true };
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('nimo_user');
  };

  const updateUser = (updatedUserData) => {
    const updatedUser = { ...user, ...updatedUserData };
    setUser(updatedUser);
    localStorage.setItem('nimo_user', JSON.stringify(updatedUser));
  };

  // Add isAuthenticated
  const isAuthenticated = !!user;

  return (
    <UserContext.Provider
      value={{ user, login, register, logout, updateUser, loading, isAuthenticated }}
    >
      {children}
    </UserContext.Provider>
  );
};

// Hook to use context
export const useUser = () => useContext(UserContext);
