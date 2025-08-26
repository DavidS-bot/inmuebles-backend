import Link from "next/link";
export default function Home() {
  return (
    <main className="p-8">
      <h1 className="text-2xl font-bold mb-4">Inmuebles Web</h1>
      <div className="space-x-4">
        <Link className="underline" href="/login">Login</Link>
        <Link className="underline" href="/dashboard">Dashboard</Link>
      </div>
    </main>
  );
}

