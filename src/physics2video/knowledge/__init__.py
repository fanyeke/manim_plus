"""
知识库与 RAG 模块

提供物理讲义、公式集、分镜范例等知识的存储与检索。
"""

from .rag import KnowledgeChunk, PhysicsRAG

__all__ = [
    "PhysicsRAG",
    "KnowledgeChunk",
]
