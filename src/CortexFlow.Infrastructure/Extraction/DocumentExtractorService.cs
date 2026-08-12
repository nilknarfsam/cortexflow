using System;
using System.IO;
using System.Text;
using System.Threading.Tasks;
using DocumentFormat.OpenXml.Packaging;
using UglyToad.PdfPig;

namespace CortexFlow.Infrastructure.Extraction;

public class DocumentExtractorService
{
    public async Task<string> ExtractTextAsync(string filePath)
    {
        if (!File.Exists(filePath))
            throw new FileNotFoundException("Arquivo de documento não encontrado.", filePath);

        var extension = Path.GetExtension(filePath).ToLowerInvariant();

        return extension switch
        {
            ".pdf" => ExtractFromPdf(filePath),
            ".docx" => ExtractFromDocx(filePath),
            ".txt" or ".md" => await File.ReadAllTextAsync(filePath, Encoding.UTF8),
            _ => throw new NotSupportedException($"Formato de documento não suportado: {extension}")
        };
    }

    private static string ExtractFromPdf(string pdfPath)
    {
        var sb = new StringBuilder();
        using var pdf = PdfDocument.Open(pdfPath);
        foreach (var page in pdf.GetPages())
        {
            sb.AppendLine(page.Text);
        }
        return sb.ToString();
    }

    private static string ExtractFromDocx(string docxPath)
    {
        using var doc = WordprocessingDocument.Open(docxPath, false);
        var mainPart = doc.MainDocumentPart;
        if (mainPart?.Document?.Body == null) return string.Empty;
        return mainPart.Document.Body.InnerText ?? string.Empty;
    }
}
