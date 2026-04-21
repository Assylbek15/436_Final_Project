import { useState } from "react";
import { motion } from "framer-motion";
import { Upload, Loader2 } from "lucide-react";

interface FileUploaderProps {
  loading: boolean;
  onUpload: (file: File) => void;
}

export default function FileUploader({ loading, onUpload }: FileUploaderProps) {
  const [dragActive, setDragActive] = useState(false);

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) onUpload(file);
  }

  function handleDrop(e: React.DragEvent) {
    e.preventDefault();
    setDragActive(false);
    const file = e.dataTransfer.files?.[0];
    const isPdf = file?.type === "application/pdf";
    const isZip = file?.type === "application/zip" || file?.name.endsWith(".zip");
    if (file && (isPdf || isZip)) onUpload(file);
  }

  function handleDrag(e: React.DragEvent) {
    e.preventDefault();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex items-center justify-center min-h-[60vh]"
    >
      <div className="w-full max-w-2xl">
        <div className="text-center mb-8">
          <h2 className="text-4xl font-black mb-3 bg-gradient-to-r from-gray-300 via-white to-gray-400 bg-clip-text text-transparent">
            Upload Your Document
          </h2>
          <p className="text-gray-400 text-lg">
            Drag and drop or click to select a PDF or ZIP file
          </p>
        </div>

        <motion.div
          className="relative bg-gray-900/80 backdrop-blur-sm rounded-xl border border-gray-700/50 shadow-2xl overflow-hidden"
          whileHover={{ scale: 1.01 }}
          whileTap={{ scale: 0.99 }}
        >
          {/* macOS Window Controls */}
          <div className="bg-gray-800/90 border-b border-gray-700/50 px-4 py-3 flex items-center gap-2">
            <button className="w-3 h-3 rounded-full bg-red-500 hover:bg-red-600 transition-colors" />
            <button className="w-3 h-3 rounded-full bg-yellow-500 hover:bg-yellow-600 transition-colors" />
            <button className="w-3 h-3 rounded-full bg-green-500 hover:bg-green-600 transition-colors" />
          </div>

          {/* Upload Area */}
          <div
            className={`relative p-12 transition-all ${
              dragActive ? "bg-blue-500/10" : "bg-black/40"
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <input
              type="file"
              accept="application/pdf,.zip"
              onChange={handleFileChange}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              disabled={loading}
            />

            <div className="text-center pointer-events-none">
              {loading ? (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex flex-col items-center gap-4"
                >
                  <Loader2 className="w-16 h-16 text-blue-500 animate-spin" />
                  <p className="text-lg text-gray-300">
                    Processing your document...
                  </p>
                </motion.div>
              ) : (
                <>
                  <Upload className="w-16 h-16 text-gray-500 mx-auto mb-4" />
                  <p className="text-lg text-gray-300 mb-2">
                    Drop your PDF or ZIP here or click to browse
                  </p>
                  <p className="text-sm text-gray-500">PDF or ZIP files</p>
                </>
              )}
            </div>
          </div>
        </motion.div>
      </div>
    </motion.div>
  );
}
