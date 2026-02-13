import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { Loader2, Check, Sparkles, ChevronRight, ChevronLeft } from 'lucide-react'
import { campaignAPI, aiAPI } from '../services/api'
import EmailEditor from '../components/EmailEditor'
import RecipientUpload from '../components/RecipientUpload'
import toast from 'react-hot-toast'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Checkbox } from '@/components/ui/checkbox'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog"

// Validation Schemas
const step1Schema = z.object({
    name: z.string().min(1, 'Campaign name is required'),
    subject: z.string().min(1, 'Subject is required'),
    from_name: z.string().min(1, 'From name is required'),
    from_email: z.string().email('Invalid email address'),
    reply_to: z.string().email('Invalid email address').optional().or(z.literal('')),
})

const step3Schema = z.object({
    use_warmup: z.boolean(),
    track_opens: z.boolean(),
    track_clicks: z.boolean(),
})

type Step1Data = z.infer<typeof step1Schema>
type Step3Data = z.infer<typeof step3Schema>

export default function CreateCampaign() {
    const navigate = useNavigate()
    const { id } = useParams() // Get campaign ID from URL if editing
    const isEditMode = Boolean(id)

    const [step, setStep] = useState(1)
    const [campaignId, setCampaignId] = useState<number | null>(null)
    const [loading, setLoading] = useState(false)
    const [fetching, setFetching] = useState(false)

    // Form State (React Hook Form for steps with inputs)
    const form1 = useForm<Step1Data>({
        resolver: zodResolver(step1Schema),
        defaultValues: {
            name: '',
            subject: '',
            from_name: '',
            from_email: '',
            reply_to: '',
        }
    })

    const form3 = useForm<Step3Data>({
        resolver: zodResolver(step3Schema),
        defaultValues: {
            use_warmup: true,
            track_opens: true,
            track_clicks: true,
        }
    })

    // Content State (Editor)
    const [htmlContent, setHtmlContent] = useState('')

    // AI Modal State
    const [showAIModal, setShowAIModal] = useState(false)
    const [aiContext, setAiContext] = useState('')
    const [aiCustomBody, setAiCustomBody] = useState('')
    const [aiTone, setAiTone] = useState('professional')
    const [aiLength, setAiLength] = useState('medium')
    const [isGenerating, setIsGenerating] = useState(false)

    // Example recipient for preview/generation
    const exampleRecipient = {
        first_name: "John",
        last_name: "Doe",
        company: "Acme Corp",
        email: "john@example.com"
    }

    // Fetch campaign data if in edit mode
    useEffect(() => {
        if (isEditMode && id) {
            const fetchCampaign = async () => {
                setFetching(true)
                try {
                    const data = await campaignAPI.get(parseInt(id))
                    setCampaignId(data.id)

                    // Populate Step 1
                    form1.reset({
                        name: data.name,
                        subject: data.subject,
                        from_name: data.from_name,
                        from_email: data.from_email,
                        reply_to: data.reply_to || '',
                    })

                    // Populate Step 2
                    setHtmlContent(data.html_content || '')

                    // Populate Step 3
                    form3.reset({
                        use_warmup: data.use_warmup,
                        track_opens: data.track_opens,
                        track_clicks: data.track_clicks,
                    })

                    // Smart Step Restoration
                    if (!data.html_content) {
                        setStep(2)
                    } else {
                        // If we have content, we assume step 1 & 2 are done.
                        // User can still go back. Default to Step 3 (Settings) or Step 1?
                        // "editing should continue from there" -> usually means the last incomplete thing.
                        // If everything is present, maybe start at Step 1 to review?
                        // Or Step 3. Let's go with Step 1 safely, but user can click through.
                        // ACTUALLY: User asked "continue from there".
                        // If I have content, I'm probably editing settings or ready to send.
                        // Let's set it to Step 3.
                        setStep(3)
                    }

                } catch (error) {
                    console.error("Failed to fetch campaign:", error)
                    toast.error("Failed to load campaign details")
                    navigate('/campaigns')
                } finally {
                    setFetching(false)
                }
            }
            fetchCampaign()
        }
    }, [id, isEditMode, navigate, form1, form3])

    const saveStep1 = async (data: Step1Data) => {
        setLoading(true)
        try {
            if (campaignId) {
                await campaignAPI.update(campaignId, data)
                toast.success('Saved')
            } else {
                const response = await campaignAPI.create({
                    ...data,
                    html_content: '', // Initial empty content
                    use_warmup: true,
                    track_opens: true,
                    track_clicks: true
                })
                setCampaignId(response.id)
                // Update URL to edit mode without reload?
                // ideally navigate(`/campaigns/${response.id}/edit`) but that might reload.
                // For now just keep state.
                toast.success('Campaign Draft Created')
            }
            setStep(2)
        } catch (error: any) {
            console.error('Save error:', error)
            toast.error('Failed to save progress')
        } finally {
            setLoading(false)
        }
    }

    const saveStep2 = async () => {
        if (!campaignId) return // Should not happen if Step 1 created it
        setLoading(true)
        try {
            await campaignAPI.update(campaignId, { html_content: htmlContent })
            toast.success('Content Saved')
            setStep(3)
        } catch (error) {
            console.error('Save error:', error)
            toast.error('Failed to save content')
        } finally {
            setLoading(false)
        }
    }

    const saveStep3 = async () => {
        if (!campaignId) return
        setLoading(true)
        try {
            const step3Data = form3.getValues()
            await campaignAPI.update(campaignId, step3Data)
            toast.success('Settings Saved')
            setStep(4)
        } catch (error) {
            console.error('Save error:', error)
            toast.error('Failed to save settings')
        } finally {
            setLoading(false)
        }
    }

    // Step 1 Submit only triggers validation, then calls save
    const handleStep1Submit = (data: Step1Data) => {
        saveStep1(data)
    }

    const handleGenerateAI = async () => {
        setIsGenerating(true)
        try {
            const result = await aiAPI.generate({
                context: aiContext,
                recipient_data: exampleRecipient,
                tone: aiTone,
                length: aiLength,
                custom_body: aiCustomBody
            })
            form1.setValue('subject', result.subject)
            setHtmlContent(result.html_content)
            setShowAIModal(false)
            toast.success('Email content generated successfully!')
        } catch (error) {
            console.error("AI Generation failed:", error)
            toast.error("Failed to generate content")
        } finally {
            setIsGenerating(false)
        }
    }

    // handleUploadComplete remains the same
    const handleUploadComplete = () => {
        toast.success(isEditMode ? 'Recipients updated!' : 'Campaign ready!')
        // navigate(`/campaigns/${campaignId}`)
        // User might want to verify recipients first?
        // But requested flow is likely fine.
        navigate(`/campaigns/${campaignId}`)
    }

    if (fetching) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
        )
    }

    return (
        <div className="min-h-screen bg-background text-foreground py-12">
            <div className="container mx-auto px-4 max-w-4xl">
                <div className="mb-8">
                    <h1 className="text-3xl font-bold tracking-tight mb-2">
                        {isEditMode ? 'Edit Campaign' : 'Create New Campaign'}
                    </h1>
                    <p className="text-muted-foreground">
                        {isEditMode ? 'Update your campaign details below.' : 'Follow the steps below to launch your email campaign.'}
                    </p>
                </div>

                {/* Progress Steps */}
                <div className="flex items-center mb-12">
                    {[1, 2, 3, 4].map((s) => (
                        <div key={s} className="flex items-center flex-1">
                            <div
                                className={`w-10 h-10 rounded-full flex items-center justify-center font-bold border-2 transition-colors ${step >= s
                                    ? 'bg-primary border-primary text-primary-foreground'
                                    : 'bg-background border-muted text-muted-foreground'
                                    }`}
                            >
                                {step > s ? <Check className="w-5 h-5" /> : s}
                            </div>
                            {s < 4 && (
                                <div
                                    className={`flex-1 h-0.5 mx-4 transition-colors ${step > s ? 'bg-primary' : 'bg-muted'
                                        }`}
                                ></div>
                            )}
                        </div>
                    ))}
                </div>

                <div className="grid gap-8">
                    {/* Step 1: Basic Info */}
                    {step === 1 && (
                        <Card>
                            <CardHeader>
                                <CardTitle>Campaign Details</CardTitle>
                                <CardDescription>Enter the basic information for your campaign.</CardDescription>
                            </CardHeader>
                            <CardContent>
                                <form id="step1-form" onSubmit={form1.handleSubmit(handleStep1Submit)} className="space-y-6">
                                    <div className="grid gap-2">
                                        <Label htmlFor="name">Campaign Name</Label>
                                        <Input id="name" placeholder="e.g., Q1 Product Launch" {...form1.register('name')} />
                                        {form1.formState.errors.name && <p className="text-sm text-destructive">{form1.formState.errors.name.message}</p>}
                                    </div>
                                    <div className="grid gap-2">
                                        <Label htmlFor="subject">Email Subject</Label>
                                        <Input id="subject" placeholder="e.g., Introducing our new feature" {...form1.register('subject')} />
                                        {form1.formState.errors.subject && <p className="text-sm text-destructive">{form1.formState.errors.subject.message}</p>}
                                    </div>
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                        <div className="grid gap-2">
                                            <Label htmlFor="from_name">From Name</Label>
                                            <Input id="from_name" placeholder="e.g., John Doe" {...form1.register('from_name')} />
                                            {form1.formState.errors.from_name && <p className="text-sm text-destructive">{form1.formState.errors.from_name.message}</p>}
                                        </div>
                                        <div className="grid gap-2">
                                            <Label htmlFor="from_email">From Email</Label>
                                            <Input id="from_email" type="email" placeholder="e.g., john@example.com" {...form1.register('from_email')} />
                                            {form1.formState.errors.from_email && <p className="text-sm text-destructive">{form1.formState.errors.from_email.message}</p>}
                                        </div>
                                    </div>
                                    <div className="grid gap-2">
                                        <Label htmlFor="reply_to">Reply-To Email (Optional)</Label>
                                        <Input id="reply_to" type="email" placeholder="e.g., support@example.com" {...form1.register('reply_to')} />
                                        {form1.formState.errors.reply_to && <p className="text-sm text-destructive">{form1.formState.errors.reply_to.message}</p>}
                                    </div>
                                </form>
                            </CardContent>
                            <CardFooter className="flex justify-end">
                                <Button type="submit" form="step1-form" disabled={loading}>
                                    {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                                    Next Step <ChevronRight className="ml-2 h-4 w-4" />
                                </Button>
                            </CardFooter>
                        </Card>
                    )}

                    {/* Step 2: Content */}
                    {step === 2 && (
                        <Card>
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                <div className="space-y-1">
                                    <CardTitle>Email Content</CardTitle>
                                    <CardDescription>Design your email template.</CardDescription>
                                </div>
                                <Dialog open={showAIModal} onOpenChange={setShowAIModal}>
                                    <DialogTrigger asChild>
                                        <Button variant="outline" className="gap-2">
                                            <Sparkles className="h-4 w-4 text-purple-600" />
                                            Generate with AI
                                        </Button>
                                    </DialogTrigger>
                                    <DialogContent className="sm:max-w-[600px]">
                                        <DialogHeader>
                                            <DialogTitle>Generate Email Content</DialogTitle>
                                            <DialogDescription>
                                                Use AI to generate a personalized email draft.
                                            </DialogDescription>
                                        </DialogHeader>
                                        <div className="grid gap-4 py-4">
                                            <div className="grid gap-2">
                                                <Label htmlFor="ai-context">Instructions / Context</Label>
                                                <Textarea
                                                    id="ai-context"
                                                    placeholder="e.g., Write a cold outreach email offering SEO services..."
                                                    value={aiContext}
                                                    onChange={(e) => setAiContext(e.target.value)}
                                                    className="min-h-[100px]"
                                                />
                                            </div>
                                            <div className="grid gap-2">
                                                <Label htmlFor="ai-body">Custom Draft (Optional)</Label>
                                                <Textarea
                                                    id="ai-body"
                                                    placeholder="Paste your rough draft here..."
                                                    value={aiCustomBody}
                                                    onChange={(e) => setAiCustomBody(e.target.value)}
                                                    className="min-h-[100px]"
                                                />
                                            </div>
                                            <div className="grid grid-cols-2 gap-4">
                                                <div className="grid gap-2">
                                                    <Label>Tone</Label>
                                                    <Select value={aiTone} onValueChange={setAiTone}>
                                                        <SelectTrigger>
                                                            <SelectValue />
                                                        </SelectTrigger>
                                                        <SelectContent>
                                                            <SelectItem value="professional">Professional</SelectItem>
                                                            <SelectItem value="casual">Casual</SelectItem>
                                                            <SelectItem value="friendly">Friendly</SelectItem>
                                                            <SelectItem value="urgent">Urgent</SelectItem>
                                                            <SelectItem value="persuasive">Persuasive</SelectItem>
                                                        </SelectContent>
                                                    </Select>
                                                </div>
                                                <div className="grid gap-2">
                                                    <Label>Length</Label>
                                                    <Select value={aiLength} onValueChange={setAiLength}>
                                                        <SelectTrigger>
                                                            <SelectValue />
                                                        </SelectTrigger>
                                                        <SelectContent>
                                                            <SelectItem value="short">Short</SelectItem>
                                                            <SelectItem value="medium">Medium</SelectItem>
                                                            <SelectItem value="long">Long</SelectItem>
                                                        </SelectContent>
                                                    </Select>
                                                </div>
                                            </div>
                                        </div>
                                        <DialogFooter>
                                            <Button variant="ghost" onClick={() => setShowAIModal(false)}>Cancel</Button>
                                            <Button onClick={handleGenerateAI} disabled={!aiContext && !aiCustomBody} className="gap-2">
                                                {isGenerating ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
                                                Generate
                                            </Button>
                                        </DialogFooter>
                                    </DialogContent>
                                </Dialog>
                            </CardHeader>
                            <CardContent className="pt-6">
                                <EmailEditor
                                    content={htmlContent}
                                    onChange={setHtmlContent}
                                    placeholder="Write your email content here..."
                                />
                            </CardContent>
                            <CardFooter className="flex justify-between">
                                <Button variant="outline" onClick={() => setStep(1)}>
                                    <ChevronLeft className="mr-2 h-4 w-4" /> Back
                                </Button>
                                <Button onClick={saveStep2} disabled={!htmlContent || loading}>
                                    {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                                    Next Step <ChevronRight className="ml-2 h-4 w-4" />
                                </Button>
                            </CardFooter>
                        </Card>
                    )}

                    {/* Step 3: Settings */}
                    {step === 3 && (
                        <Card>
                            <CardHeader>
                                <CardTitle>Campaign Settings</CardTitle>
                                <CardDescription>Configure tracking and delivery options.</CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-6">
                                <div className="flex items-center justify-between space-x-2 border p-4 rounded-lg">
                                    <Label htmlFor="use_warmup" className="flex flex-col space-y-1">
                                        <span>Use Warm-up</span>
                                        <span className="font-normal text-muted-foreground">Gradually increase sending volume.</span>
                                    </Label>
                                    <Checkbox
                                        id="use_warmup"
                                        checked={form3.watch('use_warmup')}
                                        onCheckedChange={(checked) => form3.setValue('use_warmup', checked as boolean)}
                                    />
                                </div>
                                <div className="flex items-center justify-between space-x-2 border p-4 rounded-lg">
                                    <Label htmlFor="track_opens" className="flex flex-col space-y-1">
                                        <span>Track Opens</span>
                                        <span className="font-normal text-muted-foreground">Monitor when emails are opened.</span>
                                    </Label>
                                    <Checkbox
                                        id="track_opens"
                                        checked={form3.watch('track_opens')}
                                        onCheckedChange={(checked) => form3.setValue('track_opens', checked as boolean)}
                                    />
                                </div>
                                <div className="flex items-center justify-between space-x-2 border p-4 rounded-lg">
                                    <Label htmlFor="track_clicks" className="flex flex-col space-y-1">
                                        <span>Track Clicks</span>
                                        <span className="font-normal text-muted-foreground">Monitor link clicks within emails.</span>
                                    </Label>
                                    <Checkbox
                                        id="track_clicks"
                                        checked={form3.watch('track_clicks')}
                                        onCheckedChange={(checked) => form3.setValue('track_clicks', checked as boolean)}
                                    />
                                </div>
                            </CardContent>
                            <CardFooter className="flex justify-between">
                                <Button variant="outline" onClick={() => setStep(2)}>
                                    <ChevronLeft className="mr-2 h-4 w-4" /> Back
                                </Button>
                                <Button onClick={saveStep3} disabled={loading}>
                                    {loading ? (
                                        <>
                                            <Loader2 className="mr-2 h-4 w-4 animate-spin" /> Saving...
                                        </>
                                    ) : (
                                        <>
                                            Next: Add Recipients <ChevronRight className="ml-2 h-4 w-4" />
                                        </>
                                    )}
                                </Button>
                            </CardFooter>
                        </Card>
                    )}

                    {/* Step 4: Upload Recipients */}
                    {step === 4 && campaignId && (
                        <Card>
                            <CardHeader>
                                <CardTitle>Add Recipients</CardTitle>
                                <CardDescription>Upload your recipient list (CSV).</CardDescription>
                            </CardHeader>
                            <CardContent>
                                <RecipientUpload
                                    campaignId={campaignId}
                                    onUploadComplete={handleUploadComplete}
                                />
                            </CardContent>
                            <CardFooter className="flex justify-center">
                                <Button variant="link" onClick={() => navigate(`/campaigns/${campaignId}`)}>
                                    {isEditMode ? 'Finished Editing' : 'Skip for now'}
                                </Button>
                            </CardFooter>
                        </Card>
                    )}
                </div>
            </div>
        </div>
    )
}
