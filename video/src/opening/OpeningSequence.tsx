import React from 'react';
import {
  AbsoluteFill,
  Audio,
  Img,
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
  VERSE_START_FRAME,
} from './timing';

/** 공개 저장소에 개인 사진을 넣지 않고 props로 승인된 로컬 프레임만 전달합니다. */
export type OpeningSequenceProps = {
  imagePaths: string[];
  musicPath: string;
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

const MatchCutMontage: React.FC<{imagePaths: string[]}> = ({imagePaths}) => {
  const frame = useCurrentFrame();
  const isDemo = imagePaths.length === 0;
  const paths = isDemo ? Array.from({length: DEMO_COUNT}, (_, i) => String(i)) : imagePaths;
  const durations = distributeAcceleratingCuts(paths.length, MATCHCUT_END_FRAME);
  const index = findActiveCutIndex(durations, frame);
  const progress = (frame + 1) / MATCHCUT_END_FRAME;

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

const TitleBeat: React.FC = () => {
  const frame = useCurrentFrame();
  const scale = interpolate(frame, [0, 10, 22], [0.96, 1.045, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });
  const opacity = interpolate(frame, [0, 8], [0, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });
  return (
    <AbsoluteFill style={{
      background: '#F4EEE7', color: '#333638',
      justifyContent: 'center', alignItems: 'center',
    }}>
      <div style={{textAlign: 'center', opacity, transform: 'scale(' + scale + ')'}}>
        <div style={{font: '500 28px Arial, sans-serif', letterSpacing: 12, color: '#A26E55'}}>
          OUR FIRST YEAR
        </div>
        <div style={{font: '500 174px Georgia, serif', marginTop: 24, letterSpacing: -7}}>
          Sua, One Year.
        </div>
        <div style={{font: '500 45px Arial, sans-serif', marginTop: 24, letterSpacing: 3}}>
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
 * 음악 기준 초안: 0~9초 가속 매치컷 → 9~12초 강한 타이틀
 * → 12초부터 벌스/본편. 실제 Suno 음원 편곡/마커에 맞춰 조정.
 */
export const OpeningSequence: React.FC<OpeningSequenceProps> = ({
  imagePaths,
  musicPath,
}) => (
  <AbsoluteFill>
    <Sequence from={0} durationInFrames={MATCHCUT_END_FRAME}>
      <MatchCutMontage imagePaths={imagePaths}/>
    </Sequence>
    <Sequence from={MATCHCUT_END_FRAME}
      durationInFrames={VERSE_START_FRAME - MATCHCUT_END_FRAME}>
      <TitleBeat/>
    </Sequence>
    <Sequence from={VERSE_START_FRAME}
      durationInFrames={OPENING_DURATION_FRAMES - VERSE_START_FRAME}>
      <VerseBegins/>
    </Sequence>
    {musicPath ? <Audio src={staticFile(musicPath)} volume={0.85}/> : null}
  </AbsoluteFill>
);
