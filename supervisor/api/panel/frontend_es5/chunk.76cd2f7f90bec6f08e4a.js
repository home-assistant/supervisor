(self.webpackJsonp=self.webpackJsonp||[]).push([[4],{170:function(e,t,n){"use strict";n.r(t);n(40);var r=n(7),o=(n(71),n(0)),i=n(101);n(33);"".concat(location.protocol,"//").concat(location.host);var s=n(69),a=n(28),c=n(11);function l(e){return(l="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(e){return typeof e}:function(e){return e&&"function"==typeof Symbol&&e.constructor===Symbol&&e!==Symbol.prototype?"symbol":typeof e})(e)}function u(){var e=b(["\n        paper-checkbox {\n          display: block;\n          margin: 4px;\n        }\n        .details {\n          color: var(--secondary-text-color);\n        }\n        .warning,\n        .error {\n          color: var(--error-color);\n        }\n        .buttons {\n          display: flex;\n          flex-direction: column;\n        }\n        .buttons li {\n          list-style-type: none;\n        }\n        .buttons .icon {\n          margin-right: 16px;\n        }\n        .no-margin-top {\n          margin-top: 0;\n        }\n      "]);return u=function(){return e},e}function d(){var e=b(["\n              <mwc-button\n                @click=",'\n                slot="secondaryAction"\n              >\n                <ha-svg-icon path=',' class="icon"></ha-svg-icon>\n                Wipe &amp; restore\n              </mwc-button>\n            ']);return d=function(){return e},e}function p(){var e=b([' <p class="error">Error: ',"</p> "]);return p=function(){return e},e}function h(){var e=b(['\n              <paper-input\n                autofocus=""\n                label="Password"\n                type="password"\n                @value-changed=',"\n                .value=","\n              ></paper-input>\n            "]);return h=function(){return e},e}function f(){var e=b(["\n                    <paper-checkbox\n                      .checked=",'\n                      @change="','"\n                    >\n                      ',"\n                    </paper-checkbox>\n                  "]);return f=function(){return e},e}function m(){var e=b(['\n              <div>Add-on:</div>\n              <paper-dialog-scrollable class="no-margin-top">\n                ',"\n              </paper-dialog-scrollable>\n            "]);return m=function(){return e},e}function v(){var e=b(["\n                    <paper-checkbox\n                      .checked=",'\n                      @change="','"\n                    >\n                      ',"\n                    </paper-checkbox>\n                  "]);return v=function(){return e},e}function y(){var e=b(['\n              <div>Folders:</div>\n              <paper-dialog-scrollable class="no-margin-top">\n                ',"\n              </paper-dialog-scrollable>\n            "]);return y=function(){return e},e}function g(){var e=b(["\n      <ha-dialog\n        open\n        stacked\n        @closing=","\n        .heading=",'\n      >\n        <div class="details">\n          ',"\n          (",")<br />\n          ","\n        </div>\n        <div>Home Assistant:</div>\n        <paper-checkbox\n          .checked=",'\n          @change="','"\n        >\n          Home Assistant ',"\n        </paper-checkbox>\n        ","\n        ","\n        ","\n        ","\n\n        <div>Actions:</div>\n\n        <mwc-button @click=",' slot="primaryAction">\n          <ha-svg-icon path=',' class="icon"></ha-svg-icon>\n          Download Snapshot\n        </mwc-button>\n\n        <mwc-button\n          @click=','\n          slot="secondaryAction"\n        >\n          <ha-svg-icon path=',' class="icon"></ha-svg-icon>\n          Restore Selected\n        </mwc-button>\n        ',"\n        <mwc-button @click=",' slot="secondaryAction">\n          <ha-svg-icon path=',' class="icon warning"></ha-svg-icon>\n          <span class="warning">Delete Snapshot</span>\n        </mwc-button>\n      </ha-dialog>\n    ']);return g=function(){return e},e}function k(){var e=b([""]);return k=function(){return e},e}function b(e,t){return t||(t=e.slice(0)),Object.freeze(Object.defineProperties(e,{raw:{value:Object.freeze(t)}}))}function w(e,t,n,r,o,i,s){try{var a=e[i](s),c=a.value}catch(l){return void n(l)}a.done?t(c):Promise.resolve(c).then(r,o)}function _(e){return function(){var t=this,n=arguments;return new Promise((function(r,o){var i=e.apply(t,n);function s(e){w(i,r,o,s,a,"next",e)}function a(e){w(i,r,o,s,a,"throw",e)}s(void 0)}))}}function E(e,t){if(!(e instanceof t))throw new TypeError("Cannot call a class as a function")}function O(e,t){return(O=Object.setPrototypeOf||function(e,t){return e.__proto__=t,e})(e,t)}function P(e,t){return!t||"object"!==l(t)&&"function"!=typeof t?j(e):t}function j(e){if(void 0===e)throw new ReferenceError("this hasn't been initialised - super() hasn't been called");return e}function x(){if("undefined"==typeof Reflect||!Reflect.construct)return!1;if(Reflect.construct.sham)return!1;if("function"==typeof Proxy)return!0;try{return Date.prototype.toString.call(Reflect.construct(Date,[],(function(){}))),!0}catch(e){return!1}}function A(e){return(A=Object.setPrototypeOf?Object.getPrototypeOf:function(e){return e.__proto__||Object.getPrototypeOf(e)})(e)}function S(e){var t,n=z(e.key);"method"===e.kind?t={value:e.value,writable:!0,configurable:!0,enumerable:!1}:"get"===e.kind?t={get:e.value,configurable:!0,enumerable:!1}:"set"===e.kind?t={set:e.value,configurable:!0,enumerable:!1}:"field"===e.kind&&(t={configurable:!0,writable:!0,enumerable:!0});var r={kind:"field"===e.kind?"field":"method",key:n,placement:e.static?"static":"field"===e.kind?"own":"prototype",descriptor:t};return e.decorators&&(r.decorators=e.decorators),"field"===e.kind&&(r.initializer=e.value),r}function D(e,t){void 0!==e.descriptor.get?t.descriptor.get=e.descriptor.get:t.descriptor.set=e.descriptor.set}function C(e){return e.decorators&&e.decorators.length}function R(e){return void 0!==e&&!(void 0===e.value&&void 0===e.writable)}function T(e,t){var n=e[t];if(void 0!==n&&"function"!=typeof n)throw new TypeError("Expected '"+t+"' to be a function");return n}function z(e){var t=function(e,t){if("object"!==l(e)||null===e)return e;var n=e[Symbol.toPrimitive];if(void 0!==n){var r=n.call(e,t||"default");if("object"!==l(r))return r;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===t?String:Number)(e)}(e,"string");return"symbol"===l(t)?t:String(t)}function F(e,t){(null==t||t>e.length)&&(t=e.length);for(var n=0,r=new Array(t);n<t;n++)r[n]=e[n];return r}!function(e,t,n,r){var o=function(){(function(){return e});var e={elementsDefinitionOrder:[["method"],["field"]],initializeInstanceElements:function(e,t){["method","field"].forEach((function(n){t.forEach((function(t){t.kind===n&&"own"===t.placement&&this.defineClassElement(e,t)}),this)}),this)},initializeClassElements:function(e,t){var n=e.prototype;["method","field"].forEach((function(r){t.forEach((function(t){var o=t.placement;if(t.kind===r&&("static"===o||"prototype"===o)){var i="static"===o?e:n;this.defineClassElement(i,t)}}),this)}),this)},defineClassElement:function(e,t){var n=t.descriptor;if("field"===t.kind){var r=t.initializer;n={enumerable:n.enumerable,writable:n.writable,configurable:n.configurable,value:void 0===r?void 0:r.call(e)}}Object.defineProperty(e,t.key,n)},decorateClass:function(e,t){var n=[],r=[],o={static:[],prototype:[],own:[]};if(e.forEach((function(e){this.addElementPlacement(e,o)}),this),e.forEach((function(e){if(!C(e))return n.push(e);var t=this.decorateElement(e,o);n.push(t.element),n.push.apply(n,t.extras),r.push.apply(r,t.finishers)}),this),!t)return{elements:n,finishers:r};var i=this.decorateConstructor(n,t);return r.push.apply(r,i.finishers),i.finishers=r,i},addElementPlacement:function(e,t,n){var r=t[e.placement];if(!n&&-1!==r.indexOf(e.key))throw new TypeError("Duplicated element ("+e.key+")");r.push(e.key)},decorateElement:function(e,t){for(var n=[],r=[],o=e.decorators,i=o.length-1;i>=0;i--){var s=t[e.placement];s.splice(s.indexOf(e.key),1);var a=this.fromElementDescriptor(e),c=this.toElementFinisherExtras((0,o[i])(a)||a);e=c.element,this.addElementPlacement(e,t),c.finisher&&r.push(c.finisher);var l=c.extras;if(l){for(var u=0;u<l.length;u++)this.addElementPlacement(l[u],t);n.push.apply(n,l)}}return{element:e,finishers:r,extras:n}},decorateConstructor:function(e,t){for(var n=[],r=t.length-1;r>=0;r--){var o=this.fromClassDescriptor(e),i=this.toClassDescriptor((0,t[r])(o)||o);if(void 0!==i.finisher&&n.push(i.finisher),void 0!==i.elements){e=i.elements;for(var s=0;s<e.length-1;s++)for(var a=s+1;a<e.length;a++)if(e[s].key===e[a].key&&e[s].placement===e[a].placement)throw new TypeError("Duplicated element ("+e[s].key+")")}}return{elements:e,finishers:n}},fromElementDescriptor:function(e){var t={kind:e.kind,key:e.key,placement:e.placement,descriptor:e.descriptor};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),"field"===e.kind&&(t.initializer=e.initializer),t},toElementDescriptors:function(e){var t;if(void 0!==e)return(t=e,function(e){if(Array.isArray(e))return e}(t)||function(e){if("undefined"!=typeof Symbol&&Symbol.iterator in Object(e))return Array.from(e)}(t)||function(e,t){if(e){if("string"==typeof e)return F(e,t);var n=Object.prototype.toString.call(e).slice(8,-1);return"Object"===n&&e.constructor&&(n=e.constructor.name),"Map"===n||"Set"===n?Array.from(n):"Arguments"===n||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)?F(e,t):void 0}}(t)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()).map((function(e){var t=this.toElementDescriptor(e);return this.disallowProperty(e,"finisher","An element descriptor"),this.disallowProperty(e,"extras","An element descriptor"),t}),this)},toElementDescriptor:function(e){var t=String(e.kind);if("method"!==t&&"field"!==t)throw new TypeError('An element descriptor\'s .kind property must be either "method" or "field", but a decorator created an element descriptor with .kind "'+t+'"');var n=z(e.key),r=String(e.placement);if("static"!==r&&"prototype"!==r&&"own"!==r)throw new TypeError('An element descriptor\'s .placement property must be one of "static", "prototype" or "own", but a decorator created an element descriptor with .placement "'+r+'"');var o=e.descriptor;this.disallowProperty(e,"elements","An element descriptor");var i={kind:t,key:n,placement:r,descriptor:Object.assign({},o)};return"field"!==t?this.disallowProperty(e,"initializer","A method descriptor"):(this.disallowProperty(o,"get","The property descriptor of a field descriptor"),this.disallowProperty(o,"set","The property descriptor of a field descriptor"),this.disallowProperty(o,"value","The property descriptor of a field descriptor"),i.initializer=e.initializer),i},toElementFinisherExtras:function(e){return{element:this.toElementDescriptor(e),finisher:T(e,"finisher"),extras:this.toElementDescriptors(e.extras)}},fromClassDescriptor:function(e){var t={kind:"class",elements:e.map(this.fromElementDescriptor,this)};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),t},toClassDescriptor:function(e){var t=String(e.kind);if("class"!==t)throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator created a class descriptor with .kind "'+t+'"');this.disallowProperty(e,"key","A class descriptor"),this.disallowProperty(e,"placement","A class descriptor"),this.disallowProperty(e,"descriptor","A class descriptor"),this.disallowProperty(e,"initializer","A class descriptor"),this.disallowProperty(e,"extras","A class descriptor");var n=T(e,"finisher");return{elements:this.toElementDescriptors(e.elements),finisher:n}},runClassFinishers:function(e,t){for(var n=0;n<t.length;n++){var r=(0,t[n])(e);if(void 0!==r){if("function"!=typeof r)throw new TypeError("Finishers must return a constructor.");e=r}}return e},disallowProperty:function(e,t,n){if(void 0!==e[t])throw new TypeError(n+" can't have a ."+t+" property.")}};return e}();if(r)for(var i=0;i<r.length;i++)o=r[i](o);var s=t((function(e){o.initializeInstanceElements(e,a.elements)}),n),a=o.decorateClass(function(e){for(var t=[],n=function(e){return"method"===e.kind&&e.key===i.key&&e.placement===i.placement},r=0;r<e.length;r++){var o,i=e[r];if("method"===i.kind&&(o=t.find(n)))if(R(i.descriptor)||R(o.descriptor)){if(C(i)||C(o))throw new ReferenceError("Duplicated methods ("+i.key+") can't be decorated.");o.descriptor=i.descriptor}else{if(C(i)){if(C(o))throw new ReferenceError("Decorators can't be placed on different accessors with for the same property ("+i.key+").");o.decorators=i.decorators}D(i,o)}else t.push(i)}return t}(s.d.map(S)),e);o.initializeClassElements(s.F,a.elements),o.runClassFinishers(s.F,a.finishers)}([Object(o.d)("dialog-hassio-snapshot")],(function(e,t){var n,l,b,w,S;return{F:function(t){!function(e,t){if("function"!=typeof t&&null!==t)throw new TypeError("Super expression must either be null or a function");e.prototype=Object.create(t&&t.prototype,{constructor:{value:e,writable:!0,configurable:!0}}),t&&O(e,t)}(o,t);var n,r=(n=o,function(){var e,t=A(n);if(x()){var r=A(this).constructor;e=Reflect.construct(t,arguments,r)}else e=t.apply(this,arguments);return P(this,e)});function o(){var t;E(this,o);for(var n=arguments.length,i=new Array(n),s=0;s<n;s++)i[s]=arguments[s];return t=r.call.apply(r,[this].concat(i)),e(j(t)),t}return o}(t),d:[{kind:"field",decorators:[Object(o.h)({attribute:!1})],key:"hass",value:void 0},{kind:"field",decorators:[Object(o.g)()],key:"_error",value:void 0},{kind:"field",decorators:[Object(o.g)()],key:"_snapshot",value:void 0},{kind:"field",decorators:[Object(o.g)()],key:"_folders",value:void 0},{kind:"field",decorators:[Object(o.g)()],key:"_addons",value:void 0},{kind:"field",decorators:[Object(o.g)()],key:"_dialogParams",value:void 0},{kind:"field",decorators:[Object(o.g)()],key:"_snapshotPassword",value:void 0},{kind:"field",decorators:[Object(o.g)()],key:"_restoreHass",value:function(){return!0}},{kind:"method",key:"showDialog",value:(S=_(regeneratorRuntime.mark((function e(t){return regeneratorRuntime.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return e.next=2,Object(s.c)(this.hass,t.slug);case 2:this._snapshot=e.sent,this._folders=(r=this._snapshot.folders,o=void 0,o=[],r.includes("homeassistant")&&o.push({slug:"homeassistant",name:"Home Assistant configuration",checked:!0}),r.includes("ssl")&&o.push({slug:"ssl",name:"SSL",checked:!0}),r.includes("share")&&o.push({slug:"share",name:"Share",checked:!0}),r.includes("addons/local")&&o.push({slug:"addons/local",name:"Local add-ons",checked:!0}),o).sort((function(e,t){return e.name>t.name?1:-1})),this._addons=(n=this._snapshot.addons,n.map((function(e){return{slug:e.slug,name:e.name,version:e.version,checked:!0}}))).sort((function(e,t){return e.name>t.name?1:-1})),this._dialogParams=t;case 6:case"end":return e.stop()}var n,r,o}),e,this)}))),function(e){return S.apply(this,arguments)})},{kind:"method",key:"render",value:function(){var e=this;return this._dialogParams&&this._snapshot?Object(o.f)(g(),this._closeDialog,Object(i.a)(this.hass,this._computeName),"full"===this._snapshot.type?"Full snapshot":"Partial snapshot",this._computeSize,this._formatDatetime(this._snapshot.date),this._restoreHass,(function(t){e._restoreHass=t.target.checked}),this._snapshot.homeassistant,this._folders.length?Object(o.f)(y(),this._folders.map((function(t){return Object(o.f)(v(),t.checked,(function(n){return e._updateFolders(t,n.target.checked)}),t.name)}))):"",this._addons.length?Object(o.f)(m(),this._addons.map((function(t){return Object(o.f)(f(),t.checked,(function(n){return e._updateAddons(t,n.target.checked)}),t.name)}))):"",this._snapshot.protected?Object(o.f)(h(),this._passwordInput,this._snapshotPassword):"",this._error?Object(o.f)(p(),this._error):"",this._downloadClicked,r.n,this._partialRestoreClicked,r.s,"full"===this._snapshot.type?Object(o.f)(d(),this._fullRestoreClicked,r.s):"",this._deleteClicked,r.k):Object(o.f)(k())}},{kind:"get",static:!0,key:"styles",value:function(){return[c.d,Object(o.c)(u())]}},{kind:"method",key:"_updateFolders",value:function(e,t){this._folders=this._folders.map((function(n){return n.slug===e.slug&&(n.checked=t),n}))}},{kind:"method",key:"_updateAddons",value:function(e,t){this._addons=this._addons.map((function(n){return n.slug===e.slug&&(n.checked=t),n}))}},{kind:"method",key:"_passwordInput",value:function(e){this._snapshotPassword=e.detail.value}},{kind:"method",key:"_partialRestoreClicked",value:(w=_(regeneratorRuntime.mark((function e(){var t,n,r,o=this;return regeneratorRuntime.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return e.next=2,Object(a.b)(this,{title:"Are you sure you want partially to restore this snapshot?"});case 2:if(e.sent){e.next=4;break}return e.abrupt("return");case 4:t=this._addons.filter((function(e){return e.checked})).map((function(e){return e.slug})),n=this._folders.filter((function(e){return e.checked})).map((function(e){return e.slug})),r={homeassistant:this._restoreHass,addons:t,folders:n},this._snapshot.protected&&(r.password=this._snapshotPassword),this.hass.callApi("POST","hassio/snapshots/".concat(this._snapshot.slug,"/restore/partial"),r).then((function(){alert("Snapshot restored!"),o._closeDialog()}),(function(e){o._error=e.body.message}));case 9:case"end":return e.stop()}}),e,this)}))),function(){return w.apply(this,arguments)})},{kind:"method",key:"_fullRestoreClicked",value:(b=_(regeneratorRuntime.mark((function e(){var t,n=this;return regeneratorRuntime.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return e.next=2,Object(a.b)(this,{title:"Are you sure you want to wipe your system and restore this snapshot?"});case 2:if(e.sent){e.next=4;break}return e.abrupt("return");case 4:t=this._snapshot.protected?{password:this._snapshotPassword}:void 0,this.hass.callApi("POST","hassio/snapshots/".concat(this._snapshot.slug,"/restore/full"),t).then((function(){alert("Snapshot restored!"),n._closeDialog()}),(function(e){n._error=e.body.message}));case 6:case"end":return e.stop()}}),e,this)}))),function(){return b.apply(this,arguments)})},{kind:"method",key:"_deleteClicked",value:(l=_(regeneratorRuntime.mark((function e(){var t=this;return regeneratorRuntime.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return e.next=2,Object(a.b)(this,{title:"Are you sure you want to delete this snapshot?"});case 2:if(e.sent){e.next=4;break}return e.abrupt("return");case 4:this.hass.callApi("POST","hassio/snapshots/".concat(this._snapshot.slug,"/remove")).then((function(){t._dialogParams.onDelete(),t._closeDialog()}),(function(e){t._error=e.body.message}));case 5:case"end":return e.stop()}}),e,this)}))),function(){return l.apply(this,arguments)})},{kind:"method",key:"_downloadClicked",value:(n=_(regeneratorRuntime.mark((function e(){var t,n,r;return regeneratorRuntime.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return e.prev=0,e.next=3,o=this.hass,i="/api/hassio/snapshots/".concat(this._snapshot.slug,"/download"),o.callWS({type:"auth/sign_path",path:i});case 3:t=e.sent,e.next=10;break;case 6:return e.prev=6,e.t0=e.catch(0),alert("Error: ".concat(e.t0.message)),e.abrupt("return");case 10:n=this._computeName.replace(/[^a-z0-9]+/gi,"_"),(r=document.createElement("a")).href=t.path,r.download="Hass_io_".concat(n,".tar"),this.shadowRoot.appendChild(r),r.click(),this.shadowRoot.removeChild(r);case 17:case"end":return e.stop()}var o,i}),e,this,[[0,6]])}))),function(){return n.apply(this,arguments)})},{kind:"get",key:"_computeName",value:function(){return this._snapshot?this._snapshot.name||this._snapshot.slug:"Unnamed snapshot"}},{kind:"get",key:"_computeSize",value:function(){return Math.ceil(10*this._snapshot.size)/10+" MB"}},{kind:"method",key:"_formatDatetime",value:function(e){return new Date(e).toLocaleDateString(navigator.language,{weekday:"long",year:"numeric",month:"short",day:"numeric",hour:"numeric",minute:"2-digit"})}},{kind:"method",key:"_closeDialog",value:function(){this._dialogParams=void 0,this._snapshot=void 0,this._snapshotPassword="",this._folders=[],this._addons=[]}}]}}),o.a)}}]);
//# sourceMappingURL=chunk.76cd2f7f90bec6f08e4a.js.map