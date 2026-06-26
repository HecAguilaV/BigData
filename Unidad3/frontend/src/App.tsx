import { useEffect, useState, useCallback } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  AreaChart, Area, CartesianGrid, Cell,
} from 'recharts'
import { MapContainer, TileLayer, CircleMarker, Tooltip as LeafletTooltip } from 'react-leaflet'
import {
  Database, DollarSign, Activity, Users, RefreshCw,
  TrendingUp, Store, MapPin, LayoutDashboard, Radio,
} from 'lucide-react'

const API = '/api'

type BatchKpis = { total_tx: number; total_revenue: number; avg_ticket: number }
type StreamKpis = { total_sessions: number; view_count: number; cart_count: number; purchase_count: number }
type AforoRow = { id_sucursal: number; nombre_sucursal: string; zona: string; region: string; lat: number; lng: number; aforo_actual: number; capacidad_maxima: number; porcentaje_ocupacion: number; personas_entran: number; personas_salen: number }
type MonthlyRow = { fecha: string; monto_clp: number }
type SucursalRow = { id_sucursal: number; monto_clp: number; nombre_sucursal?: string }

const navItems = [
  { id: 'resumen', label: 'Resumen', icon: LayoutDashboard },
  { id: 'ventas', label: 'Ventas', icon: TrendingUp },
  { id: 'streaming', label: 'Streaming', icon: Radio },
  { id: 'ml', label: 'ML Forecast', icon: TrendingUp },
  { id: 'sucursales', label: 'Sucursales', icon: Store },
  { id: 'aforo', label: 'Aforo IoT', icon: MapPin },
]

const COLORS10 = ['#2563eb', '#059669', '#d97706', '#dc2626', '#7c3aed', '#0891b2', '#db2777', '#65a30d', '#0d9488', '#9333ea']

function aforoColor(pct: number): string {
  if (pct >= 80) return '#dc2626'
  if (pct >= 50) return '#d97706'
  return '#16a34a'
}

export default function App() {
  const [activeTab, setActiveTab] = useState('resumen')
  const [batch, setBatch] = useState<BatchKpis | null>(null)
  const [stream, setStream] = useState<StreamKpis | null>(null)
  const [aforo, setAforo] = useState<AforoRow[]>([])
  const [monthly, setMonthly] = useState<MonthlyRow[]>([])
  const [sucursal, setSucursal] = useState<SucursalRow[]>([])
  const [devices, setDevices] = useState<{device:string;count:number}[]>([])
  const [paymentMethods, setPaymentMethods] = useState<{metodo_pago:string;count:number}[]>([])
  const [mlPredict, setMlPredict] = useState<{id_sucursal:number;nombre_sucursal:string;prediccion:number;real_ultimo_mes:number}[]>([])
  const [mlLoading, setMlLoading] = useState(false)
  const [lastUpdate, setLastUpdate] = useState<string>('')
  const [countdown, setCountdown] = useState(0)

  useEffect(() => {
    if (countdown <= 0) return
    const iv = setInterval(() => setCountdown(c => c - 1), 1000)
    return () => clearInterval(iv)
  }, [countdown])

  const fetchAll = useCallback(async () => {
    const r = async (url: string) => { try { return await fetch(url).then(r => r.json()) } catch { return null } }
    const [b, s, a, m, sc, d, p] = await Promise.all([
      r(`${API}/batch/kpis`),
      r(`${API}/streaming/kpis`),
      r(`${API}/aforo/current`),
      r(`${API}/sales/monthly`),
      r(`${API}/sales/sucursal`),
      r(`${API}/streaming/devices`),
      r(`${API}/payment/methods`),
    ])
    if (b) setBatch(b)
    if (s) setStream(s)
    if (a) setAforo(a)
    if (m) setMonthly(m.slice(-24).map((r: any) => ({ fecha: r.month, monto_clp: r.total })))
    if (sc) setSucursal(sc.slice(0, 10).map((r: any) => ({ id_sucursal: r.id_sucursal, monto_clp: r.total, nombre_sucursal: r.nombre_sucursal })))
    if (d) setDevices(d)
    if (p) setPaymentMethods(p)
    setLastUpdate(new Date().toLocaleTimeString('es-CL', { hour: '2-digit', minute: '2-digit', second: '2-digit' }))
    setCountdown(60)
  }, [])

  useEffect(() => {
    const iv = setInterval(fetchAll, 60000)
    return () => clearInterval(iv)
  }, [fetchAll])

  // Fetch ML predictions only when ML tab is active
  useEffect(() => {
    if (activeTab !== 'ml') return
    const fetchML = async () => {
      setMlLoading(true)
      try {
        const res = await fetch(`${API}/ml/predict`)
        const data = await res.json()
        if (Array.isArray(data)) setMlPredict(data)
      } catch {}
      setMlLoading(false)
    }
    fetchML()
  }, [activeTab])

  const streamPie = stream
    ? [
        { name: 'View Product', value: stream.view_count, color: '#2563eb' },
        { name: 'Add to Cart', value: stream.cart_count, color: '#d97706' },
        { name: 'Purchase', value: stream.purchase_count, color: '#059669' },
      ]
    : []

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <aside className="w-56 bg-white border-r border-gray-200 p-4 flex flex-col gap-1 shrink-0">
        <div className="mb-6 px-3 pt-2">
          <h1 className="text-base font-bold text-gray-800">Grupo Cordillera</h1>
          <p className="text-xs text-gray-400 mt-0.5">Analytics Platform</p>
        </div>
        {navItems.map(item => (
          <button
            key={item.id}
            onClick={() => setActiveTab(item.id)}
            className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition text-left ${
              activeTab === item.id
                ? 'bg-blue-50 text-blue-700'
                : 'text-gray-500 hover:bg-gray-50 hover:text-gray-700'
            }`}
          >
            <item.icon size={18} />
            {item.label}
          </button>
        ))}
        <div className="mt-auto pt-4 border-t border-gray-100">
          <button onClick={fetchAll} className="flex items-center gap-2 text-xs text-gray-400 hover:text-gray-600 transition w-full px-3 py-2">
            <RefreshCw size={14} /> Actualizar ahora
          </button>
          <p className="text-[10px] text-gray-300 px-3 mt-2">🔄 Próxima en {countdown}s · {lastUpdate || '—'}</p>
        </div>
      </aside>

      {/* Main */}
      <main className="flex-1 p-6 overflow-auto space-y-5">
        {/* KPIs */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-2">
          <div className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-lg bg-blue-50 text-blue-600"><Database size={18} /></div>
              <div>
                <p className="text-gray-400 text-xs uppercase tracking-wider font-medium">Transacciones</p>
                <p className="text-xl font-bold text-gray-900">{batch?.total_tx?.toLocaleString() ?? '-'}</p>
              </div>
            </div>
          </div>
          <div className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-lg bg-emerald-50 text-emerald-600"><DollarSign size={18} /></div>
              <div>
                <p className="text-gray-400 text-xs uppercase tracking-wider font-medium">Facturado</p>
                <p className="text-xl font-bold text-gray-900">{batch ? `$${(batch.total_revenue / 1_000_000_000).toFixed(1)}B` : '-'}</p>
              </div>
            </div>
          </div>
          <div className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-lg bg-purple-50 text-purple-600"><Activity size={18} /></div>
              <div>
                <p className="text-gray-400 text-xs uppercase tracking-wider font-medium">Eventos Streaming</p>
                <p className="text-xl font-bold text-gray-900">{stream?.total_sessions?.toLocaleString() ?? '-'}</p>
              </div>
            </div>
          </div>
          <div className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-lg bg-amber-50 text-amber-600"><Users size={18} /></div>
              <div>
                <p className="text-gray-400 text-xs uppercase tracking-wider font-medium">Aforo en Tiendas</p>
                <p className="text-xl font-bold text-gray-900">{aforo.reduce((s, r) => s + r.aforo_actual, 0).toLocaleString()}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Resumen */}
        {activeTab === 'resumen' && (
          <>
            {/* Fila 1: área + pie */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
              <div className="lg:col-span-2 bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
                <h2 className="text-sm font-semibold text-gray-700 mb-3">📈 Ventas Mensuales (últimos 24 meses)</h2>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={monthly}>
                    <defs>
                      <linearGradient id="colorMonto" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#2563eb" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#2563eb" stopOpacity={0.02} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                    <XAxis dataKey="fecha" tick={{ fontSize: 10, fill: '#9ca3af' }} tickFormatter={v => v?.slice(0, 7)} />
                    <YAxis tick={{ fontSize: 10, fill: '#9ca3af' }} tickFormatter={v => `$${(v / 1_000_000_000).toFixed(1)}B`} />
                    <Tooltip contentStyle={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 8, boxShadow: '0 2px 8px rgba(0,0,0,0.06)' }} />
                    <Area type="monotone" dataKey="monto_clp" stroke="#2563eb" strokeWidth={2} fill="url(#colorMonto)" dot={false} />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
              <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
                <h2 className="text-sm font-semibold text-gray-700 mb-3">📊 Progresión Streaming</h2>
                <div className="flex flex-col justify-center h-[300px] gap-4 px-2">
                  {streamPie.map((item, i) => {
                    const maxVal = streamPie[0]?.value || 1
                    const pct = (item.value / maxVal) * 100
                    return (
                      <div key={item.name}>
                        <div className="flex justify-between text-xs mb-1.5">
                          <span className="font-medium text-gray-600">{item.name}</span>
                          <span className="font-bold" style={{ color: item.color }}>{item.value.toLocaleString()}</span>
                        </div>
                        <div className="h-4 rounded-md overflow-hidden" style={{ width: `${60 + pct * 0.4}%`, backgroundColor: `${item.color}15` }}>
                          <div className="h-full rounded-md" style={{ width: `${pct}%`, backgroundColor: item.color }} />
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>
            </div>

            {/* Fila 2: sucursales + aforo */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
              <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
                <h2 className="text-sm font-semibold text-gray-700 mb-3">🏪 Top Sucursales</h2>
                <ResponsiveContainer width="100%" height={280}>
                  <BarChart data={sucursal} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                    <XAxis type="number" tick={{ fontSize: 10, fill: '#9ca3af' }} tickFormatter={v => `$${(v / 1_000_000_000).toFixed(1)}B`} />
                    <YAxis type="category" dataKey="id_sucursal" tick={{ fontSize: 10, fill: '#9ca3af' }} tickFormatter={v => v === 0 ? 'E-Com' : `S${v}`} width={50} />
                    <Tooltip contentStyle={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 8, boxShadow: '0 2px 8px rgba(0,0,0,0.06)' }} />
                    <Bar dataKey="monto_clp" radius={[0, 4, 4, 0]}>
                      {sucursal.map((_, i) => <Cell key={i} fill={COLORS10[i % COLORS10.length]} />)}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
                <h2 className="text-sm font-semibold text-gray-700 mb-3">📊 Ocupación Tiendas</h2>
                <div className="space-y-3">
                  {aforo.slice(0, 6).map(r => (
                    <div key={r.id_sucursal}>
                      <div className="flex justify-between text-xs mb-1">
                        <span className="font-medium text-gray-600">{r.nombre_sucursal}</span>
                        <span style={{ color: aforoColor(r.porcentaje_ocupacion) }} className="font-bold">{r.porcentaje_ocupacion}%</span>
                      </div>
                      <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                        <div className="h-full rounded-full" style={{ width: `${r.porcentaje_ocupacion}%`, backgroundColor: aforoColor(r.porcentaje_ocupacion) }} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </>
        )}

        {/* Ventas */}
        {activeTab === 'ventas' && (
          <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
            <h2 className="text-sm font-semibold text-gray-700 mb-3">📊 Evolución de Ventas (histórico completo)</h2>
            <ResponsiveContainer width="100%" height={420}>
              <AreaChart data={monthly}>
                <defs>
                  <linearGradient id="colorVentas" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#2563eb" stopOpacity={0.25} />
                    <stop offset="95%" stopColor="#2563eb" stopOpacity={0.02} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="fecha" tick={{ fontSize: 10, fill: '#9ca3af' }} tickFormatter={v => v?.slice(0, 7)} interval={5} />
                <YAxis tick={{ fontSize: 10, fill: '#9ca3af' }} tickFormatter={v => `$${(v / 1_000_000_000).toFixed(1)}B`} />
                <Tooltip contentStyle={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 8, boxShadow: '0 2px 8px rgba(0,0,0,0.06)' }} />
                <Area type="monotone" dataKey="monto_clp" stroke="#2563eb" strokeWidth={2} fill="url(#colorVentas)" dot={false} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Streaming */}
        {activeTab === 'streaming' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
            <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
              <h2 className="text-sm font-semibold text-gray-700 mb-3">📱 Dispositivos</h2>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={devices} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis type="number" tick={{ fontSize: 10, fill: '#9ca3af' }} />
                  <YAxis type="category" dataKey="device" tick={{ fontSize: 12, fill: '#9ca3af' }} width={70} />
                  <Tooltip contentStyle={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 8 }} />
                  <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                    {devices.map((_, i) => <Cell key={i} fill={['#2563eb','#059669','#d97706'][i % 3]} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
              <h2 className="text-sm font-semibold text-gray-700 mb-3">💳 Métodos de Pago</h2>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={paymentMethods} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis type="number" tick={{ fontSize: 10, fill: '#9ca3af' }} />
                  <YAxis type="category" dataKey="metodo_pago" tick={{ fontSize: 10, fill: '#9ca3af' }} width={100} tickFormatter={v => v.replace(/_/g, ' ')} />
                  <Tooltip contentStyle={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 8 }} />
                  <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                    {paymentMethods.map((_, i) => <Cell key={i} fill={['#2563eb','#0891b2','#059669','#7c3aed'][i % 4]} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="lg:col-span-2 bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
              <h2 className="text-sm font-semibold text-gray-700 mb-3">🔵 Progresión Streaming</h2>
              <div className="flex gap-6 items-end h-[120px] px-4">
                {[
                  { label: '👀 Visitas', val: stream?.view_count ?? 0, color: '#2563eb' },
                  { label: '🛒 Carrito', val: stream?.cart_count ?? 0, color: '#d97706' },
                  { label: '✅ Compras', val: stream?.purchase_count ?? 0, color: '#059669' },
                ].map((item, i) => {
                  const maxVal = Math.max(stream?.view_count ?? 1, 1)
                  const pct = (item.val / maxVal) * 100
                  return (
                    <div key={item.label} className="flex-1 flex flex-col items-center gap-2">
                      <span className="text-xs text-gray-500">{item.val.toLocaleString()}</span>
                      <div className="w-full rounded-md" style={{ height: `${Math.max(8, pct * 0.8)}px`, backgroundColor: item.color, opacity: 1 - i * 0.15 }} />
                      <span className="text-xs font-medium text-gray-600">{item.label}</span>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>
        )}

        {/* ML Forecast */}
        {activeTab === 'ml' && (
          <div className="space-y-5">
            <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
              <h2 className="text-sm font-semibold text-gray-700 mb-1">🤖 Pronóstico de Ventas LightGBM</h2>
              <p className="text-xs text-gray-400 mb-4">Predicción del próximo mes por sucursal vs. último mes real</p>
              {mlLoading ? (
                <p className="text-sm text-gray-400">Cargando predicciones...</p>
              ) : mlPredict.length > 0 ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
                  {mlPredict.map(r => {
                    const diff = r.prediccion - r.real_ultimo_mes
                    const pct = r.real_ultimo_mes > 0 ? ((diff / r.real_ultimo_mes) * 100).toFixed(1) : '—'
                    return (
                      <div key={r.id_sucursal} className="border border-gray-100 rounded-lg p-3">
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-xs font-semibold text-gray-700">
                            {r.id_sucursal === 0 ? '🛒 ' : '🏪 '}{r.nombre_sucursal || `Sucursal ${r.id_sucursal}`}
                          </span>
                          <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${diff > 0 ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-700'}`}>
                            {diff > 0 ? '↑' : '↓'} {pct}%
                          </span>
                        </div>
                        <div className="flex justify-between text-xs">
                          <span className="text-gray-400">Predicción:</span>
                          <span className="font-medium text-gray-800">${(r.prediccion / 1_000_000).toFixed(1)}M</span>
                        </div>
                        <div className="flex justify-between text-xs mt-1">
                          <span className="text-gray-400">Real último mes:</span>
                          <span className="font-medium text-gray-800">${(r.real_ultimo_mes / 1_000_000).toFixed(1)}M</span>
                        </div>
                      </div>
                    )
                  })}
                </div>
              ) : (
                <p className="text-sm text-gray-400">Ejecute el notebook LightGBM primero para entrenar el modelo, o espere a que cargue el endpoint.</p>
              )}
            </div>
          </div>
        )}

        {/* Sucursales */}
        {activeTab === 'sucursales' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
            <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
              <h2 className="text-sm font-semibold text-gray-700 mb-3">🥇 Ranking por Sucursal</h2>
              <ResponsiveContainer width="100%" height={420}>
                <BarChart data={sucursal} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis type="number" tick={{ fontSize: 10, fill: '#9ca3af' }} tickFormatter={v => `$${(v / 1_000_000_000).toFixed(1)}B`} />
                  <YAxis type="category" dataKey="id_sucursal" tick={{ fontSize: 10, fill: '#9ca3af' }} tickFormatter={v => {
                    const s = sucursal.find(r => r.id_sucursal === v)
                    return s?.nombre_sucursal ? s.nombre_sucursal.slice(0, 10) : (v === 0 ? 'E-Com' : `S${v}`)
                  }} width={85} />
                  <Tooltip contentStyle={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 8, boxShadow: '0 2px 8px rgba(0,0,0,0.06)' }} />
                  <Bar dataKey="monto_clp" radius={[0, 4, 4, 0]}>
                    {sucursal.map((_, i) => <Cell key={i} fill={COLORS10[i % COLORS10.length]} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="space-y-3">
              {sucursal.slice(0, 5).map((s, i) => (
                <div key={s.id_sucursal} className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-700">{s.id_sucursal === 0 ? '🛒 E-Commerce' : `🏪 ${s.nombre_sucursal || `Sucursal ${s.id_sucursal}`}`}</span>
                    <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${i === 0 ? 'bg-yellow-50 text-yellow-700 border border-yellow-200' : 'bg-gray-50 text-gray-500 border border-gray-200'}`}>#{i + 1}</span>
                  </div>
                  <div className="flex items-baseline gap-1">
                    <p className="text-lg font-bold text-gray-900">${(s.monto_clp / 1_000_000_000).toFixed(2)}B</p>
                    <span className="text-xs text-gray-400">CLP</span>
                  </div>
                  <div className="mt-2 h-2 bg-gray-100 rounded-full overflow-hidden">
                    <div className="h-full rounded-full" style={{ width: `${(s.monto_clp / sucursal[0]?.monto_clp) * 100}%`, backgroundColor: COLORS10[i] }} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Aforo */}
        {activeTab === 'aforo' && (
          <>
            <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
              <h2 className="text-sm font-semibold text-gray-700 mb-3">📍 Mapa Nacional — {aforo.length} sucursales</h2>
              <div className="h-[500px] rounded-lg overflow-hidden">
                {aforo.length > 0 && (
                  <MapContainer center={[-39.0, -72.0]} zoom={6} className="h-full w-full" scrollWheelZoom={false}>
                    <TileLayer url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png" />
                    {aforo.map(r => (
                      <CircleMarker key={r.id_sucursal} center={[r.lat, r.lng]} radius={Math.max(7, r.porcentaje_ocupacion / 4)} pathOptions={{ color: aforoColor(r.porcentaje_ocupacion), fillOpacity: 0.5 }}>
                        <LeafletTooltip direction="top">
                          <strong>{r.nombre_sucursal}</strong><br />
                          {r.zona} · {r.region}<br />
                          {r.porcentaje_ocupacion}% ({r.aforo_actual}/{r.capacidad_maxima})
                        </LeafletTooltip>
                      </CircleMarker>
                    ))}
                  </MapContainer>
                )}
              </div>
            </div>

            {/* KPIs por zona */}
            {['Norte', 'Centro', 'Sur', 'Austral'].map(zona => {
              const filtrados = aforo.filter(r => r.zona === zona)
              if (!filtrados.length) return null
              const totalOcup = filtrados.reduce((s, r) => s + r.aforo_actual, 0)
              const totalCap = filtrados.reduce((s, r) => s + r.capacidad_maxima, 0)
              return (
                <div key={zona} className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
                  <div className="flex items-center gap-3 mb-4">
                    <span className={`text-xs font-bold px-2.5 py-1 rounded-full ${
                      zona === 'Norte' ? 'bg-orange-50 text-orange-700' :
                      zona === 'Centro' ? 'bg-blue-50 text-blue-700' :
                      zona === 'Sur' ? 'bg-green-50 text-green-700' :
                      'bg-sky-50 text-sky-700'
                    }`}>{zona}</span>
                    <span className="text-sm text-gray-500">{filtrados.length} sucursales</span>
                    <span className="text-sm text-gray-400 ml-auto">
                      {totalOcup.toLocaleString()} / {totalCap.toLocaleString()} ocupados
                    </span>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                    {filtrados.map(r => (
                      <div key={r.id_sucursal} className="border border-gray-100 rounded-lg p-3">
                        <div className="flex justify-between items-center mb-1">
                          <span className="text-xs font-semibold text-gray-700">{r.nombre_sucursal}</span>
                          <span className="text-[10px] text-gray-400">{r.region.split(' - ')[0]}</span>
                        </div>
                        <div className="h-2 bg-gray-100 rounded-full overflow-hidden mb-1">
                          <div className="h-full rounded-full" style={{ width: `${r.porcentaje_ocupacion}%`, backgroundColor: aforoColor(r.porcentaje_ocupacion) }} />
                        </div>
                        <div className="flex justify-between text-[10px] text-gray-400">
                          <span>{r.aforo_actual}/{r.capacidad_maxima}</span>
                          <span style={{ color: aforoColor(r.porcentaje_ocupacion) }} className="font-bold">{r.porcentaje_ocupacion}%</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )
            })}
          </>
        )}
      </main>
    </div>
  )
}
