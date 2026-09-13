import React, { useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  X, Menu, ChevronRight, Layers, FileCode, Shield, Database, 
  Rocket, Sparkles, FolderUp, LogIn, LogOut, Terminal, CheckCircle2,
  ExternalLink, ArrowUpRight
} from "lucide-react";
import { MagnetButton } from "../ui/MagnetButton";

export interface NavItem {
  id: string;
  label: string;
  icon: React.ReactNode;
  badge?: string;
  badgeColor?: string;
  description?: string;
  onClick: () => void;
  active?: boolean;
}

interface SideStaggerNavigationProps {
  isOpen: boolean;
  onToggle: () => void;
  activeTab?: string;
  onSelectTab?: (tab: "overview" | "code" | "database" | "security" | "deployment") => void;
  onSelectDemoRepo?: (repoKey: string) => void;
  onScrollToDropZone?: () => void;
  onRequireAuth?: () => void;
  isAuthenticated?: boolean;
  currentUser?: { name: string; email: string; role: string } | null;
  onLogout?: () => void;
  activeRepoName?: string;
}

export function SideStaggerNavigation({
  isOpen,
  onToggle,
  activeTab = "overview",
  onSelectTab,
  onSelectDemoRepo,
  onScrollToDropZone,
  onRequireAuth,
  isAuthenticated = false,
  currentUser = null,
  onLogout,
  activeRepoName
}: SideStaggerNavigationProps) {
  // Close on Escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isOpen) {
        onToggle();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onToggle]);

  // Framer Motion staggered animation variants
  const drawerVariants = {
    hidden: { 
      x: "-100%",
      transition: {
        type: "spring",
        stiffness: 300,
        damping: 30,
        staggerChildren: 0.03,
        staggerDirection: -1
      }
    },
    visible: { 
      x: "0%",
      transition: {
        type: "spring",
        stiffness: 300,
        damping: 30,
        staggerChildren: 0.05,
        delayChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { x: -28, opacity: 0 },
    visible: { 
      x: 0, 
      opacity: 1,
      transition: { 
        type: "spring", 
        stiffness: 300, 
        damping: 24 
      }
    }
  };

  const sectionHeaderVariants = {
    hidden: { opacity: 0, y: -8 },
    visible: { 
      opacity: 1, 
      y: 0,
      transition: { duration: 0.2 }
    }
  };

  const navigationSections = [
    {
      title: "Workspace Intelligence",
      items: [
        {
          id: "overview",
          label: "Dashboard Overview",
          icon: <Layers className="w-4 h-4 text-sky-400" />,
          description: "Project health score & active metrics",
          active: activeTab === "overview",
          onClick: () => {
            if (onSelectTab) onSelectTab("overview");
            onToggle();
          }
        },
        {
          id: "code",
          label: "Code Intelligence & Self-Correction",
          icon: <FileCode className="w-4 h-4 text-emerald-400" />,
          badge: "OpenRouter AI",
          badgeColor: "bg-emerald-500/20 text-emerald-300 border-emerald-500/30",
          description: "Inspect code, AST defects & generate fixes",
          active: activeTab === "code",
          onClick: () => {
            if (onSelectTab) onSelectTab("code");
            onToggle();
          }
        },
        {
          id: "database",
          label: "Database Optimization",
          icon: <Database className="w-4 h-4 text-amber-400" />,
          badge: "Optimized",
          badgeColor: "bg-amber-500/20 text-amber-300 border-amber-500/30",
          description: "Slow query profiling & compound B-tree index",
          active: activeTab === "database",
          onClick: () => {
            if (onSelectTab) onSelectTab("database");
            onToggle();
          }
        },
        {
          id: "security",
          label: "Security & Secret Scans",
          icon: <Shield className="w-4 h-4 text-rose-400" />,
          description: "CVE detection, SQLi & exposed API keys",
          active: activeTab === "security",
          onClick: () => {
            if (onSelectTab) onSelectTab("security");
            onToggle();
          }
        },
        {
          id: "deployment",
          label: "Deployment Readiness Gate",
          icon: <Rocket className="w-4 h-4 text-indigo-400" />,
          description: "7-pillar release validation pipeline",
          active: activeTab === "deployment",
          onClick: () => {
            if (onSelectTab) onSelectTab("deployment");
            onToggle();
          }
        }
      ]
    },
    {
      title: "Target Demo Repositories",
      items: [
        {
          id: "ecommerce",
          label: "FastAPI E-Commerce",
          icon: <Terminal className="w-4 h-4 text-sky-400" />,
          badge: "6 files",
          badgeColor: "bg-slate-800 text-slate-300 border-slate-700",
          description: "Orders API, Stripe keys & pyyaml CVE",
          active: activeRepoName === "ecommerce-fastapi",
          onClick: () => {
            if (onSelectDemoRepo) onSelectDemoRepo("ecommerce");
            onToggle();
          }
        },
        {
          id: "fintech",
          label: "Fintech Payment Ledger",
          icon: <Terminal className="w-4 h-4 text-amber-400" />,
          badge: "4 files",
          badgeColor: "bg-slate-800 text-slate-300 border-slate-700",
          description: "Account balance mutations & dynamic SQLi",
          active: activeRepoName === "fintech-payment-ledger",
          onClick: () => {
            if (onSelectDemoRepo) onSelectDemoRepo("fintech");
            onToggle();
          }
        },
        {
          id: "gateway",
          label: "Microservice Gateway",
          icon: <Terminal className="w-4 h-4 text-purple-400" />,
          badge: "4 files",
          badgeColor: "bg-slate-800 text-slate-300 border-slate-700",
          description: "Unbounded cache memory leaks & Docker root",
          active: activeRepoName === "microservice-gateway",
          onClick: () => {
            if (onSelectDemoRepo) onSelectDemoRepo("gateway");
            onToggle();
          }
        }
      ]
    }
  ];

  return (
    <>
      {/* AnimatePresence for smooth backdrop and drawer exit */}
      <AnimatePresence>
        {isOpen && (
          <>
            {/* Backdrop blur overlay */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.25 }}
              onClick={onToggle}
              className="fixed inset-0 bg-black/70 backdrop-blur-sm z-40 cursor-pointer"
            />

            {/* Side Drawer with Staggered Links */}
            <motion.aside
              variants={drawerVariants}
              initial="hidden"
              animate="visible"
              exit="hidden"
              className="fixed top-0 left-0 bottom-0 w-80 md:w-96 bg-slate-950 border-r border-slate-800/90 z-50 flex flex-col shadow-2xl overflow-y-auto"
            >
              {/* Drawer Top Header */}
              <motion.div 
                variants={itemVariants}
                className="p-6 border-b border-slate-800 flex items-center justify-between"
              >
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-sky-400 to-indigo-600 flex items-center justify-center text-black font-black text-sm shadow-lg shadow-sky-500/20">
                    DI
                  </div>
                  <div>
                    <h2 className="text-sm font-extrabold text-white tracking-tight flex items-center gap-1.5">
                      <span>Developer Intelligence</span>
                      <Sparkles className="w-3.5 h-3.5 text-sky-400" />
                    </h2>
                    <p className="text-[11px] text-slate-400 font-mono">OpenRouter + Turso Engine</p>
                  </div>
                </div>

                <MagnetButton
                  variant="ghost"
                  size="icon"
                  onClick={onToggle}
                  className="text-slate-400 hover:text-white"
                >
                  <X className="w-4 h-4" />
                </MagnetButton>
              </motion.div>

              {/* Navigation Stagger Sections */}
              <div className="flex-1 p-5 space-y-6">
                {navigationSections.map((section, sIdx) => (
                  <div key={sIdx} className="space-y-2">
                    <motion.div 
                      variants={sectionHeaderVariants}
                      className="text-[10px] uppercase font-bold text-slate-500 tracking-wider px-2"
                    >
                      {section.title}
                    </motion.div>

                    <div className="space-y-1">
                      {section.items.map((item) => (
                        <motion.button
                          key={item.id}
                          variants={itemVariants}
                          onClick={item.onClick}
                          whileHover={{ x: 6, transition: { duration: 0.15 } }}
                          className={`w-full p-2.5 rounded-xl text-left flex items-center justify-between transition-all group cursor-pointer ${
                            item.active
                              ? "bg-sky-500/15 border border-sky-500/30 text-white shadow-sm"
                              : "hover:bg-slate-900 border border-transparent text-slate-300 hover:text-white"
                          }`}
                        >
                          <div className="flex items-start gap-3">
                            <div className={`p-1.5 rounded-lg shrink-0 mt-0.5 ${item.active ? "bg-sky-500/20" : "bg-slate-900 group-hover:bg-slate-800"}`}>
                              {item.icon}
                            </div>
                            <div>
                              <div className="text-xs font-semibold flex items-center gap-2">
                                <span>{item.label}</span>
                                {item.badge && (
                                  <span className={`text-[10px] font-bold px-1.5 py-0.2 rounded border ${item.badgeColor}`}>
                                    {item.badge}
                                  </span>
                                )}
                              </div>
                              {item.description && (
                                <p className="text-[11px] text-slate-400 line-clamp-1 mt-0.5">
                                  {item.description}
                                </p>
                              )}
                            </div>
                          </div>

                          <ChevronRight className={`w-3.5 h-3.5 text-slate-600 group-hover:text-sky-400 transition-colors ${item.active ? "text-sky-400" : ""}`} />
                        </motion.button>
                      ))}
                    </div>
                  </div>
                ))}

                {/* Quick Drop Zone Link */}
                <motion.div variants={itemVariants} className="pt-2">
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => {
                      if (onScrollToDropZone) onScrollToDropZone();
                      onToggle();
                    }}
                    className="w-full p-3.5 rounded-2xl bg-gradient-to-r from-sky-500/10 via-indigo-500/10 to-purple-500/10 border border-sky-500/30 text-left flex items-center justify-between group cursor-pointer"
                  >
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-xl bg-sky-500/20 text-sky-400">
                        <FolderUp className="w-5 h-5" />
                      </div>
                      <div>
                        <div className="text-xs font-bold text-white flex items-center gap-1.5">
                          <span>Analyze Custom Folder</span>
                          <Sparkles className="w-3 h-3 text-sky-400" />
                        </div>
                        <p className="text-[11px] text-slate-400">Drag & drop your local code repository</p>
                      </div>
                    </div>
                    <ArrowUpRight className="w-4 h-4 text-sky-400 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
                  </motion.button>
                </motion.div>
              </div>

              {/* Drawer Footer with Developer Account & Magnet Actions */}
              <motion.div 
                variants={itemVariants}
                className="p-5 border-t border-slate-800 bg-slate-950/80 backdrop-blur-md space-y-3"
              >
                {isAuthenticated && currentUser ? (
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2.5">
                      <div className="w-8 h-8 rounded-full bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center text-emerald-400 text-xs font-bold font-mono">
                        {currentUser.email.slice(0, 2).toUpperCase()}
                      </div>
                      <div className="overflow-hidden">
                        <div className="text-xs font-bold text-white truncate max-w-[150px] font-mono">
                          {currentUser.email}
                        </div>
                        <div className="text-[10px] text-emerald-400 flex items-center gap-1 font-medium">
                          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                          <span>Developer Authenticated</span>
                        </div>
                      </div>
                    </div>

                    {onLogout && (
                      <MagnetButton
                        variant="danger"
                        size="sm"
                        onClick={() => {
                          onLogout();
                          onToggle();
                        }}
                      >
                        <LogOut className="w-3.5 h-3.5" />
                        <span>Sign Out</span>
                      </MagnetButton>
                    )}
                  </div>
                ) : (
                  <div className="space-y-2">
                    <div className="text-xs text-slate-400">
                      Sign in with OTP to unlock live patch application and cloud persistence.
                    </div>
                    <MagnetButton
                      variant="primary"
                      size="md"
                      className="w-full justify-center"
                      onClick={() => {
                        if (onRequireAuth) onRequireAuth();
                        onToggle();
                      }}
                    >
                      <LogIn className="w-4 h-4" />
                      <span>Sign In with Email & OTP</span>
                    </MagnetButton>
                  </div>
                )}
              </motion.div>
            </motion.aside>
          </>
        )}
      </AnimatePresence>
    </>
  );
}
