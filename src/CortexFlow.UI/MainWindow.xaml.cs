using System;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Threading;
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
    private readonly DispatcherTimer _playerTimer;
    private string? _customExportFolder;
    private TranscriptionResult? _currentLoadedResult;
    private bool _autoScrollSyncEnabled = true;

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

        _viewModel.QueueItems.CollectionChanged += (s, e) => UpdateStatusBar();
        UpdateStatusBar();

        _playerTimer = new DispatcherTimer
        {
            Interval = TimeSpan.FromMilliseconds(250)
        };
        _playerTimer.Tick += PlayerTimer_Tick;

        KeyDown += MainWindow_KeyDown;
    }

    private void MainWindow_KeyDown(object sender, KeyEventArgs e)
    {
        if (e.Key == Key.F1)
        {
            OpenHelpWindow();
        }
    }

    private void UpdateStatusBar()
    {
        var count = _viewModel.QueueItems.Count;
        if (count == 0)
        {
            StatusItemCountText.Content = "Fila vazia. Arraste mídias ou clique em + Adicionar Arquivos.";
        }
        else
        {
            var completed = _viewModel.QueueItems.Count(i => i.Status == QueueItemStatus.Completed);
            var processing = _viewModel.QueueItems.Count(i => i.Status == QueueItemStatus.Processing);
            var queued = _viewModel.QueueItems.Count(i => i.Status == QueueItemStatus.Queued);
            StatusItemCountText.Content = $"Fila: {count} itens | Concluídos: {completed} | Em Processamento: {processing} | Na Fila: {queued}";
        }
    }

    // =========================================================================================
    // NAVEGAÇÃO E SELEÇÃO DE MÍDIA NO PLAYER (ABA 2)
    // =========================================================================================
    private void RowViewInPlayer_Click(object sender, RoutedEventArgs e)
    {
        if (sender is Button btn && btn.Tag is QueueItem item && item.Result != null)
        {
            LoadResultIntoPlayer(item.Result);
        }
    }

    private void QueueDataGrid_MouseDoubleClick(object sender, MouseButtonEventArgs e)
    {
        if (QueueDataGrid.SelectedItem is QueueItem item && item.Result != null)
        {
            LoadResultIntoPlayer(item.Result);
        }
    }

    private void LoadResultIntoPlayer(TranscriptionResult result)
    {
        _currentLoadedResult = result;

        PlayerMediaTitle.Text = $"📄 {Path.GetFileName(result.FilePath)}";
        PlayerMediaSubtitle.Text = $"Idioma: {result.Language} | Duração: {result.Duration:mm\\:ss}";

        PlayerResultTextBox.Text = result.FullText;
        PlayerTimestampsGrid.ItemsSource = result.Segments;

        try
        {
            if (!string.IsNullOrWhiteSpace(result.FilePath) && File.Exists(result.FilePath))
            {
                MainMediaPlayer.Source = new Uri(result.FilePath);
                PlayerStatusText.Text = "🎵 Mídia Carregada — Clique duplo na tabela para pular";
                PlayerStatusText.Foreground = System.Windows.Media.Brushes.MediumSeaGreen;
            }
            else
            {
                PlayerStatusText.Text = "⚠️ Arquivo de mídia original não encontrado no disco.";
                PlayerStatusText.Foreground = System.Windows.Media.Brushes.Orange;
            }
        }
        catch (Exception ex)
        {
            PlayerStatusText.Text = $"⚠️ Erro ao carregar player: {ex.Message}";
            PlayerStatusText.Foreground = System.Windows.Media.Brushes.IndianRed;
        }

        // Alterna para a Aba 2 (Visualizador & Player Sincronizado)
        MainTabControl.SelectedItem = PlayerTab;
    }

    // CLIQUE DUPLO OU CLIQUE NA TABELA SALTA PARA O INSTANTE EXATO DA FALA
    private void PlayerTimestampsGrid_MouseDoubleClick(object sender, MouseButtonEventArgs e)
    {
        if (PlayerTimestampsGrid.SelectedItem is TranscriptionSegment segment)
        {
            JumpToSegment(segment);
        }
    }

    private void PlayerTimestampsGrid_SelectionChanged(object sender, SelectionChangedEventArgs e)
    {
    }

    private void JumpToSegment(TranscriptionSegment segment)
    {
        try
        {
            _autoScrollSyncEnabled = true;
            MainMediaPlayer.Position = segment.Start;
            MainMediaPlayer.Play();
            _playerTimer.Start();
            PlayerStatusText.Text = $"▶ Reproduzindo em [{segment.Start:mm\\:ss}]";
            PlayerStatusText.Foreground = System.Windows.Media.Brushes.LightSkyBlue;
        }
        catch (Exception ex)
        {
            MessageBox.Show($"Não foi possível reproduzir neste ponto: {ex.Message}", "CortexFlow Player", MessageBoxButton.OK, MessageBoxImage.Warning);
        }
    }

    private void SyncButton_Click(object sender, RoutedEventArgs e)
    {
        _autoScrollSyncEnabled = true;
        SyncCurrentSegmentToVideo();
    }

    private void SyncCurrentSegmentToVideo()
    {
        if (_currentLoadedResult?.Segments == null || !MainMediaPlayer.NaturalDuration.HasTimeSpan) return;

        var pos = MainMediaPlayer.Position;
        var activeSegment = _currentLoadedResult.Segments.FirstOrDefault(s => s.Start <= pos && pos <= s.End);

        if (activeSegment != null)
        {
            PlayerTimestampsGrid.SelectedItem = activeSegment;
            PlayerTimestampsGrid.ScrollIntoView(activeSegment);
        }
    }

    private void PlayMedia_Click(object sender, RoutedEventArgs e)
    {
        try
        {
            MainMediaPlayer.Play();
            _playerTimer.Start();
            PlayerStatusText.Text = "▶ Reproduzindo Mídia";
            PlayerStatusText.Foreground = System.Windows.Media.Brushes.MediumSeaGreen;
        }
        catch (Exception ex)
        {
            MessageBox.Show($"Erro ao iniciar reprodução: {ex.Message}", "CortexFlow Player", MessageBoxButton.OK, MessageBoxImage.Warning);
        }
    }

    private void PauseMedia_Click(object sender, RoutedEventArgs e)
    {
        try
        {
            MainMediaPlayer.Pause();
            _playerTimer.Stop();
            PlayerStatusText.Text = "⏸ Reprodução Pausada";
            PlayerStatusText.Foreground = System.Windows.Media.Brushes.Orange;
        }
        catch { }
    }

    private void StopMedia_Click(object sender, RoutedEventArgs e)
    {
        try
        {
            MainMediaPlayer.Stop();
            _playerTimer.Stop();
            TimelineSlider.Value = 0;
            CurrentTimeText.Text = "00:00";
            PlayerStatusText.Text = "⏹ Reprodução Parada";
            PlayerStatusText.Foreground = System.Windows.Media.Brushes.SlateGray;
        }
        catch { }
    }

    private void MainMediaPlayer_MediaOpened(object sender, RoutedEventArgs e)
    {
        if (MainMediaPlayer.NaturalDuration.HasTimeSpan)
        {
            var duration = MainMediaPlayer.NaturalDuration.TimeSpan;
            TimelineSlider.Maximum = duration.TotalSeconds;
            TotalTimeText.Text = $"{duration:mm\\:ss}";
        }
    }

    private void MainMediaPlayer_MediaFailed(object sender, ExceptionRoutedEventArgs e)
    {
        PlayerStatusText.Text = $"⚠️ Formato de mídia não suportado nativamente pelo Windows Player.";
        PlayerStatusText.Foreground = System.Windows.Media.Brushes.IndianRed;
    }

    // TIMER EM TEMPO REAL: DESTACA E ROLA A TABELA AUTOMATICAMENTE CONFORME O VÍDEO RODA
    private void PlayerTimer_Tick(object? sender, EventArgs e)
    {
        if (MainMediaPlayer.NaturalDuration.HasTimeSpan)
        {
            TimelineSlider.Value = MainMediaPlayer.Position.TotalSeconds;
            CurrentTimeText.Text = $"{MainMediaPlayer.Position:mm\\:ss}";

            if (_autoScrollSyncEnabled)
            {
                SyncCurrentSegmentToVideo();
            }
        }
    }

    private void TimelineSlider_ValueChanged(object sender, RoutedPropertyChangedEventArgs<double> e)
    {
    }

    private void CopyPlayerText_Click(object sender, RoutedEventArgs e)
    {
        if (_currentLoadedResult != null)
        {
            Clipboard.SetText(_currentLoadedResult.FullText);
            MessageBox.Show("Texto da transcrição copiado para a área de transferência com sucesso!", "CortexFlow", MessageBoxButton.OK, MessageBoxImage.Information);
        }
    }

    private void OpenExportFolder_Click(object sender, RoutedEventArgs e)
    {
        var folder = _viewModel.Settings.ExportToSourceFolder && _currentLoadedResult != null && !string.IsNullOrWhiteSpace(_currentLoadedResult.FilePath)
            ? Path.GetDirectoryName(_currentLoadedResult.FilePath)!
            : _viewModel.Settings.ExportDirectory;

        if (string.IsNullOrWhiteSpace(folder))
        {
            folder = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments), "CortexFlow_Exports");
        }

        if (Directory.Exists(folder))
        {
            Process.Start("explorer.exe", folder);
        }
        else
        {
            MessageBox.Show("A pasta de exportação ainda não foi criada.", "CortexFlow", MessageBoxButton.OK, MessageBoxImage.Warning);
        }
    }

    // =========================================================================================
    // BARRA DE FERRAMENTAS E FILA (ABA 1)
    // =========================================================================================
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

    private async void ClearCacheMenu_Click(object sender, RoutedEventArgs e)
    {
        if (MessageBox.Show("Deseja apagar todo o cache SHA-256 de transcrições?", "CortexFlow", MessageBoxButton.YesNo, MessageBoxImage.Question) == MessageBoxResult.Yes)
        {
            await _cacheService.ClearCacheAsync();
            MessageBox.Show("Cache limpo com sucesso!", "CortexFlow", MessageBoxButton.OK, MessageBoxImage.Information);
        }
    }

    private void ExitMenu_Click(object sender, RoutedEventArgs e)
    {
        Close();
    }

    private void SwitchToQueueTab_Click(object sender, RoutedEventArgs e)
    {
        MainTabControl.SelectedIndex = 0;
    }

    private void SwitchToPlayerTab_Click(object sender, RoutedEventArgs e)
    {
        MainTabControl.SelectedIndex = 1;
    }

    private void DocumentationMenu_Click(object sender, RoutedEventArgs e)
    {
        OpenHelpWindow();
    }

    private void GitHubMenu_Click(object sender, RoutedEventArgs e)
    {
        try { Process.Start(new ProcessStartInfo("https://github.com/nilknarfsam/cortexflow") { UseShellExecute = true }); } catch { }
    }

    private void AboutMenu_Click(object sender, RoutedEventArgs e)
    {
        MessageBox.Show("CortexFlow v4.0 (.NET 9 / WinUI 3 Engine)\n\nTranscritor e Estúdio Profissional 100% Local e Offline.\nAutor: Franklin Carvalho (nilknarfsam)\nLicença: MIT License", "Sobre o CortexFlow", MessageBoxButton.OK, MessageBoxImage.Information);
    }

    private void OpenHelpWindow()
    {
        var helpWin = new HelpWindow
        {
            Owner = this
        };
        helpWin.ShowDialog();
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
        _viewModel.Settings.Language = selectedLang.Contains("pt") ? "pt" : (selectedLang.Contains("en") ? "en" : (selectedLang.Contains("es") ? "es" : "auto"));

        // 3. Tradução
        _viewModel.Settings.Translate = TranslateCheck.IsChecked ?? false;

        // 4. Modo de Estruturação
        var selectedMode = (StructuringCombo.SelectedItem as ComboBoxItem)?.Content.ToString() ?? "Clean";
        if (selectedMode.Contains("Time Blocks") || selectedMode.Contains("Blocos"))
        {
            _viewModel.Settings.StructuringMode = "TIME_BLOCKS";
        }
        else
        {
            _viewModel.Settings.StructuringMode = selectedMode.Split(' ')[0];
        }

        // 5. Formato de Exportação
        var selectedFormat = (FormatCombo.SelectedItem as ComboBoxItem)?.Content.ToString() ?? "md";
        _viewModel.Settings.ExportFormat = selectedFormat.Contains("pdf") ? "pdf" : (selectedFormat.Contains("json") ? "json" : (selectedFormat.Contains("txt") ? "txt" : "md"));

        // 6. Pasta de Exportação
        _viewModel.Settings.ExportToSourceFolder = SameFolderCheck.IsChecked ?? true;
        if (!string.IsNullOrWhiteSpace(_customExportFolder))
        {
            _viewModel.Settings.ExportDirectory = _customExportFolder;
        }

        // 7. Cache
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

    private void Window_Closed(object sender, EventArgs e)
    {
        try
        {
            _playerTimer.Stop();
            MainMediaPlayer.Stop();
            MainMediaPlayer.Close();
        }
        catch { }
    }
}