(self.webpackChunkhome_assistant_frontend=self.webpackChunkhome_assistant_frontend||[]).push([[817],{817:(e,t,r)=>{"use strict";r.r(t);r(573);var s=r(5317),o=(r(6480),r(7956),r(9722)),n=r(8928);const i=r(3274).Op?(e,t)=>e.toLocaleString(t.language,{year:"numeric",month:"long",day:"numeric",hour:"numeric",minute:"2-digit"}):e=>(0,n.WU)(e,"MMMM D, YYYY, HH:mm");var a=r(7181);r(3221),r(2039);location.protocol,location.host;var l=r(1682),c=r(7097),d=r(6765),h=r(1654);function u(){u=function(){return e};var e={elementsDefinitionOrder:[["method"],["field"]],initializeInstanceElements:function(e,t){["method","field"].forEach((function(r){t.forEach((function(t){t.kind===r&&"own"===t.placement&&this.defineClassElement(e,t)}),this)}),this)},initializeClassElements:function(e,t){var r=e.prototype;["method","field"].forEach((function(s){t.forEach((function(t){var o=t.placement;if(t.kind===s&&("static"===o||"prototype"===o)){var n="static"===o?e:r;this.defineClassElement(n,t)}}),this)}),this)},defineClassElement:function(e,t){var r=t.descriptor;if("field"===t.kind){var s=t.initializer;r={enumerable:r.enumerable,writable:r.writable,configurable:r.configurable,value:void 0===s?void 0:s.call(e)}}Object.defineProperty(e,t.key,r)},decorateClass:function(e,t){var r=[],s=[],o={static:[],prototype:[],own:[]};if(e.forEach((function(e){this.addElementPlacement(e,o)}),this),e.forEach((function(e){if(!f(e))return r.push(e);var t=this.decorateElement(e,o);r.push(t.element),r.push.apply(r,t.extras),s.push.apply(s,t.finishers)}),this),!t)return{elements:r,finishers:s};var n=this.decorateConstructor(r,t);return s.push.apply(s,n.finishers),n.finishers=s,n},addElementPlacement:function(e,t,r){var s=t[e.placement];if(!r&&-1!==s.indexOf(e.key))throw new TypeError("Duplicated element ("+e.key+")");s.push(e.key)},decorateElement:function(e,t){for(var r=[],s=[],o=e.decorators,n=o.length-1;n>=0;n--){var i=t[e.placement];i.splice(i.indexOf(e.key),1);var a=this.fromElementDescriptor(e),l=this.toElementFinisherExtras((0,o[n])(a)||a);e=l.element,this.addElementPlacement(e,t),l.finisher&&s.push(l.finisher);var c=l.extras;if(c){for(var d=0;d<c.length;d++)this.addElementPlacement(c[d],t);r.push.apply(r,c)}}return{element:e,finishers:s,extras:r}},decorateConstructor:function(e,t){for(var r=[],s=t.length-1;s>=0;s--){var o=this.fromClassDescriptor(e),n=this.toClassDescriptor((0,t[s])(o)||o);if(void 0!==n.finisher&&r.push(n.finisher),void 0!==n.elements){e=n.elements;for(var i=0;i<e.length-1;i++)for(var a=i+1;a<e.length;a++)if(e[i].key===e[a].key&&e[i].placement===e[a].placement)throw new TypeError("Duplicated element ("+e[i].key+")")}}return{elements:e,finishers:r}},fromElementDescriptor:function(e){var t={kind:e.kind,key:e.key,placement:e.placement,descriptor:e.descriptor};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),"field"===e.kind&&(t.initializer=e.initializer),t},toElementDescriptors:function(e){var t;if(void 0!==e)return(t=e,function(e){if(Array.isArray(e))return e}(t)||function(e){if("undefined"!=typeof Symbol&&null!=e[Symbol.iterator]||null!=e["@@iterator"])return Array.from(e)}(t)||function(e,t){if(e){if("string"==typeof e)return k(e,t);var r=Object.prototype.toString.call(e).slice(8,-1);return"Object"===r&&e.constructor&&(r=e.constructor.name),"Map"===r||"Set"===r?Array.from(e):"Arguments"===r||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(r)?k(e,t):void 0}}(t)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()).map((function(e){var t=this.toElementDescriptor(e);return this.disallowProperty(e,"finisher","An element descriptor"),this.disallowProperty(e,"extras","An element descriptor"),t}),this)},toElementDescriptor:function(e){var t=String(e.kind);if("method"!==t&&"field"!==t)throw new TypeError('An element descriptor\'s .kind property must be either "method" or "field", but a decorator created an element descriptor with .kind "'+t+'"');var r=y(e.key),s=String(e.placement);if("static"!==s&&"prototype"!==s&&"own"!==s)throw new TypeError('An element descriptor\'s .placement property must be one of "static", "prototype" or "own", but a decorator created an element descriptor with .placement "'+s+'"');var o=e.descriptor;this.disallowProperty(e,"elements","An element descriptor");var n={kind:t,key:r,placement:s,descriptor:Object.assign({},o)};return"field"!==t?this.disallowProperty(e,"initializer","A method descriptor"):(this.disallowProperty(o,"get","The property descriptor of a field descriptor"),this.disallowProperty(o,"set","The property descriptor of a field descriptor"),this.disallowProperty(o,"value","The property descriptor of a field descriptor"),n.initializer=e.initializer),n},toElementFinisherExtras:function(e){return{element:this.toElementDescriptor(e),finisher:v(e,"finisher"),extras:this.toElementDescriptors(e.extras)}},fromClassDescriptor:function(e){var t={kind:"class",elements:e.map(this.fromElementDescriptor,this)};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),t},toClassDescriptor:function(e){var t=String(e.kind);if("class"!==t)throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator created a class descriptor with .kind "'+t+'"');this.disallowProperty(e,"key","A class descriptor"),this.disallowProperty(e,"placement","A class descriptor"),this.disallowProperty(e,"descriptor","A class descriptor"),this.disallowProperty(e,"initializer","A class descriptor"),this.disallowProperty(e,"extras","A class descriptor");var r=v(e,"finisher");return{elements:this.toElementDescriptors(e.elements),finisher:r}},runClassFinishers:function(e,t){for(var r=0;r<t.length;r++){var s=(0,t[r])(e);if(void 0!==s){if("function"!=typeof s)throw new TypeError("Finishers must return a constructor.");e=s}}return e},disallowProperty:function(e,t,r){if(void 0!==e[t])throw new TypeError(r+" can't have a ."+t+" property.")}};return e}function p(e){var t,r=y(e.key);"method"===e.kind?t={value:e.value,writable:!0,configurable:!0,enumerable:!1}:"get"===e.kind?t={get:e.value,configurable:!0,enumerable:!1}:"set"===e.kind?t={set:e.value,configurable:!0,enumerable:!1}:"field"===e.kind&&(t={configurable:!0,writable:!0,enumerable:!0});var s={kind:"field"===e.kind?"field":"method",key:r,placement:e.static?"static":"field"===e.kind?"own":"prototype",descriptor:t};return e.decorators&&(s.decorators=e.decorators),"field"===e.kind&&(s.initializer=e.value),s}function m(e,t){void 0!==e.descriptor.get?t.descriptor.get=e.descriptor.get:t.descriptor.set=e.descriptor.set}function f(e){return e.decorators&&e.decorators.length}function g(e){return void 0!==e&&!(void 0===e.value&&void 0===e.writable)}function v(e,t){var r=e[t];if(void 0!==r&&"function"!=typeof r)throw new TypeError("Expected '"+t+"' to be a function");return r}function y(e){var t=function(e,t){if("object"!=typeof e||null===e)return e;var r=e[Symbol.toPrimitive];if(void 0!==r){var s=r.call(e,t||"default");if("object"!=typeof s)return s;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===t?String:Number)(e)}(e,"string");return"symbol"==typeof t?t:String(t)}function k(e,t){(null==t||t>e.length)&&(t=e.length);for(var r=0,s=new Array(t);r<t;r++)s[r]=e[r];return s}!function(e,t,r,s){var o=u();if(s)for(var n=0;n<s.length;n++)o=s[n](o);var i=t((function(e){o.initializeInstanceElements(e,a.elements)}),r),a=o.decorateClass(function(e){for(var t=[],r=function(e){return"method"===e.kind&&e.key===n.key&&e.placement===n.placement},s=0;s<e.length;s++){var o,n=e[s];if("method"===n.kind&&(o=t.find(r)))if(g(n.descriptor)||g(o.descriptor)){if(f(n)||f(o))throw new ReferenceError("Duplicated methods ("+n.key+") can't be decorated.");o.descriptor=n.descriptor}else{if(f(n)){if(f(o))throw new ReferenceError("Decorators can't be placed on different accessors with for the same property ("+n.key+").");o.decorators=n.decorators}m(n,o)}else t.push(n)}return t}(i.d.map(p)),e);o.initializeClassElements(i.F,a.elements),o.runClassFinishers(i.F,a.finishers)}([(0,o.Mo)("dialog-hassio-snapshot")],(function(e,t){return{F:class extends t{constructor(...t){super(...t),e(this)}},d:[{kind:"field",decorators:[(0,o.Cb)({attribute:!1})],key:"hass",value:void 0},{kind:"field",decorators:[(0,o.Cb)({attribute:!1})],key:"supervisor",value:void 0},{kind:"field",decorators:[(0,o.SB)()],key:"_error",value:void 0},{kind:"field",decorators:[(0,o.SB)()],key:"_onboarding",value:()=>!1},{kind:"field",decorators:[(0,o.SB)()],key:"_snapshot",value:void 0},{kind:"field",decorators:[(0,o.SB)()],key:"_folders",value:void 0},{kind:"field",decorators:[(0,o.SB)()],key:"_addons",value:void 0},{kind:"field",decorators:[(0,o.SB)()],key:"_dialogParams",value:void 0},{kind:"field",decorators:[(0,o.SB)()],key:"_snapshotPassword",value:void 0},{kind:"field",decorators:[(0,o.SB)()],key:"_restoreHass",value:()=>!0},{kind:"method",key:"showDialog",value:async function(e){var t,r,s,o;this._snapshot=await(0,c.Ju)(this.hass,e.slug),this._folders=(e=>{const t=[];return e.includes("homeassistant")&&t.push({slug:"homeassistant",name:"Home Assistant configuration",checked:!0}),e.includes("ssl")&&t.push({slug:"ssl",name:"SSL",checked:!0}),e.includes("share")&&t.push({slug:"share",name:"Share",checked:!0}),e.includes("addons/local")&&t.push({slug:"addons/local",name:"Local add-ons",checked:!0}),t})(null===(t=this._snapshot)||void 0===t?void 0:t.folders).sort(((e,t)=>e.name>t.name?1:-1)),this._addons=(o=null===(r=this._snapshot)||void 0===r?void 0:r.addons,o.map((e=>({slug:e.slug,name:e.name,version:e.version,checked:!0})))).sort(((e,t)=>e.name>t.name?1:-1)),this._dialogParams=e,this._onboarding=null!==(s=e.onboarding)&&void 0!==s&&s,this.supervisor=e.supervisor,this._snapshot.homeassistant||(this._restoreHass=!1)}},{kind:"method",key:"render",value:function(){return this._dialogParams&&this._snapshot?o.dy`
      <ha-dialog open @closing=${this._closeDialog} .heading=${!0}>
        <div slot="heading">
          <ha-header-bar>
            <span slot="title"> ${this._computeName} </span>
            <mwc-icon-button slot="actionItems" dialogAction="cancel">
              <ha-svg-icon .path=${s.r5M}></ha-svg-icon>
            </mwc-icon-button>
          </ha-header-bar>
        </div>
        <div class="details">
          ${"full"===this._snapshot.type?"Full snapshot":"Partial snapshot"}
          (${this._computeSize})<br />
          ${i(new Date(this._snapshot.date),this.hass.locale)}
        </div>
        ${this._snapshot.homeassistant?o.dy`<div>Home Assistant:</div>
              <paper-checkbox
                .checked=${this._restoreHass}
                @change="${e=>{this._restoreHass=e.target.checked}}"
              >
                Home Assistant
                <span class="version">(${this._snapshot.homeassistant})</span>
              </paper-checkbox>`:""}
        ${this._folders.length?o.dy`
              <div>Folders:</div>
              <paper-dialog-scrollable class="no-margin-top">
                ${this._folders.map((e=>o.dy`
                    <paper-checkbox
                      .checked=${e.checked}
                      @change="${t=>this._updateFolders(e,t.target.checked)}"
                    >
                      ${e.name}
                    </paper-checkbox>
                  `))}
              </paper-dialog-scrollable>
            `:""}
        ${this._addons.length?o.dy`
              <div>Add-on:</div>
              <paper-dialog-scrollable class="no-margin-top">
                ${this._addons.map((e=>o.dy`
                    <paper-checkbox
                      .checked=${e.checked}
                      @change="${t=>this._updateAddons(e,t.target.checked)}"
                    >
                      ${e.name}
                      <span class="version">(${e.version})</span>
                    </paper-checkbox>
                  `))}
              </paper-dialog-scrollable>
            `:""}
        ${this._snapshot.protected?o.dy`
              <paper-input
                autofocus=""
                label="Password"
                type="password"
                @value-changed=${this._passwordInput}
                .value=${this._snapshotPassword}
              ></paper-input>
            `:""}
        ${this._error?o.dy` <p class="error">Error: ${this._error}</p> `:""}

        <div class="button-row" slot="primaryAction">
          <mwc-button @click=${this._partialRestoreClicked}>
            <ha-svg-icon .path=${s.BBX} class="icon"></ha-svg-icon>
            Restore Selected
          </mwc-button>
          ${this._onboarding?"":o.dy`
                <mwc-button @click=${this._deleteClicked}>
                  <ha-svg-icon .path=${s.x9U} class="icon warning">
                  </ha-svg-icon>
                  <span class="warning">Delete Snapshot</span>
                </mwc-button>
              `}
        </div>
        <div class="button-row" slot="secondaryAction">
          ${"full"===this._snapshot.type?o.dy`
                <mwc-button @click=${this._fullRestoreClicked}>
                  <ha-svg-icon .path=${s.BBX} class="icon"></ha-svg-icon>
                  Restore Everything
                </mwc-button>
              `:""}
          ${this._onboarding?"":o.dy`<mwc-button @click=${this._downloadClicked}>
                <ha-svg-icon .path=${s.OGU} class="icon"></ha-svg-icon>
                Download Snapshot
              </mwc-button>`}
        </div>
      </ha-dialog>
    `:o.dy``}},{kind:"get",static:!0,key:"styles",value:function(){return[h.Qx,h.yu,o.iv`
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
        span.version {
          color: var(--secondary-text-color);
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
      `]}},{kind:"method",key:"_updateFolders",value:function(e,t){this._folders=this._folders.map((r=>(r.slug===e.slug&&(r.checked=t),r)))}},{kind:"method",key:"_updateAddons",value:function(e,t){this._addons=this._addons.map((r=>(r.slug===e.slug&&(r.checked=t),r)))}},{kind:"method",key:"_passwordInput",value:function(e){this._snapshotPassword=e.detail.value}},{kind:"method",key:"_partialRestoreClicked",value:async function(){if(void 0!==this.supervisor&&"running"!==this.supervisor.info.state)return void await(0,d.Ys)(this,{title:"Could not restore snapshot",text:`Restoring a snapshot is not possible right now because the system is in ${this.supervisor.info.state} state.`});if(!await(0,d.g7)(this,{title:"Are you sure you want partially to restore this snapshot?",confirmText:"restore",dismissText:"cancel"}))return;const e=this._addons.filter((e=>e.checked)).map((e=>e.slug)),t=this._folders.filter((e=>e.checked)).map((e=>e.slug)),r={homeassistant:this._restoreHass,addons:e,folders:t};this._snapshot.protected&&(r.password=this._snapshotPassword),this._onboarding?((0,a.B)(this,"restoring"),fetch(`/api/hassio/snapshots/${this._snapshot.slug}/restore/partial`,{method:"POST",body:JSON.stringify(r)}),this._closeDialog()):this.hass.callApi("POST",`hassio/snapshots/${this._snapshot.slug}/restore/partial`,r).then((()=>{alert("Snapshot restored!"),this._closeDialog()}),(e=>{this._error=e.body.message}))}},{kind:"method",key:"_fullRestoreClicked",value:async function(){if(void 0!==this.supervisor&&"running"!==this.supervisor.info.state)return void await(0,d.Ys)(this,{title:"Could not restore snapshot",text:`Restoring a snapshot is not possible right now because the system is in ${this.supervisor.info.state} state.`});if(!await(0,d.g7)(this,{title:"Are you sure you want to wipe your system and restore this snapshot?",confirmText:"restore",dismissText:"cancel"}))return;const e=this._snapshot.protected?{password:this._snapshotPassword}:void 0;this._onboarding?((0,a.B)(this,"restoring"),fetch(`/api/hassio/snapshots/${this._snapshot.slug}/restore/full`,{method:"POST",body:JSON.stringify(e)}),this._closeDialog()):this.hass.callApi("POST",`hassio/snapshots/${this._snapshot.slug}/restore/full`,e).then((()=>{alert("Snapshot restored!"),this._closeDialog()}),(e=>{this._error=e.body.message}))}},{kind:"method",key:"_deleteClicked",value:async function(){await(0,d.g7)(this,{title:"Are you sure you want to delete this snapshot?",confirmText:"delete",dismissText:"cancel"})&&this.hass.callApi("POST",`hassio/snapshots/${this._snapshot.slug}/remove`).then((()=>{this._dialogParams.onDelete&&this._dialogParams.onDelete(),this._closeDialog()}),(e=>{this._error=e.body.message}))}},{kind:"method",key:"_downloadClicked",value:async function(){let e;try{e=await(t=this.hass,r=`/api/hassio/snapshots/${this._snapshot.slug}/download`,t.callWS({type:"auth/sign_path",path:r}))}catch(e){return void alert(`Error: ${(0,l.js)(e)}`)}var t,r;if(window.location.href.includes("ui.nabu.casa")){if(!await(0,d.g7)(this,{title:"Potential slow download",text:"Downloading snapshots over the Nabu Casa URL will take some time, it is recomended to use your local URL instead, do you want to continue?",confirmText:"continue",dismissText:"cancel"}))return}const s=this._computeName.replace(/[^a-z0-9]+/gi,"_"),o=document.createElement("a");o.href=e.path,o.download=`Hass_io_${s}.tar`,this.shadowRoot.appendChild(o),o.click(),this.shadowRoot.removeChild(o)}},{kind:"get",key:"_computeName",value:function(){return this._snapshot?this._snapshot.name||this._snapshot.slug:"Unnamed snapshot"}},{kind:"get",key:"_computeSize",value:function(){return Math.ceil(10*this._snapshot.size)/10+" MB"}},{kind:"method",key:"_closeDialog",value:function(){this._dialogParams=void 0,this._snapshot=void 0,this._snapshotPassword="",this._folders=[],this._addons=[]}}]}}),o.oi)},8928:(e,t,r)=>{"use strict";r.d(t,{WU:()=>D});var s=/d{1,4}|M{1,4}|YY(?:YY)?|S{1,3}|Do|ZZ|Z|([HhMsDm])\1?|[aA]|"[^"]*"|'[^']*'/g,o="[1-9]\\d?",n="\\d\\d",i="[^\\s]+",a=/\[([^]*?)\]/gm;function l(e,t){for(var r=[],s=0,o=e.length;s<o;s++)r.push(e[s].substr(0,t));return r}var c=function(e){return function(t,r){var s=r[e].map((function(e){return e.toLowerCase()})).indexOf(t.toLowerCase());return s>-1?s:null}};function d(e){for(var t=[],r=1;r<arguments.length;r++)t[r-1]=arguments[r];for(var s=0,o=t;s<o.length;s++){var n=o[s];for(var i in n)e[i]=n[i]}return e}var h=["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"],u=["January","February","March","April","May","June","July","August","September","October","November","December"],p=l(u,3),m={dayNamesShort:l(h,3),dayNames:h,monthNamesShort:p,monthNames:u,amPm:["am","pm"],DoFn:function(e){return e+["th","st","nd","rd"][e%10>3?0:(e-e%10!=10?1:0)*e%10]}},f=d({},m),g=function(e,t){for(void 0===t&&(t=2),e=String(e);e.length<t;)e="0"+e;return e},v={D:function(e){return String(e.getDate())},DD:function(e){return g(e.getDate())},Do:function(e,t){return t.DoFn(e.getDate())},d:function(e){return String(e.getDay())},dd:function(e){return g(e.getDay())},ddd:function(e,t){return t.dayNamesShort[e.getDay()]},dddd:function(e,t){return t.dayNames[e.getDay()]},M:function(e){return String(e.getMonth()+1)},MM:function(e){return g(e.getMonth()+1)},MMM:function(e,t){return t.monthNamesShort[e.getMonth()]},MMMM:function(e,t){return t.monthNames[e.getMonth()]},YY:function(e){return g(String(e.getFullYear()),4).substr(2)},YYYY:function(e){return g(e.getFullYear(),4)},h:function(e){return String(e.getHours()%12||12)},hh:function(e){return g(e.getHours()%12||12)},H:function(e){return String(e.getHours())},HH:function(e){return g(e.getHours())},m:function(e){return String(e.getMinutes())},mm:function(e){return g(e.getMinutes())},s:function(e){return String(e.getSeconds())},ss:function(e){return g(e.getSeconds())},S:function(e){return String(Math.round(e.getMilliseconds()/100))},SS:function(e){return g(Math.round(e.getMilliseconds()/10),2)},SSS:function(e){return g(e.getMilliseconds(),3)},a:function(e,t){return e.getHours()<12?t.amPm[0]:t.amPm[1]},A:function(e,t){return e.getHours()<12?t.amPm[0].toUpperCase():t.amPm[1].toUpperCase()},ZZ:function(e){var t=e.getTimezoneOffset();return(t>0?"-":"+")+g(100*Math.floor(Math.abs(t)/60)+Math.abs(t)%60,4)},Z:function(e){var t=e.getTimezoneOffset();return(t>0?"-":"+")+g(Math.floor(Math.abs(t)/60),2)+":"+g(Math.abs(t)%60,2)}},y=function(e){return+e-1},k=[null,o],w=[null,i],b=["isPm",i,function(e,t){var r=e.toLowerCase();return r===t.amPm[0]?0:r===t.amPm[1]?1:null}],_=["timezoneOffset","[^\\s]*?[\\+\\-]\\d\\d:?\\d\\d|[^\\s]*?Z?",function(e){var t=(e+"").match(/([+-]|\d\d)/gi);if(t){var r=60*+t[1]+parseInt(t[2],10);return"+"===t[0]?r:-r}return 0}],S=(c("monthNamesShort"),c("monthNames"),{default:"ddd MMM DD YYYY HH:mm:ss",shortDate:"M/D/YY",mediumDate:"MMM D, YYYY",longDate:"MMMM D, YYYY",fullDate:"dddd, MMMM D, YYYY",isoDate:"YYYY-MM-DD",isoDateTime:"YYYY-MM-DDTHH:mm:ssZ",shortTime:"HH:mm",mediumTime:"HH:mm:ss",longTime:"HH:mm:ss.SSS"}),D=function(e,t,r){if(void 0===t&&(t=S.default),void 0===r&&(r={}),"number"==typeof e&&(e=new Date(e)),"[object Date]"!==Object.prototype.toString.call(e)||isNaN(e.getTime()))throw new Error("Invalid Date pass to format");var o=[];t=(t=S[t]||t).replace(a,(function(e,t){return o.push(t),"@@@"}));var n=d(d({},f),r);return(t=t.replace(s,(function(t){return v[t](e,n)}))).replace(/@@@/g,(function(){return o.shift()}))}},3274:(e,t,r)=>{"use strict";r.d(t,{Sb:()=>s,Op:()=>o});const s=function(){try{(new Date).toLocaleDateString("i")}catch(e){return"RangeError"===e.name}return!1}(),o=(function(){try{(new Date).toLocaleTimeString("i")}catch(e){return"RangeError"===e.name}}(),function(){try{(new Date).toLocaleString("i")}catch(e){return"RangeError"===e.name}return!1}())}}]);
//# sourceMappingURL=chunk.c5f3fbfc128ea3ea86af.js.map