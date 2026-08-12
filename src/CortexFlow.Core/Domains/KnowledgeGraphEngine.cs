using System.Collections.Generic;
using CortexFlow.Core.Models;

namespace CortexFlow.Core.Domains;

public class GraphNode
{
    public string Id { get; set; } = string.Empty;
    public string Label { get; set; } = string.Empty;
    public string Type { get; set; } = "Document";
}

public class GraphEdge
{
    public string SourceId { get; set; } = string.Empty;
    public string TargetId { get; set; } = string.Empty;
    public string Relation { get; set; } = "REFERENCES";
}

public class KnowledgeGraph
{
    public List<GraphNode> Nodes { get; set; } = new();
    public List<GraphEdge> Edges { get; set; } = new();
}

public class KnowledgeGraphEngine
{
    public KnowledgeGraph BuildGraph(IEnumerable<TranscriptionResult> results)
    {
        var graph = new KnowledgeGraph();

        foreach (var res in results)
        {
            var docNode = new GraphNode
            {
                Id = res.ContentHash,
                Label = System.IO.Path.GetFileName(res.FilePath),
                Type = "Document"
            };
            graph.Nodes.Add(docNode);
        }

        return graph;
    }
}
