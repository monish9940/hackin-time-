import { useNavigate, Link } from 'react-router-dom';
import { HeartPulse, ShieldCheck, ArrowRight, Brain, Clock, AlertTriangle, Pill, Activity, UserPlus, LogIn } from 'lucide-react';

const LandingPage = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-white">
      {/* Top Navbar */}
      <nav className="flex justify-between items-center px-8 py-5 border-b border-slate-100 sticky top-0 bg-white/95 backdrop-blur-md z-30">
        <div className="flex items-center gap-3">
          <HeartPulse className="w-8 h-8 text-brand-600" />
          <span className="text-xl font-bold text-slate-900 tracking-tight">CareBridge AI</span>
        </div>
        
        <div className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-600">
          <a href="#how-it-works" className="hover:text-brand-600 transition-colors">How It Works</a>
          <a href="#ai-agents" className="hover:text-brand-600 transition-colors">AI Agents</a>
          <a href="#privacy" className="hover:text-brand-600 transition-colors">Privacy</a>
        </div>

        <div className="flex items-center gap-4">
          <Link to="/login" className="px-4 py-2 text-sm font-medium text-slate-700 hover:text-brand-600 transition-colors flex items-center gap-1.5">
            <LogIn className="w-4 h-4" /> Log In
          </Link>
          <Link to="/register" className="px-4 py-2 text-sm font-medium text-white bg-brand-600 rounded-lg hover:bg-brand-700 shadow-sm transition-colors flex items-center gap-1.5">
            <UserPlus className="w-4 h-4" /> Create Account
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="px-8 pt-20 pb-16 max-w-6xl mx-auto text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-brand-50 text-brand-700 text-xs font-semibold mb-6 border border-brand-100">
          <Brain className="w-4 h-4 text-brand-600" /> Multi-Agent AI Clinical Decision Support
        </div>
        
        <h1 className="text-5xl md:text-6xl font-extrabold text-slate-900 leading-tight mb-6 tracking-tight max-w-4xl mx-auto">
          One patient.<br />
          <span className="text-brand-600">Every record.</span><br />
          One intelligent timeline.
        </h1>
        
        <p className="text-xl text-slate-600 mb-10 max-w-3xl mx-auto font-normal leading-relaxed">
          CareBridge AI connects fragmented medical records into a unified patient timeline and identifies potential inconsistencies and information gaps for clinician review.
        </p>

        <div className="flex justify-center items-center gap-4 mb-16">
          <button onClick={() => navigate('/register')} className="flex items-center gap-2 px-8 py-4 font-semibold text-white bg-brand-600 rounded-xl hover:bg-brand-700 shadow-lg shadow-brand-500/30 transition-all text-base">
            Get Started <ArrowRight className="w-5 h-5" />
          </button>
          <button onClick={() => navigate('/login')} className="px-8 py-4 font-semibold text-slate-700 bg-slate-100 rounded-xl hover:bg-slate-200 transition-all text-base">
            Log In
          </button>
        </div>

        {/* Realistic Dashboard Visualization Mockup */}
        <div className="bg-slate-900 rounded-2xl p-4 shadow-2xl border border-slate-800 text-left max-w-5xl mx-auto overflow-hidden">
          <div className="flex items-center justify-between px-4 py-3 border-b border-slate-800">
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 rounded-full bg-red-500" />
              <div className="w-3 h-3 rounded-full bg-yellow-500" />
              <div className="w-3 h-3 rounded-full bg-green-500" />
              <span className="text-xs text-slate-400 font-mono ml-2">CareBridge AI Clinical Workspace</span>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-xs font-semibold bg-brand-500/20 text-brand-300 px-2.5 py-1 rounded-full border border-brand-500/30 flex items-center gap-1">
                <Activity className="w-3 h-3" /> Live Timeline Engine
              </span>
            </div>
          </div>

          <div className="p-6 bg-slate-950 grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Patient Header Card */}
            <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl md:col-span-3 flex flex-wrap justify-between items-center gap-4">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-brand-600 text-white font-bold flex items-center justify-center text-lg">
                  AK
                </div>
                <div>
                  <h4 className="text-white font-bold text-lg">Arun Kumar</h4>
                  <p className="text-xs text-slate-400">ID: CB-2026-1042 • 45 yrs • Male • Blood Group: O+</p>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <div className="text-right">
                  <p className="text-xs text-slate-400">AI Review Priority</p>
                  <p className="text-xl font-bold text-amber-400">80 / 100 (Critical Review)</p>
                </div>
              </div>
            </div>

            {/* Timeline Stream */}
            <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl md:col-span-2">
              <h5 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4 flex items-center gap-2">
                <Clock className="w-4 h-4 text-brand-400" /> Unified Chronological Patient Timeline
              </h5>
              <div className="space-y-3 text-sm">
                <div className="p-3 bg-slate-800/80 rounded-lg border-l-4 border-amber-500">
                  <div className="flex justify-between text-xs text-slate-400 mb-1">
                    <span>2026-07-22</span>
                    <span className="text-amber-400 font-semibold">Dosage Increased</span>
                  </div>
                  <p className="text-white font-medium">Metformin dosage updated to 1000mg twice daily</p>
                  <p className="text-xs text-slate-400 mt-1">Source: City Hospital</p>
                </div>
                <div className="p-3 bg-slate-800/80 rounded-lg border-l-4 border-red-500">
                  <div className="flex justify-between text-xs text-slate-400 mb-1">
                    <span>2026-08-05</span>
                    <span className="text-red-400 font-semibold">Allergy Recorded</span>
                  </div>
                  <p className="text-white font-medium">Severe Penicillin Reaction (Anaphylaxis Risk)</p>
                  <p className="text-xs text-slate-400 mt-1">Source: Apollo Hospital</p>
                </div>
              </div>
            </div>

            {/* AI Insights & Flags */}
            <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
              <h5 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4 flex items-center gap-2">
                <Brain className="w-4 h-4 text-brand-400" /> AI Agents Insights
              </h5>
              <div className="space-y-3">
                <div className="p-3 bg-red-950/40 border border-red-800/50 rounded-lg">
                  <div className="flex items-center gap-2 text-red-400 text-xs font-bold mb-1">
                    <AlertTriangle className="w-3.5 h-3.5" /> Allergy Conflict
                  </div>
                  <p className="text-xs text-slate-200">Prescription matches documented Penicillin allergy.</p>
                </div>
                <div className="p-3 bg-blue-950/40 border border-blue-800/50 rounded-lg">
                  <div className="flex items-center gap-2 text-blue-400 text-xs font-bold mb-1">
                    <Pill className="w-3.5 h-3.5" /> Medication History
                  </div>
                  <p className="text-xs text-slate-200">Metformin dosage doubled within 30 days.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="bg-slate-50 py-24 border-t border-slate-100">
        <div className="max-w-6xl mx-auto px-8">
          <h2 className="text-3xl font-bold text-slate-900 text-center mb-16">How CareBridge AI Works</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
              <div className="text-4xl font-black text-brand-600 mb-4">01</div>
              <h3 className="text-lg font-bold text-slate-900 mb-2">Upload Records</h3>
              <p className="text-slate-600 text-sm">Upload medical reports, lab results, and prescriptions securely.</p>
            </div>
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
              <div className="text-4xl font-black text-brand-600 mb-4">02</div>
              <h3 className="text-lg font-bold text-slate-900 mb-2">AI Extraction</h3>
              <p className="text-slate-600 text-sm">Extraction agents parse structured medical entities from text.</p>
            </div>
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
              <div className="text-4xl font-black text-brand-600 mb-4">03</div>
              <h3 className="text-lg font-bold text-slate-900 mb-2">Build Timeline</h3>
              <p className="text-slate-600 text-sm">CareBridge organizes all records into a single chronological stream.</p>
            </div>
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
              <div className="text-4xl font-black text-brand-600 mb-4">04</div>
              <h3 className="text-lg font-bold text-slate-900 mb-2">Clinician Review</h3>
              <p className="text-slate-600 text-sm">AI highlights potential inconsistencies and missing information for review.</p>
            </div>
          </div>
        </div>
      </section>

      {/* AI Agents Section */}
      <section id="ai-agents" className="py-24 max-w-6xl mx-auto px-8">
        <h2 className="text-3xl font-bold text-slate-900 text-center mb-4">Specialized Clinical AI Agents</h2>
        <p className="text-slate-600 text-center max-w-2xl mx-auto mb-16">
          Multiple targeted agents analyze records concurrently to construct comprehensive patient profiles.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="p-6 bg-white border border-slate-200 rounded-2xl shadow-sm">
            <Brain className="w-10 h-10 text-brand-600 mb-4" />
            <h3 className="text-xl font-bold text-slate-900 mb-2">Extraction Agent</h3>
            <p className="text-slate-600 text-sm">Parses diagnoses, medications, lab values, dates, and doctor notes from OCR text.</p>
          </div>
          <div className="p-6 bg-white border border-slate-200 rounded-2xl shadow-sm">
            <AlertTriangle className="w-10 h-10 text-amber-500 mb-4" />
            <h3 className="text-xl font-bold text-slate-900 mb-2">Consistency Agent</h3>
            <p className="text-slate-600 text-sm">Checks new records against historical data to detect allergy conflicts and dosage changes.</p>
          </div>
          <div className="p-6 bg-white border border-slate-200 rounded-2xl shadow-sm">
            <Clock className="w-10 h-10 text-blue-600 mb-4" />
            <h3 className="text-xl font-bold text-slate-900 mb-2">Missing Info Agent</h3>
            <p className="text-slate-600 text-sm">Identifies gaps in routine clinical documentation based on patient diagnoses.</p>
          </div>
        </div>
      </section>

      {/* Privacy Section */}
      <section id="privacy" className="bg-slate-900 text-white py-20 px-8 text-center">
        <div className="max-w-4xl mx-auto">
          <ShieldCheck className="w-16 h-16 text-emerald-400 mx-auto mb-6" />
          <h2 className="text-3xl font-bold mb-4">Privacy & Security First</h2>
          <p className="text-lg text-slate-300 max-w-2xl mx-auto mb-8">
            CareBridge AI uses standard JWT authentication and local processing architecture to protect patient records.
          </p>
          <button onClick={() => navigate('/register')} className="px-8 py-3.5 bg-brand-600 text-white font-semibold rounded-xl hover:bg-brand-700 transition-colors">
            Register Clinician Account
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-800 py-12 text-center px-8 bg-slate-950 text-slate-400">
        <HeartPulse className="w-6 h-6 mx-auto mb-4 text-brand-500" />
        <p className="max-w-2xl mx-auto text-xs leading-relaxed text-slate-400">
          CareBridge AI is designed for healthcare information organization and clinician review support. It does not provide automated medical diagnosis or replace professional clinical judgment.
        </p>
        <p className="mt-6 text-xs text-slate-600">&copy; 2026 CareBridge AI. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default LandingPage;
