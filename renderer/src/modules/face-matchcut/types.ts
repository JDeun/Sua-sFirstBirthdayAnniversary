// Copyright (c) JDeun. All rights reserved. Third-party licenses apply separately.
export type MatchcutPhoto = Readonly<{id: string; asset: string;
  label?: string; captured_at?: string | null}>;
export type MatchcutTiming = Readonly<{fps: number; rate?: number;
  durationInFrames?: number; reverse?: boolean; excludedIds?: readonly string[]}>;
export type MatchcutCut = Readonly<{photo: MatchcutPhoto; from: number;
  durationInFrames: number}>;
export type MatchcutPlan = Readonly<{durationInFrames: number; cuts: readonly MatchcutCut[]}>;
export type MatchcutGuide = Readonly<{
  eyes?: readonly [readonly [number, number], readonly [number, number]];
  center?: readonly [number, number]; radii?: readonly [number, number]; color?: string;
}>;
