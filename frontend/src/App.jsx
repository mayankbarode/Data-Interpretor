import { useState, useEffect } from 'react'
import FileUpload from './components/FileUpload'
import ChatInterface from './components/ChatInterface'

function App() {
    const [session, setSession] = useState(null)

    return (
        <div className="min-h-screen p-8">
            <div className="max-w-6xl mx-auto">
                <header className="mb-10 text-center">
                    <h1 className="text-5xl font-bold text-white mb-3 drop-shadow-lg">
                        🤖 Data Interpreter Agent
                    </h1>
                    <p className="text-purple-100 text-lg">
                        Upload your data and let AI analyze it for you
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
