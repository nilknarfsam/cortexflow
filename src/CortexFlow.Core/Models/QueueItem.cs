using System;

namespace CortexFlow.Core.Models;

public class QueueItem
{
    public string Id { get; set; } = Guid.NewGuid().ToString();
    public string FilePath { get; set; } = string.Empty;
    public string FileName => System.IO.Path.GetFileName(FilePath);
    public long FileSizeBytes { get; set; }
    public QueueItemStatus Status { get; set; } = QueueItemStatus.Queued;
    public double Progress { get; set; }
    public string? ErrorMessage { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public DateTime? CompletedAt { get; set; }
    public TranscriptionResult? Result { get; set; }
}
