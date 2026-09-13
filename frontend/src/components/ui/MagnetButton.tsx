import React, { useRef, useState } from "react";
import { motion, useMotionValue, useSpring, useTransform } from "framer-motion";

export interface MagnetButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
  variant?: "primary" | "secondary" | "success" | "danger" | "ghost" | "glass";
  size?: "sm" | "md" | "lg" | "icon";
  strength?: number; // Magnetic pull strength (0.1 to 0.6)
  className?: string;
  onClick?: (e: React.MouseEvent<HTMLButtonElement>) => void;
  disabled?: boolean;
}

export function MagnetButton({
  children,
  variant = "primary",
  size = "md",
  strength = 0.35,
  className = "",
  onClick,
  disabled = false,
  ...props
}: MagnetButtonProps) {
  const buttonRef = useRef<HTMLButtonElement>(null);
  const [isHovered, setIsHovered] = useState(false);

  // Raw mouse delta from button center
  const x = useMotionValue(0);
  const y = useMotionValue(0);

  // Smooth physics-based spring response
  const springConfig = { damping: 14, stiffness: 160, mass: 0.15 };
  const springX = useSpring(x, springConfig);
  const springY = useSpring(y, springConfig);

  // Subtle secondary parallax shift for the inner text / icon
  const innerX = useTransform(springX, (val) => val * 0.25);
  const innerY = useTransform(springY, (val) => val * 0.25);

  const handleMouseMove = (e: React.MouseEvent<HTMLButtonElement>) => {
    if (disabled || !buttonRef.current) return;
    const { clientX, clientY } = e;
    const { left, top, width, height } = buttonRef.current.getBoundingClientRect();
    const centerX = left + width / 2;
    const centerY = top + height / 2;

    const deltaX = (clientX - centerX) * strength;
    const deltaY = (clientY - centerY) * strength;

    x.set(deltaX);
    y.set(deltaY);
  };

  const handleMouseEnter = () => {
    if (!disabled) setIsHovered(true);
  };

  const handleMouseLeave = () => {
    setIsHovered(false);
    x.set(0);
    y.set(0);
  };

  // Base styling for variants
  const variantStyles = {
    primary:
      "bg-gradient-to-r from-sky-400 to-cyan-400 hover:from-sky-300 hover:to-cyan-300 text-slate-950 font-bold shadow-lg shadow-sky-500/25 border border-sky-300/40",
    secondary:
      "bg-slate-900/90 hover:bg-slate-800 text-slate-200 hover:text-white border border-slate-800 hover:border-slate-700 shadow-sm",
    success:
      "bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold shadow-lg shadow-emerald-500/25 border border-emerald-400/40",
    danger:
      "bg-slate-900 hover:bg-rose-950/40 text-rose-300 hover:text-rose-200 border border-rose-500/40 hover:border-rose-500/60 shadow-sm",
    ghost:
      "bg-transparent hover:bg-slate-900/80 text-slate-400 hover:text-white border border-transparent hover:border-slate-800",
    glass:
      "bg-slate-950/60 hover:bg-slate-900/80 backdrop-blur-md text-sky-300 hover:text-sky-200 border border-sky-500/30 hover:border-sky-500/50 shadow-md shadow-sky-500/10"
  };

  const sizeStyles = {
    sm: "px-3 py-1.5 text-xs rounded-lg gap-1.5",
    md: "px-4 py-2 text-xs font-semibold rounded-xl gap-2",
    lg: "px-6 py-3 text-sm font-bold rounded-2xl gap-2.5",
    icon: "p-2 text-xs rounded-xl"
  };

  return (
    <motion.button
      ref={buttonRef}
      style={{
        x: springX,
        y: springY
      }}
      whileTap={!disabled ? { scale: 0.94 } : undefined}
      onMouseMove={handleMouseMove}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      onClick={onClick}
      disabled={disabled}
      className={`relative inline-flex items-center justify-center transition-colors cursor-pointer select-none disabled:opacity-50 disabled:cursor-not-allowed disabled:pointer-events-none ${variantStyles[variant]} ${sizeStyles[size]} ${className}`}
      {...(props as any)}
    >
      <motion.div
        style={{
          x: innerX,
          y: innerY
        }}
        className="flex items-center justify-center gap-2 pointer-events-none"
      >
        {children}
      </motion.div>
    </motion.button>
  );
}
