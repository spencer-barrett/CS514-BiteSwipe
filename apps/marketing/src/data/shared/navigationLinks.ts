import type { NavLink } from "@/types/navigationLink";

export const navLinks: NavLink[] = [
  {
    href: "/",
    label: "Home",
    match: (p: string) => p === "/",
  },
  {
    href: "/about",
    label: "About",
    match: (p: string) => p === "/about" || p.startsWith("/about/"),
  },
  {
    href: "/blog",
    label: "Blog",
    match: (p: string) => p === "/blog" || p.startsWith("/blog/"),
  },
];

export const navCta = {
  href: "https://biteswipe-app.pages.dev/",
  label: "Try BiteSwipe",
};