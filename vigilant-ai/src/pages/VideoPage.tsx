import { useEffect, useState, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
    ArrowLeft, Shield, Clock, Users, Zap, Send, Search, Loader2,
    AlertTriangle, ChevronDown, ChevronUp, Activity, Eye, BarChart3,
    Tag, Brain, Cpu, Server
} from 'lucide-react'
import { api, ev, type EventData, type VideoSummary, type InsightsData, type VideoInfo } from '../api'

function fmt(s: number) { const m = Math.floor(s / 60); return `${m}:${Math.floor(s % 60).toString().padStart(2, '0')}` }

function stageColor(s: string) {
    if (s === 'C') return 'bg-red-500/15 text-red-400 border-red-500/40'
    if (s === 'B') return 'bg-orange-500/15 text-orange-400 border-orange-500/30'
    if (s === 'A') return 'bg-yellow-500/15 text-yellow-400 border-yellow-500/30'
    return 'bg-zinc-700/20 text-zinc-500 border-zinc-600/30'
}
function stageGlow(s: string) {
    if (s === 'C') return 'shadow-red-500/20 shadow-lg animate-pulse-ring'
    if (s === 'B') return 'shadow-orange-500/15 shadow-md'
    return ''
}
function labelColor(l: string) {
    if (l.includes('altercation') || l.includes('weapon') || l.includes('assault')) return 'text-red-400'
    if (l.includes('confrontation') || l.includes('aggressive') || l.includes('fight')) return 'text-orange-400'
    if (l.includes('trespassing') || l.includes('shoplifting') || l.includes('theft') || l.includes('steal')) return 'text-yellow-400'
    return 'text-zinc-200'
}
function riskBadge(r: string) {
    if (r === 'high')   return 'bg-red-500/15 text-red-400 border-red-500/40'
    if (r === 'medium') return 'bg-yellow-500/15 text-yellow-400 border-yellow-500/30'
    return 'bg-green-500/15 text-green-400 border-green-500/30'
}
function riskGlow(r: string) {
    if (r === 'high')   return 'shadow-red-500/20'
    if (r === 'medium') return 'shadow-yellow-500/10'
    return 'shadow-green-500/10'
}

export default function VideoPage() {
    const { videoId } = useParams<{ videoId: string }>()
    const navigate = useNavigate()
    const [alerts, setAlerts]       = useState<EventData[]>([])
    const [events, setEvents]       = useState<EventData[]>([])
    const [summary, setSummary]     = useState<VideoSummary | null>(null)
    const [videoInfo, setVideoInfo] = useState<VideoInfo | null>(null)
    const [loading, setLoading]     = useState(true)
    const [tab, setTab]             = useState<'chat' | 'alerts' | 'events' | 'insights'>('chat')

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
        <div className="min-h-screen bg-zinc-950 text-zinc-100 flex flex-col">
            {/* Ambient glow */}
            <div className="fixed inset-0 pointer-events-none">
                <div className="absolute top-0 right-1/4 w-80 h-80 bg-indigo-600/8 rounded-full blur-3xl" />
                {summary?.risk_level === 'high' && (
                    <div className="absolute bottom-1/4 left-1/4 w-60 h-60 bg-red-600/5 rounded-full blur-3xl" />
                )}
            </div>

            {/* Header */}
            <header className="sticky top-0 z-30 bg-zinc-950/70 backdrop-blur-xl border-b border-zinc-800/50">
                <div className="max-w-5xl mx-auto px-4 sm:px-6 py-3 flex items-center gap-3">
                    <button
                        onClick={() => navigate('/')}
                        className="p-1.5 hover:bg-zinc-800/80 rounded-lg transition-all text-zinc-400 hover:text-zinc-200"
                    >
                        <ArrowLeft className="w-5 h-5" />
                    </button>
                    <div className="flex items-center gap-2.5 min-w-0 flex-1">
                        <div className="relative w-8 h-8 shrink-0">
                            <div className="absolute inset-0 bg-gradient-to-br from-indigo-500 to-violet-600 rounded-lg blur-sm opacity-50" />
                            <div className="relative w-8 h-8 bg-gradient-to-br from-indigo-500 to-violet-600 rounded-lg flex items-center justify-center">
                                <Eye className="w-4 h-4 text-white" />
                            </div>
                        </div>
                        <div className="min-w-0">
                            <h1 className="text-sm font-semibold truncate text-zinc-100">{videoName}</h1>
                            <p className="text-[10px] text-zinc-500">{events.length} events · {alerts.length} alerts</p>
                        </div>
                    </div>
                    {/* Alert level indicator */}
                    {alerts.length > 0 && (
                        <span className={`shrink-0 flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-lg border font-medium ${
                            alerts.some(a => a.alert?.stage === 'C')
                                ? 'bg-red-500/15 text-red-400 border-red-500/30 animate-pulse-ring'
                                : 'bg-orange-500/10 text-orange-400 border-orange-500/20'
                        }`}>
                            <Shield className="w-3 h-3" /> {alerts.length}
                        </span>
                    )}
                </div>
            </header>

            {/* Summary Card */}
            {summary && (
                <div className="max-w-5xl mx-auto px-4 sm:px-6 py-4 w-full animate-fade-up">
                    <div className={`bg-zinc-900/70 backdrop-blur-lg border border-zinc-800/50 rounded-xl p-4 shadow-xl ${riskGlow(summary.risk_level)}`}
                         style={{ borderLeft: `3px solid ${summary.risk_level === 'high' ? '#ef4444' : summary.risk_level === 'medium' ? '#eab308' : '#22c55e'}` }}>
                        <div className="flex items-center gap-2 mb-2.5">
                            <Brain className="w-4 h-4 text-indigo-400" />
                            <span className="text-xs font-semibold text-indigo-400 uppercase tracking-wider">AI Analysis</span>
                            <span className={`text-[10px] px-2 py-0.5 rounded-full border font-bold ml-auto ${riskBadge(summary.risk_level)}`}>
                                {summary.risk_level.toUpperCase()} RISK
                            </span>
                        </div>
                        <p className="text-sm text-zinc-300 leading-relaxed mb-3">{summary.summary}</p>
                        <div className="flex flex-wrap gap-1.5">
                            {summary.intent.map(i => (
                                <span key={i} className="text-[10px] px-2 py-0.5 bg-indigo-500/10 text-indigo-300 rounded-full border border-indigo-500/20 font-medium">
                                    {i.replace(/_/g, ' ')}
                                </span>
                            ))}
                            {summary.tags.slice(0, 5).map(t => (
                                <span key={t} className="text-[10px] px-2 py-0.5 bg-zinc-800/80 text-zinc-400 rounded-full border border-zinc-700/30">
                                    {t}
                                </span>
                            ))}
                        </div>
                        {summary.key_moments.length > 0 && (
                            <div className="mt-3 border-t border-zinc-800/40 pt-2.5 space-y-1">
                                <p className="text-[10px] text-zinc-500 font-semibold uppercase tracking-wider mb-1.5">Key Moments</p>
                                {summary.key_moments.map((km, i) => (
                                    <div key={i} className="flex items-center gap-2 text-xs text-zinc-400">
                                        <Clock className="w-3 h-3 text-zinc-600 shrink-0" />
                                        <span className="text-indigo-400 font-mono shrink-0">{km.time}</span>
                                        <span className="text-zinc-400">{km.description}</span>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* Processing Stats chips */}
            {videoInfo && ((videoInfo.chunks ?? 0) > 0 || (videoInfo.gpu_time_s ?? 0) > 0) && (
                <div className="max-w-5xl mx-auto px-4 sm:px-6 pb-3 w-full">
                    <div className="flex flex-wrap gap-2">
                        {videoInfo.gpu && (
                            <StatChip icon={<Server className="w-3 h-3" />} label={videoInfo.gpu} color="violet" />
                        )}
                        {(videoInfo.chunks ?? 0) > 0 && (
                            <StatChip icon={<Cpu className="w-3 h-3" />} label={`${videoInfo.chunks} chunks · ${videoInfo.subclips} subclips`} color="zinc" />
                        )}
                        {(videoInfo.cpu_time_s ?? 0) > 0 && (
                            <StatChip icon={null} label={`CPU ${videoInfo.cpu_time_s?.toFixed(0)}s`} color="zinc" />
                        )}
                        {(videoInfo.gpu_time_s ?? 0) > 0 && (
                            <StatChip icon={<Zap className="w-3 h-3" />} label={`GPU ${videoInfo.gpu_time_s?.toFixed(0)}s`} color="violet" />
                        )}
                        {(videoInfo.processing_time_s ?? 0) > 0 && (
                            <StatChip icon={<Clock className="w-3 h-3" />} label={`Total ${videoInfo.processing_time_s?.toFixed(0)}s`} color="zinc" />
                        )}
                    </div>
                </div>
            )}

            {/* Tabs */}
            <div className="border-b border-zinc-800/60 bg-zinc-900/20 backdrop-blur-sm sticky top-[57px] z-20">
                <div className="max-w-5xl mx-auto px-4 sm:px-6 flex gap-1">
                    {(['chat', 'alerts', 'events', 'insights'] as const).map(t => (
                        <button
                            key={t}
                            onClick={() => setTab(t)}
                            className={`px-4 py-2.5 text-xs font-medium transition-all border-b-2 capitalize ${
                                tab === t
                                    ? 'text-indigo-400 border-indigo-500'
                                    : 'text-zinc-500 border-transparent hover:text-zinc-300 hover:border-zinc-700'
                            }`}
                        >
                            {t === 'alerts'   ? `Alerts (${alerts.length})` :
                             t === 'events'   ? `Events (${events.length})` :
                             t === 'insights' ? 'Insights' : 'Chat'}
                        </button>
                    ))}
                </div>
            </div>

            {/* Tab content */}
            <div className="flex-1 overflow-hidden relative z-10">
                {loading ? (
                    <div className="flex flex-col items-center justify-center py-24 gap-3">
                        <Loader2 className="w-7 h-7 animate-spin text-indigo-500" />
                        <p className="text-xs text-zinc-600">Loading analysis...</p>
                    </div>
                ) : tab === 'chat' ? (
                    <ChatPanel videoId={videoId} />
                ) : tab === 'alerts' ? (
                    <CardList items={alerts} emptyIcon={Shield} emptyText="No alerts detected" />
                ) : tab === 'insights' ? (
                    <InsightsPanel videoId={videoId} />
                ) : (
                    <CardList items={events} emptyIcon={Activity} emptyText="No events" />
                )}
            </div>
        </div>
    )
}

// ─── StatChip ─────────────────────────────────────────────────────────────────

function StatChip({ icon, label, color }: { icon: React.ReactNode; label: string; color: 'violet' | 'zinc' }) {
    const cls = color === 'violet'
        ? 'bg-violet-500/10 text-violet-400 border-violet-500/20'
        : 'bg-zinc-800/60 text-zinc-400 border-zinc-700/30'
    return (
        <span className={`flex items-center gap-1.5 text-[10px] px-2.5 py-1 ${cls} border rounded-lg`}>
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
        <div className="text-center py-24 text-zinc-600">
            <div className="w-14 h-14 bg-zinc-900 rounded-2xl flex items-center justify-center mx-auto mb-4">
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
                        className={`w-full text-left bg-zinc-900/70 backdrop-blur-lg border border-zinc-800/50 hover:bg-zinc-800/60 rounded-xl p-4 transition-all animate-fade-up ${
                            isStageC ? 'border-red-500/30 hover:border-red-500/40' : 'hover:border-zinc-700/60'
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
                                        e.alertScore > 0.7 ? 'text-red-400' : e.alertScore > 0.4 ? 'text-orange-400' : 'text-zinc-500'
                                    }`}>{e.alertScore.toFixed(2)}</span>
                                )}
                                {isOpen ? <ChevronUp className="w-3.5 h-3.5 text-zinc-500" /> : <ChevronDown className="w-3.5 h-3.5 text-zinc-600" />}
                            </div>
                        </div>
                        <div className="flex items-center gap-3 mt-1.5 text-xs text-zinc-500">
                            <span className="flex items-center gap-1">
                                <Clock className="w-3 h-3" /> {fmt(e.start)}–{fmt(e.end)}
                            </span>
                            <span className="flex items-center gap-1">
                                <Users className="w-3 h-3" /> {e.people}
                            </span>
                            {e.peakMotion > 0 && (
                                <span className="flex items-center gap-1">
                                    <Zap className="w-3 h-3" /> {e.peakMotion.toFixed(2)}
                                </span>
                            )}
                        </div>
                        {isOpen && e.caption && (
                            <p className="mt-3 text-xs text-zinc-400 leading-relaxed border-t border-zinc-700/20 pt-3 animate-fade-up">
                                {e.caption}
                            </p>
                        )}
                    </button>
                )
            })}
        </div>
    )
}

// ─── ChatPanel ────────────────────────────────────────────────────────────────

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
                // Phase 1: results arrive immediately — show clips before Gemini finishes
                (count, results) => {
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

            // Done streaming — remove cursor
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
        <div className="flex flex-col h-[calc(100vh-220px)]">
            <div className="flex-1 overflow-y-auto px-4 sm:px-6 py-4 space-y-3">
                {messages.map((msg, idx) => (
                    <div
                        key={msg.id}
                        className={`flex animate-fade-up ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                        style={{ animationDelay: `${idx * 20}ms` }}
                    >
                        <div className={`max-w-[92%] sm:max-w-[82%] rounded-2xl px-4 py-3 ${
                            msg.role === 'user'
                                ? 'bg-gradient-to-br from-indigo-600 to-violet-600 text-white shadow-lg shadow-indigo-500/20'
                                : 'bg-zinc-900/70 backdrop-blur-lg border border-zinc-800/50 text-zinc-100'
                        }`}>
                            {msg.loading ? (
                                <div className="flex items-center gap-2 text-zinc-400 text-sm py-0.5">
                                    <div className="flex gap-1">
                                        <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                                        <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                                        <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                                    </div>
                                    <span className="text-xs text-zinc-500">Searching footage...</span>
                                </div>
                            ) : (
                                <p className="text-sm leading-relaxed whitespace-pre-wrap">
                                    {msg.text}
                                    {msg.streaming && (
                                        <span className="inline-block w-0.5 h-4 bg-indigo-400 ml-0.5 animate-blink-cursor align-middle" />
                                    )}
                                </p>
                            )}

                            {/* Phase 1: clips appear instantly */}
                            {msg.results && msg.results.length > 0 && (
                                <div className="mt-3 space-y-1.5 animate-fade-up">
                                    <p className="text-[10px] text-zinc-500 font-semibold uppercase tracking-wider">
                                        {msg.results.length} Matching Clip{msg.results.length !== 1 ? 's' : ''}
                                    </p>
                                    {msg.results.slice(0, 5).map((raw, i) => {
                                        const e = ev(raw)
                                        return (
                                            <div
                                                key={e.clipId || i}
                                                className="bg-zinc-900/70 border border-zinc-700/30 rounded-lg p-2 text-xs animate-fade-up"
                                                style={{ animationDelay: `${i * 60}ms` }}
                                            >
                                                <div className="flex items-center gap-2">
                                                    <span className="text-zinc-600 font-mono text-[10px]">#{i + 1}</span>
                                                    <span className={`font-medium ${labelColor(e.label)}`}>
                                                        {e.label.replace(/_/g, ' ')}
                                                    </span>
                                                    {e.alertStage !== 'none' && (
                                                        <span className={`text-[9px] px-1 py-0.5 rounded border ${stageColor(e.alertStage)}`}>
                                                            {e.alertStage}
                                                        </span>
                                                    )}
                                                    <span className="text-zinc-600 ml-auto font-mono">{fmt(e.start)}–{fmt(e.end)}</span>
                                                </div>
                                                {e.caption && (
                                                    <p className="text-zinc-500 mt-1 line-clamp-1">{e.caption}</p>
                                                )}
                                            </div>
                                        )
                                    })}
                                </div>
                            )}
                        </div>
                    </div>
                ))}
                <div ref={bottomRef} />
            </div>

            {/* Input bar */}
            <div className="border-t border-zinc-800/60 px-4 sm:px-6 py-3 bg-zinc-900/50 backdrop-blur-sm">
                <div className="flex items-center gap-2 max-w-3xl mx-auto">
                    <div className="relative flex-1">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
                        <input
                            type="text"
                            value={input}
                            onChange={e => setInput(e.target.value)}
                            onKeyDown={e => e.key === 'Enter' && handleSend()}
                            placeholder="Ask about this video..."
                            disabled={searching}
                            className="w-full pl-10 pr-4 py-2.5 bg-zinc-800/80 border border-zinc-700/60 rounded-xl text-sm text-zinc-100 placeholder-zinc-600 outline-none transition-all focus:border-indigo-500/60 focus:ring-1 focus:ring-indigo-500/20 focus:bg-zinc-800 disabled:opacity-40"
                        />
                    </div>
                    <button
                        onClick={handleSend}
                        disabled={searching || !input.trim()}
                        className="p-2.5 bg-gradient-to-br from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 disabled:from-zinc-800 disabled:to-zinc-800 rounded-xl transition-all disabled:opacity-40 active:scale-95 shadow-lg shadow-indigo-500/20 disabled:shadow-none"
                    >
                        {searching
                            ? <Loader2 className="w-4 h-4 text-zinc-400 animate-spin" />
                            : <Send className="w-4 h-4 text-white" />
                        }
                    </button>
                </div>
            </div>
        </div>
    )
}

// ─── InsightsPanel ────────────────────────────────────────────────────────────

function InsightsPanel({ videoId }: { videoId: string }) {
    const [data, setData]     = useState<InsightsData | null>(null)
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
        <div className="text-center py-24 text-zinc-600">
            <div className="w-14 h-14 bg-zinc-900 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <BarChart3 className="w-7 h-7 opacity-40" />
            </div>
            <p className="text-sm">No insights available</p>
        </div>
    )

    const maxTypeCount = Math.max(...Object.values(data.event_types), 1)

    return (
        <div className="max-w-3xl mx-auto px-4 sm:px-6 py-6 space-y-5">
            {/* Stats */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {[
                    { label: 'Events',      value: data.total_events,                        icon: Activity,      color: 'indigo' },
                    { label: 'Alerts',      value: data.total_alerts,                        icon: AlertTriangle, color: 'red'    },
                    { label: 'Event Types', value: Object.keys(data.event_types).length,     icon: Tag,           color: 'violet' },
                    { label: 'Max People',  value: Math.max(...data.timeline.map(t => t.people), 0), icon: Users, color: 'emerald'},
                ].map(({ label, value, icon: Icon, color }) => {
                    const colors: Record<string, string> = {
                        indigo: 'text-indigo-400 border-indigo-500/20 bg-indigo-500/5',
                        red: 'text-red-400 border-red-500/20 bg-red-500/5',
                        violet: 'text-violet-400 border-violet-500/20 bg-violet-500/5',
                        emerald: 'text-emerald-400 border-emerald-500/20 bg-emerald-500/5',
                    }
                    return (
                        <div key={label} className={`rounded-xl p-3 border animate-fade-up ${colors[color]}`}>
                            <div className="flex items-center gap-1.5 mb-1.5">
                                <Icon className="w-3.5 h-3.5 opacity-80" />
                                <span className="text-[10px] text-zinc-500 uppercase tracking-wider">{label}</span>
                            </div>
                            <div className="text-2xl font-bold">{value}</div>
                        </div>
                    )
                })}
            </div>

            {/* Event type bars */}
            <div className="bg-zinc-900/70 backdrop-blur-lg border border-zinc-800/50 rounded-xl p-4">
                <h3 className="text-[10px] font-semibold text-zinc-500 uppercase tracking-widest mb-4">Event Distribution</h3>
                <div className="space-y-2.5">
                    {Object.entries(data.event_types).sort((a, b) => b[1] - a[1]).map(([label, count]) => (
                        <div key={label} className="flex items-center gap-3">
                            <span className={`text-xs w-36 truncate ${labelColor(label)}`}>{label.replace(/_/g, ' ')}</span>
                            <div className="flex-1 bg-zinc-800 rounded-full h-1.5 overflow-hidden">
                                <div
                                    className="h-full bg-gradient-to-r from-indigo-500 to-violet-500 rounded-full transition-all duration-700"
                                    style={{ width: `${(count / maxTypeCount) * 100}%` }}
                                />
                            </div>
                            <span className="text-xs text-zinc-600 w-6 text-right font-mono">{count}</span>
                        </div>
                    ))}
                </div>
            </div>

            {/* Alert severity */}
            <div className="bg-zinc-900/70 backdrop-blur-lg border border-zinc-800/50 rounded-xl p-4">
                <h3 className="text-[10px] font-semibold text-zinc-500 uppercase tracking-widest mb-4">Alert Severity</h3>
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
            <div className="bg-zinc-900/70 backdrop-blur-lg border border-zinc-800/50 rounded-xl p-4">
                <h3 className="text-[10px] font-semibold text-zinc-500 uppercase tracking-widest mb-3">Activity Timeline</h3>
                <div className="relative h-20 bg-zinc-800/50 rounded-lg overflow-hidden">
                    {data.timeline.length > 0 && (() => {
                        const maxEnd = Math.max(...data.timeline.map(t => t.end), 1)
                        return data.timeline.map((t, i) => {
                            const left  = (t.start / maxEnd) * 100
                            const width = Math.max(((t.end - t.start) / maxEnd) * 100, 0.5)
                            const color = t.alert_stage === 'C' ? 'bg-red-500' :
                                          t.alert_stage === 'B' ? 'bg-orange-500' :
                                          t.alert_stage === 'A' ? 'bg-yellow-500' : 'bg-indigo-500'
                            return (
                                <div key={i}
                                    title={`${fmt(t.start)}–${fmt(t.end)} | ${t.label}`}
                                    className={`absolute bottom-0 ${color} opacity-70 hover:opacity-100 transition-opacity cursor-pointer rounded-t`}
                                    style={{
                                        left: `${left}%`,
                                        width: `${width}%`,
                                        height: `${Math.min(20 + t.people * 15, 100)}%`,
                                    }}
                                />
                            )
                        })
                    })()}
                </div>
                <div className="flex justify-between text-[10px] text-zinc-600 mt-1.5">
                    <span>0:00</span>
                    <span>{fmt(Math.max(...data.timeline.map(t => t.end), 0))}</span>
                </div>
            </div>
        </div>
    )
}
