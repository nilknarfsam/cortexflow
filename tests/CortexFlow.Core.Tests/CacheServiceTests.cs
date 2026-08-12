using System;
using System.IO;
using System.Threading.Tasks;
using CortexFlow.Core.Models;
using CortexFlow.Core.Services;
using Xunit;

namespace CortexFlow.Core.Tests;

public class CacheServiceTests
{
    [Fact]
    public async Task ComputeHashAsync_CalculatesCorrectSha256()
    {
        var tempFile = Path.GetTempFileName();
        try
        {
            await File.WriteAllTextAsync(tempFile, "CortexFlow Test Content");
            var service = new CacheService(Path.Combine(Path.GetTempPath(), "CortexFlowTestCache"));
            
            var hash = await service.ComputeHashAsync(tempFile);
            
            Assert.NotNull(hash);
            Assert.Equal(64, hash.Length); // SHA-256 string hexadecimal de 64 caracteres
        }
        finally
        {
            if (File.Exists(tempFile)) File.Delete(tempFile);
        }
    }

    [Fact]
    public async Task SaveAndGetCachedResult_StoresAndRetrievesData()
    {
        var tempCacheDir = Path.Combine(Path.GetTempPath(), Guid.NewGuid().ToString());
        var service = new CacheService(tempCacheDir);
        var testHash = "abcd1234efgh5678abcd1234efgh5678abcd1234efgh5678abcd1234efgh5678";

        var expectedResult = new TranscriptionResult
        {
            FilePath = "test_audio.mp3",
            FullText = "Transcrição de teste para validação de cache.",
            Language = "pt",
            Duration = TimeSpan.FromMinutes(2)
        };

        try
        {
            await service.SaveCacheResultAsync(testHash, expectedResult);
            var retrieved = await service.GetCachedResultAsync(testHash);

            Assert.NotNull(retrieved);
            Assert.Equal(expectedResult.FullText, retrieved.FullText);
            Assert.Equal(expectedResult.Language, retrieved.Language);
        }
        finally
        {
            if (Directory.Exists(tempCacheDir)) Directory.Delete(tempCacheDir, recursive: true);
        }
    }
}
