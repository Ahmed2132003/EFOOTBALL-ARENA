import { useState, useEffect, useRef } from "react";
import { Link } from "react-router-dom";
import toast from "react-hot-toast";
import useAuth from "../hooks/useAuth";
import AuthLayout from "../components/AuthLayout";
import GoogleButton from "../components/GoogleButton";
import LoadingSpinner from "../components/LoadingSpinner";

const PasswordStrength = ({ password }) => {
  const checks = [
    { label: "8 أحرف على الأقل", pass: password.length >= 8 },
    { label: "حرف كبير", pass: /[A-Z]/.test(password) },
    { label: "حرف صغير", pass: /[a-z]/.test(password) },
    { label: "رقم", pass: /[0-9]/.test(password) },
  ];

  const score = checks.filter((c) => c.pass).length;
  const colors = ["bg-danger", "bg-orange-400", "bg-yellow-400", "bg-success", "bg-success"];
  const labels = ["", "ضعيفة", "مقبولة", "جيدة", "قوية"];

  if (!password) return null;

  return (
    <div className="mt-2 space-y-1.5">
      <div className="flex gap-1">
        {[0, 1, 2, 3].map((i) => (
          <div
            key={i}
            className={`h-1 flex-1 rounded-full transition-all duration-300 ${
              i < score ? colors[score] : "bg-white/10"
            }`}
          />
        ))}
      </div>
      {score > 0 && (
        <p className={`text-xs ${score <= 1 ? "text-danger" : score <= 2 ? "text-orange-400" : score <= 3 ? "text-yellow-400" : "text-success"}`}>
          قوة كلمة المرور: {labels[score]}
        </p>
      )}
    </div>
  );
};

const Register = () => {
  const { register, loading, error, clearError } = useAuth();
  const usernameRef = useRef(null);

  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
  });

  const [fieldErrors, setFieldErrors] = useState({});
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);

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
      errors.username = "اسم المستخدم مطلوب";
    } else if (formData.username.trim().length < 3) {
      errors.username = "يجب أن يكون 3 أحرف على الأقل";
    }

    if (!formData.email.trim()) {
      errors.email = "البريد الإلكتروني مطلوب";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      errors.email = "صيغة البريد الإلكتروني غير صحيحة";
    }

    if (!formData.password) {
      errors.password = "كلمة المرور مطلوبة";
    } else if (formData.password.length < 8) {
      errors.password = "يجب أن تكون 8 أحرف على الأقل";
    } else if (!/(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])/.test(formData.password)) {
      errors.password = "يجب أن تحتوي على حرف كبير وصغير ورقم";
    }

    if (!formData.confirmPassword) {
      errors.confirmPassword = "تأكيد كلمة المرور مطلوب";
    } else if (formData.password !== formData.confirmPassword) {
      errors.confirmPassword = "كلمتا المرور غير متطابقتين";
    }

    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (fieldErrors[name]) {
      setFieldErrors((prev) => ({ ...prev, [name]: "" }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;

    const result = await register(
      formData.username.trim(),
      formData.email.trim(),
      formData.password,
      formData.confirmPassword
    );

    if (result.success) {
      toast.success("تم إنشاء حسابك بنجاح! مرحباً بك 🎉");
    }
  };

  const inputClass = (fieldName) =>
    `w-full bg-primary border rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed ${
      fieldErrors[fieldName]
        ? "border-danger focus:ring-danger/30"
        : "border-white/10 focus:border-accent focus:ring-accent/20"
    }`;

  const heroContent = (
    <>
      <div className="w-20 h-20 bg-accent rounded-2xl flex items-center justify-center mx-auto mb-8 shadow-2xl shadow-accent/30">
        <span className="text-primary font-black text-3xl">eF</span>
      </div>

      <h1 className="text-4xl font-black text-white mb-4 leading-tight">
        eFootball{" "}
        <span className="text-accent">Arena</span>
      </h1>

      <p className="text-xl text-gray-300 mb-4 font-medium">
        Join The Ultimate eFootball Community ⚽
      </p>

      <p className="text-gray-400 leading-relaxed mb-8">
        تنافسي — تعلم — ارتقِ بالرانك — شارك البطولات
      </p>

      <div className="space-y-3 text-right">
        {[
          { icon: "🏆", text: "بطولات أسبوعية مع جوائز حقيقية" },
          { icon: "📋", text: "شارك وتعلم أفضل التكتيكات" },
          { icon: "💰", text: "سوق لشراء وبيع الحسابات" },
          { icon: "🌍", text: "مجتمع من آلاف اللاعبين العرب" },
        ].map((item) => (
          <div key={item.text} className="flex items-center gap-3 bg-white/5 border border-white/10 rounded-xl px-4 py-3">
            <span className="text-xl">{item.icon}</span>
            <span className="text-gray-300 text-sm">{item.text}</span>
          </div>
        ))}
      </div>
    </>
  );

  return (
    <AuthLayout heroContent={heroContent}>
      {/* Mobile Header */}
      <div className="text-center mb-6 lg:hidden">
        <div className="w-14 h-14 bg-accent rounded-2xl flex items-center justify-center mx-auto mb-3">
          <span className="text-primary font-black text-xl">eF</span>
        </div>
        <h1 className="text-2xl font-bold text-white">eFootball Arena</h1>
      </div>

      {/* Form Card */}
      <div className="bg-secondary border border-white/10 rounded-2xl p-7 shadow-2xl">
        <div className="mb-5">
          <h2 className="text-2xl font-bold text-white">إنشاء حساب</h2>
          <p className="text-gray-400 text-sm mt-1">انضم إلى مجتمع eFootball Arena</p>
        </div>

        {/* Google Button */}
        <GoogleButton
          label="Sign up with Google"
          onClick={() => toast("قريباً — Google OAuth", { icon: "🔜" })}
        />

        {/* Divider */}
        <div className="flex items-center gap-3 my-4">
          <div className="flex-1 h-px bg-white/10" />
          <span className="text-gray-500 text-xs">أو سجل بالبريد الإلكتروني</span>
          <div className="flex-1 h-px bg-white/10" />
        </div>

        <form onSubmit={handleSubmit} className="space-y-4" noValidate>
          {/* Username */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1.5">
              اسم المستخدم <span className="text-danger">*</span>
            </label>
            <input
              ref={usernameRef}
              type="text"
              name="username"
              value={formData.username}
              onChange={handleChange}
              placeholder="PlayerName123"
              disabled={loading}
              autoComplete="username"
              className={inputClass("username")}
            />
            {fieldErrors.username && (
              <p className="mt-1 text-xs text-danger flex items-center gap-1">
                <span>⚠</span> {fieldErrors.username}
              </p>
            )}
          </div>

          {/* Email */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1.5">
              البريد الإلكتروني <span className="text-danger">*</span>
            </label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="example@email.com"
              disabled={loading}
              autoComplete="email"
              className={inputClass("email")}
            />
            {fieldErrors.email && (
              <p className="mt-1 text-xs text-danger flex items-center gap-1">
                <span>⚠</span> {fieldErrors.email}
              </p>
            )}
          </div>

          {/* Password */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1.5">
              كلمة المرور <span className="text-danger">*</span>
            </label>
            <div className="relative">
              <input
                type={showPassword ? "text" : "password"}
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="••••••••"
                disabled={loading}
                autoComplete="new-password"
                className={`${inputClass("password")} pr-12`}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-200 transition-colors"
                tabIndex={-1}
              >
                {showPassword ? (
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                  </svg>
                ) : (
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                )}
              </button>
            </div>
            <PasswordStrength password={formData.password} />
            {fieldErrors.password && (
              <p className="mt-1 text-xs text-danger flex items-center gap-1">
                <span>⚠</span> {fieldErrors.password}
              </p>
            )}
          </div>

          {/* Confirm Password */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1.5">
              تأكيد كلمة المرور <span className="text-danger">*</span>
            </label>
            <div className="relative">
              <input
                type={showConfirm ? "text" : "password"}
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                placeholder="••••••••"
                disabled={loading}
                autoComplete="new-password"
                className={`${inputClass("confirmPassword")} pr-12`}
              />
              <button
                type="button"
                onClick={() => setShowConfirm(!showConfirm)}
                className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-200 transition-colors"
                tabIndex={-1}
              >
                {showConfirm ? (
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                  </svg>
                ) : (
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                )}
              </button>

              {/* Match Indicator */}
              {formData.confirmPassword && formData.password === formData.confirmPassword && (
                <div className="absolute left-10 top-1/2 -translate-y-1/2">
                  <svg className="w-4 h-4 text-success" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
              )}
            </div>
            {fieldErrors.confirmPassword && (
              <p className="mt-1 text-xs text-danger flex items-center gap-1">
                <span>⚠</span> {fieldErrors.confirmPassword}
              </p>
            )}
          </div>

          {/* Submit */}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-accent text-primary py-3.5 rounded-xl font-bold text-base hover:bg-accent/90 active:scale-[0.98] transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 shadow-lg shadow-accent/20 mt-2"
          >
            {loading ? (
              <>
                <LoadingSpinner size="sm" color="white" />
                جاري إنشاء الحساب...
              </>
            ) : (
              "إنشاء الحساب →"
            )}
          </button>
        </form>

        {/* Footer */}
        <div className="mt-5 pt-5 border-t border-white/10 text-center">
          <p className="text-gray-400 text-sm">
            لديك حساب؟{" "}
            <Link
              to="/login"
              className="text-accent font-semibold hover:text-accent/80 transition-colors"
            >
              تسجيل الدخول
            </Link>
          </p>
        </div>
      </div>
    </AuthLayout>
  );
};

export default Register;