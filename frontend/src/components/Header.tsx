import { Search, Bell } from 'lucide-react';

const Header = () => {
  return (
    <header className="h-20 bg-white border-b border-slate-200 flex items-center justify-between px-8 sticky top-0 z-10">
      <div className="w-96 relative">
        <Search className="w-5 h-5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
        <input 
          type="text" 
          placeholder="Search patients, documents, insights..." 
          className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:bg-white transition-colors"
        />
      </div>
      
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2 px-3 py-1.5 bg-slate-100 rounded-full">
          <div className="w-2 h-2 rounded-full bg-success"></div>
          <span className="text-xs font-semibold text-slate-600">Secure Workspace</span>
        </div>
        
        <button className="relative p-2 text-slate-500 hover:text-slate-700 transition-colors">
          <Bell className="w-6 h-6" />
          <span className="absolute top-1 right-1 w-2.5 h-2.5 bg-critical rounded-full border-2 border-white"></span>
        </button>
      </div>
    </header>
  );
};

export default Header;
