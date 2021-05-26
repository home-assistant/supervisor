(self.webpackChunkhome_assistant_frontend=self.webpackChunkhome_assistant_frontend||[]).push([[452],{452:(e,t,r)=>{"use strict";var n=r(5317),i=r(424),o=r(5358),s=r(3864),a=/d{1,4}|M{1,4}|YY(?:YY)?|S{1,3}|Do|ZZ|Z|([HhMsDm])\1?|[aA]|"[^"]*"|'[^']*'/g,l="[1-9]\\d?",c="\\d\\d",d="[^\\s]+",u=/\[([^]*?)\]/gm;function h(e,t){for(var r=[],n=0,i=e.length;n<i;n++)r.push(e[n].substr(0,t));return r}var p=function(e){return function(t,r){var n=r[e].map((function(e){return e.toLowerCase()})).indexOf(t.toLowerCase());return n>-1?n:null}};function f(e){for(var t=[],r=1;r<arguments.length;r++)t[r-1]=arguments[r];for(var n=0,i=t;n<i.length;n++){var o=i[n];for(var s in o)e[s]=o[s]}return e}var m=["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"],y=["January","February","March","April","May","June","July","August","September","October","November","December"],v=h(y,3),g={dayNamesShort:h(m,3),dayNames:m,monthNamesShort:v,monthNames:y,amPm:["am","pm"],DoFn:function(e){return e+["th","st","nd","rd"][e%10>3?0:(e-e%10!=10?1:0)*e%10]}},k=f({},g),b=function(e,t){for(void 0===t&&(t=2),e=String(e);e.length<t;)e="0"+e;return e},w={D:function(e){return String(e.getDate())},DD:function(e){return b(e.getDate())},Do:function(e,t){return t.DoFn(e.getDate())},d:function(e){return String(e.getDay())},dd:function(e){return b(e.getDay())},ddd:function(e,t){return t.dayNamesShort[e.getDay()]},dddd:function(e,t){return t.dayNames[e.getDay()]},M:function(e){return String(e.getMonth()+1)},MM:function(e){return b(e.getMonth()+1)},MMM:function(e,t){return t.monthNamesShort[e.getMonth()]},MMMM:function(e,t){return t.monthNames[e.getMonth()]},YY:function(e){return b(String(e.getFullYear()),4).substr(2)},YYYY:function(e){return b(e.getFullYear(),4)},h:function(e){return String(e.getHours()%12||12)},hh:function(e){return b(e.getHours()%12||12)},H:function(e){return String(e.getHours())},HH:function(e){return b(e.getHours())},m:function(e){return String(e.getMinutes())},mm:function(e){return b(e.getMinutes())},s:function(e){return String(e.getSeconds())},ss:function(e){return b(e.getSeconds())},S:function(e){return String(Math.round(e.getMilliseconds()/100))},SS:function(e){return b(Math.round(e.getMilliseconds()/10),2)},SSS:function(e){return b(e.getMilliseconds(),3)},a:function(e,t){return e.getHours()<12?t.amPm[0]:t.amPm[1]},A:function(e,t){return e.getHours()<12?t.amPm[0].toUpperCase():t.amPm[1].toUpperCase()},ZZ:function(e){var t=e.getTimezoneOffset();return(t>0?"-":"+")+b(100*Math.floor(Math.abs(t)/60)+Math.abs(t)%60,4)},Z:function(e){var t=e.getTimezoneOffset();return(t>0?"-":"+")+b(Math.floor(Math.abs(t)/60),2)+":"+b(Math.abs(t)%60,2)}},E=function(e){return+e-1},D=[null,l],S=[null,d],P=["isPm",d,function(e,t){var r=e.toLowerCase();return r===t.amPm[0]?0:r===t.amPm[1]?1:null}],$=["timezoneOffset","[^\\s]*?[\\+\\-]\\d\\d:?\\d\\d|[^\\s]*?Z?",function(e){var t=(e+"").match(/([+-]|\d\d)/gi);if(t){var r=60*+t[1]+parseInt(t[2],10);return"+"===t[0]?r:-r}return 0}],T=(p("monthNamesShort"),p("monthNames"),{default:"ddd MMM DD YYYY HH:mm:ss",shortDate:"M/D/YY",mediumDate:"MMM D, YYYY",longDate:"MMMM D, YYYY",fullDate:"dddd, MMMM D, YYYY",isoDate:"YYYY-MM-DD",isoDateTime:"YYYY-MM-DDTHH:mm:ssZ",shortTime:"HH:mm",mediumTime:"HH:mm:ss",longTime:"HH:mm:ss.SSS"}),x=function(e,t,r){if(void 0===t&&(t=T.default),void 0===r&&(r={}),"number"==typeof e&&(e=new Date(e)),"[object Date]"!==Object.prototype.toString.call(e)||isNaN(e.getTime()))throw new Error("Invalid Date pass to format");var n=[];t=(t=T[t]||t).replace(u,(function(e,t){return n.push(t),"@@@"}));var i=f(f({},k),r);return(t=t.replace(a,(function(t){return w[t](e,i)}))).replace(/@@@/g,(function(){return n.shift()}))};var M=r(4516);const C=function(){try{(new Date).toLocaleDateString("i")}catch(e){return"RangeError"===e.name}return!1}(),A=(function(){try{(new Date).toLocaleTimeString("i")}catch(e){return"RangeError"===e.name}}(),function(){try{(new Date).toLocaleString("i")}catch(e){return"RangeError"===e.name}return!1}()),_=(0,M.Z)((e=>new Intl.DateTimeFormat(e.language,{year:"numeric",month:"long",day:"numeric"}))),z=C?(e,t)=>_(t).format(e):e=>x(e,"longDate");(0,M.Z)((e=>new Intl.DateTimeFormat(e.language,{weekday:"long",month:"long",day:"numeric"})));let Y,O;!function(e){e.language="language",e.system="system",e.comma_decimal="comma_decimal",e.decimal_comma="decimal_comma",e.space_comma="space_comma",e.none="none"}(Y||(Y={})),function(e){e.language="language",e.system="system",e.am_pm="12",e.twenty_four="24"}(O||(O={}));const H=e=>{if(e.time_format===O.language||e.time_format===O.system){const t=e.time_format===O.language?e.language:void 0,r=(new Date).toLocaleString(t);return r.includes("AM")||r.includes("PM")}return e.time_format===O.am_pm},F=(0,M.Z)((e=>new Intl.DateTimeFormat(e.language,{year:"numeric",month:"long",day:"numeric",hour:"numeric",minute:"2-digit",hour12:H(e)}))),j=A?(e,t)=>F(t).format(e):(e,t)=>x(e,(H(t)," A"));(0,M.Z)((e=>new Intl.DateTimeFormat(e.language,{year:"numeric",month:"long",day:"numeric",hour:"numeric",minute:"2-digit",second:"2-digit",hour12:H(e)})));r(7507),r(1857),r(2064),r(2039);function N(){N=function(){return e};var e={elementsDefinitionOrder:[["method"],["field"]],initializeInstanceElements:function(e,t){["method","field"].forEach((function(r){t.forEach((function(t){t.kind===r&&"own"===t.placement&&this.defineClassElement(e,t)}),this)}),this)},initializeClassElements:function(e,t){var r=e.prototype;["method","field"].forEach((function(n){t.forEach((function(t){var i=t.placement;if(t.kind===n&&("static"===i||"prototype"===i)){var o="static"===i?e:r;this.defineClassElement(o,t)}}),this)}),this)},defineClassElement:function(e,t){var r=t.descriptor;if("field"===t.kind){var n=t.initializer;r={enumerable:r.enumerable,writable:r.writable,configurable:r.configurable,value:void 0===n?void 0:n.call(e)}}Object.defineProperty(e,t.key,r)},decorateClass:function(e,t){var r=[],n=[],i={static:[],prototype:[],own:[]};if(e.forEach((function(e){this.addElementPlacement(e,i)}),this),e.forEach((function(e){if(!R(e))return r.push(e);var t=this.decorateElement(e,i);r.push(t.element),r.push.apply(r,t.extras),n.push.apply(n,t.finishers)}),this),!t)return{elements:r,finishers:n};var o=this.decorateConstructor(r,t);return n.push.apply(n,o.finishers),o.finishers=n,o},addElementPlacement:function(e,t,r){var n=t[e.placement];if(!r&&-1!==n.indexOf(e.key))throw new TypeError("Duplicated element ("+e.key+")");n.push(e.key)},decorateElement:function(e,t){for(var r=[],n=[],i=e.decorators,o=i.length-1;o>=0;o--){var s=t[e.placement];s.splice(s.indexOf(e.key),1);var a=this.fromElementDescriptor(e),l=this.toElementFinisherExtras((0,i[o])(a)||a);e=l.element,this.addElementPlacement(e,t),l.finisher&&n.push(l.finisher);var c=l.extras;if(c){for(var d=0;d<c.length;d++)this.addElementPlacement(c[d],t);r.push.apply(r,c)}}return{element:e,finishers:n,extras:r}},decorateConstructor:function(e,t){for(var r=[],n=t.length-1;n>=0;n--){var i=this.fromClassDescriptor(e),o=this.toClassDescriptor((0,t[n])(i)||i);if(void 0!==o.finisher&&r.push(o.finisher),void 0!==o.elements){e=o.elements;for(var s=0;s<e.length-1;s++)for(var a=s+1;a<e.length;a++)if(e[s].key===e[a].key&&e[s].placement===e[a].placement)throw new TypeError("Duplicated element ("+e[s].key+")")}}return{elements:e,finishers:r}},fromElementDescriptor:function(e){var t={kind:e.kind,key:e.key,placement:e.placement,descriptor:e.descriptor};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),"field"===e.kind&&(t.initializer=e.initializer),t},toElementDescriptors:function(e){var t;if(void 0!==e)return(t=e,function(e){if(Array.isArray(e))return e}(t)||function(e){if("undefined"!=typeof Symbol&&null!=e[Symbol.iterator]||null!=e["@@iterator"])return Array.from(e)}(t)||function(e,t){if(e){if("string"==typeof e)return B(e,t);var r=Object.prototype.toString.call(e).slice(8,-1);return"Object"===r&&e.constructor&&(r=e.constructor.name),"Map"===r||"Set"===r?Array.from(e):"Arguments"===r||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(r)?B(e,t):void 0}}(t)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()).map((function(e){var t=this.toElementDescriptor(e);return this.disallowProperty(e,"finisher","An element descriptor"),this.disallowProperty(e,"extras","An element descriptor"),t}),this)},toElementDescriptor:function(e){var t=String(e.kind);if("method"!==t&&"field"!==t)throw new TypeError('An element descriptor\'s .kind property must be either "method" or "field", but a decorator created an element descriptor with .kind "'+t+'"');var r=V(e.key),n=String(e.placement);if("static"!==n&&"prototype"!==n&&"own"!==n)throw new TypeError('An element descriptor\'s .placement property must be one of "static", "prototype" or "own", but a decorator created an element descriptor with .placement "'+n+'"');var i=e.descriptor;this.disallowProperty(e,"elements","An element descriptor");var o={kind:t,key:r,placement:n,descriptor:Object.assign({},i)};return"field"!==t?this.disallowProperty(e,"initializer","A method descriptor"):(this.disallowProperty(i,"get","The property descriptor of a field descriptor"),this.disallowProperty(i,"set","The property descriptor of a field descriptor"),this.disallowProperty(i,"value","The property descriptor of a field descriptor"),o.initializer=e.initializer),o},toElementFinisherExtras:function(e){return{element:this.toElementDescriptor(e),finisher:L(e,"finisher"),extras:this.toElementDescriptors(e.extras)}},fromClassDescriptor:function(e){var t={kind:"class",elements:e.map(this.fromElementDescriptor,this)};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),t},toClassDescriptor:function(e){var t=String(e.kind);if("class"!==t)throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator created a class descriptor with .kind "'+t+'"');this.disallowProperty(e,"key","A class descriptor"),this.disallowProperty(e,"placement","A class descriptor"),this.disallowProperty(e,"descriptor","A class descriptor"),this.disallowProperty(e,"initializer","A class descriptor"),this.disallowProperty(e,"extras","A class descriptor");var r=L(e,"finisher");return{elements:this.toElementDescriptors(e.elements),finisher:r}},runClassFinishers:function(e,t){for(var r=0;r<t.length;r++){var n=(0,t[r])(e);if(void 0!==n){if("function"!=typeof n)throw new TypeError("Finishers must return a constructor.");e=n}}return e},disallowProperty:function(e,t,r){if(void 0!==e[t])throw new TypeError(r+" can't have a ."+t+" property.")}};return e}function I(e){var t,r=V(e.key);"method"===e.kind?t={value:e.value,writable:!0,configurable:!0,enumerable:!1}:"get"===e.kind?t={get:e.value,configurable:!0,enumerable:!1}:"set"===e.kind?t={set:e.value,configurable:!0,enumerable:!1}:"field"===e.kind&&(t={configurable:!0,writable:!0,enumerable:!0});var n={kind:"field"===e.kind?"field":"method",key:r,placement:e.static?"static":"field"===e.kind?"own":"prototype",descriptor:t};return e.decorators&&(n.decorators=e.decorators),"field"===e.kind&&(n.initializer=e.value),n}function Z(e,t){void 0!==e.descriptor.get?t.descriptor.get=e.descriptor.get:t.descriptor.set=e.descriptor.set}function R(e){return e.decorators&&e.decorators.length}function U(e){return void 0!==e&&!(void 0===e.value&&void 0===e.writable)}function L(e,t){var r=e[t];if(void 0!==r&&"function"!=typeof r)throw new TypeError("Expected '"+t+"' to be a function");return r}function V(e){var t=function(e,t){if("object"!=typeof e||null===e)return e;var r=e[Symbol.toPrimitive];if(void 0!==r){var n=r.call(e,t||"default");if("object"!=typeof n)return n;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===t?String:Number)(e)}(e,"string");return"symbol"==typeof t?t:String(t)}function B(e,t){(null==t||t>e.length)&&(t=e.length);for(var r=0,n=new Array(t);r<t;r++)n[r]=e[r];return n}!function(e,t,r,n){var i=N();if(n)for(var o=0;o<n.length;o++)i=n[o](i);var s=t((function(e){i.initializeInstanceElements(e,a.elements)}),r),a=i.decorateClass(function(e){for(var t=[],r=function(e){return"method"===e.kind&&e.key===o.key&&e.placement===o.placement},n=0;n<e.length;n++){var i,o=e[n];if("method"===o.kind&&(i=t.find(r)))if(U(o.descriptor)||U(i.descriptor)){if(R(o)||R(i))throw new ReferenceError("Duplicated methods ("+o.key+") can't be decorated.");i.descriptor=o.descriptor}else{if(R(o)){if(R(i))throw new ReferenceError("Decorators can't be placed on different accessors with for the same property ("+o.key+").");i.decorators=o.decorators}Z(o,i)}else t.push(o)}return t}(s.d.map(I)),e);i.initializeClassElements(s.F,a.elements),i.runClassFinishers(s.F,a.finishers)}([(0,o.Mo)("supervisor-formfield-label")],(function(e,t){return{F:class extends t{constructor(...t){super(...t),e(this)}},d:[{kind:"field",decorators:[(0,o.Cb)({type:String})],key:"label",value:void 0},{kind:"field",decorators:[(0,o.Cb)({type:String})],key:"imageUrl",value:void 0},{kind:"field",decorators:[(0,o.Cb)({type:String})],key:"iconPath",value:void 0},{kind:"field",decorators:[(0,o.Cb)({type:String})],key:"version",value:void 0},{kind:"method",key:"render",value:function(){return i.dy`
      ${this.imageUrl?i.dy`<img loading="lazy" .src=${this.imageUrl} class="icon" />`:this.iconPath?i.dy`<ha-svg-icon .path=${this.iconPath} class="icon"></ha-svg-icon>`:""}
      <span class="label">${this.label}</span>
      ${this.version?i.dy`<span class="version">(${this.version})</span>`:""}
    `}},{kind:"get",static:!0,key:"styles",value:function(){return i.iv`
      :host {
        cursor: pointer;
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
    `}}]}}),i.oi);function J(){J=function(){return e};var e={elementsDefinitionOrder:[["method"],["field"]],initializeInstanceElements:function(e,t){["method","field"].forEach((function(r){t.forEach((function(t){t.kind===r&&"own"===t.placement&&this.defineClassElement(e,t)}),this)}),this)},initializeClassElements:function(e,t){var r=e.prototype;["method","field"].forEach((function(n){t.forEach((function(t){var i=t.placement;if(t.kind===n&&("static"===i||"prototype"===i)){var o="static"===i?e:r;this.defineClassElement(o,t)}}),this)}),this)},defineClassElement:function(e,t){var r=t.descriptor;if("field"===t.kind){var n=t.initializer;r={enumerable:r.enumerable,writable:r.writable,configurable:r.configurable,value:void 0===n?void 0:n.call(e)}}Object.defineProperty(e,t.key,r)},decorateClass:function(e,t){var r=[],n=[],i={static:[],prototype:[],own:[]};if(e.forEach((function(e){this.addElementPlacement(e,i)}),this),e.forEach((function(e){if(!G(e))return r.push(e);var t=this.decorateElement(e,i);r.push(t.element),r.push.apply(r,t.extras),n.push.apply(n,t.finishers)}),this),!t)return{elements:r,finishers:n};var o=this.decorateConstructor(r,t);return n.push.apply(n,o.finishers),o.finishers=n,o},addElementPlacement:function(e,t,r){var n=t[e.placement];if(!r&&-1!==n.indexOf(e.key))throw new TypeError("Duplicated element ("+e.key+")");n.push(e.key)},decorateElement:function(e,t){for(var r=[],n=[],i=e.decorators,o=i.length-1;o>=0;o--){var s=t[e.placement];s.splice(s.indexOf(e.key),1);var a=this.fromElementDescriptor(e),l=this.toElementFinisherExtras((0,i[o])(a)||a);e=l.element,this.addElementPlacement(e,t),l.finisher&&n.push(l.finisher);var c=l.extras;if(c){for(var d=0;d<c.length;d++)this.addElementPlacement(c[d],t);r.push.apply(r,c)}}return{element:e,finishers:n,extras:r}},decorateConstructor:function(e,t){for(var r=[],n=t.length-1;n>=0;n--){var i=this.fromClassDescriptor(e),o=this.toClassDescriptor((0,t[n])(i)||i);if(void 0!==o.finisher&&r.push(o.finisher),void 0!==o.elements){e=o.elements;for(var s=0;s<e.length-1;s++)for(var a=s+1;a<e.length;a++)if(e[s].key===e[a].key&&e[s].placement===e[a].placement)throw new TypeError("Duplicated element ("+e[s].key+")")}}return{elements:e,finishers:r}},fromElementDescriptor:function(e){var t={kind:e.kind,key:e.key,placement:e.placement,descriptor:e.descriptor};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),"field"===e.kind&&(t.initializer=e.initializer),t},toElementDescriptors:function(e){var t;if(void 0!==e)return(t=e,function(e){if(Array.isArray(e))return e}(t)||function(e){if("undefined"!=typeof Symbol&&null!=e[Symbol.iterator]||null!=e["@@iterator"])return Array.from(e)}(t)||function(e,t){if(e){if("string"==typeof e)return ee(e,t);var r=Object.prototype.toString.call(e).slice(8,-1);return"Object"===r&&e.constructor&&(r=e.constructor.name),"Map"===r||"Set"===r?Array.from(e):"Arguments"===r||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(r)?ee(e,t):void 0}}(t)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()).map((function(e){var t=this.toElementDescriptor(e);return this.disallowProperty(e,"finisher","An element descriptor"),this.disallowProperty(e,"extras","An element descriptor"),t}),this)},toElementDescriptor:function(e){var t=String(e.kind);if("method"!==t&&"field"!==t)throw new TypeError('An element descriptor\'s .kind property must be either "method" or "field", but a decorator created an element descriptor with .kind "'+t+'"');var r=X(e.key),n=String(e.placement);if("static"!==n&&"prototype"!==n&&"own"!==n)throw new TypeError('An element descriptor\'s .placement property must be one of "static", "prototype" or "own", but a decorator created an element descriptor with .placement "'+n+'"');var i=e.descriptor;this.disallowProperty(e,"elements","An element descriptor");var o={kind:t,key:r,placement:n,descriptor:Object.assign({},i)};return"field"!==t?this.disallowProperty(e,"initializer","A method descriptor"):(this.disallowProperty(i,"get","The property descriptor of a field descriptor"),this.disallowProperty(i,"set","The property descriptor of a field descriptor"),this.disallowProperty(i,"value","The property descriptor of a field descriptor"),o.initializer=e.initializer),o},toElementFinisherExtras:function(e){return{element:this.toElementDescriptor(e),finisher:Q(e,"finisher"),extras:this.toElementDescriptors(e.extras)}},fromClassDescriptor:function(e){var t={kind:"class",elements:e.map(this.fromElementDescriptor,this)};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),t},toClassDescriptor:function(e){var t=String(e.kind);if("class"!==t)throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator created a class descriptor with .kind "'+t+'"');this.disallowProperty(e,"key","A class descriptor"),this.disallowProperty(e,"placement","A class descriptor"),this.disallowProperty(e,"descriptor","A class descriptor"),this.disallowProperty(e,"initializer","A class descriptor"),this.disallowProperty(e,"extras","A class descriptor");var r=Q(e,"finisher");return{elements:this.toElementDescriptors(e.elements),finisher:r}},runClassFinishers:function(e,t){for(var r=0;r<t.length;r++){var n=(0,t[r])(e);if(void 0!==n){if("function"!=typeof n)throw new TypeError("Finishers must return a constructor.");e=n}}return e},disallowProperty:function(e,t,r){if(void 0!==e[t])throw new TypeError(r+" can't have a ."+t+" property.")}};return e}function W(e){var t,r=X(e.key);"method"===e.kind?t={value:e.value,writable:!0,configurable:!0,enumerable:!1}:"get"===e.kind?t={get:e.value,configurable:!0,enumerable:!1}:"set"===e.kind?t={set:e.value,configurable:!0,enumerable:!1}:"field"===e.kind&&(t={configurable:!0,writable:!0,enumerable:!0});var n={kind:"field"===e.kind?"field":"method",key:r,placement:e.static?"static":"field"===e.kind?"own":"prototype",descriptor:t};return e.decorators&&(n.decorators=e.decorators),"field"===e.kind&&(n.initializer=e.value),n}function q(e,t){void 0!==e.descriptor.get?t.descriptor.get=e.descriptor.get:t.descriptor.set=e.descriptor.set}function G(e){return e.decorators&&e.decorators.length}function K(e){return void 0!==e&&!(void 0===e.value&&void 0===e.writable)}function Q(e,t){var r=e[t];if(void 0!==r&&"function"!=typeof r)throw new TypeError("Expected '"+t+"' to be a function");return r}function X(e){var t=function(e,t){if("object"!=typeof e||null===e)return e;var r=e[Symbol.toPrimitive];if(void 0!==r){var n=r.call(e,t||"default");if("object"!=typeof n)return n;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===t?String:Number)(e)}(e,"string");return"symbol"==typeof t?t:String(t)}function ee(e,t){(null==t||t>e.length)&&(t=e.length);for(var r=0,n=new Array(t);r<t;r++)n[r]=e[r];return n}function te(e,t,r){return(te="undefined"!=typeof Reflect&&Reflect.get?Reflect.get:function(e,t,r){var n=function(e,t){for(;!Object.prototype.hasOwnProperty.call(e,t)&&null!==(e=re(e)););return e}(e,t);if(n){var i=Object.getOwnPropertyDescriptor(n,t);return i.get?i.get.call(r):i.value}})(e,t,r||e)}function re(e){return(re=Object.setPrototypeOf?Object.getPrototypeOf:function(e){return e.__proto__||Object.getPrototypeOf(e)})(e)}!function(e,t,r,n){var i=J();if(n)for(var o=0;o<n.length;o++)i=n[o](i);var s=t((function(e){i.initializeInstanceElements(e,a.elements)}),r),a=i.decorateClass(function(e){for(var t=[],r=function(e){return"method"===e.kind&&e.key===o.key&&e.placement===o.placement},n=0;n<e.length;n++){var i,o=e[n];if("method"===o.kind&&(i=t.find(r)))if(K(o.descriptor)||K(i.descriptor)){if(G(o)||G(i))throw new ReferenceError("Duplicated methods ("+o.key+") can't be decorated.");i.descriptor=o.descriptor}else{if(G(o)){if(G(i))throw new ReferenceError("Decorators can't be placed on different accessors with for the same property ("+o.key+").");i.decorators=o.decorators}q(o,i)}else t.push(o)}return t}(s.d.map(W)),e);i.initializeClassElements(s.F,a.elements),i.runClassFinishers(s.F,a.finishers)}([(0,o.Mo)("supervisor-snapshot-content")],(function(e,t){class r extends t{constructor(...t){super(...t),e(this)}}return{F:r,d:[{kind:"field",decorators:[(0,o.Cb)({attribute:!1})],key:"hass",value:void 0},{kind:"field",decorators:[(0,o.Cb)({attribute:!1})],key:"supervisor",value:void 0},{kind:"field",decorators:[(0,o.Cb)({attribute:!1})],key:"snapshot",value:void 0},{kind:"field",decorators:[(0,o.Cb)()],key:"snapshotType",value:()=>"full"},{kind:"field",decorators:[(0,o.Cb)({attribute:!1})],key:"folders",value:void 0},{kind:"field",decorators:[(0,o.Cb)({attribute:!1})],key:"addons",value:void 0},{kind:"field",decorators:[(0,o.Cb)({type:Boolean})],key:"homeAssistant",value:()=>!1},{kind:"field",decorators:[(0,o.Cb)({type:Boolean})],key:"snapshotHasPassword",value:()=>!1},{kind:"field",decorators:[(0,o.Cb)()],key:"snapshotName",value:()=>""},{kind:"field",decorators:[(0,o.Cb)()],key:"snapshotPassword",value:()=>""},{kind:"method",key:"willUpdate",value:function(e){var t,n,i,o;(te(re(r.prototype),"willUpdate",this).call(this,e),this.hasUpdated)||(this.folders=(e=>{const t=[];return e.includes("homeassistant")&&t.push({slug:"homeassistant",name:"Home Assistant configuration",checked:!1}),e.includes("ssl")&&t.push({slug:"ssl",name:"SSL",checked:!1}),e.includes("share")&&t.push({slug:"share",name:"Share",checked:!1}),e.includes("addons/local")&&t.push({slug:"addons/local",name:"Local add-ons",checked:!1}),t.sort(((e,t)=>e.name>t.name?1:-1))})(this.snapshot?this.snapshot.folders:["homeassistant","ssl","share","media","addons/local"]),this.addons=(this.snapshot?this.snapshot.addons:null===(t=this.supervisor)||void 0===t?void 0:t.supervisor.addons).map((e=>({slug:e.slug,name:e.name,version:e.version,checked:!1}))).sort(((e,t)=>e.name>t.name?1:-1)),this.snapshotType=(null===(n=this.snapshot)||void 0===n?void 0:n.type)||"full",this.snapshotName=(null===(i=this.snapshot)||void 0===i?void 0:i.name)||"",this.snapshotHasPassword=(null===(o=this.snapshot)||void 0===o?void 0:o.protected)||!1)}},{kind:"method",key:"render",value:function(){if(!this.supervisor)return i.dy``;const e="partial"===this.snapshotType?this._getSection("folders"):void 0,t="partial"===this.snapshotType?this._getSection("addons"):void 0;return i.dy`
      ${this.snapshot?i.dy`<div class="details">
            ${"full"===this.snapshot.type?this.supervisor.localize("snapshot.full_snapshot"):this.supervisor.localize("snapshot.partial_snapshot")}
            (${Math.ceil(10*this.snapshot.size)/10+" MB"})<br />
            ${j(new Date(this.snapshot.date),this.hass.locale)}
          </div>`:i.dy`<paper-input
            name="snapshotName"
            .label=${this.supervisor.localize("snapshot.name")}
            .value=${this.snapshotName}
            @value-changed=${this._handleTextValueChanged}
          >
          </paper-input>`}
      ${this.snapshot&&"full"!==this.snapshot.type?"":i.dy`<div class="sub-header">
              ${this.snapshot?this.supervisor.localize("snapshot.select_type"):this.supervisor.localize("snapshot.type")}
            </div>
            <div class="snapshot-types">
              <ha-formfield
                .label=${this.supervisor.localize("snapshot.full_snapshot")}
              >
                <ha-radio
                  @change=${this._handleRadioValueChanged}
                  value="full"
                  name="snapshotType"
                  .checked=${"full"===this.snapshotType}
                >
                </ha-radio>
              </ha-formfield>
              <ha-formfield
                .label=${this.supervisor.localize("snapshot.partial_snapshot")}
              >
                <ha-radio
                  @change=${this._handleRadioValueChanged}
                  value="partial"
                  name="snapshotType"
                  .checked=${"partial"===this.snapshotType}
                >
                </ha-radio>
              </ha-formfield>
            </div>`}
      ${this.snapshot&&"partial"===this.snapshotType?i.dy`
            ${this.snapshot.homeassistant?i.dy`
                  <ha-formfield
                    .label=${i.dy`<supervisor-formfield-label
                      label="Home Assistant"
                      .iconPath=${n.T__}
                      .version=${this.snapshot.homeassistant}
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
          `:""}
      ${"partial"===this.snapshotType?i.dy`
            ${null!=e&&e.templates.length?i.dy`
                  <ha-formfield
                    .label=${i.dy`<supervisor-formfield-label
                      .label=${this.supervisor.localize("snapshot.folders")}
                      .iconPath=${n.in3}
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
                      .label=${this.supervisor.localize("snapshot.addons")}
                      .iconPath=${n.$Z0}
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
          `:""}
      ${this.snapshot?"":i.dy`<ha-formfield
            .label=${this.supervisor.localize("snapshot.password_protection")}
          >
            <ha-checkbox
              .checked=${this.snapshotHasPassword}
              @change=${this._toggleHasPassword}
            >
            </ha-checkbox
          ></ha-formfield>`}
      ${this.snapshotHasPassword?i.dy`
            <paper-input
              .label=${this.supervisor.localize("snapshot.password")}
              type="password"
              name="snapshotPassword"
              .value=${this.snapshotPassword}
              @value-changed=${this._handleTextValueChanged}
            >
            </paper-input>
          `:""}
    `}},{kind:"get",static:!0,key:"styles",value:function(){return i.iv`
      ha-checkbox {
        --mdc-checkbox-touch-target-size: 16px;
        display: block;
        margin: 4px 12px 8px 0;
      }
      ha-formfield {
        display: contents;
      }
      supervisor-formfield-label {
        display: inline-flex;
        align-items: center;
      }
      paper-input[type="password"] {
        display: block;
        margin: 4px 0 4px 16px;
      }
      .details {
        color: var(--secondary-text-color);
      }
      .section-content {
        display: flex;
        flex-direction: column;
        margin-left: 16px;
      }
      .security {
        margin-top: 16px;
      }
      .snapshot-types {
        display: flex;
      }
      .sub-header {
        margin-top: 8px;
      }
    `}},{kind:"method",key:"snapshotDetails",value:function(){var e,t;const r={};if(this.snapshot||(r.name=this.snapshotName||z(new Date,this.hass.locale)),this.snapshotHasPassword&&(r.password=this.snapshotPassword),"full"===this.snapshotType)return r;const n=null===(e=this.addons)||void 0===e?void 0:e.filter((e=>e.checked)).map((e=>e.slug)),i=null===(t=this.folders)||void 0===t?void 0:t.filter((e=>e.checked)).map((e=>e.slug));return null!=n&&n.length&&(r.addons=n),null!=i&&i.length&&(r.folders=i),this.homeAssistant&&(r.homeassistant=this.homeAssistant),r}},{kind:"method",key:"_getSection",value:function(e){const t=[],r="addons"===e?new Map(this.supervisor.addon.addons.map((e=>[e.slug,e]))):void 0;let o=0;this[e].forEach((a=>{var l;t.push(i.dy`<ha-formfield
        .label=${i.dy`<supervisor-formfield-label
          .label=${a.name}
          .iconPath=${"addons"===e?n.$Z0:n.in3}
          .imageUrl=${"addons"===e&&(0,s.I)(this.hass.config.version,0,105)&&null!=r&&null!==(l=r.get(a.slug))&&void 0!==l&&l.icon?`/api/hassio/addons/${a.slug}/icon`:void 0}
          .version=${a.version}
        >
        </supervisor-formfield-label>`}
      >
        <ha-checkbox
          .item=${a}
          .checked=${a.checked}
          .section=${e}
          @change=${this._updateSectionEntry}
        >
        </ha-checkbox>
      </ha-formfield>`),a.checked&&o++}));const a=o===this[e].length;return{templates:t,checked:a,indeterminate:!a&&0!==o}}},{kind:"method",key:"_handleRadioValueChanged",value:function(e){const t=e.currentTarget;this[t.name]=t.value}},{kind:"method",key:"_handleTextValueChanged",value:function(e){this[e.currentTarget.name]=e.detail.value}},{kind:"method",key:"_toggleHasPassword",value:function(){this.snapshotHasPassword=!this.snapshotHasPassword}},{kind:"method",key:"_toggleSection",value:function(e){const t=e.currentTarget.section;this[t]=("addons"===t?this.addons:this.folders).map((t=>({...t,checked:e.currentTarget.checked})))}},{kind:"method",key:"_updateSectionEntry",value:function(e){const t=e.currentTarget.item,r=e.currentTarget.section;this[r]=this[r].map((r=>r.slug===t.slug?{...r,checked:e.currentTarget.checked}:r))}}]}}),i.oi)}}]);
//# sourceMappingURL=chunk.991bf05e8f2ed347e989.js.map