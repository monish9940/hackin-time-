import { useEffect, useState } from 'react';
import { useParams, NavLink } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import Header from '../components/Header';
import { Activity, FileText, Pill, Stethoscope, Send } from 'lucide-react';
import api from '../services/api';

const PatientProfile = () => {
  const { id } = useParams();
  const [patient, setPatient] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [timeline, setTimeline] = useState<any[]>([]);
  const [notes, setNotes] = useState<any[]>([]);
  const [newNote, setNewNote] = useState('');
  const [submittingNote, setSubmittingNote] = useState(false);

  const fetchPatientData = async () => {
    try {
      const [patientRes, timelineRes, notesRes] = await Promise.all([
        api.get(`/patients/${id}`),
        api.get(`/patients/timeline/${id}`),
        api.get(`/patients/notes/${id}`)
      ]);
      setPatient(patientRes.data);
      setTimeline(timelineRes.data);
      setNotes(notesRes.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPatientData();
  }, [id]);

  const handleAddNote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newNote.trim()) return;
    setSubmittingNote(true);
    try {
      await api.post(`/patients/notes/${id}`, { note: newNote });
      setNewNote('');
      const notesRes = await api.get(`/patients/notes/${id}`);
      setNotes(notesRes.data);
    } catch (err) {
      console.error("Failed to post note:", err);
    } finally {
      setSubmittingNote(false);
    }
  };

  if (loading) return <div className="flex h-screen items-center justify-center bg-slate-50">Loading patient data...</div>;
  if (!patient) return <div className="flex h-screen items-center justify-center bg-slate-50">Patient not found</div>;

  const tabs = [
    { name: 'Overview', path: `/patient/${id}` },
    { name: 'Timeline', path: `/patient/${id}/timeline` },
    { name: 'Documents', path: `/patient/${id}/documents` },
    { name: 'Medications', path: `/patient/${id}/medications` },
    { name: 'AI Insights', path: `/patient/${id}/insights` },
  ];

  return (
    <div className="flex h-screen bg-slate-50 overflow-hidden">
      <Sidebar />
      <div className="flex-1 ml-64 flex flex-col h-screen overflow-hidden">
        <Header />
        
        <main className="flex-1 overflow-y-auto p-8">
          {/* Patient Banner */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm mb-6 overflow-hidden">
            <div className="p-6 flex items-center justify-between">
              <div className="flex items-center gap-6">
                <div className="w-16 h-16 bg-brand-100 text-brand-600 rounded-2xl flex items-center justify-center text-2xl font-bold">
                  {patient.name.charAt(0)}
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-slate-900">{patient.name}</h1>
                  <div className="flex items-center gap-4 mt-2 text-sm text-slate-600">
                    <span className="font-mono bg-slate-100 px-2 py-0.5 rounded text-slate-700">{patient.patient_id}</span>
                    <span>{patient.age} years old</span>
                    <span>•</span>
                    <span>{patient.gender}</span>
                    <span>•</span>
                    <span className="flex items-center gap-1"><Activity className="w-4 h-4 text-critical"/> Blood Group: {patient.blood_group}</span>
                  </div>
                </div>
              </div>
              
              <div className="text-right">
                <div className="text-sm text-slate-500 mb-1">AI Review Priority</div>
                <div className={`text-2xl font-bold ${
                  patient.review_priority_score > 70 ? 'text-critical' : 
                  patient.review_priority_score > 30 ? 'text-warning' : 'text-success'
                }`}>
                  {patient.review_priority_score} / 100
                </div>
              </div>
            </div>
            
            {/* Tabs */}
            <div className="border-t border-slate-200 px-6 flex gap-8">
              {tabs.map(tab => (
                <NavLink
                  key={tab.name}
                  to={tab.path}
                  end={tab.name === 'Overview'}
                  className={({ isActive }) =>
                    `py-4 text-sm font-medium border-b-2 transition-colors ${
                      isActive ? 'border-brand-600 text-brand-600' : 'border-transparent text-slate-500 hover:text-slate-900'
                    }`
                  }
                >
                  {tab.name}
                </NavLink>
              ))}
            </div>
          </div>

          {/* Overview Content */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="col-span-2">
              <h2 className="text-xl font-bold text-slate-900 mb-4">Recent Activity</h2>
              <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
                <div className="space-y-6">
                  {timeline.slice(0, 5).map((event, i) => (
                    <div key={i} className="flex gap-4">
                      <div className="flex flex-col items-center">
                        <div className={`w-3 h-3 rounded-full mt-1.5 ${
                          event.badge_color === 'red' ? 'bg-critical' :
                          event.badge_color === 'green' ? 'bg-success' :
                          event.badge_color === 'orange' ? 'bg-warning' : 'bg-brand-500'
                        }`} />
                        {i < 4 && <div className="w-px h-full bg-slate-200 mt-2"></div>}
                      </div>
                      <div className="pb-6">
                        <p className="text-sm font-bold text-slate-500 mb-1">{event.date}</p>
                        <h4 className="text-base font-bold text-slate-900">{event.title}</h4>
                        <p className="text-sm text-slate-600 mt-1">{event.description}</p>
                        <p className="text-xs text-slate-400 mt-1">{event.hospital}</p>
                      </div>
                    </div>
                  ))}
                  {timeline.length === 0 && <p className="text-slate-500">No recent activity for this patient.</p>}
                </div>
              </div>
            </div>
            
            <div>
              <h2 className="text-xl font-bold text-slate-900 mb-4">Health Summary</h2>
              <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-4 space-y-4">
                <div className="flex items-center gap-3 p-3 bg-slate-50 rounded-lg">
                  <FileText className="w-5 h-5 text-brand-500" />
                  <div>
                    <p className="text-sm font-bold text-slate-900">{patient.records_count || 0}</p>
                    <p className="text-xs text-slate-500">Total Records</p>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-3 bg-slate-50 rounded-lg">
                  <Pill className="w-5 h-5 text-success" />
                  <div>
                    <p className="text-sm font-bold text-slate-900">{patient.active_medications_count || 0}</p>
                    <p className="text-xs text-slate-500">Active Medications</p>
                  </div>
                </div>
                <div className="mt-4 p-4 bg-blue-50 border border-blue-100 rounded-lg">
                  <h4 className="text-sm font-bold text-blue-900 mb-1">AI Assistant Note</h4>
                  <p className="text-xs text-blue-800">
                    Patient review priority score: {patient.review_priority_score || 0}. Check the AI Insights tab for flagged items.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Doctor Notes Section */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
            <h2 className="text-xl font-bold text-slate-900 mb-4 flex items-center gap-2">
              <Stethoscope className="w-5 h-5 text-brand-600" /> Doctor Clinical Notes
            </h2>

            <form onSubmit={handleAddNote} className="mb-6">
              <div className="flex gap-3">
                <textarea
                  rows={2}
                  value={newNote}
                  onChange={(e) => setNewNote(e.target.value)}
                  placeholder="Enter clinical observations, treatment recommendations, or progress notes..."
                  className="flex-1 p-3 border border-slate-300 rounded-xl outline-none focus:ring-2 focus:ring-brand-500 text-sm"
                />
                <button
                  type="submit"
                  disabled={submittingNote || !newNote.trim()}
                  className="px-5 py-2 bg-brand-600 text-white font-semibold rounded-xl hover:bg-brand-700 disabled:opacity-50 flex items-center gap-2 shrink-0 self-end"
                >
                  <Send className="w-4 h-4" /> Save Note
                </button>
              </div>
            </form>

            <div className="space-y-4">
              {notes.length === 0 ? (
                <p className="text-sm text-slate-500">No doctor notes recorded yet.</p>
              ) : (
                notes.map((noteItem) => (
                  <div key={noteItem.id} className="p-4 bg-slate-50 rounded-xl border border-slate-200">
                    <div className="flex justify-between items-center mb-1">
                      <p className="text-xs font-bold text-brand-600">{noteItem.author_name}</p>
                      <p className="text-xs text-slate-400">
                        {noteItem.created_at ? new Date(noteItem.created_at).toLocaleString() : 'Recent'}
                      </p>
                    </div>
                    <p className="text-sm text-slate-800 whitespace-pre-wrap">{noteItem.note}</p>
                  </div>
                ))
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default PatientProfile;

