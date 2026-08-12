using System.IO;
using System.Threading.Tasks;
using CortexFlow.Core.Models;
using CortexFlow.Core.Services;
using CortexFlow.Core.ViewModels;
using Xunit;

namespace CortexFlow.Core.Tests;

public class MainViewModelTests
{
    [Fact]
    public async Task MainViewModel_AddsFilesAndProcessesQueue()
    {
        var tempFile = Path.GetTempFileName();
        var tempCacheDir = Path.Combine(Path.GetTempPath(), System.Guid.NewGuid().ToString());
        var tempExportDir = Path.Combine(Path.GetTempPath(), System.Guid.NewGuid().ToString());

        try
        {
            await File.WriteAllTextAsync(tempFile, "Teste MVVM MainViewModel");
            var cache = new CacheService(tempCacheDir);
            var export = new ExportService();
            var mockTranscription = new MockTranscriptionService();
            var queueManager = new QueueManager(mockTranscription, cache, export);

            var viewModel = new MainViewModel(queueManager);
            viewModel.AddFiles(new[] { tempFile });

            Assert.Single(viewModel.QueueItems);

            viewModel.Settings.ExportDirectory = tempExportDir;
            await viewModel.StartQueueAsync();

            Assert.Equal(QueueItemStatus.Completed, viewModel.QueueItems[0].Status);
        }
        finally
        {
            if (File.Exists(tempFile)) File.Delete(tempFile);
            if (Directory.Exists(tempCacheDir)) Directory.Delete(tempCacheDir, recursive: true);
            if (Directory.Exists(tempExportDir)) Directory.Delete(tempExportDir, recursive: true);
        }
    }
}
