import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import { useAuthStore } from './store/authStore'

// Pages
import Dashboard from './pages/Dashboard'
import Login from './pages/Login'
import Campaigns from './pages/Campaigns'
import CreateCampaign from './pages/CreateCampaign'
import CampaignDetails from './pages/CampaignDetails'

const queryClient = new QueryClient()

function ProtectedRoute({ children }: { children: React.ReactNode }) {
    const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
    return isAuthenticated ? <>{children}</> : <Navigate to="/login" />
}

function App() {
    return (
        <QueryClientProvider client={queryClient}>
            <Router>
                <Routes>
                    <Route path="/login" element={<Login />} />
                    <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
                    <Route path="/campaigns" element={<ProtectedRoute><Campaigns /></ProtectedRoute>} />
                    <Route path="/campaigns/create" element={<ProtectedRoute><CreateCampaign /></ProtectedRoute>} />
                    <Route path="/campaigns/:id/edit" element={<ProtectedRoute><CreateCampaign /></ProtectedRoute>} />
                    <Route path="/campaigns/:id" element={<ProtectedRoute><CampaignDetails /></ProtectedRoute>} />
                </Routes>
            </Router>
            <Toaster position="top-right" />
        </QueryClientProvider>
    )
}

export default App
