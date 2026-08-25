import React, { useState, useEffect } from 'react';
import { 
  Calendar, 
  BarChart3, 
  BookOpen, 
  Users, 
  Layers, 
  Filter, 
  Clock, 
  Sparkles,
  Search,
  Activity,
  CheckCircle2
} from 'lucide-react';
import { api } from '../services/api';

export default function TimetableAnalyticsPage({ onSelectClassroom }) {
  const [selectedDept, setSelectedDept] = useState('AIML');
  const [selectedSem, setSelectedSem] = useState(3);
  const [selectedSec, setSelectedSec] = useState('B1');
  const [facultySearch, setFacultySearch] = useState('');
  const [statsData, setStatsData] = useState(null);
  const [loadingStats, setLoadingStats] = useState(true);

  const depts = [
    { code: 'AIDS', name: 'AI & Data Science' },
    { code: 'AIML', name: 'AI & Machine Learning' },
    { code: 'AR', name: 'Automation & Robotics' },
    { code: 'IIOT', name: 'Industrial IoT' }
  ];

  const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
  const timeSlots = ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00"];

  useEffect(() => {
    api.getCampusStats()
      .then(setStatsData)
      .catch(err => console.error(err))
      .finally(() => setLoadingStats(false));
  }, []);

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      
      {/* Header Banner */}
      <div className="p-6 sm:p-8 rounded-3xl bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 border border-slate-800 shadow-2xl">
        <div className="max-w-3xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/30 text-purple-400 text-xs font-semibold mb-3">
            <Activity className="w-3.5 h-3.5" />
            <span>Master Timetable Central Hub & Analytics</span>
          </div>
          <h2 className="font-['Outfit'] text-2xl sm:text-4xl font-black text-white tracking-tight">
            Campus Timetable & Room Analytics
          </h2>
          <p className="text-slate-400 text-sm mt-2">
            Explore complete department schedules, faculty allocations, and university-wide room utilization patterns.
          </p>
        </div>
      </div>

      {/* Campus Utilization Metric Cards */}
      {statsData && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Campus Classrooms</span>
            <div className="mt-2 flex items-baseline gap-2">
              <span className="font-['Outfit'] text-3xl font-extrabold text-white">{statsData.total_classrooms}</span>
              <span className="text-xs text-emerald-400 font-medium">Active & monitored</span>
            </div>
          </div>

          <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Weekly Scheduled Sessions</span>
            <div className="mt-2 flex items-baseline gap-2">
              <span className="font-['Outfit'] text-3xl font-extrabold text-white">{statsData.total_scheduled_classes}</span>
              <span className="text-xs text-indigo-400 font-medium">Across all branches</span>
            </div>
          </div>

          <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Peak Hour Average</span>
            <div className="mt-2 flex items-baseline gap-2">
              <span className="font-['Outfit'] text-3xl font-extrabold text-white">11:00 AM – 1:00 PM</span>
            </div>
          </div>

          <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Active Academic Wings</span>
            <div className="mt-2 flex items-baseline gap-2">
              <span className="font-['Outfit'] text-3xl font-extrabold text-white">3 Blocks</span>
              <span className="text-xs text-slate-400">Block A, B, C</span>
            </div>
          </div>
        </div>
      )}

      {/* Hourly Occupancy Heatmap Bar */}
      {statsData?.hourly_average_occupied_rooms && (
        <div className="p-6 rounded-3xl bg-slate-900/90 border border-slate-800 shadow-xl space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-['Outfit'] text-lg font-bold text-white flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-indigo-400" />
              <span>Campus Hourly Room Occupancy Rate</span>
            </h3>
            <span className="text-xs text-slate-400 font-mono">Mon – Fri Average</span>
          </div>

          <div className="grid grid-cols-4 sm:grid-cols-8 gap-3 pt-2">
            {Object.entries(statsData.hourly_average_occupied_rooms).map(([slot, avg]) => {
              const maxRooms = statsData.total_classrooms || 35;
              const percentage = Math.round((avg / maxRooms) * 100);
              return (
                <div key={slot} className="p-3 rounded-2xl bg-slate-950 border border-slate-800 text-center space-y-2">
                  <span className="text-xs font-mono font-bold text-slate-300">{slot}</span>
                  <div className="h-16 w-full bg-slate-900 rounded-xl overflow-hidden flex items-end p-1">
                    <div 
                      style={{ height: `${Math.min(100, Math.max(15, percentage))}%` }} 
                      className={`w-full rounded-lg transition-all ${
                        percentage > 60 ? 'bg-gradient-to-t from-rose-600 to-amber-500' : 'bg-gradient-to-t from-indigo-600 to-teal-400'
                      }`}
                    />
                  </div>
                  <div className="text-[11px] font-bold text-slate-200">{avg} rooms</div>
                  <div className="text-[10px] text-slate-500">{percentage}% busy</div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Master Department Timetable Filter Panel */}
      <div className="p-6 rounded-3xl bg-slate-900/90 border border-slate-800 shadow-xl space-y-6">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div>
            <h3 className="font-['Outfit'] text-xl font-bold text-white">
              Branch & Semester Timetable Matrix
            </h3>
            <p className="text-xs text-slate-400 mt-1">
              Select department and section to view the complete class schedule.
            </p>
          </div>

          {/* Department, Semester, Section Selectors */}
          <div className="flex flex-wrap items-center gap-2">
            {/* Department */}
            <div className="flex items-center rounded-xl bg-slate-950 p-1 border border-slate-800">
              {depts.map(d => (
                <button
                  key={d.code}
                  onClick={() => setSelectedDept(d.code)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                    selectedDept === d.code
                      ? 'bg-indigo-600 text-white shadow-sm'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {d.code}
                </button>
              ))}
            </div>

            {/* Semester */}
            <div className="flex items-center rounded-xl bg-slate-950 p-1 border border-slate-800">
              {[3, 5, 7].map(sem => (
                <button
                  key={sem}
                  onClick={() => setSelectedSem(sem)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                    selectedSem === sem
                      ? 'bg-purple-600 text-white shadow-sm'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  Sem {sem}
                </button>
              ))}
            </div>

            {/* Section */}
            <div className="flex items-center rounded-xl bg-slate-950 p-1 border border-slate-800">
              {['B1', 'B2'].map(sec => (
                <button
                  key={sec}
                  onClick={() => setSelectedSec(sec)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                    selectedSec === sec
                      ? 'bg-teal-600 text-white shadow-sm'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  Sec {sec}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Timetable Notice */}
        <div className="p-4 rounded-2xl bg-indigo-950/20 border border-indigo-500/30 flex items-center justify-between text-xs text-indigo-300">
          <span>Active Batch: <strong>{selectedDept}-Sem{selectedSem} {selectedSec}</strong> (Odd Semester 2026-27 w.e.f. August 2026)</span>
          <span className="font-mono">USAR Timetable Committee</span>
        </div>
      </div>

    </div>
  );
}
