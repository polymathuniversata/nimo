import { useState } from "react";
<<<<<<< HEAD
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Header from "./components/Header";
import Hero from "./components/Hero";
import Features from "./components/Features";
import Footer from "./components/Footer";
import Stats from "./components/Stats";
import AuthPage from "./pages/AuthPage";
import Dashboard from "./pages/Dashboard";

function App() {
  const [user, setUser] = useState(null);
  const [walletConnected, setWalletConnected] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [activeTab, setActiveTab] = useState("login");

  const handleLogin = (userData) => {
    setUser(userData);
=======
import Header from "./components/Header";
import Hero from "./components/Hero";
import Features from "./components/Features";
import Stats from "./components/Stats";  /// remove it
import Footer from "./components/Footer";
import AuthModal from "./components/AuthModal";
import Dashboard from "./pages/Dashboard";

function App() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [activeTab, setActiveTab] = useState("login");
  const [user, setUser] = useState(null);
  const [walletConnected, setWalletConnected] = useState(false);

  // This is called after login in AuthModal
  const handleLogin = (mockUser) => {
    setUser(mockUser); // ✅set user → App will render Dashboard
    setIsModalOpen(false);
>>>>>>> origin/main
  };

  const handleConnectWallet = () => setWalletConnected(true);

  return (
    <div className="bg-[#020617] text-white font-inter overflow-x-hidden min-h-screen">
<<<<<<< HEAD
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
        <Route
          path="/auth"
          element={
            user ? (
              <Navigate to="/dashboard" replace />
            ) : (
              <AuthPage onLogin={handleLogin} />
            )
          }
        />
        <Route
          path="/dashboard"
          element={
            user ? (
              <Dashboard
                user={user}
                walletConnected={walletConnected}
                onConnectWallet={handleConnectWallet}
              />
            ) : (
              <Navigate to="/auth" replace />
            )
          }
        />
      </Routes>
=======
      {!user ? (
        <>
          <Header setIsModalOpen={setIsModalOpen} setActiveTab={setActiveTab} />
          <Hero />
          <Features />
          <Stats />
          <Footer />
          {isModalOpen && (
            <AuthModal
              isOpen={isModalOpen}
              onClose={() => setIsModalOpen(false)}
              activeTab={activeTab}
              setActiveTab={setActiveTab}
              onLogin={handleLogin} // pass login handler
            />
          )}
        </>
      ) : (
        <Dashboard
          user={user}
          walletConnected={walletConnected}
          onConnectWallet={handleConnectWallet}
        /> // show Dashboard after login
      )}
>>>>>>> origin/main
    </div>
  );
}

<<<<<<< HEAD
// Wrap App with Router in main.jsx or index.js
export default App;
=======
export default App;
>>>>>>> origin/main
