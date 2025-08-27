<<<<<<< HEAD
import React, { createContext, useContext, useState } from "react";

// Create context
const UserContext = createContext();

export const UserProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);

  // Dummy users database
  const dummyUsers = [
    { name: "John Doe", email: "john@example.com", password: "123456" },
    { name: "Jane Smith", email: "jane@example.com", password: "abcdef" },
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

    const newUser = { name, email, password };
    dummyUsers.push(newUser);
    setUser(newUser);
    setLoading(false);
    return { success: true };
  };

  const logout = () => {
    setUser(null);
  };

  // Add isAuthenticated
  const isAuthenticated = !!user;

  return (
    <UserContext.Provider
      value={{ user, login, register, logout, loading, isAuthenticated }}
    >
      {children}
    </UserContext.Provider>
  );
};

// Hook to use context
export const useUser = () => useContext(UserContext);
=======
import React, { createContext, useContext, useState } from 'react'

// Create context
const UserContext = createContext()

export const UserProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(false)

  // Dummy users database
  const dummyUsers = [
    { name: 'John Doe', email: 'john@example.com', password: '123456' },
    { name: 'Jane Smith', email: 'jane@example.com', password: 'abcdef' },
  ]

  const login = async (email, password) => {
    setLoading(true)
    await new Promise((res) => setTimeout(res, 500)) // simulate network delay

    const foundUser = dummyUsers.find(
      (u) => u.email === email && u.password === password
    )

    setLoading(false)
    if (foundUser) {
      setUser(foundUser)
      return { success: true }
    } else {
      alert('Invalid email or password!')
      return { success: false }
    }
  }

  const register = async (name, email, password) => {
    setLoading(true)
    await new Promise((res) => setTimeout(res, 500)) // simulate network delay

    // Check if email exists
    if (dummyUsers.some((u) => u.email === email)) {
      setLoading(false)
      alert('Email already exists!')
      return { success: false }
    }

    const newUser = { name, email, password }
    dummyUsers.push(newUser)
    setUser(newUser)
    setLoading(false)
    return { success: true }
  }

  const logout = () => {
    setUser(null)
  }

  return (
    <UserContext.Provider value={{ user, login, register, logout, loading }}>
      {children}
    </UserContext.Provider>
  )
}

// Hook to use context
export const useUser = () => useContext(UserContext)
>>>>>>> origin/main
