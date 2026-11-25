import io,sys
p='智能数据预测设计稿-20261117-v1.html'
s=open(p,encoding='utf-8').read()
orig=s

# 1) 函数拆分：renderResultPage -> 渲染对话打底 + 挂抽屉；主体抽成 resultBodyHTML
old_start="function renderResultPage(){var t=current(),r=selectedResult();if(!r){view='chat';render();return;}"
assert s.count(old_start)==1
new_start=("function renderResultPage(){var t=current(),r=selectedResult();if(!r){view='chat';render();return;}renderChat();mountResultDrawer(resultBodyHTML());}\n"
"/* 第 3 步结果：与核对数据同款右侧抽屉，浮在内容区上方 */\n"
"var resultDrawerIn=false;\n"
"function resultBodyHTML(){var t=current(),r=selectedResult();if(!r){return '';}")
s=s.replace(old_start,new_start)

# 2) 去掉整页外壳
old_wrap="""var x=metricInfo(r.config),file=r.config.inputType==='file',s='<section class="page result-page">'+taskHeader(t,true)+'<div class="full-result"><div class="chart-heading">"""
assert s.count(old_wrap)==1
s=s.replace(old_wrap,"""var x=metricInfo(r.config),file=r.config.inputType==='file',s='<div class="chart-heading">""")

# 3) 顶部工具条补「导出数据」
old_tools="select('resultVersion',versionOptions(t),resultIndex)+btn('图表显示','charts')"
assert s.count(old_tools)==1
s=s.replace(old_tools,"select('resultVersion',versionOptions(t),resultIndex)+btn('图表显示','charts')+btn('导出数据','exportMenu')")

# 4) 尾部：底栏按钮移到抽屉 footer，去掉 composer 与整页闭合
old_tail="""'<div class="result-actions">'+btn('导出 CSV','exportCSV')+btn('导出完整 JSON','exportJSON')+btn('调整条件再次预测','editConfig',true)+'</div><p class="result-note">'+''+' 解读依据当前数值，不代表已确定生产波动的原因。</p></div>'+composer(t)+'</section>';$('main').innerHTML=s;}"""
assert s.count(old_tail)==1
s=s.replace(old_tail,"""'<p class="result-note">解读依据当前数值，不代表已确定生产波动的原因。</p>';return s;}""")

open(p,'w',encoding='utf-8').write(s)
print('patched', len(orig)!=len(s))
