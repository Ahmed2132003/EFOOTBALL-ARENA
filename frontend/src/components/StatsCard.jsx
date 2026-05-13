const StatsCard = ({ icon, label, value, color = "accent", subtitle }) => (
  <div className="bg-secondary border border-white/10 rounded-2xl p-5 hover:border-accent/30 transition-all duration-300 group">
    <div className="flex items-start justify-between mb-3">
      <span className="text-3xl">{icon}</span>
      {subtitle && (
        <span className="text-xs text-gray-500 bg-white/5 px-2 py-1 rounded-full">{subtitle}</span>
      )}
    </div>
    <div className={`text-3xl font-black mb-1 text-${color} group-hover:scale-105 transition-transform`}>
      {value}
    </div>
    <div className="text-gray-400 text-sm font-medium">{label}</div>
  </div>
);

export default StatsCard;