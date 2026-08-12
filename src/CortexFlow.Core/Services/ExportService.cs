using System;
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
        var outputDir = string.IsNullOrWhiteSpace(settings.ExportDirectory)
            ? Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments), "CortexFlow_Exports")
            : settings.ExportDirectory;

        if (!Directory.Exists(outputDir))
        {
            Directory.CreateDirectory(outputDir);
        }

        var baseFileName = Path.GetFileNameWithoutExtension(result.FilePath);
        var extension = settings.ExportFormat.ToLowerInvariant() switch
        {
            "json" => ".json",
            "txt" => ".txt",
            _ => ".md"
        };

        var outputPath = Path.Combine(outputDir, $"{baseFileName}_{settings.StructuringMode.ToLowerInvariant()}{extension}");

        string content;
        if (extension == ".json")
        {
            content = JsonSerializer.Serialize(result, new JsonSerializerOptions { WriteIndented = true });
        }
        else
        {
            content = FormatTextContent(result, settings.StructuringMode);
        }

        await File.WriteAllTextAsync(outputPath, content, Encoding.UTF8);
        return outputPath;
    }

    private static string FormatTextContent(TranscriptionResult result, string mode)
    {
        var sb = new StringBuilder();

        switch (mode.ToUpperInvariant())
        {
            case "RAW":
                sb.AppendLine(result.FullText);
                break;

            case "NOTEBOOKLM":
            case "AI_READY":
                sb.AppendLine($"# Transcrição: {Path.GetFileName(result.FilePath)}");
                sb.AppendLine($"**Idioma:** {result.Language} | **Duração:** {result.Duration:g}");
                sb.AppendLine();
                sb.AppendLine("## Conteúdo Principal");
                sb.AppendLine(result.FullText);
                sb.AppendLine();
                sb.AppendLine("## Linha do Tempo (Timestamps)");
                foreach (var seg in result.Segments)
                {
                    sb.AppendLine($"[{seg.Start:mm\\:ss} - {seg.End:mm\\:ss}] {seg.Text}");
                }
                break;

            case "STUDY_MODE":
                sb.AppendLine($"# Guia de Estudos - {Path.GetFileName(result.FilePath)}");
                sb.AppendLine();
                sb.AppendLine("## Transcrição Limpa");
                sb.AppendLine(result.FullText);
                sb.AppendLine();
                sb.AppendLine("## Marcações Temporais para Revisão");
                foreach (var seg in result.Segments)
                {
                    sb.AppendLine($" - **{seg.Start:mm\\:ss}**: {seg.Text}");
                }
                break;

            default: // CLEAN
                sb.AppendLine($"---");
                sb.AppendLine($"Arquivo: {Path.GetFileName(result.FilePath)}");
                sb.AppendLine($"---");
                sb.AppendLine(result.FullText);
                break;
        }

        return sb.ToString();
    }
}
