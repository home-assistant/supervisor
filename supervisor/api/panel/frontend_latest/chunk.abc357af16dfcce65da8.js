(self.webpackChunkhome_assistant_frontend=self.webpackChunkhome_assistant_frontend||[]).push([[835],{1835:(e,t,r)=>{"use strict";r.r(t);r(573),r(7956);var s=r(9722),n=r(8928);const i=r(3274).Sb?(e,t)=>e.toLocaleDateString(t.language,{year:"numeric",month:"long",day:"numeric"}):e=>(0,n.WU)(e,"longDate");var o=r(7181),a=r(5415),l=(r(8762),r(254),r(4990)),c=(r(9583),r(1282),r(4089),r(1682)),d=r(7097),h=r(6765),u=r(1654);function p(){p=function(){return e};var e={elementsDefinitionOrder:[["method"],["field"]],initializeInstanceElements:function(e,t){["method","field"].forEach((function(r){t.forEach((function(t){t.kind===r&&"own"===t.placement&&this.defineClassElement(e,t)}),this)}),this)},initializeClassElements:function(e,t){var r=e.prototype;["method","field"].forEach((function(s){t.forEach((function(t){var n=t.placement;if(t.kind===s&&("static"===n||"prototype"===n)){var i="static"===n?e:r;this.defineClassElement(i,t)}}),this)}),this)},defineClassElement:function(e,t){var r=t.descriptor;if("field"===t.kind){var s=t.initializer;r={enumerable:r.enumerable,writable:r.writable,configurable:r.configurable,value:void 0===s?void 0:s.call(e)}}Object.defineProperty(e,t.key,r)},decorateClass:function(e,t){var r=[],s=[],n={static:[],prototype:[],own:[]};if(e.forEach((function(e){this.addElementPlacement(e,n)}),this),e.forEach((function(e){if(!g(e))return r.push(e);var t=this.decorateElement(e,n);r.push(t.element),r.push.apply(r,t.extras),s.push.apply(s,t.finishers)}),this),!t)return{elements:r,finishers:s};var i=this.decorateConstructor(r,t);return s.push.apply(s,i.finishers),i.finishers=s,i},addElementPlacement:function(e,t,r){var s=t[e.placement];if(!r&&-1!==s.indexOf(e.key))throw new TypeError("Duplicated element ("+e.key+")");s.push(e.key)},decorateElement:function(e,t){for(var r=[],s=[],n=e.decorators,i=n.length-1;i>=0;i--){var o=t[e.placement];o.splice(o.indexOf(e.key),1);var a=this.fromElementDescriptor(e),l=this.toElementFinisherExtras((0,n[i])(a)||a);e=l.element,this.addElementPlacement(e,t),l.finisher&&s.push(l.finisher);var c=l.extras;if(c){for(var d=0;d<c.length;d++)this.addElementPlacement(c[d],t);r.push.apply(r,c)}}return{element:e,finishers:s,extras:r}},decorateConstructor:function(e,t){for(var r=[],s=t.length-1;s>=0;s--){var n=this.fromClassDescriptor(e),i=this.toClassDescriptor((0,t[s])(n)||n);if(void 0!==i.finisher&&r.push(i.finisher),void 0!==i.elements){e=i.elements;for(var o=0;o<e.length-1;o++)for(var a=o+1;a<e.length;a++)if(e[o].key===e[a].key&&e[o].placement===e[a].placement)throw new TypeError("Duplicated element ("+e[o].key+")")}}return{elements:e,finishers:r}},fromElementDescriptor:function(e){var t={kind:e.kind,key:e.key,placement:e.placement,descriptor:e.descriptor};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),"field"===e.kind&&(t.initializer=e.initializer),t},toElementDescriptors:function(e){var t;if(void 0!==e)return(t=e,function(e){if(Array.isArray(e))return e}(t)||function(e){if("undefined"!=typeof Symbol&&null!=e[Symbol.iterator]||null!=e["@@iterator"])return Array.from(e)}(t)||function(e,t){if(e){if("string"==typeof e)return _(e,t);var r=Object.prototype.toString.call(e).slice(8,-1);return"Object"===r&&e.constructor&&(r=e.constructor.name),"Map"===r||"Set"===r?Array.from(e):"Arguments"===r||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(r)?_(e,t):void 0}}(t)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()).map((function(e){var t=this.toElementDescriptor(e);return this.disallowProperty(e,"finisher","An element descriptor"),this.disallowProperty(e,"extras","An element descriptor"),t}),this)},toElementDescriptor:function(e){var t=String(e.kind);if("method"!==t&&"field"!==t)throw new TypeError('An element descriptor\'s .kind property must be either "method" or "field", but a decorator created an element descriptor with .kind "'+t+'"');var r=k(e.key),s=String(e.placement);if("static"!==s&&"prototype"!==s&&"own"!==s)throw new TypeError('An element descriptor\'s .placement property must be one of "static", "prototype" or "own", but a decorator created an element descriptor with .placement "'+s+'"');var n=e.descriptor;this.disallowProperty(e,"elements","An element descriptor");var i={kind:t,key:r,placement:s,descriptor:Object.assign({},n)};return"field"!==t?this.disallowProperty(e,"initializer","A method descriptor"):(this.disallowProperty(n,"get","The property descriptor of a field descriptor"),this.disallowProperty(n,"set","The property descriptor of a field descriptor"),this.disallowProperty(n,"value","The property descriptor of a field descriptor"),i.initializer=e.initializer),i},toElementFinisherExtras:function(e){return{element:this.toElementDescriptor(e),finisher:y(e,"finisher"),extras:this.toElementDescriptors(e.extras)}},fromClassDescriptor:function(e){var t={kind:"class",elements:e.map(this.fromElementDescriptor,this)};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),t},toClassDescriptor:function(e){var t=String(e.kind);if("class"!==t)throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator created a class descriptor with .kind "'+t+'"');this.disallowProperty(e,"key","A class descriptor"),this.disallowProperty(e,"placement","A class descriptor"),this.disallowProperty(e,"descriptor","A class descriptor"),this.disallowProperty(e,"initializer","A class descriptor"),this.disallowProperty(e,"extras","A class descriptor");var r=y(e,"finisher");return{elements:this.toElementDescriptors(e.elements),finisher:r}},runClassFinishers:function(e,t){for(var r=0;r<t.length;r++){var s=(0,t[r])(e);if(void 0!==s){if("function"!=typeof s)throw new TypeError("Finishers must return a constructor.");e=s}}return e},disallowProperty:function(e,t,r){if(void 0!==e[t])throw new TypeError(r+" can't have a ."+t+" property.")}};return e}function f(e){var t,r=k(e.key);"method"===e.kind?t={value:e.value,writable:!0,configurable:!0,enumerable:!1}:"get"===e.kind?t={get:e.value,configurable:!0,enumerable:!1}:"set"===e.kind?t={set:e.value,configurable:!0,enumerable:!1}:"field"===e.kind&&(t={configurable:!0,writable:!0,enumerable:!0});var s={kind:"field"===e.kind?"field":"method",key:r,placement:e.static?"static":"field"===e.kind?"own":"prototype",descriptor:t};return e.decorators&&(s.decorators=e.decorators),"field"===e.kind&&(s.initializer=e.value),s}function m(e,t){void 0!==e.descriptor.get?t.descriptor.get=e.descriptor.get:t.descriptor.set=e.descriptor.set}function g(e){return e.decorators&&e.decorators.length}function v(e){return void 0!==e&&!(void 0===e.value&&void 0===e.writable)}function y(e,t){var r=e[t];if(void 0!==r&&"function"!=typeof r)throw new TypeError("Expected '"+t+"' to be a function");return r}function k(e){var t=function(e,t){if("object"!=typeof e||null===e)return e;var r=e[Symbol.toPrimitive];if(void 0!==r){var s=r.call(e,t||"default");if("object"!=typeof s)return s;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===t?String:Number)(e)}(e,"string");return"symbol"==typeof t?t:String(t)}function _(e,t){(null==t||t>e.length)&&(t=e.length);for(var r=0,s=new Array(t);r<t;r++)s[r]=e[r];return s}!function(e,t,r,s){var n=p();if(s)for(var i=0;i<s.length;i++)n=s[i](n);var o=t((function(e){n.initializeInstanceElements(e,a.elements)}),r),a=n.decorateClass(function(e){for(var t=[],r=function(e){return"method"===e.kind&&e.key===i.key&&e.placement===i.placement},s=0;s<e.length;s++){var n,i=e[s];if("method"===i.kind&&(n=t.find(r)))if(v(i.descriptor)||v(n.descriptor)){if(g(i)||g(n))throw new ReferenceError("Duplicated methods ("+i.key+") can't be decorated.");n.descriptor=i.descriptor}else{if(g(i)){if(g(n))throw new ReferenceError("Decorators can't be placed on different accessors with for the same property ("+i.key+").");n.decorators=i.decorators}m(i,n)}else t.push(i)}return t}(o.d.map(f)),e);n.initializeClassElements(o.F,a.elements),n.runClassFinishers(o.F,a.finishers)}([(0,s.Mo)("dialog-hassio-create-snapshot")],(function(e,t){return{F:class extends t{constructor(...t){super(...t),e(this)}},d:[{kind:"field",decorators:[(0,s.Cb)({attribute:!1})],key:"hass",value:void 0},{kind:"field",decorators:[(0,s.SB)()],key:"_snapshotName",value:()=>""},{kind:"field",decorators:[(0,s.SB)()],key:"_snapshotPassword",value:()=>""},{kind:"field",decorators:[(0,s.SB)()],key:"_snapshotHasPassword",value:()=>!1},{kind:"field",decorators:[(0,s.SB)()],key:"_snapshotType",value:()=>"full"},{kind:"field",decorators:[(0,s.SB)()],key:"_dialogParams",value:void 0},{kind:"field",decorators:[(0,s.SB)()],key:"_addonList",value:()=>[]},{kind:"field",decorators:[(0,s.SB)()],key:"_folderList",value:()=>[{slug:"homeassistant",checked:!0},{slug:"ssl",checked:!0},{slug:"share",checked:!0},{slug:"media",checked:!0},{slug:"addons/local",checked:!0}]},{kind:"field",decorators:[(0,s.SB)()],key:"_error",value:()=>""},{kind:"method",key:"showDialog",value:function(e){this._dialogParams=e,this._addonList=this._dialogParams.supervisor.supervisor.addons.map((e=>({slug:e.slug,name:e.name,version:e.version,checked:!0}))).sort(((e,t)=>(0,a.q)(e.name,t.name))),this._snapshotType="full",this._error="",this._folderList=[{slug:"homeassistant",checked:!0},{slug:"ssl",checked:!0},{slug:"share",checked:!0},{slug:"media",checked:!0},{slug:"addons/local",checked:!0}],this._snapshotHasPassword=!1,this._snapshotPassword="",this._snapshotName=""}},{kind:"method",key:"closeDialog",value:function(){this._dialogParams=void 0,(0,o.B)(this,"dialog-closed",{dialog:this.localName})}},{kind:"method",key:"render",value:function(){return this._dialogParams?s.dy`
      <ha-dialog
        open
        @closing=${this.closeDialog}
        .heading=${(0,l.i)(this.hass,this._dialogParams.supervisor.localize("snapshot.create_snapshot"))}
      >
          <paper-input
            name="snapshotName"
            .label=${this._dialogParams.supervisor.localize("snapshot.name")}
            .value=${this._snapshotName}
            @value-changed=${this._handleTextValueChanged}
          >
          </paper-input>
          <div class="snapshot-types">
            <div>
              ${this._dialogParams.supervisor.localize("snapshot.type")}:
            </div>
            <ha-formfield
              .label=${this._dialogParams.supervisor.localize("snapshot.full_snapshot")}
            >
              <ha-radio
                @change=${this._handleRadioValueChanged}
                value="full"
                name="snapshotType"
                .checked=${"full"===this._snapshotType}
              >
              </ha-radio>
            </ha-formfield>
            <ha-formfield
              .label=${this._dialogParams.supervisor.localize("snapshot.partial_snapshot")}
            >
              <ha-radio
                @change=${this._handleRadioValueChanged}
                value="partial"
                name="snapshotType"
                .checked=${"partial"===this._snapshotType}
              >
              </ha-radio>
            </ha-formfield>
          </div>

          ${"full"===this._snapshotType?void 0:s.dy`
                  ${this._dialogParams.supervisor.localize("snapshot.folders")}:
                  <div class="checkbox-section">
                    ${this._folderList.map(((e,t)=>s.dy`
                        <div class="checkbox-line">
                          <ha-checkbox
                            .idx=${t}
                            .checked=${e.checked}
                            @change=${this._folderChecked}
                            slot="prefix"
                          >
                          </ha-checkbox>
                          <span>
                            ${this._dialogParams.supervisor.localize(`snapshot.folder.${e.slug}`)}
                          </span>
                        </div>
                      `))}
                  </div>

                  ${this._dialogParams.supervisor.localize("snapshot.addons")}:
                  <div class="checkbox-section">
                    ${this._addonList.map(((e,t)=>s.dy`
                        <div class="checkbox-line">
                          <ha-checkbox
                            .idx=${t}
                            .checked=${e.checked}
                            @change=${this._addonChecked}
                            slot="prefix"
                          >
                          </ha-checkbox>
                          <span>
                            ${e.name}<span class="version">
                              (${e.version})
                            </span>
                          </span>
                        </div>
                      `))}
                  </div>
                `}
          ${this._dialogParams.supervisor.localize("snapshot.security")}:
          <div class="checkbox-section">
          <div class="checkbox-line">
            <ha-checkbox
              .checked=${this._snapshotHasPassword}
              @change=${this._handleCheckboxValueChanged}
              slot="prefix"
            >
            </ha-checkbox>
            <span>
            ${this._dialogParams.supervisor.localize("snapshot.password_protection")}
              </span>
            </span>
          </div>
          </div>

          ${this._snapshotHasPassword?s.dy`
                  <paper-input
                    .label=${this._dialogParams.supervisor.localize("snapshot.password")}
                    type="password"
                    name="snapshotPassword"
                    .value=${this._snapshotPassword}
                    @value-changed=${this._handleTextValueChanged}
                  >
                  </paper-input>
                `:void 0}
          ${""!==this._error?s.dy` <p class="error">${this._error}</p> `:void 0}
        <mwc-button slot="secondaryAction" @click=${this.closeDialog}>
          ${this._dialogParams.supervisor.localize("common.close")}
        </mwc-button>
        <ha-progress-button slot="primaryAction" @click=${this._createSnapshot}>
          ${this._dialogParams.supervisor.localize("snapshot.create")}
        </ha-progress-button>
      </ha-dialog>
    `:s.dy``}},{kind:"method",key:"_handleTextValueChanged",value:function(e){this[`_${e.currentTarget.name}`]=e.detail.value}},{kind:"method",key:"_handleCheckboxValueChanged",value:function(e){const t=e.currentTarget;this._snapshotHasPassword=t.checked}},{kind:"method",key:"_handleRadioValueChanged",value:function(e){const t=e.currentTarget;this[`_${t.name}`]=t.value}},{kind:"method",key:"_folderChecked",value:function(e){const{idx:t,checked:r}=e.currentTarget;this._folderList=this._folderList.map(((e,s)=>s===t?{...e,checked:r}:e))}},{kind:"method",key:"_addonChecked",value:function(e){const{idx:t,checked:r}=e.currentTarget;this._addonList=this._addonList.map(((e,s)=>s===t?{...e,checked:r}:e))}},{kind:"method",key:"_createSnapshot",value:async function(e){if("running"!==this._dialogParams.supervisor.info.state)return void(0,h.Ys)(this,{title:this._dialogParams.supervisor.localize("snapshot.could_not_create"),text:this._dialogParams.supervisor.localize("snapshot.create_blocked_not_running","state",this._dialogParams.supervisor.info.state)});const t=e.currentTarget;if(t.progress=!0,this._error="",this._snapshotHasPassword&&!this._snapshotPassword.length)return this._error=this._dialogParams.supervisor.localize("snapshot.enter_password"),void(t.progress=!1);const r=this._snapshotName||i(new Date,this.hass.locale);try{if("full"===this._snapshotType){const e={name:r};this._snapshotHasPassword&&(e.password=this._snapshotPassword),await(0,d.a2)(this.hass,e)}else{const e={name:r,folders:this._folderList.filter((e=>e.checked)).map((e=>e.slug)),addons:this._addonList.filter((e=>e.checked)).map((e=>e.slug))};this._snapshotHasPassword&&(e.password=this._snapshotPassword),await(0,d.iN)(this.hass,e)}this._dialogParams.onCreate(),this.closeDialog()}catch(e){this._error=(0,c.js)(e)}t.progress=!1}},{kind:"get",static:!0,key:"styles",value:function(){return[u.Qx,u.yu,s.iv`
        .error {
          color: var(--error-color);
        }
        paper-input[type="password"] {
          display: block;
          margin: 4px 0 4px 16px;
        }
        span.version {
          color: var(--secondary-text-color);
        }
        .checkbox-section {
          display: grid;
        }
        .checkbox-line {
          display: inline-flex;
          align-items: center;
        }
      `]}}]}}),s.oi)},8928:(e,t,r)=>{"use strict";r.d(t,{WU:()=>D});var s=/d{1,4}|M{1,4}|YY(?:YY)?|S{1,3}|Do|ZZ|Z|([HhMsDm])\1?|[aA]|"[^"]*"|'[^']*'/g,n="[1-9]\\d?",i="\\d\\d",o="[^\\s]+",a=/\[([^]*?)\]/gm;function l(e,t){for(var r=[],s=0,n=e.length;s<n;s++)r.push(e[s].substr(0,t));return r}var c=function(e){return function(t,r){var s=r[e].map((function(e){return e.toLowerCase()})).indexOf(t.toLowerCase());return s>-1?s:null}};function d(e){for(var t=[],r=1;r<arguments.length;r++)t[r-1]=arguments[r];for(var s=0,n=t;s<n.length;s++){var i=n[s];for(var o in i)e[o]=i[o]}return e}var h=["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"],u=["January","February","March","April","May","June","July","August","September","October","November","December"],p=l(u,3),f={dayNamesShort:l(h,3),dayNames:h,monthNamesShort:p,monthNames:u,amPm:["am","pm"],DoFn:function(e){return e+["th","st","nd","rd"][e%10>3?0:(e-e%10!=10?1:0)*e%10]}},m=d({},f),g=function(e,t){for(void 0===t&&(t=2),e=String(e);e.length<t;)e="0"+e;return e},v={D:function(e){return String(e.getDate())},DD:function(e){return g(e.getDate())},Do:function(e,t){return t.DoFn(e.getDate())},d:function(e){return String(e.getDay())},dd:function(e){return g(e.getDay())},ddd:function(e,t){return t.dayNamesShort[e.getDay()]},dddd:function(e,t){return t.dayNames[e.getDay()]},M:function(e){return String(e.getMonth()+1)},MM:function(e){return g(e.getMonth()+1)},MMM:function(e,t){return t.monthNamesShort[e.getMonth()]},MMMM:function(e,t){return t.monthNames[e.getMonth()]},YY:function(e){return g(String(e.getFullYear()),4).substr(2)},YYYY:function(e){return g(e.getFullYear(),4)},h:function(e){return String(e.getHours()%12||12)},hh:function(e){return g(e.getHours()%12||12)},H:function(e){return String(e.getHours())},HH:function(e){return g(e.getHours())},m:function(e){return String(e.getMinutes())},mm:function(e){return g(e.getMinutes())},s:function(e){return String(e.getSeconds())},ss:function(e){return g(e.getSeconds())},S:function(e){return String(Math.round(e.getMilliseconds()/100))},SS:function(e){return g(Math.round(e.getMilliseconds()/10),2)},SSS:function(e){return g(e.getMilliseconds(),3)},a:function(e,t){return e.getHours()<12?t.amPm[0]:t.amPm[1]},A:function(e,t){return e.getHours()<12?t.amPm[0].toUpperCase():t.amPm[1].toUpperCase()},ZZ:function(e){var t=e.getTimezoneOffset();return(t>0?"-":"+")+g(100*Math.floor(Math.abs(t)/60)+Math.abs(t)%60,4)},Z:function(e){var t=e.getTimezoneOffset();return(t>0?"-":"+")+g(Math.floor(Math.abs(t)/60),2)+":"+g(Math.abs(t)%60,2)}},y=function(e){return+e-1},k=[null,n],_=[null,o],b=["isPm",o,function(e,t){var r=e.toLowerCase();return r===t.amPm[0]?0:r===t.amPm[1]?1:null}],w=["timezoneOffset","[^\\s]*?[\\+\\-]\\d\\d:?\\d\\d|[^\\s]*?Z?",function(e){var t=(e+"").match(/([+-]|\d\d)/gi);if(t){var r=60*+t[1]+parseInt(t[2],10);return"+"===t[0]?r:-r}return 0}],P=(c("monthNamesShort"),c("monthNames"),{default:"ddd MMM DD YYYY HH:mm:ss",shortDate:"M/D/YY",mediumDate:"MMM D, YYYY",longDate:"MMMM D, YYYY",fullDate:"dddd, MMMM D, YYYY",isoDate:"YYYY-MM-DD",isoDateTime:"YYYY-MM-DDTHH:mm:ssZ",shortTime:"HH:mm",mediumTime:"HH:mm:ss",longTime:"HH:mm:ss.SSS"}),D=function(e,t,r){if(void 0===t&&(t=P.default),void 0===r&&(r={}),"number"==typeof e&&(e=new Date(e)),"[object Date]"!==Object.prototype.toString.call(e)||isNaN(e.getTime()))throw new Error("Invalid Date pass to format");var n=[];t=(t=P[t]||t).replace(a,(function(e,t){return n.push(t),"@@@"}));var i=d(d({},m),r);return(t=t.replace(s,(function(t){return v[t](e,i)}))).replace(/@@@/g,(function(){return n.shift()}))}},3274:(e,t,r)=>{"use strict";r.d(t,{Sb:()=>s,Op:()=>n});const s=function(){try{(new Date).toLocaleDateString("i")}catch(e){return"RangeError"===e.name}return!1}(),n=(function(){try{(new Date).toLocaleTimeString("i")}catch(e){return"RangeError"===e.name}}(),function(){try{(new Date).toLocaleString("i")}catch(e){return"RangeError"===e.name}return!1}())}}]);
//# sourceMappingURL=chunk.abc357af16dfcce65da8.js.map