"""
RAG 检索增强生成

实现物理知识库的检索功能，支持讲义、公式、分镜范例等的检索。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class KnowledgeChunk:
    """知识片段"""

    chunk_id: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    # 元数据示例：
    # - module: 模块（力学、电磁学等）
    # - chapter: 章节
    # - topic: 知识点
    # - type: 类型（讲义、公式、范例等）
    # - has_formula: 是否含公式
    # - has_diagram: 是否含图


@dataclass
class RetrievalResult:
    """检索结果"""

    chunks: list[KnowledgeChunk]
    scores: list[float]
    query: str


class VectorStore(ABC):
    """向量存储抽象基类"""

    @abstractmethod
    def add(self, chunks: list[KnowledgeChunk], embeddings: list[list[float]]) -> None:
        """添加文档"""
        pass

    @abstractmethod
    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[tuple[KnowledgeChunk, float]]:
        """搜索相似文档"""
        pass


class InMemoryVectorStore(VectorStore):
    """内存向量存储（用于开发和测试）"""

    def __init__(self) -> None:
        self.chunks: list[KnowledgeChunk] = []
        self.embeddings: list[list[float]] = []

    def add(self, chunks: list[KnowledgeChunk], embeddings: list[list[float]]) -> None:
        """添加文档"""
        self.chunks.extend(chunks)
        self.embeddings.extend(embeddings)

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[tuple[KnowledgeChunk, float]]:
        """搜索相似文档"""
        import numpy as np

        if not self.embeddings:
            return []

        # 计算余弦相似度
        query_vec = np.array(query_embedding)
        scores = []

        for i, emb in enumerate(self.embeddings):
            # 过滤
            if filters:
                chunk = self.chunks[i]
                match = True
                for key, value in filters.items():
                    if chunk.metadata.get(key) != value:
                        match = False
                        break
                if not match:
                    continue

            emb_vec = np.array(emb)
            score = np.dot(query_vec, emb_vec) / (
                np.linalg.norm(query_vec) * np.linalg.norm(emb_vec) + 1e-8
            )
            scores.append((i, float(score)))

        # 排序取 top-k
        scores.sort(key=lambda x: x[1], reverse=True)
        results = []
        for idx, score in scores[:top_k]:
            results.append((self.chunks[idx], score))

        return results


class Embedder(ABC):
    """嵌入模型抽象基类"""

    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        """生成文本嵌入"""
        pass


class MockEmbedder(Embedder):
    """模拟嵌入模型（用于开发和测试）"""

    def __init__(self, dim: int = 768) -> None:
        self.dim = dim

    def embed(self, texts: list[str]) -> list[list[float]]:
        """生成随机嵌入（仅用于测试）"""
        import hashlib

        import numpy as np

        embeddings = []
        for text in texts:
            # 使用文本哈希生成伪随机嵌入，确保相同文本得到相同嵌入
            hash_obj = hashlib.md5(text.encode())
            seed = int(hash_obj.hexdigest(), 16) % (2**32)
            rng = np.random.default_rng(seed)
            emb = rng.random(self.dim).tolist()
            embeddings.append(emb)

        return embeddings


class PhysicsRAG:
    """
    物理知识库 RAG 系统

    用于检索物理讲义、公式、分镜范例等知识。
    支持按模块、章节、类型过滤。
    """

    def __init__(
        self,
        vector_store: VectorStore | None = None,
        embedder: Embedder | None = None,
    ):
        self.vector_store = vector_store or InMemoryVectorStore()
        self.embedder = embedder or MockEmbedder()

        # 预定义的物理模块
        self.modules = [
            "力学",
            "电磁学",
            "热学",
            "光学",
            "原子物理",
        ]

        # 预定义的知识类型
        self.knowledge_types = [
            "讲义",
            "公式",
            "分镜范例",
            "示意图范例",
            "考纲",
        ]

    def add_knowledge(self, chunks: list[KnowledgeChunk]) -> None:
        """
        添加知识到知识库

        Args:
            chunks: 知识片段列表
        """
        texts = [c.content for c in chunks]
        embeddings = self.embedder.embed(texts)
        self.vector_store.add(chunks, embeddings)

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        module: str | None = None,
        knowledge_type: str | None = None,
    ) -> RetrievalResult:
        """
        检索相关知识

        Args:
            query: 查询文本
            top_k: 返回数量
            module: 按模块过滤（力学、电磁学等）
            knowledge_type: 按类型过滤（讲义、公式等）

        Returns:
            检索结果
        """
        # 构建过滤条件
        filters = {}
        if module:
            filters["module"] = module
        if knowledge_type:
            filters["type"] = knowledge_type

        # 生成查询嵌入
        query_embedding = self.embedder.embed([query])[0]

        # 检索
        results = self.vector_store.search(
            query_embedding,
            top_k=top_k,
            filters=filters if filters else None,
        )

        chunks = [r[0] for r in results]
        scores = [r[1] for r in results]

        return RetrievalResult(chunks=chunks, scores=scores, query=query)

    def retrieve_formulas(self, topic: str, top_k: int = 5) -> list[KnowledgeChunk]:
        """检索相关公式"""
        result = self.retrieve(topic, top_k=top_k, knowledge_type="公式")
        return result.chunks

    def retrieve_storyboard_examples(
        self,
        topic: str,
        top_k: int = 3,
    ) -> list[KnowledgeChunk]:
        """检索分镜范例"""
        result = self.retrieve(topic, top_k=top_k, knowledge_type="分镜范例")
        return result.chunks

    def retrieve_for_analysis(
        self,
        question_text: str,
        top_k: int = 5,
    ) -> dict[str, list[KnowledgeChunk]]:
        """
        为物理分析步骤检索知识

        Returns:
            {
                "formulas": 相关公式,
                "concepts": 相关概念/讲义,
                "syllabus": 考纲要求,
            }
        """
        formulas = self.retrieve(
            question_text, top_k=top_k, knowledge_type="公式"
        ).chunks

        concepts = self.retrieve(
            question_text, top_k=top_k, knowledge_type="讲义"
        ).chunks

        syllabus = self.retrieve(
            question_text, top_k=2, knowledge_type="考纲"
        ).chunks

        return {
            "formulas": formulas,
            "concepts": concepts,
            "syllabus": syllabus,
        }


# 预置的高中物理公式
PHYSICS_FORMULAS = [
    # 力学
    KnowledgeChunk(
        "formula-newton-2",
        "牛顿第二定律：F = ma，其中 F 为合外力，m 为质量，a 为加速度",
        {"module": "力学", "type": "公式", "topic": "牛顿定律"},
    ),
    KnowledgeChunk(
        "formula-gravity",
        "重力公式：G = mg，其中 g ≈ 10m/s²（取整）或 9.8m/s²",
        {"module": "力学", "type": "公式", "topic": "重力"},
    ),
    KnowledgeChunk(
        "formula-kinematic-1",
        "匀变速直线运动速度公式：v = v₀ + at",
        {"module": "力学", "type": "公式", "topic": "运动学"},
    ),
    KnowledgeChunk(
        "formula-kinematic-2",
        "匀变速直线运动位移公式：s = v₀t + ½at²",
        {"module": "力学", "type": "公式", "topic": "运动学"},
    ),
    KnowledgeChunk(
        "formula-kinematic-3",
        "匀变速直线运动速度位移关系：v² - v₀² = 2as",
        {"module": "力学", "type": "公式", "topic": "运动学"},
    ),
    KnowledgeChunk(
        "formula-momentum",
        "动量定理：Ft = mv - mv₀ = Δp",
        {"module": "力学", "type": "公式", "topic": "动量"},
    ),
    KnowledgeChunk(
        "formula-energy-kinetic",
        "动能公式：Eₖ = ½mv²",
        {"module": "力学", "type": "公式", "topic": "能量"},
    ),
    KnowledgeChunk(
        "formula-energy-potential",
        "重力势能公式：Eₚ = mgh",
        {"module": "力学", "type": "公式", "topic": "能量"},
    ),
    # 电磁学
    KnowledgeChunk(
        "formula-ohm",
        "欧姆定律：U = IR，其中 U 为电压，I 为电流，R 为电阻",
        {"module": "电磁学", "type": "公式", "topic": "电路"},
    ),
    KnowledgeChunk(
        "formula-power-electric",
        "电功率公式：P = UI = I²R = U²/R",
        {"module": "电磁学", "type": "公式", "topic": "电路"},
    ),
    KnowledgeChunk(
        "formula-coulomb",
        "库仑定律：F = kq₁q₂/r²，k = 9×10⁹ N·m²/C²",
        {"module": "电磁学", "type": "公式", "topic": "电场"},
    ),
    KnowledgeChunk(
        "formula-electric-field",
        "电场强度公式：E = F/q = kQ/r²（点电荷），E = U/d（匀强电场）",
        {"module": "电磁学", "type": "公式", "topic": "电场"},
    ),
]


def create_default_rag() -> PhysicsRAG:
    """创建包含预置知识的 RAG 系统"""
    rag = PhysicsRAG()
    rag.add_knowledge(PHYSICS_FORMULAS)
    return rag
