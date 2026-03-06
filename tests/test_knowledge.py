"""
测试知识库模块
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest


class TestKnowledgeChunk:
    """测试知识片段"""

    def test_create_chunk(self):
        """测试创建知识片段"""
        from physics2video.knowledge.rag import KnowledgeChunk

        chunk = KnowledgeChunk(
            chunk_id="formula-001",
            content="牛顿第二定律：F = ma",
            metadata={
                "module": "力学",
                "type": "公式",
                "topic": "牛顿定律",
            },
        )

        assert chunk.chunk_id == "formula-001"
        assert "F = ma" in chunk.content
        assert chunk.metadata["module"] == "力学"


class TestPhysicsRAG:
    """测试物理知识库 RAG"""

    def test_create_rag(self):
        """测试创建 RAG 系统"""
        from physics2video.knowledge.rag import PhysicsRAG

        rag = PhysicsRAG()
        assert rag.vector_store is not None
        assert rag.embedder is not None

    def test_add_knowledge(self):
        """测试添加知识"""
        from physics2video.knowledge.rag import KnowledgeChunk, PhysicsRAG

        rag = PhysicsRAG()
        chunks = [
            KnowledgeChunk("test-001", "测试内容1", {"type": "讲义"}),
            KnowledgeChunk("test-002", "测试内容2", {"type": "公式"}),
        ]

        rag.add_knowledge(chunks)

        # 检查内部存储
        assert len(rag.vector_store.chunks) == 2

    def test_retrieve(self):
        """测试检索知识"""
        from physics2video.knowledge.rag import KnowledgeChunk, PhysicsRAG

        rag = PhysicsRAG()
        chunks = [
            KnowledgeChunk("formula-001", "牛顿第二定律 F=ma", {"type": "公式", "module": "力学"}),
            KnowledgeChunk("formula-002", "欧姆定律 U=IR", {"type": "公式", "module": "电磁学"}),
        ]
        rag.add_knowledge(chunks)

        result = rag.retrieve("牛顿定律", top_k=2)

        assert len(result.chunks) <= 2
        assert result.query == "牛顿定律"

    def test_retrieve_with_filter(self):
        """测试带过滤的检索"""
        from physics2video.knowledge.rag import KnowledgeChunk, PhysicsRAG

        rag = PhysicsRAG()
        chunks = [
            KnowledgeChunk("c1", "力学讲义", {"type": "讲义", "module": "力学"}),
            KnowledgeChunk("c2", "力学公式", {"type": "公式", "module": "力学"}),
            KnowledgeChunk("c3", "电磁学公式", {"type": "公式", "module": "电磁学"}),
        ]
        rag.add_knowledge(chunks)

        result = rag.retrieve("公式", top_k=5, knowledge_type="公式")

        # 只返回公式类型
        for chunk in result.chunks:
            assert chunk.metadata.get("type") == "公式"

    def test_create_default_rag(self):
        """测试创建带预置知识的 RAG"""
        from physics2video.knowledge.rag import create_default_rag

        rag = create_default_rag()

        # 应该包含预置的物理公式
        assert len(rag.vector_store.chunks) > 0

        # 检索牛顿定律相关公式
        result = rag.retrieve_formulas("牛顿定律", top_k=3)
        assert len(result) > 0

    def test_retrieve_for_analysis(self):
        """测试为物理分析检索知识"""
        from physics2video.knowledge.rag import create_default_rag

        rag = create_default_rag()
        results = rag.retrieve_for_analysis("一个质量为2kg的物体受到10N的力")

        assert "formulas" in results
        assert "concepts" in results
        assert "syllabus" in results


class TestInMemoryVectorStore:
    """测试内存向量存储"""

    def test_add_and_search(self):
        """测试添加和搜索"""
        from physics2video.knowledge.rag import InMemoryVectorStore, KnowledgeChunk

        store = InMemoryVectorStore()

        chunks = [
            KnowledgeChunk("c1", "内容1"),
            KnowledgeChunk("c2", "内容2"),
        ]
        embeddings = [
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
        ]

        store.add(chunks, embeddings)

        # 搜索
        results = store.search([1.0, 0.0, 0.0], top_k=1)

        assert len(results) == 1
        assert results[0][0].chunk_id == "c1"

    def test_search_with_filter(self):
        """测试带过滤的搜索"""
        from physics2video.knowledge.rag import InMemoryVectorStore, KnowledgeChunk

        store = InMemoryVectorStore()

        chunks = [
            KnowledgeChunk("c1", "内容1", {"type": "A"}),
            KnowledgeChunk("c2", "内容2", {"type": "B"}),
        ]
        embeddings = [
            [1.0, 0.0],
            [0.9, 0.1],
        ]

        store.add(chunks, embeddings)

        # 带过滤搜索
        results = store.search([1.0, 0.0], top_k=2, filters={"type": "B"})

        assert len(results) == 1
        assert results[0][0].metadata["type"] == "B"
