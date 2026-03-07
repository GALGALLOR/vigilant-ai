import { useEffect, useState, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
    ArrowLeft, Shield, Clock, Users, Zap, Send, Search, Loader2,
    AlertTriangle, ChevronDown, ChevronUp, Activity, Eye, BarChart3,
    Tag, Brain, Cpu, Server, Download, Globe, FileText
} from 'lucide-react'
import { api, ev, type EventData, type VideoSummary, type InsightsData, type VideoInfo } from '../api'

function fmt(s: number) { const m = Math.floor(s / 60); return `${m}:${Math.floor(s % 60).toString().padStart(2, '0')}` }

function stageColor(s: string) {
    if (s === 'C') return 'bg-red-50 text-red-600 border-red-200'
    if (s === 'B') return 'bg-orange-50 text-orange-600 border-orange-200'
    if (s === 'A') return 'bg-amber-50 text-amber-600 border-amber-200'
    return 'bg-gray-100 text-gray-500 border-gray-200'
}
function stageGlow(s: string) {
    if (s === 'C') return 'shadow-md animate-pulse-ring'
    if (s === 'B') return 'shadow-sm'
    return ''
}
function labelColor(l: string) {
    if (l.includes('altercation') || l.includes('weapon') || l.includes('assault')) return 'text-red-600'
    if (l.includes('confrontation') || l.includes('aggressive') || l.includes('fight')) return 'text-orange-600'
    if (l.includes('trespassing') || l.includes('shoplifting') || l.includes('theft') || l.includes('steal')) return 'text-amber-600'
    return 'text-gray-800'
}
function riskBadge(r: string) {
    if (r === 'high')   return 'bg-red-50 text-red-600 border-red-200'
    if (r === 'medium') return 'bg-amber-50 text-amber-600 border-amber-200'
    return 'bg-green-50 text-green-600 border-green-200'
}
function riskAccent(r: string) {
    if (r === 'high')   return '#ef4444'
    if (r === 'medium') return '#f59e0b'
    return '#22c55e'
}

export default function VideoPage() {
    const { videoId } = useParams<{ videoId: string }>()
    const navigate = useNavigate()
    const [alerts, setAlerts]       = useState<EventData[]>([])
    const [events, setEvents]       = useState<EventData[]>([])
    const [summary, setSummary]     = useState<VideoSummary | null>(null)
    const [videoInfo, setVideoInfo] = useState<VideoInfo | null>(null)
    const [loading, setLoading]     = useState(true)
    const [tab, setTab]             = useState<'chat' | 'alerts' | 'events' | 'insights' | 'memory'>('chat')
    const [reportLoading, setReportLoading] = useState(false)
    const [pdfLoading, setPdfLoading] = useState(false)

    useEffect(() => {
        if (!videoId) return
        Promise.all([
            api.videoAlerts(videoId).then(d => setAlerts(d.alerts || [])),
            api.videoEvents(videoId).then(d => setEvents(d.events || [])),
            api.videoSummary(videoId).then(d => { if (d && 'summary' in d && d.summary) setSummary(d as VideoSummary) }),
            api.videoInfo(videoId).then(setVideoInfo).catch(() => null),
        ])
            .catch(console.error)
            .finally(() => setLoading(false))
    }, [videoId])

    if (!videoId) return null
    const videoName = events[0]?.video_source || alerts[0]?.video_source || videoId

    return (
        <div className="min-h-screen bg-gray-50 text-gray-900 flex flex-col">
            {/* Subtle ambient tint */}
            <div className="fixed inset-0 pointer-events-none overflow-hidden">
                <div className="absolute -top-20 right-1/4 w-96 h-96 bg-indigo-200/30 rounded-full blur-3xl" />
                {summary?.risk_level === 'high' && (
                    <div className="absolute bottom-1/4 left-1/4 w-64 h-64 bg-red-200/25 rounded-full blur-3xl" />
                )}
            </div>

            {/* Header */}
            <header className="sticky top-0 z-30 bg-white/90 backdrop-blur-xl border-b border-gray-200 shadow-sm">
                <div className="max-w-5xl mx-auto px-4 sm:px-6 py-3 flex items-center gap-3">
                    <button
                        onClick={() => navigate('/')}
                        className="cursor-pointer p-1.5 hover:bg-gray-100 rounded-lg transition-all text-gray-500 hover:text-gray-800"
                    >
                        <ArrowLeft className="w-5 h-5" />
                    </button>
                    <div className="flex items-center gap-2.5 min-w-0 flex-1">
                        <div className="relative w-8 h-8 shrink-0">
                            <div className="absolute inset-0 bg-gradient-to-br from-indigo-500 to-violet-600 rounded-lg blur-sm opacity-40" />
                            <div className="relative w-8 h-8 bg-gradient-to-br from-indigo-500 to-violet-600 rounded-lg flex items-center justify-center">
                                <Eye className="w-4 h-4 text-white" />
                            </div>
                        </div>
                        <div className="min-w-0">
                            <h1 className="text-sm font-semibold truncate text-gray-900">{videoName}</h1>
                            <p className="text-[10px] text-gray-400">{events.length} events · {alerts.length} alerts</p>
                        </div>
                    </div>
                    {alerts.length > 0 && (
                        <span className={`shrink-0 flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-lg border font-medium ${
                            alerts.some(a => a.alert?.stage === 'C')
                                ? 'bg-red-50 text-red-600 border-red-200 animate-pulse-ring'
                                : 'bg-orange-50 text-orange-600 border-orange-200'
                        }`}>
                            <Shield className="w-3 h-3" /> {alerts.length}
                        </span>
                    )}
                    <button
                        title="Download TXT report"
                        disabled={reportLoading || events.length === 0}
                        onClick={async () => {
                            setReportLoading(true)
                            try {
                                const res = await fetch(api.videoReportTextUrl(videoId))
                                if (!res.ok) throw new Error(`HTTP ${res.status}`)
                                const blob = await res.blob()
                                const blobUrl = URL.createObjectURL(blob)
                                const a = document.createElement('a')
                                a.href = blobUrl; a.download = `report_${videoId}.txt`
                                document.body.appendChild(a); a.click(); document.body.removeChild(a)
                                URL.revokeObjectURL(blobUrl)
                            } finally { setReportLoading(false) }
                        }}
                        className="cursor-pointer shrink-0 flex items-center gap-1 px-2.5 py-1.5 text-[10px] font-medium text-gray-600 hover:text-gray-900 bg-white hover:bg-gray-50 border border-gray-200 rounded-lg transition-all disabled:opacity-30 disabled:cursor-not-allowed"
                    >
                        {reportLoading ? <Loader2 className="w-3 h-3 animate-spin" /> : <FileText className="w-3 h-3" />}
                        TXT
                    </button>
                    <button
                        title="Download PDF report"
                        disabled={pdfLoading || events.length === 0}
                        onClick={async () => {
                            setPdfLoading(true)
                            try {
                                const res = await fetch(api.videoReportPdfUrl(videoId))
                                if (!res.ok) throw new Error(`HTTP ${res.status}`)
                                const blob = await res.blob()
                                const blobUrl = URL.createObjectURL(blob)
                                const a = document.createElement('a')
                                a.href = blobUrl; a.download = `report_${videoId}.pdf`
                                document.body.appendChild(a); a.click(); document.body.removeChild(a)
                                URL.revokeObjectURL(blobUrl)
                            } finally { setPdfLoading(false) }
                        }}
                        className="cursor-pointer shrink-0 flex items-center gap-1 px-2.5 py-1.5 text-[10px] font-medium text-indigo-600 hover:text-indigo-700 bg-indigo-50 hover:bg-indigo-100 border border-indigo-200 rounded-lg transition-all disabled:opacity-30 disabled:cursor-not-allowed"
                    >
                        {pdfLoading ? <Loader2 className="w-3 h-3 animate-spin" /> : <Download className="w-3 h-3" />}
                        PDF
                    </button>
                </div>
            </header>

            {/* Summary Card */}
            {summary && (
                <div className="max-w-5xl mx-auto px-4 sm:px-6 py-4 w-full animate-fade-up">
                    <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm"
                         style={{ borderLeft: `4px solid ${riskAccent(summary.risk_level)}` }}>
                        <div className="flex items-center gap-2 mb-3">
                            <Brain className="w-4 h-4 text-indigo-600" />
                            <span className="text-xs font-semibold text-indigo-600 uppercase tracking-wider">AI Analysis</span>
                            <span className={`text-[10px] px-2.5 py-0.5 rounded-full border font-bold ml-auto ${riskBadge(summary.risk_level)} ${summary.risk_level === 'high' ? 'animate-pulse-ring' : ''}`}>
                                {summary.risk_level.toUpperCase()} RISK
                            </span>
                        </div>
                        <p className="text-sm text-gray-700 leading-relaxed mb-3">{summary.summary}</p>
                        <div className="flex flex-wrap gap-1.5 mb-1">
                            {summary.intent.map(i => (
                                <span key={i} className="text-[10px] px-2 py-0.5 bg-indigo-50 text-indigo-600 rounded-full border border-indigo-200 font-medium">
                                    {i.replace(/_/g, ' ')}
                                </span>
                            ))}
                            {summary.tags.slice(0, 5).map(t => (
                                <span key={t} className="text-[10px] px-2 py-0.5 bg-gray-100 text-gray-500 rounded-full border border-gray-200">
                                    {t}
                                </span>
                            ))}
                        </div>
                        {summary.key_moments.length > 0 && (
                            <div className="mt-3 border-t border-gray-100 pt-3">
                                <p className="text-[10px] text-gray-400 font-semibold uppercase tracking-wider mb-3">Key Moments</p>
                                <div className="relative pl-5">
                                    <div className="absolute left-1.5 top-1 bottom-1 w-px bg-gradient-to-b from-indigo-400/60 via-indigo-300/30 to-transparent" />
                                    <div className="space-y-3">
                                        {summary.key_moments.map((km, i) => (
                                            <div key={i} className="flex items-start gap-3 relative">
                                                <div className="absolute -left-[15px] top-1 w-2.5 h-2.5 rounded-full bg-indigo-500 border-2 border-white shrink-0 shadow-sm" />
                                                <span className="text-indigo-600 font-mono text-xs shrink-0 pt-px">{km.time}</span>
                                                <span className="text-gray-600 text-xs leading-relaxed">{km.description}</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* Processing Stats chips */}
            {videoInfo && ((videoInfo.chunks ?? 0) > 0 || (videoInfo.gpu_time_s ?? 0) > 0) && (
                <div className="max-w-5xl mx-auto px-4 sm:px-6 pb-3 w-full">
                    <div className="flex flex-wrap gap-2">
                        {videoInfo.gpu && <StatChip icon={<Server className="w-3 h-3" />} label={videoInfo.gpu} color="violet" />}
                        {(videoInfo.chunks ?? 0) > 0 && <StatChip icon={<Cpu className="w-3 h-3" />} label={`${videoInfo.chunks} chunks · ${videoInfo.subclips} subclips`} color="gray" />}
                        {(videoInfo.cpu_time_s ?? 0) > 0 && <StatChip icon={null} label={`CPU ${videoInfo.cpu_time_s?.toFixed(0)}s`} color="gray" />}
                        {(videoInfo.gpu_time_s ?? 0) > 0 && <StatChip icon={<Zap className="w-3 h-3" />} label={`GPU ${videoInfo.gpu_time_s?.toFixed(0)}s`} color="violet" />}
                        {(videoInfo.processing_time_s ?? 0) > 0 && <StatChip icon={<Clock className="w-3 h-3" />} label={`Total ${videoInfo.processing_time_s?.toFixed(0)}s`} color="gray" />}
                    </div>
                </div>
            )}

            {/* Tabs */}
            <div className="border-b border-gray-200 bg-white sticky top-[57px] z-20">
                <div className="max-w-5xl mx-auto px-4 sm:px-6 flex gap-1">
                    {(['chat', 'alerts', 'events', 'insights', 'memory'] as const).map(t => (
                        <button
                            key={t}
                            onClick={() => setTab(t)}
                            className={`cursor-pointer px-4 py-2.5 text-xs font-medium transition-all border-b-2 capitalize ${
                                tab === t
                                    ? 'text-indigo-600 border-indigo-600'
                                    : 'text-gray-500 border-transparent hover:text-gray-700 hover:border-gray-300'
                            }`}
                        >
                            {t === 'alerts'   ? `Alerts (${alerts.length})` :
                             t === 'events'   ? `Events (${events.length})` :
                             t === 'insights' ? 'Insights' :
                             t === 'memory'   ? 'Memory' : 'Chat'}
                        </button>
                    ))}
                </div>
            </div>

            {/* Tab content */}
            <div className="flex-1 overflow-hidden relative z-10">
                {loading ? (
                    <div className="flex flex-col items-center justify-center py-24 gap-3">
                        <Loader2 className="w-7 h-7 animate-spin text-indigo-500" />
                        <p className="text-xs text-gray-400">Loading analysis...</p>
                    </div>
                ) : tab === 'chat' ? (
                    <ChatPanel videoId={videoId} />
                ) : tab === 'alerts' ? (
                    <CardList items={alerts} emptyIcon={Shield} emptyText="No alerts detected" />
                ) : tab === 'insights' ? (
                    <InsightsPanel videoId={videoId} />
                ) : tab === 'memory' ? (
                    <MemoryPanel videoId={videoId} />
                ) : (
                    <CardList items={events} emptyIcon={Activity} emptyText="No events" />
                )}
            </div>
        </div>
    )
}

// ─── StatChip ─────────────────────────────────────────────────────────────────

function StatChip({ icon, label, color }: { icon: React.ReactNode; label: string; color: 'violet' | 'gray' }) {
    const cls = color === 'violet'
        ? 'bg-violet-50 text-violet-600 border-violet-200'
        : 'bg-gray-100 text-gray-500 border-gray-200'
    return (
        <span className={`flex items-center gap-1.5 text-[10px] px-2.5 py-1 ${cls} border rounded-lg font-medium`}>
            {icon}{label}
        </span>
    )
}

// ─── CardList ────────────────────────────────────────────────────────────────

function CardList({ items, emptyIcon: Icon, emptyText }: {
    items: EventData[]
    emptyIcon: React.ComponentType<{ className?: string }>
    emptyText: string
}) {
    const [expanded, setExpanded] = useState<string | null>(null)

    if (items.length === 0) return (
        <div className="text-center py-24 text-gray-400">
            <div className="w-14 h-14 bg-gray-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <Icon className="w-7 h-7 opacity-40" />
            </div>
            <p className="text-sm">{emptyText}</p>
        </div>
    )

    return (
        <div className="max-w-3xl mx-auto px-4 sm:px-6 py-6 space-y-2">
            {items.map((raw, idx) => {
                const e = ev(raw)
                const isOpen = expanded === e.clipId
                const isStageC = e.alertStage === 'C'

                return (
                    <button
                        key={e.clipId}
                        onClick={() => setExpanded(isOpen ? null : e.clipId)}
                        className={`cursor-pointer w-full text-left bg-white border rounded-xl p-4 transition-all animate-fade-up hover:shadow-md ${
                            isStageC
                                ? 'border-red-200 hover:border-red-300'
                                : 'border-gray-200 hover:border-gray-300'
                        } ${stageGlow(e.alertStage)}`}
                        style={{ animationDelay: `${idx * 30}ms` }}
                    >
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2 min-w-0">
                                {e.alertStage !== 'none' && (
                                    <span className={`text-[10px] px-1.5 py-0.5 rounded-md border font-bold shrink-0 ${stageColor(e.alertStage)}`}>
                                        {e.alertStage}
                                    </span>
                                )}
                                <span className={`text-sm font-medium truncate ${labelColor(e.label)}`}>
                                    {e.label.replace(/_/g, ' ')}
                                </span>
                            </div>
                            <div className="flex items-center gap-2 shrink-0">
                                {e.alertScore > 0 && (
                                    <span className={`text-xs font-mono font-semibold ${
                                        e.alertScore > 0.7 ? 'text-red-500' : e.alertScore > 0.4 ? 'text-orange-500' : 'text-gray-400'
                                    }`}>{e.alertScore.toFixed(2)}</span>
                                )}
                                {isOpen ? <ChevronUp className="w-3.5 h-3.5 text-gray-400" /> : <ChevronDown className="w-3.5 h-3.5 text-gray-300" />}
                            </div>
                        </div>
                        <div className="flex items-center gap-3 mt-1.5 text-xs text-gray-400">
                            <span className="flex items-center gap-1"><Clock className="w-3 h-3" /> {fmt(e.start)}–{fmt(e.end)}</span>
                            <span className="flex items-center gap-1"><Users className="w-3 h-3" /> {e.people}</span>
                            {e.peakMotion > 0 && (
                                <span className="flex items-center gap-1"><Zap className="w-3 h-3" /> {e.peakMotion.toFixed(2)}</span>
                            )}
                        </div>
                        {isOpen && e.caption && (
                            <p className="mt-3 text-xs text-gray-600 leading-relaxed border-t border-gray-100 pt-3 animate-fade-up">
                                {e.caption}
                            </p>
                        )}
                    </button>
                )
            })}
        </div>
    )
}

// ─── ChatPanel — ChatGPT style ────────────────────────────────────────────────

interface LocalMsg {
    id: string
    role: 'user' | 'assistant'
    text: string
    results?: EventData[]
    loading?: boolean
    streaming?: boolean
}

function ChatPanel({ videoId }: { videoId: string }) {
    const [messages, setMessages] = useState<LocalMsg[]>([])
    const [input, setInput]       = useState('')
    const [searching, setSearching] = useState(false)
    const bottomRef = useRef<HTMLDivElement>(null)

    useEffect(() => {
        api.chatHistory(videoId).then(data => {
            if (data.messages.length > 0) {
                setMessages(data.messages.map((m, i) => ({
                    id: `h-${m.id || i}`, role: m.role, text: m.content,
                })))
            } else {
                setMessages([{
                    id: 'init', role: 'assistant',
                    text: 'Ask me anything about this video. I\'ll search the footage and give you specific answers with timestamps.\n\nTry: "What happened?", "Any theft or fighting?", "Who was involved?"',
                }])
            }
        }).catch(() => {
            setMessages([{ id: 'init', role: 'assistant', text: 'Ask me anything about this video.' }])
        })
    }, [videoId])

    useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

    const handleSend = async () => {
        const q = input.trim()
        if (!q || searching) return

        const userMsg: LocalMsg = { id: `u-${Date.now()}`, role: 'user', text: q }
        const loadId = `a-${Date.now()}`
        setMessages(prev => [...prev, userMsg, { id: loadId, role: 'assistant', text: '', loading: true }])
        setInput('')
        setSearching(true)

        try {
            const stream = api.chatStream(q, videoId, 8,
                (_count, results) => {
                    setMessages(prev => prev.map(m => m.id === loadId
                        ? { ...m, loading: false, streaming: true, results, text: m.text }
                        : m
                    ))
                }
            )
            const reader = stream.getReader()
            let fullText = ''
            while (true) {
                const { done, value } = await reader.read()
                if (done) break
                fullText += value
                setMessages(prev => prev.map(m => m.id === loadId
                    ? { ...m, loading: false, streaming: true, text: fullText }
                    : m
                ))
            }
            setMessages(prev => prev.map(m => m.id === loadId
                ? { ...m, streaming: false, text: fullText || 'Nothing found.' }
                : m
            ))
        } catch {
            setMessages(prev => prev.map(m => m.id === loadId
                ? { ...m, loading: false, streaming: false, text: 'Search failed. Try again.' }
                : m
            ))
        } finally {
            setSearching(false)
        }
    }

    return (
        <div className="flex flex-col h-[calc(100vh-220px)] bg-gray-50">
            {/* Messages */}
            <div className="flex-1 overflow-y-auto py-6">
                <div className="max-w-2xl mx-auto px-4 space-y-6">
                    {messages.map((msg) => (
                        msg.role === 'user' ? (
                            /* User message — right-aligned bubble */
                            <div key={msg.id} className="flex justify-end animate-fade-up">
                                <div className="max-w-[80%] bg-indigo-600 text-white rounded-2xl rounded-br-md px-4 py-3 shadow-sm">
                                    <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.text}</p>
                                </div>
                            </div>
                        ) : (
                            /* AI message — left-aligned, no bubble, with icon */
                            <div key={msg.id} className="flex gap-3 animate-fade-up">
                                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center shrink-0 mt-0.5 shadow-sm">
                                    <Brain className="w-4 h-4 text-white" />
                                </div>
                                <div className="flex-1 min-w-0 pt-1">
                                    {msg.loading ? (
                                        <div className="flex items-center gap-1.5 pt-1">
                                            <span className="w-2 h-2 bg-gray-300 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                                            <span className="w-2 h-2 bg-gray-300 rounded-full animate-bounce" style={{ animationDelay: '160ms' }} />
                                            <span className="w-2 h-2 bg-gray-300 rounded-full animate-bounce" style={{ animationDelay: '320ms' }} />
                                        </div>
                                    ) : (
                                        <p className="text-sm text-gray-800 leading-relaxed whitespace-pre-wrap">
                                            {msg.text}
                                            {msg.streaming && (
                                                <span className="inline-block w-0.5 h-4 bg-indigo-500 ml-0.5 animate-blink-cursor align-middle" />
                                            )}
                                        </p>
                                    )}

                                    {/* Matching clips */}
                                    {msg.results && msg.results.length > 0 && (
                                        <div className="mt-3 space-y-2 animate-fade-up">
                                            <p className="text-[10px] text-gray-400 font-semibold uppercase tracking-wider">
                                                {msg.results.length} matching clip{msg.results.length !== 1 ? 's' : ''}
                                            </p>
                                            {msg.results.slice(0, 5).map((raw, i) => {
                                                const e = ev(raw)
                                                return (
                                                    <div
                                                        key={e.clipId || i}
                                                        className="bg-white border border-gray-200 rounded-xl p-3 text-xs shadow-sm animate-fade-up"
                                                        style={{ animationDelay: `${i * 60}ms` }}
                                                    >
                                                        <div className="flex items-center gap-2">
                                                            <span className="text-gray-300 font-mono">#{i + 1}</span>
                                                            <span className={`font-semibold ${labelColor(e.label)}`}>
                                                                {e.label.replace(/_/g, ' ')}
                                                            </span>
                                                            {e.alertStage !== 'none' && (
                                                                <span className={`text-[9px] px-1.5 py-0.5 rounded-md border font-bold ${stageColor(e.alertStage)}`}>
                                                                    {e.alertStage}
                                                                </span>
                                                            )}
                                                            <span className="text-gray-300 ml-auto font-mono">{fmt(e.start)}–{fmt(e.end)}</span>
                                                        </div>
                                                        {e.caption && (
                                                            <p className="text-gray-500 mt-1.5 line-clamp-2 leading-relaxed">{e.caption}</p>
                                                        )}
                                                    </div>
                                                )
                                            })}
                                        </div>
                                    )}
                                </div>
                            </div>
                        )
                    ))}
                    <div ref={bottomRef} />
                </div>
            </div>

            {/* Input bar — ChatGPT style */}
            <div className="bg-gray-50 border-t border-gray-200 px-4 py-4">
                <div className="max-w-2xl mx-auto">
                    <div className="bg-white border border-gray-300 rounded-2xl shadow-sm focus-within:shadow-md focus-within:border-indigo-300 transition-all">
                        <div className="flex items-center gap-3 px-4 py-3">
                            <Search className="w-4 h-4 text-gray-300 shrink-0" />
                            <input
                                type="text"
                                value={input}
                                onChange={e => setInput(e.target.value)}
                                onKeyDown={e => e.key === 'Enter' && handleSend()}
                                placeholder="Ask about this video..."
                                disabled={searching}
                                className="flex-1 text-sm text-gray-800 placeholder-gray-400 outline-none bg-transparent disabled:opacity-50"
                            />
                            <button
                                onClick={handleSend}
                                disabled={searching || !input.trim()}
                                className="cursor-pointer shrink-0 p-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-200 rounded-xl transition-all active:scale-95 disabled:cursor-not-allowed"
                            >
                                {searching
                                    ? <Loader2 className="w-4 h-4 text-white animate-spin" />
                                    : <Send className="w-4 h-4 text-white disabled:text-gray-400" />
                                }
                            </button>
                        </div>
                    </div>
                    <p className="text-center text-[10px] text-gray-400 mt-2">
                        CLIP semantic search + Gemini synthesis
                    </p>
                </div>
            </div>
        </div>
    )
}

// ─── MemoryPanel ──────────────────────────────────────────────────────────────

function MemoryPanel({ videoId }: { videoId: string }) {
    const [query, setQuery]   = useState('')
    const [loading, setLoading] = useState(false)
    const [scoped, setScoped] = useState(false)
    const [result, setResult] = useState<{ answer: string; memories: Array<{ content: string; score: number; metadata: Record<string, unknown> }>; configured: boolean } | null>(null)
    const [error, setError]   = useState<string | null>(null)

    const handleQuery = async () => {
        const q = query.trim()
        if (!q || loading) return
        setLoading(true); setError(null); setResult(null)
        try {
            setResult(await api.queryMemory(q, scoped ? videoId : undefined))
        } catch (e) {
            setError(String(e))
        } finally {
            setLoading(false)
        }
    }

    const suggestions = [
        'Any prior incidents involving assault?',
        'Have similar fights been detected before?',
        'Show all high-risk incidents',
        'Shoplifting near an entrance?',
    ]

    return (
        <div className="max-w-3xl mx-auto px-4 sm:px-6 py-6 space-y-4">
            <div className="bg-white border border-gray-200 rounded-xl p-4 flex gap-3 shadow-sm">
                <Globe className="w-5 h-5 text-indigo-500 shrink-0 mt-0.5" />
                <div>
                    <p className="text-sm font-semibold text-gray-800 mb-1">Cross-Video Intelligence</p>
                    <p className="text-xs text-gray-500 leading-relaxed">
                        Query persistent memory across <span className="text-gray-700 font-medium">all</span> processed videos — find patterns across time, locations, and incidents.
                    </p>
                </div>
            </div>

            <div className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm space-y-3">
                <div className="flex items-center justify-between">
                    <p className="text-[10px] text-gray-400 uppercase tracking-wider font-semibold">Query</p>
                    <label className="flex items-center gap-1.5 text-xs text-gray-500 cursor-pointer select-none">
                        <input type="checkbox" checked={scoped} onChange={e => setScoped(e.target.checked)} className="w-3 h-3 accent-indigo-500" />
                        This video only
                    </label>
                </div>
                <div className="bg-white border border-gray-300 rounded-2xl shadow-sm focus-within:shadow-md focus-within:border-indigo-300 transition-all">
                    <div className="flex items-center gap-3 px-4 py-3">
                        <Search className="w-4 h-4 text-gray-300 shrink-0" />
                        <input
                            type="text"
                            value={query}
                            onChange={e => setQuery(e.target.value)}
                            onKeyDown={e => e.key === 'Enter' && handleQuery()}
                            placeholder="e.g. Has anyone been assaulted in this area before?"
                            className="flex-1 text-sm text-gray-800 placeholder-gray-400 outline-none bg-transparent"
                        />
                        <button
                            onClick={handleQuery}
                            disabled={loading || !query.trim()}
                            className="cursor-pointer shrink-0 p-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-200 rounded-xl transition-all active:scale-95 disabled:cursor-not-allowed"
                        >
                            {loading ? <Loader2 className="w-4 h-4 text-white animate-spin" /> : <Search className="w-4 h-4 text-white" />}
                        </button>
                    </div>
                </div>
                {!result && !loading && (
                    <div className="flex flex-wrap gap-1.5">
                        {suggestions.map(s => (
                            <button key={s} onClick={() => setQuery(s)}
                                className="cursor-pointer text-[10px] px-2.5 py-1 bg-gray-50 text-gray-500 hover:text-gray-800 hover:bg-gray-100 border border-gray-200 rounded-lg transition-all">
                                {s}
                            </button>
                        ))}
                    </div>
                )}
            </div>

            {loading && (
                <div className="flex items-center justify-center gap-2.5 py-8 text-gray-400 text-sm">
                    <div className="flex gap-1">
                        <span className="w-2 h-2 bg-gray-300 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                        <span className="w-2 h-2 bg-gray-300 rounded-full animate-bounce" style={{ animationDelay: '160ms' }} />
                        <span className="w-2 h-2 bg-gray-300 rounded-full animate-bounce" style={{ animationDelay: '320ms' }} />
                    </div>
                    Searching memory…
                </div>
            )}
            {error && <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-600">{error}</div>}
            {result && !result.configured && (
                <div className="bg-white border border-gray-200 rounded-xl p-5 text-center space-y-2 shadow-sm">
                    <Globe className="w-8 h-8 text-gray-300 mx-auto" />
                    <p className="text-sm text-gray-500">Supermemory is not configured.</p>
                    <p className="text-xs text-gray-400">Set <code className="bg-gray-100 px-1.5 py-0.5 rounded font-mono">SUPERMEMORY_API_KEY</code> in your backend .env</p>
                </div>
            )}
            {result && result.configured && (
                <div className="space-y-3 animate-fade-up">
                    <div className="bg-white border border-indigo-200 rounded-xl p-4 shadow-sm" style={{ borderLeft: '3px solid #6366f1' }}>
                        <div className="flex items-center gap-2 mb-2">
                            <Brain className="w-4 h-4 text-indigo-500" />
                            <span className="text-[10px] text-indigo-600 uppercase tracking-wider font-semibold">Intelligence Synthesis</span>
                        </div>
                        <p className="text-sm text-gray-700 leading-relaxed">{result.answer}</p>
                    </div>
                    {result.memories.length > 0 && (
                        <div className="space-y-2">
                            <p className="text-[10px] text-gray-400 uppercase tracking-wider font-semibold px-1">
                                {result.memories.length} Matched Record{result.memories.length !== 1 ? 's' : ''}
                            </p>
                            {result.memories.map((mem, i) => (
                                <div key={i} className="bg-white border border-gray-200 rounded-xl p-3.5 shadow-sm animate-fade-up" style={{ animationDelay: `${i * 80}ms` }}>
                                    <div className="flex items-center justify-between mb-2">
                                        <div className="flex items-center gap-1.5">
                                            <FileText className="w-3 h-3 text-gray-300" />
                                            <span className="text-[10px] text-gray-400 font-mono">Record #{i + 1}</span>
                                        </div>
                                        {mem.score > 0 && <span className="text-[10px] text-gray-300 font-mono">score {mem.score.toFixed(3)}</span>}
                                    </div>
                                    <p className="text-xs text-gray-600 leading-relaxed line-clamp-4 whitespace-pre-line">
                                        {mem.content.slice(0, 400)}{mem.content.length > 400 && '…'}
                                    </p>
                                </div>
                            ))}
                        </div>
                    )}
                    {result.memories.length === 0 && (
                        <p className="text-center text-sm text-gray-400 py-4">No matching records found.</p>
                    )}
                </div>
            )}
        </div>
    )
}

// ─── InsightsPanel ────────────────────────────────────────────────────────────

function InsightsPanel({ videoId }: { videoId: string }) {
    const [data, setData]       = useState<InsightsData | null>(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        api.videoInsights(videoId).then(setData).catch(console.error).finally(() => setLoading(false))
    }, [videoId])

    if (loading) return (
        <div className="flex justify-center py-24">
            <Loader2 className="w-6 h-6 animate-spin text-indigo-500" />
        </div>
    )
    if (!data) return (
        <div className="text-center py-24 text-gray-400">
            <div className="w-14 h-14 bg-gray-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <BarChart3 className="w-7 h-7 opacity-40" />
            </div>
            <p className="text-sm">No insights available</p>
        </div>
    )

    const maxTypeCount = Math.max(...Object.values(data.event_types), 1)

    return (
        <div className="max-w-3xl mx-auto px-4 sm:px-6 py-6 space-y-4">
            {/* Stats bento */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {[
                    { label: 'Events',      value: data.total_events,                                   icon: Activity,      cls: 'text-indigo-600 border-indigo-200 bg-indigo-50' },
                    { label: 'Alerts',      value: data.total_alerts,                                   icon: AlertTriangle, cls: 'text-red-600 border-red-200 bg-red-50' },
                    { label: 'Event Types', value: Object.keys(data.event_types).length,                icon: Tag,           cls: 'text-violet-600 border-violet-200 bg-violet-50' },
                    { label: 'Max People',  value: Math.max(...data.timeline.map(t => t.people), 0),   icon: Users,         cls: 'text-emerald-600 border-emerald-200 bg-emerald-50' },
                ].map(({ label, value, icon: Icon, cls }) => (
                    <div key={label} className={`rounded-xl p-3.5 border animate-fade-up ${cls}`}>
                        <div className="flex items-center gap-1.5 mb-1.5">
                            <Icon className="w-3.5 h-3.5 opacity-70" />
                            <span className="text-[10px] text-gray-500 uppercase tracking-wider">{label}</span>
                        </div>
                        <div className="text-2xl font-bold">{value}</div>
                    </div>
                ))}
            </div>

            {/* Event distribution */}
            <div className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm">
                <h3 className="text-[10px] font-semibold text-gray-400 uppercase tracking-widest mb-4">Event Distribution</h3>
                <div className="space-y-2.5">
                    {Object.entries(data.event_types).sort((a, b) => b[1] - a[1]).map(([label, count]) => (
                        <div key={label} className="flex items-center gap-3">
                            <span className={`text-xs w-36 truncate font-medium ${labelColor(label)}`}>{label.replace(/_/g, ' ')}</span>
                            <div className="flex-1 bg-gray-100 rounded-full h-2 overflow-hidden">
                                <div
                                    className="h-full bg-gradient-to-r from-indigo-500 to-violet-500 rounded-full transition-all duration-700"
                                    style={{ width: `${(count / maxTypeCount) * 100}%` }}
                                />
                            </div>
                            <span className="text-xs text-gray-400 w-6 text-right font-mono">{count}</span>
                        </div>
                    ))}
                </div>
            </div>

            {/* Alert severity */}
            <div className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm">
                <h3 className="text-[10px] font-semibold text-gray-400 uppercase tracking-widest mb-4">Alert Severity</h3>
                <div className="flex gap-3">
                    {(['C', 'B', 'A'] as const).map(stage => {
                        const count = data.alert_stages[stage] || 0
                        return (
                            <div key={stage} className={`flex-1 rounded-xl p-3.5 border ${stageColor(stage)} ${count > 0 ? stageGlow(stage) : ''}`}>
                                <div className="text-2xl font-bold">{count}</div>
                                <div className="text-[10px] opacity-60 mt-0.5">Stage {stage}</div>
                            </div>
                        )
                    })}
                </div>
            </div>

            {/* Activity Timeline */}
            <div className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm">
                <h3 className="text-[10px] font-semibold text-gray-400 uppercase tracking-widest mb-3">Activity Timeline</h3>
                <div className="relative h-20 bg-gray-100 rounded-lg overflow-hidden">
                    {data.timeline.length > 0 && (() => {
                        const maxEnd = Math.max(...data.timeline.map(t => t.end), 1)
                        return data.timeline.map((t, i) => {
                            const left  = (t.start / maxEnd) * 100
                            const width = Math.max(((t.end - t.start) / maxEnd) * 100, 0.5)
                            const color = t.alert_stage === 'C' ? 'bg-red-400' :
                                          t.alert_stage === 'B' ? 'bg-orange-400' :
                                          t.alert_stage === 'A' ? 'bg-amber-400' : 'bg-indigo-400'
                            return (
                                <div key={i}
                                    title={`${fmt(t.start)}–${fmt(t.end)} | ${t.label}`}
                                    className={`absolute bottom-0 ${color} opacity-70 hover:opacity-100 cursor-pointer transition-opacity rounded-t`}
                                    style={{ left: `${left}%`, width: `${width}%`, height: `${Math.min(20 + t.people * 15, 100)}%` }}
                                />
                            )
                        })
                    })()}
                </div>
                <div className="flex justify-between text-[10px] text-gray-400 mt-1.5">
                    <span>0:00</span>
                    <span>{fmt(Math.max(...data.timeline.map(t => t.end), 0))}</span>
                </div>
            </div>
        </div>
    )
}
