/*! For license information please see 4320.9df694794635e854.js.LICENSE.txt */
"use strict";(self.webpackChunkhome_assistant_frontend=self.webpackChunkhome_assistant_frontend||[]).push([["4320"],{4918:function(t,e,i){i.d(e,{a:()=>b});i(71695),i(40251),i(47021);var r=i(9065),o=i(80573),n={ROOT:"mdc-form-field"},a={LABEL_SELECTOR:".mdc-form-field > label"};const c=function(t){function e(i){var o=t.call(this,(0,r.__assign)((0,r.__assign)({},e.defaultAdapter),i))||this;return o.click=function(){o.handleClick()},o}return(0,r.__extends)(e,t),Object.defineProperty(e,"cssClasses",{get:function(){return n},enumerable:!1,configurable:!0}),Object.defineProperty(e,"strings",{get:function(){return a},enumerable:!1,configurable:!0}),Object.defineProperty(e,"defaultAdapter",{get:function(){return{activateInputRipple:function(){},deactivateInputRipple:function(){},deregisterInteractionHandler:function(){},registerInteractionHandler:function(){}}},enumerable:!1,configurable:!0}),e.prototype.init=function(){this.adapter.registerInteractionHandler("click",this.click)},e.prototype.destroy=function(){this.adapter.deregisterInteractionHandler("click",this.click)},e.prototype.handleClick=function(){var t=this;this.adapter.activateInputRipple(),requestAnimationFrame((function(){t.adapter.deactivateInputRipple()}))},e}(o.K);var d=i(11911),s=i(88618),l=i(78611),h=i(57243),p=i(50778),m=i(35359);let u,f=t=>t;class b extends d.H{constructor(){super(...arguments),this.alignEnd=!1,this.spaceBetween=!1,this.nowrap=!1,this.label="",this.mdcFoundationClass=c}createAdapter(){return{registerInteractionHandler:(t,e)=>{this.labelEl.addEventListener(t,e)},deregisterInteractionHandler:(t,e)=>{this.labelEl.removeEventListener(t,e)},activateInputRipple:async()=>{const t=this.input;if(t instanceof s.Wg){const e=await t.ripple;e&&e.startPress()}},deactivateInputRipple:async()=>{const t=this.input;if(t instanceof s.Wg){const e=await t.ripple;e&&e.endPress()}}}}get input(){var t,e;return null!==(e=null===(t=this.slottedInputs)||void 0===t?void 0:t[0])&&void 0!==e?e:null}render(){const t={"mdc-form-field--align-end":this.alignEnd,"mdc-form-field--space-between":this.spaceBetween,"mdc-form-field--nowrap":this.nowrap};return(0,h.dy)(u||(u=f` <div class="mdc-form-field ${0}"> <slot></slot> <label class="mdc-label" @click="${0}">${0}</label> </div>`),(0,m.$)(t),this._labelClick,this.label)}click(){this._labelClick()}_labelClick(){const t=this.input;t&&(t.focus(),t.click())}}(0,r.__decorate)([(0,p.Cb)({type:Boolean})],b.prototype,"alignEnd",void 0),(0,r.__decorate)([(0,p.Cb)({type:Boolean})],b.prototype,"spaceBetween",void 0),(0,r.__decorate)([(0,p.Cb)({type:Boolean})],b.prototype,"nowrap",void 0),(0,r.__decorate)([(0,p.Cb)({type:String}),(0,l.P)((async function(t){var e;null===(e=this.input)||void 0===e||e.setAttribute("aria-label",t)}))],b.prototype,"label",void 0),(0,r.__decorate)([(0,p.IO)(".mdc-form-field")],b.prototype,"mdcRoot",void 0),(0,r.__decorate)([(0,p.vZ)("",!0,"*")],b.prototype,"slottedInputs",void 0),(0,r.__decorate)([(0,p.IO)("label")],b.prototype,"labelEl",void 0)},6394:function(t,e,i){i.d(e,{W:()=>o});let r;const o=(0,i(57243).iv)(r||(r=(t=>t)`.mdc-form-field{-moz-osx-font-smoothing:grayscale;-webkit-font-smoothing:antialiased;font-family:Roboto,sans-serif;font-family:var(--mdc-typography-body2-font-family, var(--mdc-typography-font-family, Roboto, sans-serif));font-size:.875rem;font-size:var(--mdc-typography-body2-font-size, .875rem);line-height:1.25rem;line-height:var(--mdc-typography-body2-line-height, 1.25rem);font-weight:400;font-weight:var(--mdc-typography-body2-font-weight,400);letter-spacing:.0178571429em;letter-spacing:var(--mdc-typography-body2-letter-spacing, .0178571429em);text-decoration:inherit;text-decoration:var(--mdc-typography-body2-text-decoration,inherit);text-transform:inherit;text-transform:var(--mdc-typography-body2-text-transform,inherit);color:rgba(0,0,0,.87);color:var(--mdc-theme-text-primary-on-background,rgba(0,0,0,.87));display:inline-flex;align-items:center;vertical-align:middle}.mdc-form-field>label{margin-left:0;margin-right:auto;padding-left:4px;padding-right:0;order:0}.mdc-form-field>label[dir=rtl],[dir=rtl] .mdc-form-field>label{margin-left:auto;margin-right:0}.mdc-form-field>label[dir=rtl],[dir=rtl] .mdc-form-field>label{padding-left:0;padding-right:4px}.mdc-form-field--nowrap>label{text-overflow:ellipsis;overflow:hidden;white-space:nowrap}.mdc-form-field--align-end>label{margin-left:auto;margin-right:0;padding-left:0;padding-right:4px;order:-1}.mdc-form-field--align-end>label[dir=rtl],[dir=rtl] .mdc-form-field--align-end>label{margin-left:0;margin-right:auto}.mdc-form-field--align-end>label[dir=rtl],[dir=rtl] .mdc-form-field--align-end>label{padding-left:4px;padding-right:0}.mdc-form-field--space-between{justify-content:space-between}.mdc-form-field--space-between>label{margin:0}.mdc-form-field--space-between>label[dir=rtl],[dir=rtl] .mdc-form-field--space-between>label{margin:0}:host{display:inline-flex}.mdc-form-field{width:100%}::slotted(*){-moz-osx-font-smoothing:grayscale;-webkit-font-smoothing:antialiased;font-family:Roboto,sans-serif;font-family:var(--mdc-typography-body2-font-family, var(--mdc-typography-font-family, Roboto, sans-serif));font-size:.875rem;font-size:var(--mdc-typography-body2-font-size, .875rem);line-height:1.25rem;line-height:var(--mdc-typography-body2-line-height, 1.25rem);font-weight:400;font-weight:var(--mdc-typography-body2-font-weight,400);letter-spacing:.0178571429em;letter-spacing:var(--mdc-typography-body2-letter-spacing, .0178571429em);text-decoration:inherit;text-decoration:var(--mdc-typography-body2-text-decoration,inherit);text-transform:inherit;text-transform:var(--mdc-typography-body2-text-transform,inherit);color:rgba(0,0,0,.87);color:var(--mdc-theme-text-primary-on-background,rgba(0,0,0,.87))}::slotted(mwc-switch){margin-right:10px}::slotted(mwc-switch[dir=rtl]),[dir=rtl] ::slotted(mwc-switch){margin-left:10px}`))},62523:function(t,e,i){i.d(e,{H:()=>_});i(71695),i(19423),i(47021);var r=i(9065),o=(i(16060),i(4428)),n=i(11911),a=i(78611),c=i(91532),d=i(80573),s={CHECKED:"mdc-switch--checked",DISABLED:"mdc-switch--disabled"},l={ARIA_CHECKED_ATTR:"aria-checked",NATIVE_CONTROL_SELECTOR:".mdc-switch__native-control",RIPPLE_SURFACE_SELECTOR:".mdc-switch__thumb-underlay"};const h=function(t){function e(i){return t.call(this,(0,r.__assign)((0,r.__assign)({},e.defaultAdapter),i))||this}return(0,r.__extends)(e,t),Object.defineProperty(e,"strings",{get:function(){return l},enumerable:!1,configurable:!0}),Object.defineProperty(e,"cssClasses",{get:function(){return s},enumerable:!1,configurable:!0}),Object.defineProperty(e,"defaultAdapter",{get:function(){return{addClass:function(){},removeClass:function(){},setNativeControlChecked:function(){},setNativeControlDisabled:function(){},setNativeControlAttr:function(){}}},enumerable:!1,configurable:!0}),e.prototype.setChecked=function(t){this.adapter.setNativeControlChecked(t),this.updateAriaChecked(t),this.updateCheckedStyling(t)},e.prototype.setDisabled=function(t){this.adapter.setNativeControlDisabled(t),t?this.adapter.addClass(s.DISABLED):this.adapter.removeClass(s.DISABLED)},e.prototype.handleChange=function(t){var e=t.target;this.updateAriaChecked(e.checked),this.updateCheckedStyling(e.checked)},e.prototype.updateCheckedStyling=function(t){t?this.adapter.addClass(s.CHECKED):this.adapter.removeClass(s.CHECKED)},e.prototype.updateAriaChecked=function(t){this.adapter.setNativeControlAttr(l.ARIA_CHECKED_ATTR,""+!!t)},e}(d.K);var p=i(57243),m=i(50778),u=i(20552);let f,b,g=t=>t;class _ extends n.H{constructor(){super(...arguments),this.checked=!1,this.disabled=!1,this.shouldRenderRipple=!1,this.mdcFoundationClass=h,this.rippleHandlers=new c.A((()=>(this.shouldRenderRipple=!0,this.ripple)))}changeHandler(t){this.mdcFoundation.handleChange(t),this.checked=this.formElement.checked}createAdapter(){return Object.assign(Object.assign({},(0,n.q)(this.mdcRoot)),{setNativeControlChecked:t=>{this.formElement.checked=t},setNativeControlDisabled:t=>{this.formElement.disabled=t},setNativeControlAttr:(t,e)=>{this.formElement.setAttribute(t,e)}})}renderRipple(){return this.shouldRenderRipple?(0,p.dy)(f||(f=g` <mwc-ripple .accent="${0}" .disabled="${0}" unbounded> </mwc-ripple>`),this.checked,this.disabled):""}focus(){const t=this.formElement;t&&(this.rippleHandlers.startFocus(),t.focus())}blur(){const t=this.formElement;t&&(this.rippleHandlers.endFocus(),t.blur())}click(){this.formElement&&!this.disabled&&(this.formElement.focus(),this.formElement.click())}firstUpdated(){super.firstUpdated(),this.shadowRoot&&this.mdcRoot.addEventListener("change",(t=>{this.dispatchEvent(new Event("change",t))}))}render(){return(0,p.dy)(b||(b=g` <div class="mdc-switch"> <div class="mdc-switch__track"></div> <div class="mdc-switch__thumb-underlay"> ${0} <div class="mdc-switch__thumb"> <input type="checkbox" id="basic-switch" class="mdc-switch__native-control" role="switch" aria-label="${0}" aria-labelledby="${0}" @change="${0}" @focus="${0}" @blur="${0}" @mousedown="${0}" @mouseenter="${0}" @mouseleave="${0}" @touchstart="${0}" @touchend="${0}" @touchcancel="${0}"> </div> </div> </div>`),this.renderRipple(),(0,u.o)(this.ariaLabel),(0,u.o)(this.ariaLabelledBy),this.changeHandler,this.handleRippleFocus,this.handleRippleBlur,this.handleRippleMouseDown,this.handleRippleMouseEnter,this.handleRippleMouseLeave,this.handleRippleTouchStart,this.handleRippleDeactivate,this.handleRippleDeactivate)}handleRippleMouseDown(t){const e=()=>{window.removeEventListener("mouseup",e),this.handleRippleDeactivate()};window.addEventListener("mouseup",e),this.rippleHandlers.startPress(t)}handleRippleTouchStart(t){this.rippleHandlers.startPress(t)}handleRippleDeactivate(){this.rippleHandlers.endPress()}handleRippleMouseEnter(){this.rippleHandlers.startHover()}handleRippleMouseLeave(){this.rippleHandlers.endHover()}handleRippleFocus(){this.rippleHandlers.startFocus()}handleRippleBlur(){this.rippleHandlers.endFocus()}}(0,r.__decorate)([(0,m.Cb)({type:Boolean}),(0,a.P)((function(t){this.mdcFoundation.setChecked(t)}))],_.prototype,"checked",void 0),(0,r.__decorate)([(0,m.Cb)({type:Boolean}),(0,a.P)((function(t){this.mdcFoundation.setDisabled(t)}))],_.prototype,"disabled",void 0),(0,r.__decorate)([o.L,(0,m.Cb)({attribute:"aria-label"})],_.prototype,"ariaLabel",void 0),(0,r.__decorate)([o.L,(0,m.Cb)({attribute:"aria-labelledby"})],_.prototype,"ariaLabelledBy",void 0),(0,r.__decorate)([(0,m.IO)(".mdc-switch")],_.prototype,"mdcRoot",void 0),(0,r.__decorate)([(0,m.IO)("input")],_.prototype,"formElement",void 0),(0,r.__decorate)([(0,m.GC)("mwc-ripple")],_.prototype,"ripple",void 0),(0,r.__decorate)([(0,m.SB)()],_.prototype,"shouldRenderRipple",void 0),(0,r.__decorate)([(0,m.hO)({passive:!0})],_.prototype,"handleRippleMouseDown",null),(0,r.__decorate)([(0,m.hO)({passive:!0})],_.prototype,"handleRippleTouchStart",null)},83835:function(t,e,i){i.d(e,{W:()=>o});let r;const o=(0,i(57243).iv)(r||(r=(t=>t)`.mdc-switch__thumb-underlay{left:-14px;right:initial;top:-17px;width:48px;height:48px}.mdc-switch__thumb-underlay[dir=rtl],[dir=rtl] .mdc-switch__thumb-underlay{left:initial;right:-14px}.mdc-switch__native-control{width:64px;height:48px}.mdc-switch{display:inline-block;position:relative;outline:0;user-select:none}.mdc-switch.mdc-switch--checked .mdc-switch__track{background-color:#018786;background-color:var(--mdc-theme-secondary,#018786)}.mdc-switch.mdc-switch--checked .mdc-switch__thumb{background-color:#018786;background-color:var(--mdc-theme-secondary,#018786);border-color:#018786;border-color:var(--mdc-theme-secondary,#018786)}.mdc-switch:not(.mdc-switch--checked) .mdc-switch__track{background-color:#000;background-color:var(--mdc-theme-on-surface,#000)}.mdc-switch:not(.mdc-switch--checked) .mdc-switch__thumb{background-color:#fff;background-color:var(--mdc-theme-surface,#fff);border-color:#fff;border-color:var(--mdc-theme-surface,#fff)}.mdc-switch__native-control{left:0;right:initial;position:absolute;top:0;margin:0;opacity:0;cursor:pointer;pointer-events:auto;transition:transform 90ms cubic-bezier(.4, 0, .2, 1)}.mdc-switch__native-control[dir=rtl],[dir=rtl] .mdc-switch__native-control{left:initial;right:0}.mdc-switch__track{box-sizing:border-box;width:36px;height:14px;border:1px solid transparent;border-radius:7px;opacity:.38;transition:opacity 90ms cubic-bezier(.4, 0, .2, 1),background-color 90ms cubic-bezier(.4, 0, .2, 1),border-color 90ms cubic-bezier(.4, 0, .2, 1)}.mdc-switch__thumb-underlay{display:flex;position:absolute;align-items:center;justify-content:center;transform:translateX(0);transition:transform 90ms cubic-bezier(.4, 0, .2, 1),background-color 90ms cubic-bezier(.4, 0, .2, 1),border-color 90ms cubic-bezier(.4, 0, .2, 1)}.mdc-switch__thumb{box-shadow:0px 3px 1px -2px rgba(0,0,0,.2),0px 2px 2px 0px rgba(0,0,0,.14),0px 1px 5px 0px rgba(0,0,0,.12);box-sizing:border-box;width:20px;height:20px;border:10px solid;border-radius:50%;pointer-events:none;z-index:1}.mdc-switch--checked .mdc-switch__track{opacity:.54}.mdc-switch--checked .mdc-switch__thumb-underlay{transform:translateX(16px)}.mdc-switch--checked .mdc-switch__thumb-underlay[dir=rtl],[dir=rtl] .mdc-switch--checked .mdc-switch__thumb-underlay{transform:translateX(-16px)}.mdc-switch--checked .mdc-switch__native-control{transform:translateX(-16px)}.mdc-switch--checked .mdc-switch__native-control[dir=rtl],[dir=rtl] .mdc-switch--checked .mdc-switch__native-control{transform:translateX(16px)}.mdc-switch--disabled{opacity:.38;pointer-events:none}.mdc-switch--disabled .mdc-switch__thumb{border-width:1px}.mdc-switch--disabled .mdc-switch__native-control{cursor:default;pointer-events:none}:host{display:inline-flex;outline:0;-webkit-tap-highlight-color:transparent}`))},63434:function(t,e,i){var r=i(40810),o=i(12360),n=i(13053),a=i(88045),c=i(35709);r({target:"Array",proto:!0},{at:function(t){var e=o(this),i=n(e),r=a(t),c=r>=0?r:i+r;return c<0||c>=i?void 0:e[c]}}),c("at")},96829:function(t,e,i){var r=i(40810),o=i(72878),n=i(95011),a=i(88045),c=i(72616),d=i(29660),s=o("".charAt);r({target:"String",proto:!0,forced:d((function(){return"\ud842"!=="𠮷".at(-2)}))},{at:function(t){var e=c(n(this)),i=e.length,r=a(t),o=r>=0?r:i+r;return o<0||o>=i?void 0:s(e,o)}})},31050:function(t,e,i){i.d(e,{C:()=>p});i(71695),i(40251),i(39527),i(67670),i(47021);var r=i(2841),o=i(53232),n=i(1714);i(63721),i(88230),i(52247);class a{constructor(t){this.G=t}disconnect(){this.G=void 0}reconnect(t){this.G=t}deref(){return this.G}}class c{constructor(){this.Y=void 0,this.Z=void 0}get(){return this.Y}pause(){var t;null!==(t=this.Y)&&void 0!==t||(this.Y=new Promise((t=>this.Z=t)))}resume(){var t;null===(t=this.Z)||void 0===t||t.call(this),this.Y=this.Z=void 0}}var d=i(45779);const s=t=>!(0,o.pt)(t)&&"function"==typeof t.then,l=1073741823;class h extends n.sR{constructor(){super(...arguments),this._$C_t=l,this._$Cwt=[],this._$Cq=new a(this),this._$CK=new c}render(...t){var e;return null!==(e=t.find((t=>!s(t))))&&void 0!==e?e:r.Jb}update(t,e){const i=this._$Cwt;let o=i.length;this._$Cwt=e;const n=this._$Cq,a=this._$CK;this.isConnected||this.disconnected();for(let r=0;r<e.length&&!(r>this._$C_t);r++){const t=e[r];if(!s(t))return this._$C_t=r,t;r<o&&t===i[r]||(this._$C_t=l,o=0,Promise.resolve(t).then((async e=>{for(;a.get();)await a.get();const i=n.deref();if(void 0!==i){const r=i._$Cwt.indexOf(t);r>-1&&r<i._$C_t&&(i._$C_t=r,i.setValue(e))}})))}return r.Jb}disconnected(){this._$Cq.disconnect(),this._$CK.pause()}reconnected(){this._$Cq.reconnect(this),this._$CK.resume()}}const p=(0,d.XM)(h)}}]);
//# sourceMappingURL=4320.9df694794635e854.js.map