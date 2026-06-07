import { useState, useEffect } from 'react';

export function StatusPage() {
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    fetch('/api/index/stats').then(r => r.json()).then(setStats).catch(() => {});
  }, []);

  return (
    <div className="p-6">
      <h1 className="text-xl font-semibold mb-6">索引状态</h1>
      {stats ? (
        <div className="grid grid-cols-2 gap-4 max-w-lg">
          <div className="bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl p-4">
            <div className="text-3xl font-bold">{stats.total_files}</div>
            <div className="text-sm text-zinc-500">已索引文件</div>
          </div>
          <div className="bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl p-4">
            <div className="text-3xl font-bold">{stats.total_chunks}</div>
            <div className="text-sm text-zinc-500">向量块</div>
          </div>
          <div className="bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl p-4">
            <div className="text-3xl font-bold text-green-600">{stats.indexed}</div>
            <div className="text-sm text-zinc-500">已完成</div>
          </div>
          <div className="bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl p-4">
            <div className="text-3xl font-bold text-red-600">{stats.errors}</div>
            <div className="text-sm text-zinc-500">错误</div>
          </div>
        </div>
      ) : (
        <p className="text-zinc-400 text-sm">加载中...</p>
      )}
    </div>
  );
}
