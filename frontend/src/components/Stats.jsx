const Stats = () => {
  const steps = [
    {
      title: "Join the Platform",
      description: "Sign up and create your account to start contributing.",
      color: "from-[#6366f1] to-[#3b82f6]",
    },
    {
      title: "Earn Reputation",
      description: "Participate in projects and activities to earn points and badges.",
      color: "from-[#f59e0b] to-[#fbbf24]",
    },
    {
      title: "Redeem Rewards",
      description: "Use your badges and points to unlock internships, scholarships, or cash rewards.",
      color: "from-[#10b981] to-[#34d399]",
    },
    {
      title: "Connect Wallet",
      description: "Link your wallet to manage NFTs and claim rewards seamlessly.",
      color: "from-[#ec4899] to-[#f472b6]",
    },
  ];

  return (
    <section className="max-w-6xl mx-auto px-5 mt-24">
      {/* Section title */}
      <h2 className="text-4xl font-bold text-center text-white mb-12">
        How It Works
      </h2>

      {/* Cards grid */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-8">
        {steps.map((step, i) => (
          <div
            key={i}
            className="relative p-8 rounded-xl bg-gradient-to-br from-white/5 to-white/10 border border-white/20 backdrop-blur-xl shadow-lg hover:scale-105 transform transition duration-300"
          >
            {/* Step number */}
            <div
              className={`text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r ${step.color}`}
            >
              Step {i + 1}
            </div>

            {/* Step title */}
            <div className="text-xl font-semibold mt-4">{step.title}</div>

            {/* Step description */}
            <p className="text-gray-300 mt-2 text-sm">{step.description}</p>

            {/* Optional accent glow */}
            <div className="absolute -top-4 -right-4 w-6 h-6 rounded-full bg-gradient-to-r from-pink-500 to-purple-500 blur-xl opacity-50"></div>
            <div className="absolute -bottom-4 -left-4 w-6 h-6 rounded-full bg-gradient-to-r from-blue-400 to-green-400 blur-xl opacity-50"></div>
          </div>
        ))}
      </div>
    </section>
  );
};

export default Stats;
