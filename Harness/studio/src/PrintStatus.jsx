import React,{useEffect,useState} from 'react';
import {Clock3,CheckCircle2,AlertCircle,Printer} from 'lucide-react';
import {estimateDuration,estimateWeight} from './presentation';
import './print-status.css';

const phase={dispatching:'正在下發',submitted:'已接受 · 等待設備確認',preparing:'準備 / 加熱中',running:'執行中 · 首層未核實',printing:'設備報告列印進度',paused:'已暫停',awaiting_physical_review:'設備完成 · 待實物驗收',failed:'本次任務失敗',cancelled:'本次任務取消',dispatch_unknown:'執行結果待核對',awaiting_approval:'待確認列印',approved:'已確認 · 尚未下發',awaiting_configuration:'試切片 · 待設定'};
const date=t=>t?new Date(t).toLocaleString('zh-TW',{month:'numeric',day:'numeric',hour:'2-digit',minute:'2-digit',second:'2-digit'}):'尚無記錄';

export function CurrentAttempt({record:r}){
 if(!r)return null;
 const observation=r.reconciliation,uncertain=observation&&observation.state!=='current',p=r.printer_progress;
 return <section className="current-attempt" aria-label="當前列印任務"><div className="attempt-title"><Printer size={22}/><div><span className="section-eyebrow">當前列印嘗試</span><h2>{uncertain?'狀態待核對':phase[r.state]||r.state}</h2></div></div><p>{r.execution_phase||(r.trial_only?'設定核對完成後再確認列印。':'與下方歷史任務分開記錄。')}</p>{p&&<p>設備進度 {p.progress??'未知'}% · 層數 {p.layer_num??'未知'} / {p.total_layers??'未知'}</p>}{uncertain&&<p className="attempt-warning">{observation.message||'當前顯示上次狀態；沒有重發任務。'}</p>}<div className="attempt-meta"><span>{r.id}</span><span>{r.mapping?.transport==='bambu_native'?'原生通道 · 內部儲存':'列印管理佇列'}</span><span>更新 {date(r.last_reconciled_at||r.updated_at||r.created_at)}</span></div></section>
}

export function ConfirmationCard({projectId}){
 const [card,setCard]=useState(null),[error,setError]=useState('');
 useEffect(()=>{let alive=true;const load=()=>fetch(`/api/projects/${encodeURIComponent(projectId)}/confirmation`,{cache:'no-store'}).then(r=>{if(!r.ok)throw Error('確認資訊暫時無法讀取');return r.json()}).then(c=>{if(alive){setCard(c);setError('')}}).catch(e=>alive&&setError(e.message));load();addEventListener('printlab:refresh',load);return()=>{alive=false;removeEventListener('printlab:refresh',load)}},[projectId]);
 if(error)return <p className="attempt-warning" role="alert">{error}，重新整理後重試。</p>;if(!card)return null;
 const rows=[['模型',`${card.project_name} · ${card.revision||'版本待確認'}`],['列印板',card.plate_type||'板型待核實'],['預計耗時',estimateDuration(card.estimates?.prediction_seconds)||'尚未估算'],['預計用料',estimateWeight(card.estimates?.weight_grams)||'尚未估算']];
 const facts=card.facts||{},names={design_selected:'造型已選定',colors_selected:'配色已確認',material_loaded:'裝料已確認',plate_clear:'本次列印板已清空',print_authorized:'具體任務已獲授權'};
 return <section className="confirmation-card" aria-label="列印確認卡"><div className="section-heading"><div><span className="eyebrow">{card.already_dispatched?'TASK RECORD':'READY TO REVIEW'}</span><h2>{card.already_dispatched?'這次任務的確認記錄':'列印確認卡'}</h2></div></div><dl className="confirmation-specs">{rows.map(([key,value])=><div key={key}><dt>{key}</dt><dd>{value}</dd></div>)}</dl>
 {card.material_slots?.length>0&&<div className="confirmation-slots">{card.material_slots.map((r,i)=><div key={i}><strong>AMS {String.fromCharCode(65+(r.ams_id||0))} · 槽 {r.slot_number}</strong><span>{r.english_label||r.material||'Material not identified'}{r.material_number?` (${r.material_number})`:''}</span></div>)}</div>}
 <div className="confirmation-facts">{Object.entries(facts).map(([key,f])=><p key={key}>{f.value?<CheckCircle2 size={16}/>:<AlertCircle size={16}/>}<span>{names[key]||key}{!f.value?' · 已撤回':!card.already_dispatched&&f.fresh===false?' · 已過期，需更新':''}<small>{date(f.recorded_at)}</small></span></p>)}</div>
 {(card.validation_alerts||[]).map((a,i)=><p className="attempt-warning" key={i}><AlertCircle size={18}/><span>{a.message}</span></p>)}
 {card.already_dispatched?<p className="confirmation-caption">這次任務已經下發，保留提交時的確認；這裡不會重複發送。</p>:card.missing?.length>0?<div className="confirmation-missing"><h3>還缺這些資訊</h3><ul>{card.missing.map((m,i)=><li key={i}>{m.label}{m.needs_user?'':' · 由工作流核查'}</li>)}</ul></div>:<p className="confirmation-caption">已記錄的回答會沿用；下發前仍需核對即時設備及準確文件。</p>}
 <p className="confirmation-caption"><Clock3 size={15}/>讀取 {date(card.observed_at)} · 耗時與用料是切片估算。板型長期儲存，本次清板另行記錄。</p></section>
}
