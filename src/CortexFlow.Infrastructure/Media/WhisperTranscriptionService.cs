using System;
using System.IO;
using System.Net.Http;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using CortexFlow.Core.Abstractions;
using CortexFlow.Core.Models;
using Whisper.net;
using Whisper.net.Ggml;

namespace CortexFlow.Infrastructure.Media;

public class WhisperTranscriptionService : ITranscriptionService
{
    private readonly string _modelsDirectory;

    public WhisperTranscriptionService(string? modelsDirectory = null)
    {
        _modelsDirectory = modelsDirectory ?? Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
            "CortexFlow",
            "Models");

        if (!Directory.Exists(_modelsDirectory))
        {
            Directory.CreateDirectory(_modelsDirectory);
        }
    }

    public async Task<TranscriptionResult> TranscribeAsync(
        string audioOrVideoPath,
        JobSettings settings,
        IProgress<double>? progress = null,
        CancellationToken cancellationToken = default)
    {
        if (!File.Exists(audioOrVideoPath))
        {
            throw new FileNotFoundException("Arquivo de áudio ou vídeo não encontrado.", audioOrVideoPath);
        }

        // 1. Obter ou Baixar Modelo GGML
        var modelPath = Path.Combine(_modelsDirectory, $"ggml-{settings.ModelSize.ToLowerInvariant()}.bin");
        if (!File.Exists(modelPath))
        {
            progress?.Report(0.05);
            var ggmlType = settings.ModelSize.ToLowerInvariant() switch
            {
                "tiny" => GgmlType.Tiny,
                "small" => GgmlType.Small,
                "medium" => GgmlType.Medium,
                "large" or "large-v3" => GgmlType.LargeV3,
                _ => GgmlType.Base
            };

            using var httpClient = new HttpClient();
            var downloader = new WhisperGgmlDownloader(httpClient);
            using var modelStream = await downloader.GetGgmlModelAsync(ggmlType, cancellationToken: cancellationToken);
            using var fileStream = File.Create(modelPath);
            await modelStream.CopyToAsync(fileStream, cancellationToken);
        }

        // 2. Carregar Fábrica do Whisper
        using var factory = WhisperFactory.FromPath(modelPath);
        using var processor = factory.CreateBuilder()
            .WithLanguage(settings.Language)
            .Build();

        // 3. Processar Áudio
        await using var audioStream = File.OpenRead(audioOrVideoPath);
        var result = new TranscriptionResult
        {
            FilePath = audioOrVideoPath,
            Language = settings.Language
        };

        var fullTextBuilder = new StringBuilder();

        await foreach (var segment in processor.ProcessAsync(audioStream, cancellationToken))
        {
            fullTextBuilder.Append(segment.Text);

            result.Segments.Add(new TranscriptionSegment
            {
                Start = segment.Start,
                End = segment.End,
                Text = segment.Text
            });

            progress?.Report(0.1 + (segment.End.TotalSeconds / 300.0 * 0.8));
        }

        result.FullText = fullTextBuilder.ToString().Trim();
        return result;
    }
}
