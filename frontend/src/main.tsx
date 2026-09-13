import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./index.css";

class RootErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { message: string | null }
> {
  state = { message: null as string | null };

  static getDerivedStateFromError(error: Error) {
    return { message: error.message || "The workspace failed to render." };
  }

  render() {
    if (this.state.message) {
      return (
        <div className="min-h-screen bg-[#dde3ec] text-[#0a0f1d] p-10 font-sans">
          <h1 className="text-2xl font-black mb-2">Developer Intelligence</h1>
          <p className="text-slate-600 mb-4">The interface hit an error while opening.</p>
          <p className="text-sm font-mono bg-white/80 border border-slate-200 rounded-lg p-3">
            {this.state.message}
          </p>
          <button
            type="button"
            className="mt-6 px-4 py-2 rounded-lg bg-slate-900 text-white text-sm font-semibold"
            onClick={() => window.location.reload()}
          >
            Reload
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

const root = document.getElementById("root");
if (root) {
  ReactDOM.createRoot(root).render(
    <React.StrictMode>
      <RootErrorBoundary>
        <App />
      </RootErrorBoundary>
    </React.StrictMode>
  );
}
