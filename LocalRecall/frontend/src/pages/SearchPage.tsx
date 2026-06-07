import { useState, useRef } from 'react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: Array<{ file_name: string; snippet: string; content_type: string }>;
}

export function SearchPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [streaming, setStreaming] = useState(false);
  const [input, setInput] = useState('');
  const wsRef = useRef<WebSocket | null>(null);

  const handleSend = () => {
    const question = input.trim();
    if (!question || streaming) return;
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: question }]);
    setStreaming(true);

    const ws = new WebSocket(`ws://127.0.0.1:8420/api/query/ws`);
    wsRef.current = ws;
    let answer = '';
    let sources: any[] = [];

    ws.onopen = () => ws.send(JSON.stringify({ question }));
    ws.onmessage = (e) => {
      const data = JSON.parse(e.data);
      if (data.type === 'sources') sources = data.data;
      if (data.type === 'token') {
        answer += data.text;
        setMessages(prev => {
          const next = [...prev];
          const last = next[next.length - 1];
          if (last?.role === 'assistant') {
            next[next.length - 1] = { ...last, content: answer, sources };
          } else {
            next.push({ role: 'assistant', content: answer, sources });
          }
          return next;
        });
      }
      if (data.type === 'done') {
        setStreaming(false);
        ws.close();
      }
    };
    ws.onerror = () => {
      setStreaming(false);
      setMessages(prev => [...prev, { role: 'assistant', content: '连接失败，请检查后端是否运行。' }]);
    };
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-6">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full text-zinc-400 dark:text-zinc-600">
            <div className="text-center">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1} stroke="currentColor" className="w-12 h-12 mx-auto mb-3 text-zinc-300 dark:text-zinc-700">
                <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
              </svg>
              <p className="text-lg font-medium">LocalRecall</p>
              <p className="text-sm mt-1">问我关于你数据的任何问题</p>
            </div>
          </div>
        ) : (
          <div className="max-w-3xl mx-auto space-y-4">
            {messages.map((msg, i) => (
              <div key={i} className={msg.role === 'user' ? 'flex justify-end' : ''}>
                <div className={msg.role === 'user'
                  ? 'bg-zinc-900 dark:bg-zinc-100 text-white dark:text-zinc-900 px-4 py-2.5 rounded-2xl rounded-br-sm max-w-[70%]'
                  : 'bg-zinc-100 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 px-4 py-3 rounded-2xl rounded-bl-sm'
                }>
                  {msg.role === 'assistant' && (
                    <div className="flex items-center gap-2 mb-2 pb-2 border-b border-zinc-200 dark:border-zinc-800">
                      <div className="w-5 h-5 bg-zinc-900 dark:bg-zinc-100 rounded flex items-center justify-center">
                        <span className="text-white dark:text-zinc-900 text-[9px] font-bold">LR</span>
                      </div>
                      <span className="text-xs text-zinc-500">LocalRecall</span>
                    </div>
                  )}
                  <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="mt-3 space-y-1.5">
                      {msg.sources.map((s, j) => (
                        <div key={j} className="bg-white dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 rounded-lg p-2.5 text-xs">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="font-medium text-zinc-700 dark:text-zinc-300">{s.file_name}</span>
                            <span className="text-zinc-400 text-[10px]">{s.content_type}</span>
                          </div>
                          <p className="text-zinc-500 line-clamp-2">{s.snippet}</p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
            {streaming && (
              <div className="text-xs text-zinc-400 animate-pulse">思考中...</div>
            )}
          </div>
        )}
      </div>
      <div className="p-4 border-t border-zinc-200 dark:border-zinc-800">
        <div className="max-w-3xl mx-auto flex gap-2">
          <input
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSend()}
            placeholder="问我任何关于你数据的问题..."
            className="flex-1 px-4 py-2.5 rounded-xl border border-zinc-300 dark:border-zinc-700 bg-transparent text-sm outline-none focus:border-zinc-500 dark:focus:border-zinc-500"
            disabled={streaming}
          />
          <button
            onClick={handleSend}
            disabled={streaming || !input.trim()}
            className="px-5 py-2.5 bg-zinc-900 dark:bg-zinc-100 text-white dark:text-zinc-900 rounded-xl text-sm font-medium disabled:opacity-40 cursor-pointer"
          >
            发送
          </button>
        </div>
      </div>
    </div>
  );
}
