import React, { useState, useEffect } from 'react';
import { 
  X, 
  Clock, 
  Calendar, 
  Users, 
  MapPin, 
  CheckCircle2, 
  AlertCircle, 
  Monitor, 
  Cpu, 
  BookOpen, 
  Video, 
  Sparkles,
  Info,
  ShieldAlert,
  ArrowRight
} from 'lucide-react';
import { api } from '../services/api';

export default function ClassroomModal({ classroom, onClose, simulatedTime, simulatedDay }) {
  const [activeTab, setActiveTab] = useState('today'); // 'today' | 'weekly' | 'specs'
  const [weeklyData, setWeeklyData] = useState(null);
  const [loadingWeekly, setLoadingWeekly] = useState(false);

  useEffect(() => {
    if (classroom && activeTab === 'weekly' && !weeklyData) {
      setLoadingWeekly(true);
      api.getClassroomSchedule(classroom.classroom_id)
        .then(res => setWeeklyData(res.weekly_schedule))
        .catch(err => console.error(err))
        .finally(() => setLoadingWeekly(false));
    }
  }, [classroom, activeTab, weeklyData]);

  if (!classroom) return null;

  const isAvailable = classroom.status === 'AVAILABLE';
  const timeSlots = ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00"];

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-950/80 backdrop-blur-md flex items-center justify-center p-4 sm:p-6 animate-in fade-in duration-200">
      <div className="relative w-full max-w-4xl bg-slate-900 border border-slate-700/80 rounded-3xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        
        {/* Modal Top Banner */}
        <div className="p-6 border-b border-slate-800 bg-gradient-to-r from-slate-900 via-slate-900/90 to-slate-950 flex items-start justify-between">
          <div className="flex items-center gap-4">
            <div className={`w-14 h-14 rounded-2xl flex items-center justify-center p-3 shadow-lg ${
              isAvailable 
                ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' 
                : 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
            }`}>
              {isAvailable ? <CheckCircle2 className="w-8 h-8" /> : <Clock className="w-8 h-8" />}
            </div>
            <div>
              <div className="flex items-center gap-3">
                <h2 className="font-['Outfit'] text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
                  {classroom.room_number}
                </h2>
                <span className={`px-3 py-1 text-xs font-bold rounded-full uppercase tracking-wider ${
                  isAvailable 
                    ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40' 
                    : 'bg-rose-500/20 text-rose-300 border border-rose-500/40'
                }`}>
                  {classroom.status}
                </span>
              </div>
              <p className="text-sm text-slate-400 mt-1 flex items-center gap-2">
                <MapPin className="w-4 h-4 text-slate-500" />
                {classroom.building_name} • {classroom.floor_label} • {classroom.capacity} Seats
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-2 rounded-xl bg-slate-800/80 hover:bg-slate-700 text-slate-400 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="flex items-center gap-2 px-6 pt-3 border-b border-slate-800 bg-slate-950/40">
          <button
            onClick={() => setActiveTab('today')}
            className={`px-4 py-2.5 text-sm font-semibold border-b-2 transition-all ${
              activeTab === 'today'
                ? 'border-emerald-400 text-emerald-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            Today's Live Status ({classroom.day_of_week})
          </button>
          <button
            onClick={() => setActiveTab('weekly')}
            className={`px-4 py-2.5 text-sm font-semibold border-b-2 transition-all ${
              activeTab === 'weekly'
                ? 'border-indigo-400 text-indigo-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            Full Weekly Timetable
          </button>
          <button
            onClick={() => setActiveTab('specs')}
            className={`px-4 py-2.5 text-sm font-semibold border-b-2 transition-all ${
              activeTab === 'specs'
                ? 'border-purple-400 text-purple-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            Facilities & Amenities
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-6">
          
          {activeTab === 'today' && (
            <>
              {/* Status summary metrics */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className={`p-4 rounded-2xl border ${
                  isAvailable 
                    ? 'bg-emerald-950/30 border-emerald-500/30' 
                    : 'bg-rose-950/30 border-rose-500/30'
                }`}>
                  <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                    {isAvailable ? 'Current Free Window' : 'Occupied Window'}
                  </span>
                  <div className="mt-1 flex items-baseline gap-2">
                    <span className="text-2xl font-extrabold text-white">
                      {isAvailable 
                        ? (classroom.free_until === 'Tomorrow' ? 'Rest of Day' : `Until ${classroom.free_until}`) 
                        : `Until ${classroom.occupied_until}`}
                    </span>
                    {isAvailable && classroom.remaining_free_minutes > 0 && (
                      <span className="text-xs font-medium text-emerald-400">
                        ({Math.floor(classroom.remaining_free_minutes / 60)}h {classroom.remaining_free_minutes % 60}m remaining)
                      </span>
                    )}
                  </div>
                  {classroom.current_class && (
                    <div className="mt-2 pt-2 border-t border-rose-500/20 text-xs text-slate-300">
                      <p className="font-semibold text-white">{classroom.current_class.subject}</p>
                      <p className="text-slate-400">Faculty: {classroom.current_class.faculty} ({classroom.current_class.department}-Sem{classroom.current_class.semester} {classroom.current_class.section})</p>
                    </div>
                  )}
                </div>

                <div className="p-4 rounded-2xl border bg-slate-950/60 border-slate-800">
                  <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                    Next Scheduled Class
                  </span>
                  {classroom.next_class ? (
                    <div className="mt-1">
                      <div className="flex items-baseline justify-between">
                        <span className="text-lg font-bold text-white">
                          {classroom.next_class.start_time} – {classroom.next_class.end_time}
                        </span>
                        <span className="text-xs font-semibold text-amber-400">
                          In {classroom.next_class.starts_in_minutes} mins
                        </span>
                      </div>
                      <p className="text-sm font-semibold text-slate-200 mt-1">
                        {classroom.next_class.subject} ({classroom.next_class.subject_code})
                      </p>
                      <p className="text-xs text-slate-400 mt-0.5">
                        {classroom.next_class.faculty} • {classroom.next_class.department}-Sem{classroom.next_class.semester} {classroom.next_class.section}
                      </p>
                    </div>
                  ) : (
                    <p className="text-sm text-slate-400 mt-2 font-medium">
                      No further classes scheduled for today! Room remains free.
                    </p>
                  )}
                </div>
              </div>

              {/* Visual Gantt Timeline for Today */}
              <div>
                <div className="flex items-center justify-between mb-3">
                  <h4 className="text-sm font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                    <Clock className="w-4 h-4 text-emerald-400" />
                    Today's Schedule Timeline (8:00 AM – 6:00 PM)
                  </h4>
                  <span className="text-xs text-slate-400">
                    Current Time: <strong className="text-white font-mono">{classroom.current_time_ist}</strong>
                  </span>
                </div>

                <div className="space-y-2">
                  {classroom.timeline_blocks && classroom.timeline_blocks.map((b, idx) => (
                    <div 
                      key={idx}
                      className={`p-3 rounded-xl border flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 transition-all ${
                        b.is_current
                          ? (b.status === 'OCCUPIED' ? 'bg-rose-950/40 border-rose-500/60 ring-1 ring-rose-400' : 'bg-emerald-950/40 border-emerald-500/60 ring-1 ring-emerald-400')
                          : (b.status === 'OCCUPIED' ? 'bg-slate-900 border-slate-800 text-slate-300' : 'bg-slate-950/50 border-slate-800/60 text-slate-400')
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <span className="font-mono text-xs font-bold text-slate-300 w-24">
                          {b.start_time} – {b.end_time}
                        </span>
                        <span className={`px-2 py-0.5 rounded text-[11px] font-bold uppercase ${
                          b.status === 'OCCUPIED' ? 'bg-rose-500/20 text-rose-300' : 'bg-emerald-500/20 text-emerald-300'
                        }`}>
                          {b.status}
                        </span>
                        {b.is_current && (
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40 animate-pulse">
                            Current Slot
                          </span>
                        )}
                      </div>

                      <div className="text-right">
                        {b.status === 'OCCUPIED' ? (
                          <div>
                            <span className="text-sm font-semibold text-white">{b.subject}</span>
                            {b.faculty && (
                              <span className="text-xs text-slate-400 block">
                                {b.faculty} {b.section ? `• ${b.section}` : ''}
                              </span>
                            )}
                          </div>
                        ) : (
                          <span className="text-xs text-emerald-400/80 font-medium">Free Period / Available</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}

          {activeTab === 'weekly' && (
            <div>
              {loadingWeekly ? (
                <div className="py-12 text-center text-slate-400">Loading weekly schedule...</div>
              ) : weeklyData ? (
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs border-collapse">
                    <thead>
                      <tr className="bg-slate-950 border-b border-slate-800 text-slate-400 font-mono">
                        <th className="p-3">Day</th>
                        {timeSlots.map(slot => (
                          <th key={slot} className="p-3 font-semibold">{slot}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60">
                      {['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'].map(day => {
                        const dayClasses = weeklyData[day] || [];
                        return (
                          <tr key={day} className="hover:bg-slate-800/30">
                            <td className="p-3 font-bold text-white bg-slate-950/40 font-['Outfit']">{day.slice(0, 3)}</td>
                            {timeSlots.map(slot => {
                              const match = dayClasses.find(c => c.start_time === slot);
                              return (
                                <td key={slot} className="p-2 align-top">
                                  {match ? (
                                    <div className="p-2 rounded-lg bg-indigo-950/60 border border-indigo-500/30 text-[11px] space-y-0.5">
                                      <p className="font-bold text-indigo-200 truncate" title={match.subject_name}>
                                        {match.subject_code || match.subject_name}
                                      </p>
                                      <p className="text-slate-400 truncate text-[10px]">
                                        {match.faculty_name}
                                      </p>
                                      <span className="inline-block px-1 py-0.2 rounded text-[9px] bg-indigo-500/20 text-indigo-300 font-mono">
                                        {match.department_code}-{match.semester}{match.section}
                                      </span>
                                    </div>
                                  ) : (
                                    <div className="h-12 rounded-lg bg-slate-950/30 border border-dashed border-slate-800 flex items-center justify-center text-[10px] text-slate-600">
                                      Free
                                    </div>
                                  )}
                                </td>
                              );
                            })}
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="py-12 text-center text-slate-400">No schedule records available.</div>
              )}
            </div>
          )}

          {activeTab === 'specs' && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
                <div className="p-4 rounded-2xl bg-slate-950/60 border border-slate-800">
                  <span className="text-xs text-slate-400">Room Type</span>
                  <p className="text-base font-bold text-white mt-1 capitalize">{classroom.room_type.replace('_', ' ')}</p>
                </div>
                <div className="p-4 rounded-2xl bg-slate-950/60 border border-slate-800">
                  <span className="text-xs text-slate-400">Total Seating Capacity</span>
                  <p className="text-base font-bold text-white mt-1">{classroom.capacity} Students</p>
                </div>
                <div className="p-4 rounded-2xl bg-slate-950/60 border border-slate-800">
                  <span className="text-xs text-slate-400">Floor Location</span>
                  <p className="text-base font-bold text-white mt-1">{classroom.floor_label}</p>
                </div>
              </div>

              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
                  Installed Amenities & Technology
                </h4>
                <div className="flex flex-wrap gap-2">
                  {classroom.amenities && classroom.amenities.map((item, idx) => (
                    <span key={idx} className="px-3 py-1.5 rounded-xl bg-slate-800 border border-slate-700 text-xs font-medium text-slate-200 flex items-center gap-1.5">
                      <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
                      {item}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          )}

        </div>

        {/* Modal Footer */}
        <div className="p-4 border-t border-slate-800 bg-slate-950/80 flex items-center justify-between text-xs text-slate-400">
          <span>Campus Timetable Engine • Indian Standard Time (IST)</span>
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-medium transition-colors"
          >
            Close
          </button>
        </div>

      </div>
    </div>
  );
}
