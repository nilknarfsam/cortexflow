using System;
using System.IO;
using System.Threading.Tasks;
using CortexFlow.Core.Models;
using CortexFlow.Core.Services;
using Xunit;

namespace CortexFlow.Core.Tests;

public class ExportServiceTests
{
    [Theory]
    [InlineData("md", ".md")]
    [InlineData("txt", ".txt")]
    [InlineData("json", ".json")]
    [InlineData("pdf", ".pdf")]
    public async Task ExportAsync_ExportsAllSupportedFormats(string format, string expectedExtension)
    {
        var tempExportDir = Path.Combine(Path.GetTempPath(), Guid.NewGuid().ToString());
        var exportService = new ExportService();

        var result = new TranscriptionResult
        {
            FilePath = "test_audio.mp3",
            FullText = "Conteúdo de teste para validação de formatos de exportação.",
            Language = "pt",
            Duration = TimeSpan.FromMinutes(1)
        };

        var settings = new JobSettings
        {
            ExportDirectory = tempExportDir,
            ExportFormat = format,
            StructuringMode = "Clean"
        };

        try
        {
            var exportedPath = await exportService.ExportAsync(result, settings);

            Assert.True(File.Exists(exportedPath));
            Assert.EndsWith(expectedExtension, exportedPath);
        }
        finally
        {
            if (Directory.Exists(tempExportDir)) Directory.Delete(tempExportDir, recursive: true);
        }
    }
}
