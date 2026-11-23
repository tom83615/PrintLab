import React, {useEffect, useState} from 'react';
import {BookmarkCheck, ArrowUpRight, Search, Box, AlertCircle, X} from 'lucide-react';

const categories = ['全部', '實用品', '造型與擺件'];

function safeUrl(value) {
  if (!value) return null;
  try {
    const url = new URL(value, location.origin);
    return (url.origin === location.origin || url.protocol === 'https:') &&
      !url.username && !url.password ? url.href : null;
  } catch {
    return null;
  }
}

async function loadFavorites(signal) {
  const options = {cache: 'no-store', signal};
  const response = await fetch('/api/favorites', options);
  if (response.ok) return response.json();
  if (response.status === 404) {
    const local = await fetch('/api/documents/Library/References/favorites.json', options);
    if (local.ok) return local.json();
    if (local.status === 404) return {items: []};
  }
  throw Error('收藏暫時無法讀取');
}

export default function Favorites({onNavigate}) {
  const [data, setData] = useState(null);
  const [error, setError] = useState('');
  const [query, setQuery] = useState('');
  const [category, setCategory] = useState('全部');
  const [folder, setFolder] = useState('');
  const [zoom, setZoom] = useState(null);

  useEffect(() => {
    let request;
    const load = async () => {
      request?.abort();
      request = new AbortController();
      const {signal} = request;
      try {
        const result = await loadFavorites(signal);
        if (!signal.aborted) {
          setData(result);
          setError('');
        }
      } catch (failure) {
        if (!signal.aborted) setError(failure.message);
      }
    };
    load();
    const timer = setInterval(load, 60_000);
    addEventListener('printlab:refresh', load);
    return () => {
      request?.abort();
      clearInterval(timer);
      removeEventListener('printlab:refresh', load);
    };
  }, []);

  const items = data?.items ?? [];
  const folders = data?.collections ?? [];
  const folderNames = new Map(folders.map(({id, title}) => [String(id), title]));
  const selectedFolder = folderNames.has(folder) ? folder : '';
  const search = query.trim().toLowerCase();
  const filtered = items.filter(item =>
    (category === '全部' || item.category === category) &&
    (!selectedFolder || item.collection_ids?.some(id => String(id) === selectedFolder)) &&
    [item.title, item.material_suggestion, item.source_author, item.reason].join(' ').toLowerCase().includes(search)
  );
  const sync = data?.makerworld;
  const region = sync?.region === 'cn' ? '中國站' : '國際站';
  const lastSync = sync?.last_success_at && new Date(sync.last_success_at).toLocaleString('zh-TW');

  return <div className="favorites-page">
    <header className="page-heading">
      <div><h1>靈感收藏</h1></div>
      <span className="heading-count">{data ? items.length : '—'}<small>項收藏</small></span>
    </header>
    {sync && <div className="favorites-intro" role="status">
      <BookmarkCheck size={24}/>
      <div>
        <p>{sync.region && `MakerWorld ${region} · `}{sync.message}</p>
        {lastSync && <p>上次成功同步 {lastSync} · {sync.count} 個模型</p>}
        {sync.state === 'unconfigured' && <p>連接方式可在本機終端執行 <code>printlab makerworld connect --help</code> 查看。</p>}
      </div>
    </div>}
    <div className="collection-toolbar">
      <div className="filter-tabs" role="group" aria-label="收藏分類">
        {categories.map(c => <button key={c} aria-pressed={category === c}
          className={category === c ? 'selected' : ''} onClick={() => {setCategory(c); setFolder('');}}>{c}</button>)}
      </div>
      {folders.length > 0 && <label className="search-box">
        <BookmarkCheck size={18}/>
        <select aria-label="MakerWorld 收藏夾" value={selectedFolder}
          onChange={event => {setFolder(event.target.value); setCategory('全部');}}>
          <option value="">所有收藏夾</option>
          {folders.map(({id, title}) => <option key={id} value={id}>{title}</option>)}
        </select>
      </label>}
      <label className="search-box">
        <Search size={18}/>
        <input aria-label="搜尋收藏" value={query} onChange={event => setQuery(event.target.value)} placeholder="物件、材料或作者"/>
      </label>
    </div>
    {error && <div role="alert" className="favorites-intro"><AlertCircle size={20}/><p>{error}</p></div>}
    {!data && !error && <p className="muted">正在讀取收藏…</p>}
    {filtered.length > 0 && <div className="favorites-grid">
      {filtered.map(item => <FavoriteCard key={item.id} item={item}
        folders={item.collection_ids?.map(id => folderNames.get(String(id))).filter(Boolean) || []}
        onNavigate={onNavigate} onZoom={setZoom}/>)}
    </div>}
    {data && filtered.length === 0 && <div className="empty-state">
      <Search size={32}/>
      <h3>{search || category !== '全部' || selectedFolder ? '沒有符合的收藏' : '這裡還沒有收藏'}</h3>
    </div>}
    {zoom && <div className="modal-backdrop" onMouseDown={event => event.target === event.currentTarget && setZoom(null)}>
      <section className="modal modal-wide favorite-zoom" role="dialog" aria-modal="true"
        aria-label={zoom.title} onKeyDown={event => event.key === 'Escape' && setZoom(null)}>
        <div className="modal-heading">
          <h2>{zoom.title}</h2>
          <button autoFocus className="icon-button" aria-label="關閉大圖" onClick={() => setZoom(null)}><X size={22}/></button>
        </div>
        <img src={safeUrl(zoom.preview_url)} alt={zoom.title} referrerPolicy="no-referrer"/>
        <p>{zoom.preview_credit || zoom.source_author}</p>
      </section>
    </div>}
  </div>;
}

function FavoriteCard({item, folders, onNavigate, onZoom}) {
  const [failedPreview, setFailedPreview] = useState(null);
  const url = safeUrl(item.source_url);
  const preview = safeUrl(item.preview_url);
  const showPreview = preview && failedPreview !== preview;
  const localDetail = safeUrl(item.local_detail_url);

  return <article className="favorite-card">
    <button className="favorite-cover" aria-label={`放大：${item.title}`} disabled={!showPreview} onClick={() => onZoom(item)}>
      {showPreview ? <img src={preview} alt={item.title} loading="lazy" referrerPolicy="no-referrer"
        onError={() => setFailedPreview(preview)}/> : <span className="cover-empty"><Box size={36}/><span>圖片暫不可用</span></span>}
      <span className="favorite-saved"><BookmarkCheck size={16}/>已收藏</span>
    </button>
    <div className="favorite-copy">
      <span className="section-eyebrow">{[item.category, ...folders].filter(Boolean).join(' · ')}</span>
      <h2>{item.title}</h2>
      {item.reason && <p>{item.reason}</p>}
      {(item.material_suggestion || item.color_suggestion) && <div className="favorite-material">
        <strong>{item.material_suggestion}</strong><p>{item.color_suggestion}</p>
      </div>}
      {item.fit_notes && <details><summary>適配與選型提醒</summary><p>{item.fit_notes}</p></details>}
      <div className="favorite-links">
        {url && <a className="text-link" href={url} target="_blank" rel="noopener noreferrer">作者原頁<ArrowUpRight size={16}/></a>}
        {localDetail && <a className="text-link" href={localDetail}>已選配色<ArrowUpRight size={16}/></a>}
        {(item.related_project_ids || []).map(id => <button className="text-link" key={id}
          onClick={() => onNavigate(`projects/${id}`)}>專案 {id}<ArrowUpRight size={16}/></button>)}
      </div>
      {(item.preview_credit || item.source_author) && <p className="favorite-credit">{item.preview_credit || item.source_author}</p>}
    </div>
  </article>;
}
