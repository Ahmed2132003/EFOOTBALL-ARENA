import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import useAuthStore from "../store/authStore";
import LoadingSpinner from "../components/LoadingSpinner";

const StatCard = ({ icon, label, value, color = "accent" }) => (
  <div className="bg-secondary border border-white/10 rounded-2xl p-5 hover:border-accent/30 transition-all duration-300">
    <div className="flex items-center justify-between mb-3">
      <span className="text-2xl">{icon}</span>
      <span className={`text-xs font-medium px-2 py-1 rounded-full bg-${color}/10 text-${color} border border-${color}/20`}>
        Active
      </span>
    </div>
    <div className="text-2xl font-black text-white mb-1">{value}</div>
    <div className="text-gray-400 text-sm">{label}</div>
  </div>
);

const Dashboard = () => {
  const navigate = useNavigate();
  const { user, logout, loading } = useAuthStore();

  const handleLogout = async () => {
    await logout();
    toast.success("تم تسجيل الخروج بنجاح");
    navigate("/login");
  };

  const getRankColor = (rank) => {
    const colors = {
      Bronze: "text-orange-400",
      Silver: "text-gray-300",
      Gold: "text-yellow-400",
      Platinum: "text-cyan-400",
      Diamond: "text-blue-400",
      Legend: "text-purple-400",
    };
    return colors[rank] || "text-accent";
  };

  const getRankIcon = (rank) => {
    const icons = {
      Bronze: "🥉",
      Silver: "🥈",
      Gold: "🥇",
      Platinum: "💎",
      Diamond: "💠",
      Legend: "👑",
    };
    return icons[rank] || "⭐";
  };

  return (
    <div className="min-h-[calc(100vh-64px)] bg-primary">
      <div className="max-w-6xl mx-auto px-4 py-10">

        {/* Welcome Header */}
        <div className="mb-10">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div className="flex items-center gap-4">
              {/* Avatar */}
              <div className="w-16 h-16 bg-accent rounded-2xl flex items-center justify-center shadow-lg shadow-accent/20 flex-shrink-0">
                <span className="text-primary font-black text-2xl">
                  {user?.username?.charAt(0)?.toUpperCase() || "?"}
                </span>
              </div>

              <div>
                <p className="text-gray-400 text-sm mb-1">مرحباً بعودتك 👋</p>
                <h1 className="text-2xl md:text-3xl font-black text-white">
                  {user?.username || "Champion"}
                </h1>
                <div className="flex items-center gap-2 mt-1">
                  <span className="text-lg">{getRankIcon(user?.rank_level)}</span>
                  <span className={`text-sm font-semibold ${getRankColor(user?.rank_level)}`}>
                    {user?.rank_level || "Bronze"}
                  </span>
                </div>
              </div>
            </div>

            <button
              onClick={handleLogout}
              disabled={loading}
              className="flex items-center gap-2 bg-danger/10 text-danger border border-danger/30 px-5 py-2.5 rounded-xl font-medium hover:bg-danger hover:text-white transition-all duration-200 disabled:opacity-50 self-start sm:self-center"
            >
              {loading ? (
                <LoadingSpinner size="sm" color="danger" />
              ) : (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
              )}
              تسجيل الخروج
            </button>
          </div>
        </div>

        {/* User Info Card */}
        <div className="bg-secondary border border-accent/20 rounded-2xl p-6 mb-8">
          <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
            <span>👤</span> معلومات الحساب
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {[
              { label: "اسم المستخدم", value: user?.username || "—" },
              { label: "البريد الإلكتروني", value: user?.email || "—" },
              { label: "الدولة", value: user?.country || "غير محدد" },
              { label: "التقييم", value: user?.rating ? `${user.rating} pts` : "1000 pts" },
              { label: "المستوى", value: user?.rank_level || "Bronze" },
              { label: "موثق", value: user?.is_verified ? "✅ نعم" : "❌ لا" },
            ].map((item) => (
              <div key={item.label} className="bg-primary/50 rounded-xl p-4">
                <p className="text-gray-400 text-xs mb-1">{item.label}</p>
                <p className="text-white font-semibold text-sm truncate">{item.value}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <StatCard icon="⚽" label="المباريات" value="0" />
          <StatCard icon="🏆" label="البطولات" value="0" />
          <StatCard icon="💰" label="الصفقات" value="0" />
          <StatCard icon="📋" label="التكتيكات" value="0" />
        </div>

        {/* Quick Actions */}
        <div className="bg-secondary border border-white/10 rounded-2xl p-6">
          <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
            <span>⚡</span> إجراءات سريعة
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {[
              { icon: "🏆", label: "انضم لبطولة", desc: "قريباً" },
              { icon: "📋", label: "إنشاء تكتيك", desc: "قريباً" },
              { icon: "💰", label: "تصفح السوق", desc: "قريباً" },
            ].map((action) => (
              <button
                key={action.label}
                onClick={() => toast(`${action.label} — قريباً! 🔜`, { icon: "⚡" })}
                className="flex items-center gap-3 bg-primary/50 border border-white/10 hover:border-accent/30 hover:bg-primary rounded-xl p-4 transition-all duration-200 text-left group"
              >
                <span className="text-2xl">{action.icon}</span>
                <div>
                  <p className="text-white font-medium text-sm group-hover:text-accent transition-colors">
                    {action.label}
                  </p>
                  <p className="text-gray-500 text-xs">{action.desc}</p>
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;