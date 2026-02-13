import { useState, useEffect } from 'react'
import { Plus, Trash, UserPlus, Loader2 } from 'lucide-react'
import { useForm, useFieldArray } from 'react-hook-form'
import * as z from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'
import toast from 'react-hot-toast'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

interface ManualRecipientEntryProps {
    campaignId: number
}

const recipientSchema = z.object({
    email: z.string().email('Invalid email address'),
    first_name: z.string().optional(),
    last_name: z.string().optional(),
    custom_fields: z.array(z.object({
        key: z.string().min(1, 'Key is required'),
        value: z.string().min(1, 'Value is required')
    })).optional()
})

type RecipientFormData = z.infer<typeof recipientSchema>

export default function ManualRecipientEntry({ campaignId }: ManualRecipientEntryProps) {
    const [loading, setLoading] = useState(false)

    const [recipients, setRecipients] = useState<any[]>([])

    const fetchRecipients = async () => {
        try {
            const response = await fetch(`http://localhost:8000/campaigns/${campaignId}/recipients`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            })
            if (response.ok) {
                const data = await response.json()
                setRecipients(data)
            }
        } catch (error) {
            console.error('Failed to fetch recipients:', error)
        }
    }

    // Fetch on mount
    useEffect(() => {
        fetchRecipients()
    }, [campaignId])

    const form = useForm<RecipientFormData>({
        resolver: zodResolver(recipientSchema),
        defaultValues: {
            email: '',
            first_name: '',
            last_name: '',
            custom_fields: []
        }
    })

    const { fields, append, remove } = useFieldArray({
        control: form.control,
        name: "custom_fields"
    })

    const onSubmit = async (data: RecipientFormData) => {
        setLoading(true)
        try {
            const token = localStorage.getItem('token')

            // Format data for API
            const personalization_data = data.custom_fields?.reduce((acc, field) => {
                acc[field.key] = field.value
                return acc
            }, {} as Record<string, string>) || {}

            const recipientPayload = {
                campaign_id: campaignId,
                recipients: [{
                    email: data.email,
                    first_name: data.first_name || null,
                    last_name: data.last_name || null,
                    personalization_data
                }]
            }

            const response = await fetch(`http://localhost:8000/campaigns/${campaignId}/recipients`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(recipientPayload)
            })

            if (!response.ok) {
                const errorData = await response.json()
                throw new Error(errorData.detail || 'Failed to add recipient')
            }

            toast.success('Recipient added successfully')
            form.reset({
                email: '',
                first_name: '',
                last_name: '',
                custom_fields: []
            })
            fetchRecipients() // Refresh list
            // onAddComplete is available if needed to trigger parent updates
        } catch (error: any) {
            console.error('Error adding recipient:', error)
            toast.error(error.message || 'Failed to add recipient')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="space-y-8">
            <div className="space-y-4">
                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <Label htmlFor="email">Email <span className="text-red-500">*</span></Label>
                            <Input
                                id="email"
                                placeholder="recipient@example.com"
                                {...form.register('email')}
                            />
                            {form.formState.errors.email && (
                                <p className="text-sm text-destructive">{form.formState.errors.email.message}</p>
                            )}
                        </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <Label htmlFor="first_name">First Name</Label>
                            <Input
                                id="first_name"
                                placeholder="John"
                                {...form.register('first_name')}
                            />
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="last_name">Last Name</Label>
                            <Input
                                id="last_name"
                                placeholder="Doe"
                                {...form.register('last_name')}
                            />
                        </div>
                    </div>

                    <div className="space-y-4 pt-4 border-t">
                        <div className="flex items-center justify-between">
                            <Label>Custom Fields (Personalization)</Label>
                            <Button
                                type="button"
                                variant="outline"
                                size="sm"
                                onClick={() => append({ key: '', value: '' })}
                            >
                                <Plus className="h-3 w-3 mr-1" /> Add Field
                            </Button>
                        </div>

                        {fields.length === 0 && (
                            <p className="text-sm text-muted-foreground italic">
                                No custom fields added. Add fields like 'Company', 'City' for personalization.
                            </p>
                        )}

                        {fields.map((field, index) => (
                            <div key={field.id} className="flex items-end gap-3">
                                <div className="flex-1 space-y-2">
                                    <Label htmlFor={`custom_fields.${index}.key`} className="text-xs">Field Name</Label>
                                    <Input
                                        placeholder="e.g. company"
                                        {...form.register(`custom_fields.${index}.key` as const)}
                                    />
                                    {form.formState.errors.custom_fields?.[index]?.key && (
                                        <p className="text-xs text-destructive">{form.formState.errors.custom_fields[index]?.key?.message}</p>
                                    )}
                                </div>
                                <div className="flex-1 space-y-2">
                                    <Label htmlFor={`custom_fields.${index}.value`} className="text-xs">Value</Label>
                                    <Input
                                        placeholder="e.g. Acme Inc"
                                        {...form.register(`custom_fields.${index}.value` as const)}
                                    />
                                    {form.formState.errors.custom_fields?.[index]?.value && (
                                        <p className="text-xs text-destructive">{form.formState.errors.custom_fields[index]?.value?.message}</p>
                                    )}
                                </div>
                                <Button
                                    type="button"
                                    variant="ghost"
                                    size="icon"
                                    className="text-destructive"
                                    onClick={() => remove(index)}
                                >
                                    <Trash className="h-4 w-4" />
                                </Button>
                            </div>
                        ))}
                    </div>

                    <div className="pt-4 flex justify-end">
                        <Button type="submit" disabled={loading}>
                            {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <UserPlus className="mr-2 h-4 w-4" />}
                            Add Recipient
                        </Button>
                    </div>
                </form>
            </div>

            {/* Recipient List */}
            <div className="pt-6 border-t">
                <h3 className="text-lg font-semibold mb-4">Added Recipients ({recipients.length})</h3>
                {recipients.length === 0 ? (
                    <p className="text-muted-foreground text-sm">No recipients added yet.</p>
                ) : (
                    <div className="border rounded-md">
                        <div className="max-h-60 overflow-y-auto">
                            <table className="w-full text-sm text-left">
                                <thead className="text-xs text-muted-foreground uppercase bg-muted/50 sticky top-0">
                                    <tr>
                                        <th className="px-4 py-3">Email</th>
                                        <th className="px-4 py-3">Name</th>
                                        <th className="px-4 py-3">Status</th>
                                        <th className="px-4 py-3 text-right">Actions</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y">
                                    {recipients.map((r, i) => (
                                        <tr key={i} className="bg-background">
                                            <td className="px-4 py-3 font-medium">{r.email}</td>
                                            <td className="px-4 py-3">
                                                {[r.first_name, r.last_name].filter(Boolean).join(' ') || '-'}
                                            </td>
                                            <td className="px-4 py-3">
                                                <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${r.is_sent ? 'bg-green-100 text-green-800' :
                                                    r.is_failed ? 'bg-red-100 text-red-800' :
                                                        'bg-gray-100 text-gray-800'
                                                    }`}>
                                                    {r.is_sent ? 'Sent' : r.is_failed ? 'Failed' : 'Pending'}
                                                </span>
                                            </td>
                                            <td className="px-4 py-3 text-right">
                                                <Button
                                                    variant="ghost"
                                                    size="icon"
                                                    className="h-8 w-8 text-destructive hover:text-destructive/90 hover:bg-destructive/10"
                                                    onClick={async () => {
                                                        if (!confirm('Are you sure you want to delete this recipient?')) return
                                                        try {
                                                            const token = localStorage.getItem('token')
                                                            await fetch(`http://localhost:8000/campaigns/${campaignId}/recipients/${r.id}`, {
                                                                method: 'DELETE',
                                                                headers: {
                                                                    'Authorization': `Bearer ${token}`
                                                                }
                                                            })
                                                            toast.success('Recipient deleted')
                                                            fetchRecipients()
                                                        } catch (error) {
                                                            console.error('Failed to delete recipient:', error)
                                                            toast.error('Failed to delete recipient')
                                                        }
                                                    }}
                                                >
                                                    <Trash className="h-4 w-4" />
                                                </Button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}
            </div>
        </div>
    )
}
