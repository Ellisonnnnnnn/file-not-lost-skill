# -*- coding: utf-8 -*-
"""内容区底色对齐 BOE 规范：内容卡改用半透明渐变（2-2-content-surface），画布用浅色主题背景渐变，
并把表格行改为透明，避免纯白行把卡片渐变盖住。"""
p = '智能数据预测设计稿-20261117-v1.html'
s = open(p, encoding='utf-8').read()

# 1) body 底色跟随浅色主题背景渐变顶端（避免边缘露出旧的灰底）
old_body = 'color:#303133;background:#f5f7fa}'
assert s.count(old_body) == 1, s.count(old_body)
s = s.replace(old_body, 'color:#303133;background:#F8F9FF}')

# 2) 画布：--color-bg-container 实色 -> 浅色主题背景渐变（F8F9FF -> ECF2FF）
old_main = '.main{margin:48px 0 0 var(--aside);padding:16px 24px;min-width:0;background:var(--color-bg-container,#F5F7FA)}'
assert s.count(old_main) == 1
new_main = ('.main{margin:48px 0 0 var(--aside);padding:16px 24px;min-width:0;'
            'background:linear-gradient(180deg,#F8F9FF 0%,#ECF2FF 100%)}')
s = s.replace(old_main, new_main)

# 3) 内容区底框：实色 #fff -> BOE 2-2-content-surface 半透明渐变 + 白描边 + 阴影
old_page = ('.page{background:#fff;border-radius:12px;box-shadow:0 4px 10px #0000000f;'
            'min-height:calc(100vh - 80px);overflow:hidden}')
assert s.count(old_page) == 1
new_page = ('.page{background:linear-gradient(180deg,rgba(248,249,255,.851) 0%,rgba(247,248,251,1) 100%);'
            'border:1px solid rgba(255,255,255,.851);border-radius:12px;'
            'box-shadow:0 4px 10px rgba(0,0,0,.059);min-height:calc(100vh - 80px);overflow:hidden}')
s = s.replace(old_page, new_page)

# 4) 列表表格行透明，让底框渐变透上来（BOE 表格行原本铺 #fff，会盖掉卡片渐变）
old_tr = '.list-page .boe-table tbody tr { background: #fff; }'
assert s.count(old_tr) == 1, s.count(old_tr)
s = s.replace(old_tr, '.list-page .boe-table tbody tr { background: transparent; }')

open(p, 'w', encoding='utf-8').write(s)
print('patched')
