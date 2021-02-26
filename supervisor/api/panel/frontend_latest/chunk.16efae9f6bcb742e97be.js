/*! For license information please see chunk.16efae9f6bcb742e97be.js.LICENSE.txt */
(self.webpackChunkhome_assistant_frontend=self.webpackChunkhome_assistant_frontend||[]).push([[619],{7087:(e,t,i)=>{"use strict";i(1309),i(5660);var n=i(6110),r=i(8235),a=i(7139),o=i(8149),s=i(856);(0,a.k)({_template:s.d`
    <style>
      :host {
        display: inline-block;
        position: relative;
        width: 400px;
        border: 1px solid;
        padding: 2px;
        -moz-appearance: textarea;
        -webkit-appearance: textarea;
        overflow: hidden;
      }

      .mirror-text {
        visibility: hidden;
        word-wrap: break-word;
        @apply --iron-autogrow-textarea;
      }

      .fit {
        @apply --layout-fit;
      }

      textarea {
        position: relative;
        outline: none;
        border: none;
        resize: none;
        background: inherit;
        color: inherit;
        /* see comments in template */
        width: 100%;
        height: 100%;
        font-size: inherit;
        font-family: inherit;
        line-height: inherit;
        text-align: inherit;
        @apply --iron-autogrow-textarea;
      }

      textarea::-webkit-input-placeholder {
        @apply --iron-autogrow-textarea-placeholder;
      }

      textarea:-moz-placeholder {
        @apply --iron-autogrow-textarea-placeholder;
      }

      textarea::-moz-placeholder {
        @apply --iron-autogrow-textarea-placeholder;
      }

      textarea:-ms-input-placeholder {
        @apply --iron-autogrow-textarea-placeholder;
      }
    </style>

    <!-- the mirror sizes the input/textarea so it grows with typing -->
    <!-- use &#160; instead &nbsp; of to allow this element to be used in XHTML -->
    <div id="mirror" class="mirror-text" aria-hidden="true">&nbsp;</div>

    <!-- size the input/textarea with a div, because the textarea has intrinsic size in ff -->
    <div class="textarea-container fit">
      <textarea id="textarea" name\$="[[name]]" aria-label\$="[[label]]" autocomplete\$="[[autocomplete]]" autofocus\$="[[autofocus]]" inputmode\$="[[inputmode]]" placeholder\$="[[placeholder]]" readonly\$="[[readonly]]" required\$="[[required]]" disabled\$="[[disabled]]" rows\$="[[rows]]" minlength\$="[[minlength]]" maxlength\$="[[maxlength]]"></textarea>
    </div>
`,is:"iron-autogrow-textarea",behaviors:[r.x,n.a],properties:{value:{observer:"_valueChanged",type:String,notify:!0},bindValue:{observer:"_bindValueChanged",type:String,notify:!0},rows:{type:Number,value:1,observer:"_updateCached"},maxRows:{type:Number,value:0,observer:"_updateCached"},autocomplete:{type:String,value:"off"},autofocus:{type:Boolean,value:!1},inputmode:{type:String},placeholder:{type:String},readonly:{type:String},required:{type:Boolean},minlength:{type:Number},maxlength:{type:Number},label:{type:String}},listeners:{input:"_onInput"},get textarea(){return this.$.textarea},get selectionStart(){return this.$.textarea.selectionStart},get selectionEnd(){return this.$.textarea.selectionEnd},set selectionStart(e){this.$.textarea.selectionStart=e},set selectionEnd(e){this.$.textarea.selectionEnd=e},attached:function(){navigator.userAgent.match(/iP(?:[oa]d|hone)/)&&(this.$.textarea.style.marginLeft="-3px")},validate:function(){var e=this.$.textarea.validity.valid;return e&&(this.required&&""===this.value?e=!1:this.hasValidator()&&(e=r.x.validate.call(this,this.value))),this.invalid=!e,this.fire("iron-input-validate"),e},_bindValueChanged:function(e){this.value=e},_valueChanged:function(e){var t=this.textarea;t&&(t.value!==e&&(t.value=e||0===e?e:""),this.bindValue=e,this.$.mirror.innerHTML=this._valueForMirror(),this.fire("bind-value-changed",{value:this.bindValue}))},_onInput:function(e){var t=(0,o.vz)(e).path;this.value=t?t[0].value:e.target.value},_constrain:function(e){var t;for(e=e||[""],t=this.maxRows>0&&e.length>this.maxRows?e.slice(0,this.maxRows):e.slice(0);this.rows>0&&t.length<this.rows;)t.push("");return t.join("<br/>")+"&#160;"},_valueForMirror:function(){var e=this.textarea;if(e)return this.tokens=e&&e.value?e.value.replace(/&/gm,"&amp;").replace(/"/gm,"&quot;").replace(/'/gm,"&#39;").replace(/</gm,"&lt;").replace(/>/gm,"&gt;").split("\n"):[""],this._constrain(this.tokens)},_updateCached:function(){this.$.mirror.innerHTML=this._constrain(this.tokens)}})},5782:(e,t,i)=>{"use strict";i(1309),i(5660),i(19),i(7968);var n=i(7139),r=i(856),a=i(3760);(0,n.k)({_template:r.d`
    <style include="paper-item-shared-styles"></style>
    <style>
      :host {
        @apply --layout-horizontal;
        @apply --layout-center;
        @apply --paper-font-subhead;

        @apply --paper-item;
        @apply --paper-icon-item;
      }

      .content-icon {
        @apply --layout-horizontal;
        @apply --layout-center;

        width: var(--paper-item-icon-width, 56px);
        @apply --paper-item-icon;
      }
    </style>

    <div id="contentIcon" class="content-icon">
      <slot name="item-icon"></slot>
    </div>
    <slot></slot>
`,is:"paper-icon-item",behaviors:[a.U]})},1548:(e,t,i)=>{"use strict";i(5660),i(7956);var n=i(1309);const r={properties:{value:{type:Number,value:0,notify:!0,reflectToAttribute:!0},min:{type:Number,value:0,notify:!0},max:{type:Number,value:100,notify:!0},step:{type:Number,value:1,notify:!0},ratio:{type:Number,value:0,readOnly:!0,notify:!0}},observers:["_update(value, min, max, step)"],_calcRatio:function(e){return(this._clampValue(e)-this.min)/(this.max-this.min)},_clampValue:function(e){return Math.min(this.max,Math.max(this.min,this._calcStep(e)))},_calcStep:function(e){if(e=parseFloat(e),!this.step)return e;var t=Math.round((e-this.min)/this.step);return this.step<1?t/(1/this.step)+this.min:t*this.step+this.min},_validateValue:function(){var e=this._clampValue(this.value);return this.value=this.oldValue=isNaN(e)?this.oldValue:e,this.value!==e},_update:function(){this._validateValue(),this._setRatio(100*this._calcRatio(this.value))}};var a=i(7139),o=i(856);(0,a.k)({_template:o.d`
    <style>
      :host {
        display: block;
        width: 200px;
        position: relative;
        overflow: hidden;
      }

      :host([hidden]), [hidden] {
        display: none !important;
      }

      #progressContainer {
        @apply --paper-progress-container;
        position: relative;
      }

      #progressContainer,
      /* the stripe for the indeterminate animation*/
      .indeterminate::after {
        height: var(--paper-progress-height, 4px);
      }

      #primaryProgress,
      #secondaryProgress,
      .indeterminate::after {
        @apply --layout-fit;
      }

      #progressContainer,
      .indeterminate::after {
        background: var(--paper-progress-container-color, var(--google-grey-300));
      }

      :host(.transiting) #primaryProgress,
      :host(.transiting) #secondaryProgress {
        -webkit-transition-property: -webkit-transform;
        transition-property: transform;

        /* Duration */
        -webkit-transition-duration: var(--paper-progress-transition-duration, 0.08s);
        transition-duration: var(--paper-progress-transition-duration, 0.08s);

        /* Timing function */
        -webkit-transition-timing-function: var(--paper-progress-transition-timing-function, ease);
        transition-timing-function: var(--paper-progress-transition-timing-function, ease);

        /* Delay */
        -webkit-transition-delay: var(--paper-progress-transition-delay, 0s);
        transition-delay: var(--paper-progress-transition-delay, 0s);
      }

      #primaryProgress,
      #secondaryProgress {
        @apply --layout-fit;
        -webkit-transform-origin: left center;
        transform-origin: left center;
        -webkit-transform: scaleX(0);
        transform: scaleX(0);
        will-change: transform;
      }

      #primaryProgress {
        background: var(--paper-progress-active-color, var(--google-green-500));
      }

      #secondaryProgress {
        background: var(--paper-progress-secondary-color, var(--google-green-100));
      }

      :host([disabled]) #primaryProgress {
        background: var(--paper-progress-disabled-active-color, var(--google-grey-500));
      }

      :host([disabled]) #secondaryProgress {
        background: var(--paper-progress-disabled-secondary-color, var(--google-grey-300));
      }

      :host(:not([disabled])) #primaryProgress.indeterminate {
        -webkit-transform-origin: right center;
        transform-origin: right center;
        -webkit-animation: indeterminate-bar var(--paper-progress-indeterminate-cycle-duration, 2s) linear infinite;
        animation: indeterminate-bar var(--paper-progress-indeterminate-cycle-duration, 2s) linear infinite;
      }

      :host(:not([disabled])) #primaryProgress.indeterminate::after {
        content: "";
        -webkit-transform-origin: center center;
        transform-origin: center center;

        -webkit-animation: indeterminate-splitter var(--paper-progress-indeterminate-cycle-duration, 2s) linear infinite;
        animation: indeterminate-splitter var(--paper-progress-indeterminate-cycle-duration, 2s) linear infinite;
      }

      @-webkit-keyframes indeterminate-bar {
        0% {
          -webkit-transform: scaleX(1) translateX(-100%);
        }
        50% {
          -webkit-transform: scaleX(1) translateX(0%);
        }
        75% {
          -webkit-transform: scaleX(1) translateX(0%);
          -webkit-animation-timing-function: cubic-bezier(.28,.62,.37,.91);
        }
        100% {
          -webkit-transform: scaleX(0) translateX(0%);
        }
      }

      @-webkit-keyframes indeterminate-splitter {
        0% {
          -webkit-transform: scaleX(.75) translateX(-125%);
        }
        30% {
          -webkit-transform: scaleX(.75) translateX(-125%);
          -webkit-animation-timing-function: cubic-bezier(.42,0,.6,.8);
        }
        90% {
          -webkit-transform: scaleX(.75) translateX(125%);
        }
        100% {
          -webkit-transform: scaleX(.75) translateX(125%);
        }
      }

      @keyframes indeterminate-bar {
        0% {
          transform: scaleX(1) translateX(-100%);
        }
        50% {
          transform: scaleX(1) translateX(0%);
        }
        75% {
          transform: scaleX(1) translateX(0%);
          animation-timing-function: cubic-bezier(.28,.62,.37,.91);
        }
        100% {
          transform: scaleX(0) translateX(0%);
        }
      }

      @keyframes indeterminate-splitter {
        0% {
          transform: scaleX(.75) translateX(-125%);
        }
        30% {
          transform: scaleX(.75) translateX(-125%);
          animation-timing-function: cubic-bezier(.42,0,.6,.8);
        }
        90% {
          transform: scaleX(.75) translateX(125%);
        }
        100% {
          transform: scaleX(.75) translateX(125%);
        }
      }
    </style>

    <div id="progressContainer">
      <div id="secondaryProgress" hidden\$="[[_hideSecondaryProgress(secondaryRatio)]]"></div>
      <div id="primaryProgress"></div>
    </div>
`,is:"paper-progress",behaviors:[r],properties:{secondaryProgress:{type:Number,value:0},secondaryRatio:{type:Number,value:0,readOnly:!0},indeterminate:{type:Boolean,value:!1,observer:"_toggleIndeterminate"},disabled:{type:Boolean,value:!1,reflectToAttribute:!0,observer:"_disabledChanged"}},observers:["_progressChanged(secondaryProgress, value, min, max, indeterminate)"],hostAttributes:{role:"progressbar"},_toggleIndeterminate:function(e){this.toggleClass("indeterminate",e,this.$.primaryProgress)},_transformProgress:function(e,t){var i="scaleX("+t/100+")";e.style.transform=e.style.webkitTransform=i},_mainRatioChanged:function(e){this._transformProgress(this.$.primaryProgress,e)},_progressChanged:function(e,t,i,n,r){e=this._clampValue(e),t=this._clampValue(t);var a=100*this._calcRatio(e),o=100*this._calcRatio(t);this._setSecondaryRatio(a),this._transformProgress(this.$.secondaryProgress,a),this._transformProgress(this.$.primaryProgress,o),this.secondaryProgress=e,r?this.removeAttribute("aria-valuenow"):this.setAttribute("aria-valuenow",t),this.setAttribute("aria-valuemin",i),this.setAttribute("aria-valuemax",n)},_disabledChanged:function(e){this.setAttribute("aria-disabled",e?"true":"false")},_hideSecondaryProgress:function(e){return 0===e}});var s=i(8621),l=i(1006),u=i(9075),c=i(1668);const h=n.dy`
  <style>
    :host {
      @apply --layout;
      @apply --layout-justified;
      @apply --layout-center;
      width: 200px;
      cursor: default;
      -webkit-user-select: none;
      -moz-user-select: none;
      -ms-user-select: none;
      user-select: none;
      -webkit-tap-highlight-color: rgba(0, 0, 0, 0);
      --paper-progress-active-color: var(--paper-slider-active-color, var(--google-blue-700));
      --paper-progress-secondary-color: var(--paper-slider-secondary-color, var(--google-blue-300));
      --paper-progress-disabled-active-color: var(--paper-slider-disabled-active-color, var(--paper-grey-400));
      --paper-progress-disabled-secondary-color: var(--paper-slider-disabled-secondary-color, var(--paper-grey-400));
      --calculated-paper-slider-height: var(--paper-slider-height, 2px);
    }

    /* focus shows the ripple */
    :host(:focus) {
      outline: none;
    }

    /**
      * NOTE(keanulee): Though :host-context is not universally supported, some pages
      * still rely on paper-slider being flipped when dir="rtl" is set on body. For full
      * compatibility, dir="rtl" must be explicitly set on paper-slider.
      */
    :dir(rtl) #sliderContainer {
      -webkit-transform: scaleX(-1);
      transform: scaleX(-1);
    }

    /**
      * NOTE(keanulee): This is separate from the rule above because :host-context may
      * not be recognized.
      */
    :host([dir="rtl"]) #sliderContainer {
      -webkit-transform: scaleX(-1);
      transform: scaleX(-1);
    }

    /**
      * NOTE(keanulee): Needed to override the :host-context rule (where supported)
      * to support LTR sliders in RTL pages.
      */
    :host([dir="ltr"]) #sliderContainer {
      -webkit-transform: scaleX(1);
      transform: scaleX(1);
    }

    #sliderContainer {
      position: relative;
      width: 100%;
      height: calc(30px + var(--calculated-paper-slider-height));
      margin-left: calc(15px + var(--calculated-paper-slider-height)/2);
      margin-right: calc(15px + var(--calculated-paper-slider-height)/2);
    }

    #sliderContainer:focus {
      outline: 0;
    }

    #sliderContainer.editable {
      margin-top: 12px;
      margin-bottom: 12px;
    }

    .bar-container {
      position: absolute;
      top: 0;
      bottom: 0;
      left: 0;
      right: 0;
      overflow: hidden;
    }

    .ring > .bar-container {
      left: calc(5px + var(--calculated-paper-slider-height)/2);
      transition: left 0.18s ease;
    }

    .ring.expand.dragging > .bar-container {
      transition: none;
    }

    .ring.expand:not(.pin) > .bar-container {
      left: calc(8px + var(--calculated-paper-slider-height)/2);
    }

    #sliderBar {
      padding: 15px 0;
      width: 100%;
      background-color: var(--paper-slider-bar-color, transparent);
      --paper-progress-container-color: var(--paper-slider-container-color, var(--paper-grey-400));
      --paper-progress-height: var(--calculated-paper-slider-height);
    }

    .slider-markers {
      position: absolute;
      /* slider-knob is 30px + the slider-height so that the markers should start at a offset of 15px*/
      top: 15px;
      height: var(--calculated-paper-slider-height);
      left: 0;
      right: -1px;
      box-sizing: border-box;
      pointer-events: none;
      @apply --layout-horizontal;
    }

    .slider-marker {
      @apply --layout-flex;
    }
    .slider-markers::after,
    .slider-marker::after {
      content: "";
      display: block;
      margin-left: -1px;
      width: 2px;
      height: var(--calculated-paper-slider-height);
      border-radius: 50%;
      background-color: var(--paper-slider-markers-color, #000);
    }

    .slider-knob {
      position: absolute;
      left: 0;
      top: 0;
      margin-left: calc(-15px - var(--calculated-paper-slider-height)/2);
      width: calc(30px + var(--calculated-paper-slider-height));
      height: calc(30px + var(--calculated-paper-slider-height));
    }

    .transiting > .slider-knob {
      transition: left 0.08s ease;
    }

    .slider-knob:focus {
      outline: none;
    }

    .slider-knob.dragging {
      transition: none;
    }

    .snaps > .slider-knob.dragging {
      transition: -webkit-transform 0.08s ease;
      transition: transform 0.08s ease;
    }

    .slider-knob-inner {
      margin: 10px;
      width: calc(100% - 20px);
      height: calc(100% - 20px);
      background-color: var(--paper-slider-knob-color, var(--google-blue-700));
      border: 2px solid var(--paper-slider-knob-color, var(--google-blue-700));
      border-radius: 50%;

      -moz-box-sizing: border-box;
      box-sizing: border-box;

      transition-property: -webkit-transform, background-color, border;
      transition-property: transform, background-color, border;
      transition-duration: 0.18s;
      transition-timing-function: ease;
    }

    .expand:not(.pin) > .slider-knob > .slider-knob-inner {
      -webkit-transform: scale(1.5);
      transform: scale(1.5);
    }

    .ring > .slider-knob > .slider-knob-inner {
      background-color: var(--paper-slider-knob-start-color, transparent);
      border: 2px solid var(--paper-slider-knob-start-border-color, var(--paper-grey-400));
    }

    .slider-knob-inner::before {
      background-color: var(--paper-slider-pin-color, var(--google-blue-700));
    }

    .pin > .slider-knob > .slider-knob-inner::before {
      content: "";
      position: absolute;
      top: 0;
      left: 50%;
      margin-left: -13px;
      width: 26px;
      height: 26px;
      border-radius: 50% 50% 50% 0;

      -webkit-transform: rotate(-45deg) scale(0) translate(0);
      transform: rotate(-45deg) scale(0) translate(0);
    }

    .slider-knob-inner::before,
    .slider-knob-inner::after {
      transition: -webkit-transform .18s ease, background-color .18s ease;
      transition: transform .18s ease, background-color .18s ease;
    }

    .pin.ring > .slider-knob > .slider-knob-inner::before {
      background-color: var(--paper-slider-pin-start-color, var(--paper-grey-400));
    }

    .pin.expand > .slider-knob > .slider-knob-inner::before {
      -webkit-transform: rotate(-45deg) scale(1) translate(17px, -17px);
      transform: rotate(-45deg) scale(1) translate(17px, -17px);
    }

    .pin > .slider-knob > .slider-knob-inner::after {
      content: attr(value);
      position: absolute;
      top: 0;
      left: 50%;
      margin-left: -16px;
      width: 32px;
      height: 26px;
      text-align: center;
      color: var(--paper-slider-font-color, #fff);
      font-size: 10px;

      -webkit-transform: scale(0) translate(0);
      transform: scale(0) translate(0);
    }

    .pin.expand > .slider-knob > .slider-knob-inner::after {
      -webkit-transform: scale(1) translate(0, -17px);
      transform: scale(1) translate(0, -17px);
    }

    /* paper-input */
    .slider-input {
      width: 50px;
      overflow: hidden;
      --paper-input-container-input: {
        text-align: center;
        @apply --paper-slider-input-container-input;
      };
      @apply --paper-slider-input;
    }

    /* disabled state */
    #sliderContainer.disabled {
      pointer-events: none;
    }

    .disabled > .slider-knob > .slider-knob-inner {
      background-color: var(--paper-slider-disabled-knob-color, var(--paper-grey-400));
      border: 2px solid var(--paper-slider-disabled-knob-color, var(--paper-grey-400));
      -webkit-transform: scale3d(0.75, 0.75, 1);
      transform: scale3d(0.75, 0.75, 1);
    }

    .disabled.ring > .slider-knob > .slider-knob-inner {
      background-color: var(--paper-slider-knob-start-color, transparent);
      border: 2px solid var(--paper-slider-knob-start-border-color, var(--paper-grey-400));
    }

    paper-ripple {
      color: var(--paper-slider-knob-color, var(--google-blue-700));
    }
  </style>

  <div id="sliderContainer" class\$="[[_getClassNames(disabled, pin, snaps, immediateValue, min, expand, dragging, transiting, editable)]]">
    <div class="bar-container">
      <paper-progress disabled\$="[[disabled]]" id="sliderBar" aria-hidden="true" min="[[min]]" max="[[max]]" step="[[step]]" value="[[immediateValue]]" secondary-progress="[[secondaryProgress]]" on-down="_bardown" on-up="_resetKnob" on-track="_bartrack" on-tap="_barclick">
      </paper-progress>
    </div>

    <template is="dom-if" if="[[snaps]]">
      <div class="slider-markers">
        <template is="dom-repeat" items="[[markers]]">
          <div class="slider-marker"></div>
        </template>
      </div>
    </template>

    <div id="sliderKnob" class="slider-knob" on-down="_knobdown" on-up="_resetKnob" on-track="_onTrack" on-transitionend="_knobTransitionEnd">
        <div class="slider-knob-inner" value\$="[[immediateValue]]"></div>
    </div>
  </div>

  <template is="dom-if" if="[[editable]]">
    <paper-input id="input" type="number" step="[[step]]" min="[[min]]" max="[[max]]" class="slider-input" disabled\$="[[disabled]]" value="[[immediateValue]]" on-change="_changeValue" on-keydown="_inputKeyDown" no-label-float>
    </paper-input>
  </template>
`;h.setAttribute("strip-whitespace",""),(0,a.k)({_template:h,is:"paper-slider",behaviors:[s.G,l.V,u.B,r],properties:{value:{type:Number,value:0},snaps:{type:Boolean,value:!1,notify:!0},pin:{type:Boolean,value:!1,notify:!0},secondaryProgress:{type:Number,value:0,notify:!0,observer:"_secondaryProgressChanged"},editable:{type:Boolean,value:!1},immediateValue:{type:Number,value:0,readOnly:!0,notify:!0},maxMarkers:{type:Number,value:0,notify:!0},expand:{type:Boolean,value:!1,readOnly:!0},ignoreBarTouch:{type:Boolean,value:!1},dragging:{type:Boolean,value:!1,readOnly:!0,notify:!0},transiting:{type:Boolean,value:!1,readOnly:!0},markers:{type:Array,readOnly:!0,value:function(){return[]}}},observers:["_updateKnob(value, min, max, snaps, step)","_valueChanged(value)","_immediateValueChanged(immediateValue)","_updateMarkers(maxMarkers, min, max, snaps)"],hostAttributes:{role:"slider",tabindex:0},keyBindings:{left:"_leftKey",right:"_rightKey","down pagedown home":"_decrementKey","up pageup end":"_incrementKey"},ready:function(){this.ignoreBarTouch&&(0,c.BP)(this.$.sliderBar,"auto")},increment:function(){this.value=this._clampValue(this.value+this.step)},decrement:function(){this.value=this._clampValue(this.value-this.step)},_updateKnob:function(e,t,i,n,r){this.setAttribute("aria-valuemin",t),this.setAttribute("aria-valuemax",i),this.setAttribute("aria-valuenow",e),this._positionKnob(100*this._calcRatio(e))},_valueChanged:function(){this.fire("value-change",{composed:!0})},_immediateValueChanged:function(){this.dragging?this.fire("immediate-value-change",{composed:!0}):this.value=this.immediateValue},_secondaryProgressChanged:function(){this.secondaryProgress=this._clampValue(this.secondaryProgress)},_expandKnob:function(){this._setExpand(!0)},_resetKnob:function(){this.cancelDebouncer("expandKnob"),this._setExpand(!1)},_positionKnob:function(e){this._setImmediateValue(this._calcStep(this._calcKnobPosition(e))),this._setRatio(100*this._calcRatio(this.immediateValue)),this.$.sliderKnob.style.left=this.ratio+"%",this.dragging&&(this._knobstartx=this.ratio*this._w/100,this.translate3d(0,0,0,this.$.sliderKnob))},_calcKnobPosition:function(e){return(this.max-this.min)*e/100+this.min},_onTrack:function(e){switch(e.stopPropagation(),e.detail.state){case"start":this._trackStart(e);break;case"track":this._trackX(e);break;case"end":this._trackEnd()}},_trackStart:function(e){this._setTransiting(!1),this._w=this.$.sliderBar.offsetWidth,this._x=this.ratio*this._w/100,this._startx=this._x,this._knobstartx=this._startx,this._minx=-this._startx,this._maxx=this._w-this._startx,this.$.sliderKnob.classList.add("dragging"),this._setDragging(!0)},_trackX:function(e){this.dragging||this._trackStart(e);var t=this._isRTL?-1:1,i=Math.min(this._maxx,Math.max(this._minx,e.detail.dx*t));this._x=this._startx+i;var n=this._calcStep(this._calcKnobPosition(this._x/this._w*100));this._setImmediateValue(n);var r=this._calcRatio(this.immediateValue)*this._w-this._knobstartx;this.translate3d(r+"px",0,0,this.$.sliderKnob)},_trackEnd:function(){var e=this.$.sliderKnob.style;this.$.sliderKnob.classList.remove("dragging"),this._setDragging(!1),this._resetKnob(),this.value=this.immediateValue,e.transform=e.webkitTransform="",this.fire("change",{composed:!0})},_knobdown:function(e){this._expandKnob(),e.preventDefault(),this.focus()},_bartrack:function(e){this._allowBarEvent(e)&&this._onTrack(e)},_barclick:function(e){this._w=this.$.sliderBar.offsetWidth;var t=this.$.sliderBar.getBoundingClientRect(),i=(e.detail.x-t.left)/this._w*100;this._isRTL&&(i=100-i);var n=this.ratio;this._setTransiting(!0),this._positionKnob(i),n===this.ratio&&this._setTransiting(!1),this.async((function(){this.fire("change",{composed:!0})})),e.preventDefault(),this.focus()},_bardown:function(e){this._allowBarEvent(e)&&(this.debounce("expandKnob",this._expandKnob,60),this._barclick(e))},_knobTransitionEnd:function(e){e.target===this.$.sliderKnob&&this._setTransiting(!1)},_updateMarkers:function(e,t,i,n){n||this._setMarkers([]);var r=Math.round((i-t)/this.step);r>e&&(r=e),(r<0||!isFinite(r))&&(r=0),this._setMarkers(new Array(r))},_mergeClasses:function(e){return Object.keys(e).filter((function(t){return e[t]})).join(" ")},_getClassNames:function(){return this._mergeClasses({disabled:this.disabled,pin:this.pin,snaps:this.snaps,ring:this.immediateValue<=this.min,expand:this.expand,dragging:this.dragging,transiting:this.transiting,editable:this.editable})},_allowBarEvent:function(e){return!this.ignoreBarTouch||e.detail.sourceEvent instanceof MouseEvent},get _isRTL(){return void 0===this.__isRTL&&(this.__isRTL="rtl"===window.getComputedStyle(this).direction),this.__isRTL},_leftKey:function(e){this._isRTL?this._incrementKey(e):this._decrementKey(e)},_rightKey:function(e){this._isRTL?this._decrementKey(e):this._incrementKey(e)},_incrementKey:function(e){this.disabled||("end"===e.detail.key?this.value=this.max:this.increment(),this.fire("change"),e.preventDefault())},_decrementKey:function(e){this.disabled||("home"===e.detail.key?this.value=this.min:this.decrement(),this.fire("change"),e.preventDefault())},_changeValue:function(e){this.value=e.target.value,this.fire("change",{composed:!0})},_inputKeyDown:function(e){e.stopPropagation()},_createRipple:function(){return this._rippleContainer=this.$.sliderKnob,u.S._createRipple.call(this)},_focusedChanged:function(e){e&&this.ensureRipple(),this.hasRipple()&&(this._ripple.style.display=e?"":"none",this._ripple.holdDown=e)}})},1107:(e,t,i)=>{"use strict";i.d(t,{Ud:()=>h});const n=Symbol("Comlink.proxy"),r=Symbol("Comlink.endpoint"),a=Symbol("Comlink.releaseProxy"),o=Symbol("Comlink.thrown"),s=e=>"object"==typeof e&&null!==e||"function"==typeof e,l=new Map([["proxy",{canHandle:e=>s(e)&&e[n],serialize(e){const{port1:t,port2:i}=new MessageChannel;return u(e,t),[i,[i]]},deserialize:e=>(e.start(),h(e))}],["throw",{canHandle:e=>s(e)&&o in e,serialize({value:e}){let t;return t=e instanceof Error?{isError:!0,value:{message:e.message,name:e.name,stack:e.stack}}:{isError:!1,value:e},[t,[]]},deserialize(e){if(e.isError)throw Object.assign(new Error(e.value.message),e.value);throw e.value}}]]);function u(e,t=self){t.addEventListener("message",(function i(r){if(!r||!r.data)return;const{id:a,type:s,path:l}=Object.assign({path:[]},r.data),h=(r.data.argumentList||[]).map(_);let d;try{const t=l.slice(0,-1).reduce(((e,t)=>e[t]),e),i=l.reduce(((e,t)=>e[t]),e);switch(s){case 0:d=i;break;case 1:t[l.slice(-1)[0]]=_(r.data.value),d=!0;break;case 2:d=i.apply(t,h);break;case 3:d=function(e){return Object.assign(e,{[n]:!0})}(new i(...h));break;case 4:{const{port1:t,port2:i}=new MessageChannel;u(e,i),d=function(e,t){return m.set(e,t),e}(t,[t])}break;case 5:d=void 0}}catch(e){d={value:e,[o]:0}}Promise.resolve(d).catch((e=>({value:e,[o]:0}))).then((e=>{const[n,r]=g(e);t.postMessage(Object.assign(Object.assign({},n),{id:a}),r),5===s&&(t.removeEventListener("message",i),c(t))}))})),t.start&&t.start()}function c(e){(function(e){return"MessagePort"===e.constructor.name})(e)&&e.close()}function h(e,t){return p(e,[],t)}function d(e){if(e)throw new Error("Proxy has been released and is not useable")}function p(e,t=[],i=function(){}){let n=!1;const o=new Proxy(i,{get(i,r){if(d(n),r===a)return()=>v(e,{type:5,path:t.map((e=>e.toString()))}).then((()=>{c(e),n=!0}));if("then"===r){if(0===t.length)return{then:()=>o};const i=v(e,{type:0,path:t.map((e=>e.toString()))}).then(_);return i.then.bind(i)}return p(e,[...t,r])},set(i,r,a){d(n);const[o,s]=g(a);return v(e,{type:1,path:[...t,r].map((e=>e.toString())),value:o},s).then(_)},apply(i,a,o){d(n);const s=t[t.length-1];if(s===r)return v(e,{type:4}).then(_);if("bind"===s)return p(e,t.slice(0,-1));const[l,u]=f(o);return v(e,{type:2,path:t.map((e=>e.toString())),argumentList:l},u).then(_)},construct(i,r){d(n);const[a,o]=f(r);return v(e,{type:3,path:t.map((e=>e.toString())),argumentList:a},o).then(_)}});return o}function f(e){const t=e.map(g);return[t.map((e=>e[0])),(i=t.map((e=>e[1])),Array.prototype.concat.apply([],i))];var i}const m=new WeakMap;function g(e){for(const[t,i]of l)if(i.canHandle(e)){const[n,r]=i.serialize(e);return[{type:3,name:t,value:n},r]}return[{type:0,value:e},m.get(e)||[]]}function _(e){switch(e.type){case 3:return l.get(e.name).deserialize(e.value);case 0:return e.value}}function v(e,t,i){return new Promise((n=>{const r=new Array(4).fill(0).map((()=>Math.floor(Math.random()*Number.MAX_SAFE_INTEGER).toString(16))).join("-");e.addEventListener("message",(function t(i){i.data&&i.data.id&&i.data.id===r&&(e.removeEventListener("message",t),n(i.data))})),e.start&&e.start(),e.postMessage(Object.assign({id:r},t),i)}))}},1740:()=>{var e,t,i;t={},i={},function(e,t){function i(){this._delay=0,this._endDelay=0,this._fill="none",this._iterationStart=0,this._iterations=1,this._duration=0,this._playbackRate=1,this._direction="normal",this._easing="linear",this._easingFunction=d}function n(){return e.isDeprecated("Invalid timing inputs","2016-03-02","TypeError exceptions will be thrown instead.",!0)}function r(t,n,r){var a=new i;return n&&(a.fill="both",a.duration="auto"),"number"!=typeof t||isNaN(t)?void 0!==t&&Object.getOwnPropertyNames(t).forEach((function(i){if("auto"!=t[i]){if(("number"==typeof a[i]||"duration"==i)&&("number"!=typeof t[i]||isNaN(t[i])))return;if("fill"==i&&-1==c.indexOf(t[i]))return;if("direction"==i&&-1==h.indexOf(t[i]))return;if("playbackRate"==i&&1!==t[i]&&e.isDeprecated("AnimationEffectTiming.playbackRate","2014-11-28","Use Animation.playbackRate instead."))return;a[i]=t[i]}})):a.duration=t,a}function a(e,t,i,n){return e<0||e>1||i<0||i>1?d:function(r){function a(e,t,i){return 3*e*(1-i)*(1-i)*i+3*t*(1-i)*i*i+i*i*i}if(r<=0){var o=0;return e>0?o=t/e:!t&&i>0&&(o=n/i),o*r}if(r>=1){var s=0;return i<1?s=(n-1)/(i-1):1==i&&e<1&&(s=(t-1)/(e-1)),1+s*(r-1)}for(var l=0,u=1;l<u;){var c=(l+u)/2,h=a(e,i,c);if(Math.abs(r-h)<1e-5)return a(t,n,c);h<r?l=c:u=c}return a(t,n,c)}}function o(e,t){return function(i){if(i>=1)return 1;var n=1/e;return(i+=t*n)-i%n}}function s(e){_||(_=document.createElement("div").style),_.animationTimingFunction="",_.animationTimingFunction=e;var t=_.animationTimingFunction;if(""==t&&n())throw new TypeError(e+" is not a valid value for easing");return t}function l(e){if("linear"==e)return d;var t=b.exec(e);if(t)return a.apply(this,t.slice(1).map(Number));var i=y.exec(e);if(i)return o(Number(i[1]),m);var n=w.exec(e);return n?o(Number(n[1]),{start:p,middle:f,end:m}[n[2]]):g[e]||d}function u(e,t,i){if(null==t)return x;var n=i.delay+e+i.endDelay;return t<Math.min(i.delay,n)?k:t>=Math.min(i.delay+e,n)?T:E}var c="backwards|forwards|both|none".split("|"),h="reverse|alternate|alternate-reverse".split("|"),d=function(e){return e};i.prototype={_setMember:function(t,i){this["_"+t]=i,this._effect&&(this._effect._timingInput[t]=i,this._effect._timing=e.normalizeTimingInput(this._effect._timingInput),this._effect.activeDuration=e.calculateActiveDuration(this._effect._timing),this._effect._animation&&this._effect._animation._rebuildUnderlyingAnimation())},get playbackRate(){return this._playbackRate},set delay(e){this._setMember("delay",e)},get delay(){return this._delay},set endDelay(e){this._setMember("endDelay",e)},get endDelay(){return this._endDelay},set fill(e){this._setMember("fill",e)},get fill(){return this._fill},set iterationStart(e){if((isNaN(e)||e<0)&&n())throw new TypeError("iterationStart must be a non-negative number, received: "+e);this._setMember("iterationStart",e)},get iterationStart(){return this._iterationStart},set duration(e){if("auto"!=e&&(isNaN(e)||e<0)&&n())throw new TypeError("duration must be non-negative or auto, received: "+e);this._setMember("duration",e)},get duration(){return this._duration},set direction(e){this._setMember("direction",e)},get direction(){return this._direction},set easing(e){this._easingFunction=l(s(e)),this._setMember("easing",e)},get easing(){return this._easing},set iterations(e){if((isNaN(e)||e<0)&&n())throw new TypeError("iterations must be non-negative, received: "+e);this._setMember("iterations",e)},get iterations(){return this._iterations}};var p=1,f=.5,m=0,g={ease:a(.25,.1,.25,1),"ease-in":a(.42,0,1,1),"ease-out":a(0,0,.58,1),"ease-in-out":a(.42,0,.58,1),"step-start":o(1,p),"step-middle":o(1,f),"step-end":o(1,m)},_=null,v="\\s*(-?\\d+\\.?\\d*|-?\\.\\d+)\\s*",b=new RegExp("cubic-bezier\\("+v+","+v+","+v+","+v+"\\)"),y=/steps\(\s*(\d+)\s*\)/,w=/steps\(\s*(\d+)\s*,\s*(start|middle|end)\s*\)/,x=0,k=1,T=2,E=3;e.cloneTimingInput=function(e){if("number"==typeof e)return e;var t={};for(var i in e)t[i]=e[i];return t},e.makeTiming=r,e.numericTimingToObject=function(e){return"number"==typeof e&&(e=isNaN(e)?{duration:0}:{duration:e}),e},e.normalizeTimingInput=function(t,i){return r(t=e.numericTimingToObject(t),i)},e.calculateActiveDuration=function(e){return Math.abs(function(e){return 0===e.duration||0===e.iterations?0:e.duration*e.iterations}(e)/e.playbackRate)},e.calculateIterationProgress=function(e,t,i){var n=u(e,t,i),r=function(e,t,i,n,r){switch(n){case k:return"backwards"==t||"both"==t?0:null;case E:return i-r;case T:return"forwards"==t||"both"==t?e:null;case x:return null}}(e,i.fill,t,n,i.delay);if(null===r)return null;var a=function(e,t,i,n,r){var a=r;return 0===e?t!==k&&(a+=i):a+=n/e,a}(i.duration,n,i.iterations,r,i.iterationStart),o=function(e,t,i,n,r,a){var o=e===1/0?t%1:e%1;return 0!==o||i!==T||0===n||0===r&&0!==a||(o=1),o}(a,i.iterationStart,n,i.iterations,r,i.duration),s=function(e,t,i,n){return e===T&&t===1/0?1/0:1===i?Math.floor(n)-1:Math.floor(n)}(n,i.iterations,o,a),l=function(e,t,i){var n=e;if("normal"!==e&&"reverse"!==e){var r=t;"alternate-reverse"===e&&(r+=1),n="normal",r!==1/0&&r%2!=0&&(n="reverse")}return"normal"===n?i:1-i}(i.direction,s,o);return i._easingFunction(l)},e.calculatePhase=u,e.normalizeEasing=s,e.parseEasingFunction=l}(e={}),function(e,t){function i(e,t){return e in l&&l[e][t]||t}function n(e,t,n){if(!function(e){return"display"===e||0===e.lastIndexOf("animation",0)||0===e.lastIndexOf("transition",0)}(e)){var r=a[e];if(r)for(var s in o.style[e]=t,r){var l=r[s],u=o.style[l];n[l]=i(l,u)}else n[e]=i(e,t)}}function r(e){var t=[];for(var i in e)if(!(i in["easing","offset","composite"])){var n=e[i];Array.isArray(n)||(n=[n]);for(var r,a=n.length,o=0;o<a;o++)(r={}).offset="offset"in e?e.offset:1==a?1:o/(a-1),"easing"in e&&(r.easing=e.easing),"composite"in e&&(r.composite=e.composite),r[i]=n[o],t.push(r)}return t.sort((function(e,t){return e.offset-t.offset})),t}var a={background:["backgroundImage","backgroundPosition","backgroundSize","backgroundRepeat","backgroundAttachment","backgroundOrigin","backgroundClip","backgroundColor"],border:["borderTopColor","borderTopStyle","borderTopWidth","borderRightColor","borderRightStyle","borderRightWidth","borderBottomColor","borderBottomStyle","borderBottomWidth","borderLeftColor","borderLeftStyle","borderLeftWidth"],borderBottom:["borderBottomWidth","borderBottomStyle","borderBottomColor"],borderColor:["borderTopColor","borderRightColor","borderBottomColor","borderLeftColor"],borderLeft:["borderLeftWidth","borderLeftStyle","borderLeftColor"],borderRadius:["borderTopLeftRadius","borderTopRightRadius","borderBottomRightRadius","borderBottomLeftRadius"],borderRight:["borderRightWidth","borderRightStyle","borderRightColor"],borderTop:["borderTopWidth","borderTopStyle","borderTopColor"],borderWidth:["borderTopWidth","borderRightWidth","borderBottomWidth","borderLeftWidth"],flex:["flexGrow","flexShrink","flexBasis"],font:["fontFamily","fontSize","fontStyle","fontVariant","fontWeight","lineHeight"],margin:["marginTop","marginRight","marginBottom","marginLeft"],outline:["outlineColor","outlineStyle","outlineWidth"],padding:["paddingTop","paddingRight","paddingBottom","paddingLeft"]},o=document.createElementNS("http://www.w3.org/1999/xhtml","div"),s={thin:"1px",medium:"3px",thick:"5px"},l={borderBottomWidth:s,borderLeftWidth:s,borderRightWidth:s,borderTopWidth:s,fontSize:{"xx-small":"60%","x-small":"75%",small:"89%",medium:"100%",large:"120%","x-large":"150%","xx-large":"200%"},fontWeight:{normal:"400",bold:"700"},outlineWidth:s,textShadow:{none:"0px 0px 0px transparent"},boxShadow:{none:"0px 0px 0px 0px transparent"}};e.convertToArrayForm=r,e.normalizeKeyframes=function(t){if(null==t)return[];window.Symbol&&Symbol.iterator&&Array.prototype.from&&t[Symbol.iterator]&&(t=Array.from(t)),Array.isArray(t)||(t=r(t));for(var i=t.map((function(t){var i={};for(var r in t){var a=t[r];if("offset"==r){if(null!=a){if(a=Number(a),!isFinite(a))throw new TypeError("Keyframe offsets must be numbers.");if(a<0||a>1)throw new TypeError("Keyframe offsets must be between 0 and 1.")}}else if("composite"==r){if("add"==a||"accumulate"==a)throw{type:DOMException.NOT_SUPPORTED_ERR,name:"NotSupportedError",message:"add compositing is not supported"};if("replace"!=a)throw new TypeError("Invalid composite mode "+a+".")}else a="easing"==r?e.normalizeEasing(a):""+a;n(r,a,i)}return null==i.offset&&(i.offset=null),null==i.easing&&(i.easing="linear"),i})),a=!0,o=-1/0,s=0;s<i.length;s++){var l=i[s].offset;if(null!=l){if(l<o)throw new TypeError("Keyframes are not loosely sorted by offset. Sort or specify offsets.");o=l}else a=!1}return i=i.filter((function(e){return e.offset>=0&&e.offset<=1})),a||function(){var e=i.length;null==i[e-1].offset&&(i[e-1].offset=1),e>1&&null==i[0].offset&&(i[0].offset=0);for(var t=0,n=i[0].offset,r=1;r<e;r++){var a=i[r].offset;if(null!=a){for(var o=1;o<r-t;o++)i[t+o].offset=n+(a-n)*o/(r-t);t=r,n=a}}}(),i}}(e),function(e){var t={};e.isDeprecated=function(e,i,n,r){var a=r?"are":"is",o=new Date,s=new Date(i);return s.setMonth(s.getMonth()+3),!(o<s&&(e in t||console.warn("Web Animations: "+e+" "+a+" deprecated and will stop working on "+s.toDateString()+". "+n),t[e]=!0,1))},e.deprecated=function(t,i,n,r){var a=r?"are":"is";if(e.isDeprecated(t,i,n,r))throw new Error(t+" "+a+" no longer supported. "+n)}}(e),function(){if(document.documentElement.animate){var i=document.documentElement.animate([],0),n=!0;if(i&&(n=!1,"play|currentTime|pause|reverse|playbackRate|cancel|finish|startTime|playState".split("|").forEach((function(e){void 0===i[e]&&(n=!0)}))),!n)return}!function(e,t,i){t.convertEffectInput=function(i){var n=function(e){for(var t={},i=0;i<e.length;i++)for(var n in e[i])if("offset"!=n&&"easing"!=n&&"composite"!=n){var r={offset:e[i].offset,easing:e[i].easing,value:e[i][n]};t[n]=t[n]||[],t[n].push(r)}for(var a in t){var o=t[a];if(0!=o[0].offset||1!=o[o.length-1].offset)throw{type:DOMException.NOT_SUPPORTED_ERR,name:"NotSupportedError",message:"Partial keyframes are not supported"}}return t}(e.normalizeKeyframes(i)),r=function(i){var n=[];for(var r in i)for(var a=i[r],o=0;o<a.length-1;o++){var s=o,l=o+1,u=a[s].offset,c=a[l].offset,h=u,d=c;0==o&&(h=-1/0,0==c&&(l=s)),o==a.length-2&&(d=1/0,1==u&&(s=l)),n.push({applyFrom:h,applyTo:d,startOffset:a[s].offset,endOffset:a[l].offset,easingFunction:e.parseEasingFunction(a[s].easing),property:r,interpolation:t.propertyInterpolation(r,a[s].value,a[l].value)})}return n.sort((function(e,t){return e.startOffset-t.startOffset})),n}(n);return function(e,i){if(null!=i)r.filter((function(e){return i>=e.applyFrom&&i<e.applyTo})).forEach((function(n){var r=i-n.startOffset,a=n.endOffset-n.startOffset,o=0==a?0:n.easingFunction(r/a);t.apply(e,n.property,n.interpolation(o))}));else for(var a in n)"offset"!=a&&"easing"!=a&&"composite"!=a&&t.clear(e,a)}}}(e,t),function(e,t,i){function n(e){return e.replace(/-(.)/g,(function(e,t){return t.toUpperCase()}))}function r(e,t,i){a[i]=a[i]||[],a[i].push([e,t])}var a={};t.addPropertiesHandler=function(e,t,i){for(var a=0;a<i.length;a++)r(e,t,n(i[a]))};var o={backgroundColor:"transparent",backgroundPosition:"0% 0%",borderBottomColor:"currentColor",borderBottomLeftRadius:"0px",borderBottomRightRadius:"0px",borderBottomWidth:"3px",borderLeftColor:"currentColor",borderLeftWidth:"3px",borderRightColor:"currentColor",borderRightWidth:"3px",borderSpacing:"2px",borderTopColor:"currentColor",borderTopLeftRadius:"0px",borderTopRightRadius:"0px",borderTopWidth:"3px",bottom:"auto",clip:"rect(0px, 0px, 0px, 0px)",color:"black",fontSize:"100%",fontWeight:"400",height:"auto",left:"auto",letterSpacing:"normal",lineHeight:"120%",marginBottom:"0px",marginLeft:"0px",marginRight:"0px",marginTop:"0px",maxHeight:"none",maxWidth:"none",minHeight:"0px",minWidth:"0px",opacity:"1.0",outlineColor:"invert",outlineOffset:"0px",outlineWidth:"3px",paddingBottom:"0px",paddingLeft:"0px",paddingRight:"0px",paddingTop:"0px",right:"auto",strokeDasharray:"none",strokeDashoffset:"0px",textIndent:"0px",textShadow:"0px 0px 0px transparent",top:"auto",transform:"",verticalAlign:"0px",visibility:"visible",width:"auto",wordSpacing:"normal",zIndex:"auto"};t.propertyInterpolation=function(i,r,s){var l=i;/-/.test(i)&&!e.isDeprecated("Hyphenated property names","2016-03-22","Use camelCase instead.",!0)&&(l=n(i)),"initial"!=r&&"initial"!=s||("initial"==r&&(r=o[l]),"initial"==s&&(s=o[l]));for(var u=r==s?[]:a[l],c=0;u&&c<u.length;c++){var h=u[c][0](r),d=u[c][0](s);if(void 0!==h&&void 0!==d){var p=u[c][1](h,d);if(p){var f=t.Interpolation.apply(null,p);return function(e){return 0==e?r:1==e?s:f(e)}}}}return t.Interpolation(!1,!0,(function(e){return e?s:r}))}}(e,t),function(e,t,i){t.KeyframeEffect=function(i,n,r,a){var o,s=function(t){var i=e.calculateActiveDuration(t),n=function(n){return e.calculateIterationProgress(i,n,t)};return n._totalDuration=t.delay+i+t.endDelay,n}(e.normalizeTimingInput(r)),l=t.convertEffectInput(n),u=function(){l(i,o)};return u._update=function(e){return null!==(o=s(e))},u._clear=function(){l(i,null)},u._hasSameTarget=function(e){return i===e},u._target=i,u._totalDuration=s._totalDuration,u._id=a,u}}(e,t),function(e,t){e.apply=function(t,i,n){t.style[e.propertyName(i)]=n},e.clear=function(t,i){t.style[e.propertyName(i)]=""}}(t),function(e){window.Element.prototype.animate=function(t,i){var n="";return i&&i.id&&(n=i.id),e.timeline._play(e.KeyframeEffect(this,t,i,n))}}(t),function(e,t){function i(e,t,n){if("number"==typeof e&&"number"==typeof t)return e*(1-n)+t*n;if("boolean"==typeof e&&"boolean"==typeof t)return n<.5?e:t;if(e.length==t.length){for(var r=[],a=0;a<e.length;a++)r.push(i(e[a],t[a],n));return r}throw"Mismatched interpolation arguments "+e+":"+t}e.Interpolation=function(e,t,n){return function(r){return n(i(e,t,r))}}}(t),function(e,t,i){e.sequenceNumber=0;var n=function(e,t,i){this.target=e,this.currentTime=t,this.timelineTime=i,this.type="finish",this.bubbles=!1,this.cancelable=!1,this.currentTarget=e,this.defaultPrevented=!1,this.eventPhase=Event.AT_TARGET,this.timeStamp=Date.now()};t.Animation=function(t){this.id="",t&&t._id&&(this.id=t._id),this._sequenceNumber=e.sequenceNumber++,this._currentTime=0,this._startTime=null,this._paused=!1,this._playbackRate=1,this._inTimeline=!0,this._finishedFlag=!0,this.onfinish=null,this._finishHandlers=[],this._effect=t,this._inEffect=this._effect._update(0),this._idle=!0,this._currentTimePending=!1},t.Animation.prototype={_ensureAlive:function(){this.playbackRate<0&&0===this.currentTime?this._inEffect=this._effect._update(-1):this._inEffect=this._effect._update(this.currentTime),this._inTimeline||!this._inEffect&&this._finishedFlag||(this._inTimeline=!0,t.timeline._animations.push(this))},_tickCurrentTime:function(e,t){e!=this._currentTime&&(this._currentTime=e,this._isFinished&&!t&&(this._currentTime=this._playbackRate>0?this._totalDuration:0),this._ensureAlive())},get currentTime(){return this._idle||this._currentTimePending?null:this._currentTime},set currentTime(e){e=+e,isNaN(e)||(t.restart(),this._paused||null==this._startTime||(this._startTime=this._timeline.currentTime-e/this._playbackRate),this._currentTimePending=!1,this._currentTime!=e&&(this._idle&&(this._idle=!1,this._paused=!0),this._tickCurrentTime(e,!0),t.applyDirtiedAnimation(this)))},get startTime(){return this._startTime},set startTime(e){e=+e,isNaN(e)||this._paused||this._idle||(this._startTime=e,this._tickCurrentTime((this._timeline.currentTime-this._startTime)*this.playbackRate),t.applyDirtiedAnimation(this))},get playbackRate(){return this._playbackRate},set playbackRate(e){if(e!=this._playbackRate){var i=this.currentTime;this._playbackRate=e,this._startTime=null,"paused"!=this.playState&&"idle"!=this.playState&&(this._finishedFlag=!1,this._idle=!1,this._ensureAlive(),t.applyDirtiedAnimation(this)),null!=i&&(this.currentTime=i)}},get _isFinished(){return!this._idle&&(this._playbackRate>0&&this._currentTime>=this._totalDuration||this._playbackRate<0&&this._currentTime<=0)},get _totalDuration(){return this._effect._totalDuration},get playState(){return this._idle?"idle":null==this._startTime&&!this._paused&&0!=this.playbackRate||this._currentTimePending?"pending":this._paused?"paused":this._isFinished?"finished":"running"},_rewind:function(){if(this._playbackRate>=0)this._currentTime=0;else{if(!(this._totalDuration<1/0))throw new DOMException("Unable to rewind negative playback rate animation with infinite duration","InvalidStateError");this._currentTime=this._totalDuration}},play:function(){this._paused=!1,(this._isFinished||this._idle)&&(this._rewind(),this._startTime=null),this._finishedFlag=!1,this._idle=!1,this._ensureAlive(),t.applyDirtiedAnimation(this)},pause:function(){this._isFinished||this._paused||this._idle?this._idle&&(this._rewind(),this._idle=!1):this._currentTimePending=!0,this._startTime=null,this._paused=!0},finish:function(){this._idle||(this.currentTime=this._playbackRate>0?this._totalDuration:0,this._startTime=this._totalDuration-this.currentTime,this._currentTimePending=!1,t.applyDirtiedAnimation(this))},cancel:function(){this._inEffect&&(this._inEffect=!1,this._idle=!0,this._paused=!1,this._finishedFlag=!0,this._currentTime=0,this._startTime=null,this._effect._update(null),t.applyDirtiedAnimation(this))},reverse:function(){this.playbackRate*=-1,this.play()},addEventListener:function(e,t){"function"==typeof t&&"finish"==e&&this._finishHandlers.push(t)},removeEventListener:function(e,t){if("finish"==e){var i=this._finishHandlers.indexOf(t);i>=0&&this._finishHandlers.splice(i,1)}},_fireEvents:function(e){if(this._isFinished){if(!this._finishedFlag){var t=new n(this,this._currentTime,e),i=this._finishHandlers.concat(this.onfinish?[this.onfinish]:[]);setTimeout((function(){i.forEach((function(e){e.call(t.target,t)}))}),0),this._finishedFlag=!0}}else this._finishedFlag=!1},_tick:function(e,t){this._idle||this._paused||(null==this._startTime?t&&(this.startTime=e-this._currentTime/this.playbackRate):this._isFinished||this._tickCurrentTime((e-this._startTime)*this.playbackRate)),t&&(this._currentTimePending=!1,this._fireEvents(e))},get _needsTick(){return this.playState in{pending:1,running:1}||!this._finishedFlag},_targetAnimations:function(){var e=this._effect._target;return e._activeAnimations||(e._activeAnimations=[]),e._activeAnimations},_markTarget:function(){var e=this._targetAnimations();-1===e.indexOf(this)&&e.push(this)},_unmarkTarget:function(){var e=this._targetAnimations(),t=e.indexOf(this);-1!==t&&e.splice(t,1)}}}(e,t),function(e,t,i){function n(e){var t=u;u=[],e<m.currentTime&&(e=m.currentTime),m._animations.sort(r),m._animations=s(e,!0,m._animations)[0],t.forEach((function(t){t[1](e)})),o()}function r(e,t){return e._sequenceNumber-t._sequenceNumber}function a(){this._animations=[],this.currentTime=window.performance&&performance.now?performance.now():0}function o(){p.forEach((function(e){e()})),p.length=0}function s(e,i,n){f=!0,d=!1,t.timeline.currentTime=e,h=!1;var r=[],a=[],o=[],s=[];return n.forEach((function(t){t._tick(e,i),t._inEffect?(a.push(t._effect),t._markTarget()):(r.push(t._effect),t._unmarkTarget()),t._needsTick&&(h=!0);var n=t._inEffect||t._needsTick;t._inTimeline=n,n?o.push(t):s.push(t)})),p.push.apply(p,r),p.push.apply(p,a),h&&requestAnimationFrame((function(){})),f=!1,[o,s]}var l=window.requestAnimationFrame,u=[],c=0;window.requestAnimationFrame=function(e){var t=c++;return 0==u.length&&l(n),u.push([t,e]),t},window.cancelAnimationFrame=function(e){u.forEach((function(t){t[0]==e&&(t[1]=function(){})}))},a.prototype={_play:function(i){i._timing=e.normalizeTimingInput(i.timing);var n=new t.Animation(i);return n._idle=!1,n._timeline=this,this._animations.push(n),t.restart(),t.applyDirtiedAnimation(n),n}};var h=!1,d=!1;t.restart=function(){return h||(h=!0,requestAnimationFrame((function(){})),d=!0),d},t.applyDirtiedAnimation=function(e){if(!f){e._markTarget();var i=e._targetAnimations();i.sort(r),s(t.timeline.currentTime,!1,i.slice())[1].forEach((function(e){var t=m._animations.indexOf(e);-1!==t&&m._animations.splice(t,1)})),o()}};var p=[],f=!1,m=new a;t.timeline=m}(e,t),function(e){function t(e,t){var i=e.exec(t);if(i)return[i=e.ignoreCase?i[0].toLowerCase():i[0],t.substr(i.length)]}function i(e,t){var i=e(t=t.replace(/^\s*/,""));if(i)return[i[0],i[1].replace(/^\s*/,"")]}function n(e,t,i,n,r){for(var a=[],o=[],s=[],l=function(e,t){for(var i=e,n=t;i&&n;)i>n?i%=n:n%=i;return e*t/(i+n)}(n.length,r.length),u=0;u<l;u++){var c=t(n[u%n.length],r[u%r.length]);if(!c)return;a.push(c[0]),o.push(c[1]),s.push(c[2])}return[a,o,function(t){var n=t.map((function(e,t){return s[t](e)})).join(i);return e?e(n):n}]}e.consumeToken=t,e.consumeTrimmed=i,e.consumeRepeated=function(e,n,r){e=i.bind(null,e);for(var a=[];;){var o=e(r);if(!o)return[a,r];if(a.push(o[0]),!(o=t(n,r=o[1]))||""==o[1])return[a,r];r=o[1]}},e.consumeParenthesised=function(e,t){for(var i=0,n=0;n<t.length&&(!/\s|,/.test(t[n])||0!=i);n++)if("("==t[n])i++;else if(")"==t[n]&&(0==--i&&n++,i<=0))break;var r=e(t.substr(0,n));return null==r?void 0:[r,t.substr(n)]},e.ignore=function(e){return function(t){var i=e(t);return i&&(i[0]=void 0),i}},e.optional=function(e,t){return function(i){return e(i)||[t,i]}},e.consumeList=function(t,i){for(var n=[],r=0;r<t.length;r++){var a=e.consumeTrimmed(t[r],i);if(!a||""==a[0])return;void 0!==a[0]&&n.push(a[0]),i=a[1]}if(""==i)return n},e.mergeNestedRepeated=n.bind(null,null),e.mergeWrappedNestedRepeated=n,e.mergeList=function(e,t,i){for(var n=[],r=[],a=[],o=0,s=0;s<i.length;s++)if("function"==typeof i[s]){var l=i[s](e[o],t[o++]);n.push(l[0]),r.push(l[1]),a.push(l[2])}else!function(e){n.push(!1),r.push(!1),a.push((function(){return i[e]}))}(s);return[n,r,function(e){for(var t="",i=0;i<e.length;i++)t+=a[i](e[i]);return t}]}}(t),function(e){function t(t){var i={inset:!1,lengths:[],color:null},n=e.consumeRepeated((function(t){var n=e.consumeToken(/^inset/i,t);return n?(i.inset=!0,n):(n=e.consumeLengthOrPercent(t))?(i.lengths.push(n[0]),n):(n=e.consumeColor(t))?(i.color=n[0],n):void 0}),/^/,t);if(n&&n[0].length)return[i,n[1]]}var i=function(t,i,n,r){function a(e){return{inset:e,color:[0,0,0,0],lengths:[{px:0},{px:0},{px:0},{px:0}]}}for(var o=[],s=[],l=0;l<n.length||l<r.length;l++){var u=n[l]||a(r[l].inset),c=r[l]||a(n[l].inset);o.push(u),s.push(c)}return e.mergeNestedRepeated(t,i,o,s)}.bind(null,(function(t,i){for(;t.lengths.length<Math.max(t.lengths.length,i.lengths.length);)t.lengths.push({px:0});for(;i.lengths.length<Math.max(t.lengths.length,i.lengths.length);)i.lengths.push({px:0});if(t.inset==i.inset&&!!t.color==!!i.color){for(var n,r=[],a=[[],0],o=[[],0],s=0;s<t.lengths.length;s++){var l=e.mergeDimensions(t.lengths[s],i.lengths[s],2==s);a[0].push(l[0]),o[0].push(l[1]),r.push(l[2])}if(t.color&&i.color){var u=e.mergeColors(t.color,i.color);a[1]=u[0],o[1]=u[1],n=u[2]}return[a,o,function(e){for(var i=t.inset?"inset ":" ",a=0;a<r.length;a++)i+=r[a](e[0][a])+" ";return n&&(i+=n(e[1])),i}]}}),", ");e.addPropertiesHandler((function(i){var n=e.consumeRepeated(t,/^,/,i);if(n&&""==n[1])return n[0]}),i,["box-shadow","text-shadow"])}(t),function(e,t){function i(e){return e.toFixed(3).replace(/0+$/,"").replace(/\.$/,"")}function n(e,t,i){return Math.min(t,Math.max(e,i))}function r(e){if(/^\s*[-+]?(\d*\.)?\d+\s*$/.test(e))return Number(e)}function a(e,t){return function(r,a){return[r,a,function(r){return i(n(e,t,r))}]}}function o(e){var t=e.trim().split(/\s*[\s,]\s*/);if(0!==t.length){for(var i=[],n=0;n<t.length;n++){var a=r(t[n]);if(void 0===a)return;i.push(a)}return i}}e.clamp=n,e.addPropertiesHandler(o,(function(e,t){if(e.length==t.length)return[e,t,function(e){return e.map(i).join(" ")}]}),["stroke-dasharray"]),e.addPropertiesHandler(r,a(0,1/0),["border-image-width","line-height"]),e.addPropertiesHandler(r,a(0,1),["opacity","shape-image-threshold"]),e.addPropertiesHandler(r,(function(e,t){if(0!=e)return a(0,1/0)(e,t)}),["flex-grow","flex-shrink"]),e.addPropertiesHandler(r,(function(e,t){return[e,t,function(e){return Math.round(n(1,1/0,e))}]}),["orphans","widows"]),e.addPropertiesHandler(r,(function(e,t){return[e,t,Math.round]}),["z-index"]),e.parseNumber=r,e.parseNumberList=o,e.mergeNumbers=function(e,t){return[e,t,i]},e.numberToString=i}(t),function(e,t){e.addPropertiesHandler(String,(function(e,t){if("visible"==e||"visible"==t)return[0,1,function(i){return i<=0?e:i>=1?t:"visible"}]}),["visibility"])}(t),function(e,t){function i(e){e=e.trim(),a.fillStyle="#000",a.fillStyle=e;var t=a.fillStyle;if(a.fillStyle="#fff",a.fillStyle=e,t==a.fillStyle){a.fillRect(0,0,1,1);var i=a.getImageData(0,0,1,1).data;a.clearRect(0,0,1,1);var n=i[3]/255;return[i[0]*n,i[1]*n,i[2]*n,n]}}function n(t,i){return[t,i,function(t){function i(e){return Math.max(0,Math.min(255,e))}if(t[3])for(var n=0;n<3;n++)t[n]=Math.round(i(t[n]/t[3]));return t[3]=e.numberToString(e.clamp(0,1,t[3])),"rgba("+t.join(",")+")"}]}var r=document.createElementNS("http://www.w3.org/1999/xhtml","canvas");r.width=r.height=1;var a=r.getContext("2d");e.addPropertiesHandler(i,n,["background-color","border-bottom-color","border-left-color","border-right-color","border-top-color","color","fill","flood-color","lighting-color","outline-color","stop-color","stroke","text-decoration-color"]),e.consumeColor=e.consumeParenthesised.bind(null,i),e.mergeColors=n}(t),function(e,t){function i(e){function t(){var t=o.exec(e);a=t?t[0]:void 0}function i(){if("("!==a)return function(){var e=Number(a);return t(),e}();t();var e=r();return")"!==a?NaN:(t(),e)}function n(){for(var e=i();"*"===a||"/"===a;){var n=a;t();var r=i();"*"===n?e*=r:e/=r}return e}function r(){for(var e=n();"+"===a||"-"===a;){var i=a;t();var r=n();"+"===i?e+=r:e-=r}return e}var a,o=/([\+\-\w\.]+|[\(\)\*\/])/g;return t(),r()}function n(e,t){if("0"==(t=t.trim().toLowerCase())&&"px".search(e)>=0)return{px:0};if(/^[^(]*$|^calc/.test(t)){t=t.replace(/calc\(/g,"(");var n={};t=t.replace(e,(function(e){return n[e]=null,"U"+e}));for(var r="U("+e.source+")",a=t.replace(/[-+]?(\d*\.)?\d+([Ee][-+]?\d+)?/g,"N").replace(new RegExp("N"+r,"g"),"D").replace(/\s[+-]\s/g,"O").replace(/\s/g,""),o=[/N\*(D)/g,/(N|D)[*\/]N/g,/(N|D)O\1/g,/\((N|D)\)/g],s=0;s<o.length;)o[s].test(a)?(a=a.replace(o[s],"$1"),s=0):s++;if("D"==a){for(var l in n){var u=i(t.replace(new RegExp("U"+l,"g"),"").replace(new RegExp(r,"g"),"*0"));if(!isFinite(u))return;n[l]=u}return n}}}function r(e,t){return a(e,t,!0)}function a(t,i,n){var r,a=[];for(r in t)a.push(r);for(r in i)a.indexOf(r)<0&&a.push(r);return t=a.map((function(e){return t[e]||0})),i=a.map((function(e){return i[e]||0})),[t,i,function(t){var i=t.map((function(i,r){return 1==t.length&&n&&(i=Math.max(i,0)),e.numberToString(i)+a[r]})).join(" + ");return t.length>1?"calc("+i+")":i}]}var o="px|em|ex|ch|rem|vw|vh|vmin|vmax|cm|mm|in|pt|pc",s=n.bind(null,new RegExp(o,"g")),l=n.bind(null,new RegExp(o+"|%","g")),u=n.bind(null,/deg|rad|grad|turn/g);e.parseLength=s,e.parseLengthOrPercent=l,e.consumeLengthOrPercent=e.consumeParenthesised.bind(null,l),e.parseAngle=u,e.mergeDimensions=a;var c=e.consumeParenthesised.bind(null,s),h=e.consumeRepeated.bind(void 0,c,/^/),d=e.consumeRepeated.bind(void 0,h,/^,/);e.consumeSizePairList=d;var p=e.mergeNestedRepeated.bind(void 0,r," "),f=e.mergeNestedRepeated.bind(void 0,p,",");e.mergeNonNegativeSizePair=p,e.addPropertiesHandler((function(e){var t=d(e);if(t&&""==t[1])return t[0]}),f,["background-size"]),e.addPropertiesHandler(l,r,["border-bottom-width","border-image-width","border-left-width","border-right-width","border-top-width","flex-basis","font-size","height","line-height","max-height","max-width","outline-width","width"]),e.addPropertiesHandler(l,a,["border-bottom-left-radius","border-bottom-right-radius","border-top-left-radius","border-top-right-radius","bottom","left","letter-spacing","margin-bottom","margin-left","margin-right","margin-top","min-height","min-width","outline-offset","padding-bottom","padding-left","padding-right","padding-top","perspective","right","shape-margin","stroke-dashoffset","text-indent","top","vertical-align","word-spacing"])}(t),function(e,t){function i(t){return e.consumeLengthOrPercent(t)||e.consumeToken(/^auto/,t)}function n(t){var n=e.consumeList([e.ignore(e.consumeToken.bind(null,/^rect/)),e.ignore(e.consumeToken.bind(null,/^\(/)),e.consumeRepeated.bind(null,i,/^,/),e.ignore(e.consumeToken.bind(null,/^\)/))],t);if(n&&4==n[0].length)return n[0]}var r=e.mergeWrappedNestedRepeated.bind(null,(function(e){return"rect("+e+")"}),(function(t,i){return"auto"==t||"auto"==i?[!0,!1,function(n){var r=n?t:i;if("auto"==r)return"auto";var a=e.mergeDimensions(r,r);return a[2](a[0])}]:e.mergeDimensions(t,i)}),", ");e.parseBox=n,e.mergeBoxes=r,e.addPropertiesHandler(n,r,["clip"])}(t),function(e,t){function i(e){return function(t){var i=0;return e.map((function(e){return e===u?t[i++]:e}))}}function n(e){return e}function r(t){if("none"==(t=t.toLowerCase().trim()))return[];for(var i,n=/\s*(\w+)\(([^)]*)\)/g,r=[],a=0;i=n.exec(t);){if(i.index!=a)return;a=i.index+i[0].length;var o=i[1],s=d[o];if(!s)return;var l=i[2].split(","),u=s[0];if(u.length<l.length)return;for(var p=[],f=0;f<u.length;f++){var m,g=l[f],_=u[f];if(void 0===(m=g?{A:function(t){return"0"==t.trim()?h:e.parseAngle(t)},N:e.parseNumber,T:e.parseLengthOrPercent,L:e.parseLength}[_.toUpperCase()](g):{a:h,n:p[0],t:c}[_]))return;p.push(m)}if(r.push({t:o,d:p}),n.lastIndex==t.length)return r}}function a(e){return e.toFixed(6).replace(".000000","")}function o(t,i){if(t.decompositionPair!==i){t.decompositionPair=i;var n=e.makeMatrixDecomposition(t)}if(i.decompositionPair!==t){i.decompositionPair=t;var r=e.makeMatrixDecomposition(i)}return null==n[0]||null==r[0]?[[!1],[!0],function(e){return e?i[0].d:t[0].d}]:(n[0].push(0),r[0].push(1),[n,r,function(t){var i=e.quat(n[0][3],r[0][3],t[5]);return e.composeMatrix(t[0],t[1],t[2],i,t[4]).map(a).join(",")}])}function s(e){return e.replace(/[xy]/,"")}function l(e){return e.replace(/(x|y|z|3d)?$/,"3d")}var u=null,c={px:0},h={deg:0},d={matrix:["NNNNNN",[u,u,0,0,u,u,0,0,0,0,1,0,u,u,0,1],n],matrix3d:["NNNNNNNNNNNNNNNN",n],rotate:["A"],rotatex:["A"],rotatey:["A"],rotatez:["A"],rotate3d:["NNNA"],perspective:["L"],scale:["Nn",i([u,u,1]),n],scalex:["N",i([u,1,1]),i([u,1])],scaley:["N",i([1,u,1]),i([1,u])],scalez:["N",i([1,1,u])],scale3d:["NNN",n],skew:["Aa",null,n],skewx:["A",null,i([u,h])],skewy:["A",null,i([h,u])],translate:["Tt",i([u,u,c]),n],translatex:["T",i([u,c,c]),i([u,c])],translatey:["T",i([c,u,c]),i([c,u])],translatez:["L",i([c,c,u])],translate3d:["TTL",n]};e.addPropertiesHandler(r,(function(t,i){var n=e.makeMatrixDecomposition&&!0,r=!1;if(!t.length||!i.length){t.length||(r=!0,t=i,i=[]);for(var a=0;a<t.length;a++){var u=t[a].t,c=t[a].d,h="scale"==u.substr(0,5)?1:0;i.push({t:u,d:c.map((function(e){if("number"==typeof e)return h;var t={};for(var i in e)t[i]=h;return t}))})}}var p=function(e,t){return"perspective"==e&&"perspective"==t||("matrix"==e||"matrix3d"==e)&&("matrix"==t||"matrix3d"==t)},f=[],m=[],g=[];if(t.length!=i.length){if(!n)return;f=[(k=o(t,i))[0]],m=[k[1]],g=[["matrix",[k[2]]]]}else for(a=0;a<t.length;a++){var _=t[a].t,v=i[a].t,b=t[a].d,y=i[a].d,w=d[_],x=d[v];if(p(_,v)){if(!n)return;var k=o([t[a]],[i[a]]);f.push(k[0]),m.push(k[1]),g.push(["matrix",[k[2]]])}else{if(_==v)u=_;else if(w[2]&&x[2]&&s(_)==s(v))u=s(_),b=w[2](b),y=x[2](y);else{if(!w[1]||!x[1]||l(_)!=l(v)){if(!n)return;f=[(k=o(t,i))[0]],m=[k[1]],g=[["matrix",[k[2]]]];break}u=l(_),b=w[1](b),y=x[1](y)}for(var T=[],E=[],P=[],A=0;A<b.length;A++)k=("number"==typeof b[A]?e.mergeNumbers:e.mergeDimensions)(b[A],y[A]),T[A]=k[0],E[A]=k[1],P.push(k[2]);f.push(T),m.push(E),g.push([u,P])}}if(r){var R=f;f=m,m=R}return[f,m,function(e){return e.map((function(e,t){var i=e.map((function(e,i){return g[t][1][i](e)})).join(",");return"matrix"==g[t][0]&&16==i.split(",").length&&(g[t][0]="matrix3d"),g[t][0]+"("+i+")"})).join(" ")}]}),["transform"]),e.transformToSvgMatrix=function(t){var i=e.transformListToMatrix(r(t));return"matrix("+a(i[0])+" "+a(i[1])+" "+a(i[4])+" "+a(i[5])+" "+a(i[12])+" "+a(i[13])+")"}}(t),function(e,t){function i(e,t){t.concat([e]).forEach((function(t){t in document.documentElement.style&&(n[e]=t),r[t]=e}))}var n={},r={};i("transform",["webkitTransform","msTransform"]),i("transformOrigin",["webkitTransformOrigin"]),i("perspective",["webkitPerspective"]),i("perspectiveOrigin",["webkitPerspectiveOrigin"]),e.propertyName=function(e){return n[e]||e},e.unprefixedPropertyName=function(e){return r[e]||e}}(t)}(),function(){if(void 0===document.createElement("div").animate([]).oncancel){if(window.performance&&performance.now)var e=function(){return performance.now()};else e=function(){return Date.now()};var t=function(e,t,i){this.target=e,this.currentTime=t,this.timelineTime=i,this.type="cancel",this.bubbles=!1,this.cancelable=!1,this.currentTarget=e,this.defaultPrevented=!1,this.eventPhase=Event.AT_TARGET,this.timeStamp=Date.now()},i=window.Element.prototype.animate;window.Element.prototype.animate=function(n,r){var a=i.call(this,n,r);a._cancelHandlers=[],a.oncancel=null;var o=a.cancel;a.cancel=function(){o.call(this);var i=new t(this,null,e()),n=this._cancelHandlers.concat(this.oncancel?[this.oncancel]:[]);setTimeout((function(){n.forEach((function(e){e.call(i.target,i)}))}),0)};var s=a.addEventListener;a.addEventListener=function(e,t){"function"==typeof t&&"cancel"==e?this._cancelHandlers.push(t):s.call(this,e,t)};var l=a.removeEventListener;return a.removeEventListener=function(e,t){if("cancel"==e){var i=this._cancelHandlers.indexOf(t);i>=0&&this._cancelHandlers.splice(i,1)}else l.call(this,e,t)},a}}}(),function(e){var t=document.documentElement,i=null,n=!1;try{var r="0"==getComputedStyle(t).getPropertyValue("opacity")?"1":"0";(i=t.animate({opacity:[r,r]},{duration:1})).currentTime=0,n=getComputedStyle(t).getPropertyValue("opacity")==r}catch(e){}finally{i&&i.cancel()}if(!n){var a=window.Element.prototype.animate;window.Element.prototype.animate=function(t,i){return window.Symbol&&Symbol.iterator&&Array.prototype.from&&t[Symbol.iterator]&&(t=Array.from(t)),Array.isArray(t)||null===t||(t=e.convertToArrayForm(t)),a.call(this,t,i)}}}(e),function(e,t,i){function n(e){var i=t.timeline;i.currentTime=e,i._discardAnimations(),0==i._animations.length?a=!1:requestAnimationFrame(n)}var r=window.requestAnimationFrame;window.requestAnimationFrame=function(e){return r((function(i){t.timeline._updateAnimationsPromises(),e(i),t.timeline._updateAnimationsPromises()}))},t.AnimationTimeline=function(){this._animations=[],this.currentTime=void 0},t.AnimationTimeline.prototype={getAnimations:function(){return this._discardAnimations(),this._animations.slice()},_updateAnimationsPromises:function(){t.animationsWithPromises=t.animationsWithPromises.filter((function(e){return e._updatePromises()}))},_discardAnimations:function(){this._updateAnimationsPromises(),this._animations=this._animations.filter((function(e){return"finished"!=e.playState&&"idle"!=e.playState}))},_play:function(e){var i=new t.Animation(e,this);return this._animations.push(i),t.restartWebAnimationsNextTick(),i._updatePromises(),i._animation.play(),i._updatePromises(),i},play:function(e){return e&&e.remove(),this._play(e)}};var a=!1;t.restartWebAnimationsNextTick=function(){a||(a=!0,requestAnimationFrame(n))};var o=new t.AnimationTimeline;t.timeline=o;try{Object.defineProperty(window.document,"timeline",{configurable:!0,get:function(){return o}})}catch(e){}try{window.document.timeline=o}catch(e){}}(0,i),function(e,t,i){t.animationsWithPromises=[],t.Animation=function(t,i){if(this.id="",t&&t._id&&(this.id=t._id),this.effect=t,t&&(t._animation=this),!i)throw new Error("Animation with null timeline is not supported");this._timeline=i,this._sequenceNumber=e.sequenceNumber++,this._holdTime=0,this._paused=!1,this._isGroup=!1,this._animation=null,this._childAnimations=[],this._callback=null,this._oldPlayState="idle",this._rebuildUnderlyingAnimation(),this._animation.cancel(),this._updatePromises()},t.Animation.prototype={_updatePromises:function(){var e=this._oldPlayState,t=this.playState;return this._readyPromise&&t!==e&&("idle"==t?(this._rejectReadyPromise(),this._readyPromise=void 0):"pending"==e?this._resolveReadyPromise():"pending"==t&&(this._readyPromise=void 0)),this._finishedPromise&&t!==e&&("idle"==t?(this._rejectFinishedPromise(),this._finishedPromise=void 0):"finished"==t?this._resolveFinishedPromise():"finished"==e&&(this._finishedPromise=void 0)),this._oldPlayState=this.playState,this._readyPromise||this._finishedPromise},_rebuildUnderlyingAnimation:function(){this._updatePromises();var e,i,n,r,a=!!this._animation;a&&(e=this.playbackRate,i=this._paused,n=this.startTime,r=this.currentTime,this._animation.cancel(),this._animation._wrapper=null,this._animation=null),(!this.effect||this.effect instanceof window.KeyframeEffect)&&(this._animation=t.newUnderlyingAnimationForKeyframeEffect(this.effect),t.bindAnimationForKeyframeEffect(this)),(this.effect instanceof window.SequenceEffect||this.effect instanceof window.GroupEffect)&&(this._animation=t.newUnderlyingAnimationForGroup(this.effect),t.bindAnimationForGroup(this)),this.effect&&this.effect._onsample&&t.bindAnimationForCustomEffect(this),a&&(1!=e&&(this.playbackRate=e),null!==n?this.startTime=n:null!==r?this.currentTime=r:null!==this._holdTime&&(this.currentTime=this._holdTime),i&&this.pause()),this._updatePromises()},_updateChildren:function(){if(this.effect&&"idle"!=this.playState){var e=this.effect._timing.delay;this._childAnimations.forEach(function(i){this._arrangeChildren(i,e),this.effect instanceof window.SequenceEffect&&(e+=t.groupChildDuration(i.effect))}.bind(this))}},_setExternalAnimation:function(e){if(this.effect&&this._isGroup)for(var t=0;t<this.effect.children.length;t++)this.effect.children[t]._animation=e,this._childAnimations[t]._setExternalAnimation(e)},_constructChildAnimations:function(){if(this.effect&&this._isGroup){var e=this.effect._timing.delay;this._removeChildAnimations(),this.effect.children.forEach(function(i){var n=t.timeline._play(i);this._childAnimations.push(n),n.playbackRate=this.playbackRate,this._paused&&n.pause(),i._animation=this.effect._animation,this._arrangeChildren(n,e),this.effect instanceof window.SequenceEffect&&(e+=t.groupChildDuration(i))}.bind(this))}},_arrangeChildren:function(e,t){null===this.startTime?e.currentTime=this.currentTime-t/this.playbackRate:e.startTime!==this.startTime+t/this.playbackRate&&(e.startTime=this.startTime+t/this.playbackRate)},get timeline(){return this._timeline},get playState(){return this._animation?this._animation.playState:"idle"},get finished(){return window.Promise?(this._finishedPromise||(-1==t.animationsWithPromises.indexOf(this)&&t.animationsWithPromises.push(this),this._finishedPromise=new Promise(function(e,t){this._resolveFinishedPromise=function(){e(this)},this._rejectFinishedPromise=function(){t({type:DOMException.ABORT_ERR,name:"AbortError"})}}.bind(this)),"finished"==this.playState&&this._resolveFinishedPromise()),this._finishedPromise):(console.warn("Animation Promises require JavaScript Promise constructor"),null)},get ready(){return window.Promise?(this._readyPromise||(-1==t.animationsWithPromises.indexOf(this)&&t.animationsWithPromises.push(this),this._readyPromise=new Promise(function(e,t){this._resolveReadyPromise=function(){e(this)},this._rejectReadyPromise=function(){t({type:DOMException.ABORT_ERR,name:"AbortError"})}}.bind(this)),"pending"!==this.playState&&this._resolveReadyPromise()),this._readyPromise):(console.warn("Animation Promises require JavaScript Promise constructor"),null)},get onfinish(){return this._animation.onfinish},set onfinish(e){this._animation.onfinish="function"==typeof e?function(t){t.target=this,e.call(this,t)}.bind(this):e},get oncancel(){return this._animation.oncancel},set oncancel(e){this._animation.oncancel="function"==typeof e?function(t){t.target=this,e.call(this,t)}.bind(this):e},get currentTime(){this._updatePromises();var e=this._animation.currentTime;return this._updatePromises(),e},set currentTime(e){this._updatePromises(),this._animation.currentTime=isFinite(e)?e:Math.sign(e)*Number.MAX_VALUE,this._register(),this._forEachChild((function(t,i){t.currentTime=e-i})),this._updatePromises()},get startTime(){return this._animation.startTime},set startTime(e){this._updatePromises(),this._animation.startTime=isFinite(e)?e:Math.sign(e)*Number.MAX_VALUE,this._register(),this._forEachChild((function(t,i){t.startTime=e+i})),this._updatePromises()},get playbackRate(){return this._animation.playbackRate},set playbackRate(e){this._updatePromises();var t=this.currentTime;this._animation.playbackRate=e,this._forEachChild((function(t){t.playbackRate=e})),null!==t&&(this.currentTime=t),this._updatePromises()},play:function(){this._updatePromises(),this._paused=!1,this._animation.play(),-1==this._timeline._animations.indexOf(this)&&this._timeline._animations.push(this),this._register(),t.awaitStartTime(this),this._forEachChild((function(e){var t=e.currentTime;e.play(),e.currentTime=t})),this._updatePromises()},pause:function(){this._updatePromises(),this.currentTime&&(this._holdTime=this.currentTime),this._animation.pause(),this._register(),this._forEachChild((function(e){e.pause()})),this._paused=!0,this._updatePromises()},finish:function(){this._updatePromises(),this._animation.finish(),this._register(),this._updatePromises()},cancel:function(){this._updatePromises(),this._animation.cancel(),this._register(),this._removeChildAnimations(),this._updatePromises()},reverse:function(){this._updatePromises();var e=this.currentTime;this._animation.reverse(),this._forEachChild((function(e){e.reverse()})),null!==e&&(this.currentTime=e),this._updatePromises()},addEventListener:function(e,t){var i=t;"function"==typeof t&&(i=function(e){e.target=this,t.call(this,e)}.bind(this),t._wrapper=i),this._animation.addEventListener(e,i)},removeEventListener:function(e,t){this._animation.removeEventListener(e,t&&t._wrapper||t)},_removeChildAnimations:function(){for(;this._childAnimations.length;)this._childAnimations.pop().cancel()},_forEachChild:function(t){var i=0;if(this.effect.children&&this._childAnimations.length<this.effect.children.length&&this._constructChildAnimations(),this._childAnimations.forEach(function(e){t.call(this,e,i),this.effect instanceof window.SequenceEffect&&(i+=e.effect.activeDuration)}.bind(this)),"pending"!=this.playState){var n=this.effect._timing,r=this.currentTime;null!==r&&(r=e.calculateIterationProgress(e.calculateActiveDuration(n),r,n)),(null==r||isNaN(r))&&this._removeChildAnimations()}}},window.Animation=t.Animation}(e,i),function(e,t,i){function n(t){this._frames=e.normalizeKeyframes(t)}function r(){for(var e=!1;l.length;)l.shift()._updateChildren(),e=!0;return e}var a=function(e){if(e._animation=void 0,e instanceof window.SequenceEffect||e instanceof window.GroupEffect)for(var t=0;t<e.children.length;t++)a(e.children[t])};t.removeMulti=function(e){for(var t=[],i=0;i<e.length;i++){var n=e[i];n._parent?(-1==t.indexOf(n._parent)&&t.push(n._parent),n._parent.children.splice(n._parent.children.indexOf(n),1),n._parent=null,a(n)):n._animation&&n._animation.effect==n&&(n._animation.cancel(),n._animation.effect=new KeyframeEffect(null,[]),n._animation._callback&&(n._animation._callback._animation=null),n._animation._rebuildUnderlyingAnimation(),a(n))}for(i=0;i<t.length;i++)t[i]._rebuild()},t.KeyframeEffect=function(t,i,r,a){return this.target=t,this._parent=null,r=e.numericTimingToObject(r),this._timingInput=e.cloneTimingInput(r),this._timing=e.normalizeTimingInput(r),this.timing=e.makeTiming(r,!1,this),this.timing._effect=this,"function"==typeof i?(e.deprecated("Custom KeyframeEffect","2015-06-22","Use KeyframeEffect.onsample instead."),this._normalizedKeyframes=i):this._normalizedKeyframes=new n(i),this._keyframes=i,this.activeDuration=e.calculateActiveDuration(this._timing),this._id=a,this},t.KeyframeEffect.prototype={getFrames:function(){return"function"==typeof this._normalizedKeyframes?this._normalizedKeyframes:this._normalizedKeyframes._frames},set onsample(e){if("function"==typeof this.getFrames())throw new Error("Setting onsample on custom effect KeyframeEffect is not supported.");this._onsample=e,this._animation&&this._animation._rebuildUnderlyingAnimation()},get parent(){return this._parent},clone:function(){if("function"==typeof this.getFrames())throw new Error("Cloning custom effects is not supported.");var t=new KeyframeEffect(this.target,[],e.cloneTimingInput(this._timingInput),this._id);return t._normalizedKeyframes=this._normalizedKeyframes,t._keyframes=this._keyframes,t},remove:function(){t.removeMulti([this])}};var o=Element.prototype.animate;Element.prototype.animate=function(e,i){var n="";return i&&i.id&&(n=i.id),t.timeline._play(new t.KeyframeEffect(this,e,i,n))};var s=document.createElementNS("http://www.w3.org/1999/xhtml","div");t.newUnderlyingAnimationForKeyframeEffect=function(e){if(e){var t=e.target||s;"function"==typeof(i=e._keyframes)&&(i=[]),(n=e._timingInput).id=e._id}else{t=s;var i=[],n=0}return o.apply(t,[i,n])},t.bindAnimationForKeyframeEffect=function(e){e.effect&&"function"==typeof e.effect._normalizedKeyframes&&t.bindAnimationForCustomEffect(e)};var l=[];t.awaitStartTime=function(e){null===e.startTime&&e._isGroup&&(0==l.length&&requestAnimationFrame(r),l.push(e))};var u=window.getComputedStyle;Object.defineProperty(window,"getComputedStyle",{configurable:!0,enumerable:!0,value:function(){t.timeline._updateAnimationsPromises();var e=u.apply(this,arguments);return r()&&(e=u.apply(this,arguments)),t.timeline._updateAnimationsPromises(),e}}),window.KeyframeEffect=t.KeyframeEffect,window.Element.prototype.getAnimations=function(){return document.timeline.getAnimations().filter(function(e){return null!==e.effect&&e.effect.target==this}.bind(this))}}(e,i),function(e,t,i){function n(e){e._registered||(e._registered=!0,o.push(e),s||(s=!0,requestAnimationFrame(r)))}function r(e){var t=o;o=[],t.sort((function(e,t){return e._sequenceNumber-t._sequenceNumber})),t=t.filter((function(e){e();var t=e._animation?e._animation.playState:"idle";return"running"!=t&&"pending"!=t&&(e._registered=!1),e._registered})),o.push.apply(o,t),o.length?(s=!0,requestAnimationFrame(r)):s=!1}var a=(document.createElementNS("http://www.w3.org/1999/xhtml","div"),0);t.bindAnimationForCustomEffect=function(t){var i,r=t.effect.target,o="function"==typeof t.effect.getFrames();i=o?t.effect.getFrames():t.effect._onsample;var s=t.effect.timing,l=null;s=e.normalizeTimingInput(s);var u=function(){var n=u._animation?u._animation.currentTime:null;null!==n&&(n=e.calculateIterationProgress(e.calculateActiveDuration(s),n,s),isNaN(n)&&(n=null)),n!==l&&(o?i(n,r,t.effect):i(n,t.effect,t.effect._animation)),l=n};u._animation=t,u._registered=!1,u._sequenceNumber=a++,t._callback=u,n(u)};var o=[],s=!1;t.Animation.prototype._register=function(){this._callback&&n(this._callback)}}(e,i),function(e,t,i){function n(e){return e._timing.delay+e.activeDuration+e._timing.endDelay}function r(t,i,n){this._id=n,this._parent=null,this.children=t||[],this._reparent(this.children),i=e.numericTimingToObject(i),this._timingInput=e.cloneTimingInput(i),this._timing=e.normalizeTimingInput(i,!0),this.timing=e.makeTiming(i,!0,this),this.timing._effect=this,"auto"===this._timing.duration&&(this._timing.duration=this.activeDuration)}window.SequenceEffect=function(){r.apply(this,arguments)},window.GroupEffect=function(){r.apply(this,arguments)},r.prototype={_isAncestor:function(e){for(var t=this;null!==t;){if(t==e)return!0;t=t._parent}return!1},_rebuild:function(){for(var e=this;e;)"auto"===e.timing.duration&&(e._timing.duration=e.activeDuration),e=e._parent;this._animation&&this._animation._rebuildUnderlyingAnimation()},_reparent:function(e){t.removeMulti(e);for(var i=0;i<e.length;i++)e[i]._parent=this},_putChild:function(e,t){for(var i=t?"Cannot append an ancestor or self":"Cannot prepend an ancestor or self",n=0;n<e.length;n++)if(this._isAncestor(e[n]))throw{type:DOMException.HIERARCHY_REQUEST_ERR,name:"HierarchyRequestError",message:i};for(n=0;n<e.length;n++)t?this.children.push(e[n]):this.children.unshift(e[n]);this._reparent(e),this._rebuild()},append:function(){this._putChild(arguments,!0)},prepend:function(){this._putChild(arguments,!1)},get parent(){return this._parent},get firstChild(){return this.children.length?this.children[0]:null},get lastChild(){return this.children.length?this.children[this.children.length-1]:null},clone:function(){for(var t=e.cloneTimingInput(this._timingInput),i=[],n=0;n<this.children.length;n++)i.push(this.children[n].clone());return this instanceof GroupEffect?new GroupEffect(i,t):new SequenceEffect(i,t)},remove:function(){t.removeMulti([this])}},window.SequenceEffect.prototype=Object.create(r.prototype),Object.defineProperty(window.SequenceEffect.prototype,"activeDuration",{get:function(){var e=0;return this.children.forEach((function(t){e+=n(t)})),Math.max(e,0)}}),window.GroupEffect.prototype=Object.create(r.prototype),Object.defineProperty(window.GroupEffect.prototype,"activeDuration",{get:function(){var e=0;return this.children.forEach((function(t){e=Math.max(e,n(t))})),e}}),t.newUnderlyingAnimationForGroup=function(i){var n,r=null,a=new KeyframeEffect(null,[],i._timing,i._id);return a.onsample=function(t){var i=n._wrapper;if(i&&"pending"!=i.playState&&i.effect)return null==t?void i._removeChildAnimations():0==t&&i.playbackRate<0&&(r||(r=e.normalizeTimingInput(i.effect.timing)),t=e.calculateIterationProgress(e.calculateActiveDuration(r),-1,r),isNaN(t)||null==t)?(i._forEachChild((function(e){e.currentTime=-1})),void i._removeChildAnimations()):void 0},n=t.timeline._play(a)},t.bindAnimationForGroup=function(e){e._animation._wrapper=e,e._isGroup=!0,t.awaitStartTime(e),e._constructChildAnimations(),e._setExternalAnimation(e)},t.groupChildDuration=n}(e,i)}}]);
//# sourceMappingURL=chunk.16efae9f6bcb742e97be.js.map