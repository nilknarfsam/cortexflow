using System;
using System.IO;
using System.Linq;
using System.Windows;
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
    private string? _customExportFolder;

    public MainWindow()
    {
        InitializeComponent();

        var cacheService = new CacheService();
        var exportService = new ExportService();
        var transcriptionService = new WhisperTranscriptionService();
        var queueManager = new QueueManager(transcriptionService, cacheService, exportService);

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

    private void ViewResult_Click(object sender, RoutedEventArgs e)
    {
        var selectedItem = QueueDataGrid.SelectedItem as QueueItem;
        if (selectedItem?.Result != null)
        {
            var folder = _viewModel.Settings.ExportDirectory;
            if (string.IsNullOrWhiteSpace(folder))
            {
                folder = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments), "CortexFlow_Exports");
            }
            var resultWin = new ResultWindow(selectedItem.Result, folder)
            {
                Owner = this
            };
            resultWin.ShowDialog();
        }
        else
        {
            MessageBox.Show("Selecione um item concluído na fila para visualizar o resultado.", "CortexFlow", MessageBoxButton.OK, MessageBoxImage.Information);
        }
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
            var files = (string[])e.Data.GetData(DataFormats.FileDrop);
            if (files != null && files.Length > 0)
            {
                _viewModel.AddFiles(files);
            }
        }
    }

    private async void StartQueue_Click(object sender, RoutedEventArgs e)
    {
        // 1. Modelo Whisper
        var selectedModel = (ModelCombo.SelectedItem as System.Windows.Controls.ComboBoxItem)?.Content.ToString() ?? "base";
        _viewModel.Settings.ModelSize = selectedModel.Split(' ')[0];

        // 2. Idioma
        var selectedLang = (LanguageCombo.SelectedItem as System.Windows.Controls.ComboBoxItem)?.Content.ToString() ?? "pt";
        _viewModel.Settings.Language = selectedLang.Contains("pt") ? "pt" : (selectedLang.Contains("en") ? "en" : "es");

        // 3. Modo de Estruturação
        var selectedMode = (StructuringCombo.SelectedItem as System.Windows.Controls.ComboBoxItem)?.Content.ToString() ?? "Clean";
        _viewModel.Settings.StructuringMode = selectedMode.Split(' ')[0];

        // 4. Formato de Exportação
        var selectedFormat = (FormatCombo.SelectedItem as System.Windows.Controls.ComboBoxItem)?.Content.ToString() ?? "md";
        _viewModel.Settings.ExportFormat = selectedFormat.Contains("pdf") ? "pdf" : (selectedFormat.Contains("json") ? "json" : (selectedFormat.Contains("txt") ? "txt" : "md"));

        // 5. Pasta de Exportação
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
        _viewModel.QueueItems.Clear();
    }
}