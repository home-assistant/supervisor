"use strict";(self.webpackChunkhome_assistant_frontend=self.webpackChunkhome_assistant_frontend||[]).push([["4377"],{61320:function(e,t,a){a.r(t),a.d(t,{HaSelectorSelector:()=>p});var n=a(73577),o=(a(71695),a(19423),a(13334),a(47021),a(57243)),l=a(50778),i=a(27486),s=a(36522);a(99426),a(29073);let r,d,c=e=>e;const m={number:{min:1,max:100}},u={action:[],area:[{name:"multiple",selector:{boolean:{}}}],attribute:[{name:"entity_id",selector:{entity:{}}}],boolean:[],color_temp:[{name:"unit",selector:{select:{options:["kelvin","mired"]}}},{name:"min",selector:{number:{mode:"box"}}},{name:"max",selector:{number:{mode:"box"}}}],condition:[],date:[],datetime:[],device:[{name:"multiple",selector:{boolean:{}}}],duration:[{name:"enable_day",selector:{boolean:{}}},{name:"enable_millisecond",selector:{boolean:{}}}],entity:[{name:"multiple",selector:{boolean:{}}}],floor:[{name:"multiple",selector:{boolean:{}}}],icon:[],location:[],media:[],number:[{name:"min",selector:{number:{mode:"box",step:"any"}}},{name:"max",selector:{number:{mode:"box",step:"any"}}},{name:"step",selector:{number:{mode:"box",step:"any"}}}],object:[],color_rgb:[],select:[{name:"options",selector:{object:{}}},{name:"multiple",selector:{boolean:{}}}],state:[{name:"entity_id",selector:{entity:{}}}],target:[],template:[],text:[{name:"multiple",selector:{boolean:{}}},{name:"multiline",selector:{boolean:{}}},{name:"prefix",selector:{text:{}}},{name:"suffix",selector:{text:{}}}],theme:[],time:[]};let p=(0,n.Z)([(0,l.Mo)("ha-selector-selector")],(function(e,t){return{F:class extends t{constructor(...t){super(...t),e(this)}},d:[{kind:"field",decorators:[(0,l.Cb)({attribute:!1})],key:"hass",value:void 0},{kind:"field",decorators:[(0,l.Cb)({attribute:!1})],key:"value",value:void 0},{kind:"field",decorators:[(0,l.Cb)()],key:"label",value:void 0},{kind:"field",decorators:[(0,l.Cb)()],key:"helper",value:void 0},{kind:"field",decorators:[(0,l.Cb)({type:Boolean,reflect:!0})],key:"disabled",value(){return!1}},{kind:"field",decorators:[(0,l.Cb)({type:Boolean,reflect:!0})],key:"required",value(){return!0}},{kind:"field",key:"_yamlMode",value(){return!1}},{kind:"method",key:"shouldUpdate",value:function(e){return 1!==e.size||!e.has("hass")}},{kind:"field",key:"_schema",value(){return(0,i.Z)(((e,t)=>[{name:"type",selector:{select:{mode:"dropdown",required:!0,options:Object.keys(u).concat("manual").map((e=>({label:t(`ui.components.selectors.selector.types.${e}`)||e,value:e})))}}},..."manual"===e?[{name:"manual",selector:{object:{}}}]:[],...u[e]?u[e].length>1?[{name:"",type:"expandable",title:t("ui.components.selectors.selector.options"),schema:u[e]}]:u[e]:[]]))}},{kind:"method",key:"render",value:function(){let e,t;if(this._yamlMode)t="manual",e={type:t,manual:this.value};else{t=Object.keys(this.value)[0];const a=Object.values(this.value)[0];e=Object.assign({type:t},"object"==typeof a?a:[])}const a=this._schema(t,this.hass.localize);return(0,o.dy)(r||(r=c`<ha-card> <div class="card-content"> <p>${0}</p> <ha-form .hass="${0}" .data="${0}" .schema="${0}" .computeLabel="${0}" @value-changed="${0}"></ha-form></div></ha-card>`),this.label?this.label:"",this.hass,e,a,this._computeLabelCallback,this._valueChanged)}},{kind:"method",key:"_valueChanged",value:function(e){e.stopPropagation();const t=e.detail.value,a=t.type;if(!a||"object"!=typeof t||0===Object.keys(t).length)return;const n=Object.keys(this.value)[0];if("manual"===a&&!this._yamlMode)return this._yamlMode=!0,void this.requestUpdate();if("manual"===a&&void 0===t.manual)return;let o;"manual"!==a&&(this._yamlMode=!1),delete t.type,o="manual"===a?t.manual:a===n?{[a]:Object.assign({},t.manual?t.manual[n]:t)}:{[a]:Object.assign({},m[a])},(0,s.B)(this,"value-changed",{value:o})}},{kind:"field",key:"_computeLabelCallback",value(){return e=>this.hass.localize(`ui.components.selectors.selector.${e.name}`)||e.name}},{kind:"field",static:!0,key:"styles",value(){return(0,o.iv)(d||(d=c`:host{--expansion-panel-summary-padding:0 16px}ha-alert{display:block;margin-bottom:16px}ha-card{margin:0 0 16px 0}ha-card.disabled{pointer-events:none;color:var(--disabled-text-color)}.card-content{padding:0px 16px 16px 16px}.title{font-size:16px;padding-top:16px;overflow:hidden;text-overflow:ellipsis;margin-bottom:16px;padding-left:16px;padding-right:4px;padding-inline-start:16px;padding-inline-end:4px;white-space:nowrap}`))}}]}}),o.oi)}}]);
//# sourceMappingURL=4377.1196966fab9b2eb6.js.map