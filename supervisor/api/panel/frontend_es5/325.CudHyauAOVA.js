"use strict";(self.webpackChunkhome_assistant_frontend=self.webpackChunkhome_assistant_frontend||[]).push([[325],{60325:function(e,i,s){s.r(i);var a,t,o,l,d,r,c=s(33994),n=s(22858),v=s(64599),h=s(35806),u=s(71008),m=s(62193),g=s(2816),k=s(27927),p=(s(81027),s(97741),s(16891),s(67056),s(50289)),_=s(29818),f=s(94100),y=s(34897),A=(s(32885),s(77312),s(26025)),w=s(37266),P=s(6121),b=s(55321),D=(0,f.A)((function(e){var i=""!==e.host.disk_life_time?30:10,s=1e3*e.host.disk_used/60/i,a=4*e.host.startup_time/60;return 10*Math.ceil((s+a)/10)}));(0,k.A)([(0,_.EM)("dialog-hassio-datadisk")],(function(e,i){var s,k=function(i){function s(){var i;(0,u.A)(this,s);for(var a=arguments.length,t=new Array(a),o=0;o<a;o++)t[o]=arguments[o];return i=(0,m.A)(this,s,[].concat(t)),e(i),i}return(0,g.A)(s,i),(0,h.A)(s)}(i);return{F:k,d:[{kind:"field",decorators:[(0,_.MZ)({attribute:!1})],key:"hass",value:void 0},{kind:"field",decorators:[(0,_.wk)()],key:"dialogParams",value:void 0},{kind:"field",decorators:[(0,_.wk)()],key:"selectedDevice",value:void 0},{kind:"field",decorators:[(0,_.wk)()],key:"devices",value:void 0},{kind:"field",decorators:[(0,_.wk)()],key:"moving",value:function(){return!1}},{kind:"method",key:"showDialog",value:function(e){var i=this;this.dialogParams=e,(0,w.xY)(this.hass).then((function(e){i.devices=e.devices}))}},{kind:"method",key:"closeDialog",value:function(){this.dialogParams=void 0,this.selectedDevice=void 0,this.devices=void 0,this.moving=!1,(0,y.r)(this,"dialog-closed",{dialog:this.localName})}},{kind:"method",key:"render",value:function(){var e;return this.dialogParams?(0,p.qy)(a||(a=(0,v.A)([' <ha-dialog open scrimClickAction escapeKeyAction .heading="','" @closed="','" ?hideActions="','"> '," </ha-dialog> "])),this.moving?this.dialogParams.supervisor.localize("dialog.datadisk_move.moving"):this.dialogParams.supervisor.localize("dialog.datadisk_move.title"),this.closeDialog,this.moving,this.moving?(0,p.qy)(t||(t=(0,v.A)([' <ha-circular-progress aria-label="Moving" size="large" indeterminate> </ha-circular-progress> <p class="progress-text"> '," </p>"])),this.dialogParams.supervisor.localize("dialog.datadisk_move.moving_desc")):(0,p.qy)(o||(o=(0,v.A)([" ",' <mwc-button slot="secondaryAction" @click="','" dialogInitialFocus> ',' </mwc-button> <mwc-button .disabled="','" slot="primaryAction" @click="','"> '," </mwc-button>"])),null!==(e=this.devices)&&void 0!==e&&e.length?(0,p.qy)(l||(l=(0,v.A)([" ",' <br><br> <ha-select .label="','" @selected="','" dialogInitialFocus> '," </ha-select> "])),this.dialogParams.supervisor.localize("dialog.datadisk_move.description",{current_path:this.dialogParams.supervisor.os.data_disk,time:D(this.dialogParams.supervisor)}),this.dialogParams.supervisor.localize("dialog.datadisk_move.select_device"),this._select_device,this.devices.map((function(e){return(0,p.qy)(d||(d=(0,v.A)(['<mwc-list-item .value="','">',"</mwc-list-item>"])),e,e)}))):void 0===this.devices?this.dialogParams.supervisor.localize("dialog.datadisk_move.loading_devices"):this.dialogParams.supervisor.localize("dialog.datadisk_move.no_devices"),this.closeDialog,this.dialogParams.supervisor.localize("dialog.datadisk_move.cancel"),!this.selectedDevice,this._moveDatadisk,this.dialogParams.supervisor.localize("dialog.datadisk_move.move"))):p.s6}},{kind:"method",key:"_select_device",value:function(e){this.selectedDevice=e.target.value}},{kind:"method",key:"_moveDatadisk",value:(s=(0,n.A)((0,c.A)().mark((function e(){return(0,c.A)().wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return this.moving=!0,e.prev=1,e.next=4,(0,w.v9)(this.hass,this.selectedDevice);case 4:e.next=9;break;case 6:e.prev=6,e.t0=e.catch(1),this.hass.connection.connected&&!(0,A.Tv)(e.t0)&&((0,P.K$)(this,{title:this.dialogParams.supervisor.localize("system.host.failed_to_move"),text:(0,A.VR)(e.t0)}),this.closeDialog());case 9:case"end":return e.stop()}}),e,this,[[1,6]])}))),function(){return s.apply(this,arguments)})},{kind:"get",static:!0,key:"styles",value:function(){return[b.RF,b.nA,(0,p.AH)(r||(r=(0,v.A)(["ha-select{width:100%}ha-circular-progress{display:block;margin:32px;text-align:center}.progress-text{text-align:center}"])))]}}]}}),p.WF)}}]);
//# sourceMappingURL=325.CudHyauAOVA.js.map