// Copyright (c) JDeun. All rights reserved. Third-party licenses apply separately.
import {COPY, copyText} from '../copy';
import {Audio, Video} from '@remotion/media';
import {AbsoluteFill, CanvasImage, interpolate, Sequence, staticFile, useCurrentFrame} from 'remotion';
import {OPENING_PHOTOS as allowed} from '../opening-media';
import {Greeting} from '../Greeting';
import {FILM} from '../theme';
import {NARRATIVE} from './edit';
import {NARRATIVE_FONT} from './NarrativeFonts';

const {opening} = NARRATIVE;
const Heartbeat = () => {
  const frame = useCurrentFrame();
  const end = opening.ultrasound_frames + opening.matchcut_frames;
  const volume = interpolate(frame, [0, Math.min(12, end / 3), end - Math.min(36, end / 3), end], [0, 1, 1, 0],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return COPY.assets.heartbeat ? <Audio src={staticFile(COPY.assets.heartbeat)} durationInFrames={end} volume={volume} /> : null;
};
const Prenatal = () => {
  const frame = useCurrentFrame();
  const duration = opening.ultrasound_frames;
  const fade = Math.min(24, duration / 2);
  const opacity = interpolate(frame, [0, fade, duration - fade, duration], [0, 1, 1, 0],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <AbsoluteFill style={{background: '#08090A'}}>
    <div style={{position: 'absolute', left: 704, top: 202, width: 1136, height: 656,
      padding: 16, boxSizing: 'border-box', borderRadius: 36, opacity,
      background: '#16191A', outline: '1px solid rgba(255,248,240,0.24)',
      boxShadow: '0 32px 100px rgba(0,0,0,0.4)'}}>
      <div style={{width: '100%', height: '100%', borderRadius: 24, overflow: 'hidden'}}>
        {COPY.assets.prenatal ? <Video src={staticFile(COPY.assets.prenatal)} muted durationInFrames={duration}
          objectFit="contain" style={{width: '100%', height: '100%'}} /> : null}
      </div>
    </div>
    <div style={{position: 'absolute', left: 112, top: 310, width: 548, opacity,
      color: FILM.colors.cream, fontFamily: NARRATIVE_FONT, fontWeight: 400}}>
      <div style={{height: 1, width: 54, background: FILM.colors.cream, opacity: 0.4, marginBottom: 30}} />
      <div style={{fontSize: 84, letterSpacing: -3, fontWeight: 600, marginBottom: 28}}>{copyText('narrative.NarrativeOpening.011')}</div>
      <div style={{fontSize: 48, letterSpacing: -1.3, lineHeight: 1.8, opacity: 0.88}}>
        {copyText('narrative.NarrativeOpening.012')}<br />{copyText('narrative.NarrativeOpening.013')}</div>
    </div>
  </AbsoluteFill>;
};

const ReverseMemories = () => {
  if (!allowed.length) return null;
  const collection = opening.matchcut_mode === 'full' ? allowed :
    Array.from({length: 90}, (_, i) => allowed[Math.round(i * (allowed.length - 1) / 89)]);
  return <AbsoluteFill>{collection.map((photo, index) => <Sequence key={`${index}-${photo.stem}`}
    from={Math.round(index * opening.matchcut_frames / collection.length)}
    durationInFrames={Math.round((index + 1) * opening.matchcut_frames / collection.length) -
      Math.round(index * opening.matchcut_frames / collection.length)}>
    <CanvasImage src={staticFile(photo.asset)} width={1920} height={1080} fit="fill" />
  </Sequence>)}<div style={{position: 'absolute', inset: 38, borderRadius: 30,
    border: '2px solid rgba(255,248,240,0.42)', pointerEvents: 'none'}} /></AbsoluteFill>;
};

const FirstMeeting = () => {
  const frame = useCurrentFrame();
  const duration = opening.duration_in_frames - opening.birth_start_frame;
  const opacity = interpolate(frame, [0, Math.min(30, duration / 3), duration - Math.min(24, duration / 3), duration], [0, 1, 1, 0],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const volume = interpolate(frame, [0, Math.min(24, duration / 3), duration - Math.min(24, duration / 3), duration], [0, 0.55, 0.55, 0],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <AbsoluteFill style={{opacity}}>
    <div style={{position: 'absolute', left: 60, top: 28, width: 1800, height: 1024,
      padding: 12, boxSizing: 'border-box', background: FILM.colors.cream, borderRadius: 36,
      outline: '1px solid rgba(255,248,240,0.2)'}}>
      <div style={{width: '100%', height: '100%', borderRadius: 26, overflow: 'hidden'}}>
        {COPY.assets.birth ? <Video src={staticFile(COPY.assets.birth)} trimBefore={COPY.opening.birth_trim_before ?? 0} durationInFrames={duration}
          volume={volume} objectFit="contain" style={{width: '100%', height: '100%'}} /> : null}
      </div>
    </div>
    {frame >= 60 ? <div style={{position: 'absolute', left: 112, bottom: 82,
      color: FILM.colors.ink, fontFamily: NARRATIVE_FONT, lineHeight: 1.5,
      padding: '16px 24px', background: 'rgba(255,248,240,0.94)', borderRadius: 18,
      boxShadow: '0 8px 30px rgba(0,0,0,0.1)'}}>
      <div style={{fontSize: 32, fontWeight: 600, letterSpacing: 1}}>{copyText('narrative.NarrativeOpening.014')}</div>
      <div style={{fontSize: 25, fontWeight: 400, color: FILM.colors.muted}}>{copyText('narrative.NarrativeOpening.015')}</div>
    </div> : null}
  </AbsoluteFill>;
};

export const NarrativeOpening = () => {
  if (opening.duration_in_frames <= 0) return null;
  const heartbeatFrames = opening.ultrasound_frames + opening.matchcut_frames;
  const titleFrames = Math.min(120, opening.birth_start_frame - opening.title_start_frame);
  const birthFrames = opening.duration_in_frames - opening.birth_start_frame;
  return <AbsoluteFill style={{background: '#000'}}>
    {heartbeatFrames > 0 ? <Sequence name={copyText('narrative.NarrativeOpening.016')}
      durationInFrames={heartbeatFrames}><Heartbeat /></Sequence> : null}
    {opening.ultrasound_frames > 0 ? <Sequence name={copyText('narrative.NarrativeOpening.017')}
      durationInFrames={opening.ultrasound_frames}><Prenatal /></Sequence> : null}
    {opening.matchcut_frames > 0 ? <Sequence name={copyText('narrative.NarrativeOpening.018')}
      from={opening.ultrasound_frames} durationInFrames={opening.matchcut_frames}>
      <ReverseMemories /></Sequence> : null}
    {titleFrames > 0 ? <Sequence name={copyText('Greeting.003')} from={opening.title_start_frame}
      durationInFrames={titleFrames}>
      <Greeting fontFamily={NARRATIVE_FONT} />
      <div style={{position: 'absolute', inset: 76, borderRadius: 34,
        border: '1px solid rgba(255,248,240,0.14)', pointerEvents: 'none'}} />
    </Sequence> : null}
    {birthFrames > 0 ? <Sequence name={copyText('narrative.NarrativeOpening.019')}
      from={opening.birth_start_frame} durationInFrames={birthFrames}><FirstMeeting /></Sequence> : null}
  </AbsoluteFill>;
};
