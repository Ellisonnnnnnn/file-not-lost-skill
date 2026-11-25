import re, sys

p = '/Users/gaicibi/WorkBuddy/工业 AI 平台/智能数据预测/智能数据预测设计稿-20261117-v1.html'
s = open(p, encoding='utf-8').read()
orig = len(s)

def once(old, new, tag):
    global s
    assert s.count(old) == 1, '[%s] count=%d' % (tag, s.count(old))
    s = s.replace(old, new)

# ---------- 1) 全局：内存态思考标记 ----------
once("timers={}, modalFocus=null, toastTimer=null;",
     "timers={}, thinkingTasks={}, thinkTimers={}, THINK_MS=1300, modalFocus=null, toastTimer=null;",
     'globals')

# ---------- 2) 样式：思考过程 + 步骤提示 ----------
CSS = '''
<style id="design-chat-think">
/* 冷启动后首轮：思考过程 → 总步数提示 → 条件确认卡，依次出现 */
.chat-page .think-box {
  box-sizing: border-box; width: 100%; max-width: 680px;
  border: 1px solid #E6EBF3; border-radius: 12px; background: #F7FAFE; overflow: hidden;
}
.chat-page .think-head { display: flex; align-items: center; gap: 7px; height: 38px; padding: 0 10px 0 13px; }
.chat-page .think-star { display: inline-flex; color: #5673EF; }
.chat-page .think-star svg { display: block; width: 14px; height: 14px; }
.chat-page .think-head b { font-size: 13px; font-weight: 500; color: #4E5A68; }
.chat-page .think-meta { margin-left: auto; color: #909399; font-size: 11.5px; font-variant-numeric: tabular-nums; }
.chat-page .think-toggle {
  margin-left: 6px; display: inline-flex; align-items: center; justify-content: center;
  width: 20px; height: 20px; padding: 0; border: 0; border-radius: 5px;
  background: transparent; color: #A8B0BE; cursor: pointer; transition: background .15s, color .15s;
}
.chat-page .think-toggle:hover { background: #E8EEF7; color: #606266; }
.chat-page .think-toggle svg { display: block; width: 12px; height: 12px; transition: transform .18s; }
.chat-page .think-lines { padding: 0 14px 12px 30px; }
.chat-page .think-line { position: relative; color: #606266; font-size: 12.5px; line-height: 21px; }
.chat-page .think-line + .think-line { margin-top: 2px; }
.chat-page .think-line::before {
  content: ""; position: absolute; left: -13px; top: 8px;
  width: 4px; height: 4px; border-radius: 50%; background: #C2CEDF;
}
.chat-page .think-box.is-thinking .think-line { opacity: 0; transform: translateY(2px); animation: iaiThinkIn .32s ease forwards; }
.chat-page .think-box.is-collapsed .think-lines { display: none; }
.chat-page .think-box.is-collapsed .think-toggle svg { transform: rotate(-90deg); }
.chat-page .think-dots { display: inline-flex; gap: 3px; margin-left: 1px; }
.chat-page .think-dots i { width: 4px; height: 4px; border-radius: 50%; background: #5673EF; opacity: .3; animation: iaiDot 1s infinite; }
.chat-page .think-dots i:nth-child(2) { animation-delay: .15s; }
.chat-page .think-dots i:nth-child(3) { animation-delay: .3s; }
@keyframes iaiThinkIn { to { opacity: 1; transform: none; } }
@keyframes iaiDot { 0%, 100% { opacity: .25; transform: translateY(0); } 50% { opacity: .95; transform: translateY(-2px); } }

.chat-page .step-strip {
  box-sizing: border-box; width: 100%; max-width: 680px; margin: 0 0 12px;
  padding: 11px 14px 12px; border: 1px solid #E6EBF3; border-radius: 12px; background: #FFF;
}
.chat-page .step-strip-top { display: flex; align-items: center; gap: 6px; color: #909399; font-size: 11.5px; line-height: 18px; }
.chat-page .step-strip-top b { color: #0072E3; font-weight: 600; }
.chat-page .step-strip-dot { width: 5px; height: 5px; border-radius: 50%; background: #0081FF; }
.chat-page .step-list { display: flex; align-items: center; gap: 8px; margin-top: 9px; }
.chat-page .step { display: inline-flex; align-items: center; gap: 6px; color: #909399; font-size: 12px; white-space: nowrap; }
.chat-page .step .n {
  display: inline-flex; align-items: center; justify-content: center;
  width: 17px; height: 17px; border-radius: 50%; background: #F0F3F8;
  color: #98A2B3; font-size: 10.5px; font-weight: 600; font-style: normal;
}
.chat-page .step.on { color: #303133; font-weight: 500; }
.chat-page .step.on .n { background: #0081FF; color: #FFF; }
.chat-page .step-sep { flex: 1 1 auto; height: 1px; min-width: 12px; background: #E7ECF3; }
</style>'''
i = s.find('<style id="design-chat-sample">')
assert i > 0
j = s.find('</style>', i) + len('</style>')
s = s[:j] + '\n' + CSS + s[j:]

# ---------- 3) 渲染：新增 think 消息 + ask 前插步骤提示 ----------
old_ask = """ else if(m.kind==='ask'){s+='<p class="assistant-text chat-message-bubble">'+esc(m.text)+'</p>'+(t.status==='asking'&&i===t.messages.length-1?configForm(t):'<div class="past-confirmation">此轮确认已结束，具体条件见后续记录。</div>');}"""
new_ask = """ else if(m.kind==='think'){s+=thinkHTML(t,m,i);}
 else if(m.kind==='ask'){var live=t.status==='asking'&&i===t.messages.length-1;s+=(live?stepStrip():'')+'<p class="assistant-text chat-message-bubble">'+esc(m.text)+'</p>'+(live?configForm(t):'<div class="past-confirmation">此轮确认已结束，具体条件见后续记录。</div>');}"""
once(old_ask, new_ask, 'messageHTML')

# ---------- 4) 提交需求：先思考，再出条件卡 ----------
old_commit = """t.messages.push({kind:'user',text:text,fileRefs:copy(refs.refs||[])});t.status='asking';t.step=1;t.messages.push({kind:'ask',text:refs.dataId?'已读取所引用的文件。请先核对日期、数值和汇总方式，再确认预测范围。':'已整理为下方条件；你可以直接选择和修改，不需要编写专业提示词。'});t.updated=time();save();renderChat();positionConfirm();}"""
new_commit = """t.messages.push({kind:'user',text:text,fileRefs:copy(refs.refs||[])});t.messages.push({kind:'think',steps:thinkStepsFor(t,text,refs),ms:0});t.updated=time();thinkingTasks[t.id]=Date.now();save();renderChat();scrollThread();settleThink(t.id);}
/* 思考结束：把 think 消息标记完成，再补上条件确认那一轮 */
function settleThink(id,delay){var started=thinkingTasks[id]||Date.now();clearTimeout(thinkTimers[id]);thinkTimers[id]=setTimeout(function(){delete thinkTimers[id];delete thinkingTasks[id];var t=findTask(id);if(!t){return;}var last=t.messages[t.messages.length-1];if(last&&last.kind==='think'){last.ms=Math.max(900,Date.now()-started);}t.status='asking';t.step=1;t.updated=time();t.messages.push({kind:'ask',text:askPromptText(t)});save();if(activeId===id&&view==='chat'){renderChat();positionConfirm();}else if(view==='list'){renderList();}},typeof delay==='number'?delay:THINK_MS);}
function askPromptText(t){return (t.config&&t.config.references&&t.config.references.length)?'已读取所引用的文件。请先核对日期、数值和汇总方式，再确认预测范围。':'已整理为下方条件；你可以直接选择和修改，不需要编写专业提示词。';}
function thinkStepsFor(t,text,refs){var c=t.config,mi=metricInfo(c),steps=[],brief=trimText(text||'');if(brief.length>44){brief=brief.slice(0,44)+'…';}steps.push('理解需求：'+brief);var el='指标「'+mi.label+'」· 跨度 '+c.horizon+' 天 · 置信区间 '+c.interval+'%';if(c.product&&c.product!=='全部产品'){el+=' · 产品 '+c.product;}steps.push('识别要素：'+el);var src=(refs&&refs.refs&&refs.refs.length)?('引用文件 '+refs.refs[0].name):'平台已接入数据';steps.push('匹配数据：'+src+'，历史区间 '+c.start+' ~ '+c.end);steps.push('待确认：指标、产品、历史区间、预测跨度共 4 项，确认后再核对数据');return steps;}
function thinkHTML(t,m,i){var running=!!thinkingTasks[t.id],steps=m.steps||[],k,lines='';for(k=0;k<steps.length;k++){lines+='<div class="think-line"'+(running?' style="animation-delay:'+(k*0.16).toFixed(2)+'s"':'')+'>'+esc(steps[k])+'</div>';}return '<div class="think-box'+(running?' is-thinking':'')+'"><div class="think-head"><span class="think-star" aria-hidden="true"><svg viewBox="0 0 16 16" fill="none"><path d="M8 1.6l1.35 3.55L13 6.5l-3.65 1.35L8 11.4 6.65 7.85 3 6.5l3.65-1.35L8 1.6z" fill="currentColor"/><path d="M12.4 10.6l.6 1.55 1.55.6-1.55.6-.6 1.55-.6-1.55L10.25 12.75l1.55-.6.6-1.55z" fill="currentColor" opacity=".5"/></svg></span><b>'+(running?'正在思考':'思考过程')+'</b>'+(running?'<span class="think-dots" aria-hidden="true"><i></i><i></i><i></i></span>':'<span class="think-meta">'+steps.length+' 条推理 · 用时 '+((m.ms||1200)/1000).toFixed(1)+'s</span>')+'<button type="button" class="think-toggle" data-action="toggleThink" aria-expanded="true" aria-label="收起思考过程"><svg viewBox="0 0 12 12" fill="none"><path d="M3 4.5L6 7.5L9 4.5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/></svg></button></div><div class="think-lines">'+lines+'</div></div>';}
function stepStrip(){var items=['确认预测条件','核对数据','生成预测'],k,list='';for(k=0;k<items.length;k++){if(k){list+='<i class="step-sep" aria-hidden="true"></i>';}list+='<span class="step'+(k===0?' on':'')+'"><i class="n">'+(k+1)+'</i>'+items[k]+'</span>';}return '<div class="step-strip"><div class="step-strip-top"><span class="step-strip-dot" aria-hidden="true"></span>共 3 步 · 当前第 <b>1</b> 步</div><div class="step-list">'+list+'</div></div>';}"""
once(old_commit, new_commit, 'commitRequest')

# ---------- 5) 动作：展开/收起思考过程 ----------
once("else if(a==='toggleTrace'){traceOpen=!traceOpen;renderChat();scrollThread();}",
     "else if(a==='toggleTrace'){traceOpen=!traceOpen;renderChat();scrollThread();}else if(a==='toggleThink'){var tb=el.closest('.think-box');if(tb){var cl=tb.classList.toggle('is-collapsed');el.setAttribute('aria-expanded',cl?'false':'true');}}",
     'dispatch')

# ---------- 6) 思考期间禁止再次发送 ----------
once("if(t.status==='running'||t.status==='loading'||fileUploadBusy){return;}",
     "if(t.status==='running'||t.status==='loading'||thinkingTasks[t.id]||fileUploadBusy){return;}",
     'send guard')
once("busy=t.status==='running'||t.status==='loading',",
     "busy=t.status==='running'||t.status==='loading'||!!thinkingTasks[t.id],",
     'composer busy')

# ---------- 7) 初始化修复：刷新时若停在思考中，直接补完这一轮 ----------
once("""for(var i=0;i<tasks.length;i++){if(tasks[i].status==='running'){tasks[i].status='stopped';tasks[i].messages.push({kind:'failure',text:'页面已重新打开，运行已暂停。可重新运行。'});}}""",
     """for(var i=0;i<tasks.length;i++){var tk=tasks[i];if(tk.status==='running'){tk.status='stopped';tk.messages.push({kind:'failure',text:'页面已重新打开，运行已暂停。可重新运行。'});}var tl=tk.messages.length?tk.messages[tk.messages.length-1]:null;if(tl&&tl.kind==='think'){if(!tl.ms){tl.ms=1200;}tk.status='asking';tk.step=1;tk.messages.push({kind:'ask',text:askPromptText(tk)});}}""",
     'init repair')

open(p, 'w', encoding='utf-8').write(s)
print('ok', orig, '->', len(s))
