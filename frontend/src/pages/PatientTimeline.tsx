import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import Header from '../components/Header';
import { Clock, Filter } from 'lucide-react';
import api from '../services/api';

const PatientTimeline = () => {
  const { id } = useParams();
  const [patient, setPatient] = useState<any>(null);
  const [timeline, setTimeline] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('All');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [patientRes, timelineRes] = await Promise.all([
          api.get(`/patients/${id}`),
          api.get(`/patients/timeline/${id}`)
        ]);
        setPatient(patientRes.data);
        setTimeline(timelineRes.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [id]);

  if (loading) return <div className="flex h-screen items-center justify-center">Loading...</div>;

  const filteredTimeline = filter === 'All' ? timeline : timeline.filter(t => t.category === filter);

  return (
    <div className="flex h-screen bg-slate-50 overflow-hidden">
      <Sidebar />
      <div className="flex-1 ml-64 flex flex-col h-screen overflow-hidden">
        <Header />
        
        <main className="flex-1 overflow-y-auto p-8">
          <div className="mb-6 flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-slate-900">Unified Patient Timeline</h1>
              <p className="text-slate-500 mt-1">Chronological history for {patient?.name}</p>
            </div>
            
            <div className="flex items-center gap-2 bg-white px-3 py-2 rounded-lg border border-slate-200 shadow-sm">
              <Filter className="w-4 h-4 text-slate-400" />
              <select 
                className="bg-transparent text-sm font-medium text-slate-700 focus:outline-none"
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
              >
                <option value="All">All Events</option>
                <option value="Consultation">Consultations</option>
                <option value="Lab Report">Lab Reports</option>
                <option value="Prescription">Prescriptions</option>
                <option value="Allergy">Allergies</option>
              </select>
            </div>
          </div>

          <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-8">
            <div className="space-y-8">
              {filteredTimeline.map((event, i) => (
                <div key={i} className="flex gap-6 relative">
                  <div className="flex flex-col items-center">
                    <div className={`w-4 h-4 rounded-full border-2 border-white shadow-sm mt-1 z-10 ${
                      event.badge_color === 'red' ? 'bg-critical' :
                      event.badge_color === 'green' ? 'bg-success' :
                      event.badge_color === 'orange' ? 'bg-warning' : 'bg-brand-500'
                    }`} />
                    {i < filteredTimeline.length - 1 && <div className="absolute top-5 bottom-[-2rem] left-[7px] w-0.5 bg-slate-200"></div>}
                  </div>
                  <div className="pb-4 w-full">
                    <div className="flex justify-between items-start mb-1">
                      <p className="text-sm font-bold text-brand-600">{event.date}</p>
                      <span className={`px-2.5 py-0.5 rounded-md text-xs font-semibold ${
                        event.category === 'Allergy' ? 'bg-red-50 text-red-700 border border-red-100' :
                        event.category === 'Prescription' ? 'bg-green-50 text-green-700 border border-green-100' :
                        'bg-slate-100 text-slate-700 border border-slate-200'
                      }`}>
                        {event.category}
                      </span>
                    </div>
                    <div className="bg-slate-50 p-4 rounded-xl border border-slate-100 mt-2">
                      <h4 className="text-lg font-bold text-slate-900">{event.title}</h4>
                      <p className="text-slate-700 mt-2">{event.description}</p>
                      <div className="flex items-center gap-2 mt-4 text-xs text-slate-500 font-medium">
                        <Clock className="w-3.5 h-3.5" /> Source: {event.hospital || 'Unknown'}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
              {filteredTimeline.length === 0 && (
                <div className="text-center py-12 text-slate-500">No events found for this filter.</div>
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default PatientTimeline;
