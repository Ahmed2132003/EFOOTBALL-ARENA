import { Outlet } from "react-router-dom";
import Navbar from "../components/Navbar";
import { Toaster } from "react-hot-toast";

const MainLayout = () => {
  return (
    <div className="min-h-screen bg-primary text-white">
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: "#0F172A",
            color: "#fff",
            border: "1px solid #D4AF37",
          },
          success: {
            iconTheme: {
              primary: "#22C55E",
              secondary: "#0F172A",
            },
          },
          error: {
            iconTheme: {
              primary: "#EF4444",
              secondary: "#0F172A",
            },
          },
        }}
      />
      <Navbar />
      <main>
        <Outlet />
      </main>
    </div>
  );
};

export default MainLayout;