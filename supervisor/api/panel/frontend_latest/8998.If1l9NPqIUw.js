/*! For license information please see 8998.If1l9NPqIUw.js.LICENSE.txt */
export const id=8998;export const ids=[8998];export const modules={37136:(e,t,i)=>{i.d(t,{M:()=>p});var a=i(79192),r=i(11468),o={ROOT:"mdc-form-field"},n={LABEL_SELECTOR:".mdc-form-field > label"};const l=function(e){function t(i){var r=e.call(this,(0,a.__assign)((0,a.__assign)({},t.defaultAdapter),i))||this;return r.click=function(){r.handleClick()},r}return(0,a.__extends)(t,e),Object.defineProperty(t,"cssClasses",{get:function(){return o},enumerable:!1,configurable:!0}),Object.defineProperty(t,"strings",{get:function(){return n},enumerable:!1,configurable:!0}),Object.defineProperty(t,"defaultAdapter",{get:function(){return{activateInputRipple:function(){},deactivateInputRipple:function(){},deregisterInteractionHandler:function(){},registerInteractionHandler:function(){}}},enumerable:!1,configurable:!0}),t.prototype.init=function(){this.adapter.registerInteractionHandler("click",this.click)},t.prototype.destroy=function(){this.adapter.deregisterInteractionHandler("click",this.click)},t.prototype.handleClick=function(){var e=this;this.adapter.activateInputRipple(),requestAnimationFrame((function(){e.adapter.deactivateInputRipple()}))},t}(r.I);var d=i(19637),s=i(90410),c=i(54279),h=i(50289),f=i(29818),m=i(85323);class p extends d.O{constructor(){super(...arguments),this.alignEnd=!1,this.spaceBetween=!1,this.nowrap=!1,this.label="",this.mdcFoundationClass=l}createAdapter(){return{registerInteractionHandler:(e,t)=>{this.labelEl.addEventListener(e,t)},deregisterInteractionHandler:(e,t)=>{this.labelEl.removeEventListener(e,t)},activateInputRipple:async()=>{const e=this.input;if(e instanceof s.ZS){const t=await e.ripple;t&&t.startPress()}},deactivateInputRipple:async()=>{const e=this.input;if(e instanceof s.ZS){const t=await e.ripple;t&&t.endPress()}}}}get input(){var e,t;return null!==(t=null===(e=this.slottedInputs)||void 0===e?void 0:e[0])&&void 0!==t?t:null}render(){const e={"mdc-form-field--align-end":this.alignEnd,"mdc-form-field--space-between":this.spaceBetween,"mdc-form-field--nowrap":this.nowrap};return h.qy` <div class="mdc-form-field ${(0,m.H)(e)}"> <slot></slot> <label class="mdc-label" @click="${this._labelClick}">${this.label}</label> </div>`}click(){this._labelClick()}_labelClick(){const e=this.input;e&&(e.focus(),e.click())}}(0,a.__decorate)([(0,f.MZ)({type:Boolean})],p.prototype,"alignEnd",void 0),(0,a.__decorate)([(0,f.MZ)({type:Boolean})],p.prototype,"spaceBetween",void 0),(0,a.__decorate)([(0,f.MZ)({type:Boolean})],p.prototype,"nowrap",void 0),(0,a.__decorate)([(0,f.MZ)({type:String}),(0,c.P)((async function(e){var t;null===(t=this.input)||void 0===t||t.setAttribute("aria-label",e)}))],p.prototype,"label",void 0),(0,a.__decorate)([(0,f.P)(".mdc-form-field")],p.prototype,"mdcRoot",void 0),(0,a.__decorate)([(0,f.gZ)("",!0,"*")],p.prototype,"slottedInputs",void 0),(0,a.__decorate)([(0,f.P)("label")],p.prototype,"labelEl",void 0)},18881:(e,t,i)=>{i.d(t,{R:()=>a});const a=i(50289).AH`.mdc-form-field{-moz-osx-font-smoothing:grayscale;-webkit-font-smoothing:antialiased;font-family:Roboto,sans-serif;font-family:var(--mdc-typography-body2-font-family, var(--mdc-typography-font-family, Roboto, sans-serif));font-size:.875rem;font-size:var(--mdc-typography-body2-font-size, .875rem);line-height:1.25rem;line-height:var(--mdc-typography-body2-line-height, 1.25rem);font-weight:400;font-weight:var(--mdc-typography-body2-font-weight,400);letter-spacing:.0178571429em;letter-spacing:var(--mdc-typography-body2-letter-spacing, .0178571429em);text-decoration:inherit;text-decoration:var(--mdc-typography-body2-text-decoration,inherit);text-transform:inherit;text-transform:var(--mdc-typography-body2-text-transform,inherit);color:rgba(0,0,0,.87);color:var(--mdc-theme-text-primary-on-background,rgba(0,0,0,.87));display:inline-flex;align-items:center;vertical-align:middle}.mdc-form-field>label{margin-left:0;margin-right:auto;padding-left:4px;padding-right:0;order:0}.mdc-form-field>label[dir=rtl],[dir=rtl] .mdc-form-field>label{margin-left:auto;margin-right:0}.mdc-form-field>label[dir=rtl],[dir=rtl] .mdc-form-field>label{padding-left:0;padding-right:4px}.mdc-form-field--nowrap>label{text-overflow:ellipsis;overflow:hidden;white-space:nowrap}.mdc-form-field--align-end>label{margin-left:auto;margin-right:0;padding-left:0;padding-right:4px;order:-1}.mdc-form-field--align-end>label[dir=rtl],[dir=rtl] .mdc-form-field--align-end>label{margin-left:0;margin-right:auto}.mdc-form-field--align-end>label[dir=rtl],[dir=rtl] .mdc-form-field--align-end>label{padding-left:4px;padding-right:0}.mdc-form-field--space-between{justify-content:space-between}.mdc-form-field--space-between>label{margin:0}.mdc-form-field--space-between>label[dir=rtl],[dir=rtl] .mdc-form-field--space-between>label{margin:0}:host{display:inline-flex}.mdc-form-field{width:100%}::slotted(*){-moz-osx-font-smoothing:grayscale;-webkit-font-smoothing:antialiased;font-family:Roboto,sans-serif;font-family:var(--mdc-typography-body2-font-family, var(--mdc-typography-font-family, Roboto, sans-serif));font-size:.875rem;font-size:var(--mdc-typography-body2-font-size, .875rem);line-height:1.25rem;line-height:var(--mdc-typography-body2-line-height, 1.25rem);font-weight:400;font-weight:var(--mdc-typography-body2-font-weight,400);letter-spacing:.0178571429em;letter-spacing:var(--mdc-typography-body2-letter-spacing, .0178571429em);text-decoration:inherit;text-decoration:var(--mdc-typography-body2-text-decoration,inherit);text-transform:inherit;text-transform:var(--mdc-typography-body2-text-transform,inherit);color:rgba(0,0,0,.87);color:var(--mdc-theme-text-primary-on-background,rgba(0,0,0,.87))}::slotted(mwc-switch){margin-right:10px}::slotted(mwc-switch[dir=rtl]),[dir=rtl] ::slotted(mwc-switch){margin-left:10px}`},88725:(e,t,i)=>{var a=i(36312),r=i(41204),o=i(15565),n=i(50289),l=i(29818);(0,a.A)([(0,l.EM)("ha-checkbox")],(function(e,t){return{F:class extends t{constructor(...t){super(...t),e(this)}},d:[{kind:"field",static:!0,key:"styles",value:()=>[o.R,n.AH`:host{--mdc-theme-secondary:var(--primary-color)}`]}]}}),r.L)},24284:(e,t,i)=>{var a=i(36312),r=i(37136),o=i(18881),n=i(50289),l=i(29818),d=i(85323),s=i(34897);(0,a.A)([(0,l.EM)("ha-formfield")],(function(e,t){return{F:class extends t{constructor(...t){super(...t),e(this)}},d:[{kind:"field",decorators:[(0,l.MZ)({type:Boolean,reflect:!0})],key:"disabled",value:()=>!1},{kind:"method",key:"render",value:function(){const e={"mdc-form-field--align-end":this.alignEnd,"mdc-form-field--space-between":this.spaceBetween,"mdc-form-field--nowrap":this.nowrap};return n.qy` <div class="mdc-form-field ${(0,d.H)(e)}"> <slot></slot> <label class="mdc-label" @click="${this._labelClick}"> <slot name="label">${this.label}</slot> </label> </div>`}},{kind:"method",key:"_labelClick",value:function(){const e=this.input;if(e&&(e.focus(),!e.disabled))switch(e.tagName){case"HA-CHECKBOX":e.checked=!e.checked,(0,s.r)(e,"change");break;case"HA-RADIO":e.checked=!0,(0,s.r)(e,"change");break;default:e.click()}}},{kind:"field",static:!0,key:"styles",value:()=>[o.R,n.AH`:host(:not([alignEnd])) ::slotted(ha-switch){margin-right:10px;margin-inline-end:10px;margin-inline-start:inline}.mdc-form-field{align-items:var(--ha-formfield-align-items,center);gap:4px}.mdc-form-field>label{direction:var(--direction);margin-inline-start:0;margin-inline-end:auto;padding:0}:host([disabled]) label{color:var(--disabled-text-color)}`]}]}}),r.M)},48998:(e,t,i)=>{i.r(t);var a=i(36312),r=i(50289),o=i(29818),n=i(34897),l=(i(88725),i(24284),i(90431),i(55321));(0,a.A)([(0,o.EM)("ha-timer-form")],(function(e,t){return{F:class extends t{constructor(...t){super(...t),e(this)}},d:[{kind:"field",decorators:[(0,o.MZ)({attribute:!1})],key:"hass",value:void 0},{kind:"field",decorators:[(0,o.MZ)({type:Boolean})],key:"new",value:()=>!1},{kind:"field",key:"_item",value:void 0},{kind:"field",decorators:[(0,o.wk)()],key:"_name",value:void 0},{kind:"field",decorators:[(0,o.wk)()],key:"_icon",value:void 0},{kind:"field",decorators:[(0,o.wk)()],key:"_duration",value:void 0},{kind:"field",decorators:[(0,o.wk)()],key:"_restore",value:void 0},{kind:"set",key:"item",value:function(e){this._item=e,e?(this._name=e.name||"",this._icon=e.icon||"",this._duration=e.duration||"00:00:00",this._restore=e.restore||!1):(this._name="",this._icon="",this._duration="00:00:00",this._restore=!1)}},{kind:"method",key:"focus",value:function(){this.updateComplete.then((()=>this.shadowRoot?.querySelector("[dialogInitialFocus]")?.focus()))}},{kind:"method",key:"render",value:function(){return this.hass?r.qy` <div class="form"> <ha-textfield .value="${this._name}" .configValue="${"name"}" @input="${this._valueChanged}" .label="${this.hass.localize("ui.dialogs.helper_settings.generic.name")}" autoValidate required .validationMessage="${this.hass.localize("ui.dialogs.helper_settings.required_error_msg")}" dialogInitialFocus></ha-textfield> <ha-icon-picker .hass="${this.hass}" .value="${this._icon}" .configValue="${"icon"}" @value-changed="${this._valueChanged}" .label="${this.hass.localize("ui.dialogs.helper_settings.generic.icon")}"></ha-icon-picker> <ha-textfield .configValue="${"duration"}" .value="${this._duration}" @input="${this._valueChanged}" .label="${this.hass.localize("ui.dialogs.helper_settings.timer.duration")}"></ha-textfield> <ha-formfield .label="${this.hass.localize("ui.dialogs.helper_settings.timer.restore")}"> <ha-checkbox .configValue="${"restore"}" .checked="${this._restore}" @click="${this._toggleRestore}"> </ha-checkbox> </ha-formfield> </div> `:r.s6}},{kind:"method",key:"_valueChanged",value:function(e){if(!this.new&&!this._item)return;e.stopPropagation();const t=e.target.configValue,i=e.detail?.value||e.target.value;if(this[`_${t}`]===i)return;const a={...this._item};i?a[t]=i:delete a[t],(0,n.r)(this,"value-changed",{value:a})}},{kind:"method",key:"_toggleRestore",value:function(){this._restore=!this._restore,(0,n.r)(this,"value-changed",{value:{...this._item,restore:this._restore}})}},{kind:"get",static:!0,key:"styles",value:function(){return[l.RF,r.AH`.form{color:var(--primary-text-color)}ha-textfield{display:block;margin:8px 0}`]}}]}}),r.WF)}};
//# sourceMappingURL=8998.If1l9NPqIUw.js.map