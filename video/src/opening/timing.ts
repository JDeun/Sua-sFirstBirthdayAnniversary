/** 음악의 실제 진입점을 확인한 뒤 프레임 수를 교체할 수 있는 설정. */
export const OPENING_FPS = 30;
export const MATCHCUT_END_FRAME = 8 * OPENING_FPS;
export const SONG_START_FRAME = 15 * OPENING_FPS; // Suno 곡 파일의 0초 시작 지점
export const OPENING_DURATION_FRAMES = 21 * OPENING_FPS;

/**
 * 사진은 현재에서 출생 순으로 주어졌다는 전제. 초반보다 후반이 빠르게 전환되도록
 * 정수 프레임을 배분하며, 모든 사진에 최소 2프레임을 보장한다.
 */
export const distributeAcceleratingCuts = (
  count: number,
  totalFrames: number,
  minimumFrames = 2,
): number[] => {
  if (!Number.isInteger(count) || !Number.isInteger(totalFrames) || count < 0 || totalFrames < 0) {
    throw new Error('사진 수와 전체 프레임은 0 이상의 정수여야 합니다.');
  }
  if (!Number.isInteger(minimumFrames) || minimumFrames < 1) {
    throw new Error('최소 노출 프레임은 1 이상 정수여야 합니다.');
  }
  if (count === 0) return [];
  if (count * minimumFrames > totalFrames) {
    throw new Error('정해진 매치컷 길이에 비해 사진이 너무 많습니다.');
  }
  const weights = Array.from(
    {length: count}, (_, i) => Math.exp(-1.7 * i / Math.max(1, count - 1)),
  );
  const available = totalFrames - count * minimumFrames;
  const sum = weights.reduce((a, b) => a + b, 0);
  const raw = weights.map((w) => available * w / sum);
  const allocations = raw.map(Math.floor);
  let leftover = available - allocations.reduce((a, b) => a + b, 0);
  const ranking = raw.map((value, index) => ({index, fraction: value - Math.floor(value)}))
    .sort((a, b) => b.fraction - a.fraction || a.index - b.index);
  for (let i = 0; i < leftover; i++) allocations[ranking[i].index]++;
  return allocations.map((v) => v + minimumFrames);
};

export const findActiveCutIndex = (durations: number[], frame: number): number => {
  let elapsed = 0;
  for (let i = 0; i < durations.length; i++) {
    elapsed += durations[i];
    if (frame < elapsed) return i;
  }
  return Math.max(durations.length - 1, 0);
};
