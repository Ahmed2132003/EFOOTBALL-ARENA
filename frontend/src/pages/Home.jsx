import { Link } from "react-router-dom";
import useAuthStore from "../store/authStore";

const Home = () => {
  const { isAuthenticated, user } = useAuthStore();

  return (
    <div className="min-h-[calc(100vh-64px)] flex flex-col">

      {/* Hero Section */}
      <section className="flex-1 flex items-center justify-center px-4 py-20">
        <div className="max-w-4xl mx-auto text-center">

          {/* Badge */}
          <div className="inline-flex items-center gap-2 bg-accent/10 border border-accent/30 px-4 py-2 rounded-full mb-8">
            <div className="w-2 h-2 bg-accent rounded-full animate-pulse"></div>
            <span className="text-accent text-sm font-medium">
              The Ultimate eFootball Platform
            </span>
          </div>

          {/* Title */}
          <h1 className="text-5xl md:text-7xl font-black text-white mb-6 leading-tight">
            eFootball{" "}
            <span className="text-accent">Arena</span>
          </h1>

          {/* Subtitle */}
          <p className="text-gray-400 text-xl md:text-2xl mb-4 max-w-2xl mx-auto leading-relaxed">
            منصة كرة القدم الإلكترونية الأولى
          </p>
          <p className="text-gray-500 text-lg mb-12 max-w-xl mx-auto">
            انضم إلى آلاف اللاعبين، شارك في البطولات، وتداول في السوق.
          </p>

          {/* CTA Buttons */}
          {isAuthenticated ? (
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/dashboard"
                className="bg-accent text-primary px-8 py-4 rounded-xl font-bold text-lg hover:bg-accent/90 transition-all duration-200 shadow-lg shadow-accent/20"
              >
                Go to Dashboard →
              </Link>
              <div className="flex items-center justify-center gap-2 bg-secondary border border-accent/20 px-6 py-4 rounded-xl">
                <div className="w-8 h-8 bg-accent rounded-full flex items-center justify-center">
                  <span className="text-primary font-bold text-sm">
                    {user?.username?.charAt(0)?.toUpperCase() || "U"}
                  </span>
                </div>
                <span className="text-white font-medium">
                  Welcome, {user?.username || "Player"}!
                </span>
              </div>
            </div>
          ) : (
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/register"
                className="bg-accent text-primary px-8 py-4 rounded-xl font-bold text-lg hover:bg-accent/90 transition-all duration-200 shadow-lg shadow-accent/20"
              >
                Join Now — It's Free
              </Link>
              <Link
                to="/login"
                className="bg-transparent text-white border border-white/20 px-8 py-4 rounded-xl font-bold text-lg hover:border-accent hover:text-accent transition-all duration-200"
              >
                Sign In
              </Link>
            </div>
          )}
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4 bg-secondary/50">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-bold text-center text-white mb-12">
            Everything You Need
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                icon: "⚽",
                title: "Tournaments",
                description: "شارك في بطولات حصرية وتنافس مع أفضل اللاعبين",
              },
              {
                icon: "🏆",
                title: "Tactics",
                description: "شارك وتعلم أفضل التكتيكات من المجتمع",
              },
              {
                icon: "💰",
                title: "Marketplace",
                description: "تداول وبيع أفضل اللاعبين في السوق",
              },
            ].map((feature) => (
              <div
                key={feature.title}
                className="bg-primary border border-accent/10 p-6 rounded-2xl hover:border-accent/30 transition-all duration-300 group"
              >
                <div className="text-4xl mb-4">{feature.icon}</div>
                <h3 className="text-white font-bold text-xl mb-2 group-hover:text-accent transition-colors">
                  {feature.title}
                </h3>
                <p className="text-gray-400 leading-relaxed">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;