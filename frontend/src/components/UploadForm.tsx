import { useState } from "react";
import type { AnalyzeResponse, BatchAnalyzeResponse } from "../types/types";
import Header from "./Header";
import FileUploader from "./FileUploader";
import ResultsView from "./ResultsView";
import BatchResultsView from "./BatchResultsView";
import { analyzePdf, analyzeBatch } from "../api/api";

export default function UploadForm() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [batchResult, setBatchResult] = useState<BatchAnalyzeResponse | null>(
    null
  );

  async function handleUpload(file: File) {
    setLoading(true);
    try {
      const isZip =
        file.type === "application/zip" || file.name.endsWith(".zip");

      if (isZip) {
        const data = await analyzeBatch(file);
        setBatchResult(data);
        setResult(null);
      } else {
        const data = await analyzePdf(file);
        setResult(data);
        setBatchResult(null);
      }
    } catch (err) {
      console.error(err);
      alert("Upload failed");
    }
    setLoading(false);
  }

  function handleReset() {
    setResult(null);
    setBatchResult(null);
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 via-black to-gray-900 text-white">
      <Header />

      <div className="px-4 sm:px-6 lg:px-8 py-12">
        <div className="max-w-7xl mx-auto">
          {!result && !batchResult && (
            <FileUploader loading={loading} onUpload={handleUpload} />
          )}
          {result && <ResultsView result={result} onReset={handleReset} />}
          {batchResult && (
            <BatchResultsView result={batchResult} onReset={handleReset} />
          )}
        </div>
      </div>
    </div>
  );
}
