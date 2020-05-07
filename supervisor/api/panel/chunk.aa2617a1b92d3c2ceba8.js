(self["webpackJsonp"] = self["webpackJsonp"] || []).push([[6],{

/***/ 102:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";

// EXTERNAL MODULE: ./node_modules/@material/mwc-ripple/ripple-directive.js + 1 modules
var ripple_directive = __webpack_require__(59);

// EXTERNAL MODULE: ./node_modules/@material/mwc-switch/mwc-switch.js + 4 modules
var mwc_switch = __webpack_require__(135);

// EXTERNAL MODULE: ./node_modules/@material/mwc-switch/mwc-switch-css.js
var mwc_switch_css = __webpack_require__(96);

// EXTERNAL MODULE: ./node_modules/lit-element/lit-element.js + 3 modules
var lit_element = __webpack_require__(5);

// EXTERNAL MODULE: ./src/common/dom/fire_event.ts
var fire_event = __webpack_require__(12);

// CONCATENATED MODULE: ./src/data/haptics.ts
/**
 * Broadcast haptic feedback requests
 */
 // Allowed types are from iOS HIG.
// https://developer.apple.com/design/human-interface-guidelines/ios/user-interaction/feedback/#haptics
// Implementors on platforms other than iOS should attempt to match the patterns (shown in HIG) as closely as possible.

var haptics_forwardHaptic = function forwardHaptic(hapticType) {
  Object(fire_event["a" /* fireEvent */])(window, "haptic", hapticType);
};
// CONCATENATED MODULE: ./src/components/ha-switch.ts
/* unused harmony export HaSwitch */
function _typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { _typeof = function _typeof(obj) { return typeof obj; }; } else { _typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return _typeof(obj); }

function _templateObject2() {
  var data = _taggedTemplateLiteral(["\n        :host {\n          display: flex;\n          flex-direction: row;\n          align-items: center;\n        }\n        .mdc-switch.mdc-switch--checked .mdc-switch__thumb {\n          background-color: var(--switch-checked-button-color);\n          border-color: var(--switch-checked-button-color);\n        }\n        .mdc-switch.mdc-switch--checked .mdc-switch__track {\n          background-color: var(--switch-checked-track-color);\n          border-color: var(--switch-checked-track-color);\n        }\n        .mdc-switch:not(.mdc-switch--checked) .mdc-switch__thumb {\n          background-color: var(--switch-unchecked-button-color);\n          border-color: var(--switch-unchecked-button-color);\n        }\n        .mdc-switch:not(.mdc-switch--checked) .mdc-switch__track {\n          background-color: var(--switch-unchecked-track-color);\n          border-color: var(--switch-unchecked-track-color);\n        }\n        :host(.slotted) .mdc-switch {\n          margin-right: 24px;\n        }\n      "]);

  _templateObject2 = function _templateObject2() {
    return data;
  };

  return data;
}

function _templateObject() {
  var data = _taggedTemplateLiteral(["\n      <div class=\"mdc-switch\">\n        <div class=\"mdc-switch__track\"></div>\n        <div\n          class=\"mdc-switch__thumb-underlay\"\n          .ripple=\"", "\"\n        >\n          <div class=\"mdc-switch__thumb\">\n            <input\n              type=\"checkbox\"\n              id=\"basic-switch\"\n              class=\"mdc-switch__native-control\"\n              role=\"switch\"\n              @change=\"", "\"\n            />\n          </div>\n        </div>\n      </div>\n      <label for=\"basic-switch\"><slot></slot></label>\n    "]);

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






var MwcSwitch = customElements.get("mwc-switch");
var ha_switch_HaSwitch = _decorate([Object(lit_element["d" /* customElement */])("ha-switch")], function (_initialize, _MwcSwitch) {
  var HaSwitch = /*#__PURE__*/function (_MwcSwitch2) {
    _inherits(HaSwitch, _MwcSwitch2);

    var _super = _createSuper(HaSwitch);

    function HaSwitch() {
      var _this;

      _classCallCheck(this, HaSwitch);

      for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
        args[_key] = arguments[_key];
      }

      _this = _super.call.apply(_super, [this].concat(args));

      _initialize(_assertThisInitialized(_this));

      return _this;
    }

    return HaSwitch;
  }(_MwcSwitch);

  return {
    F: HaSwitch,
    d: [{
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])({
        type: Boolean
      })],
      key: "haptic",
      value: function value() {
        return false;
      }
    }, {
      kind: "field",
      decorators: [Object(lit_element["g" /* query */])("slot")],
      key: "_slot",
      value: void 0
    }, {
      kind: "method",
      key: "firstUpdated",
      value: // Generate a haptic vibration.
      // Only set to true if the new value of the switch is applied right away when toggling.
      // Do not add haptic when a user is required to press save.
      function firstUpdated() {
        var _this2 = this;

        _get(_getPrototypeOf(HaSwitch.prototype), "firstUpdated", this).call(this);

        this.style.setProperty("--mdc-theme-secondary", "var(--switch-checked-color)");
        this.classList.toggle("slotted", Boolean(this._slot.assignedNodes().length));
        this.addEventListener("change", function () {
          if (_this2.haptic) {
            haptics_forwardHaptic("light");
          }
        });
      }
    }, {
      kind: "method",
      key: "render",
      value: function render() {
        return Object(lit_element["e" /* html */])(_templateObject(), Object(ripple_directive["a" /* ripple */])({
          interactionNode: this
        }), this._haChangeHandler);
      }
    }, {
      kind: "get",
      "static": true,
      key: "styles",
      value: function styles() {
        return [mwc_switch_css["a" /* style */], Object(lit_element["c" /* css */])(_templateObject2())];
      }
    }, {
      kind: "method",
      key: "_haChangeHandler",
      value: function _haChangeHandler(e) {
        this.mdcFoundation.handleChange(e); // catch "click" event and sync properties

        this.checked = this.formElement.checked;
      }
    }]
  };
}, MwcSwitch);

/***/ }),

/***/ 192:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);

// EXTERNAL MODULE: ./src/components/ha-icon-button.ts
var ha_icon_button = __webpack_require__(23);

// EXTERNAL MODULE: ./node_modules/@polymer/paper-spinner/paper-spinner-lite.js
var paper_spinner_lite = __webpack_require__(35);

// EXTERNAL MODULE: ./node_modules/lit-element/lit-element.js + 3 modules
var lit_element = __webpack_require__(5);

// EXTERNAL MODULE: ./node_modules/memoize-one/dist/memoize-one.esm.js
var memoize_one_esm = __webpack_require__(50);

// EXTERNAL MODULE: ./src/data/hassio/addon.ts
var hassio_addon = __webpack_require__(22);

// EXTERNAL MODULE: ./src/resources/styles.ts
var resources_styles = __webpack_require__(11);

// EXTERNAL MODULE: ./hassio/src/resources/hassio-style.ts
var hassio_style = __webpack_require__(13);

// EXTERNAL MODULE: ./node_modules/@material/mwc-button/mwc-button.js + 12 modules
var mwc_button = __webpack_require__(18);

// EXTERNAL MODULE: ./node_modules/@polymer/paper-card/paper-card.js + 2 modules
var paper_card = __webpack_require__(20);

// EXTERNAL MODULE: ./node_modules/@polymer/paper-dropdown-menu/paper-dropdown-menu.js + 3 modules
var paper_dropdown_menu = __webpack_require__(136);

// EXTERNAL MODULE: ./node_modules/@polymer/paper-item/paper-item.js + 2 modules
var paper_item = __webpack_require__(100);

// EXTERNAL MODULE: ./node_modules/@polymer/paper-listbox/paper-listbox.js
var paper_listbox = __webpack_require__(129);

// EXTERNAL MODULE: ./node_modules/web-animations-js/web-animations-next-lite.min.js
var web_animations_next_lite_min = __webpack_require__(150);

// EXTERNAL MODULE: ./src/data/hassio/hardware.ts
var hardware = __webpack_require__(127);

// EXTERNAL MODULE: ./src/dialogs/generic/show-dialog-box.ts
var show_dialog_box = __webpack_require__(39);

// CONCATENATED MODULE: ./hassio/src/dialogs/suggestAddonRestart.ts
function asyncGeneratorStep(gen, resolve, reject, _next, _throw, key, arg) { try { var info = gen[key](arg); var value = info.value; } catch (error) { reject(error); return; } if (info.done) { resolve(value); } else { Promise.resolve(value).then(_next, _throw); } }

function _asyncToGenerator(fn) { return function () { var self = this, args = arguments; return new Promise(function (resolve, reject) { var gen = fn.apply(self, args); function _next(value) { asyncGeneratorStep(gen, resolve, reject, _next, _throw, "next", value); } function _throw(err) { asyncGeneratorStep(gen, resolve, reject, _next, _throw, "throw", err); } _next(undefined); }); }; }



var suggestAddonRestart = /*#__PURE__*/function () {
  var _ref = _asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee(element, hass, addon) {
    var confirmed;
    return regeneratorRuntime.wrap(function _callee$(_context) {
      while (1) {
        switch (_context.prev = _context.next) {
          case 0:
            _context.next = 2;
            return Object(show_dialog_box["b" /* showConfirmationDialog */])(element, {
              title: addon.name,
              text: "Do you want to restart the add-on with your changes?",
              confirmText: "restart add-on",
              dismissText: "no"
            });

          case 2:
            confirmed = _context.sent;

            if (!confirmed) {
              _context.next = 12;
              break;
            }

            _context.prev = 4;
            _context.next = 7;
            return Object(hassio_addon["h" /* restartHassioAddon */])(hass, addon.slug);

          case 7:
            _context.next = 12;
            break;

          case 9:
            _context.prev = 9;
            _context.t0 = _context["catch"](4);
            Object(show_dialog_box["a" /* showAlertDialog */])(element, {
              title: "Failed to restart",
              text: _context.t0.body.message
            });

          case 12:
          case "end":
            return _context.stop();
        }
      }
    }, _callee, null, [[4, 9]]);
  }));

  return function suggestAddonRestart(_x, _x2, _x3) {
    return _ref.apply(this, arguments);
  };
}();
// CONCATENATED MODULE: ./hassio/src/addon-view/config/hassio-addon-audio.ts
function _typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { _typeof = function _typeof(obj) { return typeof obj; }; } else { _typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return _typeof(obj); }

function _toConsumableArray(arr) { return _arrayWithoutHoles(arr) || _iterableToArray(arr) || _unsupportedIterableToArray(arr) || _nonIterableSpread(); }

function _nonIterableSpread() { throw new TypeError("Invalid attempt to spread non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function _arrayWithoutHoles(arr) { if (Array.isArray(arr)) return _arrayLikeToArray(arr); }

function hassio_addon_audio_asyncGeneratorStep(gen, resolve, reject, _next, _throw, key, arg) { try { var info = gen[key](arg); var value = info.value; } catch (error) { reject(error); return; } if (info.done) { resolve(value); } else { Promise.resolve(value).then(_next, _throw); } }

function hassio_addon_audio_asyncToGenerator(fn) { return function () { var self = this, args = arguments; return new Promise(function (resolve, reject) { var gen = fn.apply(self, args); function _next(value) { hassio_addon_audio_asyncGeneratorStep(gen, resolve, reject, _next, _throw, "next", value); } function _throw(err) { hassio_addon_audio_asyncGeneratorStep(gen, resolve, reject, _next, _throw, "throw", err); } _next(undefined); }); }; }

function _templateObject5() {
  var data = _taggedTemplateLiteral(["\n        :host,\n        paper-card,\n        paper-dropdown-menu {\n          display: block;\n        }\n        .errors {\n          color: var(--google-red-500);\n          margin-bottom: 16px;\n        }\n        paper-item {\n          width: 450px;\n        }\n        .card-actions {\n          text-align: right;\n        }\n      "]);

  _templateObject5 = function _templateObject5() {
    return data;
  };

  return data;
}

function _templateObject4() {
  var data = _taggedTemplateLiteral(["\n                  <paper-item device=", "\n                    >", "</paper-item\n                  >\n                "]);

  _templateObject4 = function _templateObject4() {
    return data;
  };

  return data;
}

function _templateObject3() {
  var data = _taggedTemplateLiteral(["\n                  <paper-item device=", "\n                    >", "</paper-item\n                  >\n                "]);

  _templateObject3 = function _templateObject3() {
    return data;
  };

  return data;
}

function _templateObject2() {
  var data = _taggedTemplateLiteral([" <div class=\"errors\">", "</div> "]);

  _templateObject2 = function _templateObject2() {
    return data;
  };

  return data;
}

function _templateObject() {
  var data = _taggedTemplateLiteral(["\n      <paper-card heading=\"Audio\">\n        <div class=\"card-content\">\n          ", "\n\n          <paper-dropdown-menu\n            label=\"Input\"\n            @iron-select=", "\n          >\n            <paper-listbox\n              slot=\"dropdown-content\"\n              attr-for-selected=\"device\"\n              .selected=", "\n            >\n              ", "\n            </paper-listbox>\n          </paper-dropdown-menu>\n          <paper-dropdown-menu\n            label=\"Output\"\n            @iron-select=", "\n          >\n            <paper-listbox\n              slot=\"dropdown-content\"\n              attr-for-selected=\"device\"\n              .selected=", "\n            >\n              ", "\n            </paper-listbox>\n          </paper-dropdown-menu>\n        </div>\n        <div class=\"card-actions\">\n          <mwc-button @click=", ">Save</mwc-button>\n        </div>\n      </paper-card>\n    "]);

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














var hassio_addon_audio_HassioAddonAudio = _decorate([Object(lit_element["d" /* customElement */])("hassio-addon-audio")], function (_initialize, _LitElement) {
  var HassioAddonAudio = /*#__PURE__*/function (_LitElement2) {
    _inherits(HassioAddonAudio, _LitElement2);

    var _super = _createSuper(HassioAddonAudio);

    function HassioAddonAudio() {
      var _this;

      _classCallCheck(this, HassioAddonAudio);

      for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
        args[_key] = arguments[_key];
      }

      _this = _super.call.apply(_super, [this].concat(args));

      _initialize(_assertThisInitialized(_this));

      return _this;
    }

    return HassioAddonAudio;
  }(_LitElement);

  return {
    F: HassioAddonAudio,
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
      key: "addon",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "_error",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "_inputDevices",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "_outputDevices",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "_selectedInput",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "_selectedOutput",
      value: void 0
    }, {
      kind: "method",
      key: "render",
      value: function render() {
        return Object(lit_element["e" /* html */])(_templateObject(), this._error ? Object(lit_element["e" /* html */])(_templateObject2(), this._error) : "", this._setInputDevice, this._selectedInput, this._inputDevices && this._inputDevices.map(function (item) {
          return Object(lit_element["e" /* html */])(_templateObject3(), item.device || "", item.name);
        }), this._setOutputDevice, this._selectedOutput, this._outputDevices && this._outputDevices.map(function (item) {
          return Object(lit_element["e" /* html */])(_templateObject4(), item.device || "", item.name);
        }), this._saveSettings);
      }
    }, {
      kind: "get",
      "static": true,
      key: "styles",
      value: function styles() {
        return [resources_styles["b" /* haStyle */], hassio_style["a" /* hassioStyle */], Object(lit_element["c" /* css */])(_templateObject5())];
      }
    }, {
      kind: "method",
      key: "update",
      value: function update(changedProperties) {
        _get(_getPrototypeOf(HassioAddonAudio.prototype), "update", this).call(this, changedProperties);

        if (changedProperties.has("addon")) {
          this._addonChanged();
        }
      }
    }, {
      kind: "method",
      key: "_setInputDevice",
      value: function _setInputDevice(ev) {
        var device = ev.detail.item.getAttribute("device");
        this._selectedInput = device;
      }
    }, {
      kind: "method",
      key: "_setOutputDevice",
      value: function _setOutputDevice(ev) {
        var device = ev.detail.item.getAttribute("device");
        this._selectedOutput = device;
      }
    }, {
      kind: "method",
      key: "_addonChanged",
      value: function () {
        var _addonChanged2 = hassio_addon_audio_asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee() {
          var noDevice, _yield$fetchHassioHar, audio, input, output;

          return regeneratorRuntime.wrap(function _callee$(_context) {
            while (1) {
              switch (_context.prev = _context.next) {
                case 0:
                  this._selectedInput = this.addon.audio_input === null ? "default" : this.addon.audio_input;
                  this._selectedOutput = this.addon.audio_output === null ? "default" : this.addon.audio_output;

                  if (!this._outputDevices) {
                    _context.next = 4;
                    break;
                  }

                  return _context.abrupt("return");

                case 4:
                  noDevice = {
                    device: "default",
                    name: "Default"
                  };
                  _context.prev = 5;
                  _context.next = 8;
                  return Object(hardware["a" /* fetchHassioHardwareAudio */])(this.hass);

                case 8:
                  _yield$fetchHassioHar = _context.sent;
                  audio = _yield$fetchHassioHar.audio;
                  input = Object.keys(audio.input).map(function (key) {
                    return {
                      device: key,
                      name: audio.input[key]
                    };
                  });
                  output = Object.keys(audio.output).map(function (key) {
                    return {
                      device: key,
                      name: audio.output[key]
                    };
                  });
                  this._inputDevices = [noDevice].concat(_toConsumableArray(input));
                  this._outputDevices = [noDevice].concat(_toConsumableArray(output));
                  _context.next = 21;
                  break;

                case 16:
                  _context.prev = 16;
                  _context.t0 = _context["catch"](5);
                  this._error = "Failed to fetch audio hardware";
                  this._inputDevices = [noDevice];
                  this._outputDevices = [noDevice];

                case 21:
                case "end":
                  return _context.stop();
              }
            }
          }, _callee, this, [[5, 16]]);
        }));

        function _addonChanged() {
          return _addonChanged2.apply(this, arguments);
        }

        return _addonChanged;
      }()
    }, {
      kind: "method",
      key: "_saveSettings",
      value: function () {
        var _saveSettings2 = hassio_addon_audio_asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee2() {
          var _this$addon;

          var data;
          return regeneratorRuntime.wrap(function _callee2$(_context2) {
            while (1) {
              switch (_context2.prev = _context2.next) {
                case 0:
                  this._error = undefined;
                  data = {
                    audio_input: this._selectedInput === "default" ? null : this._selectedInput,
                    audio_output: this._selectedOutput === "default" ? null : this._selectedOutput
                  };
                  _context2.prev = 2;
                  _context2.next = 5;
                  return Object(hassio_addon["i" /* setHassioAddonOption */])(this.hass, this.addon.slug, data);

                case 5:
                  _context2.next = 10;
                  break;

                case 7:
                  _context2.prev = 7;
                  _context2.t0 = _context2["catch"](2);
                  this._error = "Failed to set addon audio device";

                case 10:
                  if (!(!this._error && ((_this$addon = this.addon) === null || _this$addon === void 0 ? void 0 : _this$addon.state) === "started")) {
                    _context2.next = 13;
                    break;
                  }

                  _context2.next = 13;
                  return suggestAddonRestart(this, this.hass, this.addon);

                case 13:
                case "end":
                  return _context2.stop();
              }
            }
          }, _callee2, this, [[2, 7]]);
        }));

        function _saveSettings() {
          return _saveSettings2.apply(this, arguments);
        }

        return _saveSettings;
      }()
    }]
  };
}, lit_element["a" /* LitElement */]);
// EXTERNAL MODULE: ./node_modules/@polymer/iron-autogrow-textarea/iron-autogrow-textarea.js
var iron_autogrow_textarea = __webpack_require__(151);

// EXTERNAL MODULE: ./src/common/dom/fire_event.ts
var fire_event = __webpack_require__(12);

// EXTERNAL MODULE: ./node_modules/js-yaml/index.js
var js_yaml = __webpack_require__(152);

// CONCATENATED MODULE: ./src/common/util/render-status.ts
var afterNextRender = function afterNextRender(cb) {
  requestAnimationFrame(function () {
    return setTimeout(cb, 0);
  });
};
var nextRender = function nextRender() {
  return new Promise(function (resolve) {
    afterNextRender(resolve);
  });
};
// CONCATENATED MODULE: ./src/resources/codemirror.ondemand.ts
function codemirror_ondemand_asyncGeneratorStep(gen, resolve, reject, _next, _throw, key, arg) { try { var info = gen[key](arg); var value = info.value; } catch (error) { reject(error); return; } if (info.done) { resolve(value); } else { Promise.resolve(value).then(_next, _throw); } }

function codemirror_ondemand_asyncToGenerator(fn) { return function () { var self = this, args = arguments; return new Promise(function (resolve, reject) { var gen = fn.apply(self, args); function _next(value) { codemirror_ondemand_asyncGeneratorStep(gen, resolve, reject, _next, _throw, "next", value); } function _throw(err) { codemirror_ondemand_asyncGeneratorStep(gen, resolve, reject, _next, _throw, "throw", err); } _next(undefined); }); }; }

var codemirror_ondemand_loaded;
var loadCodeMirror = /*#__PURE__*/function () {
  var _ref = codemirror_ondemand_asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee() {
    return regeneratorRuntime.wrap(function _callee$(_context) {
      while (1) {
        switch (_context.prev = _context.next) {
          case 0:
            if (!codemirror_ondemand_loaded) {
              codemirror_ondemand_loaded = Promise.all(/* import() | codemirror */[__webpack_require__.e(10), __webpack_require__.e(1)]).then(__webpack_require__.bind(null, 191));
            }

            return _context.abrupt("return", codemirror_ondemand_loaded);

          case 2:
          case "end":
            return _context.stop();
        }
      }
    }, _callee);
  }));

  return function loadCodeMirror() {
    return _ref.apply(this, arguments);
  };
}();
// CONCATENATED MODULE: ./src/components/ha-code-editor.ts
function ha_code_editor_typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { ha_code_editor_typeof = function _typeof(obj) { return typeof obj; }; } else { ha_code_editor_typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return ha_code_editor_typeof(obj); }

function ha_code_editor_asyncGeneratorStep(gen, resolve, reject, _next, _throw, key, arg) { try { var info = gen[key](arg); var value = info.value; } catch (error) { reject(error); return; } if (info.done) { resolve(value); } else { Promise.resolve(value).then(_next, _throw); } }

function ha_code_editor_asyncToGenerator(fn) { return function () { var self = this, args = arguments; return new Promise(function (resolve, reject) { var gen = fn.apply(self, args); function _next(value) { ha_code_editor_asyncGeneratorStep(gen, resolve, reject, _next, _throw, "next", value); } function _throw(err) { ha_code_editor_asyncGeneratorStep(gen, resolve, reject, _next, _throw, "throw", err); } _next(undefined); }); }; }

function ha_code_editor_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function ha_code_editor_inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) ha_code_editor_setPrototypeOf(subClass, superClass); }

function ha_code_editor_setPrototypeOf(o, p) { ha_code_editor_setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return ha_code_editor_setPrototypeOf(o, p); }

function ha_code_editor_createSuper(Derived) { return function () { var Super = ha_code_editor_getPrototypeOf(Derived), result; if (ha_code_editor_isNativeReflectConstruct()) { var NewTarget = ha_code_editor_getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return ha_code_editor_possibleConstructorReturn(this, result); }; }

function ha_code_editor_possibleConstructorReturn(self, call) { if (call && (ha_code_editor_typeof(call) === "object" || typeof call === "function")) { return call; } return ha_code_editor_assertThisInitialized(self); }

function ha_code_editor_assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function ha_code_editor_isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Date.prototype.toString.call(Reflect.construct(Date, [], function () {})); return true; } catch (e) { return false; } }

function ha_code_editor_decorate(decorators, factory, superClass, mixins) { var api = ha_code_editor_getDecoratorsApi(); if (mixins) { for (var i = 0; i < mixins.length; i++) { api = mixins[i](api); } } var r = factory(function initialize(O) { api.initializeInstanceElements(O, decorated.elements); }, superClass); var decorated = api.decorateClass(ha_code_editor_coalesceClassElements(r.d.map(ha_code_editor_createElementDescriptor)), decorators); api.initializeClassElements(r.F, decorated.elements); return api.runClassFinishers(r.F, decorated.finishers); }

function ha_code_editor_getDecoratorsApi() { ha_code_editor_getDecoratorsApi = function _getDecoratorsApi() { return api; }; var api = { elementsDefinitionOrder: [["method"], ["field"]], initializeInstanceElements: function initializeInstanceElements(O, elements) { ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { if (element.kind === kind && element.placement === "own") { this.defineClassElement(O, element); } }, this); }, this); }, initializeClassElements: function initializeClassElements(F, elements) { var proto = F.prototype; ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { var placement = element.placement; if (element.kind === kind && (placement === "static" || placement === "prototype")) { var receiver = placement === "static" ? F : proto; this.defineClassElement(receiver, element); } }, this); }, this); }, defineClassElement: function defineClassElement(receiver, element) { var descriptor = element.descriptor; if (element.kind === "field") { var initializer = element.initializer; descriptor = { enumerable: descriptor.enumerable, writable: descriptor.writable, configurable: descriptor.configurable, value: initializer === void 0 ? void 0 : initializer.call(receiver) }; } Object.defineProperty(receiver, element.key, descriptor); }, decorateClass: function decorateClass(elements, decorators) { var newElements = []; var finishers = []; var placements = { "static": [], prototype: [], own: [] }; elements.forEach(function (element) { this.addElementPlacement(element, placements); }, this); elements.forEach(function (element) { if (!ha_code_editor_hasDecorators(element)) return newElements.push(element); var elementFinishersExtras = this.decorateElement(element, placements); newElements.push(elementFinishersExtras.element); newElements.push.apply(newElements, elementFinishersExtras.extras); finishers.push.apply(finishers, elementFinishersExtras.finishers); }, this); if (!decorators) { return { elements: newElements, finishers: finishers }; } var result = this.decorateConstructor(newElements, decorators); finishers.push.apply(finishers, result.finishers); result.finishers = finishers; return result; }, addElementPlacement: function addElementPlacement(element, placements, silent) { var keys = placements[element.placement]; if (!silent && keys.indexOf(element.key) !== -1) { throw new TypeError("Duplicated element (" + element.key + ")"); } keys.push(element.key); }, decorateElement: function decorateElement(element, placements) { var extras = []; var finishers = []; for (var decorators = element.decorators, i = decorators.length - 1; i >= 0; i--) { var keys = placements[element.placement]; keys.splice(keys.indexOf(element.key), 1); var elementObject = this.fromElementDescriptor(element); var elementFinisherExtras = this.toElementFinisherExtras((0, decorators[i])(elementObject) || elementObject); element = elementFinisherExtras.element; this.addElementPlacement(element, placements); if (elementFinisherExtras.finisher) { finishers.push(elementFinisherExtras.finisher); } var newExtras = elementFinisherExtras.extras; if (newExtras) { for (var j = 0; j < newExtras.length; j++) { this.addElementPlacement(newExtras[j], placements); } extras.push.apply(extras, newExtras); } } return { element: element, finishers: finishers, extras: extras }; }, decorateConstructor: function decorateConstructor(elements, decorators) { var finishers = []; for (var i = decorators.length - 1; i >= 0; i--) { var obj = this.fromClassDescriptor(elements); var elementsAndFinisher = this.toClassDescriptor((0, decorators[i])(obj) || obj); if (elementsAndFinisher.finisher !== undefined) { finishers.push(elementsAndFinisher.finisher); } if (elementsAndFinisher.elements !== undefined) { elements = elementsAndFinisher.elements; for (var j = 0; j < elements.length - 1; j++) { for (var k = j + 1; k < elements.length; k++) { if (elements[j].key === elements[k].key && elements[j].placement === elements[k].placement) { throw new TypeError("Duplicated element (" + elements[j].key + ")"); } } } } } return { elements: elements, finishers: finishers }; }, fromElementDescriptor: function fromElementDescriptor(element) { var obj = { kind: element.kind, key: element.key, placement: element.placement, descriptor: element.descriptor }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); if (element.kind === "field") obj.initializer = element.initializer; return obj; }, toElementDescriptors: function toElementDescriptors(elementObjects) { if (elementObjects === undefined) return; return ha_code_editor_toArray(elementObjects).map(function (elementObject) { var element = this.toElementDescriptor(elementObject); this.disallowProperty(elementObject, "finisher", "An element descriptor"); this.disallowProperty(elementObject, "extras", "An element descriptor"); return element; }, this); }, toElementDescriptor: function toElementDescriptor(elementObject) { var kind = String(elementObject.kind); if (kind !== "method" && kind !== "field") { throw new TypeError('An element descriptor\'s .kind property must be either "method" or' + ' "field", but a decorator created an element descriptor with' + ' .kind "' + kind + '"'); } var key = ha_code_editor_toPropertyKey(elementObject.key); var placement = String(elementObject.placement); if (placement !== "static" && placement !== "prototype" && placement !== "own") { throw new TypeError('An element descriptor\'s .placement property must be one of "static",' + ' "prototype" or "own", but a decorator created an element descriptor' + ' with .placement "' + placement + '"'); } var descriptor = elementObject.descriptor; this.disallowProperty(elementObject, "elements", "An element descriptor"); var element = { kind: kind, key: key, placement: placement, descriptor: Object.assign({}, descriptor) }; if (kind !== "field") { this.disallowProperty(elementObject, "initializer", "A method descriptor"); } else { this.disallowProperty(descriptor, "get", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "set", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "value", "The property descriptor of a field descriptor"); element.initializer = elementObject.initializer; } return element; }, toElementFinisherExtras: function toElementFinisherExtras(elementObject) { var element = this.toElementDescriptor(elementObject); var finisher = ha_code_editor_optionalCallableProperty(elementObject, "finisher"); var extras = this.toElementDescriptors(elementObject.extras); return { element: element, finisher: finisher, extras: extras }; }, fromClassDescriptor: function fromClassDescriptor(elements) { var obj = { kind: "class", elements: elements.map(this.fromElementDescriptor, this) }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); return obj; }, toClassDescriptor: function toClassDescriptor(obj) { var kind = String(obj.kind); if (kind !== "class") { throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator' + ' created a class descriptor with .kind "' + kind + '"'); } this.disallowProperty(obj, "key", "A class descriptor"); this.disallowProperty(obj, "placement", "A class descriptor"); this.disallowProperty(obj, "descriptor", "A class descriptor"); this.disallowProperty(obj, "initializer", "A class descriptor"); this.disallowProperty(obj, "extras", "A class descriptor"); var finisher = ha_code_editor_optionalCallableProperty(obj, "finisher"); var elements = this.toElementDescriptors(obj.elements); return { elements: elements, finisher: finisher }; }, runClassFinishers: function runClassFinishers(constructor, finishers) { for (var i = 0; i < finishers.length; i++) { var newConstructor = (0, finishers[i])(constructor); if (newConstructor !== undefined) { if (typeof newConstructor !== "function") { throw new TypeError("Finishers must return a constructor."); } constructor = newConstructor; } } return constructor; }, disallowProperty: function disallowProperty(obj, name, objectType) { if (obj[name] !== undefined) { throw new TypeError(objectType + " can't have a ." + name + " property."); } } }; return api; }

function ha_code_editor_createElementDescriptor(def) { var key = ha_code_editor_toPropertyKey(def.key); var descriptor; if (def.kind === "method") { descriptor = { value: def.value, writable: true, configurable: true, enumerable: false }; } else if (def.kind === "get") { descriptor = { get: def.value, configurable: true, enumerable: false }; } else if (def.kind === "set") { descriptor = { set: def.value, configurable: true, enumerable: false }; } else if (def.kind === "field") { descriptor = { configurable: true, writable: true, enumerable: true }; } var element = { kind: def.kind === "field" ? "field" : "method", key: key, placement: def["static"] ? "static" : def.kind === "field" ? "own" : "prototype", descriptor: descriptor }; if (def.decorators) element.decorators = def.decorators; if (def.kind === "field") element.initializer = def.value; return element; }

function ha_code_editor_coalesceGetterSetter(element, other) { if (element.descriptor.get !== undefined) { other.descriptor.get = element.descriptor.get; } else { other.descriptor.set = element.descriptor.set; } }

function ha_code_editor_coalesceClassElements(elements) { var newElements = []; var isSameElement = function isSameElement(other) { return other.kind === "method" && other.key === element.key && other.placement === element.placement; }; for (var i = 0; i < elements.length; i++) { var element = elements[i]; var other; if (element.kind === "method" && (other = newElements.find(isSameElement))) { if (ha_code_editor_isDataDescriptor(element.descriptor) || ha_code_editor_isDataDescriptor(other.descriptor)) { if (ha_code_editor_hasDecorators(element) || ha_code_editor_hasDecorators(other)) { throw new ReferenceError("Duplicated methods (" + element.key + ") can't be decorated."); } other.descriptor = element.descriptor; } else { if (ha_code_editor_hasDecorators(element)) { if (ha_code_editor_hasDecorators(other)) { throw new ReferenceError("Decorators can't be placed on different accessors with for " + "the same property (" + element.key + ")."); } other.decorators = element.decorators; } ha_code_editor_coalesceGetterSetter(element, other); } } else { newElements.push(element); } } return newElements; }

function ha_code_editor_hasDecorators(element) { return element.decorators && element.decorators.length; }

function ha_code_editor_isDataDescriptor(desc) { return desc !== undefined && !(desc.value === undefined && desc.writable === undefined); }

function ha_code_editor_optionalCallableProperty(obj, name) { var value = obj[name]; if (value !== undefined && typeof value !== "function") { throw new TypeError("Expected '" + name + "' to be a function"); } return value; }

function ha_code_editor_toPropertyKey(arg) { var key = ha_code_editor_toPrimitive(arg, "string"); return ha_code_editor_typeof(key) === "symbol" ? key : String(key); }

function ha_code_editor_toPrimitive(input, hint) { if (ha_code_editor_typeof(input) !== "object" || input === null) return input; var prim = input[Symbol.toPrimitive]; if (prim !== undefined) { var res = prim.call(input, hint || "default"); if (ha_code_editor_typeof(res) !== "object") return res; throw new TypeError("@@toPrimitive must return a primitive value."); } return (hint === "string" ? String : Number)(input); }

function ha_code_editor_toArray(arr) { return ha_code_editor_arrayWithHoles(arr) || ha_code_editor_iterableToArray(arr) || ha_code_editor_unsupportedIterableToArray(arr) || ha_code_editor_nonIterableRest(); }

function ha_code_editor_nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function ha_code_editor_unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return ha_code_editor_arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(n); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return ha_code_editor_arrayLikeToArray(o, minLen); }

function ha_code_editor_arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function ha_code_editor_iterableToArray(iter) { if (typeof Symbol !== "undefined" && Symbol.iterator in Object(iter)) return Array.from(iter); }

function ha_code_editor_arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }

function ha_code_editor_get(target, property, receiver) { if (typeof Reflect !== "undefined" && Reflect.get) { ha_code_editor_get = Reflect.get; } else { ha_code_editor_get = function _get(target, property, receiver) { var base = ha_code_editor_superPropBase(target, property); if (!base) return; var desc = Object.getOwnPropertyDescriptor(base, property); if (desc.get) { return desc.get.call(receiver); } return desc.value; }; } return ha_code_editor_get(target, property, receiver || target); }

function ha_code_editor_superPropBase(object, property) { while (!Object.prototype.hasOwnProperty.call(object, property)) { object = ha_code_editor_getPrototypeOf(object); if (object === null) break; } return object; }

function ha_code_editor_getPrototypeOf(o) { ha_code_editor_getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return ha_code_editor_getPrototypeOf(o); }




var ha_code_editor_HaCodeEditor = ha_code_editor_decorate([Object(lit_element["d" /* customElement */])("ha-code-editor")], function (_initialize, _UpdatingElement) {
  var HaCodeEditor = /*#__PURE__*/function (_UpdatingElement2) {
    ha_code_editor_inherits(HaCodeEditor, _UpdatingElement2);

    var _super = ha_code_editor_createSuper(HaCodeEditor);

    function HaCodeEditor() {
      var _this;

      ha_code_editor_classCallCheck(this, HaCodeEditor);

      for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
        args[_key] = arguments[_key];
      }

      _this = _super.call.apply(_super, [this].concat(args));

      _initialize(ha_code_editor_assertThisInitialized(_this));

      return _this;
    }

    return HaCodeEditor;
  }(_UpdatingElement);

  return {
    F: HaCodeEditor,
    d: [{
      kind: "field",
      key: "codemirror",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "mode",
      value: void 0
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
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])({
        type: Boolean
      })],
      key: "readOnly",
      value: function value() {
        return false;
      }
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "rtl",
      value: function value() {
        return false;
      }
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "error",
      value: function value() {
        return false;
      }
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "_value",
      value: function value() {
        return "";
      }
    }, {
      kind: "set",
      key: "value",
      value: function value(_value) {
        this._value = _value;
      }
    }, {
      kind: "get",
      key: "value",
      value: function value() {
        return this.codemirror ? this.codemirror.getValue() : this._value;
      }
    }, {
      kind: "get",
      key: "hasComments",
      value: function hasComments() {
        return !!this.shadowRoot.querySelector("span.cm-comment");
      }
    }, {
      kind: "method",
      key: "connectedCallback",
      value: function connectedCallback() {
        ha_code_editor_get(ha_code_editor_getPrototypeOf(HaCodeEditor.prototype), "connectedCallback", this).call(this);

        if (!this.codemirror) {
          return;
        }

        this.codemirror.refresh();

        if (this.autofocus !== false) {
          this.codemirror.focus();
        }
      }
    }, {
      kind: "method",
      key: "update",
      value: function update(changedProps) {
        ha_code_editor_get(ha_code_editor_getPrototypeOf(HaCodeEditor.prototype), "update", this).call(this, changedProps);

        if (!this.codemirror) {
          return;
        }

        if (changedProps.has("mode")) {
          this.codemirror.setOption("mode", this.mode);
        }

        if (changedProps.has("autofocus")) {
          this.codemirror.setOption("autofocus", this.autofocus !== false);
        }

        if (changedProps.has("_value") && this._value !== this.value) {
          this.codemirror.setValue(this._value);
        }

        if (changedProps.has("rtl")) {
          this.codemirror.setOption("gutters", this._calcGutters());

          this._setScrollBarDirection();
        }

        if (changedProps.has("error")) {
          this.classList.toggle("error-state", this.error);
        }
      }
    }, {
      kind: "method",
      key: "firstUpdated",
      value: function firstUpdated(changedProps) {
        ha_code_editor_get(ha_code_editor_getPrototypeOf(HaCodeEditor.prototype), "firstUpdated", this).call(this, changedProps);

        this._load();
      }
    }, {
      kind: "method",
      key: "_load",
      value: function () {
        var _load2 = ha_code_editor_asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee() {
          var _this2 = this;

          var loaded, codeMirror, shadowRoot;
          return regeneratorRuntime.wrap(function _callee$(_context) {
            while (1) {
              switch (_context.prev = _context.next) {
                case 0:
                  _context.next = 2;
                  return loadCodeMirror();

                case 2:
                  loaded = _context.sent;
                  codeMirror = loaded.codeMirror;
                  shadowRoot = this.attachShadow({
                    mode: "open"
                  });
                  shadowRoot.innerHTML = "\n    <style>\n      ".concat(loaded.codeMirrorCss, "\n      .CodeMirror {\n        height: var(--code-mirror-height, auto);\n        direction: var(--code-mirror-direction, ltr);\n      }\n      .CodeMirror-scroll {\n        max-height: var(--code-mirror-max-height, --code-mirror-height);\n      }\n      .CodeMirror-gutters {\n        border-right: 1px solid var(--paper-input-container-color, var(--secondary-text-color));\n        background-color: var(--paper-dialog-background-color, var(--primary-background-color));\n        transition: 0.2s ease border-right;\n      }\n      :host(.error-state) .CodeMirror-gutters {\n        border-color: var(--error-state-color, red);\n      }\n      .CodeMirror-focused .CodeMirror-gutters {\n        border-right: 2px solid var(--paper-input-container-focus-color, var(--primary-color));\n      }\n      .CodeMirror-linenumber {\n        color: var(--paper-dialog-color, var(--primary-text-color));\n      }\n      .rtl .CodeMirror-vscrollbar {\n        right: auto;\n        left: 0px;\n      }\n      .rtl-gutter {\n        width: 20px;\n      }\n    </style>");
                  this.codemirror = codeMirror(shadowRoot, {
                    value: this._value,
                    lineNumbers: true,
                    tabSize: 2,
                    mode: this.mode,
                    autofocus: this.autofocus !== false,
                    viewportMargin: Infinity,
                    readOnly: this.readOnly,
                    extraKeys: {
                      Tab: "indentMore",
                      "Shift-Tab": "indentLess"
                    },
                    gutters: this._calcGutters()
                  });

                  this._setScrollBarDirection();

                  this.codemirror.on("changes", function () {
                    return _this2._onChange();
                  });

                case 9:
                case "end":
                  return _context.stop();
              }
            }
          }, _callee, this);
        }));

        function _load() {
          return _load2.apply(this, arguments);
        }

        return _load;
      }()
    }, {
      kind: "method",
      key: "_onChange",
      value: function _onChange() {
        var newValue = this.value;

        if (newValue === this._value) {
          return;
        }

        this._value = newValue;
        Object(fire_event["a" /* fireEvent */])(this, "value-changed", {
          value: this._value
        });
      }
    }, {
      kind: "method",
      key: "_calcGutters",
      value: function _calcGutters() {
        return this.rtl ? ["rtl-gutter", "CodeMirror-linenumbers"] : [];
      }
    }, {
      kind: "method",
      key: "_setScrollBarDirection",
      value: function _setScrollBarDirection() {
        if (this.codemirror) {
          this.codemirror.getWrapperElement().classList.toggle("rtl", this.rtl);
        }
      }
    }]
  };
}, lit_element["b" /* UpdatingElement */]);
// CONCATENATED MODULE: ./src/components/ha-yaml-editor.ts
function ha_yaml_editor_templateObject3() {
  var data = ha_yaml_editor_taggedTemplateLiteral([" <p>", "</p> "]);

  ha_yaml_editor_templateObject3 = function _templateObject3() {
    return data;
  };

  return data;
}

function ha_yaml_editor_templateObject2() {
  var data = ha_yaml_editor_taggedTemplateLiteral(["\n      ", "\n      <ha-code-editor\n        .value=", "\n        mode=\"yaml\"\n        .error=", "\n        @value-changed=", "\n      ></ha-code-editor>\n    "]);

  ha_yaml_editor_templateObject2 = function _templateObject2() {
    return data;
  };

  return data;
}

function ha_yaml_editor_templateObject() {
  var data = ha_yaml_editor_taggedTemplateLiteral([""]);

  ha_yaml_editor_templateObject = function _templateObject() {
    return data;
  };

  return data;
}

function ha_yaml_editor_taggedTemplateLiteral(strings, raw) { if (!raw) { raw = strings.slice(0); } return Object.freeze(Object.defineProperties(strings, { raw: { value: Object.freeze(raw) } })); }

function ha_yaml_editor_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function ha_yaml_editor_inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) ha_yaml_editor_setPrototypeOf(subClass, superClass); }

function ha_yaml_editor_setPrototypeOf(o, p) { ha_yaml_editor_setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return ha_yaml_editor_setPrototypeOf(o, p); }

function ha_yaml_editor_createSuper(Derived) { return function () { var Super = ha_yaml_editor_getPrototypeOf(Derived), result; if (ha_yaml_editor_isNativeReflectConstruct()) { var NewTarget = ha_yaml_editor_getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return ha_yaml_editor_possibleConstructorReturn(this, result); }; }

function ha_yaml_editor_possibleConstructorReturn(self, call) { if (call && (ha_yaml_editor_typeof(call) === "object" || typeof call === "function")) { return call; } return ha_yaml_editor_assertThisInitialized(self); }

function ha_yaml_editor_assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function ha_yaml_editor_isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Date.prototype.toString.call(Reflect.construct(Date, [], function () {})); return true; } catch (e) { return false; } }

function ha_yaml_editor_getPrototypeOf(o) { ha_yaml_editor_getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return ha_yaml_editor_getPrototypeOf(o); }

function ha_yaml_editor_decorate(decorators, factory, superClass, mixins) { var api = ha_yaml_editor_getDecoratorsApi(); if (mixins) { for (var i = 0; i < mixins.length; i++) { api = mixins[i](api); } } var r = factory(function initialize(O) { api.initializeInstanceElements(O, decorated.elements); }, superClass); var decorated = api.decorateClass(ha_yaml_editor_coalesceClassElements(r.d.map(ha_yaml_editor_createElementDescriptor)), decorators); api.initializeClassElements(r.F, decorated.elements); return api.runClassFinishers(r.F, decorated.finishers); }

function ha_yaml_editor_getDecoratorsApi() { ha_yaml_editor_getDecoratorsApi = function _getDecoratorsApi() { return api; }; var api = { elementsDefinitionOrder: [["method"], ["field"]], initializeInstanceElements: function initializeInstanceElements(O, elements) { ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { if (element.kind === kind && element.placement === "own") { this.defineClassElement(O, element); } }, this); }, this); }, initializeClassElements: function initializeClassElements(F, elements) { var proto = F.prototype; ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { var placement = element.placement; if (element.kind === kind && (placement === "static" || placement === "prototype")) { var receiver = placement === "static" ? F : proto; this.defineClassElement(receiver, element); } }, this); }, this); }, defineClassElement: function defineClassElement(receiver, element) { var descriptor = element.descriptor; if (element.kind === "field") { var initializer = element.initializer; descriptor = { enumerable: descriptor.enumerable, writable: descriptor.writable, configurable: descriptor.configurable, value: initializer === void 0 ? void 0 : initializer.call(receiver) }; } Object.defineProperty(receiver, element.key, descriptor); }, decorateClass: function decorateClass(elements, decorators) { var newElements = []; var finishers = []; var placements = { "static": [], prototype: [], own: [] }; elements.forEach(function (element) { this.addElementPlacement(element, placements); }, this); elements.forEach(function (element) { if (!ha_yaml_editor_hasDecorators(element)) return newElements.push(element); var elementFinishersExtras = this.decorateElement(element, placements); newElements.push(elementFinishersExtras.element); newElements.push.apply(newElements, elementFinishersExtras.extras); finishers.push.apply(finishers, elementFinishersExtras.finishers); }, this); if (!decorators) { return { elements: newElements, finishers: finishers }; } var result = this.decorateConstructor(newElements, decorators); finishers.push.apply(finishers, result.finishers); result.finishers = finishers; return result; }, addElementPlacement: function addElementPlacement(element, placements, silent) { var keys = placements[element.placement]; if (!silent && keys.indexOf(element.key) !== -1) { throw new TypeError("Duplicated element (" + element.key + ")"); } keys.push(element.key); }, decorateElement: function decorateElement(element, placements) { var extras = []; var finishers = []; for (var decorators = element.decorators, i = decorators.length - 1; i >= 0; i--) { var keys = placements[element.placement]; keys.splice(keys.indexOf(element.key), 1); var elementObject = this.fromElementDescriptor(element); var elementFinisherExtras = this.toElementFinisherExtras((0, decorators[i])(elementObject) || elementObject); element = elementFinisherExtras.element; this.addElementPlacement(element, placements); if (elementFinisherExtras.finisher) { finishers.push(elementFinisherExtras.finisher); } var newExtras = elementFinisherExtras.extras; if (newExtras) { for (var j = 0; j < newExtras.length; j++) { this.addElementPlacement(newExtras[j], placements); } extras.push.apply(extras, newExtras); } } return { element: element, finishers: finishers, extras: extras }; }, decorateConstructor: function decorateConstructor(elements, decorators) { var finishers = []; for (var i = decorators.length - 1; i >= 0; i--) { var obj = this.fromClassDescriptor(elements); var elementsAndFinisher = this.toClassDescriptor((0, decorators[i])(obj) || obj); if (elementsAndFinisher.finisher !== undefined) { finishers.push(elementsAndFinisher.finisher); } if (elementsAndFinisher.elements !== undefined) { elements = elementsAndFinisher.elements; for (var j = 0; j < elements.length - 1; j++) { for (var k = j + 1; k < elements.length; k++) { if (elements[j].key === elements[k].key && elements[j].placement === elements[k].placement) { throw new TypeError("Duplicated element (" + elements[j].key + ")"); } } } } } return { elements: elements, finishers: finishers }; }, fromElementDescriptor: function fromElementDescriptor(element) { var obj = { kind: element.kind, key: element.key, placement: element.placement, descriptor: element.descriptor }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); if (element.kind === "field") obj.initializer = element.initializer; return obj; }, toElementDescriptors: function toElementDescriptors(elementObjects) { if (elementObjects === undefined) return; return ha_yaml_editor_toArray(elementObjects).map(function (elementObject) { var element = this.toElementDescriptor(elementObject); this.disallowProperty(elementObject, "finisher", "An element descriptor"); this.disallowProperty(elementObject, "extras", "An element descriptor"); return element; }, this); }, toElementDescriptor: function toElementDescriptor(elementObject) { var kind = String(elementObject.kind); if (kind !== "method" && kind !== "field") { throw new TypeError('An element descriptor\'s .kind property must be either "method" or' + ' "field", but a decorator created an element descriptor with' + ' .kind "' + kind + '"'); } var key = ha_yaml_editor_toPropertyKey(elementObject.key); var placement = String(elementObject.placement); if (placement !== "static" && placement !== "prototype" && placement !== "own") { throw new TypeError('An element descriptor\'s .placement property must be one of "static",' + ' "prototype" or "own", but a decorator created an element descriptor' + ' with .placement "' + placement + '"'); } var descriptor = elementObject.descriptor; this.disallowProperty(elementObject, "elements", "An element descriptor"); var element = { kind: kind, key: key, placement: placement, descriptor: Object.assign({}, descriptor) }; if (kind !== "field") { this.disallowProperty(elementObject, "initializer", "A method descriptor"); } else { this.disallowProperty(descriptor, "get", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "set", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "value", "The property descriptor of a field descriptor"); element.initializer = elementObject.initializer; } return element; }, toElementFinisherExtras: function toElementFinisherExtras(elementObject) { var element = this.toElementDescriptor(elementObject); var finisher = ha_yaml_editor_optionalCallableProperty(elementObject, "finisher"); var extras = this.toElementDescriptors(elementObject.extras); return { element: element, finisher: finisher, extras: extras }; }, fromClassDescriptor: function fromClassDescriptor(elements) { var obj = { kind: "class", elements: elements.map(this.fromElementDescriptor, this) }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); return obj; }, toClassDescriptor: function toClassDescriptor(obj) { var kind = String(obj.kind); if (kind !== "class") { throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator' + ' created a class descriptor with .kind "' + kind + '"'); } this.disallowProperty(obj, "key", "A class descriptor"); this.disallowProperty(obj, "placement", "A class descriptor"); this.disallowProperty(obj, "descriptor", "A class descriptor"); this.disallowProperty(obj, "initializer", "A class descriptor"); this.disallowProperty(obj, "extras", "A class descriptor"); var finisher = ha_yaml_editor_optionalCallableProperty(obj, "finisher"); var elements = this.toElementDescriptors(obj.elements); return { elements: elements, finisher: finisher }; }, runClassFinishers: function runClassFinishers(constructor, finishers) { for (var i = 0; i < finishers.length; i++) { var newConstructor = (0, finishers[i])(constructor); if (newConstructor !== undefined) { if (typeof newConstructor !== "function") { throw new TypeError("Finishers must return a constructor."); } constructor = newConstructor; } } return constructor; }, disallowProperty: function disallowProperty(obj, name, objectType) { if (obj[name] !== undefined) { throw new TypeError(objectType + " can't have a ." + name + " property."); } } }; return api; }

function ha_yaml_editor_createElementDescriptor(def) { var key = ha_yaml_editor_toPropertyKey(def.key); var descriptor; if (def.kind === "method") { descriptor = { value: def.value, writable: true, configurable: true, enumerable: false }; } else if (def.kind === "get") { descriptor = { get: def.value, configurable: true, enumerable: false }; } else if (def.kind === "set") { descriptor = { set: def.value, configurable: true, enumerable: false }; } else if (def.kind === "field") { descriptor = { configurable: true, writable: true, enumerable: true }; } var element = { kind: def.kind === "field" ? "field" : "method", key: key, placement: def["static"] ? "static" : def.kind === "field" ? "own" : "prototype", descriptor: descriptor }; if (def.decorators) element.decorators = def.decorators; if (def.kind === "field") element.initializer = def.value; return element; }

function ha_yaml_editor_coalesceGetterSetter(element, other) { if (element.descriptor.get !== undefined) { other.descriptor.get = element.descriptor.get; } else { other.descriptor.set = element.descriptor.set; } }

function ha_yaml_editor_coalesceClassElements(elements) { var newElements = []; var isSameElement = function isSameElement(other) { return other.kind === "method" && other.key === element.key && other.placement === element.placement; }; for (var i = 0; i < elements.length; i++) { var element = elements[i]; var other; if (element.kind === "method" && (other = newElements.find(isSameElement))) { if (ha_yaml_editor_isDataDescriptor(element.descriptor) || ha_yaml_editor_isDataDescriptor(other.descriptor)) { if (ha_yaml_editor_hasDecorators(element) || ha_yaml_editor_hasDecorators(other)) { throw new ReferenceError("Duplicated methods (" + element.key + ") can't be decorated."); } other.descriptor = element.descriptor; } else { if (ha_yaml_editor_hasDecorators(element)) { if (ha_yaml_editor_hasDecorators(other)) { throw new ReferenceError("Decorators can't be placed on different accessors with for " + "the same property (" + element.key + ")."); } other.decorators = element.decorators; } ha_yaml_editor_coalesceGetterSetter(element, other); } } else { newElements.push(element); } } return newElements; }

function ha_yaml_editor_hasDecorators(element) { return element.decorators && element.decorators.length; }

function ha_yaml_editor_isDataDescriptor(desc) { return desc !== undefined && !(desc.value === undefined && desc.writable === undefined); }

function ha_yaml_editor_optionalCallableProperty(obj, name) { var value = obj[name]; if (value !== undefined && typeof value !== "function") { throw new TypeError("Expected '" + name + "' to be a function"); } return value; }

function ha_yaml_editor_toPropertyKey(arg) { var key = ha_yaml_editor_toPrimitive(arg, "string"); return ha_yaml_editor_typeof(key) === "symbol" ? key : String(key); }

function ha_yaml_editor_toPrimitive(input, hint) { if (ha_yaml_editor_typeof(input) !== "object" || input === null) return input; var prim = input[Symbol.toPrimitive]; if (prim !== undefined) { var res = prim.call(input, hint || "default"); if (ha_yaml_editor_typeof(res) !== "object") return res; throw new TypeError("@@toPrimitive must return a primitive value."); } return (hint === "string" ? String : Number)(input); }

function ha_yaml_editor_toArray(arr) { return ha_yaml_editor_arrayWithHoles(arr) || ha_yaml_editor_iterableToArray(arr) || ha_yaml_editor_unsupportedIterableToArray(arr) || ha_yaml_editor_nonIterableRest(); }

function ha_yaml_editor_nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function ha_yaml_editor_unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return ha_yaml_editor_arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(n); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return ha_yaml_editor_arrayLikeToArray(o, minLen); }

function ha_yaml_editor_arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function ha_yaml_editor_iterableToArray(iter) { if (typeof Symbol !== "undefined" && Symbol.iterator in Object(iter)) return Array.from(iter); }

function ha_yaml_editor_arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }

function ha_yaml_editor_typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { ha_yaml_editor_typeof = function _typeof(obj) { return typeof obj; }; } else { ha_yaml_editor_typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return ha_yaml_editor_typeof(obj); }







var isEmpty = function isEmpty(obj) {
  if (ha_yaml_editor_typeof(obj) !== "object") {
    return false;
  }

  for (var key in obj) {
    if (Object.prototype.hasOwnProperty.call(obj, key)) {
      return false;
    }
  }

  return true;
};

var ha_yaml_editor_HaYamlEditor = ha_yaml_editor_decorate([Object(lit_element["d" /* customElement */])("ha-yaml-editor")], function (_initialize, _LitElement) {
  var HaYamlEditor = /*#__PURE__*/function (_LitElement2) {
    ha_yaml_editor_inherits(HaYamlEditor, _LitElement2);

    var _super = ha_yaml_editor_createSuper(HaYamlEditor);

    function HaYamlEditor() {
      var _this;

      ha_yaml_editor_classCallCheck(this, HaYamlEditor);

      for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
        args[_key] = arguments[_key];
      }

      _this = _super.call.apply(_super, [this].concat(args));

      _initialize(ha_yaml_editor_assertThisInitialized(_this));

      return _this;
    }

    return HaYamlEditor;
  }(_LitElement);

  return {
    F: HaYamlEditor,
    d: [{
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "value",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "defaultValue",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "isValid",
      value: function value() {
        return true;
      }
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "label",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "_yaml",
      value: function value() {
        return "";
      }
    }, {
      kind: "field",
      decorators: [Object(lit_element["g" /* query */])("ha-code-editor")],
      key: "_editor",
      value: void 0
    }, {
      kind: "method",
      key: "setValue",
      value: function setValue(value) {
        var _this2 = this;

        try {
          this._yaml = value && !isEmpty(value) ? Object(js_yaml["safeDump"])(value) : "";
        } catch (err) {
          alert("There was an error converting to YAML: ".concat(err));
        }

        afterNextRender(function () {
          var _this2$_editor;

          if ((_this2$_editor = _this2._editor) === null || _this2$_editor === void 0 ? void 0 : _this2$_editor.codemirror) {
            _this2._editor.codemirror.refresh();
          }

          afterNextRender(function () {
            return Object(fire_event["a" /* fireEvent */])(_this2, "editor-refreshed");
          });
        });
      }
    }, {
      kind: "method",
      key: "firstUpdated",
      value: function firstUpdated() {
        if (this.defaultValue) {
          this.setValue(this.defaultValue);
        }
      }
    }, {
      kind: "method",
      key: "render",
      value: function render() {
        if (this._yaml === undefined) {
          return Object(lit_element["e" /* html */])(ha_yaml_editor_templateObject());
        }

        return Object(lit_element["e" /* html */])(ha_yaml_editor_templateObject2(), this.label ? Object(lit_element["e" /* html */])(ha_yaml_editor_templateObject3(), this.label) : "", this._yaml, this.isValid === false, this._onChange);
      }
    }, {
      kind: "method",
      key: "_onChange",
      value: function _onChange(ev) {
        ev.stopPropagation();
        var value = ev.detail.value;
        var parsed;
        var isValid = true;

        if (value) {
          try {
            parsed = Object(js_yaml["safeLoad"])(value);
          } catch (err) {
            // Invalid YAML
            isValid = false;
          }
        } else {
          parsed = {};
        }

        this.value = parsed;
        this.isValid = isValid;
        Object(fire_event["a" /* fireEvent */])(this, "value-changed", {
          value: parsed,
          isValid: isValid
        });
      }
    }]
  };
}, lit_element["a" /* LitElement */]);
// CONCATENATED MODULE: ./hassio/src/addon-view/config/hassio-addon-config.ts
function hassio_addon_config_typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { hassio_addon_config_typeof = function _typeof(obj) { return typeof obj; }; } else { hassio_addon_config_typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return hassio_addon_config_typeof(obj); }

function hassio_addon_config_asyncGeneratorStep(gen, resolve, reject, _next, _throw, key, arg) { try { var info = gen[key](arg); var value = info.value; } catch (error) { reject(error); return; } if (info.done) { resolve(value); } else { Promise.resolve(value).then(_next, _throw); } }

function hassio_addon_config_asyncToGenerator(fn) { return function () { var self = this, args = arguments; return new Promise(function (resolve, reject) { var gen = fn.apply(self, args); function _next(value) { hassio_addon_config_asyncGeneratorStep(gen, resolve, reject, _next, _throw, "next", value); } function _throw(err) { hassio_addon_config_asyncGeneratorStep(gen, resolve, reject, _next, _throw, "throw", err); } _next(undefined); }); }; }

function hassio_addon_config_templateObject4() {
  var data = hassio_addon_config_taggedTemplateLiteral(["\n        :host {\n          display: block;\n        }\n        paper-card {\n          display: block;\n        }\n        .card-actions {\n          display: flex;\n          justify-content: space-between;\n        }\n        .errors {\n          color: var(--google-red-500);\n          margin-top: 16px;\n        }\n        iron-autogrow-textarea {\n          width: 100%;\n          font-family: monospace;\n        }\n        .syntaxerror {\n          color: var(--google-red-500);\n        }\n      "]);

  hassio_addon_config_templateObject4 = function _templateObject4() {
    return data;
  };

  return data;
}

function hassio_addon_config_templateObject3() {
  var data = hassio_addon_config_taggedTemplateLiteral([" <div class=\"errors\">Invalid YAML</div> "]);

  hassio_addon_config_templateObject3 = function _templateObject3() {
    return data;
  };

  return data;
}

function hassio_addon_config_templateObject2() {
  var data = hassio_addon_config_taggedTemplateLiteral([" <div class=\"errors\">", "</div> "]);

  hassio_addon_config_templateObject2 = function _templateObject2() {
    return data;
  };

  return data;
}

function hassio_addon_config_templateObject() {
  var data = hassio_addon_config_taggedTemplateLiteral(["\n      <h1>", "</h1>\n      <paper-card heading=\"Configuration\">\n        <div class=\"card-content\">\n          <ha-yaml-editor\n            @value-changed=", "\n          ></ha-yaml-editor>\n          ", "\n          ", "\n        </div>\n        <div class=\"card-actions\">\n          <mwc-button class=\"warning\" @click=", ">\n            Reset to defaults\n          </mwc-button>\n          <mwc-button\n            @click=", "\n            .disabled=", "\n          >\n            Save\n          </mwc-button>\n        </div>\n      </paper-card>\n    "]);

  hassio_addon_config_templateObject = function _templateObject() {
    return data;
  };

  return data;
}

function hassio_addon_config_taggedTemplateLiteral(strings, raw) { if (!raw) { raw = strings.slice(0); } return Object.freeze(Object.defineProperties(strings, { raw: { value: Object.freeze(raw) } })); }

function hassio_addon_config_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function hassio_addon_config_inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) hassio_addon_config_setPrototypeOf(subClass, superClass); }

function hassio_addon_config_setPrototypeOf(o, p) { hassio_addon_config_setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return hassio_addon_config_setPrototypeOf(o, p); }

function hassio_addon_config_createSuper(Derived) { return function () { var Super = hassio_addon_config_getPrototypeOf(Derived), result; if (hassio_addon_config_isNativeReflectConstruct()) { var NewTarget = hassio_addon_config_getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return hassio_addon_config_possibleConstructorReturn(this, result); }; }

function hassio_addon_config_possibleConstructorReturn(self, call) { if (call && (hassio_addon_config_typeof(call) === "object" || typeof call === "function")) { return call; } return hassio_addon_config_assertThisInitialized(self); }

function hassio_addon_config_assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function hassio_addon_config_isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Date.prototype.toString.call(Reflect.construct(Date, [], function () {})); return true; } catch (e) { return false; } }

function hassio_addon_config_decorate(decorators, factory, superClass, mixins) { var api = hassio_addon_config_getDecoratorsApi(); if (mixins) { for (var i = 0; i < mixins.length; i++) { api = mixins[i](api); } } var r = factory(function initialize(O) { api.initializeInstanceElements(O, decorated.elements); }, superClass); var decorated = api.decorateClass(hassio_addon_config_coalesceClassElements(r.d.map(hassio_addon_config_createElementDescriptor)), decorators); api.initializeClassElements(r.F, decorated.elements); return api.runClassFinishers(r.F, decorated.finishers); }

function hassio_addon_config_getDecoratorsApi() { hassio_addon_config_getDecoratorsApi = function _getDecoratorsApi() { return api; }; var api = { elementsDefinitionOrder: [["method"], ["field"]], initializeInstanceElements: function initializeInstanceElements(O, elements) { ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { if (element.kind === kind && element.placement === "own") { this.defineClassElement(O, element); } }, this); }, this); }, initializeClassElements: function initializeClassElements(F, elements) { var proto = F.prototype; ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { var placement = element.placement; if (element.kind === kind && (placement === "static" || placement === "prototype")) { var receiver = placement === "static" ? F : proto; this.defineClassElement(receiver, element); } }, this); }, this); }, defineClassElement: function defineClassElement(receiver, element) { var descriptor = element.descriptor; if (element.kind === "field") { var initializer = element.initializer; descriptor = { enumerable: descriptor.enumerable, writable: descriptor.writable, configurable: descriptor.configurable, value: initializer === void 0 ? void 0 : initializer.call(receiver) }; } Object.defineProperty(receiver, element.key, descriptor); }, decorateClass: function decorateClass(elements, decorators) { var newElements = []; var finishers = []; var placements = { "static": [], prototype: [], own: [] }; elements.forEach(function (element) { this.addElementPlacement(element, placements); }, this); elements.forEach(function (element) { if (!hassio_addon_config_hasDecorators(element)) return newElements.push(element); var elementFinishersExtras = this.decorateElement(element, placements); newElements.push(elementFinishersExtras.element); newElements.push.apply(newElements, elementFinishersExtras.extras); finishers.push.apply(finishers, elementFinishersExtras.finishers); }, this); if (!decorators) { return { elements: newElements, finishers: finishers }; } var result = this.decorateConstructor(newElements, decorators); finishers.push.apply(finishers, result.finishers); result.finishers = finishers; return result; }, addElementPlacement: function addElementPlacement(element, placements, silent) { var keys = placements[element.placement]; if (!silent && keys.indexOf(element.key) !== -1) { throw new TypeError("Duplicated element (" + element.key + ")"); } keys.push(element.key); }, decorateElement: function decorateElement(element, placements) { var extras = []; var finishers = []; for (var decorators = element.decorators, i = decorators.length - 1; i >= 0; i--) { var keys = placements[element.placement]; keys.splice(keys.indexOf(element.key), 1); var elementObject = this.fromElementDescriptor(element); var elementFinisherExtras = this.toElementFinisherExtras((0, decorators[i])(elementObject) || elementObject); element = elementFinisherExtras.element; this.addElementPlacement(element, placements); if (elementFinisherExtras.finisher) { finishers.push(elementFinisherExtras.finisher); } var newExtras = elementFinisherExtras.extras; if (newExtras) { for (var j = 0; j < newExtras.length; j++) { this.addElementPlacement(newExtras[j], placements); } extras.push.apply(extras, newExtras); } } return { element: element, finishers: finishers, extras: extras }; }, decorateConstructor: function decorateConstructor(elements, decorators) { var finishers = []; for (var i = decorators.length - 1; i >= 0; i--) { var obj = this.fromClassDescriptor(elements); var elementsAndFinisher = this.toClassDescriptor((0, decorators[i])(obj) || obj); if (elementsAndFinisher.finisher !== undefined) { finishers.push(elementsAndFinisher.finisher); } if (elementsAndFinisher.elements !== undefined) { elements = elementsAndFinisher.elements; for (var j = 0; j < elements.length - 1; j++) { for (var k = j + 1; k < elements.length; k++) { if (elements[j].key === elements[k].key && elements[j].placement === elements[k].placement) { throw new TypeError("Duplicated element (" + elements[j].key + ")"); } } } } } return { elements: elements, finishers: finishers }; }, fromElementDescriptor: function fromElementDescriptor(element) { var obj = { kind: element.kind, key: element.key, placement: element.placement, descriptor: element.descriptor }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); if (element.kind === "field") obj.initializer = element.initializer; return obj; }, toElementDescriptors: function toElementDescriptors(elementObjects) { if (elementObjects === undefined) return; return hassio_addon_config_toArray(elementObjects).map(function (elementObject) { var element = this.toElementDescriptor(elementObject); this.disallowProperty(elementObject, "finisher", "An element descriptor"); this.disallowProperty(elementObject, "extras", "An element descriptor"); return element; }, this); }, toElementDescriptor: function toElementDescriptor(elementObject) { var kind = String(elementObject.kind); if (kind !== "method" && kind !== "field") { throw new TypeError('An element descriptor\'s .kind property must be either "method" or' + ' "field", but a decorator created an element descriptor with' + ' .kind "' + kind + '"'); } var key = hassio_addon_config_toPropertyKey(elementObject.key); var placement = String(elementObject.placement); if (placement !== "static" && placement !== "prototype" && placement !== "own") { throw new TypeError('An element descriptor\'s .placement property must be one of "static",' + ' "prototype" or "own", but a decorator created an element descriptor' + ' with .placement "' + placement + '"'); } var descriptor = elementObject.descriptor; this.disallowProperty(elementObject, "elements", "An element descriptor"); var element = { kind: kind, key: key, placement: placement, descriptor: Object.assign({}, descriptor) }; if (kind !== "field") { this.disallowProperty(elementObject, "initializer", "A method descriptor"); } else { this.disallowProperty(descriptor, "get", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "set", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "value", "The property descriptor of a field descriptor"); element.initializer = elementObject.initializer; } return element; }, toElementFinisherExtras: function toElementFinisherExtras(elementObject) { var element = this.toElementDescriptor(elementObject); var finisher = hassio_addon_config_optionalCallableProperty(elementObject, "finisher"); var extras = this.toElementDescriptors(elementObject.extras); return { element: element, finisher: finisher, extras: extras }; }, fromClassDescriptor: function fromClassDescriptor(elements) { var obj = { kind: "class", elements: elements.map(this.fromElementDescriptor, this) }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); return obj; }, toClassDescriptor: function toClassDescriptor(obj) { var kind = String(obj.kind); if (kind !== "class") { throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator' + ' created a class descriptor with .kind "' + kind + '"'); } this.disallowProperty(obj, "key", "A class descriptor"); this.disallowProperty(obj, "placement", "A class descriptor"); this.disallowProperty(obj, "descriptor", "A class descriptor"); this.disallowProperty(obj, "initializer", "A class descriptor"); this.disallowProperty(obj, "extras", "A class descriptor"); var finisher = hassio_addon_config_optionalCallableProperty(obj, "finisher"); var elements = this.toElementDescriptors(obj.elements); return { elements: elements, finisher: finisher }; }, runClassFinishers: function runClassFinishers(constructor, finishers) { for (var i = 0; i < finishers.length; i++) { var newConstructor = (0, finishers[i])(constructor); if (newConstructor !== undefined) { if (typeof newConstructor !== "function") { throw new TypeError("Finishers must return a constructor."); } constructor = newConstructor; } } return constructor; }, disallowProperty: function disallowProperty(obj, name, objectType) { if (obj[name] !== undefined) { throw new TypeError(objectType + " can't have a ." + name + " property."); } } }; return api; }

function hassio_addon_config_createElementDescriptor(def) { var key = hassio_addon_config_toPropertyKey(def.key); var descriptor; if (def.kind === "method") { descriptor = { value: def.value, writable: true, configurable: true, enumerable: false }; } else if (def.kind === "get") { descriptor = { get: def.value, configurable: true, enumerable: false }; } else if (def.kind === "set") { descriptor = { set: def.value, configurable: true, enumerable: false }; } else if (def.kind === "field") { descriptor = { configurable: true, writable: true, enumerable: true }; } var element = { kind: def.kind === "field" ? "field" : "method", key: key, placement: def["static"] ? "static" : def.kind === "field" ? "own" : "prototype", descriptor: descriptor }; if (def.decorators) element.decorators = def.decorators; if (def.kind === "field") element.initializer = def.value; return element; }

function hassio_addon_config_coalesceGetterSetter(element, other) { if (element.descriptor.get !== undefined) { other.descriptor.get = element.descriptor.get; } else { other.descriptor.set = element.descriptor.set; } }

function hassio_addon_config_coalesceClassElements(elements) { var newElements = []; var isSameElement = function isSameElement(other) { return other.kind === "method" && other.key === element.key && other.placement === element.placement; }; for (var i = 0; i < elements.length; i++) { var element = elements[i]; var other; if (element.kind === "method" && (other = newElements.find(isSameElement))) { if (hassio_addon_config_isDataDescriptor(element.descriptor) || hassio_addon_config_isDataDescriptor(other.descriptor)) { if (hassio_addon_config_hasDecorators(element) || hassio_addon_config_hasDecorators(other)) { throw new ReferenceError("Duplicated methods (" + element.key + ") can't be decorated."); } other.descriptor = element.descriptor; } else { if (hassio_addon_config_hasDecorators(element)) { if (hassio_addon_config_hasDecorators(other)) { throw new ReferenceError("Decorators can't be placed on different accessors with for " + "the same property (" + element.key + ")."); } other.decorators = element.decorators; } hassio_addon_config_coalesceGetterSetter(element, other); } } else { newElements.push(element); } } return newElements; }

function hassio_addon_config_hasDecorators(element) { return element.decorators && element.decorators.length; }

function hassio_addon_config_isDataDescriptor(desc) { return desc !== undefined && !(desc.value === undefined && desc.writable === undefined); }

function hassio_addon_config_optionalCallableProperty(obj, name) { var value = obj[name]; if (value !== undefined && typeof value !== "function") { throw new TypeError("Expected '" + name + "' to be a function"); } return value; }

function hassio_addon_config_toPropertyKey(arg) { var key = hassio_addon_config_toPrimitive(arg, "string"); return hassio_addon_config_typeof(key) === "symbol" ? key : String(key); }

function hassio_addon_config_toPrimitive(input, hint) { if (hassio_addon_config_typeof(input) !== "object" || input === null) return input; var prim = input[Symbol.toPrimitive]; if (prim !== undefined) { var res = prim.call(input, hint || "default"); if (hassio_addon_config_typeof(res) !== "object") return res; throw new TypeError("@@toPrimitive must return a primitive value."); } return (hint === "string" ? String : Number)(input); }

function hassio_addon_config_toArray(arr) { return hassio_addon_config_arrayWithHoles(arr) || hassio_addon_config_iterableToArray(arr) || hassio_addon_config_unsupportedIterableToArray(arr) || hassio_addon_config_nonIterableRest(); }

function hassio_addon_config_nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function hassio_addon_config_unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return hassio_addon_config_arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(n); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return hassio_addon_config_arrayLikeToArray(o, minLen); }

function hassio_addon_config_arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function hassio_addon_config_iterableToArray(iter) { if (typeof Symbol !== "undefined" && Symbol.iterator in Object(iter)) return Array.from(iter); }

function hassio_addon_config_arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }

function hassio_addon_config_get(target, property, receiver) { if (typeof Reflect !== "undefined" && Reflect.get) { hassio_addon_config_get = Reflect.get; } else { hassio_addon_config_get = function _get(target, property, receiver) { var base = hassio_addon_config_superPropBase(target, property); if (!base) return; var desc = Object.getOwnPropertyDescriptor(base, property); if (desc.get) { return desc.get.call(receiver); } return desc.value; }; } return hassio_addon_config_get(target, property, receiver || target); }

function hassio_addon_config_superPropBase(object, property) { while (!Object.prototype.hasOwnProperty.call(object, property)) { object = hassio_addon_config_getPrototypeOf(object); if (object === null) break; } return object; }

function hassio_addon_config_getPrototypeOf(o) { hassio_addon_config_getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return hassio_addon_config_getPrototypeOf(o); }













var hassio_addon_config_HassioAddonConfig = hassio_addon_config_decorate([Object(lit_element["d" /* customElement */])("hassio-addon-config")], function (_initialize, _LitElement) {
  var HassioAddonConfig = /*#__PURE__*/function (_LitElement2) {
    hassio_addon_config_inherits(HassioAddonConfig, _LitElement2);

    var _super = hassio_addon_config_createSuper(HassioAddonConfig);

    function HassioAddonConfig() {
      var _this;

      hassio_addon_config_classCallCheck(this, HassioAddonConfig);

      for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
        args[_key] = arguments[_key];
      }

      _this = _super.call.apply(_super, [this].concat(args));

      _initialize(hassio_addon_config_assertThisInitialized(_this));

      return _this;
    }

    return HassioAddonConfig;
  }(_LitElement);

  return {
    F: HassioAddonConfig,
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
      key: "addon",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "_error",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])({
        type: Boolean
      })],
      key: "_configHasChanged",
      value: function value() {
        return false;
      }
    }, {
      kind: "field",
      decorators: [Object(lit_element["g" /* query */])("ha-yaml-editor")],
      key: "_editor",
      value: void 0
    }, {
      kind: "method",
      key: "render",
      value: function render() {
        var editor = this._editor; // If editor not rendered, don't show the error.

        var valid = editor ? editor.isValid : true;
        return Object(lit_element["e" /* html */])(hassio_addon_config_templateObject(), this.addon.name, this._configChanged, this._error ? Object(lit_element["e" /* html */])(hassio_addon_config_templateObject2(), this._error) : "", valid ? "" : Object(lit_element["e" /* html */])(hassio_addon_config_templateObject3()), this._resetTapped, this._saveTapped, !this._configHasChanged || !valid);
      }
    }, {
      kind: "get",
      "static": true,
      key: "styles",
      value: function styles() {
        return [resources_styles["b" /* haStyle */], hassio_style["a" /* hassioStyle */], Object(lit_element["c" /* css */])(hassio_addon_config_templateObject4())];
      }
    }, {
      kind: "method",
      key: "updated",
      value: function updated(changedProperties) {
        hassio_addon_config_get(hassio_addon_config_getPrototypeOf(HassioAddonConfig.prototype), "updated", this).call(this, changedProperties);

        if (changedProperties.has("addon")) {
          this._editor.setValue(this.addon.options);
        }
      }
    }, {
      kind: "method",
      key: "_configChanged",
      value: function _configChanged() {
        this._configHasChanged = true;
        this.requestUpdate();
      }
    }, {
      kind: "method",
      key: "_resetTapped",
      value: function () {
        var _resetTapped2 = hassio_addon_config_asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee() {
          var confirmed, data, eventdata, _err$body;

          return regeneratorRuntime.wrap(function _callee$(_context) {
            while (1) {
              switch (_context.prev = _context.next) {
                case 0:
                  _context.next = 2;
                  return Object(show_dialog_box["b" /* showConfirmationDialog */])(this, {
                    title: this.addon.name,
                    text: "Are you sure you want to reset all your options?",
                    confirmText: "reset options",
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
                  this._error = undefined;
                  data = {
                    options: null
                  };
                  _context.prev = 7;
                  _context.next = 10;
                  return Object(hassio_addon["i" /* setHassioAddonOption */])(this.hass, this.addon.slug, data);

                case 10:
                  this._configHasChanged = false;
                  eventdata = {
                    success: true,
                    response: undefined,
                    path: "options"
                  };
                  Object(fire_event["a" /* fireEvent */])(this, "hass-api-called", eventdata);
                  _context.next = 18;
                  break;

                case 15:
                  _context.prev = 15;
                  _context.t0 = _context["catch"](7);
                  this._error = "Failed to reset addon configuration, ".concat(((_err$body = _context.t0.body) === null || _err$body === void 0 ? void 0 : _err$body.message) || _context.t0);

                case 18:
                case "end":
                  return _context.stop();
              }
            }
          }, _callee, this, [[7, 15]]);
        }));

        function _resetTapped() {
          return _resetTapped2.apply(this, arguments);
        }

        return _resetTapped;
      }()
    }, {
      kind: "method",
      key: "_saveTapped",
      value: function () {
        var _saveTapped2 = hassio_addon_config_asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee2() {
          var _this$addon;

          var data, eventdata, _err$body2;

          return regeneratorRuntime.wrap(function _callee2$(_context2) {
            while (1) {
              switch (_context2.prev = _context2.next) {
                case 0:
                  this._error = undefined;
                  _context2.prev = 1;
                  data = {
                    options: this._editor.value
                  };
                  _context2.next = 9;
                  break;

                case 5:
                  _context2.prev = 5;
                  _context2.t0 = _context2["catch"](1);
                  this._error = _context2.t0;
                  return _context2.abrupt("return");

                case 9:
                  _context2.prev = 9;
                  _context2.next = 12;
                  return Object(hassio_addon["i" /* setHassioAddonOption */])(this.hass, this.addon.slug, data);

                case 12:
                  this._configHasChanged = false;
                  eventdata = {
                    success: true,
                    response: undefined,
                    path: "options"
                  };
                  Object(fire_event["a" /* fireEvent */])(this, "hass-api-called", eventdata);
                  _context2.next = 20;
                  break;

                case 17:
                  _context2.prev = 17;
                  _context2.t1 = _context2["catch"](9);
                  this._error = "Failed to save addon configuration, ".concat(((_err$body2 = _context2.t1.body) === null || _err$body2 === void 0 ? void 0 : _err$body2.message) || _context2.t1);

                case 20:
                  if (!(!this._error && ((_this$addon = this.addon) === null || _this$addon === void 0 ? void 0 : _this$addon.state) === "started")) {
                    _context2.next = 23;
                    break;
                  }

                  _context2.next = 23;
                  return suggestAddonRestart(this, this.hass, this.addon);

                case 23:
                case "end":
                  return _context2.stop();
              }
            }
          }, _callee2, this, [[1, 5], [9, 17]]);
        }));

        function _saveTapped() {
          return _saveTapped2.apply(this, arguments);
        }

        return _saveTapped;
      }()
    }]
  };
}, lit_element["a" /* LitElement */]);
// EXTERNAL MODULE: ./node_modules/@polymer/paper-tooltip/paper-tooltip.js
var paper_tooltip = __webpack_require__(178);

// EXTERNAL MODULE: ./node_modules/lit-html/directives/class-map.js
var class_map = __webpack_require__(26);

// EXTERNAL MODULE: ./src/common/config/version.ts
var version = __webpack_require__(91);

// EXTERNAL MODULE: ./src/common/navigate.ts
var common_navigate = __webpack_require__(38);

// EXTERNAL MODULE: ./src/components/buttons/ha-call-api-button.js
var ha_call_api_button = __webpack_require__(71);

// EXTERNAL MODULE: ./src/components/buttons/ha-progress-button.js
var ha_progress_button = __webpack_require__(121);

// EXTERNAL MODULE: ./src/components/ha-icon.ts + 3 modules
var ha_icon = __webpack_require__(32);

// CONCATENATED MODULE: ./src/components/ha-label-badge.ts
function ha_label_badge_typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { ha_label_badge_typeof = function _typeof(obj) { return typeof obj; }; } else { ha_label_badge_typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return ha_label_badge_typeof(obj); }

function _templateObject6() {
  var data = ha_label_badge_taggedTemplateLiteral(["\n        .badge-container {\n          display: inline-block;\n          text-align: center;\n          vertical-align: top;\n          padding: var(--ha-label-badge-padding, 0 0 0 0);\n        }\n        .label-badge {\n          position: relative;\n          display: block;\n          margin: 0 auto;\n          width: var(--ha-label-badge-size, 2.5em);\n          text-align: center;\n          height: var(--ha-label-badge-size, 2.5em);\n          line-height: var(--ha-label-badge-size, 2.5em);\n          font-size: var(--ha-label-badge-font-size, 1.5em);\n          border-radius: 50%;\n          border: 0.1em solid var(--ha-label-badge-color, var(--primary-color));\n          color: var(--label-badge-text-color, rgb(76, 76, 76));\n\n          white-space: nowrap;\n          background-color: var(--label-badge-background-color, white);\n          background-size: cover;\n          transition: border 0.3s ease-in-out;\n        }\n        .label-badge .value {\n          font-size: 90%;\n          overflow: hidden;\n          text-overflow: ellipsis;\n        }\n        .label-badge .value.big {\n          font-size: 70%;\n        }\n        .label-badge .label {\n          position: absolute;\n          bottom: -1em;\n          /* Make the label as wide as container+border. (parent_borderwidth / font-size) */\n          left: -0.2em;\n          right: -0.2em;\n          line-height: 1em;\n          font-size: 0.5em;\n        }\n        .label-badge .label span {\n          box-sizing: border-box;\n          max-width: 100%;\n          display: inline-block;\n          background-color: var(--ha-label-badge-color, var(--primary-color));\n          color: var(--ha-label-badge-label-color, white);\n          border-radius: 1em;\n          padding: 9% 16% 8% 16%; /* mostly apitalized text, not much descenders => bit more top margin */\n          font-weight: 500;\n          overflow: hidden;\n          text-transform: uppercase;\n          text-overflow: ellipsis;\n          transition: background-color 0.3s ease-in-out;\n          text-transform: var(--ha-label-badge-label-text-transform, uppercase);\n        }\n        .label-badge .label.big span {\n          font-size: 90%;\n          padding: 10% 12% 7% 12%; /* push smaller text a bit down to center vertically */\n        }\n        .badge-container .title {\n          margin-top: 1em;\n          font-size: var(--ha-label-badge-title-font-size, 0.9em);\n          width: var(--ha-label-badge-title-width, 5em);\n          font-weight: var(--ha-label-badge-title-font-weight, 400);\n          overflow: hidden;\n          text-overflow: ellipsis;\n          line-height: normal;\n        }\n      "]);

  _templateObject6 = function _templateObject6() {
    return data;
  };

  return data;
}

function ha_label_badge_templateObject5() {
  var data = ha_label_badge_taggedTemplateLiteral([" <div class=\"title\">", "</div> "]);

  ha_label_badge_templateObject5 = function _templateObject5() {
    return data;
  };

  return data;
}

function ha_label_badge_templateObject4() {
  var data = ha_label_badge_taggedTemplateLiteral(["\n                <div\n                  class=\"", "\"\n                >\n                  <span>", "</span>\n                </div>\n              "]);

  ha_label_badge_templateObject4 = function _templateObject4() {
    return data;
  };

  return data;
}

function ha_label_badge_templateObject3() {
  var data = ha_label_badge_taggedTemplateLiteral([" <span>", "</span> "]);

  ha_label_badge_templateObject3 = function _templateObject3() {
    return data;
  };

  return data;
}

function ha_label_badge_templateObject2() {
  var data = ha_label_badge_taggedTemplateLiteral([" <ha-icon .icon=\"", "\"></ha-icon> "]);

  ha_label_badge_templateObject2 = function _templateObject2() {
    return data;
  };

  return data;
}

function ha_label_badge_templateObject() {
  var data = ha_label_badge_taggedTemplateLiteral(["\n      <div class=\"badge-container\">\n        <div class=\"label-badge\" id=\"badge\">\n          <div\n            class=\"", "\"\n          >\n            ", "\n            ", "\n          </div>\n          ", "\n        </div>\n        ", "\n      </div>\n    "]);

  ha_label_badge_templateObject = function _templateObject() {
    return data;
  };

  return data;
}

function ha_label_badge_taggedTemplateLiteral(strings, raw) { if (!raw) { raw = strings.slice(0); } return Object.freeze(Object.defineProperties(strings, { raw: { value: Object.freeze(raw) } })); }

function ha_label_badge_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function ha_label_badge_inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) ha_label_badge_setPrototypeOf(subClass, superClass); }

function ha_label_badge_setPrototypeOf(o, p) { ha_label_badge_setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return ha_label_badge_setPrototypeOf(o, p); }

function ha_label_badge_createSuper(Derived) { return function () { var Super = ha_label_badge_getPrototypeOf(Derived), result; if (ha_label_badge_isNativeReflectConstruct()) { var NewTarget = ha_label_badge_getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return ha_label_badge_possibleConstructorReturn(this, result); }; }

function ha_label_badge_possibleConstructorReturn(self, call) { if (call && (ha_label_badge_typeof(call) === "object" || typeof call === "function")) { return call; } return ha_label_badge_assertThisInitialized(self); }

function ha_label_badge_assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function ha_label_badge_isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Date.prototype.toString.call(Reflect.construct(Date, [], function () {})); return true; } catch (e) { return false; } }

function ha_label_badge_decorate(decorators, factory, superClass, mixins) { var api = ha_label_badge_getDecoratorsApi(); if (mixins) { for (var i = 0; i < mixins.length; i++) { api = mixins[i](api); } } var r = factory(function initialize(O) { api.initializeInstanceElements(O, decorated.elements); }, superClass); var decorated = api.decorateClass(ha_label_badge_coalesceClassElements(r.d.map(ha_label_badge_createElementDescriptor)), decorators); api.initializeClassElements(r.F, decorated.elements); return api.runClassFinishers(r.F, decorated.finishers); }

function ha_label_badge_getDecoratorsApi() { ha_label_badge_getDecoratorsApi = function _getDecoratorsApi() { return api; }; var api = { elementsDefinitionOrder: [["method"], ["field"]], initializeInstanceElements: function initializeInstanceElements(O, elements) { ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { if (element.kind === kind && element.placement === "own") { this.defineClassElement(O, element); } }, this); }, this); }, initializeClassElements: function initializeClassElements(F, elements) { var proto = F.prototype; ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { var placement = element.placement; if (element.kind === kind && (placement === "static" || placement === "prototype")) { var receiver = placement === "static" ? F : proto; this.defineClassElement(receiver, element); } }, this); }, this); }, defineClassElement: function defineClassElement(receiver, element) { var descriptor = element.descriptor; if (element.kind === "field") { var initializer = element.initializer; descriptor = { enumerable: descriptor.enumerable, writable: descriptor.writable, configurable: descriptor.configurable, value: initializer === void 0 ? void 0 : initializer.call(receiver) }; } Object.defineProperty(receiver, element.key, descriptor); }, decorateClass: function decorateClass(elements, decorators) { var newElements = []; var finishers = []; var placements = { "static": [], prototype: [], own: [] }; elements.forEach(function (element) { this.addElementPlacement(element, placements); }, this); elements.forEach(function (element) { if (!ha_label_badge_hasDecorators(element)) return newElements.push(element); var elementFinishersExtras = this.decorateElement(element, placements); newElements.push(elementFinishersExtras.element); newElements.push.apply(newElements, elementFinishersExtras.extras); finishers.push.apply(finishers, elementFinishersExtras.finishers); }, this); if (!decorators) { return { elements: newElements, finishers: finishers }; } var result = this.decorateConstructor(newElements, decorators); finishers.push.apply(finishers, result.finishers); result.finishers = finishers; return result; }, addElementPlacement: function addElementPlacement(element, placements, silent) { var keys = placements[element.placement]; if (!silent && keys.indexOf(element.key) !== -1) { throw new TypeError("Duplicated element (" + element.key + ")"); } keys.push(element.key); }, decorateElement: function decorateElement(element, placements) { var extras = []; var finishers = []; for (var decorators = element.decorators, i = decorators.length - 1; i >= 0; i--) { var keys = placements[element.placement]; keys.splice(keys.indexOf(element.key), 1); var elementObject = this.fromElementDescriptor(element); var elementFinisherExtras = this.toElementFinisherExtras((0, decorators[i])(elementObject) || elementObject); element = elementFinisherExtras.element; this.addElementPlacement(element, placements); if (elementFinisherExtras.finisher) { finishers.push(elementFinisherExtras.finisher); } var newExtras = elementFinisherExtras.extras; if (newExtras) { for (var j = 0; j < newExtras.length; j++) { this.addElementPlacement(newExtras[j], placements); } extras.push.apply(extras, newExtras); } } return { element: element, finishers: finishers, extras: extras }; }, decorateConstructor: function decorateConstructor(elements, decorators) { var finishers = []; for (var i = decorators.length - 1; i >= 0; i--) { var obj = this.fromClassDescriptor(elements); var elementsAndFinisher = this.toClassDescriptor((0, decorators[i])(obj) || obj); if (elementsAndFinisher.finisher !== undefined) { finishers.push(elementsAndFinisher.finisher); } if (elementsAndFinisher.elements !== undefined) { elements = elementsAndFinisher.elements; for (var j = 0; j < elements.length - 1; j++) { for (var k = j + 1; k < elements.length; k++) { if (elements[j].key === elements[k].key && elements[j].placement === elements[k].placement) { throw new TypeError("Duplicated element (" + elements[j].key + ")"); } } } } } return { elements: elements, finishers: finishers }; }, fromElementDescriptor: function fromElementDescriptor(element) { var obj = { kind: element.kind, key: element.key, placement: element.placement, descriptor: element.descriptor }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); if (element.kind === "field") obj.initializer = element.initializer; return obj; }, toElementDescriptors: function toElementDescriptors(elementObjects) { if (elementObjects === undefined) return; return ha_label_badge_toArray(elementObjects).map(function (elementObject) { var element = this.toElementDescriptor(elementObject); this.disallowProperty(elementObject, "finisher", "An element descriptor"); this.disallowProperty(elementObject, "extras", "An element descriptor"); return element; }, this); }, toElementDescriptor: function toElementDescriptor(elementObject) { var kind = String(elementObject.kind); if (kind !== "method" && kind !== "field") { throw new TypeError('An element descriptor\'s .kind property must be either "method" or' + ' "field", but a decorator created an element descriptor with' + ' .kind "' + kind + '"'); } var key = ha_label_badge_toPropertyKey(elementObject.key); var placement = String(elementObject.placement); if (placement !== "static" && placement !== "prototype" && placement !== "own") { throw new TypeError('An element descriptor\'s .placement property must be one of "static",' + ' "prototype" or "own", but a decorator created an element descriptor' + ' with .placement "' + placement + '"'); } var descriptor = elementObject.descriptor; this.disallowProperty(elementObject, "elements", "An element descriptor"); var element = { kind: kind, key: key, placement: placement, descriptor: Object.assign({}, descriptor) }; if (kind !== "field") { this.disallowProperty(elementObject, "initializer", "A method descriptor"); } else { this.disallowProperty(descriptor, "get", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "set", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "value", "The property descriptor of a field descriptor"); element.initializer = elementObject.initializer; } return element; }, toElementFinisherExtras: function toElementFinisherExtras(elementObject) { var element = this.toElementDescriptor(elementObject); var finisher = ha_label_badge_optionalCallableProperty(elementObject, "finisher"); var extras = this.toElementDescriptors(elementObject.extras); return { element: element, finisher: finisher, extras: extras }; }, fromClassDescriptor: function fromClassDescriptor(elements) { var obj = { kind: "class", elements: elements.map(this.fromElementDescriptor, this) }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); return obj; }, toClassDescriptor: function toClassDescriptor(obj) { var kind = String(obj.kind); if (kind !== "class") { throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator' + ' created a class descriptor with .kind "' + kind + '"'); } this.disallowProperty(obj, "key", "A class descriptor"); this.disallowProperty(obj, "placement", "A class descriptor"); this.disallowProperty(obj, "descriptor", "A class descriptor"); this.disallowProperty(obj, "initializer", "A class descriptor"); this.disallowProperty(obj, "extras", "A class descriptor"); var finisher = ha_label_badge_optionalCallableProperty(obj, "finisher"); var elements = this.toElementDescriptors(obj.elements); return { elements: elements, finisher: finisher }; }, runClassFinishers: function runClassFinishers(constructor, finishers) { for (var i = 0; i < finishers.length; i++) { var newConstructor = (0, finishers[i])(constructor); if (newConstructor !== undefined) { if (typeof newConstructor !== "function") { throw new TypeError("Finishers must return a constructor."); } constructor = newConstructor; } } return constructor; }, disallowProperty: function disallowProperty(obj, name, objectType) { if (obj[name] !== undefined) { throw new TypeError(objectType + " can't have a ." + name + " property."); } } }; return api; }

function ha_label_badge_createElementDescriptor(def) { var key = ha_label_badge_toPropertyKey(def.key); var descriptor; if (def.kind === "method") { descriptor = { value: def.value, writable: true, configurable: true, enumerable: false }; } else if (def.kind === "get") { descriptor = { get: def.value, configurable: true, enumerable: false }; } else if (def.kind === "set") { descriptor = { set: def.value, configurable: true, enumerable: false }; } else if (def.kind === "field") { descriptor = { configurable: true, writable: true, enumerable: true }; } var element = { kind: def.kind === "field" ? "field" : "method", key: key, placement: def["static"] ? "static" : def.kind === "field" ? "own" : "prototype", descriptor: descriptor }; if (def.decorators) element.decorators = def.decorators; if (def.kind === "field") element.initializer = def.value; return element; }

function ha_label_badge_coalesceGetterSetter(element, other) { if (element.descriptor.get !== undefined) { other.descriptor.get = element.descriptor.get; } else { other.descriptor.set = element.descriptor.set; } }

function ha_label_badge_coalesceClassElements(elements) { var newElements = []; var isSameElement = function isSameElement(other) { return other.kind === "method" && other.key === element.key && other.placement === element.placement; }; for (var i = 0; i < elements.length; i++) { var element = elements[i]; var other; if (element.kind === "method" && (other = newElements.find(isSameElement))) { if (ha_label_badge_isDataDescriptor(element.descriptor) || ha_label_badge_isDataDescriptor(other.descriptor)) { if (ha_label_badge_hasDecorators(element) || ha_label_badge_hasDecorators(other)) { throw new ReferenceError("Duplicated methods (" + element.key + ") can't be decorated."); } other.descriptor = element.descriptor; } else { if (ha_label_badge_hasDecorators(element)) { if (ha_label_badge_hasDecorators(other)) { throw new ReferenceError("Decorators can't be placed on different accessors with for " + "the same property (" + element.key + ")."); } other.decorators = element.decorators; } ha_label_badge_coalesceGetterSetter(element, other); } } else { newElements.push(element); } } return newElements; }

function ha_label_badge_hasDecorators(element) { return element.decorators && element.decorators.length; }

function ha_label_badge_isDataDescriptor(desc) { return desc !== undefined && !(desc.value === undefined && desc.writable === undefined); }

function ha_label_badge_optionalCallableProperty(obj, name) { var value = obj[name]; if (value !== undefined && typeof value !== "function") { throw new TypeError("Expected '" + name + "' to be a function"); } return value; }

function ha_label_badge_toPropertyKey(arg) { var key = ha_label_badge_toPrimitive(arg, "string"); return ha_label_badge_typeof(key) === "symbol" ? key : String(key); }

function ha_label_badge_toPrimitive(input, hint) { if (ha_label_badge_typeof(input) !== "object" || input === null) return input; var prim = input[Symbol.toPrimitive]; if (prim !== undefined) { var res = prim.call(input, hint || "default"); if (ha_label_badge_typeof(res) !== "object") return res; throw new TypeError("@@toPrimitive must return a primitive value."); } return (hint === "string" ? String : Number)(input); }

function ha_label_badge_toArray(arr) { return ha_label_badge_arrayWithHoles(arr) || ha_label_badge_iterableToArray(arr) || ha_label_badge_unsupportedIterableToArray(arr) || ha_label_badge_nonIterableRest(); }

function ha_label_badge_nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function ha_label_badge_unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return ha_label_badge_arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(n); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return ha_label_badge_arrayLikeToArray(o, minLen); }

function ha_label_badge_arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function ha_label_badge_iterableToArray(iter) { if (typeof Symbol !== "undefined" && Symbol.iterator in Object(iter)) return Array.from(iter); }

function ha_label_badge_arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }

function ha_label_badge_get(target, property, receiver) { if (typeof Reflect !== "undefined" && Reflect.get) { ha_label_badge_get = Reflect.get; } else { ha_label_badge_get = function _get(target, property, receiver) { var base = ha_label_badge_superPropBase(target, property); if (!base) return; var desc = Object.getOwnPropertyDescriptor(base, property); if (desc.get) { return desc.get.call(receiver); } return desc.value; }; } return ha_label_badge_get(target, property, receiver || target); }

function ha_label_badge_superPropBase(object, property) { while (!Object.prototype.hasOwnProperty.call(object, property)) { object = ha_label_badge_getPrototypeOf(object); if (object === null) break; } return object; }

function ha_label_badge_getPrototypeOf(o) { ha_label_badge_getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return ha_label_badge_getPrototypeOf(o); }





var ha_label_badge_HaLabelBadge = ha_label_badge_decorate(null, function (_initialize, _LitElement) {
  var HaLabelBadge = /*#__PURE__*/function (_LitElement2) {
    ha_label_badge_inherits(HaLabelBadge, _LitElement2);

    var _super = ha_label_badge_createSuper(HaLabelBadge);

    function HaLabelBadge() {
      var _this;

      ha_label_badge_classCallCheck(this, HaLabelBadge);

      for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
        args[_key] = arguments[_key];
      }

      _this = _super.call.apply(_super, [this].concat(args));

      _initialize(ha_label_badge_assertThisInitialized(_this));

      return _this;
    }

    return HaLabelBadge;
  }(_LitElement);

  return {
    F: HaLabelBadge,
    d: [{
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "value",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "icon",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "label",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "description",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "image",
      value: void 0
    }, {
      kind: "method",
      key: "render",
      value: function render() {
        return Object(lit_element["e" /* html */])(ha_label_badge_templateObject(), Object(class_map["a" /* classMap */])({
          value: true,
          big: Boolean(this.value && this.value.length > 4)
        }), this.icon && !this.value && !this.image ? Object(lit_element["e" /* html */])(ha_label_badge_templateObject2(), this.icon) : "", this.value && !this.image ? Object(lit_element["e" /* html */])(ha_label_badge_templateObject3(), this.value) : "", this.label ? Object(lit_element["e" /* html */])(ha_label_badge_templateObject4(), Object(class_map["a" /* classMap */])({
          label: true,
          big: this.label.length > 5
        }), this.label) : "", this.description ? Object(lit_element["e" /* html */])(ha_label_badge_templateObject5(), this.description) : "");
      }
    }, {
      kind: "get",
      "static": true,
      key: "styles",
      value: function styles() {
        return [Object(lit_element["c" /* css */])(_templateObject6())];
      }
    }, {
      kind: "method",
      key: "updated",
      value: function updated(changedProperties) {
        ha_label_badge_get(ha_label_badge_getPrototypeOf(HaLabelBadge.prototype), "updated", this).call(this, changedProperties);

        if (changedProperties.has("image")) {
          this.shadowRoot.getElementById("badge").style.backgroundImage = this.image ? "url(".concat(this.image, ")") : "";
        }
      }
    }]
  };
}, lit_element["a" /* LitElement */]);

customElements.define("ha-label-badge", ha_label_badge_HaLabelBadge);
// EXTERNAL MODULE: ./src/components/ha-markdown.ts
var ha_markdown = __webpack_require__(74);

// EXTERNAL MODULE: ./src/components/ha-switch.ts + 1 modules
var ha_switch = __webpack_require__(102);

// EXTERNAL MODULE: ./hassio/src/components/hassio-card-content.ts + 3 modules
var hassio_card_content = __webpack_require__(56);

// EXTERNAL MODULE: ./hassio/src/dialogs/markdown/show-dialog-hassio-markdown.ts
var show_dialog_hassio_markdown = __webpack_require__(128);

// CONCATENATED MODULE: ./hassio/src/addon-view/info/hassio-addon-info.ts
function hassio_addon_info_typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { hassio_addon_info_typeof = function _typeof(obj) { return typeof obj; }; } else { hassio_addon_info_typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return hassio_addon_info_typeof(obj); }

function hassio_addon_info_asyncGeneratorStep(gen, resolve, reject, _next, _throw, key, arg) { try { var info = gen[key](arg); var value = info.value; } catch (error) { reject(error); return; } if (info.done) { resolve(value); } else { Promise.resolve(value).then(_next, _throw); } }

function hassio_addon_info_asyncToGenerator(fn) { return function () { var self = this, args = arguments; return new Promise(function (resolve, reject) { var gen = fn.apply(self, args); function _next(value) { hassio_addon_info_asyncGeneratorStep(gen, resolve, reject, _next, _throw, "next", value); } function _throw(err) { hassio_addon_info_asyncGeneratorStep(gen, resolve, reject, _next, _throw, "throw", err); } _next(undefined); }); }; }

function _templateObject37() {
  var data = hassio_addon_info_taggedTemplateLiteral(["\n        :host {\n          display: block;\n        }\n        paper-card {\n          display: block;\n          margin-bottom: 16px;\n        }\n        paper-card.warning {\n          background-color: var(--google-red-500);\n          color: white;\n          --paper-card-header-color: white;\n        }\n        paper-card.warning mwc-button {\n          --mdc-theme-primary: white !important;\n        }\n        .warning {\n          color: var(--google-red-500);\n          --mdc-theme-primary: var(--google-red-500);\n        }\n        .light-color {\n          color: var(--secondary-text-color);\n        }\n        .addon-header {\n          padding-left: 8px;\n          font-size: 24px;\n          color: var(--paper-card-header-color, --primary-text-color);\n        }\n        .addon-version {\n          float: right;\n          font-size: 15px;\n          vertical-align: middle;\n        }\n        .errors {\n          color: var(--google-red-500);\n          margin-bottom: 16px;\n        }\n        .description {\n          margin-bottom: 16px;\n        }\n        img.logo {\n          max-height: 60px;\n          margin: 16px 0;\n          display: block;\n        }\n        .state {\n          display: flex;\n          margin: 33px 0;\n        }\n        .state div {\n          width: 180px;\n          display: inline-block;\n        }\n        .state ha-icon {\n          width: 16px;\n          height: 16px;\n          color: var(--secondary-text-color);\n        }\n        ha-switch {\n          display: flex;\n        }\n        ha-icon.running {\n          color: var(--paper-green-400);\n        }\n        ha-icon.stopped {\n          color: var(--google-red-300);\n        }\n        ha-call-api-button {\n          font-weight: 500;\n          color: var(--primary-color);\n        }\n        .right {\n          float: right;\n        }\n        ha-markdown img {\n          max-width: 100%;\n        }\n        protection-enable mwc-button {\n          --mdc-theme-primary: white;\n        }\n        .description a,\n        ha-markdown a {\n          color: var(--primary-color);\n        }\n        .red {\n          --ha-label-badge-color: var(--label-badge-red, #df4c1e);\n        }\n        .blue {\n          --ha-label-badge-color: var(--label-badge-blue, #039be5);\n        }\n        .green {\n          --ha-label-badge-color: var(--label-badge-green, #0da035);\n        }\n        .yellow {\n          --ha-label-badge-color: var(--label-badge-yellow, #f4b400);\n        }\n        .security {\n          margin-bottom: 16px;\n        }\n        .card-actions {\n          display: flow-root;\n        }\n        .security h3 {\n          margin-bottom: 8px;\n          font-weight: normal;\n        }\n        .security ha-label-badge {\n          cursor: pointer;\n          margin-right: 4px;\n          --ha-label-badge-padding: 8px 0 0 0;\n        }\n        .changelog {\n          display: contents;\n        }\n        .changelog-link {\n          color: var(--primary-color);\n          text-decoration: underline;\n          cursor: pointer;\n        }\n      "]);

  _templateObject37 = function _templateObject37() {
    return data;
  };

  return data;
}

function _templateObject36() {
  var data = hassio_addon_info_taggedTemplateLiteral(["\n            <paper-card>\n              <div class=\"card-content\">\n                <ha-markdown\n                  .content=", "\n                ></ha-markdown>\n              </div>\n            </paper-card>\n          "]);

  _templateObject36 = function _templateObject36() {
    return data;
  };

  return data;
}

function _templateObject35() {
  var data = hassio_addon_info_taggedTemplateLiteral(["\n                      <p class=\"warning\">\n                        This add-on is not available on your system.\n                      </p>\n                    "]);

  _templateObject35 = function _templateObject35() {
    return data;
  };

  return data;
}

function _templateObject34() {
  var data = hassio_addon_info_taggedTemplateLiteral(["\n                ", "\n                <ha-progress-button\n                  .disabled=", "\n                  .progress=", "\n                  @click=", "\n                >\n                  Install\n                </ha-progress-button>\n              "]);

  _templateObject34 = function _templateObject34() {
    return data;
  };

  return data;
}

function _templateObject33() {
  var data = hassio_addon_info_taggedTemplateLiteral(["\n                      <ha-call-api-button\n                        class=\"warning right\"\n                        .hass=", "\n                        .path=\"hassio/addons/", "/rebuild\"\n                      >\n                        Rebuild\n                      </ha-call-api-button>\n                    "]);

  _templateObject33 = function _templateObject33() {
    return data;
  };

  return data;
}

function _templateObject32() {
  var data = hassio_addon_info_taggedTemplateLiteral(["\n                      <mwc-button class=\"right\" @click=", ">\n                        Open web UI\n                      </mwc-button>\n                    "]);

  _templateObject32 = function _templateObject32() {
    return data;
  };

  return data;
}

function _templateObject31() {
  var data = hassio_addon_info_taggedTemplateLiteral(["\n                      <a\n                        href=", "\n                        tabindex=\"-1\"\n                        target=\"_blank\"\n                        class=\"right\"\n                        rel=\"noopener\"\n                      >\n                        <mwc-button>\n                          Open web UI\n                        </mwc-button>\n                      </a>\n                    "]);

  _templateObject31 = function _templateObject31() {
    return data;
  };

  return data;
}

function _templateObject30() {
  var data = hassio_addon_info_taggedTemplateLiteral(["\n                      <ha-call-api-button\n                        .hass=", "\n                        .path=\"hassio/addons/", "/start\"\n                      >\n                        Start\n                      </ha-call-api-button>\n                    "]);

  _templateObject30 = function _templateObject30() {
    return data;
  };

  return data;
}

function _templateObject29() {
  var data = hassio_addon_info_taggedTemplateLiteral(["\n                      <ha-call-api-button\n                        class=\"warning\"\n                        .hass=", "\n                        .path=\"hassio/addons/", "/stop\"\n                      >\n                        Stop\n                      </ha-call-api-button>\n                      <ha-call-api-button\n                        class=\"warning\"\n                        .hass=", "\n                        .path=\"hassio/addons/", "/restart\"\n                      >\n                        Restart\n                      </ha-call-api-button>\n                    "]);

  _templateObject29 = function _templateObject29() {
    return data;
  };

  return data;
}

function _templateObject28() {
  var data = hassio_addon_info_taggedTemplateLiteral(["\n                ", "\n                ", "\n                ", "\n                <mwc-button\n                  class=\" right warning\"\n                  @click=", "\n                >\n                  Uninstall\n                </mwc-button>\n                ", "\n              "]);

  _templateObject28 = function _templateObject28() {
    return data;
  };

  return data;
}

function _templateObject27() {
  var data = hassio_addon_info_taggedTemplateLiteral([" <div class=\"errors\">", "</div> "]);

  _templateObject27 = function _templateObject27() {
    return data;
  };

  return data;
}

function _templateObject26() {
  var data = hassio_addon_info_taggedTemplateLiteral(["\n                      <div class=\"state\">\n                        <div>\n                          Protection mode\n                          <span>\n                            <ha-icon icon=\"hassio:information\"></ha-icon>\n                            <paper-tooltip>\n                              Grant the add-on elevated system access.\n                            </paper-tooltip>\n                          </span>\n                        </div>\n                        <ha-switch\n                          @change=", "\n                          .checked=", "\n                          haptic\n                        ></ha-switch>\n                      </div>\n                    "]);

  _templateObject26 = function _templateObject26() {
    return data;
  };

  return data;
}

function _templateObject25() {
  var data = hassio_addon_info_taggedTemplateLiteral(["\n                              <span>\n                                This option requires Home Assistant 0.92 or\n                                later.\n                              </span>\n                            "]);

  _templateObject25 = function _templateObject25() {
    return data;
  };

  return data;
}

function _templateObject24() {
  var data = hassio_addon_info_taggedTemplateLiteral(["\n                      <div class=\"state\">\n                        <div>Show in sidebar</div>\n                        <ha-switch\n                          @change=", "\n                          .checked=", "\n                          .disabled=", "\n                          haptic\n                        ></ha-switch>\n                        ", "\n                      </div>\n                    "]);

  _templateObject24 = function _templateObject24() {
    return data;
  };

  return data;
}

function _templateObject23() {
  var data = hassio_addon_info_taggedTemplateLiteral(["\n                      <div class=\"state\">\n                        <div>Auto update</div>\n                        <ha-switch\n                          @change=", "\n                          .checked=", "\n                          haptic\n                        ></ha-switch>\n                      </div>\n                    "]);

  _templateObject23 = function _templateObject23() {
    return data;
  };

  return data;
}

function _templateObject22() {
  var data = hassio_addon_info_taggedTemplateLiteral(["\n                <div class=\"state\">\n                  <div>Start on boot</div>\n                  <ha-switch\n                    @change=", "\n                    .checked=", "\n                    haptic\n                  ></ha-switch>\n                </div>\n                ", "\n                ", "\n                ", "\n              "]);

  _templateObject22 = function _templateObject22() {
    return data;
  };

  return data;
}

function _templateObject21() {
  var data = hassio_addon_info_taggedTemplateLiteral(["\n                  <ha-label-badge\n                    @click=", "\n                    id=\"ingress\"\n                    icon=\"hassio:cursor-default-click-outline\"\n                    label=\"ingress\"\n                    description=\"\"\n                  ></ha-label-badge>\n                "]);

  _templateObject21 = function _templateObject21() {
    return data;
  };

  return data;
}

function _templateObject20() {
  var data = hassio_addon_info_taggedTemplateLiteral(["\n                  <ha-label-badge\n                    @click=", "\n                    id=\"auth_api\"\n                    icon=\"hassio:key\"\n                    label=\"auth\"\n                    description=\"\"\n                  ></ha-label-badge>\n                "]);

  _templateObject20 = function _templateObject20() {
    return data;
  };

  return data;
}

function _templateObject19() {
  var data = hassio_addon_info_taggedTemplateLiteral(["\n                  <ha-label-badge\n                    @click=", "\n                    class=", "\n                    id=\"apparmor\"\n                    icon=\"hassio:shield\"\n                    label=\"apparmor\"\n                    description=\"\"\n                  ></ha-label-badge>\n                "]);

  _templateObject19 = function _templateObject19() {
    return data;
  };

  return data;
}

function _templateObject18() {
  var data = hassio_addon_info_taggedTemplateLiteral(["\n                  <ha-label-badge\n                    @click=", "\n                    id=\"host_pid\"\n                    icon=\"hassio:pound\"\n                    label=\"host pid\"\n                    description=\"\"\n                  ></ha-label-badge>\n                "]);

  _templateObject18 = function _templateObject18() {
    return data;
  };

  return data;
}

function _templateObject17() {
  var data = hassio_addon_info_taggedTemplateLiteral(["\n                  <ha-label-badge\n                    @click=", "\n                    id=\"docker_api\"\n                    icon=\"hassio:docker\"\n                    label=\"docker\"\n                    description=\"\"\n                  ></ha-label-badge>\n                "]);

  _templateObject17 = function _templateObject17() {
    return data;
  };

  return data;
}

function _templateObject16() {
  var data = hassio_addon_info_taggedTemplateLiteral(["\n                  <ha-label-badge\n                    @click=", "\n                    id=\"hassio_api\"\n                    icon=\"hassio:home-assistant\"\n                    label=\"hassio\"\n                    .description=", "\n                  ></ha-label-badge>\n                "]);

  _templateObject16 = function _templateObject16() {
    return data;
  };

  return data;
}

function _templateObject15() {
  var data = hassio_addon_info_taggedTemplateLiteral(["\n                  <ha-label-badge\n                    @click=", "\n                    id=\"homeassistant_api\"\n                    icon=\"hassio:home-assistant\"\n                    label=\"hass\"\n                    description=\"\"\n                  ></ha-label-badge>\n                "]);

  _templateObject15 = function _templateObject15() {
    return data;
  };

  return data;
}

function _templateObject14() {
  var data = hassio_addon_info_taggedTemplateLiteral(["\n                  <ha-label-badge\n                    @click=", "\n                    id=\"full_access\"\n                    icon=\"hassio:chip\"\n                    label=\"hardware\"\n                    description=\"\"\n                  ></ha-label-badge>\n                "]);

  _templateObject14 = function _templateObject14() {
    return data;
  };

  return data;
}

function _templateObject13() {
  var data = hassio_addon_info_taggedTemplateLiteral(["\n                  <ha-label-badge\n                    @click=", "\n                    id=\"host_network\"\n                    icon=\"hassio:network\"\n                    label=\"host\"\n                    description=\"\"\n                  ></ha-label-badge>\n                "]);

  _templateObject13 = function _templateObject13() {
    return data;
  };

  return data;
}

function _templateObject12() {
  var data = hassio_addon_info_taggedTemplateLiteral(["\n                <img\n                  class=\"logo\"\n                  src=\"/api/hassio/addons/", "/logo\"\n                />\n              "]);

  _templateObject12 = function _templateObject12() {
    return data;
  };

  return data;
}

function _templateObject11() {
  var data = hassio_addon_info_taggedTemplateLiteral(["<span class=\"changelog-link\" @click=", "\n                  >Changelog</span\n                >"]);

  _templateObject11 = function _templateObject11() {
    return data;
  };

  return data;
}

function _templateObject10() {
  var data = hassio_addon_info_taggedTemplateLiteral(["\n                  Current version: ", "\n                  <div class=\"changelog\" @click=", ">\n                    (<span class=\"changelog-link\">changelog</span>)\n                  </div>\n                "]);

  _templateObject10 = function _templateObject10() {
    return data;
  };

  return data;
}

function _templateObject9() {
  var data = hassio_addon_info_taggedTemplateLiteral([" ", " "]);

  _templateObject9 = function _templateObject9() {
    return data;
  };

  return data;
}

function _templateObject8() {
  var data = hassio_addon_info_taggedTemplateLiteral(["\n                          <ha-icon\n                            title=\"Add-on is stopped\"\n                            class=\"stopped\"\n                            icon=\"hassio:circle\"\n                          ></ha-icon>\n                        "]);

  _templateObject8 = function _templateObject8() {
    return data;
  };

  return data;
}

function _templateObject7() {
  var data = hassio_addon_info_taggedTemplateLiteral(["\n                          <ha-icon\n                            title=\"Add-on is running\"\n                            class=\"running\"\n                            icon=\"hassio:circle\"\n                          ></ha-icon>\n                        "]);

  _templateObject7 = function _templateObject7() {
    return data;
  };

  return data;
}

function hassio_addon_info_templateObject6() {
  var data = hassio_addon_info_taggedTemplateLiteral(["\n                    ", "\n                  "]);

  hassio_addon_info_templateObject6 = function _templateObject6() {
    return data;
  };

  return data;
}

function hassio_addon_info_templateObject5() {
  var data = hassio_addon_info_taggedTemplateLiteral(["\n        <paper-card heading=\"Warning: Protection mode is disabled!\" class=\"warning\">\n          <div class=\"card-content\">\n            Protection mode on this add-on is disabled! This gives the add-on full access to the entire system, which adds security risks, and could damage your system when used incorrectly. Only disable the protection mode if you know, need AND trust the source of this add-on.\n          </div>\n          <div class=\"card-actions protection-enable\">\n              <mwc-button @click=", ">Enable Protection mode</mwc-button>\n            </div>\n          </div>\n        </paper-card>\n      "]);

  hassio_addon_info_templateObject5 = function _templateObject5() {
    return data;
  };

  return data;
}

function hassio_addon_info_templateObject4() {
  var data = hassio_addon_info_taggedTemplateLiteral(["\n                      <mwc-button @click=", ">\n                        Changelog\n                      </mwc-button>\n                    "]);

  hassio_addon_info_templateObject4 = function _templateObject4() {
    return data;
  };

  return data;
}

function hassio_addon_info_templateObject3() {
  var data = hassio_addon_info_taggedTemplateLiteral(["\n                      <p>\n                        This update is no longer compatible with your system.\n                      </p>\n                    "]);

  hassio_addon_info_templateObject3 = function _templateObject3() {
    return data;
  };

  return data;
}

function hassio_addon_info_templateObject2() {
  var data = hassio_addon_info_taggedTemplateLiteral(["\n            <paper-card heading=\"Update available! \uD83C\uDF89\">\n              <div class=\"card-content\">\n                <hassio-card-content\n                  .hass=", "\n                  .title=\"", " ", " is available\"\n                  .description=\"You are currently running version ", "\"\n                  icon=\"hassio:arrow-up-bold-circle\"\n                  iconClass=\"update\"\n                ></hassio-card-content>\n                ", "\n              </div>\n              <div class=\"card-actions\">\n                <ha-call-api-button\n                  .hass=", "\n                  .disabled=", "\n                  path=\"hassio/addons/", "/update\"\n                >\n                  Update\n                </ha-call-api-button>\n                ", "\n              </div>\n            </paper-card>\n          "]);

  hassio_addon_info_templateObject2 = function _templateObject2() {
    return data;
  };

  return data;
}

function hassio_addon_info_templateObject() {
  var data = hassio_addon_info_taggedTemplateLiteral(["\n      ", "\n      ", "\n\n      <paper-card>\n        <div class=\"card-content\">\n          <div class=\"addon-header\">\n            ", "\n            <div class=\"addon-version light-color\">\n              ", "\n            </div>\n          </div>\n          <div class=\"description light-color\">\n            ", "\n          </div>\n\n          <div class=\"description light-color\">\n            ", ".<br />\n            Visit\n            <a href=\"", "\" target=\"_blank\" rel=\"noreferrer\">\n              ", " page</a\n            >\n            for details.\n          </div>\n          ", "\n          <div class=\"security\">\n            <ha-label-badge\n              class=", "\n              @click=", "\n              id=\"stage\"\n              .icon=", "\n              label=\"stage\"\n              description=\"\"\n            ></ha-label-badge>\n            <ha-label-badge\n              class=", "\n              @click=", "\n              id=\"rating\"\n              .value=", "\n              label=\"rating\"\n              description=\"\"\n            ></ha-label-badge>\n            ", "\n            ", "\n            ", "\n            ", "\n            ", "\n            ", "\n            ", "\n            ", "\n            ", "\n          </div>\n\n          ", "\n          ", "\n        </div>\n        <div class=\"card-actions\">\n          ", "\n        </div>\n      </paper-card>\n\n      ", "\n    "]);

  hassio_addon_info_templateObject = function _templateObject() {
    return data;
  };

  return data;
}

function hassio_addon_info_taggedTemplateLiteral(strings, raw) { if (!raw) { raw = strings.slice(0); } return Object.freeze(Object.defineProperties(strings, { raw: { value: Object.freeze(raw) } })); }

function hassio_addon_info_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function hassio_addon_info_inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) hassio_addon_info_setPrototypeOf(subClass, superClass); }

function hassio_addon_info_setPrototypeOf(o, p) { hassio_addon_info_setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return hassio_addon_info_setPrototypeOf(o, p); }

function hassio_addon_info_createSuper(Derived) { return function () { var Super = hassio_addon_info_getPrototypeOf(Derived), result; if (hassio_addon_info_isNativeReflectConstruct()) { var NewTarget = hassio_addon_info_getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return hassio_addon_info_possibleConstructorReturn(this, result); }; }

function hassio_addon_info_possibleConstructorReturn(self, call) { if (call && (hassio_addon_info_typeof(call) === "object" || typeof call === "function")) { return call; } return hassio_addon_info_assertThisInitialized(self); }

function hassio_addon_info_assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function hassio_addon_info_isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Date.prototype.toString.call(Reflect.construct(Date, [], function () {})); return true; } catch (e) { return false; } }

function hassio_addon_info_getPrototypeOf(o) { hassio_addon_info_getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return hassio_addon_info_getPrototypeOf(o); }

function hassio_addon_info_decorate(decorators, factory, superClass, mixins) { var api = hassio_addon_info_getDecoratorsApi(); if (mixins) { for (var i = 0; i < mixins.length; i++) { api = mixins[i](api); } } var r = factory(function initialize(O) { api.initializeInstanceElements(O, decorated.elements); }, superClass); var decorated = api.decorateClass(hassio_addon_info_coalesceClassElements(r.d.map(hassio_addon_info_createElementDescriptor)), decorators); api.initializeClassElements(r.F, decorated.elements); return api.runClassFinishers(r.F, decorated.finishers); }

function hassio_addon_info_getDecoratorsApi() { hassio_addon_info_getDecoratorsApi = function _getDecoratorsApi() { return api; }; var api = { elementsDefinitionOrder: [["method"], ["field"]], initializeInstanceElements: function initializeInstanceElements(O, elements) { ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { if (element.kind === kind && element.placement === "own") { this.defineClassElement(O, element); } }, this); }, this); }, initializeClassElements: function initializeClassElements(F, elements) { var proto = F.prototype; ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { var placement = element.placement; if (element.kind === kind && (placement === "static" || placement === "prototype")) { var receiver = placement === "static" ? F : proto; this.defineClassElement(receiver, element); } }, this); }, this); }, defineClassElement: function defineClassElement(receiver, element) { var descriptor = element.descriptor; if (element.kind === "field") { var initializer = element.initializer; descriptor = { enumerable: descriptor.enumerable, writable: descriptor.writable, configurable: descriptor.configurable, value: initializer === void 0 ? void 0 : initializer.call(receiver) }; } Object.defineProperty(receiver, element.key, descriptor); }, decorateClass: function decorateClass(elements, decorators) { var newElements = []; var finishers = []; var placements = { "static": [], prototype: [], own: [] }; elements.forEach(function (element) { this.addElementPlacement(element, placements); }, this); elements.forEach(function (element) { if (!hassio_addon_info_hasDecorators(element)) return newElements.push(element); var elementFinishersExtras = this.decorateElement(element, placements); newElements.push(elementFinishersExtras.element); newElements.push.apply(newElements, elementFinishersExtras.extras); finishers.push.apply(finishers, elementFinishersExtras.finishers); }, this); if (!decorators) { return { elements: newElements, finishers: finishers }; } var result = this.decorateConstructor(newElements, decorators); finishers.push.apply(finishers, result.finishers); result.finishers = finishers; return result; }, addElementPlacement: function addElementPlacement(element, placements, silent) { var keys = placements[element.placement]; if (!silent && keys.indexOf(element.key) !== -1) { throw new TypeError("Duplicated element (" + element.key + ")"); } keys.push(element.key); }, decorateElement: function decorateElement(element, placements) { var extras = []; var finishers = []; for (var decorators = element.decorators, i = decorators.length - 1; i >= 0; i--) { var keys = placements[element.placement]; keys.splice(keys.indexOf(element.key), 1); var elementObject = this.fromElementDescriptor(element); var elementFinisherExtras = this.toElementFinisherExtras((0, decorators[i])(elementObject) || elementObject); element = elementFinisherExtras.element; this.addElementPlacement(element, placements); if (elementFinisherExtras.finisher) { finishers.push(elementFinisherExtras.finisher); } var newExtras = elementFinisherExtras.extras; if (newExtras) { for (var j = 0; j < newExtras.length; j++) { this.addElementPlacement(newExtras[j], placements); } extras.push.apply(extras, newExtras); } } return { element: element, finishers: finishers, extras: extras }; }, decorateConstructor: function decorateConstructor(elements, decorators) { var finishers = []; for (var i = decorators.length - 1; i >= 0; i--) { var obj = this.fromClassDescriptor(elements); var elementsAndFinisher = this.toClassDescriptor((0, decorators[i])(obj) || obj); if (elementsAndFinisher.finisher !== undefined) { finishers.push(elementsAndFinisher.finisher); } if (elementsAndFinisher.elements !== undefined) { elements = elementsAndFinisher.elements; for (var j = 0; j < elements.length - 1; j++) { for (var k = j + 1; k < elements.length; k++) { if (elements[j].key === elements[k].key && elements[j].placement === elements[k].placement) { throw new TypeError("Duplicated element (" + elements[j].key + ")"); } } } } } return { elements: elements, finishers: finishers }; }, fromElementDescriptor: function fromElementDescriptor(element) { var obj = { kind: element.kind, key: element.key, placement: element.placement, descriptor: element.descriptor }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); if (element.kind === "field") obj.initializer = element.initializer; return obj; }, toElementDescriptors: function toElementDescriptors(elementObjects) { if (elementObjects === undefined) return; return hassio_addon_info_toArray(elementObjects).map(function (elementObject) { var element = this.toElementDescriptor(elementObject); this.disallowProperty(elementObject, "finisher", "An element descriptor"); this.disallowProperty(elementObject, "extras", "An element descriptor"); return element; }, this); }, toElementDescriptor: function toElementDescriptor(elementObject) { var kind = String(elementObject.kind); if (kind !== "method" && kind !== "field") { throw new TypeError('An element descriptor\'s .kind property must be either "method" or' + ' "field", but a decorator created an element descriptor with' + ' .kind "' + kind + '"'); } var key = hassio_addon_info_toPropertyKey(elementObject.key); var placement = String(elementObject.placement); if (placement !== "static" && placement !== "prototype" && placement !== "own") { throw new TypeError('An element descriptor\'s .placement property must be one of "static",' + ' "prototype" or "own", but a decorator created an element descriptor' + ' with .placement "' + placement + '"'); } var descriptor = elementObject.descriptor; this.disallowProperty(elementObject, "elements", "An element descriptor"); var element = { kind: kind, key: key, placement: placement, descriptor: Object.assign({}, descriptor) }; if (kind !== "field") { this.disallowProperty(elementObject, "initializer", "A method descriptor"); } else { this.disallowProperty(descriptor, "get", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "set", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "value", "The property descriptor of a field descriptor"); element.initializer = elementObject.initializer; } return element; }, toElementFinisherExtras: function toElementFinisherExtras(elementObject) { var element = this.toElementDescriptor(elementObject); var finisher = hassio_addon_info_optionalCallableProperty(elementObject, "finisher"); var extras = this.toElementDescriptors(elementObject.extras); return { element: element, finisher: finisher, extras: extras }; }, fromClassDescriptor: function fromClassDescriptor(elements) { var obj = { kind: "class", elements: elements.map(this.fromElementDescriptor, this) }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); return obj; }, toClassDescriptor: function toClassDescriptor(obj) { var kind = String(obj.kind); if (kind !== "class") { throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator' + ' created a class descriptor with .kind "' + kind + '"'); } this.disallowProperty(obj, "key", "A class descriptor"); this.disallowProperty(obj, "placement", "A class descriptor"); this.disallowProperty(obj, "descriptor", "A class descriptor"); this.disallowProperty(obj, "initializer", "A class descriptor"); this.disallowProperty(obj, "extras", "A class descriptor"); var finisher = hassio_addon_info_optionalCallableProperty(obj, "finisher"); var elements = this.toElementDescriptors(obj.elements); return { elements: elements, finisher: finisher }; }, runClassFinishers: function runClassFinishers(constructor, finishers) { for (var i = 0; i < finishers.length; i++) { var newConstructor = (0, finishers[i])(constructor); if (newConstructor !== undefined) { if (typeof newConstructor !== "function") { throw new TypeError("Finishers must return a constructor."); } constructor = newConstructor; } } return constructor; }, disallowProperty: function disallowProperty(obj, name, objectType) { if (obj[name] !== undefined) { throw new TypeError(objectType + " can't have a ." + name + " property."); } } }; return api; }

function hassio_addon_info_createElementDescriptor(def) { var key = hassio_addon_info_toPropertyKey(def.key); var descriptor; if (def.kind === "method") { descriptor = { value: def.value, writable: true, configurable: true, enumerable: false }; } else if (def.kind === "get") { descriptor = { get: def.value, configurable: true, enumerable: false }; } else if (def.kind === "set") { descriptor = { set: def.value, configurable: true, enumerable: false }; } else if (def.kind === "field") { descriptor = { configurable: true, writable: true, enumerable: true }; } var element = { kind: def.kind === "field" ? "field" : "method", key: key, placement: def["static"] ? "static" : def.kind === "field" ? "own" : "prototype", descriptor: descriptor }; if (def.decorators) element.decorators = def.decorators; if (def.kind === "field") element.initializer = def.value; return element; }

function hassio_addon_info_coalesceGetterSetter(element, other) { if (element.descriptor.get !== undefined) { other.descriptor.get = element.descriptor.get; } else { other.descriptor.set = element.descriptor.set; } }

function hassio_addon_info_coalesceClassElements(elements) { var newElements = []; var isSameElement = function isSameElement(other) { return other.kind === "method" && other.key === element.key && other.placement === element.placement; }; for (var i = 0; i < elements.length; i++) { var element = elements[i]; var other; if (element.kind === "method" && (other = newElements.find(isSameElement))) { if (hassio_addon_info_isDataDescriptor(element.descriptor) || hassio_addon_info_isDataDescriptor(other.descriptor)) { if (hassio_addon_info_hasDecorators(element) || hassio_addon_info_hasDecorators(other)) { throw new ReferenceError("Duplicated methods (" + element.key + ") can't be decorated."); } other.descriptor = element.descriptor; } else { if (hassio_addon_info_hasDecorators(element)) { if (hassio_addon_info_hasDecorators(other)) { throw new ReferenceError("Decorators can't be placed on different accessors with for " + "the same property (" + element.key + ")."); } other.decorators = element.decorators; } hassio_addon_info_coalesceGetterSetter(element, other); } } else { newElements.push(element); } } return newElements; }

function hassio_addon_info_hasDecorators(element) { return element.decorators && element.decorators.length; }

function hassio_addon_info_isDataDescriptor(desc) { return desc !== undefined && !(desc.value === undefined && desc.writable === undefined); }

function hassio_addon_info_optionalCallableProperty(obj, name) { var value = obj[name]; if (value !== undefined && typeof value !== "function") { throw new TypeError("Expected '" + name + "' to be a function"); } return value; }

function hassio_addon_info_toPropertyKey(arg) { var key = hassio_addon_info_toPrimitive(arg, "string"); return hassio_addon_info_typeof(key) === "symbol" ? key : String(key); }

function hassio_addon_info_toPrimitive(input, hint) { if (hassio_addon_info_typeof(input) !== "object" || input === null) return input; var prim = input[Symbol.toPrimitive]; if (prim !== undefined) { var res = prim.call(input, hint || "default"); if (hassio_addon_info_typeof(res) !== "object") return res; throw new TypeError("@@toPrimitive must return a primitive value."); } return (hint === "string" ? String : Number)(input); }

function hassio_addon_info_toArray(arr) { return hassio_addon_info_arrayWithHoles(arr) || hassio_addon_info_iterableToArray(arr) || hassio_addon_info_unsupportedIterableToArray(arr) || hassio_addon_info_nonIterableRest(); }

function hassio_addon_info_nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function hassio_addon_info_unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return hassio_addon_info_arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(n); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return hassio_addon_info_arrayLikeToArray(o, minLen); }

function hassio_addon_info_arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function hassio_addon_info_iterableToArray(iter) { if (typeof Symbol !== "undefined" && Symbol.iterator in Object(iter)) return Array.from(iter); }

function hassio_addon_info_arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }





















var STAGE_ICON = {
  stable: "mdi:check-circle",
  experimental: "mdi:flask",
  deprecated: "mdi:exclamation-thick"
};
var PERMIS_DESC = {
  stage: {
    title: "Add-on Stage",
    description: "Add-ons can have one of three stages:\n\n<ha-icon icon='".concat(STAGE_ICON.stable, "'></ha-icon>**Stable**: These are add-ons ready to be used in production.\n<ha-icon icon='").concat(STAGE_ICON.experimental, "'></ha-icon>**Experimental**: These may contain bugs, and may be unfinished.\n<ha-icon icon='").concat(STAGE_ICON.deprecated, "'></ha-icon>**Deprecated**: These add-ons will no longer receive any updates.")
  },
  rating: {
    title: "Add-on Security Rating",
    description: "Home Assistant provides a security rating to each of the add-ons, which indicates the risks involved when using this add-on. The more access an add-on requires on your system, the lower the score, thus raising the possible security risks.\n\nA score is on a scale from 1 to 6. Where 1 is the lowest score (considered the most insecure and highest risk) and a score of 6 is the highest score (considered the most secure and lowest risk)."
  },
  host_network: {
    title: "Host Network",
    description: "Add-ons usually run in their own isolated network layer, which prevents them from accessing the network of the host operating system. In some cases, this network isolation can limit add-ons in providing their services and therefore, the isolation can be lifted by the add-on author, giving the add-on full access to the network capabilities of the host machine. This gives the add-on more networking capabilities but lowers the security, hence, the security rating of the add-on will be lowered when this option is used by the add-on."
  },
  homeassistant_api: {
    title: "Home Assistant API Access",
    description: "This add-on is allowed to access your running Home Assistant instance directly via the Home Assistant API. This mode handles authentication for the add-on as well, which enables an add-on to interact with Home Assistant without the need for additional authentication tokens."
  },
  full_access: {
    title: "Full Hardware Access",
    description: "This add-on is given full access to the hardware of your system, by request of the add-on author. Access is comparable to the privileged mode in Docker. Since this opens up possible security risks, this feature impacts the add-on security score negatively.\n\nThis level of access is not granted automatically and needs to be confirmed by you. To do this, you need to disable the protection mode on the add-on manually. Only disable the protection mode if you know, need AND trust the source of this add-on."
  },
  hassio_api: {
    title: "Supervisor API Access",
    description: "The add-on was given access to the Supervisor API, by request of the add-on author. By default, the add-on can access general version information of your system. When the add-on requests 'manager' or 'admin' level access to the API, it will gain access to control multiple parts of your Home Assistant system. This permission is indicated by this badge and will impact the security score of the addon negatively."
  },
  docker_api: {
    title: "Full Docker Access",
    description: "The add-on author has requested the add-on to have management access to the Docker instance running on your system. This mode gives the add-on full access and control to your entire Home Assistant system, which adds security risks, and could damage your system when misused. Therefore, this feature impacts the add-on security score negatively.\n\nThis level of access is not granted automatically and needs to be confirmed by you. To do this, you need to disable the protection mode on the add-on manually. Only disable the protection mode if you know, need AND trust the source of this add-on."
  },
  host_pid: {
    title: "Host Processes Namespace",
    description: "Usually, the processes the add-on runs, are isolated from all other system processes. The add-on author has requested the add-on to have access to the system processes running on the host system instance, and allow the add-on to spawn processes on the host system as well. This mode gives the add-on full access and control to your entire Home Assistant system, which adds security risks, and could damage your system when misused. Therefore, this feature impacts the add-on security score negatively.\n\nThis level of access is not granted automatically and needs to be confirmed by you. To do this, you need to disable the protection mode on the add-on manually. Only disable the protection mode if you know, need AND trust the source of this add-on."
  },
  apparmor: {
    title: "AppArmor",
    description: "AppArmor ('Application Armor') is a Linux kernel security module that restricts add-ons capabilities like network access, raw socket access, and permission to read, write, or execute specific files.\n\nAdd-on authors can provide their security profiles, optimized for the add-on, or request it to be disabled. If AppArmor is disabled, it will raise security risks and therefore, has a negative impact on the security score of the add-on."
  },
  auth_api: {
    title: "Home Assistant Authentication",
    description: "An add-on can authenticate users against Home Assistant, allowing add-ons to give users the possibility to log into applications running inside add-ons, using their Home Assistant username/password. This badge indicates if the add-on author requests this capability."
  },
  ingress: {
    title: "Ingress",
    description: "This add-on is using Ingress to embed its interface securely into Home Assistant."
  }
};

var hassio_addon_info_HassioAddonInfo = hassio_addon_info_decorate([Object(lit_element["d" /* customElement */])("hassio-addon-info")], function (_initialize, _LitElement) {
  var HassioAddonInfo = /*#__PURE__*/function (_LitElement2) {
    hassio_addon_info_inherits(HassioAddonInfo, _LitElement2);

    var _super = hassio_addon_info_createSuper(HassioAddonInfo);

    function HassioAddonInfo() {
      var _this;

      hassio_addon_info_classCallCheck(this, HassioAddonInfo);

      for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
        args[_key] = arguments[_key];
      }

      _this = _super.call.apply(_super, [this].concat(args));

      _initialize(hassio_addon_info_assertThisInitialized(_this));

      return _this;
    }

    return HassioAddonInfo;
  }(_LitElement);

  return {
    F: HassioAddonInfo,
    d: [{
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
      key: "hass",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])({
        attribute: false
      })],
      key: "addon",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "_error",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])({
        type: Boolean
      })],
      key: "_installing",
      value: function value() {
        return false;
      }
    }, {
      kind: "method",
      key: "render",
      value: function render() {
        var _this$hass$userData;

        return Object(lit_element["e" /* html */])(hassio_addon_info_templateObject(), this._computeUpdateAvailable ? Object(lit_element["e" /* html */])(hassio_addon_info_templateObject2(), this.hass, this.addon.name, this.addon.version_latest, this.addon.version, !this.addon.available ? Object(lit_element["e" /* html */])(hassio_addon_info_templateObject3()) : "", this.hass, !this.addon.available, this.addon.slug, this.addon.changelog ? Object(lit_element["e" /* html */])(hassio_addon_info_templateObject4(), this._openChangelog) : "") : "", !this.addon["protected"] ? Object(lit_element["e" /* html */])(hassio_addon_info_templateObject5(), this._protectionToggled) : "", !this.narrow ? this.addon.name : "", this.addon.version ? Object(lit_element["e" /* html */])(hassio_addon_info_templateObject6(), this._computeIsRunning ? Object(lit_element["e" /* html */])(_templateObject7()) : Object(lit_element["e" /* html */])(_templateObject8())) : Object(lit_element["e" /* html */])(_templateObject9(), this.addon.version_latest), this.addon.version ? Object(lit_element["e" /* html */])(_templateObject10(), this.addon.version, this._openChangelog) : Object(lit_element["e" /* html */])(_templateObject11(), this._openChangelog), this.addon.description, this.addon.url, this.addon.name, this.addon.logo ? Object(lit_element["e" /* html */])(_templateObject12(), this.addon.slug) : "", Object(class_map["a" /* classMap */])({
          green: this.addon.stage === "stable",
          yellow: this.addon.stage === "experimental",
          red: this.addon.stage === "deprecated"
        }), this._showMoreInfo, STAGE_ICON[this.addon.stage], Object(class_map["a" /* classMap */])({
          green: [5, 6].includes(Number(this.addon.rating)),
          yellow: [3, 4].includes(Number(this.addon.rating)),
          red: [1, 2].includes(Number(this.addon.rating))
        }), this._showMoreInfo, this.addon.rating, this.addon.host_network ? Object(lit_element["e" /* html */])(_templateObject13(), this._showMoreInfo) : "", this.addon.full_access ? Object(lit_element["e" /* html */])(_templateObject14(), this._showMoreInfo) : "", this.addon.homeassistant_api ? Object(lit_element["e" /* html */])(_templateObject15(), this._showMoreInfo) : "", this._computeHassioApi ? Object(lit_element["e" /* html */])(_templateObject16(), this._showMoreInfo, this.addon.hassio_role) : "", this.addon.docker_api ? Object(lit_element["e" /* html */])(_templateObject17(), this._showMoreInfo) : "", this.addon.host_pid ? Object(lit_element["e" /* html */])(_templateObject18(), this._showMoreInfo) : "", this.addon.apparmor ? Object(lit_element["e" /* html */])(_templateObject19(), this._showMoreInfo, this._computeApparmorClassName) : "", this.addon.auth_api ? Object(lit_element["e" /* html */])(_templateObject20(), this._showMoreInfo) : "", this.addon.ingress ? Object(lit_element["e" /* html */])(_templateObject21(), this._showMoreInfo) : "", this.addon.version ? Object(lit_element["e" /* html */])(_templateObject22(), this._startOnBootToggled, this.addon.boot === "auto", this.addon.auto_update || ((_this$hass$userData = this.hass.userData) === null || _this$hass$userData === void 0 ? void 0 : _this$hass$userData.showAdvanced) ? Object(lit_element["e" /* html */])(_templateObject23(), this._autoUpdateToggled, this.addon.auto_update) : "", this.addon.ingress ? Object(lit_element["e" /* html */])(_templateObject24(), this._panelToggled, this.addon.ingress_panel, this._computeCannotIngressSidebar, this._computeCannotIngressSidebar ? Object(lit_element["e" /* html */])(_templateObject25()) : "") : "", this._computeUsesProtectedOptions ? Object(lit_element["e" /* html */])(_templateObject26(), this._protectionToggled, this.addon["protected"]) : "") : "", this._error ? Object(lit_element["e" /* html */])(_templateObject27(), this._error) : "", this.addon.version ? Object(lit_element["e" /* html */])(_templateObject28(), this._computeIsRunning ? Object(lit_element["e" /* html */])(_templateObject29(), this.hass, this.addon.slug, this.hass, this.addon.slug) : Object(lit_element["e" /* html */])(_templateObject30(), this.hass, this.addon.slug), this._computeShowWebUI ? Object(lit_element["e" /* html */])(_templateObject31(), this._pathWebui) : "", this._computeShowIngressUI ? Object(lit_element["e" /* html */])(_templateObject32(), this._openIngress) : "", this._uninstallClicked, this.addon.build ? Object(lit_element["e" /* html */])(_templateObject33(), this.hass, this.addon.slug) : "") : Object(lit_element["e" /* html */])(_templateObject34(), !this.addon.available ? Object(lit_element["e" /* html */])(_templateObject35()) : "", !this.addon.available || this._installing, this._installing, this._installClicked), this.addon.long_description ? Object(lit_element["e" /* html */])(_templateObject36(), this.addon.long_description) : "");
      }
    }, {
      kind: "get",
      "static": true,
      key: "styles",
      value: function styles() {
        return [resources_styles["b" /* haStyle */], hassio_style["a" /* hassioStyle */], Object(lit_element["c" /* css */])(_templateObject37())];
      }
    }, {
      kind: "get",
      key: "_computeHassioApi",
      value: function _computeHassioApi() {
        return this.addon.hassio_api && (this.addon.hassio_role === "manager" || this.addon.hassio_role === "admin");
      }
    }, {
      kind: "get",
      key: "_computeApparmorClassName",
      value: function _computeApparmorClassName() {
        if (this.addon.apparmor === "profile") {
          return "green";
        }

        if (this.addon.apparmor === "disable") {
          return "red";
        }

        return "";
      }
    }, {
      kind: "method",
      key: "_showMoreInfo",
      value: function _showMoreInfo(ev) {
        var id = ev.target.getAttribute("id");
        Object(show_dialog_hassio_markdown["a" /* showHassioMarkdownDialog */])(this, {
          title: PERMIS_DESC[id].title,
          content: PERMIS_DESC[id].description
        });
      }
    }, {
      kind: "get",
      key: "_computeIsRunning",
      value: function _computeIsRunning() {
        var _this$addon;

        return ((_this$addon = this.addon) === null || _this$addon === void 0 ? void 0 : _this$addon.state) === "started";
      }
    }, {
      kind: "get",
      key: "_computeUpdateAvailable",
      value: function _computeUpdateAvailable() {
        return this.addon && !this.addon.detached && this.addon.version && this.addon.version !== this.addon.version_latest;
      }
    }, {
      kind: "get",
      key: "_pathWebui",
      value: function _pathWebui() {
        return this.addon.webui && this.addon.webui.replace("[HOST]", document.location.hostname);
      }
    }, {
      kind: "get",
      key: "_computeShowWebUI",
      value: function _computeShowWebUI() {
        return !this.addon.ingress && this.addon.webui && this._computeIsRunning;
      }
    }, {
      kind: "method",
      key: "_openIngress",
      value: function _openIngress() {
        Object(common_navigate["a" /* navigate */])(this, "/hassio/ingress/".concat(this.addon.slug));
      }
    }, {
      kind: "get",
      key: "_computeShowIngressUI",
      value: function _computeShowIngressUI() {
        return this.addon.ingress && this._computeIsRunning;
      }
    }, {
      kind: "get",
      key: "_computeCannotIngressSidebar",
      value: function _computeCannotIngressSidebar() {
        return !this.addon.ingress || !Object(version["a" /* atLeastVersion */])(this.hass.config.version, 0, 92);
      }
    }, {
      kind: "get",
      key: "_computeUsesProtectedOptions",
      value: function _computeUsesProtectedOptions() {
        return this.addon.docker_api || this.addon.full_access || this.addon.host_pid;
      }
    }, {
      kind: "method",
      key: "_startOnBootToggled",
      value: function () {
        var _startOnBootToggled2 = hassio_addon_info_asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee() {
          var data, eventdata, _err$body;

          return regeneratorRuntime.wrap(function _callee$(_context) {
            while (1) {
              switch (_context.prev = _context.next) {
                case 0:
                  this._error = undefined;
                  data = {
                    boot: this.addon.boot === "auto" ? "manual" : "auto"
                  };
                  _context.prev = 2;
                  _context.next = 5;
                  return Object(hassio_addon["i" /* setHassioAddonOption */])(this.hass, this.addon.slug, data);

                case 5:
                  eventdata = {
                    success: true,
                    response: undefined,
                    path: "option"
                  };
                  Object(fire_event["a" /* fireEvent */])(this, "hass-api-called", eventdata);
                  _context.next = 12;
                  break;

                case 9:
                  _context.prev = 9;
                  _context.t0 = _context["catch"](2);
                  this._error = "Failed to set addon option, ".concat(((_err$body = _context.t0.body) === null || _err$body === void 0 ? void 0 : _err$body.message) || _context.t0);

                case 12:
                case "end":
                  return _context.stop();
              }
            }
          }, _callee, this, [[2, 9]]);
        }));

        function _startOnBootToggled() {
          return _startOnBootToggled2.apply(this, arguments);
        }

        return _startOnBootToggled;
      }()
    }, {
      kind: "method",
      key: "_autoUpdateToggled",
      value: function () {
        var _autoUpdateToggled2 = hassio_addon_info_asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee2() {
          var data, eventdata, _err$body2;

          return regeneratorRuntime.wrap(function _callee2$(_context2) {
            while (1) {
              switch (_context2.prev = _context2.next) {
                case 0:
                  this._error = undefined;
                  data = {
                    auto_update: !this.addon.auto_update
                  };
                  _context2.prev = 2;
                  _context2.next = 5;
                  return Object(hassio_addon["i" /* setHassioAddonOption */])(this.hass, this.addon.slug, data);

                case 5:
                  eventdata = {
                    success: true,
                    response: undefined,
                    path: "option"
                  };
                  Object(fire_event["a" /* fireEvent */])(this, "hass-api-called", eventdata);
                  _context2.next = 12;
                  break;

                case 9:
                  _context2.prev = 9;
                  _context2.t0 = _context2["catch"](2);
                  this._error = "Failed to set addon option, ".concat(((_err$body2 = _context2.t0.body) === null || _err$body2 === void 0 ? void 0 : _err$body2.message) || _context2.t0);

                case 12:
                case "end":
                  return _context2.stop();
              }
            }
          }, _callee2, this, [[2, 9]]);
        }));

        function _autoUpdateToggled() {
          return _autoUpdateToggled2.apply(this, arguments);
        }

        return _autoUpdateToggled;
      }()
    }, {
      kind: "method",
      key: "_protectionToggled",
      value: function () {
        var _protectionToggled2 = hassio_addon_info_asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee3() {
          var data, eventdata, _err$body3;

          return regeneratorRuntime.wrap(function _callee3$(_context3) {
            while (1) {
              switch (_context3.prev = _context3.next) {
                case 0:
                  this._error = undefined;
                  data = {
                    "protected": !this.addon["protected"]
                  };
                  _context3.prev = 2;
                  _context3.next = 5;
                  return Object(hassio_addon["j" /* setHassioAddonSecurity */])(this.hass, this.addon.slug, data);

                case 5:
                  eventdata = {
                    success: true,
                    response: undefined,
                    path: "security"
                  };
                  Object(fire_event["a" /* fireEvent */])(this, "hass-api-called", eventdata);
                  _context3.next = 12;
                  break;

                case 9:
                  _context3.prev = 9;
                  _context3.t0 = _context3["catch"](2);
                  this._error = "Failed to set addon security option, ".concat(((_err$body3 = _context3.t0.body) === null || _err$body3 === void 0 ? void 0 : _err$body3.message) || _context3.t0);

                case 12:
                case "end":
                  return _context3.stop();
              }
            }
          }, _callee3, this, [[2, 9]]);
        }));

        function _protectionToggled() {
          return _protectionToggled2.apply(this, arguments);
        }

        return _protectionToggled;
      }()
    }, {
      kind: "method",
      key: "_panelToggled",
      value: function () {
        var _panelToggled2 = hassio_addon_info_asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee4() {
          var data, eventdata, _err$body4;

          return regeneratorRuntime.wrap(function _callee4$(_context4) {
            while (1) {
              switch (_context4.prev = _context4.next) {
                case 0:
                  this._error = undefined;
                  data = {
                    ingress_panel: !this.addon.ingress_panel
                  };
                  _context4.prev = 2;
                  _context4.next = 5;
                  return Object(hassio_addon["i" /* setHassioAddonOption */])(this.hass, this.addon.slug, data);

                case 5:
                  eventdata = {
                    success: true,
                    response: undefined,
                    path: "option"
                  };
                  Object(fire_event["a" /* fireEvent */])(this, "hass-api-called", eventdata);
                  _context4.next = 12;
                  break;

                case 9:
                  _context4.prev = 9;
                  _context4.t0 = _context4["catch"](2);
                  this._error = "Failed to set addon option, ".concat(((_err$body4 = _context4.t0.body) === null || _err$body4 === void 0 ? void 0 : _err$body4.message) || _context4.t0);

                case 12:
                case "end":
                  return _context4.stop();
              }
            }
          }, _callee4, this, [[2, 9]]);
        }));

        function _panelToggled() {
          return _panelToggled2.apply(this, arguments);
        }

        return _panelToggled;
      }()
    }, {
      kind: "method",
      key: "_openChangelog",
      value: function () {
        var _openChangelog2 = hassio_addon_info_asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee5() {
          var content, _err$body5;

          return regeneratorRuntime.wrap(function _callee5$(_context5) {
            while (1) {
              switch (_context5.prev = _context5.next) {
                case 0:
                  this._error = undefined;
                  _context5.prev = 1;
                  _context5.next = 4;
                  return Object(hassio_addon["a" /* fetchHassioAddonChangelog */])(this.hass, this.addon.slug);

                case 4:
                  content = _context5.sent;
                  Object(show_dialog_hassio_markdown["a" /* showHassioMarkdownDialog */])(this, {
                    title: "Changelog",
                    content: content
                  });
                  _context5.next = 11;
                  break;

                case 8:
                  _context5.prev = 8;
                  _context5.t0 = _context5["catch"](1);
                  this._error = "Failed to get addon changelog, ".concat(((_err$body5 = _context5.t0.body) === null || _err$body5 === void 0 ? void 0 : _err$body5.message) || _context5.t0);

                case 11:
                case "end":
                  return _context5.stop();
              }
            }
          }, _callee5, this, [[1, 8]]);
        }));

        function _openChangelog() {
          return _openChangelog2.apply(this, arguments);
        }

        return _openChangelog;
      }()
    }, {
      kind: "method",
      key: "_installClicked",
      value: function () {
        var _installClicked2 = hassio_addon_info_asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee6() {
          var eventdata, _err$body6;

          return regeneratorRuntime.wrap(function _callee6$(_context6) {
            while (1) {
              switch (_context6.prev = _context6.next) {
                case 0:
                  this._error = undefined;
                  this._installing = true;
                  _context6.prev = 2;
                  _context6.next = 5;
                  return Object(hassio_addon["f" /* installHassioAddon */])(this.hass, this.addon.slug);

                case 5:
                  eventdata = {
                    success: true,
                    response: undefined,
                    path: "install"
                  };
                  Object(fire_event["a" /* fireEvent */])(this, "hass-api-called", eventdata);
                  _context6.next = 12;
                  break;

                case 9:
                  _context6.prev = 9;
                  _context6.t0 = _context6["catch"](2);
                  this._error = "Failed to install addon, ".concat(((_err$body6 = _context6.t0.body) === null || _err$body6 === void 0 ? void 0 : _err$body6.message) || _context6.t0);

                case 12:
                  this._installing = false;

                case 13:
                case "end":
                  return _context6.stop();
              }
            }
          }, _callee6, this, [[2, 9]]);
        }));

        function _installClicked() {
          return _installClicked2.apply(this, arguments);
        }

        return _installClicked;
      }()
    }, {
      kind: "method",
      key: "_uninstallClicked",
      value: function () {
        var _uninstallClicked2 = hassio_addon_info_asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee7() {
          var confirmed, eventdata, _err$body7;

          return regeneratorRuntime.wrap(function _callee7$(_context7) {
            while (1) {
              switch (_context7.prev = _context7.next) {
                case 0:
                  _context7.next = 2;
                  return Object(show_dialog_box["b" /* showConfirmationDialog */])(this, {
                    title: this.addon.name,
                    text: "Are you sure you want to uninstall this add-on?",
                    confirmText: "uninstall add-on",
                    dismissText: "no"
                  });

                case 2:
                  confirmed = _context7.sent;

                  if (confirmed) {
                    _context7.next = 5;
                    break;
                  }

                  return _context7.abrupt("return");

                case 5:
                  this._error = undefined;
                  _context7.prev = 6;
                  _context7.next = 9;
                  return Object(hassio_addon["k" /* uninstallHassioAddon */])(this.hass, this.addon.slug);

                case 9:
                  eventdata = {
                    success: true,
                    response: undefined,
                    path: "uninstall"
                  };
                  Object(fire_event["a" /* fireEvent */])(this, "hass-api-called", eventdata);
                  _context7.next = 16;
                  break;

                case 13:
                  _context7.prev = 13;
                  _context7.t0 = _context7["catch"](6);
                  this._error = "Failed to uninstall addon, ".concat(((_err$body7 = _context7.t0.body) === null || _err$body7 === void 0 ? void 0 : _err$body7.message) || _context7.t0);

                case 16:
                case "end":
                  return _context7.stop();
              }
            }
          }, _callee7, this, [[6, 13]]);
        }));

        function _uninstallClicked() {
          return _uninstallClicked2.apply(this, arguments);
        }

        return _uninstallClicked;
      }()
    }]
  };
}, lit_element["a" /* LitElement */]);
// EXTERNAL MODULE: ./hassio/src/components/hassio-ansi-to-html.ts
var hassio_ansi_to_html = __webpack_require__(130);

// CONCATENATED MODULE: ./hassio/src/addon-view/log/hassio-addon-logs.ts
function hassio_addon_logs_typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { hassio_addon_logs_typeof = function _typeof(obj) { return typeof obj; }; } else { hassio_addon_logs_typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return hassio_addon_logs_typeof(obj); }

function hassio_addon_logs_templateObject4() {
  var data = hassio_addon_logs_taggedTemplateLiteral(["\n        :host,\n        paper-card {\n          display: block;\n        }\n        .errors {\n          color: var(--google-red-500);\n          margin-bottom: 16px;\n        }\n      "]);

  hassio_addon_logs_templateObject4 = function _templateObject4() {
    return data;
  };

  return data;
}

function hassio_addon_logs_templateObject3() {
  var data = hassio_addon_logs_taggedTemplateLiteral(["<hassio-ansi-to-html\n                .content=", "\n              ></hassio-ansi-to-html>"]);

  hassio_addon_logs_templateObject3 = function _templateObject3() {
    return data;
  };

  return data;
}

function hassio_addon_logs_templateObject2() {
  var data = hassio_addon_logs_taggedTemplateLiteral([" <div class=\"errors\">", "</div> "]);

  hassio_addon_logs_templateObject2 = function _templateObject2() {
    return data;
  };

  return data;
}

function hassio_addon_logs_templateObject() {
  var data = hassio_addon_logs_taggedTemplateLiteral(["\n      <h1>", "</h1>\n      <paper-card>\n        ", "\n        <div class=\"card-content\">\n          ", "\n        </div>\n        <div class=\"card-actions\">\n          <mwc-button @click=", ">Refresh</mwc-button>\n        </div>\n      </paper-card>\n    "]);

  hassio_addon_logs_templateObject = function _templateObject() {
    return data;
  };

  return data;
}

function hassio_addon_logs_taggedTemplateLiteral(strings, raw) { if (!raw) { raw = strings.slice(0); } return Object.freeze(Object.defineProperties(strings, { raw: { value: Object.freeze(raw) } })); }

function hassio_addon_logs_asyncGeneratorStep(gen, resolve, reject, _next, _throw, key, arg) { try { var info = gen[key](arg); var value = info.value; } catch (error) { reject(error); return; } if (info.done) { resolve(value); } else { Promise.resolve(value).then(_next, _throw); } }

function hassio_addon_logs_asyncToGenerator(fn) { return function () { var self = this, args = arguments; return new Promise(function (resolve, reject) { var gen = fn.apply(self, args); function _next(value) { hassio_addon_logs_asyncGeneratorStep(gen, resolve, reject, _next, _throw, "next", value); } function _throw(err) { hassio_addon_logs_asyncGeneratorStep(gen, resolve, reject, _next, _throw, "throw", err); } _next(undefined); }); }; }

function hassio_addon_logs_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function hassio_addon_logs_inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) hassio_addon_logs_setPrototypeOf(subClass, superClass); }

function hassio_addon_logs_setPrototypeOf(o, p) { hassio_addon_logs_setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return hassio_addon_logs_setPrototypeOf(o, p); }

function hassio_addon_logs_createSuper(Derived) { return function () { var Super = hassio_addon_logs_getPrototypeOf(Derived), result; if (hassio_addon_logs_isNativeReflectConstruct()) { var NewTarget = hassio_addon_logs_getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return hassio_addon_logs_possibleConstructorReturn(this, result); }; }

function hassio_addon_logs_possibleConstructorReturn(self, call) { if (call && (hassio_addon_logs_typeof(call) === "object" || typeof call === "function")) { return call; } return hassio_addon_logs_assertThisInitialized(self); }

function hassio_addon_logs_assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function hassio_addon_logs_isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Date.prototype.toString.call(Reflect.construct(Date, [], function () {})); return true; } catch (e) { return false; } }

function hassio_addon_logs_decorate(decorators, factory, superClass, mixins) { var api = hassio_addon_logs_getDecoratorsApi(); if (mixins) { for (var i = 0; i < mixins.length; i++) { api = mixins[i](api); } } var r = factory(function initialize(O) { api.initializeInstanceElements(O, decorated.elements); }, superClass); var decorated = api.decorateClass(hassio_addon_logs_coalesceClassElements(r.d.map(hassio_addon_logs_createElementDescriptor)), decorators); api.initializeClassElements(r.F, decorated.elements); return api.runClassFinishers(r.F, decorated.finishers); }

function hassio_addon_logs_getDecoratorsApi() { hassio_addon_logs_getDecoratorsApi = function _getDecoratorsApi() { return api; }; var api = { elementsDefinitionOrder: [["method"], ["field"]], initializeInstanceElements: function initializeInstanceElements(O, elements) { ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { if (element.kind === kind && element.placement === "own") { this.defineClassElement(O, element); } }, this); }, this); }, initializeClassElements: function initializeClassElements(F, elements) { var proto = F.prototype; ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { var placement = element.placement; if (element.kind === kind && (placement === "static" || placement === "prototype")) { var receiver = placement === "static" ? F : proto; this.defineClassElement(receiver, element); } }, this); }, this); }, defineClassElement: function defineClassElement(receiver, element) { var descriptor = element.descriptor; if (element.kind === "field") { var initializer = element.initializer; descriptor = { enumerable: descriptor.enumerable, writable: descriptor.writable, configurable: descriptor.configurable, value: initializer === void 0 ? void 0 : initializer.call(receiver) }; } Object.defineProperty(receiver, element.key, descriptor); }, decorateClass: function decorateClass(elements, decorators) { var newElements = []; var finishers = []; var placements = { "static": [], prototype: [], own: [] }; elements.forEach(function (element) { this.addElementPlacement(element, placements); }, this); elements.forEach(function (element) { if (!hassio_addon_logs_hasDecorators(element)) return newElements.push(element); var elementFinishersExtras = this.decorateElement(element, placements); newElements.push(elementFinishersExtras.element); newElements.push.apply(newElements, elementFinishersExtras.extras); finishers.push.apply(finishers, elementFinishersExtras.finishers); }, this); if (!decorators) { return { elements: newElements, finishers: finishers }; } var result = this.decorateConstructor(newElements, decorators); finishers.push.apply(finishers, result.finishers); result.finishers = finishers; return result; }, addElementPlacement: function addElementPlacement(element, placements, silent) { var keys = placements[element.placement]; if (!silent && keys.indexOf(element.key) !== -1) { throw new TypeError("Duplicated element (" + element.key + ")"); } keys.push(element.key); }, decorateElement: function decorateElement(element, placements) { var extras = []; var finishers = []; for (var decorators = element.decorators, i = decorators.length - 1; i >= 0; i--) { var keys = placements[element.placement]; keys.splice(keys.indexOf(element.key), 1); var elementObject = this.fromElementDescriptor(element); var elementFinisherExtras = this.toElementFinisherExtras((0, decorators[i])(elementObject) || elementObject); element = elementFinisherExtras.element; this.addElementPlacement(element, placements); if (elementFinisherExtras.finisher) { finishers.push(elementFinisherExtras.finisher); } var newExtras = elementFinisherExtras.extras; if (newExtras) { for (var j = 0; j < newExtras.length; j++) { this.addElementPlacement(newExtras[j], placements); } extras.push.apply(extras, newExtras); } } return { element: element, finishers: finishers, extras: extras }; }, decorateConstructor: function decorateConstructor(elements, decorators) { var finishers = []; for (var i = decorators.length - 1; i >= 0; i--) { var obj = this.fromClassDescriptor(elements); var elementsAndFinisher = this.toClassDescriptor((0, decorators[i])(obj) || obj); if (elementsAndFinisher.finisher !== undefined) { finishers.push(elementsAndFinisher.finisher); } if (elementsAndFinisher.elements !== undefined) { elements = elementsAndFinisher.elements; for (var j = 0; j < elements.length - 1; j++) { for (var k = j + 1; k < elements.length; k++) { if (elements[j].key === elements[k].key && elements[j].placement === elements[k].placement) { throw new TypeError("Duplicated element (" + elements[j].key + ")"); } } } } } return { elements: elements, finishers: finishers }; }, fromElementDescriptor: function fromElementDescriptor(element) { var obj = { kind: element.kind, key: element.key, placement: element.placement, descriptor: element.descriptor }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); if (element.kind === "field") obj.initializer = element.initializer; return obj; }, toElementDescriptors: function toElementDescriptors(elementObjects) { if (elementObjects === undefined) return; return hassio_addon_logs_toArray(elementObjects).map(function (elementObject) { var element = this.toElementDescriptor(elementObject); this.disallowProperty(elementObject, "finisher", "An element descriptor"); this.disallowProperty(elementObject, "extras", "An element descriptor"); return element; }, this); }, toElementDescriptor: function toElementDescriptor(elementObject) { var kind = String(elementObject.kind); if (kind !== "method" && kind !== "field") { throw new TypeError('An element descriptor\'s .kind property must be either "method" or' + ' "field", but a decorator created an element descriptor with' + ' .kind "' + kind + '"'); } var key = hassio_addon_logs_toPropertyKey(elementObject.key); var placement = String(elementObject.placement); if (placement !== "static" && placement !== "prototype" && placement !== "own") { throw new TypeError('An element descriptor\'s .placement property must be one of "static",' + ' "prototype" or "own", but a decorator created an element descriptor' + ' with .placement "' + placement + '"'); } var descriptor = elementObject.descriptor; this.disallowProperty(elementObject, "elements", "An element descriptor"); var element = { kind: kind, key: key, placement: placement, descriptor: Object.assign({}, descriptor) }; if (kind !== "field") { this.disallowProperty(elementObject, "initializer", "A method descriptor"); } else { this.disallowProperty(descriptor, "get", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "set", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "value", "The property descriptor of a field descriptor"); element.initializer = elementObject.initializer; } return element; }, toElementFinisherExtras: function toElementFinisherExtras(elementObject) { var element = this.toElementDescriptor(elementObject); var finisher = hassio_addon_logs_optionalCallableProperty(elementObject, "finisher"); var extras = this.toElementDescriptors(elementObject.extras); return { element: element, finisher: finisher, extras: extras }; }, fromClassDescriptor: function fromClassDescriptor(elements) { var obj = { kind: "class", elements: elements.map(this.fromElementDescriptor, this) }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); return obj; }, toClassDescriptor: function toClassDescriptor(obj) { var kind = String(obj.kind); if (kind !== "class") { throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator' + ' created a class descriptor with .kind "' + kind + '"'); } this.disallowProperty(obj, "key", "A class descriptor"); this.disallowProperty(obj, "placement", "A class descriptor"); this.disallowProperty(obj, "descriptor", "A class descriptor"); this.disallowProperty(obj, "initializer", "A class descriptor"); this.disallowProperty(obj, "extras", "A class descriptor"); var finisher = hassio_addon_logs_optionalCallableProperty(obj, "finisher"); var elements = this.toElementDescriptors(obj.elements); return { elements: elements, finisher: finisher }; }, runClassFinishers: function runClassFinishers(constructor, finishers) { for (var i = 0; i < finishers.length; i++) { var newConstructor = (0, finishers[i])(constructor); if (newConstructor !== undefined) { if (typeof newConstructor !== "function") { throw new TypeError("Finishers must return a constructor."); } constructor = newConstructor; } } return constructor; }, disallowProperty: function disallowProperty(obj, name, objectType) { if (obj[name] !== undefined) { throw new TypeError(objectType + " can't have a ." + name + " property."); } } }; return api; }

function hassio_addon_logs_createElementDescriptor(def) { var key = hassio_addon_logs_toPropertyKey(def.key); var descriptor; if (def.kind === "method") { descriptor = { value: def.value, writable: true, configurable: true, enumerable: false }; } else if (def.kind === "get") { descriptor = { get: def.value, configurable: true, enumerable: false }; } else if (def.kind === "set") { descriptor = { set: def.value, configurable: true, enumerable: false }; } else if (def.kind === "field") { descriptor = { configurable: true, writable: true, enumerable: true }; } var element = { kind: def.kind === "field" ? "field" : "method", key: key, placement: def["static"] ? "static" : def.kind === "field" ? "own" : "prototype", descriptor: descriptor }; if (def.decorators) element.decorators = def.decorators; if (def.kind === "field") element.initializer = def.value; return element; }

function hassio_addon_logs_coalesceGetterSetter(element, other) { if (element.descriptor.get !== undefined) { other.descriptor.get = element.descriptor.get; } else { other.descriptor.set = element.descriptor.set; } }

function hassio_addon_logs_coalesceClassElements(elements) { var newElements = []; var isSameElement = function isSameElement(other) { return other.kind === "method" && other.key === element.key && other.placement === element.placement; }; for (var i = 0; i < elements.length; i++) { var element = elements[i]; var other; if (element.kind === "method" && (other = newElements.find(isSameElement))) { if (hassio_addon_logs_isDataDescriptor(element.descriptor) || hassio_addon_logs_isDataDescriptor(other.descriptor)) { if (hassio_addon_logs_hasDecorators(element) || hassio_addon_logs_hasDecorators(other)) { throw new ReferenceError("Duplicated methods (" + element.key + ") can't be decorated."); } other.descriptor = element.descriptor; } else { if (hassio_addon_logs_hasDecorators(element)) { if (hassio_addon_logs_hasDecorators(other)) { throw new ReferenceError("Decorators can't be placed on different accessors with for " + "the same property (" + element.key + ")."); } other.decorators = element.decorators; } hassio_addon_logs_coalesceGetterSetter(element, other); } } else { newElements.push(element); } } return newElements; }

function hassio_addon_logs_hasDecorators(element) { return element.decorators && element.decorators.length; }

function hassio_addon_logs_isDataDescriptor(desc) { return desc !== undefined && !(desc.value === undefined && desc.writable === undefined); }

function hassio_addon_logs_optionalCallableProperty(obj, name) { var value = obj[name]; if (value !== undefined && typeof value !== "function") { throw new TypeError("Expected '" + name + "' to be a function"); } return value; }

function hassio_addon_logs_toPropertyKey(arg) { var key = hassio_addon_logs_toPrimitive(arg, "string"); return hassio_addon_logs_typeof(key) === "symbol" ? key : String(key); }

function hassio_addon_logs_toPrimitive(input, hint) { if (hassio_addon_logs_typeof(input) !== "object" || input === null) return input; var prim = input[Symbol.toPrimitive]; if (prim !== undefined) { var res = prim.call(input, hint || "default"); if (hassio_addon_logs_typeof(res) !== "object") return res; throw new TypeError("@@toPrimitive must return a primitive value."); } return (hint === "string" ? String : Number)(input); }

function hassio_addon_logs_toArray(arr) { return hassio_addon_logs_arrayWithHoles(arr) || hassio_addon_logs_iterableToArray(arr) || hassio_addon_logs_unsupportedIterableToArray(arr) || hassio_addon_logs_nonIterableRest(); }

function hassio_addon_logs_nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function hassio_addon_logs_unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return hassio_addon_logs_arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(n); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return hassio_addon_logs_arrayLikeToArray(o, minLen); }

function hassio_addon_logs_arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function hassio_addon_logs_iterableToArray(iter) { if (typeof Symbol !== "undefined" && Symbol.iterator in Object(iter)) return Array.from(iter); }

function hassio_addon_logs_arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }

function hassio_addon_logs_get(target, property, receiver) { if (typeof Reflect !== "undefined" && Reflect.get) { hassio_addon_logs_get = Reflect.get; } else { hassio_addon_logs_get = function _get(target, property, receiver) { var base = hassio_addon_logs_superPropBase(target, property); if (!base) return; var desc = Object.getOwnPropertyDescriptor(base, property); if (desc.get) { return desc.get.call(receiver); } return desc.value; }; } return hassio_addon_logs_get(target, property, receiver || target); }

function hassio_addon_logs_superPropBase(object, property) { while (!Object.prototype.hasOwnProperty.call(object, property)) { object = hassio_addon_logs_getPrototypeOf(object); if (object === null) break; } return object; }

function hassio_addon_logs_getPrototypeOf(o) { hassio_addon_logs_getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return hassio_addon_logs_getPrototypeOf(o); }









var hassio_addon_logs_HassioAddonLogs = hassio_addon_logs_decorate([Object(lit_element["d" /* customElement */])("hassio-addon-logs")], function (_initialize, _LitElement) {
  var HassioAddonLogs = /*#__PURE__*/function (_LitElement2) {
    hassio_addon_logs_inherits(HassioAddonLogs, _LitElement2);

    var _super = hassio_addon_logs_createSuper(HassioAddonLogs);

    function HassioAddonLogs() {
      var _this;

      hassio_addon_logs_classCallCheck(this, HassioAddonLogs);

      for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
        args[_key] = arguments[_key];
      }

      _this = _super.call.apply(_super, [this].concat(args));

      _initialize(hassio_addon_logs_assertThisInitialized(_this));

      return _this;
    }

    return HassioAddonLogs;
  }(_LitElement);

  return {
    F: HassioAddonLogs,
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
      key: "addon",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "_error",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "_content",
      value: void 0
    }, {
      kind: "method",
      key: "connectedCallback",
      value: function () {
        var _connectedCallback = hassio_addon_logs_asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee() {
          return regeneratorRuntime.wrap(function _callee$(_context) {
            while (1) {
              switch (_context.prev = _context.next) {
                case 0:
                  hassio_addon_logs_get(hassio_addon_logs_getPrototypeOf(HassioAddonLogs.prototype), "connectedCallback", this).call(this);

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
        return Object(lit_element["e" /* html */])(hassio_addon_logs_templateObject(), this.addon.name, this._error ? Object(lit_element["e" /* html */])(hassio_addon_logs_templateObject2(), this._error) : "", this._content ? Object(lit_element["e" /* html */])(hassio_addon_logs_templateObject3(), this._content) : "", this._refresh);
      }
    }, {
      kind: "get",
      "static": true,
      key: "styles",
      value: function styles() {
        return [resources_styles["b" /* haStyle */], hassio_style["a" /* hassioStyle */], Object(lit_element["c" /* css */])(hassio_addon_logs_templateObject4())];
      }
    }, {
      kind: "method",
      key: "_loadData",
      value: function () {
        var _loadData2 = hassio_addon_logs_asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee2() {
          var _err$body;

          return regeneratorRuntime.wrap(function _callee2$(_context2) {
            while (1) {
              switch (_context2.prev = _context2.next) {
                case 0:
                  this._error = undefined;
                  _context2.prev = 1;
                  _context2.next = 4;
                  return Object(hassio_addon["d" /* fetchHassioAddonLogs */])(this.hass, this.addon.slug);

                case 4:
                  this._content = _context2.sent;
                  _context2.next = 10;
                  break;

                case 7:
                  _context2.prev = 7;
                  _context2.t0 = _context2["catch"](1);
                  this._error = "Failed to get addon logs, ".concat(((_err$body = _context2.t0.body) === null || _err$body === void 0 ? void 0 : _err$body.message) || _context2.t0);

                case 10:
                case "end":
                  return _context2.stop();
              }
            }
          }, _callee2, this, [[1, 7]]);
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
        var _refresh2 = hassio_addon_logs_asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee3() {
          return regeneratorRuntime.wrap(function _callee3$(_context3) {
            while (1) {
              switch (_context3.prev = _context3.next) {
                case 0:
                  _context3.next = 2;
                  return this._loadData();

                case 2:
                case "end":
                  return _context3.stop();
              }
            }
          }, _callee3, this);
        }));

        function _refresh() {
          return _refresh2.apply(this, arguments);
        }

        return _refresh;
      }()
    }]
  };
}, lit_element["a" /* LitElement */]);
// CONCATENATED MODULE: ./hassio/src/addon-view/config/hassio-addon-network.ts
function hassio_addon_network_typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { hassio_addon_network_typeof = function _typeof(obj) { return typeof obj; }; } else { hassio_addon_network_typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return hassio_addon_network_typeof(obj); }

function hassio_addon_network_asyncGeneratorStep(gen, resolve, reject, _next, _throw, key, arg) { try { var info = gen[key](arg); var value = info.value; } catch (error) { reject(error); return; } if (info.done) { resolve(value); } else { Promise.resolve(value).then(_next, _throw); } }

function hassio_addon_network_asyncToGenerator(fn) { return function () { var self = this, args = arguments; return new Promise(function (resolve, reject) { var gen = fn.apply(self, args); function _next(value) { hassio_addon_network_asyncGeneratorStep(gen, resolve, reject, _next, _throw, "next", value); } function _throw(err) { hassio_addon_network_asyncGeneratorStep(gen, resolve, reject, _next, _throw, "throw", err); } _next(undefined); }); }; }

function hassio_addon_network_templateObject5() {
  var data = hassio_addon_network_taggedTemplateLiteral(["\n        :host {\n          display: block;\n        }\n        paper-card {\n          display: block;\n        }\n        .errors {\n          color: var(--google-red-500);\n          margin-bottom: 16px;\n        }\n        .card-actions {\n          display: flex;\n          justify-content: space-between;\n        }\n      "]);

  hassio_addon_network_templateObject5 = function _templateObject5() {
    return data;
  };

  return data;
}

function hassio_addon_network_templateObject4() {
  var data = hassio_addon_network_taggedTemplateLiteral(["\n                  <tr>\n                    <td>", "</td>\n                    <td>\n                      <paper-input\n                        @value-changed=", "\n                        placeholder=\"disabled\"\n                        .value=", "\n                        .container=", "\n                        no-label-float\n                      ></paper-input>\n                    </td>\n                    <td>", "</td>\n                  </tr>\n                "]);

  hassio_addon_network_templateObject4 = function _templateObject4() {
    return data;
  };

  return data;
}

function hassio_addon_network_templateObject3() {
  var data = hassio_addon_network_taggedTemplateLiteral([" <div class=\"errors\">", "</div> "]);

  hassio_addon_network_templateObject3 = function _templateObject3() {
    return data;
  };

  return data;
}

function hassio_addon_network_templateObject2() {
  var data = hassio_addon_network_taggedTemplateLiteral(["\n      <paper-card heading=\"Network\">\n        <div class=\"card-content\">\n          ", "\n\n          <table>\n            <tbody>\n              <tr>\n                <th>Container</th>\n                <th>Host</th>\n                <th>Description</th>\n              </tr>\n              ", "\n            </tbody>\n          </table>\n        </div>\n        <div class=\"card-actions\">\n          <mwc-button class=\"warning\" @click=", ">\n            Reset to defaults\n          </mwc-button>\n          <mwc-button @click=", ">Save</mwc-button>\n        </div>\n      </paper-card>\n    "]);

  hassio_addon_network_templateObject2 = function _templateObject2() {
    return data;
  };

  return data;
}

function hassio_addon_network_templateObject() {
  var data = hassio_addon_network_taggedTemplateLiteral([""]);

  hassio_addon_network_templateObject = function _templateObject() {
    return data;
  };

  return data;
}

function hassio_addon_network_taggedTemplateLiteral(strings, raw) { if (!raw) { raw = strings.slice(0); } return Object.freeze(Object.defineProperties(strings, { raw: { value: Object.freeze(raw) } })); }

function hassio_addon_network_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function hassio_addon_network_inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) hassio_addon_network_setPrototypeOf(subClass, superClass); }

function hassio_addon_network_setPrototypeOf(o, p) { hassio_addon_network_setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return hassio_addon_network_setPrototypeOf(o, p); }

function hassio_addon_network_createSuper(Derived) { return function () { var Super = hassio_addon_network_getPrototypeOf(Derived), result; if (hassio_addon_network_isNativeReflectConstruct()) { var NewTarget = hassio_addon_network_getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return hassio_addon_network_possibleConstructorReturn(this, result); }; }

function hassio_addon_network_possibleConstructorReturn(self, call) { if (call && (hassio_addon_network_typeof(call) === "object" || typeof call === "function")) { return call; } return hassio_addon_network_assertThisInitialized(self); }

function hassio_addon_network_assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function hassio_addon_network_isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Date.prototype.toString.call(Reflect.construct(Date, [], function () {})); return true; } catch (e) { return false; } }

function hassio_addon_network_decorate(decorators, factory, superClass, mixins) { var api = hassio_addon_network_getDecoratorsApi(); if (mixins) { for (var i = 0; i < mixins.length; i++) { api = mixins[i](api); } } var r = factory(function initialize(O) { api.initializeInstanceElements(O, decorated.elements); }, superClass); var decorated = api.decorateClass(hassio_addon_network_coalesceClassElements(r.d.map(hassio_addon_network_createElementDescriptor)), decorators); api.initializeClassElements(r.F, decorated.elements); return api.runClassFinishers(r.F, decorated.finishers); }

function hassio_addon_network_getDecoratorsApi() { hassio_addon_network_getDecoratorsApi = function _getDecoratorsApi() { return api; }; var api = { elementsDefinitionOrder: [["method"], ["field"]], initializeInstanceElements: function initializeInstanceElements(O, elements) { ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { if (element.kind === kind && element.placement === "own") { this.defineClassElement(O, element); } }, this); }, this); }, initializeClassElements: function initializeClassElements(F, elements) { var proto = F.prototype; ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { var placement = element.placement; if (element.kind === kind && (placement === "static" || placement === "prototype")) { var receiver = placement === "static" ? F : proto; this.defineClassElement(receiver, element); } }, this); }, this); }, defineClassElement: function defineClassElement(receiver, element) { var descriptor = element.descriptor; if (element.kind === "field") { var initializer = element.initializer; descriptor = { enumerable: descriptor.enumerable, writable: descriptor.writable, configurable: descriptor.configurable, value: initializer === void 0 ? void 0 : initializer.call(receiver) }; } Object.defineProperty(receiver, element.key, descriptor); }, decorateClass: function decorateClass(elements, decorators) { var newElements = []; var finishers = []; var placements = { "static": [], prototype: [], own: [] }; elements.forEach(function (element) { this.addElementPlacement(element, placements); }, this); elements.forEach(function (element) { if (!hassio_addon_network_hasDecorators(element)) return newElements.push(element); var elementFinishersExtras = this.decorateElement(element, placements); newElements.push(elementFinishersExtras.element); newElements.push.apply(newElements, elementFinishersExtras.extras); finishers.push.apply(finishers, elementFinishersExtras.finishers); }, this); if (!decorators) { return { elements: newElements, finishers: finishers }; } var result = this.decorateConstructor(newElements, decorators); finishers.push.apply(finishers, result.finishers); result.finishers = finishers; return result; }, addElementPlacement: function addElementPlacement(element, placements, silent) { var keys = placements[element.placement]; if (!silent && keys.indexOf(element.key) !== -1) { throw new TypeError("Duplicated element (" + element.key + ")"); } keys.push(element.key); }, decorateElement: function decorateElement(element, placements) { var extras = []; var finishers = []; for (var decorators = element.decorators, i = decorators.length - 1; i >= 0; i--) { var keys = placements[element.placement]; keys.splice(keys.indexOf(element.key), 1); var elementObject = this.fromElementDescriptor(element); var elementFinisherExtras = this.toElementFinisherExtras((0, decorators[i])(elementObject) || elementObject); element = elementFinisherExtras.element; this.addElementPlacement(element, placements); if (elementFinisherExtras.finisher) { finishers.push(elementFinisherExtras.finisher); } var newExtras = elementFinisherExtras.extras; if (newExtras) { for (var j = 0; j < newExtras.length; j++) { this.addElementPlacement(newExtras[j], placements); } extras.push.apply(extras, newExtras); } } return { element: element, finishers: finishers, extras: extras }; }, decorateConstructor: function decorateConstructor(elements, decorators) { var finishers = []; for (var i = decorators.length - 1; i >= 0; i--) { var obj = this.fromClassDescriptor(elements); var elementsAndFinisher = this.toClassDescriptor((0, decorators[i])(obj) || obj); if (elementsAndFinisher.finisher !== undefined) { finishers.push(elementsAndFinisher.finisher); } if (elementsAndFinisher.elements !== undefined) { elements = elementsAndFinisher.elements; for (var j = 0; j < elements.length - 1; j++) { for (var k = j + 1; k < elements.length; k++) { if (elements[j].key === elements[k].key && elements[j].placement === elements[k].placement) { throw new TypeError("Duplicated element (" + elements[j].key + ")"); } } } } } return { elements: elements, finishers: finishers }; }, fromElementDescriptor: function fromElementDescriptor(element) { var obj = { kind: element.kind, key: element.key, placement: element.placement, descriptor: element.descriptor }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); if (element.kind === "field") obj.initializer = element.initializer; return obj; }, toElementDescriptors: function toElementDescriptors(elementObjects) { if (elementObjects === undefined) return; return hassio_addon_network_toArray(elementObjects).map(function (elementObject) { var element = this.toElementDescriptor(elementObject); this.disallowProperty(elementObject, "finisher", "An element descriptor"); this.disallowProperty(elementObject, "extras", "An element descriptor"); return element; }, this); }, toElementDescriptor: function toElementDescriptor(elementObject) { var kind = String(elementObject.kind); if (kind !== "method" && kind !== "field") { throw new TypeError('An element descriptor\'s .kind property must be either "method" or' + ' "field", but a decorator created an element descriptor with' + ' .kind "' + kind + '"'); } var key = hassio_addon_network_toPropertyKey(elementObject.key); var placement = String(elementObject.placement); if (placement !== "static" && placement !== "prototype" && placement !== "own") { throw new TypeError('An element descriptor\'s .placement property must be one of "static",' + ' "prototype" or "own", but a decorator created an element descriptor' + ' with .placement "' + placement + '"'); } var descriptor = elementObject.descriptor; this.disallowProperty(elementObject, "elements", "An element descriptor"); var element = { kind: kind, key: key, placement: placement, descriptor: Object.assign({}, descriptor) }; if (kind !== "field") { this.disallowProperty(elementObject, "initializer", "A method descriptor"); } else { this.disallowProperty(descriptor, "get", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "set", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "value", "The property descriptor of a field descriptor"); element.initializer = elementObject.initializer; } return element; }, toElementFinisherExtras: function toElementFinisherExtras(elementObject) { var element = this.toElementDescriptor(elementObject); var finisher = hassio_addon_network_optionalCallableProperty(elementObject, "finisher"); var extras = this.toElementDescriptors(elementObject.extras); return { element: element, finisher: finisher, extras: extras }; }, fromClassDescriptor: function fromClassDescriptor(elements) { var obj = { kind: "class", elements: elements.map(this.fromElementDescriptor, this) }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); return obj; }, toClassDescriptor: function toClassDescriptor(obj) { var kind = String(obj.kind); if (kind !== "class") { throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator' + ' created a class descriptor with .kind "' + kind + '"'); } this.disallowProperty(obj, "key", "A class descriptor"); this.disallowProperty(obj, "placement", "A class descriptor"); this.disallowProperty(obj, "descriptor", "A class descriptor"); this.disallowProperty(obj, "initializer", "A class descriptor"); this.disallowProperty(obj, "extras", "A class descriptor"); var finisher = hassio_addon_network_optionalCallableProperty(obj, "finisher"); var elements = this.toElementDescriptors(obj.elements); return { elements: elements, finisher: finisher }; }, runClassFinishers: function runClassFinishers(constructor, finishers) { for (var i = 0; i < finishers.length; i++) { var newConstructor = (0, finishers[i])(constructor); if (newConstructor !== undefined) { if (typeof newConstructor !== "function") { throw new TypeError("Finishers must return a constructor."); } constructor = newConstructor; } } return constructor; }, disallowProperty: function disallowProperty(obj, name, objectType) { if (obj[name] !== undefined) { throw new TypeError(objectType + " can't have a ." + name + " property."); } } }; return api; }

function hassio_addon_network_createElementDescriptor(def) { var key = hassio_addon_network_toPropertyKey(def.key); var descriptor; if (def.kind === "method") { descriptor = { value: def.value, writable: true, configurable: true, enumerable: false }; } else if (def.kind === "get") { descriptor = { get: def.value, configurable: true, enumerable: false }; } else if (def.kind === "set") { descriptor = { set: def.value, configurable: true, enumerable: false }; } else if (def.kind === "field") { descriptor = { configurable: true, writable: true, enumerable: true }; } var element = { kind: def.kind === "field" ? "field" : "method", key: key, placement: def["static"] ? "static" : def.kind === "field" ? "own" : "prototype", descriptor: descriptor }; if (def.decorators) element.decorators = def.decorators; if (def.kind === "field") element.initializer = def.value; return element; }

function hassio_addon_network_coalesceGetterSetter(element, other) { if (element.descriptor.get !== undefined) { other.descriptor.get = element.descriptor.get; } else { other.descriptor.set = element.descriptor.set; } }

function hassio_addon_network_coalesceClassElements(elements) { var newElements = []; var isSameElement = function isSameElement(other) { return other.kind === "method" && other.key === element.key && other.placement === element.placement; }; for (var i = 0; i < elements.length; i++) { var element = elements[i]; var other; if (element.kind === "method" && (other = newElements.find(isSameElement))) { if (hassio_addon_network_isDataDescriptor(element.descriptor) || hassio_addon_network_isDataDescriptor(other.descriptor)) { if (hassio_addon_network_hasDecorators(element) || hassio_addon_network_hasDecorators(other)) { throw new ReferenceError("Duplicated methods (" + element.key + ") can't be decorated."); } other.descriptor = element.descriptor; } else { if (hassio_addon_network_hasDecorators(element)) { if (hassio_addon_network_hasDecorators(other)) { throw new ReferenceError("Decorators can't be placed on different accessors with for " + "the same property (" + element.key + ")."); } other.decorators = element.decorators; } hassio_addon_network_coalesceGetterSetter(element, other); } } else { newElements.push(element); } } return newElements; }

function hassio_addon_network_hasDecorators(element) { return element.decorators && element.decorators.length; }

function hassio_addon_network_isDataDescriptor(desc) { return desc !== undefined && !(desc.value === undefined && desc.writable === undefined); }

function hassio_addon_network_optionalCallableProperty(obj, name) { var value = obj[name]; if (value !== undefined && typeof value !== "function") { throw new TypeError("Expected '" + name + "' to be a function"); } return value; }

function hassio_addon_network_toPropertyKey(arg) { var key = hassio_addon_network_toPrimitive(arg, "string"); return hassio_addon_network_typeof(key) === "symbol" ? key : String(key); }

function hassio_addon_network_toPrimitive(input, hint) { if (hassio_addon_network_typeof(input) !== "object" || input === null) return input; var prim = input[Symbol.toPrimitive]; if (prim !== undefined) { var res = prim.call(input, hint || "default"); if (hassio_addon_network_typeof(res) !== "object") return res; throw new TypeError("@@toPrimitive must return a primitive value."); } return (hint === "string" ? String : Number)(input); }

function hassio_addon_network_toArray(arr) { return hassio_addon_network_arrayWithHoles(arr) || hassio_addon_network_iterableToArray(arr) || hassio_addon_network_unsupportedIterableToArray(arr) || hassio_addon_network_nonIterableRest(); }

function hassio_addon_network_nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function hassio_addon_network_unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return hassio_addon_network_arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(n); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return hassio_addon_network_arrayLikeToArray(o, minLen); }

function hassio_addon_network_arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function hassio_addon_network_iterableToArray(iter) { if (typeof Symbol !== "undefined" && Symbol.iterator in Object(iter)) return Array.from(iter); }

function hassio_addon_network_arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }

function hassio_addon_network_get(target, property, receiver) { if (typeof Reflect !== "undefined" && Reflect.get) { hassio_addon_network_get = Reflect.get; } else { hassio_addon_network_get = function _get(target, property, receiver) { var base = hassio_addon_network_superPropBase(target, property); if (!base) return; var desc = Object.getOwnPropertyDescriptor(base, property); if (desc.get) { return desc.get.call(receiver); } return desc.value; }; } return hassio_addon_network_get(target, property, receiver || target); }

function hassio_addon_network_superPropBase(object, property) { while (!Object.prototype.hasOwnProperty.call(object, property)) { object = hassio_addon_network_getPrototypeOf(object); if (object === null) break; } return object; }

function hassio_addon_network_getPrototypeOf(o) { hassio_addon_network_getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return hassio_addon_network_getPrototypeOf(o); }









var hassio_addon_network_HassioAddonNetwork = hassio_addon_network_decorate([Object(lit_element["d" /* customElement */])("hassio-addon-network")], function (_initialize, _LitElement) {
  var HassioAddonNetwork = /*#__PURE__*/function (_LitElement2) {
    hassio_addon_network_inherits(HassioAddonNetwork, _LitElement2);

    var _super = hassio_addon_network_createSuper(HassioAddonNetwork);

    function HassioAddonNetwork() {
      var _this;

      hassio_addon_network_classCallCheck(this, HassioAddonNetwork);

      for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
        args[_key] = arguments[_key];
      }

      _this = _super.call.apply(_super, [this].concat(args));

      _initialize(hassio_addon_network_assertThisInitialized(_this));

      return _this;
    }

    return HassioAddonNetwork;
  }(_LitElement);

  return {
    F: HassioAddonNetwork,
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
      key: "addon",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "_error",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "_config",
      value: void 0
    }, {
      kind: "method",
      key: "connectedCallback",
      value: function connectedCallback() {
        hassio_addon_network_get(hassio_addon_network_getPrototypeOf(HassioAddonNetwork.prototype), "connectedCallback", this).call(this);

        this._setNetworkConfig();
      }
    }, {
      kind: "method",
      key: "render",
      value: function render() {
        var _this2 = this;

        if (!this._config) {
          return Object(lit_element["e" /* html */])(hassio_addon_network_templateObject());
        }

        return Object(lit_element["e" /* html */])(hassio_addon_network_templateObject2(), this._error ? Object(lit_element["e" /* html */])(hassio_addon_network_templateObject3(), this._error) : "", this._config.map(function (item) {
          return Object(lit_element["e" /* html */])(hassio_addon_network_templateObject4(), item.container, _this2._configChanged, String(item.host), item.container, item.description);
        }), this._resetTapped, this._saveTapped);
      }
    }, {
      kind: "get",
      "static": true,
      key: "styles",
      value: function styles() {
        return [resources_styles["b" /* haStyle */], hassio_style["a" /* hassioStyle */], Object(lit_element["c" /* css */])(hassio_addon_network_templateObject5())];
      }
    }, {
      kind: "method",
      key: "update",
      value: function update(changedProperties) {
        hassio_addon_network_get(hassio_addon_network_getPrototypeOf(HassioAddonNetwork.prototype), "update", this).call(this, changedProperties);

        if (changedProperties.has("addon")) {
          this._setNetworkConfig();
        }
      }
    }, {
      kind: "method",
      key: "_setNetworkConfig",
      value: function _setNetworkConfig() {
        var network = this.addon.network || {};
        var description = this.addon.network_description || {};
        var items = Object.keys(network).map(function (key) {
          return {
            container: key,
            host: network[key],
            description: description[key]
          };
        });
        this._config = items.sort(function (a, b) {
          return a.container > b.container ? 1 : -1;
        });
      }
    }, {
      kind: "method",
      key: "_configChanged",
      value: function () {
        var _configChanged2 = hassio_addon_network_asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee(ev) {
          var target;
          return regeneratorRuntime.wrap(function _callee$(_context) {
            while (1) {
              switch (_context.prev = _context.next) {
                case 0:
                  target = ev.target;

                  this._config.forEach(function (item) {
                    if (item.container === target.container && item.host !== parseInt(String(target.value), 10)) {
                      item.host = target.value ? parseInt(String(target.value), 10) : null;
                    }
                  });

                case 2:
                case "end":
                  return _context.stop();
              }
            }
          }, _callee, this);
        }));

        function _configChanged(_x) {
          return _configChanged2.apply(this, arguments);
        }

        return _configChanged;
      }()
    }, {
      kind: "method",
      key: "_resetTapped",
      value: function () {
        var _resetTapped2 = hassio_addon_network_asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee2() {
          var _this$addon;

          var data, eventdata, _err$body;

          return regeneratorRuntime.wrap(function _callee2$(_context2) {
            while (1) {
              switch (_context2.prev = _context2.next) {
                case 0:
                  data = {
                    network: null
                  };
                  _context2.prev = 1;
                  _context2.next = 4;
                  return Object(hassio_addon["i" /* setHassioAddonOption */])(this.hass, this.addon.slug, data);

                case 4:
                  eventdata = {
                    success: true,
                    response: undefined,
                    path: "option"
                  };
                  Object(fire_event["a" /* fireEvent */])(this, "hass-api-called", eventdata);
                  _context2.next = 11;
                  break;

                case 8:
                  _context2.prev = 8;
                  _context2.t0 = _context2["catch"](1);
                  this._error = "Failed to set addon network configuration, ".concat(((_err$body = _context2.t0.body) === null || _err$body === void 0 ? void 0 : _err$body.message) || _context2.t0);

                case 11:
                  if (!(!this._error && ((_this$addon = this.addon) === null || _this$addon === void 0 ? void 0 : _this$addon.state) === "started")) {
                    _context2.next = 14;
                    break;
                  }

                  _context2.next = 14;
                  return suggestAddonRestart(this, this.hass, this.addon);

                case 14:
                case "end":
                  return _context2.stop();
              }
            }
          }, _callee2, this, [[1, 8]]);
        }));

        function _resetTapped() {
          return _resetTapped2.apply(this, arguments);
        }

        return _resetTapped;
      }()
    }, {
      kind: "method",
      key: "_saveTapped",
      value: function () {
        var _saveTapped2 = hassio_addon_network_asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee3() {
          var _this$addon2;

          var networkconfiguration, data, eventdata, _err$body2;

          return regeneratorRuntime.wrap(function _callee3$(_context3) {
            while (1) {
              switch (_context3.prev = _context3.next) {
                case 0:
                  this._error = undefined;
                  networkconfiguration = {};

                  this._config.forEach(function (item) {
                    networkconfiguration[item.container] = parseInt(String(item.host), 10);
                  });

                  data = {
                    network: networkconfiguration
                  };
                  _context3.prev = 4;
                  _context3.next = 7;
                  return Object(hassio_addon["i" /* setHassioAddonOption */])(this.hass, this.addon.slug, data);

                case 7:
                  eventdata = {
                    success: true,
                    response: undefined,
                    path: "option"
                  };
                  Object(fire_event["a" /* fireEvent */])(this, "hass-api-called", eventdata);
                  _context3.next = 14;
                  break;

                case 11:
                  _context3.prev = 11;
                  _context3.t0 = _context3["catch"](4);
                  this._error = "Failed to set addon network configuration, ".concat(((_err$body2 = _context3.t0.body) === null || _err$body2 === void 0 ? void 0 : _err$body2.message) || _context3.t0);

                case 14:
                  if (!(!this._error && ((_this$addon2 = this.addon) === null || _this$addon2 === void 0 ? void 0 : _this$addon2.state) === "started")) {
                    _context3.next = 17;
                    break;
                  }

                  _context3.next = 17;
                  return suggestAddonRestart(this, this.hass, this.addon);

                case 17:
                case "end":
                  return _context3.stop();
              }
            }
          }, _callee3, this, [[4, 11]]);
        }));

        function _saveTapped() {
          return _saveTapped2.apply(this, arguments);
        }

        return _saveTapped;
      }()
    }]
  };
}, lit_element["a" /* LitElement */]);
// EXTERNAL MODULE: ./src/layouts/hass-tabs-subpage.ts + 1 modules
var hass_tabs_subpage = __webpack_require__(58);

// EXTERNAL MODULE: ./src/layouts/hass-router-page.ts + 1 modules
var hass_router_page = __webpack_require__(101);

// CONCATENATED MODULE: ./hassio/src/addon-view/info/hassio-addon-info-tab.ts
function hassio_addon_info_tab_typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { hassio_addon_info_tab_typeof = function _typeof(obj) { return typeof obj; }; } else { hassio_addon_info_tab_typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return hassio_addon_info_tab_typeof(obj); }

function hassio_addon_info_tab_templateObject3() {
  var data = hassio_addon_info_tab_taggedTemplateLiteral(["\n        .content {\n          margin: auto;\n          padding: 8px;\n          max-width: 1024px;\n        }\n      "]);

  hassio_addon_info_tab_templateObject3 = function _templateObject3() {
    return data;
  };

  return data;
}

function hassio_addon_info_tab_templateObject2() {
  var data = hassio_addon_info_tab_taggedTemplateLiteral(["\n      <div class=\"content\">\n        <hassio-addon-info\n          .narrow=", "\n          .hass=", "\n          .addon=", "\n        ></hassio-addon-info>\n      </div>\n    "]);

  hassio_addon_info_tab_templateObject2 = function _templateObject2() {
    return data;
  };

  return data;
}

function hassio_addon_info_tab_templateObject() {
  var data = hassio_addon_info_tab_taggedTemplateLiteral([" <paper-spinner-lite active></paper-spinner-lite> "]);

  hassio_addon_info_tab_templateObject = function _templateObject() {
    return data;
  };

  return data;
}

function hassio_addon_info_tab_taggedTemplateLiteral(strings, raw) { if (!raw) { raw = strings.slice(0); } return Object.freeze(Object.defineProperties(strings, { raw: { value: Object.freeze(raw) } })); }

function hassio_addon_info_tab_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function hassio_addon_info_tab_inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) hassio_addon_info_tab_setPrototypeOf(subClass, superClass); }

function hassio_addon_info_tab_setPrototypeOf(o, p) { hassio_addon_info_tab_setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return hassio_addon_info_tab_setPrototypeOf(o, p); }

function hassio_addon_info_tab_createSuper(Derived) { return function () { var Super = hassio_addon_info_tab_getPrototypeOf(Derived), result; if (hassio_addon_info_tab_isNativeReflectConstruct()) { var NewTarget = hassio_addon_info_tab_getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return hassio_addon_info_tab_possibleConstructorReturn(this, result); }; }

function hassio_addon_info_tab_possibleConstructorReturn(self, call) { if (call && (hassio_addon_info_tab_typeof(call) === "object" || typeof call === "function")) { return call; } return hassio_addon_info_tab_assertThisInitialized(self); }

function hassio_addon_info_tab_assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function hassio_addon_info_tab_isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Date.prototype.toString.call(Reflect.construct(Date, [], function () {})); return true; } catch (e) { return false; } }

function hassio_addon_info_tab_getPrototypeOf(o) { hassio_addon_info_tab_getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return hassio_addon_info_tab_getPrototypeOf(o); }

function hassio_addon_info_tab_decorate(decorators, factory, superClass, mixins) { var api = hassio_addon_info_tab_getDecoratorsApi(); if (mixins) { for (var i = 0; i < mixins.length; i++) { api = mixins[i](api); } } var r = factory(function initialize(O) { api.initializeInstanceElements(O, decorated.elements); }, superClass); var decorated = api.decorateClass(hassio_addon_info_tab_coalesceClassElements(r.d.map(hassio_addon_info_tab_createElementDescriptor)), decorators); api.initializeClassElements(r.F, decorated.elements); return api.runClassFinishers(r.F, decorated.finishers); }

function hassio_addon_info_tab_getDecoratorsApi() { hassio_addon_info_tab_getDecoratorsApi = function _getDecoratorsApi() { return api; }; var api = { elementsDefinitionOrder: [["method"], ["field"]], initializeInstanceElements: function initializeInstanceElements(O, elements) { ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { if (element.kind === kind && element.placement === "own") { this.defineClassElement(O, element); } }, this); }, this); }, initializeClassElements: function initializeClassElements(F, elements) { var proto = F.prototype; ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { var placement = element.placement; if (element.kind === kind && (placement === "static" || placement === "prototype")) { var receiver = placement === "static" ? F : proto; this.defineClassElement(receiver, element); } }, this); }, this); }, defineClassElement: function defineClassElement(receiver, element) { var descriptor = element.descriptor; if (element.kind === "field") { var initializer = element.initializer; descriptor = { enumerable: descriptor.enumerable, writable: descriptor.writable, configurable: descriptor.configurable, value: initializer === void 0 ? void 0 : initializer.call(receiver) }; } Object.defineProperty(receiver, element.key, descriptor); }, decorateClass: function decorateClass(elements, decorators) { var newElements = []; var finishers = []; var placements = { "static": [], prototype: [], own: [] }; elements.forEach(function (element) { this.addElementPlacement(element, placements); }, this); elements.forEach(function (element) { if (!hassio_addon_info_tab_hasDecorators(element)) return newElements.push(element); var elementFinishersExtras = this.decorateElement(element, placements); newElements.push(elementFinishersExtras.element); newElements.push.apply(newElements, elementFinishersExtras.extras); finishers.push.apply(finishers, elementFinishersExtras.finishers); }, this); if (!decorators) { return { elements: newElements, finishers: finishers }; } var result = this.decorateConstructor(newElements, decorators); finishers.push.apply(finishers, result.finishers); result.finishers = finishers; return result; }, addElementPlacement: function addElementPlacement(element, placements, silent) { var keys = placements[element.placement]; if (!silent && keys.indexOf(element.key) !== -1) { throw new TypeError("Duplicated element (" + element.key + ")"); } keys.push(element.key); }, decorateElement: function decorateElement(element, placements) { var extras = []; var finishers = []; for (var decorators = element.decorators, i = decorators.length - 1; i >= 0; i--) { var keys = placements[element.placement]; keys.splice(keys.indexOf(element.key), 1); var elementObject = this.fromElementDescriptor(element); var elementFinisherExtras = this.toElementFinisherExtras((0, decorators[i])(elementObject) || elementObject); element = elementFinisherExtras.element; this.addElementPlacement(element, placements); if (elementFinisherExtras.finisher) { finishers.push(elementFinisherExtras.finisher); } var newExtras = elementFinisherExtras.extras; if (newExtras) { for (var j = 0; j < newExtras.length; j++) { this.addElementPlacement(newExtras[j], placements); } extras.push.apply(extras, newExtras); } } return { element: element, finishers: finishers, extras: extras }; }, decorateConstructor: function decorateConstructor(elements, decorators) { var finishers = []; for (var i = decorators.length - 1; i >= 0; i--) { var obj = this.fromClassDescriptor(elements); var elementsAndFinisher = this.toClassDescriptor((0, decorators[i])(obj) || obj); if (elementsAndFinisher.finisher !== undefined) { finishers.push(elementsAndFinisher.finisher); } if (elementsAndFinisher.elements !== undefined) { elements = elementsAndFinisher.elements; for (var j = 0; j < elements.length - 1; j++) { for (var k = j + 1; k < elements.length; k++) { if (elements[j].key === elements[k].key && elements[j].placement === elements[k].placement) { throw new TypeError("Duplicated element (" + elements[j].key + ")"); } } } } } return { elements: elements, finishers: finishers }; }, fromElementDescriptor: function fromElementDescriptor(element) { var obj = { kind: element.kind, key: element.key, placement: element.placement, descriptor: element.descriptor }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); if (element.kind === "field") obj.initializer = element.initializer; return obj; }, toElementDescriptors: function toElementDescriptors(elementObjects) { if (elementObjects === undefined) return; return hassio_addon_info_tab_toArray(elementObjects).map(function (elementObject) { var element = this.toElementDescriptor(elementObject); this.disallowProperty(elementObject, "finisher", "An element descriptor"); this.disallowProperty(elementObject, "extras", "An element descriptor"); return element; }, this); }, toElementDescriptor: function toElementDescriptor(elementObject) { var kind = String(elementObject.kind); if (kind !== "method" && kind !== "field") { throw new TypeError('An element descriptor\'s .kind property must be either "method" or' + ' "field", but a decorator created an element descriptor with' + ' .kind "' + kind + '"'); } var key = hassio_addon_info_tab_toPropertyKey(elementObject.key); var placement = String(elementObject.placement); if (placement !== "static" && placement !== "prototype" && placement !== "own") { throw new TypeError('An element descriptor\'s .placement property must be one of "static",' + ' "prototype" or "own", but a decorator created an element descriptor' + ' with .placement "' + placement + '"'); } var descriptor = elementObject.descriptor; this.disallowProperty(elementObject, "elements", "An element descriptor"); var element = { kind: kind, key: key, placement: placement, descriptor: Object.assign({}, descriptor) }; if (kind !== "field") { this.disallowProperty(elementObject, "initializer", "A method descriptor"); } else { this.disallowProperty(descriptor, "get", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "set", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "value", "The property descriptor of a field descriptor"); element.initializer = elementObject.initializer; } return element; }, toElementFinisherExtras: function toElementFinisherExtras(elementObject) { var element = this.toElementDescriptor(elementObject); var finisher = hassio_addon_info_tab_optionalCallableProperty(elementObject, "finisher"); var extras = this.toElementDescriptors(elementObject.extras); return { element: element, finisher: finisher, extras: extras }; }, fromClassDescriptor: function fromClassDescriptor(elements) { var obj = { kind: "class", elements: elements.map(this.fromElementDescriptor, this) }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); return obj; }, toClassDescriptor: function toClassDescriptor(obj) { var kind = String(obj.kind); if (kind !== "class") { throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator' + ' created a class descriptor with .kind "' + kind + '"'); } this.disallowProperty(obj, "key", "A class descriptor"); this.disallowProperty(obj, "placement", "A class descriptor"); this.disallowProperty(obj, "descriptor", "A class descriptor"); this.disallowProperty(obj, "initializer", "A class descriptor"); this.disallowProperty(obj, "extras", "A class descriptor"); var finisher = hassio_addon_info_tab_optionalCallableProperty(obj, "finisher"); var elements = this.toElementDescriptors(obj.elements); return { elements: elements, finisher: finisher }; }, runClassFinishers: function runClassFinishers(constructor, finishers) { for (var i = 0; i < finishers.length; i++) { var newConstructor = (0, finishers[i])(constructor); if (newConstructor !== undefined) { if (typeof newConstructor !== "function") { throw new TypeError("Finishers must return a constructor."); } constructor = newConstructor; } } return constructor; }, disallowProperty: function disallowProperty(obj, name, objectType) { if (obj[name] !== undefined) { throw new TypeError(objectType + " can't have a ." + name + " property."); } } }; return api; }

function hassio_addon_info_tab_createElementDescriptor(def) { var key = hassio_addon_info_tab_toPropertyKey(def.key); var descriptor; if (def.kind === "method") { descriptor = { value: def.value, writable: true, configurable: true, enumerable: false }; } else if (def.kind === "get") { descriptor = { get: def.value, configurable: true, enumerable: false }; } else if (def.kind === "set") { descriptor = { set: def.value, configurable: true, enumerable: false }; } else if (def.kind === "field") { descriptor = { configurable: true, writable: true, enumerable: true }; } var element = { kind: def.kind === "field" ? "field" : "method", key: key, placement: def["static"] ? "static" : def.kind === "field" ? "own" : "prototype", descriptor: descriptor }; if (def.decorators) element.decorators = def.decorators; if (def.kind === "field") element.initializer = def.value; return element; }

function hassio_addon_info_tab_coalesceGetterSetter(element, other) { if (element.descriptor.get !== undefined) { other.descriptor.get = element.descriptor.get; } else { other.descriptor.set = element.descriptor.set; } }

function hassio_addon_info_tab_coalesceClassElements(elements) { var newElements = []; var isSameElement = function isSameElement(other) { return other.kind === "method" && other.key === element.key && other.placement === element.placement; }; for (var i = 0; i < elements.length; i++) { var element = elements[i]; var other; if (element.kind === "method" && (other = newElements.find(isSameElement))) { if (hassio_addon_info_tab_isDataDescriptor(element.descriptor) || hassio_addon_info_tab_isDataDescriptor(other.descriptor)) { if (hassio_addon_info_tab_hasDecorators(element) || hassio_addon_info_tab_hasDecorators(other)) { throw new ReferenceError("Duplicated methods (" + element.key + ") can't be decorated."); } other.descriptor = element.descriptor; } else { if (hassio_addon_info_tab_hasDecorators(element)) { if (hassio_addon_info_tab_hasDecorators(other)) { throw new ReferenceError("Decorators can't be placed on different accessors with for " + "the same property (" + element.key + ")."); } other.decorators = element.decorators; } hassio_addon_info_tab_coalesceGetterSetter(element, other); } } else { newElements.push(element); } } return newElements; }

function hassio_addon_info_tab_hasDecorators(element) { return element.decorators && element.decorators.length; }

function hassio_addon_info_tab_isDataDescriptor(desc) { return desc !== undefined && !(desc.value === undefined && desc.writable === undefined); }

function hassio_addon_info_tab_optionalCallableProperty(obj, name) { var value = obj[name]; if (value !== undefined && typeof value !== "function") { throw new TypeError("Expected '" + name + "' to be a function"); } return value; }

function hassio_addon_info_tab_toPropertyKey(arg) { var key = hassio_addon_info_tab_toPrimitive(arg, "string"); return hassio_addon_info_tab_typeof(key) === "symbol" ? key : String(key); }

function hassio_addon_info_tab_toPrimitive(input, hint) { if (hassio_addon_info_tab_typeof(input) !== "object" || input === null) return input; var prim = input[Symbol.toPrimitive]; if (prim !== undefined) { var res = prim.call(input, hint || "default"); if (hassio_addon_info_tab_typeof(res) !== "object") return res; throw new TypeError("@@toPrimitive must return a primitive value."); } return (hint === "string" ? String : Number)(input); }

function hassio_addon_info_tab_toArray(arr) { return hassio_addon_info_tab_arrayWithHoles(arr) || hassio_addon_info_tab_iterableToArray(arr) || hassio_addon_info_tab_unsupportedIterableToArray(arr) || hassio_addon_info_tab_nonIterableRest(); }

function hassio_addon_info_tab_nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function hassio_addon_info_tab_unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return hassio_addon_info_tab_arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(n); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return hassio_addon_info_tab_arrayLikeToArray(o, minLen); }

function hassio_addon_info_tab_arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function hassio_addon_info_tab_iterableToArray(iter) { if (typeof Symbol !== "undefined" && Symbol.iterator in Object(iter)) return Array.from(iter); }

function hassio_addon_info_tab_arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }







var hassio_addon_info_tab_HassioAddonInfoDashboard = hassio_addon_info_tab_decorate([Object(lit_element["d" /* customElement */])("hassio-addon-info-tab")], function (_initialize, _LitElement) {
  var HassioAddonInfoDashboard = /*#__PURE__*/function (_LitElement2) {
    hassio_addon_info_tab_inherits(HassioAddonInfoDashboard, _LitElement2);

    var _super = hassio_addon_info_tab_createSuper(HassioAddonInfoDashboard);

    function HassioAddonInfoDashboard() {
      var _this;

      hassio_addon_info_tab_classCallCheck(this, HassioAddonInfoDashboard);

      for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
        args[_key] = arguments[_key];
      }

      _this = _super.call.apply(_super, [this].concat(args));

      _initialize(hassio_addon_info_tab_assertThisInitialized(_this));

      return _this;
    }

    return HassioAddonInfoDashboard;
  }(_LitElement);

  return {
    F: HassioAddonInfoDashboard,
    d: [{
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
      key: "hass",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])({
        attribute: false
      })],
      key: "addon",
      value: void 0
    }, {
      kind: "method",
      key: "render",
      value: function render() {
        if (!this.addon) {
          return Object(lit_element["e" /* html */])(hassio_addon_info_tab_templateObject());
        }

        return Object(lit_element["e" /* html */])(hassio_addon_info_tab_templateObject2(), this.narrow, this.hass, this.addon);
      }
    }, {
      kind: "get",
      "static": true,
      key: "styles",
      value: function styles() {
        return [resources_styles["b" /* haStyle */], hassio_style["a" /* hassioStyle */], Object(lit_element["c" /* css */])(hassio_addon_info_tab_templateObject3())];
      }
    }]
  };
}, lit_element["a" /* LitElement */]);
// CONCATENATED MODULE: ./hassio/src/addon-view/config/hassio-addon-config-tab.ts
function hassio_addon_config_tab_typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { hassio_addon_config_tab_typeof = function _typeof(obj) { return typeof obj; }; } else { hassio_addon_config_tab_typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return hassio_addon_config_tab_typeof(obj); }

function hassio_addon_config_tab_templateObject5() {
  var data = hassio_addon_config_tab_taggedTemplateLiteral(["\n        .content {\n          margin: auto;\n          padding: 8px;\n          max-width: 1024px;\n        }\n        hassio-addon-network,\n        hassio-addon-audio,\n        hassio-addon-config {\n          margin-bottom: 24px;\n        }\n      "]);

  hassio_addon_config_tab_templateObject5 = function _templateObject5() {
    return data;
  };

  return data;
}

function hassio_addon_config_tab_templateObject4() {
  var data = hassio_addon_config_tab_taggedTemplateLiteral(["\n              <hassio-addon-audio\n                .hass=", "\n                .addon=", "\n              ></hassio-addon-audio>\n            "]);

  hassio_addon_config_tab_templateObject4 = function _templateObject4() {
    return data;
  };

  return data;
}

function hassio_addon_config_tab_templateObject3() {
  var data = hassio_addon_config_tab_taggedTemplateLiteral(["\n              <hassio-addon-network\n                .hass=", "\n                .addon=", "\n              ></hassio-addon-network>\n            "]);

  hassio_addon_config_tab_templateObject3 = function _templateObject3() {
    return data;
  };

  return data;
}

function hassio_addon_config_tab_templateObject2() {
  var data = hassio_addon_config_tab_taggedTemplateLiteral(["\n      <div class=\"content\">\n        <hassio-addon-config\n          .hass=", "\n          .addon=", "\n        ></hassio-addon-config>\n        ", "\n        ", "\n      </div>\n    "]);

  hassio_addon_config_tab_templateObject2 = function _templateObject2() {
    return data;
  };

  return data;
}

function hassio_addon_config_tab_templateObject() {
  var data = hassio_addon_config_tab_taggedTemplateLiteral([" <paper-spinner-lite active></paper-spinner-lite> "]);

  hassio_addon_config_tab_templateObject = function _templateObject() {
    return data;
  };

  return data;
}

function hassio_addon_config_tab_taggedTemplateLiteral(strings, raw) { if (!raw) { raw = strings.slice(0); } return Object.freeze(Object.defineProperties(strings, { raw: { value: Object.freeze(raw) } })); }

function hassio_addon_config_tab_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function hassio_addon_config_tab_inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) hassio_addon_config_tab_setPrototypeOf(subClass, superClass); }

function hassio_addon_config_tab_setPrototypeOf(o, p) { hassio_addon_config_tab_setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return hassio_addon_config_tab_setPrototypeOf(o, p); }

function hassio_addon_config_tab_createSuper(Derived) { return function () { var Super = hassio_addon_config_tab_getPrototypeOf(Derived), result; if (hassio_addon_config_tab_isNativeReflectConstruct()) { var NewTarget = hassio_addon_config_tab_getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return hassio_addon_config_tab_possibleConstructorReturn(this, result); }; }

function hassio_addon_config_tab_possibleConstructorReturn(self, call) { if (call && (hassio_addon_config_tab_typeof(call) === "object" || typeof call === "function")) { return call; } return hassio_addon_config_tab_assertThisInitialized(self); }

function hassio_addon_config_tab_assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function hassio_addon_config_tab_isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Date.prototype.toString.call(Reflect.construct(Date, [], function () {})); return true; } catch (e) { return false; } }

function hassio_addon_config_tab_getPrototypeOf(o) { hassio_addon_config_tab_getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return hassio_addon_config_tab_getPrototypeOf(o); }

function hassio_addon_config_tab_decorate(decorators, factory, superClass, mixins) { var api = hassio_addon_config_tab_getDecoratorsApi(); if (mixins) { for (var i = 0; i < mixins.length; i++) { api = mixins[i](api); } } var r = factory(function initialize(O) { api.initializeInstanceElements(O, decorated.elements); }, superClass); var decorated = api.decorateClass(hassio_addon_config_tab_coalesceClassElements(r.d.map(hassio_addon_config_tab_createElementDescriptor)), decorators); api.initializeClassElements(r.F, decorated.elements); return api.runClassFinishers(r.F, decorated.finishers); }

function hassio_addon_config_tab_getDecoratorsApi() { hassio_addon_config_tab_getDecoratorsApi = function _getDecoratorsApi() { return api; }; var api = { elementsDefinitionOrder: [["method"], ["field"]], initializeInstanceElements: function initializeInstanceElements(O, elements) { ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { if (element.kind === kind && element.placement === "own") { this.defineClassElement(O, element); } }, this); }, this); }, initializeClassElements: function initializeClassElements(F, elements) { var proto = F.prototype; ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { var placement = element.placement; if (element.kind === kind && (placement === "static" || placement === "prototype")) { var receiver = placement === "static" ? F : proto; this.defineClassElement(receiver, element); } }, this); }, this); }, defineClassElement: function defineClassElement(receiver, element) { var descriptor = element.descriptor; if (element.kind === "field") { var initializer = element.initializer; descriptor = { enumerable: descriptor.enumerable, writable: descriptor.writable, configurable: descriptor.configurable, value: initializer === void 0 ? void 0 : initializer.call(receiver) }; } Object.defineProperty(receiver, element.key, descriptor); }, decorateClass: function decorateClass(elements, decorators) { var newElements = []; var finishers = []; var placements = { "static": [], prototype: [], own: [] }; elements.forEach(function (element) { this.addElementPlacement(element, placements); }, this); elements.forEach(function (element) { if (!hassio_addon_config_tab_hasDecorators(element)) return newElements.push(element); var elementFinishersExtras = this.decorateElement(element, placements); newElements.push(elementFinishersExtras.element); newElements.push.apply(newElements, elementFinishersExtras.extras); finishers.push.apply(finishers, elementFinishersExtras.finishers); }, this); if (!decorators) { return { elements: newElements, finishers: finishers }; } var result = this.decorateConstructor(newElements, decorators); finishers.push.apply(finishers, result.finishers); result.finishers = finishers; return result; }, addElementPlacement: function addElementPlacement(element, placements, silent) { var keys = placements[element.placement]; if (!silent && keys.indexOf(element.key) !== -1) { throw new TypeError("Duplicated element (" + element.key + ")"); } keys.push(element.key); }, decorateElement: function decorateElement(element, placements) { var extras = []; var finishers = []; for (var decorators = element.decorators, i = decorators.length - 1; i >= 0; i--) { var keys = placements[element.placement]; keys.splice(keys.indexOf(element.key), 1); var elementObject = this.fromElementDescriptor(element); var elementFinisherExtras = this.toElementFinisherExtras((0, decorators[i])(elementObject) || elementObject); element = elementFinisherExtras.element; this.addElementPlacement(element, placements); if (elementFinisherExtras.finisher) { finishers.push(elementFinisherExtras.finisher); } var newExtras = elementFinisherExtras.extras; if (newExtras) { for (var j = 0; j < newExtras.length; j++) { this.addElementPlacement(newExtras[j], placements); } extras.push.apply(extras, newExtras); } } return { element: element, finishers: finishers, extras: extras }; }, decorateConstructor: function decorateConstructor(elements, decorators) { var finishers = []; for (var i = decorators.length - 1; i >= 0; i--) { var obj = this.fromClassDescriptor(elements); var elementsAndFinisher = this.toClassDescriptor((0, decorators[i])(obj) || obj); if (elementsAndFinisher.finisher !== undefined) { finishers.push(elementsAndFinisher.finisher); } if (elementsAndFinisher.elements !== undefined) { elements = elementsAndFinisher.elements; for (var j = 0; j < elements.length - 1; j++) { for (var k = j + 1; k < elements.length; k++) { if (elements[j].key === elements[k].key && elements[j].placement === elements[k].placement) { throw new TypeError("Duplicated element (" + elements[j].key + ")"); } } } } } return { elements: elements, finishers: finishers }; }, fromElementDescriptor: function fromElementDescriptor(element) { var obj = { kind: element.kind, key: element.key, placement: element.placement, descriptor: element.descriptor }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); if (element.kind === "field") obj.initializer = element.initializer; return obj; }, toElementDescriptors: function toElementDescriptors(elementObjects) { if (elementObjects === undefined) return; return hassio_addon_config_tab_toArray(elementObjects).map(function (elementObject) { var element = this.toElementDescriptor(elementObject); this.disallowProperty(elementObject, "finisher", "An element descriptor"); this.disallowProperty(elementObject, "extras", "An element descriptor"); return element; }, this); }, toElementDescriptor: function toElementDescriptor(elementObject) { var kind = String(elementObject.kind); if (kind !== "method" && kind !== "field") { throw new TypeError('An element descriptor\'s .kind property must be either "method" or' + ' "field", but a decorator created an element descriptor with' + ' .kind "' + kind + '"'); } var key = hassio_addon_config_tab_toPropertyKey(elementObject.key); var placement = String(elementObject.placement); if (placement !== "static" && placement !== "prototype" && placement !== "own") { throw new TypeError('An element descriptor\'s .placement property must be one of "static",' + ' "prototype" or "own", but a decorator created an element descriptor' + ' with .placement "' + placement + '"'); } var descriptor = elementObject.descriptor; this.disallowProperty(elementObject, "elements", "An element descriptor"); var element = { kind: kind, key: key, placement: placement, descriptor: Object.assign({}, descriptor) }; if (kind !== "field") { this.disallowProperty(elementObject, "initializer", "A method descriptor"); } else { this.disallowProperty(descriptor, "get", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "set", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "value", "The property descriptor of a field descriptor"); element.initializer = elementObject.initializer; } return element; }, toElementFinisherExtras: function toElementFinisherExtras(elementObject) { var element = this.toElementDescriptor(elementObject); var finisher = hassio_addon_config_tab_optionalCallableProperty(elementObject, "finisher"); var extras = this.toElementDescriptors(elementObject.extras); return { element: element, finisher: finisher, extras: extras }; }, fromClassDescriptor: function fromClassDescriptor(elements) { var obj = { kind: "class", elements: elements.map(this.fromElementDescriptor, this) }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); return obj; }, toClassDescriptor: function toClassDescriptor(obj) { var kind = String(obj.kind); if (kind !== "class") { throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator' + ' created a class descriptor with .kind "' + kind + '"'); } this.disallowProperty(obj, "key", "A class descriptor"); this.disallowProperty(obj, "placement", "A class descriptor"); this.disallowProperty(obj, "descriptor", "A class descriptor"); this.disallowProperty(obj, "initializer", "A class descriptor"); this.disallowProperty(obj, "extras", "A class descriptor"); var finisher = hassio_addon_config_tab_optionalCallableProperty(obj, "finisher"); var elements = this.toElementDescriptors(obj.elements); return { elements: elements, finisher: finisher }; }, runClassFinishers: function runClassFinishers(constructor, finishers) { for (var i = 0; i < finishers.length; i++) { var newConstructor = (0, finishers[i])(constructor); if (newConstructor !== undefined) { if (typeof newConstructor !== "function") { throw new TypeError("Finishers must return a constructor."); } constructor = newConstructor; } } return constructor; }, disallowProperty: function disallowProperty(obj, name, objectType) { if (obj[name] !== undefined) { throw new TypeError(objectType + " can't have a ." + name + " property."); } } }; return api; }

function hassio_addon_config_tab_createElementDescriptor(def) { var key = hassio_addon_config_tab_toPropertyKey(def.key); var descriptor; if (def.kind === "method") { descriptor = { value: def.value, writable: true, configurable: true, enumerable: false }; } else if (def.kind === "get") { descriptor = { get: def.value, configurable: true, enumerable: false }; } else if (def.kind === "set") { descriptor = { set: def.value, configurable: true, enumerable: false }; } else if (def.kind === "field") { descriptor = { configurable: true, writable: true, enumerable: true }; } var element = { kind: def.kind === "field" ? "field" : "method", key: key, placement: def["static"] ? "static" : def.kind === "field" ? "own" : "prototype", descriptor: descriptor }; if (def.decorators) element.decorators = def.decorators; if (def.kind === "field") element.initializer = def.value; return element; }

function hassio_addon_config_tab_coalesceGetterSetter(element, other) { if (element.descriptor.get !== undefined) { other.descriptor.get = element.descriptor.get; } else { other.descriptor.set = element.descriptor.set; } }

function hassio_addon_config_tab_coalesceClassElements(elements) { var newElements = []; var isSameElement = function isSameElement(other) { return other.kind === "method" && other.key === element.key && other.placement === element.placement; }; for (var i = 0; i < elements.length; i++) { var element = elements[i]; var other; if (element.kind === "method" && (other = newElements.find(isSameElement))) { if (hassio_addon_config_tab_isDataDescriptor(element.descriptor) || hassio_addon_config_tab_isDataDescriptor(other.descriptor)) { if (hassio_addon_config_tab_hasDecorators(element) || hassio_addon_config_tab_hasDecorators(other)) { throw new ReferenceError("Duplicated methods (" + element.key + ") can't be decorated."); } other.descriptor = element.descriptor; } else { if (hassio_addon_config_tab_hasDecorators(element)) { if (hassio_addon_config_tab_hasDecorators(other)) { throw new ReferenceError("Decorators can't be placed on different accessors with for " + "the same property (" + element.key + ")."); } other.decorators = element.decorators; } hassio_addon_config_tab_coalesceGetterSetter(element, other); } } else { newElements.push(element); } } return newElements; }

function hassio_addon_config_tab_hasDecorators(element) { return element.decorators && element.decorators.length; }

function hassio_addon_config_tab_isDataDescriptor(desc) { return desc !== undefined && !(desc.value === undefined && desc.writable === undefined); }

function hassio_addon_config_tab_optionalCallableProperty(obj, name) { var value = obj[name]; if (value !== undefined && typeof value !== "function") { throw new TypeError("Expected '" + name + "' to be a function"); } return value; }

function hassio_addon_config_tab_toPropertyKey(arg) { var key = hassio_addon_config_tab_toPrimitive(arg, "string"); return hassio_addon_config_tab_typeof(key) === "symbol" ? key : String(key); }

function hassio_addon_config_tab_toPrimitive(input, hint) { if (hassio_addon_config_tab_typeof(input) !== "object" || input === null) return input; var prim = input[Symbol.toPrimitive]; if (prim !== undefined) { var res = prim.call(input, hint || "default"); if (hassio_addon_config_tab_typeof(res) !== "object") return res; throw new TypeError("@@toPrimitive must return a primitive value."); } return (hint === "string" ? String : Number)(input); }

function hassio_addon_config_tab_toArray(arr) { return hassio_addon_config_tab_arrayWithHoles(arr) || hassio_addon_config_tab_iterableToArray(arr) || hassio_addon_config_tab_unsupportedIterableToArray(arr) || hassio_addon_config_tab_nonIterableRest(); }

function hassio_addon_config_tab_nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function hassio_addon_config_tab_unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return hassio_addon_config_tab_arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(n); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return hassio_addon_config_tab_arrayLikeToArray(o, minLen); }

function hassio_addon_config_tab_arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function hassio_addon_config_tab_iterableToArray(iter) { if (typeof Symbol !== "undefined" && Symbol.iterator in Object(iter)) return Array.from(iter); }

function hassio_addon_config_tab_arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }









var hassio_addon_config_tab_HassioAddonConfigDashboard = hassio_addon_config_tab_decorate([Object(lit_element["d" /* customElement */])("hassio-addon-config-tab")], function (_initialize, _LitElement) {
  var HassioAddonConfigDashboard = /*#__PURE__*/function (_LitElement2) {
    hassio_addon_config_tab_inherits(HassioAddonConfigDashboard, _LitElement2);

    var _super = hassio_addon_config_tab_createSuper(HassioAddonConfigDashboard);

    function HassioAddonConfigDashboard() {
      var _this;

      hassio_addon_config_tab_classCallCheck(this, HassioAddonConfigDashboard);

      for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
        args[_key] = arguments[_key];
      }

      _this = _super.call.apply(_super, [this].concat(args));

      _initialize(hassio_addon_config_tab_assertThisInitialized(_this));

      return _this;
    }

    return HassioAddonConfigDashboard;
  }(_LitElement);

  return {
    F: HassioAddonConfigDashboard,
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
      key: "addon",
      value: void 0
    }, {
      kind: "method",
      key: "render",
      value: function render() {
        if (!this.addon) {
          return Object(lit_element["e" /* html */])(hassio_addon_config_tab_templateObject());
        }

        return Object(lit_element["e" /* html */])(hassio_addon_config_tab_templateObject2(), this.hass, this.addon, this.addon.network ? Object(lit_element["e" /* html */])(hassio_addon_config_tab_templateObject3(), this.hass, this.addon) : "", this.addon.audio ? Object(lit_element["e" /* html */])(hassio_addon_config_tab_templateObject4(), this.hass, this.addon) : "");
      }
    }, {
      kind: "get",
      "static": true,
      key: "styles",
      value: function styles() {
        return [resources_styles["b" /* haStyle */], hassio_style["a" /* hassioStyle */], Object(lit_element["c" /* css */])(hassio_addon_config_tab_templateObject5())];
      }
    }]
  };
}, lit_element["a" /* LitElement */]);
// CONCATENATED MODULE: ./hassio/src/addon-view/log/hassio-addon-log-tab.ts
function hassio_addon_log_tab_typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { hassio_addon_log_tab_typeof = function _typeof(obj) { return typeof obj; }; } else { hassio_addon_log_tab_typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return hassio_addon_log_tab_typeof(obj); }

function hassio_addon_log_tab_templateObject3() {
  var data = hassio_addon_log_tab_taggedTemplateLiteral(["\n        .content {\n          margin: auto;\n          padding: 8px;\n          max-width: 1024px;\n        }\n      "]);

  hassio_addon_log_tab_templateObject3 = function _templateObject3() {
    return data;
  };

  return data;
}

function hassio_addon_log_tab_templateObject2() {
  var data = hassio_addon_log_tab_taggedTemplateLiteral(["\n      <div class=\"content\">\n        <hassio-addon-logs\n          .hass=", "\n          .addon=", "\n        ></hassio-addon-logs>\n      </div>\n    "]);

  hassio_addon_log_tab_templateObject2 = function _templateObject2() {
    return data;
  };

  return data;
}

function hassio_addon_log_tab_templateObject() {
  var data = hassio_addon_log_tab_taggedTemplateLiteral([" <paper-spinner-lite active></paper-spinner-lite> "]);

  hassio_addon_log_tab_templateObject = function _templateObject() {
    return data;
  };

  return data;
}

function hassio_addon_log_tab_taggedTemplateLiteral(strings, raw) { if (!raw) { raw = strings.slice(0); } return Object.freeze(Object.defineProperties(strings, { raw: { value: Object.freeze(raw) } })); }

function hassio_addon_log_tab_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function hassio_addon_log_tab_inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) hassio_addon_log_tab_setPrototypeOf(subClass, superClass); }

function hassio_addon_log_tab_setPrototypeOf(o, p) { hassio_addon_log_tab_setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return hassio_addon_log_tab_setPrototypeOf(o, p); }

function hassio_addon_log_tab_createSuper(Derived) { return function () { var Super = hassio_addon_log_tab_getPrototypeOf(Derived), result; if (hassio_addon_log_tab_isNativeReflectConstruct()) { var NewTarget = hassio_addon_log_tab_getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return hassio_addon_log_tab_possibleConstructorReturn(this, result); }; }

function hassio_addon_log_tab_possibleConstructorReturn(self, call) { if (call && (hassio_addon_log_tab_typeof(call) === "object" || typeof call === "function")) { return call; } return hassio_addon_log_tab_assertThisInitialized(self); }

function hassio_addon_log_tab_assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function hassio_addon_log_tab_isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Date.prototype.toString.call(Reflect.construct(Date, [], function () {})); return true; } catch (e) { return false; } }

function hassio_addon_log_tab_getPrototypeOf(o) { hassio_addon_log_tab_getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return hassio_addon_log_tab_getPrototypeOf(o); }

function hassio_addon_log_tab_decorate(decorators, factory, superClass, mixins) { var api = hassio_addon_log_tab_getDecoratorsApi(); if (mixins) { for (var i = 0; i < mixins.length; i++) { api = mixins[i](api); } } var r = factory(function initialize(O) { api.initializeInstanceElements(O, decorated.elements); }, superClass); var decorated = api.decorateClass(hassio_addon_log_tab_coalesceClassElements(r.d.map(hassio_addon_log_tab_createElementDescriptor)), decorators); api.initializeClassElements(r.F, decorated.elements); return api.runClassFinishers(r.F, decorated.finishers); }

function hassio_addon_log_tab_getDecoratorsApi() { hassio_addon_log_tab_getDecoratorsApi = function _getDecoratorsApi() { return api; }; var api = { elementsDefinitionOrder: [["method"], ["field"]], initializeInstanceElements: function initializeInstanceElements(O, elements) { ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { if (element.kind === kind && element.placement === "own") { this.defineClassElement(O, element); } }, this); }, this); }, initializeClassElements: function initializeClassElements(F, elements) { var proto = F.prototype; ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { var placement = element.placement; if (element.kind === kind && (placement === "static" || placement === "prototype")) { var receiver = placement === "static" ? F : proto; this.defineClassElement(receiver, element); } }, this); }, this); }, defineClassElement: function defineClassElement(receiver, element) { var descriptor = element.descriptor; if (element.kind === "field") { var initializer = element.initializer; descriptor = { enumerable: descriptor.enumerable, writable: descriptor.writable, configurable: descriptor.configurable, value: initializer === void 0 ? void 0 : initializer.call(receiver) }; } Object.defineProperty(receiver, element.key, descriptor); }, decorateClass: function decorateClass(elements, decorators) { var newElements = []; var finishers = []; var placements = { "static": [], prototype: [], own: [] }; elements.forEach(function (element) { this.addElementPlacement(element, placements); }, this); elements.forEach(function (element) { if (!hassio_addon_log_tab_hasDecorators(element)) return newElements.push(element); var elementFinishersExtras = this.decorateElement(element, placements); newElements.push(elementFinishersExtras.element); newElements.push.apply(newElements, elementFinishersExtras.extras); finishers.push.apply(finishers, elementFinishersExtras.finishers); }, this); if (!decorators) { return { elements: newElements, finishers: finishers }; } var result = this.decorateConstructor(newElements, decorators); finishers.push.apply(finishers, result.finishers); result.finishers = finishers; return result; }, addElementPlacement: function addElementPlacement(element, placements, silent) { var keys = placements[element.placement]; if (!silent && keys.indexOf(element.key) !== -1) { throw new TypeError("Duplicated element (" + element.key + ")"); } keys.push(element.key); }, decorateElement: function decorateElement(element, placements) { var extras = []; var finishers = []; for (var decorators = element.decorators, i = decorators.length - 1; i >= 0; i--) { var keys = placements[element.placement]; keys.splice(keys.indexOf(element.key), 1); var elementObject = this.fromElementDescriptor(element); var elementFinisherExtras = this.toElementFinisherExtras((0, decorators[i])(elementObject) || elementObject); element = elementFinisherExtras.element; this.addElementPlacement(element, placements); if (elementFinisherExtras.finisher) { finishers.push(elementFinisherExtras.finisher); } var newExtras = elementFinisherExtras.extras; if (newExtras) { for (var j = 0; j < newExtras.length; j++) { this.addElementPlacement(newExtras[j], placements); } extras.push.apply(extras, newExtras); } } return { element: element, finishers: finishers, extras: extras }; }, decorateConstructor: function decorateConstructor(elements, decorators) { var finishers = []; for (var i = decorators.length - 1; i >= 0; i--) { var obj = this.fromClassDescriptor(elements); var elementsAndFinisher = this.toClassDescriptor((0, decorators[i])(obj) || obj); if (elementsAndFinisher.finisher !== undefined) { finishers.push(elementsAndFinisher.finisher); } if (elementsAndFinisher.elements !== undefined) { elements = elementsAndFinisher.elements; for (var j = 0; j < elements.length - 1; j++) { for (var k = j + 1; k < elements.length; k++) { if (elements[j].key === elements[k].key && elements[j].placement === elements[k].placement) { throw new TypeError("Duplicated element (" + elements[j].key + ")"); } } } } } return { elements: elements, finishers: finishers }; }, fromElementDescriptor: function fromElementDescriptor(element) { var obj = { kind: element.kind, key: element.key, placement: element.placement, descriptor: element.descriptor }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); if (element.kind === "field") obj.initializer = element.initializer; return obj; }, toElementDescriptors: function toElementDescriptors(elementObjects) { if (elementObjects === undefined) return; return hassio_addon_log_tab_toArray(elementObjects).map(function (elementObject) { var element = this.toElementDescriptor(elementObject); this.disallowProperty(elementObject, "finisher", "An element descriptor"); this.disallowProperty(elementObject, "extras", "An element descriptor"); return element; }, this); }, toElementDescriptor: function toElementDescriptor(elementObject) { var kind = String(elementObject.kind); if (kind !== "method" && kind !== "field") { throw new TypeError('An element descriptor\'s .kind property must be either "method" or' + ' "field", but a decorator created an element descriptor with' + ' .kind "' + kind + '"'); } var key = hassio_addon_log_tab_toPropertyKey(elementObject.key); var placement = String(elementObject.placement); if (placement !== "static" && placement !== "prototype" && placement !== "own") { throw new TypeError('An element descriptor\'s .placement property must be one of "static",' + ' "prototype" or "own", but a decorator created an element descriptor' + ' with .placement "' + placement + '"'); } var descriptor = elementObject.descriptor; this.disallowProperty(elementObject, "elements", "An element descriptor"); var element = { kind: kind, key: key, placement: placement, descriptor: Object.assign({}, descriptor) }; if (kind !== "field") { this.disallowProperty(elementObject, "initializer", "A method descriptor"); } else { this.disallowProperty(descriptor, "get", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "set", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "value", "The property descriptor of a field descriptor"); element.initializer = elementObject.initializer; } return element; }, toElementFinisherExtras: function toElementFinisherExtras(elementObject) { var element = this.toElementDescriptor(elementObject); var finisher = hassio_addon_log_tab_optionalCallableProperty(elementObject, "finisher"); var extras = this.toElementDescriptors(elementObject.extras); return { element: element, finisher: finisher, extras: extras }; }, fromClassDescriptor: function fromClassDescriptor(elements) { var obj = { kind: "class", elements: elements.map(this.fromElementDescriptor, this) }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); return obj; }, toClassDescriptor: function toClassDescriptor(obj) { var kind = String(obj.kind); if (kind !== "class") { throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator' + ' created a class descriptor with .kind "' + kind + '"'); } this.disallowProperty(obj, "key", "A class descriptor"); this.disallowProperty(obj, "placement", "A class descriptor"); this.disallowProperty(obj, "descriptor", "A class descriptor"); this.disallowProperty(obj, "initializer", "A class descriptor"); this.disallowProperty(obj, "extras", "A class descriptor"); var finisher = hassio_addon_log_tab_optionalCallableProperty(obj, "finisher"); var elements = this.toElementDescriptors(obj.elements); return { elements: elements, finisher: finisher }; }, runClassFinishers: function runClassFinishers(constructor, finishers) { for (var i = 0; i < finishers.length; i++) { var newConstructor = (0, finishers[i])(constructor); if (newConstructor !== undefined) { if (typeof newConstructor !== "function") { throw new TypeError("Finishers must return a constructor."); } constructor = newConstructor; } } return constructor; }, disallowProperty: function disallowProperty(obj, name, objectType) { if (obj[name] !== undefined) { throw new TypeError(objectType + " can't have a ." + name + " property."); } } }; return api; }

function hassio_addon_log_tab_createElementDescriptor(def) { var key = hassio_addon_log_tab_toPropertyKey(def.key); var descriptor; if (def.kind === "method") { descriptor = { value: def.value, writable: true, configurable: true, enumerable: false }; } else if (def.kind === "get") { descriptor = { get: def.value, configurable: true, enumerable: false }; } else if (def.kind === "set") { descriptor = { set: def.value, configurable: true, enumerable: false }; } else if (def.kind === "field") { descriptor = { configurable: true, writable: true, enumerable: true }; } var element = { kind: def.kind === "field" ? "field" : "method", key: key, placement: def["static"] ? "static" : def.kind === "field" ? "own" : "prototype", descriptor: descriptor }; if (def.decorators) element.decorators = def.decorators; if (def.kind === "field") element.initializer = def.value; return element; }

function hassio_addon_log_tab_coalesceGetterSetter(element, other) { if (element.descriptor.get !== undefined) { other.descriptor.get = element.descriptor.get; } else { other.descriptor.set = element.descriptor.set; } }

function hassio_addon_log_tab_coalesceClassElements(elements) { var newElements = []; var isSameElement = function isSameElement(other) { return other.kind === "method" && other.key === element.key && other.placement === element.placement; }; for (var i = 0; i < elements.length; i++) { var element = elements[i]; var other; if (element.kind === "method" && (other = newElements.find(isSameElement))) { if (hassio_addon_log_tab_isDataDescriptor(element.descriptor) || hassio_addon_log_tab_isDataDescriptor(other.descriptor)) { if (hassio_addon_log_tab_hasDecorators(element) || hassio_addon_log_tab_hasDecorators(other)) { throw new ReferenceError("Duplicated methods (" + element.key + ") can't be decorated."); } other.descriptor = element.descriptor; } else { if (hassio_addon_log_tab_hasDecorators(element)) { if (hassio_addon_log_tab_hasDecorators(other)) { throw new ReferenceError("Decorators can't be placed on different accessors with for " + "the same property (" + element.key + ")."); } other.decorators = element.decorators; } hassio_addon_log_tab_coalesceGetterSetter(element, other); } } else { newElements.push(element); } } return newElements; }

function hassio_addon_log_tab_hasDecorators(element) { return element.decorators && element.decorators.length; }

function hassio_addon_log_tab_isDataDescriptor(desc) { return desc !== undefined && !(desc.value === undefined && desc.writable === undefined); }

function hassio_addon_log_tab_optionalCallableProperty(obj, name) { var value = obj[name]; if (value !== undefined && typeof value !== "function") { throw new TypeError("Expected '" + name + "' to be a function"); } return value; }

function hassio_addon_log_tab_toPropertyKey(arg) { var key = hassio_addon_log_tab_toPrimitive(arg, "string"); return hassio_addon_log_tab_typeof(key) === "symbol" ? key : String(key); }

function hassio_addon_log_tab_toPrimitive(input, hint) { if (hassio_addon_log_tab_typeof(input) !== "object" || input === null) return input; var prim = input[Symbol.toPrimitive]; if (prim !== undefined) { var res = prim.call(input, hint || "default"); if (hassio_addon_log_tab_typeof(res) !== "object") return res; throw new TypeError("@@toPrimitive must return a primitive value."); } return (hint === "string" ? String : Number)(input); }

function hassio_addon_log_tab_toArray(arr) { return hassio_addon_log_tab_arrayWithHoles(arr) || hassio_addon_log_tab_iterableToArray(arr) || hassio_addon_log_tab_unsupportedIterableToArray(arr) || hassio_addon_log_tab_nonIterableRest(); }

function hassio_addon_log_tab_nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function hassio_addon_log_tab_unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return hassio_addon_log_tab_arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(n); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return hassio_addon_log_tab_arrayLikeToArray(o, minLen); }

function hassio_addon_log_tab_arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function hassio_addon_log_tab_iterableToArray(iter) { if (typeof Symbol !== "undefined" && Symbol.iterator in Object(iter)) return Array.from(iter); }

function hassio_addon_log_tab_arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }







var hassio_addon_log_tab_HassioAddonLogDashboard = hassio_addon_log_tab_decorate([Object(lit_element["d" /* customElement */])("hassio-addon-log-tab")], function (_initialize, _LitElement) {
  var HassioAddonLogDashboard = /*#__PURE__*/function (_LitElement2) {
    hassio_addon_log_tab_inherits(HassioAddonLogDashboard, _LitElement2);

    var _super = hassio_addon_log_tab_createSuper(HassioAddonLogDashboard);

    function HassioAddonLogDashboard() {
      var _this;

      hassio_addon_log_tab_classCallCheck(this, HassioAddonLogDashboard);

      for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
        args[_key] = arguments[_key];
      }

      _this = _super.call.apply(_super, [this].concat(args));

      _initialize(hassio_addon_log_tab_assertThisInitialized(_this));

      return _this;
    }

    return HassioAddonLogDashboard;
  }(_LitElement);

  return {
    F: HassioAddonLogDashboard,
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
      key: "addon",
      value: void 0
    }, {
      kind: "method",
      key: "render",
      value: function render() {
        if (!this.addon) {
          return Object(lit_element["e" /* html */])(hassio_addon_log_tab_templateObject());
        }

        return Object(lit_element["e" /* html */])(hassio_addon_log_tab_templateObject2(), this.hass, this.addon);
      }
    }, {
      kind: "get",
      "static": true,
      key: "styles",
      value: function styles() {
        return [resources_styles["b" /* haStyle */], hassio_style["a" /* hassioStyle */], Object(lit_element["c" /* css */])(hassio_addon_log_tab_templateObject3())];
      }
    }]
  };
}, lit_element["a" /* LitElement */]);
// EXTERNAL MODULE: ./src/layouts/loading-screen.ts
var loading_screen = __webpack_require__(89);

// CONCATENATED MODULE: ./hassio/src/addon-view/documentation/hassio-addon-documentation-tab.ts
function hassio_addon_documentation_tab_typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { hassio_addon_documentation_tab_typeof = function _typeof(obj) { return typeof obj; }; } else { hassio_addon_documentation_tab_typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return hassio_addon_documentation_tab_typeof(obj); }

function hassio_addon_documentation_tab_templateObject6() {
  var data = hassio_addon_documentation_tab_taggedTemplateLiteral(["\n        paper-card {\n          display: block;\n        }\n        .content {\n          margin: auto;\n          padding: 8px;\n          max-width: 1024px;\n        }\n      "]);

  hassio_addon_documentation_tab_templateObject6 = function _templateObject6() {
    return data;
  };

  return data;
}

function hassio_addon_documentation_tab_templateObject5() {
  var data = hassio_addon_documentation_tab_taggedTemplateLiteral(["<loading-screen></loading-screen>"]);

  hassio_addon_documentation_tab_templateObject5 = function _templateObject5() {
    return data;
  };

  return data;
}

function hassio_addon_documentation_tab_templateObject4() {
  var data = hassio_addon_documentation_tab_taggedTemplateLiteral(["<ha-markdown .content=", "></ha-markdown>"]);

  hassio_addon_documentation_tab_templateObject4 = function _templateObject4() {
    return data;
  };

  return data;
}

function hassio_addon_documentation_tab_templateObject3() {
  var data = hassio_addon_documentation_tab_taggedTemplateLiteral([" <div class=\"errors\">", "</div> "]);

  hassio_addon_documentation_tab_templateObject3 = function _templateObject3() {
    return data;
  };

  return data;
}

function hassio_addon_documentation_tab_templateObject2() {
  var data = hassio_addon_documentation_tab_taggedTemplateLiteral(["\n      <div class=\"content\">\n        <paper-card>\n          ", "\n          <div class=\"card-content\">\n            ", "\n          </div>\n        </paper-card>\n      </div>\n    "]);

  hassio_addon_documentation_tab_templateObject2 = function _templateObject2() {
    return data;
  };

  return data;
}

function hassio_addon_documentation_tab_templateObject() {
  var data = hassio_addon_documentation_tab_taggedTemplateLiteral([" <paper-spinner-lite active></paper-spinner-lite> "]);

  hassio_addon_documentation_tab_templateObject = function _templateObject() {
    return data;
  };

  return data;
}

function hassio_addon_documentation_tab_taggedTemplateLiteral(strings, raw) { if (!raw) { raw = strings.slice(0); } return Object.freeze(Object.defineProperties(strings, { raw: { value: Object.freeze(raw) } })); }

function hassio_addon_documentation_tab_asyncGeneratorStep(gen, resolve, reject, _next, _throw, key, arg) { try { var info = gen[key](arg); var value = info.value; } catch (error) { reject(error); return; } if (info.done) { resolve(value); } else { Promise.resolve(value).then(_next, _throw); } }

function hassio_addon_documentation_tab_asyncToGenerator(fn) { return function () { var self = this, args = arguments; return new Promise(function (resolve, reject) { var gen = fn.apply(self, args); function _next(value) { hassio_addon_documentation_tab_asyncGeneratorStep(gen, resolve, reject, _next, _throw, "next", value); } function _throw(err) { hassio_addon_documentation_tab_asyncGeneratorStep(gen, resolve, reject, _next, _throw, "throw", err); } _next(undefined); }); }; }

function hassio_addon_documentation_tab_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function hassio_addon_documentation_tab_inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) hassio_addon_documentation_tab_setPrototypeOf(subClass, superClass); }

function hassio_addon_documentation_tab_setPrototypeOf(o, p) { hassio_addon_documentation_tab_setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return hassio_addon_documentation_tab_setPrototypeOf(o, p); }

function hassio_addon_documentation_tab_createSuper(Derived) { return function () { var Super = hassio_addon_documentation_tab_getPrototypeOf(Derived), result; if (hassio_addon_documentation_tab_isNativeReflectConstruct()) { var NewTarget = hassio_addon_documentation_tab_getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return hassio_addon_documentation_tab_possibleConstructorReturn(this, result); }; }

function hassio_addon_documentation_tab_possibleConstructorReturn(self, call) { if (call && (hassio_addon_documentation_tab_typeof(call) === "object" || typeof call === "function")) { return call; } return hassio_addon_documentation_tab_assertThisInitialized(self); }

function hassio_addon_documentation_tab_assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function hassio_addon_documentation_tab_isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Date.prototype.toString.call(Reflect.construct(Date, [], function () {})); return true; } catch (e) { return false; } }

function hassio_addon_documentation_tab_decorate(decorators, factory, superClass, mixins) { var api = hassio_addon_documentation_tab_getDecoratorsApi(); if (mixins) { for (var i = 0; i < mixins.length; i++) { api = mixins[i](api); } } var r = factory(function initialize(O) { api.initializeInstanceElements(O, decorated.elements); }, superClass); var decorated = api.decorateClass(hassio_addon_documentation_tab_coalesceClassElements(r.d.map(hassio_addon_documentation_tab_createElementDescriptor)), decorators); api.initializeClassElements(r.F, decorated.elements); return api.runClassFinishers(r.F, decorated.finishers); }

function hassio_addon_documentation_tab_getDecoratorsApi() { hassio_addon_documentation_tab_getDecoratorsApi = function _getDecoratorsApi() { return api; }; var api = { elementsDefinitionOrder: [["method"], ["field"]], initializeInstanceElements: function initializeInstanceElements(O, elements) { ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { if (element.kind === kind && element.placement === "own") { this.defineClassElement(O, element); } }, this); }, this); }, initializeClassElements: function initializeClassElements(F, elements) { var proto = F.prototype; ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { var placement = element.placement; if (element.kind === kind && (placement === "static" || placement === "prototype")) { var receiver = placement === "static" ? F : proto; this.defineClassElement(receiver, element); } }, this); }, this); }, defineClassElement: function defineClassElement(receiver, element) { var descriptor = element.descriptor; if (element.kind === "field") { var initializer = element.initializer; descriptor = { enumerable: descriptor.enumerable, writable: descriptor.writable, configurable: descriptor.configurable, value: initializer === void 0 ? void 0 : initializer.call(receiver) }; } Object.defineProperty(receiver, element.key, descriptor); }, decorateClass: function decorateClass(elements, decorators) { var newElements = []; var finishers = []; var placements = { "static": [], prototype: [], own: [] }; elements.forEach(function (element) { this.addElementPlacement(element, placements); }, this); elements.forEach(function (element) { if (!hassio_addon_documentation_tab_hasDecorators(element)) return newElements.push(element); var elementFinishersExtras = this.decorateElement(element, placements); newElements.push(elementFinishersExtras.element); newElements.push.apply(newElements, elementFinishersExtras.extras); finishers.push.apply(finishers, elementFinishersExtras.finishers); }, this); if (!decorators) { return { elements: newElements, finishers: finishers }; } var result = this.decorateConstructor(newElements, decorators); finishers.push.apply(finishers, result.finishers); result.finishers = finishers; return result; }, addElementPlacement: function addElementPlacement(element, placements, silent) { var keys = placements[element.placement]; if (!silent && keys.indexOf(element.key) !== -1) { throw new TypeError("Duplicated element (" + element.key + ")"); } keys.push(element.key); }, decorateElement: function decorateElement(element, placements) { var extras = []; var finishers = []; for (var decorators = element.decorators, i = decorators.length - 1; i >= 0; i--) { var keys = placements[element.placement]; keys.splice(keys.indexOf(element.key), 1); var elementObject = this.fromElementDescriptor(element); var elementFinisherExtras = this.toElementFinisherExtras((0, decorators[i])(elementObject) || elementObject); element = elementFinisherExtras.element; this.addElementPlacement(element, placements); if (elementFinisherExtras.finisher) { finishers.push(elementFinisherExtras.finisher); } var newExtras = elementFinisherExtras.extras; if (newExtras) { for (var j = 0; j < newExtras.length; j++) { this.addElementPlacement(newExtras[j], placements); } extras.push.apply(extras, newExtras); } } return { element: element, finishers: finishers, extras: extras }; }, decorateConstructor: function decorateConstructor(elements, decorators) { var finishers = []; for (var i = decorators.length - 1; i >= 0; i--) { var obj = this.fromClassDescriptor(elements); var elementsAndFinisher = this.toClassDescriptor((0, decorators[i])(obj) || obj); if (elementsAndFinisher.finisher !== undefined) { finishers.push(elementsAndFinisher.finisher); } if (elementsAndFinisher.elements !== undefined) { elements = elementsAndFinisher.elements; for (var j = 0; j < elements.length - 1; j++) { for (var k = j + 1; k < elements.length; k++) { if (elements[j].key === elements[k].key && elements[j].placement === elements[k].placement) { throw new TypeError("Duplicated element (" + elements[j].key + ")"); } } } } } return { elements: elements, finishers: finishers }; }, fromElementDescriptor: function fromElementDescriptor(element) { var obj = { kind: element.kind, key: element.key, placement: element.placement, descriptor: element.descriptor }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); if (element.kind === "field") obj.initializer = element.initializer; return obj; }, toElementDescriptors: function toElementDescriptors(elementObjects) { if (elementObjects === undefined) return; return hassio_addon_documentation_tab_toArray(elementObjects).map(function (elementObject) { var element = this.toElementDescriptor(elementObject); this.disallowProperty(elementObject, "finisher", "An element descriptor"); this.disallowProperty(elementObject, "extras", "An element descriptor"); return element; }, this); }, toElementDescriptor: function toElementDescriptor(elementObject) { var kind = String(elementObject.kind); if (kind !== "method" && kind !== "field") { throw new TypeError('An element descriptor\'s .kind property must be either "method" or' + ' "field", but a decorator created an element descriptor with' + ' .kind "' + kind + '"'); } var key = hassio_addon_documentation_tab_toPropertyKey(elementObject.key); var placement = String(elementObject.placement); if (placement !== "static" && placement !== "prototype" && placement !== "own") { throw new TypeError('An element descriptor\'s .placement property must be one of "static",' + ' "prototype" or "own", but a decorator created an element descriptor' + ' with .placement "' + placement + '"'); } var descriptor = elementObject.descriptor; this.disallowProperty(elementObject, "elements", "An element descriptor"); var element = { kind: kind, key: key, placement: placement, descriptor: Object.assign({}, descriptor) }; if (kind !== "field") { this.disallowProperty(elementObject, "initializer", "A method descriptor"); } else { this.disallowProperty(descriptor, "get", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "set", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "value", "The property descriptor of a field descriptor"); element.initializer = elementObject.initializer; } return element; }, toElementFinisherExtras: function toElementFinisherExtras(elementObject) { var element = this.toElementDescriptor(elementObject); var finisher = hassio_addon_documentation_tab_optionalCallableProperty(elementObject, "finisher"); var extras = this.toElementDescriptors(elementObject.extras); return { element: element, finisher: finisher, extras: extras }; }, fromClassDescriptor: function fromClassDescriptor(elements) { var obj = { kind: "class", elements: elements.map(this.fromElementDescriptor, this) }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); return obj; }, toClassDescriptor: function toClassDescriptor(obj) { var kind = String(obj.kind); if (kind !== "class") { throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator' + ' created a class descriptor with .kind "' + kind + '"'); } this.disallowProperty(obj, "key", "A class descriptor"); this.disallowProperty(obj, "placement", "A class descriptor"); this.disallowProperty(obj, "descriptor", "A class descriptor"); this.disallowProperty(obj, "initializer", "A class descriptor"); this.disallowProperty(obj, "extras", "A class descriptor"); var finisher = hassio_addon_documentation_tab_optionalCallableProperty(obj, "finisher"); var elements = this.toElementDescriptors(obj.elements); return { elements: elements, finisher: finisher }; }, runClassFinishers: function runClassFinishers(constructor, finishers) { for (var i = 0; i < finishers.length; i++) { var newConstructor = (0, finishers[i])(constructor); if (newConstructor !== undefined) { if (typeof newConstructor !== "function") { throw new TypeError("Finishers must return a constructor."); } constructor = newConstructor; } } return constructor; }, disallowProperty: function disallowProperty(obj, name, objectType) { if (obj[name] !== undefined) { throw new TypeError(objectType + " can't have a ." + name + " property."); } } }; return api; }

function hassio_addon_documentation_tab_createElementDescriptor(def) { var key = hassio_addon_documentation_tab_toPropertyKey(def.key); var descriptor; if (def.kind === "method") { descriptor = { value: def.value, writable: true, configurable: true, enumerable: false }; } else if (def.kind === "get") { descriptor = { get: def.value, configurable: true, enumerable: false }; } else if (def.kind === "set") { descriptor = { set: def.value, configurable: true, enumerable: false }; } else if (def.kind === "field") { descriptor = { configurable: true, writable: true, enumerable: true }; } var element = { kind: def.kind === "field" ? "field" : "method", key: key, placement: def["static"] ? "static" : def.kind === "field" ? "own" : "prototype", descriptor: descriptor }; if (def.decorators) element.decorators = def.decorators; if (def.kind === "field") element.initializer = def.value; return element; }

function hassio_addon_documentation_tab_coalesceGetterSetter(element, other) { if (element.descriptor.get !== undefined) { other.descriptor.get = element.descriptor.get; } else { other.descriptor.set = element.descriptor.set; } }

function hassio_addon_documentation_tab_coalesceClassElements(elements) { var newElements = []; var isSameElement = function isSameElement(other) { return other.kind === "method" && other.key === element.key && other.placement === element.placement; }; for (var i = 0; i < elements.length; i++) { var element = elements[i]; var other; if (element.kind === "method" && (other = newElements.find(isSameElement))) { if (hassio_addon_documentation_tab_isDataDescriptor(element.descriptor) || hassio_addon_documentation_tab_isDataDescriptor(other.descriptor)) { if (hassio_addon_documentation_tab_hasDecorators(element) || hassio_addon_documentation_tab_hasDecorators(other)) { throw new ReferenceError("Duplicated methods (" + element.key + ") can't be decorated."); } other.descriptor = element.descriptor; } else { if (hassio_addon_documentation_tab_hasDecorators(element)) { if (hassio_addon_documentation_tab_hasDecorators(other)) { throw new ReferenceError("Decorators can't be placed on different accessors with for " + "the same property (" + element.key + ")."); } other.decorators = element.decorators; } hassio_addon_documentation_tab_coalesceGetterSetter(element, other); } } else { newElements.push(element); } } return newElements; }

function hassio_addon_documentation_tab_hasDecorators(element) { return element.decorators && element.decorators.length; }

function hassio_addon_documentation_tab_isDataDescriptor(desc) { return desc !== undefined && !(desc.value === undefined && desc.writable === undefined); }

function hassio_addon_documentation_tab_optionalCallableProperty(obj, name) { var value = obj[name]; if (value !== undefined && typeof value !== "function") { throw new TypeError("Expected '" + name + "' to be a function"); } return value; }

function hassio_addon_documentation_tab_toPropertyKey(arg) { var key = hassio_addon_documentation_tab_toPrimitive(arg, "string"); return hassio_addon_documentation_tab_typeof(key) === "symbol" ? key : String(key); }

function hassio_addon_documentation_tab_toPrimitive(input, hint) { if (hassio_addon_documentation_tab_typeof(input) !== "object" || input === null) return input; var prim = input[Symbol.toPrimitive]; if (prim !== undefined) { var res = prim.call(input, hint || "default"); if (hassio_addon_documentation_tab_typeof(res) !== "object") return res; throw new TypeError("@@toPrimitive must return a primitive value."); } return (hint === "string" ? String : Number)(input); }

function hassio_addon_documentation_tab_toArray(arr) { return hassio_addon_documentation_tab_arrayWithHoles(arr) || hassio_addon_documentation_tab_iterableToArray(arr) || hassio_addon_documentation_tab_unsupportedIterableToArray(arr) || hassio_addon_documentation_tab_nonIterableRest(); }

function hassio_addon_documentation_tab_nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function hassio_addon_documentation_tab_unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return hassio_addon_documentation_tab_arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(n); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return hassio_addon_documentation_tab_arrayLikeToArray(o, minLen); }

function hassio_addon_documentation_tab_arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function hassio_addon_documentation_tab_iterableToArray(iter) { if (typeof Symbol !== "undefined" && Symbol.iterator in Object(iter)) return Array.from(iter); }

function hassio_addon_documentation_tab_arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }

function hassio_addon_documentation_tab_get(target, property, receiver) { if (typeof Reflect !== "undefined" && Reflect.get) { hassio_addon_documentation_tab_get = Reflect.get; } else { hassio_addon_documentation_tab_get = function _get(target, property, receiver) { var base = hassio_addon_documentation_tab_superPropBase(target, property); if (!base) return; var desc = Object.getOwnPropertyDescriptor(base, property); if (desc.get) { return desc.get.call(receiver); } return desc.value; }; } return hassio_addon_documentation_tab_get(target, property, receiver || target); }

function hassio_addon_documentation_tab_superPropBase(object, property) { while (!Object.prototype.hasOwnProperty.call(object, property)) { object = hassio_addon_documentation_tab_getPrototypeOf(object); if (object === null) break; } return object; }

function hassio_addon_documentation_tab_getPrototypeOf(o) { hassio_addon_documentation_tab_getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return hassio_addon_documentation_tab_getPrototypeOf(o); }










var hassio_addon_documentation_tab_HassioAddonDocumentationDashboard = hassio_addon_documentation_tab_decorate([Object(lit_element["d" /* customElement */])("hassio-addon-documentation-tab")], function (_initialize, _LitElement) {
  var HassioAddonDocumentationDashboard = /*#__PURE__*/function (_LitElement2) {
    hassio_addon_documentation_tab_inherits(HassioAddonDocumentationDashboard, _LitElement2);

    var _super = hassio_addon_documentation_tab_createSuper(HassioAddonDocumentationDashboard);

    function HassioAddonDocumentationDashboard() {
      var _this;

      hassio_addon_documentation_tab_classCallCheck(this, HassioAddonDocumentationDashboard);

      for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
        args[_key] = arguments[_key];
      }

      _this = _super.call.apply(_super, [this].concat(args));

      _initialize(hassio_addon_documentation_tab_assertThisInitialized(_this));

      return _this;
    }

    return HassioAddonDocumentationDashboard;
  }(_LitElement);

  return {
    F: HassioAddonDocumentationDashboard,
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
      key: "addon",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "_error",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "_content",
      value: void 0
    }, {
      kind: "method",
      key: "connectedCallback",
      value: function () {
        var _connectedCallback = hassio_addon_documentation_tab_asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee() {
          return regeneratorRuntime.wrap(function _callee$(_context) {
            while (1) {
              switch (_context.prev = _context.next) {
                case 0:
                  hassio_addon_documentation_tab_get(hassio_addon_documentation_tab_getPrototypeOf(HassioAddonDocumentationDashboard.prototype), "connectedCallback", this).call(this);

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
        if (!this.addon) {
          return Object(lit_element["e" /* html */])(hassio_addon_documentation_tab_templateObject());
        }

        return Object(lit_element["e" /* html */])(hassio_addon_documentation_tab_templateObject2(), this._error ? Object(lit_element["e" /* html */])(hassio_addon_documentation_tab_templateObject3(), this._error) : "", this._content ? Object(lit_element["e" /* html */])(hassio_addon_documentation_tab_templateObject4(), this._content) : Object(lit_element["e" /* html */])(hassio_addon_documentation_tab_templateObject5()));
      }
    }, {
      kind: "get",
      "static": true,
      key: "styles",
      value: function styles() {
        return [resources_styles["b" /* haStyle */], hassio_style["a" /* hassioStyle */], Object(lit_element["c" /* css */])(hassio_addon_documentation_tab_templateObject6())];
      }
    }, {
      kind: "method",
      key: "_loadData",
      value: function () {
        var _loadData2 = hassio_addon_documentation_tab_asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee2() {
          var _err$body;

          return regeneratorRuntime.wrap(function _callee2$(_context2) {
            while (1) {
              switch (_context2.prev = _context2.next) {
                case 0:
                  this._error = undefined;
                  _context2.prev = 1;
                  _context2.next = 4;
                  return Object(hassio_addon["b" /* fetchHassioAddonDocumentation */])(this.hass, this.addon.slug);

                case 4:
                  this._content = _context2.sent;
                  _context2.next = 10;
                  break;

                case 7:
                  _context2.prev = 7;
                  _context2.t0 = _context2["catch"](1);
                  this._error = "Failed to get addon documentation, ".concat(((_err$body = _context2.t0.body) === null || _err$body === void 0 ? void 0 : _err$body.message) || _context2.t0);

                case 10:
                case "end":
                  return _context2.stop();
              }
            }
          }, _callee2, this, [[1, 7]]);
        }));

        function _loadData() {
          return _loadData2.apply(this, arguments);
        }

        return _loadData;
      }()
    }]
  };
}, lit_element["a" /* LitElement */]);
// CONCATENATED MODULE: ./hassio/src/addon-view/hassio-addon-router.ts
function hassio_addon_router_typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { hassio_addon_router_typeof = function _typeof(obj) { return typeof obj; }; } else { hassio_addon_router_typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return hassio_addon_router_typeof(obj); }

function hassio_addon_router_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function hassio_addon_router_inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) hassio_addon_router_setPrototypeOf(subClass, superClass); }

function hassio_addon_router_setPrototypeOf(o, p) { hassio_addon_router_setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return hassio_addon_router_setPrototypeOf(o, p); }

function hassio_addon_router_createSuper(Derived) { return function () { var Super = hassio_addon_router_getPrototypeOf(Derived), result; if (hassio_addon_router_isNativeReflectConstruct()) { var NewTarget = hassio_addon_router_getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return hassio_addon_router_possibleConstructorReturn(this, result); }; }

function hassio_addon_router_possibleConstructorReturn(self, call) { if (call && (hassio_addon_router_typeof(call) === "object" || typeof call === "function")) { return call; } return hassio_addon_router_assertThisInitialized(self); }

function hassio_addon_router_assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function hassio_addon_router_isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Date.prototype.toString.call(Reflect.construct(Date, [], function () {})); return true; } catch (e) { return false; } }

function hassio_addon_router_getPrototypeOf(o) { hassio_addon_router_getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return hassio_addon_router_getPrototypeOf(o); }

function hassio_addon_router_decorate(decorators, factory, superClass, mixins) { var api = hassio_addon_router_getDecoratorsApi(); if (mixins) { for (var i = 0; i < mixins.length; i++) { api = mixins[i](api); } } var r = factory(function initialize(O) { api.initializeInstanceElements(O, decorated.elements); }, superClass); var decorated = api.decorateClass(hassio_addon_router_coalesceClassElements(r.d.map(hassio_addon_router_createElementDescriptor)), decorators); api.initializeClassElements(r.F, decorated.elements); return api.runClassFinishers(r.F, decorated.finishers); }

function hassio_addon_router_getDecoratorsApi() { hassio_addon_router_getDecoratorsApi = function _getDecoratorsApi() { return api; }; var api = { elementsDefinitionOrder: [["method"], ["field"]], initializeInstanceElements: function initializeInstanceElements(O, elements) { ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { if (element.kind === kind && element.placement === "own") { this.defineClassElement(O, element); } }, this); }, this); }, initializeClassElements: function initializeClassElements(F, elements) { var proto = F.prototype; ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { var placement = element.placement; if (element.kind === kind && (placement === "static" || placement === "prototype")) { var receiver = placement === "static" ? F : proto; this.defineClassElement(receiver, element); } }, this); }, this); }, defineClassElement: function defineClassElement(receiver, element) { var descriptor = element.descriptor; if (element.kind === "field") { var initializer = element.initializer; descriptor = { enumerable: descriptor.enumerable, writable: descriptor.writable, configurable: descriptor.configurable, value: initializer === void 0 ? void 0 : initializer.call(receiver) }; } Object.defineProperty(receiver, element.key, descriptor); }, decorateClass: function decorateClass(elements, decorators) { var newElements = []; var finishers = []; var placements = { "static": [], prototype: [], own: [] }; elements.forEach(function (element) { this.addElementPlacement(element, placements); }, this); elements.forEach(function (element) { if (!hassio_addon_router_hasDecorators(element)) return newElements.push(element); var elementFinishersExtras = this.decorateElement(element, placements); newElements.push(elementFinishersExtras.element); newElements.push.apply(newElements, elementFinishersExtras.extras); finishers.push.apply(finishers, elementFinishersExtras.finishers); }, this); if (!decorators) { return { elements: newElements, finishers: finishers }; } var result = this.decorateConstructor(newElements, decorators); finishers.push.apply(finishers, result.finishers); result.finishers = finishers; return result; }, addElementPlacement: function addElementPlacement(element, placements, silent) { var keys = placements[element.placement]; if (!silent && keys.indexOf(element.key) !== -1) { throw new TypeError("Duplicated element (" + element.key + ")"); } keys.push(element.key); }, decorateElement: function decorateElement(element, placements) { var extras = []; var finishers = []; for (var decorators = element.decorators, i = decorators.length - 1; i >= 0; i--) { var keys = placements[element.placement]; keys.splice(keys.indexOf(element.key), 1); var elementObject = this.fromElementDescriptor(element); var elementFinisherExtras = this.toElementFinisherExtras((0, decorators[i])(elementObject) || elementObject); element = elementFinisherExtras.element; this.addElementPlacement(element, placements); if (elementFinisherExtras.finisher) { finishers.push(elementFinisherExtras.finisher); } var newExtras = elementFinisherExtras.extras; if (newExtras) { for (var j = 0; j < newExtras.length; j++) { this.addElementPlacement(newExtras[j], placements); } extras.push.apply(extras, newExtras); } } return { element: element, finishers: finishers, extras: extras }; }, decorateConstructor: function decorateConstructor(elements, decorators) { var finishers = []; for (var i = decorators.length - 1; i >= 0; i--) { var obj = this.fromClassDescriptor(elements); var elementsAndFinisher = this.toClassDescriptor((0, decorators[i])(obj) || obj); if (elementsAndFinisher.finisher !== undefined) { finishers.push(elementsAndFinisher.finisher); } if (elementsAndFinisher.elements !== undefined) { elements = elementsAndFinisher.elements; for (var j = 0; j < elements.length - 1; j++) { for (var k = j + 1; k < elements.length; k++) { if (elements[j].key === elements[k].key && elements[j].placement === elements[k].placement) { throw new TypeError("Duplicated element (" + elements[j].key + ")"); } } } } } return { elements: elements, finishers: finishers }; }, fromElementDescriptor: function fromElementDescriptor(element) { var obj = { kind: element.kind, key: element.key, placement: element.placement, descriptor: element.descriptor }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); if (element.kind === "field") obj.initializer = element.initializer; return obj; }, toElementDescriptors: function toElementDescriptors(elementObjects) { if (elementObjects === undefined) return; return hassio_addon_router_toArray(elementObjects).map(function (elementObject) { var element = this.toElementDescriptor(elementObject); this.disallowProperty(elementObject, "finisher", "An element descriptor"); this.disallowProperty(elementObject, "extras", "An element descriptor"); return element; }, this); }, toElementDescriptor: function toElementDescriptor(elementObject) { var kind = String(elementObject.kind); if (kind !== "method" && kind !== "field") { throw new TypeError('An element descriptor\'s .kind property must be either "method" or' + ' "field", but a decorator created an element descriptor with' + ' .kind "' + kind + '"'); } var key = hassio_addon_router_toPropertyKey(elementObject.key); var placement = String(elementObject.placement); if (placement !== "static" && placement !== "prototype" && placement !== "own") { throw new TypeError('An element descriptor\'s .placement property must be one of "static",' + ' "prototype" or "own", but a decorator created an element descriptor' + ' with .placement "' + placement + '"'); } var descriptor = elementObject.descriptor; this.disallowProperty(elementObject, "elements", "An element descriptor"); var element = { kind: kind, key: key, placement: placement, descriptor: Object.assign({}, descriptor) }; if (kind !== "field") { this.disallowProperty(elementObject, "initializer", "A method descriptor"); } else { this.disallowProperty(descriptor, "get", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "set", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "value", "The property descriptor of a field descriptor"); element.initializer = elementObject.initializer; } return element; }, toElementFinisherExtras: function toElementFinisherExtras(elementObject) { var element = this.toElementDescriptor(elementObject); var finisher = hassio_addon_router_optionalCallableProperty(elementObject, "finisher"); var extras = this.toElementDescriptors(elementObject.extras); return { element: element, finisher: finisher, extras: extras }; }, fromClassDescriptor: function fromClassDescriptor(elements) { var obj = { kind: "class", elements: elements.map(this.fromElementDescriptor, this) }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); return obj; }, toClassDescriptor: function toClassDescriptor(obj) { var kind = String(obj.kind); if (kind !== "class") { throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator' + ' created a class descriptor with .kind "' + kind + '"'); } this.disallowProperty(obj, "key", "A class descriptor"); this.disallowProperty(obj, "placement", "A class descriptor"); this.disallowProperty(obj, "descriptor", "A class descriptor"); this.disallowProperty(obj, "initializer", "A class descriptor"); this.disallowProperty(obj, "extras", "A class descriptor"); var finisher = hassio_addon_router_optionalCallableProperty(obj, "finisher"); var elements = this.toElementDescriptors(obj.elements); return { elements: elements, finisher: finisher }; }, runClassFinishers: function runClassFinishers(constructor, finishers) { for (var i = 0; i < finishers.length; i++) { var newConstructor = (0, finishers[i])(constructor); if (newConstructor !== undefined) { if (typeof newConstructor !== "function") { throw new TypeError("Finishers must return a constructor."); } constructor = newConstructor; } } return constructor; }, disallowProperty: function disallowProperty(obj, name, objectType) { if (obj[name] !== undefined) { throw new TypeError(objectType + " can't have a ." + name + " property."); } } }; return api; }

function hassio_addon_router_createElementDescriptor(def) { var key = hassio_addon_router_toPropertyKey(def.key); var descriptor; if (def.kind === "method") { descriptor = { value: def.value, writable: true, configurable: true, enumerable: false }; } else if (def.kind === "get") { descriptor = { get: def.value, configurable: true, enumerable: false }; } else if (def.kind === "set") { descriptor = { set: def.value, configurable: true, enumerable: false }; } else if (def.kind === "field") { descriptor = { configurable: true, writable: true, enumerable: true }; } var element = { kind: def.kind === "field" ? "field" : "method", key: key, placement: def["static"] ? "static" : def.kind === "field" ? "own" : "prototype", descriptor: descriptor }; if (def.decorators) element.decorators = def.decorators; if (def.kind === "field") element.initializer = def.value; return element; }

function hassio_addon_router_coalesceGetterSetter(element, other) { if (element.descriptor.get !== undefined) { other.descriptor.get = element.descriptor.get; } else { other.descriptor.set = element.descriptor.set; } }

function hassio_addon_router_coalesceClassElements(elements) { var newElements = []; var isSameElement = function isSameElement(other) { return other.kind === "method" && other.key === element.key && other.placement === element.placement; }; for (var i = 0; i < elements.length; i++) { var element = elements[i]; var other; if (element.kind === "method" && (other = newElements.find(isSameElement))) { if (hassio_addon_router_isDataDescriptor(element.descriptor) || hassio_addon_router_isDataDescriptor(other.descriptor)) { if (hassio_addon_router_hasDecorators(element) || hassio_addon_router_hasDecorators(other)) { throw new ReferenceError("Duplicated methods (" + element.key + ") can't be decorated."); } other.descriptor = element.descriptor; } else { if (hassio_addon_router_hasDecorators(element)) { if (hassio_addon_router_hasDecorators(other)) { throw new ReferenceError("Decorators can't be placed on different accessors with for " + "the same property (" + element.key + ")."); } other.decorators = element.decorators; } hassio_addon_router_coalesceGetterSetter(element, other); } } else { newElements.push(element); } } return newElements; }

function hassio_addon_router_hasDecorators(element) { return element.decorators && element.decorators.length; }

function hassio_addon_router_isDataDescriptor(desc) { return desc !== undefined && !(desc.value === undefined && desc.writable === undefined); }

function hassio_addon_router_optionalCallableProperty(obj, name) { var value = obj[name]; if (value !== undefined && typeof value !== "function") { throw new TypeError("Expected '" + name + "' to be a function"); } return value; }

function hassio_addon_router_toPropertyKey(arg) { var key = hassio_addon_router_toPrimitive(arg, "string"); return hassio_addon_router_typeof(key) === "symbol" ? key : String(key); }

function hassio_addon_router_toPrimitive(input, hint) { if (hassio_addon_router_typeof(input) !== "object" || input === null) return input; var prim = input[Symbol.toPrimitive]; if (prim !== undefined) { var res = prim.call(input, hint || "default"); if (hassio_addon_router_typeof(res) !== "object") return res; throw new TypeError("@@toPrimitive must return a primitive value."); } return (hint === "string" ? String : Number)(input); }

function hassio_addon_router_toArray(arr) { return hassio_addon_router_arrayWithHoles(arr) || hassio_addon_router_iterableToArray(arr) || hassio_addon_router_unsupportedIterableToArray(arr) || hassio_addon_router_nonIterableRest(); }

function hassio_addon_router_nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function hassio_addon_router_unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return hassio_addon_router_arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(n); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return hassio_addon_router_arrayLikeToArray(o, minLen); }

function hassio_addon_router_arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function hassio_addon_router_iterableToArray(iter) { if (typeof Symbol !== "undefined" && Symbol.iterator in Object(iter)) return Array.from(iter); }

function hassio_addon_router_arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }



// Don't codesplit the others, because it breaks the UI when pushed to a Pi





var hassio_addon_router_HassioAddonRouter = hassio_addon_router_decorate([Object(lit_element["d" /* customElement */])("hassio-addon-router")], function (_initialize, _HassRouterPage) {
  var HassioAddonRouter = /*#__PURE__*/function (_HassRouterPage2) {
    hassio_addon_router_inherits(HassioAddonRouter, _HassRouterPage2);

    var _super = hassio_addon_router_createSuper(HassioAddonRouter);

    function HassioAddonRouter() {
      var _this;

      hassio_addon_router_classCallCheck(this, HassioAddonRouter);

      for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
        args[_key] = arguments[_key];
      }

      _this = _super.call.apply(_super, [this].concat(args));

      _initialize(hassio_addon_router_assertThisInitialized(_this));

      return _this;
    }

    return HassioAddonRouter;
  }(_HassRouterPage);

  return {
    F: HassioAddonRouter,
    d: [{
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])({
        type: Boolean
      })],
      key: "narrow",
      value: function value() {
        return false;
      }
    }, {
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
      key: "addon",
      value: void 0
    }, {
      kind: "field",
      key: "routerOptions",
      value: function value() {
        return {
          defaultPage: "info",
          showLoading: true,
          routes: {
            info: {
              tag: "hassio-addon-info-tab"
            },
            documentation: {
              tag: "hassio-addon-documentation-tab"
            },
            config: {
              tag: "hassio-addon-config-tab"
            },
            logs: {
              tag: "hassio-addon-log-tab"
            }
          }
        };
      }
    }, {
      kind: "method",
      key: "updatePageEl",
      value: function updatePageEl(el) {
        el.route = this.routeTail;
        el.hass = this.hass;
        el.addon = this.addon;
        el.narrow = this.narrow;
      }
    }]
  };
}, hass_router_page["a" /* HassRouterPage */]);
// CONCATENATED MODULE: ./hassio/src/addon-view/hassio-addon-dashboard.ts
function hassio_addon_dashboard_typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { hassio_addon_dashboard_typeof = function _typeof(obj) { return typeof obj; }; } else { hassio_addon_dashboard_typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return hassio_addon_dashboard_typeof(obj); }

function hassio_addon_dashboard_asyncGeneratorStep(gen, resolve, reject, _next, _throw, key, arg) { try { var info = gen[key](arg); var value = info.value; } catch (error) { reject(error); return; } if (info.done) { resolve(value); } else { Promise.resolve(value).then(_next, _throw); } }

function hassio_addon_dashboard_asyncToGenerator(fn) { return function () { var self = this, args = arguments; return new Promise(function (resolve, reject) { var gen = fn.apply(self, args); function _next(value) { hassio_addon_dashboard_asyncGeneratorStep(gen, resolve, reject, _next, _throw, "next", value); } function _throw(err) { hassio_addon_dashboard_asyncGeneratorStep(gen, resolve, reject, _next, _throw, "throw", err); } _next(undefined); }); }; }

function hassio_addon_dashboard_templateObject3() {
  var data = hassio_addon_dashboard_taggedTemplateLiteral(["\n        :host {\n          color: var(--primary-text-color);\n          --paper-card-header-color: var(--primary-text-color);\n        }\n        .content {\n          padding: 24px 0 32px;\n          display: flex;\n          flex-direction: column;\n          align-items: center;\n        }\n        hassio-addon-info,\n        hassio-addon-network,\n        hassio-addon-audio,\n        hassio-addon-config {\n          margin-bottom: 24px;\n          width: 600px;\n        }\n        hassio-addon-logs {\n          max-width: calc(100% - 8px);\n          min-width: 600px;\n        }\n        @media only screen and (max-width: 600px) {\n          hassio-addon-info,\n          hassio-addon-network,\n          hassio-addon-audio,\n          hassio-addon-config,\n          hassio-addon-logs {\n            max-width: 100%;\n            min-width: 100%;\n          }\n        }\n      "]);

  hassio_addon_dashboard_templateObject3 = function _templateObject3() {
    return data;
  };

  return data;
}

function hassio_addon_dashboard_templateObject2() {
  var data = hassio_addon_dashboard_taggedTemplateLiteral(["\n      <hass-tabs-subpage\n        .hass=", "\n        .narrow=", "\n        .backPath=", "\n        .route=", "\n        hassio\n        .tabs=", "\n      >\n        <span slot=\"header\">", "</span>\n        <hassio-addon-router\n          .route=", "\n          .narrow=", "\n          .hass=", "\n          .addon=", "\n        ></hassio-addon-router>\n      </hass-tabs-subpage>\n    "]);

  hassio_addon_dashboard_templateObject2 = function _templateObject2() {
    return data;
  };

  return data;
}

function hassio_addon_dashboard_templateObject() {
  var data = hassio_addon_dashboard_taggedTemplateLiteral([" <paper-spinner-lite active></paper-spinner-lite> "]);

  hassio_addon_dashboard_templateObject = function _templateObject() {
    return data;
  };

  return data;
}

function hassio_addon_dashboard_taggedTemplateLiteral(strings, raw) { if (!raw) { raw = strings.slice(0); } return Object.freeze(Object.defineProperties(strings, { raw: { value: Object.freeze(raw) } })); }

function hassio_addon_dashboard_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function hassio_addon_dashboard_inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) hassio_addon_dashboard_setPrototypeOf(subClass, superClass); }

function hassio_addon_dashboard_setPrototypeOf(o, p) { hassio_addon_dashboard_setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return hassio_addon_dashboard_setPrototypeOf(o, p); }

function hassio_addon_dashboard_createSuper(Derived) { return function () { var Super = hassio_addon_dashboard_getPrototypeOf(Derived), result; if (hassio_addon_dashboard_isNativeReflectConstruct()) { var NewTarget = hassio_addon_dashboard_getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return hassio_addon_dashboard_possibleConstructorReturn(this, result); }; }

function hassio_addon_dashboard_possibleConstructorReturn(self, call) { if (call && (hassio_addon_dashboard_typeof(call) === "object" || typeof call === "function")) { return call; } return hassio_addon_dashboard_assertThisInitialized(self); }

function hassio_addon_dashboard_assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function hassio_addon_dashboard_isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Date.prototype.toString.call(Reflect.construct(Date, [], function () {})); return true; } catch (e) { return false; } }

function hassio_addon_dashboard_getPrototypeOf(o) { hassio_addon_dashboard_getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return hassio_addon_dashboard_getPrototypeOf(o); }

function hassio_addon_dashboard_decorate(decorators, factory, superClass, mixins) { var api = hassio_addon_dashboard_getDecoratorsApi(); if (mixins) { for (var i = 0; i < mixins.length; i++) { api = mixins[i](api); } } var r = factory(function initialize(O) { api.initializeInstanceElements(O, decorated.elements); }, superClass); var decorated = api.decorateClass(hassio_addon_dashboard_coalesceClassElements(r.d.map(hassio_addon_dashboard_createElementDescriptor)), decorators); api.initializeClassElements(r.F, decorated.elements); return api.runClassFinishers(r.F, decorated.finishers); }

function hassio_addon_dashboard_getDecoratorsApi() { hassio_addon_dashboard_getDecoratorsApi = function _getDecoratorsApi() { return api; }; var api = { elementsDefinitionOrder: [["method"], ["field"]], initializeInstanceElements: function initializeInstanceElements(O, elements) { ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { if (element.kind === kind && element.placement === "own") { this.defineClassElement(O, element); } }, this); }, this); }, initializeClassElements: function initializeClassElements(F, elements) { var proto = F.prototype; ["method", "field"].forEach(function (kind) { elements.forEach(function (element) { var placement = element.placement; if (element.kind === kind && (placement === "static" || placement === "prototype")) { var receiver = placement === "static" ? F : proto; this.defineClassElement(receiver, element); } }, this); }, this); }, defineClassElement: function defineClassElement(receiver, element) { var descriptor = element.descriptor; if (element.kind === "field") { var initializer = element.initializer; descriptor = { enumerable: descriptor.enumerable, writable: descriptor.writable, configurable: descriptor.configurable, value: initializer === void 0 ? void 0 : initializer.call(receiver) }; } Object.defineProperty(receiver, element.key, descriptor); }, decorateClass: function decorateClass(elements, decorators) { var newElements = []; var finishers = []; var placements = { "static": [], prototype: [], own: [] }; elements.forEach(function (element) { this.addElementPlacement(element, placements); }, this); elements.forEach(function (element) { if (!hassio_addon_dashboard_hasDecorators(element)) return newElements.push(element); var elementFinishersExtras = this.decorateElement(element, placements); newElements.push(elementFinishersExtras.element); newElements.push.apply(newElements, elementFinishersExtras.extras); finishers.push.apply(finishers, elementFinishersExtras.finishers); }, this); if (!decorators) { return { elements: newElements, finishers: finishers }; } var result = this.decorateConstructor(newElements, decorators); finishers.push.apply(finishers, result.finishers); result.finishers = finishers; return result; }, addElementPlacement: function addElementPlacement(element, placements, silent) { var keys = placements[element.placement]; if (!silent && keys.indexOf(element.key) !== -1) { throw new TypeError("Duplicated element (" + element.key + ")"); } keys.push(element.key); }, decorateElement: function decorateElement(element, placements) { var extras = []; var finishers = []; for (var decorators = element.decorators, i = decorators.length - 1; i >= 0; i--) { var keys = placements[element.placement]; keys.splice(keys.indexOf(element.key), 1); var elementObject = this.fromElementDescriptor(element); var elementFinisherExtras = this.toElementFinisherExtras((0, decorators[i])(elementObject) || elementObject); element = elementFinisherExtras.element; this.addElementPlacement(element, placements); if (elementFinisherExtras.finisher) { finishers.push(elementFinisherExtras.finisher); } var newExtras = elementFinisherExtras.extras; if (newExtras) { for (var j = 0; j < newExtras.length; j++) { this.addElementPlacement(newExtras[j], placements); } extras.push.apply(extras, newExtras); } } return { element: element, finishers: finishers, extras: extras }; }, decorateConstructor: function decorateConstructor(elements, decorators) { var finishers = []; for (var i = decorators.length - 1; i >= 0; i--) { var obj = this.fromClassDescriptor(elements); var elementsAndFinisher = this.toClassDescriptor((0, decorators[i])(obj) || obj); if (elementsAndFinisher.finisher !== undefined) { finishers.push(elementsAndFinisher.finisher); } if (elementsAndFinisher.elements !== undefined) { elements = elementsAndFinisher.elements; for (var j = 0; j < elements.length - 1; j++) { for (var k = j + 1; k < elements.length; k++) { if (elements[j].key === elements[k].key && elements[j].placement === elements[k].placement) { throw new TypeError("Duplicated element (" + elements[j].key + ")"); } } } } } return { elements: elements, finishers: finishers }; }, fromElementDescriptor: function fromElementDescriptor(element) { var obj = { kind: element.kind, key: element.key, placement: element.placement, descriptor: element.descriptor }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); if (element.kind === "field") obj.initializer = element.initializer; return obj; }, toElementDescriptors: function toElementDescriptors(elementObjects) { if (elementObjects === undefined) return; return hassio_addon_dashboard_toArray(elementObjects).map(function (elementObject) { var element = this.toElementDescriptor(elementObject); this.disallowProperty(elementObject, "finisher", "An element descriptor"); this.disallowProperty(elementObject, "extras", "An element descriptor"); return element; }, this); }, toElementDescriptor: function toElementDescriptor(elementObject) { var kind = String(elementObject.kind); if (kind !== "method" && kind !== "field") { throw new TypeError('An element descriptor\'s .kind property must be either "method" or' + ' "field", but a decorator created an element descriptor with' + ' .kind "' + kind + '"'); } var key = hassio_addon_dashboard_toPropertyKey(elementObject.key); var placement = String(elementObject.placement); if (placement !== "static" && placement !== "prototype" && placement !== "own") { throw new TypeError('An element descriptor\'s .placement property must be one of "static",' + ' "prototype" or "own", but a decorator created an element descriptor' + ' with .placement "' + placement + '"'); } var descriptor = elementObject.descriptor; this.disallowProperty(elementObject, "elements", "An element descriptor"); var element = { kind: kind, key: key, placement: placement, descriptor: Object.assign({}, descriptor) }; if (kind !== "field") { this.disallowProperty(elementObject, "initializer", "A method descriptor"); } else { this.disallowProperty(descriptor, "get", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "set", "The property descriptor of a field descriptor"); this.disallowProperty(descriptor, "value", "The property descriptor of a field descriptor"); element.initializer = elementObject.initializer; } return element; }, toElementFinisherExtras: function toElementFinisherExtras(elementObject) { var element = this.toElementDescriptor(elementObject); var finisher = hassio_addon_dashboard_optionalCallableProperty(elementObject, "finisher"); var extras = this.toElementDescriptors(elementObject.extras); return { element: element, finisher: finisher, extras: extras }; }, fromClassDescriptor: function fromClassDescriptor(elements) { var obj = { kind: "class", elements: elements.map(this.fromElementDescriptor, this) }; var desc = { value: "Descriptor", configurable: true }; Object.defineProperty(obj, Symbol.toStringTag, desc); return obj; }, toClassDescriptor: function toClassDescriptor(obj) { var kind = String(obj.kind); if (kind !== "class") { throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator' + ' created a class descriptor with .kind "' + kind + '"'); } this.disallowProperty(obj, "key", "A class descriptor"); this.disallowProperty(obj, "placement", "A class descriptor"); this.disallowProperty(obj, "descriptor", "A class descriptor"); this.disallowProperty(obj, "initializer", "A class descriptor"); this.disallowProperty(obj, "extras", "A class descriptor"); var finisher = hassio_addon_dashboard_optionalCallableProperty(obj, "finisher"); var elements = this.toElementDescriptors(obj.elements); return { elements: elements, finisher: finisher }; }, runClassFinishers: function runClassFinishers(constructor, finishers) { for (var i = 0; i < finishers.length; i++) { var newConstructor = (0, finishers[i])(constructor); if (newConstructor !== undefined) { if (typeof newConstructor !== "function") { throw new TypeError("Finishers must return a constructor."); } constructor = newConstructor; } } return constructor; }, disallowProperty: function disallowProperty(obj, name, objectType) { if (obj[name] !== undefined) { throw new TypeError(objectType + " can't have a ." + name + " property."); } } }; return api; }

function hassio_addon_dashboard_createElementDescriptor(def) { var key = hassio_addon_dashboard_toPropertyKey(def.key); var descriptor; if (def.kind === "method") { descriptor = { value: def.value, writable: true, configurable: true, enumerable: false }; } else if (def.kind === "get") { descriptor = { get: def.value, configurable: true, enumerable: false }; } else if (def.kind === "set") { descriptor = { set: def.value, configurable: true, enumerable: false }; } else if (def.kind === "field") { descriptor = { configurable: true, writable: true, enumerable: true }; } var element = { kind: def.kind === "field" ? "field" : "method", key: key, placement: def["static"] ? "static" : def.kind === "field" ? "own" : "prototype", descriptor: descriptor }; if (def.decorators) element.decorators = def.decorators; if (def.kind === "field") element.initializer = def.value; return element; }

function hassio_addon_dashboard_coalesceGetterSetter(element, other) { if (element.descriptor.get !== undefined) { other.descriptor.get = element.descriptor.get; } else { other.descriptor.set = element.descriptor.set; } }

function hassio_addon_dashboard_coalesceClassElements(elements) { var newElements = []; var isSameElement = function isSameElement(other) { return other.kind === "method" && other.key === element.key && other.placement === element.placement; }; for (var i = 0; i < elements.length; i++) { var element = elements[i]; var other; if (element.kind === "method" && (other = newElements.find(isSameElement))) { if (hassio_addon_dashboard_isDataDescriptor(element.descriptor) || hassio_addon_dashboard_isDataDescriptor(other.descriptor)) { if (hassio_addon_dashboard_hasDecorators(element) || hassio_addon_dashboard_hasDecorators(other)) { throw new ReferenceError("Duplicated methods (" + element.key + ") can't be decorated."); } other.descriptor = element.descriptor; } else { if (hassio_addon_dashboard_hasDecorators(element)) { if (hassio_addon_dashboard_hasDecorators(other)) { throw new ReferenceError("Decorators can't be placed on different accessors with for " + "the same property (" + element.key + ")."); } other.decorators = element.decorators; } hassio_addon_dashboard_coalesceGetterSetter(element, other); } } else { newElements.push(element); } } return newElements; }

function hassio_addon_dashboard_hasDecorators(element) { return element.decorators && element.decorators.length; }

function hassio_addon_dashboard_isDataDescriptor(desc) { return desc !== undefined && !(desc.value === undefined && desc.writable === undefined); }

function hassio_addon_dashboard_optionalCallableProperty(obj, name) { var value = obj[name]; if (value !== undefined && typeof value !== "function") { throw new TypeError("Expected '" + name + "' to be a function"); } return value; }

function hassio_addon_dashboard_toPropertyKey(arg) { var key = hassio_addon_dashboard_toPrimitive(arg, "string"); return hassio_addon_dashboard_typeof(key) === "symbol" ? key : String(key); }

function hassio_addon_dashboard_toPrimitive(input, hint) { if (hassio_addon_dashboard_typeof(input) !== "object" || input === null) return input; var prim = input[Symbol.toPrimitive]; if (prim !== undefined) { var res = prim.call(input, hint || "default"); if (hassio_addon_dashboard_typeof(res) !== "object") return res; throw new TypeError("@@toPrimitive must return a primitive value."); } return (hint === "string" ? String : Number)(input); }

function hassio_addon_dashboard_toArray(arr) { return hassio_addon_dashboard_arrayWithHoles(arr) || hassio_addon_dashboard_iterableToArray(arr) || hassio_addon_dashboard_unsupportedIterableToArray(arr) || hassio_addon_dashboard_nonIterableRest(); }

function hassio_addon_dashboard_nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function hassio_addon_dashboard_unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return hassio_addon_dashboard_arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(n); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return hassio_addon_dashboard_arrayLikeToArray(o, minLen); }

function hassio_addon_dashboard_arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function hassio_addon_dashboard_iterableToArray(iter) { if (typeof Symbol !== "undefined" && Symbol.iterator in Object(iter)) return Array.from(iter); }

function hassio_addon_dashboard_arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }
















var hassio_addon_dashboard_HassioAddonDashboard = hassio_addon_dashboard_decorate([Object(lit_element["d" /* customElement */])("hassio-addon-dashboard")], function (_initialize, _LitElement) {
  var HassioAddonDashboard = /*#__PURE__*/function (_LitElement2) {
    hassio_addon_dashboard_inherits(HassioAddonDashboard, _LitElement2);

    var _super = hassio_addon_dashboard_createSuper(HassioAddonDashboard);

    function HassioAddonDashboard() {
      var _this;

      hassio_addon_dashboard_classCallCheck(this, HassioAddonDashboard);

      for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
        args[_key] = arguments[_key];
      }

      _this = _super.call.apply(_super, [this].concat(args));

      _initialize(hassio_addon_dashboard_assertThisInitialized(_this));

      return _this;
    }

    return HassioAddonDashboard;
  }(_LitElement);

  return {
    F: HassioAddonDashboard,
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
        attribute: false
      })],
      key: "addon",
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
      key: "render",
      value: function render() {
        if (!this.addon) {
          return Object(lit_element["e" /* html */])(hassio_addon_dashboard_templateObject());
        }

        var addonTabs = [{
          name: "Info",
          path: "/hassio/addon/".concat(this.addon.slug, "/info"),
          icon: "hassio:information-variant"
        }];

        if (this.addon.documentation) {
          addonTabs.push({
            name: "Documentation",
            path: "/hassio/addon/".concat(this.addon.slug, "/documentation"),
            icon: "hassio:file-document"
          });
        }

        if (this.addon.version) {
          addonTabs.push({
            name: "Configuration",
            path: "/hassio/addon/".concat(this.addon.slug, "/config"),
            icon: "hassio:cogs"
          }, {
            name: "Log",
            path: "/hassio/addon/".concat(this.addon.slug, "/logs"),
            icon: "hassio:math-log"
          });
        }

        var route = this._computeTail(this.route);

        return Object(lit_element["e" /* html */])(hassio_addon_dashboard_templateObject2(), this.hass, this.narrow, this.addon.version ? "/hassio/dashboard" : "/hassio/store", route, addonTabs, this.addon.name, route, this.narrow, this.hass, this.addon);
      }
    }, {
      kind: "get",
      "static": true,
      key: "styles",
      value: function styles() {
        return [resources_styles["b" /* haStyle */], hassio_style["a" /* hassioStyle */], Object(lit_element["c" /* css */])(hassio_addon_dashboard_templateObject3())];
      }
    }, {
      kind: "method",
      key: "firstUpdated",
      value: function () {
        var _firstUpdated = hassio_addon_dashboard_asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee() {
          var _this2 = this;

          return regeneratorRuntime.wrap(function _callee$(_context) {
            while (1) {
              switch (_context.prev = _context.next) {
                case 0:
                  _context.next = 2;
                  return this._routeDataChanged(this.route);

                case 2:
                  this.addEventListener("hass-api-called", function (ev) {
                    return _this2._apiCalled(ev);
                  });

                case 3:
                case "end":
                  return _context.stop();
              }
            }
          }, _callee, this);
        }));

        function firstUpdated() {
          return _firstUpdated.apply(this, arguments);
        }

        return firstUpdated;
      }()
    }, {
      kind: "method",
      key: "_apiCalled",
      value: function () {
        var _apiCalled2 = hassio_addon_dashboard_asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee2(ev) {
          var path;
          return regeneratorRuntime.wrap(function _callee2$(_context2) {
            while (1) {
              switch (_context2.prev = _context2.next) {
                case 0:
                  path = ev.detail.path;

                  if (path) {
                    _context2.next = 3;
                    break;
                  }

                  return _context2.abrupt("return");

                case 3:
                  if (!(path === "uninstall")) {
                    _context2.next = 7;
                    break;
                  }

                  history.back();
                  _context2.next = 9;
                  break;

                case 7:
                  _context2.next = 9;
                  return this._routeDataChanged(this.route);

                case 9:
                case "end":
                  return _context2.stop();
              }
            }
          }, _callee2, this);
        }));

        function _apiCalled(_x) {
          return _apiCalled2.apply(this, arguments);
        }

        return _apiCalled;
      }()
    }, {
      kind: "method",
      key: "_routeDataChanged",
      value: function () {
        var _routeDataChanged2 = hassio_addon_dashboard_asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee3(routeData) {
          var addon, addoninfo;
          return regeneratorRuntime.wrap(function _callee3$(_context3) {
            while (1) {
              switch (_context3.prev = _context3.next) {
                case 0:
                  addon = routeData.path.split("/")[1];
                  _context3.prev = 1;
                  _context3.next = 4;
                  return Object(hassio_addon["c" /* fetchHassioAddonInfo */])(this.hass, addon);

                case 4:
                  addoninfo = _context3.sent;
                  this.addon = addoninfo;
                  _context3.next = 11;
                  break;

                case 8:
                  _context3.prev = 8;
                  _context3.t0 = _context3["catch"](1);
                  this.addon = undefined;

                case 11:
                case "end":
                  return _context3.stop();
              }
            }
          }, _callee3, this, [[1, 8]]);
        }));

        function _routeDataChanged(_x2) {
          return _routeDataChanged2.apply(this, arguments);
        }

        return _routeDataChanged;
      }()
    }]
  };
}, lit_element["a" /* LitElement */]);

/***/ }),

/***/ 74:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony import */ var lit_element__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(5);
/* harmony import */ var workerize_loader_resources_markdown_worker__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(94);
/* harmony import */ var workerize_loader_resources_markdown_worker__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(workerize_loader_resources_markdown_worker__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _common_dom_fire_event__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(12);
function _typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { _typeof = function _typeof(obj) { return typeof obj; }; } else { _typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return _typeof(obj); }

function asyncGeneratorStep(gen, resolve, reject, _next, _throw, key, arg) { try { var info = gen[key](arg); var value = info.value; } catch (error) { reject(error); return; } if (info.done) { resolve(value); } else { Promise.resolve(value).then(_next, _throw); } }

function _asyncToGenerator(fn) { return function () { var self = this, args = arguments; return new Promise(function (resolve, reject) { var gen = fn.apply(self, args); function _next(value) { asyncGeneratorStep(gen, resolve, reject, _next, _throw, "next", value); } function _throw(err) { asyncGeneratorStep(gen, resolve, reject, _next, _throw, "throw", err); } _next(undefined); }); }; }

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

 // @ts-ignore
// eslint-disable-next-line import/no-webpack-loader-syntax



var worker;

var HaMarkdown = _decorate([Object(lit_element__WEBPACK_IMPORTED_MODULE_0__[/* customElement */ "d"])("ha-markdown")], function (_initialize, _UpdatingElement) {
  var HaMarkdown = /*#__PURE__*/function (_UpdatingElement2) {
    _inherits(HaMarkdown, _UpdatingElement2);

    var _super = _createSuper(HaMarkdown);

    function HaMarkdown() {
      var _this;

      _classCallCheck(this, HaMarkdown);

      for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
        args[_key] = arguments[_key];
      }

      _this = _super.call.apply(_super, [this].concat(args));

      _initialize(_assertThisInitialized(_this));

      return _this;
    }

    return HaMarkdown;
  }(_UpdatingElement);

  return {
    F: HaMarkdown,
    d: [{
      kind: "field",
      decorators: [Object(lit_element__WEBPACK_IMPORTED_MODULE_0__[/* property */ "f"])()],
      key: "content",
      value: function value() {
        return "";
      }
    }, {
      kind: "field",
      decorators: [Object(lit_element__WEBPACK_IMPORTED_MODULE_0__[/* property */ "f"])({
        type: Boolean
      })],
      key: "allowSvg",
      value: function value() {
        return false;
      }
    }, {
      kind: "field",
      decorators: [Object(lit_element__WEBPACK_IMPORTED_MODULE_0__[/* property */ "f"])({
        type: Boolean
      })],
      key: "breaks",
      value: function value() {
        return false;
      }
    }, {
      kind: "method",
      key: "update",
      value: function update(changedProps) {
        _get(_getPrototypeOf(HaMarkdown.prototype), "update", this).call(this, changedProps);

        if (!worker) {
          worker = workerize_loader_resources_markdown_worker__WEBPACK_IMPORTED_MODULE_1___default()();
        }

        this._render();
      }
    }, {
      kind: "method",
      key: "_render",
      value: function () {
        var _render2 = _asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee() {
          var walker, node;
          return regeneratorRuntime.wrap(function _callee$(_context) {
            while (1) {
              switch (_context.prev = _context.next) {
                case 0:
                  _context.next = 2;
                  return worker.renderMarkdown(this.content, {
                    breaks: this.breaks,
                    gfm: true,
                    tables: true
                  }, {
                    allowSvg: this.allowSvg
                  });

                case 2:
                  this.innerHTML = _context.sent;

                  this._resize();

                  walker = document.createTreeWalker(this, 1
                  /* SHOW_ELEMENT */
                  , null, false);

                  while (walker.nextNode()) {
                    node = walker.currentNode; // Open external links in a new window

                    if (node instanceof HTMLAnchorElement && node.host !== document.location.host) {
                      node.target = "_blank";
                      node.rel = "noreferrer"; // protect referrer on external links and deny window.opener access for security reasons
                      // (see https://mathiasbynens.github.io/rel-noopener/)

                      node.rel = "noreferrer noopener"; // Fire a resize event when images loaded to notify content resized
                    } else if (node) {
                      node.addEventListener("load", this._resize);
                    }
                  }

                case 6:
                case "end":
                  return _context.stop();
              }
            }
          }, _callee, this);
        }));

        function _render() {
          return _render2.apply(this, arguments);
        }

        return _render;
      }()
    }, {
      kind: "field",
      key: "_resize",
      value: function value() {
        var _this2 = this;

        return function () {
          return Object(_common_dom_fire_event__WEBPACK_IMPORTED_MODULE_2__[/* fireEvent */ "a"])(_this2, "iron-resize");
        };
      }
    }]
  };
}, lit_element__WEBPACK_IMPORTED_MODULE_0__[/* UpdatingElement */ "b"]);

/***/ }),

/***/ 94:
/***/ (function(module, exports, __webpack_require__) {


				var addMethods = __webpack_require__(95)
				var methods = ["renderMarkdown"]
				module.exports = function() {
					var w = new Worker(__webpack_require__.p + "7e78115f8d410990252b.worker.js", { name: "[hash].worker.js" })
					addMethods(w, methods)
					
					return w
				}
			

/***/ })

}]);