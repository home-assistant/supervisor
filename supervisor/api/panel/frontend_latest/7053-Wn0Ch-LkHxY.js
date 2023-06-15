export const id=7053;export const ids=[7053];export const modules={32594:(e,t,i)=>{i.d(t,{U:()=>n});const n=e=>e.stopPropagation()},73366:(e,t,i)=>{var n=i(17463),o=i(34541),a=i(47838),s=i(61092),d=i(96762),l=i(68144),r=i(79932);(0,n.Z)([(0,r.Mo)("ha-list-item")],(function(e,t){class i extends t{constructor(...t){super(...t),e(this)}}return{F:i,d:[{kind:"method",key:"renderRipple",value:function(){return this.noninteractive?"":(0,o.Z)((0,a.Z)(i.prototype),"renderRipple",this).call(this)}},{kind:"get",static:!0,key:"styles",value:function(){return[d.W,l.iv`:host{padding-left:var(--mdc-list-side-padding-left,var(--mdc-list-side-padding,20px));padding-right:var(--mdc-list-side-padding-right,var(--mdc-list-side-padding,20px))}:host([graphic=avatar]:not([twoLine])),:host([graphic=icon]:not([twoLine])){height:48px}span.material-icons:first-of-type{margin-inline-start:0px!important;margin-inline-end:var(--mdc-list-item-graphic-margin,16px)!important;direction:var(--direction)}span.material-icons:last-of-type{margin-inline-start:auto!important;margin-inline-end:0px!important;direction:var(--direction)}.mdc-deprecated-list-item__meta{display:var(--mdc-list-item-meta-display);align-items:center}:host([multiline-secondary]){height:auto}:host([multiline-secondary]) .mdc-deprecated-list-item__text{padding:8px 0}:host([multiline-secondary]) .mdc-deprecated-list-item__secondary-text{text-overflow:initial;white-space:normal;overflow:auto;display:inline-block;margin-top:10px}:host([multiline-secondary]) .mdc-deprecated-list-item__primary-text{margin-top:10px}:host([multiline-secondary]) .mdc-deprecated-list-item__secondary-text::before{display:none}:host([multiline-secondary]) .mdc-deprecated-list-item__primary-text::before{display:none}:host([disabled]){color:var(--disabled-text-color)}:host([noninteractive]){pointer-events:unset}`]}}]}}),s.K)},86630:(e,t,i)=>{var n=i(17463),o=i(34541),a=i(47838),s=i(49412),d=i(3762),l=i(68144),r=i(79932),c=i(38346),p=i(96151);(0,n.Z)([(0,r.Mo)("ha-select")],(function(e,t){class i extends t{constructor(...t){super(...t),e(this)}}return{F:i,d:[{kind:"field",decorators:[(0,r.Cb)({type:Boolean})],key:"icon",value:void 0},{kind:"method",key:"renderLeadingIcon",value:function(){return this.icon?l.dy`<span class="mdc-select__icon"><slot name="icon"></slot></span>`:l.Ld}},{kind:"method",key:"connectedCallback",value:function(){(0,o.Z)((0,a.Z)(i.prototype),"connectedCallback",this).call(this),window.addEventListener("translations-updated",this._translationsUpdated)}},{kind:"method",key:"disconnectedCallback",value:function(){(0,o.Z)((0,a.Z)(i.prototype),"disconnectedCallback",this).call(this),window.removeEventListener("translations-updated",this._translationsUpdated)}},{kind:"field",key:"_translationsUpdated",value(){return(0,c.D)((async()=>{await(0,p.y)(),this.layoutOptions()}),500)}},{kind:"field",static:!0,key:"styles",value:()=>[d.W,l.iv`.mdc-select:not(.mdc-select--disabled) .mdc-select__icon{color:var(--secondary-text-color)}.mdc-select__anchor{width:var(--ha-select-min-width,200px)}.mdc-select--filled .mdc-floating-label{inset-inline-start:12px;inset-inline-end:initial;direction:var(--direction)}.mdc-select--filled.mdc-select--with-leading-icon .mdc-floating-label{inset-inline-start:48px;inset-inline-end:initial;direction:var(--direction)}.mdc-select .mdc-select__anchor{padding-inline-start:12px;padding-inline-end:0px;direction:var(--direction)}.mdc-select__anchor .mdc-floating-label--float-above{transform-origin:var(--float-start)}`]}]}}),s.K)},67053:(e,t,i)=>{i.r(t),i.d(t,{HaConversationAgentSelector:()=>f});var n=i(17463),o=i(68144),a=i(79932),s=i(34541),d=i(47838),l=i(47181),r=i(32594),c=i(38346),p=i(81582);var h=i(5986);const u=(e,t)=>{var i;return e.callApi("POST","config/config_entries/options/flow",{handler:t,show_advanced_options:Boolean(null===(i=e.userData)||void 0===i?void 0:i.showAdvanced)})},m=(e,t)=>e.callApi("GET",`config/config_entries/options/flow/${t}`),v=(e,t,i)=>e.callApi("POST",`config/config_entries/options/flow/${t}`,i),g=(e,t)=>e.callApi("DELETE",`config/config_entries/options/flow/${t}`);var y=i(52871);i(73366),i(86630);const _="__NONE_OPTION__";(0,n.Z)([(0,a.Mo)("ha-conversation-agent-picker")],(function(e,t){class i extends t{constructor(...t){super(...t),e(this)}}return{F:i,d:[{kind:"field",decorators:[(0,a.Cb)()],key:"value",value:void 0},{kind:"field",decorators:[(0,a.Cb)()],key:"language",value:void 0},{kind:"field",decorators:[(0,a.Cb)()],key:"label",value:void 0},{kind:"field",decorators:[(0,a.Cb)({attribute:!1})],key:"hass",value:void 0},{kind:"field",decorators:[(0,a.Cb)({type:Boolean,reflect:!0})],key:"disabled",value:()=>!1},{kind:"field",decorators:[(0,a.Cb)({type:Boolean})],key:"required",value:()=>!1},{kind:"field",decorators:[(0,a.SB)()],key:"_agents",value:void 0},{kind:"field",decorators:[(0,a.SB)()],key:"_configEntry",value:void 0},{kind:"method",key:"render",value:function(){var e,t,i;if(!this._agents)return o.Ld;const n=null!==(e=this.value)&&void 0!==e?e:this.required&&(!this.language||null!==(t=this._agents.find((e=>"homeassistant"===e.id)))&&void 0!==t&&t.supported_languages.includes(this.language))?"homeassistant":_;return o.dy` <ha-select .label="${this.label||this.hass.localize("ui.components.coversation-agent-picker.conversation_agent")}" .value="${n}" .required="${this.required}" .disabled="${this.disabled}" @selected="${this._changed}" @closed="${r.U}" fixedMenuPosition naturalMenuWidth> ${this.required?o.Ld:o.dy`<ha-list-item .value="${_}"> ${this.hass.localize("ui.components.coversation-agent-picker.none")} </ha-list-item>`} ${this._agents.map((e=>o.dy`<ha-list-item .value="${e.id}" .disabled="${"*"!==e.supported_languages&&0===e.supported_languages.length}"> ${e.name} </ha-list-item>`))}</ha-select>${null!==(i=this._configEntry)&&void 0!==i&&i.supports_options?o.dy`<ha-icon-button .path="${"M12,15.5A3.5,3.5 0 0,1 8.5,12A3.5,3.5 0 0,1 12,8.5A3.5,3.5 0 0,1 15.5,12A3.5,3.5 0 0,1 12,15.5M19.43,12.97C19.47,12.65 19.5,12.33 19.5,12C19.5,11.67 19.47,11.34 19.43,11L21.54,9.37C21.73,9.22 21.78,8.95 21.66,8.73L19.66,5.27C19.54,5.05 19.27,4.96 19.05,5.05L16.56,6.05C16.04,5.66 15.5,5.32 14.87,5.07L14.5,2.42C14.46,2.18 14.25,2 14,2H10C9.75,2 9.54,2.18 9.5,2.42L9.13,5.07C8.5,5.32 7.96,5.66 7.44,6.05L4.95,5.05C4.73,4.96 4.46,5.05 4.34,5.27L2.34,8.73C2.21,8.95 2.27,9.22 2.46,9.37L4.57,11C4.53,11.34 4.5,11.67 4.5,12C4.5,12.33 4.53,12.65 4.57,12.97L2.46,14.63C2.27,14.78 2.21,15.05 2.34,15.27L4.34,18.73C4.46,18.95 4.73,19.03 4.95,18.95L7.44,17.94C7.96,18.34 8.5,18.68 9.13,18.93L9.5,21.58C9.54,21.82 9.75,22 10,22H14C14.25,22 14.46,21.82 14.5,21.58L14.87,18.93C15.5,18.67 16.04,18.34 16.56,17.94L19.05,18.95C19.27,19.03 19.54,18.95 19.66,18.73L21.66,15.27C21.78,15.05 21.73,14.78 21.54,14.63L19.43,12.97Z"}" @click="${this._openOptionsFlow}"></ha-icon-button>`:""} `}},{kind:"method",key:"willUpdate",value:function(e){(0,s.Z)((0,d.Z)(i.prototype),"willUpdate",this).call(this,e),this.hasUpdated?e.has("language")&&this._debouncedUpdateAgents():this._updateAgents(),e.has("value")&&this._maybeFetchConfigEntry()}},{kind:"method",key:"_maybeFetchConfigEntry",value:async function(){if(this.value&&"homeassistant"!==this.value)try{this._configEntry=(await(0,p.RQ)(this.hass,this.value)).config_entry}catch(e){this._configEntry=void 0}else this._configEntry=void 0}},{kind:"field",key:"_debouncedUpdateAgents",value(){return(0,c.D)((()=>this._updateAgents()),500)}},{kind:"method",key:"_updateAgents",value:async function(){const{agents:e}=await(t=this.hass,i=this.language,n=this.hass.config.country||void 0,t.callWS({type:"conversation/agent/list",language:i,country:n}));var t,i,n;if(this._agents=e,!this.value)return;const o=e.find((e=>e.id===this.value));(0,l.B)(this,"supported-languages-changed",{value:null==o?void 0:o.supported_languages}),(!o||"*"!==o.supported_languages&&0===o.supported_languages.length)&&(this.value=void 0,(0,l.B)(this,"value-changed",{value:this.value}))}},{kind:"method",key:"_openOptionsFlow",value:async function(){var e,t,i;this._configEntry&&(e=this,t=this._configEntry,i=await(0,h.t4)(this.hass,this._configEntry.domain),(0,y.w)(e,{startFlowHandler:t.entry_id,domain:t.domain,manifest:i},{loadDevicesAndAreas:!1,createFlow:async(e,i)=>{const[n]=await Promise.all([u(e,i),e.loadBackendTranslation("options",t.domain),e.loadBackendTranslation("selector",t.domain)]);return n},fetchFlow:async(e,i)=>{const[n]=await Promise.all([m(e,i),e.loadBackendTranslation("options",t.domain),e.loadBackendTranslation("selector",t.domain)]);return n},handleFlowStep:v,deleteFlow:g,renderAbortDescription(e,i){const n=e.localize(`component.${t.domain}.options.abort.${i.reason}`,i.description_placeholders);return n?o.dy` <ha-markdown breaks allowsvg .content="${n}"></ha-markdown> `:""},renderShowFormStepHeader:(e,i)=>e.localize(`component.${t.domain}.options.step.${i.step_id}.title`,i.description_placeholders)||e.localize("ui.dialogs.options_flow.form.header"),renderShowFormStepDescription(e,i){const n=e.localize(`component.${t.domain}.options.step.${i.step_id}.description`,i.description_placeholders);return n?o.dy` <ha-markdown allowsvg breaks .content="${n}"></ha-markdown> `:""},renderShowFormStepFieldLabel:(e,i,n)=>e.localize(`component.${t.domain}.options.step.${i.step_id}.data.${n.name}`),renderShowFormStepFieldHelper(e,i,n){const a=e.localize(`component.${t.domain}.options.step.${i.step_id}.data_description.${n.name}`,i.description_placeholders);return a?o.dy`<ha-markdown breaks .content="${a}"></ha-markdown>`:""},renderShowFormStepFieldError:(e,i,n)=>e.localize(`component.${t.domain}.options.error.${n}`,i.description_placeholders),renderShowFormStepFieldLocalizeValue:(e,i,n)=>e.localize(`component.${t.domain}.selector.${n}`),renderShowFormStepSubmitButton:(e,i)=>e.localize(`component.${t.domain}.options.step.${i.step_id}.submit`)||e.localize("ui.panel.config.integrations.config_flow."+(!1===i.last_step?"next":"submit")),renderExternalStepHeader:(e,t)=>"",renderExternalStepDescription:(e,t)=>"",renderCreateEntryDescription:(e,t)=>o.dy` <p>${e.localize("ui.dialogs.options_flow.success.description")}</p> `,renderShowFormProgressHeader:(e,i)=>e.localize(`component.${t.domain}.options.step.${i.step_id}.title`)||e.localize(`component.${t.domain}.title`),renderShowFormProgressDescription(e,i){const n=e.localize(`component.${t.domain}.options.progress.${i.progress_action}`,i.description_placeholders);return n?o.dy` <ha-markdown allowsvg breaks .content="${n}"></ha-markdown> `:""},renderMenuHeader:(e,i)=>e.localize(`component.${t.domain}.options.step.${i.step_id}.title`)||e.localize(`component.${t.domain}.title`),renderMenuDescription(e,i){const n=e.localize(`component.${t.domain}.options.step.${i.step_id}.description`,i.description_placeholders);return n?o.dy` <ha-markdown allowsvg breaks .content="${n}"></ha-markdown> `:""},renderMenuOption:(e,i,n)=>e.localize(`component.${t.domain}.options.step.${i.step_id}.menu_options.${n}`,i.description_placeholders),renderLoadingDescription:(e,i)=>e.localize(`component.${t.domain}.options.loading`)||("loading_flow"===i||"loading_step"===i?e.localize(`ui.dialogs.options_flow.loading.${i}`,{integration:(0,h.Lh)(e.localize,t.domain)}):"")}))}},{kind:"get",static:!0,key:"styles",value:function(){return o.iv`:host{display:flex;align-items:center}ha-select{width:100%}ha-icon-button{color:var(--secondary-text-color)}`}},{kind:"method",key:"_changed",value:function(e){var t;const i=e.target;!this.hass||""===i.value||i.value===this.value||void 0===this.value&&i.value===_||(this.value=i.value===_?void 0:i.value,(0,l.B)(this,"value-changed",{value:this.value}),(0,l.B)(this,"supported-languages-changed",{value:null===(t=this._agents.find((e=>e.id===this.value)))||void 0===t?void 0:t.supported_languages}))}}]}}),o.oi);let f=(0,n.Z)([(0,a.Mo)("ha-selector-conversation_agent")],(function(e,t){return{F:class extends t{constructor(...t){super(...t),e(this)}},d:[{kind:"field",decorators:[(0,a.Cb)()],key:"hass",value:void 0},{kind:"field",decorators:[(0,a.Cb)()],key:"selector",value:void 0},{kind:"field",decorators:[(0,a.Cb)()],key:"value",value:void 0},{kind:"field",decorators:[(0,a.Cb)()],key:"label",value:void 0},{kind:"field",decorators:[(0,a.Cb)()],key:"helper",value:void 0},{kind:"field",decorators:[(0,a.Cb)({type:Boolean})],key:"disabled",value:()=>!1},{kind:"field",decorators:[(0,a.Cb)({type:Boolean})],key:"required",value:()=>!0},{kind:"field",decorators:[(0,a.Cb)({attribute:!1})],key:"context",value:void 0},{kind:"method",key:"render",value:function(){var e,t;return o.dy`<ha-conversation-agent-picker .hass="${this.hass}" .value="${this.value}" .language="${(null===(e=this.selector.conversation_agent)||void 0===e?void 0:e.language)||(null===(t=this.context)||void 0===t?void 0:t.language)}" .label="${this.label}" .helper="${this.helper}" .disabled="${this.disabled}" .required="${this.required}"></ha-conversation-agent-picker>`}},{kind:"field",static:!0,key:"styles",value:()=>o.iv`ha-conversation-agent-picker{width:100%}`}]}}),o.oi)},81582:(e,t,i)=>{i.d(t,{RQ:()=>o,pB:()=>n});const n=(e,t)=>{const i={};return t&&(t.type&&(i.type_filter=t.type),t.domain&&(i.domain=t.domain)),e.callWS({type:"config_entries/get",...i})},o=(e,t)=>e.callWS({type:"config_entries/get_single",entry_id:t})},5986:(e,t,i)=>{i.d(t,{Lh:()=>n,t4:()=>o});const n=(e,t,i)=>e(`component.${t}.title`)||(null==i?void 0:i.name)||t,o=(e,t)=>e.callWS({type:"manifest/get",integration:t})},52871:(e,t,i)=>{i.d(t,{w:()=>a});var n=i(47181);const o=()=>Promise.all([i.e(8133),i.e(7270),i.e(8597),i.e(7210),i.e(4171)]).then(i.bind(i,24171)),a=(e,t,i)=>{(0,n.B)(e,"show-dialog",{dialogTag:"dialog-data-entry-flow",dialogImport:o,dialogParams:{...t,flowConfig:i,dialogParentElement:e}})}}};
//# sourceMappingURL=7053-Wn0Ch-LkHxY.js.map