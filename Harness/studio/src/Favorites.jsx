import React,{useEffect,useState} from 'react';
import {BookmarkCheck,ArrowUpRight,Search,Box,AlertCircle,X} from 'lucide-react';

const dataUrl='/api/documents/Library/References/favorites.json';
function safeUrl(value){try{const url=new URL(value,location.origin);return (url.origin===location.origin||url.protocol==='https:')&&!url.username&&!url.password?url.href:null}catch{return null}}

export default function Favorites({onNavigate}){
 const [data,setData]=useState(null),[error,setError]=useState(''),[query,setQuery]=useState(''),[category,setCategory]=useState('全部'),[zoom,setZoom]=useState(null);
 useEffect(()=>{let live=true;const load=()=>fetch(dataUrl,{cache:'no-store'}).then(r=>{if(!r.ok)throw Error('收藏暫時無法讀取');return r.json()}).then(d=>{if(live){setData(d);setError('')}}).catch(e=>live&&setError(e.message));load();addEventListener('printlab:refresh',load);return()=>{live=false;removeEventListener('printlab:refresh',load)}},[]);
 const items=Array.isArray(data?.items)?data.items:[],filtered=items.filter(x=>(category==='全部'||x.category===category)&&[x.title,x.material_suggestion,x.source_author,x.reason].join(' ').toLowerCase().includes(query.toLowerCase()));
 return <div className="favorites-page"><header className="page-heading"><div><span className="eyebrow">SAVED FOR ANOTHER DAY</span><h1>靈感收藏</h1><p>看中的物件、原作者和選料建議，一起留在這裡。</p></div><span className="heading-count">{data?items.length:'—'}<small>項收藏</small></span></header>
 <div className="favorites-intro"><BookmarkCheck size={24}/><p>這裡顯示本機靈感收藏。MakerWorld 帳號收藏自動同步尚未接入，可在對話中添加原作者連結。</p></div>
 <div className="collection-toolbar"><div className="filter-tabs" role="group" aria-label="收藏分類">{['全部','實用品','造型與擺件'].map(c=><button key={c} aria-pressed={category===c} className={category===c?'selected':''} onClick={()=>setCategory(c)}>{c}</button>)}</div><label className="search-box"><Search size={18}/><input aria-label="搜尋收藏" value={query} onChange={e=>setQuery(e.target.value)} placeholder="物件、材料或作者"/></label></div>
 {error&&<div role="alert" className="favorites-intro"><AlertCircle size={20}/><p>{error}</p></div>}
 {!data&&!error?<p className="muted">正在讀取收藏…</p>:filtered.length?<div className="favorites-grid">{filtered.map(item=><FavoriteCard key={item.id} item={item} onNavigate={onNavigate} onZoom={setZoom}/>)}</div>:data&&<div className="empty-state"><Search size={32}/><h3>{query?'沒有符合的收藏':'這裡還沒有收藏'}</h3><p>{query?'換一個關鍵詞試試。':'在對話中告訴我想收藏的物件。'}</p></div>}
 {zoom&&<div className="modal-backdrop" onMouseDown={e=>e.target===e.currentTarget&&setZoom(null)}><section className="modal modal-wide favorite-zoom" role="dialog" aria-modal="true" aria-label={zoom.title} onKeyDown={e=>e.key==='Escape'&&setZoom(null)}><div className="modal-heading"><h2>{zoom.title}</h2><button autoFocus className="icon-button" aria-label="關閉大圖" onClick={()=>setZoom(null)}><X size={22}/></button></div><img src={safeUrl(zoom.preview_url)} alt={zoom.title} referrerPolicy="no-referrer"/><p>{zoom.preview_credit}</p></section></div>}
 </div>
}

function FavoriteCard({item,onNavigate,onZoom}){
 const [failed,setFailed]=useState(false),url=safeUrl(item.source_url),preview=safeUrl(item.preview_url);
 return <article className="favorite-card"><button className="favorite-cover" aria-label={`放大：${item.title}`} disabled={failed||!preview} onClick={()=>onZoom(item)}>{preview&&!failed?<img src={preview} alt={item.title} referrerPolicy="no-referrer" onError={()=>setFailed(true)}/>:<span className="cover-empty"><Box size={36}/><span>圖片暫不可用，可查看作者原頁</span></span>}<span className="favorite-saved"><BookmarkCheck size={16}/>已收藏</span></button><div className="favorite-copy"><span className="section-eyebrow">{item.category}</span><h2>{item.title}</h2><p>{item.reason}</p><div className="favorite-material"><strong>{item.material_suggestion}</strong><p>{item.color_suggestion}</p></div><details><summary>適配與選型提醒</summary><p>{item.fit_notes}</p></details><div className="favorite-links">{url&&<a className="text-link" href={url} target="_blank" rel="noopener noreferrer">作者原頁<ArrowUpRight size={16}/></a>}{item.local_detail_url&&safeUrl(item.local_detail_url)&&<a className="text-link" href={safeUrl(item.local_detail_url)}>已選配色<ArrowUpRight size={16}/></a>}{(item.related_project_ids||[]).map(id=><button className="text-link" key={id} onClick={()=>onNavigate(`projects/${id}`)}>專案 {id}<ArrowUpRight size={16}/></button>)}</div><p className="favorite-credit">{item.preview_credit}</p></div></article>
}
