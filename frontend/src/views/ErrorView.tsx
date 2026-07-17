import { Container, H1 } from "@components";
import constants from "@constants";
import { Link } from "react-router-dom";

export default function ErrorView(): React.ReactNode {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center">
      <Container>
        <article className="mx-auto max-w-3xl space-y-6 text-center">
          <p className="font-heading text-heading-blue text-7xl font-black">
            Error
          </p>
          <H1>Something went wrong.</H1>
          <p className="text-muted leading-relaxed">
            An internal error ocurred that we can't recover from.
          </p>
          <Link to={constants.ROUTES.home} className="link font-bold">
            Go back home
          </Link>
        </article>
      </Container>
    </div>
  );
}
