import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { campaignAPI } from '../services/api'
import { useAuthStore } from '../store/authStore'
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '@/components/ui/table'
import { Button } from '@/components/ui/button'
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Loader2, Plus, Trash2, Eye } from 'lucide-react'
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

export default function Campaigns() {
    const navigate = useNavigate()
    const logout = useAuthStore((state) => state.logout)
    const user = useAuthStore((state) => state.user)
    const queryClient = useQueryClient()

    const { data: campaigns = [], isLoading } = useQuery({
        queryKey: ['campaigns'],
        queryFn: campaignAPI.list,
    })

    const deleteMutation = useMutation({
        mutationFn: campaignAPI.delete,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['campaigns'] })
            toast.success('Campaign deleted successfully')
        },
        onError: (error) => {
            console.error('Delete failed:', error)
            toast.error('Failed to delete campaign')
        }
    })

    const handleLogout = () => {
        logout()
        navigate('/login')
    }

    const handleDelete = (id: number) => {
        deleteMutation.mutate(id)
    }

    const getStatusVariant = (status: string) => {
        switch (status) {
            case 'completed': return 'default' // Primary/Black
            case 'sending': return 'secondary'
            case 'scheduled': return 'outline'
            case 'failed': return 'destructive'
            default: return 'secondary'
        }
    }

    return (
        <div className="min-h-screen bg-background text-foreground">
            {/* Header - Minimalist */}
            <header className="border-b">
                <div className="container mx-auto px-4 py-4 flex justify-between items-center">
                    <h1 className="text-xl font-bold tracking-tight">Email Automation</h1>
                    <div className="flex items-center gap-4">
                        <span className="text-sm text-muted-foreground">{user?.username}</span>
                        <Button variant="ghost" size="sm" onClick={handleLogout}>
                            Logout
                        </Button>
                    </div>
                </div>
            </header>

            <main className="container mx-auto px-4 py-8">
                <div className="flex justify-between items-center mb-8">
                    <div>
                        <h2 className="text-3xl font-bold tracking-tight">Campaigns</h2>
                        <p className="text-muted-foreground mt-1">Manage your email campaigns here.</p>
                    </div>
                    <Button onClick={() => navigate('/campaigns/create')}>
                        <Plus className="mr-2 h-4 w-4" /> Create Campaign
                    </Button>
                </div>

                <Card>
                    <CardHeader>
                        <CardTitle>All Campaigns</CardTitle>
                        <CardDescription>
                            A list of your email campaigns and their current status.
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        {isLoading ? (
                            <div className="flex justify-center py-8">
                                <Loader2 className="h-8 w-8 animate-spin text-primary" />
                            </div>
                        ) : campaigns.length === 0 ? (
                            <div className="text-center py-12">
                                <p className="text-muted-foreground mb-4">No campaigns found.</p>
                                <Button onClick={() => navigate('/campaigns/create')}>
                                    Create your first campaign
                                </Button>
                            </div>
                        ) : (
                            <Table>
                                <TableHeader>
                                    <TableRow>
                                        <TableHead>Campaign Name</TableHead>
                                        <TableHead>Status</TableHead>
                                        <TableHead>Recipients</TableHead>
                                        <TableHead>Sent</TableHead>
                                        <TableHead>Created</TableHead>
                                        <TableHead className="text-right">Actions</TableHead>
                                    </TableRow>
                                </TableHeader>
                                <TableBody>
                                    {campaigns.map((campaign: any) => (
                                        <TableRow key={campaign.id}>
                                            <TableCell className="font-medium">
                                                <div>
                                                    <div>{campaign.name}</div>
                                                    <div className="text-xs text-muted-foreground">{campaign.subject}</div>
                                                </div>
                                            </TableCell>
                                            <TableCell>
                                                <Badge variant={getStatusVariant(campaign.status)}>
                                                    {campaign.status}
                                                </Badge>
                                            </TableCell>
                                            <TableCell>{campaign.total_recipients}</TableCell>
                                            <TableCell>
                                                <span>{campaign.sent_count}</span>
                                                {campaign.failed_count > 0 && (
                                                    <span className="text-xs text-destructive ml-2">({campaign.failed_count} failed)</span>
                                                )}
                                            </TableCell>
                                            <TableCell>
                                                {new Date(campaign.created_at).toLocaleDateString()}
                                            </TableCell>
                                            <TableCell className="text-right space-x-2">
                                                <Button
                                                    variant="ghost"
                                                    size="icon"
                                                    onClick={() => navigate(`/campaigns/${campaign.id}`)}
                                                >
                                                    <Eye className="h-4 w-4" />
                                                </Button>

                                                <AlertDialog>
                                                    <AlertDialogTrigger asChild>
                                                        <Button variant="ghost" size="icon" className="text-destructive hover:text-destructive hover:bg-destructive/10">
                                                            <Trash2 className="h-4 w-4" />
                                                        </Button>
                                                    </AlertDialogTrigger>
                                                    <AlertDialogContent>
                                                        <AlertDialogHeader>
                                                            <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
                                                            <AlertDialogDescription>
                                                                This action cannot be undone. This will permanently delete the campaign
                                                                "{campaign.name}" and all its data.
                                                            </AlertDialogDescription>
                                                        </AlertDialogHeader>
                                                        <AlertDialogFooter>
                                                            <AlertDialogCancel>Cancel</AlertDialogCancel>
                                                            <AlertDialogAction
                                                                onClick={() => handleDelete(campaign.id)}
                                                                className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                                                            >
                                                                Delete
                                                            </AlertDialogAction>
                                                        </AlertDialogFooter>
                                                    </AlertDialogContent>
                                                </AlertDialog>
                                            </TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        )}
                    </CardContent>
                </Card>
            </main>
        </div>
    )
}
