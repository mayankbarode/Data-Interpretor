import { useState, useEffect } from 'react'
import Plot from 'react-plotly.js'

export default function PlotCarousel({ plots }) {
    const [currentSlide, setCurrentSlide] = useState(0)
    const [plotData, setPlotData] = useState({ data: [], layout: {} })

    if (!plots || plots.length === 0) return null

    const nextSlide = () => setCurrentSlide((prev) => (prev + 1) % plots.length)
    const prevSlide = () => setCurrentSlide((prev) => (prev - 1 + plots.length) % plots.length)

    const plot = plots[currentSlide]
    const showNav = plots.length > 1

    // Extract Plotly data from HTML
    useEffect(() => {
        if (!plot.html) return

        console.log('Plot HTML received:', plot.html.substring(0, 500))

        try {
            const parser = new DOMParser()
            const doc = parser.parseFromString(plot.html, 'text/html')
            const scriptTags = doc.querySelectorAll('script')

            let foundMatch = false

            // Helper to extract balanced JSON string
            const extractBalanced = (str, openChar, closeChar, startSearchIndex = 0) => {
                let count = 0
                let startIndex = -1

                for (let i = startSearchIndex; i < str.length; i++) {
                    const char = str[i]

                    if (char === openChar) {
                        if (count === 0) startIndex = i
                        count++
                    } else if (char === closeChar) {
                        count--
                        if (count === 0 && startIndex !== -1) {
                            return {
                                content: str.substring(startIndex, i + 1),
                                endIndex: i
                            }
                        }
                    }
                }
                return null
            }

            for (const scriptTag of scriptTags) {
                const scriptContent = scriptTag.textContent

                // Look for Plotly.newPlot
                const plotCallIndex = scriptContent.indexOf('Plotly.newPlot(')
                if (plotCallIndex !== -1) {
                    console.log('Found Plotly.newPlot call')

                    // Find the data array (starts with [)
                    const dataMatch = extractBalanced(scriptContent, '[', ']', plotCallIndex)

                    if (dataMatch) {
                        // Find the layout object (starts with {), searching after the data array
                        const layoutMatch = extractBalanced(scriptContent, '{', '}', dataMatch.endIndex + 1)

                        if (layoutMatch) {
                            try {
                                // Use new Function to parse loosely (handles JS objects that aren't strict JSON)
                                // This is safe here as we trust the backend output
                                const data = new Function('return ' + dataMatch.content)()
                                const layout = new Function('return ' + layoutMatch.content)()

                                console.log('Parsed successfully with balanced extractor!')
                                setPlotData({ data, layout })
                                foundMatch = true
                                break
                            } catch (e) {
                                console.error('Error evaluating Plotly data:', e)
                            }
                        }
                    }
                }
            }

            if (!foundMatch) {
                console.error('No Plotly.newPlot match found')
                setPlotData({ data: [], layout: {} })
            }

        } catch (error) {
            console.error('Error processing plot HTML:', error)
            setPlotData({ data: [], layout: {} })
        }
    }, [plot.html])

    return (
        <div className="mt-4 glass rounded-xl overflow-hidden border-2 border-purple-200 shadow-lg">
            <div className="bg-gradient-to-r from-purple-600 to-blue-600 px-6 py-3 flex justify-between items-center">
                <h3 className="text-white font-bold text-lg">
                    {plot.insight?.title || 'Visualization'}
                </h3>
                {showNav && (
                    <span className="text-purple-100 text-sm">
                        {currentSlide + 1} / {plots.length}
                    </span>
                )}
            </div>

            <div className="bg-white p-4">
                {plotData.data.length > 0 ? (
                    <Plot
                        data={plotData.data}
                        layout={{
                            ...plotData.layout,
                            autosize: true,
                            height: 400,
                        }}
                        useResizeHandler={true}
                        style={{ width: '100%', height: '400px' }}
                        config={{ responsive: true, displayModeBar: true }}
                    />
                ) : (
                    <div className="flex items-center justify-center h-[400px] text-gray-500">
                        <p>Loading visualization... (check console for details)</p>
                    </div>
                )}

                <div className="mt-6 p-4 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg">
                    <div className="mb-3">
                        <div className="flex items-start">
                            <svg
                                className="w-5 h-5 text-purple-600 mt-0.5 mr-2 flex-shrink-0"
                                fill="currentColor"
                                viewBox="0 0 20 20"
                            >
                                <path
                                    fillRule="evenodd"
                                    d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                                    clipRule="evenodd"
                                />
                            </svg>
                            <div>
                                <p className="font-semibold text-purple-900 text-sm mb-1">
                                    Key Finding
                                </p>
                                <p className="text-gray-700 text-sm leading-relaxed">
                                    {plot.insight?.key_finding || 'Data insights'}
                                </p>
                            </div>
                        </div>
                    </div>
                    <div className="mt-3 pt-3 border-t border-purple-200">
                        <p className="text-gray-600 text-sm leading-relaxed">
                            {plot.insight?.details || 'Analysis of the visualization.'}
                        </p>
                    </div>
                </div>
            </div>

            {showNav && (
                <div className="bg-gray-50 px-6 py-4 flex justify-between items-center border-t border-gray-200">
                    <button
                        onClick={prevSlide}
                        className="flex items-center space-x-2 px-4 py-2 bg-white border-2 border-purple-300 text-purple-700 rounded-lg font-semibold hover:bg-purple-50 transition-all"
                    >
                        <svg
                            className="w-5 h-5"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M15 19l-7-7 7-7"
                            />
                        </svg>
                        <span>Previous</span>
                    </button>
                    <div className="flex space-x-2">
                        {plots.map((_, idx) => (
                            <button
                                key={idx}
                                onClick={() => setCurrentSlide(idx)}
                                className={`w-2 h-2 rounded-full transition-all ${idx === currentSlide ? 'bg-purple-600 w-8' : 'bg-purple-300'
                                    }`}
                            />
                        ))}
                    </div>
                    <button
                        onClick={nextSlide}
                        className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg font-semibold hover:shadow-lg transition-all"
                    >
                        <span>Next</span>
                        <svg
                            className="w-5 h-5"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M9 5l7 7-7 7"
                            />
                        </svg>
                    </button>
                </div>
            )}
        </div>
    )
}
