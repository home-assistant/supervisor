/*! For license information please see 6919.13PaRNiSrME.js.LICENSE.txt */
export const id=6919;export const ids=[6919];export const modules={99095:(t,e,s)=>{var i=s(79192),n=s(29818),o=s(50289);class a extends o.WF{constructor(){super(...arguments),this.multiline=!1}render(){return o.qy` <slot name="container"></slot> <slot class="non-text" name="start"></slot> <div class="text"> <slot name="overline" @slotchange="${this.handleTextSlotChange}"></slot> <slot class="default-slot" @slotchange="${this.handleTextSlotChange}"></slot> <slot name="headline" @slotchange="${this.handleTextSlotChange}"></slot> <slot name="supporting-text" @slotchange="${this.handleTextSlotChange}"></slot> </div> <slot class="non-text" name="trailing-supporting-text"></slot> <slot class="non-text" name="end"></slot> `}handleTextSlotChange(){let t=!1,e=0;for(const s of this.textSlots)if(l(s)&&(e+=1),e>1){t=!0;break}this.multiline=t}}function l(t){for(const e of t.assignedNodes({flatten:!0})){const t=e.nodeType===Node.ELEMENT_NODE,s=e.nodeType===Node.TEXT_NODE&&e.textContent?.match(/\S/);if(t||s)return!0}return!1}(0,i.__decorate)([(0,n.MZ)({type:Boolean,reflect:!0})],a.prototype,"multiline",void 0),(0,i.__decorate)([(0,n.YG)(".text slot")],a.prototype,"textSlots",void 0);const r=o.AH`:host{color:var(--md-sys-color-on-surface,#1d1b20);font-family:var(--md-sys-typescale-body-large-font, var(--md-ref-typeface-plain, Roboto));font-size:var(--md-sys-typescale-body-large-size, 1rem);font-weight:var(--md-sys-typescale-body-large-weight,var(--md-ref-typeface-weight-regular,400));line-height:var(--md-sys-typescale-body-large-line-height, 1.5rem);align-items:center;box-sizing:border-box;display:flex;gap:16px;min-height:56px;overflow:hidden;padding:12px 16px;position:relative;text-overflow:ellipsis}:host([multiline]){min-height:72px}[name=overline]{color:var(--md-sys-color-on-surface-variant,#49454f);font-family:var(--md-sys-typescale-label-small-font, var(--md-ref-typeface-plain, Roboto));font-size:var(--md-sys-typescale-label-small-size, .6875rem);font-weight:var(--md-sys-typescale-label-small-weight,var(--md-ref-typeface-weight-medium,500));line-height:var(--md-sys-typescale-label-small-line-height, 1rem)}[name=supporting-text]{color:var(--md-sys-color-on-surface-variant,#49454f);font-family:var(--md-sys-typescale-body-medium-font, var(--md-ref-typeface-plain, Roboto));font-size:var(--md-sys-typescale-body-medium-size, .875rem);font-weight:var(--md-sys-typescale-body-medium-weight,var(--md-ref-typeface-weight-regular,400));line-height:var(--md-sys-typescale-body-medium-line-height, 1.25rem)}[name=trailing-supporting-text]{color:var(--md-sys-color-on-surface-variant,#49454f);font-family:var(--md-sys-typescale-label-small-font, var(--md-ref-typeface-plain, Roboto));font-size:var(--md-sys-typescale-label-small-size, .6875rem);font-weight:var(--md-sys-typescale-label-small-weight,var(--md-ref-typeface-weight-medium,500));line-height:var(--md-sys-typescale-label-small-line-height, 1rem)}[name=container]::slotted(*){inset:0;position:absolute}.default-slot{display:inline}.default-slot,.text ::slotted(*){overflow:hidden;text-overflow:ellipsis}.text{display:flex;flex:1;flex-direction:column;overflow:hidden}`;let c=class extends a{};c.styles=[r],c=(0,i.__decorate)([(0,n.EM)("md-item")],c)},67129:(t,e,s)=>{s.d(e,{U:()=>n,Z:()=>o});s(89655);var i=s(61680);const n={ArrowDown:"ArrowDown",ArrowLeft:"ArrowLeft",ArrowUp:"ArrowUp",ArrowRight:"ArrowRight",Home:"Home",End:"End"};class o{constructor(t){this.handleKeydown=t=>{const e=t.key;if(t.defaultPrevented||!this.isNavigableKey(e))return;const s=this.items;if(!s.length)return;const o=(0,i.A6)(s,this.isActivatable);t.preventDefault();const a=this.isRtl(),l=a?n.ArrowRight:n.ArrowLeft,r=a?n.ArrowLeft:n.ArrowRight;let c=null;switch(e){case n.ArrowDown:case r:c=(0,i.wm)(s,o,this.isActivatable,this.wrapNavigation());break;case n.ArrowUp:case l:c=(0,i.u9)(s,o,this.isActivatable,this.wrapNavigation());break;case n.Home:c=(0,i.zT)(s,this.isActivatable);break;case n.End:c=(0,i.RZ)(s,this.isActivatable)}c&&o&&o.item!==c&&(o.item.tabIndex=-1)},this.onDeactivateItems=()=>{const t=this.items;for(const e of t)this.deactivateItem(e)},this.onRequestActivation=t=>{this.onDeactivateItems();const e=t.target;this.activateItem(e),e.focus()},this.onSlotchange=()=>{const t=this.items;let e=!1;for(const s of t){!(!s.disabled&&s.tabIndex>-1)||e?s.tabIndex=-1:(e=!0,s.tabIndex=0)}if(e)return;const s=(0,i.c7)(t,this.isActivatable);s&&(s.tabIndex=0)};const{isItem:e,getPossibleItems:s,isRtl:o,deactivateItem:a,activateItem:l,isNavigableKey:r,isActivatable:c,wrapNavigation:d}=t;this.isItem=e,this.getPossibleItems=s,this.isRtl=o,this.deactivateItem=a,this.activateItem=l,this.isNavigableKey=r,this.isActivatable=c,this.wrapNavigation=d??(()=>!0)}get items(){const t=this.getPossibleItems(),e=[];for(const s of t){if(this.isItem(s)){e.push(s);continue}const t=s.item;t&&this.isItem(t)&&e.push(t)}return e}activateNextItem(){const t=this.items,e=(0,i.A6)(t,this.isActivatable);return e&&(e.item.tabIndex=-1),(0,i.wm)(t,e,this.isActivatable,this.wrapNavigation())}activatePreviousItem(){const t=this.items,e=(0,i.A6)(t,this.isActivatable);return e&&(e.item.tabIndex=-1),(0,i.u9)(t,e,this.isActivatable,this.wrapNavigation())}}},61680:(t,e,s)=>{function i(t,e=h){const s=a(t,e);return s&&(s.tabIndex=0,s.focus()),s}function n(t,e=h){const s=l(t,e);return s&&(s.tabIndex=0,s.focus()),s}function o(t,e=h){for(let s=0;s<t.length;s++){const i=t[s];if(0===i.tabIndex&&e(i))return{item:i,index:s}}return null}function a(t,e=h){for(const s of t)if(e(s))return s;return null}function l(t,e=h){for(let s=t.length-1;s>=0;s--){const i=t[s];if(e(i))return i}return null}function r(t,e,s=h,n=!0){if(e){const i=function(t,e,s=h,i=!0){for(let n=1;n<t.length;n++){const o=(n+e)%t.length;if(o<e&&!i)return null;const a=t[o];if(s(a))return a}return t[e]?t[e]:null}(t,e.index,s,n);return i&&(i.tabIndex=0,i.focus()),i}return i(t,s)}function c(t,e,s=h,i=!0){if(e){const n=function(t,e,s=h,i=!0){for(let n=1;n<t.length;n++){const o=(e-n+t.length)%t.length;if(o>e&&!i)return null;const a=t[o];if(s(a))return a}return t[e]?t[e]:null}(t,e.index,s,i);return n&&(n.tabIndex=0,n.focus()),n}return n(t,s)}function d(){return new Event("request-activation",{bubbles:!0,composed:!0})}function h(t){return!t.disabled}s.d(e,{A6:()=>o,Ex:()=>l,RZ:()=>n,c7:()=>a,cG:()=>d,u9:()=>c,wm:()=>r,zT:()=>i})},20725:(t,e,s)=>{s.d(e,{qy:()=>c,eu:()=>a});s(89655),s(253),s(37679);var i=s(2501);const n=Symbol.for(""),o=t=>{if((null==t?void 0:t.r)===n)return null==t?void 0:t._$litStatic$},a=(t,...e)=>({_$litStatic$:e.reduce(((e,s,i)=>e+(t=>{if(void 0!==t._$litStatic$)return t._$litStatic$;throw Error(`Value passed to 'literal' function must be a 'literal' result: ${t}. Use 'unsafeStatic' to pass non-literal values, but\n            take care to ensure page security.`)})(s)+t[i+1]),t[0]),r:n}),l=new Map,r=t=>(e,...s)=>{const i=s.length;let n,a;const r=[],c=[];let d,h=0,m=!1;for(;h<i;){for(d=e[h];h<i&&void 0!==(a=s[h],n=o(a));)d+=n+e[++h],m=!0;h!==i&&c.push(a),r.push(d),h++}if(h===i&&r.push(e[i]),m){const t=r.join("$$lit$$");void 0===(e=l.get(t))&&(r.raw=r,l.set(t,e=r)),s=c}return t(e,...s)},c=r(i.qy);r(i.JW)}};
//# sourceMappingURL=6919.13PaRNiSrME.js.map