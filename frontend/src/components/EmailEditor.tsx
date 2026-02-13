import { useEditor, EditorContent } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import Placeholder from '@tiptap/extension-placeholder'
import { useState } from 'react'

interface EmailEditorProps {
    content: string
    onChange: (html: string) => void
    placeholder?: string
}

export default function EmailEditor({ content, onChange, placeholder }: EmailEditorProps) {
    const [showVariables, setShowVariables] = useState(false)

    const editor = useEditor({
        extensions: [
            StarterKit,
            Placeholder.configure({
                placeholder: placeholder || 'Write your email content here...',
            }),
        ],
        content,
        onUpdate: ({ editor }) => {
            onChange(editor.getHTML())
        },
    })

    const insertVariable = (variable: string) => {
        if (editor) {
            editor.chain().focus().insertContent(`{{${variable}}}`).run()
        }
    }

    const commonVariables = [
        'first_name',
        'last_name',
        'email',
        'company',
        'position',
        'city',
        'country',
    ]

    if (!editor) {
        return (
            <div className="border border-input rounded-lg p-8 text-center text-muted-foreground">
                Loading editor...
            </div>
        )
    }

    return (
        <div className="border border-input rounded-lg overflow-hidden bg-background">
            {/* Toolbar */}
            <div className="bg-muted/50 border-b border-input p-2 flex flex-wrap gap-1">
                <button
                    onClick={() => editor.chain().focus().toggleBold().run()}
                    className={`px-3 py-1 rounded hover:bg-muted ${editor.isActive('bold') ? 'bg-muted text-foreground font-bold' : 'text-muted-foreground'
                        }`}
                    title="Bold"
                >
                    <strong>B</strong>
                </button>

                <button
                    onClick={() => editor.chain().focus().toggleItalic().run()}
                    className={`px-3 py-1 rounded hover:bg-muted ${editor.isActive('italic') ? 'bg-muted text-foreground' : 'text-muted-foreground'
                        }`}
                    title="Italic"
                >
                    <em>I</em>
                </button>

                <button
                    onClick={() => editor.chain().focus().toggleStrike().run()}
                    className={`px-3 py-1 rounded hover:bg-muted ${editor.isActive('strike') ? 'bg-muted text-foreground' : 'text-muted-foreground'
                        }`}
                    title="Strikethrough"
                >
                    <s>S</s>
                </button>

                <div className="w-px bg-border mx-1"></div>

                <button
                    onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()}
                    className={`px-3 py-1 rounded hover:bg-muted ${editor.isActive('heading', { level: 1 }) ? 'bg-muted text-foreground' : 'text-muted-foreground'
                        }`}
                    title="Heading 1"
                >
                    H1
                </button>

                <button
                    onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
                    className={`px-3 py-1 rounded hover:bg-muted ${editor.isActive('heading', { level: 2 }) ? 'bg-muted text-foreground' : 'text-muted-foreground'
                        }`}
                    title="Heading 2"
                >
                    H2
                </button>

                <div className="w-px bg-border mx-1"></div>

                <button
                    onClick={() => editor.chain().focus().toggleBulletList().run()}
                    className={`px-3 py-1 rounded hover:bg-muted ${editor.isActive('bulletList') ? 'bg-muted text-foreground' : 'text-muted-foreground'
                        }`}
                    title="Bullet List"
                >
                    • List
                </button>

                <button
                    onClick={() => editor.chain().focus().toggleOrderedList().run()}
                    className={`px-3 py-1 rounded hover:bg-muted ${editor.isActive('orderedList') ? 'bg-muted text-foreground' : 'text-muted-foreground'
                        }`}
                    title="Numbered List"
                >
                    1. List
                </button>

                <div className="w-px bg-border mx-1"></div>

                <div className="relative">
                    <button
                        onClick={() => setShowVariables(!showVariables)}
                        className="px-3 py-1 rounded hover:bg-muted bg-primary text-primary-foreground text-sm font-medium"
                        title="Insert Variable"
                    >
                        {'{{'} Var {'}}'}
                    </button>

                    {showVariables && (
                        <div className="absolute top-full left-0 mt-1 bg-popover border border-border rounded-lg shadow-lg p-2 z-10 min-w-[200px]">
                            <div className="text-xs font-semibold text-muted-foreground mb-2 px-2">
                                Insert Variable
                            </div>
                            {commonVariables.map((variable) => (
                                <button
                                    key={variable}
                                    onClick={() => {
                                        insertVariable(variable)
                                        setShowVariables(false)
                                    }}
                                    className="block w-full text-left px-3 py-1 rounded hover:bg-muted text-sm text-popover-foreground"
                                >
                                    {'{{'}{variable}{'}}'}
                                </button>
                            ))}
                        </div>
                    )}
                </div>

                <div className="flex-1"></div>

                <button
                    onClick={() => editor.chain().focus().undo().run()}
                    disabled={!editor.can().undo()}
                    className="px-3 py-1 rounded hover:bg-muted disabled:opacity-50 text-muted-foreground"
                    title="Undo"
                >
                    ↶
                </button>

                <button
                    onClick={() => editor.chain().focus().redo().run()}
                    disabled={!editor.can().redo()}
                    className="px-3 py-1 rounded hover:bg-muted disabled:opacity-50 text-muted-foreground"
                    title="Redo"
                >
                    ↷
                </button>
            </div>

            {/* Editor Content */}
            <EditorContent
                editor={editor}
                className="prose prose-sm dark:prose-invert max-w-none p-4 min-h-[400px] focus:outline-none text-foreground"
            />
        </div>
    )
}
