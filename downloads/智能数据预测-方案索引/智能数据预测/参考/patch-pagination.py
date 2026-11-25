#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把列表页分页器换成 BOE 组件库 4-6-pagination 的原生组件（样式 + DOM 契约）。
- 样式：直接抽取 library3.1/src/demo/components/pagination-module.css 里
  BOE_COMPONENT_STYLE_START/END: 4-6-pagination 区块，作用域由 .pagination-module-details 换成 .list-page
- 只额外保留一个 .pagination-dock 定位容器（right/bottom 24px），不改组件本身
"""
import re

PAGE = '/Users/gaicibi/WorkBuddy/工业 AI 平台/智能数据预测/智能数据预测设计稿-20261117-v1.html'
LIB = '/Users/gaicibi/WorkBuddy/工业 AI 平台/library3.1/src/demo/components/pagination-module.css'

page = open(PAGE, encoding='utf-8').read()
lib = open(LIB, encoding='utf-8').read()

# ---------- 1. 抽取组件库分页样式 ----------
start = lib.index('/* BOE_COMPONENT_STYLE_START: 4-6-pagination */')
end = lib.index('/* BOE_COMPONENT_STYLE_END: 4-6-pagination */')
block = lib[start:end]
# 去掉每行 4 空格缩进
block = '\n'.join(line[4:] if line.startswith('    ') else line for line in block.split('\n'))
# 作用域：.pagination-module-details -> .list-page
cnt = block.count('.pagination-module-details ')
block = block.replace('.pagination-module-details ', '.list-page ')
assert '.pagination-module-details' not in block, '仍有未替换的作用域'
print('组件样式规则数：%d，原始 .pagination-module-details 出现 %d 次' % (block.count('{'), cnt))

NEW_CSS = """/* ---------- 9. 分页（pagination · 直接使用 BOE 组件库 4-6-pagination） ----------
   组件样式取自 library3.1/src/demo/components/pagination-module.css，
   作用域指向 .list-page，未改动任何组件视觉属性；此处只补一个定位容器。 */
.list-page .pagination-dock {
  position: fixed;
  z-index: 25;
  right: 24px;
  bottom: 24px;
  display: flex;
}

""" + block + """
"""

cs = page.index('/* ---------- 9. 分页（pagination） ---------- */')
ce = page.index('/* ---------- 10. 响应式 ---------- */')
page = page[:cs] + NEW_CSS + page[ce:]

# ---------- 2. 移除对组件的响应式/动效覆盖 ----------
page = page.replace("  .list-page .boe-pagination-wrap { flex-wrap: wrap; }\n", "")
page = page.replace("  .list-page .boe-page-btn { transition: none; }\n", "")

# ---------- 3. 分页 DOM 按组件契约重写 ----------
lines = page.split('\n')
i0 = None
for idx, l in enumerate(lines):
    if l.startswith(' start=Math.max(1,listPage-2);end=Math.min(pages,start+4);start=Math.max(1,end-4);'):
        i0 = idx
        break
assert i0 is not None, '未找到分页渲染起始行'
# 校验 9 行
seg = lines[i0:i0 + 9]
assert seg[0].startswith(' start=Math.max(1,listPage-2)'), seg[0][:40]
assert seg[8].startswith(" pg+='<div class=\"boe-pagination-jumper\">"), seg[8][:40]

NEW_JS = r""" pg='<div class="pagination-dock"><div class="boe-pagination-wrap">';
 pg+='<span class="boe-pagination-total">共 '+rows.length+' 条</span>';
 pg+='<div class="boe-pagination">';
 pg+='<button type="button" class="boe-page-btn'+(listPage<=1?' disabled':'')+'" data-action="prev" aria-label="上一页" title="上一页"'+(listPage<=1?' disabled':'')+'>'+pageArrow('prev')+'</button>';
 var nums=pageList(listPage,pages);
 for(i=0;i<nums.length;i++){if(nums[i]==='…'){pg+='<span class="boe-page-ellipsis">…</span>';}else{pg+='<button type="button" class="boe-page-btn'+(nums[i]===listPage?' active':'')+'" data-action="gopage" data-page="'+nums[i]+'"'+(nums[i]===listPage?' aria-current="page"':'')+'>'+nums[i]+'</button>';}}
 pg+='<button type="button" class="boe-page-btn'+(listPage>=pages?' disabled':'')+'" data-action="next" aria-label="下一页" title="下一页"'+(listPage>=pages?' disabled':'')+'>'+pageArrow('next')+'</button></div>';
 pg+='<select class="boe-page-size-select" id="pageSize" aria-label="每页条数">'+options([[10,'10条/页'],[20,'20条/页'],[50,'50条/页']],listSize)+'</select>';
 pg+='<span class="boe-pagination-jumper"><span>跳至</span><input class="boe-page-jumper-input" id="pageJump" type="text" inputmode="numeric" value="'+listPage+'" aria-label="跳转页码"><span>页</span></span>';
 pg+='</div></div>';"""
lines[i0:i0 + 9] = NEW_JS.split('\n')
page = '\n'.join(lines)

# ---------- 4. 组件页码算法 / 箭头 SVG（与 pagination-module-runtime.js 一致） ----------
helper = r"""/* 分页器：页码窗口与箭头图形与组件库 pagination-module-runtime.js 完全一致 */
function pageList(cur,total){
 if(total<=7){var arr=[];for(var i=1;i<=total;i++){arr.push(i);}return arr;}
 if(cur<=4){return [1,2,3,4,5,'…',total];}
 if(cur>=total-3){return [1,'…',total-4,total-3,total-2,total-1,total];}
 return [1,'…',cur-2,cur-1,cur,cur+1,cur+2,'…',total];
}
function pageArrow(dir){
 var points=dir==='prev'?'9,2 4,7 9,12':'5,2 10,7 5,12';
 return '<svg class="boe-page-arrow" viewBox="0 0 14 14" aria-hidden="true"><polyline points="'+points+'" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>';
}
"""
page = page.replace('function renderList(){', helper + 'function renderList(){', 1)

open(PAGE, 'w', encoding='utf-8').write(page)
print('写入完成 %.2f MB' % (len(page) / 1024 / 1024))
