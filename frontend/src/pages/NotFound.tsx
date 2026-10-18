import { Link } from 'react-router-dom'

export function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-slate-100 text-center">
      <p className="text-5xl font-bold text-slate-300">404</p>
      <p className="mt-2 text-sm text-slate-500">Esta página no existe.</p>
      <Link
        to="/"
        className="mt-4 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-indigo-500"
      >
        Volver al panel
      </Link>
    </div>
  )
}
