"use strict";(self.webpackChunkhome_assistant_frontend=self.webpackChunkhome_assistant_frontend||[]).push([["7704"],{76538:function(e,a,t){t(23792),t(62953);var i=t(62826),o=t(96196),r=t(77845);let s,l,d,n,h,c,p=e=>e;class g extends o.WF{render(){const e=(0,o.qy)(s||(s=p`<div class="header-title"> <slot name="title"></slot> </div>`)),a=(0,o.qy)(l||(l=p`<div class="header-subtitle"> <slot name="subtitle"></slot> </div>`));return(0,o.qy)(d||(d=p` <header class="header"> <div class="header-bar"> <section class="header-navigation-icon"> <slot name="navigationIcon"></slot> </section> <section class="header-content"> ${0} </section> <section class="header-action-items"> <slot name="actionItems"></slot> </section> </div> <slot></slot> </header> `),"above"===this.subtitlePosition?(0,o.qy)(n||(n=p`${0}${0}`),a,e):(0,o.qy)(h||(h=p`${0}${0}`),e,a))}static get styles(){return[(0,o.AH)(c||(c=p`:host{display:block}:host([show-border]){border-bottom:1px solid var(--mdc-dialog-scroll-divider-color,rgba(0,0,0,.12))}.header-bar{display:flex;flex-direction:row;align-items:center;padding:0 var(--ha-space-1);box-sizing:border-box}.header-content{flex:1;padding:10px var(--ha-space-1);display:flex;flex-direction:column;justify-content:center;min-height:var(--ha-space-12);min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.header-title{height:var(--ha-dialog-header-title-height,calc(var(--ha-font-size-xl) + var(--ha-space-1)));font-size:var(--ha-font-size-xl);line-height:var(--ha-line-height-condensed);font-weight:var(--ha-font-weight-medium);color:var(--ha-dialog-header-title-color,var(--primary-text-color))}.header-subtitle{font-size:var(--ha-font-size-m);line-height:var(--ha-line-height-normal);color:var(--ha-dialog-header-subtitle-color,var(--secondary-text-color))}@media all and (min-width:450px) and (min-height:500px){.header-bar{padding:0 var(--ha-space-2)}}.header-navigation-icon{flex:none;min-width:var(--ha-space-2);height:100%;display:flex;flex-direction:row}.header-action-items{flex:none;min-width:var(--ha-space-2);height:100%;display:flex;flex-direction:row}`))]}constructor(...e){super(...e),this.subtitlePosition="below",this.showBorder=!1}}(0,i.__decorate)([(0,r.MZ)({type:String,attribute:"subtitle-position"})],g.prototype,"subtitlePosition",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean,reflect:!0,attribute:"show-border"})],g.prototype,"showBorder",void 0),g=(0,i.__decorate)([(0,r.EM)("ha-dialog-header")],g)},43661:function(e,a,t){t.r(a),t.d(a,{HaIconNext:function(){return l}});t(23792),t(62953);var i=t(62826),o=t(77845),r=t(19422),s=t(67094);class l extends s.HaSvgIcon{constructor(...e){super(...e),this.path="rtl"===r.G.document.dir?"M15.41,16.58L10.83,12L15.41,7.41L14,6L8,12L14,18L15.41,16.58Z":"M8.59,16.58L13.17,12L8.59,7.41L10,6L16,12L10,18L8.59,16.58Z"}}(0,i.__decorate)([(0,o.MZ)()],l.prototype,"path",void 0),l=(0,i.__decorate)([(0,o.EM)("ha-icon-next")],l)},45331:function(e,a,t){t.a(e,async function(e,a){try{t(23792),t(3362),t(62953);var i=t(62826),o=t(93900),r=t(96196),s=t(77845),l=t(32288),d=t(1087),n=t(14503),h=(t(76538),t(50888),e([o]));o=(h.then?(await h)():h)[0];let c,p,g,v,u,f,w=e=>e;const m="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z";class b extends r.WF{updated(e){super.updated(e),e.has("open")&&(this._open=this.open)}render(){var e,a;return(0,r.qy)(c||(c=w` <wa-dialog .open="${0}" .lightDismiss="${0}" without-header aria-labelledby="${0}" aria-describedby="${0}" @wa-show="${0}" @wa-after-show="${0}" @wa-after-hide="${0}"> <slot name="header"> <ha-dialog-header .subtitlePosition="${0}" .showBorder="${0}"> <slot name="headerNavigationIcon" slot="navigationIcon"> <ha-icon-button data-dialog="close" .label="${0}" .path="${0}"></ha-icon-button> </slot> ${0} ${0} <slot name="headerActionItems" slot="actionItems"></slot> </ha-dialog-header> </slot> <div class="body ha-scrollbar" @scroll="${0}"> <slot></slot> </div> <slot name="footer" slot="footer"></slot> </wa-dialog> `),this._open,!this.preventScrimClose,(0,l.J)(this.ariaLabelledBy||(void 0!==this.headerTitle?"ha-wa-dialog-title":void 0)),(0,l.J)(this.ariaDescribedBy),this._handleShow,this._handleAfterShow,this._handleAfterHide,this.headerSubtitlePosition,this._bodyScrolled,null!==(e=null===(a=this.hass)||void 0===a?void 0:a.localize("ui.common.close"))&&void 0!==e?e:"Close",m,void 0!==this.headerTitle?(0,r.qy)(p||(p=w`<span slot="title" class="title" id="ha-wa-dialog-title"> ${0} </span>`),this.headerTitle):(0,r.qy)(g||(g=w`<slot name="headerTitle" slot="title"></slot>`)),void 0!==this.headerSubtitle?(0,r.qy)(v||(v=w`<span slot="subtitle">${0}</span>`),this.headerSubtitle):(0,r.qy)(u||(u=w`<slot name="headerSubtitle" slot="subtitle"></slot>`)),this._handleBodyScroll)}disconnectedCallback(){super.disconnectedCallback(),this._open=!1}_handleBodyScroll(e){this._bodyScrolled=e.target.scrollTop>0}constructor(...e){super(...e),this.open=!1,this.type="standard",this.width="medium",this.preventScrimClose=!1,this.headerSubtitlePosition="below",this.flexContent=!1,this._open=!1,this._bodyScrolled=!1,this._handleShow=async()=>{this._open=!0,(0,d.r)(this,"opened"),await this.updateComplete,requestAnimationFrame(()=>{var e;null===(e=this.querySelector("[autofocus]"))||void 0===e||e.focus()})},this._handleAfterShow=()=>{(0,d.r)(this,"after-show")},this._handleAfterHide=()=>{this._open=!1,(0,d.r)(this,"closed")}}}b.styles=[n.dp,(0,r.AH)(f||(f=w`
      wa-dialog {
        --full-width: var(--ha-dialog-width-full, min(95vw, var(--safe-width)));
        --width: min(var(--ha-dialog-width-md, 580px), var(--full-width));
        --spacing: var(--dialog-content-padding, var(--ha-space-6));
        --show-duration: var(--ha-dialog-show-duration, 200ms);
        --hide-duration: var(--ha-dialog-hide-duration, 200ms);
        --ha-dialog-surface-background: var(
          --card-background-color,
          var(--ha-color-surface-default)
        );
        --wa-color-surface-raised: var(
          --ha-dialog-surface-background,
          var(--card-background-color, var(--ha-color-surface-default))
        );
        --wa-panel-border-radius: var(
          --ha-dialog-border-radius,
          var(--ha-border-radius-3xl)
        );
        max-width: var(--ha-dialog-max-width, var(--safe-width));
      }

      :host([width="small"]) wa-dialog {
        --width: min(var(--ha-dialog-width-sm, 320px), var(--full-width));
      }

      :host([width="large"]) wa-dialog {
        --width: min(var(--ha-dialog-width-lg, 1024px), var(--full-width));
      }

      :host([width="full"]) wa-dialog {
        --width: var(--full-width);
      }

      wa-dialog::part(dialog) {
        min-width: var(--width, var(--full-width));
        max-width: var(--width, var(--full-width));
        max-height: var(
          --ha-dialog-max-height,
          calc(var(--safe-height) - var(--ha-space-20))
        );
        min-height: var(--ha-dialog-min-height);
        margin-top: var(--dialog-surface-margin-top, auto);
        /* Used to offset the dialog from the safe areas when space is limited */
        transform: translate(
          calc(
            var(--safe-area-offset-left, var(--ha-space-0)) - var(
                --safe-area-offset-right,
                var(--ha-space-0)
              )
          ),
          calc(
            var(--safe-area-offset-top, var(--ha-space-0)) - var(
                --safe-area-offset-bottom,
                var(--ha-space-0)
              )
          )
        );
        display: flex;
        flex-direction: column;
        overflow: hidden;
      }

      @media all and (max-width: 450px), all and (max-height: 500px) {
        :host([type="standard"]) {
          --ha-dialog-border-radius: var(--ha-space-0);

          wa-dialog {
            /* Make the container fill the whole screen width and not the safe width */
            --full-width: var(--ha-dialog-width-full, 100vw);
            --width: var(--full-width);
          }

          wa-dialog::part(dialog) {
            /* Make the dialog fill the whole screen height and not the safe height */
            min-height: var(--ha-dialog-min-height, 100vh);
            min-height: var(--ha-dialog-min-height, 100dvh);
            max-height: var(--ha-dialog-max-height, 100vh);
            max-height: var(--ha-dialog-max-height, 100dvh);
            margin-top: 0;
            margin-bottom: 0;
            /* Use safe area as padding instead of the container size */
            padding-top: var(--safe-area-inset-top);
            padding-bottom: var(--safe-area-inset-bottom);
            padding-left: var(--safe-area-inset-left);
            padding-right: var(--safe-area-inset-right);
            /* Reset the transform to center the dialog */
            transform: none;
          }
        }
      }

      .header-title-container {
        display: flex;
        align-items: center;
      }

      .header-title {
        margin: 0;
        margin-bottom: 0;
        color: var(--ha-dialog-header-title-color, var(--primary-text-color));
        font-size: var(
          --ha-dialog-header-title-font-size,
          var(--ha-font-size-2xl)
        );
        line-height: var(
          --ha-dialog-header-title-line-height,
          var(--ha-line-height-condensed)
        );
        font-weight: var(
          --ha-dialog-header-title-font-weight,
          var(--ha-font-weight-normal)
        );
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        margin-right: var(--ha-space-3);
      }

      wa-dialog::part(body) {
        padding: 0;
        display: flex;
        flex-direction: column;
        max-width: 100%;
        overflow: hidden;
      }

      .body {
        position: var(--dialog-content-position, relative);
        padding: 0 var(--dialog-content-padding, var(--ha-space-6))
          var(--dialog-content-padding, var(--ha-space-6))
          var(--dialog-content-padding, var(--ha-space-6));
        overflow: auto;
        flex-grow: 1;
      }
      :host([flexcontent]) .body {
        max-width: 100%;
        flex: 1;
        display: flex;
        flex-direction: column;
      }

      wa-dialog::part(footer) {
        padding: var(--ha-space-0);
      }

      ::slotted([slot="footer"]) {
        display: flex;
        padding: var(--ha-space-3) var(--ha-space-4) var(--ha-space-4)
          var(--ha-space-4);
        gap: var(--ha-space-3);
        justify-content: flex-end;
        align-items: center;
        width: 100%;
      }
    `))],(0,i.__decorate)([(0,s.MZ)({attribute:!1})],b.prototype,"hass",void 0),(0,i.__decorate)([(0,s.MZ)({attribute:"aria-labelledby"})],b.prototype,"ariaLabelledBy",void 0),(0,i.__decorate)([(0,s.MZ)({attribute:"aria-describedby"})],b.prototype,"ariaDescribedBy",void 0),(0,i.__decorate)([(0,s.MZ)({type:Boolean,reflect:!0})],b.prototype,"open",void 0),(0,i.__decorate)([(0,s.MZ)({reflect:!0})],b.prototype,"type",void 0),(0,i.__decorate)([(0,s.MZ)({type:String,reflect:!0,attribute:"width"})],b.prototype,"width",void 0),(0,i.__decorate)([(0,s.MZ)({type:Boolean,reflect:!0,attribute:"prevent-scrim-close"})],b.prototype,"preventScrimClose",void 0),(0,i.__decorate)([(0,s.MZ)({attribute:"header-title"})],b.prototype,"headerTitle",void 0),(0,i.__decorate)([(0,s.MZ)({attribute:"header-subtitle"})],b.prototype,"headerSubtitle",void 0),(0,i.__decorate)([(0,s.MZ)({type:String,attribute:"header-subtitle-position"})],b.prototype,"headerSubtitlePosition",void 0),(0,i.__decorate)([(0,s.MZ)({type:Boolean,reflect:!0,attribute:"flexcontent"})],b.prototype,"flexContent",void 0),(0,i.__decorate)([(0,s.wk)()],b.prototype,"_open",void 0),(0,i.__decorate)([(0,s.P)(".body")],b.prototype,"bodyContainer",void 0),(0,i.__decorate)([(0,s.wk)()],b.prototype,"_bodyScrolled",void 0),(0,i.__decorate)([(0,s.Ls)({passive:!0})],b.prototype,"_handleBodyScroll",null),b=(0,i.__decorate)([(0,s.EM)("ha-wa-dialog")],b),a()}catch(c){a(c)}})},25563:function(e,a,t){t.a(e,async function(e,i){try{t.r(a);t(23792),t(62953);var o=t(62826),r=t(96196),s=t(77845),l=t(1087),d=(t(76538),t(50888),t(43661),t(17308),t(2846),t(67094),t(45331)),n=t(92288),h=e([d,n]);[d,n]=h.then?(await h)():h;let c,p=e=>e;class g extends r.WF{showDialog(e){this._params=e,this._opened=!0}closeDialog(){return this._opened=!1,!0}_dialogClosed(){(0,l.r)(this,"dialog-closed",{dialog:this.localName}),this._params=void 0}render(){return this._params?(0,r.qy)(c||(c=p` <ha-wa-dialog .hass="${0}" .open="${0}" header-title="${0}" header-subtitle="${0}" @closed="${0}"> <ha-target-picker-item-row .hass="${0}" .type="${0}" .itemId="${0}" .deviceFilter="${0}" .entityFilter="${0}" .includeDomains="${0}" .includeDeviceClasses="${0}" expand></ha-target-picker-item-row> </ha-wa-dialog> `),this.hass,this._opened,this.hass.localize("ui.components.target-picker.target_details"),`${this.hass.localize(`ui.components.target-picker.type.${this._params.type}`)}:\n            ${this._params.title}`,this._dialogClosed,this.hass,this._params.type,this._params.itemId,this._params.deviceFilter,this._params.entityFilter,this._params.includeDomains,this._params.includeDeviceClasses):r.s6}constructor(...e){super(...e),this._opened=!1}}(0,o.__decorate)([(0,s.MZ)({attribute:!1})],g.prototype,"hass",void 0),(0,o.__decorate)([(0,s.wk)()],g.prototype,"_params",void 0),(0,o.__decorate)([(0,s.wk)()],g.prototype,"_opened",void 0),g=(0,o.__decorate)([(0,s.EM)("ha-dialog-target-details")],g),i()}catch(c){i(c)}})},99793:function(e,a,t){var i=t(96196);let o;a.A=(0,i.AH)(o||(o=(e=>e)`:host{--width:31rem;--spacing:var(--wa-space-l);--show-duration:200ms;--hide-duration:200ms;display:none}:host([open]){display:block}.dialog{display:flex;flex-direction:column;top:0;right:0;bottom:0;left:0;width:var(--width);max-width:calc(100% - var(--wa-space-2xl));max-height:calc(100% - var(--wa-space-2xl));background-color:var(--wa-color-surface-raised);border-radius:var(--wa-panel-border-radius);border:none;box-shadow:var(--wa-shadow-l);padding:0;margin:auto}.dialog.show{animation:show-dialog var(--show-duration) ease}.dialog.show::backdrop{animation:show-backdrop var(--show-duration,200ms) ease}.dialog.hide{animation:show-dialog var(--hide-duration) ease reverse}.dialog.hide::backdrop{animation:show-backdrop var(--hide-duration,200ms) ease reverse}.dialog.pulse{animation:pulse 250ms ease}.dialog:focus{outline:0}@media screen and (max-width:420px){.dialog{max-height:80vh}}.open{display:flex;opacity:1}.header{flex:0 0 auto;display:flex;flex-wrap:nowrap;padding-inline-start:var(--spacing);padding-block-end:0;padding-inline-end:calc(var(--spacing) - var(--wa-form-control-padding-block));padding-block-start:calc(var(--spacing) - var(--wa-form-control-padding-block))}.title{align-self:center;flex:1 1 auto;font-family:inherit;font-size:var(--wa-font-size-l);font-weight:var(--wa-font-weight-heading);line-height:var(--wa-line-height-condensed);margin:0}.header-actions{align-self:start;display:flex;flex-shrink:0;flex-wrap:wrap;justify-content:end;gap:var(--wa-space-2xs);padding-inline-start:var(--spacing)}.header-actions ::slotted(wa-button),.header-actions wa-button{flex:0 0 auto;display:flex;align-items:center}.body{flex:1 1 auto;display:block;padding:var(--spacing);overflow:auto;-webkit-overflow-scrolling:touch}.body:focus{outline:0}.body:focus-visible{outline:var(--wa-focus-ring);outline-offset:var(--wa-focus-ring-offset)}.footer{flex:0 0 auto;display:flex;flex-wrap:wrap;gap:var(--wa-space-xs);justify-content:end;padding:var(--spacing);padding-block-start:0}.footer ::slotted(wa-button:not(:first-of-type)){margin-inline-start:var(--wa-spacing-xs)}.dialog::backdrop{background-color:var(--wa-color-overlay-modal,rgb(0 0 0 / .25))}@keyframes pulse{0%{scale:1}50%{scale:1.02}100%{scale:1}}@keyframes show-dialog{from{opacity:0;scale:0.8}to{opacity:1;scale:1}}@keyframes show-backdrop{from{opacity:0}to{opacity:1}}@media (forced-colors:active){.dialog{border:solid 1px #fff}}`))},93900:function(e,a,t){t.a(e,async function(e,a){try{t(23792),t(3362),t(27495),t(62953);var i=t(96196),o=t(77845),r=t(94333),s=t(32288),l=t(17051),d=t(42462),n=t(28438),h=t(98779),c=t(27259),p=t(31247),g=t(93949),v=t(92070),u=t(9395),f=t(32510),w=t(17060),m=t(88496),b=t(99793),y=e([m,w]);[m,w]=y.then?(await y)():y;let $,L,C,M=e=>e;var x=Object.defineProperty,_=Object.getOwnPropertyDescriptor,k=(e,a,t,i)=>{for(var o,r=i>1?void 0:i?_(a,t):a,s=e.length-1;s>=0;s--)(o=e[s])&&(r=(i?o(a,t,r):o(r))||r);return i&&r&&x(a,t,r),r};let D=class extends f.A{firstUpdated(){this.open&&(this.addOpenListeners(),this.dialog.showModal(),(0,g.JG)(this))}disconnectedCallback(){super.disconnectedCallback(),(0,g.I7)(this),this.removeOpenListeners()}async requestClose(e){const a=new n.L({source:e});if(this.dispatchEvent(a),a.defaultPrevented)return this.open=!0,void(0,c.Ud)(this.dialog,"pulse");this.removeOpenListeners(),await(0,c.Ud)(this.dialog,"hide"),this.open=!1,this.dialog.close(),(0,g.I7)(this);const t=this.originalTrigger;"function"==typeof(null==t?void 0:t.focus)&&setTimeout(()=>t.focus()),this.dispatchEvent(new l.Z)}addOpenListeners(){document.addEventListener("keydown",this.handleDocumentKeyDown)}removeOpenListeners(){document.removeEventListener("keydown",this.handleDocumentKeyDown)}handleDialogCancel(e){e.preventDefault(),this.dialog.classList.contains("hide")||e.target!==this.dialog||this.requestClose(this.dialog)}handleDialogClick(e){const a=e.target.closest('[data-dialog="close"]');a&&(e.stopPropagation(),this.requestClose(a))}async handleDialogPointerDown(e){e.target===this.dialog&&(this.lightDismiss?this.requestClose(this.dialog):await(0,c.Ud)(this.dialog,"pulse"))}handleOpenChange(){this.open&&!this.dialog.open?this.show():!this.open&&this.dialog.open&&(this.open=!0,this.requestClose(this.dialog))}async show(){const e=new h.k;this.dispatchEvent(e),e.defaultPrevented?this.open=!1:(this.addOpenListeners(),this.originalTrigger=document.activeElement,this.open=!0,this.dialog.showModal(),(0,g.JG)(this),requestAnimationFrame(()=>{const e=this.querySelector("[autofocus]");e&&"function"==typeof e.focus?e.focus():this.dialog.focus()}),await(0,c.Ud)(this.dialog,"show"),this.dispatchEvent(new d.q))}render(){var e;const a=!this.withoutHeader,t=this.hasSlotController.test("footer");return(0,i.qy)($||($=M` <dialog aria-labelledby="${0}" aria-describedby="${0}" part="dialog" class="${0}" @cancel="${0}" @click="${0}" @pointerdown="${0}"> ${0} <div part="body" class="body"><slot></slot></div> ${0} </dialog> `),null!==(e=this.ariaLabelledby)&&void 0!==e?e:"title",(0,s.J)(this.ariaDescribedby),(0,r.H)({dialog:!0,open:this.open}),this.handleDialogCancel,this.handleDialogClick,this.handleDialogPointerDown,a?(0,i.qy)(L||(L=M` <header part="header" class="header"> <h2 part="title" class="title" id="title"> <slot name="label"> ${0} </slot> </h2> <div part="header-actions" class="header-actions"> <slot name="header-actions"></slot> <wa-button part="close-button" exportparts="base:close-button__base" class="close" appearance="plain" @click="${0}"> <wa-icon name="xmark" label="${0}" library="system" variant="solid"></wa-icon> </wa-button> </div> </header> `),this.label.length>0?this.label:String.fromCharCode(8203),e=>this.requestClose(e.target),this.localize.term("close")):"",t?(0,i.qy)(C||(C=M` <footer part="footer" class="footer"> <slot name="footer"></slot> </footer> `)):"")}constructor(){super(...arguments),this.localize=new w.c(this),this.hasSlotController=new v.X(this,"footer","header-actions","label"),this.open=!1,this.label="",this.withoutHeader=!1,this.lightDismiss=!1,this.handleDocumentKeyDown=e=>{"Escape"===e.key&&this.open&&(e.preventDefault(),e.stopPropagation(),this.requestClose(this.dialog))}}};D.css=b.A,k([(0,o.P)(".dialog")],D.prototype,"dialog",2),k([(0,o.MZ)({type:Boolean,reflect:!0})],D.prototype,"open",2),k([(0,o.MZ)({reflect:!0})],D.prototype,"label",2),k([(0,o.MZ)({attribute:"without-header",type:Boolean,reflect:!0})],D.prototype,"withoutHeader",2),k([(0,o.MZ)({attribute:"light-dismiss",type:Boolean})],D.prototype,"lightDismiss",2),k([(0,o.MZ)({attribute:"aria-labelledby"})],D.prototype,"ariaLabelledby",2),k([(0,o.MZ)({attribute:"aria-describedby"})],D.prototype,"ariaDescribedby",2),k([(0,u.w)("open",{waitUntilFirstUpdate:!0})],D.prototype,"handleOpenChange",1),D=k([(0,o.EM)("wa-dialog")],D),document.addEventListener("click",e=>{const a=e.target.closest("[data-dialog]");if(a instanceof Element){const[e,t]=(0,p.v)(a.getAttribute("data-dialog")||"");if("open"===e&&null!=t&&t.length){const e=a.getRootNode().getElementById(t);"wa-dialog"===(null==e?void 0:e.localName)?e.open=!0:console.warn(`A dialog with an ID of "${t}" could not be found in this document.`)}}}),i.S$||document.addEventListener("pointerdown",()=>{}),a()}catch($){a($)}})}}]);
//# sourceMappingURL=7704.bbbec2e70d8eb399.js.map