using System;
using System.Collections.Generic;
using CortexFlow.Core.Domains;
using CortexFlow.Core.Models;
using Xunit;

namespace CortexFlow.Core.Tests;

public class DomainEngineTests
{
    [Fact]
    public void SemanticEngine_ExtractsTopicsAndReferences()
    {
        var engine = new SemanticEngine();
        var result = new TranscriptionResult
        {
            FullText = "Estudo sobre João 3:16 e Gênesis 1:1 na transcrição.",
            Segments = new List<TranscriptionSegment>
            {
                new() { Start = TimeSpan.Zero, End = TimeSpan.FromMinutes(1), Text = "Primeira parte" },
                new() { Start = TimeSpan.FromMinutes(1), End = TimeSpan.FromMinutes(3), Text = "Segunda parte com João 3:16" }
            }
        };

        var topics = engine.ExtractTopics(result);
        var references = engine.DetectReferences(result.FullText);

        Assert.NotEmpty(topics);
        Assert.Contains("João 3:16", references);
        Assert.Contains("Gênesis 1:1", references);
    }

    [Fact]
    public void StudyEngine_GeneratesStudySet()
    {
        var engine = new StudyEngine();
        var result = new TranscriptionResult
        {
            FilePath = "aula_meta.mp3",
            FullText = "Primeira frase importante de teste. Segunda frase para resumo.",
            Segments = new List<TranscriptionSegment>
            {
                new() { Start = TimeSpan.Zero, End = TimeSpan.FromSeconds(10), Text = "Texto explicativo longo para flashcard." }
            }
        };

        var studySet = engine.GenerateStudySet(result);

        Assert.NotNull(studySet);
        Assert.NotEmpty(studySet.Summary);
        Assert.NotEmpty(studySet.Flashcards);
    }

    [Fact]
    public void KnowledgeGraphEngine_BuildsGraphFromResults()
    {
        var engine = new KnowledgeGraphEngine();
        var results = new List<TranscriptionResult>
        {
            new() { FilePath = "doc1.mp3", ContentHash = "hash1" },
            new() { FilePath = "doc2.pdf", ContentHash = "hash2" }
        };

        var graph = engine.BuildGraph(results);

        Assert.Equal(2, graph.Nodes.Count);
    }
}
