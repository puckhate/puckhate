import { Container, H1, H2 } from "@components";

import FAQ from "./components/FAQ";

interface GamePlanItem {
  title: string;
  description: React.ReactNode;
}

const GamePlanItems: GamePlanItem[] = [
  {
    title: "Who are we?",
    description: (
      <>
        PUCKHATE! is a group of PWHL fans who have decided to channel our hurt
        and frustration into positive change. Both trans and cis fans have come
        together to create this initiative and get it off the ground, from
        building the website to collecting a list of charities to setting up
        social media accounts to moderating incoming donations. Fans across the
        queer spectrum and allies alike are coming together in the face of
        transphobia to make a statement: hockey is for everyone.
      </>
    ),
  },
  {
    title: "Why are we doing this?",
    description: (
      <>
        PWHL fans have made their feelings about transphobic and uninclusive
        views in the league clear. Our goal is to provide a positive outlet for
        fans who feel frustrated and hurt by these views. It is our belief that
        choosing to step away from supporting a team she is on only serves to
        remove good people from those spaces. We hope that this donation tracker
        will help bring fans together with a common goal of good.{" "}
        <span className="text-heading-pink font-bold">
          We choose to answer hate with help.
        </span>
      </>
    ),
  },
];

export default function AboutView(): React.ReactNode {
  return (
    <>
      <Container>
        <article className="mx-auto max-w-3xl space-y-10">
          <header className="space-y-2">
            <H1>The Game Plan</H1>
          </header>

          {GamePlanItems.map((item) => (
            <section className="space-y-3" key={item.title}>
              <H2>{item.title}</H2>
              <p className="text-muted leading-relaxed">{item.description}</p>
            </section>
          ))}
        </article>
      </Container>
      <FAQ />
    </>
  );
}
