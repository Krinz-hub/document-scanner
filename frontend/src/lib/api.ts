export interface ScreeningSummary {
  id: string;
  checkpoint_id: string;
  status: string;
  review_priority: string;
  created_at: string;
  updated_at?: string;
}

export interface DocumentRecord {
  id: string;
  screening_id: string;
  type?: string;
  document_number_hash?: string;
  issue_date?: string;
  expiry_date?: string;
  object_reference?: string;
  created_at: string;
}

export interface ExtractedField {
  id: string;
  field_name: string;
  value_text?: string;
  confidence: number;
  source: string;
}

export interface EvidenceItem {
  id: string;
  category: string;
  severity: "INFO" | "WARNING" | "CRITICAL";
  explanation: string;
  source_module: string;
}

export interface ScreeningDetail {
  id: string;
  checkpoint_id: string;
  status: string;
  review_priority: string;
  created_at: string;
  updated_at?: string;
  documents: DocumentRecord[];
  extracted_fields: ExtractedField[];
  evidence_items: EvidenceItem[];
  reasons: string[];
  verification: {
    mrz: string;
    external: string;
    face: string;
  };
  analysis: {
    photo: string;
    text: string;
    stamp: string;
  };
}

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1";

async function fetchJson<T>(endpoint: string, init?: RequestInit): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  try {
    const res = await fetch(url, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...init?.headers,
      },
      cache: "no-store",
    });

    if (!res.ok) {
      const errorBody = await res.text();
      let errorMsg = `HTTP ${res.status} ${res.statusText}`;
      try {
        const parsed = JSON.parse(errorBody);
        if (parsed.detail) errorMsg = parsed.detail;
      } catch {
        // Fallback to text
      }
      throw new Error(errorMsg);
    }

    return (await res.json()) as T;
  } catch (err: any) {
    throw new Error(err.message || "Failed to communicate with screening backend");
  }
}

export const api = {
  getHealth: () => fetchJson<{ status: string; app: string; database: string }>("/health"),

  listScreenings: () => fetchJson<ScreeningSummary[]>("/screenings"),

  getScreening: (id: string) => fetchJson<ScreeningDetail>(`/screenings/${id}`),

  createScreening: (checkpoint_id: string = "CP-01") =>
    fetchJson<ScreeningDetail>("/screenings", {
      method: "POST",
      body: JSON.stringify({ checkpoint_id }),
    }),

  getScreeningEvidence: (id: string) => fetchJson<EvidenceItem[]>(`/screenings/${id}/evidence`),
};
