(self.webpackJsonp=self.webpackJsonp||[]).push([[4],{170:function(e,t,r){"use strict";r.r(t);r(40);var s=r(8),o=(r(71),r(0)),i=r(102);r(33);location.protocol,location.host;var n=r(68),a=r(11);function l(e){var t,r=u(e.key);"method"===e.kind?t={value:e.value,writable:!0,configurable:!0,enumerable:!1}:"get"===e.kind?t={get:e.value,configurable:!0,enumerable:!1}:"set"===e.kind?t={set:e.value,configurable:!0,enumerable:!1}:"field"===e.kind&&(t={configurable:!0,writable:!0,enumerable:!0});var s={kind:"field"===e.kind?"field":"method",key:r,placement:e.static?"static":"field"===e.kind?"own":"prototype",descriptor:t};return e.decorators&&(s.decorators=e.decorators),"field"===e.kind&&(s.initializer=e.value),s}function c(e,t){void 0!==e.descriptor.get?t.descriptor.get=e.descriptor.get:t.descriptor.set=e.descriptor.set}function d(e){return e.decorators&&e.decorators.length}function h(e){return void 0!==e&&!(void 0===e.value&&void 0===e.writable)}function p(e,t){var r=e[t];if(void 0!==r&&"function"!=typeof r)throw new TypeError("Expected '"+t+"' to be a function");return r}function u(e){var t=function(e,t){if("object"!=typeof e||null===e)return e;var r=e[Symbol.toPrimitive];if(void 0!==r){var s=r.call(e,t||"default");if("object"!=typeof s)return s;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===t?String:Number)(e)}(e,"string");return"symbol"==typeof t?t:String(t)}function f(e,t){(null==t||t>e.length)&&(t=e.length);for(var r=0,s=new Array(t);r<t;r++)s[r]=e[r];return s}!function(e,t,r,s){var o=function(){(function(){return e});var e={elementsDefinitionOrder:[["method"],["field"]],initializeInstanceElements:function(e,t){["method","field"].forEach((function(r){t.forEach((function(t){t.kind===r&&"own"===t.placement&&this.defineClassElement(e,t)}),this)}),this)},initializeClassElements:function(e,t){var r=e.prototype;["method","field"].forEach((function(s){t.forEach((function(t){var o=t.placement;if(t.kind===s&&("static"===o||"prototype"===o)){var i="static"===o?e:r;this.defineClassElement(i,t)}}),this)}),this)},defineClassElement:function(e,t){var r=t.descriptor;if("field"===t.kind){var s=t.initializer;r={enumerable:r.enumerable,writable:r.writable,configurable:r.configurable,value:void 0===s?void 0:s.call(e)}}Object.defineProperty(e,t.key,r)},decorateClass:function(e,t){var r=[],s=[],o={static:[],prototype:[],own:[]};if(e.forEach((function(e){this.addElementPlacement(e,o)}),this),e.forEach((function(e){if(!d(e))return r.push(e);var t=this.decorateElement(e,o);r.push(t.element),r.push.apply(r,t.extras),s.push.apply(s,t.finishers)}),this),!t)return{elements:r,finishers:s};var i=this.decorateConstructor(r,t);return s.push.apply(s,i.finishers),i.finishers=s,i},addElementPlacement:function(e,t,r){var s=t[e.placement];if(!r&&-1!==s.indexOf(e.key))throw new TypeError("Duplicated element ("+e.key+")");s.push(e.key)},decorateElement:function(e,t){for(var r=[],s=[],o=e.decorators,i=o.length-1;i>=0;i--){var n=t[e.placement];n.splice(n.indexOf(e.key),1);var a=this.fromElementDescriptor(e),l=this.toElementFinisherExtras((0,o[i])(a)||a);e=l.element,this.addElementPlacement(e,t),l.finisher&&s.push(l.finisher);var c=l.extras;if(c){for(var d=0;d<c.length;d++)this.addElementPlacement(c[d],t);r.push.apply(r,c)}}return{element:e,finishers:s,extras:r}},decorateConstructor:function(e,t){for(var r=[],s=t.length-1;s>=0;s--){var o=this.fromClassDescriptor(e),i=this.toClassDescriptor((0,t[s])(o)||o);if(void 0!==i.finisher&&r.push(i.finisher),void 0!==i.elements){e=i.elements;for(var n=0;n<e.length-1;n++)for(var a=n+1;a<e.length;a++)if(e[n].key===e[a].key&&e[n].placement===e[a].placement)throw new TypeError("Duplicated element ("+e[n].key+")")}}return{elements:e,finishers:r}},fromElementDescriptor:function(e){var t={kind:e.kind,key:e.key,placement:e.placement,descriptor:e.descriptor};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),"field"===e.kind&&(t.initializer=e.initializer),t},toElementDescriptors:function(e){var t;if(void 0!==e)return(t=e,function(e){if(Array.isArray(e))return e}(t)||function(e){if("undefined"!=typeof Symbol&&Symbol.iterator in Object(e))return Array.from(e)}(t)||function(e,t){if(e){if("string"==typeof e)return f(e,t);var r=Object.prototype.toString.call(e).slice(8,-1);return"Object"===r&&e.constructor&&(r=e.constructor.name),"Map"===r||"Set"===r?Array.from(r):"Arguments"===r||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(r)?f(e,t):void 0}}(t)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()).map((function(e){var t=this.toElementDescriptor(e);return this.disallowProperty(e,"finisher","An element descriptor"),this.disallowProperty(e,"extras","An element descriptor"),t}),this)},toElementDescriptor:function(e){var t=String(e.kind);if("method"!==t&&"field"!==t)throw new TypeError('An element descriptor\'s .kind property must be either "method" or "field", but a decorator created an element descriptor with .kind "'+t+'"');var r=u(e.key),s=String(e.placement);if("static"!==s&&"prototype"!==s&&"own"!==s)throw new TypeError('An element descriptor\'s .placement property must be one of "static", "prototype" or "own", but a decorator created an element descriptor with .placement "'+s+'"');var o=e.descriptor;this.disallowProperty(e,"elements","An element descriptor");var i={kind:t,key:r,placement:s,descriptor:Object.assign({},o)};return"field"!==t?this.disallowProperty(e,"initializer","A method descriptor"):(this.disallowProperty(o,"get","The property descriptor of a field descriptor"),this.disallowProperty(o,"set","The property descriptor of a field descriptor"),this.disallowProperty(o,"value","The property descriptor of a field descriptor"),i.initializer=e.initializer),i},toElementFinisherExtras:function(e){return{element:this.toElementDescriptor(e),finisher:p(e,"finisher"),extras:this.toElementDescriptors(e.extras)}},fromClassDescriptor:function(e){var t={kind:"class",elements:e.map(this.fromElementDescriptor,this)};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),t},toClassDescriptor:function(e){var t=String(e.kind);if("class"!==t)throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator created a class descriptor with .kind "'+t+'"');this.disallowProperty(e,"key","A class descriptor"),this.disallowProperty(e,"placement","A class descriptor"),this.disallowProperty(e,"descriptor","A class descriptor"),this.disallowProperty(e,"initializer","A class descriptor"),this.disallowProperty(e,"extras","A class descriptor");var r=p(e,"finisher");return{elements:this.toElementDescriptors(e.elements),finisher:r}},runClassFinishers:function(e,t){for(var r=0;r<t.length;r++){var s=(0,t[r])(e);if(void 0!==s){if("function"!=typeof s)throw new TypeError("Finishers must return a constructor.");e=s}}return e},disallowProperty:function(e,t,r){if(void 0!==e[t])throw new TypeError(r+" can't have a ."+t+" property.")}};return e}();if(s)for(var i=0;i<s.length;i++)o=s[i](o);var n=t((function(e){o.initializeInstanceElements(e,a.elements)}),r),a=o.decorateClass(function(e){for(var t=[],r=function(e){return"method"===e.kind&&e.key===i.key&&e.placement===i.placement},s=0;s<e.length;s++){var o,i=e[s];if("method"===i.kind&&(o=t.find(r)))if(h(i.descriptor)||h(o.descriptor)){if(d(i)||d(o))throw new ReferenceError("Duplicated methods ("+i.key+") can't be decorated.");o.descriptor=i.descriptor}else{if(d(i)){if(d(o))throw new ReferenceError("Decorators can't be placed on different accessors with for the same property ("+i.key+").");o.decorators=i.decorators}c(i,o)}else t.push(i)}return t}(n.d.map(l)),e);o.initializeClassElements(n.F,a.elements),o.runClassFinishers(n.F,a.finishers)}([Object(o.d)("dialog-hassio-snapshot")],(function(e,t){return{F:class extends t{constructor(...t){super(...t),e(this)}},d:[{kind:"field",decorators:[Object(o.h)()],key:"hass",value:void 0},{kind:"field",decorators:[Object(o.h)()],key:"_error",value:void 0},{kind:"field",decorators:[Object(o.h)()],key:"_snapshot",value:void 0},{kind:"field",decorators:[Object(o.h)()],key:"_folders",value:void 0},{kind:"field",decorators:[Object(o.h)()],key:"_addons",value:void 0},{kind:"field",decorators:[Object(o.h)()],key:"_dialogParams",value:void 0},{kind:"field",decorators:[Object(o.h)()],key:"_snapshotPassword",value:void 0},{kind:"field",decorators:[Object(o.h)()],key:"_restoreHass",value:()=>!0},{kind:"method",key:"showDialog",value:async function(e){var t;this._snapshot=await Object(n.c)(this.hass,e.slug),this._folders=(e=>{const t=[];return e.includes("homeassistant")&&t.push({slug:"homeassistant",name:"Home Assistant configuration",checked:!0}),e.includes("ssl")&&t.push({slug:"ssl",name:"SSL",checked:!0}),e.includes("share")&&t.push({slug:"share",name:"Share",checked:!0}),e.includes("addons/local")&&t.push({slug:"addons/local",name:"Local add-ons",checked:!0}),t})(this._snapshot.folders).sort((e,t)=>e.name>t.name?1:-1),this._addons=(t=this._snapshot.addons,t.map(e=>({slug:e.slug,name:e.name,version:e.version,checked:!0}))).sort((e,t)=>e.name>t.name?1:-1),this._dialogParams=e}},{kind:"method",key:"render",value:function(){return this._dialogParams&&this._snapshot?o.f`
      <ha-dialog
        open
        stacked
        @closing=${this._closeDialog}
        .heading=${Object(i.a)(this.hass,this._computeName)}
      >
        <div class="details">
          ${"full"===this._snapshot.type?"Full snapshot":"Partial snapshot"}
          (${this._computeSize})<br />
          ${this._formatDatetime(this._snapshot.date)}
        </div>
        <div>Home Assistant:</div>
        <paper-checkbox
          .checked=${this._restoreHass}
          @change="${e=>{this._restoreHass=e.target.checked}}"
        >
          Home Assistant ${this._snapshot.homeassistant}
        </paper-checkbox>
        ${this._folders.length?o.f`
              <div>Folders:</div>
              <paper-dialog-scrollable class="no-margin-top">
                ${this._folders.map(e=>o.f`
                    <paper-checkbox
                      .checked=${e.checked}
                      @change="${t=>this._updateFolders(e,t.target.checked)}"
                    >
                      ${e.name}
                    </paper-checkbox>
                  `)}
              </paper-dialog-scrollable>
            `:""}
        ${this._addons.length?o.f`
              <div>Add-on:</div>
              <paper-dialog-scrollable class="no-margin-top">
                ${this._addons.map(e=>o.f`
                    <paper-checkbox
                      .checked=${e.checked}
                      @change="${t=>this._updateAddons(e,t.target.checked)}"
                    >
                      ${e.name}
                    </paper-checkbox>
                  `)}
              </paper-dialog-scrollable>
            `:""}
        ${this._snapshot.protected?o.f`
              <paper-input
                autofocus=""
                label="Password"
                type="password"
                @value-changed=${this._passwordInput}
                .value=${this._snapshotPassword}
              ></paper-input>
            `:""}
        ${this._error?o.f` <p class="error">Error: ${this._error}</p> `:""}

        <div>Actions:</div>

        <mwc-button @click=${this._downloadClicked} slot="primaryAction">
          <ha-svg-icon path=${s.n} class="icon"></ha-svg-icon>
          Download Snapshot
        </mwc-button>

        <mwc-button
          @click=${this._partialRestoreClicked}
          slot="secondaryAction"
        >
          <ha-svg-icon path=${s.s} class="icon"></ha-svg-icon>
          Restore Selected
        </mwc-button>
        ${"full"===this._snapshot.type?o.f`
              <mwc-button
                @click=${this._fullRestoreClicked}
                slot="secondaryAction"
              >
                <ha-svg-icon path=${s.s} class="icon"></ha-svg-icon>
                Wipe &amp; restore
              </mwc-button>
            `:""}
        <mwc-button @click=${this._deleteClicked} slot="secondaryAction">
          <ha-svg-icon path=${s.k} class="icon warning"></ha-svg-icon>
          <span class="warning">Delete Snapshot</span>
        </mwc-button>
      </ha-dialog>
    `:o.f``}},{kind:"get",static:!0,key:"styles",value:function(){return[a.c,o.c`
        paper-checkbox {
          display: block;
          margin: 4px;
        }
        .details {
          color: var(--secondary-text-color);
        }
        .warning,
        .error {
          color: var(--error-color);
        }
        .buttons {
          display: flex;
          flex-direction: column;
        }
        .buttons li {
          list-style-type: none;
        }
        .buttons .icon {
          margin-right: 16px;
        }
        .no-margin-top {
          margin-top: 0;
        }
      `]}},{kind:"method",key:"_updateFolders",value:function(e,t){this._folders=this._folders.map(r=>(r.slug===e.slug&&(r.checked=t),r))}},{kind:"method",key:"_updateAddons",value:function(e,t){this._addons=this._addons.map(r=>(r.slug===e.slug&&(r.checked=t),r))}},{kind:"method",key:"_passwordInput",value:function(e){this._snapshotPassword=e.detail.value}},{kind:"method",key:"_partialRestoreClicked",value:function(){if(!confirm("Are you sure you want to restore this snapshot?"))return;const e=this._addons.filter(e=>e.checked).map(e=>e.slug),t=this._folders.filter(e=>e.checked).map(e=>e.slug),r={homeassistant:this._restoreHass,addons:e,folders:t};this._snapshot.protected&&(r.password=this._snapshotPassword),this.hass.callApi("POST",`hassio/snapshots/${this._snapshot.slug}/restore/partial`,r).then(()=>{alert("Snapshot restored!"),this._closeDialog()},e=>{this._error=e.body.message})}},{kind:"method",key:"_fullRestoreClicked",value:function(){if(!confirm("Are you sure you want to restore this snapshot?"))return;const e=this._snapshot.protected?{password:this._snapshotPassword}:void 0;this.hass.callApi("POST",`hassio/snapshots/${this._snapshot.slug}/restore/full`,e).then(()=>{alert("Snapshot restored!"),this._closeDialog()},e=>{this._error=e.body.message})}},{kind:"method",key:"_deleteClicked",value:function(){confirm("Are you sure you want to delete this snapshot?")&&this.hass.callApi("POST",`hassio/snapshots/${this._snapshot.slug}/remove`).then(()=>{this._dialogParams.onDelete(),this._closeDialog()},e=>{this._error=e.body.message})}},{kind:"method",key:"_downloadClicked",value:async function(){let e;try{e=await(t=this.hass,r=`/api/hassio/snapshots/${this._snapshot.slug}/download`,t.callWS({type:"auth/sign_path",path:r}))}catch(i){return void alert("Error: "+i.message)}var t,r;const s=this._computeName.replace(/[^a-z0-9]+/gi,"_"),o=document.createElement("a");o.href=e.path,o.download=`Hass_io_${s}.tar`,this.shadowRoot.appendChild(o),o.click(),this.shadowRoot.removeChild(o)}},{kind:"get",key:"_computeName",value:function(){return this._snapshot?this._snapshot.name||this._snapshot.slug:"Unnamed snapshot"}},{kind:"get",key:"_computeSize",value:function(){return Math.ceil(10*this._snapshot.size)/10+" MB"}},{kind:"method",key:"_formatDatetime",value:function(e){return new Date(e).toLocaleDateString(navigator.language,{weekday:"long",year:"numeric",month:"short",day:"numeric",hour:"numeric",minute:"2-digit"})}},{kind:"method",key:"_closeDialog",value:function(){this._dialogParams=void 0,this._snapshot=void 0,this._snapshotPassword="",this._folders=[],this._addons=[]}}]}}),o.a)}}]);
//# sourceMappingURL=chunk.c4f509fa93d486e491cf.js.map