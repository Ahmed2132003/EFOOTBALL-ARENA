import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import useAuthStore from "../store/authStore";
import AvatarUpload from "../components/AvatarUpload";
import PasswordChangeForm from "../components/PasswordChangeForm";
import LoadingSpinner from "../components/LoadingSpinner";

const EditProfile = () => {
  const navigate = useNavigate();
  const { user, profile, fetchProfile, updateProfile, profileLoading } = useAuthStore();

  const [form, setForm] = useState({
    bio:           "",
    country:       "",
    favorite_team: "",
  });
  const [avatarFile, setAvatarFile] = useState(null);
  const [activeTab, setActiveTab]   = useState("profile");

  useEffect(() => {
    fetchProfile();
  }, []);

  useEffect(() => {
    if (profile) {
      setForm({
        bio:           profile.bio           || "",
        country:       profile.country       || "",
        favorite_team: profile.favorite_team || "",
      });
    }
  }, [profile]);

  const handleChange = (e) => {
    setForm((p) => ({ ...p, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const fd = new FormData();
    fd.append("bio",           form.bio);
    fd.append("country",       form.country);
    fd.append("favorite_team", form.favorite_team);
    if (avatarFile) fd.append("avatar", avatarFile);

    const result = await updateProfile(fd);
    if (result.success) {
      toast.success("Profile updated successfully! ✅");
      navigate(`/profile/${user?.username}`);
    } else {
      toast.error(result.error || "Failed to update profile.");
    }
  };

  const inputClass = "w-full bg-primary border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-accent focus:ring-2 focus:ring-accent/20 transition-all duration-200";

  return (
    <div className="min-h-[calc(100vh-64px)] bg-primary py-10">
      <div className="max-w-2xl mx-auto px-4">

        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <button
            onClick={() => navigate(-1)}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <h1 className="text-2xl font-black text-white">Edit Profile</h1>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6 bg-secondary border border-white/10 rounded-xl p-1">
          {[
            { key: "profile",  label: "Profile Info" },
            { key: "password", label: "Password" },
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`flex-1 py-2.5 rounded-lg text-sm font-semibold transition-all duration-200
                ${activeTab === tab.key
                  ? "bg-accent text-primary shadow-lg"
                  : "text-gray-400 hover:text-white"}`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {activeTab === "profile" && (
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Avatar Upload */}
            <div className="bg-secondary border border-white/10 rounded-2xl p-6">
              <h3 className="text-lg font-bold text-white mb-5">Profile Photo</h3>
              <AvatarUpload
                currentAvatar={profile?.avatar_url}
                username={user?.username}
                onFileSelect={setAvatarFile}
              />
            </div>

            {/* Profile Fields */}
            <div className="bg-secondary border border-white/10 rounded-2xl p-6">
              <h3 className="text-lg font-bold text-white mb-5">Profile Details</h3>
              <div className="space-y-4">

                {/* Username (read-only) */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1.5">
                    Username <span className="text-gray-500 text-xs">(cannot be changed)</span>
                  </label>
                  <input
                    type="text"
                    value={user?.username || ""}
                    disabled
                    className={`${inputClass} opacity-50 cursor-not-allowed`}
                  />
                </div>

                {/* Bio */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1.5">Bio</label>
                  <textarea
                    name="bio"
                    value={form.bio}
                    onChange={handleChange}
                    placeholder="Tell us about yourself..."
                    rows={3}
                    maxLength={300}
                    className={`${inputClass} resize-none`}
                  />
                  <p className="text-right text-xs text-gray-500 mt-1">{form.bio.length}/300</p>
                </div>

                {/* Country */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1.5">Country</label>
                  <input
                    type="text"
                    name="country"
                    value={form.country}
                    onChange={handleChange}
                    placeholder="e.g. Egypt, Saudi Arabia..."
                    className={inputClass}
                  />
                </div>

                {/* Favorite Team */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1.5">Favorite Team</label>
                  <input
                    type="text"
                    name="favorite_team"
                    value={form.favorite_team}
                    onChange={handleChange}
                    placeholder="e.g. Al Ahly, Barcelona..."
                    className={inputClass}
                  />
                </div>
              </div>
            </div>

            {/* Buttons */}
            <div className="flex gap-3">
              <button
                type="button"
                onClick={() => navigate(-1)}
                className="flex-1 bg-white/5 border border-white/10 text-white py-3 rounded-xl font-semibold hover:bg-white/10 transition-all duration-200"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={profileLoading}
                className="flex-1 bg-accent text-primary py-3 rounded-xl font-bold hover:bg-accent/90 transition-all duration-200 disabled:opacity-50 flex items-center justify-center gap-2 shadow-lg shadow-accent/20"
              >
                {profileLoading ? (
                  <><LoadingSpinner size="sm" color="white" /> Saving...</>
                ) : "Save Changes ✅"}
              </button>
            </div>
          </form>
        )}

        {activeTab === "password" && (
          <PasswordChangeForm />
        )}
      </div>
    </div>
  );
};

export default EditProfile;