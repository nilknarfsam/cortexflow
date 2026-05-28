"""Exportador NotebookLM — pipeline RAW → CLEAN → AI_READY → NOTEBOOKLM."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.ai_ready.formatters.markdown_formatter import beautify_markdown
from src.ai_ready.metadata.metadata_builder import MetadataBuilder, build_metadata_yaml
from src.ai_ready.stages import ContentStage, StageResult
from src.ai_ready.templates import TEMPLATE_RENDERERS, TemplateContext


ExportMode = str  # raw | clean | ai_ready | notebooklm


@dataclass
class ExportContext:
    """Contexto de exportação para o pipeline AI-ready."""

    source_path: str
    language: str = "auto"
    model: str = ""
    content_template: str = "generic"
    export_mode: str = "raw"
    speaker: str = ""
    author: str = ""
    topics: list[str] | None = None


class NotebookLMExporter:
    """Engine de exportação inteligente para NotebookLM e pipelines de IA."""

    def export(self, text: str, ctx: ExportContext) -> StageResult:
        mode = ctx.export_mode.lower()
        if mode == "raw":
            return self._raw(text, ctx)
        if mode == "clean":
            return self._clean(text, ctx)
        if mode == "ai_ready":
            return self._ai_ready(text, ctx)
        if mode == "notebooklm":
            return self._notebooklm(text, ctx)
        return self._raw(text, ctx)

    def export_text(self, text: str, ctx: ExportContext) -> str:
        return self.export(text, ctx).content

    def _raw(self, text: str, ctx: ExportContext) -> StageResult:
        return StageResult(
            stage=ContentStage.RAW,
            content=text,
            metadata=self._base_metadata(ctx, ContentStage.RAW),
        )

    def _clean(self, text: str, ctx: ExportContext) -> StageResult:
        cleaned = beautify_markdown(text)
        return StageResult(
            stage=ContentStage.CLEAN,
            content=cleaned,
            metadata=self._base_metadata(ctx, ContentStage.CLEAN),
        )

    def _ai_ready(self, text: str, ctx: ExportContext) -> StageResult:
        clean = self._clean(text, ctx)
        template_ctx = TemplateContext(
            content=clean.content,
            title=self._title(ctx),
            topics=list(ctx.topics or []),
        )
        from src.ai_ready.templates.base import extract_sections

        sections = extract_sections(template_ctx)
        body = self._render_template(clean.content, ctx)
        content = f"# {self._title(ctx)}\n\n{body}"
        meta = self._base_metadata(ctx, ContentStage.AI_READY)
        meta["template"] = ctx.content_template
        meta["tags"] = sections.get("tags", [])
        return StageResult(stage=ContentStage.AI_READY, content=content.strip(), metadata=meta)

    def _notebooklm(self, text: str, ctx: ExportContext) -> StageResult:
        ai_ready = self._ai_ready(text, ctx)
        meta_builder = self._metadata_builder(ctx, ContentStage.NOTEBOOKLM, ai_ready.metadata)
        if ctx.topics:
            meta_builder.topics = list(ctx.topics)
        tags = ai_ready.metadata.get("tags", [])
        if isinstance(tags, list) and tags:
            meta_builder.tags = tags

        yaml_block = build_metadata_yaml(meta_builder)
        content = f"{yaml_block}\n\n{ai_ready.content}"
        meta = self._base_metadata(ctx, ContentStage.NOTEBOOKLM)
        meta["template"] = ctx.content_template
        return StageResult(stage=ContentStage.NOTEBOOKLM, content=content.strip(), metadata=meta)

    def _render_template(self, content: str, ctx: ExportContext) -> str:
        renderer = TEMPLATE_RENDERERS.get(ctx.content_template, TEMPLATE_RENDERERS["generic"])
        title = self._title(ctx)
        template_ctx = TemplateContext(
            content=content,
            title=title,
            topics=list(ctx.topics or []),
        )
        return renderer(template_ctx)

    def _title(self, ctx: ExportContext) -> str:
        builder = MetadataBuilder.from_source_path(
            ctx.source_path,
            language=ctx.language,
            content_type=ctx.content_template,
        )
        return builder.title

    def _metadata_builder(
        self,
        ctx: ExportContext,
        stage: ContentStage,
        extra: dict[str, Any] | None = None,
    ) -> MetadataBuilder:
        builder = MetadataBuilder.from_source_path(
            ctx.source_path,
            language=ctx.language,
            content_type=ctx.content_template,
            model=ctx.model,
            pipeline_stage=stage.value,
            speaker=ctx.speaker,
            author=ctx.author,
        )
        if ctx.topics:
            builder.topics = list(ctx.topics)
        if extra and "tags" in extra and isinstance(extra["tags"], list):
            builder.tags = extra["tags"]
        return builder

    def _base_metadata(self, ctx: ExportContext, stage: ContentStage) -> dict[str, Any]:
        builder = self._metadata_builder(ctx, stage)
        data = builder.to_dict()
        data["export_mode"] = ctx.export_mode
        data["template"] = ctx.content_template
        return data


_default_exporter = NotebookLMExporter()


def export_notebooklm(text: str, ctx: ExportContext) -> StageResult:
    return _default_exporter.export(text, ctx)
