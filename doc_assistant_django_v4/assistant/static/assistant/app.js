const uploadBtn = document.getElementById('uploadBtn');
const fileInput = document.getElementById('fileinput');
const uploadStatus = document.getElementById('uploadStatus');
uploadBtn.onclick = async () => {
  const f = fileInput.files[0]; if (!f) { alert('Select a PDF'); return; }
  const fd = new FormData(); fd.append('file', f, f.name);
  uploadStatus.innerText = 'Uploading...';
  try {
    const res = await fetch('/upload/', { method: 'POST', body: fd });
    const data = await res.json();
    if (res.ok) {
      uploadStatus.innerText = `Task queued (${data.task_id}). Polling status...`;
      pollStatus(data.task_id);
    } else { uploadStatus.innerText = 'Upload error: ' + (data.detail || JSON.stringify(data)); }
  } catch (e) { uploadStatus.innerText = 'Upload failed: ' + e.message; }
};

async function pollStatus(taskId) {
  const el = document.getElementById('uploadStatus');
  let done=false;
  while(!done) {
    await new Promise(r => setTimeout(r, 1500));
    try {
      const res = await fetch(`/task-status/?task_id=${taskId}`);
      const data = await res.json();
      el.innerText = `Status: ${data.status}`;
      if (data.result) {
        el.innerText += ` — result: ${JSON.stringify(data.result)}`;
        done = true;
        setTimeout(()=>location.reload(), 600);
      } else if (data.status === 'FAILURE') {
        done=true;
      }
    } catch (e){ el.innerText = 'Status poll failed: '+e.message; done=true; }
  }
}

const askBtn = document.getElementById('askBtn');
askBtn.onclick = async () => {
  const q = document.getElementById('queryInput').value.trim();
  if (!q) { alert('Type a question'); return; }
  document.getElementById('answer').innerText = 'Thinking...';
  try {
    const res = await fetch('/query/', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({query: q, top_k:5}) });
    const data = await res.json();
    if (res.ok) {
      document.getElementById('answer').innerText = data.answer;
      const sources = document.getElementById('sources'); sources.innerHTML='';
      (data.sources||[]).forEach(s => { const li = document.createElement('li'); li.textContent = `${s.filename} (page ${s.page}) — ${s.text_snippet.slice(0,200)}...`; sources.appendChild(li); });
    } else { document.getElementById('answer').innerText = 'Query error: ' + (data.detail || JSON.stringify(data)); }
  } catch (e) { document.getElementById('answer').innerText = 'Query failed: ' + e.message; }
};
