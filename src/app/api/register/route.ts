/* eslint-disable @typescript-eslint/no-explicit-any, no-console */
import { NextRequest, NextResponse } from 'next/server';

import { getConfig } from '@/lib/config';
import { db } from '@/lib/db';

export const runtime = 'nodejs';

export async function POST(req: NextRequest) {
  try {
    const storageType = process.env.NEXT_PUBLIC_STORAGE_TYPE || 'localstorage';
    if (storageType === 'localstorage') {
      return NextResponse.json(
        { error: '当前存储模式不支持注册，请切换为 redis/kvrocks/upstash' },
        { status: 400 }
      );
    }

    const { username, password } = await req.json();
    if (!username || typeof username !== 'string') {
      return NextResponse.json({ error: '用户名不能为空' }, { status: 400 });
    }
    if (!password || typeof password !== 'string') {
      return NextResponse.json({ error: '密码不能为空' }, { status: 400 });
    }
    if (username === process.env.USERNAME) {
      return NextResponse.json({ error: '该用户名不可用' }, { status: 400 });
    }

    const adminConfig = await getConfig();
    const existed = adminConfig.UserConfig.Users.find(
      (u) => u.username === username
    );
    if (existed) {
      return NextResponse.json({ error: '用户已存在' }, { status: 409 });
    }

    await db.registerUser(username, password);

    adminConfig.UserConfig.Users.push({
      username,
      role: 'user',
      banned: false,
    } as any);

    await db.saveAdminConfig(adminConfig);

    return NextResponse.json({ ok: true }, { status: 201 });
  } catch (error) {
    console.error('注册失败:', error);
    return NextResponse.json({ error: '服务器错误' }, { status: 500 });
  }
}


