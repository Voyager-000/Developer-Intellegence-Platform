import React, { useState, useEffect } from "react";
import { 
  ShieldCheck, Users, KeyRound, Sparkles, RefreshCw, 
  Search, Download, ArrowLeft, LogOut, CheckCircle2, 
  Clock, Globe, Laptop, Database, Filter
} from "lucide-react";
import { FlowHoverButton } from "@/components/ui/flow-hover-button";
import { API_BASE_URL } from "@/lib/api";

interface UserRecord {
  id: string;
  name: string;
  email: string;
  role: string;
  auth_provider: string;
  login_count: number;
  last_login_at: string | null;
  created_at: string | null;
}

interface LoginEventRecord {
  id: string;
  user_id?: string;
  username: string;
  email: string;
  auth_method: string;
  ip_address: string;
  region: string;
  created_at: string | null;
}

interface AdminDashboardProps {
  onBackToLanding: () => void;
  onLogout: () => void;
}

export function AdminDashboard({ onBackToLanding, onLogout }: AdminDashboardProps) {
  const [users, setUsers] = useState<UserRecord[]>([]);
  const [loginHistory, setLoginHistory] = useState<LoginEventRecord[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [providerFilter, setProviderFilter] = useState<string>("all");
  const [activeTab, setActiveTab] = useState<"users" | "history">("users");

  const fetchAdminData = async () => {
    setIsLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/auth/admin/users`);
      if (res.ok) {
        const data = await res.json();
        if (data.data) {
          setUsers(data.data.users || []);
          setLoginHistory(data.data.login_history || []);
          // Also save in localStorage as cache
          localStorage.setItem("dev_intel_cached_users", JSON.stringify(data.data.users || []));
          localStorage.setItem("dev_intel_cached_logins", JSON.stringify(data.data.login_history || []));
        }
      } else {
        throw new Error("API returned non-200");
      }
    } catch (err) {
      console.warn("Could not fetch from backend, loading cached records:", err);
      const cachedUsers = localStorage.getItem("dev_intel_cached_users");
      const cachedLogins = localStorage.getItem("dev_intel_cached_logins");
      if (cachedUsers) setUsers(JSON.parse(cachedUsers));
      if (cachedLogins) setLoginHistory(JSON.parse(cachedLogins));
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchAdminData();
  }, []);

  const formatDate = (isoString: string | null) => {
    if (!isoString) return "N/A";
    try {
      const date = new Date(isoString);
      return date.toLocaleString("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      });
    } catch {
      return isoString;
    }
  };

  const getRelativeTime = (isoString: string | null) => {
    if (!isoString) return "";
    try {
      const diffMs = Date.now() - new Date(isoString).getTime();
      const diffMins = Math.floor(diffMs / 60000);
      if (diffMins < 1) return "Just now";
      if (diffMins < 60) return `${diffMins}m ago`;
      const diffHours = Math.floor(diffMins / 60);
      if (diffHours < 24) return `${diffHours}h ago`;
      const diffDays = Math.floor(diffHours / 24);
      return `${diffDays}d ago`;
    } catch {
      return "";
    }
  };

  // Filtered Users
  const filteredUsers = users.filter((u) => {
    const matchesSearch =
      u.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      u.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
      u.id.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesProvider =
      providerFilter === "all" || u.auth_provider.toLowerCase() === providerFilter.toLowerCase();
    return matchesSearch && matchesProvider;
  });

  // Filtered Login History
  const filteredHistory = loginHistory.filter((ev) => {
    const matchesSearch =
      ev.username.toLowerCase().includes(searchQuery.toLowerCase()) ||
      ev.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
      ev.ip_address.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesProvider =
      providerFilter === "all" || ev.auth_method.toLowerCase() === providerFilter.toLowerCase();
    return matchesSearch && matchesProvider;
  });

  const exportCSV = () => {
    const headers = ["ID", "Name", "Email", "Role", "Auth Provider", "Login Count", "Last Login", "Registered At"];
    const rows = filteredUsers.map((u) => [
      u.id,
      `"${u.name}"`,
      `"${u.email}"`,
      u.role,
      u.auth_provider,
      u.login_count,
      u.last_login_at || "",
      u.created_at || "",
    ]);
    const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows.map((e) => e.join(","))].join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `developer_intelligence_users_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const getProviderBadge = (provider: string) => {
    switch (provider.toLowerCase()) {
      case "google":
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-500/15 border border-emerald-500/30 text-emerald-300">
            <Globe className="w-3 h-3 text-emerald-400" /> Google OAuth
          </span>
        );
      case "admin_passcode":
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-rose-500/20 border border-rose-500/40 text-rose-300">
            <ShieldCheck className="w-3 h-3 text-rose-400" /> Passcode 01122005
          </span>
        );
      case "password":
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-slate-800 border border-slate-700 text-slate-300">
            <Laptop className="w-3 h-3" /> Password
          </span>
        );
      case "otp":
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-sky-500/15 border border-sky-500/30 text-sky-300">
            <KeyRound className="w-3 h-3 text-sky-400" /> Email + OTP
          </span>
        );
    }
  };

  return (
    <div className="min-h-screen bg-[#06080d] text-slate-100 flex flex-col font-sans selection:bg-rose-500 selection:text-white">
      {/* Top Admin Header */}
      <header className="h-16 border-b border-rose-500/20 bg-slate-950/90 px-6 sm:px-12 flex items-center justify-between backdrop-blur-md sticky top-0 z-40">
        <div className="flex items-center gap-3">
          <FlowHoverButton
            onClick={onBackToLanding}
            className="h-8 px-3 text-xs border-slate-700 bg-slate-900 text-slate-200 before:bg-white hover:text-black"
            icon={<ArrowLeft className="w-3.5 h-3.5" />}
          >
            Back to Platform
          </FlowHoverButton>

          <div className="h-4 w-[1px] bg-slate-800 hidden sm:block" />

          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-500 animate-ping" />
            <span className="text-xs font-black uppercase tracking-wider text-rose-400 font-mono">
              Admin Console
            </span>
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-rose-500/20 text-rose-300 border border-rose-500/40 font-mono">
              Level 5 Clearance
            </span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={fetchAdminData}
            disabled={isLoading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-700 bg-slate-900/80 hover:bg-slate-800 text-xs font-medium text-slate-300 transition-all cursor-pointer"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? "animate-spin text-sky-400" : ""}`} />
            <span className="hidden sm:inline">Refresh Data</span>
          </button>

          <button
            onClick={exportCSV}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-emerald-500/40 bg-emerald-950/40 hover:bg-emerald-900/50 text-xs font-medium text-emerald-300 transition-all cursor-pointer"
          >
            <Download className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Export CSV</span>
          </button>

          <FlowHoverButton
            onClick={onLogout}
            className="h-8 px-3 text-xs border-rose-500/50 bg-rose-950/60 text-rose-200 before:bg-rose-500 hover:text-white"
            icon={<LogOut className="w-3.5 h-3.5" />}
          >
            Sign Out
          </FlowHoverButton>
        </div>
      </header>

      {/* Main Admin Content Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-6 sm:p-10 space-y-8">
        {/* Welcome Banner */}
        <div className="relative overflow-hidden rounded-3xl p-6 sm:p-8 bg-gradient-to-r from-rose-950/50 via-slate-900 to-slate-950 border border-rose-500/30 shadow-2xl">
          <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-rose-500/20 text-rose-300 border border-rose-500/30 text-xs font-mono mb-2">
                <ShieldCheck className="w-3.5 h-3.5 text-rose-400" />
                <span>Superuser Mode Activated via Passcode 01122005</span>
              </div>
              <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
                Developer Intelligence User Activity & Access Registry
              </h1>
              <p className="text-xs sm:text-sm text-slate-300 mt-1 max-w-2xl leading-relaxed">
                Complete audit ledger tracking all active authentication sessions, login dates, emails used, usernames, and authentication mechanisms across Turso Cloud and local memory.
              </p>
            </div>

            <div className="flex items-center gap-3">
              <div className="text-right font-mono hidden sm:block">
                <div className="text-xs text-slate-400">Database Engine</div>
                <div className="text-sm font-bold text-emerald-400 flex items-center justify-end gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                  Turso libSQL Cloud
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* 4 Analytics Metrics Cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
          <div className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-lg">
            <div className="flex items-center justify-between text-xs font-mono text-slate-400 mb-2">
              <span>TOTAL USERS</span>
              <Users className="w-4 h-4 text-sky-400" />
            </div>
            <div className="text-3xl font-black text-white">{users.length}</div>
            <div className="text-[11px] text-slate-400 mt-1">Unique registered identities</div>
          </div>

          <div className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-lg">
            <div className="flex items-center justify-between text-xs font-mono text-slate-400 mb-2">
              <span>LOGIN SESSIONS</span>
              <Clock className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="text-3xl font-black text-white">{loginHistory.length || users.length}</div>
            <div className="text-[11px] text-slate-400 mt-1">Total recorded logins</div>
          </div>

          <div className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-lg">
            <div className="flex items-center justify-between text-xs font-mono text-slate-400 mb-2">
              <span>EMAIL + OTP LOGINS</span>
              <KeyRound className="w-4 h-4 text-indigo-400" />
            </div>
            <div className="text-3xl font-black text-white">
              {users.filter((u) => u.auth_provider === "otp").length}
            </div>
            <div className="text-[11px] text-slate-400 mt-1">Direct passwordless users</div>
          </div>

          <div className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-lg">
            <div className="flex items-center justify-between text-xs font-mono text-slate-400 mb-2">
              <span>GOOGLE OAUTH</span>
              <Globe className="w-4 h-4 text-amber-400" />
            </div>
            <div className="text-3xl font-black text-white">
              {users.filter((u) => u.auth_provider === "google").length}
            </div>
            <div className="text-[11px] text-slate-400 mt-1">Google authenticated devs</div>
          </div>
        </div>

        {/* Controls: Search, Filter, and Tab Switcher */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4 pt-2">
          {/* Tabs */}
          <div className="flex items-center gap-2 p-1 rounded-xl bg-slate-900/90 border border-slate-800">
            <button
              onClick={() => setActiveTab("users")}
              className={`px-4 py-2 rounded-lg text-xs font-bold transition-all ${
                activeTab === "users"
                  ? "bg-rose-500 text-white shadow-md"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              Registered Users ({filteredUsers.length})
            </button>
            <button
              onClick={() => setActiveTab("history")}
              className={`px-4 py-2 rounded-lg text-xs font-bold transition-all ${
                activeTab === "history"
                  ? "bg-rose-500 text-white shadow-md"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              Login History Stream ({filteredHistory.length})
            </button>
          </div>

          {/* Search & Provider Filter */}
          <div className="flex items-center gap-3">
            <div className="relative flex-1 sm:w-64">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search email, name, IP..."
                className="w-full pl-9 pr-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-white placeholder:text-slate-500 focus:outline-none focus:border-rose-500/60"
              />
            </div>

            <div className="flex items-center gap-1.5 px-2.5 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs">
              <Filter className="w-3.5 h-3.5 text-slate-400" />
              <select
                value={providerFilter}
                onChange={(e) => setProviderFilter(e.target.value)}
                className="bg-transparent text-slate-200 text-xs font-medium focus:outline-none cursor-pointer"
              >
                <option value="all" className="bg-slate-900">All Providers</option>
                <option value="otp" className="bg-slate-900">Email + OTP</option>
                <option value="google" className="bg-slate-900">Google OAuth</option>
                <option value="admin_passcode" className="bg-slate-900">Admin Passcode</option>
                <option value="password" className="bg-slate-900">Password</option>
              </select>
            </div>
          </div>
        </div>

        {/* Data Table */}
        <div className="rounded-2xl border border-slate-800 bg-slate-950/90 overflow-hidden shadow-2xl">
          {activeTab === "users" ? (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-slate-800/80 bg-slate-900/60 text-slate-400 font-mono uppercase text-[10px] tracking-wider">
                    <th className="py-3.5 px-4 font-bold">User Identity</th>
                    <th className="py-3.5 px-4 font-bold">Email Address</th>
                    <th className="py-3.5 px-4 font-bold">Auth Provider</th>
                    <th className="py-3.5 px-4 font-bold">Role</th>
                    <th className="py-3.5 px-4 font-bold">Login Frequency</th>
                    <th className="py-3.5 px-4 font-bold">Last Login Date & Time</th>
                    <th className="py-3.5 px-4 font-bold">Registered Date</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {filteredUsers.length === 0 ? (
                    <tr>
                      <td colSpan={7} className="text-center py-10 text-slate-500 font-mono">
                        No user records matching search query "{searchQuery}".
                      </td>
                    </tr>
                  ) : (
                    filteredUsers.map((u) => (
                      <tr key={u.id} className="hover:bg-slate-900/40 transition-colors">
                        <td className="py-3.5 px-4">
                          <div className="flex items-center gap-2.5">
                            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-rose-500 to-indigo-600 flex items-center justify-center text-white font-bold text-xs shrink-0 shadow-md">
                              {u.name.slice(0, 2).toUpperCase()}
                            </div>
                            <div>
                              <div className="font-bold text-white">{u.name}</div>
                              <div className="text-[10px] font-mono text-slate-500">{u.id}</div>
                            </div>
                          </div>
                        </td>
                        <td className="py-3.5 px-4 font-mono font-medium text-slate-200">
                          {u.email}
                        </td>
                        <td className="py-3.5 px-4">
                          {getProviderBadge(u.auth_provider)}
                        </td>
                        <td className="py-3.5 px-4">
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase ${
                              u.role === "admin"
                                ? "bg-rose-500/20 text-rose-300 border border-rose-500/40"
                                : "bg-sky-500/20 text-sky-300 border border-sky-500/40"
                            }`}
                          >
                            {u.role}
                          </span>
                        </td>
                        <td className="py-3.5 px-4 font-mono text-slate-300">
                          <span className="px-2 py-0.5 rounded bg-slate-900 border border-slate-800">
                            {u.login_count} {u.login_count === 1 ? "login" : "logins"}
                          </span>
                        </td>
                        <td className="py-3.5 px-4 font-mono">
                          <div className="text-slate-200 font-medium">{formatDate(u.last_login_at)}</div>
                          <div className="text-[10px] text-slate-400">{getRelativeTime(u.last_login_at)}</div>
                        </td>
                        <td className="py-3.5 px-4 font-mono text-slate-400 text-[11px]">
                          {formatDate(u.created_at)}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-slate-800/80 bg-slate-900/60 text-slate-400 font-mono uppercase text-[10px] tracking-wider">
                    <th className="py-3.5 px-4 font-bold">Event ID</th>
                    <th className="py-3.5 px-4 font-bold">Username</th>
                    <th className="py-3.5 px-4 font-bold">Email Address</th>
                    <th className="py-3.5 px-4 font-bold">Method</th>
                    <th className="py-3.5 px-4 font-bold">Origin / Region</th>
                    <th className="py-3.5 px-4 font-bold">Timestamp</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {filteredHistory.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="text-center py-10 text-slate-500 font-mono">
                        No recorded login events matching current filter.
                      </td>
                    </tr>
                  ) : (
                    filteredHistory.map((ev) => (
                      <tr key={ev.id} className="hover:bg-slate-900/40 transition-colors">
                        <td className="py-3 px-4 font-mono text-[11px] text-slate-500">
                          {ev.id}
                        </td>
                        <td className="py-3 px-4 font-bold text-white">
                          {ev.username}
                        </td>
                        <td className="py-3 px-4 font-mono text-slate-200">
                          {ev.email}
                        </td>
                        <td className="py-3 px-4">
                          {getProviderBadge(ev.auth_method)}
                        </td>
                        <td className="py-3 px-4 text-slate-300 font-mono text-[11px]">
                          {ev.region} ({ev.ip_address})
                        </td>
                        <td className="py-3 px-4 font-mono">
                          <div className="text-slate-200 font-medium">{formatDate(ev.created_at)}</div>
                          <div className="text-[10px] text-slate-400">{getRelativeTime(ev.created_at)}</div>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default AdminDashboard;
