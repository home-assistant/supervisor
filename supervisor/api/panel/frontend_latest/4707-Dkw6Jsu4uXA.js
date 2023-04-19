/*! For license information please see 4707-Dkw6Jsu4uXA.js.LICENSE.txt */
"use strict";(self.webpackChunkhome_assistant_frontend=self.webpackChunkhome_assistant_frontend||[]).push([[4707],{29530:(e,t,i)=>{i.d(t,{t:()=>l});var s=i(57835),o=i(68144),r=i(76187);const n=Symbol("valueNotInitialized");class a extends r.sR{constructor(e){if(super(e),e.type!==s.pX.ELEMENT)throw new Error(`\`${this.constructor.name}\` must be bound to an element.`);this.previousValue=n}render(e,t){return o.Ld}update(e,[t,i]){if(!this.hasChanged(i))return o.Ld;this.host=e.options&&e.options.host,this.element=e.element,this.renderer=t;return this.previousValue===n?this.addRenderer():this.runRenderer(),this.previousValue=Array.isArray(i)?[...i]:i,o.Ld}reconnected(){this.addRenderer()}disconnected(){this.removeRenderer()}addRenderer(){throw new Error("The `addRenderer` method must be implemented.")}runRenderer(){throw new Error("The `runRenderer` method must be implemented.")}removeRenderer(){throw new Error("The `removeRenderer` method must be implemented.")}renderRenderer(e,...t){const i=this.renderer.call(this.host,...t);(0,o.sY)(i,e,{host:this.host})}hasChanged(e){return Array.isArray(e)?!Array.isArray(this.previousValue)||(this.previousValue.length!==e.length||e.some(((e,t)=>e!==this.previousValue[t]))):this.previousValue!==e}}const l=(0,s.XM)(class extends a{addRenderer(){this.element.renderer=(e,t,i)=>{this.renderRenderer(e,i.item,i,t)}}runRenderer(){this.element.requestContentUpdate()}removeRenderer(){this.element.renderer=null}})},7993:(e,t,i)=>{class s extends HTMLElement{static get version(){return"23.3.10"}}customElements.define("vaadin-material-styles",s);var o=i(86295);const r=o.iv`
  :host {
    /* Text colors */
    --material-body-text-color: var(--light-theme-text-color, rgba(0, 0, 0, 0.87));
    --material-secondary-text-color: var(--light-theme-secondary-color, rgba(0, 0, 0, 0.54));
    --material-disabled-text-color: var(--light-theme-disabled-color, rgba(0, 0, 0, 0.38));

    /* Primary colors */
    --material-primary-color: var(--primary-color, #6200ee);
    --material-primary-contrast-color: var(--dark-theme-base-color, #fff);
    --material-primary-text-color: var(--material-primary-color);

    /* Error colors */
    --material-error-color: var(--error-color, #b00020);
    --material-error-text-color: var(--material-error-color);

    /* Background colors */
    --material-background-color: var(--light-theme-background-color, #fff);
    --material-secondary-background-color: var(--light-theme-secondary-background-color, #f5f5f5);
    --material-disabled-color: rgba(0, 0, 0, 0.26);

    /* Divider colors */
    --material-divider-color: rgba(0, 0, 0, 0.12);

    /* Undocumented internal properties (prefixed with three dashes) */

    /* Text field tweaks */
    --_material-text-field-input-line-background-color: initial;
    --_material-text-field-input-line-opacity: initial;
    --_material-text-field-input-line-hover-opacity: initial;
    --_material-text-field-focused-label-opacity: initial;

    /* Button tweaks */
    --_material-button-raised-background-color: initial;
    --_material-button-outline-color: initial;

    /* Grid tweaks */
    --_material-grid-row-hover-background-color: initial;

    /* Split layout tweaks */
    --_material-split-layout-splitter-background-color: initial;

    background-color: var(--material-background-color);
    color: var(--material-body-text-color);
  }

  [theme~='dark'] {
    /* Text colors */
    --material-body-text-color: var(--dark-theme-text-color, rgba(255, 255, 255, 1));
    --material-secondary-text-color: var(--dark-theme-secondary-color, rgba(255, 255, 255, 0.7));
    --material-disabled-text-color: var(--dark-theme-disabled-color, rgba(255, 255, 255, 0.5));

    /* Primary colors */
    --material-primary-color: var(--light-primary-color, #7e3ff2);
    --material-primary-text-color: #b794f6;

    /* Error colors */
    --material-error-color: var(--error-color, #de2839);
    --material-error-text-color: var(--material-error-color);

    /* Background colors */
    --material-background-color: var(--dark-theme-background-color, #303030);
    --material-secondary-background-color: var(--dark-theme-secondary-background-color, #3b3b3b);
    --material-disabled-color: rgba(255, 255, 255, 0.3);

    /* Divider colors */
    --material-divider-color: rgba(255, 255, 255, 0.12);

    /* Undocumented internal properties (prefixed with three dashes) */

    /* Text field tweaks */
    --_material-text-field-input-line-background-color: #fff;
    --_material-text-field-input-line-opacity: 0.7;
    --_material-text-field-input-line-hover-opacity: 1;
    --_material-text-field-focused-label-opacity: 1;

    /* Button tweaks */
    --_material-button-raised-background-color: rgba(255, 255, 255, 0.08);
    --_material-button-outline-color: rgba(255, 255, 255, 0.2);

    /* Grid tweaks */
    --_material-grid-row-hover-background-color: rgba(255, 255, 255, 0.08);
    --_material-grid-row-selected-overlay-opacity: 0.16;

    /* Split layout tweaks */
    --_material-split-layout-splitter-background-color: rgba(255, 255, 255, 0.8);

    background-color: var(--material-background-color);
    color: var(--material-body-text-color);
  }

  a {
    color: inherit;
  }
`;(0,o.hC)("",r,{moduleId:"material-color-light"});const n=o.iv`
  :host {
    /* Text colors */
    --material-body-text-color: var(--dark-theme-text-color, rgba(255, 255, 255, 1));
    --material-secondary-text-color: var(--dark-theme-secondary-color, rgba(255, 255, 255, 0.7));
    --material-disabled-text-color: var(--dark-theme-disabled-color, rgba(255, 255, 255, 0.5));

    /* Primary colors */
    --material-primary-color: var(--light-primary-color, #7e3ff2);
    --material-primary-text-color: #b794f6;

    /* Error colors */
    --material-error-color: var(--error-color, #de2839);
    --material-error-text-color: var(--material-error-color);

    /* Background colors */
    --material-background-color: var(--dark-theme-background-color, #303030);
    --material-secondary-background-color: var(--dark-theme-secondary-background-color, #3b3b3b);
    --material-disabled-color: rgba(255, 255, 255, 0.3);

    /* Divider colors */
    --material-divider-color: rgba(255, 255, 255, 0.12);

    /* Undocumented internal properties (prefixed with three dashes) */

    /* Text field tweaks */
    --_material-text-field-input-line-background-color: #fff;
    --_material-text-field-input-line-opacity: 0.7;
    --_material-text-field-input-line-hover-opacity: 1;
    --_material-text-field-focused-label-opacity: 1;

    /* Button tweaks */
    --_material-button-raised-background-color: rgba(255, 255, 255, 0.08);
    --_material-button-outline-color: rgba(255, 255, 255, 0.2);

    /* Grid tweaks */
    --_material-grid-row-hover-background-color: rgba(255, 255, 255, 0.08);
    --_material-grid-row-selected-overlay-opacity: 0.16;

    /* Split layout tweaks */
    --_material-split-layout-splitter-background-color: rgba(255, 255, 255, 0.8);

    background-color: var(--material-background-color);
    color: var(--material-body-text-color);
  }
`;(0,o.hC)("",n,{moduleId:"material-color-dark"});const a=o.iv`
  :host {
    /* Text colors */
    --material-body-text-color: var(--light-theme-text-color, rgba(0, 0, 0, 0.87));
    --material-secondary-text-color: var(--light-theme-secondary-color, rgba(0, 0, 0, 0.54));
    --material-disabled-text-color: var(--light-theme-disabled-color, rgba(0, 0, 0, 0.38));

    /* Primary colors */
    --material-primary-color: var(--primary-color, #6200ee);
    --material-primary-contrast-color: var(--dark-theme-base-color, #fff);
    --material-primary-text-color: var(--material-primary-color);

    /* Error colors */
    --material-error-color: var(--error-color, #b00020);
    --material-error-text-color: var(--material-error-color);

    /* Background colors */
    --material-background-color: var(--light-theme-background-color, #fff);
    --material-secondary-background-color: var(--light-theme-secondary-background-color, #f5f5f5);
    --material-disabled-color: rgba(0, 0, 0, 0.26);

    /* Divider colors */
    --material-divider-color: rgba(0, 0, 0, 0.12);
  }
`,l=document.createElement("template");l.innerHTML=`<style>${a.toString().replace(":host","html")}</style>`,document.head.appendChild(l.content);const h=o.iv`
  /* prettier-ignore */
  :host {
    /* from http://codepen.io/shyndman/pen/c5394ddf2e8b2a5c9185904b57421cdb */
    --material-shadow-elevation-2dp: 0 2px 2px 0 rgba(0, 0, 0, 0.14), 0 1px 5px 0 rgba(0, 0, 0, 0.12), 0 3px 1px -2px rgba(0, 0, 0, 0.2);
    --material-shadow-elevation-3dp: 0 3px 4px 0 rgba(0, 0, 0, 0.14), 0 1px 8px 0 rgba(0, 0, 0, 0.12), 0 3px 3px -2px rgba(0, 0, 0, 0.4);
    --material-shadow-elevation-4dp: 0 4px 5px 0 rgba(0, 0, 0, 0.14), 0 1px 10px 0 rgba(0, 0, 0, 0.12), 0 2px 4px -1px rgba(0, 0, 0, 0.4);
    --material-shadow-elevation-6dp: 0 6px 10px 0 rgba(0, 0, 0, 0.14), 0 1px 18px 0 rgba(0, 0, 0, 0.12), 0 3px 5px -1px rgba(0, 0, 0, 0.4);
    --material-shadow-elevation-8dp: 0 8px 10px 1px rgba(0, 0, 0, 0.14), 0 3px 14px 2px rgba(0, 0, 0, 0.12), 0 5px 5px -3px rgba(0, 0, 0, 0.4);
    --material-shadow-elevation-12dp: 0 12px 16px 1px rgba(0, 0, 0, 0.14), 0 4px 22px 3px rgba(0, 0, 0, 0.12), 0 6px 7px -4px rgba(0, 0, 0, 0.4);
    --material-shadow-elevation-16dp: 0 16px 24px 2px rgba(0, 0, 0, 0.14), 0 6px 30px 5px rgba(0, 0, 0, 0.12), 0 8px 10px -5px rgba(0, 0, 0, 0.4);
    --material-shadow-elevation-24dp: 0 24px 38px 3px rgba(0, 0, 0, 0.14), 0 9px 46px 8px rgba(0, 0, 0, 0.12), 0 11px 15px -7px rgba(0, 0, 0, 0.4);
  }
`,d=document.createElement("template");d.innerHTML=`<style>${h.toString().replace(":host","html")}</style>`,document.head.appendChild(d.content);const c=o.iv`
  :host {
    top: 16px;
    right: 16px;
    /* TODO (@jouni): remove unnecessary multiplication after https://github.com/vaadin/vaadin-overlay/issues/90 is fixed */
    bottom: calc(1px * var(--vaadin-overlay-viewport-bottom) + 16px);
    left: 16px;
  }

  [part='overlay'] {
    background-color: var(--material-background-color);
    border-radius: 4px;
    box-shadow: var(--material-shadow-elevation-4dp);
    color: var(--material-body-text-color);
    font-family: var(--material-font-family);
    font-size: var(--material-body-font-size);
    font-weight: 400;
  }

  [part='content'] {
    padding: 8px 0;
  }

  [part='backdrop'] {
    opacity: 0.2;
    animation: 0.2s vaadin-overlay-backdrop-enter;
    will-change: opacity;
  }

  @keyframes vaadin-overlay-backdrop-enter {
    0% {
      opacity: 0;
    }
  }
`;(0,o.hC)("",c,{moduleId:"material-overlay"}),(0,o.hC)("vaadin-overlay",c,{moduleId:"material-vaadin-overlay"});var u=i(20723),_=i(87529),p=i(52521),m=i(28426);const g=e=>e.test(navigator.userAgent),v=e=>e.test(navigator.platform);g(/Android/),g(/Chrome/)&&/Google Inc/.test(navigator.vendor);g(/Firefox/);const b=v(/^iPad/)||v(/^Mac/)&&navigator.maxTouchPoints>1,f=v(/^iPhone/)||b,y=g(/^((?!chrome|android).)*safari/i),x=(()=>{try{return document.createEvent("TouchEvent"),!0}catch(e){return!1}})();var I=i(76389);const C=(0,I.o)((e=>class extends e{constructor(){super(),this.__controllers=new Set}connectedCallback(){super.connectedCallback(),this.__controllers.forEach((e=>{e.hostConnected&&e.hostConnected()}))}disconnectedCallback(){super.disconnectedCallback(),this.__controllers.forEach((e=>{e.hostDisconnected&&e.hostDisconnected()}))}addController(e){this.__controllers.add(e),void 0!==this.$&&this.isConnected&&e.hostConnected&&e.hostConnected()}removeController(e){this.__controllers.delete(e)}}));class w{static detectScrollType(){const e=document.createElement("div");e.textContent="ABCD",e.dir="rtl",e.style.fontSize="14px",e.style.width="4px",e.style.height="1px",e.style.position="absolute",e.style.top="-1000px",e.style.overflow="scroll",document.body.appendChild(e);let t="reverse";return e.scrollLeft>0?t="default":(e.scrollLeft=2,e.scrollLeft<2&&(t="negative")),document.body.removeChild(e),t}static getNormalizedScrollLeft(e,t,i){const{scrollLeft:s}=i;if("rtl"!==t||!e)return s;switch(e){case"negative":return i.scrollWidth-i.clientWidth+s;case"reverse":return i.scrollWidth-i.clientWidth-s;default:return s}}static setNormalizedScrollLeft(e,t,i,s){if("rtl"===t&&e)switch(e){case"negative":i.scrollLeft=i.clientWidth-i.scrollWidth+s;break;case"reverse":i.scrollLeft=i.scrollWidth-i.clientWidth-s;break;default:i.scrollLeft=s}else i.scrollLeft=s}}const E=[];let S;function T(e,t,i=e.getAttribute("dir")){t?e.setAttribute("dir",t):null!=i&&e.removeAttribute("dir")}function V(){return document.documentElement.getAttribute("dir")}new MutationObserver((function(){const e=V();E.forEach((t=>{T(t,e)}))})).observe(document.documentElement,{attributes:!0,attributeFilter:["dir"]});const k=e=>class extends e{static get properties(){return{dir:{type:String,value:"",reflectToAttribute:!0,converter:{fromAttribute:e=>e||"",toAttribute:e=>""===e?null:e}}}}static finalize(){super.finalize(),S||(S=w.detectScrollType())}connectedCallback(){super.connectedCallback(),this.hasAttribute("dir")&&!this.__restoreSubscription||(this.__subscribe(),T(this,V(),null))}attributeChangedCallback(e,t,i){if(super.attributeChangedCallback(e,t,i),"dir"!==e)return;const s=V(),o=i===s&&-1===E.indexOf(this),r=!i&&t&&-1===E.indexOf(this),n=i!==s&&t===s;o||r?(this.__subscribe(),T(this,s,i)):n&&this.__unsubscribe()}disconnectedCallback(){super.disconnectedCallback(),this.__restoreSubscription=E.includes(this),this.__unsubscribe()}_valueToNodeAttribute(e,t,i){("dir"!==i||""!==t||e.hasAttribute("dir"))&&super._valueToNodeAttribute(e,t,i)}_attributeToProperty(e,t,i){"dir"!==e||t?super._attributeToProperty(e,t,i):this.dir=""}__subscribe(){E.includes(this)||E.push(this)}__unsubscribe(){E.includes(this)&&E.splice(E.indexOf(this),1)}__getNormalizedScrollLeft(e){return w.getNormalizedScrollLeft(S,this.getAttribute("dir")||"ltr",e)}__setNormalizedScrollLeft(e,t){return w.setNormalizedScrollLeft(S,this.getAttribute("dir")||"ltr",e,t)}};let P=!1;function O(e){const t=e.style;if("hidden"===t.visibility||"none"===t.display)return!0;const i=window.getComputedStyle(e);return"hidden"===i.visibility||"none"===i.display}function A(e,t){const i=Math.max(e.tabIndex,0),s=Math.max(t.tabIndex,0);return 0===i||0===s?s>i:i>s}function L(e){const t=e.length;if(t<2)return e;const i=Math.ceil(t/2);return function(e,t){const i=[];for(;e.length>0&&t.length>0;)A(e[0],t[0])?i.push(t.shift()):i.push(e.shift());return i.concat(e,t)}(L(e.slice(0,i)),L(e.slice(i)))}function z(e,t){if(e.nodeType!==Node.ELEMENT_NODE||O(e))return!1;const i=e,s=function(e){if(!function(e){return!e.matches('[tabindex="-1"]')&&(e.matches("input, select, textarea, button, object")?e.matches(":not([disabled])"):e.matches("a[href], area[href], iframe, [tabindex], [contentEditable]"))}(e))return-1;const t=e.getAttribute("tabindex")||0;return Number(t)}(i);let o=s>0;s>=0&&t.push(i);let r=[];return r="slot"===i.localName?i.assignedNodes({flatten:!0}):(i.shadowRoot||i).children,[...r].forEach((e=>{o=z(e,t)||o})),o}function R(e){return e.getRootNode().activeElement===e}window.addEventListener("keydown",(()=>{P=!0}),{capture:!0}),window.addEventListener("mousedown",(()=>{P=!1}),{capture:!0});const N=[];class B{constructor(e){this.host=e,this.__trapNode=null,this.__onKeyDown=this.__onKeyDown.bind(this)}hostConnected(){document.addEventListener("keydown",this.__onKeyDown)}hostDisconnected(){document.removeEventListener("keydown",this.__onKeyDown)}trapFocus(e){if(this.__trapNode=e,0===this.__focusableElements.length)throw this.__trapNode=null,new Error("The trap node should have at least one focusable descendant or be focusable itself.");N.push(this),-1===this.__focusedElementIndex&&this.__focusableElements[0].focus()}releaseFocus(){this.__trapNode=null,N.pop()}__onKeyDown(e){if(this.__trapNode&&this===Array.from(N).pop()&&"Tab"===e.key){e.preventDefault();const t=e.shiftKey;this.__focusNextElement(t)}}__focusNextElement(e=!1){const t=this.__focusableElements,i=e?-1:1,s=this.__focusedElementIndex,o=t[(t.length+s+i)%t.length];o.focus(),"input"===o.localName&&o.select()}get __focusableElements(){return function(e){const t=[];return z(e,t)?L(t):t}(this.__trapNode)}get __focusedElementIndex(){const e=this.__focusableElements;return e.indexOf(e.filter(R).pop())}}class D extends((0,o.Tb)(k(C(m.H3)))){static get template(){return m.dy`
      <style>
        :host {
          z-index: 200;
          position: fixed;

          /* Despite of what the names say, <vaadin-overlay> is just a container
          for position/sizing/alignment. The actual overlay is the overlay part. */

          /* Default position constraints: the entire viewport. Note: themes can
          override this to introduce gaps between the overlay and the viewport. */
          top: 0;
          right: 0;
          bottom: var(--vaadin-overlay-viewport-bottom);
          left: 0;

          /* Use flexbox alignment for the overlay part. */
          display: flex;
          flex-direction: column; /* makes dropdowns sizing easier */
          /* Align to center by default. */
          align-items: center;
          justify-content: center;

          /* Allow centering when max-width/max-height applies. */
          margin: auto;

          /* The host is not clickable, only the overlay part is. */
          pointer-events: none;

          /* Remove tap highlight on touch devices. */
          -webkit-tap-highlight-color: transparent;

          /* CSS API for host */
          --vaadin-overlay-viewport-bottom: 0;
        }

        :host([hidden]),
        :host(:not([opened]):not([closing])) {
          display: none !important;
        }

        [part='overlay'] {
          -webkit-overflow-scrolling: touch;
          overflow: auto;
          pointer-events: auto;

          /* Prevent overflowing the host in MSIE 11 */
          max-width: 100%;
          box-sizing: border-box;

          -webkit-tap-highlight-color: initial; /* reenable tap highlight inside */
        }

        [part='backdrop'] {
          z-index: -1;
          content: '';
          background: rgba(0, 0, 0, 0.5);
          position: fixed;
          top: 0;
          left: 0;
          bottom: 0;
          right: 0;
          pointer-events: auto;
        }
      </style>

      <div id="backdrop" part="backdrop" hidden$="[[!withBackdrop]]"></div>
      <div part="overlay" id="overlay" tabindex="0">
        <div part="content" id="content">
          <slot></slot>
        </div>
      </div>
    `}static get is(){return"vaadin-overlay"}static get properties(){return{opened:{type:Boolean,notify:!0,observer:"_openedChanged",reflectToAttribute:!0},owner:Element,renderer:Function,template:{type:Object,notify:!0},content:{type:Object,notify:!0},withBackdrop:{type:Boolean,value:!1,reflectToAttribute:!0},model:Object,modeless:{type:Boolean,value:!1,reflectToAttribute:!0,observer:"_modelessChanged"},hidden:{type:Boolean,reflectToAttribute:!0,observer:"_hiddenChanged"},focusTrap:{type:Boolean,value:!1},restoreFocusOnClose:{type:Boolean,value:!1},restoreFocusNode:{type:HTMLElement},_mouseDownInside:{type:Boolean},_mouseUpInside:{type:Boolean},_instance:{type:Object},_originalContentPart:Object,_contentNodes:Array,_oldOwner:Element,_oldModel:Object,_oldTemplate:Object,_oldRenderer:Object,_oldOpened:Boolean}}static get observers(){return["_templateOrRendererChanged(template, renderer, owner, model, opened)"]}constructor(){super(),this._boundMouseDownListener=this._mouseDownListener.bind(this),this._boundMouseUpListener=this._mouseUpListener.bind(this),this._boundOutsideClickListener=this._outsideClickListener.bind(this),this._boundKeydownListener=this._keydownListener.bind(this),this._observer=new u.o(this,(e=>{this._setTemplateFromNodes(e.addedNodes)})),this._boundIronOverlayCanceledListener=this._ironOverlayCanceled.bind(this),f&&(this._boundIosResizeListener=()=>this._detectIosNavbar()),this.__focusTrapController=new B(this)}ready(){super.ready(),this._observer.flush(),this.addEventListener("click",(()=>{})),this.$.backdrop.addEventListener("click",(()=>{})),this.addController(this.__focusTrapController)}_detectIosNavbar(){if(!this.opened)return;const e=window.innerHeight,t=window.innerWidth>e,i=document.documentElement.clientHeight;t&&i>e?this.style.setProperty("--vaadin-overlay-viewport-bottom",i-e+"px"):this.style.setProperty("--vaadin-overlay-viewport-bottom","0")}_setTemplateFromNodes(e){this.template=e.find((e=>e.localName&&"template"===e.localName))||this.template}close(e){const t=new CustomEvent("vaadin-overlay-close",{bubbles:!0,cancelable:!0,detail:{sourceEvent:e}});this.dispatchEvent(t),t.defaultPrevented||(this.opened=!1)}connectedCallback(){super.connectedCallback(),this._boundIosResizeListener&&(this._detectIosNavbar(),window.addEventListener("resize",this._boundIosResizeListener))}disconnectedCallback(){super.disconnectedCallback(),this._boundIosResizeListener&&window.removeEventListener("resize",this._boundIosResizeListener)}requestContentUpdate(){this.renderer&&this.renderer.call(this.owner,this.content,this.owner,this.model)}_ironOverlayCanceled(e){e.preventDefault()}_mouseDownListener(e){this._mouseDownInside=e.composedPath().indexOf(this.$.overlay)>=0}_mouseUpListener(e){this._mouseUpInside=e.composedPath().indexOf(this.$.overlay)>=0}_outsideClickListener(e){if(e.composedPath().includes(this.$.overlay)||this._mouseDownInside||this._mouseUpInside)return this._mouseDownInside=!1,void(this._mouseUpInside=!1);if(!this._last)return;const t=new CustomEvent("vaadin-overlay-outside-click",{bubbles:!0,cancelable:!0,detail:{sourceEvent:e}});this.dispatchEvent(t),this.opened&&!t.defaultPrevented&&this.close(e)}_keydownListener(e){if(this._last&&(!this.modeless||e.composedPath().includes(this.$.overlay))&&"Escape"===e.key){const t=new CustomEvent("vaadin-overlay-escape-press",{bubbles:!0,cancelable:!0,detail:{sourceEvent:e}});this.dispatchEvent(t),this.opened&&!t.defaultPrevented&&this.close(e)}}_ensureTemplatized(){this._setTemplateFromNodes(Array.from(this.children))}_openedChanged(e,t){this._instance||this._ensureTemplatized(),e?(this.__restoreFocusNode=this._getActiveElement(),this._animatedOpening(),(0,_.T8)(this,(()=>{this.focusTrap&&this.__focusTrapController.trapFocus(this.$.overlay);const e=new CustomEvent("vaadin-overlay-open",{bubbles:!0});this.dispatchEvent(e)})),document.addEventListener("keydown",this._boundKeydownListener),this.modeless||this._addGlobalListeners()):t&&(this.focusTrap&&this.__focusTrapController.releaseFocus(),this._animatedClosing(),document.removeEventListener("keydown",this._boundKeydownListener),this.modeless||this._removeGlobalListeners())}_hiddenChanged(e){e&&this.hasAttribute("closing")&&this._flushAnimation("closing")}_shouldAnimate(){const e=getComputedStyle(this).getPropertyValue("animation-name");return!("none"===getComputedStyle(this).getPropertyValue("display"))&&e&&"none"!==e}_enqueueAnimation(e,t){const i=`__${e}Handler`,s=e=>{e&&e.target!==this||(t(),this.removeEventListener("animationend",s),delete this[i])};this[i]=s,this.addEventListener("animationend",s)}_flushAnimation(e){const t=`__${e}Handler`;"function"==typeof this[t]&&this[t]()}_animatedOpening(){this.parentNode===document.body&&this.hasAttribute("closing")&&this._flushAnimation("closing"),this._attachOverlay(),this.modeless||this._enterModalState(),this.setAttribute("opening",""),this._shouldAnimate()?this._enqueueAnimation("opening",(()=>{this._finishOpening()})):this._finishOpening()}_attachOverlay(){this._placeholder=document.createComment("vaadin-overlay-placeholder"),this.parentNode.insertBefore(this._placeholder,this),document.body.appendChild(this),this.bringToFront()}_finishOpening(){document.addEventListener("iron-overlay-canceled",this._boundIronOverlayCanceledListener),this.removeAttribute("opening")}_finishClosing(){document.removeEventListener("iron-overlay-canceled",this._boundIronOverlayCanceledListener),this._detachOverlay(),this.$.overlay.style.removeProperty("pointer-events"),this.removeAttribute("closing")}_animatedClosing(){if(this.hasAttribute("opening")&&this._flushAnimation("opening"),this._placeholder){this._exitModalState();const e=this.restoreFocusNode||this.__restoreFocusNode;if(this.restoreFocusOnClose&&e){const t=this._getActiveElement();(t===document.body||this._deepContains(t))&&setTimeout((()=>e.focus())),this.__restoreFocusNode=null}this.setAttribute("closing",""),this.dispatchEvent(new CustomEvent("vaadin-overlay-closing")),this._shouldAnimate()?this._enqueueAnimation("closing",(()=>{this._finishClosing()})):this._finishClosing()}}_detachOverlay(){this._placeholder.parentNode.insertBefore(this,this._placeholder),this._placeholder.parentNode.removeChild(this._placeholder)}static get __attachedInstances(){return Array.from(document.body.children).filter((e=>e instanceof D&&!e.hasAttribute("closing"))).sort(((e,t)=>e.__zIndex-t.__zIndex||0))}get _last(){return this===D.__attachedInstances.pop()}_modelessChanged(e){e?(this._removeGlobalListeners(),this._exitModalState()):this.opened&&(this._addGlobalListeners(),this._enterModalState())}_addGlobalListeners(){document.addEventListener("mousedown",this._boundMouseDownListener),document.addEventListener("mouseup",this._boundMouseUpListener),document.documentElement.addEventListener("click",this._boundOutsideClickListener,!0)}_enterModalState(){"none"!==document.body.style.pointerEvents&&(this._previousDocumentPointerEvents=document.body.style.pointerEvents,document.body.style.pointerEvents="none"),D.__attachedInstances.forEach((e=>{e!==this&&(e.shadowRoot.querySelector('[part="overlay"]').style.pointerEvents="none")}))}_removeGlobalListeners(){document.removeEventListener("mousedown",this._boundMouseDownListener),document.removeEventListener("mouseup",this._boundMouseUpListener),document.documentElement.removeEventListener("click",this._boundOutsideClickListener,!0)}_exitModalState(){void 0!==this._previousDocumentPointerEvents&&(document.body.style.pointerEvents=this._previousDocumentPointerEvents,delete this._previousDocumentPointerEvents);const e=D.__attachedInstances;let t;for(;(t=e.pop())&&(t===this||(t.shadowRoot.querySelector('[part="overlay"]').style.removeProperty("pointer-events"),t.modeless)););}_removeOldContent(){this.content&&this._contentNodes&&(this._observer.disconnect(),this._contentNodes.forEach((e=>{e.parentNode===this.content&&this.content.removeChild(e)})),this._originalContentPart&&(this.$.content.parentNode.replaceChild(this._originalContentPart,this.$.content),this.$.content=this._originalContentPart,this._originalContentPart=void 0),this._observer.connect(),this._contentNodes=void 0,this.content=void 0)}_stampOverlayTemplate(e){this._removeOldContent(),e._Templatizer||(e._Templatizer=(0,p.Uv)(e,this,{forwardHostProp(e,t){this._instance&&this._instance.forwardHostProp(e,t)}})),this._instance=new e._Templatizer({}),this._contentNodes=Array.from(this._instance.root.childNodes);const t=e._templateRoot||(e._templateRoot=e.getRootNode());if(t!==document){this.$.content.shadowRoot||this.$.content.attachShadow({mode:"open"});let e=Array.from(t.querySelectorAll("style")).reduce(((e,t)=>e+t.textContent),"");if(e=e.replace(/:host/g,":host-nomatch"),e){const t=document.createElement("style");t.textContent=e,this.$.content.shadowRoot.appendChild(t),this._contentNodes.unshift(t)}this.$.content.shadowRoot.appendChild(this._instance.root),this.content=this.$.content.shadowRoot}else this.appendChild(this._instance.root),this.content=this}_removeNewRendererOrTemplate(e,t,i,s){e!==t?this.template=void 0:i!==s&&(this.renderer=void 0)}_templateOrRendererChanged(e,t,i,s,o){if(e&&t)throw this._removeNewRendererOrTemplate(e,this._oldTemplate,t,this._oldRenderer),new Error("You should only use either a renderer or a template for overlay content");const r=this._oldOwner!==i||this._oldModel!==s;this._oldModel=s,this._oldOwner=i;const n=this._oldTemplate!==e;this._oldTemplate=e;const a=this._oldRenderer!==t;this._oldRenderer=t;const l=this._oldOpened!==o;this._oldOpened=o,a&&(this.content=this,this.content.innerHTML="",delete this.content._$litPart$),e&&n?this._stampOverlayTemplate(e):t&&(a||l||r)&&o&&this.requestContentUpdate()}_getActiveElement(){let e=document.activeElement||document.body;for(;e.shadowRoot&&e.shadowRoot.activeElement;)e=e.shadowRoot.activeElement;return e}_deepContains(e){if(this.contains(e))return!0;let t=e;const i=e.ownerDocument;for(;t&&t!==i&&t!==this;)t=t.parentNode||t.host;return t===this}bringToFront(){let e="";const t=D.__attachedInstances.filter((e=>e!==this)).pop();if(t){e=t.__zIndex+1}this.style.zIndex=e,this.__zIndex=e||parseFloat(getComputedStyle(this).zIndex)}}customElements.define(D.is,D);const H=o.iv`
  [part~='loader'] {
    height: 2px;
    background: var(--material-background-color)
      linear-gradient(
        90deg,
        transparent 0%,
        transparent 20%,
        var(--material-primary-color) 20%,
        var(--material-primary-color) 40%,
        transparent 40%,
        transparent 60%,
        var(--material-primary-color) 60%,
        var(--material-primary-color) 80%,
        transparent 80%,
        transparent 100%
      )
      0 0 / 400% 100% repeat-x;
    opacity: 0;
  }

  :host(:not([loading])) [part~='loader'] {
    display: none;
  }

  :host([loading]) [part='loader'] {
    animation: 3s linear infinite material-loader-progress, 0.3s 0.1s both material-loader-fade-in;
  }

  [part='loader']::before {
    content: '';
    display: block;
    height: 100%;
    opacity: 0.16;
    background: var(--material-primary-color);
  }

  @keyframes material-loader-fade-in {
    0% {
      opacity: 0;
    }

    100% {
      opacity: 1;
    }
  }

  @keyframes material-loader-progress {
    0% {
      background-position: 0 0;
      background-size: 300% 100%;
    }

    33% {
      background-position: -100% 0;
      background-size: 400% 100%;
    }

    67% {
      background-position: -200% 0;
      background-size: 250% 100%;
    }

    100% {
      background-position: -300% 0;
      background-size: 300% 100%;
    }
  }

  /* RTL specific styles */

  @keyframes material-loader-progress-rtl {
    0% {
      background-position: 100% 0;
      background-size: 300% 100%;
    }

    33% {
      background-position: 200% 0;
      background-size: 400% 100%;
    }

    67% {
      background-position: 300% 0;
      background-size: 250% 100%;
    }

    100% {
      background-position: 400% 0;
      background-size: 300% 100%;
    }
  }

  :host([loading][dir='rtl']) [part='loader'] {
    animation: 3s linear infinite material-loader-progress-rtl, 0.3s 0.1s both material-loader-fade-in;
  }
`,F=c;(0,o.hC)("",F,{moduleId:"material-menu-overlay"});const M=o.iv`
  :host {
    --_vaadin-combo-box-items-container-border-width: 8px 0;
    --_vaadin-combo-box-items-container-border-style: solid;
    --_vaadin-combo-box-items-container-border-color: transparent;
  }

  [part='overlay'] {
    position: relative;
    overflow: visible;
    border-top-left-radius: 0;
    border-top-right-radius: 0;
  }

  [part='content'] {
    padding: 0;
  }

  [part~='loader'] {
    position: absolute;
    z-index: 1;
    top: -2px;
    left: 0;
    right: 0;
  }
`;(0,o.hC)("vaadin-combo-box-overlay",[F,M,H],{moduleId:"material-combo-box-overlay"});const $=o.iv`
  :host {
    display: flex;
    align-items: center;
    box-sizing: border-box;
    min-height: 36px;
    padding: 8px 32px 8px 10px;
    overflow: hidden;
    font-family: var(--material-font-family);
    font-size: var(--material-small-font-size);
    line-height: 24px;
  }

  /* It's the list-box's responsibility to add the focus style */
  :host([focused]) {
    outline: none;
  }

  /* Checkmark */
  [part='checkmark']::before {
    display: var(--_material-item-selected-icon-display, none);
    content: '';
    font-family: material-icons;
    font-size: 24px;
    line-height: 1;
    font-weight: 400;
    width: 24px;
    text-align: center;
    margin-right: 10px;
    color: var(--material-secondary-text-color);
    flex: none;
  }

  :host([selected]) [part='checkmark']::before {
    content: var(--material-icons-check);
  }

  @media (any-hover: hover) {
    :host(:hover:not([disabled])) {
      background-color: var(--material-secondary-background-color);
    }

    :host([focused]:not([disabled])) {
      background-color: var(--material-divider-color);
    }
  }

  /* Disabled */
  :host([disabled]) {
    color: var(--material-disabled-text-color);
    cursor: default;
    pointer-events: none;
  }

  /* RTL specific styles */
  :host([dir='rtl']) {
    padding: 8px 10px 8px 32px;
  }

  :host([dir='rtl']) [part='checkmark']::before {
    margin-right: 0;
    margin-left: 10px;
  }
`;(0,o.hC)("vaadin-item",$,{moduleId:"material-item"});const q=o.iv`
  :host {
    cursor: pointer;
    -webkit-tap-highlight-color: transparent;
    padding: 4px 10px;
    --_material-item-selected-icon-display: block;
  }
`;(0,o.hC)("vaadin-combo-box-item",[$,q],{moduleId:"material-combo-box-item"});class W extends((0,o.Tb)(k(m.H3))){static get template(){return m.dy`
      <style>
        :host {
          display: block;
        }

        :host([hidden]) {
          display: none;
        }
      </style>
      <span part="checkmark" aria-hidden="true"></span>
      <div part="content">
        <slot></slot>
      </div>
    `}static get is(){return"vaadin-combo-box-item"}static get properties(){return{index:Number,item:Object,label:String,selected:{type:Boolean,value:!1,reflectToAttribute:!0},focused:{type:Boolean,value:!1,reflectToAttribute:!0},renderer:Function,_oldRenderer:Function}}static get observers(){return["__rendererOrItemChanged(renderer, index, item.*, selected, focused)","__updateLabel(label, renderer)"]}connectedCallback(){super.connectedCallback(),this._comboBox=this.parentNode.comboBox;const e=this._comboBox.getAttribute("dir");e&&this.setAttribute("dir",e)}requestContentUpdate(){if(!this.renderer)return;const e={index:this.index,item:this.item,focused:this.focused,selected:this.selected};this.renderer(this,this._comboBox,e)}__rendererOrItemChanged(e,t,i){void 0!==i&&void 0!==t&&(this._oldRenderer!==e&&(this.innerHTML="",delete this._$litPart$),e&&(this._oldRenderer=e,this.requestContentUpdate()))}__updateLabel(e,t){t||(this.textContent=e)}}customElements.define(W.is,W);const U={start:"top",end:"bottom"},j={start:"left",end:"right"},K=new ResizeObserver((e=>{setTimeout((()=>{e.forEach((e=>{e.target.__overlay&&e.target.__overlay._updatePosition()}))}))})),G=e=>class extends e{static get properties(){return{positionTarget:{type:Object,value:null},horizontalAlign:{type:String,value:"start"},verticalAlign:{type:String,value:"top"},noHorizontalOverlap:{type:Boolean,value:!1},noVerticalOverlap:{type:Boolean,value:!1},requiredVerticalSpace:{type:Number,value:0}}}static get observers(){return["__positionSettingsChanged(horizontalAlign, verticalAlign, noHorizontalOverlap, noVerticalOverlap, requiredVerticalSpace)","__overlayOpenedChanged(opened, positionTarget)"]}constructor(){super(),this.__onScroll=this.__onScroll.bind(this),this._updatePosition=this._updatePosition.bind(this)}connectedCallback(){super.connectedCallback(),this.opened&&this.__addUpdatePositionEventListeners()}disconnectedCallback(){super.disconnectedCallback(),this.__removeUpdatePositionEventListeners()}__addUpdatePositionEventListeners(){window.addEventListener("resize",this._updatePosition),this.__positionTargetAncestorRootNodes=function(e){const t=[];for(;e;){if(e.nodeType===Node.DOCUMENT_NODE){t.push(e);break}e.nodeType!==Node.DOCUMENT_FRAGMENT_NODE?e=e.assignedSlot?e.assignedSlot:e.parentNode:(t.push(e),e=e.host)}return t}(this.positionTarget),this.__positionTargetAncestorRootNodes.forEach((e=>{e.addEventListener("scroll",this.__onScroll,!0)}))}__removeUpdatePositionEventListeners(){window.removeEventListener("resize",this._updatePosition),this.__positionTargetAncestorRootNodes&&(this.__positionTargetAncestorRootNodes.forEach((e=>{e.removeEventListener("scroll",this.__onScroll,!0)})),this.__positionTargetAncestorRootNodes=null)}__overlayOpenedChanged(e,t){if(this.__removeUpdatePositionEventListeners(),t&&(t.__overlay=null,K.unobserve(t),e&&(this.__addUpdatePositionEventListeners(),t.__overlay=this,K.observe(t))),e){const e=getComputedStyle(this);this.__margins||(this.__margins={},["top","bottom","left","right"].forEach((t=>{this.__margins[t]=parseInt(e[t],10)}))),this.setAttribute("dir",e.direction),this._updatePosition(),requestAnimationFrame((()=>this._updatePosition()))}}get __isRTL(){return"rtl"===this.getAttribute("dir")}__positionSettingsChanged(){this._updatePosition()}__onScroll(e){this.contains(e.target)||this._updatePosition()}_updatePosition(){if(!this.positionTarget||!this.opened)return;const e=this.positionTarget.getBoundingClientRect(),t=this.__shouldAlignStartVertically(e);this.style.justifyContent=t?"flex-start":"flex-end";const i=this.__shouldAlignStartHorizontally(e,this.__isRTL),s=!this.__isRTL&&i||this.__isRTL&&!i;this.style.alignItems=s?"flex-start":"flex-end";const o=this.getBoundingClientRect(),r=this.__calculatePositionInOneDimension(e,o,this.noVerticalOverlap,U,this,t),n=this.__calculatePositionInOneDimension(e,o,this.noHorizontalOverlap,j,this,i);Object.assign(this.style,r,n),this.toggleAttribute("bottom-aligned",!t),this.toggleAttribute("top-aligned",t),this.toggleAttribute("end-aligned",!s),this.toggleAttribute("start-aligned",s)}__shouldAlignStartHorizontally(e,t){const i=Math.max(this.__oldContentWidth||0,this.$.overlay.offsetWidth);this.__oldContentWidth=this.$.overlay.offsetWidth;const s=Math.min(window.innerWidth,document.documentElement.clientWidth),o=!t&&"start"===this.horizontalAlign||t&&"end"===this.horizontalAlign;return this.__shouldAlignStart(e,i,s,this.__margins,o,this.noHorizontalOverlap,j)}__shouldAlignStartVertically(e){const t=this.requiredVerticalSpace||Math.max(this.__oldContentHeight||0,this.$.overlay.offsetHeight);this.__oldContentHeight=this.$.overlay.offsetHeight;const i=Math.min(window.innerHeight,document.documentElement.clientHeight),s="top"===this.verticalAlign;return this.__shouldAlignStart(e,t,i,this.__margins,s,this.noVerticalOverlap,U)}__shouldAlignStart(e,t,i,s,o,r,n){const a=i-e[r?n.end:n.start]-s[n.end],l=e[r?n.start:n.end]-s[n.start],h=o?a:l;return o===(h>(o?l:a)||h>t)}__adjustBottomProperty(e,t,i){let s;if(e===t.end){if(t.end===U.end){const e=Math.min(window.innerHeight,document.documentElement.clientHeight);if(i>e&&this.__oldViewportHeight){s=i-(this.__oldViewportHeight-e)}this.__oldViewportHeight=e}if(t.end===j.end){const e=Math.min(window.innerWidth,document.documentElement.clientWidth);if(i>e&&this.__oldViewportWidth){s=i-(this.__oldViewportWidth-e)}this.__oldViewportWidth=e}}return s}__calculatePositionInOneDimension(e,t,i,s,o,r){const n=r?s.start:s.end,a=r?s.end:s.start,l=parseFloat(o.style[n]||getComputedStyle(o)[n]),h=this.__adjustBottomProperty(n,s,l),d=t[r?s.start:s.end]-e[i===r?s.end:s.start];return{[n]:h?`${h}px`:`${l+d*(r?-1:1)}px`,[a]:""}}};let Y;(0,o.hC)("vaadin-combo-box-overlay",o.iv`
    #overlay {
      width: var(--vaadin-combo-box-overlay-width, var(--_vaadin-combo-box-overlay-default-width, auto));
    }

    [part='content'] {
      display: flex;
      flex-direction: column;
      height: 100%;
    }
  `,{moduleId:"vaadin-combo-box-overlay-styles"});class X extends(G(D)){static get is(){return"vaadin-combo-box-overlay"}static get template(){return Y||(Y=super.template.cloneNode(!0),Y.content.querySelector('[part~="overlay"]').removeAttribute("tabindex")),Y}static get observers(){return["_setOverlayWidth(positionTarget, opened)"]}connectedCallback(){super.connectedCallback();const e=this._comboBox,t=e&&e.getAttribute("dir");t&&this.setAttribute("dir",t)}ready(){super.ready();const e=document.createElement("div");e.setAttribute("part","loader");const t=this.shadowRoot.querySelector('[part~="content"]');t.parentNode.insertBefore(e,t),this.requiredVerticalSpace=200}_outsideClickListener(e){const t=e.composedPath();t.includes(this.positionTarget)||t.includes(this)||this.close()}_setOverlayWidth(e,t){if(e&&t){const t=this.localName;this.style.setProperty(`--_${t}-default-width`,`${e.clientWidth}px`);const i=getComputedStyle(this._comboBox).getPropertyValue(`--${t}-width`);""===i?this.style.removeProperty(`--${t}-width`):this.style.setProperty(`--${t}-width`,i),this._updatePosition()}}}customElements.define(X.is,X);let Q=0;let Z=0,J=0;const ee=[];let te=0,ie=!1;const se=document.createTextNode("");new window.MutationObserver((function(){ie=!1;const e=ee.length;for(let t=0;t<e;t++){const e=ee[t];if(e)try{e()}catch(e){setTimeout((()=>{throw e}))}}ee.splice(0,e),J+=e})).observe(se,{characterData:!0});const oe={after:e=>({run:t=>window.setTimeout(t,e),cancel(e){window.clearTimeout(e)}}),run:(e,t)=>window.setTimeout(e,t),cancel(e){window.clearTimeout(e)}},re={run:e=>window.requestAnimationFrame(e),cancel(e){window.cancelAnimationFrame(e)}},ne={run:e=>window.requestIdleCallback?window.requestIdleCallback(e):window.setTimeout(e,16),cancel(e){window.cancelIdleCallback?window.cancelIdleCallback(e):window.clearTimeout(e)}},ae={run(e){ie||(ie=!0,se.textContent=te,te+=1),ee.push(e);const t=Z;return Z+=1,t},cancel(e){const t=e-J;if(t>=0){if(!ee[t])throw new Error(`invalid async handle: ${e}`);ee[t]=null}}};class le{static debounce(e,t,i){return e instanceof le?e._cancelAsync():e=new le,e.setConfig(t,i),e}constructor(){this._asyncModule=null,this._callback=null,this._timer=null}setConfig(e,t){this._asyncModule=e,this._callback=t,this._timer=this._asyncModule.run((()=>{this._timer=null,he.delete(this),this._callback()}))}cancel(){this.isActive()&&(this._cancelAsync(),he.delete(this))}_cancelAsync(){this.isActive()&&(this._asyncModule.cancel(this._timer),this._timer=null)}flush(){this.isActive()&&(this.cancel(),this._callback())}isActive(){return null!=this._timer}}let he=new Set;function de(){const e=Boolean(he.size);return he.forEach((e=>{try{e.flush()}catch(e){setTimeout((()=>{throw e}))}})),e}const ce=()=>{let e;do{e=de()}while(e)},ue=navigator.userAgent.match(/iP(?:hone|ad;(?: U;)? CPU) OS (\d+)/),_e=ue&&ue[1]>=8,pe={_ratio:.5,_scrollerPaddingTop:0,_scrollPosition:0,_physicalSize:0,_physicalAverage:0,_physicalAverageCount:0,_physicalTop:0,_virtualCount:0,_estScrollHeight:0,_scrollHeight:0,_viewportHeight:0,_viewportWidth:0,_physicalItems:null,_physicalSizes:null,_firstVisibleIndexVal:null,_lastVisibleIndexVal:null,_maxPages:2,_templateCost:0,get _physicalBottom(){return this._physicalTop+this._physicalSize},get _scrollBottom(){return this._scrollPosition+this._viewportHeight},get _virtualEnd(){return this._virtualStart+this._physicalCount-1},get _hiddenContentSize(){return this._physicalSize-this._viewportHeight},get _maxScrollTop(){return this._estScrollHeight-this._viewportHeight+this._scrollOffset},get _maxVirtualStart(){const e=this._virtualCount;return Math.max(0,e-this._physicalCount)},get _virtualStart(){return this._virtualStartVal||0},set _virtualStart(e){e=this._clamp(e,0,this._maxVirtualStart),this._virtualStartVal=e},get _physicalStart(){return this._physicalStartVal||0},set _physicalStart(e){(e%=this._physicalCount)<0&&(e=this._physicalCount+e),this._physicalStartVal=e},get _physicalEnd(){return(this._physicalStart+this._physicalCount-1)%this._physicalCount},get _physicalCount(){return this._physicalCountVal||0},set _physicalCount(e){this._physicalCountVal=e},get _optPhysicalSize(){return 0===this._viewportHeight?1/0:this._viewportHeight*this._maxPages},get _isVisible(){return Boolean(this.offsetWidth||this.offsetHeight)},get firstVisibleIndex(){let e=this._firstVisibleIndexVal;if(null==e){let t=this._physicalTop+this._scrollOffset;e=this._iterateItems(((e,i)=>{if(t+=this._getPhysicalSizeIncrement(e),t>this._scrollPosition)return i}))||0,this._firstVisibleIndexVal=e}return e},get lastVisibleIndex(){let e=this._lastVisibleIndexVal;if(null==e){let t=this._physicalTop+this._scrollOffset;this._iterateItems(((i,s)=>{t<this._scrollBottom&&(e=s),t+=this._getPhysicalSizeIncrement(i)})),this._lastVisibleIndexVal=e}return e},get _scrollOffset(){return this._scrollerPaddingTop+this.scrollOffset},_scrollHandler(){const e=Math.max(0,Math.min(this._maxScrollTop,this._scrollTop));let t=e-this._scrollPosition;const i=t>=0;if(this._scrollPosition=e,this._firstVisibleIndexVal=null,this._lastVisibleIndexVal=null,Math.abs(t)>this._physicalSize&&this._physicalSize>0){t-=this._scrollOffset;const e=Math.round(t/this._physicalAverage);this._virtualStart+=e,this._physicalStart+=e,this._physicalTop=Math.min(Math.floor(this._virtualStart)*this._physicalAverage,this._scrollPosition),this._update()}else if(this._physicalCount>0){const e=this._getReusables(i);i?(this._physicalTop=e.physicalTop,this._virtualStart+=e.indexes.length,this._physicalStart+=e.indexes.length):(this._virtualStart-=e.indexes.length,this._physicalStart-=e.indexes.length),this._update(e.indexes,i?null:e.indexes),this._debounce("_increasePoolIfNeeded",this._increasePoolIfNeeded.bind(this,0),ae)}},_getReusables(e){let t,i,s;const o=[],r=this._hiddenContentSize*this._ratio,n=this._virtualStart,a=this._virtualEnd,l=this._physicalCount;let h=this._physicalTop+this._scrollOffset;const d=this._physicalBottom+this._scrollOffset,c=this._scrollPosition,u=this._scrollBottom;for(e?(t=this._physicalStart,i=c-h):(t=this._physicalEnd,i=d-u);s=this._getPhysicalSizeIncrement(t),i-=s,!(o.length>=l||i<=r);)if(e){if(a+o.length+1>=this._virtualCount)break;if(h+s>=c-this._scrollOffset)break;o.push(t),h+=s,t=(t+1)%l}else{if(n-o.length<=0)break;if(h+this._physicalSize-s<=u)break;o.push(t),h-=s,t=0===t?l-1:t-1}return{indexes:o,physicalTop:h-this._scrollOffset}},_update(e,t){if(!(e&&0===e.length||0===this._physicalCount)){if(this._assignModels(e),this._updateMetrics(e),t)for(;t.length;){const e=t.pop();this._physicalTop-=this._getPhysicalSizeIncrement(e)}this._positionItems(),this._updateScrollerSize()}},_isClientFull(){return 0!==this._scrollBottom&&this._physicalBottom-1>=this._scrollBottom&&this._physicalTop<=this._scrollPosition},_increasePoolIfNeeded(e){const t=this._clamp(this._physicalCount+e,3,this._virtualCount-this._virtualStart)-this._physicalCount;let i=Math.round(.5*this._physicalCount);if(!(t<0)){if(t>0){const e=window.performance.now();[].push.apply(this._physicalItems,this._createPool(t));for(let e=0;e<t;e++)this._physicalSizes.push(0);this._physicalCount+=t,this._physicalStart>this._physicalEnd&&this._isIndexRendered(this._focusedVirtualIndex)&&this._getPhysicalIndex(this._focusedVirtualIndex)<this._physicalEnd&&(this._physicalStart+=t),this._update(),this._templateCost=(window.performance.now()-e)/t,i=Math.round(.5*this._physicalCount)}this._virtualEnd>=this._virtualCount-1||0===i||(this._isClientFull()?this._physicalSize<this._optPhysicalSize&&this._debounce("_increasePoolIfNeeded",this._increasePoolIfNeeded.bind(this,this._clamp(Math.round(50/this._templateCost),1,i)),ne):this._debounce("_increasePoolIfNeeded",this._increasePoolIfNeeded.bind(this,i),ae))}},_render(){if(this.isAttached&&this._isVisible)if(0!==this._physicalCount){const e=this._getReusables(!0);this._physicalTop=e.physicalTop,this._virtualStart+=e.indexes.length,this._physicalStart+=e.indexes.length,this._update(e.indexes),this._update(),this._increasePoolIfNeeded(0)}else this._virtualCount>0&&(this.updateViewportBoundaries(),this._increasePoolIfNeeded(3))},_itemsChanged(e){"items"===e.path&&(this._virtualStart=0,this._physicalTop=0,this._virtualCount=this.items?this.items.length:0,this._physicalIndexForKey={},this._firstVisibleIndexVal=null,this._lastVisibleIndexVal=null,this._physicalCount=this._physicalCount||0,this._physicalItems=this._physicalItems||[],this._physicalSizes=this._physicalSizes||[],this._physicalStart=0,this._scrollTop>this._scrollOffset&&this._resetScrollPosition(0),this._debounce("_render",this._render,re))},_iterateItems(e,t){let i,s,o,r;if(2===arguments.length&&t){for(r=0;r<t.length;r++)if(i=t[r],s=this._computeVidx(i),null!=(o=e.call(this,i,s)))return o}else{for(i=this._physicalStart,s=this._virtualStart;i<this._physicalCount;i++,s++)if(null!=(o=e.call(this,i,s)))return o;for(i=0;i<this._physicalStart;i++,s++)if(null!=(o=e.call(this,i,s)))return o}},_computeVidx(e){return e>=this._physicalStart?this._virtualStart+(e-this._physicalStart):this._virtualStart+(this._physicalCount-this._physicalStart)+e},_positionItems(){this._adjustScrollPosition();let e=this._physicalTop;this._iterateItems((t=>{this.translate3d(0,`${e}px`,0,this._physicalItems[t]),e+=this._physicalSizes[t]}))},_getPhysicalSizeIncrement(e){return this._physicalSizes[e]},_adjustScrollPosition(){const e=0===this._virtualStart?this._physicalTop:Math.min(this._scrollPosition+this._physicalTop,0);if(0!==e){this._physicalTop-=e;const t=this._scrollPosition;!_e&&t>0&&this._resetScrollPosition(t-e)}},_resetScrollPosition(e){this.scrollTarget&&e>=0&&(this._scrollTop=e,this._scrollPosition=this._scrollTop)},_updateScrollerSize(e){this._estScrollHeight=this._physicalBottom+Math.max(this._virtualCount-this._physicalCount-this._virtualStart,0)*this._physicalAverage,((e=(e=e||0===this._scrollHeight)||this._scrollPosition>=this._estScrollHeight-this._physicalSize)||Math.abs(this._estScrollHeight-this._scrollHeight)>=this._viewportHeight)&&(this.$.items.style.height=`${this._estScrollHeight}px`,this._scrollHeight=this._estScrollHeight)},scrollToIndex(e){if("number"!=typeof e||e<0||e>this.items.length-1)return;if(ce(),0===this._physicalCount)return;e=this._clamp(e,0,this._virtualCount-1),(!this._isIndexRendered(e)||e>=this._maxVirtualStart)&&(this._virtualStart=e-1),this._assignModels(),this._updateMetrics(),this._physicalTop=this._virtualStart*this._physicalAverage;let t=this._physicalStart,i=this._virtualStart,s=0;const o=this._hiddenContentSize;for(;i<e&&s<=o;)s+=this._getPhysicalSizeIncrement(t),t=(t+1)%this._physicalCount,i+=1;this._updateScrollerSize(!0),this._positionItems(),this._resetScrollPosition(this._physicalTop+this._scrollOffset+s),this._increasePoolIfNeeded(0),this._firstVisibleIndexVal=null,this._lastVisibleIndexVal=null},_resetAverage(){this._physicalAverage=0,this._physicalAverageCount=0},_resizeHandler(){this._debounce("_render",(()=>{this._firstVisibleIndexVal=null,this._lastVisibleIndexVal=null,this._isVisible?(this.updateViewportBoundaries(),this.toggleScrollListener(!0),this._resetAverage(),this._render()):this.toggleScrollListener(!1)}),re)},_isIndexRendered(e){return e>=this._virtualStart&&e<=this._virtualEnd},_getPhysicalIndex(e){return(this._physicalStart+(e-this._virtualStart))%this._physicalCount},_clamp:(e,t,i)=>Math.min(i,Math.max(t,e)),_debounce(e,t,i){var s;this._debouncers=this._debouncers||{},this._debouncers[e]=le.debounce(this._debouncers[e],i,t.bind(this)),s=this._debouncers[e],he.add(s)}},me=1e3;class ge{constructor({createElements:e,updateElement:t,scrollTarget:i,scrollContainer:s,elementsContainer:o,reorderElements:r}){this.isAttached=!0,this._vidxOffset=0,this.createElements=e,this.updateElement=t,this.scrollTarget=i,this.scrollContainer=s,this.elementsContainer=o||s,this.reorderElements=r,this._maxPages=1.3,this.__placeholderHeight=200,this.__elementHeightQueue=Array(10),this.timeouts={SCROLL_REORDER:500,IGNORE_WHEEL:500,FIX_INVALID_ITEM_POSITIONING:100},this.__resizeObserver=new ResizeObserver((()=>this._resizeHandler())),"visible"===getComputedStyle(this.scrollTarget).overflow&&(this.scrollTarget.style.overflow="auto"),"static"===getComputedStyle(this.scrollContainer).position&&(this.scrollContainer.style.position="relative"),this.__resizeObserver.observe(this.scrollTarget),this.scrollTarget.addEventListener("scroll",(()=>this._scrollHandler())),this._scrollLineHeight=this._getScrollLineHeight(),this.scrollTarget.addEventListener("wheel",(e=>this.__onWheel(e))),this.reorderElements&&(this.scrollTarget.addEventListener("mousedown",(()=>{this.__mouseDown=!0})),this.scrollTarget.addEventListener("mouseup",(()=>{this.__mouseDown=!1,this.__pendingReorder&&this.__reorderElements()})))}get scrollOffset(){return 0}get adjustedFirstVisibleIndex(){return this.firstVisibleIndex+this._vidxOffset}get adjustedLastVisibleIndex(){return this.lastVisibleIndex+this._vidxOffset}scrollToIndex(e){if("number"!=typeof e||isNaN(e)||0===this.size||!this.scrollTarget.offsetHeight)return;e=this._clamp(e,0,this.size-1);const t=this.__getVisibleElements().length;let i=Math.floor(e/this.size*this._virtualCount);this._virtualCount-i<t?(i=this._virtualCount-(this.size-e),this._vidxOffset=this.size-this._virtualCount):i<t?e<me?(i=e,this._vidxOffset=0):(i=me,this._vidxOffset=e-i):this._vidxOffset=e-i,this.__skipNextVirtualIndexAdjust=!0,super.scrollToIndex(i),this.adjustedFirstVisibleIndex!==e&&this._scrollTop<this._maxScrollTop&&!this.grid&&(this._scrollTop-=this.__getIndexScrollOffset(e)||0),this._scrollHandler()}flush(){0!==this.scrollTarget.offsetHeight&&(this._resizeHandler(),ce(),this._scrollHandler(),this.__fixInvalidItemPositioningDebouncer&&this.__fixInvalidItemPositioningDebouncer.flush(),this.__scrollReorderDebouncer&&this.__scrollReorderDebouncer.flush(),this.__debouncerWheelAnimationFrame&&this.__debouncerWheelAnimationFrame.flush())}update(e=0,t=this.size-1){this.__getVisibleElements().forEach((i=>{i.__virtualIndex>=e&&i.__virtualIndex<=t&&this.__updateElement(i,i.__virtualIndex,!0)}))}_updateMetrics(e){ce();let t=0,i=0;const s=this._physicalAverageCount,o=this._physicalAverage;this._iterateItems(((e,s)=>{i+=this._physicalSizes[e],this._physicalSizes[e]=Math.ceil(this.__getBorderBoxHeight(this._physicalItems[e])),t+=this._physicalSizes[e],this._physicalAverageCount+=this._physicalSizes[e]?1:0}),e),this._physicalSize=this._physicalSize+t-i,this._physicalAverageCount!==s&&(this._physicalAverage=Math.round((o*s+t)/this._physicalAverageCount))}__getBorderBoxHeight(e){const t=getComputedStyle(e),i=parseFloat(t.height)||0;if("border-box"===t.boxSizing)return i;return i+(parseFloat(t.paddingBottom)||0)+(parseFloat(t.paddingTop)||0)+(parseFloat(t.borderBottomWidth)||0)+(parseFloat(t.borderTopWidth)||0)}__updateElement(e,t,i){e.style.paddingTop&&(e.style.paddingTop=""),this.__preventElementUpdates||e.__lastUpdatedIndex===t&&!i||(this.updateElement(e,t),e.__lastUpdatedIndex=t);const s=e.offsetHeight;if(0===s)e.style.paddingTop=`${this.__placeholderHeight}px`,requestAnimationFrame((()=>this._resizeHandler()));else{this.__elementHeightQueue.push(s),this.__elementHeightQueue.shift();const e=this.__elementHeightQueue.filter((e=>void 0!==e));this.__placeholderHeight=Math.round(e.reduce(((e,t)=>e+t),0)/e.length)}}__getIndexScrollOffset(e){const t=this.__getVisibleElements().find((t=>t.__virtualIndex===e));return t?this.scrollTarget.getBoundingClientRect().top-t.getBoundingClientRect().top:void 0}get size(){return this.__size}set size(e){if(e===this.size)return;let t,i;if(this.__fixInvalidItemPositioningDebouncer&&this.__fixInvalidItemPositioningDebouncer.cancel(),this._debouncers&&this._debouncers._increasePoolIfNeeded&&this._debouncers._increasePoolIfNeeded.cancel(),this.__preventElementUpdates=!0,e>0&&(t=this.adjustedFirstVisibleIndex,i=this.__getIndexScrollOffset(t)),this.__size=e,this._itemsChanged({path:"items"}),ce(),e>0){t=Math.min(t,e-1),this.scrollToIndex(t);const s=this.__getIndexScrollOffset(t);void 0!==i&&void 0!==s&&(this._scrollTop+=i-s)}this.elementsContainer.children.length||requestAnimationFrame((()=>this._resizeHandler())),this.__preventElementUpdates=!1,this._resizeHandler(),ce()}get _scrollTop(){return this.scrollTarget.scrollTop}set _scrollTop(e){this.scrollTarget.scrollTop=e}get items(){return{length:Math.min(this.size,1e5)}}get offsetHeight(){return this.scrollTarget.offsetHeight}get $(){return{items:this.scrollContainer}}updateViewportBoundaries(){const e=window.getComputedStyle(this.scrollTarget);this._scrollerPaddingTop=this.scrollTarget===this?0:parseInt(e["padding-top"],10),this._isRTL=Boolean("rtl"===e.direction),this._viewportWidth=this.elementsContainer.offsetWidth,this._viewportHeight=this.scrollTarget.offsetHeight,this._scrollPageHeight=this._viewportHeight-this._scrollLineHeight,this.grid&&this._updateGridMetrics()}setAttribute(){}_createPool(e){const t=this.createElements(e),i=document.createDocumentFragment();return t.forEach((e=>{e.style.position="absolute",i.appendChild(e),this.__resizeObserver.observe(e)})),this.elementsContainer.appendChild(i),t}_assignModels(e){this._iterateItems(((e,t)=>{const i=this._physicalItems[e];i.hidden=t>=this.size,i.hidden?delete i.__lastUpdatedIndex:(i.__virtualIndex=t+(this._vidxOffset||0),this.__updateElement(i,i.__virtualIndex))}),e)}_isClientFull(){return setTimeout((()=>{this.__clientFull=!0})),this.__clientFull||super._isClientFull()}translate3d(e,t,i,s){s.style.transform=`translateY(${t})`}toggleScrollListener(){}_scrollHandler(){this._adjustVirtualIndexOffset(this._scrollTop-(this.__previousScrollTop||0));const e=this.scrollTarget.scrollTop-this._scrollPosition;if(super._scrollHandler(),0!==this._physicalCount){const t=e>=0,i=this._getReusables(!t);i.indexes.length&&(this._physicalTop=i.physicalTop,t?(this._virtualStart-=i.indexes.length,this._physicalStart-=i.indexes.length):(this._virtualStart+=i.indexes.length,this._physicalStart+=i.indexes.length),this._resizeHandler())}e&&(this.__fixInvalidItemPositioningDebouncer=le.debounce(this.__fixInvalidItemPositioningDebouncer,oe.after(this.timeouts.FIX_INVALID_ITEM_POSITIONING),(()=>this.__fixInvalidItemPositioning()))),this.reorderElements&&(this.__scrollReorderDebouncer=le.debounce(this.__scrollReorderDebouncer,oe.after(this.timeouts.SCROLL_REORDER),(()=>this.__reorderElements()))),this.__previousScrollTop=this._scrollTop,0===this._scrollTop&&0!==this.firstVisibleIndex&&Math.abs(e)>0&&this.scrollToIndex(0)}__fixInvalidItemPositioning(){if(!this.scrollTarget.isConnected)return;const e=this._physicalTop>this._scrollTop,t=this._physicalBottom<this._scrollBottom,i=0===this.adjustedFirstVisibleIndex,s=this.adjustedLastVisibleIndex===this.size-1;if(e&&!i||t&&!s){const e=t,i=this._ratio;this._ratio=0,this._scrollPosition=this._scrollTop+(e?-1:1),this._scrollHandler(),this._ratio=i}}__onWheel(e){if(e.ctrlKey||this._hasScrolledAncestor(e.target,e.deltaX,e.deltaY))return;let t=e.deltaY;if(e.deltaMode===WheelEvent.DOM_DELTA_LINE?t*=this._scrollLineHeight:e.deltaMode===WheelEvent.DOM_DELTA_PAGE&&(t*=this._scrollPageHeight),this._deltaYAcc=this._deltaYAcc||0,this._wheelAnimationFrame)return this._deltaYAcc+=t,void e.preventDefault();t+=this._deltaYAcc,this._deltaYAcc=0,this._wheelAnimationFrame=!0,this.__debouncerWheelAnimationFrame=le.debounce(this.__debouncerWheelAnimationFrame,re,(()=>{this._wheelAnimationFrame=!1}));const i=Math.abs(e.deltaX)+Math.abs(t);this._canScroll(this.scrollTarget,e.deltaX,t)?(e.preventDefault(),this.scrollTarget.scrollTop+=t,this.scrollTarget.scrollLeft+=e.deltaX,this._hasResidualMomentum=!0,this._ignoreNewWheel=!0,this._debouncerIgnoreNewWheel=le.debounce(this._debouncerIgnoreNewWheel,oe.after(this.timeouts.IGNORE_WHEEL),(()=>{this._ignoreNewWheel=!1}))):this._hasResidualMomentum&&i<=this._previousMomentum||this._ignoreNewWheel?e.preventDefault():i>this._previousMomentum&&(this._hasResidualMomentum=!1),this._previousMomentum=i}_hasScrolledAncestor(e,t,i){return e!==this.scrollTarget&&e!==this.scrollTarget.getRootNode().host&&(!(!this._canScroll(e,t,i)||-1===["auto","scroll"].indexOf(getComputedStyle(e).overflow))||(e!==this&&e.parentElement?this._hasScrolledAncestor(e.parentElement,t,i):void 0))}_canScroll(e,t,i){return i>0&&e.scrollTop<e.scrollHeight-e.offsetHeight||i<0&&e.scrollTop>0||t>0&&e.scrollLeft<e.scrollWidth-e.offsetWidth||t<0&&e.scrollLeft>0}_getScrollLineHeight(){const e=document.createElement("div");e.style.fontSize="initial",e.style.display="none",document.body.appendChild(e);const t=window.getComputedStyle(e).fontSize;return document.body.removeChild(e),t?window.parseInt(t):void 0}__getVisibleElements(){return Array.from(this.elementsContainer.children).filter((e=>!e.hidden))}__reorderElements(){if(this.__mouseDown)return void(this.__pendingReorder=!0);this.__pendingReorder=!1;const e=this._virtualStart+(this._vidxOffset||0),t=this.__getVisibleElements(),i=t.find((e=>e.contains(this.elementsContainer.getRootNode().activeElement)||e.contains(this.scrollTarget.getRootNode().activeElement)))||t[0];if(!i)return;const s=i.__virtualIndex-e,o=t.indexOf(i)-s;if(o>0)for(let e=0;e<o;e++)this.elementsContainer.appendChild(t[e]);else if(o<0)for(let e=t.length+o;e<t.length;e++)this.elementsContainer.insertBefore(t[e],t[0]);if(y){const{transform:e}=this.scrollTarget.style;this.scrollTarget.style.transform="translateZ(0)",setTimeout((()=>{this.scrollTarget.style.transform=e}))}}_adjustVirtualIndexOffset(e){if(this._virtualCount>=this.size)this._vidxOffset=0;else if(this.__skipNextVirtualIndexAdjust)this.__skipNextVirtualIndexAdjust=!1;else if(Math.abs(e)>1e4){const e=this._scrollTop/(this.scrollTarget.scrollHeight-this.scrollTarget.offsetHeight),t=e*this.size;this._vidxOffset=Math.round(t-e*this._virtualCount)}else{const e=this._vidxOffset,t=me,i=100;0===this._scrollTop?(this._vidxOffset=0,e!==this._vidxOffset&&super.scrollToIndex(0)):this.firstVisibleIndex<t&&this._vidxOffset>0&&(this._vidxOffset-=Math.min(this._vidxOffset,i),super.scrollToIndex(this.firstVisibleIndex+(e-this._vidxOffset)));const s=this.size-this._virtualCount;this._scrollTop>=this._maxScrollTop&&this._maxScrollTop>0?(this._vidxOffset=s,e!==this._vidxOffset&&super.scrollToIndex(this._virtualCount-1)):this.firstVisibleIndex>this._virtualCount-t&&this._vidxOffset<s&&(this._vidxOffset+=Math.min(s-this._vidxOffset,i),super.scrollToIndex(this.firstVisibleIndex-(this._vidxOffset-e)))}}}Object.setPrototypeOf(ge.prototype,pe);class ve{constructor(e){this.__adapter=new ge(e)}get size(){return this.__adapter.size}set size(e){this.__adapter.size=e}scrollToIndex(e){this.__adapter.scrollToIndex(e)}update(e=0,t=this.size-1){this.__adapter.update(e,t)}flush(){this.__adapter.flush()}get firstVisibleIndex(){return this.__adapter.adjustedFirstVisibleIndex}get lastVisibleIndex(){return this.__adapter.adjustedLastVisibleIndex}}const be=class{toString(){return""}};class fe extends m.H3{static get is(){return"vaadin-combo-box-scroller"}static get template(){return m.dy`
      <style>
        :host {
          display: block;
          min-height: 1px;
          overflow: auto;

          /* Fixes item background from getting on top of scrollbars on Safari */
          transform: translate3d(0, 0, 0);

          /* Enable momentum scrolling on iOS */
          -webkit-overflow-scrolling: touch;

          /* Fixes scrollbar disappearing when 'Show scroll bars: Always' enabled in Safari */
          box-shadow: 0 0 0 white;
        }

        #selector {
          border-width: var(--_vaadin-combo-box-items-container-border-width);
          border-style: var(--_vaadin-combo-box-items-container-border-style);
          border-color: var(--_vaadin-combo-box-items-container-border-color);
          position: relative;
        }
      </style>
      <div id="selector">
        <slot></slot>
      </div>
    `}static get properties(){return{items:{type:Array,observer:"__itemsChanged"},focusedIndex:{type:Number,observer:"__focusedIndexChanged"},loading:{type:Boolean,observer:"__loadingChanged"},opened:{type:Boolean,observer:"__openedChanged"},selectedItem:{type:Object,observer:"__selectedItemChanged"},itemIdPath:{type:String},comboBox:{type:Object},getItemLabel:{type:Object},renderer:{type:Object,observer:"__rendererChanged"},theme:{type:String}}}constructor(){super(),this.__boundOnItemClick=this.__onItemClick.bind(this)}__openedChanged(e){e&&this.requestContentUpdate()}ready(){super.ready(),this.id=`${this.localName}-${Q++}`,this.__hostTagName=this.constructor.is.replace("-scroller",""),this.setAttribute("role","listbox"),this.addEventListener("click",(e=>e.stopPropagation())),this.__patchWheelOverScrolling(),this.__virtualizer=new ve({createElements:this.__createElements.bind(this),updateElement:this.__updateElement.bind(this),elementsContainer:this,scrollTarget:this,scrollContainer:this.$.selector})}requestContentUpdate(){this.__virtualizer&&this.__virtualizer.update()}scrollIntoView(e){if(!(this.opened&&e>=0))return;const t=this._visibleItemsCount();let i=e;e>this.__virtualizer.lastVisibleIndex-1?(this.__virtualizer.scrollToIndex(e),i=e-t+1):e>this.__virtualizer.firstVisibleIndex&&(i=this.__virtualizer.firstVisibleIndex),this.__virtualizer.scrollToIndex(Math.max(0,i));const s=[...this.children].find((e=>!e.hidden&&e.index===this.__virtualizer.lastVisibleIndex));if(!s||e!==s.index)return;const o=s.getBoundingClientRect(),r=this.getBoundingClientRect(),n=o.bottom-r.bottom+this._viewportTotalPaddingBottom;n>0&&(this.scrollTop+=n)}__getAriaRole(e){return void 0!==e&&"option"}__isItemFocused(e,t){return!this.loading&&e===t}_isItemSelected(e,t,i){return!(e instanceof be)&&(i&&void 0!==e&&void 0!==t?this.get(i,e)===this.get(i,t):e===t)}__itemsChanged(e){this.__virtualizer&&e&&(this.__virtualizer.size=e.length,this.__virtualizer.flush(),this.requestContentUpdate())}__loadingChanged(){this.requestContentUpdate()}__selectedItemChanged(){this.requestContentUpdate()}__focusedIndexChanged(e,t){e!==t&&this.requestContentUpdate(),e>=0&&!this.loading&&this.scrollIntoView(e)}__rendererChanged(e,t){(e||t)&&this.requestContentUpdate()}__createElements(e){return[...Array(e)].map((()=>{const e=document.createElement(`${this.__hostTagName}-item`);return e.addEventListener("click",this.__boundOnItemClick),e.tabIndex="-1",e.style.width="100%",e}))}__updateElement(e,t){const i=this.items[t],s=this.focusedIndex,o=this._isItemSelected(i,this.selectedItem,this.itemIdPath);e.setProperties({item:i,index:t,label:this.getItemLabel(i),selected:o,renderer:this.renderer,focused:this.__isItemFocused(s,t)}),e.id=`${this.__hostTagName}-item-${t}`,e.setAttribute("role",this.__getAriaRole(t)),e.setAttribute("aria-selected",o.toString()),e.setAttribute("aria-posinset",t+1),e.setAttribute("aria-setsize",this.items.length),this.theme?e.setAttribute("theme",this.theme):e.removeAttribute("theme"),i instanceof be&&this.__requestItemByIndex(t)}__onItemClick(e){this.dispatchEvent(new CustomEvent("selection-changed",{detail:{item:e.currentTarget.item}}))}__patchWheelOverScrolling(){this.$.selector.addEventListener("wheel",(e=>{const t=0===this.scrollTop,i=this.scrollHeight-this.scrollTop-this.clientHeight<=1;(t&&e.deltaY<0||i&&e.deltaY>0)&&e.preventDefault()}))}get _viewportTotalPaddingBottom(){if(void 0===this._cachedViewportTotalPaddingBottom){const e=window.getComputedStyle(this.$.selector);this._cachedViewportTotalPaddingBottom=[e.paddingBottom,e.borderBottomWidth].map((e=>parseInt(e,10))).reduce(((e,t)=>e+t))}return this._cachedViewportTotalPaddingBottom}__requestItemByIndex(e){requestAnimationFrame((()=>{this.dispatchEvent(new CustomEvent("index-requested",{detail:{index:e,currentScrollerPos:this._oldScrollerPosition}}))}))}_visibleItemsCount(){this.__virtualizer.scrollToIndex(this.__virtualizer.firstVisibleIndex);return this.__virtualizer.size>0?this.__virtualizer.lastVisibleIndex-this.__virtualizer.firstVisibleIndex+1:0}}customElements.define(fe.is,fe);var ye=i(67130);const xe=(0,I.o)((e=>class extends e{static get properties(){return{invalid:{type:Boolean,reflectToAttribute:!0,notify:!0,value:!1},required:{type:Boolean,reflectToAttribute:!0}}}validate(){const e=this.checkValidity();return this._setInvalid(!e),this.dispatchEvent(new CustomEvent("validated",{detail:{valid:e}})),e}checkValidity(){return!this.required||!!this.value}_setInvalid(e){this._shouldSetInvalid(e)&&(this.invalid=e)}_shouldSetInvalid(e){return!0}})),Ie=e=>class extends e{static get properties(){return{pageSize:{type:Number,value:50,observer:"_pageSizeChanged"},size:{type:Number,observer:"_sizeChanged"},dataProvider:{type:Object,observer:"_dataProviderChanged"},_pendingRequests:{value:()=>({})},__placeHolder:{value:new be},__previousDataProviderFilter:{type:String}}}static get observers(){return["_dataProviderFilterChanged(filter)","_warnDataProviderValue(dataProvider, value)","_ensureFirstPage(opened)"]}ready(){super.ready(),this._scroller.addEventListener("index-requested",(e=>{const t=e.detail.index,i=e.detail.currentScrollerPos,s=Math.floor(1.5*this.pageSize);if(!this._shouldSkipIndex(t,s,i)&&void 0!==t){const e=this._getPageForIndex(t);this._shouldLoadPage(e)&&this._loadPage(e)}}))}_dataProviderFilterChanged(e){void 0!==this.__previousDataProviderFilter||""!==e?this.__previousDataProviderFilter!==e&&(this.__previousDataProviderFilter=e,this._pendingRequests={},this.loading=this._shouldFetchData(),this.size=void 0,this.clearCache()):this.__previousDataProviderFilter=e}_shouldFetchData(){return!!this.dataProvider&&(this.opened||this.filter&&this.filter.length)}_ensureFirstPage(e){e&&this._shouldLoadPage(0)&&this._loadPage(0)}_shouldSkipIndex(e,t,i){return 0!==i&&e>=i-t&&e<=i+t}_shouldLoadPage(e){if(!this.filteredItems||this._forceNextRequest)return this._forceNextRequest=!1,!0;const t=this.filteredItems[e*this.pageSize];return void 0!==t?t instanceof be:void 0===this.size}_loadPage(e){if(this._pendingRequests[e]||!this.dataProvider)return;const t={page:e,pageSize:this.pageSize,filter:this.filter},i=(s,o)=>{if(this._pendingRequests[e]!==i)return;const r=this.filteredItems?[...this.filteredItems]:[];r.splice(t.page*t.pageSize,s.length,...s),this.filteredItems=r,this.opened||this._isInputFocused()||this._commitValue(),void 0!==o&&(this.size=o),delete this._pendingRequests[e],0===Object.keys(this._pendingRequests).length&&(this.loading=!1)};this._pendingRequests[e]=i,this.loading=!0,this.dataProvider(t,i)}_getPageForIndex(e){return Math.floor(e/this.pageSize)}clearCache(){if(!this.dataProvider)return;this._pendingRequests={};const e=[];for(let t=0;t<(this.size||0);t++)e.push(this.__placeHolder);this.filteredItems=e,this._shouldFetchData()?(this._forceNextRequest=!1,this._loadPage(0)):this._forceNextRequest=!0}_sizeChanged(e=0){const t=(this.filteredItems||[]).slice(0,e);for(let i=0;i<e;i++)t[i]=void 0!==t[i]?t[i]:this.__placeHolder;this.filteredItems=t,this._flushPendingRequests(e)}_pageSizeChanged(e,t){if(Math.floor(e)!==e||e<1)throw this.pageSize=t,new Error("`pageSize` value must be an integer > 0");this.clearCache()}_dataProviderChanged(e,t){this._ensureItemsOrDataProvider((()=>{this.dataProvider=t})),this.clearCache()}_ensureItemsOrDataProvider(e){if(void 0!==this.items&&void 0!==this.dataProvider)throw e(),new Error("Using `items` and `dataProvider` together is not supported");this.dataProvider&&!this.filteredItems&&(this.filteredItems=[])}_warnDataProviderValue(e,t){if(e&&""!==t&&(void 0===this.selectedItem||null===this.selectedItem)){const e=this.__getItemIndexByValue(this.filteredItems,t);(e<0||!this._getItemLabel(this.filteredItems[e]))&&console.warn("Warning: unable to determine the label for the provided `value`. Nothing to display in the text field. This usually happens when setting an initial `value` before any items are returned from the `dataProvider` callback. Consider setting `selectedItem` instead of `value`")}}_flushPendingRequests(e){if(this._pendingRequests){const t=Math.ceil(e/this.pageSize),i=Object.keys(this._pendingRequests);for(let s=0;s<i.length;s++){const o=parseInt(i[s]);o>=t&&this._pendingRequests[o]([],e)}}}},Ce=(0,I.o)((e=>class extends e{static get properties(){return{disabled:{type:Boolean,value:!1,observer:"_disabledChanged",reflectToAttribute:!0}}}_disabledChanged(e){this._setAriaDisabled(e)}_setAriaDisabled(e){e?this.setAttribute("aria-disabled","true"):this.removeAttribute("aria-disabled")}click(){this.disabled||super.click()}})),we=(0,I.o)((e=>class extends e{ready(){super.ready(),this.addEventListener("keydown",(e=>{this._onKeyDown(e)})),this.addEventListener("keyup",(e=>{this._onKeyUp(e)}))}_onKeyDown(e){switch(e.key){case"Enter":this._onEnter(e);break;case"Escape":this._onEscape(e)}}_onKeyUp(e){}_onEnter(e){}_onEscape(e){}}));const Ee=(0,I.o)((e=>class extends e{static get properties(){return{inputElement:{type:Object,readOnly:!0,observer:"_inputElementChanged"},type:{type:String,readOnly:!0},value:{type:String,value:"",observer:"_valueChanged",notify:!0},_hasInputValue:{type:Boolean,value:!1,observer:"_hasInputValueChanged"}}}constructor(){super(),this._boundOnInput=this.__onInput.bind(this),this._boundOnChange=this._onChange.bind(this)}clear(){this.value=""}_addInputListeners(e){e.addEventListener("input",this._boundOnInput),e.addEventListener("change",this._boundOnChange)}_removeInputListeners(e){e.removeEventListener("input",this._boundOnInput),e.removeEventListener("change",this._boundOnChange)}_forwardInputValue(e){this.inputElement&&(this.inputElement.value=null!=e?e:"")}_inputElementChanged(e,t){e?this._addInputListeners(e):t&&this._removeInputListeners(t)}_hasInputValueChanged(e,t){(e||t)&&this.dispatchEvent(new CustomEvent("has-input-value-changed"))}__onInput(e){this._setHasInputValue(e),this._onInput(e)}_onInput(e){const t=e.composedPath()[0];this.__userInput=e.isTrusted,this.value=t.value,this.__userInput=!1}_onChange(e){}_toggleHasValue(e){this.toggleAttribute("has-value",e)}_valueChanged(e,t){this._toggleHasValue(this._hasValue),""===e&&void 0===t||this.__userInput||this._forwardInputValue(e)}get _hasValue(){return null!=this.value&&""!==this.value}_setHasInputValue(e){const t=e.composedPath()[0];this._hasInputValue=t.value.length>0}}));class Se{constructor(e){this.host=e,e.addEventListener("opened-changed",(()=>{e.opened||this.__setVirtualKeyboardEnabled(!1)})),e.addEventListener("blur",(()=>this.__setVirtualKeyboardEnabled(!0))),e.addEventListener("touchstart",(()=>this.__setVirtualKeyboardEnabled(!0)))}__setVirtualKeyboardEnabled(e){this.host.inputElement&&(this.host.inputElement.inputMode=e?"":"none")}}function Te(e){return null!=e}function Ve(e,t){return e.findIndex((e=>!(e instanceof be)&&t(e)))}const ke=e=>class extends(C(we(Ee(Ce(e))))){static get properties(){return{opened:{type:Boolean,notify:!0,value:!1,reflectToAttribute:!0,observer:"_openedChanged"},autoOpenDisabled:{type:Boolean},readonly:{type:Boolean,value:!1,reflectToAttribute:!0},renderer:Function,items:{type:Array,observer:"_itemsChanged"},allowCustomValue:{type:Boolean,value:!1},filteredItems:{type:Array,observer:"_filteredItemsChanged"},_lastCommittedValue:String,loading:{type:Boolean,value:!1,reflectToAttribute:!0},_focusedIndex:{type:Number,observer:"_focusedIndexChanged",value:-1},filter:{type:String,value:"",notify:!0},selectedItem:{type:Object,notify:!0},itemLabelPath:{type:String,value:"label",observer:"_itemLabelPathChanged"},itemValuePath:{type:String,value:"value"},itemIdPath:String,_toggleElement:{type:Object,observer:"_toggleElementChanged"},_closeOnBlurIsPrevented:Boolean,_scroller:Object,_overlayOpened:{type:Boolean,observer:"_overlayOpenedChanged"}}}static get observers(){return["_selectedItemChanged(selectedItem, itemValuePath, itemLabelPath)","_openedOrItemsChanged(opened, filteredItems, loading)","_updateScroller(_scroller, filteredItems, opened, loading, selectedItem, itemIdPath, _focusedIndex, renderer, theme)"]}constructor(){super(),this._boundOnFocusout=this._onFocusout.bind(this),this._boundOverlaySelectedItemChanged=this._overlaySelectedItemChanged.bind(this),this._boundOnClearButtonMouseDown=this.__onClearButtonMouseDown.bind(this),this._boundOnClick=this._onClick.bind(this),this._boundOnOverlayTouchAction=this._onOverlayTouchAction.bind(this),this._boundOnTouchend=this._onTouchend.bind(this)}get _tagNamePrefix(){return"vaadin-combo-box"}get _inputElementValue(){return this.inputElement?this.inputElement[this._propertyForValue]:void 0}set _inputElementValue(e){this.inputElement&&(this.inputElement[this._propertyForValue]=e)}get _nativeInput(){return this.inputElement}_inputElementChanged(e){super._inputElementChanged(e);const t=this._nativeInput;t&&(t.autocomplete="off",t.autocapitalize="off",t.setAttribute("role","combobox"),t.setAttribute("aria-autocomplete","list"),t.setAttribute("aria-expanded",!!this.opened),t.setAttribute("spellcheck","false"),t.setAttribute("autocorrect","off"),this._revertInputValueToValue(),this.clearElement&&this.clearElement.addEventListener("mousedown",this._boundOnClearButtonMouseDown))}ready(){super.ready(),this._initOverlay(),this._initScroller(),this.addEventListener("focusout",this._boundOnFocusout),this._lastCommittedValue=this.value,this.addEventListener("click",this._boundOnClick),this.addEventListener("touchend",this._boundOnTouchend);const e=()=>{requestAnimationFrame((()=>{this.$.overlay.bringToFront()}))};var t;this.addEventListener("mousedown",e),this.addEventListener("touchstart",e),t=this,window.Vaadin&&window.Vaadin.templateRendererCallback?window.Vaadin.templateRendererCallback(t):t.querySelector("template")&&console.warn(`WARNING: <template> inside <${t.localName}> is no longer supported. Import @vaadin/polymer-legacy-adapter/template-renderer.js to enable compatibility.`),this.addController(new Se(this))}disconnectedCallback(){super.disconnectedCallback(),this.close()}requestContentUpdate(){this._scroller&&(this._scroller.requestContentUpdate(),this._getItemElements().forEach((e=>{e.requestContentUpdate()})))}open(){this.disabled||this.readonly||(this.opened=!0)}close(){this.opened=!1}_propertiesChanged(e,t,i){super._propertiesChanged(e,t,i),void 0!==t.filter&&this._filterChanged(t.filter)}_initOverlay(){const e=this.$.overlay;e._comboBox=this,e.addEventListener("touchend",this._boundOnOverlayTouchAction),e.addEventListener("touchmove",this._boundOnOverlayTouchAction),e.addEventListener("mousedown",(e=>e.preventDefault())),e.addEventListener("opened-changed",(e=>{this._overlayOpened=e.detail.value}))}_initScroller(e){const t=`${this._tagNamePrefix}-scroller`,i=this.$.overlay;i.renderer=e=>{e.firstChild||e.appendChild(document.createElement(t))},i.requestContentUpdate();const s=i.querySelector(t);s.comboBox=e||this,s.getItemLabel=this._getItemLabel.bind(this),s.addEventListener("selection-changed",this._boundOverlaySelectedItemChanged),this._scroller=s}_updateScroller(e,t,i,s,o,r,n,a,l){e&&(i&&(e.style.maxHeight=getComputedStyle(this).getPropertyValue(`--${this._tagNamePrefix}-overlay-max-height`)||"65vh"),e.setProperties({items:i?t:[],opened:i,loading:s,selectedItem:o,itemIdPath:r,focusedIndex:n,renderer:a,theme:l}))}_openedOrItemsChanged(e,t,i){this._overlayOpened=!(!e||!(i||t&&t.length))}_overlayOpenedChanged(e,t){e?(this.dispatchEvent(new CustomEvent("vaadin-combo-box-dropdown-opened",{bubbles:!0,composed:!0})),this._onOpened()):t&&this.filteredItems&&this.filteredItems.length&&(this.close(),this.dispatchEvent(new CustomEvent("vaadin-combo-box-dropdown-closed",{bubbles:!0,composed:!0})))}_focusedIndexChanged(e,t){void 0!==t&&this._updateActiveDescendant(e)}_isInputFocused(){return this.inputElement&&R(this.inputElement)}_updateActiveDescendant(e){const t=this._nativeInput;if(!t)return;const i=this._getItemElements().find((t=>t.index===e));i?t.setAttribute("aria-activedescendant",i.id):t.removeAttribute("aria-activedescendant")}_openedChanged(e,t){if(void 0===t)return;e?(this._openedWithFocusRing=this.hasAttribute("focus-ring"),this._isInputFocused()||x||this.focus(),this.$.overlay.restoreFocusOnClose=!0):(this._onClosed(),this._openedWithFocusRing&&this._isInputFocused()&&this.setAttribute("focus-ring",""));const i=this._nativeInput;i&&(i.setAttribute("aria-expanded",!!e),e?i.setAttribute("aria-controls",this._scroller.id):i.removeAttribute("aria-controls"))}_onOverlayTouchAction(){this._closeOnBlurIsPrevented=!0,this.inputElement.blur(),this._closeOnBlurIsPrevented=!1}_isClearButton(e){return e.composedPath()[0]===this.clearElement}_handleClearButtonClick(e){e.preventDefault(),this._clear(),this.opened&&this.requestContentUpdate()}_onToggleButtonClick(e){e.preventDefault(),this.opened?this.close():this.open()}_onHostClick(e){this.autoOpenDisabled||(e.preventDefault(),this.open())}_onClick(e){const t=e.composedPath();this._isClearButton(e)?this._handleClearButtonClick(e):t.indexOf(this._toggleElement)>-1?this._onToggleButtonClick(e):this._onHostClick(e)}_onKeyDown(e){super._onKeyDown(e),"Tab"===e.key?this.$.overlay.restoreFocusOnClose=!1:"ArrowDown"===e.key?(this._onArrowDown(),e.preventDefault()):"ArrowUp"===e.key&&(this._onArrowUp(),e.preventDefault())}_getItemLabel(e){let t=e&&this.itemLabelPath?this.get(this.itemLabelPath,e):void 0;return null==t&&(t=e?e.toString():""),t}_getItemValue(e){let t=e&&this.itemValuePath?this.get(this.itemValuePath,e):void 0;return void 0===t&&(t=e?e.toString():""),t}_onArrowDown(){if(this.opened){const e=this.filteredItems;e&&(this._focusedIndex=Math.min(e.length-1,this._focusedIndex+1),this._prefillFocusedItemLabel())}else this.open()}_onArrowUp(){if(this.opened){if(this._focusedIndex>-1)this._focusedIndex=Math.max(0,this._focusedIndex-1);else{const e=this.filteredItems;e&&(this._focusedIndex=e.length-1)}this._prefillFocusedItemLabel()}else this.open()}_prefillFocusedItemLabel(){if(this._focusedIndex>-1){const e=this.filteredItems[this._focusedIndex];this._inputElementValue=this._getItemLabel(e),this._markAllSelectionRange()}}_setSelectionRange(e,t){this._isInputFocused()&&this.inputElement.setSelectionRange&&this.inputElement.setSelectionRange(e,t)}_markAllSelectionRange(){void 0!==this._inputElementValue&&this._setSelectionRange(0,this._inputElementValue.length)}_clearSelectionRange(){if(void 0!==this._inputElementValue){const e=this._inputElementValue?this._inputElementValue.length:0;this._setSelectionRange(e,e)}}_closeOrCommit(){this.opened||this.loading?this.close():this._commitValue()}_onEnter(e){const t=this._focusedIndex<0&&""!==this._inputElementValue&&this._getItemLabel(this.selectedItem)!==this._inputElementValue;if(!this.allowCustomValue&&t)return e.preventDefault(),void e.stopPropagation();this.opened&&(e.preventDefault(),e.stopPropagation()),this._closeOrCommit()}_onEscape(e){this.autoOpenDisabled?this.opened||this.value!==this._inputElementValue&&this._inputElementValue.length>0?(e.stopPropagation(),this._focusedIndex=-1,this.cancel()):this.clearButtonVisible&&!this.opened&&this.value&&(e.stopPropagation(),this._clear()):this.opened?(e.stopPropagation(),this._focusedIndex>-1?(this._focusedIndex=-1,this._revertInputValue()):this.cancel()):this.clearButtonVisible&&this.value&&(e.stopPropagation(),this._clear())}_toggleElementChanged(e){e&&(e.addEventListener("mousedown",(e=>e.preventDefault())),e.addEventListener("click",(()=>{x&&!this._isInputFocused()&&document.activeElement.blur()})))}_clear(){this.selectedItem=null,this.allowCustomValue&&(this.value=""),this._detectAndDispatchChange()}cancel(){this._revertInputValueToValue(),this._lastCommittedValue=this.value,this._closeOrCommit()}_onOpened(){requestAnimationFrame((()=>{this._scrollIntoView(this._focusedIndex),this._updateActiveDescendant(this._focusedIndex)})),this._lastCommittedValue=this.value}_onClosed(){this.loading&&!this.allowCustomValue||this._commitValue()}_commitValue(){if(this._focusedIndex>-1){const e=this.filteredItems[this._focusedIndex];this.selectedItem!==e&&(this.selectedItem=e),this._inputElementValue=this._getItemLabel(this.selectedItem)}else if(""===this._inputElementValue||void 0===this._inputElementValue)this.selectedItem=null,this.allowCustomValue&&(this.value="");else{const e=[...this.filteredItems||[],this.selectedItem],t=e[this.__getItemIndexByLabel(e,this._inputElementValue)];if(this.allowCustomValue&&!t){const e=this._inputElementValue;this._lastCustomValue=e;const t=new CustomEvent("custom-value-set",{detail:e,composed:!0,cancelable:!0,bubbles:!0});this.dispatchEvent(t),t.defaultPrevented||(this.value=e)}else this.allowCustomValue||this.opened||!t?this._inputElementValue=this.selectedItem?this._getItemLabel(this.selectedItem):this.value||"":this.value=this._getItemValue(t)}this._detectAndDispatchChange(),this._clearSelectionRange(),this.filter=""}get _propertyForValue(){return"value"}_onInput(e){const t=this._inputElementValue,i={};this.filter===t?this._filterChanged(this.filter):i.filter=t,this.opened||this._isClearButton(e)||this.autoOpenDisabled||(i.opened=!0),this.setProperties(i)}_onChange(e){e.stopPropagation()}_itemLabelPathChanged(e){"string"!=typeof e&&console.error("You should set itemLabelPath to a valid string")}_filterChanged(e){this._scrollIntoView(0),this._focusedIndex=-1,this.items?this.filteredItems=this._filterItems(this.items,e):this._filteredItemsChanged(this.filteredItems)}_revertInputValue(){""!==this.filter?this._inputElementValue=this.filter:this._revertInputValueToValue(),this._clearSelectionRange()}_revertInputValueToValue(){this.allowCustomValue&&!this.selectedItem?this._inputElementValue=this.value:this._inputElementValue=this._getItemLabel(this.selectedItem)}_selectedItemChanged(e){if(null==e)this.filteredItems&&(this.allowCustomValue||(this.value=""),this._toggleHasValue(this._hasValue),this._inputElementValue=this.value);else{const t=this._getItemValue(e);if(this.value!==t&&(this.value=t,this.value!==t))return;this._toggleHasValue(!0),this._inputElementValue=this._getItemLabel(e)}this.filteredItems&&(this._focusedIndex=this.filteredItems.indexOf(e))}_valueChanged(e,t){""===e&&void 0===t||(Te(e)?(this._getItemValue(this.selectedItem)!==e&&this._selectItemForValue(e),!this.selectedItem&&this.allowCustomValue&&(this._inputElementValue=e),this._toggleHasValue(this._hasValue)):this.selectedItem=null,this.filter="",this._lastCommittedValue=void 0)}_detectAndDispatchChange(){this.value!==this._lastCommittedValue&&(this.dispatchEvent(new CustomEvent("change",{bubbles:!0})),this._lastCommittedValue=this.value)}_itemsChanged(e,t){this._ensureItemsOrDataProvider((()=>{this.items=t})),e?this.filteredItems=e.slice(0):t&&(this.filteredItems=null)}_filteredItemsChanged(e,t){const i=t?t[this._focusedIndex]:null,s=this.__getItemIndexByValue(e,this.value);(null===this.selectedItem||void 0===this.selectedItem)&&s>=0&&(this.selectedItem=e[s]);const o=this.__getItemIndexByValue(e,this._getItemValue(i));o>-1?this._focusedIndex=o:this.__setInitialFocusedIndex()}__setInitialFocusedIndex(){const e=this._inputElementValue;void 0===e||e===this._getItemLabel(this.selectedItem)?this._focusedIndex=this.__getItemIndexByLabel(this.filteredItems,this._getItemLabel(this.selectedItem)):this._focusedIndex=this.__getItemIndexByLabel(this.filteredItems,this.filter)}_filterItems(e,t){if(!e)return e;const i=e.filter((e=>(t=t?t.toString().toLowerCase():"",this._getItemLabel(e).toString().toLowerCase().indexOf(t)>-1)));return i}_selectItemForValue(e){const t=this.__getItemIndexByValue(this.filteredItems,e),i=this.selectedItem;t>=0?this.selectedItem=this.filteredItems[t]:this.dataProvider&&void 0===this.selectedItem?this.selectedItem=void 0:this.selectedItem=null,null===this.selectedItem&&null===i&&this._selectedItemChanged(this.selectedItem)}_getItemElements(){return Array.from(this._scroller.querySelectorAll(`${this._tagNamePrefix}-item`))}_scrollIntoView(e){this._scroller&&this._scroller.scrollIntoView(e)}__getItemIndexByValue(e,t){return e&&Te(t)?Ve(e,(e=>this._getItemValue(e)===t)):-1}__getItemIndexByLabel(e,t){return e&&t?Ve(e,(e=>this._getItemLabel(e).toString().toLowerCase()===t.toString().toLowerCase())):-1}_overlaySelectedItemChanged(e){e.stopPropagation(),e.detail.item instanceof be||this.opened&&(this._focusedIndex=this.filteredItems.indexOf(e.detail.item),this.close())}__onClearButtonMouseDown(e){e.preventDefault(),this.inputElement.focus()}_onFocusout(e){if(!e.relatedTarget||e.relatedTarget.localName!==`${this._tagNamePrefix}-item`)if(e.relatedTarget!==this.$.overlay){if(!this.readonly&&!this._closeOnBlurIsPrevented){if(!this.opened&&this.allowCustomValue&&this._inputElementValue===this._lastCustomValue)return void delete this._lastCustomValue;this._closeOrCommit()}}else e.composedPath()[0].focus()}_onTouchend(e){this.clearElement&&e.composedPath()[0]===this.clearElement&&(e.preventDefault(),this._clear())}};class Pe extends(Ie(ke(xe((0,o.Tb)(m.H3))))){static get is(){return"vaadin-combo-box-light"}static get template(){return m.dy`
      <style>
        :host([opened]) {
          pointer-events: auto;
        }
      </style>

      <slot></slot>

      <vaadin-combo-box-overlay
        id="overlay"
        opened="[[_overlayOpened]]"
        loading$="[[loading]]"
        theme$="[[_theme]]"
        position-target="[[inputElement]]"
        no-vertical-overlap
        restore-focus-node="[[inputElement]]"
      ></vaadin-combo-box-overlay>
    `}static get properties(){return{attrForValue:{type:String,value:"value"}}}get clearElement(){return this.querySelector(".clear-button")}ready(){super.ready(),this._toggleElement=this.querySelector(".toggle-button"),(0,_.T8)(this,(()=>{this._setInputElement(this.querySelector("vaadin-text-field,.input")),this._revertInputValue()}))}checkValidity(){return this.inputElement.validate?this.inputElement.validate():super.checkValidity()}get _propertyForValue(){return(0,ye.z)(this.attrForValue)}get _nativeInput(){const e=this.inputElement;if(e){if(e instanceof HTMLInputElement)return e;const t=e.querySelector("input");if(t)return t;if(e.shadowRoot){const t=e.shadowRoot.querySelector("input");if(t)return t}}}_isClearButton(e){return super._isClearButton(e)||"input"===e.type&&!e.isTrusted||"clear-button"===e.composedPath()[0].getAttribute("part")}_onChange(e){super._onChange(e),this._isClearButton(e)&&this._clear()}}customElements.define(Pe.is,Pe)},53947:(e,t,i)=>{i.d(t,{hC:()=>s.hC});var s=i(86295)},86295:(e,t,i)=>{i.d(t,{Tb:()=>u,iv:()=>s.iv,hC:()=>n});var s=i(68144);const o=e=>class extends e{static get properties(){return{theme:{type:String,reflectToAttribute:!0,observer:"__deprecatedThemePropertyChanged"},_theme:{type:String,readOnly:!0}}}__deprecatedThemePropertyChanged(e){this._set_theme(e)}},r=[];function n(e,t,i={}){var o;e&&(o=e,c(customElements.get(o))&&console.warn(`The custom element definition for "${e}"\n      was finalized before a style module was registered.\n      Make sure to add component specific style modules before\n      importing the corresponding custom element.`)),t=function(e=[]){return[e].flat(1/0).filter((e=>e instanceof s.c3||(console.warn("An item in styles is not of type CSSResult. Use `unsafeCSS` or `css`."),!1)))}(t),window.Vaadin&&window.Vaadin.styleModules?window.Vaadin.styleModules.registerStyles(e,t,i):r.push({themeFor:e,styles:t,include:i.include,moduleId:i.moduleId})}function a(){return window.Vaadin&&window.Vaadin.styleModules?window.Vaadin.styleModules.getAllThemes():r}function l(e=""){let t=0;return e.startsWith("lumo-")||e.startsWith("material-")?t=1:e.startsWith("vaadin-")&&(t=2),t}function h(e){const t=[];return e.include&&[].concat(e.include).forEach((e=>{const i=a().find((t=>t.moduleId===e));i?t.push(...h(i),...i.styles):console.warn(`Included moduleId ${e} not found in style registry`)}),e.styles),t}function d(e){const t=`${e}-default-theme`,i=a().filter((i=>i.moduleId!==t&&function(e,t){return(e||"").split(" ").some((e=>new RegExp(`^${e.split("*").join(".*")}$`).test(t)))}(i.themeFor,e))).map((e=>({...e,styles:[...h(e),...e.styles],includePriority:l(e.moduleId)}))).sort(((e,t)=>t.includePriority-e.includePriority));return i.length>0?i:a().filter((e=>e.moduleId===t))}function c(e){return e&&Object.prototype.hasOwnProperty.call(e,"__themes")}const u=e=>class extends(o(e)){static finalize(){if(super.finalize(),this.elementStyles)return;const e=this.prototype._template;e&&!c(this)&&function(e,t){const i=document.createElement("style");i.innerHTML=e.map((e=>e.cssText)).join("\n"),t.content.appendChild(i)}(this.getStylesForThis(),e)}static finalizeStyles(e){const t=this.getStylesForThis();return e?[...super.finalizeStyles(e),...t]:t}static getStylesForThis(){const e=Object.getPrototypeOf(this.prototype),t=(e?e.constructor.__themes:[])||[];this.__themes=[...t,...d(this.is)];const i=this.__themes.flatMap((e=>e.styles));return i.filter(((e,t)=>t===i.lastIndexOf(e)))}}}}]);
//# sourceMappingURL=4707-Dkw6Jsu4uXA.js.map