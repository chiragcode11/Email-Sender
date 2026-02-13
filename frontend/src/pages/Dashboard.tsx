import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { campaignAPI } from '../services/api'
import { useAuthStore } from '../store/authStore'
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import {
    LayoutDashboard,
    Mail,
    BarChart3,
    Send,
    Plus,
    LogOut,
    Eye
} from 'lucide-react'

export default function Dashboard() {
    const navigate = useNavigate()
    const user = useAuthStore((state) => state.user)
    const logout = useAuthStore((state) => state.logout)

    const { data: campaigns = [], isLoading } = useQuery({
        queryKey: ['campaigns'],
        queryFn: campaignAPI.list,
    })

    // Calculate stats
    const totalCampaigns = campaigns.length
    const totalSent = campaigns.reduce((sum: number, c: any) => sum + c.sent_count, 0)
    // Placeholder for open rate logic
    const totalOpens = 0
    const openRate = totalSent > 0 ? ((totalOpens / totalSent) * 100).toFixed(1) : 0
    const activeCampaigns = campaigns.filter((c: any) => c.status === 'sending').length

    const handleLogout = () => {
        logout()
        navigate('/login')
    }

    const getStatusVariant = (status: string) => {
        switch (status) {
            case 'completed': return 'default' // Primary color
            case 'sending': return 'secondary'
            case 'scheduled': return 'outline'
            case 'failed': return 'destructive'
            default: return 'secondary'
        }
    }

    return (
        <div className="min-h-screen bg-background text-foreground">
            {/* Header */}
            <header className="border-b border-border bg-card">
                <div className="container mx-auto px-6 py-4 flex justify-between items-center">
                    <div className="flex items-center gap-2">
                        <Mail className="h-6 w-6 text-primary" />
                        <h1 className="text-xl font-bold">Email Automation</h1>
                    </div>
                    <div className="flex items-center gap-4">
                        <span className="text-sm text-muted-foreground">Welcome, {user?.username}</span>
                        <Button variant="ghost" size="sm" onClick={handleLogout} className="gap-2">
                            <LogOut className="h-4 w-4" />
                            Logout
                        </Button>
                    </div>
                </div>
            </header>

            {/* Navigation */}
            <nav className="border-b border-border bg-background/50 backdrop-blur supports-[backdrop-filter]:bg-background/60">
                <div className="container mx-auto px-6">
                    <div className="flex gap-1">
                        <Button
                            variant="default"
                            className="rounded-none border-b-2 border-primary h-12 px-6"
                        >
                            <LayoutDashboard className="mr-2 h-4 w-4" />
                            Dashboard
                        </Button>
                        <Button
                            variant="ghost"
                            className="rounded-none border-b-2 border-transparent h-12 px-6 hover:bg-muted"
                            onClick={() => navigate('/campaigns')}
                        >
                            <Mail className="mr-2 h-4 w-4" />
                            Campaigns
                        </Button>
                    </div>
                </div>
            </nav>

            <main className="container mx-auto px-6 py-8">
                <div className="flex justify-between items-center mb-8">
                    <div>
                        <h2 className="text-3xl font-bold tracking-tight">Dashboard</h2>
                        <p className="text-muted-foreground mt-1">Overview of your email marketing performance.</p>
                    </div>
                    <Button onClick={() => navigate('/campaigns/create')} className="gap-2">
                        <Plus className="h-4 w-4" /> Create Campaign
                    </Button>
                </div>

                {/* Stats Cards */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                    <Card>
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">Total Campaigns</CardTitle>
                            <BarChart3 className="h-4 w-4 text-muted-foreground" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">{totalCampaigns}</div>
                            <p className="text-xs text-muted-foreground">All time campaigns created</p>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">Emails Sent</CardTitle>
                            <Send className="h-4 w-4 text-muted-foreground" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">{totalSent}</div>
                            <p className="text-xs text-muted-foreground">Total emails delivered</p>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">Open Rate</CardTitle>
                            <Eye className="h-4 w-4 text-muted-foreground" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">{openRate}%</div>
                            <p className="text-xs text-muted-foreground">Average engagement</p>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">Active Now</CardTitle>
                            <div className="h-4 w-4 rounded-full bg-green-500 animate-pulse" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">{activeCampaigns}</div>
                            <p className="text-xs text-muted-foreground">Campaigns currently sending</p>
                        </CardContent>
                    </Card>
                </div>

                {/* Recent Campaigns */}
                <div className="grid gap-4">
                    <h3 className="text-xl font-semibold">Recent Campaigns</h3>
                    {isLoading ? (
                        <div className="flex justify-center p-8">
                            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                        </div>
                    ) : campaigns.length === 0 ? (
                        <Card className="flex flex-col items-center justify-center p-12 text-center">
                            <div className="rounded-full bg-muted p-6 mb-4">
                                <Mail className="h-10 w-10 text-muted-foreground" />
                            </div>
                            <h3 className="text-lg font-semibold mb-2">No campaigns yet</h3>
                            <p className="text-muted-foreground mb-4">Create your first campaign to get started with email automation.</p>
                            <Button onClick={() => navigate('/campaigns/create')}>Create Campaign</Button>
                        </Card>
                    ) : (
                        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                            {campaigns.slice(0, 6).map((campaign: any) => (
                                <Card
                                    key={campaign.id}
                                    className="cursor-pointer hover:border-primary transition-colors"
                                    onClick={() => navigate(`/campaigns/${campaign.id}`)}
                                >
                                    <CardHeader className="flex flex-row items-start justify-between pb-2">
                                        <div className="space-y-1">
                                            <CardTitle className="text-base line-clamp-1">{campaign.name}</CardTitle>
                                            <p className="text-sm text-muted-foreground line-clamp-1">{campaign.subject}</p>
                                        </div>
                                        <Badge variant={getStatusVariant(campaign.status)} className="capitalize">
                                            {campaign.status}
                                        </Badge>
                                    </CardHeader>
                                    <CardContent>
                                        <div className="flex items-center justify-between text-sm">
                                            <div className="flex items-center gap-2 text-muted-foreground">
                                                <Send className="h-3 w-3" />
                                                <span>{campaign.sent_count} sent</span>
                                            </div>
                                            <div className="text-xs text-muted-foreground">
                                                {new Date(campaign.created_at).toLocaleDateString()}
                                            </div>
                                        </div>
                                    </CardContent>
                                </Card>
                            ))}
                        </div>
                    )}
                </div>
            </main>
        </div>
    )
}
