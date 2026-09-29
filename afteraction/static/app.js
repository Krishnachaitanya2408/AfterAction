'use strict';
const $ = s => document.querySelector(s);
const escape = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let state;
function notice(text, error=false) { const n=$('#notice'); n.textContent=text; n.hidden=!text; n.className=error?'error':''; }
async function api(path, data) {
  const response = await fetch(path, data === undefined ? {} : {method:'POST',headers:{'Content-Type':'application/json','X-AfterAction':'1'},body:JSON.stringify(data)});
  const result=await response.json(); if(!response.ok) throw new Error(result.error || 'Request failed'); return result;
}
async function busy(fn, message='Working… Hindsight processing can take a little while.') {
  document.querySelectorAll('button').forEach(b=>b.disabled=true); notice(message);
  try { await fn(); } catch(e) {notice(e.message,true);}
  finally {document.querySelectorAll('button').forEach(b=>b.disabled=false);}
}
function selectTab(name) {
 document.querySelectorAll('.pane').forEach(p=>p.hidden=p.id!==name);
 document.querySelectorAll('.tab').forEach(t=>{t.classList.toggle('selected',t.dataset.tab===name);t.setAttribute('aria-current',t.dataset.tab===name?'page':'false');});
}
document.querySelectorAll('.tab').forEach(t=>t.addEventListener('click',()=>selectTab(t.dataset.tab)));
function fillSample() {
 for(const id of ['incident-form','learn-form']) for(const [k,v] of Object.entries(state.sample)) $(`#${id}`).elements[k].value=v;
 $('#learn-form').elements.observed_at.value=new Date(Date.now()-60000).toISOString().slice(0,16);
}
async function refresh() {
 state=await api('/api/state');
 $('#mode').textContent=state.mode==='hindsight'?`HINDSIGHT LIVE · ${state.bank}`:'REHEARSAL · No AI / no external calls';
 $('#mode').classList.toggle('live',state.mode==='hindsight');
 $('#count').textContent=state.lessons.length;
 $('#sync').textContent=`Retry Hindsight sync${state.pending?' ('+state.pending+' pending)':''}`;
 $('#sync').hidden=state.mode!=='hindsight';
 $('#lessons').innerHTML=state.lessons.length?state.lessons.map(r=>`<article class="card lesson ${r.retired?'retired':''}"><span class="tag ${escape(r.outcome)}">${escape(r.outcome.toUpperCase())}</span><p class="source">${escape(r.id)} · ${escape(r.observed_at.slice(0,10))}</p><h3>${escape(r.action)}</h3><p class="scope">${escape(r.service)} / ${escape(r.environment)}<br>${escape(r.architecture)}</p><p>${escape(r.reason)}</p><details><summary>Incident symptoms</summary><p>${escape(r.symptom)}</p></details><p class="footnote">${r.retired?'Retired locally · excluded from decisions':state.mode==='hindsight'?(r.synced?'Synced to current Hindsight bank':'Pending Hindsight sync'):'Stored locally for rehearsal'}</p>${r.retired?'':`<button class="text-button retire" data-id="${escape(r.id)}">Retire from future decisions</button>`}</article>`).join(''):'<div class="card"><h3>No outcomes yet.</h3><p>Load the sample outcomes or record your first reviewed result.</p></div>';
 document.querySelectorAll('.retire').forEach(b=>b.addEventListener('click',()=>busy(async()=>{await api('/api/retire',{id:b.dataset.id});await refresh();notice('Lesson retired locally. It remains in the source ledger and Hindsight, but is excluded from future decisions.');})));
 $('#traces').innerHTML=state.traces.length?state.traces.map(t=>`<div class="trace-row"><code>${escape(t.operation)}</code><span>${escape(t.status)}</span><span>${escape(t.detail)}</span><time>${t.elapsed_ms}ms</time></div>`).join(''):'<p class="muted">No memory operations yet. Start an investigation.</p>';
}
function block(title,items,cls='') {
 if(!items.length)return '';
 return `<section class="decision-block ${cls}"><h3>${escape(title)}</h3>${items.map(i=>`<p><strong>${escape(i.action)}</strong></p>${i.reasons.map(r=>`<p>${escape(r)}</p>`).join('')}<p class="source">Sources: ${i.sources.map(escape).join(', ')}</p>`).join('')}</section>`;
}
function renderResult(baseline, result) {
 const d=result.decision; $('#empty').hidden=true; $('#results').hidden=false;
 $('#results').innerHTML=`<div class="compare"><div class="baseline"><span class="small-label">WITHOUT MEMORY</span><p>${escape(baseline.summary)}</p><ol>${baseline.baseline.map(x=>`<li>${escape(x)}</li>`).join('')}</ol></div><div><span class="small-label">WITH ${result.mode==='hindsight'?'HINDSIGHT':'REHEARSAL MEMORY'}</span><span class="tag">${d.eligible.length} applicable source episodes</span>${block('Previously failed — avoid repeating blindly',d.avoided,'warn')}${block('Candidate next steps — verify before acting',d.proposed)}${block('Needs review — contradictory outcomes',d.conflicts,'conflict')}${block('Inconclusive — gather more evidence',d.uncertain)}${!d.eligible.length?'<p class="muted">No applicable history found. Do not infer a fix. Check the context, sync status, or collect a verified outcome.</p>':''}</div></div><details open><summary>${result.mode==='hindsight'?'Hindsight reflection · generated guidance, review against sources':'Deterministic rehearsal summary · not AI'}</summary><p class="summary">${escape(result.summary)}</p></details><details><summary>Applicable source records (${d.eligible.length})</summary>${d.eligible.map(r=>`<p class="source">${escape(r.id)} · ${escape(r.observed_at)}</p><p>${escape(r.symptom)}</p><p>${escape(r.action)} → ${escape(r.outcome)}</p>`).join('')}</details><details><summary>Excluded recalled records (${d.excluded.length})</summary>${d.excluded.map(r=>`<p>${escape(r.id)} — ${escape(r.excluded_reason)}</p>`).join('')}<p class="muted">Hindsight also filters other services and environments before returning records.</p></details><details><summary>Raw Hindsight recalled facts (${result.facts.length})</summary><pre>${escape(JSON.stringify(result.facts,null,2))}</pre></details>`;
}
$('#incident-form').addEventListener('submit',event=>{event.preventDefault();busy(async()=>{
 const data=Object.fromEntries(new FormData(event.target));
 const baseline=await api('/api/investigate',{...data,use_memory:false});
 const result=await api('/api/investigate',{...data,use_memory:true});renderResult(baseline,result);await refresh();notice(result.warning||'Comparison complete. Review the evidence before choosing an intervention.',!!result.warning);
});});
$('#seed').addEventListener('click',()=>busy(async()=>{const r=await api('/api/seed',{});await refresh();notice(r.warnings.length?r.warnings.join(' '):'Sample outcomes loaded. Compare the same incident again to see what changed.',!!r.warnings.length);},'Loading three fictional outcomes. Live mode will retain them in your Hindsight bank.'));
$('#sync').addEventListener('click',()=>busy(async()=>{const r=await api('/api/sync',{});await refresh();notice(r.warnings.length?r.warnings.join(' '):`Sync complete: ${r.processed} outcomes processed.`,!!r.warnings.length);}));
$('#learn-form').addEventListener('submit',event=>{event.preventDefault();busy(async()=>{
 const data=Object.fromEntries(new FormData(event.target));data.confirmed=event.target.elements.confirmed.checked;
 data.observed_at+=':00Z'; // Form explicitly displays UTC, independent of browser timezone.
 const r=await api('/api/lessons',data);await refresh();notice(r.warning||`Saved ${r.lesson.id}. Investigate again to use the new outcome.`,!!r.warning);selectTab('ledger');
});});
$('#sample').addEventListener('click',()=>{fillSample();selectTab('investigate');notice('Sample incident restored.');});
$('#refresh').addEventListener('click',()=>busy(async()=>{await refresh();notice('Activity refreshed.');}));
refresh().then(fillSample).catch(e=>notice(e.message,true));
