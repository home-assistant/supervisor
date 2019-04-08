(window.webpackJsonp=window.webpackJsonp||[]).push([[18],{135:function(e,n,t){"use strict";t.r(n);t(14),t(13),t(100),t(46),t(101),t(121);var a=t(4),s=t(7),o=(t(35),t(43),t(24)),r=t(28);function i(e){return(i="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(e){return typeof e}:function(e){return e&&"function"==typeof Symbol&&e.constructor===Symbol&&e!==Symbol.prototype?"symbol":typeof e})(e)}function p(){var e=function(e,n){n||(n=e.slice(0));return Object.freeze(Object.defineProperties(e,{raw:{value:Object.freeze(n)}}))}(['\n      <style include="ha-style hassio-style">\n        paper-radio-group {\n          display: block;\n        }\n        paper-radio-button {\n          padding: 0 0 2px 2px;\n        }\n        paper-radio-button,\n        paper-checkbox,\n        paper-input[type="password"] {\n          display: block;\n          margin: 4px 0 4px 48px;\n        }\n        .pointer {\n          cursor: pointer;\n        }\n      </style>\n      <div class="content">\n        <div class="card-group">\n          <div class="title">\n            Create snapshot\n            <div class="description">\n              Snapshots allow you to easily backup and restore all data of your\n              Hass.io instance.\n            </div>\n          </div>\n          <paper-card>\n            <div class="card-content">\n              <paper-input\n                autofocus=""\n                label="Name"\n                value="{{snapshotName}}"\n              ></paper-input>\n              Type:\n              <paper-radio-group selected="{{snapshotType}}">\n                <paper-radio-button name="full">\n                  Full snapshot\n                </paper-radio-button>\n                <paper-radio-button name="partial">\n                  Partial snapshot\n                </paper-radio-button>\n              </paper-radio-group>\n              <template is="dom-if" if="[[!_fullSelected(snapshotType)]]">\n                Folders:\n                <template is="dom-repeat" items="[[folderList]]">\n                  <paper-checkbox checked="{{item.checked}}">\n                    [[item.name]]\n                  </paper-checkbox>\n                </template>\n                Add-ons:\n                <template\n                  is="dom-repeat"\n                  items="[[addonList]]"\n                  sort="_sortAddons"\n                >\n                  <paper-checkbox checked="{{item.checked}}">\n                    [[item.name]]\n                  </paper-checkbox>\n                </template>\n              </template>\n              Security:\n              <paper-checkbox checked="{{snapshotHasPassword}}"\n                >Password protection</paper-checkbox\n              >\n              <template is="dom-if" if="[[snapshotHasPassword]]">\n                <paper-input\n                  label="Password"\n                  type="password"\n                  value="{{snapshotPassword}}"\n                ></paper-input>\n              </template>\n              <template is="dom-if" if="[[error]]">\n                <p class="error">[[error]]</p>\n              </template>\n            </div>\n            <div class="card-actions">\n              <mwc-button\n                disabled="[[creatingSnapshot]]"\n                on-click="_createSnapshot"\n                >Create</mwc-button\n              >\n            </div>\n          </paper-card>\n        </div>\n\n        <div class="card-group">\n          <div class="title">Available snapshots</div>\n          <template is="dom-if" if="[[!snapshots.length]]">\n            <paper-card>\n              <div class="card-content">You don\'t have any snapshots yet.</div>\n            </paper-card>\n          </template>\n          <template\n            is="dom-repeat"\n            items="[[snapshots]]"\n            as="snapshot"\n            sort="_sortSnapshots"\n          >\n            <paper-card class="pointer" on-click="_snapshotClicked">\n              <div class="card-content">\n                <hassio-card-content\n                  hass="[[hass]]"\n                  title="[[_computeName(snapshot)]]"\n                  description="[[_computeDetails(snapshot)]]"\n                  datetime="[[snapshot.date]]"\n                  icon="[[_computeIcon(snapshot.type)]]"\n                  icon-class="snapshot"\n                ></hassio-card-content>\n              </div>\n            </paper-card>\n          </template>\n        </div>\n      </div>\n    ']);return p=function(){return e},e}function c(e,n){for(var t=0;t<n.length;t++){var a=n[t];a.enumerable=a.enumerable||!1,a.configurable=!0,"value"in a&&(a.writable=!0),Object.defineProperty(e,a.key,a)}}function l(e,n){return!n||"object"!==i(n)&&"function"!=typeof n?function(e){if(void 0===e)throw new ReferenceError("this hasn't been initialised - super() hasn't been called");return e}(e):n}function u(e,n,t){return(u="undefined"!=typeof Reflect&&Reflect.get?Reflect.get:function(e,n,t){var a=function(e,n){for(;!Object.prototype.hasOwnProperty.call(e,n)&&null!==(e=d(e)););return e}(e,n);if(a){var s=Object.getOwnPropertyDescriptor(a,n);return s.get?s.get.call(t):s.value}})(e,n,t||e)}function d(e){return(d=Object.setPrototypeOf?Object.getPrototypeOf:function(e){return e.__proto__||Object.getPrototypeOf(e)})(e)}function h(e,n){return(h=Object.setPrototypeOf||function(e,n){return e.__proto__=n,e})(e,n)}var f=function(e){function n(){return function(e,n){if(!(e instanceof n))throw new TypeError("Cannot call a class as a function")}(this,n),l(this,d(n).apply(this,arguments))}var i,f,m;return function(e,n){if("function"!=typeof n&&null!==n)throw new TypeError("Super expression must either be null or a function");e.prototype=Object.create(n&&n.prototype,{constructor:{value:e,writable:!0,configurable:!0}}),n&&h(e,n)}(n,Object(o["a"])(s["a"])),i=n,m=[{key:"template",get:function(){return Object(a.a)(p())}},{key:"properties",get:function(){return{hass:Object,snapshotName:{type:String,value:""},snapshotPassword:{type:String,value:""},snapshotHasPassword:Boolean,snapshotType:{type:String,value:"full"},snapshots:{type:Array,value:[]},supervisorInfo:Object,installedAddons:{type:Array,computed:"_computeAddons(supervisorInfo)",observer:"_installedAddonsChanged"},addonList:Array,folderList:{type:Array,value:[{slug:"homeassistant",name:"Home Assistant configuration",checked:!0},{slug:"ssl",name:"SSL",checked:!0},{slug:"share",name:"Share",checked:!0},{slug:"addons/local",name:"Local add-ons",checked:!0}]},snapshotSlug:{type:String,notify:!0},snapshotDeleted:{type:Boolean,notify:!0,observer:"_snapshotDeletedChanged"},creatingSnapshot:Boolean,dialogOpened:Boolean,error:String}}}],(f=[{key:"ready",value:function(){var e=this;u(d(n.prototype),"ready",this).call(this),this.addEventListener("hass-api-called",function(n){return e._apiCalled(n)}),this._updateSnapshots()}},{key:"_apiCalled",value:function(e){e.detail.success&&this._updateSnapshots()}},{key:"_updateSnapshots",value:function(){var e=this;this.hass.callApi("get","hassio/snapshots").then(function(n){e.snapshots=n.data.snapshots},function(n){e.error=n.message})}},{key:"_createSnapshot",value:function(){var e=this;if(this.error="",!this.snapshotHasPassword||this.snapshotPassword.length){this.creatingSnapshot=!0;var n,t,a=this.snapshotName;if(a.length||(a=(new Date).toLocaleDateString(navigator.language,{weekday:"long",year:"numeric",month:"short",day:"numeric"})),"full"===this.snapshotType)n={name:a},t="hassio/snapshots/new/full";else{var s=this.addonList.filter(function(e){return e.checked}).map(function(e){return e.slug});n={name:a,folders:this.folderList.filter(function(e){return e.checked}).map(function(e){return e.slug}),addons:s},t="hassio/snapshots/new/partial"}this.snapshotHasPassword&&(n.password=this.snapshotPassword),this.hass.callApi("post",t,n).then(function(){e.creatingSnapshot=!1,e.fire("hass-api-called",{success:!0})},function(n){e.creatingSnapshot=!1,e.error=n.message})}else this.error="Please enter a password."}},{key:"_installedAddonsChanged",value:function(e){this.addonList=e.map(function(e){return{slug:e.slug,name:e.name,checked:!0}})}},{key:"_sortAddons",value:function(e,n){return e.name<n.name?-1:1}},{key:"_sortSnapshots",value:function(e,n){return e.date<n.date?1:-1}},{key:"_computeName",value:function(e){return e.name||e.slug}},{key:"_computeDetails",value:function(e){var n="full"===e.type?"Full snapshot":"Partial snapshot";return e.protected?"".concat(n,", password protected"):n}},{key:"_computeIcon",value:function(e){return"full"===e?"hassio:package-variant-closed":"hassio:package-variant"}},{key:"_snapshotClicked",value:function(e){var n,a,s=this;n=this,a={slug:e.model.snapshot.slug,onDelete:function(){return s._updateSnapshots()}},Object(r.a)(n,"show-dialog",{dialogTag:"dialog-hassio-snapshot",dialogImport:function(){return Promise.all([t.e(1),t.e(4)]).then(t.bind(null,136))},dialogParams:a}),this.snapshotSlug=e.model.snapshot.slug}},{key:"_fullSelected",value:function(e){return"full"===e}},{key:"refreshData",value:function(){var e=this;this.hass.callApi("post","hassio/snapshots/reload").then(function(){e._updateSnapshots()})}},{key:"_computeAddons",value:function(e){return e.addons}}])&&c(i.prototype,f),m&&c(i,m),n}();customElements.define("hassio-snapshots",f)}}]);