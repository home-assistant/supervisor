(self.webpackChunkhome_assistant_frontend=self.webpackChunkhome_assistant_frontend||[]).push([[817],{60817:function(e,t,n){"use strict";n.r(t);n(30573);var r=n(55317),o=(n(76480),n(77956),n(99722)),i=n(68928),s=n(43274).Op?function(e,t){return e.toLocaleString(t.language,{year:"numeric",month:"long",day:"numeric",hour:"numeric",minute:"2-digit"})}:function(e){return(0,i.WU)(e,"MMMM D, YYYY, HH:mm")},a=n(47181);n(23221),n(52039);"".concat(location.protocol,"//").concat(location.host);var c,u,l,d,h,p,f,m,g,v,y,b,k,w=n(41682),_=n(77097),S=n(26765),D=n(11654);function x(e){return(x="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(e){return typeof e}:function(e){return e&&"function"==typeof Symbol&&e.constructor===Symbol&&e!==Symbol.prototype?"symbol":typeof e})(e)}function M(e,t){return t||(t=e.slice(0)),Object.freeze(Object.defineProperties(e,{raw:{value:Object.freeze(t)}}))}function P(e,t,n,r,o,i,s){try{var a=e[i](s),c=a.value}catch(u){return void n(u)}a.done?t(c):Promise.resolve(c).then(r,o)}function E(e){return function(){var t=this,n=arguments;return new Promise((function(r,o){var i=e.apply(t,n);function s(e){P(i,r,o,s,a,"next",e)}function a(e){P(i,r,o,s,a,"throw",e)}s(void 0)}))}}function Y(e,t){if(!(e instanceof t))throw new TypeError("Cannot call a class as a function")}function T(e,t){return(T=Object.setPrototypeOf||function(e,t){return e.__proto__=t,e})(e,t)}function A(e){var t=function(){if("undefined"==typeof Reflect||!Reflect.construct)return!1;if(Reflect.construct.sham)return!1;if("function"==typeof Proxy)return!0;try{return Boolean.prototype.valueOf.call(Reflect.construct(Boolean,[],(function(){}))),!0}catch(e){return!1}}();return function(){var n,r=R(e);if(t){var o=R(this).constructor;n=Reflect.construct(r,arguments,o)}else n=r.apply(this,arguments);return C(this,n)}}function C(e,t){return!t||"object"!==x(t)&&"function"!=typeof t?O(e):t}function O(e){if(void 0===e)throw new ReferenceError("this hasn't been initialised - super() hasn't been called");return e}function R(e){return(R=Object.setPrototypeOf?Object.getPrototypeOf:function(e){return e.__proto__||Object.getPrototypeOf(e)})(e)}function H(){H=function(){return e};var e={elementsDefinitionOrder:[["method"],["field"]],initializeInstanceElements:function(e,t){["method","field"].forEach((function(n){t.forEach((function(t){t.kind===n&&"own"===t.placement&&this.defineClassElement(e,t)}),this)}),this)},initializeClassElements:function(e,t){var n=e.prototype;["method","field"].forEach((function(r){t.forEach((function(t){var o=t.placement;if(t.kind===r&&("static"===o||"prototype"===o)){var i="static"===o?e:n;this.defineClassElement(i,t)}}),this)}),this)},defineClassElement:function(e,t){var n=t.descriptor;if("field"===t.kind){var r=t.initializer;n={enumerable:n.enumerable,writable:n.writable,configurable:n.configurable,value:void 0===r?void 0:r.call(e)}}Object.defineProperty(e,t.key,n)},decorateClass:function(e,t){var n=[],r=[],o={static:[],prototype:[],own:[]};if(e.forEach((function(e){this.addElementPlacement(e,o)}),this),e.forEach((function(e){if(!N(e))return n.push(e);var t=this.decorateElement(e,o);n.push(t.element),n.push.apply(n,t.extras),r.push.apply(r,t.finishers)}),this),!t)return{elements:n,finishers:r};var i=this.decorateConstructor(n,t);return r.push.apply(r,i.finishers),i.finishers=r,i},addElementPlacement:function(e,t,n){var r=t[e.placement];if(!n&&-1!==r.indexOf(e.key))throw new TypeError("Duplicated element ("+e.key+")");r.push(e.key)},decorateElement:function(e,t){for(var n=[],r=[],o=e.decorators,i=o.length-1;i>=0;i--){var s=t[e.placement];s.splice(s.indexOf(e.key),1);var a=this.fromElementDescriptor(e),c=this.toElementFinisherExtras((0,o[i])(a)||a);e=c.element,this.addElementPlacement(e,t),c.finisher&&r.push(c.finisher);var u=c.extras;if(u){for(var l=0;l<u.length;l++)this.addElementPlacement(u[l],t);n.push.apply(n,u)}}return{element:e,finishers:r,extras:n}},decorateConstructor:function(e,t){for(var n=[],r=t.length-1;r>=0;r--){var o=this.fromClassDescriptor(e),i=this.toClassDescriptor((0,t[r])(o)||o);if(void 0!==i.finisher&&n.push(i.finisher),void 0!==i.elements){e=i.elements;for(var s=0;s<e.length-1;s++)for(var a=s+1;a<e.length;a++)if(e[s].key===e[a].key&&e[s].placement===e[a].placement)throw new TypeError("Duplicated element ("+e[s].key+")")}}return{elements:e,finishers:n}},fromElementDescriptor:function(e){var t={kind:e.kind,key:e.key,placement:e.placement,descriptor:e.descriptor};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),"field"===e.kind&&(t.initializer=e.initializer),t},toElementDescriptors:function(e){var t;if(void 0!==e)return(t=e,function(e){if(Array.isArray(e))return e}(t)||function(e){if("undefined"!=typeof Symbol&&null!=e[Symbol.iterator]||null!=e["@@iterator"])return Array.from(e)}(t)||function(e,t){if(e){if("string"==typeof e)return I(e,t);var n=Object.prototype.toString.call(e).slice(8,-1);return"Object"===n&&e.constructor&&(n=e.constructor.name),"Map"===n||"Set"===n?Array.from(e):"Arguments"===n||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)?I(e,t):void 0}}(t)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()).map((function(e){var t=this.toElementDescriptor(e);return this.disallowProperty(e,"finisher","An element descriptor"),this.disallowProperty(e,"extras","An element descriptor"),t}),this)},toElementDescriptor:function(e){var t=String(e.kind);if("method"!==t&&"field"!==t)throw new TypeError('An element descriptor\'s .kind property must be either "method" or "field", but a decorator created an element descriptor with .kind "'+t+'"');var n=L(e.key),r=String(e.placement);if("static"!==r&&"prototype"!==r&&"own"!==r)throw new TypeError('An element descriptor\'s .placement property must be one of "static", "prototype" or "own", but a decorator created an element descriptor with .placement "'+r+'"');var o=e.descriptor;this.disallowProperty(e,"elements","An element descriptor");var i={kind:t,key:n,placement:r,descriptor:Object.assign({},o)};return"field"!==t?this.disallowProperty(e,"initializer","A method descriptor"):(this.disallowProperty(o,"get","The property descriptor of a field descriptor"),this.disallowProperty(o,"set","The property descriptor of a field descriptor"),this.disallowProperty(o,"value","The property descriptor of a field descriptor"),i.initializer=e.initializer),i},toElementFinisherExtras:function(e){return{element:this.toElementDescriptor(e),finisher:B(e,"finisher"),extras:this.toElementDescriptors(e.extras)}},fromClassDescriptor:function(e){var t={kind:"class",elements:e.map(this.fromElementDescriptor,this)};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),t},toClassDescriptor:function(e){var t=String(e.kind);if("class"!==t)throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator created a class descriptor with .kind "'+t+'"');this.disallowProperty(e,"key","A class descriptor"),this.disallowProperty(e,"placement","A class descriptor"),this.disallowProperty(e,"descriptor","A class descriptor"),this.disallowProperty(e,"initializer","A class descriptor"),this.disallowProperty(e,"extras","A class descriptor");var n=B(e,"finisher");return{elements:this.toElementDescriptors(e.elements),finisher:n}},runClassFinishers:function(e,t){for(var n=0;n<t.length;n++){var r=(0,t[n])(e);if(void 0!==r){if("function"!=typeof r)throw new TypeError("Finishers must return a constructor.");e=r}}return e},disallowProperty:function(e,t,n){if(void 0!==e[t])throw new TypeError(n+" can't have a ."+t+" property.")}};return e}function j(e){var t,n=L(e.key);"method"===e.kind?t={value:e.value,writable:!0,configurable:!0,enumerable:!1}:"get"===e.kind?t={get:e.value,configurable:!0,enumerable:!1}:"set"===e.kind?t={set:e.value,configurable:!0,enumerable:!1}:"field"===e.kind&&(t={configurable:!0,writable:!0,enumerable:!0});var r={kind:"field"===e.kind?"field":"method",key:n,placement:e.static?"static":"field"===e.kind?"own":"prototype",descriptor:t};return e.decorators&&(r.decorators=e.decorators),"field"===e.kind&&(r.initializer=e.value),r}function z(e,t){void 0!==e.descriptor.get?t.descriptor.get=e.descriptor.get:t.descriptor.set=e.descriptor.set}function N(e){return e.decorators&&e.decorators.length}function F(e){return void 0!==e&&!(void 0===e.value&&void 0===e.writable)}function B(e,t){var n=e[t];if(void 0!==n&&"function"!=typeof n)throw new TypeError("Expected '"+t+"' to be a function");return n}function L(e){var t=function(e,t){if("object"!==x(e)||null===e)return e;var n=e[Symbol.toPrimitive];if(void 0!==n){var r=n.call(e,t||"default");if("object"!==x(r))return r;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===t?String:Number)(e)}(e,"string");return"symbol"===x(t)?t:String(t)}function I(e,t){(null==t||t>e.length)&&(t=e.length);for(var n=0,r=new Array(t);n<t;n++)r[n]=e[n];return r}!function(e,t,n,r){var o=H();if(r)for(var i=0;i<r.length;i++)o=r[i](o);var s=t((function(e){o.initializeInstanceElements(e,a.elements)}),n),a=o.decorateClass(function(e){for(var t=[],n=function(e){return"method"===e.kind&&e.key===i.key&&e.placement===i.placement},r=0;r<e.length;r++){var o,i=e[r];if("method"===i.kind&&(o=t.find(n)))if(F(i.descriptor)||F(o.descriptor)){if(N(i)||N(o))throw new ReferenceError("Duplicated methods ("+i.key+") can't be decorated.");o.descriptor=i.descriptor}else{if(N(i)){if(N(o))throw new ReferenceError("Decorators can't be placed on different accessors with for the same property ("+i.key+").");o.decorators=i.decorators}z(i,o)}else t.push(i)}return t}(s.d.map(j)),e);o.initializeClassElements(s.F,a.elements),o.runClassFinishers(s.F,a.finishers)}([(0,o.Mo)("dialog-hassio-snapshot")],(function(e,t){var n,i,x,P,C;return{F:function(t){!function(e,t){if("function"!=typeof t&&null!==t)throw new TypeError("Super expression must either be null or a function");e.prototype=Object.create(t&&t.prototype,{constructor:{value:e,writable:!0,configurable:!0}}),t&&T(e,t)}(r,t);var n=A(r);function r(){var t;Y(this,r);for(var o=arguments.length,i=new Array(o),s=0;s<o;s++)i[s]=arguments[s];return t=n.call.apply(n,[this].concat(i)),e(O(t)),t}return r}(t),d:[{kind:"field",decorators:[(0,o.Cb)({attribute:!1})],key:"hass",value:void 0},{kind:"field",decorators:[(0,o.Cb)({attribute:!1})],key:"supervisor",value:void 0},{kind:"field",decorators:[(0,o.SB)()],key:"_error",value:void 0},{kind:"field",decorators:[(0,o.SB)()],key:"_onboarding",value:function(){return!1}},{kind:"field",decorators:[(0,o.SB)()],key:"_snapshot",value:void 0},{kind:"field",decorators:[(0,o.SB)()],key:"_folders",value:void 0},{kind:"field",decorators:[(0,o.SB)()],key:"_addons",value:void 0},{kind:"field",decorators:[(0,o.SB)()],key:"_dialogParams",value:void 0},{kind:"field",decorators:[(0,o.SB)()],key:"_snapshotPassword",value:void 0},{kind:"field",decorators:[(0,o.SB)()],key:"_restoreHass",value:function(){return!0}},{kind:"method",key:"showDialog",value:(C=E(regeneratorRuntime.mark((function e(t){var n,r,o;return regeneratorRuntime.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return e.next=2,(0,_.Ju)(this.hass,t.slug);case 2:this._snapshot=e.sent,this._folders=(s=null===(n=this._snapshot)||void 0===n?void 0:n.folders,a=void 0,a=[],s.includes("homeassistant")&&a.push({slug:"homeassistant",name:"Home Assistant configuration",checked:!0}),s.includes("ssl")&&a.push({slug:"ssl",name:"SSL",checked:!0}),s.includes("share")&&a.push({slug:"share",name:"Share",checked:!0}),s.includes("addons/local")&&a.push({slug:"addons/local",name:"Local add-ons",checked:!0}),a).sort((function(e,t){return e.name>t.name?1:-1})),this._addons=(i=null===(r=this._snapshot)||void 0===r?void 0:r.addons,i.map((function(e){return{slug:e.slug,name:e.name,version:e.version,checked:!0}}))).sort((function(e,t){return e.name>t.name?1:-1})),this._dialogParams=t,this._onboarding=null!==(o=t.onboarding)&&void 0!==o&&o,this.supervisor=t.supervisor,this._snapshot.homeassistant||(this._restoreHass=!1);case 9:case"end":return e.stop()}var i,s,a}),e,this)}))),function(e){return C.apply(this,arguments)})},{kind:"method",key:"render",value:function(){var e=this;return this._dialogParams&&this._snapshot?(0,o.dy)(u||(u=M(["\n      <ha-dialog open @closing="," .heading=",'>\n        <div slot="heading">\n          <ha-header-bar>\n            <span slot="title"> ',' </span>\n            <mwc-icon-button slot="actionItems" dialogAction="cancel">\n              <ha-svg-icon .path=','></ha-svg-icon>\n            </mwc-icon-button>\n          </ha-header-bar>\n        </div>\n        <div class="details">\n          ',"\n          (",")<br />\n          ","\n        </div>\n        ","\n        ","\n        ","\n        ","\n        ",'\n\n        <div class="button-row" slot="primaryAction">\n          <mwc-button @click=',">\n            <ha-svg-icon .path=",' class="icon"></ha-svg-icon>\n            Restore Selected\n          </mwc-button>\n          ','\n        </div>\n        <div class="button-row" slot="secondaryAction">\n          ',"\n          ","\n        </div>\n      </ha-dialog>\n    "])),this._closeDialog,!0,this._computeName,r.r5M,"full"===this._snapshot.type?"Full snapshot":"Partial snapshot",this._computeSize,s(new Date(this._snapshot.date),this.hass.locale),this._snapshot.homeassistant?(0,o.dy)(l||(l=M(["<div>Home Assistant:</div>\n              <paper-checkbox\n                .checked=",'\n                @change="','"\n              >\n                Home Assistant\n                <span class="version">(',")</span>\n              </paper-checkbox>"])),this._restoreHass,(function(t){e._restoreHass=t.target.checked}),this._snapshot.homeassistant):"",this._folders.length?(0,o.dy)(d||(d=M(['\n              <div>Folders:</div>\n              <paper-dialog-scrollable class="no-margin-top">\n                ',"\n              </paper-dialog-scrollable>\n            "])),this._folders.map((function(t){return(0,o.dy)(h||(h=M(["\n                    <paper-checkbox\n                      .checked=",'\n                      @change="','"\n                    >\n                      ',"\n                    </paper-checkbox>\n                  "])),t.checked,(function(n){return e._updateFolders(t,n.target.checked)}),t.name)}))):"",this._addons.length?(0,o.dy)(p||(p=M(['\n              <div>Add-on:</div>\n              <paper-dialog-scrollable class="no-margin-top">\n                ',"\n              </paper-dialog-scrollable>\n            "])),this._addons.map((function(t){return(0,o.dy)(f||(f=M(["\n                    <paper-checkbox\n                      .checked=",'\n                      @change="','"\n                    >\n                      ','\n                      <span class="version">(',")</span>\n                    </paper-checkbox>\n                  "])),t.checked,(function(n){return e._updateAddons(t,n.target.checked)}),t.name,t.version)}))):"",this._snapshot.protected?(0,o.dy)(m||(m=M(['\n              <paper-input\n                autofocus=""\n                label="Password"\n                type="password"\n                @value-changed=',"\n                .value=","\n              ></paper-input>\n            "])),this._passwordInput,this._snapshotPassword):"",this._error?(0,o.dy)(g||(g=M([' <p class="error">Error: ',"</p> "])),this._error):"",this._partialRestoreClicked,r.BBX,this._onboarding?"":(0,o.dy)(v||(v=M(["\n                <mwc-button @click=",">\n                  <ha-svg-icon .path=",' class="icon warning">\n                  </ha-svg-icon>\n                  <span class="warning">Delete Snapshot</span>\n                </mwc-button>\n              '])),this._deleteClicked,r.x9U),"full"===this._snapshot.type?(0,o.dy)(y||(y=M(["\n                <mwc-button @click=",">\n                  <ha-svg-icon .path=",' class="icon"></ha-svg-icon>\n                  Restore Everything\n                </mwc-button>\n              '])),this._fullRestoreClicked,r.BBX):"",this._onboarding?"":(0,o.dy)(b||(b=M(["<mwc-button @click=",">\n                <ha-svg-icon .path=",' class="icon"></ha-svg-icon>\n                Download Snapshot\n              </mwc-button>'])),this._downloadClicked,r.OGU)):(0,o.dy)(c||(c=M([""])))}},{kind:"get",static:!0,key:"styles",value:function(){return[D.Qx,D.yu,(0,o.iv)(k||(k=M(["\n        paper-checkbox {\n          display: block;\n          margin: 4px;\n        }\n        mwc-button ha-svg-icon {\n          margin-right: 4px;\n        }\n        .button-row {\n          display: grid;\n          gap: 8px;\n          margin-right: 8px;\n        }\n        .details {\n          color: var(--secondary-text-color);\n        }\n        .warning,\n        .error {\n          color: var(--error-color);\n        }\n        .buttons li {\n          list-style-type: none;\n        }\n        .buttons .icon {\n          margin-right: 16px;\n        }\n        .no-margin-top {\n          margin-top: 0;\n        }\n        span.version {\n          color: var(--secondary-text-color);\n        }\n        ha-header-bar {\n          --mdc-theme-on-primary: var(--primary-text-color);\n          --mdc-theme-primary: var(--mdc-theme-surface);\n          flex-shrink: 0;\n        }\n        /* overrule the ha-style-dialog max-height on small screens */\n        @media all and (max-width: 450px), all and (max-height: 500px) {\n          ha-header-bar {\n            --mdc-theme-primary: var(--app-header-background-color);\n            --mdc-theme-on-primary: var(--app-header-text-color, white);\n          }\n        }\n      "])))]}},{kind:"method",key:"_updateFolders",value:function(e,t){this._folders=this._folders.map((function(n){return n.slug===e.slug&&(n.checked=t),n}))}},{kind:"method",key:"_updateAddons",value:function(e,t){this._addons=this._addons.map((function(n){return n.slug===e.slug&&(n.checked=t),n}))}},{kind:"method",key:"_passwordInput",value:function(e){this._snapshotPassword=e.detail.value}},{kind:"method",key:"_partialRestoreClicked",value:(P=E(regeneratorRuntime.mark((function e(){var t,n,r,o=this;return regeneratorRuntime.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:if(void 0===this.supervisor||"running"===this.supervisor.info.state){e.next=4;break}return e.next=3,(0,S.Ys)(this,{title:"Could not restore snapshot",text:"Restoring a snapshot is not possible right now because the system is in ".concat(this.supervisor.info.state," state.")});case 3:return e.abrupt("return");case 4:return e.next=6,(0,S.g7)(this,{title:"Are you sure you want partially to restore this snapshot?",confirmText:"restore",dismissText:"cancel"});case 6:if(e.sent){e.next=8;break}return e.abrupt("return");case 8:t=this._addons.filter((function(e){return e.checked})).map((function(e){return e.slug})),n=this._folders.filter((function(e){return e.checked})).map((function(e){return e.slug})),r={homeassistant:this._restoreHass,addons:t,folders:n},this._snapshot.protected&&(r.password=this._snapshotPassword),this._onboarding?((0,a.B)(this,"restoring"),fetch("/api/hassio/snapshots/".concat(this._snapshot.slug,"/restore/partial"),{method:"POST",body:JSON.stringify(r)}),this._closeDialog()):this.hass.callApi("POST","hassio/snapshots/".concat(this._snapshot.slug,"/restore/partial"),r).then((function(){alert("Snapshot restored!"),o._closeDialog()}),(function(e){o._error=e.body.message}));case 13:case"end":return e.stop()}}),e,this)}))),function(){return P.apply(this,arguments)})},{kind:"method",key:"_fullRestoreClicked",value:(x=E(regeneratorRuntime.mark((function e(){var t,n=this;return regeneratorRuntime.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:if(void 0===this.supervisor||"running"===this.supervisor.info.state){e.next=4;break}return e.next=3,(0,S.Ys)(this,{title:"Could not restore snapshot",text:"Restoring a snapshot is not possible right now because the system is in ".concat(this.supervisor.info.state," state.")});case 3:return e.abrupt("return");case 4:return e.next=6,(0,S.g7)(this,{title:"Are you sure you want to wipe your system and restore this snapshot?",confirmText:"restore",dismissText:"cancel"});case 6:if(e.sent){e.next=8;break}return e.abrupt("return");case 8:t=this._snapshot.protected?{password:this._snapshotPassword}:void 0,this._onboarding?((0,a.B)(this,"restoring"),fetch("/api/hassio/snapshots/".concat(this._snapshot.slug,"/restore/full"),{method:"POST",body:JSON.stringify(t)}),this._closeDialog()):this.hass.callApi("POST","hassio/snapshots/".concat(this._snapshot.slug,"/restore/full"),t).then((function(){alert("Snapshot restored!"),n._closeDialog()}),(function(e){n._error=e.body.message}));case 10:case"end":return e.stop()}}),e,this)}))),function(){return x.apply(this,arguments)})},{kind:"method",key:"_deleteClicked",value:(i=E(regeneratorRuntime.mark((function e(){var t=this;return regeneratorRuntime.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return e.next=2,(0,S.g7)(this,{title:"Are you sure you want to delete this snapshot?",confirmText:"delete",dismissText:"cancel"});case 2:if(e.sent){e.next=4;break}return e.abrupt("return");case 4:this.hass.callApi("POST","hassio/snapshots/".concat(this._snapshot.slug,"/remove")).then((function(){t._dialogParams.onDelete&&t._dialogParams.onDelete(),t._closeDialog()}),(function(e){t._error=e.body.message}));case 5:case"end":return e.stop()}}),e,this)}))),function(){return i.apply(this,arguments)})},{kind:"method",key:"_downloadClicked",value:(n=E(regeneratorRuntime.mark((function e(){var t,n,r;return regeneratorRuntime.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return e.prev=0,e.next=3,o=this.hass,i="/api/hassio/snapshots/".concat(this._snapshot.slug,"/download"),o.callWS({type:"auth/sign_path",path:i});case 3:t=e.sent,e.next=10;break;case 6:return e.prev=6,e.t0=e.catch(0),alert("Error: ".concat((0,w.js)(e.t0))),e.abrupt("return");case 10:if(!window.location.href.includes("ui.nabu.casa")){e.next=16;break}return e.next=13,(0,S.g7)(this,{title:"Potential slow download",text:"Downloading snapshots over the Nabu Casa URL will take some time, it is recomended to use your local URL instead, do you want to continue?",confirmText:"continue",dismissText:"cancel"});case 13:if(e.sent){e.next=16;break}return e.abrupt("return");case 16:n=this._computeName.replace(/[^a-z0-9]+/gi,"_"),(r=document.createElement("a")).href=t.path,r.download="Hass_io_".concat(n,".tar"),this.shadowRoot.appendChild(r),r.click(),this.shadowRoot.removeChild(r);case 23:case"end":return e.stop()}var o,i}),e,this,[[0,6]])}))),function(){return n.apply(this,arguments)})},{kind:"get",key:"_computeName",value:function(){return this._snapshot?this._snapshot.name||this._snapshot.slug:"Unnamed snapshot"}},{kind:"get",key:"_computeSize",value:function(){return Math.ceil(10*this._snapshot.size)/10+" MB"}},{kind:"method",key:"_closeDialog",value:function(){this._dialogParams=void 0,this._snapshot=void 0,this._snapshotPassword="",this._folders=[],this._addons=[]}}]}}),o.oi)},68928:function(e,t,n){"use strict";n.d(t,{WU:function(){return D}});var r=/d{1,4}|M{1,4}|YY(?:YY)?|S{1,3}|Do|ZZ|Z|([HhMsDm])\1?|[aA]|"[^"]*"|'[^']*'/g,o="[1-9]\\d?",i="\\d\\d",s="[^\\s]+",a=/\[([^]*?)\]/gm;function c(e,t){for(var n=[],r=0,o=e.length;r<o;r++)n.push(e[r].substr(0,t));return n}var u=function(e){return function(t,n){var r=n[e].map((function(e){return e.toLowerCase()})).indexOf(t.toLowerCase());return r>-1?r:null}};function l(e){for(var t=[],n=1;n<arguments.length;n++)t[n-1]=arguments[n];for(var r=0,o=t;r<o.length;r++){var i=o[r];for(var s in i)e[s]=i[s]}return e}var d=["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"],h=["January","February","March","April","May","June","July","August","September","October","November","December"],p=c(h,3),f={dayNamesShort:c(d,3),dayNames:d,monthNamesShort:p,monthNames:h,amPm:["am","pm"],DoFn:function(e){return e+["th","st","nd","rd"][e%10>3?0:(e-e%10!=10?1:0)*e%10]}},m=l({},f),g=function(e,t){for(void 0===t&&(t=2),e=String(e);e.length<t;)e="0"+e;return e},v={D:function(e){return String(e.getDate())},DD:function(e){return g(e.getDate())},Do:function(e,t){return t.DoFn(e.getDate())},d:function(e){return String(e.getDay())},dd:function(e){return g(e.getDay())},ddd:function(e,t){return t.dayNamesShort[e.getDay()]},dddd:function(e,t){return t.dayNames[e.getDay()]},M:function(e){return String(e.getMonth()+1)},MM:function(e){return g(e.getMonth()+1)},MMM:function(e,t){return t.monthNamesShort[e.getMonth()]},MMMM:function(e,t){return t.monthNames[e.getMonth()]},YY:function(e){return g(String(e.getFullYear()),4).substr(2)},YYYY:function(e){return g(e.getFullYear(),4)},h:function(e){return String(e.getHours()%12||12)},hh:function(e){return g(e.getHours()%12||12)},H:function(e){return String(e.getHours())},HH:function(e){return g(e.getHours())},m:function(e){return String(e.getMinutes())},mm:function(e){return g(e.getMinutes())},s:function(e){return String(e.getSeconds())},ss:function(e){return g(e.getSeconds())},S:function(e){return String(Math.round(e.getMilliseconds()/100))},SS:function(e){return g(Math.round(e.getMilliseconds()/10),2)},SSS:function(e){return g(e.getMilliseconds(),3)},a:function(e,t){return e.getHours()<12?t.amPm[0]:t.amPm[1]},A:function(e,t){return e.getHours()<12?t.amPm[0].toUpperCase():t.amPm[1].toUpperCase()},ZZ:function(e){var t=e.getTimezoneOffset();return(t>0?"-":"+")+g(100*Math.floor(Math.abs(t)/60)+Math.abs(t)%60,4)},Z:function(e){var t=e.getTimezoneOffset();return(t>0?"-":"+")+g(Math.floor(Math.abs(t)/60),2)+":"+g(Math.abs(t)%60,2)}},y=function(e){return+e-1},b=[null,o],k=[null,s],w=["isPm",s,function(e,t){var n=e.toLowerCase();return n===t.amPm[0]?0:n===t.amPm[1]?1:null}],_=["timezoneOffset","[^\\s]*?[\\+\\-]\\d\\d:?\\d\\d|[^\\s]*?Z?",function(e){var t=(e+"").match(/([+-]|\d\d)/gi);if(t){var n=60*+t[1]+parseInt(t[2],10);return"+"===t[0]?n:-n}return 0}],S=(u("monthNamesShort"),u("monthNames"),{default:"ddd MMM DD YYYY HH:mm:ss",shortDate:"M/D/YY",mediumDate:"MMM D, YYYY",longDate:"MMMM D, YYYY",fullDate:"dddd, MMMM D, YYYY",isoDate:"YYYY-MM-DD",isoDateTime:"YYYY-MM-DDTHH:mm:ssZ",shortTime:"HH:mm",mediumTime:"HH:mm:ss",longTime:"HH:mm:ss.SSS"}),D=function(e,t,n){if(void 0===t&&(t=S.default),void 0===n&&(n={}),"number"==typeof e&&(e=new Date(e)),"[object Date]"!==Object.prototype.toString.call(e)||isNaN(e.getTime()))throw new Error("Invalid Date pass to format");var o=[];t=(t=S[t]||t).replace(a,(function(e,t){return o.push(t),"@@@"}));var i=l(l({},m),n);return(t=t.replace(r,(function(t){return v[t](e,i)}))).replace(/@@@/g,(function(){return o.shift()}))}},43274:function(e,t,n){"use strict";n.d(t,{Sb:function(){return r},Op:function(){return o}});var r=function(){try{(new Date).toLocaleDateString("i")}catch(e){return"RangeError"===e.name}return!1}(),o=(function(){try{(new Date).toLocaleTimeString("i")}catch(e){return"RangeError"===e.name}}(),function(){try{(new Date).toLocaleString("i")}catch(e){return"RangeError"===e.name}return!1}())}}]);
//# sourceMappingURL=chunk.a31c7cda7cf3085fe8d6.js.map