import { useState } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { HeartPulse, LogIn, UserPlus } from 'lucide-react';
import { authService } from '../services/auth';
import { useAuth } from '../context/AuthContext';

const LoginPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login: setAuthContext } = useAuth();
  const [email, setEmail] = useState(location.state?.email || '');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(location.state?.registered ? 'Account created successfully! Please log in.' : '');

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');
    try {
      const res = await authService.login(email, password);
      if (res.access_token && res.user) {
        setAuthContext(res.access_token, res.user);
      }
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };


  return (
    <div className="min-h-screen flex">
      {/* Left side */}
      <div className="hidden lg:flex flex-col justify-center w-1/2 bg-slate-900 text-white p-16 relative overflow-hidden">
        <div className="absolute inset-0 bg-brand-900/20 mix-blend-multiply" />
        <div className="relative z-10 max-w-lg">
          <div className="flex items-center gap-3 mb-12">
            <HeartPulse className="w-10 h-10 text-brand-400" />
            <span className="text-2xl font-bold">CareBridge AI</span>
          </div>
          <h1 className="text-5xl font-bold leading-tight mb-6">
            One patient.<br />
            Every record.<br />
            One intelligent timeline.
          </h1>
          <p className="text-xl text-slate-300">
            CareBridge AI connects fragmented medical records into a unified timeline for clinician review support.
          </p>
        </div>
      </div>

      {/* Right side - Login */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 bg-slate-50">
        <div className="w-full max-w-md bg-white p-8 rounded-2xl shadow-sm border border-slate-100">
          <h2 className="text-2xl font-bold text-slate-900 mb-2">Welcome Back</h2>
          <p className="text-slate-500 mb-8">Sign in to your CareBridge account</p>

          {success && <div className="mb-4 p-3 bg-green-50 text-green-700 rounded-lg text-sm">{success}</div>}
          {error && <div className="mb-4 p-3 bg-red-50 text-red-600 rounded-lg text-sm">{error}</div>}

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Email Address</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-brand-500 outline-none transition-all"
                placeholder="doctor@hospital.org"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-brand-500 outline-none transition-all"
                placeholder="••••••••"
              />
            </div>

            <button 
              type="submit" 
              disabled={loading}
              className="w-full flex justify-center items-center gap-2 py-3 px-4 bg-brand-600 text-white rounded-lg font-semibold hover:bg-brand-700 disabled:opacity-50 transition-colors mt-2"
            >
              {loading ? 'Logging in...' : 'Log In'} <LogIn className="w-5 h-5" />
            </button>
          </form>

          <div className="mt-8 pt-6 border-t border-slate-100 text-center">
            <p className="text-sm text-slate-600 mb-3">Don't have an account?</p>
            <Link 
              to="/register"
              className="w-full flex justify-center items-center gap-2 py-2.5 px-4 bg-slate-100 text-slate-700 rounded-lg font-semibold hover:bg-slate-200 transition-colors"
            >
              Create Account <UserPlus className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
