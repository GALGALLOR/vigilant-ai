import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
    ArrowLeft, Zap, Database, Cpu, Server, Activity,
    Clock, Layers, GitBranch, Search, RefreshCw, Eye
} from 'lucide-react'
import { api, type ModalBenchmark, type VectorAIBenchmark } from '../api'

// ─── Helpers ─────────────────────────────────────────────────────────────────

function MetricCard({
    icon, label, value, unit, color, sub,
}: {
    icon: React.ReactNode
    label: string
    value: string | number
    unit?: string
    color: 'indigo' | 'violet' | 'emerald' | 'orange' | 'red' | 'cyan'
    sub?: string
}) {
    const colors: Record<string, string> = {
        indigo:  'text-indigo-600 border-indigo-200 bg-indigo-50',
        violet:  'text-violet-600 border-violet-200 bg-violet-50',
        emerald: 'text-emerald-600 border-emerald-200 bg-emerald-50',
        orange:  'text-orange-600 border-orange-200 bg-orange-50',
        red:     'text-red-600 border-red-200 bg-red-50',
        cyan:    'text-cyan-600 border-cyan-200 bg-cyan-50',
    }
    return (
        <div className={`rounded-xl border p-4 animate-fade-up shadow-sm ${colors[color]}`}>
            <div className="flex items-center gap-2 mb-2">
                <span className="opacity-60">{icon}</span>
                <span className="text-[10px] text-gray-500 uppercase tracking-wider font-semibold">{label}</span>
            </div>
            <div className="flex items-end gap-1.5">
                <span className="text-3xl font-bold tabular-nums">{value}</span>
                {unit && <span className="text-sm opacity-40 mb-0.5">{unit}</span>}
            </div>
            {sub && <p className="text-[10px] text-gray-400 mt-1">{sub}</p>}
        </div>
    )
}

function SectionHeader({ icon, title, badge }: { icon: React.ReactNode; title: string; badge: string }) {
    return (
        <div className="flex items-center gap-3 mb-5">
            <div className="relative w-10 h-10 shrink-0">
                <div className="absolute inset-0 bg-gradient-to-br from-amber-400 to-orange-500 rounded-xl blur-sm opacity-40" />
                <div className="relative w-10 h-10 bg-gradient-to-br from-amber-400 to-orange-500 rounded-xl flex items-center justify-center">
                    {icon}
                </div>
            </div>
            <div>
                <h2 className="text-base font-bold text-gray-900">{title}</h2>
                <span className="text-[10px] text-gray-400 font-mono">{badge}</span>
            </div>
        </div>
    )
}

// ─── Modal Section ────────────────────────────────────────────────────────────

function ModalSection({ data }: { data: ModalBenchmark | null }) {
    if (!data) return (
        <div className="flex justify-center items-center py-16 text-gray-400 text-sm">
            <RefreshCw className="w-4 h-4 animate-spin mr-2" /> Loading Modal metrics…
        </div>
    )

    const hasData = data.total_videos_processed > 0

    return (
        <div className="space-y-5">
            <SectionHeader
                icon={<Zap className="w-5 h-5 text-white" />}
                title="Modal GPU Compute"
                badge="modal.com · A100 · up to 50 parallel containers"
            />

            {/* Key metrics */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <MetricCard icon={<Zap className="w-3.5 h-3.5" />}    label="Parallel Speedup"    value={hasData ? `${data.speedup_x}×` : '—'} color="orange" sub="vs sequential CPU baseline" />
                <MetricCard icon={<Server className="w-3.5 h-3.5" />} label="GPU Type"             value={data.gpu_type}                        color="violet" sub={`${data.max_containers} max containers`} />
                <MetricCard icon={<Layers className="w-3.5 h-3.5" />} label="Sub-clips Processed"  value={data.total_subclips_processed}        color="indigo" sub={`${data.total_chunks} chunks`} />
                <MetricCard icon={<Activity className="w-3.5 h-3.5" />} label="Videos Analyzed"    value={data.total_videos_processed}          color="emerald" sub="total since deployment" />
            </div>

            {/* GPU Model Stack — VRAM hero */}
            <div className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm">
                <p className="text-[10px] text-gray-400 uppercase tracking-wider font-semibold mb-3">
                    3 Neural Networks on A100 · VRAM Allocation (40 GB)
                </p>
                <div className="h-7 bg-gray-100 rounded-lg overflow-hidden flex mb-3">
                    <div className="h-full bg-gradient-to-r from-red-400 to-orange-400 transition-all duration-700" style={{ width: '5%' }} title="YOLO11-L ~2GB" />
                    <div className="h-full bg-gradient-to-r from-cyan-400 to-indigo-500 transition-all duration-700" style={{ width: '3.75%' }} title="CLIP ViT-L/14 ~1.5GB" />
                    <div className="h-full bg-gradient-to-r from-violet-500 to-purple-500 transition-all duration-700" style={{ width: '38.75%' }} title="Qwen2.5-VL-7B ~15.5GB" />
                    <div className="h-full bg-gray-200 flex-1" title="Free ~21GB" />
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-[11px]">
                    {[
                        { color: 'bg-gradient-to-r from-red-400 to-orange-400',     label: 'YOLO11-L',       vram: '~2 GB',    task: 'Object Detection' },
                        { color: 'bg-gradient-to-r from-cyan-400 to-indigo-500',    label: 'CLIP ViT-L/14',  vram: '~1.5 GB',  task: '768-dim Embeddings' },
                        { color: 'bg-gradient-to-r from-violet-500 to-purple-500',  label: 'Qwen2.5-VL-7B', vram: '~15.5 GB', task: 'Vision Captioning' },
                        { color: 'bg-gray-300',                                      label: 'Free',           vram: '~21 GB',   task: 'Headroom' },
                    ].map(({ color, label, vram, task }) => (
                        <div key={label} className="flex items-start gap-2">
                            <div className={`w-2.5 h-2.5 rounded-sm ${color} shrink-0 mt-0.5`} />
                            <div>
                                <p className="text-gray-700 font-medium">{label}</p>
                                <p className="text-gray-400">{vram} · {task}</p>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Speedup bar */}
            {hasData && (
                <div className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm">
                    <p className="text-[10px] text-gray-400 uppercase tracking-wider font-semibold mb-4">
                        GPU vs Sequential Estimate
                    </p>
                    <div className="space-y-3">
                        <div>
                            <div className="flex justify-between text-xs text-gray-500 mb-1.5">
                                <span className="flex items-center gap-1.5"><Zap className="w-3 h-3 text-violet-500" /> Modal GPU (parallel)</span>
                                <span className="font-mono text-violet-600">{data.total_gpu_time_s}s</span>
                            </div>
                            <div className="h-3 bg-gray-100 rounded-full overflow-hidden">
                                <div className="h-full bg-gradient-to-r from-violet-500 to-indigo-500 rounded-full transition-all duration-1000"
                                     style={{ width: `${Math.min((data.total_gpu_time_s / data.estimated_serial_s) * 100, 100)}%` }} />
                            </div>
                        </div>
                        <div>
                            <div className="flex justify-between text-xs text-gray-400 mb-1.5">
                                <span className="flex items-center gap-1.5"><Clock className="w-3 h-3 text-gray-400" /> Sequential CPU (estimated)</span>
                                <span className="font-mono text-gray-400">{data.estimated_serial_s}s</span>
                            </div>
                            <div className="h-3 bg-gray-100 rounded-full overflow-hidden">
                                <div className="h-full bg-gray-300 rounded-full w-full" />
                            </div>
                        </div>
                    </div>
                    <p className="text-[10px] text-gray-400 mt-3">
                        Sequential baseline: {data.total_subclips_processed} sub-clips × 8s/clip (single-core CPU) = {data.estimated_serial_s}s
                    </p>
                </div>
            )}

            {/* Timing breakdown */}
            {hasData && (
                <div className="grid grid-cols-3 gap-3">
                    {[
                        { label: 'Avg GPU Time',    value: `${data.avg_gpu_time_s}s`,       sub: 'per video',          cls: 'text-violet-600' },
                        { label: 'Avg CPU Time',    value: `${data.avg_cpu_time_s}s`,       sub: 'per video',          cls: 'text-gray-600' },
                        { label: 'Total Wall Time', value: `${data.total_processing_s}s`,   sub: 'all videos combined', cls: 'text-gray-800' },
                    ].map(({ label, value, sub, cls }) => (
                        <div key={label} className="bg-white border border-gray-200 rounded-xl p-3 text-center shadow-sm">
                            <p className="text-[10px] text-gray-400 uppercase tracking-wider mb-1">{label}</p>
                            <p className={`text-xl font-bold font-mono ${cls}`}>{value}</p>
                            <p className="text-[10px] text-gray-400">{sub}</p>
                        </div>
                    ))}
                </div>
            )}

            {/* Per-video table */}
            {data.videos.length > 0 && (
                <div className="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm">
                    <div className="px-4 py-3 border-b border-gray-100">
                        <p className="text-[10px] text-gray-400 uppercase tracking-wider font-semibold">Per-Video Breakdown</p>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="w-full text-xs">
                            <thead>
                                <tr className="border-b border-gray-100">
                                    <th className="px-4 py-2.5 text-left text-gray-400 font-medium">Video</th>
                                    <th className="px-3 py-2.5 text-right text-gray-400 font-medium">Chunks</th>
                                    <th className="px-3 py-2.5 text-right text-gray-400 font-medium">Sub-clips</th>
                                    <th className="px-3 py-2.5 text-right text-gray-400 font-medium">GPU</th>
                                    <th className="px-3 py-2.5 text-right text-gray-400 font-medium">CPU</th>
                                    <th className="px-4 py-2.5 text-right text-gray-400 font-medium">Total</th>
                                </tr>
                            </thead>
                            <tbody>
                                {data.videos.map((v, i) => (
                                    <tr key={i} className="border-b border-gray-50 hover:bg-gray-50 transition-colors">
                                        <td className="px-4 py-2.5 text-gray-700 max-w-[160px] truncate font-medium">{v.name}</td>
                                        <td className="px-3 py-2.5 text-right text-gray-400 font-mono">{v.chunks}</td>
                                        <td className="px-3 py-2.5 text-right text-gray-400 font-mono">{v.subclips}</td>
                                        <td className="px-3 py-2.5 text-right text-violet-600 font-mono font-medium">{v.gpu_time_s}s</td>
                                        <td className="px-3 py-2.5 text-right text-gray-400 font-mono">{v.cpu_time_s}s</td>
                                        <td className="px-4 py-2.5 text-right text-gray-700 font-mono font-medium">{v.processing_s}s</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}

            {!hasData && (
                <div className="bg-gray-50 border border-gray-200 rounded-xl p-6 text-center text-gray-400 text-sm">
                    <Cpu className="w-8 h-8 mx-auto mb-3 opacity-30" />
                    <p>No videos processed yet. Upload a video to see compute metrics.</p>
                </div>
            )}

            {/* Architecture note */}
            <div className="bg-gray-50 border border-gray-200 rounded-xl p-4 space-y-2">
                <p className="text-[10px] text-gray-400 uppercase tracking-wider font-semibold">Architecture</p>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-[11px]">
                    {[
                        { icon: <GitBranch className="w-3 h-3" />, label: 'CPU Phase',  value: 'chunk_and_score.map()' },
                        { icon: <Zap className="w-3 h-3" />,       label: 'GPU Phase',  value: 'FeatureExtractor.map()' },
                        { icon: <Server className="w-3 h-3" />,    label: 'Detection',  value: 'YOLO11-L + CLIP ViT-L/14' },
                        { icon: <Layers className="w-3 h-3" />,    label: 'Caption',    value: 'Qwen2.5-VL-7B + Gemini' },
                    ].map(({ icon, label, value }) => (
                        <div key={label} className="flex flex-col gap-1">
                            <div className="flex items-center gap-1 text-gray-400">
                                {icon}
                                <span className="uppercase tracking-wider text-[9px]">{label}</span>
                            </div>
                            <span className="text-gray-600 font-mono text-[10px]">{value}</span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    )
}

// ─── VectorAI Section ─────────────────────────────────────────────────────────

function VectorAISection({
    data, onRefresh, refreshing,
}: {
    data: VectorAIBenchmark | null
    onRefresh: () => void
    refreshing: boolean
}) {
    if (!data) return (
        <div className="flex justify-center items-center py-16 text-gray-400 text-sm">
            <RefreshCw className="w-4 h-4 animate-spin mr-2" /> Running live search test…
        </div>
    )

    const latencyColor = data.hybrid_search_latency_ms < 100 ? 'text-emerald-600' :
                         data.hybrid_search_latency_ms < 300 ? 'text-amber-600' : 'text-orange-600'

    return (
        <div className="space-y-5">
            <div className="flex items-center justify-between">
                <SectionHeader
                    icon={<Database className="w-5 h-5 text-white" />}
                    title="Actian VectorAI"
                    badge="CLIP 768-dim · COSINE distance · gRPC port 50051"
                />
                <button
                    onClick={onRefresh}
                    disabled={refreshing}
                    className="cursor-pointer flex items-center gap-1.5 text-xs text-gray-500 hover:text-gray-800 px-3 py-1.5 bg-white hover:bg-gray-50 border border-gray-200 rounded-lg transition-all disabled:opacity-40 disabled:cursor-not-allowed shadow-sm"
                >
                    <RefreshCw className={`w-3 h-3 ${refreshing ? 'animate-spin' : ''}`} />
                    {refreshing ? 'Testing…' : 'Re-run Test'}
                </button>
            </div>

            {/* Key metrics */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <MetricCard icon={<Search className="w-3.5 h-3.5" />}   label="Search Latency"   value={data.hybrid_search_latency_ms} unit="ms"   color="cyan"    sub="end-to-end hybrid search" />
                <MetricCard icon={<Cpu className="w-3.5 h-3.5" />}      label="CLIP Encode"      value={data.clip_encode_latency_ms}   unit="ms"   color="indigo"  sub="text → 768-dim vector" />
                <MetricCard icon={<Database className="w-3.5 h-3.5" />} label="Vectors Stored"   value={data.total_vectors}                        color="violet"  sub="CLIP embeddings" />
                <MetricCard icon={<Layers className="w-3.5 h-3.5" />}   label="Dimensions"       value={data.dimensions}                           color="emerald" sub={data.distance_metric} />
            </div>

            {/* Latency gauge */}
            <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
                <div className="flex items-center justify-between mb-4">
                    <p className="text-[10px] text-gray-400 uppercase tracking-wider font-semibold">Live Latency</p>
                    <span className={`text-xs font-mono font-bold ${latencyColor}`}>
                        {data.hybrid_search_latency_ms}ms
                    </span>
                </div>
                <div className="h-3 bg-gray-100 rounded-full overflow-hidden mb-2">
                    <div
                        className={`h-full rounded-full transition-all duration-700 ${
                            data.hybrid_search_latency_ms < 100 ? 'bg-gradient-to-r from-emerald-400 to-cyan-500' :
                            data.hybrid_search_latency_ms < 300 ? 'bg-gradient-to-r from-amber-400 to-orange-400' :
                            'bg-gradient-to-r from-orange-400 to-red-400'
                        }`}
                        style={{ width: `${Math.min((data.hybrid_search_latency_ms / 500) * 100, 100)}%` }}
                    />
                </div>
                <div className="flex justify-between text-[10px] text-gray-400 mb-4">
                    <span>0ms (instant)</span>
                    <span>250ms</span>
                    <span>500ms</span>
                </div>
                <div className="grid grid-cols-2 gap-3 text-xs">
                    <div className="flex items-center gap-2 text-gray-500">
                        <div className="w-2 h-2 rounded-full bg-cyan-400" />
                        <span>VectorAI similarity search</span>
                    </div>
                    <div className="flex items-center gap-2 text-gray-500">
                        <div className="w-2 h-2 rounded-full bg-indigo-400" />
                        <span>SQLite keyword fallback</span>
                    </div>
                </div>
            </div>

            {/* Specs */}
            <div className="bg-gray-50 border border-gray-200 rounded-xl p-4 space-y-2">
                <p className="text-[10px] text-gray-400 uppercase tracking-wider font-semibold">Technical Specs</p>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                    {[
                        { label: 'Collection',      value: data.collection },
                        { label: 'Model',           value: data.model },
                        { label: 'Distance',        value: data.distance_metric },
                        { label: 'Embedding dims',  value: String(data.dimensions) },
                        { label: 'Results / query', value: String(data.results_returned) },
                        { label: 'Search strategy', value: 'Hybrid (CLIP + BM25)' },
                    ].map(({ label, value }) => (
                        <div key={label} className="flex flex-col gap-0.5">
                            <span className="text-[10px] text-gray-400 uppercase tracking-wider">{label}</span>
                            <span className="text-[11px] text-gray-700 font-mono">{value}</span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    )
}

// ─── Main Page ────────────────────────────────────────────────────────────────

export default function BenchmarkPage() {
    const navigate = useNavigate()
    const [modalData,  setModalData]  = useState<ModalBenchmark | null>(null)
    const [vectorData, setVectorData] = useState<VectorAIBenchmark | null>(null)
    const [vectorRefreshing, setVectorRefreshing] = useState(false)

    useEffect(() => {
        api.modalBenchmarks().then(setModalData).catch(console.error)
        runVectorTest()
    }, [])

    const runVectorTest = () => {
        setVectorRefreshing(true)
        api.vectoraiBenchmarks().then(setVectorData).catch(console.error).finally(() => setVectorRefreshing(false))
    }

    return (
        <div className="min-h-screen bg-gray-50 text-gray-900">
            {/* Subtle ambient */}
            <div className="fixed inset-0 pointer-events-none overflow-hidden">
                <div className="absolute -top-20 left-1/3 w-96 h-80 bg-amber-200/20 rounded-full blur-3xl" />
                <div className="absolute bottom-1/3 right-1/4 w-72 h-72 bg-violet-200/20 rounded-full blur-3xl" />
            </div>

            {/* Header */}
            <header className="sticky top-0 z-30 bg-white/90 backdrop-blur-xl border-b border-gray-200 shadow-sm">
                <div className="max-w-5xl mx-auto px-4 sm:px-6 py-3 flex items-center gap-3">
                    <button
                        onClick={() => navigate('/')}
                        className="cursor-pointer p-1.5 hover:bg-gray-100 rounded-lg transition-all text-gray-400 hover:text-gray-700"
                    >
                        <ArrowLeft className="w-5 h-5" />
                    </button>
                    <div className="flex items-center gap-2.5 flex-1">
                        <div className="relative w-8 h-8 shrink-0">
                            <div className="absolute inset-0 bg-gradient-to-br from-amber-400 to-orange-500 rounded-lg blur-sm opacity-40" />
                            <div className="relative w-8 h-8 bg-gradient-to-br from-amber-400 to-orange-500 rounded-lg flex items-center justify-center">
                                <Eye className="w-4 h-4 text-white" />
                            </div>
                        </div>
                        <div>
                            <h1 className="text-sm font-semibold text-gray-900">Performance Benchmarks</h1>
                            <p className="text-[10px] text-gray-400">Live metrics from Modal GPU + Actian VectorAI</p>
                        </div>
                    </div>
                </div>
            </header>

            {/* Content */}
            <main className="max-w-5xl mx-auto px-4 sm:px-6 py-8 space-y-10 relative z-10">
                {/* Hero */}
                <div className="text-center py-4 animate-fade-up">
                    <h2 className="text-2xl sm:text-3xl font-bold bg-gradient-to-r from-amber-500 via-orange-500 to-amber-400 bg-clip-text text-transparent mb-2">
                        Real Compute Benchmarks
                    </h2>
                    <p className="text-sm text-gray-500 max-w-xl mx-auto">
                        Measured from actual video processing runs. Modal provides on-demand GPU parallelism;
                        Actian VectorAI handles 768-dimensional CLIP similarity search.
                    </p>
                </div>

                {/* Modal Section */}
                <div className="bg-white border border-gray-200 rounded-2xl p-5 sm:p-6 animate-fade-up shadow-sm">
                    <ModalSection data={modalData} />
                </div>

                {/* VectorAI Section */}
                <div className="bg-white border border-gray-200 rounded-2xl p-5 sm:p-6 animate-fade-up shadow-sm">
                    <VectorAISection
                        data={vectorData}
                        onRefresh={runVectorTest}
                        refreshing={vectorRefreshing}
                    />
                </div>

                <p className="text-center text-[11px] text-gray-400 pb-6">
                    Vigilant AI · HackIllinois 2026 · Benchmarks reflect real workloads, not synthetic tests
                </p>
            </main>
        </div>
    )
}
