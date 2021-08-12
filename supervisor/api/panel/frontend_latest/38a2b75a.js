(self.webpackChunkhome_assistant_frontend=self.webpackChunkhome_assistant_frontend||[]).push([[665],{4665:(e,t,r)=>{"use strict";var i=r(424),n=r(5358),a=r(3864),o=/d{1,4}|M{1,4}|YY(?:YY)?|S{1,3}|Do|ZZ|Z|([HhMsDm])\1?|[aA]|"[^"]*"|'[^']*'/g,s="[1-9]\\d?",l="\\d\\d",c="[^\\s]+",d=/\[([^]*?)\]/gm;function u(e,t){for(var r=[],i=0,n=e.length;i<n;i++)r.push(e[i].substr(0,t));return r}var h=function(e){return function(t,r){var i=r[e].map((function(e){return e.toLowerCase()})).indexOf(t.toLowerCase());return i>-1?i:null}};function p(e){for(var t=[],r=1;r<arguments.length;r++)t[r-1]=arguments[r];for(var i=0,n=t;i<n.length;i++){var a=n[i];for(var o in a)e[o]=a[o]}return e}var f=["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"],m=["January","February","March","April","May","June","July","August","September","October","November","December"],y=u(m,3),v={dayNamesShort:u(f,3),dayNames:f,monthNamesShort:y,monthNames:m,amPm:["am","pm"],DoFn:function(e){return e+["th","st","nd","rd"][e%10>3?0:(e-e%10!=10?1:0)*e%10]}},g=p({},v),k=function(e,t){for(void 0===t&&(t=2),e=String(e);e.length<t;)e="0"+e;return e},b={D:function(e){return String(e.getDate())},DD:function(e){return k(e.getDate())},Do:function(e,t){return t.DoFn(e.getDate())},d:function(e){return String(e.getDay())},dd:function(e){return k(e.getDay())},ddd:function(e,t){return t.dayNamesShort[e.getDay()]},dddd:function(e,t){return t.dayNames[e.getDay()]},M:function(e){return String(e.getMonth()+1)},MM:function(e){return k(e.getMonth()+1)},MMM:function(e,t){return t.monthNamesShort[e.getMonth()]},MMMM:function(e,t){return t.monthNames[e.getMonth()]},YY:function(e){return k(String(e.getFullYear()),4).substr(2)},YYYY:function(e){return k(e.getFullYear(),4)},h:function(e){return String(e.getHours()%12||12)},hh:function(e){return k(e.getHours()%12||12)},H:function(e){return String(e.getHours())},HH:function(e){return k(e.getHours())},m:function(e){return String(e.getMinutes())},mm:function(e){return k(e.getMinutes())},s:function(e){return String(e.getSeconds())},ss:function(e){return k(e.getSeconds())},S:function(e){return String(Math.round(e.getMilliseconds()/100))},SS:function(e){return k(Math.round(e.getMilliseconds()/10),2)},SSS:function(e){return k(e.getMilliseconds(),3)},a:function(e,t){return e.getHours()<12?t.amPm[0]:t.amPm[1]},A:function(e,t){return e.getHours()<12?t.amPm[0].toUpperCase():t.amPm[1].toUpperCase()},ZZ:function(e){var t=e.getTimezoneOffset();return(t>0?"-":"+")+k(100*Math.floor(Math.abs(t)/60)+Math.abs(t)%60,4)},Z:function(e){var t=e.getTimezoneOffset();return(t>0?"-":"+")+k(Math.floor(Math.abs(t)/60),2)+":"+k(Math.abs(t)%60,2)}},w=function(e){return+e-1},E=[null,s],D=[null,c],C=["isPm",c,function(e,t){var r=e.toLowerCase();return r===t.amPm[0]?0:r===t.amPm[1]?1:null}],P=["timezoneOffset","[^\\s]*?[\\+\\-]\\d\\d:?\\d\\d|[^\\s]*?Z?",function(e){var t=(e+"").match(/([+-]|\d\d)/gi);if(t){var r=60*+t[1]+parseInt(t[2],10);return"+"===t[0]?r:-r}return 0}],S=(h("monthNamesShort"),h("monthNames"),{default:"ddd MMM DD YYYY HH:mm:ss",shortDate:"M/D/YY",mediumDate:"MMM D, YYYY",longDate:"MMMM D, YYYY",fullDate:"dddd, MMMM D, YYYY",isoDate:"YYYY-MM-DD",isoDateTime:"YYYY-MM-DDTHH:mm:ssZ",shortTime:"HH:mm",mediumTime:"HH:mm:ss",longTime:"HH:mm:ss.SSS"}),A=function(e,t,r){if(void 0===t&&(t=S.default),void 0===r&&(r={}),"number"==typeof e&&(e=new Date(e)),"[object Date]"!==Object.prototype.toString.call(e)||isNaN(e.getTime()))throw new Error("Invalid Date pass to format");var i=[];t=(t=S[t]||t).replace(d,(function(e,t){return i.push(t),"@@@"}));var n=p(p({},g),r);return(t=t.replace(o,(function(t){return b[t](e,n)}))).replace(/@@@/g,(function(){return i.shift()}))};var T=r(4516);const $=function(){try{(new Date).toLocaleDateString("i")}catch(e){return"RangeError"===e.name}return!1}(),M=(function(){try{(new Date).toLocaleTimeString("i")}catch(e){return"RangeError"===e.name}}(),function(){try{(new Date).toLocaleString("i")}catch(e){return"RangeError"===e.name}return!1}()),x=((0,T.Z)((e=>new Intl.DateTimeFormat(e.language,{weekday:"long",month:"long",day:"numeric"}))),$?(e,t)=>_(t).format(e):e=>A(e,"MMMM D, YYYY")),_=(0,T.Z)((e=>new Intl.DateTimeFormat(e.language,{year:"numeric",month:"long",day:"numeric"})));(0,T.Z)((e=>new Intl.DateTimeFormat(e.language,{year:"numeric",month:"numeric",day:"numeric"}))),(0,T.Z)((e=>new Intl.DateTimeFormat(e.language,{day:"numeric",month:"short"}))),(0,T.Z)((e=>new Intl.DateTimeFormat(e.language,{month:"long",year:"numeric"}))),(0,T.Z)((e=>new Intl.DateTimeFormat(e.language,{month:"long"}))),(0,T.Z)((e=>new Intl.DateTimeFormat(e.language,{year:"numeric"})));let H,z;!function(e){e.language="language",e.system="system",e.comma_decimal="comma_decimal",e.decimal_comma="decimal_comma",e.space_comma="space_comma",e.none="none"}(H||(H={})),function(e){e.language="language",e.system="system",e.am_pm="12",e.twenty_four="24"}(z||(z={}));const Y=(0,T.Z)((e=>{if(e.time_format===z.language||e.time_format===z.system){const t=e.time_format===z.language?e.language:void 0,r=(new Date).toLocaleString(t);return r.includes("AM")||r.includes("PM")}return e.time_format===z.am_pm})),O=M?(e,t)=>F(t).format(e):(e,t)=>A(e,(Y(t)," A")),F=(0,T.Z)((e=>new Intl.DateTimeFormat(e.language,{year:"numeric",month:"long",day:"numeric",hour:"numeric",minute:"2-digit",hour12:Y(e)})));(0,T.Z)((e=>new Intl.DateTimeFormat(e.language,{year:"numeric",month:"long",day:"numeric",hour:"numeric",minute:"2-digit",second:"2-digit",hour12:Y(e)}))),(0,T.Z)((e=>new Intl.DateTimeFormat(e.language,{year:"numeric",month:"numeric",day:"numeric",hour:"numeric",minute:"2-digit",hour12:Y(e)})));r(2497),r(8358),r(4678),r(2039);function j(){j=function(){return e};var e={elementsDefinitionOrder:[["method"],["field"]],initializeInstanceElements:function(e,t){["method","field"].forEach((function(r){t.forEach((function(t){t.kind===r&&"own"===t.placement&&this.defineClassElement(e,t)}),this)}),this)},initializeClassElements:function(e,t){var r=e.prototype;["method","field"].forEach((function(i){t.forEach((function(t){var n=t.placement;if(t.kind===i&&("static"===n||"prototype"===n)){var a="static"===n?e:r;this.defineClassElement(a,t)}}),this)}),this)},defineClassElement:function(e,t){var r=t.descriptor;if("field"===t.kind){var i=t.initializer;r={enumerable:r.enumerable,writable:r.writable,configurable:r.configurable,value:void 0===i?void 0:i.call(e)}}Object.defineProperty(e,t.key,r)},decorateClass:function(e,t){var r=[],i=[],n={static:[],prototype:[],own:[]};if(e.forEach((function(e){this.addElementPlacement(e,n)}),this),e.forEach((function(e){if(!Z(e))return r.push(e);var t=this.decorateElement(e,n);r.push(t.element),r.push.apply(r,t.extras),i.push.apply(i,t.finishers)}),this),!t)return{elements:r,finishers:i};var a=this.decorateConstructor(r,t);return i.push.apply(i,a.finishers),a.finishers=i,a},addElementPlacement:function(e,t,r){var i=t[e.placement];if(!r&&-1!==i.indexOf(e.key))throw new TypeError("Duplicated element ("+e.key+")");i.push(e.key)},decorateElement:function(e,t){for(var r=[],i=[],n=e.decorators,a=n.length-1;a>=0;a--){var o=t[e.placement];o.splice(o.indexOf(e.key),1);var s=this.fromElementDescriptor(e),l=this.toElementFinisherExtras((0,n[a])(s)||s);e=l.element,this.addElementPlacement(e,t),l.finisher&&i.push(l.finisher);var c=l.extras;if(c){for(var d=0;d<c.length;d++)this.addElementPlacement(c[d],t);r.push.apply(r,c)}}return{element:e,finishers:i,extras:r}},decorateConstructor:function(e,t){for(var r=[],i=t.length-1;i>=0;i--){var n=this.fromClassDescriptor(e),a=this.toClassDescriptor((0,t[i])(n)||n);if(void 0!==a.finisher&&r.push(a.finisher),void 0!==a.elements){e=a.elements;for(var o=0;o<e.length-1;o++)for(var s=o+1;s<e.length;s++)if(e[o].key===e[s].key&&e[o].placement===e[s].placement)throw new TypeError("Duplicated element ("+e[o].key+")")}}return{elements:e,finishers:r}},fromElementDescriptor:function(e){var t={kind:e.kind,key:e.key,placement:e.placement,descriptor:e.descriptor};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),"field"===e.kind&&(t.initializer=e.initializer),t},toElementDescriptors:function(e){var t;if(void 0!==e)return(t=e,function(e){if(Array.isArray(e))return e}(t)||function(e){if("undefined"!=typeof Symbol&&null!=e[Symbol.iterator]||null!=e["@@iterator"])return Array.from(e)}(t)||function(e,t){if(e){if("string"==typeof e)return U(e,t);var r=Object.prototype.toString.call(e).slice(8,-1);return"Object"===r&&e.constructor&&(r=e.constructor.name),"Map"===r||"Set"===r?Array.from(e):"Arguments"===r||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(r)?U(e,t):void 0}}(t)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()).map((function(e){var t=this.toElementDescriptor(e);return this.disallowProperty(e,"finisher","An element descriptor"),this.disallowProperty(e,"extras","An element descriptor"),t}),this)},toElementDescriptor:function(e){var t=String(e.kind);if("method"!==t&&"field"!==t)throw new TypeError('An element descriptor\'s .kind property must be either "method" or "field", but a decorator created an element descriptor with .kind "'+t+'"');var r=R(e.key),i=String(e.placement);if("static"!==i&&"prototype"!==i&&"own"!==i)throw new TypeError('An element descriptor\'s .placement property must be one of "static", "prototype" or "own", but a decorator created an element descriptor with .placement "'+i+'"');var n=e.descriptor;this.disallowProperty(e,"elements","An element descriptor");var a={kind:t,key:r,placement:i,descriptor:Object.assign({},n)};return"field"!==t?this.disallowProperty(e,"initializer","A method descriptor"):(this.disallowProperty(n,"get","The property descriptor of a field descriptor"),this.disallowProperty(n,"set","The property descriptor of a field descriptor"),this.disallowProperty(n,"value","The property descriptor of a field descriptor"),a.initializer=e.initializer),a},toElementFinisherExtras:function(e){return{element:this.toElementDescriptor(e),finisher:N(e,"finisher"),extras:this.toElementDescriptors(e.extras)}},fromClassDescriptor:function(e){var t={kind:"class",elements:e.map(this.fromElementDescriptor,this)};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),t},toClassDescriptor:function(e){var t=String(e.kind);if("class"!==t)throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator created a class descriptor with .kind "'+t+'"');this.disallowProperty(e,"key","A class descriptor"),this.disallowProperty(e,"placement","A class descriptor"),this.disallowProperty(e,"descriptor","A class descriptor"),this.disallowProperty(e,"initializer","A class descriptor"),this.disallowProperty(e,"extras","A class descriptor");var r=N(e,"finisher");return{elements:this.toElementDescriptors(e.elements),finisher:r}},runClassFinishers:function(e,t){for(var r=0;r<t.length;r++){var i=(0,t[r])(e);if(void 0!==i){if("function"!=typeof i)throw new TypeError("Finishers must return a constructor.");e=i}}return e},disallowProperty:function(e,t,r){if(void 0!==e[t])throw new TypeError(r+" can't have a ."+t+" property.")}};return e}function V(e){var t,r=R(e.key);"method"===e.kind?t={value:e.value,writable:!0,configurable:!0,enumerable:!1}:"get"===e.kind?t={get:e.value,configurable:!0,enumerable:!1}:"set"===e.kind?t={set:e.value,configurable:!0,enumerable:!1}:"field"===e.kind&&(t={configurable:!0,writable:!0,enumerable:!0});var i={kind:"field"===e.kind?"field":"method",key:r,placement:e.static?"static":"field"===e.kind?"own":"prototype",descriptor:t};return e.decorators&&(i.decorators=e.decorators),"field"===e.kind&&(i.initializer=e.value),i}function I(e,t){void 0!==e.descriptor.get?t.descriptor.get=e.descriptor.get:t.descriptor.set=e.descriptor.set}function Z(e){return e.decorators&&e.decorators.length}function L(e){return void 0!==e&&!(void 0===e.value&&void 0===e.writable)}function N(e,t){var r=e[t];if(void 0!==r&&"function"!=typeof r)throw new TypeError("Expected '"+t+"' to be a function");return r}function R(e){var t=function(e,t){if("object"!=typeof e||null===e)return e;var r=e[Symbol.toPrimitive];if(void 0!==r){var i=r.call(e,t||"default");if("object"!=typeof i)return i;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===t?String:Number)(e)}(e,"string");return"symbol"==typeof t?t:String(t)}function U(e,t){(null==t||t>e.length)&&(t=e.length);for(var r=0,i=new Array(t);r<t;r++)i[r]=e[r];return i}!function(e,t,r,i){var n=j();if(i)for(var a=0;a<i.length;a++)n=i[a](n);var o=t((function(e){n.initializeInstanceElements(e,s.elements)}),r),s=n.decorateClass(function(e){for(var t=[],r=function(e){return"method"===e.kind&&e.key===a.key&&e.placement===a.placement},i=0;i<e.length;i++){var n,a=e[i];if("method"===a.kind&&(n=t.find(r)))if(L(a.descriptor)||L(n.descriptor)){if(Z(a)||Z(n))throw new ReferenceError("Duplicated methods ("+a.key+") can't be decorated.");n.descriptor=a.descriptor}else{if(Z(a)){if(Z(n))throw new ReferenceError("Decorators can't be placed on different accessors with for the same property ("+a.key+").");n.decorators=a.decorators}I(a,n)}else t.push(a)}return t}(o.d.map(V)),e);n.initializeClassElements(o.F,s.elements),n.runClassFinishers(o.F,s.finishers)}([(0,n.Mo)("supervisor-formfield-label")],(function(e,t){return{F:class extends t{constructor(...t){super(...t),e(this)}},d:[{kind:"field",decorators:[(0,n.Cb)({type:String})],key:"label",value:void 0},{kind:"field",decorators:[(0,n.Cb)({type:String})],key:"imageUrl",value:void 0},{kind:"field",decorators:[(0,n.Cb)({type:String})],key:"iconPath",value:void 0},{kind:"field",decorators:[(0,n.Cb)({type:String})],key:"version",value:void 0},{kind:"method",key:"render",value:function(){return i.dy`
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
    `}}]}}),i.oi);function B(){B=function(){return e};var e={elementsDefinitionOrder:[["method"],["field"]],initializeInstanceElements:function(e,t){["method","field"].forEach((function(r){t.forEach((function(t){t.kind===r&&"own"===t.placement&&this.defineClassElement(e,t)}),this)}),this)},initializeClassElements:function(e,t){var r=e.prototype;["method","field"].forEach((function(i){t.forEach((function(t){var n=t.placement;if(t.kind===i&&("static"===n||"prototype"===n)){var a="static"===n?e:r;this.defineClassElement(a,t)}}),this)}),this)},defineClassElement:function(e,t){var r=t.descriptor;if("field"===t.kind){var i=t.initializer;r={enumerable:r.enumerable,writable:r.writable,configurable:r.configurable,value:void 0===i?void 0:i.call(e)}}Object.defineProperty(e,t.key,r)},decorateClass:function(e,t){var r=[],i=[],n={static:[],prototype:[],own:[]};if(e.forEach((function(e){this.addElementPlacement(e,n)}),this),e.forEach((function(e){if(!q(e))return r.push(e);var t=this.decorateElement(e,n);r.push(t.element),r.push.apply(r,t.extras),i.push.apply(i,t.finishers)}),this),!t)return{elements:r,finishers:i};var a=this.decorateConstructor(r,t);return i.push.apply(i,a.finishers),a.finishers=i,a},addElementPlacement:function(e,t,r){var i=t[e.placement];if(!r&&-1!==i.indexOf(e.key))throw new TypeError("Duplicated element ("+e.key+")");i.push(e.key)},decorateElement:function(e,t){for(var r=[],i=[],n=e.decorators,a=n.length-1;a>=0;a--){var o=t[e.placement];o.splice(o.indexOf(e.key),1);var s=this.fromElementDescriptor(e),l=this.toElementFinisherExtras((0,n[a])(s)||s);e=l.element,this.addElementPlacement(e,t),l.finisher&&i.push(l.finisher);var c=l.extras;if(c){for(var d=0;d<c.length;d++)this.addElementPlacement(c[d],t);r.push.apply(r,c)}}return{element:e,finishers:i,extras:r}},decorateConstructor:function(e,t){for(var r=[],i=t.length-1;i>=0;i--){var n=this.fromClassDescriptor(e),a=this.toClassDescriptor((0,t[i])(n)||n);if(void 0!==a.finisher&&r.push(a.finisher),void 0!==a.elements){e=a.elements;for(var o=0;o<e.length-1;o++)for(var s=o+1;s<e.length;s++)if(e[o].key===e[s].key&&e[o].placement===e[s].placement)throw new TypeError("Duplicated element ("+e[o].key+")")}}return{elements:e,finishers:r}},fromElementDescriptor:function(e){var t={kind:e.kind,key:e.key,placement:e.placement,descriptor:e.descriptor};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),"field"===e.kind&&(t.initializer=e.initializer),t},toElementDescriptors:function(e){var t;if(void 0!==e)return(t=e,function(e){if(Array.isArray(e))return e}(t)||function(e){if("undefined"!=typeof Symbol&&null!=e[Symbol.iterator]||null!=e["@@iterator"])return Array.from(e)}(t)||function(e,t){if(e){if("string"==typeof e)return X(e,t);var r=Object.prototype.toString.call(e).slice(8,-1);return"Object"===r&&e.constructor&&(r=e.constructor.name),"Map"===r||"Set"===r?Array.from(e):"Arguments"===r||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(r)?X(e,t):void 0}}(t)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()).map((function(e){var t=this.toElementDescriptor(e);return this.disallowProperty(e,"finisher","An element descriptor"),this.disallowProperty(e,"extras","An element descriptor"),t}),this)},toElementDescriptor:function(e){var t=String(e.kind);if("method"!==t&&"field"!==t)throw new TypeError('An element descriptor\'s .kind property must be either "method" or "field", but a decorator created an element descriptor with .kind "'+t+'"');var r=Q(e.key),i=String(e.placement);if("static"!==i&&"prototype"!==i&&"own"!==i)throw new TypeError('An element descriptor\'s .placement property must be one of "static", "prototype" or "own", but a decorator created an element descriptor with .placement "'+i+'"');var n=e.descriptor;this.disallowProperty(e,"elements","An element descriptor");var a={kind:t,key:r,placement:i,descriptor:Object.assign({},n)};return"field"!==t?this.disallowProperty(e,"initializer","A method descriptor"):(this.disallowProperty(n,"get","The property descriptor of a field descriptor"),this.disallowProperty(n,"set","The property descriptor of a field descriptor"),this.disallowProperty(n,"value","The property descriptor of a field descriptor"),a.initializer=e.initializer),a},toElementFinisherExtras:function(e){return{element:this.toElementDescriptor(e),finisher:K(e,"finisher"),extras:this.toElementDescriptors(e.extras)}},fromClassDescriptor:function(e){var t={kind:"class",elements:e.map(this.fromElementDescriptor,this)};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),t},toClassDescriptor:function(e){var t=String(e.kind);if("class"!==t)throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator created a class descriptor with .kind "'+t+'"');this.disallowProperty(e,"key","A class descriptor"),this.disallowProperty(e,"placement","A class descriptor"),this.disallowProperty(e,"descriptor","A class descriptor"),this.disallowProperty(e,"initializer","A class descriptor"),this.disallowProperty(e,"extras","A class descriptor");var r=K(e,"finisher");return{elements:this.toElementDescriptors(e.elements),finisher:r}},runClassFinishers:function(e,t){for(var r=0;r<t.length;r++){var i=(0,t[r])(e);if(void 0!==i){if("function"!=typeof i)throw new TypeError("Finishers must return a constructor.");e=i}}return e},disallowProperty:function(e,t,r){if(void 0!==e[t])throw new TypeError(r+" can't have a ."+t+" property.")}};return e}function J(e){var t,r=Q(e.key);"method"===e.kind?t={value:e.value,writable:!0,configurable:!0,enumerable:!1}:"get"===e.kind?t={get:e.value,configurable:!0,enumerable:!1}:"set"===e.kind?t={set:e.value,configurable:!0,enumerable:!1}:"field"===e.kind&&(t={configurable:!0,writable:!0,enumerable:!0});var i={kind:"field"===e.kind?"field":"method",key:r,placement:e.static?"static":"field"===e.kind?"own":"prototype",descriptor:t};return e.decorators&&(i.decorators=e.decorators),"field"===e.kind&&(i.initializer=e.value),i}function W(e,t){void 0!==e.descriptor.get?t.descriptor.get=e.descriptor.get:t.descriptor.set=e.descriptor.set}function q(e){return e.decorators&&e.decorators.length}function G(e){return void 0!==e&&!(void 0===e.value&&void 0===e.writable)}function K(e,t){var r=e[t];if(void 0!==r&&"function"!=typeof r)throw new TypeError("Expected '"+t+"' to be a function");return r}function Q(e){var t=function(e,t){if("object"!=typeof e||null===e)return e;var r=e[Symbol.toPrimitive];if(void 0!==r){var i=r.call(e,t||"default");if("object"!=typeof i)return i;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===t?String:Number)(e)}(e,"string");return"symbol"==typeof t?t:String(t)}function X(e,t){(null==t||t>e.length)&&(t=e.length);for(var r=0,i=new Array(t);r<t;r++)i[r]=e[r];return i}function ee(e,t,r){return(ee="undefined"!=typeof Reflect&&Reflect.get?Reflect.get:function(e,t,r){var i=function(e,t){for(;!Object.prototype.hasOwnProperty.call(e,t)&&null!==(e=te(e)););return e}(e,t);if(i){var n=Object.getOwnPropertyDescriptor(i,t);return n.get?n.get.call(r):n.value}})(e,t,r||e)}function te(e){return(te=Object.setPrototypeOf?Object.getPrototypeOf:function(e){return e.__proto__||Object.getPrototypeOf(e)})(e)}const re="M10,4H4C2.89,4 2,4.89 2,6V18A2,2 0 0,0 4,20H20A2,2 0 0,0 22,18V8C22,6.89 21.1,6 20,6H12L10,4Z",ie="M20.5,11H19V7C19,5.89 18.1,5 17,5H13V3.5A2.5,2.5 0 0,0 10.5,1A2.5,2.5 0 0,0 8,3.5V5H4A2,2 0 0,0 2,7V10.8H3.5C5,10.8 6.2,12 6.2,13.5C6.2,15 5,16.2 3.5,16.2H2V20A2,2 0 0,0 4,22H7.8V20.5C7.8,19 9,17.8 10.5,17.8C12,17.8 13.2,19 13.2,20.5V22H17A2,2 0 0,0 19,20V16H20.5A2.5,2.5 0 0,0 23,13.5A2.5,2.5 0 0,0 20.5,11Z";!function(e,t,r,i){var n=B();if(i)for(var a=0;a<i.length;a++)n=i[a](n);var o=t((function(e){n.initializeInstanceElements(e,s.elements)}),r),s=n.decorateClass(function(e){for(var t=[],r=function(e){return"method"===e.kind&&e.key===a.key&&e.placement===a.placement},i=0;i<e.length;i++){var n,a=e[i];if("method"===a.kind&&(n=t.find(r)))if(G(a.descriptor)||G(n.descriptor)){if(q(a)||q(n))throw new ReferenceError("Duplicated methods ("+a.key+") can't be decorated.");n.descriptor=a.descriptor}else{if(q(a)){if(q(n))throw new ReferenceError("Decorators can't be placed on different accessors with for the same property ("+a.key+").");n.decorators=a.decorators}W(a,n)}else t.push(a)}return t}(o.d.map(J)),e);n.initializeClassElements(o.F,s.elements),n.runClassFinishers(o.F,s.finishers)}([(0,n.Mo)("supervisor-backup-content")],(function(e,t){class r extends t{constructor(...t){super(...t),e(this)}}return{F:r,d:[{kind:"field",decorators:[(0,n.Cb)({attribute:!1})],key:"hass",value:void 0},{kind:"field",decorators:[(0,n.Cb)()],key:"localize",value:void 0},{kind:"field",decorators:[(0,n.Cb)({attribute:!1})],key:"supervisor",value:void 0},{kind:"field",decorators:[(0,n.Cb)({attribute:!1})],key:"backup",value:void 0},{kind:"field",decorators:[(0,n.Cb)()],key:"backupType",value:()=>"full"},{kind:"field",decorators:[(0,n.Cb)({attribute:!1})],key:"folders",value:void 0},{kind:"field",decorators:[(0,n.Cb)({attribute:!1})],key:"addons",value:void 0},{kind:"field",decorators:[(0,n.Cb)({type:Boolean})],key:"homeAssistant",value:()=>!1},{kind:"field",decorators:[(0,n.Cb)({type:Boolean})],key:"backupHasPassword",value:()=>!1},{kind:"field",decorators:[(0,n.Cb)({type:Boolean})],key:"onboarding",value:()=>!1},{kind:"field",decorators:[(0,n.Cb)()],key:"backupName",value:()=>""},{kind:"field",decorators:[(0,n.Cb)()],key:"backupPassword",value:()=>""},{kind:"field",decorators:[(0,n.Cb)()],key:"confirmBackupPassword",value:()=>""},{kind:"method",key:"willUpdate",value:function(e){var t,i,n,a;(ee(te(r.prototype),"willUpdate",this).call(this,e),this.hasUpdated)||(this.folders=(e=>{const t=[];return e.includes("homeassistant")&&t.push({slug:"homeassistant",name:"Home Assistant configuration",checked:!1}),e.includes("ssl")&&t.push({slug:"ssl",name:"SSL",checked:!1}),e.includes("share")&&t.push({slug:"share",name:"Share",checked:!1}),e.includes("media")&&t.push({slug:"media",name:"Media",checked:!1}),e.includes("addons/local")&&t.push({slug:"addons/local",name:"Local add-ons",checked:!1}),t.sort(((e,t)=>e.name>t.name?1:-1))})(this.backup?this.backup.folders:["homeassistant","ssl","share","media","addons/local"]),this.addons=(this.backup?this.backup.addons:null===(t=this.supervisor)||void 0===t?void 0:t.supervisor.addons).map((e=>({slug:e.slug,name:e.name,version:e.version,checked:!1}))).sort(((e,t)=>e.name>t.name?1:-1)),this.backupType=(null===(i=this.backup)||void 0===i?void 0:i.type)||"full",this.backupName=(null===(n=this.backup)||void 0===n?void 0:n.name)||"",this.backupHasPassword=(null===(a=this.backup)||void 0===a?void 0:a.protected)||!1)}},{kind:"field",key:"_localize",value(){return e=>{var t;return(null===(t=this.supervisor)||void 0===t?void 0:t.localize(`backup.${e}`))||this.localize(`ui.panel.page-onboarding.restore.${e}`)}}},{kind:"method",key:"render",value:function(){if(!this.onboarding&&!this.supervisor)return i.dy``;const e="partial"===this.backupType?this._getSection("folders"):void 0,t="partial"===this.backupType?this._getSection("addons"):void 0;return i.dy`
      ${this.backup?i.dy`<div class="details">
            ${"full"===this.backup.type?this._localize("full_backup"):this._localize("partial_backup")}
            (${Math.ceil(10*this.backup.size)/10+" MB"})<br />
            ${this.hass?O(new Date(this.backup.date),this.hass.locale):this.backup.date}
          </div>`:i.dy`<paper-input
            name="backupName"
            .label=${this._localize("name")}
            .value=${this.backupName}
            @value-changed=${this._handleTextValueChanged}
          >
          </paper-input>`}
      ${this.backup&&"full"!==this.backup.type?"":i.dy`<div class="sub-header">
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
      ${"partial"===this.backupType?i.dy`<div class="partial-picker">
            ${this.backup&&this.backup.homeassistant?i.dy`
                  <ha-formfield
                    .label=${i.dy`<supervisor-formfield-label
                      label="Home Assistant"
                      .iconPath=${"M21.8,13H20V21H13V17.67L15.79,14.88L16.5,15C17.66,15 18.6,14.06 18.6,12.9C18.6,11.74 17.66,10.8 16.5,10.8A2.1,2.1 0 0,0 14.4,12.9L14.5,13.61L13,15.13V9.65C13.66,9.29 14.1,8.6 14.1,7.8A2.1,2.1 0 0,0 12,5.7A2.1,2.1 0 0,0 9.9,7.8C9.9,8.6 10.34,9.29 11,9.65V15.13L9.5,13.61L9.6,12.9A2.1,2.1 0 0,0 7.5,10.8A2.1,2.1 0 0,0 5.4,12.9A2.1,2.1 0 0,0 7.5,15L8.21,14.88L11,17.67V21H4V13H2.25C1.83,13 1.42,13 1.42,12.79C1.43,12.57 1.85,12.15 2.28,11.72L11,3C11.33,2.67 11.67,2.33 12,2.33C12.33,2.33 12.67,2.67 13,3L17,7V6H19V9L21.78,11.78C22.18,12.18 22.59,12.59 22.6,12.8C22.6,13 22.2,13 21.8,13M7.5,12A0.9,0.9 0 0,1 8.4,12.9A0.9,0.9 0 0,1 7.5,13.8A0.9,0.9 0 0,1 6.6,12.9A0.9,0.9 0 0,1 7.5,12M16.5,12C17,12 17.4,12.4 17.4,12.9C17.4,13.4 17,13.8 16.5,13.8A0.9,0.9 0 0,1 15.6,12.9A0.9,0.9 0 0,1 16.5,12M12,6.9C12.5,6.9 12.9,7.3 12.9,7.8C12.9,8.3 12.5,8.7 12,8.7C11.5,8.7 11.1,8.3 11.1,7.8C11.1,7.3 11.5,6.9 12,6.9Z"}
                      .version=${this.backup.homeassistant}
                    >
                    </supervisor-formfield-label>`}
                  >
                    <ha-checkbox
                      .checked=${this.homeAssistant}
                      @click=${()=>{this.homeAssistant=!this.homeAssistant}}
                    >
                    </ha-checkbox>
                  </ha-formfield>
                `:""}
            ${null!=e&&e.templates.length?i.dy`
                  <ha-formfield
                    .label=${i.dy`<supervisor-formfield-label
                      .label=${this._localize("folders")}
                      .iconPath=${re}
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
            ${null!=t&&t.templates.length?i.dy`
                  <ha-formfield
                    .label=${i.dy`<supervisor-formfield-label
                      .label=${this._localize("addons")}
                      .iconPath=${ie}
                    >
                    </supervisor-formfield-label>`}
                  >
                    <ha-checkbox
                      @change=${this._toggleSection}
                      .checked=${t.checked}
                      .indeterminate=${t.indeterminate}
                      .section=${"addons"}
                    >
                    </ha-checkbox>
                  </ha-formfield>
                  <div class="section-content">${t.templates}</div>
                `:""}
          </div> `:""}
      ${"partial"!==this.backupType||this.backup&&!this.backupHasPassword?"":i.dy`<hr />`}
      ${this.backup?"":i.dy`<ha-formfield
            class="password"
            .label=${this._localize("password_protection")}
          >
            <ha-checkbox
              .checked=${this.backupHasPassword}
              @change=${this._toggleHasPassword}
            >
            </ha-checkbox>
          </ha-formfield>`}
      ${this.backupHasPassword?i.dy`
            <paper-input
              .label=${this._localize("password")}
              type="password"
              name="backupPassword"
              .value=${this.backupPassword}
              @value-changed=${this._handleTextValueChanged}
            >
            </paper-input>
            ${this.backup?"":i.dy` <paper-input
                  .label=${this._localize("confirm_password")}
                  type="password"
                  name="confirmBackupPassword"
                  .value=${this.confirmBackupPassword}
                  @value-changed=${this._handleTextValueChanged}
                >
                </paper-input>`}
          `:""}
    `}},{kind:"get",static:!0,key:"styles",value:function(){return i.iv`
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
    `}},{kind:"method",key:"backupDetails",value:function(){var e,t;const r={};if(this.backup||(r.name=this.backupName||x(new Date,this.hass.locale)),this.backupHasPassword&&(r.password=this.backupPassword,this.backup||(r.confirm_password=this.confirmBackupPassword)),"full"===this.backupType)return r;const i=null===(e=this.addons)||void 0===e?void 0:e.filter((e=>e.checked)).map((e=>e.slug)),n=null===(t=this.folders)||void 0===t?void 0:t.filter((e=>e.checked)).map((e=>e.slug));return null!=i&&i.length&&(r.addons=i),null!=n&&n.length&&(r.folders=n),this.homeAssistant&&(r.homeassistant=this.homeAssistant),r}},{kind:"method",key:"_getSection",value:function(e){var t;const r=[],n="addons"===e?new Map(null===(t=this.supervisor)||void 0===t?void 0:t.addon.addons.map((e=>[e.slug,e]))):void 0;let o=0;this[e].forEach((t=>{var s;r.push(i.dy`<ha-formfield
        .label=${i.dy`<supervisor-formfield-label
          .label=${t.name}
          .iconPath=${"addons"===e?ie:re}
          .imageUrl=${"addons"===e&&!this.onboarding&&(0,a.I)(this.hass.config.version,0,105)&&null!=n&&null!==(s=n.get(t.slug))&&void 0!==s&&s.icon?`/api/hassio/addons/${t.slug}/icon`:void 0}
          .version=${t.version}
        >
        </supervisor-formfield-label>`}
      >
        <ha-checkbox
          .item=${t}
          .checked=${t.checked}
          .section=${e}
          @change=${this._updateSectionEntry}
        >
        </ha-checkbox>
      </ha-formfield>`),t.checked&&o++}));const s=o===this[e].length;return{templates:r,checked:s,indeterminate:!s&&0!==o}}},{kind:"method",key:"_handleRadioValueChanged",value:function(e){const t=e.currentTarget;this[t.name]=t.value}},{kind:"method",key:"_handleTextValueChanged",value:function(e){this[e.currentTarget.name]=e.detail.value}},{kind:"method",key:"_toggleHasPassword",value:function(){this.backupHasPassword=!this.backupHasPassword}},{kind:"method",key:"_toggleSection",value:function(e){const t=e.currentTarget.section;this[t]=("addons"===t?this.addons:this.folders).map((t=>({...t,checked:e.currentTarget.checked})))}},{kind:"method",key:"_updateSectionEntry",value:function(e){const t=e.currentTarget.item,r=e.currentTarget.section;this[r]=this[r].map((r=>r.slug===t.slug?{...r,checked:e.currentTarget.checked}:r))}}]}}),i.oi)}}]);
//# sourceMappingURL=38a2b75a.js.map