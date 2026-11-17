import {readFile,readdir,access} from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=fileURLToPath(new URL('../',import.meta.url));
const data=JSON.parse(await readFile(path.join(root,'content/site.json'),'utf8'));
const assert=(v,m)=>{if(!v)throw new Error(m)};
assert(['preview','published'].includes(data.publication),'Unknown publication mode');
assert(data.locale==='ja','Initial locale must be ja');
const ids=new Set(),categories=new Set(data.categories.map(c=>c.id));
const statuses=new Set(['実施済み','開発中','検証中','企画中','将来構想']);
for(const p of data.projects){assert(/^[a-z0-9-]+$/.test(p.id),'Unsafe project id');assert(!ids.has(p.id),'Duplicate project id');ids.add(p.id);assert(categories.has(p.category),'Unknown category');assert(statuses.has(p.status),'Unknown status');assert(p.source&&p.summary&&p.body&&p.next.length,'Missing project evidence/content');}
for(const l of data.logs)assert(!l.project||ids.has(l.project),'Broken log reference');
for(const group of [data.logs,data.timeline,data.ideas,data.roadmap])for(const x of group)assert(statuses.has(x.status),'Unknown item status');
for(const [name,url] of Object.entries(data.links)){if(url)assert(new URL(url).protocol==='https:',`Unsafe ${name} URL`);}
if(data.contactEmail)assert(/^[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+$/.test(data.contactEmail),'Invalid contact address');
const dist=path.join(root,'dist'), files=await readdir(dist);let links=0;
for(const name of files.filter(x=>x.endsWith('.html'))){const html=await readFile(path.join(dist,name),'utf8');assert((html.match(/<h1[ >]/g)||[]).length===1,`Expected one h1: ${name}`);assert(html.includes('lang="ja"'),`Missing language: ${name}`);assert(!/undefined|\[object Object\]/.test(html),`Invalid render: ${name}`);if(data.publication==='preview')assert(html.includes('noindex,nofollow'),`Preview indexing: ${name}`);for(const m of html.matchAll(/(?:href|src)="([^"]+)"/g)){const target=m[1];if(/^(https:|mailto:|#)/.test(target))continue;const clean=target.split(/[?#]/)[0];await access(path.join(dist,clean));links++;const anchor=target.includes('#')?target.split('#')[1]:null;if(anchor){const targetHtml=await readFile(path.join(dist,clean),'utf8');assert(targetHtml.includes(`id="${anchor}"`),`Missing anchor: ${target}`);}}}
console.log(`PASS: ${data.projects.length} projects, ${files.filter(f=>f.endsWith('.html')).length} pages, ${links} local link/asset references, states and preview guards.`);
