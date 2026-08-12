using System;
using System.IO;
using CortexFlow.Core.Models;
using CortexFlow.Core.Services;
using Xunit;

namespace CortexFlow.Core.Tests;

public class QueueManagerFolderTests
{
    [Fact]
    public void AddFolder_RecursivelyFindsSupportedFiles()
    {
        var tempDir = Path.Combine(Path.GetTempPath(), Guid.NewGuid().ToString());
        Directory.CreateDirectory(tempDir);
        var subDir = Path.Combine(tempDir, "sub");
        Directory.CreateDirectory(subDir);

        var file1 = Path.Combine(tempDir, "audio1.mp3");
        var file2 = Path.Combine(subDir, "video2.mp4");
        var fileIgnored = Path.Combine(tempDir, "document.exe");

        try
        {
            File.WriteAllText(file1, "audio content");
            File.WriteAllText(file2, "video content");
            File.WriteAllText(fileIgnored, "exe content");

            var cache = new CacheService(Path.Combine(tempDir, "cache"));
            var export = new ExportService();
            var mockTranscription = new MockTranscriptionService();
            var queueManager = new QueueManager(mockTranscription, cache, export);

            queueManager.AddFolder(tempDir, recursive: true);

            Assert.Equal(2, queueManager.Items.Count);
        }
        finally
        {
            if (Directory.Exists(tempDir)) Directory.Delete(tempDir, recursive: true);
        }
    }

    [Fact]
    public void RemoveItem_RemovesSpecificItemFromQueue()
    {
        var tempFile1 = Path.GetTempFileName() + ".mp3";
        var tempFile2 = Path.GetTempFileName() + ".mp4";

        try
        {
            File.WriteAllText(tempFile1, "audio 1");
            File.WriteAllText(tempFile2, "video 2");

            var cache = new CacheService(Path.Combine(Path.GetTempPath(), Guid.NewGuid().ToString()));
            var export = new ExportService();
            var mockTranscription = new MockTranscriptionService();
            var queueManager = new QueueManager(mockTranscription, cache, export);

            queueManager.AddFiles(new[] { tempFile1, tempFile2 });
            Assert.Equal(2, queueManager.Items.Count);

            var firstItemId = queueManager.Items[0].Id;
            queueManager.RemoveItem(firstItemId);

            Assert.Single(queueManager.Items);
            Assert.NotEqual(firstItemId, queueManager.Items[0].Id);
        }
        finally
        {
            if (File.Exists(tempFile1)) File.Delete(tempFile1);
            if (File.Exists(tempFile2)) File.Delete(tempFile2);
        }
    }
}
