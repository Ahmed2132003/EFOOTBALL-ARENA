const AuthLayout = ({ children, heroContent }) => {
  return (
    <div className="min-h-[calc(100vh-64px)] flex">
      {/* Left Side — Hero */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-primary via-secondary to-primary relative overflow-hidden items-center justify-center p-12">
        {/* Background Effects */}
        <div className="absolute inset-0">
          <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-accent/5 rounded-full blur-3xl" />
          <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-accent/3 rounded-full blur-3xl" />
        </div>

        {/* Grid Pattern */}
        <div
          className="absolute inset-0 opacity-5"
          style={{
            backgroundImage:
              "linear-gradient(#D4AF37 1px, transparent 1px), linear-gradient(90deg, #D4AF37 1px, transparent 1px)",
            backgroundSize: "50px 50px",
          }}
        />

        <div className="relative z-10 text-center max-w-md">
          {heroContent}
        </div>
      </div>

      {/* Right Side — Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center px-6 py-12">
        <div className="w-full max-w-md">{children}</div>
      </div>
    </div>
  );
};

export default AuthLayout;