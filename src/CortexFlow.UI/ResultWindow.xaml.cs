using System;
using System.Diagnostics;
using System.IO;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Threading;
using CortexFlow.Core.Models;

namespace CortexFlow.UI;

public partial class ResultWindow : Window
{
    private readonly TranscriptionResult _result;
    private readonly string _exportDirectory;
    private readonly DispatcherTimer _timer;
    private bool _isUserDraggingSlider;

    public ResultWindow(TranscriptionResult result, string exportDirectory)
    {
        InitializeComponent();
        _result = result;
        _exportDirectory = exportDirectory;

        TitleText.Text = $"📄 {Path.GetFileName(_result.FilePath)}";
        SubtitleText.Text = $"Idioma: {_result.Language} | Duração: {_result.Duration:mm\\:ss}";

        ResultTextBox.Text = _result.FullText;
        TimestampsGrid.ItemsSource = _result.Segments;

        // Configuração do Timer para atualizar o Slider do Player a cada 250ms
        _timer = new DispatcherTimer
        {
            Interval = TimeSpan.FromMilliseconds(250)
        };
        _timer.Tick += Timer_Tick;

        // Carregar Mídia no Player se o arquivo existir
        InitializeMediaPlayer();
    }

    private void InitializeMediaPlayer()
    {
        try
        {
            if (!string.IsNullOrWhiteSpace(_result.FilePath) && File.Exists(_result.FilePath))
            {
                MediaPlayer.Source = new Uri(_result.FilePath);
                PlayerStatusText.Text = "🎵 Mídia Pronta para Reprodução";
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
    }

    private void JumpToTimestamp_Click(object sender, RoutedEventArgs e)
    {
        if (sender is Button btn && btn.Tag is TranscriptionSegment segment)
        {
            try
            {
                MediaPlayer.Position = segment.Start;
                MediaPlayer.Play();
                _timer.Start();
                PlayerStatusText.Text = $"▶ Reproduzindo em [{segment.Start:mm\\:ss}]";
                PlayerStatusText.Foreground = System.Windows.Media.Brushes.LightSkyBlue;
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Não foi possível reproduzir neste ponto: {ex.Message}", "CortexFlow Player", MessageBoxButton.OK, MessageBoxImage.Warning);
            }
        }
    }

    private void PlayMedia_Click(object sender, RoutedEventArgs e)
    {
        try
        {
            MediaPlayer.Play();
            _timer.Start();
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
            MediaPlayer.Pause();
            _timer.Stop();
            PlayerStatusText.Text = "⏸ Reprodução Pausada";
            PlayerStatusText.Foreground = System.Windows.Media.Brushes.Orange;
        }
        catch { }
    }

    private void StopMedia_Click(object sender, RoutedEventArgs e)
    {
        try
        {
            MediaPlayer.Stop();
            _timer.Stop();
            TimelineSlider.Value = 0;
            CurrentTimeText.Text = "00:00";
            PlayerStatusText.Text = "⏹ Reprodução Parada";
            PlayerStatusText.Foreground = System.Windows.Media.Brushes.SlateGray;
        }
        catch { }
    }

    private void MediaPlayer_MediaOpened(object sender, RoutedEventArgs e)
    {
        if (MediaPlayer.NaturalDuration.HasTimeSpan)
        {
            var duration = MediaPlayer.NaturalDuration.TimeSpan;
            TimelineSlider.Maximum = duration.TotalSeconds;
            TotalTimeText.Text = $"{duration:mm\\:ss}";
        }
    }

    private void MediaPlayer_MediaFailed(object sender, ExceptionRoutedEventArgs e)
    {
        PlayerStatusText.Text = $"⚠️ Formato de mídia não suportado nativamente pelo player Windows.";
        PlayerStatusText.Foreground = System.Windows.Media.Brushes.IndianRed;
    }

    private void Timer_Tick(object? sender, EventArgs e)
    {
        if (!_isUserDraggingSlider && MediaPlayer.NaturalDuration.HasTimeSpan)
        {
            TimelineSlider.Value = MediaPlayer.Position.TotalSeconds;
            CurrentTimeText.Text = $"{MediaPlayer.Position:mm\\:ss}";
        }
    }

    private void TimelineSlider_ValueChanged(object sender, RoutedPropertyChangedEventArgs<double> e)
    {
        if (_isUserDraggingSlider && MediaPlayer.NaturalDuration.HasTimeSpan)
        {
            MediaPlayer.Position = TimeSpan.FromSeconds(TimelineSlider.Value);
            CurrentTimeText.Text = $"{MediaPlayer.Position:mm\\:ss}";
        }
    }

    private void Copy_Click(object sender, RoutedEventArgs e)
    {
        Clipboard.SetText(_result.FullText);
        MessageBox.Show("Texto copiado para a área de transferência com sucesso!", "CortexFlow", MessageBoxButton.OK, MessageBoxImage.Information);
    }

    private void OpenFolder_Click(object sender, RoutedEventArgs e)
    {
        if (Directory.Exists(_exportDirectory))
        {
            Process.Start("explorer.exe", _exportDirectory);
        }
        else
        {
            MessageBox.Show("A pasta de exportação ainda não foi criada.", "CortexFlow", MessageBoxButton.OK, MessageBoxImage.Warning);
        }
    }

    private void Close_Click(object sender, RoutedEventArgs e)
    {
        Close();
    }

    private void Window_Closed(object sender, EventArgs e)
    {
        try
        {
            _timer.Stop();
            MediaPlayer.Stop();
            MediaPlayer.Close();
        }
        catch { }
    }
}
