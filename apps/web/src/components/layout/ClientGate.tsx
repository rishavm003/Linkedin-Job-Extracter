"use client";

import { useState, useEffect } from "react";

/**
 * Client-side only wrapper to delay mounting until hydration is complete.
 * Prevents browser extensions from interfering with the initial React render.
 */
export default function ClientGate({ children }: { children: React.ReactNode }) {
  const [hasMounted, setHasMounted] = useState(false);

  useEffect(() => {
    setHasMounted(true);
  }, []);

  if (!hasMounted) {
    // Show a clean background while waiting for hydration
    return (
      <div className="min-h-screen bg-background" aria-hidden="true" />
    );
  }

  return <>{children}</>;
}
