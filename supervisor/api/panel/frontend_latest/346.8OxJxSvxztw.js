/*! For license information please see 346.8OxJxSvxztw.js.LICENSE.txt */
export const id=346;export const ids=[346];export const modules={70346:(e,t,i)=>{i.d(t,{m:()=>g});var o=i(79192),n=i(29818),s=(i(89655),i(408),i(50289)),a=i(85323),r=i(26604),d=i(29431),l=i(60207);const c=(0,r.n)(s.WF);class h extends c{get open(){return this.isOpen}set open(e){e!==this.isOpen&&(this.isOpen=e,e?(this.setAttribute("open",""),this.show()):(this.removeAttribute("open"),this.close()))}constructor(){super(),this.quick=!1,this.returnValue="",this.noFocusTrap=!1,this.getOpenAnimation=()=>l.T,this.getCloseAnimation=()=>l.N,this.isOpen=!1,this.isOpening=!1,this.isConnectedPromise=this.getIsConnectedPromise(),this.isAtScrollTop=!1,this.isAtScrollBottom=!1,this.nextClickIsFromContent=!1,this.hasHeadline=!1,this.hasActions=!1,this.hasIcon=!1,this.escapePressedWithoutCancel=!1,this.treewalker=s.S$?null:document.createTreeWalker(this,NodeFilter.SHOW_ELEMENT),s.S$||this.addEventListener("submit",this.handleSubmit)}async show(){this.isOpening=!0,await this.isConnectedPromise,await this.updateComplete;const e=this.dialog;if(e.open||!this.isOpening)return void(this.isOpening=!1);if(!this.dispatchEvent(new Event("open",{cancelable:!0})))return this.open=!1,void(this.isOpening=!1);e.showModal(),this.open=!0,this.scroller&&(this.scroller.scrollTop=0),this.querySelector("[autofocus]")?.focus(),await this.animateDialog(this.getOpenAnimation()),this.dispatchEvent(new Event("opened")),this.isOpening=!1}async close(e=this.returnValue){if(this.isOpening=!1,!this.isConnected)return void(this.open=!1);await this.updateComplete;const t=this.dialog;if(!t.open||this.isOpening)return void(this.open=!1);const i=this.returnValue;this.returnValue=e;this.dispatchEvent(new Event("close",{cancelable:!0}))?(await this.animateDialog(this.getCloseAnimation()),t.close(e),this.open=!1,this.dispatchEvent(new Event("closed"))):this.returnValue=i}connectedCallback(){super.connectedCallback(),this.isConnectedPromiseResolve()}disconnectedCallback(){super.disconnectedCallback(),this.isConnectedPromise=this.getIsConnectedPromise()}render(){const e=this.open&&!(this.isAtScrollTop&&this.isAtScrollBottom),t={"has-headline":this.hasHeadline,"has-actions":this.hasActions,"has-icon":this.hasIcon,scrollable:e,"show-top-divider":e&&!this.isAtScrollTop,"show-bottom-divider":e&&!this.isAtScrollBottom},i=this.open&&!this.noFocusTrap,o=s.qy` <div class="focus-trap" tabindex="0" aria-hidden="true" @focus="${this.handleFocusTrapFocus}"></div> `,{ariaLabel:n}=this;return s.qy` <div class="scrim"></div> <dialog class="${(0,a.H)(t)}" aria-label="${n||s.s6}" aria-labelledby="${this.hasHeadline?"headline":s.s6}" role="${"alert"===this.type?"alertdialog":s.s6}" @cancel="${this.handleCancel}" @click="${this.handleDialogClick}" @close="${this.handleClose}" @keydown="${this.handleKeydown}" .returnValue="${this.returnValue||s.s6}"> ${i?o:s.s6} <div class="container" @click="${this.handleContentClick}"> <div class="headline"> <div class="icon" aria-hidden="true"> <slot name="icon" @slotchange="${this.handleIconChange}"></slot> </div> <h2 id="headline" aria-hidden="${!this.hasHeadline||s.s6}"> <slot name="headline" @slotchange="${this.handleHeadlineChange}"></slot> </h2> <md-divider></md-divider> </div> <div class="scroller"> <div class="content"> <div class="top anchor"></div> <slot name="content"></slot> <div class="bottom anchor"></div> </div> </div> <div class="actions"> <md-divider></md-divider> <slot name="actions" @slotchange="${this.handleActionsChange}"></slot> </div> </div> ${i?o:s.s6} </dialog> `}firstUpdated(){this.intersectionObserver=new IntersectionObserver((e=>{for(const t of e)this.handleAnchorIntersection(t)}),{root:this.scroller}),this.intersectionObserver.observe(this.topAnchor),this.intersectionObserver.observe(this.bottomAnchor)}handleDialogClick(){if(this.nextClickIsFromContent)return void(this.nextClickIsFromContent=!1);!this.dispatchEvent(new Event("cancel",{cancelable:!0}))||this.close()}handleContentClick(){this.nextClickIsFromContent=!0}handleSubmit(e){const t=e.target,{submitter:i}=e;"dialog"===t.method&&i&&this.close(i.getAttribute("value")??this.returnValue)}handleCancel(e){if(e.target!==this.dialog)return;this.escapePressedWithoutCancel=!1;const t=!(0,d.M)(this,e);e.preventDefault(),t||this.close()}handleClose(){this.escapePressedWithoutCancel&&(this.escapePressedWithoutCancel=!1,this.dialog?.dispatchEvent(new Event("cancel",{cancelable:!0})))}handleKeydown(e){"Escape"===e.key&&(this.escapePressedWithoutCancel=!0,setTimeout((()=>{this.escapePressedWithoutCancel=!1})))}async animateDialog(e){if(this.cancelAnimations?.abort(),this.cancelAnimations=new AbortController,this.quick)return;const{dialog:t,scrim:i,container:o,headline:n,content:s,actions:a}=this;if(!(t&&i&&o&&n&&s&&a))return;const{container:r,dialog:d,scrim:l,headline:c,content:h,actions:p}=e,m=[[t,d??[]],[i,l??[]],[o,r??[]],[n,c??[]],[s,h??[]],[a,p??[]]],g=[];for(const[e,t]of m)for(const i of t){const t=e.animate(...i);this.cancelAnimations.signal.addEventListener("abort",(()=>{t.cancel()})),g.push(t)}await Promise.all(g.map((e=>e.finished.catch((()=>{})))))}handleHeadlineChange(e){const t=e.target;this.hasHeadline=t.assignedElements().length>0}handleActionsChange(e){const t=e.target;this.hasActions=t.assignedElements().length>0}handleIconChange(e){const t=e.target;this.hasIcon=t.assignedElements().length>0}handleAnchorIntersection(e){const{target:t,isIntersecting:i}=e;t===this.topAnchor&&(this.isAtScrollTop=i),t===this.bottomAnchor&&(this.isAtScrollBottom=i)}getIsConnectedPromise(){return new Promise((e=>{this.isConnectedPromiseResolve=e}))}handleFocusTrapFocus(e){const[t,i]=this.getFirstAndLastFocusableChildren();if(!t||!i)return void this.dialog?.focus();const o=e.target===this.firstFocusTrap,n=!o,s=e.relatedTarget===t,a=e.relatedTarget===i,r=!s&&!a;if(n&&a||o&&r)return void t.focus();(o&&s||n&&r)&&i.focus()}getFirstAndLastFocusableChildren(){if(!this.treewalker)return[null,null];let e=null,t=null;for(this.treewalker.currentNode=this.treewalker.root;this.treewalker.nextNode();){const i=this.treewalker.currentNode;p(i)&&(e||(e=i),t=i)}return[e,t]}}function p(e){const t=":not(:disabled,[disabled])";if(e.matches(":is(button,input,select,textarea,object,:is(a,area)[href],[tabindex],[contenteditable=true])"+t+':not([tabindex^="-"])'))return!0;return!!e.localName.includes("-")&&(!!e.matches(t)&&(e.shadowRoot?.delegatesFocus??!1))}(0,o.__decorate)([(0,n.MZ)({type:Boolean})],h.prototype,"open",null),(0,o.__decorate)([(0,n.MZ)({type:Boolean})],h.prototype,"quick",void 0),(0,o.__decorate)([(0,n.MZ)({attribute:!1})],h.prototype,"returnValue",void 0),(0,o.__decorate)([(0,n.MZ)()],h.prototype,"type",void 0),(0,o.__decorate)([(0,n.MZ)({type:Boolean,attribute:"no-focus-trap"})],h.prototype,"noFocusTrap",void 0),(0,o.__decorate)([(0,n.P)("dialog")],h.prototype,"dialog",void 0),(0,o.__decorate)([(0,n.P)(".scrim")],h.prototype,"scrim",void 0),(0,o.__decorate)([(0,n.P)(".container")],h.prototype,"container",void 0),(0,o.__decorate)([(0,n.P)(".headline")],h.prototype,"headline",void 0),(0,o.__decorate)([(0,n.P)(".content")],h.prototype,"content",void 0),(0,o.__decorate)([(0,n.P)(".actions")],h.prototype,"actions",void 0),(0,o.__decorate)([(0,n.wk)()],h.prototype,"isAtScrollTop",void 0),(0,o.__decorate)([(0,n.wk)()],h.prototype,"isAtScrollBottom",void 0),(0,o.__decorate)([(0,n.P)(".scroller")],h.prototype,"scroller",void 0),(0,o.__decorate)([(0,n.P)(".top.anchor")],h.prototype,"topAnchor",void 0),(0,o.__decorate)([(0,n.P)(".bottom.anchor")],h.prototype,"bottomAnchor",void 0),(0,o.__decorate)([(0,n.P)(".focus-trap")],h.prototype,"firstFocusTrap",void 0),(0,o.__decorate)([(0,n.wk)()],h.prototype,"hasHeadline",void 0),(0,o.__decorate)([(0,n.wk)()],h.prototype,"hasActions",void 0),(0,o.__decorate)([(0,n.wk)()],h.prototype,"hasIcon",void 0);const m=s.AH`:host{border-start-start-radius:var(--md-dialog-container-shape-start-start,var(--md-dialog-container-shape,var(--md-sys-shape-corner-extra-large,28px)));border-start-end-radius:var(--md-dialog-container-shape-start-end,var(--md-dialog-container-shape,var(--md-sys-shape-corner-extra-large,28px)));border-end-end-radius:var(--md-dialog-container-shape-end-end,var(--md-dialog-container-shape,var(--md-sys-shape-corner-extra-large,28px)));border-end-start-radius:var(--md-dialog-container-shape-end-start,var(--md-dialog-container-shape,var(--md-sys-shape-corner-extra-large,28px)));display:contents;margin:auto;max-height:min(560px,100% - 48px);max-width:min(560px,100% - 48px);min-height:140px;min-width:280px;position:fixed;height:fit-content;width:fit-content}dialog{background:rgba(0,0,0,0);border:none;border-radius:inherit;flex-direction:column;height:inherit;margin:inherit;max-height:inherit;max-width:inherit;min-height:inherit;min-width:inherit;outline:0;overflow:visible;padding:0;width:inherit}dialog[open]{display:flex}::backdrop{background:0 0}.scrim{background:var(--md-sys-color-scrim,#000);display:none;inset:0;opacity:32%;pointer-events:none;position:fixed;z-index:1}:host([open]) .scrim{display:flex}h2{all:unset;align-self:stretch}.headline{align-items:center;color:var(--md-dialog-headline-color,var(--md-sys-color-on-surface,#1d1b20));display:flex;flex-direction:column;font-family:var(--md-dialog-headline-font, var(--md-sys-typescale-headline-small-font, var(--md-ref-typeface-brand, Roboto)));font-size:var(--md-dialog-headline-size, var(--md-sys-typescale-headline-small-size, 1.5rem));line-height:var(--md-dialog-headline-line-height, var(--md-sys-typescale-headline-small-line-height, 2rem));font-weight:var(--md-dialog-headline-weight,var(--md-sys-typescale-headline-small-weight,var(--md-ref-typeface-weight-regular,400)));position:relative}slot[name=headline]::slotted(*){align-items:center;align-self:stretch;box-sizing:border-box;display:flex;gap:8px;padding:24px 24px 0}.icon{display:flex}slot[name=icon]::slotted(*){color:var(--md-dialog-icon-color,var(--md-sys-color-secondary,#625b71));fill:currentColor;font-size:var(--md-dialog-icon-size, 24px);margin-top:24px;height:var(--md-dialog-icon-size,24px);width:var(--md-dialog-icon-size,24px)}.has-icon slot[name=headline]::slotted(*){justify-content:center;padding-top:16px}.scrollable slot[name=headline]::slotted(*){padding-bottom:16px}.scrollable.has-headline slot[name=content]::slotted(*){padding-top:8px}.container{border-radius:inherit;display:flex;flex-direction:column;flex-grow:1;overflow:hidden;position:relative;transform-origin:top}.container::before{background:var(--md-dialog-container-color,var(--md-sys-color-surface-container-high,#ece6f0));border-radius:inherit;content:"";inset:0;position:absolute}.scroller{display:flex;flex:1;flex-direction:column;overflow:hidden;z-index:1}.scrollable .scroller{overflow-y:scroll}.content{color:var(--md-dialog-supporting-text-color,var(--md-sys-color-on-surface-variant,#49454f));font-family:var(--md-dialog-supporting-text-font, var(--md-sys-typescale-body-medium-font, var(--md-ref-typeface-plain, Roboto)));font-size:var(--md-dialog-supporting-text-size, var(--md-sys-typescale-body-medium-size, .875rem));line-height:var(--md-dialog-supporting-text-line-height, var(--md-sys-typescale-body-medium-line-height, 1.25rem));flex:1;font-weight:var(--md-dialog-supporting-text-weight,var(--md-sys-typescale-body-medium-weight,var(--md-ref-typeface-weight-regular,400)));height:min-content;position:relative}slot[name=content]::slotted(*){box-sizing:border-box;padding:24px}.anchor{position:absolute}.top.anchor{top:0}.bottom.anchor{bottom:0}.actions{position:relative}slot[name=actions]::slotted(*){box-sizing:border-box;display:flex;gap:8px;justify-content:flex-end;padding:16px 24px 24px}.has-actions slot[name=content]::slotted(*){padding-bottom:8px}md-divider{display:none;position:absolute}.has-actions.show-bottom-divider .actions md-divider,.has-headline.show-top-divider .headline md-divider{display:flex}.headline md-divider{bottom:0}.actions md-divider{top:0}@media(forced-colors:active){dialog{outline:2px solid WindowText}}`;let g=class extends h{};g.styles=[m],g=(0,o.__decorate)([(0,n.EM)("md-dialog")],g)},60207:(e,t,i)=>{i.d(t,{N:()=>s,T:()=>n});var o=i(43044);const n={dialog:[[[{transform:"translateY(-50px)"},{transform:"translateY(0)"}],{duration:500,easing:o.Ux.EMPHASIZED}]],scrim:[[[{opacity:0},{opacity:.32}],{duration:500,easing:"linear"}]],container:[[[{opacity:0},{opacity:1}],{duration:50,easing:"linear",pseudoElement:"::before"}],[[{height:"35%"},{height:"100%"}],{duration:500,easing:o.Ux.EMPHASIZED,pseudoElement:"::before"}]],headline:[[[{opacity:0},{opacity:0,offset:.2},{opacity:1}],{duration:250,easing:"linear",fill:"forwards"}]],content:[[[{opacity:0},{opacity:0,offset:.2},{opacity:1}],{duration:250,easing:"linear",fill:"forwards"}]],actions:[[[{opacity:0},{opacity:0,offset:.5},{opacity:1}],{duration:300,easing:"linear",fill:"forwards"}]]},s={dialog:[[[{transform:"translateY(0)"},{transform:"translateY(-50px)"}],{duration:150,easing:o.Ux.EMPHASIZED_ACCELERATE}]],scrim:[[[{opacity:.32},{opacity:0}],{duration:150,easing:"linear"}]],container:[[[{height:"100%"},{height:"35%"}],{duration:150,easing:o.Ux.EMPHASIZED_ACCELERATE,pseudoElement:"::before"}],[[{opacity:"1"},{opacity:"0"}],{delay:100,duration:50,easing:"linear",pseudoElement:"::before"}]],headline:[[[{opacity:1},{opacity:0}],{duration:100,easing:"linear",fill:"forwards"}]],content:[[[{opacity:1},{opacity:0}],{duration:100,easing:"linear",fill:"forwards"}]],actions:[[[{opacity:1},{opacity:0}],{duration:100,easing:"linear",fill:"forwards"}]]}},408:(e,t,i)=>{i.d(t,{h:()=>d});var o=i(79192),n=i(29818),s=i(50289);class a extends s.WF{constructor(){super(...arguments),this.inset=!1,this.insetStart=!1,this.insetEnd=!1}}(0,o.__decorate)([(0,n.MZ)({type:Boolean,reflect:!0})],a.prototype,"inset",void 0),(0,o.__decorate)([(0,n.MZ)({type:Boolean,reflect:!0,attribute:"inset-start"})],a.prototype,"insetStart",void 0),(0,o.__decorate)([(0,n.MZ)({type:Boolean,reflect:!0,attribute:"inset-end"})],a.prototype,"insetEnd",void 0);const r=s.AH`:host{box-sizing:border-box;color:var(--md-divider-color,var(--md-sys-color-outline-variant,#cac4d0));display:flex;height:var(--md-divider-thickness,1px);width:100%}:host([inset-start]),:host([inset]){padding-inline-start:16px}:host([inset-end]),:host([inset]){padding-inline-end:16px}:host::before{background:currentColor;content:"";height:100%;width:100%}@media(forced-colors:active){:host::before{background:CanvasText}}`;let d=class extends a{};d.styles=[r],d=(0,o.__decorate)([(0,n.EM)("md-divider")],d)},29431:(e,t,i)=>{function o(e,t){!t.bubbles||e.shadowRoot&&!t.composed||t.stopPropagation();const i=Reflect.construct(t.constructor,[t.type,t]),o=e.dispatchEvent(i);return o||t.preventDefault(),o}i.d(t,{M:()=>o})}};
//# sourceMappingURL=346.8OxJxSvxztw.js.map