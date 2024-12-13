/*! For license information please see 4834.17Nz40ffOcs.js.LICENSE.txt */
"use strict";(self.webpackChunkhome_assistant_frontend=self.webpackChunkhome_assistant_frontend||[]).push([[4834],{17314:function(t,i,e){e.d(i,{u:function(){return m}});var n,s,r=e(64599),o=e(71008),h=e(35806),a=e(62193),l=e(2816),u=(e(50693),e(29193),e(79192)),c=e(44331),_=e(50289),d=e(29818),f=e(85323),g=e(10977),p=e(96494),m=function(t){function i(){var t;return(0,o.A)(this,i),(t=(0,a.A)(this,i,arguments)).rows=2,t.cols=20,t.charCounter=!1,t}return(0,l.A)(i,t),(0,h.A)(i,[{key:"render",value:function(){var t=this.charCounter&&-1!==this.maxLength,i=t&&"internal"===this.charCounter,e=t&&!i,s=!!this.helper||!!this.validationMessage||e,o={"mdc-text-field--disabled":this.disabled,"mdc-text-field--no-label":!this.label,"mdc-text-field--filled":!this.outlined,"mdc-text-field--outlined":this.outlined,"mdc-text-field--end-aligned":this.endAligned,"mdc-text-field--with-internal-counter":i};return(0,_.qy)(n||(n=(0,r.A)([' <label class="mdc-text-field mdc-text-field--textarea ','"> '," "," "," "," "," </label> "," "])),(0,f.H)(o),this.renderRipple(),this.outlined?this.renderOutline():this.renderLabel(),this.renderInput(),this.renderCharCounter(i),this.renderLineRipple(),this.renderHelperText(s,e))}},{key:"renderInput",value:function(){var t=this.label?"label":void 0,i=-1===this.minLength?void 0:this.minLength,e=-1===this.maxLength?void 0:this.maxLength,n=this.autocapitalize?this.autocapitalize:void 0;return(0,_.qy)(s||(s=(0,r.A)([' <textarea aria-labelledby="','" class="mdc-text-field__input" .value="','" rows="','" cols="','" ?disabled="','" placeholder="','" ?required="','" ?readonly="','" minlength="','" maxlength="','" name="','" inputmode="','" autocapitalize="','" @input="','" @blur="','">\n      </textarea>'])),(0,g.J)(t),(0,p.V)(this.value),this.rows,this.cols,this.disabled,this.placeholder,this.required,this.readOnly,(0,g.J)(i),(0,g.J)(e),(0,g.J)(""===this.name?void 0:this.name),(0,g.J)(this.inputMode),(0,g.J)(n),this.handleInputChange,this.onInputBlur)}}])}(c.J);(0,u.__decorate)([(0,d.P)("textarea")],m.prototype,"formElement",void 0),(0,u.__decorate)([(0,d.MZ)({type:Number})],m.prototype,"rows",void 0),(0,u.__decorate)([(0,d.MZ)({type:Number})],m.prototype,"cols",void 0),(0,u.__decorate)([(0,d.MZ)({converter:{fromAttribute:function(t){return null!==t&&(""===t||t)},toAttribute:function(t){return"boolean"==typeof t?t?"":null:t}}})],m.prototype,"charCounter",void 0)},25983:function(t,i,e){e.d(i,{R:function(){return r}});var n,s=e(64599),r=(0,e(50289).AH)(n||(n=(0,s.A)([".mdc-text-field{height:100%}.mdc-text-field__input{resize:none}"])))},32350:function(t,i,e){var n=e(32174),s=e(23444),r=e(33616),o=e(36565),h=e(87149),a=Math.min,l=[].lastIndexOf,u=!!l&&1/[1].lastIndexOf(1,-0)<0,c=h("lastIndexOf"),_=u||!c;t.exports=_?function(t){if(u)return n(l,this,arguments)||0;var i=s(this),e=o(i);if(0===e)return-1;var h=e-1;for(arguments.length>1&&(h=a(h,r(arguments[1]))),h<0&&(h=e+h);h>=0;h--)if(h in i&&i[h]===t)return h||0;return-1}:l},78232:function(t,i,e){var n=e(26887),s=Math.floor;t.exports=Number.isInteger||function(t){return!n(t)&&isFinite(t)&&s(t)===t}},15814:function(t,i,e){var n=e(41765),s=e(32350);n({target:"Array",proto:!0,forced:s!==[].lastIndexOf},{lastIndexOf:s})},42805:function(t,i,e){var n=e(41765),s=e(73201),r=e(95689),o=e(56674),h=e(1370);n({target:"Iterator",proto:!0,real:!0},{every:function(t){o(this),r(t);var i=h(this),e=0;return!s(i,(function(i,n){if(!t(i,e++))return n()}),{IS_RECORD:!0,INTERRUPTED:!0}).stopped}})},63030:function(t,i,e){e(41765)({target:"Number",stat:!0},{isInteger:e(78232)})},6566:function(t,i,e){e(41765)({target:"Number",stat:!0,nonConfigurable:!0,nonWritable:!0},{MAX_SAFE_INTEGER:9007199254740991})},61532:function(t,i,e){e(41765)({target:"Number",stat:!0,nonConfigurable:!0,nonWritable:!0},{MIN_SAFE_INTEGER:-9007199254740991})},52353:function(t,i,e){var n=e(41765),s=e(59260).codeAt;n({target:"String",proto:!0},{codePointAt:function(t){return s(this,t)}})},5186:function(t,i,e){e(42805)},29865:function(t,i,e){e.d(i,{V:function(){return f}});var n=e(14842),s=e(71008),r=e(35806),o=e(62193),h=e(2816),a=(e(26098),e(16584)),l=e(658),u=e(35890);e(71499),e(81027),e(82386),e(89655),e(39790),e(97741),e(22871),e(16891);function c(t){return"horizontal"===t?"row":"column"}var _=function(t){function i(){var t;return(0,s.A)(this,i),(t=(0,o.A)(this,i,arguments))._itemSize={},t._gaps={},t._padding={},t}return(0,h.A)(i,t),(0,r.A)(i,[{key:"_getDefaultConfig",value:function(){return Object.assign({},(0,u.A)(i,"_getDefaultConfig",this,3)([]),{itemSize:{width:"300px",height:"300px"},gap:"8px",padding:"match-gap"})}},{key:"_gap",get:function(){return this._gaps.row}},{key:"_idealSize",get:function(){return this._itemSize[(0,a.oV)(this.direction)]}},{key:"_idealSize1",get:function(){return this._itemSize[(0,a.oV)(this.direction)]}},{key:"_idealSize2",get:function(){return this._itemSize[(0,a.vD)(this.direction)]}},{key:"_gap1",get:function(){return this._gaps[(t=this.direction,"horizontal"===t?"column":"row")];var t}},{key:"_gap2",get:function(){return this._gaps[c(this.direction)]}},{key:"_padding1",get:function(){var t=this._padding,i="horizontal"===this.direction?["left","right"]:["top","bottom"],e=(0,l.A)(i,2),n=e[0],s=e[1];return[t[n],t[s]]}},{key:"_padding2",get:function(){var t=this._padding,i="horizontal"===this.direction?["top","bottom"]:["left","right"],e=(0,l.A)(i,2),n=e[0],s=e[1];return[t[n],t[s]]}},{key:"itemSize",set:function(t){var i=this._itemSize;"string"==typeof t&&(t={width:t,height:t});var e=parseInt(t.width),n=parseInt(t.height);e!==i.width&&(i.width=e,this._triggerReflow()),n!==i.height&&(i.height=n,this._triggerReflow())}},{key:"gap",set:function(t){this._setGap(t)}},{key:"_setGap",value:function(t){var i=t.split(" ").map((function(t){return function(t){return"auto"===t?1/0:parseInt(t)}(t)})),e=this._gaps;i[0]!==e.row&&(e.row=i[0],this._triggerReflow()),void 0===i[1]?i[0]!==e.column&&(e.column=i[0],this._triggerReflow()):i[1]!==e.column&&(e.column=i[1],this._triggerReflow())}},{key:"padding",set:function(t){var i=this._padding,e=t.split(" ").map((function(t){return function(t){return"match-gap"===t?1/0:parseInt(t)}(t)}));1===e.length?(i.top=i.right=i.bottom=i.left=e[0],this._triggerReflow()):2===e.length?(i.top=i.bottom=e[0],i.right=i.left=e[1],this._triggerReflow()):3===e.length?(i.top=e[0],i.right=i.left=e[1],i.bottom=e[2],this._triggerReflow()):4===e.length&&(["top","right","bottom","left"].forEach((function(t,n){return i[t]=e[n]})),this._triggerReflow())}}])}(a.YS),d=function(t){function i(){var t;return(0,s.A)(this,i),(t=(0,o.A)(this,i,arguments))._metrics=null,t.flex=null,t.justify=null,t}return(0,h.A)(i,t),(0,r.A)(i,[{key:"_getDefaultConfig",value:function(){return Object.assign({},(0,u.A)(i,"_getDefaultConfig",this,3)([]),{flex:!1,justify:"start"})}},{key:"gap",set:function(t){(0,u.A)(i,"_setGap",this,3)([t])}},{key:"_updateLayout",value:function(){var t=this,i=this.justify,e=(0,l.A)(this._padding1,2),n=e[0],s=e[1],r=(0,l.A)(this._padding2,2),o=r[0],h=r[1];["_gap1","_gap2"].forEach((function(e){var n=t[e];if(n===1/0&&!["space-between","space-around","space-evenly"].includes(i))throw new Error("grid layout: gap can only be set to 'auto' when justify is set to 'space-between', 'space-around' or 'space-evenly'");if(n===1/0&&"_gap2"===e)throw new Error("grid layout: ".concat(c(t.direction),"-gap cannot be set to 'auto' when direction is set to ").concat(t.direction))}));var u=this.flex||["start","center","end"].includes(i),_={rolumns:-1,itemSize1:-1,itemSize2:-1,gap1:this._gap1===1/0?-1:this._gap1,gap2:u?this._gap2:0,padding1:{start:n===1/0?this._gap1:n,end:s===1/0?this._gap1:s},padding2:u?{start:o===1/0?this._gap2:o,end:h===1/0?this._gap2:h}:{start:0,end:0},positions:[]},d=this._viewDim2-_.padding2.start-_.padding2.end;if(d<=0)_.rolumns=0;else{var f,g=u?_.gap2:0,p=0,m=0;if(d>=this._idealSize2&&(m=(p=Math.floor((d-this._idealSize2)/(this._idealSize2+g))+1)*this._idealSize2+(p-1)*g),this.flex)switch((d-m)/(this._idealSize2+g)>=.5&&(p+=1),_.rolumns=p,_.itemSize2=Math.round((d-g*(p-1))/p),!0===this.flex?"area":this.flex.preserve){case"aspect-ratio":_.itemSize1=Math.round(this._idealSize1/this._idealSize2*_.itemSize2);break;case(0,a.oV)(this.direction):_.itemSize1=Math.round(this._idealSize1);break;default:_.itemSize1=Math.round(this._idealSize1*this._idealSize2/_.itemSize2)}else _.itemSize1=this._idealSize1,_.itemSize2=this._idealSize2,_.rolumns=p;if(u){var v=_.rolumns*_.itemSize2+(_.rolumns-1)*_.gap2;f=this.flex||"start"===i?_.padding2.start:"end"===i?this._viewDim2-_.padding2.end-v:Math.round(this._viewDim2/2-v/2)}else{var y=d-_.rolumns*_.itemSize2;"space-between"===i?(_.gap2=Math.round(y/(_.rolumns-1)),f=0):"space-around"===i?(_.gap2=Math.round(y/_.rolumns),f=Math.round(_.gap2/2)):(_.gap2=Math.round(y/(_.rolumns+1)),f=_.gap2),this._gap1===1/0&&(_.gap1=_.gap2,n===1/0&&(_.padding1.start=f),s===1/0&&(_.padding1.end=f))}for(var w=0;w<_.rolumns;w++)_.positions.push(f),f+=_.itemSize2+_.gap2}this._metrics=_}}])}(_),f=function(t){return Object.assign({type:g},t)},g=function(t){function i(){return(0,s.A)(this,i),(0,o.A)(this,i,arguments)}return(0,h.A)(i,t),(0,r.A)(i,[{key:"_delta",get:function(){return this._metrics.itemSize1+this._metrics.gap1}},{key:"_getItemSize",value:function(t){return(0,n.A)((0,n.A)({},this._sizeDim,this._metrics.itemSize1),this._secondarySizeDim,this._metrics.itemSize2)}},{key:"_getActiveItems",value:function(){var t=this._metrics,i=t.rolumns;if(0===i)this._first=-1,this._last=-1,this._physicalMin=0,this._physicalMax=0;else{var e=t.padding1,n=Math.max(0,this._scrollPosition-this._overhang),s=Math.min(this._scrollSize,this._scrollPosition+this._viewDim1+this._overhang),r=Math.max(0,Math.floor((n-e.start)/this._delta)),o=Math.max(0,Math.ceil((s-e.start)/this._delta));this._first=r*i,this._last=Math.min(o*i-1,this.items.length-1),this._physicalMin=e.start+this._delta*r,this._physicalMax=e.start+this._delta*o}}},{key:"_getItemPosition",value:function(t){var i=this._metrics,e=i.rolumns,s=i.padding1,r=i.positions,o=i.itemSize1,h=i.itemSize2;return(0,n.A)((0,n.A)((0,n.A)((0,n.A)({},this._positionDim,s.start+Math.floor(t/e)*this._delta),this._secondaryPositionDim,r[t%e]),(0,a.oV)(this.direction),o),(0,a.vD)(this.direction),h)}},{key:"_updateScrollSize",value:function(){var t=this._metrics,i=t.rolumns,e=t.gap1,n=t.padding1,s=t.itemSize1,r=1;if(i>0){var o=Math.ceil(this.items.length/i);r=n.start+o*s+(o-1)*e+n.end}this._scrollSize=r}}])}(d)},16584:function(t,i,e){e.d(i,{YS:function(){return a},oV:function(){return o},vD:function(){return h}});var n=e(14842),s=e(71008),r=e(35806);e(95737),e(33822),e(26098),e(39790),e(66457),e(99019),e(96858);function o(t){return"horizontal"===t?"width":"height"}function h(t){return"horizontal"===t?"height":"width"}var a=function(){return(0,r.A)((function t(i,e){var n=this;(0,s.A)(this,t),this._latestCoords={left:0,top:0},this._direction=null,this._viewportSize={width:0,height:0},this.totalScrollSize={width:0,height:0},this.offsetWithinScroller={left:0,top:0},this._pendingReflow=!1,this._pendingLayoutUpdate=!1,this._pin=null,this._firstVisible=0,this._lastVisible=0,this._physicalMin=0,this._physicalMax=0,this._first=-1,this._last=-1,this._sizeDim="height",this._secondarySizeDim="width",this._positionDim="top",this._secondaryPositionDim="left",this._scrollPosition=0,this._scrollError=0,this._items=[],this._scrollSize=1,this._overhang=1e3,this._hostSink=i,Promise.resolve().then((function(){return n.config=e||n._getDefaultConfig()}))}),[{key:"_getDefaultConfig",value:function(){return{direction:"vertical"}}},{key:"config",get:function(){return{direction:this.direction}},set:function(t){Object.assign(this,Object.assign({},this._getDefaultConfig(),t))}},{key:"items",get:function(){return this._items},set:function(t){this._setItems(t)}},{key:"_setItems",value:function(t){t!==this._items&&(this._items=t,this._scheduleReflow())}},{key:"direction",get:function(){return this._direction},set:function(t){(t="horizontal"===t?t:"vertical")!==this._direction&&(this._direction=t,this._sizeDim="horizontal"===t?"width":"height",this._secondarySizeDim="horizontal"===t?"height":"width",this._positionDim="horizontal"===t?"left":"top",this._secondaryPositionDim="horizontal"===t?"top":"left",this._triggerReflow())}},{key:"viewportSize",get:function(){return this._viewportSize},set:function(t){var i=this._viewDim1,e=this._viewDim2;Object.assign(this._viewportSize,t),e!==this._viewDim2?this._scheduleLayoutUpdate():i!==this._viewDim1&&this._checkThresholds()}},{key:"viewportScroll",get:function(){return this._latestCoords},set:function(t){Object.assign(this._latestCoords,t);var i=this._scrollPosition;this._scrollPosition=this._latestCoords[this._positionDim],Math.abs(i-this._scrollPosition)>=1&&this._checkThresholds()}},{key:"reflowIfNeeded",value:function(){(arguments.length>0&&void 0!==arguments[0]&&arguments[0]||this._pendingReflow)&&(this._pendingReflow=!1,this._reflow())}},{key:"pin",get:function(){if(null!==this._pin){var t=this._pin,i=t.index,e=t.block;return{index:Math.max(0,Math.min(i,this.items.length-1)),block:e}}return null},set:function(t){this._pin=t,this._triggerReflow()}},{key:"_clampScrollPosition",value:function(t){return Math.max(-this.offsetWithinScroller[this._positionDim],Math.min(t,this.totalScrollSize[o(this.direction)]-this._viewDim1))}},{key:"unpin",value:function(){null!==this._pin&&(this._sendUnpinnedMessage(),this._pin=null)}},{key:"_updateLayout",value:function(){}},{key:"_viewDim1",get:function(){return this._viewportSize[this._sizeDim]}},{key:"_viewDim2",get:function(){return this._viewportSize[this._secondarySizeDim]}},{key:"_scheduleReflow",value:function(){this._pendingReflow=!0}},{key:"_scheduleLayoutUpdate",value:function(){this._pendingLayoutUpdate=!0,this._scheduleReflow()}},{key:"_triggerReflow",value:function(){var t=this;this._scheduleLayoutUpdate(),Promise.resolve().then((function(){return t.reflowIfNeeded()}))}},{key:"_reflow",value:function(){this._pendingLayoutUpdate&&(this._updateLayout(),this._pendingLayoutUpdate=!1),this._updateScrollSize(),this._setPositionFromPin(),this._getActiveItems(),this._updateVisibleIndices(),this._sendStateChangedMessage()}},{key:"_setPositionFromPin",value:function(){if(null!==this.pin){var t=this._scrollPosition,i=this.pin,e=i.index,n=i.block;this._scrollPosition=this._calculateScrollIntoViewPosition({index:e,block:n||"start"})-this.offsetWithinScroller[this._positionDim],this._scrollError=t-this._scrollPosition}}},{key:"_calculateScrollIntoViewPosition",value:function(t){var i=t.block,e=Math.min(this.items.length,Math.max(0,t.index)),n=this._getItemPosition(e)[this._positionDim],s=n;if("start"!==i){var r=this._getItemSize(e)[this._sizeDim];if("center"===i)s=n-.5*this._viewDim1+.5*r;else{var o=n-this._viewDim1+r;if("end"===i)s=o;else{var h=this._scrollPosition;s=Math.abs(h-n)<Math.abs(h-o)?n:o}}}return s+=this.offsetWithinScroller[this._positionDim],this._clampScrollPosition(s)}},{key:"getScrollIntoViewCoordinates",value:function(t){return(0,n.A)({},this._positionDim,this._calculateScrollIntoViewPosition(t))}},{key:"_sendUnpinnedMessage",value:function(){this._hostSink({type:"unpinned"})}},{key:"_sendVisibilityChangedMessage",value:function(){this._hostSink({type:"visibilityChanged",firstVisible:this._firstVisible,lastVisible:this._lastVisible})}},{key:"_sendStateChangedMessage",value:function(){var t=new Map;if(-1!==this._first&&-1!==this._last)for(var i=this._first;i<=this._last;i++)t.set(i,this._getItemPosition(i));var e={type:"stateChanged",scrollSize:(0,n.A)((0,n.A)({},this._sizeDim,this._scrollSize),this._secondarySizeDim,null),range:{first:this._first,last:this._last,firstVisible:this._firstVisible,lastVisible:this._lastVisible},childPositions:t};this._scrollError&&(e.scrollError=(0,n.A)((0,n.A)({},this._positionDim,this._scrollError),this._secondaryPositionDim,0),this._scrollError=0),this._hostSink(e)}},{key:"_num",get:function(){return-1===this._first||-1===this._last?0:this._last-this._first+1}},{key:"_checkThresholds",value:function(){if(0===this._viewDim1&&this._num>0||null!==this._pin)this._scheduleReflow();else{var t=Math.max(0,this._scrollPosition-this._overhang),i=Math.min(this._scrollSize,this._scrollPosition+this._viewDim1+this._overhang);this._physicalMin>t||this._physicalMax<i?this._scheduleReflow():this._updateVisibleIndices({emit:!0})}}},{key:"_updateVisibleIndices",value:function(t){if(-1!==this._first&&-1!==this._last){for(var i=this._first;i<this._last&&Math.round(this._getItemPosition(i)[this._positionDim]+this._getItemSize(i)[this._sizeDim])<=Math.round(this._scrollPosition);)i++;for(var e=this._last;e>this._first&&Math.round(this._getItemPosition(e)[this._positionDim])>=Math.round(this._scrollPosition+this._viewDim1);)e--;i===this._firstVisible&&e===this._lastVisible||(this._firstVisible=i,this._lastVisible=e,t&&t.emit&&this._sendVisibilityChangedMessage())}}}])}()},15798:function(t,i,e){e.d(i,{T:function(){return y}});var n=e(33994),s=e(22858),r=e(71008),o=e(35806),h=e(10362),a=e(62193),l=e(2816),u=(e(44124),e(39805),e(39790),e(66457),e(253),e(94438),e(33192)),c=e(32559),_=e(62774);e(42942),e(48062),e(54143),e(67336),e(71499),e(95737),e(99019),e(96858);var d=function(){return(0,o.A)((function t(i){(0,r.A)(this,t),this.G=i}),[{key:"disconnect",value:function(){this.G=void 0}},{key:"reconnect",value:function(t){this.G=t}},{key:"deref",value:function(){return this.G}}])}(),f=function(){return(0,o.A)((function t(){(0,r.A)(this,t),this.Y=void 0,this.Z=void 0}),[{key:"get",value:function(){return this.Y}},{key:"pause",value:function(){var t,i=this;null!==(t=this.Y)&&void 0!==t||(this.Y=new Promise((function(t){return i.Z=t})))}},{key:"resume",value:function(){var t;null===(t=this.Z)||void 0===t||t.call(this),this.Y=this.Z=void 0}}])}(),g=e(68063),p=function(t){return!(0,c.sO)(t)&&"function"==typeof t.then},m=1073741823,v=function(t){function i(){var t;return(0,r.A)(this,i),(t=(0,a.A)(this,i,arguments))._$C_t=m,t._$Cwt=[],t._$Cq=new d((0,h.A)(t)),t._$CK=new f,t}return(0,l.A)(i,t),(0,o.A)(i,[{key:"render",value:function(){for(var t,i=arguments.length,e=new Array(i),n=0;n<i;n++)e[n]=arguments[n];return null!==(t=e.find((function(t){return!p(t)})))&&void 0!==t?t:u.c0}},{key:"update",value:function(t,i){var e=this,r=this._$Cwt,o=r.length;this._$Cwt=i;var h=this._$Cq,a=this._$CK;this.isConnected||this.disconnected();for(var l,c=function(){var t=i[_];if(!p(t))return{v:(e._$C_t=_,t)};_<o&&t===r[_]||(e._$C_t=m,o=0,Promise.resolve(t).then(function(){var i=(0,s.A)((0,n.A)().mark((function i(e){var s,r;return(0,n.A)().wrap((function(i){for(;;)switch(i.prev=i.next){case 0:if(!a.get()){i.next=5;break}return i.next=3,a.get();case 3:i.next=0;break;case 5:void 0!==(s=h.deref())&&(r=s._$Cwt.indexOf(t))>-1&&r<s._$C_t&&(s._$C_t=r,s.setValue(e));case 7:case"end":return i.stop()}}),i)})));return function(t){return i.apply(this,arguments)}}()))},_=0;_<i.length&&!(_>this._$C_t);_++)if(l=c())return l.v;return u.c0}},{key:"disconnected",value:function(){this._$Cq.disconnect(),this._$CK.pause()}},{key:"reconnected",value:function(){this._$Cq.reconnect(this),this._$CK.resume()}}])}(_.Kq),y=(0,g.u$)(v)}}]);
//# sourceMappingURL=4834.17Nz40ffOcs.js.map