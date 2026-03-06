"""
配置管理

Pipeline 和各组件的配置定义。
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class LLMConfig:
    """LLM 配置"""

    model: str = "gpt-4o"
    temperature: float = 0.7
    max_tokens: int = 4096
    api_key: str = ""  # 从环境变量获取


@dataclass
class RAGConfig:
    """RAG 配置"""

    embedding_model: str = "bge-large-zh"
    top_k: int = 5
    rerank: bool = True
    max_tokens_per_chunk: int = 512


@dataclass
class TTSConfig:
    """TTS 配置"""

    voice: str = "zh-CN-XiaoxiaoNeural"
    rate: str = "+0%"
    volume: str = "+0%"


@dataclass
class ManimConfig:
    """Manim 配置"""

    quality: str = "medium"  # low, medium, high
    fps: int = 30
    resolution: tuple[int, int] = (1920, 1080)


@dataclass
class ScoringConfig:
    """评分配置"""

    # 各步骤的通过阈值
    thresholds: dict[str, float] = field(default_factory=lambda: {
        "analysis": 60.0,
        "diagram": 60.0,
        "storyboard": 60.0,
        "manim_code": 60.0,
        "render": 60.0,
    })

    # 最大重试次数
    max_retries: int = 2


@dataclass
class PipelineConfig:
    """Pipeline 总配置"""

    # 组件配置
    llm: LLMConfig = field(default_factory=LLMConfig)
    rag: RAGConfig = field(default_factory=RAGConfig)
    tts: TTSConfig = field(default_factory=TTSConfig)
    manim: ManimConfig = field(default_factory=ManimConfig)
    scoring: ScoringConfig = field(default_factory=ScoringConfig)

    # 目录配置
    output_dir: str = "output"
    temp_dir: str = "temp"
    media_dir: str = "media"

    # 调试配置
    debug: bool = False
    save_intermediate: bool = True  # 是否保存中间结果

    @classmethod
    def from_dict(cls, config_dict: dict[str, Any]) -> "PipelineConfig":
        """从字典创建配置"""
        config = cls()

        if "llm" in config_dict:
            config.llm = LLMConfig(**config_dict["llm"])
        if "rag" in config_dict:
            config.rag = RAGConfig(**config_dict["rag"])
        if "tts" in config_dict:
            config.tts = TTSConfig(**config_dict["tts"])
        if "manim" in config_dict:
            config.manim = ManimConfig(**config_dict["manim"])
        if "scoring" in config_dict:
            config.scoring = ScoringConfig(**config_dict["scoring"])

        for key in ["output_dir", "temp_dir", "media_dir", "debug", "save_intermediate"]:
            if key in config_dict:
                setattr(config, key, config_dict[key])

        return config

    @classmethod
    def from_yaml(cls, filepath: str) -> "PipelineConfig":
        """从 YAML 文件创建配置"""
        import yaml
        with open(filepath, "r", encoding="utf-8") as f:
            config_dict = yaml.safe_load(f)
        return cls.from_dict(config_dict)

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        from dataclasses import asdict
        return asdict(self)
