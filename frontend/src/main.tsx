// oxlint-disable react/only-export-components -- entrypoint: rutas lazy como constantes
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { StrictMode, Suspense, lazy } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import './index.css'
import { AppLayout } from './components/AppLayout'

const Dashboard = lazy(() => import('./pages/Dashboard').then((m) => ({ default: m.Dashboard })))
const Analyze = lazy(() => import('./pages/Analyze').then((m) => ({ default: m.Analyze })))
const Applications = lazy(() =>
  import('./pages/Applications').then((m) => ({ default: m.Applications })),
)
const Profile = lazy(() => import('./pages/Profile').then((m) => ({ default: m.Profile })))
const NotFound = lazy(() => import('./pages/NotFound').then((m) => ({ default: m.NotFound })))

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 15_000,
    },
  },
})

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Suspense
          fallback={
            <div className="flex min-h-screen items-center justify-center bg-slate-100 text-sm text-slate-400">
              Cargando…
            </div>
          }
        >
          <Routes>
            <Route element={<AppLayout />}>
              <Route index element={<Dashboard />} />
              <Route path="analizar" element={<Analyze />} />
              <Route path="postulaciones" element={<Applications />} />
              <Route path="perfil" element={<Profile />} />
            </Route>
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Suspense>
      </BrowserRouter>
    </QueryClientProvider>
  </StrictMode>,
)
