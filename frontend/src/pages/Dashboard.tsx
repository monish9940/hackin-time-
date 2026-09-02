import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import Header from '../components/Header';
import { Users, FileText, Brain, AlertCircle, ChevronRight, UserPlus, X } from 'lucide-react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';

const Dashboard = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [patients, setPatients] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [newPatient, setNewPatient] = useState({
    patient_id: '',
    name: '',
    age: '',
    gender: 'Male',
    blood_group: 'O+'
  });
  const [addError, setAddError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const fetchPatients = async () => {
    try {
      const response = await api.get('/patients/');
      setPatients(response.data);
    } catch (err) {
      console.error("Failed to fetch patients", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPatients();
  }, []);

  const handleCreatePatient = async (e: React.FormEvent) => {
    e.preventDefault();
    setAddError('');
    setSubmitting(true);
    try {
      await api.post('/patients/', {
        patient_id: newPatient.patient_id,
        name: newPatient.name,
        age: parseInt(newPatient.age) || 30,
        gender: newPatient.gender,
        blood_group: newPatient.blood_group
      });
      setShowAddModal(false);
      setNewPatient({ patient_id: '', name: '', age: '', gender: 'Male', blood_group: 'O+' });
      fetchPatients();
    } catch (err: any) {
      setAddError(err.response?.data?.detail || 'Failed to create patient record.');
    } finally {
      setSubmitting(false);
    }
  };

  const totalRecords = patients.reduce((acc, p) => acc + (p.records_count || 0), 0);
  const pendingReviews = patients.filter(p => p.review_status && p.review_status !== 'Normal').length;

  const stats = [
    { title: 'Total Patients', value: patients.length, icon: Users, color: 'text-brand-600', bg: 'bg-brand-50' },
    { title: 'Records Processed', value: totalRecords, icon: FileText, color: 'text-brand-600', bg: 'bg-brand-50' },
    { title: 'Active Cases', value: patients.length, icon: Brain, color: 'text-brand-600', bg: 'bg-brand-50' },
    { title: 'Pending Reviews', value: pendingReviews, icon: AlertCircle, color: 'text-warning', bg: 'bg-orange-50' },
  ];

  return (
    <div className="flex h-screen bg-slate-50 overflow-hidden">
      <Sidebar />
      <div className="flex-1 ml-64 flex flex-col h-screen overflow-hidden">
        <Header />
        
        <main className="flex-1 overflow-y-auto p-8">
          <div className="mb-8 flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-slate-900">
                Welcome, {user?.full_name || 'Clinician'}
              </h1>
              <p className="text-slate-500 mt-1">Here is your patient care overview.</p>
            </div>
            <button
              onClick={() => setShowAddModal(true)}
              className="flex items-center gap-2 px-5 py-2.5 bg-brand-600 text-white font-semibold rounded-xl hover:bg-brand-700 transition-colors shadow-sm"
            >
              <UserPlus className="w-5 h-5" /> Add Patient
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            {stats.map((stat, i) => (
              <div key={i} className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex items-center gap-4">
                <div className={`p-4 rounded-lg ${stat.bg}`}>
                  <stat.icon className={`w-8 h-8 ${stat.color}`} />
                </div>
                <div>
                  <p className="text-sm font-medium text-slate-500">{stat.title}</p>
                  <p className="text-2xl font-bold text-slate-900">{stat.value}</p>
                </div>
              </div>
            ))}
          </div>

          <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="px-6 py-5 border-b border-slate-200 flex justify-between items-center bg-slate-50">
              <h2 className="text-lg font-bold text-slate-900">Patients</h2>
              <span className="text-xs font-semibold px-2.5 py-1 bg-slate-200 text-slate-700 rounded-full">
                {patients.length} Patient{patients.length !== 1 ? 's' : ''}
              </span>
            </div>
            
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead className="bg-white border-b border-slate-200">
                  <tr>
                    <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">Patient ID</th>
                    <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">Patient Name</th>
                    <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">Age / Gender</th>
                    <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">Active Meds</th>
                    <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">Review Status</th>
                    <th className="px-6 py-4"></th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 bg-white">
                  {loading ? (
                    <tr><td colSpan={6} className="text-center py-8 text-slate-500">Loading patient data...</td></tr>
                  ) : patients.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="text-center py-12">
                        <Users className="w-12 h-12 text-slate-300 mx-auto mb-3" />
                        <p className="text-slate-600 font-semibold mb-1">No patients found</p>
                        <p className="text-slate-400 text-sm mb-4">Click below to create your first patient record in MongoDB.</p>
                        <button
                          onClick={() => setShowAddModal(true)}
                          className="px-4 py-2 bg-brand-600 text-white font-medium rounded-lg text-sm hover:bg-brand-700"
                        >
                          + Add Patient
                        </button>
                      </td>
                    </tr>
                  ) : (
                    patients.map((patient) => (
                      <tr 
                        key={patient.id} 
                        onClick={() => navigate(`/patient/${patient.id}`)}
                        className="hover:bg-slate-50 cursor-pointer transition-colors"
                      >
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-900">{patient.patient_id}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-brand-600">{patient.name}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">{patient.age} / {patient.gender}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">{patient.active_medications_count || 0}</td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                            patient.review_status === 'Normal' ? 'bg-success/10 text-success' : 
                            patient.review_status === 'Critical Review' ? 'bg-critical/10 text-critical' : 
                            'bg-warning/10 text-warning'
                          }`}>
                            {patient.review_status || 'Normal'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <ChevronRight className="w-5 h-5 text-slate-400" />
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </main>
      </div>

      {/* Add Patient Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-xl border border-slate-100">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-bold text-slate-900">Add New Patient</h3>
              <button onClick={() => setShowAddModal(false)} className="text-slate-400 hover:text-slate-600">
                <X className="w-6 h-6" />
              </button>
            </div>

            {addError && <div className="mb-4 p-3 bg-red-50 text-red-600 text-sm rounded-lg">{addError}</div>}

            <form onSubmit={handleCreatePatient} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Medical Patient ID *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. PAT-2026-001"
                  value={newPatient.patient_id}
                  onChange={(e) => setNewPatient({ ...newPatient, patient_id: e.target.value })}
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg outline-none focus:ring-2 focus:ring-brand-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Full Name *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Eleanor Vance"
                  value={newPatient.name}
                  onChange={(e) => setNewPatient({ ...newPatient, name: e.target.value })}
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg outline-none focus:ring-2 focus:ring-brand-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Age *</label>
                  <input
                    type="number"
                    required
                    min="0"
                    max="120"
                    placeholder="45"
                    value={newPatient.age}
                    onChange={(e) => setNewPatient({ ...newPatient, age: e.target.value })}
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg outline-none focus:ring-2 focus:ring-brand-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Gender *</label>
                  <select
                    value={newPatient.gender}
                    onChange={(e) => setNewPatient({ ...newPatient, gender: e.target.value })}
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg outline-none focus:ring-2 focus:ring-brand-500 bg-white"
                  >
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Other">Other</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Blood Group</label>
                <select
                  value={newPatient.blood_group}
                  onChange={(e) => setNewPatient({ ...newPatient, blood_group: e.target.value })}
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg outline-none focus:ring-2 focus:ring-brand-500 bg-white"
                >
                  <option value="O+">O+</option>
                  <option value="O-">O-</option>
                  <option value="A+">A+</option>
                  <option value="A-">A-</option>
                  <option value="B+">B+</option>
                  <option value="B-">B-</option>
                  <option value="AB+">AB+</option>
                  <option value="AB-">AB-</option>
                </select>
              </div>

              <div className="flex gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="w-1/2 py-2.5 border border-slate-300 text-slate-700 font-semibold rounded-lg hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="w-1/2 py-2.5 bg-brand-600 text-white font-semibold rounded-lg hover:bg-brand-700 disabled:opacity-50"
                >
                  {submitting ? 'Creating...' : 'Save Patient'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;

