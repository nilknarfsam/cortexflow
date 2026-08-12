using System;
using System.IO;
using System.Threading.Tasks;
using CortexFlow.Infrastructure.Extraction;
using Xunit;

namespace CortexFlow.Core.Tests;

public class DocumentExtractorTests
{
    [Fact]
    public async Task ExtractTextAsync_ReadsTxtFileSuccessfully()
    {
        var tempFile = Path.GetTempFileName() + ".txt";
        var expectedText = "Texto de teste para validação de extração em C#.";

        try
        {
            await File.WriteAllTextAsync(tempFile, expectedText);
            var extractor = new DocumentExtractorService();
            var extracted = await extractor.ExtractTextAsync(tempFile);

            Assert.Equal(expectedText, extracted);
        }
        finally
        {
            if (File.Exists(tempFile)) File.Delete(tempFile);
        }
    }
}
