import React, {useEffect, useState} from 'react';
import {Check, Copy, ArrowRight} from 'lucide-react';
import './onboarding.css';

const roleStates = {
  pending: '待建立',
  creating: '建立結果待核對',
  created: '已建立，等待首次介紹',
  introduced: '已介紹並讀取共同資料',
};

export default function Onboarding({onNavigate, onDocument}) {
  const [data, setData] = useState(null);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);
  const [copyText, setCopyText] = useState('');

  useEffect(() => {
    const controller = new AbortController();
    async function load() {
      try {
        const response = await fetch('/api/onboarding', {cache: 'no-store', signal: controller.signal});
        if (!response.ok) throw new Error(`設定讀取失敗（${response.status}）`);
        setData(await response.json());
        setError('');
      } catch (failure) {
        if (failure.name !== 'AbortError') setError(failure.message);
      }
    }
    load();
    window.addEventListener('printlab:refresh', load);
    return () => {
      controller.abort();
      window.removeEventListener('printlab:refresh', load);
    };
  }, []);

  async function copySetup() {
    const roleNames = data.roles.map(role => role.title.split(' · ')[0]).join('、');
    const text = `請繼續設定我的 PrintLab，工作區為 ${data.workspace}。先讀取 AGENTS.md、docs/ONBOARDING.md 和 printlab onboarding status，接續已完成的步驟。核對已有角色聊天後，自動建立尚缺的 ${roleNames} 獨立聊天，讓它們讀取同一工作區並分別介紹自己。讀取設備和已裝材料，再幫我登記其他耗材，按我的設備與使用目標引導第一件作品。`;
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
    } catch {
      setCopyText(text);
    }
  }

  function openDocument(row) {
    onDocument({title: row.name, path: row.path, url: '/api/documents/' + row.path});
  }

  return <div className="onboarding-page">
    <header className="page-heading">
      <div><h1>設定與團隊</h1><p>共同設備、使用習慣和專案進度，供每個會話接續。</p></div>
      {data && <button className="button primary" onClick={copySetup}>
        {copied ? <Check size={17}/> : <Copy size={17}/>}
        {copied ? '已複製，貼上到設定會話' : '讓 Agent 接著設定'}
      </button>}
    </header>
    {error && <div role="alert" className="inline-error">{error}。{data ? '保留上次讀取的資料。' : '請重新整理重試。'}</div>}
    {!data && !error && <p className="muted">正在讀取共同設定…</p>}
    {data && <>
      <section className="onboarding-panel">
        <h2>接下來</h2>
        {data.next_actions.length > 0 ? <ul>{data.next_actions.map((action, index) =>
          <li key={`${action.kind}-${index}`}>{action.text}</li>
        )}</ul> : <p>基礎設定已記錄，可以繼續自己的作品。</p>}
        {data.questions.length > 0 && <details>
          <summary>首次會話需要補齊的資訊</summary>
          <ul>{data.questions.map(question => <li key={question.id}>{question.text}</li>)}</ul>
        </details>}
      </section>
      <div className="onboarding-roles">
        {data.roles.map(role => <section className="onboarding-panel" key={role.role}>
          <h2>{role.title}</h2>
          <p className="muted">{roleStates[role.status] || role.status}</p>
          {role.first_reply && <details><summary>首次介紹</summary><p className="role-reply">{role.first_reply}</p></details>}
          {role.thread_id && <dl><dt>聊天標識</dt><dd>{role.thread_id}</dd><dt>執行位置</dt><dd>{role.host_id}</dd></dl>}
          {role.status === 'creating' && <p>先由設定會話核對宿主中的建立結果，再繼續登記。</p>}
        </section>)}
      </div>
      <section className="onboarding-panel">
        <h2>我的設備與材料</h2>
        <p>{data.device_card?.model || '機型待確認'} · {data.device?.message || '即時連接待檢查'}</p>
        <p>{data.inventory?.state === 'online' ? `庫存已讀取，當前有 ${data.inventory.items.length} 條料卷記錄。` : '庫存尚未讀取。'}</p>
        <button className="text-link" onClick={() => onNavigate('device')}>查看設備、已裝材料與庫存<ArrowRight size={16}/></button>
      </section>
      <section className="onboarding-panel">
        <h2>共同資料</h2>
        <div className="onboarding-documents">{data.shared_documents.filter(row => row.sha256).map(row =>
          <button className="text-link" key={row.name} onClick={() => openDocument(row)}>{row.path}<ArrowRight size={16}/></button>
        )}</div>
        <p className="muted onboarding-path">{data.workspace}</p>
      </section>
    </>}
    {copyText && <label className="field">複製到設定會話<textarea readOnly value={copyText} rows={6} onFocus={event => event.target.select()}/></label>}
  </div>;
}
