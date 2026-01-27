export const __rspack_esm_id="5496";export const __rspack_esm_ids=["5496"];export const __webpack_modules__={986(t,e,a){a.a(t,async function(t,e){try{a(44114),a(18111),a(20116),a(7588);var i=a(62826),o=a(96196),r=a(77845),s=a(29485),l=a(22786),h=a(78870),n=a(1087),d=a(38508),c=t([d]);d=(c.then?(await c)():c)[0];const p="M20.65,20.87L18.3,18.5L12,12.23L8.44,8.66L7,7.25L4.27,4.5L3,5.77L5.78,8.55C3.23,11.69 3.42,16.31 6.34,19.24C7.9,20.8 9.95,21.58 12,21.58C13.79,21.58 15.57,21 17.03,19.8L19.73,22.5L21,21.23L20.65,20.87M12,19.59C10.4,19.59 8.89,18.97 7.76,17.83C6.62,16.69 6,15.19 6,13.59C6,12.27 6.43,11 7.21,10L12,14.77V19.59M12,5.1V9.68L19.25,16.94C20.62,14 20.09,10.37 17.65,7.93L12,2.27L8.3,5.97L9.71,7.38L12,5.1Z",g="M17.5,12A1.5,1.5 0 0,1 16,10.5A1.5,1.5 0 0,1 17.5,9A1.5,1.5 0 0,1 19,10.5A1.5,1.5 0 0,1 17.5,12M14.5,8A1.5,1.5 0 0,1 13,6.5A1.5,1.5 0 0,1 14.5,5A1.5,1.5 0 0,1 16,6.5A1.5,1.5 0 0,1 14.5,8M9.5,8A1.5,1.5 0 0,1 8,6.5A1.5,1.5 0 0,1 9.5,5A1.5,1.5 0 0,1 11,6.5A1.5,1.5 0 0,1 9.5,8M6.5,12A1.5,1.5 0 0,1 5,10.5A1.5,1.5 0 0,1 6.5,9A1.5,1.5 0 0,1 8,10.5A1.5,1.5 0 0,1 6.5,12M12,3A9,9 0 0,0 3,12A9,9 0 0,0 12,21A1.5,1.5 0 0,0 13.5,19.5C13.5,19.11 13.35,18.76 13.11,18.5C12.88,18.23 12.73,17.88 12.73,17.5A1.5,1.5 0 0,1 14.23,16H16A5,5 0 0,0 21,11C21,6.58 16.97,3 12,3Z";class u extends o.WF{render(){const t=this.value??this.defaultColor??"";return o.qy` <ha-generic-picker .hass="${this.hass}" .disabled="${this.disabled}" .required="${this.required}" .hideClearIcon="${!this.value&&!!this.defaultColor}" .label="${this.label}" .helper="${this.helper}" .value="${t}" .getItems="${this._getItems}" .rowRenderer="${this._rowRenderer}" .valueRenderer="${this._valueRenderer}" @value-changed="${this._valueChanged}" .notFoundLabel="${this.hass.localize("ui.components.color-picker.no_colors_found")}" .getAdditionalItems="${this._getAdditionalItems}"> </ha-generic-picker> `}_renderColorCircle(t){return o.qy` <span style="${(0,s.W)({"--circle-color":(0,h.M)(t),display:"block","background-color":"var(--circle-color, var(--divider-color))",border:"1px solid var(--outline-color)","border-radius":"var(--ha-border-radius-pill)",width:"20px",height:"20px","box-sizing":"border-box"})}"></span> `}_valueChanged(t){t.stopPropagation();const e=t.detail.value,a=e&&e===this.defaultColor?void 0:e??void 0;this.value=a,(0,n.r)(this,"value-changed",{value:this.value})}constructor(...t){super(...t),this.includeState=!1,this.includeNone=!1,this.disabled=!1,this.required=!1,this._getAdditionalItems=t=>{if(!t||""===t.trim())return[];return this._getColors(this.includeNone,this.includeState,this.defaultColor,this.value).find(e=>e.id===t)?[]:[{id:t,primary:this.hass.localize("ui.components.color-picker.custom_color"),secondary:t}]},this._getItems=()=>this._getColors(this.includeNone,this.includeState,this.defaultColor,this.value),this._getColors=(0,l.A)((t,e,a,i)=>{const o=[],r=this.hass.localize("ui.components.color-picker.default"),s=(t,e)=>e&&r?`${t} (${r})`:t;if(t){const t=this.hass.localize("ui.components.color-picker.none")||"None";o.push({id:"none",primary:s(t,"none"===a),icon_path:p})}if(e){const t=this.hass.localize("ui.components.color-picker.state")||"State";o.push({id:"state",primary:s(t,"state"===a),icon_path:g})}Array.from(h.l).forEach(t=>{const e=this.hass.localize(`ui.components.color-picker.colors.${t}`)||t;o.push({id:t,primary:s(e,a===t)})});const l="none"===i||"state"===i||h.l.has(i||"");return i&&i.length>0&&!l&&o.push({id:i,primary:i}),o}),this._rowRenderer=t=>o.qy` <ha-combo-box-item type="button" compact="compact"> ${"none"===t.id?o.qy`<ha-svg-icon slot="start" .path="${p}"></ha-svg-icon>`:"state"===t.id?o.qy`<ha-svg-icon slot="start" .path="${g}"></ha-svg-icon>`:o.qy`<span slot="start"> ${this._renderColorCircle(t.id)} </span>`} <span slot="headline">${t.primary}</span> ${t.secondary?o.qy`<span slot="supporting-text">${t.secondary}</span>`:o.s6} </ha-combo-box-item> `,this._valueRenderer=t=>"none"===t?o.qy` <ha-svg-icon slot="start" .path="${p}"></ha-svg-icon> <span slot="headline"> ${this.hass.localize("ui.components.color-picker.none")} </span> `:"state"===t?o.qy` <ha-svg-icon slot="start" .path="${g}"></ha-svg-icon> <span slot="headline"> ${this.hass.localize("ui.components.color-picker.state")} </span> `:o.qy` <span slot="start">${this._renderColorCircle(t)}</span> <span slot="headline"> ${this.hass.localize(`ui.components.color-picker.colors.${t}`)||t} </span> `}}(0,i.Cg)([(0,r.MZ)({attribute:!1})],u.prototype,"hass",void 0),(0,i.Cg)([(0,r.MZ)()],u.prototype,"label",void 0),(0,i.Cg)([(0,r.MZ)()],u.prototype,"helper",void 0),(0,i.Cg)([(0,r.MZ)()],u.prototype,"value",void 0),(0,i.Cg)([(0,r.MZ)({type:String,attribute:"default_color"})],u.prototype,"defaultColor",void 0),(0,i.Cg)([(0,r.MZ)({type:Boolean,attribute:"include_state"})],u.prototype,"includeState",void 0),(0,i.Cg)([(0,r.MZ)({type:Boolean,attribute:"include_none"})],u.prototype,"includeNone",void 0),(0,i.Cg)([(0,r.MZ)({type:Boolean})],u.prototype,"disabled",void 0),(0,i.Cg)([(0,r.MZ)({type:Boolean})],u.prototype,"required",void 0),u=(0,i.Cg)([(0,r.EM)("ha-color-picker")],u),e()}catch(t){e(t)}})},93444(t,e,a){var i=a(62826),o=a(96196),r=a(77845);class s extends o.WF{render(){return o.qy` <footer> <slot name="secondaryAction"></slot> <slot name="primaryAction"></slot> </footer> `}static get styles(){return[o.AH`footer{display:flex;gap:var(--ha-space-3);justify-content:flex-end;align-items:center;width:100%}`]}}s=(0,i.Cg)([(0,r.EM)("ha-dialog-footer")],s)},76538(t,e,a){var i=a(62826),o=a(96196),r=a(77845);class s extends o.WF{render(){const t=o.qy`<div class="header-title"> <slot name="title"></slot> </div>`,e=o.qy`<div class="header-subtitle"> <slot name="subtitle"></slot> </div>`;return o.qy` <header class="header"> <div class="header-bar"> <section class="header-navigation-icon"> <slot name="navigationIcon"></slot> </section> <section class="header-content"> ${"above"===this.subtitlePosition?o.qy`${e}${t}`:o.qy`${t}${e}`} </section> <section class="header-action-items"> <slot name="actionItems"></slot> </section> </div> <slot></slot> </header> `}static get styles(){return[o.AH`:host{display:block}:host([show-border]){border-bottom:1px solid var(--mdc-dialog-scroll-divider-color,rgba(0,0,0,.12))}.header-bar{display:flex;flex-direction:row;align-items:center;padding:0 var(--ha-space-1);box-sizing:border-box}.header-content{flex:1;padding:10px var(--ha-space-1);display:flex;flex-direction:column;justify-content:center;min-height:var(--ha-space-12);min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.header-title{height:var(--ha-dialog-header-title-height,calc(var(--ha-font-size-xl) + var(--ha-space-1)));font-size:var(--ha-font-size-xl);line-height:var(--ha-line-height-condensed);font-weight:var(--ha-font-weight-medium);color:var(--ha-dialog-header-title-color,var(--primary-text-color))}.header-subtitle{font-size:var(--ha-font-size-m);line-height:var(--ha-line-height-normal);color:var(--ha-dialog-header-subtitle-color,var(--secondary-text-color))}@media all and (min-width:450px) and (min-height:500px){.header-bar{padding:0 var(--ha-space-2)}}.header-navigation-icon{flex:none;min-width:var(--ha-space-2);height:100%;display:flex;flex-direction:row}.header-action-items{flex:none;min-width:var(--ha-space-2);height:100%;display:flex;flex-direction:row}`]}constructor(...t){super(...t),this.subtitlePosition="below",this.showBorder=!1}}(0,i.Cg)([(0,r.MZ)({type:String,attribute:"subtitle-position"})],s.prototype,"subtitlePosition",void 0),(0,i.Cg)([(0,r.MZ)({type:Boolean,reflect:!0,attribute:"show-border"})],s.prototype,"showBorder",void 0),s=(0,i.Cg)([(0,r.EM)("ha-dialog-header")],s)},59646(t,e,a){var i=a(62826),o=a(4845),r=a(49065),s=a(96196),l=a(77845),h=a(88360);class n extends o.U{firstUpdated(){super.firstUpdated(),this.addEventListener("change",()=>{this.haptic&&(0,h.j)(this,"light")})}constructor(...t){super(...t),this.haptic=!1}}n.styles=[r.R,s.AH`:host{--mdc-theme-secondary:var(--switch-checked-color)}.mdc-switch.mdc-switch--checked .mdc-switch__thumb{background-color:var(--switch-checked-button-color);border-color:var(--switch-checked-button-color)}.mdc-switch.mdc-switch--checked .mdc-switch__track{background-color:var(--switch-checked-track-color);border-color:var(--switch-checked-track-color)}.mdc-switch:not(.mdc-switch--checked) .mdc-switch__thumb{background-color:var(--switch-unchecked-button-color);border-color:var(--switch-unchecked-button-color)}.mdc-switch:not(.mdc-switch--checked) .mdc-switch__track{background-color:var(--switch-unchecked-track-color);border-color:var(--switch-unchecked-track-color)}`],(0,i.Cg)([(0,l.MZ)({type:Boolean})],n.prototype,"haptic",void 0),n=(0,i.Cg)([(0,l.EM)("ha-switch")],n)},56304(t,e,a){var i=a(62826),o=a(11896),r=a(92347),s=a(75057),l=a(96196),h=a(77845);class n extends o.u{updated(t){super.updated(t),this.autogrow&&t.has("value")&&(this.mdcRoot.dataset.value=this.value+'=​"')}constructor(...t){super(...t),this.autogrow=!1}}n.styles=[r.R,s.R,l.AH`:host([autogrow]) .mdc-text-field{position:relative;min-height:74px;min-width:178px;max-height:200px}:host([autogrow]) .mdc-text-field:after{content:attr(data-value);margin-top:23px;margin-bottom:9px;line-height:var(--ha-line-height-normal);min-height:42px;padding:0px 32px 0 16px;letter-spacing:var(
          --mdc-typography-subtitle1-letter-spacing,
          .009375em
        );visibility:hidden;white-space:pre-wrap}:host([autogrow]) .mdc-text-field__input{position:absolute;height:calc(100% - 32px)}:host([autogrow]) .mdc-text-field.mdc-text-field--no-label:after{margin-top:16px;margin-bottom:16px}.mdc-floating-label{inset-inline-start:16px!important;inset-inline-end:initial!important;transform-origin:var(--float-start) top}@media only screen and (min-width:459px){:host([mobile-multiline]) .mdc-text-field__input{white-space:nowrap;max-height:16px}}`],(0,i.Cg)([(0,h.MZ)({type:Boolean,reflect:!0})],n.prototype,"autogrow",void 0),n=(0,i.Cg)([(0,h.EM)("ha-textarea")],n)},45331(t,e,a){a.a(t,async function(t,e){try{var i=a(62826),o=a(93900),r=a(96196),s=a(77845),l=a(32288),h=a(1087),n=a(59992),d=a(14503),c=(a(76538),a(50888),t([o]));o=(c.then?(await c)():c)[0];const p="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z";class g extends((0,n.V)(r.WF)){get scrollableElement(){return this.bodyContainer}updated(t){super.updated(t),t.has("open")&&(this._open=this.open)}render(){return r.qy` <wa-dialog .open="${this._open}" .lightDismiss="${!this.preventScrimClose}" without-header aria-labelledby="${(0,l.J)(this.ariaLabelledBy||(void 0!==this.headerTitle?"ha-wa-dialog-title":void 0))}" aria-describedby="${(0,l.J)(this.ariaDescribedBy)}" @wa-show="${this._handleShow}" @wa-after-show="${this._handleAfterShow}" @wa-after-hide="${this._handleAfterHide}"> <slot name="header"> <ha-dialog-header .subtitlePosition="${this.headerSubtitlePosition}" .showBorder="${this._bodyScrolled}"> <slot name="headerNavigationIcon" slot="navigationIcon"> <ha-icon-button data-dialog="close" .label="${this.hass?.localize("ui.common.close")??"Close"}" .path="${p}"></ha-icon-button> </slot> ${void 0!==this.headerTitle?r.qy`<span slot="title" class="title" id="ha-wa-dialog-title"> ${this.headerTitle} </span>`:r.qy`<slot name="headerTitle" slot="title"></slot>`} ${void 0!==this.headerSubtitle?r.qy`<span slot="subtitle">${this.headerSubtitle}</span>`:r.qy`<slot name="headerSubtitle" slot="subtitle"></slot>`} <slot name="headerActionItems" slot="actionItems"></slot> </ha-dialog-header> </slot> <div class="content-wrapper"> <div class="body ha-scrollbar" @scroll="${this._handleBodyScroll}"> <slot></slot> </div> ${this.renderScrollableFades()} </div> <slot name="footer" slot="footer"></slot> </wa-dialog> `}disconnectedCallback(){super.disconnectedCallback(),this._open=!1}_handleBodyScroll(t){this._bodyScrolled=t.target.scrollTop>0}static get styles(){return[...super.styles,d.dp,r.AH`
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
      `]}constructor(...t){super(...t),this.open=!1,this.type="standard",this.width="medium",this.preventScrimClose=!1,this.headerSubtitlePosition="below",this.flexContent=!1,this._open=!1,this._bodyScrolled=!1,this._handleShow=async()=>{this._open=!0,(0,h.r)(this,"opened"),await this.updateComplete,requestAnimationFrame(()=>{this.querySelector("[autofocus]")?.focus()})},this._handleAfterShow=()=>{(0,h.r)(this,"after-show")},this._handleAfterHide=()=>{this._open=!1,(0,h.r)(this,"closed")}}}(0,i.Cg)([(0,s.MZ)({attribute:!1})],g.prototype,"hass",void 0),(0,i.Cg)([(0,s.MZ)({attribute:"aria-labelledby"})],g.prototype,"ariaLabelledBy",void 0),(0,i.Cg)([(0,s.MZ)({attribute:"aria-describedby"})],g.prototype,"ariaDescribedBy",void 0),(0,i.Cg)([(0,s.MZ)({type:Boolean,reflect:!0})],g.prototype,"open",void 0),(0,i.Cg)([(0,s.MZ)({reflect:!0})],g.prototype,"type",void 0),(0,i.Cg)([(0,s.MZ)({type:String,reflect:!0,attribute:"width"})],g.prototype,"width",void 0),(0,i.Cg)([(0,s.MZ)({type:Boolean,reflect:!0,attribute:"prevent-scrim-close"})],g.prototype,"preventScrimClose",void 0),(0,i.Cg)([(0,s.MZ)({attribute:"header-title"})],g.prototype,"headerTitle",void 0),(0,i.Cg)([(0,s.MZ)({attribute:"header-subtitle"})],g.prototype,"headerSubtitle",void 0),(0,i.Cg)([(0,s.MZ)({type:String,attribute:"header-subtitle-position"})],g.prototype,"headerSubtitlePosition",void 0),(0,i.Cg)([(0,s.MZ)({type:Boolean,reflect:!0,attribute:"flexcontent"})],g.prototype,"flexContent",void 0),(0,i.Cg)([(0,s.wk)()],g.prototype,"_open",void 0),(0,i.Cg)([(0,s.P)(".body")],g.prototype,"bodyContainer",void 0),(0,i.Cg)([(0,s.wk)()],g.prototype,"_bodyScrolled",void 0),(0,i.Cg)([(0,s.Ls)({passive:!0})],g.prototype,"_handleBodyScroll",null),g=(0,i.Cg)([(0,s.EM)("ha-wa-dialog")],g),e()}catch(t){e(t)}})},88360(t,e,a){a.d(e,{j:()=>o});var i=a(1087);const o=(t,e)=>{(0,i.r)(t,"haptic",e)}},427(t,e,a){a.a(t,async function(t,i){try{a.r(e);var o=a(62826),r=a(96196),s=a(77845),l=a(1087),h=(a(38962),a(18350)),n=a(986),d=(a(93444),a(59646),a(45331)),c=(a(56304),a(75709),a(14503)),p=t([h,n,d]);[h,n,d]=p.then?(await p)():p;class g extends r.WF{showDialog(t){this._params=t,this._error=void 0,this._params.entry?(this._name=this._params.entry.name||"",this._icon=this._params.entry.icon||"",this._color=this._params.entry.color||"",this._description=this._params.entry.description||""):(this._name=this._params.suggestedName||"",this._icon="",this._color="",this._description=""),this._open=!0}closeDialog(){return this._open=!1,!0}_dialogClosed(){this._params=void 0,(0,l.r)(this,"dialog-closed",{dialog:this.localName})}render(){return this._params?r.qy` <ha-wa-dialog .hass="${this.hass}" .open="${this._open}" header-title="${this._params.entry?this._params.entry.name||this._params.entry.label_id:this.hass.localize("ui.dialogs.label-detail.new_label")}" @closed="${this._dialogClosed}"> <div> ${this._error?r.qy`<ha-alert alert-type="error">${this._error}</ha-alert>`:""} <div class="form"> <ha-textfield autofocus .value="${this._name}" .configValue="${"name"}" @input="${this._input}" .label="${this.hass.localize("ui.dialogs.label-detail.name")}" .validationMessage="${this.hass.localize("ui.dialogs.label-detail.required_error_msg")}" required></ha-textfield> <ha-icon-picker .value="${this._icon}" .hass="${this.hass}" .configValue="${"icon"}" @value-changed="${this._valueChanged}" .label="${this.hass.localize("ui.dialogs.label-detail.icon")}"></ha-icon-picker> <ha-color-picker .value="${this._color}" .configValue="${"color"}" .hass="${this.hass}" @value-changed="${this._valueChanged}" .label="${this.hass.localize("ui.dialogs.label-detail.color")}"></ha-color-picker> <ha-textarea .value="${this._description}" .configValue="${"description"}" @input="${this._input}" .label="${this.hass.localize("ui.dialogs.label-detail.description")}"></ha-textarea> </div> </div> <ha-dialog-footer slot="footer"> ${this._params.entry&&this._params.removeEntry?r.qy` <ha-button slot="secondaryAction" variant="danger" appearance="plain" @click="${this._deleteEntry}" .disabled="${this._submitting}"> ${this.hass.localize("ui.common.delete")} </ha-button> `:r.s6} <ha-button slot="primaryAction" @click="${this._updateEntry}" .disabled="${this._submitting||!this._name}"> ${this._params.entry?this.hass.localize("ui.common.update"):this.hass.localize("ui.common.create")} </ha-button> </ha-dialog-footer> </ha-wa-dialog> `:r.s6}_input(t){const e=t.target,a=e.configValue;this._error=void 0,this[`_${a}`]=e.value}_valueChanged(t){const e=t.target.configValue;this._error=void 0,this[`_${e}`]=t.detail.value||""}async _updateEntry(){this._submitting=!0;try{const t={name:this._name.trim(),icon:this._icon.trim()||null,color:this._color.trim()||null,description:this._description.trim()||null};this._params.entry?await this._params.updateEntry(t):await this._params.createEntry(t),this.closeDialog()}catch(t){this._error=t?t.message:"Unknown error"}finally{this._submitting=!1}}async _deleteEntry(){this._submitting=!0;try{await this._params.removeEntry()&&(this._params=void 0)}finally{this._submitting=!1}}static get styles(){return[c.nA,r.AH`a{color:var(--primary-color)}ha-color-picker,ha-icon-picker,ha-textarea,ha-textfield{display:block}ha-color-picker,ha-textarea{margin-top:16px}`]}constructor(...t){super(...t),this._submitting=!1,this._open=!1}}(0,o.Cg)([(0,s.MZ)({attribute:!1})],g.prototype,"hass",void 0),(0,o.Cg)([(0,s.wk)()],g.prototype,"_name",void 0),(0,o.Cg)([(0,s.wk)()],g.prototype,"_icon",void 0),(0,o.Cg)([(0,s.wk)()],g.prototype,"_color",void 0),(0,o.Cg)([(0,s.wk)()],g.prototype,"_description",void 0),(0,o.Cg)([(0,s.wk)()],g.prototype,"_error",void 0),(0,o.Cg)([(0,s.wk)()],g.prototype,"_params",void 0),(0,o.Cg)([(0,s.wk)()],g.prototype,"_submitting",void 0),(0,o.Cg)([(0,s.wk)()],g.prototype,"_open",void 0),g=(0,o.Cg)([(0,s.EM)("dialog-label-detail")],g),i()}catch(t){i(t)}})}};
//# sourceMappingURL=5496.2d95e8d1d5cffff1.js.map