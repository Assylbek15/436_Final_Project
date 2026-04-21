export interface BBox {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface Detection {
  category: string; // "qr_code", "stamp", etc.
  confidence: number;
  bbox: BBox;
}

export interface PageResult {
  page_index: number;
  page_size: {
    width: number;
    height: number;
  };
  detections: Detection[];
  annotated_image_url: string;
}

export interface AnalyzeResponse {
  job_id: string;
  pages: PageResult[];
  annotated_pdf_url: string;
  result: Record<string, Record<string, BatchPageResult>>;  // Added parent JSON structure
}

// Batch analysis types
export interface BatchAnnotation {
  category: string;
  bbox: BBox;
  area: number;
}

export interface BatchPageResult {
  annotations: Record<string, BatchAnnotation>[];
  page_size: {
    width: number;
    height: number;
  };
}

export interface BatchAnalyzeResponse {
  job_id: string;
  files_processed: number;
  result: Record<string, Record<string, BatchPageResult> | { error: string }>;
}
