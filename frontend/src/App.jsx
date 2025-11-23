import { useState, useEffect } from 'react'
import FileUpload from './components/FileUpload'
import ChatInterface from './components/ChatInterface'

function App() {
    const [session, setSession] = useState(null)

    return (
        <div className="min-h-screen p-8">
            <div className="max-w-6xl mx-auto">
                <header className="mb-10 text-center">
                    <h1 className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-gold-300 via-gold-500 to-gold-300 mb-3 drop-shadow-lg tracking-tight">
                        Data Interpreter Agent
                    </h1>
                    <p className="text-zinc-400 text-lg font-light">
                        Upload your data and let <span className="text-gold-400 font-medium">AI</span> analyze it for you
                    </p>
                </header>

                {!session ? (
                    <div className="max-w-2xl mx-auto">
                        <FileUpload onUploadSuccess={setSession} />
                    </div>
                ) : (
                    <ChatInterface
                        fileId={session.file_id}
                        filename={session.filename}
                    />
                )}
            </div>
        </div>
    )
}

export default App
