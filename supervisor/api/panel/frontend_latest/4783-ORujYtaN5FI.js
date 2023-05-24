"use strict";(self.webpackChunkhome_assistant_frontend=self.webpackChunkhome_assistant_frontend||[]).push([[4783],{84783:(i,t,e)=>{e.r(t);var o=e(17463),a=(e(14271),e(68144)),n=e(14243),l=e(14516),d=e(47181),r=(e(34821),e(68331),e(41682)),s=e(29748),c=e(11654);const u=(0,l.Z)((()=>[{name:"default_backup_mount",required:!0,selector:{backup_location:{}}}]));(0,o.Z)([(0,n.Mo)("dialog-hassio-backup-location")],(function(i,t){return{F:class extends t{constructor(...t){super(...t),i(this)}},d:[{kind:"field",decorators:[(0,n.Cb)({attribute:!1})],key:"hass",value:void 0},{kind:"field",decorators:[(0,n.Cb)({attribute:!1})],key:"_dialogParams",value:void 0},{kind:"field",decorators:[(0,n.SB)()],key:"_data",value:void 0},{kind:"field",decorators:[(0,n.SB)()],key:"_waiting",value:void 0},{kind:"field",decorators:[(0,n.SB)()],key:"_error",value:void 0},{kind:"method",key:"showDialog",value:async function(i){this._dialogParams=i}},{kind:"method",key:"closeDialog",value:function(){this._data=void 0,this._error=void 0,this._waiting=void 0,this._dialogParams=void 0,(0,d.B)(this,"dialog-closed",{dialog:this.localName})}},{kind:"method",key:"render",value:function(){return this._dialogParams?a.dy` <ha-dialog open scrimClickAction escapeKeyAction .heading="${this._dialogParams.supervisor.localize("dialog.backup_location.title")}" @closed="${this.closeDialog}"> ${this._error?a.dy`<ha-alert alert-type="error">${this._error}</ha-alert>`:a.Ld} <ha-form .hass="${this.hass}" .data="${this._data}" .schema="${u()}" .computeLabel="${this._computeLabelCallback}" .computeHelper="${this._computeHelperCallback}" @value-changed="${this._valueChanged}" dialogInitialFocus></ha-form> <mwc-button slot="secondaryAction" @click="${this.closeDialog}" dialogInitialFocus> ${this._dialogParams.supervisor.localize("common.cancel")} </mwc-button> <mwc-button .disabled="${this._waiting||!this._data}" slot="primaryAction" @click="${this._changeMount}"> ${this._dialogParams.supervisor.localize("common.save")} </mwc-button> </ha-dialog> `:a.Ld}},{kind:"field",key:"_computeLabelCallback",value(){return i=>this._dialogParams.supervisor.localize(`dialog.backup_location.options.${i.name}.name`)||i.name}},{kind:"field",key:"_computeHelperCallback",value(){return i=>this._dialogParams.supervisor.localize(`dialog.backup_location.options.${i.name}.description`)}},{kind:"method",key:"_valueChanged",value:function(i){const t=i.detail.value.default_backup_mount;this._data={default_backup_mount:"/backup"===t?null:t}}},{kind:"method",key:"_changeMount",value:async function(){if(this._data){this._error=void 0,this._waiting=!0;try{await(0,s.Cl)(this.hass,this._data)}catch(i){return this._error=(0,r.js)(i),void(this._waiting=!1)}this.closeDialog()}}},{kind:"get",static:!0,key:"styles",value:function(){return[c.Qx,c.yu,a.iv`.delete-btn{--mdc-theme-primary:var(--error-color)}`]}}]}}),a.oi)},34821:(i,t,e)=>{e.d(t,{i:()=>h});var o=e(17463),a=e(34541),n=e(47838),l=e(87762),d=e(91632),r=e(68144),s=e(14243),c=e(38378);e(5666);const u=["button","ha-list-item"],h=(i,t)=>r.dy` <div class="header_title">${t}</div> <ha-icon-button .label="${i.localize("ui.dialogs.generic.close")}" .path="${"M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"}" dialogAction="close" class="header_button"></ha-icon-button> `;(0,o.Z)([(0,s.Mo)("ha-dialog")],(function(i,t){class e extends t{constructor(...t){super(...t),i(this)}}return{F:e,d:[{kind:"field",key:c.gA,value:void 0},{kind:"method",key:"scrollToPos",value:function(i,t){var e;null===(e=this.contentElement)||void 0===e||e.scrollTo(i,t)}},{kind:"method",key:"renderHeading",value:function(){return r.dy`<slot name="heading"> ${(0,a.Z)((0,n.Z)(e.prototype),"renderHeading",this).call(this)} </slot>`}},{kind:"method",key:"firstUpdated",value:function(){var i;(0,a.Z)((0,n.Z)(e.prototype),"firstUpdated",this).call(this),this.suppressDefaultPressSelector=[this.suppressDefaultPressSelector,u].join(", "),this._updateScrolledAttribute(),null===(i=this.contentElement)||void 0===i||i.addEventListener("scroll",this._onScroll,{passive:!0})}},{kind:"method",key:"disconnectedCallback",value:function(){(0,a.Z)((0,n.Z)(e.prototype),"disconnectedCallback",this).call(this),this.contentElement.removeEventListener("scroll",this._onScroll)}},{kind:"field",key:"_onScroll",value(){return()=>{this._updateScrolledAttribute()}}},{kind:"method",key:"_updateScrolledAttribute",value:function(){this.contentElement&&this.toggleAttribute("scrolled",0!==this.contentElement.scrollTop)}},{kind:"field",static:!0,key:"styles",value:()=>[d.W,r.iv`:host([scrolled]) ::slotted(ha-dialog-header){border-bottom:1px solid var(--mdc-dialog-scroll-divider-color,rgba(0,0,0,.12))}.mdc-dialog{--mdc-dialog-scroll-divider-color:var(
          --dialog-scroll-divider-color,
          var(--divider-color)
        );z-index:var(--dialog-z-index,8);-webkit-backdrop-filter:var(--dialog-backdrop-filter, none);backdrop-filter:var(--dialog-backdrop-filter, none);--mdc-dialog-box-shadow:var(--dialog-box-shadow, none);--mdc-typography-headline6-font-weight:400;--mdc-typography-headline6-font-size:1.574rem}.mdc-dialog__actions{justify-content:var(--justify-action-buttons,flex-end);padding-bottom:max(env(safe-area-inset-bottom),24px)}.mdc-dialog__actions span:nth-child(1){flex:var(--secondary-action-button-flex,unset)}.mdc-dialog__actions span:nth-child(2){flex:var(--primary-action-button-flex,unset)}.mdc-dialog__container{align-items:var(--vertical-align-dialog,center)}.mdc-dialog__title{padding:24px 24px 0 24px}.mdc-dialog__actions{padding:12px 24px 12px 24px}.mdc-dialog__title::before{display:block;height:0px}.mdc-dialog .mdc-dialog__content{position:var(--dialog-content-position,relative);padding:var(--dialog-content-padding,24px)}:host([hideactions]) .mdc-dialog .mdc-dialog__content{padding-bottom:max(var(--dialog-content-padding,24px),env(safe-area-inset-bottom))}.mdc-dialog .mdc-dialog__surface{position:var(--dialog-surface-position,relative);top:var(--dialog-surface-top);margin-top:var(--dialog-surface-margin-top);min-height:var(--mdc-dialog-min-height,auto);border-radius:var(--ha-dialog-border-radius,28px)}:host([flexContent]) .mdc-dialog .mdc-dialog__content{display:flex;flex-direction:column}.header_title{margin-right:32px;margin-inline-end:32px;margin-inline-start:initial;direction:var(--direction)}.header_button{position:absolute;right:16px;top:14px;text-decoration:none;color:inherit;inset-inline-start:initial;inset-inline-end:16px;direction:var(--direction)}.dialog-actions{inset-inline-start:initial!important;inset-inline-end:0px!important;direction:var(--direction)}`]}]}}),l.M)},29748:(i,t,e)=>{e.d(t,{Cl:()=>l,eX:()=>a,mw:()=>o,rE:()=>n});let o=function(i){return i.BIND="bind",i.CIFS="cifs",i.NFS="nfs",i}({}),a=function(i){return i.BACKUP="backup",i.MEDIA="media",i}({});const n=async i=>i.callWS({type:"supervisor/api",endpoint:"/mounts",method:"get",timeout:null}),l=async(i,t)=>i.callWS({type:"supervisor/api",endpoint:"/mounts/options",method:"post",timeout:null,data:t})}}]);
//# sourceMappingURL=4783-ORujYtaN5FI.js.map