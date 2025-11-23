import { useState } from 'react'
import axios from 'axios'

export default function FileUpload({ onUploadSuccess }) {
    const [uploading, setUploading] = useState(false)
    const [error, setError] = useState(null)

    const handleFileChange = async (e) => {
        const file = e.target.files[0]
        if (!file) return

        const formData = new FormData()
        formData.append('file', file)
        setUploading(true)
        setError(null)

        try {
            const response = await axios.post('/api/v1/upload', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            })
            onUploadSuccess(response.data)
        } catch (err) {
            setError('Upload failed. Please try again.')
            console.error(err)
        } finally {
            setUploading(false)
        }
    }

    return (
        <div className="p-8 border-2 border-dashed border-gold-500/30 rounded-2xl glass hover:border-gold-400 hover:shadow-[0_0_20px_rgba(255,193,7,0.1)] transition-all text-center cursor-pointer relative group">
            <input
                type="file"
                onChange={handleFileChange}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                accept=".csv,.xlsx,.xls"
            />
            <div className="flex flex-col items-center space-y-4">
                <div className="p-4 rounded-full bg-zinc-900/50 border border-gold-500/20 group-hover:border-gold-500/50 transition-all">
                    <svg
                        className="w-12 h-12 text-gold-400 group-hover:text-gold-300 transition-colors"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={1.5}
                            d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                        />
                    </svg>
                </div>
                <div>
                    <p className="text-xl font-semibold text-zinc-200 mb-2 group-hover:text-white transition-colors">
                        {uploading ? 'Uploading...' : 'Drop your data file here'}
                    </p>
                    <p className="text-sm text-zinc-500 group-hover:text-gold-500/80 transition-colors">
                        Supports CSV, Excel (XLSX, XLS)
                    </p>
                </div>
                {error && (
                    <p className="text-red-400 text-sm font-medium bg-red-900/20 px-3 py-1 rounded-full border border-red-900/50">{error}</p>
                )}
            </div>
        </div>
    )
}
