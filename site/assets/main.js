(() => {
  'use strict';
  document.documentElement.classList.add('js');
  const config = window.PETER_WADE_SITE || {};
  const email = typeof config.contactEmail === 'string' ? config.contactEmail.trim() : '';
  const emailReady = /^[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+$/.test(email) && !/[\r\n?#]/.test(email);
  const ready = config.launchApproved === true && emailReady;
  document.querySelectorAll('[data-year]').forEach(el => { el.textContent = String(new Date().getFullYear()); });

  const menu = document.querySelector('.menu-toggle');
  const nav = document.getElementById('primary-nav');
  if (menu && nav) {
    const closeMenu = () => { nav.classList.remove('open'); menu.setAttribute('aria-expanded', 'false'); };
    menu.addEventListener('click', () => { const open = menu.getAttribute('aria-expanded') !== 'true'; menu.setAttribute('aria-expanded', String(open)); nav.classList.toggle('open', open); });
    nav.querySelectorAll('a').forEach(a => a.addEventListener('click', closeMenu));
    document.addEventListener('keydown', e => { if (e.key === 'Escape' && nav.classList.contains('open')) { closeMenu(); menu.focus(); } });
    document.addEventListener('click', e => { if (!nav.contains(e.target) && !menu.contains(e.target)) closeMenu(); });
    window.matchMedia('(min-width: 721px)').addEventListener('change', closeMenu);
  }

  const tabs = [...document.querySelectorAll('.level-tab')];
  const tablist = document.querySelector('.level-tabs');
  if (tablist && tabs.length) {
    tablist.setAttribute('role', 'tablist');
    tabs.forEach(tab => { tab.setAttribute('role', 'tab'); const panel=document.getElementById(tab.getAttribute('aria-controls')); if(panel) {panel.setAttribute('role','tabpanel'); panel.tabIndex=0;} });
    const activate = (target, focus = false) => {
      tabs.forEach(tab => { const active=tab===target; tab.setAttribute('aria-selected',String(active)); tab.tabIndex=active?0:-1; const panel=document.getElementById(tab.getAttribute('aria-controls')); if(panel) panel.hidden=!active; });
      if(focus) target.focus();
    };
    tabs.forEach((tab,index) => {
      tab.addEventListener('click',()=>activate(tab));
      tab.addEventListener('keydown',e=>{
        let next;
        if(e.key==='ArrowRight')next=(index+1)%tabs.length;
        if(e.key==='ArrowLeft')next=(index-1+tabs.length)%tabs.length;
        if(e.key==='Home')next=0;
        if(e.key==='End')next=tabs.length-1;
        if(next!==undefined){e.preventDefault();activate(tabs[next],true);}
      });
    });
    activate(tabs.find(tab=>tab.dataset.level==='undergraduate') || tabs[0]);
  }
  document.querySelectorAll('[data-select-level]').forEach(link=>link.addEventListener('click',()=>{const field=document.getElementById('enquiry-level');if(field)field.value=link.dataset.selectLevel;}));
  document.querySelectorAll('[data-print]').forEach(button=>button.addEventListener('click',()=>window.print()));
  document.querySelectorAll('[data-contact-email]').forEach(el=>{if(ready){el.textContent=email;el.href='mailto:'+email;}else{el.textContent='Contact details are pending in this preview.';el.removeAttribute('href');}});
  document.querySelectorAll('[data-preview-only]').forEach(el=>{el.hidden=ready;});
  const status=document.getElementById('contact-status');
  const direct=document.getElementById('direct-email');
  if(ready){
    if(status)status.textContent='This enquiry tool prepares an email draft. Nothing is sent or stored by the website. Scope, fees and availability are agreed separately.';
    if(direct){direct.textContent=email;direct.href='mailto:'+email;direct.hidden=false;}
  }

  const form=document.getElementById('enquiry-form');
  if(!form)return;
  const panel=document.getElementById('draft-panel');
  const draftText=document.getElementById('draft-text');
  const draftStatus=document.getElementById('draft-status');
  const emailLink=document.getElementById('open-email');
  // Keep disabled until our preventDefault handler is attached. With JavaScript disabled,
  // personal data cannot accidentally be submitted in the URL to a static host.
  form.addEventListener('submit',event=>{
    event.preventDefault();
    if(!form.reportValidity())return;
    const data=new FormData(form);
    const get=key=>String(data.get(key)||'').trim();
    const select=document.getElementById('enquiry-level');
    const label=select.options[select.selectedIndex].textContent;
    const subject='Educational enquiry: '+get('topic').replace(/[\r\n]/g,' ');
    const text=['Hello Peter,','',get('message'),'','My details:','Name: '+get('name'),'Email: '+get('email'),'Learning stage: '+label,'Subject / topic: '+get('topic'),'Enquiry made by an adult or parent/guardian.','','Thank you,',get('name')].join('\n');
    draftText.value=text;
    panel.hidden=false;
    if(ready){
      emailLink.href='mailto:'+email+'?subject='+encodeURIComponent(subject)+'&body='+encodeURIComponent(text);
      emailLink.hidden=false;
      draftStatus.textContent='Your draft is ready. It has not been sent. Open your email app to review it and send it to '+email+'. You can also copy the text below.';
    }else{
      emailLink.removeAttribute('href');emailLink.hidden=true;
      draftStatus.textContent='Preview only: Peter’s contact address has not been connected. Nothing has been sent. You can copy this draft, but enquiries are not open through this preview.';
    }
    panel.scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'nearest'});
  });
  document.getElementById('enquiry-fields').disabled=false;
  document.getElementById('copy-draft').addEventListener('click',async()=>{
    try{
      if(!navigator.clipboard || !window.isSecureContext)throw new Error('Clipboard unavailable');
      await navigator.clipboard.writeText(draftText.value);
      draftStatus.textContent='Draft copied. Nothing has been sent.';
    }catch(_error){
      draftText.focus();draftText.select();draftText.setSelectionRange(0,draftText.value.length);
      draftStatus.textContent='Your draft is selected. Use Copy on your device, or press Ctrl+C / Command+C. Nothing has been sent.';
    }
  });
})();
