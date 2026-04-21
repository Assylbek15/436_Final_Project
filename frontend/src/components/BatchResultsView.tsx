import { useState } from "react";
import { motion } from "framer-motion";
import { CheckCircle, Copy, Check } from "lucide-react";
import type { BatchAnalyzeResponse } from "../types/types";

interface BatchResultsViewProps {
  result: BatchAnalyzeResponse;
  onReset: () => void;
}

export default function BatchResultsView({
  result,
  onReset,
}: BatchResultsViewProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    const jsonString = JSON.stringify(result, null, 2);
    navigator.clipboard.writeText(jsonString);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      <div className="flex items-center justify-between mb-8">
        {/* LEFT SIDE — Title */}
        <div className="flex items-center gap-3">
          <CheckCircle className="w-8 h-8 text-green-500" />
          <h2 className="text-3xl font-black bg-gradient-to-r from-gray-300 via-white to-gray-400 bg-clip-text text-transparent">
            Batch Analysis Complete
          </h2>
        </div>

        {/* RIGHT SIDE — Buttons */}
        <div className="flex items-center gap-4">
          {/* COPY BUTTON */}
          <button
            onClick={handleCopy}
            className="flex items-center gap-2 px-6 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-white font-semibold shadow-md transition"
          >
            {copied ? (
              <>
                <Check className="w-5 h-5" />
                Copied!
              </>
            ) : (
              <>
                <Copy className="w-5 h-5" />
                Copy JSON
              </>
            )}
          </button>

          {/* RESET BUTTON */}
          <button
            onClick={onReset}
            className="px-6 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors font-semibold"
          >
            Upload New File
          </button>
        </div>
      </div>

      {/* INFO SECTION */}
      <div className="mb-6 p-4 bg-gray-900/50 border border-gray-800 rounded-lg">
        <div className="flex items-center gap-6 text-sm">
          <div>
            <span className="text-gray-400">Job ID:</span>{" "}
            <span className="text-white font-mono">{result.job_id}</span>
          </div>
          <div>
            <span className="text-gray-400">Files Processed:</span>{" "}
            <span className="text-white font-semibold">
              {result.files_processed}
            </span>
          </div>
        </div>
      </div>

      {/* JSON DISPLAY */}
      <div className="bg-gray-900/50 border border-gray-800 rounded-xl overflow-hidden">
        <div className="p-6 border-b border-gray-800">
          <h3 className="text-xl font-bold">Analysis Results (JSON)</h3>
        </div>

        <div className="p-6">
          <div className="bg-gray-950 rounded-lg p-6 border border-gray-800 max-h-[70vh] overflow-auto">
            <pre className="text-sm text-gray-300 font-mono whitespace-pre-wrap break-words">
              {JSON.stringify(result.result, null, 2)}
            </pre>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
