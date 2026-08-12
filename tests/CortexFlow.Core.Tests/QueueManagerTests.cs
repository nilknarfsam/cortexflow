using System;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using CortexFlow.Core.Abstractions;
using CortexFlow.Core.Models;
using CortexFlow.Core.Services;
using Xunit;

namespace CortexFlow.Core.Tests;

public class MockTranscriptionService : ITranscriptionService
{
    public Task<TranscriptionResult> TranscribeAsync(
        string audioOrVideoPath, 
        JobSettings settings, 
        IProgress<double>? progress = null, 
        CancellationToken cancellationToken = default)
    {
        progress?.Report(1.0);
        return Task.FromResult(new TranscriptionResult
        {
            FilePath = audioOrVideoPath,
            FullText = "Transcrição simulada com sucesso.",
            Language = settings.Language,
            Duration = TimeSpan.FromSeconds(30)
        });
    }
}

public class QueueManagerTests
{
    [Fact]
    public async Task AddFilesAndProcess_CompletesQueueSuccessfully()
    {
        var tempFile = Path.GetTempFileName();
        var tempCacheDir = Path.Combine(Path.GetTempPath(), Guid.NewGuid().ToString());
        var tempExportDir = Path.Combine(Path.GetTempPath(), Guid.NewGuid().ToString());

        try
        {
            await File.WriteAllTextAsync(tempFile, "Fila de teste C#");
            var cacheService = new CacheService(tempCacheDir);
            var exportService = new ExportService();
            var mockTranscription = new MockTranscriptionService();

            var queueManager = new QueueManager(mockTranscription, cacheService, exportService);
            queueManager.AddFiles(new[] { tempFile });

            Assert.Single(queueManager.Items);
            Assert.Equal(QueueItemStatus.Queued, queueManager.Items[0].Status);

            var settings = new JobSettings
            {
                ExportDirectory = tempExportDir,
                StructuringMode = "Clean",
                ExportFormat = "md"
            };

            await queueManager.StartProcessingAsync(settings);

            Assert.Equal(QueueItemStatus.Completed, queueManager.Items[0].Status);
            Assert.NotNull(queueManager.Items[0].Result);
            Assert.Equal("Transcrição simulada com sucesso.", queueManager.Items[0].Result!.FullText);
        }
        finally
        {
            if (File.Exists(tempFile)) File.Delete(tempFile);
            if (Directory.Exists(tempCacheDir)) Directory.Delete(tempCacheDir, recursive: true);
            if (Directory.Exists(tempExportDir)) Directory.Delete(tempExportDir, recursive: true);
        }
    }
}
