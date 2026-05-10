'use client';

import { useState, useEffect, useCallback } from 'react';
import {
  getMondayOfWeek, addDays, toISO, formatHE, weekStatus, STATUS_LABELS,
} from '@/lib/dates';

// ── Types ──────────────────────────────────────────────────────────────
type Assignment = { id: number; week_monday: string; position: string; soldier_name: string };
type Position   = { id: number; name: string; sort_order: number };
type Tab = 'board' | 'search' | 'assign' | 'manage';

const ADMIN_PASSWORD = process.env.NEXT_PUBLIC_ADMIN_PASSWORD || '1234';

// ── Helpers ────────────────────────────────────────────────────────────
const statusColor: Record<string, string> = {
  past: '#22c55e', current: '#60a5fa', future: '#f97316',
};
const statusBg: Record<string, string> = {
  past: 'rgba(34,197,94,0.1)', current: 'rgba(96,165,250,0.1)', future: 'rgba(249,115,22,0.1)',
};

// ── Main Component ─────────────────────────────────────────────────────
export default function Home() {
  const [tab, setTab] = useState<Tab>('board');
  const [weekOffset, setWeekOffset] = useState(0);
  const [isAdmin, setIsAdmin] = useState(false);
  const [positions, setPositions] = useState<Position[]>([]);
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [allAssignments, setAllAssignments] = useState<Assignment[]>([]);
  const [loading, setLoading] = useState(true);

  // Admin state
  const [pwdInput, setPwdInput] = useState('');
  const [pwdError, setPwdError] = useState('');
  const [pendingTab, setPendingTab] = useState<Tab | null>(null);

  // Assign tab state
  const [selPos, setSelPos] = useState('');
  const [soldierName, setSoldierName] = useState('');
  const [assignMsg, setAssignMsg] = useState<{ text: string; type: 'ok' | 'err' } | null>(null);

  // Manage tab state
  const [newPosName, setNewPosName] = useState('');
  const [manageMsg, setManageMsg] = useState<{ text: string; type: 'ok' | 'err' } | null>(null);

  // Search state
  const [searchQ, setSearchQ] = useState('');

  const monday = addDays(getMondayOfWeek(new Date()), weekOffset * 7);
  const weekKey = toISO(monday);
  const sunday = addDays(monday, 6);
  const status = weekStatus(monday);

  // ── Data fetching ────────────────────────────────────────────────────
  const fetchPositions = useCallback(async () => {
    const res = await fetch('/api/positions');
    const data = await res.json();
    setPositions(Array.isArray(data) ? data : []);
  }, []);

  const fetchWeek = useCallback(async (key: string) => {
    setLoading(true);
    const res = await fetch(`/api/assignments?week=${key}`);
    const data = await res.json();
    setAssignments(Array.isArray(data) ? data : []);
    setLoading(false);
  }, []);

  const fetchAll = useCallback(async () => {
    const res = await fetch('/api/assignments');
    const data = await res.json();
    setAllAssignments(Array.isArray(data) ? data : []);
  }, []);

  useEffect(() => { fetchPositions(); fetchAll(); }, [fetchPositions, fetchAll]);
  useEffect(() => { fetchWeek(weekKey); }, [weekKey, fetchWeek]);

  // ── Derived data ─────────────────────────────────────────────────────
  const assignmentMap: Record<string, string> = {};
  assignments.forEach(a => { assignmentMap[a.position] = a.soldier_name; });

  // Sync selPos when positions load
  useEffect(() => {
    if (positions.length > 0 && !selPos) setSelPos(positions[0].name);
  }, [positions, selPos]);

  // Sync soldier name when selPos changes in assign tab
  useEffect(() => {
    setSoldierName(assignmentMap[selPos] || '');
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selPos, weekKey, assignments]);

  // ── Handlers ─────────────────────────────────────────────────────────
  function goTab(t: Tab) {
    if ((t === 'assign' || t === 'manage') && !isAdmin) {
      setPendingTab(t);
      setTab('login' as Tab);
      return;
    }
    setTab(t);
    if (t === 'search') fetchAll();
  }

  function tryLogin() {
    if (pwdInput === ADMIN_PASSWORD) {
      setIsAdmin(true);
      setPwdInput('');
      setPwdError('');
      setTab(pendingTab || 'assign');
      setPendingTab(null);
    } else {
      setPwdError('סיסמה שגויה');
    }
  }

  function logout() {
    setIsAdmin(false);
    setTab('board');
  }

  async function saveAssignment() {
    if (!soldierName.trim()) { setAssignMsg({ text: 'יש להזין שם', type: 'err' }); return; }
    await fetch('/api/assignments', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ week_monday: weekKey, position: selPos, soldier_name: soldierName.trim() }),
    });
    await fetchWeek(weekKey);
    await fetchAll();
    setAssignMsg({ text: `נשמר: ${soldierName.trim()} ← ${selPos}`, type: 'ok' });
    setTimeout(() => setAssignMsg(null), 3000);
  }

  async function clearAssignment() {
    await fetch('/api/assignments', {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ week_monday: weekKey, position: selPos }),
    });
    await fetchWeek(weekKey);
    await fetchAll();
    setSoldierName('');
    setAssignMsg({ text: 'השיבוץ נמחק', type: 'err' });
    setTimeout(() => setAssignMsg(null), 3000);
  }

  async function addPosition() {
    if (!newPosName.trim()) return;
    await fetch('/api/positions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: newPosName.trim() }),
    });
    setNewPosName('');
    await fetchPositions();
    setManageMsg({ text: `עמדה נוספה: ${newPosName.trim()}`, type: 'ok' });
    setTimeout(() => setManageMsg(null), 3000);
  }

  async function removePosition(id: number) {
    await fetch('/api/positions', {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id }),
    });
    await fetchPositions();
  }

  async function resetPositions() {
    if (!confirm('לאפס את רשימת העמדות למקורית?')) return;
    await fetch('/api/positions', { method: 'PUT' });
    await fetchPositions();
    setManageMsg({ text: 'הרשימה אופסה', type: 'ok' });
    setTimeout(() => setManageMsg(null), 3000);
  }

  // ── Search results ───────────────────────────────────────────────────
  const searchResults = searchQ.trim()
    ? allAssignments.filter(a =>
        a.soldier_name.toLowerCase().includes(searchQ.trim().toLowerCase()))
      .sort((a, b) => b.week_monday.localeCompare(a.week_monday))
    : [];

  // ── Render ────────────────────────────────────────────────────────────
  return (
    <>
      <style>{`
        .app { max-width: 800px; margin: 0 auto; padding: 1.5rem 1rem 3rem; }
        .header {
          background: linear-gradient(135deg, #0d2040 0%, #162e55 50%, #0d2040 100%);
          border: 1px solid var(--border-em);
          border-radius: var(--r-lg);
          padding: 1.5rem 2rem;
          margin-bottom: 1.5rem;
          text-align: center;
          position: relative;
          overflow: hidden;
        }
        .header::before {
          content: '';
          position: absolute;
          inset: 0;
          background: radial-gradient(ellipse 60% 80% at 50% -20%, rgba(59,130,246,0.18), transparent);
          pointer-events: none;
        }
        .header h1 {
          font-family: 'Rubik', sans-serif;
          font-size: 1.75rem;
          font-weight: 900;
          color: var(--text);
          position: relative;
        }
        .header p { color: var(--text2); font-size: 0.9rem; margin-top: 4px; position: relative; }
        .tabs {
          display: flex;
          gap: 4px;
          background: var(--bg2);
          border: 1px solid var(--border);
          border-radius: var(--r);
          padding: 4px;
          margin-bottom: 1.25rem;
        }
        .tab-btn {
          flex: 1;
          padding: 9px 4px;
          font-size: 0.85rem;
          font-weight: 600;
          border: none;
          border-radius: 9px;
          background: transparent;
          color: var(--text2);
          transition: all 0.2s;
        }
        .tab-btn:hover { color: var(--text); background: rgba(255,255,255,0.04); }
        .tab-btn.active { background: var(--accent); color: #fff; box-shadow: 0 2px 12px rgba(59,130,246,0.4); }
        .card {
          background: var(--card);
          border: 1px solid var(--border);
          border-radius: var(--r-lg);
          padding: 1.25rem 1.5rem;
          margin-bottom: 1rem;
          backdrop-filter: blur(8px);
        }
        .card-title {
          font-size: 0.85rem;
          font-weight: 700;
          color: var(--text2);
          text-transform: uppercase;
          letter-spacing: 0.06em;
          margin-bottom: 1rem;
          padding-bottom: 0.75rem;
          border-bottom: 1px solid var(--border);
        }
        .week-nav {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 1rem;
        }
        .week-info { flex: 1; text-align: center; }
        .week-dates { font-size: 1rem; font-weight: 700; font-family: 'Rubik', sans-serif; }
        .week-badge {
          display: inline-block;
          padding: 2px 12px;
          border-radius: 20px;
          font-size: 0.72rem;
          font-weight: 700;
          margin-top: 4px;
        }
        .nav-btn {
          padding: 7px 14px;
          font-size: 0.82rem;
          font-weight: 600;
          background: var(--card);
          border: 1px solid var(--border);
          border-radius: var(--r);
          color: var(--text2);
          transition: all 0.15s;
        }
        .nav-btn:hover { border-color: var(--border-em); color: var(--text); }
        .today-btn { background: var(--accent-dim); border-color: var(--border-em); color: var(--accent2); }

        /* Table */
        table { width: 100%; border-collapse: collapse; font-size: 0.88rem; }
        th {
          text-align: right;
          padding: 10px 12px;
          color: var(--text3);
          font-size: 0.75rem;
          font-weight: 700;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          border-bottom: 1px solid var(--border);
        }
        td { padding: 11px 12px; border-bottom: 1px solid rgba(255,255,255,0.04); vertical-align: middle; }
        tr:last-child td { border-bottom: none; }
        tr:hover td { background: rgba(59,130,246,0.04); }
        .pos-name { font-weight: 600; color: var(--accent2); }
        .assigned-name { color: #4ade80; font-weight: 600; }
        .empty-name { color: var(--text3); }

        /* Form */
        .form-row { display: flex; gap: 8px; margin-bottom: 0.75rem; align-items: flex-end; }
        .form-group { flex: 1; }
        .form-group label { display: block; font-size: 0.78rem; font-weight: 600; color: var(--text2); margin-bottom: 5px; }
        .form-input, .form-select {
          width: 100%;
          padding: 9px 12px;
          font-size: 0.88rem;
          background: var(--bg3);
          border: 1px solid var(--border);
          border-radius: var(--r);
          color: var(--text);
          transition: border-color 0.15s;
        }
        .form-input:focus, .form-select:focus { outline: none; border-color: var(--accent); }
        .btn { padding: 9px 18px; font-size: 0.84rem; font-weight: 700; border-radius: var(--r); border: none; transition: all 0.15s; }
        .btn-primary { background: var(--accent); color: #fff; box-shadow: 0 2px 10px rgba(59,130,246,0.3); }
        .btn-primary:hover { background: var(--accent2); transform: translateY(-1px); }
        .btn-danger { background: var(--red-dim); border: 1px solid rgba(239,68,68,0.3); color: #f87171; }
        .btn-danger:hover { background: rgba(239,68,68,0.18); }
        .btn-ghost { background: var(--card); border: 1px solid var(--border); color: var(--text2); }
        .btn-ghost:hover { border-color: var(--border-em); color: var(--text); }

        /* Messages */
        .msg { padding: 10px 14px; border-radius: var(--r); font-size: 0.84rem; margin-bottom: 0.75rem; }
        .msg-ok { background: var(--green-dim); border: 1px solid rgba(34,197,94,0.3); color: #4ade80; }
        .msg-err { background: var(--red-dim); border: 1px solid rgba(239,68,68,0.3); color: #f87171; }
        .msg-info { background: var(--accent-dim); border: 1px solid var(--border-em); color: var(--accent2); }
        .msg-warn { background: var(--orange-dim); border: 1px solid rgba(249,115,22,0.3); color: #fb923c; }

        /* Admin bar */
        .admin-bar {
          display: flex; align-items: center; justify-content: space-between;
          padding: 8px 14px; background: rgba(59,130,246,0.08);
          border: 1px solid var(--border-em); border-radius: var(--r);
          margin-bottom: 1rem; font-size: 0.82rem; color: var(--accent2);
          font-weight: 600;
        }

        /* Position list */
        .pos-item {
          display: flex; align-items: center; gap: 10px;
          padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.05);
          font-size: 0.88rem;
        }
        .pos-item:last-child { border-bottom: none; }
        .pos-item-name { flex: 1; font-weight: 600; }
        .del-btn {
          width: 28px; height: 28px; border-radius: 8px; border: 1px solid rgba(239,68,68,0.25);
          background: var(--red-dim); color: #f87171; font-size: 0.8rem; display: flex;
          align-items: center; justify-content: center;
        }
        .del-btn:hover { background: rgba(239,68,68,0.2); }

        /* Login */
        .lock-screen { text-align: center; padding: 2.5rem 1rem; }
        .lock-icon { font-size: 2.5rem; margin-bottom: 1rem; }
        .lock-form { display: flex; gap: 8px; justify-content: center; margin-top: 1rem; }
        .lock-form .form-input { max-width: 180px; }

        /* Current assignment display */
        .current-asgn {
          background: var(--bg3); border: 1px solid var(--border); border-radius: var(--r);
          padding: 10px 14px; margin-bottom: 0.75rem; font-size: 0.84rem; color: var(--text2);
        }
        .current-asgn strong { color: #4ade80; }

        .no-data { text-align: center; padding: 2rem; color: var(--text3); font-size: 0.85rem; }
        .spinner { text-align: center; padding: 2rem; color: var(--text3); }
        .summary-count {
          background: var(--accent-dim); color: var(--accent2);
          border-radius: 20px; padding: 2px 10px; font-size: 0.75rem; font-weight: 700;
          margin-right: 8px;
        }
      `}</style>

      <div className="app">
        {/* ── Header ── */}
        <div className="header">
          <h1>🛡️ מערכת ניהול תורנויות</h1>
          <p>גזרה אזרחית &nbsp;•&nbsp; ניהול ורישום שיבוצים</p>
        </div>

        {/* ── Tabs ── */}
        <div className="tabs">
          <button className={`tab-btn${tab === 'board' ? ' active' : ''}`} onClick={() => goTab('board')}>📋 לוח תורנויות</button>
          <button className={`tab-btn${tab === 'search' ? ' active' : ''}`} onClick={() => goTab('search')}>🔍 חיפוש</button>
          <button className={`tab-btn${tab === 'assign' || (tab === ('login' as Tab) && pendingTab === 'assign') ? ' active' : ''}`} onClick={() => goTab('assign')}>✏️ שיבוץ</button>
          <button className={`tab-btn${tab === 'manage' || (tab === ('login' as Tab) && pendingTab === 'manage') ? ' active' : ''}`} onClick={() => goTab('manage')}>⚙️ עמדות</button>
        </div>

        {/* ══ BOARD TAB ══ */}
        {tab === 'board' && (
          <>
            <WeekNav monday={monday} status={status} onPrev={() => setWeekOffset(o => o - 1)} onNext={() => setWeekOffset(o => o + 1)} onToday={() => setWeekOffset(0)} />
            <div className="card">
              <div className="card-title">
                📋 לוח תורנויות — {formatHE(monday)} עד {formatHE(sunday)}
              </div>
              {loading ? (
                <div className="spinner">טוען...</div>
              ) : (
                <table>
                  <thead>
                    <tr><th>עמדה</th><th>חייל משובץ</th></tr>
                  </thead>
                  <tbody>
                    {positions.map(p => (
                      <tr key={p.id}>
                        <td className="pos-name">{p.name}</td>
                        <td>
                          {assignmentMap[p.name]
                            ? <span className="assigned-name">{assignmentMap[p.name]}</span>
                            : <span className="empty-name">—</span>}
                        </td>
                      </tr>
                    ))}
                    {positions.length === 0 && <tr><td colSpan={2} className="no-data">אין עמדות</td></tr>}
                  </tbody>
                </table>
              )}
            </div>
          </>
        )}

        {/* ══ SEARCH TAB ══ */}
        {tab === 'search' && (
          <div className="card">
            <div className="card-title">🔍 חיפוש תורנויות לפי שם</div>
            <div className="form-row" style={{ marginBottom: '1rem' }}>
              <div className="form-group">
                <label>שם מלא או חלקי</label>
                <input className="form-input" type="text" placeholder="לדוגמה: כהן" value={searchQ} onChange={e => setSearchQ(e.target.value)} />
              </div>
            </div>
            {searchQ.trim() && (
              searchResults.length === 0 ? (
                <div className="msg msg-err">לא נמצאו תורנויות עבור &ldquo;{searchQ}&rdquo;</div>
              ) : (
                <>
                  <div className="msg msg-ok">נמצאו {searchResults.length} תורנויות</div>
                  <table>
                    <thead><tr><th>שבוע</th><th>עמדה</th><th>חייל</th><th>סטטוס</th></tr></thead>
                    <tbody>
                      {searchResults.map(a => {
                        const mon = new Date(a.week_monday + 'T00:00:00');
                        const st = weekStatus(mon);
                        return (
                          <tr key={a.id}>
                            <td style={{ fontSize: '0.8rem', color: 'var(--text2)' }}>{formatHE(mon)} – {formatHE(addDays(mon, 6))}</td>
                            <td className="pos-name" style={{ fontSize: '0.82rem' }}>{a.position}</td>
                            <td><strong style={{ color: '#4ade80' }}>{a.soldier_name}</strong></td>
                            <td>
                              <span style={{ background: statusBg[st], color: statusColor[st], borderRadius: '20px', padding: '3px 10px', fontSize: '0.72rem', fontWeight: 700 }}>
                                {STATUS_LABELS[st]}
                              </span>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </>
              )
            )}
          </div>
        )}

        {/* ══ LOGIN (inline) ══ */}
        {(tab as string) === 'login' && (
          <div className="card">
            <div className="lock-screen">
              <div className="lock-icon">🔒</div>
              <div style={{ color: 'var(--text2)', fontSize: '0.95rem', marginBottom: '0.5rem' }}>כניסת מנהל</div>
              <div className="lock-form">
                <input
                  className="form-input"
                  type="password"
                  placeholder="סיסמה"
                  value={pwdInput}
                  onChange={e => setPwdInput(e.target.value)}
                  onKeyDown={e => e.key === 'Enter' && tryLogin()}
                />
                <button className="btn btn-primary" onClick={tryLogin}>כניסה</button>
              </div>
              {pwdError && <div style={{ color: '#f87171', fontSize: '0.82rem', marginTop: '0.5rem' }}>{pwdError}</div>}
            </div>
          </div>
        )}

        {/* ══ ASSIGN TAB ══ */}
        {tab === 'assign' && isAdmin && (
          <>
            <div className="admin-bar">
              <span>✅ מנהל מחובר</span>
              <button className="btn btn-ghost" style={{ padding: '5px 12px', fontSize: '0.78rem' }} onClick={logout}>התנתק</button>
            </div>
            <WeekNav monday={monday} status={status} onPrev={() => setWeekOffset(o => o - 1)} onNext={() => setWeekOffset(o => o + 1)} onToday={() => setWeekOffset(0)} />
            <div className="card">
              <div className="card-title">✏️ שיבוץ חייל לעמדה</div>
              <div className="form-row">
                <div className="form-group">
                  <label>עמדה</label>
                  <select className="form-select" value={selPos} onChange={e => setSelPos(e.target.value)}>
                    {positions.map(p => <option key={p.id} value={p.name}>{p.name}</option>)}
                  </select>
                </div>
              </div>
              <div className="current-asgn">
                {assignmentMap[selPos]
                  ? <>שיבוץ נוכחי: <strong>{assignmentMap[selPos]}</strong></>
                  : <span style={{ color: 'var(--text3)' }}>אין שיבוץ לעמדה זו עדיין</span>}
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>שם החייל</label>
                  <input className="form-input" type="text" placeholder="שם מלא" value={soldierName} onChange={e => setSoldierName(e.target.value)} onKeyDown={e => e.key === 'Enter' && saveAssignment()} />
                </div>
                <button className="btn btn-primary" style={{ alignSelf: 'flex-end', whiteSpace: 'nowrap' }} onClick={saveAssignment}>💾 שמור</button>
                <button className="btn btn-danger" style={{ alignSelf: 'flex-end', whiteSpace: 'nowrap' }} onClick={clearAssignment}>🗑️ נקה</button>
              </div>
              {assignMsg && <div className={`msg msg-${assignMsg.type}`}>{assignMsg.text}</div>}
            </div>

            {/* Summary */}
            <div className="card">
              <div className="card-title">
                📋 סיכום שיבוצים
                <span className="summary-count">{Object.keys(assignmentMap).length} מתוך {positions.length}</span>
              </div>
              {loading ? <div className="spinner">טוען...</div> : (
                <table>
                  <thead><tr><th>עמדה</th><th>חייל משובץ</th></tr></thead>
                  <tbody>
                    {positions.filter(p => assignmentMap[p.name]).map(p => (
                      <tr key={p.id}>
                        <td className="pos-name">{p.name}</td>
                        <td className="assigned-name">{assignmentMap[p.name]}</td>
                      </tr>
                    ))}
                    {Object.keys(assignmentMap).length === 0 && (
                      <tr><td colSpan={2} className="no-data">אין שיבוצים לשבוע זה</td></tr>
                    )}
                  </tbody>
                </table>
              )}
            </div>
          </>
        )}

        {/* ══ MANAGE TAB ══ */}
        {tab === 'manage' && isAdmin && (
          <>
            <div className="admin-bar">
              <span>✅ מנהל מחובר</span>
              <button className="btn btn-ghost" style={{ padding: '5px 12px', fontSize: '0.78rem' }} onClick={logout}>התנתק</button>
            </div>
            <div className="card">
              <div className="card-title">⚙️ רשימת עמדות ({positions.length})</div>
              {positions.map(p => (
                <div key={p.id} className="pos-item">
                  <span className="pos-item-name">{p.name}</span>
                  <button className="del-btn" onClick={() => removePosition(p.id)} title="מחק">✕</button>
                </div>
              ))}
              {positions.length === 0 && <div className="no-data">אין עמדות</div>}
            </div>
            <div className="card">
              <div className="card-title">➕ הוספת עמדה חדשה</div>
              <div className="form-row">
                <div className="form-group">
                  <label>שם העמדה</label>
                  <input className="form-input" type="text" placeholder='לדוגמה: ש"ג מחנה' value={newPosName} onChange={e => setNewPosName(e.target.value)} onKeyDown={e => e.key === 'Enter' && addPosition()} />
                </div>
                <button className="btn btn-primary" style={{ alignSelf: 'flex-end' }} onClick={addPosition}>➕ הוסף</button>
              </div>
              {manageMsg && <div className={`msg msg-${manageMsg.type}`}>{manageMsg.text}</div>}
            </div>
            <div className="card">
              <div className="card-title">🔄 איפוס לרשימה המקורית</div>
              <div className="msg msg-warn" style={{ marginBottom: '0.75rem' }}>⚠️ פעולה זו תמחק את כל השינויים ותחזיר את רשימת העמדות למצב המקורי.</div>
              <button className="btn btn-danger" onClick={resetPositions}>אפס לרשימה המקורית</button>
            </div>
          </>
        )}

        {/* ── Footer ── */}
        <div style={{ textAlign: 'center', marginTop: '2.5rem', color: 'var(--text3)', fontSize: '0.78rem', borderTop: '1px solid var(--border)', paddingTop: '1.5rem' }}>
          <div style={{ color: 'var(--gold)', fontWeight: 800, fontFamily: 'Rubik, sans-serif', marginBottom: '4px' }}>🛡️ נוצר על ידי ניתאי כהן</div>
          <div style={{ direction: 'ltr', letterSpacing: '1px' }}>053-444-4494</div>
        </div>
      </div>
    </>
  );
}

// ── WeekNav component ─────────────────────────────────────────────────
function WeekNav({ monday, status, onPrev, onNext, onToday }: {
  monday: Date; status: string;
  onPrev: () => void; onNext: () => void; onToday: () => void;
}) {
  const sunday = addDays(monday, 6);
  return (
    <div className="week-nav">
      <button className="nav-btn" onClick={onPrev}>◀ קודם</button>
      <div className="week-info">
        <div className="week-dates">{formatHE(monday)} – {formatHE(sunday)}</div>
        <div>
          <span className="week-badge" style={{ background: statusBg[status], color: statusColor[status] }}>
            {STATUS_LABELS[status]}
          </span>
        </div>
      </div>
      <button className="nav-btn today-btn" onClick={onToday}>היום</button>
      <button className="nav-btn" onClick={onNext}>הבא ▶</button>
    </div>
  );
}
