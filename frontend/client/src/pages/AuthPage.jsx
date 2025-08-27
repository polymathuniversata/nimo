import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import AuthModal from "./AuthModal";

const AuthPage = ({ onLogin }) => {
  const [activeTab, setActiveTab] = useState("login");
  const navigate = useNavigate();

  const handleLogin = (userData) => {
    onLogin(userData);
    navigate("/dashboard");
  };

  return (
    <div className="min-h-screen bg-[#020617] flex flex-col">
      <header className="px-6 py-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <Link to="/" className="text-2xl font-bold text-white flex items-center">
            <span className="bg-blue-500 rounded-lg p-2 mr-2">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
            </span>
            Nimo
          </Link>
          <Link to="/" className="text-gray-300 hover:text-white transition-colors">
            ← Back to Home
          </Link>
        </div>
      </header>

      <div className="flex-grow flex items-center justify-center px-4 py-12">
        <div className="w-full max-w-md">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-white mb-2">
              {activeTab === "login" ? "Welcome Back" : "Create Account"}
            </h1>
            <p className="text-gray-400">
              {activeTab === "login" ? "Sign in to access" : "Join us to start your journey"}
            </p>
          </div>

          <AuthModal
            onLogin={handleLogin}
            activeTab={activeTab}
            setActiveTab={setActiveTab}
          />
        </div>
      </div>
    </div>
  );
};

export default AuthPage;
