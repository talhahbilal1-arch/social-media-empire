import React from 'react';
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
  Sequence,
  Easing,
} from 'remotion';

export type SocialMediaVideoProps = {
  brand: string;
  title: string;
  hook: string;
  bodyPoints: string[];
  cta: string;
  primaryColor: string;
  secondaryColor: string;
  backgroundVideo?: string;
};

export const SocialMediaVideo: React.FC<SocialMediaVideoProps> = ({
  brand,
  title,
  hook,
  bodyPoints,
  cta,
  primaryColor,
  secondaryColor,
  backgroundVideo,
}) => {
  const frame = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();

  // Timing (in frames)
  const hookStart = 0;
  const hookDuration = 4 * fps; // 4 seconds
  const titleStart = hookDuration;
  const titleDuration = 3 * fps; // 3 seconds
  const pointsStart = titleStart + titleDuration;
  const pointDuration = 4 * fps; // 4 seconds each
  const ctaStart = pointsStart + bodyPoints.length * pointDuration;

  return (
    <AbsoluteFill
      style={{
        background: `linear-gradient(180deg, ${primaryColor} 0%, ${secondaryColor} 100%)`,
      }}
    >
      {/* Animated background pattern */}
      <BackgroundPattern frame={frame} color={secondaryColor} />

      {/* Hook section */}
      <Sequence from={hookStart} durationInFrames={hookDuration}>
        <HookSection hook={hook} fps={fps} primaryColor={primaryColor} />
      </Sequence>

      {/* Title section */}
      <Sequence from={titleStart} durationInFrames={titleDuration}>
        <TitleSection title={title} fps={fps} />
      </Sequence>

      {/* Body points */}
      {bodyPoints.map((point, index) => (
        <Sequence
          key={index}
          from={pointsStart + index * pointDuration}
          durationInFrames={pointDuration}
        >
          <BodyPointSection
            point={point}
            index={index}
            fps={fps}
            primaryColor={primaryColor}
          />
        </Sequence>
      ))}

      {/* CTA section */}
      <Sequence from={ctaStart}>
        <CTASection cta={cta} fps={fps} primaryColor={primaryColor} />
      </Sequence>

      {/* Brand watermark */}
      <BrandWatermark brand={brand} />
    </AbsoluteFill>
  );
};

// Background animated pattern
const BackgroundPattern: React.FC<{frame: number; color: string}> = ({
  frame,
  color,
}) => {
  const rotation = interpolate(frame, [0, 900], [0, 360]);
  const scale = interpolate(frame, [0, 450, 900], [1, 1.2, 1]);

  return (
    <div
      style={{
        position: 'absolute',
        top: '50%',
        left: '50%',
        width: '200%',
        height: '200%',
        transform: `translate(-50%, -50%) rotate(${rotation}deg) scale(${scale})`,
        opacity: 0.1,
        background: `radial-gradient(circle at 50% 50%, ${color} 0%, transparent 50%)`,
      }}
    />
  );
};

// Hook section with typewriter effect
const HookSection: React.FC<{
  hook: string;
  fps: number;
  primaryColor: string;
}> = ({hook, fps, primaryColor}) => {
  const frame = useCurrentFrame();

  // Typewriter effect
  const charsToShow = Math.floor(
    interpolate(frame, [0, 2 * fps], [0, hook.length], {
      extrapolateRight: 'clamp',
    })
  );
  const displayText = hook.slice(0, charsToShow);

  // Fade in
  const opacity = interpolate(frame, [0, fps * 0.5], [0, 1], {
    extrapolateRight: 'clamp',
  });

  // Scale animation
  const scale = spring({
    frame,
    fps,
    config: {damping: 100, stiffness: 200},
  });

  return (
    <AbsoluteFill
      style={{
        justifyContent: 'center',
        alignItems: 'center',
        padding: 60,
      }}
    >
      <div
        style={{
          fontSize: 72,
          fontWeight: 'bold',
          color: 'white',
          textAlign: 'center',
          textShadow: '0 4px 20px rgba(0,0,0,0.3)',
          opacity,
          transform: `scale(${scale})`,
          lineHeight: 1.2,
        }}
      >
        {displayText}
        <span
          style={{
            opacity: frame % 30 < 15 ? 1 : 0,
            marginLeft: 4,
          }}
        >
          |
        </span>
      </div>
    </AbsoluteFill>
  );
};

// Title section with bounce animation
const TitleSection: React.FC<{title: string; fps: number}> = ({title, fps}) => {
  const frame = useCurrentFrame();

  const scale = spring({
    frame,
    fps,
    config: {damping: 80, stiffness: 300},
  });

  const opacity = interpolate(frame, [0, fps * 0.3], [0, 1], {
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill
      style={{
        justifyContent: 'center',
        alignItems: 'center',
        padding: 60,
      }}
    >
      <div
        style={{
          backgroundColor: 'white',
          borderRadius: 24,
          padding: '40px 60px',
          transform: `scale(${scale})`,
          opacity,
          boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
        }}
      >
        <div
          style={{
            fontSize: 64,
            fontWeight: 'bold',
            color: '#1a1a1a',
            textAlign: 'center',
            lineHeight: 1.2,
          }}
        >
          {title}
        </div>
      </div>
    </AbsoluteFill>
  );
};

// Body point section with slide-in animation
const BodyPointSection: React.FC<{
  point: string;
  index: number;
  fps: number;
  primaryColor: string;
}> = ({point, index, fps, primaryColor}) => {
  const frame = useCurrentFrame();

  const slideIn = spring({
    frame,
    fps,
    config: {damping: 80, stiffness: 200},
  });

  const translateX = interpolate(slideIn, [0, 1], [100, 0]);
  const opacity = interpolate(frame, [0, fps * 0.3], [0, 1], {
    extrapolateRight: 'clamp',
  });

  const numberColors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'];
  const numberColor = numberColors[index % numberColors.length];

  return (
    <AbsoluteFill
      style={{
        justifyContent: 'center',
        alignItems: 'center',
        padding: 60,
      }}
    >
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 30,
          backgroundColor: 'rgba(255,255,255,0.95)',
          borderRadius: 20,
          padding: '30px 50px',
          transform: `translateX(${translateX}px)`,
          opacity,
          boxShadow: '0 15px 50px rgba(0,0,0,0.2)',
          maxWidth: '90%',
        }}
      >
        <div
          style={{
            fontSize: 80,
            fontWeight: 'bold',
            color: numberColor,
            minWidth: 80,
            textAlign: 'center',
          }}
        >
          {index + 1}
        </div>
        <div
          style={{
            fontSize: 48,
            fontWeight: '600',
            color: '#1a1a1a',
            lineHeight: 1.3,
          }}
        >
          {point}
        </div>
      </div>
    </AbsoluteFill>
  );
};

// CTA section with pulsing animation
const CTASection: React.FC<{
  cta: string;
  fps: number;
  primaryColor: string;
}> = ({cta, fps, primaryColor}) => {
  const frame = useCurrentFrame();

  const scale = spring({
    frame,
    fps,
    config: {damping: 80, stiffness: 200},
  });

  // Pulsing effect
  const pulse = interpolate(
    frame % (fps * 0.8),
    [0, fps * 0.4, fps * 0.8],
    [1, 1.05, 1]
  );

  const opacity = interpolate(frame, [0, fps * 0.3], [0, 1], {
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill
      style={{
        justifyContent: 'center',
        alignItems: 'center',
        padding: 60,
      }}
    >
      <div
        style={{
          backgroundColor: 'white',
          borderRadius: 100,
          padding: '40px 80px',
          transform: `scale(${scale * pulse})`,
          opacity,
          boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
        }}
      >
        <div
          style={{
            fontSize: 52,
            fontWeight: 'bold',
            color: primaryColor,
            textAlign: 'center',
          }}
        >
          {cta}
        </div>
      </div>

      {/* Arrow animation */}
      <div
        style={{
          position: 'absolute',
          bottom: 200,
          fontSize: 80,
          opacity: interpolate(frame % fps, [0, fps / 2, fps], [0.5, 1, 0.5]),
          transform: `translateY(${interpolate(
            frame % fps,
            [0, fps / 2, fps],
            [0, -20, 0]
          )}px)`,
        }}
      >
        👇
      </div>
    </AbsoluteFill>
  );
};

// Brand watermark
const BrandWatermark: React.FC<{brand: string}> = ({brand}) => {
  const brandNames: Record<string, string> = {
    daily_deal_darling: 'Daily Deal Darling',
    fitnessmadeasy: 'FitnessMadeEasy',
    menopause_planner: 'Menopause Planner',
  };

  return (
    <div
      style={{
        position: 'absolute',
        bottom: 80,
        right: 40,
        fontSize: 24,
        fontWeight: '600',
        color: 'rgba(255,255,255,0.7)',
        textShadow: '0 2px 10px rgba(0,0,0,0.3)',
      }}
    >
      @{brandNames[brand] || brand}
    </div>
  );
};
