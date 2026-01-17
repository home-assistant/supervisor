export const __rspack_esm_id="5708";export const __rspack_esm_ids=["5708"];export const __webpack_modules__={93444(t,e,i){var a=i(62826),o=i(96196),s=i(77845);class r extends o.WF{render(){return o.qy` <footer> <slot name="secondaryAction"></slot> <slot name="primaryAction"></slot> </footer> `}static get styles(){return[o.AH`footer{display:flex;gap:var(--ha-space-3);justify-content:flex-end;align-items:center;width:100%}`]}}r=(0,a.Cg)([(0,s.EM)("ha-dialog-footer")],r)},44010(t,e,i){var a=i(62826),o=i(4042),s=i(77845);class r extends o.A{constructor(...t){super(...t),this.name="fadeIn",this.fill="both",this.play=!0,this.iterations=1}}(0,a.Cg)([(0,s.MZ)()],r.prototype,"name",void 0),(0,a.Cg)([(0,s.MZ)()],r.prototype,"fill",void 0),(0,a.Cg)([(0,s.MZ)({type:Boolean})],r.prototype,"play",void 0),(0,a.Cg)([(0,s.MZ)({type:Number})],r.prototype,"iterations",void 0),r=(0,a.Cg)([(0,s.EM)("ha-fade-in")],r)},71418(t,e,i){var a=i(62826),o=i(96196),s=i(77845);i(50888),i(75709);class r extends o.WF{render(){return o.qy`<ha-textfield .invalid="${this.invalid}" .errorMessage="${this.errorMessage}" .icon="${this.icon}" .iconTrailing="${this.iconTrailing}" .autocomplete="${this.autocomplete}" .autocorrect="${this.autocorrect}" .inputSpellcheck="${this.inputSpellcheck}" .value="${this.value}" .placeholder="${this.placeholder}" .label="${this.label}" .disabled="${this.disabled}" .required="${this.required}" .minLength="${this.minLength}" .maxLength="${this.maxLength}" .outlined="${this.outlined}" .helper="${this.helper}" .validateOnInitialRender="${this.validateOnInitialRender}" .validationMessage="${this.validationMessage}" .autoValidate="${this.autoValidate}" .pattern="${this.pattern}" .size="${this.size}" .helperPersistent="${this.helperPersistent}" .charCounter="${this.charCounter}" .endAligned="${this.endAligned}" .prefix="${this.prefix}" .name="${this.name}" .inputMode="${this.inputMode}" .readOnly="${this.readOnly}" .autocapitalize="${this.autocapitalize}" .type="${this._unmaskedPassword?"text":"password"}" .suffix="${o.qy`<div style="width:24px"></div>`}" @input="${this._handleInputEvent}" @change="${this._handleChangeEvent}"></ha-textfield> <ha-icon-button .label="${this.hass?.localize(this._unmaskedPassword?"ui.components.selectors.text.hide_password":"ui.components.selectors.text.show_password")||(this._unmaskedPassword?"Hide password":"Show password")}" @click="${this._toggleUnmaskedPassword}" .path="${this._unmaskedPassword?"M11.83,9L15,12.16C15,12.11 15,12.05 15,12A3,3 0 0,0 12,9C11.94,9 11.89,9 11.83,9M7.53,9.8L9.08,11.35C9.03,11.56 9,11.77 9,12A3,3 0 0,0 12,15C12.22,15 12.44,14.97 12.65,14.92L14.2,16.47C13.53,16.8 12.79,17 12,17A5,5 0 0,1 7,12C7,11.21 7.2,10.47 7.53,9.8M2,4.27L4.28,6.55L4.73,7C3.08,8.3 1.78,10 1,12C2.73,16.39 7,19.5 12,19.5C13.55,19.5 15.03,19.2 16.38,18.66L16.81,19.08L19.73,22L21,20.73L3.27,3M12,7A5,5 0 0,1 17,12C17,12.64 16.87,13.26 16.64,13.82L19.57,16.75C21.07,15.5 22.27,13.86 23,12C21.27,7.61 17,4.5 12,4.5C10.6,4.5 9.26,4.75 8,5.2L10.17,7.35C10.74,7.13 11.35,7 12,7Z":"M12,9A3,3 0 0,0 9,12A3,3 0 0,0 12,15A3,3 0 0,0 15,12A3,3 0 0,0 12,9M12,17A5,5 0 0,1 7,12A5,5 0 0,1 12,7A5,5 0 0,1 17,12A5,5 0 0,1 12,17M12,4.5C7,4.5 2.73,7.61 1,12C2.73,16.39 7,19.5 12,19.5C17,19.5 21.27,16.39 23,12C21.27,7.61 17,4.5 12,4.5Z"}"></ha-icon-button>`}focus(){this._textField.focus()}checkValidity(){return this._textField.checkValidity()}reportValidity(){return this._textField.reportValidity()}setCustomValidity(t){return this._textField.setCustomValidity(t)}layout(){return this._textField.layout()}_toggleUnmaskedPassword(){this._unmaskedPassword=!this._unmaskedPassword}_handleInputEvent(t){this.value=t.target.value}_handleChangeEvent(t){this.value=t.target.value,this._reDispatchEvent(t)}_reDispatchEvent(t){const e=new Event(t.type,t);this.dispatchEvent(e)}constructor(...t){super(...t),this.icon=!1,this.iconTrailing=!1,this.autocorrect=!0,this.value="",this.placeholder="",this.label="",this.disabled=!1,this.required=!1,this.minLength=-1,this.maxLength=-1,this.outlined=!1,this.helper="",this.validateOnInitialRender=!1,this.validationMessage="",this.autoValidate=!1,this.pattern="",this.size=null,this.helperPersistent=!1,this.charCounter=!1,this.endAligned=!1,this.prefix="",this.suffix="",this.name="",this.readOnly=!1,this.autocapitalize="",this._unmaskedPassword=!1}}r.styles=o.AH`:host{display:block;position:relative}ha-textfield{width:100%}ha-icon-button{position:absolute;top:8px;right:8px;inset-inline-start:initial;inset-inline-end:8px;--mdc-icon-button-size:40px;--mdc-icon-size:20px;color:var(--secondary-text-color);direction:var(--direction)}`,(0,a.Cg)([(0,s.MZ)({attribute:!1})],r.prototype,"hass",void 0),(0,a.Cg)([(0,s.MZ)({type:Boolean})],r.prototype,"invalid",void 0),(0,a.Cg)([(0,s.MZ)({attribute:"error-message"})],r.prototype,"errorMessage",void 0),(0,a.Cg)([(0,s.MZ)({type:Boolean})],r.prototype,"icon",void 0),(0,a.Cg)([(0,s.MZ)({type:Boolean})],r.prototype,"iconTrailing",void 0),(0,a.Cg)([(0,s.MZ)()],r.prototype,"autocomplete",void 0),(0,a.Cg)([(0,s.MZ)({type:Boolean})],r.prototype,"autocorrect",void 0),(0,a.Cg)([(0,s.MZ)({attribute:"input-spellcheck"})],r.prototype,"inputSpellcheck",void 0),(0,a.Cg)([(0,s.MZ)({type:String})],r.prototype,"value",void 0),(0,a.Cg)([(0,s.MZ)({type:String})],r.prototype,"placeholder",void 0),(0,a.Cg)([(0,s.MZ)({type:String})],r.prototype,"label",void 0),(0,a.Cg)([(0,s.MZ)({type:Boolean,reflect:!0})],r.prototype,"disabled",void 0),(0,a.Cg)([(0,s.MZ)({type:Boolean})],r.prototype,"required",void 0),(0,a.Cg)([(0,s.MZ)({type:Number})],r.prototype,"minLength",void 0),(0,a.Cg)([(0,s.MZ)({type:Number})],r.prototype,"maxLength",void 0),(0,a.Cg)([(0,s.MZ)({type:Boolean,reflect:!0})],r.prototype,"outlined",void 0),(0,a.Cg)([(0,s.MZ)({type:String})],r.prototype,"helper",void 0),(0,a.Cg)([(0,s.MZ)({type:Boolean})],r.prototype,"validateOnInitialRender",void 0),(0,a.Cg)([(0,s.MZ)({type:String})],r.prototype,"validationMessage",void 0),(0,a.Cg)([(0,s.MZ)({type:Boolean})],r.prototype,"autoValidate",void 0),(0,a.Cg)([(0,s.MZ)({type:String})],r.prototype,"pattern",void 0),(0,a.Cg)([(0,s.MZ)({type:Number})],r.prototype,"size",void 0),(0,a.Cg)([(0,s.MZ)({type:Boolean})],r.prototype,"helperPersistent",void 0),(0,a.Cg)([(0,s.MZ)({type:Boolean})],r.prototype,"charCounter",void 0),(0,a.Cg)([(0,s.MZ)({type:Boolean})],r.prototype,"endAligned",void 0),(0,a.Cg)([(0,s.MZ)({type:String})],r.prototype,"prefix",void 0),(0,a.Cg)([(0,s.MZ)({type:String})],r.prototype,"suffix",void 0),(0,a.Cg)([(0,s.MZ)({type:String})],r.prototype,"name",void 0),(0,a.Cg)([(0,s.MZ)({type:String,attribute:"input-mode"})],r.prototype,"inputMode",void 0),(0,a.Cg)([(0,s.MZ)({type:Boolean})],r.prototype,"readOnly",void 0),(0,a.Cg)([(0,s.MZ)({attribute:!1,type:String})],r.prototype,"autocapitalize",void 0),(0,a.Cg)([(0,s.wk)()],r.prototype,"_unmaskedPassword",void 0),(0,a.Cg)([(0,s.P)("ha-textfield")],r.prototype,"_textField",void 0),(0,a.Cg)([(0,s.Ls)({passive:!0})],r.prototype,"_handleInputEvent",null),(0,a.Cg)([(0,s.Ls)({passive:!0})],r.prototype,"_handleChangeEvent",null),r=(0,a.Cg)([(0,s.EM)("ha-password-field")],r)},45331(t,e,i){i.a(t,async function(t,e){try{var a=i(62826),o=i(93900),s=i(96196),r=i(77845),n=i(32288),l=i(1087),d=i(59992),h=i(14503),p=(i(76538),i(50888),t([o]));o=(p.then?(await p)():p)[0];const c="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z";class g extends((0,d.V)(s.WF)){get scrollableElement(){return this.bodyContainer}updated(t){super.updated(t),t.has("open")&&(this._open=this.open)}render(){return s.qy` <wa-dialog .open="${this._open}" .lightDismiss="${!this.preventScrimClose}" without-header aria-labelledby="${(0,n.J)(this.ariaLabelledBy||(void 0!==this.headerTitle?"ha-wa-dialog-title":void 0))}" aria-describedby="${(0,n.J)(this.ariaDescribedBy)}" @wa-show="${this._handleShow}" @wa-after-show="${this._handleAfterShow}" @wa-after-hide="${this._handleAfterHide}"> <slot name="header"> <ha-dialog-header .subtitlePosition="${this.headerSubtitlePosition}" .showBorder="${this._bodyScrolled}"> <slot name="headerNavigationIcon" slot="navigationIcon"> <ha-icon-button data-dialog="close" .label="${this.hass?.localize("ui.common.close")??"Close"}" .path="${c}"></ha-icon-button> </slot> ${void 0!==this.headerTitle?s.qy`<span slot="title" class="title" id="ha-wa-dialog-title"> ${this.headerTitle} </span>`:s.qy`<slot name="headerTitle" slot="title"></slot>`} ${void 0!==this.headerSubtitle?s.qy`<span slot="subtitle">${this.headerSubtitle}</span>`:s.qy`<slot name="headerSubtitle" slot="subtitle"></slot>`} <slot name="headerActionItems" slot="actionItems"></slot> </ha-dialog-header> </slot> <div class="content-wrapper"> <div class="body ha-scrollbar" @scroll="${this._handleBodyScroll}"> <slot></slot> </div> ${this.renderScrollableFades()} </div> <slot name="footer" slot="footer"></slot> </wa-dialog> `}disconnectedCallback(){super.disconnectedCallback(),this._open=!1}_handleBodyScroll(t){this._bodyScrolled=t.target.scrollTop>0}static get styles(){return[...super.styles,h.dp,s.AH`
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
      `]}constructor(...t){super(...t),this.open=!1,this.type="standard",this.width="medium",this.preventScrimClose=!1,this.headerSubtitlePosition="below",this.flexContent=!1,this._open=!1,this._bodyScrolled=!1,this._handleShow=async()=>{this._open=!0,(0,l.r)(this,"opened"),await this.updateComplete,requestAnimationFrame(()=>{this.querySelector("[autofocus]")?.focus()})},this._handleAfterShow=()=>{(0,l.r)(this,"after-show")},this._handleAfterHide=()=>{this._open=!1,(0,l.r)(this,"closed")}}}(0,a.Cg)([(0,r.MZ)({attribute:!1})],g.prototype,"hass",void 0),(0,a.Cg)([(0,r.MZ)({attribute:"aria-labelledby"})],g.prototype,"ariaLabelledBy",void 0),(0,a.Cg)([(0,r.MZ)({attribute:"aria-describedby"})],g.prototype,"ariaDescribedBy",void 0),(0,a.Cg)([(0,r.MZ)({type:Boolean,reflect:!0})],g.prototype,"open",void 0),(0,a.Cg)([(0,r.MZ)({reflect:!0})],g.prototype,"type",void 0),(0,a.Cg)([(0,r.MZ)({type:String,reflect:!0,attribute:"width"})],g.prototype,"width",void 0),(0,a.Cg)([(0,r.MZ)({type:Boolean,reflect:!0,attribute:"prevent-scrim-close"})],g.prototype,"preventScrimClose",void 0),(0,a.Cg)([(0,r.MZ)({attribute:"header-title"})],g.prototype,"headerTitle",void 0),(0,a.Cg)([(0,r.MZ)({attribute:"header-subtitle"})],g.prototype,"headerSubtitle",void 0),(0,a.Cg)([(0,r.MZ)({type:String,attribute:"header-subtitle-position"})],g.prototype,"headerSubtitlePosition",void 0),(0,a.Cg)([(0,r.MZ)({type:Boolean,reflect:!0,attribute:"flexcontent"})],g.prototype,"flexContent",void 0),(0,a.Cg)([(0,r.wk)()],g.prototype,"_open",void 0),(0,a.Cg)([(0,r.P)(".body")],g.prototype,"bodyContainer",void 0),(0,a.Cg)([(0,r.wk)()],g.prototype,"_bodyScrolled",void 0),(0,a.Cg)([(0,r.Ls)({passive:!0})],g.prototype,"_handleBodyScroll",null),g=(0,a.Cg)([(0,r.EM)("ha-wa-dialog")],g),e()}catch(t){e(t)}})},76944(t,e,i){i.d(e,{MV:()=>o,d8:()=>a});const a=async t=>t.callWS({type:"application_credentials/config"}),o=async(t,e,i,a,o)=>t.callWS({type:"application_credentials/create",domain:e,client_id:i,client_secret:a,name:o})},59815(t,e,i){i.a(t,async function(t,a){try{i.r(e),i.d(e,{DialogAddApplicationCredential:()=>y});i(18111),i(20116),i(61701);var o=i(62826),s=i(96196),r=i(77845),n=i(1087),l=(i(38962),i(18350)),d=(i(93444),i(44010),i(38508)),h=(i(60545),i(71418),i(65829)),p=(i(75709),i(45331)),c=i(76944),g=i(95350),u=i(14503),v=i(36918),m=t([l,d,h,p]);[l,d,h,p]=m.then?(await m)():m;const _="M14,3V5H17.59L7.76,14.83L9.17,16.24L19,6.41V10H21V3M19,19H5V5H12V3H5C3.89,3 3,3.9 3,5V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19V12H19V19Z";class y extends s.WF{showDialog(t){this._params=t,this._domain=t.selectedDomain,this._manifest=t.manifest,this._name="",this._description="",this._clientId="",this._clientSecret="",this._error=void 0,this._loading=!1,this._open=!0,this._fetchConfig()}async _fetchConfig(){this._config=await(0,c.d8)(this.hass),this._domains=Object.keys(this._config.integrations).map(t=>({id:t,name:(0,g.p$)(this.hass.localize,t)})),await this.hass.loadBackendTranslation("application_credentials"),this._updateDescription()}render(){if(!this._params)return s.s6;const t=this._params.selectedDomain?(0,g.p$)(this.hass.localize,this._domain):"";return s.qy` <ha-wa-dialog .hass="${this.hass}" .open="${this._open}" @closed="${this._abortDialog}" .preventScrimClose="${!!(this._domain||this._name||this._clientId||this._clientSecret)}" .headerTitle="${this.hass.localize("ui.panel.config.application_credentials.editor.caption")}"> ${this._config?s.qy`<div> ${this._error?s.qy`<ha-alert alert-type="error">${this._error}</ha-alert> `:s.s6} ${this._params.selectedDomain&&!this._description?s.qy`<p> ${this.hass.localize("ui.panel.config.application_credentials.editor.missing_credentials",{integration:t})} ${this._manifest?.is_built_in||this._manifest?.documentation?s.qy`<a href="${this._manifest.is_built_in?(0,v.o)(this.hass,`/integrations/${this._domain}`):this._manifest.documentation}" target="_blank" rel="noreferrer"> ${this.hass.localize("ui.panel.config.application_credentials.editor.missing_credentials_domain_link",{integration:t})} <ha-svg-icon .path="${_}"></ha-svg-icon> </a>`:s.s6} </p>`:s.s6} ${this._params.selectedDomain&&this._description?s.s6:s.qy`<p> ${this.hass.localize("ui.panel.config.application_credentials.editor.description")} <a href="${(0,v.o)(this.hass,"/integrations/application_credentials")}" target="_blank" rel="noreferrer"> ${this.hass.localize("ui.panel.config.application_credentials.editor.view_documentation")} <ha-svg-icon .path="${_}"></ha-svg-icon> </a> </p>`} ${this._params.selectedDomain?s.s6:s.qy`<ha-generic-picker name="domain" .hass="${this.hass}" .label="${this.hass.localize("ui.panel.config.application_credentials.editor.domain")}" .value="${this._domain}" .invalid="${this._invalid&&!this._domain}" .getItems="${this._getDomainItems}" required .disabled="${!this._domains}" .valueRenderer="${this._domainRenderer}" @value-changed="${this._handleDomainPicked}" .errorMessage="${this.hass.localize("ui.common.error_required")}"></ha-generic-picker>`} ${this._description?s.qy`<ha-markdown breaks .content="${this._description}"></ha-markdown>`:s.s6} <ha-textfield class="name" name="name" .label="${this.hass.localize("ui.panel.config.application_credentials.editor.name")}" .value="${this._name}" .invalid="${this._invalid&&!this._name}" required @input="${this._handleValueChanged}" .errorMessage="${this.hass.localize("ui.common.error_required")}" dialogInitialFocus></ha-textfield> <ha-textfield class="clientId" name="clientId" .label="${this.hass.localize("ui.panel.config.application_credentials.editor.client_id")}" .value="${this._clientId}" .invalid="${this._invalid&&!this._clientId}" required @input="${this._handleValueChanged}" .errorMessage="${this.hass.localize("ui.common.error_required")}" dialogInitialFocus .helper="${this.hass.localize("ui.panel.config.application_credentials.editor.client_id_helper")}" helperPersistent></ha-textfield> <ha-password-field .label="${this.hass.localize("ui.panel.config.application_credentials.editor.client_secret")}" name="clientSecret" .value="${this._clientSecret}" .invalid="${this._invalid&&!this._clientSecret}" required @input="${this._handleValueChanged}" .errorMessage="${this.hass.localize("ui.common.error_required")}" .helper="${this.hass.localize("ui.panel.config.application_credentials.editor.client_secret_helper")}" helperPersistent></ha-password-field> </div> <ha-dialog-footer slot="footer"> <ha-button appearance="plain" slot="secondaryAction" @click="${this._closeDialog}" .disabled="${this._loading}"> ${this.hass.localize("ui.common.cancel")} </ha-button> <ha-button slot="primaryAction" @click="${this._addApplicationCredential}" .loading="${this._loading}"> ${this.hass.localize("ui.panel.config.application_credentials.editor.add")} </ha-button> </ha-dialog-footer>`:s.qy`<ha-fade-in .delay="${500}"> <ha-spinner size="large"></ha-spinner> </ha-fade-in>`} </ha-wa-dialog> `}_closeDialog(){this._open=!1}closeDialog(){this._params=void 0,this._domains=void 0,(0,n.r)(this,"dialog-closed",{dialog:this.localName})}_handleDomainPicked(t){t.stopPropagation(),this._domain=t.detail.value,this._updateDescription()}async _updateDescription(){if(!this._domain)return;await this.hass.loadBackendTranslation("application_credentials",this._domain);const t=this._config.integrations[this._domain];this._description=this.hass.localize(`component.${this._domain}.application_credentials.description`,t.description_placeholders)}_handleValueChanged(t){this._error=void 0;const e=t.target.name,i=t.target.value;this[`_${e}`]=i}_abortDialog(){this._params&&this._params.dialogAbortedCallback&&this._params.dialogAbortedCallback(),this.closeDialog()}async _addApplicationCredential(t){if(t.preventDefault(),!(this._domain&&this._name&&this._clientId&&this._clientSecret))return void(this._invalid=!0);let e;this._invalid=!1,this._loading=!0,this._error="";try{e=await(0,c.MV)(this.hass,this._domain,this._clientId,this._clientSecret,this._name)}catch(t){return this._loading=!1,void(this._error=t.message)}this._params.applicationCredentialAddedCallback(e),this.closeDialog()}static get styles(){return[u.nA,s.AH`ha-dialog{--mdc-dialog-max-width:500px;--dialog-z-index:10}.row{display:flex;padding:var(--ha-space-2) 0}ha-textfield{display:block;margin-top:var(--ha-space-4);margin-bottom:var(--ha-space-4)}a{text-decoration:none}a ha-svg-icon{--mdc-icon-size:16px}ha-markdown{margin-top:var(--ha-space-4);margin-bottom:var(--ha-space-4)}ha-fade-in{display:flex;width:100%;justify-content:center}`]}constructor(...t){super(...t),this._loading=!1,this._open=!1,this._invalid=!1,this._getDomainItems=()=>this._domains?.map(t=>({id:t.id,primary:t.name,sorting_label:t.name}))??[],this._domainRenderer=t=>{const e=this._domains?.find(e=>e.id===t);return s.qy`<span slot="headline">${e?e.name:t}</span>`}}}(0,o.Cg)([(0,r.MZ)({attribute:!1})],y.prototype,"hass",void 0),(0,o.Cg)([(0,r.wk)()],y.prototype,"_loading",void 0),(0,o.Cg)([(0,r.wk)()],y.prototype,"_error",void 0),(0,o.Cg)([(0,r.wk)()],y.prototype,"_params",void 0),(0,o.Cg)([(0,r.wk)()],y.prototype,"_domain",void 0),(0,o.Cg)([(0,r.wk)()],y.prototype,"_manifest",void 0),(0,o.Cg)([(0,r.wk)()],y.prototype,"_name",void 0),(0,o.Cg)([(0,r.wk)()],y.prototype,"_description",void 0),(0,o.Cg)([(0,r.wk)()],y.prototype,"_clientId",void 0),(0,o.Cg)([(0,r.wk)()],y.prototype,"_clientSecret",void 0),(0,o.Cg)([(0,r.wk)()],y.prototype,"_domains",void 0),(0,o.Cg)([(0,r.wk)()],y.prototype,"_config",void 0),(0,o.Cg)([(0,r.wk)()],y.prototype,"_open",void 0),(0,o.Cg)([(0,r.wk)()],y.prototype,"_invalid",void 0),y=(0,o.Cg)([(0,r.EM)("dialog-add-application-credential")],y),a()}catch(t){a(t)}})}};
//# sourceMappingURL=5708.7599598933f2f5ac.js.map