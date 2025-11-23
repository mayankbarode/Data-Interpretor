import FormattedContent from './FormattedContent'
import PlotCarousel from './PlotCarousel'

export default function ChatMessage({ message }) {
    const isUser = message.type === 'user'

    return (
        <div
            className={`flex ${isUser ? 'justify-end' : 'justify-start'
                } mb-4`}
        >
            <div
                className={`max-w-[85%] rounded-2xl p-5 ${isUser
                        ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white shadow-lg'
                        : 'glass border border-gray-200'
                    }`}
            >
                {isUser ? (
                    <p className="whitespace-pre-wrap">{message.content}</p>
                ) : (
                    <FormattedContent content={message.content} />
                )}

                {message.plotly_figures && message.plotly_figures.length > 0 && (
                    <PlotCarousel plots={message.plotly_figures} />
                )}

                {message.image && (
                    <div className="mt-4 rounded-xl overflow-hidden border-2 border-purple-200 bg-white p-3 shadow-md">
                        <img
                            src={`data:image/png;base64,${message.image}`}
                            alt="Analysis Chart"
                            className="w-full rounded-lg"
                        />
                    </div>
                )}
            </div>
        </div>
    )
}
