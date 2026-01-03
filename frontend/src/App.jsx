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
import Profile from './pages/Profile';
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
  const [isDropdownOpen, setIsDropdownOpen] = React.useState(false);

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
            <div className="flex items-center gap-4 relative">
              <span className="text-sm text-slate-600 hidden md:block">
                {user?.first_name || 'User'}
              </span>

              {/* Dropdown Trigger */}
              <button
                onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                className="h-9 w-9 rounded-full bg-sky-100 border border-sky-200 flex items-center justify-center text-sky-700 font-medium hover:bg-sky-200 transition-colors focus:outline-none"
              >
                {user?.first_name ? user.first_name[0] : 'U'}
              </button>

              {/* Dropdown Menu */}
              {isDropdownOpen && (
                <div className="absolute top-12 right-0 w-48 bg-white rounded-md shadow-lg border border-slate-100 py-1 z-50">
                  <div className="px-4 py-2 border-b border-slate-50 md:hidden">
                    <p className="text-sm font-semibold text-slate-900">{user?.first_name}</p>
                  </div>
                  <Link
                    to="/profile"
                    className="block px-4 py-2 text-sm text-slate-700 hover:bg-slate-50"
                    onClick={() => setIsDropdownOpen(false)}
                  >
                    Edit Profile
                  </Link>
                  <button
                    onClick={() => {
                      setIsDropdownOpen(false);
                      logout();
                    }}
                    className="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                  >
                    Logout
                  </button>
                </div>
              )}
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

          <Route path="/profile" element={
            <PrivateRoute>
              <Layout>
                <Profile />
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
