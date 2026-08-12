using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;
using CortexFlow.Core.Abstractions;
using CortexFlow.Core.Models;

namespace CortexFlow.Core.Services;

public class ExportService : IExportService
{
    public async Task<string> ExportAsync(TranscriptionResult result, JobSettings settings)
    {
        string outputDir;

        if (settings.ExportToSourceFolder && !string.IsNullOrWhiteSpace(result.FilePath))
        {
            var dir = Path.GetDirectoryName(result.FilePath);
            if (string.IsNullOrWhiteSpace(dir))
            {
                dir = Path.GetDirectoryName(Path.GetFullPath(result.FilePath));
            }
            outputDir = !string.IsNullOrWhiteSpace(dir)
                ? dir
                : Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments), "CortexFlow_Exports");
        }
        else if (!string.IsNullOrWhiteSpace(settings.ExportDirectory))
        {
            outputDir = settings.ExportDirectory;
        }
        else
        {
            outputDir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments), "CortexFlow_Exports");
        }

        if (!Directory.Exists(outputDir))
        {
            Directory.CreateDirectory(outputDir);
        }

        var baseFileName = Path.GetFileNameWithoutExtension(result.FilePath);
        var fmt = settings.ExportFormat.ToLowerInvariant();
        var extension = fmt switch
        {
            "json" => ".json",
            "txt" => ".txt",
            "pdf" => ".pdf",
            _ => ".md"
        };

        var outputPath = Path.Combine(outputDir, $"{baseFileName}_{settings.StructuringMode.ToLowerInvariant()}{extension}");

        if (extension == ".json")
        {
            var json = JsonSerializer.Serialize(result, new JsonSerializerOptions { WriteIndented = true });
            await File.WriteAllTextAsync(outputPath, json, Encoding.UTF8);
        }
        else
        {
            var textContent = FormatTextContent(result, settings.StructuringMode);
            await File.WriteAllTextAsync(outputPath, textContent, Encoding.UTF8);
        }

        return outputPath;
    }

    public static string FormatTextContent(TranscriptionResult result, string mode)
    {
        var sb = new StringBuilder();
        var fileName = Path.GetFileName(result.FilePath);

        switch (mode.ToUpperInvariant())
        {
            case "TIME_BLOCKS":
            case "TIMEBLOCKS":
            case "BLOCOS_DE_TEMPO":
                sb.AppendLine($"# Transcrição por Blocos de Tempo: {fileName}");
                sb.AppendLine($"**Idioma:** {result.Language} | **Duração:** {result.Duration:mm\\:ss}");
                sb.AppendLine($"---");
                sb.AppendLine();

                if (result.Segments != null && result.Segments.Count > 0)
                {
                    TimeSpan currentBlockStart = result.Segments[0].Start;
                    TimeSpan blockWindow = TimeSpan.FromSeconds(30);
                    var currentBlockText = new StringBuilder();

                    foreach (var seg in result.Segments)
                    {
                        if (seg.Start - currentBlockStart >= blockWindow && currentBlockText.Length > 0)
                        {
                            var blockEnd = seg.Start;
                            sb.AppendLine($"### ⏱️ [{currentBlockStart:mm\\:ss} - {blockEnd:mm\\:ss}]");
                            sb.AppendLine(currentBlockText.ToString().Trim());
                            sb.AppendLine();

                            currentBlockStart = seg.Start;
                            currentBlockText.Clear();
                        }
                        currentBlockText.Append(seg.Text).Append(' ');
                    }

                    if (currentBlockText.Length > 0)
                    {
                        var lastEnd = result.Segments[^1].End;
                        sb.AppendLine($"### ⏱️ [{currentBlockStart:mm\\:ss} - {lastEnd:mm\\:ss}]");
                        sb.AppendLine(currentBlockText.ToString().Trim());
                        sb.AppendLine();
                    }
                }
                else
                {
                    sb.AppendLine(result.FullText);
                }
                break;

            case "NOTEBOOKLM":
            case "AI_READY":
                sb.AppendLine($"# Transcrição Estruturada para IA: {fileName}");
                sb.AppendLine($"**Idioma:** {result.Language} | **Duração:** {result.Duration:mm\\:ss}");
                sb.AppendLine();
                sb.AppendLine("## Conteúdo Principal");
                sb.AppendLine(FormatParagraphs(result.FullText));
                sb.AppendLine();
                sb.AppendLine("## Linha do Tempo (Timestamps)");
                if (result.Segments != null)
                {
                    foreach (var seg in result.Segments)
                    {
                        sb.AppendLine($"[{seg.Start:mm\\:ss} - {seg.End:mm\\:ss}] {seg.Text.Trim()}");
                    }
                }
                break;

            case "STUDY_MODE":
                sb.AppendLine($"# Guia de Estudos - {fileName}");
                sb.AppendLine($"**Data do Job:** {DateTime.Now:yyyy-MM-dd HH:mm}");
                sb.AppendLine();
                sb.AppendLine("## 📖 Conteúdo da Transcrição");
                sb.AppendLine(FormatParagraphs(result.FullText));
                sb.AppendLine();
                sb.AppendLine("## ⏱️ Pontos-Chave da Linha do Tempo");
                if (result.Segments != null)
                {
                    foreach (var seg in result.Segments)
                    {
                        sb.AppendLine($" - **[{seg.Start:mm\\:ss}]**: {seg.Text.Trim()}");
                    }
                }
                break;

            case "RAW":
                sb.AppendLine(result.FullText);
                break;

            default: // CLEAN
                sb.AppendLine($"# Transcrição Limpa: {fileName}");
                sb.AppendLine($"---");
                sb.AppendLine();
                sb.AppendLine(FormatParagraphs(result.FullText));
                break;
        }

        return sb.ToString();
    }

    private static string FormatParagraphs(string rawText)
    {
        if (string.IsNullOrWhiteSpace(rawText)) return string.Empty;

        // Se o texto já contiver quebras de linha duplas, mantém
        if (rawText.Contains("\n\n")) return rawText;

        var sb = new StringBuilder();
        var sentences = rawText.Split(new[] { ". ", "! ", "? " }, StringSplitOptions.RemoveEmptyEntries);
        var sentenceCount = 0;

        foreach (var sentence in sentences)
        {
            sb.Append(sentence.Trim());

            if (!sentence.EndsWith('.') && !sentence.EndsWith('!') && !sentence.EndsWith('?'))
            {
                sb.Append(". ");
            }
            else
            {
                sb.Append(" ");
            }

            sentenceCount++;
            if (sentenceCount >= 4)
            {
                sb.AppendLine();
                sb.AppendLine();
                sentenceCount = 0;
            }
        }

        return sb.ToString().Trim();
    }
}
