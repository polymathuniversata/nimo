import { useNavigate } from "react-router-dom";

const Hero = () => {
  const navigate = useNavigate();

  return (
    <section className="pt-32 pb-20 px-4 relative overflow-hidden">
      {/* Background effects */}
      <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 to-purple-500/10"></div>
      
      <div className="container mx-auto relative z-10">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-5xl md:text-6xl font-bold mb-6 gradient-text">
            Build Your Digital Identity on Base
          </h1>
          <p className="text-xl text-gray-300 mb-10 max-w-2xl mx-auto">
            Nimo empowers young creators to build verified digital identities, earn reputation tokens for contributions, 
            and access global opportunities through the Base network.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button 
              onClick={() => navigate("/auth")}
              className="px-8 py-4 bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-semibold transition-all transform hover:-translate-y-1"
            >
              Get Started
            </button>
            <button className="px-8 py-4 border border-blue-400 text-blue-400 hover:bg-blue-400/10 rounded-lg font-semibold transition-colors">
              Learn More
            </button>
          </div>
        </div>

        {/* Stats preview */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-20 max-w-4xl mx-auto">
          {['1.2K+ Creators', '5.4K+ Contributions', '850K Reputation', '320+ Opportunities'].map((stat, index) => (
            <div key={index} className="glass-card rounded-xl p-6 text-center">
              <div className="text-2xl font-bold text-white mb-2">{stat.split(' ')[0]}</div>
              <div className="text-gray-400">{stat.split(' ')[1]}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Hero;
