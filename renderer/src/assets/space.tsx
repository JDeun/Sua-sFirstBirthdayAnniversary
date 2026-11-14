// Copyright (c) JDeun. All rights reserved. Third-party licenses apply separately.
import {tween} from '../shared/motion';

const POINTS = [
  [104, 132], [280, 864], [1610, 140], [1810, 352], [1700, 910], [1120, 968],
] as const;

/** Sparse and behind the subject. No particle crosses the face. */
export const QuietStars = ({frame, color}: {
  readonly frame: number;
  readonly color: string;
}) => <svg width="1920" height="1080" viewBox="0 0 1920 1080"
  aria-hidden style={{position: 'absolute', inset: 0}} fill={color}>
  {POINTS.map(([x, y], i) => <g key={i} transform={`translate(${x} ${y})`}
    opacity={0.14 + (Math.sin(frame * 0.025 + i * 1.7) + 1) * 0.06}>
    {i % 3 === 0 ? <path d="M0 -8 L2 -2 L8 0 L2 2 L0 8 L-2 2 L-8 0 L-2 -2Z" />
      : <circle r={i % 2 === 0 ? 2 : 1.5} />}
  </g>)}
</svg>;

export const Halo = ({frame, x, y, radius, color, filled = false}: {
  readonly frame: number;
  readonly x: number;
  readonly y: number;
  readonly radius: number;
  readonly color: string;
  readonly filled?: boolean;
}) => <div aria-hidden style={{position: 'absolute', left: x - radius,
  top: y - radius, width: radius * 2, height: radius * 2, borderRadius: '50%',
  background: filled ? color : undefined, border: filled ? undefined : `1.5px solid ${color}`,
  opacity: filled ? 0.52 : 0.14,
  transform: `scale(${tween(frame, [0, 24], [0.86, 1])})`}} />;

export const SubjectOrbits = ({frame, x, y, color}: {
  readonly frame: number;
  readonly x: number;
  readonly y: number;
  readonly color: string;
}) => {
  const drift = tween(frame, [0, 36], [-8, 0]) + frame * 0.016;
  return <svg width="1920" height="1080" viewBox="0 0 1920 1080"
    fill="none" stroke={color} strokeWidth="1.5" opacity={0.16}
    aria-hidden style={{position: 'absolute', inset: 0}}>
    <g transform={`translate(${x} ${y}) rotate(${drift})`}>
      <ellipse rx="648" ry="208" transform="rotate(-22)" />
      <ellipse rx="524" ry="334" transform="rotate(34)" />
      <circle cx="-566" cy="157" r="5" fill={color} stroke="none" />
    </g>
  </svg>;
};

/** The world moves at the margins; the photo is never inside this transform. */
export const TremorLines = ({frame, color}: {
  readonly frame: number;
  readonly color: string;
}) => {
  const energy = tween(frame, [0, 10, 28], [0.8, 1, 0.16]);
  return <svg width="1920" height="1080" viewBox="0 0 1920 1080" fill="none"
    stroke={color} strokeWidth="2" opacity={0.14} aria-hidden
    style={{position: 'absolute', inset: 0}}>
    {[-1, 1].map((side) => <g key={side}
      transform={`translate(${side === -1 ? 240 : 1680} 680) rotate(${side * energy * 8})`}>
      {[0, 1, 2].map((i) => <path key={i}
        d={`M-310 ${i * 66 - 80} Q0 ${i * 66 - 150} 310 ${i * 66 - 80}`}
        transform={`translate(${Math.sin(frame * 0.22 + i) * 12 * energy} 0)`} />)}
    </g>)}
  </svg>;
};

/** Abstract enclosing arcs, with no literal crown or castle illustration. */
export const ShelterArcs = ({frame, color}: {
  readonly frame: number;
  readonly color: string;
}) => {
  const settle = tween(frame, [0, 28], [1, 0]);
  return <svg width="1920" height="1080" viewBox="0 0 1920 1080" fill="none"
    stroke={color} strokeWidth="2" aria-hidden style={{position: 'absolute', inset: 0}}>
    {[0, 1, 2].map((i) => <path key={i} opacity={0.18 - i * 0.04}
      d={`M${170 - i * 38} 990 V560 A${430 + i * 38} ${430 + i * 38} 0 0 1 ${1030 + i * 38} 560 V990`}
      strokeDasharray="1900" strokeDashoffset={settle * 1900}
      transform={`translate(0 ${settle * (30 + i * 18)})`} />)}
  </svg>;
};
