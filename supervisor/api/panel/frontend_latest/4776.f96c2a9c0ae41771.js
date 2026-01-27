/*! For license information please see 4776.f96c2a9c0ae41771.js.LICENSE.txt */
export const __rspack_esm_id="4776";export const __rspack_esm_ids=["4776"];export const __webpack_modules__={18350(t,e,a){a.a(t,async function(t,e){try{var o=a(62826),i=a(88496),r=a(96196),l=a(77845),s=t([i]);i=(s.then?(await s)():s)[0];class n extends i.A{static get styles(){return[i.A.styles,r.AH`:host{--wa-form-control-padding-inline:16px;--wa-font-weight-action:var(--ha-font-weight-medium);--wa-form-control-border-radius:var(
            --ha-button-border-radius,
            var(--ha-border-radius-pill)
          );--wa-form-control-height:var(
            --ha-button-height,
            var(--button-height, 40px)
          )}.button{font-size:var(--ha-font-size-m);line-height:1;transition:background-color .15s ease-in-out;text-wrap:wrap}:host([size=small]) .button{--wa-form-control-height:var(
            --ha-button-height,
            var(--button-height, 32px)
          );font-size:var(--wa-font-size-s, var(--ha-font-size-m));--wa-form-control-padding-inline:12px}:host([variant=brand]){--button-color-fill-normal-active:var(--ha-color-fill-primary-normal-active);--button-color-fill-normal-hover:var(--ha-color-fill-primary-normal-hover);--button-color-fill-loud-active:var(--ha-color-fill-primary-loud-active);--button-color-fill-loud-hover:var(--ha-color-fill-primary-loud-hover)}:host([variant=neutral]){--button-color-fill-normal-active:var(--ha-color-fill-neutral-normal-active);--button-color-fill-normal-hover:var(--ha-color-fill-neutral-normal-hover);--button-color-fill-loud-active:var(--ha-color-fill-neutral-loud-active);--button-color-fill-loud-hover:var(--ha-color-fill-neutral-loud-hover)}:host([variant=success]){--button-color-fill-normal-active:var(--ha-color-fill-success-normal-active);--button-color-fill-normal-hover:var(--ha-color-fill-success-normal-hover);--button-color-fill-loud-active:var(--ha-color-fill-success-loud-active);--button-color-fill-loud-hover:var(--ha-color-fill-success-loud-hover)}:host([variant=warning]){--button-color-fill-normal-active:var(--ha-color-fill-warning-normal-active);--button-color-fill-normal-hover:var(--ha-color-fill-warning-normal-hover);--button-color-fill-loud-active:var(--ha-color-fill-warning-loud-active);--button-color-fill-loud-hover:var(--ha-color-fill-warning-loud-hover)}:host([variant=danger]){--button-color-fill-normal-active:var(--ha-color-fill-danger-normal-active);--button-color-fill-normal-hover:var(--ha-color-fill-danger-normal-hover);--button-color-fill-loud-active:var(--ha-color-fill-danger-loud-active);--button-color-fill-loud-hover:var(--ha-color-fill-danger-loud-hover)}:host([appearance~=plain]) .button{color:var(--wa-color-on-normal);background-color:transparent}:host([appearance~=plain]) .button.disabled{background-color:transparent;color:var(--ha-color-on-disabled-quiet)}:host([appearance~=outlined]) .button.disabled{background-color:transparent;color:var(--ha-color-on-disabled-quiet)}@media (hover:hover){:host([appearance~=filled]) .button:not(.disabled):not(.loading):hover{background-color:var(--button-color-fill-normal-hover)}:host([appearance~=accent]) .button:not(.disabled):not(.loading):hover{background-color:var(--button-color-fill-loud-hover)}:host([appearance~=plain]) .button:not(.disabled):not(.loading):hover{color:var(--wa-color-on-normal)}}:host([appearance~=filled]) .button{color:var(--wa-color-on-normal);background-color:var(--wa-color-fill-normal);border-color:transparent}:host([appearance~=filled]) .button:not(.disabled):not(.loading):active{background-color:var(--button-color-fill-normal-active)}:host([appearance~=filled]) .button.disabled{background-color:var(--ha-color-fill-disabled-normal-resting);color:var(--ha-color-on-disabled-normal)}:host([appearance~=accent]) .button{background-color:var(--wa-color-fill-loud,var(--wa-color-neutral-fill-loud))}:host([appearance~=accent]) .button:not(.disabled):not(.loading):active{background-color:var(--button-color-fill-loud-active)}:host([appearance~=accent]) .button.disabled{background-color:var(--ha-color-fill-disabled-loud-resting);color:var(--ha-color-on-disabled-loud)}:host([loading]){pointer-events:none}.button.disabled{opacity:1}slot[name=start]::slotted(*){margin-inline-end:4px}slot[name=end]::slotted(*){margin-inline-start:4px}.button.has-start{padding-inline-start:8px}.button.has-end{padding-inline-end:8px}.label{overflow:hidden;text-overflow:ellipsis;padding:var(--ha-space-1) 0}`]}constructor(...t){super(...t),this.variant="brand"}}n=(0,o.Cg)([(0,l.EM)("ha-button")],n),e()}catch(t){e(t)}})},93444(t,e,a){var o=a(62826),i=a(96196),r=a(77845);class l extends i.WF{render(){return i.qy` <footer> <slot name="secondaryAction"></slot> <slot name="primaryAction"></slot> </footer> `}static get styles(){return[i.AH`footer{display:flex;gap:var(--ha-space-3);justify-content:flex-end;align-items:center;width:100%}`]}}l=(0,o.Cg)([(0,r.EM)("ha-dialog-footer")],l)},76538(t,e,a){var o=a(62826),i=a(96196),r=a(77845);class l extends i.WF{render(){const t=i.qy`<div class="header-title"> <slot name="title"></slot> </div>`,e=i.qy`<div class="header-subtitle"> <slot name="subtitle"></slot> </div>`;return i.qy` <header class="header"> <div class="header-bar"> <section class="header-navigation-icon"> <slot name="navigationIcon"></slot> </section> <section class="header-content"> ${"above"===this.subtitlePosition?i.qy`${e}${t}`:i.qy`${t}${e}`} </section> <section class="header-action-items"> <slot name="actionItems"></slot> </section> </div> <slot></slot> </header> `}static get styles(){return[i.AH`:host{display:block}:host([show-border]){border-bottom:1px solid var(--mdc-dialog-scroll-divider-color,rgba(0,0,0,.12))}.header-bar{display:flex;flex-direction:row;align-items:center;padding:0 var(--ha-space-1);box-sizing:border-box}.header-content{flex:1;padding:10px var(--ha-space-1);display:flex;flex-direction:column;justify-content:center;min-height:var(--ha-space-12);min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.header-title{height:var(--ha-dialog-header-title-height,calc(var(--ha-font-size-xl) + var(--ha-space-1)));font-size:var(--ha-font-size-xl);line-height:var(--ha-line-height-condensed);font-weight:var(--ha-font-weight-medium);color:var(--ha-dialog-header-title-color,var(--primary-text-color))}.header-subtitle{font-size:var(--ha-font-size-m);line-height:var(--ha-line-height-normal);color:var(--ha-dialog-header-subtitle-color,var(--secondary-text-color))}@media all and (min-width:450px) and (min-height:500px){.header-bar{padding:0 var(--ha-space-2)}}.header-navigation-icon{flex:none;min-width:var(--ha-space-2);height:100%;display:flex;flex-direction:row}.header-action-items{flex:none;min-width:var(--ha-space-2);height:100%;display:flex;flex-direction:row}`]}constructor(...t){super(...t),this.subtitlePosition="below",this.showBorder=!1}}(0,o.Cg)([(0,r.MZ)({type:String,attribute:"subtitle-position"})],l.prototype,"subtitlePosition",void 0),(0,o.Cg)([(0,r.MZ)({type:Boolean,reflect:!0,attribute:"show-border"})],l.prototype,"showBorder",void 0),l=(0,o.Cg)([(0,r.EM)("ha-dialog-header")],l)},45331(t,e,a){a.a(t,async function(t,e){try{var o=a(62826),i=a(93900),r=a(96196),l=a(77845),s=a(32288),n=a(1087),d=a(59992),h=a(14503),c=(a(76538),a(50888),t([i]));i=(c.then?(await c)():c)[0];const p="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z";class u extends((0,d.V)(r.WF)){get scrollableElement(){return this.bodyContainer}updated(t){super.updated(t),t.has("open")&&(this._open=this.open)}render(){return r.qy` <wa-dialog .open="${this._open}" .lightDismiss="${!this.preventScrimClose}" without-header aria-labelledby="${(0,s.J)(this.ariaLabelledBy||(void 0!==this.headerTitle?"ha-wa-dialog-title":void 0))}" aria-describedby="${(0,s.J)(this.ariaDescribedBy)}" @wa-show="${this._handleShow}" @wa-after-show="${this._handleAfterShow}" @wa-after-hide="${this._handleAfterHide}"> <slot name="header"> <ha-dialog-header .subtitlePosition="${this.headerSubtitlePosition}" .showBorder="${this._bodyScrolled}"> <slot name="headerNavigationIcon" slot="navigationIcon"> <ha-icon-button data-dialog="close" .label="${this.hass?.localize("ui.common.close")??"Close"}" .path="${p}"></ha-icon-button> </slot> ${void 0!==this.headerTitle?r.qy`<span slot="title" class="title" id="ha-wa-dialog-title"> ${this.headerTitle} </span>`:r.qy`<slot name="headerTitle" slot="title"></slot>`} ${void 0!==this.headerSubtitle?r.qy`<span slot="subtitle">${this.headerSubtitle}</span>`:r.qy`<slot name="headerSubtitle" slot="subtitle"></slot>`} <slot name="headerActionItems" slot="actionItems"></slot> </ha-dialog-header> </slot> <div class="content-wrapper"> <div class="body ha-scrollbar" @scroll="${this._handleBodyScroll}"> <slot></slot> </div> ${this.renderScrollableFades()} </div> <slot name="footer" slot="footer"></slot> </wa-dialog> `}disconnectedCallback(){super.disconnectedCallback(),this._open=!1}_handleBodyScroll(t){this._bodyScrolled=t.target.scrollTop>0}static get styles(){return[...super.styles,h.dp,r.AH`
        wa-dialog {
          --full-width: var(
            --ha-dialog-width-full,
            min(95vw, var(--safe-width))
          );
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
        @media (prefers-reduced-motion: reduce) {
          wa-dialog {
            --show-duration: 0ms;
            --hide-duration: 0ms;
          }
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
              var(--safe-area-offset-left, 0px) - var(
                  --safe-area-offset-right,
                  0px
                )
            ),
            calc(
              var(--safe-area-offset-top, 0px) - var(
                  --safe-area-offset-bottom,
                  0px
                )
            )
          );
          display: flex;
          flex-direction: column;
          overflow: hidden;
        }

        @media all and (max-width: 450px), all and (max-height: 500px) {
          :host([type="standard"]) {
            --ha-dialog-border-radius: 0;

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

        .content-wrapper {
          position: relative;
          flex: 1;
          display: flex;
          flex-direction: column;
          min-height: 0;
        }

        .body {
          position: var(--dialog-content-position, relative);
          padding: var(
            --dialog-content-padding,
            0 var(--ha-space-6) var(--ha-space-6) var(--ha-space-6)
          );
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
          padding: 0;
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
      `]}constructor(...t){super(...t),this.open=!1,this.type="standard",this.width="medium",this.preventScrimClose=!1,this.headerSubtitlePosition="below",this.flexContent=!1,this._open=!1,this._bodyScrolled=!1,this._handleShow=async()=>{this._open=!0,(0,n.r)(this,"opened"),await this.updateComplete,requestAnimationFrame(()=>{this.querySelector("[autofocus]")?.focus()})},this._handleAfterShow=()=>{(0,n.r)(this,"after-show")},this._handleAfterHide=()=>{this._open=!1,(0,n.r)(this,"closed")}}}(0,o.Cg)([(0,l.MZ)({attribute:!1})],u.prototype,"hass",void 0),(0,o.Cg)([(0,l.MZ)({attribute:"aria-labelledby"})],u.prototype,"ariaLabelledBy",void 0),(0,o.Cg)([(0,l.MZ)({attribute:"aria-describedby"})],u.prototype,"ariaDescribedBy",void 0),(0,o.Cg)([(0,l.MZ)({type:Boolean,reflect:!0})],u.prototype,"open",void 0),(0,o.Cg)([(0,l.MZ)({reflect:!0})],u.prototype,"type",void 0),(0,o.Cg)([(0,l.MZ)({type:String,reflect:!0,attribute:"width"})],u.prototype,"width",void 0),(0,o.Cg)([(0,l.MZ)({type:Boolean,reflect:!0,attribute:"prevent-scrim-close"})],u.prototype,"preventScrimClose",void 0),(0,o.Cg)([(0,l.MZ)({attribute:"header-title"})],u.prototype,"headerTitle",void 0),(0,o.Cg)([(0,l.MZ)({attribute:"header-subtitle"})],u.prototype,"headerSubtitle",void 0),(0,o.Cg)([(0,l.MZ)({type:String,attribute:"header-subtitle-position"})],u.prototype,"headerSubtitlePosition",void 0),(0,o.Cg)([(0,l.MZ)({type:Boolean,reflect:!0,attribute:"flexcontent"})],u.prototype,"flexContent",void 0),(0,o.Cg)([(0,l.wk)()],u.prototype,"_open",void 0),(0,o.Cg)([(0,l.P)(".body")],u.prototype,"bodyContainer",void 0),(0,o.Cg)([(0,l.wk)()],u.prototype,"_bodyScrolled",void 0),(0,o.Cg)([(0,l.Ls)({passive:!0})],u.prototype,"_handleBodyScroll",null),u=(0,o.Cg)([(0,l.EM)("ha-wa-dialog")],u),e()}catch(t){e(t)}})},26683(t,e,a){a.a(t,async function(t,o){try{a.r(e);var i=a(62826),r=a(96196),l=a(77845),s=a(94333),n=a(32288),d=a(1087),h=a(18350),c=(a(93444),a(76538),a(67094),a(75709),a(45331)),p=t([h,c]);[h,c]=p.then?(await p)():p;const u="M12,2L1,21H23M12,6L19.53,19H4.47M11,10V14H13V10M11,16V18H13V16",g="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z";class v extends r.WF{async showDialog(t){this._closePromise&&await this._closePromise,this._params=t,this._open=!0}closeDialog(){return!this._open||!this._params?.confirmation&&!this._params?.prompt&&(!this._params||(this._dismiss(),!0))}render(){if(!this._params)return r.s6;const t=this._params.confirmation||!!this._params.prompt,e=this._params.title||this._params.confirmation&&this.hass.localize("ui.dialogs.generic.default_confirmation_title");return r.qy` <ha-wa-dialog .hass="${this.hass}" .open="${this._open}" type="${t?"alert":"standard"}" ?prevent-scrim-close="${t}" @closed="${this._dialogClosed}" aria-labelledby="dialog-box-title" aria-describedby="dialog-box-description"> <ha-dialog-header slot="header"> ${t?r.s6:r.qy`<slot name="headerNavigationIcon" slot="navigationIcon"> <ha-icon-button data-dialog="close" .label="${this.hass?.localize("ui.common.close")??"Close"}" .path="${g}"></ha-icon-button></slot>`} <span class="${(0,s.H)({title:!0,alert:t})}" slot="title" id="dialog-box-title"> ${this._params.warning?r.qy`<ha-svg-icon .path="${u}" style="color:var(--warning-color)"></ha-svg-icon> `:r.s6} ${e} </span> </ha-dialog-header> <div id="dialog-box-description"> ${this._params.text?r.qy` <p>${this._params.text}</p> `:""} ${this._params.prompt?r.qy` <ha-textfield autofocus value="${(0,n.J)(this._params.defaultValue)}" .placeholder="${this._params.placeholder}" .label="${this._params.inputLabel?this._params.inputLabel:""}" .type="${this._params.inputType?this._params.inputType:"text"}" .min="${this._params.inputMin}" .max="${this._params.inputMax}"></ha-textfield> `:""} </div> <ha-dialog-footer slot="footer"> ${t?r.qy` <ha-button slot="secondaryAction" @click="${this._dismiss}" ?autofocus="${!this._params.prompt&&this._params.destructive}" appearance="plain"> ${this._params.dismissText?this._params.dismissText:this.hass.localize("ui.common.cancel")} </ha-button> `:r.s6} <ha-button slot="primaryAction" @click="${this._confirm}" ?autofocus="${!this._params.prompt&&!this._params.destructive}" variant="${this._params.destructive?"danger":"brand"}"> ${this._params.confirmText?this._params.confirmText:this.hass.localize("ui.common.ok")} </ha-button> </ha-dialog-footer> </ha-wa-dialog> `}_cancel(){this._params?.cancel&&this._params.cancel()}_dismiss(){this._closeState="canceled",this._cancel(),this._closeDialog()}_confirm(){this._closeState="confirmed",this._params.confirm&&this._params.confirm(this._textField?.value),this._closeDialog()}_closeDialog(){this._open=!1,this._closePromise=new Promise(t=>{this._closeResolve=t})}_dialogClosed(){(0,d.r)(this,"dialog-closed",{dialog:this.localName}),this._closeState||this._cancel(),this._closeState=void 0,this._params=void 0,this._open=!1,this._closeResolve?.(),this._closeResolve=void 0}constructor(...t){super(...t),this._open=!1}}v.styles=r.AH`:host([inert]){pointer-events:initial!important;cursor:initial!important}a{color:var(--primary-color)}p{margin:0;color:var(--primary-text-color)}.no-bottom-padding{padding-bottom:0}.secondary{color:var(--secondary-text-color)}ha-textfield{width:100%}.title.alert{padding:0 var(--ha-space-2)}@media all and (min-width:450px) and (min-height:500px){.title.alert{padding:0 var(--ha-space-1)}}`,(0,i.Cg)([(0,l.MZ)({attribute:!1})],v.prototype,"hass",void 0),(0,i.Cg)([(0,l.wk)()],v.prototype,"_params",void 0),(0,i.Cg)([(0,l.wk)()],v.prototype,"_open",void 0),(0,i.Cg)([(0,l.wk)()],v.prototype,"_closeState",void 0),(0,i.Cg)([(0,l.P)("ha-textfield")],v.prototype,"_textField",void 0),v=(0,i.Cg)([(0,l.EM)("dialog-box")],v),o()}catch(t){o(t)}})},59992(t,e,a){a.d(e,{V:()=>n});var o=a(62826),i=a(88696),r=a(96196),l=a(94333),s=a(77845);const n=t=>{class e extends t{get scrollableElement(){return e.DEFAULT_SCROLLABLE_ELEMENT}firstUpdated(t){super.firstUpdated?.(t),this.scrollableElement&&this._updateScrollableState(this.scrollableElement),this._attachScrollableElement()}updated(t){super.updated?.(t),this._attachScrollableElement()}disconnectedCallback(){this._detachScrollableElement(),this._contentScrolled=!1,this._contentScrollable=!1,super.disconnectedCallback()}renderScrollableFades(t=!1){return r.qy` <div class="${(0,l.H)({"fade-top":!0,rounded:t,visible:this._contentScrolled})}"></div> <div class="${(0,l.H)({"fade-bottom":!0,rounded:t,visible:this._contentScrollable})}"></div> `}static get styles(){const t=Object.getPrototypeOf(this);var e;return[...void 0===(e=t?.styles??[])?[]:Array.isArray(e)?e:[e],r.AH`.fade-bottom,.fade-top{position:absolute;left:0;right:0;height:var(--ha-space-2);pointer-events:none;transition:opacity 180ms ease-in-out;border-radius:var(--ha-border-radius-square);opacity:0;background:linear-gradient(to bottom,var(--ha-color-shadow-scrollable-fade),transparent)}.fade-top{top:0}.fade-bottom{bottom:0;transform:rotate(180deg)}.fade-bottom.visible,.fade-top.visible{opacity:1}.fade-bottom.rounded,.fade-top.rounded{border-radius:var(--ha-card-border-radius,var(--ha-border-radius-lg));border-bottom-left-radius:var(--ha-border-radius-square);border-bottom-right-radius:var(--ha-border-radius-square)}.fade-top.rounded{border-top-left-radius:var(--ha-border-radius-square);border-top-right-radius:var(--ha-border-radius-square)}.fade-bottom.rounded{border-bottom-left-radius:var(--ha-border-radius-square);border-bottom-right-radius:var(--ha-border-radius-square)}`]}_attachScrollableElement(){const t=this.scrollableElement;t!==this._scrollTarget&&(this._detachScrollableElement(),t&&(this._scrollTarget=t,t.addEventListener("scroll",this._onScroll,{passive:!0}),this._resize.observe(t),this._updateScrollableState(t)))}_detachScrollableElement(){this._scrollTarget&&(this._scrollTarget.removeEventListener("scroll",this._onScroll),this._resize.unobserve?.(this._scrollTarget),this._scrollTarget=void 0)}_updateScrollableState(t){const e=parseFloat(getComputedStyle(t).getPropertyValue("--safe-area-inset-bottom"))||0,{scrollHeight:a=0,clientHeight:o=0,scrollTop:i=0}=t;this._contentScrollable=a-o>i+e+this.scrollFadeSafeAreaPadding}constructor(...t){super(...t),this._contentScrolled=!1,this._contentScrollable=!1,this._onScroll=t=>{const e=t.currentTarget;this._contentScrolled=(e.scrollTop??0)>this.scrollFadeThreshold,this._updateScrollableState(e)},this._resize=new i.P(this,{target:null,callback:t=>{const e=t[0]?.target;e&&this._updateScrollableState(e)}}),this.scrollFadeSafeAreaPadding=4,this.scrollFadeThreshold=4}}return e.DEFAULT_SCROLLABLE_ELEMENT=null,(0,o.Cg)([(0,s.wk)()],e.prototype,"_contentScrolled",void 0),(0,o.Cg)([(0,s.wk)()],e.prototype,"_contentScrollable",void 0),e}},99793(t,e,a){a.d(e,{A:()=>o});const o=a(96196).AH`:host{--width:31rem;--spacing:var(--wa-space-l);--show-duration:200ms;--hide-duration:200ms;display:none}:host([open]){display:block}.dialog{display:flex;flex-direction:column;top:0;right:0;bottom:0;left:0;width:var(--width);max-width:calc(100% - var(--wa-space-2xl));max-height:calc(100% - var(--wa-space-2xl));background-color:var(--wa-color-surface-raised);border-radius:var(--wa-panel-border-radius);border:none;box-shadow:var(--wa-shadow-l);padding:0;margin:auto}.dialog.show{animation:show-dialog var(--show-duration) ease}.dialog.show::backdrop{animation:show-backdrop var(--show-duration,200ms) ease}.dialog.hide{animation:show-dialog var(--hide-duration) ease reverse}.dialog.hide::backdrop{animation:show-backdrop var(--hide-duration,200ms) ease reverse}.dialog.pulse{animation:pulse 250ms ease}.dialog:focus{outline:0}@media screen and (max-width:420px){.dialog{max-height:80vh}}.open{display:flex;opacity:1}.header{flex:0 0 auto;display:flex;flex-wrap:nowrap;padding-inline-start:var(--spacing);padding-block-end:0;padding-inline-end:calc(var(--spacing) - var(--wa-form-control-padding-block));padding-block-start:calc(var(--spacing) - var(--wa-form-control-padding-block))}.title{align-self:center;flex:1 1 auto;font-family:inherit;font-size:var(--wa-font-size-l);font-weight:var(--wa-font-weight-heading);line-height:var(--wa-line-height-condensed);margin:0}.header-actions{align-self:start;display:flex;flex-shrink:0;flex-wrap:wrap;justify-content:end;gap:var(--wa-space-2xs);padding-inline-start:var(--spacing)}.header-actions ::slotted(wa-button),.header-actions wa-button{flex:0 0 auto;display:flex;align-items:center}.body{flex:1 1 auto;display:block;padding:var(--spacing);overflow:auto;-webkit-overflow-scrolling:touch}.body:focus{outline:0}.body:focus-visible{outline:var(--wa-focus-ring);outline-offset:var(--wa-focus-ring-offset)}.footer{flex:0 0 auto;display:flex;flex-wrap:wrap;gap:var(--wa-space-xs);justify-content:end;padding:var(--spacing);padding-block-start:0}.footer ::slotted(wa-button:not(:first-of-type)){margin-inline-start:var(--wa-spacing-xs)}.dialog::backdrop{background-color:var(--wa-color-overlay-modal,rgb(0 0 0 / .25))}@keyframes pulse{0%{scale:1}50%{scale:1.02}100%{scale:1}}@keyframes show-dialog{from{opacity:0;scale:0.8}to{opacity:1;scale:1}}@keyframes show-backdrop{from{opacity:0}to{opacity:1}}@media (forced-colors:active){.dialog{border:solid 1px #fff}}`},93900(t,e,a){a.a(t,async function(t,e){try{var o=a(96196),i=a(77845),r=a(94333),l=a(32288),s=a(17051),n=a(42462),d=a(28438),h=a(98779),c=a(27259),p=a(31247),u=a(93949),g=a(92070),v=a(9395),f=a(32510),b=a(17060),m=a(88496),w=a(99793),y=t([m,b]);[m,b]=y.then?(await y)():y;var _=Object.defineProperty,x=Object.getOwnPropertyDescriptor,$=(t,e,a,o)=>{for(var i,r=o>1?void 0:o?x(e,a):e,l=t.length-1;l>=0;l--)(i=t[l])&&(r=(o?i(e,a,r):i(r))||r);return o&&r&&_(e,a,r),r};let C=class extends f.A{firstUpdated(){this.open&&(this.addOpenListeners(),this.dialog.showModal(),(0,u.JG)(this))}disconnectedCallback(){super.disconnectedCallback(),(0,u.I7)(this),this.removeOpenListeners()}async requestClose(t){const e=new d.L({source:t});if(this.dispatchEvent(e),e.defaultPrevented)return this.open=!0,void(0,c.Ud)(this.dialog,"pulse");this.removeOpenListeners(),await(0,c.Ud)(this.dialog,"hide"),this.open=!1,this.dialog.close(),(0,u.I7)(this);const a=this.originalTrigger;"function"==typeof a?.focus&&setTimeout(()=>a.focus()),this.dispatchEvent(new s.Z)}addOpenListeners(){document.addEventListener("keydown",this.handleDocumentKeyDown)}removeOpenListeners(){document.removeEventListener("keydown",this.handleDocumentKeyDown)}handleDialogCancel(t){t.preventDefault(),this.dialog.classList.contains("hide")||t.target!==this.dialog||this.requestClose(this.dialog)}handleDialogClick(t){const e=t.target.closest('[data-dialog="close"]');e&&(t.stopPropagation(),this.requestClose(e))}async handleDialogPointerDown(t){t.target===this.dialog&&(this.lightDismiss?this.requestClose(this.dialog):await(0,c.Ud)(this.dialog,"pulse"))}handleOpenChange(){this.open&&!this.dialog.open?this.show():!this.open&&this.dialog.open&&(this.open=!0,this.requestClose(this.dialog))}async show(){const t=new h.k;this.dispatchEvent(t),t.defaultPrevented?this.open=!1:(this.addOpenListeners(),this.originalTrigger=document.activeElement,this.open=!0,this.dialog.showModal(),(0,u.JG)(this),requestAnimationFrame(()=>{const t=this.querySelector("[autofocus]");t&&"function"==typeof t.focus?t.focus():this.dialog.focus()}),await(0,c.Ud)(this.dialog,"show"),this.dispatchEvent(new n.q))}render(){const t=!this.withoutHeader,e=this.hasSlotController.test("footer");return o.qy` <dialog aria-labelledby="${this.ariaLabelledby??"title"}" aria-describedby="${(0,l.J)(this.ariaDescribedby)}" part="dialog" class="${(0,r.H)({dialog:!0,open:this.open})}" @cancel="${this.handleDialogCancel}" @click="${this.handleDialogClick}" @pointerdown="${this.handleDialogPointerDown}"> ${t?o.qy` <header part="header" class="header"> <h2 part="title" class="title" id="title"> <slot name="label"> ${this.label.length>0?this.label:String.fromCharCode(8203)} </slot> </h2> <div part="header-actions" class="header-actions"> <slot name="header-actions"></slot> <wa-button part="close-button" exportparts="base:close-button__base" class="close" appearance="plain" @click="${t=>this.requestClose(t.target)}"> <wa-icon name="xmark" label="${this.localize.term("close")}" library="system" variant="solid"></wa-icon> </wa-button> </div> </header> `:""} <div part="body" class="body"><slot></slot></div> ${e?o.qy` <footer part="footer" class="footer"> <slot name="footer"></slot> </footer> `:""} </dialog> `}constructor(){super(...arguments),this.localize=new b.c(this),this.hasSlotController=new g.X(this,"footer","header-actions","label"),this.open=!1,this.label="",this.withoutHeader=!1,this.lightDismiss=!1,this.handleDocumentKeyDown=t=>{"Escape"===t.key&&this.open&&(t.preventDefault(),t.stopPropagation(),this.requestClose(this.dialog))}}};C.css=w.A,$([(0,i.P)(".dialog")],C.prototype,"dialog",2),$([(0,i.MZ)({type:Boolean,reflect:!0})],C.prototype,"open",2),$([(0,i.MZ)({reflect:!0})],C.prototype,"label",2),$([(0,i.MZ)({attribute:"without-header",type:Boolean,reflect:!0})],C.prototype,"withoutHeader",2),$([(0,i.MZ)({attribute:"light-dismiss",type:Boolean})],C.prototype,"lightDismiss",2),$([(0,i.MZ)({attribute:"aria-labelledby"})],C.prototype,"ariaLabelledby",2),$([(0,i.MZ)({attribute:"aria-describedby"})],C.prototype,"ariaDescribedby",2),$([(0,v.w)("open",{waitUntilFirstUpdate:!0})],C.prototype,"handleOpenChange",1),C=$([(0,i.EM)("wa-dialog")],C),document.addEventListener("click",t=>{const e=t.target.closest("[data-dialog]");if(e instanceof Element){const[t,a]=(0,p.v)(e.getAttribute("data-dialog")||"");if("open"===t&&a?.length){const t=e.getRootNode().getElementById(a);"wa-dialog"===t?.localName?t.open=!0:console.warn(`A dialog with an ID of "${a}" could not be found in this document.`)}}}),o.S$||document.addEventListener("pointerdown",()=>{}),e()}catch(t){e(t)}})},17051(t,e,a){a.d(e,{Z:()=>o});class o extends Event{constructor(){super("wa-after-hide",{bubbles:!0,cancelable:!1,composed:!0})}}},42462(t,e,a){a.d(e,{q:()=>o});class o extends Event{constructor(){super("wa-after-show",{bubbles:!0,cancelable:!1,composed:!0})}}},28438(t,e,a){a.d(e,{L:()=>o});class o extends Event{constructor(t){super("wa-hide",{bubbles:!0,cancelable:!0,composed:!0}),this.detail=t}}},98779(t,e,a){a.d(e,{k:()=>o});class o extends Event{constructor(){super("wa-show",{bubbles:!0,cancelable:!0,composed:!0})}}},27259(t,e,a){async function o(t,e,a){return t.animate(e,a).finished.catch(()=>{})}function i(t,e){return new Promise(a=>{const o=new AbortController,{signal:i}=o;if(t.classList.contains(e))return;t.classList.remove(e),t.classList.add(e);let r=()=>{t.classList.remove(e),a(),o.abort()};t.addEventListener("animationend",r,{once:!0,signal:i}),t.addEventListener("animationcancel",r,{once:!0,signal:i})})}function r(t){return(t=t.toString().toLowerCase()).indexOf("ms")>-1?parseFloat(t)||0:t.indexOf("s")>-1?1e3*(parseFloat(t)||0):parseFloat(t)||0}a.d(e,{E9:()=>r,Ud:()=>i,i0:()=>o})},31247(t,e,a){a.d(e,{v:()=>o});a(18111),a(22489),a(61701);function o(t){return t.split(" ").map(t=>t.trim()).filter(t=>""!==t)}},93949(t,e,a){a.d(e,{Rt:()=>l,I7:()=>r,JG:()=>i});a(17642),a(58004),a(33853),a(45876),a(32475),a(15024),a(31698);const o=new Set;function i(t){if(o.add(t),!document.documentElement.classList.contains("wa-scroll-lock")){const t=function(){const t=document.documentElement.clientWidth;return Math.abs(window.innerWidth-t)}()+function(){const t=Number(getComputedStyle(document.body).paddingRight.replace(/px/,""));return isNaN(t)||!t?0:t}();let e=getComputedStyle(document.documentElement).scrollbarGutter;e&&"auto"!==e||(e="stable"),t<2&&(e=""),document.documentElement.style.setProperty("--wa-scroll-lock-gutter",e),document.documentElement.classList.add("wa-scroll-lock"),document.documentElement.style.setProperty("--wa-scroll-lock-size",`${t}px`)}}function r(t){o.delete(t),0===o.size&&(document.documentElement.classList.remove("wa-scroll-lock"),document.documentElement.style.removeProperty("--wa-scroll-lock-size"))}function l(t,e,a="vertical",o="smooth"){const i=function(t,e){return{top:Math.round(t.getBoundingClientRect().top-e.getBoundingClientRect().top),left:Math.round(t.getBoundingClientRect().left-e.getBoundingClientRect().left)}}(t,e),r=i.top+e.scrollTop,l=i.left+e.scrollLeft,s=e.scrollLeft,n=e.scrollLeft+e.offsetWidth,d=e.scrollTop,h=e.scrollTop+e.offsetHeight;"horizontal"!==a&&"both"!==a||(l<s?e.scrollTo({left:l,behavior:o}):l+t.clientWidth>n&&e.scrollTo({left:l-e.offsetWidth+t.clientWidth,behavior:o})),"vertical"!==a&&"both"!==a||(r<d?e.scrollTo({top:r,behavior:o}):r+t.clientHeight>h&&e.scrollTo({top:r-e.offsetHeight+t.clientHeight,behavior:o}))}},88696(t,e,a){a.d(e,{P:()=>l});a(17642),a(58004),a(33853),a(45876),a(32475),a(15024),a(31698);var o=a(37540),i=a(42017),r=a(38028);class l{handleChanges(t){this.value=this.callback?.(t,this.u)}hostConnected(){for(const t of this.t)this.observe(t)}hostDisconnected(){this.disconnect()}async hostUpdated(){!this.o&&this.i&&this.handleChanges([]),this.i=!1}observe(t){this.t.add(t),this.u.observe(t,this.l),this.i=!0,this.h.requestUpdate()}unobserve(t){this.t.delete(t),this.u.unobserve(t)}disconnect(){this.u.disconnect()}target(t){return s(this,t)}constructor(t,{target:e,config:a,callback:o,skipInitial:i}){this.t=new Set,this.o=!1,this.i=!1,this.h=t,null!==e&&this.t.add(e??t),this.l=a,this.o=i??this.o,this.callback=o,r.S||(window.ResizeObserver?(this.u=new ResizeObserver(t=>{this.handleChanges(t),this.h.requestUpdate()}),t.addController(this)):console.warn("ResizeController error: browser does not support ResizeObserver."))}}const s=(0,i.u$)(class extends o.Kq{render(t,e){}update(t,[e,a]){this.controller=e,this.part=t,this.observe=a,!1===a?(e.unobserve(t.element),this.observing=!1):!1===this.observing&&(e.observe(t.element),this.observing=!0)}disconnected(){this.controller?.unobserve(this.part.element),this.observing=!1}reconnected(){!1!==this.observe&&!1===this.observing&&(this.controller?.observe(this.part.element),this.observing=!0)}constructor(){super(...arguments),this.observing=!1}})},37540(t,e,a){a.d(e,{Kq:()=>c});a(17642),a(58004),a(33853),a(45876),a(32475),a(15024),a(31698);var o=a(63937),i=a(42017);const r=(t,e)=>{const a=t._$AN;if(void 0===a)return!1;for(const t of a)t._$AO?.(e,!1),r(t,e);return!0},l=t=>{let e,a;do{if(void 0===(e=t._$AM))break;a=e._$AN,a.delete(t),t=e}while(0===a?.size)},s=t=>{for(let e;e=t._$AM;t=e){let a=e._$AN;if(void 0===a)e._$AN=a=new Set;else if(a.has(t))break;a.add(t),h(e)}};function n(t){void 0!==this._$AN?(l(this),this._$AM=t,s(this)):this._$AM=t}function d(t,e=!1,a=0){const o=this._$AH,i=this._$AN;if(void 0!==i&&0!==i.size)if(e)if(Array.isArray(o))for(let t=a;t<o.length;t++)r(o[t],!1),l(o[t]);else null!=o&&(r(o,!1),l(o));else r(this,t)}const h=t=>{t.type==i.OA.CHILD&&(t._$AP??=d,t._$AQ??=n)};class c extends i.WL{_$AT(t,e,a){super._$AT(t,e,a),s(this),this.isConnected=t._$AU}_$AO(t,e=!0){t!==this.isConnected&&(this.isConnected=t,t?this.reconnected?.():this.disconnected?.()),e&&(r(this,t),l(this))}setValue(t){if((0,o.Rt)(this._$Ct))this._$Ct._$AI(t,this);else{const e=[...this._$Ct._$AH];e[this._$Ci]=t,this._$Ct._$AI(e,this,0)}}disconnected(){}reconnected(){}constructor(){super(...arguments),this._$AN=void 0}}}};
//# sourceMappingURL=4776.f96c2a9c0ae41771.js.map