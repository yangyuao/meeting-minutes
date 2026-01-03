<template>
    <div class="transcription-panel">
        <!-- 转写区域 -->
        <div class="transcription-section">
            <div class="panel-header">
                <div class="header-icon">
                    <i class="el-icon-edit"></i>
                </div>
                <div class="header-text">
                    <h2>
                        转写文本
                        <span v-if="transcribing" class="status-badge">
                            <i class="el-icon-loading"></i>
                            <span>转写中...</span>
                        </span>
                    </h2>
                </div>
            </div>

            <div class="panel-content">
                <div class="transcription-textarea-wrapper">
                    <el-input type="textarea" :value="transcriptionText"
                        @input="handleTranscriptionChange"
                        placeholder="转写文本将显示在这里，您可以进行编辑..." :disabled="transcribing"
                        class="transcription-textarea"></el-input>
                </div>

                <!-- 使用教程下载 -->
                <div class="tutorial-download">
                    <span class="label">使用教程：</span>
                    <a :href="tutorialDownloadUrl" download="会议纪要助手使用手册.pptx">
                        <i class="el-icon-document"></i>
                        <span>下载会议纪要使用教程</span>
                    </a>
                </div>
            </div>
        </div>

        <!-- 生成区域 -->
        <div class="summary-section">
            <div class="panel-header">
                <div class="header-icon">
                    <i class="el-icon-magic-stick"></i>
                </div>
                <div class="header-text">
                    <h2>生成会议纪要</h2>
                </div>
            </div>

            <div class="panel-content">
                <!-- 模板切换标签 -->
                <div class="template-tabs">
                    <div 
                        class="tab-item" 
                        :class="{ active: promptType === 'default' }"
                        @click="promptType = 'default'; handlePromptTypeChange()">
                        默认模板
                    </div>
                    <div 
                        class="tab-item" 
                        :class="{ active: promptType === 'custom' }"
                        @click="promptType = 'custom'">
                        自定义
                    </div>
                </div>

                <!-- 提示词输入框 -->
                <div class="prompt-input-wrapper">
                    <!-- 默认模板 -->
                    <div class="prompt-textarea-wrapper">
                        <el-input 
                            v-if="promptType === 'default'"
                            ref="promptTextarea" 
                            type="textarea" 
                            v-model="promptText"
                            placeholder="默认提示词模板..." 
                            class="prompt-textarea default-prompt">
                        </el-input>

                        <!-- 自定义模板 -->
                        <el-input 
                            v-if="promptType === 'custom'"
                            ref="customPromptTextarea" 
                            type="textarea" 
                            v-model="customPrompt"
                            placeholder="请输入自定义提示词..." 
                            class="prompt-textarea">
                        </el-input>
                    </div>
                </div>

                <!-- 生成按钮 -->
                <div class="generate-action">
                    <el-button 
                        type="primary" 
                        size="medium" 
                        icon="el-icon-magic-stick" 
                        @click="generateSummary"
                        :loading="generating" 
                        :disabled="!transcriptionText || (promptType === 'custom' && !customPrompt.trim())" 
                        class="generate-btn">
                        {{ generating ? '生成中...' : '生成会议纪要' }}
                    </el-button>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { API_PROMPT_DEFAULT, API_GENERATE_SUMMARY } from '@/utils/env'

export default {
    name: 'TranscriptionPanel',
    props: {
        transcriptionText: {
            type: String,
            default: ''
        },
        transcribing: {
            type: Boolean,
            default: false
        }
    },
    data() {
        return {
            promptType: 'default',
            promptText: '',
            customPrompt: '',
            // 使用教程下载地址（静态资源）
            tutorialDownloadUrl: 'meeting-minutes-wizard.pptx',
            defaultPrompt: `请根据以下会议录音转写文本，生成结构化的会议纪要。要求包含以下部分：
1. 参会人员：列出所有参会人员
2. 主要议题：总结会议讨论的主要话题
3. 决策事项：记录会议中做出的决策
4. 待办事项：列出需要后续跟进的任务和负责人

转写文本：
{transcription}`,
            generating: false
        }
    },
    mounted() {
        this.promptText = this.defaultPrompt.replace('{transcription}', '')
        // 初始化时获取默认提示词（迁移自 old App.vue 的 useDefaultPrompt）
        this.useDefaultPrompt()
    },
    methods: {
        handleTranscriptionChange(value) {
            // 同步到父组件的 transcriptionText（事件名与父组件监听的 update:transcription-text 对齐）
            this.$emit('update:transcription-text', value)
        },
        async handlePromptTypeChange() {
            if (this.promptType === 'default') {
                await this.useDefaultPrompt()
            }
        },

        resetToDefault() {
            this.promptText = this.defaultPrompt.replace('{transcription}', '')
            this.$message.success('已重置为默认模板')
        },

        // 处理转义字符，将 \nn 和 \n 转换成换行符
        processEscapeCharacters(text) {
            if (!text) return ''
            let result = text
            // 兼容后端返回的转义字符：当出现字面量 \nn 或 \n 时再进行替换
            result = result.replace(/\\nn/g, '\n\n')
            result = result.replace(/\\n/g, '\n')
            console.log('处理转义字符:', result);
            return result
        },

        // 获取默认提示词（迁移自 old App.vue 的 useDefaultPrompt）
        async useDefaultPrompt() {
            try {
                const response = await fetch(API_PROMPT_DEFAULT)
                const data = await response.json()
                if (data && data.prompt) {
                   
                    const processedPrompt = this.processEscapeCharacters(data.prompt)
                    this.defaultPrompt = processedPrompt
                    this.promptText = processedPrompt.replace('{transcription}', '')
                }
            } catch (error) {
                console.error('获取默认提示词失败:', error)
                // 失败时使用本地默认值
            }
        },

        // 处理 <think> 和 <think> 标签
        processRedactedReasoning(text, isStreaming) {
            if (!text) return ''
            
            if (isStreaming) {
                // 流式输出时：将内容缩略成一行
                let result = text
                
                // 处理 <think>...</think> 标签
                result = result.replace(/<think>([\s\S]*?)<\/redacted_reasoning>/g, (match, content) => {
                    const singleLine = content.replace(/\s+/g, ' ').trim()
                    const truncated = singleLine.length > 50 
                        ? singleLine.substring(0, 50) + '...' 
                        : singleLine
                    return `<think>${truncated}</think>`
                })
                
                // 处理 <think>...</think> 标签
                result = result.replace(/<think>([\s\S]*?)<\/redacted_reasoning>/g, (match, content) => {
                    const singleLine = content.replace(/\s+/g, ' ').trim()
                    const truncated = singleLine.length > 50 
                        ? singleLine.substring(0, 50) + '...' 
                        : singleLine
                    return `<think>${truncated}</think>`
                })
                
                return result
            } else {
                // 正式文本时：正常显示（保持原样）
                return text
            }
        },

        // 生成会议纪要（迁移自 old App.vue 的 generateSummary，流式读取）
        async generateSummary() {
            if (!this.transcriptionText) {
                this.$message.warning('请先完成语音转文字')
                return
            }

            this.generating = true

            try {
                // 组装 prompt（迁移自 old App.vue）
                let prompt = ''
                if (this.promptType === 'default') {
                    prompt = this.promptText.trim() || this.defaultPrompt.replace('{transcription}', '')
                } else {
                    prompt = this.customPrompt.trim()
                    if (!prompt) {
                        this.$message.warning('请输入自定义提示词')
                        this.generating = false
                        return
                    }
                }

                // 如果 prompt 中没有占位符，自动追加转写文本
                if (!prompt.includes('{transcription}') && !prompt.includes('转写文本')) {
                    prompt += '\n\n转写文本：\n' + this.transcriptionText
                } else {
                    prompt = prompt.replace('{transcription}', this.transcriptionText)
                }

                const requestData = {
                    transcript: this.transcriptionText,
                    prompt: prompt
                }

                // 调用流式接口（迁移自 old App.vue）
                const response = await fetch(API_GENERATE_SUMMARY, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(requestData),
                    mode: 'cors'
                })

                if (response.ok && response.body) {
                    const reader = response.body.getReader()
                    const decoder = new TextDecoder()
                    let result = ''

                    // 流式读取，实时 emit 给父组件
                    while (true) {
                        const { done, value } = await reader.read()
                        if (done) break
                        const chunk = decoder.decode(value, { stream: true })
                        result += chunk
                        
                        // 处理 <think> 标签：在流式输出时缩略成一行
                        let displayResult = this.processRedactedReasoning(result, true)
                        
                        // 实时发送累积结果，让卡片可以流式展示
                        this.$emit('summary-generated', displayResult)
                    }

                    // 最终结果：正常显示所有内容
                    let finalResult = this.processRedactedReasoning(result, false)
                    this.$emit('summary-generated', finalResult)

                    this.$message.success('会议纪要生成完成')
                } else {
                    const errorText = await response.text().catch(() => '服务器出错，请检查日志')
                    this.$message.error(errorText || '服务器出错，请检查日志')
                    this.$emit('summary-generated', '服务器出错，请检查日志')
                }
            } catch (error) {
                console.error('请求失败:', error)
                this.$message.error('请求失败，请查看控制台错误信息。')
                this.$emit('summary-generated', '请求失败，请查看控制台错误信息。')
            } finally {
                this.generating = false
            }
        }
    }
}
</script>

<style scoped lang="scss">
.transcription-panel {
    height: 100%;
    display: flex;
    flex-direction: column;
    background: rgba(255, 255, 255, 0.98);
    backdrop-filter: blur(20px);
    box-shadow: 0 12px 48px rgba(0, 0, 0, 0.15);
    border-radius: 0 24px 24px 0;
    overflow: hidden;

    .panel-header {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 10px 24px;
        border-bottom: 1px solid rgba(0, 0, 0, 0.06);
        background: linear-gradient(135deg, rgba(79, 140, 245, 0.08), rgba(37, 99, 235, 0.08));

        .header-icon {
            width: 40px;
            height: 40px;
            border-radius: 10px;
            background: linear-gradient(135deg, #4f8cf5, #2563eb);
            display: flex;
            align-items: center;
            justify-content: center;
            color: #fff;
            font-size: 20px;
            box-shadow: 0 4px 12px rgba(191, 219, 254, 0.3);
        }

        .header-text {
            flex: 1;

            h2 {
                font-size: 18px;
                font-weight: 600;
                margin: 0 0 2px;
                color: #1f2d3d;
                display: flex;
                align-items: center;
                gap: 8px;

                .status-badge {
                    display: inline-flex;
                    align-items: center;
                    gap: 6px;
                    padding: 4px 12px;
                    background: rgba(191, 219, 254, 0.1);
                    border-radius: 12px;
                    color: #4f8cf5;
                    font-size: 12px;
                    font-weight: normal;
                    margin-left: 8px;

                    i {
                        animation: rotate 1s linear infinite;
                    }

                    @keyframes rotate {
                        from {
                            transform: rotate(0deg);
                        }
                        to {
                            transform: rotate(360deg);
                        }
                    }
                }
            }

            p {
                font-size: 12px;
                color: #5c6c80;
                margin: 0;
            }
        }
    }

    .panel-content {
        flex: 1;
        padding: 10px 24px;
        overflow: hidden;
        min-height: 0;

        &::-webkit-scrollbar {
            width: 6px;
        }

        &::-webkit-scrollbar-track {
            background: rgba(0, 0, 0, 0.05);
            border-radius: 3px;
        }

        &::-webkit-scrollbar-thumb {
            background: rgba(191, 219, 254, 0.3);
            border-radius: 3px;

            &:hover {
                background: rgba(191, 219, 254, 0.5);
            }
        }
    }

        .transcription-section {
            height: 55%;
            display: flex;
            flex-direction: column;
            border-bottom: 1px solid rgba(0, 0, 0, 0.06);

            .panel-content {
                display: flex;
                flex-direction: column;
                min-height: 0;
            }

        .transcription-textarea-wrapper {
            flex: 1;
            display: flex;
            flex-direction: column;
            min-height: 0;
        }

        .transcription-textarea {
            flex: 1;
            display: flex;
            flex-direction: column;
            min-height: 0;

            ::v-deep .el-textarea {
                flex: 1;
                display: flex;
                flex-direction: column;
                min-height: 0;
            }

            ::v-deep .el-textarea__inner {
                flex: 1;
                font-size: 14px;
                line-height: 1.8;
                border: 1px solid #e4e7ed;
                border-radius: 16px;
                background: #fafbfc;
                resize: none;
                min-height: 0;

                &:focus {
                    border-color: #4f8cf5;
                    background: #fff;
                }
            }
        }

        // 使用教程下载
        .tutorial-download {
            flex-shrink: 0;
            margin-top: 8px;
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 12px;
            color: #909399;

            .label {
                font-weight: 500;
            }

            a {
                display: inline-flex;
                align-items: center;
                gap: 4px;
                color: #4f8cf5;
                text-decoration: none;

                i {
                    font-size: 14px;
                }

                &:hover {
                    text-decoration: underline;
                }
            }
        }
    }

        .summary-section {
            display: flex;
            flex-direction: column;
            flex: 1;
            min-height: 0;

            .panel-content {
                display: flex;
                flex-direction: column;
                gap: 12px;
                padding-top: 12px;
            }

            // 模板切换标签
            .template-tabs {
                display: flex;
                gap: 8px;
                padding: 0 4px;

                .tab-item {
                    flex: 1;
                    padding: 8px 16px;
                    text-align: center;
                    font-size: 13px;
                    color: #606266;
                    background: #f5f7fa;
                    border-radius: 8px;
                    cursor: pointer;
                    transition: all 0.2s ease;
                    border: 1px solid transparent;

                    &:hover {
                        color: #4f8cf5;
                        background: rgba(79, 140, 245, 0.08);
                    }

                    &.active {
                        color: #4f8cf5;
                        background: rgba(79, 140, 245, 0.1);
                        border-color: rgba(79, 140, 245, 0.2);
                        font-weight: 500;
                    }
                }
            }

            // 提示词输入框
            .prompt-input-wrapper {
                flex: 1;
                display: flex;
                flex-direction: column;
                min-height: 0;

                .prompt-textarea-wrapper {
                    flex: 1;
                    display: flex;
                    flex-direction: column;
                    min-height: 0;
                }

                .prompt-textarea {
                    flex: 1;
                    display: flex;
                    flex-direction: column;
                    min-height: 0;

                    ::v-deep .el-textarea {
                        flex: 1;
                        display: flex;
                        flex-direction: column;
                        min-height: 0;
                    }

                    ::v-deep .el-textarea__inner {
                        flex: 1;
                        font-size: 13px;
                        line-height: 1.6;
                        border: 1px solid #e4e7ed;
                        border-radius: 8px;
                        background: #fff;
                        resize: none;
                        transition: all 0.2s ease;
                        min-height: 0;

                        &:focus {
                            border-color: #4f8cf5;
                            box-shadow: 0 0 0 2px rgba(79, 140, 245, 0.1);
                        }
                    }

                    // 默认模板样式（只读效果）
                    &.default-prompt {
                        ::v-deep .el-textarea__inner {
                            background: #f5f7fa;
                            cursor: default;
                            color: #606266;
                        }
                    }
                }
            }

            // 生成按钮
            .generate-action {
                margin-top: 4px;

                .generate-btn {
                    width: 100%;
                    border-radius: 8px;
                    font-weight: 500;
                    transition: all 0.2s ease;

                    &:hover:not(:disabled) {
                        transform: translateY(-1px);
                    }

                    &:active:not(:disabled) {
                        transform: translateY(0);
                    }
                }
            }
        }
}
</style>

