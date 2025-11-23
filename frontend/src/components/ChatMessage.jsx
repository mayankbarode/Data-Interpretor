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
                    ? 'bg-zinc-800 text-zinc-100 shadow-lg border border-zinc-700'
                    : 'bg-zinc-900 border border-gold-500/20 shadow-md'
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
                    <div className="mt-4 rounded-xl overflow-hidden border border-gold-500/30 bg-white p-2 shadow-md">
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
