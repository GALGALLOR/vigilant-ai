import { useEffect, useState, useCallback, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import {
    Eye, Upload, Video, Shield, Activity, Clock, Loader2,
    ChevronRight, Plus, X, CheckCircle2, AlertCircle, Zap, Camera, Square, Wifi
} from 'lucide-react'
import { api, wsUrl, type VideoInfo } from '../api'

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
    const totalTime = videos.reduce((s, v) => s + (v.processing_time_s || 0), 0)

    return (
        <div className="min-h-screen bg-zinc-950 text-zinc-100 relative overflow-x-hidden">
            <div className="fixed inset-0 pointer-events-none">
                <div className="absolute top-0 left-1/4 w-96 h-96 bg-indigo-600/10 rounded-full blur-3xl" />
                <div className="absolute top-1/3 right-1/4 w-80 h-80 bg-violet-600/8 rounded-full blur-3xl" />
            </div>

            <header className="sticky top-0 z-30 bg-zinc-950/70 backdrop-blur-xl border-b border-zinc-800/50">
                <div className="max-w-6xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="relative w-9 h-9">
                            <div className="absolute inset-0 bg-gradient-to-br from-indigo-500 to-violet-600 rounded-xl blur-sm opacity-60" />
                            <div className="relative w-9 h-9 bg-gradient-to-br from-indigo-500 to-violet-600 rounded-xl flex items-center justify-center">
                                <Eye className="w-5 h-5 text-white" />
                            </div>
                        </div>
                        <div>
                            <h1 className="text-lg font-bold tracking-tight bg-gradient-to-r from-indigo-400 via-violet-400 to-purple-400 bg-clip-text text-transparent">Vigilant AI</h1>
                            <p className="text-[9px] text-zinc-500 uppercase tracking-widest">Sentinel Stream</p>
                        </div>
                    </div>
                    <button
                        onClick={() => setShowUpload(true)}
                        className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 rounded-xl text-sm font-medium transition-all hover:shadow-lg hover:shadow-indigo-500/25 active:scale-95"
                    >
                        <Plus className="w-4 h-4" /> Upload Video
                    </button>
                </div>
            </header>

            <main className="max-w-6xl mx-auto px-4 sm:px-6 py-8 relative z-10">
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-8">
                    <StatCard icon={Video} label="Videos" value={videos.length} accent="indigo" />
                    <StatCard icon={Activity} label="Total Events" value={totalEvents} accent="emerald" />
                    <StatCard icon={Shield} label="Total Alerts" value={totalAlerts} accent="red" pulse={totalAlerts > 0} />
                    <StatCard icon={Clock} label="GPU Seconds" value={`${totalTime.toFixed(0)}s`} accent="violet" />
                </div>

                <div className="grid lg:grid-cols-2 gap-4 mb-8">
                    <LiveCameraPanel />
                    <PipelinePanel />
                </div>

                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-xs font-semibold text-zinc-500 uppercase tracking-widest">Your Videos</h2>
                    {videos.length > 0 && (
                        <span className="text-xs text-zinc-600">{videos.length} video{videos.length !== 1 ? 's' : ''}</span>
                    )}
                </div>

                {loading ? (
                    <div className="flex items-center justify-center py-24">
                        <div className="flex flex-col items-center gap-3">
                            <Loader2 className="w-7 h-7 animate-spin text-indigo-500" />
                            <p className="text-xs text-zinc-600">Loading...</p>
                        </div>
                    </div>
                ) : videos.length === 0 ? (
                    <div className="text-center py-24 border border-dashed border-zinc-800 rounded-2xl">
                        <div className="w-16 h-16 mx-auto mb-4 bg-zinc-900 rounded-2xl flex items-center justify-center">
                            <Video className="w-8 h-8 text-zinc-700" />
                        </div>
                        <p className="text-zinc-500 mb-2 font-medium">No videos yet</p>
                        <p className="text-zinc-700 text-sm mb-6">Upload a video to start AI-powered analysis</p>
                        <button
                            onClick={() => setShowUpload(true)}
                            className="px-6 py-2.5 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 rounded-xl text-sm font-medium transition-all"
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
            </main>

            {showUpload && (
                <UploadModal
                    onClose={() => setShowUpload(false)}
                    onDone={() => { setShowUpload(false); loadVideos() }}
                />
            )}

            <footer className="relative z-10 border-t border-zinc-900/80 mt-12 py-6 text-center text-[11px] text-zinc-700">
                Vigilant AI · HackIllinois 2026 · AI-Powered Video Intelligence
            </footer>
        </div>
    )
}

function LiveCameraPanel() {
    const [permission, setPermission] = useState<'idle' | 'granted' | 'denied' | 'error'>('idle')
    const [recording, setRecording] = useState(false)
    const [uploading, setUploading] = useState(false)
    const [message, setMessage] = useState('')
    const [wsState, setWsState] = useState<'offline' | 'connecting' | 'connected'>('offline')
    const videoRef = useRef<HTMLVideoElement>(null)
    const streamRef = useRef<MediaStream | null>(null)
    const recorderRef = useRef<MediaRecorder | null>(null)
    const chunksRef = useRef<Blob[]>([])
    const socketRef = useRef<WebSocket | null>(null)

    const stopMedia = useCallback(() => {
        recorderRef.current?.stop()
        recorderRef.current = null
        streamRef.current?.getTracks().forEach(t => t.stop())
        streamRef.current = null
        if (videoRef.current) videoRef.current.srcObject = null
        socketRef.current?.close()
        socketRef.current = null
        setRecording(false)
        setWsState('offline')
    }, [])

    useEffect(() => stopMedia, [stopMedia])

    const requestCamera = async () => {
        setMessage('')
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true })
            streamRef.current = stream
            if (videoRef.current) videoRef.current.srcObject = stream
            setPermission('granted')
            setMessage('Camera connected. You can monitor live or send a 10s clip to Modal.')
        } catch (e) {
            setPermission('denied')
            setMessage(e instanceof Error ? e.message : 'Could not access camera.')
        }
    }

    const startLiveSend = () => {
        if (!streamRef.current || recording) return
        try {
            const socket = new WebSocket(wsUrl('/ws/stream'))
            socket.binaryType = 'arraybuffer'
            socketRef.current = socket
            setWsState('connecting')

            socket.onopen = () => setWsState('connected')
            socket.onerror = () => setWsState('offline')
            socket.onclose = () => setWsState('offline')

            const recorder = new MediaRecorder(streamRef.current, { mimeType: 'video/webm;codecs=vp8,opus' })
            recorderRef.current = recorder
            recorder.ondataavailable = async (event) => {
                if (event.data.size > 0 && socket.readyState === WebSocket.OPEN) {
                    socket.send(await event.data.arrayBuffer())
                }
            }
            recorder.start(1200)
            setRecording(true)
        } catch (e) {
            setMessage(e instanceof Error ? e.message : 'Unable to start streaming.')
        }
    }

    const sendTenSecondClip = async () => {
        if (!streamRef.current || uploading) return
        setUploading(true)
        setMessage('Recording 10s clip and uploading to Modal pipeline...')
        chunksRef.current = []

        try {
            const recorder = new MediaRecorder(streamRef.current, { mimeType: 'video/webm;codecs=vp8,opus' })
            recorder.ondataavailable = (event) => {
                if (event.data.size > 0) chunksRef.current.push(event.data)
            }

            const done = new Promise<void>((resolve) => {
                recorder.onstop = () => resolve()
            })

            recorder.start(1000)
            await new Promise(resolve => setTimeout(resolve, 10000))
            recorder.stop()
            await done

            const clipBlob = new Blob(chunksRef.current, { type: 'video/webm' })
            await api.uploadClip(clipBlob)
            setMessage('Live clip queued. Backend will chunk, infer on Modal, and ingest results.')
        } catch (e) {
            setMessage(e instanceof Error ? e.message : 'Live clip upload failed.')
        } finally {
            setUploading(false)
        }
    }

    return (
        <section className="border border-zinc-800/70 rounded-2xl bg-zinc-900/40 p-4">
            <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-semibold flex items-center gap-2"><Camera className="w-4 h-4 text-indigo-400" /> Live Camera Monitor</h3>
                <span className={`text-[10px] px-2 py-1 rounded-lg border ${wsState === 'connected' ? 'text-emerald-300 border-emerald-500/40 bg-emerald-500/10' : wsState === 'connecting' ? 'text-amber-300 border-amber-500/40 bg-amber-500/10' : 'text-zinc-500 border-zinc-700 bg-zinc-800/40'}`}>
                    <Wifi className="inline w-3 h-3 mr-1" /> {wsState}
                </span>
            </div>
            <div className="aspect-video rounded-xl bg-black/70 border border-zinc-800 overflow-hidden mb-3">
                {permission === 'granted' ? (
                    <video ref={videoRef} autoPlay playsInline muted className="w-full h-full object-cover" />
                ) : (
                    <div className="w-full h-full flex items-center justify-center text-xs text-zinc-500 px-4 text-center">
                        Click “Grant Camera Access” to open browser permission popup and enable monitoring.
                    </div>
                )}
            </div>
            <div className="flex flex-wrap gap-2">
                <button onClick={requestCamera} className="px-3 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-xs font-medium">Grant Camera Access</button>
                <button onClick={startLiveSend} disabled={permission !== 'granted' || recording} className="px-3 py-2 rounded-lg bg-violet-600 hover:bg-violet-500 disabled:bg-zinc-800 disabled:text-zinc-600 text-xs font-medium">Start Live Send</button>
                <button onClick={sendTenSecondClip} disabled={permission !== 'granted' || uploading} className="px-3 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 disabled:bg-zinc-800 disabled:text-zinc-600 text-xs font-medium">Send 10s Clip</button>
                <button onClick={stopMedia} className="px-3 py-2 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-xs font-medium flex items-center gap-1"><Square className="w-3 h-3" /> Stop</button>
            </div>
            {message && <p className="mt-3 text-xs text-zinc-400">{message}</p>}
        </section>
    )
}

function PipelinePanel() {
    return (
        <section className="border border-zinc-800/70 rounded-2xl bg-zinc-900/40 p-4">
            <h3 className="text-sm font-semibold mb-3">Modal Inference Pipeline</h3>
            <ul className="space-y-2 text-xs text-zinc-400 list-disc pl-4">
                <li><span className="text-zinc-200">Chunking:</span> 5-minute CPU chunks bound memory and I/O per task.</li>
                <li><span className="text-zinc-200">Sub-clips:</span> active windows split into ~10s clips for GPU parallelism.</li>
                <li><span className="text-zinc-200">Detection/Tracking:</span> YOLO + ByteTrack produce boxes and temporal tracks.</li>
                <li><span className="text-zinc-200">Semantics:</span> CLIP embeddings support retrieval and similarity search.</li>
                <li><span className="text-zinc-200">Narrative:</span> Gemini generates forensic descriptions over keyframes.</li>
                <li><span className="text-zinc-200">Alerts:</span> rule + model signals score Stage A/B/C with explainability.</li>
            </ul>
        </section>
    )
}

function StatCard({ icon: Icon, label, value, accent, pulse }: {
    icon: React.ComponentType<{ className?: string }>
    label: string
    value: string | number
    accent: string
    pulse?: boolean
}) {
    const accents: Record<string, { border: string; glow: string; icon: string; val: string; bg: string }> = {
        indigo: { border: 'border-indigo-500/20', glow: 'hover:shadow-indigo-500/10', icon: 'text-indigo-400', val: 'text-indigo-300', bg: 'bg-indigo-500/5' },
        emerald: { border: 'border-emerald-500/20', glow: 'hover:shadow-emerald-500/10', icon: 'text-emerald-400', val: 'text-emerald-300', bg: 'bg-emerald-500/5' },
        red: { border: 'border-red-500/20', glow: 'hover:shadow-red-500/10', icon: 'text-red-400', val: 'text-red-300', bg: 'bg-red-500/5' },
        violet: { border: 'border-violet-500/20', glow: 'hover:shadow-violet-500/10', icon: 'text-violet-400', val: 'text-violet-300', bg: 'bg-violet-500/5' },
        orange: { border: 'border-orange-500/20', glow: 'hover:shadow-orange-500/10', icon: 'text-orange-400', val: 'text-orange-300', bg: 'bg-orange-500/5' },
    }
    const c = accents[accent] || accents.indigo

    return (
        <div className={`${c.bg} border ${c.border} rounded-xl p-4 hover:shadow-lg ${c.glow} transition-all`}>
            <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-1.5">
                    <Icon className={`w-3.5 h-3.5 ${c.icon}`} />
                    <span className="text-[10px] text-zinc-500 uppercase tracking-wider">{label}</span>
                </div>
                {pulse && <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse-ring" />}
            </div>
            <p className={`text-2xl font-bold ${c.val}`}>{value}</p>
        </div>
    )
}

function VideoCard({ video: v, index, onClick }: { video: VideoInfo; index: number; onClick: () => void }) {
    const alertLevel = v.total_alerts > 5 ? 'high' : v.total_alerts > 0 ? 'medium' : 'none'
    const borderColor = alertLevel === 'high' ? 'hover:border-red-500/40' : alertLevel === 'medium' ? 'hover:border-orange-500/30' : 'hover:border-indigo-500/30'

    return (
        <button
            onClick={onClick}
            className={`group w-full text-left bg-zinc-900/70 backdrop-blur-lg border border-zinc-800/50 ${borderColor} hover:bg-zinc-800/50 rounded-xl p-4 sm:p-5 transition-all hover:shadow-lg animate-fade-up`}
            style={{ animationDelay: `${index * 50}ms` }}
        >
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3 min-w-0">
                    <div className="relative w-10 h-10 shrink-0">
                        <div className="w-10 h-10 bg-gradient-to-br from-indigo-500/20 to-violet-500/20 rounded-lg flex items-center justify-center border border-indigo-500/20">
                            <Video className="w-5 h-5 text-indigo-400" />
                        </div>
                    </div>
                    <div className="min-w-0">
                        <p className="text-sm font-semibold text-zinc-100 truncate group-hover:text-white transition-colors">{v.name}</p>
                        <p className="text-xs text-zinc-500 mt-0.5">{(v.duration_s / 60).toFixed(1)} min · {v.total_events} events</p>
                    </div>
                </div>
                <div className="flex items-center gap-2.5 shrink-0">
                    {v.total_alerts > 0 && (
                        <span className={`flex items-center gap-1 text-xs px-2.5 py-1 rounded-lg border font-medium ${
                            alertLevel === 'high'
                                ? 'bg-red-500/15 text-red-400 border-red-500/30 animate-pulse-ring-orange'
                                : 'bg-orange-500/10 text-orange-400 border-orange-500/20'
                        }`}>
                            <Shield className="w-3 h-3" /> {v.total_alerts}
                        </span>
                    )}
                    {v.gpu && (
                        <span className="hidden sm:flex items-center gap-1 text-[10px] px-2 py-1 bg-violet-500/8 text-violet-500 rounded-lg border border-violet-500/15">
                            <Zap className="w-3 h-3" /> {v.gpu}
                        </span>
                    )}
                    <ChevronRight className="w-4 h-4 text-zinc-600 group-hover:text-zinc-300 group-hover:translate-x-0.5 transition-all" />
                </div>
            </div>
        </button>
    )
}

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
        if (f.size > 5120 * 1024 * 1024) {
            setError('File too large. Maximum size is 5GB.')
            return
        }
        if (!f.type.startsWith('video/')) {
            setError('Please select a video file.')
            return
        }
        setFile(f)
    }

    const handleUpload = async () => {
        if (!file) return
        setUploading(true)
        setError('')
        try {
            const res = await api.uploadVideo(file, setUploadProgress)
            setProcessingStatus('Processing video...')

            const poll = setInterval(async () => {
                try {
                    const status = await api.uploadStatus(res.video_id)
                    setProcessingStatus(
                        status.status === 'uploading' ? 'Uploading to cloud...' :
                            status.status === 'processing' ? `Analyzing video... ${status.progress}%` :
                                status.status === 'analyzing' ? 'AI synthesis in progress...' :
                                    status.status === 'done' ? 'Complete!' :
                                        status.status === 'error' ? `Error: ${status.error}` :
                                            'Queued...'
                    )
                    if (status.status === 'done') {
                        clearInterval(poll)
                        setDone(true)
                        setTimeout(onDone, 1500)
                    } else if (status.status === 'error') {
                        clearInterval(poll)
                        setError(status.error || 'Processing failed')
                        setUploading(false)
                    }
                } catch { }
            }, 2000)
        } catch (e) {
            setError(e instanceof Error ? e.message : 'Upload failed')
            setUploading(false)
        }
    }

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 animate-fade-in">
            <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" onClick={onClose} />
            <div className="relative bg-zinc-900/70 backdrop-blur-lg border border-zinc-800/50 rounded-2xl w-full max-w-md p-6 shadow-2xl shadow-black/50 animate-fade-up">
                <button onClick={onClose} className="absolute top-4 right-4 p-1.5 text-zinc-500 hover:text-zinc-200 hover:bg-zinc-800 rounded-lg transition-all">
                    <X className="w-4 h-4" />
                </button>

                <div className="flex items-center gap-2.5 mb-1">
                    <div className="w-7 h-7 bg-gradient-to-br from-indigo-500 to-violet-600 rounded-lg flex items-center justify-center">
                        <Upload className="w-3.5 h-3.5 text-white" />
                    </div>
                    <h3 className="text-base font-semibold">Upload Video</h3>
                </div>
                <p className="text-xs text-zinc-500 mb-5 ml-9">MP4, AVI, MOV — up to 5GB</p>

                {done ? (
                    <div className="text-center py-10">
                        <div className="w-14 h-14 bg-emerald-500/15 rounded-2xl flex items-center justify-center mx-auto mb-4">
                            <CheckCircle2 className="w-7 h-7 text-emerald-400" />
                        </div>
                        <p className="text-sm text-emerald-400 font-semibold">Video processed!</p>
                        <p className="text-xs text-zinc-600 mt-1">Redirecting...</p>
                    </div>
                ) : (
                    <>
                        <div
                            onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
                            onDragLeave={() => setDragging(false)}
                            onDrop={(e) => {
                                e.preventDefault(); setDragging(false)
                                const f = e.dataTransfer.files[0]
                                if (f) handleFile(f)
                            }}
                            onClick={() => fileRef.current?.click()}
                            className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all ${
                                dragging
                                    ? 'border-indigo-500 bg-indigo-500/8 shadow-lg shadow-indigo-500/10'
                                    : file
                                        ? 'border-emerald-500/40 bg-emerald-500/5'
                                        : 'border-zinc-700/60 hover:border-zinc-600 hover:bg-zinc-800/30'
                                }`}
                        >
                            <input
                                ref={fileRef}
                                type="file"
                                accept="video/*"
                                className="hidden"
                                onChange={(e) => { const f = e.target.files?.[0]; if (f) handleFile(f) }}
                            />
                            {file ? (
                                <div className="animate-fade-up">
                                    <div className="w-10 h-10 bg-emerald-500/15 rounded-xl flex items-center justify-center mx-auto mb-2">
                                        <Video className="w-5 h-5 text-emerald-400" />
                                    </div>
                                    <p className="text-sm text-zinc-200 font-medium">{file.name}</p>
                                    <p className="text-xs text-zinc-500 mt-1">{(file.size / 1024 / 1024).toFixed(1)} MB</p>
                                </div>
                            ) : (
                                <div>
                                    <div className="w-10 h-10 bg-zinc-800 rounded-xl flex items-center justify-center mx-auto mb-2">
                                        <Upload className="w-5 h-5 text-zinc-500" />
                                    </div>
                                    <p className="text-sm text-zinc-400">Drag & drop or click to select</p>
                                    <p className="text-xs text-zinc-600 mt-1">MP4, AVI, MOV — up to 5GB</p>
                                </div>
                            )}
                        </div>

                        {error && (
                            <div className="mt-3 flex items-center gap-2 text-xs text-red-400 bg-red-500/8 border border-red-500/20 px-3 py-2 rounded-lg animate-fade-up">
                                <AlertCircle className="w-3.5 h-3.5 shrink-0" /> {error}
                            </div>
                        )}

                        {uploading && (
                            <div className="mt-4 animate-fade-up">
                                <div className="flex items-center justify-between text-xs text-zinc-400 mb-1.5">
                                    <span>{processingStatus || `Uploading... ${uploadProgress}%`}</span>
                                    <Loader2 className="w-3.5 h-3.5 animate-spin text-indigo-400" />
                                </div>
                                <div className="h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                                    <div
                                        className="h-full bg-gradient-to-r from-indigo-500 to-violet-500 rounded-full transition-all duration-500"
                                        style={{ width: `${processingStatus ? 100 : uploadProgress}%` }}
                                    />
                                </div>
                            </div>
                        )}

                        {!uploading && (
                            <button
                                onClick={handleUpload}
                                disabled={!file}
                                className="mt-4 w-full py-2.5 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 disabled:from-zinc-800 disabled:to-zinc-800 disabled:text-zinc-600 rounded-xl text-sm font-medium transition-all hover:shadow-lg hover:shadow-indigo-500/20 active:scale-[0.98]"
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
