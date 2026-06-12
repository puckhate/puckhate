import { Container } from "@components";
import {
  Disclosure,
  DisclosureButton,
  DisclosurePanel,
} from "@headlessui/react";
import { ChevronDownIcon } from "@heroicons/react/24/outline";

interface FAQItem {
  question: string;
  answer: React.ReactNode;
}

const FAQItems: FAQItem[] = [
  {
    question: "Is this the best approach?",
    answer:
      "We don't know, but to this group of fans, it feels better than resignation. Since Britta Curl-Salemme was drafted to the PWHL, fans have been vocal about their outrage. Emails and letters have been sent, phone calls have been made, tickets have been cancelled, and games have been boycotted. Fans have booed whenever Curl touches the puck; booed even more when she scores. It is likely that many other players in the league share Curl's views and have simply kept quiet about it. Curl's move to Detroit reminded everyone that any team in the league would sign her given the chance-- she plays good hockey. For us, it provided the push needed to find another way of making our voices heard. Regardless of the impact on the league, at least this method of protest puts money into the organizations that fight for inclusion on a daily basis, and we think that matters.",
  },
  {
    question: "Why does it matter?",
    answer:
      "It is important to let the league know how we feel by making our voices heard. However, it's just as important to support the organizations and foundations that are working to make the world a better and more inclusive place. The charities we recommend are actively doing the work to facilitate change and create supportive environments for LGBTQ+ and BIPOC individuals, particularly in the Detroit area but also on a national scale. When you choose to donate in protest, you become an active playmaker as a part of that change!",
  },
  {
    question: "How does it work?",
    answer:
      "For every goal Curl scores, fans mobilize to donate to a charity of their choice and we record the progress here. We don't want anyone to feel constrained by these parameters. You are welcome to donate for any reason at all, and in any amount that feels right for you. You can donate for every penalty she serves, or for every point she gets, or every game she plays in. You can donate repeatedly or just once. We will happily catalogue every donation made in protest of her views.",
  },
];

export default function FAQ() {
  return (
    <Container>
      <article className="mx-auto -my-10 max-w-3xl space-y-10">
        <header className="space-y-2">
          <h1 className="font-heading text-heading-pink text-4xl font-black tracking-tight uppercase">
            FAQ
          </h1>
        </header>
        <section>
          {FAQItems.map((faq) => (
            <Disclosure
              as="div"
              key={faq.question}
              className="border-b-border-dark mb-3 border-b pb-3"
            >
              <DisclosureButton className="group justify-items-between flex w-full items-center justify-between gap-2">
                <h2 className="text-heading-blue block text-left text-xl font-bold">
                  {faq.question}
                </h2>
                <ChevronDownIcon className="block size-5 group-data-open:rotate-180" />
              </DisclosureButton>
              <DisclosurePanel
                transition
                className="text-muted mt-4 origin-top transition duration-200 ease-out data-closed:-translate-y-6 data-closed:opacity-0"
              >
                {faq.answer}
              </DisclosurePanel>
            </Disclosure>
          ))}
        </section>
      </article>
    </Container>
  );
}
