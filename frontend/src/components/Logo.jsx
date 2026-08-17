// Marque BaitWay definitive : passerelle + hameçon, sans ligne de base.
// Geometrie figee — ne pas modifier les traces.
export default function Logo({ size = 30, color = "#F5F7FA" }) {
  const small = size < 28;
  return (
    <svg viewBox="0 0 64 64" width={size} height={size} role="img" aria-label="BaitWay" style={{ flex: "none" }}>
      <g transform="translate(-2,-1)">
        {small ? (
          <>
            <path d="M34 25 V32 A7 7 0 0 1 18 32 V52" fill="none" stroke={color} strokeWidth="8" strokeLinecap="round" />
            <path d="M50 52 V30 A16 16 0 0 0 19 24" fill="none" stroke={color} strokeWidth="8" strokeLinecap="round" />
          </>
        ) : (
          <>
            <path d="M34 27 V34 A8 8 0 0 1 18 34 V52" fill="none" stroke={color} strokeWidth="6.5" strokeLinecap="round" />
            <path d="M50 52 V30 A16 16 0 0 0 20.1 22" fill="none" stroke={color} strokeWidth="6.5" strokeLinecap="round" />
          </>
        )}
      </g>
    </svg>
  );
}
