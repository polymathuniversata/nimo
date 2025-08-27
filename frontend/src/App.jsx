import { useState } from "react";
import Header from "./components/Header";
import Hero from "./components/Hero";
import Features from "./components/Features";
import Stats from "./components/Stats";
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
  };

  const handleConnectWallet = () => setWalletConnected(true);

  return (
    <div className="bg-[#020617] text-white font-inter overflow-x-hidden min-h-screen">
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
    </div>
  );
}

export default App;
