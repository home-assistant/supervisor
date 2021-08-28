(self.webpackChunkhome_assistant_frontend=self.webpackChunkhome_assistant_frontend||[]).push([[511],{6511:(e,t,r)=>{"use strict";r.r(t);r(9579);var i=r(424),o=r(5358),a=r(7181),n=(r(9381),r(4552),r(9725),r(4089),r(2039),r(7315),r(1682)),s=r(538),l=r(1654);function c(){c=function(){return e};var e={elementsDefinitionOrder:[["method"],["field"]],initializeInstanceElements:function(e,t){["method","field"].forEach((function(r){t.forEach((function(t){t.kind===r&&"own"===t.placement&&this.defineClassElement(e,t)}),this)}),this)},initializeClassElements:function(e,t){var r=e.prototype;["method","field"].forEach((function(i){t.forEach((function(t){var o=t.placement;if(t.kind===i&&("static"===o||"prototype"===o)){var a="static"===o?e:r;this.defineClassElement(a,t)}}),this)}),this)},defineClassElement:function(e,t){var r=t.descriptor;if("field"===t.kind){var i=t.initializer;r={enumerable:r.enumerable,writable:r.writable,configurable:r.configurable,value:void 0===i?void 0:i.call(e)}}Object.defineProperty(e,t.key,r)},decorateClass:function(e,t){var r=[],i=[],o={static:[],prototype:[],own:[]};if(e.forEach((function(e){this.addElementPlacement(e,o)}),this),e.forEach((function(e){if(!u(e))return r.push(e);var t=this.decorateElement(e,o);r.push(t.element),r.push.apply(r,t.extras),i.push.apply(i,t.finishers)}),this),!t)return{elements:r,finishers:i};var a=this.decorateConstructor(r,t);return i.push.apply(i,a.finishers),a.finishers=i,a},addElementPlacement:function(e,t,r){var i=t[e.placement];if(!r&&-1!==i.indexOf(e.key))throw new TypeError("Duplicated element ("+e.key+")");i.push(e.key)},decorateElement:function(e,t){for(var r=[],i=[],o=e.decorators,a=o.length-1;a>=0;a--){var n=t[e.placement];n.splice(n.indexOf(e.key),1);var s=this.fromElementDescriptor(e),l=this.toElementFinisherExtras((0,o[a])(s)||s);e=l.element,this.addElementPlacement(e,t),l.finisher&&i.push(l.finisher);var c=l.extras;if(c){for(var d=0;d<c.length;d++)this.addElementPlacement(c[d],t);r.push.apply(r,c)}}return{element:e,finishers:i,extras:r}},decorateConstructor:function(e,t){for(var r=[],i=t.length-1;i>=0;i--){var o=this.fromClassDescriptor(e),a=this.toClassDescriptor((0,t[i])(o)||o);if(void 0!==a.finisher&&r.push(a.finisher),void 0!==a.elements){e=a.elements;for(var n=0;n<e.length-1;n++)for(var s=n+1;s<e.length;s++)if(e[n].key===e[s].key&&e[n].placement===e[s].placement)throw new TypeError("Duplicated element ("+e[n].key+")")}}return{elements:e,finishers:r}},fromElementDescriptor:function(e){var t={kind:e.kind,key:e.key,placement:e.placement,descriptor:e.descriptor};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),"field"===e.kind&&(t.initializer=e.initializer),t},toElementDescriptors:function(e){var t;if(void 0!==e)return(t=e,function(e){if(Array.isArray(e))return e}(t)||function(e){if("undefined"!=typeof Symbol&&null!=e[Symbol.iterator]||null!=e["@@iterator"])return Array.from(e)}(t)||function(e,t){if(e){if("string"==typeof e)return v(e,t);var r=Object.prototype.toString.call(e).slice(8,-1);return"Object"===r&&e.constructor&&(r=e.constructor.name),"Map"===r||"Set"===r?Array.from(e):"Arguments"===r||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(r)?v(e,t):void 0}}(t)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()).map((function(e){var t=this.toElementDescriptor(e);return this.disallowProperty(e,"finisher","An element descriptor"),this.disallowProperty(e,"extras","An element descriptor"),t}),this)},toElementDescriptor:function(e){var t=String(e.kind);if("method"!==t&&"field"!==t)throw new TypeError('An element descriptor\'s .kind property must be either "method" or "field", but a decorator created an element descriptor with .kind "'+t+'"');var r=m(e.key),i=String(e.placement);if("static"!==i&&"prototype"!==i&&"own"!==i)throw new TypeError('An element descriptor\'s .placement property must be one of "static", "prototype" or "own", but a decorator created an element descriptor with .placement "'+i+'"');var o=e.descriptor;this.disallowProperty(e,"elements","An element descriptor");var a={kind:t,key:r,placement:i,descriptor:Object.assign({},o)};return"field"!==t?this.disallowProperty(e,"initializer","A method descriptor"):(this.disallowProperty(o,"get","The property descriptor of a field descriptor"),this.disallowProperty(o,"set","The property descriptor of a field descriptor"),this.disallowProperty(o,"value","The property descriptor of a field descriptor"),a.initializer=e.initializer),a},toElementFinisherExtras:function(e){return{element:this.toElementDescriptor(e),finisher:f(e,"finisher"),extras:this.toElementDescriptors(e.extras)}},fromClassDescriptor:function(e){var t={kind:"class",elements:e.map(this.fromElementDescriptor,this)};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),t},toClassDescriptor:function(e){var t=String(e.kind);if("class"!==t)throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator created a class descriptor with .kind "'+t+'"');this.disallowProperty(e,"key","A class descriptor"),this.disallowProperty(e,"placement","A class descriptor"),this.disallowProperty(e,"descriptor","A class descriptor"),this.disallowProperty(e,"initializer","A class descriptor"),this.disallowProperty(e,"extras","A class descriptor");var r=f(e,"finisher");return{elements:this.toElementDescriptors(e.elements),finisher:r}},runClassFinishers:function(e,t){for(var r=0;r<t.length;r++){var i=(0,t[r])(e);if(void 0!==i){if("function"!=typeof i)throw new TypeError("Finishers must return a constructor.");e=i}}return e},disallowProperty:function(e,t,r){if(void 0!==e[t])throw new TypeError(r+" can't have a ."+t+" property.")}};return e}function d(e){var t,r=m(e.key);"method"===e.kind?t={value:e.value,writable:!0,configurable:!0,enumerable:!1}:"get"===e.kind?t={get:e.value,configurable:!0,enumerable:!1}:"set"===e.kind?t={set:e.value,configurable:!0,enumerable:!1}:"field"===e.kind&&(t={configurable:!0,writable:!0,enumerable:!0});var i={kind:"field"===e.kind?"field":"method",key:r,placement:e.static?"static":"field"===e.kind?"own":"prototype",descriptor:t};return e.decorators&&(i.decorators=e.decorators),"field"===e.kind&&(i.initializer=e.value),i}function p(e,t){void 0!==e.descriptor.get?t.descriptor.get=e.descriptor.get:t.descriptor.set=e.descriptor.set}function u(e){return e.decorators&&e.decorators.length}function h(e){return void 0!==e&&!(void 0===e.value&&void 0===e.writable)}function f(e,t){var r=e[t];if(void 0!==r&&"function"!=typeof r)throw new TypeError("Expected '"+t+"' to be a function");return r}function m(e){var t=function(e,t){if("object"!=typeof e||null===e)return e;var r=e[Symbol.toPrimitive];if(void 0!==r){var i=r.call(e,t||"default");if("object"!=typeof i)return i;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===t?String:Number)(e)}(e,"string");return"symbol"==typeof t?t:String(t)}function v(e,t){(null==t||t>e.length)&&(t=e.length);for(var r=0,i=new Array(t);r<t;r++)i[r]=e[r];return i}!function(e,t,r,i){var o=c();if(i)for(var a=0;a<i.length;a++)o=i[a](o);var n=t((function(e){o.initializeInstanceElements(e,s.elements)}),r),s=o.decorateClass(function(e){for(var t=[],r=function(e){return"method"===e.kind&&e.key===a.key&&e.placement===a.placement},i=0;i<e.length;i++){var o,a=e[i];if("method"===a.kind&&(o=t.find(r)))if(h(a.descriptor)||h(o.descriptor)){if(u(a)||u(o))throw new ReferenceError("Duplicated methods ("+a.key+") can't be decorated.");o.descriptor=a.descriptor}else{if(u(a)){if(u(o))throw new ReferenceError("Decorators can't be placed on different accessors with for the same property ("+a.key+").");o.decorators=a.decorators}p(a,o)}else t.push(a)}return t}(n.d.map(d)),e);o.initializeClassElements(n.F,s.elements),o.runClassFinishers(n.F,s.finishers)}([(0,o.Mo)("dialog-supervisor-update")],(function(e,t){return{F:class extends t{constructor(...t){super(...t),e(this)}},d:[{kind:"field",key:"hass",value:void 0},{kind:"field",decorators:[(0,o.SB)()],key:"_opened",value:()=>!1},{kind:"field",decorators:[(0,o.SB)()],key:"_createBackup",value:()=>!0},{kind:"field",decorators:[(0,o.SB)()],key:"_action",value:()=>null},{kind:"field",decorators:[(0,o.SB)()],key:"_error",value:void 0},{kind:"field",decorators:[(0,o.SB)()],key:"_dialogParams",value:void 0},{kind:"method",key:"showDialog",value:async function(e){this._opened=!0,this._dialogParams=e,await this.updateComplete}},{kind:"method",key:"closeDialog",value:function(){this._action=null,this._createBackup=!0,this._error=void 0,this._dialogParams=void 0,(0,a.B)(this,"dialog-closed",{dialog:this.localName})}},{kind:"method",key:"focus",value:function(){this.updateComplete.then((()=>{var e,t;return null===(e=this.shadowRoot)||void 0===e||null===(t=e.querySelector("[dialogInitialFocus]"))||void 0===t?void 0:t.focus()}))}},{kind:"method",key:"render",value:function(){return this._dialogParams?i.dy`
      <ha-dialog .open=${this._opened} scrimClickAction escapeKeyAction>
        ${null===this._action?i.dy`<slot name="heading">
                <h2 id="title" class="header_title">
                  ${this._dialogParams.supervisor.localize("confirm.update.title","name",this._dialogParams.name)}
                </h2>
              </slot>
              <div>
                ${this._dialogParams.supervisor.localize("confirm.update.text","name",this._dialogParams.name,"version",this._dialogParams.version)}
              </div>

              <ha-settings-row>
                <span slot="heading">
                  ${this._dialogParams.supervisor.localize("dialog.update.backup")}
                </span>
                <span slot="description">
                  ${this._dialogParams.supervisor.localize("dialog.update.create_backup","name",this._dialogParams.name)}
                </span>
                <ha-switch
                  .checked=${this._createBackup}
                  haptic
                  @click=${this._toggleBackup}
                >
                </ha-switch>
              </ha-settings-row>
              <mwc-button @click=${this.closeDialog} slot="secondaryAction">
                ${this._dialogParams.supervisor.localize("common.cancel")}
              </mwc-button>
              <mwc-button
                .disabled=${void 0!==this._error}
                @click=${this._update}
                slot="primaryAction"
              >
                ${this._dialogParams.supervisor.localize("common.update")}
              </mwc-button>`:i.dy`<ha-circular-progress alt="Updating" size="large" active>
              </ha-circular-progress>
              <p class="progress-text">
                ${"update"===this._action?this._dialogParams.supervisor.localize("dialog.update.updating","name",this._dialogParams.name,"version",this._dialogParams.version):this._dialogParams.supervisor.localize("dialog.update.creating_backup","name",this._dialogParams.name)}
              </p>`}
        ${this._error?i.dy`<ha-alert alert-type="error">${this._error}</ha-alert>`:""}
      </ha-dialog>
    `:i.dy``}},{kind:"method",key:"_toggleBackup",value:function(){this._createBackup=!this._createBackup}},{kind:"method",key:"_update",value:async function(){if(this._createBackup){this._action="backup";try{await(0,s.zU)(this.hass,this._dialogParams.backupParams)}catch(e){return this._error=(0,n.js)(e),void(this._action=null)}}this._action="update";try{await this._dialogParams.updateHandler()}catch(e){return void(this.hass.connection.connected&&!(0,n.yz)(e)&&(this._error=(0,n.js)(e),this._action=null))}this.closeDialog()}},{kind:"get",static:!0,key:"styles",value:function(){return[l.Qx,l.yu,i.iv`
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
//# sourceMappingURL=9c14d8f0.js.map