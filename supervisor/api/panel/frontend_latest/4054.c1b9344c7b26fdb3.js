/*! For license information please see 4054.c1b9344c7b26fdb3.js.LICENSE.txt */
export const ids=["4054"];export const modules={78755:function(t,e,i){i.d(e,{g:()=>p});var s=i("9065"),r=i("50778"),n=(i("57618"),i("26499"),i("23111"),i("57243")),o=i("35359"),a=i("79840"),c=i("13823"),l=i("64840");const h=(0,c.T)(n.oi);class d extends h{constructor(){super(...arguments),this.disabled=!1,this.type="text",this.isListItem=!0,this.href="",this.target=""}get isDisabled(){return this.disabled&&"link"!==this.type}willUpdate(t){this.href&&(this.type="link"),super.willUpdate(t)}render(){return this.renderListItem(n.dy` <md-item> <div slot="container"> ${this.renderRipple()} ${this.renderFocusRing()} </div> <slot name="start" slot="start"></slot> <slot name="end" slot="end"></slot> ${this.renderBody()} </md-item> `)}renderListItem(t){const e="link"===this.type;let i;switch(this.type){case"link":i=a.i0`a`;break;case"button":i=a.i0`button`;break;default:i=a.i0`li`}const s="text"!==this.type,r=e&&this.target?this.target:n.Ld;return a.dy`
      <${i}
        id="item"
        tabindex="${this.isDisabled||!s?-1:0}"
        ?disabled=${this.isDisabled}
        role="listitem"
        aria-selected=${this.ariaSelected||n.Ld}
        aria-checked=${this.ariaChecked||n.Ld}
        aria-expanded=${this.ariaExpanded||n.Ld}
        aria-haspopup=${this.ariaHasPopup||n.Ld}
        class="list-item ${(0,o.$)(this.getRenderClasses())}"
        href=${this.href||n.Ld}
        target=${r}
        @focus=${this.onFocus}
      >${t}</${i}>
    `}renderRipple(){return"text"===this.type?n.Ld:n.dy` <md-ripple part="ripple" for="item" ?disabled="${this.isDisabled}"></md-ripple>`}renderFocusRing(){return"text"===this.type?n.Ld:n.dy` <md-focus-ring @visibility-changed="${this.onFocusRingVisibilityChanged}" part="focus-ring" for="item" inward></md-focus-ring>`}onFocusRingVisibilityChanged(t){}getRenderClasses(){return{disabled:this.isDisabled}}renderBody(){return n.dy` <slot></slot> <slot name="overline" slot="overline"></slot> <slot name="headline" slot="headline"></slot> <slot name="supporting-text" slot="supporting-text"></slot> <slot name="trailing-supporting-text" slot="trailing-supporting-text"></slot> `}onFocus(){-1===this.tabIndex&&this.dispatchEvent((0,l.oh)())}focus(){this.listItemRoot?.focus()}}d.shadowRootOptions={...n.oi.shadowRootOptions,delegatesFocus:!0},(0,s.__decorate)([(0,r.Cb)({type:Boolean,reflect:!0})],d.prototype,"disabled",void 0),(0,s.__decorate)([(0,r.Cb)({reflect:!0})],d.prototype,"type",void 0),(0,s.__decorate)([(0,r.Cb)({type:Boolean,attribute:"md-list-item",reflect:!0})],d.prototype,"isListItem",void 0),(0,s.__decorate)([(0,r.Cb)()],d.prototype,"href",void 0),(0,s.__decorate)([(0,r.Cb)()],d.prototype,"target",void 0),(0,s.__decorate)([(0,r.IO)(".list-item")],d.prototype,"listItemRoot",void 0);const u=n.iv`:host{display:flex;-webkit-tap-highlight-color:transparent;--md-ripple-hover-color:var(--md-list-item-hover-state-layer-color, var(--md-sys-color-on-surface, #1d1b20));--md-ripple-hover-opacity:var(--md-list-item-hover-state-layer-opacity, 0.08);--md-ripple-pressed-color:var(--md-list-item-pressed-state-layer-color, var(--md-sys-color-on-surface, #1d1b20));--md-ripple-pressed-opacity:var(--md-list-item-pressed-state-layer-opacity, 0.12)}:host(:is([type=button]:not([disabled]),[type=link])){cursor:pointer}md-focus-ring{z-index:1;--md-focus-ring-shape:8px}a,button,li{background:0 0;border:none;cursor:inherit;padding:0;margin:0;text-align:unset;text-decoration:none}.list-item{border-radius:inherit;display:flex;flex:1;max-width:inherit;min-width:inherit;outline:0;-webkit-tap-highlight-color:transparent;width:100%}.list-item.interactive{cursor:pointer}.list-item.disabled{opacity:var(--md-list-item-disabled-opacity, .3);pointer-events:none}[slot=container]{pointer-events:none}md-ripple{border-radius:inherit}md-item{border-radius:inherit;flex:1;height:100%;color:var(--md-list-item-label-text-color,var(--md-sys-color-on-surface,#1d1b20));font-family:var(--md-list-item-label-text-font, var(--md-sys-typescale-body-large-font, var(--md-ref-typeface-plain, Roboto)));font-size:var(--md-list-item-label-text-size, var(--md-sys-typescale-body-large-size, 1rem));line-height:var(--md-list-item-label-text-line-height, var(--md-sys-typescale-body-large-line-height, 1.5rem));font-weight:var(--md-list-item-label-text-weight,var(--md-sys-typescale-body-large-weight,var(--md-ref-typeface-weight-regular,400)));min-height:var(--md-list-item-one-line-container-height,56px);padding-top:var(--md-list-item-top-space,12px);padding-bottom:var(--md-list-item-bottom-space,12px);padding-inline-start:var(--md-list-item-leading-space,16px);padding-inline-end:var(--md-list-item-trailing-space,16px)}md-item[multiline]{min-height:var(--md-list-item-two-line-container-height,72px)}[slot=supporting-text]{color:var(--md-list-item-supporting-text-color,var(--md-sys-color-on-surface-variant,#49454f));font-family:var(--md-list-item-supporting-text-font, var(--md-sys-typescale-body-medium-font, var(--md-ref-typeface-plain, Roboto)));font-size:var(--md-list-item-supporting-text-size, var(--md-sys-typescale-body-medium-size, .875rem));line-height:var(--md-list-item-supporting-text-line-height, var(--md-sys-typescale-body-medium-line-height, 1.25rem));font-weight:var(--md-list-item-supporting-text-weight,var(--md-sys-typescale-body-medium-weight,var(--md-ref-typeface-weight-regular,400)))}[slot=trailing-supporting-text]{color:var(--md-list-item-trailing-supporting-text-color,var(--md-sys-color-on-surface-variant,#49454f));font-family:var(--md-list-item-trailing-supporting-text-font, var(--md-sys-typescale-label-small-font, var(--md-ref-typeface-plain, Roboto)));font-size:var(--md-list-item-trailing-supporting-text-size, var(--md-sys-typescale-label-small-size, .6875rem));line-height:var(--md-list-item-trailing-supporting-text-line-height, var(--md-sys-typescale-label-small-line-height, 1rem));font-weight:var(--md-list-item-trailing-supporting-text-weight,var(--md-sys-typescale-label-small-weight,var(--md-ref-typeface-weight-medium,500)))}:is([slot=start],[slot=end])::slotted(*){fill:currentColor}[slot=start]{color:var(--md-list-item-leading-icon-color,var(--md-sys-color-on-surface-variant,#49454f))}[slot=end]{color:var(--md-list-item-trailing-icon-color,var(--md-sys-color-on-surface-variant,#49454f))}@media(forced-colors:active){.disabled slot{color:GrayText}.list-item.disabled{color:GrayText;opacity:1}}`;let p=class extends d{};p.styles=[u],p=(0,s.__decorate)([(0,r.Mo)("md-list-item")],p)},623:function(t,e,i){i.d(e,{j:()=>h});var s=i("9065"),r=i("50778"),n=(i("85601"),i("92519"),i("42179"),i("89256"),i("24931"),i("88463"),i("57449"),i("19814"),i("57243")),o=i("7750");const a=new Set(Object.values(o.E));class c extends n.oi{get items(){return this.listController.items}constructor(){super(),this.listController=new o.g({isItem:t=>t.hasAttribute("md-list-item"),getPossibleItems:()=>this.slotItems,isRtl:()=>"rtl"===getComputedStyle(this).direction,deactivateItem:t=>{t.tabIndex=-1},activateItem:t=>{t.tabIndex=0},isNavigableKey:t=>a.has(t),isActivatable:t=>!t.disabled&&"text"!==t.type}),this.internals=this.attachInternals(),n.sk||(this.internals.role="list",this.addEventListener("keydown",this.listController.handleKeydown))}render(){return n.dy` <slot @deactivate-items="${this.listController.onDeactivateItems}" @request-activation="${this.listController.onRequestActivation}" @slotchange="${this.listController.onSlotchange}"> </slot> `}activateNextItem(){return this.listController.activateNextItem()}activatePreviousItem(){return this.listController.activatePreviousItem()}}(0,s.__decorate)([(0,r.NH)({flatten:!0})],c.prototype,"slotItems",void 0);const l=n.iv`:host{background:var(--md-list-container-color,var(--md-sys-color-surface,#fef7ff));color:unset;display:flex;flex-direction:column;outline:0;padding:8px 0;position:relative}`;let h=class extends c{};h.styles=[l],h=(0,s.__decorate)([(0,r.Mo)("md-list")],h)},41298:function(t,e,i){i.d(e,{Z:function(){return J}});i(92745),i(92519),i(42179),i(89256),i(24931),i(88463),i(57449),i(19814),i(39527),i(99790),i(41360),i(13334);function s(t){return Array.isArray?Array.isArray(t):"[object Array]"===h(t)}function r(t){return"string"==typeof t}function n(t){return"number"==typeof t}function o(t){return!0===t||!1===t||function(t){return a(t)&&null!==t}(t)&&"[object Boolean]"==h(t)}function a(t){return"object"==typeof t}function c(t){return null!=t}function l(t){return!t.trim().length}function h(t){return null==t?void 0===t?"[object Undefined]":"[object Null]":Object.prototype.toString.call(t)}const d=Object.prototype.hasOwnProperty;class u{constructor(t){this._keys=[],this._keyMap={};let e=0;t.forEach((t=>{let i=p(t);this._keys.push(i),this._keyMap[i.id]=i,e+=i.weight})),this._keys.forEach((t=>{t.weight/=e}))}get(t){return this._keyMap[t]}keys(){return this._keys}toJSON(){return JSON.stringify(this._keys)}}function p(t){let e=null,i=null,n=null,o=1,a=null;if(r(t)||s(t))n=t,e=g(t),i=m(t);else{if(!d.call(t,"name"))throw new Error((t=>`Missing ${t} property in key`)("name"));const s=t.name;if(n=s,d.call(t,"weight")&&(o=t.weight,o<=0))throw new Error((t=>`Property 'weight' in key '${t}' must be a positive integer`)(s));e=g(s),i=m(s),a=t.getFn}return{path:e,id:i,weight:o,src:n,getFn:a}}function g(t){return s(t)?t:t.split(".")}function m(t){return s(t)?t.join("."):t}var f={isCaseSensitive:!1,includeScore:!1,keys:[],shouldSort:!0,sortFn:(t,e)=>t.score===e.score?t.idx<e.idx?-1:1:t.score<e.score?-1:1,includeMatches:!1,findAllMatches:!1,minMatchCharLength:1,location:0,threshold:.6,distance:100,...{useExtendedSearch:!1,getFn:function(t,e){let i=[],a=!1;const l=(t,e,h)=>{if(c(t))if(e[h]){const d=t[e[h]];if(!c(d))return;if(h===e.length-1&&(r(d)||n(d)||o(d)))i.push(function(t){return null==t?"":function(t){if("string"==typeof t)return t;let e=t+"";return"0"==e&&1/t==-1/0?"-0":e}(t)}(d));else if(s(d)){a=!0;for(let t=0,i=d.length;t<i;t+=1)l(d[t],e,h+1)}else e.length&&l(d,e,h+1)}else i.push(t)};return l(t,r(e)?e.split("."):e,0),a?i:i[0]},ignoreLocation:!1,ignoreFieldNorm:!1,fieldNormWeight:1}};const y=/[^ ]+/g;class v{constructor({getFn:t=f.getFn,fieldNormWeight:e=f.fieldNormWeight}={}){this.norm=function(t=1,e=3){const i=new Map,s=Math.pow(10,e);return{get(e){const r=e.match(y).length;if(i.has(r))return i.get(r);const n=1/Math.pow(r,.5*t),o=parseFloat(Math.round(n*s)/s);return i.set(r,o),o},clear(){i.clear()}}}(e,3),this.getFn=t,this.isCreated=!1,this.setIndexRecords()}setSources(t=[]){this.docs=t}setIndexRecords(t=[]){this.records=t}setKeys(t=[]){this.keys=t,this._keysMap={},t.forEach(((t,e)=>{this._keysMap[t.id]=e}))}create(){!this.isCreated&&this.docs.length&&(this.isCreated=!0,r(this.docs[0])?this.docs.forEach(((t,e)=>{this._addString(t,e)})):this.docs.forEach(((t,e)=>{this._addObject(t,e)})),this.norm.clear())}add(t){const e=this.size();r(t)?this._addString(t,e):this._addObject(t,e)}removeAt(t){this.records.splice(t,1);for(let e=t,i=this.size();e<i;e+=1)this.records[e].i-=1}getValueForItemAtKeyId(t,e){return t[this._keysMap[e]]}size(){return this.records.length}_addString(t,e){if(!c(t)||l(t))return;let i={v:t,i:e,n:this.norm.get(t)};this.records.push(i)}_addObject(t,e){let i={i:e,$:{}};this.keys.forEach(((e,n)=>{let o=e.getFn?e.getFn(t):this.getFn(t,e.path);if(c(o))if(s(o)){let t=[];const e=[{nestedArrIndex:-1,value:o}];for(;e.length;){const{nestedArrIndex:i,value:n}=e.pop();if(c(n))if(r(n)&&!l(n)){let e={v:n,i,n:this.norm.get(n)};t.push(e)}else s(n)&&n.forEach(((t,i)=>{e.push({nestedArrIndex:i,value:t})}))}i.$[n]=t}else if(r(o)&&!l(o)){let t={v:o,n:this.norm.get(o)};i.$[n]=t}})),this.records.push(i)}toJSON(){return{keys:this.keys,records:this.records}}}function x(t,e,{getFn:i=f.getFn,fieldNormWeight:s=f.fieldNormWeight}={}){const r=new v({getFn:i,fieldNormWeight:s});return r.setKeys(t.map(p)),r.setSources(e),r.create(),r}function b(t,{errors:e=0,currentLocation:i=0,expectedLocation:s=0,distance:r=f.distance,ignoreLocation:n=f.ignoreLocation}={}){const o=e/t.length;if(n)return o;const a=Math.abs(s-i);return r?o+a/r:a?1:o}const M=32;function L(t,e,i,{location:s=f.location,distance:r=f.distance,threshold:n=f.threshold,findAllMatches:o=f.findAllMatches,minMatchCharLength:a=f.minMatchCharLength,includeMatches:c=f.includeMatches,ignoreLocation:l=f.ignoreLocation}={}){if(e.length>M)throw new Error(`Pattern length exceeds max of ${M}.`);const h=e.length,d=t.length,u=Math.max(0,Math.min(s,d));let p=n,g=u;const m=a>1||c,y=m?Array(d):[];let v;for(;(v=t.indexOf(e,g))>-1;){let t=b(e,{currentLocation:v,expectedLocation:u,distance:r,ignoreLocation:l});if(p=Math.min(t,p),g=v+h,m){let t=0;for(;t<h;)y[v+t]=1,t+=1}}g=-1;let x=[],L=1,_=h+d;const w=1<<h-1;for(let s=0;s<h;s+=1){let n=0,a=_;for(;n<a;){b(e,{errors:s,currentLocation:u+a,expectedLocation:u,distance:r,ignoreLocation:l})<=p?n=a:_=a,a=Math.floor((_-n)/2+n)}_=a;let c=Math.max(1,u-a+1),f=o?d:Math.min(u+a,d)+h,v=Array(f+2);v[f+1]=(1<<s)-1;for(let n=f;n>=c;n-=1){let o=n-1,a=i[t.charAt(o)];if(m&&(y[o]=+!!a),v[n]=(v[n+1]<<1|1)&a,s&&(v[n]|=(x[n+1]|x[n])<<1|1|x[n+1]),v[n]&w&&(L=b(e,{errors:s,currentLocation:o,expectedLocation:u,distance:r,ignoreLocation:l}),L<=p)){if(p=L,g=o,g<=u)break;c=Math.max(1,2*u-g)}}if(b(e,{errors:s+1,currentLocation:u,expectedLocation:u,distance:r,ignoreLocation:l})>p)break;x=v}const k={isMatch:g>=0,score:Math.max(.001,L)};if(m){const t=function(t=[],e=f.minMatchCharLength){let i=[],s=-1,r=-1,n=0;for(let o=t.length;n<o;n+=1){let o=t[n];o&&-1===s?s=n:o||-1===s||(r=n-1,r-s+1>=e&&i.push([s,r]),s=-1)}return t[n-1]&&n-s>=e&&i.push([s,n-1]),i}(y,a);t.length?c&&(k.indices=t):k.isMatch=!1}return k}function _(t){let e={};for(let i=0,s=t.length;i<s;i+=1){const r=t.charAt(i);e[r]=(e[r]||0)|1<<s-i-1}return e}class w{constructor(t,{location:e=f.location,threshold:i=f.threshold,distance:s=f.distance,includeMatches:r=f.includeMatches,findAllMatches:n=f.findAllMatches,minMatchCharLength:o=f.minMatchCharLength,isCaseSensitive:a=f.isCaseSensitive,ignoreLocation:c=f.ignoreLocation}={}){if(this.options={location:e,threshold:i,distance:s,includeMatches:r,findAllMatches:n,minMatchCharLength:o,isCaseSensitive:a,ignoreLocation:c},this.pattern=a?t:t.toLowerCase(),this.chunks=[],!this.pattern.length)return;const l=(t,e)=>{this.chunks.push({pattern:t,alphabet:_(t),startIndex:e})},h=this.pattern.length;if(h>M){let t=0;const e=h%M,i=h-e;for(;t<i;)l(this.pattern.substr(t,M),t),t+=M;if(e){const t=h-M;l(this.pattern.substr(t),t)}}else l(this.pattern,0)}searchIn(t){const{isCaseSensitive:e,includeMatches:i}=this.options;if(e||(t=t.toLowerCase()),this.pattern===t){let e={isMatch:!0,score:0};return i&&(e.indices=[[0,t.length-1]]),e}const{location:s,distance:r,threshold:n,findAllMatches:o,minMatchCharLength:a,ignoreLocation:c}=this.options;let l=[],h=0,d=!1;this.chunks.forEach((({pattern:e,alphabet:u,startIndex:p})=>{const{isMatch:g,score:m,indices:f}=L(t,e,u,{location:s+p,distance:r,threshold:n,findAllMatches:o,minMatchCharLength:a,includeMatches:i,ignoreLocation:c});g&&(d=!0),h+=m,g&&f&&(l=[...l,...f])}));let u={isMatch:d,score:d?h/this.chunks.length:1};return d&&i&&(u.indices=l),u}}class k{constructor(t){this.pattern=t}static isMultiMatch(t){return I(t,this.multiRegex)}static isSingleMatch(t){return I(t,this.singleRegex)}search(){}}function I(t,e){const i=t.match(e);return i?i[1]:null}class C extends k{constructor(t,{location:e=f.location,threshold:i=f.threshold,distance:s=f.distance,includeMatches:r=f.includeMatches,findAllMatches:n=f.findAllMatches,minMatchCharLength:o=f.minMatchCharLength,isCaseSensitive:a=f.isCaseSensitive,ignoreLocation:c=f.ignoreLocation}={}){super(t),this._bitapSearch=new w(t,{location:e,threshold:i,distance:s,includeMatches:r,findAllMatches:n,minMatchCharLength:o,isCaseSensitive:a,ignoreLocation:c})}static get type(){return"fuzzy"}static get multiRegex(){return/^"(.*)"$/}static get singleRegex(){return/^(.*)$/}search(t){return this._bitapSearch.searchIn(t)}}class $ extends k{constructor(t){super(t)}static get type(){return"include"}static get multiRegex(){return/^'"(.*)"$/}static get singleRegex(){return/^'(.*)$/}search(t){let e,i=0;const s=[],r=this.pattern.length;for(;(e=t.indexOf(this.pattern,i))>-1;)i=e+r,s.push([e,i-1]);const n=!!s.length;return{isMatch:n,score:n?0:1,indices:s}}}const S=[class extends k{constructor(t){super(t)}static get type(){return"exact"}static get multiRegex(){return/^="(.*)"$/}static get singleRegex(){return/^=(.*)$/}search(t){const e=t===this.pattern;return{isMatch:e,score:e?0:1,indices:[0,this.pattern.length-1]}}},$,class extends k{constructor(t){super(t)}static get type(){return"prefix-exact"}static get multiRegex(){return/^\^"(.*)"$/}static get singleRegex(){return/^\^(.*)$/}search(t){const e=t.startsWith(this.pattern);return{isMatch:e,score:e?0:1,indices:[0,this.pattern.length-1]}}},class extends k{constructor(t){super(t)}static get type(){return"inverse-prefix-exact"}static get multiRegex(){return/^!\^"(.*)"$/}static get singleRegex(){return/^!\^(.*)$/}search(t){const e=!t.startsWith(this.pattern);return{isMatch:e,score:e?0:1,indices:[0,t.length-1]}}},class extends k{constructor(t){super(t)}static get type(){return"inverse-suffix-exact"}static get multiRegex(){return/^!"(.*)"\$$/}static get singleRegex(){return/^!(.*)\$$/}search(t){const e=!t.endsWith(this.pattern);return{isMatch:e,score:e?0:1,indices:[0,t.length-1]}}},class extends k{constructor(t){super(t)}static get type(){return"suffix-exact"}static get multiRegex(){return/^"(.*)"\$$/}static get singleRegex(){return/^(.*)\$$/}search(t){const e=t.endsWith(this.pattern);return{isMatch:e,score:e?0:1,indices:[t.length-this.pattern.length,t.length-1]}}},class extends k{constructor(t){super(t)}static get type(){return"inverse-exact"}static get multiRegex(){return/^!"(.*)"$/}static get singleRegex(){return/^!(.*)$/}search(t){const e=-1===t.indexOf(this.pattern);return{isMatch:e,score:e?0:1,indices:[0,t.length-1]}}},C],R=S.length,A=/ +(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)/;const F=new Set([C.type,$.type]);class E{constructor(t,{isCaseSensitive:e=f.isCaseSensitive,includeMatches:i=f.includeMatches,minMatchCharLength:s=f.minMatchCharLength,ignoreLocation:r=f.ignoreLocation,findAllMatches:n=f.findAllMatches,location:o=f.location,threshold:a=f.threshold,distance:c=f.distance}={}){this.query=null,this.options={isCaseSensitive:e,includeMatches:i,minMatchCharLength:s,findAllMatches:n,ignoreLocation:r,location:o,threshold:a,distance:c},this.pattern=e?t:t.toLowerCase(),this.query=function(t,e={}){return t.split("|").map((t=>{let i=t.trim().split(A).filter((t=>t&&!!t.trim())),s=[];for(let t=0,r=i.length;t<r;t+=1){const r=i[t];let n=!1,o=-1;for(;!n&&++o<R;){const t=S[o];let i=t.isMultiMatch(r);i&&(s.push(new t(i,e)),n=!0)}if(!n)for(o=-1;++o<R;){const t=S[o];let i=t.isSingleMatch(r);if(i){s.push(new t(i,e));break}}}return s}))}(this.pattern,this.options)}static condition(t,e){return e.useExtendedSearch}searchIn(t){const e=this.query;if(!e)return{isMatch:!1,score:1};const{includeMatches:i,isCaseSensitive:s}=this.options;t=s?t:t.toLowerCase();let r=0,n=[],o=0;for(let s=0,a=e.length;s<a;s+=1){const a=e[s];n.length=0,r=0;for(let e=0,s=a.length;e<s;e+=1){const s=a[e],{isMatch:c,indices:l,score:h}=s.search(t);if(!c){o=0,r=0,n.length=0;break}if(r+=1,o+=h,i){const t=s.constructor.type;F.has(t)?n=[...n,...l]:n.push(l)}}if(r){let t={isMatch:!0,score:o/r};return i&&(t.indices=n),t}}return{isMatch:!1,score:1}}}const N=[];function O(t,e){for(let i=0,s=N.length;i<s;i+=1){let s=N[i];if(s.condition(t,e))return new s(t,e)}return new w(t,e)}const j="$and",z="$or",W="$path",P="$val",K=t=>!(!t[j]&&!t[z]),D=t=>({[j]:Object.keys(t).map((e=>({[e]:t[e]})))});function q(t,e,{auto:i=!0}={}){const n=t=>{let o=Object.keys(t);const c=(t=>!!t[W])(t);if(!c&&o.length>1&&!K(t))return n(D(t));if((t=>!s(t)&&a(t)&&!K(t))(t)){const s=c?t[W]:o[0],n=c?t[P]:t[s];if(!r(n))throw new Error((t=>`Invalid value for key ${t}`)(s));const a={keyId:m(s),pattern:n};return i&&(a.searcher=O(n,e)),a}let l={children:[],operator:o[0]};return o.forEach((e=>{const i=t[e];s(i)&&i.forEach((t=>{l.children.push(n(t))}))})),l};return K(t)||(t=D(t)),n(t)}function B(t,e){const i=t.matches;e.matches=[],c(i)&&i.forEach((t=>{if(!c(t.indices)||!t.indices.length)return;const{indices:i,value:s}=t;let r={indices:i,value:s};t.key&&(r.key=t.key.src),t.idx>-1&&(r.refIndex=t.idx),e.matches.push(r)}))}function V(t,e){e.score=t.score}class J{constructor(t,e={},i){this.options={...f,...e},this.options.useExtendedSearch,this._keyStore=new u(this.options.keys),this.setCollection(t,i)}setCollection(t,e){if(this._docs=t,e&&!(e instanceof v))throw new Error("Incorrect 'index' type");this._myIndex=e||x(this.options.keys,this._docs,{getFn:this.options.getFn,fieldNormWeight:this.options.fieldNormWeight})}add(t){c(t)&&(this._docs.push(t),this._myIndex.add(t))}remove(t=()=>!1){const e=[];for(let i=0,s=this._docs.length;i<s;i+=1){const r=this._docs[i];t(r,i)&&(this.removeAt(i),i-=1,s-=1,e.push(r))}return e}removeAt(t){this._docs.splice(t,1),this._myIndex.removeAt(t)}getIndex(){return this._myIndex}search(t,{limit:e=-1}={}){const{includeMatches:i,includeScore:s,shouldSort:o,sortFn:a,ignoreFieldNorm:c}=this.options;let l=r(t)?r(this._docs[0])?this._searchStringList(t):this._searchObjectList(t):this._searchLogical(t);return function(t,{ignoreFieldNorm:e=f.ignoreFieldNorm}){t.forEach((t=>{let i=1;t.matches.forEach((({key:t,norm:s,score:r})=>{const n=t?t.weight:null;i*=Math.pow(0===r&&n?Number.EPSILON:r,(n||1)*(e?1:s))})),t.score=i}))}(l,{ignoreFieldNorm:c}),o&&l.sort(a),n(e)&&e>-1&&(l=l.slice(0,e)),function(t,e,{includeMatches:i=f.includeMatches,includeScore:s=f.includeScore}={}){const r=[];return i&&r.push(B),s&&r.push(V),t.map((t=>{const{idx:i}=t,s={item:e[i],refIndex:i};return r.length&&r.forEach((e=>{e(t,s)})),s}))}(l,this._docs,{includeMatches:i,includeScore:s})}_searchStringList(t){const e=O(t,this.options),{records:i}=this._myIndex,s=[];return i.forEach((({v:t,i,n:r})=>{if(!c(t))return;const{isMatch:n,score:o,indices:a}=e.searchIn(t);n&&s.push({item:t,idx:i,matches:[{score:o,value:t,norm:r,indices:a}]})})),s}_searchLogical(t){const e=q(t,this.options),i=(t,e,s)=>{if(!t.children){const{keyId:i,searcher:r}=t,n=this._findMatches({key:this._keyStore.get(i),value:this._myIndex.getValueForItemAtKeyId(e,i),searcher:r});return n&&n.length?[{idx:s,item:e,matches:n}]:[]}const r=[];for(let n=0,o=t.children.length;n<o;n+=1){const o=t.children[n],a=i(o,e,s);if(a.length)r.push(...a);else if(t.operator===j)return[]}return r},s=this._myIndex.records,r={},n=[];return s.forEach((({$:t,i:s})=>{if(c(t)){let o=i(e,t,s);o.length&&(r[s]||(r[s]={idx:s,item:t,matches:[]},n.push(r[s])),o.forEach((({matches:t})=>{r[s].matches.push(...t)})))}})),n}_searchObjectList(t){const e=O(t,this.options),{keys:i,records:s}=this._myIndex,r=[];return s.forEach((({$:t,i:s})=>{if(!c(t))return;let n=[];i.forEach(((i,s)=>{n.push(...this._findMatches({key:i,value:t[s],searcher:e}))})),n.length&&r.push({idx:s,item:t,matches:n})})),r}_findMatches({key:t,value:e,searcher:i}){if(!c(e))return[];let r=[];if(s(e))e.forEach((({v:e,i:s,n})=>{if(!c(e))return;const{isMatch:o,score:a,indices:l}=i.searchIn(e);o&&r.push({score:a,key:t,value:e,idx:s,norm:n,indices:l})}));else{const{v:s,n}=e,{isMatch:o,score:a,indices:c}=i.searchIn(s);o&&r.push({score:a,key:t,value:s,norm:n,indices:c})}return r}}J.version="7.0.0",J.createIndex=x,J.parseIndex=function(t,{getFn:e=f.getFn,fieldNormWeight:i=f.fieldNormWeight}={}){const{keys:s,records:r}=t,n=new v({getFn:e,fieldNormWeight:i});return n.setKeys(s),n.setIndexRecords(r),n},J.config=f,J.parseQuery=q,function(...t){N.push(...t)}(E)}};
//# sourceMappingURL=4054.c1b9344c7b26fdb3.js.map