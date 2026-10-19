export type NavDropdownItem = {
    href: string;
    label: string;
    description: string;
    icon?: string;
};

export type NavDropdownFooterLink = {
    href: string;
    label: string;
};

export type NavLink = {
    label: string;
    match: (path: string) => boolean;
} & (
    | { href: string; dropdown?: never }
    | {
          href?: string;
          dropdown: {
              heading: string;
              columns: 1 | 2;
              items: NavDropdownItem[];
              footerLinks?: NavDropdownFooterLink[];
          };
      }
);