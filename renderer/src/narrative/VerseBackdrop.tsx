// Copyright (c) JDeun. All rights reserved. Third-party licenses apply separately.
import {Halo} from '../assets/space';
import {useId} from 'react';
import {StoryDoodles, storyDoodlePlacement, type StoryDoodleKind} from '../assets/StoryDoodles';
import {FILM} from '../theme';
import {NARRATIVE, NARRATIVE_SHOTS, NARRATIVE_ASSETS} from './edit';
import {storyCaptionLayout} from './story-captions';
import {getFrameLayout, type FrameLayout, type StoryShot, type Rect} from './FrameLayout';
import {VERSE_OUTRO_START, verseEase, verseQuiet} from './VerseMotion';

/** Chapter-level authorship: event presence and editorial families, never labels or private IDs. */
export const verseDoodleGroup = (shot: StoryShot, shots: readonly StoryShot[]) => {
  const group = shots.filter((entry) => entry.usage === 'baseline' && entry.chapter === shot.chapter &&
    !entry.lyricOwned);
  const first = group[0], last = group.at(-1);
  const familyEvent = group.some((entry) => entry.event &&
    (entry.frameLayout?.family === 'family-album' || entry.layout === 'family'));
  const kind: StoryDoodleKind = familyEvent ? 'orbit' : group.some((entry) => entry.event) ? 'constellation' : 'arc';
  const start = first?.song_start_frame ?? shot.song_start_frame;
  const end = last?.song_end_frame ?? shot.song_end_frame;
  const firstMedia = first?.frameLayout?.media;
  return {start, end, kind, first, members: group,
    preferRight: firstMedia ? firstMedia.x + firstMedia.width / 2 < 960 : false,
    enabled: shot.usage === 'baseline' && !shot.lyricOwned && end - start >= 174};
};

const unionBounds = (rectangles: readonly Rect[]): Rect | undefined => {
  if (!rectangles.length) return undefined;
  const x = Math.min(...rectangles.map(rect => rect.x)), y = Math.min(...rectangles.map(rect => rect.y));
  return {x, y, width: Math.max(...rectangles.map(rect => rect.x + rect.width)) - x,
    height: Math.max(...rectangles.map(rect => rect.y + rect.height)) - y};
};

/** Reserve every sentence in the chapter up front; later words cannot move a completed figure. */
const chapterWords = (group: ReturnType<typeof verseDoodleGroup>) => NARRATIVE.story_captions ?
  unionBounds(NARRATIVE.story_captions.filter(cue => cue.start_frame < group.end && cue.end_frame > group.start)
    .map(storyCaptionLayout)) : unionBounds(group.members.filter(shot => shot.caption ||
      shot.captionCues?.length || shot.event).flatMap(shot => shot.frameLayout ? [shot.frameLayout.words] : []));

export const verseBackdropState = (shot: StoryShot, layout: FrameLayout, frame: number,
  shots: readonly StoryShot[] = NARRATIVE_SHOTS) => {
  const songFrame = shot.song_start_frame + frame;
  const closing = !!shot.lyricOwned, group = verseDoodleGroup(shot, shots);
  const localFrame = songFrame - group.start;
  const quiet = verseQuiet(songFrame, closing), m = layout.media;
  const reserveLyrics = closing && songFrame >= VERSE_OUTRO_START;
  const accent = layout.shade === 'blue' ? FILM.colors.blueInk :
    layout.shade === 'peach' || layout.shade === 'rose' ? FILM.colors.peachInk : FILM.colors.lavenderInk;
  const firstAsset = group.first && NARRATIVE_ASSETS[group.first.id];
  const anchor = group.first?.frameLayout?.media ?? (firstAsset ?
    getFrameLayout(group.first!, firstAsset).media : m);
  return {songFrame, localFrame, quiet, accent, group, reserveLyrics,
    opening: closing ? 1 : verseEase(localFrame, 18),
    opacity: group.enabled ? 0.68 * (1 - verseEase(songFrame - group.end + 12, 12)) : 0,
    placement: storyDoodlePlacement(anchor, chapterWords(group), reserveLyrics, group.preferRight),
    x: m.x + m.width / 2, y: m.y + m.height / 2,
    radius: Math.max(380, Math.min(560, m.width * 0.58))};
};

const mediaExclusion = (media: Rect) => {
  const x = media.x - 32, y = media.y - 32, r = media.x + media.width + 32, b = media.y + media.height + 32;
  return `M0 0H1920V1080H0Z M${x} ${y}H${r}V${b}H${x}Z`;
};

/** A held pastel field; only the chapter's authored margin drawing has an entrance. */
export const VerseBackdrop = ({shot, layout, frame}: Readonly<{
  shot: StoryShot; layout: FrameLayout; frame: number;
}>) => {
  const s = verseBackdropState(shot, layout, frame);
  const clip = `story-margin-${useId().replace(/:/g, '')}`;
  return <div data-verse-background={layout.family} aria-hidden style={{position: 'absolute', inset: 0,
    pointerEvents: 'none', clipPath: s.reserveLyrics ? 'inset(0 0 0 1020px)' : undefined}}>
    <div style={{position: 'absolute', inset: 0, opacity: 0.65 + s.quiet * 0.35}}>
      <Halo frame={24} x={s.x} y={s.y} radius={s.radius}
        color={layout.shade === 'cream' ? FILM.colors.lavender : FILM.colors.cream} filled />
    </div>
    <svg width={0} height={0} aria-hidden style={{position: 'absolute'}}><defs>
      <clipPath id={clip} clipPathUnits="userSpaceOnUse"><path d={mediaExclusion(layout.media)} clipRule="evenodd" /></clipPath>
    </defs></svg>
    {s.placement && s.opacity > 0 ? <div style={{position: 'absolute', inset: 0,
      opacity: s.opening * s.opacity * s.quiet, clipPath: `url(#${clip})`}}>
      <StoryDoodles kind={s.group.kind} frame={s.localFrame} placement={s.placement}
        color={s.accent} highlightColor={FILM.colors.cream} />
    </div> : null}
  </div>;
};
