import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import toast from 'react-hot-toast'
import { Upload, FileSpreadsheet, UserPlus } from 'lucide-react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import ManualRecipientEntry from './ManualRecipientEntry'

interface RecipientUploadProps {
    campaignId: number
    onUploadComplete: () => void
}

interface ParsedRecipient {
    email: string
    first_name?: string
    last_name?: string
    [key: string]: any
}

export default function RecipientUpload({ campaignId, onUploadComplete }: RecipientUploadProps) {
    const [uploading, setUploading] = useState(false)
    const [parsedData, setParsedData] = useState<ParsedRecipient[]>([])
    const [columns, setColumns] = useState<string[]>([])
    const [showPreview, setShowPreview] = useState(false)
    const [activeTab, setActiveTab] = useState('upload')

    const onDrop = useCallback(async (acceptedFiles: File[]) => {
        const file = acceptedFiles[0]
        if (!file) return

        setUploading(true)
        try {
            // Parse CSV/Excel file
            const text = await file.text()
            const lines = text.split('\n').filter(line => line.trim())

            if (lines.length === 0) {
                toast.error('File is empty')
                return
            }

            // Parse header
            const headers = lines[0].split(',').map(h => h.trim().replace(/"/g, ''))
            setColumns(headers)

            // Parse data
            const data: ParsedRecipient[] = []
            for (let i = 1; i < lines.length; i++) {
                const values = lines[i].split(',').map(v => v.trim().replace(/"/g, ''))
                const row: ParsedRecipient = { email: '' }

                headers.forEach((header, index) => {
                    row[header] = values[index] || ''
                })

                if (row.email) {
                    data.push(row)
                }
            }

            setParsedData(data)
            setShowPreview(true)
            toast.success(`Parsed ${data.length} recipients`)
        } catch (error) {
            toast.error('Failed to parse file')
            console.error(error)
        } finally {
            setUploading(false)
        }
    }, [])

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'text/csv': ['.csv'],
            'application/vnd.ms-excel': ['.xls'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx']
        },
        maxFiles: 1
    })

    const handleUpload = async () => {
        setUploading(true)
        try {
            const token = localStorage.getItem('token')
            const response = await fetch(`http://localhost:8000/campaigns/${campaignId}/recipients`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    campaign_id: campaignId,
                    recipients: parsedData.map(r => ({
                        email: r.email,
                        first_name: r.first_name || null,
                        last_name: r.last_name || null,
                        personalization_data: Object.fromEntries(
                            Object.entries(r).filter(([key]) =>
                                !['email', 'first_name', 'last_name'].includes(key)
                            )
                        )
                    }))
                })
            })

            if (!response.ok) {
                throw new Error('Upload failed')
            }

            toast.success(`Uploaded ${parsedData.length} recipients`)
            onUploadComplete()
        } catch (error) {
            toast.error('Failed to upload recipients')
            console.error(error)
        } finally {
            setUploading(false)
        }
    }

    return (
        <Tabs defaultValue="upload" value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-2 mb-6">
                <TabsTrigger value="upload" className="flex items-center gap-2">
                    <FileSpreadsheet className="h-4 w-4" />
                    Upload CSV/Excel
                </TabsTrigger>
                <TabsTrigger value="manual" className="flex items-center gap-2">
                    <UserPlus className="h-4 w-4" />
                    Manual Entry
                </TabsTrigger>
            </TabsList>

            <TabsContent value="upload" className="space-y-6">
                {/* File Upload */}
                {!showPreview && (
                    <div
                        {...getRootProps()}
                        className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors ${isDragActive
                            ? 'border-primary bg-primary/10'
                            : 'border-muted-foreground/25 hover:border-primary/50'
                            }`}
                    >
                        <input {...getInputProps()} />
                        <div className="space-y-4">
                            <div className="flex justify-center">
                                <div className="h-12 w-12 rounded-full bg-muted flex items-center justify-center">
                                    <Upload className="h-6 w-6 text-muted-foreground" />
                                </div>
                            </div>
                            <div>
                                <p className="text-lg font-medium">
                                    {isDragActive ? 'Drop the file here' : 'Drag & drop a CSV file'}
                                </p>
                                <p className="text-sm text-muted-foreground mt-1">or click to browse</p>
                            </div>
                            <p className="text-xs text-muted-foreground">
                                Supported formats: .csv, .xls, .xlsx
                            </p>
                            <div className="text-xs text-muted-foreground border p-2 rounded bg-muted/50 inline-block text-left">
                                <p className="font-semibold mb-1">Required Columns:</p>
                                <ul className="list-disc list-inside">
                                    <li>email</li>
                                    <li>first_name (optional)</li>
                                    <li>last_name (optional)</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                )}

                {/* Preview */}
                {showPreview && parsedData.length > 0 && (
                    <div className="space-y-4">
                        <div className="flex items-center justify-between">
                            <h3 className="text-lg font-semibold">
                                Preview ({parsedData.length} recipients)
                            </h3>
                            <button
                                onClick={() => {
                                    setShowPreview(false)
                                    setParsedData([])
                                }}
                                className="text-sm text-red-600 hover:underline"
                            >
                                Cancel & Upload Different File
                            </button>
                        </div>

                        {/* Data Table */}
                        <div className="border rounded-lg overflow-hidden">
                            <div className="overflow-x-auto max-h-96">
                                <table className="min-w-full divide-y divide-border">
                                    <thead className="bg-muted sticky top-0">
                                        <tr>
                                            {columns.map((col) => (
                                                <th
                                                    key={col}
                                                    className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider"
                                                >
                                                    {col}
                                                </th>
                                            ))}
                                        </tr>
                                    </thead>
                                    <tbody className="bg-background divide-y divide-border">
                                        {parsedData.slice(0, 10).map((row, idx) => (
                                            <tr key={idx}>
                                                {columns.map((col) => (
                                                    <td
                                                        key={col}
                                                        className="px-4 py-3 text-sm whitespace-nowrap"
                                                    >
                                                        {row[col]}
                                                    </td>
                                                ))}
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                            {parsedData.length > 10 && (
                                <div className="bg-muted/50 px-4 py-2 text-sm text-muted-foreground text-center">
                                    Showing 10 of {parsedData.length} recipients
                                </div>
                            )}
                        </div>

                        {/* Upload Button */}
                        <div className="flex justify-end">
                            <button
                                onClick={handleUpload}
                                disabled={uploading}
                                className="bg-primary text-primary-foreground px-6 py-2 rounded-lg hover:bg-primary/90 disabled:opacity-50 flex items-center gap-2"
                            >
                                {uploading ? (
                                    <>Processing...</>
                                ) : (
                                    <>
                                        <Upload className="h-4 w-4" />
                                        Upload {parsedData.length} Recipients
                                    </>
                                )}
                            </button>
                        </div>
                    </div>
                )}

                {uploading && !showPreview && (
                    <div className="text-center py-8">
                        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                        <p className="mt-2 text-muted-foreground">Processing file...</p>
                    </div>
                )}
            </TabsContent>

            <TabsContent value="manual">
                <ManualRecipientEntry
                    campaignId={campaignId}
                />
            </TabsContent>
        </Tabs>
    )
}
