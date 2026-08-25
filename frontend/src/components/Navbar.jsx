import React, { useState, useEffect } from 'react';
import { 
  Compass, 
  Search, 
  Layers, 
  Calendar, 
  ShieldCheck, 
  Clock, 
  SlidersHorizontal,
  Sparkles,
  School,
  Palette,
  ChevronDown,
  Activity,
  Code2,
  Lock
} from 'lucide-react';
import { THEMES } from '../utils/themes';

export default function Navbar({ 
  activeTab, 
  setActiveTab, 
  simulatedTime, 
  simulatedDay,
  showTimeMachine,
  setShowTimeMachine,
  overviewData,
  currentTheme,
  setCurrentTheme,
  onLock
}) {
  const [currentTimeStr, setCurrentTimeStr] = useState('');
  const [currentDateStr, setCurrentDateStr] = useState('');
  const [showThemeMenu, setShowThemeMenu] = useState(false);

  // Live ticking IST clock
  useEffect(() => {
    const updateClock = () => {
      const now = new Date();
      const istOptions = { timeZone: 'Asia/Kolkata', hour12: true, hour: '2-digit', minute: '2-digit', second: '2-digit' };
      const dateOptions = { timeZone: 'Asia/Kolkata', weekday: 'short', month: 'short', day: 'numeric' };
      setCurrentTimeStr(now.toLocaleTimeString('en-US', istOptions));
      setCurrentDateStr(now.toLocaleDateString('en-US', dateOptions));
    };

    updateClock();
    const interval = setInterval(updateClock, 1000);
    return () => clearInterval(interval);
  }, []);

  const navItems = [
    { id: 'available', label: 'Available Now', icon: Compass },
    { id: 'search', label: 'Find a Room', icon: Search },
    { id: 'map', label: 'Campus Map', icon: Layers },
    { id: 'analytics', label: 'Timetables', icon: Calendar },
    { id: 'admin', label: 'Admin Center', icon: ShieldCheck },
  ];

  const isSimulated = Boolean(simulatedTime || simulatedDay);
  const themeObj = THEMES[currentTheme] || THEMES.cosmic;

  return (
    <header className="sticky top-0 z-40 w-full backdrop-blur-2xl bg-slate-950/85 border-b border-slate-800/80 shadow-2xl shadow-black/50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-20">
          
          {/* Logo & College Title + Dev Credit */}
          <div className="flex items-center gap-3.5 cursor-pointer group" onClick={() => setActiveTab('available')}>
            <div className="relative flex items-center justify-center w-12 h-12 rounded-2xl bg-gradient-to-tr from-emerald-400 via-teal-500 to-indigo-600 p-[2px] shadow-lg shadow-emerald-500/25 group-hover:shadow-emerald-500/50 transition-all duration-300">
              <div className="w-full h-full bg-[#030712] rounded-[14px] flex items-center justify-center relative overflow-hidden">
                <School className="w-6 h-6 text-emerald-400 group-hover:scale-110 transition-transform duration-300 z-10" />
                <div className="absolute inset-0 bg-emerald-500/10 animate-pulse" />
              </div>
              <span className="absolute -top-1 -right-1 flex h-3.5 w-3.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3.5 w-3.5 bg-emerald-500 ring-2 ring-slate-950"></span>
              </span>
            </div>
            
            <div>
              <div className="flex items-center gap-2">
                <span className="font-['Outfit'] font-black text-2xl tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-100 to-emerald-400">
                  USAR SPACE AI
                </span>
                <span className="px-2 py-0.5 text-[9px] font-mono font-bold uppercase tracking-wider rounded-md bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
                  {themeObj.badge}
                </span>
              </div>
              <div className="flex items-center gap-2 mt-0.5">
                <p className="text-[10px] text-slate-400 font-mono tracking-wider">
                  CAMPUS INTELLIGENCE
                </p>
                <span className="text-slate-600 text-[10px]">•</span>
                <div className="inline-flex items-center gap-1 px-1.5 py-0.2 rounded bg-indigo-500/15 border border-indigo-500/30 text-[10px] font-mono font-semibold text-indigo-300">
                  <Code2 className="w-2.5 h-2.5 text-indigo-400" />
                  <span>By Pranav Siroha</span>
                </div>
              </div>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center gap-1 p-1.5 rounded-2xl bg-slate-900/90 border border-slate-800/90 shadow-inner">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold uppercase tracking-wider transition-all duration-200 ${
                    isActive
                      ? 'bg-gradient-to-r from-emerald-500/25 to-indigo-500/25 text-white border border-emerald-400/50 shadow-lg shadow-emerald-500/15'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                  }`}
                >
                  <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-emerald-400' : 'text-slate-400'}`} />
                  <span>{item.label}</span>
                  {item.id === 'available' && overviewData && (
                    <span className="ml-1 px-1.5 py-0.5 text-[10px] font-mono font-black rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                      {overviewData.available_now_count}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>

          {/* Right Action Widgets: Theme Switcher, Live Clock, Time Machine & Lock */}
          <div className="flex items-center gap-2.5">
            
            {/* Iconic Theme Selector Dropdown */}
            <div className="relative">
              <button
                onClick={() => setShowThemeMenu(!showThemeMenu)}
                className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 hover:border-slate-700 text-xs font-semibold text-slate-200 transition-all shadow-sm"
                title="Change Iconic Theme"
              >
                <span>{themeObj.icon}</span>
                <span className="hidden sm:inline font-mono">{themeObj.name.split(' ')[0]}</span>
                <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
              </button>

              {showThemeMenu && (
                <div className="absolute right-0 mt-2 w-56 rounded-2xl bg-slate-900/95 border border-slate-700/80 shadow-2xl p-2 z-50 backdrop-blur-xl animate-in fade-in zoom-in-95 duration-150 space-y-1 font-sans">
                  <div className="px-3 py-1.5 text-[10px] font-mono uppercase font-bold text-slate-400 border-b border-slate-800">
                    Select Iconic Theme
                  </div>
                  {Object.values(THEMES).map((t) => (
                    <button
                      key={t.id}
                      onClick={() => {
                        setCurrentTheme(t.id);
                        setShowThemeMenu(false);
                      }}
                      className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-semibold text-left transition-all ${
                        currentTheme === t.id
                          ? 'bg-gradient-to-r from-emerald-500/20 to-indigo-500/20 text-white border border-emerald-500/40'
                          : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                      }`}
                    >
                      <span className="text-base">{t.icon}</span>
                      <div className="flex-1">
                        <p className="font-bold">{t.name}</p>
                        <p className="text-[10px] text-slate-500 font-mono">{t.badge}</p>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Live Clock Pill */}
            <div className={`hidden lg:flex items-center gap-2.5 px-3.5 py-2 rounded-xl border text-xs font-mono transition-colors ${
              isSimulated 
                ? 'bg-amber-500/10 border-amber-500/30 text-amber-300' 
                : 'bg-slate-900/90 border-slate-800 text-slate-300'
            }`}>
              <Clock className={`w-3.5 h-3.5 ${isSimulated ? 'text-amber-400 animate-pulse' : 'text-emerald-400'}`} />
              <div className="flex flex-col text-right">
                <span className="font-bold">{isSimulated ? simulatedTime || currentTimeStr : currentTimeStr}</span>
                <span className="text-[9px] text-slate-400">{isSimulated ? `${simulatedDay} (SIM)` : `${currentDateStr} IST`}</span>
              </div>
            </div>

            {/* Time Machine Toggle */}
            <button
              onClick={() => setShowTimeMachine(!showTimeMachine)}
              className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-bold uppercase tracking-wider border transition-all ${
                showTimeMachine || isSimulated
                  ? 'bg-gradient-to-r from-indigo-500/25 to-purple-500/25 text-indigo-200 border-indigo-400/50 shadow-md shadow-indigo-500/20'
                  : 'bg-slate-900 hover:bg-slate-800 text-slate-300 border-slate-800'
              }`}
              title="Campus Time Machine Simulator"
            >
              <SlidersHorizontal className={`w-3.5 h-3.5 ${isSimulated ? 'text-amber-400 animate-spin' : 'text-indigo-400'}`} />
              <span className="hidden sm:inline">Time Machine</span>
              {isSimulated && (
                <span className="w-2 h-2 rounded-full bg-amber-400 animate-ping"></span>
              )}
            </button>

            {/* Lock Button */}
            {onLock && (
              <button
                onClick={onLock}
                className="p-2 rounded-xl bg-slate-900 border border-slate-800 hover:border-rose-500/50 hover:bg-rose-500/10 text-slate-400 hover:text-rose-400 transition-colors"
                title="Lock Terminal (Requires password to unlock)"
              >
                <Lock className="w-4 h-4" />
              </button>
            )}
          </div>

        </div>

        {/* Mobile Navigation bar */}
        <div className="flex md:hidden items-center justify-around py-2.5 border-t border-slate-800/60 overflow-x-auto">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`flex flex-col items-center gap-1 px-3 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-wider ${
                  isActive ? 'text-emerald-400 font-bold' : 'text-slate-400'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </div>

      </div>
    </header>
  );
}
