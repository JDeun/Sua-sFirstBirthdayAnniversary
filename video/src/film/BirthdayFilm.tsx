import React from 'react';
import {
  AbsoluteFill,
  Audio,
  Img,
  interpolate,
  OffthreadVideo,
  Sequence,
  staticFile,
  useCurrentFrame,
} from 'remotion';
import {OpeningSequence, type OpeningSequenceProps} from '../opening/OpeningSequence';
import {SONG_START_FRAME} from '../opening/timing';

/**
 * All paths are relative to video/public and are curated on the user's computer.
 * startFrame is relative to the start of the full song, NEVER the film's first frame.
 * Source video audio is intentionally muted: the completed Suno song is the master.
 */
export type FilmShot = {
  kind: 'image' | 'video' | 'placeholder';
  path?: string;
  startFrame: number;
  durationFrames: number;
  sourceStartFrame?: number;
  chapter?: string;
  caption?: string;
  treatment?: 'cinematic' | 'scrapbook' | 'variety';
};

export type BirthdayFilmProps = {
  opening: OpeningSequenceProps;
  songDurationFrames: number;
  endCardFrames?: number;
  shots: FilmShot[];
};

const theme = {
  ink: '#343330',
  paper: '#F4EDE3',
  accent: '#B48167',
};

export const songStartOf = (props: BirthdayFilmProps): number =>
  props.opening.timing?.songStartFrame ??
  props.opening.timing?.verseStartFrame ??
  SONG_START_FRAME;

export const filmDurationOf = (props: BirthdayFilmProps): number => {
  const songStart = songStartOf(props);
  if (!Number.isInteger(songStart) || songStart < 1 || songStart >= 630) {
    throw new Error('완성곡 시작 시점은 오프닝 21초 안의 정수 프레임이어야 합니다.');
  }
  if (!Number.isInteger(props.songDurationFrames) || props.songDurationFrames <= 0) {
    throw new Error('songDurationFrames는 양의 정수여야 합니다.');
  }
  const end = props.endCardFrames ?? 120;
  if (!Number.isInteger(end) || end < 0 || end >= props.songDurationFrames) {
    throw new Error('엔딩 카드 길이를 확인하세요.');
  }
  const storyFrames = props.songDurationFrames - end;
  const sorted = [...props.shots].sort((a, b) => a.startFrame - b.startFrame);
  let next = 0;
  for (const shot of sorted) {
    if (!Number.isInteger(shot.startFrame) || !Number.isInteger(shot.durationFrames) ||
        shot.startFrame !== next || shot.durationFrames < 1 ||
        (shot.kind !== 'placeholder' && (!shot.path || !shot.path.startsWith('media/')))) {
      throw new Error('스토리보드 프레임이 연속되지 않거나 로컬 미디어 경로가 잘못되었습니다.');
    }
    next += shot.durationFrames;
  }
  if (props.shots.length > 0 && next !== storyFrames) {
    throw new Error('승인 샷의 총 프레임이 엔딩을 제외한 음악 길이와 일치해야 합니다.');
  }
  return songStart + props.songDurationFrames;
};

const Placeholder: React.FC<{chapter?: string}> = ({chapter}) => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{
      background: 'linear-gradient(135deg, #E5D4C4, #F7F2E9 55%, #BFCAC1)',
      justifyContent: 'center', alignItems: 'center', color: theme.ink,
    }}>
      <div style={{
        width: 820, height: 690, borderRadius: 36,
        background: 'rgba(255,255,255,0.32)',
        transform: 'rotate(-3deg) scale(' + (1 + frame / 10000) + ')',
        border: '2px solid rgba(255,255,255,0.65)',
      }}/>
      <div style={{
        position: 'absolute', font: '500 55px Georgia, serif',
        textAlign: 'center', letterSpacing: 2,
      }}>{chapter ?? 'OUR FIRST YEAR'}</div>
      <div style={{
        position: 'absolute', bottom: 55,
        font: '500 22px Arial, sans-serif', letterSpacing: 6,
      }}>SYNTHETIC STORYBOARD PREVIEW</div>
    </AbsoluteFill>
  );
};

const StoryShot: React.FC<{shot: FilmShot}> = ({shot}) => {
  const frame = useCurrentFrame();
  const progress = frame / Math.max(1, shot.durationFrames - 1);
  const zoom = 1.015 + progress * 0.035;
  const accentBg = shot.treatment === 'scrapbook' ? '#F8F2DE' :
    shot.treatment === 'variety' ? '#DDE7ED' : theme.paper;

  if (shot.kind === 'placeholder') return <Placeholder chapter={shot.chapter}/>;
  const source = staticFile(shot.path!);

  return (
    <AbsoluteFill style={{background: accentBg}}>
      {shot.kind === 'image' ? (
        <AbsoluteFill>
          <Img src={source} style={{
            width: '100%', height: '100%', objectFit: 'cover',
            filter: 'blur(45px) brightness(0.7)', transform: 'scale(1.1)',
          }}/>
          <Img src={source} style={{
            position: 'absolute', width: '100%', height: '100%',
            objectFit: 'contain', transform: 'scale(' + zoom + ')',
          }}/>
        </AbsoluteFill>
      ) : (
        <AbsoluteFill style={{background: '#28292A'}}>
          <OffthreadVideo
            src={source}
            muted
            startFrom={shot.sourceStartFrame ?? 0}
            style={{width: '100%', height: '100%', objectFit: 'contain'}}
          />
        </AbsoluteFill>
      )}
      {shot.chapter ? (
        <div style={{
          position: 'absolute', top: 72, left: 100, right: 100,
          font: '600 26px Arial, sans-serif', letterSpacing: 3,
          color: '#FFFFFF', textShadow: '0 2px 9px rgba(0,0,0,0.75)',
        }}>{shot.chapter}</div>
      ) : null}
      {shot.caption ? (
        <div style={{
          position: 'absolute', bottom: 85, left: 90, right: 90,
          textAlign: 'center', font: '500 43px Arial, sans-serif',
          color: '#FFFFFF', lineHeight: 1.4,
          textShadow: '0 2px 12px rgba(0,0,0,0.8)',
        }}>{shot.caption}</div>
      ) : null}
    </AbsoluteFill>
  );
};

const EndCard: React.FC = () => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 24], [0, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });
  return (
    <AbsoluteFill style={{
      background: theme.paper, color: theme.ink,
      justifyContent: 'center', alignItems: 'center', textAlign: 'center',
    }}>
      <div style={{opacity}}>
        <div style={{font: '500 32px Arial, sans-serif', color: theme.accent,
          letterSpacing: 6}}>2025.12.19 — 2026.12.19</div>
        <div style={{font: '400 133px Georgia, serif', marginTop: 30}}>수아야, 사랑해.</div>
        <div style={{font: '500 32px Arial, sans-serif', letterSpacing: 6, marginTop: 50}}>
          OUR FIRST YEAR, FOREVER.
        </div>
      </div>
    </AbsoluteFill>
  );
};

const demoShots = (storyFrames: number): FilmShot[] => {
  const names = ['처음 만난 날', '조금씩 자라던 계절', '웃음으로 가득한 하루', '우리의 첫 번째 생일'];
  const base = Math.floor(storyFrames / names.length);
  return names.map((name, i) => ({
    kind: 'placeholder' as const,
    startFrame: base * i,
    durationFrames: i === names.length - 1 ? storyFrames - base * i : base,
    chapter: name,
  }));
};

/**
 * Final film: reverse matchcut -> birth footage -> title -> complete song from audio sample 0
 * with user-approved chronological photos/clips. No generated child imagery.
 */
export const BirthdayFilm: React.FC<BirthdayFilmProps> = (props) => {
  const total = filmDurationOf(props);
  const songStart = songStartOf(props);
  const endCardFrames = props.endCardFrames ?? 120;
  const storyFrames = props.songDurationFrames - endCardFrames;
  const shots = props.shots.length ? props.shots : demoShots(storyFrames);

  return (
    <AbsoluteFill style={{background: theme.paper}}>
      <Sequence from={0} durationInFrames={songStart}>
        <OpeningSequence {...props.opening} musicPath=""/>
      </Sequence>
      {shots.map((shot, index) => (
        <Sequence
          key={index}
          from={songStart + shot.startFrame}
          durationInFrames={shot.durationFrames}
        >
          <StoryShot shot={shot}/>
        </Sequence>
      ))}
      <Sequence from={total - endCardFrames} durationInFrames={endCardFrames}>
        <EndCard/>
      </Sequence>
      {props.opening.musicPath ? (
        <Sequence from={songStart} durationInFrames={props.songDurationFrames} layout="none">
          <Audio src={staticFile(props.opening.musicPath)} volume={0.9}/>
        </Sequence>
      ) : null}
    </AbsoluteFill>
  );
};
