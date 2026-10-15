import { AuthPage } from './pages/AuthPage'
import { Home } from './pages/Home'
import { useAuth } from './lib/auth-context'

function App() {
  const { user, loading } = useAuth()

  if (loading) return null
  if (!user) return <AuthPage />

  return <Home />
}

export default App