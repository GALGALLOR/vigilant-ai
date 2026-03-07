const API_BASE = '/api';

// ─── Types ──────────────────────────────────────────────────────────────────

export interface VideoInfo {
  id: string;
  name: string;
  duration_s: number;
  total_events: number;
  total_alerts: number;
  processing_time_s: number;
  gpu: string;
  upload_time: string;
  chunks?: number;
  subclips?: number;
  cpu_time_s?: number;
  gpu_time_s?: number;
}

export interface EventData {
  clip_id: string;
  video_source: string;
  start: number;
  end: number;
  duration: number;
  detections: { people_count: number; vehicle_count: number; peak_motion: number; mean_motion: number; contact_score: number; objects: Record<string, number> | null };
  event: { label: string; confidence: number };
  caption: string;
  tags: string[];
  alert: { score: number; stage: string; reason: string };
  similarity?: number;
  search_method?: string;
}

export interface VideoSummary {
  video_id: string;
  summary: string;
  intent: string[];
  key_moments: Array<{ time: string; description: string }>;
  risk_level: string;
  tags: string[];
}

export interface ChatMessage {
  id: number;
  role: 'user' | 'assistant';
  content: string;
  results?: EventData[] | null;
  created_at: string;
}

export interface InsightsData {
  video_id: string;
  event_types: Record<string, number>;
  alert_stages: Record<string, number>;
  timeline: Array<{ start: number; end: number; label: string; alert_stage: string; people: number }>;
  total_events: number;
  total_alerts: number;
}

export interface IncidentReport {
  report_id: string;
  video_id: string;
  video_name: string;
  generated_at: string;
  title: string;
  classification: string;
  severity: string;
  executive_summary: string;
  incident_window: { start: string; end: string; duration_s: number };
  parties: { total_persons: number; perpetrators_estimated: number; victims_estimated: number; note: string };
  key_moments: Array<{ time: string; description: string }>;
  physical_indicators: { contact_detected: boolean; max_contact_score: number; sustained: boolean };
  recommendations: string[];
  evidence_clips: Array<{ clip_id: string; time_start: string; time_end: string; stage: string; score: number; caption: string }>;
  total_alerts: number;
  total_events: number;
}

export interface MemoryQueryResult {
  query: string;
  answer: string;
  memories: Array<{ content: string; score: number; metadata: Record<string, unknown> }>;
  configured: boolean;
}

export interface ModalBenchmark {
  gpu_type: string;
  max_containers: number;
  peak_parallelism: number;
  total_videos_processed: number;
  total_subclips_processed: number;
  total_chunks: number;
  total_gpu_time_s: number;
  total_cpu_time_s: number;
  total_processing_s: number;
  avg_gpu_time_s: number;
  avg_cpu_time_s: number;
  estimated_serial_s: number;
  speedup_x: number;
  videos: Array<{ name: string; chunks: number; subclips: number; gpu_time_s: number; cpu_time_s: number; processing_s: number }>;
}

export interface VectorAIBenchmark {
  collection: string;
  dimensions: number;
  distance_metric: string;
  model: string;
  clip_encode_latency_ms: number;
  hybrid_search_latency_ms: number;
  total_vectors: number;
  results_returned: number;
}

export interface UploadResponse {
  video_id: string;
  video_name: string;
  size_mb: number;
  status: string;
  message: string;
}

export interface JobStatus {
  video_id: string;
  status: string;
  progress: number;
  error: string | null;
  message?: string;
}

// ─── Helper to extract flat fields from nested event ─────────────────────────

export function ev(e: EventData) {
  return {
    clipId: e.clip_id,
    start: e.start ?? 0,
    end: e.end ?? 0,
    duration: e.duration ?? ((e.end || 0) - (e.start || 0)),
    people: e.detections?.people_count ?? 0,
    vehicles: e.detections?.vehicle_count ?? 0,
    peakMotion: e.detections?.peak_motion ?? 0,
    contactScore: e.detections?.contact_score ?? 0,
    label: e.event?.label ?? 'activity',
    confidence: e.event?.confidence ?? 0,
    alertScore: e.alert?.score ?? 0,
    alertStage: e.alert?.stage ?? 'none',
    caption: e.caption ?? '',
    tags: Array.isArray(e.tags) ? e.tags : [],
    similarity: e.similarity,
    searchMethod: e.search_method,
  };
}

// ─── Fetch helper ────────────────────────────────────────────────────────────

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    const body = await res.text().catch(() => '');
    throw new Error(`API ${res.status}: ${body || res.statusText}`);
  }
  return res.json();
}

// ─── API ─────────────────────────────────────────────────────────────────────

export const api = {
  health: () => apiFetch<{ status: string }>('/health'),

  listVideos: () => apiFetch<{ videos: VideoInfo[] }>('/videos'),

  videoEvents: (videoId: string, limit = 100) =>
    apiFetch<{ video_id: string; count: number; events: EventData[] }>(
      `/videos/${videoId}/events?limit=${limit}`
    ),

  videoAlerts: (videoId: string) =>
    apiFetch<{ video_id: string; count: number; alerts: EventData[] }>(
      `/videos/${videoId}/alerts`
    ),

  videoSummary: (videoId: string) =>
    apiFetch<VideoSummary | { video_id: string; summary: null }>(
      `/videos/${videoId}/summary`
    ),

  videoInsights: (videoId: string) =>
    apiFetch<InsightsData>(`/videos/${videoId}/insights`),

  chatHistory: (videoId: string) =>
    apiFetch<{ video_id: string; messages: ChatMessage[] }>(
      `/videos/${videoId}/chat`
    ),

  uploadVideo: async (file: File, onProgress?: (pct: number) => void): Promise<UploadResponse> => {
    const form = new FormData();
    form.append('file', file);
    const xhr = new XMLHttpRequest();
    return new Promise((resolve, reject) => {
      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable && onProgress) onProgress(Math.round((e.loaded / e.total) * 100));
      });
      xhr.addEventListener('load', () => {
        if (xhr.status >= 200 && xhr.status < 300) resolve(JSON.parse(xhr.responseText));
        else reject(new Error(`Upload failed: ${xhr.status}`));
      });
      xhr.addEventListener('error', () => reject(new Error('Upload failed')));
      xhr.open('POST', `${API_BASE}/upload`);
      xhr.send(form);
    });
  },

  uploadStatus: (videoId: string) =>
    apiFetch<JobStatus>(`/upload/status/${videoId}`),

  chat: (query: string, videoId?: string, topK = 10) =>
    apiFetch<{ query: string; answer: string; count: number; results: EventData[] }>(
      '/chat',
      { method: 'POST', body: JSON.stringify({ query, video_id: videoId, top_k: topK }) }
    ),

  chatStream: (
    query: string,
    videoId?: string,
    topK = 10,
    onResults?: (count: number, results: EventData[]) => void,
  ): ReadableStream<string> => {
    let controller: ReadableStreamDefaultController<string>;
    const stream = new ReadableStream<string>({
      start(c) { controller = c; },
    });
    fetch(`${API_BASE}/chat/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, video_id: videoId, top_k: topK }),
    }).then(async (res) => {
      if (!res.ok || !res.body) { controller.error(new Error(`API ${res.status}`)); return; }
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buf = '';
      let lastEvent = '';
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buf += decoder.decode(value, { stream: true });
        const lines = buf.split('\n');
        buf = lines.pop() ?? '';
        for (const line of lines) {
          if (line.startsWith('event: ')) { lastEvent = line.slice(7).trim(); continue; }
          if (!line.startsWith('data: ')) continue;
          const payload = line.slice(6).trim();
          if (lastEvent === 'results') {
            try {
              const d = JSON.parse(payload);
              onResults?.(d.count, d.results);
            } catch { /* skip */ }
          } else if (lastEvent === 'token') {
            try { controller.enqueue(JSON.parse(payload) as string); } catch { /* skip */ }
          } else if (lastEvent === 'done') {
            controller.close(); return;
          }
          lastEvent = '';
        }
      }
      controller.close();
    }).catch(e => controller.error(e));
    return stream;
  },

  videoInfo: (videoId: string) =>
    apiFetch<VideoInfo>(`/videos/${videoId}`),

  videoReport: (videoId: string) =>
    apiFetch<IncidentReport>(`/videos/${videoId}/report`),

  videoReportTextUrl: (videoId: string) =>
    `${API_BASE}/videos/${videoId}/report?as_text=true`,

  videoReportPdfUrl: (videoId: string) =>
    `${API_BASE}/videos/${videoId}/report?as_pdf=true`,

  queryMemory: (query: string, videoId?: string) =>
    apiFetch<MemoryQueryResult>('/memory/query', {
      method: 'POST',
      body: JSON.stringify({ query, video_id: videoId }),
    }),

  modalBenchmarks: () => apiFetch<ModalBenchmark>('/benchmarks/modal'),

  vectoraiBenchmarks: () => apiFetch<VectorAIBenchmark>('/benchmarks/vectorai'),

  stats: () => apiFetch<{
    total_videos: number; total_events: number;
    total_alerts: number; total_tracks: number;
    latest_video: VideoInfo | null;
  }>('/stats'),
};
