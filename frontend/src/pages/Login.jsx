import { useState, useEffect, useRef } from "react";
import { Link } from "react-router-dom";
import toast from "react-hot-toast";
import useAuth from "../hooks/useAuth";
import AuthLayout from "../components/AuthLayout";
import GoogleButton from "../components/GoogleButton";
import LoadingSpinner from "../components/LoadingSpinner";

const Login = () => {
  const { login, loading, error, clearError } = useAuth();
  const usernameRef = useRef(null);

  const [formData, setFormData] = useState({
    username: "",
    password: "",
    rememberMe: false,
  });

  const [fieldErrors, setFieldErrors] = useState({});
  const [showPassword, setShowPassword] = useState(false);

  useEffect(() => {
    usernameRef.current?.focus();
  }, []);

  useEffect(() => {
    if (error) {
      toast.error(error);
      clearError();
    }
  }, [error, clearError]);

  const validateForm = () => {
    const errors = {};

    if (!formData.username.trim()) {
      errors.username = "اسم المستخدم أو البريد الإلكتروني مطلوب";
    } else if (
      !formData.username.includes("@") &&
      formData.username.trim().length < 3
    ) {
      errors.username = "اسم المستخدم يجب أن يكون 3 أحرف على الأقل";
    }

    if (!formData.password) {
      errors.password = "كلمة المرور مطلوبة";
    } else if (formData.password.length < 6) {
      errors.password = "كلمة المرور يجب أن تكون 6 أحرف على الأقل";
    }

    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
    if (fieldErrors[name]) {
      setFieldErrors((prev) => ({ ...prev, [name]: "" }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;

    const result = await login(formData.username.trim(), formData.password);
    if (result.success) {
      toast.success("مرحباً بعودتك! 🎉");
    }
  };

  const inputClass = (fieldName) =>
    `w-full bg-primary border rounded-xl px-4 py-3.5 text-white placeholder-gray-500 focus:outline-none focus:ring-2 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed ${
      fieldErrors[fieldName]
        ? "border-danger focus:ring-danger/30"
        : "border-white/10 focus:border-accent focus:ring-accent/20"
    }`;

  const heroContent = (
    <>
      {/* Logo */}
      <div className="w-20 h-20 bg-accent rounded-2xl flex items-center justify-center mx-auto mb-8 shadow-2xl shadow-accent/30">
        <span className="text-primary font-black text-3xl">eF</span>
      </div>

      <h1 className="text-4xl font-black text-white mb-4 leading-tight">
        eFootball{" "}
        <span className="text-accent">Arena</span>
      </h1>

      <p className="text-xl text-gray-300 mb-4 font-medium">
        Welcome Back, Champion! ⚽
      </p>

      <p className="text-gray-400 leading-relaxed mb-8">
        تنافسي — تعلم — ارتقِ بالرانك — شارك البطولات
      </p>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        {[
          { value: "10K+", label: "لاعب" },
          { value: "500+", label: "بطولة" },
          { value: "50K+", label: "مباراة" },
        ].map((stat) => (
          <div
            key={stat.label}
            className="bg-white/5 border border-white/10 rounded-xl p-3"
          >
            <div className="text-accent font-black text-xl">{stat.value}</div>
            <div className="text-gray-400 text-xs mt-1">{stat.label}</div>
          </div>
        ))}
      </div>
    </>
  );

  return (
    <AuthLayout heroContent={heroContent}>
      {/* Mobile Header */}
      <div className="text-center mb-8 lg:hidden">
        <div className="w-14 h-14 bg-accent rounded-2xl flex items-center justify-center mx-auto mb-4">
          <span className="text-primary font-black text-xl">eF</span>
        </div>
        <h1 className="text-2xl font-bold text-white">eFootball Arena</h1>
      </div>

      {/* Form Card */}
      <div className="bg-secondary border border-white/10 rounded-2xl p-8 shadow-2xl">
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-white">Welcome Back</h2>
          <p className="text-gray-400 text-sm mt-1">سجل دخولك للمتابعة</p>
        </div>

        {/* Google Button */}
        <GoogleButton
          label="Continue with Google"
          onClick={() => toast("قريباً — Google OAuth", { icon: "🔜" })}
        />

        {/* Divider */}
        <div className="flex items-center gap-3 my-5">
          <div className="flex-1 h-px bg-white/10" />
          <span className="text-gray-500 text-xs">أو</span>
          <div className="flex-1 h-px bg-white/10" />
        </div>

        <form onSubmit={handleSubmit} className="space-y-4" noValidate>
          {/* Username Field */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              اسم المستخدم أو البريد الإلكتروني
            </label>
            <input
              ref={usernameRef}
              type="text"
              name="username"
              value={formData.username}
              onChange={handleChange}
              placeholder="PlayerName123 أو email@example.com"
              disabled={loading}
              autoComplete="username"
              className={inputClass("username")}
            />
            {fieldErrors.username && (
              <p className="mt-1.5 text-xs text-danger flex items-center gap-1">
                <span>⚠</span> {fieldErrors.username}
              </p>
            )}
          </div>

          {/* Password Field */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-sm font-medium text-gray-300">
                كلمة المرور
              </label>
              <button
                type="button"
                className="text-xs text-accent hover:text-accent/80 transition-colors"
                onClick={() => toast("قريباً — Forgot Password", { icon: "🔜" })}
              >
                نسيت كلمة المرور؟
              </button>
            </div>
            <div className="relative">
              <input
                type={showPassword ? "text" : "password"}
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="••••••••"
                disabled={loading}
                autoComplete="current-password"
                className={`${inputClass("password")} pr-12`}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-200 transition-colors"
                tabIndex={-1}
              >
                {showPassword ? (
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                  </svg>
                ) : (
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                )}
              </button>
            </div>
            {fieldErrors.password && (
              <p className="mt-1.5 text-xs text-danger flex items-center gap-1">
                <span>⚠</span> {fieldErrors.password}
              </p>
            )}
          </div>

          {/* Remember Me */}
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="rememberMe"
              name="rememberMe"
              checked={formData.rememberMe}
              onChange={handleChange}
              className="w-4 h-4 accent-yellow-500 rounded cursor-pointer"
            />
            <label
              htmlFor="rememberMe"
              className="text-sm text-gray-400 cursor-pointer select-none hover:text-gray-300 transition-colors"
            >
              تذكرني
            </label>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-accent text-primary py-3.5 rounded-xl font-bold text-base hover:bg-accent/90 active:scale-[0.98] transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 shadow-lg shadow-accent/20 mt-2"
          >
            {loading ? (
              <>
                <LoadingSpinner size="sm" color="white" />
                جاري تسجيل الدخول...
              </>
            ) : (
              "تسجيل الدخول →"
            )}
          </button>
        </form>

        {/* Footer */}
        <div className="mt-6 pt-5 border-t border-white/10 text-center">
          <p className="text-gray-400 text-sm">
            ليس لديك حساب؟{" "}
            <Link
              to="/register"
              className="text-accent font-semibold hover:text-accent/80 transition-colors"
            >
              إنشاء حساب جديد
            </Link>
          </p>
        </div>
      </div>
    </AuthLayout>
  );
};

export default Login;