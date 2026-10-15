import { useState } from "react";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/lib/auth-context";

export function Home() {
  const { user, logOut } = useAuth();
  const [busy, setBusy] = useState(false);

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
    </main>
  );
}