"use strict";(self.webpackChunkhome_assistant_frontend=self.webpackChunkhome_assistant_frontend||[]).push([[419],{2141:(e,t,i)=>{function r(e){return void 0===e||Array.isArray(e)?e:[e]}i.d(t,{r:()=>r})},95:(e,t,i)=>{i.d(t,{e:()=>r,f:()=>n});const r=(e,t)=>n(e.attributes,t),n=(e,t)=>0!=(e.supported_features&t)},5033:(e,t,i)=>{i.r(t),i.d(t,{HaTargetSelector:()=>M});var r=i(7500),n=i(3550),o=i(4516),s=i(7292),a=i(4186),d=i(715),c=i(3855),l=i(3826),p=i(7182),h=(i(1187),i(4444),i(8636)),u=i(7181),f=i(2141),v=i(8831),m=i(1741),y=i(7066);i(33),i(6647),i(8101),i(6255),i(6235),i(2039);function k(){k=function(){return e};var e={elementsDefinitionOrder:[["method"],["field"]],initializeInstanceElements:function(e,t){["method","field"].forEach((function(i){t.forEach((function(t){t.kind===i&&"own"===t.placement&&this.defineClassElement(e,t)}),this)}),this)},initializeClassElements:function(e,t){var i=e.prototype;["method","field"].forEach((function(r){t.forEach((function(t){var n=t.placement;if(t.kind===r&&("static"===n||"prototype"===n)){var o="static"===n?e:i;this.defineClassElement(o,t)}}),this)}),this)},defineClassElement:function(e,t){var i=t.descriptor;if("field"===t.kind){var r=t.initializer;i={enumerable:i.enumerable,writable:i.writable,configurable:i.configurable,value:void 0===r?void 0:r.call(e)}}Object.defineProperty(e,t.key,i)},decorateClass:function(e,t){var i=[],r=[],n={static:[],prototype:[],own:[]};if(e.forEach((function(e){this.addElementPlacement(e,n)}),this),e.forEach((function(e){if(!b(e))return i.push(e);var t=this.decorateElement(e,n);i.push(t.element),i.push.apply(i,t.extras),r.push.apply(r,t.finishers)}),this),!t)return{elements:i,finishers:r};var o=this.decorateConstructor(i,t);return r.push.apply(r,o.finishers),o.finishers=r,o},addElementPlacement:function(e,t,i){var r=t[e.placement];if(!i&&-1!==r.indexOf(e.key))throw new TypeError("Duplicated element ("+e.key+")");r.push(e.key)},decorateElement:function(e,t){for(var i=[],r=[],n=e.decorators,o=n.length-1;o>=0;o--){var s=t[e.placement];s.splice(s.indexOf(e.key),1);var a=this.fromElementDescriptor(e),d=this.toElementFinisherExtras((0,n[o])(a)||a);e=d.element,this.addElementPlacement(e,t),d.finisher&&r.push(d.finisher);var c=d.extras;if(c){for(var l=0;l<c.length;l++)this.addElementPlacement(c[l],t);i.push.apply(i,c)}}return{element:e,finishers:r,extras:i}},decorateConstructor:function(e,t){for(var i=[],r=t.length-1;r>=0;r--){var n=this.fromClassDescriptor(e),o=this.toClassDescriptor((0,t[r])(n)||n);if(void 0!==o.finisher&&i.push(o.finisher),void 0!==o.elements){e=o.elements;for(var s=0;s<e.length-1;s++)for(var a=s+1;a<e.length;a++)if(e[s].key===e[a].key&&e[s].placement===e[a].placement)throw new TypeError("Duplicated element ("+e[s].key+")")}}return{elements:e,finishers:i}},fromElementDescriptor:function(e){var t={kind:e.kind,key:e.key,placement:e.placement,descriptor:e.descriptor};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),"field"===e.kind&&(t.initializer=e.initializer),t},toElementDescriptors:function(e){var t;if(void 0!==e)return(t=e,function(e){if(Array.isArray(e))return e}(t)||function(e){if("undefined"!=typeof Symbol&&null!=e[Symbol.iterator]||null!=e["@@iterator"])return Array.from(e)}(t)||function(e,t){if(e){if("string"==typeof e)return $(e,t);var i=Object.prototype.toString.call(e).slice(8,-1);return"Object"===i&&e.constructor&&(i=e.constructor.name),"Map"===i||"Set"===i?Array.from(e):"Arguments"===i||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(i)?$(e,t):void 0}}(t)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()).map((function(e){var t=this.toElementDescriptor(e);return this.disallowProperty(e,"finisher","An element descriptor"),this.disallowProperty(e,"extras","An element descriptor"),t}),this)},toElementDescriptor:function(e){var t=String(e.kind);if("method"!==t&&"field"!==t)throw new TypeError('An element descriptor\'s .kind property must be either "method" or "field", but a decorator created an element descriptor with .kind "'+t+'"');var i=C(e.key),r=String(e.placement);if("static"!==r&&"prototype"!==r&&"own"!==r)throw new TypeError('An element descriptor\'s .placement property must be one of "static", "prototype" or "own", but a decorator created an element descriptor with .placement "'+r+'"');var n=e.descriptor;this.disallowProperty(e,"elements","An element descriptor");var o={kind:t,key:i,placement:r,descriptor:Object.assign({},n)};return"field"!==t?this.disallowProperty(e,"initializer","A method descriptor"):(this.disallowProperty(n,"get","The property descriptor of a field descriptor"),this.disallowProperty(n,"set","The property descriptor of a field descriptor"),this.disallowProperty(n,"value","The property descriptor of a field descriptor"),o.initializer=e.initializer),o},toElementFinisherExtras:function(e){return{element:this.toElementDescriptor(e),finisher:E(e,"finisher"),extras:this.toElementDescriptors(e.extras)}},fromClassDescriptor:function(e){var t={kind:"class",elements:e.map(this.fromElementDescriptor,this)};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),t},toClassDescriptor:function(e){var t=String(e.kind);if("class"!==t)throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator created a class descriptor with .kind "'+t+'"');this.disallowProperty(e,"key","A class descriptor"),this.disallowProperty(e,"placement","A class descriptor"),this.disallowProperty(e,"descriptor","A class descriptor"),this.disallowProperty(e,"initializer","A class descriptor"),this.disallowProperty(e,"extras","A class descriptor");var i=E(e,"finisher");return{elements:this.toElementDescriptors(e.elements),finisher:i}},runClassFinishers:function(e,t){for(var i=0;i<t.length;i++){var r=(0,t[i])(e);if(void 0!==r){if("function"!=typeof r)throw new TypeError("Finishers must return a constructor.");e=r}}return e},disallowProperty:function(e,t,i){if(void 0!==e[t])throw new TypeError(i+" can't have a ."+t+" property.")}};return e}function _(e){var t,i=C(e.key);"method"===e.kind?t={value:e.value,writable:!0,configurable:!0,enumerable:!1}:"get"===e.kind?t={get:e.value,configurable:!0,enumerable:!1}:"set"===e.kind?t={set:e.value,configurable:!0,enumerable:!1}:"field"===e.kind&&(t={configurable:!0,writable:!0,enumerable:!0});var r={kind:"field"===e.kind?"field":"method",key:i,placement:e.static?"static":"field"===e.kind?"own":"prototype",descriptor:t};return e.decorators&&(r.decorators=e.decorators),"field"===e.kind&&(r.initializer=e.value),r}function g(e,t){void 0!==e.descriptor.get?t.descriptor.get=e.descriptor.get:t.descriptor.set=e.descriptor.set}function b(e){return e.decorators&&e.decorators.length}function w(e){return void 0!==e&&!(void 0===e.value&&void 0===e.writable)}function E(e,t){var i=e[t];if(void 0!==i&&"function"!=typeof i)throw new TypeError("Expected '"+t+"' to be a function");return i}function C(e){var t=function(e,t){if("object"!=typeof e||null===e)return e;var i=e[Symbol.toPrimitive];if(void 0!==i){var r=i.call(e,t||"default");if("object"!=typeof r)return r;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===t?String:Number)(e)}(e,"string");return"symbol"==typeof t?t:String(t)}function $(e,t){(null==t||t>e.length)&&(t=e.length);for(var i=0,r=new Array(t);i<t;i++)r[i]=e[i];return r}const x="M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z";!function(e,t,i,r){var n=k();if(r)for(var o=0;o<r.length;o++)n=r[o](n);var s=t((function(e){n.initializeInstanceElements(e,a.elements)}),i),a=n.decorateClass(function(e){for(var t=[],i=function(e){return"method"===e.kind&&e.key===o.key&&e.placement===o.placement},r=0;r<e.length;r++){var n,o=e[r];if("method"===o.kind&&(n=t.find(i)))if(w(o.descriptor)||w(n.descriptor)){if(b(o)||b(n))throw new ReferenceError("Duplicated methods ("+o.key+") can't be decorated.");n.descriptor=o.descriptor}else{if(b(o)){if(b(n))throw new ReferenceError("Decorators can't be placed on different accessors with for the same property ("+o.key+").");n.decorators=o.decorators}g(o,n)}else t.push(o)}return t}(s.d.map(_)),e);n.initializeClassElements(s.F,a.elements),n.runClassFinishers(s.F,a.finishers)}([(0,n.Mo)("ha-target-picker")],(function(e,t){return{F:class extends t{constructor(...t){super(...t),e(this)}},d:[{kind:"field",decorators:[(0,n.Cb)({attribute:!1})],key:"hass",value:void 0},{kind:"field",decorators:[(0,n.Cb)({attribute:!1})],key:"value",value:void 0},{kind:"field",decorators:[(0,n.Cb)()],key:"label",value:void 0},{kind:"field",decorators:[(0,n.Cb)()],key:"helper",value:void 0},{kind:"field",decorators:[(0,n.Cb)({type:Array,attribute:"include-domains"})],key:"includeDomains",value:void 0},{kind:"field",decorators:[(0,n.Cb)({type:Array,attribute:"include-device-classes"})],key:"includeDeviceClasses",value:void 0},{kind:"field",decorators:[(0,n.Cb)()],key:"deviceFilter",value:void 0},{kind:"field",decorators:[(0,n.Cb)()],key:"entityRegFilter",value:void 0},{kind:"field",decorators:[(0,n.Cb)()],key:"entityFilter",value:void 0},{kind:"field",decorators:[(0,n.Cb)({type:Boolean,reflect:!0})],key:"disabled",value:()=>!1},{kind:"field",decorators:[(0,n.Cb)({type:Boolean})],key:"horizontal",value:()=>!1},{kind:"field",decorators:[(0,n.SB)()],key:"_areas",value:void 0},{kind:"field",decorators:[(0,n.SB)()],key:"_devices",value:void 0},{kind:"field",decorators:[(0,n.SB)()],key:"_entities",value:void 0},{kind:"field",decorators:[(0,n.SB)()],key:"_addMode",value:void 0},{kind:"field",decorators:[(0,n.IO)("#input")],key:"_inputElement",value:void 0},{kind:"method",key:"hassSubscribe",value:function(){return[(0,y.sG)(this.hass.connection,(e=>{const t={};for(const i of e)t[i.area_id]=i;this._areas=t})),(0,s.q4)(this.hass.connection,(e=>{const t={};for(const i of e)t[i.id]=i;this._devices=t})),(0,a.LM)(this.hass.connection,(e=>{this._entities=e}))]}},{kind:"method",key:"render",value:function(){return this._areas&&this._devices&&this._entities?r.dy`
      ${this.horizontal?r.dy`
            <div class="horizontal-container">
              ${this._renderChips()} ${this._renderPicker()}
            </div>
            ${this._renderItems()}
          `:r.dy`
            <div>
              ${this._renderItems()} ${this._renderPicker()}
              ${this._renderChips()}
            </div>
          `}
    `:r.dy``}},{kind:"method",key:"_renderItems",value:function(){var e,t,i;return r.dy`
      <div class="mdc-chip-set items">
        ${null!==(e=this.value)&&void 0!==e&&e.area_id?(0,f.r)(this.value.area_id).map((e=>{const t=this._areas[e];return this._renderChip("area_id",e,(null==t?void 0:t.name)||e,void 0,"M12.5 7C12.5 5.89 13.39 5 14.5 5H18C19.1 5 20 5.9 20 7V9.16C18.84 9.57 18 10.67 18 11.97V14H12.5V7M6 11.96V14H11.5V7C11.5 5.89 10.61 5 9.5 5H6C4.9 5 4 5.9 4 7V9.15C5.16 9.56 6 10.67 6 11.96M20.66 10.03C19.68 10.19 19 11.12 19 12.12V15H5V12C5 10.9 4.11 10 3 10S1 10.9 1 12V17C1 18.1 1.9 19 3 19V21H5V19H19V21H21V19C22.1 19 23 18.1 23 17V12C23 10.79 21.91 9.82 20.66 10.03Z")})):""}
        ${null!==(t=this.value)&&void 0!==t&&t.device_id?(0,f.r)(this.value.device_id).map((e=>{const t=this._devices[e];return this._renderChip("device_id",e,t?(0,s.jL)(t,this.hass):e,void 0,"M3 6H21V4H3C1.9 4 1 4.9 1 6V18C1 19.1 1.9 20 3 20H7V18H3V6M13 12H9V13.78C8.39 14.33 8 15.11 8 16C8 16.89 8.39 17.67 9 18.22V20H13V18.22C13.61 17.67 14 16.88 14 16S13.61 14.33 13 13.78V12M11 17.5C10.17 17.5 9.5 16.83 9.5 16S10.17 14.5 11 14.5 12.5 15.17 12.5 16 11.83 17.5 11 17.5M22 8H16C15.5 8 15 8.5 15 9V19C15 19.5 15.5 20 16 20H22C22.5 20 23 19.5 23 19V9C23 8.5 22.5 8 22 8M21 18H17V10H21V18Z")})):""}
        ${null!==(i=this.value)&&void 0!==i&&i.entity_id?(0,f.r)(this.value.entity_id).map((e=>{const t=this.hass.states[e];return this._renderChip("entity_id",e,t?(0,m.C)(t):e,t)})):""}
      </div>
    `}},{kind:"method",key:"_renderChips",value:function(){return r.dy`
      <div class="mdc-chip-set">
        <div
          class="mdc-chip area_id add"
          .type=${"area_id"}
          @click=${this._showPicker}
        >
          <div class="mdc-chip__ripple"></div>
          <ha-svg-icon
            class="mdc-chip__icon mdc-chip__icon--leading"
            .path=${x}
          ></ha-svg-icon>
          <span role="gridcell">
            <span role="button" tabindex="0" class="mdc-chip__primary-action">
              <span class="mdc-chip__text"
                >${this.hass.localize("ui.components.target-picker.add_area_id")}</span
              >
            </span>
          </span>
        </div>
        <div
          class="mdc-chip device_id add"
          .type=${"device_id"}
          @click=${this._showPicker}
        >
          <div class="mdc-chip__ripple"></div>
          <ha-svg-icon
            class="mdc-chip__icon mdc-chip__icon--leading"
            .path=${x}
          ></ha-svg-icon>
          <span role="gridcell">
            <span role="button" tabindex="0" class="mdc-chip__primary-action">
              <span class="mdc-chip__text"
                >${this.hass.localize("ui.components.target-picker.add_device_id")}</span
              >
            </span>
          </span>
        </div>
        <div
          class="mdc-chip entity_id add"
          .type=${"entity_id"}
          @click=${this._showPicker}
        >
          <div class="mdc-chip__ripple"></div>
          <ha-svg-icon
            class="mdc-chip__icon mdc-chip__icon--leading"
            .path=${x}
          ></ha-svg-icon>
          <span role="gridcell">
            <span role="button" tabindex="0" class="mdc-chip__primary-action">
              <span class="mdc-chip__text"
                >${this.hass.localize("ui.components.target-picker.add_entity_id")}</span
              >
            </span>
          </span>
        </div>
      </div>
      ${this.helper?r.dy`<ha-input-helper-text>${this.helper}</ha-input-helper-text>`:""}
    `}},{kind:"method",key:"_showPicker",value:async function(e){var t,i;this._addMode=e.currentTarget.type,await this.updateComplete,await(null===(t=this._inputElement)||void 0===t?void 0:t.focus()),await(null===(i=this._inputElement)||void 0===i?void 0:i.open())}},{kind:"method",key:"_renderChip",value:function(e,t,i,n,o){return r.dy`
      <div
        class="mdc-chip ${(0,h.$)({[e]:!0})}"
      >
        ${o?r.dy`<ha-svg-icon
              class="mdc-chip__icon mdc-chip__icon--leading"
              .path=${o}
            ></ha-svg-icon>`:""}
        ${n?r.dy`<ha-state-icon
              class="mdc-chip__icon mdc-chip__icon--leading"
              .state=${n}
            ></ha-state-icon>`:""}
        <span role="gridcell">
          <span role="button" tabindex="0" class="mdc-chip__primary-action">
            <span class="mdc-chip__text">${i}</span>
          </span>
        </span>
        ${"entity_id"===e?"":r.dy` <span role="gridcell">
              <ha-icon-button
                class="expand-btn mdc-chip__icon mdc-chip__icon--trailing"
                tabindex="-1"
                role="button"
                .label=${this.hass.localize("ui.components.target-picker.expand")}
                .path=${"M18.17,12L15,8.83L16.41,7.41L21,12L16.41,16.58L15,15.17L18.17,12M5.83,12L9,15.17L7.59,16.59L3,12L7.59,7.42L9,8.83L5.83,12Z"}
                hideTooltip
                .id=${t}
                .type=${e}
                @click=${this._handleExpand}
              ></ha-icon-button>
              <paper-tooltip class="expand" animation-delay="0"
                >${this.hass.localize(`ui.components.target-picker.expand_${e}`)}</paper-tooltip
              >
            </span>`}
        <span role="gridcell">
          <ha-icon-button
            class="mdc-chip__icon mdc-chip__icon--trailing"
            tabindex="-1"
            role="button"
            .label=${this.hass.localize("ui.components.target-picker.remove")}
            .path=${"M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"}
            hideTooltip
            .id=${t}
            .type=${e}
            @click=${this._handleRemove}
          ></ha-icon-button>
          <paper-tooltip animation-delay="0"
            >${this.hass.localize(`ui.components.target-picker.remove_${e}`)}</paper-tooltip
          >
        </span>
      </div>
    `}},{kind:"method",key:"_renderPicker",value:function(){switch(this._addMode){case"area_id":return r.dy`
          <ha-area-picker
            .hass=${this.hass}
            id="input"
            .type=${"area_id"}
            .label=${this.hass.localize("ui.components.target-picker.add_area_id")}
            no-add
            .deviceFilter=${this.deviceFilter}
            .entityFilter=${this.entityRegFilter}
            .includeDeviceClasses=${this.includeDeviceClasses}
            .includeDomains=${this.includeDomains}
            @value-changed=${this._targetPicked}
          ></ha-area-picker>
        `;case"device_id":return r.dy`
          <ha-device-picker
            .hass=${this.hass}
            id="input"
            .type=${"device_id"}
            .label=${this.hass.localize("ui.components.target-picker.add_device_id")}
            .deviceFilter=${this.deviceFilter}
            .entityFilter=${this.entityRegFilter}
            .includeDeviceClasses=${this.includeDeviceClasses}
            .includeDomains=${this.includeDomains}
            @value-changed=${this._targetPicked}
          ></ha-device-picker>
        `;case"entity_id":return r.dy`
          <ha-entity-picker
            .hass=${this.hass}
            id="input"
            .type=${"entity_id"}
            .label=${this.hass.localize("ui.components.target-picker.add_entity_id")}
            .entityFilter=${this.entityFilter}
            .includeDeviceClasses=${this.includeDeviceClasses}
            .includeDomains=${this.includeDomains}
            @value-changed=${this._targetPicked}
            allow-custom-entity
          ></ha-entity-picker>
        `}return r.dy``}},{kind:"method",key:"_targetPicked",value:function(e){if(e.stopPropagation(),!e.detail.value)return;const t=e.detail.value,i=e.currentTarget;i.value="",this._addMode=void 0,(0,u.B)(this,"value-changed",{value:this.value?{...this.value,[i.type]:this.value[i.type]?[...(0,f.r)(this.value[i.type]),t]:t}:{[i.type]:t}})}},{kind:"method",key:"_handleExpand",value:function(e){const t=e.currentTarget,i=[],r=[];if("area_id"===t.type)Object.values(this._devices).forEach((e=>{var r;e.area_id!==t.id||null!==(r=this.value.device_id)&&void 0!==r&&r.includes(e.id)||!this._deviceMeetsFilter(e)||i.push(e.id)})),this._entities.forEach((e=>{var i;e.area_id!==t.id||null!==(i=this.value.entity_id)&&void 0!==i&&i.includes(e.entity_id)||!this._entityRegMeetsFilter(e)||r.push(e.entity_id)}));else{if("device_id"!==t.type)return;this._entities.forEach((e=>{var i;e.device_id!==t.id||null!==(i=this.value.entity_id)&&void 0!==i&&i.includes(e.entity_id)||!this._entityRegMeetsFilter(e)||r.push(e.entity_id)}))}let n=this.value;r.length&&(n=this._addItems(n,"entity_id",r)),i.length&&(n=this._addItems(n,"device_id",i)),n=this._removeItem(n,t.type,t.id),(0,u.B)(this,"value-changed",{value:n})}},{kind:"method",key:"_handleRemove",value:function(e){const t=e.currentTarget;(0,u.B)(this,"value-changed",{value:this._removeItem(this.value,t.type,t.id)})}},{kind:"method",key:"_addItems",value:function(e,t,i){return{...e,[t]:e[t]?(0,f.r)(e[t]).concat(i):i}}},{kind:"method",key:"_removeItem",value:function(e,t,i){const r=(0,f.r)(e[t]).filter((e=>String(e)!==i));if(r.length)return{...e,[t]:r};const n={...e};return delete n[t],Object.keys(n).length?n:void 0}},{kind:"method",key:"_deviceMeetsFilter",value:function(e){var t;const i=null===(t=this._entities)||void 0===t?void 0:t.filter((t=>t.device_id===e.id));if(this.includeDomains){if(!i||!i.length)return!1;if(!i.some((e=>this.includeDomains.includes((0,v.M)(e.entity_id)))))return!1}if(this.includeDeviceClasses){if(!i||!i.length)return!1;if(!i.some((e=>{const t=this.hass.states[e.entity_id];return!!t&&(t.attributes.device_class&&this.includeDeviceClasses.includes(t.attributes.device_class))})))return!1}return!this.deviceFilter||this.deviceFilter(e)}},{kind:"method",key:"_entityRegMeetsFilter",value:function(e){if(e.entity_category)return!1;if(this.includeDomains&&!this.includeDomains.includes((0,v.M)(e.entity_id)))return!1;if(this.includeDeviceClasses){const t=this.hass.states[e.entity_id];if(!t)return!1;if(!t.attributes.device_class||!this.includeDeviceClasses.includes(t.attributes.device_class))return!1}return!this.entityRegFilter||this.entityRegFilter(e)}},{kind:"get",static:!0,key:"styles",value:function(){return r.iv`
      ${(0,r.$m)(p)}
      .horizontal-container {
        display: flex;
        flex-wrap: wrap;
        min-height: 56px;
        align-items: center;
      }
      .mdc-chip {
        color: var(--primary-text-color);
      }
      .items {
        z-index: 2;
      }
      .mdc-chip-set {
        padding: 4px 0;
      }
      .mdc-chip.add {
        color: rgba(0, 0, 0, 0.87);
      }
      .mdc-chip:not(.add) {
        cursor: default;
      }
      .mdc-chip ha-icon-button {
        --mdc-icon-button-size: 24px;
        display: flex;
        align-items: center;
        outline: none;
      }
      .mdc-chip ha-icon-button ha-svg-icon {
        border-radius: 50%;
        background: var(--secondary-text-color);
      }
      .mdc-chip__icon.mdc-chip__icon--trailing {
        width: 16px;
        height: 16px;
        --mdc-icon-size: 14px;
        color: var(--secondary-text-color);
        margin-inline-start: 4px !important;
        margin-inline-end: -4px !important;
        direction: var(--direction);
      }
      .mdc-chip__icon--leading {
        display: flex;
        align-items: center;
        justify-content: center;
        --mdc-icon-size: 20px;
        border-radius: 50%;
        padding: 6px;
        margin-left: -14px !important;
        margin-inline-start: -14px !important;
        margin-inline-end: 4px !important;
        direction: var(--direction);
      }
      .expand-btn {
        margin-right: 0;
      }
      .mdc-chip.area_id:not(.add) {
        border: 2px solid #fed6a4;
        background: var(--card-background-color);
      }
      .mdc-chip.area_id:not(.add) .mdc-chip__icon--leading,
      .mdc-chip.area_id.add {
        background: #fed6a4;
      }
      .mdc-chip.device_id:not(.add) {
        border: 2px solid #a8e1fb;
        background: var(--card-background-color);
      }
      .mdc-chip.device_id:not(.add) .mdc-chip__icon--leading,
      .mdc-chip.device_id.add {
        background: #a8e1fb;
      }
      .mdc-chip.entity_id:not(.add) {
        border: 2px solid #d2e7b9;
        background: var(--card-background-color);
      }
      .mdc-chip.entity_id:not(.add) .mdc-chip__icon--leading,
      .mdc-chip.entity_id.add {
        background: #d2e7b9;
      }
      .mdc-chip:hover {
        z-index: 5;
      }
      paper-tooltip.expand {
        min-width: 200px;
      }
      :host([disabled]) .mdc-chip {
        opacity: var(--light-disabled-opacity);
        pointer-events: none;
      }
    `}}]}}),(0,l.f)(r.oi));function D(){D=function(){return e};var e={elementsDefinitionOrder:[["method"],["field"]],initializeInstanceElements:function(e,t){["method","field"].forEach((function(i){t.forEach((function(t){t.kind===i&&"own"===t.placement&&this.defineClassElement(e,t)}),this)}),this)},initializeClassElements:function(e,t){var i=e.prototype;["method","field"].forEach((function(r){t.forEach((function(t){var n=t.placement;if(t.kind===r&&("static"===n||"prototype"===n)){var o="static"===n?e:i;this.defineClassElement(o,t)}}),this)}),this)},defineClassElement:function(e,t){var i=t.descriptor;if("field"===t.kind){var r=t.initializer;i={enumerable:i.enumerable,writable:i.writable,configurable:i.configurable,value:void 0===r?void 0:r.call(e)}}Object.defineProperty(e,t.key,i)},decorateClass:function(e,t){var i=[],r=[],n={static:[],prototype:[],own:[]};if(e.forEach((function(e){this.addElementPlacement(e,n)}),this),e.forEach((function(e){if(!z(e))return i.push(e);var t=this.decorateElement(e,n);i.push(t.element),i.push.apply(i,t.extras),r.push.apply(r,t.finishers)}),this),!t)return{elements:i,finishers:r};var o=this.decorateConstructor(i,t);return r.push.apply(r,o.finishers),o.finishers=r,o},addElementPlacement:function(e,t,i){var r=t[e.placement];if(!i&&-1!==r.indexOf(e.key))throw new TypeError("Duplicated element ("+e.key+")");r.push(e.key)},decorateElement:function(e,t){for(var i=[],r=[],n=e.decorators,o=n.length-1;o>=0;o--){var s=t[e.placement];s.splice(s.indexOf(e.key),1);var a=this.fromElementDescriptor(e),d=this.toElementFinisherExtras((0,n[o])(a)||a);e=d.element,this.addElementPlacement(e,t),d.finisher&&r.push(d.finisher);var c=d.extras;if(c){for(var l=0;l<c.length;l++)this.addElementPlacement(c[l],t);i.push.apply(i,c)}}return{element:e,finishers:r,extras:i}},decorateConstructor:function(e,t){for(var i=[],r=t.length-1;r>=0;r--){var n=this.fromClassDescriptor(e),o=this.toClassDescriptor((0,t[r])(n)||n);if(void 0!==o.finisher&&i.push(o.finisher),void 0!==o.elements){e=o.elements;for(var s=0;s<e.length-1;s++)for(var a=s+1;a<e.length;a++)if(e[s].key===e[a].key&&e[s].placement===e[a].placement)throw new TypeError("Duplicated element ("+e[s].key+")")}}return{elements:e,finishers:i}},fromElementDescriptor:function(e){var t={kind:e.kind,key:e.key,placement:e.placement,descriptor:e.descriptor};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),"field"===e.kind&&(t.initializer=e.initializer),t},toElementDescriptors:function(e){var t;if(void 0!==e)return(t=e,function(e){if(Array.isArray(e))return e}(t)||function(e){if("undefined"!=typeof Symbol&&null!=e[Symbol.iterator]||null!=e["@@iterator"])return Array.from(e)}(t)||function(e,t){if(e){if("string"==typeof e)return V(e,t);var i=Object.prototype.toString.call(e).slice(8,-1);return"Object"===i&&e.constructor&&(i=e.constructor.name),"Map"===i||"Set"===i?Array.from(e):"Arguments"===i||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(i)?V(e,t):void 0}}(t)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()).map((function(e){var t=this.toElementDescriptor(e);return this.disallowProperty(e,"finisher","An element descriptor"),this.disallowProperty(e,"extras","An element descriptor"),t}),this)},toElementDescriptor:function(e){var t=String(e.kind);if("method"!==t&&"field"!==t)throw new TypeError('An element descriptor\'s .kind property must be either "method" or "field", but a decorator created an element descriptor with .kind "'+t+'"');var i=T(e.key),r=String(e.placement);if("static"!==r&&"prototype"!==r&&"own"!==r)throw new TypeError('An element descriptor\'s .placement property must be one of "static", "prototype" or "own", but a decorator created an element descriptor with .placement "'+r+'"');var n=e.descriptor;this.disallowProperty(e,"elements","An element descriptor");var o={kind:t,key:i,placement:r,descriptor:Object.assign({},n)};return"field"!==t?this.disallowProperty(e,"initializer","A method descriptor"):(this.disallowProperty(n,"get","The property descriptor of a field descriptor"),this.disallowProperty(n,"set","The property descriptor of a field descriptor"),this.disallowProperty(n,"value","The property descriptor of a field descriptor"),o.initializer=e.initializer),o},toElementFinisherExtras:function(e){return{element:this.toElementDescriptor(e),finisher:F(e,"finisher"),extras:this.toElementDescriptors(e.extras)}},fromClassDescriptor:function(e){var t={kind:"class",elements:e.map(this.fromElementDescriptor,this)};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),t},toClassDescriptor:function(e){var t=String(e.kind);if("class"!==t)throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator created a class descriptor with .kind "'+t+'"');this.disallowProperty(e,"key","A class descriptor"),this.disallowProperty(e,"placement","A class descriptor"),this.disallowProperty(e,"descriptor","A class descriptor"),this.disallowProperty(e,"initializer","A class descriptor"),this.disallowProperty(e,"extras","A class descriptor");var i=F(e,"finisher");return{elements:this.toElementDescriptors(e.elements),finisher:i}},runClassFinishers:function(e,t){for(var i=0;i<t.length;i++){var r=(0,t[i])(e);if(void 0!==r){if("function"!=typeof r)throw new TypeError("Finishers must return a constructor.");e=r}}return e},disallowProperty:function(e,t,i){if(void 0!==e[t])throw new TypeError(i+" can't have a ."+t+" property.")}};return e}function P(e){var t,i=T(e.key);"method"===e.kind?t={value:e.value,writable:!0,configurable:!0,enumerable:!1}:"get"===e.kind?t={get:e.value,configurable:!0,enumerable:!1}:"set"===e.kind?t={set:e.value,configurable:!0,enumerable:!1}:"field"===e.kind&&(t={configurable:!0,writable:!0,enumerable:!0});var r={kind:"field"===e.kind?"field":"method",key:i,placement:e.static?"static":"field"===e.kind?"own":"prototype",descriptor:t};return e.decorators&&(r.decorators=e.decorators),"field"===e.kind&&(r.initializer=e.value),r}function S(e,t){void 0!==e.descriptor.get?t.descriptor.get=e.descriptor.get:t.descriptor.set=e.descriptor.set}function z(e){return e.decorators&&e.decorators.length}function A(e){return void 0!==e&&!(void 0===e.value&&void 0===e.writable)}function F(e,t){var i=e[t];if(void 0!==i&&"function"!=typeof i)throw new TypeError("Expected '"+t+"' to be a function");return i}function T(e){var t=function(e,t){if("object"!=typeof e||null===e)return e;var i=e[Symbol.toPrimitive];if(void 0!==i){var r=i.call(e,t||"default");if("object"!=typeof r)return r;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===t?String:Number)(e)}(e,"string");return"symbol"==typeof t?t:String(t)}function V(e,t){(null==t||t>e.length)&&(t=e.length);for(var i=0,r=new Array(t);i<t;i++)r[i]=e[i];return r}function O(e,t,i){return O="undefined"!=typeof Reflect&&Reflect.get?Reflect.get:function(e,t,i){var r=function(e,t){for(;!Object.prototype.hasOwnProperty.call(e,t)&&null!==(e=L(e)););return e}(e,t);if(r){var n=Object.getOwnPropertyDescriptor(r,t);return n.get?n.get.call(i):n.value}},O(e,t,i||e)}function L(e){return L=Object.setPrototypeOf?Object.getPrototypeOf:function(e){return e.__proto__||Object.getPrototypeOf(e)},L(e)}let M=function(e,t,i,r){var n=D();if(r)for(var o=0;o<r.length;o++)n=r[o](n);var s=t((function(e){n.initializeInstanceElements(e,a.elements)}),i),a=n.decorateClass(function(e){for(var t=[],i=function(e){return"method"===e.kind&&e.key===o.key&&e.placement===o.placement},r=0;r<e.length;r++){var n,o=e[r];if("method"===o.kind&&(n=t.find(i)))if(A(o.descriptor)||A(n.descriptor)){if(z(o)||z(n))throw new ReferenceError("Duplicated methods ("+o.key+") can't be decorated.");n.descriptor=o.descriptor}else{if(z(o)){if(z(n))throw new ReferenceError("Decorators can't be placed on different accessors with for the same property ("+o.key+").");n.decorators=o.decorators}S(o,n)}else t.push(o)}return t}(s.d.map(P)),e);return n.initializeClassElements(s.F,a.elements),n.runClassFinishers(s.F,a.finishers)}([(0,n.Mo)("ha-selector-target")],(function(e,t){class i extends t{constructor(...t){super(...t),e(this)}}return{F:i,d:[{kind:"field",decorators:[(0,n.Cb)()],key:"hass",value:void 0},{kind:"field",decorators:[(0,n.Cb)()],key:"selector",value:void 0},{kind:"field",decorators:[(0,n.Cb)()],key:"value",value:void 0},{kind:"field",decorators:[(0,n.Cb)()],key:"label",value:void 0},{kind:"field",decorators:[(0,n.Cb)()],key:"helper",value:void 0},{kind:"field",decorators:[(0,n.Cb)({type:Boolean})],key:"disabled",value:()=>!1},{kind:"field",decorators:[(0,n.SB)()],key:"_entitySources",value:void 0},{kind:"field",decorators:[(0,n.SB)()],key:"_entities",value:void 0},{kind:"field",key:"_deviceIntegrationLookup",value:()=>(0,o.Z)(s.HP)},{kind:"method",key:"hassSubscribe",value:function(){return[(0,a.LM)(this.hass.connection,(e=>{this._entities=e.filter((e=>null!==e.device_id))}))]}},{kind:"method",key:"updated",value:function(e){var t,r;O(L(i.prototype),"updated",this).call(this,e),e.has("selector")&&(null!==(t=this.selector.target.device)&&void 0!==t&&t.integration||null!==(r=this.selector.target.entity)&&void 0!==r&&r.integration)&&!this._entitySources&&(0,d.m)(this.hass).then((e=>{this._entitySources=e}))}},{kind:"method",key:"render",value:function(){var e,t;return(null!==(e=this.selector.target.device)&&void 0!==e&&e.integration||null!==(t=this.selector.target.entity)&&void 0!==t&&t.integration)&&!this._entitySources?r.dy``:r.dy`<ha-target-picker
      .hass=${this.hass}
      .value=${this.value}
      .helper=${this.helper}
      .deviceFilter=${this._filterDevices}
      .entityFilter=${this._filterEntities}
      .disabled=${this.disabled}
    ></ha-target-picker>`}},{kind:"field",key:"_filterEntities",value(){return e=>!this.selector.target.entity||(0,c.J)(this.selector.target.entity,e,this._entitySources)}},{kind:"field",key:"_filterDevices",value(){return e=>{if(!this.selector.target.device)return!0;const t=this._entitySources&&this._entities?this._deviceIntegrationLookup(this._entitySources,this._entities):void 0;return(0,c.l)(this.selector.target.device,e,t)}}},{kind:"get",static:!0,key:"styles",value:function(){return r.iv`
      ha-target-picker {
        display: block;
      }
    `}}]}}),(0,l.f)(r.oi))},2814:(e,t,i)=>{i.d(t,{iI:()=>r});location.protocol,location.host;const r=(e,t)=>e.callWS({type:"auth/sign_path",path:t})},6007:(e,t,i)=>{i.d(t,{nZ:()=>r,lz:()=>n,V_:()=>o});const r="unavailable",n="unknown",o=[r,n]}}]);
//# sourceMappingURL=b4773236.js.map