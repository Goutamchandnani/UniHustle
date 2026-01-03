import React from 'react';
import { BrowserRouter, Routes, Route, Link, Navigate, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Dashboard from './pages/Dashboard';
import JobDetail from './pages/JobDetail';
import TimetableInput from './pages/TimetableInput';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Jobs from './pages/Jobs';
import Applications from './pages/Applications';
import Onboarding from './pages/Onboarding';
import PrivateRoute from './components/PrivateRoute';

// Private Route Component
// const PrivateRoute = ({ children }) => { // This component is now imported from './components/PrivateRoute'
//   const { token, loading } = useAuth();
//   if (loading) return <div className="p-8 text-center text-slate-500">Loading...</div>;
//   return token ? children : <Navigate to="/login" />;
// };

// Layout Wrapper (Authenticated)
const Layout = ({ children }) => {
  const { logout, user } = useAuth();
  const location = useLocation();

  const getNavItemClass = (path) => {
    // Exact match for root, partial for others if needed, but exact is safer for these top-level items
    const isActive = location.pathname === path;
    return isActive
      ? "border-sky-500 text-slate-900 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
      : "border-transparent text-slate-500 hover:border-slate-300 hover:text-slate-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium";
  };

  return (
    <div className="min-h-screen flex flex-col">
      <nav className="bg-white border-b border-slate-200 shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <Link to="/" className="flex-shrink-0 flex items-center text-sky-600 font-bold text-xl">
                UniHustle
              </Link>
              <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                <Link to="/" className={getNavItemClass('/')}>
                  Dashboard
                </Link>
                <Link to="/schedule" className={getNavItemClass('/schedule')}>
                  Schedule
                </Link>
                <Link to="/applications" className={getNavItemClass('/applications')}>
                  Applications
                </Link>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm text-slate-600">
                {user?.first_name || 'User'}
              </span>
              <button
                onClick={logout}
                className="text-sm text-red-600 hover:text-red-800"
              >
                Logout
              </button>
              <div className="h-8 w-8 rounded-full bg-slate-200 flex items-center justify-center text-slate-500">
                {user?.first_name ? user.first_name[0] : 'U'}
              </div>
            </div>
          </div>
        </div>
      </nav>
      <main className="flex-1 bg-slate-50">
        {children}
      </main>
    </div>
  );
};

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* Public Routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />

          {/* Protected Routes */}
          <Route path="/" element={
            <PrivateRoute>
              <Layout>
                <Dashboard />
              </Layout>
            </PrivateRoute>
          } />

          <Route path="/jobs" element={
            <PrivateRoute>
              <Layout>
                <Jobs />
              </Layout>
            </PrivateRoute>
          } />

          <Route path="/jobs/:id" element={
            <PrivateRoute>
              <Layout>
                <JobDetail />
              </Layout>
            </PrivateRoute>
          } />

          <Route path="/schedule" element={
            <PrivateRoute>
              <Layout>
                <TimetableInput />
              </Layout>
            </PrivateRoute>
          } />

          <Route path="/applications" element={
            <PrivateRoute>
              <Layout>
                <Applications />
              </Layout>
            </PrivateRoute>
          } />

          <Route path="/onboarding" element={
            <PrivateRoute>
              <Onboarding />
            </PrivateRoute>
          } />

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
