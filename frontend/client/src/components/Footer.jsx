const Footer = () => {
  return (
    <footer className="mt-24 border-t border-white/10 py-16 text-center px-5">
      <a href="#" className="flex items-center justify-center gap-3 text-white text-2xl font-bold mb-4">
        <i className="fas fa-layer-group text-[#3b82f6] text-3xl"></i>
        <span>Nimo</span>
      </a>
      <p className="text-gray-400 mb-6">
        Building the future of digital identity for young creators on the Base network.
      </p>
      <div className="flex justify-center gap-8 mb-6 flex-wrap">
        <a href="#" className="text-gray-400 hover:text-[#3b82f6]">Features</a>
        <a href="#" className="text-gray-400 hover:text-[#3b82f6]">How It Works</a>
        <a href="#" className="text-gray-400 hover:text-[#3b82f6]">Documentation</a>
        <a href="#" className="text-gray-400 hover:text-[#3b82f6]">Privacy Policy</a>
        <a href="#" className="text-gray-400 hover:text-[#3b82f6]">Terms of Service</a>
      </div>
      <div className="flex justify-center gap-5 mb-6">
        {["twitter", "discord", "telegram", "github"].map((s) => (
          <a key={s} href="#" className="text-gray-400 hover:text-[#3b82f6] text-xl">
            <i className={`fab fa-${s}`}></i>
          </a>
        ))}
      </div>
      <p className="text-gray-500 text-sm">&copy; {new Date().getFullYear()} Nimo. All rights reserved.</p>
    </footer>
  );
};

export default Footer;
