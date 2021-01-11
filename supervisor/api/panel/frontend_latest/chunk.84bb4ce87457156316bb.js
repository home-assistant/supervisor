(self.webpackChunkhome_assistant_frontend=self.webpackChunkhome_assistant_frontend||[]).push([[530],{7930:(e,t,s)=>{"use strict";s.r(t);s(573);var r=s(5317),i=(s(2296),s(7956),s(9722)),o=s(7181);s(3221),s(2039);location.protocol,location.host;var a=s(1682),n=s(7097),l=s(6765),d=s(1654);function c(){c=function(){return e};var e={elementsDefinitionOrder:[["method"],["field"]],initializeInstanceElements:function(e,t){["method","field"].forEach((function(s){t.forEach((function(t){t.kind===s&&"own"===t.placement&&this.defineClassElement(e,t)}),this)}),this)},initializeClassElements:function(e,t){var s=e.prototype;["method","field"].forEach((function(r){t.forEach((function(t){var i=t.placement;if(t.kind===r&&("static"===i||"prototype"===i)){var o="static"===i?e:s;this.defineClassElement(o,t)}}),this)}),this)},defineClassElement:function(e,t){var s=t.descriptor;if("field"===t.kind){var r=t.initializer;s={enumerable:s.enumerable,writable:s.writable,configurable:s.configurable,value:void 0===r?void 0:r.call(e)}}Object.defineProperty(e,t.key,s)},decorateClass:function(e,t){var s=[],r=[],i={static:[],prototype:[],own:[]};if(e.forEach((function(e){this.addElementPlacement(e,i)}),this),e.forEach((function(e){if(!u(e))return s.push(e);var t=this.decorateElement(e,i);s.push(t.element),s.push.apply(s,t.extras),r.push.apply(r,t.finishers)}),this),!t)return{elements:s,finishers:r};var o=this.decorateConstructor(s,t);return r.push.apply(r,o.finishers),o.finishers=r,o},addElementPlacement:function(e,t,s){var r=t[e.placement];if(!s&&-1!==r.indexOf(e.key))throw new TypeError("Duplicated element ("+e.key+")");r.push(e.key)},decorateElement:function(e,t){for(var s=[],r=[],i=e.decorators,o=i.length-1;o>=0;o--){var a=t[e.placement];a.splice(a.indexOf(e.key),1);var n=this.fromElementDescriptor(e),l=this.toElementFinisherExtras((0,i[o])(n)||n);e=l.element,this.addElementPlacement(e,t),l.finisher&&r.push(l.finisher);var d=l.extras;if(d){for(var c=0;c<d.length;c++)this.addElementPlacement(d[c],t);s.push.apply(s,d)}}return{element:e,finishers:r,extras:s}},decorateConstructor:function(e,t){for(var s=[],r=t.length-1;r>=0;r--){var i=this.fromClassDescriptor(e),o=this.toClassDescriptor((0,t[r])(i)||i);if(void 0!==o.finisher&&s.push(o.finisher),void 0!==o.elements){e=o.elements;for(var a=0;a<e.length-1;a++)for(var n=a+1;n<e.length;n++)if(e[a].key===e[n].key&&e[a].placement===e[n].placement)throw new TypeError("Duplicated element ("+e[a].key+")")}}return{elements:e,finishers:s}},fromElementDescriptor:function(e){var t={kind:e.kind,key:e.key,placement:e.placement,descriptor:e.descriptor};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),"field"===e.kind&&(t.initializer=e.initializer),t},toElementDescriptors:function(e){var t;if(void 0!==e)return(t=e,function(e){if(Array.isArray(e))return e}(t)||function(e){if("undefined"!=typeof Symbol&&Symbol.iterator in Object(e))return Array.from(e)}(t)||function(e,t){if(e){if("string"==typeof e)return v(e,t);var s=Object.prototype.toString.call(e).slice(8,-1);return"Object"===s&&e.constructor&&(s=e.constructor.name),"Map"===s||"Set"===s?Array.from(e):"Arguments"===s||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(s)?v(e,t):void 0}}(t)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()).map((function(e){var t=this.toElementDescriptor(e);return this.disallowProperty(e,"finisher","An element descriptor"),this.disallowProperty(e,"extras","An element descriptor"),t}),this)},toElementDescriptor:function(e){var t=String(e.kind);if("method"!==t&&"field"!==t)throw new TypeError('An element descriptor\'s .kind property must be either "method" or "field", but a decorator created an element descriptor with .kind "'+t+'"');var s=y(e.key),r=String(e.placement);if("static"!==r&&"prototype"!==r&&"own"!==r)throw new TypeError('An element descriptor\'s .placement property must be one of "static", "prototype" or "own", but a decorator created an element descriptor with .placement "'+r+'"');var i=e.descriptor;this.disallowProperty(e,"elements","An element descriptor");var o={kind:t,key:s,placement:r,descriptor:Object.assign({},i)};return"field"!==t?this.disallowProperty(e,"initializer","A method descriptor"):(this.disallowProperty(i,"get","The property descriptor of a field descriptor"),this.disallowProperty(i,"set","The property descriptor of a field descriptor"),this.disallowProperty(i,"value","The property descriptor of a field descriptor"),o.initializer=e.initializer),o},toElementFinisherExtras:function(e){return{element:this.toElementDescriptor(e),finisher:f(e,"finisher"),extras:this.toElementDescriptors(e.extras)}},fromClassDescriptor:function(e){var t={kind:"class",elements:e.map(this.fromElementDescriptor,this)};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),t},toClassDescriptor:function(e){var t=String(e.kind);if("class"!==t)throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator created a class descriptor with .kind "'+t+'"');this.disallowProperty(e,"key","A class descriptor"),this.disallowProperty(e,"placement","A class descriptor"),this.disallowProperty(e,"descriptor","A class descriptor"),this.disallowProperty(e,"initializer","A class descriptor"),this.disallowProperty(e,"extras","A class descriptor");var s=f(e,"finisher");return{elements:this.toElementDescriptors(e.elements),finisher:s}},runClassFinishers:function(e,t){for(var s=0;s<t.length;s++){var r=(0,t[s])(e);if(void 0!==r){if("function"!=typeof r)throw new TypeError("Finishers must return a constructor.");e=r}}return e},disallowProperty:function(e,t,s){if(void 0!==e[t])throw new TypeError(s+" can't have a ."+t+" property.")}};return e}function h(e){var t,s=y(e.key);"method"===e.kind?t={value:e.value,writable:!0,configurable:!0,enumerable:!1}:"get"===e.kind?t={get:e.value,configurable:!0,enumerable:!1}:"set"===e.kind?t={set:e.value,configurable:!0,enumerable:!1}:"field"===e.kind&&(t={configurable:!0,writable:!0,enumerable:!0});var r={kind:"field"===e.kind?"field":"method",key:s,placement:e.static?"static":"field"===e.kind?"own":"prototype",descriptor:t};return e.decorators&&(r.decorators=e.decorators),"field"===e.kind&&(r.initializer=e.value),r}function p(e,t){void 0!==e.descriptor.get?t.descriptor.get=e.descriptor.get:t.descriptor.set=e.descriptor.set}function u(e){return e.decorators&&e.decorators.length}function m(e){return void 0!==e&&!(void 0===e.value&&void 0===e.writable)}function f(e,t){var s=e[t];if(void 0!==s&&"function"!=typeof s)throw new TypeError("Expected '"+t+"' to be a function");return s}function y(e){var t=function(e,t){if("object"!=typeof e||null===e)return e;var s=e[Symbol.toPrimitive];if(void 0!==s){var r=s.call(e,t||"default");if("object"!=typeof r)return r;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===t?String:Number)(e)}(e,"string");return"symbol"==typeof t?t:String(t)}function v(e,t){(null==t||t>e.length)&&(t=e.length);for(var s=0,r=new Array(t);s<t;s++)r[s]=e[s];return r}!function(e,t,s,r){var i=c();if(r)for(var o=0;o<r.length;o++)i=r[o](i);var a=t((function(e){i.initializeInstanceElements(e,n.elements)}),s),n=i.decorateClass(function(e){for(var t=[],s=function(e){return"method"===e.kind&&e.key===o.key&&e.placement===o.placement},r=0;r<e.length;r++){var i,o=e[r];if("method"===o.kind&&(i=t.find(s)))if(m(o.descriptor)||m(i.descriptor)){if(u(o)||u(i))throw new ReferenceError("Duplicated methods ("+o.key+") can't be decorated.");i.descriptor=o.descriptor}else{if(u(o)){if(u(i))throw new ReferenceError("Decorators can't be placed on different accessors with for the same property ("+o.key+").");i.decorators=o.decorators}p(o,i)}else t.push(o)}return t}(a.d.map(h)),e);i.initializeClassElements(a.F,n.elements),i.runClassFinishers(a.F,n.finishers)}([(0,i.Mo)("dialog-hassio-snapshot")],(function(e,t){return{F:class extends t{constructor(...t){super(...t),e(this)}},d:[{kind:"field",decorators:[(0,i.Cb)({attribute:!1})],key:"hass",value:void 0},{kind:"field",decorators:[(0,i.sz)()],key:"_error",value:void 0},{kind:"field",decorators:[(0,i.sz)()],key:"_onboarding",value:()=>!1},{kind:"field",decorators:[(0,i.sz)()],key:"_snapshot",value:void 0},{kind:"field",decorators:[(0,i.sz)()],key:"_folders",value:void 0},{kind:"field",decorators:[(0,i.sz)()],key:"_addons",value:void 0},{kind:"field",decorators:[(0,i.sz)()],key:"_dialogParams",value:void 0},{kind:"field",decorators:[(0,i.sz)()],key:"_snapshotPassword",value:void 0},{kind:"field",decorators:[(0,i.sz)()],key:"_restoreHass",value:()=>!0},{kind:"method",key:"showDialog",value:async function(e){var t,s,r,i;this._snapshot=await(0,n.Ju)(this.hass,e.slug),this._folders=(e=>{const t=[];return e.includes("homeassistant")&&t.push({slug:"homeassistant",name:"Home Assistant configuration",checked:!0}),e.includes("ssl")&&t.push({slug:"ssl",name:"SSL",checked:!0}),e.includes("share")&&t.push({slug:"share",name:"Share",checked:!0}),e.includes("addons/local")&&t.push({slug:"addons/local",name:"Local add-ons",checked:!0}),t})(null===(t=this._snapshot)||void 0===t?void 0:t.folders).sort(((e,t)=>e.name>t.name?1:-1)),this._addons=(i=null===(s=this._snapshot)||void 0===s?void 0:s.addons,i.map((e=>({slug:e.slug,name:e.name,version:e.version,checked:!0})))).sort(((e,t)=>e.name>t.name?1:-1)),this._dialogParams=e,this._onboarding=null!==(r=e.onboarding)&&void 0!==r&&r}},{kind:"method",key:"render",value:function(){return this._dialogParams&&this._snapshot?i.dy`
      <ha-dialog open @closing=${this._closeDialog} .heading=${!0}>
        <div slot="heading">
          <ha-header-bar>
            <span slot="title">
              ${this._computeName}
            </span>
            <mwc-icon-button slot="actionItems" dialogAction="cancel">
              <ha-svg-icon .path=${r.r5M}></ha-svg-icon>
            </mwc-icon-button>
          </ha-header-bar>
        </div>
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
        ${this._folders.length?i.dy`
              <div>Folders:</div>
              <paper-dialog-scrollable class="no-margin-top">
                ${this._folders.map((e=>i.dy`
                    <paper-checkbox
                      .checked=${e.checked}
                      @change="${t=>this._updateFolders(e,t.target.checked)}"
                    >
                      ${e.name}
                    </paper-checkbox>
                  `))}
              </paper-dialog-scrollable>
            `:""}
        ${this._addons.length?i.dy`
              <div>Add-on:</div>
              <paper-dialog-scrollable class="no-margin-top">
                ${this._addons.map((e=>i.dy`
                    <paper-checkbox
                      .checked=${e.checked}
                      @change="${t=>this._updateAddons(e,t.target.checked)}"
                    >
                      ${e.name}
                    </paper-checkbox>
                  `))}
              </paper-dialog-scrollable>
            `:""}
        ${this._snapshot.protected?i.dy`
              <paper-input
                autofocus=""
                label="Password"
                type="password"
                @value-changed=${this._passwordInput}
                .value=${this._snapshotPassword}
              ></paper-input>
            `:""}
        ${this._error?i.dy` <p class="error">Error: ${this._error}</p> `:""}

        <div class="button-row" slot="primaryAction">
          <mwc-button @click=${this._partialRestoreClicked}>
            <ha-svg-icon .path=${r.BBX} class="icon"></ha-svg-icon>
            Restore Selected
          </mwc-button>
          ${this._onboarding?"":i.dy`
                <mwc-button @click=${this._deleteClicked}>
                  <ha-svg-icon .path=${r.x9U} class="icon warning">
                  </ha-svg-icon>
                  <span class="warning">Delete Snapshot</span>
                </mwc-button>
              `}
        </div>
        <div class="button-row" slot="secondaryAction">
          ${"full"===this._snapshot.type?i.dy`
                <mwc-button @click=${this._fullRestoreClicked}>
                  <ha-svg-icon .path=${r.BBX} class="icon"></ha-svg-icon>
                  Restore Everything
                </mwc-button>
              `:""}
          ${this._onboarding?"":i.dy`<mwc-button @click=${this._downloadClicked}>
                <ha-svg-icon .path=${r.OGU} class="icon"></ha-svg-icon>
                Download Snapshot
              </mwc-button>`}
        </div>
      </ha-dialog>
    `:i.dy``}},{kind:"get",static:!0,key:"styles",value:function(){return[d.Qx,d.yu,i.iv`
        paper-checkbox {
          display: block;
          margin: 4px;
        }
        mwc-button ha-svg-icon {
          margin-right: 4px;
        }
        .button-row {
          display: grid;
          gap: 8px;
          margin-right: 8px;
        }
        .details {
          color: var(--secondary-text-color);
        }
        .warning,
        .error {
          color: var(--error-color);
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
        ha-header-bar {
          --mdc-theme-on-primary: var(--primary-text-color);
          --mdc-theme-primary: var(--mdc-theme-surface);
          flex-shrink: 0;
        }
        /* overrule the ha-style-dialog max-height on small screens */
        @media all and (max-width: 450px), all and (max-height: 500px) {
          ha-header-bar {
            --mdc-theme-primary: var(--app-header-background-color);
            --mdc-theme-on-primary: var(--app-header-text-color, white);
          }
        }
      `]}},{kind:"method",key:"_updateFolders",value:function(e,t){this._folders=this._folders.map((s=>(s.slug===e.slug&&(s.checked=t),s)))}},{kind:"method",key:"_updateAddons",value:function(e,t){this._addons=this._addons.map((s=>(s.slug===e.slug&&(s.checked=t),s)))}},{kind:"method",key:"_passwordInput",value:function(e){this._snapshotPassword=e.detail.value}},{kind:"method",key:"_partialRestoreClicked",value:async function(){if(!await(0,l.g7)(this,{title:"Are you sure you want partially to restore this snapshot?",confirmText:"restore",dismissText:"cancel"}))return;const e=this._addons.filter((e=>e.checked)).map((e=>e.slug)),t=this._folders.filter((e=>e.checked)).map((e=>e.slug)),s={homeassistant:this._restoreHass,addons:e,folders:t};this._snapshot.protected&&(s.password=this._snapshotPassword),this._onboarding?((0,o.B)(this,"restoring"),fetch(`/api/hassio/snapshots/${this._snapshot.slug}/restore/partial`,{method:"POST",body:JSON.stringify(s)}),this._closeDialog()):this.hass.callApi("POST",`hassio/snapshots/${this._snapshot.slug}/restore/partial`,s).then((()=>{alert("Snapshot restored!"),this._closeDialog()}),(e=>{this._error=e.body.message}))}},{kind:"method",key:"_fullRestoreClicked",value:async function(){if(!await(0,l.g7)(this,{title:"Are you sure you want to wipe your system and restore this snapshot?",confirmText:"restore",dismissText:"cancel"}))return;const e=this._snapshot.protected?{password:this._snapshotPassword}:void 0;this._onboarding?((0,o.B)(this,"restoring"),fetch(`/api/hassio/snapshots/${this._snapshot.slug}/restore/full`,{method:"POST",body:JSON.stringify(e)}),this._closeDialog()):this.hass.callApi("POST",`hassio/snapshots/${this._snapshot.slug}/restore/full`,e).then((()=>{alert("Snapshot restored!"),this._closeDialog()}),(e=>{this._error=e.body.message}))}},{kind:"method",key:"_deleteClicked",value:async function(){await(0,l.g7)(this,{title:"Are you sure you want to delete this snapshot?",confirmText:"delete",dismissText:"cancel"})&&this.hass.callApi("POST",`hassio/snapshots/${this._snapshot.slug}/remove`).then((()=>{this._dialogParams.onDelete&&this._dialogParams.onDelete(),this._closeDialog()}),(e=>{this._error=e.body.message}))}},{kind:"method",key:"_downloadClicked",value:async function(){let e;try{e=await(t=this.hass,s=`/api/hassio/snapshots/${this._snapshot.slug}/download`,t.callWS({type:"auth/sign_path",path:s}))}catch(e){return void alert("Error: "+(0,a.js)(e))}var t,s;if(window.location.href.includes("ui.nabu.casa")){if(!await(0,l.g7)(this,{title:"Potential slow download",text:"Downloading snapshots over the Nabu Casa URL will take some time, it is recomended to use your local URL instead, do you want to continue?",confirmText:"continue",dismissText:"cancel"}))return}const r=this._computeName.replace(/[^a-z0-9]+/gi,"_"),i=document.createElement("a");i.href=e.path,i.download=`Hass_io_${r}.tar`,this.shadowRoot.appendChild(i),i.click(),this.shadowRoot.removeChild(i)}},{kind:"get",key:"_computeName",value:function(){return this._snapshot?this._snapshot.name||this._snapshot.slug:"Unnamed snapshot"}},{kind:"get",key:"_computeSize",value:function(){return Math.ceil(10*this._snapshot.size)/10+" MB"}},{kind:"method",key:"_formatDatetime",value:function(e){return new Date(e).toLocaleDateString(navigator.language,{weekday:"long",year:"numeric",month:"short",day:"numeric",hour:"numeric",minute:"2-digit"})}},{kind:"method",key:"_closeDialog",value:function(){this._dialogParams=void 0,this._snapshot=void 0,this._snapshotPassword="",this._folders=[],this._addons=[]}}]}}),i.oi)}}]);
//# sourceMappingURL=chunk.84bb4ce87457156316bb.js.map