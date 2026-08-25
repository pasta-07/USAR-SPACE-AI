import React from 'react';
import { 
  Users, 
  Clock, 
  Sparkles, 
  Monitor, 
  Cpu, 
  BookOpen, 
  ChevronRight, 
  CheckCircle2, 
  AlertCircle, 
  XCircle,
  Video
} from 'lucide-react';

export default function ClassroomCard({ classroom, room, onClick, currentMinutes }) {
  const data = classroom || room || {};
  const isAvailable = data.status === 'AVAILABLE';
  const isOccupied = data.status === 'OCCUPIED';
  
  // Calculate if occupied room becomes free soon (within 60m)
  const isFreeSoon = isOccupied && Boolean(data.occupied_until);

  const getStatusBadge = () => {
    if (isAvailable) {
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 shadow-sm shadow-emerald-500/20">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          AVAILABLE NOW
        </span>
      );
    }
    if (isFreeSoon) {
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-amber-500/15 text-amber-300 border border-amber-500/30 shadow-sm shadow-amber-500/20">
          <span className="w-2 h-2 rounded-full bg-amber-400"></span>
          FREE AT {data.occupied_until}
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-rose-500/15 text-rose-400 border border-rose-500/30 shadow-sm shadow-rose-500/20">
        <span className="w-2 h-2 rounded-full bg-rose-500"></span>
        OCCUPIED
      </span>
    );
  };

  const getRoomTypeIcon = () => {
    if (data.room_type === 'computer_lab') return <Monitor className="w-3.5 h-3.5 text-cyan-400" />;
    if (data.room_type === 'robotics_lab' || data.room_type === 'hardware_lab') return <Cpu className="w-3.5 h-3.5 text-purple-400" />;
    if (data.room_type === 'lecture_theatre') return <Video className="w-3.5 h-3.5 text-amber-400" />;
    return <BookOpen className="w-3.5 h-3.5 text-blue-400" />;
  };

  const formatFreeDuration = (minutes) => {
    if (minutes === null || minutes === undefined) return null;
    if (minutes >= 60) {
      const h = Math.floor(minutes / 60);
      const m = minutes % 60;
      return `${h}h ${m > 0 ? `${m}m` : ''}`.trim();
    }
    return `${minutes} mins`;
  };

  return (
    <div 
      onClick={() => onClick && onClick(data)}
      className={`group relative overflow-hidden rounded-2xl bg-slate-900/80 border transition-all duration-300 hover:-translate-y-1 hover:shadow-2xl cursor-pointer p-5 flex flex-col justify-between ${
        isAvailable 
          ? 'border-emerald-500/30 hover:border-emerald-500/60 hover:shadow-emerald-950/40 bg-gradient-to-b from-slate-900/90 to-slate-950/90' 
          : 'border-slate-800 hover:border-slate-700 hover:shadow-indigo-950/30 bg-gradient-to-b from-slate-900/60 to-slate-950/80'
      }`}
    >
      {/* Top subtle glow bar */}
      <div className={`absolute top-0 left-0 right-0 h-1 transition-all ${
        isAvailable ? 'bg-gradient-to-r from-emerald-500 via-teal-400 to-emerald-500' : 'bg-slate-800 group-hover:bg-indigo-500'
      }`} />

      <div>
        {/* Header: Room Number & Status */}
        <div className="flex items-start justify-between gap-2 mb-3">
          <div>
            <div className="flex items-center gap-2">
              <h3 className="font-['Outfit'] text-xl font-bold text-white group-hover:text-emerald-300 transition-colors tracking-tight">
                {data.room_number || 'Room'}
              </h3>
              <span className="p-1 rounded-md bg-slate-800/80 border border-slate-700/60" title={(data.room_type || '').replace('_', ' ')}>
                {getRoomTypeIcon()}
              </span>
            </div>
            <p className="text-xs text-slate-400 font-medium">
              {data.building_name} • {data.floor_label}
            </p>
          </div>

          <div className="flex flex-col items-end">
            {getStatusBadge()}
          </div>
        </div>

        {/* Dynamic Availability State Card */}
        <div className={`p-3.5 rounded-xl border mb-4 text-xs ${
          isAvailable
            ? 'bg-emerald-950/20 border-emerald-500/20 text-emerald-100'
            : 'bg-slate-950/60 border-slate-800/80 text-slate-300'
        }`}>
          {isAvailable ? (
            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <span className="text-emerald-400/90 font-medium">Free Duration:</span>
                <span className="font-bold text-emerald-300 text-sm">
                  {data.free_until === 'Tomorrow' ? 'Rest of Day' : `Free until ${data.free_until || 'Rest of Day'}`}
                </span>
              </div>
              {data.remaining_free_minutes > 0 && (
                <div className="flex items-center justify-between text-[11px] text-slate-400">
                  <span>Continuous free time:</span>
                  <span className="font-semibold text-emerald-400">
                    {formatFreeDuration(data.remaining_free_minutes)}
                  </span>
                </div>
              )}
              {data.next_class && (
                <div className="pt-1.5 border-t border-emerald-500/20 text-[11px] text-slate-400 flex items-center justify-between">
                  <span>Next Class:</span>
                  <span className="text-slate-200 font-medium truncate max-w-[140px]">
                    {data.next_class.start_time} ({data.next_class.subject_code || data.next_class.subject})
                  </span>
                </div>
              )}
            </div>
          ) : (
            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <span className="text-rose-400/90 font-medium">Occupied Until:</span>
                <span className="font-bold text-rose-300 text-sm">{data.occupied_until || 'End of Period'}</span>
              </div>
              {data.current_class && (
                <div className="space-y-1">
                  <p className="font-semibold text-white truncate" title={data.current_class.subject}>
                    {data.current_class.subject}
                  </p>
                  <p className="text-[11px] text-slate-400 truncate">
                    {data.current_class.faculty} • {data.current_class.department}-Sem{data.current_class.semester} {data.current_class.section}
                  </p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Mini Day Timeline Gauge */}
        <div className="mb-4">
          <div className="flex items-center justify-between text-[10px] text-slate-500 mb-1 font-mono">
            <span>8 AM</span>
            <span>12 PM</span>
            <span>3 PM</span>
            <span>6 PM</span>
          </div>
          <div className="h-2 w-full bg-slate-950 rounded-full overflow-hidden flex gap-0.5 p-0.5 border border-slate-800">
            {data.timeline_blocks && data.timeline_blocks.map((b, i) => (
              <div
                key={i}
                title={`${b.start_time}-${b.end_time}: ${b.status === 'OCCUPIED' ? b.subject : 'Available'}`}
                className={`h-full flex-1 rounded-sm transition-all ${
                  b.is_current 
                    ? (b.status === 'OCCUPIED' ? 'bg-rose-500 ring-2 ring-white/50' : 'bg-emerald-400 ring-2 ring-white/50 animate-pulse') 
                    : (b.status === 'OCCUPIED' ? 'bg-rose-900/60' : 'bg-emerald-950/60')
                }`}
              />
            ))}
          </div>
        </div>
      </div>

      {/* Footer: Capacity & View Details Button */}
      <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs">
        <div className="flex items-center gap-3 text-slate-400">
          <span className="flex items-center gap-1">
            <Users className="w-3.5 h-3.5 text-slate-500" />
            <span>{data.capacity || 60} seats</span>
          </span>
        </div>

        <button 
          className="flex items-center gap-1 font-semibold text-emerald-400 group-hover:text-emerald-300 transition-colors"
        >
          <span>View Schedule</span>
          <ChevronRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
        </button>
      </div>

    </div>
  );
}
