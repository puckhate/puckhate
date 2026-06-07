import Hero from "./components/Hero";
import LogDonation from "./components/LogDonation.tsx";
import Playbook from "./components/PlaybookCard";

export default function HomeView() {
  return (
    <>
      <Hero raised={999999} donors={7777} goals={10} />
      <Playbook />
      <LogDonation />
    </>
  );
}
