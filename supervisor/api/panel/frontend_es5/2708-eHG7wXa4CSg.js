"use strict";(self.webpackChunkhome_assistant_frontend=self.webpackChunkhome_assistant_frontend||[]).push([[2708],{52708:function(e,t,n){n.r(t);var i,r,a,o,s,l,c=n(99312),d=n(81043),u=n(88962),v=n(33368),h=n(71650),f=n(82390),m=n(69205),g=n(70906),p=n(91808),k=(n(44577),n(68144)),y=n(79932),b=n(14516),w=n(47181),Z=(n(76870),n(65189),n(86630),n(41682)),E=n(35460),_=n(26765),z=n(11654),x=(0,b.Z)((function(e){var t=""!==e.host.disk_life_time?30:10,n=1e3*e.host.disk_used/60/t,i=4*e.host.startup_time/60;return 10*Math.ceil((n+i)/10)}));(0,p.Z)([(0,y.Mo)("dialog-hassio-datadisk")],(function(e,t){var n,p=function(t){(0,m.Z)(i,t);var n=(0,g.Z)(i);function i(){var t;(0,h.Z)(this,i);for(var r=arguments.length,a=new Array(r),o=0;o<r;o++)a[o]=arguments[o];return t=n.call.apply(n,[this].concat(a)),e((0,f.Z)(t)),t}return(0,v.Z)(i)}(t);return{F:p,d:[{kind:"field",decorators:[(0,y.Cb)({attribute:!1})],key:"hass",value:void 0},{kind:"field",decorators:[(0,y.SB)()],key:"dialogParams",value:void 0},{kind:"field",decorators:[(0,y.SB)()],key:"selectedDevice",value:void 0},{kind:"field",decorators:[(0,y.SB)()],key:"devices",value:void 0},{kind:"field",decorators:[(0,y.SB)()],key:"moving",value:function(){return!1}},{kind:"method",key:"showDialog",value:function(e){var t=this;this.dialogParams=e,(0,E.ou)(this.hass).then((function(e){t.devices=e.devices}))}},{kind:"method",key:"closeDialog",value:function(){this.dialogParams=void 0,this.selectedDevice=void 0,this.devices=void 0,this.moving=!1,(0,w.B)(this,"dialog-closed",{dialog:this.localName})}},{kind:"method",key:"render",value:function(){var e;return this.dialogParams?(0,k.dy)(i||(i=(0,u.Z)([' <ha-dialog open scrimClickAction escapeKeyAction .heading="','" @closed="','" ?hideActions="','"> '," </ha-dialog> "])),this.moving?this.dialogParams.supervisor.localize("dialog.datadisk_move.moving"):this.dialogParams.supervisor.localize("dialog.datadisk_move.title"),this.closeDialog,this.moving,this.moving?(0,k.dy)(r||(r=(0,u.Z)([' <ha-circular-progress alt="Moving" size="large" active> </ha-circular-progress> <p class="progress-text"> '," </p>"])),this.dialogParams.supervisor.localize("dialog.datadisk_move.moving_desc")):(0,k.dy)(a||(a=(0,u.Z)([" ",' <mwc-button slot="secondaryAction" @click="','" dialogInitialFocus> ',' </mwc-button> <mwc-button .disabled="','" slot="primaryAction" @click="','"> '," </mwc-button>"])),null!==(e=this.devices)&&void 0!==e&&e.length?(0,k.dy)(o||(o=(0,u.Z)([" ",' <br><br> <ha-select .label="','" @selected="','" dialogInitialFocus> '," </ha-select> "])),this.dialogParams.supervisor.localize("dialog.datadisk_move.description",{current_path:this.dialogParams.supervisor.os.data_disk,time:x(this.dialogParams.supervisor)}),this.dialogParams.supervisor.localize("dialog.datadisk_move.select_device"),this._select_device,this.devices.map((function(e){return(0,k.dy)(s||(s=(0,u.Z)(['<mwc-list-item .value="','">',"</mwc-list-item>"])),e,e)}))):void 0===this.devices?this.dialogParams.supervisor.localize("dialog.datadisk_move.loading_devices"):this.dialogParams.supervisor.localize("dialog.datadisk_move.no_devices"),this.closeDialog,this.dialogParams.supervisor.localize("dialog.datadisk_move.cancel"),!this.selectedDevice,this._moveDatadisk,this.dialogParams.supervisor.localize("dialog.datadisk_move.move"))):k.Ld}},{kind:"method",key:"_select_device",value:function(e){this.selectedDevice=e.target.value}},{kind:"method",key:"_moveDatadisk",value:(n=(0,d.Z)((0,c.Z)().mark((function e(){return(0,c.Z)().wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return this.moving=!0,e.prev=1,e.next=4,(0,E.Sx)(this.hass,this.selectedDevice);case 4:e.next=9;break;case 6:e.prev=6,e.t0=e.catch(1),this.hass.connection.connected&&!(0,Z.yz)(e.t0)&&((0,_.Ys)(this,{title:this.dialogParams.supervisor.localize("system.host.failed_to_move"),text:(0,Z.js)(e.t0)}),this.closeDialog());case 9:case"end":return e.stop()}}),e,this,[[1,6]])}))),function(){return n.apply(this,arguments)})},{kind:"get",static:!0,key:"styles",value:function(){return[z.Qx,z.yu,(0,k.iv)(l||(l=(0,u.Z)(["ha-select{width:100%}ha-circular-progress{display:block;margin:32px;text-align:center}.progress-text{text-align:center}"])))]}}]}}),k.oi)},65189:function(e,t,n){var i,r,a,o=n(88962),s=n(33368),l=n(71650),c=n(82390),d=n(69205),u=n(70906),v=n(91808),h=n(68144),f=n(79932),m=n(99312),g=n(40039),p=n(81043),k=n(34541),y=n(47838),b=n(47181),w=n(93217),Z=function(){var e=(0,p.Z)((0,m.Z)().mark((function e(t,r,a){return(0,m.Z)().wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return i||(i=(0,w.Ud)(new Worker(new URL(n.p+n.u(1402),n.b)))),e.abrupt("return",i.renderMarkdown(t,r,a));case 2:case"end":return e.stop()}}),e)})));return function(t,n,i){return e.apply(this,arguments)}}(),E={Note:"info",Warning:"warning"};(0,v.Z)([(0,f.Mo)("ha-markdown-element")],(function(e,t){var n,i=function(t){(0,d.Z)(i,t);var n=(0,u.Z)(i);function i(){var t;(0,l.Z)(this,i);for(var r=arguments.length,a=new Array(r),o=0;o<r;o++)a[o]=arguments[o];return t=n.call.apply(n,[this].concat(a)),e((0,c.Z)(t)),t}return(0,s.Z)(i)}(t);return{F:i,d:[{kind:"field",decorators:[(0,f.Cb)()],key:"content",value:void 0},{kind:"field",decorators:[(0,f.Cb)({type:Boolean})],key:"allowSvg",value:function(){return!1}},{kind:"field",decorators:[(0,f.Cb)({type:Boolean})],key:"breaks",value:function(){return!1}},{kind:"field",decorators:[(0,f.Cb)({type:Boolean,attribute:"lazy-images"})],key:"lazyImages",value:function(){return!1}},{kind:"method",key:"createRenderRoot",value:function(){return this}},{kind:"method",key:"update",value:function(e){(0,k.Z)((0,y.Z)(i.prototype),"update",this).call(this,e),void 0!==this.content&&this._render()}},{kind:"method",key:"_render",value:(n=(0,p.Z)((0,m.Z)().mark((function e(){var t,n,i,r,a,o,s,l,c,d,u;return(0,m.Z)().wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return e.next=2,Z(String(this.content),{breaks:this.breaks,gfm:!0},{allowSvg:this.allowSvg});case 2:for(this.innerHTML=e.sent,this._resize(),t=document.createTreeWalker(this,NodeFilter.SHOW_ELEMENT,null);t.nextNode();)if((n=t.currentNode)instanceof HTMLAnchorElement&&n.host!==document.location.host)n.target="_blank",n.rel="noreferrer noopener";else if(n instanceof HTMLImageElement)this.lazyImages&&(n.loading="lazy"),n.addEventListener("load",this._resize);else if(n instanceof HTMLQuoteElement&&(i=n.firstElementChild,r=null==i?void 0:i.firstElementChild,a=(null==r?void 0:r.textContent)&&E[r.textContent],"STRONG"===(null==r?void 0:r.nodeName)&&a)){(s=document.createElement("ha-alert")).alertType=a,s.title="#text"===i.childNodes[1].nodeName&&(null===(o=i.childNodes[1].textContent)||void 0===o?void 0:o.trimStart())||"",l=Array.from(i.childNodes),c=(0,g.Z)(l.slice(l.findIndex((function(e){return e instanceof HTMLBRElement}))+1));try{for(c.s();!(d=c.n()).done;)u=d.value,s.appendChild(u)}catch(v){c.e(v)}finally{c.f()}n.firstElementChild.replaceWith(s)}case 6:case"end":return e.stop()}}),e,this)}))),function(){return n.apply(this,arguments)})},{kind:"field",key:"_resize",value:function(){var e=this;return function(){return(0,b.B)(e,"iron-resize")}}}]}}),h.fl),n(9381),n(52039),(0,v.Z)([(0,f.Mo)("ha-markdown")],(function(e,t){var n=function(t){(0,d.Z)(i,t);var n=(0,u.Z)(i);function i(){var t;(0,l.Z)(this,i);for(var r=arguments.length,a=new Array(r),o=0;o<r;o++)a[o]=arguments[o];return t=n.call.apply(n,[this].concat(a)),e((0,c.Z)(t)),t}return(0,s.Z)(i)}(t);return{F:n,d:[{kind:"field",decorators:[(0,f.Cb)()],key:"content",value:void 0},{kind:"field",decorators:[(0,f.Cb)({type:Boolean})],key:"allowSvg",value:function(){return!1}},{kind:"field",decorators:[(0,f.Cb)({type:Boolean})],key:"breaks",value:function(){return!1}},{kind:"field",decorators:[(0,f.Cb)({type:Boolean,attribute:"lazy-images"})],key:"lazyImages",value:function(){return!1}},{kind:"method",key:"render",value:function(){return this.content?(0,h.dy)(r||(r=(0,o.Z)(['<ha-markdown-element .content="','" .allowSvg="','" .breaks="','" .lazyImages="','"></ha-markdown-element>'])),this.content,this.allowSvg,this.breaks,this.lazyImages):h.Ld}},{kind:"get",static:!0,key:"styles",value:function(){return(0,h.iv)(a||(a=(0,o.Z)([":host{display:block}ha-markdown-element{-ms-user-select:text;-webkit-user-select:text;-moz-user-select:text}ha-markdown-element>:first-child{margin-top:0}ha-markdown-element>:last-child{margin-bottom:0}a{color:var(--primary-color)}img{max-width:100%}code,pre{background-color:var(--markdown-code-background-color,none);border-radius:3px}svg{background-color:var(--markdown-svg-background-color,none);color:var(--markdown-svg-color,none)}code{font-size:85%;padding:.2em .4em}pre code{padding:0}pre{padding:16px;overflow:auto;line-height:1.45;font-family:var(--code-font-family,monospace)}h1,h2,h3,h4,h5,h6{line-height:initial}h2{font-size:1.5em;font-weight:700}"])))}}]}}),h.oi)},93217:function(e,t,n){n.d(t,{Ud:function(){return k}});var i=n(62746),r=n(93359),a=n(59202),o=n(46097),s=n(40039),l=n(76775),c=Symbol("Comlink.proxy"),d=Symbol("Comlink.endpoint"),u=Symbol("Comlink.releaseProxy"),v=Symbol("Comlink.finalizer"),h=Symbol("Comlink.thrown"),f=function(e){return"object"===(0,l.Z)(e)&&null!==e||"function"==typeof e},m=new Map([["proxy",{canHandle:function(e){return f(e)&&e[c]},serialize:function(e){var t=new MessageChannel,n=t.port1,i=t.port2;return g(e,n),[i,[i]]},deserialize:function(e){return e.start(),k(e)}}],["throw",{canHandle:function(e){return f(e)&&h in e},serialize:function(e){var t=e.value;return[t instanceof Error?{isError:!0,value:{message:t.message,name:t.name,stack:t.stack}}:{isError:!1,value:t},[]]},deserialize:function(e){if(e.isError)throw Object.assign(new Error(e.value.message),e.value);throw e.value}}]]);function g(e){var t=arguments.length>1&&void 0!==arguments[1]?arguments[1]:globalThis,n=arguments.length>2&&void 0!==arguments[2]?arguments[2]:["*"];t.addEventListener("message",(function l(d){if(d&&d.data)if(function(e,t){var n,i=(0,s.Z)(e);try{for(i.s();!(n=i.n()).done;){var r=n.value;if(t===r||"*"===r)return!0;if(r instanceof RegExp&&r.test(t))return!0}}catch(a){i.e(a)}finally{i.f()}return!1}(n,d.origin)){var u,f=Object.assign({path:[]},d.data),m=f.id,k=f.type,y=f.path,b=(d.data.argumentList||[]).map(S);try{var w=y.slice(0,-1).reduce((function(e,t){return e[t]}),e),Z=y.reduce((function(e,t){return e[t]}),e);switch(k){case"GET":u=Z;break;case"SET":w[y.slice(-1)[0]]=S(d.data.value),u=!0;break;case"APPLY":u=Z.apply(w,b);break;case"CONSTRUCT":var E;u=function(e){return Object.assign(e,(0,r.Z)({},c,!0))}((0,a.Z)(Z,(0,o.Z)(b)));break;case"ENDPOINT":var _=new MessageChannel,C=_.port1,P=_.port2;g(e,P),u=function(e,t){return z.set(e,t),e}(C,[C]);break;case"RELEASE":u=void 0;break;default:return}}catch(E){u=(0,r.Z)({value:E},h,0)}Promise.resolve(u).catch((function(e){return(0,r.Z)({value:e},h,0)})).then((function(n){var r=x(n),a=(0,i.Z)(r,2),o=a[0],s=a[1];t.postMessage(Object.assign(Object.assign({},o),{id:m}),s),"RELEASE"===k&&(t.removeEventListener("message",l),p(t),v in e&&"function"==typeof e[v]&&e[v]())})).catch((function(e){var n=x((0,r.Z)({value:new TypeError("Unserializable return value")},h,0)),a=(0,i.Z)(n,2),o=a[0],s=a[1];t.postMessage(Object.assign(Object.assign({},o),{id:m}),s)}))}else console.warn("Invalid origin '".concat(d.origin,"' for comlink proxy"))})),t.start&&t.start()}function p(e){(function(e){return"MessagePort"===e.constructor.name})(e)&&e.close()}function k(e,t){return E(e,[],t)}function y(e){if(e)throw new Error("Proxy has been released and is not useable")}function b(e){return C(e,{type:"RELEASE"}).then((function(){p(e)}))}var w=new WeakMap,Z="FinalizationRegistry"in globalThis&&new FinalizationRegistry((function(e){var t=(w.get(e)||0)-1;w.set(e,t),0===t&&b(e)}));function E(e){var t=arguments.length>1&&void 0!==arguments[1]?arguments[1]:[],n=!1,r=new Proxy(arguments.length>2&&void 0!==arguments[2]?arguments[2]:function(){},{get:function(i,a){if(y(n),a===u)return function(){!function(e){Z&&Z.unregister(e)}(r),b(e),n=!0};if("then"===a){if(0===t.length)return{then:function(){return r}};var s=C(e,{type:"GET",path:t.map((function(e){return e.toString()}))}).then(S);return s.then.bind(s)}return E(e,[].concat((0,o.Z)(t),[a]))},set:function(r,a,s){y(n);var l=x(s),c=(0,i.Z)(l,2),d=c[0],u=c[1];return C(e,{type:"SET",path:[].concat((0,o.Z)(t),[a]).map((function(e){return e.toString()})),value:d},u).then(S)},apply:function(r,a,o){y(n);var s=t[t.length-1];if(s===d)return C(e,{type:"ENDPOINT"}).then(S);if("bind"===s)return E(e,t.slice(0,-1));var l=_(o),c=(0,i.Z)(l,2),u=c[0],v=c[1];return C(e,{type:"APPLY",path:t.map((function(e){return e.toString()})),argumentList:u},v).then(S)},construct:function(r,a){y(n);var o=_(a),s=(0,i.Z)(o,2),l=s[0],c=s[1];return C(e,{type:"CONSTRUCT",path:t.map((function(e){return e.toString()})),argumentList:l},c).then(S)}});return function(e,t){var n=(w.get(t)||0)+1;w.set(t,n),Z&&Z.register(e,t,e)}(r,e),r}function _(e){var t,n=e.map(x);return[n.map((function(e){return e[0]})),(t=n.map((function(e){return e[1]})),Array.prototype.concat.apply([],t))]}var z=new WeakMap;function x(e){var t,n=(0,s.Z)(m);try{for(n.s();!(t=n.n()).done;){var r=(0,i.Z)(t.value,2),a=r[0],o=r[1];if(o.canHandle(e)){var l=o.serialize(e),c=(0,i.Z)(l,2);return[{type:"HANDLER",name:a,value:c[0]},c[1]]}}}catch(d){n.e(d)}finally{n.f()}return[{type:"RAW",value:e},z.get(e)||[]]}function S(e){switch(e.type){case"HANDLER":return m.get(e.name).deserialize(e.value);case"RAW":return e.value}}function C(e,t,n){return new Promise((function(i){var r=new Array(4).fill(0).map((function(){return Math.floor(Math.random()*Number.MAX_SAFE_INTEGER).toString(16)})).join("-");e.addEventListener("message",(function t(n){n.data&&n.data.id&&n.data.id===r&&(e.removeEventListener("message",t),i(n.data))})),e.start&&e.start(),e.postMessage(Object.assign({id:r},t),n)}))}}}]);
//# sourceMappingURL=2708-eHG7wXa4CSg.js.map