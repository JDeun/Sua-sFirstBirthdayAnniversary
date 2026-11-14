// Copyright (c) JDeun. All rights reserved. Third-party licenses apply separately.
import type {MatchcutGuide} from './types';

/** Normalized positions share the same canvas as the aligned input images. */
export const FaceMatchcutGuide = ({width, height, eyes = [[850 / 1920, 430 / 1080],
  [1070 / 1920, 430 / 1080]], center = [0.5, 420 / 1080],
  radii = [420 / 1920, 400 / 1080], color = '#47ffcf'}: MatchcutGuide &
  Readonly<{width: number; height: number}>) => <svg aria-hidden width={width} height={height}
    viewBox={`0 0 ${width} ${height}`} style={{position: 'absolute', pointerEvents: 'none'}}>
  <ellipse cx={center[0] * width} cy={center[1] * height} rx={radii[0] * width}
    ry={radii[1] * height} fill="none" stroke={color} strokeWidth={3} />
  <path d={`M${width * 600 / 1920} ${height * 430 / 1080}H${width * 1320 / 1920}
    M${width / 2} ${height * 90 / 1080}V${height * 860 / 1080}`}
    fill="none" stroke={color} strokeWidth={2} />
  {eyes.map(([x, y], index) => <circle key={index} cx={x * width} cy={y * height}
    r={width * 12 / 1920} fill="none" stroke="#ffdf5c" strokeWidth={4} />)}
</svg>;
