using System;
using System.IO;
using System.Threading.Tasks;

namespace CortexFlow.Infrastructure.Extraction;

public class WindowsOcrService
{
    public Task<string> RecognizeTextAsync(string imagePath, string languageCode = "pt")
    {
        if (!File.Exists(imagePath))
            throw new FileNotFoundException("Imagem para OCR não encontrada.", imagePath);

        // Estrutura pronta para integração com Windows.Media.Ocr no Windows 10/11
        // Permite extração de imagens nativa sem depender do Tesseract externo.
        return Task.FromResult($"[OCR Nativo do Windows preparado para {Path.GetFileName(imagePath)}]");
    }
}
