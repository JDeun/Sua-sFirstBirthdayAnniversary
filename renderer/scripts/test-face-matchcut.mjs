// Copyright (c) JDeun. All rights reserved. Third-party licenses apply separately.
import assert from 'node:assert/strict';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {test} from 'node:test';
import {build} from 'esbuild';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const result = await build({entryPoints: [path.join(root, 'src/modules/face-matchcut/timeline.ts')],
  bundle: true, write: false, platform: 'node', format: 'esm'});
const {createMatchcutPlan: plan, getMatchcutDuration: duration, sampleMatchcutPhotos: sample} =
  await import('data:text/javascript;base64,' + Buffer.from(result.outputFiles[0].contents).toString('base64'));
const photos = count => Array.from({length: count}, (_, i) => Object.freeze({id: `photo-${i}`, asset: `${i}.svg`}));
const boundaries = value => [...value.cuts.map(cut => cut.from), value.durationInFrames];
const continuous = value => {
  let end = 0;
  for (const cut of value.cuts) {
    assert.equal(cut.from, end);
    assert.ok(Number.isInteger(cut.durationInFrames) && cut.durationInFrames > 0);
    end += cut.durationInFrames;
  }
  assert.equal(end, value.durationInFrames);
};

test('274 photos retain every two-frame cut in a 548-frame window', () => {
  const value = plan(photos(274), {fps: 30, durationInFrames: 548});
  assert.equal(value.cuts.length, 274);
  value.cuts.forEach((cut, i) => {assert.equal(cut.from, i * 2); assert.equal(cut.durationInFrames, 2);});
  continuous(value);
});
test('fractional frame cadence retains rate-derived boundaries', () => {
  const value = plan(photos(7), {fps: 30, rate: 17});
  assert.deepEqual(boundaries(value), [0, 2, 4, 5, 7, 9, 11, 12]);
  continuous(value);
});
test('an exact window distributes integer frames without gaps', () => {
  const value = plan(photos(7), {fps: 30, durationInFrames: 11});
  assert.deepEqual(boundaries(value), [0, 2, 3, 5, 6, 8, 9, 11]);
  continuous(value);
});
test('reverse and exclusion preserve immutable input', () => {
  const input = Object.freeze(photos(4));
  const value = plan(input, {fps: 30, reverse: true, excludedIds: ['photo-1']});
  assert.deepEqual(value.cuts.map(c => c.photo.id), ['photo-3', 'photo-2', 'photo-0']);
  assert.deepEqual(input.map(p => p.id), ['photo-0', 'photo-1', 'photo-2', 'photo-3']);
});
test('fewer frames than photos cannot silently discard a photo', () => {
  assert.throws(() => plan(photos(4), {fps: 30, durationInFrames: 3}));
});
test('ambiguous timing and invalid values are rejected', () => {
  for (const rate of [0, -1, NaN, Infinity, 31]) assert.throws(() => plan(photos(2), {fps: 30, rate}));
  for (const fps of [0, -1, NaN, Infinity]) assert.throws(() => plan(photos(2), {fps}));
  for (const frames of [-1, 0, 1.5, NaN, Infinity]) assert.throws(() => plan(photos(2), {fps: 30, durationInFrames: frames}));
  assert.throws(() => plan(photos(2), {fps: 30, rate: 10, durationInFrames: 6}));
});
test('ids and asset references must be nonempty, with unique ids', () => {
  assert.throws(() => plan([photos(1)[0], photos(1)[0]], {fps: 30}));
  for (const photo of [{id: '', asset: 'x'}, {id: 'x', asset: ''}, {id: null, asset: 'x'}]) {
    assert.throws(() => plan([photo], {fps: 30}));
  }
});
test('sampling keeps endpoints and never repeats a shorter input', () => {
  const input = photos(274);
  const sampled = sample(input, 90);
  assert.equal(sampled.length, 90);
  assert.equal(sampled[0], input[0]);
  assert.equal(sampled.at(-1), input.at(-1));
  assert.equal(new Set(sampled.map(p => p.id)).size, 90);
  assert.equal(sample(photos(3), 90).length, 3);
  assert.deepEqual(sample(input, 1), [input[0]]);
  assert.throws(() => sample(input, 0));
});
test('empty inputs and invalid duration counts are explicit', () => {
  assert.deepEqual(plan([], {fps: 30}), {durationInFrames: 0, cuts: []});
  for (const count of [-1, 0.5, NaN, Infinity]) assert.throws(() => duration(count));
  assert.equal(duration(274, 15, 30), 548);
});
test('noninteger fps still yields complete integer-frame coverage', () => {
  const value = plan(photos(50), {fps: 23.976, rate: 12});
  continuous(value);
  assert.equal(value.durationInFrames, Math.round(50 * 23.976 / 12));
});
test('independent preview imports no project data, typography or theme', async () => {
  const built = await build({entryPoints: [path.join(root, 'src/matchcut-index.ts')], bundle: true,
    write: false, metafile: true, packages: 'external', platform: 'browser', format: 'esm'});
  const inputs = Object.keys(built.metafile.inputs).map(filename => path.resolve(filename));
  assert.ok(inputs.every(filename => filename === path.join(root, 'src/matchcut-index.ts') ||
    filename.startsWith(path.join(root, 'src/modules/face-matchcut') + path.sep)));
});
