import { useState } from "react";

const AuthModal = ({ isOpen, onClose, activeTab, setActiveTab, onLogin }) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");

  const dummyUsers = [
    { name: "John Doe", email: "john@example.com", password: "123456" },
  ];

  const handleSubmit = (e) => {
    e.preventDefault();

    if (activeTab === "login") {
      const foundUser = dummyUsers.find(
        (u) => u.email === email && u.password === password
      );
      if (foundUser) {
        onLogin(foundUser); // set user → Dashboard renders
        onClose();
      } else {
        alert("Invalid email or password!");
      }
    } else {
      const newUser = { name, email, password };
      onLogin(newUser); // set new user → Dashboard renders
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-800 rounded-xl max-w-md w-full p-6 relative">
        <button onClick={onClose} className="absolute top-4 right-4 text-gray-400 hover:text-white">
          &times;
        </button>

        <div className="flex border-b border-gray-700 mb-6">
          <button
            className={`py-3 px-6 font-semibold ${activeTab === "login" ? "text-blue-400 border-b-2 border-blue-400" : "text-gray-400"}`}
            onClick={() => setActiveTab("login")}
          >
            Login
          </button>
          <button
            className={`py-3 px-6 font-semibold ${activeTab === "register" ? "text-blue-400 border-b-2 border-blue-400" : "text-gray-400"}`}
            onClick={() => setActiveTab("register")}
          >
            Sign Up
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {activeTab === "register" && (
            <div>
              <label className="block text-gray-300 mb-2">Full Name</label>
              <input type="text" value={name} onChange={(e) => setName(e.target.value)} className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-white" placeholder="Enter your name" required />
            </div>
          )}

          <div>
            <label className="block text-gray-300 mb-2">Email</label>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-white" placeholder="Enter your email" required />
          </div>

          <div>
            <label className="block text-gray-300 mb-2">Password</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-white" placeholder="Enter your password" required />
          </div>

          <button type="submit" className="w-full bg-blue-500 hover:bg-blue-600 text-white py-3 rounded-lg font-semibold">
            {activeTab === "login" ? "Login" : "Sign Up"}
          </button>
        </form>
      </div>
    </div>
  );
};

export default AuthModal;
