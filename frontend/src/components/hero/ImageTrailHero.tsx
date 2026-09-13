import React, { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowDown } from "lucide-react";
import codeEditor3d from "../../assets/trail/code-editor-3d.jpeg";
import ironmanGraffiti from "../../assets/trail/ironman-graffiti.jpeg";
import ninjaCoder from "../../assets/trail/ninja-coder.jpeg";
import spidermanNewspaper from "../../assets/trail/spiderman-newspaper.jpeg";
import steampunkClockwork from "../../assets/trail/steampunk-clockwork.jpeg";
import ironmanStark from "../../assets/trail/ironman-stark.jpeg";
import scifiHud from "../../assets/trail/scifi-hud.jpeg";
import spidermanComic from "../../assets/trail/spiderman-comic.jpeg";

interface TrailImage {
  id: number;
  x: number;
  y: number;
  rotation: number;
  src: string;
}

const HERO_IMAGES = [
  codeEditor3d,
  ironmanGraffiti,
  ninjaCoder,
  spidermanNewspaper,
  steampunkClockwork,
  ironmanStark,
  scifiHud,
  spidermanComic,
];

interface ImageTrailHeroProps {
  onOpenAuth: () => void;
  onOpenOrbitalPipeline: () => void;
  onScrollToDropZone: () => void;
  currentUser?: { email: string; name: string; role: string } | null;
  onLogout?: () => void;
}

export function ImageTrailHero({
  onOpenAuth,
  onOpenOrbitalPipeline,
  onScrollToDropZone,
  currentUser,
  onLogout,
}: ImageTrailHeroProps) {
  const [trail, setTrail] = useState<TrailImage[]>([]);
  const containerRef = useRef<HTMLDivElement>(null);
  const lastPosRef = useRef<{ x: number; y: number }>({ x: 0, y: 0 });
  const imageIndexRef = useRef<number>(0);
  const idCounterRef = useRef<number>(0);

  const handlePointerMove = (e: React.PointerEvent<HTMLDivElement>) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const dx = x - lastPosRef.current.x;
    const dy = y - lastPosRef.current.y;
    const distance = Math.sqrt(dx * dx + dy * dy);

    // Hover.dev distance threshold: spawn image every 50px of movement
    if (distance > 50) {
      lastPosRef.current = { x, y };
      const currentImage = HERO_IMAGES[imageIndexRef.current % HERO_IMAGES.length];
      imageIndexRef.current += 1;

      const randomRotation = (Math.random() - 0.5) * 24; // -12deg to +12deg
      const newImage: TrailImage = {
        id: idCounterRef.current++,
        x,
        y,
        rotation: randomRotation,
        src: currentImage,
      };

      setTrail((prev) => [...prev.slice(-9), newImage]);
    }
  };

  useEffect(() => {
    if (trail.length === 0) return;
    const timer = setTimeout(() => {
      setTrail((prev) => prev.slice(1));
    }, 1100);
    return () => clearTimeout(timer);
  }, [trail]);

  return (
    <div
      ref={containerRef}
      onPointerMove={handlePointerMove}
      className="relative h-screen min-h-[640px] w-full overflow-hidden bg-[#dde3ec] text-[#0a0f1d] select-none flex flex-col justify-between p-6 sm:p-12"
    >
      {/* 1. BACKGROUND MOVING WATERMARK TEXT (Continuous Seamless Drifting Rows) */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none select-none flex flex-col justify-between py-4 z-0">
        {/* Row 1: Drifting Left */}
        <div className="flex overflow-hidden whitespace-nowrap">
          <motion.div
            animate={{ x: ["0%", "-50%"] }}
            transition={{ repeat: Infinity, duration: 32, ease: "linear" }}
            className="flex whitespace-nowrap text-[#c5cfdd] font-black text-[12vw] sm:text-[9.5vw] uppercase tracking-normal leading-[0.88] select-none"
          >
            <span className="pr-12">ACTIVATED GENERATE MOTIVATED AUTOMATE SCALE SHIP CODE</span>
            <span className="pr-12">ACTIVATED GENERATE MOTIVATED AUTOMATE SCALE SHIP CODE</span>
          </motion.div>
        </div>

        {/* Row 2: Drifting Right */}
        <div className="flex overflow-hidden whitespace-nowrap">
          <motion.div
            animate={{ x: ["-50%", "0%"] }}
            transition={{ repeat: Infinity, duration: 36, ease: "linear" }}
            className="flex whitespace-nowrap text-[#c5cfdd] font-black text-[12vw] sm:text-[9.5vw] uppercase tracking-normal leading-[0.88] select-none"
          >
            <span className="pr-12">INSPIRED PASSION CODE STRIX SECURITY AUDIT ZERO VULNERABILITY</span>
            <span className="pr-12">INSPIRED PASSION CODE STRIX SECURITY AUDIT ZERO VULNERABILITY</span>
          </motion.div>
        </div>

        {/* Row 3: Drifting Left */}
        <div className="flex overflow-hidden whitespace-nowrap">
          <motion.div
            animate={{ x: ["0%", "-50%"] }}
            transition={{ repeat: Infinity, duration: 38, ease: "linear" }}
            className="flex whitespace-nowrap text-[#c5cfdd] font-black text-[12vw] sm:text-[9.5vw] uppercase tracking-normal leading-[0.88] select-none"
          >
            <span className="pr-12">PASSION FIRE AUTONOMOUS OPENROUTER LLM VALIDATED REPOSITORIES</span>
            <span className="pr-12">PASSION FIRE AUTONOMOUS OPENROUTER LLM VALIDATED REPOSITORIES</span>
          </motion.div>
        </div>

        {/* Row 4: Drifting Right */}
        <div className="flex overflow-hidden whitespace-nowrap">
          <motion.div
            animate={{ x: ["-50%", "0%"] }}
            transition={{ repeat: Infinity, duration: 34, ease: "linear" }}
            className="flex whitespace-nowrap text-[#c5cfdd] font-black text-[12vw] sm:text-[9.5vw] uppercase tracking-normal leading-[0.88] select-none"
          >
            <span className="pr-12">EMPIRE OF AUTOMATION DYNAMIC DATABASE BENCHMARK 100% HEALTH</span>
            <span className="pr-12">EMPIRE OF AUTOMATION DYNAMIC DATABASE BENCHMARK 100% HEALTH</span>
          </motion.div>
        </div>
      </div>

      {/* 2. TOP BAR (Double Slanted Logo + Login & Sign Up Controls) */}
      <div className="relative z-20 w-full flex items-center justify-between">
        {/* Left: Double slanted black parallelogram icon (matches screenshot) */}
        <div
          className="cursor-pointer flex items-center gap-2"
          onClick={onScrollToDropZone}
          title="Developer Intelligence"
        >
          <svg className="w-9 h-9 text-[#0a0f1d] fill-current" viewBox="0 0 28 28">
            <path d="M4 16l6-11h6l-6 11H4z" />
            <path d="M10 21l6-11h6l-6 11H10z" />
          </svg>
          <span className="font-extrabold text-xs tracking-tight text-[#0a0f1d] font-mono uppercase hidden sm:inline-block">
            Developer Intelligence
          </span>
        </div>

        {/* Right: Orbital Pipeline, Log In & Sign Up buttons */}
        <div className="flex items-center gap-2 sm:gap-3">
          {currentUser ? (
            <>
              <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-300/80 border border-slate-400/50 text-xs font-mono text-slate-800">
                <span className="w-2 h-2 rounded-full bg-emerald-600 animate-pulse"></span>
                <span className="truncate max-w-[140px]">{currentUser.email}</span>
              </div>
              <button
                type="button"
                onClick={onOpenOrbitalPipeline}
                className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-[#5b5df4] hover:bg-[#4f51e8] text-white text-xs sm:text-sm font-semibold shadow-sm active:scale-95 transition-all cursor-pointer"
              >
                <span>Orbital Pipeline</span>
              </button>
              {onLogout && (
                <button
                  type="button"
                  onClick={onLogout}
                  className="inline-flex items-center px-3.5 py-2 rounded-lg bg-slate-900/90 hover:bg-slate-900 text-white text-xs sm:text-sm font-semibold shadow-sm transition-all cursor-pointer active:scale-95"
                >
                  <span>Log Out</span>
                </button>
              )}
            </>
          ) : (
            <>
              <button
                type="button"
                onClick={onOpenOrbitalPipeline}
                className="hidden sm:inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-slate-300/80 hover:bg-slate-300 text-slate-800 text-xs font-bold uppercase tracking-wider transition-all cursor-pointer shadow-sm active:scale-95"
              >
                <span>Orbital Pipeline</span>
              </button>
              <button
                type="button"
                onClick={onOpenAuth}
                className="inline-flex items-center px-4 py-2 rounded-lg bg-slate-900/90 hover:bg-slate-900 text-white text-xs sm:text-sm font-semibold shadow-sm transition-all cursor-pointer active:scale-95"
              >
                <span>Log In</span>
              </button>
              <button
                type="button"
                onClick={onOpenAuth}
                className="inline-flex items-center px-4 py-2 rounded-lg bg-[#5b5df4] hover:bg-[#4f51e8] text-white text-xs sm:text-sm font-semibold shadow-sm active:scale-95 transition-all cursor-pointer"
              >
                <span>Sign Up / OTP</span>
              </button>
            </>
          )}
        </div>
      </div>

      {/* 3. MOUSE IMAGE TRAIL (Hover.dev Interactive Cursor Trails) */}
      <div className="pointer-events-none absolute inset-0 overflow-hidden z-10">
        <AnimatePresence>
          {trail.map((item) => (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, scale: 0.45, rotate: 0 }}
              animate={{ opacity: 1, scale: 1, rotate: item.rotation }}
              exit={{ opacity: 0, scale: 0.5, transition: { duration: 0.3 } }}
              transition={{ type: "spring", stiffness: 320, damping: 24 }}
              style={{
                position: "absolute",
                left: item.x - 90,
                top: item.y - 90,
              }}
              className="w-44 h-44 sm:w-56 sm:h-56 rounded-2xl overflow-hidden shadow-2xl border-2 border-slate-400/60 bg-slate-900"
            >
              <img
                src={item.src}
                alt="Developer Snapshot"
                className="w-full h-full object-cover pointer-events-none filter contrast-110"
              />
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {/* 4. MAIN CENTER-LEFT HEADLINE (Project copy in exact Hover.dev theme) */}
      <div className="relative z-20 max-w-4xl my-auto py-6">
        <div className="text-xs font-mono font-bold text-slate-600 uppercase tracking-widest mb-2">
          Autonomous Deep Inspection
        </div>
        <h1 className="text-6xl sm:text-7xl md:text-8xl lg:text-[7.2rem] font-black text-[#0a0f1d] tracking-tight leading-[0.94]">
          Drop Any Repository <br />
          To <span className="text-[#5b5df4]">Scan</span>
        </h1>
      </div>

      {/* 5. BOTTOM BAR: SUBTEXT CARD (LEFT) + CIRCULAR DOWN ARROW (RIGHT) */}
      <div className="relative z-20 w-full flex flex-col sm:flex-row items-start sm:items-end justify-between gap-6">
        {/* Bottom-Left Subtext Card (Exact project needs in same theme) */}
        <div className="bg-[#cbd5e1]/45 backdrop-blur-sm p-4 sm:p-5 rounded-xl max-w-lg border border-slate-300/60 shadow-sm">
          <p className="text-slate-700 text-xs sm:text-sm leading-relaxed font-medium">
            Zero configuration required. AST parsing, Strix pentesting, database latency, and 5-stage validation.
          </p>
        </div>

        {/* Bottom-Right Circular Button with Down Arrow (Exact match from screenshot) */}
        <button
          type="button"
          onClick={onScrollToDropZone}
          aria-label="Scroll to Workspace"
          className="w-16 h-16 sm:w-20 sm:h-20 rounded-full border-2 border-slate-600 hover:border-slate-800 bg-transparent flex items-center justify-center transition-all duration-200 group cursor-pointer shadow-sm shrink-0 active:scale-90"
        >
          <ArrowDown className="w-8 h-8 sm:w-9 sm:h-9 text-slate-700 group-hover:translate-y-1 transition-transform" />
        </button>
      </div>
    </div>
  );
}
