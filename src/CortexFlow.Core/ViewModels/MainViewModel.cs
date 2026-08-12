using System;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Runtime.CompilerServices;
using System.Threading.Tasks;
using CortexFlow.Core.Abstractions;
using CortexFlow.Core.Models;

namespace CortexFlow.Core.ViewModels;

public class MainViewModel : INotifyPropertyChanged
{
    private readonly IQueueManager _queueManager;
    private JobSettings _settings = new();

    public ObservableCollection<QueueItem> QueueItems { get; } = new();
    public JobSettings Settings
    {
        get => _settings;
        set { _settings = value; OnPropertyChanged(); }
    }

    public event PropertyChangedEventHandler? PropertyChanged;

    public MainViewModel(IQueueManager queueManager)
    {
        _queueManager = queueManager;
        _queueManager.ItemUpdated += OnQueueItemUpdated;
    }

    public void AddFiles(string[] filePaths)
    {
        _queueManager.AddFiles(filePaths);
        RefreshQueue();
    }

    public async Task StartQueueAsync()
    {
        await _queueManager.StartProcessingAsync(Settings);
    }

    public void CancelQueue()
    {
        _queueManager.CancelProcessing();
    }

    private void RefreshQueue()
    {
        QueueItems.Clear();
        foreach (var item in _queueManager.Items)
        {
            QueueItems.Add(item);
        }
    }

    private void OnQueueItemUpdated(object? sender, QueueItem item)
    {
        RefreshQueue();
    }

    protected virtual void OnPropertyChanged([CallerMemberName] string? propertyName = null)
    {
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
    }
}
