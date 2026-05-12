const LoadingSpinner = ({ size = "md", color = "accent" }) => {
  const sizes = {
    sm: "w-4 h-4",
    md: "w-6 h-6",
    lg: "w-10 h-10",
  };

  const colors = {
    accent: "border-accent",
    white: "border-white",
    danger: "border-danger",
  };

  return (
    <div
      className={`${sizes[size]} border-2 ${colors[color]} border-t-transparent rounded-full animate-spin`}
    />
  );
};

export default LoadingSpinner;