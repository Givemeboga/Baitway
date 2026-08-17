// Jetons visuels BaitWay — source unique pour toute l'interface.
// Les couleurs de severite ne servent QU'A une severite : jamais de decoration.

export const color = {
  bg: "#080A0D",        // fond application
  sidebar: "#0B0F14",   // navigation laterale
  card: "#11161D",      // carte
  elevated: "#171D26",  // panneau eleve / ligne active
  border: "#242B35",
  divider: "#1A212B",
  text: "#F5F7FA",
  muted: "#8B95A5",
  accent: "#2563EB",    // action, nav active, lien, selection
  info: "#38BDF8",      // etiquette informative
};

// Rouge critique, orange eleve, jaune moyen, vert sain. Jamais de bleu ici.
export const severity = {
  critical: { fg: "#EF4444", border: "#4A1A1E", bg: "#1A0B0D" },
  high:     { fg: "#F5A524", border: "#4A3A12", bg: "#181207" },
  medium:   { fg: "#FACC15", border: "#4A4212", bg: "#181507" },
  safe:     { fg: "#34D399", border: "#1B4033", bg: "#0B1A14" },
  unknown:  { fg: "#8B95A5", border: "#242B35", bg: "#11161D" },
};

export const font = {
  sans: "'Space Grotesk', system-ui, -apple-system, sans-serif",
  mono: "'IBM Plex Mono', ui-monospace, monospace",
};

// Echelle d'espacement en px, utilisee telle quelle dans les styles inline.
export const space = { xs: 6, sm: 10, md: 16, lg: 24, xl: 34 };

export const layout = {
  sidebarWidth: 240,
  sidebarCollapsed: 62,
  contentMax: 1440,
};
