import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import Header from '../components/Header';
import { Brain, AlertTriangle, HelpCircle, AlertCircle, ShieldAlert } from 'lucide-react';
import api from '../services/api';

const AIInsightsPage = () => {
  const { id } = useParams();
  const [insights, setInsights] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchInsights = async () => {
      try {
        const res = await api.get(`/ai/insights/${id}`);
        setInsights(res.data);
      } catch (e) { console.error(e); } finally {
        setLoading(false);
      }
    };
    fetchInsights();
  }, [id]);

  if (loading) return <div className="flex h-screen items-center justify-center">Loading insights...</div>;

  return (
    <div className="flex h-screen bg-slate-50 overflow-hidden">
      <Sidebar />
      <div className="flex-1 ml-64 flex flex-col h-screen overflow-hidden">
        <Header />
        
        <main className="flex-1 overflow-y-auto p-8">
          <div className="mb-6 flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-slate-900">AI Clinical Insights</h1>
              <p className="text-slate-500 mt-1">Automated analysis of inconsistencies and missing data</p>
            </div>
            <div className="bg-blue-50 text-blue-800 text-sm px-4 py-2 rounded-lg flex items-center gap-2 border border-blue-100">
              <ShieldAlert className="w-4 h-4" />
              <span>AI reviews are for assistive purposes only.</span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Inconsistencies */}
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm flex flex-col">
              <div className="px-6 py-4 border-b border-slate-200 bg-red-50/50 flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-critical" />
                <h3 className="font-bold text-slate-900">Detected Inconsistencies</h3>
              </div>
              <div className="p-6 flex-1">
                {insights.filter(i => i.insight_type === 'Inconsistency').length === 0 ? (
                  <p className="text-slate-500 text-center py-8">No inconsistencies detected.</p>
                ) : (
                  <div className="space-y-4">
                    {insights.filter(i => i.insight_type === 'Inconsistency').map(insight => (
                      <div key={insight.id} className="p-4 bg-red-50/30 border border-red-100 rounded-lg">
                        <div className="flex justify-between items-start mb-2">
                          <h4 className="font-bold text-slate-900 text-sm">{insight.title}</h4>
                          <span className={`text-xs font-bold px-2 py-1 rounded ${insight.severity === 'high' ? 'bg-red-100 text-critical' : 'bg-orange-100 text-warning'}`}>
                            {insight.severity.toUpperCase()}
                          </span>
                        </div>
                        <p className="text-sm text-slate-700">{insight.description}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Missing Information */}
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm flex flex-col">
              <div className="px-6 py-4 border-b border-slate-200 bg-orange-50/50 flex items-center gap-2">
                <HelpCircle className="w-5 h-5 text-warning" />
                <h3 className="font-bold text-slate-900">Missing Information</h3>
              </div>
              <div className="p-6 flex-1">
                {insights.filter(i => i.insight_type === 'Missing Info').length === 0 ? (
                  <p className="text-slate-500 text-center py-8">No missing information detected.</p>
                ) : (
                  <div className="space-y-4">
                    {insights.filter(i => i.insight_type === 'Missing Info').map(insight => (
                      <div key={insight.id} className="p-4 bg-orange-50/30 border border-orange-100 rounded-lg">
                        <div className="flex justify-between items-start mb-2">
                          <h4 className="font-bold text-slate-900 text-sm">{insight.title}</h4>
                          <span className="text-xs font-bold px-2 py-1 rounded bg-slate-100 text-slate-600">
                            REQUIRED
                          </span>
                        </div>
                        <p className="text-sm text-slate-700">{insight.description}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
            
            {/* Medication Changes */}
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm flex flex-col md:col-span-2">
              <div className="px-6 py-4 border-b border-slate-200 bg-blue-50/50 flex items-center gap-2">
                <Brain className="w-5 h-5 text-brand-600" />
                <h3 className="font-bold text-slate-900">Medication & Care Changes</h3>
              </div>
              <div className="p-6">
                 {insights.filter(i => i.insight_type === 'Medication Change').length === 0 ? (
                  <p className="text-slate-500 text-center py-8">No critical medication changes detected.</p>
                ) : (
                  <div className="space-y-4">
                    {insights.filter(i => i.insight_type === 'Medication Change').map(insight => (
                      <div key={insight.id} className="p-4 bg-blue-50/30 border border-blue-100 rounded-lg flex items-start gap-3">
                        <AlertCircle className="w-5 h-5 text-brand-500 mt-0.5 shrink-0" />
                        <div>
                          <h4 className="font-bold text-slate-900 text-sm mb-1">{insight.title}</h4>
                          <p className="text-sm text-slate-700">{insight.description}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

          </div>
        </main>
      </div>
    </div>
  );
};

export default AIInsightsPage;
