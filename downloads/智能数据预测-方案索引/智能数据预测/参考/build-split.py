#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把单文件原型拆成「列表页」+「任务页」两个自包含 HTML。
源：智能数据预测设计稿-20261117-v1.html（不改动）
出：智能数据预测-列表页-20261118-v2.html / 智能数据预测-任务页-20261118-v2.html
"""
import io, os, re, sys

SRC = '/Users/gaicibi/WorkBuddy/工业 AI 平台/智能数据预测/智能数据预测设计稿-20261117-v1.html'
OUT_DIR = '/Users/gaicibi/WorkBuddy/工业 AI 平台/智能数据预测/'
PAGE_LIST = '智能数据预测-列表页-20261118-v2.html'
PAGE_TASK = '智能数据预测-任务页-20261118-v2.html'

src = open(SRC, encoding='utf-8').read()

STATE_OLD = ("var KEY='iai-prediction-design-20261117-v1', tasks=[], activeId='', view='list', "
             "resultIndex=-1, traceOpen=false,")

HELPERS = """
/* ==== 双页面拆分：列表页 / 任务页（共用同一份 localStorage 任务库） ==== */
function toList(){
 if(PAGE_MODE==='TASK'){save();location.href=PAGE_LIST;}
 else{navOpen.asset=false;navOpen.train=true;view='list';render();}
}
function toTask(id,wantResult){
 if(PAGE_MODE==='LIST'){
  save();
  location.href=PAGE_TASK+'?task='+encodeURIComponent(id)+(wantResult?'&view=result':'');
 }else{openTask(id,wantResult);}
}
"""


def once(s, old, new, tag):
    if s.count(old) != 1:
        raise SystemExit('[FAIL] %s: 命中 %d 次' % (tag, s.count(old)))
    return s.replace(old, new)


def build(mode, out_name):
    s = src

    # 1) 页面模式常量
    s = once(s, STATE_OLD,
             "var KEY='iai-prediction-design-20261117-v1', PAGE_MODE='%s', "
             "PAGE_LIST='%s', PAGE_TASK='%s', tasks=[], activeId='', view='list', "
             "resultIndex=-1, traceOpen=false," % (mode, PAGE_LIST, PAGE_TASK),
             'state')

    # 2) 路由助手：插到状态声明后（紧跟该行换行）
    anchor = "listSort='desc', timers={}, modalFocus=null, toastTimer=null;\n"
    s = once(s, anchor, anchor + HELPERS, 'helpers')

    # 3) render 守卫
    s = once(s, 'function render(){stopReviewDrag();drawShell();',
             "function render(){"
             "if(PAGE_MODE==='LIST'&&(view==='chat'||view==='dataReview'||view==='result')){view='list';}"
             "if(PAGE_MODE==='TASK'&&(view==='list'||!current())){location.replace(PAGE_LIST);return;}"
             "stopReviewDrag();drawShell();",
             'render')

    # 4) openTask：列表页跳转 / 任务页就地渲染，支持直接落到结果页
    s = once(s,
             "function openTask(id){activeId=id;resultIndex=-1;var t=current();hydrateTaskFiles(t);"
             "view=t.status==='review'||t.status==='loading'?'dataReview':'chat';render();"
             "if(view==='chat'){scrollThread();}}",
             "function openTask(id,wantResult){"
             "if(PAGE_MODE==='LIST'){toTask(id,wantResult);return;}"
             "activeId=id;resultIndex=-1;var t=current();if(!t){toList();return;}"
             "hydrateTaskFiles(t);"
             "view=t.status==='review'||t.status==='loading'?'dataReview':'chat';"
             "if(view==='chat'&&wantResult&&t.results.length){view='result';resultIndex=t.results.length-1;}"
             "render();if(view==='chat'){scrollThread();}}",
             'openTask')

    # 5) init 尾部：任务页按 ?task= 定位，列表页保持默认
    s = once(s,
             "initSources();bindTaskSources();initFileStore();initPredictionReview();drawShell();render();save();",
             "initSources();bindTaskSources();initFileStore();initPredictionReview();\n"
             "var bootNote='';\n"
             "if(PAGE_MODE==='TASK'){\n"
             " var qp=null;try{qp=new URLSearchParams(location.search);}catch(ignore){}\n"
             " var wanted=qp?qp.get('task'):'',t=wanted?findTask(wanted):null;\n"
             " if(wanted&&!t){bootNote='未找到该任务，已打开最近的任务。';}\n"
             " if(!t){t=tasks[0]||null;}\n"
             " if(t){activeId=t.id;hydrateTaskFiles(t);\n"
             "  if(qp&&qp.get('view')==='result'&&t.results.length){resultIndex=t.results.length-1;view='result';}\n"
             "  else if(t.status==='review'||t.status==='loading'){view='dataReview';}\n"
             "  else{view='chat';}\n"
             " }else{bootNote='任务库为空，请先在列表页新建预测任务。';}\n"
             "}\n"
             "drawShell();render();save();\n"
             "if(bootNote&&document.getElementById('toast')){toast(bootNote);}",
             'init')

    # 6) 返回列表：跨页跳转
    s = once(s, "if(a==='list'){navOpen.asset=false;navOpen.train=true;view='list';render();}",
             "if(a==='list'){toList();}", 'dispatch-list')

    # 7) 行操作：完成态直接进结果页
    s = once(s,
             "<button type=\"button\" class=\"boe-table__action\" data-action=\"open\" data-id=\"'+t.id+'\">",
             "<button type=\"button\" class=\"boe-table__action\" data-action=\"open\" data-id=\"'+t.id+'\" "
             "data-result=\"'+(t.status==='complete'?'1':'0')+'\">",
             'row-open')
    s = once(s, "else if(a==='open'){openTask(id);}",
             "else if(a==='open'){openTask(id,el.getAttribute('data-result')==='1');}",
             'dispatch-open')

    # 8) 列表页不渲染对话（避免复制配置后短暂刷出对话）
    s = once(s, "function renderChat(){var t=current();",
             "function renderChat(){if(PAGE_MODE==='LIST'){return;}var t=current();",
             'renderChat')

    # 9) 标题
    s = once(s, '<title>智能数据预测 · 工业AI平台 · v12</title>',
             '<title>智能数据预测 · %s · 工业AI平台</title>' % ('预测任务列表' if mode == 'LIST' else '预测任务'),
             'title')

    # 10) 任务页静态首屏：注入对话页快照（无脚本也能看到页面）
    if mode == 'TASK':
        snap_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'task-static.html')
        snap = open(snap_path, encoding='utf-8').read() if os.path.exists(snap_path) else \
            '<section class="page chat-page"></section>'
        m = re.search(r'<main id="main"[^>]*>', s)
        if not m:
            raise SystemExit('[FAIL] 未找到 main 容器')
        start = m.end()
        end = s.index('</main>', start)
        s = s[:start] + snap + s[end:]

    out = os.path.join(OUT_DIR, out_name)
    open(out, 'w', encoding='utf-8').write(s)
    print('[OK] %s  %.2f MB' % (out_name, len(s) / 1024 / 1024))
    return out


if __name__ == '__main__':
    build('LIST', PAGE_LIST)
    build('TASK', PAGE_TASK)
