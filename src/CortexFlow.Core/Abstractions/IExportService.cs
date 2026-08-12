using System.Threading.Tasks;
using CortexFlow.Core.Models;

namespace CortexFlow.Core.Abstractions;

public interface IExportService
{
    Task<string> ExportAsync(TranscriptionResult result, JobSettings settings);
}
