namespace CortexFlow.Core.Models;

public class JobSettings
{
    public string ModelSize { get; set; } = "base"; // tiny, base, small, medium, large-v3
    public string Language { get; set; } = "pt";
    public string ExportFormat { get; set; } = "md"; // txt, md, json
    public string StructuringMode { get; set; } = "Clean"; // Raw, Clean, AI_Ready, NotebookLM, Study_Mode
    public string ExportDirectory { get; set; } = string.Empty;
    public bool UseGpu { get; set; } = true;
    public bool EnableCache { get; set; } = true;
}
