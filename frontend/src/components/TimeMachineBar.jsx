import React from 'react';
import { Clock, RotateCcw, Zap, Sparkles, AlertCircle, X } from 'lucide-react';

export default function TimeMachineBar({
  simulatedTime,
  setSimulatedTime,
  simulatedDay,
  setSimulatedDay,
  onReset,
  onClose
}) {
  const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
  const presets = [
    { label: 'Morning Class (10:15 AM)', time: '10:15', day: 'Monday' },
    { label: 'Mid-day Rush (11:45 AM)', time: '11:45', day: 'Tuesday' },
    { label: 'Lunch / Labs (01:30 PM)', time: '13:30', day: 'Wednesday' },
    { label: 'Afternoon (02:45 PM)', time: '14:45', day: 'Thursday' },
    { label: 'Evening Free (05:15 PM)', time: '17:15', day: 'Friday' },
  ];

  const isSimulated = Boolean(simulatedTime || simulatedDay);

  return (
    <div className="w-full bg-gradient-to-r from-indigo-950/90 via-slate-900/95 to-purple-950/90 border-b border-indigo-500/30 backdrop-blur-xl px-4 py-3 shadow-xl transition-all">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-start md:items-center justify-between gap-3">
        
        {/* Info Header */}
        <div className="flex items-center gap-2.5">
          <div className="p-1.5 rounded-lg bg-indigo-500/20 border border-indigo-400/30 text-indigo-400">
            <Zap className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold uppercase tracking-wider text-indigo-300">
                Campus Time Machine
              </span>
              {isSimulated ? (
                <span className="px-2 py-0.5 text-[10px] font-bold rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30 animate-pulse">
                  Simulation Active
                </span>
              ) : (
                <span className="px-2 py-0.5 text-[10px] font-medium rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                  Live Real-World IST
                </span>
              )}
            </div>
            <p className="text-[11px] text-slate-400">
              Test classroom statuses and timetable transitions across days & hours.
            </p>
          </div>
        </div>

        {/* Controls */}
        <div className="flex flex-wrap items-center gap-2 w-full md:w-auto">
          {/* Day Selector */}
          <div className="flex items-center rounded-lg bg-slate-950/60 p-0.5 border border-slate-800">
            {days.map((d) => (
              <button
                key={d}
                onClick={() => setSimulatedDay(d)}
                className={`px-2.5 py-1 rounded-md text-xs font-medium transition-colors ${
                  simulatedDay === d
                    ? 'bg-indigo-600 text-white font-semibold shadow-sm'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {d.slice(0, 3)}
              </button>
            ))}
          </div>

          {/* Time Input */}
          <div className="flex items-center gap-1.5 bg-slate-950/60 border border-slate-800 rounded-lg px-2 py-1">
            <Clock className="w-3.5 h-3.5 text-slate-400" />
            <input
              type="time"
              value={simulatedTime || '14:35'}
              onChange={(e) => setSimulatedTime(e.target.value)}
              className="bg-transparent text-xs font-mono font-medium text-slate-200 focus:outline-none"
            />
          </div>

          {/* Presets dropdown / buttons */}
          <div className="hidden lg:flex items-center gap-1">
            {presets.slice(0, 3).map((p, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setSimulatedTime(p.time);
                  setSimulatedDay(p.day);
                }}
                className="px-2 py-1 text-[11px] font-medium rounded-md bg-slate-800/80 hover:bg-slate-700/80 text-slate-300 border border-slate-700/60 transition-colors"
              >
                {p.label.split(' ')[0]} {p.time}
              </button>
            ))}
          </div>

          {/* Reset Button */}
          {isSimulated && (
            <button
              onClick={onReset}
              className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium bg-rose-500/20 text-rose-300 hover:bg-rose-500/30 border border-rose-500/30 transition-colors"
              title="Reset to Real-World Time"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Reset Live</span>
            </button>
          )}

          {/* Close bar */}
          {onClose && (
            <button
              onClick={onClose}
              className="p-1 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

      </div>
    </div>
  );
}
