export function calculateLostCandidates(current, next) {
  return Math.max(0, current - next);
}

export function calculateDropOffPercent(current, next) {
  if (!current || current === 0) return 0;
  const lost = calculateLostCandidates(current, next);
  return +(lost / current * 100).toFixed(1);
}

export function calculateConversion(numerator, denominator) {
  if (!denominator || denominator === 0) return 0;
  return +((numerator / denominator) * 100).toFixed(1);
}

export function findBiggestLeak(funnel) {
  if (!Array.isArray(funnel) || funnel.length < 2) return null;
  let best = null;
  for (let i = 0; i < funnel.length - 1; i++) {
    const cur = funnel[i];
    const next = funnel[i + 1];
    const percent = calculateDropOffPercent(cur.candidates, next.candidates);
    const lost = calculateLostCandidates(cur.candidates, next.candidates);
    if (!best || percent > best.percent) {
      best = {
        from: cur.stage,
        to: next.stage,
        percent,
        lost
      };
    }
  }
  return best;
}

export function calculateEndToEndConversion(applications, joined) {
  return calculateConversion(joined, applications);
}

export function calculateOfferAcceptance(offers, accepted) {
  return calculateConversion(accepted, offers);
}

export function calculateAcceptedNeverJoined(accepted, joined) {
  return Math.max(0, accepted - joined);
}

export function getStatusFromDropOff(dropOff) {
  if (dropOff > 30) return { label: 'Critical', color: 'red' };
  if (dropOff >= 18) return { label: 'Watch', color: 'amber' };
  return { label: 'Healthy', color: 'green' };
}
