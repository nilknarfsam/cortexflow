using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;
using CortexFlow.Core.Models;

namespace CortexFlow.Core.Domains;

public class TopicCluster
{
    public string TopicName { get; set; } = string.Empty;
    public List<TranscriptionSegment> Segments { get; set; } = new();
}

public class SemanticEngine
{
    public List<TopicCluster> ExtractTopics(TranscriptionResult result)
    {
        var clusters = new List<TopicCluster>();
        if (result.Segments == null || !result.Segments.Any()) return clusters;

        // Agrupa segmentos a cada ~2 minutos ou por frases chave
        var currentCluster = new TopicCluster { TopicName = "Tópico Inicial" };
        var groupDuration = TimeSpan.Zero;

        foreach (var seg in result.Segments)
        {
            currentCluster.Segments.Add(seg);
            groupDuration += (seg.End - seg.Start);

            if (groupDuration >= TimeSpan.FromMinutes(2))
            {
                clusters.Add(currentCluster);
                currentCluster = new TopicCluster { TopicName = $"Tópico {clusters.Count + 1}" };
                groupDuration = TimeSpan.Zero;
            }
        }

        if (currentCluster.Segments.Any())
        {
            clusters.Add(currentCluster);
        }

        return clusters;
    }

    public List<string> DetectReferences(string text)
    {
        var references = new List<string>();
        // Exemplo: Detecta referências bíblicas ou acadêmicas (ex: João 3:16, Gênesis 1:1)
        var bibleRegex = new Regex(@"(?:[123]\s+)?(?:João|Gênesis|Êxodo|Mateus|Marcos|Lucas|Atos|Romanos|Salmos|Provérbios)\s+\d+:\d+", RegexOptions.IgnoreCase);
        foreach (Match match in bibleRegex.Matches(text))
        {
            if (!references.Contains(match.Value))
            {
                references.Add(match.Value);
            }
        }
        return references;
    }
}
