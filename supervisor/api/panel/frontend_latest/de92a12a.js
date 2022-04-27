"use strict";(self.webpackChunkhome_assistant_frontend=self.webpackChunkhome_assistant_frontend||[]).push([[872],{9872:(e,t,r)=>{r.r(t);var i=r(7500),o=r(3550),n=r(4516),s=r(7181),a=r(3849),d=r(5493),l=(r(4552),r(4154)),c=r(1682),h=(r(8811),r(1625),r(1359),r(1654)),p=r(5677),u=(r(1187),r(4577),r(2594)),f=(r(8762),r(9381),r(2098),r(6248),r(258)),m=r(6765);const v=async(e,t,r,i)=>{if(await(0,m.g7)(e,{title:r.localize("common.restart_name","name",i.name),text:r.localize("dialog.restart_addon.text"),confirmText:r.localize("dialog.restart_addon.confirm_text"),dismissText:r.localize("common.cancel")}))try{await(0,l.P$)(t,i.slug)}catch(t){(0,m.Ys)(e,{title:r.localize("common.failed_to_restart_name","name",i.name),text:(0,c.js)(t)})}};function y(){y=function(){return e};var e={elementsDefinitionOrder:[["method"],["field"]],initializeInstanceElements:function(e,t){["method","field"].forEach((function(r){t.forEach((function(t){t.kind===r&&"own"===t.placement&&this.defineClassElement(e,t)}),this)}),this)},initializeClassElements:function(e,t){var r=e.prototype;["method","field"].forEach((function(i){t.forEach((function(t){var o=t.placement;if(t.kind===i&&("static"===o||"prototype"===o)){var n="static"===o?e:r;this.defineClassElement(n,t)}}),this)}),this)},defineClassElement:function(e,t){var r=t.descriptor;if("field"===t.kind){var i=t.initializer;r={enumerable:r.enumerable,writable:r.writable,configurable:r.configurable,value:void 0===i?void 0:i.call(e)}}Object.defineProperty(e,t.key,r)},decorateClass:function(e,t){var r=[],i=[],o={static:[],prototype:[],own:[]};if(e.forEach((function(e){this.addElementPlacement(e,o)}),this),e.forEach((function(e){if(!k(e))return r.push(e);var t=this.decorateElement(e,o);r.push(t.element),r.push.apply(r,t.extras),i.push.apply(i,t.finishers)}),this),!t)return{elements:r,finishers:i};var n=this.decorateConstructor(r,t);return i.push.apply(i,n.finishers),n.finishers=i,n},addElementPlacement:function(e,t,r){var i=t[e.placement];if(!r&&-1!==i.indexOf(e.key))throw new TypeError("Duplicated element ("+e.key+")");i.push(e.key)},decorateElement:function(e,t){for(var r=[],i=[],o=e.decorators,n=o.length-1;n>=0;n--){var s=t[e.placement];s.splice(s.indexOf(e.key),1);var a=this.fromElementDescriptor(e),d=this.toElementFinisherExtras((0,o[n])(a)||a);e=d.element,this.addElementPlacement(e,t),d.finisher&&i.push(d.finisher);var l=d.extras;if(l){for(var c=0;c<l.length;c++)this.addElementPlacement(l[c],t);r.push.apply(r,l)}}return{element:e,finishers:i,extras:r}},decorateConstructor:function(e,t){for(var r=[],i=t.length-1;i>=0;i--){var o=this.fromClassDescriptor(e),n=this.toClassDescriptor((0,t[i])(o)||o);if(void 0!==n.finisher&&r.push(n.finisher),void 0!==n.elements){e=n.elements;for(var s=0;s<e.length-1;s++)for(var a=s+1;a<e.length;a++)if(e[s].key===e[a].key&&e[s].placement===e[a].placement)throw new TypeError("Duplicated element ("+e[s].key+")")}}return{elements:e,finishers:r}},fromElementDescriptor:function(e){var t={kind:e.kind,key:e.key,placement:e.placement,descriptor:e.descriptor};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),"field"===e.kind&&(t.initializer=e.initializer),t},toElementDescriptors:function(e){var t;if(void 0!==e)return(t=e,function(e){if(Array.isArray(e))return e}(t)||function(e){if("undefined"!=typeof Symbol&&null!=e[Symbol.iterator]||null!=e["@@iterator"])return Array.from(e)}(t)||function(e,t){if(e){if("string"==typeof e)return _(e,t);var r=Object.prototype.toString.call(e).slice(8,-1);return"Object"===r&&e.constructor&&(r=e.constructor.name),"Map"===r||"Set"===r?Array.from(e):"Arguments"===r||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(r)?_(e,t):void 0}}(t)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()).map((function(e){var t=this.toElementDescriptor(e);return this.disallowProperty(e,"finisher","An element descriptor"),this.disallowProperty(e,"extras","An element descriptor"),t}),this)},toElementDescriptor:function(e){var t=String(e.kind);if("method"!==t&&"field"!==t)throw new TypeError('An element descriptor\'s .kind property must be either "method" or "field", but a decorator created an element descriptor with .kind "'+t+'"');var r=C(e.key),i=String(e.placement);if("static"!==i&&"prototype"!==i&&"own"!==i)throw new TypeError('An element descriptor\'s .placement property must be one of "static", "prototype" or "own", but a decorator created an element descriptor with .placement "'+i+'"');var o=e.descriptor;this.disallowProperty(e,"elements","An element descriptor");var n={kind:t,key:r,placement:i,descriptor:Object.assign({},o)};return"field"!==t?this.disallowProperty(e,"initializer","A method descriptor"):(this.disallowProperty(o,"get","The property descriptor of a field descriptor"),this.disallowProperty(o,"set","The property descriptor of a field descriptor"),this.disallowProperty(o,"value","The property descriptor of a field descriptor"),n.initializer=e.initializer),n},toElementFinisherExtras:function(e){return{element:this.toElementDescriptor(e),finisher:E(e,"finisher"),extras:this.toElementDescriptors(e.extras)}},fromClassDescriptor:function(e){var t={kind:"class",elements:e.map(this.fromElementDescriptor,this)};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),t},toClassDescriptor:function(e){var t=String(e.kind);if("class"!==t)throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator created a class descriptor with .kind "'+t+'"');this.disallowProperty(e,"key","A class descriptor"),this.disallowProperty(e,"placement","A class descriptor"),this.disallowProperty(e,"descriptor","A class descriptor"),this.disallowProperty(e,"initializer","A class descriptor"),this.disallowProperty(e,"extras","A class descriptor");var r=E(e,"finisher");return{elements:this.toElementDescriptors(e.elements),finisher:r}},runClassFinishers:function(e,t){for(var r=0;r<t.length;r++){var i=(0,t[r])(e);if(void 0!==i){if("function"!=typeof i)throw new TypeError("Finishers must return a constructor.");e=i}}return e},disallowProperty:function(e,t,r){if(void 0!==e[t])throw new TypeError(r+" can't have a ."+t+" property.")}};return e}function g(e){var t,r=C(e.key);"method"===e.kind?t={value:e.value,writable:!0,configurable:!0,enumerable:!1}:"get"===e.kind?t={get:e.value,configurable:!0,enumerable:!1}:"set"===e.kind?t={set:e.value,configurable:!0,enumerable:!1}:"field"===e.kind&&(t={configurable:!0,writable:!0,enumerable:!0});var i={kind:"field"===e.kind?"field":"method",key:r,placement:e.static?"static":"field"===e.kind?"own":"prototype",descriptor:t};return e.decorators&&(i.decorators=e.decorators),"field"===e.kind&&(i.initializer=e.value),i}function b(e,t){void 0!==e.descriptor.get?t.descriptor.get=e.descriptor.get:t.descriptor.set=e.descriptor.set}function k(e){return e.decorators&&e.decorators.length}function w(e){return void 0!==e&&!(void 0===e.value&&void 0===e.writable)}function E(e,t){var r=e[t];if(void 0!==r&&"function"!=typeof r)throw new TypeError("Expected '"+t+"' to be a function");return r}function C(e){var t=function(e,t){if("object"!=typeof e||null===e)return e;var r=e[Symbol.toPrimitive];if(void 0!==r){var i=r.call(e,t||"default");if("object"!=typeof i)return i;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===t?String:Number)(e)}(e,"string");return"symbol"==typeof t?t:String(t)}function _(e,t){(null==t||t>e.length)&&(t=e.length);for(var r=0,i=new Array(t);r<t;r++)i[r]=e[r];return i}function A(e,t,r){return A="undefined"!=typeof Reflect&&Reflect.get?Reflect.get:function(e,t,r){var i=function(e,t){for(;!Object.prototype.hasOwnProperty.call(e,t)&&null!==(e=P(e)););return e}(e,t);if(i){var o=Object.getOwnPropertyDescriptor(i,t);return o.get?o.get.call(r):o.value}},A(e,t,r||e)}function P(e){return P=Object.setPrototypeOf?Object.getPrototypeOf:function(e){return e.__proto__||Object.getPrototypeOf(e)},P(e)}!function(e,t,r,i){var o=y();if(i)for(var n=0;n<i.length;n++)o=i[n](o);var s=t((function(e){o.initializeInstanceElements(e,a.elements)}),r),a=o.decorateClass(function(e){for(var t=[],r=function(e){return"method"===e.kind&&e.key===n.key&&e.placement===n.placement},i=0;i<e.length;i++){var o,n=e[i];if("method"===n.kind&&(o=t.find(r)))if(w(n.descriptor)||w(o.descriptor)){if(k(n)||k(o))throw new ReferenceError("Duplicated methods ("+n.key+") can't be decorated.");o.descriptor=n.descriptor}else{if(k(n)){if(k(o))throw new ReferenceError("Decorators can't be placed on different accessors with for the same property ("+n.key+").");o.decorators=n.decorators}b(n,o)}else t.push(n)}return t}(s.d.map(g)),e);o.initializeClassElements(s.F,a.elements),o.runClassFinishers(s.F,a.finishers)}([(0,o.Mo)("hassio-addon-audio")],(function(e,t){class r extends t{constructor(...t){super(...t),e(this)}}return{F:r,d:[{kind:"field",decorators:[(0,o.Cb)({attribute:!1})],key:"hass",value:void 0},{kind:"field",decorators:[(0,o.Cb)({attribute:!1})],key:"supervisor",value:void 0},{kind:"field",decorators:[(0,o.Cb)({attribute:!1})],key:"addon",value:void 0},{kind:"field",decorators:[(0,o.SB)()],key:"_error",value:void 0},{kind:"field",decorators:[(0,o.SB)()],key:"_inputDevices",value:void 0},{kind:"field",decorators:[(0,o.SB)()],key:"_outputDevices",value:void 0},{kind:"field",decorators:[(0,o.SB)()],key:"_selectedInput",value:void 0},{kind:"field",decorators:[(0,o.SB)()],key:"_selectedOutput",value:void 0},{kind:"method",key:"render",value:function(){return i.dy`
      <ha-card
        .header=${this.supervisor.localize("addon.configuration.audio.header")}
      >
        <div class="card-content">
          ${this._error?i.dy`<ha-alert alert-type="error">${this._error}</ha-alert>`:""}
          ${this._inputDevices&&i.dy`<ha-select
            .label=${this.supervisor.localize("addon.configuration.audio.input")}
            @selected=${this._setInputDevice}
            @closed=${u.U}
            fixedMenuPosition
            naturalMenuWidth
            .value=${this._selectedInput}
          >
            ${this._inputDevices.map((e=>i.dy`
                <mwc-list-item .value=${e.device||""}>
                  ${e.name}
                </mwc-list-item>
              `))}
          </ha-select>`}
          ${this._outputDevices&&i.dy`<ha-select
            .label=${this.supervisor.localize("addon.configuration.audio.output")}
            @selected=${this._setOutputDevice}
            @closed=${u.U}
            fixedMenuPosition
            naturalMenuWidth
            .value=${this._selectedOutput}
          >
            ${this._outputDevices.map((e=>i.dy`
                <mwc-list-item .value=${e.device||""}
                  >${e.name}</mwc-list-item
                >
              `))}
          </ha-select>`}
        </div>
        <div class="card-actions">
          <ha-progress-button @click=${this._saveSettings}>
            ${this.supervisor.localize("common.save")}
          </ha-progress-button>
        </div>
      </ha-card>
    `}},{kind:"get",static:!0,key:"styles",value:function(){return[h.Qx,p.l,i.iv`
        :host,
        ha-card {
          display: block;
        }
        paper-item {
          width: 450px;
        }
        .card-actions {
          text-align: right;
        }
        ha-select {
          width: 100%;
        }
        ha-select:last-child {
          margin-top: 8px;
        }
      `]}},{kind:"method",key:"willUpdate",value:function(e){A(P(r.prototype),"willUpdate",this).call(this,e),e.has("addon")&&this._addonChanged()}},{kind:"method",key:"_setInputDevice",value:function(e){const t=e.target.value;this._selectedInput=t}},{kind:"method",key:"_setOutputDevice",value:function(e){const t=e.target.value;this._selectedOutput=t}},{kind:"method",key:"_addonChanged",value:async function(){if(this._selectedInput=null===this.addon.audio_input?"default":this.addon.audio_input,this._selectedOutput=null===this.addon.audio_output?"default":this.addon.audio_output,this._outputDevices)return;const e={device:"default",name:this.supervisor.localize("addon.configuration.audio.default")};try{const{audio:t}=await(0,f.G)(this.hass),r=Object.keys(t.input).map((e=>({device:e,name:t.input[e]}))),i=Object.keys(t.output).map((e=>({device:e,name:t.output[e]})));this._inputDevices=[e,...r],this._outputDevices=[e,...i]}catch{this._error="Failed to fetch audio hardware",this._inputDevices=[e],this._outputDevices=[e]}}},{kind:"method",key:"_saveSettings",value:async function(e){const t=e.currentTarget;t.progress=!0,this._error=void 0;const r={audio_input:"default"===this._selectedInput?null:this._selectedInput,audio_output:"default"===this._selectedOutput?null:this._selectedOutput};try{var i;await(0,l.d3)(this.hass,this.addon.slug,r),"started"===(null===(i=this.addon)||void 0===i?void 0:i.state)&&await v(this,this.hass,this.supervisor,this.addon)}catch{this._error="Failed to set addon audio device"}t.progress=!1}}]}}),i.oi);var $=r(7426);r(1545),r(3701),r(3927),r(6255),r(4019),r(8900);function x(){x=function(){return e};var e={elementsDefinitionOrder:[["method"],["field"]],initializeInstanceElements:function(e,t){["method","field"].forEach((function(r){t.forEach((function(t){t.kind===r&&"own"===t.placement&&this.defineClassElement(e,t)}),this)}),this)},initializeClassElements:function(e,t){var r=e.prototype;["method","field"].forEach((function(i){t.forEach((function(t){var o=t.placement;if(t.kind===i&&("static"===o||"prototype"===o)){var n="static"===o?e:r;this.defineClassElement(n,t)}}),this)}),this)},defineClassElement:function(e,t){var r=t.descriptor;if("field"===t.kind){var i=t.initializer;r={enumerable:r.enumerable,writable:r.writable,configurable:r.configurable,value:void 0===i?void 0:i.call(e)}}Object.defineProperty(e,t.key,r)},decorateClass:function(e,t){var r=[],i=[],o={static:[],prototype:[],own:[]};if(e.forEach((function(e){this.addElementPlacement(e,o)}),this),e.forEach((function(e){if(!S(e))return r.push(e);var t=this.decorateElement(e,o);r.push(t.element),r.push.apply(r,t.extras),i.push.apply(i,t.finishers)}),this),!t)return{elements:r,finishers:i};var n=this.decorateConstructor(r,t);return i.push.apply(i,n.finishers),n.finishers=i,n},addElementPlacement:function(e,t,r){var i=t[e.placement];if(!r&&-1!==i.indexOf(e.key))throw new TypeError("Duplicated element ("+e.key+")");i.push(e.key)},decorateElement:function(e,t){for(var r=[],i=[],o=e.decorators,n=o.length-1;n>=0;n--){var s=t[e.placement];s.splice(s.indexOf(e.key),1);var a=this.fromElementDescriptor(e),d=this.toElementFinisherExtras((0,o[n])(a)||a);e=d.element,this.addElementPlacement(e,t),d.finisher&&i.push(d.finisher);var l=d.extras;if(l){for(var c=0;c<l.length;c++)this.addElementPlacement(l[c],t);r.push.apply(r,l)}}return{element:e,finishers:i,extras:r}},decorateConstructor:function(e,t){for(var r=[],i=t.length-1;i>=0;i--){var o=this.fromClassDescriptor(e),n=this.toClassDescriptor((0,t[i])(o)||o);if(void 0!==n.finisher&&r.push(n.finisher),void 0!==n.elements){e=n.elements;for(var s=0;s<e.length-1;s++)for(var a=s+1;a<e.length;a++)if(e[s].key===e[a].key&&e[s].placement===e[a].placement)throw new TypeError("Duplicated element ("+e[s].key+")")}}return{elements:e,finishers:r}},fromElementDescriptor:function(e){var t={kind:e.kind,key:e.key,placement:e.placement,descriptor:e.descriptor};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),"field"===e.kind&&(t.initializer=e.initializer),t},toElementDescriptors:function(e){var t;if(void 0!==e)return(t=e,function(e){if(Array.isArray(e))return e}(t)||function(e){if("undefined"!=typeof Symbol&&null!=e[Symbol.iterator]||null!=e["@@iterator"])return Array.from(e)}(t)||function(e,t){if(e){if("string"==typeof e)return j(e,t);var r=Object.prototype.toString.call(e).slice(8,-1);return"Object"===r&&e.constructor&&(r=e.constructor.name),"Map"===r||"Set"===r?Array.from(e):"Arguments"===r||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(r)?j(e,t):void 0}}(t)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()).map((function(e){var t=this.toElementDescriptor(e);return this.disallowProperty(e,"finisher","An element descriptor"),this.disallowProperty(e,"extras","An element descriptor"),t}),this)},toElementDescriptor:function(e){var t=String(e.kind);if("method"!==t&&"field"!==t)throw new TypeError('An element descriptor\'s .kind property must be either "method" or "field", but a decorator created an element descriptor with .kind "'+t+'"');var r=H(e.key),i=String(e.placement);if("static"!==i&&"prototype"!==i&&"own"!==i)throw new TypeError('An element descriptor\'s .placement property must be one of "static", "prototype" or "own", but a decorator created an element descriptor with .placement "'+i+'"');var o=e.descriptor;this.disallowProperty(e,"elements","An element descriptor");var n={kind:t,key:r,placement:i,descriptor:Object.assign({},o)};return"field"!==t?this.disallowProperty(e,"initializer","A method descriptor"):(this.disallowProperty(o,"get","The property descriptor of a field descriptor"),this.disallowProperty(o,"set","The property descriptor of a field descriptor"),this.disallowProperty(o,"value","The property descriptor of a field descriptor"),n.initializer=e.initializer),n},toElementFinisherExtras:function(e){return{element:this.toElementDescriptor(e),finisher:O(e,"finisher"),extras:this.toElementDescriptors(e.extras)}},fromClassDescriptor:function(e){var t={kind:"class",elements:e.map(this.fromElementDescriptor,this)};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),t},toClassDescriptor:function(e){var t=String(e.kind);if("class"!==t)throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator created a class descriptor with .kind "'+t+'"');this.disallowProperty(e,"key","A class descriptor"),this.disallowProperty(e,"placement","A class descriptor"),this.disallowProperty(e,"descriptor","A class descriptor"),this.disallowProperty(e,"initializer","A class descriptor"),this.disallowProperty(e,"extras","A class descriptor");var r=O(e,"finisher");return{elements:this.toElementDescriptors(e.elements),finisher:r}},runClassFinishers:function(e,t){for(var r=0;r<t.length;r++){var i=(0,t[r])(e);if(void 0!==i){if("function"!=typeof i)throw new TypeError("Finishers must return a constructor.");e=i}}return e},disallowProperty:function(e,t,r){if(void 0!==e[t])throw new TypeError(r+" can't have a ."+t+" property.")}};return e}function D(e){var t,r=H(e.key);"method"===e.kind?t={value:e.value,writable:!0,configurable:!0,enumerable:!1}:"get"===e.kind?t={get:e.value,configurable:!0,enumerable:!1}:"set"===e.kind?t={set:e.value,configurable:!0,enumerable:!1}:"field"===e.kind&&(t={configurable:!0,writable:!0,enumerable:!0});var i={kind:"field"===e.kind?"field":"method",key:r,placement:e.static?"static":"field"===e.kind?"own":"prototype",descriptor:t};return e.decorators&&(i.decorators=e.decorators),"field"===e.kind&&(i.initializer=e.value),i}function z(e,t){void 0!==e.descriptor.get?t.descriptor.get=e.descriptor.get:t.descriptor.set=e.descriptor.set}function S(e){return e.decorators&&e.decorators.length}function T(e){return void 0!==e&&!(void 0===e.value&&void 0===e.writable)}function O(e,t){var r=e[t];if(void 0!==r&&"function"!=typeof r)throw new TypeError("Expected '"+t+"' to be a function");return r}function H(e){var t=function(e,t){if("object"!=typeof e||null===e)return e;var r=e[Symbol.toPrimitive];if(void 0!==r){var i=r.call(e,t||"default");if("object"!=typeof i)return i;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===t?String:Number)(e)}(e,"string");return"symbol"==typeof t?t:String(t)}function j(e,t){(null==t||t>e.length)&&(t=e.length);for(var r=0,i=new Array(t);r<t;r++)i[r]=e[r];return i}function V(e,t,r){return V="undefined"!=typeof Reflect&&Reflect.get?Reflect.get:function(e,t,r){var i=function(e,t){for(;!Object.prototype.hasOwnProperty.call(e,t)&&null!==(e=L(e)););return e}(e,t);if(i){var o=Object.getOwnPropertyDescriptor(i,t);return o.get?o.get.call(r):o.value}},V(e,t,r||e)}function L(e){return L=Object.setPrototypeOf?Object.getPrototypeOf:function(e){return e.__proto__||Object.getPrototypeOf(e)},L(e)}const M=["string","select","boolean","integer","float","schema"],I=$.oW.extend([new $.Dy("!secret",{kind:"scalar",construct:e=>`!secret ${e}`})]),F=["password","secret","token"];!function(e,t,r,i){var o=x();if(i)for(var n=0;n<i.length;n++)o=i[n](o);var s=t((function(e){o.initializeInstanceElements(e,a.elements)}),r),a=o.decorateClass(function(e){for(var t=[],r=function(e){return"method"===e.kind&&e.key===n.key&&e.placement===n.placement},i=0;i<e.length;i++){var o,n=e[i];if("method"===n.kind&&(o=t.find(r)))if(T(n.descriptor)||T(o.descriptor)){if(S(n)||S(o))throw new ReferenceError("Duplicated methods ("+n.key+") can't be decorated.");o.descriptor=n.descriptor}else{if(S(n)){if(S(o))throw new ReferenceError("Decorators can't be placed on different accessors with for the same property ("+n.key+").");o.decorators=n.decorators}z(n,o)}else t.push(n)}return t}(s.d.map(D)),e);o.initializeClassElements(s.F,a.elements),o.runClassFinishers(s.F,a.finishers)}([(0,o.Mo)("hassio-addon-config")],(function(e,t){class r extends t{constructor(...t){super(...t),e(this)}}return{F:r,d:[{kind:"field",decorators:[(0,o.Cb)({attribute:!1})],key:"addon",value:void 0},{kind:"field",decorators:[(0,o.Cb)({attribute:!1})],key:"hass",value:void 0},{kind:"field",decorators:[(0,o.Cb)({attribute:!1})],key:"supervisor",value:void 0},{kind:"field",decorators:[(0,o.Cb)({type:Boolean})],key:"_configHasChanged",value:()=>!1},{kind:"field",decorators:[(0,o.Cb)({type:Boolean})],key:"_valid",value:()=>!0},{kind:"field",decorators:[(0,o.SB)()],key:"_canShowSchema",value:()=>!1},{kind:"field",decorators:[(0,o.SB)()],key:"_showOptional",value:()=>!1},{kind:"field",decorators:[(0,o.SB)()],key:"_error",value:void 0},{kind:"field",decorators:[(0,o.SB)()],key:"_options",value:void 0},{kind:"field",decorators:[(0,o.SB)()],key:"_yamlMode",value:()=>!1},{kind:"field",decorators:[(0,o.IO)("ha-yaml-editor")],key:"_editor",value:void 0},{kind:"field",key:"computeLabel",value(){return e=>{var t,r,i,o,n,s;return(null===(t=this.addon.translations[this.hass.language])||void 0===t||null===(r=t.configuration)||void 0===r||null===(i=r[e.name])||void 0===i?void 0:i.name)||(null===(o=this.addon.translations.en)||void 0===o||null===(n=o.configuration)||void 0===n||null===(s=n[e.name])||void 0===s?void 0:s.name)||e.name}}},{kind:"field",key:"computeHelper",value(){return e=>{var t,r,i,o,n,s;return(null===(t=this.addon.translations[this.hass.language])||void 0===t||null===(r=t.configuration)||void 0===r||null===(i=r[e.name])||void 0===i?void 0:i.description)||(null===(o=this.addon.translations.en)||void 0===o||null===(n=o.configuration)||void 0===n||null===(s=n[e.name])||void 0===s?void 0:s.description)||""}}},{kind:"field",key:"_convertSchema",value:()=>(0,n.Z)((e=>e.map((e=>"select"===e.type?{name:e.name,required:e.required,selector:{select:{options:e.options}}}:"string"===e.type?e.multiple?{name:e.name,required:e.required,selector:{select:{options:[],multiple:!0,custom_value:!0}}}:{name:e.name,required:e.required,selector:{text:{type:e.format||F.includes(e.name)?"password":"text"}}}:"boolean"===e.type?{name:e.name,required:e.required,selector:{boolean:{}}}:"schema"===e.type?{name:e.name,required:e.required,selector:{object:{}}}:"float"===e.type||"integer"===e.type?{name:e.name,required:e.required,selector:{number:{mode:"box"}}}:e))))},{kind:"field",key:"_filteredShchema",value:()=>(0,n.Z)(((e,t)=>t.filter((t=>t.name in e||t.required))))},{kind:"method",key:"render",value:function(){const e=!this._yamlMode&&this._canShowSchema&&this.addon.schema,t=e&&JSON.stringify(this.addon.schema)!==JSON.stringify(this._filteredShchema(this.addon.options,this.addon.schema));return i.dy`
      <h1>${this.addon.name}</h1>
      <ha-card>
        <div class="header">
          <h2>
            ${this.supervisor.localize("addon.configuration.options.header")}
          </h2>
          <div class="card-menu">
            <ha-button-menu corner="BOTTOM_START" @action=${this._handleAction}>
              <ha-icon-button
                .label=${this.supervisor.localize("common.menu")}
                .path=${"M12,16A2,2 0 0,1 14,18A2,2 0 0,1 12,20A2,2 0 0,1 10,18A2,2 0 0,1 12,16M12,10A2,2 0 0,1 14,12A2,2 0 0,1 12,14A2,2 0 0,1 10,12A2,2 0 0,1 12,10M12,4A2,2 0 0,1 14,6A2,2 0 0,1 12,8A2,2 0 0,1 10,6A2,2 0 0,1 12,4Z"}
                slot="trigger"
              ></ha-icon-button>
              <mwc-list-item .disabled=${!this._canShowSchema}>
                ${this._yamlMode?this.supervisor.localize("addon.configuration.options.edit_in_ui"):this.supervisor.localize("addon.configuration.options.edit_in_yaml")}
              </mwc-list-item>
              <mwc-list-item class="warning">
                ${this.supervisor.localize("common.reset_defaults")}
              </mwc-list-item>
            </ha-button-menu>
          </div>
        </div>

        <div class="card-content">
          ${e?i.dy`<ha-form
                .data=${this._options}
                @value-changed=${this._configChanged}
                .computeLabel=${this.computeLabel}
                .computeHelper=${this.computeHelper}
                .schema=${this._convertSchema(this._showOptional?this.addon.schema:this._filteredShchema(this.addon.options,this.addon.schema))}
              ></ha-form>`:i.dy` <ha-yaml-editor
                @value-changed=${this._configChanged}
                .yamlSchema=${I}
              ></ha-yaml-editor>`}
          ${this._error?i.dy`<ha-alert alert-type="error">${this._error}</ha-alert>`:""}
          ${!this._yamlMode||this._canShowSchema&&this.addon.schema||this._valid?"":i.dy`
                <ha-alert alert-type="error">
                  ${this.supervisor.localize("addon.configuration.options.invalid_yaml")}
                </ha-alert>
              `}
        </div>
        ${t?i.dy`<ha-formfield
              class="show-additional"
              .label=${this.supervisor.localize("addon.configuration.options.show_unused_optional")}
            >
              <ha-switch
                @change=${this._toggleOptional}
                .checked=${this._showOptional}
              >
              </ha-switch>
            </ha-formfield>`:""}
        <div class="card-actions right">
          <ha-progress-button
            @click=${this._saveTapped}
            .disabled=${!this._configHasChanged||!this._valid}
          >
            ${this.supervisor.localize("common.save")}
          </ha-progress-button>
        </div>
      </ha-card>
    `}},{kind:"method",key:"firstUpdated",value:function(e){V(L(r.prototype),"firstUpdated",this).call(this,e),this._canShowSchema=!this.addon.schema.find((e=>!M.includes(e.type))),this._yamlMode=!this._canShowSchema}},{kind:"method",key:"updated",value:function(e){if(e.has("addon")&&(this._options={...this.addon.options}),V(L(r.prototype),"updated",this).call(this,e),(e.has("_yamlMode")||e.has("_options"))&&this._yamlMode){const e=this._editor;e&&e.setValue(this._options)}}},{kind:"method",key:"_handleAction",value:function(e){switch(e.detail.index){case 0:this._yamlMode=!this._yamlMode;break;case 1:this._resetTapped(e)}}},{kind:"method",key:"_toggleOptional",value:function(){this._showOptional=!this._showOptional}},{kind:"method",key:"_configChanged",value:function(e){this.addon.schema&&this._canShowSchema&&!this._yamlMode?(this._valid=!0,this._configHasChanged=!0,this._options=e.detail.value):(this._configHasChanged=!0,this._valid=e.detail.isValid)}},{kind:"method",key:"_resetTapped",value:async function(e){const t=e.currentTarget;t.progress=!0;if(!await(0,m.g7)(this,{title:this.supervisor.localize("confirm.reset_options.title"),text:this.supervisor.localize("confirm.reset_options.text"),confirmText:this.supervisor.localize("common.reset_options"),dismissText:this.supervisor.localize("common.cancel")}))return void(t.progress=!1);this._error=void 0;const r={options:null};try{await(0,l.d3)(this.hass,this.addon.slug,r),this._configHasChanged=!1;const e={success:!0,response:void 0,path:"options"};(0,s.B)(this,"hass-api-called",e)}catch(e){this._error=this.supervisor.localize("addon.common.update_available","error",(0,c.js)(e))}t.progress=!1}},{kind:"method",key:"_saveTapped",value:async function(e){var t;const r=e.currentTarget,i=this._yamlMode?null===(t=this._editor)||void 0===t?void 0:t.value:this._options,o={success:!0,response:void 0,path:"options"};r.progress=!0,this._error=void 0;try{var n;const e=await(0,l.su)(this.hass,this.addon.slug,i);if(!e.valid)throw Error(e.message);await(0,l.d3)(this.hass,this.addon.slug,{options:i}),this._configHasChanged=!1,"started"===(null===(n=this.addon)||void 0===n?void 0:n.state)&&await v(this,this.hass,this.supervisor,this.addon)}catch(e){this._error=this.supervisor.localize("addon.failed_to_save","error",(0,c.js)(e)),o.success=!1}r.progress=!1,(0,s.B)(this,"hass-api-called",o)}},{kind:"get",static:!0,key:"styles",value:function(){return[h.Qx,p.l,i.iv`
        :host {
          display: block;
        }
        ha-card {
          display: block;
        }
        .card-actions {
          display: flex;
          justify-content: space-between;
        }

        .card-menu {
          float: right;
          z-index: 3;
          --mdc-theme-text-primary-on-background: var(--primary-text-color);
        }
        mwc-list-item[disabled] {
          --mdc-theme-text-primary-on-background: var(--disabled-text-color);
        }
        .header {
          display: flex;
          justify-content: space-between;
        }
        .header h2 {
          color: var(--ha-card-header-color, --primary-text-color);
          font-family: var(--ha-card-header-font-family, inherit);
          font-size: var(--ha-card-header-font-size, 24px);
          letter-spacing: -0.012em;
          line-height: 48px;
          padding: 12px 16px 16px;
          display: block;
          margin-block: 0px;
          font-weight: normal;
        }
        .card-actions.right {
          justify-content: flex-end;
        }

        .show-additional {
          padding: 16px;
        }
      `]}}]}}),i.oi);function B(){B=function(){return e};var e={elementsDefinitionOrder:[["method"],["field"]],initializeInstanceElements:function(e,t){["method","field"].forEach((function(r){t.forEach((function(t){t.kind===r&&"own"===t.placement&&this.defineClassElement(e,t)}),this)}),this)},initializeClassElements:function(e,t){var r=e.prototype;["method","field"].forEach((function(i){t.forEach((function(t){var o=t.placement;if(t.kind===i&&("static"===o||"prototype"===o)){var n="static"===o?e:r;this.defineClassElement(n,t)}}),this)}),this)},defineClassElement:function(e,t){var r=t.descriptor;if("field"===t.kind){var i=t.initializer;r={enumerable:r.enumerable,writable:r.writable,configurable:r.configurable,value:void 0===i?void 0:i.call(e)}}Object.defineProperty(e,t.key,r)},decorateClass:function(e,t){var r=[],i=[],o={static:[],prototype:[],own:[]};if(e.forEach((function(e){this.addElementPlacement(e,o)}),this),e.forEach((function(e){if(!Z(e))return r.push(e);var t=this.decorateElement(e,o);r.push(t.element),r.push.apply(r,t.extras),i.push.apply(i,t.finishers)}),this),!t)return{elements:r,finishers:i};var n=this.decorateConstructor(r,t);return i.push.apply(i,n.finishers),n.finishers=i,n},addElementPlacement:function(e,t,r){var i=t[e.placement];if(!r&&-1!==i.indexOf(e.key))throw new TypeError("Duplicated element ("+e.key+")");i.push(e.key)},decorateElement:function(e,t){for(var r=[],i=[],o=e.decorators,n=o.length-1;n>=0;n--){var s=t[e.placement];s.splice(s.indexOf(e.key),1);var a=this.fromElementDescriptor(e),d=this.toElementFinisherExtras((0,o[n])(a)||a);e=d.element,this.addElementPlacement(e,t),d.finisher&&i.push(d.finisher);var l=d.extras;if(l){for(var c=0;c<l.length;c++)this.addElementPlacement(l[c],t);r.push.apply(r,l)}}return{element:e,finishers:i,extras:r}},decorateConstructor:function(e,t){for(var r=[],i=t.length-1;i>=0;i--){var o=this.fromClassDescriptor(e),n=this.toClassDescriptor((0,t[i])(o)||o);if(void 0!==n.finisher&&r.push(n.finisher),void 0!==n.elements){e=n.elements;for(var s=0;s<e.length-1;s++)for(var a=s+1;a<e.length;a++)if(e[s].key===e[a].key&&e[s].placement===e[a].placement)throw new TypeError("Duplicated element ("+e[s].key+")")}}return{elements:e,finishers:r}},fromElementDescriptor:function(e){var t={kind:e.kind,key:e.key,placement:e.placement,descriptor:e.descriptor};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),"field"===e.kind&&(t.initializer=e.initializer),t},toElementDescriptors:function(e){var t;if(void 0!==e)return(t=e,function(e){if(Array.isArray(e))return e}(t)||function(e){if("undefined"!=typeof Symbol&&null!=e[Symbol.iterator]||null!=e["@@iterator"])return Array.from(e)}(t)||function(e,t){if(e){if("string"==typeof e)return Y(e,t);var r=Object.prototype.toString.call(e).slice(8,-1);return"Object"===r&&e.constructor&&(r=e.constructor.name),"Map"===r||"Set"===r?Array.from(e):"Arguments"===r||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(r)?Y(e,t):void 0}}(t)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()).map((function(e){var t=this.toElementDescriptor(e);return this.disallowProperty(e,"finisher","An element descriptor"),this.disallowProperty(e,"extras","An element descriptor"),t}),this)},toElementDescriptor:function(e){var t=String(e.kind);if("method"!==t&&"field"!==t)throw new TypeError('An element descriptor\'s .kind property must be either "method" or "field", but a decorator created an element descriptor with .kind "'+t+'"');var r=Q(e.key),i=String(e.placement);if("static"!==i&&"prototype"!==i&&"own"!==i)throw new TypeError('An element descriptor\'s .placement property must be one of "static", "prototype" or "own", but a decorator created an element descriptor with .placement "'+i+'"');var o=e.descriptor;this.disallowProperty(e,"elements","An element descriptor");var n={kind:t,key:r,placement:i,descriptor:Object.assign({},o)};return"field"!==t?this.disallowProperty(e,"initializer","A method descriptor"):(this.disallowProperty(o,"get","The property descriptor of a field descriptor"),this.disallowProperty(o,"set","The property descriptor of a field descriptor"),this.disallowProperty(o,"value","The property descriptor of a field descriptor"),n.initializer=e.initializer),n},toElementFinisherExtras:function(e){return{element:this.toElementDescriptor(e),finisher:q(e,"finisher"),extras:this.toElementDescriptors(e.extras)}},fromClassDescriptor:function(e){var t={kind:"class",elements:e.map(this.fromElementDescriptor,this)};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),t},toClassDescriptor:function(e){var t=String(e.kind);if("class"!==t)throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator created a class descriptor with .kind "'+t+'"');this.disallowProperty(e,"key","A class descriptor"),this.disallowProperty(e,"placement","A class descriptor"),this.disallowProperty(e,"descriptor","A class descriptor"),this.disallowProperty(e,"initializer","A class descriptor"),this.disallowProperty(e,"extras","A class descriptor");var r=q(e,"finisher");return{elements:this.toElementDescriptors(e.elements),finisher:r}},runClassFinishers:function(e,t){for(var r=0;r<t.length;r++){var i=(0,t[r])(e);if(void 0!==i){if("function"!=typeof i)throw new TypeError("Finishers must return a constructor.");e=i}}return e},disallowProperty:function(e,t,r){if(void 0!==e[t])throw new TypeError(r+" can't have a ."+t+" property.")}};return e}function R(e){var t,r=Q(e.key);"method"===e.kind?t={value:e.value,writable:!0,configurable:!0,enumerable:!1}:"get"===e.kind?t={get:e.value,configurable:!0,enumerable:!1}:"set"===e.kind?t={set:e.value,configurable:!0,enumerable:!1}:"field"===e.kind&&(t={configurable:!0,writable:!0,enumerable:!0});var i={kind:"field"===e.kind?"field":"method",key:r,placement:e.static?"static":"field"===e.kind?"own":"prototype",descriptor:t};return e.decorators&&(i.decorators=e.decorators),"field"===e.kind&&(i.initializer=e.value),i}function U(e,t){void 0!==e.descriptor.get?t.descriptor.get=e.descriptor.get:t.descriptor.set=e.descriptor.set}function Z(e){return e.decorators&&e.decorators.length}function N(e){return void 0!==e&&!(void 0===e.value&&void 0===e.writable)}function q(e,t){var r=e[t];if(void 0!==r&&"function"!=typeof r)throw new TypeError("Expected '"+t+"' to be a function");return r}function Q(e){var t=function(e,t){if("object"!=typeof e||null===e)return e;var r=e[Symbol.toPrimitive];if(void 0!==r){var i=r.call(e,t||"default");if("object"!=typeof i)return i;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===t?String:Number)(e)}(e,"string");return"symbol"==typeof t?t:String(t)}function Y(e,t){(null==t||t>e.length)&&(t=e.length);for(var r=0,i=new Array(t);r<t;r++)i[r]=e[r];return i}function W(e,t,r){return W="undefined"!=typeof Reflect&&Reflect.get?Reflect.get:function(e,t,r){var i=function(e,t){for(;!Object.prototype.hasOwnProperty.call(e,t)&&null!==(e=K(e)););return e}(e,t);if(i){var o=Object.getOwnPropertyDescriptor(i,t);return o.get?o.get.call(r):o.value}},W(e,t,r||e)}function K(e){return K=Object.setPrototypeOf?Object.getPrototypeOf:function(e){return e.__proto__||Object.getPrototypeOf(e)},K(e)}!function(e,t,r,i){var o=B();if(i)for(var n=0;n<i.length;n++)o=i[n](o);var s=t((function(e){o.initializeInstanceElements(e,a.elements)}),r),a=o.decorateClass(function(e){for(var t=[],r=function(e){return"method"===e.kind&&e.key===n.key&&e.placement===n.placement},i=0;i<e.length;i++){var o,n=e[i];if("method"===n.kind&&(o=t.find(r)))if(N(n.descriptor)||N(o.descriptor)){if(Z(n)||Z(o))throw new ReferenceError("Duplicated methods ("+n.key+") can't be decorated.");o.descriptor=n.descriptor}else{if(Z(n)){if(Z(o))throw new ReferenceError("Decorators can't be placed on different accessors with for the same property ("+n.key+").");o.decorators=n.decorators}U(n,o)}else t.push(n)}return t}(s.d.map(R)),e);o.initializeClassElements(s.F,a.elements),o.runClassFinishers(s.F,a.finishers)}([(0,o.Mo)("hassio-addon-network")],(function(e,t){class r extends t{constructor(...t){super(...t),e(this)}}return{F:r,d:[{kind:"field",decorators:[(0,o.Cb)({attribute:!1})],key:"hass",value:void 0},{kind:"field",decorators:[(0,o.Cb)({attribute:!1})],key:"supervisor",value:void 0},{kind:"field",decorators:[(0,o.Cb)({attribute:!1})],key:"addon",value:void 0},{kind:"field",decorators:[(0,o.SB)()],key:"_showOptional",value:()=>!1},{kind:"field",decorators:[(0,o.SB)()],key:"_configHasChanged",value:()=>!1},{kind:"field",decorators:[(0,o.SB)()],key:"_error",value:void 0},{kind:"field",decorators:[(0,o.SB)()],key:"_config",value:void 0},{kind:"method",key:"connectedCallback",value:function(){W(K(r.prototype),"connectedCallback",this).call(this),this._setNetworkConfig()}},{kind:"method",key:"render",value:function(){var e;if(!this._config)return i.dy``;const t=Object.keys(this._config).find((e=>null===this._config[e]));return i.dy`
      <ha-card
        .header=${this.supervisor.localize("addon.configuration.network.header")}
      >
        <div class="card-content">
          <p>
            ${this.supervisor.localize("addon.configuration.network.introduction")}
          </p>
          ${this._error?i.dy`<ha-alert alert-type="error">${this._error}</ha-alert>`:""}

          <ha-form
            .data=${this._config}
            @value-changed=${this._configChanged}
            .computeLabel=${this._computeLabel}
            .computeHelper=${this._computeHelper}
            .schema=${this._createSchema(this._config,this._showOptional,(null===(e=this.hass.userData)||void 0===e?void 0:e.showAdvanced)||!1)}
          ></ha-form>
        </div>
        ${t?i.dy`<ha-formfield
              class="show-optional"
              .label=${this.supervisor.localize("addon.configuration.network.show_disabled")}
            >
              <ha-switch
                @change=${this._toggleOptional}
                .checked=${this._showOptional}
              >
              </ha-switch>
            </ha-formfield>`:""}
        <div class="card-actions">
          <ha-progress-button class="warning" @click=${this._resetTapped}>
            ${this.supervisor.localize("common.reset_defaults")}
          </ha-progress-button>
          <ha-progress-button
            @click=${this._saveTapped}
            .disabled=${!this._configHasChanged}
          >
            ${this.supervisor.localize("common.save")}
          </ha-progress-button>
        </div>
      </ha-card>
    `}},{kind:"method",key:"update",value:function(e){W(K(r.prototype),"update",this).call(this,e),e.has("addon")&&this._setNetworkConfig()}},{kind:"field",key:"_createSchema",value:()=>(0,n.Z)(((e,t,r)=>(t?Object.keys(e):Object.keys(e).filter((t=>null!==e[t]))).map((e=>({name:e,selector:{number:{mode:"box",min:0,max:65535,unit_of_measurement:r?e:void 0}}})))))},{kind:"field",key:"_computeLabel",value:()=>e=>""},{kind:"field",key:"_computeHelper",value(){return e=>{var t,r,i,o,n;return(null===(t=this.addon.translations[this.hass.language])||void 0===t||null===(r=t.network)||void 0===r?void 0:r[e.name])||(null===(i=this.addon.translations.en)||void 0===i||null===(o=i.network)||void 0===o?void 0:o[e.name])||(null===(n=this.addon.network_description)||void 0===n?void 0:n[e.name])||e.name}}},{kind:"method",key:"_setNetworkConfig",value:function(){this._config=this.addon.network||{}}},{kind:"method",key:"_configChanged",value:async function(e){this._configHasChanged=!0,this._config=e.detail.value}},{kind:"method",key:"_resetTapped",value:async function(e){const t=e.currentTarget,r={network:null};try{var i;await(0,l.d3)(this.hass,this.addon.slug,r),this._configHasChanged=!1;const e={success:!0,response:void 0,path:"option"};t.actionSuccess(),(0,s.B)(this,"hass-api-called",e),"started"===(null===(i=this.addon)||void 0===i?void 0:i.state)&&await v(this,this.hass,this.supervisor,this.addon)}catch(e){this._error=this.supervisor.localize("addon.failed_to_reset","error",(0,c.js)(e)),t.actionError()}}},{kind:"method",key:"_toggleOptional",value:function(){this._showOptional=!this._showOptional}},{kind:"method",key:"_saveTapped",value:async function(e){const t=e.currentTarget;this._error=void 0;const r={};Object.entries(this._config).forEach((([e,t])=>{r[e]=null!=t?t:null}));const i={network:r};try{var o;await(0,l.d3)(this.hass,this.addon.slug,i),this._configHasChanged=!1;const e={success:!0,response:void 0,path:"option"};t.actionSuccess(),(0,s.B)(this,"hass-api-called",e),"started"===(null===(o=this.addon)||void 0===o?void 0:o.state)&&await v(this,this.hass,this.supervisor,this.addon)}catch(e){this._error=this.supervisor.localize("addon.failed_to_save","error",(0,c.js)(e)),t.actionError()}}},{kind:"get",static:!0,key:"styles",value:function(){return[h.Qx,p.l,i.iv`
        :host {
          display: block;
        }
        ha-card {
          display: block;
        }
        .card-actions {
          display: flex;
          justify-content: space-between;
        }
        .show-optional {
          padding: 16px;
        }
      `]}}]}}),i.oi);var G=r(8199);function J(){J=function(){return e};var e={elementsDefinitionOrder:[["method"],["field"]],initializeInstanceElements:function(e,t){["method","field"].forEach((function(r){t.forEach((function(t){t.kind===r&&"own"===t.placement&&this.defineClassElement(e,t)}),this)}),this)},initializeClassElements:function(e,t){var r=e.prototype;["method","field"].forEach((function(i){t.forEach((function(t){var o=t.placement;if(t.kind===i&&("static"===o||"prototype"===o)){var n="static"===o?e:r;this.defineClassElement(n,t)}}),this)}),this)},defineClassElement:function(e,t){var r=t.descriptor;if("field"===t.kind){var i=t.initializer;r={enumerable:r.enumerable,writable:r.writable,configurable:r.configurable,value:void 0===i?void 0:i.call(e)}}Object.defineProperty(e,t.key,r)},decorateClass:function(e,t){var r=[],i=[],o={static:[],prototype:[],own:[]};if(e.forEach((function(e){this.addElementPlacement(e,o)}),this),e.forEach((function(e){if(!te(e))return r.push(e);var t=this.decorateElement(e,o);r.push(t.element),r.push.apply(r,t.extras),i.push.apply(i,t.finishers)}),this),!t)return{elements:r,finishers:i};var n=this.decorateConstructor(r,t);return i.push.apply(i,n.finishers),n.finishers=i,n},addElementPlacement:function(e,t,r){var i=t[e.placement];if(!r&&-1!==i.indexOf(e.key))throw new TypeError("Duplicated element ("+e.key+")");i.push(e.key)},decorateElement:function(e,t){for(var r=[],i=[],o=e.decorators,n=o.length-1;n>=0;n--){var s=t[e.placement];s.splice(s.indexOf(e.key),1);var a=this.fromElementDescriptor(e),d=this.toElementFinisherExtras((0,o[n])(a)||a);e=d.element,this.addElementPlacement(e,t),d.finisher&&i.push(d.finisher);var l=d.extras;if(l){for(var c=0;c<l.length;c++)this.addElementPlacement(l[c],t);r.push.apply(r,l)}}return{element:e,finishers:i,extras:r}},decorateConstructor:function(e,t){for(var r=[],i=t.length-1;i>=0;i--){var o=this.fromClassDescriptor(e),n=this.toClassDescriptor((0,t[i])(o)||o);if(void 0!==n.finisher&&r.push(n.finisher),void 0!==n.elements){e=n.elements;for(var s=0;s<e.length-1;s++)for(var a=s+1;a<e.length;a++)if(e[s].key===e[a].key&&e[s].placement===e[a].placement)throw new TypeError("Duplicated element ("+e[s].key+")")}}return{elements:e,finishers:r}},fromElementDescriptor:function(e){var t={kind:e.kind,key:e.key,placement:e.placement,descriptor:e.descriptor};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),"field"===e.kind&&(t.initializer=e.initializer),t},toElementDescriptors:function(e){var t;if(void 0!==e)return(t=e,function(e){if(Array.isArray(e))return e}(t)||function(e){if("undefined"!=typeof Symbol&&null!=e[Symbol.iterator]||null!=e["@@iterator"])return Array.from(e)}(t)||function(e,t){if(e){if("string"==typeof e)return ne(e,t);var r=Object.prototype.toString.call(e).slice(8,-1);return"Object"===r&&e.constructor&&(r=e.constructor.name),"Map"===r||"Set"===r?Array.from(e):"Arguments"===r||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(r)?ne(e,t):void 0}}(t)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()).map((function(e){var t=this.toElementDescriptor(e);return this.disallowProperty(e,"finisher","An element descriptor"),this.disallowProperty(e,"extras","An element descriptor"),t}),this)},toElementDescriptor:function(e){var t=String(e.kind);if("method"!==t&&"field"!==t)throw new TypeError('An element descriptor\'s .kind property must be either "method" or "field", but a decorator created an element descriptor with .kind "'+t+'"');var r=oe(e.key),i=String(e.placement);if("static"!==i&&"prototype"!==i&&"own"!==i)throw new TypeError('An element descriptor\'s .placement property must be one of "static", "prototype" or "own", but a decorator created an element descriptor with .placement "'+i+'"');var o=e.descriptor;this.disallowProperty(e,"elements","An element descriptor");var n={kind:t,key:r,placement:i,descriptor:Object.assign({},o)};return"field"!==t?this.disallowProperty(e,"initializer","A method descriptor"):(this.disallowProperty(o,"get","The property descriptor of a field descriptor"),this.disallowProperty(o,"set","The property descriptor of a field descriptor"),this.disallowProperty(o,"value","The property descriptor of a field descriptor"),n.initializer=e.initializer),n},toElementFinisherExtras:function(e){return{element:this.toElementDescriptor(e),finisher:ie(e,"finisher"),extras:this.toElementDescriptors(e.extras)}},fromClassDescriptor:function(e){var t={kind:"class",elements:e.map(this.fromElementDescriptor,this)};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),t},toClassDescriptor:function(e){var t=String(e.kind);if("class"!==t)throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator created a class descriptor with .kind "'+t+'"');this.disallowProperty(e,"key","A class descriptor"),this.disallowProperty(e,"placement","A class descriptor"),this.disallowProperty(e,"descriptor","A class descriptor"),this.disallowProperty(e,"initializer","A class descriptor"),this.disallowProperty(e,"extras","A class descriptor");var r=ie(e,"finisher");return{elements:this.toElementDescriptors(e.elements),finisher:r}},runClassFinishers:function(e,t){for(var r=0;r<t.length;r++){var i=(0,t[r])(e);if(void 0!==i){if("function"!=typeof i)throw new TypeError("Finishers must return a constructor.");e=i}}return e},disallowProperty:function(e,t,r){if(void 0!==e[t])throw new TypeError(r+" can't have a ."+t+" property.")}};return e}function X(e){var t,r=oe(e.key);"method"===e.kind?t={value:e.value,writable:!0,configurable:!0,enumerable:!1}:"get"===e.kind?t={get:e.value,configurable:!0,enumerable:!1}:"set"===e.kind?t={set:e.value,configurable:!0,enumerable:!1}:"field"===e.kind&&(t={configurable:!0,writable:!0,enumerable:!0});var i={kind:"field"===e.kind?"field":"method",key:r,placement:e.static?"static":"field"===e.kind?"own":"prototype",descriptor:t};return e.decorators&&(i.decorators=e.decorators),"field"===e.kind&&(i.initializer=e.value),i}function ee(e,t){void 0!==e.descriptor.get?t.descriptor.get=e.descriptor.get:t.descriptor.set=e.descriptor.set}function te(e){return e.decorators&&e.decorators.length}function re(e){return void 0!==e&&!(void 0===e.value&&void 0===e.writable)}function ie(e,t){var r=e[t];if(void 0!==r&&"function"!=typeof r)throw new TypeError("Expected '"+t+"' to be a function");return r}function oe(e){var t=function(e,t){if("object"!=typeof e||null===e)return e;var r=e[Symbol.toPrimitive];if(void 0!==r){var i=r.call(e,t||"default");if("object"!=typeof i)return i;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===t?String:Number)(e)}(e,"string");return"symbol"==typeof t?t:String(t)}function ne(e,t){(null==t||t>e.length)&&(t=e.length);for(var r=0,i=new Array(t);r<t;r++)i[r]=e[r];return i}!function(e,t,r,i){var o=J();if(i)for(var n=0;n<i.length;n++)o=i[n](o);var s=t((function(e){o.initializeInstanceElements(e,a.elements)}),r),a=o.decorateClass(function(e){for(var t=[],r=function(e){return"method"===e.kind&&e.key===n.key&&e.placement===n.placement},i=0;i<e.length;i++){var o,n=e[i];if("method"===n.kind&&(o=t.find(r)))if(re(n.descriptor)||re(o.descriptor)){if(te(n)||te(o))throw new ReferenceError("Duplicated methods ("+n.key+") can't be decorated.");o.descriptor=n.descriptor}else{if(te(n)){if(te(o))throw new ReferenceError("Decorators can't be placed on different accessors with for the same property ("+n.key+").");o.decorators=n.decorators}ee(n,o)}else t.push(n)}return t}(s.d.map(X)),e);o.initializeClassElements(s.F,a.elements),o.runClassFinishers(s.F,a.finishers)}([(0,o.Mo)("hassio-addon-config-tab")],(function(e,t){return{F:class extends t{constructor(...t){super(...t),e(this)}},d:[{kind:"field",decorators:[(0,o.Cb)({attribute:!1})],key:"hass",value:void 0},{kind:"field",decorators:[(0,o.Cb)({attribute:!1})],key:"supervisor",value:void 0},{kind:"field",decorators:[(0,o.Cb)({attribute:!1})],key:"addon",value:void 0},{kind:"method",key:"render",value:function(){if(!this.addon)return i.dy`<ha-circular-progress active></ha-circular-progress>`;const e=this.addon.options&&Object.keys(this.addon.options).length||this.addon.schema&&Object.keys(this.addon.schema).length;return i.dy`
      <div class="content">
        ${e||this.addon.network||this.addon.audio?i.dy`
              ${e?i.dy`
                    <hassio-addon-config
                      .hass=${this.hass}
                      .addon=${this.addon}
                      .supervisor=${this.supervisor}
                    ></hassio-addon-config>
                  `:""}
              ${this.addon.network?i.dy`
                    <hassio-addon-network
                      .hass=${this.hass}
                      .addon=${this.addon}
                      .supervisor=${this.supervisor}
                    ></hassio-addon-network>
                  `:""}
              ${this.addon.audio?i.dy`
                    <hassio-addon-audio
                      .hass=${this.hass}
                      .addon=${this.addon}
                      .supervisor=${this.supervisor}
                    ></hassio-addon-audio>
                  `:""}
            `:this.supervisor.localize("addon.configuration.no_configuration")}
      </div>
    `}},{kind:"get",static:!0,key:"styles",value:function(){return[h.Qx,p.l,i.iv`
        .content {
          margin: auto;
          padding: 8px;
          max-width: 1024px;
        }
        hassio-addon-network,
        hassio-addon-audio,
        hassio-addon-config {
          margin-bottom: 24px;
        }
      `]}}]}}),i.oi);r(3546);function se(){se=function(){return e};var e={elementsDefinitionOrder:[["method"],["field"]],initializeInstanceElements:function(e,t){["method","field"].forEach((function(r){t.forEach((function(t){t.kind===r&&"own"===t.placement&&this.defineClassElement(e,t)}),this)}),this)},initializeClassElements:function(e,t){var r=e.prototype;["method","field"].forEach((function(i){t.forEach((function(t){var o=t.placement;if(t.kind===i&&("static"===o||"prototype"===o)){var n="static"===o?e:r;this.defineClassElement(n,t)}}),this)}),this)},defineClassElement:function(e,t){var r=t.descriptor;if("field"===t.kind){var i=t.initializer;r={enumerable:r.enumerable,writable:r.writable,configurable:r.configurable,value:void 0===i?void 0:i.call(e)}}Object.defineProperty(e,t.key,r)},decorateClass:function(e,t){var r=[],i=[],o={static:[],prototype:[],own:[]};if(e.forEach((function(e){this.addElementPlacement(e,o)}),this),e.forEach((function(e){if(!le(e))return r.push(e);var t=this.decorateElement(e,o);r.push(t.element),r.push.apply(r,t.extras),i.push.apply(i,t.finishers)}),this),!t)return{elements:r,finishers:i};var n=this.decorateConstructor(r,t);return i.push.apply(i,n.finishers),n.finishers=i,n},addElementPlacement:function(e,t,r){var i=t[e.placement];if(!r&&-1!==i.indexOf(e.key))throw new TypeError("Duplicated element ("+e.key+")");i.push(e.key)},decorateElement:function(e,t){for(var r=[],i=[],o=e.decorators,n=o.length-1;n>=0;n--){var s=t[e.placement];s.splice(s.indexOf(e.key),1);var a=this.fromElementDescriptor(e),d=this.toElementFinisherExtras((0,o[n])(a)||a);e=d.element,this.addElementPlacement(e,t),d.finisher&&i.push(d.finisher);var l=d.extras;if(l){for(var c=0;c<l.length;c++)this.addElementPlacement(l[c],t);r.push.apply(r,l)}}return{element:e,finishers:i,extras:r}},decorateConstructor:function(e,t){for(var r=[],i=t.length-1;i>=0;i--){var o=this.fromClassDescriptor(e),n=this.toClassDescriptor((0,t[i])(o)||o);if(void 0!==n.finisher&&r.push(n.finisher),void 0!==n.elements){e=n.elements;for(var s=0;s<e.length-1;s++)for(var a=s+1;a<e.length;a++)if(e[s].key===e[a].key&&e[s].placement===e[a].placement)throw new TypeError("Duplicated element ("+e[s].key+")")}}return{elements:e,finishers:r}},fromElementDescriptor:function(e){var t={kind:e.kind,key:e.key,placement:e.placement,descriptor:e.descriptor};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),"field"===e.kind&&(t.initializer=e.initializer),t},toElementDescriptors:function(e){var t;if(void 0!==e)return(t=e,function(e){if(Array.isArray(e))return e}(t)||function(e){if("undefined"!=typeof Symbol&&null!=e[Symbol.iterator]||null!=e["@@iterator"])return Array.from(e)}(t)||function(e,t){if(e){if("string"==typeof e)return ue(e,t);var r=Object.prototype.toString.call(e).slice(8,-1);return"Object"===r&&e.constructor&&(r=e.constructor.name),"Map"===r||"Set"===r?Array.from(e):"Arguments"===r||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(r)?ue(e,t):void 0}}(t)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()).map((function(e){var t=this.toElementDescriptor(e);return this.disallowProperty(e,"finisher","An element descriptor"),this.disallowProperty(e,"extras","An element descriptor"),t}),this)},toElementDescriptor:function(e){var t=String(e.kind);if("method"!==t&&"field"!==t)throw new TypeError('An element descriptor\'s .kind property must be either "method" or "field", but a decorator created an element descriptor with .kind "'+t+'"');var r=pe(e.key),i=String(e.placement);if("static"!==i&&"prototype"!==i&&"own"!==i)throw new TypeError('An element descriptor\'s .placement property must be one of "static", "prototype" or "own", but a decorator created an element descriptor with .placement "'+i+'"');var o=e.descriptor;this.disallowProperty(e,"elements","An element descriptor");var n={kind:t,key:r,placement:i,descriptor:Object.assign({},o)};return"field"!==t?this.disallowProperty(e,"initializer","A method descriptor"):(this.disallowProperty(o,"get","The property descriptor of a field descriptor"),this.disallowProperty(o,"set","The property descriptor of a field descriptor"),this.disallowProperty(o,"value","The property descriptor of a field descriptor"),n.initializer=e.initializer),n},toElementFinisherExtras:function(e){return{element:this.toElementDescriptor(e),finisher:he(e,"finisher"),extras:this.toElementDescriptors(e.extras)}},fromClassDescriptor:function(e){var t={kind:"class",elements:e.map(this.fromElementDescriptor,this)};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),t},toClassDescriptor:function(e){var t=String(e.kind);if("class"!==t)throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator created a class descriptor with .kind "'+t+'"');this.disallowProperty(e,"key","A class descriptor"),this.disallowProperty(e,"placement","A class descriptor"),this.disallowProperty(e,"descriptor","A class descriptor"),this.disallowProperty(e,"initializer","A class descriptor"),this.disallowProperty(e,"extras","A class descriptor");var r=he(e,"finisher");return{elements:this.toElementDescriptors(e.elements),finisher:r}},runClassFinishers:function(e,t){for(var r=0;r<t.length;r++){var i=(0,t[r])(e);if(void 0!==i){if("function"!=typeof i)throw new TypeError("Finishers must return a constructor.");e=i}}return e},disallowProperty:function(e,t,r){if(void 0!==e[t])throw new TypeError(r+" can't have a ."+t+" property.")}};return e}function ae(e){var t,r=pe(e.key);"method"===e.kind?t={value:e.value,writable:!0,configurable:!0,enumerable:!1}:"get"===e.kind?t={get:e.value,configurable:!0,enumerable:!1}:"set"===e.kind?t={set:e.value,configurable:!0,enumerable:!1}:"field"===e.kind&&(t={configurable:!0,writable:!0,enumerable:!0});var i={kind:"field"===e.kind?"field":"method",key:r,placement:e.static?"static":"field"===e.kind?"own":"prototype",descriptor:t};return e.decorators&&(i.decorators=e.decorators),"field"===e.kind&&(i.initializer=e.value),i}function de(e,t){void 0!==e.descriptor.get?t.descriptor.get=e.descriptor.get:t.descriptor.set=e.descriptor.set}function le(e){return e.decorators&&e.decorators.length}function ce(e){return void 0!==e&&!(void 0===e.value&&void 0===e.writable)}function he(e,t){var r=e[t];if(void 0!==r&&"function"!=typeof r)throw new TypeError("Expected '"+t+"' to be a function");return r}function pe(e){var t=function(e,t){if("object"!=typeof e||null===e)return e;var r=e[Symbol.toPrimitive];if(void 0!==r){var i=r.call(e,t||"default");if("object"!=typeof i)return i;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===t?String:Number)(e)}(e,"string");return"symbol"==typeof t?t:String(t)}function ue(e,t){(null==t||t>e.length)&&(t=e.length);for(var r=0,i=new Array(t);r<t;r++)i[r]=e[r];return i}function fe(e,t,r){return fe="undefined"!=typeof Reflect&&Reflect.get?Reflect.get:function(e,t,r){var i=function(e,t){for(;!Object.prototype.hasOwnProperty.call(e,t)&&null!==(e=me(e)););return e}(e,t);if(i){var o=Object.getOwnPropertyDescriptor(i,t);return o.get?o.get.call(r):o.value}},fe(e,t,r||e)}function me(e){return me=Object.setPrototypeOf?Object.getPrototypeOf:function(e){return e.__proto__||Object.getPrototypeOf(e)},me(e)}!function(e,t,r,i){var o=se();if(i)for(var n=0;n<i.length;n++)o=i[n](o);var s=t((function(e){o.initializeInstanceElements(e,a.elements)}),r),a=o.decorateClass(function(e){for(var t=[],r=function(e){return"method"===e.kind&&e.key===n.key&&e.placement===n.placement},i=0;i<e.length;i++){var o,n=e[i];if("method"===n.kind&&(o=t.find(r)))if(ce(n.descriptor)||ce(o.descriptor)){if(le(n)||le(o))throw new ReferenceError("Duplicated methods ("+n.key+") can't be decorated.");o.descriptor=n.descriptor}else{if(le(n)){if(le(o))throw new ReferenceError("Decorators can't be placed on different accessors with for the same property ("+n.key+").");o.decorators=n.decorators}de(n,o)}else t.push(n)}return t}(s.d.map(ae)),e);o.initializeClassElements(s.F,a.elements),o.runClassFinishers(s.F,a.finishers)}([(0,o.Mo)("hassio-addon-documentation-tab")],(function(e,t){class r extends t{constructor(...t){super(...t),e(this)}}return{F:r,d:[{kind:"field",decorators:[(0,o.Cb)({attribute:!1})],key:"hass",value:void 0},{kind:"field",decorators:[(0,o.Cb)({attribute:!1})],key:"supervisor",value:void 0},{kind:"field",decorators:[(0,o.Cb)({attribute:!1})],key:"addon",value:void 0},{kind:"field",decorators:[(0,o.SB)()],key:"_error",value:void 0},{kind:"field",decorators:[(0,o.SB)()],key:"_content",value:void 0},{kind:"method",key:"connectedCallback",value:async function(){fe(me(r.prototype),"connectedCallback",this).call(this),await this._loadData()}},{kind:"method",key:"render",value:function(){return this.addon?i.dy`
      <div class="content">
        <ha-card>
          ${this._error?i.dy`<ha-alert alert-type="error">${this._error}</ha-alert>`:""}
          <div class="card-content">
            ${this._content?i.dy`<ha-markdown .content=${this._content}></ha-markdown>`:i.dy`<hass-loading-screen no-toolbar></hass-loading-screen>`}
          </div>
        </ha-card>
      </div>
    `:i.dy`<ha-circular-progress active></ha-circular-progress>`}},{kind:"get",static:!0,key:"styles",value:function(){return[h.Qx,p.l,i.iv`
        ha-card {
          display: block;
        }
        .content {
          margin: auto;
          padding: 8px;
          max-width: 1024px;
        }
        ha-markdown {
          padding: 16px;
        }
      `]}},{kind:"method",key:"_loadData",value:async function(){this._error=void 0;try{this._content=await(0,l.ii)(this.hass,this.addon.slug)}catch(e){this._error=this.supervisor.localize("addon.documentation.get_logs","error",(0,c.js)(e))}}}]}}),i.oi);var ve=r(8636),ye=r(3864);function ge(){ge=function(){return e};var e={elementsDefinitionOrder:[["method"],["field"]],initializeInstanceElements:function(e,t){["method","field"].forEach((function(r){t.forEach((function(t){t.kind===r&&"own"===t.placement&&this.defineClassElement(e,t)}),this)}),this)},initializeClassElements:function(e,t){var r=e.prototype;["method","field"].forEach((function(i){t.forEach((function(t){var o=t.placement;if(t.kind===i&&("static"===o||"prototype"===o)){var n="static"===o?e:r;this.defineClassElement(n,t)}}),this)}),this)},defineClassElement:function(e,t){var r=t.descriptor;if("field"===t.kind){var i=t.initializer;r={enumerable:r.enumerable,writable:r.writable,configurable:r.configurable,value:void 0===i?void 0:i.call(e)}}Object.defineProperty(e,t.key,r)},decorateClass:function(e,t){var r=[],i=[],o={static:[],prototype:[],own:[]};if(e.forEach((function(e){this.addElementPlacement(e,o)}),this),e.forEach((function(e){if(!we(e))return r.push(e);var t=this.decorateElement(e,o);r.push(t.element),r.push.apply(r,t.extras),i.push.apply(i,t.finishers)}),this),!t)return{elements:r,finishers:i};var n=this.decorateConstructor(r,t);return i.push.apply(i,n.finishers),n.finishers=i,n},addElementPlacement:function(e,t,r){var i=t[e.placement];if(!r&&-1!==i.indexOf(e.key))throw new TypeError("Duplicated element ("+e.key+")");i.push(e.key)},decorateElement:function(e,t){for(var r=[],i=[],o=e.decorators,n=o.length-1;n>=0;n--){var s=t[e.placement];s.splice(s.indexOf(e.key),1);var a=this.fromElementDescriptor(e),d=this.toElementFinisherExtras((0,o[n])(a)||a);e=d.element,this.addElementPlacement(e,t),d.finisher&&i.push(d.finisher);var l=d.extras;if(l){for(var c=0;c<l.length;c++)this.addElementPlacement(l[c],t);r.push.apply(r,l)}}return{element:e,finishers:i,extras:r}},decorateConstructor:function(e,t){for(var r=[],i=t.length-1;i>=0;i--){var o=this.fromClassDescriptor(e),n=this.toClassDescriptor((0,t[i])(o)||o);if(void 0!==n.finisher&&r.push(n.finisher),void 0!==n.elements){e=n.elements;for(var s=0;s<e.length-1;s++)for(var a=s+1;a<e.length;a++)if(e[s].key===e[a].key&&e[s].placement===e[a].placement)throw new TypeError("Duplicated element ("+e[s].key+")")}}return{elements:e,finishers:r}},fromElementDescriptor:function(e){var t={kind:e.kind,key:e.key,placement:e.placement,descriptor:e.descriptor};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),"field"===e.kind&&(t.initializer=e.initializer),t},toElementDescriptors:function(e){var t;if(void 0!==e)return(t=e,function(e){if(Array.isArray(e))return e}(t)||function(e){if("undefined"!=typeof Symbol&&null!=e[Symbol.iterator]||null!=e["@@iterator"])return Array.from(e)}(t)||function(e,t){if(e){if("string"==typeof e)return Ae(e,t);var r=Object.prototype.toString.call(e).slice(8,-1);return"Object"===r&&e.constructor&&(r=e.constructor.name),"Map"===r||"Set"===r?Array.from(e):"Arguments"===r||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(r)?Ae(e,t):void 0}}(t)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()).map((function(e){var t=this.toElementDescriptor(e);return this.disallowProperty(e,"finisher","An element descriptor"),this.disallowProperty(e,"extras","An element descriptor"),t}),this)},toElementDescriptor:function(e){var t=String(e.kind);if("method"!==t&&"field"!==t)throw new TypeError('An element descriptor\'s .kind property must be either "method" or "field", but a decorator created an element descriptor with .kind "'+t+'"');var r=_e(e.key),i=String(e.placement);if("static"!==i&&"prototype"!==i&&"own"!==i)throw new TypeError('An element descriptor\'s .placement property must be one of "static", "prototype" or "own", but a decorator created an element descriptor with .placement "'+i+'"');var o=e.descriptor;this.disallowProperty(e,"elements","An element descriptor");var n={kind:t,key:r,placement:i,descriptor:Object.assign({},o)};return"field"!==t?this.disallowProperty(e,"initializer","A method descriptor"):(this.disallowProperty(o,"get","The property descriptor of a field descriptor"),this.disallowProperty(o,"set","The property descriptor of a field descriptor"),this.disallowProperty(o,"value","The property descriptor of a field descriptor"),n.initializer=e.initializer),n},toElementFinisherExtras:function(e){return{element:this.toElementDescriptor(e),finisher:Ce(e,"finisher"),extras:this.toElementDescriptors(e.extras)}},fromClassDescriptor:function(e){var t={kind:"class",elements:e.map(this.fromElementDescriptor,this)};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),t},toClassDescriptor:function(e){var t=String(e.kind);if("class"!==t)throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator created a class descriptor with .kind "'+t+'"');this.disallowProperty(e,"key","A class descriptor"),this.disallowProperty(e,"placement","A class descriptor"),this.disallowProperty(e,"descriptor","A class descriptor"),this.disallowProperty(e,"initializer","A class descriptor"),this.disallowProperty(e,"extras","A class descriptor");var r=Ce(e,"finisher");return{elements:this.toElementDescriptors(e.elements),finisher:r}},runClassFinishers:function(e,t){for(var r=0;r<t.length;r++){var i=(0,t[r])(e);if(void 0!==i){if("function"!=typeof i)throw new TypeError("Finishers must return a constructor.");e=i}}return e},disallowProperty:function(e,t,r){if(void 0!==e[t])throw new TypeError(r+" can't have a ."+t+" property.")}};return e}function be(e){var t,r=_e(e.key);"method"===e.kind?t={value:e.value,writable:!0,configurable:!0,enumerable:!1}:"get"===e.kind?t={get:e.value,configurable:!0,enumerable:!1}:"set"===e.kind?t={set:e.value,configurable:!0,enumerable:!1}:"field"===e.kind&&(t={configurable:!0,writable:!0,enumerable:!0});var i={kind:"field"===e.kind?"field":"method",key:r,placement:e.static?"static":"field"===e.kind?"own":"prototype",descriptor:t};return e.decorators&&(i.decorators=e.decorators),"field"===e.kind&&(i.initializer=e.value),i}function ke(e,t){void 0!==e.descriptor.get?t.descriptor.get=e.descriptor.get:t.descriptor.set=e.descriptor.set}function we(e){return e.decorators&&e.decorators.length}function Ee(e){return void 0!==e&&!(void 0===e.value&&void 0===e.writable)}function Ce(e,t){var r=e[t];if(void 0!==r&&"function"!=typeof r)throw new TypeError("Expected '"+t+"' to be a function");return r}function _e(e){var t=function(e,t){if("object"!=typeof e||null===e)return e;var r=e[Symbol.toPrimitive];if(void 0!==r){var i=r.call(e,t||"default");if("object"!=typeof i)return i;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===t?String:Number)(e)}(e,"string");return"symbol"==typeof t?t:String(t)}function Ae(e,t){(null==t||t>e.length)&&(t=e.length);for(var r=0,i=new Array(t);r<t;r++)i[r]=e[r];return i}let Pe=function(e,t,r,i){var o=ge();if(i)for(var n=0;n<i.length;n++)o=i[n](o);var s=t((function(e){o.initializeInstanceElements(e,a.elements)}),r),a=o.decorateClass(function(e){for(var t=[],r=function(e){return"method"===e.kind&&e.key===n.key&&e.placement===n.placement},i=0;i<e.length;i++){var o,n=e[i];if("method"===n.kind&&(o=t.find(r)))if(Ee(n.descriptor)||Ee(o.descriptor)){if(we(n)||we(o))throw new ReferenceError("Duplicated methods ("+n.key+") can't be decorated.");o.descriptor=n.descriptor}else{if(we(n)){if(we(o))throw new ReferenceError("Decorators can't be placed on different accessors with for the same property ("+n.key+").");o.decorators=n.decorators}ke(n,o)}else t.push(n)}return t}(s.d.map(be)),e);return o.initializeClassElements(s.F,a.elements),o.runClassFinishers(s.F,a.finishers)}(null,(function(e,t){return{F:class extends t{constructor(...t){super(...t),e(this)}},d:[{kind:"field",decorators:[(0,o.Cb)({attribute:!1})],key:"hass",value:void 0},{kind:"field",decorators:[(0,o.Cb)()],key:"method",value:()=>"POST"},{kind:"field",decorators:[(0,o.Cb)()],key:"data",value:()=>({})},{kind:"field",decorators:[(0,o.Cb)({type:Boolean,reflect:!0})],key:"disabled",value:()=>!1},{kind:"field",decorators:[(0,o.Cb)({type:Boolean})],key:"progress",value:()=>!1},{kind:"field",decorators:[(0,o.Cb)()],key:"path",value:void 0},{kind:"field",decorators:[(0,o.IO)("ha-progress-button",!0)],key:"_progressButton",value:void 0},{kind:"method",key:"render",value:function(){return i.dy`
      <ha-progress-button
        .progress=${this.progress}
        @click=${this._buttonTapped}
        ?disabled=${this.disabled}
        ><slot></slot
      ></ha-progress-button>
    `}},{kind:"method",key:"_buttonTapped",value:async function(){this.progress=!0;const e={method:this.method,path:this.path,data:this.data};try{const t=await this.hass.callApi(this.method,this.path,this.data);this.progress=!1,this._progressButton.actionSuccess(),e.success=!0,e.response=t}catch(t){this.progress=!1,this._progressButton.actionError(),e.success=!1,e.response=t}(0,s.B)(this,"hass-api-called",e)}},{kind:"get",static:!0,key:"styles",value:function(){return i.iv`
      :host([disabled]) {
        pointer-events: none;
      }
    `}}]}}),i.oi);customElements.define("ha-call-api-button",Pe);r(8324),r(5124),r(4089),r(2039);var $e=r(203);r(6586),r(3226);const xe=(e,t)=>{(0,s.B)(e,"show-dialog",{dialogTag:"dialog-hassio-markdown",dialogImport:()=>r.e(884).then(r.bind(r,6884)),dialogParams:t})};r(3432);var De=r(4450);function ze(){ze=function(){return e};var e={elementsDefinitionOrder:[["method"],["field"]],initializeInstanceElements:function(e,t){["method","field"].forEach((function(r){t.forEach((function(t){t.kind===r&&"own"===t.placement&&this.defineClassElement(e,t)}),this)}),this)},initializeClassElements:function(e,t){var r=e.prototype;["method","field"].forEach((function(i){t.forEach((function(t){var o=t.placement;if(t.kind===i&&("static"===o||"prototype"===o)){var n="static"===o?e:r;this.defineClassElement(n,t)}}),this)}),this)},defineClassElement:function(e,t){var r=t.descriptor;if("field"===t.kind){var i=t.initializer;r={enumerable:r.enumerable,writable:r.writable,configurable:r.configurable,value:void 0===i?void 0:i.call(e)}}Object.defineProperty(e,t.key,r)},decorateClass:function(e,t){var r=[],i=[],o={static:[],prototype:[],own:[]};if(e.forEach((function(e){this.addElementPlacement(e,o)}),this),e.forEach((function(e){if(!Oe(e))return r.push(e);var t=this.decorateElement(e,o);r.push(t.element),r.push.apply(r,t.extras),i.push.apply(i,t.finishers)}),this),!t)return{elements:r,finishers:i};var n=this.decorateConstructor(r,t);return i.push.apply(i,n.finishers),n.finishers=i,n},addElementPlacement:function(e,t,r){var i=t[e.placement];if(!r&&-1!==i.indexOf(e.key))throw new TypeError("Duplicated element ("+e.key+")");i.push(e.key)},decorateElement:function(e,t){for(var r=[],i=[],o=e.decorators,n=o.length-1;n>=0;n--){var s=t[e.placement];s.splice(s.indexOf(e.key),1);var a=this.fromElementDescriptor(e),d=this.toElementFinisherExtras((0,o[n])(a)||a);e=d.element,this.addElementPlacement(e,t),d.finisher&&i.push(d.finisher);var l=d.extras;if(l){for(var c=0;c<l.length;c++)this.addElementPlacement(l[c],t);r.push.apply(r,l)}}return{element:e,finishers:i,extras:r}},decorateConstructor:function(e,t){for(var r=[],i=t.length-1;i>=0;i--){var o=this.fromClassDescriptor(e),n=this.toClassDescriptor((0,t[i])(o)||o);if(void 0!==n.finisher&&r.push(n.finisher),void 0!==n.elements){e=n.elements;for(var s=0;s<e.length-1;s++)for(var a=s+1;a<e.length;a++)if(e[s].key===e[a].key&&e[s].placement===e[a].placement)throw new TypeError("Duplicated element ("+e[s].key+")")}}return{elements:e,finishers:r}},fromElementDescriptor:function(e){var t={kind:e.kind,key:e.key,placement:e.placement,descriptor:e.descriptor};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),"field"===e.kind&&(t.initializer=e.initializer),t},toElementDescriptors:function(e){var t;if(void 0!==e)return(t=e,function(e){if(Array.isArray(e))return e}(t)||function(e){if("undefined"!=typeof Symbol&&null!=e[Symbol.iterator]||null!=e["@@iterator"])return Array.from(e)}(t)||function(e,t){if(e){if("string"==typeof e)return Le(e,t);var r=Object.prototype.toString.call(e).slice(8,-1);return"Object"===r&&e.constructor&&(r=e.constructor.name),"Map"===r||"Set"===r?Array.from(e):"Arguments"===r||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(r)?Le(e,t):void 0}}(t)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()).map((function(e){var t=this.toElementDescriptor(e);return this.disallowProperty(e,"finisher","An element descriptor"),this.disallowProperty(e,"extras","An element descriptor"),t}),this)},toElementDescriptor:function(e){var t=String(e.kind);if("method"!==t&&"field"!==t)throw new TypeError('An element descriptor\'s .kind property must be either "method" or "field", but a decorator created an element descriptor with .kind "'+t+'"');var r=Ve(e.key),i=String(e.placement);if("static"!==i&&"prototype"!==i&&"own"!==i)throw new TypeError('An element descriptor\'s .placement property must be one of "static", "prototype" or "own", but a decorator created an element descriptor with .placement "'+i+'"');var o=e.descriptor;this.disallowProperty(e,"elements","An element descriptor");var n={kind:t,key:r,placement:i,descriptor:Object.assign({},o)};return"field"!==t?this.disallowProperty(e,"initializer","A method descriptor"):(this.disallowProperty(o,"get","The property descriptor of a field descriptor"),this.disallowProperty(o,"set","The property descriptor of a field descriptor"),this.disallowProperty(o,"value","The property descriptor of a field descriptor"),n.initializer=e.initializer),n},toElementFinisherExtras:function(e){return{element:this.toElementDescriptor(e),finisher:je(e,"finisher"),extras:this.toElementDescriptors(e.extras)}},fromClassDescriptor:function(e){var t={kind:"class",elements:e.map(this.fromElementDescriptor,this)};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),t},toClassDescriptor:function(e){var t=String(e.kind);if("class"!==t)throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator created a class descriptor with .kind "'+t+'"');this.disallowProperty(e,"key","A class descriptor"),this.disallowProperty(e,"placement","A class descriptor"),this.disallowProperty(e,"descriptor","A class descriptor"),this.disallowProperty(e,"initializer","A class descriptor"),this.disallowProperty(e,"extras","A class descriptor");var r=je(e,"finisher");return{elements:this.toElementDescriptors(e.elements),finisher:r}},runClassFinishers:function(e,t){for(var r=0;r<t.length;r++){var i=(0,t[r])(e);if(void 0!==i){if("function"!=typeof i)throw new TypeError("Finishers must return a constructor.");e=i}}return e},disallowProperty:function(e,t,r){if(void 0!==e[t])throw new TypeError(r+" can't have a ."+t+" property.")}};return e}function Se(e){var t,r=Ve(e.key);"method"===e.kind?t={value:e.value,writable:!0,configurable:!0,enumerable:!1}:"get"===e.kind?t={get:e.value,configurable:!0,enumerable:!1}:"set"===e.kind?t={set:e.value,configurable:!0,enumerable:!1}:"field"===e.kind&&(t={configurable:!0,writable:!0,enumerable:!0});var i={kind:"field"===e.kind?"field":"method",key:r,placement:e.static?"static":"field"===e.kind?"own":"prototype",descriptor:t};return e.decorators&&(i.decorators=e.decorators),"field"===e.kind&&(i.initializer=e.value),i}function Te(e,t){void 0!==e.descriptor.get?t.descriptor.get=e.descriptor.get:t.descriptor.set=e.descriptor.set}function Oe(e){return e.decorators&&e.decorators.length}function He(e){return void 0!==e&&!(void 0===e.value&&void 0===e.writable)}function je(e,t){var r=e[t];if(void 0!==r&&"function"!=typeof r)throw new TypeError("Expected '"+t+"' to be a function");return r}function Ve(e){var t=function(e,t){if("object"!=typeof e||null===e)return e;var r=e[Symbol.toPrimitive];if(void 0!==r){var i=r.call(e,t||"default");if("object"!=typeof i)return i;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===t?String:Number)(e)}(e,"string");return"symbol"==typeof t?t:String(t)}function Le(e,t){(null==t||t>e.length)&&(t=e.length);for(var r=0,i=new Array(t);r<t;r++)i[r]=e[r];return i}function Me(e,t,r){return Me="undefined"!=typeof Reflect&&Reflect.get?Reflect.get:function(e,t,r){var i=function(e,t){for(;!Object.prototype.hasOwnProperty.call(e,t)&&null!==(e=Ie(e)););return e}(e,t);if(i){var o=Object.getOwnPropertyDescriptor(i,t);return o.get?o.get.call(r):o.value}},Me(e,t,r||e)}function Ie(e){return Ie=Object.setPrototypeOf?Object.getPrototypeOf:function(e){return e.__proto__||Object.getPrototypeOf(e)},Ie(e)}const Fe="M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2Z",Be="M21.8,13H20V21H13V17.67L15.79,14.88L16.5,15C17.66,15 18.6,14.06 18.6,12.9C18.6,11.74 17.66,10.8 16.5,10.8A2.1,2.1 0 0,0 14.4,12.9L14.5,13.61L13,15.13V9.65C13.66,9.29 14.1,8.6 14.1,7.8A2.1,2.1 0 0,0 12,5.7A2.1,2.1 0 0,0 9.9,7.8C9.9,8.6 10.34,9.29 11,9.65V15.13L9.5,13.61L9.6,12.9A2.1,2.1 0 0,0 7.5,10.8A2.1,2.1 0 0,0 5.4,12.9A2.1,2.1 0 0,0 7.5,15L8.21,14.88L11,17.67V21H4V13H2.25C1.83,13 1.42,13 1.42,12.79C1.43,12.57 1.85,12.15 2.28,11.72L11,3C11.33,2.67 11.67,2.33 12,2.33C12.33,2.33 12.67,2.67 13,3L17,7V6H19V9L21.78,11.78C22.18,12.18 22.59,12.59 22.6,12.8C22.6,13 22.2,13 21.8,13M7.5,12A0.9,0.9 0 0,1 8.4,12.9A0.9,0.9 0 0,1 7.5,13.8A0.9,0.9 0 0,1 6.6,12.9A0.9,0.9 0 0,1 7.5,12M16.5,12C17,12 17.4,12.4 17.4,12.9C17.4,13.4 17,13.8 16.5,13.8A0.9,0.9 0 0,1 15.6,12.9A0.9,0.9 0 0,1 16.5,12M12,6.9C12.5,6.9 12.9,7.3 12.9,7.8C12.9,8.3 12.5,8.7 12,8.7C11.5,8.7 11.1,8.3 11.1,7.8C11.1,7.3 11.5,6.9 12,6.9Z",Re={stable:"M12 2C6.5 2 2 6.5 2 12S6.5 22 12 22 22 17.5 22 12 17.5 2 12 2M10 17L5 12L6.41 10.59L10 14.17L17.59 6.58L19 8L10 17Z",experimental:"M6,22A3,3 0 0,1 3,19C3,18.4 3.18,17.84 3.5,17.37L9,7.81V6A1,1 0 0,1 8,5V4A2,2 0 0,1 10,2H14A2,2 0 0,1 16,4V5A1,1 0 0,1 15,6V7.81L20.5,17.37C20.82,17.84 21,18.4 21,19A3,3 0 0,1 18,22H6M5,19A1,1 0 0,0 6,20H18A1,1 0 0,0 19,19C19,18.79 18.93,18.59 18.82,18.43L16.53,14.47L14,17L8.93,11.93L5.18,18.43C5.07,18.59 5,18.79 5,19M13,10A1,1 0 0,0 12,11A1,1 0 0,0 13,12A1,1 0 0,0 14,11A1,1 0 0,0 13,10Z",deprecated:"M10 3H14V14H10V3M10 21V17H14V21H10Z"},Ue={1:"M10,7V9H12V17H14V7H10Z",2:"M9,7V9H13V11H11A2,2 0 0,0 9,13V17H11L15,17V15H11V13H13A2,2 0 0,0 15,11V9A2,2 0 0,0 13,7H9Z",3:"M15,15V13.5A1.5,1.5 0 0,0 13.5,12A1.5,1.5 0 0,0 15,10.5V9C15,7.89 14.1,7 13,7H9V9H13V11H11V13H13V15H9V17H13A2,2 0 0,0 15,15",4:"M9,7V13H13V17H15V7H13V11H11V7H9Z",5:"M9,7V13H13V15H9V17H13A2,2 0 0,0 15,15V13A2,2 0 0,0 13,11H11V9H15V7H9Z",6:"M11,7A2,2 0 0,0 9,9V15A2,2 0 0,0 11,17H13A2,2 0 0,0 15,15V13A2,2 0 0,0 13,11H11V9H15V7H11M11,13H13V15H11V13Z",7:"M11,17L15,9V7H9V9H13L9,17",8:"M11,13H13V15H11M11,9H13V11H11M11,17H13A2,2 0 0,0 15,15V13.5A1.5,1.5 0 0,0 13.5,12A1.5,1.5 0 0,0 15,10.5V9C15,7.89 14.1,7 13,7H11A2,2 0 0,0 9,9V10.5A1.5,1.5 0 0,0 10.5,12A1.5,1.5 0 0,0 9,13.5V15C9,16.11 9.9,17 11,17"};!function(e,t,r,i){var o=ze();if(i)for(var n=0;n<i.length;n++)o=i[n](o);var s=t((function(e){o.initializeInstanceElements(e,a.elements)}),r),a=o.decorateClass(function(e){for(var t=[],r=function(e){return"method"===e.kind&&e.key===n.key&&e.placement===n.placement},i=0;i<e.length;i++){var o,n=e[i];if("method"===n.kind&&(o=t.find(r)))if(He(n.descriptor)||He(o.descriptor)){if(Oe(n)||Oe(o))throw new ReferenceError("Duplicated methods ("+n.key+") can't be decorated.");o.descriptor=n.descriptor}else{if(Oe(n)){if(Oe(o))throw new ReferenceError("Decorators can't be placed on different accessors with for the same property ("+n.key+").");o.decorators=n.decorators}Te(n,o)}else t.push(n)}return t}(s.d.map(Se)),e);o.initializeClassElements(s.F,a.elements),o.runClassFinishers(s.F,a.finishers)}([(0,o.Mo)("hassio-addon-info")],(function(e,t){class r extends t{constructor(...t){super(...t),e(this)}}return{F:r,d:[{kind:"field",decorators:[(0,o.Cb)({type:Boolean})],key:"narrow",value:void 0},{kind:"field",decorators:[(0,o.Cb)({attribute:!1})],key:"route",value:void 0},{kind:"field",decorators:[(0,o.Cb)({attribute:!1})],key:"hass",value:void 0},{kind:"field",decorators:[(0,o.Cb)({attribute:!1})],key:"addon",value:void 0},{kind:"field",decorators:[(0,o.Cb)({attribute:!1})],key:"supervisor",value:void 0},{kind:"field",decorators:[(0,o.SB)()],key:"_metrics",value:void 0},{kind:"field",decorators:[(0,o.SB)()],key:"_error",value:void 0},{kind:"field",key:"_addonStoreInfo",value:()=>(0,n.Z)(((e,t)=>t.find((t=>t.slug===e))))},{kind:"method",key:"render",value:function(){var e,t,r,o,n;const s=this.addon.detached||this.addon.available?void 0:this._addonStoreInfo(this.addon.slug,this.supervisor.store.addons),a=[{description:this.supervisor.localize("addon.dashboard.cpu_usage"),value:null===(e=this._metrics)||void 0===e?void 0:e.cpu_percent},{description:this.supervisor.localize("addon.dashboard.ram_usage"),value:null===(t=this._metrics)||void 0===t?void 0:t.memory_percent,tooltip:`${(0,$e.d)(null===(r=this._metrics)||void 0===r?void 0:r.memory_usage)}/${(0,$e.d)(null===(o=this._metrics)||void 0===o?void 0:o.memory_limit)}`}];return i.dy`
      ${this.addon.update_available?i.dy`
            <update-available-card
              .hass=${this.hass}
              .narrow=${this.narrow}
              .supervisor=${this.supervisor}
              .addonSlug=${this.addon.slug}
              @update-complete=${this._updateComplete}
            ></update-available-card>
          `:""}
      ${this.addon.protected?"":i.dy`
            <ha-alert
              alert-type="error"
              .title=${this.supervisor.localize("addon.dashboard.protection_mode.title")}
            >
              ${this.supervisor.localize("addon.dashboard.protection_mode.content")}
              <mwc-button
                slot="action"
                .label=${this.supervisor.localize("addon.dashboard.protection_mode.enable")}
                @click=${this._protectionToggled}
              >
              </mwc-button>
            </ha-alert>
          `}

      <ha-card>
        <div class="card-content">
          <div class="addon-header">
            ${this.narrow?"":this.addon.name}
            <div class="addon-version light-color">
              ${this.addon.version?i.dy`
                    ${this._computeIsRunning?i.dy`
                          <ha-svg-icon
                            .title=${this.supervisor.localize("dashboard.addon_running")}
                            class="running"
                            .path=${Fe}
                          ></ha-svg-icon>
                        `:i.dy`
                          <ha-svg-icon
                            .title=${this.supervisor.localize("dashboard.addon_stopped")}
                            class="stopped"
                            .path=${Fe}
                          ></ha-svg-icon>
                        `}
                  `:i.dy` ${this.addon.version_latest} `}
            </div>
          </div>
          <div class="description light-color">
            ${this.addon.version?i.dy`
                  Current version: ${this.addon.version}
                  <div class="changelog" @click=${this._openChangelog}>
                    (<span class="changelog-link"
                      >${this.supervisor.localize("addon.dashboard.changelog")}</span
                    >)
                  </div>
                `:i.dy`<span class="changelog-link" @click=${this._openChangelog}
                  >${this.supervisor.localize("addon.dashboard.changelog")}</span
                >`}
          </div>

          <ha-chip-set class="capabilities">
            ${"stable"!==this.addon.stage?i.dy` <ha-chip
                  hasIcon
                  class=${(0,ve.$)({yellow:"experimental"===this.addon.stage,red:"deprecated"===this.addon.stage})}
                  @click=${this._showMoreInfo}
                  id="stage"
                >
                  <ha-svg-icon
                    slot="icon"
                    .path=${Re[this.addon.stage]}
                  >
                  </ha-svg-icon>
                  ${this.supervisor.localize(`addon.dashboard.capability.stages.${this.addon.stage}`)}
                </ha-chip>`:""}

            <ha-chip
              hasIcon
              class=${(0,ve.$)({green:Number(this.addon.rating)>=6,yellow:[3,4,5].includes(Number(this.addon.rating)),red:Number(this.addon.rating)>=2})}
              @click=${this._showMoreInfo}
              id="rating"
            >
              <ha-svg-icon slot="icon" .path=${Ue[this.addon.rating]}>
              </ha-svg-icon>

              ${this.supervisor.localize("addon.dashboard.capability.label.rating")}
            </ha-chip>
            ${this.addon.host_network?i.dy`
                  <ha-chip
                    hasIcon
                    @click=${this._showMoreInfo}
                    id="host_network"
                  >
                    <ha-svg-icon slot="icon" .path=${"M17,3A2,2 0 0,1 19,5V15A2,2 0 0,1 17,17H13V19H14A1,1 0 0,1 15,20H22V22H15A1,1 0 0,1 14,23H10A1,1 0 0,1 9,22H2V20H9A1,1 0 0,1 10,19H11V17H7C5.89,17 5,16.1 5,15V5A2,2 0 0,1 7,3H17Z"}> </ha-svg-icon>
                    ${this.supervisor.localize("addon.dashboard.capability.label.host")}
                  </ha-chip>
                `:""}
            ${this.addon.full_access?i.dy`
                  <ha-chip
                    hasIcon
                    @click=${this._showMoreInfo}
                    id="full_access"
                  >
                    <ha-svg-icon slot="icon" .path=${"M6,4H18V5H21V7H18V9H21V11H18V13H21V15H18V17H21V19H18V20H6V19H3V17H6V15H3V13H6V11H3V9H6V7H3V5H6V4M11,15V18H12V15H11M13,15V18H14V15H13M15,15V18H16V15H15Z"}></ha-svg-icon>
                    ${this.supervisor.localize("addon.dashboard.capability.label.hardware")}
                  </ha-chip>
                `:""}
            ${this.addon.homeassistant_api?i.dy`
                  <ha-chip
                    hasIcon
                    @click=${this._showMoreInfo}
                    id="homeassistant_api"
                  >
                    <ha-svg-icon
                      slot="icon"
                      .path=${Be}
                    ></ha-svg-icon>
                    ${this.supervisor.localize("addon.dashboard.capability.label.core")}
                  </ha-chip>
                `:""}
            ${this._computeHassioApi?i.dy`
                  <ha-chip hasIcon @click=${this._showMoreInfo} id="hassio_api">
                    <ha-svg-icon
                      slot="icon"
                      .path=${Be}
                    ></ha-svg-icon>
                    ${this.supervisor.localize(`addon.dashboard.capability.role.${this.addon.hassio_role}`)||this.addon.hassio_role}
                  </ha-chip>
                `:""}
            ${this.addon.docker_api?i.dy`
                  <ha-chip hasIcon @click=${this._showMoreInfo} id="docker_api">
                    <ha-svg-icon slot="icon" .path=${"M21.81 10.25C21.75 10.21 21.25 9.82 20.17 9.82C19.89 9.82 19.61 9.85 19.33 9.9C19.12 8.5 17.95 7.79 17.9 7.76L17.61 7.59L17.43 7.86C17.19 8.22 17 8.63 16.92 9.05C16.72 9.85 16.84 10.61 17.25 11.26C16.76 11.54 15.96 11.61 15.79 11.61H2.62C2.28 11.61 2 11.89 2 12.24C2 13.39 2.18 14.54 2.58 15.62C3.03 16.81 3.71 17.69 4.58 18.23C5.56 18.83 7.17 19.17 9 19.17C9.79 19.17 10.61 19.1 11.42 18.95C12.54 18.75 13.62 18.36 14.61 17.79C15.43 17.32 16.16 16.72 16.78 16C17.83 14.83 18.45 13.5 18.9 12.35H19.09C20.23 12.35 20.94 11.89 21.33 11.5C21.59 11.26 21.78 10.97 21.92 10.63L22 10.39L21.81 10.25M3.85 11.24H5.61C5.69 11.24 5.77 11.17 5.77 11.08V9.5C5.77 9.42 5.7 9.34 5.61 9.34H3.85C3.76 9.34 3.69 9.41 3.69 9.5V11.08C3.7 11.17 3.76 11.24 3.85 11.24M6.28 11.24H8.04C8.12 11.24 8.2 11.17 8.2 11.08V9.5C8.2 9.42 8.13 9.34 8.04 9.34H6.28C6.19 9.34 6.12 9.41 6.12 9.5V11.08C6.13 11.17 6.19 11.24 6.28 11.24M8.75 11.24H10.5C10.6 11.24 10.67 11.17 10.67 11.08V9.5C10.67 9.42 10.61 9.34 10.5 9.34H8.75C8.67 9.34 8.6 9.41 8.6 9.5V11.08C8.6 11.17 8.66 11.24 8.75 11.24M11.19 11.24H12.96C13.04 11.24 13.11 11.17 13.11 11.08V9.5C13.11 9.42 13.05 9.34 12.96 9.34H11.19C11.11 9.34 11.04 9.41 11.04 9.5V11.08C11.04 11.17 11.11 11.24 11.19 11.24M6.28 9H8.04C8.12 9 8.2 8.91 8.2 8.82V7.25C8.2 7.16 8.13 7.09 8.04 7.09H6.28C6.19 7.09 6.12 7.15 6.12 7.25V8.82C6.13 8.91 6.19 9 6.28 9M8.75 9H10.5C10.6 9 10.67 8.91 10.67 8.82V7.25C10.67 7.16 10.61 7.09 10.5 7.09H8.75C8.67 7.09 8.6 7.15 8.6 7.25V8.82C8.6 8.91 8.66 9 8.75 9M11.19 9H12.96C13.04 9 13.11 8.91 13.11 8.82V7.25C13.11 7.16 13.04 7.09 12.96 7.09H11.19C11.11 7.09 11.04 7.15 11.04 7.25V8.82C11.04 8.91 11.11 9 11.19 9M11.19 6.72H12.96C13.04 6.72 13.11 6.65 13.11 6.56V5C13.11 4.9 13.04 4.83 12.96 4.83H11.19C11.11 4.83 11.04 4.89 11.04 5V6.56C11.04 6.64 11.11 6.72 11.19 6.72M13.65 11.24H15.41C15.5 11.24 15.57 11.17 15.57 11.08V9.5C15.57 9.42 15.5 9.34 15.41 9.34H13.65C13.57 9.34 13.5 9.41 13.5 9.5V11.08C13.5 11.17 13.57 11.24 13.65 11.24"}></ha-svg-icon>
                    ${this.supervisor.localize("addon.dashboard.capability.label.docker")}
                  </ha-chip>
                `:""}
            ${this.addon.host_pid?i.dy`
                  <ha-chip hasIcon @click=${this._showMoreInfo} id="host_pid">
                    <ha-svg-icon slot="icon" .path=${"M5.41,21L6.12,17H2.12L2.47,15H6.47L7.53,9H3.53L3.88,7H7.88L8.59,3H10.59L9.88,7H15.88L16.59,3H18.59L17.88,7H21.88L21.53,9H17.53L16.47,15H20.47L20.12,17H16.12L15.41,21H13.41L14.12,17H8.12L7.41,21H5.41M9.53,9L8.47,15H14.47L15.53,9H9.53Z"}></ha-svg-icon>
                    ${this.supervisor.localize("addon.dashboard.capability.label.host_pid")}
                  </ha-chip>
                `:""}
            ${"default"!==this.addon.apparmor?i.dy`
                  <ha-chip
                    hasIcon
                    @click=${this._showMoreInfo}
                    class=${this._computeApparmorClassName}
                    id="apparmor"
                  >
                    <ha-svg-icon slot="icon" .path=${"M12,1L3,5V11C3,16.55 6.84,21.74 12,23C17.16,21.74 21,16.55 21,11V5L12,1Z"}></ha-svg-icon>
                    ${this.supervisor.localize("addon.dashboard.capability.label.apparmor")}
                  </ha-chip>
                `:""}
            ${this.addon.auth_api?i.dy`
                  <ha-chip hasIcon @click=${this._showMoreInfo} id="auth_api">
                    <ha-svg-icon slot="icon" .path=${"M7 14C5.9 14 5 13.1 5 12S5.9 10 7 10 9 10.9 9 12 8.1 14 7 14M12.6 10C11.8 7.7 9.6 6 7 6C3.7 6 1 8.7 1 12S3.7 18 7 18C9.6 18 11.8 16.3 12.6 14H16V18H20V14H23V10H12.6Z"}></ha-svg-icon>
                    ${this.supervisor.localize("addon.dashboard.capability.label.auth")}
                  </ha-chip>
                `:""}
            ${this.addon.ingress?i.dy`
                  <ha-chip hasIcon @click=${this._showMoreInfo} id="ingress">
                    <ha-svg-icon
                      slot="icon"
                      .path=${"M11.5,11L17.88,16.37L17,16.55L16.36,16.67C15.73,16.8 15.37,17.5 15.65,18.07L15.92,18.65L17.28,21.59L15.86,22.25L14.5,19.32L14.24,18.74C13.97,18.15 13.22,17.97 12.72,18.38L12.21,18.78L11.5,19.35V11M10.76,8.69A0.76,0.76 0 0,0 10,9.45V20.9C10,21.32 10.34,21.66 10.76,21.66C10.95,21.66 11.11,21.6 11.24,21.5L13.15,19.95L14.81,23.57C14.94,23.84 15.21,24 15.5,24C15.61,24 15.72,24 15.83,23.92L18.59,22.64C18.97,22.46 19.15,22 18.95,21.63L17.28,18L19.69,17.55C19.85,17.5 20,17.43 20.12,17.29C20.39,16.97 20.35,16.5 20,16.21L11.26,8.86L11.25,8.87C11.12,8.76 10.95,8.69 10.76,8.69M15,10V8H20V10H15M13.83,4.76L16.66,1.93L18.07,3.34L15.24,6.17L13.83,4.76M10,0H12V5H10V0M3.93,14.66L6.76,11.83L8.17,13.24L5.34,16.07L3.93,14.66M3.93,3.34L5.34,1.93L8.17,4.76L6.76,6.17L3.93,3.34M7,10H2V8H7V10"}
                    ></ha-svg-icon>
                    ${this.supervisor.localize("addon.dashboard.capability.label.ingress")}
                  </ha-chip>
                `:""}
            ${this.addon.signed?i.dy`
                  <ha-chip hasIcon @click=${this._showMoreInfo} id="signed">
                    <ha-svg-icon slot="icon" .path=${"M23 16V15.5A2.5 2.5 0 0 0 18 15.5V16A1 1 0 0 0 17 17V21A1 1 0 0 0 18 22H23A1 1 0 0 0 24 21V17A1 1 0 0 0 23 16M22 16H19V15.5A1.5 1.5 0 0 1 22 15.5M7 8.9H11V7H7A5 5 0 0 0 7 17H11V15.1H7A3.1 3.1 0 0 1 7 8.9M8 11V13H16V11M13 15.1V17H15V15.1M17 7H13V8.9H17A3.09 3.09 0 0 1 19.94 11A5.12 5.12 0 0 1 20.5 11H21.9A5 5 0 0 0 17 7Z"}></ha-svg-icon>
                    ${this.supervisor.localize("addon.dashboard.capability.label.signed")}
                  </ha-chip>
                `:""}
          </ha-chip-set>

          <div class="description light-color">
            ${this.addon.description}.<br />
            ${this.supervisor.localize("addon.dashboard.visit_addon_page","name",i.dy`<a href=${this.addon.url} target="_blank" rel="noreferrer"
                >${this.addon.name}</a
              >`)}
          </div>
          <div class="addon-container">
            <div>
              ${this.addon.logo?i.dy`
                    <img
                      class="logo"
                      src="/api/hassio/addons/${this.addon.slug}/logo"
                    />
                  `:""}
              ${this.addon.version?i.dy`
                    <div
                      class=${(0,ve.$)({"addon-options":!0,started:"started"===this.addon.state})}
                    >
                      <ha-settings-row ?three-line=${this.narrow}>
                        <span slot="heading">
                          ${this.supervisor.localize("addon.dashboard.option.boot.title")}
                        </span>
                        <span slot="description">
                          ${this.supervisor.localize("addon.dashboard.option.boot.description")}
                        </span>
                        <ha-switch
                          @change=${this._startOnBootToggled}
                          .checked=${"auto"===this.addon.boot}
                          haptic
                        ></ha-switch>
                      </ha-settings-row>

                      ${"once"!==this.addon.startup?i.dy`
                            <ha-settings-row ?three-line=${this.narrow}>
                              <span slot="heading">
                                ${this.supervisor.localize("addon.dashboard.option.watchdog.title")}
                              </span>
                              <span slot="description">
                                ${this.supervisor.localize("addon.dashboard.option.watchdog.description")}
                              </span>
                              <ha-switch
                                @change=${this._watchdogToggled}
                                .checked=${this.addon.watchdog}
                                haptic
                              ></ha-switch>
                            </ha-settings-row>
                          `:""}
                      ${this.addon.auto_update||null!==(n=this.hass.userData)&&void 0!==n&&n.showAdvanced?i.dy`
                            <ha-settings-row ?three-line=${this.narrow}>
                              <span slot="heading">
                                ${this.supervisor.localize("addon.dashboard.option.auto_update.title")}
                              </span>
                              <span slot="description">
                                ${this.supervisor.localize("addon.dashboard.option.auto_update.description")}
                              </span>
                              <ha-switch
                                @change=${this._autoUpdateToggled}
                                .checked=${this.addon.auto_update}
                                haptic
                              ></ha-switch>
                            </ha-settings-row>
                          `:""}
                      ${!this._computeCannotIngressSidebar&&this.addon.ingress?i.dy`
                            <ha-settings-row ?three-line=${this.narrow}>
                              <span slot="heading">
                                ${this.supervisor.localize("addon.dashboard.option.ingress_panel.title")}
                              </span>
                              <span slot="description">
                                ${this.supervisor.localize("addon.dashboard.option.ingress_panel.description")}
                              </span>
                              <ha-switch
                                @change=${this._panelToggled}
                                .checked=${this.addon.ingress_panel}
                                haptic
                              ></ha-switch>
                            </ha-settings-row>
                          `:""}
                      ${this._computeUsesProtectedOptions?i.dy`
                            <ha-settings-row ?three-line=${this.narrow}>
                              <span slot="heading">
                                ${this.supervisor.localize("addon.dashboard.option.protected.title")}
                              </span>
                              <span slot="description">
                                ${this.supervisor.localize("addon.dashboard.option.protected.description")}
                              </span>
                              <ha-switch
                                @change=${this._protectionToggled}
                                .checked=${this.addon.protected}
                                haptic
                              ></ha-switch>
                            </ha-settings-row>
                          `:""}
                    </div>
                  `:""}
            </div>
            <div>
              ${"started"===this.addon.state?i.dy`<ha-settings-row ?three-line=${this.narrow}>
                      <span slot="heading">
                        ${this.supervisor.localize("addon.dashboard.hostname")}
                      </span>
                      <code slot="description"> ${this.addon.hostname} </code>
                    </ha-settings-row>
                    ${a.map((e=>{var t;return i.dy`
                          <supervisor-metric
                            .description=${e.description}
                            .value=${null!==(t=e.value)&&void 0!==t?t:0}
                            .tooltip=${e.tooltip}
                          ></supervisor-metric>
                        `}))}`:""}
            </div>
          </div>
          ${this._error?i.dy`<ha-alert alert-type="error">${this._error}</ha-alert>`:""}
          ${this.addon.version||!s||this.addon.available?"":(0,De.I)(this.supervisor.info.supported_arch,this.addon.arch)?i.dy`
                  <ha-alert alert-type="warning">
                    ${this.supervisor.localize("addon.dashboard.not_available_version","core_version_installed",this.supervisor.core.version,"core_version_needed",s.homeassistant)}
                  </ha-alert>
                `:i.dy`
                  <ha-alert alert-type="warning">
                    ${this.supervisor.localize("addon.dashboard.not_available_arch")}
                  </ha-alert>
                `}
        </div>
        <div class="card-actions">
          <div>
            ${this.addon.version?this._computeIsRunning?i.dy`
                    <ha-progress-button
                      class="warning"
                      @click=${this._stopClicked}
                    >
                      ${this.supervisor.localize("addon.dashboard.stop")}
                    </ha-progress-button>
                    <ha-progress-button
                      class="warning"
                      @click=${this._restartClicked}
                    >
                      ${this.supervisor.localize("addon.dashboard.restart")}
                    </ha-progress-button>
                  `:i.dy`
                    <ha-progress-button @click=${this._startClicked}>
                      ${this.supervisor.localize("addon.dashboard.start")}
                    </ha-progress-button>
                  `:i.dy`
                  <ha-progress-button
                    .disabled=${!this.addon.available}
                    @click=${this._installClicked}
                  >
                    ${this.supervisor.localize("addon.dashboard.install")}
                  </ha-progress-button>
                `}
          </div>
          <div>
            ${this.addon.version?i.dy` ${this._computeShowWebUI?i.dy`
                        <a
                          href=${this._pathWebui}
                          tabindex="-1"
                          target="_blank"
                          rel="noopener"
                        >
                          <mwc-button>
                            ${this.supervisor.localize("addon.dashboard.open_web_ui")}
                          </mwc-button>
                        </a>
                      `:""}
                  ${this._computeShowIngressUI?i.dy`
                        <mwc-button @click=${this._openIngress}>
                          ${this.supervisor.localize("addon.dashboard.open_web_ui")}
                        </mwc-button>
                      `:""}
                  <ha-progress-button
                    class="warning"
                    @click=${this._uninstallClicked}
                  >
                    ${this.supervisor.localize("addon.dashboard.uninstall")}
                  </ha-progress-button>
                  ${this.addon.build?i.dy`
                        <ha-call-api-button
                          class="warning"
                          .hass=${this.hass}
                          .path="hassio/addons/${this.addon.slug}/rebuild"
                        >
                          ${this.supervisor.localize("addon.dashboard.rebuild")}
                        </ha-call-api-button>
                      `:""}`:""}
          </div>
        </div>
      </ha-card>

      ${this.addon.long_description?i.dy`
            <ha-card>
              <div class="card-content">
                <ha-markdown
                  .content=${this.addon.long_description}
                ></ha-markdown>
              </div>
            </ha-card>
          `:""}
    `}},{kind:"method",key:"updated",value:function(e){Me(Ie(r.prototype),"updated",this).call(this,e),e.has("addon")&&this._loadData()}},{kind:"method",key:"_loadData",value:async function(){"started"===this.addon.state&&(this._metrics=await(0,c.yd)(this.hass,`addons/${this.addon.slug}`))}},{kind:"get",key:"_computeHassioApi",value:function(){return this.addon.hassio_api&&("manager"===this.addon.hassio_role||"admin"===this.addon.hassio_role)}},{kind:"get",key:"_computeApparmorClassName",value:function(){return"profile"===this.addon.apparmor?"green":"disable"===this.addon.apparmor?"red":""}},{kind:"method",key:"_showMoreInfo",value:function(e){const t=e.currentTarget.id;xe(this,{title:this.supervisor.localize(`addon.dashboard.capability.${t}.title`),content:"stage"===t?this.supervisor.localize(`addon.dashboard.capability.${t}.description`,"icon_stable",`<ha-svg-icon path="${Re.stable}"></ha-svg-icon>`,"icon_experimental",`<ha-svg-icon path="${Re.experimental}"></ha-svg-icon>`,"icon_deprecated",`<ha-svg-icon path="${Re.deprecated}"></ha-svg-icon>`):this.supervisor.localize(`addon.dashboard.capability.${t}.description`)})}},{kind:"get",key:"_computeIsRunning",value:function(){var e;return"started"===(null===(e=this.addon)||void 0===e?void 0:e.state)}},{kind:"get",key:"_pathWebui",value:function(){return this.addon.webui&&this.addon.webui.replace("[HOST]",document.location.hostname)}},{kind:"get",key:"_computeShowWebUI",value:function(){return!this.addon.ingress&&this.addon.webui&&this._computeIsRunning}},{kind:"method",key:"_openIngress",value:function(){(0,a.c)(`/hassio/ingress/${this.addon.slug}`)}},{kind:"get",key:"_computeShowIngressUI",value:function(){return this.addon.ingress&&this._computeIsRunning}},{kind:"get",key:"_computeCannotIngressSidebar",value:function(){return!this.addon.ingress||!(0,ye.I)(this.hass.config.version,0,92)}},{kind:"get",key:"_computeUsesProtectedOptions",value:function(){return this.addon.docker_api||this.addon.full_access||this.addon.host_pid}},{kind:"method",key:"_startOnBootToggled",value:async function(){this._error=void 0;const e={boot:"auto"===this.addon.boot?"manual":"auto"};try{await(0,l.d3)(this.hass,this.addon.slug,e);const t={success:!0,response:void 0,path:"option"};(0,s.B)(this,"hass-api-called",t)}catch(e){this._error=this.supervisor.localize("addon.failed_to_save","error",(0,c.js)(e))}}},{kind:"method",key:"_watchdogToggled",value:async function(){this._error=void 0;const e={watchdog:!this.addon.watchdog};try{await(0,l.d3)(this.hass,this.addon.slug,e);const t={success:!0,response:void 0,path:"option"};(0,s.B)(this,"hass-api-called",t)}catch(e){this._error=this.supervisor.localize("addon.failed_to_save","error",(0,c.js)(e))}}},{kind:"method",key:"_autoUpdateToggled",value:async function(){this._error=void 0;const e={auto_update:!this.addon.auto_update};try{await(0,l.d3)(this.hass,this.addon.slug,e);const t={success:!0,response:void 0,path:"option"};(0,s.B)(this,"hass-api-called",t)}catch(e){this._error=this.supervisor.localize("addon.failed_to_save","error",(0,c.js)(e))}}},{kind:"method",key:"_protectionToggled",value:async function(){this._error=void 0;const e={protected:!this.addon.protected};try{await(0,l.NI)(this.hass,this.addon.slug,e);const t={success:!0,response:void 0,path:"security"};(0,s.B)(this,"hass-api-called",t)}catch(e){this._error=this.supervisor.localize("addon.failed_to_save","error",(0,c.js)(e))}}},{kind:"method",key:"_panelToggled",value:async function(){this._error=void 0;const e={ingress_panel:!this.addon.ingress_panel};try{await(0,l.d3)(this.hass,this.addon.slug,e);const t={success:!0,response:void 0,path:"option"};(0,s.B)(this,"hass-api-called",t)}catch(e){this._error=this.supervisor.localize("addon.failed_to_save","error",(0,c.js)(e))}}},{kind:"method",key:"_openChangelog",value:async function(){try{const e=await(0,l.CH)(this.hass,this.addon.slug);xe(this,{title:this.supervisor.localize("addon.dashboard.changelog"),content:(0,De.H)(this.addon,e)})}catch(e){(0,m.Ys)(this,{title:this.supervisor.localize("addon.dashboard.action_error.get_changelog"),text:(0,c.js)(e)})}}},{kind:"method",key:"_updateComplete",value:function(){const e={success:!0,response:void 0,path:"install"};(0,s.B)(this,"hass-api-called",e)}},{kind:"method",key:"_installClicked",value:async function(e){const t=e.currentTarget;t.progress=!0;try{await(0,l.fU)(this.hass,this.addon.slug);const e={success:!0,response:void 0,path:"install"};(0,s.B)(this,"hass-api-called",e)}catch(e){(0,m.Ys)(this,{title:this.supervisor.localize("addon.dashboard.action_error.install"),text:(0,c.js)(e)})}t.progress=!1}},{kind:"method",key:"_stopClicked",value:async function(e){const t=e.currentTarget;t.progress=!0;try{await(0,l.ow)(this.hass,this.addon.slug);const e={success:!0,response:void 0,path:"stop"};(0,s.B)(this,"hass-api-called",e)}catch(e){(0,m.Ys)(this,{title:this.supervisor.localize("addon.dashboard.action_error.stop"),text:(0,c.js)(e)})}t.progress=!1}},{kind:"method",key:"_restartClicked",value:async function(e){const t=e.currentTarget;t.progress=!0;try{await(0,l.P$)(this.hass,this.addon.slug);const e={success:!0,response:void 0,path:"stop"};(0,s.B)(this,"hass-api-called",e)}catch(e){(0,m.Ys)(this,{title:this.supervisor.localize("addon.dashboard.action_error.restart"),text:(0,c.js)(e)})}t.progress=!1}},{kind:"method",key:"_startClicked",value:async function(e){const t=e.currentTarget;t.progress=!0;try{const e=await(0,l.su)(this.hass,this.addon.slug);if(!e.valid)return await(0,m.g7)(this,{title:this.supervisor.localize("addon.dashboard.action_error.start_invalid_config"),text:e.message.split(" Got ")[0],confirm:()=>this._openConfiguration(),confirmText:this.supervisor.localize("addon.dashboard.action_error.go_to_config"),dismissText:this.supervisor.localize("common.cancel")}),void(t.progress=!1)}catch(e){return(0,m.Ys)(this,{title:"Failed to validate addon configuration",text:(0,c.js)(e)}),void(t.progress=!1)}try{await(0,l.kP)(this.hass,this.addon.slug),this.addon=await(0,l.AD)(this.hass,this.addon.slug);const e={success:!0,response:void 0,path:"start"};(0,s.B)(this,"hass-api-called",e)}catch(e){(0,m.Ys)(this,{title:this.supervisor.localize("addon.dashboard.action_error.start"),text:(0,c.js)(e)})}t.progress=!1}},{kind:"method",key:"_openConfiguration",value:function(){(0,a.c)(`/hassio/addon/${this.addon.slug}/config`)}},{kind:"method",key:"_uninstallClicked",value:async function(e){const t=e.currentTarget;t.progress=!0;if(await(0,m.g7)(this,{title:this.addon.name,text:"Are you sure you want to uninstall this add-on?",confirmText:"uninstall add-on",dismissText:"no"})){this._error=void 0;try{await(0,l.Yn)(this.hass,this.addon.slug);const e={success:!0,response:void 0,path:"uninstall"};(0,s.B)(this,"hass-api-called",e)}catch(e){(0,m.Ys)(this,{title:this.supervisor.localize("addon.dashboard.action_error.uninstall"),text:(0,c.js)(e)})}t.progress=!1}else t.progress=!1}},{kind:"get",static:!0,key:"styles",value:function(){return[h.Qx,p.l,i.iv`
        :host {
          display: block;
        }
        ha-card {
          display: block;
          margin-bottom: 16px;
        }
        ha-card.warning {
          background-color: var(--error-color);
          color: white;
        }
        ha-card.warning .card-header {
          color: white;
        }
        ha-card.warning .card-content {
          color: white;
        }
        ha-card.warning mwc-button {
          --mdc-theme-primary: white !important;
        }
        .warning {
          color: var(--error-color);
          --mdc-theme-primary: var(--error-color);
        }
        .light-color {
          color: var(--secondary-text-color);
        }
        .addon-header {
          padding-left: 8px;
          font-size: 24px;
          color: var(--ha-card-header-color, --primary-text-color);
        }
        .addon-version {
          float: right;
          font-size: 15px;
          vertical-align: middle;
        }
        .errors {
          color: var(--error-color);
          margin-bottom: 16px;
        }
        .description {
          margin-bottom: 16px;
        }
        img.logo {
          max-width: 100%;
          max-height: 60px;
          margin: 16px 0;
          display: block;
        }

        ha-switch {
          display: flex;
        }
        ha-svg-icon.running {
          color: var(--success-color);
        }
        ha-svg-icon.stopped {
          color: var(--error-color);
        }
        ha-call-api-button {
          font-weight: 500;
          color: var(--primary-color);
        }
        protection-enable mwc-button {
          --mdc-theme-primary: white;
        }
        .description a {
          color: var(--primary-color);
        }
        ha-chip {
          text-transform: capitalize;
          --ha-chip-text-color: var(--text-primary-color);
          --ha-chip-background-color: var(--primary-color);
        }

        .red {
          --ha-chip-background-color: var(--label-badge-red, #df4c1e);
        }
        .blue {
          --ha-chip-background-color: var(--label-badge-blue, #039be5);
        }
        .green {
          --ha-chip-background-color: var(--label-badge-green, #0da035);
        }
        .yellow {
          --ha-chip-background-color: var(--label-badge-yellow, #f4b400);
        }
        .capabilities {
          margin-bottom: 16px;
        }
        .card-actions {
          justify-content: space-between;
          display: flex;
        }
        .changelog {
          display: contents;
        }
        .changelog-link {
          color: var(--primary-color);
          text-decoration: underline;
          cursor: pointer;
        }
        ha-markdown {
          padding: 16px;
        }
        ha-settings-row {
          padding: 0;
          height: 54px;
          width: 100%;
        }
        ha-settings-row > span[slot="description"] {
          white-space: normal;
          color: var(--secondary-text-color);
        }
        ha-settings-row[three-line] {
          height: 74px;
        }

        .addon-options {
          max-width: 90%;
        }

        .addon-container {
          display: grid;
          grid-auto-flow: column;
          grid-template-columns: 60% 40%;
        }

        .addon-container > div:last-of-type {
          align-self: end;
        }

        ha-alert mwc-button {
          --mdc-theme-primary: var(--primary-text-color);
        }
        a {
          text-decoration: none;
        }

        update-available-card {
          padding-bottom: 16px;
        }

        @media (max-width: 720px) {
          ha-chip {
            line-height: 36px;
          }
          .addon-options {
            max-width: 100%;
          }
          .addon-container {
            display: block;
          }
        }
      `]}}]}}),i.oi);function Ze(){Ze=function(){return e};var e={elementsDefinitionOrder:[["method"],["field"]],initializeInstanceElements:function(e,t){["method","field"].forEach((function(r){t.forEach((function(t){t.kind===r&&"own"===t.placement&&this.defineClassElement(e,t)}),this)}),this)},initializeClassElements:function(e,t){var r=e.prototype;["method","field"].forEach((function(i){t.forEach((function(t){var o=t.placement;if(t.kind===i&&("static"===o||"prototype"===o)){var n="static"===o?e:r;this.defineClassElement(n,t)}}),this)}),this)},defineClassElement:function(e,t){var r=t.descriptor;if("field"===t.kind){var i=t.initializer;r={enumerable:r.enumerable,writable:r.writable,configurable:r.configurable,value:void 0===i?void 0:i.call(e)}}Object.defineProperty(e,t.key,r)},decorateClass:function(e,t){var r=[],i=[],o={static:[],prototype:[],own:[]};if(e.forEach((function(e){this.addElementPlacement(e,o)}),this),e.forEach((function(e){if(!Qe(e))return r.push(e);var t=this.decorateElement(e,o);r.push(t.element),r.push.apply(r,t.extras),i.push.apply(i,t.finishers)}),this),!t)return{elements:r,finishers:i};var n=this.decorateConstructor(r,t);return i.push.apply(i,n.finishers),n.finishers=i,n},addElementPlacement:function(e,t,r){var i=t[e.placement];if(!r&&-1!==i.indexOf(e.key))throw new TypeError("Duplicated element ("+e.key+")");i.push(e.key)},decorateElement:function(e,t){for(var r=[],i=[],o=e.decorators,n=o.length-1;n>=0;n--){var s=t[e.placement];s.splice(s.indexOf(e.key),1);var a=this.fromElementDescriptor(e),d=this.toElementFinisherExtras((0,o[n])(a)||a);e=d.element,this.addElementPlacement(e,t),d.finisher&&i.push(d.finisher);var l=d.extras;if(l){for(var c=0;c<l.length;c++)this.addElementPlacement(l[c],t);r.push.apply(r,l)}}return{element:e,finishers:i,extras:r}},decorateConstructor:function(e,t){for(var r=[],i=t.length-1;i>=0;i--){var o=this.fromClassDescriptor(e),n=this.toClassDescriptor((0,t[i])(o)||o);if(void 0!==n.finisher&&r.push(n.finisher),void 0!==n.elements){e=n.elements;for(var s=0;s<e.length-1;s++)for(var a=s+1;a<e.length;a++)if(e[s].key===e[a].key&&e[s].placement===e[a].placement)throw new TypeError("Duplicated element ("+e[s].key+")")}}return{elements:e,finishers:r}},fromElementDescriptor:function(e){var t={kind:e.kind,key:e.key,placement:e.placement,descriptor:e.descriptor};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),"field"===e.kind&&(t.initializer=e.initializer),t},toElementDescriptors:function(e){var t;if(void 0!==e)return(t=e,function(e){if(Array.isArray(e))return e}(t)||function(e){if("undefined"!=typeof Symbol&&null!=e[Symbol.iterator]||null!=e["@@iterator"])return Array.from(e)}(t)||function(e,t){if(e){if("string"==typeof e)return Ge(e,t);var r=Object.prototype.toString.call(e).slice(8,-1);return"Object"===r&&e.constructor&&(r=e.constructor.name),"Map"===r||"Set"===r?Array.from(e):"Arguments"===r||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(r)?Ge(e,t):void 0}}(t)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()).map((function(e){var t=this.toElementDescriptor(e);return this.disallowProperty(e,"finisher","An element descriptor"),this.disallowProperty(e,"extras","An element descriptor"),t}),this)},toElementDescriptor:function(e){var t=String(e.kind);if("method"!==t&&"field"!==t)throw new TypeError('An element descriptor\'s .kind property must be either "method" or "field", but a decorator created an element descriptor with .kind "'+t+'"');var r=Ke(e.key),i=String(e.placement);if("static"!==i&&"prototype"!==i&&"own"!==i)throw new TypeError('An element descriptor\'s .placement property must be one of "static", "prototype" or "own", but a decorator created an element descriptor with .placement "'+i+'"');var o=e.descriptor;this.disallowProperty(e,"elements","An element descriptor");var n={kind:t,key:r,placement:i,descriptor:Object.assign({},o)};return"field"!==t?this.disallowProperty(e,"initializer","A method descriptor"):(this.disallowProperty(o,"get","The property descriptor of a field descriptor"),this.disallowProperty(o,"set","The property descriptor of a field descriptor"),this.disallowProperty(o,"value","The property descriptor of a field descriptor"),n.initializer=e.initializer),n},toElementFinisherExtras:function(e){return{element:this.toElementDescriptor(e),finisher:We(e,"finisher"),extras:this.toElementDescriptors(e.extras)}},fromClassDescriptor:function(e){var t={kind:"class",elements:e.map(this.fromElementDescriptor,this)};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),t},toClassDescriptor:function(e){var t=String(e.kind);if("class"!==t)throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator created a class descriptor with .kind "'+t+'"');this.disallowProperty(e,"key","A class descriptor"),this.disallowProperty(e,"placement","A class descriptor"),this.disallowProperty(e,"descriptor","A class descriptor"),this.disallowProperty(e,"initializer","A class descriptor"),this.disallowProperty(e,"extras","A class descriptor");var r=We(e,"finisher");return{elements:this.toElementDescriptors(e.elements),finisher:r}},runClassFinishers:function(e,t){for(var r=0;r<t.length;r++){var i=(0,t[r])(e);if(void 0!==i){if("function"!=typeof i)throw new TypeError("Finishers must return a constructor.");e=i}}return e},disallowProperty:function(e,t,r){if(void 0!==e[t])throw new TypeError(r+" can't have a ."+t+" property.")}};return e}function Ne(e){var t,r=Ke(e.key);"method"===e.kind?t={value:e.value,writable:!0,configurable:!0,enumerable:!1}:"get"===e.kind?t={get:e.value,configurable:!0,enumerable:!1}:"set"===e.kind?t={set:e.value,configurable:!0,enumerable:!1}:"field"===e.kind&&(t={configurable:!0,writable:!0,enumerable:!0});var i={kind:"field"===e.kind?"field":"method",key:r,placement:e.static?"static":"field"===e.kind?"own":"prototype",descriptor:t};return e.decorators&&(i.decorators=e.decorators),"field"===e.kind&&(i.initializer=e.value),i}function qe(e,t){void 0!==e.descriptor.get?t.descriptor.get=e.descriptor.get:t.descriptor.set=e.descriptor.set}function Qe(e){return e.decorators&&e.decorators.length}function Ye(e){return void 0!==e&&!(void 0===e.value&&void 0===e.writable)}function We(e,t){var r=e[t];if(void 0!==r&&"function"!=typeof r)throw new TypeError("Expected '"+t+"' to be a function");return r}function Ke(e){var t=function(e,t){if("object"!=typeof e||null===e)return e;var r=e[Symbol.toPrimitive];if(void 0!==r){var i=r.call(e,t||"default");if("object"!=typeof i)return i;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===t?String:Number)(e)}(e,"string");return"symbol"==typeof t?t:String(t)}function Ge(e,t){(null==t||t>e.length)&&(t=e.length);for(var r=0,i=new Array(t);r<t;r++)i[r]=e[r];return i}!function(e,t,r,i){var o=Ze();if(i)for(var n=0;n<i.length;n++)o=i[n](o);var s=t((function(e){o.initializeInstanceElements(e,a.elements)}),r),a=o.decorateClass(function(e){for(var t=[],r=function(e){return"method"===e.kind&&e.key===n.key&&e.placement===n.placement},i=0;i<e.length;i++){var o,n=e[i];if("method"===n.kind&&(o=t.find(r)))if(Ye(n.descriptor)||Ye(o.descriptor)){if(Qe(n)||Qe(o))throw new ReferenceError("Duplicated methods ("+n.key+") can't be decorated.");o.descriptor=n.descriptor}else{if(Qe(n)){if(Qe(o))throw new ReferenceError("Decorators can't be placed on different accessors with for the same property ("+n.key+").");o.decorators=n.decorators}qe(n,o)}else t.push(n)}return t}(s.d.map(Ne)),e);o.initializeClassElements(s.F,a.elements),o.runClassFinishers(s.F,a.finishers)}([(0,o.Mo)("hassio-addon-info-tab")],(function(e,t){return{F:class extends t{constructor(...t){super(...t),e(this)}},d:[{kind:"field",decorators:[(0,o.Cb)({type:Boolean})],key:"narrow",value:void 0},{kind:"field",decorators:[(0,o.Cb)({attribute:!1})],key:"route",value:void 0},{kind:"field",decorators:[(0,o.Cb)({attribute:!1})],key:"hass",value:void 0},{kind:"field",decorators:[(0,o.Cb)({attribute:!1})],key:"supervisor",value:void 0},{kind:"field",decorators:[(0,o.Cb)({attribute:!1})],key:"addon",value:void 0},{kind:"method",key:"render",value:function(){return this.addon?i.dy`
      <div class="content">
        <hassio-addon-info
          .narrow=${this.narrow}
          .route=${this.route}
          .hass=${this.hass}
          .supervisor=${this.supervisor}
          .addon=${this.addon}
        ></hassio-addon-info>
      </div>
    `:i.dy`<ha-circular-progress active></ha-circular-progress>`}},{kind:"get",static:!0,key:"styles",value:function(){return[h.Qx,p.l,i.iv`
        .content {
          margin: auto;
          padding: 8px;
          max-width: 1024px;
        }
      `]}}]}}),i.oi);r(4736);function Je(){Je=function(){return e};var e={elementsDefinitionOrder:[["method"],["field"]],initializeInstanceElements:function(e,t){["method","field"].forEach((function(r){t.forEach((function(t){t.kind===r&&"own"===t.placement&&this.defineClassElement(e,t)}),this)}),this)},initializeClassElements:function(e,t){var r=e.prototype;["method","field"].forEach((function(i){t.forEach((function(t){var o=t.placement;if(t.kind===i&&("static"===o||"prototype"===o)){var n="static"===o?e:r;this.defineClassElement(n,t)}}),this)}),this)},defineClassElement:function(e,t){var r=t.descriptor;if("field"===t.kind){var i=t.initializer;r={enumerable:r.enumerable,writable:r.writable,configurable:r.configurable,value:void 0===i?void 0:i.call(e)}}Object.defineProperty(e,t.key,r)},decorateClass:function(e,t){var r=[],i=[],o={static:[],prototype:[],own:[]};if(e.forEach((function(e){this.addElementPlacement(e,o)}),this),e.forEach((function(e){if(!tt(e))return r.push(e);var t=this.decorateElement(e,o);r.push(t.element),r.push.apply(r,t.extras),i.push.apply(i,t.finishers)}),this),!t)return{elements:r,finishers:i};var n=this.decorateConstructor(r,t);return i.push.apply(i,n.finishers),n.finishers=i,n},addElementPlacement:function(e,t,r){var i=t[e.placement];if(!r&&-1!==i.indexOf(e.key))throw new TypeError("Duplicated element ("+e.key+")");i.push(e.key)},decorateElement:function(e,t){for(var r=[],i=[],o=e.decorators,n=o.length-1;n>=0;n--){var s=t[e.placement];s.splice(s.indexOf(e.key),1);var a=this.fromElementDescriptor(e),d=this.toElementFinisherExtras((0,o[n])(a)||a);e=d.element,this.addElementPlacement(e,t),d.finisher&&i.push(d.finisher);var l=d.extras;if(l){for(var c=0;c<l.length;c++)this.addElementPlacement(l[c],t);r.push.apply(r,l)}}return{element:e,finishers:i,extras:r}},decorateConstructor:function(e,t){for(var r=[],i=t.length-1;i>=0;i--){var o=this.fromClassDescriptor(e),n=this.toClassDescriptor((0,t[i])(o)||o);if(void 0!==n.finisher&&r.push(n.finisher),void 0!==n.elements){e=n.elements;for(var s=0;s<e.length-1;s++)for(var a=s+1;a<e.length;a++)if(e[s].key===e[a].key&&e[s].placement===e[a].placement)throw new TypeError("Duplicated element ("+e[s].key+")")}}return{elements:e,finishers:r}},fromElementDescriptor:function(e){var t={kind:e.kind,key:e.key,placement:e.placement,descriptor:e.descriptor};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),"field"===e.kind&&(t.initializer=e.initializer),t},toElementDescriptors:function(e){var t;if(void 0!==e)return(t=e,function(e){if(Array.isArray(e))return e}(t)||function(e){if("undefined"!=typeof Symbol&&null!=e[Symbol.iterator]||null!=e["@@iterator"])return Array.from(e)}(t)||function(e,t){if(e){if("string"==typeof e)return nt(e,t);var r=Object.prototype.toString.call(e).slice(8,-1);return"Object"===r&&e.constructor&&(r=e.constructor.name),"Map"===r||"Set"===r?Array.from(e):"Arguments"===r||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(r)?nt(e,t):void 0}}(t)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()).map((function(e){var t=this.toElementDescriptor(e);return this.disallowProperty(e,"finisher","An element descriptor"),this.disallowProperty(e,"extras","An element descriptor"),t}),this)},toElementDescriptor:function(e){var t=String(e.kind);if("method"!==t&&"field"!==t)throw new TypeError('An element descriptor\'s .kind property must be either "method" or "field", but a decorator created an element descriptor with .kind "'+t+'"');var r=ot(e.key),i=String(e.placement);if("static"!==i&&"prototype"!==i&&"own"!==i)throw new TypeError('An element descriptor\'s .placement property must be one of "static", "prototype" or "own", but a decorator created an element descriptor with .placement "'+i+'"');var o=e.descriptor;this.disallowProperty(e,"elements","An element descriptor");var n={kind:t,key:r,placement:i,descriptor:Object.assign({},o)};return"field"!==t?this.disallowProperty(e,"initializer","A method descriptor"):(this.disallowProperty(o,"get","The property descriptor of a field descriptor"),this.disallowProperty(o,"set","The property descriptor of a field descriptor"),this.disallowProperty(o,"value","The property descriptor of a field descriptor"),n.initializer=e.initializer),n},toElementFinisherExtras:function(e){return{element:this.toElementDescriptor(e),finisher:it(e,"finisher"),extras:this.toElementDescriptors(e.extras)}},fromClassDescriptor:function(e){var t={kind:"class",elements:e.map(this.fromElementDescriptor,this)};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),t},toClassDescriptor:function(e){var t=String(e.kind);if("class"!==t)throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator created a class descriptor with .kind "'+t+'"');this.disallowProperty(e,"key","A class descriptor"),this.disallowProperty(e,"placement","A class descriptor"),this.disallowProperty(e,"descriptor","A class descriptor"),this.disallowProperty(e,"initializer","A class descriptor"),this.disallowProperty(e,"extras","A class descriptor");var r=it(e,"finisher");return{elements:this.toElementDescriptors(e.elements),finisher:r}},runClassFinishers:function(e,t){for(var r=0;r<t.length;r++){var i=(0,t[r])(e);if(void 0!==i){if("function"!=typeof i)throw new TypeError("Finishers must return a constructor.");e=i}}return e},disallowProperty:function(e,t,r){if(void 0!==e[t])throw new TypeError(r+" can't have a ."+t+" property.")}};return e}function Xe(e){var t,r=ot(e.key);"method"===e.kind?t={value:e.value,writable:!0,configurable:!0,enumerable:!1}:"get"===e.kind?t={get:e.value,configurable:!0,enumerable:!1}:"set"===e.kind?t={set:e.value,configurable:!0,enumerable:!1}:"field"===e.kind&&(t={configurable:!0,writable:!0,enumerable:!0});var i={kind:"field"===e.kind?"field":"method",key:r,placement:e.static?"static":"field"===e.kind?"own":"prototype",descriptor:t};return e.decorators&&(i.decorators=e.decorators),"field"===e.kind&&(i.initializer=e.value),i}function et(e,t){void 0!==e.descriptor.get?t.descriptor.get=e.descriptor.get:t.descriptor.set=e.descriptor.set}function tt(e){return e.decorators&&e.decorators.length}function rt(e){return void 0!==e&&!(void 0===e.value&&void 0===e.writable)}function it(e,t){var r=e[t];if(void 0!==r&&"function"!=typeof r)throw new TypeError("Expected '"+t+"' to be a function");return r}function ot(e){var t=function(e,t){if("object"!=typeof e||null===e)return e;var r=e[Symbol.toPrimitive];if(void 0!==r){var i=r.call(e,t||"default");if("object"!=typeof i)return i;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===t?String:Number)(e)}(e,"string");return"symbol"==typeof t?t:String(t)}function nt(e,t){(null==t||t>e.length)&&(t=e.length);for(var r=0,i=new Array(t);r<t;r++)i[r]=e[r];return i}function st(e,t,r){return st="undefined"!=typeof Reflect&&Reflect.get?Reflect.get:function(e,t,r){var i=function(e,t){for(;!Object.prototype.hasOwnProperty.call(e,t)&&null!==(e=at(e)););return e}(e,t);if(i){var o=Object.getOwnPropertyDescriptor(i,t);return o.get?o.get.call(r):o.value}},st(e,t,r||e)}function at(e){return at=Object.setPrototypeOf?Object.getPrototypeOf:function(e){return e.__proto__||Object.getPrototypeOf(e)},at(e)}!function(e,t,r,i){var o=Je();if(i)for(var n=0;n<i.length;n++)o=i[n](o);var s=t((function(e){o.initializeInstanceElements(e,a.elements)}),r),a=o.decorateClass(function(e){for(var t=[],r=function(e){return"method"===e.kind&&e.key===n.key&&e.placement===n.placement},i=0;i<e.length;i++){var o,n=e[i];if("method"===n.kind&&(o=t.find(r)))if(rt(n.descriptor)||rt(o.descriptor)){if(tt(n)||tt(o))throw new ReferenceError("Duplicated methods ("+n.key+") can't be decorated.");o.descriptor=n.descriptor}else{if(tt(n)){if(tt(o))throw new ReferenceError("Decorators can't be placed on different accessors with for the same property ("+n.key+").");o.decorators=n.decorators}et(n,o)}else t.push(n)}return t}(s.d.map(Xe)),e);o.initializeClassElements(s.F,a.elements),o.runClassFinishers(s.F,a.finishers)}([(0,o.Mo)("hassio-addon-logs")],(function(e,t){class r extends t{constructor(...t){super(...t),e(this)}}return{F:r,d:[{kind:"field",decorators:[(0,o.Cb)({attribute:!1})],key:"hass",value:void 0},{kind:"field",decorators:[(0,o.Cb)({attribute:!1})],key:"supervisor",value:void 0},{kind:"field",decorators:[(0,o.Cb)({attribute:!1})],key:"addon",value:void 0},{kind:"field",decorators:[(0,o.SB)()],key:"_error",value:void 0},{kind:"field",decorators:[(0,o.SB)()],key:"_content",value:void 0},{kind:"method",key:"connectedCallback",value:async function(){st(at(r.prototype),"connectedCallback",this).call(this),await this._loadData()}},{kind:"method",key:"render",value:function(){return i.dy`
      <h1>${this.addon.name}</h1>
      <ha-card>
        ${this._error?i.dy`<ha-alert alert-type="error">${this._error}</ha-alert>`:""}
        <div class="card-content">
          ${this._content?i.dy`<ha-ansi-to-html
                .content=${this._content}
              ></ha-ansi-to-html>`:""}
        </div>
        <div class="card-actions">
          <mwc-button @click=${this._refresh}>
            ${this.supervisor.localize("common.refresh")}
          </mwc-button>
        </div>
      </ha-card>
    `}},{kind:"get",static:!0,key:"styles",value:function(){return[h.Qx,p.l,i.iv`
        :host,
        ha-card {
          display: block;
        }
      `]}},{kind:"method",key:"_loadData",value:async function(){this._error=void 0;try{this._content=await(0,l.kr)(this.hass,this.addon.slug)}catch(e){this._error=this.supervisor.localize("addon.logs.get_logs","error",(0,c.js)(e))}}},{kind:"method",key:"_refresh",value:async function(){await this._loadData()}}]}}),i.oi);function dt(){dt=function(){return e};var e={elementsDefinitionOrder:[["method"],["field"]],initializeInstanceElements:function(e,t){["method","field"].forEach((function(r){t.forEach((function(t){t.kind===r&&"own"===t.placement&&this.defineClassElement(e,t)}),this)}),this)},initializeClassElements:function(e,t){var r=e.prototype;["method","field"].forEach((function(i){t.forEach((function(t){var o=t.placement;if(t.kind===i&&("static"===o||"prototype"===o)){var n="static"===o?e:r;this.defineClassElement(n,t)}}),this)}),this)},defineClassElement:function(e,t){var r=t.descriptor;if("field"===t.kind){var i=t.initializer;r={enumerable:r.enumerable,writable:r.writable,configurable:r.configurable,value:void 0===i?void 0:i.call(e)}}Object.defineProperty(e,t.key,r)},decorateClass:function(e,t){var r=[],i=[],o={static:[],prototype:[],own:[]};if(e.forEach((function(e){this.addElementPlacement(e,o)}),this),e.forEach((function(e){if(!ht(e))return r.push(e);var t=this.decorateElement(e,o);r.push(t.element),r.push.apply(r,t.extras),i.push.apply(i,t.finishers)}),this),!t)return{elements:r,finishers:i};var n=this.decorateConstructor(r,t);return i.push.apply(i,n.finishers),n.finishers=i,n},addElementPlacement:function(e,t,r){var i=t[e.placement];if(!r&&-1!==i.indexOf(e.key))throw new TypeError("Duplicated element ("+e.key+")");i.push(e.key)},decorateElement:function(e,t){for(var r=[],i=[],o=e.decorators,n=o.length-1;n>=0;n--){var s=t[e.placement];s.splice(s.indexOf(e.key),1);var a=this.fromElementDescriptor(e),d=this.toElementFinisherExtras((0,o[n])(a)||a);e=d.element,this.addElementPlacement(e,t),d.finisher&&i.push(d.finisher);var l=d.extras;if(l){for(var c=0;c<l.length;c++)this.addElementPlacement(l[c],t);r.push.apply(r,l)}}return{element:e,finishers:i,extras:r}},decorateConstructor:function(e,t){for(var r=[],i=t.length-1;i>=0;i--){var o=this.fromClassDescriptor(e),n=this.toClassDescriptor((0,t[i])(o)||o);if(void 0!==n.finisher&&r.push(n.finisher),void 0!==n.elements){e=n.elements;for(var s=0;s<e.length-1;s++)for(var a=s+1;a<e.length;a++)if(e[s].key===e[a].key&&e[s].placement===e[a].placement)throw new TypeError("Duplicated element ("+e[s].key+")")}}return{elements:e,finishers:r}},fromElementDescriptor:function(e){var t={kind:e.kind,key:e.key,placement:e.placement,descriptor:e.descriptor};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),"field"===e.kind&&(t.initializer=e.initializer),t},toElementDescriptors:function(e){var t;if(void 0!==e)return(t=e,function(e){if(Array.isArray(e))return e}(t)||function(e){if("undefined"!=typeof Symbol&&null!=e[Symbol.iterator]||null!=e["@@iterator"])return Array.from(e)}(t)||function(e,t){if(e){if("string"==typeof e)return mt(e,t);var r=Object.prototype.toString.call(e).slice(8,-1);return"Object"===r&&e.constructor&&(r=e.constructor.name),"Map"===r||"Set"===r?Array.from(e):"Arguments"===r||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(r)?mt(e,t):void 0}}(t)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()).map((function(e){var t=this.toElementDescriptor(e);return this.disallowProperty(e,"finisher","An element descriptor"),this.disallowProperty(e,"extras","An element descriptor"),t}),this)},toElementDescriptor:function(e){var t=String(e.kind);if("method"!==t&&"field"!==t)throw new TypeError('An element descriptor\'s .kind property must be either "method" or "field", but a decorator created an element descriptor with .kind "'+t+'"');var r=ft(e.key),i=String(e.placement);if("static"!==i&&"prototype"!==i&&"own"!==i)throw new TypeError('An element descriptor\'s .placement property must be one of "static", "prototype" or "own", but a decorator created an element descriptor with .placement "'+i+'"');var o=e.descriptor;this.disallowProperty(e,"elements","An element descriptor");var n={kind:t,key:r,placement:i,descriptor:Object.assign({},o)};return"field"!==t?this.disallowProperty(e,"initializer","A method descriptor"):(this.disallowProperty(o,"get","The property descriptor of a field descriptor"),this.disallowProperty(o,"set","The property descriptor of a field descriptor"),this.disallowProperty(o,"value","The property descriptor of a field descriptor"),n.initializer=e.initializer),n},toElementFinisherExtras:function(e){return{element:this.toElementDescriptor(e),finisher:ut(e,"finisher"),extras:this.toElementDescriptors(e.extras)}},fromClassDescriptor:function(e){var t={kind:"class",elements:e.map(this.fromElementDescriptor,this)};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),t},toClassDescriptor:function(e){var t=String(e.kind);if("class"!==t)throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator created a class descriptor with .kind "'+t+'"');this.disallowProperty(e,"key","A class descriptor"),this.disallowProperty(e,"placement","A class descriptor"),this.disallowProperty(e,"descriptor","A class descriptor"),this.disallowProperty(e,"initializer","A class descriptor"),this.disallowProperty(e,"extras","A class descriptor");var r=ut(e,"finisher");return{elements:this.toElementDescriptors(e.elements),finisher:r}},runClassFinishers:function(e,t){for(var r=0;r<t.length;r++){var i=(0,t[r])(e);if(void 0!==i){if("function"!=typeof i)throw new TypeError("Finishers must return a constructor.");e=i}}return e},disallowProperty:function(e,t,r){if(void 0!==e[t])throw new TypeError(r+" can't have a ."+t+" property.")}};return e}function lt(e){var t,r=ft(e.key);"method"===e.kind?t={value:e.value,writable:!0,configurable:!0,enumerable:!1}:"get"===e.kind?t={get:e.value,configurable:!0,enumerable:!1}:"set"===e.kind?t={set:e.value,configurable:!0,enumerable:!1}:"field"===e.kind&&(t={configurable:!0,writable:!0,enumerable:!0});var i={kind:"field"===e.kind?"field":"method",key:r,placement:e.static?"static":"field"===e.kind?"own":"prototype",descriptor:t};return e.decorators&&(i.decorators=e.decorators),"field"===e.kind&&(i.initializer=e.value),i}function ct(e,t){void 0!==e.descriptor.get?t.descriptor.get=e.descriptor.get:t.descriptor.set=e.descriptor.set}function ht(e){return e.decorators&&e.decorators.length}function pt(e){return void 0!==e&&!(void 0===e.value&&void 0===e.writable)}function ut(e,t){var r=e[t];if(void 0!==r&&"function"!=typeof r)throw new TypeError("Expected '"+t+"' to be a function");return r}function ft(e){var t=function(e,t){if("object"!=typeof e||null===e)return e;var r=e[Symbol.toPrimitive];if(void 0!==r){var i=r.call(e,t||"default");if("object"!=typeof i)return i;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===t?String:Number)(e)}(e,"string");return"symbol"==typeof t?t:String(t)}function mt(e,t){(null==t||t>e.length)&&(t=e.length);for(var r=0,i=new Array(t);r<t;r++)i[r]=e[r];return i}!function(e,t,r,i){var o=dt();if(i)for(var n=0;n<i.length;n++)o=i[n](o);var s=t((function(e){o.initializeInstanceElements(e,a.elements)}),r),a=o.decorateClass(function(e){for(var t=[],r=function(e){return"method"===e.kind&&e.key===n.key&&e.placement===n.placement},i=0;i<e.length;i++){var o,n=e[i];if("method"===n.kind&&(o=t.find(r)))if(pt(n.descriptor)||pt(o.descriptor)){if(ht(n)||ht(o))throw new ReferenceError("Duplicated methods ("+n.key+") can't be decorated.");o.descriptor=n.descriptor}else{if(ht(n)){if(ht(o))throw new ReferenceError("Decorators can't be placed on different accessors with for the same property ("+n.key+").");o.decorators=n.decorators}ct(n,o)}else t.push(n)}return t}(s.d.map(lt)),e);o.initializeClassElements(s.F,a.elements),o.runClassFinishers(s.F,a.finishers)}([(0,o.Mo)("hassio-addon-log-tab")],(function(e,t){return{F:class extends t{constructor(...t){super(...t),e(this)}},d:[{kind:"field",decorators:[(0,o.Cb)({attribute:!1})],key:"hass",value:void 0},{kind:"field",decorators:[(0,o.Cb)({attribute:!1})],key:"supervisor",value:void 0},{kind:"field",decorators:[(0,o.Cb)({attribute:!1})],key:"addon",value:void 0},{kind:"method",key:"render",value:function(){return this.addon?i.dy`
      <div class="content">
        <hassio-addon-logs
          .hass=${this.hass}
          .supervisor=${this.supervisor}
          .addon=${this.addon}
        ></hassio-addon-logs>
      </div>
    `:i.dy` <ha-circular-progress active></ha-circular-progress> `}},{kind:"get",static:!0,key:"styles",value:function(){return[h.Qx,p.l,i.iv`
        .content {
          margin: auto;
          padding: 8px;
          max-width: 1024px;
        }
      `]}}]}}),i.oi);function vt(){vt=function(){return e};var e={elementsDefinitionOrder:[["method"],["field"]],initializeInstanceElements:function(e,t){["method","field"].forEach((function(r){t.forEach((function(t){t.kind===r&&"own"===t.placement&&this.defineClassElement(e,t)}),this)}),this)},initializeClassElements:function(e,t){var r=e.prototype;["method","field"].forEach((function(i){t.forEach((function(t){var o=t.placement;if(t.kind===i&&("static"===o||"prototype"===o)){var n="static"===o?e:r;this.defineClassElement(n,t)}}),this)}),this)},defineClassElement:function(e,t){var r=t.descriptor;if("field"===t.kind){var i=t.initializer;r={enumerable:r.enumerable,writable:r.writable,configurable:r.configurable,value:void 0===i?void 0:i.call(e)}}Object.defineProperty(e,t.key,r)},decorateClass:function(e,t){var r=[],i=[],o={static:[],prototype:[],own:[]};if(e.forEach((function(e){this.addElementPlacement(e,o)}),this),e.forEach((function(e){if(!bt(e))return r.push(e);var t=this.decorateElement(e,o);r.push(t.element),r.push.apply(r,t.extras),i.push.apply(i,t.finishers)}),this),!t)return{elements:r,finishers:i};var n=this.decorateConstructor(r,t);return i.push.apply(i,n.finishers),n.finishers=i,n},addElementPlacement:function(e,t,r){var i=t[e.placement];if(!r&&-1!==i.indexOf(e.key))throw new TypeError("Duplicated element ("+e.key+")");i.push(e.key)},decorateElement:function(e,t){for(var r=[],i=[],o=e.decorators,n=o.length-1;n>=0;n--){var s=t[e.placement];s.splice(s.indexOf(e.key),1);var a=this.fromElementDescriptor(e),d=this.toElementFinisherExtras((0,o[n])(a)||a);e=d.element,this.addElementPlacement(e,t),d.finisher&&i.push(d.finisher);var l=d.extras;if(l){for(var c=0;c<l.length;c++)this.addElementPlacement(l[c],t);r.push.apply(r,l)}}return{element:e,finishers:i,extras:r}},decorateConstructor:function(e,t){for(var r=[],i=t.length-1;i>=0;i--){var o=this.fromClassDescriptor(e),n=this.toClassDescriptor((0,t[i])(o)||o);if(void 0!==n.finisher&&r.push(n.finisher),void 0!==n.elements){e=n.elements;for(var s=0;s<e.length-1;s++)for(var a=s+1;a<e.length;a++)if(e[s].key===e[a].key&&e[s].placement===e[a].placement)throw new TypeError("Duplicated element ("+e[s].key+")")}}return{elements:e,finishers:r}},fromElementDescriptor:function(e){var t={kind:e.kind,key:e.key,placement:e.placement,descriptor:e.descriptor};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),"field"===e.kind&&(t.initializer=e.initializer),t},toElementDescriptors:function(e){var t;if(void 0!==e)return(t=e,function(e){if(Array.isArray(e))return e}(t)||function(e){if("undefined"!=typeof Symbol&&null!=e[Symbol.iterator]||null!=e["@@iterator"])return Array.from(e)}(t)||function(e,t){if(e){if("string"==typeof e)return Ct(e,t);var r=Object.prototype.toString.call(e).slice(8,-1);return"Object"===r&&e.constructor&&(r=e.constructor.name),"Map"===r||"Set"===r?Array.from(e):"Arguments"===r||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(r)?Ct(e,t):void 0}}(t)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()).map((function(e){var t=this.toElementDescriptor(e);return this.disallowProperty(e,"finisher","An element descriptor"),this.disallowProperty(e,"extras","An element descriptor"),t}),this)},toElementDescriptor:function(e){var t=String(e.kind);if("method"!==t&&"field"!==t)throw new TypeError('An element descriptor\'s .kind property must be either "method" or "field", but a decorator created an element descriptor with .kind "'+t+'"');var r=Et(e.key),i=String(e.placement);if("static"!==i&&"prototype"!==i&&"own"!==i)throw new TypeError('An element descriptor\'s .placement property must be one of "static", "prototype" or "own", but a decorator created an element descriptor with .placement "'+i+'"');var o=e.descriptor;this.disallowProperty(e,"elements","An element descriptor");var n={kind:t,key:r,placement:i,descriptor:Object.assign({},o)};return"field"!==t?this.disallowProperty(e,"initializer","A method descriptor"):(this.disallowProperty(o,"get","The property descriptor of a field descriptor"),this.disallowProperty(o,"set","The property descriptor of a field descriptor"),this.disallowProperty(o,"value","The property descriptor of a field descriptor"),n.initializer=e.initializer),n},toElementFinisherExtras:function(e){return{element:this.toElementDescriptor(e),finisher:wt(e,"finisher"),extras:this.toElementDescriptors(e.extras)}},fromClassDescriptor:function(e){var t={kind:"class",elements:e.map(this.fromElementDescriptor,this)};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),t},toClassDescriptor:function(e){var t=String(e.kind);if("class"!==t)throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator created a class descriptor with .kind "'+t+'"');this.disallowProperty(e,"key","A class descriptor"),this.disallowProperty(e,"placement","A class descriptor"),this.disallowProperty(e,"descriptor","A class descriptor"),this.disallowProperty(e,"initializer","A class descriptor"),this.disallowProperty(e,"extras","A class descriptor");var r=wt(e,"finisher");return{elements:this.toElementDescriptors(e.elements),finisher:r}},runClassFinishers:function(e,t){for(var r=0;r<t.length;r++){var i=(0,t[r])(e);if(void 0!==i){if("function"!=typeof i)throw new TypeError("Finishers must return a constructor.");e=i}}return e},disallowProperty:function(e,t,r){if(void 0!==e[t])throw new TypeError(r+" can't have a ."+t+" property.")}};return e}function yt(e){var t,r=Et(e.key);"method"===e.kind?t={value:e.value,writable:!0,configurable:!0,enumerable:!1}:"get"===e.kind?t={get:e.value,configurable:!0,enumerable:!1}:"set"===e.kind?t={set:e.value,configurable:!0,enumerable:!1}:"field"===e.kind&&(t={configurable:!0,writable:!0,enumerable:!0});var i={kind:"field"===e.kind?"field":"method",key:r,placement:e.static?"static":"field"===e.kind?"own":"prototype",descriptor:t};return e.decorators&&(i.decorators=e.decorators),"field"===e.kind&&(i.initializer=e.value),i}function gt(e,t){void 0!==e.descriptor.get?t.descriptor.get=e.descriptor.get:t.descriptor.set=e.descriptor.set}function bt(e){return e.decorators&&e.decorators.length}function kt(e){return void 0!==e&&!(void 0===e.value&&void 0===e.writable)}function wt(e,t){var r=e[t];if(void 0!==r&&"function"!=typeof r)throw new TypeError("Expected '"+t+"' to be a function");return r}function Et(e){var t=function(e,t){if("object"!=typeof e||null===e)return e;var r=e[Symbol.toPrimitive];if(void 0!==r){var i=r.call(e,t||"default");if("object"!=typeof i)return i;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===t?String:Number)(e)}(e,"string");return"symbol"==typeof t?t:String(t)}function Ct(e,t){(null==t||t>e.length)&&(t=e.length);for(var r=0,i=new Array(t);r<t;r++)i[r]=e[r];return i}!function(e,t,r,i){var o=vt();if(i)for(var n=0;n<i.length;n++)o=i[n](o);var s=t((function(e){o.initializeInstanceElements(e,a.elements)}),r),a=o.decorateClass(function(e){for(var t=[],r=function(e){return"method"===e.kind&&e.key===n.key&&e.placement===n.placement},i=0;i<e.length;i++){var o,n=e[i];if("method"===n.kind&&(o=t.find(r)))if(kt(n.descriptor)||kt(o.descriptor)){if(bt(n)||bt(o))throw new ReferenceError("Duplicated methods ("+n.key+") can't be decorated.");o.descriptor=n.descriptor}else{if(bt(n)){if(bt(o))throw new ReferenceError("Decorators can't be placed on different accessors with for the same property ("+n.key+").");o.decorators=n.decorators}gt(n,o)}else t.push(n)}return t}(s.d.map(yt)),e);o.initializeClassElements(s.F,a.elements),o.runClassFinishers(s.F,a.finishers)}([(0,o.Mo)("hassio-addon-router")],(function(e,t){return{F:class extends t{constructor(...t){super(...t),e(this)}},d:[{kind:"field",decorators:[(0,o.Cb)({type:Boolean})],key:"narrow",value:()=>!1},{kind:"field",decorators:[(0,o.Cb)({attribute:!1})],key:"hass",value:void 0},{kind:"field",decorators:[(0,o.Cb)({attribute:!1})],key:"supervisor",value:void 0},{kind:"field",decorators:[(0,o.Cb)({attribute:!1})],key:"addon",value:void 0},{kind:"field",key:"routerOptions",value:()=>({defaultPage:"info",showLoading:!0,routes:{info:{tag:"hassio-addon-info-tab"},documentation:{tag:"hassio-addon-documentation-tab"},config:{tag:"hassio-addon-config-tab"},logs:{tag:"hassio-addon-log-tab"}}})},{kind:"method",key:"updatePageEl",value:function(e){e.route=this.routeTail,e.hass=this.hass,e.supervisor=this.supervisor,e.addon=this.addon,e.narrow=this.narrow}}]}}),G.n);function _t(){_t=function(){return e};var e={elementsDefinitionOrder:[["method"],["field"]],initializeInstanceElements:function(e,t){["method","field"].forEach((function(r){t.forEach((function(t){t.kind===r&&"own"===t.placement&&this.defineClassElement(e,t)}),this)}),this)},initializeClassElements:function(e,t){var r=e.prototype;["method","field"].forEach((function(i){t.forEach((function(t){var o=t.placement;if(t.kind===i&&("static"===o||"prototype"===o)){var n="static"===o?e:r;this.defineClassElement(n,t)}}),this)}),this)},defineClassElement:function(e,t){var r=t.descriptor;if("field"===t.kind){var i=t.initializer;r={enumerable:r.enumerable,writable:r.writable,configurable:r.configurable,value:void 0===i?void 0:i.call(e)}}Object.defineProperty(e,t.key,r)},decorateClass:function(e,t){var r=[],i=[],o={static:[],prototype:[],own:[]};if(e.forEach((function(e){this.addElementPlacement(e,o)}),this),e.forEach((function(e){if(!$t(e))return r.push(e);var t=this.decorateElement(e,o);r.push(t.element),r.push.apply(r,t.extras),i.push.apply(i,t.finishers)}),this),!t)return{elements:r,finishers:i};var n=this.decorateConstructor(r,t);return i.push.apply(i,n.finishers),n.finishers=i,n},addElementPlacement:function(e,t,r){var i=t[e.placement];if(!r&&-1!==i.indexOf(e.key))throw new TypeError("Duplicated element ("+e.key+")");i.push(e.key)},decorateElement:function(e,t){for(var r=[],i=[],o=e.decorators,n=o.length-1;n>=0;n--){var s=t[e.placement];s.splice(s.indexOf(e.key),1);var a=this.fromElementDescriptor(e),d=this.toElementFinisherExtras((0,o[n])(a)||a);e=d.element,this.addElementPlacement(e,t),d.finisher&&i.push(d.finisher);var l=d.extras;if(l){for(var c=0;c<l.length;c++)this.addElementPlacement(l[c],t);r.push.apply(r,l)}}return{element:e,finishers:i,extras:r}},decorateConstructor:function(e,t){for(var r=[],i=t.length-1;i>=0;i--){var o=this.fromClassDescriptor(e),n=this.toClassDescriptor((0,t[i])(o)||o);if(void 0!==n.finisher&&r.push(n.finisher),void 0!==n.elements){e=n.elements;for(var s=0;s<e.length-1;s++)for(var a=s+1;a<e.length;a++)if(e[s].key===e[a].key&&e[s].placement===e[a].placement)throw new TypeError("Duplicated element ("+e[s].key+")")}}return{elements:e,finishers:r}},fromElementDescriptor:function(e){var t={kind:e.kind,key:e.key,placement:e.placement,descriptor:e.descriptor};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),"field"===e.kind&&(t.initializer=e.initializer),t},toElementDescriptors:function(e){var t;if(void 0!==e)return(t=e,function(e){if(Array.isArray(e))return e}(t)||function(e){if("undefined"!=typeof Symbol&&null!=e[Symbol.iterator]||null!=e["@@iterator"])return Array.from(e)}(t)||function(e,t){if(e){if("string"==typeof e)return St(e,t);var r=Object.prototype.toString.call(e).slice(8,-1);return"Object"===r&&e.constructor&&(r=e.constructor.name),"Map"===r||"Set"===r?Array.from(e):"Arguments"===r||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(r)?St(e,t):void 0}}(t)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()).map((function(e){var t=this.toElementDescriptor(e);return this.disallowProperty(e,"finisher","An element descriptor"),this.disallowProperty(e,"extras","An element descriptor"),t}),this)},toElementDescriptor:function(e){var t=String(e.kind);if("method"!==t&&"field"!==t)throw new TypeError('An element descriptor\'s .kind property must be either "method" or "field", but a decorator created an element descriptor with .kind "'+t+'"');var r=zt(e.key),i=String(e.placement);if("static"!==i&&"prototype"!==i&&"own"!==i)throw new TypeError('An element descriptor\'s .placement property must be one of "static", "prototype" or "own", but a decorator created an element descriptor with .placement "'+i+'"');var o=e.descriptor;this.disallowProperty(e,"elements","An element descriptor");var n={kind:t,key:r,placement:i,descriptor:Object.assign({},o)};return"field"!==t?this.disallowProperty(e,"initializer","A method descriptor"):(this.disallowProperty(o,"get","The property descriptor of a field descriptor"),this.disallowProperty(o,"set","The property descriptor of a field descriptor"),this.disallowProperty(o,"value","The property descriptor of a field descriptor"),n.initializer=e.initializer),n},toElementFinisherExtras:function(e){return{element:this.toElementDescriptor(e),finisher:Dt(e,"finisher"),extras:this.toElementDescriptors(e.extras)}},fromClassDescriptor:function(e){var t={kind:"class",elements:e.map(this.fromElementDescriptor,this)};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),t},toClassDescriptor:function(e){var t=String(e.kind);if("class"!==t)throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator created a class descriptor with .kind "'+t+'"');this.disallowProperty(e,"key","A class descriptor"),this.disallowProperty(e,"placement","A class descriptor"),this.disallowProperty(e,"descriptor","A class descriptor"),this.disallowProperty(e,"initializer","A class descriptor"),this.disallowProperty(e,"extras","A class descriptor");var r=Dt(e,"finisher");return{elements:this.toElementDescriptors(e.elements),finisher:r}},runClassFinishers:function(e,t){for(var r=0;r<t.length;r++){var i=(0,t[r])(e);if(void 0!==i){if("function"!=typeof i)throw new TypeError("Finishers must return a constructor.");e=i}}return e},disallowProperty:function(e,t,r){if(void 0!==e[t])throw new TypeError(r+" can't have a ."+t+" property.")}};return e}function At(e){var t,r=zt(e.key);"method"===e.kind?t={value:e.value,writable:!0,configurable:!0,enumerable:!1}:"get"===e.kind?t={get:e.value,configurable:!0,enumerable:!1}:"set"===e.kind?t={set:e.value,configurable:!0,enumerable:!1}:"field"===e.kind&&(t={configurable:!0,writable:!0,enumerable:!0});var i={kind:"field"===e.kind?"field":"method",key:r,placement:e.static?"static":"field"===e.kind?"own":"prototype",descriptor:t};return e.decorators&&(i.decorators=e.decorators),"field"===e.kind&&(i.initializer=e.value),i}function Pt(e,t){void 0!==e.descriptor.get?t.descriptor.get=e.descriptor.get:t.descriptor.set=e.descriptor.set}function $t(e){return e.decorators&&e.decorators.length}function xt(e){return void 0!==e&&!(void 0===e.value&&void 0===e.writable)}function Dt(e,t){var r=e[t];if(void 0!==r&&"function"!=typeof r)throw new TypeError("Expected '"+t+"' to be a function");return r}function zt(e){var t=function(e,t){if("object"!=typeof e||null===e)return e;var r=e[Symbol.toPrimitive];if(void 0!==r){var i=r.call(e,t||"default");if("object"!=typeof i)return i;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===t?String:Number)(e)}(e,"string");return"symbol"==typeof t?t:String(t)}function St(e,t){(null==t||t>e.length)&&(t=e.length);for(var r=0,i=new Array(t);r<t;r++)i[r]=e[r];return i}!function(e,t,r,i){var o=_t();if(i)for(var n=0;n<i.length;n++)o=i[n](o);var s=t((function(e){o.initializeInstanceElements(e,a.elements)}),r),a=o.decorateClass(function(e){for(var t=[],r=function(e){return"method"===e.kind&&e.key===n.key&&e.placement===n.placement},i=0;i<e.length;i++){var o,n=e[i];if("method"===n.kind&&(o=t.find(r)))if(xt(n.descriptor)||xt(o.descriptor)){if($t(n)||$t(o))throw new ReferenceError("Duplicated methods ("+n.key+") can't be decorated.");o.descriptor=n.descriptor}else{if($t(n)){if($t(o))throw new ReferenceError("Decorators can't be placed on different accessors with for the same property ("+n.key+").");o.decorators=n.decorators}Pt(n,o)}else t.push(n)}return t}(s.d.map(At)),e);o.initializeClassElements(s.F,a.elements),o.runClassFinishers(s.F,a.finishers)}([(0,o.Mo)("hassio-addon-dashboard")],(function(e,t){return{F:class extends t{constructor(...t){super(...t),e(this)}},d:[{kind:"field",decorators:[(0,o.Cb)({attribute:!1})],key:"hass",value:void 0},{kind:"field",decorators:[(0,o.Cb)({attribute:!1})],key:"supervisor",value:void 0},{kind:"field",decorators:[(0,o.Cb)({attribute:!1})],key:"route",value:void 0},{kind:"field",decorators:[(0,o.Cb)({attribute:!1})],key:"addon",value:void 0},{kind:"field",decorators:[(0,o.Cb)({type:Boolean})],key:"narrow",value:void 0},{kind:"field",decorators:[(0,o.SB)()],key:"_error",value:void 0},{kind:"field",key:"_computeTail",value:()=>(0,n.Z)((e=>{const t=e.path.indexOf("/",1);return-1===t?{prefix:e.prefix+e.path,path:""}:{prefix:e.prefix+e.path.substr(0,t),path:e.path.substr(t)}}))},{kind:"method",key:"render",value:function(){if(this._error)return i.dy`<hass-error-screen
        .error=${this._error}
      ></hass-error-screen>`;if(!this.addon)return i.dy`<hass-loading-screen></hass-loading-screen>`;const e=[{translationKey:"addon.panel.info",path:`/hassio/addon/${this.addon.slug}/info`,iconPath:"M13.5,4A1.5,1.5 0 0,0 12,5.5A1.5,1.5 0 0,0 13.5,7A1.5,1.5 0 0,0 15,5.5A1.5,1.5 0 0,0 13.5,4M13.14,8.77C11.95,8.87 8.7,11.46 8.7,11.46C8.5,11.61 8.56,11.6 8.72,11.88C8.88,12.15 8.86,12.17 9.05,12.04C9.25,11.91 9.58,11.7 10.13,11.36C12.25,10 10.47,13.14 9.56,18.43C9.2,21.05 11.56,19.7 12.17,19.3C12.77,18.91 14.38,17.8 14.54,17.69C14.76,17.54 14.6,17.42 14.43,17.17C14.31,17 14.19,17.12 14.19,17.12C13.54,17.55 12.35,18.45 12.19,17.88C12,17.31 13.22,13.4 13.89,10.71C14,10.07 14.3,8.67 13.14,8.77Z"}];this.addon.documentation&&e.push({translationKey:"addon.panel.documentation",path:`/hassio/addon/${this.addon.slug}/documentation`,iconPath:"M13,9H18.5L13,3.5V9M6,2H14L20,8V20A2,2 0 0,1 18,22H6C4.89,22 4,21.1 4,20V4C4,2.89 4.89,2 6,2M15,18V16H6V18H15M18,14V12H6V14H18Z"}),this.addon.version&&e.push({translationKey:"addon.panel.configuration",path:`/hassio/addon/${this.addon.slug}/config`,iconPath:"M15.9,18.45C17.25,18.45 18.35,17.35 18.35,16C18.35,14.65 17.25,13.55 15.9,13.55C14.54,13.55 13.45,14.65 13.45,16C13.45,17.35 14.54,18.45 15.9,18.45M21.1,16.68L22.58,17.84C22.71,17.95 22.75,18.13 22.66,18.29L21.26,20.71C21.17,20.86 21,20.92 20.83,20.86L19.09,20.16C18.73,20.44 18.33,20.67 17.91,20.85L17.64,22.7C17.62,22.87 17.47,23 17.3,23H14.5C14.32,23 14.18,22.87 14.15,22.7L13.89,20.85C13.46,20.67 13.07,20.44 12.71,20.16L10.96,20.86C10.81,20.92 10.62,20.86 10.54,20.71L9.14,18.29C9.05,18.13 9.09,17.95 9.22,17.84L10.7,16.68L10.65,16L10.7,15.31L9.22,14.16C9.09,14.05 9.05,13.86 9.14,13.71L10.54,11.29C10.62,11.13 10.81,11.07 10.96,11.13L12.71,11.84C13.07,11.56 13.46,11.32 13.89,11.15L14.15,9.29C14.18,9.13 14.32,9 14.5,9H17.3C17.47,9 17.62,9.13 17.64,9.29L17.91,11.15C18.33,11.32 18.73,11.56 19.09,11.84L20.83,11.13C21,11.07 21.17,11.13 21.26,11.29L22.66,13.71C22.75,13.86 22.71,14.05 22.58,14.16L21.1,15.31L21.15,16L21.1,16.68M6.69,8.07C7.56,8.07 8.26,7.37 8.26,6.5C8.26,5.63 7.56,4.92 6.69,4.92A1.58,1.58 0 0,0 5.11,6.5C5.11,7.37 5.82,8.07 6.69,8.07M10.03,6.94L11,7.68C11.07,7.75 11.09,7.87 11.03,7.97L10.13,9.53C10.08,9.63 9.96,9.67 9.86,9.63L8.74,9.18L8,9.62L7.81,10.81C7.79,10.92 7.7,11 7.59,11H5.79C5.67,11 5.58,10.92 5.56,10.81L5.4,9.62L4.64,9.18L3.5,9.63C3.41,9.67 3.3,9.63 3.24,9.53L2.34,7.97C2.28,7.87 2.31,7.75 2.39,7.68L3.34,6.94L3.31,6.5L3.34,6.06L2.39,5.32C2.31,5.25 2.28,5.13 2.34,5.03L3.24,3.47C3.3,3.37 3.41,3.33 3.5,3.37L4.63,3.82L5.4,3.38L5.56,2.19C5.58,2.08 5.67,2 5.79,2H7.59C7.7,2 7.79,2.08 7.81,2.19L8,3.38L8.74,3.82L9.86,3.37C9.96,3.33 10.08,3.37 10.13,3.47L11.03,5.03C11.09,5.13 11.07,5.25 11,5.32L10.03,6.06L10.06,6.5L10.03,6.94Z"},{translationKey:"addon.panel.log",path:`/hassio/addon/${this.addon.slug}/logs`,iconPath:"M18 7C16.9 7 16 7.9 16 9V15C16 16.1 16.9 17 18 17H20C21.1 17 22 16.1 22 15V11H20V15H18V9H22V7H18M2 7V17H8V15H4V7H2M11 7C9.9 7 9 7.9 9 9V15C9 16.1 9.9 17 11 17H13C14.1 17 15 16.1 15 15V9C15 7.9 14.1 7 13 7H11M11 9H13V15H11V9Z"});const t=this._computeTail(this.route);return i.dy`
      <hass-tabs-subpage
        .hass=${this.hass}
        .localizeFunc=${this.supervisor.localize}
        .narrow=${this.narrow}
        .route=${t}
        .tabs=${e}
        supervisor
      >
        <span slot="header">${this.addon.name}</span>
        <hassio-addon-router
          .route=${t}
          .narrow=${this.narrow}
          .hass=${this.hass}
          .supervisor=${this.supervisor}
          .addon=${this.addon}
        ></hassio-addon-router>
      </hass-tabs-subpage>
    `}},{kind:"get",static:!0,key:"styles",value:function(){return[h.Qx,p.l,i.iv`
        :host {
          color: var(--primary-text-color);
        }
        .content {
          padding: 24px 0 32px;
          display: flex;
          flex-direction: column;
          align-items: center;
        }
        hassio-addon-info,
        hassio-addon-network,
        hassio-addon-audio,
        hassio-addon-config {
          margin-bottom: 24px;
          width: 600px;
        }
        hassio-addon-logs {
          max-width: calc(100% - 8px);
          min-width: 600px;
        }
        @media only screen and (max-width: 600px) {
          hassio-addon-info,
          hassio-addon-network,
          hassio-addon-audio,
          hassio-addon-config,
          hassio-addon-logs {
            max-width: 100%;
            min-width: 100%;
          }
        }
      `]}},{kind:"method",key:"firstUpdated",value:async function(){if(""===this.route.path){const e=(0,d.io)("addon");if(e){const t=(await(0,l.yt)(this.hass)).addons.some((t=>t.slug===e));t?(0,a.c)(`/hassio/addon/${e}`,{replace:!0}):this._error=this.supervisor.localize("my.error_addon_not_found")}}this.addEventListener("hass-api-called",(e=>this._apiCalled(e)))}},{kind:"method",key:"_apiCalled",value:async function(e){var t;if(!e.detail.success)return;const r=null===(t=e.detail.path)||void 0===t?void 0:t.split("/");if(!r||0===r.length)return;const i=r[r.length-1];["uninstall","install","update","start","stop"].includes(i)&&(0,s.B)(this,"supervisor-collection-refresh",{collection:"supervisor"}),"uninstall"===i?window.history.back():await this._routeDataChanged()}},{kind:"method",key:"updated",value:function(e){e.has("route")&&!this.addon&&this._routeDataChanged()}},{kind:"method",key:"_routeDataChanged",value:async function(){const e=this.route.path.split("/")[1];if(e)try{const t=await(0,l.AD)(this.hass,e);this.addon=t}catch(e){this._error=`Error fetching addon info: ${(0,c.js)(e)}`,this.addon=void 0}}}]}}),i.oi)}}]);
//# sourceMappingURL=de92a12a.js.map