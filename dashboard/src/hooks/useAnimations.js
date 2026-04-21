import { useEffect, useRef, useState } from 'react';

/** Intersection Observer – triggers `visible` class when element enters viewport */
export function useReveal(threshold = 0.15) {
  const ref = useRef(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const obs = new IntersectionObserver(
      ([entry]) => { if (entry.isIntersecting) { setVisible(true); obs.disconnect(); } },
      { threshold }
    );
    obs.observe(el);
    return () => obs.disconnect();
  }, [threshold]);

  return [ref, visible];
}

/** Animated counter – counts from 0 to `end` */
export function useCountUp(end, duration = 2000, startOnVisible = true) {
  const [count, setCount] = useState(0);
  const [started, setStarted] = useState(!startOnVisible);
  const ref = useRef(null);

  useEffect(() => {
    if (!startOnVisible) return;
    const el = ref.current;
    if (!el) return;
    const obs = new IntersectionObserver(
      ([entry]) => { if (entry.isIntersecting) { setStarted(true); obs.disconnect(); } },
      { threshold: 0.3 }
    );
    obs.observe(el);
    return () => obs.disconnect();
  }, [startOnVisible]);

  useEffect(() => {
    if (!started) return;
    let frame;
    const start = performance.now();
    const step = (now) => {
      const progress = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
      setCount(Math.round(eased * end));
      if (progress < 1) frame = requestAnimationFrame(step);
    };
    frame = requestAnimationFrame(step);
    return () => cancelAnimationFrame(frame);
  }, [started, end, duration]);

  return [count, ref];
}

/** Format currency with $ and commas */
export function formatCurrency(value) {
  if (value == null) return '—';
  if (value >= 1_000_000) return `$${(value / 1_000_000).toFixed(2)}M`;
  if (value >= 1_000) return `$${(value / 1_000).toFixed(0)}K`;
  return `$${value.toLocaleString()}`;
}

/** Format large numbers with K/M suffix */
export function formatNumber(value) {
  if (value == null) return '—';
  if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(1)}M`;
  if (value >= 1_000) return `${(value / 1_000).toFixed(0)}K`;
  return value.toLocaleString();
}

/** Status badge color */
export function statusColor(status) {
  const s = (status || '').toLowerCase();
  if (s.includes('approved')) return 'badge-emerald';
  if (s.includes('lodged')) return 'badge-amber';
  if (s.includes('assessment')) return 'badge-cyan';
  if (s.includes('refused') || s.includes('reject')) return 'badge-rose';
  return 'badge-purple';
}

/** ROI badge color */
export function roiColor(roi) {
  const r = (roi || '').toLowerCase();
  if (r.includes('very high')) return 'badge-emerald';
  if (r.includes('high')) return 'badge-cyan';
  if (r.includes('moderate')) return 'badge-amber';
  return 'badge-purple';
}

/** Heatmap intensity (0–1) */
export function heatIntensity(count, max) {
  if (!max) return 0;
  return Math.min(count / max, 1);
}

/** Heatmap color from intensity */
export function heatColor(intensity) {
  // Gradient from dark blue → cyan → green → yellow → red
  if (intensity < 0.25) return `rgba(0, 150, 255, ${0.2 + intensity * 2})`;
  if (intensity < 0.5) return `rgba(0, 240, 200, ${0.3 + intensity * 1.4})`;
  if (intensity < 0.75) return `rgba(200, 220, 50, ${0.4 + intensity * 0.8})`;
  return `rgba(255, 80, 60, ${0.5 + intensity * 0.5})`;
}
