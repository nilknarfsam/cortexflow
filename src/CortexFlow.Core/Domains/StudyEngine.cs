using System;
using System.Collections.Generic;
using System.Linq;
using CortexFlow.Core.Models;

namespace CortexFlow.Core.Domains;

public class Flashcard
{
    public string Question { get; set; } = string.Empty;
    public string Answer { get; set; } = string.Empty;
}

public class QuizQuestion
{
    public string QuestionText { get; set; } = string.Empty;
    public List<string> Options { get; set; } = new();
    public int CorrectOptionIndex { get; set; }
}

public class StudySet
{
    public string Title { get; set; } = string.Empty;
    public string Summary { get; set; } = string.Empty;
    public List<Flashcard> Flashcards { get; set; } = new();
    public List<QuizQuestion> Quizzes { get; set; } = new();
}

public class StudyEngine
{
    public StudySet GenerateStudySet(TranscriptionResult result)
    {
        var studySet = new StudySet
        {
            Title = $"Estudo: {System.IO.Path.GetFileName(result.FilePath)}",
            Summary = ExtractSummary(result.FullText)
        };

        // Geração heurística de flashcards a partir dos segmentos principais
        foreach (var seg in result.Segments.Take(5))
        {
            if (seg.Text.Length > 20)
            {
                studySet.Flashcards.Add(new Flashcard
                {
                    Question = $"O que é abordado no minuto [{seg.Start:mm\\:ss}]?",
                    Answer = seg.Text
                });
            }
        }

        return studySet;
    }

    private static string ExtractSummary(string text)
    {
        if (string.IsNullOrWhiteSpace(text)) return string.Empty;
        var sentences = text.Split(new[] { '.', '!', '?' }, StringSplitOptions.RemoveEmptyEntries);
        return string.Join(". ", sentences.Take(3)) + ".";
    }
}
