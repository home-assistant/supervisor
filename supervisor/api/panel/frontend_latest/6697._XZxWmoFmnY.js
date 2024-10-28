/*! For license information please see 6697._XZxWmoFmnY.js.LICENSE.txt */
export const id=6697;export const ids=[6697];export const modules={93027:(e,a,t)=>{t.d(a,{z:()=>p});var r=t(79192),s=t(29818),o=(t(24969),t(50289)),i=t(40141);class n extends i.v{constructor(){super(...arguments),this.elevated=!1,this.href="",this.target=""}get primaryId(){return this.href?"link":"button"}get rippleDisabled(){return!this.href&&(this.disabled||this.softDisabled)}getContainerClasses(){return{...super.getContainerClasses(),disabled:!this.href&&(this.disabled||this.softDisabled),elevated:this.elevated,link:!!this.href}}renderPrimaryAction(e){const{ariaLabel:a}=this;return this.href?o.qy` <a class="primary action" id="link" aria-label="${a||o.s6}" href="${this.href}" target="${this.target||o.s6}">${e}</a> `:o.qy` <button class="primary action" id="button" aria-label="${a||o.s6}" aria-disabled="${this.softDisabled||o.s6}" ?disabled="${this.disabled&&!this.alwaysFocusable}" type="button">${e}</button> `}renderOutline(){return this.elevated?o.qy`<md-elevation part="elevation"></md-elevation>`:super.renderOutline()}}(0,r.__decorate)([(0,s.MZ)({type:Boolean})],n.prototype,"elevated",void 0),(0,r.__decorate)([(0,s.MZ)()],n.prototype,"href",void 0),(0,r.__decorate)([(0,s.MZ)()],n.prototype,"target",void 0);const l=o.AH`:host{--_container-height:var(--md-assist-chip-container-height, 32px);--_disabled-label-text-color:var(--md-assist-chip-disabled-label-text-color, var(--md-sys-color-on-surface, #1d1b20));--_disabled-label-text-opacity:var(--md-assist-chip-disabled-label-text-opacity, 0.38);--_elevated-container-color:var(--md-assist-chip-elevated-container-color, var(--md-sys-color-surface-container-low, #f7f2fa));--_elevated-container-elevation:var(--md-assist-chip-elevated-container-elevation, 1);--_elevated-container-shadow-color:var(--md-assist-chip-elevated-container-shadow-color, var(--md-sys-color-shadow, #000));--_elevated-disabled-container-color:var(--md-assist-chip-elevated-disabled-container-color, var(--md-sys-color-on-surface, #1d1b20));--_elevated-disabled-container-elevation:var(--md-assist-chip-elevated-disabled-container-elevation, 0);--_elevated-disabled-container-opacity:var(--md-assist-chip-elevated-disabled-container-opacity, 0.12);--_elevated-focus-container-elevation:var(--md-assist-chip-elevated-focus-container-elevation, 1);--_elevated-hover-container-elevation:var(--md-assist-chip-elevated-hover-container-elevation, 2);--_elevated-pressed-container-elevation:var(--md-assist-chip-elevated-pressed-container-elevation, 1);--_focus-label-text-color:var(--md-assist-chip-focus-label-text-color, var(--md-sys-color-on-surface, #1d1b20));--_hover-label-text-color:var(--md-assist-chip-hover-label-text-color, var(--md-sys-color-on-surface, #1d1b20));--_hover-state-layer-color:var(--md-assist-chip-hover-state-layer-color, var(--md-sys-color-on-surface, #1d1b20));--_hover-state-layer-opacity:var(--md-assist-chip-hover-state-layer-opacity, 0.08);--_label-text-color:var(--md-assist-chip-label-text-color, var(--md-sys-color-on-surface, #1d1b20));--_label-text-font:var(--md-assist-chip-label-text-font, var(--md-sys-typescale-label-large-font, var(--md-ref-typeface-plain, Roboto)));--_label-text-line-height:var(--md-assist-chip-label-text-line-height, var(--md-sys-typescale-label-large-line-height, 1.25rem));--_label-text-size:var(--md-assist-chip-label-text-size, var(--md-sys-typescale-label-large-size, 0.875rem));--_label-text-weight:var(--md-assist-chip-label-text-weight, var(--md-sys-typescale-label-large-weight, var(--md-ref-typeface-weight-medium, 500)));--_pressed-label-text-color:var(--md-assist-chip-pressed-label-text-color, var(--md-sys-color-on-surface, #1d1b20));--_pressed-state-layer-color:var(--md-assist-chip-pressed-state-layer-color, var(--md-sys-color-on-surface, #1d1b20));--_pressed-state-layer-opacity:var(--md-assist-chip-pressed-state-layer-opacity, 0.12);--_disabled-outline-color:var(--md-assist-chip-disabled-outline-color, var(--md-sys-color-on-surface, #1d1b20));--_disabled-outline-opacity:var(--md-assist-chip-disabled-outline-opacity, 0.12);--_focus-outline-color:var(--md-assist-chip-focus-outline-color, var(--md-sys-color-on-surface, #1d1b20));--_outline-color:var(--md-assist-chip-outline-color, var(--md-sys-color-outline, #79747e));--_outline-width:var(--md-assist-chip-outline-width, 1px);--_disabled-leading-icon-color:var(--md-assist-chip-disabled-leading-icon-color, var(--md-sys-color-on-surface, #1d1b20));--_disabled-leading-icon-opacity:var(--md-assist-chip-disabled-leading-icon-opacity, 0.38);--_focus-leading-icon-color:var(--md-assist-chip-focus-leading-icon-color, var(--md-sys-color-primary, #6750a4));--_hover-leading-icon-color:var(--md-assist-chip-hover-leading-icon-color, var(--md-sys-color-primary, #6750a4));--_leading-icon-color:var(--md-assist-chip-leading-icon-color, var(--md-sys-color-primary, #6750a4));--_icon-size:var(--md-assist-chip-icon-size, 18px);--_pressed-leading-icon-color:var(--md-assist-chip-pressed-leading-icon-color, var(--md-sys-color-primary, #6750a4));--_container-shape-start-start:var(--md-assist-chip-container-shape-start-start, var(--md-assist-chip-container-shape, var(--md-sys-shape-corner-small, 8px)));--_container-shape-start-end:var(--md-assist-chip-container-shape-start-end, var(--md-assist-chip-container-shape, var(--md-sys-shape-corner-small, 8px)));--_container-shape-end-end:var(--md-assist-chip-container-shape-end-end, var(--md-assist-chip-container-shape, var(--md-sys-shape-corner-small, 8px)));--_container-shape-end-start:var(--md-assist-chip-container-shape-end-start, var(--md-assist-chip-container-shape, var(--md-sys-shape-corner-small, 8px)));--_leading-space:var(--md-assist-chip-leading-space, 16px);--_trailing-space:var(--md-assist-chip-trailing-space, 16px);--_icon-label-space:var(--md-assist-chip-icon-label-space, 8px);--_with-leading-icon-leading-space:var(--md-assist-chip-with-leading-icon-leading-space, 8px)}@media(forced-colors:active){.link .outline{border-color:ActiveText}}`;var d=t(41908),c=t(89325);let p=class extends n{};p.styles=[c.R,d.R,l],p=(0,r.__decorate)([(0,s.EM)("md-assist-chip")],p)},40141:(e,a,t)=>{t.d(a,{v:()=>l});var r=t(79192),s=(t(39299),t(70252),t(50289)),o=t(29818),i=t(85323);const n=(0,t(26604).n)(s.WF);class l extends n{get rippleDisabled(){return this.disabled||this.softDisabled}constructor(){super(),this.disabled=!1,this.softDisabled=!1,this.alwaysFocusable=!1,this.label="",this.hasIcon=!1,s.S$||this.addEventListener("click",this.handleClick.bind(this))}focus(e){this.disabled&&!this.alwaysFocusable||super.focus(e)}render(){return s.qy` <div class="container ${(0,i.H)(this.getContainerClasses())}"> ${this.renderContainerContent()} </div> `}updated(e){e.has("disabled")&&void 0!==e.get("disabled")&&this.dispatchEvent(new Event("update-focus",{bubbles:!0}))}getContainerClasses(){return{disabled:this.disabled||this.softDisabled,"has-icon":this.hasIcon}}renderContainerContent(){return s.qy` ${this.renderOutline()} <md-focus-ring part="focus-ring" for="${this.primaryId}"></md-focus-ring> <md-ripple for="${this.primaryId}" ?disabled="${this.rippleDisabled}"></md-ripple> ${this.renderPrimaryAction(this.renderPrimaryContent())} `}renderOutline(){return s.qy`<span class="outline"></span>`}renderLeadingIcon(){return s.qy`<slot name="icon" @slotchange="${this.handleIconChange}"></slot>`}renderPrimaryContent(){return s.qy` <span class="leading icon" aria-hidden="true"> ${this.renderLeadingIcon()} </span> <span class="label"> <span class="label-text" id="label"> ${this.label?this.label:s.qy`<slot></slot>`} </span> </span> <span class="touch"></span> `}handleIconChange(e){const a=e.target;this.hasIcon=a.assignedElements({flatten:!0}).length>0}handleClick(e){if(this.softDisabled||this.disabled&&this.alwaysFocusable)return e.stopImmediatePropagation(),void e.preventDefault()}}l.shadowRootOptions={...s.WF.shadowRootOptions,delegatesFocus:!0},(0,r.__decorate)([(0,o.MZ)({type:Boolean,reflect:!0})],l.prototype,"disabled",void 0),(0,r.__decorate)([(0,o.MZ)({type:Boolean,attribute:"soft-disabled",reflect:!0})],l.prototype,"softDisabled",void 0),(0,r.__decorate)([(0,o.MZ)({type:Boolean,attribute:"always-focusable"})],l.prototype,"alwaysFocusable",void 0),(0,r.__decorate)([(0,o.MZ)()],l.prototype,"label",void 0),(0,r.__decorate)([(0,o.MZ)({type:Boolean,reflect:!0,attribute:"has-icon"})],l.prototype,"hasIcon",void 0)},41908:(e,a,t)=>{t.d(a,{R:()=>r});const r=t(50289).AH`.elevated{--md-elevation-level:var(--_elevated-container-elevation);--md-elevation-shadow-color:var(--_elevated-container-shadow-color)}.elevated::before{background:var(--_elevated-container-color)}.elevated:hover{--md-elevation-level:var(--_elevated-hover-container-elevation)}.elevated:focus-within{--md-elevation-level:var(--_elevated-focus-container-elevation)}.elevated:active{--md-elevation-level:var(--_elevated-pressed-container-elevation)}.elevated.disabled{--md-elevation-level:var(--_elevated-disabled-container-elevation)}.elevated.disabled::before{background:var(--_elevated-disabled-container-color);opacity:var(--_elevated-disabled-container-opacity)}@media(forced-colors:active){.elevated md-elevation{border:1px solid CanvasText}.elevated.disabled md-elevation{border-color:GrayText}}`},89325:(e,a,t)=>{t.d(a,{R:()=>r});const r=t(50289).AH`:host{border-start-start-radius:var(--_container-shape-start-start);border-start-end-radius:var(--_container-shape-start-end);border-end-start-radius:var(--_container-shape-end-start);border-end-end-radius:var(--_container-shape-end-end);display:inline-flex;height:var(--_container-height);cursor:pointer;-webkit-tap-highlight-color:transparent;--md-ripple-hover-color:var(--_hover-state-layer-color);--md-ripple-hover-opacity:var(--_hover-state-layer-opacity);--md-ripple-pressed-color:var(--_pressed-state-layer-color);--md-ripple-pressed-opacity:var(--_pressed-state-layer-opacity)}:host(:is([disabled],[soft-disabled])){pointer-events:none}:host([touch-target=wrapper]){margin:max(0px,(48px - var(--_container-height))/2) 0}md-focus-ring{--md-focus-ring-shape-start-start:var(--_container-shape-start-start);--md-focus-ring-shape-start-end:var(--_container-shape-start-end);--md-focus-ring-shape-end-end:var(--_container-shape-end-end);--md-focus-ring-shape-end-start:var(--_container-shape-end-start)}.container{border-radius:inherit;box-sizing:border-box;display:flex;height:100%;position:relative;width:100%}.container::before{border-radius:inherit;content:"";inset:0;pointer-events:none;position:absolute}.container:not(.disabled){cursor:pointer}.container.disabled{pointer-events:none}.cell{display:flex}.action{align-items:baseline;appearance:none;background:0 0;border:none;border-radius:inherit;display:flex;outline:0;padding:0;position:relative;text-decoration:none}.primary.action{min-width:0;padding-inline-start:var(--_leading-space);padding-inline-end:var(--_trailing-space)}.has-icon .primary.action{padding-inline-start:var(--_with-leading-icon-leading-space)}.touch{height:48px;inset:50% 0 0;position:absolute;transform:translateY(-50%);width:100%}:host([touch-target=none]) .touch{display:none}.outline{border:var(--_outline-width) solid var(--_outline-color);border-radius:inherit;inset:0;pointer-events:none;position:absolute}:where(:focus) .outline{border-color:var(--_focus-outline-color)}:where(.disabled) .outline{border-color:var(--_disabled-outline-color);opacity:var(--_disabled-outline-opacity)}md-ripple{border-radius:inherit}.icon,.label,.touch{z-index:1}.label{align-items:center;color:var(--_label-text-color);display:flex;font-family:var(--_label-text-font);font-size:var(--_label-text-size);font-weight:var(--_label-text-weight);height:100%;line-height:var(--_label-text-line-height);overflow:hidden;user-select:none}.label-text{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}:where(:hover) .label{color:var(--_hover-label-text-color)}:where(:focus) .label{color:var(--_focus-label-text-color)}:where(:active) .label{color:var(--_pressed-label-text-color)}:where(.disabled) .label{color:var(--_disabled-label-text-color);opacity:var(--_disabled-label-text-opacity)}.icon{align-self:center;display:flex;fill:currentColor;position:relative}.icon ::slotted(:first-child){font-size:var(--_icon-size);height:var(--_icon-size);width:var(--_icon-size)}.leading.icon{color:var(--_leading-icon-color)}.leading.icon ::slotted(*),.leading.icon svg{margin-inline-end:var(--_icon-label-space)}:where(:hover) .leading.icon{color:var(--_hover-leading-icon-color)}:where(:focus) .leading.icon{color:var(--_focus-leading-icon-color)}:where(:active) .leading.icon{color:var(--_pressed-leading-icon-color)}:where(.disabled) .leading.icon{color:var(--_disabled-leading-icon-color);opacity:var(--_disabled-leading-icon-opacity)}@media(forced-colors:active){:where(.disabled) :is(.label,.outline,.leading.icon){color:GrayText;opacity:1}}a,button{text-transform:inherit}a,button:not(:disabled,[aria-disabled=true]){cursor:inherit}`},24969:(e,a,t)=>{var r=t(79192),s=t(29818),o=t(50289);class i extends o.WF{connectedCallback(){super.connectedCallback(),this.setAttribute("aria-hidden","true")}render(){return o.qy`<span class="shadow"></span>`}}const n=o.AH`.shadow,.shadow::after,.shadow::before,:host{border-radius:inherit;inset:0;position:absolute;transition-duration:inherit;transition-property:inherit;transition-timing-function:inherit}:host{display:flex;pointer-events:none;transition-property:box-shadow,opacity}.shadow::after,.shadow::before{content:"";transition-property:box-shadow,opacity;--_level:var(--md-elevation-level, 0);--_shadow-color:var(--md-elevation-shadow-color, var(--md-sys-color-shadow, #000))}.shadow::before{box-shadow:0px calc(1px*(clamp(0,var(--_level),1) + clamp(0,var(--_level) - 3,1) + 2*clamp(0,var(--_level) - 4,1))) calc(1px*(2*clamp(0,var(--_level),1) + clamp(0,var(--_level) - 2,1) + clamp(0,var(--_level) - 4,1))) 0px var(--_shadow-color);opacity:.3}.shadow::after{box-shadow:0px calc(1px*(clamp(0,var(--_level),1) + clamp(0,var(--_level) - 1,1) + 2*clamp(0,var(--_level) - 2,3))) calc(1px*(3*clamp(0,var(--_level),2) + 2*clamp(0,var(--_level) - 2,3))) calc(1px*(clamp(0,var(--_level),4) + 2*clamp(0,var(--_level) - 4,1))) var(--_shadow-color);opacity:.15}`;let l=class extends i{};l.styles=[n],l=(0,r.__decorate)([(0,s.EM)("md-elevation")],l)},36575:(e,a,t)=>{t.d(a,{LV:()=>h});t(253),t(16891),t(37679);const r=Symbol("Comlink.proxy"),s=Symbol("Comlink.endpoint"),o=Symbol("Comlink.releaseProxy"),i=Symbol("Comlink.finalizer"),n=Symbol("Comlink.thrown"),l=e=>"object"==typeof e&&null!==e||"function"==typeof e,d=new Map([["proxy",{canHandle:e=>l(e)&&e[r],serialize(e){const{port1:a,port2:t}=new MessageChannel;return c(e,a),[t,[t]]},deserialize:e=>(e.start(),h(e))}],["throw",{canHandle:e=>l(e)&&n in e,serialize({value:e}){let a;return a=e instanceof Error?{isError:!0,value:{message:e.message,name:e.name,stack:e.stack}}:{isError:!1,value:e},[a,[]]},deserialize(e){if(e.isError)throw Object.assign(new Error(e.value.message),e.value);throw e.value}}]]);function c(e,a=globalThis,t=["*"]){a.addEventListener("message",(function s(o){if(!o||!o.data)return;if(!function(e,a){for(const t of e){if(a===t||"*"===t)return!0;if(t instanceof RegExp&&t.test(a))return!0}return!1}(t,o.origin))return void console.warn(`Invalid origin '${o.origin}' for comlink proxy`);const{id:l,type:d,path:h}=Object.assign({path:[]},o.data),v=(o.data.argumentList||[]).map(x);let b;try{const a=h.slice(0,-1).reduce(((e,a)=>e[a]),e),t=h.reduce(((e,a)=>e[a]),e);switch(d){case"GET":b=t;break;case"SET":a[h.slice(-1)[0]]=x(o.data.value),b=!0;break;case"APPLY":b=t.apply(a,v);break;case"CONSTRUCT":b=function(e){return Object.assign(e,{[r]:!0})}(new t(...v));break;case"ENDPOINT":{const{port1:a,port2:t}=new MessageChannel;c(e,t),b=function(e,a){return g.set(e,a),e}(a,[a])}break;case"RELEASE":b=void 0;break;default:return}}catch(e){b={value:e,[n]:0}}Promise.resolve(b).catch((e=>({value:e,[n]:0}))).then((t=>{const[r,o]=_(t);a.postMessage(Object.assign(Object.assign({},r),{id:l}),o),"RELEASE"===d&&(a.removeEventListener("message",s),p(a),i in e&&"function"==typeof e[i]&&e[i]())})).catch((e=>{const[t,r]=_({value:new TypeError("Unserializable return value"),[n]:0});a.postMessage(Object.assign(Object.assign({},t),{id:l}),r)}))})),a.start&&a.start()}function p(e){(function(e){return"MessagePort"===e.constructor.name})(e)&&e.close()}function h(e,a){return y(e,[],a)}function v(e){if(e)throw new Error("Proxy has been released and is not useable")}function b(e){return w(e,{type:"RELEASE"}).then((()=>{p(e)}))}const u=new WeakMap,m="FinalizationRegistry"in globalThis&&new FinalizationRegistry((e=>{const a=(u.get(e)||0)-1;u.set(e,a),0===a&&b(e)}));function y(e,a=[],t=function(){}){let r=!1;const i=new Proxy(t,{get(t,s){if(v(r),s===o)return()=>{!function(e){m&&m.unregister(e)}(i),b(e),r=!0};if("then"===s){if(0===a.length)return{then:()=>i};const t=w(e,{type:"GET",path:a.map((e=>e.toString()))}).then(x);return t.then.bind(t)}return y(e,[...a,s])},set(t,s,o){v(r);const[i,n]=_(o);return w(e,{type:"SET",path:[...a,s].map((e=>e.toString())),value:i},n).then(x)},apply(t,o,i){v(r);const n=a[a.length-1];if(n===s)return w(e,{type:"ENDPOINT"}).then(x);if("bind"===n)return y(e,a.slice(0,-1));const[l,d]=f(i);return w(e,{type:"APPLY",path:a.map((e=>e.toString())),argumentList:l},d).then(x)},construct(t,s){v(r);const[o,i]=f(s);return w(e,{type:"CONSTRUCT",path:a.map((e=>e.toString())),argumentList:o},i).then(x)}});return function(e,a){const t=(u.get(a)||0)+1;u.set(a,t),m&&m.register(e,a,e)}(i,e),i}function f(e){const a=e.map(_);return[a.map((e=>e[0])),(t=a.map((e=>e[1])),Array.prototype.concat.apply([],t))];var t}const g=new WeakMap;function _(e){for(const[a,t]of d)if(t.canHandle(e)){const[r,s]=t.serialize(e);return[{type:"HANDLER",name:a,value:r},s]}return[{type:"RAW",value:e},g.get(e)||[]]}function x(e){switch(e.type){case"HANDLER":return d.get(e.name).deserialize(e.value);case"RAW":return e.value}}function w(e,a,t){return new Promise((r=>{const s=new Array(4).fill(0).map((()=>Math.floor(Math.random()*Number.MAX_SAFE_INTEGER).toString(16))).join("-");e.addEventListener("message",(function a(t){t.data&&t.data.id&&t.data.id===s&&(e.removeEventListener("message",a),r(t.data))})),e.start&&e.start(),e.postMessage(Object.assign({id:s},a),t)}))}}};
//# sourceMappingURL=6697._XZxWmoFmnY.js.map