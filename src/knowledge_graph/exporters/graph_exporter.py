"""Exportação Markdown do grafo de conhecimento."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from src.knowledge_graph.graph_engine import GRAPH_EXPORT_FILE

if TYPE_CHECKING:
    from src.knowledge_graph.graph_engine import GraphEngine


class GraphExporter:
    def __init__(self, graph: "GraphEngine") -> None:
        self._graph = graph

    def render(self) -> str:
        stats = self._graph.stats or {}
        lines = [
            "# Visão Geral do Grafo",
            "",
            f"- **Atualizado em:** {self._graph.updated_at or '—'}",
            f"- **Total de nós:** {stats.get('total_nodes', 0)}",
            f"- **Total de relações:** {stats.get('total_edges', 0)}",
            f"- **Documentos:** {stats.get('documents', 0)}",
            f"- **Documentos conectados:** {stats.get('connected_documents', 0)}",
            f"- **Chunks:** {stats.get('chunks', 0)}",
            f"- **Flashcards:** {stats.get('flashcards', 0)}",
            f"- **Quizzes:** {stats.get('quizzes', 0)}",
            "",
            "# Tópicos Mais Conectados",
            "",
        ]
        lines.extend(self._bullet_section(stats.get("top_topics", []), "label", "connections"))

        lines.extend(["", "# Referências Mais Usadas", ""])
        lines.extend(
            self._bullet_section(stats.get("top_references", []), "label", "connections")
        )

        lines.extend(["", "# Coleções", ""])
        lines.extend(
            self._bullet_section(stats.get("top_collections", []), "label", "connections")
        )

        lines.extend(["", "# Documentos Relacionados", ""])
        lines.extend(self._related_section())

        return "\n".join(lines) + "\n"

    def write(self) -> Path:
        GRAPH_EXPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
        content = self.render()
        GRAPH_EXPORT_FILE.write_text(content, encoding="utf-8")
        return GRAPH_EXPORT_FILE

    def _related_section(self) -> list[str]:
        from src.library import get_library

        lib = get_library()
        lines: list[str] = []
        doc_nodes = [
            n for n in self._graph.nodes.values() if n.get("type") == "document"
        ][:20]
        for node in doc_nodes:
            cid = str(node.get("metadata", {}).get("catalog_id", ""))
            if not cid:
                continue
            title = node.get("label", cid)
            related = self._graph.related.find_related(cid, limit=5)
            if not related:
                continue
            lines.append(f"## {title}")
            for rel in related:
                reasons = ", ".join(rel.get("reasons", []))
                rtitle = rel.get("title", rel.get("document_id", ""))
                lines.append(f"- **{rtitle}** (score {rel.get('score', 0):.1f}) — {reasons}")
            lines.append("")
        if not lines:
            lines.append("_Nenhuma relação documento-documento registrada ainda._")
        return lines

    @staticmethod
    def _bullet_section(
        items: list[dict[str, Any]],
        label_key: str,
        count_key: str,
    ) -> list[str]:
        if not items:
            return ["_Nenhum item registrado._"]
        return [f"- **{it.get(label_key, '—')}** — {it.get(count_key, 0)} conexões" for it in items]
