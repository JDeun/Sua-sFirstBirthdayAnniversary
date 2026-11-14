// Copyright (c) JDeun. All rights reserved. Third-party licenses apply separately.
import {access, mkdir, mkdtemp, rm, writeFile} from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {parseArgs} from 'node:util';
import webpack from 'webpack';
import {bundle} from '@remotion/bundler';
import {inspectEngine, loadEngine, planStills, readJson, referencedAssets, RUNTIME_FILES} from './engine-inspection.mjs';

const project = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const {values: flags} = parseArgs({options: {
  help: {type: 'boolean', short: 'h'}, preflight: {type: 'boolean'}, config: {type: 'string'}, output: {type: 'string'},
  'browser-executable': {type: 'string'}, 'stills-only': {type: 'boolean'}, frames: {type: 'string'},
}});
if (flags.help) {
  process.stdout.write(`Usage: node scripts/verify-headless.mjs [options]
  --preflight                 Validate and create a fresh bundle without Chrome
  --config FILE               External project.json (default: project.local.json if present)
  --output DIRECTORY          Override the project's output directory
  --frames START-END          Render an inclusive frame range, e.g. 0-2
  --stills-only               Render planned stills without encoding the movie
  --browser-executable FILE   Installed Chrome executable (or CHROME_EXECUTABLE)
  -h, --help                  Show this help without loading runtime data or Chrome
`);
  process.exit(0);
}
const saveJson = (directory, name, value) => writeFile(path.join(directory, name), JSON.stringify(value, null, 2) + '\n');
const exists = async (filename) => access(filename).then(() => true, () => false);

const settings = async () => {
  const defaultConfig = path.join(project, 'project.local.json');
  const filename = flags.config ? path.resolve(flags.config) : await exists(defaultConfig) ? defaultConfig : null;
  const config = filename ? await readJson(filename) : {};
  const base = filename ? path.dirname(filename) : project;
  const resolve = (key, fallback) => path.resolve(base, config[key] ?? fallback);
  const runtime = resolve('runtime_directory', 'src/generated');
  const publicDir = resolve('asset_directory', 'public');
  const output = flags.output ? path.resolve(flags.output) : resolve('output_directory', 'output');
  const media = config.media_directory ? resolve('media_directory', '.') : null;
  if ([runtime, publicDir, ...(media ? [media] : [])].some((source) =>
    output === source || output.startsWith(source + path.sep))) {
    throw new Error('Output must be outside the runtime and asset directories.');
  }
  return {runtime, publicDir, output};
};

const checkAssets = async (runtime, publicDir, songAsset) => {
  const names = RUNTIME_FILES.filter((name) => name !== 'narrative-media.json');
  const data = await Promise.all(names.map(async (name) => {
    const value = await readJson(path.join(runtime, name));
    if (['copy.json', 'chorus-alignment.json'].includes(name)) return {...value, song_asset: null};
    return value;
  }));
  const references = [...new Set([...data.flatMap(referencedAssets), ...(songAsset ? [songAsset] : [])])];
  await Promise.all(references.map(async (name) => {
    const filename = path.resolve(publicDir, name);
    if (path.isAbsolute(name) || name.includes('\\') || filename === publicDir ||
      !filename.startsWith(publicDir + path.sep)) throw new Error('Asset reference must stay inside the asset directory.');
    await access(filename);
  }));
  return references.length;
};

const makeBundle = (runtime, publicDir, outDir) => bundle({entryPoint: path.join(project, 'src/index.ts'),
  rootDir: project, publicDir, outDir, enableCaching: false, symlinkPublicDir: true,
  webpackOverride: (config) => ({...config, plugins: [...(config.plugins ?? []),
    new webpack.NormalModuleReplacementPlugin(/generated\/[^/]+\.json$/, (resource) => {
      resource.request = path.join(runtime, path.basename(resource.request));
    })]}),
});

const renderProgress = ({progress}) => {
  process.stdout.write(`\r[FamilyFilm] ${Math.floor(progress * 100)}%`);
};

const frameRange = (duration) => {
  if (!flags.frames) return undefined;
  const match = /^(\d+)-(\d+)$/.exec(flags.frames);
  const range = match?.slice(1).map(Number);
  if (!range || range.some((frame) => !Number.isSafeInteger(frame)) ||
    range[0] > range[1] || range[1] >= duration) throw new Error('--frames must be an inclusive START-END range inside the composition.');
  return range;
};

const render = async (serveUrl, output, report) => {
  const range = frameRange(report.metadata.durationInFrames);
  const executable = flags['browser-executable'] ?? process.env.CHROME_EXECUTABLE;
  if (executable) await access(executable);
  const {openBrowser, selectComposition, renderStill, renderMedia} = await import('@remotion/renderer');
  const browser = await openBrowser('chrome', {...(executable ? {browserExecutable: executable} : {}), logLevel: 'info'});
  try {
    const composition = await selectComposition({serveUrl, id: 'FamilyFilm', puppeteerInstance: browser});
    const {fps, width, height, durationInFrames} = composition;
    if (JSON.stringify({fps, width, height, durationInFrames}) !== JSON.stringify(report.metadata)) {
      throw new Error('Browser composition metadata differs from the preflight.');
    }
    const stills = range ? report.still_frames.filter(({frame}) => frame >= range[0] && frame <= range[1]) : report.still_frames;
    for (const {frame, filename} of stills) {
      await renderStill({serveUrl, composition, frame, imageFormat: 'png',
        output: path.join(output, filename), puppeteerInstance: browser});
    }
    if (!flags['stills-only']) await renderMedia({serveUrl, composition,
      codec: 'h264', audioCodec: 'aac', crf: 18, concurrency: 1, frameRange: range,
      outputLocation: path.join(output, 'family-film.mp4'), puppeteerInstance: browser, onProgress: renderProgress});
  } finally {
    await browser.close({silent: true});
  }
};

const main = async () => {
  const {runtime, publicDir, output} = await settings();
  await mkdir(output, {recursive: true});
  const engine = await loadEngine(project, runtime);
  const inspected = inspectEngine(engine);
  const referenced = await checkAssets(runtime, publicDir, engine.SONG_ASSET);
  const stills = planStills(engine);
  const requestedFrames = frameRange(inspected.metadata.durationInFrames);
  const outDir = await mkdtemp(path.join(output, '.bundle-'));
  try {
    const serveUrl = await makeBundle(runtime, publicDir, outDir);
    const report = {status: 'preflight_passed', composition: 'FamilyFilm', metadata: inspected.metadata,
      opening_frames: engine.NARRATIVE.opening.duration_in_frames,
      main_frames: engine.NARRATIVE.main_duration_in_frames, baseline_layouts: inspected.layouts.length,
      choruses: engine.NARRATIVE.choruses.length, referenced_assets: referenced,
      still_frames: stills, requested_frame_range: requestedFrames ?? null, fresh_bundle: true, browser_launched: false,
      visual_review: 'pending', audio_review: 'pending', temporary_bundle_retained: false};
    await saveJson(output, 'layouts.json', {width: 1920, height: 1080, shots: inspected.layouts});
    await saveJson(output, 'preflight.json', report);
    if (!flags.preflight) {
      await render(serveUrl, output, report);
      await saveJson(output, 'render-report.json', {...report, status: flags['stills-only'] ? 'stills_rendered' : 'rendered',
        browser_launched: true});
    }
    process.stdout.write(`\nFamilyFilm ${flags.preflight ? 'preflight passed' : 'render complete'}: ${report.metadata.durationInFrames} frames, ${stills.length} planned stills.\n`);
  } finally {
    await rm(outDir, {recursive: true, force: true});
  }
};

await main().catch((error) => {
  process.stderr.write(`${error.stack ?? error}\n`);
  process.exitCode = 1;
});
