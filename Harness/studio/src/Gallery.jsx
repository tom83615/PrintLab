import React,{useEffect,useState} from 'react';
import {Box,ArrowUpRight,Search} from 'lucide-react';
import './gallery.css';

const when=t=>t&&!Number.isNaN(+new Date(t))?new Intl.DateTimeFormat('zh-TW',{year:'numeric',month:'short',day:'numeric'}).format(new Date(t)):'時間未知';
const state={completed:'設備報告完成',failed:'列印失敗',printing:'列印中',paused:'已暫停',unresolved:'狀態待核對',cancelled:'已取消'};
const previewLabels = {sliced_plate: '切片模型預覽', cloud_plate: '設定板預覽', reference_plate: '原模型參考', reference_model: '原模型參考'};
export default function Gallery({onNavigate}){
 const [data,setData]=useState(null),[error,setError]=useState(''),[query,setQuery]=useState('');
 useEffect(()=>{let live=true;const load=()=>fetch('/api/history',{cache:'no-store'}).then(r=>{if(!r.ok)throw Error('記錄暫不可用');return r.json()}).then(d=>{if(live){setData(d);setError('')}}).catch(()=>live&&setError('無法讀取列印記錄'));load();addEventListener('printlab:refresh',load);return()=>{live=false;removeEventListener('printlab:refresh',load)}},[]);
 const rows=(data?.items||[]).filter(r=>r.is_print_event).filter(r=>`${r.name} ${r.project_name||''}`.toLowerCase().includes(query.toLowerCase()));
 return <section className="gallery-section" aria-label="列印模型圖冊"><div className="section-heading gallery-heading"><div><span className="eyebrow">PRINTED MODELS</span><h2>我的列印圖冊</h2><p>從最近一次開始，向下瀏覽列印記錄。</p></div><label className="search-box"><Search size={18}/><input value={query} onChange={e=>setQuery(e.target.value)} placeholder="搜尋模型" aria-label="搜尋列印模型"/></label></div>
 <p className="gallery-note">當次切片、設定板預覽與原模型參考分別標記。設定板和參考圖的當次配色及修改尚未核實。{data?.coverage?.cloud_history_synced===false?' 此頁展示 Bambuddy 已捕獲的記錄。':''}{data?.stale?' 連接中斷，顯示上次記錄。':''}</p>
 {error?<div className="quiet-empty">{error}</div>:!data?<div className="quiet-empty">正在讀取列印記錄…</div>:rows.length?<div className="gallery-grid">{rows.map(r=><article className="gallery-card" key={r.id}><div className="gallery-cover">{r.model_preview?.url?<img src={r.model_preview.url} loading="lazy" alt={`${r.name}的模型預覽`}/>:<div className="gallery-missing"><Box size={30} strokeWidth={1.2}/><span>模型預覽待找回</span></div>}<span className="gallery-badge">{previewLabels[r.model_preview?.kind] || (r.model_preview ? '模型預覽' : '無模型預覽')}</span></div><div className="gallery-card-content"><h3>{r.project_name||r.name}</h3>{r.project_name&&r.name!==r.project_name&&<p className="gallery-job">{r.name}</p>}<p>{when(r.started_at||r.created_at)} · {state[r.status]||r.status||'狀態未知'}</p><div className="gallery-links">{r.project_id&&<button onClick={()=>onNavigate(`projects/${r.project_id}`)}>查看專案 <ArrowUpRight size={15}/></button>}{r.makerworld_url&&<a href={r.makerworld_url} target="_blank" rel="noreferrer">原模型頁面 <ArrowUpRight size={15}/></a>}</div></div></article>)}</div>:<div className="quiet-empty">{query?'沒有找到符合條件的列印記錄。':(data?.state === 'unconfigured' ? data.message : '還沒有捕獲到列印記錄。')}</div>}</section>
}
