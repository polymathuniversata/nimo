import { useState } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { UserProvider } from "./contexts/UserContext";
import Navbar from "./components/Navbar";
import Header from "./components/Header";
import Hero from "./components/Hero";
import Features from "./components/Features";
import Footer from "./components/Footer";
import Stats from "./components/Stats";
import AuthPage from "./pages/AuthPage";
import Dashboard from "./pages/Dashboard";
import Contributions from "./pages/Contributions";
import Profile from "./pages/Profile";
import Skills from "./pages/Skills";

function App() {
  return (
    <UserProvider>
      <div className="bg-[#020617] text-white font-inter overflow-x-hidden min-h-screen">
        <Routes>
          <Route
            path="/"
            element={
              <>
                <Header />
                <Hero />
                <Features />
                <Stats />
                <Footer />
              </>
            }
          />
          <Route path="/auth" element={<AuthPage />} />
          <Route
            path="/*"
            element={
              <ProtectedRoutes />
            }
          />
        </Routes>
      </div>
    </UserProvider>
  );
}

function ProtectedRoutes() {
  const [user] = useState(JSON.parse(localStorage.getItem('nimo_user')));
  const [walletConnected, setWalletConnected] = useState(false);

  const handleConnectWallet = () => setWalletConnected(true);

  if (!user) {
    return <Navigate to="/auth" replace />;
  }

  return (
    <>
      <Navbar />
      <Routes>
        <Route
          path="/dashboard"
          element={
            <Dashboard
              user={user}
              walletConnected={walletConnected}
              onConnectWallet={handleConnectWallet}
            />
          }
        />
        <Route path="/contributions" element={<Contributions user={user} />} />
        <Route path="/profile" element={<Profile user={user} />} />
        <Route path="/skills" element={<Skills />} />
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </>
  );
}

// Wrap App with Router in main.jsx or index.js
export default App;