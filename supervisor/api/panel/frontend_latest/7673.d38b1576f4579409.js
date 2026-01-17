export const __rspack_esm_id="7673";export const __rspack_esm_ids=["7673"];export const __webpack_modules__={93444(e,t,a){var o=a(62826),i=a(96196),r=a(77845);class s extends i.WF{render(){return i.qy` <footer> <slot name="secondaryAction"></slot> <slot name="primaryAction"></slot> </footer> `}static get styles(){return[i.AH`footer{display:flex;gap:var(--ha-space-3);justify-content:flex-end;align-items:center;width:100%}`]}}s=(0,o.Cg)([(0,r.EM)("ha-dialog-footer")],s)},76538(e,t,a){var o=a(62826),i=a(96196),r=a(77845);class s extends i.WF{render(){const e=i.qy`<div class="header-title"> <slot name="title"></slot> </div>`,t=i.qy`<div class="header-subtitle"> <slot name="subtitle"></slot> </div>`;return i.qy` <header class="header"> <div class="header-bar"> <section class="header-navigation-icon"> <slot name="navigationIcon"></slot> </section> <section class="header-content"> ${"above"===this.subtitlePosition?i.qy`${t}${e}`:i.qy`${e}${t}`} </section> <section class="header-action-items"> <slot name="actionItems"></slot> </section> </div> <slot></slot> </header> `}static get styles(){return[i.AH`:host{display:block}:host([show-border]){border-bottom:1px solid var(--mdc-dialog-scroll-divider-color,rgba(0,0,0,.12))}.header-bar{display:flex;flex-direction:row;align-items:center;padding:0 var(--ha-space-1);box-sizing:border-box}.header-content{flex:1;padding:10px var(--ha-space-1);display:flex;flex-direction:column;justify-content:center;min-height:var(--ha-space-12);min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.header-title{height:var(--ha-dialog-header-title-height,calc(var(--ha-font-size-xl) + var(--ha-space-1)));font-size:var(--ha-font-size-xl);line-height:var(--ha-line-height-condensed);font-weight:var(--ha-font-weight-medium);color:var(--ha-dialog-header-title-color,var(--primary-text-color))}.header-subtitle{font-size:var(--ha-font-size-m);line-height:var(--ha-line-height-normal);color:var(--ha-dialog-header-subtitle-color,var(--secondary-text-color))}@media all and (min-width:450px) and (min-height:500px){.header-bar{padding:0 var(--ha-space-2)}}.header-navigation-icon{flex:none;min-width:var(--ha-space-2);height:100%;display:flex;flex-direction:row}.header-action-items{flex:none;min-width:var(--ha-space-2);height:100%;display:flex;flex-direction:row}`]}constructor(...e){super(...e),this.subtitlePosition="below",this.showBorder=!1}}(0,o.Cg)([(0,r.MZ)({type:String,attribute:"subtitle-position"})],s.prototype,"subtitlePosition",void 0),(0,o.Cg)([(0,r.MZ)({type:Boolean,reflect:!0,attribute:"show-border"})],s.prototype,"showBorder",void 0),s=(0,o.Cg)([(0,r.EM)("ha-dialog-header")],s)},45331(e,t,a){a.a(e,async function(e,t){try{var o=a(62826),i=a(93900),r=a(96196),s=a(77845),l=a(32288),d=a(1087),h=a(59992),n=a(14503),c=(a(76538),a(50888),e([i]));i=(c.then?(await c)():c)[0];const p="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z";class g extends((0,h.V)(r.WF)){get scrollableElement(){return this.bodyContainer}updated(e){super.updated(e),e.has("open")&&(this._open=this.open)}render(){return r.qy` <wa-dialog .open="${this._open}" .lightDismiss="${!this.preventScrimClose}" without-header aria-labelledby="${(0,l.J)(this.ariaLabelledBy||(void 0!==this.headerTitle?"ha-wa-dialog-title":void 0))}" aria-describedby="${(0,l.J)(this.ariaDescribedBy)}" @wa-show="${this._handleShow}" @wa-after-show="${this._handleAfterShow}" @wa-after-hide="${this._handleAfterHide}"> <slot name="header"> <ha-dialog-header .subtitlePosition="${this.headerSubtitlePosition}" .showBorder="${this._bodyScrolled}"> <slot name="headerNavigationIcon" slot="navigationIcon"> <ha-icon-button data-dialog="close" .label="${this.hass?.localize("ui.common.close")??"Close"}" .path="${p}"></ha-icon-button> </slot> ${void 0!==this.headerTitle?r.qy`<span slot="title" class="title" id="ha-wa-dialog-title"> ${this.headerTitle} </span>`:r.qy`<slot name="headerTitle" slot="title"></slot>`} ${void 0!==this.headerSubtitle?r.qy`<span slot="subtitle">${this.headerSubtitle}</span>`:r.qy`<slot name="headerSubtitle" slot="subtitle"></slot>`} <slot name="headerActionItems" slot="actionItems"></slot> </ha-dialog-header> </slot> <div class="content-wrapper"> <div class="body ha-scrollbar" @scroll="${this._handleBodyScroll}"> <slot></slot> </div> ${this.renderScrollableFades()} </div> <slot name="footer" slot="footer"></slot> </wa-dialog> `}disconnectedCallback(){super.disconnectedCallback(),this._open=!1}_handleBodyScroll(e){this._bodyScrolled=e.target.scrollTop>0}static get styles(){return[...super.styles,n.dp,r.AH`
        wa-dialog {
          --full-width: var(
            --ha-dialog-width-full,
            min(95vw, var(--safe-width))
          );
          --width: min(var(--ha-dialog-width-md, 580px), var(--full-width));
          --spacing: var(--dialog-content-padding, var(--ha-space-6));
          --show-duration: var(--ha-dialog-show-duration, 200ms);
          --hide-duration: var(--ha-dialog-hide-duration, 200ms);
          --ha-dialog-surface-background: var(
            --card-background-color,
            var(--ha-color-surface-default)
          );
          --wa-color-surface-raised: var(
            --ha-dialog-surface-background,
            var(--card-background-color, var(--ha-color-surface-default))
          );
          --wa-panel-border-radius: var(
            --ha-dialog-border-radius,
            var(--ha-border-radius-3xl)
          );
          max-width: var(--ha-dialog-max-width, var(--safe-width));
        }
        @media (prefers-reduced-motion: reduce) {
          wa-dialog {
            --show-duration: 0ms;
            --hide-duration: 0ms;
          }
        }

        :host([width="small"]) wa-dialog {
          --width: min(var(--ha-dialog-width-sm, 320px), var(--full-width));
        }

        :host([width="large"]) wa-dialog {
          --width: min(var(--ha-dialog-width-lg, 1024px), var(--full-width));
        }

        :host([width="full"]) wa-dialog {
          --width: var(--full-width);
        }

        wa-dialog::part(dialog) {
          min-width: var(--width, var(--full-width));
          max-width: var(--width, var(--full-width));
          max-height: var(
            --ha-dialog-max-height,
            calc(var(--safe-height) - var(--ha-space-20))
          );
          min-height: var(--ha-dialog-min-height);
          margin-top: var(--dialog-surface-margin-top, auto);
          /* Used to offset the dialog from the safe areas when space is limited */
          transform: translate(
            calc(
              var(--safe-area-offset-left, 0px) - var(
                  --safe-area-offset-right,
                  0px
                )
            ),
            calc(
              var(--safe-area-offset-top, 0px) - var(
                  --safe-area-offset-bottom,
                  0px
                )
            )
          );
          display: flex;
          flex-direction: column;
          overflow: hidden;
        }

        @media all and (max-width: 450px), all and (max-height: 500px) {
          :host([type="standard"]) {
            --ha-dialog-border-radius: 0;

            wa-dialog {
              /* Make the container fill the whole screen width and not the safe width */
              --full-width: var(--ha-dialog-width-full, 100vw);
              --width: var(--full-width);
            }

            wa-dialog::part(dialog) {
              /* Make the dialog fill the whole screen height and not the safe height */
              min-height: var(--ha-dialog-min-height, 100vh);
              min-height: var(--ha-dialog-min-height, 100dvh);
              max-height: var(--ha-dialog-max-height, 100vh);
              max-height: var(--ha-dialog-max-height, 100dvh);
              margin-top: 0;
              margin-bottom: 0;
              /* Use safe area as padding instead of the container size */
              padding-top: var(--safe-area-inset-top);
              padding-bottom: var(--safe-area-inset-bottom);
              padding-left: var(--safe-area-inset-left);
              padding-right: var(--safe-area-inset-right);
              /* Reset the transform to center the dialog */
              transform: none;
            }
          }
        }

        .header-title-container {
          display: flex;
          align-items: center;
        }

        .header-title {
          margin: 0;
          margin-bottom: 0;
          color: var(--ha-dialog-header-title-color, var(--primary-text-color));
          font-size: var(
            --ha-dialog-header-title-font-size,
            var(--ha-font-size-2xl)
          );
          line-height: var(
            --ha-dialog-header-title-line-height,
            var(--ha-line-height-condensed)
          );
          font-weight: var(
            --ha-dialog-header-title-font-weight,
            var(--ha-font-weight-normal)
          );
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
          margin-right: var(--ha-space-3);
        }

        wa-dialog::part(body) {
          padding: 0;
          display: flex;
          flex-direction: column;
          max-width: 100%;
          overflow: hidden;
        }

        .content-wrapper {
          position: relative;
          flex: 1;
          display: flex;
          flex-direction: column;
          min-height: 0;
        }

        .body {
          position: var(--dialog-content-position, relative);
          padding: var(
            --dialog-content-padding,
            0 var(--ha-space-6) var(--ha-space-6) var(--ha-space-6)
          );
          overflow: auto;
          flex-grow: 1;
        }
        :host([flexcontent]) .body {
          max-width: 100%;
          flex: 1;
          display: flex;
          flex-direction: column;
        }

        wa-dialog::part(footer) {
          padding: 0;
        }

        ::slotted([slot="footer"]) {
          display: flex;
          padding: var(--ha-space-3) var(--ha-space-4) var(--ha-space-4)
            var(--ha-space-4);
          gap: var(--ha-space-3);
          justify-content: flex-end;
          align-items: center;
          width: 100%;
        }
      `]}constructor(...e){super(...e),this.open=!1,this.type="standard",this.width="medium",this.preventScrimClose=!1,this.headerSubtitlePosition="below",this.flexContent=!1,this._open=!1,this._bodyScrolled=!1,this._handleShow=async()=>{this._open=!0,(0,d.r)(this,"opened"),await this.updateComplete,requestAnimationFrame(()=>{this.querySelector("[autofocus]")?.focus()})},this._handleAfterShow=()=>{(0,d.r)(this,"after-show")},this._handleAfterHide=()=>{this._open=!1,(0,d.r)(this,"closed")}}}(0,o.Cg)([(0,s.MZ)({attribute:!1})],g.prototype,"hass",void 0),(0,o.Cg)([(0,s.MZ)({attribute:"aria-labelledby"})],g.prototype,"ariaLabelledBy",void 0),(0,o.Cg)([(0,s.MZ)({attribute:"aria-describedby"})],g.prototype,"ariaDescribedBy",void 0),(0,o.Cg)([(0,s.MZ)({type:Boolean,reflect:!0})],g.prototype,"open",void 0),(0,o.Cg)([(0,s.MZ)({reflect:!0})],g.prototype,"type",void 0),(0,o.Cg)([(0,s.MZ)({type:String,reflect:!0,attribute:"width"})],g.prototype,"width",void 0),(0,o.Cg)([(0,s.MZ)({type:Boolean,reflect:!0,attribute:"prevent-scrim-close"})],g.prototype,"preventScrimClose",void 0),(0,o.Cg)([(0,s.MZ)({attribute:"header-title"})],g.prototype,"headerTitle",void 0),(0,o.Cg)([(0,s.MZ)({attribute:"header-subtitle"})],g.prototype,"headerSubtitle",void 0),(0,o.Cg)([(0,s.MZ)({type:String,attribute:"header-subtitle-position"})],g.prototype,"headerSubtitlePosition",void 0),(0,o.Cg)([(0,s.MZ)({type:Boolean,reflect:!0,attribute:"flexcontent"})],g.prototype,"flexContent",void 0),(0,o.Cg)([(0,s.wk)()],g.prototype,"_open",void 0),(0,o.Cg)([(0,s.P)(".body")],g.prototype,"bodyContainer",void 0),(0,o.Cg)([(0,s.wk)()],g.prototype,"_bodyScrolled",void 0),(0,o.Cg)([(0,s.Ls)({passive:!0})],g.prototype,"_handleBodyScroll",null),g=(0,o.Cg)([(0,s.EM)("ha-wa-dialog")],g),t()}catch(e){t(e)}})},97424(e,t,a){a.a(e,async function(e,o){try{a.r(t),a.d(t,{HaImagecropperDialog:()=>m});a(14603),a(47566),a(98721);var i=a(62826),r=a(23318),s=a.n(r),l=a(32609),d=a(96196),h=a(77845),n=a(94333),c=a(1087),p=a(18350),g=(a(93444),a(45331)),u=a(14503),v=e([p,g]);[p,g]=v.then?(await v)():v;class m extends d.WF{showDialog(e){this._params=e,this._open=!0}closeDialog(){return this._open=!1,this._cropper?.destroy(),this._cropper=void 0,this._isTargetAspectRatio=!1,!0}_dialogClosed(){this._params=void 0,(0,c.r)(this,"dialog-closed",{dialog:this.localName})}updated(e){e.has("_params")&&this._params&&(this._cropper?this._cropper.replace(URL.createObjectURL(this._params.file)):(this._image.src=URL.createObjectURL(this._params.file),this._cropper=new(s())(this._image,{aspectRatio:this._params.options.aspectRatio,viewMode:1,dragMode:"move",minCropBoxWidth:50,ready:()=>{this._isTargetAspectRatio=this._checkMatchAspectRatio(),URL.revokeObjectURL(this._image.src)}})))}_checkMatchAspectRatio(){const e=this._params?.options.aspectRatio;if(!e)return!0;const t=this._cropper.getImageData();if(t.aspectRatio===e)return!0;if(t.naturalWidth>t.naturalHeight){const a=t.naturalWidth/e;return Math.abs(a-t.naturalHeight)<=1}const a=t.naturalHeight*e;return Math.abs(a-t.naturalWidth)<=1}render(){return this._params?d.qy` <ha-wa-dialog .hass="${this.hass}" .open="${this._open}" header-title="${this.hass.localize("ui.dialogs.image_cropper.crop_image")}" @closed="${this._dialogClosed}"> <div class="container ${(0,n.H)({round:Boolean(this._params?.options.round)})}"> <img alt="${this.hass.localize("ui.dialogs.image_cropper.crop_image")}"> </div> <ha-dialog-footer slot="footer"> <ha-button slot="secondaryAction" appearance="plain" @click="${this.closeDialog}"> ${this.hass.localize("ui.common.cancel")} </ha-button> ${this._isTargetAspectRatio?d.qy` <ha-button slot="secondaryAction" appearance="plain" @click="${this._useOriginal}"> ${this.hass.localize("ui.dialogs.image_cropper.use_original")} </ha-button> `:d.s6} <ha-button slot="primaryAction" @click="${this._cropImage}"> ${this.hass.localize("ui.dialogs.image_cropper.crop")} </ha-button> </ha-dialog-footer> </ha-wa-dialog> `:d.s6}_cropImage(){this._cropper.getCroppedCanvas().toBlob(e=>{if(!e)return;const t=new File([e],this._params.file.name,{type:this._params.options.type||this._params.file.type});this._params.croppedCallback(t),this.closeDialog()},this._params.options.type||this._params.file.type,this._params.options.quality)}_useOriginal(){this._params.croppedCallback(this._params.file),this.closeDialog()}static get styles(){return[u.nA,d.AH`${(0,d.iz)(l)} .container{max-width:640px}img{max-width:100%}.container.round .cropper-face,.container.round .cropper-view-box{border-radius:var(--ha-border-radius-circle)}.cropper-line,.cropper-point,.cropper-point.point-se::before{background-color:var(--primary-color)}`]}constructor(...e){super(...e),this._open=!1}}(0,i.Cg)([(0,h.MZ)({attribute:!1})],m.prototype,"hass",void 0),(0,i.Cg)([(0,h.wk)()],m.prototype,"_params",void 0),(0,i.Cg)([(0,h.wk)()],m.prototype,"_open",void 0),(0,i.Cg)([(0,h.P)("img",!0)],m.prototype,"_image",void 0),(0,i.Cg)([(0,h.wk)()],m.prototype,"_isTargetAspectRatio",void 0),m=(0,i.Cg)([(0,h.EM)("image-cropper-dialog")],m),o()}catch(e){o(e)}})},59992(e,t,a){a.d(t,{V:()=>d});var o=a(62826),i=a(88696),r=a(96196),s=a(94333),l=a(77845);const d=e=>{class t extends e{get scrollableElement(){return t.DEFAULT_SCROLLABLE_ELEMENT}firstUpdated(e){super.firstUpdated?.(e),this.scrollableElement&&this._updateScrollableState(this.scrollableElement),this._attachScrollableElement()}updated(e){super.updated?.(e),this._attachScrollableElement()}disconnectedCallback(){this._detachScrollableElement(),this._contentScrolled=!1,this._contentScrollable=!1,super.disconnectedCallback()}renderScrollableFades(e=!1){return r.qy` <div class="${(0,s.H)({"fade-top":!0,rounded:e,visible:this._contentScrolled})}"></div> <div class="${(0,s.H)({"fade-bottom":!0,rounded:e,visible:this._contentScrollable})}"></div> `}static get styles(){const e=Object.getPrototypeOf(this);var t;return[...void 0===(t=e?.styles??[])?[]:Array.isArray(t)?t:[t],r.AH`.fade-bottom,.fade-top{position:absolute;left:0;right:0;height:var(--ha-space-2);pointer-events:none;transition:opacity 180ms ease-in-out;border-radius:var(--ha-border-radius-square);opacity:0;background:linear-gradient(to bottom,var(--ha-color-shadow-scrollable-fade),transparent)}.fade-top{top:0}.fade-bottom{bottom:0;transform:rotate(180deg)}.fade-bottom.visible,.fade-top.visible{opacity:1}.fade-bottom.rounded,.fade-top.rounded{border-radius:var(--ha-card-border-radius,var(--ha-border-radius-lg));border-bottom-left-radius:var(--ha-border-radius-square);border-bottom-right-radius:var(--ha-border-radius-square)}.fade-top.rounded{border-top-left-radius:var(--ha-border-radius-square);border-top-right-radius:var(--ha-border-radius-square)}.fade-bottom.rounded{border-bottom-left-radius:var(--ha-border-radius-square);border-bottom-right-radius:var(--ha-border-radius-square)}`]}_attachScrollableElement(){const e=this.scrollableElement;e!==this._scrollTarget&&(this._detachScrollableElement(),e&&(this._scrollTarget=e,e.addEventListener("scroll",this._onScroll,{passive:!0}),this._resize.observe(e),this._updateScrollableState(e)))}_detachScrollableElement(){this._scrollTarget&&(this._scrollTarget.removeEventListener("scroll",this._onScroll),this._resize.unobserve?.(this._scrollTarget),this._scrollTarget=void 0)}_updateScrollableState(e){const t=parseFloat(getComputedStyle(e).getPropertyValue("--safe-area-inset-bottom"))||0,{scrollHeight:a=0,clientHeight:o=0,scrollTop:i=0}=e;this._contentScrollable=a-o>i+t+this.scrollFadeSafeAreaPadding}constructor(...e){super(...e),this._contentScrolled=!1,this._contentScrollable=!1,this._onScroll=e=>{const t=e.currentTarget;this._contentScrolled=(t.scrollTop??0)>this.scrollFadeThreshold,this._updateScrollableState(t)},this._resize=new i.P(this,{target:null,callback:e=>{const t=e[0]?.target;t&&this._updateScrollableState(t)}}),this.scrollFadeSafeAreaPadding=4,this.scrollFadeThreshold=4}}return t.DEFAULT_SCROLLABLE_ELEMENT=null,(0,o.Cg)([(0,l.wk)()],t.prototype,"_contentScrolled",void 0),(0,o.Cg)([(0,l.wk)()],t.prototype,"_contentScrollable",void 0),t}}};
//# sourceMappingURL=7673.d38b1576f4579409.js.map