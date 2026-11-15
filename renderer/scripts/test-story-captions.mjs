// Copyright (c) JDeun. All rights reserved. Third-party licenses apply separately.
import assert from 'node:assert/strict';
import {test} from 'node:test';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {build} from 'esbuild';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const result = await build({entryPoints: [path.join(root, 'src/narrative/story-captions.ts')],
  bundle: true, write: false, format: 'esm', platform: 'node'});
const {activeStoryCaption, storyCaptionLayout, validateStoryCaptions} = await import(
  'data:text/javascript;base64,' + Buffer.from(result.outputFiles[0].contents).toString('base64'));
const cue = (overrides = {}) => ({id: 'one', text: 'A quiet start', start_frame: 0, end_frame: 90, ...overrides});

test('a narration holds across photo cuts and expires on its exact last boundary', () => {
  const value = cue();
  for (const frame of [0, 29, 30, 59, 60, 89]) assert.equal(activeStoryCaption([value], frame), value);
  assert.equal(activeStoryCaption([value], 90), undefined);
});
test('new mode leaves existing projects valid and never enters protected chorus or outro', () => {
  validateStoryCaptions(undefined, 300, []);
  const chorus = [{start_frame: 90, end_frame: 180}];
  validateStoryCaptions([cue()], 300, chorus, 240);
  assert.throws(() => validateStoryCaptions([cue({end_frame: 91})], 300, chorus, 240));
  assert.throws(() => validateStoryCaptions([cue({start_frame: 230, end_frame: 241})], 300, chorus, 240));
});
test('overlaps, duplicate ids, invalid geometry and unreadable empty lines fail', () => {
  assert.throws(() => validateStoryCaptions([cue(), cue({start_frame: 80, end_frame: 100})], 300, []));
  assert.throws(() => validateStoryCaptions([cue(), cue({start_frame: 90, end_frame: 100})], 300, []));
  for (const overrides of [{start_frame: -1}, {end_frame: 0}, {text: '\nHidden'}, {size: NaN},
    {placement: 'unknown'}, {label: {}}, {text: 'a\nb\nc'}]) {
    assert.throws(() => validateStoryCaptions([cue(overrides)], 300, []));
  }
});
test('two lines and a milestone label fit the visible canvas in each placement', () => {
  for (const placement of ['bottom', 'left', 'right']) {
    const value = cue({text: 'A new day\nA small discovery', label: 'Milestone', date_label: 'Year', placement});
    validateStoryCaptions([value], 300, []);
    const box = storyCaptionLayout(value);
    assert.ok(box.x >= 0 && box.y >= 0 && box.x + box.width <= 1920 && box.y + box.height <= 1080);
  }
});
