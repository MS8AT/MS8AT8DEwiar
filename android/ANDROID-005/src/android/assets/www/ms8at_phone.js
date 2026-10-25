/* Android-конструктор: небольшая связка независимых блоков с существующим Dewiar.
   Модели вызываются через штатный HTTP-мост. Компьютер для выполнения задач не нужен.
   Настройки разрешений меняет только интерфейс человека; модель их не получает. */
"use strict";
const MS8ATPhone = window.MS8ATPhone = (() => {
  const roles = ["chat", "tasks", "check", "memory"];
  const words = {
    ru: {title:"AI-конструктор", enabled:"Модели по назначениям", chat:"Разговор", tasks:"Задачи", check:"Самопроверка", memory:"Память", none:"Не выбрано", auto:"Автовыбор из отмеченных", tools:"Разрешить инструменты", allow:"Разрешён для автовыбора", save:"Сохранить", brains:"Подключить модель", refresh:"Обновить состояние", doctor:"Проверка системы", checkHealth:"Проверить", ready:"Готово", attention:"Нужна настройка", blocked:"Заблокировано", routingDisabled:"Маршрутизация выключена", unavailable:"Адаптер ещё не подключён", goal:"Что сделать на Android", start:"Запустить", stop:"Остановить", queue:"Создать задачу", local:"Локальная память", read:"Читать заметки", write:"Сохранять заметки", taskread:"Разрешить задачам читать заметки", add:"Добавить заметку", search:"Найти", logs:"Журнал и heartbeat", foreground:"Задачи работают, пока открыт Dewiar. После перезапуска требуют ручного продолжения. Читают разрешённые заметки и создают текстовый результат; системных команд пока нет.", privacy:"В журнале только состояние и коды ошибок. Текст задачи и заметки хранятся на этом Android.", developer:"Разработка", devhint:"Codex CLI и code-server устанавливаются отдельным блоком внутри Android. Вход в аккаунт — отдельно.", connect:"Настройте модель в разделе «Мозг», затем выберите её здесь.", reason:{storage_unavailable:"хранилище недоступно", corrupt_or_unavailable:"ошибка хранилища", provider_missing:"профиль модели не найден", not_configured:"профиль модели не настроен", not_allowed:"модель не разрешена для этого назначения", no_tools:"у модели нет инструментов", no_approved_provider:"нет разрешённой модели", adapter_unavailable:"адаптер не подключён", unassigned:"модель не выбрана"}},
    en: {title:"AI constructor", enabled:"Route models by purpose", chat:"Chat", tasks:"Tasks", check:"Review", memory:"Memory", none:"Not selected", auto:"Auto from approved models", tools:"Allow tools", allow:"Allow automatic selection", save:"Save", brains:"Connect a model", refresh:"Refresh status", doctor:"System check", checkHealth:"Check now", ready:"Ready", attention:"Needs setup", blocked:"Blocked", routingDisabled:"Routing is off", unavailable:"Adapter not connected", goal:"What to do on Android", start:"Start", stop:"Stop", queue:"Create task", local:"Local memory", read:"Read notes", write:"Save notes", taskread:"Allow tasks to read notes", add:"Add note", search:"Search", logs:"Journal and heartbeat", foreground:"Tasks run while Dewiar is open. Restart requires manual continuation. Tasks can read approved notes and produce text; system commands are not available yet.", privacy:"The journal contains states and error codes only. Task text and notes stay on this Android device.", developer:"Development", devhint:"Codex CLI and code-server are separate Android modules. Account sign-in is a separate step.", connect:"Configure a model under Brain, then select it here.", reason:{storage_unavailable:"storage unavailable", corrupt_or_unavailable:"storage error", provider_missing:"model profile not found", not_configured:"model profile is not configured", not_allowed:"model is not approved for this purpose", no_tools:"model has no tools", no_approved_provider:"no approved model", adapter_unavailable:"adapter is not connected", unassigned:"no model selected"}},
    "zh-CN": {title:"AI 构建器", enabled:"按用途选择模型", chat:"对话", tasks:"任务", check:"自检", memory:"记忆", none:"未选择", auto:"从已授权模型自动选择", tools:"允许工具", allow:"允许自动选择", save:"保存", brains:"连接模型", refresh:"刷新状态", doctor:"系统检查", checkHealth:"立即检查", ready:"就绪", attention:"需要设置", blocked:"已阻止", routingDisabled:"路由已关闭", unavailable:"适配器尚未连接", goal:"在 Android 上做什么", start:"启动", stop:"停止", queue:"创建任务", local:"本地记忆", read:"读取笔记", write:"保存笔记", taskread:"允许任务读取笔记", add:"添加笔记", search:"搜索", logs:"日志和心跳", foreground:"任务在 Dewiar 打开时运行，重启后需手动继续。任务可读取授权笔记并生成文本，尚不执行系统命令。", privacy:"日志仅包含状态和错误代码。任务文本和笔记保存在此 Android 设备上。", developer:"开发工具", devhint:"Codex CLI 和 code-server 是独立的 Android 模块，账户登录需另行完成。", connect:"在模型设置中配置连接，然后在此选择。", reason:{storage_unavailable:"存储不可用", corrupt_or_unavailable:"存储错误", provider_missing:"未找到模型配置", not_configured:"模型配置尚未完成", not_allowed:"该模型未获此用途授权", no_tools:"模型不支持工具", no_approved_provider:"没有获准的模型", adapter_unavailable:"适配器未连接", unassigned:"尚未选择模型"}}
  };
  const tr = () => words[S.language] || words.ru;
  const label=(ru,en,zh)=>S.language==="en"?en:S.language==="zh-CN"?zh:ru;
  const read = key => prefGet(key);
  const write = (key, value) => { prefSet(key, value); return true; };
  const core = MS8ATConstructor.create({storage:{getItem:read, setItem:write}});
  let permissions = {enabled:false, read:false, write:false, tasks:false};
  try { const saved = JSON.parse(read("ms8at_memory_permissions") || "{}"); for (const k of Object.keys(permissions)) permissions[k] = saved[k] === true; } catch (_) {}
  const memory = MS8ATMemory.create({storage:{read:()=>read("ms8at_memory"), write:v=>write("ms8at_memory",v)}, permissions});
  let profiles = new Map();
  function localAddress(value) {
    try { const h=new URL(value).hostname;return h==="localhost"||h==="[::1]"||/^(127|10)\.\d+\.\d+\.\d+$/.test(h)||/^192\.168\.\d+\.\d+$/.test(h)||/^172\.(1[6-9]|2\d|3[01])\.\d+\.\d+$/.test(h); } catch(_){return false;}
  }
  const uuid = () => "p_" + (globalThis.crypto && crypto.randomUUID ? crypto.randomUUID().replace(/-/g,"") : Date.now().toString(36) + Math.random().toString(36).slice(2));
  function sync() {
    profiles = new Map(); let changed = false;
    for (const p of [S.llm, ...(S.llmSaved || [])]) {
      if (!p || !p.base_url || p.trial || (p.account && !loggedIn())) continue;
      if (!/^p_[a-zA-Z0-9_-]{1,60}$/.test(p.ms8at_id || "")) { p.ms8at_id = uuid(); changed = true; }
      if (!profiles.has(p.ms8at_id)) profiles.set(p.ms8at_id, p);
    }
    if (changed) saveS();
    core.setProviders([...profiles].map(([id,p])=>({id,kind:localAddress(p.base_url)?"local":"cloud", configured:!!p.model, enabled:true, tools:p.ms8at_tools === true, purposes:roles})));
  }
  async function call(messages, tools, onText, signal, opt = {}) {
    if (!core.snapshot().enabled) return llmStreamRaw(messages, tools, onText, signal, opt);
    sync();
    const role = opt.purpose || "chat", run = core.begin(role, {tools:!!(tools && tools.length)});
    if (!run.ok) throw Object.assign(new Error(run.reason), {ms8at:true,human:true});
    // Снимок сохраняет провайдера на все этапы одного запроса, включая его настройки.
    const provider = {...profiles.get(run.providerId)}; let lastSignal=0;
    try {
      if(messages.some(m=>Array.isArray(m.content)&&m.content.some(p=>p.type==="image_url")) && provider.ms8at_vision!==true) throw new Error("vision_not_confirmed");
      const result = await llmStreamRaw(messages, tools, piece => { if(Date.now()-lastSignal>=1000){core.signal(run.id);lastSignal=Date.now();} if(onText) onText(piece); }, signal, {...opt,provider,noRetry:true});
      core.finish(run.id, {ok:true}); return result;
    } catch (e) {
      core.finish(run.id, {ok:false,category:String(e.message || "")});
      throw Object.assign(new Error(core.diagnose(String(e.message || "")).code), {ms8at:true,human:true});
    }
  }
  let taskStorageError=false;
  let tasks;
  try { tasks = MS8ATTasks.create({
    storage:{load:()=>JSON.parse(read("ms8at_tasks") || "null"),save:s=>write("ms8at_tasks",JSON.stringify(s))},
    call:(messages,opt)=>{
      if(!core.snapshot().enabled) throw new Error("routing_disabled");
      const localized=messages.map(m=>m.role==="system"?{...m,content:m.content+"\n"+DewiarLanguage.mode(S.language).prompt}:m);
      return call(localized,null,null,opt.signal,{purpose:opt.purpose,max:opt.max});
    },
    memory:{read:a=>memory.get(a.id,{purpose:"task"}),search:a=>memory.search(a.query,{purpose:"task",limit:5})}
  }); } catch (_) {
    taskStorageError=true;
    const blocked=()=>{throw new Error("task_storage_unavailable");};
    tasks={snapshot:()=>({tasks:[],status:"storage_unavailable"}),detail:blocked,add:blocked,start:blocked,stop:blocked,subscribe:()=>{}};
  }
  const check = (id,label,value) => `<label class="ms8-check"><input type="checkbox" id="${id}" ${value?"checked":""}> ${esc(label)}</label>`;
  const btn = (id,text) => `<button class="btn" id="${id}">${esc(text)}</button>`;
  let selectedTask = "";
  function render() {
    sync(); const w=tr(), st=core.tick(), cfg=core.getConfig();
    const options = (role)=>(cfg.routes[role] && cfg.routes[role]!=="auto" && !profiles.has(cfg.routes[role]) ? `<option selected disabled value="${esc(cfg.routes[role])}">${esc(w.unavailable)}</option>`:"")+`<option value="">${esc(w.none)}</option><option value="auto" ${cfg.routes[role]==="auto"?"selected":""}>${esc(w.auto)}</option>`+[...profiles].map(([id,p])=>`<option value="${id}" ${cfg.routes[role]===id?"selected":""}>${esc(brainNameOf(p))}</option>`).join("");
    const phtml=[...profiles].map(([id,p])=>`<div class="ms8-model"><b>${esc(brainNameOf(p))}</b>${check("tools-"+id,w.tools,p.ms8at_tools)}${check("vision-"+id,label("Модель понимает картинки","Model supports images","模型支持图像"),p.ms8at_vision)}<div class="ms8-roles">${roles.map(r=>check("auto-"+r+"-"+id,w[r],cfg.auto[r].includes(id))).join("")}</div></div>`).join("");
    $("#constructor-body").innerHTML=`<h2>${esc(w.title)}</h2><p class="hint">${esc(w.connect)}</p>${btn("ms8-brains",w.brains)}<div class="card">${check("ms8-enabled",w.enabled,st.enabled)}${roles.map(r=>`<label class="f"><span>${esc(w[r])}</span><select id="route-${r}">${options(r)}</select></label>`).join("")}<h3>${esc(w.allow)}</h3>${phtml}${btn("ms8-save",w.save)}</div>
      <h3>${esc(w.tasks)}</h3><p class="hint">${esc(w.foreground)}</p><div class="card"><label class="f"><span>${esc(w.goal)}</span><textarea id="ms8-goal" maxlength="4000"></textarea></label><label class="f"><span>Requests (3–20)</span><input id="ms8-budget" type="number" min="3" max="20" value="5"></label>${check("ms8-task-memory",w.taskread,false)}${check("ms8-task-review",w.check,false)}${btn("ms8-create",w.queue)}<div id="ms8-task-list"></div><div id="ms8-task-detail"></div></div>
      <h3>${esc(w.local)}</h3><div class="card">${check("mem-enabled",w.local,permissions.enabled)}${check("mem-read",w.read,permissions.read)}${check("mem-write",w.write,permissions.write)}${check("mem-tasks",w.taskread,permissions.tasks)}${btn("ms8-mem-save",w.save)}<label class="f"><textarea id="ms8-note" maxlength="4000"></textarea></label>${btn("ms8-note-add",w.add)}${btn("ms8-note-search",w.search)}<pre id="ms8-memory-result"></pre><p>Human Memory / Semantic: ${esc(w.unavailable)}</p></div>
      <h3>${esc(w.doctor)}</h3>${btn("ms8-doctor",w.checkHealth)}<pre id="ms8-doctor-result" role="status"></pre><h3>${esc(w.logs)}</h3><p class="hint">${esc(w.privacy)}</p>${btn("ms8-refresh",w.refresh)}<pre id="ms8-log"></pre><h3>${esc(w.developer)}</h3><p class="hint">${esc(w.devhint)}</p>${btn("ms8-editor","VS Code · code-server")}${btn("ms8-terminal","Termux · Codex CLI")}${btn("ms8-edge","Microsoft Edge") }<p id="ms8-vault"></p><div id="ms8-result" role="status"></div>`;
    const safe=fn=>async()=>{try{await fn();}catch(e){$("#ms8-result").textContent=core.diagnose(String(e.message||e)).code;}};
    $("#ms8-brains").onclick=()=>openSettings("brain");
    $("#ms8-editor").onclick=()=>D.openUrl("http://127.0.0.1:8787");
    $("#ms8-terminal").onclick=()=>D.openApp("Termux");
    $("#ms8-edge").onclick=()=>{if(!D.openApp("Microsoft Edge"))D.openUrl("https://play.google.com/store/apps/details?id=com.microsoft.emmx");};
    if(D.securePrefsStatus){try{const v=JSON.parse(D.securePrefsStatus());$("#ms8-vault").textContent="Android Keystore: "+v.settings;}catch(_) {$("#ms8-vault").textContent="Android Keystore: unavailable";}}
    if(taskStorageError)$("#ms8-result").textContent="Task storage unavailable — data preserved";
    if(["unavailable","corrupt_or_unavailable"].includes(st.storage))$("#ms8-result").textContent=label("Настройки не сохранены. Запросы заблокированы.","Settings could not be saved. Requests blocked.","设置无法保存，请求已阻止。");
    $("#ms8-save").onclick=safe(()=>{
      for(const [id,p] of profiles){p.ms8at_tools=$("#tools-"+id).checked;p.ms8at_vision=$("#vision-"+id).checked;}
      saveS(); sync();
      for(const r of roles){const ids=[...profiles.keys()].filter(id=>$("#auto-"+r+"-"+id).checked); core.allowAuto(r,ids);core.assign(r,$("#route-"+r).value);}
      core.setEnabled($("#ms8-enabled").checked); render();
    });
    $("#ms8-create").onclick=safe(()=>{selectedTask=tasks.add({title:$("#ms8-goal").value.slice(0,80),goal:$("#ms8-goal").value,budget:Number($("#ms8-budget").value),memoryRead:$("#ms8-task-memory").checked,review:$("#ms8-task-review").checked});updateTasks();});
    $("#ms8-mem-save").onclick=safe(()=>{const next={};for(const k of Object.keys(permissions))next[k]=$("#mem-"+k).checked;write("ms8at_memory_permissions",JSON.stringify(next));permissions=next;memory.configure(permissions);});
    $("#ms8-note-add").onclick=safe(async()=>{$("#ms8-memory-result").textContent=JSON.stringify(await memory.add({text:$("#ms8-note").value,tags:[]}));});
    $("#ms8-note-search").onclick=safe(async()=>{$("#ms8-memory-result").textContent=JSON.stringify(await memory.search($("#ms8-note").value),null,2);});
    $("#ms8-refresh").onclick=()=>{core.tick();updateLog();updateTasks();};updateLog();updateTasks();
    $("#ms8-doctor").onclick=()=>updateDoctor();updateDoctor();
  }
  function updateDoctor(){
    const el=$("#ms8-doctor-result");if(!el)return;
    const report=core.health(),w=tr(),state=report.status==="ready"?w.ready:report.status==="blocked"?w.blocked:w.attention;
    el.textContent=[state,...report.purposes.map(row=>`${w[row.purpose]}: ${row.ok?w.ready:(row.code==="routing_disabled"?w.routingDisabled:(w.reason[row.code]||row.code))}`)].join("\n");
  }
  function updateLog(){const el=$("#ms8-log");if(el)el.textContent=JSON.stringify({inFlight:core.snapshot().inFlight,events:core.snapshot().events.slice(-12)},null,2);}
  function updateTasks(){
    const el=$("#ms8-task-list");if(!el)return;const w=tr(), all=tasks.snapshot().tasks;
    el.innerHTML=all.map(t=>`<div class="ms8-task"><button class="btn" data-detail="${esc(t.id)}">${esc(tasks.detail(t.id).title)}</button> <span>${esc(t.status)} · ${t.calls || 0}</span><button class="btn" data-run="${esc(t.id)}">${esc(w.start)}</button><button class="btn" data-stop="${esc(t.id)}">${esc(w.stop)}</button></div>`).join("");
    $$('[data-run]',el).forEach(b=>b.onclick=()=>{selectedTask=b.dataset.run;tasks.start(selectedTask).catch(()=>{}).finally(updateTasks);updateTasks();});
    $$('[data-stop]',el).forEach(b=>b.onclick=()=>{tasks.stop(b.dataset.stop);updateTasks();});
    $$('[data-detail]',el).forEach(b=>b.onclick=()=>{selectedTask=b.dataset.detail;updateTasks();});
    if(selectedTask){const d=tasks.detail(selectedTask);$("#ms8-task-detail").innerHTML=`<h3>${esc(d.title)}</h3><p>${esc(d.status)} · ${d.calls}/${d.budget}</p><label class="f"><span>${esc(label("Общий лимит запросов","Total request budget","总请求限制"))}</span><input id="ms8-total-budget" type="number" min="3" max="20" value="${d.budget}"></label><button class="btn" id="ms8-grant">${esc(w.save)}</button><ol>${d.plan.map(s=>`<li>${esc(s)}</li>`).join("")}</ol><p style="white-space:pre-wrap">${esc(d.result || d.reason || "")}</p><p>${esc(w.check)}: ${esc(d.reviewStatus || "off")}</p><p>${esc(d.reviewReason || "")}</p>${d.pendingResult?`<details><summary>${esc(label("Предварительный результат — ещё не принят","Draft result — not accepted yet","草稿结果 — 尚未确认"))}</summary><p style="white-space:pre-wrap">${esc(d.pendingResult)}</p></details>`:""}<details><summary>API / ${esc(w.logs)}</summary><pre>${esc(JSON.stringify(d.log,null,2))}</pre></details>`;}
    const grant=$("#ms8-grant");if(grant)grant.onclick=()=>{try{tasks.setBudget(selectedTask,Number($("#ms8-total-budget").value));updateTasks();}catch(e){$("#ms8-result").textContent="invalid_budget";}};
    updateLog();
  }
  tasks.subscribe(updateTasks);
  $("#b-constructor").onclick=()=>{render();openSheet("#sh-constructor");};
  // Page lifecycle supplies heartbeat; no extra OS service or automatic request loop.
  document.addEventListener("visibilitychange",()=>{core.tick();updateLog();});
  return {core,memory,tasks,call,sync,render,open:()=>{$("#b-constructor").click();},status:()=>({core:core.tick(),tasks:tasks.snapshot(),memory:memory.status()})};
})();
