import constants from "@constants";
import {
  Disclosure,
  DisclosureButton,
  DisclosurePanel,
} from "@headlessui/react";
import { Bars3Icon, XMarkIcon } from "@heroicons/react/24/outline";
import { Link } from "react-router-dom";

const NavLinks = [
  { label: "Game Plan", href: constants.ROUTES.about },
  { label: "Charities", href: constants.ROUTES.charities },
  { label: "Donation List", href: constants.ROUTES.donations },
];

const linkClasses =
  "font-heading text-body/80 hover:text-heading-pink text-sm font-bold tracking-wide uppercase transition-colors";

export default function Nav() {
  return (
    <Disclosure
      as="header"
      className="bg-page/80 sticky top-0 z-20 border-b border-white/10 backdrop-blur-md"
    >
      {({ open, close }) => (
        <>
          <div className="flex items-center justify-between px-6 py-5 lg:px-14">
            <Link
              to={constants.ROUTES.home}
              className="flex items-center gap-3"
            >
              <span className="font-heading text-body text-2xl font-extrabold tracking-wide">
                PUCKHATE!
              </span>
            </Link>

            <nav className="hidden items-center gap-4 md:flex">
              {NavLinks.map((l) => (
                <Link key={l.label} to={l.href} className={linkClasses}>
                  {l.label}
                </Link>
              ))}
            </nav>

            <DisclosureButton
              className="text-body hover:text-heading-pink transition-colors md:hidden"
              aria-label="Toggle navigation menu"
            >
              {open ? (
                <XMarkIcon className="size-7" aria-hidden />
              ) : (
                <Bars3Icon className="size-7" aria-hidden />
              )}
            </DisclosureButton>
          </div>

          <DisclosurePanel className="border-t border-white/10 px-6 pt-2 pb-4 md:hidden">
            <nav className="flex flex-col gap-4">
              {NavLinks.map((link) => (
                <Link
                  key={link.label}
                  to={link.href}
                  onClick={() => close()}
                  className={linkClasses}
                >
                  {link.label}
                </Link>
              ))}
            </nav>
          </DisclosurePanel>
        </>
      )}
    </Disclosure>
  );
}
