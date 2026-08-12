using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using CortexFlow.Core.Abstractions;
using CortexFlow.Core.Models;

namespace CortexFlow.Core.Services;

public class QueueManager : IQueueManager
{
    private static readonly string[] SupportedExtensions = new[]
    {
        ".mp3", ".wav", ".mp4", ".mkv", ".avi", ".flac", ".m4a", ".aac",
        ".pdf", ".docx", ".txt", ".md", ".jpg", ".jpeg", ".png", ".tmp"
    };

    private readonly List<QueueItem> _items = new();
    private readonly ITranscriptionService _transcriptionService;
    private readonly ICacheService _cacheService;
    private readonly IExportService _exportService;
    private CancellationTokenSource? _cts;

    public IReadOnlyList<QueueItem> Items => _items.AsReadOnly();
    public event EventHandler<QueueItem>? ItemUpdated;

    public QueueManager(
        ITranscriptionService transcriptionService, 
        ICacheService cacheService, 
        IExportService exportService)
    {
        _transcriptionService = transcriptionService;
        _cacheService = cacheService;
        _exportService = exportService;
    }

    public void AddFiles(IEnumerable<string> filePaths)
    {
        foreach (var path in filePaths)
        {
            if (!File.Exists(path)) continue;
            var ext = Path.GetExtension(path).ToLowerInvariant();
            if (!SupportedExtensions.Contains(ext)) continue;

            // Evita duplicados na fila
            if (_items.Any(i => i.FilePath.Equals(path, StringComparison.OrdinalIgnoreCase))) continue;

            var fileInfo = new FileInfo(path);
            var item = new QueueItem
            {
                FilePath = path,
                FileSizeBytes = fileInfo.Length,
                Status = QueueItemStatus.Queued
            };
            
            _items.Add(item);
            OnItemUpdated(item);
        }
    }

    public void AddFolder(string folderPath, bool recursive = true)
    {
        if (!Directory.Exists(folderPath)) return;

        var option = recursive ? SearchOption.AllDirectories : SearchOption.TopDirectoryOnly;
        var files = Directory.GetFiles(folderPath, "*.*", option)
            .Where(f => SupportedExtensions.Contains(Path.GetExtension(f).ToLowerInvariant()));

        AddFiles(files);
    }

    public void RemoveItem(string itemId)
    {
        var item = _items.FirstOrDefault(i => i.Id == itemId);
        if (item != null)
        {
            _items.Remove(item);
            OnItemUpdated(item);
        }
    }

    public void RemoveItems(IEnumerable<string> itemIds)
    {
        var idsToRemove = itemIds.ToList();
        var itemsToRemove = _items.Where(i => idsToRemove.Contains(i.Id)).ToList();
        foreach (var item in itemsToRemove)
        {
            _items.Remove(item);
            OnItemUpdated(item);
        }
    }

    public void ClearQueue()
    {
        _items.Clear();
    }

    public async Task StartProcessingAsync(JobSettings settings, CancellationToken cancellationToken = default)
    {
        _cts = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);
        var token = _cts.Token;

        var queuedItems = _items.Where(i => i.Status == QueueItemStatus.Queued).ToList();

        foreach (var item in queuedItems)
        {
            if (token.IsCancellationRequested)
            {
                item.Status = QueueItemStatus.Cancelled;
                OnItemUpdated(item);
                continue;
            }

            try
            {
                item.Status = QueueItemStatus.Processing;
                item.Progress = 0.1;
                OnItemUpdated(item);

                // 1. Verificação de Cache
                var hash = await _cacheService.ComputeHashAsync(item.FilePath);
                TranscriptionResult? result = null;

                if (settings.EnableCache)
                {
                    result = await _cacheService.GetCachedResultAsync(hash);
                }

                if (result != null)
                {
                    result.FromCache = true;
                    item.Progress = 0.9;
                }
                else
                {
                    // 2. Transcrição / Extração Real
                    var progressReporter = new Progress<double>(p =>
                    {
                        item.Progress = 0.1 + (p * 0.7);
                        OnItemUpdated(item);
                    });

                    result = await _transcriptionService.TranscribeAsync(item.FilePath, settings, progressReporter, token);
                    result.ContentHash = hash;

                    if (settings.EnableCache)
                    {
                        await _cacheService.SaveCacheResultAsync(hash, result);
                    }
                }

                // 3. Exportação
                var exportedPath = await _exportService.ExportAsync(result, settings);

                item.Result = result;
                item.Progress = 1.0;
                item.Status = QueueItemStatus.Completed;
                item.ErrorMessage = $"Salvo: {Path.GetFileName(exportedPath)}";
                item.CompletedAt = DateTime.UtcNow;
            }
            catch (OperationCanceledException)
            {
                item.Status = QueueItemStatus.Cancelled;
            }
            catch (Exception ex)
            {
                item.Status = QueueItemStatus.Failed;
                item.ErrorMessage = ex.Message;
            }

            OnItemUpdated(item);
        }
    }

    public void CancelProcessing()
    {
        _cts?.Cancel();
    }

    protected virtual void OnItemUpdated(QueueItem item)
    {
        ItemUpdated?.Invoke(this, item);
    }
}
