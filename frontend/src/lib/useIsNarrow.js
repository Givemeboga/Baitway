import { useEffect, useState } from "react";

// Desktop d'abord : BaitWay est une console d'analyste. Ces bornes ne servent
// qu'a degrader proprement, pas a concevoir pour mobile.
export function useViewport() {
  const [width, setWidth] = useState(() => window.innerWidth);
  useEffect(() => {
    const onResize = () => setWidth(window.innerWidth);
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, []);
  return { width, isTablet: width < 1180, isMobile: width < 760 };
}
