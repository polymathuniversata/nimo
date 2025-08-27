import { useState } from "react";

const AuthModal = ({ onLogin }) => {
  const [isConnecting, setIsConnecting] = useState(false);

  const handleWalletConnect = () => {
    setIsConnecting(true);

    // Simulate wallet connection
    setTimeout(() => {
      setIsConnecting(false);

      // Create a wallet user object
      const walletUser = { 
        name: "John Doe", 
        isWalletConnected: true 
      };

      // Pass the user to the parent
      onLogin(walletUser);
    }, 1500);
  };

  return (
    <div className="bg-gray-800 rounded-xl w-full max-w-md p-6">
      <h2 className="text-2xl font-bold text-white mb-6 text-center">Connect Your Wallet</h2>

      <p className="text-gray-400 mb-6 text-center">
        Use your  wallet to log in or sign up. 
      </p>

      <button
        onClick={handleWalletConnect}
        disabled={isConnecting}
        className="w-full bg-purple-600 hover:bg-purple-700 disabled:bg-purple-800 text-white py-3 rounded-lg font-semibold transition-colors flex items-center justify-center gap-2"
      >
        {isConnecting ? (
          <>
            <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            Connecting...
          </>
        ) : (
          "Connect Wallet"
        )}
      </button>
    </div>
  );
};

export default AuthModal;
