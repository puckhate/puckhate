import { Container } from "@components";

export default function Privacy(): React.ReactNode {
  return (
    <Container>
      <article className="mx-auto max-w-3xl space-y-10">
        <header className="space-y-2">
          <h1 className="font-heading text-heading-pink text-4xl font-black tracking-tight uppercase">
            Privacy Policy
          </h1>
          <p className="text-muted text-sm">
            <strong>Last updated: June 30, 2026</strong>
          </p>
        </header>

        <p className="text-muted leading-relaxed">
          PUCKHATE ("we," "us," or "the site") is an independent, fan-organized
          initiative. This policy explains what information we collect, why we
          collect it, and how we handle it. We've tried to keep it short and in
          plain language.
        </p>

        <section className="space-y-3">
          <h2 className="font-heading text-heading-blue text-xl font-bold">
            What we collect
          </h2>
          <p className="text-muted leading-relaxed">
            <strong>Donation receipts.</strong> If you choose to submit a
            donation receipt through the upload feature on this site, we receive
            whatever information appears on that receipt. Depending on what you
            upload, this may include your name, email address, mailing address,
            the recipient organization, the donation amount, and the donation
            date.
          </p>
          <p className="text-muted leading-relaxed">
            <strong>You may redact personal details before uploading.</strong>{" "}
            We only need to see the recipient organization, the date, and the
            amount. We encourage you to black out or crop your name, email,
            address, and any payment details before submitting.
          </p>
          <p className="text-muted leading-relaxed">
            <strong>Contact information.</strong> If you email us or use a
            contact form, we receive your email address and the contents of your
            message.
          </p>
          <p className="text-muted leading-relaxed">
            <strong>Technical information.</strong> We do not use analytics
            tools or advertising trackers. Our hosting provider may
            automatically log basic technical data, such as IP addresses, as
            part of operating the service.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="font-heading text-heading-blue text-xl font-bold">
            Why we collect it
          </h2>
          <p className="text-muted leading-relaxed">
            We collect donation receipts for one purpose: to verify, in good
            faith, that reported donations occurred, so that the totals
            published on this site are as accurate as possible. We use contact
            information to respond to you.
          </p>
          <p className="text-muted leading-relaxed">
            We do not use your information for advertising, and we never sell
            it.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="font-heading text-heading-blue text-xl font-bold">
            A note on sensitivity
          </h2>
          <p className="text-muted leading-relaxed">
            We recognize that your choice of recipient organization may reveal
            information about your beliefs or identity. We treat all submitted
            receipts as confidential, regardless of content.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="font-heading text-heading-blue text-xl font-bold">
            How long we keep it
          </h2>
          <p className="text-muted leading-relaxed">
            Submitted receipts are retained for up to <strong>one year</strong>{" "}
            from the date of submission, after which they are permanently
            deleted. We retain logged donation data (such as amount, date,
            organization, name, and email) indefinitely.
          </p>
          <p className="text-muted leading-relaxed">
            Emails and correspondence are kept only as long as needed to handle
            your inquiry.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="font-heading text-heading-blue text-xl font-bold">
            Who can access it
          </h2>
          <p className="text-muted leading-relaxed">
            Submitted receipts are accessible only to the site's organizers. Our
            hosting and infrastructure providers process data on our behalf as
            part of operating the site. We do not share your information with
            anyone else, except if required by law.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="font-heading text-heading-blue text-xl font-bold">
            Your choices and rights
          </h2>
          <ul className="text-muted list-disc space-y-2 pl-5 leading-relaxed">
            <li>
              <strong>Submission is voluntary.</strong> You can participate in
              donating without submitting data to this website.
            </li>
            <li>
              <strong>Deletion.</strong> You may request deletion of any receipt
              or personal information you've submitted at any time by contacting
              us at{" "}
              <a href="mailto:privacy@puckhate.com" className="link font-bold">
                privacy@puckhate.com
              </a>
              . We will delete it promptly, though the anonymized amount may
              remain in published totals.
            </li>
            <li>
              <strong>Access and correction.</strong> You may ask us what
              information we hold about you and request corrections.
            </li>
          </ul>
          <p className="text-muted leading-relaxed">
            Depending on where you live (for example, the EU/UK, California, or
            Canada), you may have additional rights under local privacy law. We
            will honor reasonable requests consistent with those laws.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="font-heading text-heading-blue text-xl font-bold">
            Security
          </h2>
          <p className="text-muted leading-relaxed">
            We take reasonable measures to protect submitted information, but no
            website can guarantee perfect security. This is another reason we
            encourage redacting personal details before uploading.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="font-heading text-heading-blue text-xl font-bold">
            Children
          </h2>
          <p className="text-muted leading-relaxed">
            This site is not directed at children under 13, and we do not
            knowingly collect their information. If you believe a child has
            submitted personal information, contact us and we will delete it.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="font-heading text-heading-blue text-xl font-bold">
            Changes to this policy
          </h2>
          <p className="text-muted leading-relaxed">
            If we change this policy, we will update the date above and note
            material changes on this page.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="font-heading text-heading-blue text-xl font-bold">
            Contact
          </h2>
          <p className="text-muted leading-relaxed">
            Questions, deletion requests, or concerns:{" "}
            <a href="mailto:hello@puckhate.com" className="link font-bold">
              hello@puckhate.com
            </a>
          </p>
        </section>
      </article>
    </Container>
  );
}
