import { Container, H1 } from "@components";
import constants from "@constants";
import { Link } from "react-router-dom";

export default function NotFoundView(): React.ReactNode {
  return (
    <Container>
      <article className="mx-auto max-w-3xl space-y-6 text-center">
        <p className="font-heading text-heading-blue text-7xl font-black">
          404
        </p>
        <H1>Page not found</H1>
        <p className="text-muted leading-relaxed">
          The page you're looking for doesn't exist or has moved.
        </p>
        <Link to={constants.ROUTES.home} className="link font-bold">
          Go Back Home
        </Link>
      </article>
    </Container>
  );
}
