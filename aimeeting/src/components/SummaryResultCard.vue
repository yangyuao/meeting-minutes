<template>
    <transition name="slide-up">
        <div
            v-if="summaryText"
            class="result-card"
            :class="{ 'dragging': isDragging }"
            :style="{
            left: cardPosition.x + 'px',
            top: cardPosition.y + 'px',
            right: 'auto',
            bottom: 'auto'
        }"
            @mousedown="startDrag"
        >
            <div class="result-card-header">
                <div class="result-title">
                    <div class="title-icon-wrapper">
                        <i class="el-icon-document"></i>
                    </div>
                    <div>
                        <h3>会议纪要</h3>
                        <p>生成完成</p>
                    </div>
                </div>
                <div class="result-actions">
                    <el-button size="small" icon="el-icon-document-copy" @click="copySummary" circle
                        title="复制"></el-button>
                    <el-button size="small" icon="el-icon-download" @click="exportSummary" circle
                        title="导出"></el-button>
                    <el-button size="small" icon="el-icon-document" @click="exportToWord" circle
                        title="导出为Word" :loading="exportingWord"></el-button>
                    <el-button size="small" icon="el-icon-close" @click="closeResult" circle
                        title="关闭"></el-button>
                </div>
            </div>
            <div class="result-card-content">
                <div 
                    v-if="summaryText" 
                    v-html="renderedMarkdown" 
                    :key="summaryText.length"
                    class="result-text" 
                />
            </div>
        </div>
    </transition>
</template>

<script>
import MarkdownIt from "markdown-it";
import multimdTable from "markdown-it-multimd-table";
import mk from "markdown-it-katex";
import { API_GENERATE_DOCX } from '@/utils/env'

export default {
    name: 'SummaryResultCard',
    props: {
        summaryText: {
            type: String,
            default: ''
        }
    },
    data() {
        return {
            isDragging: false,
            // 拖拽开始时卡片的位置
            dragStartPosition: { x: 0, y: 0 },
            // 拖拽开始时鼠标的位置
            dragStartMouse: { x: 0, y: 0 },
            // 当前卡片位置（用于绑定到 style）
            cardPosition: { x: 0, y: 0 },
            // markdown-it 实例
            md: null,
            // 导出Word加载状态
            exportingWord: false
        }
    },
    computed: {
        // 显示文本：去掉 <think> 和 <think> 标签及其内容
        displayText() {
            if (!this.summaryText) return ''
            let text = this.summaryText
            // 移除 <think>...</think> 标签及其内容
            text = text.replace(/<think>[\s\S]*?<\/think>/g, '')
            // 移除 <think>...</think> 标签及其内容
            text = text.replace(/<think>[\s\S]*?<\/redacted_reasoning>/g, '')
            return text
        },
        // 渲染后的 markdown HTML
        renderedMarkdown() {
            if (!this.displayText) {
                // 如果没有 displayText，但 summaryText 存在，直接返回 summaryText（处理过滤后为空的情况）
                if (this.summaryText) {
                    return this.summaryText.replace(/\n/g, '<br>')
                }
                return ''
            }
            // 如果 md 还没初始化，先显示纯文本（换行转换为 <br>）
            if (!this.md) {
                return this.displayText.replace(/\n/g, '<br>')
            }
            try {
                const rendered = this.md.render(this.displayText)
                // 确保返回的内容不为空
                return rendered || this.displayText.replace(/\n/g, '<br>')
            } catch (error) {
                console.error('Markdown 渲染错误:', error)
                // 如果渲染失败，返回纯文本
                return this.displayText.replace(/\n/g, '<br>')
            }
        },
        // 复制文本：markdown 格式，去掉 think 内容
        copyText() {
            if (!this.summaryText) return ''
            let text = this.summaryText
            // 移除 <think>...</think> 标签及其内容
            text = text.replace(/<think>[\s\S]*?<\/think>/g, '')
            // 移除 <think>...</think> 标签及其内容
            text = text.replace(/<think>[\s\S]*?<\/redacted_reasoning>/g, '')
            return text
        }
    },
    mounted() {
        // 初始化 markdown-it
        this.md = new MarkdownIt({
            html: true,
            xhtmlOut: true,
            linkify: true,
            typographer: true,
            breaks: true,
        }).use(multimdTable).use(mk, {
            delimiters: [
                { left: "$$", right: "$$", display: true },
                { left: "$", right: "$", display: false },
                { left: "\\[", right: "\\]", display: true },
                { left: "\\(", right: "\\)", display: false },
            ],
            throwOnError: false,
            errorColor: "#cc0000",
            strict: false,
        })
        
        // 初始时定位一次（此时通常还没有内容）
        this.initCardPosition()
        document.addEventListener('mousemove', this.onDrag)
        document.addEventListener('mouseup', this.stopDrag)
    },
    beforeDestroy() {
        document.removeEventListener('mousemove', this.onDrag)
        document.removeEventListener('mouseup', this.stopDrag)
    },
    watch: {
        // 注意：调用 generateSummary 时，父组件会以“流式”的方式不断更新 summaryText。
        // 之前每次 summaryText 变化都会重新调用 initCardPosition，
        // 导致拖拽过程中位置被反复重置，看起来“拖动后又弹回原位”。
        //
        // 这里改为：只有从「无内容 -> 有内容」（第一次出现卡片）时才重置位置，
        // 后续流式追加内容不再动位置信息，拖拽就不会被打断了。
        summaryText(newVal, oldVal) {
            if (newVal && !oldVal) {
                this.$nextTick(() => {
                    this.initCardPosition()
                })
            }
        }
    },
    methods: {
        closeResult() {
            this.$emit('close')
        },

        initCardPosition() {
            this.$nextTick(() => {
                const cardWidth = 600
                const cardHeight = Math.min(window.innerHeight * 0.8, 600)

                const centerX = (window.innerWidth - cardWidth) / 2
                const centerY = (window.innerHeight - cardHeight) / 2

                this.cardPosition.x = Math.max(20, Math.min(centerX, window.innerWidth - cardWidth - 20))
                this.cardPosition.y = Math.max(20, Math.min(centerY, window.innerHeight - cardHeight - 20))
            })
        },

        startDrag(event) {
            if (event.target.closest('.el-button') || event.target.closest('.result-actions')) {
                return
            }

            this.isDragging = true

            // 记录拖拽开始时卡片和鼠标的位置
            this.dragStartPosition = { ...this.cardPosition }
            this.dragStartMouse = { x: event.clientX, y: event.clientY }

            event.preventDefault()
            event.stopPropagation()
        },

        onDrag(event) {
            if (!this.isDragging) return

            const deltaX = event.clientX - this.dragStartMouse.x
            const deltaY = event.clientY - this.dragStartMouse.y

            this.cardPosition.x = this.dragStartPosition.x + deltaX
            this.cardPosition.y = this.dragStartPosition.y + deltaY

            event.preventDefault()
        },

        stopDrag() {
            if (this.isDragging) {
                this.isDragging = false
            }
        },

        copySummary() {
            if (!this.copyText) return

            const textarea = document.createElement('textarea')
            textarea.value = this.copyText
            document.body.appendChild(textarea)
            textarea.select()
            try {
                document.execCommand('copy')
                this.$message.success('已复制到剪贴板')
            } catch (error) {
                this.$message.error('复制失败')
            }
            document.body.removeChild(textarea)
        },

        exportSummary() {
            if (!this.copyText) return

            const blob = new Blob([this.copyText], { type: 'text/plain;charset=utf-8' })
            const url = URL.createObjectURL(blob)
            const link = document.createElement('a')
            link.href = url
            link.download = `会议纪要_${new Date().toISOString().slice(0, 10)}.txt`
            document.body.appendChild(link)
            link.click()
            document.body.removeChild(link)
            URL.revokeObjectURL(url)

            this.$message.success('导出成功')
        },

        async exportToWord() {
            if (!this.copyText) {
                this.$message.warning('没有可导出的内容')
                return
            }

            this.exportingWord = true

            try {
                // 调用生成Word文档接口
                const response = await fetch(API_GENERATE_DOCX, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        markdown: this.copyText
                    }),
                    mode: 'cors'
                })

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`)
                }

                // 获取返回的Word文件blob
                const blob = await response.blob()
                
                // 创建下载链接
                const url = URL.createObjectURL(blob)
                const link = document.createElement('a')
                link.href = url
                link.download = `会议纪要_${new Date().toISOString().slice(0, 10)}.docx`
                document.body.appendChild(link)
                link.click()
                document.body.removeChild(link)
                URL.revokeObjectURL(url)

                this.$message.success('Word文档导出成功')
            } catch (error) {
                console.error('导出Word文档失败:', error)
                this.$message.error('导出Word文档失败，请重试')
            } finally {
                this.exportingWord = false
            }
        }
    }
}
</script>

<style scoped lang="scss">
.result-card {
    position: fixed;
    width: 600px;
    max-height: 80vh;
    background: rgba(255, 255, 255, 0.98);
    backdrop-filter: blur(20px);
    border-radius: 20px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    z-index: 1000;
    animation: slideUpIn 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    user-select: none;

    &.dragging {
        cursor: move;
        user-select: none;
    }

    @keyframes slideUpIn {
        from {
            opacity: 0;
            transform: translateY(100px) scale(0.9);
        }
        to {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
    }

    .result-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 20px 24px;
        background: linear-gradient(135deg, rgba(191, 219, 254, 0.1), rgba(118, 75, 162, 0.1));
        border-bottom: 1px solid rgba(0, 0, 0, 0.06);

        &.dragging {
            cursor: move;
            user-select: none;
        }

        .result-title {
            display: flex;
            align-items: center;
            gap: 16px;
            user-select: none;
            flex: 1;
            cursor: move;

            .title-icon-wrapper {
                width: 48px;
                height: 48px;
                border-radius: 12px;
                background: linear-gradient(135deg, #60a5fa, #3b82f6);
                display: flex;
                align-items: center;
                justify-content: center;
                color: #fff;
                font-size: 24px;
                box-shadow: 0 4px 12px rgba(191, 219, 254, 0.3);
                animation: pulse 2s ease-in-out infinite;

                @keyframes pulse {
                    0%, 100% {
                        transform: scale(1);
                        box-shadow: 0 4px 12px rgba(191, 219, 254, 0.3);
                    }
                    50% {
                        transform: scale(1.05);
                        box-shadow: 0 6px 16px rgba(191, 219, 254, 0.4);
                    }
                }

                i {
                    animation: float 3s ease-in-out infinite;

                    @keyframes float {
                        0%, 100% {
                            transform: translateY(0);
                        }
                        50% {
                            transform: translateY(-5px);
                        }
                    }
                }
            }

            h3 {
                font-size: 20px;
                font-weight: 600;
                margin: 0 0 4px;
                color: #1f2d3d;
            }

            p {
                font-size: 12px;
                color: #5c6c80;
                margin: 0;
            }
        }

        .result-actions {
            display: flex;
            gap: 8px;
        }
    }

    .result-card-content {
        flex: 1;
        padding: 24px;
        overflow-y: auto;
        max-height: calc(80vh - 100px);

        &::-webkit-scrollbar {
            width: 6px;
        }

        &::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 3px;
        }

        &::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #60a5fa, #3b82f6);
            border-radius: 3px;

            &:hover {
                background: linear-gradient(135deg, #3b82f6, #60a5fa);
            }
        }

        .result-text {
            font-size: 14px;
            line-height: 1.8;
            color: #1f2d3d;
            word-break: normal;
            overflow-wrap: break-word;
            white-space: normal;

            h1 {
                font-size: 24px;
                font-weight: 700;
                margin: 0 0 20px;
                color: #1f2d3d;
                background: linear-gradient(135deg, #60a5fa, #3b82f6);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }

            h2 {
                font-size: 18px;
                font-weight: 600;
                margin: 24px 0 12px;
                color: #1f2d3d;
                padding-bottom: 8px;
                border-bottom: 2px solid rgba(191, 219, 254, 0.2);
            }

            h3 {
                font-size: 16px;
                font-weight: 600;
                margin: 20px 0 10px;
                color: #1f2d3d;
            }

            ul {
                margin: 12px 0;
                padding-left: 24px;
                list-style: none;

                li {
                    position: relative;
                    padding-left: 20px;
                    margin-bottom: 8px;
                    color: #5c6c80;

                    &::before {
                        content: '•';
                        position: absolute;
                        left: 0;
                        color: #60a5fa;
                        font-weight: bold;
                        font-size: 18px;
                    }
                }
            }

            p {
                margin: 12px 0;
                color: #5c6c80;
            }
        }
    }
}

// 过渡动画
.slide-up-enter-active,
.slide-up-leave-active {
    transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-up-enter,
.slide-up-leave-to {
    opacity: 0;
    transform: translateY(100px) scale(0.9);
}

// 响应式设计
@media (max-width: 1400px) {
    .result-card {
        width: 500px;
    }
}

@media (max-width: 1200px) {
    .result-card {
        width: 450px;
        max-height: 70vh;
    }
}

@media (max-width: 768px) {
    .result-card {
        width: calc(100vw - 40px);
        right: 20px;
        left: 20px;
        bottom: 20px;
        max-height: 60vh;
    }
}
</style>

