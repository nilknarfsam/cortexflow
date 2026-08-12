using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using CortexFlow.Core.Models;

namespace CortexFlow.Core.Abstractions;

public interface IQueueManager
{
    IReadOnlyList<QueueItem> Items { get; }
    event EventHandler<QueueItem>? ItemUpdated;
    
    void AddFiles(IEnumerable<string> filePaths);
    void AddFolder(string folderPath, bool recursive = true);
    void RemoveItem(string itemId);
    void RemoveItems(IEnumerable<string> itemIds);
    void ClearQueue();
    Task StartProcessingAsync(JobSettings settings, CancellationToken cancellationToken = default);
    void CancelProcessing();
}
