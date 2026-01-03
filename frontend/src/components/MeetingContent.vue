<template>
    <div class="meeting-content">
        <div class="main-layout">
            <RecordingPanel
                :upload-action="uploadAction"
                :enable-realtime-transcription="true"
                @recording-complete="handleRecordingComplete"
                @file-uploaded="handleFileUploaded"
                @realtime-transcription="handleRealtimeTranscription"
            />

            <div class="divider-line"></div>

            <TranscriptionPanel
                :transcription-text="transcriptionText"
                :transcribing="transcribing"
                @update:transcription-text="transcriptionText = $event"
                @summary-generated="handleSummaryGenerated"
            />

            <SummaryResultCard
                :summary-text="summaryText"
                @close="handleCloseResult"
            />
        </div>
    </div>
</template>

<script>
import RecordingPanel from './RecordingPanel.vue'
import TranscriptionPanel from './TranscriptionPanel.vue'
import SummaryResultCard from './SummaryResultCard.vue'
import { API_UPLOAD_AUDIO, API_GET_TRANSCRIPT } from '@/utils/env'

export default {
    name: 'MeetingContent',
    components: {
        RecordingPanel,
        TranscriptionPanel,
        SummaryResultCard
    },
    data() {
        return {
            uploadAction: API_UPLOAD_AUDIO,
            transcriptionText: '',
            transcribing: false,
            summaryText: ''
        }
    },
    methods: {
        // 录音完成（左侧面板 emit）
        async handleRecordingComplete(audioBlob) {
            await this.transcribeAudio(audioBlob)
        },
        // 上传文件完成（左侧面板 emit）
        async handleFileUploaded(audioBlob) {
            await this.transcribeAudio(audioBlob)
        },
        // 实时转写文本更新（WebSocket 实时识别）
        handleRealtimeTranscription(text) {
            this.transcriptionText = text
        },
        // 调用后端接口，将音频文件转为文字（迁移自 old App.vue 的 getTranscript 逻辑）
        async transcribeAudio(audioSource) {
            if (!audioSource) return

            const fileName = audioSource?.name || `recording_${Date.now()}.wav`
            const mimeType = audioSource?.type || 'audio/wav'
            const uploadFile = audioSource instanceof File
                ? audioSource
                : new File([audioSource], fileName, { type: mimeType })

            this.transcribing = true
            this.transcriptionText = ''

            const formData = new FormData()
            formData.append('file', uploadFile, fileName)
            formData.append('username', 'undown')
            try {
                this.transcriptionText = '处理中，请稍候...'

                const response = await fetch(API_GET_TRANSCRIPT, {
                    method: 'POST',
                    body: formData
                })

                // 解析 JSON 响应数据（沿用 old App.vue 里的约定）
                const data = await response.json()

                if (data && data.transcript) {
                    this.transcriptionText = data.transcript
                } else if (data && data.error) {
                    this.transcriptionText = `服务器出错: ${data.error}`
                } else {
                    this.transcriptionText = '未知错误'
                }

                this.$message && this.$message.success('转写完成')
            } catch (error) {
                console.error('语音转文字失败:', error)
                this.transcriptionText = '请求失败，请查看控制台错误信息。'
                this.$message && this.$message.error('语音转文字失败，请重试')
            } finally {
                this.transcribing = false
            }
        },
        // 右侧生成完成后的纪要文本
        handleSummaryGenerated(summaryText) {
            this.summaryText = summaryText
        },
        handleCloseResult() {
            this.summaryText = ''
        }
    }
}
</script>

<style scoped lang="scss">
.meeting-content {
    width: 100%;
    height: 100%;
    position: relative;

    .main-layout {
        height: 100%;
        display: grid;
        grid-template-columns: 1fr 1px 1fr;
        min-height: 0;
        position: relative;
        z-index: 1;
        padding: 20px;
        gap: 0;
        overflow: hidden;

        .divider-line {
            width: 1px;
            background: linear-gradient(180deg, transparent, rgba(37, 99, 235, 0.2), transparent);
            margin: 20px 0;
        }
    }
}

@keyframes fadeIn {
    from {
        opacity: 0;
    }
    to {
        opacity: 1;
    }
}
</style>

