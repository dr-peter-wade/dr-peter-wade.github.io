(() => {
  'use strict';
  document.documentElement.classList.add('js');
  const config = window.PETER_WADE_SITE || {};
  // Visitor-facing text comes from shared_data via the generated site-config.js.
  const messages = config.messages || {};
  const fillIn = (template, values) => String(template || '').replace(/\{(\w+)\}/g, (match, key) => (key in values ? values[key] : match));
  const email = typeof config.contactEmail === 'string' ? config.contactEmail.trim() : '';
  const emailReady = /^[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+$/.test(email) && !/[\r\n?#]/.test(email);
  const contactReady = config.launchApproved === true && emailReady;
  const sendReady = config.launchApproved === true && config.enquiryServiceEnabled === true &&
    typeof config.enquiryEndpoint === 'string' && config.enquiryEndpoint.startsWith('https://') &&
    typeof config.turnstileSiteKey === 'string' && Boolean(config.turnstileSiteKey);
  const ready = contactReady || sendReady;
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
    document.querySelectorAll('[data-offer-level]').forEach(link=>link.addEventListener('click',()=>{
      const target=tabs.find(tab=>tab.dataset.level===link.dataset.offerLevel);
      if(target)activate(target);
    }));
  }
  document.querySelectorAll('[data-select-level]').forEach(link=>link.addEventListener('click',()=>{const field=document.getElementById('enquiry-level');if(field)field.value=link.dataset.selectLevel;}));
  document.querySelectorAll('[data-print]').forEach(button=>button.addEventListener('click',()=>window.print()));
  document.querySelectorAll('[data-contact-email]').forEach(el=>{if(contactReady){el.textContent=email;el.href='mailto:'+email;}else{el.removeAttribute('href');}});
  document.querySelectorAll('[data-preview-only]').forEach(el=>{el.hidden=ready;});
  const status=document.getElementById('contact-status');
  const direct=document.getElementById('direct-email');
  if(ready){
    if(status)status.textContent=sendReady?messages.status_send:messages.status_draft;
    if(direct && contactReady){direct.textContent=email;direct.href='mailto:'+email;direct.hidden=false;}
  }

  const form=document.getElementById('enquiry-form');
  if(!form)return;
  const panel=document.getElementById('draft-panel');
  const draftText=document.getElementById('draft-text');
  const draftStatus=document.getElementById('draft-status');
  const emailLink=document.getElementById('open-email');
  let sendButton;
  let turnstileWidget;
  if(sendReady){
    const verification=document.createElement('div');
    verification.className='enquiry-verification';
    const challenge=document.createElement('div');
    verification.appendChild(challenge);
    sendButton=document.createElement('button');
    sendButton.type='button';
    sendButton.className='button primary';
    sendButton.textContent=messages.send;
    sendButton.hidden=true;
    verification.appendChild(sendButton);
    panel.appendChild(verification);
    const script=document.createElement('script');
    script.src='https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit';
    script.async=true;
    script.onload=()=>{turnstileWidget=window.turnstile.render(challenge,{sitekey:config.turnstileSiteKey,action:'enquiry'});};
    script.onerror=()=>{draftStatus.textContent=messages.verification_unavailable;};
    document.head.appendChild(script);
    sendButton.addEventListener('click',async()=>{
      const token=turnstileWidget===undefined?'':window.turnstile.getResponse(turnstileWidget);
      if(!token){draftStatus.textContent=messages.verification_required;return;}
      sendButton.disabled=true;
      draftStatus.textContent=messages.sending;
      try{
        const response=await fetch(config.enquiryEndpoint,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({site:'education',name:form.elements.namedItem('name').value,email:form.elements.namedItem('email').value,message:draftText.value,token,fax_organisation:''})});
        if(!response.ok)throw new Error('Delivery not confirmed');
        draftStatus.textContent=messages.sent;
      }catch(_error){
        draftStatus.textContent=messages.not_confirmed;
        sendButton.disabled=false;
        window.turnstile.reset(turnstileWidget);
      }
    });
  }
  // Keep disabled until our preventDefault handler is attached. With JavaScript disabled,
  // personal data cannot accidentally be submitted in the URL to a static host.
  form.addEventListener('submit',event=>{
    event.preventDefault();
    if(!form.reportValidity())return;
    const data=new FormData(form);
    const get=key=>String(data.get(key)||'').trim();
    const select=document.getElementById('enquiry-level');
    const label=select.options[select.selectedIndex].textContent;
    const values={name:get('name'),email:get('email'),level:label,topic:get('topic'),message:get('message')};
    const subject=fillIn(messages.subject,values).replace(/[\r\n]/g,' ');
    const text=(messages.draft_lines||[]).map(line=>fillIn(line,values)).join('\n');
    draftText.value=text;
    panel.hidden=false;
    if(contactReady){
      emailLink.href='mailto:'+email+'?subject='+encodeURIComponent(subject)+'&body='+encodeURIComponent(text);
      emailLink.hidden=false;
      draftStatus.textContent=fillIn(messages.ready_email,{email});
    }else if(sendReady){
      emailLink.removeAttribute('href');emailLink.hidden=true;
      draftStatus.textContent=messages.ready_send;
    }else{
      emailLink.removeAttribute('href');emailLink.hidden=true;
      draftStatus.textContent=messages.ready_preview;
    }
    if(sendButton){sendButton.hidden=false;sendButton.disabled=false;}
    panel.scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'nearest'});
  });
  document.getElementById('enquiry-fields').disabled=false;
  document.getElementById('copy-draft').addEventListener('click',async()=>{
    try{
      if(!navigator.clipboard || !window.isSecureContext)throw new Error('Clipboard unavailable');
      await navigator.clipboard.writeText(draftText.value);
      draftStatus.textContent=messages.copied;
    }catch(_error){
      draftText.focus();draftText.select();draftText.setSelectionRange(0,draftText.value.length);
      draftStatus.textContent=messages.selected;
    }
  });
})();
