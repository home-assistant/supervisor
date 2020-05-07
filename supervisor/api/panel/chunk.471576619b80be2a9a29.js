(self["webpackJsonp"] = self["webpackJsonp"] || []).push([[8],{

/***/ 101:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";

// EXTERNAL MODULE: ./node_modules/lit-element/lit-element.js + 3 modules
var lit_element = __webpack_require__(5);

// EXTERNAL MODULE: ./node_modules/memoize-one/dist/memoize-one.esm.js
var memoize_one_esm = __webpack_require__(50);

// EXTERNAL MODULE: ./src/common/navigate.ts
var common_navigate = __webpack_require__(38);

// EXTERNAL MODULE: ./node_modules/@material/mwc-button/mwc-button.js + 12 modules
var mwc_button = __webpack_require__(18);

// EXTERNAL MODULE: ./src/layouts/hass-subpage.ts
var hass_subpage = __webpack_require__(113);

// CONCATENATED MODULE: ./src/layouts/hass-error-screen.ts
function _typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { _typeof = function _typeof(obj) { return typeof obj; }; } else { _typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return _typeof(obj); }

function _templateObject2() {
  var data = _taggedTemplateLiteral(["\n        .content {\n          height: calc(100% - 64px);\n          display: flex;\n          align-items: center;\n          justify-content: center;\n          flex-direction: column;\n        }\n      "]);

  _templateObject2 = function _templateObject2() {
    return data;
  };

  return data;
}

function _templateObject() {
  var data = _taggedTemplateLiteral(["\n      <hass-subpage>\n        <div class=\"content\">\n          <h3>", "</h3>\n          <slot>\n            <mwc-button @click=", ">go back</mwc-button>\n          </slot>\n        </div>\n      </hass-subpage>\n    "]);

  _templateObject = function _templateObject() {
    return data;
  };

  return data;
}

function _taggedTemplateLiteral(strings, raw) { if (!raw) { raw = strings.slice(0); } return Object.freeze(Object.defineProperties(strings, { raw: { value: Object.freeze(raw) } })); }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) _setPrototypeOf(subClass, superClass); }

function _setPrototypeOf(o, p) { _setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return _setPrototypeOf(o, p); }

function _createSuper(Derived) { return function () { var Super = _getPrototypeOf(Derived), result; if (_isNativeReflectConstruct()) { var NewTarget = _getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return _possibleConstructorReturn(this, result); }; }

function _possibleConstructorReturn(self, call) { if (call && (_typeof(call) === "object" || typeof call === "function")) { return call; } return _assertThisInitialized(self); }

function _assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function _isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Date.prototype.toString.call(Reflect.construct(Date, [], function () {})); return true; } catch (e) { return false; } }

function _getPrototypeOf(o) { _getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return _getPrototypeOf(o); }

function _decorate(decorators, factory, superClass, mixins) { var api = _getDecoratorsApi(); if (mixins) { for (var i = 0; i < mixins.length; i++) { api = mixins[i](api); } } var r = factory(function initialize(O) { api.initializeInstanceElements(O, decorated.elements); }, superClass); var decorated = api.decorateClass(_coalesceClassElements(r.d.map(_createElementDescriptor)), decorators); api.initializeClassElements(r.F, decorated.elements); return api.runClassFinishers(r.F, decorated.finishers); }

function _getDecoratorsApi() { _getDecoratorsApi = function _getDecoratorsApi() { return api; }; var api = { elementsDefinitionOrder: [["method"], ["field"]], initializeInstanceElements: function initializeInstanceElements(O, elements) { ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { if (element.kind === kind && element.placement === "own") { this.defineClassElement(O, element); } }, this); }, this); }, initializeClassElements: function initializeClassElements(F, elements) { var proto = F.prototype; ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { var placement = element.placement; if (element.kind === kind && (placement === "static" || placement === "prototype")) { var receiver = placement === "static" ? F : proto; this.defineClassElement(receiver, element); } }, this); }, this); }, defineClassElement: function defineClassElement(receiver, element) { var descriptor = element.descriptor; if (element.kind === "field") { var initializer = element.initializer; descriptor = { enumerable: descriptor.enumerable, writable: descriptor.writable, configurable: descriptor.configurable, value: initializer === void 0 ? void 0 : initializer.call(receiver) }; } Object.defineProperty(receiver, element.key, descriptor); }, decorateClass: function decorateClass(elements, decorators) { var newElements = []; var finishers = []; var placements = { "static": [], prototype: [], own: [] }; elements.forEach(function (element) { this.addElementPlacement(element, placements); }, this); elements.forEach(function (element) { if (!_hasDecorators(element)) return newElements.push(element); var elementFinishersExtras = this.decorateElement(element, placements); newElements.push(elementFinishersExtras.element); newElements.push.apply(newElements, elementFinishersExtras.extras); finishers.push.apply(finishers, elementFinishersExtras.finishers); }, this); if (!decorators) { return { elements: newElements, finishers: finishers }; } var result = this.decorateConstructor(newElements, decorators); finishers.push.apply(finishers, result.finishers); result.finishers = finishers; return result; }, addElementPlacement: function addElementPlacement(element, placements, silent) { var keys = placements[element.placement]; if (!silent && keys.indexOf(element.key) !== -1) { throw new TypeError("Duplicated element (" + element.key + ")"); } keys.push(element.key); }, decorateElement: function decorateElement(element, placements) { var extras = []; var finishers = []; for (var decorators = element.decorators, i = decorators.length - 1; i >= 0; i--) { var keys = placements[element.placement]; keys.splice(keys.indexOf(element.key), 1); var elementObject = this.fromElementDescriptor(element); var elementFinisherExtras = this.toElementFinisherExtras((0, decorators[i])(elementObject) || elementObject); element = elementFinisherExtras.element; this.addElementPlacement(element, placements); if (elementFinisherExtras.finisher) { finishers.push(elementFinisherExtras.finisher); } var newExtras = elementFinisherExtras.extras; if (newExtras) { for (var j = 0; j < newExtras.length; j++) { this.addElementPlacement(newExtras[j], placements); } extras.push.apply(extras, newExtras); } } return { element: element, finishers: finishers, extras: extras }; }, decorateConstructor: function decorateConstructor(elements, decorators) { var finishers = []; for (var i = decorators.length - 1; i >= 0; i--) { var obj = this.fromClassDescriptor(elements); var elementsAndFinisher = this.toClassDescriptor((0, decorators[i])(obj) || obj); if (elementsAndFinisher.finisher !== undefined) { finishers.push(elementsAndFinisher.finisher); } if (elementsAndFinisher.elements !== undefined) { elements = elementsAndFinisher.elements; for (var j = 0; j < elements.length - 1; j++) { for (var k = j + 1; k < elements.length; k++) { if (elements[j].key === elements[k].key && elements[j].placement === elements[k].placement) { throw new TypeError("Duplicated element (" + elements[j].key + ")"); } } } } } return { elements: elements, finishers: finishers }; }, fromElementDescriptor: function fromElementDescriptor(element) { var obj = { kind: element.kind, key: element.key, placement: element.placement, descriptor: element.descriptor }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); if (element.kind === "field") obj.initializer = element.initializer; return obj; }, toElementDescriptors: function toElementDescriptors(elementObjects) { if (elementObjects === undefined) return; return _toArray(elementObjects).map(function (elementObject) { var element = this.toElementDescriptor(elementObject); this.disallowProperty(elementObject, "finisher", "An element descriptor"); this.disallowProperty(elementObject, "extras", "An element descriptor"); return element; }, this); }, toElementDescriptor: function toElementDescriptor(elementObject) { var kind = String(elementObject.kind); if (kind !== "method" && kind !== "field") { throw new TypeError('An element descriptor\'s .kind property must be either "method" or' + ' "field", but a decorator created an element descriptor with' + ' .kind "' + kind + '"'); } var key = _toPropertyKey(elementObject.key); var placement = String(elementObject.placement); if (placement !== "static" && placement !== "prototype" && placement !== "own") { throw new TypeError('An element descriptor\'s .placement property must be one of "static",' + ' "prototype" or "own", but a decorator created an element descriptor' + ' with .placement "' + placement + '"'); } var descriptor = elementObject.descriptor; this.disallowProperty(elementObject, "elements", "An element descriptor"); var element = { kind: kind, key: key, placement: placement, descriptor: Object.assign({}, descriptor) }; if (kind !== "field") { this.disallowProperty(elementObject, "initializer", "A method descriptor"); } else { this.disallowProperty(descriptor, "get", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "set", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "value", "The property descriptor of a field descriptor"); element.initializer = elementObject.initializer; } return element; }, toElementFinisherExtras: function toElementFinisherExtras(elementObject) { var element = this.toElementDescriptor(elementObject); var finisher = _optionalCallableProperty(elementObject, "finisher"); var extras = this.toElementDescriptors(elementObject.extras); return { element: element, finisher: finisher, extras: extras }; }, fromClassDescriptor: function fromClassDescriptor(elements) { var obj = { kind: "class", elements: elements.map(this.fromElementDescriptor, this) }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); return obj; }, toClassDescriptor: function toClassDescriptor(obj) { var kind = String(obj.kind); if (kind !== "class") { throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator' + ' created a class descriptor with .kind "' + kind + '"'); } this.disallowProperty(obj, "key", "A class descriptor"); this.disallowProperty(obj, "placement", "A class descriptor"); this.disallowProperty(obj, "descriptor", "A class descriptor"); this.disallowProperty(obj, "initializer", "A class descriptor"); this.disallowProperty(obj, "extras", "A class descriptor"); var finisher = _optionalCallableProperty(obj, "finisher"); var elements = this.toElementDescriptors(obj.elements); return { elements: elements, finisher: finisher }; }, runClassFinishers: function runClassFinishers(constructor, finishers) { for (var i = 0; i < finishers.length; i++) { var newConstructor = (0, finishers[i])(constructor); if (newConstructor !== undefined) { if (typeof newConstructor !== "function") { throw new TypeError("Finishers must return a constructor."); } constructor = newConstructor; } } return constructor; }, disallowProperty: function disallowProperty(obj, name, objectType) { if (obj[name] !== undefined) { throw new TypeError(objectType + " can't have a ." + name + " property."); } } }; return api; }

function _createElementDescriptor(def) { var key = _toPropertyKey(def.key); var descriptor; if (def.kind === "method") { descriptor = { value: def.value, writable: true, configurable: true, enumerable: false }; } else if (def.kind === "get") { descriptor = { get: def.value, configurable: true, enumerable: false }; } else if (def.kind === "set") { descriptor = { set: def.value, configurable: true, enumerable: false }; } else if (def.kind === "field") { descriptor = { configurable: true, writable: true, enumerable: true }; } var element = { kind: def.kind === "field" ? "field" : "method", key: key, placement: def["static"] ? "static" : def.kind === "field" ? "own" : "prototype", descriptor: descriptor }; if (def.decorators) element.decorators = def.decorators; if (def.kind === "field") element.initializer = def.value; return element; }

function _coalesceGetterSetter(element, other) { if (element.descriptor.get !== undefined) { other.descriptor.get = element.descriptor.get; } else { other.descriptor.set = element.descriptor.set; } }

function _coalesceClassElements(elements) { var newElements = []; var isSameElement = function isSameElement(other) { return other.kind === "method" && other.key === element.key && other.placement === element.placement; }; for (var i = 0; i < elements.length; i++) { var element = elements[i]; var other; if (element.kind === "method" && (other = newElements.find(isSameElement))) { if (_isDataDescriptor(element.descriptor) || _isDataDescriptor(other.descriptor)) { if (_hasDecorators(element) || _hasDecorators(other)) { throw new ReferenceError("Duplicated methods (" + element.key + ") can't be decorated."); } other.descriptor = element.descriptor; } else { if (_hasDecorators(element)) { if (_hasDecorators(other)) { throw new ReferenceError("Decorators can't be placed on different accessors with for " + "the same property (" + element.key + ")."); } other.decorators = element.decorators; } _coalesceGetterSetter(element, other); } } else { newElements.push(element); } } return newElements; }

function _hasDecorators(element) { return element.decorators && element.decorators.length; }

function _isDataDescriptor(desc) { return desc !== undefined && !(desc.value === undefined && desc.writable === undefined); }

function _optionalCallableProperty(obj, name) { var value = obj[name]; if (value !== undefined && typeof value !== "function") { throw new TypeError("Expected '" + name + "' to be a function"); } return value; }

function _toPropertyKey(arg) { var key = _toPrimitive(arg, "string"); return _typeof(key) === "symbol" ? key : String(key); }

function _toPrimitive(input, hint) { if (_typeof(input) !== "object" || input === null) return input; var prim = input[Symbol.toPrimitive]; if (prim !== undefined) { var res = prim.call(input, hint || "default"); if (_typeof(res) !== "object") return res; throw new TypeError("@@toPrimitive must return a primitive value."); } return (hint === "string" ? String : Number)(input); }

function _toArray(arr) { return _arrayWithHoles(arr) || _iterableToArray(arr) || _unsupportedIterableToArray(arr) || _nonIterableRest(); }

function _nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function _unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return _arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(n); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return _arrayLikeToArray(o, minLen); }

function _arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function _iterableToArray(iter) { if (typeof Symbol !== "undefined" && Symbol.iterator in Object(iter)) return Array.from(iter); }

function _arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }





var hass_error_screen_HassErrorScreen = _decorate([Object(lit_element["d" /* customElement */])("hass-error-screen")], function (_initialize, _LitElement) {
  var HassErrorScreen = /*#__PURE__*/function (_LitElement2) {
    _inherits(HassErrorScreen, _LitElement2);

    var _super = _createSuper(HassErrorScreen);

    function HassErrorScreen() {
      var _this;

      _classCallCheck(this, HassErrorScreen);

      for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
        args[_key] = arguments[_key];
      }

      _this = _super.call.apply(_super, [this].concat(args));

      _initialize(_assertThisInitialized(_this));

      return _this;
    }

    return HassErrorScreen;
  }(_LitElement);

  return {
    F: HassErrorScreen,
    d: [{
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "error",
      value: void 0
    }, {
      kind: "method",
      key: "render",
      value: function render() {
        return Object(lit_element["e" /* html */])(_templateObject(), this.error, this._backTapped);
      }
    }, {
      kind: "method",
      key: "_backTapped",
      value: function _backTapped() {
        history.back();
      }
    }, {
      kind: "get",
      "static": true,
      key: "styles",
      value: function styles() {
        return [Object(lit_element["c" /* css */])(_templateObject2())];
      }
    }]
  };
}, lit_element["a" /* LitElement */]);
// EXTERNAL MODULE: ./src/layouts/hass-loading-screen.ts
var hass_loading_screen = __webpack_require__(114);

// CONCATENATED MODULE: ./src/layouts/hass-router-page.ts
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "a", function() { return hass_router_page_HassRouterPage; });
function asyncGeneratorStep(gen, resolve, reject, _next, _throw, key, arg) { try { var info = gen[key](arg); var value = info.value; } catch (error) { reject(error); return; } if (info.done) { resolve(value); } else { Promise.resolve(value).then(_next, _throw); } }

function _asyncToGenerator(fn) { return function () { var self = this, args = arguments; return new Promise(function (resolve, reject) { var gen = fn.apply(self, args); function _next(value) { asyncGeneratorStep(gen, resolve, reject, _next, _throw, "next", value); } function _throw(err) { asyncGeneratorStep(gen, resolve, reject, _next, _throw, "throw", err); } _next(undefined); }); }; }

function hass_router_page_typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { hass_router_page_typeof = function _typeof(obj) { return typeof obj; }; } else { hass_router_page_typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return hass_router_page_typeof(obj); }

function hass_router_page_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function hass_router_page_inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) hass_router_page_setPrototypeOf(subClass, superClass); }

function hass_router_page_setPrototypeOf(o, p) { hass_router_page_setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return hass_router_page_setPrototypeOf(o, p); }

function hass_router_page_createSuper(Derived) { return function () { var Super = hass_router_page_getPrototypeOf(Derived), result; if (hass_router_page_isNativeReflectConstruct()) { var NewTarget = hass_router_page_getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return hass_router_page_possibleConstructorReturn(this, result); }; }

function hass_router_page_possibleConstructorReturn(self, call) { if (call && (hass_router_page_typeof(call) === "object" || typeof call === "function")) { return call; } return hass_router_page_assertThisInitialized(self); }

function hass_router_page_assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function hass_router_page_isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Date.prototype.toString.call(Reflect.construct(Date, [], function () {})); return true; } catch (e) { return false; } }

function hass_router_page_decorate(decorators, factory, superClass, mixins) { var api = hass_router_page_getDecoratorsApi(); if (mixins) { for (var i = 0; i < mixins.length; i++) { api = mixins[i](api); } } var r = factory(function initialize(O) { api.initializeInstanceElements(O, decorated.elements); }, superClass); var decorated = api.decorateClass(hass_router_page_coalesceClassElements(r.d.map(hass_router_page_createElementDescriptor)), decorators); api.initializeClassElements(r.F, decorated.elements); return api.runClassFinishers(r.F, decorated.finishers); }

function hass_router_page_getDecoratorsApi() { hass_router_page_getDecoratorsApi = function _getDecoratorsApi() { return api; }; var api = { elementsDefinitionOrder: [["method"], ["field"]], initializeInstanceElements: function initializeInstanceElements(O, elements) { ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { if (element.kind === kind && element.placement === "own") { this.defineClassElement(O, element); } }, this); }, this); }, initializeClassElements: function initializeClassElements(F, elements) { var proto = F.prototype; ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { var placement = element.placement; if (element.kind === kind && (placement === "static" || placement === "prototype")) { var receiver = placement === "static" ? F : proto; this.defineClassElement(receiver, element); } }, this); }, this); }, defineClassElement: function defineClassElement(receiver, element) { var descriptor = element.descriptor; if (element.kind === "field") { var initializer = element.initializer; descriptor = { enumerable: descriptor.enumerable, writable: descriptor.writable, configurable: descriptor.configurable, value: initializer === void 0 ? void 0 : initializer.call(receiver) }; } Object.defineProperty(receiver, element.key, descriptor); }, decorateClass: function decorateClass(elements, decorators) { var newElements = []; var finishers = []; var placements = { "static": [], prototype: [], own: [] }; elements.forEach(function (element) { this.addElementPlacement(element, placements); }, this); elements.forEach(function (element) { if (!hass_router_page_hasDecorators(element)) return newElements.push(element); var elementFinishersExtras = this.decorateElement(element, placements); newElements.push(elementFinishersExtras.element); newElements.push.apply(newElements, elementFinishersExtras.extras); finishers.push.apply(finishers, elementFinishersExtras.finishers); }, this); if (!decorators) { return { elements: newElements, finishers: finishers }; } var result = this.decorateConstructor(newElements, decorators); finishers.push.apply(finishers, result.finishers); result.finishers = finishers; return result; }, addElementPlacement: function addElementPlacement(element, placements, silent) { var keys = placements[element.placement]; if (!silent && keys.indexOf(element.key) !== -1) { throw new TypeError("Duplicated element (" + element.key + ")"); } keys.push(element.key); }, decorateElement: function decorateElement(element, placements) { var extras = []; var finishers = []; for (var decorators = element.decorators, i = decorators.length - 1; i >= 0; i--) { var keys = placements[element.placement]; keys.splice(keys.indexOf(element.key), 1); var elementObject = this.fromElementDescriptor(element); var elementFinisherExtras = this.toElementFinisherExtras((0, decorators[i])(elementObject) || elementObject); element = elementFinisherExtras.element; this.addElementPlacement(element, placements); if (elementFinisherExtras.finisher) { finishers.push(elementFinisherExtras.finisher); } var newExtras = elementFinisherExtras.extras; if (newExtras) { for (var j = 0; j < newExtras.length; j++) { this.addElementPlacement(newExtras[j], placements); } extras.push.apply(extras, newExtras); } } return { element: element, finishers: finishers, extras: extras }; }, decorateConstructor: function decorateConstructor(elements, decorators) { var finishers = []; for (var i = decorators.length - 1; i >= 0; i--) { var obj = this.fromClassDescriptor(elements); var elementsAndFinisher = this.toClassDescriptor((0, decorators[i])(obj) || obj); if (elementsAndFinisher.finisher !== undefined) { finishers.push(elementsAndFinisher.finisher); } if (elementsAndFinisher.elements !== undefined) { elements = elementsAndFinisher.elements; for (var j = 0; j < elements.length - 1; j++) { for (var k = j + 1; k < elements.length; k++) { if (elements[j].key === elements[k].key && elements[j].placement === elements[k].placement) { throw new TypeError("Duplicated element (" + elements[j].key + ")"); } } } } } return { elements: elements, finishers: finishers }; }, fromElementDescriptor: function fromElementDescriptor(element) { var obj = { kind: element.kind, key: element.key, placement: element.placement, descriptor: element.descriptor }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); if (element.kind === "field") obj.initializer = element.initializer; return obj; }, toElementDescriptors: function toElementDescriptors(elementObjects) { if (elementObjects === undefined) return; return hass_router_page_toArray(elementObjects).map(function (elementObject) { var element = this.toElementDescriptor(elementObject); this.disallowProperty(elementObject, "finisher", "An element descriptor"); this.disallowProperty(elementObject, "extras", "An element descriptor"); return element; }, this); }, toElementDescriptor: function toElementDescriptor(elementObject) { var kind = String(elementObject.kind); if (kind !== "method" && kind !== "field") { throw new TypeError('An element descriptor\'s .kind property must be either "method" or' + ' "field", but a decorator created an element descriptor with' + ' .kind "' + kind + '"'); } var key = hass_router_page_toPropertyKey(elementObject.key); var placement = String(elementObject.placement); if (placement !== "static" && placement !== "prototype" && placement !== "own") { throw new TypeError('An element descriptor\'s .placement property must be one of "static",' + ' "prototype" or "own", but a decorator created an element descriptor' + ' with .placement "' + placement + '"'); } var descriptor = elementObject.descriptor; this.disallowProperty(elementObject, "elements", "An element descriptor"); var element = { kind: kind, key: key, placement: placement, descriptor: Object.assign({}, descriptor) }; if (kind !== "field") { this.disallowProperty(elementObject, "initializer", "A method descriptor"); } else { this.disallowProperty(descriptor, "get", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "set", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "value", "The property descriptor of a field descriptor"); element.initializer = elementObject.initializer; } return element; }, toElementFinisherExtras: function toElementFinisherExtras(elementObject) { var element = this.toElementDescriptor(elementObject); var finisher = hass_router_page_optionalCallableProperty(elementObject, "finisher"); var extras = this.toElementDescriptors(elementObject.extras); return { element: element, finisher: finisher, extras: extras }; }, fromClassDescriptor: function fromClassDescriptor(elements) { var obj = { kind: "class", elements: elements.map(this.fromElementDescriptor, this) }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); return obj; }, toClassDescriptor: function toClassDescriptor(obj) { var kind = String(obj.kind); if (kind !== "class") { throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator' + ' created a class descriptor with .kind "' + kind + '"'); } this.disallowProperty(obj, "key", "A class descriptor"); this.disallowProperty(obj, "placement", "A class descriptor"); this.disallowProperty(obj, "descriptor", "A class descriptor"); this.disallowProperty(obj, "initializer", "A class descriptor"); this.disallowProperty(obj, "extras", "A class descriptor"); var finisher = hass_router_page_optionalCallableProperty(obj, "finisher"); var elements = this.toElementDescriptors(obj.elements); return { elements: elements, finisher: finisher }; }, runClassFinishers: function runClassFinishers(constructor, finishers) { for (var i = 0; i < finishers.length; i++) { var newConstructor = (0, finishers[i])(constructor); if (newConstructor !== undefined) { if (typeof newConstructor !== "function") { throw new TypeError("Finishers must return a constructor."); } constructor = newConstructor; } } return constructor; }, disallowProperty: function disallowProperty(obj, name, objectType) { if (obj[name] !== undefined) { throw new TypeError(objectType + " can't have a ." + name + " property."); } } }; return api; }

function hass_router_page_createElementDescriptor(def) { var key = hass_router_page_toPropertyKey(def.key); var descriptor; if (def.kind === "method") { descriptor = { value: def.value, writable: true, configurable: true, enumerable: false }; } else if (def.kind === "get") { descriptor = { get: def.value, configurable: true, enumerable: false }; } else if (def.kind === "set") { descriptor = { set: def.value, configurable: true, enumerable: false }; } else if (def.kind === "field") { descriptor = { configurable: true, writable: true, enumerable: true }; } var element = { kind: def.kind === "field" ? "field" : "method", key: key, placement: def["static"] ? "static" : def.kind === "field" ? "own" : "prototype", descriptor: descriptor }; if (def.decorators) element.decorators = def.decorators; if (def.kind === "field") element.initializer = def.value; return element; }

function hass_router_page_coalesceGetterSetter(element, other) { if (element.descriptor.get !== undefined) { other.descriptor.get = element.descriptor.get; } else { other.descriptor.set = element.descriptor.set; } }

function hass_router_page_coalesceClassElements(elements) { var newElements = []; var isSameElement = function isSameElement(other) { return other.kind === "method" && other.key === element.key && other.placement === element.placement; }; for (var i = 0; i < elements.length; i++) { var element = elements[i]; var other; if (element.kind === "method" && (other = newElements.find(isSameElement))) { if (hass_router_page_isDataDescriptor(element.descriptor) || hass_router_page_isDataDescriptor(other.descriptor)) { if (hass_router_page_hasDecorators(element) || hass_router_page_hasDecorators(other)) { throw new ReferenceError("Duplicated methods (" + element.key + ") can't be decorated."); } other.descriptor = element.descriptor; } else { if (hass_router_page_hasDecorators(element)) { if (hass_router_page_hasDecorators(other)) { throw new ReferenceError("Decorators can't be placed on different accessors with for " + "the same property (" + element.key + ")."); } other.decorators = element.decorators; } hass_router_page_coalesceGetterSetter(element, other); } } else { newElements.push(element); } } return newElements; }

function hass_router_page_hasDecorators(element) { return element.decorators && element.decorators.length; }

function hass_router_page_isDataDescriptor(desc) { return desc !== undefined && !(desc.value === undefined && desc.writable === undefined); }

function hass_router_page_optionalCallableProperty(obj, name) { var value = obj[name]; if (value !== undefined && typeof value !== "function") { throw new TypeError("Expected '" + name + "' to be a function"); } return value; }

function hass_router_page_toPropertyKey(arg) { var key = hass_router_page_toPrimitive(arg, "string"); return hass_router_page_typeof(key) === "symbol" ? key : String(key); }

function hass_router_page_toPrimitive(input, hint) { if (hass_router_page_typeof(input) !== "object" || input === null) return input; var prim = input[Symbol.toPrimitive]; if (prim !== undefined) { var res = prim.call(input, hint || "default"); if (hass_router_page_typeof(res) !== "object") return res; throw new TypeError("@@toPrimitive must return a primitive value."); } return (hint === "string" ? String : Number)(input); }

function hass_router_page_toArray(arr) { return hass_router_page_arrayWithHoles(arr) || hass_router_page_iterableToArray(arr) || hass_router_page_unsupportedIterableToArray(arr) || hass_router_page_nonIterableRest(); }

function hass_router_page_nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function hass_router_page_unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return hass_router_page_arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(n); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return hass_router_page_arrayLikeToArray(o, minLen); }

function hass_router_page_arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function hass_router_page_iterableToArray(iter) { if (typeof Symbol !== "undefined" && Symbol.iterator in Object(iter)) return Array.from(iter); }

function hass_router_page_arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }

function _get(target, property, receiver) { if (typeof Reflect !== "undefined" && Reflect.get) { _get = Reflect.get; } else { _get = function _get(target, property, receiver) { var base = _superPropBase(target, property); if (!base) return; var desc = Object.getOwnPropertyDescriptor(base, property); if (desc.get) { return desc.get.call(receiver); } return desc.value; }; } return _get(target, property, receiver || target); }

function _superPropBase(object, property) { while (!Object.prototype.hasOwnProperty.call(object, property)) { object = hass_router_page_getPrototypeOf(object); if (object === null) break; } return object; }

function hass_router_page_getPrototypeOf(o) { hass_router_page_getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return hass_router_page_getPrototypeOf(o); }







var extractPage = function extractPage(path, defaultPage) {
  if (path === "") {
    return defaultPage;
  }

  var subpathStart = path.indexOf("/", 1);
  return subpathStart === -1 ? path.substr(1) : path.substr(1, subpathStart - 1);
};

// Time to wait for code to load before we show loading screen.
var LOADING_SCREEN_THRESHOLD = 400; // ms

var hass_router_page_HassRouterPage = hass_router_page_decorate(null, function (_initialize, _UpdatingElement) {
  var HassRouterPage = /*#__PURE__*/function (_UpdatingElement2) {
    hass_router_page_inherits(HassRouterPage, _UpdatingElement2);

    var _super = hass_router_page_createSuper(HassRouterPage);

    function HassRouterPage() {
      var _this;

      hass_router_page_classCallCheck(this, HassRouterPage);

      for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
        args[_key] = arguments[_key];
      }

      _this = _super.call.apply(_super, [this].concat(args));

      _initialize(hass_router_page_assertThisInitialized(_this));

      return _this;
    }

    return HassRouterPage;
  }(_UpdatingElement);

  return {
    F: HassRouterPage,
    d: [{
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "route",
      value: void 0
    }, {
      kind: "field",
      key: "routerOptions",
      value: void 0
    }, {
      kind: "field",
      key: "_currentPage",
      value: function value() {
        return "";
      }
    }, {
      kind: "field",
      key: "_currentLoadProm",
      value: void 0
    }, {
      kind: "field",
      key: "_cache",
      value: function value() {
        return {};
      }
    }, {
      kind: "field",
      key: "_initialLoadDone",
      value: function value() {
        return false;
      }
    }, {
      kind: "field",
      key: "_computeTail",
      value: function value() {
        return Object(memoize_one_esm["a" /* default */])(function (route) {
          var dividerPos = route.path.indexOf("/", 1);
          return dividerPos === -1 ? {
            prefix: route.prefix + route.path,
            path: ""
          } : {
            prefix: route.prefix + route.path.substr(0, dividerPos),
            path: route.path.substr(dividerPos)
          };
        });
      }
    }, {
      kind: "method",
      key: "update",
      value: function update(changedProps) {
        var _this2 = this;

        _get(hass_router_page_getPrototypeOf(HassRouterPage.prototype), "update", this).call(this, changedProps);

        var routerOptions = this.routerOptions || {
          routes: {}
        };

        if (routerOptions && routerOptions.initialLoad && !this._initialLoadDone) {
          return;
        }

        if (!changedProps.has("route")) {
          // Do not update if we have a currentLoadProm, because that means
          // that there is still an old panel shown and we're moving to a new one.
          if (this.lastChild && !this._currentLoadProm) {
            this.updatePageEl(this.lastChild, changedProps);
          }

          return;
        }

        var route = this.route;
        var defaultPage = routerOptions.defaultPage;

        if (route && route.path === "" && defaultPage !== undefined) {
          Object(common_navigate["a" /* navigate */])(this, "".concat(route.prefix, "/").concat(defaultPage), true);
        }

        var newPage = route ? extractPage(route.path, defaultPage || "") : "not_found";
        var routeOptions = routerOptions.routes[newPage]; // Handle redirects

        while (typeof routeOptions === "string") {
          newPage = routeOptions;
          routeOptions = routerOptions.routes[newPage];
        }

        if (routerOptions.beforeRender) {
          var result = routerOptions.beforeRender(newPage);

          if (result !== undefined) {
            newPage = result;
            routeOptions = routerOptions.routes[newPage]; // Handle redirects

            while (typeof routeOptions === "string") {
              newPage = routeOptions;
              routeOptions = routerOptions.routes[newPage];
            } // Update the url if we know where we're mounted.


            if (route) {
              Object(common_navigate["a" /* navigate */])(this, "".concat(route.prefix, "/").concat(result), true);
            }
          }
        }

        if (this._currentPage === newPage) {
          if (this.lastChild) {
            this.updatePageEl(this.lastChild, changedProps);
          }

          return;
        }

        if (!routeOptions) {
          this._currentPage = "";

          if (this.lastChild) {
            this.removeChild(this.lastChild);
          }

          return;
        }

        this._currentPage = newPage;
        var loadProm = routeOptions.load ? routeOptions.load() : Promise.resolve(); // Check when loading the page source failed.

        loadProm["catch"](function (err) {
          // eslint-disable-next-line
          console.error("Error loading page", newPage, err); // Verify that we're still trying to show the same page.

          if (_this2._currentPage !== newPage) {
            return;
          } // Removes either loading screen or the panel


          _this2.removeChild(_this2.lastChild); // Show error screen


          var errorEl = document.createElement("hass-error-screen");
          errorEl.error = "Error while loading page ".concat(newPage, ".");

          _this2.appendChild(errorEl);
        }); // If we don't show loading screen, just show the panel.
        // It will be automatically upgraded when loading done.

        if (!routerOptions.showLoading) {
          this._createPanel(routerOptions, newPage, routeOptions);

          return;
        } // We are only going to show the loading screen after some time.
        // That way we won't have a double fast flash on fast connections.


        var created = false;
        setTimeout(function () {
          if (created || _this2._currentPage !== newPage) {
            return;
          } // Show a loading screen.


          if (_this2.lastChild) {
            _this2.removeChild(_this2.lastChild);
          }

          _this2.appendChild(_this2.createLoadingScreen());
        }, LOADING_SCREEN_THRESHOLD);
        this._currentLoadProm = loadProm.then(function () {
          _this2._currentLoadProm = undefined; // Check if we're still trying to show the same page.

          if (_this2._currentPage !== newPage) {
            return;
          }

          created = true;

          _this2._createPanel(routerOptions, newPage, // @ts-ignore TS forgot this is not a string.
          routeOptions);
        }, function () {
          _this2._currentLoadProm = undefined;
        });
      }
    }, {
      kind: "method",
      key: "firstUpdated",
      value: function firstUpdated(changedProps) {
        var _this3 = this;

        _get(hass_router_page_getPrototypeOf(HassRouterPage.prototype), "firstUpdated", this).call(this, changedProps);

        var options = this.routerOptions;

        if (!options) {
          return;
        }

        if (options.preloadAll) {
          Object.values(options.routes).forEach(function (route) {
            return hass_router_page_typeof(route) === "object" && route.load && route.load();
          });
        }

        if (options.initialLoad) {
          setTimeout(function () {
            if (!_this3._initialLoadDone) {
              _this3.appendChild(_this3.createLoadingScreen());
            }
          }, LOADING_SCREEN_THRESHOLD);
          options.initialLoad().then(function () {
            _this3._initialLoadDone = true;

            _this3.requestUpdate("route");
          });
        }
      }
    }, {
      kind: "method",
      key: "createLoadingScreen",
      value: function createLoadingScreen() {
        return document.createElement("hass-loading-screen");
      }
      /**
       * Rebuild the current panel.
       *
       * Promise will resolve when rebuilding is done and DOM updated.
       */

    }, {
      kind: "method",
      key: "rebuild",
      value: function () {
        var _rebuild = _asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee() {
          var oldRoute;
          return regeneratorRuntime.wrap(function _callee$(_context) {
            while (1) {
              switch (_context.prev = _context.next) {
                case 0:
                  oldRoute = this.route;

                  if (!(oldRoute === undefined)) {
                    _context.next = 3;
                    break;
                  }

                  return _context.abrupt("return");

                case 3:
                  this.route = undefined;
                  _context.next = 6;
                  return this.updateComplete;

                case 6:
                  // Make sure that the parent didn't override this in the meanwhile.
                  if (this.route === undefined) {
                    this.route = oldRoute;
                  }

                case 7:
                case "end":
                  return _context.stop();
              }
            }
          }, _callee, this);
        }));

        function rebuild() {
          return _rebuild.apply(this, arguments);
        }

        return rebuild;
      }()
      /**
       * Promise that resolves when the page has rendered.
       */

    }, {
      kind: "get",
      key: "pageRendered",
      value: function pageRendered() {
        var _this4 = this;

        return this.updateComplete.then(function () {
          return _this4._currentLoadProm;
        });
      }
    }, {
      kind: "method",
      key: "createElement",
      value: function createElement(tag) {
        return document.createElement(tag);
      }
    }, {
      kind: "method",
      key: "updatePageEl",
      value: function updatePageEl(_pageEl, _changedProps) {// default we do nothing
      }
    }, {
      kind: "get",
      key: "routeTail",
      value: function routeTail() {
        return this._computeTail(this.route);
      }
    }, {
      kind: "method",
      key: "_createPanel",
      value: function _createPanel(routerOptions, page, routeOptions) {
        if (this.lastChild) {
          this.removeChild(this.lastChild);
        }

        var panelEl = this._cache[page] || this.createElement(routeOptions.tag);
        this.updatePageEl(panelEl);
        this.appendChild(panelEl);

        if (routerOptions.cacheAll || routeOptions.cache) {
          this._cache[page] = panelEl;
        }
      }
    }]
  };
}, lit_element["b" /* UpdatingElement */]);

/***/ }),

/***/ 11:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "a", function() { return derivedStyles; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "b", function() { return haStyle; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "c", function() { return haStyleDialog; });
/* harmony import */ var lit_element__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(5);
function _templateObject2() {
  var data = _taggedTemplateLiteral(["\n  /* prevent clipping of positioned elements */\n  paper-dialog-scrollable {\n    --paper-dialog-scrollable: {\n      -webkit-overflow-scrolling: auto;\n    }\n  }\n\n  /* force smooth scrolling for iOS 10 */\n  paper-dialog-scrollable.can-scroll {\n    --paper-dialog-scrollable: {\n      -webkit-overflow-scrolling: touch;\n    }\n  }\n\n  .paper-dialog-buttons {\n    align-items: flex-end;\n    padding: 8px;\n  }\n\n  @media all and (min-width: 450px) {\n    ha-paper-dialog {\n      min-width: 400px;\n    }\n  }\n\n  @media all and (max-width: 450px), all and (max-height: 500px) {\n    paper-dialog,\n    ha-paper-dialog {\n      margin: 0;\n      width: 100% !important;\n      max-height: calc(100% - 64px);\n\n      position: fixed !important;\n      bottom: 0px;\n      left: 0px;\n      right: 0px;\n      overflow: scroll;\n      border-bottom-left-radius: 0px;\n      border-bottom-right-radius: 0px;\n    }\n  }\n\n  /* mwc-dialog (ha-dialog) styles */\n  ha-dialog {\n    --mdc-dialog-min-width: 400px;\n    --mdc-dialog-max-width: 600px;\n    --mdc-dialog-heading-ink-color: var(--primary-text-color);\n    --mdc-dialog-content-ink-color: var(--primary-text-color);\n    --justify-action-buttons: space-between;\n  }\n\n  ha-dialog .form {\n    padding-bottom: 24px;\n    color: var(--primary-text-color);\n  }\n\n  /* make dialog fullscreen on small screens */\n  @media all and (max-width: 450px), all and (max-height: 500px) {\n    ha-dialog {\n      --mdc-dialog-min-width: 100vw;\n      --mdc-dialog-max-height: 100vh;\n      --mdc-dialog-shape-radius: 0px;\n      --vertial-align-dialog: flex-end;\n    }\n  }\n  mwc-button.warning {\n    --mdc-theme-primary: var(--google-red-500);\n  }\n  .error {\n    color: var(--google-red-500);\n  }\n"]);

  _templateObject2 = function _templateObject2() {
    return data;
  };

  return data;
}

function _templateObject() {
  var data = _taggedTemplateLiteral(["\n  :host {\n    font-family: var(--paper-font-body1_-_font-family);\n    -webkit-font-smoothing: var(--paper-font-body1_-_-webkit-font-smoothing);\n    font-size: var(--paper-font-body1_-_font-size);\n    font-weight: var(--paper-font-body1_-_font-weight);\n    line-height: var(--paper-font-body1_-_line-height);\n  }\n\n  app-header-layout,\n  ha-app-layout {\n    background-color: var(--primary-background-color);\n  }\n\n  app-header,\n  app-toolbar {\n    background-color: var(--app-header-background-color);\n    font-weight: 400;\n    color: var(--app-header-text-color, white);\n  }\n\n  app-toolbar ha-menu-button + [main-title],\n  app-toolbar ha-icon-button-arrow-prev + [main-title],\n  app-toolbar ha-icon-button + [main-title] {\n    margin-left: 24px;\n  }\n\n  h1 {\n    font-family: var(--paper-font-title_-_font-family);\n    -webkit-font-smoothing: var(--paper-font-title_-_-webkit-font-smoothing);\n    white-space: var(--paper-font-title_-_white-space);\n    overflow: var(--paper-font-title_-_overflow);\n    text-overflow: var(--paper-font-title_-_text-overflow);\n    font-size: var(--paper-font-title_-_font-size);\n    font-weight: var(--paper-font-title_-_font-weight);\n    line-height: var(--paper-font-title_-_line-height);\n  }\n\n  h2 {\n    font-family: var(--paper-font-subhead_-_font-family);\n    -webkit-font-smoothing: var(--paper-font-subhead_-_-webkit-font-smoothing);\n    white-space: var(--paper-font-subhead_-_white-space);\n    overflow: var(--paper-font-subhead_-_overflow);\n    text-overflow: var(--paper-font-subhead_-_text-overflow);\n    font-size: var(--paper-font-subhead_-_font-size);\n    font-weight: var(--paper-font-subhead_-_font-weight);\n    line-height: var(--paper-font-subhead_-_line-height);\n  }\n\n  .secondary {\n    color: var(--secondary-text-color);\n  }\n\n  .error {\n    color: var(--google-red-500);\n  }\n\n  .warning {\n    color: var(--google-red-500);\n  }\n\n  mwc-button.warning {\n    --mdc-theme-primary: var(--google-red-500);\n  }\n\n  button.link {\n    background: none;\n    color: inherit;\n    border: none;\n    padding: 0;\n    font: inherit;\n    text-align: left;\n    text-decoration: underline;\n    cursor: pointer;\n  }\n\n  .card-actions a {\n    text-decoration: none;\n  }\n\n  .card-actions .warning {\n    --mdc-theme-primary: var(--google-red-500);\n  }\n\n  .layout.horizontal,\n  .layout.vertical {\n    display: flex;\n  }\n  .layout.inline {\n    display: inline-flex;\n  }\n  .layout.horizontal {\n    flex-direction: row;\n  }\n  .layout.vertical {\n    flex-direction: column;\n  }\n  .layout.wrap {\n    flex-wrap: wrap;\n  }\n  .layout.no-wrap {\n    flex-wrap: nowrap;\n  }\n  .layout.center,\n  .layout.center-center {\n    align-items: center;\n  }\n  .layout.bottom {\n    align-items: flex-end;\n  }\n  .layout.center-justified,\n  .layout.center-center {\n    justify-content: center;\n  }\n  .flex {\n    flex: 1;\n    flex-basis: 0.000000001px;\n  }\n  .flex-auto {\n    flex: 1 1 auto;\n  }\n  .flex-none {\n    flex: none;\n  }\n  .layout.justified {\n    justify-content: space-between;\n  }\n"]);

  _templateObject = function _templateObject() {
    return data;
  };

  return data;
}

function _taggedTemplateLiteral(strings, raw) { if (!raw) { raw = strings.slice(0); } return Object.freeze(Object.defineProperties(strings, { raw: { value: Object.freeze(raw) } })); }


var derivedStyles = {
  "paper-spinner-color": "var(--primary-color)",
  "error-state-color": "var(--error-color)",
  "state-icon-unavailable-color": "var(--disabled-text-color)",
  "sidebar-text-color": "var(--primary-text-color)",
  "sidebar-background-color": "var(--card-background-color)",
  "sidebar-selected-text-color": "var(--primary-color)",
  "sidebar-selected-icon-color": "var(--primary-color)",
  "sidebar-icon-color": "rgba(var(--rgb-primary-text-color), 0.6)",
  "switch-checked-color": "var(--primary-color)",
  "switch-checked-button-color": "var(--switch-checked-color, var(--primary-background-color))",
  "switch-checked-track-color": "var(--switch-checked-color, #000000)",
  "switch-unchecked-button-color": "var(--switch-unchecked-color, var(--primary-background-color))",
  "switch-unchecked-track-color": "var(--switch-unchecked-color, #000000)",
  "slider-color": "var(--primary-color)",
  "slider-secondary-color": "var(--light-primary-color)",
  "slider-bar-color": "var(--disabled-text-color)",
  "label-badge-grey": "var(--paper-grey-500)",
  "label-badge-background-color": "var(--card-background-color)",
  "label-badge-text-color": "rgba(var(--rgb-primary-text-color), 0.8)",
  "paper-card-background-color": "var(--card-background-color)",
  "paper-listbox-background-color": "var(--card-background-color)",
  "paper-item-icon-color": "var(--state-icon-color)",
  "paper-item-icon-active-color": "var(--state-icon-active-color)",
  "table-row-background-color": "var(--primary-background-color)",
  "table-row-alternative-background-color": "var(--secondary-background-color)",
  "paper-slider-knob-color": "var(--slider-color)",
  "paper-slider-knob-start-color": "var(--slider-color)",
  "paper-slider-pin-color": "var(--slider-color)",
  "paper-slider-active-color": "var(--slider-color)",
  "paper-slider-secondary-color": "var(--slider-secondary-color)",
  "paper-slider-container-color": "var(--slider-bar-color)",
  "data-table-background-color": "var(--card-background-color)",
  "mdc-theme-primary": "var(--primary-color)",
  "mdc-theme-secondary": "var(--accent-color)",
  "mdc-theme-background": "var(--primary-background-color)",
  "mdc-theme-surface": "var(--card-background-color)",
  "mdc-theme-on-primary": "var(--text-primary-color)",
  "mdc-theme-on-secondary": "var(--text-primary-color)",
  "mdc-theme-on-surface": "var(--primary-text-color)",
  "mdc-theme-text-primary-on-background": "var(--primary-text-color)",
  "app-header-text-color": "var(--text-primary-color)",
  "app-header-background-color": "var(--primary-color)",
  "material-body-text-color": "var(--primary-text-color)",
  "material-background-color": "var(--card-background-color)",
  "material-secondary-background-color": "var(--secondary-background-color)"
};
var haStyle = Object(lit_element__WEBPACK_IMPORTED_MODULE_0__[/* css */ "c"])(_templateObject());
var haStyleDialog = Object(lit_element__WEBPACK_IMPORTED_MODULE_0__[/* css */ "c"])(_templateObject2());

/***/ }),

/***/ 113:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony import */ var lit_element__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(5);
/* harmony import */ var lit_html_directives_class_map__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(26);
/* harmony import */ var _components_ha_menu_button__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(99);
/* harmony import */ var _components_ha_icon_button_arrow_prev__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(87);
function _typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { _typeof = function _typeof(obj) { return typeof obj; }; } else { _typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return _typeof(obj); }

function _templateObject2() {
  var data = _taggedTemplateLiteral(["\n      :host {\n        display: block;\n        height: 100%;\n        background-color: var(--primary-background-color);\n      }\n\n      .toolbar {\n        display: flex;\n        align-items: center;\n        font-size: 20px;\n        height: 65px;\n        padding: 0 16px;\n        pointer-events: none;\n        background-color: var(--app-header-background-color);\n        font-weight: 400;\n        color: var(--app-header-text-color, white);\n        border-bottom: var(--app-header-border-bottom, none);\n        box-sizing: border-box;\n      }\n\n      ha-menu-button,\n      ha-icon-button-arrow-prev,\n      ::slotted([slot=\"toolbar-icon\"]) {\n        pointer-events: auto;\n      }\n\n      ha-icon-button-arrow-prev.hidden {\n        visibility: hidden;\n      }\n\n      [main-title] {\n        margin: 0 0 0 24px;\n        line-height: 20px;\n        flex-grow: 1;\n      }\n\n      .content {\n        position: relative;\n        width: 100%;\n        height: calc(100% - 65px);\n        overflow-y: auto;\n        overflow: auto;\n        -webkit-overflow-scrolling: touch;\n      }\n    "]);

  _templateObject2 = function _templateObject2() {
    return data;
  };

  return data;
}

function _templateObject() {
  var data = _taggedTemplateLiteral(["\n      <div class=\"toolbar\">\n        <ha-icon-button-arrow-prev\n          aria-label=\"Back\"\n          @click=", "\n          class=", "\n        ></ha-icon-button-arrow-prev>\n\n        <div main-title>", "</div>\n        <slot name=\"toolbar-icon\"></slot>\n      </div>\n      <div class=\"content\"><slot></slot></div>\n    "]);

  _templateObject = function _templateObject() {
    return data;
  };

  return data;
}

function _taggedTemplateLiteral(strings, raw) { if (!raw) { raw = strings.slice(0); } return Object.freeze(Object.defineProperties(strings, { raw: { value: Object.freeze(raw) } })); }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) _setPrototypeOf(subClass, superClass); }

function _setPrototypeOf(o, p) { _setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return _setPrototypeOf(o, p); }

function _createSuper(Derived) { return function () { var Super = _getPrototypeOf(Derived), result; if (_isNativeReflectConstruct()) { var NewTarget = _getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return _possibleConstructorReturn(this, result); }; }

function _possibleConstructorReturn(self, call) { if (call && (_typeof(call) === "object" || typeof call === "function")) { return call; } return _assertThisInitialized(self); }

function _assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function _isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Date.prototype.toString.call(Reflect.construct(Date, [], function () {})); return true; } catch (e) { return false; } }

function _getPrototypeOf(o) { _getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return _getPrototypeOf(o); }

function _decorate(decorators, factory, superClass, mixins) { var api = _getDecoratorsApi(); if (mixins) { for (var i = 0; i < mixins.length; i++) { api = mixins[i](api); } } var r = factory(function initialize(O) { api.initializeInstanceElements(O, decorated.elements); }, superClass); var decorated = api.decorateClass(_coalesceClassElements(r.d.map(_createElementDescriptor)), decorators); api.initializeClassElements(r.F, decorated.elements); return api.runClassFinishers(r.F, decorated.finishers); }

function _getDecoratorsApi() { _getDecoratorsApi = function _getDecoratorsApi() { return api; }; var api = { elementsDefinitionOrder: [["method"], ["field"]], initializeInstanceElements: function initializeInstanceElements(O, elements) { ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { if (element.kind === kind && element.placement === "own") { this.defineClassElement(O, element); } }, this); }, this); }, initializeClassElements: function initializeClassElements(F, elements) { var proto = F.prototype; ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { var placement = element.placement; if (element.kind === kind && (placement === "static" || placement === "prototype")) { var receiver = placement === "static" ? F : proto; this.defineClassElement(receiver, element); } }, this); }, this); }, defineClassElement: function defineClassElement(receiver, element) { var descriptor = element.descriptor; if (element.kind === "field") { var initializer = element.initializer; descriptor = { enumerable: descriptor.enumerable, writable: descriptor.writable, configurable: descriptor.configurable, value: initializer === void 0 ? void 0 : initializer.call(receiver) }; } Object.defineProperty(receiver, element.key, descriptor); }, decorateClass: function decorateClass(elements, decorators) { var newElements = []; var finishers = []; var placements = { "static": [], prototype: [], own: [] }; elements.forEach(function (element) { this.addElementPlacement(element, placements); }, this); elements.forEach(function (element) { if (!_hasDecorators(element)) return newElements.push(element); var elementFinishersExtras = this.decorateElement(element, placements); newElements.push(elementFinishersExtras.element); newElements.push.apply(newElements, elementFinishersExtras.extras); finishers.push.apply(finishers, elementFinishersExtras.finishers); }, this); if (!decorators) { return { elements: newElements, finishers: finishers }; } var result = this.decorateConstructor(newElements, decorators); finishers.push.apply(finishers, result.finishers); result.finishers = finishers; return result; }, addElementPlacement: function addElementPlacement(element, placements, silent) { var keys = placements[element.placement]; if (!silent && keys.indexOf(element.key) !== -1) { throw new TypeError("Duplicated element (" + element.key + ")"); } keys.push(element.key); }, decorateElement: function decorateElement(element, placements) { var extras = []; var finishers = []; for (var decorators = element.decorators, i = decorators.length - 1; i >= 0; i--) { var keys = placements[element.placement]; keys.splice(keys.indexOf(element.key), 1); var elementObject = this.fromElementDescriptor(element); var elementFinisherExtras = this.toElementFinisherExtras((0, decorators[i])(elementObject) || elementObject); element = elementFinisherExtras.element; this.addElementPlacement(element, placements); if (elementFinisherExtras.finisher) { finishers.push(elementFinisherExtras.finisher); } var newExtras = elementFinisherExtras.extras; if (newExtras) { for (var j = 0; j < newExtras.length; j++) { this.addElementPlacement(newExtras[j], placements); } extras.push.apply(extras, newExtras); } } return { element: element, finishers: finishers, extras: extras }; }, decorateConstructor: function decorateConstructor(elements, decorators) { var finishers = []; for (var i = decorators.length - 1; i >= 0; i--) { var obj = this.fromClassDescriptor(elements); var elementsAndFinisher = this.toClassDescriptor((0, decorators[i])(obj) || obj); if (elementsAndFinisher.finisher !== undefined) { finishers.push(elementsAndFinisher.finisher); } if (elementsAndFinisher.elements !== undefined) { elements = elementsAndFinisher.elements; for (var j = 0; j < elements.length - 1; j++) { for (var k = j + 1; k < elements.length; k++) { if (elements[j].key === elements[k].key && elements[j].placement === elements[k].placement) { throw new TypeError("Duplicated element (" + elements[j].key + ")"); } } } } } return { elements: elements, finishers: finishers }; }, fromElementDescriptor: function fromElementDescriptor(element) { var obj = { kind: element.kind, key: element.key, placement: element.placement, descriptor: element.descriptor }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); if (element.kind === "field") obj.initializer = element.initializer; return obj; }, toElementDescriptors: function toElementDescriptors(elementObjects) { if (elementObjects === undefined) return; return _toArray(elementObjects).map(function (elementObject) { var element = this.toElementDescriptor(elementObject); this.disallowProperty(elementObject, "finisher", "An element descriptor"); this.disallowProperty(elementObject, "extras", "An element descriptor"); return element; }, this); }, toElementDescriptor: function toElementDescriptor(elementObject) { var kind = String(elementObject.kind); if (kind !== "method" && kind !== "field") { throw new TypeError('An element descriptor\'s .kind property must be either "method" or' + ' "field", but a decorator created an element descriptor with' + ' .kind "' + kind + '"'); } var key = _toPropertyKey(elementObject.key); var placement = String(elementObject.placement); if (placement !== "static" && placement !== "prototype" && placement !== "own") { throw new TypeError('An element descriptor\'s .placement property must be one of "static",' + ' "prototype" or "own", but a decorator created an element descriptor' + ' with .placement "' + placement + '"'); } var descriptor = elementObject.descriptor; this.disallowProperty(elementObject, "elements", "An element descriptor"); var element = { kind: kind, key: key, placement: placement, descriptor: Object.assign({}, descriptor) }; if (kind !== "field") { this.disallowProperty(elementObject, "initializer", "A method descriptor"); } else { this.disallowProperty(descriptor, "get", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "set", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "value", "The property descriptor of a field descriptor"); element.initializer = elementObject.initializer; } return element; }, toElementFinisherExtras: function toElementFinisherExtras(elementObject) { var element = this.toElementDescriptor(elementObject); var finisher = _optionalCallableProperty(elementObject, "finisher"); var extras = this.toElementDescriptors(elementObject.extras); return { element: element, finisher: finisher, extras: extras }; }, fromClassDescriptor: function fromClassDescriptor(elements) { var obj = { kind: "class", elements: elements.map(this.fromElementDescriptor, this) }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); return obj; }, toClassDescriptor: function toClassDescriptor(obj) { var kind = String(obj.kind); if (kind !== "class") { throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator' + ' created a class descriptor with .kind "' + kind + '"'); } this.disallowProperty(obj, "key", "A class descriptor"); this.disallowProperty(obj, "placement", "A class descriptor"); this.disallowProperty(obj, "descriptor", "A class descriptor"); this.disallowProperty(obj, "initializer", "A class descriptor"); this.disallowProperty(obj, "extras", "A class descriptor"); var finisher = _optionalCallableProperty(obj, "finisher"); var elements = this.toElementDescriptors(obj.elements); return { elements: elements, finisher: finisher }; }, runClassFinishers: function runClassFinishers(constructor, finishers) { for (var i = 0; i < finishers.length; i++) { var newConstructor = (0, finishers[i])(constructor); if (newConstructor !== undefined) { if (typeof newConstructor !== "function") { throw new TypeError("Finishers must return a constructor."); } constructor = newConstructor; } } return constructor; }, disallowProperty: function disallowProperty(obj, name, objectType) { if (obj[name] !== undefined) { throw new TypeError(objectType + " can't have a ." + name + " property."); } } }; return api; }

function _createElementDescriptor(def) { var key = _toPropertyKey(def.key); var descriptor; if (def.kind === "method") { descriptor = { value: def.value, writable: true, configurable: true, enumerable: false }; } else if (def.kind === "get") { descriptor = { get: def.value, configurable: true, enumerable: false }; } else if (def.kind === "set") { descriptor = { set: def.value, configurable: true, enumerable: false }; } else if (def.kind === "field") { descriptor = { configurable: true, writable: true, enumerable: true }; } var element = { kind: def.kind === "field" ? "field" : "method", key: key, placement: def["static"] ? "static" : def.kind === "field" ? "own" : "prototype", descriptor: descriptor }; if (def.decorators) element.decorators = def.decorators; if (def.kind === "field") element.initializer = def.value; return element; }

function _coalesceGetterSetter(element, other) { if (element.descriptor.get !== undefined) { other.descriptor.get = element.descriptor.get; } else { other.descriptor.set = element.descriptor.set; } }

function _coalesceClassElements(elements) { var newElements = []; var isSameElement = function isSameElement(other) { return other.kind === "method" && other.key === element.key && other.placement === element.placement; }; for (var i = 0; i < elements.length; i++) { var element = elements[i]; var other; if (element.kind === "method" && (other = newElements.find(isSameElement))) { if (_isDataDescriptor(element.descriptor) || _isDataDescriptor(other.descriptor)) { if (_hasDecorators(element) || _hasDecorators(other)) { throw new ReferenceError("Duplicated methods (" + element.key + ") can't be decorated."); } other.descriptor = element.descriptor; } else { if (_hasDecorators(element)) { if (_hasDecorators(other)) { throw new ReferenceError("Decorators can't be placed on different accessors with for " + "the same property (" + element.key + ")."); } other.decorators = element.decorators; } _coalesceGetterSetter(element, other); } } else { newElements.push(element); } } return newElements; }

function _hasDecorators(element) { return element.decorators && element.decorators.length; }

function _isDataDescriptor(desc) { return desc !== undefined && !(desc.value === undefined && desc.writable === undefined); }

function _optionalCallableProperty(obj, name) { var value = obj[name]; if (value !== undefined && typeof value !== "function") { throw new TypeError("Expected '" + name + "' to be a function"); } return value; }

function _toPropertyKey(arg) { var key = _toPrimitive(arg, "string"); return _typeof(key) === "symbol" ? key : String(key); }

function _toPrimitive(input, hint) { if (_typeof(input) !== "object" || input === null) return input; var prim = input[Symbol.toPrimitive]; if (prim !== undefined) { var res = prim.call(input, hint || "default"); if (_typeof(res) !== "object") return res; throw new TypeError("@@toPrimitive must return a primitive value."); } return (hint === "string" ? String : Number)(input); }

function _toArray(arr) { return _arrayWithHoles(arr) || _iterableToArray(arr) || _unsupportedIterableToArray(arr) || _nonIterableRest(); }

function _nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function _unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return _arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(n); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return _arrayLikeToArray(o, minLen); }

function _arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function _iterableToArray(iter) { if (typeof Symbol !== "undefined" && Symbol.iterator in Object(iter)) return Array.from(iter); }

function _arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }






var HassSubpage = _decorate([Object(lit_element__WEBPACK_IMPORTED_MODULE_0__[/* customElement */ "d"])("hass-subpage")], function (_initialize, _LitElement) {
  var HassSubpage = /*#__PURE__*/function (_LitElement2) {
    _inherits(HassSubpage, _LitElement2);

    var _super = _createSuper(HassSubpage);

    function HassSubpage() {
      var _this;

      _classCallCheck(this, HassSubpage);

      for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
        args[_key] = arguments[_key];
      }

      _this = _super.call.apply(_super, [this].concat(args));

      _initialize(_assertThisInitialized(_this));

      return _this;
    }

    return HassSubpage;
  }(_LitElement);

  return {
    F: HassSubpage,
    d: [{
      kind: "field",
      decorators: [Object(lit_element__WEBPACK_IMPORTED_MODULE_0__[/* property */ "f"])()],
      key: "header",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element__WEBPACK_IMPORTED_MODULE_0__[/* property */ "f"])({
        type: Boolean
      })],
      key: "showBackButton",
      value: function value() {
        return true;
      }
    }, {
      kind: "field",
      decorators: [Object(lit_element__WEBPACK_IMPORTED_MODULE_0__[/* property */ "f"])({
        type: Boolean
      })],
      key: "hassio",
      value: function value() {
        return false;
      }
    }, {
      kind: "method",
      key: "render",
      value: function render() {
        return Object(lit_element__WEBPACK_IMPORTED_MODULE_0__[/* html */ "e"])(_templateObject(), this._backTapped, Object(lit_html_directives_class_map__WEBPACK_IMPORTED_MODULE_1__[/* classMap */ "a"])({
          hidden: !this.showBackButton
        }), this.header);
      }
    }, {
      kind: "method",
      key: "_backTapped",
      value: function _backTapped() {
        history.back();
      }
    }, {
      kind: "get",
      "static": true,
      key: "styles",
      value: function styles() {
        return Object(lit_element__WEBPACK_IMPORTED_MODULE_0__[/* css */ "c"])(_templateObject2());
      }
    }]
  };
}, lit_element__WEBPACK_IMPORTED_MODULE_0__[/* LitElement */ "a"]);

/***/ }),

/***/ 114:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony import */ var _polymer_app_layout_app_toolbar_app_toolbar__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(88);
/* harmony import */ var _polymer_paper_spinner_paper_spinner_lite__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(35);
/* harmony import */ var lit_element__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(5);
/* harmony import */ var _components_ha_menu_button__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(99);
/* harmony import */ var _components_ha_icon_button_arrow_prev__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(87);
/* harmony import */ var _resources_styles__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(11);
function _typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { _typeof = function _typeof(obj) { return typeof obj; }; } else { _typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return _typeof(obj); }

function _templateObject4() {
  var data = _taggedTemplateLiteral(["\n        :host {\n          display: block;\n          height: 100%;\n          background-color: var(--primary-background-color);\n        }\n        .content {\n          height: calc(100% - 64px);\n          display: flex;\n          align-items: center;\n          justify-content: center;\n        }\n      "]);

  _templateObject4 = function _templateObject4() {
    return data;
  };

  return data;
}

function _templateObject3() {
  var data = _taggedTemplateLiteral(["\n              <ha-icon-button-arrow-prev\n                @click=", "\n              ></ha-icon-button-arrow-prev>\n            "]);

  _templateObject3 = function _templateObject3() {
    return data;
  };

  return data;
}

function _templateObject2() {
  var data = _taggedTemplateLiteral(["\n              <ha-menu-button\n                .hass=", "\n                .narrow=", "\n              ></ha-menu-button>\n            "]);

  _templateObject2 = function _templateObject2() {
    return data;
  };

  return data;
}

function _templateObject() {
  var data = _taggedTemplateLiteral(["\n      <app-toolbar>\n        ", "\n      </app-toolbar>\n      <div class=\"content\">\n        <paper-spinner-lite active></paper-spinner-lite>\n      </div>\n    "]);

  _templateObject = function _templateObject() {
    return data;
  };

  return data;
}

function _taggedTemplateLiteral(strings, raw) { if (!raw) { raw = strings.slice(0); } return Object.freeze(Object.defineProperties(strings, { raw: { value: Object.freeze(raw) } })); }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) _setPrototypeOf(subClass, superClass); }

function _setPrototypeOf(o, p) { _setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return _setPrototypeOf(o, p); }

function _createSuper(Derived) { return function () { var Super = _getPrototypeOf(Derived), result; if (_isNativeReflectConstruct()) { var NewTarget = _getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return _possibleConstructorReturn(this, result); }; }

function _possibleConstructorReturn(self, call) { if (call && (_typeof(call) === "object" || typeof call === "function")) { return call; } return _assertThisInitialized(self); }

function _assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function _isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Date.prototype.toString.call(Reflect.construct(Date, [], function () {})); return true; } catch (e) { return false; } }

function _getPrototypeOf(o) { _getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return _getPrototypeOf(o); }

function _decorate(decorators, factory, superClass, mixins) { var api = _getDecoratorsApi(); if (mixins) { for (var i = 0; i < mixins.length; i++) { api = mixins[i](api); } } var r = factory(function initialize(O) { api.initializeInstanceElements(O, decorated.elements); }, superClass); var decorated = api.decorateClass(_coalesceClassElements(r.d.map(_createElementDescriptor)), decorators); api.initializeClassElements(r.F, decorated.elements); return api.runClassFinishers(r.F, decorated.finishers); }

function _getDecoratorsApi() { _getDecoratorsApi = function _getDecoratorsApi() { return api; }; var api = { elementsDefinitionOrder: [["method"], ["field"]], initializeInstanceElements: function initializeInstanceElements(O, elements) { ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { if (element.kind === kind && element.placement === "own") { this.defineClassElement(O, element); } }, this); }, this); }, initializeClassElements: function initializeClassElements(F, elements) { var proto = F.prototype; ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { var placement = element.placement; if (element.kind === kind && (placement === "static" || placement === "prototype")) { var receiver = placement === "static" ? F : proto; this.defineClassElement(receiver, element); } }, this); }, this); }, defineClassElement: function defineClassElement(receiver, element) { var descriptor = element.descriptor; if (element.kind === "field") { var initializer = element.initializer; descriptor = { enumerable: descriptor.enumerable, writable: descriptor.writable, configurable: descriptor.configurable, value: initializer === void 0 ? void 0 : initializer.call(receiver) }; } Object.defineProperty(receiver, element.key, descriptor); }, decorateClass: function decorateClass(elements, decorators) { var newElements = []; var finishers = []; var placements = { "static": [], prototype: [], own: [] }; elements.forEach(function (element) { this.addElementPlacement(element, placements); }, this); elements.forEach(function (element) { if (!_hasDecorators(element)) return newElements.push(element); var elementFinishersExtras = this.decorateElement(element, placements); newElements.push(elementFinishersExtras.element); newElements.push.apply(newElements, elementFinishersExtras.extras); finishers.push.apply(finishers, elementFinishersExtras.finishers); }, this); if (!decorators) { return { elements: newElements, finishers: finishers }; } var result = this.decorateConstructor(newElements, decorators); finishers.push.apply(finishers, result.finishers); result.finishers = finishers; return result; }, addElementPlacement: function addElementPlacement(element, placements, silent) { var keys = placements[element.placement]; if (!silent && keys.indexOf(element.key) !== -1) { throw new TypeError("Duplicated element (" + element.key + ")"); } keys.push(element.key); }, decorateElement: function decorateElement(element, placements) { var extras = []; var finishers = []; for (var decorators = element.decorators, i = decorators.length - 1; i >= 0; i--) { var keys = placements[element.placement]; keys.splice(keys.indexOf(element.key), 1); var elementObject = this.fromElementDescriptor(element); var elementFinisherExtras = this.toElementFinisherExtras((0, decorators[i])(elementObject) || elementObject); element = elementFinisherExtras.element; this.addElementPlacement(element, placements); if (elementFinisherExtras.finisher) { finishers.push(elementFinisherExtras.finisher); } var newExtras = elementFinisherExtras.extras; if (newExtras) { for (var j = 0; j < newExtras.length; j++) { this.addElementPlacement(newExtras[j], placements); } extras.push.apply(extras, newExtras); } } return { element: element, finishers: finishers, extras: extras }; }, decorateConstructor: function decorateConstructor(elements, decorators) { var finishers = []; for (var i = decorators.length - 1; i >= 0; i--) { var obj = this.fromClassDescriptor(elements); var elementsAndFinisher = this.toClassDescriptor((0, decorators[i])(obj) || obj); if (elementsAndFinisher.finisher !== undefined) { finishers.push(elementsAndFinisher.finisher); } if (elementsAndFinisher.elements !== undefined) { elements = elementsAndFinisher.elements; for (var j = 0; j < elements.length - 1; j++) { for (var k = j + 1; k < elements.length; k++) { if (elements[j].key === elements[k].key && elements[j].placement === elements[k].placement) { throw new TypeError("Duplicated element (" + elements[j].key + ")"); } } } } } return { elements: elements, finishers: finishers }; }, fromElementDescriptor: function fromElementDescriptor(element) { var obj = { kind: element.kind, key: element.key, placement: element.placement, descriptor: element.descriptor }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); if (element.kind === "field") obj.initializer = element.initializer; return obj; }, toElementDescriptors: function toElementDescriptors(elementObjects) { if (elementObjects === undefined) return; return _toArray(elementObjects).map(function (elementObject) { var element = this.toElementDescriptor(elementObject); this.disallowProperty(elementObject, "finisher", "An element descriptor"); this.disallowProperty(elementObject, "extras", "An element descriptor"); return element; }, this); }, toElementDescriptor: function toElementDescriptor(elementObject) { var kind = String(elementObject.kind); if (kind !== "method" && kind !== "field") { throw new TypeError('An element descriptor\'s .kind property must be either "method" or' + ' "field", but a decorator created an element descriptor with' + ' .kind "' + kind + '"'); } var key = _toPropertyKey(elementObject.key); var placement = String(elementObject.placement); if (placement !== "static" && placement !== "prototype" && placement !== "own") { throw new TypeError('An element descriptor\'s .placement property must be one of "static",' + ' "prototype" or "own", but a decorator created an element descriptor' + ' with .placement "' + placement + '"'); } var descriptor = elementObject.descriptor; this.disallowProperty(elementObject, "elements", "An element descriptor"); var element = { kind: kind, key: key, placement: placement, descriptor: Object.assign({}, descriptor) }; if (kind !== "field") { this.disallowProperty(elementObject, "initializer", "A method descriptor"); } else { this.disallowProperty(descriptor, "get", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "set", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "value", "The property descriptor of a field descriptor"); element.initializer = elementObject.initializer; } return element; }, toElementFinisherExtras: function toElementFinisherExtras(elementObject) { var element = this.toElementDescriptor(elementObject); var finisher = _optionalCallableProperty(elementObject, "finisher"); var extras = this.toElementDescriptors(elementObject.extras); return { element: element, finisher: finisher, extras: extras }; }, fromClassDescriptor: function fromClassDescriptor(elements) { var obj = { kind: "class", elements: elements.map(this.fromElementDescriptor, this) }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); return obj; }, toClassDescriptor: function toClassDescriptor(obj) { var kind = String(obj.kind); if (kind !== "class") { throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator' + ' created a class descriptor with .kind "' + kind + '"'); } this.disallowProperty(obj, "key", "A class descriptor"); this.disallowProperty(obj, "placement", "A class descriptor"); this.disallowProperty(obj, "descriptor", "A class descriptor"); this.disallowProperty(obj, "initializer", "A class descriptor"); this.disallowProperty(obj, "extras", "A class descriptor"); var finisher = _optionalCallableProperty(obj, "finisher"); var elements = this.toElementDescriptors(obj.elements); return { elements: elements, finisher: finisher }; }, runClassFinishers: function runClassFinishers(constructor, finishers) { for (var i = 0; i < finishers.length; i++) { var newConstructor = (0, finishers[i])(constructor); if (newConstructor !== undefined) { if (typeof newConstructor !== "function") { throw new TypeError("Finishers must return a constructor."); } constructor = newConstructor; } } return constructor; }, disallowProperty: function disallowProperty(obj, name, objectType) { if (obj[name] !== undefined) { throw new TypeError(objectType + " can't have a ." + name + " property."); } } }; return api; }

function _createElementDescriptor(def) { var key = _toPropertyKey(def.key); var descriptor; if (def.kind === "method") { descriptor = { value: def.value, writable: true, configurable: true, enumerable: false }; } else if (def.kind === "get") { descriptor = { get: def.value, configurable: true, enumerable: false }; } else if (def.kind === "set") { descriptor = { set: def.value, configurable: true, enumerable: false }; } else if (def.kind === "field") { descriptor = { configurable: true, writable: true, enumerable: true }; } var element = { kind: def.kind === "field" ? "field" : "method", key: key, placement: def["static"] ? "static" : def.kind === "field" ? "own" : "prototype", descriptor: descriptor }; if (def.decorators) element.decorators = def.decorators; if (def.kind === "field") element.initializer = def.value; return element; }

function _coalesceGetterSetter(element, other) { if (element.descriptor.get !== undefined) { other.descriptor.get = element.descriptor.get; } else { other.descriptor.set = element.descriptor.set; } }

function _coalesceClassElements(elements) { var newElements = []; var isSameElement = function isSameElement(other) { return other.kind === "method" && other.key === element.key && other.placement === element.placement; }; for (var i = 0; i < elements.length; i++) { var element = elements[i]; var other; if (element.kind === "method" && (other = newElements.find(isSameElement))) { if (_isDataDescriptor(element.descriptor) || _isDataDescriptor(other.descriptor)) { if (_hasDecorators(element) || _hasDecorators(other)) { throw new ReferenceError("Duplicated methods (" + element.key + ") can't be decorated."); } other.descriptor = element.descriptor; } else { if (_hasDecorators(element)) { if (_hasDecorators(other)) { throw new ReferenceError("Decorators can't be placed on different accessors with for " + "the same property (" + element.key + ")."); } other.decorators = element.decorators; } _coalesceGetterSetter(element, other); } } else { newElements.push(element); } } return newElements; }

function _hasDecorators(element) { return element.decorators && element.decorators.length; }

function _isDataDescriptor(desc) { return desc !== undefined && !(desc.value === undefined && desc.writable === undefined); }

function _optionalCallableProperty(obj, name) { var value = obj[name]; if (value !== undefined && typeof value !== "function") { throw new TypeError("Expected '" + name + "' to be a function"); } return value; }

function _toPropertyKey(arg) { var key = _toPrimitive(arg, "string"); return _typeof(key) === "symbol" ? key : String(key); }

function _toPrimitive(input, hint) { if (_typeof(input) !== "object" || input === null) return input; var prim = input[Symbol.toPrimitive]; if (prim !== undefined) { var res = prim.call(input, hint || "default"); if (_typeof(res) !== "object") return res; throw new TypeError("@@toPrimitive must return a primitive value."); } return (hint === "string" ? String : Number)(input); }

function _toArray(arr) { return _arrayWithHoles(arr) || _iterableToArray(arr) || _unsupportedIterableToArray(arr) || _nonIterableRest(); }

function _nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function _unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return _arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(n); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return _arrayLikeToArray(o, minLen); }

function _arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function _iterableToArray(iter) { if (typeof Symbol !== "undefined" && Symbol.iterator in Object(iter)) return Array.from(iter); }

function _arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }








var HassLoadingScreen = _decorate([Object(lit_element__WEBPACK_IMPORTED_MODULE_2__[/* customElement */ "d"])("hass-loading-screen")], function (_initialize, _LitElement) {
  var HassLoadingScreen = /*#__PURE__*/function (_LitElement2) {
    _inherits(HassLoadingScreen, _LitElement2);

    var _super = _createSuper(HassLoadingScreen);

    function HassLoadingScreen() {
      var _this;

      _classCallCheck(this, HassLoadingScreen);

      for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
        args[_key] = arguments[_key];
      }

      _this = _super.call.apply(_super, [this].concat(args));

      _initialize(_assertThisInitialized(_this));

      return _this;
    }

    return HassLoadingScreen;
  }(_LitElement);

  return {
    F: HassLoadingScreen,
    d: [{
      kind: "field",
      decorators: [Object(lit_element__WEBPACK_IMPORTED_MODULE_2__[/* property */ "f"])({
        type: Boolean
      })],
      key: "rootnav",
      value: function value() {
        return false;
      }
    }, {
      kind: "field",
      decorators: [Object(lit_element__WEBPACK_IMPORTED_MODULE_2__[/* property */ "f"])()],
      key: "hass",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element__WEBPACK_IMPORTED_MODULE_2__[/* property */ "f"])()],
      key: "narrow",
      value: void 0
    }, {
      kind: "method",
      key: "render",
      value: function render() {
        return Object(lit_element__WEBPACK_IMPORTED_MODULE_2__[/* html */ "e"])(_templateObject(), this.rootnav ? Object(lit_element__WEBPACK_IMPORTED_MODULE_2__[/* html */ "e"])(_templateObject2(), this.hass, this.narrow) : Object(lit_element__WEBPACK_IMPORTED_MODULE_2__[/* html */ "e"])(_templateObject3(), this._handleBack));
      }
    }, {
      kind: "method",
      key: "_handleBack",
      value: function _handleBack() {
        history.back();
      }
    }, {
      kind: "get",
      "static": true,
      key: "styles",
      value: function styles() {
        return [_resources_styles__WEBPACK_IMPORTED_MODULE_5__[/* haStyle */ "b"], Object(lit_element__WEBPACK_IMPORTED_MODULE_2__[/* css */ "c"])(_templateObject4())];
      }
    }]
  };
}, lit_element__WEBPACK_IMPORTED_MODULE_2__[/* LitElement */ "a"]);

/***/ }),

/***/ 117:
/***/ (function(module, exports) {

/* empty file that we alias some files to that we don't want to include */

/***/ }),

/***/ 12:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "a", function() { return fireEvent; });
// Polymer legacy event helpers used courtesy of the Polymer project.
//
// Copyright (c) 2017 The Polymer Authors. All rights reserved.
//
// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions are
// met:
//
//    * Redistributions of source code must retain the above copyright
// notice, this list of conditions and the following disclaimer.
//    * Redistributions in binary form must reproduce the above
// copyright notice, this list of conditions and the following disclaimer
// in the documentation and/or other materials provided with the
// distribution.
//    * Neither the name of Google Inc. nor the names of its
// contributors may be used to endorse or promote products derived from
// this software without specific prior written permission.
//
// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
// "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
// LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
// A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
// OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
// SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
// LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
// DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
// THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
// (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
// OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

/**
 * Dispatches a custom event with an optional detail value.
 *
 * @param {string} type Name of event type.
 * @param {*=} detail Detail value containing event-specific
 *   payload.
 * @param {{ bubbles: (boolean|undefined),
 *           cancelable: (boolean|undefined),
 *           composed: (boolean|undefined) }=}
 *  options Object specifying options.  These may include:
 *  `bubbles` (boolean, defaults to `true`),
 *  `cancelable` (boolean, defaults to false), and
 *  `node` on which to fire the event (HTMLElement, defaults to `this`).
 * @return {Event} The new event that was fired.
 */
var fireEvent = function fireEvent(node, type, detail, options) {
  options = options || {}; // @ts-ignore

  detail = detail === null || detail === undefined ? {} : detail;
  var event = new Event(type, {
    bubbles: options.bubbles === undefined ? true : options.bubbles,
    cancelable: Boolean(options.cancelable),
    composed: options.composed === undefined ? true : options.composed
  });
  event.detail = detail;
  node.dispatchEvent(event);
  return event;
};

/***/ }),

/***/ 121:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony import */ var _material_mwc_button__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(18);
/* harmony import */ var _polymer_paper_spinner_paper_spinner__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(118);
/* harmony import */ var _polymer_polymer_lib_utils_html_tag__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(7);
/* harmony import */ var _polymer_polymer_polymer_element__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(37);
function _typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { _typeof = function _typeof(obj) { return typeof obj; }; } else { _typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return _typeof(obj); }

function _templateObject() {
  var data = _taggedTemplateLiteral(["\n      <style>\n        .container {\n          position: relative;\n          display: inline-block;\n        }\n\n        mwc-button {\n          transition: all 1s;\n        }\n\n        .success mwc-button {\n          --mdc-theme-primary: white;\n          background-color: var(--google-green-500);\n          transition: none;\n        }\n\n        .error mwc-button {\n          --mdc-theme-primary: white;\n          background-color: var(--google-red-500);\n          transition: none;\n        }\n\n        .progress {\n          @apply --layout;\n          @apply --layout-center-center;\n          position: absolute;\n          top: 0;\n          left: 0;\n          right: 0;\n          bottom: 0;\n        }\n      </style>\n      <div class=\"container\" id=\"container\">\n        <mwc-button\n          id=\"button\"\n          disabled=\"[[computeDisabled(disabled, progress)]]\"\n          on-click=\"buttonTapped\"\n        >\n          <slot></slot>\n        </mwc-button>\n        <template is=\"dom-if\" if=\"[[progress]]\">\n          <div class=\"progress\"><paper-spinner active=\"\"></paper-spinner></div>\n        </template>\n      </div>\n    "]);

  _templateObject = function _templateObject() {
    return data;
  };

  return data;
}

function _taggedTemplateLiteral(strings, raw) { if (!raw) { raw = strings.slice(0); } return Object.freeze(Object.defineProperties(strings, { raw: { value: Object.freeze(raw) } })); }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } }

function _createClass(Constructor, protoProps, staticProps) { if (protoProps) _defineProperties(Constructor.prototype, protoProps); if (staticProps) _defineProperties(Constructor, staticProps); return Constructor; }

function _get(target, property, receiver) { if (typeof Reflect !== "undefined" && Reflect.get) { _get = Reflect.get; } else { _get = function _get(target, property, receiver) { var base = _superPropBase(target, property); if (!base) return; var desc = Object.getOwnPropertyDescriptor(base, property); if (desc.get) { return desc.get.call(receiver); } return desc.value; }; } return _get(target, property, receiver || target); }

function _superPropBase(object, property) { while (!Object.prototype.hasOwnProperty.call(object, property)) { object = _getPrototypeOf(object); if (object === null) break; } return object; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) _setPrototypeOf(subClass, superClass); }

function _setPrototypeOf(o, p) { _setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return _setPrototypeOf(o, p); }

function _createSuper(Derived) { return function () { var Super = _getPrototypeOf(Derived), result; if (_isNativeReflectConstruct()) { var NewTarget = _getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return _possibleConstructorReturn(this, result); }; }

function _possibleConstructorReturn(self, call) { if (call && (_typeof(call) === "object" || typeof call === "function")) { return call; } return _assertThisInitialized(self); }

function _assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function _isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Date.prototype.toString.call(Reflect.construct(Date, [], function () {})); return true; } catch (e) { return false; } }

function _getPrototypeOf(o) { _getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return _getPrototypeOf(o); }




/* eslint-plugin-disable lit */



var HaProgressButton = /*#__PURE__*/function (_PolymerElement) {
  _inherits(HaProgressButton, _PolymerElement);

  var _super = _createSuper(HaProgressButton);

  function HaProgressButton() {
    _classCallCheck(this, HaProgressButton);

    return _super.apply(this, arguments);
  }

  _createClass(HaProgressButton, [{
    key: "tempClass",
    value: function tempClass(className) {
      var classList = this.$.container.classList;
      classList.add(className);
      setTimeout(function () {
        classList.remove(className);
      }, 1000);
    }
  }, {
    key: "ready",
    value: function ready() {
      var _this = this;

      _get(_getPrototypeOf(HaProgressButton.prototype), "ready", this).call(this);

      this.addEventListener("click", function (ev) {
        return _this.buttonTapped(ev);
      });
    }
  }, {
    key: "buttonTapped",
    value: function buttonTapped(ev) {
      if (this.progress) ev.stopPropagation();
    }
  }, {
    key: "actionSuccess",
    value: function actionSuccess() {
      this.tempClass("success");
    }
  }, {
    key: "actionError",
    value: function actionError() {
      this.tempClass("error");
    }
  }, {
    key: "computeDisabled",
    value: function computeDisabled(disabled, progress) {
      return disabled || progress;
    }
  }], [{
    key: "template",
    get: function get() {
      return Object(_polymer_polymer_lib_utils_html_tag__WEBPACK_IMPORTED_MODULE_2__[/* html */ "a"])(_templateObject());
    }
  }, {
    key: "properties",
    get: function get() {
      return {
        hass: {
          type: Object
        },
        progress: {
          type: Boolean,
          value: false
        },
        disabled: {
          type: Boolean,
          value: false
        }
      };
    }
  }]);

  return HaProgressButton;
}(_polymer_polymer_polymer_element__WEBPACK_IMPORTED_MODULE_3__[/* PolymerElement */ "a"]);

customElements.define("ha-progress-button", HaProgressButton);

/***/ }),

/***/ 126:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "d", function() { return fetchHassioSnapshots; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "c", function() { return fetchHassioSnapshotInfo; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "e", function() { return reloadHassioSnapshots; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "a", function() { return createHassioFullSnapshot; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "b", function() { return createHassioPartialSnapshot; });
/* harmony import */ var _common__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(48);
function asyncGeneratorStep(gen, resolve, reject, _next, _throw, key, arg) { try { var info = gen[key](arg); var value = info.value; } catch (error) { reject(error); return; } if (info.done) { resolve(value); } else { Promise.resolve(value).then(_next, _throw); } }

function _asyncToGenerator(fn) { return function () { var self = this, args = arguments; return new Promise(function (resolve, reject) { var gen = fn.apply(self, args); function _next(value) { asyncGeneratorStep(gen, resolve, reject, _next, _throw, "next", value); } function _throw(err) { asyncGeneratorStep(gen, resolve, reject, _next, _throw, "throw", err); } _next(undefined); }); }; }


var fetchHassioSnapshots = /*#__PURE__*/function () {
  var _ref = _asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee(hass) {
    return regeneratorRuntime.wrap(function _callee$(_context) {
      while (1) {
        switch (_context.prev = _context.next) {
          case 0:
            _context.t0 = _common__WEBPACK_IMPORTED_MODULE_0__[/* hassioApiResultExtractor */ "a"];
            _context.next = 3;
            return hass.callApi("GET", "hassio/snapshots");

          case 3:
            _context.t1 = _context.sent;
            return _context.abrupt("return", (0, _context.t0)(_context.t1).snapshots);

          case 5:
          case "end":
            return _context.stop();
        }
      }
    }, _callee);
  }));

  return function fetchHassioSnapshots(_x) {
    return _ref.apply(this, arguments);
  };
}();
var fetchHassioSnapshotInfo = /*#__PURE__*/function () {
  var _ref2 = _asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee2(hass, snapshot) {
    return regeneratorRuntime.wrap(function _callee2$(_context2) {
      while (1) {
        switch (_context2.prev = _context2.next) {
          case 0:
            _context2.t0 = _common__WEBPACK_IMPORTED_MODULE_0__[/* hassioApiResultExtractor */ "a"];
            _context2.next = 3;
            return hass.callApi("GET", "hassio/snapshots/".concat(snapshot, "/info"));

          case 3:
            _context2.t1 = _context2.sent;
            return _context2.abrupt("return", (0, _context2.t0)(_context2.t1));

          case 5:
          case "end":
            return _context2.stop();
        }
      }
    }, _callee2);
  }));

  return function fetchHassioSnapshotInfo(_x2, _x3) {
    return _ref2.apply(this, arguments);
  };
}();
var reloadHassioSnapshots = /*#__PURE__*/function () {
  var _ref3 = _asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee3(hass) {
    return regeneratorRuntime.wrap(function _callee3$(_context3) {
      while (1) {
        switch (_context3.prev = _context3.next) {
          case 0:
            _context3.next = 2;
            return hass.callApi("POST", "hassio/snapshots/reload");

          case 2:
          case "end":
            return _context3.stop();
        }
      }
    }, _callee3);
  }));

  return function reloadHassioSnapshots(_x4) {
    return _ref3.apply(this, arguments);
  };
}();
var createHassioFullSnapshot = /*#__PURE__*/function () {
  var _ref4 = _asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee4(hass, data) {
    return regeneratorRuntime.wrap(function _callee4$(_context4) {
      while (1) {
        switch (_context4.prev = _context4.next) {
          case 0:
            _context4.next = 2;
            return hass.callApi("POST", "hassio/snapshots/new/full", data);

          case 2:
          case "end":
            return _context4.stop();
        }
      }
    }, _callee4);
  }));

  return function createHassioFullSnapshot(_x5, _x6) {
    return _ref4.apply(this, arguments);
  };
}();
var createHassioPartialSnapshot = /*#__PURE__*/function () {
  var _ref5 = _asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee5(hass, data) {
    return regeneratorRuntime.wrap(function _callee5$(_context5) {
      while (1) {
        switch (_context5.prev = _context5.next) {
          case 0:
            _context5.next = 2;
            return hass.callApi("POST", "hassio/snapshots/new/partial", data);

          case 2:
          case "end":
            return _context5.stop();
        }
      }
    }, _callee5);
  }));

  return function createHassioPartialSnapshot(_x7, _x8) {
    return _ref5.apply(this, arguments);
  };
}();

/***/ }),

/***/ 127:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "a", function() { return fetchHassioHardwareAudio; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "b", function() { return fetchHassioHardwareInfo; });
/* harmony import */ var _common__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(48);
function asyncGeneratorStep(gen, resolve, reject, _next, _throw, key, arg) { try { var info = gen[key](arg); var value = info.value; } catch (error) { reject(error); return; } if (info.done) { resolve(value); } else { Promise.resolve(value).then(_next, _throw); } }

function _asyncToGenerator(fn) { return function () { var self = this, args = arguments; return new Promise(function (resolve, reject) { var gen = fn.apply(self, args); function _next(value) { asyncGeneratorStep(gen, resolve, reject, _next, _throw, "next", value); } function _throw(err) { asyncGeneratorStep(gen, resolve, reject, _next, _throw, "throw", err); } _next(undefined); }); }; }


var fetchHassioHardwareAudio = /*#__PURE__*/function () {
  var _ref = _asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee(hass) {
    return regeneratorRuntime.wrap(function _callee$(_context) {
      while (1) {
        switch (_context.prev = _context.next) {
          case 0:
            _context.t0 = _common__WEBPACK_IMPORTED_MODULE_0__[/* hassioApiResultExtractor */ "a"];
            _context.next = 3;
            return hass.callApi("GET", "hassio/hardware/audio");

          case 3:
            _context.t1 = _context.sent;
            return _context.abrupt("return", (0, _context.t0)(_context.t1));

          case 5:
          case "end":
            return _context.stop();
        }
      }
    }, _callee);
  }));

  return function fetchHassioHardwareAudio(_x) {
    return _ref.apply(this, arguments);
  };
}();
var fetchHassioHardwareInfo = /*#__PURE__*/function () {
  var _ref2 = _asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee2(hass) {
    return regeneratorRuntime.wrap(function _callee2$(_context2) {
      while (1) {
        switch (_context2.prev = _context2.next) {
          case 0:
            _context2.t0 = _common__WEBPACK_IMPORTED_MODULE_0__[/* hassioApiResultExtractor */ "a"];
            _context2.next = 3;
            return hass.callApi("GET", "hassio/hardware/info");

          case 3:
            _context2.t1 = _context2.sent;
            return _context2.abrupt("return", (0, _context2.t0)(_context2.t1));

          case 5:
          case "end":
            return _context2.stop();
        }
      }
    }, _callee2);
  }));

  return function fetchHassioHardwareInfo(_x2) {
    return _ref2.apply(this, arguments);
  };
}();

/***/ }),

/***/ 128:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "a", function() { return showHassioMarkdownDialog; });
/* harmony import */ var _src_common_dom_fire_event__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(12);

var showHassioMarkdownDialog = function showHassioMarkdownDialog(element, dialogParams) {
  Object(_src_common_dom_fire_event__WEBPACK_IMPORTED_MODULE_0__[/* fireEvent */ "a"])(element, "show-dialog", {
    dialogTag: "dialog-hassio-markdown",
    dialogImport: function dialogImport() {
      return __webpack_require__.e(/* import() | dialog-hassio-markdown */ 3).then(__webpack_require__.bind(null, 180));
    },
    dialogParams: dialogParams
  });
};

/***/ }),

/***/ 13:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "a", function() { return hassioStyle; });
/* harmony import */ var lit_element__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(5);
function _templateObject() {
  var data = _taggedTemplateLiteral(["\n  .content {\n    margin: 8px;\n  }\n  h1,\n  .description,\n  .card-content {\n    color: var(--primary-text-color);\n  }\n  h1 {\n    font-size: 2em;\n    margin-bottom: 8px;\n    font-family: var(--paper-font-headline_-_font-family);\n    -webkit-font-smoothing: var(--paper-font-headline_-_-webkit-font-smoothing);\n    font-size: var(--paper-font-headline_-_font-size);\n    font-weight: var(--paper-font-headline_-_font-weight);\n    letter-spacing: var(--paper-font-headline_-_letter-spacing);\n    line-height: var(--paper-font-headline_-_line-height);\n    padding-left: 8px;\n  }\n  .description {\n    margin-top: 4px;\n    padding-left: 8px;\n  }\n  .card-group {\n    display: grid;\n    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));\n    grid-gap: 8px;\n  }\n  @media screen and (min-width: 640px) {\n    .card-group {\n      grid-template-columns: repeat(auto-fit, minmax(300px, 0.5fr));\n    }\n  }\n  @media screen and (min-width: 1020px) {\n    .card-group {\n      grid-template-columns: repeat(auto-fit, minmax(300px, 0.333fr));\n    }\n  }\n  @media screen and (min-width: 1300px) {\n    .card-group {\n      grid-template-columns: repeat(auto-fit, minmax(300px, 0.25fr));\n    }\n  }\n  ha-call-api-button {\n    font-weight: 500;\n    color: var(--primary-color);\n  }\n  .error {\n    color: var(--error-color);\n    margin-top: 16px;\n  }\n"]);

  _templateObject = function _templateObject() {
    return data;
  };

  return data;
}

function _taggedTemplateLiteral(strings, raw) { if (!raw) { raw = strings.slice(0); } return Object.freeze(Object.defineProperties(strings, { raw: { value: Object.freeze(raw) } })); }


var hassioStyle = Object(lit_element__WEBPACK_IMPORTED_MODULE_0__[/* css */ "c"])(_templateObject());

/***/ }),

/***/ 130:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony import */ var lit_element__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(5);
function _typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { _typeof = function _typeof(obj) { return typeof obj; }; } else { _typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return _typeof(obj); }

function _templateObject2() {
  var data = _taggedTemplateLiteral(["\n      pre {\n        overflow-x: auto;\n        white-space: pre-wrap;\n        overflow-wrap: break-word;\n      }\n      .bold {\n        font-weight: bold;\n      }\n      .italic {\n        font-style: italic;\n      }\n      .underline {\n        text-decoration: underline;\n      }\n      .strikethrough {\n        text-decoration: line-through;\n      }\n      .underline.strikethrough {\n        text-decoration: underline line-through;\n      }\n      .fg-red {\n        color: rgb(222, 56, 43);\n      }\n      .fg-green {\n        color: rgb(57, 181, 74);\n      }\n      .fg-yellow {\n        color: rgb(255, 199, 6);\n      }\n      .fg-blue {\n        color: rgb(0, 111, 184);\n      }\n      .fg-magenta {\n        color: rgb(118, 38, 113);\n      }\n      .fg-cyan {\n        color: rgb(44, 181, 233);\n      }\n      .fg-white {\n        color: rgb(204, 204, 204);\n      }\n      .bg-black {\n        background-color: rgb(0, 0, 0);\n      }\n      .bg-red {\n        background-color: rgb(222, 56, 43);\n      }\n      .bg-green {\n        background-color: rgb(57, 181, 74);\n      }\n      .bg-yellow {\n        background-color: rgb(255, 199, 6);\n      }\n      .bg-blue {\n        background-color: rgb(0, 111, 184);\n      }\n      .bg-magenta {\n        background-color: rgb(118, 38, 113);\n      }\n      .bg-cyan {\n        background-color: rgb(44, 181, 233);\n      }\n      .bg-white {\n        background-color: rgb(204, 204, 204);\n      }\n    "]);

  _templateObject2 = function _templateObject2() {
    return data;
  };

  return data;
}

function _templateObject() {
  var data = _taggedTemplateLiteral(["", ""]);

  _templateObject = function _templateObject() {
    return data;
  };

  return data;
}

function _taggedTemplateLiteral(strings, raw) { if (!raw) { raw = strings.slice(0); } return Object.freeze(Object.defineProperties(strings, { raw: { value: Object.freeze(raw) } })); }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) _setPrototypeOf(subClass, superClass); }

function _setPrototypeOf(o, p) { _setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return _setPrototypeOf(o, p); }

function _createSuper(Derived) { return function () { var Super = _getPrototypeOf(Derived), result; if (_isNativeReflectConstruct()) { var NewTarget = _getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return _possibleConstructorReturn(this, result); }; }

function _possibleConstructorReturn(self, call) { if (call && (_typeof(call) === "object" || typeof call === "function")) { return call; } return _assertThisInitialized(self); }

function _assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function _isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Date.prototype.toString.call(Reflect.construct(Date, [], function () {})); return true; } catch (e) { return false; } }

function _getPrototypeOf(o) { _getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return _getPrototypeOf(o); }

function _decorate(decorators, factory, superClass, mixins) { var api = _getDecoratorsApi(); if (mixins) { for (var i = 0; i < mixins.length; i++) { api = mixins[i](api); } } var r = factory(function initialize(O) { api.initializeInstanceElements(O, decorated.elements); }, superClass); var decorated = api.decorateClass(_coalesceClassElements(r.d.map(_createElementDescriptor)), decorators); api.initializeClassElements(r.F, decorated.elements); return api.runClassFinishers(r.F, decorated.finishers); }

function _getDecoratorsApi() { _getDecoratorsApi = function _getDecoratorsApi() { return api; }; var api = { elementsDefinitionOrder: [["method"], ["field"]], initializeInstanceElements: function initializeInstanceElements(O, elements) { ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { if (element.kind === kind && element.placement === "own") { this.defineClassElement(O, element); } }, this); }, this); }, initializeClassElements: function initializeClassElements(F, elements) { var proto = F.prototype; ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { var placement = element.placement; if (element.kind === kind && (placement === "static" || placement === "prototype")) { var receiver = placement === "static" ? F : proto; this.defineClassElement(receiver, element); } }, this); }, this); }, defineClassElement: function defineClassElement(receiver, element) { var descriptor = element.descriptor; if (element.kind === "field") { var initializer = element.initializer; descriptor = { enumerable: descriptor.enumerable, writable: descriptor.writable, configurable: descriptor.configurable, value: initializer === void 0 ? void 0 : initializer.call(receiver) }; } Object.defineProperty(receiver, element.key, descriptor); }, decorateClass: function decorateClass(elements, decorators) { var newElements = []; var finishers = []; var placements = { "static": [], prototype: [], own: [] }; elements.forEach(function (element) { this.addElementPlacement(element, placements); }, this); elements.forEach(function (element) { if (!_hasDecorators(element)) return newElements.push(element); var elementFinishersExtras = this.decorateElement(element, placements); newElements.push(elementFinishersExtras.element); newElements.push.apply(newElements, elementFinishersExtras.extras); finishers.push.apply(finishers, elementFinishersExtras.finishers); }, this); if (!decorators) { return { elements: newElements, finishers: finishers }; } var result = this.decorateConstructor(newElements, decorators); finishers.push.apply(finishers, result.finishers); result.finishers = finishers; return result; }, addElementPlacement: function addElementPlacement(element, placements, silent) { var keys = placements[element.placement]; if (!silent && keys.indexOf(element.key) !== -1) { throw new TypeError("Duplicated element (" + element.key + ")"); } keys.push(element.key); }, decorateElement: function decorateElement(element, placements) { var extras = []; var finishers = []; for (var decorators = element.decorators, i = decorators.length - 1; i >= 0; i--) { var keys = placements[element.placement]; keys.splice(keys.indexOf(element.key), 1); var elementObject = this.fromElementDescriptor(element); var elementFinisherExtras = this.toElementFinisherExtras((0, decorators[i])(elementObject) || elementObject); element = elementFinisherExtras.element; this.addElementPlacement(element, placements); if (elementFinisherExtras.finisher) { finishers.push(elementFinisherExtras.finisher); } var newExtras = elementFinisherExtras.extras; if (newExtras) { for (var j = 0; j < newExtras.length; j++) { this.addElementPlacement(newExtras[j], placements); } extras.push.apply(extras, newExtras); } } return { element: element, finishers: finishers, extras: extras }; }, decorateConstructor: function decorateConstructor(elements, decorators) { var finishers = []; for (var i = decorators.length - 1; i >= 0; i--) { var obj = this.fromClassDescriptor(elements); var elementsAndFinisher = this.toClassDescriptor((0, decorators[i])(obj) || obj); if (elementsAndFinisher.finisher !== undefined) { finishers.push(elementsAndFinisher.finisher); } if (elementsAndFinisher.elements !== undefined) { elements = elementsAndFinisher.elements; for (var j = 0; j < elements.length - 1; j++) { for (var k = j + 1; k < elements.length; k++) { if (elements[j].key === elements[k].key && elements[j].placement === elements[k].placement) { throw new TypeError("Duplicated element (" + elements[j].key + ")"); } } } } } return { elements: elements, finishers: finishers }; }, fromElementDescriptor: function fromElementDescriptor(element) { var obj = { kind: element.kind, key: element.key, placement: element.placement, descriptor: element.descriptor }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); if (element.kind === "field") obj.initializer = element.initializer; return obj; }, toElementDescriptors: function toElementDescriptors(elementObjects) { if (elementObjects === undefined) return; return _toArray(elementObjects).map(function (elementObject) { var element = this.toElementDescriptor(elementObject); this.disallowProperty(elementObject, "finisher", "An element descriptor"); this.disallowProperty(elementObject, "extras", "An element descriptor"); return element; }, this); }, toElementDescriptor: function toElementDescriptor(elementObject) { var kind = String(elementObject.kind); if (kind !== "method" && kind !== "field") { throw new TypeError('An element descriptor\'s .kind property must be either "method" or' + ' "field", but a decorator created an element descriptor with' + ' .kind "' + kind + '"'); } var key = _toPropertyKey(elementObject.key); var placement = String(elementObject.placement); if (placement !== "static" && placement !== "prototype" && placement !== "own") { throw new TypeError('An element descriptor\'s .placement property must be one of "static",' + ' "prototype" or "own", but a decorator created an element descriptor' + ' with .placement "' + placement + '"'); } var descriptor = elementObject.descriptor; this.disallowProperty(elementObject, "elements", "An element descriptor"); var element = { kind: kind, key: key, placement: placement, descriptor: Object.assign({}, descriptor) }; if (kind !== "field") { this.disallowProperty(elementObject, "initializer", "A method descriptor"); } else { this.disallowProperty(descriptor, "get", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "set", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "value", "The property descriptor of a field descriptor"); element.initializer = elementObject.initializer; } return element; }, toElementFinisherExtras: function toElementFinisherExtras(elementObject) { var element = this.toElementDescriptor(elementObject); var finisher = _optionalCallableProperty(elementObject, "finisher"); var extras = this.toElementDescriptors(elementObject.extras); return { element: element, finisher: finisher, extras: extras }; }, fromClassDescriptor: function fromClassDescriptor(elements) { var obj = { kind: "class", elements: elements.map(this.fromElementDescriptor, this) }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); return obj; }, toClassDescriptor: function toClassDescriptor(obj) { var kind = String(obj.kind); if (kind !== "class") { throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator' + ' created a class descriptor with .kind "' + kind + '"'); } this.disallowProperty(obj, "key", "A class descriptor"); this.disallowProperty(obj, "placement", "A class descriptor"); this.disallowProperty(obj, "descriptor", "A class descriptor"); this.disallowProperty(obj, "initializer", "A class descriptor"); this.disallowProperty(obj, "extras", "A class descriptor"); var finisher = _optionalCallableProperty(obj, "finisher"); var elements = this.toElementDescriptors(obj.elements); return { elements: elements, finisher: finisher }; }, runClassFinishers: function runClassFinishers(constructor, finishers) { for (var i = 0; i < finishers.length; i++) { var newConstructor = (0, finishers[i])(constructor); if (newConstructor !== undefined) { if (typeof newConstructor !== "function") { throw new TypeError("Finishers must return a constructor."); } constructor = newConstructor; } } return constructor; }, disallowProperty: function disallowProperty(obj, name, objectType) { if (obj[name] !== undefined) { throw new TypeError(objectType + " can't have a ." + name + " property."); } } }; return api; }

function _createElementDescriptor(def) { var key = _toPropertyKey(def.key); var descriptor; if (def.kind === "method") { descriptor = { value: def.value, writable: true, configurable: true, enumerable: false }; } else if (def.kind === "get") { descriptor = { get: def.value, configurable: true, enumerable: false }; } else if (def.kind === "set") { descriptor = { set: def.value, configurable: true, enumerable: false }; } else if (def.kind === "field") { descriptor = { configurable: true, writable: true, enumerable: true }; } var element = { kind: def.kind === "field" ? "field" : "method", key: key, placement: def["static"] ? "static" : def.kind === "field" ? "own" : "prototype", descriptor: descriptor }; if (def.decorators) element.decorators = def.decorators; if (def.kind === "field") element.initializer = def.value; return element; }

function _coalesceGetterSetter(element, other) { if (element.descriptor.get !== undefined) { other.descriptor.get = element.descriptor.get; } else { other.descriptor.set = element.descriptor.set; } }

function _coalesceClassElements(elements) { var newElements = []; var isSameElement = function isSameElement(other) { return other.kind === "method" && other.key === element.key && other.placement === element.placement; }; for (var i = 0; i < elements.length; i++) { var element = elements[i]; var other; if (element.kind === "method" && (other = newElements.find(isSameElement))) { if (_isDataDescriptor(element.descriptor) || _isDataDescriptor(other.descriptor)) { if (_hasDecorators(element) || _hasDecorators(other)) { throw new ReferenceError("Duplicated methods (" + element.key + ") can't be decorated."); } other.descriptor = element.descriptor; } else { if (_hasDecorators(element)) { if (_hasDecorators(other)) { throw new ReferenceError("Decorators can't be placed on different accessors with for " + "the same property (" + element.key + ")."); } other.decorators = element.decorators; } _coalesceGetterSetter(element, other); } } else { newElements.push(element); } } return newElements; }

function _hasDecorators(element) { return element.decorators && element.decorators.length; }

function _isDataDescriptor(desc) { return desc !== undefined && !(desc.value === undefined && desc.writable === undefined); }

function _optionalCallableProperty(obj, name) { var value = obj[name]; if (value !== undefined && typeof value !== "function") { throw new TypeError("Expected '" + name + "' to be a function"); } return value; }

function _toPropertyKey(arg) { var key = _toPrimitive(arg, "string"); return _typeof(key) === "symbol" ? key : String(key); }

function _toPrimitive(input, hint) { if (_typeof(input) !== "object" || input === null) return input; var prim = input[Symbol.toPrimitive]; if (prim !== undefined) { var res = prim.call(input, hint || "default"); if (_typeof(res) !== "object") return res; throw new TypeError("@@toPrimitive must return a primitive value."); } return (hint === "string" ? String : Number)(input); }

function _toArray(arr) { return _arrayWithHoles(arr) || _iterableToArray(arr) || _unsupportedIterableToArray(arr) || _nonIterableRest(); }

function _nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function _unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return _arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(n); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return _arrayLikeToArray(o, minLen); }

function _arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function _iterableToArray(iter) { if (typeof Symbol !== "undefined" && Symbol.iterator in Object(iter)) return Array.from(iter); }

function _arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }



var HassioAnsiToHtml = _decorate([Object(lit_element__WEBPACK_IMPORTED_MODULE_0__[/* customElement */ "d"])("hassio-ansi-to-html")], function (_initialize, _LitElement) {
  var HassioAnsiToHtml = /*#__PURE__*/function (_LitElement2) {
    _inherits(HassioAnsiToHtml, _LitElement2);

    var _super = _createSuper(HassioAnsiToHtml);

    function HassioAnsiToHtml() {
      var _this;

      _classCallCheck(this, HassioAnsiToHtml);

      for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
        args[_key] = arguments[_key];
      }

      _this = _super.call.apply(_super, [this].concat(args));

      _initialize(_assertThisInitialized(_this));

      return _this;
    }

    return HassioAnsiToHtml;
  }(_LitElement);

  return {
    F: HassioAnsiToHtml,
    d: [{
      kind: "field",
      decorators: [Object(lit_element__WEBPACK_IMPORTED_MODULE_0__[/* property */ "f"])()],
      key: "content",
      value: void 0
    }, {
      kind: "method",
      key: "render",
      value: function render() {
        return Object(lit_element__WEBPACK_IMPORTED_MODULE_0__[/* html */ "e"])(_templateObject(), this._parseTextToColoredPre(this.content));
      }
    }, {
      kind: "get",
      "static": true,
      key: "styles",
      value: function styles() {
        return Object(lit_element__WEBPACK_IMPORTED_MODULE_0__[/* css */ "c"])(_templateObject2());
      }
    }, {
      kind: "method",
      key: "_parseTextToColoredPre",
      value: function _parseTextToColoredPre(text) {
        var pre = document.createElement("pre");
        var re = /\033(?:\[(.*?)[@-~]|\].*?(?:\007|\033\\))/g;
        var i = 0;
        var state = {
          bold: false,
          italic: false,
          underline: false,
          strikethrough: false,
          foregroundColor: null,
          backgroundColor: null
        };

        var addSpan = function addSpan(content) {
          var span = document.createElement("span");

          if (state.bold) {
            span.classList.add("bold");
          }

          if (state.italic) {
            span.classList.add("italic");
          }

          if (state.underline) {
            span.classList.add("underline");
          }

          if (state.strikethrough) {
            span.classList.add("strikethrough");
          }

          if (state.foregroundColor !== null) {
            span.classList.add("fg-".concat(state.foregroundColor));
          }

          if (state.backgroundColor !== null) {
            span.classList.add("bg-".concat(state.backgroundColor));
          }

          span.appendChild(document.createTextNode(content));
          pre.appendChild(span);
        };
        /* eslint-disable no-cond-assign */


        var match; // eslint-disable-next-line

        while ((match = re.exec(text)) !== null) {
          var j = match.index;
          addSpan(text.substring(i, j));
          i = j + match[0].length;

          if (match[1] === undefined) {
            continue;
          }

          match[1].split(";").forEach(function (colorCode) {
            switch (parseInt(colorCode, 10)) {
              case 0:
                // reset
                state.bold = false;
                state.italic = false;
                state.underline = false;
                state.strikethrough = false;
                state.foregroundColor = null;
                state.backgroundColor = null;
                break;

              case 1:
                state.bold = true;
                break;

              case 3:
                state.italic = true;
                break;

              case 4:
                state.underline = true;
                break;

              case 9:
                state.strikethrough = true;
                break;

              case 22:
                state.bold = false;
                break;

              case 23:
                state.italic = false;
                break;

              case 24:
                state.underline = false;
                break;

              case 29:
                state.strikethrough = false;
                break;

              case 30:
                // foreground black
                state.foregroundColor = null;
                break;

              case 31:
                state.foregroundColor = "red";
                break;

              case 32:
                state.foregroundColor = "green";
                break;

              case 33:
                state.foregroundColor = "yellow";
                break;

              case 34:
                state.foregroundColor = "blue";
                break;

              case 35:
                state.foregroundColor = "magenta";
                break;

              case 36:
                state.foregroundColor = "cyan";
                break;

              case 37:
                state.foregroundColor = "white";
                break;

              case 39:
                // foreground reset
                state.foregroundColor = null;
                break;

              case 40:
                state.backgroundColor = "black";
                break;

              case 41:
                state.backgroundColor = "red";
                break;

              case 42:
                state.backgroundColor = "green";
                break;

              case 43:
                state.backgroundColor = "yellow";
                break;

              case 44:
                state.backgroundColor = "blue";
                break;

              case 45:
                state.backgroundColor = "magenta";
                break;

              case 46:
                state.backgroundColor = "cyan";
                break;

              case 47:
                state.backgroundColor = "white";
                break;

              case 49:
                // background reset
                state.backgroundColor = null;
                break;
            }
          });
        }

        addSpan(text.substring(i));
        return pre;
      }
    }]
  };
}, lit_element__WEBPACK_IMPORTED_MODULE_0__[/* LitElement */ "a"]);

/***/ }),

/***/ 143:
/***/ (function(module) {

module.exports = JSON.parse("{\"version\":\"4.9.95\",\"parts\":[{\"file\":\"ac96ae39d5ca52d23a4ca3d8c6efd5817270091d\"},{\"start\":\"alarm-o\",\"file\":\"d561c36273559890cb6dd9ff93c52f65ebd813c1\"},{\"start\":\"arrow-decision-o\",\"file\":\"c9b7511d0d2534fd6eb9a2d4096ae2d6986c5437\"},{\"start\":\"basket-\",\"file\":\"bc336f888b18158e39d0bf49be0f4c6159b9cc85\"},{\"start\":\"blur\",\"file\":\"119bbb7a5c295866fca20bccb3f56815ad7b9a3d\"},{\"start\":\"bus-d\",\"file\":\"cb82b14ed371a8b31c33d1e86221168c88a2daa1\"},{\"start\":\"card-s\",\"file\":\"c696f5a7ff858eed9b0360a22afa93a4e149f281\"},{\"start\":\"circle-slice-7\",\"file\":\"0aa03086dceff355dce1a5fd76b655532d1ce106\"},{\"start\":\"comment-t\",\"file\":\"b80a4774f52c2c2a5e4239cc559281cb5a46541e\"},{\"start\":\"cursor-m\",\"file\":\"689ebae34d4c444f2ac79c845935f6a39d9cb55e\"},{\"start\":\"door-closed-\",\"file\":\"e3d51e324319d10fd3e55ac99e0748aa4e5055ee\"},{\"start\":\"eraser-\",\"file\":\"42a1c8b700556b7e088be85381b9ac492be31732\"},{\"start\":\"file-pdf-o\",\"file\":\"6c687283fbb6d8413dccbaac610e5e91917d0197\"},{\"start\":\"folder-alert-\",\"file\":\"8be2f984e49a6eaa69a04fd95bd805b3331d94ae\"},{\"start\":\"gamepad-circle-l\",\"file\":\"986ac139fe53bb8be3fedc1ee88af3d7d3e5d53e\"},{\"start\":\"google-p\",\"file\":\"dafb98730fb6f5fcb84b8b94daa920f839d40489\"},{\"start\":\"help-network-\",\"file\":\"a9beb4f10e3575df275e888c1160fc0c1f479a6e\"},{\"start\":\"je\",\"file\":\"df7feb02fe5538edfabb04344646a7318b595259\"},{\"start\":\"layers-ou\",\"file\":\"d8a4c48654c6d31621b08d77a32a5960d64b010c\"},{\"start\":\"map-marker-radius-\",\"file\":\"912daef373e4d5f510836a3b5d195046dfba22c2\"},{\"start\":\"music-\",\"file\":\"cdd1042da2ee7f986e1b035f47901990602c2396\"},{\"start\":\"ou\",\"file\":\"e0ca7b494b7d522f697b00bf83ef596485c7bb98\"},{\"start\":\"phone-paused-\",\"file\":\"93595e945f217083b66408535f56938cb236e91a\"},{\"start\":\"qual\",\"file\":\"d225ac5378ccb48ee4228521f7325526bec0ebd9\"},{\"start\":\"safe-square-\",\"file\":\"bb47adffdf4b9ae3bdcddf438611375c79b73e22\"},{\"start\":\"shield-h\",\"file\":\"344afc4666d56ca2265ec5b8e693b326350c8fcc\"},{\"start\":\"source-repository-\",\"file\":\"369429d8708392e396580146ef6b5b29bdc980a2\"},{\"start\":\"table-p\",\"file\":\"20834d5f95635fd28910309cbdf72cd5249db156\"},{\"start\":\"tow\",\"file\":\"475e7121d81fbc25c95af2cf38622d5192dc005c\"},{\"start\":\"vibrate-\",\"file\":\"56507ed6d56716b4e846f901e9d980a7cdb56555\"},{\"start\":\"weather-su\",\"file\":\"22359538f304ca383bbc4401af6207227c68e4ec\"},{\"start\":\"zodiac-li\",\"file\":\"ad46cd3ed385233a41d3bda8b2975dfcf14a02a3\"}]}");

/***/ }),

/***/ 188:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);

// EXTERNAL MODULE: ./node_modules/@material/mwc-button/mwc-button.js + 12 modules
var mwc_button = __webpack_require__(18);

// EXTERNAL MODULE: ./node_modules/@polymer/paper-input/paper-input.js + 7 modules
var paper_input = __webpack_require__(43);

// EXTERNAL MODULE: ./node_modules/@polymer/paper-spinner/paper-spinner.js
var paper_spinner = __webpack_require__(118);

// EXTERNAL MODULE: ./node_modules/@polymer/paper-item/paper-item.js + 2 modules
var paper_item = __webpack_require__(100);

// EXTERNAL MODULE: ./node_modules/@polymer/paper-item/paper-item-body.js
var paper_item_body = __webpack_require__(146);

// EXTERNAL MODULE: ./node_modules/lit-element/lit-element.js + 3 modules
var lit_element = __webpack_require__(5);

// EXTERNAL MODULE: ./node_modules/memoize-one/dist/memoize-one.esm.js
var memoize_one_esm = __webpack_require__(50);

// EXTERNAL MODULE: ./node_modules/@material/mwc-dialog/mwc-dialog.js + 3 modules
var mwc_dialog = __webpack_require__(186);

// EXTERNAL MODULE: ./node_modules/@material/mwc-dialog/mwc-dialog-css.js
var mwc_dialog_css = __webpack_require__(120);

// EXTERNAL MODULE: ./src/components/ha-icon-button.ts
var ha_icon_button = __webpack_require__(23);

// CONCATENATED MODULE: ./src/components/ha-dialog.ts
function _typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { _typeof = function _typeof(obj) { return typeof obj; }; } else { _typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return _typeof(obj); }

function _templateObject2() {
  var data = _taggedTemplateLiteral(["\n        .mdc-dialog__actions {\n          justify-content: var(--justify-action-buttons, flex-end);\n        }\n        .mdc-dialog__container {\n          align-items: var(--vertial-align-dialog, center);\n        }\n        .mdc-dialog__title::before {\n          display: block;\n          height: 20px;\n        }\n        .close_button {\n          position: absolute;\n          right: 16px;\n          top: 12px;\n        }\n      "]);

  _templateObject2 = function _templateObject2() {
    return data;
  };

  return data;
}

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) _setPrototypeOf(subClass, superClass); }

function _setPrototypeOf(o, p) { _setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return _setPrototypeOf(o, p); }

function _createSuper(Derived) { return function () { var Super = _getPrototypeOf(Derived), result; if (_isNativeReflectConstruct()) { var NewTarget = _getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return _possibleConstructorReturn(this, result); }; }

function _possibleConstructorReturn(self, call) { if (call && (_typeof(call) === "object" || typeof call === "function")) { return call; } return _assertThisInitialized(self); }

function _assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function _isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Date.prototype.toString.call(Reflect.construct(Date, [], function () {})); return true; } catch (e) { return false; } }

function _getPrototypeOf(o) { _getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return _getPrototypeOf(o); }

function _decorate(decorators, factory, superClass, mixins) { var api = _getDecoratorsApi(); if (mixins) { for (var i = 0; i < mixins.length; i++) { api = mixins[i](api); } } var r = factory(function initialize(O) { api.initializeInstanceElements(O, decorated.elements); }, superClass); var decorated = api.decorateClass(_coalesceClassElements(r.d.map(_createElementDescriptor)), decorators); api.initializeClassElements(r.F, decorated.elements); return api.runClassFinishers(r.F, decorated.finishers); }

function _getDecoratorsApi() { _getDecoratorsApi = function _getDecoratorsApi() { return api; }; var api = { elementsDefinitionOrder: [["method"], ["field"]], initializeInstanceElements: function initializeInstanceElements(O, elements) { ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { if (element.kind === kind && element.placement === "own") { this.defineClassElement(O, element); } }, this); }, this); }, initializeClassElements: function initializeClassElements(F, elements) { var proto = F.prototype; ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { var placement = element.placement; if (element.kind === kind && (placement === "static" || placement === "prototype")) { var receiver = placement === "static" ? F : proto; this.defineClassElement(receiver, element); } }, this); }, this); }, defineClassElement: function defineClassElement(receiver, element) { var descriptor = element.descriptor; if (element.kind === "field") { var initializer = element.initializer; descriptor = { enumerable: descriptor.enumerable, writable: descriptor.writable, configurable: descriptor.configurable, value: initializer === void 0 ? void 0 : initializer.call(receiver) }; } Object.defineProperty(receiver, element.key, descriptor); }, decorateClass: function decorateClass(elements, decorators) { var newElements = []; var finishers = []; var placements = { "static": [], prototype: [], own: [] }; elements.forEach(function (element) { this.addElementPlacement(element, placements); }, this); elements.forEach(function (element) { if (!_hasDecorators(element)) return newElements.push(element); var elementFinishersExtras = this.decorateElement(element, placements); newElements.push(elementFinishersExtras.element); newElements.push.apply(newElements, elementFinishersExtras.extras); finishers.push.apply(finishers, elementFinishersExtras.finishers); }, this); if (!decorators) { return { elements: newElements, finishers: finishers }; } var result = this.decorateConstructor(newElements, decorators); finishers.push.apply(finishers, result.finishers); result.finishers = finishers; return result; }, addElementPlacement: function addElementPlacement(element, placements, silent) { var keys = placements[element.placement]; if (!silent && keys.indexOf(element.key) !== -1) { throw new TypeError("Duplicated element (" + element.key + ")"); } keys.push(element.key); }, decorateElement: function decorateElement(element, placements) { var extras = []; var finishers = []; for (var decorators = element.decorators, i = decorators.length - 1; i >= 0; i--) { var keys = placements[element.placement]; keys.splice(keys.indexOf(element.key), 1); var elementObject = this.fromElementDescriptor(element); var elementFinisherExtras = this.toElementFinisherExtras((0, decorators[i])(elementObject) || elementObject); element = elementFinisherExtras.element; this.addElementPlacement(element, placements); if (elementFinisherExtras.finisher) { finishers.push(elementFinisherExtras.finisher); } var newExtras = elementFinisherExtras.extras; if (newExtras) { for (var j = 0; j < newExtras.length; j++) { this.addElementPlacement(newExtras[j], placements); } extras.push.apply(extras, newExtras); } } return { element: element, finishers: finishers, extras: extras }; }, decorateConstructor: function decorateConstructor(elements, decorators) { var finishers = []; for (var i = decorators.length - 1; i >= 0; i--) { var obj = this.fromClassDescriptor(elements); var elementsAndFinisher = this.toClassDescriptor((0, decorators[i])(obj) || obj); if (elementsAndFinisher.finisher !== undefined) { finishers.push(elementsAndFinisher.finisher); } if (elementsAndFinisher.elements !== undefined) { elements = elementsAndFinisher.elements; for (var j = 0; j < elements.length - 1; j++) { for (var k = j + 1; k < elements.length; k++) { if (elements[j].key === elements[k].key && elements[j].placement === elements[k].placement) { throw new TypeError("Duplicated element (" + elements[j].key + ")"); } } } } } return { elements: elements, finishers: finishers }; }, fromElementDescriptor: function fromElementDescriptor(element) { var obj = { kind: element.kind, key: element.key, placement: element.placement, descriptor: element.descriptor }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); if (element.kind === "field") obj.initializer = element.initializer; return obj; }, toElementDescriptors: function toElementDescriptors(elementObjects) { if (elementObjects === undefined) return; return _toArray(elementObjects).map(function (elementObject) { var element = this.toElementDescriptor(elementObject); this.disallowProperty(elementObject, "finisher", "An element descriptor"); this.disallowProperty(elementObject, "extras", "An element descriptor"); return element; }, this); }, toElementDescriptor: function toElementDescriptor(elementObject) { var kind = String(elementObject.kind); if (kind !== "method" && kind !== "field") { throw new TypeError('An element descriptor\'s .kind property must be either "method" or' + ' "field", but a decorator created an element descriptor with' + ' .kind "' + kind + '"'); } var key = _toPropertyKey(elementObject.key); var placement = String(elementObject.placement); if (placement !== "static" && placement !== "prototype" && placement !== "own") { throw new TypeError('An element descriptor\'s .placement property must be one of "static",' + ' "prototype" or "own", but a decorator created an element descriptor' + ' with .placement "' + placement + '"'); } var descriptor = elementObject.descriptor; this.disallowProperty(elementObject, "elements", "An element descriptor"); var element = { kind: kind, key: key, placement: placement, descriptor: Object.assign({}, descriptor) }; if (kind !== "field") { this.disallowProperty(elementObject, "initializer", "A method descriptor"); } else { this.disallowProperty(descriptor, "get", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "set", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "value", "The property descriptor of a field descriptor"); element.initializer = elementObject.initializer; } return element; }, toElementFinisherExtras: function toElementFinisherExtras(elementObject) { var element = this.toElementDescriptor(elementObject); var finisher = _optionalCallableProperty(elementObject, "finisher"); var extras = this.toElementDescriptors(elementObject.extras); return { element: element, finisher: finisher, extras: extras }; }, fromClassDescriptor: function fromClassDescriptor(elements) { var obj = { kind: "class", elements: elements.map(this.fromElementDescriptor, this) }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); return obj; }, toClassDescriptor: function toClassDescriptor(obj) { var kind = String(obj.kind); if (kind !== "class") { throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator' + ' created a class descriptor with .kind "' + kind + '"'); } this.disallowProperty(obj, "key", "A class descriptor"); this.disallowProperty(obj, "placement", "A class descriptor"); this.disallowProperty(obj, "descriptor", "A class descriptor"); this.disallowProperty(obj, "initializer", "A class descriptor"); this.disallowProperty(obj, "extras", "A class descriptor"); var finisher = _optionalCallableProperty(obj, "finisher"); var elements = this.toElementDescriptors(obj.elements); return { elements: elements, finisher: finisher }; }, runClassFinishers: function runClassFinishers(constructor, finishers) { for (var i = 0; i < finishers.length; i++) { var newConstructor = (0, finishers[i])(constructor); if (newConstructor !== undefined) { if (typeof newConstructor !== "function") { throw new TypeError("Finishers must return a constructor."); } constructor = newConstructor; } } return constructor; }, disallowProperty: function disallowProperty(obj, name, objectType) { if (obj[name] !== undefined) { throw new TypeError(objectType + " can't have a ." + name + " property."); } } }; return api; }

function _createElementDescriptor(def) { var key = _toPropertyKey(def.key); var descriptor; if (def.kind === "method") { descriptor = { value: def.value, writable: true, configurable: true, enumerable: false }; } else if (def.kind === "get") { descriptor = { get: def.value, configurable: true, enumerable: false }; } else if (def.kind === "set") { descriptor = { set: def.value, configurable: true, enumerable: false }; } else if (def.kind === "field") { descriptor = { configurable: true, writable: true, enumerable: true }; } var element = { kind: def.kind === "field" ? "field" : "method", key: key, placement: def["static"] ? "static" : def.kind === "field" ? "own" : "prototype", descriptor: descriptor }; if (def.decorators) element.decorators = def.decorators; if (def.kind === "field") element.initializer = def.value; return element; }

function _coalesceGetterSetter(element, other) { if (element.descriptor.get !== undefined) { other.descriptor.get = element.descriptor.get; } else { other.descriptor.set = element.descriptor.set; } }

function _coalesceClassElements(elements) { var newElements = []; var isSameElement = function isSameElement(other) { return other.kind === "method" && other.key === element.key && other.placement === element.placement; }; for (var i = 0; i < elements.length; i++) { var element = elements[i]; var other; if (element.kind === "method" && (other = newElements.find(isSameElement))) { if (_isDataDescriptor(element.descriptor) || _isDataDescriptor(other.descriptor)) { if (_hasDecorators(element) || _hasDecorators(other)) { throw new ReferenceError("Duplicated methods (" + element.key + ") can't be decorated."); } other.descriptor = element.descriptor; } else { if (_hasDecorators(element)) { if (_hasDecorators(other)) { throw new ReferenceError("Decorators can't be placed on different accessors with for " + "the same property (" + element.key + ")."); } other.decorators = element.decorators; } _coalesceGetterSetter(element, other); } } else { newElements.push(element); } } return newElements; }

function _hasDecorators(element) { return element.decorators && element.decorators.length; }

function _isDataDescriptor(desc) { return desc !== undefined && !(desc.value === undefined && desc.writable === undefined); }

function _optionalCallableProperty(obj, name) { var value = obj[name]; if (value !== undefined && typeof value !== "function") { throw new TypeError("Expected '" + name + "' to be a function"); } return value; }

function _toPropertyKey(arg) { var key = _toPrimitive(arg, "string"); return _typeof(key) === "symbol" ? key : String(key); }

function _toPrimitive(input, hint) { if (_typeof(input) !== "object" || input === null) return input; var prim = input[Symbol.toPrimitive]; if (prim !== undefined) { var res = prim.call(input, hint || "default"); if (_typeof(res) !== "object") return res; throw new TypeError("@@toPrimitive must return a primitive value."); } return (hint === "string" ? String : Number)(input); }

function _toArray(arr) { return _arrayWithHoles(arr) || _iterableToArray(arr) || _unsupportedIterableToArray(arr) || _nonIterableRest(); }

function _nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function _unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return _arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(n); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return _arrayLikeToArray(o, minLen); }

function _arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function _iterableToArray(iter) { if (typeof Symbol !== "undefined" && Symbol.iterator in Object(iter)) return Array.from(iter); }

function _arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }

function _templateObject() {
  var data = _taggedTemplateLiteral(["\n  ", "\n  <ha-icon-button\n    aria-label=", "\n    icon=\"hass:close\"\n    dialogAction=\"close\"\n    class=\"close_button\"\n  ></ha-icon-button>\n"]);

  _templateObject = function _templateObject() {
    return data;
  };

  return data;
}

function _taggedTemplateLiteral(strings, raw) { if (!raw) { raw = strings.slice(0); } return Object.freeze(Object.defineProperties(strings, { raw: { value: Object.freeze(raw) } })); }





var MwcDialog = customElements.get("mwc-dialog");
var ha_dialog_createCloseHeading = function createCloseHeading(hass, title) {
  return Object(lit_element["e" /* html */])(_templateObject(), title, hass.localize("ui.dialogs.generic.close"));
};
var ha_dialog_HaDialog = _decorate([Object(lit_element["d" /* customElement */])("ha-dialog")], function (_initialize, _MwcDialog) {
  var HaDialog = /*#__PURE__*/function (_MwcDialog2) {
    _inherits(HaDialog, _MwcDialog2);

    var _super = _createSuper(HaDialog);

    function HaDialog() {
      var _this;

      _classCallCheck(this, HaDialog);

      for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
        args[_key] = arguments[_key];
      }

      _this = _super.call.apply(_super, [this].concat(args));

      _initialize(_assertThisInitialized(_this));

      return _this;
    }

    return HaDialog;
  }(_MwcDialog);

  return {
    F: HaDialog,
    d: [{
      kind: "get",
      "static": true,
      key: "styles",
      value: function styles() {
        return [mwc_dialog_css["a" /* style */], Object(lit_element["c" /* css */])(_templateObject2())];
      }
    }]
  };
}, MwcDialog);
// EXTERNAL MODULE: ./src/resources/styles.ts
var resources_styles = __webpack_require__(11);

// EXTERNAL MODULE: ./src/data/hassio/addon.ts
var addon = __webpack_require__(22);

// EXTERNAL MODULE: ./src/data/hassio/supervisor.ts
var supervisor = __webpack_require__(49);

// CONCATENATED MODULE: ./hassio/src/dialogs/repositories/dialog-hassio-repositories.ts
function dialog_hassio_repositories_typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { dialog_hassio_repositories_typeof = function _typeof(obj) { return typeof obj; }; } else { dialog_hassio_repositories_typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return dialog_hassio_repositories_typeof(obj); }

function _templateObject6() {
  var data = dialog_hassio_repositories_taggedTemplateLiteral(["\n        ha-dialog.button-left {\n          --justify-action-buttons: flex-start;\n        }\n        paper-icon-item {\n          cursor: pointer;\n        }\n        .form {\n          color: var(--primary-text-color);\n        }\n        .option {\n          border: 1px solid var(--divider-color);\n          border-radius: 4px;\n          margin-top: 4px;\n        }\n        mwc-button {\n          margin-left: 8px;\n        }\n        ha-paper-dropdown-menu {\n          display: block;\n        }\n      "]);

  _templateObject6 = function _templateObject6() {
    return data;
  };

  return data;
}

function _templateObject5() {
  var data = dialog_hassio_repositories_taggedTemplateLiteral(["<paper-spinner active></paper-spinner>"]);

  _templateObject5 = function _templateObject5() {
    return data;
  };

  return data;
}

function _templateObject4() {
  var data = dialog_hassio_repositories_taggedTemplateLiteral(["\n                <paper-item>\n                  No repositories\n                </paper-item>\n              "]);

  _templateObject4 = function _templateObject4() {
    return data;
  };

  return data;
}

function _templateObject3() {
  var data = dialog_hassio_repositories_taggedTemplateLiteral(["\n                  <paper-item class=\"option\">\n                    <paper-item-body three-line>\n                      <div>", "</div>\n                      <div secondary>", "</div>\n                      <div secondary>", "</div>\n                    </paper-item-body>\n                    <ha-icon-button\n                      .slug=", "\n                      title=\"Remove\"\n                      @click=", "\n                      icon=\"hassio:delete\"\n                    ></ha-icon-button>\n                  </paper-item>\n                "]);

  _templateObject3 = function _templateObject3() {
    return data;
  };

  return data;
}

function dialog_hassio_repositories_templateObject2() {
  var data = dialog_hassio_repositories_taggedTemplateLiteral(["<div class=\"error\">", "</div>"]);

  dialog_hassio_repositories_templateObject2 = function _templateObject2() {
    return data;
  };

  return data;
}

function dialog_hassio_repositories_templateObject() {
  var data = dialog_hassio_repositories_taggedTemplateLiteral(["\n      <ha-dialog\n        .open=", "\n        @closing=", "\n        scrimClickAction\n        escapeKeyAction\n        heading=\"Manage add-on repositories\"\n      >\n        ", "\n        <div class=\"form\">\n          ", "\n          <div class=\"layout horizontal bottom\">\n            <paper-input\n              class=\"flex-auto\"\n              id=\"repository_input\"\n              label=\"Add repository\"\n              @keydown=", "\n            ></paper-input>\n            <mwc-button @click=", ">\n              ", "\n            </mwc-button>\n          </div>\n        </div>\n        <mwc-button slot=\"primaryAction\" @click=\"", "\">\n          Close\n        </mwc-button>\n      </ha-dialog>\n    "]);

  dialog_hassio_repositories_templateObject = function _templateObject() {
    return data;
  };

  return data;
}

function dialog_hassio_repositories_taggedTemplateLiteral(strings, raw) { if (!raw) { raw = strings.slice(0); } return Object.freeze(Object.defineProperties(strings, { raw: { value: Object.freeze(raw) } })); }

function asyncGeneratorStep(gen, resolve, reject, _next, _throw, key, arg) { try { var info = gen[key](arg); var value = info.value; } catch (error) { reject(error); return; } if (info.done) { resolve(value); } else { Promise.resolve(value).then(_next, _throw); } }

function _asyncToGenerator(fn) { return function () { var self = this, args = arguments; return new Promise(function (resolve, reject) { var gen = fn.apply(self, args); function _next(value) { asyncGeneratorStep(gen, resolve, reject, _next, _throw, "next", value); } function _throw(err) { asyncGeneratorStep(gen, resolve, reject, _next, _throw, "throw", err); } _next(undefined); }); }; }

function dialog_hassio_repositories_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function dialog_hassio_repositories_inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) dialog_hassio_repositories_setPrototypeOf(subClass, superClass); }

function dialog_hassio_repositories_setPrototypeOf(o, p) { dialog_hassio_repositories_setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return dialog_hassio_repositories_setPrototypeOf(o, p); }

function dialog_hassio_repositories_createSuper(Derived) { return function () { var Super = dialog_hassio_repositories_getPrototypeOf(Derived), result; if (dialog_hassio_repositories_isNativeReflectConstruct()) { var NewTarget = dialog_hassio_repositories_getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return dialog_hassio_repositories_possibleConstructorReturn(this, result); }; }

function dialog_hassio_repositories_possibleConstructorReturn(self, call) { if (call && (dialog_hassio_repositories_typeof(call) === "object" || typeof call === "function")) { return call; } return dialog_hassio_repositories_assertThisInitialized(self); }

function dialog_hassio_repositories_assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function dialog_hassio_repositories_isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Date.prototype.toString.call(Reflect.construct(Date, [], function () {})); return true; } catch (e) { return false; } }

function dialog_hassio_repositories_getPrototypeOf(o) { dialog_hassio_repositories_getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return dialog_hassio_repositories_getPrototypeOf(o); }

function dialog_hassio_repositories_decorate(decorators, factory, superClass, mixins) { var api = dialog_hassio_repositories_getDecoratorsApi(); if (mixins) { for (var i = 0; i < mixins.length; i++) { api = mixins[i](api); } } var r = factory(function initialize(O) { api.initializeInstanceElements(O, decorated.elements); }, superClass); var decorated = api.decorateClass(dialog_hassio_repositories_coalesceClassElements(r.d.map(dialog_hassio_repositories_createElementDescriptor)), decorators); api.initializeClassElements(r.F, decorated.elements); return api.runClassFinishers(r.F, decorated.finishers); }

function dialog_hassio_repositories_getDecoratorsApi() { dialog_hassio_repositories_getDecoratorsApi = function _getDecoratorsApi() { return api; }; var api = { elementsDefinitionOrder: [["method"], ["field"]], initializeInstanceElements: function initializeInstanceElements(O, elements) { ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { if (element.kind === kind && element.placement === "own") { this.defineClassElement(O, element); } }, this); }, this); }, initializeClassElements: function initializeClassElements(F, elements) { var proto = F.prototype; ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { var placement = element.placement; if (element.kind === kind && (placement === "static" || placement === "prototype")) { var receiver = placement === "static" ? F : proto; this.defineClassElement(receiver, element); } }, this); }, this); }, defineClassElement: function defineClassElement(receiver, element) { var descriptor = element.descriptor; if (element.kind === "field") { var initializer = element.initializer; descriptor = { enumerable: descriptor.enumerable, writable: descriptor.writable, configurable: descriptor.configurable, value: initializer === void 0 ? void 0 : initializer.call(receiver) }; } Object.defineProperty(receiver, element.key, descriptor); }, decorateClass: function decorateClass(elements, decorators) { var newElements = []; var finishers = []; var placements = { "static": [], prototype: [], own: [] }; elements.forEach(function (element) { this.addElementPlacement(element, placements); }, this); elements.forEach(function (element) { if (!dialog_hassio_repositories_hasDecorators(element)) return newElements.push(element); var elementFinishersExtras = this.decorateElement(element, placements); newElements.push(elementFinishersExtras.element); newElements.push.apply(newElements, elementFinishersExtras.extras); finishers.push.apply(finishers, elementFinishersExtras.finishers); }, this); if (!decorators) { return { elements: newElements, finishers: finishers }; } var result = this.decorateConstructor(newElements, decorators); finishers.push.apply(finishers, result.finishers); result.finishers = finishers; return result; }, addElementPlacement: function addElementPlacement(element, placements, silent) { var keys = placements[element.placement]; if (!silent && keys.indexOf(element.key) !== -1) { throw new TypeError("Duplicated element (" + element.key + ")"); } keys.push(element.key); }, decorateElement: function decorateElement(element, placements) { var extras = []; var finishers = []; for (var decorators = element.decorators, i = decorators.length - 1; i >= 0; i--) { var keys = placements[element.placement]; keys.splice(keys.indexOf(element.key), 1); var elementObject = this.fromElementDescriptor(element); var elementFinisherExtras = this.toElementFinisherExtras((0, decorators[i])(elementObject) || elementObject); element = elementFinisherExtras.element; this.addElementPlacement(element, placements); if (elementFinisherExtras.finisher) { finishers.push(elementFinisherExtras.finisher); } var newExtras = elementFinisherExtras.extras; if (newExtras) { for (var j = 0; j < newExtras.length; j++) { this.addElementPlacement(newExtras[j], placements); } extras.push.apply(extras, newExtras); } } return { element: element, finishers: finishers, extras: extras }; }, decorateConstructor: function decorateConstructor(elements, decorators) { var finishers = []; for (var i = decorators.length - 1; i >= 0; i--) { var obj = this.fromClassDescriptor(elements); var elementsAndFinisher = this.toClassDescriptor((0, decorators[i])(obj) || obj); if (elementsAndFinisher.finisher !== undefined) { finishers.push(elementsAndFinisher.finisher); } if (elementsAndFinisher.elements !== undefined) { elements = elementsAndFinisher.elements; for (var j = 0; j < elements.length - 1; j++) { for (var k = j + 1; k < elements.length; k++) { if (elements[j].key === elements[k].key && elements[j].placement === elements[k].placement) { throw new TypeError("Duplicated element (" + elements[j].key + ")"); } } } } } return { elements: elements, finishers: finishers }; }, fromElementDescriptor: function fromElementDescriptor(element) { var obj = { kind: element.kind, key: element.key, placement: element.placement, descriptor: element.descriptor }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); if (element.kind === "field") obj.initializer = element.initializer; return obj; }, toElementDescriptors: function toElementDescriptors(elementObjects) { if (elementObjects === undefined) return; return dialog_hassio_repositories_toArray(elementObjects).map(function (elementObject) { var element = this.toElementDescriptor(elementObject); this.disallowProperty(elementObject, "finisher", "An element descriptor"); this.disallowProperty(elementObject, "extras", "An element descriptor"); return element; }, this); }, toElementDescriptor: function toElementDescriptor(elementObject) { var kind = String(elementObject.kind); if (kind !== "method" && kind !== "field") { throw new TypeError('An element descriptor\'s .kind property must be either "method" or' + ' "field", but a decorator created an element descriptor with' + ' .kind "' + kind + '"'); } var key = dialog_hassio_repositories_toPropertyKey(elementObject.key); var placement = String(elementObject.placement); if (placement !== "static" && placement !== "prototype" && placement !== "own") { throw new TypeError('An element descriptor\'s .placement property must be one of "static",' + ' "prototype" or "own", but a decorator created an element descriptor' + ' with .placement "' + placement + '"'); } var descriptor = elementObject.descriptor; this.disallowProperty(elementObject, "elements", "An element descriptor"); var element = { kind: kind, key: key, placement: placement, descriptor: Object.assign({}, descriptor) }; if (kind !== "field") { this.disallowProperty(elementObject, "initializer", "A method descriptor"); } else { this.disallowProperty(descriptor, "get", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "set", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "value", "The property descriptor of a field descriptor"); element.initializer = elementObject.initializer; } return element; }, toElementFinisherExtras: function toElementFinisherExtras(elementObject) { var element = this.toElementDescriptor(elementObject); var finisher = dialog_hassio_repositories_optionalCallableProperty(elementObject, "finisher"); var extras = this.toElementDescriptors(elementObject.extras); return { element: element, finisher: finisher, extras: extras }; }, fromClassDescriptor: function fromClassDescriptor(elements) { var obj = { kind: "class", elements: elements.map(this.fromElementDescriptor, this) }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); return obj; }, toClassDescriptor: function toClassDescriptor(obj) { var kind = String(obj.kind); if (kind !== "class") { throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator' + ' created a class descriptor with .kind "' + kind + '"'); } this.disallowProperty(obj, "key", "A class descriptor"); this.disallowProperty(obj, "placement", "A class descriptor"); this.disallowProperty(obj, "descriptor", "A class descriptor"); this.disallowProperty(obj, "initializer", "A class descriptor"); this.disallowProperty(obj, "extras", "A class descriptor"); var finisher = dialog_hassio_repositories_optionalCallableProperty(obj, "finisher"); var elements = this.toElementDescriptors(obj.elements); return { elements: elements, finisher: finisher }; }, runClassFinishers: function runClassFinishers(constructor, finishers) { for (var i = 0; i < finishers.length; i++) { var newConstructor = (0, finishers[i])(constructor); if (newConstructor !== undefined) { if (typeof newConstructor !== "function") { throw new TypeError("Finishers must return a constructor."); } constructor = newConstructor; } } return constructor; }, disallowProperty: function disallowProperty(obj, name, objectType) { if (obj[name] !== undefined) { throw new TypeError(objectType + " can't have a ." + name + " property."); } } }; return api; }

function dialog_hassio_repositories_createElementDescriptor(def) { var key = dialog_hassio_repositories_toPropertyKey(def.key); var descriptor; if (def.kind === "method") { descriptor = { value: def.value, writable: true, configurable: true, enumerable: false }; } else if (def.kind === "get") { descriptor = { get: def.value, configurable: true, enumerable: false }; } else if (def.kind === "set") { descriptor = { set: def.value, configurable: true, enumerable: false }; } else if (def.kind === "field") { descriptor = { configurable: true, writable: true, enumerable: true }; } var element = { kind: def.kind === "field" ? "field" : "method", key: key, placement: def["static"] ? "static" : def.kind === "field" ? "own" : "prototype", descriptor: descriptor }; if (def.decorators) element.decorators = def.decorators; if (def.kind === "field") element.initializer = def.value; return element; }

function dialog_hassio_repositories_coalesceGetterSetter(element, other) { if (element.descriptor.get !== undefined) { other.descriptor.get = element.descriptor.get; } else { other.descriptor.set = element.descriptor.set; } }

function dialog_hassio_repositories_coalesceClassElements(elements) { var newElements = []; var isSameElement = function isSameElement(other) { return other.kind === "method" && other.key === element.key && other.placement === element.placement; }; for (var i = 0; i < elements.length; i++) { var element = elements[i]; var other; if (element.kind === "method" && (other = newElements.find(isSameElement))) { if (dialog_hassio_repositories_isDataDescriptor(element.descriptor) || dialog_hassio_repositories_isDataDescriptor(other.descriptor)) { if (dialog_hassio_repositories_hasDecorators(element) || dialog_hassio_repositories_hasDecorators(other)) { throw new ReferenceError("Duplicated methods (" + element.key + ") can't be decorated."); } other.descriptor = element.descriptor; } else { if (dialog_hassio_repositories_hasDecorators(element)) { if (dialog_hassio_repositories_hasDecorators(other)) { throw new ReferenceError("Decorators can't be placed on different accessors with for " + "the same property (" + element.key + ")."); } other.decorators = element.decorators; } dialog_hassio_repositories_coalesceGetterSetter(element, other); } } else { newElements.push(element); } } return newElements; }

function dialog_hassio_repositories_hasDecorators(element) { return element.decorators && element.decorators.length; }

function dialog_hassio_repositories_isDataDescriptor(desc) { return desc !== undefined && !(desc.value === undefined && desc.writable === undefined); }

function dialog_hassio_repositories_optionalCallableProperty(obj, name) { var value = obj[name]; if (value !== undefined && typeof value !== "function") { throw new TypeError("Expected '" + name + "' to be a function"); } return value; }

function dialog_hassio_repositories_toPropertyKey(arg) { var key = dialog_hassio_repositories_toPrimitive(arg, "string"); return dialog_hassio_repositories_typeof(key) === "symbol" ? key : String(key); }

function dialog_hassio_repositories_toPrimitive(input, hint) { if (dialog_hassio_repositories_typeof(input) !== "object" || input === null) return input; var prim = input[Symbol.toPrimitive]; if (prim !== undefined) { var res = prim.call(input, hint || "default"); if (dialog_hassio_repositories_typeof(res) !== "object") return res; throw new TypeError("@@toPrimitive must return a primitive value."); } return (hint === "string" ? String : Number)(input); }

function dialog_hassio_repositories_toArray(arr) { return dialog_hassio_repositories_arrayWithHoles(arr) || dialog_hassio_repositories_iterableToArray(arr) || dialog_hassio_repositories_unsupportedIterableToArray(arr) || dialog_hassio_repositories_nonIterableRest(); }

function dialog_hassio_repositories_nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function dialog_hassio_repositories_unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return dialog_hassio_repositories_arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(n); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return dialog_hassio_repositories_arrayLikeToArray(o, minLen); }

function dialog_hassio_repositories_arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function dialog_hassio_repositories_iterableToArray(iter) { if (typeof Symbol !== "undefined" && Symbol.iterator in Object(iter)) return Array.from(iter); }

function dialog_hassio_repositories_arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }














var dialog_hassio_repositories_HassioRepositoriesDialog = dialog_hassio_repositories_decorate([Object(lit_element["d" /* customElement */])("dialog-hassio-repositories")], function (_initialize, _LitElement) {
  var HassioRepositoriesDialog = /*#__PURE__*/function (_LitElement2) {
    dialog_hassio_repositories_inherits(HassioRepositoriesDialog, _LitElement2);

    var _super = dialog_hassio_repositories_createSuper(HassioRepositoriesDialog);

    function HassioRepositoriesDialog() {
      var _this;

      dialog_hassio_repositories_classCallCheck(this, HassioRepositoriesDialog);

      for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
        args[_key] = arguments[_key];
      }

      _this = _super.call.apply(_super, [this].concat(args));

      _initialize(dialog_hassio_repositories_assertThisInitialized(_this));

      return _this;
    }

    return HassioRepositoriesDialog;
  }(_LitElement);

  return {
    F: HassioRepositoriesDialog,
    d: [{
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])({
        attribute: false
      })],
      key: "hass",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])({
        attribute: false
      })],
      key: "_repos",
      value: function value() {
        return [];
      }
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])({
        attribute: false
      })],
      key: "_dialogParams",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["g" /* query */])("#repository_input")],
      key: "_optionInput",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "_opened",
      value: function value() {
        return false;
      }
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "_prosessing",
      value: function value() {
        return false;
      }
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "_error",
      value: void 0
    }, {
      kind: "method",
      key: "showDialog",
      value: function () {
        var _showDialog = _asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee(_dialogParams) {
          return regeneratorRuntime.wrap(function _callee$(_context) {
            while (1) {
              switch (_context.prev = _context.next) {
                case 0:
                  this._dialogParams = _dialogParams;
                  this._repos = _dialogParams.repos;
                  this._opened = true;
                  _context.next = 5;
                  return this.updateComplete;

                case 5:
                case "end":
                  return _context.stop();
              }
            }
          }, _callee, this);
        }));

        function showDialog(_x) {
          return _showDialog.apply(this, arguments);
        }

        return showDialog;
      }()
    }, {
      kind: "method",
      key: "closeDialog",
      value: function closeDialog() {
        this._opened = false;
        this._error = "";
      }
    }, {
      kind: "field",
      key: "_filteredRepositories",
      value: function value() {
        return Object(memoize_one_esm["a" /* default */])(function (repos) {
          return repos.filter(function (repo) {
            return repo.slug !== "core" && repo.slug !== "local";
          }).sort(function (a, b) {
            return a.name < b.name ? -1 : 1;
          });
        });
      }
    }, {
      kind: "method",
      key: "render",
      value: function render() {
        var _this2 = this;

        var repositories = this._filteredRepositories(this._repos);

        return Object(lit_element["e" /* html */])(dialog_hassio_repositories_templateObject(), this._opened, this.closeDialog, this._error ? Object(lit_element["e" /* html */])(dialog_hassio_repositories_templateObject2(), this._error) : "", repositories.length ? repositories.map(function (repo) {
          return Object(lit_element["e" /* html */])(_templateObject3(), repo.name, repo.maintainer, repo.url, repo.slug, _this2._removeRepository);
        }) : Object(lit_element["e" /* html */])(_templateObject4()), this._handleKeyAdd, this._addRepository, this._prosessing ? Object(lit_element["e" /* html */])(_templateObject5()) : "Add", this.closeDialog);
      }
    }, {
      kind: "get",
      "static": true,
      key: "styles",
      value: function styles() {
        return [resources_styles["b" /* haStyle */], resources_styles["c" /* haStyleDialog */], Object(lit_element["c" /* css */])(_templateObject6())];
      }
    }, {
      kind: "method",
      key: "focus",
      value: function focus() {
        var _this3 = this;

        this.updateComplete.then(function () {
          var _ref, _this3$shadowRoot;

          return (_ref = (_this3$shadowRoot = _this3.shadowRoot) === null || _this3$shadowRoot === void 0 ? void 0 : _this3$shadowRoot.querySelector("[dialogInitialFocus]")) === null || _ref === void 0 ? void 0 : _ref.focus();
        });
      }
    }, {
      kind: "method",
      key: "_handleKeyAdd",
      value: function _handleKeyAdd(ev) {
        ev.stopPropagation();

        if (ev.keyCode !== 13) {
          return;
        }

        this._addRepository();
      }
    }, {
      kind: "method",
      key: "_addRepository",
      value: function () {
        var _addRepository2 = _asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee2() {
          var input, repositories, newRepositories, addonsInfo;
          return regeneratorRuntime.wrap(function _callee2$(_context2) {
            while (1) {
              switch (_context2.prev = _context2.next) {
                case 0:
                  input = this._optionInput;

                  if (!(!input || !input.value)) {
                    _context2.next = 3;
                    break;
                  }

                  return _context2.abrupt("return");

                case 3:
                  this._prosessing = true;
                  repositories = this._filteredRepositories(this._repos);
                  newRepositories = repositories.map(function (repo) {
                    return repo.source;
                  });
                  newRepositories.push(input.value);
                  _context2.prev = 7;
                  _context2.next = 10;
                  return Object(supervisor["e" /* setSupervisorOption */])(this.hass, {
                    addons_repositories: newRepositories
                  });

                case 10:
                  _context2.next = 12;
                  return Object(addon["e" /* fetchHassioAddonsInfo */])(this.hass);

                case 12:
                  addonsInfo = _context2.sent;
                  this._repos = addonsInfo.repositories;
                  _context2.next = 16;
                  return this._dialogParams.loadData();

                case 16:
                  input.value = "";
                  _context2.next = 22;
                  break;

                case 19:
                  _context2.prev = 19;
                  _context2.t0 = _context2["catch"](7);
                  this._error = _context2.t0.message;

                case 22:
                  this._prosessing = false;

                case 23:
                case "end":
                  return _context2.stop();
              }
            }
          }, _callee2, this, [[7, 19]]);
        }));

        function _addRepository() {
          return _addRepository2.apply(this, arguments);
        }

        return _addRepository;
      }()
    }, {
      kind: "method",
      key: "_removeRepository",
      value: function () {
        var _removeRepository2 = _asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee3(ev) {
          var slug, repositories, repository, newRepositories, addonsInfo;
          return regeneratorRuntime.wrap(function _callee3$(_context3) {
            while (1) {
              switch (_context3.prev = _context3.next) {
                case 0:
                  slug = ev.target.slug;
                  repositories = this._filteredRepositories(this._repos);
                  repository = repositories.find(function (repo) {
                    return repo.slug === slug;
                  });

                  if (repository) {
                    _context3.next = 5;
                    break;
                  }

                  return _context3.abrupt("return");

                case 5:
                  newRepositories = repositories.map(function (repo) {
                    return repo.source;
                  }).filter(function (repo) {
                    return repo !== repository.source;
                  });
                  _context3.prev = 6;
                  _context3.next = 9;
                  return Object(supervisor["e" /* setSupervisorOption */])(this.hass, {
                    addons_repositories: newRepositories
                  });

                case 9:
                  _context3.next = 11;
                  return Object(addon["e" /* fetchHassioAddonsInfo */])(this.hass);

                case 11:
                  addonsInfo = _context3.sent;
                  this._repos = addonsInfo.repositories;
                  _context3.next = 15;
                  return this._dialogParams.loadData();

                case 15:
                  _context3.next = 20;
                  break;

                case 17:
                  _context3.prev = 17;
                  _context3.t0 = _context3["catch"](6);
                  this._error = _context3.t0.message;

                case 20:
                case "end":
                  return _context3.stop();
              }
            }
          }, _callee3, this, [[6, 17]]);
        }));

        function _removeRepository(_x2) {
          return _removeRepository2.apply(this, arguments);
        }

        return _removeRepository;
      }()
    }]
  };
}, lit_element["a" /* LitElement */]);

/***/ }),

/***/ 22:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "g", function() { return reloadHassioAddons; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "e", function() { return fetchHassioAddonsInfo; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "c", function() { return fetchHassioAddonInfo; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "a", function() { return fetchHassioAddonChangelog; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "d", function() { return fetchHassioAddonLogs; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "b", function() { return fetchHassioAddonDocumentation; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "i", function() { return setHassioAddonOption; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "j", function() { return setHassioAddonSecurity; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "f", function() { return installHassioAddon; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "h", function() { return restartHassioAddon; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "k", function() { return uninstallHassioAddon; });
/* harmony import */ var _common__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(48);
function asyncGeneratorStep(gen, resolve, reject, _next, _throw, key, arg) { try { var info = gen[key](arg); var value = info.value; } catch (error) { reject(error); return; } if (info.done) { resolve(value); } else { Promise.resolve(value).then(_next, _throw); } }

function _asyncToGenerator(fn) { return function () { var self = this, args = arguments; return new Promise(function (resolve, reject) { var gen = fn.apply(self, args); function _next(value) { asyncGeneratorStep(gen, resolve, reject, _next, _throw, "next", value); } function _throw(err) { asyncGeneratorStep(gen, resolve, reject, _next, _throw, "throw", err); } _next(undefined); }); }; }


var reloadHassioAddons = /*#__PURE__*/function () {
  var _ref = _asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee(hass) {
    return regeneratorRuntime.wrap(function _callee$(_context) {
      while (1) {
        switch (_context.prev = _context.next) {
          case 0:
            _context.next = 2;
            return hass.callApi("POST", "hassio/addons/reload");

          case 2:
          case "end":
            return _context.stop();
        }
      }
    }, _callee);
  }));

  return function reloadHassioAddons(_x) {
    return _ref.apply(this, arguments);
  };
}();
var fetchHassioAddonsInfo = /*#__PURE__*/function () {
  var _ref2 = _asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee2(hass) {
    return regeneratorRuntime.wrap(function _callee2$(_context2) {
      while (1) {
        switch (_context2.prev = _context2.next) {
          case 0:
            _context2.t0 = _common__WEBPACK_IMPORTED_MODULE_0__[/* hassioApiResultExtractor */ "a"];
            _context2.next = 3;
            return hass.callApi("GET", "hassio/addons");

          case 3:
            _context2.t1 = _context2.sent;
            return _context2.abrupt("return", (0, _context2.t0)(_context2.t1));

          case 5:
          case "end":
            return _context2.stop();
        }
      }
    }, _callee2);
  }));

  return function fetchHassioAddonsInfo(_x2) {
    return _ref2.apply(this, arguments);
  };
}();
var fetchHassioAddonInfo = /*#__PURE__*/function () {
  var _ref3 = _asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee3(hass, slug) {
    return regeneratorRuntime.wrap(function _callee3$(_context3) {
      while (1) {
        switch (_context3.prev = _context3.next) {
          case 0:
            _context3.t0 = _common__WEBPACK_IMPORTED_MODULE_0__[/* hassioApiResultExtractor */ "a"];
            _context3.next = 3;
            return hass.callApi("GET", "hassio/addons/".concat(slug, "/info"));

          case 3:
            _context3.t1 = _context3.sent;
            return _context3.abrupt("return", (0, _context3.t0)(_context3.t1));

          case 5:
          case "end":
            return _context3.stop();
        }
      }
    }, _callee3);
  }));

  return function fetchHassioAddonInfo(_x3, _x4) {
    return _ref3.apply(this, arguments);
  };
}();
var fetchHassioAddonChangelog = /*#__PURE__*/function () {
  var _ref4 = _asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee4(hass, slug) {
    return regeneratorRuntime.wrap(function _callee4$(_context4) {
      while (1) {
        switch (_context4.prev = _context4.next) {
          case 0:
            return _context4.abrupt("return", hass.callApi("GET", "hassio/addons/".concat(slug, "/changelog")));

          case 1:
          case "end":
            return _context4.stop();
        }
      }
    }, _callee4);
  }));

  return function fetchHassioAddonChangelog(_x5, _x6) {
    return _ref4.apply(this, arguments);
  };
}();
var fetchHassioAddonLogs = /*#__PURE__*/function () {
  var _ref5 = _asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee5(hass, slug) {
    return regeneratorRuntime.wrap(function _callee5$(_context5) {
      while (1) {
        switch (_context5.prev = _context5.next) {
          case 0:
            return _context5.abrupt("return", hass.callApi("GET", "hassio/addons/".concat(slug, "/logs")));

          case 1:
          case "end":
            return _context5.stop();
        }
      }
    }, _callee5);
  }));

  return function fetchHassioAddonLogs(_x7, _x8) {
    return _ref5.apply(this, arguments);
  };
}();
var fetchHassioAddonDocumentation = /*#__PURE__*/function () {
  var _ref6 = _asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee6(hass, slug) {
    return regeneratorRuntime.wrap(function _callee6$(_context6) {
      while (1) {
        switch (_context6.prev = _context6.next) {
          case 0:
            return _context6.abrupt("return", hass.callApi("GET", "hassio/addons/".concat(slug, "/documentation")));

          case 1:
          case "end":
            return _context6.stop();
        }
      }
    }, _callee6);
  }));

  return function fetchHassioAddonDocumentation(_x9, _x10) {
    return _ref6.apply(this, arguments);
  };
}();
var setHassioAddonOption = /*#__PURE__*/function () {
  var _ref7 = _asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee7(hass, slug, data) {
    return regeneratorRuntime.wrap(function _callee7$(_context7) {
      while (1) {
        switch (_context7.prev = _context7.next) {
          case 0:
            _context7.next = 2;
            return hass.callApi("POST", "hassio/addons/".concat(slug, "/options"), data);

          case 2:
          case "end":
            return _context7.stop();
        }
      }
    }, _callee7);
  }));

  return function setHassioAddonOption(_x11, _x12, _x13) {
    return _ref7.apply(this, arguments);
  };
}();
var setHassioAddonSecurity = /*#__PURE__*/function () {
  var _ref8 = _asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee8(hass, slug, data) {
    return regeneratorRuntime.wrap(function _callee8$(_context8) {
      while (1) {
        switch (_context8.prev = _context8.next) {
          case 0:
            _context8.next = 2;
            return hass.callApi("POST", "hassio/addons/".concat(slug, "/security"), data);

          case 2:
          case "end":
            return _context8.stop();
        }
      }
    }, _callee8);
  }));

  return function setHassioAddonSecurity(_x14, _x15, _x16) {
    return _ref8.apply(this, arguments);
  };
}();
var installHassioAddon = /*#__PURE__*/function () {
  var _ref9 = _asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee9(hass, slug) {
    return regeneratorRuntime.wrap(function _callee9$(_context9) {
      while (1) {
        switch (_context9.prev = _context9.next) {
          case 0:
            return _context9.abrupt("return", hass.callApi("POST", "hassio/addons/".concat(slug, "/install")));

          case 1:
          case "end":
            return _context9.stop();
        }
      }
    }, _callee9);
  }));

  return function installHassioAddon(_x17, _x18) {
    return _ref9.apply(this, arguments);
  };
}();
var restartHassioAddon = /*#__PURE__*/function () {
  var _ref10 = _asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee10(hass, slug) {
    return regeneratorRuntime.wrap(function _callee10$(_context10) {
      while (1) {
        switch (_context10.prev = _context10.next) {
          case 0:
            return _context10.abrupt("return", hass.callApi("POST", "hassio/addons/".concat(slug, "/restart")));

          case 1:
          case "end":
            return _context10.stop();
        }
      }
    }, _callee10);
  }));

  return function restartHassioAddon(_x19, _x20) {
    return _ref10.apply(this, arguments);
  };
}();
var uninstallHassioAddon = /*#__PURE__*/function () {
  var _ref11 = _asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee11(hass, slug) {
    return regeneratorRuntime.wrap(function _callee11$(_context11) {
      while (1) {
        switch (_context11.prev = _context11.next) {
          case 0:
            _context11.next = 2;
            return hass.callApi("POST", "hassio/addons/".concat(slug, "/uninstall"));

          case 2:
          case "end":
            return _context11.stop();
        }
      }
    }, _callee11);
  }));

  return function uninstallHassioAddon(_x21, _x22) {
    return _ref11.apply(this, arguments);
  };
}();

/***/ }),

/***/ 23:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "a", function() { return HaIconButton; });
/* harmony import */ var _material_mwc_icon_button__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(184);
/* harmony import */ var lit_element__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(5);
/* harmony import */ var _ha_icon__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(32);
function _typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { _typeof = function _typeof(obj) { return typeof obj; }; } else { _typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return _typeof(obj); }

function _templateObject2() {
  var data = _taggedTemplateLiteral(["\n      :host {\n        display: inline-block;\n        outline: none;\n      }\n      mwc-icon-button {\n        --mdc-theme-on-primary: currentColor;\n      }\n      ha-icon {\n        --ha-icon-display: inline;\n      }\n    "]);

  _templateObject2 = function _templateObject2() {
    return data;
  };

  return data;
}

function _templateObject() {
  var data = _taggedTemplateLiteral(["\n      <mwc-icon-button\n        .label=", "\n        ?disabled=", "\n        @click=", "\n      >\n        <ha-icon .icon=", "></ha-icon>\n      </mwc-icon-button>\n    "]);

  _templateObject = function _templateObject() {
    return data;
  };

  return data;
}

function _taggedTemplateLiteral(strings, raw) { if (!raw) { raw = strings.slice(0); } return Object.freeze(Object.defineProperties(strings, { raw: { value: Object.freeze(raw) } })); }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) _setPrototypeOf(subClass, superClass); }

function _setPrototypeOf(o, p) { _setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return _setPrototypeOf(o, p); }

function _createSuper(Derived) { return function () { var Super = _getPrototypeOf(Derived), result; if (_isNativeReflectConstruct()) { var NewTarget = _getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return _possibleConstructorReturn(this, result); }; }

function _possibleConstructorReturn(self, call) { if (call && (_typeof(call) === "object" || typeof call === "function")) { return call; } return _assertThisInitialized(self); }

function _assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function _isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Date.prototype.toString.call(Reflect.construct(Date, [], function () {})); return true; } catch (e) { return false; } }

function _getPrototypeOf(o) { _getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return _getPrototypeOf(o); }

function _decorate(decorators, factory, superClass, mixins) { var api = _getDecoratorsApi(); if (mixins) { for (var i = 0; i < mixins.length; i++) { api = mixins[i](api); } } var r = factory(function initialize(O) { api.initializeInstanceElements(O, decorated.elements); }, superClass); var decorated = api.decorateClass(_coalesceClassElements(r.d.map(_createElementDescriptor)), decorators); api.initializeClassElements(r.F, decorated.elements); return api.runClassFinishers(r.F, decorated.finishers); }

function _getDecoratorsApi() { _getDecoratorsApi = function _getDecoratorsApi() { return api; }; var api = { elementsDefinitionOrder: [["method"], ["field"]], initializeInstanceElements: function initializeInstanceElements(O, elements) { ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { if (element.kind === kind && element.placement === "own") { this.defineClassElement(O, element); } }, this); }, this); }, initializeClassElements: function initializeClassElements(F, elements) { var proto = F.prototype; ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { var placement = element.placement; if (element.kind === kind && (placement === "static" || placement === "prototype")) { var receiver = placement === "static" ? F : proto; this.defineClassElement(receiver, element); } }, this); }, this); }, defineClassElement: function defineClassElement(receiver, element) { var descriptor = element.descriptor; if (element.kind === "field") { var initializer = element.initializer; descriptor = { enumerable: descriptor.enumerable, writable: descriptor.writable, configurable: descriptor.configurable, value: initializer === void 0 ? void 0 : initializer.call(receiver) }; } Object.defineProperty(receiver, element.key, descriptor); }, decorateClass: function decorateClass(elements, decorators) { var newElements = []; var finishers = []; var placements = { "static": [], prototype: [], own: [] }; elements.forEach(function (element) { this.addElementPlacement(element, placements); }, this); elements.forEach(function (element) { if (!_hasDecorators(element)) return newElements.push(element); var elementFinishersExtras = this.decorateElement(element, placements); newElements.push(elementFinishersExtras.element); newElements.push.apply(newElements, elementFinishersExtras.extras); finishers.push.apply(finishers, elementFinishersExtras.finishers); }, this); if (!decorators) { return { elements: newElements, finishers: finishers }; } var result = this.decorateConstructor(newElements, decorators); finishers.push.apply(finishers, result.finishers); result.finishers = finishers; return result; }, addElementPlacement: function addElementPlacement(element, placements, silent) { var keys = placements[element.placement]; if (!silent && keys.indexOf(element.key) !== -1) { throw new TypeError("Duplicated element (" + element.key + ")"); } keys.push(element.key); }, decorateElement: function decorateElement(element, placements) { var extras = []; var finishers = []; for (var decorators = element.decorators, i = decorators.length - 1; i >= 0; i--) { var keys = placements[element.placement]; keys.splice(keys.indexOf(element.key), 1); var elementObject = this.fromElementDescriptor(element); var elementFinisherExtras = this.toElementFinisherExtras((0, decorators[i])(elementObject) || elementObject); element = elementFinisherExtras.element; this.addElementPlacement(element, placements); if (elementFinisherExtras.finisher) { finishers.push(elementFinisherExtras.finisher); } var newExtras = elementFinisherExtras.extras; if (newExtras) { for (var j = 0; j < newExtras.length; j++) { this.addElementPlacement(newExtras[j], placements); } extras.push.apply(extras, newExtras); } } return { element: element, finishers: finishers, extras: extras }; }, decorateConstructor: function decorateConstructor(elements, decorators) { var finishers = []; for (var i = decorators.length - 1; i >= 0; i--) { var obj = this.fromClassDescriptor(elements); var elementsAndFinisher = this.toClassDescriptor((0, decorators[i])(obj) || obj); if (elementsAndFinisher.finisher !== undefined) { finishers.push(elementsAndFinisher.finisher); } if (elementsAndFinisher.elements !== undefined) { elements = elementsAndFinisher.elements; for (var j = 0; j < elements.length - 1; j++) { for (var k = j + 1; k < elements.length; k++) { if (elements[j].key === elements[k].key && elements[j].placement === elements[k].placement) { throw new TypeError("Duplicated element (" + elements[j].key + ")"); } } } } } return { elements: elements, finishers: finishers }; }, fromElementDescriptor: function fromElementDescriptor(element) { var obj = { kind: element.kind, key: element.key, placement: element.placement, descriptor: element.descriptor }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); if (element.kind === "field") obj.initializer = element.initializer; return obj; }, toElementDescriptors: function toElementDescriptors(elementObjects) { if (elementObjects === undefined) return; return _toArray(elementObjects).map(function (elementObject) { var element = this.toElementDescriptor(elementObject); this.disallowProperty(elementObject, "finisher", "An element descriptor"); this.disallowProperty(elementObject, "extras", "An element descriptor"); return element; }, this); }, toElementDescriptor: function toElementDescriptor(elementObject) { var kind = String(elementObject.kind); if (kind !== "method" && kind !== "field") { throw new TypeError('An element descriptor\'s .kind property must be either "method" or' + ' "field", but a decorator created an element descriptor with' + ' .kind "' + kind + '"'); } var key = _toPropertyKey(elementObject.key); var placement = String(elementObject.placement); if (placement !== "static" && placement !== "prototype" && placement !== "own") { throw new TypeError('An element descriptor\'s .placement property must be one of "static",' + ' "prototype" or "own", but a decorator created an element descriptor' + ' with .placement "' + placement + '"'); } var descriptor = elementObject.descriptor; this.disallowProperty(elementObject, "elements", "An element descriptor"); var element = { kind: kind, key: key, placement: placement, descriptor: Object.assign({}, descriptor) }; if (kind !== "field") { this.disallowProperty(elementObject, "initializer", "A method descriptor"); } else { this.disallowProperty(descriptor, "get", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "set", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "value", "The property descriptor of a field descriptor"); element.initializer = elementObject.initializer; } return element; }, toElementFinisherExtras: function toElementFinisherExtras(elementObject) { var element = this.toElementDescriptor(elementObject); var finisher = _optionalCallableProperty(elementObject, "finisher"); var extras = this.toElementDescriptors(elementObject.extras); return { element: element, finisher: finisher, extras: extras }; }, fromClassDescriptor: function fromClassDescriptor(elements) { var obj = { kind: "class", elements: elements.map(this.fromElementDescriptor, this) }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); return obj; }, toClassDescriptor: function toClassDescriptor(obj) { var kind = String(obj.kind); if (kind !== "class") { throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator' + ' created a class descriptor with .kind "' + kind + '"'); } this.disallowProperty(obj, "key", "A class descriptor"); this.disallowProperty(obj, "placement", "A class descriptor"); this.disallowProperty(obj, "descriptor", "A class descriptor"); this.disallowProperty(obj, "initializer", "A class descriptor"); this.disallowProperty(obj, "extras", "A class descriptor"); var finisher = _optionalCallableProperty(obj, "finisher"); var elements = this.toElementDescriptors(obj.elements); return { elements: elements, finisher: finisher }; }, runClassFinishers: function runClassFinishers(constructor, finishers) { for (var i = 0; i < finishers.length; i++) { var newConstructor = (0, finishers[i])(constructor); if (newConstructor !== undefined) { if (typeof newConstructor !== "function") { throw new TypeError("Finishers must return a constructor."); } constructor = newConstructor; } } return constructor; }, disallowProperty: function disallowProperty(obj, name, objectType) { if (obj[name] !== undefined) { throw new TypeError(objectType + " can't have a ." + name + " property."); } } }; return api; }

function _createElementDescriptor(def) { var key = _toPropertyKey(def.key); var descriptor; if (def.kind === "method") { descriptor = { value: def.value, writable: true, configurable: true, enumerable: false }; } else if (def.kind === "get") { descriptor = { get: def.value, configurable: true, enumerable: false }; } else if (def.kind === "set") { descriptor = { set: def.value, configurable: true, enumerable: false }; } else if (def.kind === "field") { descriptor = { configurable: true, writable: true, enumerable: true }; } var element = { kind: def.kind === "field" ? "field" : "method", key: key, placement: def["static"] ? "static" : def.kind === "field" ? "own" : "prototype", descriptor: descriptor }; if (def.decorators) element.decorators = def.decorators; if (def.kind === "field") element.initializer = def.value; return element; }

function _coalesceGetterSetter(element, other) { if (element.descriptor.get !== undefined) { other.descriptor.get = element.descriptor.get; } else { other.descriptor.set = element.descriptor.set; } }

function _coalesceClassElements(elements) { var newElements = []; var isSameElement = function isSameElement(other) { return other.kind === "method" && other.key === element.key && other.placement === element.placement; }; for (var i = 0; i < elements.length; i++) { var element = elements[i]; var other; if (element.kind === "method" && (other = newElements.find(isSameElement))) { if (_isDataDescriptor(element.descriptor) || _isDataDescriptor(other.descriptor)) { if (_hasDecorators(element) || _hasDecorators(other)) { throw new ReferenceError("Duplicated methods (" + element.key + ") can't be decorated."); } other.descriptor = element.descriptor; } else { if (_hasDecorators(element)) { if (_hasDecorators(other)) { throw new ReferenceError("Decorators can't be placed on different accessors with for " + "the same property (" + element.key + ")."); } other.decorators = element.decorators; } _coalesceGetterSetter(element, other); } } else { newElements.push(element); } } return newElements; }

function _hasDecorators(element) { return element.decorators && element.decorators.length; }

function _isDataDescriptor(desc) { return desc !== undefined && !(desc.value === undefined && desc.writable === undefined); }

function _optionalCallableProperty(obj, name) { var value = obj[name]; if (value !== undefined && typeof value !== "function") { throw new TypeError("Expected '" + name + "' to be a function"); } return value; }

function _toPropertyKey(arg) { var key = _toPrimitive(arg, "string"); return _typeof(key) === "symbol" ? key : String(key); }

function _toPrimitive(input, hint) { if (_typeof(input) !== "object" || input === null) return input; var prim = input[Symbol.toPrimitive]; if (prim !== undefined) { var res = prim.call(input, hint || "default"); if (_typeof(res) !== "object") return res; throw new TypeError("@@toPrimitive must return a primitive value."); } return (hint === "string" ? String : Number)(input); }

function _toArray(arr) { return _arrayWithHoles(arr) || _iterableToArray(arr) || _unsupportedIterableToArray(arr) || _nonIterableRest(); }

function _nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function _unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return _arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(n); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return _arrayLikeToArray(o, minLen); }

function _arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function _iterableToArray(iter) { if (typeof Symbol !== "undefined" && Symbol.iterator in Object(iter)) return Array.from(iter); }

function _arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }




var HaIconButton = _decorate([Object(lit_element__WEBPACK_IMPORTED_MODULE_1__[/* customElement */ "d"])("ha-icon-button")], function (_initialize, _LitElement) {
  var HaIconButton = /*#__PURE__*/function (_LitElement2) {
    _inherits(HaIconButton, _LitElement2);

    var _super = _createSuper(HaIconButton);

    function HaIconButton() {
      var _this;

      _classCallCheck(this, HaIconButton);

      for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
        args[_key] = arguments[_key];
      }

      _this = _super.call.apply(_super, [this].concat(args));

      _initialize(_assertThisInitialized(_this));

      return _this;
    }

    return HaIconButton;
  }(_LitElement);

  return {
    F: HaIconButton,
    d: [{
      kind: "field",
      decorators: [Object(lit_element__WEBPACK_IMPORTED_MODULE_1__[/* property */ "f"])({
        type: Boolean,
        reflect: true
      })],
      key: "disabled",
      value: function value() {
        return false;
      }
    }, {
      kind: "field",
      decorators: [Object(lit_element__WEBPACK_IMPORTED_MODULE_1__[/* property */ "f"])({
        type: String
      })],
      key: "icon",
      value: function value() {
        return "";
      }
    }, {
      kind: "field",
      decorators: [Object(lit_element__WEBPACK_IMPORTED_MODULE_1__[/* property */ "f"])({
        type: String
      })],
      key: "label",
      value: function value() {
        return "";
      }
    }, {
      kind: "method",
      key: "createRenderRoot",
      value: function createRenderRoot() {
        return this.attachShadow({
          mode: "open",
          delegatesFocus: true
        });
      }
    }, {
      kind: "method",
      key: "render",
      value: function render() {
        return Object(lit_element__WEBPACK_IMPORTED_MODULE_1__[/* html */ "e"])(_templateObject(), this.label || this.icon, this.disabled, this._handleClick, this.icon);
      }
    }, {
      kind: "method",
      key: "_handleClick",
      value: function _handleClick(ev) {
        if (this.disabled) {
          ev.stopPropagation();
        }
      }
    }, {
      kind: "get",
      "static": true,
      key: "styles",
      value: function styles() {
        return Object(lit_element__WEBPACK_IMPORTED_MODULE_1__[/* css */ "c"])(_templateObject2());
      }
    }]
  };
}, lit_element__WEBPACK_IMPORTED_MODULE_1__[/* LitElement */ "a"]);

/***/ }),

/***/ 3:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);

// EXTERNAL MODULE: ./src/components/ha-icon-button.ts
var ha_icon_button = __webpack_require__(23);

// EXTERNAL MODULE: ./node_modules/lit-element/lit-element.js + 3 modules
var lit_element = __webpack_require__(5);

// EXTERNAL MODULE: ./src/resources/styles.ts
var resources_styles = __webpack_require__(11);

// CONCATENATED MODULE: ./src/common/dom/apply_themes_on_element.ts


var hexToRgb = function hexToRgb(hex) {
  var shorthandRegex = /^#?([a-f\d])([a-f\d])([a-f\d])$/i;
  var checkHex = hex.replace(shorthandRegex, function (_m, r, g, b) {
    return r + r + g + g + b + b;
  });
  var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(checkHex);
  return result ? "".concat(parseInt(result[1], 16), ", ").concat(parseInt(result[2], 16), ", ").concat(parseInt(result[3], 16)) : null;
};

var PROCESSED_THEMES = {};
/**
 * Apply a theme to an element by setting the CSS variables on it.
 *
 * element: Element to apply theme on.
 * themes: HASS Theme information
 * selectedTheme: selected theme.
 */

var applyThemesOnElement = function applyThemesOnElement(element, themes, selectedTheme) {
  var newTheme = selectedTheme ? PROCESSED_THEMES[selectedTheme] || apply_themes_on_element_processTheme(selectedTheme, themes) : undefined;

  if (!element._themes && !newTheme) {
    // No styles to reset, and no styles to set
    return;
  } // Add previous set keys to reset them, and new theme


  var styles = Object.assign({}, element._themes, {}, newTheme === null || newTheme === void 0 ? void 0 : newTheme.styles);
  element._themes = newTheme === null || newTheme === void 0 ? void 0 : newTheme.keys; // Set and/or reset styles

  if (element.updateStyles) {
    element.updateStyles(styles);
  } else if (window.ShadyCSS) {
    // Implement updateStyles() method of Polymer elements
    window.ShadyCSS.styleSubtree(
    /** @type {!HTMLElement} */
    element, styles);
  }
};

var apply_themes_on_element_processTheme = function processTheme(themeName, themes) {
  if (!themes.themes[themeName]) {
    return undefined;
  }

  var theme = Object.assign({}, resources_styles["a" /* derivedStyles */], {}, themes.themes[themeName]);
  var styles = {};
  var keys = {};

  for (var _i = 0, _Object$keys = Object.keys(theme); _i < _Object$keys.length; _i++) {
    var _key = _Object$keys[_i];
    var prefixedKey = "--".concat(_key);
    var value = theme[_key];
    styles[prefixedKey] = value;
    keys[prefixedKey] = ""; // Try to create a rgb value for this key if it is a hex color

    if (!value.startsWith("#")) {
      // Not a hex color
      continue;
    }

    var rgbKey = "rgb-".concat(_key);

    if (theme[rgbKey] !== undefined) {
      // Theme has it's own rgb value
      continue;
    }

    var rgbValue = hexToRgb(value);

    if (rgbValue !== null) {
      var prefixedRgbKey = "--".concat(rgbKey);
      styles[prefixedRgbKey] = rgbValue;
      keys[prefixedRgbKey] = "";
    }
  }

  PROCESSED_THEMES[themeName] = {
    styles: styles,
    keys: keys
  };
  return {
    styles: styles,
    keys: keys
  };
};

var invalidateThemeCache = function invalidateThemeCache() {
  PROCESSED_THEMES = {};
};
// EXTERNAL MODULE: ./src/common/dom/fire_event.ts
var fire_event = __webpack_require__(12);

// EXTERNAL MODULE: ./src/common/navigate.ts
var common_navigate = __webpack_require__(38);

// EXTERNAL MODULE: ./src/data/hassio/addon.ts
var hassio_addon = __webpack_require__(22);

// EXTERNAL MODULE: ./src/data/hassio/common.ts
var common = __webpack_require__(48);

// CONCATENATED MODULE: ./src/data/hassio/host.ts
function asyncGeneratorStep(gen, resolve, reject, _next, _throw, key, arg) { try { var info = gen[key](arg); var value = info.value; } catch (error) { reject(error); return; } if (info.done) { resolve(value); } else { Promise.resolve(value).then(_next, _throw); } }

function _asyncToGenerator(fn) { return function () { var self = this, args = arguments; return new Promise(function (resolve, reject) { var gen = fn.apply(self, args); function _next(value) { asyncGeneratorStep(gen, resolve, reject, _next, _throw, "next", value); } function _throw(err) { asyncGeneratorStep(gen, resolve, reject, _next, _throw, "throw", err); } _next(undefined); }); }; }


var fetchHassioHostInfo = /*#__PURE__*/function () {
  var _ref = _asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee(hass) {
    var response;
    return regeneratorRuntime.wrap(function _callee$(_context) {
      while (1) {
        switch (_context.prev = _context.next) {
          case 0:
            _context.next = 2;
            return hass.callApi("GET", "hassio/host/info");

          case 2:
            response = _context.sent;
            return _context.abrupt("return", Object(common["a" /* hassioApiResultExtractor */])(response));

          case 4:
          case "end":
            return _context.stop();
        }
      }
    }, _callee);
  }));

  return function fetchHassioHostInfo(_x) {
    return _ref.apply(this, arguments);
  };
}();
var fetchHassioHassOsInfo = /*#__PURE__*/function () {
  var _ref2 = _asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee2(hass) {
    return regeneratorRuntime.wrap(function _callee2$(_context2) {
      while (1) {
        switch (_context2.prev = _context2.next) {
          case 0:
            _context2.t0 = common["a" /* hassioApiResultExtractor */];
            _context2.next = 3;
            return hass.callApi("GET", "hassio/os/info");

          case 3:
            _context2.t1 = _context2.sent;
            return _context2.abrupt("return", (0, _context2.t0)(_context2.t1));

          case 5:
          case "end":
            return _context2.stop();
        }
      }
    }, _callee2);
  }));

  return function fetchHassioHassOsInfo(_x2) {
    return _ref2.apply(this, arguments);
  };
}();
var rebootHost = /*#__PURE__*/function () {
  var _ref3 = _asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee3(hass) {
    return regeneratorRuntime.wrap(function _callee3$(_context3) {
      while (1) {
        switch (_context3.prev = _context3.next) {
          case 0:
            return _context3.abrupt("return", hass.callApi("POST", "hassio/host/reboot"));

          case 1:
          case "end":
            return _context3.stop();
        }
      }
    }, _callee3);
  }));

  return function rebootHost(_x3) {
    return _ref3.apply(this, arguments);
  };
}();
var shutdownHost = /*#__PURE__*/function () {
  var _ref4 = _asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee4(hass) {
    return regeneratorRuntime.wrap(function _callee4$(_context4) {
      while (1) {
        switch (_context4.prev = _context4.next) {
          case 0:
            return _context4.abrupt("return", hass.callApi("POST", "hassio/host/shutdown"));

          case 1:
          case "end":
            return _context4.stop();
        }
      }
    }, _callee4);
  }));

  return function shutdownHost(_x4) {
    return _ref4.apply(this, arguments);
  };
}();
var updateOS = /*#__PURE__*/function () {
  var _ref5 = _asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee5(hass) {
    return regeneratorRuntime.wrap(function _callee5$(_context5) {
      while (1) {
        switch (_context5.prev = _context5.next) {
          case 0:
            return _context5.abrupt("return", hass.callApi("POST", "hassio/os/update"));

          case 1:
          case "end":
            return _context5.stop();
        }
      }
    }, _callee5);
  }));

  return function updateOS(_x5) {
    return _ref5.apply(this, arguments);
  };
}();
var changeHostOptions = /*#__PURE__*/function () {
  var _ref6 = _asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee6(hass, options) {
    return regeneratorRuntime.wrap(function _callee6$(_context6) {
      while (1) {
        switch (_context6.prev = _context6.next) {
          case 0:
            return _context6.abrupt("return", hass.callApi("POST", "hassio/host/options", options));

          case 1:
          case "end":
            return _context6.stop();
        }
      }
    }, _callee6);
  }));

  return function changeHostOptions(_x6, _x7) {
    return _ref6.apply(this, arguments);
  };
}();
// EXTERNAL MODULE: ./src/data/hassio/supervisor.ts
var supervisor = __webpack_require__(49);

// EXTERNAL MODULE: ./src/dialogs/generic/show-dialog-box.ts
var show_dialog_box = __webpack_require__(39);

// CONCATENATED MODULE: ./src/dialogs/make-dialog-manager.ts
function make_dialog_manager_asyncGeneratorStep(gen, resolve, reject, _next, _throw, key, arg) { try { var info = gen[key](arg); var value = info.value; } catch (error) { reject(error); return; } if (info.done) { resolve(value); } else { Promise.resolve(value).then(_next, _throw); } }

function make_dialog_manager_asyncToGenerator(fn) { return function () { var self = this, args = arguments; return new Promise(function (resolve, reject) { var gen = fn.apply(self, args); function _next(value) { make_dialog_manager_asyncGeneratorStep(gen, resolve, reject, _next, _throw, "next", value); } function _throw(err) { make_dialog_manager_asyncGeneratorStep(gen, resolve, reject, _next, _throw, "throw", err); } _next(undefined); }); }; }

var LOADED = {};
var showDialog = /*#__PURE__*/function () {
  var _ref = make_dialog_manager_asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee(element, root, dialogImport, dialogTag, dialogParams) {
    var dialogElement;
    return regeneratorRuntime.wrap(function _callee$(_context) {
      while (1) {
        switch (_context.prev = _context.next) {
          case 0:
            if (!(dialogTag in LOADED)) {
              LOADED[dialogTag] = dialogImport().then(function () {
                var dialogEl = document.createElement(dialogTag);
                element.provideHass(dialogEl);
                root.appendChild(dialogEl);
                return dialogEl;
              });
            }

            _context.next = 3;
            return LOADED[dialogTag];

          case 3:
            dialogElement = _context.sent;
            dialogElement.showDialog(dialogParams);

          case 5:
          case "end":
            return _context.stop();
        }
      }
    }, _callee);
  }));

  return function showDialog(_x, _x2, _x3, _x4, _x5) {
    return _ref.apply(this, arguments);
  };
}();
var makeDialogManager = function makeDialogManager(element, root) {
  element.addEventListener("show-dialog", /*#__PURE__*/function () {
    var _ref2 = make_dialog_manager_asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee2(e) {
      var _e$detail, dialogTag, dialogImport, dialogParams;

      return regeneratorRuntime.wrap(function _callee2$(_context2) {
        while (1) {
          switch (_context2.prev = _context2.next) {
            case 0:
              _e$detail = e.detail, dialogTag = _e$detail.dialogTag, dialogImport = _e$detail.dialogImport, dialogParams = _e$detail.dialogParams;
              showDialog(element, root, dialogImport, dialogTag, dialogParams);

            case 2:
            case "end":
              return _context2.stop();
          }
        }
      }, _callee2);
    }));

    return function (_x6) {
      return _ref2.apply(this, arguments);
    };
  }());
};
// EXTERNAL MODULE: ./src/layouts/hass-router-page.ts + 1 modules
var hass_router_page = __webpack_require__(101);

// CONCATENATED MODULE: ./src/mixins/provide-hass-lit-mixin.ts
function _typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { _typeof = function _typeof(obj) { return typeof obj; }; } else { _typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return _typeof(obj); }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } }

function _createClass(Constructor, protoProps, staticProps) { if (protoProps) _defineProperties(Constructor.prototype, protoProps); if (staticProps) _defineProperties(Constructor, staticProps); return Constructor; }

function _get(target, property, receiver) { if (typeof Reflect !== "undefined" && Reflect.get) { _get = Reflect.get; } else { _get = function _get(target, property, receiver) { var base = _superPropBase(target, property); if (!base) return; var desc = Object.getOwnPropertyDescriptor(base, property); if (desc.get) { return desc.get.call(receiver); } return desc.value; }; } return _get(target, property, receiver || target); }

function _superPropBase(object, property) { while (!Object.prototype.hasOwnProperty.call(object, property)) { object = _getPrototypeOf(object); if (object === null) break; } return object; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) _setPrototypeOf(subClass, superClass); }

function _setPrototypeOf(o, p) { _setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return _setPrototypeOf(o, p); }

function _createSuper(Derived) { return function () { var Super = _getPrototypeOf(Derived), result; if (_isNativeReflectConstruct()) { var NewTarget = _getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return _possibleConstructorReturn(this, result); }; }

function _possibleConstructorReturn(self, call) { if (call && (_typeof(call) === "object" || typeof call === "function")) { return call; } return _assertThisInitialized(self); }

function _assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function _isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Date.prototype.toString.call(Reflect.construct(Date, [], function () {})); return true; } catch (e) { return false; } }

function _getPrototypeOf(o) { _getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return _getPrototypeOf(o); }

function _defineProperty(obj, key, value) { if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }

var ProvideHassLitMixin = function ProvideHassLitMixin(superClass) {
  var _temp;

  return _temp = /*#__PURE__*/function (_superClass) {
    _inherits(_temp, _superClass);

    var _super = _createSuper(_temp);

    function _temp() {
      var _this;

      _classCallCheck(this, _temp);

      for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
        args[_key] = arguments[_key];
      }

      _this = _super.call.apply(_super, [this].concat(args));

      _defineProperty(_assertThisInitialized(_this), "hass", void 0);

      _defineProperty(_assertThisInitialized(_this), "__provideHass", []);

      return _this;
    }

    _createClass(_temp, [{
      key: "provideHass",
      value: function provideHass(el) {
        this.__provideHass.push(el);

        el.hass = this.hass;
      }
    }, {
      key: "updated",
      value: function updated(changedProps) {
        var _this2 = this;

        _get(_getPrototypeOf(_temp.prototype), "updated", this).call(this, changedProps);

        if (changedProps.has("hass")) {
          this.__provideHass.forEach(function (el) {
            el.hass = _this2.hass;
          });
        }
      }
    }]);

    return _temp;
  }(superClass), _temp;
};
// EXTERNAL MODULE: ./node_modules/@polymer/paper-styles/paper-styles.js
var paper_styles = __webpack_require__(144);

// EXTERNAL MODULE: ./node_modules/@polymer/polymer/lib/elements/custom-style.js + 1 modules
var custom_style = __webpack_require__(137);

// CONCATENATED MODULE: ./src/resources/ha-style.ts
function _slicedToArray(arr, i) { return _arrayWithHoles(arr) || _iterableToArrayLimit(arr, i) || _unsupportedIterableToArray(arr, i) || _nonIterableRest(); }

function _nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function _unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return _arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(n); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return _arrayLikeToArray(o, minLen); }

function _arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function _iterableToArrayLimit(arr, i) { if (typeof Symbol === "undefined" || !(Symbol.iterator in Object(arr))) return; var _arr = []; var _n = true; var _d = false; var _e = undefined; try { for (var _i = arr[Symbol.iterator](), _s; !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i["return"] != null) _i["return"](); } finally { if (_d) throw _e; } } return _arr; }

function _arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }




var documentContainer = document.createElement("template");
documentContainer.setAttribute("style", "display: none;");
documentContainer.innerHTML = "<custom-style>\n  <style>\n    /*\n      Home Assistant default styles.\n\n      In Polymer 2.0, default styles should to be set on the html selector.\n      (Setting all default styles only on body breaks shadyCSS polyfill.)\n      See: https://github.com/home-assistant/home-assistant-polymer/pull/901\n    */\n    html {\n      font-size: 14px;\n      height: 100vh;\n\n      /* text */\n      --primary-text-color: #212121;\n      --secondary-text-color: #727272;\n      --text-primary-color: #ffffff;\n      --disabled-text-color: #bdbdbd;\n\n      /* main interface colors */\n      --primary-color: #03a9f4;\n      --dark-primary-color: #0288d1;\n      --light-primary-color: #b3e5fC;\n      --accent-color: #ff9800;\n      --divider-color: rgba(0, 0, 0, .12);\n\n      --scrollbar-thumb-color: rgb(194, 194, 194);\n\n      --error-color: #db4437;\n\n      /* states and badges */\n      --state-icon-color: #44739e;\n      --state-icon-active-color: #FDD835;\n\n      /* background and sidebar */\n      --card-background-color: #ffffff;\n      --primary-background-color: #fafafa;\n      --secondary-background-color: #e5e5e5; /* behind the cards on state */\n\n      /* for label-badge */\n      --label-badge-red: #DF4C1E;\n      --label-badge-blue: #039be5;\n      --label-badge-green: #0DA035;\n      --label-badge-yellow: #f4b400;\n\n      /*\n        Paper-styles color.html dependency is stripped on build.\n        When a default paper-style color is used, it needs to be copied\n        from paper-styles/color.html to here.\n      */\n\n      --paper-grey-50: #fafafa; /* default for: --mwc-switch-unchecked-button-color */\n      --paper-grey-200: #eeeeee;  /* for ha-date-picker-style */\n      --paper-grey-500: #9e9e9e;  /* --label-badge-grey */\n\n      /* for paper-spinner */\n      --google-red-500: #db4437;\n      --google-blue-500: #4285f4;\n      --google-green-500: #0f9d58;\n      --google-yellow-500: #f4b400;\n\n      /* for paper-slider */\n      --paper-green-400: #66bb6a;\n      --paper-blue-400: #42a5f5;\n      --paper-orange-400: #ffa726;\n\n      /* opacity for dark text on a light background */\n      --dark-divider-opacity: 0.12;\n      --dark-disabled-opacity: 0.38; /* or hint text or icon */\n      --dark-secondary-opacity: 0.54;\n      --dark-primary-opacity: 0.87;\n\n      /* opacity for light text on a dark background */\n      --light-divider-opacity: 0.12;\n      --light-disabled-opacity: 0.3; /* or hint text or icon */\n      --light-secondary-opacity: 0.7;\n      --light-primary-opacity: 1.0;\n\n      /* set our slider style */\n      --ha-paper-slider-pin-font-size: 15px;\n\n      /* rgb */\n      --rgb-primary-color: 3, 169, 244;\n      --rgb-accent-color: 255, 152, 0;\n      --rgb-primary-text-color: 33, 33, 33;\n      --rgb-secondary-text-color: 114, 114, 114;\n      --rgb-text-primary-color: 255, 255, 255;\n\n      ".concat(Object.entries(resources_styles["a" /* derivedStyles */]).map(function (_ref) {
  var _ref2 = _slicedToArray(_ref, 2),
      key = _ref2[0],
      value = _ref2[1];

  return "--".concat(key, ": ").concat(value, ";");
}).join(""), "\n    }\n  </style>\n\n  <style shady-unscoped=\"\">\n    /*\n      prevent clipping of positioned elements in a small scrollable\n      force smooth scrolling if can scroll\n      use non-shady selectors so this only targets iOS 9\n      conditional mixin set in ha-style-dialog does not work with shadyCSS\n    */\n    paper-dialog-scrollable:not(.can-scroll) &gt; .scrollable {\n      -webkit-overflow-scrolling: auto !important;\n    }\n\n    paper-dialog-scrollable.can-scroll &gt; .scrollable {\n      -webkit-overflow-scrolling: touch !important;\n    }\n  </style>\n</custom-style><dom-module id=\"ha-style\">\n  <template>\n    <style>\n    ").concat(resources_styles["b" /* haStyle */].cssText, "\n    </style>\n  </template>\n</dom-module><dom-module id=\"ha-style-dialog\">\n  <template>\n    <style>\n      ").concat(resources_styles["c" /* haStyleDialog */].cssText, "\n    </style>\n  </template>\n</dom-module>");
document.head.appendChild(documentContainer.content);
// EXTERNAL MODULE: ./node_modules/lit-html/lit-html.js + 1 modules
var lit_html = __webpack_require__(6);

// EXTERNAL MODULE: ./src/layouts/loading-screen.ts
var loading_screen = __webpack_require__(89);

// EXTERNAL MODULE: ./src/layouts/hass-tabs-subpage.ts + 1 modules
var hass_tabs_subpage = __webpack_require__(58);

// EXTERNAL MODULE: ./node_modules/@polymer/paper-input/paper-input.js + 7 modules
var paper_input = __webpack_require__(43);

// EXTERNAL MODULE: ./node_modules/lit-html/directives/class-map.js
var class_map = __webpack_require__(26);

// EXTERNAL MODULE: ./src/components/ha-icon.ts + 3 modules
var ha_icon = __webpack_require__(32);

// CONCATENATED MODULE: ./src/common/search/search-input.ts
function search_input_typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { search_input_typeof = function _typeof(obj) { return typeof obj; }; } else { search_input_typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return search_input_typeof(obj); }

function _templateObject3() {
  var data = _taggedTemplateLiteral(["\n      ha-icon,\n      ha-icon-button {\n        color: var(--primary-text-color);\n      }\n      ha-icon {\n        margin: 8px;\n      }\n    "]);

  _templateObject3 = function _templateObject3() {
    return data;
  };

  return data;
}

function search_input_asyncGeneratorStep(gen, resolve, reject, _next, _throw, key, arg) { try { var info = gen[key](arg); var value = info.value; } catch (error) { reject(error); return; } if (info.done) { resolve(value); } else { Promise.resolve(value).then(_next, _throw); } }

function search_input_asyncToGenerator(fn) { return function () { var self = this, args = arguments; return new Promise(function (resolve, reject) { var gen = fn.apply(self, args); function _next(value) { search_input_asyncGeneratorStep(gen, resolve, reject, _next, _throw, "next", value); } function _throw(err) { search_input_asyncGeneratorStep(gen, resolve, reject, _next, _throw, "throw", err); } _next(undefined); }); }; }

function _templateObject2() {
  var data = _taggedTemplateLiteral(["\n          <ha-icon-button\n            slot=\"suffix\"\n            class=\"suffix\"\n            @click=", "\n            icon=\"hass:close\"\n            alt=\"Clear\"\n            title=\"Clear\"\n          ></ha-icon-button>\n        "]);

  _templateObject2 = function _templateObject2() {
    return data;
  };

  return data;
}

function _templateObject() {
  var data = _taggedTemplateLiteral(["\n      <style>\n        .no-underline:not(.focused) {\n          --paper-input-container-underline: {\n            display: none;\n            height: 0;\n          }\n        }\n      </style>\n      <paper-input\n        class=", "\n        .autofocus=", "\n        label=\"Search\"\n        .value=", "\n        @value-changed=", "\n        .noLabelFloat=", "\n      >\n        <ha-icon icon=\"hass:magnify\" slot=\"prefix\" class=\"prefix\"></ha-icon>\n        ", "\n      </paper-input>\n    "]);

  _templateObject = function _templateObject() {
    return data;
  };

  return data;
}

function _taggedTemplateLiteral(strings, raw) { if (!raw) { raw = strings.slice(0); } return Object.freeze(Object.defineProperties(strings, { raw: { value: Object.freeze(raw) } })); }

function search_input_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function search_input_inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) search_input_setPrototypeOf(subClass, superClass); }

function search_input_setPrototypeOf(o, p) { search_input_setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return search_input_setPrototypeOf(o, p); }

function search_input_createSuper(Derived) { return function () { var Super = search_input_getPrototypeOf(Derived), result; if (search_input_isNativeReflectConstruct()) { var NewTarget = search_input_getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return search_input_possibleConstructorReturn(this, result); }; }

function search_input_possibleConstructorReturn(self, call) { if (call && (search_input_typeof(call) === "object" || typeof call === "function")) { return call; } return search_input_assertThisInitialized(self); }

function search_input_assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function search_input_isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Date.prototype.toString.call(Reflect.construct(Date, [], function () {})); return true; } catch (e) { return false; } }

function search_input_getPrototypeOf(o) { search_input_getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return search_input_getPrototypeOf(o); }

function _decorate(decorators, factory, superClass, mixins) { var api = _getDecoratorsApi(); if (mixins) { for (var i = 0; i < mixins.length; i++) { api = mixins[i](api); } } var r = factory(function initialize(O) { api.initializeInstanceElements(O, decorated.elements); }, superClass); var decorated = api.decorateClass(_coalesceClassElements(r.d.map(_createElementDescriptor)), decorators); api.initializeClassElements(r.F, decorated.elements); return api.runClassFinishers(r.F, decorated.finishers); }

function _getDecoratorsApi() { _getDecoratorsApi = function _getDecoratorsApi() { return api; }; var api = { elementsDefinitionOrder: [["method"], ["field"]], initializeInstanceElements: function initializeInstanceElements(O, elements) { ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { if (element.kind === kind && element.placement === "own") { this.defineClassElement(O, element); } }, this); }, this); }, initializeClassElements: function initializeClassElements(F, elements) { var proto = F.prototype; ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { var placement = element.placement; if (element.kind === kind && (placement === "static" || placement === "prototype")) { var receiver = placement === "static" ? F : proto; this.defineClassElement(receiver, element); } }, this); }, this); }, defineClassElement: function defineClassElement(receiver, element) { var descriptor = element.descriptor; if (element.kind === "field") { var initializer = element.initializer; descriptor = { enumerable: descriptor.enumerable, writable: descriptor.writable, configurable: descriptor.configurable, value: initializer === void 0 ? void 0 : initializer.call(receiver) }; } Object.defineProperty(receiver, element.key, descriptor); }, decorateClass: function decorateClass(elements, decorators) { var newElements = []; var finishers = []; var placements = { "static": [], prototype: [], own: [] }; elements.forEach(function (element) { this.addElementPlacement(element, placements); }, this); elements.forEach(function (element) { if (!_hasDecorators(element)) return newElements.push(element); var elementFinishersExtras = this.decorateElement(element, placements); newElements.push(elementFinishersExtras.element); newElements.push.apply(newElements, elementFinishersExtras.extras); finishers.push.apply(finishers, elementFinishersExtras.finishers); }, this); if (!decorators) { return { elements: newElements, finishers: finishers }; } var result = this.decorateConstructor(newElements, decorators); finishers.push.apply(finishers, result.finishers); result.finishers = finishers; return result; }, addElementPlacement: function addElementPlacement(element, placements, silent) { var keys = placements[element.placement]; if (!silent && keys.indexOf(element.key) !== -1) { throw new TypeError("Duplicated element (" + element.key + ")"); } keys.push(element.key); }, decorateElement: function decorateElement(element, placements) { var extras = []; var finishers = []; for (var decorators = element.decorators, i = decorators.length - 1; i >= 0; i--) { var keys = placements[element.placement]; keys.splice(keys.indexOf(element.key), 1); var elementObject = this.fromElementDescriptor(element); var elementFinisherExtras = this.toElementFinisherExtras((0, decorators[i])(elementObject) || elementObject); element = elementFinisherExtras.element; this.addElementPlacement(element, placements); if (elementFinisherExtras.finisher) { finishers.push(elementFinisherExtras.finisher); } var newExtras = elementFinisherExtras.extras; if (newExtras) { for (var j = 0; j < newExtras.length; j++) { this.addElementPlacement(newExtras[j], placements); } extras.push.apply(extras, newExtras); } } return { element: element, finishers: finishers, extras: extras }; }, decorateConstructor: function decorateConstructor(elements, decorators) { var finishers = []; for (var i = decorators.length - 1; i >= 0; i--) { var obj = this.fromClassDescriptor(elements); var elementsAndFinisher = this.toClassDescriptor((0, decorators[i])(obj) || obj); if (elementsAndFinisher.finisher !== undefined) { finishers.push(elementsAndFinisher.finisher); } if (elementsAndFinisher.elements !== undefined) { elements = elementsAndFinisher.elements; for (var j = 0; j < elements.length - 1; j++) { for (var k = j + 1; k < elements.length; k++) { if (elements[j].key === elements[k].key && elements[j].placement === elements[k].placement) { throw new TypeError("Duplicated element (" + elements[j].key + ")"); } } } } } return { elements: elements, finishers: finishers }; }, fromElementDescriptor: function fromElementDescriptor(element) { var obj = { kind: element.kind, key: element.key, placement: element.placement, descriptor: element.descriptor }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); if (element.kind === "field") obj.initializer = element.initializer; return obj; }, toElementDescriptors: function toElementDescriptors(elementObjects) { if (elementObjects === undefined) return; return _toArray(elementObjects).map(function (elementObject) { var element = this.toElementDescriptor(elementObject); this.disallowProperty(elementObject, "finisher", "An element descriptor"); this.disallowProperty(elementObject, "extras", "An element descriptor"); return element; }, this); }, toElementDescriptor: function toElementDescriptor(elementObject) { var kind = String(elementObject.kind); if (kind !== "method" && kind !== "field") { throw new TypeError('An element descriptor\'s .kind property must be either "method" or' + ' "field", but a decorator created an element descriptor with' + ' .kind "' + kind + '"'); } var key = _toPropertyKey(elementObject.key); var placement = String(elementObject.placement); if (placement !== "static" && placement !== "prototype" && placement !== "own") { throw new TypeError('An element descriptor\'s .placement property must be one of "static",' + ' "prototype" or "own", but a decorator created an element descriptor' + ' with .placement "' + placement + '"'); } var descriptor = elementObject.descriptor; this.disallowProperty(elementObject, "elements", "An element descriptor"); var element = { kind: kind, key: key, placement: placement, descriptor: Object.assign({}, descriptor) }; if (kind !== "field") { this.disallowProperty(elementObject, "initializer", "A method descriptor"); } else { this.disallowProperty(descriptor, "get", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "set", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "value", "The property descriptor of a field descriptor"); element.initializer = elementObject.initializer; } return element; }, toElementFinisherExtras: function toElementFinisherExtras(elementObject) { var element = this.toElementDescriptor(elementObject); var finisher = _optionalCallableProperty(elementObject, "finisher"); var extras = this.toElementDescriptors(elementObject.extras); return { element: element, finisher: finisher, extras: extras }; }, fromClassDescriptor: function fromClassDescriptor(elements) { var obj = { kind: "class", elements: elements.map(this.fromElementDescriptor, this) }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); return obj; }, toClassDescriptor: function toClassDescriptor(obj) { var kind = String(obj.kind); if (kind !== "class") { throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator' + ' created a class descriptor with .kind "' + kind + '"'); } this.disallowProperty(obj, "key", "A class descriptor"); this.disallowProperty(obj, "placement", "A class descriptor"); this.disallowProperty(obj, "descriptor", "A class descriptor"); this.disallowProperty(obj, "initializer", "A class descriptor"); this.disallowProperty(obj, "extras", "A class descriptor"); var finisher = _optionalCallableProperty(obj, "finisher"); var elements = this.toElementDescriptors(obj.elements); return { elements: elements, finisher: finisher }; }, runClassFinishers: function runClassFinishers(constructor, finishers) { for (var i = 0; i < finishers.length; i++) { var newConstructor = (0, finishers[i])(constructor); if (newConstructor !== undefined) { if (typeof newConstructor !== "function") { throw new TypeError("Finishers must return a constructor."); } constructor = newConstructor; } } return constructor; }, disallowProperty: function disallowProperty(obj, name, objectType) { if (obj[name] !== undefined) { throw new TypeError(objectType + " can't have a ." + name + " property."); } } }; return api; }

function _createElementDescriptor(def) { var key = _toPropertyKey(def.key); var descriptor; if (def.kind === "method") { descriptor = { value: def.value, writable: true, configurable: true, enumerable: false }; } else if (def.kind === "get") { descriptor = { get: def.value, configurable: true, enumerable: false }; } else if (def.kind === "set") { descriptor = { set: def.value, configurable: true, enumerable: false }; } else if (def.kind === "field") { descriptor = { configurable: true, writable: true, enumerable: true }; } var element = { kind: def.kind === "field" ? "field" : "method", key: key, placement: def["static"] ? "static" : def.kind === "field" ? "own" : "prototype", descriptor: descriptor }; if (def.decorators) element.decorators = def.decorators; if (def.kind === "field") element.initializer = def.value; return element; }

function _coalesceGetterSetter(element, other) { if (element.descriptor.get !== undefined) { other.descriptor.get = element.descriptor.get; } else { other.descriptor.set = element.descriptor.set; } }

function _coalesceClassElements(elements) { var newElements = []; var isSameElement = function isSameElement(other) { return other.kind === "method" && other.key === element.key && other.placement === element.placement; }; for (var i = 0; i < elements.length; i++) { var element = elements[i]; var other; if (element.kind === "method" && (other = newElements.find(isSameElement))) { if (_isDataDescriptor(element.descriptor) || _isDataDescriptor(other.descriptor)) { if (_hasDecorators(element) || _hasDecorators(other)) { throw new ReferenceError("Duplicated methods (" + element.key + ") can't be decorated."); } other.descriptor = element.descriptor; } else { if (_hasDecorators(element)) { if (_hasDecorators(other)) { throw new ReferenceError("Decorators can't be placed on different accessors with for " + "the same property (" + element.key + ")."); } other.decorators = element.decorators; } _coalesceGetterSetter(element, other); } } else { newElements.push(element); } } return newElements; }

function _hasDecorators(element) { return element.decorators && element.decorators.length; }

function _isDataDescriptor(desc) { return desc !== undefined && !(desc.value === undefined && desc.writable === undefined); }

function _optionalCallableProperty(obj, name) { var value = obj[name]; if (value !== undefined && typeof value !== "function") { throw new TypeError("Expected '" + name + "' to be a function"); } return value; }

function _toPropertyKey(arg) { var key = _toPrimitive(arg, "string"); return search_input_typeof(key) === "symbol" ? key : String(key); }

function _toPrimitive(input, hint) { if (search_input_typeof(input) !== "object" || input === null) return input; var prim = input[Symbol.toPrimitive]; if (prim !== undefined) { var res = prim.call(input, hint || "default"); if (search_input_typeof(res) !== "object") return res; throw new TypeError("@@toPrimitive must return a primitive value."); } return (hint === "string" ? String : Number)(input); }

function _toArray(arr) { return search_input_arrayWithHoles(arr) || _iterableToArray(arr) || search_input_unsupportedIterableToArray(arr) || search_input_nonIterableRest(); }

function search_input_nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function search_input_unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return search_input_arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(n); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return search_input_arrayLikeToArray(o, minLen); }

function search_input_arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function _iterableToArray(iter) { if (typeof Symbol !== "undefined" && Symbol.iterator in Object(iter)) return Array.from(iter); }

function search_input_arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }









var search_input_SearchInput = _decorate([Object(lit_element["d" /* customElement */])("search-input")], function (_initialize, _LitElement) {
  var SearchInput = /*#__PURE__*/function (_LitElement2) {
    search_input_inherits(SearchInput, _LitElement2);

    var _super = search_input_createSuper(SearchInput);

    function SearchInput() {
      var _this;

      search_input_classCallCheck(this, SearchInput);

      for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
        args[_key] = arguments[_key];
      }

      _this = _super.call.apply(_super, [this].concat(args));

      _initialize(search_input_assertThisInitialized(_this));

      return _this;
    }

    return SearchInput;
  }(_LitElement);

  return {
    F: SearchInput,
    d: [{
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "filter",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])({
        type: Boolean,
        attribute: "no-label-float"
      })],
      key: "noLabelFloat",
      value: function value() {
        return false;
      }
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])({
        type: Boolean,
        attribute: "no-underline"
      })],
      key: "noUnderline",
      value: function value() {
        return false;
      }
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])({
        type: Boolean
      })],
      key: "autofocus",
      value: function value() {
        return false;
      }
    }, {
      kind: "method",
      key: "focus",
      value: function focus() {
        this.shadowRoot.querySelector("paper-input").focus();
      }
    }, {
      kind: "method",
      key: "render",
      value: function render() {
        return Object(lit_html["f" /* html */])(_templateObject(), Object(class_map["a" /* classMap */])({
          "no-underline": this.noUnderline
        }), this.autofocus, this.filter, this._filterInputChanged, this.noLabelFloat, this.filter && Object(lit_html["f" /* html */])(_templateObject2(), this._clearSearch));
      }
    }, {
      kind: "method",
      key: "_filterChanged",
      value: function () {
        var _filterChanged2 = search_input_asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee(value) {
          return regeneratorRuntime.wrap(function _callee$(_context) {
            while (1) {
              switch (_context.prev = _context.next) {
                case 0:
                  Object(fire_event["a" /* fireEvent */])(this, "value-changed", {
                    value: String(value)
                  });

                case 1:
                case "end":
                  return _context.stop();
              }
            }
          }, _callee, this);
        }));

        function _filterChanged(_x) {
          return _filterChanged2.apply(this, arguments);
        }

        return _filterChanged;
      }()
    }, {
      kind: "method",
      key: "_filterInputChanged",
      value: function () {
        var _filterInputChanged2 = search_input_asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee2(e) {
          return regeneratorRuntime.wrap(function _callee2$(_context2) {
            while (1) {
              switch (_context2.prev = _context2.next) {
                case 0:
                  this._filterChanged(e.target.value);

                case 1:
                case "end":
                  return _context2.stop();
              }
            }
          }, _callee2, this);
        }));

        function _filterInputChanged(_x2) {
          return _filterInputChanged2.apply(this, arguments);
        }

        return _filterInputChanged;
      }()
    }, {
      kind: "method",
      key: "_clearSearch",
      value: function () {
        var _clearSearch2 = search_input_asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee3() {
          return regeneratorRuntime.wrap(function _callee3$(_context3) {
            while (1) {
              switch (_context3.prev = _context3.next) {
                case 0:
                  this._filterChanged("");

                case 1:
                case "end":
                  return _context3.stop();
              }
            }
          }, _callee3, this);
        }));

        function _clearSearch() {
          return _clearSearch2.apply(this, arguments);
        }

        return _clearSearch;
      }()
    }, {
      kind: "get",
      "static": true,
      key: "styles",
      value: function styles() {
        return Object(lit_element["c" /* css */])(_templateObject3());
      }
    }]
  };
}, lit_element["a" /* LitElement */]);
// EXTERNAL MODULE: ./node_modules/@polymer/paper-card/paper-card.js + 2 modules
var paper_card = __webpack_require__(20);

// EXTERNAL MODULE: ./node_modules/memoize-one/dist/memoize-one.esm.js
var memoize_one_esm = __webpack_require__(50);

// EXTERNAL MODULE: ./src/common/config/version.ts
var version = __webpack_require__(91);

// EXTERNAL MODULE: ./hassio/src/components/hassio-card-content.ts + 3 modules
var hassio_card_content = __webpack_require__(56);

// EXTERNAL MODULE: ./node_modules/fuse.js/dist/fuse.js
var dist_fuse = __webpack_require__(145);

// CONCATENATED MODULE: ./hassio/src/components/hassio-filter-addons.ts

function filterAndSort(addons, filter) {
  var options = {
    keys: ["name", "description", "slug"],
    caseSensitive: false,
    minMatchCharLength: 2,
    threshold: 0.2
  };
  var fuse = new dist_fuse(addons, options);
  return fuse.search(filter);
}
// EXTERNAL MODULE: ./hassio/src/resources/hassio-style.ts
var hassio_style = __webpack_require__(13);

// CONCATENATED MODULE: ./hassio/src/addon-store/hassio-addon-repository.ts
function hassio_addon_repository_typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { hassio_addon_repository_typeof = function _typeof(obj) { return typeof obj; }; } else { hassio_addon_repository_typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return hassio_addon_repository_typeof(obj); }

function _templateObject4() {
  var data = hassio_addon_repository_taggedTemplateLiteral(["\n        paper-card {\n          cursor: pointer;\n        }\n        .not_available {\n          opacity: 0.6;\n        }\n        a.repo {\n          color: var(--primary-text-color);\n        }\n      "]);

  _templateObject4 = function _templateObject4() {
    return data;
  };

  return data;
}

function hassio_addon_repository_templateObject3() {
  var data = hassio_addon_repository_taggedTemplateLiteral(["\n              <paper-card\n                .addon=", "\n                class=", "\n                @click=", "\n              >\n                <div class=\"card-content\">\n                  <hassio-card-content\n                    .hass=", "\n                    .title=", "\n                    .description=", "\n                    .available=", "\n                    .icon=", "\n                    .iconTitle=", "\n                    .iconClass=", "\n                    .iconImage=", "\n                    .showTopbar=", "\n                    .topbarClass=", "\n                  ></hassio-card-content>\n                </div>\n              </paper-card>\n            "]);

  hassio_addon_repository_templateObject3 = function _templateObject3() {
    return data;
  };

  return data;
}

function hassio_addon_repository_templateObject2() {
  var data = hassio_addon_repository_taggedTemplateLiteral(["\n      <div class=\"content\">\n        <h1>\n          ", "\n        </h1>\n        <div class=\"card-group\">\n          ", "\n        </div>\n      </div>\n    "]);

  hassio_addon_repository_templateObject2 = function _templateObject2() {
    return data;
  };

  return data;
}

function hassio_addon_repository_templateObject() {
  var data = hassio_addon_repository_taggedTemplateLiteral(["\n        <div class=\"content\">\n          <p class=\"description\">\n            No results found in \"", ".\"\n          </p>\n        </div>\n      "]);

  hassio_addon_repository_templateObject = function _templateObject() {
    return data;
  };

  return data;
}

function hassio_addon_repository_taggedTemplateLiteral(strings, raw) { if (!raw) { raw = strings.slice(0); } return Object.freeze(Object.defineProperties(strings, { raw: { value: Object.freeze(raw) } })); }

function hassio_addon_repository_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function hassio_addon_repository_inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) hassio_addon_repository_setPrototypeOf(subClass, superClass); }

function hassio_addon_repository_setPrototypeOf(o, p) { hassio_addon_repository_setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return hassio_addon_repository_setPrototypeOf(o, p); }

function hassio_addon_repository_createSuper(Derived) { return function () { var Super = hassio_addon_repository_getPrototypeOf(Derived), result; if (hassio_addon_repository_isNativeReflectConstruct()) { var NewTarget = hassio_addon_repository_getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return hassio_addon_repository_possibleConstructorReturn(this, result); }; }

function hassio_addon_repository_possibleConstructorReturn(self, call) { if (call && (hassio_addon_repository_typeof(call) === "object" || typeof call === "function")) { return call; } return hassio_addon_repository_assertThisInitialized(self); }

function hassio_addon_repository_assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function hassio_addon_repository_isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Date.prototype.toString.call(Reflect.construct(Date, [], function () {})); return true; } catch (e) { return false; } }

function hassio_addon_repository_getPrototypeOf(o) { hassio_addon_repository_getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return hassio_addon_repository_getPrototypeOf(o); }

function hassio_addon_repository_decorate(decorators, factory, superClass, mixins) { var api = hassio_addon_repository_getDecoratorsApi(); if (mixins) { for (var i = 0; i < mixins.length; i++) { api = mixins[i](api); } } var r = factory(function initialize(O) { api.initializeInstanceElements(O, decorated.elements); }, superClass); var decorated = api.decorateClass(hassio_addon_repository_coalesceClassElements(r.d.map(hassio_addon_repository_createElementDescriptor)), decorators); api.initializeClassElements(r.F, decorated.elements); return api.runClassFinishers(r.F, decorated.finishers); }

function hassio_addon_repository_getDecoratorsApi() { hassio_addon_repository_getDecoratorsApi = function _getDecoratorsApi() { return api; }; var api = { elementsDefinitionOrder: [["method"], ["field"]], initializeInstanceElements: function initializeInstanceElements(O, elements) { ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { if (element.kind === kind && element.placement === "own") { this.defineClassElement(O, element); } }, this); }, this); }, initializeClassElements: function initializeClassElements(F, elements) { var proto = F.prototype; ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { var placement = element.placement; if (element.kind === kind && (placement === "static" || placement === "prototype")) { var receiver = placement === "static" ? F : proto; this.defineClassElement(receiver, element); } }, this); }, this); }, defineClassElement: function defineClassElement(receiver, element) { var descriptor = element.descriptor; if (element.kind === "field") { var initializer = element.initializer; descriptor = { enumerable: descriptor.enumerable, writable: descriptor.writable, configurable: descriptor.configurable, value: initializer === void 0 ? void 0 : initializer.call(receiver) }; } Object.defineProperty(receiver, element.key, descriptor); }, decorateClass: function decorateClass(elements, decorators) { var newElements = []; var finishers = []; var placements = { "static": [], prototype: [], own: [] }; elements.forEach(function (element) { this.addElementPlacement(element, placements); }, this); elements.forEach(function (element) { if (!hassio_addon_repository_hasDecorators(element)) return newElements.push(element); var elementFinishersExtras = this.decorateElement(element, placements); newElements.push(elementFinishersExtras.element); newElements.push.apply(newElements, elementFinishersExtras.extras); finishers.push.apply(finishers, elementFinishersExtras.finishers); }, this); if (!decorators) { return { elements: newElements, finishers: finishers }; } var result = this.decorateConstructor(newElements, decorators); finishers.push.apply(finishers, result.finishers); result.finishers = finishers; return result; }, addElementPlacement: function addElementPlacement(element, placements, silent) { var keys = placements[element.placement]; if (!silent && keys.indexOf(element.key) !== -1) { throw new TypeError("Duplicated element (" + element.key + ")"); } keys.push(element.key); }, decorateElement: function decorateElement(element, placements) { var extras = []; var finishers = []; for (var decorators = element.decorators, i = decorators.length - 1; i >= 0; i--) { var keys = placements[element.placement]; keys.splice(keys.indexOf(element.key), 1); var elementObject = this.fromElementDescriptor(element); var elementFinisherExtras = this.toElementFinisherExtras((0, decorators[i])(elementObject) || elementObject); element = elementFinisherExtras.element; this.addElementPlacement(element, placements); if (elementFinisherExtras.finisher) { finishers.push(elementFinisherExtras.finisher); } var newExtras = elementFinisherExtras.extras; if (newExtras) { for (var j = 0; j < newExtras.length; j++) { this.addElementPlacement(newExtras[j], placements); } extras.push.apply(extras, newExtras); } } return { element: element, finishers: finishers, extras: extras }; }, decorateConstructor: function decorateConstructor(elements, decorators) { var finishers = []; for (var i = decorators.length - 1; i >= 0; i--) { var obj = this.fromClassDescriptor(elements); var elementsAndFinisher = this.toClassDescriptor((0, decorators[i])(obj) || obj); if (elementsAndFinisher.finisher !== undefined) { finishers.push(elementsAndFinisher.finisher); } if (elementsAndFinisher.elements !== undefined) { elements = elementsAndFinisher.elements; for (var j = 0; j < elements.length - 1; j++) { for (var k = j + 1; k < elements.length; k++) { if (elements[j].key === elements[k].key && elements[j].placement === elements[k].placement) { throw new TypeError("Duplicated element (" + elements[j].key + ")"); } } } } } return { elements: elements, finishers: finishers }; }, fromElementDescriptor: function fromElementDescriptor(element) { var obj = { kind: element.kind, key: element.key, placement: element.placement, descriptor: element.descriptor }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); if (element.kind === "field") obj.initializer = element.initializer; return obj; }, toElementDescriptors: function toElementDescriptors(elementObjects) { if (elementObjects === undefined) return; return hassio_addon_repository_toArray(elementObjects).map(function (elementObject) { var element = this.toElementDescriptor(elementObject); this.disallowProperty(elementObject, "finisher", "An element descriptor"); this.disallowProperty(elementObject, "extras", "An element descriptor"); return element; }, this); }, toElementDescriptor: function toElementDescriptor(elementObject) { var kind = String(elementObject.kind); if (kind !== "method" && kind !== "field") { throw new TypeError('An element descriptor\'s .kind property must be either "method" or' + ' "field", but a decorator created an element descriptor with' + ' .kind "' + kind + '"'); } var key = hassio_addon_repository_toPropertyKey(elementObject.key); var placement = String(elementObject.placement); if (placement !== "static" && placement !== "prototype" && placement !== "own") { throw new TypeError('An element descriptor\'s .placement property must be one of "static",' + ' "prototype" or "own", but a decorator created an element descriptor' + ' with .placement "' + placement + '"'); } var descriptor = elementObject.descriptor; this.disallowProperty(elementObject, "elements", "An element descriptor"); var element = { kind: kind, key: key, placement: placement, descriptor: Object.assign({}, descriptor) }; if (kind !== "field") { this.disallowProperty(elementObject, "initializer", "A method descriptor"); } else { this.disallowProperty(descriptor, "get", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "set", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "value", "The property descriptor of a field descriptor"); element.initializer = elementObject.initializer; } return element; }, toElementFinisherExtras: function toElementFinisherExtras(elementObject) { var element = this.toElementDescriptor(elementObject); var finisher = hassio_addon_repository_optionalCallableProperty(elementObject, "finisher"); var extras = this.toElementDescriptors(elementObject.extras); return { element: element, finisher: finisher, extras: extras }; }, fromClassDescriptor: function fromClassDescriptor(elements) { var obj = { kind: "class", elements: elements.map(this.fromElementDescriptor, this) }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); return obj; }, toClassDescriptor: function toClassDescriptor(obj) { var kind = String(obj.kind); if (kind !== "class") { throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator' + ' created a class descriptor with .kind "' + kind + '"'); } this.disallowProperty(obj, "key", "A class descriptor"); this.disallowProperty(obj, "placement", "A class descriptor"); this.disallowProperty(obj, "descriptor", "A class descriptor"); this.disallowProperty(obj, "initializer", "A class descriptor"); this.disallowProperty(obj, "extras", "A class descriptor"); var finisher = hassio_addon_repository_optionalCallableProperty(obj, "finisher"); var elements = this.toElementDescriptors(obj.elements); return { elements: elements, finisher: finisher }; }, runClassFinishers: function runClassFinishers(constructor, finishers) { for (var i = 0; i < finishers.length; i++) { var newConstructor = (0, finishers[i])(constructor); if (newConstructor !== undefined) { if (typeof newConstructor !== "function") { throw new TypeError("Finishers must return a constructor."); } constructor = newConstructor; } } return constructor; }, disallowProperty: function disallowProperty(obj, name, objectType) { if (obj[name] !== undefined) { throw new TypeError(objectType + " can't have a ." + name + " property."); } } }; return api; }

function hassio_addon_repository_createElementDescriptor(def) { var key = hassio_addon_repository_toPropertyKey(def.key); var descriptor; if (def.kind === "method") { descriptor = { value: def.value, writable: true, configurable: true, enumerable: false }; } else if (def.kind === "get") { descriptor = { get: def.value, configurable: true, enumerable: false }; } else if (def.kind === "set") { descriptor = { set: def.value, configurable: true, enumerable: false }; } else if (def.kind === "field") { descriptor = { configurable: true, writable: true, enumerable: true }; } var element = { kind: def.kind === "field" ? "field" : "method", key: key, placement: def["static"] ? "static" : def.kind === "field" ? "own" : "prototype", descriptor: descriptor }; if (def.decorators) element.decorators = def.decorators; if (def.kind === "field") element.initializer = def.value; return element; }

function hassio_addon_repository_coalesceGetterSetter(element, other) { if (element.descriptor.get !== undefined) { other.descriptor.get = element.descriptor.get; } else { other.descriptor.set = element.descriptor.set; } }

function hassio_addon_repository_coalesceClassElements(elements) { var newElements = []; var isSameElement = function isSameElement(other) { return other.kind === "method" && other.key === element.key && other.placement === element.placement; }; for (var i = 0; i < elements.length; i++) { var element = elements[i]; var other; if (element.kind === "method" && (other = newElements.find(isSameElement))) { if (hassio_addon_repository_isDataDescriptor(element.descriptor) || hassio_addon_repository_isDataDescriptor(other.descriptor)) { if (hassio_addon_repository_hasDecorators(element) || hassio_addon_repository_hasDecorators(other)) { throw new ReferenceError("Duplicated methods (" + element.key + ") can't be decorated."); } other.descriptor = element.descriptor; } else { if (hassio_addon_repository_hasDecorators(element)) { if (hassio_addon_repository_hasDecorators(other)) { throw new ReferenceError("Decorators can't be placed on different accessors with for " + "the same property (" + element.key + ")."); } other.decorators = element.decorators; } hassio_addon_repository_coalesceGetterSetter(element, other); } } else { newElements.push(element); } } return newElements; }

function hassio_addon_repository_hasDecorators(element) { return element.decorators && element.decorators.length; }

function hassio_addon_repository_isDataDescriptor(desc) { return desc !== undefined && !(desc.value === undefined && desc.writable === undefined); }

function hassio_addon_repository_optionalCallableProperty(obj, name) { var value = obj[name]; if (value !== undefined && typeof value !== "function") { throw new TypeError("Expected '" + name + "' to be a function"); } return value; }

function hassio_addon_repository_toPropertyKey(arg) { var key = hassio_addon_repository_toPrimitive(arg, "string"); return hassio_addon_repository_typeof(key) === "symbol" ? key : String(key); }

function hassio_addon_repository_toPrimitive(input, hint) { if (hassio_addon_repository_typeof(input) !== "object" || input === null) return input; var prim = input[Symbol.toPrimitive]; if (prim !== undefined) { var res = prim.call(input, hint || "default"); if (hassio_addon_repository_typeof(res) !== "object") return res; throw new TypeError("@@toPrimitive must return a primitive value."); } return (hint === "string" ? String : Number)(input); }

function hassio_addon_repository_toArray(arr) { return hassio_addon_repository_arrayWithHoles(arr) || hassio_addon_repository_iterableToArray(arr) || hassio_addon_repository_unsupportedIterableToArray(arr) || hassio_addon_repository_nonIterableRest(); }

function hassio_addon_repository_nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function hassio_addon_repository_unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return hassio_addon_repository_arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(n); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return hassio_addon_repository_arrayLikeToArray(o, minLen); }

function hassio_addon_repository_arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function hassio_addon_repository_iterableToArray(iter) { if (typeof Symbol !== "undefined" && Symbol.iterator in Object(iter)) return Array.from(iter); }

function hassio_addon_repository_arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }










var hassio_addon_repository_HassioAddonRepositoryEl = hassio_addon_repository_decorate(null, function (_initialize, _LitElement) {
  var HassioAddonRepositoryEl = /*#__PURE__*/function (_LitElement2) {
    hassio_addon_repository_inherits(HassioAddonRepositoryEl, _LitElement2);

    var _super = hassio_addon_repository_createSuper(HassioAddonRepositoryEl);

    function HassioAddonRepositoryEl() {
      var _this;

      hassio_addon_repository_classCallCheck(this, HassioAddonRepositoryEl);

      for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
        args[_key] = arguments[_key];
      }

      _this = _super.call.apply(_super, [this].concat(args));

      _initialize(hassio_addon_repository_assertThisInitialized(_this));

      return _this;
    }

    return HassioAddonRepositoryEl;
  }(_LitElement);

  return {
    F: HassioAddonRepositoryEl,
    d: [{
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "hass",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "repo",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "addons",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "filter",
      value: void 0
    }, {
      kind: "field",
      key: "_getAddons",
      value: function value() {
        return Object(memoize_one_esm["a" /* default */])(function (addons, filter) {
          if (filter) {
            return filterAndSort(addons, filter);
          }

          return addons.sort(function (a, b) {
            return a.name.toUpperCase() < b.name.toUpperCase() ? -1 : 1;
          });
        });
      }
    }, {
      kind: "method",
      key: "render",
      value: function render() {
        var _this$hass$userData,
            _this2 = this;

        var repo = this.repo;
        var _addons = this.addons;

        if (!((_this$hass$userData = this.hass.userData) === null || _this$hass$userData === void 0 ? void 0 : _this$hass$userData.showAdvanced)) {
          _addons = _addons.filter(function (addon) {
            return !addon.advanced;
          });
        }

        var addons = this._getAddons(_addons, this.filter);

        if (this.filter && addons.length < 1) {
          return Object(lit_element["e" /* html */])(hassio_addon_repository_templateObject(), repo.name);
        }

        return Object(lit_element["e" /* html */])(hassio_addon_repository_templateObject2(), repo.name, addons.map(function (addon) {
          return Object(lit_element["e" /* html */])(hassio_addon_repository_templateObject3(), addon, addon.available ? "" : "not_available", _this2._addonTapped, _this2.hass, addon.name, addon.description, addon.available, addon.installed && addon.installed !== addon.version ? "hassio:arrow-up-bold-circle" : "hassio:puzzle", addon.installed ? addon.installed !== addon.version ? "New version available" : "Add-on is installed" : addon.available ? "Add-on is not installed" : "Add-on is not available on your system", addon.installed ? addon.installed !== addon.version ? "update" : "installed" : !addon.available ? "not_available" : "", Object(version["a" /* atLeastVersion */])(_this2.hass.config.version, 0, 105) && addon.icon ? "/api/hassio/addons/".concat(addon.slug, "/icon") : undefined, addon.installed || !addon.available, addon.installed ? addon.installed !== addon.version ? "update" : "installed" : !addon.available ? "unavailable" : "");
        }));
      }
    }, {
      kind: "method",
      key: "_addonTapped",
      value: function _addonTapped(ev) {
        Object(common_navigate["a" /* navigate */])(this, "/hassio/addon/".concat(ev.currentTarget.addon.slug));
      }
    }, {
      kind: "get",
      "static": true,
      key: "styles",
      value: function styles() {
        return [hassio_style["a" /* hassioStyle */], Object(lit_element["c" /* css */])(_templateObject4())];
      }
    }]
  };
}, lit_element["a" /* LitElement */]);

customElements.define("hassio-addon-repository", hassio_addon_repository_HassioAddonRepositoryEl);
// EXTERNAL MODULE: ./hassio/src/dialogs/repositories/dialog-hassio-repositories.ts + 1 modules
var dialog_hassio_repositories = __webpack_require__(188);

// CONCATENATED MODULE: ./hassio/src/dialogs/repositories/show-dialog-repositories.ts


var show_dialog_repositories_showRepositoriesDialog = function showRepositoriesDialog(element, dialogParams) {
  Object(fire_event["a" /* fireEvent */])(element, "show-dialog", {
    dialogTag: "dialog-hassio-repositories",
    dialogImport: function dialogImport() {
      return Promise.resolve(/* import() */).then(__webpack_require__.bind(null, 188));
    },
    dialogParams: dialogParams
  });
};
// CONCATENATED MODULE: ./hassio/src/addon-store/hassio-addon-store.ts
function hassio_addon_store_typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { hassio_addon_store_typeof = function _typeof(obj) { return typeof obj; }; } else { hassio_addon_store_typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return hassio_addon_store_typeof(obj); }

function _templateObject6() {
  var data = hassio_addon_store_taggedTemplateLiteral(["\n      hassio-addon-repository {\n        margin-top: 24px;\n      }\n      .search {\n        padding: 0 16px;\n        background: var(--sidebar-background-color);\n        border-bottom: 1px solid var(--divider-color);\n      }\n      .search search-input {\n        position: relative;\n        top: 2px;\n      }\n      .advanced {\n        padding: 12px;\n        display: flex;\n        flex-wrap: wrap;\n        color: var(--primary-text-color);\n      }\n      .advanced a {\n        margin-left: 0.5em;\n        color: var(--primary-color);\n      }\n    "]);

  _templateObject6 = function _templateObject6() {
    return data;
  };

  return data;
}

function _templateObject5() {
  var data = hassio_addon_store_taggedTemplateLiteral(["\n              <div class=\"advanced\">\n                Missing add-ons? Enable advanced mode on\n                <a href=\"/profile\" target=\"_top\">\n                  your profile page\n                </a>\n                .\n              </div>\n            "]);

  _templateObject5 = function _templateObject5() {
    return data;
  };

  return data;
}

function hassio_addon_store_templateObject4() {
  var data = hassio_addon_store_taggedTemplateLiteral(["\n              <div class=\"search\">\n                <search-input\n                  no-label-float\n                  no-underline\n                  .filter=", "\n                  @value-changed=", "\n                ></search-input>\n              </div>\n\n              ", "\n            "]);

  hassio_addon_store_templateObject4 = function _templateObject4() {
    return data;
  };

  return data;
}

function hassio_addon_store_templateObject3() {
  var data = hassio_addon_store_taggedTemplateLiteral(["<loading-screen></loading-screen>"]);

  hassio_addon_store_templateObject3 = function _templateObject3() {
    return data;
  };

  return data;
}

function hassio_addon_store_templateObject2() {
  var data = hassio_addon_store_taggedTemplateLiteral(["\n      <hass-tabs-subpage\n        .hass=", "\n        .narrow=", "\n        .route=", "\n        hassio\n        main-page\n        .tabs=", "\n      >\n        <span slot=\"header\">Add-on store</span>\n        <paper-menu-button\n          close-on-activate\n          no-animations\n          horizontal-align=\"right\"\n          horizontal-offset=\"-5\"\n          slot=\"toolbar-icon\"\n        >\n          <ha-icon-button\n            icon=\"hassio:dots-vertical\"\n            slot=\"dropdown-trigger\"\n            alt=\"menu\"\n          ></ha-icon-button>\n          <paper-listbox slot=\"dropdown-content\" role=\"listbox\">\n            <paper-item @tap=", ">\n              Repositories\n            </paper-item>\n            <paper-item @tap=", ">\n              Reload\n            </paper-item>\n          </paper-listbox>\n        </paper-menu-button>\n        ", "\n        ", "\n      </hass-tabs-subpage>\n    "]);

  hassio_addon_store_templateObject2 = function _templateObject2() {
    return data;
  };

  return data;
}

function hassio_addon_store_templateObject() {
  var data = hassio_addon_store_taggedTemplateLiteral(["\n          <hassio-addon-repository\n            .hass=", "\n            .repo=", "\n            .addons=", "\n            .filter=", "\n          ></hassio-addon-repository>\n        "]);

  hassio_addon_store_templateObject = function _templateObject() {
    return data;
  };

  return data;
}

function hassio_addon_store_taggedTemplateLiteral(strings, raw) { if (!raw) { raw = strings.slice(0); } return Object.freeze(Object.defineProperties(strings, { raw: { value: Object.freeze(raw) } })); }

function _createForOfIteratorHelper(o) { if (typeof Symbol === "undefined" || o[Symbol.iterator] == null) { if (Array.isArray(o) || (o = hassio_addon_store_unsupportedIterableToArray(o))) { var i = 0; var F = function F() {}; return { s: F, n: function n() { if (i >= o.length) return { done: true }; return { done: false, value: o[i++] }; }, e: function e(_e) { throw _e; }, f: F }; } throw new TypeError("Invalid attempt to iterate non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); } var it, normalCompletion = true, didErr = false, err; return { s: function s() { it = o[Symbol.iterator](); }, n: function n() { var step = it.next(); normalCompletion = step.done; return step; }, e: function e(_e2) { didErr = true; err = _e2; }, f: function f() { try { if (!normalCompletion && it["return"] != null) it["return"](); } finally { if (didErr) throw err; } } }; }

function hassio_addon_store_asyncGeneratorStep(gen, resolve, reject, _next, _throw, key, arg) { try { var info = gen[key](arg); var value = info.value; } catch (error) { reject(error); return; } if (info.done) { resolve(value); } else { Promise.resolve(value).then(_next, _throw); } }

function hassio_addon_store_asyncToGenerator(fn) { return function () { var self = this, args = arguments; return new Promise(function (resolve, reject) { var gen = fn.apply(self, args); function _next(value) { hassio_addon_store_asyncGeneratorStep(gen, resolve, reject, _next, _throw, "next", value); } function _throw(err) { hassio_addon_store_asyncGeneratorStep(gen, resolve, reject, _next, _throw, "throw", err); } _next(undefined); }); }; }

function hassio_addon_store_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function hassio_addon_store_inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) hassio_addon_store_setPrototypeOf(subClass, superClass); }

function hassio_addon_store_setPrototypeOf(o, p) { hassio_addon_store_setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return hassio_addon_store_setPrototypeOf(o, p); }

function hassio_addon_store_createSuper(Derived) { return function () { var Super = hassio_addon_store_getPrototypeOf(Derived), result; if (hassio_addon_store_isNativeReflectConstruct()) { var NewTarget = hassio_addon_store_getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return hassio_addon_store_possibleConstructorReturn(this, result); }; }

function hassio_addon_store_possibleConstructorReturn(self, call) { if (call && (hassio_addon_store_typeof(call) === "object" || typeof call === "function")) { return call; } return hassio_addon_store_assertThisInitialized(self); }

function hassio_addon_store_assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function hassio_addon_store_isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Date.prototype.toString.call(Reflect.construct(Date, [], function () {})); return true; } catch (e) { return false; } }

function hassio_addon_store_decorate(decorators, factory, superClass, mixins) { var api = hassio_addon_store_getDecoratorsApi(); if (mixins) { for (var i = 0; i < mixins.length; i++) { api = mixins[i](api); } } var r = factory(function initialize(O) { api.initializeInstanceElements(O, decorated.elements); }, superClass); var decorated = api.decorateClass(hassio_addon_store_coalesceClassElements(r.d.map(hassio_addon_store_createElementDescriptor)), decorators); api.initializeClassElements(r.F, decorated.elements); return api.runClassFinishers(r.F, decorated.finishers); }

function hassio_addon_store_getDecoratorsApi() { hassio_addon_store_getDecoratorsApi = function _getDecoratorsApi() { return api; }; var api = { elementsDefinitionOrder: [["method"], ["field"]], initializeInstanceElements: function initializeInstanceElements(O, elements) { ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { if (element.kind === kind && element.placement === "own") { this.defineClassElement(O, element); } }, this); }, this); }, initializeClassElements: function initializeClassElements(F, elements) { var proto = F.prototype; ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { var placement = element.placement; if (element.kind === kind && (placement === "static" || placement === "prototype")) { var receiver = placement === "static" ? F : proto; this.defineClassElement(receiver, element); } }, this); }, this); }, defineClassElement: function defineClassElement(receiver, element) { var descriptor = element.descriptor; if (element.kind === "field") { var initializer = element.initializer; descriptor = { enumerable: descriptor.enumerable, writable: descriptor.writable, configurable: descriptor.configurable, value: initializer === void 0 ? void 0 : initializer.call(receiver) }; } Object.defineProperty(receiver, element.key, descriptor); }, decorateClass: function decorateClass(elements, decorators) { var newElements = []; var finishers = []; var placements = { "static": [], prototype: [], own: [] }; elements.forEach(function (element) { this.addElementPlacement(element, placements); }, this); elements.forEach(function (element) { if (!hassio_addon_store_hasDecorators(element)) return newElements.push(element); var elementFinishersExtras = this.decorateElement(element, placements); newElements.push(elementFinishersExtras.element); newElements.push.apply(newElements, elementFinishersExtras.extras); finishers.push.apply(finishers, elementFinishersExtras.finishers); }, this); if (!decorators) { return { elements: newElements, finishers: finishers }; } var result = this.decorateConstructor(newElements, decorators); finishers.push.apply(finishers, result.finishers); result.finishers = finishers; return result; }, addElementPlacement: function addElementPlacement(element, placements, silent) { var keys = placements[element.placement]; if (!silent && keys.indexOf(element.key) !== -1) { throw new TypeError("Duplicated element (" + element.key + ")"); } keys.push(element.key); }, decorateElement: function decorateElement(element, placements) { var extras = []; var finishers = []; for (var decorators = element.decorators, i = decorators.length - 1; i >= 0; i--) { var keys = placements[element.placement]; keys.splice(keys.indexOf(element.key), 1); var elementObject = this.fromElementDescriptor(element); var elementFinisherExtras = this.toElementFinisherExtras((0, decorators[i])(elementObject) || elementObject); element = elementFinisherExtras.element; this.addElementPlacement(element, placements); if (elementFinisherExtras.finisher) { finishers.push(elementFinisherExtras.finisher); } var newExtras = elementFinisherExtras.extras; if (newExtras) { for (var j = 0; j < newExtras.length; j++) { this.addElementPlacement(newExtras[j], placements); } extras.push.apply(extras, newExtras); } } return { element: element, finishers: finishers, extras: extras }; }, decorateConstructor: function decorateConstructor(elements, decorators) { var finishers = []; for (var i = decorators.length - 1; i >= 0; i--) { var obj = this.fromClassDescriptor(elements); var elementsAndFinisher = this.toClassDescriptor((0, decorators[i])(obj) || obj); if (elementsAndFinisher.finisher !== undefined) { finishers.push(elementsAndFinisher.finisher); } if (elementsAndFinisher.elements !== undefined) { elements = elementsAndFinisher.elements; for (var j = 0; j < elements.length - 1; j++) { for (var k = j + 1; k < elements.length; k++) { if (elements[j].key === elements[k].key && elements[j].placement === elements[k].placement) { throw new TypeError("Duplicated element (" + elements[j].key + ")"); } } } } } return { elements: elements, finishers: finishers }; }, fromElementDescriptor: function fromElementDescriptor(element) { var obj = { kind: element.kind, key: element.key, placement: element.placement, descriptor: element.descriptor }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); if (element.kind === "field") obj.initializer = element.initializer; return obj; }, toElementDescriptors: function toElementDescriptors(elementObjects) { if (elementObjects === undefined) return; return hassio_addon_store_toArray(elementObjects).map(function (elementObject) { var element = this.toElementDescriptor(elementObject); this.disallowProperty(elementObject, "finisher", "An element descriptor"); this.disallowProperty(elementObject, "extras", "An element descriptor"); return element; }, this); }, toElementDescriptor: function toElementDescriptor(elementObject) { var kind = String(elementObject.kind); if (kind !== "method" && kind !== "field") { throw new TypeError('An element descriptor\'s .kind property must be either "method" or' + ' "field", but a decorator created an element descriptor with' + ' .kind "' + kind + '"'); } var key = hassio_addon_store_toPropertyKey(elementObject.key); var placement = String(elementObject.placement); if (placement !== "static" && placement !== "prototype" && placement !== "own") { throw new TypeError('An element descriptor\'s .placement property must be one of "static",' + ' "prototype" or "own", but a decorator created an element descriptor' + ' with .placement "' + placement + '"'); } var descriptor = elementObject.descriptor; this.disallowProperty(elementObject, "elements", "An element descriptor"); var element = { kind: kind, key: key, placement: placement, descriptor: Object.assign({}, descriptor) }; if (kind !== "field") { this.disallowProperty(elementObject, "initializer", "A method descriptor"); } else { this.disallowProperty(descriptor, "get", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "set", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "value", "The property descriptor of a field descriptor"); element.initializer = elementObject.initializer; } return element; }, toElementFinisherExtras: function toElementFinisherExtras(elementObject) { var element = this.toElementDescriptor(elementObject); var finisher = hassio_addon_store_optionalCallableProperty(elementObject, "finisher"); var extras = this.toElementDescriptors(elementObject.extras); return { element: element, finisher: finisher, extras: extras }; }, fromClassDescriptor: function fromClassDescriptor(elements) { var obj = { kind: "class", elements: elements.map(this.fromElementDescriptor, this) }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); return obj; }, toClassDescriptor: function toClassDescriptor(obj) { var kind = String(obj.kind); if (kind !== "class") { throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator' + ' created a class descriptor with .kind "' + kind + '"'); } this.disallowProperty(obj, "key", "A class descriptor"); this.disallowProperty(obj, "placement", "A class descriptor"); this.disallowProperty(obj, "descriptor", "A class descriptor"); this.disallowProperty(obj, "initializer", "A class descriptor"); this.disallowProperty(obj, "extras", "A class descriptor"); var finisher = hassio_addon_store_optionalCallableProperty(obj, "finisher"); var elements = this.toElementDescriptors(obj.elements); return { elements: elements, finisher: finisher }; }, runClassFinishers: function runClassFinishers(constructor, finishers) { for (var i = 0; i < finishers.length; i++) { var newConstructor = (0, finishers[i])(constructor); if (newConstructor !== undefined) { if (typeof newConstructor !== "function") { throw new TypeError("Finishers must return a constructor."); } constructor = newConstructor; } } return constructor; }, disallowProperty: function disallowProperty(obj, name, objectType) { if (obj[name] !== undefined) { throw new TypeError(objectType + " can't have a ." + name + " property."); } } }; return api; }

function hassio_addon_store_createElementDescriptor(def) { var key = hassio_addon_store_toPropertyKey(def.key); var descriptor; if (def.kind === "method") { descriptor = { value: def.value, writable: true, configurable: true, enumerable: false }; } else if (def.kind === "get") { descriptor = { get: def.value, configurable: true, enumerable: false }; } else if (def.kind === "set") { descriptor = { set: def.value, configurable: true, enumerable: false }; } else if (def.kind === "field") { descriptor = { configurable: true, writable: true, enumerable: true }; } var element = { kind: def.kind === "field" ? "field" : "method", key: key, placement: def["static"] ? "static" : def.kind === "field" ? "own" : "prototype", descriptor: descriptor }; if (def.decorators) element.decorators = def.decorators; if (def.kind === "field") element.initializer = def.value; return element; }

function hassio_addon_store_coalesceGetterSetter(element, other) { if (element.descriptor.get !== undefined) { other.descriptor.get = element.descriptor.get; } else { other.descriptor.set = element.descriptor.set; } }

function hassio_addon_store_coalesceClassElements(elements) { var newElements = []; var isSameElement = function isSameElement(other) { return other.kind === "method" && other.key === element.key && other.placement === element.placement; }; for (var i = 0; i < elements.length; i++) { var element = elements[i]; var other; if (element.kind === "method" && (other = newElements.find(isSameElement))) { if (hassio_addon_store_isDataDescriptor(element.descriptor) || hassio_addon_store_isDataDescriptor(other.descriptor)) { if (hassio_addon_store_hasDecorators(element) || hassio_addon_store_hasDecorators(other)) { throw new ReferenceError("Duplicated methods (" + element.key + ") can't be decorated."); } other.descriptor = element.descriptor; } else { if (hassio_addon_store_hasDecorators(element)) { if (hassio_addon_store_hasDecorators(other)) { throw new ReferenceError("Decorators can't be placed on different accessors with for " + "the same property (" + element.key + ")."); } other.decorators = element.decorators; } hassio_addon_store_coalesceGetterSetter(element, other); } } else { newElements.push(element); } } return newElements; }

function hassio_addon_store_hasDecorators(element) { return element.decorators && element.decorators.length; }

function hassio_addon_store_isDataDescriptor(desc) { return desc !== undefined && !(desc.value === undefined && desc.writable === undefined); }

function hassio_addon_store_optionalCallableProperty(obj, name) { var value = obj[name]; if (value !== undefined && typeof value !== "function") { throw new TypeError("Expected '" + name + "' to be a function"); } return value; }

function hassio_addon_store_toPropertyKey(arg) { var key = hassio_addon_store_toPrimitive(arg, "string"); return hassio_addon_store_typeof(key) === "symbol" ? key : String(key); }

function hassio_addon_store_toPrimitive(input, hint) { if (hassio_addon_store_typeof(input) !== "object" || input === null) return input; var prim = input[Symbol.toPrimitive]; if (prim !== undefined) { var res = prim.call(input, hint || "default"); if (hassio_addon_store_typeof(res) !== "object") return res; throw new TypeError("@@toPrimitive must return a primitive value."); } return (hint === "string" ? String : Number)(input); }

function hassio_addon_store_toArray(arr) { return hassio_addon_store_arrayWithHoles(arr) || hassio_addon_store_iterableToArray(arr) || hassio_addon_store_unsupportedIterableToArray(arr) || hassio_addon_store_nonIterableRest(); }

function hassio_addon_store_nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function hassio_addon_store_unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return hassio_addon_store_arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(n); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return hassio_addon_store_arrayLikeToArray(o, minLen); }

function hassio_addon_store_arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function hassio_addon_store_iterableToArray(iter) { if (typeof Symbol !== "undefined" && Symbol.iterator in Object(iter)) return Array.from(iter); }

function hassio_addon_store_arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }

function hassio_addon_store_get(target, property, receiver) { if (typeof Reflect !== "undefined" && Reflect.get) { hassio_addon_store_get = Reflect.get; } else { hassio_addon_store_get = function _get(target, property, receiver) { var base = hassio_addon_store_superPropBase(target, property); if (!base) return; var desc = Object.getOwnPropertyDescriptor(base, property); if (desc.get) { return desc.get.call(receiver); } return desc.value; }; } return hassio_addon_store_get(target, property, receiver || target); }

function hassio_addon_store_superPropBase(object, property) { while (!Object.prototype.hasOwnProperty.call(object, property)) { object = hassio_addon_store_getPrototypeOf(object); if (object === null) break; } return object; }

function hassio_addon_store_getPrototypeOf(o) { hassio_addon_store_getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return hassio_addon_store_getPrototypeOf(o); }












var sortRepos = function sortRepos(a, b) {
  if (a.slug === "local") {
    return -1;
  }

  if (b.slug === "local") {
    return 1;
  }

  if (a.slug === "core") {
    return -1;
  }

  if (b.slug === "core") {
    return 1;
  }

  return a.name.toUpperCase() < b.name.toUpperCase() ? -1 : 1;
};

var hassio_addon_store_HassioAddonStore = hassio_addon_store_decorate(null, function (_initialize, _LitElement) {
  var HassioAddonStore = /*#__PURE__*/function (_LitElement2) {
    hassio_addon_store_inherits(HassioAddonStore, _LitElement2);

    var _super = hassio_addon_store_createSuper(HassioAddonStore);

    function HassioAddonStore() {
      var _this;

      hassio_addon_store_classCallCheck(this, HassioAddonStore);

      for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
        args[_key] = arguments[_key];
      }

      _this = _super.call.apply(_super, [this].concat(args));

      _initialize(hassio_addon_store_assertThisInitialized(_this));

      return _this;
    }

    return HassioAddonStore;
  }(_LitElement);

  return {
    F: HassioAddonStore,
    d: [{
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])({
        attribute: false
      })],
      key: "hass",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])({
        type: Boolean
      })],
      key: "narrow",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])({
        attribute: false
      })],
      key: "route",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])({
        attribute: false
      })],
      key: "_addons",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])({
        attribute: false
      })],
      key: "_repos",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "_filter",
      value: void 0
    }, {
      kind: "method",
      key: "refreshData",
      value: function () {
        var _refreshData = hassio_addon_store_asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee() {
          return regeneratorRuntime.wrap(function _callee$(_context) {
            while (1) {
              switch (_context.prev = _context.next) {
                case 0:
                  this._repos = undefined;
                  this._addons = undefined;
                  this._filter = undefined;
                  _context.next = 5;
                  return Object(hassio_addon["g" /* reloadHassioAddons */])(this.hass);

                case 5:
                  _context.next = 7;
                  return this._loadData();

                case 7:
                case "end":
                  return _context.stop();
              }
            }
          }, _callee, this);
        }));

        function refreshData() {
          return _refreshData.apply(this, arguments);
        }

        return refreshData;
      }()
    }, {
      kind: "method",
      key: "render",
      value: function render() {
        var _this2 = this,
            _this$hass$userData;

        var repos = [];

        if (this._repos) {
          var _iterator = _createForOfIteratorHelper(this._repos),
              _step;

          try {
            var _loop = function _loop() {
              var repo = _step.value;

              var addons = _this2._addons.filter(function (addon) {
                return addon.repository === repo.slug;
              });

              if (addons.length === 0) {
                return "continue";
              }

              repos.push(Object(lit_html["f" /* html */])(hassio_addon_store_templateObject(), _this2.hass, repo, addons, _this2._filter));
            };

            for (_iterator.s(); !(_step = _iterator.n()).done;) {
              var _ret = _loop();

              if (_ret === "continue") continue;
            }
          } catch (err) {
            _iterator.e(err);
          } finally {
            _iterator.f();
          }
        }

        return Object(lit_html["f" /* html */])(hassio_addon_store_templateObject2(), this.hass, this.narrow, this.route, supervisorTabs, this._manageRepositories, this.refreshData, repos.length === 0 ? Object(lit_html["f" /* html */])(hassio_addon_store_templateObject3()) : Object(lit_html["f" /* html */])(hassio_addon_store_templateObject4(), this._filter, this._filterChanged, repos), !((_this$hass$userData = this.hass.userData) === null || _this$hass$userData === void 0 ? void 0 : _this$hass$userData.showAdvanced) ? Object(lit_html["f" /* html */])(_templateObject5()) : "");
      }
    }, {
      kind: "method",
      key: "firstUpdated",
      value: function firstUpdated(changedProps) {
        var _this3 = this;

        hassio_addon_store_get(hassio_addon_store_getPrototypeOf(HassioAddonStore.prototype), "firstUpdated", this).call(this, changedProps);

        this.addEventListener("hass-api-called", function (ev) {
          return _this3.apiCalled(ev);
        });

        this._loadData();
      }
    }, {
      kind: "method",
      key: "apiCalled",
      value: function apiCalled(ev) {
        if (ev.detail.success) {
          this._loadData();
        }
      }
    }, {
      kind: "method",
      key: "_manageRepositories",
      value: function () {
        var _manageRepositories2 = hassio_addon_store_asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee2() {
          var _this4 = this;

          return regeneratorRuntime.wrap(function _callee2$(_context2) {
            while (1) {
              switch (_context2.prev = _context2.next) {
                case 0:
                  show_dialog_repositories_showRepositoriesDialog(this, {
                    repos: this._repos,
                    loadData: function loadData() {
                      return _this4._loadData();
                    }
                  });

                case 1:
                case "end":
                  return _context2.stop();
              }
            }
          }, _callee2, this);
        }));

        function _manageRepositories() {
          return _manageRepositories2.apply(this, arguments);
        }

        return _manageRepositories;
      }()
    }, {
      kind: "method",
      key: "_loadData",
      value: function () {
        var _loadData2 = hassio_addon_store_asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee3() {
          var addonsInfo;
          return regeneratorRuntime.wrap(function _callee3$(_context3) {
            while (1) {
              switch (_context3.prev = _context3.next) {
                case 0:
                  _context3.prev = 0;
                  _context3.next = 3;
                  return Object(hassio_addon["e" /* fetchHassioAddonsInfo */])(this.hass);

                case 3:
                  addonsInfo = _context3.sent;
                  this._repos = addonsInfo.repositories;

                  this._repos.sort(sortRepos);

                  this._addons = addonsInfo.addons;
                  _context3.next = 12;
                  break;

                case 9:
                  _context3.prev = 9;
                  _context3.t0 = _context3["catch"](0);
                  alert("Failed to fetch add-on info");

                case 12:
                case "end":
                  return _context3.stop();
              }
            }
          }, _callee3, this, [[0, 9]]);
        }));

        function _loadData() {
          return _loadData2.apply(this, arguments);
        }

        return _loadData;
      }()
    }, {
      kind: "method",
      key: "_filterChanged",
      value: function () {
        var _filterChanged2 = hassio_addon_store_asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee4(e) {
          return regeneratorRuntime.wrap(function _callee4$(_context4) {
            while (1) {
              switch (_context4.prev = _context4.next) {
                case 0:
                  this._filter = e.detail.value;

                case 1:
                case "end":
                  return _context4.stop();
              }
            }
          }, _callee4, this);
        }));

        function _filterChanged(_x) {
          return _filterChanged2.apply(this, arguments);
        }

        return _filterChanged;
      }()
    }, {
      kind: "get",
      "static": true,
      key: "styles",
      value: function styles() {
        return Object(lit_element["c" /* css */])(_templateObject6());
      }
    }]
  };
}, lit_element["a" /* LitElement */]);

customElements.define("hassio-addon-store", hassio_addon_store_HassioAddonStore);
// CONCATENATED MODULE: ./hassio/src/dashboard/hassio-addons.ts
function hassio_addons_typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { hassio_addons_typeof = function _typeof(obj) { return typeof obj; }; } else { hassio_addons_typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return hassio_addons_typeof(obj); }

function hassio_addons_templateObject4() {
  var data = hassio_addons_taggedTemplateLiteral(["\n        paper-card {\n          cursor: pointer;\n        }\n      "]);

  hassio_addons_templateObject4 = function _templateObject4() {
    return data;
  };

  return data;
}

function hassio_addons_templateObject3() {
  var data = hassio_addons_taggedTemplateLiteral(["\n                    <paper-card .addon=", " @click=", ">\n                      <div class=\"card-content\">\n                        <hassio-card-content\n                          .hass=", "\n                          .title=", "\n                          .description=", "\n                          available\n                          .showTopbar=", "\n                          topbarClass=\"update\"\n                          .icon=", "\n                          .iconTitle=", "\n                          .iconClass=", "\n                          .iconImage=", "\n                        ></hassio-card-content>\n                      </div>\n                    </paper-card>\n                  "]);

  hassio_addons_templateObject3 = function _templateObject3() {
    return data;
  };

  return data;
}

function hassio_addons_templateObject2() {
  var data = hassio_addons_taggedTemplateLiteral(["\n                <paper-card>\n                  <div class=\"card-content\">\n                    You don't have any add-ons installed yet. Head over to\n                    <a href=\"#\" @click=", ">the add-on store</a>\n                    to get started!\n                  </div>\n                </paper-card>\n              "]);

  hassio_addons_templateObject2 = function _templateObject2() {
    return data;
  };

  return data;
}

function hassio_addons_templateObject() {
  var data = hassio_addons_taggedTemplateLiteral(["\n      <div class=\"content\">\n        <h1>Add-ons</h1>\n        <div class=\"card-group\">\n          ", "\n        </div>\n      </div>\n    "]);

  hassio_addons_templateObject = function _templateObject() {
    return data;
  };

  return data;
}

function hassio_addons_taggedTemplateLiteral(strings, raw) { if (!raw) { raw = strings.slice(0); } return Object.freeze(Object.defineProperties(strings, { raw: { value: Object.freeze(raw) } })); }

function hassio_addons_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function hassio_addons_inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) hassio_addons_setPrototypeOf(subClass, superClass); }

function hassio_addons_setPrototypeOf(o, p) { hassio_addons_setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return hassio_addons_setPrototypeOf(o, p); }

function hassio_addons_createSuper(Derived) { return function () { var Super = hassio_addons_getPrototypeOf(Derived), result; if (hassio_addons_isNativeReflectConstruct()) { var NewTarget = hassio_addons_getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return hassio_addons_possibleConstructorReturn(this, result); }; }

function hassio_addons_possibleConstructorReturn(self, call) { if (call && (hassio_addons_typeof(call) === "object" || typeof call === "function")) { return call; } return hassio_addons_assertThisInitialized(self); }

function hassio_addons_assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function hassio_addons_isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Date.prototype.toString.call(Reflect.construct(Date, [], function () {})); return true; } catch (e) { return false; } }

function hassio_addons_getPrototypeOf(o) { hassio_addons_getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return hassio_addons_getPrototypeOf(o); }

function hassio_addons_decorate(decorators, factory, superClass, mixins) { var api = hassio_addons_getDecoratorsApi(); if (mixins) { for (var i = 0; i < mixins.length; i++) { api = mixins[i](api); } } var r = factory(function initialize(O) { api.initializeInstanceElements(O, decorated.elements); }, superClass); var decorated = api.decorateClass(hassio_addons_coalesceClassElements(r.d.map(hassio_addons_createElementDescriptor)), decorators); api.initializeClassElements(r.F, decorated.elements); return api.runClassFinishers(r.F, decorated.finishers); }

function hassio_addons_getDecoratorsApi() { hassio_addons_getDecoratorsApi = function _getDecoratorsApi() { return api; }; var api = { elementsDefinitionOrder: [["method"], ["field"]], initializeInstanceElements: function initializeInstanceElements(O, elements) { ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { if (element.kind === kind && element.placement === "own") { this.defineClassElement(O, element); } }, this); }, this); }, initializeClassElements: function initializeClassElements(F, elements) { var proto = F.prototype; ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { var placement = element.placement; if (element.kind === kind && (placement === "static" || placement === "prototype")) { var receiver = placement === "static" ? F : proto; this.defineClassElement(receiver, element); } }, this); }, this); }, defineClassElement: function defineClassElement(receiver, element) { var descriptor = element.descriptor; if (element.kind === "field") { var initializer = element.initializer; descriptor = { enumerable: descriptor.enumerable, writable: descriptor.writable, configurable: descriptor.configurable, value: initializer === void 0 ? void 0 : initializer.call(receiver) }; } Object.defineProperty(receiver, element.key, descriptor); }, decorateClass: function decorateClass(elements, decorators) { var newElements = []; var finishers = []; var placements = { "static": [], prototype: [], own: [] }; elements.forEach(function (element) { this.addElementPlacement(element, placements); }, this); elements.forEach(function (element) { if (!hassio_addons_hasDecorators(element)) return newElements.push(element); var elementFinishersExtras = this.decorateElement(element, placements); newElements.push(elementFinishersExtras.element); newElements.push.apply(newElements, elementFinishersExtras.extras); finishers.push.apply(finishers, elementFinishersExtras.finishers); }, this); if (!decorators) { return { elements: newElements, finishers: finishers }; } var result = this.decorateConstructor(newElements, decorators); finishers.push.apply(finishers, result.finishers); result.finishers = finishers; return result; }, addElementPlacement: function addElementPlacement(element, placements, silent) { var keys = placements[element.placement]; if (!silent && keys.indexOf(element.key) !== -1) { throw new TypeError("Duplicated element (" + element.key + ")"); } keys.push(element.key); }, decorateElement: function decorateElement(element, placements) { var extras = []; var finishers = []; for (var decorators = element.decorators, i = decorators.length - 1; i >= 0; i--) { var keys = placements[element.placement]; keys.splice(keys.indexOf(element.key), 1); var elementObject = this.fromElementDescriptor(element); var elementFinisherExtras = this.toElementFinisherExtras((0, decorators[i])(elementObject) || elementObject); element = elementFinisherExtras.element; this.addElementPlacement(element, placements); if (elementFinisherExtras.finisher) { finishers.push(elementFinisherExtras.finisher); } var newExtras = elementFinisherExtras.extras; if (newExtras) { for (var j = 0; j < newExtras.length; j++) { this.addElementPlacement(newExtras[j], placements); } extras.push.apply(extras, newExtras); } } return { element: element, finishers: finishers, extras: extras }; }, decorateConstructor: function decorateConstructor(elements, decorators) { var finishers = []; for (var i = decorators.length - 1; i >= 0; i--) { var obj = this.fromClassDescriptor(elements); var elementsAndFinisher = this.toClassDescriptor((0, decorators[i])(obj) || obj); if (elementsAndFinisher.finisher !== undefined) { finishers.push(elementsAndFinisher.finisher); } if (elementsAndFinisher.elements !== undefined) { elements = elementsAndFinisher.elements; for (var j = 0; j < elements.length - 1; j++) { for (var k = j + 1; k < elements.length; k++) { if (elements[j].key === elements[k].key && elements[j].placement === elements[k].placement) { throw new TypeError("Duplicated element (" + elements[j].key + ")"); } } } } } return { elements: elements, finishers: finishers }; }, fromElementDescriptor: function fromElementDescriptor(element) { var obj = { kind: element.kind, key: element.key, placement: element.placement, descriptor: element.descriptor }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); if (element.kind === "field") obj.initializer = element.initializer; return obj; }, toElementDescriptors: function toElementDescriptors(elementObjects) { if (elementObjects === undefined) return; return hassio_addons_toArray(elementObjects).map(function (elementObject) { var element = this.toElementDescriptor(elementObject); this.disallowProperty(elementObject, "finisher", "An element descriptor"); this.disallowProperty(elementObject, "extras", "An element descriptor"); return element; }, this); }, toElementDescriptor: function toElementDescriptor(elementObject) { var kind = String(elementObject.kind); if (kind !== "method" && kind !== "field") { throw new TypeError('An element descriptor\'s .kind property must be either "method" or' + ' "field", but a decorator created an element descriptor with' + ' .kind "' + kind + '"'); } var key = hassio_addons_toPropertyKey(elementObject.key); var placement = String(elementObject.placement); if (placement !== "static" && placement !== "prototype" && placement !== "own") { throw new TypeError('An element descriptor\'s .placement property must be one of "static",' + ' "prototype" or "own", but a decorator created an element descriptor' + ' with .placement "' + placement + '"'); } var descriptor = elementObject.descriptor; this.disallowProperty(elementObject, "elements", "An element descriptor"); var element = { kind: kind, key: key, placement: placement, descriptor: Object.assign({}, descriptor) }; if (kind !== "field") { this.disallowProperty(elementObject, "initializer", "A method descriptor"); } else { this.disallowProperty(descriptor, "get", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "set", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "value", "The property descriptor of a field descriptor"); element.initializer = elementObject.initializer; } return element; }, toElementFinisherExtras: function toElementFinisherExtras(elementObject) { var element = this.toElementDescriptor(elementObject); var finisher = hassio_addons_optionalCallableProperty(elementObject, "finisher"); var extras = this.toElementDescriptors(elementObject.extras); return { element: element, finisher: finisher, extras: extras }; }, fromClassDescriptor: function fromClassDescriptor(elements) { var obj = { kind: "class", elements: elements.map(this.fromElementDescriptor, this) }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); return obj; }, toClassDescriptor: function toClassDescriptor(obj) { var kind = String(obj.kind); if (kind !== "class") { throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator' + ' created a class descriptor with .kind "' + kind + '"'); } this.disallowProperty(obj, "key", "A class descriptor"); this.disallowProperty(obj, "placement", "A class descriptor"); this.disallowProperty(obj, "descriptor", "A class descriptor"); this.disallowProperty(obj, "initializer", "A class descriptor"); this.disallowProperty(obj, "extras", "A class descriptor"); var finisher = hassio_addons_optionalCallableProperty(obj, "finisher"); var elements = this.toElementDescriptors(obj.elements); return { elements: elements, finisher: finisher }; }, runClassFinishers: function runClassFinishers(constructor, finishers) { for (var i = 0; i < finishers.length; i++) { var newConstructor = (0, finishers[i])(constructor); if (newConstructor !== undefined) { if (typeof newConstructor !== "function") { throw new TypeError("Finishers must return a constructor."); } constructor = newConstructor; } } return constructor; }, disallowProperty: function disallowProperty(obj, name, objectType) { if (obj[name] !== undefined) { throw new TypeError(objectType + " can't have a ." + name + " property."); } } }; return api; }

function hassio_addons_createElementDescriptor(def) { var key = hassio_addons_toPropertyKey(def.key); var descriptor; if (def.kind === "method") { descriptor = { value: def.value, writable: true, configurable: true, enumerable: false }; } else if (def.kind === "get") { descriptor = { get: def.value, configurable: true, enumerable: false }; } else if (def.kind === "set") { descriptor = { set: def.value, configurable: true, enumerable: false }; } else if (def.kind === "field") { descriptor = { configurable: true, writable: true, enumerable: true }; } var element = { kind: def.kind === "field" ? "field" : "method", key: key, placement: def["static"] ? "static" : def.kind === "field" ? "own" : "prototype", descriptor: descriptor }; if (def.decorators) element.decorators = def.decorators; if (def.kind === "field") element.initializer = def.value; return element; }

function hassio_addons_coalesceGetterSetter(element, other) { if (element.descriptor.get !== undefined) { other.descriptor.get = element.descriptor.get; } else { other.descriptor.set = element.descriptor.set; } }

function hassio_addons_coalesceClassElements(elements) { var newElements = []; var isSameElement = function isSameElement(other) { return other.kind === "method" && other.key === element.key && other.placement === element.placement; }; for (var i = 0; i < elements.length; i++) { var element = elements[i]; var other; if (element.kind === "method" && (other = newElements.find(isSameElement))) { if (hassio_addons_isDataDescriptor(element.descriptor) || hassio_addons_isDataDescriptor(other.descriptor)) { if (hassio_addons_hasDecorators(element) || hassio_addons_hasDecorators(other)) { throw new ReferenceError("Duplicated methods (" + element.key + ") can't be decorated."); } other.descriptor = element.descriptor; } else { if (hassio_addons_hasDecorators(element)) { if (hassio_addons_hasDecorators(other)) { throw new ReferenceError("Decorators can't be placed on different accessors with for " + "the same property (" + element.key + ")."); } other.decorators = element.decorators; } hassio_addons_coalesceGetterSetter(element, other); } } else { newElements.push(element); } } return newElements; }

function hassio_addons_hasDecorators(element) { return element.decorators && element.decorators.length; }

function hassio_addons_isDataDescriptor(desc) { return desc !== undefined && !(desc.value === undefined && desc.writable === undefined); }

function hassio_addons_optionalCallableProperty(obj, name) { var value = obj[name]; if (value !== undefined && typeof value !== "function") { throw new TypeError("Expected '" + name + "' to be a function"); } return value; }

function hassio_addons_toPropertyKey(arg) { var key = hassio_addons_toPrimitive(arg, "string"); return hassio_addons_typeof(key) === "symbol" ? key : String(key); }

function hassio_addons_toPrimitive(input, hint) { if (hassio_addons_typeof(input) !== "object" || input === null) return input; var prim = input[Symbol.toPrimitive]; if (prim !== undefined) { var res = prim.call(input, hint || "default"); if (hassio_addons_typeof(res) !== "object") return res; throw new TypeError("@@toPrimitive must return a primitive value."); } return (hint === "string" ? String : Number)(input); }

function hassio_addons_toArray(arr) { return hassio_addons_arrayWithHoles(arr) || hassio_addons_iterableToArray(arr) || hassio_addons_unsupportedIterableToArray(arr) || hassio_addons_nonIterableRest(); }

function hassio_addons_nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function hassio_addons_unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return hassio_addons_arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(n); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return hassio_addons_arrayLikeToArray(o, minLen); }

function hassio_addons_arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function hassio_addons_iterableToArray(iter) { if (typeof Symbol !== "undefined" && Symbol.iterator in Object(iter)) return Array.from(iter); }

function hassio_addons_arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }









var hassio_addons_HassioAddons = hassio_addons_decorate([Object(lit_element["d" /* customElement */])("hassio-addons")], function (_initialize, _LitElement) {
  var HassioAddons = /*#__PURE__*/function (_LitElement2) {
    hassio_addons_inherits(HassioAddons, _LitElement2);

    var _super = hassio_addons_createSuper(HassioAddons);

    function HassioAddons() {
      var _this;

      hassio_addons_classCallCheck(this, HassioAddons);

      for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
        args[_key] = arguments[_key];
      }

      _this = _super.call.apply(_super, [this].concat(args));

      _initialize(hassio_addons_assertThisInitialized(_this));

      return _this;
    }

    return HassioAddons;
  }(_LitElement);

  return {
    F: HassioAddons,
    d: [{
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "hass",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "addons",
      value: void 0
    }, {
      kind: "method",
      key: "render",
      value: function render() {
        var _this2 = this;

        return Object(lit_element["e" /* html */])(hassio_addons_templateObject(), !this.addons ? Object(lit_element["e" /* html */])(hassio_addons_templateObject2(), this._openStore) : this.addons.sort(function (a, b) {
          return a.name > b.name ? 1 : -1;
        }).map(function (addon) {
          return Object(lit_element["e" /* html */])(hassio_addons_templateObject3(), addon, _this2._addonTapped, _this2.hass, addon.name, addon.description, addon.installed !== addon.version, addon.installed !== addon.version ? "hassio:arrow-up-bold-circle" : "hassio:puzzle", addon.state !== "started" ? "Add-on is stopped" : addon.installed !== addon.version ? "New version available" : "Add-on is running", addon.installed && addon.installed !== addon.version ? addon.state === "started" ? "update" : "update stopped" : addon.installed && addon.state === "started" ? "running" : "stopped", Object(version["a" /* atLeastVersion */])(_this2.hass.config.version, 0, 105) && addon.icon ? "/api/hassio/addons/".concat(addon.slug, "/icon") : undefined);
        }));
      }
    }, {
      kind: "get",
      "static": true,
      key: "styles",
      value: function styles() {
        return [resources_styles["b" /* haStyle */], hassio_style["a" /* hassioStyle */], Object(lit_element["c" /* css */])(hassio_addons_templateObject4())];
      }
    }, {
      kind: "method",
      key: "_addonTapped",
      value: function _addonTapped(ev) {
        Object(common_navigate["a" /* navigate */])(this, "/hassio/addon/".concat(ev.currentTarget.addon.slug, "/info"));
      }
    }, {
      kind: "method",
      key: "_openStore",
      value: function _openStore() {
        Object(common_navigate["a" /* navigate */])(this, "/hassio/store");
      }
    }]
  };
}, lit_element["a" /* LitElement */]);
// EXTERNAL MODULE: ./node_modules/@material/mwc-button/mwc-button.js + 12 modules
var mwc_button = __webpack_require__(18);

// EXTERNAL MODULE: ./src/components/buttons/ha-call-api-button.js
var ha_call_api_button = __webpack_require__(71);

// CONCATENATED MODULE: ./hassio/src/dashboard/hassio-update.ts
function _templateObject7() {
  var data = hassio_update_taggedTemplateLiteral(["\n        .icon {\n          --mdc-icon-size: 48px;\n          float: right;\n          margin: 0 0 2px 10px;\n          color: var(--primary-text-color);\n        }\n        .update-heading {\n          font-size: var(--paper-font-subhead_-_font-size);\n          font-weight: 500;\n          margin-bottom: 0.5em;\n          color: var(--primary-text-color);\n        }\n        .warning {\n          color: var(--secondary-text-color);\n        }\n        .card-content {\n          height: calc(100% - 47px);\n          box-sizing: border-box;\n        }\n        .card-actions {\n          text-align: right;\n        }\n        .errors {\n          color: var(--google-red-500);\n          padding: 16px;\n        }\n        a {\n          text-decoration: none;\n        }\n      "]);

  _templateObject7 = function _templateObject7() {
    return data;
  };

  return data;
}

function hassio_update_typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { hassio_update_typeof = function _typeof(obj) { return typeof obj; }; } else { hassio_update_typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return hassio_update_typeof(obj); }

function hassio_update_templateObject6() {
  var data = hassio_update_taggedTemplateLiteral(["\n                <div class=\"icon\">\n                  <ha-icon .icon=", "></ha-icon>\n                </div>\n              "]);

  hassio_update_templateObject6 = function _templateObject6() {
    return data;
  };

  return data;
}

function hassio_update_templateObject5() {
  var data = hassio_update_taggedTemplateLiteral(["\n      <paper-card>\n        <div class=\"card-content\">\n          ", "\n          <div class=\"update-heading\">", " ", "</div>\n          <div class=\"warning\">\n            You are currently running version ", "\n          </div>\n        </div>\n        <div class=\"card-actions\">\n          <a href=\"", "\" target=\"_blank\" rel=\"noreferrer\">\n            <mwc-button>Release notes</mwc-button>\n          </a>\n          <ha-call-api-button\n            .hass=", "\n            .path=", "\n            @hass-api-called=", "\n          >\n            Update\n          </ha-call-api-button>\n        </div>\n      </paper-card>\n    "]);

  hassio_update_templateObject5 = function _templateObject5() {
    return data;
  };

  return data;
}

function hassio_update_templateObject4() {
  var data = hassio_update_taggedTemplateLiteral([""]);

  hassio_update_templateObject4 = function _templateObject4() {
    return data;
  };

  return data;
}

function hassio_update_templateObject3() {
  var data = hassio_update_taggedTemplateLiteral([" <div class=\"error\">Error: ", "</div> "]);

  hassio_update_templateObject3 = function _templateObject3() {
    return data;
  };

  return data;
}

function hassio_update_templateObject2() {
  var data = hassio_update_taggedTemplateLiteral(["\n      <div class=\"content\">\n        ", "\n        <h1>\n          ", "\n        </h1>\n        <div class=\"card-group\">\n          ", "\n          ", "\n          ", "\n        </div>\n      </div>\n    "]);

  hassio_update_templateObject2 = function _templateObject2() {
    return data;
  };

  return data;
}

function hassio_update_templateObject() {
  var data = hassio_update_taggedTemplateLiteral([""]);

  hassio_update_templateObject = function _templateObject() {
    return data;
  };

  return data;
}

function hassio_update_taggedTemplateLiteral(strings, raw) { if (!raw) { raw = strings.slice(0); } return Object.freeze(Object.defineProperties(strings, { raw: { value: Object.freeze(raw) } })); }

function hassio_update_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function hassio_update_inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) hassio_update_setPrototypeOf(subClass, superClass); }

function hassio_update_setPrototypeOf(o, p) { hassio_update_setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return hassio_update_setPrototypeOf(o, p); }

function hassio_update_createSuper(Derived) { return function () { var Super = hassio_update_getPrototypeOf(Derived), result; if (hassio_update_isNativeReflectConstruct()) { var NewTarget = hassio_update_getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return hassio_update_possibleConstructorReturn(this, result); }; }

function hassio_update_possibleConstructorReturn(self, call) { if (call && (hassio_update_typeof(call) === "object" || typeof call === "function")) { return call; } return hassio_update_assertThisInitialized(self); }

function hassio_update_assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function hassio_update_isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Date.prototype.toString.call(Reflect.construct(Date, [], function () {})); return true; } catch (e) { return false; } }

function hassio_update_getPrototypeOf(o) { hassio_update_getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return hassio_update_getPrototypeOf(o); }

function hassio_update_decorate(decorators, factory, superClass, mixins) { var api = hassio_update_getDecoratorsApi(); if (mixins) { for (var i = 0; i < mixins.length; i++) { api = mixins[i](api); } } var r = factory(function initialize(O) { api.initializeInstanceElements(O, decorated.elements); }, superClass); var decorated = api.decorateClass(hassio_update_coalesceClassElements(r.d.map(hassio_update_createElementDescriptor)), decorators); api.initializeClassElements(r.F, decorated.elements); return api.runClassFinishers(r.F, decorated.finishers); }

function hassio_update_getDecoratorsApi() { hassio_update_getDecoratorsApi = function _getDecoratorsApi() { return api; }; var api = { elementsDefinitionOrder: [["method"], ["field"]], initializeInstanceElements: function initializeInstanceElements(O, elements) { ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { if (element.kind === kind && element.placement === "own") { this.defineClassElement(O, element); } }, this); }, this); }, initializeClassElements: function initializeClassElements(F, elements) { var proto = F.prototype; ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { var placement = element.placement; if (element.kind === kind && (placement === "static" || placement === "prototype")) { var receiver = placement === "static" ? F : proto; this.defineClassElement(receiver, element); } }, this); }, this); }, defineClassElement: function defineClassElement(receiver, element) { var descriptor = element.descriptor; if (element.kind === "field") { var initializer = element.initializer; descriptor = { enumerable: descriptor.enumerable, writable: descriptor.writable, configurable: descriptor.configurable, value: initializer === void 0 ? void 0 : initializer.call(receiver) }; } Object.defineProperty(receiver, element.key, descriptor); }, decorateClass: function decorateClass(elements, decorators) { var newElements = []; var finishers = []; var placements = { "static": [], prototype: [], own: [] }; elements.forEach(function (element) { this.addElementPlacement(element, placements); }, this); elements.forEach(function (element) { if (!hassio_update_hasDecorators(element)) return newElements.push(element); var elementFinishersExtras = this.decorateElement(element, placements); newElements.push(elementFinishersExtras.element); newElements.push.apply(newElements, elementFinishersExtras.extras); finishers.push.apply(finishers, elementFinishersExtras.finishers); }, this); if (!decorators) { return { elements: newElements, finishers: finishers }; } var result = this.decorateConstructor(newElements, decorators); finishers.push.apply(finishers, result.finishers); result.finishers = finishers; return result; }, addElementPlacement: function addElementPlacement(element, placements, silent) { var keys = placements[element.placement]; if (!silent && keys.indexOf(element.key) !== -1) { throw new TypeError("Duplicated element (" + element.key + ")"); } keys.push(element.key); }, decorateElement: function decorateElement(element, placements) { var extras = []; var finishers = []; for (var decorators = element.decorators, i = decorators.length - 1; i >= 0; i--) { var keys = placements[element.placement]; keys.splice(keys.indexOf(element.key), 1); var elementObject = this.fromElementDescriptor(element); var elementFinisherExtras = this.toElementFinisherExtras((0, decorators[i])(elementObject) || elementObject); element = elementFinisherExtras.element; this.addElementPlacement(element, placements); if (elementFinisherExtras.finisher) { finishers.push(elementFinisherExtras.finisher); } var newExtras = elementFinisherExtras.extras; if (newExtras) { for (var j = 0; j < newExtras.length; j++) { this.addElementPlacement(newExtras[j], placements); } extras.push.apply(extras, newExtras); } } return { element: element, finishers: finishers, extras: extras }; }, decorateConstructor: function decorateConstructor(elements, decorators) { var finishers = []; for (var i = decorators.length - 1; i >= 0; i--) { var obj = this.fromClassDescriptor(elements); var elementsAndFinisher = this.toClassDescriptor((0, decorators[i])(obj) || obj); if (elementsAndFinisher.finisher !== undefined) { finishers.push(elementsAndFinisher.finisher); } if (elementsAndFinisher.elements !== undefined) { elements = elementsAndFinisher.elements; for (var j = 0; j < elements.length - 1; j++) { for (var k = j + 1; k < elements.length; k++) { if (elements[j].key === elements[k].key && elements[j].placement === elements[k].placement) { throw new TypeError("Duplicated element (" + elements[j].key + ")"); } } } } } return { elements: elements, finishers: finishers }; }, fromElementDescriptor: function fromElementDescriptor(element) { var obj = { kind: element.kind, key: element.key, placement: element.placement, descriptor: element.descriptor }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); if (element.kind === "field") obj.initializer = element.initializer; return obj; }, toElementDescriptors: function toElementDescriptors(elementObjects) { if (elementObjects === undefined) return; return hassio_update_toArray(elementObjects).map(function (elementObject) { var element = this.toElementDescriptor(elementObject); this.disallowProperty(elementObject, "finisher", "An element descriptor"); this.disallowProperty(elementObject, "extras", "An element descriptor"); return element; }, this); }, toElementDescriptor: function toElementDescriptor(elementObject) { var kind = String(elementObject.kind); if (kind !== "method" && kind !== "field") { throw new TypeError('An element descriptor\'s .kind property must be either "method" or' + ' "field", but a decorator created an element descriptor with' + ' .kind "' + kind + '"'); } var key = hassio_update_toPropertyKey(elementObject.key); var placement = String(elementObject.placement); if (placement !== "static" && placement !== "prototype" && placement !== "own") { throw new TypeError('An element descriptor\'s .placement property must be one of "static",' + ' "prototype" or "own", but a decorator created an element descriptor' + ' with .placement "' + placement + '"'); } var descriptor = elementObject.descriptor; this.disallowProperty(elementObject, "elements", "An element descriptor"); var element = { kind: kind, key: key, placement: placement, descriptor: Object.assign({}, descriptor) }; if (kind !== "field") { this.disallowProperty(elementObject, "initializer", "A method descriptor"); } else { this.disallowProperty(descriptor, "get", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "set", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "value", "The property descriptor of a field descriptor"); element.initializer = elementObject.initializer; } return element; }, toElementFinisherExtras: function toElementFinisherExtras(elementObject) { var element = this.toElementDescriptor(elementObject); var finisher = hassio_update_optionalCallableProperty(elementObject, "finisher"); var extras = this.toElementDescriptors(elementObject.extras); return { element: element, finisher: finisher, extras: extras }; }, fromClassDescriptor: function fromClassDescriptor(elements) { var obj = { kind: "class", elements: elements.map(this.fromElementDescriptor, this) }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); return obj; }, toClassDescriptor: function toClassDescriptor(obj) { var kind = String(obj.kind); if (kind !== "class") { throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator' + ' created a class descriptor with .kind "' + kind + '"'); } this.disallowProperty(obj, "key", "A class descriptor"); this.disallowProperty(obj, "placement", "A class descriptor"); this.disallowProperty(obj, "descriptor", "A class descriptor"); this.disallowProperty(obj, "initializer", "A class descriptor"); this.disallowProperty(obj, "extras", "A class descriptor"); var finisher = hassio_update_optionalCallableProperty(obj, "finisher"); var elements = this.toElementDescriptors(obj.elements); return { elements: elements, finisher: finisher }; }, runClassFinishers: function runClassFinishers(constructor, finishers) { for (var i = 0; i < finishers.length; i++) { var newConstructor = (0, finishers[i])(constructor); if (newConstructor !== undefined) { if (typeof newConstructor !== "function") { throw new TypeError("Finishers must return a constructor."); } constructor = newConstructor; } } return constructor; }, disallowProperty: function disallowProperty(obj, name, objectType) { if (obj[name] !== undefined) { throw new TypeError(objectType + " can't have a ." + name + " property."); } } }; return api; }

function hassio_update_createElementDescriptor(def) { var key = hassio_update_toPropertyKey(def.key); var descriptor; if (def.kind === "method") { descriptor = { value: def.value, writable: true, configurable: true, enumerable: false }; } else if (def.kind === "get") { descriptor = { get: def.value, configurable: true, enumerable: false }; } else if (def.kind === "set") { descriptor = { set: def.value, configurable: true, enumerable: false }; } else if (def.kind === "field") { descriptor = { configurable: true, writable: true, enumerable: true }; } var element = { kind: def.kind === "field" ? "field" : "method", key: key, placement: def["static"] ? "static" : def.kind === "field" ? "own" : "prototype", descriptor: descriptor }; if (def.decorators) element.decorators = def.decorators; if (def.kind === "field") element.initializer = def.value; return element; }

function hassio_update_coalesceGetterSetter(element, other) { if (element.descriptor.get !== undefined) { other.descriptor.get = element.descriptor.get; } else { other.descriptor.set = element.descriptor.set; } }

function hassio_update_coalesceClassElements(elements) { var newElements = []; var isSameElement = function isSameElement(other) { return other.kind === "method" && other.key === element.key && other.placement === element.placement; }; for (var i = 0; i < elements.length; i++) { var element = elements[i]; var other; if (element.kind === "method" && (other = newElements.find(isSameElement))) { if (hassio_update_isDataDescriptor(element.descriptor) || hassio_update_isDataDescriptor(other.descriptor)) { if (hassio_update_hasDecorators(element) || hassio_update_hasDecorators(other)) { throw new ReferenceError("Duplicated methods (" + element.key + ") can't be decorated."); } other.descriptor = element.descriptor; } else { if (hassio_update_hasDecorators(element)) { if (hassio_update_hasDecorators(other)) { throw new ReferenceError("Decorators can't be placed on different accessors with for " + "the same property (" + element.key + ")."); } other.decorators = element.decorators; } hassio_update_coalesceGetterSetter(element, other); } } else { newElements.push(element); } } return newElements; }

function hassio_update_hasDecorators(element) { return element.decorators && element.decorators.length; }

function hassio_update_isDataDescriptor(desc) { return desc !== undefined && !(desc.value === undefined && desc.writable === undefined); }

function hassio_update_optionalCallableProperty(obj, name) { var value = obj[name]; if (value !== undefined && typeof value !== "function") { throw new TypeError("Expected '" + name + "' to be a function"); } return value; }

function hassio_update_toPropertyKey(arg) { var key = hassio_update_toPrimitive(arg, "string"); return hassio_update_typeof(key) === "symbol" ? key : String(key); }

function hassio_update_toPrimitive(input, hint) { if (hassio_update_typeof(input) !== "object" || input === null) return input; var prim = input[Symbol.toPrimitive]; if (prim !== undefined) { var res = prim.call(input, hint || "default"); if (hassio_update_typeof(res) !== "object") return res; throw new TypeError("@@toPrimitive must return a primitive value."); } return (hint === "string" ? String : Number)(input); }

function hassio_update_toArray(arr) { return hassio_update_arrayWithHoles(arr) || hassio_update_iterableToArray(arr) || hassio_update_unsupportedIterableToArray(arr) || hassio_update_nonIterableRest(); }

function hassio_update_nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function hassio_update_unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return hassio_update_arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(n); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return hassio_update_arrayLikeToArray(o, minLen); }

function hassio_update_arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function hassio_update_iterableToArray(iter) { if (typeof Symbol !== "undefined" && Symbol.iterator in Object(iter)) return Array.from(iter); }

function hassio_update_arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }









var hassio_update_HassioUpdate = hassio_update_decorate([Object(lit_element["d" /* customElement */])("hassio-update")], function (_initialize, _LitElement) {
  var HassioUpdate = /*#__PURE__*/function (_LitElement2) {
    hassio_update_inherits(HassioUpdate, _LitElement2);

    var _super = hassio_update_createSuper(HassioUpdate);

    function HassioUpdate() {
      var _this;

      hassio_update_classCallCheck(this, HassioUpdate);

      for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
        args[_key] = arguments[_key];
      }

      _this = _super.call.apply(_super, [this].concat(args));

      _initialize(hassio_update_assertThisInitialized(_this));

      return _this;
    }

    return HassioUpdate;
  }(_LitElement);

  return {
    F: HassioUpdate,
    d: [{
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "hass",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "hassInfo",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "hassOsInfo",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "supervisorInfo",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "_error",
      value: void 0
    }, {
      kind: "method",
      key: "render",
      value: function render() {
        var updatesAvailable = [this.hassInfo, this.supervisorInfo, this.hassOsInfo].filter(function (value) {
          return !!value && (value.version_latest ? value.version !== value.version_latest : value.version_latest ? value.version !== value.version_latest : false);
        }).length;

        if (!updatesAvailable) {
          return Object(lit_element["e" /* html */])(hassio_update_templateObject());
        }

        return Object(lit_element["e" /* html */])(hassio_update_templateObject2(), this._error ? Object(lit_element["e" /* html */])(hassio_update_templateObject3(), this._error) : "", updatesAvailable > 1 ? "Updates Available 🎉" : "Update Available 🎉", this._renderUpdateCard("Home Assistant Core", this.hassInfo.version, this.hassInfo.version_latest, "hassio/homeassistant/update", "https://".concat(this.hassInfo.version_latest.includes("b") ? "rc" : "www", ".home-assistant.io/latest-release-notes/"), "hassio:home-assistant"), this._renderUpdateCard("Supervisor", this.supervisorInfo.version, this.supervisorInfo.version_latest, "hassio/supervisor/update", "https://github.com//home-assistant/hassio/releases/tag/".concat(this.supervisorInfo.version_latest)), this.hassOsInfo ? this._renderUpdateCard("Operating System", this.hassOsInfo.version, this.hassOsInfo.version_latest, "hassio/os/update", "https://github.com//home-assistant/hassos/releases/tag/".concat(this.hassOsInfo.version_latest)) : "");
      }
    }, {
      kind: "method",
      key: "_renderUpdateCard",
      value: function _renderUpdateCard(name, curVersion, lastVersion, apiPath, releaseNotesUrl, icon) {
        if (!lastVersion || lastVersion === curVersion) {
          return Object(lit_element["e" /* html */])(hassio_update_templateObject4());
        }

        return Object(lit_element["e" /* html */])(hassio_update_templateObject5(), icon ? Object(lit_element["e" /* html */])(hassio_update_templateObject6(), icon) : "", name, lastVersion, curVersion, releaseNotesUrl, this.hass, apiPath, this._apiCalled);
      }
    }, {
      kind: "method",
      key: "_apiCalled",
      value: function _apiCalled(ev) {
        if (ev.detail.success) {
          this._error = "";
          return;
        }

        var response = ev.detail.response;

        if (hassio_update_typeof(response.body) === "object") {
          this._error = response.body.message || "Unknown error";
        } else {
          this._error = response.body;
        }
      }
    }, {
      kind: "get",
      "static": true,
      key: "styles",
      value: function styles() {
        return [resources_styles["b" /* haStyle */], hassio_style["a" /* hassioStyle */], Object(lit_element["c" /* css */])(_templateObject7())];
      }
    }]
  };
}, lit_element["a" /* LitElement */]);
// CONCATENATED MODULE: ./hassio/src/dashboard/hassio-dashboard.ts
function hassio_dashboard_typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { hassio_dashboard_typeof = function _typeof(obj) { return typeof obj; }; } else { hassio_dashboard_typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return hassio_dashboard_typeof(obj); }

function hassio_dashboard_templateObject2() {
  var data = hassio_dashboard_taggedTemplateLiteral(["\n        .content {\n          margin: 0 auto;\n        }\n      "]);

  hassio_dashboard_templateObject2 = function _templateObject2() {
    return data;
  };

  return data;
}

function hassio_dashboard_templateObject() {
  var data = hassio_dashboard_taggedTemplateLiteral(["\n      <hass-tabs-subpage\n        .hass=", "\n        .narrow=", "\n        hassio\n        main-page\n        .route=", "\n        .tabs=", "\n      >\n        <span slot=\"header\">Dashboard</span>\n        <div class=\"content\">\n          <hassio-update\n            .hass=", "\n            .hassInfo=", "\n            .supervisorInfo=", "\n            .hassOsInfo=", "\n          ></hassio-update>\n          <hassio-addons\n            .hass=", "\n            .addons=", "\n          ></hassio-addons>\n        </div>\n      </hass-tabs-subpage>\n    "]);

  hassio_dashboard_templateObject = function _templateObject() {
    return data;
  };

  return data;
}

function hassio_dashboard_taggedTemplateLiteral(strings, raw) { if (!raw) { raw = strings.slice(0); } return Object.freeze(Object.defineProperties(strings, { raw: { value: Object.freeze(raw) } })); }

function hassio_dashboard_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function hassio_dashboard_inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) hassio_dashboard_setPrototypeOf(subClass, superClass); }

function hassio_dashboard_setPrototypeOf(o, p) { hassio_dashboard_setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return hassio_dashboard_setPrototypeOf(o, p); }

function hassio_dashboard_createSuper(Derived) { return function () { var Super = hassio_dashboard_getPrototypeOf(Derived), result; if (hassio_dashboard_isNativeReflectConstruct()) { var NewTarget = hassio_dashboard_getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return hassio_dashboard_possibleConstructorReturn(this, result); }; }

function hassio_dashboard_possibleConstructorReturn(self, call) { if (call && (hassio_dashboard_typeof(call) === "object" || typeof call === "function")) { return call; } return hassio_dashboard_assertThisInitialized(self); }

function hassio_dashboard_assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function hassio_dashboard_isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Date.prototype.toString.call(Reflect.construct(Date, [], function () {})); return true; } catch (e) { return false; } }

function hassio_dashboard_getPrototypeOf(o) { hassio_dashboard_getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return hassio_dashboard_getPrototypeOf(o); }

function hassio_dashboard_decorate(decorators, factory, superClass, mixins) { var api = hassio_dashboard_getDecoratorsApi(); if (mixins) { for (var i = 0; i < mixins.length; i++) { api = mixins[i](api); } } var r = factory(function initialize(O) { api.initializeInstanceElements(O, decorated.elements); }, superClass); var decorated = api.decorateClass(hassio_dashboard_coalesceClassElements(r.d.map(hassio_dashboard_createElementDescriptor)), decorators); api.initializeClassElements(r.F, decorated.elements); return api.runClassFinishers(r.F, decorated.finishers); }

function hassio_dashboard_getDecoratorsApi() { hassio_dashboard_getDecoratorsApi = function _getDecoratorsApi() { return api; }; var api = { elementsDefinitionOrder: [["method"], ["field"]], initializeInstanceElements: function initializeInstanceElements(O, elements) { ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { if (element.kind === kind && element.placement === "own") { this.defineClassElement(O, element); } }, this); }, this); }, initializeClassElements: function initializeClassElements(F, elements) { var proto = F.prototype; ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { var placement = element.placement; if (element.kind === kind && (placement === "static" || placement === "prototype")) { var receiver = placement === "static" ? F : proto; this.defineClassElement(receiver, element); } }, this); }, this); }, defineClassElement: function defineClassElement(receiver, element) { var descriptor = element.descriptor; if (element.kind === "field") { var initializer = element.initializer; descriptor = { enumerable: descriptor.enumerable, writable: descriptor.writable, configurable: descriptor.configurable, value: initializer === void 0 ? void 0 : initializer.call(receiver) }; } Object.defineProperty(receiver, element.key, descriptor); }, decorateClass: function decorateClass(elements, decorators) { var newElements = []; var finishers = []; var placements = { "static": [], prototype: [], own: [] }; elements.forEach(function (element) { this.addElementPlacement(element, placements); }, this); elements.forEach(function (element) { if (!hassio_dashboard_hasDecorators(element)) return newElements.push(element); var elementFinishersExtras = this.decorateElement(element, placements); newElements.push(elementFinishersExtras.element); newElements.push.apply(newElements, elementFinishersExtras.extras); finishers.push.apply(finishers, elementFinishersExtras.finishers); }, this); if (!decorators) { return { elements: newElements, finishers: finishers }; } var result = this.decorateConstructor(newElements, decorators); finishers.push.apply(finishers, result.finishers); result.finishers = finishers; return result; }, addElementPlacement: function addElementPlacement(element, placements, silent) { var keys = placements[element.placement]; if (!silent && keys.indexOf(element.key) !== -1) { throw new TypeError("Duplicated element (" + element.key + ")"); } keys.push(element.key); }, decorateElement: function decorateElement(element, placements) { var extras = []; var finishers = []; for (var decorators = element.decorators, i = decorators.length - 1; i >= 0; i--) { var keys = placements[element.placement]; keys.splice(keys.indexOf(element.key), 1); var elementObject = this.fromElementDescriptor(element); var elementFinisherExtras = this.toElementFinisherExtras((0, decorators[i])(elementObject) || elementObject); element = elementFinisherExtras.element; this.addElementPlacement(element, placements); if (elementFinisherExtras.finisher) { finishers.push(elementFinisherExtras.finisher); } var newExtras = elementFinisherExtras.extras; if (newExtras) { for (var j = 0; j < newExtras.length; j++) { this.addElementPlacement(newExtras[j], placements); } extras.push.apply(extras, newExtras); } } return { element: element, finishers: finishers, extras: extras }; }, decorateConstructor: function decorateConstructor(elements, decorators) { var finishers = []; for (var i = decorators.length - 1; i >= 0; i--) { var obj = this.fromClassDescriptor(elements); var elementsAndFinisher = this.toClassDescriptor((0, decorators[i])(obj) || obj); if (elementsAndFinisher.finisher !== undefined) { finishers.push(elementsAndFinisher.finisher); } if (elementsAndFinisher.elements !== undefined) { elements = elementsAndFinisher.elements; for (var j = 0; j < elements.length - 1; j++) { for (var k = j + 1; k < elements.length; k++) { if (elements[j].key === elements[k].key && elements[j].placement === elements[k].placement) { throw new TypeError("Duplicated element (" + elements[j].key + ")"); } } } } } return { elements: elements, finishers: finishers }; }, fromElementDescriptor: function fromElementDescriptor(element) { var obj = { kind: element.kind, key: element.key, placement: element.placement, descriptor: element.descriptor }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); if (element.kind === "field") obj.initializer = element.initializer; return obj; }, toElementDescriptors: function toElementDescriptors(elementObjects) { if (elementObjects === undefined) return; return hassio_dashboard_toArray(elementObjects).map(function (elementObject) { var element = this.toElementDescriptor(elementObject); this.disallowProperty(elementObject, "finisher", "An element descriptor"); this.disallowProperty(elementObject, "extras", "An element descriptor"); return element; }, this); }, toElementDescriptor: function toElementDescriptor(elementObject) { var kind = String(elementObject.kind); if (kind !== "method" && kind !== "field") { throw new TypeError('An element descriptor\'s .kind property must be either "method" or' + ' "field", but a decorator created an element descriptor with' + ' .kind "' + kind + '"'); } var key = hassio_dashboard_toPropertyKey(elementObject.key); var placement = String(elementObject.placement); if (placement !== "static" && placement !== "prototype" && placement !== "own") { throw new TypeError('An element descriptor\'s .placement property must be one of "static",' + ' "prototype" or "own", but a decorator created an element descriptor' + ' with .placement "' + placement + '"'); } var descriptor = elementObject.descriptor; this.disallowProperty(elementObject, "elements", "An element descriptor"); var element = { kind: kind, key: key, placement: placement, descriptor: Object.assign({}, descriptor) }; if (kind !== "field") { this.disallowProperty(elementObject, "initializer", "A method descriptor"); } else { this.disallowProperty(descriptor, "get", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "set", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "value", "The property descriptor of a field descriptor"); element.initializer = elementObject.initializer; } return element; }, toElementFinisherExtras: function toElementFinisherExtras(elementObject) { var element = this.toElementDescriptor(elementObject); var finisher = hassio_dashboard_optionalCallableProperty(elementObject, "finisher"); var extras = this.toElementDescriptors(elementObject.extras); return { element: element, finisher: finisher, extras: extras }; }, fromClassDescriptor: function fromClassDescriptor(elements) { var obj = { kind: "class", elements: elements.map(this.fromElementDescriptor, this) }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); return obj; }, toClassDescriptor: function toClassDescriptor(obj) { var kind = String(obj.kind); if (kind !== "class") { throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator' + ' created a class descriptor with .kind "' + kind + '"'); } this.disallowProperty(obj, "key", "A class descriptor"); this.disallowProperty(obj, "placement", "A class descriptor"); this.disallowProperty(obj, "descriptor", "A class descriptor"); this.disallowProperty(obj, "initializer", "A class descriptor"); this.disallowProperty(obj, "extras", "A class descriptor"); var finisher = hassio_dashboard_optionalCallableProperty(obj, "finisher"); var elements = this.toElementDescriptors(obj.elements); return { elements: elements, finisher: finisher }; }, runClassFinishers: function runClassFinishers(constructor, finishers) { for (var i = 0; i < finishers.length; i++) { var newConstructor = (0, finishers[i])(constructor); if (newConstructor !== undefined) { if (typeof newConstructor !== "function") { throw new TypeError("Finishers must return a constructor."); } constructor = newConstructor; } } return constructor; }, disallowProperty: function disallowProperty(obj, name, objectType) { if (obj[name] !== undefined) { throw new TypeError(objectType + " can't have a ." + name + " property."); } } }; return api; }

function hassio_dashboard_createElementDescriptor(def) { var key = hassio_dashboard_toPropertyKey(def.key); var descriptor; if (def.kind === "method") { descriptor = { value: def.value, writable: true, configurable: true, enumerable: false }; } else if (def.kind === "get") { descriptor = { get: def.value, configurable: true, enumerable: false }; } else if (def.kind === "set") { descriptor = { set: def.value, configurable: true, enumerable: false }; } else if (def.kind === "field") { descriptor = { configurable: true, writable: true, enumerable: true }; } var element = { kind: def.kind === "field" ? "field" : "method", key: key, placement: def["static"] ? "static" : def.kind === "field" ? "own" : "prototype", descriptor: descriptor }; if (def.decorators) element.decorators = def.decorators; if (def.kind === "field") element.initializer = def.value; return element; }

function hassio_dashboard_coalesceGetterSetter(element, other) { if (element.descriptor.get !== undefined) { other.descriptor.get = element.descriptor.get; } else { other.descriptor.set = element.descriptor.set; } }

function hassio_dashboard_coalesceClassElements(elements) { var newElements = []; var isSameElement = function isSameElement(other) { return other.kind === "method" && other.key === element.key && other.placement === element.placement; }; for (var i = 0; i < elements.length; i++) { var element = elements[i]; var other; if (element.kind === "method" && (other = newElements.find(isSameElement))) { if (hassio_dashboard_isDataDescriptor(element.descriptor) || hassio_dashboard_isDataDescriptor(other.descriptor)) { if (hassio_dashboard_hasDecorators(element) || hassio_dashboard_hasDecorators(other)) { throw new ReferenceError("Duplicated methods (" + element.key + ") can't be decorated."); } other.descriptor = element.descriptor; } else { if (hassio_dashboard_hasDecorators(element)) { if (hassio_dashboard_hasDecorators(other)) { throw new ReferenceError("Decorators can't be placed on different accessors with for " + "the same property (" + element.key + ")."); } other.decorators = element.decorators; } hassio_dashboard_coalesceGetterSetter(element, other); } } else { newElements.push(element); } } return newElements; }

function hassio_dashboard_hasDecorators(element) { return element.decorators && element.decorators.length; }

function hassio_dashboard_isDataDescriptor(desc) { return desc !== undefined && !(desc.value === undefined && desc.writable === undefined); }

function hassio_dashboard_optionalCallableProperty(obj, name) { var value = obj[name]; if (value !== undefined && typeof value !== "function") { throw new TypeError("Expected '" + name + "' to be a function"); } return value; }

function hassio_dashboard_toPropertyKey(arg) { var key = hassio_dashboard_toPrimitive(arg, "string"); return hassio_dashboard_typeof(key) === "symbol" ? key : String(key); }

function hassio_dashboard_toPrimitive(input, hint) { if (hassio_dashboard_typeof(input) !== "object" || input === null) return input; var prim = input[Symbol.toPrimitive]; if (prim !== undefined) { var res = prim.call(input, hint || "default"); if (hassio_dashboard_typeof(res) !== "object") return res; throw new TypeError("@@toPrimitive must return a primitive value."); } return (hint === "string" ? String : Number)(input); }

function hassio_dashboard_toArray(arr) { return hassio_dashboard_arrayWithHoles(arr) || hassio_dashboard_iterableToArray(arr) || hassio_dashboard_unsupportedIterableToArray(arr) || hassio_dashboard_nonIterableRest(); }

function hassio_dashboard_nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function hassio_dashboard_unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return hassio_dashboard_arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(n); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return hassio_dashboard_arrayLikeToArray(o, minLen); }

function hassio_dashboard_arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function hassio_dashboard_iterableToArray(iter) { if (typeof Symbol !== "undefined" && Symbol.iterator in Object(iter)) return Array.from(iter); }

function hassio_dashboard_arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }








var hassio_dashboard_HassioDashboard = hassio_dashboard_decorate([Object(lit_element["d" /* customElement */])("hassio-dashboard")], function (_initialize, _LitElement) {
  var HassioDashboard = /*#__PURE__*/function (_LitElement2) {
    hassio_dashboard_inherits(HassioDashboard, _LitElement2);

    var _super = hassio_dashboard_createSuper(HassioDashboard);

    function HassioDashboard() {
      var _this;

      hassio_dashboard_classCallCheck(this, HassioDashboard);

      for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
        args[_key] = arguments[_key];
      }

      _this = _super.call.apply(_super, [this].concat(args));

      _initialize(hassio_dashboard_assertThisInitialized(_this));

      return _this;
    }

    return HassioDashboard;
  }(_LitElement);

  return {
    F: HassioDashboard,
    d: [{
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])({
        attribute: false
      })],
      key: "hass",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])({
        type: Boolean
      })],
      key: "narrow",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])({
        attribute: false
      })],
      key: "route",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])({
        attribute: false
      })],
      key: "supervisorInfo",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])({
        attribute: false
      })],
      key: "hassInfo",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])({
        attribute: false
      })],
      key: "hassOsInfo",
      value: void 0
    }, {
      kind: "method",
      key: "render",
      value: function render() {
        return Object(lit_element["e" /* html */])(hassio_dashboard_templateObject(), this.hass, this.narrow, this.route, supervisorTabs, this.hass, this.hassInfo, this.supervisorInfo, this.hassOsInfo, this.hass, this.supervisorInfo.addons);
      }
    }, {
      kind: "get",
      "static": true,
      key: "styles",
      value: function styles() {
        return [resources_styles["b" /* haStyle */], Object(lit_element["c" /* css */])(hassio_dashboard_templateObject2())];
      }
    }]
  };
}, lit_element["a" /* LitElement */]);
// EXTERNAL MODULE: ./node_modules/@polymer/paper-checkbox/paper-checkbox.js
var paper_checkbox = __webpack_require__(149);

// EXTERNAL MODULE: ./node_modules/@polymer/paper-radio-button/paper-radio-button.js
var paper_radio_button = __webpack_require__(125);

// EXTERNAL MODULE: ./node_modules/@polymer/paper-radio-group/paper-radio-group.js + 1 modules
var paper_radio_group = __webpack_require__(187);

// EXTERNAL MODULE: ./src/data/hassio/snapshot.ts
var hassio_snapshot = __webpack_require__(126);

// CONCATENATED MODULE: ./hassio/src/dialogs/snapshot/show-dialog-hassio-snapshot.ts

var show_dialog_hassio_snapshot_showHassioSnapshotDialog = function showHassioSnapshotDialog(element, dialogParams) {
  Object(fire_event["a" /* fireEvent */])(element, "show-dialog", {
    dialogTag: "dialog-hassio-snapshot",
    dialogImport: function dialogImport() {
      return __webpack_require__.e(/* import() | dialog-hassio-snapshot */ 4).then(__webpack_require__.bind(null, 193));
    },
    dialogParams: dialogParams
  });
};
// CONCATENATED MODULE: ./hassio/src/snapshots/hassio-snapshots.ts
function hassio_snapshots_typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { hassio_snapshots_typeof = function _typeof(obj) { return typeof obj; }; } else { hassio_snapshots_typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return hassio_snapshots_typeof(obj); }

function _templateObject9() {
  var data = hassio_snapshots_taggedTemplateLiteral(["\n        paper-radio-group {\n          display: block;\n        }\n        paper-radio-button {\n          padding: 0 0 2px 2px;\n        }\n        paper-radio-button,\n        paper-checkbox,\n        paper-input[type=\"password\"] {\n          display: block;\n          margin: 4px 0 4px 48px;\n        }\n        .pointer {\n          cursor: pointer;\n        }\n      "]);

  _templateObject9 = function _templateObject9() {
    return data;
  };

  return data;
}

function _templateObject8() {
  var data = hassio_snapshots_taggedTemplateLiteral(["\n                    <paper-card\n                      class=\"pointer\"\n                      .snapshot=", "\n                      @click=", "\n                    >\n                      <div class=\"card-content\">\n                        <hassio-card-content\n                          .hass=", "\n                          .title=", "\n                          .description=", "\n                          .datetime=", "\n                          .icon=", "\n                          .icon-class=\"snapshot\"\n                        ></hassio-card-content>\n                      </div>\n                    </paper-card>\n                  "]);

  _templateObject8 = function _templateObject8() {
    return data;
  };

  return data;
}

function hassio_snapshots_templateObject7() {
  var data = hassio_snapshots_taggedTemplateLiteral(["\n                  <paper-card>\n                    <div class=\"card-content\">\n                      You don't have any snapshots yet.\n                    </div>\n                  </paper-card>\n                "]);

  hassio_snapshots_templateObject7 = function _templateObject7() {
    return data;
  };

  return data;
}

function hassio_snapshots_templateObject6() {
  var data = hassio_snapshots_taggedTemplateLiteral([" <p class=\"error\">", "</p> "]);

  hassio_snapshots_templateObject6 = function _templateObject6() {
    return data;
  };

  return data;
}

function hassio_snapshots_templateObject5() {
  var data = hassio_snapshots_taggedTemplateLiteral(["\n                      <paper-input\n                        label=\"Password\"\n                        type=\"password\"\n                        name=\"snapshotPassword\"\n                        .value=", "\n                        @value-changed=", "\n                      ></paper-input>\n                    "]);

  hassio_snapshots_templateObject5 = function _templateObject5() {
    return data;
  };

  return data;
}

function hassio_snapshots_templateObject4() {
  var data = hassio_snapshots_taggedTemplateLiteral(["\n                          <paper-checkbox\n                            .idx=", "\n                            .checked=", "\n                            @checked-changed=", "\n                          >\n                            ", "\n                          </paper-checkbox>\n                        "]);

  hassio_snapshots_templateObject4 = function _templateObject4() {
    return data;
  };

  return data;
}

function hassio_snapshots_templateObject3() {
  var data = hassio_snapshots_taggedTemplateLiteral(["\n                          <paper-checkbox\n                            .idx=", "\n                            .checked=", "\n                            @checked-changed=", "\n                          >\n                            ", "\n                          </paper-checkbox>\n                        "]);

  hassio_snapshots_templateObject3 = function _templateObject3() {
    return data;
  };

  return data;
}

function hassio_snapshots_templateObject2() {
  var data = hassio_snapshots_taggedTemplateLiteral(["\n                      Folders:\n                      ", "\n                      Add-ons:\n                      ", "\n                    "]);

  hassio_snapshots_templateObject2 = function _templateObject2() {
    return data;
  };

  return data;
}

function hassio_snapshots_templateObject() {
  var data = hassio_snapshots_taggedTemplateLiteral(["\n      <hass-tabs-subpage\n        .hass=", "\n        .narrow=", "\n        hassio\n        main-page\n        .route=", "\n        .tabs=", "\n      >\n        <span slot=\"header\">Snapshots</span>\n\n        <ha-icon-button\n          icon=\"hassio:reload\"\n          slot=\"toolbar-icon\"\n          aria-label=\"Reload snapshots\"\n          @click=", "\n        ></ha-icon-button>\n\n        <div class=\"content\">\n          <h1>\n            Create snapshot\n          </h1>\n          <p class=\"description\">\n            Snapshots allow you to easily backup and restore all data of your\n            Home Assistant instance.\n          </p>\n          <div class=\"card-group\">\n            <paper-card>\n              <div class=\"card-content\">\n                <paper-input\n                  autofocus\n                  label=\"Name\"\n                  name=\"snapshotName\"\n                  .value=", "\n                  @value-changed=", "\n                ></paper-input>\n                Type:\n                <paper-radio-group\n                  name=\"snapshotType\"\n                  .selected=", "\n                  @selected-changed=", "\n                >\n                  <paper-radio-button name=\"full\">\n                    Full snapshot\n                  </paper-radio-button>\n                  <paper-radio-button name=\"partial\">\n                    Partial snapshot\n                  </paper-radio-button>\n                </paper-radio-group>\n                ", "\n                Security:\n                <paper-checkbox\n                  name=\"snapshotHasPassword\"\n                  .checked=", "\n                  @checked-changed=", "\n                >\n                  Password protection\n                </paper-checkbox>\n                ", "\n                ", "\n              </div>\n              <div class=\"card-actions\">\n                <mwc-button\n                  .disabled=", "\n                  @click=", "\n                >\n                  Create\n                </mwc-button>\n              </div>\n            </paper-card>\n          </div>\n\n          <h1>Available snapshots</h1>\n          <div class=\"card-group\">\n            ", "\n          </div>\n        </div>\n      </hass-tabs-subpage>\n    "]);

  hassio_snapshots_templateObject = function _templateObject() {
    return data;
  };

  return data;
}

function hassio_snapshots_taggedTemplateLiteral(strings, raw) { if (!raw) { raw = strings.slice(0); } return Object.freeze(Object.defineProperties(strings, { raw: { value: Object.freeze(raw) } })); }

function hassio_snapshots_asyncGeneratorStep(gen, resolve, reject, _next, _throw, key, arg) { try { var info = gen[key](arg); var value = info.value; } catch (error) { reject(error); return; } if (info.done) { resolve(value); } else { Promise.resolve(value).then(_next, _throw); } }

function hassio_snapshots_asyncToGenerator(fn) { return function () { var self = this, args = arguments; return new Promise(function (resolve, reject) { var gen = fn.apply(self, args); function _next(value) { hassio_snapshots_asyncGeneratorStep(gen, resolve, reject, _next, _throw, "next", value); } function _throw(err) { hassio_snapshots_asyncGeneratorStep(gen, resolve, reject, _next, _throw, "throw", err); } _next(undefined); }); }; }

function hassio_snapshots_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function hassio_snapshots_inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) hassio_snapshots_setPrototypeOf(subClass, superClass); }

function hassio_snapshots_setPrototypeOf(o, p) { hassio_snapshots_setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return hassio_snapshots_setPrototypeOf(o, p); }

function hassio_snapshots_createSuper(Derived) { return function () { var Super = hassio_snapshots_getPrototypeOf(Derived), result; if (hassio_snapshots_isNativeReflectConstruct()) { var NewTarget = hassio_snapshots_getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return hassio_snapshots_possibleConstructorReturn(this, result); }; }

function hassio_snapshots_possibleConstructorReturn(self, call) { if (call && (hassio_snapshots_typeof(call) === "object" || typeof call === "function")) { return call; } return hassio_snapshots_assertThisInitialized(self); }

function hassio_snapshots_assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function hassio_snapshots_isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Date.prototype.toString.call(Reflect.construct(Date, [], function () {})); return true; } catch (e) { return false; } }

function hassio_snapshots_decorate(decorators, factory, superClass, mixins) { var api = hassio_snapshots_getDecoratorsApi(); if (mixins) { for (var i = 0; i < mixins.length; i++) { api = mixins[i](api); } } var r = factory(function initialize(O) { api.initializeInstanceElements(O, decorated.elements); }, superClass); var decorated = api.decorateClass(hassio_snapshots_coalesceClassElements(r.d.map(hassio_snapshots_createElementDescriptor)), decorators); api.initializeClassElements(r.F, decorated.elements); return api.runClassFinishers(r.F, decorated.finishers); }

function hassio_snapshots_getDecoratorsApi() { hassio_snapshots_getDecoratorsApi = function _getDecoratorsApi() { return api; }; var api = { elementsDefinitionOrder: [["method"], ["field"]], initializeInstanceElements: function initializeInstanceElements(O, elements) { ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { if (element.kind === kind && element.placement === "own") { this.defineClassElement(O, element); } }, this); }, this); }, initializeClassElements: function initializeClassElements(F, elements) { var proto = F.prototype; ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { var placement = element.placement; if (element.kind === kind && (placement === "static" || placement === "prototype")) { var receiver = placement === "static" ? F : proto; this.defineClassElement(receiver, element); } }, this); }, this); }, defineClassElement: function defineClassElement(receiver, element) { var descriptor = element.descriptor; if (element.kind === "field") { var initializer = element.initializer; descriptor = { enumerable: descriptor.enumerable, writable: descriptor.writable, configurable: descriptor.configurable, value: initializer === void 0 ? void 0 : initializer.call(receiver) }; } Object.defineProperty(receiver, element.key, descriptor); }, decorateClass: function decorateClass(elements, decorators) { var newElements = []; var finishers = []; var placements = { "static": [], prototype: [], own: [] }; elements.forEach(function (element) { this.addElementPlacement(element, placements); }, this); elements.forEach(function (element) { if (!hassio_snapshots_hasDecorators(element)) return newElements.push(element); var elementFinishersExtras = this.decorateElement(element, placements); newElements.push(elementFinishersExtras.element); newElements.push.apply(newElements, elementFinishersExtras.extras); finishers.push.apply(finishers, elementFinishersExtras.finishers); }, this); if (!decorators) { return { elements: newElements, finishers: finishers }; } var result = this.decorateConstructor(newElements, decorators); finishers.push.apply(finishers, result.finishers); result.finishers = finishers; return result; }, addElementPlacement: function addElementPlacement(element, placements, silent) { var keys = placements[element.placement]; if (!silent && keys.indexOf(element.key) !== -1) { throw new TypeError("Duplicated element (" + element.key + ")"); } keys.push(element.key); }, decorateElement: function decorateElement(element, placements) { var extras = []; var finishers = []; for (var decorators = element.decorators, i = decorators.length - 1; i >= 0; i--) { var keys = placements[element.placement]; keys.splice(keys.indexOf(element.key), 1); var elementObject = this.fromElementDescriptor(element); var elementFinisherExtras = this.toElementFinisherExtras((0, decorators[i])(elementObject) || elementObject); element = elementFinisherExtras.element; this.addElementPlacement(element, placements); if (elementFinisherExtras.finisher) { finishers.push(elementFinisherExtras.finisher); } var newExtras = elementFinisherExtras.extras; if (newExtras) { for (var j = 0; j < newExtras.length; j++) { this.addElementPlacement(newExtras[j], placements); } extras.push.apply(extras, newExtras); } } return { element: element, finishers: finishers, extras: extras }; }, decorateConstructor: function decorateConstructor(elements, decorators) { var finishers = []; for (var i = decorators.length - 1; i >= 0; i--) { var obj = this.fromClassDescriptor(elements); var elementsAndFinisher = this.toClassDescriptor((0, decorators[i])(obj) || obj); if (elementsAndFinisher.finisher !== undefined) { finishers.push(elementsAndFinisher.finisher); } if (elementsAndFinisher.elements !== undefined) { elements = elementsAndFinisher.elements; for (var j = 0; j < elements.length - 1; j++) { for (var k = j + 1; k < elements.length; k++) { if (elements[j].key === elements[k].key && elements[j].placement === elements[k].placement) { throw new TypeError("Duplicated element (" + elements[j].key + ")"); } } } } } return { elements: elements, finishers: finishers }; }, fromElementDescriptor: function fromElementDescriptor(element) { var obj = { kind: element.kind, key: element.key, placement: element.placement, descriptor: element.descriptor }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); if (element.kind === "field") obj.initializer = element.initializer; return obj; }, toElementDescriptors: function toElementDescriptors(elementObjects) { if (elementObjects === undefined) return; return hassio_snapshots_toArray(elementObjects).map(function (elementObject) { var element = this.toElementDescriptor(elementObject); this.disallowProperty(elementObject, "finisher", "An element descriptor"); this.disallowProperty(elementObject, "extras", "An element descriptor"); return element; }, this); }, toElementDescriptor: function toElementDescriptor(elementObject) { var kind = String(elementObject.kind); if (kind !== "method" && kind !== "field") { throw new TypeError('An element descriptor\'s .kind property must be either "method" or' + ' "field", but a decorator created an element descriptor with' + ' .kind "' + kind + '"'); } var key = hassio_snapshots_toPropertyKey(elementObject.key); var placement = String(elementObject.placement); if (placement !== "static" && placement !== "prototype" && placement !== "own") { throw new TypeError('An element descriptor\'s .placement property must be one of "static",' + ' "prototype" or "own", but a decorator created an element descriptor' + ' with .placement "' + placement + '"'); } var descriptor = elementObject.descriptor; this.disallowProperty(elementObject, "elements", "An element descriptor"); var element = { kind: kind, key: key, placement: placement, descriptor: Object.assign({}, descriptor) }; if (kind !== "field") { this.disallowProperty(elementObject, "initializer", "A method descriptor"); } else { this.disallowProperty(descriptor, "get", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "set", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "value", "The property descriptor of a field descriptor"); element.initializer = elementObject.initializer; } return element; }, toElementFinisherExtras: function toElementFinisherExtras(elementObject) { var element = this.toElementDescriptor(elementObject); var finisher = hassio_snapshots_optionalCallableProperty(elementObject, "finisher"); var extras = this.toElementDescriptors(elementObject.extras); return { element: element, finisher: finisher, extras: extras }; }, fromClassDescriptor: function fromClassDescriptor(elements) { var obj = { kind: "class", elements: elements.map(this.fromElementDescriptor, this) }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); return obj; }, toClassDescriptor: function toClassDescriptor(obj) { var kind = String(obj.kind); if (kind !== "class") { throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator' + ' created a class descriptor with .kind "' + kind + '"'); } this.disallowProperty(obj, "key", "A class descriptor"); this.disallowProperty(obj, "placement", "A class descriptor"); this.disallowProperty(obj, "descriptor", "A class descriptor"); this.disallowProperty(obj, "initializer", "A class descriptor"); this.disallowProperty(obj, "extras", "A class descriptor"); var finisher = hassio_snapshots_optionalCallableProperty(obj, "finisher"); var elements = this.toElementDescriptors(obj.elements); return { elements: elements, finisher: finisher }; }, runClassFinishers: function runClassFinishers(constructor, finishers) { for (var i = 0; i < finishers.length; i++) { var newConstructor = (0, finishers[i])(constructor); if (newConstructor !== undefined) { if (typeof newConstructor !== "function") { throw new TypeError("Finishers must return a constructor."); } constructor = newConstructor; } } return constructor; }, disallowProperty: function disallowProperty(obj, name, objectType) { if (obj[name] !== undefined) { throw new TypeError(objectType + " can't have a ." + name + " property."); } } }; return api; }

function hassio_snapshots_createElementDescriptor(def) { var key = hassio_snapshots_toPropertyKey(def.key); var descriptor; if (def.kind === "method") { descriptor = { value: def.value, writable: true, configurable: true, enumerable: false }; } else if (def.kind === "get") { descriptor = { get: def.value, configurable: true, enumerable: false }; } else if (def.kind === "set") { descriptor = { set: def.value, configurable: true, enumerable: false }; } else if (def.kind === "field") { descriptor = { configurable: true, writable: true, enumerable: true }; } var element = { kind: def.kind === "field" ? "field" : "method", key: key, placement: def["static"] ? "static" : def.kind === "field" ? "own" : "prototype", descriptor: descriptor }; if (def.decorators) element.decorators = def.decorators; if (def.kind === "field") element.initializer = def.value; return element; }

function hassio_snapshots_coalesceGetterSetter(element, other) { if (element.descriptor.get !== undefined) { other.descriptor.get = element.descriptor.get; } else { other.descriptor.set = element.descriptor.set; } }

function hassio_snapshots_coalesceClassElements(elements) { var newElements = []; var isSameElement = function isSameElement(other) { return other.kind === "method" && other.key === element.key && other.placement === element.placement; }; for (var i = 0; i < elements.length; i++) { var element = elements[i]; var other; if (element.kind === "method" && (other = newElements.find(isSameElement))) { if (hassio_snapshots_isDataDescriptor(element.descriptor) || hassio_snapshots_isDataDescriptor(other.descriptor)) { if (hassio_snapshots_hasDecorators(element) || hassio_snapshots_hasDecorators(other)) { throw new ReferenceError("Duplicated methods (" + element.key + ") can't be decorated."); } other.descriptor = element.descriptor; } else { if (hassio_snapshots_hasDecorators(element)) { if (hassio_snapshots_hasDecorators(other)) { throw new ReferenceError("Decorators can't be placed on different accessors with for " + "the same property (" + element.key + ")."); } other.decorators = element.decorators; } hassio_snapshots_coalesceGetterSetter(element, other); } } else { newElements.push(element); } } return newElements; }

function hassio_snapshots_hasDecorators(element) { return element.decorators && element.decorators.length; }

function hassio_snapshots_isDataDescriptor(desc) { return desc !== undefined && !(desc.value === undefined && desc.writable === undefined); }

function hassio_snapshots_optionalCallableProperty(obj, name) { var value = obj[name]; if (value !== undefined && typeof value !== "function") { throw new TypeError("Expected '" + name + "' to be a function"); } return value; }

function hassio_snapshots_toPropertyKey(arg) { var key = hassio_snapshots_toPrimitive(arg, "string"); return hassio_snapshots_typeof(key) === "symbol" ? key : String(key); }

function hassio_snapshots_toPrimitive(input, hint) { if (hassio_snapshots_typeof(input) !== "object" || input === null) return input; var prim = input[Symbol.toPrimitive]; if (prim !== undefined) { var res = prim.call(input, hint || "default"); if (hassio_snapshots_typeof(res) !== "object") return res; throw new TypeError("@@toPrimitive must return a primitive value."); } return (hint === "string" ? String : Number)(input); }

function hassio_snapshots_toArray(arr) { return hassio_snapshots_arrayWithHoles(arr) || hassio_snapshots_iterableToArray(arr) || hassio_snapshots_unsupportedIterableToArray(arr) || hassio_snapshots_nonIterableRest(); }

function hassio_snapshots_nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function hassio_snapshots_unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return hassio_snapshots_arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(n); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return hassio_snapshots_arrayLikeToArray(o, minLen); }

function hassio_snapshots_arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function hassio_snapshots_iterableToArray(iter) { if (typeof Symbol !== "undefined" && Symbol.iterator in Object(iter)) return Array.from(iter); }

function hassio_snapshots_arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }

function hassio_snapshots_get(target, property, receiver) { if (typeof Reflect !== "undefined" && Reflect.get) { hassio_snapshots_get = Reflect.get; } else { hassio_snapshots_get = function _get(target, property, receiver) { var base = hassio_snapshots_superPropBase(target, property); if (!base) return; var desc = Object.getOwnPropertyDescriptor(base, property); if (desc.get) { return desc.get.call(receiver); } return desc.value; }; } return hassio_snapshots_get(target, property, receiver || target); }

function hassio_snapshots_superPropBase(object, property) { while (!Object.prototype.hasOwnProperty.call(object, property)) { object = hassio_snapshots_getPrototypeOf(object); if (object === null) break; } return object; }

function hassio_snapshots_getPrototypeOf(o) { hassio_snapshots_getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return hassio_snapshots_getPrototypeOf(o); }

















var hassio_snapshots_HassioSnapshots = hassio_snapshots_decorate([Object(lit_element["d" /* customElement */])("hassio-snapshots")], function (_initialize, _LitElement) {
  var HassioSnapshots = /*#__PURE__*/function (_LitElement2) {
    hassio_snapshots_inherits(HassioSnapshots, _LitElement2);

    var _super = hassio_snapshots_createSuper(HassioSnapshots);

    function HassioSnapshots() {
      var _this;

      hassio_snapshots_classCallCheck(this, HassioSnapshots);

      for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
        args[_key] = arguments[_key];
      }

      _this = _super.call.apply(_super, [this].concat(args));

      _initialize(hassio_snapshots_assertThisInitialized(_this));

      return _this;
    }

    return HassioSnapshots;
  }(_LitElement);

  return {
    F: HassioSnapshots,
    d: [{
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])({
        attribute: false
      })],
      key: "hass",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])({
        type: Boolean
      })],
      key: "narrow",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])({
        attribute: false
      })],
      key: "route",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])({
        attribute: false
      })],
      key: "supervisorInfo",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "_snapshotName",
      value: function value() {
        return "";
      }
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "_snapshotPassword",
      value: function value() {
        return "";
      }
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "_snapshotHasPassword",
      value: function value() {
        return false;
      }
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "_snapshotType",
      value: function value() {
        return "full";
      }
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "_snapshots",
      value: function value() {
        return [];
      }
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "_addonList",
      value: function value() {
        return [];
      }
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "_folderList",
      value: function value() {
        return [{
          slug: "homeassistant",
          name: "Home Assistant configuration",
          checked: true
        }, {
          slug: "ssl",
          name: "SSL",
          checked: true
        }, {
          slug: "share",
          name: "Share",
          checked: true
        }, {
          slug: "addons/local",
          name: "Local add-ons",
          checked: true
        }];
      }
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "_creatingSnapshot",
      value: function value() {
        return false;
      }
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "_error",
      value: function value() {
        return "";
      }
    }, {
      kind: "method",
      key: "refreshData",
      value: function () {
        var _refreshData = hassio_snapshots_asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee() {
          return regeneratorRuntime.wrap(function _callee$(_context) {
            while (1) {
              switch (_context.prev = _context.next) {
                case 0:
                  _context.next = 2;
                  return Object(hassio_snapshot["e" /* reloadHassioSnapshots */])(this.hass);

                case 2:
                  _context.next = 4;
                  return this._updateSnapshots();

                case 4:
                case "end":
                  return _context.stop();
              }
            }
          }, _callee, this);
        }));

        function refreshData() {
          return _refreshData.apply(this, arguments);
        }

        return refreshData;
      }()
    }, {
      kind: "method",
      key: "render",
      value: function render() {
        var _this2 = this;

        return Object(lit_element["e" /* html */])(hassio_snapshots_templateObject(), this.hass, this.narrow, this.route, supervisorTabs, this.refreshData, this._snapshotName, this._handleTextValueChanged, this._snapshotType, this._handleRadioValueChanged, this._snapshotType === "full" ? undefined : Object(lit_element["e" /* html */])(hassio_snapshots_templateObject2(), this._folderList.map(function (folder, idx) {
          return Object(lit_element["e" /* html */])(hassio_snapshots_templateObject3(), idx, folder.checked, _this2._folderChecked, folder.name);
        }), this._addonList.map(function (addon, idx) {
          return Object(lit_element["e" /* html */])(hassio_snapshots_templateObject4(), idx, addon.checked, _this2._addonChecked, addon.name);
        })), this._snapshotHasPassword, this._handleCheckboxValueChanged, this._snapshotHasPassword ? Object(lit_element["e" /* html */])(hassio_snapshots_templateObject5(), this._snapshotPassword, this._handleTextValueChanged) : undefined, this._error !== "" ? Object(lit_element["e" /* html */])(hassio_snapshots_templateObject6(), this._error) : undefined, this._creatingSnapshot, this._createSnapshot, this._snapshots === undefined ? undefined : this._snapshots.length === 0 ? Object(lit_element["e" /* html */])(hassio_snapshots_templateObject7()) : this._snapshots.map(function (snapshot) {
          return Object(lit_element["e" /* html */])(_templateObject8(), snapshot, _this2._snapshotClicked, _this2.hass, snapshot.name || snapshot.slug, _this2._computeDetails(snapshot), snapshot.date, snapshot.type === "full" ? "hassio:package-variant-closed" : "hassio:package-variant");
        }));
      }
    }, {
      kind: "method",
      key: "firstUpdated",
      value: function firstUpdated(changedProps) {
        hassio_snapshots_get(hassio_snapshots_getPrototypeOf(HassioSnapshots.prototype), "firstUpdated", this).call(this, changedProps);

        this._updateSnapshots();
      }
    }, {
      kind: "method",
      key: "updated",
      value: function updated(changedProps) {
        if (changedProps.has("supervisorInfo")) {
          this._addonList = this.supervisorInfo.addons.map(function (addon) {
            return {
              slug: addon.slug,
              name: addon.name,
              checked: true
            };
          }).sort(function (a, b) {
            return a.name < b.name ? -1 : 1;
          });
        }
      }
    }, {
      kind: "method",
      key: "_handleTextValueChanged",
      value: function _handleTextValueChanged(ev) {
        var input = ev.currentTarget;
        this["_".concat(input.name)] = ev.detail.value;
      }
    }, {
      kind: "method",
      key: "_handleCheckboxValueChanged",
      value: function _handleCheckboxValueChanged(ev) {
        var input = ev.currentTarget;
        this["_".concat(input.name)] = input.checked;
      }
    }, {
      kind: "method",
      key: "_handleRadioValueChanged",
      value: function _handleRadioValueChanged(ev) {
        var input = ev.currentTarget;
        this["_".concat(input.getAttribute("name"))] = ev.detail.value;
      }
    }, {
      kind: "method",
      key: "_folderChecked",
      value: function _folderChecked(ev) {
        var _ref = ev.currentTarget,
            idx = _ref.idx,
            checked = _ref.checked;
        this._folderList = this._folderList.map(function (folder, curIdx) {
          return curIdx === idx ? Object.assign({}, folder, {
            checked: checked
          }) : folder;
        });
      }
    }, {
      kind: "method",
      key: "_addonChecked",
      value: function _addonChecked(ev) {
        var _ref2 = ev.currentTarget,
            idx = _ref2.idx,
            checked = _ref2.checked;
        this._addonList = this._addonList.map(function (addon, curIdx) {
          return curIdx === idx ? Object.assign({}, addon, {
            checked: checked
          }) : addon;
        });
      }
    }, {
      kind: "method",
      key: "_updateSnapshots",
      value: function () {
        var _updateSnapshots2 = hassio_snapshots_asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee2() {
          return regeneratorRuntime.wrap(function _callee2$(_context2) {
            while (1) {
              switch (_context2.prev = _context2.next) {
                case 0:
                  _context2.prev = 0;
                  _context2.next = 3;
                  return Object(hassio_snapshot["d" /* fetchHassioSnapshots */])(this.hass);

                case 3:
                  this._snapshots = _context2.sent;

                  this._snapshots.sort(function (a, b) {
                    return a.date < b.date ? 1 : -1;
                  });

                  _context2.next = 10;
                  break;

                case 7:
                  _context2.prev = 7;
                  _context2.t0 = _context2["catch"](0);
                  this._error = _context2.t0.message;

                case 10:
                case "end":
                  return _context2.stop();
              }
            }
          }, _callee2, this, [[0, 7]]);
        }));

        function _updateSnapshots() {
          return _updateSnapshots2.apply(this, arguments);
        }

        return _updateSnapshots;
      }()
    }, {
      kind: "method",
      key: "_createSnapshot",
      value: function () {
        var _createSnapshot2 = hassio_snapshots_asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee3() {
          var name, data, addons, folders, _data;

          return regeneratorRuntime.wrap(function _callee3$(_context3) {
            while (1) {
              switch (_context3.prev = _context3.next) {
                case 0:
                  this._error = "";

                  if (!(this._snapshotHasPassword && !this._snapshotPassword.length)) {
                    _context3.next = 4;
                    break;
                  }

                  this._error = "Please enter a password.";
                  return _context3.abrupt("return");

                case 4:
                  this._creatingSnapshot = true;
                  _context3.next = 7;
                  return this.updateComplete;

                case 7:
                  name = this._snapshotName || new Date().toLocaleDateString(navigator.language, {
                    weekday: "long",
                    year: "numeric",
                    month: "short",
                    day: "numeric"
                  });
                  _context3.prev = 8;

                  if (!(this._snapshotType === "full")) {
                    _context3.next = 16;
                    break;
                  }

                  data = {
                    name: name
                  };

                  if (this._snapshotHasPassword) {
                    data.password = this._snapshotPassword;
                  }

                  _context3.next = 14;
                  return Object(hassio_snapshot["a" /* createHassioFullSnapshot */])(this.hass, data);

                case 14:
                  _context3.next = 22;
                  break;

                case 16:
                  addons = this._addonList.filter(function (addon) {
                    return addon.checked;
                  }).map(function (addon) {
                    return addon.slug;
                  });
                  folders = this._folderList.filter(function (folder) {
                    return folder.checked;
                  }).map(function (folder) {
                    return folder.slug;
                  });
                  _data = {
                    name: name,
                    folders: folders,
                    addons: addons
                  };

                  if (this._snapshotHasPassword) {
                    _data.password = this._snapshotPassword;
                  }

                  _context3.next = 22;
                  return Object(hassio_snapshot["b" /* createHassioPartialSnapshot */])(this.hass, _data);

                case 22:
                  this._updateSnapshots();

                  Object(fire_event["a" /* fireEvent */])(this, "hass-api-called", {
                    success: true,
                    response: null
                  });
                  _context3.next = 29;
                  break;

                case 26:
                  _context3.prev = 26;
                  _context3.t0 = _context3["catch"](8);
                  this._error = _context3.t0.message;

                case 29:
                  _context3.prev = 29;
                  this._creatingSnapshot = false;
                  return _context3.finish(29);

                case 32:
                case "end":
                  return _context3.stop();
              }
            }
          }, _callee3, this, [[8, 26, 29, 32]]);
        }));

        function _createSnapshot() {
          return _createSnapshot2.apply(this, arguments);
        }

        return _createSnapshot;
      }()
    }, {
      kind: "method",
      key: "_computeDetails",
      value: function _computeDetails(snapshot) {
        var type = snapshot.type === "full" ? "Full snapshot" : "Partial snapshot";
        return snapshot["protected"] ? "".concat(type, ", password protected") : type;
      }
    }, {
      kind: "method",
      key: "_snapshotClicked",
      value: function _snapshotClicked(ev) {
        var _this3 = this;

        show_dialog_hassio_snapshot_showHassioSnapshotDialog(this, {
          slug: ev.currentTarget.snapshot.slug,
          onDelete: function onDelete() {
            return _this3._updateSnapshots();
          }
        });
      }
    }, {
      kind: "get",
      "static": true,
      key: "styles",
      value: function styles() {
        return [resources_styles["b" /* haStyle */], hassio_style["a" /* hassioStyle */], Object(lit_element["c" /* css */])(_templateObject9())];
      }
    }]
  };
}, lit_element["a" /* LitElement */]);
// EXTERNAL MODULE: ./node_modules/@polymer/paper-menu-button/paper-menu-button.js + 5 modules
var paper_menu_button = __webpack_require__(134);

// EXTERNAL MODULE: ./src/data/hassio/hardware.ts
var hardware = __webpack_require__(127);

// EXTERNAL MODULE: ./hassio/src/dialogs/markdown/show-dialog-hassio-markdown.ts
var show_dialog_hassio_markdown = __webpack_require__(128);

// CONCATENATED MODULE: ./hassio/src/system/hassio-host-info.ts
function hassio_host_info_asyncGeneratorStep(gen, resolve, reject, _next, _throw, key, arg) { try { var info = gen[key](arg); var value = info.value; } catch (error) { reject(error); return; } if (info.done) { resolve(value); } else { Promise.resolve(value).then(_next, _throw); } }

function hassio_host_info_asyncToGenerator(fn) { return function () { var self = this, args = arguments; return new Promise(function (resolve, reject) { var gen = fn.apply(self, args); function _next(value) { hassio_host_info_asyncGeneratorStep(gen, resolve, reject, _next, _throw, "next", value); } function _throw(err) { hassio_host_info_asyncGeneratorStep(gen, resolve, reject, _next, _throw, "throw", err); } _next(undefined); }); }; }

function hassio_host_info_typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { hassio_host_info_typeof = function _typeof(obj) { return typeof obj; }; } else { hassio_host_info_typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return hassio_host_info_typeof(obj); }

function hassio_host_info_templateObject9() {
  var data = hassio_host_info_taggedTemplateLiteral(["\n        paper-card {\n          height: 100%;\n          width: 100%;\n        }\n        .card-content {\n          color: var(--primary-text-color);\n          box-sizing: border-box;\n          height: calc(100% - 47px);\n        }\n        .info {\n          width: 100%;\n        }\n        .info td:nth-child(2) {\n          text-align: right;\n        }\n        .errors {\n          color: var(--google-red-500);\n          margin-top: 16px;\n        }\n        mwc-button.info {\n          max-width: calc(50% - 12px);\n        }\n        table.info {\n          margin-bottom: 10px;\n        }\n        .warning {\n          --mdc-theme-primary: var(--google-red-500);\n        }\n      "]);

  hassio_host_info_templateObject9 = function _templateObject9() {
    return data;
  };

  return data;
}

function hassio_host_info_templateObject8() {
  var data = hassio_host_info_taggedTemplateLiteral([" <mwc-button @click=", ">Update</mwc-button> "]);

  hassio_host_info_templateObject8 = function _templateObject8() {
    return data;
  };

  return data;
}

function hassio_host_info_templateObject7() {
  var data = hassio_host_info_taggedTemplateLiteral(["\n                <ha-call-api-button\n                  class=\"warning\"\n                  .hass=", "\n                  path=\"hassio/os/config/sync\"\n                  title=\"Load HassOS configs or updates from USB\"\n                  >Import from USB</ha-call-api-button\n                >\n              "]);

  hassio_host_info_templateObject7 = function _templateObject7() {
    return data;
  };

  return data;
}

function hassio_host_info_templateObject6() {
  var data = hassio_host_info_taggedTemplateLiteral(["\n                <mwc-button class=\"warning\" @click=", "\n                  >Shutdown</mwc-button\n                >\n              "]);

  hassio_host_info_templateObject6 = function _templateObject6() {
    return data;
  };

  return data;
}

function hassio_host_info_templateObject5() {
  var data = hassio_host_info_taggedTemplateLiteral(["\n                <mwc-button class=\"warning\" @click=", "\n                  >Reboot</mwc-button\n                >\n              "]);

  hassio_host_info_templateObject5 = function _templateObject5() {
    return data;
  };

  return data;
}

function hassio_host_info_templateObject4() {
  var data = hassio_host_info_taggedTemplateLiteral([" <div class=\"errors\">Error: ", "</div> "]);

  hassio_host_info_templateObject4 = function _templateObject4() {
    return data;
  };

  return data;
}

function hassio_host_info_templateObject3() {
  var data = hassio_host_info_taggedTemplateLiteral(["\n                <mwc-button\n                  raised\n                  @click=", "\n                  class=\"info\"\n                >\n                  Change hostname\n                </mwc-button>\n              "]);

  hassio_host_info_templateObject3 = function _templateObject3() {
    return data;
  };

  return data;
}

function hassio_host_info_templateObject2() {
  var data = hassio_host_info_taggedTemplateLiteral(["\n                    <tr>\n                      <td>Deployment</td>\n                      <td>", "</td>\n                    </tr>\n                  "]);

  hassio_host_info_templateObject2 = function _templateObject2() {
    return data;
  };

  return data;
}

function hassio_host_info_templateObject() {
  var data = hassio_host_info_taggedTemplateLiteral(["\n      <paper-card>\n        <div class=\"card-content\">\n          <h2>Host system</h2>\n          <table class=\"info\">\n            <tbody>\n              <tr>\n                <td>Hostname</td>\n                <td>", "</td>\n              </tr>\n              <tr>\n                <td>System</td>\n                <td>", "</td>\n              </tr>\n              ", "\n            </tbody>\n          </table>\n          <mwc-button raised @click=", " class=\"info\">\n            Hardware\n          </mwc-button>\n          ", "\n          ", "\n        </div>\n        <div class=\"card-actions\">\n          ", "\n          ", "\n          ", "\n          ", "\n        </div>\n      </paper-card>\n    "]);

  hassio_host_info_templateObject = function _templateObject() {
    return data;
  };

  return data;
}

function hassio_host_info_taggedTemplateLiteral(strings, raw) { if (!raw) { raw = strings.slice(0); } return Object.freeze(Object.defineProperties(strings, { raw: { value: Object.freeze(raw) } })); }

function hassio_host_info_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function hassio_host_info_inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) hassio_host_info_setPrototypeOf(subClass, superClass); }

function hassio_host_info_setPrototypeOf(o, p) { hassio_host_info_setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return hassio_host_info_setPrototypeOf(o, p); }

function hassio_host_info_createSuper(Derived) { return function () { var Super = hassio_host_info_getPrototypeOf(Derived), result; if (hassio_host_info_isNativeReflectConstruct()) { var NewTarget = hassio_host_info_getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return hassio_host_info_possibleConstructorReturn(this, result); }; }

function hassio_host_info_possibleConstructorReturn(self, call) { if (call && (hassio_host_info_typeof(call) === "object" || typeof call === "function")) { return call; } return hassio_host_info_assertThisInitialized(self); }

function hassio_host_info_assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function hassio_host_info_isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Date.prototype.toString.call(Reflect.construct(Date, [], function () {})); return true; } catch (e) { return false; } }

function hassio_host_info_getPrototypeOf(o) { hassio_host_info_getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return hassio_host_info_getPrototypeOf(o); }

function hassio_host_info_decorate(decorators, factory, superClass, mixins) { var api = hassio_host_info_getDecoratorsApi(); if (mixins) { for (var i = 0; i < mixins.length; i++) { api = mixins[i](api); } } var r = factory(function initialize(O) { api.initializeInstanceElements(O, decorated.elements); }, superClass); var decorated = api.decorateClass(hassio_host_info_coalesceClassElements(r.d.map(hassio_host_info_createElementDescriptor)), decorators); api.initializeClassElements(r.F, decorated.elements); return api.runClassFinishers(r.F, decorated.finishers); }

function hassio_host_info_getDecoratorsApi() { hassio_host_info_getDecoratorsApi = function _getDecoratorsApi() { return api; }; var api = { elementsDefinitionOrder: [["method"], ["field"]], initializeInstanceElements: function initializeInstanceElements(O, elements) { ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { if (element.kind === kind && element.placement === "own") { this.defineClassElement(O, element); } }, this); }, this); }, initializeClassElements: function initializeClassElements(F, elements) { var proto = F.prototype; ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { var placement = element.placement; if (element.kind === kind && (placement === "static" || placement === "prototype")) { var receiver = placement === "static" ? F : proto; this.defineClassElement(receiver, element); } }, this); }, this); }, defineClassElement: function defineClassElement(receiver, element) { var descriptor = element.descriptor; if (element.kind === "field") { var initializer = element.initializer; descriptor = { enumerable: descriptor.enumerable, writable: descriptor.writable, configurable: descriptor.configurable, value: initializer === void 0 ? void 0 : initializer.call(receiver) }; } Object.defineProperty(receiver, element.key, descriptor); }, decorateClass: function decorateClass(elements, decorators) { var newElements = []; var finishers = []; var placements = { "static": [], prototype: [], own: [] }; elements.forEach(function (element) { this.addElementPlacement(element, placements); }, this); elements.forEach(function (element) { if (!hassio_host_info_hasDecorators(element)) return newElements.push(element); var elementFinishersExtras = this.decorateElement(element, placements); newElements.push(elementFinishersExtras.element); newElements.push.apply(newElements, elementFinishersExtras.extras); finishers.push.apply(finishers, elementFinishersExtras.finishers); }, this); if (!decorators) { return { elements: newElements, finishers: finishers }; } var result = this.decorateConstructor(newElements, decorators); finishers.push.apply(finishers, result.finishers); result.finishers = finishers; return result; }, addElementPlacement: function addElementPlacement(element, placements, silent) { var keys = placements[element.placement]; if (!silent && keys.indexOf(element.key) !== -1) { throw new TypeError("Duplicated element (" + element.key + ")"); } keys.push(element.key); }, decorateElement: function decorateElement(element, placements) { var extras = []; var finishers = []; for (var decorators = element.decorators, i = decorators.length - 1; i >= 0; i--) { var keys = placements[element.placement]; keys.splice(keys.indexOf(element.key), 1); var elementObject = this.fromElementDescriptor(element); var elementFinisherExtras = this.toElementFinisherExtras((0, decorators[i])(elementObject) || elementObject); element = elementFinisherExtras.element; this.addElementPlacement(element, placements); if (elementFinisherExtras.finisher) { finishers.push(elementFinisherExtras.finisher); } var newExtras = elementFinisherExtras.extras; if (newExtras) { for (var j = 0; j < newExtras.length; j++) { this.addElementPlacement(newExtras[j], placements); } extras.push.apply(extras, newExtras); } } return { element: element, finishers: finishers, extras: extras }; }, decorateConstructor: function decorateConstructor(elements, decorators) { var finishers = []; for (var i = decorators.length - 1; i >= 0; i--) { var obj = this.fromClassDescriptor(elements); var elementsAndFinisher = this.toClassDescriptor((0, decorators[i])(obj) || obj); if (elementsAndFinisher.finisher !== undefined) { finishers.push(elementsAndFinisher.finisher); } if (elementsAndFinisher.elements !== undefined) { elements = elementsAndFinisher.elements; for (var j = 0; j < elements.length - 1; j++) { for (var k = j + 1; k < elements.length; k++) { if (elements[j].key === elements[k].key && elements[j].placement === elements[k].placement) { throw new TypeError("Duplicated element (" + elements[j].key + ")"); } } } } } return { elements: elements, finishers: finishers }; }, fromElementDescriptor: function fromElementDescriptor(element) { var obj = { kind: element.kind, key: element.key, placement: element.placement, descriptor: element.descriptor }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); if (element.kind === "field") obj.initializer = element.initializer; return obj; }, toElementDescriptors: function toElementDescriptors(elementObjects) { if (elementObjects === undefined) return; return hassio_host_info_toArray(elementObjects).map(function (elementObject) { var element = this.toElementDescriptor(elementObject); this.disallowProperty(elementObject, "finisher", "An element descriptor"); this.disallowProperty(elementObject, "extras", "An element descriptor"); return element; }, this); }, toElementDescriptor: function toElementDescriptor(elementObject) { var kind = String(elementObject.kind); if (kind !== "method" && kind !== "field") { throw new TypeError('An element descriptor\'s .kind property must be either "method" or' + ' "field", but a decorator created an element descriptor with' + ' .kind "' + kind + '"'); } var key = hassio_host_info_toPropertyKey(elementObject.key); var placement = String(elementObject.placement); if (placement !== "static" && placement !== "prototype" && placement !== "own") { throw new TypeError('An element descriptor\'s .placement property must be one of "static",' + ' "prototype" or "own", but a decorator created an element descriptor' + ' with .placement "' + placement + '"'); } var descriptor = elementObject.descriptor; this.disallowProperty(elementObject, "elements", "An element descriptor"); var element = { kind: kind, key: key, placement: placement, descriptor: Object.assign({}, descriptor) }; if (kind !== "field") { this.disallowProperty(elementObject, "initializer", "A method descriptor"); } else { this.disallowProperty(descriptor, "get", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "set", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "value", "The property descriptor of a field descriptor"); element.initializer = elementObject.initializer; } return element; }, toElementFinisherExtras: function toElementFinisherExtras(elementObject) { var element = this.toElementDescriptor(elementObject); var finisher = hassio_host_info_optionalCallableProperty(elementObject, "finisher"); var extras = this.toElementDescriptors(elementObject.extras); return { element: element, finisher: finisher, extras: extras }; }, fromClassDescriptor: function fromClassDescriptor(elements) { var obj = { kind: "class", elements: elements.map(this.fromElementDescriptor, this) }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); return obj; }, toClassDescriptor: function toClassDescriptor(obj) { var kind = String(obj.kind); if (kind !== "class") { throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator' + ' created a class descriptor with .kind "' + kind + '"'); } this.disallowProperty(obj, "key", "A class descriptor"); this.disallowProperty(obj, "placement", "A class descriptor"); this.disallowProperty(obj, "descriptor", "A class descriptor"); this.disallowProperty(obj, "initializer", "A class descriptor"); this.disallowProperty(obj, "extras", "A class descriptor"); var finisher = hassio_host_info_optionalCallableProperty(obj, "finisher"); var elements = this.toElementDescriptors(obj.elements); return { elements: elements, finisher: finisher }; }, runClassFinishers: function runClassFinishers(constructor, finishers) { for (var i = 0; i < finishers.length; i++) { var newConstructor = (0, finishers[i])(constructor); if (newConstructor !== undefined) { if (typeof newConstructor !== "function") { throw new TypeError("Finishers must return a constructor."); } constructor = newConstructor; } } return constructor; }, disallowProperty: function disallowProperty(obj, name, objectType) { if (obj[name] !== undefined) { throw new TypeError(objectType + " can't have a ." + name + " property."); } } }; return api; }

function hassio_host_info_createElementDescriptor(def) { var key = hassio_host_info_toPropertyKey(def.key); var descriptor; if (def.kind === "method") { descriptor = { value: def.value, writable: true, configurable: true, enumerable: false }; } else if (def.kind === "get") { descriptor = { get: def.value, configurable: true, enumerable: false }; } else if (def.kind === "set") { descriptor = { set: def.value, configurable: true, enumerable: false }; } else if (def.kind === "field") { descriptor = { configurable: true, writable: true, enumerable: true }; } var element = { kind: def.kind === "field" ? "field" : "method", key: key, placement: def["static"] ? "static" : def.kind === "field" ? "own" : "prototype", descriptor: descriptor }; if (def.decorators) element.decorators = def.decorators; if (def.kind === "field") element.initializer = def.value; return element; }

function hassio_host_info_coalesceGetterSetter(element, other) { if (element.descriptor.get !== undefined) { other.descriptor.get = element.descriptor.get; } else { other.descriptor.set = element.descriptor.set; } }

function hassio_host_info_coalesceClassElements(elements) { var newElements = []; var isSameElement = function isSameElement(other) { return other.kind === "method" && other.key === element.key && other.placement === element.placement; }; for (var i = 0; i < elements.length; i++) { var element = elements[i]; var other; if (element.kind === "method" && (other = newElements.find(isSameElement))) { if (hassio_host_info_isDataDescriptor(element.descriptor) || hassio_host_info_isDataDescriptor(other.descriptor)) { if (hassio_host_info_hasDecorators(element) || hassio_host_info_hasDecorators(other)) { throw new ReferenceError("Duplicated methods (" + element.key + ") can't be decorated."); } other.descriptor = element.descriptor; } else { if (hassio_host_info_hasDecorators(element)) { if (hassio_host_info_hasDecorators(other)) { throw new ReferenceError("Decorators can't be placed on different accessors with for " + "the same property (" + element.key + ")."); } other.decorators = element.decorators; } hassio_host_info_coalesceGetterSetter(element, other); } } else { newElements.push(element); } } return newElements; }

function hassio_host_info_hasDecorators(element) { return element.decorators && element.decorators.length; }

function hassio_host_info_isDataDescriptor(desc) { return desc !== undefined && !(desc.value === undefined && desc.writable === undefined); }

function hassio_host_info_optionalCallableProperty(obj, name) { var value = obj[name]; if (value !== undefined && typeof value !== "function") { throw new TypeError("Expected '" + name + "' to be a function"); } return value; }

function hassio_host_info_toPropertyKey(arg) { var key = hassio_host_info_toPrimitive(arg, "string"); return hassio_host_info_typeof(key) === "symbol" ? key : String(key); }

function hassio_host_info_toPrimitive(input, hint) { if (hassio_host_info_typeof(input) !== "object" || input === null) return input; var prim = input[Symbol.toPrimitive]; if (prim !== undefined) { var res = prim.call(input, hint || "default"); if (hassio_host_info_typeof(res) !== "object") return res; throw new TypeError("@@toPrimitive must return a primitive value."); } return (hint === "string" ? String : Number)(input); }

function hassio_host_info_toArray(arr) { return hassio_host_info_arrayWithHoles(arr) || hassio_host_info_iterableToArray(arr) || hassio_host_info_unsupportedIterableToArray(arr) || hassio_host_info_nonIterableRest(); }

function hassio_host_info_nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function hassio_host_info_unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return hassio_host_info_arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(n); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return hassio_host_info_arrayLikeToArray(o, minLen); }

function hassio_host_info_arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function hassio_host_info_iterableToArray(iter) { if (typeof Symbol !== "undefined" && Symbol.iterator in Object(iter)) return Array.from(iter); }

function hassio_host_info_arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }












var hassio_host_info_HassioHostInfo = hassio_host_info_decorate([Object(lit_element["d" /* customElement */])("hassio-host-info")], function (_initialize, _LitElement) {
  var HassioHostInfo = /*#__PURE__*/function (_LitElement2) {
    hassio_host_info_inherits(HassioHostInfo, _LitElement2);

    var _super = hassio_host_info_createSuper(HassioHostInfo);

    function HassioHostInfo() {
      var _this;

      hassio_host_info_classCallCheck(this, HassioHostInfo);

      for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
        args[_key] = arguments[_key];
      }

      _this = _super.call.apply(_super, [this].concat(args));

      _initialize(hassio_host_info_assertThisInitialized(_this));

      return _this;
    }

    return HassioHostInfo;
  }(_LitElement);

  return {
    F: HassioHostInfo,
    d: [{
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "hass",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "hostInfo",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "hassOsInfo",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "_errors",
      value: void 0
    }, {
      kind: "method",
      key: "render",
      value: function render() {
        return Object(lit_element["e" /* html */])(hassio_host_info_templateObject(), this.hostInfo.hostname, this.hostInfo.operating_system, this.hostInfo.deployment ? Object(lit_element["e" /* html */])(hassio_host_info_templateObject2(), this.hostInfo.deployment) : "", this._showHardware, this.hostInfo.features.includes("hostname") ? Object(lit_element["e" /* html */])(hassio_host_info_templateObject3(), this._changeHostnameClicked) : "", this._errors ? Object(lit_element["e" /* html */])(hassio_host_info_templateObject4(), this._errors) : "", this.hostInfo.features.includes("reboot") ? Object(lit_element["e" /* html */])(hassio_host_info_templateObject5(), this._rebootHost) : "", this.hostInfo.features.includes("shutdown") ? Object(lit_element["e" /* html */])(hassio_host_info_templateObject6(), this._shutdownHost) : "", this.hostInfo.features.includes("hassos") ? Object(lit_element["e" /* html */])(hassio_host_info_templateObject7(), this.hass) : "", this.hostInfo.version !== this.hostInfo.version_latest ? Object(lit_element["e" /* html */])(hassio_host_info_templateObject8(), this._updateOS) : "");
      }
    }, {
      kind: "get",
      "static": true,
      key: "styles",
      value: function styles() {
        return [resources_styles["b" /* haStyle */], hassio_style["a" /* hassioStyle */], Object(lit_element["c" /* css */])(hassio_host_info_templateObject9())];
      }
    }, {
      kind: "method",
      key: "firstUpdated",
      value: function firstUpdated() {
        var _this2 = this;

        this.addEventListener("hass-api-called", function (ev) {
          return _this2._apiCalled(ev);
        });
      }
    }, {
      kind: "method",
      key: "_apiCalled",
      value: function _apiCalled(ev) {
        if (ev.detail.success) {
          this._errors = undefined;
          return;
        }

        var response = ev.detail.response;
        this._errors = hassio_host_info_typeof(response.body) === "object" ? response.body.message || "Unknown error" : response.body;
      }
    }, {
      kind: "method",
      key: "_showHardware",
      value: function () {
        var _showHardware2 = hassio_host_info_asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee() {
          var content;
          return regeneratorRuntime.wrap(function _callee$(_context) {
            while (1) {
              switch (_context.prev = _context.next) {
                case 0:
                  _context.prev = 0;
                  _context.t0 = this;
                  _context.next = 4;
                  return Object(hardware["b" /* fetchHassioHardwareInfo */])(this.hass);

                case 4:
                  _context.t1 = _context.sent;
                  content = _context.t0._objectToMarkdown.call(_context.t0, _context.t1);
                  Object(show_dialog_hassio_markdown["a" /* showHassioMarkdownDialog */])(this, {
                    title: "Hardware",
                    content: content
                  });
                  _context.next = 12;
                  break;

                case 9:
                  _context.prev = 9;
                  _context.t2 = _context["catch"](0);
                  Object(show_dialog_hassio_markdown["a" /* showHassioMarkdownDialog */])(this, {
                    title: "Hardware",
                    content: "Error getting hardware info"
                  });

                case 12:
                case "end":
                  return _context.stop();
              }
            }
          }, _callee, this, [[0, 9]]);
        }));

        function _showHardware() {
          return _showHardware2.apply(this, arguments);
        }

        return _showHardware;
      }()
    }, {
      kind: "method",
      key: "_rebootHost",
      value: function () {
        var _rebootHost2 = hassio_host_info_asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee2() {
          var confirmed;
          return regeneratorRuntime.wrap(function _callee2$(_context2) {
            while (1) {
              switch (_context2.prev = _context2.next) {
                case 0:
                  _context2.next = 2;
                  return Object(show_dialog_box["b" /* showConfirmationDialog */])(this, {
                    title: "Reboot",
                    text: "Are you sure you want to reboot the host?",
                    confirmText: "reboot host",
                    dismissText: "no"
                  });

                case 2:
                  confirmed = _context2.sent;

                  if (confirmed) {
                    _context2.next = 5;
                    break;
                  }

                  return _context2.abrupt("return");

                case 5:
                  _context2.prev = 5;
                  _context2.next = 8;
                  return rebootHost(this.hass);

                case 8:
                  _context2.next = 13;
                  break;

                case 10:
                  _context2.prev = 10;
                  _context2.t0 = _context2["catch"](5);
                  Object(show_dialog_box["a" /* showAlertDialog */])(this, {
                    title: "Failed to reboot",
                    text: _context2.t0.body.message
                  });

                case 13:
                case "end":
                  return _context2.stop();
              }
            }
          }, _callee2, this, [[5, 10]]);
        }));

        function _rebootHost() {
          return _rebootHost2.apply(this, arguments);
        }

        return _rebootHost;
      }()
    }, {
      kind: "method",
      key: "_shutdownHost",
      value: function () {
        var _shutdownHost2 = hassio_host_info_asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee3() {
          var confirmed;
          return regeneratorRuntime.wrap(function _callee3$(_context3) {
            while (1) {
              switch (_context3.prev = _context3.next) {
                case 0:
                  _context3.next = 2;
                  return Object(show_dialog_box["b" /* showConfirmationDialog */])(this, {
                    title: "Shutdown",
                    text: "Are you sure you want to shutdown the host?",
                    confirmText: "shutdown host",
                    dismissText: "no"
                  });

                case 2:
                  confirmed = _context3.sent;

                  if (confirmed) {
                    _context3.next = 5;
                    break;
                  }

                  return _context3.abrupt("return");

                case 5:
                  _context3.prev = 5;
                  _context3.next = 8;
                  return shutdownHost(this.hass);

                case 8:
                  _context3.next = 13;
                  break;

                case 10:
                  _context3.prev = 10;
                  _context3.t0 = _context3["catch"](5);
                  Object(show_dialog_box["a" /* showAlertDialog */])(this, {
                    title: "Failed to shutdown",
                    text: _context3.t0.body.message
                  });

                case 13:
                case "end":
                  return _context3.stop();
              }
            }
          }, _callee3, this, [[5, 10]]);
        }));

        function _shutdownHost() {
          return _shutdownHost2.apply(this, arguments);
        }

        return _shutdownHost;
      }()
    }, {
      kind: "method",
      key: "_updateOS",
      value: function () {
        var _updateOS2 = hassio_host_info_asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee4() {
          var confirmed;
          return regeneratorRuntime.wrap(function _callee4$(_context4) {
            while (1) {
              switch (_context4.prev = _context4.next) {
                case 0:
                  _context4.next = 2;
                  return Object(show_dialog_box["b" /* showConfirmationDialog */])(this, {
                    title: "Update",
                    text: "Are you sure you want to update the OS?",
                    confirmText: "update os",
                    dismissText: "no"
                  });

                case 2:
                  confirmed = _context4.sent;

                  if (confirmed) {
                    _context4.next = 5;
                    break;
                  }

                  return _context4.abrupt("return");

                case 5:
                  _context4.prev = 5;
                  _context4.next = 8;
                  return updateOS(this.hass);

                case 8:
                  _context4.next = 13;
                  break;

                case 10:
                  _context4.prev = 10;
                  _context4.t0 = _context4["catch"](5);
                  Object(show_dialog_box["a" /* showAlertDialog */])(this, {
                    title: "Failed to update",
                    text: _context4.t0.body.message
                  });

                case 13:
                case "end":
                  return _context4.stop();
              }
            }
          }, _callee4, this, [[5, 10]]);
        }));

        function _updateOS() {
          return _updateOS2.apply(this, arguments);
        }

        return _updateOS;
      }()
    }, {
      kind: "method",
      key: "_objectToMarkdown",
      value: function _objectToMarkdown(obj) {
        var _this3 = this;

        var indent = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : "";
        var data = "";
        Object.keys(obj).forEach(function (key) {
          if (hassio_host_info_typeof(obj[key]) !== "object") {
            data += "".concat(indent, "- ").concat(key, ": ").concat(obj[key], "\n");
          } else {
            data += "".concat(indent, "- ").concat(key, ":\n");

            if (Array.isArray(obj[key])) {
              if (obj[key].length) {
                data += "".concat(indent, "    - ") + obj[key].join("\n".concat(indent, "    - ")) + "\n";
              }
            } else {
              data += _this3._objectToMarkdown(obj[key], "    ".concat(indent));
            }
          }
        });
        return data;
      }
    }, {
      kind: "method",
      key: "_changeHostnameClicked",
      value: function () {
        var _changeHostnameClicked2 = hassio_host_info_asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee5() {
          var curHostname, hostname;
          return regeneratorRuntime.wrap(function _callee5$(_context5) {
            while (1) {
              switch (_context5.prev = _context5.next) {
                case 0:
                  curHostname = this.hostInfo.hostname;
                  _context5.next = 3;
                  return Object(show_dialog_box["c" /* showPromptDialog */])(this, {
                    title: "Change hostname",
                    inputLabel: "Please enter a new hostname:",
                    inputType: "string",
                    defaultValue: curHostname
                  });

                case 3:
                  hostname = _context5.sent;

                  if (!(hostname && hostname !== curHostname)) {
                    _context5.next = 16;
                    break;
                  }

                  _context5.prev = 5;
                  _context5.next = 8;
                  return changeHostOptions(this.hass, {
                    hostname: hostname
                  });

                case 8:
                  _context5.next = 10;
                  return fetchHassioHostInfo(this.hass);

                case 10:
                  this.hostInfo = _context5.sent;
                  _context5.next = 16;
                  break;

                case 13:
                  _context5.prev = 13;
                  _context5.t0 = _context5["catch"](5);
                  Object(show_dialog_box["a" /* showAlertDialog */])(this, {
                    title: "Setting hostname failed",
                    text: _context5.t0.body.message
                  });

                case 16:
                case "end":
                  return _context5.stop();
              }
            }
          }, _callee5, this, [[5, 13]]);
        }));

        function _changeHostnameClicked() {
          return _changeHostnameClicked2.apply(this, arguments);
        }

        return _changeHostnameClicked;
      }()
    }]
  };
}, lit_element["a" /* LitElement */]);
// CONCATENATED MODULE: ./hassio/src/system/hassio-supervisor-info.ts
function hassio_supervisor_info_templateObject8() {
  var data = hassio_supervisor_info_taggedTemplateLiteral([" Beta releases are for testers and early adopters and can\n        contain unstable code changes.\n        <br />\n        <b>\n          Make sure you have backups of your data before you activate this\n          feature.\n        </b>\n        <br /><br />\n        This includes beta releases for:\n        <li>Home Assistant Core</li>\n        <li>Home Assistant Supervisor</li>\n        <li>Home Assistant Operating System</li>\n        <br />\n        Do you want to join the beta channel?"]);

  hassio_supervisor_info_templateObject8 = function _templateObject8() {
    return data;
  };

  return data;
}

function hassio_supervisor_info_asyncGeneratorStep(gen, resolve, reject, _next, _throw, key, arg) { try { var info = gen[key](arg); var value = info.value; } catch (error) { reject(error); return; } if (info.done) { resolve(value); } else { Promise.resolve(value).then(_next, _throw); } }

function hassio_supervisor_info_asyncToGenerator(fn) { return function () { var self = this, args = arguments; return new Promise(function (resolve, reject) { var gen = fn.apply(self, args); function _next(value) { hassio_supervisor_info_asyncGeneratorStep(gen, resolve, reject, _next, _throw, "next", value); } function _throw(err) { hassio_supervisor_info_asyncGeneratorStep(gen, resolve, reject, _next, _throw, "throw", err); } _next(undefined); }); }; }

function hassio_supervisor_info_typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { hassio_supervisor_info_typeof = function _typeof(obj) { return typeof obj; }; } else { hassio_supervisor_info_typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return hassio_supervisor_info_typeof(obj); }

function hassio_supervisor_info_templateObject7() {
  var data = hassio_supervisor_info_taggedTemplateLiteral(["\n        paper-card {\n          height: 100%;\n          width: 100%;\n        }\n        .card-content {\n          color: var(--primary-text-color);\n          box-sizing: border-box;\n          height: calc(100% - 47px);\n        }\n        .info {\n          width: 100%;\n        }\n        .info td:nth-child(2) {\n          text-align: right;\n        }\n        .errors {\n          color: var(--google-red-500);\n          margin-top: 16px;\n        }\n      "]);

  hassio_supervisor_info_templateObject7 = function _templateObject7() {
    return data;
  };

  return data;
}

function hassio_supervisor_info_templateObject6() {
  var data = hassio_supervisor_info_taggedTemplateLiteral(["\n                <mwc-button\n                  @click=", "\n                  class=\"warning\"\n                  title=\"Get beta updates for Home Assistant (RCs), supervisor and host\"\n                  >Join beta channel</mwc-button\n                >\n              "]);

  hassio_supervisor_info_templateObject6 = function _templateObject6() {
    return data;
  };

  return data;
}

function hassio_supervisor_info_templateObject5() {
  var data = hassio_supervisor_info_taggedTemplateLiteral(["\n                <ha-call-api-button\n                  .hass=", "\n                  path=\"hassio/supervisor/options\"\n                  .data=", "\n                  >Leave beta channel</ha-call-api-button\n                >\n              "]);

  hassio_supervisor_info_templateObject5 = function _templateObject5() {
    return data;
  };

  return data;
}

function hassio_supervisor_info_templateObject4() {
  var data = hassio_supervisor_info_taggedTemplateLiteral(["\n                <ha-call-api-button\n                  .hass=", "\n                  path=\"hassio/supervisor/update\"\n                  >Update</ha-call-api-button\n                >\n              "]);

  hassio_supervisor_info_templateObject4 = function _templateObject4() {
    return data;
  };

  return data;
}

function hassio_supervisor_info_templateObject3() {
  var data = hassio_supervisor_info_taggedTemplateLiteral([" <div class=\"errors\">Error: ", "</div> "]);

  hassio_supervisor_info_templateObject3 = function _templateObject3() {
    return data;
  };

  return data;
}

function hassio_supervisor_info_templateObject2() {
  var data = hassio_supervisor_info_taggedTemplateLiteral(["\n                    <tr>\n                      <td>Channel</td>\n                      <td>", "</td>\n                    </tr>\n                  "]);

  hassio_supervisor_info_templateObject2 = function _templateObject2() {
    return data;
  };

  return data;
}

function hassio_supervisor_info_templateObject() {
  var data = hassio_supervisor_info_taggedTemplateLiteral(["\n      <paper-card>\n        <div class=\"card-content\">\n          <h2>Supervisor</h2>\n          <table class=\"info\">\n            <tbody>\n              <tr>\n                <td>Version</td>\n                <td>", "</td>\n              </tr>\n              <tr>\n                <td>Latest version</td>\n                <td>", "</td>\n              </tr>\n              ", "\n            </tbody>\n          </table>\n          ", "\n        </div>\n        <div class=\"card-actions\">\n          <ha-call-api-button .hass=", " path=\"hassio/supervisor/reload\"\n            >Reload</ha-call-api-button\n          >\n          ", "\n          ", "\n          ", "\n        </div>\n      </paper-card>\n    "]);

  hassio_supervisor_info_templateObject = function _templateObject() {
    return data;
  };

  return data;
}

function hassio_supervisor_info_taggedTemplateLiteral(strings, raw) { if (!raw) { raw = strings.slice(0); } return Object.freeze(Object.defineProperties(strings, { raw: { value: Object.freeze(raw) } })); }

function hassio_supervisor_info_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function hassio_supervisor_info_inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) hassio_supervisor_info_setPrototypeOf(subClass, superClass); }

function hassio_supervisor_info_setPrototypeOf(o, p) { hassio_supervisor_info_setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return hassio_supervisor_info_setPrototypeOf(o, p); }

function hassio_supervisor_info_createSuper(Derived) { return function () { var Super = hassio_supervisor_info_getPrototypeOf(Derived), result; if (hassio_supervisor_info_isNativeReflectConstruct()) { var NewTarget = hassio_supervisor_info_getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return hassio_supervisor_info_possibleConstructorReturn(this, result); }; }

function hassio_supervisor_info_possibleConstructorReturn(self, call) { if (call && (hassio_supervisor_info_typeof(call) === "object" || typeof call === "function")) { return call; } return hassio_supervisor_info_assertThisInitialized(self); }

function hassio_supervisor_info_assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function hassio_supervisor_info_isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Date.prototype.toString.call(Reflect.construct(Date, [], function () {})); return true; } catch (e) { return false; } }

function hassio_supervisor_info_getPrototypeOf(o) { hassio_supervisor_info_getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return hassio_supervisor_info_getPrototypeOf(o); }

function hassio_supervisor_info_decorate(decorators, factory, superClass, mixins) { var api = hassio_supervisor_info_getDecoratorsApi(); if (mixins) { for (var i = 0; i < mixins.length; i++) { api = mixins[i](api); } } var r = factory(function initialize(O) { api.initializeInstanceElements(O, decorated.elements); }, superClass); var decorated = api.decorateClass(hassio_supervisor_info_coalesceClassElements(r.d.map(hassio_supervisor_info_createElementDescriptor)), decorators); api.initializeClassElements(r.F, decorated.elements); return api.runClassFinishers(r.F, decorated.finishers); }

function hassio_supervisor_info_getDecoratorsApi() { hassio_supervisor_info_getDecoratorsApi = function _getDecoratorsApi() { return api; }; var api = { elementsDefinitionOrder: [["method"], ["field"]], initializeInstanceElements: function initializeInstanceElements(O, elements) { ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { if (element.kind === kind && element.placement === "own") { this.defineClassElement(O, element); } }, this); }, this); }, initializeClassElements: function initializeClassElements(F, elements) { var proto = F.prototype; ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { var placement = element.placement; if (element.kind === kind && (placement === "static" || placement === "prototype")) { var receiver = placement === "static" ? F : proto; this.defineClassElement(receiver, element); } }, this); }, this); }, defineClassElement: function defineClassElement(receiver, element) { var descriptor = element.descriptor; if (element.kind === "field") { var initializer = element.initializer; descriptor = { enumerable: descriptor.enumerable, writable: descriptor.writable, configurable: descriptor.configurable, value: initializer === void 0 ? void 0 : initializer.call(receiver) }; } Object.defineProperty(receiver, element.key, descriptor); }, decorateClass: function decorateClass(elements, decorators) { var newElements = []; var finishers = []; var placements = { "static": [], prototype: [], own: [] }; elements.forEach(function (element) { this.addElementPlacement(element, placements); }, this); elements.forEach(function (element) { if (!hassio_supervisor_info_hasDecorators(element)) return newElements.push(element); var elementFinishersExtras = this.decorateElement(element, placements); newElements.push(elementFinishersExtras.element); newElements.push.apply(newElements, elementFinishersExtras.extras); finishers.push.apply(finishers, elementFinishersExtras.finishers); }, this); if (!decorators) { return { elements: newElements, finishers: finishers }; } var result = this.decorateConstructor(newElements, decorators); finishers.push.apply(finishers, result.finishers); result.finishers = finishers; return result; }, addElementPlacement: function addElementPlacement(element, placements, silent) { var keys = placements[element.placement]; if (!silent && keys.indexOf(element.key) !== -1) { throw new TypeError("Duplicated element (" + element.key + ")"); } keys.push(element.key); }, decorateElement: function decorateElement(element, placements) { var extras = []; var finishers = []; for (var decorators = element.decorators, i = decorators.length - 1; i >= 0; i--) { var keys = placements[element.placement]; keys.splice(keys.indexOf(element.key), 1); var elementObject = this.fromElementDescriptor(element); var elementFinisherExtras = this.toElementFinisherExtras((0, decorators[i])(elementObject) || elementObject); element = elementFinisherExtras.element; this.addElementPlacement(element, placements); if (elementFinisherExtras.finisher) { finishers.push(elementFinisherExtras.finisher); } var newExtras = elementFinisherExtras.extras; if (newExtras) { for (var j = 0; j < newExtras.length; j++) { this.addElementPlacement(newExtras[j], placements); } extras.push.apply(extras, newExtras); } } return { element: element, finishers: finishers, extras: extras }; }, decorateConstructor: function decorateConstructor(elements, decorators) { var finishers = []; for (var i = decorators.length - 1; i >= 0; i--) { var obj = this.fromClassDescriptor(elements); var elementsAndFinisher = this.toClassDescriptor((0, decorators[i])(obj) || obj); if (elementsAndFinisher.finisher !== undefined) { finishers.push(elementsAndFinisher.finisher); } if (elementsAndFinisher.elements !== undefined) { elements = elementsAndFinisher.elements; for (var j = 0; j < elements.length - 1; j++) { for (var k = j + 1; k < elements.length; k++) { if (elements[j].key === elements[k].key && elements[j].placement === elements[k].placement) { throw new TypeError("Duplicated element (" + elements[j].key + ")"); } } } } } return { elements: elements, finishers: finishers }; }, fromElementDescriptor: function fromElementDescriptor(element) { var obj = { kind: element.kind, key: element.key, placement: element.placement, descriptor: element.descriptor }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); if (element.kind === "field") obj.initializer = element.initializer; return obj; }, toElementDescriptors: function toElementDescriptors(elementObjects) { if (elementObjects === undefined) return; return hassio_supervisor_info_toArray(elementObjects).map(function (elementObject) { var element = this.toElementDescriptor(elementObject); this.disallowProperty(elementObject, "finisher", "An element descriptor"); this.disallowProperty(elementObject, "extras", "An element descriptor"); return element; }, this); }, toElementDescriptor: function toElementDescriptor(elementObject) { var kind = String(elementObject.kind); if (kind !== "method" && kind !== "field") { throw new TypeError('An element descriptor\'s .kind property must be either "method" or' + ' "field", but a decorator created an element descriptor with' + ' .kind "' + kind + '"'); } var key = hassio_supervisor_info_toPropertyKey(elementObject.key); var placement = String(elementObject.placement); if (placement !== "static" && placement !== "prototype" && placement !== "own") { throw new TypeError('An element descriptor\'s .placement property must be one of "static",' + ' "prototype" or "own", but a decorator created an element descriptor' + ' with .placement "' + placement + '"'); } var descriptor = elementObject.descriptor; this.disallowProperty(elementObject, "elements", "An element descriptor"); var element = { kind: kind, key: key, placement: placement, descriptor: Object.assign({}, descriptor) }; if (kind !== "field") { this.disallowProperty(elementObject, "initializer", "A method descriptor"); } else { this.disallowProperty(descriptor, "get", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "set", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "value", "The property descriptor of a field descriptor"); element.initializer = elementObject.initializer; } return element; }, toElementFinisherExtras: function toElementFinisherExtras(elementObject) { var element = this.toElementDescriptor(elementObject); var finisher = hassio_supervisor_info_optionalCallableProperty(elementObject, "finisher"); var extras = this.toElementDescriptors(elementObject.extras); return { element: element, finisher: finisher, extras: extras }; }, fromClassDescriptor: function fromClassDescriptor(elements) { var obj = { kind: "class", elements: elements.map(this.fromElementDescriptor, this) }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); return obj; }, toClassDescriptor: function toClassDescriptor(obj) { var kind = String(obj.kind); if (kind !== "class") { throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator' + ' created a class descriptor with .kind "' + kind + '"'); } this.disallowProperty(obj, "key", "A class descriptor"); this.disallowProperty(obj, "placement", "A class descriptor"); this.disallowProperty(obj, "descriptor", "A class descriptor"); this.disallowProperty(obj, "initializer", "A class descriptor"); this.disallowProperty(obj, "extras", "A class descriptor"); var finisher = hassio_supervisor_info_optionalCallableProperty(obj, "finisher"); var elements = this.toElementDescriptors(obj.elements); return { elements: elements, finisher: finisher }; }, runClassFinishers: function runClassFinishers(constructor, finishers) { for (var i = 0; i < finishers.length; i++) { var newConstructor = (0, finishers[i])(constructor); if (newConstructor !== undefined) { if (typeof newConstructor !== "function") { throw new TypeError("Finishers must return a constructor."); } constructor = newConstructor; } } return constructor; }, disallowProperty: function disallowProperty(obj, name, objectType) { if (obj[name] !== undefined) { throw new TypeError(objectType + " can't have a ." + name + " property."); } } }; return api; }

function hassio_supervisor_info_createElementDescriptor(def) { var key = hassio_supervisor_info_toPropertyKey(def.key); var descriptor; if (def.kind === "method") { descriptor = { value: def.value, writable: true, configurable: true, enumerable: false }; } else if (def.kind === "get") { descriptor = { get: def.value, configurable: true, enumerable: false }; } else if (def.kind === "set") { descriptor = { set: def.value, configurable: true, enumerable: false }; } else if (def.kind === "field") { descriptor = { configurable: true, writable: true, enumerable: true }; } var element = { kind: def.kind === "field" ? "field" : "method", key: key, placement: def["static"] ? "static" : def.kind === "field" ? "own" : "prototype", descriptor: descriptor }; if (def.decorators) element.decorators = def.decorators; if (def.kind === "field") element.initializer = def.value; return element; }

function hassio_supervisor_info_coalesceGetterSetter(element, other) { if (element.descriptor.get !== undefined) { other.descriptor.get = element.descriptor.get; } else { other.descriptor.set = element.descriptor.set; } }

function hassio_supervisor_info_coalesceClassElements(elements) { var newElements = []; var isSameElement = function isSameElement(other) { return other.kind === "method" && other.key === element.key && other.placement === element.placement; }; for (var i = 0; i < elements.length; i++) { var element = elements[i]; var other; if (element.kind === "method" && (other = newElements.find(isSameElement))) { if (hassio_supervisor_info_isDataDescriptor(element.descriptor) || hassio_supervisor_info_isDataDescriptor(other.descriptor)) { if (hassio_supervisor_info_hasDecorators(element) || hassio_supervisor_info_hasDecorators(other)) { throw new ReferenceError("Duplicated methods (" + element.key + ") can't be decorated."); } other.descriptor = element.descriptor; } else { if (hassio_supervisor_info_hasDecorators(element)) { if (hassio_supervisor_info_hasDecorators(other)) { throw new ReferenceError("Decorators can't be placed on different accessors with for " + "the same property (" + element.key + ")."); } other.decorators = element.decorators; } hassio_supervisor_info_coalesceGetterSetter(element, other); } } else { newElements.push(element); } } return newElements; }

function hassio_supervisor_info_hasDecorators(element) { return element.decorators && element.decorators.length; }

function hassio_supervisor_info_isDataDescriptor(desc) { return desc !== undefined && !(desc.value === undefined && desc.writable === undefined); }

function hassio_supervisor_info_optionalCallableProperty(obj, name) { var value = obj[name]; if (value !== undefined && typeof value !== "function") { throw new TypeError("Expected '" + name + "' to be a function"); } return value; }

function hassio_supervisor_info_toPropertyKey(arg) { var key = hassio_supervisor_info_toPrimitive(arg, "string"); return hassio_supervisor_info_typeof(key) === "symbol" ? key : String(key); }

function hassio_supervisor_info_toPrimitive(input, hint) { if (hassio_supervisor_info_typeof(input) !== "object" || input === null) return input; var prim = input[Symbol.toPrimitive]; if (prim !== undefined) { var res = prim.call(input, hint || "default"); if (hassio_supervisor_info_typeof(res) !== "object") return res; throw new TypeError("@@toPrimitive must return a primitive value."); } return (hint === "string" ? String : Number)(input); }

function hassio_supervisor_info_toArray(arr) { return hassio_supervisor_info_arrayWithHoles(arr) || hassio_supervisor_info_iterableToArray(arr) || hassio_supervisor_info_unsupportedIterableToArray(arr) || hassio_supervisor_info_nonIterableRest(); }

function hassio_supervisor_info_nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function hassio_supervisor_info_unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return hassio_supervisor_info_arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(n); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return hassio_supervisor_info_arrayLikeToArray(o, minLen); }

function hassio_supervisor_info_arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function hassio_supervisor_info_iterableToArray(iter) { if (typeof Symbol !== "undefined" && Symbol.iterator in Object(iter)) return Array.from(iter); }

function hassio_supervisor_info_arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }











var hassio_supervisor_info_HassioSupervisorInfo = hassio_supervisor_info_decorate([Object(lit_element["d" /* customElement */])("hassio-supervisor-info")], function (_initialize, _LitElement) {
  var HassioSupervisorInfo = /*#__PURE__*/function (_LitElement2) {
    hassio_supervisor_info_inherits(HassioSupervisorInfo, _LitElement2);

    var _super = hassio_supervisor_info_createSuper(HassioSupervisorInfo);

    function HassioSupervisorInfo() {
      var _this;

      hassio_supervisor_info_classCallCheck(this, HassioSupervisorInfo);

      for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
        args[_key] = arguments[_key];
      }

      _this = _super.call.apply(_super, [this].concat(args));

      _initialize(hassio_supervisor_info_assertThisInitialized(_this));

      return _this;
    }

    return HassioSupervisorInfo;
  }(_LitElement);

  return {
    F: HassioSupervisorInfo,
    d: [{
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "hass",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "supervisorInfo",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "_errors",
      value: void 0
    }, {
      kind: "method",
      key: "render",
      value: function render() {
        return Object(lit_element["e" /* html */])(hassio_supervisor_info_templateObject(), this.supervisorInfo.version, this.supervisorInfo.version_latest, this.supervisorInfo.channel !== "stable" ? Object(lit_element["e" /* html */])(hassio_supervisor_info_templateObject2(), this.supervisorInfo.channel) : "", this._errors ? Object(lit_element["e" /* html */])(hassio_supervisor_info_templateObject3(), this._errors) : "", this.hass, this.supervisorInfo.version !== this.supervisorInfo.version_latest ? Object(lit_element["e" /* html */])(hassio_supervisor_info_templateObject4(), this.hass) : "", this.supervisorInfo.channel === "beta" ? Object(lit_element["e" /* html */])(hassio_supervisor_info_templateObject5(), this.hass, {
          channel: "stable"
        }) : "", this.supervisorInfo.channel === "stable" ? Object(lit_element["e" /* html */])(hassio_supervisor_info_templateObject6(), this._joinBeta) : "");
      }
    }, {
      kind: "get",
      "static": true,
      key: "styles",
      value: function styles() {
        return [resources_styles["b" /* haStyle */], hassio_style["a" /* hassioStyle */], Object(lit_element["c" /* css */])(hassio_supervisor_info_templateObject7())];
      }
    }, {
      kind: "method",
      key: "firstUpdated",
      value: function firstUpdated() {
        var _this2 = this;

        this.addEventListener("hass-api-called", function (ev) {
          return _this2._apiCalled(ev);
        });
      }
    }, {
      kind: "method",
      key: "_apiCalled",
      value: function _apiCalled(ev) {
        if (ev.detail.success) {
          this._errors = undefined;
          return;
        }

        var response = ev.detail.response;
        this._errors = hassio_supervisor_info_typeof(response.body) === "object" ? response.body.message || "Unknown error" : response.body;
      }
    }, {
      kind: "method",
      key: "_joinBeta",
      value: function () {
        var _joinBeta2 = hassio_supervisor_info_asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee() {
          var confirmed, data, eventdata, _err$body;

          return regeneratorRuntime.wrap(function _callee$(_context) {
            while (1) {
              switch (_context.prev = _context.next) {
                case 0:
                  _context.next = 2;
                  return Object(show_dialog_box["b" /* showConfirmationDialog */])(this, {
                    title: "WARNING",
                    text: Object(lit_element["e" /* html */])(hassio_supervisor_info_templateObject8()),
                    confirmText: "join beta",
                    dismissText: "no"
                  });

                case 2:
                  confirmed = _context.sent;

                  if (confirmed) {
                    _context.next = 5;
                    break;
                  }

                  return _context.abrupt("return");

                case 5:
                  _context.prev = 5;
                  data = {
                    channel: "beta"
                  };
                  _context.next = 9;
                  return Object(supervisor["e" /* setSupervisorOption */])(this.hass, data);

                case 9:
                  eventdata = {
                    success: true,
                    response: undefined,
                    path: "option"
                  };
                  Object(fire_event["a" /* fireEvent */])(this, "hass-api-called", eventdata);
                  _context.next = 16;
                  break;

                case 13:
                  _context.prev = 13;
                  _context.t0 = _context["catch"](5);
                  this._errors = "Error joining beta channel, ".concat(((_err$body = _context.t0.body) === null || _err$body === void 0 ? void 0 : _err$body.message) || _context.t0);

                case 16:
                case "end":
                  return _context.stop();
              }
            }
          }, _callee, this, [[5, 13]]);
        }));

        function _joinBeta() {
          return _joinBeta2.apply(this, arguments);
        }

        return _joinBeta;
      }()
    }]
  };
}, lit_element["a" /* LitElement */]);
// EXTERNAL MODULE: ./node_modules/@polymer/paper-dropdown-menu/paper-dropdown-menu.js + 3 modules
var paper_dropdown_menu = __webpack_require__(136);

// EXTERNAL MODULE: ./node_modules/@polymer/paper-item/paper-item.js + 2 modules
var paper_item = __webpack_require__(100);

// EXTERNAL MODULE: ./node_modules/@polymer/paper-listbox/paper-listbox.js
var paper_listbox = __webpack_require__(129);

// EXTERNAL MODULE: ./hassio/src/components/hassio-ansi-to-html.ts
var hassio_ansi_to_html = __webpack_require__(130);

// CONCATENATED MODULE: ./hassio/src/system/hassio-supervisor-log.ts
function hassio_supervisor_log_typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { hassio_supervisor_log_typeof = function _typeof(obj) { return typeof obj; }; } else { hassio_supervisor_log_typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return hassio_supervisor_log_typeof(obj); }

function hassio_supervisor_log_templateObject7() {
  var data = hassio_supervisor_log_taggedTemplateLiteral(["\n        paper-card {\n          width: 100%;\n        }\n        pre {\n          white-space: pre-wrap;\n        }\n        paper-dropdown-menu {\n          padding: 0 2%;\n          width: 96%;\n        }\n        .errors {\n          color: var(--google-red-500);\n          margin-bottom: 16px;\n        }\n        .card-content {\n          padding-top: 0px;\n        }\n      "]);

  hassio_supervisor_log_templateObject7 = function _templateObject7() {
    return data;
  };

  return data;
}

function hassio_supervisor_log_templateObject6() {
  var data = hassio_supervisor_log_taggedTemplateLiteral(["<loading-screen></loading-screen>"]);

  hassio_supervisor_log_templateObject6 = function _templateObject6() {
    return data;
  };

  return data;
}

function hassio_supervisor_log_templateObject5() {
  var data = hassio_supervisor_log_taggedTemplateLiteral(["<hassio-ansi-to-html\n                .content=", "\n              ></hassio-ansi-to-html>"]);

  hassio_supervisor_log_templateObject5 = function _templateObject5() {
    return data;
  };

  return data;
}

function hassio_supervisor_log_templateObject4() {
  var data = hassio_supervisor_log_taggedTemplateLiteral(["\n                      <paper-item provider=", "\n                        >", "</paper-item\n                      >\n                    "]);

  hassio_supervisor_log_templateObject4 = function _templateObject4() {
    return data;
  };

  return data;
}

function hassio_supervisor_log_templateObject3() {
  var data = hassio_supervisor_log_taggedTemplateLiteral(["\n              <paper-dropdown-menu\n                label=\"Log provider\"\n                @iron-select=", "\n              >\n                <paper-listbox\n                  slot=\"dropdown-content\"\n                  attr-for-selected=\"provider\"\n                  .selected=", "\n                >\n                  ", "\n                </paper-listbox>\n              </paper-dropdown-menu>\n            "]);

  hassio_supervisor_log_templateObject3 = function _templateObject3() {
    return data;
  };

  return data;
}

function hassio_supervisor_log_templateObject2() {
  var data = hassio_supervisor_log_taggedTemplateLiteral([" <div class=\"errors\">", "</div> "]);

  hassio_supervisor_log_templateObject2 = function _templateObject2() {
    return data;
  };

  return data;
}

function hassio_supervisor_log_templateObject() {
  var data = hassio_supervisor_log_taggedTemplateLiteral(["\n      <paper-card>\n        ", "\n        ", "\n\n        <div class=\"card-content\" id=\"content\">\n          ", "\n        </div>\n        <div class=\"card-actions\">\n          <mwc-button @click=", ">Refresh</mwc-button>\n        </div>\n      </paper-card>\n    "]);

  hassio_supervisor_log_templateObject = function _templateObject() {
    return data;
  };

  return data;
}

function hassio_supervisor_log_taggedTemplateLiteral(strings, raw) { if (!raw) { raw = strings.slice(0); } return Object.freeze(Object.defineProperties(strings, { raw: { value: Object.freeze(raw) } })); }

function hassio_supervisor_log_asyncGeneratorStep(gen, resolve, reject, _next, _throw, key, arg) { try { var info = gen[key](arg); var value = info.value; } catch (error) { reject(error); return; } if (info.done) { resolve(value); } else { Promise.resolve(value).then(_next, _throw); } }

function hassio_supervisor_log_asyncToGenerator(fn) { return function () { var self = this, args = arguments; return new Promise(function (resolve, reject) { var gen = fn.apply(self, args); function _next(value) { hassio_supervisor_log_asyncGeneratorStep(gen, resolve, reject, _next, _throw, "next", value); } function _throw(err) { hassio_supervisor_log_asyncGeneratorStep(gen, resolve, reject, _next, _throw, "throw", err); } _next(undefined); }); }; }

function hassio_supervisor_log_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function hassio_supervisor_log_inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) hassio_supervisor_log_setPrototypeOf(subClass, superClass); }

function hassio_supervisor_log_setPrototypeOf(o, p) { hassio_supervisor_log_setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return hassio_supervisor_log_setPrototypeOf(o, p); }

function hassio_supervisor_log_createSuper(Derived) { return function () { var Super = hassio_supervisor_log_getPrototypeOf(Derived), result; if (hassio_supervisor_log_isNativeReflectConstruct()) { var NewTarget = hassio_supervisor_log_getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return hassio_supervisor_log_possibleConstructorReturn(this, result); }; }

function hassio_supervisor_log_possibleConstructorReturn(self, call) { if (call && (hassio_supervisor_log_typeof(call) === "object" || typeof call === "function")) { return call; } return hassio_supervisor_log_assertThisInitialized(self); }

function hassio_supervisor_log_assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function hassio_supervisor_log_isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Date.prototype.toString.call(Reflect.construct(Date, [], function () {})); return true; } catch (e) { return false; } }

function hassio_supervisor_log_decorate(decorators, factory, superClass, mixins) { var api = hassio_supervisor_log_getDecoratorsApi(); if (mixins) { for (var i = 0; i < mixins.length; i++) { api = mixins[i](api); } } var r = factory(function initialize(O) { api.initializeInstanceElements(O, decorated.elements); }, superClass); var decorated = api.decorateClass(hassio_supervisor_log_coalesceClassElements(r.d.map(hassio_supervisor_log_createElementDescriptor)), decorators); api.initializeClassElements(r.F, decorated.elements); return api.runClassFinishers(r.F, decorated.finishers); }

function hassio_supervisor_log_getDecoratorsApi() { hassio_supervisor_log_getDecoratorsApi = function _getDecoratorsApi() { return api; }; var api = { elementsDefinitionOrder: [["method"], ["field"]], initializeInstanceElements: function initializeInstanceElements(O, elements) { ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { if (element.kind === kind && element.placement === "own") { this.defineClassElement(O, element); } }, this); }, this); }, initializeClassElements: function initializeClassElements(F, elements) { var proto = F.prototype; ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { var placement = element.placement; if (element.kind === kind && (placement === "static" || placement === "prototype")) { var receiver = placement === "static" ? F : proto; this.defineClassElement(receiver, element); } }, this); }, this); }, defineClassElement: function defineClassElement(receiver, element) { var descriptor = element.descriptor; if (element.kind === "field") { var initializer = element.initializer; descriptor = { enumerable: descriptor.enumerable, writable: descriptor.writable, configurable: descriptor.configurable, value: initializer === void 0 ? void 0 : initializer.call(receiver) }; } Object.defineProperty(receiver, element.key, descriptor); }, decorateClass: function decorateClass(elements, decorators) { var newElements = []; var finishers = []; var placements = { "static": [], prototype: [], own: [] }; elements.forEach(function (element) { this.addElementPlacement(element, placements); }, this); elements.forEach(function (element) { if (!hassio_supervisor_log_hasDecorators(element)) return newElements.push(element); var elementFinishersExtras = this.decorateElement(element, placements); newElements.push(elementFinishersExtras.element); newElements.push.apply(newElements, elementFinishersExtras.extras); finishers.push.apply(finishers, elementFinishersExtras.finishers); }, this); if (!decorators) { return { elements: newElements, finishers: finishers }; } var result = this.decorateConstructor(newElements, decorators); finishers.push.apply(finishers, result.finishers); result.finishers = finishers; return result; }, addElementPlacement: function addElementPlacement(element, placements, silent) { var keys = placements[element.placement]; if (!silent && keys.indexOf(element.key) !== -1) { throw new TypeError("Duplicated element (" + element.key + ")"); } keys.push(element.key); }, decorateElement: function decorateElement(element, placements) { var extras = []; var finishers = []; for (var decorators = element.decorators, i = decorators.length - 1; i >= 0; i--) { var keys = placements[element.placement]; keys.splice(keys.indexOf(element.key), 1); var elementObject = this.fromElementDescriptor(element); var elementFinisherExtras = this.toElementFinisherExtras((0, decorators[i])(elementObject) || elementObject); element = elementFinisherExtras.element; this.addElementPlacement(element, placements); if (elementFinisherExtras.finisher) { finishers.push(elementFinisherExtras.finisher); } var newExtras = elementFinisherExtras.extras; if (newExtras) { for (var j = 0; j < newExtras.length; j++) { this.addElementPlacement(newExtras[j], placements); } extras.push.apply(extras, newExtras); } } return { element: element, finishers: finishers, extras: extras }; }, decorateConstructor: function decorateConstructor(elements, decorators) { var finishers = []; for (var i = decorators.length - 1; i >= 0; i--) { var obj = this.fromClassDescriptor(elements); var elementsAndFinisher = this.toClassDescriptor((0, decorators[i])(obj) || obj); if (elementsAndFinisher.finisher !== undefined) { finishers.push(elementsAndFinisher.finisher); } if (elementsAndFinisher.elements !== undefined) { elements = elementsAndFinisher.elements; for (var j = 0; j < elements.length - 1; j++) { for (var k = j + 1; k < elements.length; k++) { if (elements[j].key === elements[k].key && elements[j].placement === elements[k].placement) { throw new TypeError("Duplicated element (" + elements[j].key + ")"); } } } } } return { elements: elements, finishers: finishers }; }, fromElementDescriptor: function fromElementDescriptor(element) { var obj = { kind: element.kind, key: element.key, placement: element.placement, descriptor: element.descriptor }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); if (element.kind === "field") obj.initializer = element.initializer; return obj; }, toElementDescriptors: function toElementDescriptors(elementObjects) { if (elementObjects === undefined) return; return hassio_supervisor_log_toArray(elementObjects).map(function (elementObject) { var element = this.toElementDescriptor(elementObject); this.disallowProperty(elementObject, "finisher", "An element descriptor"); this.disallowProperty(elementObject, "extras", "An element descriptor"); return element; }, this); }, toElementDescriptor: function toElementDescriptor(elementObject) { var kind = String(elementObject.kind); if (kind !== "method" && kind !== "field") { throw new TypeError('An element descriptor\'s .kind property must be either "method" or' + ' "field", but a decorator created an element descriptor with' + ' .kind "' + kind + '"'); } var key = hassio_supervisor_log_toPropertyKey(elementObject.key); var placement = String(elementObject.placement); if (placement !== "static" && placement !== "prototype" && placement !== "own") { throw new TypeError('An element descriptor\'s .placement property must be one of "static",' + ' "prototype" or "own", but a decorator created an element descriptor' + ' with .placement "' + placement + '"'); } var descriptor = elementObject.descriptor; this.disallowProperty(elementObject, "elements", "An element descriptor"); var element = { kind: kind, key: key, placement: placement, descriptor: Object.assign({}, descriptor) }; if (kind !== "field") { this.disallowProperty(elementObject, "initializer", "A method descriptor"); } else { this.disallowProperty(descriptor, "get", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "set", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "value", "The property descriptor of a field descriptor"); element.initializer = elementObject.initializer; } return element; }, toElementFinisherExtras: function toElementFinisherExtras(elementObject) { var element = this.toElementDescriptor(elementObject); var finisher = hassio_supervisor_log_optionalCallableProperty(elementObject, "finisher"); var extras = this.toElementDescriptors(elementObject.extras); return { element: element, finisher: finisher, extras: extras }; }, fromClassDescriptor: function fromClassDescriptor(elements) { var obj = { kind: "class", elements: elements.map(this.fromElementDescriptor, this) }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); return obj; }, toClassDescriptor: function toClassDescriptor(obj) { var kind = String(obj.kind); if (kind !== "class") { throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator' + ' created a class descriptor with .kind "' + kind + '"'); } this.disallowProperty(obj, "key", "A class descriptor"); this.disallowProperty(obj, "placement", "A class descriptor"); this.disallowProperty(obj, "descriptor", "A class descriptor"); this.disallowProperty(obj, "initializer", "A class descriptor"); this.disallowProperty(obj, "extras", "A class descriptor"); var finisher = hassio_supervisor_log_optionalCallableProperty(obj, "finisher"); var elements = this.toElementDescriptors(obj.elements); return { elements: elements, finisher: finisher }; }, runClassFinishers: function runClassFinishers(constructor, finishers) { for (var i = 0; i < finishers.length; i++) { var newConstructor = (0, finishers[i])(constructor); if (newConstructor !== undefined) { if (typeof newConstructor !== "function") { throw new TypeError("Finishers must return a constructor."); } constructor = newConstructor; } } return constructor; }, disallowProperty: function disallowProperty(obj, name, objectType) { if (obj[name] !== undefined) { throw new TypeError(objectType + " can't have a ." + name + " property."); } } }; return api; }

function hassio_supervisor_log_createElementDescriptor(def) { var key = hassio_supervisor_log_toPropertyKey(def.key); var descriptor; if (def.kind === "method") { descriptor = { value: def.value, writable: true, configurable: true, enumerable: false }; } else if (def.kind === "get") { descriptor = { get: def.value, configurable: true, enumerable: false }; } else if (def.kind === "set") { descriptor = { set: def.value, configurable: true, enumerable: false }; } else if (def.kind === "field") { descriptor = { configurable: true, writable: true, enumerable: true }; } var element = { kind: def.kind === "field" ? "field" : "method", key: key, placement: def["static"] ? "static" : def.kind === "field" ? "own" : "prototype", descriptor: descriptor }; if (def.decorators) element.decorators = def.decorators; if (def.kind === "field") element.initializer = def.value; return element; }

function hassio_supervisor_log_coalesceGetterSetter(element, other) { if (element.descriptor.get !== undefined) { other.descriptor.get = element.descriptor.get; } else { other.descriptor.set = element.descriptor.set; } }

function hassio_supervisor_log_coalesceClassElements(elements) { var newElements = []; var isSameElement = function isSameElement(other) { return other.kind === "method" && other.key === element.key && other.placement === element.placement; }; for (var i = 0; i < elements.length; i++) { var element = elements[i]; var other; if (element.kind === "method" && (other = newElements.find(isSameElement))) { if (hassio_supervisor_log_isDataDescriptor(element.descriptor) || hassio_supervisor_log_isDataDescriptor(other.descriptor)) { if (hassio_supervisor_log_hasDecorators(element) || hassio_supervisor_log_hasDecorators(other)) { throw new ReferenceError("Duplicated methods (" + element.key + ") can't be decorated."); } other.descriptor = element.descriptor; } else { if (hassio_supervisor_log_hasDecorators(element)) { if (hassio_supervisor_log_hasDecorators(other)) { throw new ReferenceError("Decorators can't be placed on different accessors with for " + "the same property (" + element.key + ")."); } other.decorators = element.decorators; } hassio_supervisor_log_coalesceGetterSetter(element, other); } } else { newElements.push(element); } } return newElements; }

function hassio_supervisor_log_hasDecorators(element) { return element.decorators && element.decorators.length; }

function hassio_supervisor_log_isDataDescriptor(desc) { return desc !== undefined && !(desc.value === undefined && desc.writable === undefined); }

function hassio_supervisor_log_optionalCallableProperty(obj, name) { var value = obj[name]; if (value !== undefined && typeof value !== "function") { throw new TypeError("Expected '" + name + "' to be a function"); } return value; }

function hassio_supervisor_log_toPropertyKey(arg) { var key = hassio_supervisor_log_toPrimitive(arg, "string"); return hassio_supervisor_log_typeof(key) === "symbol" ? key : String(key); }

function hassio_supervisor_log_toPrimitive(input, hint) { if (hassio_supervisor_log_typeof(input) !== "object" || input === null) return input; var prim = input[Symbol.toPrimitive]; if (prim !== undefined) { var res = prim.call(input, hint || "default"); if (hassio_supervisor_log_typeof(res) !== "object") return res; throw new TypeError("@@toPrimitive must return a primitive value."); } return (hint === "string" ? String : Number)(input); }

function hassio_supervisor_log_toArray(arr) { return hassio_supervisor_log_arrayWithHoles(arr) || hassio_supervisor_log_iterableToArray(arr) || hassio_supervisor_log_unsupportedIterableToArray(arr) || hassio_supervisor_log_nonIterableRest(); }

function hassio_supervisor_log_nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function hassio_supervisor_log_unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return hassio_supervisor_log_arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(n); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return hassio_supervisor_log_arrayLikeToArray(o, minLen); }

function hassio_supervisor_log_arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function hassio_supervisor_log_iterableToArray(iter) { if (typeof Symbol !== "undefined" && Symbol.iterator in Object(iter)) return Array.from(iter); }

function hassio_supervisor_log_arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }

function hassio_supervisor_log_get(target, property, receiver) { if (typeof Reflect !== "undefined" && Reflect.get) { hassio_supervisor_log_get = Reflect.get; } else { hassio_supervisor_log_get = function _get(target, property, receiver) { var base = hassio_supervisor_log_superPropBase(target, property); if (!base) return; var desc = Object.getOwnPropertyDescriptor(base, property); if (desc.get) { return desc.get.call(receiver); } return desc.value; }; } return hassio_supervisor_log_get(target, property, receiver || target); }

function hassio_supervisor_log_superPropBase(object, property) { while (!Object.prototype.hasOwnProperty.call(object, property)) { object = hassio_supervisor_log_getPrototypeOf(object); if (object === null) break; } return object; }

function hassio_supervisor_log_getPrototypeOf(o) { hassio_supervisor_log_getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return hassio_supervisor_log_getPrototypeOf(o); }












var logProviders = [{
  key: "supervisor",
  name: "Supervisor"
}, {
  key: "core",
  name: "Core"
}, {
  key: "host",
  name: "Host"
}, {
  key: "dns",
  name: "DNS"
}, {
  key: "audio",
  name: "Audio"
}, {
  key: "multicast",
  name: "Multicast"
}];

var hassio_supervisor_log_HassioSupervisorLog = hassio_supervisor_log_decorate([Object(lit_element["d" /* customElement */])("hassio-supervisor-log")], function (_initialize, _LitElement) {
  var HassioSupervisorLog = /*#__PURE__*/function (_LitElement2) {
    hassio_supervisor_log_inherits(HassioSupervisorLog, _LitElement2);

    var _super = hassio_supervisor_log_createSuper(HassioSupervisorLog);

    function HassioSupervisorLog() {
      var _this;

      hassio_supervisor_log_classCallCheck(this, HassioSupervisorLog);

      for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
        args[_key] = arguments[_key];
      }

      _this = _super.call.apply(_super, [this].concat(args));

      _initialize(hassio_supervisor_log_assertThisInitialized(_this));

      return _this;
    }

    return HassioSupervisorLog;
  }(_LitElement);

  return {
    F: HassioSupervisorLog,
    d: [{
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])({
        attribute: false
      })],
      key: "hass",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "_error",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "_selectedLogProvider",
      value: function value() {
        return "supervisor";
      }
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "_content",
      value: void 0
    }, {
      kind: "method",
      key: "connectedCallback",
      value: function () {
        var _connectedCallback = hassio_supervisor_log_asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee() {
          return regeneratorRuntime.wrap(function _callee$(_context) {
            while (1) {
              switch (_context.prev = _context.next) {
                case 0:
                  hassio_supervisor_log_get(hassio_supervisor_log_getPrototypeOf(HassioSupervisorLog.prototype), "connectedCallback", this).call(this);

                  _context.next = 3;
                  return this._loadData();

                case 3:
                case "end":
                  return _context.stop();
              }
            }
          }, _callee, this);
        }));

        function connectedCallback() {
          return _connectedCallback.apply(this, arguments);
        }

        return connectedCallback;
      }()
    }, {
      kind: "method",
      key: "render",
      value: function render() {
        var _this$hass$userData;

        return Object(lit_element["e" /* html */])(hassio_supervisor_log_templateObject(), this._error ? Object(lit_element["e" /* html */])(hassio_supervisor_log_templateObject2(), this._error) : "", ((_this$hass$userData = this.hass.userData) === null || _this$hass$userData === void 0 ? void 0 : _this$hass$userData.showAdvanced) ? Object(lit_element["e" /* html */])(hassio_supervisor_log_templateObject3(), this._setLogProvider, this._selectedLogProvider, logProviders.map(function (provider) {
          return Object(lit_element["e" /* html */])(hassio_supervisor_log_templateObject4(), provider.key, provider.name);
        })) : "", this._content ? Object(lit_element["e" /* html */])(hassio_supervisor_log_templateObject5(), this._content) : Object(lit_element["e" /* html */])(hassio_supervisor_log_templateObject6()), this._refresh);
      }
    }, {
      kind: "get",
      "static": true,
      key: "styles",
      value: function styles() {
        return [resources_styles["b" /* haStyle */], hassio_style["a" /* hassioStyle */], Object(lit_element["c" /* css */])(hassio_supervisor_log_templateObject7())];
      }
    }, {
      kind: "method",
      key: "_setLogProvider",
      value: function () {
        var _setLogProvider2 = hassio_supervisor_log_asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee2(ev) {
          var provider;
          return regeneratorRuntime.wrap(function _callee2$(_context2) {
            while (1) {
              switch (_context2.prev = _context2.next) {
                case 0:
                  provider = ev.detail.item.getAttribute("provider");
                  this._selectedLogProvider = provider;
                  _context2.next = 4;
                  return this._loadData();

                case 4:
                case "end":
                  return _context2.stop();
              }
            }
          }, _callee2, this);
        }));

        function _setLogProvider(_x) {
          return _setLogProvider2.apply(this, arguments);
        }

        return _setLogProvider;
      }()
    }, {
      kind: "method",
      key: "_loadData",
      value: function () {
        var _loadData2 = hassio_supervisor_log_asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee3() {
          var _err$body;

          return regeneratorRuntime.wrap(function _callee3$(_context3) {
            while (1) {
              switch (_context3.prev = _context3.next) {
                case 0:
                  this._error = undefined;
                  this._content = undefined;
                  _context3.prev = 2;
                  _context3.next = 5;
                  return Object(supervisor["c" /* fetchHassioLogs */])(this.hass, this._selectedLogProvider);

                case 5:
                  this._content = _context3.sent;
                  _context3.next = 11;
                  break;

                case 8:
                  _context3.prev = 8;
                  _context3.t0 = _context3["catch"](2);
                  this._error = "Failed to get supervisor logs, ".concat(((_err$body = _context3.t0.body) === null || _err$body === void 0 ? void 0 : _err$body.message) || _context3.t0);

                case 11:
                case "end":
                  return _context3.stop();
              }
            }
          }, _callee3, this, [[2, 8]]);
        }));

        function _loadData() {
          return _loadData2.apply(this, arguments);
        }

        return _loadData;
      }()
    }, {
      kind: "method",
      key: "_refresh",
      value: function () {
        var _refresh2 = hassio_supervisor_log_asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee4() {
          return regeneratorRuntime.wrap(function _callee4$(_context4) {
            while (1) {
              switch (_context4.prev = _context4.next) {
                case 0:
                  _context4.next = 2;
                  return this._loadData();

                case 2:
                case "end":
                  return _context4.stop();
              }
            }
          }, _callee4, this);
        }));

        function _refresh() {
          return _refresh2.apply(this, arguments);
        }

        return _refresh;
      }()
    }]
  };
}, lit_element["a" /* LitElement */]);
// CONCATENATED MODULE: ./hassio/src/system/hassio-system.ts
function hassio_system_typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { hassio_system_typeof = function _typeof(obj) { return typeof obj; }; } else { hassio_system_typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return hassio_system_typeof(obj); }

function hassio_system_templateObject2() {
  var data = hassio_system_taggedTemplateLiteral(["\n        .content {\n          margin: 8px;\n          color: var(--primary-text-color);\n        }\n        .title {\n          margin-top: 24px;\n          color: var(--primary-text-color);\n          font-size: 2em;\n          padding-left: 8px;\n          margin-bottom: 8px;\n        }\n        hassio-supervisor-log {\n          width: 100%;\n        }\n      "]);

  hassio_system_templateObject2 = function _templateObject2() {
    return data;
  };

  return data;
}

function hassio_system_templateObject() {
  var data = hassio_system_taggedTemplateLiteral(["\n      <hass-tabs-subpage\n        .hass=", "\n        .narrow=", "\n        hassio\n        main-page\n        .route=", "\n        .tabs=", "\n      >\n        <span slot=\"header\">System</span>\n        <div class=\"content\">\n          <h1>Information</h1>\n          <div class=\"card-group\">\n            <hassio-supervisor-info\n              .hass=", "\n              .supervisorInfo=", "\n            ></hassio-supervisor-info>\n            <hassio-host-info\n              .hass=", "\n              .hostInfo=", "\n              .hassOsInfo=", "\n            ></hassio-host-info>\n          </div>\n          <h1>System log</h1>\n          <hassio-supervisor-log .hass=", "></hassio-supervisor-log>\n        </div>\n      </hass-tabs-subpage>\n    "]);

  hassio_system_templateObject = function _templateObject() {
    return data;
  };

  return data;
}

function hassio_system_taggedTemplateLiteral(strings, raw) { if (!raw) { raw = strings.slice(0); } return Object.freeze(Object.defineProperties(strings, { raw: { value: Object.freeze(raw) } })); }

function hassio_system_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function hassio_system_inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) hassio_system_setPrototypeOf(subClass, superClass); }

function hassio_system_setPrototypeOf(o, p) { hassio_system_setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return hassio_system_setPrototypeOf(o, p); }

function hassio_system_createSuper(Derived) { return function () { var Super = hassio_system_getPrototypeOf(Derived), result; if (hassio_system_isNativeReflectConstruct()) { var NewTarget = hassio_system_getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return hassio_system_possibleConstructorReturn(this, result); }; }

function hassio_system_possibleConstructorReturn(self, call) { if (call && (hassio_system_typeof(call) === "object" || typeof call === "function")) { return call; } return hassio_system_assertThisInitialized(self); }

function hassio_system_assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function hassio_system_isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Date.prototype.toString.call(Reflect.construct(Date, [], function () {})); return true; } catch (e) { return false; } }

function hassio_system_getPrototypeOf(o) { hassio_system_getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return hassio_system_getPrototypeOf(o); }

function hassio_system_decorate(decorators, factory, superClass, mixins) { var api = hassio_system_getDecoratorsApi(); if (mixins) { for (var i = 0; i < mixins.length; i++) { api = mixins[i](api); } } var r = factory(function initialize(O) { api.initializeInstanceElements(O, decorated.elements); }, superClass); var decorated = api.decorateClass(hassio_system_coalesceClassElements(r.d.map(hassio_system_createElementDescriptor)), decorators); api.initializeClassElements(r.F, decorated.elements); return api.runClassFinishers(r.F, decorated.finishers); }

function hassio_system_getDecoratorsApi() { hassio_system_getDecoratorsApi = function _getDecoratorsApi() { return api; }; var api = { elementsDefinitionOrder: [["method"], ["field"]], initializeInstanceElements: function initializeInstanceElements(O, elements) { ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { if (element.kind === kind && element.placement === "own") { this.defineClassElement(O, element); } }, this); }, this); }, initializeClassElements: function initializeClassElements(F, elements) { var proto = F.prototype; ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { var placement = element.placement; if (element.kind === kind && (placement === "static" || placement === "prototype")) { var receiver = placement === "static" ? F : proto; this.defineClassElement(receiver, element); } }, this); }, this); }, defineClassElement: function defineClassElement(receiver, element) { var descriptor = element.descriptor; if (element.kind === "field") { var initializer = element.initializer; descriptor = { enumerable: descriptor.enumerable, writable: descriptor.writable, configurable: descriptor.configurable, value: initializer === void 0 ? void 0 : initializer.call(receiver) }; } Object.defineProperty(receiver, element.key, descriptor); }, decorateClass: function decorateClass(elements, decorators) { var newElements = []; var finishers = []; var placements = { "static": [], prototype: [], own: [] }; elements.forEach(function (element) { this.addElementPlacement(element, placements); }, this); elements.forEach(function (element) { if (!hassio_system_hasDecorators(element)) return newElements.push(element); var elementFinishersExtras = this.decorateElement(element, placements); newElements.push(elementFinishersExtras.element); newElements.push.apply(newElements, elementFinishersExtras.extras); finishers.push.apply(finishers, elementFinishersExtras.finishers); }, this); if (!decorators) { return { elements: newElements, finishers: finishers }; } var result = this.decorateConstructor(newElements, decorators); finishers.push.apply(finishers, result.finishers); result.finishers = finishers; return result; }, addElementPlacement: function addElementPlacement(element, placements, silent) { var keys = placements[element.placement]; if (!silent && keys.indexOf(element.key) !== -1) { throw new TypeError("Duplicated element (" + element.key + ")"); } keys.push(element.key); }, decorateElement: function decorateElement(element, placements) { var extras = []; var finishers = []; for (var decorators = element.decorators, i = decorators.length - 1; i >= 0; i--) { var keys = placements[element.placement]; keys.splice(keys.indexOf(element.key), 1); var elementObject = this.fromElementDescriptor(element); var elementFinisherExtras = this.toElementFinisherExtras((0, decorators[i])(elementObject) || elementObject); element = elementFinisherExtras.element; this.addElementPlacement(element, placements); if (elementFinisherExtras.finisher) { finishers.push(elementFinisherExtras.finisher); } var newExtras = elementFinisherExtras.extras; if (newExtras) { for (var j = 0; j < newExtras.length; j++) { this.addElementPlacement(newExtras[j], placements); } extras.push.apply(extras, newExtras); } } return { element: element, finishers: finishers, extras: extras }; }, decorateConstructor: function decorateConstructor(elements, decorators) { var finishers = []; for (var i = decorators.length - 1; i >= 0; i--) { var obj = this.fromClassDescriptor(elements); var elementsAndFinisher = this.toClassDescriptor((0, decorators[i])(obj) || obj); if (elementsAndFinisher.finisher !== undefined) { finishers.push(elementsAndFinisher.finisher); } if (elementsAndFinisher.elements !== undefined) { elements = elementsAndFinisher.elements; for (var j = 0; j < elements.length - 1; j++) { for (var k = j + 1; k < elements.length; k++) { if (elements[j].key === elements[k].key && elements[j].placement === elements[k].placement) { throw new TypeError("Duplicated element (" + elements[j].key + ")"); } } } } } return { elements: elements, finishers: finishers }; }, fromElementDescriptor: function fromElementDescriptor(element) { var obj = { kind: element.kind, key: element.key, placement: element.placement, descriptor: element.descriptor }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); if (element.kind === "field") obj.initializer = element.initializer; return obj; }, toElementDescriptors: function toElementDescriptors(elementObjects) { if (elementObjects === undefined) return; return hassio_system_toArray(elementObjects).map(function (elementObject) { var element = this.toElementDescriptor(elementObject); this.disallowProperty(elementObject, "finisher", "An element descriptor"); this.disallowProperty(elementObject, "extras", "An element descriptor"); return element; }, this); }, toElementDescriptor: function toElementDescriptor(elementObject) { var kind = String(elementObject.kind); if (kind !== "method" && kind !== "field") { throw new TypeError('An element descriptor\'s .kind property must be either "method" or' + ' "field", but a decorator created an element descriptor with' + ' .kind "' + kind + '"'); } var key = hassio_system_toPropertyKey(elementObject.key); var placement = String(elementObject.placement); if (placement !== "static" && placement !== "prototype" && placement !== "own") { throw new TypeError('An element descriptor\'s .placement property must be one of "static",' + ' "prototype" or "own", but a decorator created an element descriptor' + ' with .placement "' + placement + '"'); } var descriptor = elementObject.descriptor; this.disallowProperty(elementObject, "elements", "An element descriptor"); var element = { kind: kind, key: key, placement: placement, descriptor: Object.assign({}, descriptor) }; if (kind !== "field") { this.disallowProperty(elementObject, "initializer", "A method descriptor"); } else { this.disallowProperty(descriptor, "get", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "set", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "value", "The property descriptor of a field descriptor"); element.initializer = elementObject.initializer; } return element; }, toElementFinisherExtras: function toElementFinisherExtras(elementObject) { var element = this.toElementDescriptor(elementObject); var finisher = hassio_system_optionalCallableProperty(elementObject, "finisher"); var extras = this.toElementDescriptors(elementObject.extras); return { element: element, finisher: finisher, extras: extras }; }, fromClassDescriptor: function fromClassDescriptor(elements) { var obj = { kind: "class", elements: elements.map(this.fromElementDescriptor, this) }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); return obj; }, toClassDescriptor: function toClassDescriptor(obj) { var kind = String(obj.kind); if (kind !== "class") { throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator' + ' created a class descriptor with .kind "' + kind + '"'); } this.disallowProperty(obj, "key", "A class descriptor"); this.disallowProperty(obj, "placement", "A class descriptor"); this.disallowProperty(obj, "descriptor", "A class descriptor"); this.disallowProperty(obj, "initializer", "A class descriptor"); this.disallowProperty(obj, "extras", "A class descriptor"); var finisher = hassio_system_optionalCallableProperty(obj, "finisher"); var elements = this.toElementDescriptors(obj.elements); return { elements: elements, finisher: finisher }; }, runClassFinishers: function runClassFinishers(constructor, finishers) { for (var i = 0; i < finishers.length; i++) { var newConstructor = (0, finishers[i])(constructor); if (newConstructor !== undefined) { if (typeof newConstructor !== "function") { throw new TypeError("Finishers must return a constructor."); } constructor = newConstructor; } } return constructor; }, disallowProperty: function disallowProperty(obj, name, objectType) { if (obj[name] !== undefined) { throw new TypeError(objectType + " can't have a ." + name + " property."); } } }; return api; }

function hassio_system_createElementDescriptor(def) { var key = hassio_system_toPropertyKey(def.key); var descriptor; if (def.kind === "method") { descriptor = { value: def.value, writable: true, configurable: true, enumerable: false }; } else if (def.kind === "get") { descriptor = { get: def.value, configurable: true, enumerable: false }; } else if (def.kind === "set") { descriptor = { set: def.value, configurable: true, enumerable: false }; } else if (def.kind === "field") { descriptor = { configurable: true, writable: true, enumerable: true }; } var element = { kind: def.kind === "field" ? "field" : "method", key: key, placement: def["static"] ? "static" : def.kind === "field" ? "own" : "prototype", descriptor: descriptor }; if (def.decorators) element.decorators = def.decorators; if (def.kind === "field") element.initializer = def.value; return element; }

function hassio_system_coalesceGetterSetter(element, other) { if (element.descriptor.get !== undefined) { other.descriptor.get = element.descriptor.get; } else { other.descriptor.set = element.descriptor.set; } }

function hassio_system_coalesceClassElements(elements) { var newElements = []; var isSameElement = function isSameElement(other) { return other.kind === "method" && other.key === element.key && other.placement === element.placement; }; for (var i = 0; i < elements.length; i++) { var element = elements[i]; var other; if (element.kind === "method" && (other = newElements.find(isSameElement))) { if (hassio_system_isDataDescriptor(element.descriptor) || hassio_system_isDataDescriptor(other.descriptor)) { if (hassio_system_hasDecorators(element) || hassio_system_hasDecorators(other)) { throw new ReferenceError("Duplicated methods (" + element.key + ") can't be decorated."); } other.descriptor = element.descriptor; } else { if (hassio_system_hasDecorators(element)) { if (hassio_system_hasDecorators(other)) { throw new ReferenceError("Decorators can't be placed on different accessors with for " + "the same property (" + element.key + ")."); } other.decorators = element.decorators; } hassio_system_coalesceGetterSetter(element, other); } } else { newElements.push(element); } } return newElements; }

function hassio_system_hasDecorators(element) { return element.decorators && element.decorators.length; }

function hassio_system_isDataDescriptor(desc) { return desc !== undefined && !(desc.value === undefined && desc.writable === undefined); }

function hassio_system_optionalCallableProperty(obj, name) { var value = obj[name]; if (value !== undefined && typeof value !== "function") { throw new TypeError("Expected '" + name + "' to be a function"); } return value; }

function hassio_system_toPropertyKey(arg) { var key = hassio_system_toPrimitive(arg, "string"); return hassio_system_typeof(key) === "symbol" ? key : String(key); }

function hassio_system_toPrimitive(input, hint) { if (hassio_system_typeof(input) !== "object" || input === null) return input; var prim = input[Symbol.toPrimitive]; if (prim !== undefined) { var res = prim.call(input, hint || "default"); if (hassio_system_typeof(res) !== "object") return res; throw new TypeError("@@toPrimitive must return a primitive value."); } return (hint === "string" ? String : Number)(input); }

function hassio_system_toArray(arr) { return hassio_system_arrayWithHoles(arr) || hassio_system_iterableToArray(arr) || hassio_system_unsupportedIterableToArray(arr) || hassio_system_nonIterableRest(); }

function hassio_system_nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function hassio_system_unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return hassio_system_arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(n); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return hassio_system_arrayLikeToArray(o, minLen); }

function hassio_system_arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function hassio_system_iterableToArray(iter) { if (typeof Symbol !== "undefined" && Symbol.iterator in Object(iter)) return Array.from(iter); }

function hassio_system_arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }











var hassio_system_HassioSystem = hassio_system_decorate([Object(lit_element["d" /* customElement */])("hassio-system")], function (_initialize, _LitElement) {
  var HassioSystem = /*#__PURE__*/function (_LitElement2) {
    hassio_system_inherits(HassioSystem, _LitElement2);

    var _super = hassio_system_createSuper(HassioSystem);

    function HassioSystem() {
      var _this;

      hassio_system_classCallCheck(this, HassioSystem);

      for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
        args[_key] = arguments[_key];
      }

      _this = _super.call.apply(_super, [this].concat(args));

      _initialize(hassio_system_assertThisInitialized(_this));

      return _this;
    }

    return HassioSystem;
  }(_LitElement);

  return {
    F: HassioSystem,
    d: [{
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])({
        attribute: false
      })],
      key: "hass",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])({
        type: Boolean
      })],
      key: "narrow",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])({
        attribute: false
      })],
      key: "route",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "supervisorInfo",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "hostInfo",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "hassOsInfo",
      value: void 0
    }, {
      kind: "method",
      key: "render",
      value: function render() {
        return Object(lit_element["e" /* html */])(hassio_system_templateObject(), this.hass, this.narrow, this.route, supervisorTabs, this.hass, this.supervisorInfo, this.hass, this.hostInfo, this.hassOsInfo, this.hass);
      }
    }, {
      kind: "get",
      "static": true,
      key: "styles",
      value: function styles() {
        return [resources_styles["b" /* haStyle */], hassio_style["a" /* hassioStyle */], Object(lit_element["c" /* css */])(hassio_system_templateObject2())];
      }
    }]
  };
}, lit_element["a" /* LitElement */]);
// CONCATENATED MODULE: ./hassio/src/hassio-panel-router.ts
function hassio_panel_router_typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { hassio_panel_router_typeof = function _typeof(obj) { return typeof obj; }; } else { hassio_panel_router_typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return hassio_panel_router_typeof(obj); }

function hassio_panel_router_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function hassio_panel_router_inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) hassio_panel_router_setPrototypeOf(subClass, superClass); }

function hassio_panel_router_setPrototypeOf(o, p) { hassio_panel_router_setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return hassio_panel_router_setPrototypeOf(o, p); }

function hassio_panel_router_createSuper(Derived) { return function () { var Super = hassio_panel_router_getPrototypeOf(Derived), result; if (hassio_panel_router_isNativeReflectConstruct()) { var NewTarget = hassio_panel_router_getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return hassio_panel_router_possibleConstructorReturn(this, result); }; }

function hassio_panel_router_possibleConstructorReturn(self, call) { if (call && (hassio_panel_router_typeof(call) === "object" || typeof call === "function")) { return call; } return hassio_panel_router_assertThisInitialized(self); }

function hassio_panel_router_assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function hassio_panel_router_isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Date.prototype.toString.call(Reflect.construct(Date, [], function () {})); return true; } catch (e) { return false; } }

function hassio_panel_router_getPrototypeOf(o) { hassio_panel_router_getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return hassio_panel_router_getPrototypeOf(o); }

function hassio_panel_router_decorate(decorators, factory, superClass, mixins) { var api = hassio_panel_router_getDecoratorsApi(); if (mixins) { for (var i = 0; i < mixins.length; i++) { api = mixins[i](api); } } var r = factory(function initialize(O) { api.initializeInstanceElements(O, decorated.elements); }, superClass); var decorated = api.decorateClass(hassio_panel_router_coalesceClassElements(r.d.map(hassio_panel_router_createElementDescriptor)), decorators); api.initializeClassElements(r.F, decorated.elements); return api.runClassFinishers(r.F, decorated.finishers); }

function hassio_panel_router_getDecoratorsApi() { hassio_panel_router_getDecoratorsApi = function _getDecoratorsApi() { return api; }; var api = { elementsDefinitionOrder: [["method"], ["field"]], initializeInstanceElements: function initializeInstanceElements(O, elements) { ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { if (element.kind === kind && element.placement === "own") { this.defineClassElement(O, element); } }, this); }, this); }, initializeClassElements: function initializeClassElements(F, elements) { var proto = F.prototype; ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { var placement = element.placement; if (element.kind === kind && (placement === "static" || placement === "prototype")) { var receiver = placement === "static" ? F : proto; this.defineClassElement(receiver, element); } }, this); }, this); }, defineClassElement: function defineClassElement(receiver, element) { var descriptor = element.descriptor; if (element.kind === "field") { var initializer = element.initializer; descriptor = { enumerable: descriptor.enumerable, writable: descriptor.writable, configurable: descriptor.configurable, value: initializer === void 0 ? void 0 : initializer.call(receiver) }; } Object.defineProperty(receiver, element.key, descriptor); }, decorateClass: function decorateClass(elements, decorators) { var newElements = []; var finishers = []; var placements = { "static": [], prototype: [], own: [] }; elements.forEach(function (element) { this.addElementPlacement(element, placements); }, this); elements.forEach(function (element) { if (!hassio_panel_router_hasDecorators(element)) return newElements.push(element); var elementFinishersExtras = this.decorateElement(element, placements); newElements.push(elementFinishersExtras.element); newElements.push.apply(newElements, elementFinishersExtras.extras); finishers.push.apply(finishers, elementFinishersExtras.finishers); }, this); if (!decorators) { return { elements: newElements, finishers: finishers }; } var result = this.decorateConstructor(newElements, decorators); finishers.push.apply(finishers, result.finishers); result.finishers = finishers; return result; }, addElementPlacement: function addElementPlacement(element, placements, silent) { var keys = placements[element.placement]; if (!silent && keys.indexOf(element.key) !== -1) { throw new TypeError("Duplicated element (" + element.key + ")"); } keys.push(element.key); }, decorateElement: function decorateElement(element, placements) { var extras = []; var finishers = []; for (var decorators = element.decorators, i = decorators.length - 1; i >= 0; i--) { var keys = placements[element.placement]; keys.splice(keys.indexOf(element.key), 1); var elementObject = this.fromElementDescriptor(element); var elementFinisherExtras = this.toElementFinisherExtras((0, decorators[i])(elementObject) || elementObject); element = elementFinisherExtras.element; this.addElementPlacement(element, placements); if (elementFinisherExtras.finisher) { finishers.push(elementFinisherExtras.finisher); } var newExtras = elementFinisherExtras.extras; if (newExtras) { for (var j = 0; j < newExtras.length; j++) { this.addElementPlacement(newExtras[j], placements); } extras.push.apply(extras, newExtras); } } return { element: element, finishers: finishers, extras: extras }; }, decorateConstructor: function decorateConstructor(elements, decorators) { var finishers = []; for (var i = decorators.length - 1; i >= 0; i--) { var obj = this.fromClassDescriptor(elements); var elementsAndFinisher = this.toClassDescriptor((0, decorators[i])(obj) || obj); if (elementsAndFinisher.finisher !== undefined) { finishers.push(elementsAndFinisher.finisher); } if (elementsAndFinisher.elements !== undefined) { elements = elementsAndFinisher.elements; for (var j = 0; j < elements.length - 1; j++) { for (var k = j + 1; k < elements.length; k++) { if (elements[j].key === elements[k].key && elements[j].placement === elements[k].placement) { throw new TypeError("Duplicated element (" + elements[j].key + ")"); } } } } } return { elements: elements, finishers: finishers }; }, fromElementDescriptor: function fromElementDescriptor(element) { var obj = { kind: element.kind, key: element.key, placement: element.placement, descriptor: element.descriptor }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); if (element.kind === "field") obj.initializer = element.initializer; return obj; }, toElementDescriptors: function toElementDescriptors(elementObjects) { if (elementObjects === undefined) return; return hassio_panel_router_toArray(elementObjects).map(function (elementObject) { var element = this.toElementDescriptor(elementObject); this.disallowProperty(elementObject, "finisher", "An element descriptor"); this.disallowProperty(elementObject, "extras", "An element descriptor"); return element; }, this); }, toElementDescriptor: function toElementDescriptor(elementObject) { var kind = String(elementObject.kind); if (kind !== "method" && kind !== "field") { throw new TypeError('An element descriptor\'s .kind property must be either "method" or' + ' "field", but a decorator created an element descriptor with' + ' .kind "' + kind + '"'); } var key = hassio_panel_router_toPropertyKey(elementObject.key); var placement = String(elementObject.placement); if (placement !== "static" && placement !== "prototype" && placement !== "own") { throw new TypeError('An element descriptor\'s .placement property must be one of "static",' + ' "prototype" or "own", but a decorator created an element descriptor' + ' with .placement "' + placement + '"'); } var descriptor = elementObject.descriptor; this.disallowProperty(elementObject, "elements", "An element descriptor"); var element = { kind: kind, key: key, placement: placement, descriptor: Object.assign({}, descriptor) }; if (kind !== "field") { this.disallowProperty(elementObject, "initializer", "A method descriptor"); } else { this.disallowProperty(descriptor, "get", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "set", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "value", "The property descriptor of a field descriptor"); element.initializer = elementObject.initializer; } return element; }, toElementFinisherExtras: function toElementFinisherExtras(elementObject) { var element = this.toElementDescriptor(elementObject); var finisher = hassio_panel_router_optionalCallableProperty(elementObject, "finisher"); var extras = this.toElementDescriptors(elementObject.extras); return { element: element, finisher: finisher, extras: extras }; }, fromClassDescriptor: function fromClassDescriptor(elements) { var obj = { kind: "class", elements: elements.map(this.fromElementDescriptor, this) }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); return obj; }, toClassDescriptor: function toClassDescriptor(obj) { var kind = String(obj.kind); if (kind !== "class") { throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator' + ' created a class descriptor with .kind "' + kind + '"'); } this.disallowProperty(obj, "key", "A class descriptor"); this.disallowProperty(obj, "placement", "A class descriptor"); this.disallowProperty(obj, "descriptor", "A class descriptor"); this.disallowProperty(obj, "initializer", "A class descriptor"); this.disallowProperty(obj, "extras", "A class descriptor"); var finisher = hassio_panel_router_optionalCallableProperty(obj, "finisher"); var elements = this.toElementDescriptors(obj.elements); return { elements: elements, finisher: finisher }; }, runClassFinishers: function runClassFinishers(constructor, finishers) { for (var i = 0; i < finishers.length; i++) { var newConstructor = (0, finishers[i])(constructor); if (newConstructor !== undefined) { if (typeof newConstructor !== "function") { throw new TypeError("Finishers must return a constructor."); } constructor = newConstructor; } } return constructor; }, disallowProperty: function disallowProperty(obj, name, objectType) { if (obj[name] !== undefined) { throw new TypeError(objectType + " can't have a ." + name + " property."); } } }; return api; }

function hassio_panel_router_createElementDescriptor(def) { var key = hassio_panel_router_toPropertyKey(def.key); var descriptor; if (def.kind === "method") { descriptor = { value: def.value, writable: true, configurable: true, enumerable: false }; } else if (def.kind === "get") { descriptor = { get: def.value, configurable: true, enumerable: false }; } else if (def.kind === "set") { descriptor = { set: def.value, configurable: true, enumerable: false }; } else if (def.kind === "field") { descriptor = { configurable: true, writable: true, enumerable: true }; } var element = { kind: def.kind === "field" ? "field" : "method", key: key, placement: def["static"] ? "static" : def.kind === "field" ? "own" : "prototype", descriptor: descriptor }; if (def.decorators) element.decorators = def.decorators; if (def.kind === "field") element.initializer = def.value; return element; }

function hassio_panel_router_coalesceGetterSetter(element, other) { if (element.descriptor.get !== undefined) { other.descriptor.get = element.descriptor.get; } else { other.descriptor.set = element.descriptor.set; } }

function hassio_panel_router_coalesceClassElements(elements) { var newElements = []; var isSameElement = function isSameElement(other) { return other.kind === "method" && other.key === element.key && other.placement === element.placement; }; for (var i = 0; i < elements.length; i++) { var element = elements[i]; var other; if (element.kind === "method" && (other = newElements.find(isSameElement))) { if (hassio_panel_router_isDataDescriptor(element.descriptor) || hassio_panel_router_isDataDescriptor(other.descriptor)) { if (hassio_panel_router_hasDecorators(element) || hassio_panel_router_hasDecorators(other)) { throw new ReferenceError("Duplicated methods (" + element.key + ") can't be decorated."); } other.descriptor = element.descriptor; } else { if (hassio_panel_router_hasDecorators(element)) { if (hassio_panel_router_hasDecorators(other)) { throw new ReferenceError("Decorators can't be placed on different accessors with for " + "the same property (" + element.key + ")."); } other.decorators = element.decorators; } hassio_panel_router_coalesceGetterSetter(element, other); } } else { newElements.push(element); } } return newElements; }

function hassio_panel_router_hasDecorators(element) { return element.decorators && element.decorators.length; }

function hassio_panel_router_isDataDescriptor(desc) { return desc !== undefined && !(desc.value === undefined && desc.writable === undefined); }

function hassio_panel_router_optionalCallableProperty(obj, name) { var value = obj[name]; if (value !== undefined && typeof value !== "function") { throw new TypeError("Expected '" + name + "' to be a function"); } return value; }

function hassio_panel_router_toPropertyKey(arg) { var key = hassio_panel_router_toPrimitive(arg, "string"); return hassio_panel_router_typeof(key) === "symbol" ? key : String(key); }

function hassio_panel_router_toPrimitive(input, hint) { if (hassio_panel_router_typeof(input) !== "object" || input === null) return input; var prim = input[Symbol.toPrimitive]; if (prim !== undefined) { var res = prim.call(input, hint || "default"); if (hassio_panel_router_typeof(res) !== "object") return res; throw new TypeError("@@toPrimitive must return a primitive value."); } return (hint === "string" ? String : Number)(input); }

function hassio_panel_router_toArray(arr) { return hassio_panel_router_arrayWithHoles(arr) || hassio_panel_router_iterableToArray(arr) || hassio_panel_router_unsupportedIterableToArray(arr) || hassio_panel_router_nonIterableRest(); }

function hassio_panel_router_nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function hassio_panel_router_unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return hassio_panel_router_arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(n); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return hassio_panel_router_arrayLikeToArray(o, minLen); }

function hassio_panel_router_arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function hassio_panel_router_iterableToArray(iter) { if (typeof Symbol !== "undefined" && Symbol.iterator in Object(iter)) return Array.from(iter); }

function hassio_panel_router_arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }



 // Don't codesplit it, that way the dashboard always loads fast.

 // Don't codesplit the others, because it breaks the UI when pushed to a Pi




var hassio_panel_router_HassioPanelRouter = hassio_panel_router_decorate([Object(lit_element["d" /* customElement */])("hassio-panel-router")], function (_initialize, _HassRouterPage) {
  var HassioPanelRouter = /*#__PURE__*/function (_HassRouterPage2) {
    hassio_panel_router_inherits(HassioPanelRouter, _HassRouterPage2);

    var _super = hassio_panel_router_createSuper(HassioPanelRouter);

    function HassioPanelRouter() {
      var _this;

      hassio_panel_router_classCallCheck(this, HassioPanelRouter);

      for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
        args[_key] = arguments[_key];
      }

      _this = _super.call.apply(_super, [this].concat(args));

      _initialize(hassio_panel_router_assertThisInitialized(_this));

      return _this;
    }

    return HassioPanelRouter;
  }(_HassRouterPage);

  return {
    F: HassioPanelRouter,
    d: [{
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])({
        attribute: false
      })],
      key: "hass",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])({
        attribute: false
      })],
      key: "route",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])({
        type: Boolean
      })],
      key: "narrow",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])({
        attribute: false
      })],
      key: "supervisorInfo",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])({
        attribute: false
      })],
      key: "hostInfo",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])({
        attribute: false
      })],
      key: "hassInfo",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])({
        attribute: false
      })],
      key: "hassOsInfo",
      value: void 0
    }, {
      kind: "field",
      key: "routerOptions",
      value: function value() {
        return {
          routes: {
            dashboard: {
              tag: "hassio-dashboard"
            },
            store: {
              tag: "hassio-addon-store"
            },
            snapshots: {
              tag: "hassio-snapshots"
            },
            system: {
              tag: "hassio-system"
            }
          }
        };
      }
    }, {
      kind: "method",
      key: "updatePageEl",
      value: function updatePageEl(el) {
        el.hass = this.hass;
        el.route = this.route;
        el.narrow = this.narrow;
        el.supervisorInfo = this.supervisorInfo;
        el.hostInfo = this.hostInfo;
        el.hassInfo = this.hassInfo;
        el.hassOsInfo = this.hassOsInfo;
      }
    }]
  };
}, hass_router_page["a" /* HassRouterPage */]);
// CONCATENATED MODULE: ./hassio/src/hassio-panel.ts
function hassio_panel_typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { hassio_panel_typeof = function _typeof(obj) { return typeof obj; }; } else { hassio_panel_typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return hassio_panel_typeof(obj); }

function hassio_panel_templateObject() {
  var data = hassio_panel_taggedTemplateLiteral(["\n      <hassio-panel-router\n        .route=", "\n        .hass=", "\n        .narrow=", "\n        .supervisorInfo=", "\n        .hostInfo=", "\n        .hassInfo=", "\n        .hassOsInfo=", "\n      ></hassio-panel-router>\n    "]);

  hassio_panel_templateObject = function _templateObject() {
    return data;
  };

  return data;
}

function hassio_panel_taggedTemplateLiteral(strings, raw) { if (!raw) { raw = strings.slice(0); } return Object.freeze(Object.defineProperties(strings, { raw: { value: Object.freeze(raw) } })); }

function hassio_panel_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function hassio_panel_inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) hassio_panel_setPrototypeOf(subClass, superClass); }

function hassio_panel_setPrototypeOf(o, p) { hassio_panel_setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return hassio_panel_setPrototypeOf(o, p); }

function hassio_panel_createSuper(Derived) { return function () { var Super = hassio_panel_getPrototypeOf(Derived), result; if (hassio_panel_isNativeReflectConstruct()) { var NewTarget = hassio_panel_getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return hassio_panel_possibleConstructorReturn(this, result); }; }

function hassio_panel_possibleConstructorReturn(self, call) { if (call && (hassio_panel_typeof(call) === "object" || typeof call === "function")) { return call; } return hassio_panel_assertThisInitialized(self); }

function hassio_panel_assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function hassio_panel_isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Date.prototype.toString.call(Reflect.construct(Date, [], function () {})); return true; } catch (e) { return false; } }

function hassio_panel_getPrototypeOf(o) { hassio_panel_getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return hassio_panel_getPrototypeOf(o); }

function hassio_panel_decorate(decorators, factory, superClass, mixins) { var api = hassio_panel_getDecoratorsApi(); if (mixins) { for (var i = 0; i < mixins.length; i++) { api = mixins[i](api); } } var r = factory(function initialize(O) { api.initializeInstanceElements(O, decorated.elements); }, superClass); var decorated = api.decorateClass(hassio_panel_coalesceClassElements(r.d.map(hassio_panel_createElementDescriptor)), decorators); api.initializeClassElements(r.F, decorated.elements); return api.runClassFinishers(r.F, decorated.finishers); }

function hassio_panel_getDecoratorsApi() { hassio_panel_getDecoratorsApi = function _getDecoratorsApi() { return api; }; var api = { elementsDefinitionOrder: [["method"], ["field"]], initializeInstanceElements: function initializeInstanceElements(O, elements) { ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { if (element.kind === kind && element.placement === "own") { this.defineClassElement(O, element); } }, this); }, this); }, initializeClassElements: function initializeClassElements(F, elements) { var proto = F.prototype; ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { var placement = element.placement; if (element.kind === kind && (placement === "static" || placement === "prototype")) { var receiver = placement === "static" ? F : proto; this.defineClassElement(receiver, element); } }, this); }, this); }, defineClassElement: function defineClassElement(receiver, element) { var descriptor = element.descriptor; if (element.kind === "field") { var initializer = element.initializer; descriptor = { enumerable: descriptor.enumerable, writable: descriptor.writable, configurable: descriptor.configurable, value: initializer === void 0 ? void 0 : initializer.call(receiver) }; } Object.defineProperty(receiver, element.key, descriptor); }, decorateClass: function decorateClass(elements, decorators) { var newElements = []; var finishers = []; var placements = { "static": [], prototype: [], own: [] }; elements.forEach(function (element) { this.addElementPlacement(element, placements); }, this); elements.forEach(function (element) { if (!hassio_panel_hasDecorators(element)) return newElements.push(element); var elementFinishersExtras = this.decorateElement(element, placements); newElements.push(elementFinishersExtras.element); newElements.push.apply(newElements, elementFinishersExtras.extras); finishers.push.apply(finishers, elementFinishersExtras.finishers); }, this); if (!decorators) { return { elements: newElements, finishers: finishers }; } var result = this.decorateConstructor(newElements, decorators); finishers.push.apply(finishers, result.finishers); result.finishers = finishers; return result; }, addElementPlacement: function addElementPlacement(element, placements, silent) { var keys = placements[element.placement]; if (!silent && keys.indexOf(element.key) !== -1) { throw new TypeError("Duplicated element (" + element.key + ")"); } keys.push(element.key); }, decorateElement: function decorateElement(element, placements) { var extras = []; var finishers = []; for (var decorators = element.decorators, i = decorators.length - 1; i >= 0; i--) { var keys = placements[element.placement]; keys.splice(keys.indexOf(element.key), 1); var elementObject = this.fromElementDescriptor(element); var elementFinisherExtras = this.toElementFinisherExtras((0, decorators[i])(elementObject) || elementObject); element = elementFinisherExtras.element; this.addElementPlacement(element, placements); if (elementFinisherExtras.finisher) { finishers.push(elementFinisherExtras.finisher); } var newExtras = elementFinisherExtras.extras; if (newExtras) { for (var j = 0; j < newExtras.length; j++) { this.addElementPlacement(newExtras[j], placements); } extras.push.apply(extras, newExtras); } } return { element: element, finishers: finishers, extras: extras }; }, decorateConstructor: function decorateConstructor(elements, decorators) { var finishers = []; for (var i = decorators.length - 1; i >= 0; i--) { var obj = this.fromClassDescriptor(elements); var elementsAndFinisher = this.toClassDescriptor((0, decorators[i])(obj) || obj); if (elementsAndFinisher.finisher !== undefined) { finishers.push(elementsAndFinisher.finisher); } if (elementsAndFinisher.elements !== undefined) { elements = elementsAndFinisher.elements; for (var j = 0; j < elements.length - 1; j++) { for (var k = j + 1; k < elements.length; k++) { if (elements[j].key === elements[k].key && elements[j].placement === elements[k].placement) { throw new TypeError("Duplicated element (" + elements[j].key + ")"); } } } } } return { elements: elements, finishers: finishers }; }, fromElementDescriptor: function fromElementDescriptor(element) { var obj = { kind: element.kind, key: element.key, placement: element.placement, descriptor: element.descriptor }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); if (element.kind === "field") obj.initializer = element.initializer; return obj; }, toElementDescriptors: function toElementDescriptors(elementObjects) { if (elementObjects === undefined) return; return hassio_panel_toArray(elementObjects).map(function (elementObject) { var element = this.toElementDescriptor(elementObject); this.disallowProperty(elementObject, "finisher", "An element descriptor"); this.disallowProperty(elementObject, "extras", "An element descriptor"); return element; }, this); }, toElementDescriptor: function toElementDescriptor(elementObject) { var kind = String(elementObject.kind); if (kind !== "method" && kind !== "field") { throw new TypeError('An element descriptor\'s .kind property must be either "method" or' + ' "field", but a decorator created an element descriptor with' + ' .kind "' + kind + '"'); } var key = hassio_panel_toPropertyKey(elementObject.key); var placement = String(elementObject.placement); if (placement !== "static" && placement !== "prototype" && placement !== "own") { throw new TypeError('An element descriptor\'s .placement property must be one of "static",' + ' "prototype" or "own", but a decorator created an element descriptor' + ' with .placement "' + placement + '"'); } var descriptor = elementObject.descriptor; this.disallowProperty(elementObject, "elements", "An element descriptor"); var element = { kind: kind, key: key, placement: placement, descriptor: Object.assign({}, descriptor) }; if (kind !== "field") { this.disallowProperty(elementObject, "initializer", "A method descriptor"); } else { this.disallowProperty(descriptor, "get", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "set", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "value", "The property descriptor of a field descriptor"); element.initializer = elementObject.initializer; } return element; }, toElementFinisherExtras: function toElementFinisherExtras(elementObject) { var element = this.toElementDescriptor(elementObject); var finisher = hassio_panel_optionalCallableProperty(elementObject, "finisher"); var extras = this.toElementDescriptors(elementObject.extras); return { element: element, finisher: finisher, extras: extras }; }, fromClassDescriptor: function fromClassDescriptor(elements) { var obj = { kind: "class", elements: elements.map(this.fromElementDescriptor, this) }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); return obj; }, toClassDescriptor: function toClassDescriptor(obj) { var kind = String(obj.kind); if (kind !== "class") { throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator' + ' created a class descriptor with .kind "' + kind + '"'); } this.disallowProperty(obj, "key", "A class descriptor"); this.disallowProperty(obj, "placement", "A class descriptor"); this.disallowProperty(obj, "descriptor", "A class descriptor"); this.disallowProperty(obj, "initializer", "A class descriptor"); this.disallowProperty(obj, "extras", "A class descriptor"); var finisher = hassio_panel_optionalCallableProperty(obj, "finisher"); var elements = this.toElementDescriptors(obj.elements); return { elements: elements, finisher: finisher }; }, runClassFinishers: function runClassFinishers(constructor, finishers) { for (var i = 0; i < finishers.length; i++) { var newConstructor = (0, finishers[i])(constructor); if (newConstructor !== undefined) { if (typeof newConstructor !== "function") { throw new TypeError("Finishers must return a constructor."); } constructor = newConstructor; } } return constructor; }, disallowProperty: function disallowProperty(obj, name, objectType) { if (obj[name] !== undefined) { throw new TypeError(objectType + " can't have a ." + name + " property."); } } }; return api; }

function hassio_panel_createElementDescriptor(def) { var key = hassio_panel_toPropertyKey(def.key); var descriptor; if (def.kind === "method") { descriptor = { value: def.value, writable: true, configurable: true, enumerable: false }; } else if (def.kind === "get") { descriptor = { get: def.value, configurable: true, enumerable: false }; } else if (def.kind === "set") { descriptor = { set: def.value, configurable: true, enumerable: false }; } else if (def.kind === "field") { descriptor = { configurable: true, writable: true, enumerable: true }; } var element = { kind: def.kind === "field" ? "field" : "method", key: key, placement: def["static"] ? "static" : def.kind === "field" ? "own" : "prototype", descriptor: descriptor }; if (def.decorators) element.decorators = def.decorators; if (def.kind === "field") element.initializer = def.value; return element; }

function hassio_panel_coalesceGetterSetter(element, other) { if (element.descriptor.get !== undefined) { other.descriptor.get = element.descriptor.get; } else { other.descriptor.set = element.descriptor.set; } }

function hassio_panel_coalesceClassElements(elements) { var newElements = []; var isSameElement = function isSameElement(other) { return other.kind === "method" && other.key === element.key && other.placement === element.placement; }; for (var i = 0; i < elements.length; i++) { var element = elements[i]; var other; if (element.kind === "method" && (other = newElements.find(isSameElement))) { if (hassio_panel_isDataDescriptor(element.descriptor) || hassio_panel_isDataDescriptor(other.descriptor)) { if (hassio_panel_hasDecorators(element) || hassio_panel_hasDecorators(other)) { throw new ReferenceError("Duplicated methods (" + element.key + ") can't be decorated."); } other.descriptor = element.descriptor; } else { if (hassio_panel_hasDecorators(element)) { if (hassio_panel_hasDecorators(other)) { throw new ReferenceError("Decorators can't be placed on different accessors with for " + "the same property (" + element.key + ")."); } other.decorators = element.decorators; } hassio_panel_coalesceGetterSetter(element, other); } } else { newElements.push(element); } } return newElements; }

function hassio_panel_hasDecorators(element) { return element.decorators && element.decorators.length; }

function hassio_panel_isDataDescriptor(desc) { return desc !== undefined && !(desc.value === undefined && desc.writable === undefined); }

function hassio_panel_optionalCallableProperty(obj, name) { var value = obj[name]; if (value !== undefined && typeof value !== "function") { throw new TypeError("Expected '" + name + "' to be a function"); } return value; }

function hassio_panel_toPropertyKey(arg) { var key = hassio_panel_toPrimitive(arg, "string"); return hassio_panel_typeof(key) === "symbol" ? key : String(key); }

function hassio_panel_toPrimitive(input, hint) { if (hassio_panel_typeof(input) !== "object" || input === null) return input; var prim = input[Symbol.toPrimitive]; if (prim !== undefined) { var res = prim.call(input, hint || "default"); if (hassio_panel_typeof(res) !== "object") return res; throw new TypeError("@@toPrimitive must return a primitive value."); } return (hint === "string" ? String : Number)(input); }

function hassio_panel_toArray(arr) { return hassio_panel_arrayWithHoles(arr) || hassio_panel_iterableToArray(arr) || hassio_panel_unsupportedIterableToArray(arr) || hassio_panel_nonIterableRest(); }

function hassio_panel_nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function hassio_panel_unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return hassio_panel_arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(n); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return hassio_panel_arrayLikeToArray(o, minLen); }

function hassio_panel_arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function hassio_panel_iterableToArray(iter) { if (typeof Symbol !== "undefined" && Symbol.iterator in Object(iter)) return Array.from(iter); }

function hassio_panel_arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }




var supervisorTabs = [{
  name: "Dashboard",
  path: "/hassio/dashboard",
  icon: "hassio:view-dashboard"
}, {
  name: "Add-on store",
  path: "/hassio/store",
  icon: "hassio:store"
}, {
  name: "Snapshots",
  path: "/hassio/snapshots",
  icon: "hassio:backup-restore"
}, {
  name: "System",
  path: "/hassio/system",
  icon: "hassio:cogs"
}];

var hassio_panel_HassioPanel = hassio_panel_decorate([Object(lit_element["d" /* customElement */])("hassio-panel")], function (_initialize, _LitElement) {
  var HassioPanel = /*#__PURE__*/function (_LitElement2) {
    hassio_panel_inherits(HassioPanel, _LitElement2);

    var _super = hassio_panel_createSuper(HassioPanel);

    function HassioPanel() {
      var _this;

      hassio_panel_classCallCheck(this, HassioPanel);

      for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
        args[_key] = arguments[_key];
      }

      _this = _super.call.apply(_super, [this].concat(args));

      _initialize(hassio_panel_assertThisInitialized(_this));

      return _this;
    }

    return HassioPanel;
  }(_LitElement);

  return {
    F: HassioPanel,
    d: [{
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])({
        attribute: false
      })],
      key: "hass",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])({
        type: Boolean
      })],
      key: "narrow",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])({
        attribute: false
      })],
      key: "route",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])({
        attribute: false
      })],
      key: "supervisorInfo",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])({
        attribute: false
      })],
      key: "hostInfo",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])({
        attribute: false
      })],
      key: "hassInfo",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])({
        attribute: false
      })],
      key: "hassOsInfo",
      value: void 0
    }, {
      kind: "method",
      key: "render",
      value: function render() {
        return Object(lit_element["e" /* html */])(hassio_panel_templateObject(), this.route, this.hass, this.narrow, this.supervisorInfo, this.hostInfo, this.hassInfo, this.hassOsInfo);
      }
    }]
  };
}, lit_element["a" /* LitElement */]);
// CONCATENATED MODULE: ./hassio/src/hassio-main.ts
function hassio_main_typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { hassio_main_typeof = function _typeof(obj) { return typeof obj; }; } else { hassio_main_typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return hassio_main_typeof(obj); }

function hassio_main_slicedToArray(arr, i) { return hassio_main_arrayWithHoles(arr) || hassio_main_iterableToArrayLimit(arr, i) || hassio_main_unsupportedIterableToArray(arr, i) || hassio_main_nonIterableRest(); }

function hassio_main_iterableToArrayLimit(arr, i) { if (typeof Symbol === "undefined" || !(Symbol.iterator in Object(arr))) return; var _arr = []; var _n = true; var _d = false; var _e = undefined; try { for (var _i = arr[Symbol.iterator](), _s; !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i["return"] != null) _i["return"](); } finally { if (_d) throw _e; } } return _arr; }

function hassio_main_asyncGeneratorStep(gen, resolve, reject, _next, _throw, key, arg) { try { var info = gen[key](arg); var value = info.value; } catch (error) { reject(error); return; } if (info.done) { resolve(value); } else { Promise.resolve(value).then(_next, _throw); } }

function hassio_main_asyncToGenerator(fn) { return function () { var self = this, args = arguments; return new Promise(function (resolve, reject) { var gen = fn.apply(self, args); function _next(value) { hassio_main_asyncGeneratorStep(gen, resolve, reject, _next, _throw, "next", value); } function _throw(err) { hassio_main_asyncGeneratorStep(gen, resolve, reject, _next, _throw, "throw", err); } _next(undefined); }); }; }

function hassio_main_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function hassio_main_inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) hassio_main_setPrototypeOf(subClass, superClass); }

function hassio_main_setPrototypeOf(o, p) { hassio_main_setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return hassio_main_setPrototypeOf(o, p); }

function hassio_main_createSuper(Derived) { return function () { var Super = hassio_main_getPrototypeOf(Derived), result; if (hassio_main_isNativeReflectConstruct()) { var NewTarget = hassio_main_getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return hassio_main_possibleConstructorReturn(this, result); }; }

function hassio_main_possibleConstructorReturn(self, call) { if (call && (hassio_main_typeof(call) === "object" || typeof call === "function")) { return call; } return hassio_main_assertThisInitialized(self); }

function hassio_main_assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function hassio_main_isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Date.prototype.toString.call(Reflect.construct(Date, [], function () {})); return true; } catch (e) { return false; } }

function hassio_main_decorate(decorators, factory, superClass, mixins) { var api = hassio_main_getDecoratorsApi(); if (mixins) { for (var i = 0; i < mixins.length; i++) { api = mixins[i](api); } } var r = factory(function initialize(O) { api.initializeInstanceElements(O, decorated.elements); }, superClass); var decorated = api.decorateClass(hassio_main_coalesceClassElements(r.d.map(hassio_main_createElementDescriptor)), decorators); api.initializeClassElements(r.F, decorated.elements); return api.runClassFinishers(r.F, decorated.finishers); }

function hassio_main_getDecoratorsApi() { hassio_main_getDecoratorsApi = function _getDecoratorsApi() { return api; }; var api = { elementsDefinitionOrder: [["method"], ["field"]], initializeInstanceElements: function initializeInstanceElements(O, elements) { ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { if (element.kind === kind && element.placement === "own") { this.defineClassElement(O, element); } }, this); }, this); }, initializeClassElements: function initializeClassElements(F, elements) { var proto = F.prototype; ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { var placement = element.placement; if (element.kind === kind && (placement === "static" || placement === "prototype")) { var receiver = placement === "static" ? F : proto; this.defineClassElement(receiver, element); } }, this); }, this); }, defineClassElement: function defineClassElement(receiver, element) { var descriptor = element.descriptor; if (element.kind === "field") { var initializer = element.initializer; descriptor = { enumerable: descriptor.enumerable, writable: descriptor.writable, configurable: descriptor.configurable, value: initializer === void 0 ? void 0 : initializer.call(receiver) }; } Object.defineProperty(receiver, element.key, descriptor); }, decorateClass: function decorateClass(elements, decorators) { var newElements = []; var finishers = []; var placements = { "static": [], prototype: [], own: [] }; elements.forEach(function (element) { this.addElementPlacement(element, placements); }, this); elements.forEach(function (element) { if (!hassio_main_hasDecorators(element)) return newElements.push(element); var elementFinishersExtras = this.decorateElement(element, placements); newElements.push(elementFinishersExtras.element); newElements.push.apply(newElements, elementFinishersExtras.extras); finishers.push.apply(finishers, elementFinishersExtras.finishers); }, this); if (!decorators) { return { elements: newElements, finishers: finishers }; } var result = this.decorateConstructor(newElements, decorators); finishers.push.apply(finishers, result.finishers); result.finishers = finishers; return result; }, addElementPlacement: function addElementPlacement(element, placements, silent) { var keys = placements[element.placement]; if (!silent && keys.indexOf(element.key) !== -1) { throw new TypeError("Duplicated element (" + element.key + ")"); } keys.push(element.key); }, decorateElement: function decorateElement(element, placements) { var extras = []; var finishers = []; for (var decorators = element.decorators, i = decorators.length - 1; i >= 0; i--) { var keys = placements[element.placement]; keys.splice(keys.indexOf(element.key), 1); var elementObject = this.fromElementDescriptor(element); var elementFinisherExtras = this.toElementFinisherExtras((0, decorators[i])(elementObject) || elementObject); element = elementFinisherExtras.element; this.addElementPlacement(element, placements); if (elementFinisherExtras.finisher) { finishers.push(elementFinisherExtras.finisher); } var newExtras = elementFinisherExtras.extras; if (newExtras) { for (var j = 0; j < newExtras.length; j++) { this.addElementPlacement(newExtras[j], placements); } extras.push.apply(extras, newExtras); } } return { element: element, finishers: finishers, extras: extras }; }, decorateConstructor: function decorateConstructor(elements, decorators) { var finishers = []; for (var i = decorators.length - 1; i >= 0; i--) { var obj = this.fromClassDescriptor(elements); var elementsAndFinisher = this.toClassDescriptor((0, decorators[i])(obj) || obj); if (elementsAndFinisher.finisher !== undefined) { finishers.push(elementsAndFinisher.finisher); } if (elementsAndFinisher.elements !== undefined) { elements = elementsAndFinisher.elements; for (var j = 0; j < elements.length - 1; j++) { for (var k = j + 1; k < elements.length; k++) { if (elements[j].key === elements[k].key && elements[j].placement === elements[k].placement) { throw new TypeError("Duplicated element (" + elements[j].key + ")"); } } } } } return { elements: elements, finishers: finishers }; }, fromElementDescriptor: function fromElementDescriptor(element) { var obj = { kind: element.kind, key: element.key, placement: element.placement, descriptor: element.descriptor }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); if (element.kind === "field") obj.initializer = element.initializer; return obj; }, toElementDescriptors: function toElementDescriptors(elementObjects) { if (elementObjects === undefined) return; return hassio_main_toArray(elementObjects).map(function (elementObject) { var element = this.toElementDescriptor(elementObject); this.disallowProperty(elementObject, "finisher", "An element descriptor"); this.disallowProperty(elementObject, "extras", "An element descriptor"); return element; }, this); }, toElementDescriptor: function toElementDescriptor(elementObject) { var kind = String(elementObject.kind); if (kind !== "method" && kind !== "field") { throw new TypeError('An element descriptor\'s .kind property must be either "method" or' + ' "field", but a decorator created an element descriptor with' + ' .kind "' + kind + '"'); } var key = hassio_main_toPropertyKey(elementObject.key); var placement = String(elementObject.placement); if (placement !== "static" && placement !== "prototype" && placement !== "own") { throw new TypeError('An element descriptor\'s .placement property must be one of "static",' + ' "prototype" or "own", but a decorator created an element descriptor' + ' with .placement "' + placement + '"'); } var descriptor = elementObject.descriptor; this.disallowProperty(elementObject, "elements", "An element descriptor"); var element = { kind: kind, key: key, placement: placement, descriptor: Object.assign({}, descriptor) }; if (kind !== "field") { this.disallowProperty(elementObject, "initializer", "A method descriptor"); } else { this.disallowProperty(descriptor, "get", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "set", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "value", "The property descriptor of a field descriptor"); element.initializer = elementObject.initializer; } return element; }, toElementFinisherExtras: function toElementFinisherExtras(elementObject) { var element = this.toElementDescriptor(elementObject); var finisher = hassio_main_optionalCallableProperty(elementObject, "finisher"); var extras = this.toElementDescriptors(elementObject.extras); return { element: element, finisher: finisher, extras: extras }; }, fromClassDescriptor: function fromClassDescriptor(elements) { var obj = { kind: "class", elements: elements.map(this.fromElementDescriptor, this) }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); return obj; }, toClassDescriptor: function toClassDescriptor(obj) { var kind = String(obj.kind); if (kind !== "class") { throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator' + ' created a class descriptor with .kind "' + kind + '"'); } this.disallowProperty(obj, "key", "A class descriptor"); this.disallowProperty(obj, "placement", "A class descriptor"); this.disallowProperty(obj, "descriptor", "A class descriptor"); this.disallowProperty(obj, "initializer", "A class descriptor"); this.disallowProperty(obj, "extras", "A class descriptor"); var finisher = hassio_main_optionalCallableProperty(obj, "finisher"); var elements = this.toElementDescriptors(obj.elements); return { elements: elements, finisher: finisher }; }, runClassFinishers: function runClassFinishers(constructor, finishers) { for (var i = 0; i < finishers.length; i++) { var newConstructor = (0, finishers[i])(constructor); if (newConstructor !== undefined) { if (typeof newConstructor !== "function") { throw new TypeError("Finishers must return a constructor."); } constructor = newConstructor; } } return constructor; }, disallowProperty: function disallowProperty(obj, name, objectType) { if (obj[name] !== undefined) { throw new TypeError(objectType + " can't have a ." + name + " property."); } } }; return api; }

function hassio_main_createElementDescriptor(def) { var key = hassio_main_toPropertyKey(def.key); var descriptor; if (def.kind === "method") { descriptor = { value: def.value, writable: true, configurable: true, enumerable: false }; } else if (def.kind === "get") { descriptor = { get: def.value, configurable: true, enumerable: false }; } else if (def.kind === "set") { descriptor = { set: def.value, configurable: true, enumerable: false }; } else if (def.kind === "field") { descriptor = { configurable: true, writable: true, enumerable: true }; } var element = { kind: def.kind === "field" ? "field" : "method", key: key, placement: def["static"] ? "static" : def.kind === "field" ? "own" : "prototype", descriptor: descriptor }; if (def.decorators) element.decorators = def.decorators; if (def.kind === "field") element.initializer = def.value; return element; }

function hassio_main_coalesceGetterSetter(element, other) { if (element.descriptor.get !== undefined) { other.descriptor.get = element.descriptor.get; } else { other.descriptor.set = element.descriptor.set; } }

function hassio_main_coalesceClassElements(elements) { var newElements = []; var isSameElement = function isSameElement(other) { return other.kind === "method" && other.key === element.key && other.placement === element.placement; }; for (var i = 0; i < elements.length; i++) { var element = elements[i]; var other; if (element.kind === "method" && (other = newElements.find(isSameElement))) { if (hassio_main_isDataDescriptor(element.descriptor) || hassio_main_isDataDescriptor(other.descriptor)) { if (hassio_main_hasDecorators(element) || hassio_main_hasDecorators(other)) { throw new ReferenceError("Duplicated methods (" + element.key + ") can't be decorated."); } other.descriptor = element.descriptor; } else { if (hassio_main_hasDecorators(element)) { if (hassio_main_hasDecorators(other)) { throw new ReferenceError("Decorators can't be placed on different accessors with for " + "the same property (" + element.key + ")."); } other.decorators = element.decorators; } hassio_main_coalesceGetterSetter(element, other); } } else { newElements.push(element); } } return newElements; }

function hassio_main_hasDecorators(element) { return element.decorators && element.decorators.length; }

function hassio_main_isDataDescriptor(desc) { return desc !== undefined && !(desc.value === undefined && desc.writable === undefined); }

function hassio_main_optionalCallableProperty(obj, name) { var value = obj[name]; if (value !== undefined && typeof value !== "function") { throw new TypeError("Expected '" + name + "' to be a function"); } return value; }

function hassio_main_toPropertyKey(arg) { var key = hassio_main_toPrimitive(arg, "string"); return hassio_main_typeof(key) === "symbol" ? key : String(key); }

function hassio_main_toPrimitive(input, hint) { if (hassio_main_typeof(input) !== "object" || input === null) return input; var prim = input[Symbol.toPrimitive]; if (prim !== undefined) { var res = prim.call(input, hint || "default"); if (hassio_main_typeof(res) !== "object") return res; throw new TypeError("@@toPrimitive must return a primitive value."); } return (hint === "string" ? String : Number)(input); }

function hassio_main_toArray(arr) { return hassio_main_arrayWithHoles(arr) || hassio_main_iterableToArray(arr) || hassio_main_unsupportedIterableToArray(arr) || hassio_main_nonIterableRest(); }

function hassio_main_nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function hassio_main_unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return hassio_main_arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(n); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return hassio_main_arrayLikeToArray(o, minLen); }

function hassio_main_arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function hassio_main_iterableToArray(iter) { if (typeof Symbol !== "undefined" && Symbol.iterator in Object(iter)) return Array.from(iter); }

function hassio_main_arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }

function hassio_main_get(target, property, receiver) { if (typeof Reflect !== "undefined" && Reflect.get) { hassio_main_get = Reflect.get; } else { hassio_main_get = function _get(target, property, receiver) { var base = hassio_main_superPropBase(target, property); if (!base) return; var desc = Object.getOwnPropertyDescriptor(base, property); if (desc.get) { return desc.get.call(receiver); } return desc.value; }; } return hassio_main_get(target, property, receiver || target); }

function hassio_main_superPropBase(object, property) { while (!Object.prototype.hasOwnProperty.call(object, property)) { object = hassio_main_getPrototypeOf(object); if (object === null) break; } return object; }

function hassio_main_getPrototypeOf(o) { hassio_main_getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return hassio_main_getPrototypeOf(o); }














// Don't codesplit it, that way the dashboard always loads fast.
 // The register callback of the IronA11yKeysBehavior inside ha-icon-button
// is not called, causing _keyBindings to be uninitiliazed for ha-icon-button,
// causing an exception when added to DOM. When transpiled to ES5, this will
// break the build.

customElements.get("ha-icon-button").prototype._keyBindings = {};

var hassio_main_HassioMain = hassio_main_decorate([Object(lit_element["d" /* customElement */])("hassio-main")], function (_initialize, _ProvideHassLitMixin) {
  var HassioMain = /*#__PURE__*/function (_ProvideHassLitMixin2) {
    hassio_main_inherits(HassioMain, _ProvideHassLitMixin2);

    var _super = hassio_main_createSuper(HassioMain);

    function HassioMain() {
      var _this;

      hassio_main_classCallCheck(this, HassioMain);

      for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
        args[_key] = arguments[_key];
      }

      _this = _super.call.apply(_super, [this].concat(args));

      _initialize(hassio_main_assertThisInitialized(_this));

      return _this;
    }

    return HassioMain;
  }(_ProvideHassLitMixin);

  return {
    F: HassioMain,
    d: [{
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "hass",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "panel",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "narrow",
      value: void 0
    }, {
      kind: "field",
      key: "routerOptions",
      value: function value() {
        var _this2 = this;

        return {
          // Hass.io has a page with tabs, so we route all non-matching routes to it.
          defaultPage: "dashboard",
          initialLoad: function initialLoad() {
            return _this2._fetchData();
          },
          showLoading: true,
          routes: {
            dashboard: {
              tag: "hassio-panel",
              cache: true
            },
            snapshots: "dashboard",
            store: "dashboard",
            system: "dashboard",
            addon: {
              tag: "hassio-addon-dashboard",
              load: function load() {
                return Promise.all(/* import() | hassio-addon-dashboard */[__webpack_require__.e(0), __webpack_require__.e(11), __webpack_require__.e(6)]).then(__webpack_require__.bind(null, 192));
              }
            },
            ingress: {
              tag: "hassio-ingress-view",
              load: function load() {
                return __webpack_require__.e(/* import() | hassio-ingress-view */ 7).then(__webpack_require__.bind(null, 190));
              }
            }
          }
        };
      }
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "_supervisorInfo",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "_hostInfo",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "_hassOsInfo",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "_hassInfo",
      value: void 0
    }, {
      kind: "method",
      key: "firstUpdated",
      value: function firstUpdated(changedProps) {
        var _this3 = this;

        hassio_main_get(hassio_main_getPrototypeOf(HassioMain.prototype), "firstUpdated", this).call(this, changedProps);

        applyThemesOnElement(this.parentElement, this.hass.themes, this.hass.selectedTheme || this.hass.themes.default_theme);
        this.style.setProperty("--app-header-background-color", "var(--sidebar-background-color)");
        this.style.setProperty("--app-header-text-color", "var(--sidebar-text-color)");
        this.style.setProperty("--app-header-border-bottom", "1px solid var(--divider-color)");
        this.addEventListener("hass-api-called", function (ev) {
          return _this3._apiCalled(ev);
        }); // Paulus - March 17, 2019
        // We went to a single hass-toggle-menu event in HA 0.90. However, the
        // supervisor UI can also run under older versions of Home Assistant.
        // So here we are going to translate toggle events into the appropriate
        // open and close events. These events are a no-op in newer versions of
        // Home Assistant.

        this.addEventListener("hass-toggle-menu", function () {
          Object(fire_event["a" /* fireEvent */])(window.parent.customPanel, // @ts-ignore
          _this3.hass.dockedSidebar ? "hass-close-menu" : "hass-open-menu");
        }); // Paulus - March 19, 2019
        // We changed the navigate event to fire directly on the window, as that's
        // where we are listening for it. However, the older panel_custom will
        // listen on this element for navigation events, so we need to forward them.

        window.addEventListener("location-changed", function (ev) {
          return (// @ts-ignore
            Object(fire_event["a" /* fireEvent */])(_this3, ev.type, ev.detail, {
              bubbles: false
            })
          );
        }); // Forward haptic events to parent window.

        window.addEventListener("haptic", function (ev) {
          // @ts-ignore
          Object(fire_event["a" /* fireEvent */])(window.parent, ev.type, ev.detail, {
            bubbles: false
          });
        });
        makeDialogManager(this, document.body);
      }
    }, {
      kind: "method",
      key: "updatePageEl",
      value: function updatePageEl(el) {
        // the tabs page does its own routing so needs full route.
        var route = el.nodeName === "HASSIO-PANEL" ? this.route : this.routeTail;

        if ("setProperties" in el) {
          // As long as we have Polymer pages
          el.setProperties({
            hass: this.hass,
            narrow: this.narrow,
            supervisorInfo: this._supervisorInfo,
            hostInfo: this._hostInfo,
            hassInfo: this._hassInfo,
            hassOsInfo: this._hassOsInfo,
            route: route
          });
        } else {
          el.hass = this.hass;
          el.narrow = this.narrow;
          el.supervisorInfo = this._supervisorInfo;
          el.hostInfo = this._hostInfo;
          el.hassInfo = this._hassInfo;
          el.hassOsInfo = this._hassOsInfo;
          el.route = route;
        }
      }
    }, {
      kind: "method",
      key: "_fetchData",
      value: function () {
        var _fetchData2 = hassio_main_asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee() {
          var _yield$Promise$all, _yield$Promise$all2, supervisorInfo, hostInfo, hassInfo;

          return regeneratorRuntime.wrap(function _callee$(_context) {
            while (1) {
              switch (_context.prev = _context.next) {
                case 0:
                  if (!(this.panel.config && this.panel.config.ingress)) {
                    _context.next = 4;
                    break;
                  }

                  _context.next = 3;
                  return this._redirectIngress(this.panel.config.ingress);

                case 3:
                  return _context.abrupt("return");

                case 4:
                  _context.next = 6;
                  return Promise.all([Object(supervisor["d" /* fetchHassioSupervisorInfo */])(this.hass), fetchHassioHostInfo(this.hass), Object(supervisor["b" /* fetchHassioHomeAssistantInfo */])(this.hass)]);

                case 6:
                  _yield$Promise$all = _context.sent;
                  _yield$Promise$all2 = hassio_main_slicedToArray(_yield$Promise$all, 3);
                  supervisorInfo = _yield$Promise$all2[0];
                  hostInfo = _yield$Promise$all2[1];
                  hassInfo = _yield$Promise$all2[2];
                  this._supervisorInfo = supervisorInfo;
                  this._hostInfo = hostInfo;
                  this._hassInfo = hassInfo;

                  if (!(this._hostInfo.features && this._hostInfo.features.includes("hassos"))) {
                    _context.next = 18;
                    break;
                  }

                  _context.next = 17;
                  return fetchHassioHassOsInfo(this.hass);

                case 17:
                  this._hassOsInfo = _context.sent;

                case 18:
                case "end":
                  return _context.stop();
              }
            }
          }, _callee, this);
        }));

        function _fetchData() {
          return _fetchData2.apply(this, arguments);
        }

        return _fetchData;
      }()
    }, {
      kind: "method",
      key: "_redirectIngress",
      value: function () {
        var _redirectIngress2 = hassio_main_asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee3(addonSlug) {
          var _this4 = this;

          var awaitAlert, createSessionPromise, addon;
          return regeneratorRuntime.wrap(function _callee3$(_context3) {
            while (1) {
              switch (_context3.prev = _context3.next) {
                case 0:
                  // When we trigger a navigation, we sleep to make sure we don't
                  // show the hassio dashboard before navigating away.
                  awaitAlert = /*#__PURE__*/function () {
                    var _ref = hassio_main_asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee2(alertParams, action) {
                      return regeneratorRuntime.wrap(function _callee2$(_context2) {
                        while (1) {
                          switch (_context2.prev = _context2.next) {
                            case 0:
                              _context2.next = 2;
                              return new Promise(function (resolve) {
                                alertParams.confirm = resolve;
                                Object(show_dialog_box["a" /* showAlertDialog */])(_this4, alertParams);
                              });

                            case 2:
                              action();
                              _context2.next = 5;
                              return new Promise(function (resolve) {
                                return setTimeout(resolve, 1000);
                              });

                            case 5:
                            case "end":
                              return _context2.stop();
                          }
                        }
                      }, _callee2);
                    }));

                    return function awaitAlert(_x2, _x3) {
                      return _ref.apply(this, arguments);
                    };
                  }();

                  createSessionPromise = Object(supervisor["a" /* createHassioSession */])(this.hass).then(function () {
                    return true;
                  }, function () {
                    return false;
                  });
                  _context3.prev = 2;
                  _context3.next = 5;
                  return Object(hassio_addon["c" /* fetchHassioAddonInfo */])(this.hass, addonSlug);

                case 5:
                  addon = _context3.sent;
                  _context3.next = 13;
                  break;

                case 8:
                  _context3.prev = 8;
                  _context3.t0 = _context3["catch"](2);
                  _context3.next = 12;
                  return awaitAlert({
                    text: "Unable to fetch add-on info to start Ingress",
                    title: "Supervisor"
                  }, function () {
                    return history.back();
                  });

                case 12:
                  return _context3.abrupt("return");

                case 13:
                  if (addon.ingress_url) {
                    _context3.next = 17;
                    break;
                  }

                  _context3.next = 16;
                  return awaitAlert({
                    text: "Add-on does not support Ingress",
                    title: addon.name
                  }, function () {
                    return history.back();
                  });

                case 16:
                  return _context3.abrupt("return");

                case 17:
                  if (!(addon.state !== "started")) {
                    _context3.next = 21;
                    break;
                  }

                  _context3.next = 20;
                  return awaitAlert({
                    text: "Add-on is not running. Please start it first",
                    title: addon.name
                  }, function () {
                    return Object(common_navigate["a" /* navigate */])(_this4, "/hassio/addon/".concat(addon.slug, "/info"), true);
                  });

                case 20:
                  return _context3.abrupt("return");

                case 21:
                  _context3.next = 23;
                  return createSessionPromise;

                case 23:
                  if (_context3.sent) {
                    _context3.next = 27;
                    break;
                  }

                  _context3.next = 26;
                  return awaitAlert({
                    text: "Unable to create an Ingress session",
                    title: addon.name
                  }, function () {
                    return history.back();
                  });

                case 26:
                  return _context3.abrupt("return");

                case 27:
                  location.assign(addon.ingress_url); // await a promise that doesn't resolve, so we show the loading screen
                  // while we load the next page.

                  _context3.next = 30;
                  return new Promise(function () {
                    return undefined;
                  });

                case 30:
                case "end":
                  return _context3.stop();
              }
            }
          }, _callee3, this, [[2, 8]]);
        }));

        function _redirectIngress(_x) {
          return _redirectIngress2.apply(this, arguments);
        }

        return _redirectIngress;
      }()
    }, {
      kind: "method",
      key: "_apiCalled",
      value: function _apiCalled(ev) {
        var _this5 = this;

        if (!ev.detail.success) {
          return;
        }

        var tries = 1;

        var tryUpdate = function tryUpdate() {
          _this5._fetchData()["catch"](function () {
            tries += 1;
            setTimeout(tryUpdate, Math.min(tries, 5) * 1000);
          });
        };

        tryUpdate();
      }
    }]
  };
}, ProvideHassLitMixin(hass_router_page["a" /* HassRouterPage */]));

/***/ }),

/***/ 32:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";

// EXTERNAL MODULE: ./node_modules/@polymer/iron-icon/iron-icon.js
var iron_icon = __webpack_require__(107);

// EXTERNAL MODULE: ./node_modules/idb-keyval/dist/idb-keyval.mjs
var idb_keyval = __webpack_require__(142);

// EXTERNAL MODULE: ./node_modules/lit-element/lit-element.js + 3 modules
var lit_element = __webpack_require__(5);

// CONCATENATED MODULE: ./src/components/ha-svg-icon.ts
function _typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { _typeof = function _typeof(obj) { return typeof obj; }; } else { _typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return _typeof(obj); }

function _templateObject3() {
  var data = _taggedTemplateLiteral(["\n      :host {\n        display: var(--ha-icon-display, inline-flex);\n        align-items: center;\n        justify-content: center;\n        position: relative;\n        vertical-align: middle;\n        fill: currentcolor;\n        width: var(--mdc-icon-size, 24px);\n        height: var(--mdc-icon-size, 24px);\n      }\n      svg {\n        width: 100%;\n        height: 100%;\n        pointer-events: none;\n        display: block;\n      }\n    "]);

  _templateObject3 = function _templateObject3() {
    return data;
  };

  return data;
}

function _templateObject2() {
  var data = _taggedTemplateLiteral(["<path d=", "></path>"]);

  _templateObject2 = function _templateObject2() {
    return data;
  };

  return data;
}

function _templateObject() {
  var data = _taggedTemplateLiteral(["\n    <svg \n      viewBox=\"0 0 24 24\" \n      preserveAspectRatio=\"xMidYMid meet\"\n      focusable=\"false\">\n      <g>\n      ", "\n      </g>\n    </svg>"]);

  _templateObject = function _templateObject() {
    return data;
  };

  return data;
}

function _taggedTemplateLiteral(strings, raw) { if (!raw) { raw = strings.slice(0); } return Object.freeze(Object.defineProperties(strings, { raw: { value: Object.freeze(raw) } })); }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) _setPrototypeOf(subClass, superClass); }

function _setPrototypeOf(o, p) { _setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return _setPrototypeOf(o, p); }

function _createSuper(Derived) { return function () { var Super = _getPrototypeOf(Derived), result; if (_isNativeReflectConstruct()) { var NewTarget = _getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return _possibleConstructorReturn(this, result); }; }

function _possibleConstructorReturn(self, call) { if (call && (_typeof(call) === "object" || typeof call === "function")) { return call; } return _assertThisInitialized(self); }

function _assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function _isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Date.prototype.toString.call(Reflect.construct(Date, [], function () {})); return true; } catch (e) { return false; } }

function _getPrototypeOf(o) { _getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return _getPrototypeOf(o); }

function _decorate(decorators, factory, superClass, mixins) { var api = _getDecoratorsApi(); if (mixins) { for (var i = 0; i < mixins.length; i++) { api = mixins[i](api); } } var r = factory(function initialize(O) { api.initializeInstanceElements(O, decorated.elements); }, superClass); var decorated = api.decorateClass(_coalesceClassElements(r.d.map(_createElementDescriptor)), decorators); api.initializeClassElements(r.F, decorated.elements); return api.runClassFinishers(r.F, decorated.finishers); }

function _getDecoratorsApi() { _getDecoratorsApi = function _getDecoratorsApi() { return api; }; var api = { elementsDefinitionOrder: [["method"], ["field"]], initializeInstanceElements: function initializeInstanceElements(O, elements) { ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { if (element.kind === kind && element.placement === "own") { this.defineClassElement(O, element); } }, this); }, this); }, initializeClassElements: function initializeClassElements(F, elements) { var proto = F.prototype; ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { var placement = element.placement; if (element.kind === kind && (placement === "static" || placement === "prototype")) { var receiver = placement === "static" ? F : proto; this.defineClassElement(receiver, element); } }, this); }, this); }, defineClassElement: function defineClassElement(receiver, element) { var descriptor = element.descriptor; if (element.kind === "field") { var initializer = element.initializer; descriptor = { enumerable: descriptor.enumerable, writable: descriptor.writable, configurable: descriptor.configurable, value: initializer === void 0 ? void 0 : initializer.call(receiver) }; } Object.defineProperty(receiver, element.key, descriptor); }, decorateClass: function decorateClass(elements, decorators) { var newElements = []; var finishers = []; var placements = { "static": [], prototype: [], own: [] }; elements.forEach(function (element) { this.addElementPlacement(element, placements); }, this); elements.forEach(function (element) { if (!_hasDecorators(element)) return newElements.push(element); var elementFinishersExtras = this.decorateElement(element, placements); newElements.push(elementFinishersExtras.element); newElements.push.apply(newElements, elementFinishersExtras.extras); finishers.push.apply(finishers, elementFinishersExtras.finishers); }, this); if (!decorators) { return { elements: newElements, finishers: finishers }; } var result = this.decorateConstructor(newElements, decorators); finishers.push.apply(finishers, result.finishers); result.finishers = finishers; return result; }, addElementPlacement: function addElementPlacement(element, placements, silent) { var keys = placements[element.placement]; if (!silent && keys.indexOf(element.key) !== -1) { throw new TypeError("Duplicated element (" + element.key + ")"); } keys.push(element.key); }, decorateElement: function decorateElement(element, placements) { var extras = []; var finishers = []; for (var decorators = element.decorators, i = decorators.length - 1; i >= 0; i--) { var keys = placements[element.placement]; keys.splice(keys.indexOf(element.key), 1); var elementObject = this.fromElementDescriptor(element); var elementFinisherExtras = this.toElementFinisherExtras((0, decorators[i])(elementObject) || elementObject); element = elementFinisherExtras.element; this.addElementPlacement(element, placements); if (elementFinisherExtras.finisher) { finishers.push(elementFinisherExtras.finisher); } var newExtras = elementFinisherExtras.extras; if (newExtras) { for (var j = 0; j < newExtras.length; j++) { this.addElementPlacement(newExtras[j], placements); } extras.push.apply(extras, newExtras); } } return { element: element, finishers: finishers, extras: extras }; }, decorateConstructor: function decorateConstructor(elements, decorators) { var finishers = []; for (var i = decorators.length - 1; i >= 0; i--) { var obj = this.fromClassDescriptor(elements); var elementsAndFinisher = this.toClassDescriptor((0, decorators[i])(obj) || obj); if (elementsAndFinisher.finisher !== undefined) { finishers.push(elementsAndFinisher.finisher); } if (elementsAndFinisher.elements !== undefined) { elements = elementsAndFinisher.elements; for (var j = 0; j < elements.length - 1; j++) { for (var k = j + 1; k < elements.length; k++) { if (elements[j].key === elements[k].key && elements[j].placement === elements[k].placement) { throw new TypeError("Duplicated element (" + elements[j].key + ")"); } } } } } return { elements: elements, finishers: finishers }; }, fromElementDescriptor: function fromElementDescriptor(element) { var obj = { kind: element.kind, key: element.key, placement: element.placement, descriptor: element.descriptor }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); if (element.kind === "field") obj.initializer = element.initializer; return obj; }, toElementDescriptors: function toElementDescriptors(elementObjects) { if (elementObjects === undefined) return; return _toArray(elementObjects).map(function (elementObject) { var element = this.toElementDescriptor(elementObject); this.disallowProperty(elementObject, "finisher", "An element descriptor"); this.disallowProperty(elementObject, "extras", "An element descriptor"); return element; }, this); }, toElementDescriptor: function toElementDescriptor(elementObject) { var kind = String(elementObject.kind); if (kind !== "method" && kind !== "field") { throw new TypeError('An element descriptor\'s .kind property must be either "method" or' + ' "field", but a decorator created an element descriptor with' + ' .kind "' + kind + '"'); } var key = _toPropertyKey(elementObject.key); var placement = String(elementObject.placement); if (placement !== "static" && placement !== "prototype" && placement !== "own") { throw new TypeError('An element descriptor\'s .placement property must be one of "static",' + ' "prototype" or "own", but a decorator created an element descriptor' + ' with .placement "' + placement + '"'); } var descriptor = elementObject.descriptor; this.disallowProperty(elementObject, "elements", "An element descriptor"); var element = { kind: kind, key: key, placement: placement, descriptor: Object.assign({}, descriptor) }; if (kind !== "field") { this.disallowProperty(elementObject, "initializer", "A method descriptor"); } else { this.disallowProperty(descriptor, "get", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "set", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "value", "The property descriptor of a field descriptor"); element.initializer = elementObject.initializer; } return element; }, toElementFinisherExtras: function toElementFinisherExtras(elementObject) { var element = this.toElementDescriptor(elementObject); var finisher = _optionalCallableProperty(elementObject, "finisher"); var extras = this.toElementDescriptors(elementObject.extras); return { element: element, finisher: finisher, extras: extras }; }, fromClassDescriptor: function fromClassDescriptor(elements) { var obj = { kind: "class", elements: elements.map(this.fromElementDescriptor, this) }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); return obj; }, toClassDescriptor: function toClassDescriptor(obj) { var kind = String(obj.kind); if (kind !== "class") { throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator' + ' created a class descriptor with .kind "' + kind + '"'); } this.disallowProperty(obj, "key", "A class descriptor"); this.disallowProperty(obj, "placement", "A class descriptor"); this.disallowProperty(obj, "descriptor", "A class descriptor"); this.disallowProperty(obj, "initializer", "A class descriptor"); this.disallowProperty(obj, "extras", "A class descriptor"); var finisher = _optionalCallableProperty(obj, "finisher"); var elements = this.toElementDescriptors(obj.elements); return { elements: elements, finisher: finisher }; }, runClassFinishers: function runClassFinishers(constructor, finishers) { for (var i = 0; i < finishers.length; i++) { var newConstructor = (0, finishers[i])(constructor); if (newConstructor !== undefined) { if (typeof newConstructor !== "function") { throw new TypeError("Finishers must return a constructor."); } constructor = newConstructor; } } return constructor; }, disallowProperty: function disallowProperty(obj, name, objectType) { if (obj[name] !== undefined) { throw new TypeError(objectType + " can't have a ." + name + " property."); } } }; return api; }

function _createElementDescriptor(def) { var key = _toPropertyKey(def.key); var descriptor; if (def.kind === "method") { descriptor = { value: def.value, writable: true, configurable: true, enumerable: false }; } else if (def.kind === "get") { descriptor = { get: def.value, configurable: true, enumerable: false }; } else if (def.kind === "set") { descriptor = { set: def.value, configurable: true, enumerable: false }; } else if (def.kind === "field") { descriptor = { configurable: true, writable: true, enumerable: true }; } var element = { kind: def.kind === "field" ? "field" : "method", key: key, placement: def["static"] ? "static" : def.kind === "field" ? "own" : "prototype", descriptor: descriptor }; if (def.decorators) element.decorators = def.decorators; if (def.kind === "field") element.initializer = def.value; return element; }

function _coalesceGetterSetter(element, other) { if (element.descriptor.get !== undefined) { other.descriptor.get = element.descriptor.get; } else { other.descriptor.set = element.descriptor.set; } }

function _coalesceClassElements(elements) { var newElements = []; var isSameElement = function isSameElement(other) { return other.kind === "method" && other.key === element.key && other.placement === element.placement; }; for (var i = 0; i < elements.length; i++) { var element = elements[i]; var other; if (element.kind === "method" && (other = newElements.find(isSameElement))) { if (_isDataDescriptor(element.descriptor) || _isDataDescriptor(other.descriptor)) { if (_hasDecorators(element) || _hasDecorators(other)) { throw new ReferenceError("Duplicated methods (" + element.key + ") can't be decorated."); } other.descriptor = element.descriptor; } else { if (_hasDecorators(element)) { if (_hasDecorators(other)) { throw new ReferenceError("Decorators can't be placed on different accessors with for " + "the same property (" + element.key + ")."); } other.decorators = element.decorators; } _coalesceGetterSetter(element, other); } } else { newElements.push(element); } } return newElements; }

function _hasDecorators(element) { return element.decorators && element.decorators.length; }

function _isDataDescriptor(desc) { return desc !== undefined && !(desc.value === undefined && desc.writable === undefined); }

function _optionalCallableProperty(obj, name) { var value = obj[name]; if (value !== undefined && typeof value !== "function") { throw new TypeError("Expected '" + name + "' to be a function"); } return value; }

function _toPropertyKey(arg) { var key = _toPrimitive(arg, "string"); return _typeof(key) === "symbol" ? key : String(key); }

function _toPrimitive(input, hint) { if (_typeof(input) !== "object" || input === null) return input; var prim = input[Symbol.toPrimitive]; if (prim !== undefined) { var res = prim.call(input, hint || "default"); if (_typeof(res) !== "object") return res; throw new TypeError("@@toPrimitive must return a primitive value."); } return (hint === "string" ? String : Number)(input); }

function _toArray(arr) { return _arrayWithHoles(arr) || _iterableToArray(arr) || _unsupportedIterableToArray(arr) || _nonIterableRest(); }

function _nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function _unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return _arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(n); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return _arrayLikeToArray(o, minLen); }

function _arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function _iterableToArray(iter) { if (typeof Symbol !== "undefined" && Symbol.iterator in Object(iter)) return Array.from(iter); }

function _arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }


var ha_svg_icon_HaSvgIcon = _decorate([Object(lit_element["d" /* customElement */])("ha-svg-icon")], function (_initialize, _LitElement) {
  var HaSvgIcon = /*#__PURE__*/function (_LitElement2) {
    _inherits(HaSvgIcon, _LitElement2);

    var _super = _createSuper(HaSvgIcon);

    function HaSvgIcon() {
      var _this;

      _classCallCheck(this, HaSvgIcon);

      for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
        args[_key] = arguments[_key];
      }

      _this = _super.call.apply(_super, [this].concat(args));

      _initialize(_assertThisInitialized(_this));

      return _this;
    }

    return HaSvgIcon;
  }(_LitElement);

  return {
    F: HaSvgIcon,
    d: [{
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "path",
      value: void 0
    }, {
      kind: "method",
      key: "render",
      value: function render() {
        return Object(lit_element["h" /* svg */])(_templateObject(), this.path ? Object(lit_element["h" /* svg */])(_templateObject2(), this.path) : "");
      }
    }, {
      kind: "get",
      "static": true,
      key: "styles",
      value: function styles() {
        return Object(lit_element["c" /* css */])(_templateObject3());
      }
    }]
  };
}, lit_element["a" /* LitElement */]);
// CONCATENATED MODULE: ./src/common/util/debounce.ts
// From: https://davidwalsh.name/javascript-debounce-function
// Returns a function, that, as long as it continues to be invoked, will not
// be triggered. The function will be called after it stops being called for
// N milliseconds. If `immediate` is passed, trigger the function on the
// leading edge, instead of the trailing.
// eslint-disable-next-line: ban-types
var debounce = function debounce(func, wait) {
  var immediate = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : false;
  var timeout; // @ts-ignore

  return function () {
    for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
      args[_key] = arguments[_key];
    }

    // @ts-ignore
    // eslint-disable-next-line @typescript-eslint/no-this-alias
    var context = this;

    var later = function later() {
      timeout = null;

      if (!immediate) {
        func.apply(context, args);
      }
    };

    var callNow = immediate && !timeout;
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);

    if (callNow) {
      func.apply(context, args);
    }
  };
};
// EXTERNAL MODULE: ./build/mdi/iconMetadata.json
var iconMetadata = __webpack_require__(143);

// CONCATENATED MODULE: ./src/resources/icon-metadata.ts

var icon_metadata_iconMetadata = iconMetadata;
// CONCATENATED MODULE: ./src/components/ha-icon.ts
/* unused harmony export HaIcon */
function ha_icon_typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { ha_icon_typeof = function _typeof(obj) { return typeof obj; }; } else { ha_icon_typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return ha_icon_typeof(obj); }

function _templateObject4() {
  var data = ha_icon_taggedTemplateLiteral(["\n      :host {\n        fill: currentcolor;\n      }\n    "]);

  _templateObject4 = function _templateObject4() {
    return data;
  };

  return data;
}

function ha_icon_templateObject3() {
  var data = ha_icon_taggedTemplateLiteral(["<ha-svg-icon .path=", "></ha-svg-icon>"]);

  ha_icon_templateObject3 = function _templateObject3() {
    return data;
  };

  return data;
}

function ha_icon_templateObject2() {
  var data = ha_icon_taggedTemplateLiteral(["<iron-icon .icon=", "></iron-icon>"]);

  ha_icon_templateObject2 = function _templateObject2() {
    return data;
  };

  return data;
}

function ha_icon_templateObject() {
  var data = ha_icon_taggedTemplateLiteral([""]);

  ha_icon_templateObject = function _templateObject() {
    return data;
  };

  return data;
}

function ha_icon_taggedTemplateLiteral(strings, raw) { if (!raw) { raw = strings.slice(0); } return Object.freeze(Object.defineProperties(strings, { raw: { value: Object.freeze(raw) } })); }

function ha_icon_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function ha_icon_inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) ha_icon_setPrototypeOf(subClass, superClass); }

function ha_icon_setPrototypeOf(o, p) { ha_icon_setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return ha_icon_setPrototypeOf(o, p); }

function ha_icon_createSuper(Derived) { return function () { var Super = ha_icon_getPrototypeOf(Derived), result; if (ha_icon_isNativeReflectConstruct()) { var NewTarget = ha_icon_getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return ha_icon_possibleConstructorReturn(this, result); }; }

function ha_icon_possibleConstructorReturn(self, call) { if (call && (ha_icon_typeof(call) === "object" || typeof call === "function")) { return call; } return ha_icon_assertThisInitialized(self); }

function ha_icon_assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function ha_icon_isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Date.prototype.toString.call(Reflect.construct(Date, [], function () {})); return true; } catch (e) { return false; } }

function ha_icon_getPrototypeOf(o) { ha_icon_getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return ha_icon_getPrototypeOf(o); }

function ha_icon_decorate(decorators, factory, superClass, mixins) { var api = ha_icon_getDecoratorsApi(); if (mixins) { for (var i = 0; i < mixins.length; i++) { api = mixins[i](api); } } var r = factory(function initialize(O) { api.initializeInstanceElements(O, decorated.elements); }, superClass); var decorated = api.decorateClass(ha_icon_coalesceClassElements(r.d.map(ha_icon_createElementDescriptor)), decorators); api.initializeClassElements(r.F, decorated.elements); return api.runClassFinishers(r.F, decorated.finishers); }

function ha_icon_getDecoratorsApi() { ha_icon_getDecoratorsApi = function _getDecoratorsApi() { return api; }; var api = { elementsDefinitionOrder: [["method"], ["field"]], initializeInstanceElements: function initializeInstanceElements(O, elements) { ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { if (element.kind === kind && element.placement === "own") { this.defineClassElement(O, element); } }, this); }, this); }, initializeClassElements: function initializeClassElements(F, elements) { var proto = F.prototype; ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { var placement = element.placement; if (element.kind === kind && (placement === "static" || placement === "prototype")) { var receiver = placement === "static" ? F : proto; this.defineClassElement(receiver, element); } }, this); }, this); }, defineClassElement: function defineClassElement(receiver, element) { var descriptor = element.descriptor; if (element.kind === "field") { var initializer = element.initializer; descriptor = { enumerable: descriptor.enumerable, writable: descriptor.writable, configurable: descriptor.configurable, value: initializer === void 0 ? void 0 : initializer.call(receiver) }; } Object.defineProperty(receiver, element.key, descriptor); }, decorateClass: function decorateClass(elements, decorators) { var newElements = []; var finishers = []; var placements = { "static": [], prototype: [], own: [] }; elements.forEach(function (element) { this.addElementPlacement(element, placements); }, this); elements.forEach(function (element) { if (!ha_icon_hasDecorators(element)) return newElements.push(element); var elementFinishersExtras = this.decorateElement(element, placements); newElements.push(elementFinishersExtras.element); newElements.push.apply(newElements, elementFinishersExtras.extras); finishers.push.apply(finishers, elementFinishersExtras.finishers); }, this); if (!decorators) { return { elements: newElements, finishers: finishers }; } var result = this.decorateConstructor(newElements, decorators); finishers.push.apply(finishers, result.finishers); result.finishers = finishers; return result; }, addElementPlacement: function addElementPlacement(element, placements, silent) { var keys = placements[element.placement]; if (!silent && keys.indexOf(element.key) !== -1) { throw new TypeError("Duplicated element (" + element.key + ")"); } keys.push(element.key); }, decorateElement: function decorateElement(element, placements) { var extras = []; var finishers = []; for (var decorators = element.decorators, i = decorators.length - 1; i >= 0; i--) { var keys = placements[element.placement]; keys.splice(keys.indexOf(element.key), 1); var elementObject = this.fromElementDescriptor(element); var elementFinisherExtras = this.toElementFinisherExtras((0, decorators[i])(elementObject) || elementObject); element = elementFinisherExtras.element; this.addElementPlacement(element, placements); if (elementFinisherExtras.finisher) { finishers.push(elementFinisherExtras.finisher); } var newExtras = elementFinisherExtras.extras; if (newExtras) { for (var j = 0; j < newExtras.length; j++) { this.addElementPlacement(newExtras[j], placements); } extras.push.apply(extras, newExtras); } } return { element: element, finishers: finishers, extras: extras }; }, decorateConstructor: function decorateConstructor(elements, decorators) { var finishers = []; for (var i = decorators.length - 1; i >= 0; i--) { var obj = this.fromClassDescriptor(elements); var elementsAndFinisher = this.toClassDescriptor((0, decorators[i])(obj) || obj); if (elementsAndFinisher.finisher !== undefined) { finishers.push(elementsAndFinisher.finisher); } if (elementsAndFinisher.elements !== undefined) { elements = elementsAndFinisher.elements; for (var j = 0; j < elements.length - 1; j++) { for (var k = j + 1; k < elements.length; k++) { if (elements[j].key === elements[k].key && elements[j].placement === elements[k].placement) { throw new TypeError("Duplicated element (" + elements[j].key + ")"); } } } } } return { elements: elements, finishers: finishers }; }, fromElementDescriptor: function fromElementDescriptor(element) { var obj = { kind: element.kind, key: element.key, placement: element.placement, descriptor: element.descriptor }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); if (element.kind === "field") obj.initializer = element.initializer; return obj; }, toElementDescriptors: function toElementDescriptors(elementObjects) { if (elementObjects === undefined) return; return ha_icon_toArray(elementObjects).map(function (elementObject) { var element = this.toElementDescriptor(elementObject); this.disallowProperty(elementObject, "finisher", "An element descriptor"); this.disallowProperty(elementObject, "extras", "An element descriptor"); return element; }, this); }, toElementDescriptor: function toElementDescriptor(elementObject) { var kind = String(elementObject.kind); if (kind !== "method" && kind !== "field") { throw new TypeError('An element descriptor\'s .kind property must be either "method" or' + ' "field", but a decorator created an element descriptor with' + ' .kind "' + kind + '"'); } var key = ha_icon_toPropertyKey(elementObject.key); var placement = String(elementObject.placement); if (placement !== "static" && placement !== "prototype" && placement !== "own") { throw new TypeError('An element descriptor\'s .placement property must be one of "static",' + ' "prototype" or "own", but a decorator created an element descriptor' + ' with .placement "' + placement + '"'); } var descriptor = elementObject.descriptor; this.disallowProperty(elementObject, "elements", "An element descriptor"); var element = { kind: kind, key: key, placement: placement, descriptor: Object.assign({}, descriptor) }; if (kind !== "field") { this.disallowProperty(elementObject, "initializer", "A method descriptor"); } else { this.disallowProperty(descriptor, "get", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "set", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "value", "The property descriptor of a field descriptor"); element.initializer = elementObject.initializer; } return element; }, toElementFinisherExtras: function toElementFinisherExtras(elementObject) { var element = this.toElementDescriptor(elementObject); var finisher = ha_icon_optionalCallableProperty(elementObject, "finisher"); var extras = this.toElementDescriptors(elementObject.extras); return { element: element, finisher: finisher, extras: extras }; }, fromClassDescriptor: function fromClassDescriptor(elements) { var obj = { kind: "class", elements: elements.map(this.fromElementDescriptor, this) }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); return obj; }, toClassDescriptor: function toClassDescriptor(obj) { var kind = String(obj.kind); if (kind !== "class") { throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator' + ' created a class descriptor with .kind "' + kind + '"'); } this.disallowProperty(obj, "key", "A class descriptor"); this.disallowProperty(obj, "placement", "A class descriptor"); this.disallowProperty(obj, "descriptor", "A class descriptor"); this.disallowProperty(obj, "initializer", "A class descriptor"); this.disallowProperty(obj, "extras", "A class descriptor"); var finisher = ha_icon_optionalCallableProperty(obj, "finisher"); var elements = this.toElementDescriptors(obj.elements); return { elements: elements, finisher: finisher }; }, runClassFinishers: function runClassFinishers(constructor, finishers) { for (var i = 0; i < finishers.length; i++) { var newConstructor = (0, finishers[i])(constructor); if (newConstructor !== undefined) { if (typeof newConstructor !== "function") { throw new TypeError("Finishers must return a constructor."); } constructor = newConstructor; } } return constructor; }, disallowProperty: function disallowProperty(obj, name, objectType) { if (obj[name] !== undefined) { throw new TypeError(objectType + " can't have a ." + name + " property."); } } }; return api; }

function ha_icon_createElementDescriptor(def) { var key = ha_icon_toPropertyKey(def.key); var descriptor; if (def.kind === "method") { descriptor = { value: def.value, writable: true, configurable: true, enumerable: false }; } else if (def.kind === "get") { descriptor = { get: def.value, configurable: true, enumerable: false }; } else if (def.kind === "set") { descriptor = { set: def.value, configurable: true, enumerable: false }; } else if (def.kind === "field") { descriptor = { configurable: true, writable: true, enumerable: true }; } var element = { kind: def.kind === "field" ? "field" : "method", key: key, placement: def["static"] ? "static" : def.kind === "field" ? "own" : "prototype", descriptor: descriptor }; if (def.decorators) element.decorators = def.decorators; if (def.kind === "field") element.initializer = def.value; return element; }

function ha_icon_coalesceGetterSetter(element, other) { if (element.descriptor.get !== undefined) { other.descriptor.get = element.descriptor.get; } else { other.descriptor.set = element.descriptor.set; } }

function ha_icon_coalesceClassElements(elements) { var newElements = []; var isSameElement = function isSameElement(other) { return other.kind === "method" && other.key === element.key && other.placement === element.placement; }; for (var i = 0; i < elements.length; i++) { var element = elements[i]; var other; if (element.kind === "method" && (other = newElements.find(isSameElement))) { if (ha_icon_isDataDescriptor(element.descriptor) || ha_icon_isDataDescriptor(other.descriptor)) { if (ha_icon_hasDecorators(element) || ha_icon_hasDecorators(other)) { throw new ReferenceError("Duplicated methods (" + element.key + ") can't be decorated."); } other.descriptor = element.descriptor; } else { if (ha_icon_hasDecorators(element)) { if (ha_icon_hasDecorators(other)) { throw new ReferenceError("Decorators can't be placed on different accessors with for " + "the same property (" + element.key + ")."); } other.decorators = element.decorators; } ha_icon_coalesceGetterSetter(element, other); } } else { newElements.push(element); } } return newElements; }

function ha_icon_hasDecorators(element) { return element.decorators && element.decorators.length; }

function ha_icon_isDataDescriptor(desc) { return desc !== undefined && !(desc.value === undefined && desc.writable === undefined); }

function ha_icon_optionalCallableProperty(obj, name) { var value = obj[name]; if (value !== undefined && typeof value !== "function") { throw new TypeError("Expected '" + name + "' to be a function"); } return value; }

function ha_icon_toPropertyKey(arg) { var key = ha_icon_toPrimitive(arg, "string"); return ha_icon_typeof(key) === "symbol" ? key : String(key); }

function ha_icon_toPrimitive(input, hint) { if (ha_icon_typeof(input) !== "object" || input === null) return input; var prim = input[Symbol.toPrimitive]; if (prim !== undefined) { var res = prim.call(input, hint || "default"); if (ha_icon_typeof(res) !== "object") return res; throw new TypeError("@@toPrimitive must return a primitive value."); } return (hint === "string" ? String : Number)(input); }

function ha_icon_toArray(arr) { return ha_icon_arrayWithHoles(arr) || ha_icon_iterableToArray(arr) || ha_icon_unsupportedIterableToArray(arr) || ha_icon_nonIterableRest(); }

function ha_icon_iterableToArray(iter) { if (typeof Symbol !== "undefined" && Symbol.iterator in Object(iter)) return Array.from(iter); }

function asyncGeneratorStep(gen, resolve, reject, _next, _throw, key, arg) { try { var info = gen[key](arg); var value = info.value; } catch (error) { reject(error); return; } if (info.done) { resolve(value); } else { Promise.resolve(value).then(_next, _throw); } }

function _asyncToGenerator(fn) { return function () { var self = this, args = arguments; return new Promise(function (resolve, reject) { var gen = fn.apply(self, args); function _next(value) { asyncGeneratorStep(gen, resolve, reject, _next, _throw, "next", value); } function _throw(err) { asyncGeneratorStep(gen, resolve, reject, _next, _throw, "throw", err); } _next(undefined); }); }; }

function _slicedToArray(arr, i) { return ha_icon_arrayWithHoles(arr) || _iterableToArrayLimit(arr, i) || ha_icon_unsupportedIterableToArray(arr, i) || ha_icon_nonIterableRest(); }

function ha_icon_nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function _iterableToArrayLimit(arr, i) { if (typeof Symbol === "undefined" || !(Symbol.iterator in Object(arr))) return; var _arr = []; var _n = true; var _d = false; var _e = undefined; try { for (var _i = arr[Symbol.iterator](), _s; !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i["return"] != null) _i["return"](); } finally { if (_d) throw _e; } } return _arr; }

function ha_icon_arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }

function _createForOfIteratorHelper(o) { if (typeof Symbol === "undefined" || o[Symbol.iterator] == null) { if (Array.isArray(o) || (o = ha_icon_unsupportedIterableToArray(o))) { var i = 0; var F = function F() {}; return { s: F, n: function n() { if (i >= o.length) return { done: true }; return { done: false, value: o[i++] }; }, e: function e(_e2) { throw _e2; }, f: F }; } throw new TypeError("Invalid attempt to iterate non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); } var it, normalCompletion = true, didErr = false, err; return { s: function s() { it = o[Symbol.iterator](); }, n: function n() { var step = it.next(); normalCompletion = step.done; return step; }, e: function e(_e3) { didErr = true; err = _e3; }, f: function f() { try { if (!normalCompletion && it["return"] != null) it["return"](); } finally { if (didErr) throw err; } } }; }

function ha_icon_unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return ha_icon_arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(n); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return ha_icon_arrayLikeToArray(o, minLen); }

function ha_icon_arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }







var iconStore = new idb_keyval["a" /* Store */]("hass-icon-db", "mdi-icon-store");
Object(idb_keyval["c" /* get */])("_version", iconStore).then(function (version) {
  if (!version) {
    Object(idb_keyval["d" /* set */])("_version", icon_metadata_iconMetadata.version, iconStore);
  } else if (version !== icon_metadata_iconMetadata.version) {
    Object(idb_keyval["b" /* clear */])(iconStore).then(function () {
      return Object(idb_keyval["d" /* set */])("_version", icon_metadata_iconMetadata.version, iconStore);
    });
  }
});
var chunks = {};
var MDI_PREFIXES = ["mdi", "hass", "hassio", "hademo"];
var toRead = []; // Queue up as many icon fetches in 1 transaction

var getIcon = function getIcon(iconName) {
  return new Promise(function (resolve) {
    toRead.push([iconName, resolve]);

    if (toRead.length > 1) {
      return;
    }

    var results = [];

    iconStore._withIDBStore("readonly", function (store) {
      var _iterator = _createForOfIteratorHelper(toRead),
          _step;

      try {
        for (_iterator.s(); !(_step = _iterator.n()).done;) {
          var _step$value = _slicedToArray(_step.value, 2),
              iconName_ = _step$value[0],
              resolve_ = _step$value[1];

          results.push([resolve_, store.get(iconName_)]);
        }
      } catch (err) {
        _iterator.e(err);
      } finally {
        _iterator.f();
      }

      toRead = [];
    }).then(function () {
      var _iterator2 = _createForOfIteratorHelper(results),
          _step2;

      try {
        for (_iterator2.s(); !(_step2 = _iterator2.n()).done;) {
          var _step2$value = _slicedToArray(_step2.value, 2),
              resolve_ = _step2$value[0],
              request = _step2$value[1];

          resolve_(request.result);
        }
      } catch (err) {
        _iterator2.e(err);
      } finally {
        _iterator2.f();
      }
    });
  });
};

var ha_icon_findIconChunk = function findIconChunk(icon) {
  var lastChunk;

  var _iterator3 = _createForOfIteratorHelper(icon_metadata_iconMetadata.parts),
      _step3;

  try {
    for (_iterator3.s(); !(_step3 = _iterator3.n()).done;) {
      var chunk = _step3.value;

      if (chunk.start !== undefined && icon < chunk.start) {
        break;
      }

      lastChunk = chunk;
    }
  } catch (err) {
    _iterator3.e(err);
  } finally {
    _iterator3.f();
  }

  return lastChunk.file;
};

var debouncedWriteCache = debounce( /*#__PURE__*/_asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee() {
  var keys, iconsSets;
  return regeneratorRuntime.wrap(function _callee$(_context) {
    while (1) {
      switch (_context.prev = _context.next) {
        case 0:
          keys = Object.keys(chunks);
          _context.next = 3;
          return Promise.all(Object.values(chunks));

        case 3:
          iconsSets = _context.sent;

          // We do a batch opening the store just once, for (considerable) performance
          iconStore._withIDBStore("readwrite", function (store) {
            iconsSets.forEach(function (icons, idx) {
              Object.entries(icons).forEach(function (_ref2) {
                var _ref3 = _slicedToArray(_ref2, 2),
                    name = _ref3[0],
                    path = _ref3[1];

                store.put(path, name);
              });
              delete chunks[keys[idx]];
            });
          });

        case 5:
        case "end":
          return _context.stop();
      }
    }
  }, _callee);
})), 2000);
var ha_icon_HaIcon = ha_icon_decorate([Object(lit_element["d" /* customElement */])("ha-icon")], function (_initialize, _LitElement) {
  var HaIcon = /*#__PURE__*/function (_LitElement2) {
    ha_icon_inherits(HaIcon, _LitElement2);

    var _super = ha_icon_createSuper(HaIcon);

    function HaIcon() {
      var _this;

      ha_icon_classCallCheck(this, HaIcon);

      for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
        args[_key] = arguments[_key];
      }

      _this = _super.call.apply(_super, [this].concat(args));

      _initialize(ha_icon_assertThisInitialized(_this));

      return _this;
    }

    return HaIcon;
  }(_LitElement);

  return {
    F: HaIcon,
    d: [{
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "icon",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "_path",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "_noMdi",
      value: function value() {
        return false;
      }
    }, {
      kind: "method",
      key: "updated",
      value: function updated(changedProps) {
        if (changedProps.has("icon")) {
          this._path = undefined;

          this._loadIcon();
        }
      }
    }, {
      kind: "method",
      key: "render",
      value: function render() {
        if (!this.icon) {
          return Object(lit_element["e" /* html */])(ha_icon_templateObject());
        }

        if (this._noMdi) {
          return Object(lit_element["e" /* html */])(ha_icon_templateObject2(), this.icon);
        }

        return Object(lit_element["e" /* html */])(ha_icon_templateObject3(), this._path);
      }
    }, {
      kind: "method",
      key: "_loadIcon",
      value: function () {
        var _loadIcon2 = _asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee2() {
          var icon, iconName, cachedPath, chunk, iconPromise;
          return regeneratorRuntime.wrap(function _callee2$(_context2) {
            while (1) {
              switch (_context2.prev = _context2.next) {
                case 0:
                  if (this.icon) {
                    _context2.next = 2;
                    break;
                  }

                  return _context2.abrupt("return");

                case 2:
                  icon = this.icon.split(":", 2);

                  if (MDI_PREFIXES.includes(icon[0])) {
                    _context2.next = 6;
                    break;
                  }

                  this._noMdi = true;
                  return _context2.abrupt("return");

                case 6:
                  this._noMdi = false;
                  iconName = icon[1];
                  _context2.next = 10;
                  return getIcon(iconName);

                case 10:
                  cachedPath = _context2.sent;

                  if (!cachedPath) {
                    _context2.next = 14;
                    break;
                  }

                  this._path = cachedPath;
                  return _context2.abrupt("return");

                case 14:
                  chunk = ha_icon_findIconChunk(iconName);

                  if (!(chunk in chunks)) {
                    _context2.next = 18;
                    break;
                  }

                  this._setPath(chunks[chunk], iconName);

                  return _context2.abrupt("return");

                case 18:
                  iconPromise = fetch("/static/mdi/".concat(chunk, ".json")).then(function (response) {
                    return response.json();
                  });
                  chunks[chunk] = iconPromise;

                  this._setPath(iconPromise, iconName);

                  debouncedWriteCache();

                case 22:
                case "end":
                  return _context2.stop();
              }
            }
          }, _callee2, this);
        }));

        function _loadIcon() {
          return _loadIcon2.apply(this, arguments);
        }

        return _loadIcon;
      }()
    }, {
      kind: "method",
      key: "_setPath",
      value: function () {
        var _setPath2 = _asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee3(promise, iconName) {
          var iconPack;
          return regeneratorRuntime.wrap(function _callee3$(_context3) {
            while (1) {
              switch (_context3.prev = _context3.next) {
                case 0:
                  _context3.next = 2;
                  return promise;

                case 2:
                  iconPack = _context3.sent;
                  this._path = iconPack[iconName];

                case 4:
                case "end":
                  return _context3.stop();
              }
            }
          }, _callee3, this);
        }));

        function _setPath(_x, _x2) {
          return _setPath2.apply(this, arguments);
        }

        return _setPath;
      }()
    }, {
      kind: "get",
      "static": true,
      key: "styles",
      value: function styles() {
        return Object(lit_element["c" /* css */])(_templateObject4());
      }
    }]
  };
}, lit_element["a" /* LitElement */]);

/***/ }),

/***/ 38:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "a", function() { return navigate; });
/* harmony import */ var _dom_fire_event__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(12);

var navigate = function navigate(_node, path) {
  var replace = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : false;

  if (false) {} else if (replace) {
    history.replaceState(null, "", path);
  } else {
    history.pushState(null, "", path);
  }

  Object(_dom_fire_event__WEBPACK_IMPORTED_MODULE_0__[/* fireEvent */ "a"])(window, "location-changed", {
    replace: replace
  });
};

/***/ }),

/***/ 39:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* unused harmony export loadGenericDialog */
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "a", function() { return showAlertDialog; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "b", function() { return showConfirmationDialog; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "c", function() { return showPromptDialog; });
/* harmony import */ var _common_dom_fire_event__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(12);

var loadGenericDialog = function loadGenericDialog() {
  return Promise.all(/* import() | confirmation */[__webpack_require__.e(0), __webpack_require__.e(2)]).then(__webpack_require__.bind(null, 179));
};

var showDialogHelper = function showDialogHelper(element, dialogParams, extra) {
  return new Promise(function (resolve) {
    var origCancel = dialogParams.cancel;
    var origConfirm = dialogParams.confirm;
    Object(_common_dom_fire_event__WEBPACK_IMPORTED_MODULE_0__[/* fireEvent */ "a"])(element, "show-dialog", {
      dialogTag: "dialog-box",
      dialogImport: loadGenericDialog,
      dialogParams: Object.assign({}, dialogParams, {}, extra, {
        cancel: function cancel() {
          resolve((extra === null || extra === void 0 ? void 0 : extra.prompt) ? null : false);

          if (origCancel) {
            origCancel();
          }
        },
        confirm: function confirm(out) {
          resolve((extra === null || extra === void 0 ? void 0 : extra.prompt) ? out : true);

          if (origConfirm) {
            origConfirm(out);
          }
        }
      })
    });
  });
};

var showAlertDialog = function showAlertDialog(element, dialogParams) {
  return showDialogHelper(element, dialogParams);
};
var showConfirmationDialog = function showConfirmationDialog(element, dialogParams) {
  return showDialogHelper(element, dialogParams, {
    confirmation: true
  });
};
var showPromptDialog = function showPromptDialog(element, dialogParams) {
  return showDialogHelper(element, dialogParams, {
    prompt: true
  });
};

/***/ }),

/***/ 48:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "a", function() { return hassioApiResultExtractor; });
var hassioApiResultExtractor = function hassioApiResultExtractor(response) {
  return response.data;
};

/***/ }),

/***/ 49:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "b", function() { return fetchHassioHomeAssistantInfo; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "d", function() { return fetchHassioSupervisorInfo; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "c", function() { return fetchHassioLogs; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "a", function() { return createHassioSession; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "e", function() { return setSupervisorOption; });
/* harmony import */ var _common__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(48);
function asyncGeneratorStep(gen, resolve, reject, _next, _throw, key, arg) { try { var info = gen[key](arg); var value = info.value; } catch (error) { reject(error); return; } if (info.done) { resolve(value); } else { Promise.resolve(value).then(_next, _throw); } }

function _asyncToGenerator(fn) { return function () { var self = this, args = arguments; return new Promise(function (resolve, reject) { var gen = fn.apply(self, args); function _next(value) { asyncGeneratorStep(gen, resolve, reject, _next, _throw, "next", value); } function _throw(err) { asyncGeneratorStep(gen, resolve, reject, _next, _throw, "throw", err); } _next(undefined); }); }; }


var fetchHassioHomeAssistantInfo = /*#__PURE__*/function () {
  var _ref = _asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee(hass) {
    return regeneratorRuntime.wrap(function _callee$(_context) {
      while (1) {
        switch (_context.prev = _context.next) {
          case 0:
            _context.t0 = _common__WEBPACK_IMPORTED_MODULE_0__[/* hassioApiResultExtractor */ "a"];
            _context.next = 3;
            return hass.callApi("GET", "hassio/core/info");

          case 3:
            _context.t1 = _context.sent;
            return _context.abrupt("return", (0, _context.t0)(_context.t1));

          case 5:
          case "end":
            return _context.stop();
        }
      }
    }, _callee);
  }));

  return function fetchHassioHomeAssistantInfo(_x) {
    return _ref.apply(this, arguments);
  };
}();
var fetchHassioSupervisorInfo = /*#__PURE__*/function () {
  var _ref2 = _asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee2(hass) {
    return regeneratorRuntime.wrap(function _callee2$(_context2) {
      while (1) {
        switch (_context2.prev = _context2.next) {
          case 0:
            _context2.t0 = _common__WEBPACK_IMPORTED_MODULE_0__[/* hassioApiResultExtractor */ "a"];
            _context2.next = 3;
            return hass.callApi("GET", "hassio/supervisor/info");

          case 3:
            _context2.t1 = _context2.sent;
            return _context2.abrupt("return", (0, _context2.t0)(_context2.t1));

          case 5:
          case "end":
            return _context2.stop();
        }
      }
    }, _callee2);
  }));

  return function fetchHassioSupervisorInfo(_x2) {
    return _ref2.apply(this, arguments);
  };
}();
var fetchHassioLogs = /*#__PURE__*/function () {
  var _ref3 = _asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee3(hass, provider) {
    return regeneratorRuntime.wrap(function _callee3$(_context3) {
      while (1) {
        switch (_context3.prev = _context3.next) {
          case 0:
            return _context3.abrupt("return", hass.callApi("GET", "hassio/".concat(provider, "/logs")));

          case 1:
          case "end":
            return _context3.stop();
        }
      }
    }, _callee3);
  }));

  return function fetchHassioLogs(_x3, _x4) {
    return _ref3.apply(this, arguments);
  };
}();
var createHassioSession = /*#__PURE__*/function () {
  var _ref4 = _asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee4(hass) {
    var response;
    return regeneratorRuntime.wrap(function _callee4$(_context4) {
      while (1) {
        switch (_context4.prev = _context4.next) {
          case 0:
            _context4.next = 2;
            return hass.callApi("POST", "hassio/ingress/session");

          case 2:
            response = _context4.sent;
            document.cookie = "ingress_session=".concat(response.data.session, ";path=/api/hassio_ingress/");

          case 4:
          case "end":
            return _context4.stop();
        }
      }
    }, _callee4);
  }));

  return function createHassioSession(_x5) {
    return _ref4.apply(this, arguments);
  };
}();
var setSupervisorOption = /*#__PURE__*/function () {
  var _ref5 = _asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee5(hass, data) {
    return regeneratorRuntime.wrap(function _callee5$(_context5) {
      while (1) {
        switch (_context5.prev = _context5.next) {
          case 0:
            _context5.next = 2;
            return hass.callApi("POST", "hassio/supervisor/options", data);

          case 2:
          case "end":
            return _context5.stop();
        }
      }
    }, _callee5);
  }));

  return function setSupervisorOption(_x6, _x7) {
    return _ref5.apply(this, arguments);
  };
}();

/***/ }),

/***/ 56:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";

// EXTERNAL MODULE: ./node_modules/lit-element/lit-element.js + 3 modules
var lit_element = __webpack_require__(5);

// EXTERNAL MODULE: ./node_modules/@polymer/polymer/lib/legacy/polymer.dom.js + 1 modules
var polymer_dom = __webpack_require__(9);

// EXTERNAL MODULE: ./node_modules/@polymer/polymer/polymer-element.js
var polymer_element = __webpack_require__(37);

// CONCATENATED MODULE: ./src/common/datetime/relative_time.ts
/**
 * Calculate a string representing a date object as relative time from now.
 *
 * Example output: 5 minutes ago, in 3 days.
 */
var tests = [60, 60, 24, 7];
var langKey = ["second", "minute", "hour", "day"];
function relativeTime(dateObj, localize) {
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};
  var compareTime = options.compareTime || new Date();
  var delta = (compareTime.getTime() - dateObj.getTime()) / 1000;
  var tense = delta >= 0 ? "past" : "future";
  delta = Math.abs(delta);
  var timeDesc;

  for (var i = 0; i < tests.length; i++) {
    if (delta < tests[i]) {
      delta = Math.floor(delta);
      timeDesc = localize("ui.components.relative_time.duration.".concat(langKey[i]), "count", delta);
      break;
    }

    delta /= tests[i];
  }

  if (timeDesc === undefined) {
    delta = Math.floor(delta);
    timeDesc = localize("ui.components.relative_time.duration.week", "count", delta);
  }

  return options.includeTense === false ? timeDesc : localize("ui.components.relative_time.".concat(tense), "time", timeDesc);
}
// EXTERNAL MODULE: ./node_modules/@polymer/polymer/lib/utils/mixin.js
var mixin = __webpack_require__(19);

// CONCATENATED MODULE: ./src/mixins/localize-mixin.js
function _typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { _typeof = function _typeof(obj) { return typeof obj; }; } else { _typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return _typeof(obj); }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } }

function _createClass(Constructor, protoProps, staticProps) { if (protoProps) _defineProperties(Constructor.prototype, protoProps); if (staticProps) _defineProperties(Constructor, staticProps); return Constructor; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) _setPrototypeOf(subClass, superClass); }

function _setPrototypeOf(o, p) { _setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return _setPrototypeOf(o, p); }

function _createSuper(Derived) { return function () { var Super = _getPrototypeOf(Derived), result; if (_isNativeReflectConstruct()) { var NewTarget = _getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return _possibleConstructorReturn(this, result); }; }

function _possibleConstructorReturn(self, call) { if (call && (_typeof(call) === "object" || typeof call === "function")) { return call; } return _assertThisInitialized(self); }

function _assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function _isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Date.prototype.toString.call(Reflect.construct(Date, [], function () {})); return true; } catch (e) { return false; } }

function _getPrototypeOf(o) { _getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return _getPrototypeOf(o); }


/**
 * Polymer Mixin to enable a localize function powered by language/resources from hass object.
 *
 * @polymerMixin
 */

/* harmony default export */ var localize_mixin = (Object(mixin["a" /* dedupingMixin */])(function (superClass) {
  return /*#__PURE__*/function (_superClass) {
    _inherits(_class, _superClass);

    var _super = _createSuper(_class);

    function _class() {
      _classCallCheck(this, _class);

      return _super.apply(this, arguments);
    }

    _createClass(_class, [{
      key: "__computeLocalize",
      value: function __computeLocalize(localize) {
        return localize;
      }
    }], [{
      key: "properties",
      get: function get() {
        return {
          hass: Object,

          /**
           * Translates a string to the current `language`. Any parameters to the
           * string should be passed in order, as follows:
           * `localize(stringKey, param1Name, param1Value, param2Name, param2Value)`
           */
          localize: {
            type: Function,
            computed: "__computeLocalize(hass.localize)"
          }
        };
      }
    }]);

    return _class;
  }(superClass);
}));
// CONCATENATED MODULE: ./src/components/ha-relative-time.js
function ha_relative_time_typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { ha_relative_time_typeof = function _typeof(obj) { return typeof obj; }; } else { ha_relative_time_typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return ha_relative_time_typeof(obj); }

function ha_relative_time_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _get(target, property, receiver) { if (typeof Reflect !== "undefined" && Reflect.get) { _get = Reflect.get; } else { _get = function _get(target, property, receiver) { var base = _superPropBase(target, property); if (!base) return; var desc = Object.getOwnPropertyDescriptor(base, property); if (desc.get) { return desc.get.call(receiver); } return desc.value; }; } return _get(target, property, receiver || target); }

function _superPropBase(object, property) { while (!Object.prototype.hasOwnProperty.call(object, property)) { object = ha_relative_time_getPrototypeOf(object); if (object === null) break; } return object; }

function ha_relative_time_defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } }

function ha_relative_time_createClass(Constructor, protoProps, staticProps) { if (protoProps) ha_relative_time_defineProperties(Constructor.prototype, protoProps); if (staticProps) ha_relative_time_defineProperties(Constructor, staticProps); return Constructor; }

function ha_relative_time_inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) ha_relative_time_setPrototypeOf(subClass, superClass); }

function ha_relative_time_setPrototypeOf(o, p) { ha_relative_time_setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return ha_relative_time_setPrototypeOf(o, p); }

function ha_relative_time_createSuper(Derived) { return function () { var Super = ha_relative_time_getPrototypeOf(Derived), result; if (ha_relative_time_isNativeReflectConstruct()) { var NewTarget = ha_relative_time_getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return ha_relative_time_possibleConstructorReturn(this, result); }; }

function ha_relative_time_possibleConstructorReturn(self, call) { if (call && (ha_relative_time_typeof(call) === "object" || typeof call === "function")) { return call; } return ha_relative_time_assertThisInitialized(self); }

function ha_relative_time_assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function ha_relative_time_isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Date.prototype.toString.call(Reflect.construct(Date, [], function () {})); return true; } catch (e) { return false; } }

function ha_relative_time_getPrototypeOf(o) { ha_relative_time_getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return ha_relative_time_getPrototypeOf(o); }


/* eslint-plugin-disable lit */




/*
 * @appliesMixin LocalizeMixin
 */

var ha_relative_time_HaRelativeTime = /*#__PURE__*/function (_LocalizeMixin) {
  ha_relative_time_inherits(HaRelativeTime, _LocalizeMixin);

  var _super = ha_relative_time_createSuper(HaRelativeTime);

  ha_relative_time_createClass(HaRelativeTime, null, [{
    key: "properties",
    get: function get() {
      return {
        hass: Object,
        datetime: {
          type: String,
          observer: "datetimeChanged"
        },
        datetimeObj: {
          type: Object,
          observer: "datetimeObjChanged"
        },
        parsedDateTime: Object
      };
    }
  }]);

  function HaRelativeTime() {
    var _this;

    ha_relative_time_classCallCheck(this, HaRelativeTime);

    _this = _super.call(this);
    _this.updateRelative = _this.updateRelative.bind(ha_relative_time_assertThisInitialized(_this));
    return _this;
  }

  ha_relative_time_createClass(HaRelativeTime, [{
    key: "connectedCallback",
    value: function connectedCallback() {
      _get(ha_relative_time_getPrototypeOf(HaRelativeTime.prototype), "connectedCallback", this).call(this); // update every 60 seconds


      this.updateInterval = setInterval(this.updateRelative, 60000);
    }
  }, {
    key: "disconnectedCallback",
    value: function disconnectedCallback() {
      _get(ha_relative_time_getPrototypeOf(HaRelativeTime.prototype), "disconnectedCallback", this).call(this);

      clearInterval(this.updateInterval);
    }
  }, {
    key: "datetimeChanged",
    value: function datetimeChanged(newVal) {
      this.parsedDateTime = newVal ? new Date(newVal) : null;
      this.updateRelative();
    }
  }, {
    key: "datetimeObjChanged",
    value: function datetimeObjChanged(newVal) {
      this.parsedDateTime = newVal;
      this.updateRelative();
    }
  }, {
    key: "updateRelative",
    value: function updateRelative() {
      var root = Object(polymer_dom["a" /* dom */])(this);

      if (!this.parsedDateTime) {
        root.innerHTML = this.localize("ui.components.relative_time.never");
      } else {
        root.innerHTML = relativeTime(this.parsedDateTime, this.localize);
      }
    }
  }]);

  return HaRelativeTime;
}(localize_mixin(polymer_element["a" /* PolymerElement */]));

customElements.define("ha-relative-time", ha_relative_time_HaRelativeTime);
// EXTERNAL MODULE: ./src/components/ha-icon.ts + 3 modules
var ha_icon = __webpack_require__(32);

// CONCATENATED MODULE: ./hassio/src/components/hassio-card-content.ts
function hassio_card_content_typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { hassio_card_content_typeof = function _typeof(obj) { return typeof obj; }; } else { hassio_card_content_typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return hassio_card_content_typeof(obj); }

function _templateObject6() {
  var data = _taggedTemplateLiteral(["\n      ha-icon {\n        margin-right: 24px;\n        margin-left: 8px;\n        margin-top: 12px;\n        float: left;\n        color: var(--secondary-text-color);\n      }\n      ha-icon.update {\n        color: var(--paper-orange-400);\n      }\n      ha-icon.running,\n      ha-icon.installed {\n        color: var(--paper-green-400);\n      }\n      ha-icon.hassupdate,\n      ha-icon.snapshot {\n        color: var(--paper-item-icon-color);\n      }\n      ha-icon.not_available {\n        color: var(--google-red-500);\n      }\n      .title {\n        color: var(--primary-text-color);\n        white-space: nowrap;\n        text-overflow: ellipsis;\n        overflow: hidden;\n      }\n      .addition {\n        color: var(--secondary-text-color);\n        overflow: hidden;\n        position: relative;\n        height: 2.4em;\n        line-height: 1.2em;\n      }\n      ha-relative-time {\n        display: block;\n      }\n      .icon_image img {\n        max-height: 40px;\n        max-width: 40px;\n        margin-top: 4px;\n        margin-right: 16px;\n        float: left;\n      }\n      .icon_image.stopped,\n      .icon_image.not_available {\n        filter: grayscale(1);\n      }\n      .dot {\n        position: absolute;\n        background-color: var(--paper-orange-400);\n        width: 12px;\n        height: 12px;\n        top: 8px;\n        right: 8px;\n        border-radius: 50%;\n      }\n      .topbar {\n        position: absolute;\n        width: 100%;\n        height: 2px;\n        top: 0;\n        left: 0;\n        border-top-left-radius: 2px;\n        border-top-right-radius: 2px;\n      }\n      .topbar.installed {\n        background-color: var(--primary-color);\n      }\n      .topbar.update {\n        background-color: var(--accent-color);\n      }\n      .topbar.unavailable {\n        background-color: var(--error-color);\n      }\n    "]);

  _templateObject6 = function _templateObject6() {
    return data;
  };

  return data;
}

function _templateObject5() {
  var data = _taggedTemplateLiteral(["\n                <ha-relative-time\n                  .hass=", "\n                  class=\"addition\"\n                  .datetime=", "\n                ></ha-relative-time>\n              "]);

  _templateObject5 = function _templateObject5() {
    return data;
  };

  return data;
}

function _templateObject4() {
  var data = _taggedTemplateLiteral(["\n            <ha-icon\n              class=", "\n              .icon=", "\n              .title=", "\n            ></ha-icon>\n          "]);

  _templateObject4 = function _templateObject4() {
    return data;
  };

  return data;
}

function _templateObject3() {
  var data = _taggedTemplateLiteral(["\n            <div class=\"icon_image ", "\">\n              <img src=\"", "\" title=\"", "\" />\n              <div></div>\n            </div>\n          "]);

  _templateObject3 = function _templateObject3() {
    return data;
  };

  return data;
}

function _templateObject2() {
  var data = _taggedTemplateLiteral([" <div class=\"topbar ", "\"></div> "]);

  _templateObject2 = function _templateObject2() {
    return data;
  };

  return data;
}

function _templateObject() {
  var data = _taggedTemplateLiteral(["\n      ", "\n      ", "\n      <div>\n        <div class=\"title\">\n          ", "\n        </div>\n        <div class=\"addition\">\n          ", "\n          ", "\n          ", "\n        </div>\n      </div>\n    "]);

  _templateObject = function _templateObject() {
    return data;
  };

  return data;
}

function _taggedTemplateLiteral(strings, raw) { if (!raw) { raw = strings.slice(0); } return Object.freeze(Object.defineProperties(strings, { raw: { value: Object.freeze(raw) } })); }

function hassio_card_content_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function hassio_card_content_inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) hassio_card_content_setPrototypeOf(subClass, superClass); }

function hassio_card_content_setPrototypeOf(o, p) { hassio_card_content_setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return hassio_card_content_setPrototypeOf(o, p); }

function hassio_card_content_createSuper(Derived) { return function () { var Super = hassio_card_content_getPrototypeOf(Derived), result; if (hassio_card_content_isNativeReflectConstruct()) { var NewTarget = hassio_card_content_getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return hassio_card_content_possibleConstructorReturn(this, result); }; }

function hassio_card_content_possibleConstructorReturn(self, call) { if (call && (hassio_card_content_typeof(call) === "object" || typeof call === "function")) { return call; } return hassio_card_content_assertThisInitialized(self); }

function hassio_card_content_assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function hassio_card_content_isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Date.prototype.toString.call(Reflect.construct(Date, [], function () {})); return true; } catch (e) { return false; } }

function hassio_card_content_getPrototypeOf(o) { hassio_card_content_getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return hassio_card_content_getPrototypeOf(o); }

function _decorate(decorators, factory, superClass, mixins) { var api = _getDecoratorsApi(); if (mixins) { for (var i = 0; i < mixins.length; i++) { api = mixins[i](api); } } var r = factory(function initialize(O) { api.initializeInstanceElements(O, decorated.elements); }, superClass); var decorated = api.decorateClass(_coalesceClassElements(r.d.map(_createElementDescriptor)), decorators); api.initializeClassElements(r.F, decorated.elements); return api.runClassFinishers(r.F, decorated.finishers); }

function _getDecoratorsApi() { _getDecoratorsApi = function _getDecoratorsApi() { return api; }; var api = { elementsDefinitionOrder: [["method"], ["field"]], initializeInstanceElements: function initializeInstanceElements(O, elements) { ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { if (element.kind === kind && element.placement === "own") { this.defineClassElement(O, element); } }, this); }, this); }, initializeClassElements: function initializeClassElements(F, elements) { var proto = F.prototype; ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { var placement = element.placement; if (element.kind === kind && (placement === "static" || placement === "prototype")) { var receiver = placement === "static" ? F : proto; this.defineClassElement(receiver, element); } }, this); }, this); }, defineClassElement: function defineClassElement(receiver, element) { var descriptor = element.descriptor; if (element.kind === "field") { var initializer = element.initializer; descriptor = { enumerable: descriptor.enumerable, writable: descriptor.writable, configurable: descriptor.configurable, value: initializer === void 0 ? void 0 : initializer.call(receiver) }; } Object.defineProperty(receiver, element.key, descriptor); }, decorateClass: function decorateClass(elements, decorators) { var newElements = []; var finishers = []; var placements = { "static": [], prototype: [], own: [] }; elements.forEach(function (element) { this.addElementPlacement(element, placements); }, this); elements.forEach(function (element) { if (!_hasDecorators(element)) return newElements.push(element); var elementFinishersExtras = this.decorateElement(element, placements); newElements.push(elementFinishersExtras.element); newElements.push.apply(newElements, elementFinishersExtras.extras); finishers.push.apply(finishers, elementFinishersExtras.finishers); }, this); if (!decorators) { return { elements: newElements, finishers: finishers }; } var result = this.decorateConstructor(newElements, decorators); finishers.push.apply(finishers, result.finishers); result.finishers = finishers; return result; }, addElementPlacement: function addElementPlacement(element, placements, silent) { var keys = placements[element.placement]; if (!silent && keys.indexOf(element.key) !== -1) { throw new TypeError("Duplicated element (" + element.key + ")"); } keys.push(element.key); }, decorateElement: function decorateElement(element, placements) { var extras = []; var finishers = []; for (var decorators = element.decorators, i = decorators.length - 1; i >= 0; i--) { var keys = placements[element.placement]; keys.splice(keys.indexOf(element.key), 1); var elementObject = this.fromElementDescriptor(element); var elementFinisherExtras = this.toElementFinisherExtras((0, decorators[i])(elementObject) || elementObject); element = elementFinisherExtras.element; this.addElementPlacement(element, placements); if (elementFinisherExtras.finisher) { finishers.push(elementFinisherExtras.finisher); } var newExtras = elementFinisherExtras.extras; if (newExtras) { for (var j = 0; j < newExtras.length; j++) { this.addElementPlacement(newExtras[j], placements); } extras.push.apply(extras, newExtras); } } return { element: element, finishers: finishers, extras: extras }; }, decorateConstructor: function decorateConstructor(elements, decorators) { var finishers = []; for (var i = decorators.length - 1; i >= 0; i--) { var obj = this.fromClassDescriptor(elements); var elementsAndFinisher = this.toClassDescriptor((0, decorators[i])(obj) || obj); if (elementsAndFinisher.finisher !== undefined) { finishers.push(elementsAndFinisher.finisher); } if (elementsAndFinisher.elements !== undefined) { elements = elementsAndFinisher.elements; for (var j = 0; j < elements.length - 1; j++) { for (var k = j + 1; k < elements.length; k++) { if (elements[j].key === elements[k].key && elements[j].placement === elements[k].placement) { throw new TypeError("Duplicated element (" + elements[j].key + ")"); } } } } } return { elements: elements, finishers: finishers }; }, fromElementDescriptor: function fromElementDescriptor(element) { var obj = { kind: element.kind, key: element.key, placement: element.placement, descriptor: element.descriptor }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); if (element.kind === "field") obj.initializer = element.initializer; return obj; }, toElementDescriptors: function toElementDescriptors(elementObjects) { if (elementObjects === undefined) return; return _toArray(elementObjects).map(function (elementObject) { var element = this.toElementDescriptor(elementObject); this.disallowProperty(elementObject, "finisher", "An element descriptor"); this.disallowProperty(elementObject, "extras", "An element descriptor"); return element; }, this); }, toElementDescriptor: function toElementDescriptor(elementObject) { var kind = String(elementObject.kind); if (kind !== "method" && kind !== "field") { throw new TypeError('An element descriptor\'s .kind property must be either "method" or' + ' "field", but a decorator created an element descriptor with' + ' .kind "' + kind + '"'); } var key = _toPropertyKey(elementObject.key); var placement = String(elementObject.placement); if (placement !== "static" && placement !== "prototype" && placement !== "own") { throw new TypeError('An element descriptor\'s .placement property must be one of "static",' + ' "prototype" or "own", but a decorator created an element descriptor' + ' with .placement "' + placement + '"'); } var descriptor = elementObject.descriptor; this.disallowProperty(elementObject, "elements", "An element descriptor"); var element = { kind: kind, key: key, placement: placement, descriptor: Object.assign({}, descriptor) }; if (kind !== "field") { this.disallowProperty(elementObject, "initializer", "A method descriptor"); } else { this.disallowProperty(descriptor, "get", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "set", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "value", "The property descriptor of a field descriptor"); element.initializer = elementObject.initializer; } return element; }, toElementFinisherExtras: function toElementFinisherExtras(elementObject) { var element = this.toElementDescriptor(elementObject); var finisher = _optionalCallableProperty(elementObject, "finisher"); var extras = this.toElementDescriptors(elementObject.extras); return { element: element, finisher: finisher, extras: extras }; }, fromClassDescriptor: function fromClassDescriptor(elements) { var obj = { kind: "class", elements: elements.map(this.fromElementDescriptor, this) }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); return obj; }, toClassDescriptor: function toClassDescriptor(obj) { var kind = String(obj.kind); if (kind !== "class") { throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator' + ' created a class descriptor with .kind "' + kind + '"'); } this.disallowProperty(obj, "key", "A class descriptor"); this.disallowProperty(obj, "placement", "A class descriptor"); this.disallowProperty(obj, "descriptor", "A class descriptor"); this.disallowProperty(obj, "initializer", "A class descriptor"); this.disallowProperty(obj, "extras", "A class descriptor"); var finisher = _optionalCallableProperty(obj, "finisher"); var elements = this.toElementDescriptors(obj.elements); return { elements: elements, finisher: finisher }; }, runClassFinishers: function runClassFinishers(constructor, finishers) { for (var i = 0; i < finishers.length; i++) { var newConstructor = (0, finishers[i])(constructor); if (newConstructor !== undefined) { if (typeof newConstructor !== "function") { throw new TypeError("Finishers must return a constructor."); } constructor = newConstructor; } } return constructor; }, disallowProperty: function disallowProperty(obj, name, objectType) { if (obj[name] !== undefined) { throw new TypeError(objectType + " can't have a ." + name + " property."); } } }; return api; }

function _createElementDescriptor(def) { var key = _toPropertyKey(def.key); var descriptor; if (def.kind === "method") { descriptor = { value: def.value, writable: true, configurable: true, enumerable: false }; } else if (def.kind === "get") { descriptor = { get: def.value, configurable: true, enumerable: false }; } else if (def.kind === "set") { descriptor = { set: def.value, configurable: true, enumerable: false }; } else if (def.kind === "field") { descriptor = { configurable: true, writable: true, enumerable: true }; } var element = { kind: def.kind === "field" ? "field" : "method", key: key, placement: def["static"] ? "static" : def.kind === "field" ? "own" : "prototype", descriptor: descriptor }; if (def.decorators) element.decorators = def.decorators; if (def.kind === "field") element.initializer = def.value; return element; }

function _coalesceGetterSetter(element, other) { if (element.descriptor.get !== undefined) { other.descriptor.get = element.descriptor.get; } else { other.descriptor.set = element.descriptor.set; } }

function _coalesceClassElements(elements) { var newElements = []; var isSameElement = function isSameElement(other) { return other.kind === "method" && other.key === element.key && other.placement === element.placement; }; for (var i = 0; i < elements.length; i++) { var element = elements[i]; var other; if (element.kind === "method" && (other = newElements.find(isSameElement))) { if (_isDataDescriptor(element.descriptor) || _isDataDescriptor(other.descriptor)) { if (_hasDecorators(element) || _hasDecorators(other)) { throw new ReferenceError("Duplicated methods (" + element.key + ") can't be decorated."); } other.descriptor = element.descriptor; } else { if (_hasDecorators(element)) { if (_hasDecorators(other)) { throw new ReferenceError("Decorators can't be placed on different accessors with for " + "the same property (" + element.key + ")."); } other.decorators = element.decorators; } _coalesceGetterSetter(element, other); } } else { newElements.push(element); } } return newElements; }

function _hasDecorators(element) { return element.decorators && element.decorators.length; }

function _isDataDescriptor(desc) { return desc !== undefined && !(desc.value === undefined && desc.writable === undefined); }

function _optionalCallableProperty(obj, name) { var value = obj[name]; if (value !== undefined && typeof value !== "function") { throw new TypeError("Expected '" + name + "' to be a function"); } return value; }

function _toPropertyKey(arg) { var key = _toPrimitive(arg, "string"); return hassio_card_content_typeof(key) === "symbol" ? key : String(key); }

function _toPrimitive(input, hint) { if (hassio_card_content_typeof(input) !== "object" || input === null) return input; var prim = input[Symbol.toPrimitive]; if (prim !== undefined) { var res = prim.call(input, hint || "default"); if (hassio_card_content_typeof(res) !== "object") return res; throw new TypeError("@@toPrimitive must return a primitive value."); } return (hint === "string" ? String : Number)(input); }

function _toArray(arr) { return _arrayWithHoles(arr) || _iterableToArray(arr) || _unsupportedIterableToArray(arr) || _nonIterableRest(); }

function _nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function _unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return _arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(n); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return _arrayLikeToArray(o, minLen); }

function _arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function _iterableToArray(iter) { if (typeof Symbol !== "undefined" && Symbol.iterator in Object(iter)) return Array.from(iter); }

function _arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }





var hassio_card_content_HassioCardContent = _decorate([Object(lit_element["d" /* customElement */])("hassio-card-content")], function (_initialize, _LitElement) {
  var HassioCardContent = /*#__PURE__*/function (_LitElement2) {
    hassio_card_content_inherits(HassioCardContent, _LitElement2);

    var _super = hassio_card_content_createSuper(HassioCardContent);

    function HassioCardContent() {
      var _this;

      hassio_card_content_classCallCheck(this, HassioCardContent);

      for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
        args[_key] = arguments[_key];
      }

      _this = _super.call.apply(_super, [this].concat(args));

      _initialize(hassio_card_content_assertThisInitialized(_this));

      return _this;
    }

    return HassioCardContent;
  }(_LitElement);

  return {
    F: HassioCardContent,
    d: [{
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "hass",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "title",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "description",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])({
        type: Boolean
      })],
      key: "available",
      value: function value() {
        return true;
      }
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])({
        type: Boolean
      })],
      key: "showTopbar",
      value: function value() {
        return false;
      }
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "topbarClass",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "datetime",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "iconTitle",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "iconClass",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "icon",
      value: function value() {
        return "hass:help-circle";
      }
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "iconImage",
      value: void 0
    }, {
      kind: "method",
      key: "render",
      value: function render() {
        return Object(lit_element["e" /* html */])(_templateObject(), this.showTopbar ? Object(lit_element["e" /* html */])(_templateObject2(), this.topbarClass) : "", this.iconImage ? Object(lit_element["e" /* html */])(_templateObject3(), this.iconClass, this.iconImage, this.iconTitle) : Object(lit_element["e" /* html */])(_templateObject4(), this.iconClass, this.icon, this.iconTitle), this.title, this.description,
        /* treat as available when undefined */
        this.available === false ? " (Not available)" : "", this.datetime ? Object(lit_element["e" /* html */])(_templateObject5(), this.hass, this.datetime) : undefined);
      }
    }, {
      kind: "get",
      "static": true,
      key: "styles",
      value: function styles() {
        return Object(lit_element["c" /* css */])(_templateObject6());
      }
    }]
  };
}, lit_element["a" /* LitElement */]);

/***/ }),

/***/ 58:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";

// EXTERNAL MODULE: ./node_modules/@material/mwc-ripple/mwc-ripple.js + 3 modules
var mwc_ripple = __webpack_require__(185);

// EXTERNAL MODULE: ./node_modules/lit-element/lit-element.js + 3 modules
var lit_element = __webpack_require__(5);

// EXTERNAL MODULE: ./node_modules/lit-html/directives/class-map.js
var class_map = __webpack_require__(26);

// EXTERNAL MODULE: ./node_modules/memoize-one/dist/memoize-one.esm.js
var memoize_one_esm = __webpack_require__(50);

// CONCATENATED MODULE: ./src/common/config/is_component_loaded.ts
/** Return if a component is loaded. */
var isComponentLoaded = function isComponentLoaded(hass, component) {
  return hass && hass.config.components.indexOf(component) !== -1;
};
// EXTERNAL MODULE: ./src/common/navigate.ts
var common_navigate = __webpack_require__(38);

// EXTERNAL MODULE: ./src/components/ha-menu-button.ts + 2 modules
var ha_menu_button = __webpack_require__(99);

// EXTERNAL MODULE: ./src/components/ha-icon-button-arrow-prev.ts
var ha_icon_button_arrow_prev = __webpack_require__(87);

// EXTERNAL MODULE: ./src/components/ha-icon.ts + 3 modules
var ha_icon = __webpack_require__(32);

// CONCATENATED MODULE: ./src/layouts/hass-tabs-subpage.ts
function _typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { _typeof = function _typeof(obj) { return typeof obj; }; } else { _typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return _typeof(obj); }

function _templateObject9() {
  var data = _taggedTemplateLiteral(["\n      :host {\n        display: block;\n        height: 100%;\n        background-color: var(--primary-background-color);\n      }\n\n      .toolbar {\n        display: flex;\n        align-items: center;\n        font-size: 20px;\n        height: 65px;\n        background-color: var(--sidebar-background-color);\n        font-weight: 400;\n        color: var(--sidebar-text-color);\n        border-bottom: 1px solid var(--divider-color);\n        padding: 0 16px;\n        box-sizing: border-box;\n      }\n\n      #tabbar {\n        display: flex;\n        font-size: 14px;\n      }\n\n      #tabbar.bottom-bar {\n        position: absolute;\n        bottom: 0;\n        left: 0;\n        padding: 0 16px;\n        box-sizing: border-box;\n        background-color: var(--sidebar-background-color);\n        border-top: 1px solid var(--divider-color);\n        justify-content: space-between;\n        z-index: 1;\n        font-size: 12px;\n        width: 100%;\n      }\n\n      #tabbar:not(.bottom-bar) {\n        flex: 1;\n        justify-content: center;\n      }\n\n      .tab {\n        padding: 0 32px;\n        display: flex;\n        flex-direction: column;\n        text-align: center;\n        align-items: center;\n        justify-content: center;\n        height: 64px;\n        cursor: pointer;\n      }\n\n      .name {\n        white-space: nowrap;\n      }\n\n      .tab.active {\n        color: var(--primary-color);\n      }\n\n      #tabbar:not(.bottom-bar) .tab.active {\n        border-bottom: 2px solid var(--primary-color);\n      }\n\n      .bottom-bar .tab {\n        padding: 0 16px;\n        width: 20%;\n        min-width: 0;\n      }\n\n      :host(:not([narrow])) #toolbar-icon {\n        min-width: 40px;\n      }\n\n      ha-menu-button,\n      ha-icon-button-arrow-prev,\n      ::slotted([slot=\"toolbar-icon\"]) {\n        flex-shrink: 0;\n        pointer-events: auto;\n        color: var(--sidebar-icon-color);\n      }\n\n      .main-title {\n        flex: 1;\n        overflow: hidden;\n        text-overflow: ellipsis;\n        max-height: 40px;\n        line-height: 20px;\n      }\n\n      .content {\n        position: relative;\n        width: 100%;\n        height: calc(100% - 65px);\n        overflow-y: auto;\n        overflow: auto;\n        -webkit-overflow-scrolling: touch;\n      }\n\n      :host([narrow]) .content {\n        height: calc(100% - 128px);\n      }\n    "]);

  _templateObject9 = function _templateObject9() {
    return data;
  };

  return data;
}

function _templateObject8() {
  var data = _taggedTemplateLiteral(["\n              <div id=\"tabbar\" class=", ">\n                ", "\n              </div>\n            "]);

  _templateObject8 = function _templateObject8() {
    return data;
  };

  return data;
}

function _templateObject7() {
  var data = _taggedTemplateLiteral([" <div class=\"main-title\"><slot name=\"header\"></slot></div> "]);

  _templateObject7 = function _templateObject7() {
    return data;
  };

  return data;
}

function _templateObject6() {
  var data = _taggedTemplateLiteral(["\n              <ha-icon-button-arrow-prev\n                aria-label=\"Back\"\n                @click=", "\n              ></ha-icon-button-arrow-prev>\n            "]);

  _templateObject6 = function _templateObject6() {
    return data;
  };

  return data;
}

function _templateObject5() {
  var data = _taggedTemplateLiteral(["\n              <ha-menu-button\n                .hass=", "\n                .hassio=", "\n                .narrow=", "\n              ></ha-menu-button>\n            "]);

  _templateObject5 = function _templateObject5() {
    return data;
  };

  return data;
}

function _templateObject4() {
  var data = _taggedTemplateLiteral(["\n      <div class=\"toolbar\">\n        ", "\n        ", "\n        ", "\n        <div id=\"toolbar-icon\">\n          <slot name=\"toolbar-icon\"></slot>\n        </div>\n      </div>\n      <div class=\"content\">\n        <slot></slot>\n      </div>\n    "]);

  _templateObject4 = function _templateObject4() {
    return data;
  };

  return data;
}

function _templateObject3() {
  var data = _taggedTemplateLiteral(["\n                    <span class=\"name\"\n                      >", "</span\n                    >\n                  "]);

  _templateObject3 = function _templateObject3() {
    return data;
  };

  return data;
}

function _templateObject2() {
  var data = _taggedTemplateLiteral([" <ha-icon .icon=", "></ha-icon> "]);

  _templateObject2 = function _templateObject2() {
    return data;
  };

  return data;
}

function _templateObject() {
  var data = _taggedTemplateLiteral(["\n            <div\n              class=\"tab ", "\"\n              @click=", "\n              .path=", "\n            >\n              ", "\n              ", "\n              <mwc-ripple></mwc-ripple>\n            </div>\n          "]);

  _templateObject = function _templateObject() {
    return data;
  };

  return data;
}

function _taggedTemplateLiteral(strings, raw) { if (!raw) { raw = strings.slice(0); } return Object.freeze(Object.defineProperties(strings, { raw: { value: Object.freeze(raw) } })); }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) _setPrototypeOf(subClass, superClass); }

function _setPrototypeOf(o, p) { _setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return _setPrototypeOf(o, p); }

function _createSuper(Derived) { return function () { var Super = _getPrototypeOf(Derived), result; if (_isNativeReflectConstruct()) { var NewTarget = _getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return _possibleConstructorReturn(this, result); }; }

function _possibleConstructorReturn(self, call) { if (call && (_typeof(call) === "object" || typeof call === "function")) { return call; } return _assertThisInitialized(self); }

function _assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function _isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Date.prototype.toString.call(Reflect.construct(Date, [], function () {})); return true; } catch (e) { return false; } }

function _decorate(decorators, factory, superClass, mixins) { var api = _getDecoratorsApi(); if (mixins) { for (var i = 0; i < mixins.length; i++) { api = mixins[i](api); } } var r = factory(function initialize(O) { api.initializeInstanceElements(O, decorated.elements); }, superClass); var decorated = api.decorateClass(_coalesceClassElements(r.d.map(_createElementDescriptor)), decorators); api.initializeClassElements(r.F, decorated.elements); return api.runClassFinishers(r.F, decorated.finishers); }

function _getDecoratorsApi() { _getDecoratorsApi = function _getDecoratorsApi() { return api; }; var api = { elementsDefinitionOrder: [["method"], ["field"]], initializeInstanceElements: function initializeInstanceElements(O, elements) { ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { if (element.kind === kind && element.placement === "own") { this.defineClassElement(O, element); } }, this); }, this); }, initializeClassElements: function initializeClassElements(F, elements) { var proto = F.prototype; ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { var placement = element.placement; if (element.kind === kind && (placement === "static" || placement === "prototype")) { var receiver = placement === "static" ? F : proto; this.defineClassElement(receiver, element); } }, this); }, this); }, defineClassElement: function defineClassElement(receiver, element) { var descriptor = element.descriptor; if (element.kind === "field") { var initializer = element.initializer; descriptor = { enumerable: descriptor.enumerable, writable: descriptor.writable, configurable: descriptor.configurable, value: initializer === void 0 ? void 0 : initializer.call(receiver) }; } Object.defineProperty(receiver, element.key, descriptor); }, decorateClass: function decorateClass(elements, decorators) { var newElements = []; var finishers = []; var placements = { "static": [], prototype: [], own: [] }; elements.forEach(function (element) { this.addElementPlacement(element, placements); }, this); elements.forEach(function (element) { if (!_hasDecorators(element)) return newElements.push(element); var elementFinishersExtras = this.decorateElement(element, placements); newElements.push(elementFinishersExtras.element); newElements.push.apply(newElements, elementFinishersExtras.extras); finishers.push.apply(finishers, elementFinishersExtras.finishers); }, this); if (!decorators) { return { elements: newElements, finishers: finishers }; } var result = this.decorateConstructor(newElements, decorators); finishers.push.apply(finishers, result.finishers); result.finishers = finishers; return result; }, addElementPlacement: function addElementPlacement(element, placements, silent) { var keys = placements[element.placement]; if (!silent && keys.indexOf(element.key) !== -1) { throw new TypeError("Duplicated element (" + element.key + ")"); } keys.push(element.key); }, decorateElement: function decorateElement(element, placements) { var extras = []; var finishers = []; for (var decorators = element.decorators, i = decorators.length - 1; i >= 0; i--) { var keys = placements[element.placement]; keys.splice(keys.indexOf(element.key), 1); var elementObject = this.fromElementDescriptor(element); var elementFinisherExtras = this.toElementFinisherExtras((0, decorators[i])(elementObject) || elementObject); element = elementFinisherExtras.element; this.addElementPlacement(element, placements); if (elementFinisherExtras.finisher) { finishers.push(elementFinisherExtras.finisher); } var newExtras = elementFinisherExtras.extras; if (newExtras) { for (var j = 0; j < newExtras.length; j++) { this.addElementPlacement(newExtras[j], placements); } extras.push.apply(extras, newExtras); } } return { element: element, finishers: finishers, extras: extras }; }, decorateConstructor: function decorateConstructor(elements, decorators) { var finishers = []; for (var i = decorators.length - 1; i >= 0; i--) { var obj = this.fromClassDescriptor(elements); var elementsAndFinisher = this.toClassDescriptor((0, decorators[i])(obj) || obj); if (elementsAndFinisher.finisher !== undefined) { finishers.push(elementsAndFinisher.finisher); } if (elementsAndFinisher.elements !== undefined) { elements = elementsAndFinisher.elements; for (var j = 0; j < elements.length - 1; j++) { for (var k = j + 1; k < elements.length; k++) { if (elements[j].key === elements[k].key && elements[j].placement === elements[k].placement) { throw new TypeError("Duplicated element (" + elements[j].key + ")"); } } } } } return { elements: elements, finishers: finishers }; }, fromElementDescriptor: function fromElementDescriptor(element) { var obj = { kind: element.kind, key: element.key, placement: element.placement, descriptor: element.descriptor }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); if (element.kind === "field") obj.initializer = element.initializer; return obj; }, toElementDescriptors: function toElementDescriptors(elementObjects) { if (elementObjects === undefined) return; return _toArray(elementObjects).map(function (elementObject) { var element = this.toElementDescriptor(elementObject); this.disallowProperty(elementObject, "finisher", "An element descriptor"); this.disallowProperty(elementObject, "extras", "An element descriptor"); return element; }, this); }, toElementDescriptor: function toElementDescriptor(elementObject) { var kind = String(elementObject.kind); if (kind !== "method" && kind !== "field") { throw new TypeError('An element descriptor\'s .kind property must be either "method" or' + ' "field", but a decorator created an element descriptor with' + ' .kind "' + kind + '"'); } var key = _toPropertyKey(elementObject.key); var placement = String(elementObject.placement); if (placement !== "static" && placement !== "prototype" && placement !== "own") { throw new TypeError('An element descriptor\'s .placement property must be one of "static",' + ' "prototype" or "own", but a decorator created an element descriptor' + ' with .placement "' + placement + '"'); } var descriptor = elementObject.descriptor; this.disallowProperty(elementObject, "elements", "An element descriptor"); var element = { kind: kind, key: key, placement: placement, descriptor: Object.assign({}, descriptor) }; if (kind !== "field") { this.disallowProperty(elementObject, "initializer", "A method descriptor"); } else { this.disallowProperty(descriptor, "get", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "set", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "value", "The property descriptor of a field descriptor"); element.initializer = elementObject.initializer; } return element; }, toElementFinisherExtras: function toElementFinisherExtras(elementObject) { var element = this.toElementDescriptor(elementObject); var finisher = _optionalCallableProperty(elementObject, "finisher"); var extras = this.toElementDescriptors(elementObject.extras); return { element: element, finisher: finisher, extras: extras }; }, fromClassDescriptor: function fromClassDescriptor(elements) { var obj = { kind: "class", elements: elements.map(this.fromElementDescriptor, this) }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); return obj; }, toClassDescriptor: function toClassDescriptor(obj) { var kind = String(obj.kind); if (kind !== "class") { throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator' + ' created a class descriptor with .kind "' + kind + '"'); } this.disallowProperty(obj, "key", "A class descriptor"); this.disallowProperty(obj, "placement", "A class descriptor"); this.disallowProperty(obj, "descriptor", "A class descriptor"); this.disallowProperty(obj, "initializer", "A class descriptor"); this.disallowProperty(obj, "extras", "A class descriptor"); var finisher = _optionalCallableProperty(obj, "finisher"); var elements = this.toElementDescriptors(obj.elements); return { elements: elements, finisher: finisher }; }, runClassFinishers: function runClassFinishers(constructor, finishers) { for (var i = 0; i < finishers.length; i++) { var newConstructor = (0, finishers[i])(constructor); if (newConstructor !== undefined) { if (typeof newConstructor !== "function") { throw new TypeError("Finishers must return a constructor."); } constructor = newConstructor; } } return constructor; }, disallowProperty: function disallowProperty(obj, name, objectType) { if (obj[name] !== undefined) { throw new TypeError(objectType + " can't have a ." + name + " property."); } } }; return api; }

function _createElementDescriptor(def) { var key = _toPropertyKey(def.key); var descriptor; if (def.kind === "method") { descriptor = { value: def.value, writable: true, configurable: true, enumerable: false }; } else if (def.kind === "get") { descriptor = { get: def.value, configurable: true, enumerable: false }; } else if (def.kind === "set") { descriptor = { set: def.value, configurable: true, enumerable: false }; } else if (def.kind === "field") { descriptor = { configurable: true, writable: true, enumerable: true }; } var element = { kind: def.kind === "field" ? "field" : "method", key: key, placement: def["static"] ? "static" : def.kind === "field" ? "own" : "prototype", descriptor: descriptor }; if (def.decorators) element.decorators = def.decorators; if (def.kind === "field") element.initializer = def.value; return element; }

function _coalesceGetterSetter(element, other) { if (element.descriptor.get !== undefined) { other.descriptor.get = element.descriptor.get; } else { other.descriptor.set = element.descriptor.set; } }

function _coalesceClassElements(elements) { var newElements = []; var isSameElement = function isSameElement(other) { return other.kind === "method" && other.key === element.key && other.placement === element.placement; }; for (var i = 0; i < elements.length; i++) { var element = elements[i]; var other; if (element.kind === "method" && (other = newElements.find(isSameElement))) { if (_isDataDescriptor(element.descriptor) || _isDataDescriptor(other.descriptor)) { if (_hasDecorators(element) || _hasDecorators(other)) { throw new ReferenceError("Duplicated methods (" + element.key + ") can't be decorated."); } other.descriptor = element.descriptor; } else { if (_hasDecorators(element)) { if (_hasDecorators(other)) { throw new ReferenceError("Decorators can't be placed on different accessors with for " + "the same property (" + element.key + ")."); } other.decorators = element.decorators; } _coalesceGetterSetter(element, other); } } else { newElements.push(element); } } return newElements; }

function _hasDecorators(element) { return element.decorators && element.decorators.length; }

function _isDataDescriptor(desc) { return desc !== undefined && !(desc.value === undefined && desc.writable === undefined); }

function _optionalCallableProperty(obj, name) { var value = obj[name]; if (value !== undefined && typeof value !== "function") { throw new TypeError("Expected '" + name + "' to be a function"); } return value; }

function _toPropertyKey(arg) { var key = _toPrimitive(arg, "string"); return _typeof(key) === "symbol" ? key : String(key); }

function _toPrimitive(input, hint) { if (_typeof(input) !== "object" || input === null) return input; var prim = input[Symbol.toPrimitive]; if (prim !== undefined) { var res = prim.call(input, hint || "default"); if (_typeof(res) !== "object") return res; throw new TypeError("@@toPrimitive must return a primitive value."); } return (hint === "string" ? String : Number)(input); }

function _toArray(arr) { return _arrayWithHoles(arr) || _iterableToArray(arr) || _unsupportedIterableToArray(arr) || _nonIterableRest(); }

function _nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function _unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return _arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(n); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return _arrayLikeToArray(o, minLen); }

function _arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function _iterableToArray(iter) { if (typeof Symbol !== "undefined" && Symbol.iterator in Object(iter)) return Array.from(iter); }

function _arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }

function _get(target, property, receiver) { if (typeof Reflect !== "undefined" && Reflect.get) { _get = Reflect.get; } else { _get = function _get(target, property, receiver) { var base = _superPropBase(target, property); if (!base) return; var desc = Object.getOwnPropertyDescriptor(base, property); if (desc.get) { return desc.get.call(receiver); } return desc.value; }; } return _get(target, property, receiver || target); }

function _superPropBase(object, property) { while (!Object.prototype.hasOwnProperty.call(object, property)) { object = _getPrototypeOf(object); if (object === null) break; } return object; }

function _getPrototypeOf(o) { _getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return _getPrototypeOf(o); }











var hass_tabs_subpage_HassTabsSubpage = _decorate([Object(lit_element["d" /* customElement */])("hass-tabs-subpage")], function (_initialize, _LitElement) {
  var HassTabsSubpage = /*#__PURE__*/function (_LitElement2) {
    _inherits(HassTabsSubpage, _LitElement2);

    var _super = _createSuper(HassTabsSubpage);

    function HassTabsSubpage() {
      var _this;

      _classCallCheck(this, HassTabsSubpage);

      for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
        args[_key] = arguments[_key];
      }

      _this = _super.call.apply(_super, [this].concat(args));

      _initialize(_assertThisInitialized(_this));

      return _this;
    }

    return HassTabsSubpage;
  }(_LitElement);

  return {
    F: HassTabsSubpage,
    d: [{
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "hass",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])({
        type: String,
        attribute: "back-path"
      })],
      key: "backPath",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "backCallback",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])({
        type: Boolean
      })],
      key: "hassio",
      value: function value() {
        return false;
      }
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])({
        type: Boolean,
        attribute: "main-page"
      })],
      key: "mainPage",
      value: function value() {
        return false;
      }
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "route",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "tabs",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])({
        type: Boolean,
        reflect: true
      })],
      key: "narrow",
      value: function value() {
        return false;
      }
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "_activeTab",
      value: void 0
    }, {
      kind: "field",
      key: "_getTabs",
      value: function value() {
        var _this2 = this;

        return Object(memoize_one_esm["a" /* default */])(function (tabs, activeTab, showAdvanced, _components, _language, _narrow) {
          var shownTabs = tabs.filter(function (page) {
            return (!page.component || page.core || isComponentLoaded(_this2.hass, page.component)) && (!page.advancedOnly || showAdvanced);
          });
          return shownTabs.map(function (page) {
            return Object(lit_element["e" /* html */])(_templateObject(), Object(class_map["a" /* classMap */])({
              active: page === activeTab
            }), _this2._tabTapped, page.path, _this2.narrow ? Object(lit_element["e" /* html */])(_templateObject2(), page.icon) : "", !_this2.narrow || page === activeTab ? Object(lit_element["e" /* html */])(_templateObject3(), page.translationKey ? _this2.hass.localize(page.translationKey) : page.name) : "");
          });
        });
      }
    }, {
      kind: "method",
      key: "updated",
      value: function updated(changedProperties) {
        var _this3 = this;

        _get(_getPrototypeOf(HassTabsSubpage.prototype), "updated", this).call(this, changedProperties);

        if (changedProperties.has("route")) {
          this._activeTab = this.tabs.find(function (tab) {
            return "".concat(_this3.route.prefix).concat(_this3.route.path).includes(tab.path);
          });
        }
      }
    }, {
      kind: "method",
      key: "render",
      value: function render() {
        var _this$hass$userData;

        var tabs = this._getTabs(this.tabs, this._activeTab, (_this$hass$userData = this.hass.userData) === null || _this$hass$userData === void 0 ? void 0 : _this$hass$userData.showAdvanced, this.hass.config.components, this.hass.language, this.narrow);

        return Object(lit_element["e" /* html */])(_templateObject4(), this.mainPage ? Object(lit_element["e" /* html */])(_templateObject5(), this.hass, this.hassio, this.narrow) : Object(lit_element["e" /* html */])(_templateObject6(), this._backTapped), this.narrow ? Object(lit_element["e" /* html */])(_templateObject7()) : "", tabs.length > 1 || !this.narrow ? Object(lit_element["e" /* html */])(_templateObject8(), Object(class_map["a" /* classMap */])({
          "bottom-bar": this.narrow
        }), tabs) : "");
      }
    }, {
      kind: "method",
      key: "_tabTapped",
      value: function _tabTapped(ev) {
        Object(common_navigate["a" /* navigate */])(this, ev.currentTarget.path, true);
      }
    }, {
      kind: "method",
      key: "_backTapped",
      value: function _backTapped() {
        if (this.backPath) {
          Object(common_navigate["a" /* navigate */])(this, this.backPath);
          return;
        }

        if (this.backCallback) {
          this.backCallback();
          return;
        }

        history.back();
      }
    }, {
      kind: "get",
      "static": true,
      key: "styles",
      value: function styles() {
        return Object(lit_element["c" /* css */])(_templateObject9());
      }
    }]
  };
}, lit_element["a" /* LitElement */]);

/***/ }),

/***/ 68:
/***/ (function(module, exports) {

/* empty file that we alias some files to that we don't want to include */

/***/ }),

/***/ 71:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony import */ var lit_element__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(5);
/* harmony import */ var _common_dom_fire_event__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(12);
/* harmony import */ var _ha_progress_button__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(121);
function _typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { _typeof = function _typeof(obj) { return typeof obj; }; } else { _typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return _typeof(obj); }

function asyncGeneratorStep(gen, resolve, reject, _next, _throw, key, arg) { try { var info = gen[key](arg); var value = info.value; } catch (error) { reject(error); return; } if (info.done) { resolve(value); } else { Promise.resolve(value).then(_next, _throw); } }

function _asyncToGenerator(fn) { return function () { var self = this, args = arguments; return new Promise(function (resolve, reject) { var gen = fn.apply(self, args); function _next(value) { asyncGeneratorStep(gen, resolve, reject, _next, _throw, "next", value); } function _throw(err) { asyncGeneratorStep(gen, resolve, reject, _next, _throw, "throw", err); } _next(undefined); }); }; }

function _templateObject() {
  var data = _taggedTemplateLiteral(["\n      <ha-progress-button\n        .progress=\"", "\"\n        @click=\"", "\"\n        ?disabled=\"", "\"\n        ><slot></slot\n      ></ha-progress-button>\n    "]);

  _templateObject = function _templateObject() {
    return data;
  };

  return data;
}

function _taggedTemplateLiteral(strings, raw) { if (!raw) { raw = strings.slice(0); } return Object.freeze(Object.defineProperties(strings, { raw: { value: Object.freeze(raw) } })); }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } }

function _createClass(Constructor, protoProps, staticProps) { if (protoProps) _defineProperties(Constructor.prototype, protoProps); if (staticProps) _defineProperties(Constructor, staticProps); return Constructor; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) _setPrototypeOf(subClass, superClass); }

function _setPrototypeOf(o, p) { _setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return _setPrototypeOf(o, p); }

function _createSuper(Derived) { return function () { var Super = _getPrototypeOf(Derived), result; if (_isNativeReflectConstruct()) { var NewTarget = _getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return _possibleConstructorReturn(this, result); }; }

function _possibleConstructorReturn(self, call) { if (call && (_typeof(call) === "object" || typeof call === "function")) { return call; } return _assertThisInitialized(self); }

function _assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function _isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Date.prototype.toString.call(Reflect.construct(Date, [], function () {})); return true; } catch (e) { return false; } }

function _getPrototypeOf(o) { _getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return _getPrototypeOf(o); }





var HaCallApiButton = /*#__PURE__*/function (_LitElement) {
  _inherits(HaCallApiButton, _LitElement);

  var _super = _createSuper(HaCallApiButton);

  _createClass(HaCallApiButton, [{
    key: "render",
    value: function render() {
      return Object(lit_element__WEBPACK_IMPORTED_MODULE_0__[/* html */ "e"])(_templateObject(), this.progress, this._buttonTapped, this.disabled);
    }
  }]);

  function HaCallApiButton() {
    var _this;

    _classCallCheck(this, HaCallApiButton);

    _this = _super.call(this);
    _this.method = "POST";
    _this.data = {};
    _this.disabled = false;
    _this.progress = false;
    return _this;
  }

  _createClass(HaCallApiButton, [{
    key: "_buttonTapped",
    value: function () {
      var _buttonTapped2 = _asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee() {
        var eventData, resp;
        return regeneratorRuntime.wrap(function _callee$(_context) {
          while (1) {
            switch (_context.prev = _context.next) {
              case 0:
                this.progress = true;
                eventData = {
                  method: this.method,
                  path: this.path,
                  data: this.data
                };
                _context.prev = 2;
                _context.next = 5;
                return this.hass.callApi(this.method, this.path, this.data);

              case 5:
                resp = _context.sent;
                this.progress = false;
                this.progressButton.actionSuccess();
                eventData.success = true;
                eventData.response = resp;
                _context.next = 18;
                break;

              case 12:
                _context.prev = 12;
                _context.t0 = _context["catch"](2);
                this.progress = false;
                this.progressButton.actionError();
                eventData.success = false;
                eventData.response = _context.t0;

              case 18:
                Object(_common_dom_fire_event__WEBPACK_IMPORTED_MODULE_1__[/* fireEvent */ "a"])(this, "hass-api-called", eventData);

              case 19:
              case "end":
                return _context.stop();
            }
          }
        }, _callee, this, [[2, 12]]);
      }));

      function _buttonTapped() {
        return _buttonTapped2.apply(this, arguments);
      }

      return _buttonTapped;
    }()
  }, {
    key: "progressButton",
    get: function get() {
      return this.renderRoot.querySelector("ha-progress-button");
    }
  }], [{
    key: "properties",
    get: function get() {
      return {
        hass: {},
        progress: Boolean,
        path: String,
        method: String,
        data: {},
        disabled: Boolean
      };
    }
  }]);

  return HaCallApiButton;
}(lit_element__WEBPACK_IMPORTED_MODULE_0__[/* LitElement */ "a"]);

customElements.define("ha-call-api-button", HaCallApiButton);

/***/ }),

/***/ 87:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* unused harmony export HaIconButtonArrowPrev */
/* harmony import */ var _ha_icon_button__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(23);
function _typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { _typeof = function _typeof(obj) { return typeof obj; }; } else { _typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return _typeof(obj); }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } }

function _createClass(Constructor, protoProps, staticProps) { if (protoProps) _defineProperties(Constructor.prototype, protoProps); if (staticProps) _defineProperties(Constructor, staticProps); return Constructor; }

function _get(target, property, receiver) { if (typeof Reflect !== "undefined" && Reflect.get) { _get = Reflect.get; } else { _get = function _get(target, property, receiver) { var base = _superPropBase(target, property); if (!base) return; var desc = Object.getOwnPropertyDescriptor(base, property); if (desc.get) { return desc.get.call(receiver); } return desc.value; }; } return _get(target, property, receiver || target); }

function _superPropBase(object, property) { while (!Object.prototype.hasOwnProperty.call(object, property)) { object = _getPrototypeOf(object); if (object === null) break; } return object; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) _setPrototypeOf(subClass, superClass); }

function _setPrototypeOf(o, p) { _setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return _setPrototypeOf(o, p); }

function _createSuper(Derived) { return function () { var Super = _getPrototypeOf(Derived), result; if (_isNativeReflectConstruct()) { var NewTarget = _getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return _possibleConstructorReturn(this, result); }; }

function _possibleConstructorReturn(self, call) { if (call && (_typeof(call) === "object" || typeof call === "function")) { return call; } return _assertThisInitialized(self); }

function _assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function _isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Date.prototype.toString.call(Reflect.construct(Date, [], function () {})); return true; } catch (e) { return false; } }

function _getPrototypeOf(o) { _getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return _getPrototypeOf(o); }


var HaIconButtonArrowPrev = /*#__PURE__*/function (_HaIconButton) {
  _inherits(HaIconButtonArrowPrev, _HaIconButton);

  var _super = _createSuper(HaIconButtonArrowPrev);

  function HaIconButtonArrowPrev() {
    _classCallCheck(this, HaIconButtonArrowPrev);

    return _super.apply(this, arguments);
  }

  _createClass(HaIconButtonArrowPrev, [{
    key: "connectedCallback",
    value: function connectedCallback() {
      var _this = this;

      _get(_getPrototypeOf(HaIconButtonArrowPrev.prototype), "connectedCallback", this).call(this); // wait to check for direction since otherwise direction is wrong even though top level is RTL


      setTimeout(function () {
        _this.icon = window.getComputedStyle(_this).direction === "ltr" ? "hass:arrow-left" : "hass:arrow-right";
      }, 100);
    }
  }]);

  return HaIconButtonArrowPrev;
}(_ha_icon_button__WEBPACK_IMPORTED_MODULE_0__[/* HaIconButton */ "a"]);
customElements.define("ha-icon-button-arrow-prev", HaIconButtonArrowPrev);

/***/ }),

/***/ 89:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony import */ var _polymer_paper_spinner_paper_spinner_lite__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(35);
/* harmony import */ var lit_element__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(5);
function _typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { _typeof = function _typeof(obj) { return typeof obj; }; } else { _typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return _typeof(obj); }

function _templateObject2() {
  var data = _taggedTemplateLiteral(["\n      :host {\n        height: 100%;\n        display: flex;\n        align-items: center;\n        justify-content: center;\n      }\n    "]);

  _templateObject2 = function _templateObject2() {
    return data;
  };

  return data;
}

function _templateObject() {
  var data = _taggedTemplateLiteral([" <paper-spinner-lite active></paper-spinner-lite> "]);

  _templateObject = function _templateObject() {
    return data;
  };

  return data;
}

function _taggedTemplateLiteral(strings, raw) { if (!raw) { raw = strings.slice(0); } return Object.freeze(Object.defineProperties(strings, { raw: { value: Object.freeze(raw) } })); }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) _setPrototypeOf(subClass, superClass); }

function _setPrototypeOf(o, p) { _setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return _setPrototypeOf(o, p); }

function _createSuper(Derived) { return function () { var Super = _getPrototypeOf(Derived), result; if (_isNativeReflectConstruct()) { var NewTarget = _getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return _possibleConstructorReturn(this, result); }; }

function _possibleConstructorReturn(self, call) { if (call && (_typeof(call) === "object" || typeof call === "function")) { return call; } return _assertThisInitialized(self); }

function _assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function _isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Date.prototype.toString.call(Reflect.construct(Date, [], function () {})); return true; } catch (e) { return false; } }

function _getPrototypeOf(o) { _getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return _getPrototypeOf(o); }

function _decorate(decorators, factory, superClass, mixins) { var api = _getDecoratorsApi(); if (mixins) { for (var i = 0; i < mixins.length; i++) { api = mixins[i](api); } } var r = factory(function initialize(O) { api.initializeInstanceElements(O, decorated.elements); }, superClass); var decorated = api.decorateClass(_coalesceClassElements(r.d.map(_createElementDescriptor)), decorators); api.initializeClassElements(r.F, decorated.elements); return api.runClassFinishers(r.F, decorated.finishers); }

function _getDecoratorsApi() { _getDecoratorsApi = function _getDecoratorsApi() { return api; }; var api = { elementsDefinitionOrder: [["method"], ["field"]], initializeInstanceElements: function initializeInstanceElements(O, elements) { ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { if (element.kind === kind && element.placement === "own") { this.defineClassElement(O, element); } }, this); }, this); }, initializeClassElements: function initializeClassElements(F, elements) { var proto = F.prototype; ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { var placement = element.placement; if (element.kind === kind && (placement === "static" || placement === "prototype")) { var receiver = placement === "static" ? F : proto; this.defineClassElement(receiver, element); } }, this); }, this); }, defineClassElement: function defineClassElement(receiver, element) { var descriptor = element.descriptor; if (element.kind === "field") { var initializer = element.initializer; descriptor = { enumerable: descriptor.enumerable, writable: descriptor.writable, configurable: descriptor.configurable, value: initializer === void 0 ? void 0 : initializer.call(receiver) }; } Object.defineProperty(receiver, element.key, descriptor); }, decorateClass: function decorateClass(elements, decorators) { var newElements = []; var finishers = []; var placements = { "static": [], prototype: [], own: [] }; elements.forEach(function (element) { this.addElementPlacement(element, placements); }, this); elements.forEach(function (element) { if (!_hasDecorators(element)) return newElements.push(element); var elementFinishersExtras = this.decorateElement(element, placements); newElements.push(elementFinishersExtras.element); newElements.push.apply(newElements, elementFinishersExtras.extras); finishers.push.apply(finishers, elementFinishersExtras.finishers); }, this); if (!decorators) { return { elements: newElements, finishers: finishers }; } var result = this.decorateConstructor(newElements, decorators); finishers.push.apply(finishers, result.finishers); result.finishers = finishers; return result; }, addElementPlacement: function addElementPlacement(element, placements, silent) { var keys = placements[element.placement]; if (!silent && keys.indexOf(element.key) !== -1) { throw new TypeError("Duplicated element (" + element.key + ")"); } keys.push(element.key); }, decorateElement: function decorateElement(element, placements) { var extras = []; var finishers = []; for (var decorators = element.decorators, i = decorators.length - 1; i >= 0; i--) { var keys = placements[element.placement]; keys.splice(keys.indexOf(element.key), 1); var elementObject = this.fromElementDescriptor(element); var elementFinisherExtras = this.toElementFinisherExtras((0, decorators[i])(elementObject) || elementObject); element = elementFinisherExtras.element; this.addElementPlacement(element, placements); if (elementFinisherExtras.finisher) { finishers.push(elementFinisherExtras.finisher); } var newExtras = elementFinisherExtras.extras; if (newExtras) { for (var j = 0; j < newExtras.length; j++) { this.addElementPlacement(newExtras[j], placements); } extras.push.apply(extras, newExtras); } } return { element: element, finishers: finishers, extras: extras }; }, decorateConstructor: function decorateConstructor(elements, decorators) { var finishers = []; for (var i = decorators.length - 1; i >= 0; i--) { var obj = this.fromClassDescriptor(elements); var elementsAndFinisher = this.toClassDescriptor((0, decorators[i])(obj) || obj); if (elementsAndFinisher.finisher !== undefined) { finishers.push(elementsAndFinisher.finisher); } if (elementsAndFinisher.elements !== undefined) { elements = elementsAndFinisher.elements; for (var j = 0; j < elements.length - 1; j++) { for (var k = j + 1; k < elements.length; k++) { if (elements[j].key === elements[k].key && elements[j].placement === elements[k].placement) { throw new TypeError("Duplicated element (" + elements[j].key + ")"); } } } } } return { elements: elements, finishers: finishers }; }, fromElementDescriptor: function fromElementDescriptor(element) { var obj = { kind: element.kind, key: element.key, placement: element.placement, descriptor: element.descriptor }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); if (element.kind === "field") obj.initializer = element.initializer; return obj; }, toElementDescriptors: function toElementDescriptors(elementObjects) { if (elementObjects === undefined) return; return _toArray(elementObjects).map(function (elementObject) { var element = this.toElementDescriptor(elementObject); this.disallowProperty(elementObject, "finisher", "An element descriptor"); this.disallowProperty(elementObject, "extras", "An element descriptor"); return element; }, this); }, toElementDescriptor: function toElementDescriptor(elementObject) { var kind = String(elementObject.kind); if (kind !== "method" && kind !== "field") { throw new TypeError('An element descriptor\'s .kind property must be either "method" or' + ' "field", but a decorator created an element descriptor with' + ' .kind "' + kind + '"'); } var key = _toPropertyKey(elementObject.key); var placement = String(elementObject.placement); if (placement !== "static" && placement !== "prototype" && placement !== "own") { throw new TypeError('An element descriptor\'s .placement property must be one of "static",' + ' "prototype" or "own", but a decorator created an element descriptor' + ' with .placement "' + placement + '"'); } var descriptor = elementObject.descriptor; this.disallowProperty(elementObject, "elements", "An element descriptor"); var element = { kind: kind, key: key, placement: placement, descriptor: Object.assign({}, descriptor) }; if (kind !== "field") { this.disallowProperty(elementObject, "initializer", "A method descriptor"); } else { this.disallowProperty(descriptor, "get", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "set", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "value", "The property descriptor of a field descriptor"); element.initializer = elementObject.initializer; } return element; }, toElementFinisherExtras: function toElementFinisherExtras(elementObject) { var element = this.toElementDescriptor(elementObject); var finisher = _optionalCallableProperty(elementObject, "finisher"); var extras = this.toElementDescriptors(elementObject.extras); return { element: element, finisher: finisher, extras: extras }; }, fromClassDescriptor: function fromClassDescriptor(elements) { var obj = { kind: "class", elements: elements.map(this.fromElementDescriptor, this) }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); return obj; }, toClassDescriptor: function toClassDescriptor(obj) { var kind = String(obj.kind); if (kind !== "class") { throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator' + ' created a class descriptor with .kind "' + kind + '"'); } this.disallowProperty(obj, "key", "A class descriptor"); this.disallowProperty(obj, "placement", "A class descriptor"); this.disallowProperty(obj, "descriptor", "A class descriptor"); this.disallowProperty(obj, "initializer", "A class descriptor"); this.disallowProperty(obj, "extras", "A class descriptor"); var finisher = _optionalCallableProperty(obj, "finisher"); var elements = this.toElementDescriptors(obj.elements); return { elements: elements, finisher: finisher }; }, runClassFinishers: function runClassFinishers(constructor, finishers) { for (var i = 0; i < finishers.length; i++) { var newConstructor = (0, finishers[i])(constructor); if (newConstructor !== undefined) { if (typeof newConstructor !== "function") { throw new TypeError("Finishers must return a constructor."); } constructor = newConstructor; } } return constructor; }, disallowProperty: function disallowProperty(obj, name, objectType) { if (obj[name] !== undefined) { throw new TypeError(objectType + " can't have a ." + name + " property."); } } }; return api; }

function _createElementDescriptor(def) { var key = _toPropertyKey(def.key); var descriptor; if (def.kind === "method") { descriptor = { value: def.value, writable: true, configurable: true, enumerable: false }; } else if (def.kind === "get") { descriptor = { get: def.value, configurable: true, enumerable: false }; } else if (def.kind === "set") { descriptor = { set: def.value, configurable: true, enumerable: false }; } else if (def.kind === "field") { descriptor = { configurable: true, writable: true, enumerable: true }; } var element = { kind: def.kind === "field" ? "field" : "method", key: key, placement: def["static"] ? "static" : def.kind === "field" ? "own" : "prototype", descriptor: descriptor }; if (def.decorators) element.decorators = def.decorators; if (def.kind === "field") element.initializer = def.value; return element; }

function _coalesceGetterSetter(element, other) { if (element.descriptor.get !== undefined) { other.descriptor.get = element.descriptor.get; } else { other.descriptor.set = element.descriptor.set; } }

function _coalesceClassElements(elements) { var newElements = []; var isSameElement = function isSameElement(other) { return other.kind === "method" && other.key === element.key && other.placement === element.placement; }; for (var i = 0; i < elements.length; i++) { var element = elements[i]; var other; if (element.kind === "method" && (other = newElements.find(isSameElement))) { if (_isDataDescriptor(element.descriptor) || _isDataDescriptor(other.descriptor)) { if (_hasDecorators(element) || _hasDecorators(other)) { throw new ReferenceError("Duplicated methods (" + element.key + ") can't be decorated."); } other.descriptor = element.descriptor; } else { if (_hasDecorators(element)) { if (_hasDecorators(other)) { throw new ReferenceError("Decorators can't be placed on different accessors with for " + "the same property (" + element.key + ")."); } other.decorators = element.decorators; } _coalesceGetterSetter(element, other); } } else { newElements.push(element); } } return newElements; }

function _hasDecorators(element) { return element.decorators && element.decorators.length; }

function _isDataDescriptor(desc) { return desc !== undefined && !(desc.value === undefined && desc.writable === undefined); }

function _optionalCallableProperty(obj, name) { var value = obj[name]; if (value !== undefined && typeof value !== "function") { throw new TypeError("Expected '" + name + "' to be a function"); } return value; }

function _toPropertyKey(arg) { var key = _toPrimitive(arg, "string"); return _typeof(key) === "symbol" ? key : String(key); }

function _toPrimitive(input, hint) { if (_typeof(input) !== "object" || input === null) return input; var prim = input[Symbol.toPrimitive]; if (prim !== undefined) { var res = prim.call(input, hint || "default"); if (_typeof(res) !== "object") return res; throw new TypeError("@@toPrimitive must return a primitive value."); } return (hint === "string" ? String : Number)(input); }

function _toArray(arr) { return _arrayWithHoles(arr) || _iterableToArray(arr) || _unsupportedIterableToArray(arr) || _nonIterableRest(); }

function _nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function _unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return _arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(n); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return _arrayLikeToArray(o, minLen); }

function _arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function _iterableToArray(iter) { if (typeof Symbol !== "undefined" && Symbol.iterator in Object(iter)) return Array.from(iter); }

function _arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }




var LoadingScreen = _decorate([Object(lit_element__WEBPACK_IMPORTED_MODULE_1__[/* customElement */ "d"])("loading-screen")], function (_initialize, _LitElement) {
  var LoadingScreen = /*#__PURE__*/function (_LitElement2) {
    _inherits(LoadingScreen, _LitElement2);

    var _super = _createSuper(LoadingScreen);

    function LoadingScreen() {
      var _this;

      _classCallCheck(this, LoadingScreen);

      for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
        args[_key] = arguments[_key];
      }

      _this = _super.call.apply(_super, [this].concat(args));

      _initialize(_assertThisInitialized(_this));

      return _this;
    }

    return LoadingScreen;
  }(_LitElement);

  return {
    F: LoadingScreen,
    d: [{
      kind: "method",
      key: "render",
      value: function render() {
        return Object(lit_element__WEBPACK_IMPORTED_MODULE_1__[/* html */ "e"])(_templateObject());
      }
    }, {
      kind: "get",
      "static": true,
      key: "styles",
      value: function styles() {
        return Object(lit_element__WEBPACK_IMPORTED_MODULE_1__[/* css */ "c"])(_templateObject2());
      }
    }]
  };
}, lit_element__WEBPACK_IMPORTED_MODULE_1__[/* LitElement */ "a"]);

/***/ }),

/***/ 91:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "a", function() { return atLeastVersion; });
function _slicedToArray(arr, i) { return _arrayWithHoles(arr) || _iterableToArrayLimit(arr, i) || _unsupportedIterableToArray(arr, i) || _nonIterableRest(); }

function _nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function _unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return _arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(n); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return _arrayLikeToArray(o, minLen); }

function _arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function _iterableToArrayLimit(arr, i) { if (typeof Symbol === "undefined" || !(Symbol.iterator in Object(arr))) return; var _arr = []; var _n = true; var _d = false; var _e = undefined; try { for (var _i = arr[Symbol.iterator](), _s; !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i["return"] != null) _i["return"](); } finally { if (_d) throw _e; } } return _arr; }

function _arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }

var atLeastVersion = function atLeastVersion(version, major, minor) {
  var _version$split = version.split(".", 2),
      _version$split2 = _slicedToArray(_version$split, 2),
      haMajor = _version$split2[0],
      haMinor = _version$split2[1];

  return Number(haMajor) > major || Number(haMajor) === major && Number(haMinor) >= minor;
};

/***/ }),

/***/ 99:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";

// EXTERNAL MODULE: ./node_modules/lit-element/lit-element.js + 3 modules
var lit_element = __webpack_require__(5);

// EXTERNAL MODULE: ./src/common/dom/fire_event.ts
var fire_event = __webpack_require__(12);

// CONCATENATED MODULE: ./src/common/entity/compute_domain.ts
var computeDomain = function computeDomain(entityId) {
  return entityId.substr(0, entityId.indexOf("."));
};
// EXTERNAL MODULE: ./node_modules/home-assistant-js-websocket/dist/collection.js + 1 modules
var collection = __webpack_require__(194);

// CONCATENATED MODULE: ./src/data/persistent_notification.ts


var fetchNotifications = function fetchNotifications(conn) {
  return conn.sendMessagePromise({
    type: "persistent_notification/get"
  });
};

var subscribeUpdates = function subscribeUpdates(conn, store) {
  return conn.subscribeEvents(function () {
    return fetchNotifications(conn).then(function (ntf) {
      return store.setState(ntf, true);
    });
  }, "persistent_notifications_updated");
};

var persistent_notification_subscribeNotifications = function subscribeNotifications(conn, onChange) {
  return Object(collection["a" /* createCollection */])("_ntf", fetchNotifications, subscribeUpdates, conn, onChange);
};
// EXTERNAL MODULE: ./src/components/ha-icon-button.ts
var ha_icon_button = __webpack_require__(23);

// CONCATENATED MODULE: ./src/components/ha-menu-button.ts
function _typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { _typeof = function _typeof(obj) { return typeof obj; }; } else { _typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return _typeof(obj); }

function _templateObject3() {
  var data = _taggedTemplateLiteral(["\n      :host {\n        position: relative;\n      }\n      .dot {\n        pointer-events: none;\n        position: absolute;\n        background-color: var(--accent-color);\n        width: 12px;\n        height: 12px;\n        top: 5px;\n        right: 2px;\n        border-radius: 50%;\n        border: 2px solid var(--app-header-background-color);\n      }\n    "]);

  _templateObject3 = function _templateObject3() {
    return data;
  };

  return data;
}

function _templateObject2() {
  var data = _taggedTemplateLiteral([" <div class=\"dot\"></div> "]);

  _templateObject2 = function _templateObject2() {
    return data;
  };

  return data;
}

function _templateObject() {
  var data = _taggedTemplateLiteral(["\n      <ha-icon-button\n        aria-label=", "\n        icon=\"hass:menu\"\n        @click=", "\n      ></ha-icon-button>\n      ", "\n    "]);

  _templateObject = function _templateObject() {
    return data;
  };

  return data;
}

function _taggedTemplateLiteral(strings, raw) { if (!raw) { raw = strings.slice(0); } return Object.freeze(Object.defineProperties(strings, { raw: { value: Object.freeze(raw) } })); }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) _setPrototypeOf(subClass, superClass); }

function _setPrototypeOf(o, p) { _setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return _setPrototypeOf(o, p); }

function _createSuper(Derived) { return function () { var Super = _getPrototypeOf(Derived), result; if (_isNativeReflectConstruct()) { var NewTarget = _getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return _possibleConstructorReturn(this, result); }; }

function _possibleConstructorReturn(self, call) { if (call && (_typeof(call) === "object" || typeof call === "function")) { return call; } return _assertThisInitialized(self); }

function _assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function _isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Date.prototype.toString.call(Reflect.construct(Date, [], function () {})); return true; } catch (e) { return false; } }

function _decorate(decorators, factory, superClass, mixins) { var api = _getDecoratorsApi(); if (mixins) { for (var i = 0; i < mixins.length; i++) { api = mixins[i](api); } } var r = factory(function initialize(O) { api.initializeInstanceElements(O, decorated.elements); }, superClass); var decorated = api.decorateClass(_coalesceClassElements(r.d.map(_createElementDescriptor)), decorators); api.initializeClassElements(r.F, decorated.elements); return api.runClassFinishers(r.F, decorated.finishers); }

function _getDecoratorsApi() { _getDecoratorsApi = function _getDecoratorsApi() { return api; }; var api = { elementsDefinitionOrder: [["method"], ["field"]], initializeInstanceElements: function initializeInstanceElements(O, elements) { ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { if (element.kind === kind && element.placement === "own") { this.defineClassElement(O, element); } }, this); }, this); }, initializeClassElements: function initializeClassElements(F, elements) { var proto = F.prototype; ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { var placement = element.placement; if (element.kind === kind && (placement === "static" || placement === "prototype")) { var receiver = placement === "static" ? F : proto; this.defineClassElement(receiver, element); } }, this); }, this); }, defineClassElement: function defineClassElement(receiver, element) { var descriptor = element.descriptor; if (element.kind === "field") { var initializer = element.initializer; descriptor = { enumerable: descriptor.enumerable, writable: descriptor.writable, configurable: descriptor.configurable, value: initializer === void 0 ? void 0 : initializer.call(receiver) }; } Object.defineProperty(receiver, element.key, descriptor); }, decorateClass: function decorateClass(elements, decorators) { var newElements = []; var finishers = []; var placements = { "static": [], prototype: [], own: [] }; elements.forEach(function (element) { this.addElementPlacement(element, placements); }, this); elements.forEach(function (element) { if (!_hasDecorators(element)) return newElements.push(element); var elementFinishersExtras = this.decorateElement(element, placements); newElements.push(elementFinishersExtras.element); newElements.push.apply(newElements, elementFinishersExtras.extras); finishers.push.apply(finishers, elementFinishersExtras.finishers); }, this); if (!decorators) { return { elements: newElements, finishers: finishers }; } var result = this.decorateConstructor(newElements, decorators); finishers.push.apply(finishers, result.finishers); result.finishers = finishers; return result; }, addElementPlacement: function addElementPlacement(element, placements, silent) { var keys = placements[element.placement]; if (!silent && keys.indexOf(element.key) !== -1) { throw new TypeError("Duplicated element (" + element.key + ")"); } keys.push(element.key); }, decorateElement: function decorateElement(element, placements) { var extras = []; var finishers = []; for (var decorators = element.decorators, i = decorators.length - 1; i >= 0; i--) { var keys = placements[element.placement]; keys.splice(keys.indexOf(element.key), 1); var elementObject = this.fromElementDescriptor(element); var elementFinisherExtras = this.toElementFinisherExtras((0, decorators[i])(elementObject) || elementObject); element = elementFinisherExtras.element; this.addElementPlacement(element, placements); if (elementFinisherExtras.finisher) { finishers.push(elementFinisherExtras.finisher); } var newExtras = elementFinisherExtras.extras; if (newExtras) { for (var j = 0; j < newExtras.length; j++) { this.addElementPlacement(newExtras[j], placements); } extras.push.apply(extras, newExtras); } } return { element: element, finishers: finishers, extras: extras }; }, decorateConstructor: function decorateConstructor(elements, decorators) { var finishers = []; for (var i = decorators.length - 1; i >= 0; i--) { var obj = this.fromClassDescriptor(elements); var elementsAndFinisher = this.toClassDescriptor((0, decorators[i])(obj) || obj); if (elementsAndFinisher.finisher !== undefined) { finishers.push(elementsAndFinisher.finisher); } if (elementsAndFinisher.elements !== undefined) { elements = elementsAndFinisher.elements; for (var j = 0; j < elements.length - 1; j++) { for (var k = j + 1; k < elements.length; k++) { if (elements[j].key === elements[k].key && elements[j].placement === elements[k].placement) { throw new TypeError("Duplicated element (" + elements[j].key + ")"); } } } } } return { elements: elements, finishers: finishers }; }, fromElementDescriptor: function fromElementDescriptor(element) { var obj = { kind: element.kind, key: element.key, placement: element.placement, descriptor: element.descriptor }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); if (element.kind === "field") obj.initializer = element.initializer; return obj; }, toElementDescriptors: function toElementDescriptors(elementObjects) { if (elementObjects === undefined) return; return _toArray(elementObjects).map(function (elementObject) { var element = this.toElementDescriptor(elementObject); this.disallowProperty(elementObject, "finisher", "An element descriptor"); this.disallowProperty(elementObject, "extras", "An element descriptor"); return element; }, this); }, toElementDescriptor: function toElementDescriptor(elementObject) { var kind = String(elementObject.kind); if (kind !== "method" && kind !== "field") { throw new TypeError('An element descriptor\'s .kind property must be either "method" or' + ' "field", but a decorator created an element descriptor with' + ' .kind "' + kind + '"'); } var key = _toPropertyKey(elementObject.key); var placement = String(elementObject.placement); if (placement !== "static" && placement !== "prototype" && placement !== "own") { throw new TypeError('An element descriptor\'s .placement property must be one of "static",' + ' "prototype" or "own", but a decorator created an element descriptor' + ' with .placement "' + placement + '"'); } var descriptor = elementObject.descriptor; this.disallowProperty(elementObject, "elements", "An element descriptor"); var element = { kind: kind, key: key, placement: placement, descriptor: Object.assign({}, descriptor) }; if (kind !== "field") { this.disallowProperty(elementObject, "initializer", "A method descriptor"); } else { this.disallowProperty(descriptor, "get", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "set", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "value", "The property descriptor of a field descriptor"); element.initializer = elementObject.initializer; } return element; }, toElementFinisherExtras: function toElementFinisherExtras(elementObject) { var element = this.toElementDescriptor(elementObject); var finisher = _optionalCallableProperty(elementObject, "finisher"); var extras = this.toElementDescriptors(elementObject.extras); return { element: element, finisher: finisher, extras: extras }; }, fromClassDescriptor: function fromClassDescriptor(elements) { var obj = { kind: "class", elements: elements.map(this.fromElementDescriptor, this) }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); return obj; }, toClassDescriptor: function toClassDescriptor(obj) { var kind = String(obj.kind); if (kind !== "class") { throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator' + ' created a class descriptor with .kind "' + kind + '"'); } this.disallowProperty(obj, "key", "A class descriptor"); this.disallowProperty(obj, "placement", "A class descriptor"); this.disallowProperty(obj, "descriptor", "A class descriptor"); this.disallowProperty(obj, "initializer", "A class descriptor"); this.disallowProperty(obj, "extras", "A class descriptor"); var finisher = _optionalCallableProperty(obj, "finisher"); var elements = this.toElementDescriptors(obj.elements); return { elements: elements, finisher: finisher }; }, runClassFinishers: function runClassFinishers(constructor, finishers) { for (var i = 0; i < finishers.length; i++) { var newConstructor = (0, finishers[i])(constructor); if (newConstructor !== undefined) { if (typeof newConstructor !== "function") { throw new TypeError("Finishers must return a constructor."); } constructor = newConstructor; } } return constructor; }, disallowProperty: function disallowProperty(obj, name, objectType) { if (obj[name] !== undefined) { throw new TypeError(objectType + " can't have a ." + name + " property."); } } }; return api; }

function _createElementDescriptor(def) { var key = _toPropertyKey(def.key); var descriptor; if (def.kind === "method") { descriptor = { value: def.value, writable: true, configurable: true, enumerable: false }; } else if (def.kind === "get") { descriptor = { get: def.value, configurable: true, enumerable: false }; } else if (def.kind === "set") { descriptor = { set: def.value, configurable: true, enumerable: false }; } else if (def.kind === "field") { descriptor = { configurable: true, writable: true, enumerable: true }; } var element = { kind: def.kind === "field" ? "field" : "method", key: key, placement: def["static"] ? "static" : def.kind === "field" ? "own" : "prototype", descriptor: descriptor }; if (def.decorators) element.decorators = def.decorators; if (def.kind === "field") element.initializer = def.value; return element; }

function _coalesceGetterSetter(element, other) { if (element.descriptor.get !== undefined) { other.descriptor.get = element.descriptor.get; } else { other.descriptor.set = element.descriptor.set; } }

function _coalesceClassElements(elements) { var newElements = []; var isSameElement = function isSameElement(other) { return other.kind === "method" && other.key === element.key && other.placement === element.placement; }; for (var i = 0; i < elements.length; i++) { var element = elements[i]; var other; if (element.kind === "method" && (other = newElements.find(isSameElement))) { if (_isDataDescriptor(element.descriptor) || _isDataDescriptor(other.descriptor)) { if (_hasDecorators(element) || _hasDecorators(other)) { throw new ReferenceError("Duplicated methods (" + element.key + ") can't be decorated."); } other.descriptor = element.descriptor; } else { if (_hasDecorators(element)) { if (_hasDecorators(other)) { throw new ReferenceError("Decorators can't be placed on different accessors with for " + "the same property (" + element.key + ")."); } other.decorators = element.decorators; } _coalesceGetterSetter(element, other); } } else { newElements.push(element); } } return newElements; }

function _hasDecorators(element) { return element.decorators && element.decorators.length; }

function _isDataDescriptor(desc) { return desc !== undefined && !(desc.value === undefined && desc.writable === undefined); }

function _optionalCallableProperty(obj, name) { var value = obj[name]; if (value !== undefined && typeof value !== "function") { throw new TypeError("Expected '" + name + "' to be a function"); } return value; }

function _toPropertyKey(arg) { var key = _toPrimitive(arg, "string"); return _typeof(key) === "symbol" ? key : String(key); }

function _toPrimitive(input, hint) { if (_typeof(input) !== "object" || input === null) return input; var prim = input[Symbol.toPrimitive]; if (prim !== undefined) { var res = prim.call(input, hint || "default"); if (_typeof(res) !== "object") return res; throw new TypeError("@@toPrimitive must return a primitive value."); } return (hint === "string" ? String : Number)(input); }

function _toArray(arr) { return _arrayWithHoles(arr) || _iterableToArray(arr) || _unsupportedIterableToArray(arr) || _nonIterableRest(); }

function _nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function _unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return _arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(n); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return _arrayLikeToArray(o, minLen); }

function _arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function _iterableToArray(iter) { if (typeof Symbol !== "undefined" && Symbol.iterator in Object(iter)) return Array.from(iter); }

function _arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }

function _get(target, property, receiver) { if (typeof Reflect !== "undefined" && Reflect.get) { _get = Reflect.get; } else { _get = function _get(target, property, receiver) { var base = _superPropBase(target, property); if (!base) return; var desc = Object.getOwnPropertyDescriptor(base, property); if (desc.get) { return desc.get.call(receiver); } return desc.value; }; } return _get(target, property, receiver || target); }

function _superPropBase(object, property) { while (!Object.prototype.hasOwnProperty.call(object, property)) { object = _getPrototypeOf(object); if (object === null) break; } return object; }

function _getPrototypeOf(o) { _getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return _getPrototypeOf(o); }







var ha_menu_button_HaMenuButton = _decorate([Object(lit_element["d" /* customElement */])("ha-menu-button")], function (_initialize, _LitElement) {
  var HaMenuButton = /*#__PURE__*/function (_LitElement2) {
    _inherits(HaMenuButton, _LitElement2);

    var _super = _createSuper(HaMenuButton);

    function HaMenuButton() {
      var _this;

      _classCallCheck(this, HaMenuButton);

      for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
        args[_key] = arguments[_key];
      }

      _this = _super.call.apply(_super, [this].concat(args));

      _initialize(_assertThisInitialized(_this));

      return _this;
    }

    return HaMenuButton;
  }(_LitElement);

  return {
    F: HaMenuButton,
    d: [{
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])({
        type: Boolean
      })],
      key: "hassio",
      value: function value() {
        return false;
      }
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "narrow",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "hass",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "_hasNotifications",
      value: function value() {
        return false;
      }
    }, {
      kind: "field",
      key: "_alwaysVisible",
      value: function value() {
        return false;
      }
    }, {
      kind: "field",
      key: "_attachNotifOnConnect",
      value: function value() {
        return false;
      }
    }, {
      kind: "field",
      key: "_unsubNotifications",
      value: void 0
    }, {
      kind: "method",
      key: "connectedCallback",
      value: function connectedCallback() {
        _get(_getPrototypeOf(HaMenuButton.prototype), "connectedCallback", this).call(this);

        if (this._attachNotifOnConnect) {
          this._attachNotifOnConnect = false;

          this._subscribeNotifications();
        }
      }
    }, {
      kind: "method",
      key: "disconnectedCallback",
      value: function disconnectedCallback() {
        _get(_getPrototypeOf(HaMenuButton.prototype), "disconnectedCallback", this).call(this);

        if (this._unsubNotifications) {
          this._attachNotifOnConnect = true;

          this._unsubNotifications();

          this._unsubNotifications = undefined;
        }
      }
    }, {
      kind: "method",
      key: "render",
      value: function render() {
        var hasNotifications = (this.narrow || this.hass.dockedSidebar === "always_hidden") && (this._hasNotifications || Object.keys(this.hass.states).some(function (entityId) {
          return computeDomain(entityId) === "configurator";
        }));
        return Object(lit_element["e" /* html */])(_templateObject(), this.hass.localize("ui.sidebar.sidebar_toggle"), this._toggleMenu, hasNotifications ? Object(lit_element["e" /* html */])(_templateObject2()) : "");
      }
    }, {
      kind: "method",
      key: "firstUpdated",
      value: function firstUpdated(changedProps) {
        _get(_getPrototypeOf(HaMenuButton.prototype), "firstUpdated", this).call(this, changedProps);

        if (!this.hassio) {
          return;
        } // This component is used on Hass.io too, but Hass.io might run the UI
        // on older frontends too, that don't have an always visible menu button
        // in the sidebar.


        this._alwaysVisible = (Number(window.parent.frontendVersion) || 0) < 20190710;
      }
    }, {
      kind: "method",
      key: "updated",
      value: function updated(changedProps) {
        _get(_getPrototypeOf(HaMenuButton.prototype), "updated", this).call(this, changedProps);

        if (!changedProps.has("narrow") && !changedProps.has("hass")) {
          return;
        }

        var oldHass = changedProps.get("hass");
        var oldNarrow = changedProps.get("narrow") || oldHass && oldHass.dockedSidebar === "always_hidden";
        var newNarrow = this.narrow || this.hass.dockedSidebar === "always_hidden";

        if (oldNarrow === newNarrow) {
          return;
        }

        this.style.visibility = newNarrow || this._alwaysVisible ? "initial" : "hidden";

        if (!newNarrow) {
          this._hasNotifications = false;

          if (this._unsubNotifications) {
            this._unsubNotifications();

            this._unsubNotifications = undefined;
          }

          return;
        }

        this._subscribeNotifications();
      }
    }, {
      kind: "method",
      key: "_subscribeNotifications",
      value: function _subscribeNotifications() {
        var _this2 = this;

        this._unsubNotifications = persistent_notification_subscribeNotifications(this.hass.connection, function (notifications) {
          _this2._hasNotifications = notifications.length > 0;
        });
      }
    }, {
      kind: "method",
      key: "_toggleMenu",
      value: function _toggleMenu() {
        Object(fire_event["a" /* fireEvent */])(this, "hass-toggle-menu");
      }
    }, {
      kind: "get",
      "static": true,
      key: "styles",
      value: function styles() {
        return Object(lit_element["c" /* css */])(_templateObject3());
      }
    }]
  };
}, lit_element["a" /* LitElement */]);

/***/ })

}]);