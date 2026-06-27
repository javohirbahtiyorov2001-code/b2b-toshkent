"use client";

import { useState, useEffect } from "react";
import { createClient } from "@supabase/supabase-js";

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

const SCORE_COLORS = { Hot: "bg-red-500", Warm: "bg-yellow-500", Cold: "bg-blue-400" };
const STATUS_COLORS = {
  New: "bg-gray-600",
  Contacted: "bg-blue-600",
  Qualified: "bg-purple-600",
  Won: "bg-green-600",
  Lost: "bg-red-800",
};

const NICHES = ["All", "Restaurant", "Clinic", "Construction", "Logistics", "Retail",
  "Auto Service", "Hotel", "Fitness", "Education", "Marketing Agency", "Other"];
const STATUSES = ["All", "New", "Contacted", "Qualified", "Won", "Lost"];
const SCORES = ["All", "Hot", "Warm", "Cold"];

type Lead = {
  id: string;
  name: string;
  phone: string | null;
  niche: string;
  source: string;
  score: "Hot" | "Warm" | "Cold";
  status: "New" | "Contacted" | "Qualified" | "Won" | "Lost";
  address: string | null;
  website: string | null;
  notes: string | null;
  created_at: string;
};

export default function CRMDashboard() {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [filtered, setFiltered] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [filterNiche, setFilterNiche] = useState("All");
  const [filterStatus, setFilterStatus] = useState("All");
  const [filterScore, setFilterScore] = useState("All");
  const [selected, setSelected] = useState<Lead | null>(null);
  const [editNotes, setEditNotes] = useState("");
  const [stats, setStats] = useState({ total: 0, hot: 0, warm: 0, won: 0 });

  useEffect(() => { fetchLeads(); }, []);

  useEffect(() => {
    let list = [...leads];
    if (search) list = list.filter(l =>
      l.name.toLowerCase().includes(search.toLowerCase()) ||
      (l.phone || "").includes(search)
    );
    if (filterNiche !== "All") list = list.filter(l => l.niche === filterNiche);
    if (filterStatus !== "All") list = list.filter(l => l.status === filterStatus);
    if (filterScore !== "All") list = list.filter(l => l.score === filterScore);
    setFiltered(list);
  }, [leads, search, filterNiche, filterStatus, filterScore]);

  async function fetchLeads() {
    setLoading(true);
    const { data } = await supabase
      .from("leads")
      .select("*")
      .order("created_at", { ascending: false });
    const list = data as Lead[] || [];
    setLeads(list);
    setStats({
      total: list.length,
      hot: list.filter(l => l.score === "Hot").length,
      warm: list.filter(l => l.score === "Warm").length,
      won: list.filter(l => l.status === "Won").length,
    });
    setLoading(false);
  }

  async function updateLead(id: string, updates: Partial<Lead>) {
    await supabase.from("leads").update(updates).eq("id", id);
    setLeads(prev => prev.map(l => l.id === id ? { ...l, ...updates } : l));
    if (selected?.id === id) setSelected(prev => prev ? { ...prev, ...updates } : null);
  }

  async function buildWebsite(lead: Lead) {
    const brief = {
      business_name: lead.name,
      niche: lead.niche,
      type: "landing",
      phone: lead.phone,
      address: lead.address,
      language: "uzbek",
      colors: { primary: "#1a1a2e", accent: "#e94560" },
      services: [],
    };
    const res = await fetch("/api/build", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(brief),
    });
    const data = await res.json();
    if (data.url) {
      await updateLead(lead.id, { status: "Won" });
      alert(`Site deployed: ${data.url}`);
    }
  }

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 p-6 font-sans">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-white">B2B Lead CRM</h1>
            <p className="text-gray-400 text-sm mt-1">Toshkent biznes leedlari boshqaruvi</p>
          </div>
          <button
            onClick={fetchLeads}
            className="bg-indigo-600 hover:bg-indigo-500 px-4 py-2 rounded-lg text-sm font-medium transition"
          >
            Yangilash
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-4 gap-4 mb-8">
          {[
            { label: "Jami leedlar", value: stats.total, color: "text-white" },
            { label: "Hot leedlar", value: stats.hot, color: "text-red-400" },
            { label: "Warm leedlar", value: stats.warm, color: "text-yellow-400" },
            { label: "Won (bitim)", value: stats.won, color: "text-green-400" },
          ].map(s => (
            <div key={s.label} className="bg-gray-900 border border-gray-800 rounded-xl p-4">
              <div className={`text-3xl font-bold ${s.color}`}>{s.value}</div>
              <div className="text-gray-400 text-sm mt-1">{s.label}</div>
            </div>
          ))}
        </div>

        {/* Filters */}
        <div className="flex gap-3 mb-6 flex-wrap">
          <input
            type="text"
            placeholder="Qidirish (ism, telefon)..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-sm flex-1 min-w-48 focus:outline-none focus:border-indigo-500"
          />
          {[
            { label: "Niche", options: NICHES, value: filterNiche, set: setFilterNiche },
            { label: "Status", options: STATUSES, value: filterStatus, set: setFilterStatus },
            { label: "Score", options: SCORES, value: filterScore, set: setFilterScore },
          ].map(f => (
            <select
              key={f.label}
              value={f.value}
              onChange={e => f.set(e.target.value)}
              className="bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-indigo-500"
            >
              {f.options.map(o => <option key={o}>{o}</option>)}
            </select>
          ))}
        </div>

        {/* Table */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
          {loading ? (
            <div className="p-12 text-center text-gray-500">Yuklanmoqda...</div>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-800 text-gray-400 text-xs uppercase">
                  <th className="text-left p-4">Kompaniya</th>
                  <th className="text-left p-4">Telefon</th>
                  <th className="text-left p-4">Niche</th>
                  <th className="text-left p-4">Score</th>
                  <th className="text-left p-4">Status</th>
                  <th className="text-left p-4">Amallar</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map(lead => (
                  <tr
                    key={lead.id}
                    className="border-b border-gray-800/50 hover:bg-gray-800/50 cursor-pointer transition"
                    onClick={() => { setSelected(lead); setEditNotes(lead.notes || ""); }}
                  >
                    <td className="p-4 font-medium text-white">{lead.name}</td>
                    <td className="p-4 text-gray-300 font-mono">{lead.phone || "—"}</td>
                    <td className="p-4 text-gray-400">{lead.niche}</td>
                    <td className="p-4">
                      <span className={`${SCORE_COLORS[lead.score]} text-white text-xs px-2 py-1 rounded-full font-medium`}>
                        {lead.score}
                      </span>
                    </td>
                    <td className="p-4">
                      <span className={`${STATUS_COLORS[lead.status]} text-white text-xs px-2 py-1 rounded-full font-medium`}>
                        {lead.status}
                      </span>
                    </td>
                    <td className="p-4" onClick={e => e.stopPropagation()}>
                      <div className="flex gap-2">
                        {lead.phone && (
                          <a
                            href={`https://wa.me/${lead.phone.replace(/\D/g, "")}`}
                            target="_blank"
                            className="bg-green-700 hover:bg-green-600 px-2 py-1 rounded text-xs transition"
                          >
                            WA
                          </a>
                        )}
                        <button
                          onClick={() => buildWebsite(lead)}
                          className="bg-indigo-700 hover:bg-indigo-600 px-2 py-1 rounded text-xs transition"
                        >
                          Build
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* Lead Detail Modal */}
        {selected && (
          <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4" onClick={() => setSelected(null)}>
            <div className="bg-gray-900 border border-gray-700 rounded-2xl p-6 w-full max-w-lg" onClick={e => e.stopPropagation()}>
              <h2 className="text-xl font-bold text-white mb-4">{selected.name}</h2>
              <div className="space-y-3 text-sm">
                <div className="flex justify-between"><span className="text-gray-400">Telefon</span><span className="text-white font-mono">{selected.phone || "—"}</span></div>
                <div className="flex justify-between"><span className="text-gray-400">Niche</span><span className="text-white">{selected.niche}</span></div>
                <div className="flex justify-between"><span className="text-gray-400">Manzil</span><span className="text-white">{selected.address || "—"}</span></div>
                <div className="flex justify-between"><span className="text-gray-400">Sayt</span><span className="text-blue-400">{selected.website || "—"}</span></div>
              </div>

              <div className="mt-4 grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs text-gray-400 mb-1 block">Status</label>
                  <select
                    value={selected.status}
                    onChange={e => updateLead(selected.id, { status: e.target.value as Lead["status"] })}
                    className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm"
                  >
                    {["New", "Contacted", "Qualified", "Won", "Lost"].map(s => <option key={s}>{s}</option>)}
                  </select>
                </div>
                <div>
                  <label className="text-xs text-gray-400 mb-1 block">Score</label>
                  <select
                    value={selected.score}
                    onChange={e => updateLead(selected.id, { score: e.target.value as Lead["score"] })}
                    className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm"
                  >
                    {["Hot", "Warm", "Cold"].map(s => <option key={s}>{s}</option>)}
                  </select>
                </div>
              </div>

              <div className="mt-4">
                <label className="text-xs text-gray-400 mb-1 block">Izohlar</label>
                <textarea
                  value={editNotes}
                  onChange={e => setEditNotes(e.target.value)}
                  rows={3}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm resize-none"
                />
              </div>

              <div className="flex gap-3 mt-4">
                <button
                  onClick={() => { updateLead(selected.id, { notes: editNotes }); setSelected(null); }}
                  className="flex-1 bg-indigo-600 hover:bg-indigo-500 py-2 rounded-lg text-sm font-medium transition"
                >
                  Saqlash
                </button>
                <button
                  onClick={() => buildWebsite(selected)}
                  className="flex-1 bg-green-700 hover:bg-green-600 py-2 rounded-lg text-sm font-medium transition"
                >
                  Sayt yaratish
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
