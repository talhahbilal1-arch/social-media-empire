import React from 'react';
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
  Audio,
  Img,
  staticFile,
} from 'remotion';
import { TransitionSeries, linearTiming } from '@remotion/transitions';
import { fade } from '@remotion/transitions/fade';
import { BRAND_CONFIG } from '../config/brands';

// ─────────────────────────────────────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────────────────────────────────────

export interface SlideshowVideoProps {
  brand?: string;
  hook?: string;
  title?: string;
  points?: string[];
  cta?: string;
  images?: string[];
  voiceover?: string;
}

type Theme = { primary: string; secondary: string; accent: string };
type OpacityTimeline = { frames: number[]; values: number[] };

// ─────────────────────────────────────────────────────────────────────────────
// Constants
// ─────────────────────────────────────────────────────────────────────────────

/** Crossfade duration in frames. Must be shorter than any section. */
const CROSSFADE = 15; // 0.5s at 30fps

// ─────────────────────────────────────────────────────────────────────────────
// Helper: compute per-image opacity keyframes from background transition events
//
// This produces a deterministic { frames[], values[] } pair for each image.
// Using interpolate(frame, frames, values) gives a smooth frame-based opacity
// without any CSS transitions — the only correct approach in Remotion.
// ─────────────────────────────────────────────────────────────────────────────

function computeOpacityTimelines(
  imageCount: number,
  events: { at: number; toIndex: number }[],
  totalFrames: number
): OpacityTimeline[] {
  return Array.from({ length: imageCount }, (_, imgIdx) => {
    const frames: number[] = [];
    const values: number[] = [];
    let active = false;

    for (const ev of events) {
      if (ev.toIndex === imgIdx && !active) {
        // Fade in: 0 → 1 over [ev.at, ev.at + CROSSFADE]
        if (frames.length === 0 && ev.at > 0) {
          frames.push(0);
          values.push(0);
        }
        if (!frames.length || frames[frames.length - 1] < ev.at) {
          frames.push(ev.at);
          values.push(0);
        }
        frames.push(ev.at + CROSSFADE);
        values.push(1);
        active = true;
      } else if (ev.toIndex !== imgIdx && active) {
        // Fade out: 1 → 0 over [ev.at, ev.at + CROSSFADE]
        if (frames[frames.length - 1] < ev.at) {
          frames.push(ev.at);
          values.push(1);
        }
        frames.push(ev.at + CROSSFADE);
        values.push(0);
        active = false;
      }
    }

    if (!frames.length) {
      return { frames: [0, totalFrames], values: [0, 0] };
    }
    // Ensure monotonically increasing by deduplicating
    const deduped: { f: number; v: number }[] = [];
    for (let i = 0; i < frames.length; i++) {
      if (deduped.length === 0 || frames[i] > deduped[deduped.length - 1].f) {
        deduped.push({ f: frames[i], v: values[i] });
      }
    }
    // Add final frame
    const lastFrame = deduped[deduped.length - 1].f;
    if (lastFrame < totalFrames) {
      deduped.push({ f: totalFrames, v: active ? 1 : 0 });
    }
    return { frames: deduped.map(d => d.f), values: deduped.map(d => d.v) };
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// Main Component
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Multi-image slideshow video component — v2 (frame-based transitions)
 *
 * Structure (15 seconds / 450 frames at 30fps):
 *   0–90:   Hook   (image 0)
 *  90–165:  Title  (image 1)
 * 165–225:  Point 1 (image 2)
 * 225–285:  Point 2 (image 3)
 * 285–345:  Point 3 (image 2)
 * 345–450:  CTA    (image 0)
 *
 * All section transitions use @remotion/transitions TransitionSeries with fade().
 * All image crossfades use interpolate() — no CSS transitions anywhere.
 */
export const SlideshowVideo: React.FC<SlideshowVideoProps> = ({
  brand = 'daily_deal_darling',
  hook,
  title,
  points,
  cta,
  images,
  voiceover,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const config = BRAND_CONFIG[brand] ?? BRAND_CONFIG['daily_deal_darling'];

  const content = {
    hook: hook || config.content.hook,
    title: title || config.content.title,
    points: points?.length ? points : config.content.points,
    cta: cta || config.content.cta,
  };
  const imageList = images?.length ? images : config.images;
  // undefined → use brand config default; "" → no audio
  const voiceoverSrc = voiceover !== undefined ? voiceover : config.voiceover;

  // ─── Timing ───────────────────────────────────────────────────────────────
  const HOOK_DUR = Math.round(3 * fps);       // 90 at 30fps
  const TITLE_DUR = Math.round(2.5 * fps);    // 75
  const POINT_DUR = Math.round(2 * fps);      // 60
  const POINTS_START = HOOK_DUR + TITLE_DUR;  // 165
  const CTA_START = POINTS_START + content.points.length * POINT_DUR; // 345

  // ─── Background image transition events ───────────────────────────────────
  // Each event marks when a specific image becomes the "dominant" background.
  // Crossfades begin exactly at these frames — matching TransitionSeries boundaries.
  const imgAt = (i: number) => i % Math.max(imageList.length, 1);
  const bgEvents = [
    { at: 0,                             toIndex: imgAt(0) },
    { at: HOOK_DUR,                      toIndex: imgAt(1) },
    { at: POINTS_START,                  toIndex: imgAt(2) },
    { at: POINTS_START + POINT_DUR,      toIndex: imgAt(3) },
    { at: POINTS_START + 2 * POINT_DUR,  toIndex: imgAt(2) },
    { at: CTA_START,                     toIndex: imgAt(0) },
  ];

  const opacityTimelines = computeOpacityTimelines(imageList.length, bgEvents, durationInFrames);

  // ─── TransitionSeries durations ───────────────────────────────────────────
  // Each section except CTA gets +CROSSFADE so that when TransitionSeries
  // subtracts the overlap, the net start frame of each section == original timing.
  //
  // Derivation: TransitionSeries starts section N at:
  //   sum(durations[0..N-1]) - N * CROSSFADE
  // Adding CROSSFADE to each section cancels out, keeping original start times.
  const hookSeqDur  = HOOK_DUR + CROSSFADE;                         // 105
  const titleSeqDur = TITLE_DUR + CROSSFADE;                        // 90
  const pointSeqDur = POINT_DUR + CROSSFADE;                        // 75
  const ctaSeqDur   = durationInFrames - CTA_START;                 // 105

  // ─── Build dynamic point sections with interleaved transitions ────────────
  const pointElements: React.ReactNode[] = [];
  content.points.forEach((point, i) => {
    pointElements.push(
      <TransitionSeries.Sequence key={`pt-${i}`} durationInFrames={pointSeqDur}>
        <PointSection point={point} index={i} theme={config.theme} fps={fps} />
      </TransitionSeries.Sequence>
    );
    if (i < content.points.length - 1) {
      pointElements.push(
        <TransitionSeries.Transition
          key={`pt-tr-${i}`}
          presentation={fade()}
          timing={linearTiming({ durationInFrames: CROSSFADE })}
        />
      );
    }
  });

  return (
    <AbsoluteFill style={{ backgroundColor: '#000' }}>

      {/* ── Layer 1: Background images (frame-based crossfades — no CSS transitions) */}
      <SlideshowBackground
        images={imageList}
        frame={frame}
        fps={fps}
        durationInFrames={durationInFrames}
        opacityTimelines={opacityTimelines}
      />

      {/* ── Layer 2: Cinematic gradient for text readability */}
      <AbsoluteFill>
        <div
          style={{
            width: '100%',
            height: '100%',
            background: `linear-gradient(
              180deg,
              rgba(0,0,0,0.6) 0%,
              rgba(0,0,0,0.12) 20%,
              rgba(0,0,0,0.12) 75%,
              rgba(0,0,0,0.78) 100%
            )`,
          }}
        />
      </AbsoluteFill>

      {/* ── Layer 3: Vignette (cinematic edge darkening) */}
      <VignetteOverlay />

      {/* ── Layer 4: Film grain texture */}
      <FilmGrain frame={frame} />

      {/* ── Layer 5: Animated accent shapes */}
      <AnimatedShapes frame={frame} theme={config.theme} />

      {/* ── Layer 6: Content with smooth fade transitions */}
      <TransitionSeries>
        <TransitionSeries.Sequence durationInFrames={hookSeqDur}>
          <HookSection hook={content.hook} theme={config.theme} fps={fps} />
        </TransitionSeries.Sequence>

        <TransitionSeries.Transition
          presentation={fade()}
          timing={linearTiming({ durationInFrames: CROSSFADE })}
        />

        <TransitionSeries.Sequence durationInFrames={titleSeqDur}>
          <TitleSection title={content.title} theme={config.theme} fps={fps} />
        </TransitionSeries.Sequence>

        <TransitionSeries.Transition
          presentation={fade()}
          timing={linearTiming({ durationInFrames: CROSSFADE })}
        />

        {pointElements}

        <TransitionSeries.Transition
          presentation={fade()}
          timing={linearTiming({ durationInFrames: CROSSFADE })}
        />

        <TransitionSeries.Sequence durationInFrames={ctaSeqDur}>
          <CTASection cta={content.cta} theme={config.theme} fps={fps} />
        </TransitionSeries.Sequence>
      </TransitionSeries>

      {/* ── Layer 7: Brand watermark */}
      <BrandWatermark brand={config.displayName} theme={config.theme} />

      {/* ── Layer 8: Progress bar (8px) */}
      <ProgressBar frame={frame} durationInFrames={durationInFrames} theme={config.theme} />

      {voiceoverSrc && (
        <Audio
          src={voiceoverSrc.startsWith('http') ? voiceoverSrc : staticFile(voiceoverSrc)}
          volume={(f) =>
            interpolate(
              f,
              [0, fps * 0.3, durationInFrames - fps * 0.3, durationInFrames],
              [0, 1, 1, 0],
              { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
            )
          }
        />
      )}
    </AbsoluteFill>
  );
};

// ─────────────────────────────────────────────────────────────────────────────
// SlideshowBackground — frame-based crossfades between multiple images
//
// Critical: opacity for each image is computed via interpolate(frame, ...) only.
// CSS `transition` is explicitly forbidden here — it has no effect in Remotion's
// per-frame render pipeline and causes the jarring flash/cut artifacts.
// ─────────────────────────────────────────────────────────────────────────────

const SlideshowBackground: React.FC<{
  images: string[];
  frame: number;
  fps: number;
  durationInFrames: number;
  opacityTimelines: OpacityTimeline[];
}> = ({ images, frame, fps, durationInFrames, opacityTimelines }) => {
  // Ken Burns parameters — enhanced for more noticeable cinematic movement
  const kenBurnsConfigs = [
    { startScale: 1.0, endScale: 1.22, startX: 0,   endX: -4, startY: 0,   endY: -3 },
    { startScale: 1.15, endScale: 1.0, startX: -3,  endX: 3,  startY: -2,  endY: 2  },
    { startScale: 1.0, endScale: 1.18, startX: 3,   endX: -3, startY: 2,   endY: -2 },
    { startScale: 1.12, endScale: 1.0, startX: -2,  endX: 2,  startY: -3,  endY: 3  },
  ];

  return (
    <AbsoluteFill>
      {images.map((imagePath, index) => {
        const kb = kenBurnsConfigs[index % kenBurnsConfigs.length];
        const timeline = opacityTimelines[index];

        // Frame-based opacity — the ONLY correct approach for Remotion
        const opacity = timeline
          ? interpolate(frame, timeline.frames, timeline.values, {
              extrapolateLeft: 'clamp',
              extrapolateRight: 'clamp',
            })
          : 0;

        // Ken Burns: slow continuous motion across the full video duration
        const scale = interpolate(frame, [0, durationInFrames], [kb.startScale, kb.endScale], {
          extrapolateRight: 'clamp',
        });
        const translateX = interpolate(frame, [0, durationInFrames], [kb.startX, kb.endX], {
          extrapolateRight: 'clamp',
        });
        const translateY = interpolate(frame, [0, durationInFrames], [kb.startY, kb.endY], {
          extrapolateRight: 'clamp',
        });

        return (
          <AbsoluteFill
            key={index}
            style={{
              opacity,
              // NO CSS transition property — this is intentional
            }}
          >
            <div style={{ width: '100%', height: '100%', overflow: 'hidden' }}>
              <Img
                src={imagePath.startsWith('http') ? imagePath : staticFile(imagePath)}
                style={{
                  width: '100%',
                  height: '100%',
                  objectFit: 'cover',
                  transform: `scale(${scale}) translate(${translateX}%, ${translateY}%)`,
                }}
              />
            </div>
          </AbsoluteFill>
        );
      })}
    </AbsoluteFill>
  );
};

// ─────────────────────────────────────────────────────────────────────────────
// VignetteOverlay — radial darkening on all edges for cinematic look
// ─────────────────────────────────────────────────────────────────────────────

const VignetteOverlay: React.FC = () => (
  <AbsoluteFill style={{ pointerEvents: 'none' }}>
    <div
      style={{
        width: '100%',
        height: '100%',
        background: `radial-gradient(ellipse at 50% 50%, transparent 35%, rgba(0,0,0,0.72) 100%)`,
      }}
    />
  </AbsoluteFill>
);

// ─────────────────────────────────────────────────────────────────────────────
// FilmGrain — SVG turbulence noise that changes every frame for animated grain
// ─────────────────────────────────────────────────────────────────────────────

const FilmGrain: React.FC<{ frame: number }> = ({ frame }) => (
  <AbsoluteFill style={{ mixBlendMode: 'overlay', opacity: 0.06, pointerEvents: 'none' }}>
    <svg width="100%" height="100%" style={{ position: 'absolute', top: 0, left: 0 }}>
      <filter id={`grain-${frame}`}>
        <feTurbulence
          type="fractalNoise"
          baseFrequency="0.68"
          numOctaves="4"
          seed={frame}
          stitchTiles="stitch"
        />
        <feColorMatrix type="saturate" values="0" />
      </filter>
      <rect width="100%" height="100%" filter={`url(#grain-${frame})`} />
    </svg>
  </AbsoluteFill>
);

// ─────────────────────────────────────────────────────────────────────────────
// AnimatedShapes — enhanced prominence
// ─────────────────────────────────────────────────────────────────────────────

const AnimatedShapes: React.FC<{ frame: number; theme: Theme }> = ({ frame, theme }) => {
  const shapes = [
    { size: 480, x: -120, y: -100, speed: 0.3, opacity: 0.22 },
    { size: 360, x: 860,  y: 1400, speed: 0.2, opacity: 0.16 },
    { size: 300, x: 760,  y: 250,  speed: 0.35, opacity: 0.18 },
    { size: 200, x: 200,  y: 800,  speed: 0.25, opacity: 0.12 },
  ];

  return (
    <AbsoluteFill style={{ overflow: 'hidden', pointerEvents: 'none' }}>
      {shapes.map((shape, i) => {
        const movement = Math.sin(frame * shape.speed * 0.05) * 50;
        const scale = 1 + Math.sin(frame * shape.speed * 0.03) * 0.1;
        const hex = Math.round(shape.opacity * 255)
          .toString(16)
          .padStart(2, '0');

        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: shape.x,
              top: shape.y + movement,
              width: shape.size,
              height: shape.size,
              borderRadius: '50%',
              background: `radial-gradient(circle, ${theme.accent}${hex} 0%, transparent 70%)`,
              transform: `scale(${scale})`,
              filter: 'blur(45px)',
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};

// ─────────────────────────────────────────────────────────────────────────────
// KaraokeWord — highlighted word with frame-driven scale (no CSS transitions)
// ─────────────────────────────────────────────────────────────────────────────

const KaraokeWord: React.FC<{
  word: string;
  isActive: boolean;
  isSpoken: boolean;
  theme: Theme;
}> = ({ word, isActive, isSpoken, theme }) => {
  const frame = useCurrentFrame();
  const pulseScale = isActive ? 1 + Math.sin(frame * 0.3) * 0.04 : 1;

  return (
    <span
      style={{
        display: 'inline-block',
        marginRight: 12,
        padding: '3px 7px',
        borderRadius: 6,
        transform: `scale(${pulseScale})`,
        backgroundColor: isActive
          ? theme.accent
          : isSpoken
          ? `${theme.primary}70`
          : 'transparent',
        color: isActive || isSpoken ? 'white' : 'rgba(255,255,255,0.6)',
        textShadow: isActive
          ? `0 0 22px ${theme.accent}, 0 0 8px ${theme.accent}88, 0 3px 12px rgba(0,0,0,0.7)`
          : '0 2px 12px rgba(0,0,0,0.8), 0 1px 4px rgba(0,0,0,0.9)',
        // NOTE: no CSS `transition` — Remotion renders each frame independently
      }}
    >
      {word}
    </span>
  );
};

// ─────────────────────────────────────────────────────────────────────────────
// HookSection
// ─────────────────────────────────────────────────────────────────────────────

const HookSection: React.FC<{ hook: string; theme: Theme; fps: number }> = ({
  hook,
  theme,
  fps,
}) => {
  const frame = useCurrentFrame();

  const enterProgress = spring({
    frame,
    fps,
    config: { damping: 12, stiffness: 100, mass: 0.8 },
  });

  const scale = interpolate(enterProgress, [0, 1], [1.4, 1]);
  const opacity = interpolate(frame, [0, fps * 0.25], [0, 1], { extrapolateRight: 'clamp' });
  const blur = interpolate(frame, [0, fps * 0.25], [10, 0], { extrapolateRight: 'clamp' });

  const words = hook.split(' ');
  const startDelay = fps * 0.25;
  const currentWordIndex = Math.floor(
    interpolate(frame, [startDelay, startDelay + fps * 2.3], [0, words.length], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    })
  );

  return (
    <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', padding: 45 }}>
      <div style={{ transform: `scale(${scale})`, opacity, filter: `blur(${blur}px)` }}>
        <div
          style={{
            fontSize: 62,
            fontWeight: 900,
            color: 'white',
            textAlign: 'center',
            lineHeight: 1.4,
            letterSpacing: '-0.5px',
            maxWidth: 880,
            textShadow: '0 3px 16px rgba(0,0,0,0.9), 0 1px 4px rgba(0,0,0,1)',
          }}
        >
          {words.map((word, i) => (
            <KaraokeWord
              key={i}
              word={word}
              isActive={i === currentWordIndex}
              isSpoken={i < currentWordIndex}
              theme={theme}
            />
          ))}
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ─────────────────────────────────────────────────────────────────────────────
// TitleSection
// ─────────────────────────────────────────────────────────────────────────────

const TitleSection: React.FC<{ title: string; theme: Theme; fps: number }> = ({
  title,
  theme,
  fps,
}) => {
  const frame = useCurrentFrame();

  const scaleSpring = spring({ frame, fps, config: { damping: 14, stiffness: 140 } });
  const scale = interpolate(scaleSpring, [0, 1], [0.85, 1]);
  const opacity = interpolate(frame, [0, fps * 0.2], [0, 1], { extrapolateRight: 'clamp' });
  const y = interpolate(scaleSpring, [0, 1], [40, 0]);

  const words = title.split(' ');
  const startDelay = fps * 0.25;
  const currentWordIndex = Math.floor(
    interpolate(frame, [startDelay, startDelay + fps * 1.8], [0, words.length], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    })
  );

  return (
    <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', padding: 35 }}>
      <div style={{ transform: `scale(${scale}) translateY(${y}px)`, opacity }}>
        {/* Animated accent bar */}
        <div
          style={{
            width: interpolate(frame, [0, fps * 0.3], [0, 120], { extrapolateRight: 'clamp' }),
            height: 6,
            backgroundColor: theme.accent,
            borderRadius: 3,
            margin: '0 auto 20px',
            boxShadow: `0 0 18px ${theme.accent}88`,
          }}
        />

        <div
          style={{
            background: `linear-gradient(135deg, ${theme.primary} 0%, ${theme.secondary} 100%)`,
            borderRadius: 24,
            padding: '34px 48px',
            boxShadow: `0 24px 80px rgba(0,0,0,0.5), 0 0 0 2px ${theme.accent}30, 0 0 40px ${theme.primary}40`,
          }}
        >
          <div
            style={{
              fontSize: 50,
              fontWeight: 800,
              color: 'white',
              textAlign: 'center',
              lineHeight: 1.3,
              textShadow: '0 2px 12px rgba(0,0,0,0.5)',
            }}
          >
            {words.map((word, i) => {
              const isActive = i === currentWordIndex;
              const isSpoken = i < currentWordIndex;
              const pulseScale = isActive ? 1 + Math.sin(frame * 0.3) * 0.04 : 1;
              return (
                <span
                  key={i}
                  style={{
                    display: 'inline-block',
                    marginRight: 10,
                    padding: '2px 6px',
                    borderRadius: 6,
                    transform: `scale(${pulseScale})`,
                    backgroundColor: isActive ? 'rgba(255,255,255,0.3)' : 'transparent',
                    textShadow: isActive
                      ? '0 0 28px white, 0 2px 10px rgba(0,0,0,0.4)'
                      : '0 2px 10px rgba(0,0,0,0.4)',
                    opacity: isSpoken || isActive ? 1 : 0.72,
                  }}
                >
                  {word}
                </span>
              );
            })}
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ─────────────────────────────────────────────────────────────────────────────
// PointSection
// ─────────────────────────────────────────────────────────────────────────────

const PointSection: React.FC<{
  point: string;
  index: number;
  theme: Theme;
  fps: number;
}> = ({ point, index, theme, fps }) => {
  const frame = useCurrentFrame();

  const slideSpring = spring({ frame, fps, config: { damping: 13, stiffness: 115 } });
  const slideX = interpolate(slideSpring, [0, 1], [index % 2 === 0 ? -100 : 100, 0]);
  const opacity = interpolate(slideSpring, [0, 1], [0, 1]);

  const numberScale = spring({ frame: frame - 4, fps, config: { damping: 8, stiffness: 180 } });

  const words = point.split(' ');
  const startDelay = fps * 0.35;
  const currentWordIndex = Math.floor(
    interpolate(frame, [startDelay, startDelay + fps * 1.4], [0, words.length], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    })
  );

  const colors = [
    { bg: '#FF6B6B', text: '#fff' },
    { bg: '#4ECDC4', text: '#fff' },
    { bg: '#45B7D1', text: '#fff' },
  ];
  const color = colors[index % colors.length];

  return (
    <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', padding: 35 }}>
      <div
        style={{
          transform: `translateX(${slideX}px)`,
          opacity,
          display: 'flex',
          alignItems: 'center',
          gap: 22,
          background: 'rgba(255,255,255,0.95)',
          borderRadius: 20,
          padding: '24px 38px',
          boxShadow: `0 20px 60px rgba(0,0,0,0.4), 0 0 0 2px ${color.bg}30`,
          maxWidth: '94%',
          borderLeft: `6px solid ${color.bg}`,
        }}
      >
        <div
          style={{
            width: 68,
            height: 68,
            borderRadius: '50%',
            backgroundColor: color.bg,
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            flexShrink: 0,
            transform: `scale(${numberScale})`,
            boxShadow: `0 8px 24px ${color.bg}55`,
          }}
        >
          <span style={{ fontSize: 36, fontWeight: 900, color: color.text }}>{index + 1}</span>
        </div>

        <div
          style={{
            fontSize: 37,
            fontWeight: 700,
            lineHeight: 1.3,
            textShadow: '0 1px 4px rgba(0,0,0,0.12)',
          }}
        >
          {words.map((word, i) => {
            const isActive = i === currentWordIndex;
            const isSpoken = i < currentWordIndex;
            const pulseScale = isActive ? 1.05 : 1;
            return (
              <span
                key={i}
                style={{
                  display: 'inline-block',
                  marginRight: 9,
                  padding: '2px 5px',
                  borderRadius: 4,
                  transform: `scale(${pulseScale})`,
                  backgroundColor: isActive
                    ? color.bg
                    : isSpoken
                    ? `${color.bg}38`
                    : 'transparent',
                  color: isActive ? 'white' : '#1a1a1a',
                  // NOTE: no CSS `transition` — each frame is rendered independently
                }}
              >
                {word}
              </span>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ─────────────────────────────────────────────────────────────────────────────
// CTASection
// ─────────────────────────────────────────────────────────────────────────────

const CTASection: React.FC<{ cta: string; theme: Theme; fps: number }> = ({ cta, theme, fps }) => {
  const frame = useCurrentFrame();

  const enterSpring = spring({ frame, fps, config: { damping: 10, stiffness: 95 } });
  const scale = interpolate(enterSpring, [0, 1], [0.55, 1]);
  const opacity = interpolate(enterSpring, [0, 1], [0, 1]);

  const pulsePhase = (frame % (fps * 0.55)) / (fps * 0.55);
  const glowSize = 20 + Math.sin(pulsePhase * Math.PI * 2) * 14;
  const buttonScale = 1 + Math.sin(pulsePhase * Math.PI * 2) * 0.028;

  const arrowY = interpolate(frame % fps, [0, fps / 2, fps], [0, -14, 0]);
  const arrowOpacity = interpolate(frame % fps, [0, fps / 2, fps], [0.6, 1, 0.6]);

  return (
    <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', padding: 35 }}>
      <div style={{ transform: `scale(${scale})`, opacity, textAlign: 'center' }}>
        <div
          style={{
            background: `linear-gradient(135deg, ${theme.accent} 0%, ${theme.primary} 100%)`,
            borderRadius: 100,
            padding: '34px 70px',
            transform: `scale(${buttonScale})`,
            boxShadow: `0 0 ${glowSize}px ${theme.accent}88, 0 0 ${glowSize * 2}px ${theme.accent}44, 0 20px 50px rgba(0,0,0,0.35)`,
            border: '2.5px solid rgba(255,255,255,0.3)',
          }}
        >
          <div
            style={{
              fontSize: 46,
              fontWeight: 800,
              color: 'white',
              textShadow: '0 3px 12px rgba(0,0,0,0.4)',
              letterSpacing: '0.5px',
            }}
          >
            {cta}
          </div>
        </div>

        <div
          style={{
            marginTop: 30,
            fontSize: 58,
            opacity: arrowOpacity,
            transform: `translateY(${arrowY}px)`,
            textShadow: '0 4px 16px rgba(0,0,0,0.6)',
          }}
        >
          <span role="img" aria-label="point down">
            {'\u{1F447}'}
          </span>
        </div>

        <div
          style={{
            marginTop: 14,
            fontSize: 28,
            fontWeight: 600,
            color: 'rgba(255,255,255,0.9)',
            textShadow: '0 2px 12px rgba(0,0,0,0.7)',
            letterSpacing: '0.3px',
          }}
        >
          Save this for later!
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ─────────────────────────────────────────────────────────────────────────────
// BrandWatermark
// ─────────────────────────────────────────────────────────────────────────────

const BrandWatermark: React.FC<{ brand: string; theme: Theme }> = ({ brand, theme }) => (
  <div
    style={{
      position: 'absolute',
      bottom: 105,
      left: 0,
      right: 0,
      display: 'flex',
      justifyContent: 'center',
    }}
  >
    <div
      style={{
        background: 'rgba(0,0,0,0.52)',
        backdropFilter: 'blur(10px)',
        padding: '10px 24px',
        borderRadius: 30,
        border: `1px solid ${theme.accent}40`,
        boxShadow: `0 4px 20px rgba(0,0,0,0.3)`,
      }}
    >
      <span
        style={{
          fontSize: 21,
          fontWeight: 600,
          color: 'white',
          letterSpacing: '0.5px',
          textShadow: '0 1px 6px rgba(0,0,0,0.5)',
        }}
      >
        @{brand}
      </span>
    </div>
  </div>
);

// ─────────────────────────────────────────────────────────────────────────────
// ProgressBar — 8px, prominent, glowing
// ─────────────────────────────────────────────────────────────────────────────

const ProgressBar: React.FC<{
  frame: number;
  durationInFrames: number;
  theme: Theme;
}> = ({ frame, durationInFrames, theme }) => {
  const progress = (frame / durationInFrames) * 100;
  return (
    <div
      style={{
        position: 'absolute',
        bottom: 0,
        left: 0,
        right: 0,
        height: 8,
        background: 'rgba(255,255,255,0.15)',
      }}
    >
      <div
        style={{
          width: `${progress}%`,
          height: '100%',
          background: `linear-gradient(90deg, ${theme.accent}, ${theme.primary})`,
          boxShadow: `0 0 22px ${theme.accent}, 0 0 8px ${theme.accent}88`,
        }}
      />
    </div>
  );
};

export default SlideshowVideo;
