import { Container } from "@components";

export default function Plan(): React.ReactNode {
  return (
    <Container>
      <article className="mx-auto max-w-3xl space-y-10">
        <header className="space-y-2">
          <h1 className="font-heading text-heading-pink text-4xl font-black tracking-tight uppercase">
            The Plan
          </h1>
          <p className="text-sm">Here's why we're doing this.</p>
        </header>
      </article>
    </Container>
  );
}
