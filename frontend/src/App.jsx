import { BrowserRouter, Routes, Route } from "react-router-dom";
import { useEffect } from "react";
import MainLayout    from "./layouts/MainLayout";
import ProtectedRoute from "./components/ProtectedRoute";
import Home          from "./pages/Home";
import Login         from "./pages/Login";
import Register      from "./pages/Register";
import Dashboard     from "./pages/Dashboard";
import Profile       from "./pages/Profile";
import EditProfile   from "./pages/EditProfile";
import NotFound      from "./pages/NotFound";
import useAuthStore  from "./store/authStore";

const App = () => {
  const { initializeAuth } = useAuthStore();

  useEffect(() => {
    initializeAuth();
  }, [initializeAuth]);

  return (
    <BrowserRouter>
      <Routes>
        <Route element={<MainLayout />}>
          <Route path="/"          element={<Home />} />
          <Route path="/login"     element={<Login />} />
          <Route path="/register"  element={<Register />} />

          {/* Public profile */}
          <Route path="/profile/:username" element={<Profile />} />

          <Route element={<ProtectedRoute />}>
            <Route path="/dashboard"   element={<Dashboard />} />
            <Route path="/profile/edit" element={<EditProfile />} />
            {/* Own profile redirect */}
            <Route path="/profile"     element={<Profile />} />
          </Route>

          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};

export default App;