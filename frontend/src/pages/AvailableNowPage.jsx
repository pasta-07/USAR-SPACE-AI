import React, { useState, useEffect } from 'react';
import { 
  Compass, 
  Search, 
  Filter, 
  RefreshCw, 
  CheckCircle2, 
  Clock, 
  AlertTriangle, 
  Layers, 
  Users, 
  ArrowRight,
  SlidersHorizontal,
  Code2,
  Sparkles
} from 'lucide-react';
import ClassroomCard from '../components/ClassroomCard';
import { api } from '../services/api';

export default function AvailableNowPage({
  simulatedTime,
  simulatedDay,
  overviewData,
  loading,
  onRefresh,
  onSelectClassroom,
  onNavigateToSearch
}) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedBuilding, setSelectedBuilding] = useState('');
  const [selectedFloor, setSelectedFloor] = useState('');
  const [selectedType, setSelectedType] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL'); // 'ALL' | 'AVAILABLE' | 'OCCUPIED' | 'FREE_SOON'

  const classrooms = overviewData?.classrooms || [];

  // Filter classrooms
  const filteredClassrooms = classrooms.filter((room) => {
    // Search query
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      const matchName = room.room_number.toLowerCase().includes(q);
      const matchBldg = room.building_name.toLowerCase().includes(q);
      const matchType = room.room_type.toLowerCase().includes(q);
      if (!matchName && !matchBldg && !matchType) return false;
    }
    // Building
    if (selectedBuilding && room.building_code !== selectedBuilding) return false;
    // Floor
    if (selectedFloor !== '' && room.floor !== parseInt(selectedFloor, 10)) return false;
    // Type
    if (selectedType && room.room_type !== selectedType) return false;
    // Status
    if (statusFilter === 'AVAILABLE' && room.status !== 'AVAILABLE') return false;
    if (statusFilter === 'OCCUPIED' && room.status !== 'OCCUPIED') return false;
    if (statusFilter === 'FREE_SOON') {
      if (room.status !== 'OCCUPIED') return false;
      if (!room.occupied_until) return false;
    }

    return true;
  });

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      
      {/* Hero Section */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-slate-900 via-indigo-950/40 to-slate-950 border border-slate-800/80 p-6 sm:p-10 shadow-2xl">
        <div className="absolute -top-24 -right-24 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-24 -left-24 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 max-w-3xl">
          <div className="flex flex-wrap items-center gap-2.5 mb-4">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              Real-Time Campus Availability Engine (IST)
            </div>

            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 text-xs font-mono font-medium">
              <Code2 className="w-3.5 h-3.5 text-indigo-400" />
              <span>Developed by <strong>Pranav Siroha</strong></span>
            </div>
          </div>

          <h1 className="font-['Outfit'] text-3xl sm:text-5xl font-black text-white tracking-tight leading-tight">
            Find an Empty Classroom, <br />
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-emerald-400 via-teal-300 to-indigo-400">
              Instantly.
            </span>
          </h1>

          <p className="text-slate-300 text-sm sm:text-base mt-3 leading-relaxed">
            Real-time classroom availability based on the centralized college timetable. Automatically analyzes active classes, free windows, and upcoming schedules in Indian Standard Time.
          </p>

          <div className="mt-6 flex flex-wrap items-center gap-3">
            <button
              onClick={onNavigateToSearch}
              className="flex items-center gap-2 px-5 py-3 rounded-2xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-slate-950 font-bold text-sm shadow-lg shadow-emerald-500/25 transition-all hover:scale-[1.02] active:scale-[0.98]"
            >
              <Search className="w-4 h-4" />
              <span>Find a Room for a Time Slot</span>
              <ArrowRight className="w-4 h-4" />
            </button>

            <button
              onClick={onRefresh}
              className="flex items-center gap-2 px-4 py-3 rounded-2xl bg-slate-800/80 hover:bg-slate-700 border border-slate-700 text-slate-200 font-semibold text-sm transition-colors"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-emerald-400' : ''}`} />
              <span>Refresh Live</span>
            </button>
          </div>
        </div>
      </div>

      {/* Hero Metric Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Available Now */}
        <div 
          onClick={() => setStatusFilter(statusFilter === 'AVAILABLE' ? 'ALL' : 'AVAILABLE')}
          className={`p-5 rounded-2xl border transition-all cursor-pointer ${
            statusFilter === 'AVAILABLE' 
              ? 'bg-emerald-950/40 border-emerald-500 ring-2 ring-emerald-500/40 shadow-xl shadow-emerald-950/30' 
              : 'bg-slate-900/70 border-slate-800/80 hover:border-emerald-500/40 hover:bg-slate-900'
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Available Right Now</span>
            <div className="w-8 h-8 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center">
              <CheckCircle2 className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="font-['Outfit'] text-4xl font-extrabold text-white">
              {overviewData?.available_now_count ?? '--'}
            </span>
            <span className="text-xs text-emerald-400 font-medium">Free for study/events</span>
          </div>
        </div>

        {/* Occupied */}
        <div 
          onClick={() => setStatusFilter(statusFilter === 'OCCUPIED' ? 'ALL' : 'OCCUPIED')}
          className={`p-5 rounded-2xl border transition-all cursor-pointer ${
            statusFilter === 'OCCUPIED' 
              ? 'bg-rose-950/40 border-rose-500 ring-2 ring-rose-500/40 shadow-xl shadow-rose-950/30' 
              : 'bg-slate-900/70 border-slate-800/80 hover:border-rose-500/40 hover:bg-slate-900'
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Occupied (In Class)</span>
            <div className="w-8 h-8 rounded-xl bg-rose-500/20 text-rose-400 flex items-center justify-center">
              <Clock className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="font-['Outfit'] text-4xl font-extrabold text-white">
              {overviewData?.occupied_now_count ?? '--'}
            </span>
            <span className="text-xs text-rose-400 font-medium">Active lectures/labs</span>
          </div>
        </div>

        {/* Free Soon */}
        <div 
          onClick={() => setStatusFilter(statusFilter === 'FREE_SOON' ? 'ALL' : 'FREE_SOON')}
          className={`p-5 rounded-2xl border transition-all cursor-pointer ${
            statusFilter === 'FREE_SOON' 
              ? 'bg-amber-950/40 border-amber-500 ring-2 ring-amber-500/40 shadow-xl shadow-amber-950/30' 
              : 'bg-slate-900/70 border-slate-800/80 hover:border-amber-500/40 hover:bg-slate-900'
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Free Soon (&lt;30m)</span>
            <div className="w-8 h-8 rounded-xl bg-amber-500/20 text-amber-400 flex items-center justify-center">
              <AlertTriangle className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="font-['Outfit'] text-4xl font-extrabold text-white">
              {overviewData?.free_soon_count ?? '--'}
            </span>
            <span className="text-xs text-amber-400 font-medium">Class ending shortly</span>
          </div>
        </div>

        {/* Total Classrooms */}
        <div 
          onClick={() => setStatusFilter('ALL')}
          className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800/80 hover:border-indigo-500/40 hover:bg-slate-900 transition-all cursor-pointer"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Total Classrooms</span>
            <div className="w-8 h-8 rounded-xl bg-indigo-500/20 text-indigo-400 flex items-center justify-center">
              <Layers className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="font-['Outfit'] text-4xl font-extrabold text-white">
              {overviewData?.total_classrooms ?? '--'}
            </span>
            <span className="text-xs text-indigo-400 font-medium">Across Block A, B, C</span>
          </div>
        </div>
      </div>

      {/* Filters & Search Control Bar */}
      <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 backdrop-blur-xl shadow-xl flex flex-col lg:flex-row items-center justify-between gap-4">
        
        {/* Search input */}
        <div className="relative w-full lg:w-96">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search room (e.g. A-602, Com Lab, Lec Hall)..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-950/70 border border-slate-700/80 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-all"
          />
        </div>

        {/* Dropdown filters */}
        <div className="flex flex-wrap items-center gap-2.5 w-full lg:w-auto justify-end">
          
          {/* Building */}
          <select
            value={selectedBuilding}
            onChange={(e) => setSelectedBuilding(e.target.value)}
            className="px-3 py-2 rounded-xl bg-slate-950/70 border border-slate-700/80 text-xs font-semibold text-slate-200 focus:outline-none focus:border-emerald-500"
          >
            <option value="">All Buildings</option>
            <option value="BLOCK_A">Academic Block A</option>
            <option value="BLOCK_B">Block B / USDI</option>
            <option value="BLOCK_C">Block C</option>
          </select>

          {/* Floor */}
          <select
            value={selectedFloor}
            onChange={(e) => setSelectedFloor(e.target.value)}
            className="px-3 py-2 rounded-xl bg-slate-950/70 border border-slate-700/80 text-xs font-semibold text-slate-200 focus:outline-none focus:border-emerald-500"
          >
            <option value="">All Floors</option>
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

          {/* Room Type */}
          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="px-3 py-2 rounded-xl bg-slate-950/70 border border-slate-700/80 text-xs font-semibold text-slate-200 focus:outline-none focus:border-emerald-500"
          >
            <option value="">All Room Types</option>
            <option value="normal_classroom">Classrooms</option>
            <option value="computer_lab">Computer Labs</option>
            <option value="hardware_lab">Hardware / Electronics Labs</option>
            <option value="robotics_lab">Robotics Labs</option>
            <option value="lecture_theatre">Lecture Theatres</option>
          </select>

          {/* Reset Filters */}
          {(selectedBuilding || selectedFloor !== '' || selectedType || searchQuery || statusFilter !== 'ALL') && (
            <button
              onClick={() => {
                setSelectedBuilding('');
                setSelectedFloor('');
                setSelectedType('');
                setSearchQuery('');
                setStatusFilter('ALL');
              }}
              className="px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-300 transition-colors"
            >
              Reset Filters
            </button>
          )}

        </div>

      </div>

      {/* Classroom Cards Grid */}
      {loading ? (
        <div className="py-20 flex flex-col items-center justify-center space-y-4">
          <div className="w-12 h-12 rounded-full border-4 border-emerald-500/20 border-t-emerald-400 animate-spin" />
          <p className="text-sm font-semibold text-slate-400">Loading campus availability telemetry...</p>
        </div>
      ) : filteredClassrooms.length === 0 ? (
        <div className="py-16 text-center rounded-2xl border border-slate-800 bg-slate-900/50 p-8 space-y-3">
          <div className="w-12 h-12 mx-auto rounded-full bg-slate-800 flex items-center justify-center text-slate-400">
            <Search className="w-6 h-6" />
          </div>
          <h3 className="text-base font-bold text-white">No classrooms match your filters</h3>
          <p className="text-xs text-slate-400 max-w-sm mx-auto">
            Try adjusting your search query, building, or status filter to see available rooms.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredClassrooms.map((room) => (
            <ClassroomCard
              key={room.classroom_id}
              room={room}
              onClick={() => onSelectClassroom(room)}
            />
          ))}
        </div>
      )}

    </div>
  );
}
