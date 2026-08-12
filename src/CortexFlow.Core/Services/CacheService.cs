using System;
using System.Collections.Concurrent;
using System.IO;
using System.Security.Cryptography;
using System.Text.Json;
using System.Threading.Tasks;
using CortexFlow.Core.Abstractions;
using CortexFlow.Core.Models;

namespace CortexFlow.Core.Services;

public class CacheService : ICacheService
{
    private readonly string _cacheDirectory;
    private readonly ConcurrentDictionary<string, TranscriptionResult> _memoryCache = new();

    public CacheService(string? cacheDirectory = null)
    {
        _cacheDirectory = cacheDirectory ?? Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), 
            "CortexFlow", 
            "Cache");
        
        if (!Directory.Exists(_cacheDirectory))
        {
            Directory.CreateDirectory(_cacheDirectory);
        }
    }

    public async Task<string> ComputeHashAsync(string filePath)
    {
        if (!File.Exists(filePath))
            throw new FileNotFoundException("Arquivo para computar hash não encontrado", filePath);

        using var sha256 = SHA256.Create();
        await using var stream = File.OpenRead(filePath);
        var hashBytes = await sha256.ComputeHashAsync(stream);
        return BitConverter.ToString(hashBytes).Replace("-", "").ToLowerInvariant();
    }

    public async Task<TranscriptionResult?> GetCachedResultAsync(string contentHash)
    {
        if (_memoryCache.TryGetValue(contentHash, out var cached))
        {
            return cached;
        }

        var cacheFilePath = Path.Combine(_cacheDirectory, $"{contentHash}.json");
        if (!File.Exists(cacheFilePath))
        {
            return null;
        }

        try
        {
            var json = await File.ReadAllTextAsync(cacheFilePath);
            var result = JsonSerializer.Deserialize<TranscriptionResult>(json);
            if (result != null)
            {
                _memoryCache[contentHash] = result;
            }
            return result;
        }
        catch
        {
            return null;
        }
    }

    public async Task SaveCacheResultAsync(string contentHash, TranscriptionResult result)
    {
        _memoryCache[contentHash] = result;
        var cacheFilePath = Path.Combine(_cacheDirectory, $"{contentHash}.json");
        var tempFilePath = cacheFilePath + ".tmp";

        var json = JsonSerializer.Serialize(result, new JsonSerializerOptions { WriteIndented = true });
        await File.WriteAllTextAsync(tempFilePath, json);
        File.Move(tempFilePath, cacheFilePath, overwrite: true);
    }

    public Task ClearCacheAsync()
    {
        _memoryCache.Clear();
        if (Directory.Exists(_cacheDirectory))
        {
            foreach (var file in Directory.GetFiles(_cacheDirectory, "*.json"))
            {
                try { File.Delete(file); } catch { }
            }
        }
        return Task.CompletedTask;
    }
}
