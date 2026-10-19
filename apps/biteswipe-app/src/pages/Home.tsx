import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/lib/auth-context";
import { apiFetch } from "@/lib/api";
import { SwipeDeck } from "@/components/SwipeDeck";

export function Home() {
  const { user, logOut } = useAuth();
  const [busy, setBusy] = useState(false);

  // const [profile, setProfile] = useState<{ id: number; email: string } | null>(
  //   null,
  // );

  useEffect(() => {
    apiFetch("/api/me")
      .then((r) => (r.ok ? r.json() : Promise.reject(r.status)))
      .catch((err) => console.error("profile fetch failed", err));
  }, []);

  async function handleSignOut() {
    setBusy(true);
    try {
      await logOut();
    } catch (err) {
      console.error("Sign out failed", err);
      setBusy(false);
    }
  }

  return (
    <main>
      <p>Signed in as {user?.email}</p>
      <Button onClick={handleSignOut} disabled={busy}>
        {busy ? "Signing out…" : "Log out"}
      </Button>
      <SwipeDeck/>
    </main>
  );
}
