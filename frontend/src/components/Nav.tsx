import constants from "@constants";
import { Link } from "react-router-dom";

const NavLinks = [
  { label: "The Plan", href: constants.ROUTES.plan },
  { label: "Charities", href: constants.ROUTES.charities },
  { label: "Donation List", href: constants.ROUTES.charities },
];

export default function Nav() {
  return (
    <header className="bg-page/80 sticky top-0 z-20 flex items-center justify-between border-b border-white/10 px-14 py-5 backdrop-blur-md">
      <a href={constants.ROUTES.home} className="flex items-center gap-3">
        <span className="font-heading text-body text-2xl font-extrabold tracking-wide">
          PUCKCURL!
        </span>
      </a>

      <nav className="flex items-center gap-4">
        {NavLinks.map((l) => (
          <Link
            key={l.href}
            to={l.href}
            className="font-heading text-body/80 hover:text-heading-pink text-sm font-bold tracking-wide uppercase transition-colors"
          >
            {l.label}
          </Link>
        ))}
      </nav>
    </header>
  );
}
