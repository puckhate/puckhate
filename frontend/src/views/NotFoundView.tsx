import { Link } from "react-router-dom";

export default function NotFoundView() {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-gray-900">Page not found</h1>
      <Link to="/" className="text-blue-600 underline">
        Go home
      </Link>
    </div>
  );
}
