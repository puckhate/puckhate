import { Container } from "@components";

import FAQ from "./components/FAQ";

interface GamePlanItem {
  title: string;
  description: React.ReactNode;
}

const GamePlanItems: GamePlanItem[] = [
  {
    title: "Who are we?",
    description:
      "We are a group of PWHL fans who have decided to channel our anger and frustration into positive change. Both trans and cis fans have come together to create this initiative and get it off the ground, from building the website to collecting a list of charities to setting up social media accounts to moderating incoming donations. Fans across the queer spectrum and allies alike are coming together in the face of transphobia to make a statement: hockey is for everyone.",
  },
  {
    title: "Why are we doing this?",
    description:
      "PUCKHATE! is a fan-organized initiative designed to turn a negative into a positive. Since Britta Curl-Salemme has joined the PWHL, fans have made their feelings about her publicly stated views clear. Our goal is to provide a positive outlet for fans who feel frustrated and hurt by Curl's views. It is our belief that choosing to step away from supporting a team she is on only serves to remove good people from those spaces. We hope that this donation tracker will help bring fans together with a common goal of good.",
  },
];

export default function AboutView(): React.ReactNode {
  return (
    <>
      <Container>
        <article className="mx-auto max-w-3xl space-y-10">
          <header className="space-y-2">
            <h1 className="font-heading text-heading-pink text-4xl font-black tracking-tight uppercase">
              The Game Plan
            </h1>
          </header>

          {GamePlanItems.map((item) => (
            <section className="space-y-3" key={item.title}>
              <h2 className="font-heading text-heading-blue text-xl font-bold">
                {item.title}
              </h2>
              <p className="text-muted leading-relaxed">{item.description}</p>
            </section>
          ))}
        </article>
      </Container>
      <FAQ />
    </>
  );
}
