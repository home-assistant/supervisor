/*! For license information please see 9652.hCaLBPdfZAM.js.LICENSE.txt */
export const id=9652;export const ids=[9652];export const modules={37136:(e,t,i)=>{i.d(t,{M:()=>h});var r=i(79192),a=i(11468),o={ROOT:"mdc-form-field"},n={LABEL_SELECTOR:".mdc-form-field > label"};const l=function(e){function t(i){var a=e.call(this,(0,r.__assign)((0,r.__assign)({},t.defaultAdapter),i))||this;return a.click=function(){a.handleClick()},a}return(0,r.__extends)(t,e),Object.defineProperty(t,"cssClasses",{get:function(){return o},enumerable:!1,configurable:!0}),Object.defineProperty(t,"strings",{get:function(){return n},enumerable:!1,configurable:!0}),Object.defineProperty(t,"defaultAdapter",{get:function(){return{activateInputRipple:function(){},deactivateInputRipple:function(){},deregisterInteractionHandler:function(){},registerInteractionHandler:function(){}}},enumerable:!1,configurable:!0}),t.prototype.init=function(){this.adapter.registerInteractionHandler("click",this.click)},t.prototype.destroy=function(){this.adapter.deregisterInteractionHandler("click",this.click)},t.prototype.handleClick=function(){var e=this;this.adapter.activateInputRipple(),requestAnimationFrame((function(){e.adapter.deactivateInputRipple()}))},t}(a.I);var d=i(19637),c=i(90410),s=i(54279),p=i(50289),f=i(29818),m=i(85323);class h extends d.O{constructor(){super(...arguments),this.alignEnd=!1,this.spaceBetween=!1,this.nowrap=!1,this.label="",this.mdcFoundationClass=l}createAdapter(){return{registerInteractionHandler:(e,t)=>{this.labelEl.addEventListener(e,t)},deregisterInteractionHandler:(e,t)=>{this.labelEl.removeEventListener(e,t)},activateInputRipple:async()=>{const e=this.input;if(e instanceof c.ZS){const t=await e.ripple;t&&t.startPress()}},deactivateInputRipple:async()=>{const e=this.input;if(e instanceof c.ZS){const t=await e.ripple;t&&t.endPress()}}}}get input(){var e,t;return null!==(t=null===(e=this.slottedInputs)||void 0===e?void 0:e[0])&&void 0!==t?t:null}render(){const e={"mdc-form-field--align-end":this.alignEnd,"mdc-form-field--space-between":this.spaceBetween,"mdc-form-field--nowrap":this.nowrap};return p.qy` <div class="mdc-form-field ${(0,m.H)(e)}"> <slot></slot> <label class="mdc-label" @click="${this._labelClick}">${this.label}</label> </div>`}click(){this._labelClick()}_labelClick(){const e=this.input;e&&(e.focus(),e.click())}}(0,r.__decorate)([(0,f.MZ)({type:Boolean})],h.prototype,"alignEnd",void 0),(0,r.__decorate)([(0,f.MZ)({type:Boolean})],h.prototype,"spaceBetween",void 0),(0,r.__decorate)([(0,f.MZ)({type:Boolean})],h.prototype,"nowrap",void 0),(0,r.__decorate)([(0,f.MZ)({type:String}),(0,s.P)((async function(e){var t;null===(t=this.input)||void 0===t||t.setAttribute("aria-label",e)}))],h.prototype,"label",void 0),(0,r.__decorate)([(0,f.P)(".mdc-form-field")],h.prototype,"mdcRoot",void 0),(0,r.__decorate)([(0,f.gZ)("",!0,"*")],h.prototype,"slottedInputs",void 0),(0,r.__decorate)([(0,f.P)("label")],h.prototype,"labelEl",void 0)},18881:(e,t,i)=>{i.d(t,{R:()=>r});const r=i(50289).AH`.mdc-form-field{-moz-osx-font-smoothing:grayscale;-webkit-font-smoothing:antialiased;font-family:Roboto,sans-serif;font-family:var(--mdc-typography-body2-font-family, var(--mdc-typography-font-family, Roboto, sans-serif));font-size:.875rem;font-size:var(--mdc-typography-body2-font-size, .875rem);line-height:1.25rem;line-height:var(--mdc-typography-body2-line-height, 1.25rem);font-weight:400;font-weight:var(--mdc-typography-body2-font-weight,400);letter-spacing:.0178571429em;letter-spacing:var(--mdc-typography-body2-letter-spacing, .0178571429em);text-decoration:inherit;text-decoration:var(--mdc-typography-body2-text-decoration,inherit);text-transform:inherit;text-transform:var(--mdc-typography-body2-text-transform,inherit);color:rgba(0,0,0,.87);color:var(--mdc-theme-text-primary-on-background,rgba(0,0,0,.87));display:inline-flex;align-items:center;vertical-align:middle}.mdc-form-field>label{margin-left:0;margin-right:auto;padding-left:4px;padding-right:0;order:0}.mdc-form-field>label[dir=rtl],[dir=rtl] .mdc-form-field>label{margin-left:auto;margin-right:0}.mdc-form-field>label[dir=rtl],[dir=rtl] .mdc-form-field>label{padding-left:0;padding-right:4px}.mdc-form-field--nowrap>label{text-overflow:ellipsis;overflow:hidden;white-space:nowrap}.mdc-form-field--align-end>label{margin-left:auto;margin-right:0;padding-left:0;padding-right:4px;order:-1}.mdc-form-field--align-end>label[dir=rtl],[dir=rtl] .mdc-form-field--align-end>label{margin-left:0;margin-right:auto}.mdc-form-field--align-end>label[dir=rtl],[dir=rtl] .mdc-form-field--align-end>label{padding-left:4px;padding-right:0}.mdc-form-field--space-between{justify-content:space-between}.mdc-form-field--space-between>label{margin:0}.mdc-form-field--space-between>label[dir=rtl],[dir=rtl] .mdc-form-field--space-between>label{margin:0}:host{display:inline-flex}.mdc-form-field{width:100%}::slotted(*){-moz-osx-font-smoothing:grayscale;-webkit-font-smoothing:antialiased;font-family:Roboto,sans-serif;font-family:var(--mdc-typography-body2-font-family, var(--mdc-typography-font-family, Roboto, sans-serif));font-size:.875rem;font-size:var(--mdc-typography-body2-font-size, .875rem);line-height:1.25rem;line-height:var(--mdc-typography-body2-line-height, 1.25rem);font-weight:400;font-weight:var(--mdc-typography-body2-font-weight,400);letter-spacing:.0178571429em;letter-spacing:var(--mdc-typography-body2-letter-spacing, .0178571429em);text-decoration:inherit;text-decoration:var(--mdc-typography-body2-text-decoration,inherit);text-transform:inherit;text-transform:var(--mdc-typography-body2-text-transform,inherit);color:rgba(0,0,0,.87);color:var(--mdc-theme-text-primary-on-background,rgba(0,0,0,.87))}::slotted(mwc-switch){margin-right:10px}::slotted(mwc-switch[dir=rtl]),[dir=rtl] ::slotted(mwc-switch){margin-left:10px}`},88725:(e,t,i)=>{var r=i(36312),a=i(41204),o=i(15565),n=i(50289),l=i(29818);(0,r.A)([(0,l.EM)("ha-checkbox")],(function(e,t){return{F:class extends t{constructor(...t){super(...t),e(this)}},d:[{kind:"field",static:!0,key:"styles",value:()=>[o.R,n.AH`:host{--mdc-theme-secondary:var(--primary-color)}`]}]}}),a.L)},39652:(e,t,i)=>{i.r(t),i.d(t,{HaFormBoolean:()=>p});var r=i(36312),a=i(79192),o=i(29818),n=i(37136),l=i(18881);let d=class extends n.M{};d.styles=[l.R],d=(0,a.__decorate)([(0,o.EM)("mwc-formfield")],d);var c=i(50289),s=i(34897);i(88725);let p=(0,r.A)([(0,o.EM)("ha-form-boolean")],(function(e,t){return{F:class extends t{constructor(...t){super(...t),e(this)}},d:[{kind:"field",decorators:[(0,o.MZ)({attribute:!1})],key:"schema",value:void 0},{kind:"field",decorators:[(0,o.MZ)({attribute:!1})],key:"data",value:void 0},{kind:"field",decorators:[(0,o.MZ)()],key:"label",value:void 0},{kind:"field",decorators:[(0,o.MZ)()],key:"helper",value:void 0},{kind:"field",decorators:[(0,o.MZ)({type:Boolean})],key:"disabled",value:()=>!1},{kind:"field",decorators:[(0,o.P)("ha-checkbox",!0)],key:"_input",value:void 0},{kind:"method",key:"focus",value:function(){this._input&&this._input.focus()}},{kind:"method",key:"render",value:function(){return c.qy` <mwc-formfield .label="${this.label}"> <ha-checkbox .checked="${this.data}" .disabled="${this.disabled}" @change="${this._valueChanged}"></ha-checkbox> <span slot="label"> <p class="primary">${this.label}</p> ${this.helper?c.qy`<p class="secondary">${this.helper}</p>`:c.s6} </span> </mwc-formfield> `}},{kind:"method",key:"_valueChanged",value:function(e){(0,s.r)(this,"value-changed",{value:e.target.checked})}},{kind:"get",static:!0,key:"styles",value:function(){return c.AH`ha-formfield{display:flex;min-height:56px;align-items:center;--mdc-typography-body2-font-size:1em}p{margin:0}.secondary{direction:var(--direction);padding-top:4px;box-sizing:border-box;color:var(--secondary-text-color);font-size:.875rem;font-weight:var(--mdc-typography-body2-font-weight,400)}`}}]}}),c.WF)}};
//# sourceMappingURL=9652.hCaLBPdfZAM.js.map