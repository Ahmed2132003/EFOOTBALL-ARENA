import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import useAuthStore from "../store/authStore";

const Navbar = () => {
  const [menuOpen, setMenuOpen] = useState(false);
  const { isAuthenticated, user, logout, loading } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  return (
    <nav className="bg-secondary border-b border-accent/20 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">

          {/* Logo */}
          <Link to="/" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-accent rounded-full flex items-center justify-center">
              <span className="text-primary font-black text-sm">eF</span>
            </div>
            <span className="text-white font-bold text-lg tracking-wide">
              eFootball <span className="text-accent">Arena</span>
            </span>
          </Link>

          {/* Desktop Nav */}
          <div className="hidden md:flex items-center gap-6">
            <Link
              to="/"
              className="text-gray-300 hover:text-accent transition-colors duration-200 font-medium"
            >
              Home
            </Link>

            {!isAuthenticated ? (
              <>
                <Link
                  to="/login"
                  className="text-gray-300 hover:text-accent transition-colors duration-200 font-medium"
                >
                  Login
                </Link>
                <Link
                  to="/register"
                  className="bg-accent text-primary px-4 py-2 rounded-lg font-semibold hover:bg-accent/90 transition-colors duration-200"
                >
                  Register
                </Link>
              </>
            ) : (
              <div className="flex items-center gap-4">
                <Link
                  to="/dashboard"
                  className="text-gray-300 hover:text-accent transition-colors duration-200 font-medium"
                >
                  Dashboard
                </Link>
                <div className="flex items-center gap-2 bg-primary/50 px-3 py-1.5 rounded-lg border border-accent/20">
                  <div className="w-6 h-6 bg-accent rounded-full flex items-center justify-center">
                    <span className="text-primary font-bold text-xs">
                      {user?.username?.charAt(0)?.toUpperCase() || "U"}
                    </span>
                  </div>
                  <span className="text-white text-sm font-medium">
                    {user?.username || "User"}
                  </span>
                </div>
                <button
                  onClick={handleLogout}
                  disabled={loading}
                  className="bg-danger/10 text-danger border border-danger/30 px-4 py-2 rounded-lg font-medium hover:bg-danger hover:text-white transition-all duration-200 disabled:opacity-50"
                >
                  {loading ? "..." : "Logout"}
                </button>
              </div>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button
            className="md:hidden text-gray-300 hover:text-accent focus:outline-none"
            onClick={() => setMenuOpen(!menuOpen)}
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              {menuOpen ? (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>
        </div>

        {/* Mobile Menu */}
        {menuOpen && (
          <div className="md:hidden pb-4 pt-2 border-t border-accent/10 mt-2">
            <div className="flex flex-col gap-3">
              <Link
                to="/"
                className="text-gray-300 hover:text-accent transition-colors duration-200 font-medium px-2 py-1"
                onClick={() => setMenuOpen(false)}
              >
                Home
              </Link>

              {!isAuthenticated ? (
                <>
                  <Link
                    to="/login"
                    className="text-gray-300 hover:text-accent transition-colors duration-200 font-medium px-2 py-1"
                    onClick={() => setMenuOpen(false)}
                  >
                    Login
                  </Link>
                  <Link
                    to="/register"
                    className="bg-accent text-primary px-4 py-2 rounded-lg font-semibold hover:bg-accent/90 transition-colors duration-200 text-center"
                    onClick={() => setMenuOpen(false)}
                  >
                    Register
                  </Link>
                </>
              ) : (
                <>
                  <div className="flex items-center gap-2 px-2 py-1">
                    <div className="w-6 h-6 bg-accent rounded-full flex items-center justify-center">
                      <span className="text-primary font-bold text-xs">
                        {user?.username?.charAt(0)?.toUpperCase() || "U"}
                      </span>
                    </div>
                    <span className="text-white text-sm font-medium">
                      {user?.username || "User"}
                    </span>
                  </div>
                  <Link
                    to="/dashboard"
                    className="text-gray-300 hover:text-accent transition-colors duration-200 font-medium px-2 py-1"
                    onClick={() => setMenuOpen(false)}
                  >
                    Dashboard
                  </Link>
                  <button
                    onClick={() => { handleLogout(); setMenuOpen(false); }}
                    disabled={loading}
                    className="bg-danger/10 text-danger border border-danger/30 px-4 py-2 rounded-lg font-medium hover:bg-danger hover:text-white transition-all duration-200 text-left disabled:opacity-50"
                  >
                    {loading ? "Logging out..." : "Logout"}
                  </button>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;