using System;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Threading.Tasks;

namespace CortexFlow.Infrastructure.Diagnostics;

public class SystemPerformanceService
{
    public static async Task<string> GetSystemStatusSummaryAsync()
    {
        return await Task.Run(() =>
        {
            try
            {
                var cores = Environment.ProcessorCount;
                var proc = Process.GetCurrentProcess();
                var ramMb = proc.WorkingSet64 / (1024 * 1024);

                return $"⚡ Acelerador Local (Whisper.net Engine - {cores} Cores) | 🧠 RAM App: {ramMb} MB | 🔒 100% Offline";
            }
            catch
            {
                return "⚡ Processamento Local (Whisper.net Engine) | 🔒 100% Offline";
            }
        });
    }
}
