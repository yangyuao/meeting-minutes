<template>
    <div class="recording-panel">
        <!-- 背景装饰元素 -->
        <div class="background-decorations">
            <div class="retro-aura" v-if="themeMode === 'retro'"></div>
            <div class="decoration-circle circle-1"></div>
            <div class="decoration-circle circle-2"></div>
            <div class="decoration-circle circle-3"></div>
            <div class="decoration-wave wave-1"></div>
            <div class="decoration-wave wave-2"></div>
        </div>

        <!-- 左上角：环境监测 (装饰性) -->
        <transition name="fade">
            <div v-if="!isIdle" class="env-monitor">
                <div class="monitor-item">
                    <span class="label">NOISE</span>
                    <div class="bar-group">
                        <div class="bar" v-for="n in 5" :key="n" :style="{ height: Math.random() * 100 + '%' }"></div>
                    </div>
                </div>
                <div class="monitor-item">
                    <span class="label">FREQ</span>
                    <span class="value">16kHz</span>
                </div>
            </div>
        </transition>

        <div class="panel-content">
            <!-- 风格切换开关 -->
            <div class="style-switcher">
                <div class="switch-item" :class="{ active: themeMode === 'modern' }" @click="themeMode = 'modern'">
                    <i class="el-icon-s-data"></i> 现代律动
                </div>
                <div class="switch-item" :class="{ active: themeMode === 'retro' }" @click="themeMode = 'retro'">
                    <i class="el-icon-video-camera-solid"></i> 复古磁带
                </div>
            </div>

            <!-- 使用 transition 组件实现平滑切换 -->
            <transition name="panel-switch" mode="out-in">
                <!-- 空闲态：标题 + 提示 + 操作区 -->
                <div v-if="isIdle" key="idle" class="idle-shell">
                    <!-- 标题区域 - 居中 -->
                    <div class="title-section">
                        <div class="title-icon-wrapper">
                            <div class="title-icon-glow"></div>
                            <div class="title-icon">🎙️</div>
                        </div>
                        <div class="title-text">
                            <h1>智能会议纪要</h1>
                            <p>AI 驱动的会议记录与智能分析</p>
                        </div>
                        <!-- 功能提示 -->
                        <div class="feature-hints">
                            <div class="hint-item">
                                <i class="el-icon-upload2"></i>
                                <span>支持多种音频格式</span>
                            </div>
                            <div class="hint-item">
                                <i class="el-icon-microphone"></i>
                                <span>实时录音转文字</span>
                            </div>
                            <div class="hint-item">
                                <i class="el-icon-magic-stick"></i>
                                <span>AI 智能生成纪要</span>
                            </div>
                        </div>
                    </div>

                    <!-- 操作区域：左侧拖拽上传 + 右侧按钮 -->
                    <div class="action-area">
                        <!-- 左侧：拖拽上传区域 -->
                        <div class="upload-dropzone">
                            <el-upload class="upload-dragger" :action="uploadAction" :before-upload="beforeUpload"
                                :on-success="handleUploadSuccess" :on-error="handleUploadError" :show-file-list="false"
                                :drag="true" accept="audio/*">
                                <div class="dropzone-content" :class="{ 'has-file': uploadedFile }">
                                    <!-- 未上传文件时显示上传提示 -->
                                    <template v-if="!uploadedFile">
                                        <div class="dropzone-icon">
                                            <i class="el-icon-upload"></i>
                                        </div>
                                        <div class="dropzone-text">
                                            <p class="main-text">拖拽音频文件到此处</p>
                                            <p class="sub-text">或点击选择文件</p>
                                            <p class="hint-text">支持 MP3、WAV、M4A 等格式</p>
                                        </div>
                                    </template>
                                    <!-- 已上传文件时显示文件信息 -->
                                    <template v-else>
                                        <div class="dropzone-icon file-icon">
                                            <i class="el-icon-document"></i>
                                        </div>
                                        <div class="dropzone-text file-info">
                                            <p class="main-text">{{ uploadedFile.name }}</p>
                                            <p class="sub-text">{{ formatFileSize(uploadedFile.size) }}</p>
                                            <p class="hint-text">{{ uploadedFile.type || '音频文件' }}</p>
                                        </div>
                                        <div class="file-actions">
                                            <el-button size="small" type="text" @click.stop="clearUploadedFile">
                                                <i class="el-icon-close"></i> 清除
                                            </el-button>
                                        </div>
                                    </template>
                                </div>
                            </el-upload>
                        </div>

                        <!-- 右侧：操作按钮 -->
                        <div class="action-buttons">
                            <el-upload class="action-button-wrapper" :action="uploadAction"
                                :before-upload="beforeUpload" :on-success="handleUploadSuccess"
                                :on-error="handleUploadError" :show-file-list="false" accept="audio/*">
                                <button class="action-btn">
                                    <i class="el-icon-upload2"></i>
                                    <span>上传音频</span>
                                </button>
                            </el-upload>

                            <button class="action-btn" @click="startRecording" :disabled="recordingLoading">
                                <i class="el-icon-loading" v-if="recordingLoading"></i>
                                <i class="el-icon-microphone" v-else></i>
                                <span>开始录音</span>
                            </button>
                        </div>
                    </div>
                </div>

                <!-- 录音状态展示 - 居中 -->
                <div v-else key="recording" class="recording-display">
                    
                    <!-- 现代律动风格 -->
                    <div v-if="themeMode === 'modern'" class="mic-with-waves">
                        <!-- 左侧律动条 -->
                        <div v-if="recordingState === 'recording'" class="wave-left">
                            <div v-for="(bar, index) in leftWaveBars" :key="'left-' + index" class="wave-bar"
                                :style="{ height: bar + '%', animationDelay: index * 0.05 + 's' }"></div>
                        </div>

                        <!-- 麦克风 -->
                        <div class="mic-container">
                            <div class="mic-outer-ring"></div>
                            <div class="mic-inner-circle">
                                <i class="el-icon-microphone mic-icon"
                                   :class="{ 'recording': recordingState === 'recording', 'paused': recordingState === 'paused' }">
                                </i>
                            </div>
                        </div>

                        <!-- 右侧律动条 -->
                        <div v-if="recordingState === 'recording'" class="wave-right">
                            <div v-for="(bar, index) in rightWaveBars" :key="'right-' + index" class="wave-bar"
                                :style="{ height: bar + '%', animationDelay: index * 0.05 + 's' }"></div>
                        </div>
                    </div>

                    <!-- 复古磁带录音机风格 (包含磁带+右侧控制区) -->
                    <div v-if="themeMode === 'retro'" class="retro-container">
                        <!-- 磁带 -->
                        <div class="tape-wrapper-level">
                            <div class="cassette-tape blue-theme">
                                <div class="tape-screw topleft"></div>
                                <div class="tape-screw topright"></div>
                                <div class="tape-screw bottomleft"></div>
                                <div class="tape-screw bottomright"></div>
                                
                                <!-- 磁带贴纸区域：集成 VU 表和时间 -->
                                <div class="tape-label">
                                    <!-- 左侧 VU 表 -->
                                    <div class="integrated-vu">
                                        <div class="vu-scale"></div>
                                        <div class="vu-needle" :style="{ transform: `rotate(${vuNeedleAngle}deg)` }"></div>
                                        <span class="vu-text">L</span>
                                    </div>

                                    <!-- 中间：状态和时间显示 -->
                                    <div class="center-display">
                                        <div class="status-text-retro">
                                            <span v-if="recordingState === 'recording'">正在录音...</span>
                                            <span v-else-if="recordingState === 'paused'">录音暂停</span>
                                            <span v-else>准备就绪</span>
                                        </div>
                                        <div class="digital-clock">{{ formatTime(recordingTime) }}</div>
                                    </div>

                                    <!-- 右侧 VU 表 -->
                                    <div class="integrated-vu">
                                        <div class="vu-scale"></div>
                                        <div class="vu-needle" :style="{ transform: `rotate(${vuNeedleAngle}deg)` }"></div>
                                        <span class="vu-text">R</span>
                                    </div>
                                </div>
                                
                                <div class="tape-window">
                                    <div class="reel left">
                                        <div class="reel-spokes" :class="{ 'spinning': recordingState === 'recording' }"></div>
                                    </div>
                                    <div class="tape-link"></div>
                                    <div class="reel right">
                                        <div class="reel-spokes" :class="{ 'spinning': recordingState === 'recording' }"></div>
                                    </div>
                                </div>
                                
                                <div class="tape-bottom"></div>

                                <!-- 右侧复古机械按钮组 (仅保留凸起联动) -->
                                <div class="side-controls-wrapper">
                                    <!-- 暂停/继续 (Play/Pause) -->
                                    <div class="control-row">
                                        <div class="micro-tab play-pause" 
                                             :class="{ 'pressed': recordingState === 'recording' }">
                                        </div>
                                    </div>

                                    <!-- 完成 (Stop) -->
                                    <div class="control-row">
                                        <div class="micro-tab finish" :class="{ 'pressed': activeSideBtn === 'finish' }"></div>
                                    </div>

                                    <!-- 取消 (Eject) -->
                                    <div class="control-row">
                                        <div class="micro-tab cancel" :class="{ 'pressed': activeSideBtn === 'eject' }"></div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- 下方：实体控制面板 (Control Deck) -->
                        <div class="control-deck" v-if="recordingState !== 'reviewed'">
                            <div class="deck-surface">
                                <div class="deck-btn cancel-btn" @click="triggerDeckAction('eject')" title="取消/弹出">
                                    <div class="btn-cap">
                                        <i class="el-icon-close"></i>
                                    </div>
                                    <span class="btn-label">取消录音</span>
                                </div>
                                
                                <div class="deck-btn play-btn" 
                                     @click="triggerDeckAction('play')"
                                     :class="{ 'active': recordingState === 'recording' }">
                                    <div class="btn-cap">
                                        <i :class="recordingState === 'recording' ? 'el-icon-video-pause' : 'el-icon-video-play'"></i>
                                    </div>
                                    <span class="btn-label">{{ recordingState === 'recording' ? '暂停录音' : '开始录音' }}</span>
                                </div>

                                <div class="deck-btn finish-btn" @click="triggerDeckAction('finish')" title="完成录音">
                                    <div class="btn-cap">
                                        <i class="el-icon-check"></i>
                                    </div>
                                    <span class="btn-label">完成录音</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div v-if="themeMode === 'modern'" class="recording-status-info">
                        <div class="status-label">
                            <span v-if="recordingState === 'recording'">正在录音</span>
                            <span v-else-if="recordingState === 'paused'">已暂停</span>
                            <span v-else-if="recordingState === 'reviewed'">录音完成</span>
                        </div>
                        <div class="time-display">{{ formatTime(recordingTime) }}</div>
                    </div>

                    <!-- 控制按钮 (仅现代模式显示) -->
                    <div v-if="themeMode === 'modern' && recordingState !== 'reviewed'" class="control-buttons-group">
                        <!-- 中间：取消录制按钮 -->
                        <el-button type="info" icon="el-icon-close" @click="cancelRecording" size="large"
                            class="control-btn cancel-btn">
                            <span>取消录制</span>
                        </el-button>
                        <!-- 左侧：暂停/继续按钮 -->
                        <el-button :type="recordingState === 'recording' ? 'warning' : 'success'"
                            :icon="recordingState === 'recording' ? 'el-icon-video-pause' : 'el-icon-video-play'"
                            @click="recordingState === 'recording' ? pauseRecording() : resumeRecording()"
                            size="large" class="control-btn pause-resume-btn">
                            <span>{{ recordingState === 'recording' ? '暂停录音' : '继续录音' }}</span>
                        </el-button>

                        <!-- 右侧：完成录制按钮 -->
                        <el-button type="primary" icon="el-icon-check" @click="confirmStopRecording" size="large"
                            class="control-btn finish-btn">
                            <span>完成录制</span>
                        </el-button>
                    </div>

                    <!-- 现代模式：结果展示卡片 -->
                    <div v-if="themeMode === 'modern' && recordingState === 'reviewed'" class="result-card-modern">
                        <div class="player-row">
                            <div class="play-btn" @click="togglePlay">
                                <i :class="isPlaying ? 'el-icon-video-pause' : 'el-icon-video-play'"></i>
                            </div>
                            <div class="progress-bar">
                                <el-slider v-model="playProgress" :show-tooltip="false" @change="onSliderChange" input-size="small"></el-slider>
                                <div class="time-hint">
                                    <span>{{ formatTime(currentTime) }}</span>
                                    <span>{{ formatTime(audioDuration || recordingTime) }}</span>
                                </div>
                            </div>
                        </div>
                        <div class="action-row">
                            <div class="action-item secondary" @click="backToHome">
                                <i class="el-icon-refresh-left" ></i>
                                <span>返回首页</span>
                            </div>
                            <div class="action-item primary" @click="downloadRecordedAudio">
                                <i class="el-icon-download"></i>
                                <span>下载录音</span>
                            </div>
                            <div class="action-item primary" :class="{ disabled: translatingRecordedAudio }" @click="transcribeRecordedAudio">
                                <i class="el-icon-edit-outline"></i>
                                <span>{{ translatingRecordedAudio ? '转译中...' : '转译' }}</span>
                            </div>
                        </div>
                    </div>

                    <!-- 复古模式：结果展示卡片 -->
                    <div v-if="themeMode === 'retro' && recordingState === 'reviewed'" class="result-card-retro">
                        <div class="paper-tape">
                            <div class="perforation"></div>
                            <div class="note-content">
                                <div class="retro-player">
                                    <div class="retro-play-btn" @click="togglePlay" :class="{ playing: isPlaying }">
                                        <i :class="isPlaying ? 'el-icon-video-pause' : 'el-icon-video-play'"></i>
                                    </div>
                                    <div class="retro-info-col">
                                        <div class="retro-progress" ref="retroProgressBar" @mousedown="startRetroDrag">
                                            <div class="progress-fill" :style="{ width: playProgress + '%' }"></div>
                                        </div>
                                        <div class="retro-time-text">
                                            {{ formatTime(currentTime) }} / {{ formatTime(audioDuration || recordingTime) }}
                                        </div>
                                    </div>
                                </div>
                                <div class="retro-actions">
                                    <button class="retro-btn" @click="backToHome">重新录制</button>
                                    <button class="retro-btn primary" @click="downloadRecordedAudio">保存录音</button>
                                    <button class="retro-btn primary" :class="{ loading: translatingRecordedAudio }" @click="transcribeRecordedAudio">
                                        {{ translatingRecordedAudio ? '转译中...' : '转译' }}
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- 隐形音频播放器 -->
                    <audio 
                        ref="audioPlayer" 
                        :src="downloadAudioUrl" 
                        @timeupdate="onTimeUpdate" 
                        @ended="onAudioEnded"
                        @loadedmetadata="onAudioLoaded"
                        style="display: none;">
                    </audio>
                </div>
            </transition>
        </div>
    </div>
</template>

<script>
import { MessageBox } from 'element-ui'
import { API_UPLOAD_AUDIO, API_UPLOAD, API_GET_TRANSCRIPT, getWebSocketUrl } from '@/utils/env'

export default {
    name: 'RecordingPanel',
    props: {
        uploadAction: {
            type: String,
            default: API_UPLOAD_AUDIO
        },
        // 是否启用实时识别（WebSocket）
        enableRealtimeTranscription: {
            type: Boolean,
            default: true
        }
    },
    data() {
        return {
            // 录音相关
            mediaRecorder: null,
            audioStream: null,
            audioContext: null,
            analyser: null,
            recordingState: 'idle', // idle, recording, paused, reviewed
            recordingTime: 0,
            recordingTimer: null,
            recordingLoading: false,
            audioChunks: [],

            // 播放器相关
            isPlaying: false,
            playProgress: 0, // 0-100
            audioDuration: 0,
            currentTime: 0,

            // 主题模式：'retro' | 'modern'
            themeMode: 'retro',

            // 现代模式波形数据
            leftWaveBars: Array(15).fill(20),
            rightWaveBars: Array(15).fill(20),
            waveformAnimation: null,

            // 复古 VU 表指针角度 (-45deg 到 45deg)
            vuNeedleAngle: -45,

            // 上传的文件信息
            uploadedFile: null,

            // WebSocket 实时识别相关（迁移自 old App.vue）
            wsconnecter: null,
            rec: null, // Recorder 实例
            sampleBuf: null, // Int16Array
            rec_text: '', // 实时识别文本
            offline_text: '', // 离线识别文本
            isRec: false, // 是否正在识别
            sendBuf: null,

            // 侧边按钮联动状态
            activeSideBtn: '',
            
            // 复古进度条拖拽状态
            isDraggingRetro: false,

            // 最近一次录音的下载链接
            // 这里先放一个示例音频地址，方便在无法真实录音时预览界面效果
            downloadAudioUrl: '',
            recentRecordingBlob: null,
            translatingRecordedAudio: false
        }
    },
    computed: {
        isIdle() {
            return this.recordingState === 'idle'
        }
    },
    mounted() {
        // 初始化 WebSocket 实时识别相关对象（迁移自 old App.vue）
        if (this.enableRealtimeTranscription && window.WebSocketConnectMethod && window.Recorder) {
            this.initWebSocketRecorder()
        }
    },
    beforeDestroy() {
        this.cleanup()
        // 清理 WebSocket 连接
        if (this.wsconnecter) {
            try {
                this.wsconnecter.wsStop()
            } catch (e) {
                console.error('关闭 WebSocket 失败:', e)
            }
        }
    },
    methods: {
        // 初始化 WebSocket 录音器（迁移自 old App.vue）
        initWebSocketRecorder() {
            if (!window.WebSocketConnectMethod || !window.Recorder) {
                console.warn('WebSocket 或 Recorder 未加载，实时识别功能不可用')
                return
            }

            const WEBSOCKET_BASE_URL = getWebSocketUrl()
            
            // 创建 WebSocket 连接器（迁移自 old App.vue）
            this.wsconnecter = new window.WebSocketConnectMethod({
                msgHandle: this.getJsonMessage.bind(this),
                stateHandle: this.getConnState.bind(this),
                wsUrl: WEBSOCKET_BASE_URL
            })

            // 创建 Recorder 实例（迁移自 old App.vue）
            this.rec = window.Recorder({
                type: 'pcm',
                bitRate: 16,
                sampleRate: 16000,
                onProcess: this.recProcess.bind(this)
            })

            this.sampleBuf = new Int16Array()
            this.rec_text = ''
            this.offline_text = ''
            this.isRec = false
        },

        // WebSocket 消息处理（迁移自 old App.vue 的 getJsonMessage）
        getJsonMessage(jsonMsg) {
            try {
                const data = JSON.parse(jsonMsg.data)
                const rectxt = '' + (data.text || '')
                const asrmodel = data.mode
                const timestamp = data.timestamp

                if (asrmodel === '2pass-offline') {
                    // 离线模式，带时间戳
                    this.offline_text += this.handleWithTimestamp(rectxt, timestamp)
                    this.rec_text = this.offline_text
                } else {
                    // 在线模式，直接追加
                    this.rec_text += rectxt
                }

                // 实时更新转写文本到父组件
                this.$emit('realtime-transcription', this.rec_text)
            } catch (error) {
                console.error('解析 WebSocket 消息失败:', error)
            }
        },

        // 处理时间戳（迁移自 old App.vue 的 handleWithTimestamp）
        handleWithTimestamp(tmptext, tmptime) {
            if (!tmptime || tmptime === 'undefined' || tmptext.length <= 0) {
                return tmptext
            }

            tmptext = tmptext.replace(/。|？|，|、|\?|\.|\ /g, ',')
            const words = tmptext.split(',')
            const jsontime = JSON.parse(tmptime)
            let char_index = 0
            let text_withtime = ''

            for (let i = 0; i < words.length; i++) {
                if (words[i] === 'undefined' || words[i].length <= 0) {
                    continue
                }
                if (/^[a-zA-Z]+$/.test(words[i])) {
                    text_withtime += jsontime[char_index][0] / 1000 + ':' + words[i] + '\n'
                    char_index += 1
                } else {
                    text_withtime += jsontime[char_index][0] / 1000 + ':' + words[i] + '\n'
                    char_index += words[i].length
                }
            }
            return text_withtime
        },

        // WebSocket 连接状态处理（完全按照 old App.vue 的 getConnState）
        getConnState(connState) {
            if (connState === 0) {
                // 连接成功，延迟200ms后开始录音（完全按照老版本）
                console.log('连接成功!请点击开始')
                setTimeout(() => {
                    this.startRecorder()
                    // 开始波形动画（时间在 recProcess 中更新，不需要单独的 timer）
                    this.recordingState = 'recording'
                    this.startRealTimeWaveform()
                    this.recordingLoading = false
                }, 200)
            } else if (connState === 1) {
                // 连接关闭（老版本这里没有操作）
                console.log('WebSocket 连接关闭')
            } else if (connState === 2) {
                // 连接失败（完全按照老版本）
                this.stopRecorder()
                console.log('连接地址失败,请检查asr地址和端口。或试试界面上手动授权，再连接。')
                this.recordingState = 'idle'
                this.recordingLoading = false
            }
        },

        // 启动 Recorder（迁移自 old App.vue 的 record）
        startRecorder() {
            if (this.rec) {
                this.rec.open(() => {
                    this.rec.start()
                    console.log('Recorder 开始录音')
                })
            }
        },

            // 停止 Recorder（迁移自 old App.vue 的 stop），并生成可下载的录音文件
        stopRecorder() {
            if (!this.wsconnecter || !this.rec) return

            const chunk_size = [5, 10, 5]
            const request = {
                chunk_size: chunk_size,
                wav_name: 'h5',
                is_speaking: false,
                chunk_interval: 10,
                mode: '2pass'
            }

            // 发送剩余数据
            if (this.sampleBuf && this.sampleBuf.length > 0) {
                this.wsconnecter.wsSend(this.sampleBuf)
                this.sampleBuf = new Int16Array()
            }

            // 发送结束请求
            this.wsconnecter.wsSend(JSON.stringify(request))
            this.isRec = false

            // 延迟关闭 WebSocket
            setTimeout(() => {
                if (this.wsconnecter) {
                    this.wsconnecter.wsStop()
                }
            }, 2000)

            // 停止录音并获取 WAV，用于下载
            if (this.rec) {
                this.rec.stop((blob) => {
                    if (window.Recorder && window.Recorder.pcm2wav) {
                        window.Recorder.pcm2wav(
                            { sampleRate: 16000, bitRate: 16, blob: blob },
                            (theblob) => {
                                try {
                                    // 释放上一次的 URL
                                    if (this.downloadAudioUrl) {
                                        (window.URL || window.webkitURL).revokeObjectURL(this.downloadAudioUrl)
                                    }
                                    // 生成新的下载链接
                                    const url = (window.URL || window.webkitURL).createObjectURL(theblob)
                                    this.downloadAudioUrl = url
                                    this.$message.success('录音文件已生成，可在左侧点击"下载录音"保存到本地.')
                                    
                                    // 自动上传音频文件到 /upload 接口
                                    this.uploadAudioFile(theblob)
                                    this.recentRecordingBlob = theblob
                                } catch (e) {
                                    console.error('生成录音下载链接失败:', e)
                                }
                            },
                            (msg) => {
                                console.error('PCM 转 WAV 失败:', msg)
                            }
                        )
                    }
                }, (errMsg) => {
                    console.error('停止录音失败:', errMsg)
                })
            }
        },

        // 下载最近一次录音（生成 WAV 文件）
        downloadRecordedAudio() {
            if (!this.downloadAudioUrl) {
                this.$message.warning('暂时没有可下载的录音，请先完成一次录制')
                return
            }

            const link = document.createElement('a')
            link.href = this.downloadAudioUrl
            link.download = `${Date.now()}.wav`
            document.body.appendChild(link)
            link.click()
            document.body.removeChild(link)

            this.$message.success('录音已开始下载')
        },

        async transcribeRecordedAudio() {
            if (this.translatingRecordedAudio) {
                this.$message.info('正在转译，请稍候')
                return
            }
            if (!this.recentRecordingBlob) {
                this.$message.warning('暂无可转译的录音，请先完成一次录制')
                return
            }

            this.translatingRecordedAudio = true
            const username = this.$store?.getters?.nickName || 'undown'
            let fileBlob = this.recentRecordingBlob
            if (!fileBlob.type || !fileBlob.type.startsWith('audio/')) {
                fileBlob = new Blob([fileBlob], { type: 'audio/wav' })
            }

            const file = new File([fileBlob], `recording_${Date.now()}.wav`, {
                type: 'audio/wav',
                lastModified: Date.now()
            })

            const formData = new FormData()
            formData.append('file', file)
            formData.append('username', username)

            this.$emit('realtime-transcription', '')
            this.$emit('realtime-transcription', '处理中，请稍候...')

            try {
                const response = await fetch(API_GET_TRANSCRIPT, {
                    method: 'POST',
                    body: formData
                })
                const data = await response.json()

                if (data && data.transcript) {
                    this.$emit('realtime-transcription', data.transcript)
                    this.$message.success('转译完成')
                } else if (data && data.error) {
                    const errorMsg = `服务器出错: ${data.error}`
                    this.$emit('realtime-transcription', errorMsg)
                    this.$message.error('转译失败')
                } else {
                    this.$emit('realtime-transcription', '未知错误')
                    this.$message.error('转译失败，返回数据为空')
                }
            } catch (error) {
                console.error('转译录音失败:', error)
                this.$emit('realtime-transcription', '请求失败，请查看控制台错误信息。')
                this.$message.error('转译录音失败，请重试')
            } finally {
                this.translatingRecordedAudio = false
            }
        },

        // 录音处理回调（迁移自 old App.vue 的 recProcess）
        recProcess(buffer, powerLevel, bufferDuration, bufferSampleRate, newBufferIdx, asyncEnd) {
            // 更新录音时长和波动条（无论是否启用实时识别，只要处于录音状态就根据音量刷新 UI）
            if (this.recordingState === 'recording') {
                // 使用 Recorder 提供的 bufferDuration 计算时长（毫秒）
                this.recordingTime = Math.floor(bufferDuration / 1000)

                // --- 1. 现代律动模式数据更新 ---
                const baseHeight = 20
                const amplitude = Math.max(powerLevel, 5) // 避免完全不动

                const leftData = []
                const rightData = []

                for (let i = 0; i < 15; i++) {
                    const randomFactor = 0.5 + (Math.random() - 0.5) * 0.6 // 大约 0.2 - 0.8
                    const height = baseHeight + amplitude * randomFactor
                    leftData.push(height)
                }

                for (let i = 0; i < 15; i++) {
                    const randomFactor = 0.5 + (Math.random() - 0.5) * 0.6
                    const height = baseHeight + amplitude * randomFactor
                    rightData.push(height)
                }

                this.leftWaveBars = leftData
                this.rightWaveBars = rightData

                // --- 2. 复古模式 VU 表指针更新 ---
                // powerLevel 通常在 0-100 之间
                // 映射到 -45deg (min) 到 45deg (max)
                // 增加大幅随机抖动模拟真实指针的机械感 (更灵敏)
                const jitter = (Math.random() - 0.5) * 15; 
                // 放大信号倍率，让指针更容易大幅摆动
                let targetAngle = -45 + (powerLevel / 60) * 90 + jitter;
                
                // 限制角度范围
                if (targetAngle < -45) targetAngle = -45;
                if (targetAngle > 45) targetAngle = 45;

                // 减少惯性，加快响应速度 (原为 0.6/0.4，改为 0.3/0.7)
                this.vuNeedleAngle = this.vuNeedleAngle * 0.3 + targetAngle * 0.7;
            } else {
                // 非录音状态回落到底部
                this.vuNeedleAngle = -45;
                this.leftWaveBars = Array(15).fill(20);
                this.rightWaveBars = Array(15).fill(20);
            }

            // 实时识别时，按老版本逻辑进行重采样并推送到 WebSocket
            if (this.isRec && this.sampleBuf) {
                const data_48k = buffer[buffer.length - 1]
                const array_48k = new Array(data_48k)
                const data_16k = window.Recorder.SampleData(array_48k, bufferSampleRate, 16000).data
                this.sampleBuf = Int16Array.from([...this.sampleBuf, ...data_16k])

                const chunk_size = 960

                // 分块发送
                while (this.sampleBuf.length >= chunk_size && this.wsconnecter) {
                    this.sendBuf = this.sampleBuf.slice(0, chunk_size)
                    this.sampleBuf = this.sampleBuf.slice(chunk_size, this.sampleBuf.length)
                    this.wsconnecter.wsSend(this.sendBuf)
                }
            }
        },

        // 启动 WebSocket 实时识别（迁移自 old App.vue 的 startWS）
        startWS() {
            this.start()
            this.$message.success('实时转译开始！')
        },

        // 识别启动、停止、清空操作（迁移自 old App.vue 的 start）
        start() {
            // 清除显示
            this.clear()
            // 启动连接
            const ret = this.wsconnecter.wsStart()
            // 1 is ok, 0 is error
            if (ret === 1) {
                console.log('正在连接 ASR 服务器，请等待...')
                this.isRec = true
                return 1
            } else {
                console.log('请点击开始...')
                return 0
            }
        },

        // 清空文本（迁移自 old App.vue 的 clear）
        clear() {
            this.rec_text = ''
            this.offline_text = ''
        },

        // 停止 WebSocket 实时识别（迁移自 old App.vue 的 stopWS）
        stopWS() {
            this.stopRecorder()
            this.$message.success('实时转译结束！')
        },

        // 开始录音（完全按照 old App.vue 的 toggleRecording 流程）
        startRecording() {
            // 完全按照老版本的 toggleRecording 流程
            // 清空文本和状态
            this.offline_text = ''
            this.rec_text = ''
            this.recordingTime = 0
            this.audioChunks = []
            this.recentRecordingBlob = null
            this.translatingRecordedAudio = false
            // 清空右侧转写框（等价于老版本的 initTranscript.value = ''）
            this.$emit('realtime-transcription', '')
            
            // 设置录音状态
            this.recordingState = 'recording'
            
            // 启动 WebSocket 实时识别（完全按照老版本的 startWS 流程）
            if (this.enableRealtimeTranscription && this.wsconnecter) {
                this.startWS()
            } else {
                // 如果不启用实时识别，直接开始录音（使用 Recorder）
                this.startRecorder()
                this.recordingState = 'recording'
                this.startTimer()
                this.startRealTimeWaveform()
                this.$message.success('开始录音')
            }
        },

        // 暂停录音（老版本没有此功能，保留但不使用 MediaRecorder）
        pauseRecording() {
            // 仅在录音进行中时才能暂停
            if (this.recordingState !== 'recording') return

            if (this.rec) {
                try {
                    // 使用 Recorder 自带的 pause 功能（来自 oldmetting 的 recorder-core.js）
                    this.rec.pause()
                } catch (e) {
                    console.error('暂停录音失败:', e)
                }
            }

            // 更新状态与动画/计时
            this.recordingState = 'paused'
            this.stopTimer()
            this.stopWaveformAnimation()

            this.$message.info('已暂停录音')
        },

        // 继续录音（老版本没有此功能，保留但不使用 MediaRecorder）
        resumeRecording() {
            // 仅在暂停状态下才能继续
            if (this.recordingState !== 'paused') return

            if (this.rec) {
                try {
                    // 使用 Recorder 自带的 resume 功能
                    this.rec.resume()
                } catch (e) {
                    console.error('恢复录音失败:', e)
                }
            }

            this.recordingState = 'recording'

            // 非实时识别模式下，计时器与波形是本地驱动的，需要重新启动
            if (!this.enableRealtimeTranscription || !this.wsconnecter) {
                this.startTimer()
                this.startRealTimeWaveform()
            }

            this.$message.success('继续录音')
        },

        confirmStopRecording() {
            MessageBox.confirm('确定要完成录制吗？录音将结束并开始转写。', '完成录制', {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                type: 'info',
                center: true
            }).then(() => {
                this.stopRecording()
            }).catch(() => {})
        },

        // 实体按钮点击处理
        triggerDeckAction(type) {
            if (type === 'play') {
                this.recordingState === 'recording' ? this.pauseRecording() : this.resumeRecording();
            } else if (type === 'eject') {
                this.activeSideBtn = 'eject';
                setTimeout(() => this.activeSideBtn = '', 200);
                this.cancelRecording();
            } else if (type === 'finish') {
                this.activeSideBtn = 'finish';
                setTimeout(() => this.activeSideBtn = '', 200);
                this.confirmStopRecording();
            }
        },

        // 取消录音（完全按照 old App.vue 的 cancelRecording 流程）
        cancelRecording() {
            // 完全按照老版本：清空所有状态
            this.offline_text = ''
            this.rec_text = ''
            this.recordingState = 'idle'
            this.recordingTime = 0
            this.audioChunks = []

            // 清理最近录音下载链接
            if (this.downloadAudioUrl) {
                try {
                    (window.URL || window.webkitURL).revokeObjectURL(this.downloadAudioUrl)
                } catch (e) {
                    console.error('释放录音链接失败:', e)
                }
                this.downloadAudioUrl = ''
            }
            this.recentRecordingBlob = null
            
            // 如果正在识别，停止 WebSocket
            if (this.isRec && this.wsconnecter) {
                this.stopWS()
            }
            
            // 清空转写文本（emit 空字符串）
            this.$emit('realtime-transcription', '')
            
            this.$message.info('已取消录制')
        },

        // 停止录音（完全按照 old App.vue 的 stopRecording 流程）
        stopRecording() {
            // 完全按照老版本的 stopRecording：调用 stopWS()
            this.stopWS()
            // 改为进入预览状态，而不是直接回首页
            this.recordingState = 'reviewed' 
            this.stopTimer()
            this.stopWaveformAnimation()
        },

        // 返回首页（从预览状态）
        backToHome() {
            this.recordingState = 'idle'
            this.offline_text = ''
            this.rec_text = ''
            this.recordingTime = 0
            this.audioChunks = []
            this.downloadAudioUrl = ''
            this.recentRecordingBlob = null
            this.isPlaying = false
            this.playProgress = 0
            this.currentTime = 0
            this.$emit('realtime-transcription', '')
        },

        // 播放器控制
        togglePlay() {
            const audio = this.$refs.audioPlayer;
            if (!audio) return;
            
            if (this.isPlaying) {
                audio.pause();
            } else {
                audio.play();
            }
            this.isPlaying = !this.isPlaying;
        },
        
        onTimeUpdate() {
            if (this.isDraggingRetro) return;
            const audio = this.$refs.audioPlayer;
            if (!audio) return;
            this.currentTime = audio.currentTime;
            this.playProgress = (audio.currentTime / audio.duration) * 100 || 0;
        },
        
        onAudioEnded() {
            this.isPlaying = false;
            this.playProgress = 0;
            this.currentTime = 0;
        },
        
        onAudioLoaded() {
            const audio = this.$refs.audioPlayer;
            if (audio) {
                this.audioDuration = audio.duration;
            }
        },
        
        onSliderChange(val) {
            const audio = this.$refs.audioPlayer;
            if (audio) {
                const time = (val / 100) * audio.duration;
                audio.currentTime = time;
                this.currentTime = time;
            }
        },

        // 复古进度条拖拽逻辑
        startRetroDrag(e) {
            this.isDraggingRetro = true;
            this.updateRetroProgress(e);
            window.addEventListener('mousemove', this.updateRetroProgress);
            window.addEventListener('mouseup', this.stopRetroDrag);
        },

        stopRetroDrag() {
            this.isDraggingRetro = false;
            window.removeEventListener('mousemove', this.updateRetroProgress);
            window.removeEventListener('mouseup', this.stopRetroDrag);
        },

        updateRetroProgress(e) {
            const progressBar = this.$refs.retroProgressBar;
            if (!progressBar) return;

            const rect = progressBar.getBoundingClientRect();
            let percentage = (e.clientX - rect.left) / rect.width;
            percentage = Math.max(0, Math.min(1, percentage));

            this.playProgress = percentage * 100;
            
            const audio = this.$refs.audioPlayer;
            if (audio && audio.duration) {
                const time = percentage * audio.duration;
                audio.currentTime = time;
                this.currentTime = time;
            }
        },

        startTimer() {
            this.recordingTimer = setInterval(() => {
                this.recordingTime++
            }, 1000)
        },

        stopTimer() {
            if (this.recordingTimer) {
                clearInterval(this.recordingTimer)
                this.recordingTimer = null
            }
        },

        formatTime(seconds) {
            const wholeSeconds = Math.floor(seconds)
            const mins = Math.floor(wholeSeconds / 60)
            const secs = wholeSeconds % 60
            return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`
        },

        startRealTimeWaveform() {
            // 动画由 recProcess 驱动，这里重置状态即可
            this.vuNeedleAngle = -45;
            this.leftWaveBars = Array(15).fill(20);
            this.rightWaveBars = Array(15).fill(20);
        },

        stopWaveformAnimation() {
            this.vuNeedleAngle = -45;
            this.leftWaveBars = Array(15).fill(20);
            this.rightWaveBars = Array(15).fill(20);
        },

        beforeUpload(file) {
            const isAudio = file.type.startsWith('audio/')
            const isLt200M = file.size / 1024 / 1024 < 200

            if (!isAudio) {
                this.$message.error('只能上传音频文件!')
                return false
            }
            if (!isLt200M) {
                this.$message.error('音频文件大小不能超过 200MB!')
                return false
            }

            this.handleFile(file)
            return false
        },

        async handleFile(file) {
            this.$message.info('正在处理音频文件...')
            // 保存文件信息
            this.uploadedFile = {
                name: file.name,
                size: file.size,
                type: file.type,
                lastModified: file.lastModified
            }
            const normalizedFile = file instanceof File
                ? file
                : new File([file], file.name || `upload_${Date.now()}.wav`, { type: file.type || 'audio/wav' })
            this.$emit('file-uploaded', normalizedFile)
        },

        // 格式化文件大小
        formatFileSize(bytes) {
            if (bytes === 0) return '0 B'
            const k = 1024
            const sizes = ['B', 'KB', 'MB', 'GB']
            const i = Math.floor(Math.log(bytes) / Math.log(k))
            return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
        },

        // 清除上传的文件
        clearUploadedFile() {
            this.uploadedFile = null
        },

        handleUploadSuccess() {
            this.$message.success('上传成功')
        },

        handleUploadError() {
            this.$message.error('上传失败')
        },

        // 上传音频文件到 /upload 接口
        async uploadAudioFile(audioBlob) {
            console.log('上传音频文件到 /upload 接口');
            if (!audioBlob) {
                console.error('音频文件为空，无法上传')
                return
            }

            try {
                // 获取 username（优先使用 store 中的 nickName，否则使用默认值）
                const username = this.$store?.getters?.nickName || 'undown'
                // 确保 blob 有正确的 MIME 类型
                let fileBlob = audioBlob
                if (!audioBlob.type || !audioBlob.type.startsWith('audio/')) {
                    fileBlob = new Blob([audioBlob], { type: 'audio/wav' })
                    console.log('重新创建 blob，设置 MIME 类型为 audio/wav')
                }
                
                console.log('上传的 blob 信息:', {
                    size: fileBlob.size,
                    type: fileBlob.type,
                    name: `recording_${Date.now()}.wav`
                })
                
                // 创建 FormData
                const formData = new FormData()
                // 使用 File 对象而不是 Blob，确保有正确的文件名和类型
                const file = new File([fileBlob], `recording_${Date.now()}.wav`, { 
                    type: 'audio/wav',
                    lastModified: Date.now()
                })
                formData.append('file', file)
                formData.append('username', username)

                // 调用上传接口
                const response = await fetch(API_UPLOAD, {
                    method: 'POST',
                    body: formData
                })

                if (response.ok) {
                    const result = await response.json()
                    console.log('音频文件上传成功:', result)
                    this.$message.success('录音文件已自动上传')
                } else {
                    const errorText = await response.text()
                    console.error('上传失败:', response.status, errorText)
                    this.$message.warning('录音文件上传失败，请稍后重试')
                }
            } catch (error) {
                console.error('上传音频文件时发生错误:', error)
                this.$message.warning('录音文件上传失败，请稍后重试')
            }
        },

        cleanup() {
            this.stopTimer()
            this.stopWaveformAnimation()

            // 停止 WebSocket 实时识别
            if (this.enableRealtimeTranscription && this.isRec) {
                this.stopWS()
            }

            if (this.mediaRecorder && this.recordingState !== 'idle') {
                try {
                    if (this.recordingState === 'recording') {
                        this.mediaRecorder.stop()
                    }
                } catch (error) {
                    console.error('停止录音器失败:', error)
                }
            }

            if (this.audioContext) {
                this.audioContext.close().catch(console.error)
                this.audioContext = null
            }

            if (this.audioStream) {
                this.audioStream.getTracks().forEach(track => track.stop())
                this.audioStream = null
            }

            this.mediaRecorder = null
            this.analyser = null
        }
    }
}
</script>

<style scoped lang="scss">
.recording-panel {
    position: relative;
    overflow: hidden;
    height: 100%;
    display: flex;
    flex-direction: column;
    background: rgba(255, 255, 255, 0.98);
    backdrop-filter: blur(20px);
    box-shadow: 0 12px 48px rgba(0, 0, 0, 0.15);
    border-radius: 24px 0 0 24px;

    // 背景装饰
    .background-decorations {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        pointer-events: none;
        overflow: hidden;
        z-index: 0;
        background: linear-gradient(180deg, #f8fbff 0%, #eef5fc 100%);

        /* 复古氛围光环 */
        .retro-aura {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 600px;
            height: 600px;
            background: radial-gradient(circle, rgba(79, 140, 245, 0.08) 0%, transparent 70%);
            z-index: 0;
            pointer-events: none;
            animation: auraPulse 4s ease-in-out infinite;
        }

        @keyframes auraPulse {
            0%, 100% { opacity: 0.5; transform: translate(-50%, -50%) scale(1); }
            50% { opacity: 0.8; transform: translate(-50%, -50%) scale(1.1); }
        }

        .decoration-circle {
            position: absolute;
            border-radius: 50%;
            background: linear-gradient(135deg, rgba(79, 140, 245, 0.1), rgba(125, 174, 250, 0.1));
            animation: float 6s ease-in-out infinite;

            &.circle-1 {
                width: 200px;
                height: 200px;
                top: -50px;
                right: -50px;
                animation-delay: 0s;
            }

            &.circle-2 {
                width: 150px;
                height: 150px;
                bottom: 100px;
                left: -30px;
                animation-delay: 2s;
            }

            &.circle-3 {
                width: 100px;
                height: 100px;
                top: 50%;
                right: 50px;
                animation-delay: 4s;
            }
        }

        .decoration-wave {
            position: absolute;
            width: 300px;
            height: 300px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(87, 145, 245, 0.3) 0%, transparent 70%);
            animation: pulse 4s ease-in-out infinite;

            &.wave-1 {
                top: 20%;
                left: 10%;
                animation-delay: 0s;
                
            }

            &.wave-2 {
                bottom: 20%;
                right: 10%;
                animation-delay: 2s;
            }
        }

        @keyframes float {
            0%, 100% {
                transform: translate(0, 0) scale(1);
                opacity: 0.6;
            }
            50% {
                transform: translate(20px, -20px) scale(1.1);
                opacity: 0.8;
            }
        }

        @keyframes pulse {
            0%, 100% {
                transform: scale(1);
                opacity: 0.4;
            }
            50% {
                transform: scale(1.2);
                opacity: 0.6;
            }
        }
    }

    // 左上角环境监测
    .env-monitor {
        position: absolute;
        top: 24px;
        left: 24px;
        display: flex;
        gap: 16px;
        z-index: 10;

        .monitor-item {
            background: rgba(255, 255, 255, 0.8);
            backdrop-filter: blur(4px);
            padding: 8px 12px;
            border-radius: 8px;
            border: 1px solid rgba(0,0,0,0.05);
            display: flex;
            flex-direction: column;
            gap: 4px;
            min-width: 60px;

            .label {
                font-size: 10px;
                color: #909399;
                font-weight: 700;
                letter-spacing: 1px;
            }

            .value {
                font-family: 'Courier New', monospace;
                font-size: 14px;
                font-weight: 700;
                color: #606266;
            }

            .bar-group {
                display: flex;
                gap: 2px;
                height: 12px;
                align-items: flex-end;

                .bar {
                    width: 3px;
                    background: #4f8cf5;
                    border-radius: 1px;
                    animation: barBounce 0.5s infinite alternate;
                }
            }
        }
        @keyframes barBounce { to { height: 20%; } }
    }

    .panel-content {
        position: relative;
        z-index: 1;
        flex: 1;
        padding: 20px 24px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: stretch;
        gap: 32px;
        min-height: 0;
        overflow: hidden;
        overflow-y: auto;

        &::-webkit-scrollbar {
            width: 6px;
        }

        &::-webkit-scrollbar-track {
            background: rgba(0, 0, 0, 0.05);
            border-radius: 3px;
        }

        &::-webkit-scrollbar-thumb {
            background: rgba(79, 140, 245, 0.3);
            border-radius: 3px;

            &:hover {
                background: rgba(79, 140, 245, 0.5);
            }
        }
    }

    // 风格切换开关
    .style-switcher {
        position: absolute;
        top: 20px;
        right: 24px;
        display: flex;
        background: rgba(0, 0, 0, 0.05);
        border-radius: 20px;
        padding: 4px;
        z-index: 10;
        gap: 4px;

        .switch-item {
            padding: 6px 16px;
            font-size: 13px;
            color: #5c6c80;
            border-radius: 16px;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 6px;

            &:hover {
                color: #4f8cf5;
                background: rgba(255, 255, 255, 0.5);
            }

            &.active {
                background: #fff;
                color: #4f8cf5;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                font-weight: 600;
            }
        }
    }

    // 模块切换过渡动画
    .panel-switch-enter-active {
                transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
        
        .title-section,
        .action-area,
        .mic-with-waves,
        .recording-status-info,
        .control-buttons-group {
                    animation: fadeInUp 0.35s cubic-bezier(0.4, 0, 0.2, 1) forwards;
        }
        
        .title-section {
            animation-delay: 0.1s;
            opacity: 0;
        }
        
        .action-area {
            animation-delay: 0.2s;
            opacity: 0;
        }
        
        .mic-with-waves {
            animation-delay: 0.1s;
            opacity: 0;
        }
        
        .recording-status-info {
            animation-delay: 0.2s;
            opacity: 0;
        }
        
        .control-buttons-group {
            animation-delay: 0.3s;
            opacity: 0;
        }
    }

            .panel-switch-leave-active {
                transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .panel-switch-enter {
        opacity: 0;
        transform: translateY(20px) scale(0.98);
    }

    .panel-switch-enter-to {
        opacity: 1;
        transform: translateY(0) scale(1);
    }

    .panel-switch-leave {
        opacity: 1;
        transform: translateY(0) scale(1);
    }

    .panel-switch-leave-to {
        opacity: 0;
        transform: translateY(-20px) scale(0.98);
    }

            @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(15px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .title-section {
        text-align: center;
        margin-bottom: 20px;
        width: 100%;

        .title-icon-wrapper {
            position: relative;
            display: inline-block;
            margin-bottom: 16px;

            .title-icon-glow {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                width: 120px;
                height: 120px;
                background: radial-gradient(circle, rgba(79, 140, 245, 0.3) 0%, transparent 70%);
                border-radius: 50%;
                animation: glow 3s ease-in-out infinite;
                z-index: 0;
            }

            .title-icon {
                position: relative;
                font-size: 64px;
                z-index: 1;
                filter: drop-shadow(0 4px 12px rgba(79, 140, 245, 0.3));
                animation: iconFloat 3s ease-in-out infinite;
            }

            @keyframes glow {
                0%, 100% {
                    transform: translate(-50%, -50%) scale(1);
                    opacity: 0.5;
                }
                50% {
                    transform: translate(-50%, -50%) scale(1.2);
                    opacity: 0.8;
                }
            }

            @keyframes iconFloat {
                0%, 100% {
                    transform: translateY(0);
                }
                50% {
                    transform: translateY(-8px);
                }
            }
        }

        .title-text {
            margin-bottom: 24px;

            h1 {
                font-size: 32px;
                font-weight: 700;
                margin: 0 0 8px;
                background: linear-gradient(135deg, #4f8cf5, #2563eb);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                animation: textShine 3s ease-in-out infinite;
            }

            p {
                font-size: 15px;
                color: #5c6c80;
                margin: 0;
            }

            @keyframes textShine {
                0%, 100% {
                    opacity: 1;
                }
                50% {
                    opacity: 0.8;
                }
            }
        }

        .feature-hints {
            width: 400px;
            margin: 0 auto;
            display: flex;
            flex-direction: column;
            gap: 12px;
            margin-top: 32px;
            padding: 20px;
            background: rgba(79, 140, 245, 0.05);
            border-radius: 16px;
            border: 1px solid rgba(79, 140, 245, 0.1);
            
            .hint-item {
                display: flex;
                align-items: center;
                gap: 10px;
                font-size: 13px;
                color: #5c6c80;
                transition: all 0.3s ease;

                i {
                    width: 24px;
                    height: 24px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    background: linear-gradient(135deg, rgba(79, 140, 245, 0.1), rgba(125, 174, 250, 0.1));
                    border-radius: 6px;
                    color: #4f8cf5;
                    font-size: 14px;
                }

                &:hover {
                    color: #4f8cf5;
                    transform: translateX(4px);

                    i {
                        background: linear-gradient(135deg, #4f8cf5, #2563eb);
                        color: #fff;
                        transform: scale(1.1);
                    }
                }
            }
        }

        // 最近一次录音卡片
        .last-recording-card {
            margin-top: 16px;
            padding: 12px 16px;
            border-radius: 12px;
            background: rgba(79, 140, 245, 0.04);
            border: 1px solid rgba(79, 140, 245, 0.12);
            display: flex;
            flex-direction: column;
            gap: 8px;

            .last-recording-header {
                display: flex;
                align-items: center;
                gap: 10px;

                i {
                    font-size: 18px;
                    color: #4f8cf5;
                }

                .text {
                    .title {
                        font-size: 13px;
                        font-weight: 600;
                        color: #1f2d3d;
                    }

                    .subtitle {
                        font-size: 12px;
                        color: #909399;
                    }
                }
            }

            .last-recording-body {
                display: flex;
                align-items: center;
                gap: 12px;
                margin-top: 4px;

                .last-recording-audio {
                    flex: 1;
                    height: 32px;
                }
            }
        }
    }

    .recording-display {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 24px;
        width: 100%;

        .mic-with-waves {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 20px;
            width: 100%;

            .wave-left,
            .wave-right {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 3px;
                height: 120px;

                .wave-bar {
                    width: 4px;
                    background: linear-gradient(180deg, #4f8cf5, #2563eb);
                    border-radius: 2px;
                    animation: waveMotion 0.8s ease-in-out infinite;
                    min-height: 20px;
                }

                @keyframes waveMotion {
                    0%, 100% {
                        transform: scaleY(0.3);
                    }
                    50% {
                        transform: scaleY(1);
                    }
                }
            }

            .mic-container {
                position: relative;
                width: 120px;
                height: 120px;
                display: flex;
                align-items: center;
                justify-content: center;

                .mic-outer-ring {
                    position: absolute;
                    inset: 0;
                    border-radius: 50%;
                    background: linear-gradient(135deg, #ff6b6b, #ff4757);
                    opacity: 0.2;
                    animation: pulseOuter 2s ease-out infinite;
                }

                @keyframes pulseOuter {
                    0% {
                        transform: scale(0.9);
                        opacity: 0.2;
                    }
                    100% {
                        transform: scale(1.4);
                        opacity: 0;
                    }
                }

                .mic-inner-circle {
                    position: relative;
                    z-index: 1;
                    width: 100px;
                    height: 100px;
                    border-radius: 50%;
                    background: linear-gradient(135deg, #ff6b6b, #ff4757);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    box-shadow: 0 8px 32px rgba(255, 107, 107, 0.5);

                    .mic-icon {
                        font-size: 44px;
                        color: #fff;

                        &.recording {
                            animation: micBounce 1.5s ease-in-out infinite;
                        }

                        &.paused {
                            opacity: 0.7;
                        }
                    }

                    @keyframes micBounce {
                        0%, 100% {
                            transform: scale(1);
                        }
                        50% {
                            transform: scale(1.15);
                        }
                    }
                }
            }
        }

        .retro-container {
            display: flex;
            flex-direction: column; /* 改回 column 布局，因为加了下方的大卡片 */
            justify-content: center;
            align-items: center;
            gap: 40px;
            margin-bottom: 20px;
            padding-left: 0; /* 重置左边距 */

            /* 包裹磁带和侧边按钮的容器，用于保持它们原来的相对位置 */
            .tape-wrapper-level {
                display: flex;
                flex-direction: row;
                align-items: center;
                gap: 0;
                position: relative;
                justify-content: center; /* 确保磁带水平居中 */
            }

            /* 磁带样式 */
            .cassette-tape {
                /* ... 原有样式保持不变 ... */
                flex-shrink: 0;
                position: relative;
                width: 340px;
                height: 220px;
                /* 3D 实体质感：渐变 + 厚边框 */
                background: linear-gradient(160deg, #e3f2fd 0%, #bbdefb 100%);
                border: 1px solid #90caf9;
                border-bottom: 8px solid #64b5f6; /* 底部厚度 */
                border-right: 2px solid #90caf9;  /* 右侧微厚度 */
                border-radius: 24px;
                
                display: flex;
                flex-direction: column;
                align-items: center;
                padding: 15px;
                box-sizing: border-box;
                /* 轻微透视 + 左移以视觉居中 */
                transform: perspective(1000px) rotateX(5deg) rotateY(0deg) translateX(0px);
                transition: transform 0.3s ease;

                &:hover {
                    transform: perspective(1000px) rotateX(2deg) translateY(-5px) translateX(0px);
                }

                /* 螺丝装饰 */
                .tape-screw {
                    position: absolute;
                    width: 10px;
                    height: 10px;
                    background: #90caf9;
                    border-radius: 50%;
                    box-shadow: inset 1px 1px 2px rgba(0,0,0,0.1);
                    z-index: 2;
                    
                    &::after {
                        content: '';
                        position: absolute;
                        top: 50%;
                        left: 50%;
                        width: 60%;
                        height: 2px;
                        background: #64b5f6;
                        transform: translate(-50%, -50%) rotate(45deg);
                    }
                    &::before {
                        content: '';
                        position: absolute;
                        top: 50%;
                        left: 50%;
                        width: 60%;
                        height: 2px;
                        background: #64b5f6;
                        transform: translate(-50%, -50%) rotate(-45deg);
                    }

                    &.topleft { top: 12px; left: 12px; }
                    &.topright { top: 12px; right: 12px; }
                    &.bottomleft { bottom: 12px; left: 12px; }
                    &.bottomright { bottom: 12px; right: 12px; }
                }

                /* 磁带贴纸区域 - 集成仪表盘 */
                .tape-label {
                    width: 92%;
                    height: 110px;
                    background: #fff;
                    border-radius: 8px 8px 4px 4px;
                    padding: 8px 12px;
                    box-sizing: border-box;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    position: relative;
                    box-shadow: 0 2px 8px rgba(33, 150, 243, 0.1);
                    border: 1px solid #e3f2fd;

                    /* 顶部彩色条纹装饰 */
                    &::before {
                        content: '';
                        position: absolute;
                        top: 0;
                        left: 10px;
                        right: 10px;
                        height: 4px;
                        background: linear-gradient(90deg, #42a5f5, #2196f3, #1e88e5);
                        border-radius: 0 0 4px 4px;
                    }

                    /* 集成的 VU 表 */
                    .integrated-vu {
                        width: 70px;
                        height: 50px;
                        position: relative;
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        justify-content: flex-end;
                        
                        .vu-scale {
                            width: 60px;
                            height: 30px;
                            border-top-left-radius: 35px;
                            border-top-right-radius: 35px;
                            border: 2px solid #e0e0e0;
                            border-bottom: none;
                            position: relative;
                            background: radial-gradient(circle at bottom, #fff, #f5f5f5);
                            
                            /* 刻度线 */
                            &::before {
                                content: '';
                                position: absolute;
                                inset: 2px;
                                border-top-left-radius: 30px;
                                border-top-right-radius: 30px;
                                border: 1px dashed #bdbdbd;
                                border-bottom: none;
                            }
                        }

                        .vu-needle {
                            position: absolute;
                            bottom: 18px;
                            left: 50%;
                            width: 2px;
                            height: 28px;
                            background: #ef5350;
                            transform-origin: bottom center;
                            transition: transform 0.1s cubic-bezier(0.1, 0.7, 1.0, 0.1);
                            z-index: 2;
                            
                            &::after {
                                content: '';
                                position: absolute;
                                bottom: -2px;
                                left: -3px;
                                width: 8px;
                                height: 8px;
                                background: #424242;
                                border-radius: 50%;
                            }
                        }

                        .vu-text {
                            font-size: 10px;
                            font-weight: bold;
                            color: #90caf9;
                            margin-top: 4px;
                        }
                    }

                    /* 中间信息区 */
                    .center-display {
                        flex: 1;
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        justify-content: center;
                        gap: 2px;

                        .status-text-retro {
                            font-size: 18px;
                            font-weight: 600;
                            color: #1976d2;
                            letter-spacing: 1px;
                            opacity: 0.8;
                            transform: translateY(20px);
                        }

                        .digital-clock {
                            font-family: 'Courier New', monospace;
                            font-size: 25px;
                            font-weight: 700;
                            color: #1565c0;
                            background: #ffffff;
                            padding: 4px 14px;
                            border-radius: 6px;
                            letter-spacing: 2px;
                            box-shadow: inset 0 2px 4px rgba(0,0,0,0.05);
                            transform: translateY(80px);
                        }
                    }
                }

                .tape-window {
                    position: absolute;
                    top: 85px;
                    width: 55%;
                    height: 50px;
                    background: rgba(255,255,255,0.9);
                    border-radius: 25px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 0 15px;
                    box-sizing: border-box;
                    border: 1px solid #bbdefb;
                    overflow: hidden;
                    z-index: 5;
                    box-shadow: inset 0 2px 6px rgba(0,0,0,0.05);

                    .reel {
                        width: 36px;
                        height: 36px;
                        border-radius: 50%;
                        background: #e3f2fd;
                        position: relative;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        border: 1px solid #bbdefb;

                        .reel-spokes {
                            width: 100%;
                            height: 100%;
                            background: 
                                radial-gradient(circle at center, transparent 30%, #64b5f6 31%, #64b5f6 35%, transparent 36%),
                                linear-gradient(0deg, transparent 45%, #64b5f6 45%, #64b5f6 55%, transparent 55%),
                                linear-gradient(60deg, transparent 45%, #64b5f6 45%, #64b5f6 55%, transparent 55%),
                                linear-gradient(120deg, transparent 45%, #64b5f6 45%, #64b5f6 55%, transparent 55%);
                            border-radius: 50%;
                            opacity: 0.6;
                            
                            &.spinning {
                                animation: spin 2s linear infinite;
                            }
                        }
                    }

                    .tape-link {
                        flex: 1;
                        height: 20px;
                        background: #e3f2fd;
                        margin: 0 10px;
                        opacity: 0.3;
                    }
                }

                .tape-bottom {
                    position: absolute;
                    bottom: 0;
                    width: 70%;
                    height: 30px;
                    background: #bbdefb;
                    clip-path: polygon(10% 0, 90% 0, 100% 100%, 0 100%);
                    opacity: 0.5;
                }
            }
            /* 下方实体控制面板 */
            .control-deck {
                width: 360px;
                margin-top: 15px;
                position: relative;
                z-index: 5;
                display: flex;
                justify-content: center;

                .deck-surface {
                    width: 100%;
                    height: 80px;
                    background: linear-gradient(180deg, #ecf5ff 0%, #bbdefb 70%, #9fc5f7 100%);
                    border-radius: 18px;
                    display: flex;
                    justify-content: space-around;
                    align-items: center;
                    padding: 12px 36px;
                    box-sizing: border-box;
                    border: 1px solid rgba(15, 76, 129, 0.2);
                    box-shadow: inset 0 14px 22px rgba(255,255,255,0.45);
                }

                .deck-btn {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    gap: 8px;
                    cursor: pointer;

                    .btn-cap {
                        width: 56px;
                        height: 40px;
                        border-radius: 10px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 18px;
                        font-weight: 600;
                        border: 1px solid rgba(0,0,0,0.1);
                        box-shadow:
                            inset 0 2px 6px rgba(255,255,255,0.7),
                            0 3px 6px rgba(15, 76, 129, 0.25);
                        transition: transform 0.1s ease, box-shadow 0.1s ease;
                    }

                    &:hover .btn-cap {
                        transform: translateY(2px);
                        box-shadow:
                            inset 0 2px 6px rgba(255,255,255,0.7),
                            0 2px 4px rgba(15, 76, 129, 0.2);
                    }

                    &:active .btn-cap {
                        transform: translateY(4px);
                        box-shadow:
                            inset 0 2px 6px rgba(255,255,255,0.7),
                            0 1px 2px rgba(15, 76, 129, 0.15);
                    }

                    .btn-label {
                        font-size: 12px;
                        font-weight: 700;
                        color: #0d47a1;
                        letter-spacing: 0.1em;
                    }

                    &.cancel-btn .btn-cap {
                        background: linear-gradient(180deg, #ffcdd2, #e57373);
                        color: #b71c1c;
                    }

                    &.play-btn .btn-cap {
                        background: linear-gradient(180deg, #bbdefb, #64b5f6);
                        color: #1565c0;
                    }

                    &.finish-btn .btn-cap {
                        background: linear-gradient(180deg, #c8e6c9, #81c784);
                        color: #1b5e20;
                    }
                }
            }
            
            @keyframes spin {
                from { transform: rotate(0deg); }
                to { transform: rotate(360deg); }
            }
        }

        /* 现代模式下的状态信息 */
        .recording-status-info {
            text-align: center;

            .status-label {
                font-size: 16px;
                font-weight: 600;
                color: #1f2d3d;
                margin-bottom: 12px;
            }

            .time-display {
                font-size: 32px;
                font-weight: 700;
                color: #4f8cf5;
                font-family: 'Courier New', monospace;
            }
        }

        .control-buttons-group {
            display: flex;
            gap: 24px;
            justify-content: center;
            align-items: center;
            padding-top: 20px;

            .control-btn {
                min-width: 50px;
                height: 50px;
                padding: 0 28px;
                font-size: 15px;
                font-weight: 600;
                border-radius: 25px;
                border: none;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
                cursor: pointer;
                outline: none;
                position: relative;
                overflow: hidden;
                
                span {
                    position: relative;
                    z-index: 1;
                    font-size: 15px;
                    letter-spacing: 1px;
                }

                i {
                    position: relative;
                    z-index: 1;
                    font-size: 18px;
                }

                /* 光泽流光效果 */
                &::after {
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: linear-gradient(rgba(255,255,255,0.2), transparent);
                    z-index: 0;
                }

                &:hover {
                    transform: translateY(-3px);
                }
                
                &:active {
                    transform: translateY(-1px);
                    filter: brightness(0.95);
                }

                /* 取消按钮 - 极简白灰风格 */
                &.cancel-btn {
                    background: #ffffff;
                    color: #909399;
                    border: 1px solid #e4e7ed;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
                    min-width: 130px;

                    &:hover {
                        color: #f56c6c;
                        border-color: #fbc4c4;
                        background: #fff5f5;
                        box-shadow: 0 8px 20px rgba(245, 108, 108, 0.15);
                    }
                }

                /* 暂停/继续按钮 - 鲜亮渐变风格 */
                &.pause-resume-btn {
                    color: #fff;
                    min-width: 160px;

                    &.el-button--warning {
                        background: linear-gradient(135deg, #ffba00, #ff9c00);
                        box-shadow: 0 8px 20px rgba(255, 156, 0, 0.3);

                        &:hover {
                            box-shadow: 0 12px 28px rgba(255, 156, 0, 0.4);
                        }
                    }

                    &.el-button--success {
                        background: linear-gradient(135deg, #67c23a, #4caf50);
                        box-shadow: 0 8px 20px rgba(103, 194, 58, 0.3);

                        &:hover {
                            box-shadow: 0 12px 28px rgba(103, 194, 58, 0.4);
                        }
                    }
                }

                /* 完成按钮 - 科技蓝渐变风格 */
                &.finish-btn {
                    background: linear-gradient(135deg, #2196f3, #1976d2);
                    color: #fff;
                    min-width: 140px;
                    box-shadow: 0 8px 20px rgba(33, 150, 243, 0.3);

                    &:hover {
                        background: linear-gradient(135deg, #42a5f5, #2196f3);
                        box-shadow: 0 12px 28px rgba(33, 150, 243, 0.4);
                    }
                }
            }
        }
    }

    .action-area {
        display: flex;
        gap: 24px;
        width: 100%;
        align-items: stretch;
        justify-content: center;

        .upload-dropzone {
            min-width: 0;

            .upload-dragger {
                width: 100%;
                height: 100%;
                min-height: 200px;

                ::v-deep .el-upload-dragger {
                    width: 140px;       // 固定可见虚线框宽度
                    min-width: 140px;
                    max-width: 140px;
                    height: 130px;
                    border: 2px dashed rgba(79, 140, 245, 0.3);
                    border-radius: 16px;
                    background: rgba(79, 140, 245, 0.02);
                    transition: all 0.3s ease;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    cursor: pointer;
                    position: relative;
                    overflow: hidden;

                    &::before {
                        content: '';
                        position: absolute;
                        top: 0;
                        left: -100%;
                        width: 100%;
                        height: 100%;
                        background: linear-gradient(90deg, transparent, rgba(79, 140, 245, 0.1), transparent);
                        transition: left 0.5s;
                    }

                    &:hover {
                        border-color: rgba(79, 140, 245, 0.5);
                        background: rgba(79, 140, 245, 0.05);
                        transform: translateY(-2px);
                        box-shadow: 0 8px 24px rgba(79, 140, 245, 0.15);

                        &::before {
                            left: 100%;
                        }
                    }

                    &.is-dragover {
                        border-color: #4f8cf5;
                        background: rgba(79, 140, 245, 0.1);
                        box-shadow: 0 0 0 4px rgba(79, 140, 245, 0.1);
                        transform: scale(1.02);
                    }
                }

                .dropzone-content {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    gap: 10px;
                    padding: 12px;
                    text-align: center;

                    // 文件信息显示时减小间距
                    &.has-file {
                        gap: 6px;
                        padding: 10px;
                    }

                    .dropzone-icon {
                        width: 42px;
                        height: 42px;
                        border-radius: 50%;
                        background: linear-gradient(135deg, rgba(79, 140, 245, 0.1), rgba(125, 174, 250, 0.1));
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        transition: all 0.3s ease;
                        position: relative;

                        &::before {
                            content: '';
                            position: absolute;
                            inset: -3px;
                            border-radius: 50%;
                            border: 2px solid rgba(79, 140, 245, 0.2);
                            animation: ripple 2s ease-out infinite;
                        }

                        i {
                            font-size: 21px;
                            color: #4f8cf5;
                            position: relative;
                            z-index: 1;
                            transition: all 0.3s ease;
                        }

                        @keyframes ripple {
                            0% {
                                transform: scale(0.8);
                                opacity: 1;
                            }
                            100% {
                                transform: scale(1.5);
                                opacity: 0;
                            }
                        }
                    }

                    .dropzone-text {
                        .main-text {
                            font-size: 10px;
                            font-weight: 600;
                            color: #1f2d3d;
                            margin: 0 0 5px;
                        }

                        .sub-text {
                            font-size: 9px;
                            color: #5c6c80;
                            margin: 0 0 3px;
                        }

                        .hint-text {
                            font-size: 8px;
                            color: #909399;
                            margin: 5px 0 0;
                        }
                    }

                    // 文件信息样式
                    .file-icon {
                        background: linear-gradient(135deg, rgba(79, 140, 245, 0.15), rgba(125, 174, 250, 0.15));
                        
                        i {
                            color: #4f8cf5;
                            font-size: 24px;
                        }
                    }

                    .file-info {
                        .main-text {
                            font-size: 11px;
                            font-weight: 600;
                            color: #1f2d3d;
                            margin: 0 0 3px;
                            word-break: break-all;
                            max-width: 200px;
                            overflow: hidden;
                            text-overflow: ellipsis;
                            white-space: nowrap;
                        }

                        .sub-text {
                            font-size: 9px;
                            color: #4f8cf5;
                            margin: 0 0 2px;
                            font-weight: 500;
                        }

                        .hint-text {
                            font-size: 8px;
                            color: #909399;
                            margin: 2px 0 0;
                        }
                    }

                    .file-actions {
                        
                        .el-button {
                            color: #909399;
                            font-size: 9px;
                            padding: 4px 8px;
                            
                            &:hover {
                                color: #4f8cf5;
                            }
                        }
                    }
                }
            }
        }

        .action-buttons {
            display: flex;
            flex-direction: column;
            gap: 16px;
            width: 200px;
            flex-shrink: 0;

            .action-button-wrapper {
                width: 100%;
                display: block;
            }

            .action-btn {
                width: 100%;
                min-width: 200px;
                padding: 16px 24px;
                font-size: 16px;
                font-weight: 600;
                color: #3090ff;
                background: rgba(125, 186, 255, 0.6);
                backdrop-filter: blur(12px);
                border: 1px solid rgba(64, 158, 255, 0.25);
                border-radius: 16px;
                box-shadow: 0 8px 24px rgba(64, 158, 255, 0.1);
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 10px;
                outline: none;
                box-sizing: border-box;

                i {
                    font-size: 22px;
                    filter: drop-shadow(0 2px 4px rgba(64, 158, 255, 0.1));
                }

                &:hover:not(:disabled) {
                    transform: translateY(-3px);
                    background: rgba(236, 245, 255, 0.7);
                    box-shadow: 0 12px 32px rgba(64, 158, 255, 0.2);
                    border-color: rgba(64, 158, 255, 0.4);
                }

                &:active:not(:disabled) {
                    transform: translateY(-1px);
                    background: rgba(217, 236, 255, 0.8);
                    box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
                }

                &:disabled {
                    opacity: 0.6;
                    cursor: not-allowed;
                    filter: grayscale(0.5);
                    background: rgba(245, 247, 250, 0.4);
                    border-color: rgba(228, 231, 237, 0.4);
                }
                &.secondary {
                    background: #ffffff;
                    color: #4f8cf5;
                    border: 1px solid rgba(79, 140, 245, 0.3);
                    box-shadow: 0 4px 12px rgba(79, 140, 245, 0.15);

                    i {
                        color: #4f8cf5;
                    }

                    &:hover:not(:disabled) {
                        background: #f5f7ff;
                        box-shadow: 0 6px 16px rgba(79, 140, 245, 0.25);
                    }
                }
            }            
        }
    }

    // 现代模式结果卡片
    .result-card-modern {
        width: 100%;
        max-width: 400px;
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(12px);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.6);
        display: flex;
        justify-content: center;
        flex-direction: column;
        gap: 20px;
        margin-top: 20px;

        .player-row {
            display: flex;
            align-items: center;
            gap: 16px;

            .play-btn {
                width: 40px;
                height: 40px;
                border-radius: 50%;
                background: linear-gradient(135deg, #4f8cf5, #2563eb);
                display: flex;
                align-items: center;
                justify-content: center;
                color: #fff;
                font-size: 18px;
                cursor: pointer;
                box-shadow: 0 4px 12px rgba(79, 140, 245, 0.3);
                transition: transform 0.2s ease;

                &:active {
                    transform: scale(0.95);
                }
            }

            .progress-bar {
                flex: 1;
                display: flex;
                flex-direction: column;
                justify-content: center; /* 垂直居中 */
                position: relative; /* 为绝对定位时间做准备 */
                height: 40px; /* 与播放按钮等高 */

                ::v-deep .el-slider__runway {
                    margin: 0;
                    background-color: rgba(0, 0, 0, 0.05);
                }

                .time-hint {
                    position: absolute;
                    bottom: -16px; /* 移到下方 */
                    left: 0;
                    right: 0;
                    display: flex;
                    justify-content: space-between;
                    font-size: 12px;
                    color: #909399;
                    font-variant-numeric: tabular-nums;
                }
            }
        }

        .action-row {
            display: flex;
            gap: 12px;

            .action-item {
                flex: 1;
                height: 44px;
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
                font-size: 14px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.2s ease;

                &.secondary {
                    background: #f5f7fa;
                    color: #606266;
                    &:hover { background: #eef1f6; }
                }

                &.primary {
                    background: rgba(79, 140, 245, 0.1);
                    color: #4f8cf5;
                    &:hover { background: rgba(79, 140, 245, 0.15); }
                }
            }
        }
    }

    // 复古模式结果卡片
    .result-card-retro {
        margin-top: 20px;
        width: 340px;
        
        .paper-tape {
            background: #fffcf5;
            padding: 20px;
            border-radius: 4px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            position: relative;
            border: 1px solid #e0dac5;
            /* transform: rotate(-1deg);  去除倾斜 */

            &::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 4px;
                background: repeating-linear-gradient(
                    90deg,
                    #e0dac5 0,
                    #e0dac5 8px,
                    transparent 8px,
                    transparent 16px
                );
            }

            .note-content {
                display: flex;
                flex-direction: column;
                gap: 16px;

                .retro-player {
                    display: flex;
                    align-items: center;
                    gap: 12px;
                    padding: 12px;
                    background: #f5f2e6;
                    border-radius: 4px;
                    border: 1px dashed #d4cfb8;

                    .retro-play-btn {
                        width: 36px;
                        height: 36px;
                        background: #4a4a4a;
                        border-radius: 2px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        color: #fff;
                        cursor: pointer;
                        box-shadow: 2px 2px 0 rgba(0,0,0,0.2);

                        &:active {
                            transform: translate(1px, 1px);
                            box-shadow: 1px 1px 0 rgba(0,0,0,0.2);
                        }
                    }

                    .retro-info-col {
                        flex: 1;
                        display: flex;
                        flex-direction: column;
                        justify-content: center; /* 垂直居中 */
                        position: relative; /* 为绝对定位时间做准备 */
                        height: 36px; /* 与按钮高度一致 */

                        .retro-progress {
                            width: 100%;
                            height: 8px;
                            background: #e0dac5;
                            border-radius: 4px;
                            overflow: hidden;
                            position: relative;
                            cursor: pointer;

                            .progress-fill {
                                height: 100%;
                                background: #ff6b6b;
                                width: 0;
                                transition: width 0.1s linear;
                            }
                        }

                        .retro-time-text {
                            position: absolute;
                            bottom: -8px; /* 移到下方 */
                            right: 0;
                            font-family: 'Courier New', monospace;
                            font-size: 10px; /* 稍微调小一点 */
                            color: #8d8675;
                            font-weight: bold;
                            opacity: 0.8;
                        }
                    }
                }

                .retro-actions {
                    display: flex;
                    justify-content: space-between;
                    gap: 12px;

                    .retro-btn {
                        flex: 1;
                        padding: 8px;
                        border: 2px solid #4a4a4a;
                        background: transparent;
                        font-family: 'Courier New', monospace;
                        font-weight: bold;
                        font-size: 14px;
                        color: #4a4a4a;
                        cursor: pointer;
                        transition: all 0.2s;

                        &:hover {
                            background: #4a4a4a;
                            color: #fff;
                        }

                        &.primary {
                            border-color: #1976d2;
                            color: #1976d2;

                            &:hover {
                                background: #1976d2;
                                color: #fff;
                            }
                        }
                    }
                }
            }
        }
    }
}
</style>

