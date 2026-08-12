using System;
using System.Collections.Generic;
using CortexFlow.Core.Models;
using CortexFlow.Core.Services;
using Xunit;

namespace CortexFlow.Core.Tests;

public class ExportServiceTimeBlocksTests
{
    [Fact]
    public void FormatTextContent_TimeBlocks_FormatsIntervalsWithHeaders()
    {
        var result = new TranscriptionResult
        {
            FilePath = "aula_teologia.mp4",
            Language = "pt",
            FullText = "Primeira frase da aula. Segunda frase da aula.",
            Segments = new List<TranscriptionSegment>
            {
                new TranscriptionSegment { Start = TimeSpan.FromSeconds(0), End = TimeSpan.FromSeconds(15), Text = "Primeira frase da aula." },
                new TranscriptionSegment { Start = TimeSpan.FromSeconds(35), End = TimeSpan.FromSeconds(50), Text = "Segunda frase da aula." }
            }
        };

        var formatted = ExportService.FormatTextContent(result, "TIME_BLOCKS");

        Assert.Contains("# Transcrição por Blocos de Tempo: aula_teologia.mp4", formatted);
        Assert.Contains("### ⏱️ [00:00 - 00:35]", formatted);
        Assert.Contains("Primeira frase da aula.", formatted);
        Assert.Contains("Segunda frase da aula.", formatted);
    }
}
