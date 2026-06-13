import RaisedCard from "./components/RaisedCard";

export interface HeroProps {
  raised?: number;
  donations?: number;
  goals?: number;
  loading?: boolean;
}

export default function Hero(props: HeroProps) {
  const { raised, donations, goals, loading } = props;
  return (
    <section className="flex flex-col items-center justify-center md:gap-8 lg:flex-row lg:justify-between">
      <div className="w-full lg:w-1/2">
        <div className="font-heading text-heading-blue mb-5 text-sm font-extrabold tracking-widest uppercase">
          She scores. We Fight Back.
        </div>

        <h1 className="font-heading text-body m-0 text-5xl leading-10 font-black tracking-tight uppercase md:text-7xl md:leading-15">
          Every Goal
          <br />
          Has a <span className="text-heading-pink">Price.</span>
        </h1>

        <p className="text-muted my-8 text-lg leading-relaxed">
          Every goal #77 Britta Curl-Salemme scores becomes a donation to
          support the trans community she decries.
        </p>
      </div>

      <RaisedCard
        raised={raised}
        donations={donations}
        goals={goals}
        loading={loading}
      />
    </section>
  );
}
