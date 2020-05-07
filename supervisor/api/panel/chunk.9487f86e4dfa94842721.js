(self["webpackJsonp"] = self["webpackJsonp"] || []).push([[11],[
/* 0 */,
/* 1 */,
/* 2 */,
/* 3 */,
/* 4 */,
/* 5 */,
/* 6 */,
/* 7 */,
/* 8 */,
/* 9 */,
/* 10 */,
/* 11 */,
/* 12 */,
/* 13 */,
/* 14 */,
/* 15 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


var YAMLException = __webpack_require__(51);

var TYPE_CONSTRUCTOR_OPTIONS = ['kind', 'resolve', 'construct', 'instanceOf', 'predicate', 'represent', 'defaultStyle', 'styleAliases'];
var YAML_NODE_KINDS = ['scalar', 'sequence', 'mapping'];

function compileStyleAliases(map) {
  var result = {};

  if (map !== null) {
    Object.keys(map).forEach(function (style) {
      map[style].forEach(function (alias) {
        result[String(alias)] = style;
      });
    });
  }

  return result;
}

function Type(tag, options) {
  options = options || {};
  Object.keys(options).forEach(function (name) {
    if (TYPE_CONSTRUCTOR_OPTIONS.indexOf(name) === -1) {
      throw new YAMLException('Unknown option "' + name + '" is met in definition of "' + tag + '" YAML type.');
    }
  }); // TODO: Add tag format check.

  this.tag = tag;
  this.kind = options['kind'] || null;

  this.resolve = options['resolve'] || function () {
    return true;
  };

  this.construct = options['construct'] || function (data) {
    return data;
  };

  this.instanceOf = options['instanceOf'] || null;
  this.predicate = options['predicate'] || null;
  this.represent = options['represent'] || null;
  this.defaultStyle = options['defaultStyle'] || null;
  this.styleAliases = compileStyleAliases(options['styleAliases'] || null);

  if (YAML_NODE_KINDS.indexOf(this.kind) === -1) {
    throw new YAMLException('Unknown kind "' + this.kind + '" is specified for "' + tag + '" YAML type.');
  }
}

module.exports = Type;

/***/ }),
/* 16 */,
/* 17 */,
/* 18 */,
/* 19 */,
/* 20 */,
/* 21 */,
/* 22 */,
/* 23 */,
/* 24 */,
/* 25 */,
/* 26 */,
/* 27 */,
/* 28 */,
/* 29 */,
/* 30 */,
/* 31 */,
/* 32 */,
/* 33 */,
/* 34 */,
/* 35 */,
/* 36 */,
/* 37 */,
/* 38 */,
/* 39 */,
/* 40 */,
/* 41 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


function _typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { _typeof = function _typeof(obj) { return typeof obj; }; } else { _typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return _typeof(obj); }

function isNothing(subject) {
  return typeof subject === 'undefined' || subject === null;
}

function isObject(subject) {
  return _typeof(subject) === 'object' && subject !== null;
}

function toArray(sequence) {
  if (Array.isArray(sequence)) return sequence;else if (isNothing(sequence)) return [];
  return [sequence];
}

function extend(target, source) {
  var index, length, key, sourceKeys;

  if (source) {
    sourceKeys = Object.keys(source);

    for (index = 0, length = sourceKeys.length; index < length; index += 1) {
      key = sourceKeys[index];
      target[key] = source[key];
    }
  }

  return target;
}

function repeat(string, count) {
  var result = '',
      cycle;

  for (cycle = 0; cycle < count; cycle += 1) {
    result += string;
  }

  return result;
}

function isNegativeZero(number) {
  return number === 0 && Number.NEGATIVE_INFINITY === 1 / number;
}

module.exports.isNothing = isNothing;
module.exports.isObject = isObject;
module.exports.toArray = toArray;
module.exports.repeat = repeat;
module.exports.isNegativeZero = isNegativeZero;
module.exports.extend = extend;

/***/ }),
/* 42 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

/*eslint-disable max-len*/

var common = __webpack_require__(41);

var YAMLException = __webpack_require__(51);

var Type = __webpack_require__(15);

function compileList(schema, name, result) {
  var exclude = [];
  schema.include.forEach(function (includedSchema) {
    result = compileList(includedSchema, name, result);
  });
  schema[name].forEach(function (currentType) {
    result.forEach(function (previousType, previousIndex) {
      if (previousType.tag === currentType.tag && previousType.kind === currentType.kind) {
        exclude.push(previousIndex);
      }
    });
    result.push(currentType);
  });
  return result.filter(function (type, index) {
    return exclude.indexOf(index) === -1;
  });
}

function compileMap()
/* lists... */
{
  var result = {
    scalar: {},
    sequence: {},
    mapping: {},
    fallback: {}
  },
      index,
      length;

  function collectType(type) {
    result[type.kind][type.tag] = result['fallback'][type.tag] = type;
  }

  for (index = 0, length = arguments.length; index < length; index += 1) {
    arguments[index].forEach(collectType);
  }

  return result;
}

function Schema(definition) {
  this.include = definition.include || [];
  this.implicit = definition.implicit || [];
  this.explicit = definition.explicit || [];
  this.implicit.forEach(function (type) {
    if (type.loadKind && type.loadKind !== 'scalar') {
      throw new YAMLException('There is a non-scalar type in the implicit list of a schema. Implicit resolving of such types is not supported.');
    }
  });
  this.compiledImplicit = compileList(this, 'implicit', []);
  this.compiledExplicit = compileList(this, 'explicit', []);
  this.compiledTypeMap = compileMap(this.compiledImplicit, this.compiledExplicit);
}

Schema.DEFAULT = null;

Schema.create = function createSchema() {
  var schemas, types;

  switch (arguments.length) {
    case 1:
      schemas = Schema.DEFAULT;
      types = arguments[0];
      break;

    case 2:
      schemas = arguments[0];
      types = arguments[1];
      break;

    default:
      throw new YAMLException('Wrong number of arguments for Schema.create function');
  }

  schemas = common.toArray(schemas);
  types = common.toArray(types);

  if (!schemas.every(function (schema) {
    return schema instanceof Schema;
  })) {
    throw new YAMLException('Specified list of super schemas (or a single Schema object) contains a non-Schema object.');
  }

  if (!types.every(function (type) {
    return type instanceof Type;
  })) {
    throw new YAMLException('Specified list of YAML types (or a single Type object) contains a non-Type object.');
  }

  return new Schema({
    include: schemas,
    explicit: types
  });
};

module.exports = Schema;

/***/ }),
/* 43 */,
/* 44 */,
/* 45 */,
/* 46 */,
/* 47 */,
/* 48 */,
/* 49 */,
/* 50 */,
/* 51 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";
// YAML error class. http://stackoverflow.com/questions/8458984
//


function YAMLException(reason, mark) {
  // Super constructor
  Error.call(this);
  this.name = 'YAMLException';
  this.reason = reason;
  this.mark = mark;
  this.message = (this.reason || '(unknown reason)') + (this.mark ? ' ' + this.mark.toString() : ''); // Include stack trace in error object

  if (Error.captureStackTrace) {
    // Chrome and NodeJS
    Error.captureStackTrace(this, this.constructor);
  } else {
    // FF, IE 10+ and Safari 6+. Fallback for others
    this.stack = new Error().stack || '';
  }
} // Inherit from Error


YAMLException.prototype = Object.create(Error.prototype);
YAMLException.prototype.constructor = YAMLException;

YAMLException.prototype.toString = function toString(compact) {
  var result = this.name + ': ';
  result += this.reason || '(unknown reason)';

  if (!compact && this.mark) {
    result += ' ' + this.mark.toString();
  }

  return result;
};

module.exports = YAMLException;

/***/ }),
/* 52 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";
// JS-YAML's default schema for `safeLoad` function.
// It is not described in the YAML specification.
//
// This schema is based on standard YAML's Core schema and includes most of
// extra types described at YAML tag repository. (http://yaml.org/type/)


var Schema = __webpack_require__(42);

module.exports = new Schema({
  include: [__webpack_require__(131)],
  implicit: [__webpack_require__(163), __webpack_require__(164)],
  explicit: [__webpack_require__(165), __webpack_require__(171), __webpack_require__(172), __webpack_require__(173)]
});

/***/ }),
/* 53 */,
/* 54 */,
/* 55 */,
/* 56 */,
/* 57 */,
/* 58 */,
/* 59 */,
/* 60 */,
/* 61 */,
/* 62 */,
/* 63 */,
/* 64 */,
/* 65 */,
/* 66 */,
/* 67 */,
/* 68 */,
/* 69 */,
/* 70 */,
/* 71 */,
/* 72 */,
/* 73 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";
// JS-YAML's default schema for `load` function.
// It is not described in the YAML specification.
//
// This schema is based on JS-YAML's default safe schema and includes
// JavaScript-specific types: !!js/undefined, !!js/regexp and !!js/function.
//
// Also this schema is used as default base schema at `Schema.create` function.


var Schema = __webpack_require__(42);

module.exports = Schema.DEFAULT = new Schema({
  include: [__webpack_require__(52)],
  explicit: [__webpack_require__(174), __webpack_require__(175), __webpack_require__(176)]
});

/***/ }),
/* 74 */,
/* 75 */,
/* 76 */,
/* 77 */,
/* 78 */,
/* 79 */,
/* 80 */,
/* 81 */,
/* 82 */,
/* 83 */,
/* 84 */,
/* 85 */,
/* 86 */,
/* 87 */,
/* 88 */,
/* 89 */,
/* 90 */,
/* 91 */,
/* 92 */,
/* 93 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";
// Standard YAML's Failsafe schema.
// http://www.yaml.org/spec/1.2/spec.html#id2802346


var Schema = __webpack_require__(42);

module.exports = new Schema({
  explicit: [__webpack_require__(156), __webpack_require__(157), __webpack_require__(158)]
});

/***/ }),
/* 94 */,
/* 95 */
/***/ (function(module, exports) {

function addMethods(worker, methods) {
  var c = 0;
  var callbacks = {};
  worker.addEventListener('message', function (e) {
    var d = e.data;

    if (d.type !== 'RPC') {
      return;
    }

    if (d.id) {
      var f = callbacks[d.id];

      if (f) {
        delete callbacks[d.id];

        if (d.error) {
          f[1](Object.assign(Error(d.error.message), d.error));
        } else {
          f[0](d.result);
        }
      }
    } else {
      var evt = document.createEvent('Event');
      evt.initEvent(d.method, false, false);
      evt.data = d.params;
      worker.dispatchEvent(evt);
    }
  });
  methods.forEach(function (method) {
    worker[method] = function () {
      var params = [],
          len = arguments.length;

      while (len--) {
        params[len] = arguments[len];
      }

      return new Promise(function (a, b) {
        var id = ++c;
        callbacks[id] = [a, b];
        worker.postMessage({
          type: 'RPC',
          id: id,
          method: method,
          params: params
        });
      });
    };
  });
}

module.exports = addMethods;

/***/ }),
/* 96 */,
/* 97 */,
/* 98 */,
/* 99 */,
/* 100 */,
/* 101 */,
/* 102 */,
/* 103 */,
/* 104 */,
/* 105 */,
/* 106 */,
/* 107 */,
/* 108 */,
/* 109 */,
/* 110 */,
/* 111 */,
/* 112 */,
/* 113 */,
/* 114 */,
/* 115 */,
/* 116 */,
/* 117 */,
/* 118 */,
/* 119 */,
/* 120 */,
/* 121 */,
/* 122 */,
/* 123 */,
/* 124 */,
/* 125 */,
/* 126 */,
/* 127 */,
/* 128 */,
/* 129 */,
/* 130 */,
/* 131 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";
// Standard YAML's Core schema.
// http://www.yaml.org/spec/1.2/spec.html#id2804923
//
// NOTE: JS-YAML does not support schema-specific tag resolution restrictions.
// So, Core schema has no distinctions from JSON schema is JS-YAML.


var Schema = __webpack_require__(42);

module.exports = new Schema({
  include: [__webpack_require__(132)]
});

/***/ }),
/* 132 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";
// Standard YAML's JSON schema.
// http://www.yaml.org/spec/1.2/spec.html#id2803231
//
// NOTE: JS-YAML does not support schema-specific tag resolution restrictions.
// So, this schema is not such strict as defined in the YAML specification.
// It allows numbers in binary notaion, use `Null` and `NULL` as `null`, etc.


var Schema = __webpack_require__(42);

module.exports = new Schema({
  include: [__webpack_require__(93)],
  implicit: [__webpack_require__(159), __webpack_require__(160), __webpack_require__(161), __webpack_require__(162)]
});

/***/ }),
/* 133 */,
/* 134 */,
/* 135 */,
/* 136 */,
/* 137 */,
/* 138 */,
/* 139 */,
/* 140 */,
/* 141 */,
/* 142 */,
/* 143 */,
/* 144 */,
/* 145 */,
/* 146 */,
/* 147 */,
/* 148 */,
/* 149 */,
/* 150 */
/***/ (function(module, exports) {

// Copyright 2014 Google Inc. All rights reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
//     You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//     See the License for the specific language governing permissions and
// limitations under the License.
!function (a, b) {
  var c = {},
      d = {},
      e = {};
  !function (a, b) {
    function c(a) {
      if ("number" == typeof a) return a;
      var b = {};

      for (var c in a) {
        b[c] = a[c];
      }

      return b;
    }

    function d() {
      this._delay = 0, this._endDelay = 0, this._fill = "none", this._iterationStart = 0, this._iterations = 1, this._duration = 0, this._playbackRate = 1, this._direction = "normal", this._easing = "linear", this._easingFunction = x;
    }

    function e() {
      return a.isDeprecated("Invalid timing inputs", "2016-03-02", "TypeError exceptions will be thrown instead.", !0);
    }

    function f(b, c, e) {
      var f = new d();
      return c && (f.fill = "both", f.duration = "auto"), "number" != typeof b || isNaN(b) ? void 0 !== b && Object.getOwnPropertyNames(b).forEach(function (c) {
        if ("auto" != b[c]) {
          if (("number" == typeof f[c] || "duration" == c) && ("number" != typeof b[c] || isNaN(b[c]))) return;
          if ("fill" == c && -1 == v.indexOf(b[c])) return;
          if ("direction" == c && -1 == w.indexOf(b[c])) return;
          if ("playbackRate" == c && 1 !== b[c] && a.isDeprecated("AnimationEffectTiming.playbackRate", "2014-11-28", "Use Animation.playbackRate instead.")) return;
          f[c] = b[c];
        }
      }) : f.duration = b, f;
    }

    function g(a) {
      return "number" == typeof a && (a = isNaN(a) ? {
        duration: 0
      } : {
        duration: a
      }), a;
    }

    function h(b, c) {
      return b = a.numericTimingToObject(b), f(b, c);
    }

    function i(a, b, c, d) {
      return a < 0 || a > 1 || c < 0 || c > 1 ? x : function (e) {
        function f(a, b, c) {
          return 3 * a * (1 - c) * (1 - c) * c + 3 * b * (1 - c) * c * c + c * c * c;
        }

        if (e <= 0) {
          var g = 0;
          return a > 0 ? g = b / a : !b && c > 0 && (g = d / c), g * e;
        }

        if (e >= 1) {
          var h = 0;
          return c < 1 ? h = (d - 1) / (c - 1) : 1 == c && a < 1 && (h = (b - 1) / (a - 1)), 1 + h * (e - 1);
        }

        for (var i = 0, j = 1; i < j;) {
          var k = (i + j) / 2,
              l = f(a, c, k);
          if (Math.abs(e - l) < 1e-5) return f(b, d, k);
          l < e ? i = k : j = k;
        }

        return f(b, d, k);
      };
    }

    function j(a, b) {
      return function (c) {
        if (c >= 1) return 1;
        var d = 1 / a;
        return (c += b * d) - c % d;
      };
    }

    function k(a) {
      C || (C = document.createElement("div").style), C.animationTimingFunction = "", C.animationTimingFunction = a;
      var b = C.animationTimingFunction;
      if ("" == b && e()) throw new TypeError(a + " is not a valid value for easing");
      return b;
    }

    function l(a) {
      if ("linear" == a) return x;
      var b = E.exec(a);
      if (b) return i.apply(this, b.slice(1).map(Number));
      var c = F.exec(a);
      return c ? j(Number(c[1]), {
        start: y,
        middle: z,
        end: A
      }[c[2]]) : B[a] || x;
    }

    function m(a) {
      return Math.abs(n(a) / a.playbackRate);
    }

    function n(a) {
      return 0 === a.duration || 0 === a.iterations ? 0 : a.duration * a.iterations;
    }

    function o(a, b, c) {
      if (null == b) return G;
      var d = c.delay + a + c.endDelay;
      return b < Math.min(c.delay, d) ? H : b >= Math.min(c.delay + a, d) ? I : J;
    }

    function p(a, b, c, d, e) {
      switch (d) {
        case H:
          return "backwards" == b || "both" == b ? 0 : null;

        case J:
          return c - e;

        case I:
          return "forwards" == b || "both" == b ? a : null;

        case G:
          return null;
      }
    }

    function q(a, b, c, d, e) {
      var f = e;
      return 0 === a ? b !== H && (f += c) : f += d / a, f;
    }

    function r(a, b, c, d, e, f) {
      var g = a === 1 / 0 ? b % 1 : a % 1;
      return 0 !== g || c !== I || 0 === d || 0 === e && 0 !== f || (g = 1), g;
    }

    function s(a, b, c, d) {
      return a === I && b === 1 / 0 ? 1 / 0 : 1 === c ? Math.floor(d) - 1 : Math.floor(d);
    }

    function t(a, b, c) {
      var d = a;

      if ("normal" !== a && "reverse" !== a) {
        var e = b;
        "alternate-reverse" === a && (e += 1), d = "normal", e !== 1 / 0 && e % 2 != 0 && (d = "reverse");
      }

      return "normal" === d ? c : 1 - c;
    }

    function u(a, b, c) {
      var d = o(a, b, c),
          e = p(a, c.fill, b, d, c.delay);
      if (null === e) return null;
      var f = q(c.duration, d, c.iterations, e, c.iterationStart),
          g = r(f, c.iterationStart, d, c.iterations, e, c.duration),
          h = s(d, c.iterations, g, f),
          i = t(c.direction, h, g);
      return c._easingFunction(i);
    }

    var v = "backwards|forwards|both|none".split("|"),
        w = "reverse|alternate|alternate-reverse".split("|"),
        x = function x(a) {
      return a;
    };

    d.prototype = {
      _setMember: function _setMember(b, c) {
        this["_" + b] = c, this._effect && (this._effect._timingInput[b] = c, this._effect._timing = a.normalizeTimingInput(this._effect._timingInput), this._effect.activeDuration = a.calculateActiveDuration(this._effect._timing), this._effect._animation && this._effect._animation._rebuildUnderlyingAnimation());
      },

      get playbackRate() {
        return this._playbackRate;
      },

      set delay(a) {
        this._setMember("delay", a);
      },

      get delay() {
        return this._delay;
      },

      set endDelay(a) {
        this._setMember("endDelay", a);
      },

      get endDelay() {
        return this._endDelay;
      },

      set fill(a) {
        this._setMember("fill", a);
      },

      get fill() {
        return this._fill;
      },

      set iterationStart(a) {
        if ((isNaN(a) || a < 0) && e()) throw new TypeError("iterationStart must be a non-negative number, received: " + timing.iterationStart);

        this._setMember("iterationStart", a);
      },

      get iterationStart() {
        return this._iterationStart;
      },

      set duration(a) {
        if ("auto" != a && (isNaN(a) || a < 0) && e()) throw new TypeError("duration must be non-negative or auto, received: " + a);

        this._setMember("duration", a);
      },

      get duration() {
        return this._duration;
      },

      set direction(a) {
        this._setMember("direction", a);
      },

      get direction() {
        return this._direction;
      },

      set easing(a) {
        this._easingFunction = l(k(a)), this._setMember("easing", a);
      },

      get easing() {
        return this._easing;
      },

      set iterations(a) {
        if ((isNaN(a) || a < 0) && e()) throw new TypeError("iterations must be non-negative, received: " + a);

        this._setMember("iterations", a);
      },

      get iterations() {
        return this._iterations;
      }

    };
    var y = 1,
        z = .5,
        A = 0,
        B = {
      ease: i(.25, .1, .25, 1),
      "ease-in": i(.42, 0, 1, 1),
      "ease-out": i(0, 0, .58, 1),
      "ease-in-out": i(.42, 0, .58, 1),
      "step-start": j(1, y),
      "step-middle": j(1, z),
      "step-end": j(1, A)
    },
        C = null,
        D = "\\s*(-?\\d+\\.?\\d*|-?\\.\\d+)\\s*",
        E = new RegExp("cubic-bezier\\(" + D + "," + D + "," + D + "," + D + "\\)"),
        F = /steps\(\s*(\d+)\s*,\s*(start|middle|end)\s*\)/,
        G = 0,
        H = 1,
        I = 2,
        J = 3;
    a.cloneTimingInput = c, a.makeTiming = f, a.numericTimingToObject = g, a.normalizeTimingInput = h, a.calculateActiveDuration = m, a.calculateIterationProgress = u, a.calculatePhase = o, a.normalizeEasing = k, a.parseEasingFunction = l;
  }(c), function (a, b) {
    function c(a, b) {
      return a in k ? k[a][b] || b : b;
    }

    function d(a) {
      return "display" === a || 0 === a.lastIndexOf("animation", 0) || 0 === a.lastIndexOf("transition", 0);
    }

    function e(a, b, e) {
      if (!d(a)) {
        var f = h[a];

        if (f) {
          i.style[a] = b;

          for (var g in f) {
            var j = f[g],
                k = i.style[j];
            e[j] = c(j, k);
          }
        } else e[a] = c(a, b);
      }
    }

    function f(a) {
      var b = [];

      for (var c in a) {
        if (!(c in ["easing", "offset", "composite"])) {
          var d = a[c];
          Array.isArray(d) || (d = [d]);

          for (var e, f = d.length, g = 0; g < f; g++) {
            e = {}, e.offset = "offset" in a ? a.offset : 1 == f ? 1 : g / (f - 1), "easing" in a && (e.easing = a.easing), "composite" in a && (e.composite = a.composite), e[c] = d[g], b.push(e);
          }
        }
      }

      return b.sort(function (a, b) {
        return a.offset - b.offset;
      }), b;
    }

    function g(b) {
      function c() {
        var a = d.length;
        null == d[a - 1].offset && (d[a - 1].offset = 1), a > 1 && null == d[0].offset && (d[0].offset = 0);

        for (var b = 0, c = d[0].offset, e = 1; e < a; e++) {
          var f = d[e].offset;

          if (null != f) {
            for (var g = 1; g < e - b; g++) {
              d[b + g].offset = c + (f - c) * g / (e - b);
            }

            b = e, c = f;
          }
        }
      }

      if (null == b) return [];
      window.Symbol && Symbol.iterator && Array.prototype.from && b[Symbol.iterator] && (b = Array.from(b)), Array.isArray(b) || (b = f(b));

      for (var d = b.map(function (b) {
        var c = {};

        for (var d in b) {
          var f = b[d];

          if ("offset" == d) {
            if (null != f) {
              if (f = Number(f), !isFinite(f)) throw new TypeError("Keyframe offsets must be numbers.");
              if (f < 0 || f > 1) throw new TypeError("Keyframe offsets must be between 0 and 1.");
            }
          } else if ("composite" == d) {
            if ("add" == f || "accumulate" == f) throw {
              type: DOMException.NOT_SUPPORTED_ERR,
              name: "NotSupportedError",
              message: "add compositing is not supported"
            };
            if ("replace" != f) throw new TypeError("Invalid composite mode " + f + ".");
          } else f = "easing" == d ? a.normalizeEasing(f) : "" + f;

          e(d, f, c);
        }

        return void 0 == c.offset && (c.offset = null), void 0 == c.easing && (c.easing = "linear"), c;
      }), g = !0, h = -1 / 0, i = 0; i < d.length; i++) {
        var j = d[i].offset;

        if (null != j) {
          if (j < h) throw new TypeError("Keyframes are not loosely sorted by offset. Sort or specify offsets.");
          h = j;
        } else g = !1;
      }

      return d = d.filter(function (a) {
        return a.offset >= 0 && a.offset <= 1;
      }), g || c(), d;
    }

    var h = {
      background: ["backgroundImage", "backgroundPosition", "backgroundSize", "backgroundRepeat", "backgroundAttachment", "backgroundOrigin", "backgroundClip", "backgroundColor"],
      border: ["borderTopColor", "borderTopStyle", "borderTopWidth", "borderRightColor", "borderRightStyle", "borderRightWidth", "borderBottomColor", "borderBottomStyle", "borderBottomWidth", "borderLeftColor", "borderLeftStyle", "borderLeftWidth"],
      borderBottom: ["borderBottomWidth", "borderBottomStyle", "borderBottomColor"],
      borderColor: ["borderTopColor", "borderRightColor", "borderBottomColor", "borderLeftColor"],
      borderLeft: ["borderLeftWidth", "borderLeftStyle", "borderLeftColor"],
      borderRadius: ["borderTopLeftRadius", "borderTopRightRadius", "borderBottomRightRadius", "borderBottomLeftRadius"],
      borderRight: ["borderRightWidth", "borderRightStyle", "borderRightColor"],
      borderTop: ["borderTopWidth", "borderTopStyle", "borderTopColor"],
      borderWidth: ["borderTopWidth", "borderRightWidth", "borderBottomWidth", "borderLeftWidth"],
      flex: ["flexGrow", "flexShrink", "flexBasis"],
      font: ["fontFamily", "fontSize", "fontStyle", "fontVariant", "fontWeight", "lineHeight"],
      margin: ["marginTop", "marginRight", "marginBottom", "marginLeft"],
      outline: ["outlineColor", "outlineStyle", "outlineWidth"],
      padding: ["paddingTop", "paddingRight", "paddingBottom", "paddingLeft"]
    },
        i = document.createElementNS("http://www.w3.org/1999/xhtml", "div"),
        j = {
      thin: "1px",
      medium: "3px",
      thick: "5px"
    },
        k = {
      borderBottomWidth: j,
      borderLeftWidth: j,
      borderRightWidth: j,
      borderTopWidth: j,
      fontSize: {
        "xx-small": "60%",
        "x-small": "75%",
        small: "89%",
        medium: "100%",
        large: "120%",
        "x-large": "150%",
        "xx-large": "200%"
      },
      fontWeight: {
        normal: "400",
        bold: "700"
      },
      outlineWidth: j,
      textShadow: {
        none: "0px 0px 0px transparent"
      },
      boxShadow: {
        none: "0px 0px 0px 0px transparent"
      }
    };
    a.convertToArrayForm = f, a.normalizeKeyframes = g;
  }(c), function (a) {
    var b = {};
    a.isDeprecated = function (a, c, d, e) {
      var f = e ? "are" : "is",
          g = new Date(),
          h = new Date(c);
      return h.setMonth(h.getMonth() + 3), !(g < h && (a in b || console.warn("Web Animations: " + a + " " + f + " deprecated and will stop working on " + h.toDateString() + ". " + d), b[a] = !0, 1));
    }, a.deprecated = function (b, c, d, e) {
      var f = e ? "are" : "is";
      if (a.isDeprecated(b, c, d, e)) throw new Error(b + " " + f + " no longer supported. " + d);
    };
  }(c), function () {
    if (document.documentElement.animate) {
      var a = document.documentElement.animate([], 0),
          b = !0;
      if (a && (b = !1, "play|currentTime|pause|reverse|playbackRate|cancel|finish|startTime|playState".split("|").forEach(function (c) {
        void 0 === a[c] && (b = !0);
      })), !b) return;
    }

    !function (a, b, c) {
      function d(a) {
        for (var b = {}, c = 0; c < a.length; c++) {
          for (var d in a[c]) {
            if ("offset" != d && "easing" != d && "composite" != d) {
              var e = {
                offset: a[c].offset,
                easing: a[c].easing,
                value: a[c][d]
              };
              b[d] = b[d] || [], b[d].push(e);
            }
          }
        }

        for (var f in b) {
          var g = b[f];
          if (0 != g[0].offset || 1 != g[g.length - 1].offset) throw {
            type: DOMException.NOT_SUPPORTED_ERR,
            name: "NotSupportedError",
            message: "Partial keyframes are not supported"
          };
        }

        return b;
      }

      function e(c) {
        var d = [];

        for (var e in c) {
          for (var f = c[e], g = 0; g < f.length - 1; g++) {
            var h = g,
                i = g + 1,
                j = f[h].offset,
                k = f[i].offset,
                l = j,
                m = k;
            0 == g && (l = -1 / 0, 0 == k && (i = h)), g == f.length - 2 && (m = 1 / 0, 1 == j && (h = i)), d.push({
              applyFrom: l,
              applyTo: m,
              startOffset: f[h].offset,
              endOffset: f[i].offset,
              easingFunction: a.parseEasingFunction(f[h].easing),
              property: e,
              interpolation: b.propertyInterpolation(e, f[h].value, f[i].value)
            });
          }
        }

        return d.sort(function (a, b) {
          return a.startOffset - b.startOffset;
        }), d;
      }

      b.convertEffectInput = function (c) {
        var f = a.normalizeKeyframes(c),
            g = d(f),
            h = e(g);
        return function (a, c) {
          if (null != c) h.filter(function (a) {
            return c >= a.applyFrom && c < a.applyTo;
          }).forEach(function (d) {
            var e = c - d.startOffset,
                f = d.endOffset - d.startOffset,
                g = 0 == f ? 0 : d.easingFunction(e / f);
            b.apply(a, d.property, d.interpolation(g));
          });else for (var d in g) {
            "offset" != d && "easing" != d && "composite" != d && b.clear(a, d);
          }
        };
      };
    }(c, d), function (a, b, c) {
      function d(a) {
        return a.replace(/-(.)/g, function (a, b) {
          return b.toUpperCase();
        });
      }

      function e(a, b, c) {
        h[c] = h[c] || [], h[c].push([a, b]);
      }

      function f(a, b, c) {
        for (var f = 0; f < c.length; f++) {
          e(a, b, d(c[f]));
        }
      }

      function g(c, e, f) {
        var g = c;
        /-/.test(c) && !a.isDeprecated("Hyphenated property names", "2016-03-22", "Use camelCase instead.", !0) && (g = d(c)), "initial" != e && "initial" != f || ("initial" == e && (e = i[g]), "initial" == f && (f = i[g]));

        for (var j = e == f ? [] : h[g], k = 0; j && k < j.length; k++) {
          var l = j[k][0](e),
              m = j[k][0](f);

          if (void 0 !== l && void 0 !== m) {
            var n = j[k][1](l, m);

            if (n) {
              var o = b.Interpolation.apply(null, n);
              return function (a) {
                return 0 == a ? e : 1 == a ? f : o(a);
              };
            }
          }
        }

        return b.Interpolation(!1, !0, function (a) {
          return a ? f : e;
        });
      }

      var h = {};
      b.addPropertiesHandler = f;
      var i = {
        backgroundColor: "transparent",
        backgroundPosition: "0% 0%",
        borderBottomColor: "currentColor",
        borderBottomLeftRadius: "0px",
        borderBottomRightRadius: "0px",
        borderBottomWidth: "3px",
        borderLeftColor: "currentColor",
        borderLeftWidth: "3px",
        borderRightColor: "currentColor",
        borderRightWidth: "3px",
        borderSpacing: "2px",
        borderTopColor: "currentColor",
        borderTopLeftRadius: "0px",
        borderTopRightRadius: "0px",
        borderTopWidth: "3px",
        bottom: "auto",
        clip: "rect(0px, 0px, 0px, 0px)",
        color: "black",
        fontSize: "100%",
        fontWeight: "400",
        height: "auto",
        left: "auto",
        letterSpacing: "normal",
        lineHeight: "120%",
        marginBottom: "0px",
        marginLeft: "0px",
        marginRight: "0px",
        marginTop: "0px",
        maxHeight: "none",
        maxWidth: "none",
        minHeight: "0px",
        minWidth: "0px",
        opacity: "1.0",
        outlineColor: "invert",
        outlineOffset: "0px",
        outlineWidth: "3px",
        paddingBottom: "0px",
        paddingLeft: "0px",
        paddingRight: "0px",
        paddingTop: "0px",
        right: "auto",
        strokeDasharray: "none",
        strokeDashoffset: "0px",
        textIndent: "0px",
        textShadow: "0px 0px 0px transparent",
        top: "auto",
        transform: "",
        verticalAlign: "0px",
        visibility: "visible",
        width: "auto",
        wordSpacing: "normal",
        zIndex: "auto"
      };
      b.propertyInterpolation = g;
    }(c, d), function (a, b, c) {
      function d(b) {
        var c = a.calculateActiveDuration(b),
            d = function d(_d) {
          return a.calculateIterationProgress(c, _d, b);
        };

        return d._totalDuration = b.delay + c + b.endDelay, d;
      }

      b.KeyframeEffect = function (c, e, f, g) {
        var h,
            i = d(a.normalizeTimingInput(f)),
            j = b.convertEffectInput(e),
            k = function k() {
          j(c, h);
        };

        return k._update = function (a) {
          return null !== (h = i(a));
        }, k._clear = function () {
          j(c, null);
        }, k._hasSameTarget = function (a) {
          return c === a;
        }, k._target = c, k._totalDuration = i._totalDuration, k._id = g, k;
      };
    }(c, d), function (a, b) {
      a.apply = function (b, c, d) {
        b.style[a.propertyName(c)] = d;
      }, a.clear = function (b, c) {
        b.style[a.propertyName(c)] = "";
      };
    }(d), function (a) {
      window.Element.prototype.animate = function (b, c) {
        var d = "";
        return c && c.id && (d = c.id), a.timeline._play(a.KeyframeEffect(this, b, c, d));
      };
    }(d), function (a, b) {
      function c(a, b, d) {
        if ("number" == typeof a && "number" == typeof b) return a * (1 - d) + b * d;
        if ("boolean" == typeof a && "boolean" == typeof b) return d < .5 ? a : b;

        if (a.length == b.length) {
          for (var e = [], f = 0; f < a.length; f++) {
            e.push(c(a[f], b[f], d));
          }

          return e;
        }

        throw "Mismatched interpolation arguments " + a + ":" + b;
      }

      a.Interpolation = function (a, b, d) {
        return function (e) {
          return d(c(a, b, e));
        };
      };
    }(d), function (a, b, c) {
      a.sequenceNumber = 0;

      var d = function d(a, b, c) {
        this.target = a, this.currentTime = b, this.timelineTime = c, this.type = "finish", this.bubbles = !1, this.cancelable = !1, this.currentTarget = a, this.defaultPrevented = !1, this.eventPhase = Event.AT_TARGET, this.timeStamp = Date.now();
      };

      b.Animation = function (b) {
        this.id = "", b && b._id && (this.id = b._id), this._sequenceNumber = a.sequenceNumber++, this._currentTime = 0, this._startTime = null, this._paused = !1, this._playbackRate = 1, this._inTimeline = !0, this._finishedFlag = !0, this.onfinish = null, this._finishHandlers = [], this._effect = b, this._inEffect = this._effect._update(0), this._idle = !0, this._currentTimePending = !1;
      }, b.Animation.prototype = {
        _ensureAlive: function _ensureAlive() {
          this.playbackRate < 0 && 0 === this.currentTime ? this._inEffect = this._effect._update(-1) : this._inEffect = this._effect._update(this.currentTime), this._inTimeline || !this._inEffect && this._finishedFlag || (this._inTimeline = !0, b.timeline._animations.push(this));
        },
        _tickCurrentTime: function _tickCurrentTime(a, b) {
          a != this._currentTime && (this._currentTime = a, this._isFinished && !b && (this._currentTime = this._playbackRate > 0 ? this._totalDuration : 0), this._ensureAlive());
        },

        get currentTime() {
          return this._idle || this._currentTimePending ? null : this._currentTime;
        },

        set currentTime(a) {
          a = +a, isNaN(a) || (b.restart(), this._paused || null == this._startTime || (this._startTime = this._timeline.currentTime - a / this._playbackRate), this._currentTimePending = !1, this._currentTime != a && (this._idle && (this._idle = !1, this._paused = !0), this._tickCurrentTime(a, !0), b.applyDirtiedAnimation(this)));
        },

        get startTime() {
          return this._startTime;
        },

        set startTime(a) {
          a = +a, isNaN(a) || this._paused || this._idle || (this._startTime = a, this._tickCurrentTime((this._timeline.currentTime - this._startTime) * this.playbackRate), b.applyDirtiedAnimation(this));
        },

        get playbackRate() {
          return this._playbackRate;
        },

        set playbackRate(a) {
          if (a != this._playbackRate) {
            var c = this.currentTime;
            this._playbackRate = a, this._startTime = null, "paused" != this.playState && "idle" != this.playState && (this._finishedFlag = !1, this._idle = !1, this._ensureAlive(), b.applyDirtiedAnimation(this)), null != c && (this.currentTime = c);
          }
        },

        get _isFinished() {
          return !this._idle && (this._playbackRate > 0 && this._currentTime >= this._totalDuration || this._playbackRate < 0 && this._currentTime <= 0);
        },

        get _totalDuration() {
          return this._effect._totalDuration;
        },

        get playState() {
          return this._idle ? "idle" : null == this._startTime && !this._paused && 0 != this.playbackRate || this._currentTimePending ? "pending" : this._paused ? "paused" : this._isFinished ? "finished" : "running";
        },

        _rewind: function _rewind() {
          if (this._playbackRate >= 0) this._currentTime = 0;else {
            if (!(this._totalDuration < 1 / 0)) throw new DOMException("Unable to rewind negative playback rate animation with infinite duration", "InvalidStateError");
            this._currentTime = this._totalDuration;
          }
        },
        play: function play() {
          this._paused = !1, (this._isFinished || this._idle) && (this._rewind(), this._startTime = null), this._finishedFlag = !1, this._idle = !1, this._ensureAlive(), b.applyDirtiedAnimation(this);
        },
        pause: function pause() {
          this._isFinished || this._paused || this._idle ? this._idle && (this._rewind(), this._idle = !1) : this._currentTimePending = !0, this._startTime = null, this._paused = !0;
        },
        finish: function finish() {
          this._idle || (this.currentTime = this._playbackRate > 0 ? this._totalDuration : 0, this._startTime = this._totalDuration - this.currentTime, this._currentTimePending = !1, b.applyDirtiedAnimation(this));
        },
        cancel: function cancel() {
          this._inEffect && (this._inEffect = !1, this._idle = !0, this._paused = !1, this._isFinished = !0, this._finishedFlag = !0, this._currentTime = 0, this._startTime = null, this._effect._update(null), b.applyDirtiedAnimation(this));
        },
        reverse: function reverse() {
          this.playbackRate *= -1, this.play();
        },
        addEventListener: function addEventListener(a, b) {
          "function" == typeof b && "finish" == a && this._finishHandlers.push(b);
        },
        removeEventListener: function removeEventListener(a, b) {
          if ("finish" == a) {
            var c = this._finishHandlers.indexOf(b);

            c >= 0 && this._finishHandlers.splice(c, 1);
          }
        },
        _fireEvents: function _fireEvents(a) {
          if (this._isFinished) {
            if (!this._finishedFlag) {
              var b = new d(this, this._currentTime, a),
                  c = this._finishHandlers.concat(this.onfinish ? [this.onfinish] : []);

              setTimeout(function () {
                c.forEach(function (a) {
                  a.call(b.target, b);
                });
              }, 0), this._finishedFlag = !0;
            }
          } else this._finishedFlag = !1;
        },
        _tick: function _tick(a, b) {
          this._idle || this._paused || (null == this._startTime ? b && (this.startTime = a - this._currentTime / this.playbackRate) : this._isFinished || this._tickCurrentTime((a - this._startTime) * this.playbackRate)), b && (this._currentTimePending = !1, this._fireEvents(a));
        },

        get _needsTick() {
          return this.playState in {
            pending: 1,
            running: 1
          } || !this._finishedFlag;
        },

        _targetAnimations: function _targetAnimations() {
          var a = this._effect._target;
          return a._activeAnimations || (a._activeAnimations = []), a._activeAnimations;
        },
        _markTarget: function _markTarget() {
          var a = this._targetAnimations();

          -1 === a.indexOf(this) && a.push(this);
        },
        _unmarkTarget: function _unmarkTarget() {
          var a = this._targetAnimations(),
              b = a.indexOf(this);

          -1 !== b && a.splice(b, 1);
        }
      };
    }(c, d), function (a, b, c) {
      function d(a) {
        var b = j;
        j = [], a < q.currentTime && (a = q.currentTime), q._animations.sort(e), q._animations = h(a, !0, q._animations)[0], b.forEach(function (b) {
          b[1](a);
        }), g(), l = void 0;
      }

      function e(a, b) {
        return a._sequenceNumber - b._sequenceNumber;
      }

      function f() {
        this._animations = [], this.currentTime = window.performance && performance.now ? performance.now() : 0;
      }

      function g() {
        o.forEach(function (a) {
          a();
        }), o.length = 0;
      }

      function h(a, c, d) {
        p = !0, n = !1, b.timeline.currentTime = a, m = !1;
        var e = [],
            f = [],
            g = [],
            h = [];
        return d.forEach(function (b) {
          b._tick(a, c), b._inEffect ? (f.push(b._effect), b._markTarget()) : (e.push(b._effect), b._unmarkTarget()), b._needsTick && (m = !0);
          var d = b._inEffect || b._needsTick;
          b._inTimeline = d, d ? g.push(b) : h.push(b);
        }), o.push.apply(o, e), o.push.apply(o, f), m && requestAnimationFrame(function () {}), p = !1, [g, h];
      }

      var i = window.requestAnimationFrame,
          j = [],
          k = 0;
      window.requestAnimationFrame = function (a) {
        var b = k++;
        return 0 == j.length && i(d), j.push([b, a]), b;
      }, window.cancelAnimationFrame = function (a) {
        j.forEach(function (b) {
          b[0] == a && (b[1] = function () {});
        });
      }, f.prototype = {
        _play: function _play(c) {
          c._timing = a.normalizeTimingInput(c.timing);
          var d = new b.Animation(c);
          return d._idle = !1, d._timeline = this, this._animations.push(d), b.restart(), b.applyDirtiedAnimation(d), d;
        }
      };
      var l = void 0,
          m = !1,
          n = !1;
      b.restart = function () {
        return m || (m = !0, requestAnimationFrame(function () {}), n = !0), n;
      }, b.applyDirtiedAnimation = function (a) {
        if (!p) {
          a._markTarget();

          var c = a._targetAnimations();

          c.sort(e), h(b.timeline.currentTime, !1, c.slice())[1].forEach(function (a) {
            var b = q._animations.indexOf(a);

            -1 !== b && q._animations.splice(b, 1);
          }), g();
        }
      };
      var o = [],
          p = !1,
          q = new f();
      b.timeline = q;
    }(c, d), function (a) {
      function b(a, b) {
        var c = a.exec(b);
        if (c) return c = a.ignoreCase ? c[0].toLowerCase() : c[0], [c, b.substr(c.length)];
      }

      function c(a, b) {
        b = b.replace(/^\s*/, "");
        var c = a(b);
        if (c) return [c[0], c[1].replace(/^\s*/, "")];
      }

      function d(a, d, e) {
        a = c.bind(null, a);

        for (var f = [];;) {
          var g = a(e);
          if (!g) return [f, e];
          if (f.push(g[0]), e = g[1], !(g = b(d, e)) || "" == g[1]) return [f, e];
          e = g[1];
        }
      }

      function e(a, b) {
        for (var c = 0, d = 0; d < b.length && (!/\s|,/.test(b[d]) || 0 != c); d++) {
          if ("(" == b[d]) c++;else if (")" == b[d] && (c--, 0 == c && d++, c <= 0)) break;
        }

        var e = a(b.substr(0, d));
        return void 0 == e ? void 0 : [e, b.substr(d)];
      }

      function f(a, b) {
        for (var c = a, d = b; c && d;) {
          c > d ? c %= d : d %= c;
        }

        return c = a * b / (c + d);
      }

      function g(a) {
        return function (b) {
          var c = a(b);
          return c && (c[0] = void 0), c;
        };
      }

      function h(a, b) {
        return function (c) {
          return a(c) || [b, c];
        };
      }

      function i(b, c) {
        for (var d = [], e = 0; e < b.length; e++) {
          var f = a.consumeTrimmed(b[e], c);
          if (!f || "" == f[0]) return;
          void 0 !== f[0] && d.push(f[0]), c = f[1];
        }

        if ("" == c) return d;
      }

      function j(a, b, c, d, e) {
        for (var g = [], h = [], i = [], j = f(d.length, e.length), k = 0; k < j; k++) {
          var l = b(d[k % d.length], e[k % e.length]);
          if (!l) return;
          g.push(l[0]), h.push(l[1]), i.push(l[2]);
        }

        return [g, h, function (b) {
          var d = b.map(function (a, b) {
            return i[b](a);
          }).join(c);
          return a ? a(d) : d;
        }];
      }

      function k(a, b, c) {
        for (var d = [], e = [], f = [], g = 0, h = 0; h < c.length; h++) {
          if ("function" == typeof c[h]) {
            var i = c[h](a[g], b[g++]);
            d.push(i[0]), e.push(i[1]), f.push(i[2]);
          } else !function (a) {
            d.push(!1), e.push(!1), f.push(function () {
              return c[a];
            });
          }(h);
        }

        return [d, e, function (a) {
          for (var b = "", c = 0; c < a.length; c++) {
            b += f[c](a[c]);
          }

          return b;
        }];
      }

      a.consumeToken = b, a.consumeTrimmed = c, a.consumeRepeated = d, a.consumeParenthesised = e, a.ignore = g, a.optional = h, a.consumeList = i, a.mergeNestedRepeated = j.bind(null, null), a.mergeWrappedNestedRepeated = j, a.mergeList = k;
    }(d), function (a) {
      function b(b) {
        function c(b) {
          var c = a.consumeToken(/^inset/i, b);
          if (c) return d.inset = !0, c;
          var c = a.consumeLengthOrPercent(b);
          if (c) return d.lengths.push(c[0]), c;
          var c = a.consumeColor(b);
          return c ? (d.color = c[0], c) : void 0;
        }

        var d = {
          inset: !1,
          lengths: [],
          color: null
        },
            e = a.consumeRepeated(c, /^/, b);
        if (e && e[0].length) return [d, e[1]];
      }

      function c(c) {
        var d = a.consumeRepeated(b, /^,/, c);
        if (d && "" == d[1]) return d[0];
      }

      function d(b, c) {
        for (; b.lengths.length < Math.max(b.lengths.length, c.lengths.length);) {
          b.lengths.push({
            px: 0
          });
        }

        for (; c.lengths.length < Math.max(b.lengths.length, c.lengths.length);) {
          c.lengths.push({
            px: 0
          });
        }

        if (b.inset == c.inset && !!b.color == !!c.color) {
          for (var d, e = [], f = [[], 0], g = [[], 0], h = 0; h < b.lengths.length; h++) {
            var i = a.mergeDimensions(b.lengths[h], c.lengths[h], 2 == h);
            f[0].push(i[0]), g[0].push(i[1]), e.push(i[2]);
          }

          if (b.color && c.color) {
            var j = a.mergeColors(b.color, c.color);
            f[1] = j[0], g[1] = j[1], d = j[2];
          }

          return [f, g, function (a) {
            for (var c = b.inset ? "inset " : " ", f = 0; f < e.length; f++) {
              c += e[f](a[0][f]) + " ";
            }

            return d && (c += d(a[1])), c;
          }];
        }
      }

      function e(b, c, d, e) {
        function f(a) {
          return {
            inset: a,
            color: [0, 0, 0, 0],
            lengths: [{
              px: 0
            }, {
              px: 0
            }, {
              px: 0
            }, {
              px: 0
            }]
          };
        }

        for (var g = [], h = [], i = 0; i < d.length || i < e.length; i++) {
          var j = d[i] || f(e[i].inset),
              k = e[i] || f(d[i].inset);
          g.push(j), h.push(k);
        }

        return a.mergeNestedRepeated(b, c, g, h);
      }

      var f = e.bind(null, d, ", ");
      a.addPropertiesHandler(c, f, ["box-shadow", "text-shadow"]);
    }(d), function (a, b) {
      function c(a) {
        return a.toFixed(3).replace(/0+$/, "").replace(/\.$/, "");
      }

      function d(a, b, c) {
        return Math.min(b, Math.max(a, c));
      }

      function e(a) {
        if (/^\s*[-+]?(\d*\.)?\d+\s*$/.test(a)) return Number(a);
      }

      function f(a, b) {
        return [a, b, c];
      }

      function g(a, b) {
        if (0 != a) return i(0, 1 / 0)(a, b);
      }

      function h(a, b) {
        return [a, b, function (a) {
          return Math.round(d(1, 1 / 0, a));
        }];
      }

      function i(a, b) {
        return function (e, f) {
          return [e, f, function (e) {
            return c(d(a, b, e));
          }];
        };
      }

      function j(a) {
        var b = a.trim().split(/\s*[\s,]\s*/);

        if (0 !== b.length) {
          for (var c = [], d = 0; d < b.length; d++) {
            var f = e(b[d]);
            if (void 0 === f) return;
            c.push(f);
          }

          return c;
        }
      }

      function k(a, b) {
        if (a.length == b.length) return [a, b, function (a) {
          return a.map(c).join(" ");
        }];
      }

      function l(a, b) {
        return [a, b, Math.round];
      }

      a.clamp = d, a.addPropertiesHandler(j, k, ["stroke-dasharray"]), a.addPropertiesHandler(e, i(0, 1 / 0), ["border-image-width", "line-height"]), a.addPropertiesHandler(e, i(0, 1), ["opacity", "shape-image-threshold"]), a.addPropertiesHandler(e, g, ["flex-grow", "flex-shrink"]), a.addPropertiesHandler(e, h, ["orphans", "widows"]), a.addPropertiesHandler(e, l, ["z-index"]), a.parseNumber = e, a.parseNumberList = j, a.mergeNumbers = f, a.numberToString = c;
    }(d), function (a, b) {
      function c(a, b) {
        if ("visible" == a || "visible" == b) return [0, 1, function (c) {
          return c <= 0 ? a : c >= 1 ? b : "visible";
        }];
      }

      a.addPropertiesHandler(String, c, ["visibility"]);
    }(d), function (a, b) {
      function c(a) {
        a = a.trim(), f.fillStyle = "#000", f.fillStyle = a;
        var b = f.fillStyle;

        if (f.fillStyle = "#fff", f.fillStyle = a, b == f.fillStyle) {
          f.fillRect(0, 0, 1, 1);
          var c = f.getImageData(0, 0, 1, 1).data;
          f.clearRect(0, 0, 1, 1);
          var d = c[3] / 255;
          return [c[0] * d, c[1] * d, c[2] * d, d];
        }
      }

      function d(b, c) {
        return [b, c, function (b) {
          function c(a) {
            return Math.max(0, Math.min(255, a));
          }

          if (b[3]) for (var d = 0; d < 3; d++) {
            b[d] = Math.round(c(b[d] / b[3]));
          }
          return b[3] = a.numberToString(a.clamp(0, 1, b[3])), "rgba(" + b.join(",") + ")";
        }];
      }

      var e = document.createElementNS("http://www.w3.org/1999/xhtml", "canvas");
      e.width = e.height = 1;
      var f = e.getContext("2d");
      a.addPropertiesHandler(c, d, ["background-color", "border-bottom-color", "border-left-color", "border-right-color", "border-top-color", "color", "fill", "flood-color", "lighting-color", "outline-color", "stop-color", "stroke", "text-decoration-color"]), a.consumeColor = a.consumeParenthesised.bind(null, c), a.mergeColors = d;
    }(d), function (a, b) {
      function c(a) {
        function b() {
          var b = h.exec(a);
          g = b ? b[0] : void 0;
        }

        function c() {
          var a = Number(g);
          return b(), a;
        }

        function d() {
          if ("(" !== g) return c();
          b();
          var a = f();
          return ")" !== g ? NaN : (b(), a);
        }

        function e() {
          for (var a = d(); "*" === g || "/" === g;) {
            var c = g;
            b();
            var e = d();
            "*" === c ? a *= e : a /= e;
          }

          return a;
        }

        function f() {
          for (var a = e(); "+" === g || "-" === g;) {
            var c = g;
            b();
            var d = e();
            "+" === c ? a += d : a -= d;
          }

          return a;
        }

        var g,
            h = /([\+\-\w\.]+|[\(\)\*\/])/g;
        return b(), f();
      }

      function d(a, b) {
        if ("0" == (b = b.trim().toLowerCase()) && "px".search(a) >= 0) return {
          px: 0
        };

        if (/^[^(]*$|^calc/.test(b)) {
          b = b.replace(/calc\(/g, "(");
          var d = {};
          b = b.replace(a, function (a) {
            return d[a] = null, "U" + a;
          });

          for (var e = "U(" + a.source + ")", f = b.replace(/[-+]?(\d*\.)?\d+([Ee][-+]?\d+)?/g, "N").replace(new RegExp("N" + e, "g"), "D").replace(/\s[+-]\s/g, "O").replace(/\s/g, ""), g = [/N\*(D)/g, /(N|D)[*\/]N/g, /(N|D)O\1/g, /\((N|D)\)/g], h = 0; h < g.length;) {
            g[h].test(f) ? (f = f.replace(g[h], "$1"), h = 0) : h++;
          }

          if ("D" == f) {
            for (var i in d) {
              var j = c(b.replace(new RegExp("U" + i, "g"), "").replace(new RegExp(e, "g"), "*0"));
              if (!isFinite(j)) return;
              d[i] = j;
            }

            return d;
          }
        }
      }

      function e(a, b) {
        return f(a, b, !0);
      }

      function f(b, c, d) {
        var e,
            f = [];

        for (e in b) {
          f.push(e);
        }

        for (e in c) {
          f.indexOf(e) < 0 && f.push(e);
        }

        return b = f.map(function (a) {
          return b[a] || 0;
        }), c = f.map(function (a) {
          return c[a] || 0;
        }), [b, c, function (b) {
          var c = b.map(function (c, e) {
            return 1 == b.length && d && (c = Math.max(c, 0)), a.numberToString(c) + f[e];
          }).join(" + ");
          return b.length > 1 ? "calc(" + c + ")" : c;
        }];
      }

      var g = "px|em|ex|ch|rem|vw|vh|vmin|vmax|cm|mm|in|pt|pc",
          h = d.bind(null, new RegExp(g, "g")),
          i = d.bind(null, new RegExp(g + "|%", "g")),
          j = d.bind(null, /deg|rad|grad|turn/g);
      a.parseLength = h, a.parseLengthOrPercent = i, a.consumeLengthOrPercent = a.consumeParenthesised.bind(null, i), a.parseAngle = j, a.mergeDimensions = f;
      var k = a.consumeParenthesised.bind(null, h),
          l = a.consumeRepeated.bind(void 0, k, /^/),
          m = a.consumeRepeated.bind(void 0, l, /^,/);
      a.consumeSizePairList = m;

      var n = function n(a) {
        var b = m(a);
        if (b && "" == b[1]) return b[0];
      },
          o = a.mergeNestedRepeated.bind(void 0, e, " "),
          p = a.mergeNestedRepeated.bind(void 0, o, ",");

      a.mergeNonNegativeSizePair = o, a.addPropertiesHandler(n, p, ["background-size"]), a.addPropertiesHandler(i, e, ["border-bottom-width", "border-image-width", "border-left-width", "border-right-width", "border-top-width", "flex-basis", "font-size", "height", "line-height", "max-height", "max-width", "outline-width", "width"]), a.addPropertiesHandler(i, f, ["border-bottom-left-radius", "border-bottom-right-radius", "border-top-left-radius", "border-top-right-radius", "bottom", "left", "letter-spacing", "margin-bottom", "margin-left", "margin-right", "margin-top", "min-height", "min-width", "outline-offset", "padding-bottom", "padding-left", "padding-right", "padding-top", "perspective", "right", "shape-margin", "stroke-dashoffset", "text-indent", "top", "vertical-align", "word-spacing"]);
    }(d), function (a, b) {
      function c(b) {
        return a.consumeLengthOrPercent(b) || a.consumeToken(/^auto/, b);
      }

      function d(b) {
        var d = a.consumeList([a.ignore(a.consumeToken.bind(null, /^rect/)), a.ignore(a.consumeToken.bind(null, /^\(/)), a.consumeRepeated.bind(null, c, /^,/), a.ignore(a.consumeToken.bind(null, /^\)/))], b);
        if (d && 4 == d[0].length) return d[0];
      }

      function e(b, c) {
        return "auto" == b || "auto" == c ? [!0, !1, function (d) {
          var e = d ? b : c;
          if ("auto" == e) return "auto";
          var f = a.mergeDimensions(e, e);
          return f[2](f[0]);
        }] : a.mergeDimensions(b, c);
      }

      function f(a) {
        return "rect(" + a + ")";
      }

      var g = a.mergeWrappedNestedRepeated.bind(null, f, e, ", ");
      a.parseBox = d, a.mergeBoxes = g, a.addPropertiesHandler(d, g, ["clip"]);
    }(d), function (a, b) {
      function c(a) {
        return function (b) {
          var c = 0;
          return a.map(function (a) {
            return a === k ? b[c++] : a;
          });
        };
      }

      function d(a) {
        return a;
      }

      function e(b) {
        if ("none" == (b = b.toLowerCase().trim())) return [];

        for (var c, d = /\s*(\w+)\(([^)]*)\)/g, e = [], f = 0; c = d.exec(b);) {
          if (c.index != f) return;
          f = c.index + c[0].length;
          var g = c[1],
              h = n[g];
          if (!h) return;
          var i = c[2].split(","),
              j = h[0];
          if (j.length < i.length) return;

          for (var k = [], o = 0; o < j.length; o++) {
            var p,
                q = i[o],
                r = j[o];
            if (void 0 === (p = q ? {
              A: function A(b) {
                return "0" == b.trim() ? m : a.parseAngle(b);
              },
              N: a.parseNumber,
              T: a.parseLengthOrPercent,
              L: a.parseLength
            }[r.toUpperCase()](q) : {
              a: m,
              n: k[0],
              t: l
            }[r])) return;
            k.push(p);
          }

          if (e.push({
            t: g,
            d: k
          }), d.lastIndex == b.length) return e;
        }
      }

      function f(a) {
        return a.toFixed(6).replace(".000000", "");
      }

      function g(b, c) {
        if (b.decompositionPair !== c) {
          b.decompositionPair = c;
          var d = a.makeMatrixDecomposition(b);
        }

        if (c.decompositionPair !== b) {
          c.decompositionPair = b;
          var e = a.makeMatrixDecomposition(c);
        }

        return null == d[0] || null == e[0] ? [[!1], [!0], function (a) {
          return a ? c[0].d : b[0].d;
        }] : (d[0].push(0), e[0].push(1), [d, e, function (b) {
          var c = a.quat(d[0][3], e[0][3], b[5]);
          return a.composeMatrix(b[0], b[1], b[2], c, b[4]).map(f).join(",");
        }]);
      }

      function h(a) {
        return a.replace(/[xy]/, "");
      }

      function i(a) {
        return a.replace(/(x|y|z|3d)?$/, "3d");
      }

      function j(b, c) {
        var d = a.makeMatrixDecomposition && !0,
            e = !1;

        if (!b.length || !c.length) {
          b.length || (e = !0, b = c, c = []);

          for (var f = 0; f < b.length; f++) {
            var j = b[f].t,
                k = b[f].d,
                l = "scale" == j.substr(0, 5) ? 1 : 0;
            c.push({
              t: j,
              d: k.map(function (a) {
                if ("number" == typeof a) return l;
                var b = {};

                for (var c in a) {
                  b[c] = l;
                }

                return b;
              })
            });
          }
        }

        var m = function m(a, b) {
          return "perspective" == a && "perspective" == b || ("matrix" == a || "matrix3d" == a) && ("matrix" == b || "matrix3d" == b);
        },
            o = [],
            p = [],
            q = [];

        if (b.length != c.length) {
          if (!d) return;
          var r = g(b, c);
          o = [r[0]], p = [r[1]], q = [["matrix", [r[2]]]];
        } else for (var f = 0; f < b.length; f++) {
          var j,
              s = b[f].t,
              t = c[f].t,
              u = b[f].d,
              v = c[f].d,
              w = n[s],
              x = n[t];

          if (m(s, t)) {
            if (!d) return;
            var r = g([b[f]], [c[f]]);
            o.push(r[0]), p.push(r[1]), q.push(["matrix", [r[2]]]);
          } else {
            if (s == t) j = s;else if (w[2] && x[2] && h(s) == h(t)) j = h(s), u = w[2](u), v = x[2](v);else {
              if (!w[1] || !x[1] || i(s) != i(t)) {
                if (!d) return;
                var r = g(b, c);
                o = [r[0]], p = [r[1]], q = [["matrix", [r[2]]]];
                break;
              }

              j = i(s), u = w[1](u), v = x[1](v);
            }

            for (var y = [], z = [], A = [], B = 0; B < u.length; B++) {
              var C = "number" == typeof u[B] ? a.mergeNumbers : a.mergeDimensions,
                  r = C(u[B], v[B]);
              y[B] = r[0], z[B] = r[1], A.push(r[2]);
            }

            o.push(y), p.push(z), q.push([j, A]);
          }
        }

        if (e) {
          var D = o;
          o = p, p = D;
        }

        return [o, p, function (a) {
          return a.map(function (a, b) {
            var c = a.map(function (a, c) {
              return q[b][1][c](a);
            }).join(",");
            return "matrix" == q[b][0] && 16 == c.split(",").length && (q[b][0] = "matrix3d"), q[b][0] + "(" + c + ")";
          }).join(" ");
        }];
      }

      var k = null,
          l = {
        px: 0
      },
          m = {
        deg: 0
      },
          n = {
        matrix: ["NNNNNN", [k, k, 0, 0, k, k, 0, 0, 0, 0, 1, 0, k, k, 0, 1], d],
        matrix3d: ["NNNNNNNNNNNNNNNN", d],
        rotate: ["A"],
        rotatex: ["A"],
        rotatey: ["A"],
        rotatez: ["A"],
        rotate3d: ["NNNA"],
        perspective: ["L"],
        scale: ["Nn", c([k, k, 1]), d],
        scalex: ["N", c([k, 1, 1]), c([k, 1])],
        scaley: ["N", c([1, k, 1]), c([1, k])],
        scalez: ["N", c([1, 1, k])],
        scale3d: ["NNN", d],
        skew: ["Aa", null, d],
        skewx: ["A", null, c([k, m])],
        skewy: ["A", null, c([m, k])],
        translate: ["Tt", c([k, k, l]), d],
        translatex: ["T", c([k, l, l]), c([k, l])],
        translatey: ["T", c([l, k, l]), c([l, k])],
        translatez: ["L", c([l, l, k])],
        translate3d: ["TTL", d]
      };
      a.addPropertiesHandler(e, j, ["transform"]), a.transformToSvgMatrix = function (b) {
        var c = a.transformListToMatrix(e(b));
        return "matrix(" + f(c[0]) + " " + f(c[1]) + " " + f(c[4]) + " " + f(c[5]) + " " + f(c[12]) + " " + f(c[13]) + ")";
      };
    }(d), function (a, b) {
      function c(a, b) {
        b.concat([a]).forEach(function (b) {
          b in document.documentElement.style && (d[a] = b), e[b] = a;
        });
      }

      var d = {},
          e = {};
      c("transform", ["webkitTransform", "msTransform"]), c("transformOrigin", ["webkitTransformOrigin"]), c("perspective", ["webkitPerspective"]), c("perspectiveOrigin", ["webkitPerspectiveOrigin"]), a.propertyName = function (a) {
        return d[a] || a;
      }, a.unprefixedPropertyName = function (a) {
        return e[a] || a;
      };
    }(d);
  }(), function () {
    if (void 0 === document.createElement("div").animate([]).oncancel) {
      var a;
      if (window.performance && performance.now) var a = function a() {
        return performance.now();
      };else var a = function a() {
        return Date.now();
      };

      var b = function b(a, _b, c) {
        this.target = a, this.currentTime = _b, this.timelineTime = c, this.type = "cancel", this.bubbles = !1, this.cancelable = !1, this.currentTarget = a, this.defaultPrevented = !1, this.eventPhase = Event.AT_TARGET, this.timeStamp = Date.now();
      },
          c = window.Element.prototype.animate;

      window.Element.prototype.animate = function (d, e) {
        var f = c.call(this, d, e);
        f._cancelHandlers = [], f.oncancel = null;
        var g = f.cancel;

        f.cancel = function () {
          g.call(this);

          var c = new b(this, null, a()),
              d = this._cancelHandlers.concat(this.oncancel ? [this.oncancel] : []);

          setTimeout(function () {
            d.forEach(function (a) {
              a.call(c.target, c);
            });
          }, 0);
        };

        var h = f.addEventListener;

        f.addEventListener = function (a, b) {
          "function" == typeof b && "cancel" == a ? this._cancelHandlers.push(b) : h.call(this, a, b);
        };

        var i = f.removeEventListener;
        return f.removeEventListener = function (a, b) {
          if ("cancel" == a) {
            var c = this._cancelHandlers.indexOf(b);

            c >= 0 && this._cancelHandlers.splice(c, 1);
          } else i.call(this, a, b);
        }, f;
      };
    }
  }(), function (a) {
    var b = document.documentElement,
        c = null,
        d = !1;

    try {
      var e = getComputedStyle(b).getPropertyValue("opacity"),
          f = "0" == e ? "1" : "0";
      c = b.animate({
        opacity: [f, f]
      }, {
        duration: 1
      }), c.currentTime = 0, d = getComputedStyle(b).getPropertyValue("opacity") == f;
    } catch (a) {} finally {
      c && c.cancel();
    }

    if (!d) {
      var g = window.Element.prototype.animate;

      window.Element.prototype.animate = function (b, c) {
        return window.Symbol && Symbol.iterator && Array.prototype.from && b[Symbol.iterator] && (b = Array.from(b)), Array.isArray(b) || null === b || (b = a.convertToArrayForm(b)), g.call(this, b, c);
      };
    }
  }(c), function (a, b, c) {
    function d(a) {
      var c = b.timeline;
      c.currentTime = a, c._discardAnimations(), 0 == c._animations.length ? f = !1 : requestAnimationFrame(d);
    }

    var e = window.requestAnimationFrame;
    window.requestAnimationFrame = function (a) {
      return e(function (c) {
        b.timeline._updateAnimationsPromises(), a(c), b.timeline._updateAnimationsPromises();
      });
    }, b.AnimationTimeline = function () {
      this._animations = [], this.currentTime = void 0;
    }, b.AnimationTimeline.prototype = {
      getAnimations: function getAnimations() {
        return this._discardAnimations(), this._animations.slice();
      },
      _updateAnimationsPromises: function _updateAnimationsPromises() {
        b.animationsWithPromises = b.animationsWithPromises.filter(function (a) {
          return a._updatePromises();
        });
      },
      _discardAnimations: function _discardAnimations() {
        this._updateAnimationsPromises(), this._animations = this._animations.filter(function (a) {
          return "finished" != a.playState && "idle" != a.playState;
        });
      },
      _play: function _play(a) {
        var c = new b.Animation(a, this);
        return this._animations.push(c), b.restartWebAnimationsNextTick(), c._updatePromises(), c._animation.play(), c._updatePromises(), c;
      },
      play: function play(a) {
        return a && a.remove(), this._play(a);
      }
    };
    var f = !1;

    b.restartWebAnimationsNextTick = function () {
      f || (f = !0, requestAnimationFrame(d));
    };

    var g = new b.AnimationTimeline();
    b.timeline = g;

    try {
      Object.defineProperty(window.document, "timeline", {
        configurable: !0,
        get: function get() {
          return g;
        }
      });
    } catch (a) {}

    try {
      window.document.timeline = g;
    } catch (a) {}
  }(0, e), function (a, b, c) {
    b.animationsWithPromises = [], b.Animation = function (b, c) {
      if (this.id = "", b && b._id && (this.id = b._id), this.effect = b, b && (b._animation = this), !c) throw new Error("Animation with null timeline is not supported");
      this._timeline = c, this._sequenceNumber = a.sequenceNumber++, this._holdTime = 0, this._paused = !1, this._isGroup = !1, this._animation = null, this._childAnimations = [], this._callback = null, this._oldPlayState = "idle", this._rebuildUnderlyingAnimation(), this._animation.cancel(), this._updatePromises();
    }, b.Animation.prototype = {
      _updatePromises: function _updatePromises() {
        var a = this._oldPlayState,
            b = this.playState;
        return this._readyPromise && b !== a && ("idle" == b ? (this._rejectReadyPromise(), this._readyPromise = void 0) : "pending" == a ? this._resolveReadyPromise() : "pending" == b && (this._readyPromise = void 0)), this._finishedPromise && b !== a && ("idle" == b ? (this._rejectFinishedPromise(), this._finishedPromise = void 0) : "finished" == b ? this._resolveFinishedPromise() : "finished" == a && (this._finishedPromise = void 0)), this._oldPlayState = this.playState, this._readyPromise || this._finishedPromise;
      },
      _rebuildUnderlyingAnimation: function _rebuildUnderlyingAnimation() {
        this._updatePromises();

        var a,
            c,
            d,
            e,
            f = !!this._animation;
        f && (a = this.playbackRate, c = this._paused, d = this.startTime, e = this.currentTime, this._animation.cancel(), this._animation._wrapper = null, this._animation = null), (!this.effect || this.effect instanceof window.KeyframeEffect) && (this._animation = b.newUnderlyingAnimationForKeyframeEffect(this.effect), b.bindAnimationForKeyframeEffect(this)), (this.effect instanceof window.SequenceEffect || this.effect instanceof window.GroupEffect) && (this._animation = b.newUnderlyingAnimationForGroup(this.effect), b.bindAnimationForGroup(this)), this.effect && this.effect._onsample && b.bindAnimationForCustomEffect(this), f && (1 != a && (this.playbackRate = a), null !== d ? this.startTime = d : null !== e ? this.currentTime = e : null !== this._holdTime && (this.currentTime = this._holdTime), c && this.pause()), this._updatePromises();
      },
      _updateChildren: function _updateChildren() {
        if (this.effect && "idle" != this.playState) {
          var a = this.effect._timing.delay;

          this._childAnimations.forEach(function (c) {
            this._arrangeChildren(c, a), this.effect instanceof window.SequenceEffect && (a += b.groupChildDuration(c.effect));
          }.bind(this));
        }
      },
      _setExternalAnimation: function _setExternalAnimation(a) {
        if (this.effect && this._isGroup) for (var b = 0; b < this.effect.children.length; b++) {
          this.effect.children[b]._animation = a, this._childAnimations[b]._setExternalAnimation(a);
        }
      },
      _constructChildAnimations: function _constructChildAnimations() {
        if (this.effect && this._isGroup) {
          var a = this.effect._timing.delay;
          this._removeChildAnimations(), this.effect.children.forEach(function (c) {
            var d = b.timeline._play(c);

            this._childAnimations.push(d), d.playbackRate = this.playbackRate, this._paused && d.pause(), c._animation = this.effect._animation, this._arrangeChildren(d, a), this.effect instanceof window.SequenceEffect && (a += b.groupChildDuration(c));
          }.bind(this));
        }
      },
      _arrangeChildren: function _arrangeChildren(a, b) {
        null === this.startTime ? a.currentTime = this.currentTime - b / this.playbackRate : a.startTime !== this.startTime + b / this.playbackRate && (a.startTime = this.startTime + b / this.playbackRate);
      },

      get timeline() {
        return this._timeline;
      },

      get playState() {
        return this._animation ? this._animation.playState : "idle";
      },

      get finished() {
        return window.Promise ? (this._finishedPromise || (-1 == b.animationsWithPromises.indexOf(this) && b.animationsWithPromises.push(this), this._finishedPromise = new Promise(function (a, b) {
          this._resolveFinishedPromise = function () {
            a(this);
          }, this._rejectFinishedPromise = function () {
            b({
              type: DOMException.ABORT_ERR,
              name: "AbortError"
            });
          };
        }.bind(this)), "finished" == this.playState && this._resolveFinishedPromise()), this._finishedPromise) : (console.warn("Animation Promises require JavaScript Promise constructor"), null);
      },

      get ready() {
        return window.Promise ? (this._readyPromise || (-1 == b.animationsWithPromises.indexOf(this) && b.animationsWithPromises.push(this), this._readyPromise = new Promise(function (a, b) {
          this._resolveReadyPromise = function () {
            a(this);
          }, this._rejectReadyPromise = function () {
            b({
              type: DOMException.ABORT_ERR,
              name: "AbortError"
            });
          };
        }.bind(this)), "pending" !== this.playState && this._resolveReadyPromise()), this._readyPromise) : (console.warn("Animation Promises require JavaScript Promise constructor"), null);
      },

      get onfinish() {
        return this._animation.onfinish;
      },

      set onfinish(a) {
        this._animation.onfinish = "function" == typeof a ? function (b) {
          b.target = this, a.call(this, b);
        }.bind(this) : a;
      },

      get oncancel() {
        return this._animation.oncancel;
      },

      set oncancel(a) {
        this._animation.oncancel = "function" == typeof a ? function (b) {
          b.target = this, a.call(this, b);
        }.bind(this) : a;
      },

      get currentTime() {
        this._updatePromises();

        var a = this._animation.currentTime;
        return this._updatePromises(), a;
      },

      set currentTime(a) {
        this._updatePromises(), this._animation.currentTime = isFinite(a) ? a : Math.sign(a) * Number.MAX_VALUE, this._register(), this._forEachChild(function (b, c) {
          b.currentTime = a - c;
        }), this._updatePromises();
      },

      get startTime() {
        return this._animation.startTime;
      },

      set startTime(a) {
        this._updatePromises(), this._animation.startTime = isFinite(a) ? a : Math.sign(a) * Number.MAX_VALUE, this._register(), this._forEachChild(function (b, c) {
          b.startTime = a + c;
        }), this._updatePromises();
      },

      get playbackRate() {
        return this._animation.playbackRate;
      },

      set playbackRate(a) {
        this._updatePromises();

        var b = this.currentTime;
        this._animation.playbackRate = a, this._forEachChild(function (b) {
          b.playbackRate = a;
        }), null !== b && (this.currentTime = b), this._updatePromises();
      },

      play: function play() {
        this._updatePromises(), this._paused = !1, this._animation.play(), -1 == this._timeline._animations.indexOf(this) && this._timeline._animations.push(this), this._register(), b.awaitStartTime(this), this._forEachChild(function (a) {
          var b = a.currentTime;
          a.play(), a.currentTime = b;
        }), this._updatePromises();
      },
      pause: function pause() {
        this._updatePromises(), this.currentTime && (this._holdTime = this.currentTime), this._animation.pause(), this._register(), this._forEachChild(function (a) {
          a.pause();
        }), this._paused = !0, this._updatePromises();
      },
      finish: function finish() {
        this._updatePromises(), this._animation.finish(), this._register(), this._updatePromises();
      },
      cancel: function cancel() {
        this._updatePromises(), this._animation.cancel(), this._register(), this._removeChildAnimations(), this._updatePromises();
      },
      reverse: function reverse() {
        this._updatePromises();

        var a = this.currentTime;
        this._animation.reverse(), this._forEachChild(function (a) {
          a.reverse();
        }), null !== a && (this.currentTime = a), this._updatePromises();
      },
      addEventListener: function addEventListener(a, b) {
        var c = b;
        "function" == typeof b && (c = function (a) {
          a.target = this, b.call(this, a);
        }.bind(this), b._wrapper = c), this._animation.addEventListener(a, c);
      },
      removeEventListener: function removeEventListener(a, b) {
        this._animation.removeEventListener(a, b && b._wrapper || b);
      },
      _removeChildAnimations: function _removeChildAnimations() {
        for (; this._childAnimations.length;) {
          this._childAnimations.pop().cancel();
        }
      },
      _forEachChild: function _forEachChild(b) {
        var c = 0;

        if (this.effect.children && this._childAnimations.length < this.effect.children.length && this._constructChildAnimations(), this._childAnimations.forEach(function (a) {
          b.call(this, a, c), this.effect instanceof window.SequenceEffect && (c += a.effect.activeDuration);
        }.bind(this)), "pending" != this.playState) {
          var d = this.effect._timing,
              e = this.currentTime;
          null !== e && (e = a.calculateIterationProgress(a.calculateActiveDuration(d), e, d)), (null == e || isNaN(e)) && this._removeChildAnimations();
        }
      }
    }, window.Animation = b.Animation;
  }(c, e), function (a, b, c) {
    function d(b) {
      this._frames = a.normalizeKeyframes(b);
    }

    function e() {
      for (var a = !1; i.length;) {
        i.shift()._updateChildren(), a = !0;
      }

      return a;
    }

    var f = function f(a) {
      if (a._animation = void 0, a instanceof window.SequenceEffect || a instanceof window.GroupEffect) for (var b = 0; b < a.children.length; b++) {
        f(a.children[b]);
      }
    };

    b.removeMulti = function (a) {
      for (var b = [], c = 0; c < a.length; c++) {
        var d = a[c];
        d._parent ? (-1 == b.indexOf(d._parent) && b.push(d._parent), d._parent.children.splice(d._parent.children.indexOf(d), 1), d._parent = null, f(d)) : d._animation && d._animation.effect == d && (d._animation.cancel(), d._animation.effect = new KeyframeEffect(null, []), d._animation._callback && (d._animation._callback._animation = null), d._animation._rebuildUnderlyingAnimation(), f(d));
      }

      for (c = 0; c < b.length; c++) {
        b[c]._rebuild();
      }
    }, b.KeyframeEffect = function (b, c, e, f) {
      return this.target = b, this._parent = null, e = a.numericTimingToObject(e), this._timingInput = a.cloneTimingInput(e), this._timing = a.normalizeTimingInput(e), this.timing = a.makeTiming(e, !1, this), this.timing._effect = this, "function" == typeof c ? (a.deprecated("Custom KeyframeEffect", "2015-06-22", "Use KeyframeEffect.onsample instead."), this._normalizedKeyframes = c) : this._normalizedKeyframes = new d(c), this._keyframes = c, this.activeDuration = a.calculateActiveDuration(this._timing), this._id = f, this;
    }, b.KeyframeEffect.prototype = {
      getFrames: function getFrames() {
        return "function" == typeof this._normalizedKeyframes ? this._normalizedKeyframes : this._normalizedKeyframes._frames;
      },

      set onsample(a) {
        if ("function" == typeof this.getFrames()) throw new Error("Setting onsample on custom effect KeyframeEffect is not supported.");
        this._onsample = a, this._animation && this._animation._rebuildUnderlyingAnimation();
      },

      get parent() {
        return this._parent;
      },

      clone: function clone() {
        if ("function" == typeof this.getFrames()) throw new Error("Cloning custom effects is not supported.");
        var b = new KeyframeEffect(this.target, [], a.cloneTimingInput(this._timingInput), this._id);
        return b._normalizedKeyframes = this._normalizedKeyframes, b._keyframes = this._keyframes, b;
      },
      remove: function remove() {
        b.removeMulti([this]);
      }
    };
    var g = Element.prototype.animate;

    Element.prototype.animate = function (a, c) {
      var d = "";
      return c && c.id && (d = c.id), b.timeline._play(new b.KeyframeEffect(this, a, c, d));
    };

    var h = document.createElementNS("http://www.w3.org/1999/xhtml", "div");
    b.newUnderlyingAnimationForKeyframeEffect = function (a) {
      if (a) {
        var b = a.target || h,
            c = a._keyframes;
        "function" == typeof c && (c = []);
        var d = a._timingInput;
        d.id = a._id;
      } else var b = h,
          c = [],
          d = 0;

      return g.apply(b, [c, d]);
    }, b.bindAnimationForKeyframeEffect = function (a) {
      a.effect && "function" == typeof a.effect._normalizedKeyframes && b.bindAnimationForCustomEffect(a);
    };
    var i = [];

    b.awaitStartTime = function (a) {
      null === a.startTime && a._isGroup && (0 == i.length && requestAnimationFrame(e), i.push(a));
    };

    var j = window.getComputedStyle;
    Object.defineProperty(window, "getComputedStyle", {
      configurable: !0,
      enumerable: !0,
      value: function value() {
        b.timeline._updateAnimationsPromises();

        var a = j.apply(this, arguments);
        return e() && (a = j.apply(this, arguments)), b.timeline._updateAnimationsPromises(), a;
      }
    }), window.KeyframeEffect = b.KeyframeEffect, window.Element.prototype.getAnimations = function () {
      return document.timeline.getAnimations().filter(function (a) {
        return null !== a.effect && a.effect.target == this;
      }.bind(this));
    };
  }(c, e), function (a, b, c) {
    function d(a) {
      a._registered || (a._registered = !0, g.push(a), h || (h = !0, requestAnimationFrame(e)));
    }

    function e(a) {
      var b = g;
      g = [], b.sort(function (a, b) {
        return a._sequenceNumber - b._sequenceNumber;
      }), b = b.filter(function (a) {
        a();
        var b = a._animation ? a._animation.playState : "idle";
        return "running" != b && "pending" != b && (a._registered = !1), a._registered;
      }), g.push.apply(g, b), g.length ? (h = !0, requestAnimationFrame(e)) : h = !1;
    }

    var f = (document.createElementNS("http://www.w3.org/1999/xhtml", "div"), 0);

    b.bindAnimationForCustomEffect = function (b) {
      var c,
          e = b.effect.target,
          g = "function" == typeof b.effect.getFrames();
      c = g ? b.effect.getFrames() : b.effect._onsample;
      var h = b.effect.timing,
          i = null;
      h = a.normalizeTimingInput(h);

      var j = function j() {
        var d = j._animation ? j._animation.currentTime : null;
        null !== d && (d = a.calculateIterationProgress(a.calculateActiveDuration(h), d, h), isNaN(d) && (d = null)), d !== i && (g ? c(d, e, b.effect) : c(d, b.effect, b.effect._animation)), i = d;
      };

      j._animation = b, j._registered = !1, j._sequenceNumber = f++, b._callback = j, d(j);
    };

    var g = [],
        h = !1;

    b.Animation.prototype._register = function () {
      this._callback && d(this._callback);
    };
  }(c, e), function (a, b, c) {
    function d(a) {
      return a._timing.delay + a.activeDuration + a._timing.endDelay;
    }

    function e(b, c, d) {
      this._id = d, this._parent = null, this.children = b || [], this._reparent(this.children), c = a.numericTimingToObject(c), this._timingInput = a.cloneTimingInput(c), this._timing = a.normalizeTimingInput(c, !0), this.timing = a.makeTiming(c, !0, this), this.timing._effect = this, "auto" === this._timing.duration && (this._timing.duration = this.activeDuration);
    }

    window.SequenceEffect = function () {
      e.apply(this, arguments);
    }, window.GroupEffect = function () {
      e.apply(this, arguments);
    }, e.prototype = {
      _isAncestor: function _isAncestor(a) {
        for (var b = this; null !== b;) {
          if (b == a) return !0;
          b = b._parent;
        }

        return !1;
      },
      _rebuild: function _rebuild() {
        for (var a = this; a;) {
          "auto" === a.timing.duration && (a._timing.duration = a.activeDuration), a = a._parent;
        }

        this._animation && this._animation._rebuildUnderlyingAnimation();
      },
      _reparent: function _reparent(a) {
        b.removeMulti(a);

        for (var c = 0; c < a.length; c++) {
          a[c]._parent = this;
        }
      },
      _putChild: function _putChild(a, b) {
        for (var c = b ? "Cannot append an ancestor or self" : "Cannot prepend an ancestor or self", d = 0; d < a.length; d++) {
          if (this._isAncestor(a[d])) throw {
            type: DOMException.HIERARCHY_REQUEST_ERR,
            name: "HierarchyRequestError",
            message: c
          };
        }

        for (var d = 0; d < a.length; d++) {
          b ? this.children.push(a[d]) : this.children.unshift(a[d]);
        }

        this._reparent(a), this._rebuild();
      },
      append: function append() {
        this._putChild(arguments, !0);
      },
      prepend: function prepend() {
        this._putChild(arguments, !1);
      },

      get parent() {
        return this._parent;
      },

      get firstChild() {
        return this.children.length ? this.children[0] : null;
      },

      get lastChild() {
        return this.children.length ? this.children[this.children.length - 1] : null;
      },

      clone: function clone() {
        for (var b = a.cloneTimingInput(this._timingInput), c = [], d = 0; d < this.children.length; d++) {
          c.push(this.children[d].clone());
        }

        return this instanceof GroupEffect ? new GroupEffect(c, b) : new SequenceEffect(c, b);
      },
      remove: function remove() {
        b.removeMulti([this]);
      }
    }, window.SequenceEffect.prototype = Object.create(e.prototype), Object.defineProperty(window.SequenceEffect.prototype, "activeDuration", {
      get: function get() {
        var a = 0;
        return this.children.forEach(function (b) {
          a += d(b);
        }), Math.max(a, 0);
      }
    }), window.GroupEffect.prototype = Object.create(e.prototype), Object.defineProperty(window.GroupEffect.prototype, "activeDuration", {
      get: function get() {
        var a = 0;
        return this.children.forEach(function (b) {
          a = Math.max(a, d(b));
        }), a;
      }
    }), b.newUnderlyingAnimationForGroup = function (c) {
      var d,
          e = null,
          f = function f(b) {
        var c = d._wrapper;
        if (c && "pending" != c.playState && c.effect) return null == b ? void c._removeChildAnimations() : 0 == b && c.playbackRate < 0 && (e || (e = a.normalizeTimingInput(c.effect.timing)), b = a.calculateIterationProgress(a.calculateActiveDuration(e), -1, e), isNaN(b) || null == b) ? (c._forEachChild(function (a) {
          a.currentTime = -1;
        }), void c._removeChildAnimations()) : void 0;
      },
          g = new KeyframeEffect(null, [], c._timing, c._id);

      return g.onsample = f, d = b.timeline._play(g);
    }, b.bindAnimationForGroup = function (a) {
      a._animation._wrapper = a, a._isGroup = !0, b.awaitStartTime(a), a._constructChildAnimations(), a._setExternalAnimation(a);
    }, b.groupChildDuration = d;
  }(c, e), b["true"] = a;
}({}, function () {
  return this;
}());

/***/ }),
/* 151 */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony import */ var _polymer_polymer_polymer_legacy_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(4);
/* harmony import */ var _polymer_iron_flex_layout_iron_flex_layout_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(16);
/* harmony import */ var _polymer_iron_behaviors_iron_control_state_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(30);
/* harmony import */ var _polymer_iron_validatable_behavior_iron_validatable_behavior_js__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(69);
/* harmony import */ var _polymer_polymer_lib_legacy_polymer_fn_js__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(8);
/* harmony import */ var _polymer_polymer_lib_legacy_polymer_dom_js__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(9);
/* harmony import */ var _polymer_polymer_lib_utils_html_tag_js__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(7);
function _templateObject() {
  var data = _taggedTemplateLiteral(["\n    <style>\n      :host {\n        display: inline-block;\n        position: relative;\n        width: 400px;\n        border: 1px solid;\n        padding: 2px;\n        -moz-appearance: textarea;\n        -webkit-appearance: textarea;\n        overflow: hidden;\n      }\n\n      .mirror-text {\n        visibility: hidden;\n        word-wrap: break-word;\n        @apply --iron-autogrow-textarea;\n      }\n\n      .fit {\n        @apply --layout-fit;\n      }\n\n      textarea {\n        position: relative;\n        outline: none;\n        border: none;\n        resize: none;\n        background: inherit;\n        color: inherit;\n        /* see comments in template */\n        width: 100%;\n        height: 100%;\n        font-size: inherit;\n        font-family: inherit;\n        line-height: inherit;\n        text-align: inherit;\n        @apply --iron-autogrow-textarea;\n      }\n\n      textarea::-webkit-input-placeholder {\n        @apply --iron-autogrow-textarea-placeholder;\n      }\n\n      textarea:-moz-placeholder {\n        @apply --iron-autogrow-textarea-placeholder;\n      }\n\n      textarea::-moz-placeholder {\n        @apply --iron-autogrow-textarea-placeholder;\n      }\n\n      textarea:-ms-input-placeholder {\n        @apply --iron-autogrow-textarea-placeholder;\n      }\n    </style>\n\n    <!-- the mirror sizes the input/textarea so it grows with typing -->\n    <!-- use &#160; instead &nbsp; of to allow this element to be used in XHTML -->\n    <div id=\"mirror\" class=\"mirror-text\" aria-hidden=\"true\">&nbsp;</div>\n\n    <!-- size the input/textarea with a div, because the textarea has intrinsic size in ff -->\n    <div class=\"textarea-container fit\">\n      <textarea id=\"textarea\" name$=\"[[name]]\" aria-label$=\"[[label]]\" autocomplete$=\"[[autocomplete]]\" autofocus$=\"[[autofocus]]\" inputmode$=\"[[inputmode]]\" placeholder$=\"[[placeholder]]\" readonly$=\"[[readonly]]\" required$=\"[[required]]\" disabled$=\"[[disabled]]\" rows$=\"[[rows]]\" minlength$=\"[[minlength]]\" maxlength$=\"[[maxlength]]\"></textarea>\n    </div>\n"], ["\n    <style>\n      :host {\n        display: inline-block;\n        position: relative;\n        width: 400px;\n        border: 1px solid;\n        padding: 2px;\n        -moz-appearance: textarea;\n        -webkit-appearance: textarea;\n        overflow: hidden;\n      }\n\n      .mirror-text {\n        visibility: hidden;\n        word-wrap: break-word;\n        @apply --iron-autogrow-textarea;\n      }\n\n      .fit {\n        @apply --layout-fit;\n      }\n\n      textarea {\n        position: relative;\n        outline: none;\n        border: none;\n        resize: none;\n        background: inherit;\n        color: inherit;\n        /* see comments in template */\n        width: 100%;\n        height: 100%;\n        font-size: inherit;\n        font-family: inherit;\n        line-height: inherit;\n        text-align: inherit;\n        @apply --iron-autogrow-textarea;\n      }\n\n      textarea::-webkit-input-placeholder {\n        @apply --iron-autogrow-textarea-placeholder;\n      }\n\n      textarea:-moz-placeholder {\n        @apply --iron-autogrow-textarea-placeholder;\n      }\n\n      textarea::-moz-placeholder {\n        @apply --iron-autogrow-textarea-placeholder;\n      }\n\n      textarea:-ms-input-placeholder {\n        @apply --iron-autogrow-textarea-placeholder;\n      }\n    </style>\n\n    <!-- the mirror sizes the input/textarea so it grows with typing -->\n    <!-- use &#160; instead &nbsp; of to allow this element to be used in XHTML -->\n    <div id=\"mirror\" class=\"mirror-text\" aria-hidden=\"true\">&nbsp;</div>\n\n    <!-- size the input/textarea with a div, because the textarea has intrinsic size in ff -->\n    <div class=\"textarea-container fit\">\n      <textarea id=\"textarea\" name\\$=\"[[name]]\" aria-label\\$=\"[[label]]\" autocomplete\\$=\"[[autocomplete]]\" autofocus\\$=\"[[autofocus]]\" inputmode\\$=\"[[inputmode]]\" placeholder\\$=\"[[placeholder]]\" readonly\\$=\"[[readonly]]\" required\\$=\"[[required]]\" disabled\\$=\"[[disabled]]\" rows\\$=\"[[rows]]\" minlength\\$=\"[[minlength]]\" maxlength\\$=\"[[maxlength]]\"></textarea>\n    </div>\n"]);

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
`iron-autogrow-textarea` is an element containing a textarea that grows in
height as more lines of input are entered. Unless an explicit height or the
`maxRows` property is set, it will never scroll.

Example:

    <iron-autogrow-textarea></iron-autogrow-textarea>

### Styling

The following custom properties and mixins are available for styling:

Custom property | Description | Default
----------------|-------------|----------
`--iron-autogrow-textarea` | Mixin applied to the textarea | `{}`
`--iron-autogrow-textarea-placeholder` | Mixin applied to the textarea placeholder | `{}`

@group Iron Elements
@hero hero.svg
@demo demo/index.html
*/

Object(_polymer_polymer_lib_legacy_polymer_fn_js__WEBPACK_IMPORTED_MODULE_4__[/* Polymer */ "a"])({
  _template: Object(_polymer_polymer_lib_utils_html_tag_js__WEBPACK_IMPORTED_MODULE_6__[/* html */ "a"])(_templateObject()),
  is: 'iron-autogrow-textarea',
  behaviors: [_polymer_iron_validatable_behavior_iron_validatable_behavior_js__WEBPACK_IMPORTED_MODULE_3__[/* IronValidatableBehavior */ "a"], _polymer_iron_behaviors_iron_control_state_js__WEBPACK_IMPORTED_MODULE_2__[/* IronControlState */ "a"]],
  properties: {
    /**
     * Use this property instead of `bind-value` for two-way data binding.
     * @type {string|number}
     */
    value: {
      observer: '_valueChanged',
      type: String,
      notify: true
    },

    /**
     * This property is deprecated, and just mirrors `value`. Use `value`
     * instead.
     * @type {string|number}
     */
    bindValue: {
      observer: '_bindValueChanged',
      type: String,
      notify: true
    },

    /**
     * The initial number of rows.
     *
     * @attribute rows
     * @type number
     * @default 1
     */
    rows: {
      type: Number,
      value: 1,
      observer: '_updateCached'
    },

    /**
     * The maximum number of rows this element can grow to until it
     * scrolls. 0 means no maximum.
     *
     * @attribute maxRows
     * @type number
     * @default 0
     */
    maxRows: {
      type: Number,
      value: 0,
      observer: '_updateCached'
    },

    /**
     * Bound to the textarea's `autocomplete` attribute.
     */
    autocomplete: {
      type: String,
      value: 'off'
    },

    /**
     * Bound to the textarea's `autofocus` attribute.
     */
    autofocus: {
      type: Boolean,
      value: false
    },

    /**
     * Bound to the textarea's `inputmode` attribute.
     */
    inputmode: {
      type: String
    },

    /**
     * Bound to the textarea's `placeholder` attribute.
     */
    placeholder: {
      type: String
    },

    /**
     * Bound to the textarea's `readonly` attribute.
     */
    readonly: {
      type: String
    },

    /**
     * Set to true to mark the textarea as required.
     */
    required: {
      type: Boolean
    },

    /**
     * The minimum length of the input value.
     */
    minlength: {
      type: Number
    },

    /**
     * The maximum length of the input value.
     */
    maxlength: {
      type: Number
    },

    /**
     * Bound to the textarea's `aria-label` attribute.
     */
    label: {
      type: String
    }
  },
  listeners: {
    'input': '_onInput'
  },

  /**
   * Returns the underlying textarea.
   * @return {!HTMLTextAreaElement}
   */
  get textarea() {
    return this.$.textarea;
  },

  /**
   * Returns textarea's selection start.
   * @return {number}
   */
  get selectionStart() {
    return this.$.textarea.selectionStart;
  },

  /**
   * Returns textarea's selection end.
   * @return {number}
   */
  get selectionEnd() {
    return this.$.textarea.selectionEnd;
  },

  /**
   * Sets the textarea's selection start.
   */
  set selectionStart(value) {
    this.$.textarea.selectionStart = value;
  },

  /**
   * Sets the textarea's selection end.
   */
  set selectionEnd(value) {
    this.$.textarea.selectionEnd = value;
  },

  attached: function attached() {
    /* iOS has an arbitrary left margin of 3px that isn't present
     * in any other browser, and means that the paper-textarea's cursor
     * overlaps the label.
     * See https://github.com/PolymerElements/paper-input/issues/468.
     */
    var IS_IOS = navigator.userAgent.match(/iP(?:[oa]d|hone)/);

    if (IS_IOS) {
      this.$.textarea.style.marginLeft = '-3px';
    }
  },

  /**
   * Returns true if `value` is valid. The validator provided in `validator`
   * will be used first, if it exists; otherwise, the `textarea`'s validity
   * is used.
   * @return {boolean} True if the value is valid.
   */
  validate: function validate() {
    // Use the nested input's native validity.
    var valid = this.$.textarea.validity.valid; // Only do extra checking if the browser thought this was valid.

    if (valid) {
      // Empty, required input is invalid
      if (this.required && this.value === '') {
        valid = false;
      } else if (this.hasValidator()) {
        valid = _polymer_iron_validatable_behavior_iron_validatable_behavior_js__WEBPACK_IMPORTED_MODULE_3__[/* IronValidatableBehavior */ "a"].validate.call(this, this.value);
      }
    }

    this.invalid = !valid;
    this.fire('iron-input-validate');
    return valid;
  },
  _bindValueChanged: function _bindValueChanged(bindValue) {
    this.value = bindValue;
  },
  _valueChanged: function _valueChanged(value) {
    var textarea = this.textarea;

    if (!textarea) {
      return;
    } // If the bindValue changed manually, then we need to also update
    // the underlying textarea's value. Otherwise this change was probably
    // generated from the _onInput handler, and the two values are already
    // the same.


    if (textarea.value !== value) {
      textarea.value = !(value || value === 0) ? '' : value;
    }

    this.bindValue = value;
    this.$.mirror.innerHTML = this._valueForMirror(); // Manually notify because we don't want to notify until after setting
    // value.

    this.fire('bind-value-changed', {
      value: this.bindValue
    });
  },
  _onInput: function _onInput(event) {
    var eventPath = Object(_polymer_polymer_lib_legacy_polymer_dom_js__WEBPACK_IMPORTED_MODULE_5__[/* dom */ "a"])(event).path;
    this.value = eventPath ? eventPath[0].value : event.target.value;
  },
  _constrain: function _constrain(tokens) {
    var _tokens;

    tokens = tokens || ['']; // Enforce the min and max heights for a multiline input to avoid
    // measurement

    if (this.maxRows > 0 && tokens.length > this.maxRows) {
      _tokens = tokens.slice(0, this.maxRows);
    } else {
      _tokens = tokens.slice(0);
    }

    while (this.rows > 0 && _tokens.length < this.rows) {
      _tokens.push('');
    } // Use &#160; instead &nbsp; of to allow this element to be used in XHTML.


    return _tokens.join('<br/>') + '&#160;';
  },
  _valueForMirror: function _valueForMirror() {
    var input = this.textarea;

    if (!input) {
      return;
    }

    this.tokens = input && input.value ? input.value.replace(/&/gm, '&amp;').replace(/"/gm, '&quot;').replace(/'/gm, '&#39;').replace(/</gm, '&lt;').replace(/>/gm, '&gt;').split('\n') : [''];
    return this._constrain(this.tokens);
  },
  _updateCached: function _updateCached() {
    this.$.mirror.innerHTML = this._constrain(this.tokens);
  }
});

/***/ }),
/* 152 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


var yaml = __webpack_require__(153);

module.exports = yaml;

/***/ }),
/* 153 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


var loader = __webpack_require__(154);

var dumper = __webpack_require__(177);

function deprecated(name) {
  return function () {
    throw new Error('Function ' + name + ' is deprecated and cannot be used.');
  };
}

module.exports.Type = __webpack_require__(15);
module.exports.Schema = __webpack_require__(42);
module.exports.FAILSAFE_SCHEMA = __webpack_require__(93);
module.exports.JSON_SCHEMA = __webpack_require__(132);
module.exports.CORE_SCHEMA = __webpack_require__(131);
module.exports.DEFAULT_SAFE_SCHEMA = __webpack_require__(52);
module.exports.DEFAULT_FULL_SCHEMA = __webpack_require__(73);
module.exports.load = loader.load;
module.exports.loadAll = loader.loadAll;
module.exports.safeLoad = loader.safeLoad;
module.exports.safeLoadAll = loader.safeLoadAll;
module.exports.dump = dumper.dump;
module.exports.safeDump = dumper.safeDump;
module.exports.YAMLException = __webpack_require__(51); // Deprecated schema names from JS-YAML 2.0.x

module.exports.MINIMAL_SCHEMA = __webpack_require__(93);
module.exports.SAFE_SCHEMA = __webpack_require__(52);
module.exports.DEFAULT_SCHEMA = __webpack_require__(73); // Deprecated functions from JS-YAML 1.x.x

module.exports.scan = deprecated('scan');
module.exports.parse = deprecated('parse');
module.exports.compose = deprecated('compose');
module.exports.addConstructor = deprecated('addConstructor');

/***/ }),
/* 154 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

/*eslint-disable max-len,no-use-before-define*/

function _typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { _typeof = function _typeof(obj) { return typeof obj; }; } else { _typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return _typeof(obj); }

var common = __webpack_require__(41);

var YAMLException = __webpack_require__(51);

var Mark = __webpack_require__(155);

var DEFAULT_SAFE_SCHEMA = __webpack_require__(52);

var DEFAULT_FULL_SCHEMA = __webpack_require__(73);

var _hasOwnProperty = Object.prototype.hasOwnProperty;
var CONTEXT_FLOW_IN = 1;
var CONTEXT_FLOW_OUT = 2;
var CONTEXT_BLOCK_IN = 3;
var CONTEXT_BLOCK_OUT = 4;
var CHOMPING_CLIP = 1;
var CHOMPING_STRIP = 2;
var CHOMPING_KEEP = 3;
var PATTERN_NON_PRINTABLE = /[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x84\x86-\x9F\uFFFE\uFFFF]|[\uD800-\uDBFF](?![\uDC00-\uDFFF])|(?:[^\uD800-\uDBFF]|^)[\uDC00-\uDFFF]/;
var PATTERN_NON_ASCII_LINE_BREAKS = /[\x85\u2028\u2029]/;
var PATTERN_FLOW_INDICATORS = /[,\[\]\{\}]/;
var PATTERN_TAG_HANDLE = /^(?:!|!!|![a-z\-]+!)$/i;
var PATTERN_TAG_URI = /^(?:!|[^,\[\]\{\}])(?:%[0-9a-f]{2}|[0-9a-z\-#;\/\?:@&=\+\$,_\.!~\*'\(\)\[\]])*$/i;

function _class(obj) {
  return Object.prototype.toString.call(obj);
}

function is_EOL(c) {
  return c === 0x0A
  /* LF */
  || c === 0x0D
  /* CR */
  ;
}

function is_WHITE_SPACE(c) {
  return c === 0x09
  /* Tab */
  || c === 0x20
  /* Space */
  ;
}

function is_WS_OR_EOL(c) {
  return c === 0x09
  /* Tab */
  || c === 0x20
  /* Space */
  || c === 0x0A
  /* LF */
  || c === 0x0D
  /* CR */
  ;
}

function is_FLOW_INDICATOR(c) {
  return c === 0x2C
  /* , */
  || c === 0x5B
  /* [ */
  || c === 0x5D
  /* ] */
  || c === 0x7B
  /* { */
  || c === 0x7D
  /* } */
  ;
}

function fromHexCode(c) {
  var lc;

  if (0x30
  /* 0 */
  <= c && c <= 0x39
  /* 9 */
  ) {
    return c - 0x30;
  }
  /*eslint-disable no-bitwise*/


  lc = c | 0x20;

  if (0x61
  /* a */
  <= lc && lc <= 0x66
  /* f */
  ) {
    return lc - 0x61 + 10;
  }

  return -1;
}

function escapedHexLen(c) {
  if (c === 0x78
  /* x */
  ) {
      return 2;
    }

  if (c === 0x75
  /* u */
  ) {
      return 4;
    }

  if (c === 0x55
  /* U */
  ) {
      return 8;
    }

  return 0;
}

function fromDecimalCode(c) {
  if (0x30
  /* 0 */
  <= c && c <= 0x39
  /* 9 */
  ) {
    return c - 0x30;
  }

  return -1;
}

function simpleEscapeSequence(c) {
  /* eslint-disable indent */
  return c === 0x30
  /* 0 */
  ? '\x00' : c === 0x61
  /* a */
  ? '\x07' : c === 0x62
  /* b */
  ? '\x08' : c === 0x74
  /* t */
  ? '\x09' : c === 0x09
  /* Tab */
  ? '\x09' : c === 0x6E
  /* n */
  ? '\x0A' : c === 0x76
  /* v */
  ? '\x0B' : c === 0x66
  /* f */
  ? '\x0C' : c === 0x72
  /* r */
  ? '\x0D' : c === 0x65
  /* e */
  ? '\x1B' : c === 0x20
  /* Space */
  ? ' ' : c === 0x22
  /* " */
  ? '\x22' : c === 0x2F
  /* / */
  ? '/' : c === 0x5C
  /* \ */
  ? '\x5C' : c === 0x4E
  /* N */
  ? '\x85' : c === 0x5F
  /* _ */
  ? '\xA0' : c === 0x4C
  /* L */
  ? "\u2028" : c === 0x50
  /* P */
  ? "\u2029" : '';
}

function charFromCodepoint(c) {
  if (c <= 0xFFFF) {
    return String.fromCharCode(c);
  } // Encode UTF-16 surrogate pair
  // https://en.wikipedia.org/wiki/UTF-16#Code_points_U.2B010000_to_U.2B10FFFF


  return String.fromCharCode((c - 0x010000 >> 10) + 0xD800, (c - 0x010000 & 0x03FF) + 0xDC00);
}

var simpleEscapeCheck = new Array(256); // integer, for fast access

var simpleEscapeMap = new Array(256);

for (var i = 0; i < 256; i++) {
  simpleEscapeCheck[i] = simpleEscapeSequence(i) ? 1 : 0;
  simpleEscapeMap[i] = simpleEscapeSequence(i);
}

function State(input, options) {
  this.input = input;
  this.filename = options['filename'] || null;
  this.schema = options['schema'] || DEFAULT_FULL_SCHEMA;
  this.onWarning = options['onWarning'] || null;
  this.legacy = options['legacy'] || false;
  this.json = options['json'] || false;
  this.listener = options['listener'] || null;
  this.implicitTypes = this.schema.compiledImplicit;
  this.typeMap = this.schema.compiledTypeMap;
  this.length = input.length;
  this.position = 0;
  this.line = 0;
  this.lineStart = 0;
  this.lineIndent = 0;
  this.documents = [];
  /*
  this.version;
  this.checkLineBreaks;
  this.tagMap;
  this.anchorMap;
  this.tag;
  this.anchor;
  this.kind;
  this.result;*/
}

function generateError(state, message) {
  return new YAMLException(message, new Mark(state.filename, state.input, state.position, state.line, state.position - state.lineStart));
}

function throwError(state, message) {
  throw generateError(state, message);
}

function throwWarning(state, message) {
  if (state.onWarning) {
    state.onWarning.call(null, generateError(state, message));
  }
}

var directiveHandlers = {
  YAML: function handleYamlDirective(state, name, args) {
    var match, major, minor;

    if (state.version !== null) {
      throwError(state, 'duplication of %YAML directive');
    }

    if (args.length !== 1) {
      throwError(state, 'YAML directive accepts exactly one argument');
    }

    match = /^([0-9]+)\.([0-9]+)$/.exec(args[0]);

    if (match === null) {
      throwError(state, 'ill-formed argument of the YAML directive');
    }

    major = parseInt(match[1], 10);
    minor = parseInt(match[2], 10);

    if (major !== 1) {
      throwError(state, 'unacceptable YAML version of the document');
    }

    state.version = args[0];
    state.checkLineBreaks = minor < 2;

    if (minor !== 1 && minor !== 2) {
      throwWarning(state, 'unsupported YAML version of the document');
    }
  },
  TAG: function handleTagDirective(state, name, args) {
    var handle, prefix;

    if (args.length !== 2) {
      throwError(state, 'TAG directive accepts exactly two arguments');
    }

    handle = args[0];
    prefix = args[1];

    if (!PATTERN_TAG_HANDLE.test(handle)) {
      throwError(state, 'ill-formed tag handle (first argument) of the TAG directive');
    }

    if (_hasOwnProperty.call(state.tagMap, handle)) {
      throwError(state, 'there is a previously declared suffix for "' + handle + '" tag handle');
    }

    if (!PATTERN_TAG_URI.test(prefix)) {
      throwError(state, 'ill-formed tag prefix (second argument) of the TAG directive');
    }

    state.tagMap[handle] = prefix;
  }
};

function captureSegment(state, start, end, checkJson) {
  var _position, _length, _character, _result;

  if (start < end) {
    _result = state.input.slice(start, end);

    if (checkJson) {
      for (_position = 0, _length = _result.length; _position < _length; _position += 1) {
        _character = _result.charCodeAt(_position);

        if (!(_character === 0x09 || 0x20 <= _character && _character <= 0x10FFFF)) {
          throwError(state, 'expected valid JSON character');
        }
      }
    } else if (PATTERN_NON_PRINTABLE.test(_result)) {
      throwError(state, 'the stream contains non-printable characters');
    }

    state.result += _result;
  }
}

function mergeMappings(state, destination, source, overridableKeys) {
  var sourceKeys, key, index, quantity;

  if (!common.isObject(source)) {
    throwError(state, 'cannot merge mappings; the provided source object is unacceptable');
  }

  sourceKeys = Object.keys(source);

  for (index = 0, quantity = sourceKeys.length; index < quantity; index += 1) {
    key = sourceKeys[index];

    if (!_hasOwnProperty.call(destination, key)) {
      destination[key] = source[key];
      overridableKeys[key] = true;
    }
  }
}

function storeMappingPair(state, _result, overridableKeys, keyTag, keyNode, valueNode, startLine, startPos) {
  var index, quantity; // The output is a plain object here, so keys can only be strings.
  // We need to convert keyNode to a string, but doing so can hang the process
  // (deeply nested arrays that explode exponentially using aliases).

  if (Array.isArray(keyNode)) {
    keyNode = Array.prototype.slice.call(keyNode);

    for (index = 0, quantity = keyNode.length; index < quantity; index += 1) {
      if (Array.isArray(keyNode[index])) {
        throwError(state, 'nested arrays are not supported inside keys');
      }

      if (_typeof(keyNode) === 'object' && _class(keyNode[index]) === '[object Object]') {
        keyNode[index] = '[object Object]';
      }
    }
  } // Avoid code execution in load() via toString property
  // (still use its own toString for arrays, timestamps,
  // and whatever user schema extensions happen to have @@toStringTag)


  if (_typeof(keyNode) === 'object' && _class(keyNode) === '[object Object]') {
    keyNode = '[object Object]';
  }

  keyNode = String(keyNode);

  if (_result === null) {
    _result = {};
  }

  if (keyTag === 'tag:yaml.org,2002:merge') {
    if (Array.isArray(valueNode)) {
      for (index = 0, quantity = valueNode.length; index < quantity; index += 1) {
        mergeMappings(state, _result, valueNode[index], overridableKeys);
      }
    } else {
      mergeMappings(state, _result, valueNode, overridableKeys);
    }
  } else {
    if (!state.json && !_hasOwnProperty.call(overridableKeys, keyNode) && _hasOwnProperty.call(_result, keyNode)) {
      state.line = startLine || state.line;
      state.position = startPos || state.position;
      throwError(state, 'duplicated mapping key');
    }

    _result[keyNode] = valueNode;
    delete overridableKeys[keyNode];
  }

  return _result;
}

function readLineBreak(state) {
  var ch;
  ch = state.input.charCodeAt(state.position);

  if (ch === 0x0A
  /* LF */
  ) {
      state.position++;
    } else if (ch === 0x0D
  /* CR */
  ) {
      state.position++;

      if (state.input.charCodeAt(state.position) === 0x0A
      /* LF */
      ) {
          state.position++;
        }
    } else {
    throwError(state, 'a line break is expected');
  }

  state.line += 1;
  state.lineStart = state.position;
}

function skipSeparationSpace(state, allowComments, checkIndent) {
  var lineBreaks = 0,
      ch = state.input.charCodeAt(state.position);

  while (ch !== 0) {
    while (is_WHITE_SPACE(ch)) {
      ch = state.input.charCodeAt(++state.position);
    }

    if (allowComments && ch === 0x23
    /* # */
    ) {
        do {
          ch = state.input.charCodeAt(++state.position);
        } while (ch !== 0x0A
        /* LF */
        && ch !== 0x0D
        /* CR */
        && ch !== 0);
      }

    if (is_EOL(ch)) {
      readLineBreak(state);
      ch = state.input.charCodeAt(state.position);
      lineBreaks++;
      state.lineIndent = 0;

      while (ch === 0x20
      /* Space */
      ) {
        state.lineIndent++;
        ch = state.input.charCodeAt(++state.position);
      }
    } else {
      break;
    }
  }

  if (checkIndent !== -1 && lineBreaks !== 0 && state.lineIndent < checkIndent) {
    throwWarning(state, 'deficient indentation');
  }

  return lineBreaks;
}

function testDocumentSeparator(state) {
  var _position = state.position,
      ch;
  ch = state.input.charCodeAt(_position); // Condition state.position === state.lineStart is tested
  // in parent on each call, for efficiency. No needs to test here again.

  if ((ch === 0x2D
  /* - */
  || ch === 0x2E
  /* . */
  ) && ch === state.input.charCodeAt(_position + 1) && ch === state.input.charCodeAt(_position + 2)) {
    _position += 3;
    ch = state.input.charCodeAt(_position);

    if (ch === 0 || is_WS_OR_EOL(ch)) {
      return true;
    }
  }

  return false;
}

function writeFoldedLines(state, count) {
  if (count === 1) {
    state.result += ' ';
  } else if (count > 1) {
    state.result += common.repeat('\n', count - 1);
  }
}

function readPlainScalar(state, nodeIndent, withinFlowCollection) {
  var preceding,
      following,
      captureStart,
      captureEnd,
      hasPendingContent,
      _line,
      _lineStart,
      _lineIndent,
      _kind = state.kind,
      _result = state.result,
      ch;

  ch = state.input.charCodeAt(state.position);

  if (is_WS_OR_EOL(ch) || is_FLOW_INDICATOR(ch) || ch === 0x23
  /* # */
  || ch === 0x26
  /* & */
  || ch === 0x2A
  /* * */
  || ch === 0x21
  /* ! */
  || ch === 0x7C
  /* | */
  || ch === 0x3E
  /* > */
  || ch === 0x27
  /* ' */
  || ch === 0x22
  /* " */
  || ch === 0x25
  /* % */
  || ch === 0x40
  /* @ */
  || ch === 0x60
  /* ` */
  ) {
      return false;
    }

  if (ch === 0x3F
  /* ? */
  || ch === 0x2D
  /* - */
  ) {
      following = state.input.charCodeAt(state.position + 1);

      if (is_WS_OR_EOL(following) || withinFlowCollection && is_FLOW_INDICATOR(following)) {
        return false;
      }
    }

  state.kind = 'scalar';
  state.result = '';
  captureStart = captureEnd = state.position;
  hasPendingContent = false;

  while (ch !== 0) {
    if (ch === 0x3A
    /* : */
    ) {
        following = state.input.charCodeAt(state.position + 1);

        if (is_WS_OR_EOL(following) || withinFlowCollection && is_FLOW_INDICATOR(following)) {
          break;
        }
      } else if (ch === 0x23
    /* # */
    ) {
        preceding = state.input.charCodeAt(state.position - 1);

        if (is_WS_OR_EOL(preceding)) {
          break;
        }
      } else if (state.position === state.lineStart && testDocumentSeparator(state) || withinFlowCollection && is_FLOW_INDICATOR(ch)) {
      break;
    } else if (is_EOL(ch)) {
      _line = state.line;
      _lineStart = state.lineStart;
      _lineIndent = state.lineIndent;
      skipSeparationSpace(state, false, -1);

      if (state.lineIndent >= nodeIndent) {
        hasPendingContent = true;
        ch = state.input.charCodeAt(state.position);
        continue;
      } else {
        state.position = captureEnd;
        state.line = _line;
        state.lineStart = _lineStart;
        state.lineIndent = _lineIndent;
        break;
      }
    }

    if (hasPendingContent) {
      captureSegment(state, captureStart, captureEnd, false);
      writeFoldedLines(state, state.line - _line);
      captureStart = captureEnd = state.position;
      hasPendingContent = false;
    }

    if (!is_WHITE_SPACE(ch)) {
      captureEnd = state.position + 1;
    }

    ch = state.input.charCodeAt(++state.position);
  }

  captureSegment(state, captureStart, captureEnd, false);

  if (state.result) {
    return true;
  }

  state.kind = _kind;
  state.result = _result;
  return false;
}

function readSingleQuotedScalar(state, nodeIndent) {
  var ch, captureStart, captureEnd;
  ch = state.input.charCodeAt(state.position);

  if (ch !== 0x27
  /* ' */
  ) {
      return false;
    }

  state.kind = 'scalar';
  state.result = '';
  state.position++;
  captureStart = captureEnd = state.position;

  while ((ch = state.input.charCodeAt(state.position)) !== 0) {
    if (ch === 0x27
    /* ' */
    ) {
        captureSegment(state, captureStart, state.position, true);
        ch = state.input.charCodeAt(++state.position);

        if (ch === 0x27
        /* ' */
        ) {
            captureStart = state.position;
            state.position++;
            captureEnd = state.position;
          } else {
          return true;
        }
      } else if (is_EOL(ch)) {
      captureSegment(state, captureStart, captureEnd, true);
      writeFoldedLines(state, skipSeparationSpace(state, false, nodeIndent));
      captureStart = captureEnd = state.position;
    } else if (state.position === state.lineStart && testDocumentSeparator(state)) {
      throwError(state, 'unexpected end of the document within a single quoted scalar');
    } else {
      state.position++;
      captureEnd = state.position;
    }
  }

  throwError(state, 'unexpected end of the stream within a single quoted scalar');
}

function readDoubleQuotedScalar(state, nodeIndent) {
  var captureStart, captureEnd, hexLength, hexResult, tmp, ch;
  ch = state.input.charCodeAt(state.position);

  if (ch !== 0x22
  /* " */
  ) {
      return false;
    }

  state.kind = 'scalar';
  state.result = '';
  state.position++;
  captureStart = captureEnd = state.position;

  while ((ch = state.input.charCodeAt(state.position)) !== 0) {
    if (ch === 0x22
    /* " */
    ) {
        captureSegment(state, captureStart, state.position, true);
        state.position++;
        return true;
      } else if (ch === 0x5C
    /* \ */
    ) {
        captureSegment(state, captureStart, state.position, true);
        ch = state.input.charCodeAt(++state.position);

        if (is_EOL(ch)) {
          skipSeparationSpace(state, false, nodeIndent); // TODO: rework to inline fn with no type cast?
        } else if (ch < 256 && simpleEscapeCheck[ch]) {
          state.result += simpleEscapeMap[ch];
          state.position++;
        } else if ((tmp = escapedHexLen(ch)) > 0) {
          hexLength = tmp;
          hexResult = 0;

          for (; hexLength > 0; hexLength--) {
            ch = state.input.charCodeAt(++state.position);

            if ((tmp = fromHexCode(ch)) >= 0) {
              hexResult = (hexResult << 4) + tmp;
            } else {
              throwError(state, 'expected hexadecimal character');
            }
          }

          state.result += charFromCodepoint(hexResult);
          state.position++;
        } else {
          throwError(state, 'unknown escape sequence');
        }

        captureStart = captureEnd = state.position;
      } else if (is_EOL(ch)) {
      captureSegment(state, captureStart, captureEnd, true);
      writeFoldedLines(state, skipSeparationSpace(state, false, nodeIndent));
      captureStart = captureEnd = state.position;
    } else if (state.position === state.lineStart && testDocumentSeparator(state)) {
      throwError(state, 'unexpected end of the document within a double quoted scalar');
    } else {
      state.position++;
      captureEnd = state.position;
    }
  }

  throwError(state, 'unexpected end of the stream within a double quoted scalar');
}

function readFlowCollection(state, nodeIndent) {
  var readNext = true,
      _line,
      _tag = state.tag,
      _result,
      _anchor = state.anchor,
      following,
      terminator,
      isPair,
      isExplicitPair,
      isMapping,
      overridableKeys = {},
      keyNode,
      keyTag,
      valueNode,
      ch;

  ch = state.input.charCodeAt(state.position);

  if (ch === 0x5B
  /* [ */
  ) {
      terminator = 0x5D;
      /* ] */

      isMapping = false;
      _result = [];
    } else if (ch === 0x7B
  /* { */
  ) {
      terminator = 0x7D;
      /* } */

      isMapping = true;
      _result = {};
    } else {
    return false;
  }

  if (state.anchor !== null) {
    state.anchorMap[state.anchor] = _result;
  }

  ch = state.input.charCodeAt(++state.position);

  while (ch !== 0) {
    skipSeparationSpace(state, true, nodeIndent);
    ch = state.input.charCodeAt(state.position);

    if (ch === terminator) {
      state.position++;
      state.tag = _tag;
      state.anchor = _anchor;
      state.kind = isMapping ? 'mapping' : 'sequence';
      state.result = _result;
      return true;
    } else if (!readNext) {
      throwError(state, 'missed comma between flow collection entries');
    }

    keyTag = keyNode = valueNode = null;
    isPair = isExplicitPair = false;

    if (ch === 0x3F
    /* ? */
    ) {
        following = state.input.charCodeAt(state.position + 1);

        if (is_WS_OR_EOL(following)) {
          isPair = isExplicitPair = true;
          state.position++;
          skipSeparationSpace(state, true, nodeIndent);
        }
      }

    _line = state.line;
    composeNode(state, nodeIndent, CONTEXT_FLOW_IN, false, true);
    keyTag = state.tag;
    keyNode = state.result;
    skipSeparationSpace(state, true, nodeIndent);
    ch = state.input.charCodeAt(state.position);

    if ((isExplicitPair || state.line === _line) && ch === 0x3A
    /* : */
    ) {
        isPair = true;
        ch = state.input.charCodeAt(++state.position);
        skipSeparationSpace(state, true, nodeIndent);
        composeNode(state, nodeIndent, CONTEXT_FLOW_IN, false, true);
        valueNode = state.result;
      }

    if (isMapping) {
      storeMappingPair(state, _result, overridableKeys, keyTag, keyNode, valueNode);
    } else if (isPair) {
      _result.push(storeMappingPair(state, null, overridableKeys, keyTag, keyNode, valueNode));
    } else {
      _result.push(keyNode);
    }

    skipSeparationSpace(state, true, nodeIndent);
    ch = state.input.charCodeAt(state.position);

    if (ch === 0x2C
    /* , */
    ) {
        readNext = true;
        ch = state.input.charCodeAt(++state.position);
      } else {
      readNext = false;
    }
  }

  throwError(state, 'unexpected end of the stream within a flow collection');
}

function readBlockScalar(state, nodeIndent) {
  var captureStart,
      folding,
      chomping = CHOMPING_CLIP,
      didReadContent = false,
      detectedIndent = false,
      textIndent = nodeIndent,
      emptyLines = 0,
      atMoreIndented = false,
      tmp,
      ch;
  ch = state.input.charCodeAt(state.position);

  if (ch === 0x7C
  /* | */
  ) {
      folding = false;
    } else if (ch === 0x3E
  /* > */
  ) {
      folding = true;
    } else {
    return false;
  }

  state.kind = 'scalar';
  state.result = '';

  while (ch !== 0) {
    ch = state.input.charCodeAt(++state.position);

    if (ch === 0x2B
    /* + */
    || ch === 0x2D
    /* - */
    ) {
        if (CHOMPING_CLIP === chomping) {
          chomping = ch === 0x2B
          /* + */
          ? CHOMPING_KEEP : CHOMPING_STRIP;
        } else {
          throwError(state, 'repeat of a chomping mode identifier');
        }
      } else if ((tmp = fromDecimalCode(ch)) >= 0) {
      if (tmp === 0) {
        throwError(state, 'bad explicit indentation width of a block scalar; it cannot be less than one');
      } else if (!detectedIndent) {
        textIndent = nodeIndent + tmp - 1;
        detectedIndent = true;
      } else {
        throwError(state, 'repeat of an indentation width identifier');
      }
    } else {
      break;
    }
  }

  if (is_WHITE_SPACE(ch)) {
    do {
      ch = state.input.charCodeAt(++state.position);
    } while (is_WHITE_SPACE(ch));

    if (ch === 0x23
    /* # */
    ) {
        do {
          ch = state.input.charCodeAt(++state.position);
        } while (!is_EOL(ch) && ch !== 0);
      }
  }

  while (ch !== 0) {
    readLineBreak(state);
    state.lineIndent = 0;
    ch = state.input.charCodeAt(state.position);

    while ((!detectedIndent || state.lineIndent < textIndent) && ch === 0x20
    /* Space */
    ) {
      state.lineIndent++;
      ch = state.input.charCodeAt(++state.position);
    }

    if (!detectedIndent && state.lineIndent > textIndent) {
      textIndent = state.lineIndent;
    }

    if (is_EOL(ch)) {
      emptyLines++;
      continue;
    } // End of the scalar.


    if (state.lineIndent < textIndent) {
      // Perform the chomping.
      if (chomping === CHOMPING_KEEP) {
        state.result += common.repeat('\n', didReadContent ? 1 + emptyLines : emptyLines);
      } else if (chomping === CHOMPING_CLIP) {
        if (didReadContent) {
          // i.e. only if the scalar is not empty.
          state.result += '\n';
        }
      } // Break this `while` cycle and go to the funciton's epilogue.


      break;
    } // Folded style: use fancy rules to handle line breaks.


    if (folding) {
      // Lines starting with white space characters (more-indented lines) are not folded.
      if (is_WHITE_SPACE(ch)) {
        atMoreIndented = true; // except for the first content line (cf. Example 8.1)

        state.result += common.repeat('\n', didReadContent ? 1 + emptyLines : emptyLines); // End of more-indented block.
      } else if (atMoreIndented) {
        atMoreIndented = false;
        state.result += common.repeat('\n', emptyLines + 1); // Just one line break - perceive as the same line.
      } else if (emptyLines === 0) {
        if (didReadContent) {
          // i.e. only if we have already read some scalar content.
          state.result += ' ';
        } // Several line breaks - perceive as different lines.

      } else {
        state.result += common.repeat('\n', emptyLines);
      } // Literal style: just add exact number of line breaks between content lines.

    } else {
      // Keep all line breaks except the header line break.
      state.result += common.repeat('\n', didReadContent ? 1 + emptyLines : emptyLines);
    }

    didReadContent = true;
    detectedIndent = true;
    emptyLines = 0;
    captureStart = state.position;

    while (!is_EOL(ch) && ch !== 0) {
      ch = state.input.charCodeAt(++state.position);
    }

    captureSegment(state, captureStart, state.position, false);
  }

  return true;
}

function readBlockSequence(state, nodeIndent) {
  var _line,
      _tag = state.tag,
      _anchor = state.anchor,
      _result = [],
      following,
      detected = false,
      ch;

  if (state.anchor !== null) {
    state.anchorMap[state.anchor] = _result;
  }

  ch = state.input.charCodeAt(state.position);

  while (ch !== 0) {
    if (ch !== 0x2D
    /* - */
    ) {
        break;
      }

    following = state.input.charCodeAt(state.position + 1);

    if (!is_WS_OR_EOL(following)) {
      break;
    }

    detected = true;
    state.position++;

    if (skipSeparationSpace(state, true, -1)) {
      if (state.lineIndent <= nodeIndent) {
        _result.push(null);

        ch = state.input.charCodeAt(state.position);
        continue;
      }
    }

    _line = state.line;
    composeNode(state, nodeIndent, CONTEXT_BLOCK_IN, false, true);

    _result.push(state.result);

    skipSeparationSpace(state, true, -1);
    ch = state.input.charCodeAt(state.position);

    if ((state.line === _line || state.lineIndent > nodeIndent) && ch !== 0) {
      throwError(state, 'bad indentation of a sequence entry');
    } else if (state.lineIndent < nodeIndent) {
      break;
    }
  }

  if (detected) {
    state.tag = _tag;
    state.anchor = _anchor;
    state.kind = 'sequence';
    state.result = _result;
    return true;
  }

  return false;
}

function readBlockMapping(state, nodeIndent, flowIndent) {
  var following,
      allowCompact,
      _line,
      _pos,
      _tag = state.tag,
      _anchor = state.anchor,
      _result = {},
      overridableKeys = {},
      keyTag = null,
      keyNode = null,
      valueNode = null,
      atExplicitKey = false,
      detected = false,
      ch;

  if (state.anchor !== null) {
    state.anchorMap[state.anchor] = _result;
  }

  ch = state.input.charCodeAt(state.position);

  while (ch !== 0) {
    following = state.input.charCodeAt(state.position + 1);
    _line = state.line; // Save the current line.

    _pos = state.position; //
    // Explicit notation case. There are two separate blocks:
    // first for the key (denoted by "?") and second for the value (denoted by ":")
    //

    if ((ch === 0x3F
    /* ? */
    || ch === 0x3A
    /* : */
    ) && is_WS_OR_EOL(following)) {
      if (ch === 0x3F
      /* ? */
      ) {
          if (atExplicitKey) {
            storeMappingPair(state, _result, overridableKeys, keyTag, keyNode, null);
            keyTag = keyNode = valueNode = null;
          }

          detected = true;
          atExplicitKey = true;
          allowCompact = true;
        } else if (atExplicitKey) {
        // i.e. 0x3A/* : */ === character after the explicit key.
        atExplicitKey = false;
        allowCompact = true;
      } else {
        throwError(state, 'incomplete explicit mapping pair; a key node is missed; or followed by a non-tabulated empty line');
      }

      state.position += 1;
      ch = following; //
      // Implicit notation case. Flow-style node as the key first, then ":", and the value.
      //
    } else if (composeNode(state, flowIndent, CONTEXT_FLOW_OUT, false, true)) {
      if (state.line === _line) {
        ch = state.input.charCodeAt(state.position);

        while (is_WHITE_SPACE(ch)) {
          ch = state.input.charCodeAt(++state.position);
        }

        if (ch === 0x3A
        /* : */
        ) {
            ch = state.input.charCodeAt(++state.position);

            if (!is_WS_OR_EOL(ch)) {
              throwError(state, 'a whitespace character is expected after the key-value separator within a block mapping');
            }

            if (atExplicitKey) {
              storeMappingPair(state, _result, overridableKeys, keyTag, keyNode, null);
              keyTag = keyNode = valueNode = null;
            }

            detected = true;
            atExplicitKey = false;
            allowCompact = false;
            keyTag = state.tag;
            keyNode = state.result;
          } else if (detected) {
          throwError(state, 'can not read an implicit mapping pair; a colon is missed');
        } else {
          state.tag = _tag;
          state.anchor = _anchor;
          return true; // Keep the result of `composeNode`.
        }
      } else if (detected) {
        throwError(state, 'can not read a block mapping entry; a multiline key may not be an implicit key');
      } else {
        state.tag = _tag;
        state.anchor = _anchor;
        return true; // Keep the result of `composeNode`.
      }
    } else {
        break; // Reading is done. Go to the epilogue.
      } //
    // Common reading code for both explicit and implicit notations.
    //


    if (state.line === _line || state.lineIndent > nodeIndent) {
      if (composeNode(state, nodeIndent, CONTEXT_BLOCK_OUT, true, allowCompact)) {
        if (atExplicitKey) {
          keyNode = state.result;
        } else {
          valueNode = state.result;
        }
      }

      if (!atExplicitKey) {
        storeMappingPair(state, _result, overridableKeys, keyTag, keyNode, valueNode, _line, _pos);
        keyTag = keyNode = valueNode = null;
      }

      skipSeparationSpace(state, true, -1);
      ch = state.input.charCodeAt(state.position);
    }

    if (state.lineIndent > nodeIndent && ch !== 0) {
      throwError(state, 'bad indentation of a mapping entry');
    } else if (state.lineIndent < nodeIndent) {
      break;
    }
  } //
  // Epilogue.
  //
  // Special case: last mapping's node contains only the key in explicit notation.


  if (atExplicitKey) {
    storeMappingPair(state, _result, overridableKeys, keyTag, keyNode, null);
  } // Expose the resulting mapping.


  if (detected) {
    state.tag = _tag;
    state.anchor = _anchor;
    state.kind = 'mapping';
    state.result = _result;
  }

  return detected;
}

function readTagProperty(state) {
  var _position,
      isVerbatim = false,
      isNamed = false,
      tagHandle,
      tagName,
      ch;

  ch = state.input.charCodeAt(state.position);
  if (ch !== 0x21
  /* ! */
  ) return false;

  if (state.tag !== null) {
    throwError(state, 'duplication of a tag property');
  }

  ch = state.input.charCodeAt(++state.position);

  if (ch === 0x3C
  /* < */
  ) {
      isVerbatim = true;
      ch = state.input.charCodeAt(++state.position);
    } else if (ch === 0x21
  /* ! */
  ) {
      isNamed = true;
      tagHandle = '!!';
      ch = state.input.charCodeAt(++state.position);
    } else {
    tagHandle = '!';
  }

  _position = state.position;

  if (isVerbatim) {
    do {
      ch = state.input.charCodeAt(++state.position);
    } while (ch !== 0 && ch !== 0x3E
    /* > */
    );

    if (state.position < state.length) {
      tagName = state.input.slice(_position, state.position);
      ch = state.input.charCodeAt(++state.position);
    } else {
      throwError(state, 'unexpected end of the stream within a verbatim tag');
    }
  } else {
    while (ch !== 0 && !is_WS_OR_EOL(ch)) {
      if (ch === 0x21
      /* ! */
      ) {
          if (!isNamed) {
            tagHandle = state.input.slice(_position - 1, state.position + 1);

            if (!PATTERN_TAG_HANDLE.test(tagHandle)) {
              throwError(state, 'named tag handle cannot contain such characters');
            }

            isNamed = true;
            _position = state.position + 1;
          } else {
            throwError(state, 'tag suffix cannot contain exclamation marks');
          }
        }

      ch = state.input.charCodeAt(++state.position);
    }

    tagName = state.input.slice(_position, state.position);

    if (PATTERN_FLOW_INDICATORS.test(tagName)) {
      throwError(state, 'tag suffix cannot contain flow indicator characters');
    }
  }

  if (tagName && !PATTERN_TAG_URI.test(tagName)) {
    throwError(state, 'tag name cannot contain such characters: ' + tagName);
  }

  if (isVerbatim) {
    state.tag = tagName;
  } else if (_hasOwnProperty.call(state.tagMap, tagHandle)) {
    state.tag = state.tagMap[tagHandle] + tagName;
  } else if (tagHandle === '!') {
    state.tag = '!' + tagName;
  } else if (tagHandle === '!!') {
    state.tag = 'tag:yaml.org,2002:' + tagName;
  } else {
    throwError(state, 'undeclared tag handle "' + tagHandle + '"');
  }

  return true;
}

function readAnchorProperty(state) {
  var _position, ch;

  ch = state.input.charCodeAt(state.position);
  if (ch !== 0x26
  /* & */
  ) return false;

  if (state.anchor !== null) {
    throwError(state, 'duplication of an anchor property');
  }

  ch = state.input.charCodeAt(++state.position);
  _position = state.position;

  while (ch !== 0 && !is_WS_OR_EOL(ch) && !is_FLOW_INDICATOR(ch)) {
    ch = state.input.charCodeAt(++state.position);
  }

  if (state.position === _position) {
    throwError(state, 'name of an anchor node must contain at least one character');
  }

  state.anchor = state.input.slice(_position, state.position);
  return true;
}

function readAlias(state) {
  var _position, alias, ch;

  ch = state.input.charCodeAt(state.position);
  if (ch !== 0x2A
  /* * */
  ) return false;
  ch = state.input.charCodeAt(++state.position);
  _position = state.position;

  while (ch !== 0 && !is_WS_OR_EOL(ch) && !is_FLOW_INDICATOR(ch)) {
    ch = state.input.charCodeAt(++state.position);
  }

  if (state.position === _position) {
    throwError(state, 'name of an alias node must contain at least one character');
  }

  alias = state.input.slice(_position, state.position);

  if (!state.anchorMap.hasOwnProperty(alias)) {
    throwError(state, 'unidentified alias "' + alias + '"');
  }

  state.result = state.anchorMap[alias];
  skipSeparationSpace(state, true, -1);
  return true;
}

function composeNode(state, parentIndent, nodeContext, allowToSeek, allowCompact) {
  var allowBlockStyles,
      allowBlockScalars,
      allowBlockCollections,
      indentStatus = 1,
      // 1: this>parent, 0: this=parent, -1: this<parent
  atNewLine = false,
      hasContent = false,
      typeIndex,
      typeQuantity,
      type,
      flowIndent,
      blockIndent;

  if (state.listener !== null) {
    state.listener('open', state);
  }

  state.tag = null;
  state.anchor = null;
  state.kind = null;
  state.result = null;
  allowBlockStyles = allowBlockScalars = allowBlockCollections = CONTEXT_BLOCK_OUT === nodeContext || CONTEXT_BLOCK_IN === nodeContext;

  if (allowToSeek) {
    if (skipSeparationSpace(state, true, -1)) {
      atNewLine = true;

      if (state.lineIndent > parentIndent) {
        indentStatus = 1;
      } else if (state.lineIndent === parentIndent) {
        indentStatus = 0;
      } else if (state.lineIndent < parentIndent) {
        indentStatus = -1;
      }
    }
  }

  if (indentStatus === 1) {
    while (readTagProperty(state) || readAnchorProperty(state)) {
      if (skipSeparationSpace(state, true, -1)) {
        atNewLine = true;
        allowBlockCollections = allowBlockStyles;

        if (state.lineIndent > parentIndent) {
          indentStatus = 1;
        } else if (state.lineIndent === parentIndent) {
          indentStatus = 0;
        } else if (state.lineIndent < parentIndent) {
          indentStatus = -1;
        }
      } else {
        allowBlockCollections = false;
      }
    }
  }

  if (allowBlockCollections) {
    allowBlockCollections = atNewLine || allowCompact;
  }

  if (indentStatus === 1 || CONTEXT_BLOCK_OUT === nodeContext) {
    if (CONTEXT_FLOW_IN === nodeContext || CONTEXT_FLOW_OUT === nodeContext) {
      flowIndent = parentIndent;
    } else {
      flowIndent = parentIndent + 1;
    }

    blockIndent = state.position - state.lineStart;

    if (indentStatus === 1) {
      if (allowBlockCollections && (readBlockSequence(state, blockIndent) || readBlockMapping(state, blockIndent, flowIndent)) || readFlowCollection(state, flowIndent)) {
        hasContent = true;
      } else {
        if (allowBlockScalars && readBlockScalar(state, flowIndent) || readSingleQuotedScalar(state, flowIndent) || readDoubleQuotedScalar(state, flowIndent)) {
          hasContent = true;
        } else if (readAlias(state)) {
          hasContent = true;

          if (state.tag !== null || state.anchor !== null) {
            throwError(state, 'alias node should not have any properties');
          }
        } else if (readPlainScalar(state, flowIndent, CONTEXT_FLOW_IN === nodeContext)) {
          hasContent = true;

          if (state.tag === null) {
            state.tag = '?';
          }
        }

        if (state.anchor !== null) {
          state.anchorMap[state.anchor] = state.result;
        }
      }
    } else if (indentStatus === 0) {
      // Special case: block sequences are allowed to have same indentation level as the parent.
      // http://www.yaml.org/spec/1.2/spec.html#id2799784
      hasContent = allowBlockCollections && readBlockSequence(state, blockIndent);
    }
  }

  if (state.tag !== null && state.tag !== '!') {
    if (state.tag === '?') {
      for (typeIndex = 0, typeQuantity = state.implicitTypes.length; typeIndex < typeQuantity; typeIndex += 1) {
        type = state.implicitTypes[typeIndex]; // Implicit resolving is not allowed for non-scalar types, and '?'
        // non-specific tag is only assigned to plain scalars. So, it isn't
        // needed to check for 'kind' conformity.

        if (type.resolve(state.result)) {
          // `state.result` updated in resolver if matched
          state.result = type.construct(state.result);
          state.tag = type.tag;

          if (state.anchor !== null) {
            state.anchorMap[state.anchor] = state.result;
          }

          break;
        }
      }
    } else if (_hasOwnProperty.call(state.typeMap[state.kind || 'fallback'], state.tag)) {
      type = state.typeMap[state.kind || 'fallback'][state.tag];

      if (state.result !== null && type.kind !== state.kind) {
        throwError(state, 'unacceptable node kind for !<' + state.tag + '> tag; it should be "' + type.kind + '", not "' + state.kind + '"');
      }

      if (!type.resolve(state.result)) {
        // `state.result` updated in resolver if matched
        throwError(state, 'cannot resolve a node with !<' + state.tag + '> explicit tag');
      } else {
        state.result = type.construct(state.result);

        if (state.anchor !== null) {
          state.anchorMap[state.anchor] = state.result;
        }
      }
    } else {
      throwError(state, 'unknown tag !<' + state.tag + '>');
    }
  }

  if (state.listener !== null) {
    state.listener('close', state);
  }

  return state.tag !== null || state.anchor !== null || hasContent;
}

function readDocument(state) {
  var documentStart = state.position,
      _position,
      directiveName,
      directiveArgs,
      hasDirectives = false,
      ch;

  state.version = null;
  state.checkLineBreaks = state.legacy;
  state.tagMap = {};
  state.anchorMap = {};

  while ((ch = state.input.charCodeAt(state.position)) !== 0) {
    skipSeparationSpace(state, true, -1);
    ch = state.input.charCodeAt(state.position);

    if (state.lineIndent > 0 || ch !== 0x25
    /* % */
    ) {
        break;
      }

    hasDirectives = true;
    ch = state.input.charCodeAt(++state.position);
    _position = state.position;

    while (ch !== 0 && !is_WS_OR_EOL(ch)) {
      ch = state.input.charCodeAt(++state.position);
    }

    directiveName = state.input.slice(_position, state.position);
    directiveArgs = [];

    if (directiveName.length < 1) {
      throwError(state, 'directive name must not be less than one character in length');
    }

    while (ch !== 0) {
      while (is_WHITE_SPACE(ch)) {
        ch = state.input.charCodeAt(++state.position);
      }

      if (ch === 0x23
      /* # */
      ) {
          do {
            ch = state.input.charCodeAt(++state.position);
          } while (ch !== 0 && !is_EOL(ch));

          break;
        }

      if (is_EOL(ch)) break;
      _position = state.position;

      while (ch !== 0 && !is_WS_OR_EOL(ch)) {
        ch = state.input.charCodeAt(++state.position);
      }

      directiveArgs.push(state.input.slice(_position, state.position));
    }

    if (ch !== 0) readLineBreak(state);

    if (_hasOwnProperty.call(directiveHandlers, directiveName)) {
      directiveHandlers[directiveName](state, directiveName, directiveArgs);
    } else {
      throwWarning(state, 'unknown document directive "' + directiveName + '"');
    }
  }

  skipSeparationSpace(state, true, -1);

  if (state.lineIndent === 0 && state.input.charCodeAt(state.position) === 0x2D
  /* - */
  && state.input.charCodeAt(state.position + 1) === 0x2D
  /* - */
  && state.input.charCodeAt(state.position + 2) === 0x2D
  /* - */
  ) {
      state.position += 3;
      skipSeparationSpace(state, true, -1);
    } else if (hasDirectives) {
    throwError(state, 'directives end mark is expected');
  }

  composeNode(state, state.lineIndent - 1, CONTEXT_BLOCK_OUT, false, true);
  skipSeparationSpace(state, true, -1);

  if (state.checkLineBreaks && PATTERN_NON_ASCII_LINE_BREAKS.test(state.input.slice(documentStart, state.position))) {
    throwWarning(state, 'non-ASCII line breaks are interpreted as content');
  }

  state.documents.push(state.result);

  if (state.position === state.lineStart && testDocumentSeparator(state)) {
    if (state.input.charCodeAt(state.position) === 0x2E
    /* . */
    ) {
        state.position += 3;
        skipSeparationSpace(state, true, -1);
      }

    return;
  }

  if (state.position < state.length - 1) {
    throwError(state, 'end of the stream or a document separator is expected');
  } else {
    return;
  }
}

function loadDocuments(input, options) {
  input = String(input);
  options = options || {};

  if (input.length !== 0) {
    // Add tailing `\n` if not exists
    if (input.charCodeAt(input.length - 1) !== 0x0A
    /* LF */
    && input.charCodeAt(input.length - 1) !== 0x0D
    /* CR */
    ) {
        input += '\n';
      } // Strip BOM


    if (input.charCodeAt(0) === 0xFEFF) {
      input = input.slice(1);
    }
  }

  var state = new State(input, options); // Use 0 as string terminator. That significantly simplifies bounds check.

  state.input += '\0';

  while (state.input.charCodeAt(state.position) === 0x20
  /* Space */
  ) {
    state.lineIndent += 1;
    state.position += 1;
  }

  while (state.position < state.length - 1) {
    readDocument(state);
  }

  return state.documents;
}

function loadAll(input, iterator, options) {
  var documents = loadDocuments(input, options),
      index,
      length;

  if (typeof iterator !== 'function') {
    return documents;
  }

  for (index = 0, length = documents.length; index < length; index += 1) {
    iterator(documents[index]);
  }
}

function load(input, options) {
  var documents = loadDocuments(input, options);

  if (documents.length === 0) {
    /*eslint-disable no-undefined*/
    return undefined;
  } else if (documents.length === 1) {
    return documents[0];
  }

  throw new YAMLException('expected a single document in the stream, but found more');
}

function safeLoadAll(input, output, options) {
  if (typeof output === 'function') {
    loadAll(input, output, common.extend({
      schema: DEFAULT_SAFE_SCHEMA
    }, options));
  } else {
    return loadAll(input, common.extend({
      schema: DEFAULT_SAFE_SCHEMA
    }, options));
  }
}

function safeLoad(input, options) {
  return load(input, common.extend({
    schema: DEFAULT_SAFE_SCHEMA
  }, options));
}

module.exports.loadAll = loadAll;
module.exports.load = load;
module.exports.safeLoadAll = safeLoadAll;
module.exports.safeLoad = safeLoad;

/***/ }),
/* 155 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


var common = __webpack_require__(41);

function Mark(name, buffer, position, line, column) {
  this.name = name;
  this.buffer = buffer;
  this.position = position;
  this.line = line;
  this.column = column;
}

Mark.prototype.getSnippet = function getSnippet(indent, maxLength) {
  var head, start, tail, end, snippet;
  if (!this.buffer) return null;
  indent = indent || 4;
  maxLength = maxLength || 75;
  head = '';
  start = this.position;

  while (start > 0 && "\0\r\n\x85\u2028\u2029".indexOf(this.buffer.charAt(start - 1)) === -1) {
    start -= 1;

    if (this.position - start > maxLength / 2 - 1) {
      head = ' ... ';
      start += 5;
      break;
    }
  }

  tail = '';
  end = this.position;

  while (end < this.buffer.length && "\0\r\n\x85\u2028\u2029".indexOf(this.buffer.charAt(end)) === -1) {
    end += 1;

    if (end - this.position > maxLength / 2 - 1) {
      tail = ' ... ';
      end -= 5;
      break;
    }
  }

  snippet = this.buffer.slice(start, end);
  return common.repeat(' ', indent) + head + snippet + tail + '\n' + common.repeat(' ', indent + this.position - start + head.length) + '^';
};

Mark.prototype.toString = function toString(compact) {
  var snippet,
      where = '';

  if (this.name) {
    where += 'in "' + this.name + '" ';
  }

  where += 'at line ' + (this.line + 1) + ', column ' + (this.column + 1);

  if (!compact) {
    snippet = this.getSnippet();

    if (snippet) {
      where += ':\n' + snippet;
    }
  }

  return where;
};

module.exports = Mark;

/***/ }),
/* 156 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


var Type = __webpack_require__(15);

module.exports = new Type('tag:yaml.org,2002:str', {
  kind: 'scalar',
  construct: function construct(data) {
    return data !== null ? data : '';
  }
});

/***/ }),
/* 157 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


var Type = __webpack_require__(15);

module.exports = new Type('tag:yaml.org,2002:seq', {
  kind: 'sequence',
  construct: function construct(data) {
    return data !== null ? data : [];
  }
});

/***/ }),
/* 158 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


var Type = __webpack_require__(15);

module.exports = new Type('tag:yaml.org,2002:map', {
  kind: 'mapping',
  construct: function construct(data) {
    return data !== null ? data : {};
  }
});

/***/ }),
/* 159 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


var Type = __webpack_require__(15);

function resolveYamlNull(data) {
  if (data === null) return true;
  var max = data.length;
  return max === 1 && data === '~' || max === 4 && (data === 'null' || data === 'Null' || data === 'NULL');
}

function constructYamlNull() {
  return null;
}

function isNull(object) {
  return object === null;
}

module.exports = new Type('tag:yaml.org,2002:null', {
  kind: 'scalar',
  resolve: resolveYamlNull,
  construct: constructYamlNull,
  predicate: isNull,
  represent: {
    canonical: function canonical() {
      return '~';
    },
    lowercase: function lowercase() {
      return 'null';
    },
    uppercase: function uppercase() {
      return 'NULL';
    },
    camelcase: function camelcase() {
      return 'Null';
    }
  },
  defaultStyle: 'lowercase'
});

/***/ }),
/* 160 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


var Type = __webpack_require__(15);

function resolveYamlBoolean(data) {
  if (data === null) return false;
  var max = data.length;
  return max === 4 && (data === 'true' || data === 'True' || data === 'TRUE') || max === 5 && (data === 'false' || data === 'False' || data === 'FALSE');
}

function constructYamlBoolean(data) {
  return data === 'true' || data === 'True' || data === 'TRUE';
}

function isBoolean(object) {
  return Object.prototype.toString.call(object) === '[object Boolean]';
}

module.exports = new Type('tag:yaml.org,2002:bool', {
  kind: 'scalar',
  resolve: resolveYamlBoolean,
  construct: constructYamlBoolean,
  predicate: isBoolean,
  represent: {
    lowercase: function lowercase(object) {
      return object ? 'true' : 'false';
    },
    uppercase: function uppercase(object) {
      return object ? 'TRUE' : 'FALSE';
    },
    camelcase: function camelcase(object) {
      return object ? 'True' : 'False';
    }
  },
  defaultStyle: 'lowercase'
});

/***/ }),
/* 161 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


var common = __webpack_require__(41);

var Type = __webpack_require__(15);

function isHexCode(c) {
  return 0x30
  /* 0 */
  <= c && c <= 0x39
  /* 9 */
  || 0x41
  /* A */
  <= c && c <= 0x46
  /* F */
  || 0x61
  /* a */
  <= c && c <= 0x66
  /* f */
  ;
}

function isOctCode(c) {
  return 0x30
  /* 0 */
  <= c && c <= 0x37
  /* 7 */
  ;
}

function isDecCode(c) {
  return 0x30
  /* 0 */
  <= c && c <= 0x39
  /* 9 */
  ;
}

function resolveYamlInteger(data) {
  if (data === null) return false;
  var max = data.length,
      index = 0,
      hasDigits = false,
      ch;
  if (!max) return false;
  ch = data[index]; // sign

  if (ch === '-' || ch === '+') {
    ch = data[++index];
  }

  if (ch === '0') {
    // 0
    if (index + 1 === max) return true;
    ch = data[++index]; // base 2, base 8, base 16

    if (ch === 'b') {
      // base 2
      index++;

      for (; index < max; index++) {
        ch = data[index];
        if (ch === '_') continue;
        if (ch !== '0' && ch !== '1') return false;
        hasDigits = true;
      }

      return hasDigits && ch !== '_';
    }

    if (ch === 'x') {
      // base 16
      index++;

      for (; index < max; index++) {
        ch = data[index];
        if (ch === '_') continue;
        if (!isHexCode(data.charCodeAt(index))) return false;
        hasDigits = true;
      }

      return hasDigits && ch !== '_';
    } // base 8


    for (; index < max; index++) {
      ch = data[index];
      if (ch === '_') continue;
      if (!isOctCode(data.charCodeAt(index))) return false;
      hasDigits = true;
    }

    return hasDigits && ch !== '_';
  } // base 10 (except 0) or base 60
  // value should not start with `_`;


  if (ch === '_') return false;

  for (; index < max; index++) {
    ch = data[index];
    if (ch === '_') continue;
    if (ch === ':') break;

    if (!isDecCode(data.charCodeAt(index))) {
      return false;
    }

    hasDigits = true;
  } // Should have digits and should not end with `_`


  if (!hasDigits || ch === '_') return false; // if !base60 - done;

  if (ch !== ':') return true; // base60 almost not used, no needs to optimize

  return /^(:[0-5]?[0-9])+$/.test(data.slice(index));
}

function constructYamlInteger(data) {
  var value = data,
      sign = 1,
      ch,
      base,
      digits = [];

  if (value.indexOf('_') !== -1) {
    value = value.replace(/_/g, '');
  }

  ch = value[0];

  if (ch === '-' || ch === '+') {
    if (ch === '-') sign = -1;
    value = value.slice(1);
    ch = value[0];
  }

  if (value === '0') return 0;

  if (ch === '0') {
    if (value[1] === 'b') return sign * parseInt(value.slice(2), 2);
    if (value[1] === 'x') return sign * parseInt(value, 16);
    return sign * parseInt(value, 8);
  }

  if (value.indexOf(':') !== -1) {
    value.split(':').forEach(function (v) {
      digits.unshift(parseInt(v, 10));
    });
    value = 0;
    base = 1;
    digits.forEach(function (d) {
      value += d * base;
      base *= 60;
    });
    return sign * value;
  }

  return sign * parseInt(value, 10);
}

function isInteger(object) {
  return Object.prototype.toString.call(object) === '[object Number]' && object % 1 === 0 && !common.isNegativeZero(object);
}

module.exports = new Type('tag:yaml.org,2002:int', {
  kind: 'scalar',
  resolve: resolveYamlInteger,
  construct: constructYamlInteger,
  predicate: isInteger,
  represent: {
    binary: function binary(obj) {
      return obj >= 0 ? '0b' + obj.toString(2) : '-0b' + obj.toString(2).slice(1);
    },
    octal: function octal(obj) {
      return obj >= 0 ? '0' + obj.toString(8) : '-0' + obj.toString(8).slice(1);
    },
    decimal: function decimal(obj) {
      return obj.toString(10);
    },

    /* eslint-disable max-len */
    hexadecimal: function hexadecimal(obj) {
      return obj >= 0 ? '0x' + obj.toString(16).toUpperCase() : '-0x' + obj.toString(16).toUpperCase().slice(1);
    }
  },
  defaultStyle: 'decimal',
  styleAliases: {
    binary: [2, 'bin'],
    octal: [8, 'oct'],
    decimal: [10, 'dec'],
    hexadecimal: [16, 'hex']
  }
});

/***/ }),
/* 162 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


var common = __webpack_require__(41);

var Type = __webpack_require__(15);

var YAML_FLOAT_PATTERN = new RegExp( // 2.5e4, 2.5 and integers
'^(?:[-+]?(?:0|[1-9][0-9_]*)(?:\\.[0-9_]*)?(?:[eE][-+]?[0-9]+)?' + // .2e4, .2
// special case, seems not from spec
'|\\.[0-9_]+(?:[eE][-+]?[0-9]+)?' + // 20:59
'|[-+]?[0-9][0-9_]*(?::[0-5]?[0-9])+\\.[0-9_]*' + // .inf
'|[-+]?\\.(?:inf|Inf|INF)' + // .nan
'|\\.(?:nan|NaN|NAN))$');

function resolveYamlFloat(data) {
  if (data === null) return false;

  if (!YAML_FLOAT_PATTERN.test(data) || // Quick hack to not allow integers end with `_`
  // Probably should update regexp & check speed
  data[data.length - 1] === '_') {
    return false;
  }

  return true;
}

function constructYamlFloat(data) {
  var value, sign, base, digits;
  value = data.replace(/_/g, '').toLowerCase();
  sign = value[0] === '-' ? -1 : 1;
  digits = [];

  if ('+-'.indexOf(value[0]) >= 0) {
    value = value.slice(1);
  }

  if (value === '.inf') {
    return sign === 1 ? Number.POSITIVE_INFINITY : Number.NEGATIVE_INFINITY;
  } else if (value === '.nan') {
    return NaN;
  } else if (value.indexOf(':') >= 0) {
    value.split(':').forEach(function (v) {
      digits.unshift(parseFloat(v, 10));
    });
    value = 0.0;
    base = 1;
    digits.forEach(function (d) {
      value += d * base;
      base *= 60;
    });
    return sign * value;
  }

  return sign * parseFloat(value, 10);
}

var SCIENTIFIC_WITHOUT_DOT = /^[-+]?[0-9]+e/;

function representYamlFloat(object, style) {
  var res;

  if (isNaN(object)) {
    switch (style) {
      case 'lowercase':
        return '.nan';

      case 'uppercase':
        return '.NAN';

      case 'camelcase':
        return '.NaN';
    }
  } else if (Number.POSITIVE_INFINITY === object) {
    switch (style) {
      case 'lowercase':
        return '.inf';

      case 'uppercase':
        return '.INF';

      case 'camelcase':
        return '.Inf';
    }
  } else if (Number.NEGATIVE_INFINITY === object) {
    switch (style) {
      case 'lowercase':
        return '-.inf';

      case 'uppercase':
        return '-.INF';

      case 'camelcase':
        return '-.Inf';
    }
  } else if (common.isNegativeZero(object)) {
    return '-0.0';
  }

  res = object.toString(10); // JS stringifier can build scientific format without dots: 5e-100,
  // while YAML requres dot: 5.e-100. Fix it with simple hack

  return SCIENTIFIC_WITHOUT_DOT.test(res) ? res.replace('e', '.e') : res;
}

function isFloat(object) {
  return Object.prototype.toString.call(object) === '[object Number]' && (object % 1 !== 0 || common.isNegativeZero(object));
}

module.exports = new Type('tag:yaml.org,2002:float', {
  kind: 'scalar',
  resolve: resolveYamlFloat,
  construct: constructYamlFloat,
  predicate: isFloat,
  represent: representYamlFloat,
  defaultStyle: 'lowercase'
});

/***/ }),
/* 163 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


var Type = __webpack_require__(15);

var YAML_DATE_REGEXP = new RegExp('^([0-9][0-9][0-9][0-9])' + // [1] year
'-([0-9][0-9])' + // [2] month
'-([0-9][0-9])$'); // [3] day

var YAML_TIMESTAMP_REGEXP = new RegExp('^([0-9][0-9][0-9][0-9])' + // [1] year
'-([0-9][0-9]?)' + // [2] month
'-([0-9][0-9]?)' + // [3] day
'(?:[Tt]|[ \\t]+)' + // ...
'([0-9][0-9]?)' + // [4] hour
':([0-9][0-9])' + // [5] minute
':([0-9][0-9])' + // [6] second
'(?:\\.([0-9]*))?' + // [7] fraction
'(?:[ \\t]*(Z|([-+])([0-9][0-9]?)' + // [8] tz [9] tz_sign [10] tz_hour
'(?::([0-9][0-9]))?))?$'); // [11] tz_minute

function resolveYamlTimestamp(data) {
  if (data === null) return false;
  if (YAML_DATE_REGEXP.exec(data) !== null) return true;
  if (YAML_TIMESTAMP_REGEXP.exec(data) !== null) return true;
  return false;
}

function constructYamlTimestamp(data) {
  var match,
      year,
      month,
      day,
      hour,
      minute,
      second,
      fraction = 0,
      delta = null,
      tz_hour,
      tz_minute,
      date;
  match = YAML_DATE_REGEXP.exec(data);
  if (match === null) match = YAML_TIMESTAMP_REGEXP.exec(data);
  if (match === null) throw new Error('Date resolve error'); // match: [1] year [2] month [3] day

  year = +match[1];
  month = +match[2] - 1; // JS month starts with 0

  day = +match[3];

  if (!match[4]) {
    // no hour
    return new Date(Date.UTC(year, month, day));
  } // match: [4] hour [5] minute [6] second [7] fraction


  hour = +match[4];
  minute = +match[5];
  second = +match[6];

  if (match[7]) {
    fraction = match[7].slice(0, 3);

    while (fraction.length < 3) {
      // milli-seconds
      fraction += '0';
    }

    fraction = +fraction;
  } // match: [8] tz [9] tz_sign [10] tz_hour [11] tz_minute


  if (match[9]) {
    tz_hour = +match[10];
    tz_minute = +(match[11] || 0);
    delta = (tz_hour * 60 + tz_minute) * 60000; // delta in mili-seconds

    if (match[9] === '-') delta = -delta;
  }

  date = new Date(Date.UTC(year, month, day, hour, minute, second, fraction));
  if (delta) date.setTime(date.getTime() - delta);
  return date;
}

function representYamlTimestamp(object
/*, style*/
) {
  return object.toISOString();
}

module.exports = new Type('tag:yaml.org,2002:timestamp', {
  kind: 'scalar',
  resolve: resolveYamlTimestamp,
  construct: constructYamlTimestamp,
  instanceOf: Date,
  represent: representYamlTimestamp
});

/***/ }),
/* 164 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


var Type = __webpack_require__(15);

function resolveYamlMerge(data) {
  return data === '<<' || data === null;
}

module.exports = new Type('tag:yaml.org,2002:merge', {
  kind: 'scalar',
  resolve: resolveYamlMerge
});

/***/ }),
/* 165 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";
var require;
/*eslint-disable no-bitwise*/

var NodeBuffer;

try {
  // A trick for browserified version, to not include `Buffer` shim
  var _require = require;
  NodeBuffer = __webpack_require__(166).Buffer;
} catch (__) {}

var Type = __webpack_require__(15); // [ 64, 65, 66 ] -> [ padding, CR, LF ]


var BASE64_MAP = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=\n\r';

function resolveYamlBinary(data) {
  if (data === null) return false;
  var code,
      idx,
      bitlen = 0,
      max = data.length,
      map = BASE64_MAP; // Convert one by one.

  for (idx = 0; idx < max; idx++) {
    code = map.indexOf(data.charAt(idx)); // Skip CR/LF

    if (code > 64) continue; // Fail on illegal characters

    if (code < 0) return false;
    bitlen += 6;
  } // If there are any bits left, source was corrupted


  return bitlen % 8 === 0;
}

function constructYamlBinary(data) {
  var idx,
      tailbits,
      input = data.replace(/[\r\n=]/g, ''),
      // remove CR/LF & padding to simplify scan
  max = input.length,
      map = BASE64_MAP,
      bits = 0,
      result = []; // Collect by 6*4 bits (3 bytes)

  for (idx = 0; idx < max; idx++) {
    if (idx % 4 === 0 && idx) {
      result.push(bits >> 16 & 0xFF);
      result.push(bits >> 8 & 0xFF);
      result.push(bits & 0xFF);
    }

    bits = bits << 6 | map.indexOf(input.charAt(idx));
  } // Dump tail


  tailbits = max % 4 * 6;

  if (tailbits === 0) {
    result.push(bits >> 16 & 0xFF);
    result.push(bits >> 8 & 0xFF);
    result.push(bits & 0xFF);
  } else if (tailbits === 18) {
    result.push(bits >> 10 & 0xFF);
    result.push(bits >> 2 & 0xFF);
  } else if (tailbits === 12) {
    result.push(bits >> 4 & 0xFF);
  } // Wrap into Buffer for NodeJS and leave Array for browser


  if (NodeBuffer) {
    // Support node 6.+ Buffer API when available
    return NodeBuffer.from ? NodeBuffer.from(result) : new NodeBuffer(result);
  }

  return result;
}

function representYamlBinary(object
/*, style*/
) {
  var result = '',
      bits = 0,
      idx,
      tail,
      max = object.length,
      map = BASE64_MAP; // Convert every three bytes to 4 ASCII characters.

  for (idx = 0; idx < max; idx++) {
    if (idx % 3 === 0 && idx) {
      result += map[bits >> 18 & 0x3F];
      result += map[bits >> 12 & 0x3F];
      result += map[bits >> 6 & 0x3F];
      result += map[bits & 0x3F];
    }

    bits = (bits << 8) + object[idx];
  } // Dump tail


  tail = max % 3;

  if (tail === 0) {
    result += map[bits >> 18 & 0x3F];
    result += map[bits >> 12 & 0x3F];
    result += map[bits >> 6 & 0x3F];
    result += map[bits & 0x3F];
  } else if (tail === 2) {
    result += map[bits >> 10 & 0x3F];
    result += map[bits >> 4 & 0x3F];
    result += map[bits << 2 & 0x3F];
    result += map[64];
  } else if (tail === 1) {
    result += map[bits >> 2 & 0x3F];
    result += map[bits << 4 & 0x3F];
    result += map[64];
    result += map[64];
  }

  return result;
}

function isBinary(object) {
  return NodeBuffer && NodeBuffer.isBuffer(object);
}

module.exports = new Type('tag:yaml.org,2002:binary', {
  kind: 'scalar',
  resolve: resolveYamlBinary,
  construct: constructYamlBinary,
  predicate: isBinary,
  represent: representYamlBinary
});

/***/ }),
/* 166 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";
/* WEBPACK VAR INJECTION */(function(global) {/*!
 * The buffer module from node.js, for the browser.
 *
 * @author   Feross Aboukhadijeh <feross@feross.org> <http://feross.org>
 * @license  MIT
 */

/* eslint-disable no-proto */


var base64 = __webpack_require__(168);

var ieee754 = __webpack_require__(169);

var isArray = __webpack_require__(170);

exports.Buffer = Buffer;
exports.SlowBuffer = SlowBuffer;
exports.INSPECT_MAX_BYTES = 50;
/**
 * If `Buffer.TYPED_ARRAY_SUPPORT`:
 *   === true    Use Uint8Array implementation (fastest)
 *   === false   Use Object implementation (most compatible, even IE6)
 *
 * Browsers that support typed arrays are IE 10+, Firefox 4+, Chrome 7+, Safari 5.1+,
 * Opera 11.6+, iOS 4.2+.
 *
 * Due to various browser bugs, sometimes the Object implementation will be used even
 * when the browser supports typed arrays.
 *
 * Note:
 *
 *   - Firefox 4-29 lacks support for adding new properties to `Uint8Array` instances,
 *     See: https://bugzilla.mozilla.org/show_bug.cgi?id=695438.
 *
 *   - Chrome 9-10 is missing the `TypedArray.prototype.subarray` function.
 *
 *   - IE10 has a broken `TypedArray.prototype.subarray` function which returns arrays of
 *     incorrect length in some situations.

 * We detect these buggy browsers and set `Buffer.TYPED_ARRAY_SUPPORT` to `false` so they
 * get the Object implementation, which is slower but behaves correctly.
 */

Buffer.TYPED_ARRAY_SUPPORT = global.TYPED_ARRAY_SUPPORT !== undefined ? global.TYPED_ARRAY_SUPPORT : typedArraySupport();
/*
 * Export kMaxLength after typed array support is determined.
 */

exports.kMaxLength = kMaxLength();

function typedArraySupport() {
  try {
    var arr = new Uint8Array(1);
    arr.__proto__ = {
      __proto__: Uint8Array.prototype,
      foo: function foo() {
        return 42;
      }
    };
    return arr.foo() === 42 && // typed array instances can be augmented
    typeof arr.subarray === 'function' && // chrome 9-10 lack `subarray`
    arr.subarray(1, 1).byteLength === 0; // ie10 has broken `subarray`
  } catch (e) {
    return false;
  }
}

function kMaxLength() {
  return Buffer.TYPED_ARRAY_SUPPORT ? 0x7fffffff : 0x3fffffff;
}

function createBuffer(that, length) {
  if (kMaxLength() < length) {
    throw new RangeError('Invalid typed array length');
  }

  if (Buffer.TYPED_ARRAY_SUPPORT) {
    // Return an augmented `Uint8Array` instance, for best performance
    that = new Uint8Array(length);
    that.__proto__ = Buffer.prototype;
  } else {
    // Fallback: Return an object instance of the Buffer class
    if (that === null) {
      that = new Buffer(length);
    }

    that.length = length;
  }

  return that;
}
/**
 * The Buffer constructor returns instances of `Uint8Array` that have their
 * prototype changed to `Buffer.prototype`. Furthermore, `Buffer` is a subclass of
 * `Uint8Array`, so the returned instances will have all the node `Buffer` methods
 * and the `Uint8Array` methods. Square bracket notation works as expected -- it
 * returns a single octet.
 *
 * The `Uint8Array` prototype remains unmodified.
 */


function Buffer(arg, encodingOrOffset, length) {
  if (!Buffer.TYPED_ARRAY_SUPPORT && !(this instanceof Buffer)) {
    return new Buffer(arg, encodingOrOffset, length);
  } // Common case.


  if (typeof arg === 'number') {
    if (typeof encodingOrOffset === 'string') {
      throw new Error('If encoding is specified then the first argument must be a string');
    }

    return allocUnsafe(this, arg);
  }

  return from(this, arg, encodingOrOffset, length);
}

Buffer.poolSize = 8192; // not used by this implementation
// TODO: Legacy, not needed anymore. Remove in next major version.

Buffer._augment = function (arr) {
  arr.__proto__ = Buffer.prototype;
  return arr;
};

function from(that, value, encodingOrOffset, length) {
  if (typeof value === 'number') {
    throw new TypeError('"value" argument must not be a number');
  }

  if (typeof ArrayBuffer !== 'undefined' && value instanceof ArrayBuffer) {
    return fromArrayBuffer(that, value, encodingOrOffset, length);
  }

  if (typeof value === 'string') {
    return fromString(that, value, encodingOrOffset);
  }

  return fromObject(that, value);
}
/**
 * Functionally equivalent to Buffer(arg, encoding) but throws a TypeError
 * if value is a number.
 * Buffer.from(str[, encoding])
 * Buffer.from(array)
 * Buffer.from(buffer)
 * Buffer.from(arrayBuffer[, byteOffset[, length]])
 **/


Buffer.from = function (value, encodingOrOffset, length) {
  return from(null, value, encodingOrOffset, length);
};

if (Buffer.TYPED_ARRAY_SUPPORT) {
  Buffer.prototype.__proto__ = Uint8Array.prototype;
  Buffer.__proto__ = Uint8Array;

  if (typeof Symbol !== 'undefined' && Symbol.species && Buffer[Symbol.species] === Buffer) {
    // Fix subarray() in ES2016. See: https://github.com/feross/buffer/pull/97
    Object.defineProperty(Buffer, Symbol.species, {
      value: null,
      configurable: true
    });
  }
}

function assertSize(size) {
  if (typeof size !== 'number') {
    throw new TypeError('"size" argument must be a number');
  } else if (size < 0) {
    throw new RangeError('"size" argument must not be negative');
  }
}

function alloc(that, size, fill, encoding) {
  assertSize(size);

  if (size <= 0) {
    return createBuffer(that, size);
  }

  if (fill !== undefined) {
    // Only pay attention to encoding if it's a string. This
    // prevents accidentally sending in a number that would
    // be interpretted as a start offset.
    return typeof encoding === 'string' ? createBuffer(that, size).fill(fill, encoding) : createBuffer(that, size).fill(fill);
  }

  return createBuffer(that, size);
}
/**
 * Creates a new filled Buffer instance.
 * alloc(size[, fill[, encoding]])
 **/


Buffer.alloc = function (size, fill, encoding) {
  return alloc(null, size, fill, encoding);
};

function allocUnsafe(that, size) {
  assertSize(size);
  that = createBuffer(that, size < 0 ? 0 : checked(size) | 0);

  if (!Buffer.TYPED_ARRAY_SUPPORT) {
    for (var i = 0; i < size; ++i) {
      that[i] = 0;
    }
  }

  return that;
}
/**
 * Equivalent to Buffer(num), by default creates a non-zero-filled Buffer instance.
 * */


Buffer.allocUnsafe = function (size) {
  return allocUnsafe(null, size);
};
/**
 * Equivalent to SlowBuffer(num), by default creates a non-zero-filled Buffer instance.
 */


Buffer.allocUnsafeSlow = function (size) {
  return allocUnsafe(null, size);
};

function fromString(that, string, encoding) {
  if (typeof encoding !== 'string' || encoding === '') {
    encoding = 'utf8';
  }

  if (!Buffer.isEncoding(encoding)) {
    throw new TypeError('"encoding" must be a valid string encoding');
  }

  var length = byteLength(string, encoding) | 0;
  that = createBuffer(that, length);
  var actual = that.write(string, encoding);

  if (actual !== length) {
    // Writing a hex string, for example, that contains invalid characters will
    // cause everything after the first invalid character to be ignored. (e.g.
    // 'abxxcd' will be treated as 'ab')
    that = that.slice(0, actual);
  }

  return that;
}

function fromArrayLike(that, array) {
  var length = array.length < 0 ? 0 : checked(array.length) | 0;
  that = createBuffer(that, length);

  for (var i = 0; i < length; i += 1) {
    that[i] = array[i] & 255;
  }

  return that;
}

function fromArrayBuffer(that, array, byteOffset, length) {
  array.byteLength; // this throws if `array` is not a valid ArrayBuffer

  if (byteOffset < 0 || array.byteLength < byteOffset) {
    throw new RangeError('\'offset\' is out of bounds');
  }

  if (array.byteLength < byteOffset + (length || 0)) {
    throw new RangeError('\'length\' is out of bounds');
  }

  if (byteOffset === undefined && length === undefined) {
    array = new Uint8Array(array);
  } else if (length === undefined) {
    array = new Uint8Array(array, byteOffset);
  } else {
    array = new Uint8Array(array, byteOffset, length);
  }

  if (Buffer.TYPED_ARRAY_SUPPORT) {
    // Return an augmented `Uint8Array` instance, for best performance
    that = array;
    that.__proto__ = Buffer.prototype;
  } else {
    // Fallback: Return an object instance of the Buffer class
    that = fromArrayLike(that, array);
  }

  return that;
}

function fromObject(that, obj) {
  if (Buffer.isBuffer(obj)) {
    var len = checked(obj.length) | 0;
    that = createBuffer(that, len);

    if (that.length === 0) {
      return that;
    }

    obj.copy(that, 0, 0, len);
    return that;
  }

  if (obj) {
    if (typeof ArrayBuffer !== 'undefined' && obj.buffer instanceof ArrayBuffer || 'length' in obj) {
      if (typeof obj.length !== 'number' || isnan(obj.length)) {
        return createBuffer(that, 0);
      }

      return fromArrayLike(that, obj);
    }

    if (obj.type === 'Buffer' && isArray(obj.data)) {
      return fromArrayLike(that, obj.data);
    }
  }

  throw new TypeError('First argument must be a string, Buffer, ArrayBuffer, Array, or array-like object.');
}

function checked(length) {
  // Note: cannot use `length < kMaxLength()` here because that fails when
  // length is NaN (which is otherwise coerced to zero.)
  if (length >= kMaxLength()) {
    throw new RangeError('Attempt to allocate Buffer larger than maximum ' + 'size: 0x' + kMaxLength().toString(16) + ' bytes');
  }

  return length | 0;
}

function SlowBuffer(length) {
  if (+length != length) {
    // eslint-disable-line eqeqeq
    length = 0;
  }

  return Buffer.alloc(+length);
}

Buffer.isBuffer = function isBuffer(b) {
  return !!(b != null && b._isBuffer);
};

Buffer.compare = function compare(a, b) {
  if (!Buffer.isBuffer(a) || !Buffer.isBuffer(b)) {
    throw new TypeError('Arguments must be Buffers');
  }

  if (a === b) return 0;
  var x = a.length;
  var y = b.length;

  for (var i = 0, len = Math.min(x, y); i < len; ++i) {
    if (a[i] !== b[i]) {
      x = a[i];
      y = b[i];
      break;
    }
  }

  if (x < y) return -1;
  if (y < x) return 1;
  return 0;
};

Buffer.isEncoding = function isEncoding(encoding) {
  switch (String(encoding).toLowerCase()) {
    case 'hex':
    case 'utf8':
    case 'utf-8':
    case 'ascii':
    case 'latin1':
    case 'binary':
    case 'base64':
    case 'ucs2':
    case 'ucs-2':
    case 'utf16le':
    case 'utf-16le':
      return true;

    default:
      return false;
  }
};

Buffer.concat = function concat(list, length) {
  if (!isArray(list)) {
    throw new TypeError('"list" argument must be an Array of Buffers');
  }

  if (list.length === 0) {
    return Buffer.alloc(0);
  }

  var i;

  if (length === undefined) {
    length = 0;

    for (i = 0; i < list.length; ++i) {
      length += list[i].length;
    }
  }

  var buffer = Buffer.allocUnsafe(length);
  var pos = 0;

  for (i = 0; i < list.length; ++i) {
    var buf = list[i];

    if (!Buffer.isBuffer(buf)) {
      throw new TypeError('"list" argument must be an Array of Buffers');
    }

    buf.copy(buffer, pos);
    pos += buf.length;
  }

  return buffer;
};

function byteLength(string, encoding) {
  if (Buffer.isBuffer(string)) {
    return string.length;
  }

  if (typeof ArrayBuffer !== 'undefined' && typeof ArrayBuffer.isView === 'function' && (ArrayBuffer.isView(string) || string instanceof ArrayBuffer)) {
    return string.byteLength;
  }

  if (typeof string !== 'string') {
    string = '' + string;
  }

  var len = string.length;
  if (len === 0) return 0; // Use a for loop to avoid recursion

  var loweredCase = false;

  for (;;) {
    switch (encoding) {
      case 'ascii':
      case 'latin1':
      case 'binary':
        return len;

      case 'utf8':
      case 'utf-8':
      case undefined:
        return utf8ToBytes(string).length;

      case 'ucs2':
      case 'ucs-2':
      case 'utf16le':
      case 'utf-16le':
        return len * 2;

      case 'hex':
        return len >>> 1;

      case 'base64':
        return base64ToBytes(string).length;

      default:
        if (loweredCase) return utf8ToBytes(string).length; // assume utf8

        encoding = ('' + encoding).toLowerCase();
        loweredCase = true;
    }
  }
}

Buffer.byteLength = byteLength;

function slowToString(encoding, start, end) {
  var loweredCase = false; // No need to verify that "this.length <= MAX_UINT32" since it's a read-only
  // property of a typed array.
  // This behaves neither like String nor Uint8Array in that we set start/end
  // to their upper/lower bounds if the value passed is out of range.
  // undefined is handled specially as per ECMA-262 6th Edition,
  // Section 13.3.3.7 Runtime Semantics: KeyedBindingInitialization.

  if (start === undefined || start < 0) {
    start = 0;
  } // Return early if start > this.length. Done here to prevent potential uint32
  // coercion fail below.


  if (start > this.length) {
    return '';
  }

  if (end === undefined || end > this.length) {
    end = this.length;
  }

  if (end <= 0) {
    return '';
  } // Force coersion to uint32. This will also coerce falsey/NaN values to 0.


  end >>>= 0;
  start >>>= 0;

  if (end <= start) {
    return '';
  }

  if (!encoding) encoding = 'utf8';

  while (true) {
    switch (encoding) {
      case 'hex':
        return hexSlice(this, start, end);

      case 'utf8':
      case 'utf-8':
        return utf8Slice(this, start, end);

      case 'ascii':
        return asciiSlice(this, start, end);

      case 'latin1':
      case 'binary':
        return latin1Slice(this, start, end);

      case 'base64':
        return base64Slice(this, start, end);

      case 'ucs2':
      case 'ucs-2':
      case 'utf16le':
      case 'utf-16le':
        return utf16leSlice(this, start, end);

      default:
        if (loweredCase) throw new TypeError('Unknown encoding: ' + encoding);
        encoding = (encoding + '').toLowerCase();
        loweredCase = true;
    }
  }
} // The property is used by `Buffer.isBuffer` and `is-buffer` (in Safari 5-7) to detect
// Buffer instances.


Buffer.prototype._isBuffer = true;

function swap(b, n, m) {
  var i = b[n];
  b[n] = b[m];
  b[m] = i;
}

Buffer.prototype.swap16 = function swap16() {
  var len = this.length;

  if (len % 2 !== 0) {
    throw new RangeError('Buffer size must be a multiple of 16-bits');
  }

  for (var i = 0; i < len; i += 2) {
    swap(this, i, i + 1);
  }

  return this;
};

Buffer.prototype.swap32 = function swap32() {
  var len = this.length;

  if (len % 4 !== 0) {
    throw new RangeError('Buffer size must be a multiple of 32-bits');
  }

  for (var i = 0; i < len; i += 4) {
    swap(this, i, i + 3);
    swap(this, i + 1, i + 2);
  }

  return this;
};

Buffer.prototype.swap64 = function swap64() {
  var len = this.length;

  if (len % 8 !== 0) {
    throw new RangeError('Buffer size must be a multiple of 64-bits');
  }

  for (var i = 0; i < len; i += 8) {
    swap(this, i, i + 7);
    swap(this, i + 1, i + 6);
    swap(this, i + 2, i + 5);
    swap(this, i + 3, i + 4);
  }

  return this;
};

Buffer.prototype.toString = function toString() {
  var length = this.length | 0;
  if (length === 0) return '';
  if (arguments.length === 0) return utf8Slice(this, 0, length);
  return slowToString.apply(this, arguments);
};

Buffer.prototype.equals = function equals(b) {
  if (!Buffer.isBuffer(b)) throw new TypeError('Argument must be a Buffer');
  if (this === b) return true;
  return Buffer.compare(this, b) === 0;
};

Buffer.prototype.inspect = function inspect() {
  var str = '';
  var max = exports.INSPECT_MAX_BYTES;

  if (this.length > 0) {
    str = this.toString('hex', 0, max).match(/.{2}/g).join(' ');
    if (this.length > max) str += ' ... ';
  }

  return '<Buffer ' + str + '>';
};

Buffer.prototype.compare = function compare(target, start, end, thisStart, thisEnd) {
  if (!Buffer.isBuffer(target)) {
    throw new TypeError('Argument must be a Buffer');
  }

  if (start === undefined) {
    start = 0;
  }

  if (end === undefined) {
    end = target ? target.length : 0;
  }

  if (thisStart === undefined) {
    thisStart = 0;
  }

  if (thisEnd === undefined) {
    thisEnd = this.length;
  }

  if (start < 0 || end > target.length || thisStart < 0 || thisEnd > this.length) {
    throw new RangeError('out of range index');
  }

  if (thisStart >= thisEnd && start >= end) {
    return 0;
  }

  if (thisStart >= thisEnd) {
    return -1;
  }

  if (start >= end) {
    return 1;
  }

  start >>>= 0;
  end >>>= 0;
  thisStart >>>= 0;
  thisEnd >>>= 0;
  if (this === target) return 0;
  var x = thisEnd - thisStart;
  var y = end - start;
  var len = Math.min(x, y);
  var thisCopy = this.slice(thisStart, thisEnd);
  var targetCopy = target.slice(start, end);

  for (var i = 0; i < len; ++i) {
    if (thisCopy[i] !== targetCopy[i]) {
      x = thisCopy[i];
      y = targetCopy[i];
      break;
    }
  }

  if (x < y) return -1;
  if (y < x) return 1;
  return 0;
}; // Finds either the first index of `val` in `buffer` at offset >= `byteOffset`,
// OR the last index of `val` in `buffer` at offset <= `byteOffset`.
//
// Arguments:
// - buffer - a Buffer to search
// - val - a string, Buffer, or number
// - byteOffset - an index into `buffer`; will be clamped to an int32
// - encoding - an optional encoding, relevant is val is a string
// - dir - true for indexOf, false for lastIndexOf


function bidirectionalIndexOf(buffer, val, byteOffset, encoding, dir) {
  // Empty buffer means no match
  if (buffer.length === 0) return -1; // Normalize byteOffset

  if (typeof byteOffset === 'string') {
    encoding = byteOffset;
    byteOffset = 0;
  } else if (byteOffset > 0x7fffffff) {
    byteOffset = 0x7fffffff;
  } else if (byteOffset < -0x80000000) {
    byteOffset = -0x80000000;
  }

  byteOffset = +byteOffset; // Coerce to Number.

  if (isNaN(byteOffset)) {
    // byteOffset: it it's undefined, null, NaN, "foo", etc, search whole buffer
    byteOffset = dir ? 0 : buffer.length - 1;
  } // Normalize byteOffset: negative offsets start from the end of the buffer


  if (byteOffset < 0) byteOffset = buffer.length + byteOffset;

  if (byteOffset >= buffer.length) {
    if (dir) return -1;else byteOffset = buffer.length - 1;
  } else if (byteOffset < 0) {
    if (dir) byteOffset = 0;else return -1;
  } // Normalize val


  if (typeof val === 'string') {
    val = Buffer.from(val, encoding);
  } // Finally, search either indexOf (if dir is true) or lastIndexOf


  if (Buffer.isBuffer(val)) {
    // Special case: looking for empty string/buffer always fails
    if (val.length === 0) {
      return -1;
    }

    return arrayIndexOf(buffer, val, byteOffset, encoding, dir);
  } else if (typeof val === 'number') {
    val = val & 0xFF; // Search for a byte value [0-255]

    if (Buffer.TYPED_ARRAY_SUPPORT && typeof Uint8Array.prototype.indexOf === 'function') {
      if (dir) {
        return Uint8Array.prototype.indexOf.call(buffer, val, byteOffset);
      } else {
        return Uint8Array.prototype.lastIndexOf.call(buffer, val, byteOffset);
      }
    }

    return arrayIndexOf(buffer, [val], byteOffset, encoding, dir);
  }

  throw new TypeError('val must be string, number or Buffer');
}

function arrayIndexOf(arr, val, byteOffset, encoding, dir) {
  var indexSize = 1;
  var arrLength = arr.length;
  var valLength = val.length;

  if (encoding !== undefined) {
    encoding = String(encoding).toLowerCase();

    if (encoding === 'ucs2' || encoding === 'ucs-2' || encoding === 'utf16le' || encoding === 'utf-16le') {
      if (arr.length < 2 || val.length < 2) {
        return -1;
      }

      indexSize = 2;
      arrLength /= 2;
      valLength /= 2;
      byteOffset /= 2;
    }
  }

  function read(buf, i) {
    if (indexSize === 1) {
      return buf[i];
    } else {
      return buf.readUInt16BE(i * indexSize);
    }
  }

  var i;

  if (dir) {
    var foundIndex = -1;

    for (i = byteOffset; i < arrLength; i++) {
      if (read(arr, i) === read(val, foundIndex === -1 ? 0 : i - foundIndex)) {
        if (foundIndex === -1) foundIndex = i;
        if (i - foundIndex + 1 === valLength) return foundIndex * indexSize;
      } else {
        if (foundIndex !== -1) i -= i - foundIndex;
        foundIndex = -1;
      }
    }
  } else {
    if (byteOffset + valLength > arrLength) byteOffset = arrLength - valLength;

    for (i = byteOffset; i >= 0; i--) {
      var found = true;

      for (var j = 0; j < valLength; j++) {
        if (read(arr, i + j) !== read(val, j)) {
          found = false;
          break;
        }
      }

      if (found) return i;
    }
  }

  return -1;
}

Buffer.prototype.includes = function includes(val, byteOffset, encoding) {
  return this.indexOf(val, byteOffset, encoding) !== -1;
};

Buffer.prototype.indexOf = function indexOf(val, byteOffset, encoding) {
  return bidirectionalIndexOf(this, val, byteOffset, encoding, true);
};

Buffer.prototype.lastIndexOf = function lastIndexOf(val, byteOffset, encoding) {
  return bidirectionalIndexOf(this, val, byteOffset, encoding, false);
};

function hexWrite(buf, string, offset, length) {
  offset = Number(offset) || 0;
  var remaining = buf.length - offset;

  if (!length) {
    length = remaining;
  } else {
    length = Number(length);

    if (length > remaining) {
      length = remaining;
    }
  } // must be an even number of digits


  var strLen = string.length;
  if (strLen % 2 !== 0) throw new TypeError('Invalid hex string');

  if (length > strLen / 2) {
    length = strLen / 2;
  }

  for (var i = 0; i < length; ++i) {
    var parsed = parseInt(string.substr(i * 2, 2), 16);
    if (isNaN(parsed)) return i;
    buf[offset + i] = parsed;
  }

  return i;
}

function utf8Write(buf, string, offset, length) {
  return blitBuffer(utf8ToBytes(string, buf.length - offset), buf, offset, length);
}

function asciiWrite(buf, string, offset, length) {
  return blitBuffer(asciiToBytes(string), buf, offset, length);
}

function latin1Write(buf, string, offset, length) {
  return asciiWrite(buf, string, offset, length);
}

function base64Write(buf, string, offset, length) {
  return blitBuffer(base64ToBytes(string), buf, offset, length);
}

function ucs2Write(buf, string, offset, length) {
  return blitBuffer(utf16leToBytes(string, buf.length - offset), buf, offset, length);
}

Buffer.prototype.write = function write(string, offset, length, encoding) {
  // Buffer#write(string)
  if (offset === undefined) {
    encoding = 'utf8';
    length = this.length;
    offset = 0; // Buffer#write(string, encoding)
  } else if (length === undefined && typeof offset === 'string') {
    encoding = offset;
    length = this.length;
    offset = 0; // Buffer#write(string, offset[, length][, encoding])
  } else if (isFinite(offset)) {
    offset = offset | 0;

    if (isFinite(length)) {
      length = length | 0;
      if (encoding === undefined) encoding = 'utf8';
    } else {
      encoding = length;
      length = undefined;
    } // legacy write(string, encoding, offset, length) - remove in v0.13

  } else {
    throw new Error('Buffer.write(string, encoding, offset[, length]) is no longer supported');
  }

  var remaining = this.length - offset;
  if (length === undefined || length > remaining) length = remaining;

  if (string.length > 0 && (length < 0 || offset < 0) || offset > this.length) {
    throw new RangeError('Attempt to write outside buffer bounds');
  }

  if (!encoding) encoding = 'utf8';
  var loweredCase = false;

  for (;;) {
    switch (encoding) {
      case 'hex':
        return hexWrite(this, string, offset, length);

      case 'utf8':
      case 'utf-8':
        return utf8Write(this, string, offset, length);

      case 'ascii':
        return asciiWrite(this, string, offset, length);

      case 'latin1':
      case 'binary':
        return latin1Write(this, string, offset, length);

      case 'base64':
        // Warning: maxLength not taken into account in base64Write
        return base64Write(this, string, offset, length);

      case 'ucs2':
      case 'ucs-2':
      case 'utf16le':
      case 'utf-16le':
        return ucs2Write(this, string, offset, length);

      default:
        if (loweredCase) throw new TypeError('Unknown encoding: ' + encoding);
        encoding = ('' + encoding).toLowerCase();
        loweredCase = true;
    }
  }
};

Buffer.prototype.toJSON = function toJSON() {
  return {
    type: 'Buffer',
    data: Array.prototype.slice.call(this._arr || this, 0)
  };
};

function base64Slice(buf, start, end) {
  if (start === 0 && end === buf.length) {
    return base64.fromByteArray(buf);
  } else {
    return base64.fromByteArray(buf.slice(start, end));
  }
}

function utf8Slice(buf, start, end) {
  end = Math.min(buf.length, end);
  var res = [];
  var i = start;

  while (i < end) {
    var firstByte = buf[i];
    var codePoint = null;
    var bytesPerSequence = firstByte > 0xEF ? 4 : firstByte > 0xDF ? 3 : firstByte > 0xBF ? 2 : 1;

    if (i + bytesPerSequence <= end) {
      var secondByte, thirdByte, fourthByte, tempCodePoint;

      switch (bytesPerSequence) {
        case 1:
          if (firstByte < 0x80) {
            codePoint = firstByte;
          }

          break;

        case 2:
          secondByte = buf[i + 1];

          if ((secondByte & 0xC0) === 0x80) {
            tempCodePoint = (firstByte & 0x1F) << 0x6 | secondByte & 0x3F;

            if (tempCodePoint > 0x7F) {
              codePoint = tempCodePoint;
            }
          }

          break;

        case 3:
          secondByte = buf[i + 1];
          thirdByte = buf[i + 2];

          if ((secondByte & 0xC0) === 0x80 && (thirdByte & 0xC0) === 0x80) {
            tempCodePoint = (firstByte & 0xF) << 0xC | (secondByte & 0x3F) << 0x6 | thirdByte & 0x3F;

            if (tempCodePoint > 0x7FF && (tempCodePoint < 0xD800 || tempCodePoint > 0xDFFF)) {
              codePoint = tempCodePoint;
            }
          }

          break;

        case 4:
          secondByte = buf[i + 1];
          thirdByte = buf[i + 2];
          fourthByte = buf[i + 3];

          if ((secondByte & 0xC0) === 0x80 && (thirdByte & 0xC0) === 0x80 && (fourthByte & 0xC0) === 0x80) {
            tempCodePoint = (firstByte & 0xF) << 0x12 | (secondByte & 0x3F) << 0xC | (thirdByte & 0x3F) << 0x6 | fourthByte & 0x3F;

            if (tempCodePoint > 0xFFFF && tempCodePoint < 0x110000) {
              codePoint = tempCodePoint;
            }
          }

      }
    }

    if (codePoint === null) {
      // we did not generate a valid codePoint so insert a
      // replacement char (U+FFFD) and advance only 1 byte
      codePoint = 0xFFFD;
      bytesPerSequence = 1;
    } else if (codePoint > 0xFFFF) {
      // encode to utf16 (surrogate pair dance)
      codePoint -= 0x10000;
      res.push(codePoint >>> 10 & 0x3FF | 0xD800);
      codePoint = 0xDC00 | codePoint & 0x3FF;
    }

    res.push(codePoint);
    i += bytesPerSequence;
  }

  return decodeCodePointsArray(res);
} // Based on http://stackoverflow.com/a/22747272/680742, the browser with
// the lowest limit is Chrome, with 0x10000 args.
// We go 1 magnitude less, for safety


var MAX_ARGUMENTS_LENGTH = 0x1000;

function decodeCodePointsArray(codePoints) {
  var len = codePoints.length;

  if (len <= MAX_ARGUMENTS_LENGTH) {
    return String.fromCharCode.apply(String, codePoints); // avoid extra slice()
  } // Decode in chunks to avoid "call stack size exceeded".


  var res = '';
  var i = 0;

  while (i < len) {
    res += String.fromCharCode.apply(String, codePoints.slice(i, i += MAX_ARGUMENTS_LENGTH));
  }

  return res;
}

function asciiSlice(buf, start, end) {
  var ret = '';
  end = Math.min(buf.length, end);

  for (var i = start; i < end; ++i) {
    ret += String.fromCharCode(buf[i] & 0x7F);
  }

  return ret;
}

function latin1Slice(buf, start, end) {
  var ret = '';
  end = Math.min(buf.length, end);

  for (var i = start; i < end; ++i) {
    ret += String.fromCharCode(buf[i]);
  }

  return ret;
}

function hexSlice(buf, start, end) {
  var len = buf.length;
  if (!start || start < 0) start = 0;
  if (!end || end < 0 || end > len) end = len;
  var out = '';

  for (var i = start; i < end; ++i) {
    out += toHex(buf[i]);
  }

  return out;
}

function utf16leSlice(buf, start, end) {
  var bytes = buf.slice(start, end);
  var res = '';

  for (var i = 0; i < bytes.length; i += 2) {
    res += String.fromCharCode(bytes[i] + bytes[i + 1] * 256);
  }

  return res;
}

Buffer.prototype.slice = function slice(start, end) {
  var len = this.length;
  start = ~~start;
  end = end === undefined ? len : ~~end;

  if (start < 0) {
    start += len;
    if (start < 0) start = 0;
  } else if (start > len) {
    start = len;
  }

  if (end < 0) {
    end += len;
    if (end < 0) end = 0;
  } else if (end > len) {
    end = len;
  }

  if (end < start) end = start;
  var newBuf;

  if (Buffer.TYPED_ARRAY_SUPPORT) {
    newBuf = this.subarray(start, end);
    newBuf.__proto__ = Buffer.prototype;
  } else {
    var sliceLen = end - start;
    newBuf = new Buffer(sliceLen, undefined);

    for (var i = 0; i < sliceLen; ++i) {
      newBuf[i] = this[i + start];
    }
  }

  return newBuf;
};
/*
 * Need to make sure that buffer isn't trying to write out of bounds.
 */


function checkOffset(offset, ext, length) {
  if (offset % 1 !== 0 || offset < 0) throw new RangeError('offset is not uint');
  if (offset + ext > length) throw new RangeError('Trying to access beyond buffer length');
}

Buffer.prototype.readUIntLE = function readUIntLE(offset, byteLength, noAssert) {
  offset = offset | 0;
  byteLength = byteLength | 0;
  if (!noAssert) checkOffset(offset, byteLength, this.length);
  var val = this[offset];
  var mul = 1;
  var i = 0;

  while (++i < byteLength && (mul *= 0x100)) {
    val += this[offset + i] * mul;
  }

  return val;
};

Buffer.prototype.readUIntBE = function readUIntBE(offset, byteLength, noAssert) {
  offset = offset | 0;
  byteLength = byteLength | 0;

  if (!noAssert) {
    checkOffset(offset, byteLength, this.length);
  }

  var val = this[offset + --byteLength];
  var mul = 1;

  while (byteLength > 0 && (mul *= 0x100)) {
    val += this[offset + --byteLength] * mul;
  }

  return val;
};

Buffer.prototype.readUInt8 = function readUInt8(offset, noAssert) {
  if (!noAssert) checkOffset(offset, 1, this.length);
  return this[offset];
};

Buffer.prototype.readUInt16LE = function readUInt16LE(offset, noAssert) {
  if (!noAssert) checkOffset(offset, 2, this.length);
  return this[offset] | this[offset + 1] << 8;
};

Buffer.prototype.readUInt16BE = function readUInt16BE(offset, noAssert) {
  if (!noAssert) checkOffset(offset, 2, this.length);
  return this[offset] << 8 | this[offset + 1];
};

Buffer.prototype.readUInt32LE = function readUInt32LE(offset, noAssert) {
  if (!noAssert) checkOffset(offset, 4, this.length);
  return (this[offset] | this[offset + 1] << 8 | this[offset + 2] << 16) + this[offset + 3] * 0x1000000;
};

Buffer.prototype.readUInt32BE = function readUInt32BE(offset, noAssert) {
  if (!noAssert) checkOffset(offset, 4, this.length);
  return this[offset] * 0x1000000 + (this[offset + 1] << 16 | this[offset + 2] << 8 | this[offset + 3]);
};

Buffer.prototype.readIntLE = function readIntLE(offset, byteLength, noAssert) {
  offset = offset | 0;
  byteLength = byteLength | 0;
  if (!noAssert) checkOffset(offset, byteLength, this.length);
  var val = this[offset];
  var mul = 1;
  var i = 0;

  while (++i < byteLength && (mul *= 0x100)) {
    val += this[offset + i] * mul;
  }

  mul *= 0x80;
  if (val >= mul) val -= Math.pow(2, 8 * byteLength);
  return val;
};

Buffer.prototype.readIntBE = function readIntBE(offset, byteLength, noAssert) {
  offset = offset | 0;
  byteLength = byteLength | 0;
  if (!noAssert) checkOffset(offset, byteLength, this.length);
  var i = byteLength;
  var mul = 1;
  var val = this[offset + --i];

  while (i > 0 && (mul *= 0x100)) {
    val += this[offset + --i] * mul;
  }

  mul *= 0x80;
  if (val >= mul) val -= Math.pow(2, 8 * byteLength);
  return val;
};

Buffer.prototype.readInt8 = function readInt8(offset, noAssert) {
  if (!noAssert) checkOffset(offset, 1, this.length);
  if (!(this[offset] & 0x80)) return this[offset];
  return (0xff - this[offset] + 1) * -1;
};

Buffer.prototype.readInt16LE = function readInt16LE(offset, noAssert) {
  if (!noAssert) checkOffset(offset, 2, this.length);
  var val = this[offset] | this[offset + 1] << 8;
  return val & 0x8000 ? val | 0xFFFF0000 : val;
};

Buffer.prototype.readInt16BE = function readInt16BE(offset, noAssert) {
  if (!noAssert) checkOffset(offset, 2, this.length);
  var val = this[offset + 1] | this[offset] << 8;
  return val & 0x8000 ? val | 0xFFFF0000 : val;
};

Buffer.prototype.readInt32LE = function readInt32LE(offset, noAssert) {
  if (!noAssert) checkOffset(offset, 4, this.length);
  return this[offset] | this[offset + 1] << 8 | this[offset + 2] << 16 | this[offset + 3] << 24;
};

Buffer.prototype.readInt32BE = function readInt32BE(offset, noAssert) {
  if (!noAssert) checkOffset(offset, 4, this.length);
  return this[offset] << 24 | this[offset + 1] << 16 | this[offset + 2] << 8 | this[offset + 3];
};

Buffer.prototype.readFloatLE = function readFloatLE(offset, noAssert) {
  if (!noAssert) checkOffset(offset, 4, this.length);
  return ieee754.read(this, offset, true, 23, 4);
};

Buffer.prototype.readFloatBE = function readFloatBE(offset, noAssert) {
  if (!noAssert) checkOffset(offset, 4, this.length);
  return ieee754.read(this, offset, false, 23, 4);
};

Buffer.prototype.readDoubleLE = function readDoubleLE(offset, noAssert) {
  if (!noAssert) checkOffset(offset, 8, this.length);
  return ieee754.read(this, offset, true, 52, 8);
};

Buffer.prototype.readDoubleBE = function readDoubleBE(offset, noAssert) {
  if (!noAssert) checkOffset(offset, 8, this.length);
  return ieee754.read(this, offset, false, 52, 8);
};

function checkInt(buf, value, offset, ext, max, min) {
  if (!Buffer.isBuffer(buf)) throw new TypeError('"buffer" argument must be a Buffer instance');
  if (value > max || value < min) throw new RangeError('"value" argument is out of bounds');
  if (offset + ext > buf.length) throw new RangeError('Index out of range');
}

Buffer.prototype.writeUIntLE = function writeUIntLE(value, offset, byteLength, noAssert) {
  value = +value;
  offset = offset | 0;
  byteLength = byteLength | 0;

  if (!noAssert) {
    var maxBytes = Math.pow(2, 8 * byteLength) - 1;
    checkInt(this, value, offset, byteLength, maxBytes, 0);
  }

  var mul = 1;
  var i = 0;
  this[offset] = value & 0xFF;

  while (++i < byteLength && (mul *= 0x100)) {
    this[offset + i] = value / mul & 0xFF;
  }

  return offset + byteLength;
};

Buffer.prototype.writeUIntBE = function writeUIntBE(value, offset, byteLength, noAssert) {
  value = +value;
  offset = offset | 0;
  byteLength = byteLength | 0;

  if (!noAssert) {
    var maxBytes = Math.pow(2, 8 * byteLength) - 1;
    checkInt(this, value, offset, byteLength, maxBytes, 0);
  }

  var i = byteLength - 1;
  var mul = 1;
  this[offset + i] = value & 0xFF;

  while (--i >= 0 && (mul *= 0x100)) {
    this[offset + i] = value / mul & 0xFF;
  }

  return offset + byteLength;
};

Buffer.prototype.writeUInt8 = function writeUInt8(value, offset, noAssert) {
  value = +value;
  offset = offset | 0;
  if (!noAssert) checkInt(this, value, offset, 1, 0xff, 0);
  if (!Buffer.TYPED_ARRAY_SUPPORT) value = Math.floor(value);
  this[offset] = value & 0xff;
  return offset + 1;
};

function objectWriteUInt16(buf, value, offset, littleEndian) {
  if (value < 0) value = 0xffff + value + 1;

  for (var i = 0, j = Math.min(buf.length - offset, 2); i < j; ++i) {
    buf[offset + i] = (value & 0xff << 8 * (littleEndian ? i : 1 - i)) >>> (littleEndian ? i : 1 - i) * 8;
  }
}

Buffer.prototype.writeUInt16LE = function writeUInt16LE(value, offset, noAssert) {
  value = +value;
  offset = offset | 0;
  if (!noAssert) checkInt(this, value, offset, 2, 0xffff, 0);

  if (Buffer.TYPED_ARRAY_SUPPORT) {
    this[offset] = value & 0xff;
    this[offset + 1] = value >>> 8;
  } else {
    objectWriteUInt16(this, value, offset, true);
  }

  return offset + 2;
};

Buffer.prototype.writeUInt16BE = function writeUInt16BE(value, offset, noAssert) {
  value = +value;
  offset = offset | 0;
  if (!noAssert) checkInt(this, value, offset, 2, 0xffff, 0);

  if (Buffer.TYPED_ARRAY_SUPPORT) {
    this[offset] = value >>> 8;
    this[offset + 1] = value & 0xff;
  } else {
    objectWriteUInt16(this, value, offset, false);
  }

  return offset + 2;
};

function objectWriteUInt32(buf, value, offset, littleEndian) {
  if (value < 0) value = 0xffffffff + value + 1;

  for (var i = 0, j = Math.min(buf.length - offset, 4); i < j; ++i) {
    buf[offset + i] = value >>> (littleEndian ? i : 3 - i) * 8 & 0xff;
  }
}

Buffer.prototype.writeUInt32LE = function writeUInt32LE(value, offset, noAssert) {
  value = +value;
  offset = offset | 0;
  if (!noAssert) checkInt(this, value, offset, 4, 0xffffffff, 0);

  if (Buffer.TYPED_ARRAY_SUPPORT) {
    this[offset + 3] = value >>> 24;
    this[offset + 2] = value >>> 16;
    this[offset + 1] = value >>> 8;
    this[offset] = value & 0xff;
  } else {
    objectWriteUInt32(this, value, offset, true);
  }

  return offset + 4;
};

Buffer.prototype.writeUInt32BE = function writeUInt32BE(value, offset, noAssert) {
  value = +value;
  offset = offset | 0;
  if (!noAssert) checkInt(this, value, offset, 4, 0xffffffff, 0);

  if (Buffer.TYPED_ARRAY_SUPPORT) {
    this[offset] = value >>> 24;
    this[offset + 1] = value >>> 16;
    this[offset + 2] = value >>> 8;
    this[offset + 3] = value & 0xff;
  } else {
    objectWriteUInt32(this, value, offset, false);
  }

  return offset + 4;
};

Buffer.prototype.writeIntLE = function writeIntLE(value, offset, byteLength, noAssert) {
  value = +value;
  offset = offset | 0;

  if (!noAssert) {
    var limit = Math.pow(2, 8 * byteLength - 1);
    checkInt(this, value, offset, byteLength, limit - 1, -limit);
  }

  var i = 0;
  var mul = 1;
  var sub = 0;
  this[offset] = value & 0xFF;

  while (++i < byteLength && (mul *= 0x100)) {
    if (value < 0 && sub === 0 && this[offset + i - 1] !== 0) {
      sub = 1;
    }

    this[offset + i] = (value / mul >> 0) - sub & 0xFF;
  }

  return offset + byteLength;
};

Buffer.prototype.writeIntBE = function writeIntBE(value, offset, byteLength, noAssert) {
  value = +value;
  offset = offset | 0;

  if (!noAssert) {
    var limit = Math.pow(2, 8 * byteLength - 1);
    checkInt(this, value, offset, byteLength, limit - 1, -limit);
  }

  var i = byteLength - 1;
  var mul = 1;
  var sub = 0;
  this[offset + i] = value & 0xFF;

  while (--i >= 0 && (mul *= 0x100)) {
    if (value < 0 && sub === 0 && this[offset + i + 1] !== 0) {
      sub = 1;
    }

    this[offset + i] = (value / mul >> 0) - sub & 0xFF;
  }

  return offset + byteLength;
};

Buffer.prototype.writeInt8 = function writeInt8(value, offset, noAssert) {
  value = +value;
  offset = offset | 0;
  if (!noAssert) checkInt(this, value, offset, 1, 0x7f, -0x80);
  if (!Buffer.TYPED_ARRAY_SUPPORT) value = Math.floor(value);
  if (value < 0) value = 0xff + value + 1;
  this[offset] = value & 0xff;
  return offset + 1;
};

Buffer.prototype.writeInt16LE = function writeInt16LE(value, offset, noAssert) {
  value = +value;
  offset = offset | 0;
  if (!noAssert) checkInt(this, value, offset, 2, 0x7fff, -0x8000);

  if (Buffer.TYPED_ARRAY_SUPPORT) {
    this[offset] = value & 0xff;
    this[offset + 1] = value >>> 8;
  } else {
    objectWriteUInt16(this, value, offset, true);
  }

  return offset + 2;
};

Buffer.prototype.writeInt16BE = function writeInt16BE(value, offset, noAssert) {
  value = +value;
  offset = offset | 0;
  if (!noAssert) checkInt(this, value, offset, 2, 0x7fff, -0x8000);

  if (Buffer.TYPED_ARRAY_SUPPORT) {
    this[offset] = value >>> 8;
    this[offset + 1] = value & 0xff;
  } else {
    objectWriteUInt16(this, value, offset, false);
  }

  return offset + 2;
};

Buffer.prototype.writeInt32LE = function writeInt32LE(value, offset, noAssert) {
  value = +value;
  offset = offset | 0;
  if (!noAssert) checkInt(this, value, offset, 4, 0x7fffffff, -0x80000000);

  if (Buffer.TYPED_ARRAY_SUPPORT) {
    this[offset] = value & 0xff;
    this[offset + 1] = value >>> 8;
    this[offset + 2] = value >>> 16;
    this[offset + 3] = value >>> 24;
  } else {
    objectWriteUInt32(this, value, offset, true);
  }

  return offset + 4;
};

Buffer.prototype.writeInt32BE = function writeInt32BE(value, offset, noAssert) {
  value = +value;
  offset = offset | 0;
  if (!noAssert) checkInt(this, value, offset, 4, 0x7fffffff, -0x80000000);
  if (value < 0) value = 0xffffffff + value + 1;

  if (Buffer.TYPED_ARRAY_SUPPORT) {
    this[offset] = value >>> 24;
    this[offset + 1] = value >>> 16;
    this[offset + 2] = value >>> 8;
    this[offset + 3] = value & 0xff;
  } else {
    objectWriteUInt32(this, value, offset, false);
  }

  return offset + 4;
};

function checkIEEE754(buf, value, offset, ext, max, min) {
  if (offset + ext > buf.length) throw new RangeError('Index out of range');
  if (offset < 0) throw new RangeError('Index out of range');
}

function writeFloat(buf, value, offset, littleEndian, noAssert) {
  if (!noAssert) {
    checkIEEE754(buf, value, offset, 4, 3.4028234663852886e+38, -3.4028234663852886e+38);
  }

  ieee754.write(buf, value, offset, littleEndian, 23, 4);
  return offset + 4;
}

Buffer.prototype.writeFloatLE = function writeFloatLE(value, offset, noAssert) {
  return writeFloat(this, value, offset, true, noAssert);
};

Buffer.prototype.writeFloatBE = function writeFloatBE(value, offset, noAssert) {
  return writeFloat(this, value, offset, false, noAssert);
};

function writeDouble(buf, value, offset, littleEndian, noAssert) {
  if (!noAssert) {
    checkIEEE754(buf, value, offset, 8, 1.7976931348623157E+308, -1.7976931348623157E+308);
  }

  ieee754.write(buf, value, offset, littleEndian, 52, 8);
  return offset + 8;
}

Buffer.prototype.writeDoubleLE = function writeDoubleLE(value, offset, noAssert) {
  return writeDouble(this, value, offset, true, noAssert);
};

Buffer.prototype.writeDoubleBE = function writeDoubleBE(value, offset, noAssert) {
  return writeDouble(this, value, offset, false, noAssert);
}; // copy(targetBuffer, targetStart=0, sourceStart=0, sourceEnd=buffer.length)


Buffer.prototype.copy = function copy(target, targetStart, start, end) {
  if (!start) start = 0;
  if (!end && end !== 0) end = this.length;
  if (targetStart >= target.length) targetStart = target.length;
  if (!targetStart) targetStart = 0;
  if (end > 0 && end < start) end = start; // Copy 0 bytes; we're done

  if (end === start) return 0;
  if (target.length === 0 || this.length === 0) return 0; // Fatal error conditions

  if (targetStart < 0) {
    throw new RangeError('targetStart out of bounds');
  }

  if (start < 0 || start >= this.length) throw new RangeError('sourceStart out of bounds');
  if (end < 0) throw new RangeError('sourceEnd out of bounds'); // Are we oob?

  if (end > this.length) end = this.length;

  if (target.length - targetStart < end - start) {
    end = target.length - targetStart + start;
  }

  var len = end - start;
  var i;

  if (this === target && start < targetStart && targetStart < end) {
    // descending copy from end
    for (i = len - 1; i >= 0; --i) {
      target[i + targetStart] = this[i + start];
    }
  } else if (len < 1000 || !Buffer.TYPED_ARRAY_SUPPORT) {
    // ascending copy from start
    for (i = 0; i < len; ++i) {
      target[i + targetStart] = this[i + start];
    }
  } else {
    Uint8Array.prototype.set.call(target, this.subarray(start, start + len), targetStart);
  }

  return len;
}; // Usage:
//    buffer.fill(number[, offset[, end]])
//    buffer.fill(buffer[, offset[, end]])
//    buffer.fill(string[, offset[, end]][, encoding])


Buffer.prototype.fill = function fill(val, start, end, encoding) {
  // Handle string cases:
  if (typeof val === 'string') {
    if (typeof start === 'string') {
      encoding = start;
      start = 0;
      end = this.length;
    } else if (typeof end === 'string') {
      encoding = end;
      end = this.length;
    }

    if (val.length === 1) {
      var code = val.charCodeAt(0);

      if (code < 256) {
        val = code;
      }
    }

    if (encoding !== undefined && typeof encoding !== 'string') {
      throw new TypeError('encoding must be a string');
    }

    if (typeof encoding === 'string' && !Buffer.isEncoding(encoding)) {
      throw new TypeError('Unknown encoding: ' + encoding);
    }
  } else if (typeof val === 'number') {
    val = val & 255;
  } // Invalid ranges are not set to a default, so can range check early.


  if (start < 0 || this.length < start || this.length < end) {
    throw new RangeError('Out of range index');
  }

  if (end <= start) {
    return this;
  }

  start = start >>> 0;
  end = end === undefined ? this.length : end >>> 0;
  if (!val) val = 0;
  var i;

  if (typeof val === 'number') {
    for (i = start; i < end; ++i) {
      this[i] = val;
    }
  } else {
    var bytes = Buffer.isBuffer(val) ? val : utf8ToBytes(new Buffer(val, encoding).toString());
    var len = bytes.length;

    for (i = 0; i < end - start; ++i) {
      this[i + start] = bytes[i % len];
    }
  }

  return this;
}; // HELPER FUNCTIONS
// ================


var INVALID_BASE64_RE = /[^+\/0-9A-Za-z-_]/g;

function base64clean(str) {
  // Node strips out invalid characters like \n and \t from the string, base64-js does not
  str = stringtrim(str).replace(INVALID_BASE64_RE, ''); // Node converts strings with length < 2 to ''

  if (str.length < 2) return ''; // Node allows for non-padded base64 strings (missing trailing ===), base64-js does not

  while (str.length % 4 !== 0) {
    str = str + '=';
  }

  return str;
}

function stringtrim(str) {
  if (str.trim) return str.trim();
  return str.replace(/^\s+|\s+$/g, '');
}

function toHex(n) {
  if (n < 16) return '0' + n.toString(16);
  return n.toString(16);
}

function utf8ToBytes(string, units) {
  units = units || Infinity;
  var codePoint;
  var length = string.length;
  var leadSurrogate = null;
  var bytes = [];

  for (var i = 0; i < length; ++i) {
    codePoint = string.charCodeAt(i); // is surrogate component

    if (codePoint > 0xD7FF && codePoint < 0xE000) {
      // last char was a lead
      if (!leadSurrogate) {
        // no lead yet
        if (codePoint > 0xDBFF) {
          // unexpected trail
          if ((units -= 3) > -1) bytes.push(0xEF, 0xBF, 0xBD);
          continue;
        } else if (i + 1 === length) {
          // unpaired lead
          if ((units -= 3) > -1) bytes.push(0xEF, 0xBF, 0xBD);
          continue;
        } // valid lead


        leadSurrogate = codePoint;
        continue;
      } // 2 leads in a row


      if (codePoint < 0xDC00) {
        if ((units -= 3) > -1) bytes.push(0xEF, 0xBF, 0xBD);
        leadSurrogate = codePoint;
        continue;
      } // valid surrogate pair


      codePoint = (leadSurrogate - 0xD800 << 10 | codePoint - 0xDC00) + 0x10000;
    } else if (leadSurrogate) {
      // valid bmp char, but last char was a lead
      if ((units -= 3) > -1) bytes.push(0xEF, 0xBF, 0xBD);
    }

    leadSurrogate = null; // encode utf8

    if (codePoint < 0x80) {
      if ((units -= 1) < 0) break;
      bytes.push(codePoint);
    } else if (codePoint < 0x800) {
      if ((units -= 2) < 0) break;
      bytes.push(codePoint >> 0x6 | 0xC0, codePoint & 0x3F | 0x80);
    } else if (codePoint < 0x10000) {
      if ((units -= 3) < 0) break;
      bytes.push(codePoint >> 0xC | 0xE0, codePoint >> 0x6 & 0x3F | 0x80, codePoint & 0x3F | 0x80);
    } else if (codePoint < 0x110000) {
      if ((units -= 4) < 0) break;
      bytes.push(codePoint >> 0x12 | 0xF0, codePoint >> 0xC & 0x3F | 0x80, codePoint >> 0x6 & 0x3F | 0x80, codePoint & 0x3F | 0x80);
    } else {
      throw new Error('Invalid code point');
    }
  }

  return bytes;
}

function asciiToBytes(str) {
  var byteArray = [];

  for (var i = 0; i < str.length; ++i) {
    // Node's code seems to be doing this and not & 0x7F..
    byteArray.push(str.charCodeAt(i) & 0xFF);
  }

  return byteArray;
}

function utf16leToBytes(str, units) {
  var c, hi, lo;
  var byteArray = [];

  for (var i = 0; i < str.length; ++i) {
    if ((units -= 2) < 0) break;
    c = str.charCodeAt(i);
    hi = c >> 8;
    lo = c % 256;
    byteArray.push(lo);
    byteArray.push(hi);
  }

  return byteArray;
}

function base64ToBytes(str) {
  return base64.toByteArray(base64clean(str));
}

function blitBuffer(src, dst, offset, length) {
  for (var i = 0; i < length; ++i) {
    if (i + offset >= dst.length || i >= src.length) break;
    dst[i + offset] = src[i];
  }

  return i;
}

function isnan(val) {
  return val !== val; // eslint-disable-line no-self-compare
}
/* WEBPACK VAR INJECTION */}.call(this, __webpack_require__(167)))

/***/ }),
/* 167 */
/***/ (function(module, exports) {

function _typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { _typeof = function _typeof(obj) { return typeof obj; }; } else { _typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return _typeof(obj); }

var g; // This works in non-strict mode

g = function () {
  return this;
}();

try {
  // This works if eval is allowed (see CSP)
  g = g || new Function("return this")();
} catch (e) {
  // This works if the window reference is available
  if ((typeof window === "undefined" ? "undefined" : _typeof(window)) === "object") g = window;
} // g can still be undefined, but nothing to do about it...
// We return undefined, instead of nothing here, so it's
// easier to handle this case. if(!global) { ...}


module.exports = g;

/***/ }),
/* 168 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


exports.byteLength = byteLength;
exports.toByteArray = toByteArray;
exports.fromByteArray = fromByteArray;
var lookup = [];
var revLookup = [];
var Arr = typeof Uint8Array !== 'undefined' ? Uint8Array : Array;
var code = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';

for (var i = 0, len = code.length; i < len; ++i) {
  lookup[i] = code[i];
  revLookup[code.charCodeAt(i)] = i;
} // Support decoding URL-safe base64 strings, as Node.js does.
// See: https://en.wikipedia.org/wiki/Base64#URL_applications


revLookup['-'.charCodeAt(0)] = 62;
revLookup['_'.charCodeAt(0)] = 63;

function getLens(b64) {
  var len = b64.length;

  if (len % 4 > 0) {
    throw new Error('Invalid string. Length must be a multiple of 4');
  } // Trim off extra bytes after placeholder bytes are found
  // See: https://github.com/beatgammit/base64-js/issues/42


  var validLen = b64.indexOf('=');
  if (validLen === -1) validLen = len;
  var placeHoldersLen = validLen === len ? 0 : 4 - validLen % 4;
  return [validLen, placeHoldersLen];
} // base64 is 4/3 + up to two characters of the original data


function byteLength(b64) {
  var lens = getLens(b64);
  var validLen = lens[0];
  var placeHoldersLen = lens[1];
  return (validLen + placeHoldersLen) * 3 / 4 - placeHoldersLen;
}

function _byteLength(b64, validLen, placeHoldersLen) {
  return (validLen + placeHoldersLen) * 3 / 4 - placeHoldersLen;
}

function toByteArray(b64) {
  var tmp;
  var lens = getLens(b64);
  var validLen = lens[0];
  var placeHoldersLen = lens[1];
  var arr = new Arr(_byteLength(b64, validLen, placeHoldersLen));
  var curByte = 0; // if there are placeholders, only get up to the last complete 4 chars

  var len = placeHoldersLen > 0 ? validLen - 4 : validLen;

  for (var i = 0; i < len; i += 4) {
    tmp = revLookup[b64.charCodeAt(i)] << 18 | revLookup[b64.charCodeAt(i + 1)] << 12 | revLookup[b64.charCodeAt(i + 2)] << 6 | revLookup[b64.charCodeAt(i + 3)];
    arr[curByte++] = tmp >> 16 & 0xFF;
    arr[curByte++] = tmp >> 8 & 0xFF;
    arr[curByte++] = tmp & 0xFF;
  }

  if (placeHoldersLen === 2) {
    tmp = revLookup[b64.charCodeAt(i)] << 2 | revLookup[b64.charCodeAt(i + 1)] >> 4;
    arr[curByte++] = tmp & 0xFF;
  }

  if (placeHoldersLen === 1) {
    tmp = revLookup[b64.charCodeAt(i)] << 10 | revLookup[b64.charCodeAt(i + 1)] << 4 | revLookup[b64.charCodeAt(i + 2)] >> 2;
    arr[curByte++] = tmp >> 8 & 0xFF;
    arr[curByte++] = tmp & 0xFF;
  }

  return arr;
}

function tripletToBase64(num) {
  return lookup[num >> 18 & 0x3F] + lookup[num >> 12 & 0x3F] + lookup[num >> 6 & 0x3F] + lookup[num & 0x3F];
}

function encodeChunk(uint8, start, end) {
  var tmp;
  var output = [];

  for (var i = start; i < end; i += 3) {
    tmp = (uint8[i] << 16 & 0xFF0000) + (uint8[i + 1] << 8 & 0xFF00) + (uint8[i + 2] & 0xFF);
    output.push(tripletToBase64(tmp));
  }

  return output.join('');
}

function fromByteArray(uint8) {
  var tmp;
  var len = uint8.length;
  var extraBytes = len % 3; // if we have 1 byte left, pad 2 bytes

  var parts = [];
  var maxChunkLength = 16383; // must be multiple of 3
  // go through the array every three bytes, we'll deal with trailing stuff later

  for (var i = 0, len2 = len - extraBytes; i < len2; i += maxChunkLength) {
    parts.push(encodeChunk(uint8, i, i + maxChunkLength > len2 ? len2 : i + maxChunkLength));
  } // pad the end with zeros, but make sure to not forget the extra bytes


  if (extraBytes === 1) {
    tmp = uint8[len - 1];
    parts.push(lookup[tmp >> 2] + lookup[tmp << 4 & 0x3F] + '==');
  } else if (extraBytes === 2) {
    tmp = (uint8[len - 2] << 8) + uint8[len - 1];
    parts.push(lookup[tmp >> 10] + lookup[tmp >> 4 & 0x3F] + lookup[tmp << 2 & 0x3F] + '=');
  }

  return parts.join('');
}

/***/ }),
/* 169 */
/***/ (function(module, exports) {

exports.read = function (buffer, offset, isLE, mLen, nBytes) {
  var e, m;
  var eLen = nBytes * 8 - mLen - 1;
  var eMax = (1 << eLen) - 1;
  var eBias = eMax >> 1;
  var nBits = -7;
  var i = isLE ? nBytes - 1 : 0;
  var d = isLE ? -1 : 1;
  var s = buffer[offset + i];
  i += d;
  e = s & (1 << -nBits) - 1;
  s >>= -nBits;
  nBits += eLen;

  for (; nBits > 0; e = e * 256 + buffer[offset + i], i += d, nBits -= 8) {}

  m = e & (1 << -nBits) - 1;
  e >>= -nBits;
  nBits += mLen;

  for (; nBits > 0; m = m * 256 + buffer[offset + i], i += d, nBits -= 8) {}

  if (e === 0) {
    e = 1 - eBias;
  } else if (e === eMax) {
    return m ? NaN : (s ? -1 : 1) * Infinity;
  } else {
    m = m + Math.pow(2, mLen);
    e = e - eBias;
  }

  return (s ? -1 : 1) * m * Math.pow(2, e - mLen);
};

exports.write = function (buffer, value, offset, isLE, mLen, nBytes) {
  var e, m, c;
  var eLen = nBytes * 8 - mLen - 1;
  var eMax = (1 << eLen) - 1;
  var eBias = eMax >> 1;
  var rt = mLen === 23 ? Math.pow(2, -24) - Math.pow(2, -77) : 0;
  var i = isLE ? 0 : nBytes - 1;
  var d = isLE ? 1 : -1;
  var s = value < 0 || value === 0 && 1 / value < 0 ? 1 : 0;
  value = Math.abs(value);

  if (isNaN(value) || value === Infinity) {
    m = isNaN(value) ? 1 : 0;
    e = eMax;
  } else {
    e = Math.floor(Math.log(value) / Math.LN2);

    if (value * (c = Math.pow(2, -e)) < 1) {
      e--;
      c *= 2;
    }

    if (e + eBias >= 1) {
      value += rt / c;
    } else {
      value += rt * Math.pow(2, 1 - eBias);
    }

    if (value * c >= 2) {
      e++;
      c /= 2;
    }

    if (e + eBias >= eMax) {
      m = 0;
      e = eMax;
    } else if (e + eBias >= 1) {
      m = (value * c - 1) * Math.pow(2, mLen);
      e = e + eBias;
    } else {
      m = value * Math.pow(2, eBias - 1) * Math.pow(2, mLen);
      e = 0;
    }
  }

  for (; mLen >= 8; buffer[offset + i] = m & 0xff, i += d, m /= 256, mLen -= 8) {}

  e = e << mLen | m;
  eLen += mLen;

  for (; eLen > 0; buffer[offset + i] = e & 0xff, i += d, e /= 256, eLen -= 8) {}

  buffer[offset + i - d] |= s * 128;
};

/***/ }),
/* 170 */
/***/ (function(module, exports) {

var toString = {}.toString;

module.exports = Array.isArray || function (arr) {
  return toString.call(arr) == '[object Array]';
};

/***/ }),
/* 171 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


var Type = __webpack_require__(15);

var _hasOwnProperty = Object.prototype.hasOwnProperty;
var _toString = Object.prototype.toString;

function resolveYamlOmap(data) {
  if (data === null) return true;
  var objectKeys = [],
      index,
      length,
      pair,
      pairKey,
      pairHasKey,
      object = data;

  for (index = 0, length = object.length; index < length; index += 1) {
    pair = object[index];
    pairHasKey = false;
    if (_toString.call(pair) !== '[object Object]') return false;

    for (pairKey in pair) {
      if (_hasOwnProperty.call(pair, pairKey)) {
        if (!pairHasKey) pairHasKey = true;else return false;
      }
    }

    if (!pairHasKey) return false;
    if (objectKeys.indexOf(pairKey) === -1) objectKeys.push(pairKey);else return false;
  }

  return true;
}

function constructYamlOmap(data) {
  return data !== null ? data : [];
}

module.exports = new Type('tag:yaml.org,2002:omap', {
  kind: 'sequence',
  resolve: resolveYamlOmap,
  construct: constructYamlOmap
});

/***/ }),
/* 172 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


var Type = __webpack_require__(15);

var _toString = Object.prototype.toString;

function resolveYamlPairs(data) {
  if (data === null) return true;
  var index,
      length,
      pair,
      keys,
      result,
      object = data;
  result = new Array(object.length);

  for (index = 0, length = object.length; index < length; index += 1) {
    pair = object[index];
    if (_toString.call(pair) !== '[object Object]') return false;
    keys = Object.keys(pair);
    if (keys.length !== 1) return false;
    result[index] = [keys[0], pair[keys[0]]];
  }

  return true;
}

function constructYamlPairs(data) {
  if (data === null) return [];
  var index,
      length,
      pair,
      keys,
      result,
      object = data;
  result = new Array(object.length);

  for (index = 0, length = object.length; index < length; index += 1) {
    pair = object[index];
    keys = Object.keys(pair);
    result[index] = [keys[0], pair[keys[0]]];
  }

  return result;
}

module.exports = new Type('tag:yaml.org,2002:pairs', {
  kind: 'sequence',
  resolve: resolveYamlPairs,
  construct: constructYamlPairs
});

/***/ }),
/* 173 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


var Type = __webpack_require__(15);

var _hasOwnProperty = Object.prototype.hasOwnProperty;

function resolveYamlSet(data) {
  if (data === null) return true;
  var key,
      object = data;

  for (key in object) {
    if (_hasOwnProperty.call(object, key)) {
      if (object[key] !== null) return false;
    }
  }

  return true;
}

function constructYamlSet(data) {
  return data !== null ? data : {};
}

module.exports = new Type('tag:yaml.org,2002:set', {
  kind: 'mapping',
  resolve: resolveYamlSet,
  construct: constructYamlSet
});

/***/ }),
/* 174 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


var Type = __webpack_require__(15);

function resolveJavascriptUndefined() {
  return true;
}

function constructJavascriptUndefined() {
  /*eslint-disable no-undefined*/
  return undefined;
}

function representJavascriptUndefined() {
  return '';
}

function isUndefined(object) {
  return typeof object === 'undefined';
}

module.exports = new Type('tag:yaml.org,2002:js/undefined', {
  kind: 'scalar',
  resolve: resolveJavascriptUndefined,
  construct: constructJavascriptUndefined,
  predicate: isUndefined,
  represent: representJavascriptUndefined
});

/***/ }),
/* 175 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


var Type = __webpack_require__(15);

function resolveJavascriptRegExp(data) {
  if (data === null) return false;
  if (data.length === 0) return false;
  var regexp = data,
      tail = /\/([gim]*)$/.exec(data),
      modifiers = ''; // if regexp starts with '/' it can have modifiers and must be properly closed
  // `/foo/gim` - modifiers tail can be maximum 3 chars

  if (regexp[0] === '/') {
    if (tail) modifiers = tail[1];
    if (modifiers.length > 3) return false; // if expression starts with /, is should be properly terminated

    if (regexp[regexp.length - modifiers.length - 1] !== '/') return false;
  }

  return true;
}

function constructJavascriptRegExp(data) {
  var regexp = data,
      tail = /\/([gim]*)$/.exec(data),
      modifiers = ''; // `/foo/gim` - tail can be maximum 4 chars

  if (regexp[0] === '/') {
    if (tail) modifiers = tail[1];
    regexp = regexp.slice(1, regexp.length - modifiers.length - 1);
  }

  return new RegExp(regexp, modifiers);
}

function representJavascriptRegExp(object
/*, style*/
) {
  var result = '/' + object.source + '/';
  if (object.global) result += 'g';
  if (object.multiline) result += 'm';
  if (object.ignoreCase) result += 'i';
  return result;
}

function isRegExp(object) {
  return Object.prototype.toString.call(object) === '[object RegExp]';
}

module.exports = new Type('tag:yaml.org,2002:js/regexp', {
  kind: 'scalar',
  resolve: resolveJavascriptRegExp,
  construct: constructJavascriptRegExp,
  predicate: isRegExp,
  represent: representJavascriptRegExp
});

/***/ }),
/* 176 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";
var require;

var esprima; // Browserified version does not have esprima
//
// 1. For node.js just require module as deps
// 2. For browser try to require mudule via external AMD system.
//    If not found - try to fallback to window.esprima. If not
//    found too - then fail to parse.
//

try {
  // workaround to exclude package from browserify list.
  var _require = require;
  esprima = __webpack_require__(2);
} catch (_) {
  /*global window */
  if (typeof window !== 'undefined') esprima = window.esprima;
}

var Type = __webpack_require__(15);

function resolveJavascriptFunction(data) {
  if (data === null) return false;

  try {
    var source = '(' + data + ')',
        ast = esprima.parse(source, {
      range: true
    });

    if (ast.type !== 'Program' || ast.body.length !== 1 || ast.body[0].type !== 'ExpressionStatement' || ast.body[0].expression.type !== 'ArrowFunctionExpression' && ast.body[0].expression.type !== 'FunctionExpression') {
      return false;
    }

    return true;
  } catch (err) {
    return false;
  }
}

function constructJavascriptFunction(data) {
  /*jslint evil:true*/
  var source = '(' + data + ')',
      ast = esprima.parse(source, {
    range: true
  }),
      params = [],
      body;

  if (ast.type !== 'Program' || ast.body.length !== 1 || ast.body[0].type !== 'ExpressionStatement' || ast.body[0].expression.type !== 'ArrowFunctionExpression' && ast.body[0].expression.type !== 'FunctionExpression') {
    throw new Error('Failed to resolve function');
  }

  ast.body[0].expression.params.forEach(function (param) {
    params.push(param.name);
  });
  body = ast.body[0].expression.body.range; // Esprima's ranges include the first '{' and the last '}' characters on
  // function expressions. So cut them out.

  if (ast.body[0].expression.body.type === 'BlockStatement') {
    /*eslint-disable no-new-func*/
    return new Function(params, source.slice(body[0] + 1, body[1] - 1));
  } // ES6 arrow functions can omit the BlockStatement. In that case, just return
  // the body.

  /*eslint-disable no-new-func*/


  return new Function(params, 'return ' + source.slice(body[0], body[1]));
}

function representJavascriptFunction(object
/*, style*/
) {
  return object.toString();
}

function isFunction(object) {
  return Object.prototype.toString.call(object) === '[object Function]';
}

module.exports = new Type('tag:yaml.org,2002:js/function', {
  kind: 'scalar',
  resolve: resolveJavascriptFunction,
  construct: constructJavascriptFunction,
  predicate: isFunction,
  represent: representJavascriptFunction
});

/***/ }),
/* 177 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

/*eslint-disable no-use-before-define*/

function _typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { _typeof = function _typeof(obj) { return typeof obj; }; } else { _typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return _typeof(obj); }

var common = __webpack_require__(41);

var YAMLException = __webpack_require__(51);

var DEFAULT_FULL_SCHEMA = __webpack_require__(73);

var DEFAULT_SAFE_SCHEMA = __webpack_require__(52);

var _toString = Object.prototype.toString;
var _hasOwnProperty = Object.prototype.hasOwnProperty;
var CHAR_TAB = 0x09;
/* Tab */

var CHAR_LINE_FEED = 0x0A;
/* LF */

var CHAR_SPACE = 0x20;
/* Space */

var CHAR_EXCLAMATION = 0x21;
/* ! */

var CHAR_DOUBLE_QUOTE = 0x22;
/* " */

var CHAR_SHARP = 0x23;
/* # */

var CHAR_PERCENT = 0x25;
/* % */

var CHAR_AMPERSAND = 0x26;
/* & */

var CHAR_SINGLE_QUOTE = 0x27;
/* ' */

var CHAR_ASTERISK = 0x2A;
/* * */

var CHAR_COMMA = 0x2C;
/* , */

var CHAR_MINUS = 0x2D;
/* - */

var CHAR_COLON = 0x3A;
/* : */

var CHAR_GREATER_THAN = 0x3E;
/* > */

var CHAR_QUESTION = 0x3F;
/* ? */

var CHAR_COMMERCIAL_AT = 0x40;
/* @ */

var CHAR_LEFT_SQUARE_BRACKET = 0x5B;
/* [ */

var CHAR_RIGHT_SQUARE_BRACKET = 0x5D;
/* ] */

var CHAR_GRAVE_ACCENT = 0x60;
/* ` */

var CHAR_LEFT_CURLY_BRACKET = 0x7B;
/* { */

var CHAR_VERTICAL_LINE = 0x7C;
/* | */

var CHAR_RIGHT_CURLY_BRACKET = 0x7D;
/* } */

var ESCAPE_SEQUENCES = {};
ESCAPE_SEQUENCES[0x00] = '\\0';
ESCAPE_SEQUENCES[0x07] = '\\a';
ESCAPE_SEQUENCES[0x08] = '\\b';
ESCAPE_SEQUENCES[0x09] = '\\t';
ESCAPE_SEQUENCES[0x0A] = '\\n';
ESCAPE_SEQUENCES[0x0B] = '\\v';
ESCAPE_SEQUENCES[0x0C] = '\\f';
ESCAPE_SEQUENCES[0x0D] = '\\r';
ESCAPE_SEQUENCES[0x1B] = '\\e';
ESCAPE_SEQUENCES[0x22] = '\\"';
ESCAPE_SEQUENCES[0x5C] = '\\\\';
ESCAPE_SEQUENCES[0x85] = '\\N';
ESCAPE_SEQUENCES[0xA0] = '\\_';
ESCAPE_SEQUENCES[0x2028] = '\\L';
ESCAPE_SEQUENCES[0x2029] = '\\P';
var DEPRECATED_BOOLEANS_SYNTAX = ['y', 'Y', 'yes', 'Yes', 'YES', 'on', 'On', 'ON', 'n', 'N', 'no', 'No', 'NO', 'off', 'Off', 'OFF'];

function compileStyleMap(schema, map) {
  var result, keys, index, length, tag, style, type;
  if (map === null) return {};
  result = {};
  keys = Object.keys(map);

  for (index = 0, length = keys.length; index < length; index += 1) {
    tag = keys[index];
    style = String(map[tag]);

    if (tag.slice(0, 2) === '!!') {
      tag = 'tag:yaml.org,2002:' + tag.slice(2);
    }

    type = schema.compiledTypeMap['fallback'][tag];

    if (type && _hasOwnProperty.call(type.styleAliases, style)) {
      style = type.styleAliases[style];
    }

    result[tag] = style;
  }

  return result;
}

function encodeHex(character) {
  var string, handle, length;
  string = character.toString(16).toUpperCase();

  if (character <= 0xFF) {
    handle = 'x';
    length = 2;
  } else if (character <= 0xFFFF) {
    handle = 'u';
    length = 4;
  } else if (character <= 0xFFFFFFFF) {
    handle = 'U';
    length = 8;
  } else {
    throw new YAMLException('code point within a string may not be greater than 0xFFFFFFFF');
  }

  return '\\' + handle + common.repeat('0', length - string.length) + string;
}

function State(options) {
  this.schema = options['schema'] || DEFAULT_FULL_SCHEMA;
  this.indent = Math.max(1, options['indent'] || 2);
  this.noArrayIndent = options['noArrayIndent'] || false;
  this.skipInvalid = options['skipInvalid'] || false;
  this.flowLevel = common.isNothing(options['flowLevel']) ? -1 : options['flowLevel'];
  this.styleMap = compileStyleMap(this.schema, options['styles'] || null);
  this.sortKeys = options['sortKeys'] || false;
  this.lineWidth = options['lineWidth'] || 80;
  this.noRefs = options['noRefs'] || false;
  this.noCompatMode = options['noCompatMode'] || false;
  this.condenseFlow = options['condenseFlow'] || false;
  this.implicitTypes = this.schema.compiledImplicit;
  this.explicitTypes = this.schema.compiledExplicit;
  this.tag = null;
  this.result = '';
  this.duplicates = [];
  this.usedDuplicates = null;
} // Indents every line in a string. Empty lines (\n only) are not indented.


function indentString(string, spaces) {
  var ind = common.repeat(' ', spaces),
      position = 0,
      next = -1,
      result = '',
      line,
      length = string.length;

  while (position < length) {
    next = string.indexOf('\n', position);

    if (next === -1) {
      line = string.slice(position);
      position = length;
    } else {
      line = string.slice(position, next + 1);
      position = next + 1;
    }

    if (line.length && line !== '\n') result += ind;
    result += line;
  }

  return result;
}

function generateNextLine(state, level) {
  return '\n' + common.repeat(' ', state.indent * level);
}

function testImplicitResolving(state, str) {
  var index, length, type;

  for (index = 0, length = state.implicitTypes.length; index < length; index += 1) {
    type = state.implicitTypes[index];

    if (type.resolve(str)) {
      return true;
    }
  }

  return false;
} // [33] s-white ::= s-space | s-tab


function isWhitespace(c) {
  return c === CHAR_SPACE || c === CHAR_TAB;
} // Returns true if the character can be printed without escaping.
// From YAML 1.2: "any allowed characters known to be non-printable
// should also be escaped. [However,] This isn’t mandatory"
// Derived from nb-char - \t - #x85 - #xA0 - #x2028 - #x2029.


function isPrintable(c) {
  return 0x00020 <= c && c <= 0x00007E || 0x000A1 <= c && c <= 0x00D7FF && c !== 0x2028 && c !== 0x2029 || 0x0E000 <= c && c <= 0x00FFFD && c !== 0xFEFF
  /* BOM */
  || 0x10000 <= c && c <= 0x10FFFF;
} // Simplified test for values allowed after the first character in plain style.


function isPlainSafe(c) {
  // Uses a subset of nb-char - c-flow-indicator - ":" - "#"
  // where nb-char ::= c-printable - b-char - c-byte-order-mark.
  return isPrintable(c) && c !== 0xFEFF // - c-flow-indicator
  && c !== CHAR_COMMA && c !== CHAR_LEFT_SQUARE_BRACKET && c !== CHAR_RIGHT_SQUARE_BRACKET && c !== CHAR_LEFT_CURLY_BRACKET && c !== CHAR_RIGHT_CURLY_BRACKET // - ":" - "#"
  && c !== CHAR_COLON && c !== CHAR_SHARP;
} // Simplified test for values allowed as the first character in plain style.


function isPlainSafeFirst(c) {
  // Uses a subset of ns-char - c-indicator
  // where ns-char = nb-char - s-white.
  return isPrintable(c) && c !== 0xFEFF && !isWhitespace(c) // - s-white
  // - (c-indicator ::=
  // “-” | “?” | “:” | “,” | “[” | “]” | “{” | “}”
  && c !== CHAR_MINUS && c !== CHAR_QUESTION && c !== CHAR_COLON && c !== CHAR_COMMA && c !== CHAR_LEFT_SQUARE_BRACKET && c !== CHAR_RIGHT_SQUARE_BRACKET && c !== CHAR_LEFT_CURLY_BRACKET && c !== CHAR_RIGHT_CURLY_BRACKET // | “#” | “&” | “*” | “!” | “|” | “>” | “'” | “"”
  && c !== CHAR_SHARP && c !== CHAR_AMPERSAND && c !== CHAR_ASTERISK && c !== CHAR_EXCLAMATION && c !== CHAR_VERTICAL_LINE && c !== CHAR_GREATER_THAN && c !== CHAR_SINGLE_QUOTE && c !== CHAR_DOUBLE_QUOTE // | “%” | “@” | “`”)
  && c !== CHAR_PERCENT && c !== CHAR_COMMERCIAL_AT && c !== CHAR_GRAVE_ACCENT;
} // Determines whether block indentation indicator is required.


function needIndentIndicator(string) {
  var leadingSpaceRe = /^\n* /;
  return leadingSpaceRe.test(string);
}

var STYLE_PLAIN = 1,
    STYLE_SINGLE = 2,
    STYLE_LITERAL = 3,
    STYLE_FOLDED = 4,
    STYLE_DOUBLE = 5; // Determines which scalar styles are possible and returns the preferred style.
// lineWidth = -1 => no limit.
// Pre-conditions: str.length > 0.
// Post-conditions:
//    STYLE_PLAIN or STYLE_SINGLE => no \n are in the string.
//    STYLE_LITERAL => no lines are suitable for folding (or lineWidth is -1).
//    STYLE_FOLDED => a line > lineWidth and can be folded (and lineWidth != -1).

function chooseScalarStyle(string, singleLineOnly, indentPerLevel, lineWidth, testAmbiguousType) {
  var i;

  var _char;

  var hasLineBreak = false;
  var hasFoldableLine = false; // only checked if shouldTrackWidth

  var shouldTrackWidth = lineWidth !== -1;
  var previousLineBreak = -1; // count the first line correctly

  var plain = isPlainSafeFirst(string.charCodeAt(0)) && !isWhitespace(string.charCodeAt(string.length - 1));

  if (singleLineOnly) {
    // Case: no block styles.
    // Check for disallowed characters to rule out plain and single.
    for (i = 0; i < string.length; i++) {
      _char = string.charCodeAt(i);

      if (!isPrintable(_char)) {
        return STYLE_DOUBLE;
      }

      plain = plain && isPlainSafe(_char);
    }
  } else {
    // Case: block styles permitted.
    for (i = 0; i < string.length; i++) {
      _char = string.charCodeAt(i);

      if (_char === CHAR_LINE_FEED) {
        hasLineBreak = true; // Check if any line can be folded.

        if (shouldTrackWidth) {
          hasFoldableLine = hasFoldableLine || // Foldable line = too long, and not more-indented.
          i - previousLineBreak - 1 > lineWidth && string[previousLineBreak + 1] !== ' ';
          previousLineBreak = i;
        }
      } else if (!isPrintable(_char)) {
        return STYLE_DOUBLE;
      }

      plain = plain && isPlainSafe(_char);
    } // in case the end is missing a \n


    hasFoldableLine = hasFoldableLine || shouldTrackWidth && i - previousLineBreak - 1 > lineWidth && string[previousLineBreak + 1] !== ' ';
  } // Although every style can represent \n without escaping, prefer block styles
  // for multiline, since they're more readable and they don't add empty lines.
  // Also prefer folding a super-long line.


  if (!hasLineBreak && !hasFoldableLine) {
    // Strings interpretable as another type have to be quoted;
    // e.g. the string 'true' vs. the boolean true.
    return plain && !testAmbiguousType(string) ? STYLE_PLAIN : STYLE_SINGLE;
  } // Edge case: block indentation indicator can only have one digit.


  if (indentPerLevel > 9 && needIndentIndicator(string)) {
    return STYLE_DOUBLE;
  } // At this point we know block styles are valid.
  // Prefer literal style unless we want to fold.


  return hasFoldableLine ? STYLE_FOLDED : STYLE_LITERAL;
} // Note: line breaking/folding is implemented for only the folded style.
// NB. We drop the last trailing newline (if any) of a returned block scalar
//  since the dumper adds its own newline. This always works:
//    • No ending newline => unaffected; already using strip "-" chomping.
//    • Ending newline    => removed then restored.
//  Importantly, this keeps the "+" chomp indicator from gaining an extra line.


function writeScalar(state, string, level, iskey) {
  state.dump = function () {
    if (string.length === 0) {
      return "''";
    }

    if (!state.noCompatMode && DEPRECATED_BOOLEANS_SYNTAX.indexOf(string) !== -1) {
      return "'" + string + "'";
    }

    var indent = state.indent * Math.max(1, level); // no 0-indent scalars
    // As indentation gets deeper, let the width decrease monotonically
    // to the lower bound min(state.lineWidth, 40).
    // Note that this implies
    //  state.lineWidth ≤ 40 + state.indent: width is fixed at the lower bound.
    //  state.lineWidth > 40 + state.indent: width decreases until the lower bound.
    // This behaves better than a constant minimum width which disallows narrower options,
    // or an indent threshold which causes the width to suddenly increase.

    var lineWidth = state.lineWidth === -1 ? -1 : Math.max(Math.min(state.lineWidth, 40), state.lineWidth - indent); // Without knowing if keys are implicit/explicit, assume implicit for safety.

    var singleLineOnly = iskey // No block styles in flow mode.
    || state.flowLevel > -1 && level >= state.flowLevel;

    function testAmbiguity(string) {
      return testImplicitResolving(state, string);
    }

    switch (chooseScalarStyle(string, singleLineOnly, state.indent, lineWidth, testAmbiguity)) {
      case STYLE_PLAIN:
        return string;

      case STYLE_SINGLE:
        return "'" + string.replace(/'/g, "''") + "'";

      case STYLE_LITERAL:
        return '|' + blockHeader(string, state.indent) + dropEndingNewline(indentString(string, indent));

      case STYLE_FOLDED:
        return '>' + blockHeader(string, state.indent) + dropEndingNewline(indentString(foldString(string, lineWidth), indent));

      case STYLE_DOUBLE:
        return '"' + escapeString(string, lineWidth) + '"';

      default:
        throw new YAMLException('impossible error: invalid scalar style');
    }
  }();
} // Pre-conditions: string is valid for a block scalar, 1 <= indentPerLevel <= 9.


function blockHeader(string, indentPerLevel) {
  var indentIndicator = needIndentIndicator(string) ? String(indentPerLevel) : ''; // note the special case: the string '\n' counts as a "trailing" empty line.

  var clip = string[string.length - 1] === '\n';
  var keep = clip && (string[string.length - 2] === '\n' || string === '\n');
  var chomp = keep ? '+' : clip ? '' : '-';
  return indentIndicator + chomp + '\n';
} // (See the note for writeScalar.)


function dropEndingNewline(string) {
  return string[string.length - 1] === '\n' ? string.slice(0, -1) : string;
} // Note: a long line without a suitable break point will exceed the width limit.
// Pre-conditions: every char in str isPrintable, str.length > 0, width > 0.


function foldString(string, width) {
  // In folded style, $k$ consecutive newlines output as $k+1$ newlines—
  // unless they're before or after a more-indented line, or at the very
  // beginning or end, in which case $k$ maps to $k$.
  // Therefore, parse each chunk as newline(s) followed by a content line.
  var lineRe = /(\n+)([^\n]*)/g; // first line (possibly an empty line)

  var result = function () {
    var nextLF = string.indexOf('\n');
    nextLF = nextLF !== -1 ? nextLF : string.length;
    lineRe.lastIndex = nextLF;
    return foldLine(string.slice(0, nextLF), width);
  }(); // If we haven't reached the first content line yet, don't add an extra \n.


  var prevMoreIndented = string[0] === '\n' || string[0] === ' ';
  var moreIndented; // rest of the lines

  var match;

  while (match = lineRe.exec(string)) {
    var prefix = match[1],
        line = match[2];
    moreIndented = line[0] === ' ';
    result += prefix + (!prevMoreIndented && !moreIndented && line !== '' ? '\n' : '') + foldLine(line, width);
    prevMoreIndented = moreIndented;
  }

  return result;
} // Greedy line breaking.
// Picks the longest line under the limit each time,
// otherwise settles for the shortest line over the limit.
// NB. More-indented lines *cannot* be folded, as that would add an extra \n.


function foldLine(line, width) {
  if (line === '' || line[0] === ' ') return line; // Since a more-indented line adds a \n, breaks can't be followed by a space.

  var breakRe = / [^ ]/g; // note: the match index will always be <= length-2.

  var match; // start is an inclusive index. end, curr, and next are exclusive.

  var start = 0,
      end,
      curr = 0,
      next = 0;
  var result = ''; // Invariants: 0 <= start <= length-1.
  //   0 <= curr <= next <= max(0, length-2). curr - start <= width.
  // Inside the loop:
  //   A match implies length >= 2, so curr and next are <= length-2.

  while (match = breakRe.exec(line)) {
    next = match.index; // maintain invariant: curr - start <= width

    if (next - start > width) {
      end = curr > start ? curr : next; // derive end <= length-2

      result += '\n' + line.slice(start, end); // skip the space that was output as \n

      start = end + 1; // derive start <= length-1
    }

    curr = next;
  } // By the invariants, start <= length-1, so there is something left over.
  // It is either the whole string or a part starting from non-whitespace.


  result += '\n'; // Insert a break if the remainder is too long and there is a break available.

  if (line.length - start > width && curr > start) {
    result += line.slice(start, curr) + '\n' + line.slice(curr + 1);
  } else {
    result += line.slice(start);
  }

  return result.slice(1); // drop extra \n joiner
} // Escapes a double-quoted string.


function escapeString(string) {
  var result = '';

  var _char2, nextChar;

  var escapeSeq;

  for (var i = 0; i < string.length; i++) {
    _char2 = string.charCodeAt(i); // Check for surrogate pairs (reference Unicode 3.0 section "3.7 Surrogates").

    if (_char2 >= 0xD800 && _char2 <= 0xDBFF
    /* high surrogate */
    ) {
        nextChar = string.charCodeAt(i + 1);

        if (nextChar >= 0xDC00 && nextChar <= 0xDFFF
        /* low surrogate */
        ) {
            // Combine the surrogate pair and store it escaped.
            result += encodeHex((_char2 - 0xD800) * 0x400 + nextChar - 0xDC00 + 0x10000); // Advance index one extra since we already used that char here.

            i++;
            continue;
          }
      }

    escapeSeq = ESCAPE_SEQUENCES[_char2];
    result += !escapeSeq && isPrintable(_char2) ? string[i] : escapeSeq || encodeHex(_char2);
  }

  return result;
}

function writeFlowSequence(state, level, object) {
  var _result = '',
      _tag = state.tag,
      index,
      length;

  for (index = 0, length = object.length; index < length; index += 1) {
    // Write only valid elements.
    if (writeNode(state, level, object[index], false, false)) {
      if (index !== 0) _result += ',' + (!state.condenseFlow ? ' ' : '');
      _result += state.dump;
    }
  }

  state.tag = _tag;
  state.dump = '[' + _result + ']';
}

function writeBlockSequence(state, level, object, compact) {
  var _result = '',
      _tag = state.tag,
      index,
      length;

  for (index = 0, length = object.length; index < length; index += 1) {
    // Write only valid elements.
    if (writeNode(state, level + 1, object[index], true, true)) {
      if (!compact || index !== 0) {
        _result += generateNextLine(state, level);
      }

      if (state.dump && CHAR_LINE_FEED === state.dump.charCodeAt(0)) {
        _result += '-';
      } else {
        _result += '- ';
      }

      _result += state.dump;
    }
  }

  state.tag = _tag;
  state.dump = _result || '[]'; // Empty sequence if no valid values.
}

function writeFlowMapping(state, level, object) {
  var _result = '',
      _tag = state.tag,
      objectKeyList = Object.keys(object),
      index,
      length,
      objectKey,
      objectValue,
      pairBuffer;

  for (index = 0, length = objectKeyList.length; index < length; index += 1) {
    pairBuffer = state.condenseFlow ? '"' : '';
    if (index !== 0) pairBuffer += ', ';
    objectKey = objectKeyList[index];
    objectValue = object[objectKey];

    if (!writeNode(state, level, objectKey, false, false)) {
      continue; // Skip this pair because of invalid key;
    }

    if (state.dump.length > 1024) pairBuffer += '? ';
    pairBuffer += state.dump + (state.condenseFlow ? '"' : '') + ':' + (state.condenseFlow ? '' : ' ');

    if (!writeNode(state, level, objectValue, false, false)) {
      continue; // Skip this pair because of invalid value.
    }

    pairBuffer += state.dump; // Both key and value are valid.

    _result += pairBuffer;
  }

  state.tag = _tag;
  state.dump = '{' + _result + '}';
}

function writeBlockMapping(state, level, object, compact) {
  var _result = '',
      _tag = state.tag,
      objectKeyList = Object.keys(object),
      index,
      length,
      objectKey,
      objectValue,
      explicitPair,
      pairBuffer; // Allow sorting keys so that the output file is deterministic

  if (state.sortKeys === true) {
    // Default sorting
    objectKeyList.sort();
  } else if (typeof state.sortKeys === 'function') {
    // Custom sort function
    objectKeyList.sort(state.sortKeys);
  } else if (state.sortKeys) {
    // Something is wrong
    throw new YAMLException('sortKeys must be a boolean or a function');
  }

  for (index = 0, length = objectKeyList.length; index < length; index += 1) {
    pairBuffer = '';

    if (!compact || index !== 0) {
      pairBuffer += generateNextLine(state, level);
    }

    objectKey = objectKeyList[index];
    objectValue = object[objectKey];

    if (!writeNode(state, level + 1, objectKey, true, true, true)) {
      continue; // Skip this pair because of invalid key.
    }

    explicitPair = state.tag !== null && state.tag !== '?' || state.dump && state.dump.length > 1024;

    if (explicitPair) {
      if (state.dump && CHAR_LINE_FEED === state.dump.charCodeAt(0)) {
        pairBuffer += '?';
      } else {
        pairBuffer += '? ';
      }
    }

    pairBuffer += state.dump;

    if (explicitPair) {
      pairBuffer += generateNextLine(state, level);
    }

    if (!writeNode(state, level + 1, objectValue, true, explicitPair)) {
      continue; // Skip this pair because of invalid value.
    }

    if (state.dump && CHAR_LINE_FEED === state.dump.charCodeAt(0)) {
      pairBuffer += ':';
    } else {
      pairBuffer += ': ';
    }

    pairBuffer += state.dump; // Both key and value are valid.

    _result += pairBuffer;
  }

  state.tag = _tag;
  state.dump = _result || '{}'; // Empty mapping if no valid pairs.
}

function detectType(state, object, explicit) {
  var _result, typeList, index, length, type, style;

  typeList = explicit ? state.explicitTypes : state.implicitTypes;

  for (index = 0, length = typeList.length; index < length; index += 1) {
    type = typeList[index];

    if ((type.instanceOf || type.predicate) && (!type.instanceOf || _typeof(object) === 'object' && object instanceof type.instanceOf) && (!type.predicate || type.predicate(object))) {
      state.tag = explicit ? type.tag : '?';

      if (type.represent) {
        style = state.styleMap[type.tag] || type.defaultStyle;

        if (_toString.call(type.represent) === '[object Function]') {
          _result = type.represent(object, style);
        } else if (_hasOwnProperty.call(type.represent, style)) {
          _result = type.represent[style](object, style);
        } else {
          throw new YAMLException('!<' + type.tag + '> tag resolver accepts not "' + style + '" style');
        }

        state.dump = _result;
      }

      return true;
    }
  }

  return false;
} // Serializes `object` and writes it to global `result`.
// Returns true on success, or false on invalid object.
//


function writeNode(state, level, object, block, compact, iskey) {
  state.tag = null;
  state.dump = object;

  if (!detectType(state, object, false)) {
    detectType(state, object, true);
  }

  var type = _toString.call(state.dump);

  if (block) {
    block = state.flowLevel < 0 || state.flowLevel > level;
  }

  var objectOrArray = type === '[object Object]' || type === '[object Array]',
      duplicateIndex,
      duplicate;

  if (objectOrArray) {
    duplicateIndex = state.duplicates.indexOf(object);
    duplicate = duplicateIndex !== -1;
  }

  if (state.tag !== null && state.tag !== '?' || duplicate || state.indent !== 2 && level > 0) {
    compact = false;
  }

  if (duplicate && state.usedDuplicates[duplicateIndex]) {
    state.dump = '*ref_' + duplicateIndex;
  } else {
    if (objectOrArray && duplicate && !state.usedDuplicates[duplicateIndex]) {
      state.usedDuplicates[duplicateIndex] = true;
    }

    if (type === '[object Object]') {
      if (block && Object.keys(state.dump).length !== 0) {
        writeBlockMapping(state, level, state.dump, compact);

        if (duplicate) {
          state.dump = '&ref_' + duplicateIndex + state.dump;
        }
      } else {
        writeFlowMapping(state, level, state.dump);

        if (duplicate) {
          state.dump = '&ref_' + duplicateIndex + ' ' + state.dump;
        }
      }
    } else if (type === '[object Array]') {
      var arrayLevel = state.noArrayIndent && level > 0 ? level - 1 : level;

      if (block && state.dump.length !== 0) {
        writeBlockSequence(state, arrayLevel, state.dump, compact);

        if (duplicate) {
          state.dump = '&ref_' + duplicateIndex + state.dump;
        }
      } else {
        writeFlowSequence(state, arrayLevel, state.dump);

        if (duplicate) {
          state.dump = '&ref_' + duplicateIndex + ' ' + state.dump;
        }
      }
    } else if (type === '[object String]') {
      if (state.tag !== '?') {
        writeScalar(state, state.dump, level, iskey);
      }
    } else {
      if (state.skipInvalid) return false;
      throw new YAMLException('unacceptable kind of an object to dump ' + type);
    }

    if (state.tag !== null && state.tag !== '?') {
      state.dump = '!<' + state.tag + '> ' + state.dump;
    }
  }

  return true;
}

function getDuplicateReferences(object, state) {
  var objects = [],
      duplicatesIndexes = [],
      index,
      length;
  inspectNode(object, objects, duplicatesIndexes);

  for (index = 0, length = duplicatesIndexes.length; index < length; index += 1) {
    state.duplicates.push(objects[duplicatesIndexes[index]]);
  }

  state.usedDuplicates = new Array(length);
}

function inspectNode(object, objects, duplicatesIndexes) {
  var objectKeyList, index, length;

  if (object !== null && _typeof(object) === 'object') {
    index = objects.indexOf(object);

    if (index !== -1) {
      if (duplicatesIndexes.indexOf(index) === -1) {
        duplicatesIndexes.push(index);
      }
    } else {
      objects.push(object);

      if (Array.isArray(object)) {
        for (index = 0, length = object.length; index < length; index += 1) {
          inspectNode(object[index], objects, duplicatesIndexes);
        }
      } else {
        objectKeyList = Object.keys(object);

        for (index = 0, length = objectKeyList.length; index < length; index += 1) {
          inspectNode(object[objectKeyList[index]], objects, duplicatesIndexes);
        }
      }
    }
  }
}

function dump(input, options) {
  options = options || {};
  var state = new State(options);
  if (!state.noRefs) getDuplicateReferences(input, state);
  if (writeNode(state, 0, input, true, true)) return state.dump + '\n';
  return '';
}

function safeDump(input, options) {
  return dump(input, common.extend({
    schema: DEFAULT_SAFE_SCHEMA
  }, options));
}

module.exports.dump = dump;
module.exports.safeDump = safeDump;

/***/ }),
/* 178 */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony import */ var _polymer_polymer_polymer_legacy_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(4);
/* harmony import */ var _polymer_polymer_lib_legacy_polymer_fn_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(8);
/* harmony import */ var _polymer_polymer_lib_legacy_polymer_dom_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(9);
/* harmony import */ var _polymer_polymer_lib_utils_html_tag_js__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(7);
function _templateObject() {
  var data = _taggedTemplateLiteral(["\n    <style>\n      :host {\n        display: block;\n        position: absolute;\n        outline: none;\n        z-index: 1002;\n        -moz-user-select: none;\n        -ms-user-select: none;\n        -webkit-user-select: none;\n        user-select: none;\n        cursor: default;\n      }\n\n      #tooltip {\n        display: block;\n        outline: none;\n        @apply --paper-font-common-base;\n        font-size: 10px;\n        line-height: 1;\n        background-color: var(--paper-tooltip-background, #616161);\n        color: var(--paper-tooltip-text-color, white);\n        padding: 8px;\n        border-radius: 2px;\n        @apply --paper-tooltip;\n      }\n\n      @keyframes keyFrameScaleUp {\n        0% {\n          transform: scale(0.0);\n        }\n        100% {\n          transform: scale(1.0);\n        }\n      }\n\n      @keyframes keyFrameScaleDown {\n        0% {\n          transform: scale(1.0);\n        }\n        100% {\n          transform: scale(0.0);\n        }\n      }\n\n      @keyframes keyFrameFadeInOpacity {\n        0% {\n          opacity: 0;\n        }\n        100% {\n          opacity: var(--paper-tooltip-opacity, 0.9);\n        }\n      }\n\n      @keyframes keyFrameFadeOutOpacity {\n        0% {\n          opacity: var(--paper-tooltip-opacity, 0.9);\n        }\n        100% {\n          opacity: 0;\n        }\n      }\n\n      @keyframes keyFrameSlideDownIn {\n        0% {\n          transform: translateY(-2000px);\n          opacity: 0;\n        }\n        10% {\n          opacity: 0.2;\n        }\n        100% {\n          transform: translateY(0);\n          opacity: var(--paper-tooltip-opacity, 0.9);\n        }\n      }\n\n      @keyframes keyFrameSlideDownOut {\n        0% {\n          transform: translateY(0);\n          opacity: var(--paper-tooltip-opacity, 0.9);\n        }\n        10% {\n          opacity: 0.2;\n        }\n        100% {\n          transform: translateY(-2000px);\n          opacity: 0;\n        }\n      }\n\n      .fade-in-animation {\n        opacity: 0;\n        animation-delay: var(--paper-tooltip-delay-in, 500ms);\n        animation-name: keyFrameFadeInOpacity;\n        animation-iteration-count: 1;\n        animation-timing-function: ease-in;\n        animation-duration: var(--paper-tooltip-duration-in, 500ms);\n        animation-fill-mode: forwards;\n        @apply --paper-tooltip-animation;\n      }\n\n      .fade-out-animation {\n        opacity: var(--paper-tooltip-opacity, 0.9);\n        animation-delay: var(--paper-tooltip-delay-out, 0ms);\n        animation-name: keyFrameFadeOutOpacity;\n        animation-iteration-count: 1;\n        animation-timing-function: ease-in;\n        animation-duration: var(--paper-tooltip-duration-out, 500ms);\n        animation-fill-mode: forwards;\n        @apply --paper-tooltip-animation;\n      }\n\n      .scale-up-animation {\n        transform: scale(0);\n        opacity: var(--paper-tooltip-opacity, 0.9);\n        animation-delay: var(--paper-tooltip-delay-in, 500ms);\n        animation-name: keyFrameScaleUp;\n        animation-iteration-count: 1;\n        animation-timing-function: ease-in;\n        animation-duration: var(--paper-tooltip-duration-in, 500ms);\n        animation-fill-mode: forwards;\n        @apply --paper-tooltip-animation;\n      }\n\n      .scale-down-animation {\n        transform: scale(1);\n        opacity: var(--paper-tooltip-opacity, 0.9);\n        animation-delay: var(--paper-tooltip-delay-out, 500ms);\n        animation-name: keyFrameScaleDown;\n        animation-iteration-count: 1;\n        animation-timing-function: ease-in;\n        animation-duration: var(--paper-tooltip-duration-out, 500ms);\n        animation-fill-mode: forwards;\n        @apply --paper-tooltip-animation;\n      }\n\n      .slide-down-animation {\n        transform: translateY(-2000px);\n        opacity: 0;\n        animation-delay: var(--paper-tooltip-delay-out, 500ms);\n        animation-name: keyFrameSlideDownIn;\n        animation-iteration-count: 1;\n        animation-timing-function: cubic-bezier(0.0, 0.0, 0.2, 1);\n        animation-duration: var(--paper-tooltip-duration-out, 500ms);\n        animation-fill-mode: forwards;\n        @apply --paper-tooltip-animation;\n      }\n\n      .slide-down-animation-out {\n        transform: translateY(0);\n        opacity: var(--paper-tooltip-opacity, 0.9);\n        animation-delay: var(--paper-tooltip-delay-out, 500ms);\n        animation-name: keyFrameSlideDownOut;\n        animation-iteration-count: 1;\n        animation-timing-function: cubic-bezier(0.4, 0.0, 1, 1);\n        animation-duration: var(--paper-tooltip-duration-out, 500ms);\n        animation-fill-mode: forwards;\n        @apply --paper-tooltip-animation;\n      }\n\n      .cancel-animation {\n        animation-delay: -30s !important;\n      }\n\n      /* Thanks IE 10. */\n\n      .hidden {\n        display: none !important;\n      }\n    </style>\n\n    <div id=\"tooltip\" class=\"hidden\">\n      <slot></slot>\n    </div>\n"]);

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
[Tooltips](https://www.google.com/design/spec/components/tooltips.html)
`<paper-tooltip>` is a label that appears on hover and focus when the user
hovers over an element with the cursor or with the keyboard. It will be centered
to an anchor element specified in the `for` attribute, or, if that doesn't
exist, centered to the parent node containing it.
Example:
    <div style="display:inline-block">
      <button>Click me!</button>
      <paper-tooltip>Tooltip text</paper-tooltip>
    </div>
    <div>
      <button id="btn">Click me!</button>
      <paper-tooltip for="btn">Tooltip text</paper-tooltip>
    </div>
The tooltip can be positioned on the top|bottom|left|right of the anchor using
the `position` attribute. The default position is bottom.
    <paper-tooltip for="btn" position="left">Tooltip text</paper-tooltip>
    <paper-tooltip for="btn" position="top">Tooltip text</paper-tooltip>

### Styling
The following custom properties and mixins are available for styling:
Custom property | Description | Default
----------------|-------------|----------
`--paper-tooltip-background` | The background color of the tooltip | `#616161`
`--paper-tooltip-opacity` | The opacity of the tooltip | `0.9`
`--paper-tooltip-text-color` | The text color of the tooltip | `white`
`--paper-tooltip` | Mixin applied to the tooltip | `{}`
`--paper-tooltip-delay-in` | Delay before tooltip starts to fade in | `500`
`--paper-tooltip-delay-out` | Delay before tooltip starts to fade out | `0`
`--paper-tooltip-duration-in` | Timing for animation when showing tooltip | `500`
`--paper-tooltip-duration-out` | Timing for animation when hiding tooltip | `0`
`--paper-tooltip-animation` | Mixin applied to the tooltip animation | `{}`
@group Paper Elements
@element paper-tooltip
@demo demo/index.html
*/

Object(_polymer_polymer_lib_legacy_polymer_fn_js__WEBPACK_IMPORTED_MODULE_1__[/* Polymer */ "a"])({
  _template: Object(_polymer_polymer_lib_utils_html_tag_js__WEBPACK_IMPORTED_MODULE_3__[/* html */ "a"])(_templateObject()),
  is: 'paper-tooltip',
  hostAttributes: {
    role: 'tooltip',
    tabindex: -1
  },
  properties: {
    /**
     * The id of the element that the tooltip is anchored to. This element
     * must be a sibling of the tooltip. If this property is not set,
     * then the tooltip will be centered to the parent node containing it.
     */
    "for": {
      type: String,
      observer: '_findTarget'
    },

    /**
     * Set this to true if you want to manually control when the tooltip
     * is shown or hidden.
     */
    manualMode: {
      type: Boolean,
      value: false,
      observer: '_manualModeChanged'
    },

    /**
     * Positions the tooltip to the top, right, bottom, left of its content.
     */
    position: {
      type: String,
      value: 'bottom'
    },

    /**
     * If true, no parts of the tooltip will ever be shown offscreen.
     */
    fitToVisibleBounds: {
      type: Boolean,
      value: false
    },

    /**
     * The spacing between the top of the tooltip and the element it is
     * anchored to.
     */
    offset: {
      type: Number,
      value: 14
    },

    /**
     * This property is deprecated, but left over so that it doesn't
     * break exiting code. Please use `offset` instead. If both `offset` and
     * `marginTop` are provided, `marginTop` will be ignored.
     * @deprecated since version 1.0.3
     */
    marginTop: {
      type: Number,
      value: 14
    },

    /**
     * The delay that will be applied before the `entry` animation is
     * played when showing the tooltip.
     */
    animationDelay: {
      type: Number,
      value: 500,
      observer: '_delayChange'
    },

    /**
     * The animation that will be played on entry.  This replaces the
     * deprecated animationConfig.  Entries here will override the
     * animationConfig settings.  You can enter your own animation
     * by setting it to the css class name.
     */
    animationEntry: {
      type: String,
      value: ''
    },

    /**
     * The animation that will be played on exit.  This replaces the
     * deprecated animationConfig.  Entries here will override the
     * animationConfig settings.  You can enter your own animation
     * by setting it to the css class name.
     */
    animationExit: {
      type: String,
      value: ''
    },

    /**
     * This property is deprecated.  Use --paper-tooltip-animation to change the
     * animation. The entry and exit animations that will be played when showing
     * and hiding the tooltip. If you want to override this, you must ensure
     * that your animationConfig has the exact format below.
     * @deprecated since version
     *
     * The entry and exit animations that will be played when showing and
     * hiding the tooltip. If you want to override this, you must ensure
     * that your animationConfig has the exact format below.
     */
    animationConfig: {
      type: Object,
      value: function value() {
        return {
          'entry': [{
            name: 'fade-in-animation',
            node: this,
            timing: {
              delay: 0
            }
          }],
          'exit': [{
            name: 'fade-out-animation',
            node: this
          }]
        };
      }
    },
    _showing: {
      type: Boolean,
      value: false
    }
  },
  listeners: {
    'webkitAnimationEnd': '_onAnimationEnd'
  },

  /**
   * Returns the target element that this tooltip is anchored to. It is
   * either the element given by the `for` attribute, or the immediate parent
   * of the tooltip.
   *
   * @type {Node}
   */
  get target() {
    var parentNode = Object(_polymer_polymer_lib_legacy_polymer_dom_js__WEBPACK_IMPORTED_MODULE_2__[/* dom */ "a"])(this).parentNode; // If the parentNode is a document fragment, then we need to use the host.

    var ownerRoot = Object(_polymer_polymer_lib_legacy_polymer_dom_js__WEBPACK_IMPORTED_MODULE_2__[/* dom */ "a"])(this).getOwnerRoot();
    var target;

    if (this["for"]) {
      target = Object(_polymer_polymer_lib_legacy_polymer_dom_js__WEBPACK_IMPORTED_MODULE_2__[/* dom */ "a"])(ownerRoot).querySelector('#' + this["for"]);
    } else {
      target = parentNode.nodeType == Node.DOCUMENT_FRAGMENT_NODE ? ownerRoot.host : parentNode;
    }

    return target;
  },

  /**
   * @return {void}
   */
  attached: function attached() {
    this._findTarget();
  },

  /**
   * @return {void}
   */
  detached: function detached() {
    if (!this.manualMode) this._removeListeners();
  },

  /**
   * Replaces Neon-Animation playAnimation - just calls show and hide.
   * @deprecated Use show and hide instead.
   * @param {string} type Either `entry` or `exit`
   */
  playAnimation: function playAnimation(type) {
    if (type === 'entry') {
      this.show();
    } else if (type === 'exit') {
      this.hide();
    }
  },

  /**
   * Cancels the animation and either fully shows or fully hides tooltip
   */
  cancelAnimation: function cancelAnimation() {
    // Short-cut and cancel all animations and hide
    this.$.tooltip.classList.add('cancel-animation');
  },

  /**
   * Shows the tooltip programatically
   * @return {void}
   */
  show: function show() {
    // If the tooltip is already showing, there's nothing to do.
    if (this._showing) return;

    if (Object(_polymer_polymer_lib_legacy_polymer_dom_js__WEBPACK_IMPORTED_MODULE_2__[/* dom */ "a"])(this).textContent.trim() === '') {
      // Check if effective children are also empty
      var allChildrenEmpty = true;
      var effectiveChildren = Object(_polymer_polymer_lib_legacy_polymer_dom_js__WEBPACK_IMPORTED_MODULE_2__[/* dom */ "a"])(this).getEffectiveChildNodes();

      for (var i = 0; i < effectiveChildren.length; i++) {
        if (effectiveChildren[i].textContent.trim() !== '') {
          allChildrenEmpty = false;
          break;
        }
      }

      if (allChildrenEmpty) {
        return;
      }
    }

    this._showing = true;
    this.$.tooltip.classList.remove('hidden');
    this.$.tooltip.classList.remove('cancel-animation');
    this.$.tooltip.classList.remove(this._getAnimationType('exit'));
    this.updatePosition();
    this._animationPlaying = true;
    this.$.tooltip.classList.add(this._getAnimationType('entry'));
  },

  /**
   * Hides the tooltip programatically
   * @return {void}
   */
  hide: function hide() {
    // If the tooltip is already hidden, there's nothing to do.
    if (!this._showing) {
      return;
    } // If the entry animation is still playing, don't try to play the exit
    // animation since this will reset the opacity to 1. Just end the animation.


    if (this._animationPlaying) {
      this._showing = false;

      this._cancelAnimation();

      return;
    } else {
      // Play Exit Animation
      this._onAnimationFinish();
    }

    this._showing = false;
    this._animationPlaying = true;
  },

  /**
   * @return {void}
   */
  updatePosition: function updatePosition() {
    if (!this._target || !this.offsetParent) return;
    var offset = this.offset; // If a marginTop has been provided by the user (pre 1.0.3), use it.

    if (this.marginTop != 14 && this.offset == 14) offset = this.marginTop;
    var parentRect = this.offsetParent.getBoundingClientRect();

    var targetRect = this._target.getBoundingClientRect();

    var thisRect = this.getBoundingClientRect();
    var horizontalCenterOffset = (targetRect.width - thisRect.width) / 2;
    var verticalCenterOffset = (targetRect.height - thisRect.height) / 2;
    var targetLeft = targetRect.left - parentRect.left;
    var targetTop = targetRect.top - parentRect.top;
    var tooltipLeft, tooltipTop;

    switch (this.position) {
      case 'top':
        tooltipLeft = targetLeft + horizontalCenterOffset;
        tooltipTop = targetTop - thisRect.height - offset;
        break;

      case 'bottom':
        tooltipLeft = targetLeft + horizontalCenterOffset;
        tooltipTop = targetTop + targetRect.height + offset;
        break;

      case 'left':
        tooltipLeft = targetLeft - thisRect.width - offset;
        tooltipTop = targetTop + verticalCenterOffset;
        break;

      case 'right':
        tooltipLeft = targetLeft + targetRect.width + offset;
        tooltipTop = targetTop + verticalCenterOffset;
        break;
    } // TODO(noms): This should use IronFitBehavior if possible.


    if (this.fitToVisibleBounds) {
      // Clip the left/right side
      if (parentRect.left + tooltipLeft + thisRect.width > window.innerWidth) {
        this.style.right = '0px';
        this.style.left = 'auto';
      } else {
        this.style.left = Math.max(0, tooltipLeft) + 'px';
        this.style.right = 'auto';
      } // Clip the top/bottom side.


      if (parentRect.top + tooltipTop + thisRect.height > window.innerHeight) {
        this.style.bottom = parentRect.height - targetTop + offset + 'px';
        this.style.top = 'auto';
      } else {
        this.style.top = Math.max(-parentRect.top, tooltipTop) + 'px';
        this.style.bottom = 'auto';
      }
    } else {
      this.style.left = tooltipLeft + 'px';
      this.style.top = tooltipTop + 'px';
    }
  },
  _addListeners: function _addListeners() {
    if (this._target) {
      this.listen(this._target, 'mouseenter', 'show');
      this.listen(this._target, 'focus', 'show');
      this.listen(this._target, 'mouseleave', 'hide');
      this.listen(this._target, 'blur', 'hide');
      this.listen(this._target, 'tap', 'hide');
    }

    this.listen(this.$.tooltip, 'animationend', '_onAnimationEnd');
    this.listen(this, 'mouseenter', 'hide');
  },
  _findTarget: function _findTarget() {
    if (!this.manualMode) this._removeListeners();
    this._target = this.target;
    if (!this.manualMode) this._addListeners();
  },
  _delayChange: function _delayChange(newValue) {
    // Only Update delay if different value set
    if (newValue !== 500) {
      this.updateStyles({
        '--paper-tooltip-delay-in': newValue + 'ms'
      });
    }
  },
  _manualModeChanged: function _manualModeChanged() {
    if (this.manualMode) this._removeListeners();else this._addListeners();
  },
  _cancelAnimation: function _cancelAnimation() {
    // Short-cut and cancel all animations and hide
    this.$.tooltip.classList.remove(this._getAnimationType('entry'));
    this.$.tooltip.classList.remove(this._getAnimationType('exit'));
    this.$.tooltip.classList.remove('cancel-animation');
    this.$.tooltip.classList.add('hidden');
  },
  _onAnimationFinish: function _onAnimationFinish() {
    if (this._showing) {
      this.$.tooltip.classList.remove(this._getAnimationType('entry'));
      this.$.tooltip.classList.remove('cancel-animation');
      this.$.tooltip.classList.add(this._getAnimationType('exit'));
    }
  },
  _onAnimationEnd: function _onAnimationEnd() {
    // If no longer showing add class hidden to completely hide tooltip
    this._animationPlaying = false;

    if (!this._showing) {
      this.$.tooltip.classList.remove(this._getAnimationType('exit'));
      this.$.tooltip.classList.add('hidden');
    }
  },
  _getAnimationType: function _getAnimationType(type) {
    // These properties have priority over animationConfig values
    if (type === 'entry' && this.animationEntry !== '') {
      return this.animationEntry;
    }

    if (type === 'exit' && this.animationExit !== '') {
      return this.animationExit;
    } // If no results then return the legacy value from animationConfig


    if (this.animationConfig[type] && typeof this.animationConfig[type][0].name === 'string') {
      // Checking Timing and Update if necessary - Legacy for animationConfig
      if (this.animationConfig[type][0].timing && this.animationConfig[type][0].timing.delay && this.animationConfig[type][0].timing.delay !== 0) {
        var timingDelay = this.animationConfig[type][0].timing.delay; // Has Timing Change - Update CSS

        if (type === 'entry') {
          this.updateStyles({
            '--paper-tooltip-delay-in': timingDelay + 'ms'
          });
        } else if (type === 'exit') {
          this.updateStyles({
            '--paper-tooltip-delay-out': timingDelay + 'ms'
          });
        }
      }

      return this.animationConfig[type][0].name;
    }
  },
  _removeListeners: function _removeListeners() {
    if (this._target) {
      this.unlisten(this._target, 'mouseenter', 'show');
      this.unlisten(this._target, 'focus', 'show');
      this.unlisten(this._target, 'mouseleave', 'hide');
      this.unlisten(this._target, 'blur', 'hide');
      this.unlisten(this._target, 'tap', 'hide');
    }

    this.unlisten(this.$.tooltip, 'animationend', '_onAnimationEnd');
    this.unlisten(this, 'mouseenter', 'hide');
  }
});

/***/ })
]]);