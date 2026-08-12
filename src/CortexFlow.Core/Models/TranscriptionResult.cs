using System;
using System.Collections.Generic;

namespace CortexFlow.Core.Models;

public class TranscriptionSegment
{
    public TimeSpan Start { get; set; }
    public TimeSpan End { get; set; }
    public string Text { get; set; } = string.Empty;
}

public class TranscriptionResult
{
    public string FilePath { get; set; } = string.Empty;
    public string ContentHash { get; set; } = string.Empty;
    public string FullText { get; set; } = string.Empty;
    public string Language { get; set; } = "pt";
    public List<TranscriptionSegment> Segments { get; set; } = new();
    public TimeSpan Duration { get; set; }
    public bool FromCache { get; set; }
}
