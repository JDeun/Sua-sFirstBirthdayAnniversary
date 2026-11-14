// Copyright (c) JDeun. All rights reserved. Third-party licenses apply separately.
import {Easing, interpolate} from 'remotion';

export const tween = (
  frame: number, input: readonly number[], output: readonly number[],
  easing = Easing.out(Easing.cubic),
) => interpolate(frame, input, output, {
  extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing,
});
