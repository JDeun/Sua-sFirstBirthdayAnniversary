// Copyright (c) JDeun. All rights reserved. Third-party licenses apply separately.
import {Halo, QuietStars, SubjectOrbits} from '../shared/space';
import {StarBloom} from '../performance/graphics';
import {FILM} from '../theme';
import type {FrameLayout, StoryShot} from './FrameLayout';
import {VERSE_OUTRO_START, verseBeat, verseEase, verseQuiet, verseShotFrame,
  verseShotProgress} from './VerseMotion';

export const verseBackdropState = (shot: StoryShot, layout: FrameLayout, frame: number) => {
  const songFrame = shot.song_start_frame + frame;
  const closing = !!shot.lyricOwned;
  const quiet = verseQuiet(songFrame, closing);
  const motionFrame = verseShotFrame(frame, songFrame, closing);
  const clock = shot.song_start_frame + motionFrame;
  const drift = verseShotProgress(frame, shot.duration_in_frames, songFrame, closing) * (closing ? 0.2 : 1);
  const m = layout.media;
  const accent = layout.shade === 'blue' ? FILM.colors.blueInk :
    layout.shade === 'peach' || layout.shade === 'rose' ? FILM.colors.peachInk : FILM.colors.lavenderInk;
  return {songFrame, clock, quiet, beat: verseBeat(songFrame), accent, ribbon: 0,
    opening: verseEase(motionFrame, 24), drift,
    x: m.x + m.width / 2, y: m.y + m.height / 2,
    radius: Math.max(380, Math.min(560, m.width * 0.58)),
    right: m.x + m.width / 2 < 960,
    reserveLyrics: !!shot.lyricOwned && songFrame >= VERSE_OUTRO_START};
};

const VerseSweep = ({state}: Readonly<{
  state: ReturnType<typeof verseBackdropState>;
}>) => {
  const {accent, quiet, x, y, radius, drift} = state;
  const angle = -0.45 + drift * 0.2;
  return <svg aria-hidden width={1920} height={1080} viewBox="0 0 1920 1080"
    style={{position: 'absolute', inset: 0, pointerEvents: 'none'}}>
    <g transform={`translate(${x} ${y}) rotate(${-22 + drift * 3})`}
      fill="none" stroke={accent} opacity={0.22 * quiet}>
      <ellipse rx={radius + 105} ry={radius * 0.47} strokeWidth={3} />
      <circle cx={(radius + 105) * Math.cos(angle)}
        cy={radius * 0.47 * Math.sin(angle)} r={7} fill={accent} />
    </g>
  </svg>;
};

/** A single entrance into the pastel universe, followed by slow, shot-long drift. */
export const VerseBackdrop = ({shot, layout, frame}: Readonly<{
  shot: StoryShot; layout: FrameLayout; frame: number;
}>) => {
  const s = verseBackdropState(shot, layout, frame);
  return <div data-verse-background={layout.family} aria-hidden style={{position: 'absolute', inset: 0,
    pointerEvents: 'none', opacity: s.opening,
    clipPath: s.reserveLyrics ? 'inset(0 0 0 1020px)' : undefined}}>
    <div style={{position: 'absolute', inset: 0, transformOrigin: `${s.x}px ${s.y}px`,
      transform: `translate(${s.drift * 8}px, ${-s.drift * 5}px) scale(${1 + s.drift * 0.01})`,
      opacity: 0.65 + s.quiet * 0.35}}>
      <Halo frame={24} x={s.x} y={s.y} radius={s.radius}
        color={layout.shade === 'cream' ? FILM.colors.lavender : FILM.colors.cream} filled />
      <SubjectOrbits frame={36 + s.drift * 160} x={s.x} y={s.y} color={s.accent} />
    </div>
    <div style={{opacity: s.quiet * 0.65,
      transform: `translate(${-s.drift * 6}px, ${s.drift * 4}px)`}}>
      <QuietStars frame={0} color={s.accent} />
      <StarBloom frame={12} x={s.right ? 1800 : 120} y={164} size={136}
        color={layout.shade === 'lavender' ? FILM.colors.peach : FILM.colors.lavender} />
    </div>
    <VerseSweep state={s} />
  </div>;
};
