import React, { useRef, useState } from "react";
import { useTransform, useScroll, motion, useMotionValueEvent, AnimatePresence } from "motion/react";
import { FlowHoverButton } from "@/components/ui/flow-hover-button";
import { Sparkles, ArrowDown, Compass, ArrowLeft } from "lucide-react";

export interface TrippyScrollProps {
  children?: React.ReactNode;
  className?: string;
  onOpenWheel?: () => void;
  onBack?: () => void;
}

const NUM_SECTIONS = 25;
const PADDING = `${100 / NUM_SECTIONS / 2}vmin`;

const generateSections = (count: number, color: string, rotate: any): React.ReactNode => {
  if (count === NUM_SECTIONS) {
    return <></>;
  }

  const nextColor = color === "black" ? "white" : "black";

  return (
    <Section rotate={rotate} background={color} key={count}>
      {generateSections(count + 1, nextColor, rotate)}
    </Section>
  );
};

const Trippy = ({ rotate }: { rotate: any }) => {
  return (
    <motion.div className="absolute inset-0 overflow-hidden bg-black select-none pointer-events-none">
      {generateSections(0, "black", rotate)}
    </motion.div>
  );
};

const Section = ({
  background,
  children,
  rotate,
}: {
  background: string;
  children: React.ReactNode;
  rotate: any;
}) => {
  return (
    <motion.div
      className="relative h-full w-full origin-center"
      style={{
        background,
        rotate,
        padding: PADDING,
      }}
    >
      {children}
    </motion.div>
  );
};

export default function TrippyScroll({
  children,
  className = "",
  onOpenWheel,
  onBack,
}: TrippyScrollProps) {
  const targetRef = useRef<HTMLDivElement>(null);
  const [scrollProgress, setScrollProgress] = useState(0);

  const { scrollYProgress } = useScroll({
    target: targetRef,
  });

  const rotate = useTransform(scrollYProgress, [0, 1], ["0deg", "90deg"]);

  useMotionValueEvent(scrollYProgress, "change", (latest) => {
    setScrollProgress(latest);
  });

  const rawPercent = Math.round(scrollProgress * 100);
  const is100Percent = rawPercent >= 100 || scrollProgress >= 0.985;
  const displayPercent = is100Percent ? 100 : Math.min(99, rawPercent);

  return (
    <div ref={targetRef} className={`relative z-0 h-[800vh] bg-black ${className}`}>
      <div className="sticky top-0 h-screen w-full overflow-hidden bg-black flex flex-col justify-between">
        {/* Infinite Monochrome Vortex Background */}
        <Trippy rotate={rotate} />

        {/* Top Floating HUD Bar */}
        <div className="relative z-30 w-full px-6 py-4 flex items-center justify-between pointer-events-auto">
          <div className="flex items-center gap-3">
            {onBack && (
              <FlowHoverButton
                onClick={onBack}
                className="h-8 px-3 text-xs border-zinc-700 bg-black/85 text-zinc-200 before:bg-zinc-200 hover:text-zinc-900 backdrop-blur-md"
                icon={<ArrowLeft className="w-3.5 h-3.5" />}
              >
                Back to Home
              </FlowHoverButton>
            )}
            {onOpenWheel && (
              <FlowHoverButton
                onClick={onOpenWheel}
                className="h-8 px-3 text-xs border-white bg-white text-black before:bg-zinc-950 hover:text-white"
                icon={<Sparkles className="w-3.5 h-3.5" />}
              >
                Skip to Pipeline
              </FlowHoverButton>
            )}
          </div>
        </div>

        {/* Center copy: always visible so the tunnel reads as a designed sequence */}
        <div className="relative z-20 flex-1 flex items-center justify-center pointer-events-none px-4">
          <AnimatePresence mode="wait">
            {!is100Percent && (
              <motion.div
                key="vortex-intro"
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -12 }}
                className="relative pointer-events-none max-w-lg w-full text-center"
              >
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-black/80 border border-white/30 text-[10px] font-mono uppercase tracking-[0.2em] text-white mb-4">
                  <Compass className="w-3.5 h-3.5" />
                  Ingestion Vortex
                </div>
                <h2 className="text-4xl sm:text-5xl font-black text-white tracking-tight drop-shadow-[0_0_24px_rgba(0,0,0,0.9)]">
                  Traverse the Tunnel
                </h2>
                <p className="mt-3 text-sm text-zinc-200 font-mono leading-relaxed drop-shadow-[0_0_16px_rgba(0,0,0,0.9)]">
                  Scroll through the monochrome singularity to align the 5-stage orbital pipeline.
                </p>
              </motion.div>
            )}
            {is100Percent && (
              <motion.div
                key="vortex-complete"
                initial={{ opacity: 0, scale: 0.9, y: 20 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.9, y: 20 }}
                transition={{ duration: 0.35, ease: "easeOut" }}
                className="relative pointer-events-auto max-w-xl w-full p-8 sm:p-10 rounded-3xl bg-black border-2 border-white shadow-[0_0_120px_rgba(0,0,0,1),0_0_60px_rgba(255,255,255,0.4)] text-center flex flex-col items-center gap-6 z-30"
              >
                {/* Solid Dark Protective Halo Shield */}
                <div className="absolute -inset-4 bg-black/95 rounded-[32px] blur-xl -z-10 pointer-events-none" />

                <div className="w-16 h-16 rounded-2xl border-2 border-white bg-white/10 flex items-center justify-center text-white shadow-2xl">
                  <Compass className="w-8 h-8 animate-spin text-white" style={{ animationDuration: "10s" }} />
                </div>

                <div className="space-y-2">
                  <span className="text-xs font-mono uppercase tracking-widest text-emerald-400 font-bold px-3 py-1 rounded-full bg-emerald-950/60 border border-emerald-500/40 inline-block">
                    Singularity Traversed • 100% Ingestion Alignment
                  </span>
                  <h2 className="text-3xl sm:text-4xl font-black text-white tracking-tight leading-tight">
                    The Orbital Pipeline Awaits
                  </h2>
                  <p className="text-xs sm:text-sm text-zinc-200 mt-2 font-mono leading-relaxed max-w-md mx-auto">
                    Dimensional vortex traversed. Launch the 5-node Developer Intelligence architecture running on the 3D Voxel Matrix heightmap.
                  </p>
                </div>

                {onOpenWheel && (
                  <div className="pt-2 w-full flex justify-center">
                    <FlowHoverButton
                      onClick={onOpenWheel}
                      className="px-10 py-4 text-base font-black border-2 border-white bg-white text-black before:bg-zinc-950 hover:text-white shadow-[0_0_50px_rgba(255,255,255,0.9)] cursor-pointer tracking-wider uppercase"
                      icon={<Sparkles className="w-5 h-5 text-sky-500" />}
                    >
                      Open The Wheel
                    </FlowHoverButton>
                  </div>
                )}
              </motion.div>
            )}
          </AnimatePresence>

          {/* Any custom children embedded */}
          {children}
        </div>

        {/* Bottom Floating Scroll Nudge - Only shown during scroll, hides when 100% traversed */}
        <div className="relative z-30 pb-8 flex flex-col items-center justify-center pointer-events-auto min-h-[48px]">
          {!is100Percent && (
            <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-black/90 border border-white/40 text-white text-xs font-mono backdrop-blur-md shadow-2xl animate-bounce">
              <ArrowDown className="w-3.5 h-3.5 text-zinc-400" />
              <span>Scroll to traverse vortex ({displayPercent}%)</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export { Trippy, Section };
