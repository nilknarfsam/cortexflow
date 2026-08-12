using System.Threading.Tasks;
using CortexFlow.Core.Models;

namespace CortexFlow.Core.Abstractions;

public interface ICacheService
{
    Task<string> ComputeHashAsync(string filePath);
    Task<TranscriptionResult?> GetCachedResultAsync(string contentHash);
    Task SaveCacheResultAsync(string contentHash, TranscriptionResult result);
    Task ClearCacheAsync();
}
