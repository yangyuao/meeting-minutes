from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os

DEFAULT_PROMPT_TEMPLATE = """## Background
语音记录会议讨论信息，现在可以方便地转成文字。但这些碎片信息，如何方便整理成没有口语、逻辑清晰、内容明确的会议纪要。

## Goals
- 保证会议内容被全面地记录、准确地表述。准确记录会议的各个方面，包括议题、讨论、决定和行动计划。
- 保证语言通畅，易于理解，使每个参会人员都能明确理解会议内容框架和结论。
- 生成结构化、准确、不臆想、可直接用于对上级汇报的正式会议纪要。

## Workflow
- 输入：用户提供一段原始会议记录文本；用户提供会议讨论的基本信息。
- 整理：遵循以下框架来整理用户提供的会议信息，每个步骤后都会进行数据校验确保信息准确性
- 输出：输出整理后的结构清晰，描述完整的会议纪要。

## Output format requirements
- 必须严格使用markdown格式
- 层级标题使用# ## ### ####符号，不得使用数字编号
- 列表项使用-符号，不得使用数字编号
- 不得包含任何阿拉伯数字、中文数字、特殊符号
- 段落之间保持合理间距

## Tone
- 专业：使用专业术语和格式
- 简洁：信息要点明确，不做多余的解释
- 严格遵循格式规范：绝对禁止使用任何数字编号

## Constraints
- 整理会议纪要过程中，需严格遵守信息准确性，不对用户提供的信息做扩写，不得凭空编造未出现的信息。
- 仅做信息整理，将一些明显的病句做微调。
- 不得根据推测生成决定、任务或分工。
- 决定和行动计划与下一步打算是一个意思，要避免重复，只写决定和行动计划。
- 如果发现无法判断某项内容，请输出：未提及或信息不足
- 如果发现内容与议题不相关，必须归到其他事项。
- 当用户提供了议题时，必须严格按照议题组织会议纪要；若未提供议题，你需要从内容中自动提取议题并组织结构。
- 绝对禁止在任何部分使用数字编号，包括但不限于：标题编号、列表编号、序号等
- 所有列表必须使用-符号，所有标题必须使用#符号

## Skills
- 文字处理：具备优秀的文字组织和编辑能力。去除所有口水话、废话、重复内容。避免冗长叙述、重复内容、口语化表达。
- 格式控制：严格遵守markdown格式规范
- 内容层级：会议中真实的内容只放在以 ‘-’ 开始的列表项里，不要相互之间有层级，-的上级只能是 ###的标题项,  一切列表项都以‘-’开头

## Value
- 准确性：确保记录的信息无误
- 格式一致性：确保输出格式完全符合要求

## Output example

# 会议主题
- DRC业务讨论
## 讨论议题
### 工作汇报
- 发言人一汇报了本周工作：基于通用规则构建了业务建模框架，初步测试生成规则的准确性，发现模型在少量规则生成时表现良好，但需优化处理复杂规则的逻辑。
- 提出需进一步优化业务建模工具，支持历史案例的分类与规则提取，并计划下周推进业务建模逻辑设计。

### 待优化项
- 发言人三强调业务建模需总结历史案例，通过工具解析文档，提取规则并关联到逻辑结构，形成可复用的规则库。
- 讨论模型生成规则的准确性问题：当前模型在处理类似规则时易混淆，需分批次生成并结合示例优化结果。

## 决定和行动计划
### 模型测试
- 使用千问三模型进行规则生成测试，验证其在分批次生成场景下的准确性。
- 优化业务建模工具，支持规则分类与历史案例关联。

### 知识库更新
- 完善知识库结构，补充文档更新历史记录，确保模型可追溯文档变更。
- 制定知识库更新规范，要求上传文档时标注版本信息。

"""


@dataclass(frozen=True)
class DBConfig:
    host: str
    port: int
    user: str
    password: str
    database: str
    charset: str = "utf8mb4"


@dataclass(frozen=True)
class Settings:
    cors_origins: list[str]
    ollama_api: str
    llm_api: str
    vllm_api: str
    production_ip: str
    ollama_model: str
    vllm_model: str
    asr_model: str
    vad_model: str
    punc_model: str
    spk_model: str
    device: str
    hotwords_path: Path
    template_path: Path
    audio_dir: Path
    prompt_template: str
    db: DBConfig
    log_level: str
    debug: bool
    host: str
    port: int

    @classmethod
    def from_env(cls) -> "Settings":
        base_dir = Path(__file__).resolve().parents[1]
        cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
        return cls(
            cors_origins=[origin.strip() for origin in cors_origins if origin.strip()],
            ollama_api=os.getenv("OLLAMA_API", "http://localhost:11434/api/generate"),
            llm_api=os.getenv("LLM_API", "http://10.8.3.173:1025/v1/api/generate"),
            vllm_api=os.getenv("VLLM_API", "http://10.8.2.21:8999/v1/chat/completions"),
            production_ip=os.getenv("PRODUCTION_IP", "10.6.2.178"),
            ollama_model=os.getenv("OLLAMA_MODEL", "qwen3:4b"),
            vllm_model=os.getenv("VLLM_MODEL", "/home/ubuntu/models/Qwen3-8B"),
            asr_model=os.getenv(
                "ASR_MODEL",
                "/root/.cache/modelscope/hub/models/iic/speech_seaco_paraformer_large_asr_nat-zh-cn-16k-common-vocab8404-pytorch",
            ),
            vad_model=os.getenv(
                "VAD_MODEL",
                "/root/.cache/modelscope/hub/models/iic/speech_fsmn_vad_zh-cn-16k-common-pytorch",
            ),
            punc_model=os.getenv(
                "PUNC_MODEL",
                "/root/.cache/modelscope/hub/models/iic/punc_ct-transformer_cn-en-common-vocab471067-large",
            ),
            spk_model=os.getenv(
                "SPK_MODEL",
                "/root/.cache/modelscope/hub/models/iic/speech_campplus_sv_zh-cn_16k-common",
            ),
            device=os.getenv("DEVICE", "cuda:0"),
            hotwords_path=Path(os.getenv("HOTWORDS_PATH", base_dir / "hotwords.txt")),
            template_path=Path(
                os.getenv("PPT_TEMPLATE", base_dir / "会议纪要模板.docx")
            ),
            audio_dir=Path(os.getenv("AUDIO_DIR", base_dir / "audio_files")),
            prompt_template=os.getenv("PROMPT_TEMPLATE", DEFAULT_PROMPT_TEMPLATE),
            db=DBConfig(
                host=os.getenv("DB_HOST", "localhost"),
                port=int(os.getenv("DB_PORT", 3306)),
                user=os.getenv("DB_USER", "root"),
                password=os.getenv("DB_PASSWORD", ""),
                database=os.getenv("DB_NAME", "meeting_minutes"),
            ),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            debug=os.getenv("DEBUG", "False").lower() == "true",
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", 8002)),
        )
