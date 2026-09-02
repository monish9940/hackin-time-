import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import Dashboard from './pages/Dashboard';
import PatientProfile from './pages/PatientProfile';
import PatientTimeline from './pages/PatientTimeline';
import DocumentsPage from './pages/DocumentsPage';
import MedicationsPage from './pages/MedicationsPage';
import AIInsightsPage from './pages/AIInsightsPage';
import { AuthProvider, useAuth } from './context/AuthContext';

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { user, loading } = useAuth();
  if (loading) {
    return <div className="flex h-screen items-center justify-center bg-slate-50 text-slate-600 font-semibold">Validating session...</div>;
  }
  if (!user) return <Navigate to="/login" replace />;
  return <>{children}</>;
};

function AppRoutes() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        <Route path="/patient/:id" element={<ProtectedRoute><PatientProfile /></ProtectedRoute>} />
        <Route path="/patient/:id/timeline" element={<ProtectedRoute><PatientTimeline /></ProtectedRoute>} />
        <Route path="/patient/:id/documents" element={<ProtectedRoute><DocumentsPage /></ProtectedRoute>} />
        <Route path="/patient/:id/medications" element={<ProtectedRoute><MedicationsPage /></ProtectedRoute>} />
        <Route path="/patient/:id/insights" element={<ProtectedRoute><AIInsightsPage /></ProtectedRoute>} />
        <Route path="/patient/:id/notes" element={<ProtectedRoute><PatientProfile /></ProtectedRoute>} />
        <Route path="/privacy" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </Router>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  );
}

export default App;

