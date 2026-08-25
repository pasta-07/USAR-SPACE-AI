import React, { useState, useEffect } from 'react';
import { 
  Upload as UploadIcon, 
  FileText, 
  CheckCircle2, 
  AlertTriangle, 
  AlertOctagon, 
  Plus, 
  Trash2, 
  Edit3, 
  ShieldCheck, 
  RotateCcw, 
  Sparkles, 
  Calendar, 
  Clock, 
  Building2, 
  X,
  FileCheck,
  Zap,
  Download
} from 'lucide-react';
import confetti from 'canvas-confetti';
import { api } from '../services/api';

export default function AdminPage({ onRefreshAvailability }) {
  const [activeSubTab, setActiveSubTab] = useState('upload'); // 'upload' | 'review' | 'conflicts' | 'exceptions'
  
  // Upload state
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadProgressStep, setUploadProgressStep] = useState(0);
  const [uploadResult, setUploadResult] = useState(null);
  const [uploadError, setUploadError] = useState(null);

  // Review state
  const [reviewUploadId, setReviewUploadId] = useState(null);
  const [reviewData, setReviewData] = useState(null);
  const [editingEntry, setEditingEntry] = useState(null);
  const [newEntryModal, setNewEntryModal] = useState(false);

  // Conflicts state
  const [conflicts, setConflicts] = useState([]);
  const [loadingConflicts, setLoadingConflicts] = useState(false);

  // Exceptions state
  const [exceptions, setExceptions] = useState([]);
  const [newExceptionModal, setNewExceptionModal] = useState(false);
  const [exceptionForm, setExceptionForm] = useState({
    exception_date: new Date().toISOString().split('T')[0],
    classroom_id: 1,
    exception_type: 'CANCELLED_CLASS',
    start_time: '10:00',
    end_time: '11:00',
    reason: 'Guest Lecture / Room Maintenance',
    alternate_classroom_id: null
  });

  const [classroomsList, setClassroomsList] = useState([]);

  // Load classrooms for dropdowns
  useEffect(() => {
    api.getAvailableNow()
      .then(res => setClassroomsList(res.classrooms || []))
      .catch(err => console.error(err));
  }, []);

  // Load conflicts
  const loadConflicts = () => {
    setLoadingConflicts(true);
    api.getConflicts()
      .then(setConflicts)
      .catch(err => console.error(err))
      .finally(() => setLoadingConflicts(false));
  };

  // Load exceptions
  const loadExceptions = () => {
    api.getExceptions()
      .then(setExceptions)
      .catch(err => console.error(err));
  };

  useEffect(() => {
    if (activeSubTab === 'conflicts') loadConflicts();
    if (activeSubTab === 'exceptions') loadExceptions();
  }, [activeSubTab]);

  // Handle PDF file upload
  const handleFileUpload = async (file) => {
    if (!file || !file.name.toLowerCase().endsWith('.pdf')) {
      setUploadError('Please upload a valid PDF timetable file.');
      return;
    }

    setUploading(true);
    setUploadError(null);
    setUploadProgressStep(1);

    // Simulate animated step transitions for realistic feedback
    const timer1 = setTimeout(() => setUploadProgressStep(2), 400);
    const timer2 = setTimeout(() => setUploadProgressStep(3), 800);
    const timer3 = setTimeout(() => setUploadProgressStep(4), 1200);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('academic_year', '2026-27');

    try {
      const res = await api.uploadTimetable(formData);
      setUploadProgressStep(7);
      setUploadResult(res);
      setReviewUploadId(res.upload_id);
      // Load review screen
      loadReviewData(res.upload_id);
      setActiveSubTab('review');
    } catch (err) {
      setUploadError(err.message || 'Upload processing failed.');
    } finally {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
      setUploading(false);
    }
  };

  const loadReviewData = (uploadId) => {
    api.getTimetableReview(uploadId)
      .then(setReviewData)
      .catch(err => console.error(err));
  };

  const handleApproveTimetable = async () => {
    if (!reviewUploadId) return;
    try {
      await api.approveUpload(reviewUploadId);
      confetti({
        particleCount: 100,
        spread: 70,
        origin: { y: 0.6 }
      });
      loadReviewData(reviewUploadId);
      onRefreshAvailability();
    } catch (err) {
      alert(err.message || 'Failed to approve timetable.');
    }
  };

  const handleResolveConflict = async (id) => {
    try {
      await api.resolveConflict(id, 'Resolved via Admin Center');
      loadConflicts();
    } catch (err) {
      console.error(err);
    }
  };

  const handleCreateException = async (e) => {
    e.preventDefault();
    try {
      await api.createException({
        ...exceptionForm,
        classroom_id: parseInt(exceptionForm.classroom_id, 10),
        alternate_classroom_id: exceptionForm.alternate_classroom_id ? parseInt(exceptionForm.alternate_classroom_id, 10) : null
      });
      setNewExceptionModal(false);
      loadExceptions();
      onRefreshAvailability();
    } catch (err) {
      alert(err.message || 'Failed to create exception');
    }
  };

  const handleDeleteException = async (id) => {
    try {
      await api.deleteException(id);
      loadExceptions();
      onRefreshAvailability();
    } catch (err) {
      console.error(err);
    }
  };

  const handleResetDatabase = async () => {
    if (window.confirm('Reset database to authentic USAR full 20-page master timetable dataset?')) {
      try {
        await api.resetDatabase();
        alert('Database reset and re-seeded successfully!');
        onRefreshAvailability();
        if (activeSubTab === 'conflicts') loadConflicts();
        if (activeSubTab === 'exceptions') loadExceptions();
      } catch (err) {
        alert(err.message || 'Failed to reset');
      }
    }
  };

  const uploadSteps = [
    "Uploading PDF to secure campus server...",
    "Reading layout & cell coordinates...",
    "Extracting timetable grid...",
    "Detecting classrooms & specialized labs...",
    "Detecting time slots & batches...",
    "Running conflict detection algorithm...",
    "Extraction complete! Ready for review."
  ];

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      
      {/* Admin Top Banner */}
      <div className="p-6 sm:p-8 rounded-3xl bg-gradient-to-r from-slate-900 via-slate-900 to-indigo-950/70 border border-slate-800 shadow-2xl flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-xs font-semibold mb-3">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Admin Command Center</span>
          </div>
          <h2 className="font-['Outfit'] text-2xl sm:text-4xl font-black text-white tracking-tight">
            Timetable Management & Control
          </h2>
          <p className="text-slate-400 text-sm mt-1">
            Upload new timetable PDFs, review extracted data, resolve conflicts, and manage live college exceptions.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleResetDatabase}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-800/80 hover:bg-slate-700 border border-slate-700 text-slate-200 text-xs font-semibold transition-colors"
            title="Reset to pre-loaded 20-page USAR Lantiv timetable"
          >
            <RotateCcw className="w-4 h-4 text-emerald-400" />
            <span>Reset / Re-Seed Dataset</span>
          </button>
        </div>
      </div>

      {/* Admin Sub-Tabs Navigation */}
      <div className="flex flex-wrap items-center gap-2 p-1.5 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl">
        <button
          onClick={() => setActiveSubTab('upload')}
          className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold transition-all ${
            activeSubTab === 'upload'
              ? 'bg-gradient-to-r from-emerald-500/20 to-teal-500/20 text-white border border-emerald-500/40 shadow-md'
              : 'text-slate-400 hover:text-white'
          }`}
        >
          <UploadIcon className="w-4 h-4 text-emerald-400" />
          <span>Upload PDF Timetables</span>
        </button>

        <button
          onClick={() => setActiveSubTab('review')}
          className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold transition-all ${
            activeSubTab === 'review'
              ? 'bg-gradient-to-r from-indigo-500/20 to-purple-500/20 text-white border border-indigo-500/40 shadow-md'
              : 'text-slate-400 hover:text-white'
          }`}
        >
          <FileCheck className="w-4 h-4 text-indigo-400" />
          <span>Timetable Review Screen</span>
          {reviewData && (
            <span className="ml-1 px-1.5 py-0.5 text-[10px] rounded-md bg-indigo-500/30 text-indigo-300">
              {reviewData.entries.length}
            </span>
          )}
        </button>

        <button
          onClick={() => setActiveSubTab('conflicts')}
          className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold transition-all ${
            activeSubTab === 'conflicts'
              ? 'bg-gradient-to-r from-rose-500/20 to-amber-500/20 text-white border border-rose-500/40 shadow-md'
              : 'text-slate-400 hover:text-white'
          }`}
        >
          <AlertOctagon className="w-4 h-4 text-rose-400" />
          <span>Conflict Center</span>
        </button>

        <button
          onClick={() => setActiveSubTab('exceptions')}
          className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold transition-all ${
            activeSubTab === 'exceptions'
              ? 'bg-gradient-to-r from-purple-500/20 to-indigo-500/20 text-white border border-purple-500/40 shadow-md'
              : 'text-slate-400 hover:text-white'
          }`}
        >
          <Calendar className="w-4 h-4 text-purple-400" />
          <span>Campus Exceptions & Holidays</span>
        </button>
      </div>

      {/* Tab 1: PDF Upload */}
      {activeSubTab === 'upload' && (
        <div className="space-y-6">
          
          <div 
            onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
            onDragLeave={() => setDragActive(false)}
            onDrop={(e) => {
              e.preventDefault();
              setDragActive(false);
              if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                handleFileUpload(e.dataTransfer.files[0]);
              }
            }}
            className={`p-10 rounded-3xl border-2 border-dashed transition-all text-center flex flex-col items-center justify-center gap-4 ${
              dragActive 
                ? 'border-emerald-500 bg-emerald-950/20 shadow-2xl shadow-emerald-950/40' 
                : 'border-slate-800 bg-slate-900/60 hover:border-slate-700'
            }`}
          >
            <div className="w-16 h-16 rounded-2xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center justify-center shadow-lg">
              <UploadIcon className="w-8 h-8 animate-bounce" />
            </div>

            <div>
              <h3 className="font-['Outfit'] text-xl font-bold text-white">
                Upload College Timetable PDF
              </h3>
              <p className="text-sm text-slate-400 mt-1 max-w-md mx-auto">
                Drag and drop your department timetable PDF here, or click to browse.
              </p>
            </div>

            <label className="cursor-pointer">
              <input
                type="file"
                accept=".pdf"
                className="hidden"
                onChange={(e) => {
                  if (e.target.files && e.target.files[0]) {
                    handleFileUpload(e.target.files[0]);
                  }
                }}
              />
              <span className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-slate-950 font-bold text-sm shadow-md transition-all inline-block">
                Select PDF File
              </span>
            </label>

            <div className="pt-4 flex items-center gap-4 text-xs text-slate-500">
              <span>Supports: Multi-page PDFs</span>
              <span>•</span>
              <span>Lantiv format compatible</span>
              <span>•</span>
              <span>Auto-room mapping</span>
            </div>
          </div>

          {/* Upload Progress Indicator */}
          {uploading && (
            <div className="p-6 rounded-3xl bg-slate-900 border border-slate-800 shadow-xl space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider">
                  Processing Timetable ({uploadProgressStep}/7)
                </span>
                <span className="text-xs font-mono text-slate-400">Please wait...</span>
              </div>

              {/* Progress bar */}
              <div className="h-2 w-full bg-slate-950 rounded-full overflow-hidden border border-slate-800">
                <div 
                  style={{ width: `${(uploadProgressStep / 7) * 100}%` }}
                  className="h-full bg-gradient-to-r from-emerald-500 via-teal-400 to-indigo-500 transition-all duration-300 rounded-full"
                />
              </div>

              <p className="text-sm font-medium text-slate-300 flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-emerald-400 animate-spin" />
                {uploadSteps[uploadProgressStep - 1] || "Extracting..."}
              </p>
            </div>
          )}

          {uploadError && (
            <div className="p-4 rounded-2xl bg-rose-950/40 border border-rose-500/30 text-rose-300 text-sm">
              {uploadError}
            </div>
          )}

        </div>
      )}

      {/* Tab 2: Timetable Review Screen */}
      {activeSubTab === 'review' && (
        <div className="space-y-6">
          
          <div className="p-6 rounded-3xl bg-slate-900/90 border border-slate-800 shadow-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-3">
                <h3 className="font-['Outfit'] text-2xl font-bold text-white">
                  Timetable Review & Approval
                </h3>
                {reviewData?.upload && (
                  <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${
                    reviewData.upload.status === 'APPROVED' ? 'bg-emerald-500/20 text-emerald-300' : 'bg-amber-500/20 text-amber-300'
                  }`}>
                    {reviewData.upload.status}
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-400 mt-1">
                Verify extracted entries before publishing. You can edit, delete, or add records.
              </p>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={() => setNewEntryModal(true)}
                className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold transition-colors"
              >
                <Plus className="w-4 h-4 text-indigo-400" />
                <span>Add Entry</span>
              </button>

              <button
                onClick={handleApproveTimetable}
                className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-slate-950 font-bold text-xs shadow-lg shadow-emerald-500/20 transition-all"
              >
                <CheckCircle2 className="w-4 h-4" />
                <span>Approve & Publish Live</span>
              </button>
            </div>
          </div>

          {/* Table of Entries */}
          {reviewData?.entries && reviewData.entries.length > 0 ? (
            <div className="overflow-hidden rounded-3xl bg-slate-900/80 border border-slate-800 shadow-xl">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="bg-slate-950 border-b border-slate-800 text-slate-400 uppercase font-mono tracking-wider">
                      <th className="p-3">Dept & Sem</th>
                      <th className="p-3">Day</th>
                      <th className="p-3">Time Slot</th>
                      <th className="p-3">Subject</th>
                      <th className="p-3">Faculty</th>
                      <th className="p-3">Classroom / Lab</th>
                      <th className="p-3 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 font-medium">
                    {reviewData.entries.map((entry) => (
                      <tr key={entry.id} className="hover:bg-slate-800/40 transition-colors">
                        <td className="p-3 text-white font-mono">
                          {entry.department_code}-Sem{entry.semester} {entry.section} {entry.batch ? `(Batch ${entry.batch})` : ''}
                        </td>
                        <td className="p-3 text-slate-300">{entry.day_of_week}</td>
                        <td className="p-3 font-mono text-emerald-400">{entry.start_time} – {entry.end_time}</td>
                        <td className="p-3 text-slate-200">
                          <div>{entry.subject_name}</div>
                          {entry.subject_code && <div className="text-[10px] text-slate-500">{entry.subject_code}</div>}
                        </td>
                        <td className="p-3 text-slate-300">{entry.faculty_name}</td>
                        <td className="p-3 font-semibold text-indigo-300">
                          {entry.room_raw_text}
                          {entry.is_lab && <span className="ml-1.5 px-1.5 py-0.5 rounded text-[9px] bg-purple-500/20 text-purple-300">Lab</span>}
                        </td>
                        <td className="p-3 text-right">
                          <button
                            onClick={async () => {
                              await api.deleteTimetableEntry(entry.id);
                              loadReviewData(reviewUploadId || 1);
                            }}
                            className="p-1.5 rounded-lg hover:bg-rose-500/20 text-slate-500 hover:text-rose-400 transition-colors"
                            title="Delete entry"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ) : (
            <div className="py-16 text-center rounded-3xl bg-slate-900/40 border border-slate-800 text-slate-400">
              No review records loaded. Upload a PDF or select an existing upload.
            </div>
          )}

        </div>
      )}

      {/* Tab 3: Conflict Center */}
      {activeSubTab === 'conflicts' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-['Outfit'] text-xl font-bold text-white flex items-center gap-2">
                <AlertOctagon className="w-5 h-5 text-rose-400" />
                <span>Detected Timetable Conflicts ({conflicts.length})</span>
              </h3>
              <p className="text-xs text-slate-400 mt-1">
                Automated conflict detection prevents room double-booking, faculty overlap, and duplicate entries.
              </p>
            </div>
            
            <button
              onClick={loadConflicts}
              className="px-3 py-1.5 rounded-xl bg-slate-800 text-xs text-slate-300 hover:bg-slate-700"
            >
              Re-Scan Conflicts
            </button>
          </div>

          {loadingConflicts ? (
            <div className="py-12 text-center text-slate-400">Scanning schedule database...</div>
          ) : conflicts.length > 0 ? (
            <div className="space-y-3">
              {conflicts.map((c) => (
                <div 
                  key={c.id} 
                  className={`p-4 rounded-2xl border flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 ${
                    c.resolved 
                      ? 'bg-slate-900/40 border-slate-800 text-slate-400' 
                      : 'bg-rose-950/20 border-rose-500/40 text-slate-200'
                  }`}
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className={`px-2.5 py-0.5 rounded-md text-[10px] font-bold uppercase ${
                        c.conflict_type === 'ROOM_DOUBLE_BOOKING' ? 'bg-rose-500/20 text-rose-300' : 'bg-amber-500/20 text-amber-300'
                      }`}>
                        {c.conflict_type.replace('_', ' ')}
                      </span>
                      {c.resolved && (
                        <span className="px-2 py-0.5 rounded-md text-[10px] font-medium bg-emerald-500/20 text-emerald-400">
                          Resolved
                        </span>
                      )}
                    </div>
                    <p className="text-xs font-medium text-white">{c.description}</p>
                  </div>

                  {!c.resolved && (
                    <button
                      onClick={() => handleResolveConflict(c.id)}
                      className="px-3.5 py-1.5 rounded-xl bg-slate-800 hover:bg-emerald-600 hover:text-slate-950 text-slate-200 text-xs font-bold transition-all shrink-0"
                    >
                      Mark Resolved
                    </button>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="py-16 text-center rounded-3xl bg-slate-900/40 border border-slate-800 text-slate-400 space-y-2">
              <CheckCircle2 className="w-8 h-8 text-emerald-400 mx-auto" />
              <p className="font-bold text-white">Zero Schedule Conflicts Detected!</p>
              <p className="text-xs text-slate-400">All classrooms and faculty allocations are completely conflict-free.</p>
            </div>
          )}
        </div>
      )}

      {/* Tab 4: Campus Exceptions Manager */}
      {activeSubTab === 'exceptions' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-['Outfit'] text-xl font-bold text-white flex items-center gap-2">
                <Calendar className="w-5 h-5 text-purple-400" />
                <span>Live Campus Exceptions & Holidays</span>
              </h3>
              <p className="text-xs text-slate-400 mt-1">
                Mark holidays, cancellations, extra classes, or room changes that immediately modify live room availability.
              </p>
            </div>

            <button
              onClick={() => setNewExceptionModal(true)}
              className="flex items-center gap-1.5 px-4 py-2.5 rounded-xl bg-gradient-to-r from-purple-500 to-indigo-600 hover:from-purple-400 hover:to-indigo-500 text-white text-xs font-bold shadow-lg"
            >
              <Plus className="w-4 h-4" />
              <span>Add Exception</span>
            </button>
          </div>

          {exceptions.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {exceptions.map((exc) => (
                <div key={exc.id} className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-3">
                  <div className="flex items-start justify-between">
                    <span className="px-2.5 py-0.5 rounded-md text-[10px] font-bold uppercase bg-purple-500/20 text-purple-300 border border-purple-500/30">
                      {exc.exception_type.replace('_', ' ')}
                    </span>
                    <button
                      onClick={() => handleDeleteException(exc.id)}
                      className="p-1 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-rose-500/20 transition-colors"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>

                  <div>
                    <h4 className="font-bold text-white text-sm">Room {exc.room_number || 'All'}</h4>
                    <p className="text-xs text-slate-400">{exc.exception_date} ({exc.start_time} – {exc.end_time})</p>
                    <p className="text-xs text-indigo-300 mt-1 font-medium">{exc.reason}</p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="py-16 text-center rounded-3xl bg-slate-900/40 border border-slate-800 text-slate-400 space-y-2">
              <Calendar className="w-8 h-8 text-purple-400 mx-auto" />
              <p className="font-bold text-white">No active exceptions configured.</p>
              <p className="text-xs text-slate-400">Regular college timetable is running normally.</p>
            </div>
          )}
        </div>
      )}

      {/* Exception Creation Modal */}
      {newExceptionModal && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-md flex items-center justify-center p-4">
          <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-['Outfit'] text-lg font-bold text-white">Add Campus Exception</h3>
              <button onClick={() => setNewExceptionModal(false)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateException} className="space-y-3 text-xs">
              <div>
                <label className="text-slate-400 font-semibold block mb-1">Exception Type</label>
                <select
                  value={exceptionForm.exception_type}
                  onChange={(e) => setExceptionForm({ ...exceptionForm, exception_type: e.target.value })}
                  className="w-full p-2.5 rounded-xl bg-slate-950 border border-slate-800 text-white"
                >
                  <option value="CANCELLED_CLASS">Cancelled Class (Room Becomes Available)</option>
                  <option value="EXTRA_CLASS">Extra Class (Room Becomes Occupied)</option>
                  <option value="HOLIDAY">Campus Holiday (All Rooms Free)</option>
                  <option value="ROOM_CHANGE">Room Change / Rescheduled Session</option>
                </select>
              </div>

              <div>
                <label className="text-slate-400 font-semibold block mb-1">Target Classroom</label>
                <select
                  value={exceptionForm.classroom_id}
                  onChange={(e) => setExceptionForm({ ...exceptionForm, classroom_id: e.target.value })}
                  className="w-full p-2.5 rounded-xl bg-slate-950 border border-slate-800 text-white"
                >
                  {classroomsList.map(c => (
                    <option key={c.classroom_id} value={c.classroom_id}>
                      {c.room_number} ({c.building_name})
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-slate-400 font-semibold block mb-1">Date</label>
                  <input
                    type="date"
                    value={exceptionForm.exception_date}
                    onChange={(e) => setExceptionForm({ ...exceptionForm, exception_date: e.target.value })}
                    className="w-full p-2.5 rounded-xl bg-slate-950 border border-slate-800 text-white font-mono"
                    required
                  />
                </div>
                <div>
                  <label className="text-slate-400 font-semibold block mb-1">Time Window</label>
                  <div className="flex items-center gap-1">
                    <input
                      type="time"
                      value={exceptionForm.start_time}
                      onChange={(e) => setExceptionForm({ ...exceptionForm, start_time: e.target.value })}
                      className="w-full p-2 rounded-xl bg-slate-950 border border-slate-800 text-white font-mono"
                    />
                    <input
                      type="time"
                      value={exceptionForm.end_time}
                      onChange={(e) => setExceptionForm({ ...exceptionForm, end_time: e.target.value })}
                      className="w-full p-2 rounded-xl bg-slate-950 border border-slate-800 text-white font-mono"
                    />
                  </div>
                </div>
              </div>

              <div>
                <label className="text-slate-400 font-semibold block mb-1">Reason / Note</label>
                <input
                  type="text"
                  placeholder="e.g. Dean's Special Address, Guest Lecture"
                  value={exceptionForm.reason}
                  onChange={(e) => setExceptionForm({ ...exceptionForm, reason: e.target.value })}
                  className="w-full p-2.5 rounded-xl bg-slate-950 border border-slate-800 text-white"
                />
              </div>

              <div className="pt-2 flex items-center justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setNewExceptionModal(false)}
                  className="px-4 py-2 rounded-xl bg-slate-800 text-slate-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-gradient-to-r from-purple-500 to-indigo-600 text-white font-bold"
                >
                  Save Exception
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}
