/*! For license information please see 91d7b1f7.js.LICENSE.txt */
"use strict";(self.webpackChunkhome_assistant_frontend=self.webpackChunkhome_assistant_frontend||[]).push([[7853],{87853:function(t,e,i){function r(t){return r="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(t){return typeof t}:function(t){return t&&"function"==typeof Symbol&&t.constructor===Symbol&&t!==Symbol.prototype?"symbol":typeof t},r(t)}function s(t,e){for(var i=0;i<e.length;i++){var s=e[i];s.enumerable=s.enumerable||!1,s.configurable=!0,"value"in s&&(s.writable=!0),Object.defineProperty(t,(n=s.key,a=void 0,a=function(t,e){if("object"!==r(t)||null===t)return t;var i=t[Symbol.toPrimitive];if(void 0!==i){var s=i.call(t,e||"default");if("object"!==r(s))return s;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===e?String:Number)(t)}(n,"string"),"symbol"===r(a)?a:String(a)),s)}var n,a}i.r(e),i.d(e,{FlowLayout:function(){return C},flow:function(){return S}});var n=function(){function t(e){!function(t,e){if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}(this,t),this._map=new Map,this._roundAverageSize=!1,this.totalSize=0,!0===(null==e?void 0:e.roundAverageSize)&&(this._roundAverageSize=!0)}var e,i,r;return e=t,(i=[{key:"set",value:function(t,e){var i=this._map.get(t)||0;this._map.set(t,e),this.totalSize+=e-i}},{key:"averageSize",get:function(){if(this._map.size>0){var t=this.totalSize/this._map.size;return this._roundAverageSize?Math.round(t):t}return 0}},{key:"getSize",value:function(t){return this._map.get(t)}},{key:"clear",value:function(){this._map.clear(),this.totalSize=0}}])&&s(e.prototype,i),r&&s(e,r),Object.defineProperty(e,"prototype",{writable:!1}),t}(),a=i(73418);function o(t){return o="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(t){return typeof t}:function(t){return t&&"function"==typeof Symbol&&t.constructor===Symbol&&t!==Symbol.prototype?"symbol":typeof t},o(t)}function h(t,e,i){return(e=g(e))in t?Object.defineProperty(t,e,{value:i,enumerable:!0,configurable:!0,writable:!0}):t[e]=i,t}function c(t,e){return c=Object.setPrototypeOf?Object.setPrototypeOf.bind():function(t,e){return t.__proto__=e,t},c(t,e)}function l(t){var e=function(){if("undefined"==typeof Reflect||!Reflect.construct)return!1;if(Reflect.construct.sham)return!1;if("function"==typeof Proxy)return!0;try{return Boolean.prototype.valueOf.call(Reflect.construct(Boolean,[],(function(){}))),!0}catch(t){return!1}}();return function(){var i,r=u(t);if(e){var s=u(this).constructor;i=Reflect.construct(r,arguments,s)}else i=r.apply(this,arguments);return function(t,e){if(e&&("object"===o(e)||"function"==typeof e))return e;if(void 0!==e)throw new TypeError("Derived constructors may only return object or undefined");return function(t){if(void 0===t)throw new ReferenceError("this hasn't been initialised - super() hasn't been called");return t}(t)}(this,i)}}function u(t){return u=Object.setPrototypeOf?Object.getPrototypeOf.bind():function(t){return t.__proto__||Object.getPrototypeOf(t)},u(t)}function _(t,e){if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}function f(t,e){for(var i=0;i<e.length;i++){var r=e[i];r.enumerable=r.enumerable||!1,r.configurable=!0,"value"in r&&(r.writable=!0),Object.defineProperty(t,g(r.key),r)}}function y(t,e,i){return e&&f(t.prototype,e),i&&f(t,i),Object.defineProperty(t,"prototype",{writable:!1}),t}function g(t){var e=function(t,e){if("object"!==o(t)||null===t)return t;var i=t[Symbol.toPrimitive];if(void 0!==i){var r=i.call(t,e||"default");if("object"!==o(r))return r;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===e?String:Number)(t)}(t,"string");return"symbol"===o(e)?e:String(e)}function m(t){return function(t){if(Array.isArray(t))return p(t)}(t)||function(t){if("undefined"!=typeof Symbol&&null!=t[Symbol.iterator]||null!=t["@@iterator"])return Array.from(t)}(t)||v(t)||function(){throw new TypeError("Invalid attempt to spread non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()}function v(t,e){if(t){if("string"==typeof t)return p(t,e);var i=Object.prototype.toString.call(t).slice(8,-1);return"Object"===i&&t.constructor&&(i=t.constructor.name),"Map"===i||"Set"===i?Array.from(t):"Arguments"===i||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(i)?p(t,e):void 0}}function p(t,e){(null==e||e>t.length)&&(e=t.length);for(var i=0,r=new Array(e);i<e;i++)r[i]=t[i];return r}var S=function(t){return Object.assign({type:C},t)};function d(t){return"horizontal"===t?"marginLeft":"marginTop"}function z(t){return"horizontal"===t?"marginRight":"marginBottom"}function b(t,e){var i=[t,e].sort();return i[1]<=0?Math.min.apply(Math,m(i)):i[0]>=0?Math.max.apply(Math,m(i)):i[0]+i[1]}var P=function(){function t(){_(this,t),this._childSizeCache=new n,this._marginSizeCache=new n,this._metricsCache=new Map}return y(t,[{key:"update",value:function(t,e){var i,r,s=this,n=new Set;Object.keys(t).forEach((function(i){var r=Number(i);s._metricsCache.set(r,t[r]),s._childSizeCache.set(r,t[r][(0,a.qF)(e)]),n.add(r),n.add(r+1)}));var o,h=function(t,e){var i="undefined"!=typeof Symbol&&t[Symbol.iterator]||t["@@iterator"];if(!i){if(Array.isArray(t)||(i=v(t))||e&&t&&"number"==typeof t.length){i&&(t=i);var r=0,s=function(){};return{s:s,n:function(){return r>=t.length?{done:!0}:{done:!1,value:t[r++]}},e:function(t){throw t},f:s}}throw new TypeError("Invalid attempt to iterate non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}var n,a=!0,o=!1;return{s:function(){i=i.call(t)},n:function(){var t=i.next();return a=t.done,t},e:function(t){o=!0,n=t},f:function(){try{a||null==i.return||i.return()}finally{if(o)throw n}}}}(n);try{for(h.s();!(o=h.n()).done;){var c=o.value,l=(null===(i=this._metricsCache.get(c))||void 0===i?void 0:i[d(e)])||0,u=(null===(r=this._metricsCache.get(c-1))||void 0===r?void 0:r[z(e)])||0;this._marginSizeCache.set(c,b(l,u))}}catch(_){h.e(_)}finally{h.f()}}},{key:"averageChildSize",get:function(){return this._childSizeCache.averageSize}},{key:"totalChildSize",get:function(){return this._childSizeCache.totalSize}},{key:"averageMarginSize",get:function(){return this._marginSizeCache.averageSize}},{key:"totalMarginSize",get:function(){return this._marginSizeCache.totalSize}},{key:"getLeadingMarginValue",value:function(t,e){var i;return(null===(i=this._metricsCache.get(t))||void 0===i?void 0:i[d(e)])||0}},{key:"getChildSize",value:function(t){return this._childSizeCache.getSize(t)}},{key:"getMarginSize",value:function(t){return this._marginSizeCache.getSize(t)}},{key:"clear",value:function(){this._childSizeCache.clear(),this._marginSizeCache.clear(),this._metricsCache.clear()}}]),t}(),C=function(t){!function(t,e){if("function"!=typeof e&&null!==e)throw new TypeError("Super expression must either be null or a function");t.prototype=Object.create(e&&e.prototype,{constructor:{value:t,writable:!0,configurable:!0}}),Object.defineProperty(t,"prototype",{writable:!1}),e&&c(t,e)}(i,t);var e=l(i);function i(){var t;return _(this,i),(t=e.apply(this,arguments))._itemSize={width:100,height:100},t._physicalItems=new Map,t._newPhysicalItems=new Map,t._metricsCache=new P,t._anchorIdx=null,t._anchorPos=null,t._stable=!0,t._measureChildren=!0,t._estimate=!0,t}return y(i,[{key:"measureChildren",get:function(){return this._measureChildren}},{key:"updateItemSizes",value:function(t){this._metricsCache.update(t,this.direction),this._scheduleReflow()}},{key:"_getPhysicalItem",value:function(t){var e;return null!==(e=this._newPhysicalItems.get(t))&&void 0!==e?e:this._physicalItems.get(t)}},{key:"_getSize",value:function(t){return this._getPhysicalItem(t)&&this._metricsCache.getChildSize(t)}},{key:"_getAverageSize",value:function(){return this._metricsCache.averageChildSize||this._itemSize[this._sizeDim]}},{key:"_estimatePosition",value:function(t){var e=this._metricsCache;if(-1===this._first||-1===this._last)return e.averageMarginSize+t*(e.averageMarginSize+this._getAverageSize());if(t<this._first){var i=this._first-t;return this._getPhysicalItem(this._first).pos-(e.getMarginSize(this._first-1)||e.averageMarginSize)-(i*e.averageChildSize+(i-1)*e.averageMarginSize)}var r=t-this._last;return this._getPhysicalItem(this._last).pos+(e.getChildSize(this._last)||e.averageChildSize)+(e.getMarginSize(this._last)||e.averageMarginSize)+r*(e.averageChildSize+e.averageMarginSize)}},{key:"_getPosition",value:function(t){var e,i=this._getPhysicalItem(t),r=this._metricsCache.averageMarginSize;return 0===t?null!==(e=this._metricsCache.getMarginSize(0))&&void 0!==e?e:r:i?i.pos:this._estimatePosition(t)}},{key:"_calculateAnchor",value:function(t,e){return t<=0?0:e>this._scrollSize-this._viewDim1?this.items.length-1:Math.max(0,Math.min(this.items.length-1,Math.floor((t+e)/2/this._delta)))}},{key:"_getAnchor",value:function(t,e){if(0===this._physicalItems.size)return this._calculateAnchor(t,e);if(this._first<0)return this._calculateAnchor(t,e);if(this._last<0)return this._calculateAnchor(t,e);var i=this._getPhysicalItem(this._first),r=this._getPhysicalItem(this._last),s=i.pos;if(r.pos+this._metricsCache.getChildSize(this._last)<t)return this._calculateAnchor(t,e);if(s>e)return this._calculateAnchor(t,e);for(var n=this._firstVisible-1,a=-1/0;a<t;){a=this._getPhysicalItem(++n).pos+this._metricsCache.getChildSize(n)}return n}},{key:"_getActiveItems",value:function(){0===this._viewDim1||0===this.items.length?this._clearItems():this._getItems()}},{key:"_clearItems",value:function(){this._first=-1,this._last=-1,this._physicalMin=0,this._physicalMax=0;var t=this._newPhysicalItems;this._newPhysicalItems=this._physicalItems,this._newPhysicalItems.clear(),this._physicalItems=t,this._stable=!0}},{key:"_getItems",value:function(){var t,e,i,r,s=this._newPhysicalItems;if(this._stable=!0,null!==this.pin){var n=this.pin.index;this._anchorIdx=n,this._anchorPos=this._getPosition(n)}if(i=this._scrollPosition-this._overhang,(r=this._scrollPosition+this._viewDim1+this._overhang)<0||i>this._scrollSize)this._clearItems();else{null!==this._anchorIdx&&null!==this._anchorPos||(this._anchorIdx=this._getAnchor(i,r),this._anchorPos=this._getPosition(this._anchorIdx));var a=this._getSize(this._anchorIdx);void 0===a&&(this._stable=!1,a=this._getAverageSize());var o=null!==(t=this._metricsCache.getMarginSize(this._anchorIdx))&&void 0!==t?t:this._metricsCache.averageMarginSize,h=null!==(e=this._metricsCache.getMarginSize(this._anchorIdx+1))&&void 0!==e?e:this._metricsCache.averageMarginSize;0===this._anchorIdx&&(this._anchorPos=o),this._anchorIdx===this.items.length-1&&(this._anchorPos=this._scrollSize-h-a);var c=0;for(this._anchorPos+a+h<i&&(c=i-(this._anchorPos+a+h)),this._anchorPos-o>r&&(c=r-(this._anchorPos-o)),c&&(this._scrollPosition-=c,i-=c,r-=c,this._scrollError+=c),s.set(this._anchorIdx,{pos:this._anchorPos,size:a}),this._first=this._last=this._anchorIdx,this._physicalMin=this._anchorPos-o,this._physicalMax=this._anchorPos+a+h;this._physicalMin>i&&this._first>0;){var l=this._getSize(--this._first);void 0===l&&(this._stable=!1,l=this._getAverageSize());var u=this._metricsCache.getMarginSize(this._first);void 0===u&&(this._stable=!1,u=this._metricsCache.averageMarginSize),this._physicalMin-=l;var _=this._physicalMin;if(s.set(this._first,{pos:_,size:l}),this._physicalMin-=u,!1===this._stable&&!1===this._estimate)break}for(;this._physicalMax<r&&this._last<this.items.length-1;){var f=this._getSize(++this._last);void 0===f&&(this._stable=!1,f=this._getAverageSize());var y=this._metricsCache.getMarginSize(this._last);void 0===y&&(this._stable=!1,y=this._metricsCache.averageMarginSize);var g=this._physicalMax;if(s.set(this._last,{pos:g,size:f}),this._physicalMax+=f+y,!this._stable&&!this._estimate)break}var m=this._calculateError();m&&(this._physicalMin-=m,this._physicalMax-=m,this._anchorPos-=m,this._scrollPosition-=m,s.forEach((function(t){return t.pos-=m})),this._scrollError+=m),this._stable&&(this._newPhysicalItems=this._physicalItems,this._newPhysicalItems.clear(),this._physicalItems=s)}}},{key:"_calculateError",value:function(){return 0===this._first?this._physicalMin:this._physicalMin<=0?this._physicalMin-this._first*this._delta:this._last===this.items.length-1?this._physicalMax-this._scrollSize:this._physicalMax>=this._scrollSize?this._physicalMax-this._scrollSize+(this.items.length-1-this._last)*this._delta:0}},{key:"_reflow",value:function(){var t=this._first,e=this._last,i=this._scrollSize,r=this._firstVisible,s=this._lastVisible;this._updateScrollSize(),this._setPositionFromPin(),this._getActiveItems(),this._updateVisibleIndices(),this._scrollSize!==i&&this._emitScrollSize(),this._first===t&&this._last===e&&this._firstVisible===r&&this._lastVisible===s||this._emitRange(),-1===this._first&&-1===this._last||this._emitChildPositions(),0!==this._scrollError&&this._emitScrollError(),(-1===this._first&&-1==this._last||this._first===t&&this._last===e)&&this._resetReflowState()}},{key:"_resetReflowState",value:function(){this._anchorIdx=null,this._anchorPos=null,this._stable=!0}},{key:"_updateScrollSize",value:function(){var t=this._metricsCache.averageMarginSize;this._scrollSize=Math.max(1,this.items.length*(t+this._getAverageSize())+t)}},{key:"_delta",get:function(){var t=this._metricsCache.averageMarginSize;return this._getAverageSize()+t}},{key:"_getItemPosition",value:function(t){var e,i;return h(e={},this._positionDim,this._getPosition(t)),h(e,this._secondaryPositionDim,0),h(e,"horizontal"===this.direction?"xOffset":"yOffset",-(null!==(i=this._metricsCache.getLeadingMarginValue(t,this.direction))&&void 0!==i?i:this._metricsCache.averageMarginSize)),e}},{key:"_getItemSize",value:function(t){var e;return h(e={},this._sizeDim,this._getSize(t)||this._getAverageSize()),h(e,this._secondarySizeDim,this._itemSize[this._secondarySizeDim]),e}},{key:"_viewDim2Changed",value:function(){this._metricsCache.clear(),this._scheduleReflow()}}]),i}(a.IE)}}]);