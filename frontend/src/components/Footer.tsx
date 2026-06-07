import constants from "@constants";
import { Link } from "react-router-dom";

export default function Footer() {
  return (
    <footer className="border-heading-pink bg-dark-amethyst-950 border-t-4">
      <div className="text-muted flex flex-wrap justify-between gap-10 px-14 py-12 align-bottom">
        <div>
          <p className="m-0 text-sm leading-relaxed">
            PUCKCURL is an independent, fan-organized initiative not affiliated
            with the PWHL, any team, or any player.
          </p>
          <p className="text-heading-pink font-black">
            We choose to answer hate with help.
          </p>
        </div>

        <div className="flex items-end gap-5 text-sm leading-loose">
          <Link to={constants.ROUTES.privacy} className="link">
            Privacy Policy
          </Link>
          <Link to={constants.ROUTES.disclaimer} className="link">
            Disclaimer
          </Link>
        </div>
      </div>
    </footer>
  );
}
