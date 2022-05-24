"use strict";(self.webpackChunkhome_assistant_frontend=self.webpackChunkhome_assistant_frontend||[]).push([[595],{1595:(e,t,r)=>{r.a(e,(async e=>{var t=r(7500),i=r(3550),n=r(3864),o=r(2198),a=r(4583),s=(r(2511),r(3927),r(260),r(7712),e([o,a]));function l(){l=function(){return e};var e={elementsDefinitionOrder:[["method"],["field"]],initializeInstanceElements:function(e,t){["method","field"].forEach((function(r){t.forEach((function(t){t.kind===r&&"own"===t.placement&&this.defineClassElement(e,t)}),this)}),this)},initializeClassElements:function(e,t){var r=e.prototype;["method","field"].forEach((function(i){t.forEach((function(t){var n=t.placement;if(t.kind===i&&("static"===n||"prototype"===n)){var o="static"===n?e:r;this.defineClassElement(o,t)}}),this)}),this)},defineClassElement:function(e,t){var r=t.descriptor;if("field"===t.kind){var i=t.initializer;r={enumerable:r.enumerable,writable:r.writable,configurable:r.configurable,value:void 0===i?void 0:i.call(e)}}Object.defineProperty(e,t.key,r)},decorateClass:function(e,t){var r=[],i=[],n={static:[],prototype:[],own:[]};if(e.forEach((function(e){this.addElementPlacement(e,n)}),this),e.forEach((function(e){if(!p(e))return r.push(e);var t=this.decorateElement(e,n);r.push(t.element),r.push.apply(r,t.extras),i.push.apply(i,t.finishers)}),this),!t)return{elements:r,finishers:i};var o=this.decorateConstructor(r,t);return i.push.apply(i,o.finishers),o.finishers=i,o},addElementPlacement:function(e,t,r){var i=t[e.placement];if(!r&&-1!==i.indexOf(e.key))throw new TypeError("Duplicated element ("+e.key+")");i.push(e.key)},decorateElement:function(e,t){for(var r=[],i=[],n=e.decorators,o=n.length-1;o>=0;o--){var a=t[e.placement];a.splice(a.indexOf(e.key),1);var s=this.fromElementDescriptor(e),l=this.toElementFinisherExtras((0,n[o])(s)||s);e=l.element,this.addElementPlacement(e,t),l.finisher&&i.push(l.finisher);var c=l.extras;if(c){for(var d=0;d<c.length;d++)this.addElementPlacement(c[d],t);r.push.apply(r,c)}}return{element:e,finishers:i,extras:r}},decorateConstructor:function(e,t){for(var r=[],i=t.length-1;i>=0;i--){var n=this.fromClassDescriptor(e),o=this.toClassDescriptor((0,t[i])(n)||n);if(void 0!==o.finisher&&r.push(o.finisher),void 0!==o.elements){e=o.elements;for(var a=0;a<e.length-1;a++)for(var s=a+1;s<e.length;s++)if(e[a].key===e[s].key&&e[a].placement===e[s].placement)throw new TypeError("Duplicated element ("+e[a].key+")")}}return{elements:e,finishers:r}},fromElementDescriptor:function(e){var t={kind:e.kind,key:e.key,placement:e.placement,descriptor:e.descriptor};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),"field"===e.kind&&(t.initializer=e.initializer),t},toElementDescriptors:function(e){var t;if(void 0!==e)return(t=e,function(e){if(Array.isArray(e))return e}(t)||function(e){if("undefined"!=typeof Symbol&&null!=e[Symbol.iterator]||null!=e["@@iterator"])return Array.from(e)}(t)||function(e,t){if(e){if("string"==typeof e)return m(e,t);var r=Object.prototype.toString.call(e).slice(8,-1);return"Object"===r&&e.constructor&&(r=e.constructor.name),"Map"===r||"Set"===r?Array.from(e):"Arguments"===r||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(r)?m(e,t):void 0}}(t)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()).map((function(e){var t=this.toElementDescriptor(e);return this.disallowProperty(e,"finisher","An element descriptor"),this.disallowProperty(e,"extras","An element descriptor"),t}),this)},toElementDescriptor:function(e){var t=String(e.kind);if("method"!==t&&"field"!==t)throw new TypeError('An element descriptor\'s .kind property must be either "method" or "field", but a decorator created an element descriptor with .kind "'+t+'"');var r=f(e.key),i=String(e.placement);if("static"!==i&&"prototype"!==i&&"own"!==i)throw new TypeError('An element descriptor\'s .placement property must be one of "static", "prototype" or "own", but a decorator created an element descriptor with .placement "'+i+'"');var n=e.descriptor;this.disallowProperty(e,"elements","An element descriptor");var o={kind:t,key:r,placement:i,descriptor:Object.assign({},n)};return"field"!==t?this.disallowProperty(e,"initializer","A method descriptor"):(this.disallowProperty(n,"get","The property descriptor of a field descriptor"),this.disallowProperty(n,"set","The property descriptor of a field descriptor"),this.disallowProperty(n,"value","The property descriptor of a field descriptor"),o.initializer=e.initializer),o},toElementFinisherExtras:function(e){return{element:this.toElementDescriptor(e),finisher:h(e,"finisher"),extras:this.toElementDescriptors(e.extras)}},fromClassDescriptor:function(e){var t={kind:"class",elements:e.map(this.fromElementDescriptor,this)};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),t},toClassDescriptor:function(e){var t=String(e.kind);if("class"!==t)throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator created a class descriptor with .kind "'+t+'"');this.disallowProperty(e,"key","A class descriptor"),this.disallowProperty(e,"placement","A class descriptor"),this.disallowProperty(e,"descriptor","A class descriptor"),this.disallowProperty(e,"initializer","A class descriptor"),this.disallowProperty(e,"extras","A class descriptor");var r=h(e,"finisher");return{elements:this.toElementDescriptors(e.elements),finisher:r}},runClassFinishers:function(e,t){for(var r=0;r<t.length;r++){var i=(0,t[r])(e);if(void 0!==i){if("function"!=typeof i)throw new TypeError("Finishers must return a constructor.");e=i}}return e},disallowProperty:function(e,t,r){if(void 0!==e[t])throw new TypeError(r+" can't have a ."+t+" property.")}};return e}function c(e){var t,r=f(e.key);"method"===e.kind?t={value:e.value,writable:!0,configurable:!0,enumerable:!1}:"get"===e.kind?t={get:e.value,configurable:!0,enumerable:!1}:"set"===e.kind?t={set:e.value,configurable:!0,enumerable:!1}:"field"===e.kind&&(t={configurable:!0,writable:!0,enumerable:!0});var i={kind:"field"===e.kind?"field":"method",key:r,placement:e.static?"static":"field"===e.kind?"own":"prototype",descriptor:t};return e.decorators&&(i.decorators=e.decorators),"field"===e.kind&&(i.initializer=e.value),i}function d(e,t){void 0!==e.descriptor.get?t.descriptor.get=e.descriptor.get:t.descriptor.set=e.descriptor.set}function p(e){return e.decorators&&e.decorators.length}function u(e){return void 0!==e&&!(void 0===e.value&&void 0===e.writable)}function h(e,t){var r=e[t];if(void 0!==r&&"function"!=typeof r)throw new TypeError("Expected '"+t+"' to be a function");return r}function f(e){var t=function(e,t){if("object"!=typeof e||null===e)return e;var r=e[Symbol.toPrimitive];if(void 0!==r){var i=r.call(e,t||"default");if("object"!=typeof i)return i;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===t?String:Number)(e)}(e,"string");return"symbol"==typeof t?t:String(t)}function m(e,t){(null==t||t>e.length)&&(t=e.length);for(var r=0,i=new Array(t);r<t;r++)i[r]=e[r];return i}function v(e,t,r){return v="undefined"!=typeof Reflect&&Reflect.get?Reflect.get:function(e,t,r){var i=function(e,t){for(;!Object.prototype.hasOwnProperty.call(e,t)&&null!==(e=y(e)););return e}(e,t);if(i){var n=Object.getOwnPropertyDescriptor(i,t);return n.get?n.get.call(r):n.value}},v(e,t,r||e)}function y(e){return y=Object.setPrototypeOf?Object.getPrototypeOf:function(e){return e.__proto__||Object.getPrototypeOf(e)},y(e)}[o,a]=s.then?await s:s;const k="M10,4H4C2.89,4 2,4.89 2,6V18A2,2 0 0,0 4,20H20A2,2 0 0,0 22,18V8C22,6.89 21.1,6 20,6H12L10,4Z",b="M20.5,11H19V7C19,5.89 18.1,5 17,5H13V3.5A2.5,2.5 0 0,0 10.5,1A2.5,2.5 0 0,0 8,3.5V5H4A2,2 0 0,0 2,7V10.8H3.5C5,10.8 6.2,12 6.2,13.5C6.2,15 5,16.2 3.5,16.2H2V20A2,2 0 0,0 4,22H7.8V20.5C7.8,19 9,17.8 10.5,17.8C12,17.8 13.2,19 13.2,20.5V22H17A2,2 0 0,0 19,20V16H20.5A2.5,2.5 0 0,0 23,13.5A2.5,2.5 0 0,0 20.5,11Z";!function(e,t,r,i){var n=l();if(i)for(var o=0;o<i.length;o++)n=i[o](n);var a=t((function(e){n.initializeInstanceElements(e,s.elements)}),r),s=n.decorateClass(function(e){for(var t=[],r=function(e){return"method"===e.kind&&e.key===o.key&&e.placement===o.placement},i=0;i<e.length;i++){var n,o=e[i];if("method"===o.kind&&(n=t.find(r)))if(u(o.descriptor)||u(n.descriptor)){if(p(o)||p(n))throw new ReferenceError("Duplicated methods ("+o.key+") can't be decorated.");n.descriptor=o.descriptor}else{if(p(o)){if(p(n))throw new ReferenceError("Decorators can't be placed on different accessors with for the same property ("+o.key+").");n.decorators=o.decorators}d(o,n)}else t.push(o)}return t}(a.d.map(c)),e);n.initializeClassElements(a.F,s.elements),n.runClassFinishers(a.F,s.finishers)}([(0,i.Mo)("supervisor-backup-content")],(function(e,r){class s extends r{constructor(...t){super(...t),e(this)}}return{F:s,d:[{kind:"field",decorators:[(0,i.Cb)({attribute:!1})],key:"hass",value:void 0},{kind:"field",decorators:[(0,i.Cb)()],key:"localize",value:void 0},{kind:"field",decorators:[(0,i.Cb)({attribute:!1})],key:"supervisor",value:void 0},{kind:"field",decorators:[(0,i.Cb)({attribute:!1})],key:"backup",value:void 0},{kind:"field",decorators:[(0,i.Cb)()],key:"backupType",value:()=>"full"},{kind:"field",decorators:[(0,i.Cb)({attribute:!1})],key:"folders",value:void 0},{kind:"field",decorators:[(0,i.Cb)({attribute:!1})],key:"addons",value:void 0},{kind:"field",decorators:[(0,i.Cb)({type:Boolean})],key:"homeAssistant",value:()=>!1},{kind:"field",decorators:[(0,i.Cb)({type:Boolean})],key:"backupHasPassword",value:()=>!1},{kind:"field",decorators:[(0,i.Cb)({type:Boolean})],key:"onboarding",value:()=>!1},{kind:"field",decorators:[(0,i.Cb)()],key:"backupName",value:()=>""},{kind:"field",decorators:[(0,i.Cb)()],key:"backupPassword",value:()=>""},{kind:"field",decorators:[(0,i.Cb)()],key:"confirmBackupPassword",value:()=>""},{kind:"field",decorators:[(0,i.IO)("paper-input, ha-radio, ha-checkbox",!0)],key:"_focusTarget",value:void 0},{kind:"method",key:"willUpdate",value:function(e){var t,r,i,n;(v(y(s.prototype),"willUpdate",this).call(this,e),this.hasUpdated)||(this.folders=(e=>{const t=[];return e.includes("ssl")&&t.push({slug:"ssl",name:"SSL",checked:!1}),e.includes("share")&&t.push({slug:"share",name:"Share",checked:!1}),e.includes("media")&&t.push({slug:"media",name:"Media",checked:!1}),e.includes("addons/local")&&t.push({slug:"addons/local",name:"Local add-ons",checked:!1}),t.sort(((e,t)=>e.name>t.name?1:-1))})(this.backup?this.backup.folders:["ssl","share","media","addons/local"]),this.addons=(this.backup?this.backup.addons:null===(t=this.supervisor)||void 0===t?void 0:t.supervisor.addons).map((e=>({slug:e.slug,name:e.name,version:e.version,checked:!1}))).sort(((e,t)=>e.name>t.name?1:-1)),this.backupType=(null===(r=this.backup)||void 0===r?void 0:r.type)||"full",this.backupName=(null===(i=this.backup)||void 0===i?void 0:i.name)||"",this.backupHasPassword=(null===(n=this.backup)||void 0===n?void 0:n.protected)||!1)}},{kind:"method",key:"focus",value:function(){var e;null===(e=this._focusTarget)||void 0===e||e.focus()}},{kind:"field",key:"_localize",value(){return e=>{var t;return(null===(t=this.supervisor)||void 0===t?void 0:t.localize(`backup.${e}`))||this.localize(`ui.panel.page-onboarding.restore.${e}`)}}},{kind:"method",key:"render",value:function(){if(!this.onboarding&&!this.supervisor)return t.dy``;const e="partial"===this.backupType?this._getSection("folders"):void 0,r="partial"===this.backupType?this._getSection("addons"):void 0;return t.dy`
      ${this.backup?t.dy`<div class="details">
            ${"full"===this.backup.type?this._localize("full_backup"):this._localize("partial_backup")}
            (${Math.ceil(10*this.backup.size)/10+" MB"})<br />
            ${this.hass?(0,a.o0)(new Date(this.backup.date),this.hass.locale):this.backup.date}
          </div>`:t.dy`<paper-input
            name="backupName"
            .label=${this._localize("name")}
            .value=${this.backupName}
            @value-changed=${this._handleTextValueChanged}
          >
          </paper-input>`}
      ${this.backup&&"full"!==this.backup.type?"":t.dy`<div class="sub-header">
              ${this.backup?this._localize("select_type"):this._localize("type")}
            </div>
            <div class="backup-types">
              <ha-formfield .label=${this._localize("full_backup")}>
                <ha-radio
                  @change=${this._handleRadioValueChanged}
                  value="full"
                  name="backupType"
                  .checked=${"full"===this.backupType}
                >
                </ha-radio>
              </ha-formfield>
              <ha-formfield .label=${this._localize("partial_backup")}>
                <ha-radio
                  @change=${this._handleRadioValueChanged}
                  value="partial"
                  name="backupType"
                  .checked=${"partial"===this.backupType}
                >
                </ha-radio>
              </ha-formfield>
            </div>`}
      ${"partial"===this.backupType?t.dy`<div class="partial-picker">
            <ha-formfield
              .label=${t.dy`<supervisor-formfield-label
                label="Home Assistant"
                .iconPath=${"M21.8,13H20V21H13V17.67L15.79,14.88L16.5,15C17.66,15 18.6,14.06 18.6,12.9C18.6,11.74 17.66,10.8 16.5,10.8A2.1,2.1 0 0,0 14.4,12.9L14.5,13.61L13,15.13V9.65C13.66,9.29 14.1,8.6 14.1,7.8A2.1,2.1 0 0,0 12,5.7A2.1,2.1 0 0,0 9.9,7.8C9.9,8.6 10.34,9.29 11,9.65V15.13L9.5,13.61L9.6,12.9A2.1,2.1 0 0,0 7.5,10.8A2.1,2.1 0 0,0 5.4,12.9A2.1,2.1 0 0,0 7.5,15L8.21,14.88L11,17.67V21H4V13H2.25C1.83,13 1.42,13 1.42,12.79C1.43,12.57 1.85,12.15 2.28,11.72L11,3C11.33,2.67 11.67,2.33 12,2.33C12.33,2.33 12.67,2.67 13,3L17,7V6H19V9L21.78,11.78C22.18,12.18 22.59,12.59 22.6,12.8C22.6,13 22.2,13 21.8,13M7.5,12A0.9,0.9 0 0,1 8.4,12.9A0.9,0.9 0 0,1 7.5,13.8A0.9,0.9 0 0,1 6.6,12.9A0.9,0.9 0 0,1 7.5,12M16.5,12C17,12 17.4,12.4 17.4,12.9C17.4,13.4 17,13.8 16.5,13.8A0.9,0.9 0 0,1 15.6,12.9A0.9,0.9 0 0,1 16.5,12M12,6.9C12.5,6.9 12.9,7.3 12.9,7.8C12.9,8.3 12.5,8.7 12,8.7C11.5,8.7 11.1,8.3 11.1,7.8C11.1,7.3 11.5,6.9 12,6.9Z"}
                .version=${this.backup?this.backup.homeassistant:this.hass.config.version}
              >
              </supervisor-formfield-label>`}
            >
              <ha-checkbox
                .checked=${this.homeAssistant}
                @change=${this.toggleHomeAssistant}
              >
              </ha-checkbox>
            </ha-formfield>

            ${null!=e&&e.templates.length?t.dy`
                  <ha-formfield
                    .label=${t.dy`<supervisor-formfield-label
                      .label=${this._localize("folders")}
                      .iconPath=${k}
                    >
                    </supervisor-formfield-label>`}
                  >
                    <ha-checkbox
                      @change=${this._toggleSection}
                      .checked=${e.checked}
                      .indeterminate=${e.indeterminate}
                      .section=${"folders"}
                    >
                    </ha-checkbox>
                  </ha-formfield>
                  <div class="section-content">${e.templates}</div>
                `:""}
            ${null!=r&&r.templates.length?t.dy`
                  <ha-formfield
                    .label=${t.dy`<supervisor-formfield-label
                      .label=${this._localize("addons")}
                      .iconPath=${b}
                    >
                    </supervisor-formfield-label>`}
                  >
                    <ha-checkbox
                      @change=${this._toggleSection}
                      .checked=${r.checked}
                      .indeterminate=${r.indeterminate}
                      .section=${"addons"}
                    >
                    </ha-checkbox>
                  </ha-formfield>
                  <div class="section-content">${r.templates}</div>
                `:""}
          </div> `:""}
      ${"partial"!==this.backupType||this.backup&&!this.backupHasPassword?"":t.dy`<hr />`}
      ${this.backup?"":t.dy`<ha-formfield
            class="password"
            .label=${this._localize("password_protection")}
          >
            <ha-checkbox
              .checked=${this.backupHasPassword}
              @change=${this._toggleHasPassword}
            >
            </ha-checkbox>
          </ha-formfield>`}
      ${this.backupHasPassword?t.dy`
            <paper-input
              .label=${this._localize("password")}
              type="password"
              name="backupPassword"
              .value=${this.backupPassword}
              @value-changed=${this._handleTextValueChanged}
            >
            </paper-input>
            ${this.backup?"":t.dy` <paper-input
                  .label=${this._localize("confirm_password")}
                  type="password"
                  name="confirmBackupPassword"
                  .value=${this.confirmBackupPassword}
                  @value-changed=${this._handleTextValueChanged}
                >
                </paper-input>`}
          `:""}
    `}},{kind:"method",key:"toggleHomeAssistant",value:function(){this.homeAssistant=!this.homeAssistant}},{kind:"get",static:!0,key:"styles",value:function(){return t.iv`
      .partial-picker ha-formfield {
        display: block;
      }
      .partial-picker ha-checkbox {
        --mdc-checkbox-touch-target-size: 32px;
      }
      .partial-picker {
        display: block;
        margin: 0px -6px;
      }
      supervisor-formfield-label {
        display: inline-flex;
        align-items: center;
      }
      hr {
        border-color: var(--divider-color);
        border-bottom: none;
        margin: 16px 0;
      }
      .details {
        color: var(--secondary-text-color);
      }
      .section-content {
        display: flex;
        flex-direction: column;
        margin-left: 30px;
      }
      ha-formfield.password {
        display: block;
        margin: 0 -14px -16px;
      }
      .backup-types {
        display: flex;
        margin-left: -13px;
      }
      .sub-header {
        margin-top: 8px;
      }
    `}},{kind:"method",key:"backupDetails",value:function(){var e,t;const r={};if(this.backup||(r.name=this.backupName||(0,o.p6)(new Date,this.hass.locale)),this.backupHasPassword&&(r.password=this.backupPassword,this.backup||(r.confirm_password=this.confirmBackupPassword)),"full"===this.backupType)return r;const i=null===(e=this.addons)||void 0===e?void 0:e.filter((e=>e.checked)).map((e=>e.slug)),n=null===(t=this.folders)||void 0===t?void 0:t.filter((e=>e.checked)).map((e=>e.slug));return null!=i&&i.length&&(r.addons=i),null!=n&&n.length&&(r.folders=n),r.homeassistant=this.homeAssistant,r}},{kind:"method",key:"_getSection",value:function(e){var r;const i=[],o="addons"===e?new Map(null===(r=this.supervisor)||void 0===r?void 0:r.addon.addons.map((e=>[e.slug,e]))):void 0;let a=0;this[e].forEach((r=>{var s;i.push(t.dy`<ha-formfield
        .label=${t.dy`<supervisor-formfield-label
          .label=${r.name}
          .iconPath=${"addons"===e?b:k}
          .imageUrl=${"addons"===e&&!this.onboarding&&(0,n.I)(this.hass.config.version,0,105)&&null!=o&&null!==(s=o.get(r.slug))&&void 0!==s&&s.icon?`/api/hassio/addons/${r.slug}/icon`:void 0}
          .version=${r.version}
        >
        </supervisor-formfield-label>`}
      >
        <ha-checkbox
          .item=${r}
          .checked=${r.checked}
          .section=${e}
          @change=${this._updateSectionEntry}
        >
        </ha-checkbox>
      </ha-formfield>`),r.checked&&a++}));const s=a===this[e].length;return{templates:i,checked:s,indeterminate:!s&&0!==a}}},{kind:"method",key:"_handleRadioValueChanged",value:function(e){const t=e.currentTarget;this[t.name]=t.value}},{kind:"method",key:"_handleTextValueChanged",value:function(e){this[e.currentTarget.name]=e.detail.value}},{kind:"method",key:"_toggleHasPassword",value:function(){this.backupHasPassword=!this.backupHasPassword}},{kind:"method",key:"_toggleSection",value:function(e){const t=e.currentTarget.section;this[t]=("addons"===t?this.addons:this.folders).map((t=>({...t,checked:e.currentTarget.checked})))}},{kind:"method",key:"_updateSectionEntry",value:function(e){const t=e.currentTarget.item,r=e.currentTarget.section;this[r]=this[r].map((r=>r.slug===t.slug?{...r,checked:e.currentTarget.checked}:r))}}]}}),t.oi)}))},7712:(e,t,r)=>{var i=r(7500),n=r(3550);r(2039);function o(){o=function(){return e};var e={elementsDefinitionOrder:[["method"],["field"]],initializeInstanceElements:function(e,t){["method","field"].forEach((function(r){t.forEach((function(t){t.kind===r&&"own"===t.placement&&this.defineClassElement(e,t)}),this)}),this)},initializeClassElements:function(e,t){var r=e.prototype;["method","field"].forEach((function(i){t.forEach((function(t){var n=t.placement;if(t.kind===i&&("static"===n||"prototype"===n)){var o="static"===n?e:r;this.defineClassElement(o,t)}}),this)}),this)},defineClassElement:function(e,t){var r=t.descriptor;if("field"===t.kind){var i=t.initializer;r={enumerable:r.enumerable,writable:r.writable,configurable:r.configurable,value:void 0===i?void 0:i.call(e)}}Object.defineProperty(e,t.key,r)},decorateClass:function(e,t){var r=[],i=[],n={static:[],prototype:[],own:[]};if(e.forEach((function(e){this.addElementPlacement(e,n)}),this),e.forEach((function(e){if(!l(e))return r.push(e);var t=this.decorateElement(e,n);r.push(t.element),r.push.apply(r,t.extras),i.push.apply(i,t.finishers)}),this),!t)return{elements:r,finishers:i};var o=this.decorateConstructor(r,t);return i.push.apply(i,o.finishers),o.finishers=i,o},addElementPlacement:function(e,t,r){var i=t[e.placement];if(!r&&-1!==i.indexOf(e.key))throw new TypeError("Duplicated element ("+e.key+")");i.push(e.key)},decorateElement:function(e,t){for(var r=[],i=[],n=e.decorators,o=n.length-1;o>=0;o--){var a=t[e.placement];a.splice(a.indexOf(e.key),1);var s=this.fromElementDescriptor(e),l=this.toElementFinisherExtras((0,n[o])(s)||s);e=l.element,this.addElementPlacement(e,t),l.finisher&&i.push(l.finisher);var c=l.extras;if(c){for(var d=0;d<c.length;d++)this.addElementPlacement(c[d],t);r.push.apply(r,c)}}return{element:e,finishers:i,extras:r}},decorateConstructor:function(e,t){for(var r=[],i=t.length-1;i>=0;i--){var n=this.fromClassDescriptor(e),o=this.toClassDescriptor((0,t[i])(n)||n);if(void 0!==o.finisher&&r.push(o.finisher),void 0!==o.elements){e=o.elements;for(var a=0;a<e.length-1;a++)for(var s=a+1;s<e.length;s++)if(e[a].key===e[s].key&&e[a].placement===e[s].placement)throw new TypeError("Duplicated element ("+e[a].key+")")}}return{elements:e,finishers:r}},fromElementDescriptor:function(e){var t={kind:e.kind,key:e.key,placement:e.placement,descriptor:e.descriptor};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),"field"===e.kind&&(t.initializer=e.initializer),t},toElementDescriptors:function(e){var t;if(void 0!==e)return(t=e,function(e){if(Array.isArray(e))return e}(t)||function(e){if("undefined"!=typeof Symbol&&null!=e[Symbol.iterator]||null!=e["@@iterator"])return Array.from(e)}(t)||function(e,t){if(e){if("string"==typeof e)return u(e,t);var r=Object.prototype.toString.call(e).slice(8,-1);return"Object"===r&&e.constructor&&(r=e.constructor.name),"Map"===r||"Set"===r?Array.from(e):"Arguments"===r||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(r)?u(e,t):void 0}}(t)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()).map((function(e){var t=this.toElementDescriptor(e);return this.disallowProperty(e,"finisher","An element descriptor"),this.disallowProperty(e,"extras","An element descriptor"),t}),this)},toElementDescriptor:function(e){var t=String(e.kind);if("method"!==t&&"field"!==t)throw new TypeError('An element descriptor\'s .kind property must be either "method" or "field", but a decorator created an element descriptor with .kind "'+t+'"');var r=p(e.key),i=String(e.placement);if("static"!==i&&"prototype"!==i&&"own"!==i)throw new TypeError('An element descriptor\'s .placement property must be one of "static", "prototype" or "own", but a decorator created an element descriptor with .placement "'+i+'"');var n=e.descriptor;this.disallowProperty(e,"elements","An element descriptor");var o={kind:t,key:r,placement:i,descriptor:Object.assign({},n)};return"field"!==t?this.disallowProperty(e,"initializer","A method descriptor"):(this.disallowProperty(n,"get","The property descriptor of a field descriptor"),this.disallowProperty(n,"set","The property descriptor of a field descriptor"),this.disallowProperty(n,"value","The property descriptor of a field descriptor"),o.initializer=e.initializer),o},toElementFinisherExtras:function(e){return{element:this.toElementDescriptor(e),finisher:d(e,"finisher"),extras:this.toElementDescriptors(e.extras)}},fromClassDescriptor:function(e){var t={kind:"class",elements:e.map(this.fromElementDescriptor,this)};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),t},toClassDescriptor:function(e){var t=String(e.kind);if("class"!==t)throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator created a class descriptor with .kind "'+t+'"');this.disallowProperty(e,"key","A class descriptor"),this.disallowProperty(e,"placement","A class descriptor"),this.disallowProperty(e,"descriptor","A class descriptor"),this.disallowProperty(e,"initializer","A class descriptor"),this.disallowProperty(e,"extras","A class descriptor");var r=d(e,"finisher");return{elements:this.toElementDescriptors(e.elements),finisher:r}},runClassFinishers:function(e,t){for(var r=0;r<t.length;r++){var i=(0,t[r])(e);if(void 0!==i){if("function"!=typeof i)throw new TypeError("Finishers must return a constructor.");e=i}}return e},disallowProperty:function(e,t,r){if(void 0!==e[t])throw new TypeError(r+" can't have a ."+t+" property.")}};return e}function a(e){var t,r=p(e.key);"method"===e.kind?t={value:e.value,writable:!0,configurable:!0,enumerable:!1}:"get"===e.kind?t={get:e.value,configurable:!0,enumerable:!1}:"set"===e.kind?t={set:e.value,configurable:!0,enumerable:!1}:"field"===e.kind&&(t={configurable:!0,writable:!0,enumerable:!0});var i={kind:"field"===e.kind?"field":"method",key:r,placement:e.static?"static":"field"===e.kind?"own":"prototype",descriptor:t};return e.decorators&&(i.decorators=e.decorators),"field"===e.kind&&(i.initializer=e.value),i}function s(e,t){void 0!==e.descriptor.get?t.descriptor.get=e.descriptor.get:t.descriptor.set=e.descriptor.set}function l(e){return e.decorators&&e.decorators.length}function c(e){return void 0!==e&&!(void 0===e.value&&void 0===e.writable)}function d(e,t){var r=e[t];if(void 0!==r&&"function"!=typeof r)throw new TypeError("Expected '"+t+"' to be a function");return r}function p(e){var t=function(e,t){if("object"!=typeof e||null===e)return e;var r=e[Symbol.toPrimitive];if(void 0!==r){var i=r.call(e,t||"default");if("object"!=typeof i)return i;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===t?String:Number)(e)}(e,"string");return"symbol"==typeof t?t:String(t)}function u(e,t){(null==t||t>e.length)&&(t=e.length);for(var r=0,i=new Array(t);r<t;r++)i[r]=e[r];return i}!function(e,t,r,i){var n=o();if(i)for(var d=0;d<i.length;d++)n=i[d](n);var p=t((function(e){n.initializeInstanceElements(e,u.elements)}),r),u=n.decorateClass(function(e){for(var t=[],r=function(e){return"method"===e.kind&&e.key===o.key&&e.placement===o.placement},i=0;i<e.length;i++){var n,o=e[i];if("method"===o.kind&&(n=t.find(r)))if(c(o.descriptor)||c(n.descriptor)){if(l(o)||l(n))throw new ReferenceError("Duplicated methods ("+o.key+") can't be decorated.");n.descriptor=o.descriptor}else{if(l(o)){if(l(n))throw new ReferenceError("Decorators can't be placed on different accessors with for the same property ("+o.key+").");n.decorators=o.decorators}s(o,n)}else t.push(o)}return t}(p.d.map(a)),e);n.initializeClassElements(p.F,u.elements),n.runClassFinishers(p.F,u.finishers)}([(0,n.Mo)("supervisor-formfield-label")],(function(e,t){return{F:class extends t{constructor(...t){super(...t),e(this)}},d:[{kind:"field",decorators:[(0,n.Cb)({type:String})],key:"label",value:void 0},{kind:"field",decorators:[(0,n.Cb)({type:String})],key:"imageUrl",value:void 0},{kind:"field",decorators:[(0,n.Cb)({type:String})],key:"iconPath",value:void 0},{kind:"field",decorators:[(0,n.Cb)({type:String})],key:"version",value:void 0},{kind:"method",key:"render",value:function(){return i.dy`
      ${this.imageUrl?i.dy`<img loading="lazy" .src=${this.imageUrl} class="icon" />`:this.iconPath?i.dy`<ha-svg-icon .path=${this.iconPath} class="icon"></ha-svg-icon>`:""}
      <span class="label">${this.label}</span>
      ${this.version?i.dy`<span class="version">(${this.version})</span>`:""}
    `}},{kind:"get",static:!0,key:"styles",value:function(){return i.iv`
      :host {
        display: flex;
        align-items: center;
      }
      .label {
        margin-right: 4px;
      }
      .version {
        color: var(--secondary-text-color);
      }
      .icon {
        max-height: 22px;
        max-width: 22px;
        margin-right: 8px;
      }
    `}}]}}),i.oi)},2198:(e,t,r)=>{r.a(e,(async e=>{r.d(t,{p6:()=>o,WB:()=>s});var i=r(4516),n=r(4121);n.Xp&&await n.Xp;(0,i.Z)((e=>new Intl.DateTimeFormat(e.language,{weekday:"long",month:"long",day:"numeric"})));const o=(e,t)=>a(t).format(e),a=(0,i.Z)((e=>new Intl.DateTimeFormat(e.language,{year:"numeric",month:"long",day:"numeric"}))),s=(e,t)=>l(t).format(e),l=(0,i.Z)((e=>new Intl.DateTimeFormat(e.language,{year:"numeric",month:"numeric",day:"numeric"})));(0,i.Z)((e=>new Intl.DateTimeFormat(e.language,{day:"numeric",month:"short"}))),(0,i.Z)((e=>new Intl.DateTimeFormat(e.language,{month:"long",year:"numeric"}))),(0,i.Z)((e=>new Intl.DateTimeFormat(e.language,{month:"long"}))),(0,i.Z)((e=>new Intl.DateTimeFormat(e.language,{year:"numeric"})));e()}),1)}}]);
//# sourceMappingURL=e6d89b8d.js.map