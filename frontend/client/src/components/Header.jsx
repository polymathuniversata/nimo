const Header = ({ setIsModalOpen, setActiveTab }) => {
  const openModal = (tab) => {
    setActiveTab(tab);
    setIsModalOpen(true);
  };

  return (
    <header className="fixed w-full top-0 z-50 bg-[#02061780] backdrop-blur-md border-b border-white/5 p-5">
      <div className="max-w-6xl mx-auto flex justify-between items-center">
        <a href="#" className="flex items-center gap-3 text-white text-2xl font-bold">
          <i className="fas fa-layer-group text-[#3b82f6] text-3xl"></i>
          <span>Nimo</span>
        </a>

        <nav className="hidden lg:block">
          <ul className="flex gap-8 text-gray-400 font-medium">
            <li><a href="#features" className="hover:text-[#3b82f6]">Features</a></li>
            <li><a href="#howitworks" className="hover:text-[#3b82f6]">How It Works</a></li>
    
            <li><a href="#community" className="hover:text-[#3b82f6]">Community</a></li>
          </ul>
        </nav>
      </div>
    </header>
  );
};

export default Header;
