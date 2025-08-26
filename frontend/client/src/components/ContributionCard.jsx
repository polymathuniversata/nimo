const Stats = () => {
  const stats = [
    { label: "Users", value: "12k+" },
    { label: "NFTs Earned", value: "1.2k+" },
    { label: "Bond Offers", value: "350+" },
    { label: "Rewards Redeemed", value: "500+" },
  ];

  return (
    <section className="max-w-6xl mx-auto px-5 mt-20 grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
      {stats.map((s, i) => (
        <div key={i}>
          <h3 className="text-3xl font-bold text-white">{s.value}</h3>
          <p className="text-gray-400 mt-2">{s.label}</p>
        </div>
      ))}
    </section>
  );
};

export default Stats;
