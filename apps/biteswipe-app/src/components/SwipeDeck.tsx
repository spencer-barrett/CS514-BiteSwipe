import { useCallback, useEffect, useRef, useState } from "react";

import { RestaurantCard } from "./RestaurantCard";
import { Button } from "@/components/ui/button";
import { apiFetch } from "@/lib/api";
import type { Restaurant } from "../lib/types";

const DECK_SIZE = 10;
const REFILL_AT = 3;

export function SwipeDeck() {
  const [deck, setDeck] = useState<Restaurant[]>([]);
  const [loading, setLoading] = useState(true);
  const [exhausted, setExhausted] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const seen = useRef<Set<number>>(new Set());
  const refilling = useRef(false);

  const deckRef = useRef<Restaurant[]>([]);
  const setDeckBoth = useCallback((next: Restaurant[]) => {
    deckRef.current = next;
    setDeck(next);
  }, []);

  const loadMore = useCallback(async () => {
    if (refilling.current) return;
    refilling.current = true;
    try {
      const res = await apiFetch(`/api/feed?limit=${DECK_SIZE}`);
      if (!res.ok) throw new Error(`feed failed: ${res.status}`);
      const batch: Restaurant[] = await res.json();

      const inDeck = new Set(deckRef.current.map((r) => r.id));
      const fresh = batch.filter(
        (r) => !seen.current.has(r.id) && !inDeck.has(r.id),
      );

      setDeckBoth([...deckRef.current, ...fresh]);

      if (batch.length === 0) setExhausted(true);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Could not load restaurants",
      );
    } finally {
      refilling.current = false;
      setLoading(false);
    }
  }, [setDeckBoth]);

  useEffect(() => {
    void loadMore();
  }, [loadMore]);

  const swipe = useCallback(
    (liked: boolean) => {
      const [card, ...rest] = deckRef.current;
      if (!card) return;

      seen.current.add(card.id);

      setDeckBoth(rest.filter((r) => r.id !== card.id));

      void apiFetch("/api/swipes", {
        method: "POST",
        body: JSON.stringify({ restaurant_id: card.id, liked }),
      })
        .then((res) => {
          if (!res.ok) throw new Error(`swipe failed: ${res.status}`);
        })
        .catch(() => setError("A swipe didn't save"));
    },
    [setDeckBoth],
  );

  // Refill
  useEffect(() => {
    if (!loading && !exhausted && deck.length <= REFILL_AT) void loadMore();
  }, [deck.length, loading, exhausted, loadMore]);

  useEffect(() => {
    function onKey(event: KeyboardEvent) {
      if (event.key === "ArrowLeft") swipe(false);
      if (event.key === "ArrowRight") swipe(true);
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [swipe]);

  if (loading) {
    return (
      <div className="mx-auto w-full max-w-sm">
        <div className="aspect-3/4 w-full animate-pulse rounded-2xl bg-muted" />
      </div>
    );
  }

  const current = deck[0];
  const next = deck[1];

  if (!current) {
    return (
      <div className="mx-auto flex w-full max-w-sm flex-col items-center gap-3 py-16 text-center">
        <p className="text-xl font-semibold">That's everywhere</p>
        <p className="text-muted-foreground text-sm">
          You've swiped through every restaurant we have.
        </p>
      </div>
    );
  }

  return (
    <div className="mx-auto w-full max-w-sm">
      <div className="relative">
        {next && (
          <div className="absolute inset-0 scale-95 opacity-40" aria-hidden>
            <RestaurantCard restaurant={next} />
          </div>
        )}
        <div className="relative">
          <RestaurantCard restaurant={current} />
        </div>
      </div>

      <div className="mt-6 flex justify-center gap-4">
        <Button
          variant="outline"
          size="lg"
          className="min-w-32"
          onClick={() => swipe(false)}
          aria-label={`Pass on ${current.name}`}
        >
          I'll Pass
        </Button>
        <Button
          size="lg"
          className="min-w-32 bg-brand text-brand-foreground hover:bg-brand/90"
          onClick={() => swipe(true)}
          aria-label={`Save ${current.name}`}
        >
          Like
        </Button>
      </div>

      <p className="text-muted-foreground mt-3 text-center text-xs">
        Use ← and → to swipe
      </p>

      {error && (
        <p
          role="status"
          className="text-muted-foreground mt-2 text-center text-xs"
        >
          {error}
        </p>
      )}
    </div>
  );
}
