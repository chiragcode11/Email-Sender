import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useParams, useNavigate } from 'react-router-dom'
import { campaignAPI } from '../services/api'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { Loader2, ArrowLeft, Send, Trash2, ExternalLink, MousePointerClick, Ban } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
    AlertDialogTrigger,
} from "@/components/ui/alert-dialog"
import toast from 'react-hot-toast'

export default function CampaignDetails() {
    const { id } = useParams()
    const navigate = useNavigate()
    const queryClient = useQueryClient()

    const { data: campaign, isLoading } = useQuery({
        queryKey: ['campaign', id],
        queryFn: () => campaignAPI.get(Number(id)),
    })

    const { data: stats } = useQuery({
        queryKey: ['campaign-stats', id],
        queryFn: () => campaignAPI.getStats(Number(id)),
        enabled: !!campaign,
    })

    const deleteMutation = useMutation({
        mutationFn: campaignAPI.delete,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['campaigns'] })
            toast.success('Campaign deleted successfully')
            navigate('/campaigns')
        },
        onError: (error) => {
            console.error('Delete failed:', error)
            toast.error('Failed to delete campaign')
        }
    })

    const sendMutation = useMutation({
        mutationFn: campaignAPI.send,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['campaign', id] })
            toast.success('Campaign sending started!')
        },
        onError: (error) => {
            console.error('Failed to send campaign:', error)
            toast.error('Failed to start sending campaign')
        }
    })

    const cancelMutation = useMutation({
        mutationFn: campaignAPI.cancel,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['campaign', id] })
            toast.success('Campaign cancelled')
        },
        onError: (error) => {
            console.error('Failed to cancel campaign:', error)
            toast.error('Failed to cancel campaign')
        }
    })

    const retryMutation = useMutation({
        mutationFn: campaignAPI.retry,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['campaign', id] })
            toast.success('Campaign retry started')
        },
        onError: (error) => {
            console.error('Failed to retry campaign:', error)
            toast.error('Failed to retry campaign')
        }
    })

    const handleDelete = () => {
        if (id) deleteMutation.mutate(Number(id))
    }

    const handleSendCampaign = () => {
        if (id) sendMutation.mutate(Number(id))
    }

    if (isLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
        )
    }

    if (!campaign) {
        return (
            <div className="min-h-screen flex flex-col items-center justify-center gap-4">
                <h2 className="text-2xl font-bold">Campaign not found</h2>
                <Button onClick={() => navigate('/campaigns')}>
                    Back to Campaigns
                </Button>
            </div>
        )
    }

    const chartData = [
        { name: 'Sent', value: stats?.total_sent || 0 },
        { name: 'Opens', value: stats?.total_opens || 0 },
        { name: 'Clicks', value: stats?.total_clicks || 0 },
        { name: 'Bounces', value: stats?.total_bounces || 0 },
    ]

    const getStatusVariant = (status: string) => {
        switch (status) {
            case 'completed': return 'default'
            case 'sending': return 'secondary'
            case 'scheduled': return 'outline'
            case 'failed': return 'destructive'
            case 'cancelled': return 'destructive'
            default: return 'secondary'
        }
    }

    return (
        <div className="min-h-screen bg-background text-foreground pb-12">
            <div className="container mx-auto px-4 py-8">
                {/* Header */}
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
                    <div>
                        <Button variant="ghost" className="mb-2 pl-0 hover:pl-0 hover:bg-transparent" onClick={() => navigate('/campaigns')}>
                            <ArrowLeft className="mr-2 h-4 w-4" /> Back to Campaigns
                        </Button>
                        <div className="flex items-center gap-3">
                            <h1 className="text-3xl font-bold tracking-tight">{campaign.name}</h1>
                            <Badge variant={getStatusVariant(campaign.status)} className="capitalize">
                                {campaign.status}
                            </Badge>
                        </div>
                        <p className="text-muted-foreground mt-1">{campaign.subject}</p>
                    </div>

                    <div className="flex items-center gap-2">
                        {['draft', 'scheduled', 'cancelled', 'completed', 'failed'].includes(campaign.status) && (
                            <AlertDialog>
                                <AlertDialogTrigger asChild>
                                    <Button variant="destructive" size="sm">
                                        <Trash2 className="mr-2 h-4 w-4" /> Delete Campaign
                                    </Button>
                                </AlertDialogTrigger>
                                <AlertDialogContent>
                                    <AlertDialogHeader>
                                        <AlertDialogTitle>Delete Campaign?</AlertDialogTitle>
                                        <AlertDialogDescription>
                                            This action cannot be undone. This will permanently delete the campaign
                                            "{campaign.name}" and all associated data including recipients and logs.
                                        </AlertDialogDescription>
                                    </AlertDialogHeader>
                                    <AlertDialogFooter>
                                        <AlertDialogCancel>Cancel</AlertDialogCancel>
                                        <AlertDialogAction onClick={handleDelete} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">
                                            Delete
                                        </AlertDialogAction>
                                    </AlertDialogFooter>
                                </AlertDialogContent>
                            </AlertDialog>
                        )}

                        {(campaign.status === 'draft' || campaign.status === 'scheduled') && (
                            <>
                                <Button variant="outline" size="sm" onClick={() => navigate(`/campaigns/${campaign.id}/edit`)}>
                                    Edit Campaign
                                </Button>
                                <AlertDialog>
                                    <AlertDialogTrigger asChild>
                                        <Button>
                                            <Send className="mr-2 h-4 w-4" /> Send Campaign
                                        </Button>
                                    </AlertDialogTrigger>
                                    <AlertDialogContent>
                                        <AlertDialogHeader>
                                            <AlertDialogTitle>Start Sending Campaign?</AlertDialogTitle>
                                            <AlertDialogDescription>
                                                Are you sure you want to send this campaign to {campaign.total_recipients} recipients?
                                                Sending will start immediately.
                                            </AlertDialogDescription>
                                        </AlertDialogHeader>
                                        <AlertDialogFooter>
                                            <AlertDialogCancel>Cancel</AlertDialogCancel>
                                            <AlertDialogAction onClick={handleSendCampaign}>
                                                Start Sending
                                            </AlertDialogAction>
                                        </AlertDialogFooter>
                                    </AlertDialogContent>
                                </AlertDialog>
                            </>
                        )}

                        {(campaign.status === 'sending' || campaign.status === 'scheduled') && (
                            <AlertDialog>
                                <AlertDialogTrigger asChild>
                                    <Button variant="destructive">
                                        <Ban className="mr-2 h-4 w-4" /> Cancel Campaign
                                    </Button>
                                </AlertDialogTrigger>
                                <AlertDialogContent>
                                    <AlertDialogHeader>
                                        <AlertDialogTitle>Cancel Campaign?</AlertDialogTitle>
                                        <AlertDialogDescription>
                                            Are you sure you want to cancel this campaign? Sending will be stopped.
                                            Emails that have already been sent cannot be recalled.
                                        </AlertDialogDescription>
                                    </AlertDialogHeader>
                                    <AlertDialogFooter>
                                        <AlertDialogCancel>Keep Sending</AlertDialogCancel>
                                        <AlertDialogAction onClick={() => cancelMutation.mutate(Number(id))} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">
                                            Yes, Cancel
                                        </AlertDialogAction>
                                    </AlertDialogFooter>
                                </AlertDialogContent>
                            </AlertDialog>
                        )}

                        {(campaign.status === 'failed' || campaign.status === 'cancelled' || (campaign.status === 'completed' && campaign.failed_count > 0)) && (
                            <AlertDialog>
                                <AlertDialogTrigger asChild>
                                    <Button variant="default">
                                        <Send className="mr-2 h-4 w-4" /> Retry Campaign
                                    </Button>
                                </AlertDialogTrigger>
                                <AlertDialogContent>
                                    <AlertDialogHeader>
                                        <AlertDialogTitle>Retry Campaign?</AlertDialogTitle>
                                        <AlertDialogDescription>
                                            This will resume sending to recipients who haven't received the email yet.
                                            Already sent emails will not be duplicated.
                                        </AlertDialogDescription>
                                    </AlertDialogHeader>
                                    <AlertDialogFooter>
                                        <AlertDialogCancel>Cancel</AlertDialogCancel>
                                        <AlertDialogAction onClick={() => retryMutation.mutate(Number(id))}>
                                            Start Retrying
                                        </AlertDialogAction>
                                    </AlertDialogFooter>
                                </AlertDialogContent>
                            </AlertDialog>
                        )}

                        {campaign.status === 'sending' && (
                            <Button disabled variant="outline">
                                <Loader2 className="mr-2 h-4 w-4 animate-spin" /> Sending...
                            </Button>
                        )}
                    </div>
                </div>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Total Sent</CardTitle>
                        <Send className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{stats?.total_sent || 0}</div>
                        <p className="text-xs text-muted-foreground">
                            {campaign.sent_count} / {campaign.total_recipients} processed
                        </p>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Open Rate</CardTitle>
                        <ExternalLink className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-blue-600">{stats?.open_rate || 0}%</div>
                        <p className="text-xs text-muted-foreground">
                            {stats?.total_opens || 0} total opens
                        </p>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Click Rate</CardTitle>
                        <MousePointerClick className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-green-600">{stats?.click_rate || 0}%</div>
                        <p className="text-xs text-muted-foreground">
                            {stats?.total_clicks || 0} total clicks
                        </p>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Bounce Rate</CardTitle>
                        <Ban className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-red-600">{stats?.bounce_rate || 0}%</div>
                        <p className="text-xs text-muted-foreground">
                            {stats?.total_bounces || 0} bounced
                        </p>
                    </CardContent>
                </Card>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Main Chart */}
                <div className="lg:col-span-2">
                    <Card className="h-full">
                        <CardHeader>
                            <CardTitle>Performance Overview</CardTitle>
                            <CardDescription>Key metrics for this campaign.</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <ResponsiveContainer width="100%" height={350}>
                                <BarChart data={chartData}>
                                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                                    <XAxis dataKey="name" fontSize={12} tickLine={false} axisLine={false} />
                                    <YAxis fontSize={12} tickLine={false} axisLine={false} />
                                    <Tooltip
                                        cursor={{ fill: 'transparent' }}
                                        contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                                    />
                                    <Bar dataKey="value" fill="currentColor" radius={[4, 4, 0, 0]} className="fill-primary" />
                                </BarChart>
                            </ResponsiveContainer>
                        </CardContent>
                    </Card>
                </div>

                {/* Sidebar Details */}
                <div className="space-y-8">
                    <Card>
                        <CardHeader>
                            <CardTitle>Details</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div>
                                <span className="text-sm font-medium text-muted-foreground block mb-1">Status</span>
                                <span className="capitalize font-medium">{campaign.status}</span>
                            </div>
                            <Separator />
                            <div>
                                <span className="text-sm font-medium text-muted-foreground block mb-1">Total Recipients</span>
                                <span className="font-medium">{campaign.total_recipients}</span>
                            </div>
                            <Separator />
                            <div>
                                <span className="text-sm font-medium text-muted-foreground block mb-1">Created At</span>
                                <span className="font-medium">{new Date(campaign.created_at).toLocaleDateString()}</span>
                            </div>
                            <Separator />
                            <div>
                                <span className="text-sm font-medium text-muted-foreground block mb-1">From</span>
                                <div className="font-medium">{campaign.from_name}</div>
                                <div className="text-sm text-muted-foreground">{campaign.from_email}</div>
                            </div>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader>
                            <CardTitle>Settings</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="flex items-center justify-between">
                                <span className="text-sm">Warm-up</span>
                                <Badge variant={campaign.use_warmup ? "secondary" : "outline"}>
                                    {campaign.use_warmup ? 'Enabled' : 'Disabled'}
                                </Badge>
                            </div>
                            <div className="flex items-center justify-between">
                                <span className="text-sm">Track Opens</span>
                                <Badge variant={campaign.track_opens ? "secondary" : "outline"}>
                                    {campaign.track_opens ? 'Enabled' : 'Disabled'}
                                </Badge>
                            </div>
                            <div className="flex items-center justify-between">
                                <span className="text-sm">Track Clicks</span>
                                <Badge variant={campaign.track_clicks ? "secondary" : "outline"}>
                                    {campaign.track_clicks ? 'Enabled' : 'Disabled'}
                                </Badge>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>

    )
}
