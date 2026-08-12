using System;
using System.IO;
using System.Linq;
using System.Windows;
using System.Windows.Controls;
using CortexFlow.Core.Models;
using CortexFlow.Core.Services;
using CortexFlow.Core.ViewModels;
using CortexFlow.Infrastructure.Extraction;
using CortexFlow.Infrastructure.Media;
using Microsoft.Win32;

namespace CortexFlow.UI;

public partial class MainWindow : Window
{
    private readonly MainViewModel _viewModel;
    private readonly CacheService _cacheService;
    private string? _customExportFolder;

    public MainWindow()
    {
        InitializeComponent();

        _cacheService = new CacheService();
        var exportService = new ExportService();
        var transcriptionService = new WhisperTranscriptionService();
        var queueManager = new QueueManager(transcriptionService, _cacheService, exportService);

        _viewModel = new MainViewModel(queueManager);
        DataContext = _viewModel;
        QueueDataGrid.ItemsSource = _viewModel.QueueItems;
    }

    private void SelectFiles_Click(object sender, RoutedEventArgs e)
    {
        var openFileDialog = new OpenFileDialog
        {
            Multiselect = true,
            Title = "Selecionar Arquivos para Transcrição e Extração",
            Filter = "Todos os Suportados (*.mp3;*.wav;*.mp4;*.mkv;*.pdf;*.docx;*.txt)|*.mp3;*.wav;*.mp4;*.mkv;*.pdf;*.docx;*.txt|Áudio e Vídeo (*.mp3;*.wav;*.mp4;*.mkv)|*.mp3;*.wav;*.mp4;*.mkv|Documentos (*.pdf;*.docx;*.txt)|*.pdf;*.docx;*.txt|Todos os Arquivos (*.*)|*.*"
        };

        if (openFileDialog.ShowDialog() == true)
        {
            _viewModel.AddFiles(openFileDialog.FileNames);
        }
    }

    private void SelectFolder_Click(object sender, RoutedEventArgs e)
    {
        var dialog = new OpenFolderDialog
        {
            Title = "Selecionar Pasta Inteira com Arquivos de Mídia"
        };

        if (dialog.ShowDialog() == true)
        {
            _viewModel.AddFolder(dialog.FolderName);
        }
    }

    private void RemoveSelected_Click(object sender, RoutedEventArgs e)
    {
        var selectedItems = QueueDataGrid.SelectedItems.Cast<QueueItem>().ToList();
        if (selectedItems.Any())
        {
            _viewModel.RemoveItems(selectedItems.Select(i => i.Id));
        }
    }

    private void RowRemoveItem_Click(object sender, RoutedEventArgs e)
    {
        if (sender is Button btn && btn.Tag is QueueItem item)
        {
            _viewModel.RemoveItem(item.Id);
        }
    }

    private void RowViewResult_Click(object sender, RoutedEventArgs e)
    {
        if (sender is Button btn && btn.Tag is QueueItem item && item.Result != null)
        {
            OpenResultWindow(item.Result);
        }
    }

    private void SelectExportFolder_Click(object sender, RoutedEventArgs e)
    {
        var dialog = new OpenFolderDialog
        {
            Title = "Selecionar Pasta de Saída dos Arquivos Exportados"
        };

        if (dialog.ShowDialog() == true)
        {
            _customExportFolder = dialog.FolderName;
            ExportPathText.Text = _customExportFolder;
        }
    }

    private void SameFolderCheck_Changed(object sender, RoutedEventArgs e)
    {
        if (CustomFolderGrid != null)
        {
            CustomFolderGrid.Visibility = (SameFolderCheck.IsChecked == true) ? Visibility.Collapsed : Visibility.Visible;
        }
    }

    private void OpenSettings_Click(object sender, RoutedEventArgs e)
    {
        var settingsWin = new SettingsWindow(_cacheService, _viewModel.Settings)
        {
            Owner = this
        };
        settingsWin.ShowDialog();
    }

    private void ViewResult_Click(object sender, RoutedEventArgs e)
    {
        var selectedItem = QueueDataGrid.SelectedItem as QueueItem;
        if (selectedItem?.Result != null)
        {
            OpenResultWindow(selectedItem.Result);
        }
        else
        {
            MessageBox.Show("Selecione um item concluído na fila para visualizar o resultado.", "CortexFlow", MessageBoxButton.OK, MessageBoxImage.Information);
        }
    }

    private void OpenResultWindow(TranscriptionResult result)
    {
        var folder = _viewModel.Settings.ExportToSourceFolder && !string.IsNullOrWhiteSpace(result.FilePath)
            ? Path.GetDirectoryName(result.FilePath)!
            : _viewModel.Settings.ExportDirectory;

        if (string.IsNullOrWhiteSpace(folder))
        {
            folder = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments), "CortexFlow_Exports");
        }

        var resultWin = new ResultWindow(result, folder)
        {
            Owner = this
        };
        resultWin.ShowDialog();
    }

    private void Window_DragOver(object sender, DragEventArgs e)
    {
        if (e.Data.GetDataPresent(DataFormats.FileDrop))
        {
            e.Effects = DragDropEffects.Copy;
        }
        else
        {
            e.Effects = DragDropEffects.None;
        }
        e.Handled = true;
    }

    private void Window_Drop(object sender, DragEventArgs e)
    {
        if (e.Data.GetDataPresent(DataFormats.FileDrop))
        {
            var dropped = (string[])e.Data.GetData(DataFormats.FileDrop);
            if (dropped != null && dropped.Length > 0)
            {
                foreach (var path in dropped)
                {
                    if (Directory.Exists(path))
                    {
                        _viewModel.AddFolder(path);
                    }
                    else if (File.Exists(path))
                    {
                        _viewModel.AddFiles(new[] { path });
                    }
                }
            }
        }
    }

    private async void StartQueue_Click(object sender, RoutedEventArgs e)
    {
        // 1. Modelo Whisper
        var selectedModel = (ModelCombo.SelectedItem as ComboBoxItem)?.Content.ToString() ?? "base";
        _viewModel.Settings.ModelSize = selectedModel.Split(' ')[0];

        // 2. Idioma
        var selectedLang = (LanguageCombo.SelectedItem as ComboBoxItem)?.Content.ToString() ?? "pt";
        _viewModel.Settings.Language = selectedLang.Contains("pt") ? "pt" : (selectedLang.Contains("en") ? "en" : "es");

        // 3. Modo de Estruturação
        var selectedMode = (StructuringCombo.SelectedItem as ComboBoxItem)?.Content.ToString() ?? "Clean";
        _viewModel.Settings.StructuringMode = selectedMode.Split(' ')[0];

        // 4. Formato de Exportação
        var selectedFormat = (FormatCombo.SelectedItem as ComboBoxItem)?.Content.ToString() ?? "md";
        _viewModel.Settings.ExportFormat = selectedFormat.Contains("pdf") ? "pdf" : (selectedFormat.Contains("json") ? "json" : (selectedFormat.Contains("txt") ? "txt" : "md"));

        // 5. Pasta de Exportação
        _viewModel.Settings.ExportToSourceFolder = SameFolderCheck.IsChecked ?? true;
        if (!string.IsNullOrWhiteSpace(_customExportFolder))
        {
            _viewModel.Settings.ExportDirectory = _customExportFolder;
        }

        // 6. Cache
        _viewModel.Settings.EnableCache = CacheCheck.IsChecked ?? true;

        await _viewModel.StartQueueAsync();
    }

    private void CancelQueue_Click(object sender, RoutedEventArgs e)
    {
        _viewModel.CancelQueue();
    }

    private void ClearQueue_Click(object sender, RoutedEventArgs e)
    {
        _viewModel.ClearQueue();
    }
}