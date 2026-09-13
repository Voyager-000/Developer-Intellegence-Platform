'use client';

import React, { useEffect, useRef, useState } from 'react';

export interface CubeMatrixProps {
  children?: React.ReactNode;
  showOverlayText?: boolean;
  className?: string;
}

export default function CubeMatrix({
  children,
  showOverlayText = false,
  className = "",
}: CubeMatrixProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [isDarkMode, setIsDarkMode] = useState<boolean>(true);

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    setIsDarkMode(mediaQuery.matches);
    const handler = (e: MediaQueryListEvent) => setIsDarkMode(e.matches);
    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, []);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d', { alpha: false });
    if (!ctx) return;

    let animationFrameId: number;
    let width = 0;
    let height = 0;

    const mouse = { x: -1000, y: -1000 };

    const handleResize = () => {
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      width = window.innerWidth;
      height = window.innerHeight;
      canvas.width = Math.floor(width * dpr);
      canvas.height = Math.floor(height * dpr);
      canvas.style.width = `${width}px`;
      canvas.style.height = `${height}px`;
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.scale(dpr, dpr);
    };

    const handleMouseMove = (e: MouseEvent) => {
      mouse.x = e.clientX;
      mouse.y = e.clientY;
    };

    handleResize();
    window.addEventListener('resize', handleResize);
    window.addEventListener('mousemove', handleMouseMove);

    let time = 0;

    const render = () => {
      time += 0.025;

      const bgColor = isDarkMode ? '#030712' : '#f8fafc';
      ctx.fillStyle = bgColor;
      ctx.fillRect(0, 0, width, height);

      const size = 28;
      const hSize = (size * Math.sqrt(3)) / 2;

      const cols = Math.ceil(width / (size * 1.5)) + 4;
      const rows = Math.ceil(height / (hSize * 2)) + 4;

      const drawCube = (x: number, y: number, elevation: number) => {
        const topY = y - elevation;

        // Ultra high quality palette definition with subtle depth
        const topColor = isDarkMode ? '#1e293b' : '#e2e8f0';
        const leftColor = isDarkMode ? '#0f172a' : '#cbd5e1';
        const rightColor = isDarkMode ? '#334155' : '#94a3b8';
        const accentTop = isDarkMode ? '#38bdf8' : '#2563eb';
        const strokeColor = isDarkMode ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.06)';
        const accentStroke = isDarkMode ? 'rgba(125, 211, 252, 0.4)' : 'rgba(37, 99, 235, 0.3)';

        const isElevated = elevation > 9;

        // Top Face
        ctx.fillStyle = isElevated ? accentTop : topColor;
        ctx.beginPath();
        ctx.moveTo(x, topY - size / 2);
        ctx.lineTo(x + hSize, topY - size / 4);
        ctx.lineTo(x, topY);
        ctx.lineTo(x - hSize, topY - size / 4);
        ctx.closePath();
        ctx.fill();
        ctx.strokeStyle = isElevated ? accentStroke : strokeColor;
        ctx.lineWidth = 0.5;
        ctx.stroke();

        // Left Face
        ctx.fillStyle = leftColor;
        ctx.beginPath();
        ctx.moveTo(x - hSize, topY - size / 4);
        ctx.lineTo(x, topY);
        ctx.lineTo(x, topY + size / 2);
        ctx.lineTo(x - hSize, topY + size / 4);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();

        // Right Face
        ctx.fillStyle = rightColor;
        ctx.beginPath();
        ctx.moveTo(x + hSize, topY - size / 4);
        ctx.lineTo(x, topY);
        ctx.lineTo(x, topY + size / 2);
        ctx.lineTo(x + hSize, topY + size / 4);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();
      };

      for (let r = -2; r < rows; r++) {
        for (let c = -2; c < cols; c++) {
          const x = c * size * 1.5;
          const y = r * hSize * 2 + (c % 2 === 0 ? 0 : hSize);

          const wave = Math.sin(c * 0.3 + r * 0.3 + time) * 8;

          // Mouse proximity calculation
          const dx = mouse.x - x;
          const dy = mouse.y - y;
          const dist = Math.sqrt(dx * dx + dy * dy);

          let mouseElevation = 0;
          if (dist < 190) {
            mouseElevation = (1 - dist / 190) * 36;
          }

          drawCube(x, y, wave + mouseElevation);
        }
      }

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('mousemove', handleMouseMove);
    };
  }, [isDarkMode]);

  return (
    <div className={`relative w-full min-h-screen overflow-hidden select-none bg-[#030712] ${className}`}>
      {/* 3D Isometric Voxel Canvas */}
      <canvas
        ref={canvasRef}
        className="fixed inset-0 w-full h-full block cursor-default pointer-events-none z-0"
      />

      {/* Subtle Vignette Overlay for Depth & Contrast */}
      <div className="fixed inset-0 pointer-events-none bg-[radial-gradient(ellipse_at_center,transparent_40%,rgba(3,7,18,0.7)_100%)] z-0" />

      {/* Standalone Demo Text */}
      {showOverlayText && (
        <div className="relative z-10 flex h-full min-h-screen flex-col items-center justify-center text-center px-4 pointer-events-none mix-blend-difference text-white">
          <span className="font-mono text-xs tracking-widest uppercase mb-3 text-sky-400">
            Developer Intelligence Visual Core
          </span>
          <h1 className="font-mono text-6xl md:text-9xl font-black tracking-tighter uppercase leading-none">
            VOXEL
          </h1>
          <p className="mt-4 font-mono text-xs md:text-sm max-w-lg opacity-80">
            Dynamic 3D voxel heightmap oscillating with continuous sine harmonics and mouse elevation fields.
          </p>
        </div>
      )}

      {/* Embedded Children (e.g. Radial Orbital Wheel Pipeline) */}
      {children && (
        <div className="relative z-10 w-full min-h-screen pointer-events-auto">
          {children}
        </div>
      )}
    </div>
  );
}

export { CubeMatrix };
