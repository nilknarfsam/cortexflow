namespace CortexFlow.Core.Models;

public class JobSettings
{
    public string ModelSize { get; set; } = "base"; // tiny, base, small, medium, large-v3
    public string Language { get; set; } = "pt"; // pt, en, es, auto
    public bool Translate { get; set; } = false; // Tradução automática via Whisper
    public string ExportFormat { get; set; } = "md"; // txt, md, json, pdf
    public string StructuringMode { get; set; } = "Clean"; // Raw, Clean, AI_Ready, NotebookLM, Study_Mode
    public string ExportDirectory { get; set; } = string.Empty;
    public bool ExportToSourceFolder { get; set; } = true; // Padrão prático: salvar na pasta de origem do arquivo
    public bool UseGpu { get; set; } = true;
    public bool EnableCache { get; set; } = true;
}
