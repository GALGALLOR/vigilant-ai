import { useEffect, useState, useCallback, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import {
    Eye, Upload, Video, Shield, Activity, Clock, Loader2,
    ChevronRight, Plus, X, CheckCircle2, AlertCircle, Zap, BarChart3,
    Brain, Send, Sparkles, Globe, Search
} from 'lucide-react'
import { api, type VideoInfo, type MemoryQueryResult } from '../api'

export default function HomePage() {
    const [videos, setVideos] = useState<VideoInfo[]>([])
    const [loading, setLoading] = useState(true)
    const [showUpload, setShowUpload] = useState(false)
    const navigate = useNavigate()

    const loadVideos = useCallback(() => {
        api.listVideos()
            .then(d => setVideos(d.videos || []))
            .catch(console.error)
            .finally(() => setLoading(false))
    }, [])

    useEffect(() => { loadVideos() }, [loadVideos])

    const totalEvents = videos.reduce((s, v) => s + (v.total_events || 0), 0)
    const totalAlerts = videos.reduce((s, v) => s + (v.total_alerts || 0), 0)
    const totalTime   = videos.reduce((s, v) => s + (v.processing_time_s || 0), 0)

    return (
        <div className="min-h-screen bg-gray-50 text-gray-900 relative overflow-x-hidden">
            {/* Subtle ambient */}
            <div className="fixed inset-0 pointer-events-none overflow-hidden">
                <div className="absolute -top-20 left-1/4 w-[500px] h-[400px] bg-amber-200/20 rounded-full blur-3xl" />
                <div className="absolute top-1/3 right-1/4 w-80 h-80 bg-violet-200/20 rounded-full blur-3xl" />
            </div>

            {/* Header */}
            <header className="sticky top-0 z-30 bg-white/90 backdrop-blur-xl border-b border-gray-200 shadow-sm">
                <div className="max-w-6xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="relative w-9 h-9">
                            <div className="absolute inset-0 bg-gradient-to-br from-amber-400 to-orange-500 rounded-xl blur-sm opacity-50" />
                            <div className="relative w-9 h-9 bg-gradient-to-br from-amber-400 to-orange-500 rounded-xl flex items-center justify-center">
                                <Eye className="w-5 h-5 text-white" />
                            </div>
                        </div>
                        <div>
                            <h1 className="text-lg font-bold tracking-tight bg-gradient-to-r from-amber-500 via-orange-500 to-amber-400 bg-clip-text text-transparent">Vigilant AI</h1>
                            <p className="text-[9px] text-gray-400 uppercase tracking-widest">Sentinel Stream</p>
                        </div>
                    </div>
                    <div className="flex items-center gap-2">
                        <button
                            onClick={() => navigate('/benchmarks')}
                            className="cursor-pointer flex items-center gap-1.5 px-3 py-2 text-gray-600 hover:text-gray-900 bg-white hover:bg-gray-50 border border-gray-200 rounded-xl text-xs font-medium transition-all hover:shadow-sm"
                        >
                            <BarChart3 className="w-3.5 h-3.5" /> Benchmarks
                        </button>
                        <button
                            onClick={() => setShowUpload(true)}
                            className="cursor-pointer flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-400 hover:to-orange-400 rounded-xl text-sm font-medium text-white transition-all hover:shadow-lg hover:shadow-amber-500/25 active:scale-95"
                        >
                            <Plus className="w-4 h-4" /> Upload Video
                        </button>
                    </div>
                </div>
            </header>

            <main className="max-w-6xl mx-auto px-4 sm:px-6 py-8 relative z-10 space-y-8">
                {/* Cross-Video Intelligence */}
                <GlobalMemoryChat />

                {/* Stats row */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                    <StatCard icon={Video}    label="Videos"       value={videos.length}            accent="amber"   />
                    <StatCard icon={Activity} label="Total Events" value={totalEvents}              accent="emerald" />
                    <StatCard icon={Shield}   label="Total Alerts" value={totalAlerts}              accent="red"     pulse={totalAlerts > 0} />
                    <StatCard icon={Clock}    label="GPU Seconds"  value={`${totalTime.toFixed(0)}s`} accent="violet" />
                </div>

                {/* Video list */}
                <div>
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-widest">Your Videos</h2>
                        {videos.length > 0 && (
                            <span className="text-xs text-gray-400">{videos.length} video{videos.length !== 1 ? 's' : ''}</span>
                        )}
                    </div>

                    {loading ? (
                        <div className="flex items-center justify-center py-24">
                            <div className="flex flex-col items-center gap-3">
                                <Loader2 className="w-7 h-7 animate-spin text-amber-500" />
                                <p className="text-xs text-gray-400">Loading...</p>
                            </div>
                        </div>
                    ) : videos.length === 0 ? (
                        <div className="text-center py-24 border-2 border-dashed border-gray-200 rounded-2xl bg-white">
                            <div className="w-16 h-16 mx-auto mb-4 bg-gray-100 rounded-2xl flex items-center justify-center">
                                <Video className="w-8 h-8 text-gray-300" />
                            </div>
                            <p className="text-gray-600 mb-2 font-medium">No videos yet</p>
                            <p className="text-gray-400 text-sm mb-6">Upload a video to start AI-powered analysis</p>
                            <button
                                onClick={() => setShowUpload(true)}
                                className="cursor-pointer px-6 py-2.5 bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-400 hover:to-orange-400 rounded-xl text-sm font-medium text-white transition-all hover:shadow-lg hover:shadow-amber-500/25 active:scale-95"
                            >
                                Upload your first video
                            </button>
                        </div>
                    ) : (
                        <div className="grid gap-2.5">
                            {videos.map((v, i) => (
                                <VideoCard key={v.id} video={v} index={i} onClick={() => navigate(`/video/${v.id}`)} />
                            ))}
                        </div>
                    )}
                </div>
            </main>

            {showUpload && (
                <UploadModal
                    onClose={() => setShowUpload(false)}
                    onDone={() => { setShowUpload(false); loadVideos() }}
                />
            )}

            <footer className="relative z-10 border-t border-gray-100 mt-12 py-6 text-center text-[11px] text-gray-400">
                Vigilant AI · HackIllinois 2026 · AI-Powered Video Intelligence
            </footer>
        </div>
    )
}

// ─── GlobalMemoryChat ─────────────────────────────────────────────────────────

function GlobalMemoryChat() {
    const [query, setQuery]   = useState('')
    const [loading, setLoading] = useState(false)
    const [result, setResult] = useState<MemoryQueryResult | null>(null)
    const [error, setError]   = useState('')
    const inputRef = useRef<HTMLInputElement>(null)

    const SUGGESTIONS = [
        'Any high-risk incidents detected?',
        'Were there any fights or assaults?',
        'Show me all shoplifting events',
        'Any trespassing or unauthorized access?',
    ]

    const ask = async (q: string) => {
        const trimmed = q.trim()
        if (!trimmed) return
        setQuery(trimmed); setLoading(true); setError(''); setResult(null)
        try {
            setResult(await api.queryMemory(trimmed))
        } catch (e) {
            setError(e instanceof Error ? e.message : 'Query failed')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="bg-white border border-gray-200 rounded-2xl p-5 sm:p-6 shadow-sm">
            {/* Header */}
            <div className="flex items-center gap-3 mb-4">
                <div className="relative w-9 h-9 shrink-0">
                    <div className="absolute inset-0 bg-gradient-to-br from-violet-500 to-purple-600 rounded-xl blur-sm opacity-30" />
                    <div className="relative w-9 h-9 bg-gradient-to-br from-violet-500 to-purple-600 rounded-xl flex items-center justify-center">
                        <Brain className="w-4 h-4 text-white" />
                    </div>
                </div>
                <div>
                    <h2 className="text-sm font-bold text-gray-900 flex items-center gap-1.5">
                        Cross-Video Intelligence
                        <span className="inline-flex items-center gap-1 text-[9px] px-1.5 py-0.5 bg-violet-50 text-violet-600 border border-violet-200 rounded-full font-semibold uppercase tracking-wider">
                            <Sparkles className="w-2.5 h-2.5" /> Supermemory
                        </span>
                    </h2>
                    <p className="text-[11px] text-gray-500 mt-0.5">
                        Ask anything across <em>all</em> your processed videos — patterns, incidents, repeat offenders
                    </p>
                </div>
            </div>

            {/* Search */}
            <div className="bg-white border border-gray-300 rounded-2xl shadow-sm focus-within:shadow-md focus-within:border-violet-300 transition-all">
                <div className="flex items-center gap-3 px-4 py-3">
                    <Globe className="w-4 h-4 text-gray-300 shrink-0" />
                    <input
                        ref={inputRef}
                        type="text"
                        value={query}
                        onChange={e => setQuery(e.target.value)}
                        onKeyDown={e => e.key === 'Enter' && ask(query)}
                        placeholder="e.g. 'Were there any fights across all cameras?'"
                        className="flex-1 text-sm text-gray-800 placeholder-gray-400 outline-none bg-transparent"
                    />
                    <button
                        onClick={() => ask(query)}
                        disabled={loading || !query.trim()}
                        className="cursor-pointer shrink-0 p-2 bg-violet-600 hover:bg-violet-700 disabled:bg-gray-200 rounded-xl transition-all active:scale-95 disabled:cursor-not-allowed"
                    >
                        {loading ? <Loader2 className="w-4 h-4 text-white animate-spin" /> : <Send className="w-4 h-4 text-white" />}
                    </button>
                </div>
            </div>

            {/* Suggestion chips */}
            {!result && !loading && (
                <div className="flex flex-wrap gap-1.5 mt-3">
                    {SUGGESTIONS.map(s => (
                        <button
                            key={s}
                            onClick={() => ask(s)}
                            className="cursor-pointer flex items-center gap-1 text-[11px] px-2.5 py-1 bg-gray-50 hover:bg-gray-100 border border-gray-200 text-gray-500 hover:text-gray-800 rounded-lg transition-all"
                        >
                            <Search className="w-2.5 h-2.5" /> {s}
                        </button>
                    ))}
                </div>
            )}

            {error && (
                <div className="mt-3 flex items-center gap-2 text-xs text-red-600 bg-red-50 border border-red-200 px-3 py-2 rounded-lg">
                    <AlertCircle className="w-3.5 h-3.5 shrink-0" /> {error}
                </div>
            )}

            {loading && (
                <div className="mt-4 flex items-center gap-2.5 text-sm text-gray-400">
                    <Loader2 className="w-4 h-4 animate-spin text-violet-500" />
                    <span>Searching cross-video intelligence...</span>
                </div>
            )}

            {result && !loading && (
                <div className="mt-4 animate-fade-up space-y-3">
                    <div className="bg-violet-50 border border-violet-200 rounded-xl p-4">
                        <div className="flex items-center gap-1.5 mb-2">
                            <Brain className="w-3.5 h-3.5 text-violet-600" />
                            <span className="text-[10px] text-violet-600 font-semibold uppercase tracking-wider">AI Analysis</span>
                        </div>
                        <p className="text-sm text-gray-700 leading-relaxed">
                            {result.configured
                                ? result.answer
                                : 'Supermemory is not configured. Add SUPERMEMORY_API_KEY to backend/.env'}
                        </p>
                    </div>

                    {result.memories && result.memories.length > 0 && (
                        <div className="space-y-2">
                            <p className="text-[10px] text-gray-400 uppercase tracking-wider font-semibold">
                                Matched Records ({result.memories.length})
                            </p>
                            {result.memories.slice(0, 3).map((m, i) => (
                                <div key={i} className="bg-white border border-gray-200 rounded-lg p-3 shadow-sm">
                                    <p className="text-[11px] text-gray-600 line-clamp-3">{m.content?.slice(0, 250)}...</p>
                                    {m.score != null && (
                                        <span className="text-[10px] text-gray-400 mt-1 inline-block">
                                            relevance: {(m.score * 100).toFixed(0)}%
                                        </span>
                                    )}
                                </div>
                            ))}
                        </div>
                    )}

                    <button
                        onClick={() => { setResult(null); setQuery(''); inputRef.current?.focus() }}
                        className="cursor-pointer text-[11px] text-gray-400 hover:text-gray-600 transition-colors"
                    >
                        ← Ask another question
                    </button>
                </div>
            )}
        </div>
    )
}

// ─── StatCard ─────────────────────────────────────────────────────────────────

function StatCard({ icon: Icon, label, value, accent, pulse }: {
    icon: React.ComponentType<{ className?: string }>
    label: string
    value: string | number
    accent: string
    pulse?: boolean
}) {
    const accents: Record<string, { border: string; icon: string; val: string; bg: string }> = {
        amber:   { border: 'border-amber-200',   icon: 'text-amber-500',   val: 'text-amber-600',   bg: 'bg-amber-50' },
        emerald: { border: 'border-emerald-200', icon: 'text-emerald-500', val: 'text-emerald-600', bg: 'bg-emerald-50' },
        red:     { border: 'border-red-200',     icon: 'text-red-500',     val: 'text-red-600',     bg: 'bg-red-50' },
        violet:  { border: 'border-violet-200',  icon: 'text-violet-500',  val: 'text-violet-600',  bg: 'bg-violet-50' },
    }
    const c = accents[accent] || accents.amber

    return (
        <div className={`${c.bg} border ${c.border} rounded-xl p-4 hover:shadow-md transition-all bg-white`}>
            <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-1.5">
                    <Icon className={`w-3.5 h-3.5 ${c.icon}`} />
                    <span className="text-[10px] text-gray-500 uppercase tracking-wider">{label}</span>
                </div>
                {pulse && <span className="w-2 h-2 rounded-full bg-red-400 animate-pulse" />}
            </div>
            <p className={`text-2xl font-bold ${c.val}`}>{value}</p>
        </div>
    )
}

// ─── VideoCard ────────────────────────────────────────────────────────────────

function VideoCard({ video: v, index, onClick }: { video: VideoInfo; index: number; onClick: () => void }) {
    const alertLevel = v.total_alerts > 5 ? 'high' : v.total_alerts > 0 ? 'medium' : 'none'
    const borderHover = alertLevel === 'high' ? 'hover:border-red-300' : alertLevel === 'medium' ? 'hover:border-orange-300' : 'hover:border-amber-300'

    return (
        <button
            onClick={onClick}
            className={`cursor-pointer group w-full text-left bg-white border border-gray-200 ${borderHover} hover:shadow-md rounded-xl p-4 sm:p-5 transition-all animate-fade-up`}
            style={{ animationDelay: `${index * 50}ms` }}
        >
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3 min-w-0">
                    <div className="w-10 h-10 bg-amber-50 rounded-lg flex items-center justify-center border border-amber-200 shrink-0">
                        <Video className="w-5 h-5 text-amber-500" />
                    </div>
                    <div className="min-w-0">
                        <p className="text-sm font-semibold text-gray-900 truncate group-hover:text-gray-700 transition-colors">
                            {v.name}
                        </p>
                        <p className="text-xs text-gray-400 mt-0.5">
                            {(v.duration_s / 60).toFixed(1)} min · {v.total_events} events
                        </p>
                    </div>
                </div>
                <div className="flex items-center gap-2.5 shrink-0">
                    {v.total_alerts > 0 && (
                        <span className={`flex items-center gap-1 text-xs px-2.5 py-1 rounded-lg border font-medium ${
                            alertLevel === 'high'
                                ? 'bg-red-50 text-red-600 border-red-200'
                                : 'bg-orange-50 text-orange-600 border-orange-200'
                        }`}>
                            <Shield className="w-3 h-3" /> {v.total_alerts}
                        </span>
                    )}
                    {v.gpu && (
                        <span className="hidden sm:flex items-center gap-1 text-[10px] px-2 py-1 bg-violet-50 text-violet-600 rounded-lg border border-violet-200">
                            <Zap className="w-3 h-3" /> {v.gpu}
                        </span>
                    )}
                    <ChevronRight className="w-4 h-4 text-gray-300 group-hover:text-gray-500 group-hover:translate-x-0.5 transition-all" />
                </div>
            </div>
        </button>
    )
}

// ─── UploadModal ──────────────────────────────────────────────────────────────

function UploadModal({ onClose, onDone }: { onClose: () => void; onDone: () => void }) {
    const [file, setFile] = useState<File | null>(null)
    const [dragging, setDragging] = useState(false)
    const [uploading, setUploading] = useState(false)
    const [uploadProgress, setUploadProgress] = useState(0)
    const [processingStatus, setProcessingStatus] = useState('')
    const [error, setError] = useState('')
    const [done, setDone] = useState(false)
    const fileRef = useRef<HTMLInputElement>(null)

    const handleFile = (f: File) => {
        setError('')
        if (f.size > 5120 * 1024 * 1024) { setError('File too large. Maximum size is 5GB.'); return }
        if (!f.type.startsWith('video/')) { setError('Please select a video file.'); return }
        setFile(f)
    }

    const handleUpload = async () => {
        if (!file) return
        setUploading(true); setError('')
        try {
            const res = await api.uploadVideo(file, setUploadProgress)
            setProcessingStatus('Processing video...')
            const poll = setInterval(async () => {
                try {
                    const status = await api.uploadStatus(res.video_id)
                    setProcessingStatus(
                        status.status === 'uploading'  ? 'Uploading to cloud...' :
                        status.status === 'processing' ? `Analyzing video... ${status.progress}%` :
                        status.status === 'analyzing'  ? 'AI synthesis in progress...' :
                        status.status === 'done'       ? 'Complete!' :
                        status.status === 'error'      ? `Error: ${status.error}` : 'Queued...'
                    )
                    if (status.status === 'done') {
                        clearInterval(poll); setDone(true); setTimeout(onDone, 1500)
                    } else if (status.status === 'error') {
                        clearInterval(poll); setError(status.error || 'Processing failed'); setUploading(false)
                    }
                } catch { /* keep polling */ }
            }, 2000)
        } catch (e) {
            setError(e instanceof Error ? e.message : 'Upload failed'); setUploading(false)
        }
    }

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 animate-fade-in">
            <div className="absolute inset-0 bg-black/30 backdrop-blur-sm" onClick={onClose} />
            <div className="relative bg-white rounded-2xl w-full max-w-md p-6 shadow-2xl border border-gray-200 animate-fade-up">
                <button onClick={onClose} className="cursor-pointer absolute top-4 right-4 p-1.5 text-gray-400 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-all">
                    <X className="w-4 h-4" />
                </button>

                <div className="flex items-center gap-2.5 mb-1">
                    <div className="w-7 h-7 bg-gradient-to-br from-amber-400 to-orange-500 rounded-lg flex items-center justify-center">
                        <Upload className="w-3.5 h-3.5 text-white" />
                    </div>
                    <h3 className="text-base font-semibold text-gray-900">Upload Video</h3>
                </div>
                <p className="text-xs text-gray-400 mb-5 ml-9">MP4, AVI, MOV — up to 5GB</p>

                {done ? (
                    <div className="text-center py-10">
                        <div className="w-14 h-14 bg-emerald-50 rounded-2xl flex items-center justify-center mx-auto mb-4 border border-emerald-200">
                            <CheckCircle2 className="w-7 h-7 text-emerald-500" />
                        </div>
                        <p className="text-sm text-emerald-600 font-semibold">Video processed!</p>
                        <p className="text-xs text-gray-400 mt-1">Redirecting...</p>
                    </div>
                ) : (
                    <>
                        <div
                            onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
                            onDragLeave={() => setDragging(false)}
                            onDrop={(e) => { e.preventDefault(); setDragging(false); const f = e.dataTransfer.files[0]; if (f) handleFile(f) }}
                            onClick={() => fileRef.current?.click()}
                            className={`cursor-pointer border-2 border-dashed rounded-xl p-8 text-center transition-all ${
                                dragging
                                    ? 'border-amber-400 bg-amber-50'
                                    : file
                                        ? 'border-emerald-300 bg-emerald-50'
                                        : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                            }`}
                        >
                            <input ref={fileRef} type="file" accept="video/*" className="hidden"
                                onChange={(e) => { const f = e.target.files?.[0]; if (f) handleFile(f) }} />
                            {file ? (
                                <div className="animate-fade-up">
                                    <div className="w-10 h-10 bg-emerald-100 rounded-xl flex items-center justify-center mx-auto mb-2 border border-emerald-200">
                                        <Video className="w-5 h-5 text-emerald-600" />
                                    </div>
                                    <p className="text-sm text-gray-800 font-medium">{file.name}</p>
                                    <p className="text-xs text-gray-400 mt-1">{(file.size / 1024 / 1024).toFixed(1)} MB</p>
                                </div>
                            ) : (
                                <div>
                                    <div className="w-10 h-10 bg-gray-100 rounded-xl flex items-center justify-center mx-auto mb-2">
                                        <Upload className="w-5 h-5 text-gray-400" />
                                    </div>
                                    <p className="text-sm text-gray-600">Drag & drop or click to select</p>
                                    <p className="text-xs text-gray-400 mt-1">MP4, AVI, MOV — up to 5GB</p>
                                </div>
                            )}
                        </div>

                        {error && (
                            <div className="mt-3 flex items-center gap-2 text-xs text-red-600 bg-red-50 border border-red-200 px-3 py-2 rounded-lg animate-fade-up">
                                <AlertCircle className="w-3.5 h-3.5 shrink-0" /> {error}
                            </div>
                        )}

                        {uploading && (
                            <div className="mt-4 animate-fade-up">
                                <div className="flex items-center justify-between text-xs text-gray-500 mb-1.5">
                                    <span>{processingStatus || `Uploading... ${uploadProgress}%`}</span>
                                    <Loader2 className="w-3.5 h-3.5 animate-spin text-amber-500" />
                                </div>
                                <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                                    <div
                                        className="h-full bg-gradient-to-r from-amber-400 to-orange-500 rounded-full transition-all duration-500"
                                        style={{ width: `${processingStatus ? 100 : uploadProgress}%` }}
                                    />
                                </div>
                            </div>
                        )}

                        {!uploading && (
                            <button
                                onClick={handleUpload}
                                disabled={!file}
                                className="cursor-pointer mt-4 w-full py-2.5 bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-400 hover:to-orange-400 disabled:from-gray-200 disabled:to-gray-200 disabled:text-gray-400 text-white rounded-xl text-sm font-medium transition-all hover:shadow-lg hover:shadow-amber-500/20 active:scale-[0.98] disabled:cursor-not-allowed"
                            >
                                Analyze Video
                            </button>
                        )}
                    </>
                )}
            </div>
        </div>
    )
}
