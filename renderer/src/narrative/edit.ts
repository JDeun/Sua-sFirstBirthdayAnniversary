// Copyright (c) JDeun. All rights reserved. Third-party licenses apply separately.
import plan from '../generated/narrative-edit.json';
import staged from '../generated/narrative-media.json';
import {EXCLUDED_STEMS} from '../opening-media';
import type {FrameLayout} from './FrameLayout';
import type {NarrativePlan} from './runtime-types';
import type {PerformanceAsset, PerformanceAssignments} from '../performance/production-media';
import {validateStoryCaptions} from './story-captions';

export type NarrativeAsset = PerformanceAsset & {readonly poster?: string;
  readonly crop?: readonly [number, number, number, number]};
export type NarrativeShot = {
  readonly id: string;
  readonly usage: 'baseline' | 'chorus_slot';
  readonly chapter: number;
  readonly occurrenceIndex?: number;
  readonly cue_id?: string;
  readonly song_start_frame: number;
  readonly song_end_frame: number;
  readonly duration_in_frames: number;
  readonly kind: 'photo' | 'video';
  readonly captured_at: string | null;
  readonly date_basis: {readonly sort_interval?: readonly [string, string]};
  readonly canonical_original_source: string;
  readonly layout?: string;
  readonly frameLayout?: FrameLayout;
  readonly caption?: string;
  readonly captionCues?: readonly {readonly text: string; readonly start_frame: number;
    readonly end_frame: number; readonly role?: 'lead' | 'support'}[];
  readonly lyricOwned?: boolean;
  readonly pending_media?: string;
  readonly event?: {readonly label: string; readonly date_label: string;
    readonly start_frame: number; readonly end_frame: number};
};

export const NARRATIVE = plan as unknown as NarrativePlan;
export const NARRATIVE_SHOTS = plan.shots as unknown as readonly NarrativeShot[];
const prepared = Object.fromEntries(Object.values(staged.assets).map((asset) => [asset.asset, asset])) as unknown as
  Readonly<Record<string, {readonly dimensions: readonly [number, number]; readonly poster?: string}>>;
export const NARRATIVE_ASSETS = Object.fromEntries(Object.entries(plan.assets).map(([id, asset]) => {
  const record = prepared[asset.asset];
  return [id, {...asset, dimensions: record?.dimensions ?? asset.dimensions,
    ...('poster' in asset ? {poster: record?.poster ?? asset.poster} : {})}];
})) as unknown as Readonly<Record<string, NarrativeAsset>>;

const validate = () => {
  const closing = NARRATIVE.outro_alignment?.lines.find(line =>
    line.id === NARRATIVE.outro_alignment?.final_line_id);
  validateStoryCaptions(NARRATIVE.story_captions, NARRATIVE.main_duration_in_frames,
    NARRATIVE.choruses, closing?.start_frame);
  const seen = new Set<string>();
  const forbidden = new Set(EXCLUDED_STEMS.map((s) => s.toLowerCase()));
  let end = 0;
  let date = '';
  for (const shot of NARRATIVE_SHOTS) {
    const asset = NARRATIVE_ASSETS[shot.id];
    if (!asset) throw new Error(`Missing narrative source: ${shot.id}`);
    const stem = asset.original.split('/').pop()!.replace(/\.[^.]+$/, '').toLowerCase();
    if (forbidden.has(stem) || seen.has(asset.original) ||
      shot.song_start_frame !== end || shot.song_end_frame <= end ||
      asset.original !== shot.canonical_original_source) throw new Error(`Invalid narrative source: ${shot.id}`);
    if (shot.usage === 'baseline') {
      const range = shot.date_basis.sort_interval ?? (shot.captured_at ?
        [shot.captured_at.slice(0, 10), shot.captured_at.slice(0, 10)] : null);
      if (!range) throw new Error(`Missing factual date or date range: ${shot.id}`);
      if (range[1] < date) throw new Error(`Growth event is out of chronological order: ${shot.id}`);
      date = date > range[0] ? date : range[0];
    }
    seen.add(asset.original);
    end = shot.song_end_frame;
  }
  if (end !== plan.main_duration_in_frames || staged.status !== 'ready') {
    throw new Error('The narrative timeline and its actual media are not ready.');
  }
  if (NARRATIVE.final_chorus_sequence && NARRATIVE.choruses.length) {
    const lastChorus = NARRATIVE.choruses.at(-1)!;
    const dates = NARRATIVE_SHOTS.filter((shot) => shot.occurrenceIndex === lastChorus.occurrenceIndex)
      .map((shot) => shot.captured_at!.slice(0, 10));
    const finalEnd = lastChorus.end_frame;
    const following = NARRATIVE_SHOTS.find((shot) => shot.usage === 'baseline' &&
      shot.song_start_frame >= finalEnd)!;
    if (!following) throw new Error('Final chorus chronology requires a following baseline.');
    const cutoff = following.date_basis.sort_interval?.[0] ?? following.captured_at!.slice(0, 10);
    if (dates.length !== NARRATIVE.final_chorus_sequence.distinct_dates || dates.some((date, index) => date >= cutoff ||
      (index > 0 && date <= dates[index - 1]))) {
      throw new Error('The final chorus requires different capture dates in increasing order.');
    }
  }
};
validate();

export const narrativeAssignments = (index: number): PerformanceAssignments => {
  const slots = NARRATIVE_SHOTS.filter((s) => s.occurrenceIndex === index);
  if (slots.length !== 10) throw new Error('Narrative chorus must keep all eight lines / ten scenes.');
  return Object.fromEntries(slots.map((s) => [s.cue_id!, NARRATIVE_ASSETS[s.id]]));
};
