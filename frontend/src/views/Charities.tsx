import { Container } from "@components";

export default function Charities(): React.ReactNode {
  return (
    <Container>
      <article className="mx-auto max-w-3xl space-y-10">
        <header className="space-y-2">
          <h1 className="font-heading text-heading-pink text-4xl font-black tracking-tight uppercase">
            Reccomended Charities List
          </h1>
          <p className="text-sm">
            These organizations are doing the work. Every donation to them is an
            assist. This list is curated by our organizers and community, and is
            by no means exhaustive.
          </p>
        </header>

        <section className="space-y-3">List.</section>
      </article>
    </Container>
  );
}
