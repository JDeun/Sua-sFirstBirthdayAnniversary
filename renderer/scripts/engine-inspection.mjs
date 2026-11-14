// Copyright (c) JDeun. All rights reserved. Third-party licenses apply separately.
import {createRequire} from 'node:module';
import path from 'node:path';
import {readFile} from 'node:fs/promises';
import {build} from 'esbuild';

export const RUNTIME_FILES = ['narrative-edit.json', 'narrative-media.json', 'media-exclusions.json',
  'chorus-alignment.json', 'outro-alignment.json', 'stopmotion.json', 'matchcut.json', 'copy.json'];
export const readJson = async (filename) => JSON.parse(await readFile(filename, 'utf8'));
export const validFrame = (value) => Number.isSafeInteger(value) && value >= 0;
const require = createRequire(import.meta.url);

export const loadEngine = async (project, runtime) => {
  const contents = `export {Root,filmMetadata} from './src/Root';
    export {NARRATIVE,NARRATIVE_SHOTS,NARRATIVE_ASSETS,narrativeAssignments} from './src/narrative/edit';
    export {getFrameLayout,getStoryAsset} from './src/narrative/FrameLayout';
    export {getPerformanceTiming} from './src/performance/full-timing';
    export {laughterVolume} from './src/narrative/MemorySound';
    export {wordEvent} from './src/performance/timing';
    export {COPY,SONG_ASSET} from './src/copy';`;
  const compiled = await build({stdin: {contents, resolveDir: project, loader: 'ts'},
    bundle: true, platform: 'node', format: 'cjs', packages: 'external', write: false,
    plugins: [{name: 'external-runtime', setup(buildApi) {
      buildApi.onResolve({filter: /generated\/[^/]+\.json$/}, ({path: name}) =>
        ({path: path.join(runtime, path.basename(name))}));
    }}]});
  const media = await import('@remotion/media');
  const load = (name) => name === '@remotion/media' ? media : require(name);
  const loaded = {exports: {}};
  new Function('require', 'module', 'exports', compiled.outputFiles[0].text)(load, loaded, loaded.exports);
  return loaded.exports;
};

const validateOpening = (opening) => {
  const names = ['duration_in_frames', 'ultrasound_frames', 'matchcut_frames',
    'title_start_frame', 'birth_start_frame'];
  if (names.some((key) => !validFrame(opening[key]))) throw new Error('Opening frame fields must be nonnegative integers.');
  if (opening.duration_in_frames > 0 &&
    (opening.ultrasound_frames + opening.matchcut_frames > opening.title_start_frame ||
     opening.title_start_frame > opening.birth_start_frame ||
     opening.birth_start_frame > opening.duration_in_frames)) {
    throw new Error('Opening sections must be ordered and fit within the opening.');
  }
};

const validateChoruses = (engine) => {
  const {NARRATIVE: edit} = engine;
  const indices = new Set();
  let previousEnd = 0;
  for (const chorus of edit.choruses) {
    if (indices.has(chorus.occurrenceIndex) || !validFrame(chorus.start_frame) ||
      !validFrame(chorus.end_frame) || chorus.start_frame < previousEnd ||
      chorus.end_frame <= chorus.start_frame || chorus.end_frame > edit.main_duration_in_frames) {
      throw new Error('Chorus windows must be unique, ordered and inside the main timeline.');
    }
    const timing = engine.getPerformanceTiming(chorus.occurrenceIndex);
    const cues = timing.occurrence.cues;
    if (timing.alignment.fps !== edit.fps || chorus.start_frame !== cues[0].words[0].start_frame ||
      chorus.end_frame < cues.at(-1).end_frame) throw new Error('Chorus window must retain every native word.');
    engine.narrativeAssignments(chorus.occurrenceIndex);
    indices.add(chorus.occurrenceIndex);
    previousEnd = chorus.end_frame;
  }
};

const validateLayout = (layout, id) => {
  for (const key of ['media', 'words']) {
    const rect = layout[key];
    if (!rect || Object.values(rect).some((v) => !Number.isFinite(v)) || rect.width <= 0 || rect.height <= 0 ||
      rect.x < 0 || rect.y < 0 || rect.x + rect.width > 1920.01 || rect.y + rect.height > 1080.01) {
      throw new Error(`Invalid ${key} rectangle for ${id}.`);
    }
  }
};

const validateMemory = (engine) => {
  const sound = engine.NARRATIVE.memory_audio;
  if (!sound || sound.enabled === false) return;
  const shot = engine.NARRATIVE_SHOTS.find((item) => item.id === sound.shot_id);
  const [start, end] = sound.source_window_frames;
  if (!shot || !sound.asset || !validFrame(start) || !validFrame(end) || start >= end ||
    end > shot.duration_in_frames || !Number.isFinite(sound.source_gain) || sound.source_gain < 0 ||
    !validFrame(sound.source_fade_frames)) throw new Error('Invalid enabled memory audio.');
  for (const frame of [start - 1, start, Math.floor((start + end) / 2), end]) {
    const gain = engine.laughterVolume(frame);
    if (!Number.isFinite(gain) || gain < 0 || gain > sound.source_gain) throw new Error('Invalid memory audio envelope.');
  }
};

export const inspectEngine = (engine) => {
  const {NARRATIVE: edit, NARRATIVE_SHOTS: shots, NARRATIVE_ASSETS: assets} = engine;
  validateOpening(edit.opening);
  if (!Number.isInteger(edit.fps) || edit.fps <= 0 || !validFrame(edit.total_frames) ||
    edit.main_duration_in_frames <= 0 || edit.total_frames !== edit.opening.duration_in_frames + edit.main_duration_in_frames) {
    throw new Error('Film metadata must match the dynamic opening and main timeline.');
  }
  validateChoruses(engine);
  validateMemory(engine);
  const layouts = shots.filter((shot) => shot.usage === 'baseline').map((shot) => {
    const layout = engine.getFrameLayout(shot, engine.getStoryAsset(shot, assets[shot.id]));
    validateLayout(layout, shot.id);
    if (shot.frameLayout && JSON.stringify(layout) !== JSON.stringify(shot.frameLayout)) {
      throw new Error(`Reviewed layout changed for ${shot.id}.`);
    }
    return {id: shot.id, kind: shot.kind, ...layout};
  });
  return {metadata: engine.filmMetadata(), layouts};
};

export const referencedAssets = (value) => {
  if (Array.isArray(value)) return value.flatMap(referencedAssets);
  if (!value || typeof value !== 'object') return [];
  const openingAssets = value.assets && !Array.isArray(value.assets) ? Object.values(value.assets)
    .filter((asset) => typeof asset === 'string' && asset) : [];
  return [...openingAssets, ...Object.entries(value).flatMap(([key, item]) =>
    ['asset', 'poster', 'song_asset'].includes(key) && typeof item === 'string' && item ? [item] : referencedAssets(item))];
};

const chapterStills = (edit) => [...new Set(edit.shots.filter((shot) => shot.usage === 'baseline')
  .map((shot) => shot.chapter))].flatMap((chapter) => {
  const shots = edit.shots.filter((shot) => shot.usage === 'baseline' && shot.chapter === chapter);
  const candidates = [shots[0], shots[Math.floor(shots.length / 2)], shots.at(-1)];
  return candidates.map((shot) => ({label: `baseline-${edit.shots.indexOf(shot) + 1}`,
    frame: edit.opening.duration_in_frames + shot.song_start_frame + Math.floor(shot.duration_in_frames / 2)}));
});

export const planStills = (engine) => {
  const {NARRATIVE: edit} = engine;
  const offset = edit.opening.duration_in_frames;
  const opening = edit.opening;
  const ranges = [[0, opening.ultrasound_frames], [opening.ultrasound_frames, opening.title_start_frame],
    [opening.title_start_frame, opening.birth_start_frame], [opening.birth_start_frame, offset]];
  const intro = ranges.flatMap(([start, end], index) => end > start ?
    [{label: `opening-${index + 1}`, frame: start + Math.floor((end - start) / 2)}] : []);
  const choruses = edit.choruses.flatMap((chorus) => engine.getPerformanceTiming(chorus.occurrenceIndex)
    .occurrence.cues.map((cue, index) => ({label: `chorus-${chorus.occurrenceIndex + 1}-phrase-${index + 1}`,
      frame: offset + Math.min(cue.end_frame - 1, cue.words.at(-1).start_frame + 8)})));
  const closing = edit.outro_alignment?.lines.find((line) => line.id === edit.outro_alignment.final_line_id);
  const words = (closing?.words ?? []).flatMap((word, index) => [-1, 0].map((delta) =>
    ({label: `closing-word-${index + 1}-${delta < 0 ? 'before' : 'onset'}`, frame: offset + word.start_frame + delta})));
  const all = [...intro, ...chapterStills(edit), ...choruses, ...words].filter(({frame}) =>
    validFrame(frame) && frame < edit.total_frames).sort((a, b) => a.frame - b.frame);
  const unique = all.filter((item, index) => !index || item.frame !== all[index - 1].frame);
  const selected = unique.length > 60 ? Array.from({length: 60}, (_, i) =>
    unique[Math.round(i * (unique.length - 1) / 59)]) : unique;
  return selected.map((item) => ({...item, filename: `frame-${String(item.frame).padStart(6, '0')}-${item.label}.png`}));
};
