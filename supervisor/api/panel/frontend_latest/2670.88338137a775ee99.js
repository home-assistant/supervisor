export const ids=["2670"];export const modules={53203:function(e,i,t){t.r(i),t.d(i,{HaFormFloat:function(){return s}});var a=t(44249),d=t(57243),o=t(50778),l=t(36522);t(83166);let s=(0,a.Z)([(0,o.Mo)("ha-form-float")],(function(e,i){return{F:class extends i{constructor(...i){super(...i),e(this)}},d:[{kind:"field",decorators:[(0,o.Cb)({attribute:!1})],key:"localize",value:void 0},{kind:"field",decorators:[(0,o.Cb)({attribute:!1})],key:"schema",value:void 0},{kind:"field",decorators:[(0,o.Cb)({attribute:!1})],key:"data",value:void 0},{kind:"field",decorators:[(0,o.Cb)()],key:"label",value:void 0},{kind:"field",decorators:[(0,o.Cb)()],key:"helper",value:void 0},{kind:"field",decorators:[(0,o.Cb)({type:Boolean})],key:"disabled",value:()=>!1},{kind:"field",decorators:[(0,o.IO)("ha-textfield")],key:"_input",value:void 0},{kind:"method",key:"focus",value:function(){this._input&&this._input.focus()}},{kind:"method",key:"render",value:function(){return d.dy` <ha-textfield type="numeric" inputMode="decimal" .label="${this.label}" .helper="${this.helper}" helperPersistent .value="${void 0!==this.data?this.data:""}" .disabled="${this.disabled}" .required="${this.schema.required}" .autoValidate="${this.schema.required}" .suffix="${this.schema.description?.suffix}" .validationMessage="${this.schema.required?this.localize?.("ui.common.error_required"):void 0}" @input="${this._valueChanged}"></ha-textfield> `}},{kind:"method",key:"updated",value:function(e){e.has("schema")&&this.toggleAttribute("own-margin",!!this.schema.required)}},{kind:"method",key:"_valueChanged",value:function(e){const i=e.target,t=i.value.replace(",",".");let a;if(!t.endsWith(".")&&"-"!==t)if(""!==t&&(a=parseFloat(t),isNaN(a)&&(a=void 0)),this.data!==a)(0,l.B)(this,"value-changed",{value:a});else{const e=void 0===a?"":String(a);i.value!==e&&(i.value=e)}}},{kind:"field",static:!0,key:"styles",value:()=>d.iv`:host([own-margin]){margin-bottom:5px}ha-textfield{display:block}`}]}}),d.oi)}};
//# sourceMappingURL=2670.88338137a775ee99.js.map