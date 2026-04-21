import axios from "axios";
import type { AnalyzeResponse, BatchAnalyzeResponse } from "../types/types";

const API_BASE = "http://localhost:8000";

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
