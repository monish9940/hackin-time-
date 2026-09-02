import { NavLink, useNavigate, useParams } from 'react-router-dom';
import { HeartPulse, LayoutDashboard, Clock, FileText, Pill, Brain, Stethoscope, ShieldCheck, LogOut } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const Sidebar = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Patient Timeline', path: id ? `/patient/${id}/timeline` : '/dashboard', icon: Clock },
    { name: 'Documents', path: id ? `/patient/${id}/documents` : '/dashboard', icon: FileText },
    { name: 'Medications', path: id ? `/patient/${id}/medications` : '/dashboard', icon: Pill },
    { name: 'AI Insights', path: id ? `/patient/${id}/insights` : '/dashboard', icon: Brain },
    { name: 'Doctor Notes', path: id ? `/patient/${id}/notes` : '/dashboard', icon: Stethoscope },
    { name: 'Privacy Center', path: '/privacy', icon: ShieldCheck },
  ];

  return (
    <div className="w-64 bg-slate-900 text-slate-300 h-screen fixed left-0 top-0 flex flex-col border-r border-slate-800">
      <div className="p-6 flex items-center gap-3 border-b border-slate-800">
        <HeartPulse className="w-8 h-8 text-brand-500" />
        <span className="text-xl font-bold text-white">CareBridge AI</span>
      </div>
      
      <div className="flex-1 overflow-y-auto py-6">
        <nav className="space-y-1 px-3">
          {navItems.map((item) => (
            <NavLink
              key={item.name}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg font-medium transition-colors ${
                  isActive ? 'bg-brand-600 text-white' : 'hover:bg-slate-800 hover:text-white'
                }`
              }
            >
              <item.icon className="w-5 h-5" />
              {item.name}
            </NavLink>
          ))}
        </nav>
      </div>

      <div className="p-4 border-t border-slate-800">
        <div className="bg-slate-800 rounded-lg p-3 mb-4">
          <div className="flex items-center gap-2 text-success mb-1">
            <ShieldCheck className="w-4 h-4" />
            <span className="text-sm font-semibold">Privacy protected</span>
          </div>
          <p className="text-xs text-slate-400">Authenticated Session</p>
        </div>
        
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-brand-500 flex items-center justify-center text-white font-bold">
              {user?.full_name?.charAt(0) || 'U'}
            </div>
            <div className="overflow-hidden">
              <p className="text-sm font-bold text-white truncate">{user?.full_name || 'Clinician'}</p>
              <p className="text-xs text-slate-400 truncate">{user?.specialization || 'Healthcare Provider'}</p>
            </div>
          </div>
          <button onClick={handleLogout} title="Log out" className="text-slate-400 hover:text-white p-2 shrink-0">
            <LogOut className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;

