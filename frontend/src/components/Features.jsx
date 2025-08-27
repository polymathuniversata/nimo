import React from "react";

const Features = () => {
  const features = [
    {
      title: "NFT Identity",
      desc: "Create a unique, verifiable digital identity as an NFT on the Base network.",
      icon: (
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="w-8 h-8 text-white"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={2}
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M12 11c0-1.104.896-2 2-2h4v4h-4c-1.104 0-2-.896-2-2zM6 6v12h12"
          />
        </svg>
      ),
      gradient: "from-blue-500 to-purple-500",
    },
    {
      title: "Reputation System",
      desc: "Earn reputation tokens for your contributions and achievements.",
      icon: (
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="w-8 h-8 text-white"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={2}
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M12 2l3 7h7l-5.5 4.5L18 21l-6-4-6 4 2.5-7.5L2 9h7l3-7z"
          />
        </svg>
      ),
      gradient: "from-yellow-400 to-orange-500",
    },
    {
      title: "Community Verification",
      desc: "Get your skills verified by trusted community members.",
      icon: (
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="w-8 h-8 text-white"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={2}
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M5 13l4 4L19 7"
          />
        </svg>
      ),
      gradient: "from-green-400 to-teal-500",
    },
  ];

  return (
    <section className="py-20 px-5 bg-[#020617]">
      <div className="max-w-6xl mx-auto">
        <h2 className="text-4xl font-bold text-center mb-16 text-white">
          Powerful Features
        </h2>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((f, idx) => (
            <div
              key={idx}
              className="relative p-8 rounded-2xl bg-[#1e293b] border border-white/10 backdrop-blur-xl shadow-lg hover:scale-105 transform transition duration-300 text-center"
            >
              {/* Icon Circle */}
              <div
                className={`w-16 h-16 mx-auto rounded-full flex items-center justify-center text-white text-2xl mb-4 bg-gradient-to-r ${f.gradient}`}
              >
                {f.icon}
              </div>

              <h3 className="text-xl font-semibold mb-2 text-white">{f.title}</h3>
              <p className="text-gray-300 text-sm">{f.desc}</p>

              {/* Accent glows */}
              <div className="absolute -top-4 -right-4 w-6 h-6 rounded-full bg-gradient-to-r from-pink-500 to-purple-500 blur-xl opacity-50"></div>
              <div className="absolute -bottom-4 -left-4 w-6 h-6 rounded-full bg-gradient-to-r from-blue-400 to-green-400 blur-xl opacity-50"></div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Features;
