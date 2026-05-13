import { useState, useRef } from "react";

const AvatarUpload = ({ currentAvatar, username, onFileSelect }) => {
  const [preview, setPreview] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const [error, setError] = useState("");
  const inputRef = useRef(null);

  const ALLOWED_TYPES = ["image/jpeg", "image/jpg", "image/png", "image/webp"];
  const MAX_SIZE_MB   = 5;

  const validateFile = (file) => {
    if (!ALLOWED_TYPES.includes(file.type)) {
      return "Only JPG, PNG, WEBP files are allowed.";
    }
    if (file.size > MAX_SIZE_MB * 1024 * 1024) {
      return `File size must not exceed ${MAX_SIZE_MB}MB.`;
    }
    return null;
  };

  const processFile = (file) => {
    const err = validateFile(file);
    if (err) { setError(err); return; }
    setError("");
    const reader = new FileReader();
    reader.onloadend = () => setPreview(reader.result);
    reader.readAsDataURL(file);
    onFileSelect(file);
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) processFile(file);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) processFile(file);
  };

  const displaySrc = preview || currentAvatar;
  const initials   = username?.charAt(0)?.toUpperCase() || "?";

  return (
    <div className="flex flex-col items-center gap-4">
      {/* Avatar Display */}
      <div
        className={`relative w-32 h-32 rounded-2xl overflow-hidden border-2 cursor-pointer transition-all duration-200 group
          ${dragOver ? "border-accent scale-105" : "border-white/20 hover:border-accent"}`}
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
      >
        {displaySrc ? (
          <img src={displaySrc} alt="Avatar" className="w-full h-full object-cover" />
        ) : (
          <div className="w-full h-full bg-accent/20 flex items-center justify-center">
            <span className="text-accent font-black text-4xl">{initials}</span>
          </div>
        )}

        {/* Overlay */}
        <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity duration-200 flex items-center justify-center">
          <div className="text-center">
            <svg className="w-8 h-8 text-white mx-auto mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            <span className="text-white text-xs font-medium">Change Photo</span>
          </div>
        </div>

        {/* New badge */}
        {preview && (
          <div className="absolute top-2 right-2 bg-accent text-primary text-xs font-bold px-2 py-0.5 rounded-full">
            NEW
          </div>
        )}
      </div>

      <input
        ref={inputRef}
        type="file"
        accept=".jpg,.jpeg,.png,.webp"
        onChange={handleFileChange}
        className="hidden"
      />

      <div className="text-center">
        <button
          type="button"
          onClick={() => inputRef.current?.click()}
          className="text-accent text-sm font-medium hover:text-accent/80 transition-colors"
        >
          Upload New Photo
        </button>
        <p className="text-gray-500 text-xs mt-1">JPG, PNG, WEBP — Max 5MB</p>
      </div>

      {error && (
        <p className="text-danger text-sm flex items-center gap-1">
          <span>⚠</span> {error}
        </p>
      )}
    </div>
  );
};

export default AvatarUpload;