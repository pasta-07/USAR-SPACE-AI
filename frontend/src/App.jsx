import React, { useState, useEffect, useCallback } from 'react';
import Navbar from './components/Navbar';
import TimeMachineBar from './components/TimeMachineBar';
import ClassroomModal from './components/ClassroomModal';
import CosmicBackground from './components/CosmicBackground';
import PasscodeGateway from './components/PasscodeGateway';
import AvailableNowPage from './pages/AvailableNowPage';
import FindRoomPage from './pages/FindRoomPage';
import FloorMapPage from './pages/FloorMapPage';
import TimetableAnalyticsPage from './pages/TimetableAnalyticsPage';
import AdminPage from './pages/AdminPage';
import { api } from './services/api';
import { THEMES } from './utils/themes';
import { Code, Heart, Sparkles, Terminal, Lock } from 'lucide-react';

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    return localStorage.getItem('usar_space_auth') === 'pasta_alfredo_granted';
  });

  const [activeTab, setActiveTab] = useState('available');
  const [selectedClassroom, setSelectedClassroom] = useState(null);
  const [currentTheme, setCurrentTheme] = useState('cosmic'); // 'cosmic' | 'mission_control' | 'synthwave' | 'aurora'
  
  // Time Machine states (null = live IST)
  const [simulatedTime, setSimulatedTime] = useState(null);
  const [simulatedDay, setSimulatedDay] = useState(null);
  const [showTimeMachine, setShowTimeMachine] = useState(false);

  // Overview data
  const [overviewData, setOverviewData] = useState(null);
  const [loading, setLoading] = useState(true);

  const themeObj = THEMES[currentTheme] || THEMES.cosmic;

  const handleUnlock = () => {
    localStorage.setItem('usar_space_auth', 'pasta_alfredo_granted');
    setIsAuthenticated(true);
  };

  const handleLock = () => {
    localStorage.removeItem('usar_space_auth');
    setIsAuthenticated(false);
  };

  // Fetch live availability overview
  const fetchOverview = useCallback(async (isBackground = false) => {
    if (!isBackground) setLoading(true);
    try {
      const data = await api.getAvailableNow({
        simulatedTime,
        simulatedDay
      });
      setOverviewData(data);
    } catch (err) {
      console.error('Failed to fetch classroom availability overview:', err);
    } finally {
      if (!isBackground) setLoading(false);
    }
  }, [simulatedTime, simulatedDay]);

  // Initial load and on time shift (when authenticated)
  useEffect(() => {
    if (isAuthenticated) {
      fetchOverview();
    }
  }, [fetchOverview, isAuthenticated]);

  // Auto-refresh ticker every 30 seconds
  useEffect(() => {
    if (!isAuthenticated) return;
    const interval = setInterval(() => {
      // Only auto-refresh in live mode
      if (!simulatedTime && !simulatedDay) {
        fetchOverview(true);
      }
    }, 30000);
    return () => clearInterval(interval);
  }, [fetchOverview, simulatedTime, simulatedDay, isAuthenticated]);

  const handleResetTimeMachine = () => {
    setSimulatedTime(null);
    setSimulatedDay(null);
  };

  return (
    <div className={`min-h-screen bg-gradient-to-br ${themeObj.bg} text-slate-100 flex flex-col font-['Space_Grotesk'] relative selection:bg-emerald-400 selection:text-slate-950 transition-colors duration-500`}>
      
      {/* Living Cosmic Neural Background */}
      <CosmicBackground theme={themeObj} />

      {/* Password Protection Gateway if Not Authenticated */}
      {!isAuthenticated ? (
        <PasscodeGateway onUnlock={handleUnlock} theme={themeObj} />
      ) : (
        <>
          {/* Top Navbar */}
          <Navbar
            activeTab={activeTab}
            setActiveTab={setActiveTab}
            simulatedTime={simulatedTime}
            simulatedDay={simulatedDay}
            showTimeMachine={showTimeMachine}
            setShowTimeMachine={setShowTimeMachine}
            overviewData={overviewData}
            currentTheme={currentTheme}
            setCurrentTheme={setCurrentTheme}
            onLock={handleLock}
          />

          {/* Campus Time Machine Bar (when toggled or active) */}
          {(showTimeMachine || simulatedTime || simulatedDay) && (
            <TimeMachineBar
              simulatedTime={simulatedTime}
              setSimulatedTime={setSimulatedTime}
              simulatedDay={simulatedDay}
              setSimulatedDay={setSimulatedDay}
              onReset={handleResetTimeMachine}
              onClose={() => setShowTimeMachine(false)}
            />
          )}

          {/* Main Page Content */}
          <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 relative z-10">
            
            {activeTab === 'available' && (
              <AvailableNowPage
                simulatedTime={simulatedTime}
                simulatedDay={simulatedDay}
                overviewData={overviewData}
                loading={loading}
                onRefresh={() => fetchOverview(false)}
                onSelectClassroom={(room) => setSelectedClassroom(room)}
                onNavigateToSearch={() => setActiveTab('search')}
              />
            )}

            {activeTab === 'search' && (
              <FindRoomPage
                simulatedTime={simulatedTime}
                simulatedDay={simulatedDay}
                onSelectClassroom={(room) => setSelectedClassroom(room)}
              />
            )}

            {activeTab === 'map' && (
              <FloorMapPage
                simulatedTime={simulatedTime}
                simulatedDay={simulatedDay}
                onSelectClassroom={(room) => setSelectedClassroom(room)}
              />
            )}

            {activeTab === 'analytics' && (
              <TimetableAnalyticsPage
                onSelectClassroom={(room) => setSelectedClassroom(room)}
              />
            )}

            {activeTab === 'admin' && (
              <AdminPage
                onRefreshAvailability={() => fetchOverview(false)}
              />
            )}

          </main>

          {/* Classroom Detailed Modal */}
          {selectedClassroom && (
            <ClassroomModal
              classroom={selectedClassroom}
              onClose={() => setSelectedClassroom(null)}
              simulatedTime={simulatedTime}
              simulatedDay={simulatedDay}
            />
          )}

          {/* Futuristic HUD Footer with Developer Credit */}
          <footer className="border-t border-slate-900/90 bg-slate-950/90 backdrop-blur-xl py-10 px-4 sm:px-6 lg:px-8 mt-16 text-center space-y-4 relative z-10 font-mono">
            
            {/* Creator Badge */}
            <div className="flex flex-wrap items-center justify-center gap-3">
              <div className="inline-flex items-center gap-2.5 px-4 py-2 rounded-2xl bg-gradient-to-r from-emerald-500/15 via-indigo-500/15 to-purple-500/15 border border-emerald-500/30 text-xs shadow-lg shadow-emerald-500/10">
                <Terminal className="w-3.5 h-3.5 text-emerald-400" />
                <span className="text-slate-300 font-sans">Architected & Developed by</span>
                <span className="font-['Outfit'] font-black text-sm tracking-wide text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 via-teal-300 to-indigo-300">
                  Pranav Siroha
                </span>
                <Sparkles className="w-3.5 h-3.5 text-amber-400" />
              </div>
            </div>

            {/* System telemetry bar */}
            <div className="flex items-center justify-center gap-2 text-xs text-slate-500">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span className="font-bold text-slate-400">USAR SPACE AI • CAMPUS INTELLIGENCE SYSTEM</span>
              <span>•</span>
              <span className="text-emerald-400/90 font-semibold">{themeObj.name}</span>
            </div>

            <p className="text-[11px] text-slate-500 max-w-xl mx-auto font-sans">
              University School of Automation and Robotics (USAR), GGSIPU East Delhi Campus • Odd Semester 2026-27
            </p>

          </footer>
        </>
      )}

    </div>
  );
}
