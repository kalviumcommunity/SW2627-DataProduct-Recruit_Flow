'use client';

import React, { useRef, useState } from 'react';
import { UploadCloud, FileText, CheckCircle2, AlertCircle, Loader2, X } from 'lucide-react';

export default function UploadDropzone({ onFileUpload, isUploading, activeBatchId, batchMode }) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      handleFileSelected(file);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      handleFileSelected(file);
    }
  };

  const handleFileSelected = (file) => {
    const validExtensions = ['.csv', '.xlsx', '.xls', '.json'];
    const hasValidExt = validExtensions.some(ext => file.name.toLowerCase().endsWith(ext));
    
    if (!hasValidExt) {
      alert('Please upload a valid CSV, Excel (.xlsx, .xls), or JSON dataset.');
      return;
    }
    
    setSelectedFile(file);
    if (onFileUpload) {
      onFileUpload(file);
    }
  };

  const clearSelectedFile = (e) => {
    e.stopPropagation();
    setSelectedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="rounded-xl border border-[#27272A] bg-[#141417] p-6 shadow-xl">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-base font-semibold text-white">Upload Recruitment Dataset</h3>
          <p className="text-xs text-[#A1A1AA] mt-0.5">
            {batchMode === 'append' ? (
              <span>Mode: <strong className="text-[#22C55E]">Appending to Batch #{activeBatchId || 'Active'}</strong></span>
            ) : (
              <span>Mode: <strong className="text-[#38BDF8]">New Ingestion Batch Session</strong></span>
            )}
          </p>
        </div>
        <span className="text-[11px] font-mono px-2.5 py-1 rounded bg-[#27272A] text-[#D4D4D8] border border-[#3F3F46]">
          Supported: CSV, XLSX, XLS, JSON
        </span>
      </div>

      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`relative flex flex-col items-center justify-center rounded-lg border-2 border-dashed p-10 text-center transition-all cursor-pointer ${
          isDragOver
            ? 'border-[#38BDF8] bg-[#38BDF8]/10'
            : 'border-[#3F3F46] bg-[#101014] hover:border-[#71717A] hover:bg-[#18181D]'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv,.xlsx,.xls,.json"
          onChange={handleFileChange}
          className="hidden"
        />

        {isUploading ? (
          <div className="flex flex-col items-center gap-3 py-4">
            <Loader2 className="w-10 h-10 text-[#38BDF8] animate-spin" />
            <p className="text-sm font-semibold text-white">Processing & Validating Batch Records...</p>
            <p className="text-xs text-[#A1A1AA]">Running schema checks, deduplication, and journey reconstruction.</p>
          </div>
        ) : selectedFile ? (
          <div className="flex flex-col items-center gap-3 py-2">
            <div className="flex items-center gap-3 px-4 py-2.5 rounded-lg bg-[#27272A] border border-[#3F3F46]">
              <FileText className="w-6 h-6 text-[#38BDF8]" />
              <div className="text-left">
                <p className="text-sm font-medium text-white">{selectedFile.name}</p>
                <p className="text-xs text-[#A1A1AA]">{(selectedFile.size / 1024).toFixed(1)} KB • Ready to Ingest</p>
              </div>
              <button
                onClick={clearSelectedFile}
                className="p-1 text-[#A1A1AA] hover:text-white hover:bg-[#3F3F46] rounded ml-2 transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <p className="text-xs text-[#22C55E] flex items-center gap-1 font-medium">
              <CheckCircle2 className="w-3.5 h-3.5" /> File parsed successfully. Drop another file to replace.
            </p>
          </div>
        ) : (
          <div className="flex flex-col items-center">
            <div className="w-12 h-12 rounded-full bg-[#27272A] flex items-center justify-center text-[#A1A1AA] mb-4">
              <UploadCloud className="w-6 h-6" />
            </div>
            <p className="text-sm font-semibold text-white mb-1">Drag and drop CSV or Excel files here</p>
            <p className="text-xs text-[#71717A] max-w-md mb-5">
              Drop candidates, interviews, offers, or stage event logs to populate the recruitment analytics pipeline.
            </p>
            <button
              type="button"
              className="px-5 py-2.5 rounded-md bg-white text-black text-xs font-semibold hover:bg-slate-200 transition-colors shadow"
            >
              Browse Files
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
