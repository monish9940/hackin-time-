import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import Header from '../components/Header';
import { Pill, TrendingUp, AlertTriangle, CheckCircle2 } from 'lucide-react';
import api from '../services/api';

const MedicationsPage = () => {
  const { id } = useParams();
  const [medications, setMedications] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMedications = async () => {
      try {
        const res = await api.get(`/patients/medications/${id}`);
        setMedications(res.data);
      } catch (e) { console.error(e); } finally {
        setLoading(false);
      }
    };
    fetchMedications();
  }, [id]);

  if (loading) return <div className="flex h-screen items-center justify-center">Loading medications...</div>;

  const active = medications.filter(m => m.status === 'Active');
  const discontinued = medications.filter(m => m.status !== 'Active');

  return (
    <div className="flex h-screen bg-slate-50 overflow-hidden">
      <Sidebar />
      <div className="flex-1 ml-64 flex flex-col h-screen overflow-hidden">
        <Header />
        
        <main className="flex-1 overflow-y-auto p-8">
          <div className="mb-6">
            <h1 className="text-2xl font-bold text-slate-900">Medication History</h1>
            <p className="text-slate-500 mt-1">Track all prescribed medications and dosage changes</p>
          </div>

          {/* Active Medications */}
          <div className="mb-8">
            <h2 className="text-lg font-bold text-slate-900 mb-4 flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5 text-success" /> Active Medications ({active.length})
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {active.map(med => (
                <div key={med.id} className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 hover:shadow-md transition-shadow">
                  <div className="flex justify-between items-start mb-3">
                    <div className="flex items-center gap-3">
                      <div className="p-2.5 bg-green-50 text-success rounded-lg">
                        <Pill className="w-6 h-6" />
                      </div>
                      <div>
                        <h3 className="font-bold text-slate-900">{med.name}</h3>
                        <p className="text-sm text-slate-500">{med.generic_name}</p>
                      </div>
                    </div>
                    <span className="px-2.5 py-1 bg-green-50 text-success text-xs font-bold rounded-full">Active</span>
                  </div>
                  <div className="grid grid-cols-2 gap-3 mt-4">
                    <div className="bg-slate-50 p-3 rounded-lg">
                      <p className="text-xs text-slate-500 mb-1">Dosage</p>
                      <p className="text-sm font-bold text-slate-900">{med.dosage}</p>
                    </div>
                    <div className="bg-slate-50 p-3 rounded-lg">
                      <p className="text-xs text-slate-500 mb-1">Frequency</p>
                      <p className="text-sm font-bold text-slate-900">{med.frequency}</p>
                    </div>
                    <div className="bg-slate-50 p-3 rounded-lg">
                      <p className="text-xs text-slate-500 mb-1">Prescribed By</p>
                      <p className="text-sm font-bold text-slate-900">{med.prescribed_by}</p>
                    </div>
                    <div className="bg-slate-50 p-3 rounded-lg">
                      <p className="text-xs text-slate-500 mb-1">Start Date</p>
                      <p className="text-sm font-bold text-slate-900">{med.start_date}</p>
                    </div>
                  </div>
                  {med.dosage_history && (
                    <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-100">
                      <div className="flex items-center gap-1 mb-1">
                        <TrendingUp className="w-4 h-4 text-brand-600" />
                        <p className="text-xs font-bold text-blue-800">Dosage History</p>
                      </div>
                      <p className="text-xs text-blue-700">{med.dosage_history}</p>
                    </div>
                  )}
                </div>
              ))}
              {active.length === 0 && <p className="text-slate-500 col-span-2">No active medications.</p>}
            </div>
          </div>

          {/* Discontinued */}
          {discontinued.length > 0 && (
            <div>
              <h2 className="text-lg font-bold text-slate-900 mb-4 flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-warning" /> Discontinued / Past Medications ({discontinued.length})
              </h2>
              <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                <table className="w-full">
                  <thead className="bg-slate-50 border-b border-slate-200">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase">Medication</th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase">Dosage</th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase">Duration</th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {discontinued.map(med => (
                      <tr key={med.id} className="hover:bg-slate-50">
                        <td className="px-6 py-4">
                          <p className="font-bold text-sm text-slate-900">{med.name}</p>
                          <p className="text-xs text-slate-500">{med.generic_name}</p>
                        </td>
                        <td className="px-6 py-4 text-sm text-slate-700">{med.dosage}</td>
                        <td className="px-6 py-4 text-sm text-slate-700">{med.start_date} — {med.end_date || 'N/A'}</td>
                        <td className="px-6 py-4">
                          <span className="px-2.5 py-1 bg-slate-100 text-slate-600 text-xs font-bold rounded-full">{med.status}</span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default MedicationsPage;
