// Copyright (c) JDeun. All rights reserved. Third-party licenses apply separately.
import type {AlignedWord} from '../synced/alignment';
import type {NarrativeAsset, NarrativeShot} from './edit';

export type OutroAlignment = Readonly<{
  fps: number; final_line_id?: string | null;
  lines: readonly Readonly<{id: string; text: string; start_frame: number; end_frame: number;
    words: readonly AlignedWord[]}>[];
}>;
export type NarrativeOpeningPlan = Readonly<{
  duration_in_frames: number; ultrasound_frames: number; matchcut_frames: number;
  matchcut_mode?: string; title_start_frame: number; birth_start_frame: number;
}>;
export type MemoryAudioPlan = Readonly<{
  enabled?: boolean; shot_id: string; asset: string; source_gain: number;
  source_window_frames: readonly [number, number]; source_fade_frames: number;
}>;
export type StoryNarrationCue = Readonly<{
  id: string; text: string; start_frame: number; end_frame: number;
  placement?: 'bottom' | 'left' | 'right'; label?: string; date_label?: string; size?: number;
}>;
export type NarrativePlan = Readonly<{
  fps: number; revision?: string; render_directory?: string;
  total_frames: number; main_duration_in_frames: number; opening: NarrativeOpeningPlan;
  shots: readonly NarrativeShot[]; assets: Readonly<Record<string, NarrativeAsset>>;
  choruses: readonly Readonly<{occurrenceIndex: number; start_frame: number; end_frame: number}>[];
  memory_audio?: MemoryAudioPlan | null; outro_alignment?: OutroAlignment;
  rhythm?: Readonly<{beat_frames: readonly number[]}>;
  final_chorus_sequence?: Readonly<{distinct_dates: number}>;
  story_captions?: readonly StoryNarrationCue[];
}>;
