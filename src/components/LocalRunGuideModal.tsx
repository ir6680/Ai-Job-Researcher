import React, { useState } from 'react';
import { Terminal, Copy, CheckCircle, X, ExternalLink, Container } from 'lucide-react';

interface LocalRunGuideModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const LocalRunGuideModal: React.FC<LocalRunGuideModalProps> = ({ isOpen, onClose }) => {
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  if (!isOpen) return null;

  const handleCopy = (text: string, index: number) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const dockerCommand = `docker-compose up --build`;
  const pythonCommands = `python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload`;

  const testCommand = `pytest backend/tests -v`;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-xs p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-2xl w-full shadow-2xl space-y-5 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-lg bg-emerald-500/20 text-emerald-400">
              <Terminal className="w-5 h-5" />
            </span>
            <div>
              <h3 className="text-base font-bold text-white">How to Run Phase 1 Locally</h3>
              <p className="text-xs text-slate-400">Complete instructions for Docker & local Python 3.12+</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white p-1 rounded-lg transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Option 1: Docker Compose */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider">
              Option A: Docker Compose (PostgreSQL 16 + FastAPI)
            </span>
            <button
              onClick={() => handleCopy(dockerCommand, 1)}
              className="text-[11px] text-slate-400 hover:text-white flex items-center gap-1 font-mono"
            >
              {copiedIndex === 1 ? <CheckCircle className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copiedIndex === 1 ? 'Copied' : 'Copy Command'}</span>
            </button>
          </div>
          <p className="text-xs text-slate-300">
            Spins up PostgreSQL 16 container, applies schema DDL, seeds starter Lahore jobs, and launches FastAPI with hot-reloading:
          </p>
          <pre className="p-3 bg-slate-950 rounded-xl font-mono text-xs text-emerald-300 border border-slate-800">
            {dockerCommand}
          </pre>
        </div>

        {/* Option 2: Local Python */}
        <div className="space-y-2 pt-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-sky-400 uppercase tracking-wider">
              Option B: Native Python 3.12 Setup
            </span>
            <button
              onClick={() => handleCopy(pythonCommands, 2)}
              className="text-[11px] text-slate-400 hover:text-white flex items-center gap-1 font-mono"
            >
              {copiedIndex === 2 ? <CheckCircle className="w-3.5 h-3.5 text-sky-400" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copiedIndex === 2 ? 'Copied' : 'Copy Script'}</span>
            </button>
          </div>
          <p className="text-xs text-slate-300">
            Create a virtual environment, install requirements, and run with Uvicorn:
          </p>
          <pre className="p-3 bg-slate-950 rounded-xl font-mono text-xs text-slate-300 border border-slate-800 leading-relaxed overflow-x-auto">
            {pythonCommands}
          </pre>
        </div>

        {/* Test execution */}
        <div className="space-y-2 pt-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-amber-400 uppercase tracking-wider">
              Run Automated Tests
            </span>
            <button
              onClick={() => handleCopy(testCommand, 3)}
              className="text-[11px] text-slate-400 hover:text-white flex items-center gap-1 font-mono"
            >
              {copiedIndex === 3 ? <CheckCircle className="w-3.5 h-3.5 text-amber-400" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copiedIndex === 3 ? 'Copied' : 'Copy'}</span>
            </button>
          </div>
          <p className="text-xs text-slate-300">
            Validates anti-hallucination extraction, phone regex, and job schemas:
          </p>
          <pre className="p-3 bg-slate-950 rounded-xl font-mono text-xs text-amber-300 border border-slate-800">
            {testCommand}
          </pre>
        </div>

        {/* URLs info */}
        <div className="p-3.5 bg-slate-950/80 rounded-xl border border-slate-800 text-xs space-y-1.5">
          <div className="text-white font-semibold">Active URLs once started:</div>
          <div className="text-slate-400 font-mono text-[11px] space-y-1">
            <div>• Interactive Docs: <span className="text-emerald-400">http://localhost:8000/docs</span></div>
            <div>• Alternative ReDoc: <span className="text-emerald-400">http://localhost:8000/redoc</span></div>
            <div>• Database: <span className="text-sky-400">localhost:5432 (job_agent_db)</span></div>
          </div>
        </div>

        <div className="flex justify-end pt-2">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-bold rounded-xl transition"
          >
            Close Guide
          </button>
        </div>
      </div>
    </div>
  );
};
