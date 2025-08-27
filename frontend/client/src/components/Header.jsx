<<<<<<< HEAD
import { Link } from "react-router-dom";

const Header = () => {
  return (
    <header className="fixed w-full top-0 z-50 bg-[#02061780] backdrop-blur-md border-b border-white/5 p-5">
      <div className="max-w-6xl mx-auto flex justify-between items-center">
        <Link to="/" className="flex items-center gap-3 text-white text-2xl font-bold">
          <i className="fas fa-layer-group text-[#3b82f6] text-3xl"></i>
          <span>Nimo</span>
        </Link>
=======
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
>>>>>>> origin/main

        <nav className="hidden lg:block">
          <ul className="flex gap-8 text-gray-400 font-medium">
            <li><a href="#features" className="hover:text-[#3b82f6]">Features</a></li>
            <li><a href="#howitworks" className="hover:text-[#3b82f6]">How It Works</a></li>
<<<<<<< HEAD
            <li><a href="#community" className="hover:text-[#3b82f6]">Community</a></li>
          </ul>
        </nav>

        <div className="flex items-center gap-4">
          <Link 
            to="/auth" 
            className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg transition-colors"
          >
            Login
          </Link>
        </div>
=======
    
            <li><a href="#community" className="hover:text-[#3b82f6]">Community</a></li>
          </ul>
        </nav>
>>>>>>> origin/main
      </div>
    </header>
  );
};

<<<<<<< HEAD
export default Header;
=======
export default Header;
>>>>>>> origin/main
