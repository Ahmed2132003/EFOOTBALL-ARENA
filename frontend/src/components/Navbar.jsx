import { useState, useRef, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import useAuthStore from "../store/authStore";

const Navbar = () => {
  const [menuOpen,    setMenuOpen]    = useState(false);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const { isAuthenticated, user, logout, loading } = useAuthStore();
  const navigate   = useNavigate();
  const dropdownRef = useRef(null);

  const handleLogout = async () => {
    setDropdownOpen(false);
    await logout();
    navigate("/login");
  };

  // Close dropdown on outside click
  useEffect(() => {
    const handler = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target))
        setDropdownOpen(false);
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const avatarSrc  = user?.avatar;
  const initials   = user?.username?.charAt(0)?.toUpperCase() || "U";

  const AvatarCircle = ({ size = "sm" }) => {
    const dim = size === "sm" ? "w-8 h-8 text-xs" : "w-10 h-10 text-sm";
    return avatarSrc ? (
      <img src={avatarSrc} alt="avatar"
        className={`${dim} rounded-full object-cover border border-accent/40`} />
    ) : (
      <div className={`${dim} bg-accent rounded-full flex items-center justify-center font-bold text-primary`}>
        {initials}
      </div>
    );
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

          {/* Desktop */}
          <div className="hidden md:flex items-center gap-6">
            <Link to="/" className="text-gray-300 hover:text-accent transition-colors font-medium">Home</Link>

            {!isAuthenticated ? (
              <>
                <Link to="/login" className="text-gray-300 hover:text-accent transition-colors font-medium">Login</Link>
                <Link to="/register" className="bg-accent text-primary px-4 py-2 rounded-lg font-semibold hover:bg-accent/90 transition-colors">Register</Link>
              </>
            ) : (
              <div className="flex items-center gap-4">
                <Link to="/dashboard" className="text-gray-300 hover:text-accent transition-colors font-medium">Dashboard</Link>

                {/* User Dropdown */}
                <div className="relative" ref={dropdownRef}>
                  <button
                    onClick={() => setDropdownOpen(!dropdownOpen)}
                    className="flex items-center gap-2 bg-primary/50 px-3 py-1.5 rounded-xl border border-accent/20 hover:border-accent/50 transition-all duration-200"
                  >
                    <AvatarCircle size="sm" />
                    <span className="text-white text-sm font-medium">{user?.username || "User"}</span>
                    <svg className={`w-4 h-4 text-gray-400 transition-transform duration-200 ${dropdownOpen ? "rotate-180" : ""}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>

                  {dropdownOpen && (
                    <div className="absolute right-0 mt-2 w-52 bg-secondary border border-white/10 rounded-2xl shadow-2xl overflow-hidden z-50">
                      <div className="px-4 py-3 border-b border-white/10">
                        <p className="text-white font-semibold text-sm">{user?.username}</p>
                        <p className="text-gray-400 text-xs truncate">{user?.email}</p>
                      </div>
                      {[
                        { label: "My Profile",  icon: "👤", to: `/profile/${user?.username}` },
                        { label: "Dashboard",   icon: "📊", to: "/dashboard" },
                        { label: "Edit Profile",icon: "✏️", to: "/profile/edit" },
                      ].map((item) => (
                        <Link
                          key={item.label}
                          to={item.to}
                          onClick={() => setDropdownOpen(false)}
                          className="flex items-center gap-3 px-4 py-3 text-gray-300 hover:bg-white/5 hover:text-white transition-colors text-sm"
                        >
                          <span>{item.icon}</span> {item.label}
                        </Link>
                      ))}
                      <div className="border-t border-white/10">
                        <button
                          onClick={handleLogout}
                          disabled={loading}
                          className="w-full flex items-center gap-3 px-4 py-3 text-danger hover:bg-danger/10 transition-colors text-sm disabled:opacity-50"
                        >
                          <span>🚪</span> {loading ? "Logging out..." : "Logout"}
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Mobile Toggle */}
          <button className="md:hidden text-gray-300 hover:text-accent" onClick={() => setMenuOpen(!menuOpen)}>
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              {menuOpen
                ? <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                : <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />}
            </svg>
          </button>
        </div>

        {/* Mobile Menu */}
        {menuOpen && (
          <div className="md:hidden pb-4 pt-2 border-t border-accent/10 mt-2 space-y-2">
            <Link to="/" className="block text-gray-300 hover:text-accent px-2 py-2 font-medium" onClick={() => setMenuOpen(false)}>Home</Link>
            {!isAuthenticated ? (
              <>
                <Link to="/login"    className="block text-gray-300 hover:text-accent px-2 py-2" onClick={() => setMenuOpen(false)}>Login</Link>
                <Link to="/register" className="block bg-accent text-primary px-4 py-2 rounded-lg font-semibold text-center" onClick={() => setMenuOpen(false)}>Register</Link>
              </>
            ) : (
              <>
                <div className="flex items-center gap-3 px-2 py-2">
                  <AvatarCircle size="md" />
                  <div>
                    <p className="text-white font-semibold text-sm">{user?.username}</p>
                    <p className="text-gray-400 text-xs">{user?.rank_level}</p>
                  </div>
                </div>
                {[
                  { label: "My Profile",   to: `/profile/${user?.username}` },
                  { label: "Dashboard",    to: "/dashboard" },
                  { label: "Edit Profile", to: "/profile/edit" },
                ].map((item) => (
                  <Link key={item.label} to={item.to} className="block text-gray-300 hover:text-accent px-2 py-2 text-sm" onClick={() => setMenuOpen(false)}>
                    {item.label}
                  </Link>
                ))}
                <button
                  onClick={() => { handleLogout(); setMenuOpen(false); }}
                  className="w-full text-left text-danger px-2 py-2 text-sm hover:bg-danger/10 rounded-lg transition-colors"
                >
                  Logout
                </button>
              </>
            )}
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;