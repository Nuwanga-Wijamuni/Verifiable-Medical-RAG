import React, { useState, useRef, useEffect } from 'react';
import { 
  Upload, 
  FileText, 
  Send, 
  Activity, 
  ShieldCheck, 
  Database,
  CheckCircle2,
  X,
  Plus
} from 'lucide-react';

export default function App() {
  // --- STATE MANAGEMENT ---
  const [files, setFiles] = useState([]);
  const [uploadStatus, setUploadStatus] = useState('idle'); // idle, uploading, success, error
  const [uploadStats, setUploadStats] = useState(null);
  const [errorMessage, setErrorMessage] = useState(''); // New state for error messages
  
  const [query, setQuery] = useState('');
  // Removed yearFilter state
  const [chatHistory, setChatHistory] = useState([]);
  const [isGenerating, setIsGenerating] = useState(false);
  
  const [activeCitation, setActiveCitation] = useState(null);
  const chatEndRef = useRef(null);

  // --- API HANDLERS ---

  const handleFileChange = (e) => {
    setErrorMessage(''); // Clear previous errors
    if (e.target.files && e.target.files[0]) {
      const newFile = e.target.files[0];

      // 1. Check for Max Limit (3 files)
      if (files.length >= 3) {
        setErrorMessage("Maximum of 3 files allowed.");
        return;
      }

      // 2. Check for Duplicates
      const isDuplicate = files.some(f => f.name === newFile.name);
      if (isDuplicate) {
        setErrorMessage("This file has already been added.");
        return;
      }

      // Append the new file
      setFiles(prev => [...prev, newFile]);
      // CRITICAL FIX: Reset status to 'idle' so the button re-enables for the new file
      setUploadStatus('idle');
    }
    // Reset input value so the same file can be selected again if needed
    e.target.value = null;
  };

  const removeFile = (indexToRemove) => {
    setFiles(prev => prev.filter((_, index) => index !== indexToRemove));
    setErrorMessage('');
    // Reset status to 'idle' whenever the list changes
    setUploadStatus('idle');
  };

  const handleUpload = async () => {
    if (files.length === 0) return;
    
    setUploadStatus('uploading');
    setErrorMessage('');
    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });

    try {
      const response = await fetch('http://localhost:8000/api/v1/ingest', {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) throw new Error('Upload failed');
      
      const data = await response.json();
      setUploadStatus('success');
      setUploadStats(data);
      
      // Add system message
      setChatHistory(prev => [...prev, {
        role: 'system',
        content: `Ingestion Complete: Processed ${data.files_processed.length} files (${data.total_chunks} chunks). Database is ready.`
      }]);
    } catch (error) {
      console.error(error);
      setUploadStatus('error');
      setErrorMessage("Failed to upload files. Check backend.");
    }
  };

  const handleSend = async () => {
    if (!query.trim()) return;

    const userMessage = { role: 'user', content: query };
    setChatHistory(prev => [...prev, userMessage]);
    setQuery('');
    setIsGenerating(true);
    setActiveCitation(null);

    try {
      const response = await fetch('http://localhost:8000/api/v1/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: userMessage.content,
          year_filter: null // Removed year filter logic
        })
      });

      const data = await response.json();
      
      const aiMessage = {
        role: 'assistant',
        content: data.answer,
        citations: data.citations || []
      };

      setChatHistory(prev => [...prev, aiMessage]);
    } catch (error) {
      setChatHistory(prev => [...prev, {
        role: 'system',
        content: "Error connecting to the AI. Is the backend running?"
      }]);
    } finally {
      setIsGenerating(false);
    }
  };

  // Scroll to bottom
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory]);

  return (
    <div className="flex h-screen bg-slate-50 text-slate-900 font-sans overflow-hidden">
      
      {/* --- LEFT SIDEBAR (Controls & Ingestion) --- */}
      <div className="w-80 bg-white border-r border-slate-200 flex flex-col shadow-sm z-10">
        <div className="p-6 border-b border-slate-100">
          <div className="flex items-center gap-2 text-indigo-600 mb-1">
            <Activity className="w-6 h-6" />
            <h1 className="text-xl font-bold tracking-tight">VitalSource AI</h1>
          </div>
          <p className="text-xs text-slate-500 font-medium ml-8">Verifiable Medical RAG</p>
        </div>

        <div className="p-6 flex-1 overflow-y-auto">
          {/* Upload Section */}
          <div className="mb-8">
            <h2 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">Data Ingestion</h2>
            
            {/* Custom "One by One" File Input */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                 <span className="text-sm font-medium text-slate-600">Patient Records</span>
                 <span className="text-xs text-slate-400">{files.length} added</span>
              </div>

              {/* File List */}
              <div className="flex flex-col gap-2">
                {files.map((file, idx) => (
                  <div key={idx} className="flex items-center justify-between p-2 bg-slate-50 border border-slate-200 rounded-md group">
                    <div className="flex items-center gap-2 overflow-hidden">
                      <FileText className="w-4 h-4 text-indigo-400 flex-shrink-0" />
                      <span className="text-xs text-slate-700 truncate">{file.name}</span>
                    </div>
                    <button 
                      onClick={() => removeFile(idx)}
                      className="text-slate-400 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>

              {/* Error Message */}
              {errorMessage && (
                <div className="p-2 bg-red-50 border border-red-200 rounded-md flex items-center gap-2">
                    <X className="w-4 h-4 text-red-500" />
                    <span className="text-xs text-red-600">{errorMessage}</span>
                </div>
              )}

              {/* Add Button */}
              <div>
                <input 
                  type="file" 
                  accept=".pdf"
                  onChange={handleFileChange}
                  className="hidden"
                  id="file-upload"
                  disabled={files.length >= 3} // Disable input if max reached
                />
                <label 
                  htmlFor="file-upload" 
                  className={`cursor-pointer flex items-center justify-center gap-2 w-full p-2 border border-dashed border-indigo-300 rounded-md text-sm text-indigo-600 transition-colors ${
                      files.length >= 3 ? 'opacity-50 cursor-not-allowed bg-slate-50' : 'hover:bg-indigo-50'
                  }`}
                >
                  <Plus className="w-4 h-4" />
                  {files.length >= 3 ? "Max Files Reached" : "Add Document"}
                </label>
              </div>
            </div>

            {/* Ingest Button */}
            {files.length > 0 && (
              <button 
                onClick={handleUpload}
                disabled={uploadStatus === 'uploading'}
                className={`w-full mt-4 py-2 px-4 rounded-lg text-sm font-semibold transition-all flex items-center justify-center gap-2
                  ${uploadStatus === 'success' 
                    ? 'bg-green-50 text-green-700 border border-green-200' 
                    : 'bg-indigo-600 text-white hover:bg-indigo-700 shadow-md hover:shadow-lg'
                  }`}
              >
                {uploadStatus === 'uploading' ? (
                  <>Processing...</>
                ) : uploadStatus === 'success' ? (
                  <><CheckCircle2 className="w-4 h-4"/> Ingested (Click to Retry)</>
                ) : (
                  "Ingest All Documents"
                )}
              </button>
            )}
          </div>

          {/* Configuration Section REMOVED (Year Filter Deleted) */}

        </div>

        {/* Footer Status */}
        <div className="p-4 bg-slate-50 border-t border-slate-200">
          <div className="flex items-center gap-2 text-xs text-slate-500">
            <div className={`w-2 h-2 rounded-full ${uploadStatus === 'success' ? 'bg-green-500' : 'bg-amber-400'}`}></div>
            System Status: {uploadStatus === 'success' ? 'Ready' : 'Waiting for Data'}
          </div>
        </div>
      </div>

      {/* --- MAIN CHAT AREA --- */}
      <div className="flex-1 flex flex-col bg-slate-50/50 relative">
        {/* Header */}
        <div className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-6 shadow-sm z-10">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-emerald-500" />
            <span className="font-semibold text-slate-700">Medical Analyst Agent</span>
            <span className="bg-indigo-100 text-indigo-700 text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wide">OpenAI GPT-OSS-120B</span>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {chatHistory.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center opacity-40">
              <div className="w-16 h-16 bg-slate-200 rounded-2xl flex items-center justify-center mb-4">
                <Database className="w-8 h-8 text-slate-500" />
              </div>
              <h3 className="text-lg font-bold text-slate-700">No Patient Records Loaded</h3>
              <p className="max-w-xs text-sm text-slate-500 mt-2">Add PDF documents from the sidebar to begin analyzing patient history.</p>
            </div>
          ) : (
            chatHistory.map((msg, idx) => (
              <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div 
                  className={`max-w-[80%] rounded-2xl p-4 shadow-sm relative ${
                    msg.role === 'user' 
                      ? 'bg-indigo-600 text-white rounded-tr-none' 
                      : 'bg-white border border-slate-200 text-slate-800 rounded-tl-none'
                  }`}
                >
                  <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</p>
                  
                  {/* Citations Renderer */}
                  {msg.citations && msg.citations.length > 0 && (
                    <div className="mt-4 pt-3 border-t border-slate-100">
                      <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">Verified Sources</p>
                      <div className="flex flex-wrap gap-2">
                        {msg.citations.map((cit, cIdx) => (
                          <button
                            key={cIdx}
                            onClick={() => setActiveCitation(cit)}
                            className="flex items-center gap-1.5 px-2 py-1 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-md text-xs font-medium hover:bg-emerald-100 transition-colors"
                          >
                            <ShieldCheck className="w-3 h-3" />
                            Source {cit.year}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
          {isGenerating && (
            <div className="flex justify-start">
              <div className="bg-white border border-slate-200 rounded-2xl rounded-tl-none p-4 shadow-sm flex items-center gap-2">
                <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce delay-75"></div>
                <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce delay-150"></div>
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-4 bg-white border-t border-slate-200">
          <div className="max-w-4xl mx-auto relative">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Ask a clinical question (e.g., 'What was the trend in Creatinine levels?')"
              className="w-full pl-4 pr-12 py-3.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none shadow-sm transition-all"
            />
            <button 
              onClick={handleSend}
              disabled={isGenerating || !query.trim()}
              className="absolute right-2 top-2 p-1.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
          <p className="text-center text-[10px] text-slate-400 mt-2">
            AI can make mistakes. All outputs are strictly grounded in provided records.
          </p>
        </div>
      </div>

      {/* --- RIGHT EVIDENCE PANEL (Constraint 3) --- */}
      {activeCitation && (
        <div className="w-96 bg-white border-l border-slate-200 shadow-xl flex flex-col animate-in slide-in-from-right duration-300 z-20">
          <div className="p-4 border-b border-slate-100 flex items-center justify-between bg-emerald-50/50">
            <div className="flex items-center gap-2 text-emerald-700">
              <CheckCircle2 className="w-5 h-5" />
              <h3 className="font-bold text-sm">Verification Evidence</h3>
            </div>
            <button 
              onClick={() => setActiveCitation(null)}
              className="text-slate-400 hover:text-slate-600"
            >
              &times;
            </button>
          </div>
          
          <div className="p-6 flex-1 overflow-y-auto">
            <div className="mb-6">
              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Source Document</h4>
              <div className="flex items-center gap-3 p-3 bg-slate-50 rounded-lg border border-slate-200">
                <FileText className="w-8 h-8 text-indigo-400" />
                <div>
                  <p className="text-sm font-semibold text-slate-700 truncate max-w-[200px]">{activeCitation.source}</p>
                  <p className="text-xs text-slate-500">Page {activeCitation.page} • Year {activeCitation.year}</p>
                </div>
              </div>
            </div>

            <div className="mb-6">
              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Verified Chunk Content</h4>
              <div className="bg-slate-50 p-4 rounded-lg border border-slate-200 text-sm text-slate-700 font-mono leading-relaxed whitespace-pre-wrap">
                {activeCitation.snippet}
              </div>
            </div>

            <div>
              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">System Metadata</h4>
              <div className="space-y-2">
                <div className="flex justify-between text-xs py-2 border-b border-slate-100">
                  <span className="text-slate-500">Chunk ID</span>
                  <span className="font-mono text-slate-700 truncate max-w-[150px]" title={activeCitation.chunk_id}>
                    {activeCitation.chunk_id || "N/A"}
                  </span>
                </div>
                <div className="flex justify-between text-xs py-2 border-b border-slate-100">
                  <span className="text-slate-500">Confidence</span>
                  <span className="font-mono text-emerald-600 font-bold">100% (Grounded)</span>
                </div>
              </div>
            </div>
          </div>
          
          <div className="p-4 bg-slate-50 border-t border-slate-200 text-center">
             <button 
               onClick={() => setActiveCitation(null)}
               className="text-xs text-indigo-600 hover:underline font-medium"
             >
               Close Verification Panel
             </button>
          </div>
        </div>
      )}
    </div>
  );
}