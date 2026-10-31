import { useState, useEffect } from "react";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";
const examples = [
  "What is the total revenue?",
  "Which product generated the highest revenue?",
  "What is the monthly revenue trend?",
  "Which region generated the highest sales?",
  "How did revenue change between January and February?",
];

export default function App() {
  const [q, setQ] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [status, setStatus] = useState(null);

  useEffect(() => {
    fetch(`${API}/api/data-status`).then(r=>r.json()).then(setStatus).catch(()=>setError("Cannot reach backend"));
  }, []);

  async function submit(question) {
    const text = question || q;
    if (!text.trim()) return;
    setLoading(true); setError(""); setResult(null);
    try {
      const r = await fetch(`${API}/api/ask`, { method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({question:text}) });
      if (!r.ok) throw new Error((await r.json()).detail || "Request failed");
      setResult(await r.json());
    } catch (e) { setError(e.message); }
    finally { setLoading(false); }
  }

  return (
    <div style={{minHeight:"100vh",background:"linear-gradient(135deg,#0f172a,#1e293b)",color:"#e2e8f0",fontFamily:"Inter,system-ui",padding:24}}>
      <div style={{maxWidth:960,margin:"0 auto"}}>
        <h1 style={{fontSize:32,marginBottom:4}}>Mini AI Business Intelligence Assistant</h1>
        <p style={{color:"#94a3b8",marginBottom:24}}>Ask questions about sales data</p>
        {status && <div style={{background:"#1e293b",padding:12,borderRadius:8,marginBottom:16}}>Records loaded: {status.records_loaded}</div>}
        <div style={{display:"flex",gap:8,marginBottom:12}}>
          <input value={q} onChange={e=>setQ(e.target.value)} placeholder="Ask a question..." style={{flex:1,padding:12,borderRadius:8,border:"1px solid #334155",background:"#0f172a",color:"#e2e8f0"}} />
          <button onClick={()=>submit()} disabled={loading} style={{padding:"12px 20px",borderRadius:8,border:"none",background:"#3b82f6",color:"white",cursor:"pointer"}}>Ask</button>
        </div>
        <div style={{display:"flex",flexWrap:"wrap",gap:8,marginBottom:20}}>
          {examples.map(ex=> <button key={ex} onClick={()=>{setQ(ex);submit(ex);}} style={{fontSize:12,padding:"6px 10px",borderRadius:6,border:"1px solid #334155",background:"#1e293b",color:"#e2e8f0",cursor:"pointer"}}>{ex}</button>)}
        </div>
        {loading && <p>Loading...</p>}
        {error && <p style={{color:"#f87171"}}>{error}</p>}
        {result && (
          <div style={{background:"#1e293b",padding:20,borderRadius:12}}>
            <h2 style={{marginTop:0}}>{result.operation}</h2>
            <p>{result.answer}</p>
            <pre style={{background:"#0f172a",padding:12,borderRadius:8,overflow:"auto"}}>{JSON.stringify(result.metrics,null,2)}</pre>
            {result.supporting_data?.length>0 && (
              <table style={{width:"100%",borderCollapse:"collapse",marginTop:12}}>
                <thead><tr>{Object.keys(result.supporting_data[0]).map(k=><th key={k} style={{textAlign:"left",padding:8,borderBottom:"1px solid #334155"}}>{k}</th>)}</tr></thead>
                <tbody>{result.supporting_data.map((row,i)=><tr key={i}>{Object.values(row).map((v,j)=><td key={j} style={{padding:8,borderBottom:"1px solid #1e293b"}}>{String(v)}</td>)}</tr>)}</tbody>
              </table>
            )}
            <p style={{fontSize:12,color:"#64748b",marginTop:12}}>AI mode: {result.ai?.mode}</p>
          </div>
        )}
      </div>
    </div>
  );
}
