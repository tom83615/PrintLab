import React,{lazy,Suspense,useEffect,useRef,useState} from 'react';
import {Box,CheckCircle2,AlertCircle,Clock3,RefreshCw,Printer} from 'lucide-react';
import {estimateDuration,estimateWeight,materialDisplayColor} from './presentation';
const ModelViewer=lazy(()=>import('./ModelViewer'));
import {requestJson as json} from './request-json';
import './prepared.css';

const arr=x=>Array.isArray(x)?x:[];
function requestId(){if(globalThis.crypto?.randomUUID)return globalThis.crypto.randomUUID();if(!globalThis.crypto?.getRandomValues)throw Error('瀏覽器不支援安全隨機數，無法啟動');const bytes=crypto.getRandomValues(new Uint8Array(16));bytes[6]=(bytes[6]&15)|64;bytes[8]=(bytes[8]&63)|128;const hex=Array.from(bytes,x=>x.toString(16).padStart(2,'0')).join('');return `${hex.slice(0,8)}-${hex.slice(8,12)}-${hex.slice(12,16)}-${hex.slice(16,20)}-${hex.slice(20)}`;}
const path=(p,j)=>`/api/prepared/${encodeURIComponent(p)}/${encodeURIComponent(j)}`;
const sameOriginUrl=value=>{if(!value)return null;try{const u=new URL(value,location.origin);return u.origin===location.origin?u.href:null}catch{return null}};
const detail=x=>typeof x==='string'?x:(x?.message||x?.label||x?.name||'待核實');

export default function Prepared(){
 const [items,setItems]=useState(null),[error,setError]=useState('');
 useEffect(()=>{let live=true;const load=()=>json('/api/prepared').then(d=>{if(live){setItems(arr(d.items));setError('')}}).catch(e=>live&&setError(e.message));load();addEventListener('printlab:refresh',load);return()=>{live=false;removeEventListener('printlab:refresh',load)}},[]);
 return <div className="prepared-page"><header className="page-heading"><div><span className="eyebrow">PREPARED PRINTS</span><h1>待列印</h1><p>準備好的任務會留在這裡。啟動前再核對設備和材料。</p></div></header>
 <SenderSetup items={items}/>
 {error&&<p className="prepared-alert" role="alert"><AlertCircle size={20}/>{error}</p>}
 {!items&&!error?<p className="muted">正在讀取待列印任務…</p>:items?.length?<div className="prepared-list">{items.map((item,i)=><PreparedCard key={`${item.project_id||item.pid}-${item.job_id||item.jid}-${i}`} item={item}/>)}</div>:items&&<div className="empty-state"><Box size={32}/><h3>還沒有待列印任務</h3><p>準備好的任務會顯示在這裡。</p></div>}
 </div>
}
function SenderSetup({items}){
 const [cap,setCap]=useState(null),[error,setError]=useState(''),[confirm,setConfirm]=useState(false),[busy,setBusy]=useState(false),[notice,setNotice]=useState('');
 const topLevel=window.top===window.self;
 async function refresh(){try{const result=await json('/api/prepared/sender/capability');setCap(result);setError('')}catch(e){setError(`發送助手狀態暫不可用：${e.message}`)}}
 useEffect(()=>{refresh()},[]);
 async function enable(){if(!topLevel||busy)return;setBusy(true);setError('');try{const session=await json('/api/prepared/session');const result=await json('/api/prepared/sender/enable',{method:'POST',headers:{'Content-Type':'application/json','X-PrintLab-CSRF':session.csrf_token},body:JSON.stringify({request_permissions:true})});setNotice(result.message||'請在 macOS 系統設定中檢查並勾選 PrintLab發送助手，然後重新整理權限狀態。');setConfirm(false);await refresh()}catch(e){setError(`暫時無法啟用發送助手：${e.message}`)}finally{setBusy(false)}}
 if(items?.length&&items.every(item=>item.transport==='bambuddy_queue'))return null;
 if(!cap&&!error)return null;
 if(cap?.setup_supported===false)return <section className="sender-setup" aria-label="Windows 列印交接"><h2>Windows 發送通道</h2><p>已綁定 Bambuddy 佇列通道的任務可逐項核驗並啟動。需要官方 Studio 的任務繼續使用下方交接步驟。</p><a href="https://github.com/AFangTeam/PrintLab/blob/main/docs/WINDOWS.md" target="_blank" rel="noreferrer">查看 Windows 列印步驟</a></section>;
 if(cap?.available===true&&!cap?.setup_required&&!notice&&!error)return null;
 const permission=value=>value===true?'已授權':value===false?'待授權':'待核實';
 return <section className="sender-setup" aria-label="發送助手設定"><div className="sender-setup-title"><div><span className="section-eyebrow">一次性設定</span><h2>啟用 PrintLab發送助手</h2></div></div>
 <p>{cap?.message||'發送助手狀態暫不可用，請稍後重新整理。'}</p>
 {cap?.setup_required&&<p>macOS 需要為“PrintLab發送助手”授予輔助功能和螢幕讀取權限，只用於核對和操作 Studio 發送視窗。請在系統設定中勾選這兩項權限。</p>}
 {cap?.permissions&&<div className="sender-permissions"><span>輔助功能 · {permission(cap.permissions.accessibility)}</span><span>螢幕讀取 · {permission(cap.permissions.screen_capture)}</span></div>}
 {arr(cap?.limitations).map((entry,i)=><p className="sender-note" key={i}>{detail(entry)}</p>)}{notice&&<p className="sender-note" role="status">{notice}</p>}{error&&<p className="prepared-alert" role="alert"><AlertCircle size={18}/>{error}</p>}
 {!topLevel&&<p className="sender-note">請獨立開啟工作台後啟用發送助手。</p>}
 {confirm&&<div className="sender-confirm" role="group" aria-label="確認權限用途"><p>將請求輔助功能和螢幕讀取權限，用於核對和操作 Studio 發送視窗。你仍需在 macOS 系統設定中勾選“PrintLab發送助手”。</p><div className="sender-actions"><button className="button primary" disabled={!topLevel||busy} onClick={enable}>{busy?'正在請求…':'確認並請求權限'}</button><button className="button secondary" disabled={busy} onClick={()=>setConfirm(false)}>取消</button></div></div>}
 {!confirm&&<div className="sender-actions">{cap?.setup_required&&<button className="button primary" disabled={!topLevel||busy} onClick={()=>setConfirm(true)}>啟用發送助手</button>}<button className="button secondary" disabled={busy} onClick={refresh}><RefreshCw size={17}/>重新整理權限狀態</button></div>}
 </section>
}
function PreparedCard({item}){
 const pid=item.project_id||item.pid,jid=item.job_id||item.jid;
 const topLevel=window.top===window.self;
 const storageKey=`printlab-prepared:${pid}:${jid}`;
 const saved=(()=>{try{return JSON.parse(sessionStorage.getItem(storageKey)||'null')}catch{return null}})();
 const [check,setCheck]=useState(null),[busy,setBusy]=useState(''),[error,setError]=useState(''),[operation,setOperation]=useState(item.operation||saved?.operation||null),[uncertain,setUncertain]=useState(!!saved?.uncertain),[now,setNow]=useState(Date.now());
 const lock=useRef(false),opId=operation?.id||operation?.operation_id;
 useEffect(()=>{const timer=setInterval(()=>setNow(Date.now()),1000);return()=>clearInterval(timer)},[]);
 useEffect(()=>{if(!opId)return;let live=true,timer;const poll=async()=>{try{await json('/api/prepared/session');const data=await json(`/api/prepared/operations/${encodeURIComponent(opId)}`);if(!live)return;setOperation(data.operation||data);const s=(data.operation||data).state||(data.operation||data).status;if(['checking','queued','pending','running','dispatching','starting'].includes(s))timer=setTimeout(poll,2500)}catch{if(live)setUncertain(true)}};poll();return()=>{live=false;clearTimeout(timer)}},[opId]);
 useEffect(()=>{try{if(operation||uncertain)sessionStorage.setItem(storageKey,JSON.stringify({operation,uncertain}));else sessionStorage.removeItem(storageKey)}catch{}},[operation,uncertain,storageKey]);
 const expires=check?.expires_at?new Date(check.expires_at).getTime():NaN;
 const checksPass=arr(check?.checks).every(c=>['ok','pass','passed','ready'].includes(c.status));
 const valid=check?.ready===true&&checksPass&&arr(check?.blockers).length===0&&!!check?.check_token&&Number.isFinite(expires)&&expires>now;
 async function verify(){if(!topLevel||lock.current)return;lock.current=true;setBusy('check');setCheck(null);setError('');try{const session=await json('/api/prepared/session');const result=await json(`${path(pid,jid)}/check`,{method:'POST',headers:{'X-PrintLab-CSRF':session.csrf_token}});setCheck(result)}catch(e){setError(e.message)}finally{lock.current=false;setBusy('')}}
 async function start(){if(!topLevel||lock.current||!valid||operation||uncertain)return;lock.current=true;setBusy('start');setError('');try{const session=await json('/api/prepared/session');const result=await json(`${path(pid,jid)}/start`,{method:'POST',headers:{'Content-Type':'application/json','X-PrintLab-CSRF':session.csrf_token},body:JSON.stringify({check_token:check.check_token,request_id:requestId()})});setOperation(result.operation||result);setCheck(null)}catch(e){setCheck(null);setUncertain(true);setError(`提交結果待核對：${e.message}。請勿重複發送。`)}finally{lock.current=false;setBusy('')}}
 async function reconcile(){if(!topLevel||lock.current||!opId)return;lock.current=true;setBusy('reconcile');setError('');try{const session=await json('/api/prepared/session');const result=await json(`/api/prepared/operations/${encodeURIComponent(opId)}/reconcile`,{method:'POST',headers:{'X-PrintLab-CSRF':session.csrf_token}});setOperation(result.operation||result);setUncertain(false)}catch(e){setError(`設備核對失敗：${e.message}。不會重新發送。`)}finally{lock.current=false;setBusy('')}}
 const preview=sameOriginUrl(item.preview_url||item.cover_url||'');const model=sameOriginUrl(item.model_url||'');const name=item.title||item.name||item.project_name||'待列印模型';const mats=arr(item.materials);const duration=estimateDuration(item.estimates?.prediction_seconds??item.prediction_seconds),weight=estimateWeight(item.estimates?.weight_grams??item.weight_grams);const state=operation?.state||operation?.status;
 return <article className="prepared-card"><div className="prepared-visual">{preview?<img src={preview} alt={`${name}預覽`}/>:model?<Suspense fallback={<div className="cover-empty">正在載入模型…</div>}><ModelViewer url={model} name={name} interactive={false}/></Suspense>:<div className="cover-empty"><Box size={40}/><span>預覽待生成</span></div>}</div><div className="prepared-content"><div className="prepared-heading"><div><span className="section-eyebrow">{item.project_name||pid} · {item.revision||'版本待核實'}</span><h2>{name}</h2>{(item.part_name||arr(item.parts).length>0)&&<p>部件：{item.part_name||arr(item.parts).join('、')}</p>}{item.note&&<p>{item.note}</p>}</div><span className="prepared-tag">{item.state_label||'待列印'}</span></div>
 {item.registration_issue&&<p className="prepared-alert"><AlertCircle size={18}/>{item.registration_issue}</p>}<div className="prepared-specs"><div><Clock3 size={17}/><span>{duration||item.duration||'耗時待核實'}</span></div><div><Box size={17}/><span>{weight||'用料待核實'}</span></div></div>
 <div className="prepared-materials">{mats.length?mats.map((m,i)=>{const c=typeof m==='object'?materialDisplayColor(m):null;return <span key={i}>{c&&<i style={{background:c.hex}}/>}{typeof m==='string'?m:[m.slot_label,m.name||m.series||m.material,m.required_grams!=null?`約 ${m.required_grams} g`:null].filter(Boolean).join(' · ')}</span>}):<span>材料待核實</span>}</div>
 {!topLevel&&<p className="prepared-alert" role="alert"><AlertCircle size={18}/>請獨立開啟工作台，再核驗或啟動列印。</p>}
 {!operation&&!uncertain&&<button className="button secondary prepared-check-button" disabled={!topLevel||!!busy||!pid||!jid} onClick={verify}><RefreshCw size={17}/>{busy==='check'?'正在核驗…':'核驗設備與材料'}</button>}
 {error&&<p className="prepared-alert" role="alert"><AlertCircle size={18}/>{error}</p>}
 {check&&<section className="prepared-check" aria-live="polite"><h3>{valid?'核驗通過':check.ready?'核驗已過期':'暫時不能啟動'}</h3><ul>{arr(check.checks).map((c,i)=><li key={c.id||i} className={['ok','pass','passed','ready'].includes(c.status)?'good':'attention'}>{['ok','pass','passed','ready'].includes(c.status)?<CheckCircle2 size={17}/>:<AlertCircle size={17}/>}<span>{c.label}{c.message?`：${c.message}`:''}</span></li>)}{arr(check.blockers).filter(b=>!arr(check.checks).some(c=>c.id&&c.id===b.id)).map((b,i)=><li className="attention" key={`b${i}`}><AlertCircle size={17}/><span>{detail(b)}</span></li>)}</ul>{arr(check.materials).length>0&&<div className="prepared-quantities">{arr(check.materials).map((m,i)=><p key={i}><strong>{m.slot_label||'槽位待核實'}</strong> · 需 {m.required_grams??'未知'} g，預留 {m.reserve_grams??'未知'} g{m.estimated_available_grams!=null?`，估算 ${m.estimated_available_grams} g`:''}。{m.message}</p>)}</div>}{valid&&<div className="prepared-start"><button className="button primary" disabled={!topLevel||!!busy} onClick={start}><Printer size={17}/>{busy==='start'?'正在提交…':'啟動列印'}</button></div>}{check.ready&&!valid&&<p>請重新核驗後再啟動。</p>}</section>}
 {(operation||uncertain)&&<div className="prepared-operation" role="status"><strong>{uncertain?'提交結果待核對':({checking:'正在再次核驗，尚未發送',blocked:'核驗未通過，未發送',observed:'設備已讀回符合任務',queued:'等待處理',pending:'等待處理',running:'正在處理',dispatching:'正在發送',submitted:'已提交，等待設備確認',started:'設備已確認啟動',printing:'設備報告列印中',unknown:'發送結果待核對',dispatch_unknown:'發送結果待核對',failed:'本次發送失敗'}[state]||'正在核對提交狀態')}</strong><p>{operation?.message||'請查看設備狀態；不要重複發送。'}</p>{opId&&['unknown','submitted','observed'].includes(state)&&<button className="button secondary" disabled={!topLevel||!!busy} onClick={reconcile}>{busy==='reconcile'?'正在核對…':'核對設備結果'}</button>}{state==='blocked'&&!uncertain&&<button className="button secondary" onClick={()=>{setOperation(null);setCheck(null)}}>重新核驗</button>}</div>}
 </div></article>
}
