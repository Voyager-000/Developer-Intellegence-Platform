import React, { useState, useEffect, useRef } from "react";
import { ArrowRight, Link, Zap } from "lucide-react";
import { motion, useMotionValue, useSpring, useTransform } from "framer-motion";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { FlowHoverButton } from "@/components/ui/flow-hover-button";

export interface NodeColorScheme {
  bg: string;
  text: string;
  border: string;
  glow: string;
  badgeBg: string;
  iconBg?: string;
}

export interface TimelineItem {
  id: number;
  title: string;
  date: string;
  content: string;
  category: string;
  icon: React.ElementType;
  relatedIds: number[];
  status: "completed" | "in-progress" | "pending";
  energy?: number;
  metricLabel?: string;
  metricValue?: string;
  cardWidthClass?: string;
  customCardContent?: React.ReactNode;
  colorScheme?: NodeColorScheme;
}

export interface RadialOrbitalTimelineProps {
  timelineData: TimelineItem[];
  onNodeClick?: (id: number) => void;
  defaultExpandedId?: number;
  className?: string;
}

// Flow-Hover Button Node Component matching the requested liquid hover effect
function FlowHoverNodeButton({
  item,
  isExpanded,
  isRelated,
  isPulsing,
  onClick,
}: {
  item: TimelineItem;
  isExpanded: boolean;
  isRelated: boolean;
  isPulsing: boolean;
  onClick: (e: React.MouseEvent) => void;
}) {
  const Icon = item.icon;

  return (
    <div className="relative flex items-center justify-center">
      {/* Dark Protective Halo Shield (Guarantees contrast against Trippy background) */}
      <div className="absolute -inset-2.5 rounded-lg bg-black/95 blur-md pointer-events-none -z-20 shadow-2xl" />

      <button
        onClick={onClick}
        className={cn(
          `relative cursor-pointer z-0 flex items-center justify-center gap-2 overflow-hidden rounded-md 
          border border-zinc-300 dark:border-zinc-700 bg-zinc-100 dark:bg-zinc-800 
          px-4 py-2 font-semibold text-zinc-800 dark:text-zinc-200 transition-all duration-500
          before:absolute before:inset-0 before:-z-10 before:translate-x-[150%] before:translate-y-[150%] before:scale-[2.5]
          before:rounded-[100%] before:bg-zinc-800 dark:before:bg-zinc-200 before:transition-transform before:duration-1000 before:content-[""]
          hover:scale-105 hover:text-zinc-100 dark:hover:text-zinc-900 hover:before:translate-x-[0%] hover:before:translate-y-[0%] active:scale-95 shadow-xl`,
          isExpanded &&
            "ring-2 ring-white border-zinc-100 text-zinc-900 dark:text-zinc-900 before:translate-x-[0%] before:translate-y-[0%] scale-105 shadow-[0_0_35px_rgba(255,255,255,0.6)]",
          isRelated && "ring-2 ring-zinc-400/80 animate-pulse"
        )}
      >
        <span className="w-4 h-4 flex items-center justify-center shrink-0">
          <Icon size={14} className="currentColor" />
        </span>
        <span className="text-xs tracking-tight whitespace-nowrap">
          {item.title}
        </span>

        {/* Active status pulse dot */}
        {item.status === "in-progress" ? (
          <span className="relative flex h-2 w-2 ml-0.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-sky-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-sky-400"></span>
          </span>
        ) : item.status === "completed" ? (
          <span className="text-[10px] opacity-70 font-mono">✓</span>
        ) : (
          <span className="text-[10px] opacity-60 font-mono">•</span>
        )}
      </button>
    </div>
  );
}

export default function RadialOrbitalTimeline({
  timelineData,
  onNodeClick,
  defaultExpandedId = 1,
  className = "",
}: RadialOrbitalTimelineProps) {
  const [expandedItems, setExpandedItems] = useState<Record<number, boolean>>(() => {
    return defaultExpandedId ? { [defaultExpandedId]: true } : {};
  });
  const [viewMode] = useState<"orbital">("orbital");
  const [rotationAngle, setRotationAngle] = useState<number>(0);
  const [autoRotate, setAutoRotate] = useState<boolean>(() => !defaultExpandedId);
  const [pulseEffect, setPulseEffect] = useState<Record<number, boolean>>({});
  const [centerOffset] = useState<{ x: number; y: number }>({
    x: 0,
    y: 0,
  });
  const [activeNodeId, setActiveNodeId] = useState<number | null>(() => defaultExpandedId || null);
  const containerRef = useRef<HTMLDivElement>(null);
  const orbitRef = useRef<HTMLDivElement>(null);
  const nodeRefs = useRef<Record<number, HTMLDivElement | null>>({});

  const handleContainerClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === containerRef.current || e.target === orbitRef.current) {
      setExpandedItems({});
      setActiveNodeId(null);
      setPulseEffect({});
      setAutoRotate(true);
    }
  };

  const toggleItem = (id: number) => {
    if (onNodeClick) onNodeClick(id);

    setExpandedItems((prev) => {
      const newState = { ...prev };
      Object.keys(newState).forEach((key) => {
        if (parseInt(key) !== id) {
          newState[parseInt(key)] = false;
        }
      });

      newState[id] = !prev[id];

      if (!prev[id]) {
        setActiveNodeId(id);
        setAutoRotate(false);

        const relatedItems = getRelatedItems(id);
        const newPulseEffect: Record<number, boolean> = {};
        relatedItems.forEach((relId) => {
          newPulseEffect[relId] = true;
        });
        setPulseEffect(newPulseEffect);

        centerViewOnNode(id);
      } else {
        setActiveNodeId(null);
        setAutoRotate(true);
        setPulseEffect({});
      }

      return newState;
    });
  };

  useEffect(() => {
    let rotationTimer: any;

    if (autoRotate && viewMode === "orbital") {
      rotationTimer = setInterval(() => {
        setRotationAngle((prev) => {
          const newAngle = (prev + 0.25) % 360;
          return Number(newAngle.toFixed(3));
        });
      }, 50);
    }

    return () => {
      if (rotationTimer) {
        clearInterval(rotationTimer);
      }
    };
  }, [autoRotate, viewMode]);

  useEffect(() => {
    if (defaultExpandedId) {
      const timer = setTimeout(() => {
        centerViewOnNode(defaultExpandedId);
      }, 150);
      return () => clearTimeout(timer);
    }
  }, [defaultExpandedId]);

  const centerViewOnNode = (nodeId: number) => {
    if (viewMode !== "orbital" || !nodeRefs.current[nodeId]) return;

    const nodeIndex = timelineData.findIndex((item) => item.id === nodeId);
    const totalNodes = timelineData.length;
    const targetAngle = (nodeIndex / totalNodes) * 360;

    setRotationAngle(270 - targetAngle);
  };

  const calculateNodePosition = (index: number, total: number) => {
    const angle = ((index / total) * 360 + rotationAngle) % 360;
    const radius = 230; // Radius providing comfortable spacing for pill buttons
    const radian = (angle * Math.PI) / 180;

    const x = radius * Math.cos(radian) + centerOffset.x;
    const y = radius * Math.sin(radian) + centerOffset.y;

    const zIndex = Math.round(100 + 50 * Math.cos(radian));

    return { x, y, angle, zIndex };
  };

  const getRelatedItems = (itemId: number): number[] => {
    const currentItem = timelineData.find((item) => item.id === itemId);
    return currentItem ? currentItem.relatedIds : [];
  };

  const isRelatedToActive = (itemId: number): boolean => {
    if (!activeNodeId) return false;
    const relatedItems = getRelatedItems(activeNodeId);
    return relatedItems.includes(itemId);
  };

  const getStatusStyles = (status: TimelineItem["status"]): string => {
    switch (status) {
      case "completed":
        return "text-white bg-black border-white";
      case "in-progress":
        return "text-black bg-white border-black font-bold";
      case "pending":
        return "text-white bg-black/60 border-white/40";
      default:
        return "text-white bg-black/60 border-white/40";
    }
  };

  return (
    <div
      className={`w-full h-full flex flex-col items-center justify-center overflow-hidden bg-transparent ${className}`}
      ref={containerRef}
      onClick={handleContainerClick}
    >
      <div className="relative w-full max-w-4xl h-full flex items-center justify-center">
        <div
          className="absolute w-full h-full flex items-center justify-center"
          ref={orbitRef}
          style={{
            perspective: "1000px",
            transform: `translate(${centerOffset.x}px, ${centerOffset.y}px)`,
          }}
        >
          {/* Central Neural Hub with Pulsing Aura */}
          <div className="absolute w-20 h-20 rounded-full bg-black/95 border-2 border-white/50 flex items-center justify-center z-10 shadow-[0_0_50px_rgba(255,255,255,0.25)]">
            <div className="absolute -inset-2 rounded-full border border-white/30 animate-ping opacity-35"></div>
            <div className="w-11 h-11 rounded-full bg-gradient-to-tr from-sky-400 to-indigo-500 flex items-center justify-center text-white font-mono text-xs font-black shadow-lg shadow-sky-500/50">
              <Zap size={18} className="text-white" />
            </div>
          </div>

          {/* High-Contrast Orbit Guide Ring */}
          <div className="absolute w-[460px] h-[460px] rounded-full border border-white/25 shadow-[0_0_50px_rgba(255,255,255,0.05)] pointer-events-none"></div>

          {/* Render All Orbiting Magnet Button Nodes */}
          {timelineData.map((item, index) => {
            const position = calculateNodePosition(index, timelineData.length);
            const isExpanded = expandedItems[item.id];
            const isRelated = isRelatedToActive(item.id);
            const isPulsing = pulseEffect[item.id];
            const Icon = item.icon;

            const nodeStyle = {
              transform: `translate(${position.x}px, ${position.y}px)`,
              zIndex: isExpanded ? 300 : position.zIndex,
            };

            return (
              <div
                key={item.id}
                ref={(el) => (nodeRefs.current[item.id] = el)}
                className="absolute transition-transform duration-700 -translate-x-1/2 -translate-y-1/2"
                style={nodeStyle}
              >
                {/* Flow-Hover Button Node */}
                <FlowHoverNodeButton
                  item={item}
                  isExpanded={isExpanded}
                  isRelated={isRelated}
                  isPulsing={isPulsing}
                  onClick={(e) => {
                    e.stopPropagation();
                    toggleItem(item.id);
                  }}
                />

                {/* Expanded Detail / Ingestion Card */}
                {isExpanded && (
                  <Card
                    onClick={(e) => e.stopPropagation()}
                    className={`absolute top-14 left-1/2 -translate-x-1/2 ${
                      item.cardWidthClass || "w-80 sm:w-96"
                    } max-h-[75vh] overflow-y-auto bg-slate-950/95 backdrop-blur-2xl border-2 ${
                      item.colorScheme?.border || "border-white/40"
                    } shadow-2xl shadow-black z-50 rounded-2xl`}
                  >
                    <div className="absolute -top-3 left-1/2 -translate-x-1/2 w-px h-3 bg-white"></div>
                    <CardHeader className="pb-2 pt-4 px-4">
                      <div className="flex justify-between items-center">
                        <Badge
                          className={`px-2 text-[10px] uppercase font-mono tracking-wider ${
                            item.colorScheme?.badgeBg || getStatusStyles(item.status)
                          }`}
                        >
                          {item.status === "completed"
                            ? "COMPLETE"
                            : item.status === "in-progress"
                            ? "ACTIVE STAGE"
                            : "STANDBY"}
                        </Badge>
                        <span className="text-[11px] font-mono text-white/60">
                          {item.date}
                        </span>
                      </div>
                      <CardTitle className="text-sm font-black text-white mt-2 flex items-center gap-2">
                        <div className={`w-5 h-5 rounded-full flex items-center justify-center ${item.colorScheme?.bg || "bg-white text-black"}`}>
                          <Icon size={12} className={item.colorScheme?.text || "text-black"} />
                        </div>
                        <span>{item.title}</span>
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="text-xs text-white/80 px-4 pb-4">
                      <p className="leading-relaxed text-slate-300">{item.content}</p>

                      {/* Custom In-Node Interactive Content (Drop Zone, Demo Selectors, etc.) */}
                      {item.customCardContent && (
                        <div className="mt-3 pt-3 border-t border-white/15">
                          {item.customCardContent}
                        </div>
                      )}

                      {/* Realistic Metrics / Status (High-Contrast, No Fake Numbers) */}
                      {item.energy !== undefined && item.energy > 0 ? (
                        <div className="mt-3 pt-3 border-t border-white/15">
                          <div className="flex justify-between items-center text-xs mb-1">
                            <span className="flex items-center text-slate-300 font-medium">
                              <Zap size={11} className="mr-1 text-sky-400" />
                              {item.metricLabel || "Pipeline Energy"}
                            </span>
                            <span className="font-mono text-white font-bold">{item.energy}%</span>
                          </div>
                          <div className="w-full h-1.5 bg-white/20 rounded-full overflow-hidden">
                            <div
                              className={`h-full ${item.colorScheme?.bg || "bg-white"}`}
                              style={{ width: `${item.energy}%` }}
                            ></div>
                          </div>
                        </div>
                      ) : (
                        <div className="mt-3 pt-3 border-t border-white/15 flex items-center justify-between text-xs">
                          <span className="flex items-center text-slate-400">
                            <Zap size={11} className="mr-1 text-white/70" />
                            {item.metricLabel || "Stage Status"}
                          </span>
                          <span className="font-mono text-[11px] px-2 py-0.5 rounded bg-white/10 border border-white/20 text-white font-semibold">
                            {item.metricValue || "Standby — Awaiting Ingestion"}
                          </span>
                        </div>
                      )}

                      {item.relatedIds.length > 0 && (
                        <div className="mt-3 pt-3 border-t border-white/15">
                          <div className="flex items-center mb-2">
                            <Link size={10} className="text-white/70 mr-1" />
                            <h4 className="text-[10px] uppercase tracking-wider font-semibold text-white/60">
                              Connected Pipeline Stages
                            </h4>
                          </div>
                          <div className="flex flex-wrap gap-2">
                            {item.relatedIds.map((relatedId) => {
                              const relatedItem = timelineData.find(
                                (i) => i.id === relatedId
                              );
                              return (
                                <FlowHoverButton
                                  key={relatedId}
                                  className="h-7 px-2.5 py-1 text-[11px] font-semibold border-zinc-700 bg-zinc-900 text-zinc-200 before:bg-zinc-200 hover:text-zinc-900"
                                  icon={<ArrowRight size={10} className="order-last ml-0.5" />}
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    toggleItem(relatedId);
                                  }}
                                >
                                  {relatedItem?.title}
                                </FlowHoverButton>
                              );
                            })}
                          </div>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
