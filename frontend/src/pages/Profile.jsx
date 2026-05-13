import { useEffect, useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { userAPI } from "../api/user.api";
import useAuthStore from "../store/authStore";
import StatsCard from "../components/StatsCard";

const RankColors = {
  Bronze:   { text: "text-orange-400",  bg: "bg-orange-400/10",  border: "border-orange-400/30",  glow: "shadow-orange-400/20" },
  Silver:   { text: "text-gray-300",    bg: "bg-gray-300/10",    border: "border-gray-300/30",    glow: "shadow-gray-300/20" },
  Gold:     { text: "text-yellow-400",  bg: "bg-yellow-400/10",  border: "border-yellow-400/30",  glow: "shadow-yellow-400/20" },
  Platinum: { text: "text-cyan-400",    bg: "bg-cyan-400/10",    border: "border-cyan-400/30",    glow: "shadow-cyan-400/20" },
  Diamond:  { text: "text-blue-400",    bg: "bg-blue-400/10",    border: "border-blue-400/30",    glow: "shadow-blue-400/20" },
  Legend:   { text: "text-purple-400",  bg: "bg-purple-400/10",  border: "border-purple-400/30",  glow: "shadow-purple-400/20" },
};

const RankIcons = {
  Bronze: "🥉", Silver: "🥈", Gold: "🥇",
  Platinum: "💎", Diamond: "💠", Legend: "👑",
};

const ProfileSkeleton = () => (
  <div className="max-w-4xl mx-auto px-4 py-10 animate-pulse">
    <div className="bg-secondary rounded-3xl p-8 mb-6">
      <div className="flex flex-col sm:flex-row gap-6 items-center sm:items-start">
        <div className="w-32 h-32 bg-white/10 rounded-2xl" />
        <div className="flex-1 space-y-3 text-center sm:text-left">
          <div className="h-8 bg-white/10 rounded-lg w-48 mx-auto sm:mx-0" />
          <div className="h-4 bg-white/10 rounded w-32 mx-auto sm:mx-0" />
          <div className="h-4 bg-white/10 rounded w-64 mx-auto sm:mx-0" />
        </div>
      </div>
    </div>
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {[...Array(4)].map((_, i) => (
        <div key={i} className="h-32 bg-secondary rounded-2xl" />
      ))}
    </div>
  </div>
);

const Profile = () => {
  const { username } = useParams();
  const { user }     = useAuthStore();
  const navigate     = useNavigate();

  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState(null);

  const isOwn = !username || username === user?.username;

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        let data;
        if (isOwn) {
          const { userAPI: api } = await import("../api/user.api");
          data = await api.getMyProfile();
          setProfile(data.profile || data);
        } else {
          data = await userAPI.getUserProfile(username);
          setProfile(data.profile || data);
        }
      } catch (err) {
        setError("Profile not found.");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [username, isOwn]);

  if (loading) return <ProfileSkeleton />;

  if (error) return (
    <div className="min-h-[calc(100vh-64px)] flex items-center justify-center">
      <div className="text-center">
        <div className="text-6xl mb-4">😔</div>
        <h2 className="text-2xl font-bold text-white mb-2">Profile Not Found</h2>
        <p className="text-gray-400 mb-6">{error}</p>
        <Link to="/" className="bg-accent text-primary px-6 py-3 rounded-xl font-bold hover:bg-accent/90 transition-colors">
          Go Home
        </Link>
      </div>
    </div>
  );

  const rank    = profile?.rank_level || "Bronze";
  const rankCol = RankColors[rank] || RankColors.Bronze;
  const joined  = profile?.date_joined
    ? new Date(profile.date_joined).toLocaleDateString("en-US", { year: "numeric", month: "long" })
    : "—";

  return (
    <div className="min-h-[calc(100vh-64px)] bg-primary py-10">
      <div className="max-w-4xl mx-auto px-4">

        {/* Profile Header Card */}
        <div className={`bg-secondary border ${rankCol.border} rounded-3xl p-8 mb-6 shadow-2xl ${rankCol.glow}`}>
          <div className="flex flex-col sm:flex-row gap-6 items-center sm:items-start">
            {/* Avatar */}
            <div className={`relative w-32 h-32 rounded-2xl overflow-hidden border-2 ${rankCol.border} shadow-xl flex-shrink-0`}>
              {profile?.avatar_url ? (
                <img src={profile.avatar_url} alt={profile.username} className="w-full h-full object-cover" />
              ) : (
                <div className={`w-full h-full ${rankCol.bg} flex items-center justify-center`}>
                  <span className={`font-black text-5xl ${rankCol.text}`}>
                    {profile?.username?.charAt(0)?.toUpperCase()}
                  </span>
                </div>
              )}
              {/* Rank Badge */}
              <div className="absolute -bottom-2 -right-2 text-2xl">{RankIcons[rank]}</div>
            </div>

            {/* Info */}
            <div className="flex-1 text-center sm:text-left">
              <div className="flex flex-col sm:flex-row sm:items-center gap-3 mb-2">
                <h1 className="text-3xl font-black text-white">{profile?.username}</h1>
                <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm font-bold ${rankCol.bg} ${rankCol.text} border ${rankCol.border}`}>
                  {RankIcons[rank]} {rank}
                </span>
              </div>

              {/* Rating */}
              <div className="flex items-center gap-2 justify-center sm:justify-start mb-3">
                <span className="text-accent font-black text-2xl">{profile?.rating?.toFixed(0) || 1000}</span>
                <span className="text-gray-400 text-sm">Rating Points</span>
              </div>

              {/* Meta */}
              <div className="flex flex-wrap gap-3 justify-center sm:justify-start text-sm text-gray-400 mb-4">
                {profile?.country && (
                  <span className="flex items-center gap-1">🌍 {profile.country}</span>
                )}
                {profile?.favorite_team && (
                  <span className="flex items-center gap-1">⚽ {profile.favorite_team}</span>
                )}
                <span className="flex items-center gap-1">📅 Joined {joined}</span>
              </div>

              {/* Bio */}
              {profile?.bio && (
                <p className="text-gray-300 text-sm leading-relaxed max-w-md mx-auto sm:mx-0 mb-4">
                  {profile.bio}
                </p>
              )}

              {/* Edit Button (owner only) */}
              {isOwn && (
                <button
                  onClick={() => navigate("/profile/edit")}
                  className="inline-flex items-center gap-2 bg-accent text-primary px-5 py-2.5 rounded-xl font-bold hover:bg-accent/90 transition-all duration-200 shadow-lg shadow-accent/20"
                >
                  ✏️ Edit Profile
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <StatsCard icon="⚽" label="Matches"  value={profile?.matches_played || 0} />
          <StatsCard icon="🏆" label="Wins"     value={profile?.wins || 0}           color="success" />
          <StatsCard icon="❌" label="Losses"   value={profile?.losses || 0}         color="danger" />
          <StatsCard
            icon="📊"
            label="Win Rate"
            value={`${profile?.win_rate || 0}%`}
            color={profile?.win_rate >= 50 ? "success" : "danger"}
          />
        </div>

        {/* Additional Info */}
        <div className="bg-secondary border border-white/10 rounded-2xl p-6">
          <h2 className="text-lg font-bold text-white mb-4">Player Info</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {[
              { label: "Username",      value: profile?.username },
              { label: "Rank",          value: `${RankIcons[rank]} ${rank}` },
              { label: "Rating",        value: `${profile?.rating?.toFixed(0) || 1000} pts` },
              { label: "Country",       value: profile?.country || "Not specified" },
              { label: "Favorite Team", value: profile?.favorite_team || "Not specified" },
              { label: "Member Since",  value: joined },
            ].map((item) => (
              <div key={item.label} className="flex justify-between items-center bg-primary/50 rounded-xl px-4 py-3">
                <span className="text-gray-400 text-sm">{item.label}</span>
                <span className="text-white font-semibold text-sm">{item.value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;