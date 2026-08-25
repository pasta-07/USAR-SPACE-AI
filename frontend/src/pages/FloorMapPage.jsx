import React, { useState, useEffect } from 'react';
import { 
  Building2, 
  Layers, 
  Clock, 
  CheckCircle2, 
  XCircle, 
  AlertCircle, 
  ChevronRight, 
  Sparkles,
  RefreshCw,
  Monitor,
  Cpu,
  Video
} from 'lucide-react';
import { api } from '../services/api';

export default function FloorMapPage({
  simulatedTime,
  simulatedDay,
  onSelectClassroom
}) {
  const [buildings, setBuildings] = useState([]);
  const [selectedBuildingId, setSelectedBuildingId] = useState(null);
  const [buildingData, setBuildingData] = useState(null);
  const [selectedFloor, setSelectedFloor] = useState(null);
  const [loading, setLoading] = useState(true);

  // Load buildings
  useEffect(() => {
    api.getBuildings()
      .then((data) => {
        setBuildings(data);
        if (data.length > 0) {
          setSelectedBuildingId(data[0].id);
        }
      })
      .catch((err) => console.error(err));
  }, []);

  // Load selected building classrooms
  useEffect(() => {
    if (!selectedBuildingId) return;
    setLoading(true);
    api.getBuildingClassrooms(selectedBuildingId, { simulatedTime, simulatedDay })
      .then((data) => {
        setBuildingData(data);
        if (data.floors && data.floors.length > 0) {
          // Default to first floor or 2nd floor
          setSelectedFloor(data.floors[0].floor_number);
        }
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, [selectedBuildingId, simulatedTime, simulatedDay]);

  const activeFloorData = buildingData?.floors?.find(f => f.floor_number === selectedFloor);

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      
      {/* Blueprint Header Banner */}
      <div className="p-6 sm:p-8 rounded-3xl bg-gradient-to-r from-slate-900 via-slate-900 to-indigo-950/60 border border-slate-800 shadow-2xl flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold mb-3">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span>Live Campus Digital Twin Map</span>
          </div>
          <h2 className="font-['Outfit'] text-2xl sm:text-4xl font-black text-white tracking-tight">
            Floor Plan & Building Monitor
          </h2>
          <p className="text-slate-400 text-sm mt-1 max-w-xl">
            Visual spatial view of university academic blocks. Monitor live occupancy states floor-by-floor in real time.
          </p>
        </div>

        {/* Legend */}
        <div className="flex flex-wrap items-center gap-3 p-3.5 rounded-2xl bg-slate-950/80 border border-slate-800 text-xs">
          <div className="flex items-center gap-1.5 font-medium text-emerald-400">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 shadow-sm shadow-emerald-500/50"></span>
            <span>Available</span>
          </div>
          <div className="flex items-center gap-1.5 font-medium text-rose-400">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-500 shadow-sm shadow-rose-500/50"></span>
            <span>Occupied</span>
          </div>
          <div className="flex items-center gap-1.5 font-medium text-amber-400">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500 shadow-sm shadow-amber-500/50"></span>
            <span>Free &lt; 1hr</span>
          </div>
          <div className="flex items-center gap-1.5 font-medium text-slate-500">
            <span className="w-2.5 h-2.5 rounded-full bg-slate-600"></span>
            <span>No Timetable</span>
          </div>
        </div>
      </div>

      {/* Building Tabs */}
      <div className="flex flex-wrap items-center gap-2 p-1.5 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl">
        {buildings.map((b) => (
          <button
            key={b.id}
            onClick={() => setSelectedBuildingId(b.id)}
            className={`flex items-center gap-2.5 px-5 py-3 rounded-xl text-sm font-semibold transition-all ${
              selectedBuildingId === b.id
                ? 'bg-gradient-to-r from-emerald-500/20 to-indigo-500/20 text-white border border-emerald-500/40 shadow-lg shadow-emerald-500/10'
                : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
            }`}
          >
            <Building2 className={`w-4 h-4 ${selectedBuildingId === b.id ? 'text-emerald-400' : 'text-slate-500'}`} />
            <span>{b.name}</span>
          </button>
        ))}
      </div>

      {/* Main Floor View Area */}
      {loading ? (
        <div className="py-20 text-center space-y-3">
          <RefreshCw className="w-8 h-8 text-emerald-400 animate-spin mx-auto" />
          <p className="text-sm text-slate-400">Loading building architectural floor matrix...</p>
        </div>
      ) : buildingData ? (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          
          {/* Left Floor Switcher Sidebar */}
          <div className="lg:col-span-3 space-y-2">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 px-2 mb-2 flex items-center gap-2">
              <Layers className="w-4 h-4 text-indigo-400" />
              <span>Select Floor Level</span>
            </h4>
            
            <div className="space-y-1.5">
              {buildingData.floors.map((fl) => {
                const isSelected = selectedFloor === fl.floor_number;
                const freeCount = fl.classrooms.filter(c => c.status === 'AVAILABLE').length;
                const totalCount = fl.classrooms.length;

                return (
                  <button
                    key={fl.floor_number}
                    onClick={() => setSelectedFloor(fl.floor_number)}
                    className={`w-full p-3.5 rounded-2xl border text-left transition-all flex items-center justify-between group ${
                      isSelected
                        ? 'bg-indigo-950/40 border-indigo-500 text-white shadow-lg shadow-indigo-950/30'
                        : 'bg-slate-900/80 border-slate-800/80 text-slate-400 hover:border-slate-700 hover:bg-slate-900 hover:text-slate-200'
                    }`}
                  >
                    <div>
                      <p className="font-bold text-sm text-white font-['Outfit']">{fl.floor_label}</p>
                      <p className="text-[11px] text-slate-400 mt-0.5">
                        {freeCount} of {totalCount} rooms available
                      </p>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      <span className={`w-2.5 h-2.5 rounded-full ${
                        freeCount > 0 ? 'bg-emerald-400 shadow-sm shadow-emerald-400/50 animate-pulse' : 'bg-rose-500'
                      }`} />
                      <ChevronRight className={`w-4 h-4 ${isSelected ? 'text-indigo-400 translate-x-1' : 'text-slate-600'} transition-transform`} />
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Right Floor Blueprint Cards Matrix */}
          <div className="lg:col-span-9 space-y-4">
            
            {activeFloorData ? (
              <div className="p-6 rounded-3xl bg-slate-900/80 border border-slate-800 shadow-xl space-y-5">
                <div className="flex items-center justify-between pb-4 border-b border-slate-800">
                  <div>
                    <h3 className="font-['Outfit'] text-xl font-bold text-white">
                      {buildingData.building_name} • {activeFloorData.floor_label}
                    </h3>
                    <p className="text-xs text-slate-400 mt-0.5">
                      Showing live occupancy states for {buildingData.day_of_week} ({buildingData.current_time_ist})
                    </p>
                  </div>

                  <span className="px-3 py-1 rounded-xl bg-slate-950 text-xs font-mono font-medium text-slate-300 border border-slate-800">
                    {activeFloorData.classrooms.length} Active Rooms
                  </span>
                </div>

                {/* Grid of rooms on this floor */}
                <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
                  {activeFloorData.classrooms.map((room) => {
                    const isAvail = room.status === 'AVAILABLE';
                    return (
                      <div
                        key={room.classroom_id}
                        onClick={() => onSelectClassroom(room)}
                        className={`p-4 rounded-2xl border transition-all cursor-pointer group hover:-translate-y-1 hover:shadow-xl ${
                          isAvail
                            ? 'bg-gradient-to-br from-emerald-950/20 via-slate-900 to-slate-950 border-emerald-500/30 hover:border-emerald-500/60 shadow-emerald-950/20'
                            : 'bg-gradient-to-br from-rose-950/20 via-slate-900 to-slate-950 border-rose-500/20 hover:border-rose-500/40 shadow-rose-950/20'
                        }`}
                      >
                        <div className="flex items-start justify-between gap-2 mb-2">
                          <h4 className="font-['Outfit'] text-lg font-bold text-white group-hover:text-emerald-300 transition-colors">
                            {room.room_number}
                          </h4>
                          <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                            isAvail ? 'bg-emerald-500/20 text-emerald-300' : 'bg-rose-500/20 text-rose-300'
                          }`}>
                            {isAvail ? '🟢 Available' : '🔴 Busy'}
                          </span>
                        </div>

                        <p className="text-xs text-slate-400 capitalize mb-3">
                          {room.room_type.replace('_', ' ')} • {room.capacity} seats
                        </p>

                        <div className={`p-2.5 rounded-xl text-xs ${
                          isAvail ? 'bg-emerald-950/30 text-emerald-200' : 'bg-slate-950 text-slate-300'
                        }`}>
                          {isAvail ? (
                            <p className="font-medium text-[11px]">
                              Free until <strong>{room.free_until}</strong>
                            </p>
                          ) : (
                            <p className="font-medium text-[11px] truncate">
                              Class: {room.current_class?.subject || 'Lecture in Progress'}
                            </p>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            ) : (
              <div className="py-20 text-center rounded-3xl bg-slate-900/40 border border-slate-800 text-slate-400">
                Select a floor to view classrooms.
              </div>
            )}

          </div>

        </div>
      ) : null}

    </div>
  );
}
