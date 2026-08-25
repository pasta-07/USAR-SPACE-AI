import React, { useState, useEffect } from 'react';
import { 
  Search, 
  Clock, 
  Calendar, 
  Building2, 
  Users, 
  CheckCircle2, 
  SlidersHorizontal, 
  ChevronRight, 
  Sparkles, 
  Zap,
  Info
} from 'lucide-react';
import { api } from '../services/api';

export default function FindRoomPage({
  simulatedTime,
  simulatedDay,
  onSelectClassroom
}) {
  const [startTime, setStartTime] = useState('14:00');
  const [endTime, setEndTime] = useState('16:00');
  const [selectedDay, setSelectedDay] = useState(simulatedDay || 'Monday');
  const [buildingCode, setBuildingCode] = useState('');
  const [floor, setFloor] = useState('');
  const [roomType, setRoomType] = useState('');
  const [minCapacity, setMinCapacity] = useState('');

  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [error, setError] = useState(null);

  const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];

  const quickPresets = [
    { label: 'Available Now', start: '14:00', end: '15:00', icon: '🟢' },
    { label: 'Next 1 Hour', start: '11:00', end: '12:00', icon: '⚡' },
    { label: 'Next 2 Hours', start: '14:00', end: '16:00', icon: '⏱️' },
    { label: 'Morning (9 AM – 1 PM)', start: '09:00', end: '13:00', icon: '🌅' },
    { label: 'Afternoon (1 PM – 5 PM)', start: '13:00', end: '17:00', icon: '☀️' },
    { label: 'Evening (5 PM – 7 PM)', start: '17:00', end: '19:00', icon: '🌙' },
  ];

  const handleSearch = async (sTime = startTime, eTime = endTime, day = selectedDay) => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.searchClassrooms({
        startTime: sTime,
        endTime: eTime,
        dayOfWeek: day,
        buildingCode: buildingCode || undefined,
        floor: floor !== '' ? parseInt(floor, 10) : undefined,
        roomType: roomType || undefined,
        minCapacity: minCapacity ? parseInt(minCapacity, 10) : undefined,
        simulatedTime,
        simulatedDay
      });
      setResults(res);
      setSearched(true);
    } catch (err) {
      setError(err.message || 'Failed to search classrooms');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Initial auto search
    handleSearch(startTime, endTime, selectedDay);
  }, []);

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      
      {/* Search Header Banner */}
      <div className="p-6 sm:p-8 rounded-3xl bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 border border-slate-800 shadow-2xl">
        <div className="max-w-3xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-xs font-semibold mb-3">
            <Zap className="w-3.5 h-3.5" />
            <span>Intelligent Free Room Finder</span>
          </div>
          <h2 className="font-['Outfit'] text-2xl sm:text-4xl font-black text-white tracking-tight">
            Search Available Classrooms
          </h2>
          <p className="text-slate-400 text-sm mt-2">
            Need a room for a study session, project work, hackathon prep, or faculty meeting? Enter your required hours and get instant conflict-free rooms.
          </p>
        </div>

        {/* Quick Slot Preset Buttons */}
        <div className="mt-6 pt-6 border-t border-slate-800/80">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400 block mb-2">
            Quick Slot Presets
          </span>
          <div className="flex flex-wrap items-center gap-2">
            {quickPresets.map((preset, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setStartTime(preset.start);
                  setEndTime(preset.end);
                  handleSearch(preset.start, preset.end, selectedDay);
                }}
                className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-medium border transition-all ${
                  startTime === preset.start && endTime === preset.end
                    ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40 shadow-sm'
                    : 'bg-slate-950/60 hover:bg-slate-800 text-slate-300 border-slate-800'
                }`}
              >
                <span>{preset.icon}</span>
                <span>{preset.label}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Search Panel */}
      <div className="p-6 rounded-3xl bg-slate-900/90 border border-slate-800 shadow-xl space-y-6">
        <form 
          onSubmit={(e) => {
            e.preventDefault();
            handleSearch();
          }}
          className="space-y-4"
        >
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            
            {/* Day of Week */}
            <div>
              <label className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5 block">
                Day of Week
              </label>
              <select
                value={selectedDay}
                onChange={(e) => setSelectedDay(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-sm font-medium text-white focus:outline-none focus:border-emerald-500"
              >
                {days.map(d => (
                  <option key={d} value={d}>{d}</option>
                ))}
              </select>
            </div>

            {/* Start Time */}
            <div>
              <label className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5 block">
                Start Time
              </label>
              <input
                type="time"
                value={startTime}
                onChange={(e) => setStartTime(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-sm font-mono text-white focus:outline-none focus:border-emerald-500"
                required
              />
            </div>

            {/* End Time */}
            <div>
              <label className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5 block">
                End Time
              </label>
              <input
                type="time"
                value={endTime}
                onChange={(e) => setEndTime(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-sm font-mono text-white focus:outline-none focus:border-emerald-500"
                required
              />
            </div>

            {/* Submit Action */}
            <div className="flex items-end">
              <button
                type="submit"
                disabled={loading}
                className="w-full py-2.5 px-4 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-slate-950 font-bold text-sm shadow-lg shadow-emerald-500/20 transition-all flex items-center justify-center gap-2"
              >
                <Search className="w-4 h-4" />
                <span>{loading ? 'Searching...' : 'Find Free Rooms'}</span>
              </button>
            </div>

          </div>

          {/* Secondary Filters: Building, Floor, Type, Capacity */}
          <div className="pt-4 border-t border-slate-800/80 grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div>
              <label className="text-[11px] font-medium text-slate-400 mb-1 block">Building</label>
              <select
                value={buildingCode}
                onChange={(e) => setBuildingCode(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-300 focus:outline-none"
              >
                <option value="">Any Building</option>
                <option value="BLOCK_A">Academic Block A</option>
                <option value="BLOCK_B">Academic Block B / USDI</option>
                <option value="BLOCK_C">Academic Block C</option>
              </select>
            </div>

            <div>
              <label className="text-[11px] font-medium text-slate-400 mb-1 block">Floor</label>
              <select
                value={floor}
                onChange={(e) => setFloor(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-300 focus:outline-none"
              >
                <option value="">Any Floor</option>
                <option value="-1">Basement (AUB)</option>
                <option value="0">Ground Floor</option>
                <option value="1">1st Floor</option>
                <option value="2">2nd Floor</option>
                <option value="3">3rd Floor</option>
                <option value="4">4th Floor</option>
                <option value="5">5th Floor</option>
                <option value="6">6th Floor</option>
                <option value="7">7th Floor</option>
              </select>
            </div>

            <div>
              <label className="text-[11px] font-medium text-slate-400 mb-1 block">Room Type</label>
              <select
                value={roomType}
                onChange={(e) => setRoomType(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-300 focus:outline-none"
              >
                <option value="">All Types</option>
                <option value="normal_classroom">Normal Classrooms</option>
                <option value="lecture_theatre">Lecture Theatres</option>
                <option value="computer_lab">Computer Labs</option>
                <option value="robotics_lab">Robotics Labs</option>
                <option value="hardware_lab">Hardware/Elec Labs</option>
              </select>
            </div>

            <div>
              <label className="text-[11px] font-medium text-slate-400 mb-1 block">Min Capacity</label>
              <input
                type="number"
                placeholder="e.g. 50 seats"
                value={minCapacity}
                onChange={(e) => setMinCapacity(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-300 focus:outline-none"
              />
            </div>
          </div>
        </form>
      </div>

      {/* Results Section */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <h3 className="font-['Outfit'] text-xl font-bold text-white">
              Available Classrooms ({results.length})
            </h3>
            <span className="px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
              {selectedDay} • {startTime} – {endTime}
            </span>
          </div>
        </div>

        {loading ? (
          <div className="py-16 text-center text-slate-400 space-y-2">
            <Clock className="w-8 h-8 text-emerald-400 animate-spin mx-auto" />
            <p className="text-sm">Finding completely free rooms with zero scheduling conflicts...</p>
          </div>
        ) : error ? (
          <div className="p-4 rounded-2xl bg-rose-950/40 border border-rose-500/30 text-rose-300 text-sm">
            {error}
          </div>
        ) : results.length > 0 ? (
          <div className="overflow-hidden rounded-3xl bg-slate-900/80 border border-slate-800 shadow-xl">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm border-collapse">
                <thead>
                  <tr className="bg-slate-950/80 border-b border-slate-800 text-slate-400 text-xs font-mono uppercase tracking-wider">
                    <th className="p-4">Classroom</th>
                    <th className="p-4">Building</th>
                    <th className="p-4">Floor</th>
                    <th className="p-4">Capacity</th>
                    <th className="p-4">Type</th>
                    <th className="p-4">Available Free Window</th>
                    <th className="p-4 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {results.map((r) => (
                    <tr 
                      key={r.classroom_id}
                      className="hover:bg-slate-800/40 transition-colors group"
                    >
                      <td className="p-4 font-bold text-white font-['Outfit'] text-base">
                        <div className="flex items-center gap-2">
                          <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                          <span>{r.room_number}</span>
                        </div>
                      </td>
                      <td className="p-4 text-slate-300 font-medium">{r.building_name}</td>
                      <td className="p-4 text-slate-400">{r.floor_label}</td>
                      <td className="p-4 text-slate-300">
                        <span className="flex items-center gap-1.5">
                          <Users className="w-3.5 h-3.5 text-slate-500" />
                          {r.capacity} seats
                        </span>
                      </td>
                      <td className="p-4">
                        <span className="px-2.5 py-1 rounded-lg text-xs font-medium bg-slate-800 border border-slate-700 text-slate-300 capitalize">
                          {r.room_type.replace('_', ' ')}
                        </span>
                      </td>
                      <td className="p-4 font-mono font-semibold text-emerald-400">
                        {r.available_window_start} – {r.available_window_end}
                      </td>
                      <td className="p-4 text-right">
                        <button
                          onClick={() => {
                            // Fetch full classroom detail
                            api.getClassroomStatus(r.classroom_id, { simulatedTime, simulatedDay })
                              .then(onSelectClassroom)
                              .catch(err => console.error(err));
                          }}
                          className="px-3.5 py-1.5 rounded-xl bg-slate-800 hover:bg-emerald-600 hover:text-slate-950 text-slate-200 text-xs font-bold transition-all inline-flex items-center gap-1.5 shadow-sm"
                        >
                          <span>Inspect</span>
                          <ChevronRight className="w-3.5 h-3.5" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <div className="py-16 text-center rounded-3xl bg-slate-900/40 border border-slate-800/80 p-8 space-y-2">
            <p className="text-base font-bold text-white font-['Outfit']">No empty classrooms found for this time slot</p>
            <p className="text-sm text-slate-400 max-w-md mx-auto">
              All classrooms are currently occupied with scheduled lectures or labs during {startTime} – {endTime}. Try adjusting the time window.
            </p>
          </div>
        )}
      </div>

    </div>
  );
}
