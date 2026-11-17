const menu = document.querySelector('.menu-toggle');
const nav = document.querySelector('#nav');
menu?.addEventListener('click', () => {
  const open = menu.getAttribute('aria-expanded') !== 'true';
  menu.setAttribute('aria-expanded', String(open));
  nav.classList.toggle('open', open);
});
document.addEventListener('keydown', e=>{if(e.key==='Escape' && menu?.getAttribute('aria-expanded')==='true'){menu.setAttribute('aria-expanded','false');nav.classList.remove('open');menu.focus();}});
const form = document.querySelector('.filters');
if (form) {
  const search = document.querySelector('#search');
  const category = document.querySelector('#category');
  const status = document.querySelector('#status');
  const cards = [...document.querySelectorAll('#project-grid .project-card')];
  const apply = (updateUrl=true) => {
    const q=search.value.trim().toLocaleLowerCase('ja');
    let count=0;
    cards.forEach(card=>{
      const show=(category.value==='all'||card.dataset.category===category.value)&&(status.value==='all'||card.dataset.status===status.value)&&card.dataset.search.toLocaleLowerCase('ja').includes(q);
      card.hidden=!show;
      if(show)count++;
    });
    document.querySelector('#result-count').textContent=`${count} / ${cards.length} projects`;
    document.querySelector('#empty').hidden=count!==0;
    if(updateUrl){const url=new URL(location.href);url.search='';if(category.value!=='all')url.searchParams.set('category',category.value);if(status.value!=='all')url.searchParams.set('status',status.value);if(q)url.searchParams.set('q',search.value.trim());history.replaceState(null,'',url);}
  };
  const params=new URLSearchParams(location.search);
  if([...category.options].some(o=>o.value===params.get('category')))category.value=params.get('category');
  if([...status.options].some(o=>o.value===params.get('status')))status.value=params.get('status');
  search.value=params.get('q')||'';
  form.addEventListener('input',()=>apply());
  form.addEventListener('submit',e=>e.preventDefault());
  form.addEventListener('reset',()=>setTimeout(()=>apply(),0));
  apply(false);
}
