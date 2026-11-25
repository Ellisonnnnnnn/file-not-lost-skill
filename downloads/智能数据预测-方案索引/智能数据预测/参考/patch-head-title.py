# -*- coding: utf-8 -*-
"""对话页顶栏：去掉「任务名称」label、标题底框按文字宽、标签与标题同行对齐、删掉空态提示文案。"""
p = '智能数据预测设计稿-20261117-v1.html'
s = open(p, encoding='utf-8').read()

# ---------- 1) taskHeader 结构改写 ----------
old = """function taskHeader(t,results){return '<div class="detail-head"><div class="head-title"><button class="back" data-action="'+(results?'chat':view==='dataReview'?'reviewClose':'list')+'" aria-label="返回">‹</button><div>'+(results?'<h1>'+esc(t.name)+'</h1>':'<div class="inline-task-name"><label for="taskName">任务名称</label><input id="taskName" class="control" value="'+esc(t.name)+'" maxlength="60" aria-label="任务名称"'+(t.status==='running'?' disabled':'')+'></div>')+'<div class="subline">'+esc(t.id)+' · '+(results?'结果版本 '+(resultIndex+1):t.messages.length?esc(metricInfo(t.config).label)+' · 对话预测':'选择场景或上传数据开始')+'</div></div>'+tag(t.status)+storageStatus()+'</div><div class="actions">'+(results?btn('导出数据','exportMenu'):view==='dataReview'?'':(t.review&&t.status==='review'?btn('继续核对数据','reviewOpen'):'')+(t.results.length?btn('查看结果','fullResult'):'')+btn(traceOpen?'收起执行记录':'执行记录','toggleTrace'))+'</div></div>';}"""
assert s.count(old) == 1, s.count(old)

new = """function taskHeader(t,results){
 var back='<button class="back" data-action="'+(results?'chat':view==='dataReview'?'reviewClose':'list')+'" aria-label="返回">‹</button>';
 var nameHTML=results?'<h1>'+esc(t.name)+'</h1>':
  '<div class="chat-head-name"><span class="chat-task-name" data-value="'+esc(t.name)+'">'+
   '<input id="taskName" class="chat-task-name-input" value="'+esc(t.name)+'" maxlength="60" aria-label="任务名称"'+(t.status==='running'?' disabled':'')+'>'+
  '</span>'+tag(t.status)+storageStatus()+'</div>';
 var sub=esc(t.id);
 if(results){sub+=' · 结果版本 '+(resultIndex+1);}
 else if(t.messages.length){sub+=' · '+esc(metricInfo(t.config).label)+' · 对话预测';}
 var actions=results?btn('导出数据','exportMenu'):view==='dataReview'?'':(t.review&&t.status==='review'?btn('继续核对数据','reviewOpen'):'')+(t.results.length?btn('查看结果','fullResult'):'')+btn(traceOpen?'收起执行记录':'执行记录','toggleTrace');
 return '<div class="detail-head"><div class="head-title">'+back+
  '<div class="head-main">'+nameHTML+'<div class="subline">'+sub+'</div></div>'+
  '</div><div class="actions">'+actions+'</div></div>';
}"""
s = s.replace(old, new)

# ---------- 2) 样式：替换旧的 inline-task-name 覆盖 ----------
old_css = """.chat-page .head-title { gap: 10px; }
.chat-page .inline-task-name { margin-bottom: 2px; }
.chat-page .inline-task-name .control { height: 28px; padding: 0 8px; font-size: 15px; }
.chat-page .subline { margin-top: 0; line-height: 16px; }"""
assert s.count(old_css) == 1, s.count(old_css)

new_css = """.chat-page .head-title { gap: 8px; align-items: center; }
.chat-page .head-main { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.chat-page .chat-head-name { display: flex; align-items: center; gap: 6px; min-width: 0; }
/* 任务名：默认无底框，宽度贴合文字；hover / focus 才出底框 */
.chat-page .chat-task-name { position: relative; display: inline-block; max-width: 360px; min-width: 0; }
.chat-page .chat-task-name::after {
  content: attr(data-value) " ";
  display: block;
  overflow: hidden;
  padding: 0 9px;
  font-size: 15px;
  font-weight: 600;
  line-height: 26px;
  white-space: pre;
  text-overflow: ellipsis;
  visibility: hidden;
}
.chat-page .chat-task-name-input {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  box-sizing: border-box;
  width: 100%;
  height: 26px;
  padding: 0 8px;
  border: 1px solid transparent;
  border-radius: 4px;
  background: transparent;
  color: #1F2733;
  font-family: inherit;
  font-size: 15px;
  font-weight: 600;
  line-height: 24px;
  text-overflow: ellipsis;
  transition: border-color .15s ease, background-color .15s ease, box-shadow .15s ease;
}
.chat-page .chat-task-name-input:hover { border-color: #DCDFE6; background: #FFF; }
.chat-page .chat-task-name-input:focus {
  border-color: #0081FF;
  background: #FFF;
  outline: none;
  box-shadow: 0 0 0 2px rgba(0, 129, 255, .12);
}
.chat-page .chat-task-name-input:disabled { color: #1F2733; -webkit-text-fill-color: #1F2733; cursor: default; }
.chat-page .chat-head-name > .boe-tag { flex: 0 0 auto; }
.chat-page .head-main > .subline { margin-top: 0; line-height: 16px; }"""
s = s.replace(old_css, new_css)

# ---------- 3) 输入时同步 ghost 宽度 ----------
old_in = "function predictionInput(e){if(e.target.id==='taskName'){current().name=e.target.value;save();return true;}return false;}"
assert s.count(old_in) == 1
new_in = "function syncTaskNameWidth(el){var w=el.parentNode;if(w&&w.className&&w.className.indexOf('chat-task-name')>=0){w.setAttribute('data-value',el.value);}}\nfunction predictionInput(e){if(e.target.id==='taskName'){current().name=e.target.value;syncTaskNameWidth(e.target);save();return true;}return false;}"
s = s.replace(old_in, new_in)

old_ch = "function predictionChange(e){if(e.target.id==='taskName'){var value=trimText(e.target.value);if(!value){toast('任务名称不能为空，请填写后继续。');return true;}current().name=value;current().updated=time();save();return true;}return false;}"
assert s.count(old_ch) == 1
new_ch = "function predictionChange(e){if(e.target.id==='taskName'){var value=trimText(e.target.value);if(!value){toast('任务名称不能为空，请填写后继续。');return true;}current().name=value;current().updated=time();syncTaskNameWidth(e.target);save();return true;}return false;}"
s = s.replace(old_ch, new_ch)

open(p, 'w', encoding='utf-8').write(s)
print('patched')
