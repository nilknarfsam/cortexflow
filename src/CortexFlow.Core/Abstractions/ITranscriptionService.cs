using System;
using System.Threading;
using System.Threading.Tasks;
using CortexFlow.Core.Models;

namespace CortexFlow.Core.Abstractions;

public interface ITranscriptionService
{
    Task<TranscriptionResult> TranscribeAsync(
        string audioOrVideoPath, 
        JobSettings settings, 
        IProgress<double>? progress = null, 
        CancellationToken cancellationToken = default);
}
