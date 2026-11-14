// Copyright (c) JDeun. All rights reserved. Third-party licenses apply separately.
import {createContext, useContext} from 'react';

export type PerformanceAsset = {
  readonly original: string;
  readonly asset: string;
  readonly kind: 'photo' | 'video';
  readonly framing: 'cutout' | 'full';
  readonly preserveContext?: boolean;
  readonly subjectScale?: number;
  readonly dimensions: readonly [number, number];
  readonly face: readonly [number, number];
  readonly head: readonly [number, number];
  readonly alphaBounds?: readonly [number, number, number, number];
  /** Output span metadata; Video's same-named prop trims source frames before retiming. */
  readonly durationInFrames?: number;
  readonly playbackRate?: number;
};

export const PerformanceMedia = createContext<PerformanceAsset | null>(null);
export const usePerformanceAsset = () => useContext(PerformanceMedia);
export type PerformanceAssignments = Readonly<Record<string, PerformanceAsset>>;
