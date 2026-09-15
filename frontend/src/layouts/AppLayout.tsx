import Footer from "@components/Footer";
import Nav from "@components/Nav";
import { Outlet } from "react-router";

export default function AppLayout(): React.ReactNode {
  return (
    <div className="flex min-h-screen flex-col">
      <Nav />
      <main className="flex flex-1 flex-col">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}
