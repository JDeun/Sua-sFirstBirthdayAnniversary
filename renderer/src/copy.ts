// Copyright (c) JDeun. All rights reserved. Third-party licenses apply separately.
import data from './generated/copy.json';
import alignment from './generated/chorus-alignment.json';
import type {CopyKey} from './copy-keys';

export type FilmCopy = Readonly<{
  strings: Readonly<Record<string, string>>;
  assets: Readonly<{heartbeat?: string | null; prenatal?: string | null; birth?: string | null;
    greeting?: string | null}>;
  opening: Readonly<{birth_trim_before?: number}>;
  song_asset?: string | null;
}>;
export const COPY = data as FilmCopy;
export const SONG_ASSET = COPY.song_asset === undefined ? alignment.song_asset || null : COPY.song_asset;

/** Absent optional copy stays silent; supplied templates use named placeholders. */
export const copyText = (key: CopyKey, values: Readonly<Record<string, string | number>> = {}): string =>
  (COPY.strings[key] ?? '').replace(/\{(\w+)\}/g, (token, name: string) =>
    values[name] === undefined ? token : String(values[name]));
