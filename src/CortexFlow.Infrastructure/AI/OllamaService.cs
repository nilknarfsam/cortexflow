using System;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

namespace CortexFlow.Infrastructure.AI;

public class OllamaService
{
    private static readonly HttpClient _httpClient = new HttpClient
    {
        BaseAddress = new Uri("http://localhost:11434/"),
        Timeout = TimeSpan.FromSeconds(3)
    };

    public async Task<bool> IsOllamaAvailableAsync()
    {
        try
        {
            var response = await _httpClient.GetAsync("api/tags");
            return response.IsSuccessStatusCode;
        }
        catch
        {
            return false;
        }
    }

    public async Task<string> GenerateSummaryAsync(string textContent, string model = "llama3")
    {
        try
        {
            var prompt = $"Resuma em português os pontos principais do seguinte texto transcrito:\n\n{textContent}";
            var payload = new
            {
                model = model,
                prompt = prompt,
                stream = false
            };

            var jsonPayload = JsonSerializer.Serialize(payload);
            var content = new StringContent(jsonPayload, Encoding.UTF8, "application/json");

            var response = await _httpClient.PostAsync("api/generate", content);
            if (!response.IsSuccessStatusCode)
            {
                return "⚠️ O Ollama local não retornou uma resposta válida.";
            }

            var responseBody = await response.Content.ReadAsStringAsync();
            using var doc = JsonDocument.Parse(responseBody);
            if (doc.RootElement.TryGetProperty("response", out var respProp))
            {
                return respProp.GetString() ?? "Sem resposta.";
            }

            return "Resposta gerada.";
        }
        catch (Exception ex)
        {
            return $"⚠️ Erro ao conectar ao Ollama local (100% Offline): {ex.Message}";
        }
    }
}
