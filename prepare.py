from pathlib import Path
import json,re,html
root=Path('.')
s=(root/'preview.html').read_text()
i=s.index('const routes=')+len('const routes=')
routes,_=json.JSONDecoder().raw_decode(s[i:])
assert len(routes)==33
head=s[:s.index('<div id="view">')]
footer=s[s.index('<footer class="shell footer">'):s.index('<script>const routes=')]
css=re.search(r'<style>(.*?)</style>',head,re.S).group(1)
head=head.replace('<style>'+css+'</style>','<link rel="stylesheet" href="/style.css">')
head=head.replace('<title>OWSPACE — 官网预览</title>','<title>__PAGE_TITLE__</title>')
(root/'public').mkdir(exist_ok=True)
(root/'public/style.css').write_text(css)
(root/'src/pages').mkdir(parents=True,exist_ok=True)
(root/'src/lib').mkdir(parents=True,exist_ok=True)
(root/'src/lib/routes.json').write_text(json.dumps(routes,ensure_ascii=False,indent=2))
(root/'src/lib/shell.json').write_text(json.dumps({'head':head,'footer':footer},ensure_ascii=False,indent=2))
(root/'src/pages/[...path].astro').write_text("""---
import routes from '../lib/routes.json';
import shell from '../lib/shell.json';
export function getStaticPaths() {
  return Object.keys(routes).map(route => ({params:{path:route === '/' ? undefined : route.slice(1,-1)},props:{route}}));
}
const {route} = Astro.props;
const body = routes[route];
const heading = body.match(/<h1>(.*?)<\\/h1>/s)?.[1]?.replace(/<[^>]+>/g,'') || '独立软件工作室';
const title = route === '/' ? 'OWSPACE — 独立软件工作室' : heading + ' · OWSPACE';
---
<Fragment set:html={shell.head.replace('__PAGE_TITLE__', title) + body + shell.footer + '</body></html>'} />
""")
(root/'package.json').write_text(json.dumps({'name':'owspace-studio','version':'0.1.0','private':True,'type':'module','scripts':{'dev':'astro dev','build':'astro build','preview':'astro preview'},'dependencies':{'astro':'^5.0.0'}},indent=2))
(root/'astro.config.mjs').write_text("import {defineConfig} from 'astro/config';\nexport default defineConfig({site:'https://owspace.github.io',output:'static',trailingSlash:'always'});\n")
(root/'.gitignore').write_text('node_modules/\ndist/\n.astro/\n.DS_Store\n')
(root/'README.md').write_text('# OWSPACE 官网 V0.1\n\n原始首版预览拆为 33 个实际路由。Astro 源码从首版 HTML 数据重建，视觉和文案保留；docs 为已生成的 GitHub Pages 静态发布目录。\n\n- npm install && npm run dev\n- npm run build：生成 dist；更新 docs 以发布。\n\n网站为开发预览，所有页面保留 noindex。隐私政策是待审核草稿，支持联系渠道待补充，概念图并非实际产品截图。\n')
for route,body in routes.items():
    p=root/'docs'/route.strip('/')
    p.mkdir(parents=True,exist_ok=True)
    m=re.search(r'<h1>(.*?)</h1>',body,re.S)
    title='OWSPACE — 独立软件工作室' if route=='/' else (re.sub(r'<[^>]+>','',m[1]) if m else 'OWSPACE')+' · OWSPACE'
    (p/'index.html').write_text(head.replace('__PAGE_TITLE__',html.escape(title))+body+footer+'</body></html>')
(root/'docs/style.css').write_text(css)
(root/'docs/.nojekyll').touch()
for p in (root/'docs').rglob('*.html'):
    for href in re.findall(r'href="(/[^"]*)"',p.read_text()):
        target=href.split('#')[0]
        assert (root/'docs'/target.strip('/')/'index.html').exists() or (root/'docs'/target.strip('/')).is_file(), (p,href)
print('Generated and checked 33 static routes.')
