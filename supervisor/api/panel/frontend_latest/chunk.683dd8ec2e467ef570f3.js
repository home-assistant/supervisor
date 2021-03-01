(self.webpackChunkhome_assistant_frontend=self.webpackChunkhome_assistant_frontend||[]).push([[310],{2310:(e,t,r)=>{"use strict";r.r(t);r(573);var i=r(9722),n=r(7181),o=(r(5602),r(2923),r(4089),r(2039),r(9602),r(4154)),s=r(1682),a=r(7097),l=r(1654);function c(){c=function(){return e};var e={elementsDefinitionOrder:[["method"],["field"]],initializeInstanceElements:function(e,t){["method","field"].forEach((function(r){t.forEach((function(t){t.kind===r&&"own"===t.placement&&this.defineClassElement(e,t)}),this)}),this)},initializeClassElements:function(e,t){var r=e.prototype;["method","field"].forEach((function(i){t.forEach((function(t){var n=t.placement;if(t.kind===i&&("static"===n||"prototype"===n)){var o="static"===n?e:r;this.defineClassElement(o,t)}}),this)}),this)},defineClassElement:function(e,t){var r=t.descriptor;if("field"===t.kind){var i=t.initializer;r={enumerable:r.enumerable,writable:r.writable,configurable:r.configurable,value:void 0===i?void 0:i.call(e)}}Object.defineProperty(e,t.key,r)},decorateClass:function(e,t){var r=[],i=[],n={static:[],prototype:[],own:[]};if(e.forEach((function(e){this.addElementPlacement(e,n)}),this),e.forEach((function(e){if(!h(e))return r.push(e);var t=this.decorateElement(e,n);r.push(t.element),r.push.apply(r,t.extras),i.push.apply(i,t.finishers)}),this),!t)return{elements:r,finishers:i};var o=this.decorateConstructor(r,t);return i.push.apply(i,o.finishers),o.finishers=i,o},addElementPlacement:function(e,t,r){var i=t[e.placement];if(!r&&-1!==i.indexOf(e.key))throw new TypeError("Duplicated element ("+e.key+")");i.push(e.key)},decorateElement:function(e,t){for(var r=[],i=[],n=e.decorators,o=n.length-1;o>=0;o--){var s=t[e.placement];s.splice(s.indexOf(e.key),1);var a=this.fromElementDescriptor(e),l=this.toElementFinisherExtras((0,n[o])(a)||a);e=l.element,this.addElementPlacement(e,t),l.finisher&&i.push(l.finisher);var c=l.extras;if(c){for(var d=0;d<c.length;d++)this.addElementPlacement(c[d],t);r.push.apply(r,c)}}return{element:e,finishers:i,extras:r}},decorateConstructor:function(e,t){for(var r=[],i=t.length-1;i>=0;i--){var n=this.fromClassDescriptor(e),o=this.toClassDescriptor((0,t[i])(n)||n);if(void 0!==o.finisher&&r.push(o.finisher),void 0!==o.elements){e=o.elements;for(var s=0;s<e.length-1;s++)for(var a=s+1;a<e.length;a++)if(e[s].key===e[a].key&&e[s].placement===e[a].placement)throw new TypeError("Duplicated element ("+e[s].key+")")}}return{elements:e,finishers:r}},fromElementDescriptor:function(e){var t={kind:e.kind,key:e.key,placement:e.placement,descriptor:e.descriptor};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),"field"===e.kind&&(t.initializer=e.initializer),t},toElementDescriptors:function(e){var t;if(void 0!==e)return(t=e,function(e){if(Array.isArray(e))return e}(t)||function(e){if("undefined"!=typeof Symbol&&Symbol.iterator in Object(e))return Array.from(e)}(t)||function(e,t){if(e){if("string"==typeof e)return y(e,t);var r=Object.prototype.toString.call(e).slice(8,-1);return"Object"===r&&e.constructor&&(r=e.constructor.name),"Map"===r||"Set"===r?Array.from(e):"Arguments"===r||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(r)?y(e,t):void 0}}(t)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()).map((function(e){var t=this.toElementDescriptor(e);return this.disallowProperty(e,"finisher","An element descriptor"),this.disallowProperty(e,"extras","An element descriptor"),t}),this)},toElementDescriptor:function(e){var t=String(e.kind);if("method"!==t&&"field"!==t)throw new TypeError('An element descriptor\'s .kind property must be either "method" or "field", but a decorator created an element descriptor with .kind "'+t+'"');var r=m(e.key),i=String(e.placement);if("static"!==i&&"prototype"!==i&&"own"!==i)throw new TypeError('An element descriptor\'s .placement property must be one of "static", "prototype" or "own", but a decorator created an element descriptor with .placement "'+i+'"');var n=e.descriptor;this.disallowProperty(e,"elements","An element descriptor");var o={kind:t,key:r,placement:i,descriptor:Object.assign({},n)};return"field"!==t?this.disallowProperty(e,"initializer","A method descriptor"):(this.disallowProperty(n,"get","The property descriptor of a field descriptor"),this.disallowProperty(n,"set","The property descriptor of a field descriptor"),this.disallowProperty(n,"value","The property descriptor of a field descriptor"),o.initializer=e.initializer),o},toElementFinisherExtras:function(e){return{element:this.toElementDescriptor(e),finisher:f(e,"finisher"),extras:this.toElementDescriptors(e.extras)}},fromClassDescriptor:function(e){var t={kind:"class",elements:e.map(this.fromElementDescriptor,this)};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),t},toClassDescriptor:function(e){var t=String(e.kind);if("class"!==t)throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator created a class descriptor with .kind "'+t+'"');this.disallowProperty(e,"key","A class descriptor"),this.disallowProperty(e,"placement","A class descriptor"),this.disallowProperty(e,"descriptor","A class descriptor"),this.disallowProperty(e,"initializer","A class descriptor"),this.disallowProperty(e,"extras","A class descriptor");var r=f(e,"finisher");return{elements:this.toElementDescriptors(e.elements),finisher:r}},runClassFinishers:function(e,t){for(var r=0;r<t.length;r++){var i=(0,t[r])(e);if(void 0!==i){if("function"!=typeof i)throw new TypeError("Finishers must return a constructor.");e=i}}return e},disallowProperty:function(e,t,r){if(void 0!==e[t])throw new TypeError(r+" can't have a ."+t+" property.")}};return e}function d(e){var t,r=m(e.key);"method"===e.kind?t={value:e.value,writable:!0,configurable:!0,enumerable:!1}:"get"===e.kind?t={get:e.value,configurable:!0,enumerable:!1}:"set"===e.kind?t={set:e.value,configurable:!0,enumerable:!1}:"field"===e.kind&&(t={configurable:!0,writable:!0,enumerable:!0});var i={kind:"field"===e.kind?"field":"method",key:r,placement:e.static?"static":"field"===e.kind?"own":"prototype",descriptor:t};return e.decorators&&(i.decorators=e.decorators),"field"===e.kind&&(i.initializer=e.value),i}function p(e,t){void 0!==e.descriptor.get?t.descriptor.get=e.descriptor.get:t.descriptor.set=e.descriptor.set}function h(e){return e.decorators&&e.decorators.length}function u(e){return void 0!==e&&!(void 0===e.value&&void 0===e.writable)}function f(e,t){var r=e[t];if(void 0!==r&&"function"!=typeof r)throw new TypeError("Expected '"+t+"' to be a function");return r}function m(e){var t=function(e,t){if("object"!=typeof e||null===e)return e;var r=e[Symbol.toPrimitive];if(void 0!==r){var i=r.call(e,t||"default");if("object"!=typeof i)return i;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===t?String:Number)(e)}(e,"string");return"symbol"==typeof t?t:String(t)}function y(e,t){(null==t||t>e.length)&&(t=e.length);for(var r=0,i=new Array(t);r<t;r++)i[r]=e[r];return i}!function(e,t,r,i){var n=c();if(i)for(var o=0;o<i.length;o++)n=i[o](n);var s=t((function(e){n.initializeInstanceElements(e,a.elements)}),r),a=n.decorateClass(function(e){for(var t=[],r=function(e){return"method"===e.kind&&e.key===o.key&&e.placement===o.placement},i=0;i<e.length;i++){var n,o=e[i];if("method"===o.kind&&(n=t.find(r)))if(u(o.descriptor)||u(n.descriptor)){if(h(o)||h(n))throw new ReferenceError("Duplicated methods ("+o.key+") can't be decorated.");n.descriptor=o.descriptor}else{if(h(o)){if(h(n))throw new ReferenceError("Decorators can't be placed on different accessors with for the same property ("+o.key+").");n.decorators=o.decorators}p(o,n)}else t.push(o)}return t}(s.d.map(d)),e);n.initializeClassElements(s.F,a.elements),n.runClassFinishers(s.F,a.finishers)}([(0,i.Mo)("dialog-supervisor-addon-update")],(function(e,t){return{F:class extends t{constructor(...t){super(...t),e(this)}},d:[{kind:"field",key:"hass",value:void 0},{kind:"field",key:"addon",value:void 0},{kind:"field",decorators:[(0,i.sz)()],key:"_opened",value:()=>!1},{kind:"field",decorators:[(0,i.sz)()],key:"_createSnapshot",value:()=>!0},{kind:"field",decorators:[(0,i.sz)()],key:"_action",value:()=>null},{kind:"field",decorators:[(0,i.sz)()],key:"_error",value:void 0},{kind:"method",key:"showDialog",value:async function(e){this._opened=!0,this.addon=e.addon,await this.updateComplete}},{kind:"method",key:"closeDialog",value:function(){this._action=null,this._createSnapshot=!0,this._opened=!1,(0,n.B)(this,"dialog-closed",{dialog:this.localName})}},{kind:"method",key:"focus",value:function(){this.updateComplete.then((()=>{var e,t;return null===(e=this.shadowRoot)||void 0===e||null===(t=e.querySelector("[dialogInitialFocus]"))||void 0===t?void 0:t.focus()}))}},{kind:"method",key:"render",value:function(){return i.dy`
      <ha-dialog .open=${this._opened} scrimClickAction escapeKeyAction>
        ${null===this._action?i.dy`<slot name="heading">
                <h2 id="title" class="header_title">
                  Update ${this.addon.name}
                </h2>
              </slot>
              <div>
                Are you sure you want to update the ${this.addon.name} add-on to
                version ${this.addon.version_latest}?
              </div>

              <ha-settings-row>
                <span slot="heading">
                  Snapshot
                </span>
                <span slot="description">
                  Create a snapshot of the ${this.addon.name} add-on before
                  updating
                </span>
                <ha-switch
                  .checked=${this._createSnapshot}
                  haptic
                  title="Create snapshot"
                  @click=${this._toggleSnapshot}
                >
                </ha-switch>
              </ha-settings-row>
              <mwc-button @click=${this.closeDialog} slot="secondaryAction">
                Cancel
              </mwc-button>
              <mwc-button @click=${this._update} slot="primaryAction">
                Update
              </mwc-button>`:i.dy`<ha-circular-progress alt="Updating" size="large" active>
              </ha-circular-progress>
              <p class="progress-text">
                ${"update"===this._action?`Updating ${this.addon.name} to version ${this.addon.version_latest}`:"Creating snapshot of Home Assistant Core"}
              </p>`}
        ${this._error?i.dy`<p class="error">${this._error}</p>`:""}
      </ha-dialog>
    `}},{kind:"method",key:"_toggleSnapshot",value:function(){this._createSnapshot=!this._createSnapshot}},{kind:"method",key:"_update",value:async function(){if(this._createSnapshot){this._action="snapshot";try{await(0,a.iN)(this.hass,{name:`addon_${this.addon.slug}_${this.addon.version}`,addons:[this.addon.slug],homeassistant:!1})}catch(e){return this._error=(0,s.js)(e),void(this._action=null)}}this._action="update";try{await(0,o.V_)(this.hass,this.addon.slug)}catch(e){return this._error=(0,s.js)(e),void(this._action=null)}(0,n.B)(this,"supervisor-colllection-refresh",{colllection:"addon"}),(0,n.B)(this,"supervisor-colllection-refresh",{colllection:"supervisor"}),this.closeDialog()}},{kind:"get",static:!0,key:"styles",value:function(){return[l.Qx,l.yu,i.iv`
        .form {
          color: var(--primary-text-color);
        }

        ha-settings-row {
          margin-top: 32px;
          padding: 0;
        }

        ha-circular-progress {
          display: block;
          margin: 32px;
          text-align: center;
        }

        .progress-text {
          text-align: center;
        }
      `]}}]}}),i.oi)}}]);
//# sourceMappingURL=chunk.683dd8ec2e467ef570f3.js.map