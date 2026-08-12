using System;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using CliWrap;

namespace CortexFlow.Infrastructure.Media;

public class AudioPreProcessor
{
    private readonly string _ffmpegPath;

    public AudioPreProcessor(string? ffmpegPath = null)
    {
        _ffmpegPath = ffmpegPath ?? FindFfmpegExecutable();
    }

    public async Task<string> ConvertTo16kHzWavAsync(string inputFilePath, CancellationToken cancellationToken = default)
    {
        if (!File.Exists(inputFilePath))
            throw new FileNotFoundException("Arquivo de entrada de mídia não encontrado.", inputFilePath);

        var tempWavPath = Path.Combine(Path.GetTempPath(), $"cortexflow_16k_{Guid.NewGuid():N}.wav");

        try
        {
            // Executa FFmpeg para converter qualquer áudio/vídeo para PCM 16kHz 16-bit mono WAV
            var result = await Cli.Wrap(_ffmpegPath)
                .WithArguments(new[]
                {
                    "-y",
                    "-i", inputFilePath,
                    "-ar", "16000",
                    "-ac", "1",
                    "-c:a", "pcm_s16le",
                    tempWavPath
                })
                .WithValidation(CommandResultValidation.None)
                .ExecuteAsync(cancellationToken);

            if (result.ExitCode != 0 || !File.Exists(tempWavPath))
            {
                // Se falhar a conversão do FFmpeg (ex: se FFmpeg não estiver no PATH), gera aviso gracioso
                throw new InvalidOperationException($"FFmpeg falhou ao converter a mídia. Código de saída: {result.ExitCode}");
            }

            return tempWavPath;
        }
        catch (Exception ex) when (ex is not InvalidOperationException and not OperationCanceledException)
        {
            throw new InvalidOperationException($"Erro ao invocar FFmpeg no caminho '{_ffmpegPath}'. Certifique-se de que o FFmpeg está instalado.", ex);
        }
    }

    private static string FindFfmpegExecutable()
    {
        // 1. Verifica no diretório bin/ local
        var localBinPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "ffmpeg.exe");
        if (File.Exists(localBinPath)) return localBinPath;

        var rootBinPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "..", "..", "..", "..", "bin", "ffmpeg.exe");
        if (File.Exists(rootBinPath)) return Path.GetFullPath(rootBinPath);

        // 2. Por padrão, usa 'ffmpeg' do PATH do Windows
        return "ffmpeg";
    }
}
