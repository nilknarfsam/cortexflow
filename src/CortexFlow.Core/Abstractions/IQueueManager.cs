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
    void RemoveItem(string itemId);
    void ClearQueue();
    Task StartProcessingAsync(JobSettings settings, CancellationToken cancellationToken = default);
    void CancelProcessing();
}
