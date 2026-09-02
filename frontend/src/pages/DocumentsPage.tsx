import React, { useState, useRef, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import Header from '../components/Header';
import { UploadCloud, File, CheckCircle2, Loader2, AlertCircle, Trash2 } from 'lucide-react';
import api from '../services/api';

const DocumentsPage = () => {
  const { id } = useParams();
  const [documents, setDocuments] = useState<any[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadStatusText, setUploadStatusText] = useState('Uploading document...');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    fetchDocuments();
  }, [id]);

  const fetchDocuments = async () => {
    try {
      const res = await api.get(`/documents/?patient_id=${id}`);
      setDocuments(res.data);
    } catch (e) {
      console.error("Failed to fetch documents", e);
    }
  };

  const pollDocumentStatus = (docId: string | number) => {
    const interval = setInterval(async () => {
      try {
        const res = await api.get(`/documents/${docId}`);
        const currentDoc = res.data;
        
        if (currentDoc.status === 'extracting_text') {
          setUploadStatusText('Extracting text via OCR...');
        } else if (currentDoc.status === 'ai_extraction') {
          setUploadStatusText('Identifying medical entities...');
        } else if (currentDoc.status === 'updating_timeline') {
          setUploadStatusText('Updating patient timeline...');
        } else if (currentDoc.status === 'consistency_check') {
          setUploadStatusText('Running clinical consistency checks...');
        } else if (currentDoc.status === 'processed' || currentDoc.status === 'failed') {
          clearInterval(interval);
          setUploading(false);
          fetchDocuments();
        }
      } catch (err) {
        clearInterval(interval);
        setUploading(false);
        fetchDocuments();
      }
    }, 1500);
  };

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    const file = e.target.files[0];
    setErrorMsg(null);

    // Client-side file validation
    const allowedTypes = ['.pdf', '.jpg', '.jpeg', '.png'];
    const ext = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
    if (!allowedTypes.includes(ext)) {
      setErrorMsg(`Unsupported file type '${ext}'. Please select a PDF, JPG, JPEG, or PNG file.`);
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setErrorMsg('File size exceeds the 10 MB maximum limit.');
      return;
    }

    setUploading(true);
    setUploadStatusText('Uploading document to server...');

    const formData = new FormData();
    formData.append('patient_id', id as string);
    formData.append('file', file);

    try {
      // 1. Upload file
      const uploadRes = await api.post('/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      const docId = uploadRes.data.id;

      // 2. Trigger real AI processing pipeline
      setUploadStatusText('Processing document...');
      await api.post(`/ai/process-document?document_id=${docId}`);

      // 3. Poll backend for actual status updates
      pollDocumentStatus(docId);
    } catch (err: any) {
      console.error("Document upload error:", err);
      const detail = err.response?.data?.detail || 'Document upload failed. Please try again.';
      setErrorMsg(detail);
      setUploading(false);
    } finally {
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleDelete = async (docId: string | number) => {
    if (!window.confirm("Are you sure you want to delete this document?")) return;
    try {
      await api.delete(`/documents/${docId}`);
      fetchDocuments();
    } catch (err) {
      console.error("Delete document failed:", err);
    }
  };

  return (
    <div className="flex h-screen bg-slate-50 overflow-hidden">
      <Sidebar />
      <div className="flex-1 ml-64 flex flex-col h-screen overflow-hidden">
        <Header />

        <main className="flex-1 overflow-y-auto p-8">
          <div className="mb-6">
            <h1 className="text-2xl font-bold text-slate-900">Medical Documents</h1>
            <p className="text-slate-500 mt-1">Upload and manage patient medical records</p>
          </div>

          {errorMsg && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-700 rounded-xl flex items-center gap-3">
              <AlertCircle className="w-5 h-5 shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="md:col-span-2">
              <div
                className={`border-2 border-dashed rounded-xl p-10 text-center transition-all ${
                  uploading
                    ? 'bg-slate-50 border-slate-300'
                    : 'bg-white border-brand-300 hover:bg-brand-50 hover:border-brand-500 cursor-pointer'
                }`}
                onClick={() => !uploading && fileInputRef.current?.click()}
              >
                {!uploading ? (
                  <>
                    <UploadCloud className="w-12 h-12 text-brand-500 mx-auto mb-4" />
                    <h3 className="text-lg font-bold text-slate-900 mb-1">Upload Medical Records</h3>
                    <p className="text-slate-500 text-sm mb-4">Support for PDF, JPG, JPEG, PNG up to 10MB</p>
                    <button className="px-5 py-2 bg-brand-600 text-white font-medium rounded-lg hover:bg-brand-700 transition-colors">
                      + Select Files
                    </button>
                    <input
                      type="file"
                      className="hidden"
                      ref={fileInputRef}
                      onChange={handleUpload}
                      accept=".pdf,.png,.jpg,.jpeg"
                    />
                  </>
                ) : (
                  <div className="py-8">
                    <Loader2 className="w-12 h-12 text-brand-500 mx-auto mb-4 animate-spin" />
                    <h3 className="text-lg font-bold text-slate-900 mb-2">Processing Document...</h3>
                    <p className="text-sm font-medium text-slate-600">{uploadStatusText}</p>
                  </div>
                )}
              </div>
            </div>

            <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
              <h3 className="text-lg font-bold text-slate-900 mb-4">Supported Pipeline</h3>
              <ul className="space-y-3 text-sm text-slate-600">
                <li className="flex gap-2"><CheckCircle2 className="w-5 h-5 text-success shrink-0"/> PyMuPDF PDF Text Extraction</li>
                <li className="flex gap-2"><CheckCircle2 className="w-5 h-5 text-success shrink-0"/> Image OCR Processing</li>
                <li className="flex gap-2"><CheckCircle2 className="w-5 h-5 text-success shrink-0"/> Entity & Medication Parsing</li>
                <li className="flex gap-2"><CheckCircle2 className="w-5 h-5 text-success shrink-0"/> Timeline Synchronization</li>
                <li className="flex gap-2"><CheckCircle2 className="w-5 h-5 text-success shrink-0"/> Clinical Consistency Checks</li>
              </ul>
            </div>
          </div>

          <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-200 bg-slate-50">
              <h3 className="font-bold text-slate-900">Uploaded Documents</h3>
            </div>
            <div className="divide-y divide-slate-100">
              {documents.length === 0 ? (
                <div className="p-8 text-center text-slate-500">No documents uploaded yet for this patient.</div>
              ) : (
                documents.map(doc => (
                  <div key={doc.id} className="p-4 px-6 flex items-center justify-between hover:bg-slate-50">
                    <div className="flex items-center gap-4">
                      <div className="p-3 bg-blue-50 text-brand-600 rounded-lg">
                        <File className="w-6 h-6" />
                      </div>
                      <div>
                        <h4 className="font-bold text-slate-900 text-sm">{doc.file_name}</h4>
                        <p className="text-xs text-slate-500 mt-1">
                          Uploaded: {doc.upload_date ? new Date(doc.upload_date).toLocaleDateString() : 'Recent'} • {doc.document_type || 'Record'}
                        </p>
                        {doc.status === 'failed' && (
                          <p className="text-xs text-red-600 font-medium mt-1">
                            {doc.error_message || "Text could not be reliably extracted. Manual review required."}
                          </p>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      {doc.status === 'processed' ? (
                        <span className="px-3 py-1 bg-success/10 text-success text-xs font-semibold rounded-full flex items-center gap-1">
                          <CheckCircle2 className="w-4 h-4"/> Processed
                        </span>
                      ) : doc.status === 'failed' ? (
                        <span className="px-3 py-1 bg-critical/10 text-critical text-xs font-semibold rounded-full flex items-center gap-1">
                          <AlertCircle className="w-4 h-4"/> Failed
                        </span>
                      ) : (
                        <span className="px-3 py-1 bg-warning/10 text-warning text-xs font-semibold rounded-full flex items-center gap-1">
                          <Loader2 className="w-4 h-4 animate-spin"/> Processing
                        </span>
                      )}
                      <button onClick={() => handleDelete(doc.id)} className="text-slate-400 hover:text-red-600 p-1">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
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

export default DocumentsPage;

