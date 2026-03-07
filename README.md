# Vigilant AI — Sentinel Stream

> **AI-powered video surveillance intelligence built at HackIllinois 2026**

[![Modal](https://img.shields.io/badge/GPU-Modal_A100-7C3AED?style=flat-square&logo=lightning&logoColor=white)](https://modal.com)
[![Gemini](https://img.shields.io/badge/AI-Gemini_2.5_Flash-4285F4?style=flat-square&logo=google&logoColor=white)](https://deepmind.google/gemini)
[![Actian VectorAI](https://img.shields.io/badge/VectorDB-Actian_VectorAI-F97316?style=flat-square)](https://actian.com)
[![Supermemory](https://img.shields.io/badge/Memory-Supermemory-8B5CF6?style=flat-square)](https://supermemory.ai)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React_19-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev)

---

Vigilant AI transforms raw security footage into structured, searchable, queryable intelligence. Upload a video, and within minutes our GPU pipeline has detected every notable event, classified threats by severity, generated a natural-language report, embedded every clip as a semantic vector, and made it all searchable through a ChatGPT-style interface — in plain English.

No manual review. No timeline scrubbing. Just answers.

---

## Table of Contents

- [Features](#features)
- [How It Works](#how-it-works)
- [Tech Stack](#tech-stack)
- [ML Pipeline Deep Dive](#ml-pipeline-deep-dive)
- [Alert System](#alert-system)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [API Reference](#api-reference)
- [Sponsor Tracks](#sponsor-tracks)

---

## Features

**Core Intelligence**
- Upload any surveillance video (MP4/AVI/MOV, up to 5 GB)
- Automatic scene decomposition into overlapping sub-clips for parallel GPU processing
- Person detection, crowd counting, and motion scoring on every frame
- Vision-language captioning using two models simultaneously (GPU + API)
- Three-stage threat classification: **Stage A** (suspicious) → **Stage B** (concerning) → **Stage C** (critical)
- Holistic video synthesis: overall risk level, behavioral intent, and named key moments

**Search & Chat**
- ChatGPT-style interface to interrogate any video in natural language
- Hybrid search: CLIP semantic vector search + SQLite keyword fallback running in parallel
- Server-Sent Events (SSE) streaming — clip results appear instantly, AI narrative follows
- Per-video and cross-video memory queries via Supermemory

**Reports & Export**
- One-click incident report download as **TXT** or **PDF**
- Report includes timeline, severity breakdown, affected parties, and AI narrative
- Persistent cross-video behavioral intelligence stored to Supermemory

**Benchmarks**
- Live Modal GPU compute dashboard: speedup factor, VRAM allocation, per-video timing
- Live Actian VectorAI latency dashboard: encode time, search latency, vector count

---

## How It Works

```
User uploads video
        │
        ▼
┌──────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                           │
│  • Receives upload, stores to Modal Volume                   │
│  • Kicks off Modal pipeline via .spawn()                     │
│  • Polls status, streams SSE progress to frontend            │
└──────────────────┬───────────────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────────────┐
│               Modal Serverless GPU (A100 40GB)               │
│                                                              │
│  PHASE 1 — CPU  (chunk_and_score.map)                        │
│  ┌─────────────────────────────────────────────────────┐     │
│  │ Video → 30s chunks → sub-clips → motion scoring     │     │
│  │ Each chunk processed in a parallel Modal container  │     │
│  └─────────────────────────────────────────────────────┘     │
│                                                              │
│  PHASE 2 — GPU  (FeatureExtractor.map)                       │
│  ┌─────────────────────────────────────────────────────┐     │
│  │  YOLO11-L          →  person detection + labels     │     │
│  │  CLIP ViT-L/14     →  768-dim semantic embedding    │     │
│  │  Qwen2.5-VL-7B  ┐  →  GPU vision caption            │     │
│  │  Gemini Vision  ┘  →  API vision caption (parallel) │     │
│  │                                                     │     │
│  │  Merge: Gemini caption + OR-union boolean flags     │     │
│  │  Alert scoring: motion × people × label confidence  │     │
│  └─────────────────────────────────────────────────────┘     │
└──────────────────┬───────────────────────────────────────────┘
                   │  events JSON
                   ▼
┌──────────────────────────────────────────────────────────────┐
│                   Ingest Pipeline                            │
│                                                              │
│  ① SQLite      — structured events + video metadata         │
│  ② VectorAI    — 768-dim CLIP embeddings (cosine search)     │
│  ③ Gemini 2.5  — holistic video synthesis (risk + intent)   │
│  ④ Supermemory — cross-video behavioral intelligence         │
└──────────────────┬───────────────────────────────────────────┘
                   │
                   ▼
        React 19 frontend
  ┌─────────────────────────────┐
  │  Chat · Alerts · Insights  │
  │  Memory · Reports · Bench  │
  └─────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology | Why We Chose It |
|---|---|---|
| **GPU Compute** | [Modal](https://modal.com) | Serverless A100s, per-second billing, automatic parallel containers via `.map()`. We run 3 heavy neural networks without managing any infrastructure. |
| **Object Detection** | YOLO11-L | State-of-the-art real-time detector. Gives us per-frame person counts, bounding boxes, and activity labels at high throughput on GPU. |
| **Semantic Search** | CLIP ViT-L/14 (OpenAI) | Maps images and text into the same 768-dimensional embedding space — the backbone of natural language video search. We store every clip's embedding in VectorAI. |
| **GPU Captioning** | Qwen2.5-VL-7B | Open-source 7B vision-language model running directly on our A100. Provides forensic-quality frame analysis with no API rate limits, no content restrictions, and near-zero marginal cost per clip. BF16 precision, SDPA attention. |
| **API Captioning** | Gemini 2.0 Flash Vision | Google's best multimodal model. Used as the primary caption quality source; its descriptions feed into synthesis. Runs in a background thread while Qwen runs on GPU simultaneously. |
| **Video Synthesis** | Gemini 2.5 Flash | Given structured clip data (labels, flags, captions, alert scores), generates a holistic human-readable summary with risk level, behavioral intent, and named key moments. |
| **Vector Database** | Actian VectorAI | Purpose-built vector store with a gRPC interface. Sub-100ms cosine similarity search over 768-dim CLIP embeddings. Runs locally in Docker. |
| **Cross-Video Memory** | Supermemory | Persistent long-term memory API. After each video, behavioral intelligence is stored. Users can query across all historical footage in natural language. |
| **Backend** | FastAPI (Python) | Async web framework with first-class Server-Sent Events support — critical for our two-phase streaming chat (clips first, then narrative). |
| **Structured Storage** | SQLite | Zero-config relational database for events, alerts, video metadata, and chat history. No setup, ships with Python. |
| **Frontend** | React 19 + TypeScript | Component model and strict types keep the codebase maintainable under hackathon time pressure. |
| **Styling** | Tailwind CSS v4 | Utility-first, zero custom CSS. The `@theme {}` block in `index.css` handles all custom animations without a config file. |

---

## ML Pipeline Deep Dive

### Three Neural Networks on One A100

The GPU container loads three models at startup and keeps them warm across clips:

```
A100 40GB VRAM
├── YOLO11-L           ~2.0 GB   Object detection
├── CLIP ViT-L/14      ~1.5 GB   768-dim embeddings
└── Qwen2.5-VL-7B      ~15.5 GB  Vision-language model (BF16)
                       ─────────
    Total              ~19 GB    (21 GB free headroom)
```

### Dual-Model Captioning (Parallel)

For every sub-clip, we run two captioning models **simultaneously**:

```python
# Gemini runs in a background thread
threading.Thread(target=lambda: gemini_result.set(caption_gemini(frames))).start()

# Qwen runs on GPU in the main thread
qwen_result = caption_qwen(frames)   # actual GPU inference

# Merge: Gemini caption (quality) + OR-union of boolean flags
caption    = gemini_result if gemini_result else qwen_result
is_fighting = gemini.is_fighting OR qwen.is_fighting
is_stealing = gemini.is_stealing OR qwen.is_stealing
```

This gives us:
- **Quality**: Gemini's superior natural language descriptions
- **Coverage**: Qwen's GPU-local flags as a secondary signal
- **Resilience**: If Gemini times out or fails, Qwen's caption is used as fallback

### CLIP Embedding (Version-Stable)

We access CLIP's sub-modules directly instead of `get_image_features()` to guarantee consistent output shape across transformers library versions:

```python
vision_out = clip_model.vision_model(pixel_values=pixel_values)
pooled     = vision_out.pooler_output          # [N, 1024]  CLS token
feats      = clip_model.visual_projection(pooled)  # [N, 768]  projected
```

### Safety Net — CV Labels Override Synthesis

Gemini's synthesis can sometimes under-call a threat based on captions. We have a programmatic validator that runs after synthesis:

- If ≥ 30% of clips have a threat CV label but synthesis says `normal_activity` → override intent and bump risk
- If ≥ 50% of clips triggered alerts but risk is `low` → bump to `medium`

---

## Alert System

Every processed clip receives a score based on motion magnitude, person count, label confidence, and VLM boolean flags. Clips that cross thresholds are assigned a stage:

| Stage | Color | Meaning | Trigger |
|---|---|---|---|
| **A** | 🟡 Yellow | Suspicious activity | Score ≥ 0.40 |
| **B** | 🟠 Orange | Concerning behavior | Score ≥ 0.65 |
| **C** | 🔴 Red | Critical incident | Score ≥ 0.85 |

Stage C alerts trigger a pulsing red badge in the UI header and a red ambient glow on the analysis card.

---

## Project Structure

```
HackIllinois/
├── backend/                    Python + FastAPI
│   ├── api/
│   │   └── main.py             REST + SSE endpoints
│   ├── workers/
│   │   ├── inference.py        Modal GPU — YOLO, CLIP, Qwen, Gemini
│   │   ├── pipeline.py         CPU phase — chunking, scoring, alert logic
│   │   └── models.py           Pydantic schemas
│   ├── services/
│   │   ├── db.py               SQLite helpers
│   │   ├── vectordb.py         Actian VectorAI gRPC client
│   │   ├── clip_search.py      Hybrid CLIP + SQLite search
│   │   ├── gemini_synthesis.py Holistic video synthesis prompt
│   │   ├── ingest.py           Post-processing ingest pipeline
│   │   ├── incident_report.py  TXT + PDF report generation
│   │   └── supermemory_client.py Cross-video memory store/query
│   └── .env                    API keys (gitignored)
│
├── vigilant-ai/                React 19 + TypeScript + Tailwind v4
│   └── src/
│       ├── pages/
│       │   ├── HomePage.tsx    Video list, global memory chat, upload
│       │   ├── VideoPage.tsx   ChatGPT chat, alerts, insights, memory
│       │   └── BenchmarkPage.tsx Modal + VectorAI performance dashboard
│       ├── api.ts              Typed API client + SSE stream helpers
│       └── index.css           Tailwind v4 @theme animations
│
└── actian-vectorAI-db-beta/    Local VectorAI Docker setup
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- [Modal account](https://modal.com) with CLI configured (`pip install modal && modal setup`)
- [Docker](https://docker.com) (for Actian VectorAI local instance)
- API keys: `GEMINI_API_KEY`, `SUPERMEMORY_API_KEY`

### 1 — Backend

```bash
cd backend

# Create and activate virtual environment
python -m venv .venv
source .venv/Scripts/activate   # Windows
# source .venv/bin/activate     # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
GEMINI_API_KEY=your_gemini_key_here
SUPERMEMORY_API_KEY=your_supermemory_key_here
EOF

# Start the API server
uvicorn api.main:app --reload --port 8000
```

### 2 — Modal GPU Pipeline

```bash
# Deploy the inference worker to Modal
modal deploy workers/inference.py

# Pre-download models to Modal Volume (first time only — ~17GB)
modal run workers/inference.py::download_models
```

### 3 — Actian VectorAI

```bash
cd actian-vectorAI-db-beta
# Follow the Docker setup in that directory's README
# VectorAI will be available at localhost:50051
```

### 4 — Frontend

```bash
cd vigilant-ai
npm install
npm run dev
# Open http://localhost:5173
```

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/upload` | Upload a video file and start processing |
| `GET` | `/api/upload/status/{id}` | Poll processing status |
| `GET` | `/api/videos` | List all processed videos |
| `GET` | `/api/videos/{id}/alerts` | Get all alerts for a video |
| `GET` | `/api/videos/{id}/events` | Get all events for a video |
| `GET` | `/api/videos/{id}/summary` | Get AI synthesis (risk, intent, key moments) |
| `GET` | `/api/videos/{id}/insights` | Get aggregated stats and timeline |
| `GET` | `/api/videos/{id}/report` | Download incident report (TXT or PDF) |
| `GET` | `/api/chat/stream` | SSE chat stream (CLIP search + Gemini narration) |
| `GET` | `/api/chat/history/{id}` | Get chat history for a video |
| `POST` | `/api/memory/query` | Cross-video Supermemory intelligence query |
| `GET` | `/api/benchmarks/modal` | Live Modal GPU compute metrics |
| `GET` | `/api/benchmarks/vectorai` | Live VectorAI search latency metrics |

---

## Sponsor Tracks

### Modal — AI Inference Track

We run **three heavy neural networks simultaneously on a single A100**:

- `YOLO11-L` for real-time object detection
- `CLIP ViT-L/14` for 768-dimensional semantic embeddings
- `Qwen2.5-VL-7B` (7 billion parameter vision-language model) for on-GPU forensic captioning

Total GPU footprint: ~19 GB of 40 GB VRAM. All models are pre-warmed and re-used across clips within a container using Modal's container lifecycle hooks. Videos are processed in parallel across multiple containers using Modal's `.map()` API. A100 GPU time is billed per-second with zero idle cost.

**Why Modal?** Provisioning an A100 server for a hackathon would be impractical. Modal gave us enterprise-grade GPU compute on demand, paid only for the seconds we used, with automatic container scaling.

### Actian VectorAI — Vector Database Track

Every processed video clip is stored as a **768-dimensional CLIP embedding** in Actian VectorAI using cosine similarity distance. When a user searches ("show me fights"), we:

1. Encode the query text with CLIP's text encoder
2. Run cosine similarity search in VectorAI (gRPC)
3. Merge results with a parallel SQLite keyword search
4. Return ranked clips in < 100ms end-to-end

VectorAI's purpose-built architecture delivers sub-100ms similarity search at this dimensionality with no extra configuration.

### Supermemory — Memory Track

After every video is processed, we store a structured intelligence document to Supermemory:

```
Video: store_entrance_cam_03.mp4
Risk: HIGH | Intent: assault/fighting
Incidents: physical_altercation at 02:14, 03:51
Alerts: Stage C × 2, Stage B × 1
Duration: 8.3 min | People: up to 4
```

This creates a persistent, queryable memory across all historical footage. Security operators can ask "Have we seen this person fight before?" or "Show all high-risk incidents in the last month" in natural language — across every camera feed ever analyzed.

---

## Key Design Decisions

**Synthesis Authority Hierarchy**

Early versions let Gemini's synthesis override correct CV detections. A clip captioned as "person bending over to pick something up" could suppress a `physical_altercation` CV label. We fixed this with a strict authority chain:

```
CV label (authoritative) > VLM flags > caption text
```

The synthesis prompt explicitly states: *"CV_LABEL is the output of computer vision. It is authoritative. Trust CV_LABEL over captions."* A programmatic post-synthesis validator provides an additional safety net.

**False Positive Suppression**

Generic motion verbs (`grab`, `pick up`, `reach`) were generating false shoplifting detections in assault footage. We replaced them with context-specific multi-word phrases (`concealing merchandise`, `removes item from shelf`, `slips into pocket`) and changed the theft synthesis rule from "any clip" to "≥2 clips or single clip with ≥0.75 confidence."

**Two-Phase SSE Chat**

The chat interface uses a two-phase streaming pattern:
1. **Phase 1** — CLIP + SQLite hybrid search completes; matching clips fire immediately via an `event: results` SSE message
2. **Phase 2** — Gemini narration streams token-by-token via `event: token` SSE messages

Users see video clips appear within ~200ms while the full AI response is still being generated.

---

## Built at HackIllinois 2026

Vigilant AI was built in a weekend at HackIllinois 2026, University of Illinois Urbana-Champaign.

The goal was to demonstrate that modern open-weight vision models, serverless GPU infrastructure, and purpose-built vector databases can together solve a real-world safety problem — with a production-quality developer experience — in under 48 hours.

---

## License

MIT
