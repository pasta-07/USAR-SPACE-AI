import React, { useState } from 'react';
import { Lock, Unlock, KeyRound, Sparkles, ShieldCheck, AlertCircle, ArrowRight, School, Code2 } from 'lucide-react';

export default function PasscodeGateway({ onUnlock, theme }) {
  const [passcode, setPasscode] = useState('');
  const [error, setError] = useState(false);
  const [isUnlocking, setIsUnlocking] = useState(false);

  const CORRECT_PASSCODE = 'pasta_alfredo';

  const handleSubmit = (e) => {
    e.preventDefault();
    if (passcode.trim() === CORRECT_PASSCODE) {
      setIsUnlocking(true);
      setError(false);
      setTimeout(() => {
        onUnlock();
      }, 700);
    } else {
      setError(true);
      setPasscode('');
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#030712]/95 backdrop-blur-2xl font-['Space_Grotesk'] selection:bg-emerald-500 selection:text-black">
      
      {/* Background ambient lighting */}
      <div className="absolute w-96 h-96 bg-emerald-500/15 rounded-full blur-3xl pointer-events-none top-1/4 left-1/4" />
      <div className="absolute w-96 h-96 bg-indigo-500/15 rounded-full blur-3xl pointer-events-none bottom-1/4 right-1/4" />

      <div className="relative w-full max-w-md bg-slate-900/90 border border-slate-700/80 rounded-3xl p-8 shadow-2xl shadow-black/80 text-center space-y-6 animate-in zoom-in-95 duration-300">
        
        {/* Top Lock Icon Badge */}
        <div className="relative mx-auto w-20 h-20 rounded-3xl bg-gradient-to-tr from-emerald-500 via-teal-500 to-indigo-600 p-[2px] shadow-xl shadow-emerald-500/20">
          <div className="w-full h-full bg-[#030712] rounded-[22px] flex items-center justify-center relative overflow-hidden">
            {isUnlocking ? (
              <Unlock className="w-10 h-10 text-emerald-400 animate-bounce" />
            ) : (
              <Lock className="w-10 h-10 text-emerald-400 animate-pulse" />
            )}
            <div className="absolute inset-0 bg-emerald-500/10" />
          </div>
        </div>

        {/* Title and Subtitle */}
        <div className="space-y-1.5">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-mono font-semibold">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>AUTHENTICATION GATEWAY</span>
          </div>

          <h2 className="font-['Outfit'] text-3xl font-black text-white tracking-tight">
            USAR SPACE AI
          </h2>

          <p className="text-slate-400 text-xs leading-relaxed max-w-xs mx-auto">
            This campus intelligence portal is password-protected. Enter the designated access key to proceed.
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-500">
              <KeyRound className="w-4 h-4" />
            </div>
            <input
              type="password"
              value={passcode}
              onChange={(e) => {
                setPasscode(e.target.value);
                setError(false);
              }}
              placeholder="Enter Access Password..."
              autoFocus
              className={`w-full pl-11 pr-4 py-3.5 rounded-2xl bg-slate-950/80 border text-sm text-slate-100 placeholder-slate-500 focus:outline-none transition-all font-mono ${
                error 
                  ? 'border-rose-500 ring-2 ring-rose-500/30 focus:border-rose-500' 
                  : 'border-slate-700/80 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/30'
              }`}
            />
          </div>

          {error && (
            <div className="flex items-center justify-center gap-2 text-xs font-semibold text-rose-400 animate-in fade-in slide-in-from-top-1">
              <AlertCircle className="w-4 h-4" />
              <span>Incorrect password. Access denied.</span>
            </div>
          )}

          <button
            type="submit"
            disabled={!passcode.trim() || isUnlocking}
            className={`w-full py-3.5 rounded-2xl font-bold text-sm tracking-wider uppercase transition-all shadow-lg flex items-center justify-center gap-2 ${
              isUnlocking
                ? 'bg-emerald-500 text-slate-950 shadow-emerald-500/40 scale-95'
                : passcode.trim()
                ? 'bg-gradient-to-r from-emerald-500 via-teal-500 to-indigo-600 hover:from-emerald-400 hover:to-teal-400 text-slate-950 shadow-emerald-500/25 hover:scale-[1.02] active:scale-[0.98]'
                : 'bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700'
            }`}
          >
            {isUnlocking ? (
              <>
                <Sparkles className="w-4 h-4 animate-spin" />
                <span>Decrypting Terminal...</span>
              </>
            ) : (
              <>
                <span>Unlock Terminal</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </form>

        {/* Creator Attribution */}
        <div className="pt-4 border-t border-slate-800/80 flex items-center justify-center gap-2 text-slate-500 text-[11px] font-mono">
          <Code2 className="w-3.5 h-3.5 text-indigo-400" />
          <span>Developed by <strong className="text-slate-300">Pranav Siroha</strong></span>
        </div>

      </div>
    </div>
  );
}
