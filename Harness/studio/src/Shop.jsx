import React,{useEffect,useState} from 'react';
import {ShoppingBag,ArrowUpRight,ArrowLeft,Copy,Check,Search,Package} from 'lucide-react';

const statusNames={unverified:'待核實',needed:'待購',owned:'已有',purchased:'已購',settled:'已用 / 餘料'};
const supplierNames={available:'創客寶庫 · 可購買',unavailable:'創客寶庫 · 不可購買',unverified:'創客寶庫 · 尚未核實'};
const qty=(n,unit)=>n==null?'待核實':`${n} ${unit}`;
const safeLink=url=>{try{const u=new URL(url);return u.protocol==='https:'&&!u.username&&!u.password?u.href:null}catch{return null}};

export default function Shop({projectId,onNavigate}){
 const [data,setData]=useState(null),[error,setError]=useState(''),[query,setQuery]=useState(''),[filter,setFilter]=useState('all'),[copied,setCopied]=useState(null),[copyText,setCopyText]=useState('');
 useEffect(()=>{let active=true;setData(null);setError('');const load=()=>fetch('/api/shop'+(projectId?'?project='+encodeURIComponent(projectId):''),{cache:'no-store'}).then(r=>{if(!r.ok)throw Error('購物清單暫時無法讀取');return r.json()}).then(d=>{if(active){setData(d);setError('')}}).catch(e=>active&&setError(e.message));load();addEventListener('printlab:refresh',load);return()=>{active=false;removeEventListener('printlab:refresh',load)}},[projectId]);
 async function copy(item){const prompt=`請載入 當前 PrintLab 專案根目錄的 AGENTS.md 和 printlab shop list。我要更新配件 ${item.id}（${item.name}）的庫存或購買記錄。請先向我核對具體數量，再通過共享 shop 命令儲存；已有與已購不重複計數，不下單、不列印。`;try{await navigator.clipboard.writeText(prompt);setCopied(item.id)}catch{setCopyText(prompt)}}
 const rows=(data?.items||[]).filter(r=>(filter==='all'||r.status===filter)&&`${r.name} ${JSON.stringify(r.specification)} ${r.sources.map(s=>s.project_name).join(' ')}`.toLowerCase().includes(query.toLowerCase()));
 const project=projectId?data?.projects?.[projectId]:null;
 return <div className="shop-page">{projectId&&<button className="breadcrumb" onClick={()=>onNavigate('shop')}><ArrowLeft size={16}/>全部購物清單</button>}
 <header className="page-heading"><div><span className="eyebrow">SHOP LIST</span><h1>{projectId?'專案配件':'購物清單'}</h1><p>{projectId?(project?.name||projectId):'把確定要做的作品所需配件，攢在一起買。'}</p></div><span className="heading-count">{data?.items?.length??'—'}<small>種配件</small></span></header>
 <div className="shop-intro"><ShoppingBag size={24}/><div><strong>規格相同，合併採購</strong><p>已有與已購只計算一次；庫存不清楚時先核實。製作決定會加入清單，列印仍需單獨確認。</p></div></div>
 {projectId&&!project&&data&&<div className="quiet-empty">尚未記錄這個專案的製作決定。明確要做以後，Agent 會檢查配件並同步到這裡。</div>}
 {Object.values(data?.projects||{}).filter(p=>!p.parts_reviewed).map(p=><div className="shop-pending" key={p.id}><span>{p.name} · 已決定製作，配件待梳理</span><button className="text-link" onClick={()=>onNavigate(`projects/${p.id}`)}>查看專案<ArrowUpRight size={16}/></button></div>)}
 <div className="collection-toolbar"><div className="filter-tabs scroll-tabs" role="group" aria-label="購物狀態"><button aria-pressed={filter==='all'} className={filter==='all'?'selected':''} onClick={()=>setFilter('all')}>全部</button>{Object.entries(statusNames).map(([value,name])=><button key={value} aria-pressed={filter===value} className={filter===value?'selected':''} onClick={()=>setFilter(value)}>{name}{data?.counts?.[value]>0?` ${data.counts[value]}`:''}</button>)}</div><label className="search-box"><Search size={18}/><input aria-label="搜尋配件" value={query} onChange={e=>setQuery(e.target.value)} placeholder="配件、規格或專案"/></label></div>
 {error&&<div role="alert" className="shop-pending">{error}。{data?'當前保留上次讀取的記錄。':'請稍後重新整理。'}</div>}
 {!data&&!error?<p className="muted">正在讀取購物清單…</p>:rows.length?<div className="shop-list">{rows.map(item=>{const url=item.supplier.status==='available'?safeLink(item.supplier.url):null;return <article className="shop-card" key={item.id}>
 <div className="shop-card-heading"><div><span className="section-eyebrow">{item.category}</span><h2>{item.name}</h2></div><span className={`status ${item.status==='needed'?'accent':''}`}>{statusNames[item.status]}</span></div>
 <dl className="shop-numbers"><div><dt>共需</dt><dd>{item.unknown_quantities>0?(item.required>0?`已知 ${qty(item.required,item.unit)}`:'待核實'):qty(item.required,item.unit)}{item.unknown_quantities>0&&<small>另有 {item.unknown_quantities} 項數量待核實</small>}</dd></div><div><dt>已有 · 未用</dt><dd>{qty(item.existing,item.unit)}</dd></div><div><dt>已購 · 未用</dt><dd>{qty(item.purchased,item.unit)}</dd></div><div><dt>還需購買</dt><dd>{qty(item.to_buy,item.unit)}</dd></div></dl>
 <details className="shop-detail"><summary>規格、來源與購買連結<ArrowUpRight size={16}/></summary><div className="shop-detail-body">
 <div><h3>具體規格 {item.spec_verified?'':'· 待核實'}</h3>{Object.keys(item.specification).length?<dl className="shop-spec">{Object.entries(item.specification).map(([key,value])=><div key={key}><dt>{key}</dt><dd>{value}</dd></div>)}</dl>:<p className="muted">尚未確認規格，不合並、不猜測型號。</p>}</div>
 <div><h3>來源專案</h3>{item.sources.length?item.sources.map(s=><div className="shop-source" key={`${s.project_id}-${s.requirement_id}`}>{s.project_id==='general'?<strong>{s.project_name}</strong>:<button className="text-link" onClick={()=>onNavigate(`projects/${s.project_id}`)}>{s.project_name}<ArrowUpRight size={16}/></button>}<span>{qty(s.quantity,item.unit)} · {s.active?(s.project_id==='general'?'採購需求':'待裝配'):'已使用'}</span>{s.note&&<p>{s.note}</p>}</div>):<p className="muted">暫無待制作專案使用這份餘料。</p>}<p className="shop-caption">數量始終按全部專案彙總，避免跨專案重複採購。</p></div>
 <div className="shop-supplier"><h3>{supplierNames[item.supplier.status]||supplierNames.unverified}</h3>{url?<a className="button secondary" href={url} target="_blank" rel="noopener noreferrer">查看符合規格的商品<ArrowUpRight size={16}/></a>:<p className="muted">{item.supplier.status==='unavailable'?'已記錄不可購買的核查結果，需另找來源。':'具體商品尚未核實，暫不提供購買連結。'}</p>}{item.supplier.evidence&&<p className="shop-caption">{item.supplier.evidence}</p>}{item.supplier.checked_at&&<p className="shop-caption">核查於 {new Date(item.supplier.checked_at).toLocaleDateString('zh-TW')}，下單前複核規格與庫存。</p>}</div>
 {item.stock_note&&<p className="shop-caption">庫存依據：{item.stock_note}</p>}
 </div></details><div className="shop-card-footer"><span>已購包含在途配件，不代表已到貨。</span><button className="text-link" onClick={()=>copy(item)}>{copied===item.id?<Check size={16}/>:<Copy size={16}/>} {copied===item.id?'已複製，貼上到對話':'在對話中更新庫存'}</button></div>
 </article>})}</div>:data&&<div className="empty-state"><Package size={40} strokeWidth={1.2}/><h3>{query||filter!=='all'?'沒有符合的配件':'還沒有需要採購的配件'}</h3><p>{query||filter!=='all'?'換一個關鍵詞或狀態試試。':'明確決定製作後，Agent 會把非列印配件加入這裡。討論中的想法不會自動加入。'}</p></div>}
 {copyText&&<label className="field shop-copy">複製到對話<textarea readOnly value={copyText} rows={5} onFocus={e=>e.target.select()}/></label>}
 <p className="shop-caption shop-endnote">購物清單由各個 PrintLab 會話共同維護。這裡只查看、整理需求；不會下單或啟動列印。</p>
 </div>
}
