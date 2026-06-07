import { useState, useEffect } from 'react';

export function TagsPage() {
  const [tags, setTags] = useState<any[]>([]);
  const [newTag, setNewTag] = useState('');

  const loadTags = () => {
    fetch('/api/files/tags').then(r => r.json()).then(setTags).catch(() => {});
  };

  useEffect(() => { loadTags(); }, []);

  const addTag = async () => {
    if (!newTag.trim()) return;
    await fetch('/api/files/tags', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: newTag.trim() }),
    });
    setNewTag('');
    loadTags();
  };

  return (
    <div className="p-6">
      <h1 className="text-xl font-semibold mb-6">标签管理</h1>
      <div className="flex gap-2 mb-6">
        <input
          value={newTag}
          onChange={e => setNewTag(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && addTag()}
          placeholder="新标签名称"
          className="flex-1 max-w-xs px-4 py-2 rounded-lg border border-zinc-300 dark:border-zinc-700 bg-transparent text-sm"
        />
        <button onClick={addTag} className="px-4 py-2 bg-zinc-900 dark:bg-zinc-100 text-white dark:text-zinc-900 rounded-lg text-sm font-medium cursor-pointer">添加</button>
      </div>
      <div className="flex flex-wrap gap-2">
        {tags.map((t, i) => (
          <span key={i} className="px-3 py-1.5 rounded-full text-sm border border-zinc-300 dark:border-zinc-700" style={{ borderColor: t.color }}>
            {t.name}
          </span>
        ))}
        {tags.length === 0 && <p className="text-zinc-400 text-sm">暂无标签</p>}
      </div>
    </div>
  );
}
