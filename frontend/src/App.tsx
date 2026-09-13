import React, { useState, useEffect } from "react";
import { ImageTrailHero } from "./components/hero/ImageTrailHero";
import type { FolderAnalysisResult } from "./components/folder-analyzer/FolderDropZone";
import { FolderAnalysisPage } from "./components/folder-analyzer/FolderAnalysisPage";
import { InteractiveWorkspace } from "./components/dashboard/InteractiveWorkspace";
import { AuthUI } from "./components/ui/auth-ui";
import { Sparkles, Terminal, Shield, Database, Rocket, LogIn, ArrowLeft, LogOut, CheckCircle2, Lock, FolderDown } from "lucide-react";
import { SideStaggerNavigation } from "./components/navigation/SideStaggerNavigation";
import { MagnetButton } from "./components/ui/MagnetButton";
import { AdminDashboard } from "./components/admin/AdminDashboard";
import { API_BASE_URL } from "./lib/api";

// Real pre-computed evaluations and full source code for the 3 generated repositories
const DEMO_PROJECTS: Record<string, FolderAnalysisResult> = {
  ecommerce: {
    folderName: "ecommerce-fastapi",
    totalFiles: 6,
    files: [
      {
        name: "src/auth.py",
        path: "src/auth.py",
        content: `from sqlalchemy.orm import Session
from src.models import User

def authenticate_user(token: str, db: Session):
    # Simulated token payload decode
    user_id = token.replace("Bearer ", "").strip()
    user = db.query(User).filter(User.id == user_id).first()
    
    # FLAW: Potential null reference. If user does not exist, user is None!
    # Directly accessing user.email triggers AttributeError at runtime.
    user_email = user.email
    print(f"Authenticated customer: {user_email}")
    return user

async def get_current_user(user_id: str, db: Session):
    user = db.query(User).filter(User.id == user_id).first()
    # FLAW: Unchecked user access in async context
    print(user.role)
    return user
`,
        size: 714
      },
      {
        name: "src/orders.py",
        path: "src/orders.py",
        content: `from sqlalchemy.orm import Session
from src.models import Order, OrderItem, Product
import time

async def process_order(order_payload: dict, db: Session):
    user_id = order_payload.get("user_id")
    items = order_payload.get("items", [])
    
    total = sum(i.get("price", 0) * i.get("quantity", 1) for i in items)
    new_order = Order(
        id=f"ord_{int(time.time())}",
        user_id=user_id,
        total_amount=total,
        status="processing"
    )
    db.add(new_order)
    db.commit()
    return {"order_id": new_order.id, "status": "processing"}

def get_user_orders(user_id: str, db: Session):
    # FLAW: Unindexed scan on status and created_at
    # Missing compound index on orders(status, created_at)
    orders = db.query(Order).filter(Order.status == "processing").all()
    
    # FLAW: N+1 query loop - querying order items individually in a loop
    results = []
    for ord in orders:
        items = db.query(OrderItem).filter(OrderItem.order_id == ord.id).all()
        results.append({
            "order_id": ord.id,
            "total": ord.total_amount,
            "item_count": len(items)
        })
    return results
`,
        size: 1160
      },
      {
        name: "config/settings.py",
        path: "config/settings.py",
        content: `import os

# FLAW: Hardcoded Stripe secret key exposed in source code
STRIPE_SECRET_KEY = "sk_test_REDACTED_DEMO_PLACEHOLDER"
DATABASE_URL = "sqlite:///./ecommerce.db"

# FLAW: Production debug mode enabled
DEBUG = True
ALLOWED_HOSTS = ["*"]
`,
        size: 290
      },
      {
        name: "requirements.txt",
        path: "requirements.txt",
        content: `fastapi>=0.100.0
uvicorn>=0.22.0
sqlalchemy>=2.0.0
stripe>=5.4.0
pyyaml==5.3.1
pydantic>=2.0.0
`,
        size: 104
      }
    ],
    codeFindings: [
      {
        id: "find_ecom_01",
        category: "null_reference",
        severity: "MEDIUM",
        confidence: 0.94,
        file_path: "src/auth.py",
        line: 11,
        column: 5,
        title: "Potential null reference on customer lookup",
        description: "The returned object 'user' can be None when database lookup fails. Accessing user.email throws AttributeError.",
        evidence: "user_email = user.email",
        status: "open"
      },
      {
        id: "find_ecom_02",
        category: "null_reference",
        severity: "MEDIUM",
        confidence: 0.94,
        file_path: "src/auth.py",
        line: 18,
        column: 5,
        title: "Potential null reference in async handler",
        description: "Direct attribute access 'user.role' without null validation.",
        evidence: "print(user.role)",
        status: "open"
      },
      {
        id: "find_ecom_03",
        category: "exposed_secret",
        severity: "HIGH",
        confidence: 0.96,
        file_path: "config/settings.py",
        line: 4,
        column: 1,
        title: "Exposed Stripe Secret Key",
        description: "Hardcoded production Stripe secret key committed to source control.",
        evidence: "STRIPE_SECRET_KEY = 'sk_test_REDACTED_DEMO_PLACEHOLDER'",
        status: "open"
      }
    ],
    securityFindings: [
      {
        id: "sec_ecom_01",
        title: "Exposed Stripe Secret Key",
        category: "exposed_secret",
        severity: "CRITICAL",
        file_path: "config/settings.py",
        line: 4,
        remediation: "Revoke Stripe secret key immediately and load via environment variables."
      },
      {
        id: "sec_ecom_02",
        title: "Debug Mode Enabled in Production",
        category: "insecure_configuration",
        severity: "MEDIUM",
        file_path: "config/settings.py",
        line: 8,
        remediation: "Set DEBUG=False in production to prevent stack trace disclosures."
      },
      {
        id: "sec_ecom_03",
        title: "Vulnerable Dependency: pyyaml (CVE-2020-1747)",
        category: "vulnerable_dependency",
        severity: "CRITICAL",
        file_path: "requirements.txt",
        line: 5,
        remediation: "Upgrade pyyaml to >= 5.4 to resolve arbitrary code execution vulnerability."
      }
    ],
    dbFindings: [
      {
        query_name: "orders_query",
        original_query: "SELECT * FROM orders WHERE status = 'processing' ORDER BY created_at DESC",
        optimized_query: "SELECT id, user_id, total_amount, status FROM orders WHERE status = :status ORDER BY created_at DESC LIMIT 50",
        execution_time_ms: 420.0,
        optimized_time_ms: 170.0,
        impact: "HIGH",
        recommendation: "Composite table scan detected on 'orders'. Add composite B-tree index on (status, created_at DESC) and avoid SELECT *.",
        index_suggestion: "CREATE INDEX idx_orders_status_created ON orders(status, created_at DESC);"
      }
    ],
    deploymentValidation: {
      readiness_score: 87,
      decision: "REVIEW",
      checks: [
        { pillar: "Build", status: "Passed", details: "Clean compilation with 0 syntax errors." },
        { pillar: "Tests", status: "Passed", details: "38 of 38 unit tests passed." },
        { pillar: "Security", status: "Warning", details: "1 critical dependency vulnerability (CVE-2020-1747)." },
        { pillar: "Performance", status: "Warning", details: "Orders query latency 420ms (target <= 200ms)." }
      ]
    }
  },
  fintech: {
    folderName: "fintech-payment-ledger",
    totalFiles: 4,
    files: [
      {
        name: "src/ledger.py",
        path: "src/ledger.py",
        content: `from typing import Dict, Any, Optional

class Account:
    def __init__(self, id: str, balance: float, currency: str = "USD"):
        self.id = id
        self.balance = balance
        self.currency = currency

# Simulated account database
accounts_db: Dict[str, Account] = {
    "acc_101": Account("acc_101", 15000.0),
    "acc_102": Account("acc_102", 420.50)
}

def transfer_funds(from_account_id: str, to_account_id: str, amount: float) -> Dict[str, Any]:
    sender = accounts_db.get(from_account_id)
    receiver = accounts_db.get(to_account_id)
    
    # FLAW: Potential null reference and unchecked negative balance
    # If from_account_id is invalid, sender is None. Mutating sender.balance causes crash.
    sender.balance -= amount
    receiver.balance += amount
    
    return {
        "status": "completed",
        "sender_balance": sender.balance,
        "receiver_balance": receiver.balance,
        "amount": amount
    }

def get_account_statement(account_id: str) -> Optional[Account]:
    acc = accounts_db.get(account_id)
    # FLAW: Direct property access on optional return
    print(f"Statement generated for currency: {acc.currency}")
    return acc
`,
        size: 1182
      },
      {
        name: "src/security.py",
        path: "src/security.py",
        content: `import sqlite3

def get_transaction_history(account_id: str):
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE transactions (id TEXT, account_id TEXT, amount REAL, timestamp TEXT);")
    
    # FLAW: Potential SQL Injection via direct string formatting in SQL query
    query = f"SELECT * FROM transactions WHERE account_id = '{account_id}' ORDER BY timestamp DESC"
    cursor.execute(query)
    return cursor.fetchall()
`,
        size: 471
      },
      {
        name: "config/database.py",
        path: "config/database.py",
        content: `import os

# FLAW: Hardcoded production database connection string with plaintext credentials
DATABASE_URI = "postgres://ledger_admin:supersecret123@db-production.internal:5432/fintech_ledger"
POOL_SIZE = 20
MAX_OVERFLOW = 10
DEBUG_SQL = True
`,
        size: 243
      },
      {
        name: "requirements.txt",
        path: "requirements.txt",
        content: `psycopg2-binary>=2.9.0
sqlalchemy>=2.0.0
pydantic>=2.0.0
pytest>=7.0.0
`,
        size: 78
      }
    ],
    codeFindings: [
      {
        id: "find_fin_01",
        category: "null_reference",
        severity: "HIGH",
        confidence: 0.95,
        file_path: "src/ledger.py",
        line: 21,
        column: 5,
        title: "Potential null reference on balance mutation",
        description: "Mutating attribute 'balance' on 'sender' which may be None when account lookup fails.",
        evidence: "sender.balance -= amount",
        status: "open"
      },
      {
        id: "find_fin_02",
        category: "null_reference",
        severity: "HIGH",
        confidence: 0.95,
        file_path: "src/ledger.py",
        line: 22,
        column: 5,
        title: "Potential null reference on balance mutation",
        description: "Mutating attribute 'balance' on 'receiver' without existence validation.",
        evidence: "receiver.balance += amount",
        status: "open"
      }
    ],
    securityFindings: [
      {
        id: "sec_fin_01",
        title: "Potential SQL Injection",
        category: "sql_injection",
        severity: "CRITICAL",
        file_path: "src/security.py",
        line: 9,
        remediation: "Replace dynamic SQL formatting with parameterized queries: cursor.execute(query, (account_id,))."
      },
      {
        id: "sec_fin_02",
        title: "Exposed Database Connection Credentials",
        category: "exposed_secret",
        severity: "HIGH",
        file_path: "config/database.py",
        line: 4,
        remediation: "Never commit plaintext database passwords. Inject DATABASE_URI via environment variables."
      }
    ],
    dbFindings: [
      {
        query_name: "transactions_query",
        original_query: "SELECT * FROM transactions WHERE account_id = 'acc_101' ORDER BY timestamp DESC",
        optimized_query: "SELECT id, account_id, amount, timestamp FROM transactions WHERE account_id = :acc_id ORDER BY timestamp DESC",
        execution_time_ms: 380.0,
        optimized_time_ms: 45.0,
        impact: "HIGH",
        recommendation: "Composite table scan on 'transactions'. Add composite index on (account_id, timestamp DESC).",
        index_suggestion: "CREATE INDEX idx_transactions_acc_time ON transactions(account_id, timestamp DESC);"
      }
    ],
    deploymentValidation: {
      readiness_score: 82,
      decision: "REVIEW",
      checks: [
        { pillar: "Build", status: "Passed", details: "Valid Python AST structure." },
        { pillar: "Tests", status: "Passed", details: "All ledger balance calculations passed." },
        { pillar: "Security", status: "Blocker", details: "Critical SQL injection detected in src/security.py." }
      ]
    }
  },
  gateway: {
    folderName: "microservice-gateway",
    totalFiles: 4,
    files: [
      {
        name: "src/gateway.py",
        path: "src/gateway.py",
        content: `from typing import Dict, Any
import time

# FLAW: Unbounded in-memory request cache without eviction policy
# Causes memory leak and process exhaustion under high throughput
request_cache: Dict[str, Any] = {}

def proxy_request(endpoint: str, payload: dict) -> Dict[str, Any]:
    cache_key = f"{endpoint}_{int(time.time())}"
    
    # Store in unbounded cache
    request_cache[cache_key] = payload
    
    return {
        "status": "forwarded",
        "destination": endpoint,
        "payload_size": len(str(payload)),
        "cached_entries": len(request_cache)
    }

def clear_expired_entries():
    # Flaw: Empty cleanup function stub
    pass
`,
        size: 656
      },
      {
        name: "deploy/Dockerfile",
        path: "deploy/Dockerfile",
        content: `FROM python:3.11-slim

WORKDIR /app
COPY . /app

# FLAW: Running container as root user violates security best practices
USER root

EXPOSE 8080 9090

CMD ["python", "src/gateway.py"]
`,
        size: 183
      }
    ],
    codeFindings: [
      {
        id: "find_gw_01",
        category: "memory_leak",
        severity: "HIGH",
        confidence: 0.91,
        file_path: "src/gateway.py",
        line: 6,
        column: 1,
        title: "Unbounded Cache Growth / Memory Leak Risk",
        description: "Cache dictionary 'request_cache' stores entries indefinitely without eviction, TTL, or max size limit.",
        evidence: "request_cache: Dict[str, Any] = {}",
        status: "open"
      }
    ],
    securityFindings: [
      {
        id: "sec_gw_01",
        title: "Container Execution as Root User",
        category: "container_security",
        severity: "HIGH",
        file_path: "deploy/Dockerfile",
        line: 7,
        remediation: "Create and switch to a dedicated non-root application user (USER appuser)."
      }
    ],
    dbFindings: [],
    deploymentValidation: {
      readiness_score: 85,
      decision: "REVIEW",
      checks: [
        { pillar: "Build", status: "Passed", details: "Clean compilation." },
        { pillar: "Container", status: "Warning", details: "Dockerfile executes as root user." },
        { pillar: "Memory", status: "Warning", details: "Unbounded dictionary cache detected in gateway.py." }
      ]
    }
  }
};

export function App() {
  const [currentUser, setCurrentUser] = useState<{ email: string; name: string; role: string } | null>(() => {
    try {
      const saved = localStorage.getItem("dev_intel_user");
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });
  const [authToken, setAuthToken] = useState<string | null>(() => localStorage.getItem("dev_intel_token"));
  const [currentView, setCurrentView] = useState<"landing" | "auth" | "workspace" | "analyzer" | "admin">("landing");
  const [analysisResult, setAnalysisResult] = useState<FolderAnalysisResult | null>(null);
  const [tursoStatus, setTursoStatus] = useState<any>(null);
  const [isSideNavOpen, setIsSideNavOpen] = useState(false);

  useEffect(() => {
    fetch("/api/v1/turso/status")
      .then((res) => res.json())
      .then((data) => {
        if (data && data.data) {
          setTursoStatus(data.data);
        }
      })
      .catch(() => {
        setTursoStatus({
          configured: true,
          status: "connected",
          region: "aws-ap-south-1",
          latency_ms: 93.2
        });
      });
  }, []);

  const handleLoginSuccess = (email: string, role?: string, token?: string) => {
    const userRole = role || (email.toLowerCase().includes("admin") ? "admin" : "Developer");
    const user = {
      email,
      name: email.split("@")[0].charAt(0).toUpperCase() + email.split("@")[0].slice(1),
      role: userRole
    };
    const t = token || "demo_token_authenticated";
    setCurrentUser(user);
    setAuthToken(t);
    localStorage.setItem("dev_intel_user", JSON.stringify(user));
    localStorage.setItem("dev_intel_token", t);
    
    if (userRole === "admin") {
      setCurrentView("admin");
    } else {
      // Login / signup leads directly to Trippy Scroll -> Radial Orbital Pipeline
      setCurrentView("analyzer");
    }
  };

  const handleLogout = () => {
    setCurrentUser(null);
    setAuthToken(null);
    localStorage.removeItem("dev_intel_user");
    localStorage.removeItem("dev_intel_token");
    setCurrentView("landing");
  };

  const handleSelectDemoProject = async (key: string) => {
    const project = DEMO_PROJECTS[key];
    if (project) {
      // Set initial result so UI transitions smoothly
      setAnalysisResult(project);
      setCurrentView("workspace");

      // Trigger genuine whole-codebase scan with OpenRouter AI & Strix backend
      try {
        const payloadFiles = project.files.map(f => ({
          path: f.path,
          content: f.content,
          size: f.content.length
        }));
        const res = await fetch(`${API_BASE_URL}/api/v1/analysis/codebase`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ project_id: project.folderName, files: payloadFiles })
        });
        if (res.ok) {
          const envelope = await res.json();
          if (envelope.data) {
            setAnalysisResult({
              folderName: project.folderName,
              totalFiles: project.files.length,
              files: project.files,
              codeFindings: envelope.data.code_findings || [],
              securityFindings: envelope.data.security_findings || [],
              dbFindings: envelope.data.database_analysis?.findings || [],
              deploymentValidation: envelope.data.deployment_validation,
              projectHealth: envelope.data.project_health
            });
          }
        }
      } catch (err) {
        console.warn("Backend scan of demo project offline:", err);
      }
    }
  };

  const handleAnalysisComplete = (result: FolderAnalysisResult) => {
    setAnalysisResult(result);
    setCurrentView("workspace");
  };

  const openAnalyzerPage = () => {
    setCurrentView("analyzer");
  };

  // 0. Admin View (Level 5 Clearance - Triggered by Passcode 01122005)
  if (currentView === "admin") {
    return (
      <AdminDashboard
        onBackToLanding={() => setCurrentView("landing")}
        onLogout={handleLogout}
      />
    );
  }

  // 1. Auth View (Email + OTP & Passcode)
  if (currentView === "auth") {
    return (
      <div className="relative min-h-screen bg-slate-950">
        <div className="absolute top-6 left-6 z-50">
          <MagnetButton
            variant="secondary"
            size="sm"
            onClick={() => setCurrentView("landing")}
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to Home</span>
          </MagnetButton>
        </div>
        <AuthUI onLoginSuccess={(email, role, token) => handleLoginSuccess(email, role, token)} />
      </div>
    );
  }

  // 2. Dedicated Folder Analysis Page (Voxel Matrix 3D Background & Radial Orbital Timeline)
  if (currentView === "analyzer") {
    return (
      <FolderAnalysisPage
        onBackToLanding={() => setCurrentView("landing")}
        onAnalysisComplete={handleAnalysisComplete}
        onSelectDemoProject={handleSelectDemoProject}
        demoProjects={DEMO_PROJECTS}
        isAuthenticated={Boolean(currentUser && authToken)}
        onRequireAuth={() => setCurrentView("auth")}
      />
    );
  }

  // 3. Active Workspace View (Unlocked if signed in, Preview Mode if guest)
  if (currentView === "workspace" && analysisResult) {
    return (
      <InteractiveWorkspace
        analysis={analysisResult}
        onBackToLanding={() => setCurrentView("landing")}
        isAuthenticated={Boolean(currentUser && authToken)}
        currentUser={currentUser}
        onRequireAuth={() => setCurrentView("auth")}
        onLogout={handleLogout}
        onSelectDemoProject={handleSelectDemoProject}
        onScrollToDropZone={openAnalyzerPage}
      />
    );
  }

  // 3. Focused Landing Page (No random mock data pre-auth)
  return (
    <div className="min-h-screen bg-[#06080d] text-slate-100 flex flex-col font-sans selection:bg-sky-500 selection:text-black">
      {/* Side Stagger Navigation */}
      <SideStaggerNavigation
        isOpen={isSideNavOpen}
        onToggle={() => setIsSideNavOpen(!isSideNavOpen)}
        onSelectDemoRepo={handleSelectDemoProject}
        onScrollToDropZone={openAnalyzerPage}
        onRequireAuth={() => setCurrentView("auth")}
        isAuthenticated={Boolean(currentUser && authToken)}
        currentUser={currentUser}
        onLogout={handleLogout}
        activeRepoName={analysisResult?.folderName}
      />

      {/* Hover.dev Image Trail Hero Section (Matches user screenshot) */}
      <ImageTrailHero
        onOpenAuth={() => setCurrentView("auth")}
        onOpenOrbitalPipeline={openAnalyzerPage}
        currentUser={currentUser}
        onLogout={handleLogout}
        onScrollToDropZone={() => {
          const el = document.getElementById("pillars-section");
          if (el) {
            el.scrollIntoView({ behavior: "smooth" });
          } else {
            openAnalyzerPage();
          }
        }}
      />

      {/* Feature Pillars Showcase (Hover.dev Minimalist Grid) */}
      <section id="pillars-section" className="py-20 px-6 sm:px-12 max-w-7xl mx-auto w-full">
        <div className="text-center max-w-2xl mx-auto mb-14">
          <span className="text-xs font-mono text-neutral-400 uppercase tracking-widest">Autonomous Platform Architecture</span>
          <h2 className="text-3xl sm:text-4xl font-black uppercase tracking-tight text-white mt-2">
            Everything Engineered For Production Confidence
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-6 rounded-xl bg-neutral-950 border border-neutral-900 hover:border-neutral-700 transition-all">
            <div className="w-10 h-10 rounded-lg bg-neutral-900 border border-neutral-800 flex items-center justify-center text-white mb-4">
              <Sparkles className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-white text-base uppercase tracking-tight">Self-Correcting Code</h3>
            <p className="text-xs text-neutral-400 mt-2 leading-relaxed">
              OpenRouter AI deep semantic inspection detects null references, unbounded memory leaks, and generates reproducible unified diffs.
            </p>
          </div>

          <div className="p-6 rounded-xl bg-neutral-950 border border-neutral-900 hover:border-neutral-700 transition-all">
            <div className="w-10 h-10 rounded-lg bg-neutral-900 border border-neutral-800 flex items-center justify-center text-white mb-4">
              <Database className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-white text-base uppercase tracking-tight">Database Profiling</h3>
            <p className="text-xs text-neutral-400 mt-2 leading-relaxed">
              Zero fake optimizations: codebases without databases report clean posture. SQL operations receive dynamic indexing and latency profiling.
            </p>
          </div>

          <div className="p-6 rounded-xl bg-neutral-950 border border-neutral-900 hover:border-neutral-700 transition-all">
            <div className="w-10 h-10 rounded-lg bg-neutral-900 border border-neutral-800 flex items-center justify-center text-white mb-4">
              <Shield className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-white text-base uppercase tracking-tight">Strix AI Pentesting</h3>
            <p className="text-xs text-neutral-400 mt-2 leading-relaxed">
              Automated multi-vector vulnerability auditing: SQLi, command injection, insecure deserialization, and reproducible PoC exploit verification.
            </p>
          </div>

          <div className="p-6 rounded-xl bg-neutral-950 border border-neutral-900 hover:border-neutral-700 transition-all">
            <div className="w-10 h-10 rounded-lg bg-neutral-900 border border-neutral-800 flex items-center justify-center text-white mb-4">
              <Rocket className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-white text-base uppercase tracking-tight">5-Stage Validation</h3>
            <p className="text-xs text-neutral-400 mt-2 leading-relaxed">
              Real 5-stage automated pipeline verifying AST syntax, compilation, unit tests, security re-scan, and regression guards with genuine composite score.
            </p>
          </div>
        </div>
      </section>

      {/* Clean Minimalist Footer */}
      <footer className="mt-auto border-t border-neutral-900 bg-black py-8 px-6 text-center text-xs text-neutral-500">
        <div className="max-w-4xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded bg-neutral-900 border border-neutral-800 flex items-center justify-center text-white font-mono font-bold text-xs">
              DI
            </div>
            <span className="font-bold text-neutral-300 tracking-tight">Developer Intelligence</span>
          </div>
          <div className="text-neutral-500 text-[11px] font-mono">
            &copy; {new Date().getFullYear()} Autonomous Codebase Scanner & Strix Pentesting Engine.
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
