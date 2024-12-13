export const id=27;export const ids=[27];export const modules={4433:(e,t,a)=>{Object.defineProperty(t,"__esModule",{value:!0}),t.GetOperands=function(e){(0,l.invariant)("string"==typeof e,"GetOperands should have been called with a string");var t=(0,l.ToNumber)(e);(0,l.invariant)(isFinite(t),"n should be finite");var a,r,i,n=e.indexOf("."),o="";-1===n?(a=t,r=0,i=0):(a=e.slice(0,n),o=e.slice(n,e.length),r=(0,l.ToNumber)(o),i=o.length);var u,c,s=Math.abs((0,l.ToNumber)(a));if(0!==r){var f=o.replace(/0+$/,"");u=f.length,c=(0,l.ToNumber)(f)}else u=0,c=0;return{Number:t,IntegerDigits:s,NumberOfFractionDigits:i,NumberOfFractionDigitsWithoutTrailing:u,FractionDigits:r,FractionDigitsWithoutTrailing:c}};var l=a(97555)},1332:(e,t,a)=>{Object.defineProperty(t,"__esModule",{value:!0}),t.InitializePluralRules=function(e,t,a,i){var n=i.availableLocales,o=i.relevantExtensionKeys,u=i.localeData,c=i.getDefaultLocale,s=i.getInternalSlots,f=(0,l.CanonicalizeLocaleList)(t),b=Object.create(null),d=(0,l.CoerceOptionsToObject)(a),p=s(e);p.initializedPluralRules=!0;var v=(0,l.GetOption)(d,"localeMatcher","string",["best fit","lookup"],"best fit");b.localeMatcher=v,p.type=(0,l.GetOption)(d,"type","string",["cardinal","ordinal"],"cardinal"),(0,l.SetNumberFormatDigitOptions)(p,d,0,3,"standard");var g=(0,r.ResolveLocale)(n,f,b,o,u,c);return p.locale=g.locale,e};var l=a(97555),r=a(70517)},71037:(e,t,a)=>{Object.defineProperty(t,"__esModule",{value:!0}),t.ResolvePlural=function(e,t,a){var i=a.getInternalSlots,n=a.PluralRuleSelect,o=i(e);if((0,l.invariant)("Object"===(0,l.Type)(o),"pl has to be an object"),(0,l.invariant)("initializedPluralRules"in o,"pluralrules must be initialized"),(0,l.invariant)("Number"===(0,l.Type)(t),"n must be a number"),!isFinite(t))return"other";var u=o.locale,c=o.type,s=(0,l.FormatNumericToString)(o,t).formattedString,f=(0,r.GetOperands)(s);return n(u,c,t,f)};var l=a(97555),r=a(4433)},87376:(e,t)=>{Object.defineProperty(t,"__esModule",{value:!0}),t.default=function(e){var t=a.get(e);t||(t=Object.create(null),a.set(e,t));return t};var a=new WeakMap},69140:(e,t,a)=>{a(24545),a(51855),a(82130),a(31743),a(22328),a(4959),a(62435),Object.defineProperty(t,"__esModule",{value:!0}),t.PluralRules=void 0;var l=a(79192),r=a(97555),i=a(1332),n=a(71037),o=l.__importDefault(a(87376));function u(e,t){if(!(e instanceof s))throw new TypeError("Method Intl.PluralRules.prototype.".concat(t," called on incompatible receiver ").concat(String(e)))}function c(e,t,a,l){var r=l.IntegerDigits,i=l.NumberOfFractionDigits,n=l.FractionDigits;return s.localeData[e].fn(i?"".concat(r,".").concat(n):r,"ordinal"===t)}var s=function(){function e(t,a){if(!(this&&this instanceof e?this.constructor:void 0))throw new TypeError("Intl.PluralRules must be called with 'new'");return(0,i.InitializePluralRules)(this,t,a,{availableLocales:e.availableLocales,relevantExtensionKeys:e.relevantExtensionKeys,localeData:e.localeData,getDefaultLocale:e.getDefaultLocale,getInternalSlots:o.default})}return e.prototype.resolvedOptions=function(){u(this,"resolvedOptions");var t=Object.create(null),a=(0,o.default)(this);return t.locale=a.locale,t.type=a.type,["minimumIntegerDigits","minimumFractionDigits","maximumFractionDigits","minimumSignificantDigits","maximumSignificantDigits"].forEach((function(e){var l=a[e];void 0!==l&&(t[e]=l)})),t.pluralCategories=l.__spreadArray([],e.localeData[t.locale].categories[t.type],!0),t},e.prototype.select=function(e){u(this,"select");var t=(0,r.ToNumber)(e);return(0,n.ResolvePlural)(this,t,{getInternalSlots:o.default,PluralRuleSelect:c})},e.prototype.toString=function(){return"[object Intl.PluralRules]"},e.supportedLocalesOf=function(t,a){return(0,r.SupportedLocales)(e.availableLocales,(0,r.CanonicalizeLocaleList)(t),a)},e.__addLocaleData=function(){for(var t=[],a=0;a<arguments.length;a++)t[a]=arguments[a];for(var l=0,r=t;l<r.length;l++){var i=r[l],n=i.data,o=i.locale;e.localeData[o]=n,e.availableLocales.add(o),e.__defaultLocale||(e.__defaultLocale=o)}},e.getDefaultLocale=function(){return e.__defaultLocale},e.localeData={},e.availableLocales=new Set,e.__defaultLocale="",e.relevantExtensionKeys=[],e.polyfilled=!0,e}();t.PluralRules=s;try{"undefined"!=typeof Symbol&&Object.defineProperty(s.prototype,Symbol.toStringTag,{value:"Intl.PluralRules",writable:!1,enumerable:!1,configurable:!0});try{Object.defineProperty(s,"length",{value:0,writable:!1,enumerable:!1,configurable:!0})}catch(e){}Object.defineProperty(s.prototype.constructor,"length",{value:0,writable:!1,enumerable:!1,configurable:!0}),Object.defineProperty(s.supportedLocalesOf,"length",{value:1,writable:!1,enumerable:!1,configurable:!0}),Object.defineProperty(s,"name",{value:"PluralRules",writable:!1,enumerable:!1,configurable:!0})}catch(e){}},50027:(e,t,a)=>{Object.defineProperty(t,"__esModule",{value:!0});var l=a(69140);Object.defineProperty(Intl,"PluralRules",{value:l.PluralRules,writable:!0,enumerable:!1,configurable:!0})}};
//# sourceMappingURL=27.p8D4fQhG5rc.js.map