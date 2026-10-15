import { useState, type FormEvent } from "react";
import { FirebaseError } from "firebase/app";
import { useAuth } from "@/lib/auth-context";
import { Button } from "@/components/ui/button";
import {
  Field,
  FieldDescription,
  FieldGroup,
  FieldLabel,
  FieldLegend,
  FieldSet,
  FieldError,
} from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import foodBg from "@/assets/food-bg-1280.webp";

export function AuthPage() {
  const { signIn, signUp } = useAuth();
  const [mode, setMode] = useState<"signin" | "signup">("signin");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [confirmTouched, setConfirmTouched] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    if (mode === "signup" && password !== confirmPassword) {
      setConfirmTouched(true);
      setError("Passwords do not match.");
      return;
    }
    setBusy(true);
    try {
      if (mode === "signin") await signIn(email, password);
      else await signUp(email, password);
    } catch (err) {
      setError(messageFor(err));
    } finally {
      setBusy(false);
    }
  }

  const mismatch = confirmTouched && confirmPassword !== password;
  const filled =
    email.trim() !== "" &&
    password !== "" &&
    (mode === "signin" || confirmPassword !== "");

  const canSubmit = filled && !busy;

  return (
    <main
      className="relative flex min-h-dvh w-full items-center justify-center overflow-hidden bg-[#2d2e2e] bg-cover bg-center px-4"
      style={{ backgroundImage: `url(${foodBg})` }}
    >
      <div
        aria-hidden
        className="absolute inset-0 bg-black/50 backdrop-blur-[10px]"
      />
      <section className="relative w-full max-w-md rounded-xl border bg-background p-6 shadow-lg">
        <div className="flex items-center justify-center m-4">
          <h1 className="text-5xl font-black tracking-tight text-foreground">
            <span className="text-brand">Bite</span>Swipe
          </h1>
        </div>
        <form onSubmit={handleSubmit}>
          <FieldGroup>
            <FieldSet>
              <FieldLegend>
                {mode === "signin" ? "Sign In" : "Register"}
              </FieldLegend>
              <FieldDescription>
                {mode === "signin"
                  ? "Sign into your account"
                  : "Create a new account"}
              </FieldDescription>
              <FieldGroup>
                <Field>
                  <FieldLabel htmlFor="email-field">Email</FieldLabel>
                  <Input
                    onChange={(e) => setEmail(e.target.value)}
                    id="email-field"
                    placeholder="email"
                    type="email"
                    required
                    autoComplete="email"
                    value={email}
                  />
                </Field>
                <Field>
                  <FieldLabel htmlFor="password-field">Password</FieldLabel>
                  <Input
                    onChange={(e) => setPassword(e.target.value)}
                    id="password-field"
                    placeholder="password"
                    type="password"
                    required
                    autoComplete={
                      mode === "signin" ? "current-password" : "new-password"
                    }
                    value={password}
                  />
                </Field>
                {mode === "signup" && (
                  <Field>
                    <FieldLabel htmlFor="confirm-password-field">
                      Confirm Password
                    </FieldLabel>
                    <Input
                      id="confirm-password-field"
                      type="password"
                      autoComplete="new-password"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      onBlur={() => setConfirmTouched(true)}
                      aria-invalid={mismatch}
                      required
                      placeholder="confirm password"
                    />
                    {/* {mismatch && (
                      <FieldError>Passwords do not match</FieldError>
                    )} */}
                  </Field>
                )}
              </FieldGroup>
            </FieldSet>
            <Button type="submit" disabled={!canSubmit}>
              {busy ? "…" : mode === "signin" ? "Sign in" : "Create account"}
            </Button>
            {error && <FieldError role="alert">{error}</FieldError>}
          </FieldGroup>
        </form>

        <Button
          variant="text"
          onClick={() => {
            setMode(mode === "signin" ? "signup" : "signin");
            setError(null);
            setConfirmPassword("");
            setConfirmTouched(false);
          }}
          type="button"
        >
          {mode === "signin" ? "Need an account?" : "Already have an account?"}
        </Button>
      </section>
    </main>
  );
}

function messageFor(err: unknown): string {
  if (!(err instanceof FirebaseError)) return "Something went wrong.";
  switch (err.code) {
    case "auth/invalid-credential":
      return "Incorrect email or password.";
    case "auth/email-already-in-use":
      return "That email is already registered.";
    case "auth/weak-password":
      return "Password must be at least 6 characters.";
    case "auth/invalid-email":
      return "Enter a valid email address.";
    default:
      return "Something went wrong. Try again.";
  }
}
