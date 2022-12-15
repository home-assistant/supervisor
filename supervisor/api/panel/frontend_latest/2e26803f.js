"use strict";(self.webpackChunkhome_assistant_frontend=self.webpackChunkhome_assistant_frontend||[]).push([[4875],{4875:(e,r,t)=>{t.r(r),t.d(r,{HaColorTempSelector:()=>y});var i=t(7500),n=t(3550),o=t(7181),a=t(856),s=t(8426);t(5025);class l extends s.H3{static get template(){return a.d`
      <style>
        :host {
          display: block;
        }

        .title {
          margin: 5px 0 8px;
          color: var(--primary-text-color);
        }

        .slider-container {
          display: flex;
        }

        ha-icon {
          margin-top: 4px;
          color: var(--secondary-text-color);
        }

        ha-slider {
          flex-grow: 1;
          background-image: var(--ha-slider-background);
          border-radius: 4px;
        }
      </style>

      <div class="title">[[_getTitle()]]</div>
      <div class="extra-container"><slot name="extra"></slot></div>
      <div class="slider-container">
        <ha-icon icon="[[icon]]" hidden$="[[!icon]]"></ha-icon>
        <ha-slider
          min="[[min]]"
          max="[[max]]"
          step="[[step]]"
          pin="[[pin]]"
          disabled="[[disabled]]"
          value="{{value}}"
        ></ha-slider>
      </div>
      <template is="dom-if" if="[[helper]]">
        <ha-input-helper-text>[[helper]]</ha-input-helper-text>
      </template>
    `}_getTitle(){return`${this.caption}${this.caption&&this.required?" *":""}`}static get properties(){return{caption:String,disabled:Boolean,required:Boolean,min:Number,max:Number,pin:Boolean,step:Number,helper:String,extra:{type:Boolean,value:!1},ignoreBarTouch:{type:Boolean,value:!0},icon:{type:String,value:""},value:{type:Number,notify:!0}}}}function d(){d=function(){return e};var e={elementsDefinitionOrder:[["method"],["field"]],initializeInstanceElements:function(e,r){["method","field"].forEach((function(t){r.forEach((function(r){r.kind===t&&"own"===r.placement&&this.defineClassElement(e,r)}),this)}),this)},initializeClassElements:function(e,r){var t=e.prototype;["method","field"].forEach((function(i){r.forEach((function(r){var n=r.placement;if(r.kind===i&&("static"===n||"prototype"===n)){var o="static"===n?e:t;this.defineClassElement(o,r)}}),this)}),this)},defineClassElement:function(e,r){var t=r.descriptor;if("field"===r.kind){var i=r.initializer;t={enumerable:t.enumerable,writable:t.writable,configurable:t.configurable,value:void 0===i?void 0:i.call(e)}}Object.defineProperty(e,r.key,t)},decorateClass:function(e,r){var t=[],i=[],n={static:[],prototype:[],own:[]};if(e.forEach((function(e){this.addElementPlacement(e,n)}),this),e.forEach((function(e){if(!u(e))return t.push(e);var r=this.decorateElement(e,n);t.push(r.element),t.push.apply(t,r.extras),i.push.apply(i,r.finishers)}),this),!r)return{elements:t,finishers:i};var o=this.decorateConstructor(t,r);return i.push.apply(i,o.finishers),o.finishers=i,o},addElementPlacement:function(e,r,t){var i=r[e.placement];if(!t&&-1!==i.indexOf(e.key))throw new TypeError("Duplicated element ("+e.key+")");i.push(e.key)},decorateElement:function(e,r){for(var t=[],i=[],n=e.decorators,o=n.length-1;o>=0;o--){var a=r[e.placement];a.splice(a.indexOf(e.key),1);var s=this.fromElementDescriptor(e),l=this.toElementFinisherExtras((0,n[o])(s)||s);e=l.element,this.addElementPlacement(e,r),l.finisher&&i.push(l.finisher);var d=l.extras;if(d){for(var c=0;c<d.length;c++)this.addElementPlacement(d[c],r);t.push.apply(t,d)}}return{element:e,finishers:i,extras:t}},decorateConstructor:function(e,r){for(var t=[],i=r.length-1;i>=0;i--){var n=this.fromClassDescriptor(e),o=this.toClassDescriptor((0,r[i])(n)||n);if(void 0!==o.finisher&&t.push(o.finisher),void 0!==o.elements){e=o.elements;for(var a=0;a<e.length-1;a++)for(var s=a+1;s<e.length;s++)if(e[a].key===e[s].key&&e[a].placement===e[s].placement)throw new TypeError("Duplicated element ("+e[a].key+")")}}return{elements:e,finishers:t}},fromElementDescriptor:function(e){var r={kind:e.kind,key:e.key,placement:e.placement,descriptor:e.descriptor};return Object.defineProperty(r,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),"field"===e.kind&&(r.initializer=e.initializer),r},toElementDescriptors:function(e){var r;if(void 0!==e)return(r=e,function(e){if(Array.isArray(e))return e}(r)||function(e){if("undefined"!=typeof Symbol&&null!=e[Symbol.iterator]||null!=e["@@iterator"])return Array.from(e)}(r)||function(e,r){if(e){if("string"==typeof e)return v(e,r);var t=Object.prototype.toString.call(e).slice(8,-1);return"Object"===t&&e.constructor&&(t=e.constructor.name),"Map"===t||"Set"===t?Array.from(e):"Arguments"===t||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(t)?v(e,r):void 0}}(r)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()).map((function(e){var r=this.toElementDescriptor(e);return this.disallowProperty(e,"finisher","An element descriptor"),this.disallowProperty(e,"extras","An element descriptor"),r}),this)},toElementDescriptor:function(e){var r=String(e.kind);if("method"!==r&&"field"!==r)throw new TypeError('An element descriptor\'s .kind property must be either "method" or "field", but a decorator created an element descriptor with .kind "'+r+'"');var t=m(e.key),i=String(e.placement);if("static"!==i&&"prototype"!==i&&"own"!==i)throw new TypeError('An element descriptor\'s .placement property must be one of "static", "prototype" or "own", but a decorator created an element descriptor with .placement "'+i+'"');var n=e.descriptor;this.disallowProperty(e,"elements","An element descriptor");var o={kind:r,key:t,placement:i,descriptor:Object.assign({},n)};return"field"!==r?this.disallowProperty(e,"initializer","A method descriptor"):(this.disallowProperty(n,"get","The property descriptor of a field descriptor"),this.disallowProperty(n,"set","The property descriptor of a field descriptor"),this.disallowProperty(n,"value","The property descriptor of a field descriptor"),o.initializer=e.initializer),o},toElementFinisherExtras:function(e){return{element:this.toElementDescriptor(e),finisher:h(e,"finisher"),extras:this.toElementDescriptors(e.extras)}},fromClassDescriptor:function(e){var r={kind:"class",elements:e.map(this.fromElementDescriptor,this)};return Object.defineProperty(r,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),r},toClassDescriptor:function(e){var r=String(e.kind);if("class"!==r)throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator created a class descriptor with .kind "'+r+'"');this.disallowProperty(e,"key","A class descriptor"),this.disallowProperty(e,"placement","A class descriptor"),this.disallowProperty(e,"descriptor","A class descriptor"),this.disallowProperty(e,"initializer","A class descriptor"),this.disallowProperty(e,"extras","A class descriptor");var t=h(e,"finisher");return{elements:this.toElementDescriptors(e.elements),finisher:t}},runClassFinishers:function(e,r){for(var t=0;t<r.length;t++){var i=(0,r[t])(e);if(void 0!==i){if("function"!=typeof i)throw new TypeError("Finishers must return a constructor.");e=i}}return e},disallowProperty:function(e,r,t){if(void 0!==e[r])throw new TypeError(t+" can't have a ."+r+" property.")}};return e}function c(e){var r,t=m(e.key);"method"===e.kind?r={value:e.value,writable:!0,configurable:!0,enumerable:!1}:"get"===e.kind?r={get:e.value,configurable:!0,enumerable:!1}:"set"===e.kind?r={set:e.value,configurable:!0,enumerable:!1}:"field"===e.kind&&(r={configurable:!0,writable:!0,enumerable:!0});var i={kind:"field"===e.kind?"field":"method",key:t,placement:e.static?"static":"field"===e.kind?"own":"prototype",descriptor:r};return e.decorators&&(i.decorators=e.decorators),"field"===e.kind&&(i.initializer=e.value),i}function p(e,r){void 0!==e.descriptor.get?r.descriptor.get=e.descriptor.get:r.descriptor.set=e.descriptor.set}function u(e){return e.decorators&&e.decorators.length}function f(e){return void 0!==e&&!(void 0===e.value&&void 0===e.writable)}function h(e,r){var t=e[r];if(void 0!==t&&"function"!=typeof t)throw new TypeError("Expected '"+r+"' to be a function");return t}function m(e){var r=function(e,r){if("object"!=typeof e||null===e)return e;var t=e[Symbol.toPrimitive];if(void 0!==t){var i=t.call(e,r||"default");if("object"!=typeof i)return i;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===r?String:Number)(e)}(e,"string");return"symbol"==typeof r?r:String(r)}function v(e,r){(null==r||r>e.length)&&(r=e.length);for(var t=0,i=new Array(r);t<r;t++)i[t]=e[t];return i}customElements.define("ha-labeled-slider",l);let y=function(e,r,t,i){var n=d();if(i)for(var o=0;o<i.length;o++)n=i[o](n);var a=r((function(e){n.initializeInstanceElements(e,s.elements)}),t),s=n.decorateClass(function(e){for(var r=[],t=function(e){return"method"===e.kind&&e.key===o.key&&e.placement===o.placement},i=0;i<e.length;i++){var n,o=e[i];if("method"===o.kind&&(n=r.find(t)))if(f(o.descriptor)||f(n.descriptor)){if(u(o)||u(n))throw new ReferenceError("Duplicated methods ("+o.key+") can't be decorated.");n.descriptor=o.descriptor}else{if(u(o)){if(u(n))throw new ReferenceError("Decorators can't be placed on different accessors with for the same property ("+o.key+").");n.decorators=o.decorators}p(o,n)}else r.push(o)}return r}(a.d.map(c)),e);return n.initializeClassElements(a.F,s.elements),n.runClassFinishers(a.F,s.finishers)}([(0,n.Mo)("ha-selector-color_temp")],(function(e,r){return{F:class extends r{constructor(...r){super(...r),e(this)}},d:[{kind:"field",decorators:[(0,n.Cb)()],key:"hass",value:void 0},{kind:"field",decorators:[(0,n.Cb)()],key:"selector",value:void 0},{kind:"field",decorators:[(0,n.Cb)()],key:"value",value:void 0},{kind:"field",decorators:[(0,n.Cb)()],key:"label",value:void 0},{kind:"field",decorators:[(0,n.Cb)()],key:"helper",value:void 0},{kind:"field",decorators:[(0,n.Cb)({type:Boolean,reflect:!0})],key:"disabled",value:()=>!1},{kind:"field",decorators:[(0,n.Cb)({type:Boolean})],key:"required",value:()=>!0},{kind:"method",key:"render",value:function(){var e,r,t,n;return i.dy`
      <ha-labeled-slider
        pin
        icon="hass:thermometer"
        .caption=${this.label||""}
        .min=${null!==(e=null===(r=this.selector.color_temp)||void 0===r?void 0:r.min_mireds)&&void 0!==e?e:153}
        .max=${null!==(t=null===(n=this.selector.color_temp)||void 0===n?void 0:n.max_mireds)&&void 0!==t?t:500}
        .value=${this.value}
        .disabled=${this.disabled}
        .helper=${this.helper}
        .required=${this.required}
        @change=${this._valueChanged}
      ></ha-labeled-slider>
    `}},{kind:"method",key:"_valueChanged",value:function(e){(0,o.B)(this,"value-changed",{value:Number(e.target.value)})}},{kind:"field",static:!0,key:"styles",value:()=>i.iv`
    ha-labeled-slider {
      --ha-slider-background: -webkit-linear-gradient(
        var(--float-end),
        rgb(255, 160, 0) 0%,
        white 50%,
        rgb(166, 209, 255) 100%
      );
      /* The color temp minimum value shouldn't be rendered differently. It's not "off". */
      --paper-slider-knob-start-border-color: var(--primary-color);
    }
  `}]}}),i.oi)}}]);
//# sourceMappingURL=2e26803f.js.map