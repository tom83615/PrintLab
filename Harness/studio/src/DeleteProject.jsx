import React, {useRef, useState} from 'react';
import {ExternalLink, Trash2} from 'lucide-react';
import {requestJson} from './request-json';

export default function DeleteProject({project, onDeleted}) {
  const dialog = useRef(null);
  const submitting = useRef(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  if (window.top !== window.self) {
    return <a className="button secondary" href={location.href} target="_blank" rel="noopener noreferrer">
      獨立開啟以刪除專案<ExternalLink size={16}/>
    </a>;
  }

  async function confirmDeletion() {
    if (submitting.current) return;
    submitting.current = true;
    setBusy(true);
    setError('');
    try {
      const session = await requestJson('/api/prepared/session');
      const result = await requestJson(`/api/projects/${encodeURIComponent(project.id)}`, {
        method: 'DELETE',
        headers: {'Content-Type': 'application/json', 'X-PrintLab-CSRF': session.csrf_token},
        body: JSON.stringify({confirm_id: project.id}),
      });
      if (result.deleted !== true || result.project_id !== project.id) {
        throw new Error('未收到這個專案的刪除回執，請重新整理專案圖冊核對。');
      }
      dialog.current?.close();
      onDeleted(project);
    } catch (cause) {
      setError(cause instanceof TypeError ? '連接中斷，請重新整理專案圖冊核對刪除結果。' : cause.message);
    } finally {
      submitting.current = false;
      setBusy(false);
    }
  }

  return <>
    <button className="button secondary" onClick={() => {setError(''); dialog.current.showModal();}}>
      <Trash2 size={16}/>刪除專案
    </button>
    <dialog ref={dialog} className="modal delete-project-dialog" aria-labelledby="delete-project-title"
      aria-describedby="delete-project-scope" onCancel={event => {if (submitting.current) event.preventDefault();}}>
      <h2 id="delete-project-title">刪除這個專案？</h2>
      <div id="delete-project-scope">
        <p className="delete-project-name"><strong>{project.name}</strong> · {project.id}</p>
        <p>將永久刪除此專案的本機資料夾，包括模型、切片和會話記錄，同時移除它的待列印任務和購物需求。此操作無法撤銷。</p>
      </div>
      {error && <p className="delete-project-error" role="alert">{error}</p>}
      <div className="delete-project-buttons">
        <button className="button secondary" autoFocus disabled={busy} onClick={() => dialog.current.close()}>取消</button>
        <button className="button delete-project-confirm" disabled={busy} onClick={confirmDeletion}>
          {busy ? '正在刪除…' : '永久刪除'}
        </button>
      </div>
    </dialog>
  </>;
}
