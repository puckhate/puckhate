import { Container } from "@components";
import type { Charity } from "@types";

import CharityPickerModal from "./components/CharityPickerModal";

interface PlaybookCardProps {
  charities: Charity[];
}

interface Step {
  number: string;
  title: string;
  desc: React.ReactNode;
}

export default function PlaybookCard({ charities }: PlaybookCardProps) {
  const Steps: Step[] = [
    {
      number: "1",
      title: "She scores. You pick.",
      desc: (
        <>
          Curl lights the lamp, you pick a trans-supporting charity.
          <br />
          <br />
          <CharityPickerModal charities={charities} />
        </>
      ),
    },
    {
      number: "2",
      title: "Donate. Keep the receipt.",
      desc: "Give what you can (even a single dollar) straight to the charity, then save the confirmation email or PDF.",
    },
    {
      number: "3",
      title: "Upload it. Make it count.",
      desc: "Drop your receipt below and watch the protest total climb throughout the season.",
    },
  ];

  return (
    <section className="bg-dark-amethyst-950/70 py-12">
      <Container>
        <h1 className="font-heading text-body text-center text-4xl font-black uppercase">
          The Playbook
        </h1>

        <div className="mx-auto mt-8 grid grid-cols-1 gap-5 md:grid-cols-3">
          {Steps.map((step) => (
            <div
              key={step.number}
              className="bg-page border-border-dark rounded-2xl border px-7 py-9 text-center"
            >
              <div className="bg-heading-blue font-heading text-page mx-auto mb-5 flex size-15 items-center justify-center rounded-full text-3xl font-black">
                {step.number}
              </div>
              <div className="font-heading text-body mb-2.5 text-lg font-extrabold">
                {step.title}
              </div>
              <p className="text-muted">{step.desc}</p>
            </div>
          ))}
        </div>
      </Container>
    </section>
  );
}
