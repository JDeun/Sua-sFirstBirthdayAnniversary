import React from 'react';
import {
  AbsoluteFill,
  Audio,
  Img,
  OffthreadVideo,
  interpolate,
  Sequence,
  staticFile,
  useCurrentFrame,
} from 'remotion';
import {
  distributeAcceleratingCuts,
  findActiveCutIndex,
  MATCHCUT_END_FRAME,
  OPENING_DURATION_FRAMES,
  SONG_START_FRAME,
} from './timing';

/** 공개 저장소에 개인 사진을 넣지 않고 props로 승인된 로컬 프레임만 전달합니다. */
export type OpeningSequenceProps = {
  imagePaths: string[];
  musicPath: string;
  soundEffects?: {montagePath?: string; titleImpactPath?: string};
  timing?: {matchcutEndFrame: number; birthEndFrame?: number; songStartFrame?: number; verseStartFrame?: number};
  birthClip?: {path: string; sourceStartFrame?: number; withAudio?: boolean};
};

const demoPalettes = ['#E8C6B2', '#D7B399', '#CFAC92', '#D9BDA4', '#E2BDA8'];
const DEMO_COUNT = 48;

/** 인공 그래픽 데모. 실제 아이 얼굴을 생성하거나 모사하지 않습니다. */
const DemoAlignedPortrait: React.FC<{index: number}> = ({index}) => {
  const month = Math.min(11, Math.floor(index / 4));
  const accent = demoPalettes[month % demoPalettes.length];
  const hairColor = ['#7B675D', '#695346', '#55473D'][month % 3];
  return (
    <AbsoluteFill style={{
      background: 'linear-gradient(140deg, #F0ECE5, ' + accent + ')',
      justifyContent: 'center', alignItems: 'center',
    }}>
      <div style={{
        position: 'relative', width: 750, height: 750,
        borderRadius: 24, background: '#F6F0E6',
        boxShadow: '0 20px 75px rgba(48,46,44,0.15)',
      }}>
        <div style={{
          position: 'absolute', width: 520, height: 585,
          borderRadius: '50% 50% 45% 45%',
          left: 115, top: 65,
          background: '#E5B99B', border: '9px solid #DCAE8D',
        }}/>
        <div style={{
          position: 'absolute', width: 510, height: 170, borderRadius: '52% 52% 12% 12%',
          left: 120, top: 65, background: hairColor,
          opacity: 0.34 + month * 0.035,
        }}/>
        {[0, 1].map((eye) => (
          <div key={eye} style={{
            position: 'absolute', top: 355, left: eye === 0 ? 278 : 455,
            width: 20, height: 23, background: '#4A413C',
            borderRadius: '50%',
          }}/>
        ))}
        <div style={{
          position: 'absolute', width: 85, height: 30, left: 330, top: 494,
          borderBottom: '9px solid #B97D77', borderRadius: '0 0 50% 50%',
        }}/>
        <div style={{
          position: 'absolute', bottom: 25, left: 0, right: 0,
          textAlign: 'center', color: '#675A50', font: '600 22px Arial, sans-serif',
          letterSpacing: 4,
        }}>MONTH {String(month + 1).padStart(2, '0')}</div>
      </div>
      <div style={{
        position: 'absolute', top: 70, left: 100, font: '600 26px Arial, sans-serif',
        letterSpacing: 9, color: '#584F49',
      }}>DEMO · ALIGNMENT GUIDE</div>
    </AbsoluteFill>
  );
};

const MatchCutMontage: React.FC<{imagePaths: string[]; totalFrames: number}> = ({imagePaths, totalFrames}) => {
  const frame = useCurrentFrame();
  const isDemo = imagePaths.length === 0;
  const paths = isDemo ? Array.from({length: DEMO_COUNT}, (_, i) => String(i)) : imagePaths;
  const durations = distributeAcceleratingCuts(paths.length, totalFrames);
  const index = findActiveCutIndex(durations, frame);
  const progress = (frame + 1) / totalFrames;

  return (
    <AbsoluteFill style={{backgroundColor: '#242727'}}>
      {isDemo ? (
        <DemoAlignedPortrait index={index} />
      ) : (
        <>
          {/* 1080x1080으로 기하 정렬된 사진. 얼굴이 가운데 고정되도록 보존. */}
          <Img src={staticFile(paths[index])} style={{
            width: '100%', height: '100%', objectFit: 'cover',
            filter: 'blur(36px)', opacity: 0.34, transform: 'scale(1.12)',
          }}/>
          <div style={{
            position: 'absolute', width: 1080, height: 1080, top: 0,
            left: 420, overflow: 'hidden',
          }}>
            <Img src={staticFile(paths[index])} style={{
              width: '100%', height: '100%', objectFit: 'contain',
            }}/>
          </div>
        </>
      )}
      <div style={{
        position: 'absolute', bottom: 0, left: 0, height: 9, width: (progress * 100) + '%',
        background: '#E9D3BB',
      }}/>
      <div style={{
        position: 'absolute', right: 75, top: 70,
        font: '600 26px Arial, sans-serif', color: '#FFFFFF',
        letterSpacing: 7, opacity: 0.8,
      }}>THE FIRST YEAR · {index + 1}/{paths.length}</div>
    </AbsoluteFill>
  );
};

/**
 * 마스크 리빌: 타이틀 악센트에서 멈춘 뒤 읽을 시간을 확보합니다.
 * awesome-ai-motion의 설계 원칙을 참고해 Remotion으로 독자 구현.
 */
const TitleBeat: React.FC = () => {
  const frame = useCurrentFrame();
  const y = interpolate(frame, [0, 20], [115, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const subtitleOpacity = interpolate(frame, [16, 34], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  return (
    <AbsoluteFill style={{
      background: '#F4EEE7', color: '#333638',
      justifyContent: 'center', alignItems: 'center',
    }}>
      <div style={{textAlign: 'center', maxWidth: 1720}}>
        <div style={{font: '500 28px Arial, sans-serif', letterSpacing: 12, color: '#A26E55'}}>
          OUR FIRST YEAR
        </div>
        <div style={{overflow: 'hidden', marginTop: 24, height: 212}}>
          <div style={{
            font: '500 160px Georgia, serif', lineHeight: '204px',
            letterSpacing: -7, transform: 'translateY(' + y + '%)',
          }}>
            Sua, One Year.
          </div>
        </div>
        <div style={{
          font: '500 45px Arial, sans-serif', marginTop: 18,
          opacity: subtitleOpacity, letterSpacing: 3,
        }}>
          수아의 첫 번째 이야기
        </div>
      </div>
    </AbsoluteFill>
  );
};

const VerseBegins: React.FC = () => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 30], [0, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });
  return (
    <AbsoluteFill style={{
      background: 'linear-gradient(120deg, #DFD0C1, #F7F0E7)',
      justifyContent: 'center', alignItems: 'center', color: '#363738',
    }}>
      <div style={{opacity, textAlign: 'center'}}>
        <div style={{font: '500 28px Arial, sans-serif', letterSpacing: 11, color: '#A26E55'}}>
          CHAPTER ONE · THE BEGINNING
        </div>
        <div style={{font: '400 100px Georgia, serif', marginTop: 45}}>그리고, 우리의 이야기는 시작되었습니다.</div>
        <div style={{font: '400 25px Arial, sans-serif', marginTop: 60, color: '#84766B'}}>
          실제 성장 영상으로 교체될 데모 구간
        </div>
      </div>
    </AbsoluteFill>
  );
};

/**
 * 콜드 오픈: 매치컷에는 배경음악을 넣지 않습니다.
 * 0~9s 사진과 선택적 전환 효과음 → 9~12s 타이틀 + 선택적 임팩트 효과음
 * → 12s부터 Suno 완성곡의 처음(0:00)을 재생합니다.
 * 실제 시점은 props.timing으로 조정 가능; 음악 파일 자체를 잘라 시작하지 않습니다.
 */
export const OpeningSequence: React.FC<OpeningSequenceProps> = ({
  imagePaths,
  musicPath,
  soundEffects,
  timing,
  birthClip,
}) => {
  const matchcutEnd = timing?.matchcutEndFrame ?? MATCHCUT_END_FRAME;
  // 이전 버전 props의 verseStartFrame도 안전하게 읽되, 신규 키는 songStartFrame입니다.
  const songStart = timing?.songStartFrame ?? timing?.verseStartFrame ?? SONG_START_FRAME;
  const birthEnd = timing?.birthEndFrame ?? matchcutEnd + 4 * 30;
  if (
    !Number.isInteger(birthEnd) || birthEnd <= matchcutEnd || birthEnd >= songStart ||
    !Number.isInteger(matchcutEnd) ||
    !Number.isInteger(songStart) ||
    matchcutEnd < 2 ||
    songStart - birthEnd < 15 ||
    songStart >= OPENING_DURATION_FRAMES
  ) {
    throw new Error('콜드 오픈 마커가 잘못되었습니다. 타이틀과 노래 시작 시점을 확인하세요.');
  }
  return (
    <AbsoluteFill>
      <Sequence from={0} durationInFrames={matchcutEnd}>
        <MatchCutMontage imagePaths={imagePaths} totalFrames={matchcutEnd}/>
      </Sequence>
      <Sequence from={matchcutEnd} durationInFrames={birthEnd - matchcutEnd}>
        {birthClip?.path ? <OffthreadVideo src={staticFile(birthClip.path)} startFrom={birthClip.sourceStartFrame ?? 0} muted={!birthClip.withAudio} style={{width: '100%', height: '100%', objectFit: 'contain', background: '#181818'}}/> : <VerseBegins/>}
      </Sequence>
      <Sequence from={birthEnd} durationInFrames={songStart - birthEnd}>
        <TitleBeat/>
      </Sequence>
      <Sequence from={songStart} durationInFrames={OPENING_DURATION_FRAMES - songStart}>
        <VerseBegins/>
      </Sequence>
      {/* 선택적 효과음만 사용. 아무 파일도 지정하지 않으면 콜드 오픈은 무음입니다. */}
      {soundEffects?.montagePath ? (
        <Sequence from={0} durationInFrames={matchcutEnd} layout="none">
          <Audio src={staticFile(soundEffects.montagePath)} volume={0.35}/>
        </Sequence>
      ) : null}
      {soundEffects?.titleImpactPath ? (
        <Sequence from={birthEnd} durationInFrames={songStart - birthEnd} layout="none">
          <Audio src={staticFile(soundEffects.titleImpactPath)} volume={0.5}/>
        </Sequence>
      ) : null}
      {/* 완성곡의 첫 샘플이 정확히 노래 시작 프레임에서 재생됩니다. */}
      {musicPath ? (
        <Sequence from={songStart} durationInFrames={OPENING_DURATION_FRAMES - songStart} layout="none">
          <Audio src={staticFile(musicPath)} volume={0.85}/>
        </Sequence>
      ) : null}
    </AbsoluteFill>
  );
};
