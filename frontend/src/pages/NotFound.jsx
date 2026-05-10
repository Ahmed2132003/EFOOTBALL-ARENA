import { Link } from "react-router-dom";

const NotFound = () => {
  return (
    <div className="min-h-[calc(100vh-64px)] flex items-center justify-center px-4">
      <div className="text-center">
        <div className="text-8xl font-black text-accent mb-4">404</div>
        <h1 className="text-3xl font-bold text-white mb-4">
          الصفحة غير موجودة
        </h1>
        <p className="text-gray-400 text-lg mb-8 max-w-md mx-auto">
          عذراً، الصفحة التي تبحث عنها غير موجودة أو تم نقلها.
        </p>
        <Link
          to="/"
          className="inline-flex items-center gap-2 bg-accent text-primary px-8 py-3.5 rounded-xl font-bold text-lg hover:bg-accent/90 transition-all duration-200 shadow-lg shadow-accent/20"
        >
          ← العودة للرئيسية
        </Link>
      </div>
    </div>
  );
};

export default NotFound;