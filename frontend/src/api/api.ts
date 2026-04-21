import axios from "axios";
import type { AnalyzeResponse, BatchAnalyzeResponse } from "../types/types";

const rawApiBase = (import.meta.env.VITE_API_BASE ?? "").trim();

function isLoopbackUrl(value: string): boolean {
  try {
    const { hostname } = new URL(value);
    return hostname === "localhost" || hostname === "127.0.0.1" || hostname === "0.0.0.0";
  } catch {
    return false;
  }
}

const isRemotePage =
  typeof window !== "undefined" &&
  window.location.hostname !== "localhost" &&
  window.location.hostname !== "127.0.0.1" &&
  window.location.hostname !== "0.0.0.0";

const API_BASE =
  isRemotePage && isLoopbackUrl(rawApiBase)
    ? ""
    : rawApiBase.replace(/\/$/, "");

export async function analyzePdf(file: File): Promise<AnalyzeResponse> {
  const formData = new FormData();
  formData.append("pdf_file", file);

  const res = await axios.post(`${API_BASE}/analyze`, formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

  return res.data;
}

export async function analyzeBatch(file: File): Promise<BatchAnalyzeResponse> {
  const formData = new FormData();
  formData.append("zip_file", file);

  const res = await axios.post(`${API_BASE}/batch-analyze`, formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

  return res.data;
}
