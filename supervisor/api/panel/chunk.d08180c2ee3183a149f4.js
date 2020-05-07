(self["webpackJsonp"] = self["webpackJsonp"] || []).push([[4],{

/***/ 193:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);

// EXTERNAL MODULE: ./node_modules/@material/mwc-button/mwc-button.js + 12 modules
var mwc_button = __webpack_require__(18);

// EXTERNAL MODULE: ./node_modules/@polymer/app-layout/app-toolbar/app-toolbar.js
var app_toolbar = __webpack_require__(88);

// EXTERNAL MODULE: ./node_modules/@polymer/paper-dialog-scrollable/paper-dialog-scrollable.js
var paper_dialog_scrollable = __webpack_require__(53);

// EXTERNAL MODULE: ./src/components/ha-icon-button.ts
var ha_icon_button = __webpack_require__(23);

// EXTERNAL MODULE: ./src/components/ha-icon.ts + 3 modules
var ha_icon = __webpack_require__(32);

// EXTERNAL MODULE: ./node_modules/@polymer/paper-input/paper-input.js + 7 modules
var paper_input = __webpack_require__(43);

// EXTERNAL MODULE: ./node_modules/lit-element/lit-element.js + 3 modules
var lit_element = __webpack_require__(5);

// EXTERNAL MODULE: ./src/components/dialog/ha-paper-dialog.ts + 3 modules
var ha_paper_dialog = __webpack_require__(57);

// CONCATENATED MODULE: ./src/data/auth.ts
function asyncGeneratorStep(gen, resolve, reject, _next, _throw, key, arg) { try { var info = gen[key](arg); var value = info.value; } catch (error) { reject(error); return; } if (info.done) { resolve(value); } else { Promise.resolve(value).then(_next, _throw); } }

function _asyncToGenerator(fn) { return function () { var self = this, args = arguments; return new Promise(function (resolve, reject) { var gen = fn.apply(self, args); function _next(value) { asyncGeneratorStep(gen, resolve, reject, _next, _throw, "next", value); } function _throw(err) { asyncGeneratorStep(gen, resolve, reject, _next, _throw, "throw", err); } _next(undefined); }); }; }

var hassUrl = "".concat(location.protocol, "//").concat(location.host);
var getSignedPath = function getSignedPath(hass, path) {
  return hass.callWS({
    type: "auth/sign_path",
    path: path
  });
};
var fetchAuthProviders = function fetchAuthProviders() {
  return fetch("/auth/providers", {
    credentials: "same-origin"
  });
};
var createAuthForUser = /*#__PURE__*/function () {
  var _ref = _asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee(hass, userId, username, password) {
    return regeneratorRuntime.wrap(function _callee$(_context) {
      while (1) {
        switch (_context.prev = _context.next) {
          case 0:
            return _context.abrupt("return", hass.callWS({
              type: "config/auth_provider/homeassistant/create",
              user_id: userId,
              username: username,
              password: password
            }));

          case 1:
          case "end":
            return _context.stop();
        }
      }
    }, _callee);
  }));

  return function createAuthForUser(_x, _x2, _x3, _x4) {
    return _ref.apply(this, arguments);
  };
}();
// EXTERNAL MODULE: ./src/data/hassio/snapshot.ts
var snapshot = __webpack_require__(126);

// EXTERNAL MODULE: ./src/resources/styles.ts
var resources_styles = __webpack_require__(11);

// CONCATENATED MODULE: ./hassio/src/dialogs/snapshot/dialog-hassio-snapshot.ts
function _typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { _typeof = function _typeof(obj) { return typeof obj; }; } else { _typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return _typeof(obj); }

function _templateObject10() {
  var data = _taggedTemplateLiteral(["\n        ha-paper-dialog {\n          min-width: 350px;\n          font-size: 14px;\n          border-radius: 2px;\n        }\n        app-toolbar {\n          margin: 0;\n          padding: 0 16px;\n          color: var(--primary-text-color);\n          background-color: var(--secondary-background-color);\n        }\n        app-toolbar [main-title] {\n          margin-left: 16px;\n        }\n        ha-paper-dialog-scrollable {\n          margin: 0;\n        }\n        paper-checkbox {\n          display: block;\n          margin: 4px;\n        }\n        @media all and (max-width: 450px), all and (max-height: 500px) {\n          ha-paper-dialog {\n            max-height: 100%;\n            height: 100%;\n          }\n          app-toolbar {\n            color: var(--text-primary-color);\n            background-color: var(--primary-color);\n          }\n        }\n        .details {\n          color: var(--secondary-text-color);\n        }\n        .warning,\n        .error {\n          color: var(--google-red-500);\n        }\n        .buttons {\n          display: flex;\n          flex-direction: column;\n        }\n        .buttons li {\n          list-style-type: none;\n        }\n        .buttons .icon {\n          margin-right: 16px;\n        }\n        .no-margin-top {\n          margin-top: 0;\n        }\n      "]);

  _templateObject10 = function _templateObject10() {
    return data;
  };

  return data;
}

function _templateObject9() {
  var data = _taggedTemplateLiteral(["\n                <li>\n                  <mwc-button @click=", ">\n                    <ha-icon icon=\"hassio:history\" class=\"icon\"> </ha-icon>\n                    Wipe &amp; restore\n                  </mwc-button>\n                </li>\n              "]);

  _templateObject9 = function _templateObject9() {
    return data;
  };

  return data;
}

function _templateObject8() {
  var data = _taggedTemplateLiteral([" <p class=\"error\">Error: ", "</p> "]);

  _templateObject8 = function _templateObject8() {
    return data;
  };

  return data;
}

function _templateObject7() {
  var data = _taggedTemplateLiteral(["\n              <paper-input\n                autofocus=\"\"\n                label=\"Password\"\n                type=\"password\"\n                @value-changed=", "\n                .value=", "\n              ></paper-input>\n            "]);

  _templateObject7 = function _templateObject7() {
    return data;
  };

  return data;
}

function _templateObject6() {
  var data = _taggedTemplateLiteral(["\n                    <paper-checkbox\n                      .checked=", "\n                      @change=\"", "\"\n                    >\n                      ", "\n                    </paper-checkbox>\n                  "]);

  _templateObject6 = function _templateObject6() {
    return data;
  };

  return data;
}

function _templateObject5() {
  var data = _taggedTemplateLiteral(["\n              <div>Add-on:</div>\n              <paper-dialog-scrollable class=\"no-margin-top\">\n                ", "\n              </paper-dialog-scrollable>\n            "]);

  _templateObject5 = function _templateObject5() {
    return data;
  };

  return data;
}

function _templateObject4() {
  var data = _taggedTemplateLiteral(["\n                    <paper-checkbox\n                      .checked=", "\n                      @change=\"", "\"\n                    >\n                      ", "\n                    </paper-checkbox>\n                  "]);

  _templateObject4 = function _templateObject4() {
    return data;
  };

  return data;
}

function _templateObject3() {
  var data = _taggedTemplateLiteral(["\n              <div>Folders:</div>\n              <paper-dialog-scrollable class=\"no-margin-top\">\n                ", "\n              </paper-dialog-scrollable>\n            "]);

  _templateObject3 = function _templateObject3() {
    return data;
  };

  return data;
}

function _templateObject2() {
  var data = _taggedTemplateLiteral(["\n      <ha-paper-dialog\n        id=\"dialog\"\n        with-backdrop=\"\"\n        .on-iron-overlay-closed=", "\n      >\n        <app-toolbar>\n          <ha-icon-button\n            icon=\"hassio:close\"\n            dialog-dismiss=\"\"\n          ></ha-icon-button>\n          <div main-title=\"\">", "</div>\n        </app-toolbar>\n        <div class=\"details\">\n          ", "\n          (", ")<br />\n          ", "\n        </div>\n        <div>Home Assistant:</div>\n        <paper-checkbox\n          .checked=", "\n          @change=\"", "\"\n        >\n          Home Assistant ", "\n        </paper-checkbox>\n        ", "\n        ", "\n        ", "\n        ", "\n\n        <div>Actions:</div>\n        <ul class=\"buttons\">\n          <li>\n            <mwc-button @click=", ">\n              <ha-icon icon=\"hassio:download\" class=\"icon\"></ha-icon>\n              Download Snapshot\n            </mwc-button>\n          </li>\n          <li>\n            <mwc-button @click=", ">\n              <ha-icon icon=\"hassio:history\" class=\"icon\"> </ha-icon>\n              Restore Selected\n            </mwc-button>\n          </li>\n          ", "\n          <li>\n            <mwc-button @click=", ">\n              <ha-icon icon=\"hassio:delete\" class=\"icon warning\"> </ha-icon>\n              <span class=\"warning\">Delete Snapshot</span>\n            </mwc-button>\n          </li>\n        </ul>\n      </ha-paper-dialog>\n    "]);

  _templateObject2 = function _templateObject2() {
    return data;
  };

  return data;
}

function _templateObject() {
  var data = _taggedTemplateLiteral([""]);

  _templateObject = function _templateObject() {
    return data;
  };

  return data;
}

function _taggedTemplateLiteral(strings, raw) { if (!raw) { raw = strings.slice(0); } return Object.freeze(Object.defineProperties(strings, { raw: { value: Object.freeze(raw) } })); }

function dialog_hassio_snapshot_asyncGeneratorStep(gen, resolve, reject, _next, _throw, key, arg) { try { var info = gen[key](arg); var value = info.value; } catch (error) { reject(error); return; } if (info.done) { resolve(value); } else { Promise.resolve(value).then(_next, _throw); } }

function dialog_hassio_snapshot_asyncToGenerator(fn) { return function () { var self = this, args = arguments; return new Promise(function (resolve, reject) { var gen = fn.apply(self, args); function _next(value) { dialog_hassio_snapshot_asyncGeneratorStep(gen, resolve, reject, _next, _throw, "next", value); } function _throw(err) { dialog_hassio_snapshot_asyncGeneratorStep(gen, resolve, reject, _next, _throw, "throw", err); } _next(undefined); }); }; }

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













var _computeFolders = function _computeFolders(folders) {
  var list = [];

  if (folders.includes("homeassistant")) {
    list.push({
      slug: "homeassistant",
      name: "Home Assistant configuration",
      checked: true
    });
  }

  if (folders.includes("ssl")) {
    list.push({
      slug: "ssl",
      name: "SSL",
      checked: true
    });
  }

  if (folders.includes("share")) {
    list.push({
      slug: "share",
      name: "Share",
      checked: true
    });
  }

  if (folders.includes("addons/local")) {
    list.push({
      slug: "addons/local",
      name: "Local add-ons",
      checked: true
    });
  }

  return list;
};

var _computeAddons = function _computeAddons(addons) {
  return addons.map(function (addon) {
    return {
      slug: addon.slug,
      name: addon.name,
      version: addon.version,
      checked: true
    };
  });
};

var dialog_hassio_snapshot_HassioSnapshotDialog = _decorate([Object(lit_element["d" /* customElement */])("dialog-hassio-snapshot")], function (_initialize, _LitElement) {
  var HassioSnapshotDialog = /*#__PURE__*/function (_LitElement2) {
    _inherits(HassioSnapshotDialog, _LitElement2);

    var _super = _createSuper(HassioSnapshotDialog);

    function HassioSnapshotDialog() {
      var _this;

      _classCallCheck(this, HassioSnapshotDialog);

      for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
        args[_key] = arguments[_key];
      }

      _this = _super.call.apply(_super, [this].concat(args));

      _initialize(_assertThisInitialized(_this));

      return _this;
    }

    return HassioSnapshotDialog;
  }(_LitElement);

  return {
    F: HassioSnapshotDialog,
    d: [{
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
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
      key: "snapshot",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "_folders",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "_addons",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "_dialogParams",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "_snapshotPassword",
      value: void 0
    }, {
      kind: "field",
      decorators: [Object(lit_element["f" /* property */])()],
      key: "_restoreHass",
      value: function value() {
        return true;
      }
    }, {
      kind: "field",
      decorators: [Object(lit_element["g" /* query */])("#dialog")],
      key: "_dialog",
      value: void 0
    }, {
      kind: "method",
      key: "showDialog",
      value: function () {
        var _showDialog = dialog_hassio_snapshot_asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee(params) {
          return regeneratorRuntime.wrap(function _callee$(_context) {
            while (1) {
              switch (_context.prev = _context.next) {
                case 0:
                  _context.next = 2;
                  return Object(snapshot["c" /* fetchHassioSnapshotInfo */])(this.hass, params.slug);

                case 2:
                  this.snapshot = _context.sent;
                  this._folders = _computeFolders(this.snapshot.folders).sort(function (a, b) {
                    return a.name > b.name ? 1 : -1;
                  });
                  this._addons = _computeAddons(this.snapshot.addons).sort(function (a, b) {
                    return a.name > b.name ? 1 : -1;
                  });
                  this._dialogParams = params;
                  _context.prev = 6;

                  this._dialog.open();

                  _context.next = 14;
                  break;

                case 10:
                  _context.prev = 10;
                  _context.t0 = _context["catch"](6);
                  _context.next = 14;
                  return this.showDialog(params);

                case 14:
                case "end":
                  return _context.stop();
              }
            }
          }, _callee, this, [[6, 10]]);
        }));

        function showDialog(_x) {
          return _showDialog.apply(this, arguments);
        }

        return showDialog;
      }()
    }, {
      kind: "method",
      key: "render",
      value: function render() {
        var _this2 = this;

        if (!this.snapshot) {
          return Object(lit_element["e" /* html */])(_templateObject());
        }

        return Object(lit_element["e" /* html */])(_templateObject2(), this._dialogClosed, this._computeName, this.snapshot.type === "full" ? "Full snapshot" : "Partial snapshot", this._computeSize, this._formatDatetime(this.snapshot.date), this._restoreHass, function (ev) {
          _this2._restoreHass = ev.target.checked;
        }, this.snapshot.homeassistant, this._folders.length ? Object(lit_element["e" /* html */])(_templateObject3(), this._folders.map(function (item) {
          return Object(lit_element["e" /* html */])(_templateObject4(), item.checked, function (ev) {
            return _this2._updateFolders(item, ev.target.checked);
          }, item.name);
        })) : "", this._addons.length ? Object(lit_element["e" /* html */])(_templateObject5(), this._addons.map(function (item) {
          return Object(lit_element["e" /* html */])(_templateObject6(), item.checked, function (ev) {
            return _this2._updateAddons(item, ev.target.checked);
          }, item.name);
        })) : "", this.snapshot["protected"] ? Object(lit_element["e" /* html */])(_templateObject7(), this._passwordInput, this._snapshotPassword) : "", this._error ? Object(lit_element["e" /* html */])(_templateObject8(), this._error) : "", this._downloadClicked, this._partialRestoreClicked, this.snapshot.type === "full" ? Object(lit_element["e" /* html */])(_templateObject9(), this._fullRestoreClicked) : "", this._deleteClicked);
      }
    }, {
      kind: "get",
      "static": true,
      key: "styles",
      value: function styles() {
        return [resources_styles["c" /* haStyleDialog */], Object(lit_element["c" /* css */])(_templateObject10())];
      }
    }, {
      kind: "method",
      key: "_updateFolders",
      value: function _updateFolders(item, value) {
        this._folders = this._folders.map(function (folder) {
          if (folder.slug === item.slug) {
            folder.checked = value;
          }

          return folder;
        });
      }
    }, {
      kind: "method",
      key: "_updateAddons",
      value: function _updateAddons(item, value) {
        this._addons = this._addons.map(function (addon) {
          if (addon.slug === item.slug) {
            addon.checked = value;
          }

          return addon;
        });
      }
    }, {
      kind: "method",
      key: "_passwordInput",
      value: function _passwordInput(ev) {
        this._snapshotPassword = ev.detail.value;
      }
    }, {
      kind: "method",
      key: "_partialRestoreClicked",
      value: function _partialRestoreClicked() {
        var _this3 = this;

        if (!confirm("Are you sure you want to restore this snapshot?")) {
          return;
        }

        var addons = this._addons.filter(function (addon) {
          return addon.checked;
        }).map(function (addon) {
          return addon.slug;
        });

        var folders = this._folders.filter(function (folder) {
          return folder.checked;
        }).map(function (folder) {
          return folder.slug;
        });

        var data = {
          homeassistant: this._restoreHass,
          addons: addons,
          folders: folders
        };

        if (this.snapshot["protected"]) {
          data.password = this._snapshotPassword;
        }

        this.hass.callApi("POST", "hassio/snapshots/".concat(this.snapshot.slug, "/restore/partial"), data).then(function () {
          alert("Snapshot restored!");

          _this3._dialog.close();
        }, function (error) {
          _this3._error = error.body.message;
        });
      }
    }, {
      kind: "method",
      key: "_fullRestoreClicked",
      value: function _fullRestoreClicked() {
        var _this4 = this;

        if (!confirm("Are you sure you want to restore this snapshot?")) {
          return;
        }

        var data = this.snapshot["protected"] ? {
          password: this._snapshotPassword
        } : undefined;
        this.hass.callApi("POST", "hassio/snapshots/".concat(this.snapshot.slug, "/restore/full"), data).then(function () {
          alert("Snapshot restored!");

          _this4._dialog.close();
        }, function (error) {
          _this4._error = error.body.message;
        });
      }
    }, {
      kind: "method",
      key: "_deleteClicked",
      value: function _deleteClicked() {
        var _this5 = this;

        if (!confirm("Are you sure you want to delete this snapshot?")) {
          return;
        }

        this.hass.callApi("POST", "hassio/snapshots/".concat(this.snapshot.slug, "/remove")).then(function () {
          _this5._dialog.close();

          _this5._dialogParams.onDelete();
        }, function (error) {
          _this5._error = error.body.message;
        });
      }
    }, {
      kind: "method",
      key: "_downloadClicked",
      value: function () {
        var _downloadClicked2 = dialog_hassio_snapshot_asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee2() {
          var signedPath, name, a;
          return regeneratorRuntime.wrap(function _callee2$(_context2) {
            while (1) {
              switch (_context2.prev = _context2.next) {
                case 0:
                  _context2.prev = 0;
                  _context2.next = 3;
                  return getSignedPath(this.hass, "/api/hassio/snapshots/".concat(this.snapshot.slug, "/download"));

                case 3:
                  signedPath = _context2.sent;
                  _context2.next = 10;
                  break;

                case 6:
                  _context2.prev = 6;
                  _context2.t0 = _context2["catch"](0);
                  alert("Error: ".concat(_context2.t0.message));
                  return _context2.abrupt("return");

                case 10:
                  name = this._computeName.replace(/[^a-z0-9]+/gi, "_");
                  a = document.createElement("a");
                  a.href = signedPath.path;
                  a.download = "Hass_io_".concat(name, ".tar");

                  this._dialog.appendChild(a);

                  a.click();

                  this._dialog.removeChild(a);

                case 17:
                case "end":
                  return _context2.stop();
              }
            }
          }, _callee2, this, [[0, 6]]);
        }));

        function _downloadClicked() {
          return _downloadClicked2.apply(this, arguments);
        }

        return _downloadClicked;
      }()
    }, {
      kind: "get",
      key: "_computeName",
      value: function _computeName() {
        return this.snapshot ? this.snapshot.name || this.snapshot.slug : "Unnamed snapshot";
      }
    }, {
      kind: "get",
      key: "_computeSize",
      value: function _computeSize() {
        return Math.ceil(this.snapshot.size * 10) / 10 + " MB";
      }
    }, {
      kind: "method",
      key: "_formatDatetime",
      value: function _formatDatetime(datetime) {
        return new Date(datetime).toLocaleDateString(navigator.language, {
          weekday: "long",
          year: "numeric",
          month: "short",
          day: "numeric",
          hour: "numeric",
          minute: "2-digit"
        });
      }
    }, {
      kind: "method",
      key: "_dialogClosed",
      value: function _dialogClosed() {
        this._dialogParams = undefined;
        this.snapshot = undefined;
        this._snapshotPassword = "";
        this._folders = [];
        this._addons = [];
      }
    }]
  };
}, lit_element["a" /* LitElement */]);

/***/ }),

/***/ 31:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "b", function() { return PaperDialogBehaviorImpl; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "a", function() { return PaperDialogBehavior; });
/* harmony import */ var _polymer_polymer_polymer_legacy_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(4);
/* harmony import */ var _polymer_iron_overlay_behavior_iron_overlay_behavior_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(75);
/* harmony import */ var _polymer_polymer_lib_legacy_polymer_dom_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(9);
/**
@license
Copyright (c) 2015 The Polymer Project Authors. All rights reserved.
This code may only be used under the BSD style license found at
http://polymer.github.io/LICENSE.txt The complete set of authors may be found at
http://polymer.github.io/AUTHORS.txt The complete set of contributors may be
found at http://polymer.github.io/CONTRIBUTORS.txt Code distributed by Google as
part of the polymer project is also subject to an additional IP rights grant
found at http://polymer.github.io/PATENTS.txt
*/



/**
  Use `Polymer.PaperDialogBehavior` and `paper-dialog-shared-styles.html` to
  implement a Material Design dialog.

  For example, if `<paper-dialog-impl>` implements this behavior:

      <paper-dialog-impl>
          <h2>Header</h2>
          <div>Dialog body</div>
          <div class="buttons">
              <paper-button dialog-dismiss>Cancel</paper-button>
              <paper-button dialog-confirm>Accept</paper-button>
          </div>
      </paper-dialog-impl>

  `paper-dialog-shared-styles.html` provide styles for a header, content area,
  and an action area for buttons. Use the `<h2>` tag for the header and the
  `buttons` class for the action area. You can use the `paper-dialog-scrollable`
  element (in its own repository) if you need a scrolling content area.

  Use the `dialog-dismiss` and `dialog-confirm` attributes on interactive
  controls to close the dialog. If the user dismisses the dialog with
  `dialog-confirm`, the `closingReason` will update to include `confirmed:
  true`.

  ### Accessibility

  This element has `role="dialog"` by default. Depending on the context, it may
  be more appropriate to override this attribute with `role="alertdialog"`.

  If `modal` is set, the element will prevent the focus from exiting the
  element. It will also ensure that focus remains in the dialog.

  @hero hero.svg
  @demo demo/index.html
  @polymerBehavior PaperDialogBehavior
 */

var PaperDialogBehaviorImpl = {
  hostAttributes: {
    'role': 'dialog',
    'tabindex': '-1'
  },
  properties: {
    /**
     * If `modal` is true, this implies `no-cancel-on-outside-click`,
     * `no-cancel-on-esc-key` and `with-backdrop`.
     */
    modal: {
      type: Boolean,
      value: false
    },
    __readied: {
      type: Boolean,
      value: false
    }
  },
  observers: ['_modalChanged(modal, __readied)'],
  listeners: {
    'tap': '_onDialogClick'
  },

  /**
   * @return {void}
   */
  ready: function ready() {
    // Only now these properties can be read.
    this.__prevNoCancelOnOutsideClick = this.noCancelOnOutsideClick;
    this.__prevNoCancelOnEscKey = this.noCancelOnEscKey;
    this.__prevWithBackdrop = this.withBackdrop;
    this.__readied = true;
  },
  _modalChanged: function _modalChanged(modal, readied) {
    // modal implies noCancelOnOutsideClick, noCancelOnEscKey and withBackdrop.
    // We need to wait for the element to be ready before we can read the
    // properties values.
    if (!readied) {
      return;
    }

    if (modal) {
      this.__prevNoCancelOnOutsideClick = this.noCancelOnOutsideClick;
      this.__prevNoCancelOnEscKey = this.noCancelOnEscKey;
      this.__prevWithBackdrop = this.withBackdrop;
      this.noCancelOnOutsideClick = true;
      this.noCancelOnEscKey = true;
      this.withBackdrop = true;
    } else {
      // If the value was changed to false, let it false.
      this.noCancelOnOutsideClick = this.noCancelOnOutsideClick && this.__prevNoCancelOnOutsideClick;
      this.noCancelOnEscKey = this.noCancelOnEscKey && this.__prevNoCancelOnEscKey;
      this.withBackdrop = this.withBackdrop && this.__prevWithBackdrop;
    }
  },
  _updateClosingReasonConfirmed: function _updateClosingReasonConfirmed(confirmed) {
    this.closingReason = this.closingReason || {};
    this.closingReason.confirmed = confirmed;
  },

  /**
   * Will dismiss the dialog if user clicked on an element with dialog-dismiss
   * or dialog-confirm attribute.
   */
  _onDialogClick: function _onDialogClick(event) {
    // Search for the element with dialog-confirm or dialog-dismiss,
    // from the root target until this (excluded).
    var path = Object(_polymer_polymer_lib_legacy_polymer_dom_js__WEBPACK_IMPORTED_MODULE_2__[/* dom */ "a"])(event).path;

    for (var i = 0, l = path.indexOf(this); i < l; i++) {
      var target = path[i];

      if (target.hasAttribute && (target.hasAttribute('dialog-dismiss') || target.hasAttribute('dialog-confirm'))) {
        this._updateClosingReasonConfirmed(target.hasAttribute('dialog-confirm'));

        this.close();
        event.stopPropagation();
        break;
      }
    }
  }
};
/** @polymerBehavior */

var PaperDialogBehavior = [_polymer_iron_overlay_behavior_iron_overlay_behavior_js__WEBPACK_IMPORTED_MODULE_1__[/* IronOverlayBehavior */ "a"], PaperDialogBehaviorImpl];

/***/ }),

/***/ 53:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony import */ var _polymer_polymer_polymer_legacy_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(4);
/* harmony import */ var _polymer_iron_flex_layout_iron_flex_layout_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(16);
/* harmony import */ var _polymer_paper_styles_default_theme_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(14);
/* harmony import */ var _polymer_paper_dialog_behavior_paper_dialog_behavior_js__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(31);
/* harmony import */ var _polymer_polymer_lib_legacy_polymer_fn_js__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(8);
/* harmony import */ var _polymer_polymer_lib_utils_html_tag_js__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(7);
function _templateObject() {
  var data = _taggedTemplateLiteral(["\n    <style>\n\n      :host {\n        display: block;\n        @apply --layout-relative;\n      }\n\n      :host(.is-scrolled:not(:first-child))::before {\n        content: '';\n        position: absolute;\n        top: 0;\n        left: 0;\n        right: 0;\n        height: 1px;\n        background: var(--divider-color);\n      }\n\n      :host(.can-scroll:not(.scrolled-to-bottom):not(:last-child))::after {\n        content: '';\n        position: absolute;\n        bottom: 0;\n        left: 0;\n        right: 0;\n        height: 1px;\n        background: var(--divider-color);\n      }\n\n      .scrollable {\n        padding: 0 24px;\n\n        @apply --layout-scroll;\n        @apply --paper-dialog-scrollable;\n      }\n\n      .fit {\n        @apply --layout-fit;\n      }\n    </style>\n\n    <div id=\"scrollable\" class=\"scrollable\" on-scroll=\"updateScrollState\">\n      <slot></slot>\n    </div>\n"]);

  _templateObject = function _templateObject() {
    return data;
  };

  return data;
}

function _taggedTemplateLiteral(strings, raw) { if (!raw) { raw = strings.slice(0); } return Object.freeze(Object.defineProperties(strings, { raw: { value: Object.freeze(raw) } })); }

/**
@license
Copyright (c) 2015 The Polymer Project Authors. All rights reserved.
This code may only be used under the BSD style license found at
http://polymer.github.io/LICENSE.txt The complete set of authors may be found at
http://polymer.github.io/AUTHORS.txt The complete set of contributors may be
found at http://polymer.github.io/CONTRIBUTORS.txt Code distributed by Google as
part of the polymer project is also subject to an additional IP rights grant
found at http://polymer.github.io/PATENTS.txt
*/






/**
Material design:
[Dialogs](https://www.google.com/design/spec/components/dialogs.html)

`paper-dialog-scrollable` implements a scrolling area used in a Material Design
dialog. It shows a divider at the top and/or bottom indicating more content,
depending on scroll position. Use this together with elements implementing
`Polymer.PaperDialogBehavior`.

    <paper-dialog-impl>
      <h2>Header</h2>
      <paper-dialog-scrollable>
        Lorem ipsum...
      </paper-dialog-scrollable>
      <div class="buttons">
        <paper-button>OK</paper-button>
      </div>
    </paper-dialog-impl>

It shows a top divider after scrolling if it is not the first child in its
parent container, indicating there is more content above. It shows a bottom
divider if it is scrollable and it is not the last child in its parent
container, indicating there is more content below. The bottom divider is hidden
if it is scrolled to the bottom.

If `paper-dialog-scrollable` is not a direct child of the element implementing
`Polymer.PaperDialogBehavior`, remember to set the `dialogElement`:

    <paper-dialog-impl id="myDialog">
      <h2>Header</h2>
      <div class="my-content-wrapper">
        <h4>Sub-header</h4>
        <paper-dialog-scrollable>
          Lorem ipsum...
        </paper-dialog-scrollable>
      </div>
      <div class="buttons">
        <paper-button>OK</paper-button>
      </div>
    </paper-dialog-impl>

    <script>
      var scrollable =
Polymer.dom(myDialog).querySelector('paper-dialog-scrollable');
      scrollable.dialogElement = myDialog;
    </script>

### Styling
The following custom properties and mixins are available for styling:

Custom property | Description | Default
----------------|-------------|----------
`--paper-dialog-scrollable` | Mixin for the scrollable content | {}

@group Paper Elements
@element paper-dialog-scrollable
@demo demo/index.html
@hero hero.svg
*/

Object(_polymer_polymer_lib_legacy_polymer_fn_js__WEBPACK_IMPORTED_MODULE_4__[/* Polymer */ "a"])({
  _template: Object(_polymer_polymer_lib_utils_html_tag_js__WEBPACK_IMPORTED_MODULE_5__[/* html */ "a"])(_templateObject()),
  is: 'paper-dialog-scrollable',
  properties: {
    /**
     * The dialog element that implements `Polymer.PaperDialogBehavior`
     * containing this element.
     * @type {?Node}
     */
    dialogElement: {
      type: Object
    }
  },

  /**
   * Returns the scrolling element.
   */
  get scrollTarget() {
    return this.$.scrollable;
  },

  ready: function ready() {
    this._ensureTarget();

    this.classList.add('no-padding');
  },
  attached: function attached() {
    this._ensureTarget();

    requestAnimationFrame(this.updateScrollState.bind(this));
  },
  updateScrollState: function updateScrollState() {
    this.toggleClass('is-scrolled', this.scrollTarget.scrollTop > 0);
    this.toggleClass('can-scroll', this.scrollTarget.offsetHeight < this.scrollTarget.scrollHeight);
    this.toggleClass('scrolled-to-bottom', this.scrollTarget.scrollTop + this.scrollTarget.offsetHeight >= this.scrollTarget.scrollHeight);
  },
  _ensureTarget: function _ensureTarget() {
    // Read parentElement instead of parentNode in order to skip shadowRoots.
    this.dialogElement = this.dialogElement || this.parentElement; // Check if dialog implements paper-dialog-behavior. If not, fit
    // scrollTarget to host.

    if (this.dialogElement && this.dialogElement.behaviors && this.dialogElement.behaviors.indexOf(_polymer_paper_dialog_behavior_paper_dialog_behavior_js__WEBPACK_IMPORTED_MODULE_3__[/* PaperDialogBehaviorImpl */ "b"]) >= 0) {
      this.dialogElement.sizingTarget = this.scrollTarget;
      this.scrollTarget.classList.remove('fit');
    } else if (this.dialogElement) {
      this.scrollTarget.classList.add('fit');
    }
  }
});

/***/ }),

/***/ 57:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";

// EXTERNAL MODULE: ./node_modules/@polymer/polymer/polymer-legacy.js + 8 modules
var polymer_legacy = __webpack_require__(4);

// EXTERNAL MODULE: ./node_modules/@polymer/iron-flex-layout/iron-flex-layout.js
var iron_flex_layout = __webpack_require__(16);

// EXTERNAL MODULE: ./node_modules/@polymer/paper-styles/default-theme.js
var default_theme = __webpack_require__(14);

// EXTERNAL MODULE: ./node_modules/@polymer/paper-styles/typography.js
var typography = __webpack_require__(27);

// EXTERNAL MODULE: ./node_modules/@polymer/paper-styles/shadow.js
var shadow = __webpack_require__(40);

// CONCATENATED MODULE: ./node_modules/@polymer/paper-dialog-behavior/paper-dialog-shared-styles.js
/**
@license
Copyright (c) 2015 The Polymer Project Authors. All rights reserved.
This code may only be used under the BSD style license found at
http://polymer.github.io/LICENSE.txt The complete set of authors may be found at
http://polymer.github.io/AUTHORS.txt The complete set of contributors may be
found at http://polymer.github.io/CONTRIBUTORS.txt Code distributed by Google as
part of the polymer project is also subject to an additional IP rights grant
found at http://polymer.github.io/PATENTS.txt
*/

/*
### Styling

The following custom properties and mixins are available for styling.

Custom property | Description | Default
----------------|-------------|----------
`--paper-dialog-background-color` | Dialog background color | `--primary-background-color`
`--paper-dialog-color` | Dialog foreground color | `--primary-text-color`
`--paper-dialog` | Mixin applied to the dialog | `{}`
`--paper-dialog-title` | Mixin applied to the title (`<h2>`) element | `{}`
`--paper-dialog-button-color` | Button area foreground color | `--default-primary-color`
*/





var $_documentContainer = document.createElement('template');
$_documentContainer.setAttribute('style', 'display: none;');
$_documentContainer.innerHTML = "<dom-module id=\"paper-dialog-shared-styles\">\n  <template>\n    <style>\n      :host {\n        display: block;\n        margin: 24px 40px;\n\n        background: var(--paper-dialog-background-color, var(--primary-background-color));\n        color: var(--paper-dialog-color, var(--primary-text-color));\n\n        @apply --paper-font-body1;\n        @apply --shadow-elevation-16dp;\n        @apply --paper-dialog;\n      }\n\n      :host > ::slotted(*) {\n        margin-top: 20px;\n        padding: 0 24px;\n      }\n\n      :host > ::slotted(.no-padding) {\n        padding: 0;\n      }\n\n      \n      :host > ::slotted(*:first-child) {\n        margin-top: 24px;\n      }\n\n      :host > ::slotted(*:last-child) {\n        margin-bottom: 24px;\n      }\n\n      /* In 1.x, this selector was `:host > ::content h2`. In 2.x <slot> allows\n      to select direct children only, which increases the weight of this\n      selector, so we have to re-define first-child/last-child margins below. */\n      :host > ::slotted(h2) {\n        position: relative;\n        margin: 0;\n\n        @apply --paper-font-title;\n        @apply --paper-dialog-title;\n      }\n\n      /* Apply mixin again, in case it sets margin-top. */\n      :host > ::slotted(h2:first-child) {\n        margin-top: 24px;\n        @apply --paper-dialog-title;\n      }\n\n      /* Apply mixin again, in case it sets margin-bottom. */\n      :host > ::slotted(h2:last-child) {\n        margin-bottom: 24px;\n        @apply --paper-dialog-title;\n      }\n\n      :host > ::slotted(.paper-dialog-buttons),\n      :host > ::slotted(.buttons) {\n        position: relative;\n        padding: 8px 8px 8px 24px;\n        margin: 0;\n\n        color: var(--paper-dialog-button-color, var(--primary-color));\n\n        @apply --layout-horizontal;\n        @apply --layout-end-justified;\n      }\n    </style>\n  </template>\n</dom-module>";
document.head.appendChild($_documentContainer.content);
// EXTERNAL MODULE: ./node_modules/@polymer/neon-animation/neon-animation-runner-behavior.js + 1 modules
var neon_animation_runner_behavior = __webpack_require__(78);

// EXTERNAL MODULE: ./node_modules/@polymer/paper-dialog-behavior/paper-dialog-behavior.js
var paper_dialog_behavior = __webpack_require__(31);

// EXTERNAL MODULE: ./node_modules/@polymer/polymer/lib/legacy/polymer-fn.js
var polymer_fn = __webpack_require__(8);

// EXTERNAL MODULE: ./node_modules/@polymer/polymer/lib/utils/html-tag.js
var html_tag = __webpack_require__(7);

// CONCATENATED MODULE: ./node_modules/@polymer/paper-dialog/paper-dialog.js
function _templateObject() {
  var data = _taggedTemplateLiteral(["\n    <style include=\"paper-dialog-shared-styles\"></style>\n    <slot></slot>\n"]);

  _templateObject = function _templateObject() {
    return data;
  };

  return data;
}

function _taggedTemplateLiteral(strings, raw) { if (!raw) { raw = strings.slice(0); } return Object.freeze(Object.defineProperties(strings, { raw: { value: Object.freeze(raw) } })); }

/**
@license
Copyright (c) 2015 The Polymer Project Authors. All rights reserved.
This code may only be used under the BSD style license found at
http://polymer.github.io/LICENSE.txt The complete set of authors may be found at
http://polymer.github.io/AUTHORS.txt The complete set of contributors may be
found at http://polymer.github.io/CONTRIBUTORS.txt Code distributed by Google as
part of the polymer project is also subject to an additional IP rights grant
found at http://polymer.github.io/PATENTS.txt
*/






/**
Material design:
[Dialogs](https://www.google.com/design/spec/components/dialogs.html)

`<paper-dialog>` is a dialog with Material Design styling and optional
animations when it is opened or closed. It provides styles for a header, content
area, and an action area for buttons. You can use the
`<paper-dialog-scrollable>` element (in its own repository) if you need a
scrolling content area. To autofocus a specific child element after opening the
dialog, give it the `autofocus` attribute. See `Polymer.PaperDialogBehavior` and
`Polymer.IronOverlayBehavior` for specifics.

For example, the following code implements a dialog with a header, scrolling
content area and buttons. Focus will be given to the `dialog-confirm` button
when the dialog is opened.

    <paper-dialog>
      <h2>Header</h2>
      <paper-dialog-scrollable>
        Lorem ipsum...
      </paper-dialog-scrollable>
      <div class="buttons">
        <paper-button dialog-dismiss>Cancel</paper-button>
        <paper-button dialog-confirm autofocus>Accept</paper-button>
      </div>
    </paper-dialog>

### Styling

See the docs for `Polymer.PaperDialogBehavior` for the custom properties
available for styling this element.

### Animations

Set the `entry-animation` and/or `exit-animation` attributes to add an animation
when the dialog is opened or closed. See the documentation in
[PolymerElements/neon-animation](https://github.com/PolymerElements/neon-animation)
for more info.

For example:

    <script type="module">
      import '@polymer/neon-animation/animations/fade-out-animation.js';
      import '@polymer/neon-animation/animations/scale-up-animation.js';
    </script>

    <paper-dialog entry-animation="scale-up-animation"
                  exit-animation="fade-out-animation">
      <h2>Header</h2>
      <div>Dialog body</div>
    </paper-dialog>

### Accessibility

See the docs for `Polymer.PaperDialogBehavior` for accessibility features
implemented by this element.

@group Paper Elements
@element paper-dialog
@hero hero.svg
@demo demo/index.html
*/

Object(polymer_fn["a" /* Polymer */])({
  _template: Object(html_tag["a" /* html */])(_templateObject()),
  is: 'paper-dialog',
  behaviors: [paper_dialog_behavior["a" /* PaperDialogBehavior */], neon_animation_runner_behavior["a" /* NeonAnimationRunnerBehavior */]],
  listeners: {
    'neon-animation-finish': '_onNeonAnimationFinish'
  },
  _renderOpened: function _renderOpened() {
    this.cancelAnimation();
    this.playAnimation('entry');
  },
  _renderClosed: function _renderClosed() {
    this.cancelAnimation();
    this.playAnimation('exit');
  },
  _onNeonAnimationFinish: function _onNeonAnimationFinish() {
    if (this.opened) {
      this._finishRenderOpened();
    } else {
      this._finishRenderClosed();
    }
  }
});
// EXTERNAL MODULE: ./node_modules/@polymer/polymer/lib/legacy/class.js
var legacy_class = __webpack_require__(67);

// EXTERNAL MODULE: ./node_modules/@polymer/iron-overlay-behavior/iron-focusables-helper.js
var iron_focusables_helper = __webpack_require__(72);

// EXTERNAL MODULE: ./node_modules/@polymer/polymer/lib/legacy/polymer.dom.js + 1 modules
var polymer_dom = __webpack_require__(9);

// CONCATENATED MODULE: ./src/components/dialog/ha-iron-focusables-helper.js
/**
@license
Copyright (c) 2016 The Polymer Project Authors. All rights reserved.
This code may only be used under the BSD style license found at
http://polymer.github.io/LICENSE.txt The complete set of authors may be found at
http://polymer.github.io/AUTHORS.txt The complete set of contributors may be
found at http://polymer.github.io/CONTRIBUTORS.txt Code distributed by Google as
part of the polymer project is also subject to an additional IP rights grant
found at http://polymer.github.io/PATENTS.txt
*/

/*
  Fixes issue with not using shadow dom properly in iron-overlay-behavior/icon-focusables-helper.js
*/


var HaIronFocusablesHelper = {
  /**
   * Returns a sorted array of tabbable nodes, including the root node.
   * It searches the tabbable nodes in the light and shadow dom of the chidren,
   * sorting the result by tabindex.
   * @param {!Node} node
   * @return {!Array<!HTMLElement>}
   */
  getTabbableNodes: function getTabbableNodes(node) {
    var result = []; // If there is at least one element with tabindex > 0, we need to sort
    // the final array by tabindex.

    var needsSortByTabIndex = this._collectTabbableNodes(node, result);

    if (needsSortByTabIndex) {
      return iron_focusables_helper["a" /* IronFocusablesHelper */]._sortByTabIndex(result);
    }

    return result;
  },

  /**
   * Searches for nodes that are tabbable and adds them to the `result` array.
   * Returns if the `result` array needs to be sorted by tabindex.
   * @param {!Node} node The starting point for the search; added to `result`
   * if tabbable.
   * @param {!Array<!HTMLElement>} result
   * @return {boolean}
   * @private
   */
  _collectTabbableNodes: function _collectTabbableNodes(node, result) {
    // If not an element or not visible, no need to explore children.
    if (node.nodeType !== Node.ELEMENT_NODE || !iron_focusables_helper["a" /* IronFocusablesHelper */]._isVisible(node)) {
      return false;
    }

    var element =
    /** @type {!HTMLElement} */
    node;

    var tabIndex = iron_focusables_helper["a" /* IronFocusablesHelper */]._normalizedTabIndex(element);

    var needsSort = tabIndex > 0;

    if (tabIndex >= 0) {
      result.push(element);
    } // In ShadowDOM v1, tab order is affected by the order of distrubution.
    // E.g. getTabbableNodes(#root) in ShadowDOM v1 should return [#A, #B];
    // in ShadowDOM v0 tab order is not affected by the distrubution order,
    // in fact getTabbableNodes(#root) returns [#B, #A].
    //  <div id="root">
    //   <!-- shadow -->
    //     <slot name="a">
    //     <slot name="b">
    //   <!-- /shadow -->
    //   <input id="A" slot="a">
    //   <input id="B" slot="b" tabindex="1">
    //  </div>
    // TODO(valdrin) support ShadowDOM v1 when upgrading to Polymer v2.0.


    var children;

    if (element.localName === "content" || element.localName === "slot") {
      children = Object(polymer_dom["a" /* dom */])(element).getDistributedNodes();
    } else {
      // /////////////////////////
      // Use shadow root if possible, will check for distributed nodes.
      // THIS IS THE CHANGED LINE
      children = Object(polymer_dom["a" /* dom */])(element.shadowRoot || element.root || element).children; // /////////////////////////
    }

    for (var i = 0; i < children.length; i++) {
      // Ensure method is always invoked to collect tabbable children.
      needsSort = this._collectTabbableNodes(children[i], result) || needsSort;
    }

    return needsSort;
  }
};
// CONCATENATED MODULE: ./src/components/dialog/ha-paper-dialog.ts
/* unused harmony export HaPaperDialog */
function _typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { _typeof = function _typeof(obj) { return typeof obj; }; } else { _typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return _typeof(obj); }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) _setPrototypeOf(subClass, superClass); }

function _setPrototypeOf(o, p) { _setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return _setPrototypeOf(o, p); }

function _createSuper(Derived) { return function () { var Super = _getPrototypeOf(Derived), result; if (_isNativeReflectConstruct()) { var NewTarget = _getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return _possibleConstructorReturn(this, result); }; }

function _possibleConstructorReturn(self, call) { if (call && (_typeof(call) === "object" || typeof call === "function")) { return call; } return _assertThisInitialized(self); }

function _assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function _isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Date.prototype.toString.call(Reflect.construct(Date, [], function () {})); return true; } catch (e) { return false; } }

function _getPrototypeOf(o) { _getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return _getPrototypeOf(o); }




var paperDialogClass = customElements.get("paper-dialog"); // behavior that will override existing iron-overlay-behavior and call the fixed implementation

var haTabFixBehaviorImpl = {
  get _focusableNodes() {
    return HaIronFocusablesHelper.getTabbableNodes(this);
  }

}; // paper-dialog that uses the haTabFixBehaviorImpl behvaior
// export class HaPaperDialog extends paperDialogClass {}
// @ts-ignore

var HaPaperDialog = /*#__PURE__*/function (_mixinBehaviors) {
  _inherits(HaPaperDialog, _mixinBehaviors);

  var _super = _createSuper(HaPaperDialog);

  function HaPaperDialog() {
    _classCallCheck(this, HaPaperDialog);

    return _super.apply(this, arguments);
  }

  return HaPaperDialog;
}(Object(legacy_class["b" /* mixinBehaviors */])([haTabFixBehaviorImpl], paperDialogClass));
// @ts-ignore
customElements.define("ha-paper-dialog", HaPaperDialog);

/***/ })

}]);