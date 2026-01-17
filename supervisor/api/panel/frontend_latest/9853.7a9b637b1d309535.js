export const __rspack_esm_id="9853";export const __rspack_esm_ids=["9853"];export const __webpack_modules__={93905(e,t,i){i.d(t,{I:()=>o});i(44114),i(18111),i(7588),i(33110),i(58335);class s{addFromStorage(e){if(!this._storage[e]){const t=this.storage.getItem(e);t&&(this._storage[e]=JSON.parse(t))}}subscribeChanges(e,t){return this._listeners[e]?this._listeners[e].push(t):this._listeners[e]=[t],()=>{this.unsubscribeChanges(e,t)}}unsubscribeChanges(e,t){if(!(e in this._listeners))return;const i=this._listeners[e].indexOf(t);-1!==i&&this._listeners[e].splice(i,1)}hasKey(e){return e in this._storage}getValue(e){return this._storage[e]}setValue(e,t){const i=this._storage[e];this._storage[e]=t;try{void 0===t?this.storage.removeItem(e):this.storage.setItem(e,JSON.stringify(t))}catch(e){}finally{this._listeners[e]&&this._listeners[e].forEach(e=>e(i,t))}}constructor(e=window.localStorage){this._storage={},this._listeners={},this.storage=e,this.storage===window.localStorage&&window.addEventListener("storage",e=>{e.key&&this.hasKey(e.key)&&(this._storage[e.key]=e.newValue?JSON.parse(e.newValue):e.newValue,this._listeners[e.key]&&this._listeners[e.key].forEach(t=>t(e.oldValue?JSON.parse(e.oldValue):e.oldValue,this._storage[e.key])))})}}const a={};function o(e){return(t,i)=>{if("object"==typeof i)throw new Error("This decorator does not support this compilation type.");const o=e.storage||"localStorage";let n;o&&o in a?n=a[o]:(n=new s(window[o]),a[o]=n);const r=e.key||String(i);n.addFromStorage(r);const l=!1!==e.subscribe?e=>n.subscribeChanges(r,(t,s)=>{e.requestUpdate(i,t)}):void 0,d=()=>n.hasKey(r)?e.deserializer?e.deserializer(n.getValue(r)):n.getValue(r):void 0,h=(t,s)=>{let a;e.state&&(a=d()),n.setValue(r,e.serializer?e.serializer(s):s),e.state&&t.requestUpdate(i,a)},c=t.performUpdate;if(t.performUpdate=function(){this.__initialized=!0,c.call(this)},e.subscribe){const e=t.connectedCallback,i=t.disconnectedCallback;t.connectedCallback=function(){e.call(this);const t=this;t.__unbsubLocalStorage||(t.__unbsubLocalStorage=l?.(this))},t.disconnectedCallback=function(){i.call(this);this.__unbsubLocalStorage?.(),this.__unbsubLocalStorage=void 0}}const p=Object.getOwnPropertyDescriptor(t,i);let _;if(void 0===p)_={get:()=>d(),set(e){(this.__initialized||void 0===d())&&h(this,e)},configurable:!0,enumerable:!0};else{const e=p.set;_={...p,get:()=>d(),set(t){(this.__initialized||void 0===d())&&h(this,t),e?.call(this,t)}}}Object.defineProperty(t,i,_)}}},99727(e,t,i){i(44114),i(16573),i(78100),i(77936),i(18111),i(61701),i(37467),i(44732),i(79577),i(41549),i(49797),i(49631),i(35623);var s=i(62826),a=i(96196),o=i(77845),n=i(94333),r=i(82286),l=i(69150),d=i(88433),h=i(65063);i(14603),i(47566),i(98721);class c{get active(){return this._active}get sampleRate(){return this._context?.sampleRate}static get isSupported(){return window.isSecureContext&&(window.AudioContext||window.webkitAudioContext)}async start(){if(this._context&&this._stream&&this._source&&this._recorder)this._stream.getTracks()[0].enabled=!0,await this._context.resume(),this._active=!0;else try{await this._createContext()}catch(e){console.error(e),this._active=!1}}async stop(){this._active=!1,this._stream&&(this._stream.getTracks()[0].enabled=!1),await(this._context?.suspend())}close(){this._active=!1,this._stream?.getTracks()[0].stop(),this._recorder&&(this._recorder.port.onmessage=null),this._source?.disconnect(),this._context?.close(),this._stream=void 0,this._source=void 0,this._recorder=void 0,this._context=void 0}async _createContext(){const e=new(AudioContext||webkitAudioContext);this._stream=await navigator.mediaDevices.getUserMedia({audio:!0}),await e.audioWorklet.addModule(new URL(i.p+i.u("3921"),i.b)),this._context=e,this._source=this._context.createMediaStreamSource(this._stream),this._recorder=new AudioWorkletNode(this._context,"recorder-worklet"),this._recorder.port.onmessage=e=>{this._active&&this._callback(e.data)},this._active=!0,this._source.connect(this._recorder)}constructor(e){this._active=!1,this._callback=e}}var p=i(36918);i(38962),i(60545),i(75709);class _ extends a.WF{willUpdate(e){this.hasUpdated&&!e.has("pipeline")||(this._conversation=[{who:"hass",text:this.hass.localize("ui.dialogs.voice_command.how_can_i_help")}])}firstUpdated(e){super.firstUpdated(e),this.startListening&&this.pipeline&&this.pipeline.stt_engine&&c.isSupported&&this._toggleListening(),setTimeout(()=>this._messageInput.focus(),0)}updated(e){super.updated(e),e.has("_conversation")&&this._scrollMessagesBottom()}disconnectedCallback(){super.disconnectedCallback(),this._audioRecorder?.close(),this._unloadAudio()}render(){const e=!!this.pipeline&&(this.pipeline.prefer_local_intents||!this.hass.states[this.pipeline.conversation_engine]||(0,r.$)(this.hass.states[this.pipeline.conversation_engine],d.ZE.CONTROL)),t=c.isSupported,i=this.pipeline?.stt_engine&&!this.disableSpeech;return a.qy` <div class="messages"> ${e?a.s6:a.qy` <ha-alert> ${this.hass.localize("ui.dialogs.voice_command.conversation_no_control")} </ha-alert> `} <div class="spacer"></div> ${this._conversation.map(e=>a.qy` <ha-markdown class="message ${(0,n.H)({error:!!e.error,[e.who]:!0})}" breaks cache .content="${e.text}"> </ha-markdown> `)} </div> <div class="input" slot="primaryAction"> <ha-textfield id="message-input" @keyup="${this._handleKeyUp}" @input="${this._handleInput}" .label="${this.hass.localize("ui.dialogs.voice_command.input_label")}" .iconTrailing="${!0}"> <div slot="trailingIcon"> ${this._showSendButton||!i?a.qy` <ha-icon-button class="listening-icon" .path="${"M2,21L23,12L2,3V10L17,12L2,14V21Z"}" @click="${this._handleSendMessage}" .disabled="${this._processing}" .label="${this.hass.localize("ui.dialogs.voice_command.send_text")}"> </ha-icon-button> `:a.qy` ${this._audioRecorder?.active?a.qy` <div class="bouncer"> <div class="double-bounce1"></div> <div class="double-bounce2"></div> </div> `:a.s6} <div class="listening-icon"> <ha-icon-button .path="${"M12,2A3,3 0 0,1 15,5V11A3,3 0 0,1 12,14A3,3 0 0,1 9,11V5A3,3 0 0,1 12,2M19,11C19,14.53 16.39,17.44 13,17.93V21H11V17.93C7.61,17.44 5,14.53 5,11H7A5,5 0 0,0 12,16A5,5 0 0,0 17,11H19Z"}" @click="${this._handleListeningButton}" .disabled="${this._processing}" .label="${this.hass.localize("ui.dialogs.voice_command.start_listening")}"> </ha-icon-button> ${t?null:a.qy` <ha-svg-icon .path="${"M13,13H11V7H13M13,17H11V15H13M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2Z"}" class="unsupported"></ha-svg-icon> `} </div> `} </div> </ha-textfield> </div> `}async _scrollMessagesBottom(){const e=this._lastChatMessage;if(e.hasUpdated||await e.updateComplete,this._lastChatMessageImage&&!this._lastChatMessageImage.naturalHeight)try{await this._lastChatMessageImage.decode()}catch(e){console.warn("Failed to decode image:",e)}e.getBoundingClientRect().y<this.getBoundingClientRect().top+24||e.scrollIntoView({behavior:"smooth",block:"start"})}_handleKeyUp(e){const t=e.target;!this._processing&&"Enter"===e.key&&t.value&&(this._processText(t.value),t.value="",this._showSendButton=!1)}_handleInput(e){const t=e.target.value;t&&!this._showSendButton?this._showSendButton=!0:!t&&this._showSendButton&&(this._showSendButton=!1)}_handleSendMessage(){this._messageInput.value&&(this._processText(this._messageInput.value.trim()),this._messageInput.value="",this._showSendButton=!1)}_handleListeningButton(e){e.stopPropagation(),e.preventDefault(),this._toggleListening()}async _toggleListening(){c.isSupported?this._audioRecorder?.active?this._stopListening():this._startListening():this._showNotSupportedMessage()}_addMessage(e){this._conversation=[...this._conversation,e]}async _showNotSupportedMessage(){this._addMessage({who:"hass",text:a.qy`${this.hass.localize("ui.dialogs.voice_command.not_supported_microphone_browser")} ${this.hass.localize("ui.dialogs.voice_command.not_supported_microphone_documentation",{documentation_link:a.qy`<a target="_blank" rel="noopener noreferrer" href="${(0,p.o)(this.hass,"/docs/configuration/securing/#remote-access")}">${this.hass.localize("ui.dialogs.voice_command.not_supported_microphone_documentation_link")}</a>`})}`})}async _startListening(){this._unloadAudio(),this._processing=!0,this._audioRecorder||(this._audioRecorder=new c(e=>{this._audioBuffer?this._audioBuffer.push(e):this._sendAudioChunk(e)})),this._stt_binary_handler_id=void 0,this._audioBuffer=[];const e={who:"user",text:"…"};await this._audioRecorder.start(),this._addMessage(e);const t=this._createAddHassMessageProcessor();try{const i=await(0,l.vU)(this.hass,s=>{if("run-start"===s.type)this._stt_binary_handler_id=s.data.runner_data.stt_binary_handler_id,this._audio=new Audio(s.data.tts_output.url),this._audio.play(),this._audio.addEventListener("ended",()=>{this._unloadAudio(),t.continueConversation&&this._startListening()}),this._audio.addEventListener("pause",this._unloadAudio),this._audio.addEventListener("canplaythrough",()=>this._audio?.play()),this._audio.addEventListener("error",()=>{this._unloadAudio(),(0,h.K$)(this,{title:"Error playing audio."})});else if("stt-start"===s.type&&this._audioBuffer){for(const e of this._audioBuffer)this._sendAudioChunk(e);this._audioBuffer=void 0}else"stt-end"===s.type?(this._stt_binary_handler_id=void 0,this._stopListening(),e.text=s.data.stt_output.text,this.requestUpdate("_conversation"),t.addMessage()):s.type.startsWith("intent-")?t.processEvent(s):"run-end"===s.type?(this._stt_binary_handler_id=void 0,i()):"error"===s.type&&(this._unloadAudio(),this._stt_binary_handler_id=void 0,"…"===e.text?(e.text=s.data.message,e.error=!0):t.setError(s.data.message),this._stopListening(),this.requestUpdate("_conversation"),i())},{start_stage:"stt",end_stage:this.pipeline?.tts_engine?"tts":"intent",input:{sample_rate:this._audioRecorder.sampleRate},pipeline:this.pipeline?.id,conversation_id:this._conversationId})}catch(e){await(0,h.K$)(this,{title:"Error starting pipeline",text:e.message||e}),this._stopListening()}finally{this._processing=!1}}_stopListening(){if(this._audioRecorder?.stop(),this.requestUpdate("_audioRecorder"),this._stt_binary_handler_id){if(this._audioBuffer)for(const e of this._audioBuffer)this._sendAudioChunk(e);this._sendAudioChunk(new Int16Array),this._stt_binary_handler_id=void 0}this._audioBuffer=void 0}_sendAudioChunk(e){if(this.hass.connection.socket.binaryType="arraybuffer",null==this._stt_binary_handler_id)return;const t=new Uint8Array(1+2*e.length);t[0]=this._stt_binary_handler_id,t.set(new Uint8Array(e.buffer),1),this.hass.connection.socket.send(t)}async _processText(e){this._unloadAudio(),this._processing=!0,this._addMessage({who:"user",text:e});const t=this._createAddHassMessageProcessor();t.addMessage();try{const i=await(0,l.vU)(this.hass,e=>{e.type.startsWith("intent-")&&t.processEvent(e),"intent-end"===e.type&&i(),"error"===e.type&&(t.setError(e.data.message),i())},{start_stage:"intent",input:{text:e},end_stage:"intent",pipeline:this.pipeline?.id,conversation_id:this._conversationId})}catch{t.setError(this.hass.localize("ui.dialogs.voice_command.error"))}finally{this._processing=!1}}_createAddHassMessageProcessor(){let e="";const t=()=>{"…"!==s.hassMessage.text&&(s.hassMessage.text=s.hassMessage.text.substring(0,s.hassMessage.text.length-1),s.hassMessage={who:"hass",text:"…",error:!1},this._addMessage(s.hassMessage))},i={},s={continueConversation:!1,hassMessage:{who:"hass",text:"…",error:!1},addMessage:()=>{this._addMessage(s.hassMessage)},setError:e=>{t(),s.hassMessage.text=e,s.hassMessage.error=!0,this.requestUpdate("_conversation")},processEvent:a=>{if("intent-progress"===a.type&&a.data.chat_log_delta){const o=a.data.chat_log_delta;if(o.role&&(t(),e=o.role),"assistant"===e){if(o.content&&(s.hassMessage.text=s.hassMessage.text.substring(0,s.hassMessage.text.length-1)+o.content+"…",this.requestUpdate("_conversation")),o.tool_calls)for(const e of o.tool_calls)i[e.id]=e}else"tool_result"===e&&i[o.tool_call_id]&&delete i[o.tool_call_id]}else if("intent-end"===a.type){this._conversationId=a.data.intent_output.conversation_id,s.continueConversation=a.data.intent_output.continue_conversation;const e=a.data.intent_output.response.speech?.plain.speech;if(!e)return;"error"===a.data.intent_output.response.response_type?s.setError(e):(s.hassMessage.text=e,this.requestUpdate("_conversation"))}}};return s}constructor(...e){super(...e),this.disableSpeech=!1,this._conversation=[],this._showSendButton=!1,this._processing=!1,this._conversationId=null,this._unloadAudio=()=>{this._audio&&(this._audio.pause(),this._audio.removeAttribute("src"),this._audio=void 0)}}}_.styles=a.AH`
    :host {
      flex: 1;
      display: flex;
      flex-direction: column;
    }
    ha-alert {
      margin-bottom: 8px;
    }
    ha-textfield {
      display: block;
    }
    .messages {
      flex: 1;
      display: block;
      box-sizing: border-box;
      overflow-y: auto;
      max-height: 100%;
      display: flex;
      flex-direction: column;
      padding: 0 12px 16px;
    }
    .spacer {
      flex: 1;
    }
    .message {
      font-size: var(--ha-font-size-l);
      clear: both;
      max-width: -webkit-fill-available;
      overflow-wrap: break-word;
      scroll-margin-top: 24px;
      margin: 8px 0;
      padding: 8px;
      border-radius: var(--ha-border-radius-xl);
    }
    @media all and (max-width: 450px), all and (max-height: 500px) {
      .message {
        font-size: var(--ha-font-size-l);
      }
    }
    .message.user {
      margin-left: 24px;
      margin-inline-start: 24px;
      margin-inline-end: initial;
      align-self: flex-end;
      border-bottom-right-radius: 0px;
      --markdown-link-color: var(--text-primary-color);
      background-color: var(--chat-background-color-user, var(--primary-color));
      color: var(--text-primary-color);
      direction: var(--direction);
    }
    .message.hass {
      margin-right: 24px;
      margin-inline-end: 24px;
      margin-inline-start: initial;
      align-self: flex-start;
      border-bottom-left-radius: 0px;
      background-color: var(
        --chat-background-color-hass,
        var(--secondary-background-color)
      );

      color: var(--primary-text-color);
      direction: var(--direction);
    }
    .message.error {
      background-color: var(--error-color);
      color: var(--text-primary-color);
    }
    ha-markdown {
      --markdown-image-border-radius: calc(var(--ha-border-radius-xl) / 2);
      --markdown-table-border-color: var(--divider-color);
      --markdown-code-background-color: var(--primary-background-color);
      --markdown-code-text-color: var(--primary-text-color);
      --markdown-list-indent: 1.15em;
      &:not(:has(ha-markdown-element)) {
        min-height: 1lh;
        min-width: 1lh;
        flex-shrink: 0;
      }
    }
    .bouncer {
      width: 48px;
      height: 48px;
      position: absolute;
    }
    .double-bounce1,
    .double-bounce2 {
      width: 48px;
      height: 48px;
      border-radius: var(--ha-border-radius-circle);
      background-color: var(--primary-color);
      opacity: 0.2;
      position: absolute;
      top: 0;
      left: 0;
      -webkit-animation: sk-bounce 2s infinite ease-in-out;
      animation: sk-bounce 2s infinite ease-in-out;
    }
    .double-bounce2 {
      -webkit-animation-delay: -1s;
      animation-delay: -1s;
    }
    @-webkit-keyframes sk-bounce {
      0%,
      100% {
        -webkit-transform: scale(0);
      }
      50% {
        -webkit-transform: scale(1);
      }
    }
    @keyframes sk-bounce {
      0%,
      100% {
        transform: scale(0);
        -webkit-transform: scale(0);
      }
      50% {
        transform: scale(1);
        -webkit-transform: scale(1);
      }
    }

    .listening-icon {
      position: relative;
      color: var(--secondary-text-color);
      margin-right: -24px;
      margin-inline-end: -24px;
      margin-inline-start: initial;
      direction: var(--direction);
      transform: scaleX(var(--scale-direction));
    }

    .listening-icon[active] {
      color: var(--primary-color);
    }

    .unsupported {
      color: var(--error-color);
      position: absolute;
      --mdc-icon-size: 16px;
      right: 5px;
      inset-inline-end: 5px;
      inset-inline-start: initial;
      top: 0px;
    }
  `,(0,s.Cg)([(0,o.MZ)({attribute:!1})],_.prototype,"hass",void 0),(0,s.Cg)([(0,o.MZ)({attribute:!1})],_.prototype,"pipeline",void 0),(0,s.Cg)([(0,o.MZ)({type:Boolean,attribute:"disable-speech"})],_.prototype,"disableSpeech",void 0),(0,s.Cg)([(0,o.MZ)({type:Boolean,attribute:!1})],_.prototype,"startListening",void 0),(0,s.Cg)([(0,o.P)("#message-input")],_.prototype,"_messageInput",void 0),(0,s.Cg)([(0,o.P)(".message:last-child")],_.prototype,"_lastChatMessage",void 0),(0,s.Cg)([(0,o.P)(".message:last-child img:last-of-type")],_.prototype,"_lastChatMessageImage",void 0),(0,s.Cg)([(0,o.wk)()],_.prototype,"_conversation",void 0),(0,s.Cg)([(0,o.wk)()],_.prototype,"_showSendButton",void 0),(0,s.Cg)([(0,o.wk)()],_.prototype,"_processing",void 0),_=(0,s.Cg)([(0,o.EM)("ha-assist-chat")],_)},24524(e,t,i){i.a(e,async function(e,s){try{i.r(t),i.d(t,{HaVoiceCommandDialog:()=>f});i(18111),i(61701);var a=i(62826),o=i(96196),n=i(77845),r=i(93905),l=i(1087),d=i(57237),h=(i(38962),i(99727),i(18350)),c=(i(13416),i(72554),i(76538),i(50888),i(28732),i(65829)),p=i(69150),_=i(14503),u=i(36918),g=e([h,c]);[h,c]=g.then?(await g)():g;const m="M7.41,8.58L12,13.17L16.59,8.58L18,10L12,16L6,10L7.41,8.58Z",v="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z",b="M11,18H13V16H11V18M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M12,20C7.59,20 4,16.41 4,12C4,7.59 7.59,4 12,4C16.41,4 20,7.59 20,12C20,16.41 16.41,20 12,20M12,6A4,4 0 0,0 8,10H10A2,2 0 0,1 12,8A2,2 0 0,1 14,10C14,12 11,11.75 11,15H13C13,12.75 16,12.5 16,10A4,4 0 0,0 12,6Z",y="M12,17.27L18.18,21L16.54,13.97L22,9.24L14.81,8.62L12,2L9.19,8.62L2,9.24L7.45,13.97L5.82,21L12,17.27Z";class f extends o.WF{async showDialog(e){await this._loadPipelines();const t=this._pipelines?.map(e=>e.id)||[];"preferred"===e.pipeline_id||"last_used"===e.pipeline_id&&!this._pipelineId?this._pipelineId=this._preferredPipeline:["last_used","preferred"].includes(e.pipeline_id)||(this._pipelineId=e.pipeline_id),this._pipelineId&&!t.includes(this._pipelineId)&&(this._pipelineId=this._preferredPipeline),this._startListening=e.start_listening,this._opened=!0}async closeDialog(){this._opened=!1,this._pipelines=void 0,(0,l.r)(this,"dialog-closed",{dialog:this.localName})}render(){return this._opened?o.qy` <ha-dialog open @closed="${this.closeDialog}" .heading="${this.hass.localize("ui.dialogs.voice_command.title")}" flexContent hideactions> <ha-dialog-header slot="heading"> <ha-icon-button slot="navigationIcon" dialogAction="cancel" .label="${this.hass.localize("ui.common.close")}" .path="${v}"></ha-icon-button> <div slot="title"> ${this.hass.localize("ui.dialogs.voice_command.title")} <ha-button-menu @opened="${this._loadPipelines}" @closed="${d.d}" activatable fixed> <ha-button slot="trigger" appearance="plain" variant="neutral" size="small"> ${this._pipeline?.name} <ha-svg-icon slot="end" .path="${m}"></ha-svg-icon> </ha-button> ${this._pipelines?this._pipelines?.map(e=>o.qy`<ha-list-item ?selected="${e.id===this._pipelineId||!this._pipelineId&&e.id===this._preferredPipeline}" .pipeline="${e.id}" @click="${this._selectPipeline}" .hasMeta="${e.id===this._preferredPipeline}"> ${e.name}${e.id===this._preferredPipeline?o.qy` <ha-svg-icon slot="meta" .path="${y}"></ha-svg-icon> `:o.s6} </ha-list-item>`):o.qy`<div class="pipelines-loading"> <ha-spinner size="small"></ha-spinner> </div>`} ${this.hass.user?.is_admin?o.qy`<li divider role="separator"></li> <a href="/config/voice-assistants/assistants"><ha-list-item>${this.hass.localize("ui.dialogs.voice_command.manage_assistants")}</ha-list-item></a>`:o.s6} </ha-button-menu> </div> <a href="${(0,u.o)(this.hass,"/docs/assist/")}" slot="actionItems" target="_blank" rel="noopener noreferer"> <ha-icon-button .label="${this.hass.localize("ui.common.help")}" .path="${b}"></ha-icon-button> </a> </ha-dialog-header> ${this._errorLoadAssist?o.qy`<ha-alert alert-type="error"> ${this.hass.localize(`ui.dialogs.voice_command.${this._errorLoadAssist}_error_load_assist`)} </ha-alert>`:this._pipeline?o.qy` <ha-assist-chat .hass="${this.hass}" .pipeline="${this._pipeline}" .startListening="${this._startListening}"> </ha-assist-chat> `:o.qy`<div class="pipelines-loading"> <ha-spinner size="large"></ha-spinner> </div>`} </ha-dialog> `:o.s6}willUpdate(e){(e.has("_pipelineId")||e.has("_opened")&&!0===this._opened&&this._pipelineId)&&this._getPipeline()}async _loadPipelines(){if(this._pipelines)return;const{pipelines:e,preferred_pipeline:t}=await(0,p.nx)(this.hass);this._pipelines=e,this._preferredPipeline=t||void 0}async _selectPipeline(e){this._pipelineId=e.currentTarget.pipeline,await this.updateComplete}async _getPipeline(){this._pipeline=void 0,this._errorLoadAssist=void 0;const e=this._pipelineId;try{const t=await(0,p.mp)(this.hass,e);e===this._pipelineId&&(this._pipeline=t)}catch(t){if(e!==this._pipelineId)return;"not_found"===t.code?this._errorLoadAssist="not_found":(this._errorLoadAssist="unknown",console.error(t))}}static get styles(){return[_.nA,o.AH`ha-dialog{--mdc-dialog-max-width:500px;--mdc-dialog-max-height:500px;--dialog-content-padding:0}ha-dialog-header a{color:var(--primary-text-color)}div[slot=title]{display:flex;flex-direction:column;margin:-4px 0}ha-button-menu{--mdc-theme-on-primary:var(--text-primary-color);--mdc-theme-primary:var(--primary-color);margin-top:-8px;margin-bottom:0;margin-right:0;margin-inline-end:0;margin-left:-8px;margin-inline-start:-8px}ha-button-menu ha-button{--ha-button-height:20px}ha-button-menu ha-button::part(base){margin-left:5px;padding:0}@media (prefers-color-scheme:dark){ha-button-menu ha-button{--ha-button-theme-lighter-color:rgba(255, 255, 255, 0.1)}}ha-button-menu ha-button ha-svg-icon{height:28px;margin-left:4px;margin-inline-start:4px;margin-inline-end:initial;direction:var(--direction)}ha-list-item{--mdc-list-item-meta-size:16px}ha-list-item ha-svg-icon{margin-left:4px;margin-inline-start:4px;margin-inline-end:initial;direction:var(--direction);display:block}ha-button-menu a{text-decoration:none}.pipelines-loading{display:flex;justify-content:center}ha-assist-chat{margin:0 24px 16px;min-height:399px}`]}constructor(...e){super(...e),this._opened=!1,this._startListening=!1}}(0,a.Cg)([(0,n.MZ)({attribute:!1})],f.prototype,"hass",void 0),(0,a.Cg)([(0,n.wk)()],f.prototype,"_opened",void 0),(0,a.Cg)([(0,n.wk)(),(0,r.I)({key:"AssistPipelineId",state:!0,subscribe:!1})],f.prototype,"_pipelineId",void 0),(0,a.Cg)([(0,n.wk)()],f.prototype,"_pipeline",void 0),(0,a.Cg)([(0,n.wk)()],f.prototype,"_pipelines",void 0),(0,a.Cg)([(0,n.wk)()],f.prototype,"_preferredPipeline",void 0),(0,a.Cg)([(0,n.wk)()],f.prototype,"_errorLoadAssist",void 0),f=(0,a.Cg)([(0,n.EM)("ha-voice-command-dialog")],f),s()}catch(e){s(e)}})}};
//# sourceMappingURL=9853.7a9b637b1d309535.js.map