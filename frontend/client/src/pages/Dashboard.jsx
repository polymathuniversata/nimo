import React from "react";

const mockBadges = [
  { id: 1, name: "Volunteering Badge", redeemable: true },
  { id: 2, name: "Project Contributor", redeemable: false },
  { id: 3, name: "Event Attendee", redeemable: true },
];

const Dashboard = ({ user, walletConnected, onConnectWallet }) => {
  return (
    <div className="p-6 bg-[#020617] text-white min-h-screen font-inter">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Welcome, {user.name}!</h1>
        {!walletConnected ? (
          <button
            onClick={onConnectWallet}
            className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded"
          >
            Connect Wallet
          </button>
        ) : (
          <span className="text-green-400 font-semibold">Wallet Connected ✅</span>
        )}
      </div>

      <h2 className="text-xl font-semibold mb-4">Your Badges / NFTs</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {mockBadges.map((badge) => (
          <div
            key={badge.id}
            className="bg-gray-800 p-4 rounded-lg flex flex-col justify-between"
          >
            <span className="font-semibold">{badge.name}</span>
            {badge.redeemable ? (
              <div className="mt-2 flex gap-2">
                <button className="bg-blue-500 px-2 py-1 rounded text-sm hover:bg-blue-600">
                  Redeem Internship
                </button>
                <button className="bg-green-500 px-2 py-1 rounded text-sm hover:bg-green-600">
                  Redeem Cash
                </button>
                <button className="bg-yellow-500 px-2 py-1 rounded text-sm hover:bg-yellow-600">
                  Redeem Scholarship
                </button>
              </div>
            ) : (
              <span className="text-gray-400 mt-2 text-sm">Not redeemable yet</span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default Dashboard;
