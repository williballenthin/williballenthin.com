(function (root, factory) {
  if (typeof module === 'object' && module.exports) {
    module.exports = factory();
  } else {
    root.VNoteTranscript = factory();
  }
}(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  function readTranscript(result) {
    if (!result || !result[0] || typeof result[0].transcript !== 'string') {
      return '';
    }

    return result[0].transcript.trim();
  }

  function snapshotRecognitionResults(results) {
    return Array.from(results || [], (result) => ({
      transcript: readTranscript(result),
      isFinal: Boolean(result && result.isFinal)
    }));
  }

  function joinTranscriptParts(parts) {
    return parts
      .map((part) => (part || '').trim())
      .filter(Boolean)
      .join(' ');
  }

  function computeTranscriptState(resultsByIndex) {
    const finalParts = [];
    const interimParts = [];

    for (const result of resultsByIndex || []) {
      if (!result || !result.transcript) {
        continue;
      }

      if (result.isFinal) {
        finalParts.push(result.transcript.trim());
      } else {
        interimParts.push(result.transcript.trim());
      }
    }

    return {
      finalTranscript: joinTranscriptParts(finalParts),
      interimTranscript: joinTranscriptParts(interimParts)
    };
  }

  function getTranscriptText(resultsByIndex, options) {
    const includeInterim = Boolean(options && options.includeInterim);
    const transcriptState = computeTranscriptState(resultsByIndex);
    const transcriptText = joinTranscriptParts([
      transcriptState.finalTranscript,
      includeInterim ? transcriptState.interimTranscript : ''
    ]);

    return transcriptText || '(No transcript captured)';
  }

  return {
    joinTranscriptParts,
    snapshotRecognitionResults,
    computeTranscriptState,
    getTranscriptText
  };
}));
