"""
TTS 语音合成工具

使用 edge-tts 进行语音合成。
"""

import asyncio
import os
from dataclasses import dataclass


@dataclass
class TTSResult:
    """TTS 结果"""

    file_path: str
    duration: float  # 秒
    text: str
    voice: str


class TextToSpeech:
    """
    文本转语音工具

    使用 edge-tts 进行语音合成，支持中文普通话。
    """

    # 推荐的中文语音
    VOICES = {
        "female": "zh-CN-XiaoxiaoNeural",  # 女声，清晰自然
        "male": "zh-CN-YunxiNeural",  # 男声
        "female_news": "zh-CN-XiaoyiNeural",  # 女声，新闻风格
    }

    def __init__(
        self,
        voice: str = "female",
        output_dir: str = "audio",
        rate: str = "+0%",
        volume: str = "+0%",
    ):
        """
        初始化 TTS

        Args:
            voice: 语音类型 (female, male, female_news) 或完整语音名称
            output_dir: 输出目录
            rate: 语速调整（如 +20%, -10%）
            volume: 音量调整
        """
        self.voice = self.VOICES.get(voice, voice)
        self.output_dir = output_dir
        self.rate = rate
        self.volume = volume

        os.makedirs(output_dir, exist_ok=True)

    async def synthesize_async(
        self,
        text: str,
        filename: str | None = None,
    ) -> TTSResult:
        """
        异步合成语音

        Args:
            text: 要合成的文本
            filename: 输出文件名（不含路径和扩展名）

        Returns:
            TTSResult 对象
        """
        try:
            import edge_tts
        except ImportError:
            raise ImportError("请安装 edge-tts: pip install edge-tts")

        # 生成文件名
        if filename is None:
            import hashlib
            hash_obj = hashlib.md5(text.encode())
            filename = hash_obj.hexdigest()[:12]

        output_path = os.path.join(self.output_dir, f"{filename}.mp3")

        # 合成语音
        communicate = edge_tts.Communicate(
            text,
            self.voice,
            rate=self.rate,
            volume=self.volume,
        )

        await communicate.save(output_path)

        # 获取时长
        duration = self._get_audio_duration(output_path)

        return TTSResult(
            file_path=output_path,
            duration=duration,
            text=text,
            voice=self.voice,
        )

    def synthesize(
        self,
        text: str,
        filename: str | None = None,
    ) -> TTSResult:
        """
        同步合成语音

        Args:
            text: 要合成的文本
            filename: 输出文件名

        Returns:
            TTSResult 对象
        """
        return asyncio.run(self.synthesize_async(text, filename))

    def synthesize_batch(
        self,
        texts: list[str],
        filenames: list[str] | None = None,
    ) -> list[TTSResult]:
        """
        批量合成语音

        Args:
            texts: 文本列表
            filenames: 文件名列表

        Returns:
            TTSResult 列表
        """
        if filenames is None:
            filenames = [None] * len(texts)

        results = []
        for text, filename in zip(texts, filenames):
            result = self.synthesize(text, filename)
            results.append(result)

        return results

    def _get_audio_duration(self, file_path: str) -> float:
        """获取音频时长"""
        try:
            from pydub import AudioSegment
            audio = AudioSegment.from_file(file_path)
            return len(audio) / 1000.0
        except Exception:
            # 如果无法读取，返回估算值（约 5 字/秒）
            return 3.0

    @staticmethod
    def estimate_duration(text: str, chars_per_second: float = 5.0) -> float:
        """
        估算文本的语音时长

        Args:
            text: 文本
            chars_per_second: 每秒字数

        Returns:
            估计时长（秒）
        """
        # 移除标点和空白
        import re
        clean_text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]', '', text)
        return len(clean_text) / chars_per_second


class TTSManager:
    """
    TTS 管理器

    管理分镜的语音合成，支持缓存和批量处理。
    """

    def __init__(
        self,
        tts: TextToSpeech | None = None,
        cache_dir: str = "tts_cache",
    ):
        self.tts = tts or TextToSpeech()
        self.cache_dir = cache_dir
        self.cache: dict[str, TTSResult] = {}

        os.makedirs(cache_dir, exist_ok=True)

    def get_or_create(self, text: str, scene_id: int) -> TTSResult:
        """
        获取或创建语音

        如果缓存中存在则返回缓存，否则合成新语音。
        """
        cache_key = f"{scene_id}_{hash(text)}"

        if cache_key in self.cache:
            return self.cache[cache_key]

        filename = f"scene_{scene_id:03d}"
        result = self.tts.synthesize(text, filename)

        self.cache[cache_key] = result
        return result

    def synthesize_storyboard(
        self,
        narrations: list[str],
    ) -> list[TTSResult]:
        """
        合成整个分镜的语音

        Args:
            narrations: 各场景的读白列表

        Returns:
            TTSResult 列表
        """
        results = []
        for i, narration in enumerate(narrations, 1):
            result = self.get_or_create(narration, i)
            results.append(result)
        return results

    def get_total_duration(self, results: list[TTSResult]) -> float:
        """获取总时长"""
        return sum(r.duration for r in results)
