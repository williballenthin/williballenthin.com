const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

function loadTranscriptHelpers() {
  const html = fs.readFileSync(
    path.join(__dirname, '..', 'static', 'tools', 'vnote.html'),
    'utf8'
  );
  const match = html.match(/const VNoteTranscript = \(\(\) => \{[\s\S]*?\n    \}\)\(\);/);

  assert.ok(match, 'expected inline VNoteTranscript helper in vnote.html');

  const context = {
    module: { exports: null }
  };
  vm.runInNewContext(`${match[0]}\nmodule.exports = VNoteTranscript;`, context);
  return context.module.exports;
}

const {
  joinTranscriptParts,
  snapshotRecognitionResults,
  computeTranscriptState,
  getTranscriptText
} = loadTranscriptHelpers();

function makeResult(transcript, isFinal) {
  return {
    0: { transcript },
    isFinal
  };
}

test('snapshotRecognitionResults keeps every result slot so later updates do not drop earlier text', () => {
  const results = JSON.parse(JSON.stringify(snapshotRecognitionResults([
    makeResult('first part', true),
    makeResult('second half', false)
  ])));

  assert.deepEqual(results, [
    { transcript: 'first part', isFinal: true },
    { transcript: 'second half', isFinal: false }
  ]);
});

test('computeTranscriptState rebuilds transcript text from all result slots', () => {
  const transcriptState = computeTranscriptState([
    { transcript: 'first part', isFinal: true },
    { transcript: 'second half', isFinal: false },
    { transcript: 'third part', isFinal: true }
  ]);

  assert.equal(transcriptState.finalTranscript, 'first part third part');
  assert.equal(transcriptState.interimTranscript, 'second half');
});

test('getTranscriptText can include interim text so stopping does not discard the tail of the transcript', () => {
  const results = [
    { transcript: 'first half', isFinal: true },
    { transcript: 'second half', isFinal: false }
  ];

  assert.equal(getTranscriptText(results), 'first half');
  assert.equal(getTranscriptText(results, { includeInterim: true }), 'first half second half');
});

test('joinTranscriptParts preserves earlier committed text when recognition restarts with a fresh results array', () => {
  const previousSessionText = getTranscriptText([
    { transcript: 'first half', isFinal: true }
  ]);
  const nextSessionText = getTranscriptText([
    { transcript: 'second half', isFinal: false }
  ], { includeInterim: true });

  assert.equal(joinTranscriptParts([previousSessionText, nextSessionText]), 'first half second half');
});

test('getTranscriptText returns the placeholder when nothing has been captured', () => {
  assert.equal(getTranscriptText([], { includeInterim: true }), '(No transcript captured)');
});
