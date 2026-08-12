using System;
using System.Collections.Generic;
using CortexFlow.Core.Models;
using CortexFlow.Core.Services;
using Xunit;

namespace CortexFlow.Core.Tests;

public class ExportServiceAnkiTests
{
    [Fact]
    public void FormatAnkiCsvContent_CreatesValidAnkiCsvFormat()
    {
        var result = new TranscriptionResult
        {
            FilePath = "aula_estudo.mp4",
            Language = "pt",
            FullText = "Introdução ao conceito de teologia.",
            Segments = new List<TranscriptionSegment>
            {
                new TranscriptionSegment { Start = TimeSpan.FromSeconds(0), End = TimeSpan.FromSeconds(10), Text = "Primeiro ponto da aula." }
            }
        };

        var csv = ExportService.FormatAnkiCsvContent(result);

        Assert.Contains("#front,back,tags", csv);
        Assert.Contains("aula_estudo.mp4 [00:00 - 00:10]", csv);
        Assert.Contains("Primeiro ponto da aula.", csv);
        Assert.Contains("CortexFlow_Flashcards", csv);
    }
}
