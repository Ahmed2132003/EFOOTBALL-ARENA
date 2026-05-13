import { useState } from "react";
import toast from "react-hot-toast";
import useAuthStore from "../store/authStore";
import LoadingSpinner from "./LoadingSpinner";

const PasswordChangeForm = () => {
  const { changePassword, passwordLoading } = useAuthStore();
  const [form, setForm] = useState({
    current_password: "",
    new_password:     "",
    confirm_password: "",
  });
  const [errors, setErrors]         = useState({});
  const [showPasswords, setShowPasswords] = useState({
    current: false, new: false, confirm: false,
  });

  const validate = () => {
    const errs = {};
    if (!form.current_password) errs.current_password = "Current password is required.";
    if (!form.new_password)     errs.new_password = "New password is required.";
    else if (form.new_password.length < 8) errs.new_password = "Min 8 characters.";
    if (form.new_password !== form.confirm_password)
      errs.confirm_password = "Passwords do not match.";
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleChange = (e) => {
    setForm((p) => ({ ...p, [e.target.name]: e.target.value }));
    if (errors[e.target.name]) setErrors((p) => ({ ...p, [e.target.name]: "" }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;
    const result = await changePassword(form);
    if (result.success) {
      toast.success("Password changed successfully! Please log in again.");
      setForm({ current_password: "", new_password: "", confirm_password: "" });
    } else {
      toast.error(result.error || "Failed to change password.");
    }
  };

  const toggleShow = (field) =>
    setShowPasswords((p) => ({ ...p, [field]: !p[field] }));

  const inputClass = (field) =>
    `w-full bg-primary border rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 transition-all duration-200 pr-12
    ${errors[field] ? "border-danger focus:ring-danger/30" : "border-white/10 focus:border-accent focus:ring-accent/20"}`;

  const EyeIcon = ({ show }) => show ? (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
    </svg>
  ) : (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
    </svg>
  );

  return (
    <div className="bg-secondary border border-white/10 rounded-2xl p-6">
      <h3 className="text-lg font-bold text-white mb-5 flex items-center gap-2">
        🔐 Change Password
      </h3>
      <form onSubmit={handleSubmit} className="space-y-4" noValidate>
        {[
          { key: "current_password", label: "Current Password",  show: "current" },
          { key: "new_password",     label: "New Password",      show: "new" },
          { key: "confirm_password", label: "Confirm Password",  show: "confirm" },
        ].map(({ key, label, show }) => (
          <div key={key}>
            <label className="block text-sm font-medium text-gray-300 mb-1.5">{label}</label>
            <div className="relative">
              <input
                type={showPasswords[show] ? "text" : "password"}
                name={key}
                value={form[key]}
                onChange={handleChange}
                placeholder="••••••••"
                disabled={passwordLoading}
                className={inputClass(key)}
              />
              <button
                type="button"
                onClick={() => toggleShow(show)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-200 transition-colors"
                tabIndex={-1}
              >
                <EyeIcon show={showPasswords[show]} />
              </button>
            </div>
            {errors[key] && (
              <p className="mt-1 text-xs text-danger flex items-center gap-1">
                <span>⚠</span> {errors[key]}
              </p>
            )}
          </div>
        ))}

        <button
          type="submit"
          disabled={passwordLoading}
          className="w-full bg-accent text-primary py-3 rounded-xl font-bold hover:bg-accent/90 transition-all duration-200 disabled:opacity-50 flex items-center justify-center gap-2 mt-2"
        >
          {passwordLoading ? (
            <><LoadingSpinner size="sm" color="white" /> Changing...</>
          ) : "Change Password"}
        </button>
      </form>
    </div>
  );
};

export default PasswordChangeForm;