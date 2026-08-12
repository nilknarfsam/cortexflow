using System;
using System.Diagnostics;
using System.IO;
using System.Windows;
using CortexFlow.Core.Models;

namespace CortexFlow.UI;

public partial class ResultWindow : Window
{
    private readonly TranscriptionResult _result;
    private readonly string _exportDirectory;

    public ResultWindow(TranscriptionResult result, string exportDirectory)
    {
        InitializeComponent();
        _result = result;
        _exportDirectory = exportDirectory;

        TitleText.Text = $"📄 {Path.GetFileName(_result.FilePath)}";
        SubtitleText.Text = $"Idioma: {_result.Language} | Duração: {_result.Duration:g}";

        ResultTextBox.Text = _result.FullText;
        TimestampsGrid.ItemsSource = _result.Segments;
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
}
