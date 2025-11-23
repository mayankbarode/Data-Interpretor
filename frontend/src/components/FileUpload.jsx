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
        <div className="p-8 border-2 border-dashed border-purple-300 rounded-2xl glass hover:shadow-2xl transition-all text-center cursor-pointer relative">
            <input
                type="file"
                onChange={handleFileChange}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                accept=".csv,.xlsx,.xls"
            />
            <div className="flex flex-col items-center space-y-4">
                <svg
                    className="w-16 h-16 text-purple-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                >
                    <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                    />
                </svg>
                <div>
                    <p className="text-xl font-semibold text-gray-800 mb-2">
                        {uploading ? 'Uploading...' : 'Drop your data file here'}
                    </p>
                    <p className="text-sm text-gray-500">
                        Supports CSV, Excel (XLSX, XLS)
                    </p>
                </div>
                {error && (
                    <p className="text-red-500 text-sm font-medium">{error}</p>
                )}
            </div>
        </div>
    )
}
