import { Container, H1, H2 } from "@components";
import constants from "@constants";
import { Link } from "react-router-dom";

export default function DisclaimerView(): React.ReactNode {
  return (
    <Container>
      <article className="mx-auto max-w-3xl space-y-10">
        <header className="space-y-2">
          <H1>Disclaimer</H1>
          <p className="text-muted text-sm">
            <strong>Last updated: June 30, 2026</strong>
          </p>
        </header>

        <section className="space-y-3">
          <H2>Independence and non-affiliation</H2>
          <p className="text-muted leading-relaxed">
            PUCKHATE is an independent, fan-organized initiative. It is not
            affiliated with, endorsed by, or sponsored by the Professional
            Women's Hockey League (PWHL), any of its teams, or any of its
            players, including Britta Curl-Salemme. All trademarks, team names,
            league names, and player names belong to their respective owners and
            are used solely for identification and commentary.
          </p>
        </section>

        <section className="space-y-3">
          <H2>How this campaign works</H2>
          <p className="text-muted leading-relaxed">
            Participants choose their own recipient organizations and donate
            directly to them. PUCKHATE does not collect, process, hold, or
            direct any donation funds at any time. We are not a charity, a
            fundraising platform, or a payment processor.
          </p>
          <p className="text-muted leading-relaxed">
            References to any charitable organization by participants do not
            imply that organization's endorsement of, or involvement in, this
            campaign.
          </p>
        </section>

        <section className="space-y-3">
          <H2>Donation totals</H2>
          <p className="text-muted leading-relaxed">
            Published totals reflect donation receipts voluntarily submitted by
            participants and reviewed in good faith by the site's organizers.
            They are not independently audited, and we cannot guarantee that
            every submitted receipt corresponds to a completed donation. Totals
            should be understood as a best-effort tally, not a certified figure.
          </p>
        </section>

        <section className="space-y-3">
          <H2>Statistics</H2>
          <p className="text-muted leading-relaxed">
            Goal and game statistics are compiled from publicly available
            sources. They are unofficial and are not verified by or endorsed by
            the PWHL.
          </p>
        </section>

        <section className="space-y-3">
          <H2>Opinions</H2>
          <p className="text-muted leading-relaxed">
            Commentary on this site reflects the opinions of its organizers,
            based on publicly available statements and reporting. Nothing on
            this site should be construed as a statement of fact about any
            individual beyond what is publicly documented.
          </p>
        </section>

        <section className="space-y-3">
          <H2>Tax matters</H2>
          <p className="text-muted leading-relaxed">
            Because donations are made directly to organizations of each
            participant's choosing, any tax receipts or deductibility questions
            are between the donor and that organization. PUCKHATE provides no
            tax documentation and makes no representations about the
            deductibility of any donation.
          </p>
        </section>

        <section className="space-y-3">
          <H2>No legal or financial advice</H2>
          <p className="text-muted leading-relaxed">
            Nothing on this site constitutes legal, financial, or tax advice.
          </p>
        </section>

        <section className="space-y-3">
          <H2>Contact</H2>
          <p className="text-muted leading-relaxed">
            Questions or concerns, including requests to correct or remove
            content:{" "}
            <a href="mailto:hello@puckhate.com" className="link font-bold">
              hello@puckhate.com
            </a>
          </p>
          <p className="text-muted leading-relaxed">
            For how we handle submitted receipts and personal information, see
            our{" "}
            <Link to={constants.ROUTES.privacy} className="link font-bold">
              Privacy Policy
            </Link>
            .
          </p>
        </section>
      </article>
    </Container>
  );
}
