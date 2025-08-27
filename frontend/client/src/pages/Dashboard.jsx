import React, { useState } from "react";

const Dashboard = () => {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [walletConnected, setWalletConnected] = useState(false);
  const [contributions, setContributions] = useState([
    { id: 1, type: "Volunteering", title: "Community Clean-up", date: "2025-06-01", verified: true },
    { id: 2, type: "Hackathon", title: "KRNL Project", date: "2025-06-15", verified: false },
  ]);
  const [newContribution, setNewContribution] = useState({ type: "", title: "", date: "" });

  const handleWalletConnect = () => setWalletConnected(!walletConnected);

  const handleAddContribution = (e) => {
    e.preventDefault();
    if (!newContribution.type || !newContribution.title || !newContribution.date) return;

    const contribution = {
      ...newContribution,
      id: contributions.length + 1,
      verified: false,
    };
    setContributions([...contributions, contribution]);
    setNewContribution({ type: "", title: "", date: "" });
  };

  const user = {
    name: "John Doe",
    reputation: 120,
    badges: [
      { id: 1, name: "Volunteering Star", redeemable: true },
      { id: 2, name: "Project Hero", redeemable: false },
      { id: 3, name: "Event Enthusiast", redeemable: true },
    ],
    rewards: [
      { id: 1, name: "Internship Tokens", count: 3 },
      { id: 2, name: "Cash Bonus", count: 2 },
      { id: 3, name: "Scholarship", count: 1 },
    ],
  };

  const NavItem = ({ tab, label }) => (
    <li
      className={`cursor-pointer my-2 py-3 px-6 rounded-full text-center transition-all duration-300 ${
        activeTab === tab
          ? "bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow-lg"
          : "text-gray-300 hover:bg-gray-700 hover:text-white"
      }`}
      onClick={() => setActiveTab(tab)}
    >
      {label}
    </li>
  );

  return (
    <div className="flex min-h-screen bg-gradient-to-tr from-gray-900 to-gray-800 text-gray-100">
      {/* Sidebar */}
      <div className="w-64 bg-gray-900/80 backdrop-blur-lg p-6 flex flex-col">
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-600 mb-1">
            YouthID
          </h1>
          <p className="text-gray-400 text-sm">{user.name}</p>
          <p className="text-gray-400 text-sm">Reputation: {user.reputation}</p>

          <button
            onClick={handleWalletConnect}
            className={`mt-3 w-full py-2 rounded-full font-semibold transition-colors ${
              walletConnected
                ? "bg-green-500 hover:bg-green-600 text-white"
                : "bg-blue-600 hover:bg-blue-700 text-white"
            }`}
          >
            {walletConnected ? "Wallet Connected ✅" : "Connect Wallet"}
          </button>
        </div>

        <ul className="space-y-2 flex-1">
          <NavItem tab="dashboard" label="Dashboard" />
          <NavItem tab="contributions" label="Contributions" />
          <NavItem tab="badges" label="Badges" />
          <NavItem tab="rewards" label="Rewards" />
        </ul>
      </div>

      {/* Main Content */}
      <div className="flex-1 p-6 space-y-6">
        {/* Dashboard Interactive Section */}
        {activeTab === "dashboard" && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Reputation Card */}
            <div className="bg-gray-800/50 backdrop-blur-md p-6 rounded-3xl shadow-lg hover:shadow-xl flex flex-col items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-300 mb-4">Reputation</h3>
              <p className="text-4xl font-bold text-green-400 mb-4">{user.reputation}</p>
              <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-full w-full transition-colors">
                Boost Reputation
              </button>
            </div>

            {/* Contributions Card */}
            <div className="bg-gray-800/50 backdrop-blur-md p-6 rounded-3xl shadow-lg hover:shadow-xl flex flex-col items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-300 mb-4">Contributions</h3>
              <p className="text-4xl font-bold text-blue-400 mb-4">{contributions.length}</p>
              <button
                onClick={() => setActiveTab("contributions")}
                className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-full w-full transition-colors"
              >
                Add / View Contributions
              </button>
            </div>

            {/* Badges Card */}
            <div className="bg-gray-800/50 backdrop-blur-md p-6 rounded-3xl shadow-lg hover:shadow-xl flex flex-col items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-300 mb-4">Badges</h3>
              <p className="text-4xl font-bold text-yellow-400 mb-4">{user.badges.length}</p>
              <button
                onClick={() => setActiveTab("badges")}
                className="bg-yellow-600 hover:bg-yellow-700 text-white px-4 py-2 rounded-full w-full transition-colors"
              >
                View / Redeem Badges
              </button>
            </div>
          </div>
        )}

        {/* Contributions Tab */}
        {activeTab === "contributions" && (
          <div>
            <h2 className="text-2xl font-bold mb-4">Your Contributions</h2>

            <form
              onSubmit={handleAddContribution}
              className="mb-6 bg-gray-800/50 backdrop-blur-md p-6 rounded-3xl shadow-lg space-y-3"
            >
              <h3 className="font-semibold text-lg text-gray-300 mb-2">Add New Contribution</h3>
              <input
                type="text"
                placeholder="Type (e.g. Volunteering)"
                value={newContribution.type}
                onChange={(e) => setNewContribution({ ...newContribution, type: e.target.value })}
                className="w-full px-3 py-2 bg-gray-700 rounded-lg"
              />
              <input
                type="text"
                placeholder="Title"
                value={newContribution.title}
                onChange={(e) => setNewContribution({ ...newContribution, title: e.target.value })}
                className="w-full px-3 py-2 bg-gray-700 rounded-lg"
              />
              <input
                type="date"
                value={newContribution.date}
                onChange={(e) => setNewContribution({ ...newContribution, date: e.target.value })}
                className="w-full px-3 py-2 bg-gray-700 rounded-lg"
              />
              <button type="submit" className="w-full bg-blue-600 py-2 rounded-full text-white hover:bg-blue-700">
                Add Contribution
              </button>
            </form>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {contributions.map((c) => (
                <div
                  key={c.id}
                  className={`p-4 rounded-2xl backdrop-blur-md bg-gray-800/50 shadow-md hover:shadow-xl border-l-4 ${
                    c.verified ? "border-green-400" : "border-yellow-400"
                  }`}
                >
                  <h3 className="font-semibold text-lg">{c.title}</h3>
                  <p className="text-gray-300 text-sm">{c.type} — {c.date}</p>
                  <p className={`text-xs mt-1 ${c.verified ? "text-green-400" : "text-yellow-400"}`}>
                    {c.verified ? "Verified" : "Pending Verification"}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Badges Tab */}
        {activeTab === "badges" && (
          <div>
            <h2 className="text-2xl font-bold mb-4">Your Badges / Tokens</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {user.badges.map((badge) => (
                <div
                  key={badge.id}
                  className="p-6 rounded-3xl backdrop-blur-md bg-gray-800/50 shadow-lg hover:shadow-xl flex flex-col items-center"
                >
                  <span className="font-bold text-lg mb-2">{badge.name}</span>
                  {badge.redeemable ? (
                    <button className="mt-2 w-full bg-blue-600 rounded-full py-2 text-white hover:bg-blue-700">
                      Redeem Token
                    </button>
                  ) : (
                    <button className="mt-2 w-full bg-gray-600 rounded-full py-2 text-gray-300 cursor-not-allowed">
                      Not Redeemable
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Rewards Tab */}
        {activeTab === "rewards" && (
          <div>
            <h2 className="text-2xl font-bold mb-4">Available Rewards</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {user.rewards.map((reward) => (
                <div
                  key={reward.id}
                  className="p-6 rounded-3xl bg-gradient-to-r from-blue-500 to-purple-600 shadow-lg hover:shadow-xl text-center font-bold text-white"
                >
                  <p className="mb-2">{reward.name}</p>
                  <p>{reward.count} available</p>
                  <button className="mt-2 w-full bg-green-500 py-2 rounded-full hover:bg-green-600 transition-colors">
                    Redeem
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
